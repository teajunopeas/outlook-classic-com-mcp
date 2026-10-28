"""Subprocess fixture only. Never connects to COM or Outlook."""
import sys
import types

if sys.platform != 'win32':
    sys.modules.setdefault('pythoncom', types.ModuleType('pythoncom'))

from outlook_mcp.server import build_server

server, bridge = build_server()

async def simulated_call(func, *args, **kwargs):
    if func.__name__ != 'whoami':
        raise AssertionError('Installation smoke test must never read or write messages')
    return {'accounts': [], 'simulation': True}

bridge.call = simulated_call
server.run()
