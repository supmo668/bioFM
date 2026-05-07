"""Pull v0.5.0 Modal artifacts to local ``artifacts/v0.5.0/``.

Usage::

    python3 scripts/local/pull_v05_artifacts.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REMOTE_PREFIX = "/v0.5.0"
LOCAL_PREFIX = Path(__file__).resolve().parents[2] / "artifacts" / "v0.5.0"
FILES = ("trainer_runs.jsonl", "lifecycle_runs.jsonl", "provenance.json")


def main() -> int:
    LOCAL_PREFIX.mkdir(parents=True, exist_ok=True)
    ok = True
    for name in FILES:
        remote = f"{REMOTE_PREFIX}/{name}"
        local = LOCAL_PREFIX / name
        print(f"[pull] perturb-eval-data:{remote} -> {local}")
        try:
            subprocess.run(
                [
                    "modal", "volume", "get",
                    "perturb-eval-data", remote, str(local), "--force",
                ],
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            print(f"  failed: {exc}", file=sys.stderr)
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
