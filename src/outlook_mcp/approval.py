"""Small durable content-bound approval ledger, not independent human auth.

Canonical hashing/expiry/invalidation adapted from the user's secure_drafts.
Stores hashes and operation states, never bodies, recipients or token caches.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import secrets
import sqlite3
import time
from contextlib import contextmanager


def digest(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def state_path() -> Path:
    override = os.environ.get("OUTLOOK_MCP_STATE_DIR")
    base = Path(override) if override else Path(os.environ["LOCALAPPDATA"]) / "OutlookClassicMCP"
    return base / "approvals.sqlite3"


class ApprovalLedger:
    def __init__(self, path: Path | None = None):
        self.path = path or state_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.transaction() as db:
            db.execute("CREATE TABLE IF NOT EXISTS approvals (id TEXT PRIMARY KEY, item TEXT, hash TEXT, expires REAL, state TEXT)")

    @contextmanager
    def transaction(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def item_key(account: str, entry_id: str) -> str:
        return digest([account.strip().casefold(), entry_id])

    def _check_busy(self, db, key):
        if db.execute("SELECT 1 FROM approvals WHERE item=? AND state IN ('checking','attempted','uncertain','submitted')", (key,)).fetchone():
            raise PermissionError("Draft has a pending, attempted or uncertain send; inspect Outlook manually. Never retry automatically.")

    def invalidate(self, account: str, entry_id: str):
        key = self.item_key(account, entry_id)
        with self.transaction() as db:
            self._check_busy(db, key)
            db.execute("UPDATE approvals SET state='invalidated' WHERE item=? AND state='active'", (key,))

    def prepare(self, account: str, entry_id: str, snapshot: dict) -> dict:
        key, fingerprint = self.item_key(account, entry_id), digest(snapshot)
        approval_id, expires = secrets.token_hex(16), time.time() + 600
        with self.transaction() as db:
            self._check_busy(db, key)
            db.execute("UPDATE approvals SET state='invalidated' WHERE item=? AND state='active'", (key,))
            db.execute("INSERT INTO approvals VALUES (?,?,?,?,?)", (approval_id, key, fingerprint, expires, 'active'))
        return {"approval_id": approval_id, "snapshot_hash": fingerprint, "expires_at_unix": expires,
                "required_user_phrase": f"SEND {fingerprint}", "snapshot": snapshot,
                "warning": "Wait for explicit human approval. The phrase and id are visible to the agent; this is not independent authentication. No scheduled or delayed sending."}

    def claim(self, account: str, entry_id: str, approval_id: str, phrase: str) -> str:
        key = self.item_key(account, entry_id)
        with self.transaction() as db:
            self._check_busy(db, key)
            row = db.execute("SELECT * FROM approvals WHERE id=? AND item=?", (approval_id, key)).fetchone()
            if not row or row['state'] != 'active' or time.time() >= row['expires']:
                raise PermissionError("Approval missing, consumed, invalidated or expired")
            if phrase != f"SEND {row['hash']}":
                raise PermissionError("Exact SEND phrase required after human review")
            db.execute("UPDATE approvals SET state='checking' WHERE id=?", (approval_id,))
            return row['hash']

    def mark(self, approval_id: str, state: str):
        with self.transaction() as db:
            row = db.execute("SELECT state FROM approvals WHERE id=?", (approval_id,)).fetchone()
            allowed = {'checking': {'attempted', 'rejected'}, 'attempted': {'submitted', 'uncertain'}}
            if not row or state not in allowed.get(row['state'], set()):
                raise PermissionError("Invalid approval state transition")
            db.execute("UPDATE approvals SET state=? WHERE id=?", (state, approval_id))

    def revoke(self, approval_id: str) -> dict:
        with self.transaction() as db:
            row = db.execute("SELECT state FROM approvals WHERE id=?", (approval_id,)).fetchone()
            if not row or row['state'] != 'active':
                raise PermissionError("Only an active, unused approval can be revoked")
            db.execute("UPDATE approvals SET state='revoked' WHERE id=?", (approval_id,))
        return {"status": "revoked"}
