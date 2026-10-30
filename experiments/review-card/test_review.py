"""Backend simulation tests only, not evidence of host UI or human approval."""
import importlib.util
from pathlib import Path
import unittest
import sys
from concurrent.futures import ThreadPoolExecutor
import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('review_simulator',Path(__file__).with_name('server.py'))
server=importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)

class ReviewTests(unittest.TestCase):
    def setUp(self): server.reservations.clear()
    def test_complete_preview(self):
        p=server.review_preview().structuredContent
        self.assertTrue(p['review']['bcc'])
        self.assertTrue(p['review']['body'].endswith('END-OF-SYNTHETIC-BODY'))
        self.assertEqual(p['snapshot_hash'],server.digest(p['review']))
    def test_once_only(self):
        p=server.review_preview().structuredContent
        out=server.review_simulate_submit(p['reservation'],p['snapshot_hash']).structuredContent
        self.assertFalse(out['real_mail_sent'])
        with self.assertRaises(ValueError):server.review_simulate_submit(p['reservation'],p['snapshot_hash'])
    def test_mismatch_consumes(self):
        p=server.review_preview().structuredContent
        with self.assertRaises(ValueError):server.review_simulate_submit(p['reservation'],'wrong')
        with self.assertRaises(ValueError):server.review_simulate_submit(p['reservation'],p['snapshot_hash'])
    def test_expiry(self):
        p=server.review_preview().structuredContent
        with patch.object(server.time,'time',return_value=p['expires_at_unix']):
            with self.assertRaises(ValueError):server.review_simulate_submit(p['reservation'],p['snapshot_hash'])
    def test_independent_previews(self):
        a=server.review_preview().structuredContent;b=server.review_preview().structuredContent
        server.review_simulate_submit(a['reservation'],a['snapshot_hash'])
        self.assertFalse(server.reservations[b['reservation']]['consumed'])
    def test_concurrent_claim(self):
        p=server.review_preview().structuredContent
        def attempt(_):
            try:server.review_simulate_submit(p['reservation'],p['snapshot_hash']);return 1
            except ValueError:return 0
        with ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(sum(pool.map(attempt,range(8))),1)
    def test_mcp_resource_and_catalog(self):
        anyio.run(self.protocol)
    async def protocol(self):
        params=StdioServerParameters(command=sys.executable,args=['-c',
            "import importlib.abc,sys,runpy\n"
            "class Block(importlib.abc.MetaPathFinder):\n"
            " def find_spec(self,fullname,path=None,target=None):\n"
            "  if fullname.split('.')[0] in {'outlook_mcp','pythoncom','win32com'}: raise RuntimeError('COM forbidden')\n"
            "sys.meta_path.insert(0,Block())\n"
            "runpy.run_path(sys.argv[1],run_name='__main__')",str(Path(__file__).with_name('server.py'))])
        with anyio.fail_after(20):
            async with stdio_client(params) as (reader,writer):
                async with ClientSession(reader,writer) as session:
                    await session.initialize()
                    catalog=await session.list_tools()
                    self.assertEqual({t.name for t in catalog.tools},{'review_preview','review_simulate_submit'})
                    preview=next(t for t in catalog.tools if t.name=='review_preview')
                    self.assertEqual(preview.meta['ui']['resourceUri'],server.URI)
                    submit=next(t for t in catalog.tools if t.name=='review_simulate_submit')
                    self.assertEqual(submit.meta['ui']['visibility'],['app'])
                    resource=await session.read_resource(server.URI)
                    self.assertEqual(resource.contents[0].mimeType,'text/html;profile=mcp-app')
                    self.assertIn('Simular envío',resource.contents[0].text)
                    data=(await session.call_tool('review_preview',{})).structuredContent
                    response=await session.call_tool('review_simulate_submit',{'reservation':data['reservation'],'snapshot_hash':data['snapshot_hash']})
                    self.assertFalse(response.structuredContent['real_mail_sent'])

if __name__=='__main__':unittest.main()
