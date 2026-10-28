"""Account-bound adapters around Macfly's existing COM mail implementation."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import tempfile
from typing import Any

from outlook_mcp.approval import ApprovalLedger, digest
from outlook_mcp.client import mail as upstream
from outlook_mcp.client.sender import AccountNamespace, bind_sender, require_draft, verify_sender
from outlook_mcp.utils.paths import validate_attachment_path


def _context(namespace, account_smtp, entry_id=None, *, draft=False):
    ns = AccountNamespace(namespace, account_smtp)
    if not entry_id:
        return ns, None
    item = ns.GetItemFromID(entry_id)
    if draft:
        require_draft(item, ns.store)
        verify_sender(item, account_smtp)
    return ns, item


def list_mail(outlook, namespace, *, account_smtp, folder='inbox', limit=10, offset=0):
    ns, _ = _context(namespace, account_smtp)
    return upstream.list_mails(outlook, ns, folder=folder, limit=limit, offset=offset, include_preview=False)


def search_mail(outlook, namespace, *, account_smtp, query, folder='inbox', limit=10):
    ns, _ = _context(namespace, account_smtp)
    return upstream.search_mails(outlook, ns, query=query, folder=folder, limit=limit, include_preview=False)


def get_mail(outlook, namespace, *, account_smtp, entry_id, max_body_chars=10000):
    _, item = _context(namespace, account_smtp, entry_id)
    return upstream._mail_full(item, max_body_chars=max_body_chars)


def get_draft(outlook, namespace, *, account_smtp, entry_id):
    _, item = _context(namespace, account_smtp, entry_id, draft=True)
    return snapshot(item, account_smtp)


def _save_draft(item, ns, smtp):
    verify_sender(item, smtp)
    item.Save()
    require_draft(item, ns.store)
    verify_sender(item, smtp)
    return {"status": "draft_saved", "entry_id": item.EntryID, "account_smtp": smtp,
            "subject": item.Subject}


def create_draft(outlook, namespace, *, account_smtp, to=None, subject='', body='', cc=None, bcc=None,
                 attachments=None, action='new', source_entry_id=None):
    ns, _ = _context(namespace, account_smtp)
    if action == 'new':
        if source_entry_id:
            raise ValueError("New mail cannot have a source EntryID")
        item = ns.store.GetDefaultFolder(16).Items.Add(0)
    else:
        if action not in {'reply', 'reply_all', 'forward'} or not source_entry_id:
            raise ValueError("reply/reply_all/forward require a source EntryID")
        original = ns.GetItemFromID(source_entry_id)
        item = {'reply': original.Reply, 'reply_all': original.ReplyAll, 'forward': original.Forward}[action]()
    bind_sender(item, ns.account)
    if to is not None:
        item.To = '; '.join(to)
    if cc is not None:
        item.CC = '; '.join(cc)
    if bcc is not None:
        item.BCC = '; '.join(bcc)
    if action == 'new':
        item.Subject = subject
    elif subject:
        item.Subject = subject
    if action == 'new':
        item.Body = body
    elif body:
        item.Body = body + '\r\n\r\n' + str(item.Body or '')
    # Native Reply/ReplyAll/Forward preserves the thread and inherited attachments.
    for raw in attachments or []:
        item.Attachments.Add(validate_attachment_path(raw))
    result = _save_draft(item, ns, account_smtp)
    result['action'] = action
    return result


def update_draft(outlook, namespace, *, account_smtp, entry_id, subject=None, body=None, to=None,
                 cc=None, bcc=None, attachments_to_add=None, clear_attachments=False):
    ns, item = _context(namespace, account_smtp, entry_id, draft=True)
    ledger = ApprovalLedger()
    ledger.invalidate(account_smtp, entry_id)  # Invalidate BEFORE any mutation, even on partial failure.
    bind_sender(item, ns.account)
    result = upstream.update_draft(outlook, ns, entry_id=entry_id, subject=subject, body=body,
                                   to=to, cc=cc, bcc=bcc, attachments_to_add=attachments_to_add,
                                   clear_attachments=clear_attachments)
    # Upstream saves once. Do not silently repair an account changed by Save.
    require_draft(item, ns.store)
    verify_sender(item, account_smtp)
    return result


def _smtp_recipient(recipient):
    if not recipient.Resolved:
        raise ValueError("Unresolved recipient; review it in Outlook")
    address = recipient.AddressEntry
    if str(address.Type).upper() == 'EX':
        exchange = address.GetExchangeUser() or address.GetExchangeDistributionList()
        smtp = str(exchange.PrimarySmtpAddress or '') if exchange else ''
    else:
        smtp = str(address.Address or '')
    if '@' not in smtp or any(c.isspace() for c in smtp):
        raise ValueError("Recipient has no unambiguous SMTP address")
    return {"type": int(recipient.Type), "smtp": smtp.casefold(), "name": str(recipient.Name or '')}


def snapshot(item, smtp):
    """Read the whole real draft, including embedded by-value attachment bytes.

    Temporary extraction is deleted immediately; linked/OLE/embedded-item attachments
    fail closed rather than pretending their content has been frozen.
    """
    actual = verify_sender(item, smtp)
    recipients = [_smtp_recipient(r) for r in item.Recipients]
    attachments = []
    with tempfile.TemporaryDirectory(prefix='outlook-mcp-hash-') as temp:
        for index, attachment in enumerate(item.Attachments, 1):
            if int(attachment.Type) != 1:
                raise ValueError("Only by-value file attachments can be approved in this version")
            target = Path(temp) / str(index)
            attachment.SaveAsFile(str(target))
            with target.open('rb') as handle:
                attachment_hash = hashlib.file_digest(handle, 'sha256').hexdigest()
            attachments.append({"name": str(attachment.FileName), "size": target.stat().st_size,
                                "type": int(attachment.Type), "position": int(attachment.Position),
                                "sha256": attachment_hash})
    def binary(value):
        return bytes(value).hex() if value else ''
    return {"account_smtp": actual.casefold(), "delegated_identity": str(item.SentOnBehalfOfName or ''),
            "entry_id": str(item.EntryID), "store_id": str(item.Parent.StoreID),
            "folder_id": str(item.Parent.EntryID), "revision": str(item.LastModificationTime),
            "to": str(item.To or ''), "cc": str(item.CC or ''), "bcc": str(item.BCC or ''),
            "recipients": recipients, "subject": str(item.Subject or ''), "body": str(item.Body or ''),
            "html_body": str(item.HTMLBody or ''), "body_format": int(item.BodyFormat),
            "rtf_body_sha256": hashlib.sha256(bytes(item.RTFBody or b'')).hexdigest(),
            "importance": int(item.Importance), "sensitivity": int(item.Sensitivity),
            "read_receipt": bool(item.ReadReceiptRequested),
            "delivery_receipt": bool(item.OriginatorDeliveryReportRequested),
            "deferred_delivery": str(item.DeferredDeliveryTime),
            "origin": {"conversation_id": str(item.ConversationID or ''),
                       "conversation_index": binary(item.ConversationIndex)},
            "attachments": attachments}


def preview_draft(outlook, namespace, *, account_smtp, entry_id):
    ns, item = _context(namespace, account_smtp, entry_id, draft=True)
    ledger = ApprovalLedger()
    ledger.invalidate(account_smtp, entry_id)
    if not item.Recipients.ResolveAll():
        raise ValueError("Recipients could not all be resolved")
    _save_draft(item, ns, account_smtp)
    content = snapshot(item, account_smtp)
    if not any(r['type'] == 1 for r in content['recipients']):
        raise ValueError("At least one To recipient is required")
    return ledger.prepare(account_smtp, entry_id, content)


def send_draft(outlook, namespace, *, account_smtp, entry_id, approval_id, confirmation_phrase):
    if os.environ.get('OUTLOOK_MCP_ALLOW_SEND', '0') != '1':
        raise PermissionError("Sending is disabled; set OUTLOOK_MCP_ALLOW_SEND=1 explicitly")
    ledger = ApprovalLedger()
    expected = ledger.claim(account_smtp, entry_id, approval_id, confirmation_phrase)
    attempted = False
    try:
        ns, item = _context(namespace, account_smtp, entry_id, draft=True)
        if digest(snapshot(item, account_smtp)) != expected:
            raise PermissionError("Draft changed after review; approval consumed, preview again")
        # Do NOT rebind or Save here: that could hide sender tampering or change the approved revision.
        require_draft(item, ns.store)
        verify_sender(item, account_smtp)
        ledger.mark(approval_id, 'attempted')  # Durable before Send: process death cannot trigger a retry.
        attempted = True
        item.Send()  # Exactly one attempt. Outlook submission is not proof of delivery.
        ledger.mark(approval_id, 'submitted')
        return {"status": "submitted", "approval_id": approval_id, "retry_allowed": False}
    except Exception:
        status = 'uncertain' if attempted else 'rejected'
        ledger.mark(approval_id, status)
        return {"status": status, "approval_id": approval_id, "retry_allowed": False,
                "message": "Inspect Outlook manually if uncertain; never repeat the send automatically."}


# The bridge fails closed for everything else (including all draft writes).
for _read in (list_mail, search_mail, get_mail, get_draft):
    _read.outlook_read_only = True
