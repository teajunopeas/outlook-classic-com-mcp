# Experiment results — 2026-10-29

## Verdict

**Partial CLI validation: native acceptance, cancellation, and a fresh approval
for identical arguments, plus approval/cancellation after session resume and a
fresh client/session restart, were observed by the operator in CLI.**
The execution log independently confirms exactly one execution for `reject-001`
and none for `reject-002`, `resume-001`, or `restart-001`. This does not validate
the complete matrix or unrestricted remembered-permission behavior across sessions.
The desktop application remains unverified and does not block CLI testing.
No real sending integration is authorized by these results.

## Source review and minimum closure continuation

After milestone `4d8d65b`, a new repository review checked source, tests, commits,
the execution log and evidence journal. The stable checkout remains clean at
`2768ca8`, and `src`, production `tests`, installation scripts and project metadata
have no experimental changes. See [RETROSPECTIVE.md](RETROSPECTIVE.md).

The automatic simulator/launcher suite now passes **four** tests. The added
fail-closed test uses mocked effective configurations for reviewer `auto_review`,
approval policy `never`, and tool mode `auto`. Each is rejected before inventory
or interactive client launch. No automatic reviewer was enabled in a live test.
The prepared substantive-change fixtures pass the existing probe input schema
with mail/COM imports blocked; validation dispatched no tool call.

The baseline is still total one, solely `reject-001`, with zero `restart-001`.
The next manual pair is `content-sequence-001` then `content-sequence-002`, changing
revision, subject, body and attachment labels in consecutive valid calls.
[CLOSURE_CHECKS.md](CLOSURE_CHECKS.md) defines native decisions, content/permission
observations and expected counts. Both cases remain **prepared, not run** until
the operator reports the dialogs and independent event checks are completed.

The original per-call gate, remembered-permission restrictions and pending-dialog
lifecycle/presentation requirements are not waived. Stage 1 is substantiated for
CLI; stage 2 remains open. [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md) is conditional
planning only, not stage-3 implementation or permission for real mail.

## Current CLI observations and independent execution audit

The operator explicitly reported that all three valid calls displayed native
approval. Case IDs are labels, not decisions: despite its name, the first
`reject-001` call was accepted.

| Call in the reported sequence | Operator-observed native decision/result | Independently verified execution evidence |
| --- | --- | --- |
| `reject-001`, first call | Accepted; result `simulated_execution` | Exactly one matching event |
| `reject-001`, identical arguments repeated | A new native dialog appeared; cancelled; result `user cancelled MCP tool call` | No additional event; `reject-001` total remains one |
| `reject-002` | Native dialog appeared; cancelled; same cancellation result; no retries reported | Zero matching events |

The entire execution log currently contains exactly one record, with:

- Execution ID: `3f9ce11a-e606-45c9-a78a-fd4b9196d8e7`.
- Recorded UTC time: `2026-10-28T23:38:31.943764+00:00`.
- Arguments: revision 1, subject `Synthetic approval test`, body
  `Invented text. No real message exists.`, and label `fictional-report.txt`.
- Recomputed snapshot hash matches the recorded hash.
- Execution log SHA-256 at verification:
  `0efbaede839170142233035c9d382557314c4a88aafd2e925525d1e48473e6da`.

This is a point-in-time audit. The separate evidence journal retains the
operator's report and independent count/hash checks; the execution log was not
edited. The server records executions, not approval dialogs or cancellations.
Therefore identical pending arguments, native dialog appearance, cancellation
messages and absence of retries are operator observations. No per-dialog
before/after counts were independently sampled; the final total matches the
reported sequence. No authorization was inferred from chat files or screenshots.

The operator subsequently supplied `/status` and the verbose MCP inventory for
successful session `01a184de-f501-79f2-93bf-2c7285b28ffb`, CLI 0.165.0:

