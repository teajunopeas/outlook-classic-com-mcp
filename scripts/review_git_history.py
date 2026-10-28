"""Check reachable Git objects before publishing; print rules/paths, never matched values.

This is a pattern scan, not a guarantee that arbitrary private data is absent.
Author metadata and public upstream assets remain part of the preserved history.
"""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
import re
import subprocess

RULES = {
    'github-token': rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})',
    'private-key': rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
    'aws-access-key': rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    'jwt-like': rb'\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}',
}
SENSITIVE_PATH = re.compile(r'(^|/)(?:\.env|auth\.json|credentials|state|secure_outbox|secure_drafts|\.venv|rescue-reference|json_lut)(?:[./]|$)|\.(?:pst|ost|eml|msg|docx|pdf|xlsx|sqlite3?|log)$', re.I)


def scan(git: str, root: Path, private_patterns=()):
    def run(*args, input=None):
        return subprocess.run([git, '-C', str(root), *args], input=input, check=True, capture_output=True).stdout
    objects = run('rev-list', '--objects', 'HEAD').decode('utf-8').splitlines()
    names = {line.split(' ', 1)[0]: line.split(' ', 1)[1] for line in objects if ' ' in line}
    raw = run('cat-file', '--batch', input=('\n'.join(names) + '\n').encode('ascii'))
    stream = io.BytesIO(raw)
    findings, checked, binaries = [], 0, 0
    patterns = {name: re.compile(value) for name, value in RULES.items()}
    patterns.update({f'private-pattern-{i + 1}': re.compile(value.encode('utf-8'), re.I)
                     for i, value in enumerate(private_patterns)})
    while header := stream.readline():
        sha, kind, size = header.decode('ascii').strip().split()
        data = stream.read(int(size))
        stream.read(1)
        if kind != 'blob':
            continue
        checked += 1
        path = names[sha]
        if SENSITIVE_PATH.search(path):
            findings.append({'rule': 'sensitive-path', 'path': path, 'blob': sha})
        for rule, pattern in patterns.items():
            if pattern.search(data):
                findings.append({'rule': rule, 'path': path, 'blob': sha})
        if b'\x00' in data:
            binaries += 1
    report = {'head': run('rev-parse', 'HEAD').decode().strip(),
              'reachable_commits': int(run('rev-list', '--count', 'HEAD')),
              'unique_blobs_scanned': checked, 'binary_blobs': binaries, 'findings': findings,
              'limits': 'Pattern scan only. Manually inspect public binary assets and author metadata. Only HEAD ancestry is scanned; do not push --all, --mirror or tags.'}
    print(json.dumps(report, indent=2))
    return bool(findings)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--git', default='git')
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--private-pattern', action='append', default=[])
    options = parser.parse_args()
    raise SystemExit(1 if scan(options.git, options.root, options.private_pattern) else 0)
