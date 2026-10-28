"""Simulated COM tests. No Outlook process, profile or real messages are used."""
from __future__ import annotations

import asyncio
import sys
import types
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

if sys.platform != 'win32':
    sys.modules.setdefault('pythoncom', types.ModuleType('pythoncom'))

from outlook_mcp.approval import ApprovalLedger, digest
from outlook_mcp.client import bound_mail as mail
from outlook_mcp.client.sender import AccountNamespace, account_for, put_reference, require_draft, verify_sender

SMTP = 'sender@example.test'


class Recipients(list):
    def ResolveAll(self):
        return all(r.Resolved for r in self)


class Attachments(list):
    @property
    def Count(self):
        return len(self)

    def Add(self, path):
        self.append(Attachment(Path(path).read_bytes()))

    def Remove(self, index):
        self.pop(index - 1)


class Attachment:
    Type = 1
    FileName = 'file.txt'
    Position = 0

    def __init__(self, content=b'approved'):
        self.content = content

    def SaveAsFile(self, path):
        Path(path).write_bytes(self.content)


class Item:
    def __init__(self, env):
        self.env = env
        self.Class = 43
        self.Sent = self.Submitted = False
        self.Saved = True
        self.EntryID = 'draft-1'
        self.Parent = env.folder
        self.SendUsingAccount = env.account
        self.SentOnBehalfOfName = ''
        self.SaveSentMessageFolder = env.sent
        self.LastModificationTime = 'revision-1'
        self.To, self.CC, self.BCC = 'receiver@example.test', '', ''
        self.Subject, self.Body = 'Subject', 'Body'
        self.HTMLBody, self.RTFBody, self.BodyFormat = '<p>Body</p>', b'rtf', 1
        self.Importance, self.Sensitivity = 1, 0
        self.ReadReceiptRequested = self.OriginatorDeliveryReportRequested = False
        self.DeferredDeliveryTime = 'none'
        self.ConversationID, self.ConversationIndex = 'thread', b'index'
        self.Recipients = Recipients([NS(Resolved=True, Type=1, Name='Receiver',
                                       AddressEntry=NS(Type='SMTP', Address='receiver@example.test'))])
        self.Attachments = Attachments()
        self.saves = self.sends = 0
        self.change_on_save = self.send_error = False

    def Save(self):
        self.saves += 1
        self.LastModificationTime = f'revision-save-{self.saves}'
        if self.change_on_save:
            self.SendUsingAccount = NS(SmtpAddress='wrong@example.test')

    def Send(self):
        self.sends += 1
        if self.send_error:
            raise RuntimeError('RPC result unavailable')
        self.Submitted = True

    def Reply(self):
        self.env.actions.append('reply')
        return self.env.item

    def ReplyAll(self):
        self.env.actions.append('reply_all')
        return self.env.item

    def Forward(self):
        self.env.actions.append('forward')
        return self.env.item


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setenv('OUTLOOK_MCP_STATE_DIR', str(tmp_path / 'state'))
    monkeypatch.setenv('OUTLOOK_MCP_ALLOW_SEND', '1')
    e = NS(actions=[], created=[])
    e.folder = NS(StoreID='store-1', EntryID='draft-folder')
    e.sent = NS(StoreID='store-1', EntryID='sent-folder')
    e.store = NS(StoreID='store-1', DisplayName='Account store', GetDefaultFolder=lambda n: e.folder if n == 16 else e.sent)
    e.account = NS(SmtpAddress=SMTP, DisplayName='Sender', CurrentUser=NS(Name='Sender'), DeliveryStore=e.store)
    e.item = Item(e)
    e.original = Item(e)
    e.original.EntryID = 'source-1'
    e.original.Parent = NS(StoreID='store-1', EntryID='inbox-folder')
    e.original.Sent = True
    e.folder.Items = NS(Add=lambda kind: e.created.append(kind) or e.item)
    e.ns = NS(Accounts=[e.account], GetItemFromID=lambda eid, sid: e.original if eid == 'source-1' else e.item)
    return e


def preview(e):
    return mail.preview_draft(None, e.ns, account_smtp=SMTP, entry_id=e.item.EntryID)


def send(e, approval):
    return mail.send_draft(None, e.ns, account_smtp=SMTP, entry_id=e.item.EntryID,
                           approval_id=approval['approval_id'], confirmation_phrase=approval['required_user_phrase'])


def test_putref_is_required():
    calls = []
    account = object()
    item = NS(_oleobj_=NS(GetIDsOfNames=lambda name: 123, Invoke=lambda *args: calls.append(args)))
    put_reference(item, 'SendUsingAccount', account)
    assert calls == [(123, 0, 8, 0, account)]


