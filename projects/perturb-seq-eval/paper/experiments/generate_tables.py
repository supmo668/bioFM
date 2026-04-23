"""Emit LaTeX table snippets from the simulation CSVs.

Each snippet is included by paper.tex via \\input{tables/xxx.tex}.
"""

from __future__ import annotations

import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
TABLES = HERE.parent / "tables"


def _load(name: str) -> list[dict[str, str]]:
    with (OUT / name).open() as fh:
        return list(csv.DictReader(fh))


def _write(name: str, content: str) -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    (TABLES / name).write_text(content)


def table1_metric_correlations() -> None:
    """Per-metric Spearman and R² with ground-truth difficulty d.

    Uses the univariate ablation numbers from E5 plus a row for the full
    default TDI.
    """
    rows = _load("e5_tdi_ablation.csv")
    # We want a specific row order.
    order = ["ace_norm", "csd", "lack_of_convergence", "wfr", "TDI_full"]
    nice = {
        "ace_norm": r"ACE$_{\mathrm{norm}}$ (final round)",
        "csd": r"CSD (final round)",
        "lack_of_convergence": r"$1 - \Delta C$",
        "wfr": r"WFR",
        "TDI_full": r"TDI (default coeffs)",
    }
    lookup = {r["feature"]: r for r in rows}

    lines = [
        r"\begin{tabular}{lrr}",
        r"\toprule",
        r"Feature & Spearman $\rho$ & Univariate $R^2$ \\",
        r"\midrule",
    ]
    for key in order:
        r = lookup.get(key)
        if not r:
            continue
        sp = float(r["spearman"])
        r2 = float(r["r2"])
        r2_s = f"{r2:.3f}" if r2 == r2 and abs(r2) < 10 else "--"  # nan-safe
        lines.append(f"{nice[key]} & {sp:+.3f} & {r2_s} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    _write("tab1_metric_correlations.tex", "\n".join(lines) + "\n")


def table2_calibration_improvement() -> None:
    rows = _load("e1b_tdi_calibration.csv")
    r = rows[0]
    default_sp = float(r["default_spearman_test"])
    default_r2 = float(r["default_r2_test"])
    calib_sp = float(r["calibrated_spearman_test"])
    calib_r2 = float(r["calibrated_r2_test"])
    lines = [
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"TDI variant & $\alpha$ & $\beta$ & $\gamma$ & $\delta$ & Spearman $\rho$ \\",
        r"\midrule",
        f"Default (heuristic) & 0.350 & 0.250 & 0.250 & 0.150 & {default_sp:+.3f} \\\\",
        (f"Calibrated (ridge) & {float(r['calibrated_alpha']):.3f} & "
         f"{float(r['calibrated_beta']):.3f} & {float(r['calibrated_gamma']):.3f} & "
         f"{float(r['calibrated_delta']):.3f} & {calib_sp:+.3f} \\\\"),
        r"\bottomrule",
        r"\end{tabular}",
    ]
    _write("tab2_calibration_improvement.tex", "\n".join(lines) + "\n")


def table3_probe_to_target() -> None:
    e2 = _load("e2_probe_to_tdi_meta.csv")[0]
    e2b = _load("e2b_probe_to_difficulty.csv")[0]
    lines = [
        r"\begin{tabular}{lrr}",
        r"\toprule",
        r"Regression target & Test $R^2$ & Test Spearman $\rho$ \\",
        r"\midrule",
        (f"Probe $\\to$ post-hoc TDI (default) & {float(e2['r2_test']):+.3f} & -- \\\\"),
        (f"Probe $\\to$ latent difficulty $d$ & {float(e2b['probe_to_d_r2_test']):+.3f} & "
         f"{float(e2b['probe_to_d_spearman_test']):+.3f} \\\\"),
        r"\bottomrule",
        r"\end{tabular}",
    ]
    _write("tab3_probe_to_target.tex", "\n".join(lines) + "\n")


def table4_agent_scaling() -> None:
    rows = _load("e4_agent_scaling.csv")
    tiers = ["easy", "medium", "hard"]
    n_agents = sorted({int(r["n_agents"]) for r in rows})

    # Pivot: rows = tier, cols = n_agents.
    cell: dict[tuple[str, int], tuple[float, float]] = {}
    for r in rows:
        cell[(r["tier"], int(r["n_agents"]))] = (float(r["mean_auroc"]),
                                                  float(r["sem_auroc"]))

    col_spec = "l" + "r" * len(n_agents)
    head = " & ".join([""] + [f"$N{{=}}{n}$" for n in n_agents])
    body_lines = []
    for t in tiers:
        entries = []
        for n in n_agents:
            mu, sem = cell.get((t, n), (float("nan"), float("nan")))
            entries.append(f"{mu:.3f}\\,$\\pm$\\,{sem:.3f}")
        body_lines.append(f"{t} & " + " & ".join(entries) + r" \\")

    lines = [
        rf"\begin{{tabular}}{{{col_spec}}}",
        r"\toprule",
        head + r" \\",
        r"\midrule",
        *body_lines,
        r"\bottomrule",
        r"\end{tabular}",
    ]
    _write("tab4_agent_scaling.tex", "\n".join(lines) + "\n")


def table5_pareto_samples() -> None:
    rows = _load("e3_pareto.csv")
    # Pick a coarse grid across budgets for the table.
    # Keep row 0, last, and three in between.
    n = len(rows)
    if n == 0:
        return
    idx = sorted({0, n // 4, n // 2, (3 * n) // 4, n - 1})
    lines = [
        r"\begin{tabular}{rrrr}",
        r"\toprule",
        r"Budget (FLOPs proxy) & Uniform & Minimal & Adaptive \\",
        r"\midrule",
    ]
    for i in idx:
        r = rows[i]
        lines.append(
            f"{int(float(r['budget']))} & "
            f"{float(r['uniform_mean_auroc']):.3f} & "
            f"{float(r['minimal_mean_auroc']):.3f} & "
            f"{float(r['adaptive_mean_auroc']):.3f} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    _write("tab5_pareto_samples.tex", "\n".join(lines) + "\n")


def main() -> None:
    table1_metric_correlations()
    table2_calibration_improvement()
    table3_probe_to_target()
    table4_agent_scaling()
    table5_pareto_samples()
    print("wrote tables into", TABLES)


if __name__ == "__main__":
    main()
