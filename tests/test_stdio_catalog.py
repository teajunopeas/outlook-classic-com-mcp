"""Real stdio transport against a simulated backend, not Outlook integration."""
import subprocess
import sys
from pathlib import Path


def test_stdio_initialize_tools_and_simulated_accounts():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run([sys.executable, str(root / 'scripts' / 'verify_mail_mcp.py'), '--simulate'],
                            capture_output=True, text=True, encoding='utf-8', timeout=30)
    assert result.returncode == 0, result.stderr
    assert '"mode": "simulated"' in result.stdout
    assert 'outlook_send_draft' in result.stdout
