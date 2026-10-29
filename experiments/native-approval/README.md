# Native send approval experiment

Only stages 1 and 2 are in scope. This directory is independent of the Outlook
package. It never opens Outlook, reads attachments, or sends mail. All test
content must be invented. Attachment strings are display labels, never paths to
open. The hash identifies synthetic content; it is not an authorization token.

## Current result: partial native approval observations in CLI

See [RESULTS.md](RESULTS.md) and the [CLI operator guide](CLI_GUIDE.md). The user
has authorized Codex CLI as the primary client. Its isolated effective
configuration and diagnostic one-tool MCP catalog have been checked. The operator
has now observed native acceptance, cancellation and a new dialog for identical
arguments in the current CLI session. The execution log contains exactly one
`reject-001` event and zero `reject-002` events. After session resume, the operator
also observed a fresh approval for `resume-001` and cancelled it; independent
inspection confirms zero `resume-001` events and the same total of one. The
fresh-session restart also produced native cancellation for `restart-001`, with
zero matching events and the total unchanged at one. The desktop app and remaining
matrix are pending. Do not adapt the real sending backend on the strength of this
partial validation.

The server deliberately does not implement approval itself: an execution event
means the call reached the handler, not that a human approved it. A direct MCP
caller can execute the simulator. Only observation in the selected client can
establish guarantee A.

## Local preparation

Use a separate Python 3.12 environment in this directory:

```powershell
python -m venv experiments/native-approval/.venv
& experiments/native-approval/.venv/Scripts/python.exe -m pip install -r experiments/native-approval/requirements.txt
& experiments/native-approval/.venv/Scripts/python.exe -m unittest discover -s experiments/native-approval -v
& experiments/native-approval/.venv/Scripts/python.exe experiments/native-approval/prepare.py
```

Run from the experimental worktree root. `prepare.py` creates
`runtime/client-home/config.toml` and refuses to overwrite it. It does not launch
a client, read the active home, copy credentials, or migrate approvals. Runtime
state and the virtual environment are ignored by Git. The MCP SDK depends on
pywin32 on Windows; the simulator never imports `pythoncom` or `win32com`. The
protocol test installs an import blocker for both and for `outlook_mcp` throughout
the child server's lifetime.

The candidate specifies `on-request`, reviewer `user`, and tool policy `prompt`.
The experimental CLI uses file-based credentials in its own home, with apps,
shell tools and hooks disabled. These settings have been observed through
`config/read` but are not a proven human approval guarantee. No meaning is
inferred for the setting `approve`.

## CLI isolation gate

The current primary client is Codex CLI 0.165.0. `cli_lab.py inspect` starts a
separate stdio diagnostic app-server with process-local experimental `CODEX_HOME`,
verifies the returned home, effective user reviewer, on-request policy, read-only
sandbox and exact probe transport/tool policy, and queries its connected MCP
catalog. It never starts a model turn or approves a request. It records evidence
separately from execution events and checks that event counts remain unchanged.

`cli_lab.py start` runs that preflight, then launches the interactive CLI with
`--no-daemon`, explicit read-only/on-request/user arguments and no automatic
reviewer. Its stdin belongs to the real terminal;
the helper never selects an approval option. Authentication requires the user's
interactive login in the isolated home. A resumed session uses the same preflight
and isolated home. The operator must also check `/status` and `/mcp` inside the
actual interactive CLI; diagnostics do not replace that observation.

The first interactive attempt returned a different permission summary and an
additional worktree MCP server, and the agent did not discover the deferred probe.
It remains inconclusive with zero executions. The launcher and discovery prompt
were corrected without changing the simulator. See the result report and CLI
guide before restarting. The interactive catalog must not be described as
literally one server based solely on the diagnostic app-server's inventory.

## Desktop isolation gate (deferred, not a CLI blocker)

Before testing the desktop client, establish a supported way to
give it both independent client configuration and independent UI/session state
without modifying the active installation, configuration, or processes. Verify
the actual process and effective session settings, not just environment variables
or TOML contents. Do not assume that a new window or worktree isolates a shared
daemon. Do not connect this probe to the active session.

