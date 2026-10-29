# Original approval plan versus repository evidence

Reviewed on 2026-10-29. This document separates source implementation, automated
checks, operator observations and proposals. It does not authorize real mail.

## Evidence and provenance

The original five-stage plan is available in the user-supplied task. A standalone
verbatim version was not found among the tracked repository documents inspected.
The stage mapping below is a reconstruction from that supplied plan, checked
against actual source, commits and artifacts. Later design details in
[INTEGRATION_PLAN.md](INTEGRATION_PLAN.md) are proposals, not recovered original
implementation or proven client features.

Repository evidence reviewed:

- `git log`, `git show --stat 4d8d65b`, and the working-tree status.
- `git diff 2768ca8 HEAD -- src tests scripts pyproject.toml`: no changes at review
  baseline. The stable checkout is clean at
  `2768ca86246f12b00aff9affcc663c41fb4b1edf`; experiment HEAD was
  `4d8d65b45c001b8187058142ae71930ac7a6a649` before this documentation update.
- [RESULTS.md](RESULTS.md), [CLI_GUIDE.md](CLI_GUIDE.md), [README.md](README.md),
  the ignored execution log and the separate ignored evidence journal.
- [Probe](probe.py), [launcher/preflight](cli_lab.py), configuration template,
  preparation script and all experimental tests.
- [Approval ledger](../../src/outlook_mcp/approval.py),
  [public mail tools](../../src/outlook_mcp/tools/bound_mail.py),
  [mail adapter](../../src/outlook_mcp/client/bound_mail.py),
  [sender validation](../../src/outlook_mcp/client/sender.py),
  [bridge](../../src/outlook_mcp/bridge.py), server and entrypoint.
- [Account-bound tests](../../tests/test_account_bound_drafts.py),
  [historical validation](../../docs/VALIDATION.md),
  [account-bound design](../../docs/ACCOUNT_BOUND.md), and
  [development log](../../docs/DEVELOPMENT_LOG.md).

The stable installation version `0.5.0+accountbound.2` is documented in those
records and the source project metadata. This review did not import, reinstall,
or run that installed backend. The historical remote equality/push reports are
historical evidence, not a fresh remote query. No fetch, push or PR was needed.

## Objective and trust boundary

The original objective was to test native per-tool approval before altering the
mail backend. The manual `SEND <hash>` phrase is visible to the agent and cannot
independently prove a human decision. A client-owned dispatch decision could
provide an independent human step for a particular tool call.

- **A, the objective:** under the verified client version/configuration, the
  sending tool call is not dispatched without a fresh manual decision for that
  call. Native approval must describe the exact operation/content being reviewed.
- **B, outside scope:** prevent any alternative mail program, COM route, policy
  modification, ledger tampering, or permission escalation from bypassing the
  system. Same-user code/configuration, a hash, SQLite and agent instructions do
  not provide that isolation. No complete administrator-free B was established.

A content hash identifies a version; it is never a credential. Native tool
approval also is not a general assertion that any process under the same user
can be trusted, nor a delivery receipt.

## Original stages and current status