- Directory: `native-send-approval/experiments/native-approval`.
- Interactive permissions: `Read Only (Ask for approval)`.
- `outlook_approval_probe`: connected, exactly `outlook_send_draft`.
- `codex_worktrees`: connected, `create_worktree`,
  `get_worktree_creation_status`, and `list_worktrees`; none invoked by this test.
- No real Outlook server, Gmail connector, or alternative mail tool in this
  supplied interactive inventory; no MCP resources or resource templates.

This closes the earlier permission/catalog evidence gap for the supplied session
snapshot. It does not retroactively validate the earlier inconclusive session.
The pasted prior execution has the same execution ID as the one existing record;
showing it in restored history is not a new execution. A fresh independent count
check still finds exactly one event for `reject-001` and zero for `reject-002`.
The operator subsequently reported that valid call `resume-001` displayed a new
native approval after restoration and was cancelled. Independent log inspection
confirmed zero executions for `resume-001`, exactly one total event (still only
`reject-001`), and the same execution-log SHA-256 recorded above. This establishes
the observed post-resume approval/cancellation case in this CLI test. No automatic
execution was found at the checked pre-call and post-cancellation checkpoints.
It does not establish all remembered-permission choices or cancellation through
other lifecycle paths. Those remain pending.

## Fresh client/session restart milestone

The operator exited the previous experimental CLI and supplied the output of
`cli_lab.py start`, not `resume`, followed by `/status` and verbose MCP inventory.
Local launcher records independently show the latest launch has `resume: false`.
The new session is `01a184f4-2997-71c3-803c-aae70dcba224`, different from
`01a184de-f501-79f2-93bf-2c7285b28ffb`.

Before the call:

- CLI 0.165.0 used the experimental home and directory.
- Diagnostics returned reviewer `user`, policy `on-request`, and read-only.
- Actual `/status` showed `Read Only (Ask for approval)`.
- Actual MCP inventory showed the fictitious tool plus the same three worktree
  tools, with no Outlook/Gmail or alternative mail sender.
- Local execution count remained one; `restart-001` had zero events. Opening the
  fresh CLI did not create another execution at that checkpoint.

The operator then supplied the valid `restart-001` invocation and cancellation
result, `user cancelled MCP tool call` (`isError: true`), with no retry reported.
Afterwards, independent log checks confirm:

| Case | Recorded executions |
| --- | ---: |
| `reject-001` | 1 |
| `reject-002` | 0 |
| `resume-001` | 0 |
| `restart-001` | 0 |
| Total | 1 |

The execution log SHA-256 remains
`0efbaede839170142233035c9d382557314c4a88aafd2e925525d1e48473e6da`.
The native cancellation result is operator-supplied evidence; the unchanged log
and counts are independently checked evidence. No dialog button wording or
remembered-permission selection is inferred. This milestone covers a fresh
CLI process/session using `start` with `--no-daemon`; it is not a machine reboot,
desktop-app validation, or a complete proof of mandatory approval under every
permission choice. Only the experimental harness, English documentation and
tests are included in the local milestone commit; runtime evidence, login state,
SQLite databases and the virtual environment remain ignored and local. No push.

## First interactive CLI attempt: inconclusive, zero executions

The operator reported a successful isolated login and session
`01a184d9-d57f-7971-8c5f-8af561ed35ed` using CLI 0.165.0. No authentication codes,
tokens, account email addresses, or unrelated installer details are retained here.

Observed from the operator's report:

- `/mcp` listed connected `outlook_approval_probe` (one tool) and
  `codex_worktrees` (three tools). The diagnostic app-server's one-server catalog
  did not include this extra interactive-session worktree server. Its exact tool
  names should be confirmed with `/mcp verbose`; no worktree tool was authorized
  or invoked as part of this experiment.
- `/status` showed `Workspace (Ask for approval)` rather than the expected
  read-only permissions. Therefore the effective interactive sandbox was not
  established by the diagnostic `config/read` result.