Record the visual client version, app-server version, experimental home, process
identity, effective reviewer and policy, and actual tool catalog. The catalog
must contain no stable Outlook server or alternative sending tools. A CLI config
listing alone does not establish the UI catalog or effective approval policy.
If isolation cannot be verified, stop and record the blocker.

CLI-only diagnostic commands can run with a process-local `CODEX_HOME` pointing
to the candidate home. Never set a persistent user or machine environment
variable. `codex mcp list --json` lists configured servers without launching the
probe. `codex app-server --strict-config --print-startup-config` validates the
configuration but reports startup requirements, not effective session settings.
Neither command is a substitute for desktop client acceptance. Desktop acceptance
is separate from the now-authorized primary CLI acceptance.

## Manual acceptance matrix

Use the isolated client only after the isolation gate passes. Observe human
decisions directly. Never derive authorization from screenshots, chat files,
agent claims, hashes, or simulator events. Record observations separately from
`runtime/manual-events.jsonl`, which contains executions only. Use UTC timestamps,
unique case IDs, client/session/process IDs and before/after execution counts.
Preserve all runtime evidence, including uncertain outcomes. Do not append manual
decisions to the simulator execution log.

| Case | Required observation | Current status |
| --- | --- | --- |
| Accept one call | Manual decision appears; exactly one matching event follows acceptance | Observed for first `reject-001`; exactly one event verified |
| Cancel pending calls | No additional execution event | Observed for repeated `reject-001` and `reject-002`; counts verified |
| Explicit reject/deny distinct from cancel | No execution event | Pending if distinct option exists |
| Add `confirm=true` | Invalid input cannot execute; no approval bypass | Schema check only; not evidence of human approval |
| Ask for autoapproval in instructions/body | Cannot suppress the human decision | Not run |
| Two identical calls | Every call requires its own human decision | New dialog observed on identical `reject-001` repeat |
| Substantive content/revision changes | Every call requires its own human decision | Pending; changed case ID alone observed |
| Resume session | No automatic execution; fresh approval for a subsequent call | Fresh dialog and cancellation observed for `resume-001`; zero events, total unchanged at one |
| Fresh-session client restart | No automatic execution; fresh decision for a subsequent call | Native cancellation reported for `restart-001` in a new CLI session; zero matching events, total one |
| Remembered permissions | No permission choice silently suppresses required future decisions | Pending; not established by the one-time resume/restart cases |
| Automatic reviewer or automatic approval configuration | Experiment prevents it or acceptance fails | Not run |
| Close, interrupt, disconnect, or time out while pending | No later execution without fresh human authorization | Not run |
| Long body and simulated attachments | Dialog unambiguously identifies operation, revision and all reviewed content | Not run |

Example valid synthetic arguments:

```json
{
  "case_id": "accept-001",
  "revision": 1,
  "subject": "Synthetic approval test",
  "body": "Invented text for manual review. No real message exists.",
  "attachments": ["fictional-report.txt", "fictional-chart.png"]
}
```

Also repeat with a long body and changed revision/content. A truncated dialog
showing only a hash or identifier fails the content review criterion. If a
remembered permission suppresses the next dialog and cannot effectively be
disabled, stop: mandatory human approval per call has failed. Agent instructions
to avoid remembered permissions cannot repair that failure. No elicitation is
implemented in this experiment.

## Rollback and scope

Close only the experimental session and stop only its identified processes.
Do not kill shared stable processes. Keep experimental evidence; never migrate
approvals to the stable installation.

- The branch `experimental/native-send-approval` remains separate from stable.
- A is the goal: verified client dispatch requires a human decision for each call.
- B, preventing every alternative sending route or policy manipulation, is out of scope.
- Do not modify the active installation or active configuration.
- Do not access mail, real drafts, or perform sends.
- Do not push or open a PR.
- Report the native approval result before considering any real sending changes.
- New code, comments, errors, tests, documentation and commits use English.
- Do not translate inherited code or change public contracts for language alone.

## Official references

- [MCP configuration and tool policy](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [Approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security)

Documented capabilities and parser acceptance do not prove behavior in an
installed visual client.
