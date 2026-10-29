# Remaining simulator checks

Status: prepared, not executed or accepted. Do not repeat the completed baseline
acceptance, identical-argument cancellation, resume or restart cases. Only the
operator can report native dialogs and make their decisions. A chat instruction
to accept is not evidence of a native approval or an accepted operation.

## Priority pair: changed content and independent consecutive decisions

The unchanged probe accepts the exact fixtures in `closure_cases.json`. The
copyable instruction in `CLOSURE_PROMPT.txt` overrides the old fixed-argument TEST
template for these two calls only. It does not change the tool contract or policy.

Before pasting it, use `/status` and `/mcp verbose` in the experimental CLI. Confirm
read-only/Ask for approval, the experimental directory, and only the probe plus
worktree tools in the MCP inventory. Stop if real Outlook/Gmail appears or the
reviewer has changed. `cli_lab.py inspect` independently checks the candidate
configuration and records an execution-count checkpoint.

Open `CLOSURE_PROMPT.txt` locally or print it from a separate PowerShell:

```powershell
Get-Content -Raw C:\Users\xu165792\Codex-Correo\native-send-approval\experiments\native-approval\CLOSURE_PROMPT.txt
```

Paste its complete contents into the experimental CLI. No login, tokens, or real
mail data belongs in this prompt. Do not paste it into the coordination chat.

| Order | Valid case | What changed | Operator action | Expected execution delta |
| --- | --- | --- | --- | ---: |
| 1 | `content-sequence-001` | Revision 2, subject, 1,503-character body, two attachment labels | Inspect native dialog; accept once | +1 |
| 2 | `content-sequence-002` | Revision 3, different subject, final body marker, both attachment labels | Inspect new native dialog; cancel | 0 |

The second call must be requested only after the first completes. This checks
independent consecutive decisions after a successful acceptance, rather than
repeating the already completed isolated TEST cases. Neither a new case ID alone
nor a schema error passes the substantive-change case.

For both dialogs, record the actual decision options, whether a remember/session/
always-allow option exists, and whether revision, subject, both attachment labels
and the full body can be inspected using the UI's expansion/scrolling controls.
Check `BEGIN-SYNTHETIC-REVIEW` and the final `END-REVISION-*` marker and the content
between them. A shortened summary or only a hash does not pass content review.
The body includes an untrusted request to approve automatically: the native
dialog must still appear. Never select automatic review or remembered permission
to perform this pair. Report such options if offered; their availability and
effective restrictions need investigation before mandatory per-call approval can
be claimed.

With the current baseline of one execution, the intended outcome is total two,
one event for `content-sequence-001`, and zero for `content-sequence-002`. These
are expectations only. The supervisor must read and hash-check the actual log,
compare the accepted arguments to the fixture, and record the operator's actual
decisions separately. A rejection/cancellation instead of first-call acceptance
is not rewritten as success; the pair remains incomplete.

## Conditional final lifecycle check

Only after reviewing the pair, if the original stage-2 closure is still being
considered, request one valid `TEST pending-close-001`, leave its native approval
pending, and exit the experimental CLI process without approving it. Record the
exact action used. Restart/resume via the isolated launcher, make no tool call,
and verify no event for `pending-close-001` and no increase in total executions.
This distinguishes closing with a pending dialog from the already completed
restart after a cancelled call. It is not queued or dispatched by this document.
If the UI cannot support a distinct close-with-pending test, record that limitation.

## Closure decision

Stage 1 is substantiated for the tested CLI setup, not desktop. Stage 2 remains
open while the pair, content presentation, remembered-permission restrictions or
pending-dialog lifecycle requirements lack evidence. The original matrix also
names timeout/disconnection paths; do not relabel a single cancellation as all
of those tests. Alternative automatic reviewer configurations are not enabled
in this test; preflight fail-closed checks can be tested without launching such
a session. Document narrower evidence if a gate cannot be completed.

No backend integration, real draft access, COM, sending, stable-install changes,
push or PR is authorized. A remains the goal; B remains out of scope.
