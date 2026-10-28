"""Read-only MCP installation check: initialize, tools/list, whoami only.

Use --live explicitly for the installed server. With --simulate the subprocess
uses a fake account backend and never initializes Outlook. No mail tools are called.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

EXPECTED = {'outlook_whoami', 'outlook_list_mails', 'outlook_search_mails', 'outlook_get_mail',
            'outlook_get_draft', 'outlook_create_draft', 'outlook_reply_draft', 'outlook_forward_draft',
            'outlook_update_draft', 'outlook_preview_draft', 'outlook_revoke_approval', 'outlook_send_draft'}


async def verify(simulate: bool):
    root = Path(__file__).resolve().parents[1]
    args = [str(root / 'tests' / 'simulated_mcp_host.py')] if simulate else ['-m', 'outlook_mcp']
    env = dict(os.environ)
    env['PYTHONIOENCODING'] = 'utf-8'
    params = StdioServerParameters(command=sys.executable, args=args, env=env, cwd=str(root))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = {t.name for t in tools.tools}
            if names != EXPECTED:
                raise RuntimeError(f'Unexpected effective tool catalog: {sorted(names)}')
            resources = await session.list_resources()
            if resources.resources:
                raise RuntimeError('Unexpected UI resources')
            accounts = await session.call_tool('outlook_whoami', {})
            if accounts.isError:
                raise RuntimeError('Account enumeration failed; check Outlook manually')
            print(json.dumps({'mode': 'simulated' if simulate else 'live', 'tools': sorted(names),
                              'accounts_result': accounts.model_dump(mode='json')}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--live', action='store_true')
    mode.add_argument('--simulate', action='store_true')
    options = parser.parse_args()
    asyncio.run(verify(options.simulate))
