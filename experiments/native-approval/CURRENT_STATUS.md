# Current acceptance matrix — 2026-10-30

This matrix supersedes pending entries in older RESULTS/RETROSPECTIVE checkpoints. This is a partial experimental milestone, not a real-send implementation or a desktop approval guarantee.

| Check | Evidence | Status |
| --- | --- | --- |
| CLI acceptance, cancellation, repeated identical arguments | Operator observations and execution audit | Observed in CLI 0.165.0 |
| CLI resume and fresh session | Operator observations and unchanged counts | Observed in CLI 0.165.0 |
| Changed content and consecutive independent decisions | Operator observations, accepted fixture and log audit | Observed; no unnecessary rerun |
| Full body inside native card | Truncated; full pending arguments above | Not demonstrated |
| Complete pending arguments reliably associated with approval | Exact future contract and UI inspection needed | Pending |
| Effective restriction against remembered approval | No remember option observed in first card only | Pending; no universal guarantee |
| Close with pending approval, interruption, disconnection, supported timeout | Not completed in recovered checkpoint | Pending human supervision |
| Desktop isolation, policy, inventory and decisions | CLI does not establish desktop behavior | Pending human supervision |
| Native real-send backend | Stable SEND phrase unchanged | Not implemented; second milestone |

## Evidence

The original ZIP contains two events: reject-001 and content-sequence-001, one each. Both canonical argument hashes were independently recalculated on 2026-10-30. Log SHA-256 matches the historical audit: `72e93e065fa0456b150b3600457bff7ed079d2a64dde28dfed408ed07a10a634`. Zero events alone do not prove dialog appearance or cancellation. No runtime, session, login or credential files are published.

## Reproduction

Use the isolated interpreter with requirements.txt, then run `python run_tests.py`. The supervisor has an external 60-second deadline, workspace-local temporary files and unbuffered phase diagnostics. Timeout stops only the newly created test process tree, never Outlook or another user application.

The earlier restricted attempt could not write its default temporary config and later stalled without phase diagnostics. In the current environment, all four tests completed with system Python 3.14, MCP 1.29.0 / AnyIO 4.14.2 in 13.534 seconds. A separate fresh virtual environment installed the exact requirements.txt successfully; all four tests also passed there with Python 3.14, MCP 1.27.0 / AnyIO 4.15.1 in 10.001 seconds, including protocol teardown/restart. The original run used Python 3.12.16, so this is not an identical interpreter reproduction. Neither successful run isolates the earlier stall to a particular dependency or permission.

## Manual continuation and second milestone

Use a fresh isolated client home; do not copy the old authentication or approvals. Verify actual session policy/catalog before asking the user for the missing synthetic decisions. No automated Allow clicks. Do not enable remembered/automatic approval to manufacture a pass. If mandatory per-call review cannot be enforced, document the limitation and retain the native real-send gate.

The next milestone is a COM-free review/ledger prototype, then a separately validated native backend. Preserve account/store binding, complete snapshot, final expiry, single claim and attempted-before-Send; uncertain outcomes never retry. Test the exact intended schema/annotations in the chosen client. No production activation or real send follows automatically.

The local export/queue integration is separate: do not import its four-minute delay, scheduler, HMAC envelopes or private runtime into this immediate-send fork. No active installation, COM connection, real draft or real send was used here.
