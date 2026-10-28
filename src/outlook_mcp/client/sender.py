"""Exact account/store binding; adapted from the user's secure_dispatch helpers.

No default-account fallback and no delegated identities are supported.
"""
from __future__ import annotations

from typing import Any


def account_for(namespace: Any, smtp: str) -> Any:
    smtp = smtp.strip().casefold()
    if not smtp or "@" not in smtp:
        raise ValueError("An exact sender SMTP address is required")
    matches = [a for a in namespace.Accounts if str(a.SmtpAddress).strip().casefold() == smtp]
    if len(matches) != 1:
        raise ValueError("Sender account missing or ambiguous; no default fallback")
    if not matches[0].DeliveryStore.StoreID:
        raise ValueError("Sender account has no accessible DeliveryStore")
    return matches[0]


def put_reference(message: Any, name: str, value: Any) -> None:
    ole = getattr(message, "_oleobj_", None)
    if ole is not None:
        ole.Invoke(ole.GetIDsOfNames(name), 0, 8, 0, value)  # DISPATCH_PROPERTYPUTREF
    else:  # Test doubles only; COM errors never fall back.
        setattr(message, name, value)


def verify_sender(message: Any, smtp: str) -> str:
    account = message.SendUsingAccount
    actual = str(account.SmtpAddress).strip()
    if actual.casefold() != smtp.strip().casefold():
        raise PermissionError("Effective SendUsingAccount differs from requested sender")
    behalf = str(message.SentOnBehalfOfName or "").strip().casefold()
    own_names = {smtp.strip().casefold(), str(account.DisplayName or "").strip().casefold()}
    owner = getattr(account, "CurrentUser", None)
    own_names.add(str(getattr(owner, "Name", "") or "").strip().casefold())
    if behalf and behalf not in own_names:
        raise PermissionError("Unapproved delegated sender identity")
    return actual


def bind_sender(message: Any, account: Any) -> None:
    put_reference(message, "SendUsingAccount", account)
    verify_sender(message, account.SmtpAddress)
    put_reference(message, "SaveSentMessageFolder", account.DeliveryStore.GetDefaultFolder(5))


def require_draft(message: Any, store: Any) -> None:
    """Fail closed: saved, unsent MailItem in this account's actual Drafts folder."""
    if message.Class != 43 or message.Sent is not False or message.Submitted is not False:
        raise ValueError("Only an unsent, unsubmitted Outlook MailItem is a draft")
    if not message.EntryID or message.Saved is not True:
        raise ValueError("Draft must be saved and have no unsaved changes")
    parent = message.Parent
    drafts = store.GetDefaultFolder(16)
    if parent.StoreID != store.StoreID or parent.EntryID != drafts.EntryID:
        raise ValueError("Item is not in the selected account's Drafts folder")


class AccountNamespace:
    """Give upstream read helpers a namespace bounded to one DeliveryStore."""

    def __init__(self, namespace: Any, smtp: str):
        self.namespace = namespace
        self.account = account_for(namespace, smtp)
        self.store = self.account.DeliveryStore
        self.Stores = [self.store]

    def GetDefaultFolder(self, kind: int) -> Any:
        return self.store.GetDefaultFolder(kind)

    def GetItemFromID(self, entry_id: str, store_id: str | None = None) -> Any:
        if store_id and store_id != self.store.StoreID:
            raise PermissionError("Cross-account item lookup refused")
        item = self.namespace.GetItemFromID(entry_id, self.store.StoreID)
        if item.Parent.StoreID != self.store.StoreID:
            raise PermissionError("Item belongs to another DeliveryStore")
        if item.Class != 43:
            raise ValueError("Only mail messages are supported")
        return item