| Original stage and objective | Implemented | Automated evidence | Manual evidence | Pending / decision |
| --- | --- | --- | --- | --- |
| 1. Inventory/isolation: separate branch, Python, client configuration, state and mail-tool catalog | Sibling worktree and `experimental/native-send-approval`; fresh venv and `CODEX_HOME`; file-based login; explicit user/on-request/read-only flags; no shared daemon | Launcher policy/environment tests; diagnostic initialize/config/read/connected inventory and unchanged counts | CLI 0.165.0 `/status` and verbose `/mcp` for the two successful sessions; probe plus three worktree tools, no real mail tools | Substantiated for CLI. Original desktop priority was explicitly changed by the user to CLI; desktop isolation remains untested and does not block CLI |
| 2. Native proof of concept without COM: one human decision per synthetic call and adequate presentation | Existing standalone synthetic `outlook_send_draft`, append-only execution events, no `confirm` field, no queue/retry | Protocol test with forbidden mail/COM imports; schema rejection; no startup/restart replay; four experimental tests now pass including unsafe-policy preflight refusal | Acceptance, cancellation, identical arguments requiring a new dialog, post-resume and fresh-session restart cancellation | Partial only. Substantive changes/consecutive sequence, presentation, remembered-permission restrictions and original pending-dialog lifecycle cases need evidence |
| 3. Bind native decision to a concrete real draft revision while preserving backend guarantees | Not implemented; production contracts still require `confirmation_phrase` | Existing backend tests and historical validation provide a baseline, not native integration tests | No real draft or send observations in this experiment | Proposed only in integration plan; original gate prohibits progressing without adequate stage-2 acceptance |
| 4. Viability report distinguishing documented/observed/pending per client | Existing RESULTS and this retrospective; scope and evidence sources recorded | Source/commit/log comparisons; hashes and counts independently checked | Operator-reported CLI dialogs explicitly separated from server events | Update after pending manual tests; never extrapolate to desktop or B |
| 5. Later review, promotion and return to stable | Stable unchanged; experiment can be closed without reconfiguring stable; local milestone commit | Local stable HEAD/status and exact experimental commit scope checked | Experimental session restored and a new CLI session opened; no stable reinstall or mail operation | No merge, push, PR, package publication or real test. Any real testing/promotion requires a separate later decision |

The five rows reconstruct the original plan's intended stages. Stage 4 reporting
can progress while stage 2 is pending; that is not approval to implement stage 3.

## Commit and observed results

Local commit `4d8d65b` is titled
`Add isolated CLI approval probe and record native approval milestone`.
Its eleven new files are exclusively under `experiments/native-approval`.
It contains three automated tests and the documented CLI milestone; it contains
no production implementation changes, runtime logs, credentials or databases.

| Valid simulator operation | Operator observation | Independent event evidence |
| --- | --- | --- |
| First `reject-001` | Accepted native approval, despite the case name | Exactly one execution |
| Identical `reject-001` repeated | New native approval; cancelled | No additional execution |
| `reject-002` | Native approval; cancelled, no retry reported | Zero executions |
| `resume-001` | New approval after resume; cancelled | Zero executions; total one |
| `restart-001` | Cancellation after verified new CLI process/session | Zero executions; total one |

The successful original/restored session was
`01a184de-f501-79f2-93bf-2c7285b28ffb`; the verified fresh session was
`01a184f4-2997-71c3-803c-aae70dcba224`. Earlier refusal to discover the probe was
inconclusive and is not counted as a native rejection. A pasted status from the
coordination session with real Outlook/Gmail tools was correctly excluded from
experimental-isolation evidence. No real mail tool was invoked.

The last independently rechecked baseline is exactly one execution, solely for
`reject-001`, ID `3f9ce11a-e606-45c9-a78a-fd4b9196d8e7`. Execution-log SHA-256:
`0efbaede839170142233035c9d382557314c4a88aafd2e925525d1e48473e6da`.
Dialog appearance and decisions are operator observations; the event log only
proves which handler executions were recorded. Replayed historical terminal
output is not a new execution. Initial three-call counts were checked afterwards,
not independently sampled at each individual dialog. Later lifecycle cases have
separate pre-call and post-result checkpoints.

## Automatic checks: what they do and do not establish

- The experimental protocol test initializes a real stdio simulator, checks the
  sole tool, rejects extra `confirm` and unknown tools without events, performs
  synthetic calls in a disposable directory, and checks no replay on restart.
  Its import blocker rejects `pythoncom`, `win32com` and `outlook_mcp` in the server.
- Launcher tests cover explicit policy on start/resume and process-local home.
- The added fail-closed test supplies mocked effective `auto_review`, `never`, or
  tool `auto` configurations. Diagnostics reject them before inventory or client
  launch. It never enables automatic review in a live test. This verifies the
  launcher check, not prevention of every later policy edit or saved permission.
