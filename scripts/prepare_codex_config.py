"""Prepare/review or apply ONLY the named Codex MCP entries; never touches auth files.

Preparation saves the proposed config and an original hash below InstallRoot.
Applying refuses concurrent config changes and backs up the original below InstallRoot.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tomllib


def prepare(config: Path, root: Path):
    raw = config.read_bytes() if config.exists() else b''
    text = raw.decode('utf-8-sig')
    data = tomllib.loads(text)
    if 'outlook_classic' in data.get('mcp_servers', {}):
        raise ValueError('outlook_classic already exists. Do not overwrite an existing configuration.')
    disabled_ms365 = False
    if 'ms365' in data.get('mcp_servers', {}):
        pattern = r'(?ms)^\[mcp_servers\.ms365\][^\S\r\n]*\r?\n(?P<body>.*?)(?=^\[|\Z)'
        def disable(match):
            body = match.group('body')
            if re.search(r'(?m)^enabled\s*=', body):
                body = re.sub(r'(?m)^enabled\s*=.*$', 'enabled = false', body)
            else:
                body = 'enabled = false\n' + body
            return '[mcp_servers.ms365]\n' + body
        text, count = re.subn(pattern, disable, text)
        if count != 1:
            raise ValueError('Nonstandard ms365 table; review it manually instead of guessing')
        disabled_ms365 = True
    quote = lambda value: json.dumps(str(value), ensure_ascii=False)
    tools = ['whoami', 'list_mails', 'search_mails', 'get_mail', 'get_draft', 'create_draft',
             'reply_draft', 'forward_draft', 'update_draft', 'preview_draft', 'revoke_approval', 'send_draft']
    block = '\n[mcp_servers.outlook_classic]\n'
    block += f'command = {quote(root / "venv" / "Scripts" / "python.exe")}\n'
    block += 'args = ["-m", "outlook_mcp"]\n'
    block += f'cwd = {quote(root)}\nstartup_timeout_sec = 90\ntool_timeout_sec = 150\n'
    block += 'enabled_tools = ' + json.dumps(['outlook_' + t for t in tools]) + '\n'
    block += '\n[mcp_servers.outlook_classic.env]\nPYTHONIOENCODING = "utf-8"\n'
    block += 'OUTLOOK_MCP_ALLOW_SEND = "1"\n'
    block += f'OUTLOOK_MCP_STATE_DIR = {quote(root / "state")}\n'
    for key in ('SystemRoot', 'COMSPEC', 'USERPROFILE', 'LOCALAPPDATA', 'APPDATA', 'TEMP', 'TMP'):
        if key in os.environ:
            block += f'{key} = {quote(os.environ[key])}\n'
    proposed = text.rstrip() + '\n' + block
    checked = tomllib.loads(proposed)
    assert checked['mcp_servers']['outlook_classic']['enabled_tools'] == ['outlook_' + t for t in tools]
    # All non-MCP sections and all unrelated MCP entries must remain semantically identical.
    for key, value in data.items():
        if key != 'mcp_servers':
            assert checked[key] == value
    for key, value in data.get('mcp_servers', {}).items():
        assert checked['mcp_servers'][key] == ({**value, 'enabled': False} if key == 'ms365' else value)
    root.mkdir(parents=True, exist_ok=True)
    # Persist the exact hashed bytes: Windows text newline translation changes the hash.
    (root / 'codex-config-proposed.toml').write_bytes(proposed.encode('utf-8'))
    metadata = {'config': str(config), 'original_sha256': hashlib.sha256(raw).hexdigest(),
                'proposed_sha256': hashlib.sha256(proposed.encode('utf-8')).hexdigest(), 'disabled_ms365': disabled_ms365}
    (root / 'codex-config-review.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print('Prepared outlook_classic with 12 mail-only tools; sending requires content-bound approval.')
    print('ms365 will be disabled:', disabled_ms365)
    print('No configuration or authentication file has been modified.')


def apply(config: Path, root: Path):
    metadata = json.loads((root / 'codex-config-review.json').read_text(encoding='utf-8'))
    raw = config.read_bytes() if config.exists() else b''
    proposed = (root / 'codex-config-proposed.toml').read_bytes()
    if str(config) != metadata['config'] or hashlib.sha256(raw).hexdigest() != metadata['original_sha256']:
        raise ValueError('Configuration changed since preparation; prepare and review again')
    if hashlib.sha256(proposed).hexdigest() != metadata['proposed_sha256']:
        raise ValueError('Proposed configuration changed since preparation')
    tomllib.loads(proposed.decode('utf-8'))
    backup = root / ('codex-config-before-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.toml')
    with backup.open('xb') as handle:
        handle.write(raw)
    # Write only the explicitly authorized file. No auth.json, token store or profile-wide permissions.
    config.write_bytes(proposed)
    print('Applied only the reviewed MCP changes. Backup:', backup)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install-root', type=Path, required=True)
    parser.add_argument('--config', type=Path, default=Path.home() / '.codex' / 'config.toml')
    parser.add_argument('--apply', action='store_true')
    options = parser.parse_args()
    (apply if options.apply else prepare)(options.config.resolve(), options.install_root.resolve())
