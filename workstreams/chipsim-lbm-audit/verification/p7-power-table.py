#!/usr/bin/env python
"""Regenerate P7's clustered sign-test power table from a recorded seed.

CTO ruling, 2026-09-08: the table in the A&D had no seed, no trial count and no
driver anywhere in the repo, and its power column did not reproduce — `(5, 0.8)`
returned 0.497 / 0.467 / 0.477 / 0.520 across seeds against a recorded 0.46. That
is within Monte-Carlo noise at 300 trials and is NOT fabrication, but 0.46 is the
single number that flips the halt rule from PROCEED to HALT, in a repository whose
S12 machinery exists so a run can be regenerated from its config and seed.

Run from `projects/lung-on-chipsim`:

    ./.venv/bin/python ../../workstreams/chipsim-lbm-audit/verification/p7-power-table.py

Deliberately NOT seed-shopped. SEED is fixed at 0, chosen before running, and the
output is reported whatever it says — including if it moves the verdict. TRIALS is
raised from the original 300 to 20000 so the Monte-Carlo standard error (~0.0035)
sits in the third decimal rather than the second; at 300 trials the SE was ~0.029,
which is the entire discrepancy this driver exists to remove.

Both ligand counts are generated. n=40 is the within-panel arm and the headline.
n=20 is the CROSS-FAMILY tier, whose power was never computed: r1.6b re-based that
tier's conclusion onto the sign test, and the sign test is fully exposed to
effective n, so the tier that the fix made sign-test-dependent is the one tier
running at half the ligand count.
"""

from __future__ import annotations

import math
import sys

from chipsim.audit.power import clustered_sign_test_power
from chipsim.audit.series import effective_n_unequal

SEED = 0
TRIALS = 20_000
N_TARGETS = 7
RHO_NATIVE = 0.5
RHO_SHUFFLED = 0.0  # true delta-rho = 0.5

# (series size, icc) — the seven cells of P7's table, unchanged.
CELLS = [(1, 0.0), (2, 0.5), (3, 0.5), (5, 0.3), (5, 0.5), (5, 0.8), (8, 0.8)]
LIGAND_COUNTS = [40, 20]


def mc_stderr(p: float, trials: int) -> float:
    return math.sqrt(max(p * (1.0 - p), 0.0) / trials)


def main() -> int:
    print(
        f"seed={SEED}  trials={TRIALS}  n_targets={N_TARGETS}  "
        f"true_delta_rho={RHO_NATIVE - RHO_SHUFFLED}"
    )
    print(f"Monte-Carlo SE at p=0.5: {mc_stderr(0.5, TRIALS):.4f}\n")
    for n in LIGAND_COUNTS:
        arm = "within-panel / headline" if n == 40 else "CROSS-FAMILY tier"
        print(f"### n = {n} ligands  ({arm})\n")
        print("| series size | icc | n_eff | sign-test power | MC SE |")
        print("|---|---|---|---|---|")
        for size, icc in CELLS:
            if size > n:
                continue
            n_clusters, remainder = divmod(n, size)
            sizes = [size] * n_clusters + ([remainder] if remainder else [])
            n_eff = effective_n_unequal(sizes, icc)
            power = clustered_sign_test_power(
                n=n,
                n_targets=N_TARGETS,
                rho_native=RHO_NATIVE,
                rho_shuffled=RHO_SHUFFLED,
                cluster_size=size,
                icc=icc,
                trials=TRIALS,
                seed=SEED,
            )
            print(
                f"| {size} | {icc} | {n_eff:.1f} | **{power:.3f}** | {mc_stderr(power, TRIALS):.4f} |"
            )
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
