"""Draw the two v0.6.0 figures from ``paper/data/exploratory_v060.json``.

* ``paper/figures/fig_h4_scatter.pdf`` -- per screen, each pre-registered trace feature
  against held-out MSD, one point per task (the seed median the pre-registered test uses).
  No fitted line and no statistic is drawn: the estimates are the macros in the text.
* ``paper/figures/fig_confidence_by_round.pdf`` -- per screen, each role's mean stated
  confidence by round, with the median MSD by round in the adjacent panel (two panels, never
  two y-scales on one axis). The dashed line marks that prompts carry the previous round's
  held-out error from round 1 on.

The JSON is the only input (it holds the per-task table), so a figure cannot disagree with the
macros. Needs matplotlib (the optional ``paper`` dependency group). Output is deterministic for
a given matplotlib version: fixed fonts (DejaVu Sans, embedded as TrueType), no timestamps.

    python scripts/paper/make_v060_figures.py [--data ...] [--out-dir ...]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCREENS = {"adamson_full": "Adamson", "norman": "Norman"}
FEATURES = {
    "ace_norm": r"$\mathrm{ACE}_{\mathrm{norm}}$",
    "one_minus_delta_c": r"$1-\Delta C$",
    "tdi_lifecycle": r"$\mathrm{TDI}_{\mathrm{lifecycle}}$",
}
# Okabe-Ito hues in a fixed role order; marker and dash repeat the identity for
# colour-blind and greyscale readers.
ROLES = {
    "DataCurator": ("Curator", "#0072B2", "o", "-"),
    "Literature": ("Literature", "#D55E00", "s", "--"),
    "Architect": ("Architect", "#009E73", "^", "-."),
    "Trainer": ("Trainer", "#CC79A7", "D", ":"),
    "Validator": ("Validator", "#E69F00", "v", (0, (5, 1, 1, 1, 1, 1))),
}
ROUNDS = (0, 1, 2)
INK, MUTED, POINT = "#1a1a1a", "#6b6b6b", "#0072B2"
FEEDBACK_X = 0.5  # between round 0 and round 1
WIDTH_IN = 6.27  # a4paper with 1in margins: the text width
RC = {
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "font.family": "DejaVu Sans",
    "mathtext.fontset": "dejavusans",
    "font.size": 8,
    "axes.labelsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "grid.color": "#e3e3e3",
    "grid.linewidth": 0.5,
}
# No creation date, so the same inputs give the same bytes under one matplotlib version.
PDF_METADATA = {"CreationDate": None, "ModDate": None, "Creator": None, "Producer": None}


def _save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, format="pdf", metadata=PDF_METADATA)
    plt.close(fig)


def scatter(data: dict, path: Path) -> None:
    fig, axes = plt.subplots(
        len(SCREENS), len(FEATURES), figsize=(WIDTH_IN, 4.1), sharey="row", layout="constrained"
    )
    for i, (ds, screen) in enumerate(SCREENS.items()):
        rows = data["screens"][ds]["per_task"]
        for j, (key, label) in enumerate(FEATURES.items()):
            ax = axes[i][j]
            ax.scatter(
                [r[key] for r in rows],
                [r["msd"] for r in rows],
                s=16,
                color=POINT,
                edgecolors="white",
                linewidths=0.5,
            )
            ax.set_yscale("log")
            ax.xaxis.set_major_locator(MaxNLocator(nbins=4))
            ax.grid(True, which="major")
            ax.set_axisbelow(True)
            ax.set_xlabel(label)
            if j == 0:
                ax.set_ylabel(f"{screen}: held-out MSD")
    _save(fig, path)


def confidence_by_round(data: dict, path: Path) -> None:
    fig, axes = plt.subplots(
        len(SCREENS),
        2,
        figsize=(WIDTH_IN, 4.4),
        sharex=True,
        layout="constrained",
        gridspec_kw={"width_ratios": [1.5, 1]},
    )
    for i, (ds, screen) in enumerate(SCREENS.items()):
        q = data["screens"][ds]["quantities"]
        left, right = axes[i]
        for role, (_, colour, marker, dash) in ROLES.items():
            left.plot(
                ROUNDS,
                [q[f"role_{role}_conf_round{r}"]["value"] for r in ROUNDS],
                color=colour,
                marker=marker,
                linestyle=dash,
                linewidth=1.5,
                markersize=5,
                markeredgecolor="white",
                markeredgewidth=0.6,
            )
        left.set_ylabel("Mean stated confidence")
        left.set_title(screen, loc="left", fontsize=8, color=INK)
        right.plot(
            ROUNDS,
            data["screens"][ds]["figure_only"]["median_msd_by_round"],
            color=INK,
            marker="o",
            linewidth=1.5,
            markersize=5,
            markeredgecolor="white",
            markeredgewidth=0.6,
        )
        right.set_ylabel("Median held-out MSD")
        right.set_title(screen, loc="left", fontsize=8, color=INK)
        for ax in (left, right):
            ax.axvline(FEEDBACK_X, color=MUTED, linestyle=(0, (4, 3)), linewidth=0.9)
            ax.set_xticks(ROUNDS)
            ax.set_xlim(-0.25, 2.25)
            ax.grid(True, axis="y")
            ax.set_axisbelow(True)
            if i == len(SCREENS) - 1:
                ax.set_xlabel("Round")
    axes[1][0].sharey(axes[0][0])
    handles = [
        Line2D(
            [],
            [],
            color=colour,
            marker=marker,
            linestyle=dash,
            linewidth=1.5,
            markersize=5,
            markeredgecolor="white",
            markeredgewidth=0.6,
            label=name,
        )
        for name, colour, marker, dash in ROLES.values()
    ]
    handles.append(
        Line2D(
            [],
            [],
            color=MUTED,
            linestyle=(0, (4, 3)),
            linewidth=0.9,
            label="prompts carry the prior round's held-out error from round 1",
        )
    )
    fig.legend(handles=handles, loc="outside upper center", ncols=3, frameon=False)
    _save(fig, path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--data", type=Path, default=PROJECT_ROOT / "paper" / "data" / "exploratory_v060.json"
    )
    ap.add_argument("--out-dir", type=Path, default=PROJECT_ROOT / "paper" / "figures")
    a = ap.parse_args()
    data = json.loads(a.data.read_text())
    with matplotlib.rc_context(RC):
        scatter(data, a.out_dir / "fig_h4_scatter.pdf")
        confidence_by_round(data, a.out_dir / "fig_confidence_by_round.pdf")
    print(f"wrote fig_h4_scatter.pdf and fig_confidence_by_round.pdf to {a.out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