- Historical `docs/VALIDATION.md` records **122 simulated backend tests**. Source
  review confirms relevant cases. Those tests were not rerun in this task and
  are not misreported as new experimental checks. No existing live verification
  script or real Outlook entrypoint was executed.

## Simulator versus real sending

| Property | Experimental probe | Existing real backend |
| --- | --- | --- |
| Effect | Writes one local JSONL execution event | Calls Outlook `Send()` once after verification |
| Data source | Agent-supplied invented arguments | Saved MailItem retrieved by exact SMTP/EntryID within DeliveryStore |
| Sender and recipients | Not modeled | Effective sender, delegated identity, To/CC/BCC and resolved recipients |
| Revision | Arbitrary positive integer argument | Outlook LastModificationTime plus complete observable snapshot |
| Body | One synthetic string | Final text, HTML, format and RTF hash, including inherited content |
| Attachments | Labels only, never opened | Hashes bytes extracted from embedded by-value attachments |
| Reservation/expiry/replay | No ledger or expiry; repeated direct calls can execute | Durable ten-minute, content-bound reservation; single transactional claim; busy states |
| Authorization | Native client decision only, when correctly configured | Agent-visible exact SEND phrase plus reservation; not independent human authentication |
| Metadata | `destructiveHint=true`, `openWorldHint=false` | Current SEND tool has `destructiveHint=false`, `openWorldHint=true` |
| Result | Simulated event, not mail | `submitted` means handed to Outlook, not delivered; uncertainty blocks retry |

The metadata difference is an integration acceptance issue: probe success cannot
be assumed to transfer to the current real tool's annotation/routing. A proposed
native contract must be retested with its intended annotations and namespace in
another COM-free harness before it can be used with the backend.

## Protections that integration must preserve

- Exact unique SMTP selection, no default fallback, DeliveryStore scoping,
  cross-store lookup refusal and rejection of unsupported delegated identities.
- PROPERTYPUTREF for SendUsingAccount and sent-folder binding; verify effective
  sender and valid draft again after Save, without silently repairing tampering.
- Saved, unsent, unsubmitted MailItem in that account's actual Drafts folder.
- Same-draft edits; native reply/forward origin; invalidate existing reservations
  before mutation, including partial failures.
- Full snapshot including identities, item/store/folder, revision, recipient
  type/address, subject, final bodies and format, RTF hash, conversation origin,
  delivery options and embedded attachment hashes. Reject unresolved recipients
  and unsupported attachment types; remove temporary extraction files.
- Ten-minute expiry, revocation, replacement invalidation, `BEGIN IMMEDIATE`,
  single claim and expiry recheck at the durable attempted transition.
- No Save/rebind during send verification; reject changed content; durable
  attempted record before Send; `submitted`/`uncertain` semantics and busy-state
  blocking across process restarts.
- Bridge retries only explicitly read-only operations, never draft writes or
  send. Timeout/disconnection does not prove a dispatched COM mutation stopped.
- Explicit send-enable switch, no delayed queue, no automatic retry and no
  interpretation of email text or chat files as authorization.

The existing ledger stores hashes/states, not message bodies. Native integration
must preserve that privacy property or explicitly justify and separately review
any new storage. There is no atomic transaction or immutable lock spanning Outlook
and SQLite; a final-read-to-Send race with external editors already exists and
must be disclosed, not described as solved by native approval.

## Readiness

Stage 1 is substantiated for the identified CLI setup. Stage 2 is not yet closed
under the original mandatory matrix. [CLOSURE_CHECKS.md](CLOSURE_CHECKS.md) selects
the immediate nonredundant pair and states the remaining hard gates. Prepared
fixtures and instructions are not executed tests. Integration planning is safe
to review now, but implementing native real-send behavior remains gated.
