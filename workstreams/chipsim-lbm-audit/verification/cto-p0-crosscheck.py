#!/usr/bin/env python3
"""CTO independent cross-check of P0's `insensitive`-unreachability result.

Provenance for the half-width figures cited in the A&D and ASSUMPTIONS. Run from
`projects/lung-on-chipsim` with the project env:

    uv run python ../../workstreams/chipsim-lbm-audit/verification/cto-p0-crosscheck.py

Deliberately uses a DIFFERENT seed (4242) from the agent's P0 scan, and cells chosen
independently, so agreement is a cross-check rather than one implementation agreeing
with itself. Recorded output is in `cto-p0-crosscheck.out`.

This exists because a peer-reported measurement carried as an established fact is
exactly what the no-fabrication rule covers — flagged in the QG review, correctly.
"""

from chipsim.audit.power import power_scan

SEED = 4242
TRIALS = 200
N_BOOT = 600
CELLS = ((0.5, 0.2), (0.7, 0.2), (0.3, 0.0))
N_VALUES = (40, 160)

def main() -> None:
    print(f"seed={SEED} trials={TRIALS} n_boot={N_BOOT} equivalence=0.10 sensitive_floor=0.20")
    for rho_native, rho_shuffled in CELLS:
        for r in power_scan(
            n_values=N_VALUES,
            rho_native=rho_native,
            rho_shuffled=rho_shuffled,
            equivalence=0.10,
            sensitive_floor=0.20,
            trials=TRIALS,
            n_boot=N_BOOT,
            seed=SEED,
        ):
            print(
                f"rho_nat={rho_native} rho_shuf={rho_shuffled} n={r.n:3d}  "
                f"half_width={r.median_half_width:.3f}  "
                f"P(insensitive)={r.p_fits_equivalence_band:.3f}"
            )

if __name__ == "__main__":
    main()
