"""Protocol checks only: these do not demonstrate a client approval dialog."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent


class ProbeTests(unittest.TestCase):
    def test_protocol_validation_and_execution(self):
        anyio.run(self.exercise)

    async def exercise(self):
        with tempfile.TemporaryDirectory() as temporary:
            events = Path(temporary) / "events.jsonl"
            params = StdioServerParameters(
                command=sys.executable,
                args=["-c", """
import importlib.abc
import runpy
import sys
class NoMailImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'pythoncom', 'win32com', 'outlook_mcp'}:
            raise RuntimeError('Mail integration import forbidden in probe')
sys.meta_path.insert(0, NoMailImports())
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
""", str(ROOT / "probe.py"), "--events", str(events)],
                cwd=str(ROOT),
            )
            async with stdio_client(params) as (reader, writer):
                async with ClientSession(reader, writer) as session:
                    await session.initialize()
                    catalog = await session.list_tools()
                    self.assertEqual([t.name for t in catalog.tools], ["outlook_send_draft"])
                    self.assertFalse(events.exists())
                    arguments = dict(case_id="protocol-only", revision=1,
                                     subject="Synthetic subject", body="Invented content",
                                     attachments=["fictional.txt"])
                    invalid = await session.call_tool(
                        "outlook_send_draft", {**arguments, "confirm": True})
                    self.assertTrue(invalid.isError)
                    self.assertFalse(events.exists())
                    unknown = await session.call_tool("send_mail", arguments)
                    self.assertTrue(unknown.isError)
                    self.assertFalse(events.exists())
                    for _ in range(2):
                        result = await session.call_tool("outlook_send_draft", arguments)
                        self.assertFalse(result.isError)
                    records = [json.loads(line) for line in events.read_text().splitlines()]
                    self.assertEqual(len(records), 2)
                    self.assertNotEqual(records[0]["execution_id"], records[1]["execution_id"])
                    self.assertEqual(records[0]["arguments"], arguments)
                    self.assertEqual(records[0]["snapshot_hash"], records[1]["snapshot_hash"])
            # Restarting without calls must not replay previous executions.
            async with stdio_client(params) as (reader, writer):
                async with ClientSession(reader, writer) as session:
                    await session.initialize()
            self.assertEqual(len(events.read_text().splitlines()), 2)


if __name__ == "__main__":
    unittest.main()
