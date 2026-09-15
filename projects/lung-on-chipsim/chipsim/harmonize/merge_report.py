"""Measured effect of the stereo guard on the real snapshot — CTO #106 §4 / #108 / #122 §2.

`python -m chipsim.harmonize.merge_report --raw-dir data/raw/drugbank --out <dir>`

Writes TRACKED `<dir>/merge_report.json` and `<dir>/merge_report.md`: merge groups and
their stage with the guard OFF and ON, every group the guard SPLITS (identified by
canonical InChIKey), how many groups it newly merges (expected none), and how many
compounds it fires on. The run is journaled like an ETL stage (`journal/<run_id>/` with a
copy of every config), so the numbers are attributable.

**No DrugBank record content in tracked output (principal invariant, CTO #120 §1 / #122 §2).**
The first version of this generator wrote each split group's members as
`[accession, DrugBank name]` pairs into the tracked JSON — 89 real accessions on the real
snapshot — and its markdown listed every group by name. A generator that re-creates
forbidden content on every run is worse than the content, because it returns. So:

- tracked `merge_report.{json,md}` identify members by **canonical InChIKey only**;
- the id / name / key association goes to `merge_report_members.json` **inside the
  journal run directory**, which is git-ignored, beside the licensed data;
- #108's "list all split groups by name" requirement is RETIRED (#122 §2).

PubChem CIDs are NOT resolved here: the generator runs offline and reproducibly, and a
network lookup per member would make the tracked report depend on a live service.

Not a `chipsim.pipeline` subcommand: T16 pins that inventory to the ETL chain plus the
human-only seal, and a measurement is neither.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from chipsim.harmonize.ids import (
    MERGE_STAGES,
    GuardEffect,
    add_canonical_identity,
    add_canonical_identity_excluding,
    guard_effect,
    load_preregistered_exclusions,
)
from chipsim.ingest.drugbank_snapshot import MIN_COMPOUND_ROWS, load_compounds
from chipsim.journal import finish_run, start_run

#: The CTO's coarser rollup (#97/#108) — `parse` folds into salt_or_uncharge, since both
#: are pre-tautomer normalisation. `relative-stereo` is its OWN category (CTO #122 §0):
#: the re-key's effect must be attributable, not folded into existing counts.
ROLLUP = {
    "upstream-duplicate": "source_identical",
    "parse": "salt_or_uncharge",
    "relative-stereo": "relative_stereo",
    "salt": "salt_or_uncharge",
    "uncharge": "salt_or_uncharge",
    "tautomer": "tautomer",
}

#: Name of the untracked mapping file written into the journal run directory.
MEMBERS_MAPPING_NAME = "merge_report_members.json"


def _rollup(breakdown: dict[str, int]) -> dict[str, int]:
    out: Counter = Counter()
    for stage, n in breakdown.items():
        out[ROLLUP[stage]] += n
    return dict(out)


def report_payload(effect: GuardEffect, *, raw_dir: str, run_dir: str | None, excluded: int) -> dict:
    """The TRACKED JSON payload. Members are canonical InChIKeys; no id, no name.

    Built field by field rather than from `asdict(effect)`: `asdict` would serialize
    `SplitGroup.members` (id, name) and the id tuples in `new_merges` — exactly the
    record content this function exists to keep out.
    """
    return {
        "compounds": effect.compounds,
        "excluded_unparseable": excluded,
        "guard_fired": effect.guard_fired,
        "merge_groups_before": effect.merge_groups_before,
        "merge_groups_after": effect.merge_groups_after,
        "before_breakdown": dict(effect.before_breakdown),
        "after_breakdown": dict(effect.after_breakdown),
        "before_rollup": _rollup(effect.before_breakdown),
        "after_rollup": _rollup(effect.after_breakdown),
        "split_groups": [
            {
                "key_before": g.key_before,
                "stage_before": g.stage_before,
                "member_keys": list(g.member_keys),
                "keys_after": list(g.keys_after),
                "layers": list(g.layers),
            }
            for g in effect.split_groups
        ],
        # Count only: the members are DrugBank row ids (record content) — see the journal.
        "new_merges": len(effect.new_merges),
        "reclassified": [
            {"key": k, "stage_before": b, "stage_after": a} for k, b, a in effect.reclassified
        ],
        "raw_dir": raw_dir,
        "journal_run": run_dir,
        "members_mapping": f"{MEMBERS_MAPPING_NAME} in the journal run directory (untracked)",
    }


def members_mapping(effect: GuardEffect) -> list[dict]:
    """The id / name / canonical-key association — for the UNTRACKED journal only."""
    rows: list[dict] = []
    for g in effect.split_groups:
        keys = g.member_keys or ("",) * len(g.members)
        for (drugbank_id, name), key in zip(g.members, keys, strict=True):
            rows.append(
                {
                    "kind": "split",
                    "group_key_before": g.key_before,
                    "drugbank_id": drugbank_id,
                    "name": name,
                    "canonical_inchikey": key,
                }
            )
    for n, members in enumerate(effect.new_merges, 1):
        for drugbank_id in members:
            rows.append(
                {
                    "kind": "new_merge",
                    "group": n,
                    "drugbank_id": drugbank_id,
                    "name": "",
                    "canonical_inchikey": "",
                }
            )
    return rows


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
        (
            "Members are identified by canonical InChIKey. The id/name association is in "
            f"`{MEMBERS_MAPPING_NAME}` inside the journal run directory (untracked) — DrugBank "
            "record content never enters this report (CTO #122 §2)."
        ),
        "",
        "## Stage breakdown",
        "",
        "| stage | without guard | with guard |",
        "|---|---:|---:|",
    ]
    for stage in MERGE_STAGES:
        lines.append(
            f"| {stage} | {effect.before_breakdown.get(stage, 0)} | {effect.after_breakdown.get(stage, 0)} |"
        )
    rb, ra = _rollup(effect.before_breakdown), _rollup(effect.after_breakdown)
    lines += ["", "Rollup (CTO's categories; `parse` folded into salt_or_uncharge):", ""]
    lines += ["| category | without guard | with guard |", "|---|---:|---:|"]
    for cat in ("source_identical", "relative_stereo", "salt_or_uncharge", "tautomer"):
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
        "| # | member keys | stage before | layers altered | keys after |",
        "|---:|---|---|---|---|",
    ]
    for n, g in enumerate(effect.split_groups, 1):
        keys = " \\| ".join(f"`{k}`" for k in g.member_keys)
        lines.append(
            f"| {n} | {keys} | {g.stage_before} | {','.join(g.layers) or '—'} | "
            f"{' / '.join(k.split('-')[0] for k in g.keys_after)} |"
        )
    lines += ["", "## New merges", ""]
    if effect.new_merges:
        lines.append(
            f"{len(effect.new_merges)} group(s); members in `{MEMBERS_MAPPING_NAME}` (journal, untracked)."
        )
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
        payload = report_payload(effect, raw_dir=str(ns.raw_dir), run_dir=str(run_dir), excluded=excluded)
        (ns.out / "merge_report.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        (ns.out / "merge_report.md").write_text(
            render_markdown(effect, raw_dir=str(ns.raw_dir), run_dir=str(run_dir))
        )
        # The id/name association: journal ONLY (git-ignored), never the tracked out dir.
        (Path(run_dir) / MEMBERS_MAPPING_NAME).write_text(
            json.dumps(members_mapping(effect), indent=2, sort_keys=True) + "\n"
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
