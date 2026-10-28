"""Create a small execution bundle from an explicit allowlist, never the checkout."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile


def build(output: Path, git: str):
    root = Path(__file__).resolve().parents[1]
    wheels = list((root / 'dist').glob('outlook_classic_mcp-*.whl'))
    if len(wheels) != 1:
        raise ValueError('Build exactly one reviewed wheel first')
    expected = (root / 'dist' / 'SHA256SUMS.txt').read_text(encoding='utf-8').split()[0]
    if hashlib.sha256(wheels[0].read_bytes()).hexdigest() != expected:
        raise ValueError('Wheel checksum mismatch')
    paths = ['LICENSE', 'requirements.lock', 'docs/ACCOUNT_BOUND.md', 'docs/PROVENANCE.md',
             'docs/UPSTREAM_PROPOSALS.md', 'docs/DEVELOPMENT_LOG.md',
             'scripts/Install-Local.ps1', 'scripts/prepare_codex_config.py', 'scripts/verify_mail_mcp.py',
             'dist/SHA256SUMS.txt', 'dist/' + wheels[0].name]
    revision = subprocess.check_output([git, '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    data = {path: (root / path).read_bytes() for path in paths}
    data['README.txt'] = ("Start with docs/ACCOUNT_BOUND.md. Run scripts/Install-Local.ps1 as a normal user.\n"
                          "No accounts, mail, credentials, runtime or local approval state are included.\n").encode()
    data['SOURCE-REVISION.txt'] = ("base=3295bba51b4719e947b501e7dbb809b8e3708572\nsource=" + revision + '\n').encode()
    data['MANIFEST.json'] = json.dumps({name: hashlib.sha256(value).hexdigest() for name, value in data.items()}, indent=2).encode()
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, value in data.items():
            archive.writestr(name, value)
    with zipfile.ZipFile(output) as archive:
        assert set(archive.namelist()) == set(data)
        for name, value in data.items():
            assert archive.read(name) == value
    print('Portable bundle:', output)
    print('SHA256:', hashlib.sha256(output.read_bytes()).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--git', default='git')
    options = parser.parse_args()
    build(options.output, options.git)
