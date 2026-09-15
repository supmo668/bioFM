"""Measured effect of the stereo guard on the real snapshot — CTO #106 §4 / #108.

`python -m chipsim.harmonize.merge_report --raw-dir data/raw/drugbank --out <dir>`

Writes `<dir>/merge_report.json` and `<dir>/merge_report.md`: merge groups and their
stage with the guard OFF and ON, every group the guard SPLITS **by name** (the record
of reference — not the summary counts), every group it newly merges (expected none),
and how many compounds it fires on. The run is journaled like an ETL stage
(`journal/<run_id>/` with a copy of every config), so the numbers are attributable.

Not a `chipsim.pipeline` subcommand: T16 pins that inventory to the ETL chain plus
the human-only seal, and a measurement is neither.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from chipsim.harmonize.ids import (
    GuardEffect,
    add_canonical_identity,
    add_canonical_identity_excluding,
    guard_effect,
    load_preregistered_exclusions,
)
from chipsim.ingest.drugbank_snapshot import MIN_COMPOUND_ROWS, load_compounds
from chipsim.journal import finish_run, start_run

#: The CTO's coarser rollup (#97/#108) — `parse` folds into salt_or_uncharge, since
#: both are pre-tautomer normalisation and the CTO's table had no parse bucket.
ROLLUP = {
    "upstream-duplicate": "source_identical",
    "parse": "salt_or_uncharge",
    "salt": "salt_or_uncharge",
    "uncharge": "salt_or_uncharge",
    "tautomer": "tautomer",
}


def _rollup(breakdown: dict[str, int]) -> dict[str, int]:
    out: Counter = Counter()
    for stage, n in breakdown.items():
        out[ROLLUP[stage]] += n
    return dict(out)


def render_markdown(effect: GuardEffect, *, raw_dir: str, run_dir: str | None) -> str:
    fired_pct = 100.0 * effect.guard_fired / effect.compounds if effect.compounds else 0.0
    lines = [
        "# Stereo guard {t,m,s} — measured effect on the snapshot",
        "",
        f"- snapshot: `{raw_dir}`",
        f"- journal run: `{run_dir}`" if run_dir else "- journal run: (none)",
        f"- compounds canonicalized: **{effect.compounds}**",
        f"- guard fired on: **{effect.guard_fired}** ({fired_pct:.1f}%)",
        f"- merge groups: **{effect.merge_groups_before} → {effect.merge_groups_after}**",
        f"- groups split by the guard: **{len(effect.split_groups)}**",
        f"- groups newly merged by the guard: **{len(effect.new_merges)}**",
        "",
        "## Stage breakdown",
        "",
        "| stage | without guard | with guard |",
        "|---|---:|---:|",
    ]
    for stage in ("upstream-duplicate", "parse", "salt", "uncharge", "tautomer"):
        lines.append(
            f"| {stage} | {effect.before_breakdown.get(stage, 0)} | {effect.after_breakdown.get(stage, 0)} |"
        )
    rb, ra = _rollup(effect.before_breakdown), _rollup(effect.after_breakdown)
    lines += ["", "Rollup (CTO's categories; `parse` folded into salt_or_uncharge):", ""]
    lines += ["| category | without guard | with guard |", "|---|---:|---:|"]
    for cat in ("source_identical", "salt_or_uncharge", "tautomer"):
        lines.append(f"| {cat} | {rb.get(cat, 0)} | {ra.get(cat, 0)} |")
    lines += [
        "",
        (
            f"Source-identical count, exactly: **{rb.get('source_identical', 0)} without the guard, "
            f"{ra.get('source_identical', 0)} with it** (any difference is reclassification, not a new merge)."
        ),
        "",
        "## Split groups",
        "",
        "Every group that exists without the guard and is split by it — the record of reference.",
        "",
        "| # | members (name) | stage before | layers altered | keys after |",
        "|---:|---|---|---|---|",
    ]
    for n, g in enumerate(effect.split_groups, 1):
        names = " \\| ".join(name for _, name in g.members)
        lines.append(
            f"| {n} | {names} | {g.stage_before} | {','.join(g.layers) or '—'} | "
            f"{' / '.join(k.split('-')[0] for k in g.keys_after)} |"
        )
    lines += ["", "## New merges", ""]
    if effect.new_merges:
        lines += [f"- {', '.join(m)}" for m in effect.new_merges]
    else:
        lines.append("None.")
    lines += ["", "## Reclassified groups (same members, different stage)", ""]
    if effect.reclassified:
        lines += [f"- `{k}`: {b} → {a}" for k, b, a in effect.reclassified]
    else:
        lines.append("None.")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="python -m chipsim.harmonize.merge_report")
    ap.add_argument("--raw-dir", required=True, type=Path, dest="raw_dir")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--project-root", type=Path, default=None, dest="project_root")
    ap.add_argument("--min-rows", type=int, default=MIN_COMPOUND_ROWS, dest="min_rows")
    ap.add_argument(
        "--exclusions",
        type=Path,
        default=Path("configs/unparseable_compounds.yaml"),
        help="pre-registered unparseable-compound roster (principal's ruling 2026-09-14)",
    )
    ap.add_argument(
        "--no-exclusions",
        action="store_true",
        dest="no_exclusions",
        help="fixtures only: canonicalize without the closed roster (raises on any failure)",
    )
    return ap


def main(argv: list[str] | None = None) -> int:
    ns = build_parser().parse_args(argv)
    if ns.project_root is None:
        from chipsim.pipeline import project_root

        root = project_root()
    else:
        root = Path(ns.project_root)
    recorded = list(sys.argv) if argv is None else ["merge-report", *argv]
    run_dir = start_run("merge-report", root, argv=recorded)
    try:
        compounds = load_compounds(ns.raw_dir, min_rows=ns.min_rows)
        if ns.no_exclusions:
            compounds = add_canonical_identity(compounds)
            excluded = 0
        else:
            compounds, dropped = add_canonical_identity_excluding(
                compounds, preregistered=load_preregistered_exclusions(root / ns.exclusions)
            )
            excluded = len(dropped)
        effect = guard_effect(compounds)
        ns.out.mkdir(parents=True, exist_ok=True)
        payload = asdict(effect)
        payload.update(
            {
                "excluded_unparseable": excluded,
                "raw_dir": str(ns.raw_dir),
                "journal_run": str(run_dir),
                "before_rollup": _rollup(effect.before_breakdown),
                "after_rollup": _rollup(effect.after_breakdown),
            }
        )
        (ns.out / "merge_report.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n"
        )
        (ns.out / "merge_report.md").write_text(
            render_markdown(effect, raw_dir=str(ns.raw_dir), run_dir=str(run_dir))
        )
        print(
            f"compounds={effect.compounds} excluded_unparseable={excluded} "
            f"guard_fired={effect.guard_fired} groups={effect.merge_groups_before}->{effect.merge_groups_after} "
            f"splits={len(effect.split_groups)} new_merges={len(effect.new_merges)} -> {ns.out}"
        )
    except BaseException as exc:
        finish_run(run_dir, status="crashed", detail=f"{type(exc).__name__}: {exc}")
        raise
    finish_run(run_dir, status="ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
