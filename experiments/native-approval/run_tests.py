"""Run only the COM-free experiment with a 60-second external deadline."""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

def main():
    temporary = ROOT / 'runtime' / 'test-temp'
    temporary.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment.update(TEMP=str(temporary), TMP=str(temporary), PYTHONUNBUFFERED='1')
    process = subprocess.Popen(
        [sys.executable, '-u', '-m', 'unittest', 'discover', '-s', str(ROOT), '-v'],
        cwd=ROOT, env=environment, creationflags=getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0))
    try:
        return process.wait(timeout=60)
    except subprocess.TimeoutExpired:
        print('FAIL: experiment exceeded 60 seconds; stopping only this test process tree.', flush=True)
        if os.name == 'nt':
            subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], check=False)
        else:
            process.kill()
        process.wait(timeout=10)
        return 124

if __name__ == '__main__':
    raise SystemExit(main())
