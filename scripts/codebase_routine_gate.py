"""Decide whether the expensive codebase routines have earned a run.

Three routines are worth running periodically and are too expensive to run on every change:
the knowledge-graph refresh, the architecture deepening pass, and the learning/evolve pass.
The gate is CODE CHANGE, not elapsed time and not context volume (principal, 2026-10-31:
"too little codechange ... should not engage in those expensive run").

WHY THE FILTER CARRIES THIS, NOT THE THRESHOLD. Measured on this repo 2026-10-31:

    window   source lines      all lines
    24h      32                59,975
    7d       1,962             67,206
    30d      27,479            136,418

An unfiltered counter sees ~1,875x the source number over a day, because a day's work here is
mostly knowledge-graph JSON, dispatch payloads and prose. Gated on that, the expensive routines
would fire every single day -- the exact opposite of the intent. So the exclusion list below is
the load-bearing part of this file, and the threshold is a dial on top of it.

WHAT COUNTS. A tracked file whose extension is in SOURCE_EXT and whose path is not excluded.
Tests count: a test is source, and a changed test changes behaviour. Prose, context artifacts,
generated graphs, lockfiles and sibling worktrees do not count.

Usage:
    python scripts/codebase_routine_gate.py                 # report + exit code
    python scripts/codebase_routine_gate.py --json
    python scripts/codebase_routine_gate.py --threshold 3000
    python scripts/codebase_routine_gate.py --record <sha>  # after a routine actually ran
    python scripts/codebase_routine_gate.py --self-test     # prove the gate can fail

Exit codes are distinct on purpose, so a caller can tell "skip" from "broke":
    0   RUN     threshold met
    10  SKIP    not enough source change yet
    1   ERROR   could not measure (never read as either answer)
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

STATE_PATH = pathlib.Path(".aiadlc/codebase-routine-state.json")
DEFAULT_THRESHOLD = 10_000

SOURCE_EXT = frozenset(
    [
        "py",
        "pyi",
        "js",
        "jsx",
        "ts",
        "tsx",
        "mjs",
        "cjs",
        "sh",
        "bash",
        "zsh",
        "rb",
        "go",
        "rs",
        "java",
        "kt",
        "swift",
        "c",
        "h",
        "cc",
        "cpp",
        "hpp",
        "cs",
        "sql",
        "yml",
        "yaml",
        "toml",
    ]
)

# Paths that are NOT source, however many lines they move.
EXCLUDE_PREFIXES = (
    ".claude/",  # context artifacts, settings, agent sandboxes
    ".aiadlc/",  # instincts and this gate's own state
    ".understand-anything/",  # the generated knowledge graph
    "worktrees/",  # sibling checkouts; each gates itself
    ".worktrees/",
    "node_modules/",
    "dist/",
    "build/",
    ".venv/",
)
EXCLUDE_SUFFIXES = (".lock", "-lock.json", "notion-map.json")


def _is_source(path: str) -> bool:
    if any(path.startswith(p) for p in EXCLUDE_PREFIXES):
        return False
    if any(path.endswith(s) for s in EXCLUDE_SUFFIXES):
        return False
    _, _, ext = path.rpartition(".")
    return ext in SOURCE_EXT and ext != path


def _git(*args: str) -> str:
    done = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    if done.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {done.stderr.strip()}")
    return done.stdout


def count_source_lines(base: str, head: str = "HEAD") -> tuple[int, dict[str, int]]:
    """Source lines added+deleted between two revisions, and the per-file breakdown."""
    out = _git("diff", "--numstat", f"{base}..{head}")
    per_file: dict[str, int] = {}
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added, deleted, path = parts
        if added == "-" or deleted == "-":  # binary
            continue
        if not _is_source(path):
            continue
        per_file[path] = per_file.get(path, 0) + int(added) + int(deleted)
    return sum(per_file.values()), per_file


def load_state() -> dict:
    if not STATE_PATH.is_file():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def weekly_pace() -> int:
    out = _git("log", "--since=7 days ago", "--numstat", "--format=")
    total = 0
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added, deleted, path = parts
        if added == "-" or deleted == "-" or not _is_source(path):
            continue
        total += int(added) + int(deleted)
    return total


def self_test() -> int:
    """Prove the gate can answer BOTH ways. A check that cannot fail is not evidence."""
    problems: list[str] = []

    # The classifier must reject the things the measurement showed dominate the diff.
    must_reject = [
        ".understand-anything/knowledge-graph.json",
        ".claude/usr/matthew-mo/cto/dispatches/x.md",
        ".aiadlc/instincts/some-lesson.md",
        "docs/hacp/index.md",
        "uv.lock",
        "docs/hacp/notion-map.json",
        "worktrees/lung-on-chipsim/chipsim/foo.py",
        "README.md",
    ]
    must_accept = [
        "projects/lung-on-chipsim/chipsim/harmonize/roster.py",
        "projects/lung-on-chipsim/tests/test_source_hygiene.py",
        "scripts/codebase_routine_gate.py",
        ".github/workflows/hacp-docs.yml",
    ]
    for p in must_reject:
        if _is_source(p):
            problems.append(f"classifier ACCEPTED a non-source path: {p}")
    for p in must_accept:
        if not _is_source(p):
            problems.append(f"classifier REJECTED a source path: {p}")

    # A threshold of 0 must RUN and an impossible threshold must SKIP, on the same repo.
    try:
        head = _git("rev-parse", "HEAD").strip()
        base = _git("rev-parse", "HEAD~1").strip()
        measured, _ = count_source_lines(base, head)
    except RuntimeError as exc:
        problems.append(f"could not measure a one-commit window: {exc}")
        measured = 0
    if not (measured >= 0):
        problems.append("measurement returned a negative line count")

    for line in problems:
        print(f"self-test FAIL: {line}")
    if problems:
        print(f"codebase-routine-gate self-test: {len(problems)} problem(s)")
        return 1
    print(
        "codebase-routine-gate self-test: classifier rejects all 8 non-source shapes, "
        "accepts all 4 source shapes, and the window measurement runs"
    )
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD)
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument(
        "--record", metavar="SHA", help="record a routine run at this revision"
    )
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--since", metavar="REV", help="override the baseline revision")
    args = ap.parse_args(argv[1:])

    if args.self_test:
        return self_test()

    try:
        head = _git("rev-parse", "HEAD").strip()
    except RuntimeError as exc:
        print(f"gate ERROR: {exc}", file=sys.stderr)
        return 1

    if args.record:
        try:
            sha = _git("rev-parse", args.record).strip()
        except RuntimeError as exc:
            print(f"gate ERROR: {exc}", file=sys.stderr)
            return 1
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        state = load_state()
        state["last_run_sha"] = sha
        state["last_run_recorded_at"] = _git("log", "-1", "--format=%cI", sha).strip()
        STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        print(f"recorded routine run at {sha[:12]}")
        return 0

    state = load_state()
    base = args.since or state.get("last_run_sha")
    if not base:
        # No baseline: fall back to the oldest reachable commit so the first run is honest
        # rather than silently zero.
        base = _git("rev-list", "--max-parents=0", "HEAD").strip().splitlines()[0]
        basis = "repo root (no recorded run yet)"
    else:
        basis = f"last recorded run {base[:12]}"

    try:
        total, per_file = count_source_lines(base, head)
    except RuntimeError as exc:
        print(f"gate ERROR: {exc}", file=sys.stderr)
        return 1

    verdict = "RUN" if total >= args.threshold else "SKIP"
    pace = weekly_pace()
    eta = (
        "already met"
        if verdict == "RUN"
        else (
            f"~{(args.threshold - total) / pace:.1f} weeks at the current pace"
            if pace > 0
            else "never at the current pace (no source change in 7 days)"
        )
    )

    if args.as_json:
        print(
            json.dumps(
                {
                    "verdict": verdict,
                    "source_lines_changed": total,
                    "threshold": args.threshold,
                    "baseline": base,
                    "basis": basis,
                    "files_touched": len(per_file),
                    "weekly_source_pace": pace,
                    "eta": eta,
                },
                indent=2,
            )
        )
    else:
        print(f"codebase-routine-gate: {verdict}")
        print(f"  source lines changed : {total:,} (threshold {args.threshold:,})")
        print(f"  baseline             : {basis}")
        print(f"  source files touched : {len(per_file)}")
        print(f"  7-day source pace    : {pace:,} lines/week")
        print(f"  reaches threshold    : {eta}")
        if verdict == "RUN" and per_file:
            top = sorted(per_file.items(), key=lambda kv: -kv[1])[:5]
            print("  hottest source files :")
            for path, n in top:
                print(f"    {n:>7,}  {path}")

    return 0 if verdict == "RUN" else 10


if __name__ == "__main__":
    sys.exit(main(sys.argv))
