"""Fill {{PLACEHOLDER}} tokens in v050_results.tex from summary.json.

Usage::

    python3 scripts/paper/fill_v050_numbers.py \\
        --summary artifacts/v0.5.0/summary.json \\
        --template paper/sections/v050_results.tex \\
        --out paper/sections/v050_results_filled.tex
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path


def _fmt_float(x: float, digits: int = 3) -> str:
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return str(x)
    if math.isnan(x):
        return "n/a"
    return f"{x:.{digits}f}"


def _fmt_gate(ok: bool) -> str:
    return r"\textbf{PASS}" if ok else r"\textbf{FAIL}"


def fill(summary: dict) -> dict[str, str]:
    n_life_runs = int(summary.get("n_lifecycle_runs", 0))
    n_life_finite = int(summary.get("n_lifecycle_finite", 0))
    adamson_n = sum(
        1
        for bc in summary.get("best_config_per_task", {}).values()
        if bc.get("best_config", {}).get("dataset") == "adamson_full"
    )
    norman_n = sum(
        1
        for bc in summary.get("best_config_per_task", {}).values()
        if bc.get("best_config", {}).get("dataset") == "norman"
    )
    tokens: dict[str, str] = {
        "ADAMSON_MEDIAN_MSD": _fmt_float(summary.get("median_msd_adamson", float("nan"))),
        "ADAMSON_N_TASKS": str(adamson_n),
        "NORMAN_MEDIAN_MSD": _fmt_float(summary.get("median_msd_norman", float("nan"))),
        "NORMAN_N_TASKS": str(norman_n),
        "N_TASKS_TOTAL": str(adamson_n + norman_n),
        "N_LIFECYCLE_RUNS": str(n_life_runs),
        "N_LIFECYCLE_FINITE": str(n_life_finite),
        "ARCHITECT_BACKBONE_ENTROPY_NATS": _fmt_float(
            summary.get("architect_backbone_entropy_nats", float("nan")), 2
        ),
        "ARCHITECT_HVG_ENTROPY_NATS": _fmt_float(
            summary.get("architect_hvg_entropy_nats", float("nan")), 2
        ),
        "RHO_ACE": _fmt_float(summary.get("rho_ace", float("nan")), 2),
        "RHO_DC": _fmt_float(summary.get("rho_dc", float("nan")), 2),
        "RHO_CSD": _fmt_float(summary.get("rho_csd", float("nan")), 2),
        "RHO_WFR": _fmt_float(summary.get("rho_wfr", float("nan")), 2),
        "RHO_TDI": _fmt_float(summary.get("rho_tdi", float("nan")), 2),
        "RHO_TRANSFER": _fmt_float(summary.get("rho_transfer", float("nan")), 2),
        "GATE_ADAMSON": _fmt_gate(
            bool(summary.get("gate_adamson_median_below_0_20", False))
        ),
        "GATE_NORMAN": _fmt_gate(
            bool(summary.get("gate_norman_median_below_0_30", False))
        ),
        "GATE_ENTROPY": _fmt_gate(
            bool(summary.get("gate_architect_entropy_above_0_5_nats", False))
        ),
    }
    return tokens


_PLACEHOLDER = re.compile(r"\{\{([A-Z0-9_\\ ]+)\}\}")


def substitute(template: str, tokens: dict[str, str]) -> str:
    def _replace(m: re.Match) -> str:
        # Strip any leading backslashes (LaTeX \_ escaping inside \mathbf).
        key = m.group(1).replace(r"\_", "_").replace("\\", "").strip()
        return str(tokens.get(key, m.group(0)))

    return _PLACEHOLDER.sub(_replace, template)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--template", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    summary = json.loads(args.summary.read_text())
    tokens = fill(summary)
    filled = substitute(args.template.read_text(), tokens)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(filled)
    print(f"wrote {args.out}")
    unresolved = _PLACEHOLDER.findall(filled)
    if unresolved:
        print(f"  WARNING: {len(unresolved)} unresolved placeholders: {unresolved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