def test_exact_account_no_default_or_duplicate(env):
    assert account_for(env.ns, SMTP.upper()) is env.account
    with pytest.raises(ValueError):
        account_for(env.ns, 'other@example.test')
    env.ns.Accounts.append(env.account)
    with pytest.raises(ValueError):
        account_for(env.ns, SMTP)


def test_delegate_rejected_and_own_name_allowed(env):
    env.item.SentOnBehalfOfName = 'Sender'
    assert verify_sender(env.item, SMTP) == SMTP
    env.item.SentOnBehalfOfName = 'someone@example.test'
    with pytest.raises(PermissionError):
        verify_sender(env.item, SMTP)


def test_create_and_save_rechecks_sender(env):
    env.item.change_on_save = True
    with pytest.raises(PermissionError):
        mail.create_draft(None, env.ns, account_smtp=SMTP, to=['receiver@example.test'])
    assert env.item.saves == 1 and env.item.sends == 0


def test_sender_assignment_failure_never_falls_back(env):
    env.item._oleobj_ = NS(GetIDsOfNames=lambda _: 1, Invoke=lambda *args: None)
    env.item.SendUsingAccount = NS(SmtpAddress='other@example.test')
    with pytest.raises(PermissionError):
        mail.create_draft(None, env.ns, account_smtp=SMTP)
    assert env.item.saves == env.item.sends == 0


@pytest.mark.parametrize('field,value', [('Class', 26), ('Sent', True), ('Submitted', True), ('Saved', False), ('EntryID', '')])
def test_only_valid_drafts_can_be_edited_or_sent(env, field, value):
    approval = preview(env)
    setattr(env.item, field, value)
    with pytest.raises(ValueError):
        mail.update_draft(None, env.ns, account_smtp=SMTP, entry_id='draft-1', subject='change')
    result = mail.send_draft(None, env.ns, account_smtp=SMTP, entry_id='draft-1',
                             approval_id=approval['approval_id'], confirmation_phrase=approval['required_user_phrase'])
    assert result['status'] == 'rejected' and env.item.sends == 0


def test_inbox_unsent_is_not_a_draft(env):
    env.item.Parent = NS(StoreID='store-1', EntryID='inbox-folder')
    with pytest.raises(ValueError):
        require_draft(env.item, env.store)


def test_cross_account_lookup_is_rejected(env):
    env.item.Parent = NS(StoreID='other-store', EntryID='draft-folder')
    with pytest.raises(PermissionError):
        AccountNamespace(env.ns, SMTP).GetItemFromID('draft-1')


@pytest.mark.parametrize('action', ['reply', 'reply_all', 'forward'])
def test_native_reply_and_forward_only_save(env, action):
    env.item.Body = 'Quoted original'
    result = mail.create_draft(None, env.ns, account_smtp=SMTP, action=action, source_entry_id='source-1', body='Reply')
    assert env.actions == [action]
    assert env.item.Body == 'Reply\r\n\r\nQuoted original'
    assert env.item.saves == 1 and env.item.sends == 0
    assert result['entry_id'] == 'draft-1'


def test_update_same_real_draft_invalidates_approval(env):
    approval = preview(env)
    result = mail.update_draft(None, env.ns, account_smtp=SMTP, entry_id='draft-1', subject='changed')
    assert result['entry_id'] == 'draft-1'
    assert env.item.Subject == 'changed'
    with pytest.raises(PermissionError):
        send(env, approval)
    assert env.item.sends == 0


def test_sender_changed_by_update_save_is_not_repaired(env):
    env.item.change_on_save = True
    with pytest.raises(PermissionError):
        mail.update_draft(None, env.ns, account_smtp=SMTP, entry_id='draft-1', body='new')
    assert env.item.SendUsingAccount.SmtpAddress == 'wrong@example.test'


@pytest.mark.parametrize('field,value', [('Body', 'changed'), ('HTMLBody', '<p>changed</p>'), ('RTFBody', b'changed'),
                                      ('Subject', 'changed'), ('To', 'other@example.test'), ('CC', 'cc@example.test'),
                                      ('BCC', 'bcc@example.test'), ('LastModificationTime', 'new-revision'),
                                      ('ConversationID', 'other-thread'), ('Importance', 2)])
def test_external_edits_invalidate_snapshot(env, field, value):
    approval = preview(env)
    setattr(env.item, field, value)
    assert send(env, approval)['status'] == 'rejected'
    assert env.item.sends == 0


def test_sender_tamper_is_not_silently_rebound(env):
    approval = preview(env)
    env.item.SendUsingAccount = NS(SmtpAddress='other@example.test')
    assert send(env, approval)['status'] == 'rejected'
    assert env.item.sends == 0


