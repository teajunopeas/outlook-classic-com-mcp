# Proposed native approval integration — design only

No part of this backend integration is implemented by this document. All paths,
new contracts and mode names below are proposals. Stable defaults, installed
files, the SEND phrase and public contracts remain unchanged. The objective is
A for a pinned, verified CLI configuration, not B. Desktop is unvalidated.

## Prerequisites and smallest next step

First finish the selected simulator checks and resolve any mandatory per-call
approval blocker. Passing a few one-time dialogs is insufficient if remembered
permission can bypass the next decision and cannot effectively be prohibited.
Do not use an agent instruction as the restriction. If the original mandatory
matrix cannot be completed, keep stage 2 open and report the narrower evidence.

The next implementation step to propose after that gate is a **COM-free review
contract prototype only** under the experimental directory, using synthetic
snapshots and temporary ledger files. It should model the exact intended tool
annotations, schema, review payload, expiry and single claim, without importing
Outlook or registering the stable server. Do not change the real send adapter in
that first step. That step itself is a proposal, not an instruction to implement
it in the current task.

Acceptance for that prototype:

1. Full sender/recipient/body/attachment review is inspectable in native dialogs.
2. Valid consecutive calls and changed arguments each request a fresh decision.
3. A lied-about review, stale hash, stale revision, wrong account/store, expired
   or consumed reservation produces zero fake Send calls.
4. Two concurrent claims permit at most one fake attempt; interruption does not
   replay it; every mutating callable stays nonretryable.
5. No alternative sending tool, real Outlook import or stable-state access.

Only after reviewing that result should an actual experimental backend change
be authorized. No real draft or send test follows automatically.

## Components that would change later

| Component | Proposed change | Preserve / review constraint |
| --- | --- | --- |
| `src/outlook_mcp/tools/bound_mail.py` | Register a native-experimental preview/send schema only in an explicit server-selected mode. Add structured reviewed content and explicit snapshot hash; remove phrase only in that mode | Stable phrase schema/default retained. No agent argument selects a weaker mode. No second send tool bypasses the native gate |
| `src/outlook_mcp/approval.py` | Add a separate native claim policy and persisted policy/schema version for each reservation; bind supplied hash/content to stored hash under the same claim transaction | Keep hash-only persistence, ten-minute expiry, replacement invalidation, revocation, BEGIN IMMEDIATE and state transitions. Existing rows default to legacy phrase policy; cross-mode use rejected |
| `src/outlook_mcp/client/bound_mail.py` | Reuse snapshot/preview and factor a common one-attempt submission path after policy-specific claim and review checks | Re-fetch and compare same draft; preserve embedded-byte hashes, sender/draft/store checks, final expiry check, attempted-before-Send and uncertainty semantics |
| New experimental review-schema/renderer module, location chosen after prototype | Deterministic full review payload derived by the server from the final snapshot; no agent-written summary accepted | No executable email markup, truncation or omitted BCC; schema-versioned canonical encoding |
| `src/outlook_mcp/server.py` and possibly a dedicated experimental entrypoint | Explicit opt-in registration/instructions for native mode; stable remains phrase mode. Separate package/environment/client home/state | Never connect the current real entrypoint during COM-free tests: it starts the bridge and attaches to Outlook before serving MCP |
| `src/outlook_mcp/client/sender.py`, `bridge.py` | Intended unchanged; audit shared calls and add regression checks if factoring affects them | Exact SMTP/PROPERTYPUTREF/DeliveryStore/draft validation and read-only-only retry remain mandatory |
| Experimental client configuration and preflight | Pin mode, exact server/tool and approval policy; verify actual session inventory/reviewer, not just TOML | `user`, `on-request`, per-tool `prompt`; no auto reviewer. Stable server excluded from the experimental catalog |
| Tests and experimental documentation | Synthetic review/state/stdio tests, CLI acceptance record and explicit mode/trust limitations | No new live Outlook/CI mail test, installation change, push or PR |

The proposed native namespace must be tested again. Current probe annotations
are destructive=true/openWorld=false; current backend SEND annotations are
destructive=false/openWorld=true. Choose and justify intended native annotations
(sending is an external side effect), then exercise those exact annotations in
the COM-free prototype. Never infer routing equivalence from the tool name.

## Proposed review and send contract