- The agent said the probe was not exposed directly and refused `TEST reject-001`
  without a tool call. No native approval dialog was observed. This is not a
  human rejection test and is not a pass.
- Independent local event inspection confirmed zero total executions after the
  attempt. The operator report is recorded separately in the evidence journal
  with decision `not_attempted`, not `rejected`.

The launcher now explicitly supplies `--sandbox read-only`,
`--ask-for-approval on-request`, and `approvals_reviewer="user"` on both fresh and
resumed launch paths. These are corrective startup inputs; their interactive
effect must still be checked with `/status`.

The initial operator prompt now permits metadata-only discovery through
`functions.exec` / `ALL_TOOLS`, when that runtime is available. Deferred tool
visibility is a hypothesis for the agent's refusal, not an observed fact about
that session. Only the exact discovered simulator tool may subsequently be
called through the normal tool dispatcher. No direct Python/MCP transport call,
alternate mail tool, automatic reviewer, or synthetic approval is permitted.
The simulator itself is unchanged.

Three automated tests pass: the existing simulator protocol test and two launch
checks covering explicit human-review flags on fresh/resumed sessions and
process-local environment isolation. These tests do not demonstrate native
human approval.

## CLI continuation authorized by the user

The existing simulator is unchanged. `cli_lab.py` adds diagnostics, isolated
interactive login/start/resume, execution counts and separate operator reports.
It never fabricates a native approval or feeds approval keystrokes to the CLI.

Observed on 2026-10-29 with Codex CLI/app-server 0.165.0:

- `initialize` returned the exact experimental `codexHome`.
- `config/read` returned `approval_policy = on-request`,
  `approvals_reviewer = user`, `sandbox_mode = read-only`, isolated file-based
  authentication, and disabled apps, shell tools and hooks.
- Effective MCP configuration contained only `outlook_approval_probe`, with
  `outlook_send_draft` set to `prompt`, using the experimental interpreter, probe
  path and event path.
- `mcpServerStatus/list` connected to the simulator and returned exactly one MCP
  server and one tool, `outlook_send_draft`; no real Outlook server, MCP resources,
  or alternative MCP sending tools appeared.
- Execution count was zero before and after diagnostics. Evidence is in ignored
  `runtime/cli-observations.jsonl`, separate from simulator execution events.
- Initially the fresh experimental home reported `Not logged in`. The operator
  subsequently reported successful interactive login in that home. No stable
  credentials or approvals have been copied.

These configuration observations come from CLI diagnostics, separately from the
operator's interactive observations above. The launcher uses `--no-daemon` to avoid the shared daemon;
the operator must confirm `/status` and `/mcp` in that actual session. No
`--approve-for-me` or `auto_review` is used for test execution.

| Valid-call test | Native human decision | Execution result | Status |
| --- | --- | --- | --- |
| Accept one valid call | Operator accepted first `reject-001` | Exactly one event | Observed in current CLI session |
| Cancel pending valid calls | Operator cancelled repeated `reject-001` and `reject-002` | No extra events; zero for `reject-002` | Observed in current CLI session |
| Repeat identical arguments | Operator observed a new native dialog for identical `reject-001` | Still exactly one event after cancellation | Observed in current CLI session |
| Different case ID | Operator observed native dialog for `reject-002` | Zero events after cancellation | Observed in current CLI session; substantive content changes remain untested |
| Explicit reject/deny option distinct from cancel | Not reported | Not established | Pending if client exposes a distinct option |
| Resume session | Operator observed a new native dialog for `resume-001` and cancelled | Zero `resume-001` events; total unchanged at one | Observed in this CLI test |
| Fresh-session client restart | Operator supplied native cancellation for `restart-001` in a new session | Zero `restart-001` events; total unchanged at one | Observed in this CLI test |

Schema rejection of `confirm=true` is **not** evidence of native human approval.
Only valid calls are used for these five cases. Follow [CLI_GUIDE.md](CLI_GUIDE.md)
and report each dialog decision separately from the execution count.