def test_attachment_content_changes_in_real_draft_are_detected(env):
    attachment = Attachment()
    env.item.Attachments.append(attachment)
    approval = preview(env)
    assert approval['snapshot']['attachments'][0]['sha256']
    attachment.content = b'replaced'
    assert send(env, approval)['status'] == 'rejected'
    assert env.item.sends == 0


def test_non_file_attachment_and_unresolved_recipient_block_approval(env):
    env.item.Recipients[0].Resolved = False
    with pytest.raises(ValueError):
        preview(env)
    env.item.Recipients[0].Resolved = True
    attachment = Attachment()
    attachment.Type = 5
    env.item.Attachments.append(attachment)
    with pytest.raises(ValueError):
        preview(env)


def test_uncertain_send_only_one_attempt_even_after_restart(env):
    approval = preview(env)
    env.item.send_error = True
    assert send(env, approval)['status'] == 'uncertain'
    assert env.item.sends == 1
    with pytest.raises(PermissionError):
        send(env, approval)
    with pytest.raises(PermissionError):
        preview(env)
    assert env.item.sends == 1


def test_success_is_submission_not_delivery_and_not_repeatable(env):
    approval = preview(env)
    assert send(env, approval)['status'] == 'submitted'
    assert env.item.sends == 1
    with pytest.raises(PermissionError):
        send(env, approval)


def test_disabled_send_and_wrong_phrase_never_send(env, monkeypatch):
    approval = preview(env)
    monkeypatch.setenv('OUTLOOK_MCP_ALLOW_SEND', '0')
    with pytest.raises(PermissionError):
        send(env, approval)
    monkeypatch.setenv('OUTLOOK_MCP_ALLOW_SEND', '1')
    with pytest.raises(PermissionError):
        mail.send_draft(None, env.ns, account_smtp=SMTP, entry_id='draft-1', approval_id=approval['approval_id'], confirmation_phrase='yes')
    assert env.item.sends == 0


def test_expiry_revocation_and_single_claim_under_concurrency(env, monkeypatch):
    ledger = ApprovalLedger()
    approval = ledger.prepare(SMTP, 'other-id', {'body': 'test'})
    ledger.revoke(approval['approval_id'])
    with pytest.raises(PermissionError):
        ledger.claim(SMTP, 'other-id', approval['approval_id'], approval['required_user_phrase'])
    approval = preview(env)
    def claim():
        try:
            return ApprovalLedger().claim(SMTP, 'draft-1', approval['approval_id'], approval['required_user_phrase'])
        except PermissionError:
            return None
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: claim(), range(2)))
    assert sum(r is not None for r in results) == 1
    approval = ledger.prepare(SMTP, 'expires', {})
    import outlook_mcp.approval as module
    monkeypatch.setattr(module.time, 'time', lambda: approval['expires_at_unix'] + 1)
    with pytest.raises(PermissionError):
        ledger.claim(SMTP, 'expires', approval['approval_id'], approval['required_user_phrase'])


def test_effective_server_catalog_and_no_hidden_tools(env):
    from outlook_mcp.server import build_server
    mcp, bridge = build_server()
    # Building/listing the catalog must not start COM or read messages.
    assert bridge._thread is None
    tools = asyncio.run(mcp.list_tools())
    names = {t.name for t in tools}
    assert names == {'outlook_whoami', 'outlook_list_mails', 'outlook_search_mails', 'outlook_get_mail',
                     'outlook_get_draft', 'outlook_create_draft', 'outlook_reply_draft', 'outlook_forward_draft',
                     'outlook_update_draft', 'outlook_preview_draft', 'outlook_revoke_approval', 'outlook_send_draft'}
    assert asyncio.run(mcp.list_resources()) == []
    send_tool = next(t for t in tools if t.name == 'outlook_send_draft')
    assert {'account_smtp', 'entry_id', 'approval_id', 'confirmation_phrase'} <= set(send_tool.inputSchema['required'])


@pytest.mark.skipif(sys.platform != 'win32', reason='pywin32 exception type needed; COM remains simulated')
def test_write_bridge_never_retries_disconnect():
    from outlook_mcp.bridge import OutlookBridge
    import pythoncom
    bridge = OutlookBridge()
    bridge._outlook = bridge._namespace = object()
    calls = []
    def write(*_):
        calls.append(1)
        raise pythoncom.com_error(-2147023174, 'disconnected', None, None)
    holder = {}
    bridge._execute(write, (), {}, holder)
    assert len(calls) == 1 and 'error' in holder
