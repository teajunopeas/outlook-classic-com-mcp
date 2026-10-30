"""Standalone MCP Apps review-card experiment. No Outlook imports or sending."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import secrets
import time
from threading import Lock

from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, TextContent

URI = 'ui://outlook-experiment/review.html'
mcp = FastMCP('outlook_review_card_simulator', instructions=(
    'Synthetic UI experiment only. No mail account is connected. '
    'The card records a simulated attempt, never sends mail or proves human authorization.'))
reservations = {}
claim_lock = Lock()

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode()).hexdigest()

def result(value):
    return CallToolResult(content=[TextContent(type='text', text=json.dumps(value))],
                          structuredContent=value)

@mcp.resource(URI, mime_type='text/html;profile=mcp-app',
              meta={'ui': {'prefersBorder': True}})
def review_card() -> str:
    return Path(__file__).with_name('review.html').read_text(encoding='utf-8')

@mcp.tool(meta={'ui': {'resourceUri': URI}}, annotations={'readOnlyHint': True})
def review_preview() -> CallToolResult:
    """Show a wholly synthetic email. Creates no real draft, account or permission."""
    # Bounded memory; a UI experiment must not accumulate unbounded reservations.
    for key in list(reservations):
        if reservations[key]['expires'] <= time.time():
            del reservations[key]
    if len(reservations) >= 32:
        raise ValueError('Too many live previews; wait for expiry or restart simulator')
    review = {
        'schema_version': 1, 'simulation': True, 'revision': 'synthetic-v1',
        'sender': 'sender@example.test', 'to': ['recipient@example.test'],
        'cc': ['copy@example.test'], 'bcc': ['hidden@example.test'],
        'subject': 'Synthetic review — no email will be sent',
        'body': ('Complete synthetic body. Please inspect all text.\n' * 40)
                + '<img src=x onerror=alert(1)>\nEND-OF-SYNTHETIC-BODY',
        'attachments': [{'name': 'fictional-report.txt', 'size': 12,
                         'sha256': hashlib.sha256(b'invented.txt').hexdigest()}],
    }
    token = secrets.token_hex(16)
    fingerprint = digest(review)
    expires = time.time() + 600
    reservations[token] = {'hash': fingerprint, 'review': deepcopy(review),
                           'expires': expires, 'consumed': False}
    return result({'review': review, 'reservation': token,
                   'snapshot_hash': fingerprint, 'expires_at_unix': expires})

@mcp.tool(meta={'ui': {'visibility': ['app']}}, annotations={
    'readOnlyHint': False, 'destructiveHint': True,
    'idempotentHint': False, 'openWorldHint': False})
def review_simulate_submit(reservation: str, snapshot_hash: str) -> CallToolResult:
    """SIMULATION ONLY: consume a synthetic review once. Not a real send or consent attestation."""
    with claim_lock:
        saved = reservations.get(reservation)
        if not saved or saved['consumed'] or time.time() >= saved['expires']:
            raise ValueError('Review missing, expired or consumed; do not retry automatically')
        # Consumed before checking: a rejected request cannot silently revive it.
        saved['consumed'] = True
        if not secrets.compare_digest(saved['hash'], snapshot_hash):
            raise ValueError('Review hash mismatch; request a new preview')
    return result({'status': 'simulated_attempt', 'simulation': True,
                   'human_approval_verified': False, 'real_mail_sent': False})

if __name__ == '__main__':
    mcp.run()