## Initial preparation observations (before CLI authorization)

- Stable checkout was clean at
  `2768ca86246f12b00aff9affcc663c41fb4b1edf`, branch
  `feature/account-bound-drafts`. Its checked-out files remain unchanged.
- Created sibling worktree `../native-send-approval`, branch
  `experimental/native-send-approval`, at that exact revision.
- Created a fresh experimental virtual environment and client home under
  `experiments/native-approval`. No stable SQLite database, approval state,
  credentials, or server package was copied.
- CLI identifies as `codex-cli 0.165.0`. Running process paths identify standalone
  and shared app-server/code-mode-host releases `0.165.0`.
- Process inventory showed CLI launchers, including a `resume --last` invocation,
  and the managed shared daemon. This does not identify an independent visual
  client version or prove that a visual client can select an isolated daemon.
- The OpenAI program directory examined contained CLI/host binaries. The
  installed-package query returned no matching OpenAI package for this user.
  No independent visual client was launched and no existing process was stopped.
- With process-local `CODEX_HOME` set to the fresh candidate home,
  `codex mcp list --json` listed exactly `outlook_approval_probe`. This is the
  configured CLI server list, not an observed visual tool catalog.
- `codex app-server --strict-config --print-startup-config` succeeded and reported
  `appServerVersion: 0.165.0`. Its output contains configuration requirements,
  not effective reviewer/tool approval settings. Those remain unverified.
- `codex --strict-config mcp list --json` is unsupported in this version. The
  non-strict list command and separate strict startup validation were used.

## Protocol verification

Python 3.12.16, MCP SDK 1.27.0, independent virtual environment. The exact installed
dependency versions are in `requirements.txt`. The Windows SDK dependency graph
includes pywin32; no Outlook integration is imported or used.

`python -m unittest discover -s experiments/native-approval -v` passed one
end-to-end stdio protocol test, exercising:

- MCP initialization and a single-tool catalog.
- No execution at initialization/catalog listing.
- Rejection of `confirm=true` with no event.
- Rejection of an unknown sending tool with no event.
- Two direct synthetic calls producing distinct execution IDs and matching hashes.
- Restart without replay of previous calls.
- Import blocking of `pythoncom`, `win32com`, and `outlook_mcp` in the server.

The two automated-test events were confined to a temporary directory removed by
the test. Separately, `runtime/manual-events.jsonl` now contains the single
operator-accepted execution described above.
These checks verify the harness, not a human approval boundary. The simulator
does not assert that its caller has obtained authorization.

## Remaining acceptance work

Do not repeat the observed acceptance/cancellation/identical-arguments cases just
to populate the originally suggested case IDs. Remaining CLI checks include:

- Preserve both confirmed session IDs and their interactive read-only/MCP
  inventory snapshots. The observed `resume-001` and `restart-001` cancellation
  cases are complete; do not repeat them merely to populate the matrix.
- Remembered-permission behavior and any effective restriction on suppressing
  later dialogs. One-time approval observations do not establish that restriction.
- A substantive content/revision change, long content and simulated attachment
  presentation, and agent instructions requesting autoapproval.
- Explicit denial if distinct from cancellation, and separate close/interruption/
  disconnection/timeout behavior while approval is pending.
- Remaining configuration-policy cases from the original matrix; no automatic
  reviewer has been enabled for this test session.

Every desktop-client case remains pending, including
acceptance, rejection, cancellation, remembered permissions, resume/restart,
automatic review, pending-dialog interruption and long-content presentation.
Effective desktop-session policy and the absence of alternative sending tools
must be verified before running desktop cases. CLI results must be labeled CLI
only; desktop acceptance is separate and does not block the current experiment.

The active installation and configuration were not edited. No mail access, COM
calls, real drafts, actual sends, push, PR, package publication, or merge occurred.
Guarantee A is unproven; guarantee B remains outside the experiment's scope.
