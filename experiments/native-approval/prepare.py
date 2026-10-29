"""Prepare a fresh candidate client home without launching any client."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def prepare():
    runtime = ROOT / "runtime"
    home = runtime / "client-home"
    home.mkdir(parents=True, exist_ok=True)
    config = (ROOT / "config.template.toml").read_text(encoding="utf-8")
    values = {
        "__PYTHON__": Path(sys.executable).resolve().as_posix(),
        "__PROBE__": (ROOT / "probe.py").as_posix(),
        "__EVENTS__": (runtime / "manual-events.jsonl").as_posix(),
    }
    for placeholder, value in values.items():
        config = config.replace(placeholder, json.dumps(value)[1:-1])
    # Never overwrite client state, copy approvals, or touch the active home.
    with (home / "config.toml").open("x", encoding="utf-8") as stream:
        stream.write(config)
    print(f"Candidate client home: {home}")
    print("No client launched. Client isolation must be verified before manual tests.")


if __name__ == "__main__":
    prepare()
