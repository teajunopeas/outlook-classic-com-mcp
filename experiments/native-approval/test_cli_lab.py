"""Ensure every launch path retains explicit human-review policy arguments."""

import os
import unittest
from unittest.mock import patch

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


if __name__ == "__main__":
    unittest.main()
