"""R5 pair-count power curve — committed, seeded driver.

Run from `projects/lung-on-chipsim`:

    uv run python ../../workstreams/chipsim-lbm-audit/verification/r5-pair-count-curve.py

Regenerable per the P7 ruling: a number that sizes the roster must be reproducible
from a committed driver with a recorded seed and trial count. Output is committed
alongside as `r5-pair-count-curve.out`.

**This reports a curve. It does not pre-register a pair count.**
"""

import sys

sys.path.insert(0, ".")

from chipsim.audit.cliff_power import cliff_power  # noqa: E402

SEED, TRIALS, ALPHA = 4242, 2000, 0.05
BASE = 0.55  # descriptor baseline near chance on cliff pairs
PAIRS = (10, 15, 20, 25, 30, 40, 60)

print("R5 · power vs PAIR COUNT — one-sided exact McNemar on discordant pairs")
print(f"seed={SEED}  trials={TRIALS}  alpha={ALPHA}  descriptor baseline p={BASE}")
print()
print("CONSERVATIVE by construction: concordance=0 (arms err independently).")
print("Shared pair difficulty RAISES power (measured 0.70 -> 0.98 at n=40), so a")
print("real study sits ABOVE these rows. A2 pushes the other way; do not net them.")
print()

print("=== 1. power vs pair count, by LBM accuracy (concordance=0, no clustering) ===")
hdr = f"{'pairs':>6}" + "".join(f"{f'p_lbm={p}':>12}" for p in (0.65, 0.70, 0.80, 0.90))
print(hdr)
print("-" * len(hdr))
for n in PAIRS:
    cells = []
    for p in (0.65, 0.70, 0.80, 0.90):
        r = cliff_power(
            n_pairs=n, p_lbm=p, p_base=BASE, concordance=0.0,
            alpha=ALPHA, trials=TRIALS, seed=SEED,
        )
        cells.append(f"{r.power:>12.3f}")
    print(f"{n:>6}" + "".join(cells))

print()
print("=== 2. median DISCORDANT pairs — the quantity the test actually consumes ===")
print("   (fewer than 5 discordant can NEVER reach alpha=0.05: 1/2^4 = 0.0625)")
print(f"{'pairs':>6}" + "".join(f"{f'p_lbm={p}':>12}" for p in (0.65, 0.80)))
print("-" * 30)
for n in PAIRS:
    cells = []
    for p in (0.65, 0.80):
        r = cliff_power(
            n_pairs=n, p_lbm=p, p_base=BASE, concordance=0.0,
            alpha=ALPHA, trials=TRIALS, seed=SEED,
        )
        cells.append(f"{r.median_discordant:>12.1f}")
    print(f"{n:>6}" + "".join(cells))

print()
print("=== 3. BETWEEN-pair clustering (A7 at the correct unit), p_lbm=0.80, series of 5 ===")
print("   Within-pair similarity is the SIGNAL and is NOT discounted — the unit is")
print("   the pair. A7 applies BETWEEN pairs: several pairs from one med-chem")
print("   campaign are not independent of EACH OTHER.")
print()
print("   NOTE, and it is why this sweeps concordance too: clustering correlates")
print("   pair DIFFICULTY, and difficulty reaches the outcome only through the")
print("   concordance channel. At concordance=0 it is PROVABLY INERT — a sweep")
print("   there would report a column of identical numbers and measure nothing.")
print()
hdr = f"{'pairs':>6}{'conc':>7}{'icc0.0':>9}{'icc0.5':>9}{'icc0.8':>9}{'delta':>9}"
print(hdr)
print("-" * len(hdr))
for n in (20, 40, 60):
    for conc in (0.0, 0.3, 0.6):
        cells, powers = [], []
        for icc in (0.0, 0.5, 0.8):
            r = cliff_power(
                n_pairs=n, p_lbm=0.80, p_base=BASE, concordance=conc,
                between_pair_icc=icc, cluster_size=5,
                alpha=ALPHA, trials=TRIALS, seed=SEED,
            )
            powers.append(r.power)
            cells.append(f"{r.power:>9.3f}")
        delta = max(powers) - min(powers)
        tag = "  INERT" if delta == 0.0 else ""
        print(f"{n:>6}{conc:>7.1f}" + "".join(cells) + f"{delta:>9.3f}{tag}")
print()
print("   READ THIS ROW-WISE: the delta column is the cost of clustering. It is")
print("   at most a few points, against A7's 0.95 -> 0.46 for the SIGN test.")
print("   Structural reason: McNemar consumes the SPLIT of discordant pairs;")
print("   clustering perturbs their COUNT without biasing the split.")
print()
print("=== 4. type-I error control (p_lbm == p_base), must sit at or below alpha ===")
for n in (20, 40, 60):
    r = cliff_power(
        n_pairs=n, p_lbm=BASE, p_base=BASE, concordance=0.0,
        alpha=ALPHA, trials=TRIALS, seed=SEED,
    )
    print(f"   n_pairs={n:<4} type-I = {r.power:.4f}   (exact test is conservative)")