The existing preview saves/resolves the same real draft before taking its final
snapshot. A future experimental preview would return:

- `account_smtp`, `entry_id`, `approval_id`, `snapshot_hash`, expiry and a versioned
  `review` object derived from that final snapshot, not a hand-written summary.
- The review object's complete observable content, including store/folder and
  revision, so its canonical digest can be compared to the reservation's hash.
  Use one canonical content model; do not hash an unrelated prose summary.
- If a separate readable rendering is necessary, it must be deterministic from
  that exact review object and the server must verify the supplied rendering too.

Candidate native send arguments are `account_smtp`, `entry_id`, `approval_id`,
`snapshot_hash`, and `review` (plus only a deterministically checked rendering if
the UI needs it). The existing integer synthetic revision is not an Outlook
version credential. A proposed review schema must carry actual snapshot revision
and identifiers. The hash and reservation ID are content references, not proof
that a person clicked approval; the verified client supplies that step.

The current 1,503-character simulator case already exposed a limitation: the
native card truncated the body while the pending call above showed it in full.
The prototype must test that this complete pending display is unambiguously the
call/version being approved and remains inspectable through the decision. Do not
describe it as full-body display inside the card. If the actual review payload
cannot be inspected and associated reliably, the presentation gate fails even
when per-call prompting works.

To preserve hash-only ledger storage, preview may return the complete snapshot
without persisting plaintext in SQLite. On send, digest the submitted review and
compare with the stored hash, then independently digest the freshly read real
draft and compare again. If schema versioning introduces a wrapper, define the
digest domain consistently at preview, claim and reread; do not accidentally
compare two differently serialized representations.

## What the user must be able to inspect

| Field | Required presentation |
| --- | --- |
| Operation and version | Immediate submit of this draft once; account, item/store, revision, expiry, reservation and hash as references |
| Sender | Exact effective SendUsingAccount SMTP; delegated identity explicitly absent or matching permitted own identity |
| Recipients | Separate To/CC/BCC groups; every resolved SMTP and recipient type; no hidden BCC or names-only ambiguity |
| Subject | Complete final subject |
| Body | Complete final text including quoted/replied/forwarded content; HTML source or a safe faithful inspectable representation, body format and any alternate-body distinctions |
| Attachments | Every incorporated filename, size, type, position and SHA-256 of embedded bytes; never only local source paths |
| Additional bound content | Conversation origin, folder and delivery/receipt/importance/sensitivity/defer options that affect the snapshot |

The native decision must refer to those same call arguments. A previous chat
preview plus a native dialog showing only an EntryID/hash is insufficient under
the original plan. Expansion/scrolling may be acceptable if all content can
actually be inspected and that behavior is tested. Default-truncated content
that cannot be expanded fails the presentation gate. Never run markup/scripts
from email content. Control characters or misleading labels must be escaped.

Existing RTF handling hashes bytes but does not provide a human-readable RTF
review. Do not claim that hash proves readable content. If the active format
cannot be presented faithfully, fail closed for that format until a separate
safe rendering method has been designed and verified. Do not silently convert
or Save at send time to make review simpler.

If native argument presentation cannot satisfy this, document a separate form
elicitation experiment only after advertised and observed client support. A
server-authored form could show the registered content and accept only a channel
response, followed by reread. That runs inside a dispatched MCP call; it is not
equivalent to A's pre-dispatch native gate. No URL forms or external UI are
proposed, and no elicitation is implemented here.

## Proposed execution sequence and state rules

1. Draft editing continues through existing account-bound tools. Invalidate
   active reservations before any mutation, even if a partial mutation fails.
2. Preview resolves recipients, saves, checks effective account/draft/store and
   reads complete final content, including embedded attachments. Register one
   active, expiring reservation for that item under the server-selected policy.
3. The client presents the exact proposed native send call and waits for a human
   decision. The backend is not entered on native rejection/cancellation.
4. On dispatch, the backend atomically claims the matching active reservation
   for the account/item/mode. Duplicate or concurrent claims fail. Enter
   `checking` before potentially lengthy verification. Validate supplied
   `snapshot_hash`, review digest and any rendering against the registered hash.
   A review mismatch after claim is marked `rejected`; it cannot silently revive
   the reservation through a rolled-back error path.
