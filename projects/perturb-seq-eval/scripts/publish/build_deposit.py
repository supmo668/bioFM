"""Build the files a deposit uploads (CTO #577 (b)). Prep only: this never submits.

1. Checks the deposit description is a fresh render of the manuscript abstract.
2. Builds ``paper/paper.pdf`` from the sources with tectonic and keeps the log as
   ``build/deposit/paper_build.log`` (paper.pdf and build/ are gitignored).
3. Stages ``build/deposit/v060_run_artifacts/``: the committed v0.6.0 run files, the run
   manifest, and ``SHA256SUMS`` over them.

    .venv/bin/python scripts/publish/build_deposit.py [--skip-pdf]
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT = PROJECT_ROOT / "build" / "deposit"
RUN_ID = "20260929T035447Z-ce5f237"
RUN_FILES = ("trainer_runs.jsonl", "lifecycle_runs.jsonl", "provenance.json", "summary.json")


def deposit_inputs() -> list[str]:
    """Every committed input of the deposit: the files publish.yml ships (except build outputs)
    plus the sources the generated values and the paper come from."""
    import yaml

    cfg = yaml.safe_load((PROJECT_ROOT / "publish.yml").read_text())
    shipped = [
        f["path"]
        for f in cfg["files"]
        if not f["path"].startswith("build/") and f["path"] != "paper/paper.pdf"
    ]
    return sorted(
        set(shipped)
        | {
            "paper",
            "scripts/paper",
            "artifacts/v0.6.0",
            "configs/runs",
            "publish.yml",
            "CITATION.cff",
        }
    )


def uncommitted_inputs() -> str:
    return subprocess.run(
        ["git", "status", "--porcelain", "--", *deposit_inputs()],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def stage_run_artifacts(out: Path = OUT) -> Path:
    dst = out / "v060_run_artifacts"
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    srcs = [PROJECT_ROOT / "artifacts" / "v0.6.0" / n for n in RUN_FILES]
    srcs.append(PROJECT_ROOT / "configs" / "runs" / f"{RUN_ID}.json")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, capture_output=True, text=True, check=False
    ).stdout.strip()
    sums = []
    for s in srcs:
        if not s.exists():
            raise FileNotFoundError(s)
        shutil.copy2(s, dst / s.name)
        sums.append(f"{hashlib.sha256(s.read_bytes()).hexdigest()}  {s.name}")
    (dst / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    (dst / "BUILD_INFO").write_text(f"staged from git {head}; run {RUN_ID}\n")
    return dst


def build_pdf(out: Path = OUT) -> Path:
    tectonic = shutil.which("tectonic")
    if tectonic is None:
        raise RuntimeError(
            "tectonic not found on PATH; the deposit needs paper.pdf built from the sources"
        )
    paper = PROJECT_ROOT / "paper"
    dirty = uncommitted_inputs()
    if dirty:
        raise RuntimeError(
            f"paper sources are not committed; paper.pdf must be built from landed sources:\n{dirty}"
        )
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()
    for stale in ("paper.pdf", "paper.log"):
        (paper / stale).unlink(missing_ok=True)
    r = subprocess.run(
        [tectonic, "--keep-logs", "paper.tex"],
        cwd=paper,
        capture_output=True,
        text=True,
        check=False,
    )
    out.mkdir(parents=True, exist_ok=True)
    log = out / "paper_build.log"
    body = (paper / "paper.log").read_text() if (paper / "paper.log").exists() else ""
    log.write_text(
        f"% built from git {head}\n{body}\n% tectonic stdout/stderr:\n{r.stdout}{r.stderr}"
    )
    if r.returncode != 0 or not (paper / "paper.pdf").exists():
        raise RuntimeError(f"tectonic failed (exit {r.returncode}); see {log}")
    return paper / "paper.pdf"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-pdf", action="store_true")
    a = ap.parse_args()
    check = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "paper" / "render_publish_description.py"),
            "--check",
        ],
        capture_output=True,
        text=True,
    )
    if check.returncode != 0:
        print(check.stderr, file=sys.stderr)
        return 1
    dirty = uncommitted_inputs()
    if dirty:
        print(
            f"deposit inputs are not committed; stage and build from landed sources only:\n{dirty}",
            file=sys.stderr,
        )
        return 1
    print(f"staged {stage_run_artifacts()}")
    if not a.skip_pdf:
        print(f"built {build_pdf()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
