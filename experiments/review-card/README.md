# Synthetic MCP Apps review card

Standalone prototype for the second milestone. No production registration, no Outlook imports, no real mail, no native authorization guarantee. The first partial CLI milestone was published at `9e191d75356d070507da62b3b096f6ed2c5f77b6`.

Use the interpreter from the pinned native-approval development environment to run `server.py` as a separate STDIO MCP. Its catalog contains only `review_preview` and `review_simulate_submit`; the latter is app-visible only and destructive/non-idempotent. Those hints do not establish that a particular host enforces human approval. Do not add real mail servers to an isolated test client.

Preview generates a fixed synthetic message, including sender, To/CC/BCC, long plain text, hostile markup shown literally, and fictional attachment metadata. It returns a ten-minute in-memory reservation; restart loses it. Simulated submit consumes it once, rejects mismatches/expiry and never retries. This is not the durable production approval ledger and must not be promoted as one.

The HTML resource uses the documented MCP Apps `ui/initialize`, tool-result notification and `tools/call` bridge. No external assets or scripts are loaded. It checks that messages come from the parent window, renders email values via textContent, disables submit outside the host, on expiry, after one click or after an uncertain response. An acknowledgement checkbox is UI state, not proof of human consent. No raw HTML email rendering is supported.

Tests: `python -m unittest discover -s experiments/review-card -v`. Backend tests cover complete preview, mismatch consumption, expiry, independent previews and concurrent claims. A real stdio test checks catalog/metadata, MIME resource and synthetic submission with all production/COM imports blocked. These do not validate browser layout, native approval or actual desktop-host compatibility.

Pending supervised host test: connect only this simulator to a fresh isolated client; call review_preview; inspect every field and the end marker; verify the markup is inert; review the native decision if offered; test cancellation, double click, expiry and restart. If component-origin tool calls skip the mandatory native gate, do not connect this button to real sending. Without host UI support retain textual review; do not present a normal browser preview as an integrated-client pass.

Official references:
- https://developers.openai.com/plugins/build/chatgpt-ui
- https://developers.openai.com/plugins/reference

No active client configuration has been changed. Desktop visual verification remains pending; no manual approval evidence is manufactured.