5. Retrieve the draft again via exact SMTP and DeliveryStore; require saved,
   unsent, unsubmitted MailItem in the actual Drafts folder. Verify sender and
   delegated identity. Re-read the full snapshot and embedded attachment bytes.
   Any mismatch, including revision, origin, bodies, recipients or attachments,
   rejects and consumes the claimed reservation. Require a new preview and new
   native decision; never replace the approved snapshot behind the dialog.
6. Recheck draft/sender after snapshot work, without Save, rebinding, moving or
   resolving recipients during the send path. Atomically mark `attempted` only
   if not expired at that final transition. This preserves expiry both while the
   dialog is pending and during the final read/hash work.
7. Call `Send()` exactly once, then record `submitted`. If execution has begun
   and the outcome is uncertain, preserve `uncertain` or the durable attempted
   state; never replay. `submitted` is not delivery confirmation.

SQLite and Outlook cannot be made one atomic transaction by this plan. There is
an external-editor race after the last read and before Send. The server rejects
changes observable at its verification points; it cannot promise detection of
every edit in that tiny interval. If stronger atomic version binding is required,
stop for a different Outlook-side design rather than claiming native approval
solved that race or sending a silently created replacement item.

## Cancellation, reuse and retries

- A native cancellation before dispatch produces no backend attempt. The stored
  preview may still be active because the backend never received the call; it
  is a content reservation, not reusable human permission. A later valid call
  still requires a new native decision. Do not falsely claim server-side
  cancellation consumes a reservation without a client-to-server notification.
- Once claimed, a reservation never becomes active again automatically. Reject,
  expiry, submission, uncertainty or crash cannot be converted into an automatic
  retry. Changing preview invalidates previous active reservations.
- Keep busy blocking for checking/attempted/uncertain/submitted across processes
  and restarts. Do not delete SQLite or clear those states to retry.
- Preserve bridge no-retry classification for all writes, including preview and
  sending. A disconnected client after dispatch does not prove a queued/running
  COM operation was cancelled. After that boundary, report possible execution
  and block repetition instead of promising that cancellation prevented Send.
- No timer, scheduled send, background replay or automatic fallback tool. Exact
  native permission behavior must remain independently verified after client,
  namespace, annotation or approval-policy changes.
- Native mode trusts the client boundary for A. It cannot establish a signed
  human attestation on the server. Same-user mutable code/configuration and
  alternate programs remain B and are not solved by adding another token.

## Proposed tests and later checks

Start with temporary ledgers, synthetic snapshots and a fake Send counter:

- Wrong sender/account, Save-changing account, delegated identity, wrong store,
  wrong folder, unsaved/already-sent/submitted/non-MailItem draft: zero attempts.
- Changed resolved To/CC/BCC, subject, text/HTML/RTF/format, revision, origin,
  delivery options, attachment name/type/position/size/bytes: rejection; no attempt.
- Supplied displayed review differs from registered review despite matching
  identifiers, forged summary, wrong hash/mode/schema, malformed/missing field:
  reject without Send; no silent version update.
- Expired before dispatch, expired while dialog waits, and expired during final
  snapshot hashing: zero attempts. Verify the last attempted-transition check.
- Invalidated/revoked/consumed reservations, repeated calls and concurrent
  processes: at most one attempt; legacy/native reservations cannot cross modes.
- Native cancellation before dispatch: no invocation; subsequent call requests
  a new decision. Shutdown with pending approval cannot replay later.
- Failure before Send, crash after durable attempted, disconnect during/after
  Send, and ledger write failure after submission: preserve conservative state,
  no retry, no false delivery claim. Separate no-call from uncertain-call cases.
- Exact intended stdio catalog/annotations/arguments, server instructions and
  client policy; stable send absent from the experimental client catalog.
- Explicit permission restrictions, no automatic reviewer, full readable content,
  independent decisions for consecutive/changed calls, resume/restart and long
  content presentation in the actual CLI. Mocks cannot pass UI criteria.

Historical backend tests should be rerun in an isolated dev environment with
COM replaced/blocked after actual integration changes; do not treat a historical
122-pass report as current regression execution. Revalidate only the affected
simulator checks when fixtures/contracts change rather than rerunning accepted
UI cases without a reason.

No live mail follows from these tests. A later review would separately decide
whether any narrowly scoped real-draft test is appropriate; any actual send is
another explicit authorization. No packaging, active-install update, merge,
push, PR or promotion occurs in this task.
