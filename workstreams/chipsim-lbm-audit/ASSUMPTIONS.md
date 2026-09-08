# Assumptions ledger — chipsim-lbm-audit

Every assumption this PoC rests on, with **which direction it errs**. That column
is the point: an assumption whose direction is unknown is more dangerous than one
that is known to be optimistic, because only the second can be corrected for.

Referenced by id from the code that depends on each (`chipsim/audit/power.py`
cites A1, A3, A5, A6 at their use sites). **An assumption not in this file is a
defect**, not an omission — the r1.3 sweep exists because two of them had been
sitting unstated in the A&D for two revisions.

Status: `LIVE` (in force), `RETIRED` (measured, replaced by a fact), `OPEN`
(identified, not yet resolved).

---

## P0 · the power simulation

| id | Assumption | Direction of error | Status |
|---|---|---|---|
| **A1** | The joint distribution of (measured, native-pred, shuffled-pred) is a **Gaussian copula**. | **Unknown.** Spearman is rank-based so the *marginals* are irrelevant — that part is safe. The *dependence structure* is not: a copula with tail dependence (strong binders agreeing more than mid-range ones, which is plausible) would change CI width in a direction I have not derived. This is the least-controlled assumption in P0. | LIVE |
| **A2** | Measured affinities are **noise-free ground truth**. | **Optimistic.** ChEMBL/BindingDB values carry assay and inter-lab error; published inter-assay reproducibility on pIC50 is routinely ±0.5 log or worse. Real noise **attenuates** `ρ_native`, so the true effect is smaller than simulated and **actual power is below the table**. P0's "92% at Δρ=0.5" is an upper bound. | LIVE |
| **A3** | Native and shuffled predictions are **conditionally independent given the measured value** — shuffling destroys target information entirely. | **Pessimistic for `insensitive`, optimistic for the sign test.** If the arms share a ligand-driven component their ρ estimates co-vary, the paired difference has lower variance, and CIs narrow. Swept explicitly at `ρ_shuf = 0.2`; `P(insensitive)` stayed 0.000 throughout, so the conclusion is robust to it. | LIVE |
| **A4** | All seven targets share **the same n and the same true Δρ**. | **Optimistic, and materially so.** Measured-pair counts will differ per target (ABCB1 is far better characterised than SLCO2B1), and effects will differ. Heterogeneity **reduces** sign-test power below the table, because the unanimity criterion is only as strong as the weakest target. **The pilot must report per-target n**, and P0 should be re-run on the realised counts rather than a common n. | OPEN |
| **A5** | `insensitive_reachable` uses a **5% frequency floor**. | **Convention, not derivation.** Recorded so nobody later cites it as computed. It did not affect the conclusion — every cell returned exactly 0.000, so no threshold choice could have changed the verdict. | LIVE |
| **A6** | Ties are ranked by **average**. | **Neutral, but load-bearing.** Ordinal ranking would silently impose an order the data lacks; censored and repeated assay values tie routinely. Tested. | LIVE |
| **A7** | Ligands are **exchangeable**, so bootstrap-over-ligands is valid. | **Optimistic, and QUANTIFIED (P7).** At series of 5 with icc 0.5, n_eff = 13.3 and sign-test power falls **0.95 → 0.75**; at icc 0.8, n_eff = 9.5 and power **0.46**. P0's headline 92% is the exchangeable case. **Composition now matters as much as count**, and compound selection must maximise diversity. Realised clustering is measurable locally from SMILES; P0 is re-run on it. | MEASURED (magnitude), OPEN (realised value) |
| **A8** | `numpy` is available. | **Was hidden.** It arrived transitively via pandas while `power.py` imports it directly. Now declared explicitly in `pyproject.toml`. | RETIRED |

---

## Design-level

| id | Assumption | Direction of error | Status |
|---|---|---|---|
| **A9** | Boltz-2 throughput on **L40S is ~90 complexes/GPU-h**. | **Corroborated, not measured.** The Boltz-2 paper reports *"20 GPU sec"* per complex on H100 (~180/GPU-h); the PVR's 80–100/GPU-h for the slower L40S is consistent with that. G2's estimator deliberately uses the **slow** bound so the error direction is fail-closed. Pilot measures the real rate. | LIVE |
| **A10** | The `$30` ceiling is the binding constraint. | **Probably false, and the PVR says so** — *"the surviving pair count, not the $30 ceiling, may be the binding constraint."* P0 agrees: the budget closes at $26.87, while power depends entirely on n. **Assembling measured pairs, not GPU spend, is the real risk to this study.** | LIVE |
| **A11** | `Δ_mut` (R4) is on a scale where an `±1 SD` band is meaningful. | **Unverified.** The band formula is sealed but its output is unknown until the pilot runs. Cross-check is mandatory: if `2 SD` lands below Boltz-2's published PMAE (0.85–1.20 log₁₀), R4 claims resolution finer than the model has demonstrated on differences. | OPEN |
| **A12** | Boltz-2 predictions are **reproducible enough** for a replay tolerance to exist. | **Unknown, and unknowable from the literature.** The affinity head is a two-model ensemble and the paper never uses the word "deterministic". If run-to-run σ is large, R10's tolerance is wide enough to be vacuous. Pilot measures it. | OPEN |
| **A13** | The AFDB wild-type pose is **stable enough** that a 5 Å pocket definition is meaningful. | **Unmitigated.** Chai-1 was the check and is excluded, so nothing detects a wrong pose. An unstable pose mis-assigns "pocket", corrupting the contrast R4 *is*. F2a's RSA+Grantham matching bounds the damage but cannot detect it. Belongs in the report's limitations. | LIVE |

---

## Facts established (no longer assumptions)

| was | now | source |
|---|---|---|
| "bootstrap CI" | **BCa**, coverage 0.930 at n=40 (nominal 0.95) | P0 test suite |
| "percentile is too narrow here" | **False for this statistic.** percentile 0.943 / half-width 0.386 vs BCa 0.930 / 0.384 — equivalent. G5's general argument stands; its specific claim did not survive measurement | P0, 300 trials |
| "`insensitive` may be unreachable" | **Unreachable.** `P(insensitive) = 0.000` in all 36 scanned cells, n ≤ 160 | P0 scan |
| "is the study three-region?" | **Two-region in practice**, declared in advance by principal's ruling 2026-09-08. Band NOT widened; `insensitive` NOT deleted; the card must say the study *can demonstrate moiety-sensitivity but never its absence* | 1B1 |
| "does P0 replicate?" | **Yes.** CTO re-ran on seed 4242 with its own cells: half-widths 0.342–0.421 at n=40, 0.167–0.206 at n=160, `P(insensitive)=0.000` throughout — third-decimal agreement | CTO cross-check |
| "the study may be underpowered" | **92% power at Δρ=0.5, n=40** *for exchangeable ligands*; **0.46–0.75 under realistic analog-series clustering** | P0 scan, P7 |
| affinity units | `log₁₀` of µM | Boltz-2 paper |
| error on *differences* | PMAE **0.85–1.20** log₁₀ | Boltz-2 paper |
| activity cliff | MMP + **≥100-fold** | Stumpfe & Bajorath |
