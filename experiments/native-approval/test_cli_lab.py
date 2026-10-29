"""Ensure every launch path retains explicit human-review policy arguments."""

import os
import copy
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import cli_lab


class CliLaunchPolicyTests(unittest.TestCase):
    @patch("cli_lab.executable", return_value="codex.exe")
    def test_fresh_and_resumed_launches_keep_policy(self, unused_executable):
        for resume in (False, True):
            with self.subTest(resume=resume):
                arguments = cli_lab.cli_arguments(resume)
                self.assertEqual(arguments[arguments.index("--sandbox") + 1], "read-only")
                self.assertEqual(arguments[arguments.index("--ask-for-approval") + 1], "on-request")
                self.assertEqual(arguments[arguments.index("-c") + 1], 'approvals_reviewer="user"')
                self.assertIn("--no-daemon", arguments)
                self.assertNotIn("--approve-for-me", arguments)
                self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", arguments)
                if resume:
                    self.assertEqual(arguments[1:3], ["resume", "--last"])

    def test_environment_is_process_local(self):
        with patch.dict(os.environ, {"CODEX_HOME": "stable-home"}):
            child = cli_lab.environment()
            self.assertEqual(child["CODEX_HOME"], str(cli_lab.HOME))
            self.assertEqual(os.environ["CODEX_HOME"], "stable-home")

    def test_unsafe_effective_policy_stops_before_inventory_or_launch(self):
        baseline = tomllib.loads((cli_lab.ROOT / "config.template.toml").read_text(encoding="utf-8"))
        variants = []
        for key, value in (("approvals_reviewer", "auto_review"), ("approval_policy", "never")):
            changed = copy.deepcopy(baseline)
            changed[key] = value
            variants.append(changed)
        changed = copy.deepcopy(baseline)
        changed["mcp_servers"]["outlook_approval_probe"]["tools"]["outlook_send_draft"]["approval_mode"] = "auto"
        variants.append(changed)
        for effective_config in variants:
            with self.subTest(effective_config=effective_config), tempfile.TemporaryDirectory() as temporary:
                home = Path(temporary)
                (home / "config.toml").write_text(
                    (cli_lab.ROOT / "config.template.toml").read_text(encoding="utf-8"), encoding="utf-8")
                diagnostic = MagicMock()

                def reply(method, params):
                    if method == "initialize":
                        return {"codexHome": str(home)}
                    if method == "config/read":
                        return {"config": effective_config}
                    self.fail(f"Unexpected RPC after unsafe policy: {method}")

                diagnostic.request.side_effect = reply
                context = MagicMock()
                context.__enter__.return_value = diagnostic
                with patch.object(cli_lab, "HOME", home), \
                     patch.object(cli_lab, "EVENTS", home / "events.jsonl"), \
                     patch.object(cli_lab, "DiagnosticServer", return_value=context), \
                     patch.object(cli_lab.subprocess, "run") as login_status, \
                     patch.object(cli_lab.subprocess, "call") as launch:
                    with self.assertRaises(RuntimeError):
                        cli_lab.launch(False)
                    self.assertEqual([call.args[0] for call in diagnostic.request.call_args_list],
                                     ["initialize", "config/read"])
                    launch.assert_not_called()
                    login_status.assert_not_called()
                    self.assertFalse((home / "events.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
