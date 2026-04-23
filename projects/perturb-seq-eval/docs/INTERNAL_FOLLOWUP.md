# Internal Follow-Up Tracker

> Single source of truth for revision work on the perturb-seq-eval
> supplement. Consolidates [`REVIEWER_CRITIQUE.md`](REVIEWER_CRITIQUE.md)
> (evidence + rationale) with [`PUBLICATION_CHECKLIST.md`](PUBLICATION_CHECKLIST.md)
> (scope + venue-fit) into one tracker the team actually updates.
>
> **Edit this file as work happens.** Mark items ☑ when done, add an
> owner + date, link the PR / commit.

## 0. Current posture (2026-04-23 after §5.5 end-to-end lifecycle)

| Signal | State |
|---|---|
| Unit tests | ✅ 92/92 pytest green |
| Modal full run | ✅ complete (artifacts under [`artifacts/modal_run/`](../artifacts/modal_run/)) |
| Revision pass (MC1 + mc5 + mc8 + mc9) | ✅ bootstrap CIs + cum regret + γ_T + CI-banded figures in [`artifacts/modal_run/revision/`](../artifacts/modal_run/revision/) |
| Inline figures render in GitHub | ✅ PNG versions (Wong palette + CI bands) |
| Reviewer assessment | ✅ **Accept** — all P0 blockers closed; live-probe collection + BioFM-grounded variant both reproduced; cross-provenance conclusion robust |
| Blockers open | ✅ **0** (MC3b closed via live baseline + BioFM collection on Modal; MC4 Norman remains deferred-explicitly as an enlargement, not a blocker) |
| Budget consumed | ≤ $25 / $30 ceiling (E2 grid + image builds + BioFM cache + live collections) |
| Soonest viable submission | **bioRxiv preprint + MassGen skill PR ready now**; ICLR workshop strong-accept bar still benefits from MC4 (Norman 2019 grid) |

## 1. Headline — what to change before publication

The supplement is close but **three claims will not survive a peer
reviewer in their current form**:

| # | Overstated claim (as written) | Honest reframe needed |
|---|---|---|
| **MC1** | "Contextual GP beats CMA-ES by 2.6 % on Adamson" | *Without CIs this is a point estimate; seed-to-seed SE ~0.02 almost certainly swallows the gap. Rerun with per-seed trajectories and bootstrap 95 % CIs before quoting.* |
| **MC2** | "scgpt_small wins 5/7 Adamson tasks" | *Only seed 2026 produces 5/1/1. Seed 2027 gives 4/3/0, seed 2028 gives 3/2/2. The three backbones are statistically tied on most tasks within seed variance. Reframe as "all three backbones statistically indistinguishable per task; linear's synthetic dominance does not transfer."* |
| **MC3** | "Contextual GP routes based on probe signatures on real Adamson data" | *The probe signatures used by the Adamson E3 run are **simulated**, not collected from a live orchestrator. Must disclose (cheap) or collect real traces (1 day, $0 on OpenRouter free tier).* |

Everything else is either already honest (E3/E3b comparison, metric
drop rule, deviation log) or minor polish.

## 2. Prioritized revision backlog

Legend: **P0** blocker for submission · **P1** strongly recommended ·
**P2** nice-to-have · **P3** aesthetic.

| ID | P | Work item | Effort | Modal $ | Status | Owner | Notes |
|---|---|---|---|---|---|---|---|
| MC1 | P0 | Expose per-seed E3 trajectories; bootstrap 95 % CIs on `(final, AULC, regret)` for all three regimes; regenerate Figs 2/3/4 with shaded bands. | 4 h | $0.50 | ☑ | compbio-researcher 2026-04-22 | `OptimizerTrajectory` gained `per_seed_trajectories`, `cum_regret_per_iter`; `scripts/local/bootstrap_and_analyze.py` produces CIs (n_boot=2000); CI bands in Figs 2/3/4. **Outcome: Adamson CIs overlap; 2.6 % edge retracted.** Revision output in `artifacts/modal_run/revision/revision_stats.json`. |
| MC2 | P0 | Reframe §5.2 and §6.2 of [`SUPPLEMENT.md`](SUPPLEMENT.md) to acknowledge backbone ties within seed variance; retract "5/7 wins" headline. | 1 h | $0 | ☑ | compbio-researcher 2026-04-22 | §5.2 now quotes per-seed decomposition (5/1/1, 4/3/0, 3/2/2); §6.2 retracts architectural-advantage claim. Defensible statement: "linear's synthetic dominance does not transfer; backbone axis is non-trivial on real data." |
| MC3a | P0 | Add probe-simulation disclosure in §5.3 preamble and paper abstract. Minimum acceptable. | 1 h | $0 | ☑ | compbio-researcher 2026-04-22 | §5.3 leads with a dedicated disclosure block + pointer to MC3b. Status line at top of SUPPLEMENT.md flagged simulated probes explicitly. |
| MC3b | P1 | Collect real CellForge traces on each Adamson task via OpenRouter free tier; rerun E3-Adamson with real probe signatures. Supersedes MC3a. | 1 d | $0 | ☑ | compbio-researcher 2026-04-22 | Closed via two implementations: (a) [`scripts/local/collect_real_probes.py`](../scripts/local/collect_real_probes.py) — CellForge + rule-based tools + Nemotron rater; (b) [`scripts/modal/app_biofm.py`](../scripts/modal/app_biofm.py) — Modal image with `microsoft/BioGPT` (Literature) + `ctheodoris/Geneformer` (Validator) + Nemotron rater. Probes cached at [`artifacts/real_probes/adamson_probes{,_biofm}.json`](../artifacts/real_probes/). 175 LLM calls per variant, $0 per run on OpenRouter free tier. Full audit in [`adamson_traces{,_biofm}.jsonl`](../artifacts/real_probes/). Rerun E3 with both → all optimizer CIs overlap; conclusion unchanged across all three probe provenances (simulated / live-baseline / live-BioFM). γ_T ordering (63.10 / 37.36 / 50.59) confirms BioFM probes carry more kernel information than rule-based, but iteration budget saturates the 27-point Φ before γ_T advantage materialises. **All P0 blockers now closed.** |
| MC4 | P1 | Add Norman 2019 grid (larger, ~200 perturbations) or defer explicitly in §7 Open Questions. | 4 h + fetch | $5–10 | 🔄 deferred-explicitly | 2026-04-22 | Deferred to §7 Open Questions with rationale; CI widths on Adamson are n_tasks-limited, so Norman is the mechanically-correct path to tighter CIs. |
| mc5 | P1 | Switch primary optimizer metric from AULC to cumulative regret Σ(y_t − y_min). Retain AULC as secondary. | 1 h | $0 | ☑ | 2026-04-22 | `cum_regret_per_iter` added to `OptimizerTrajectory`; §5.3 and §5.4 tables now report final regret alongside MSD. |
| mc10 | P1 | Fix `scgpt_small` vocab size to a constant 2 000 across synthetic + Adamson grids (pad synthetic to 2 000 genes). Rerun E2-synthetic. | 2 h + rerun | $2 | ⬜ | — | Now documented as a known confound in §7 Open Questions #4. Next Modal run. |
| mc6 | P2 | Tone down "wins 5/7" language across all docs + paper. | 30 m | $0 | ☑ | 2026-04-22 | Closed by MC2 reframe (single source edit cascaded to §6.2 and §7). |
| mc7 | P2 | Rename `cma_es` → `one_plus_lambda_es` (or install the `cma` pkg and dispatch to real CMA-ES). | 30 m | $0 | ☑ | 2026-04-22 | `OnePlusLambdaES` is canonical class + registry key; `CMAESOptimizer` retained as backwards-compat alias. |
| mc8 | P2 | Compute γ_T numerically per regime or delete the bound-interpretation paragraph. | 3 h or 15 m | $0 | ☑ | 2026-04-22 | Greedy max-info-gain (Krause–Singh–Guestrin 2008) in `bootstrap_and_analyze.py`. §6.4 now quotes γ_T = 56.17 / 63.10 / 53.97 with honest caveat about what γ_T does/doesn't predict. |
| mc9 | P3 | Switch Plotly trajectory lines to Wong colourblind-safe palette. | 30 m | $0 | ☑ | 2026-04-22 | `WONG` palette in `scripts/local/render_figures_revised.py`; all five PNGs regenerated. |
| LIFECYCLE | P0 | End-to-end agentic lifecycle benchmark on Adamson (closes partial-agentic gap). | 1 d | $2 | ☑ | 2026-04-23 | v2 (`ap-wlIETcuaNPkJin8nScWi94`): **63/63 finite** runs × 3 backbones × 7 tasks × 3 seeds; mean MSD **0.117 [0.089, 0.146]**; multi-round triggered 48/63 (threshold=0.05). Post-fix `57bac5b` (DataCurator target-gene preservation). §5.5. |
| LIFECYCLE-OPT | P1 | Contextual-BO over live agentic lifecycle (headline end-to-end). | ~45 min | $1–2 | ☑ | 2026-04-23 | Modal app `ap-qqqInu3Fa4r9djbz1I3TvL`: 8 iter × 1 seed × 7 Adamson tasks, live-eval per iter. Both `random` and `contextual_gp` converge to **MSD 0.056 by iter 1**; AULC 0.4447 vs 0.4450 (Δ = 0.0003). Small |Φ|=18 → first pick near-optimum. Fig 6 updated. |

**Minimum submission bar (P0 only):** MC1 + MC2 + MC3a → **closed 2026-04-22**. bioRxiv-ready.

**Strong submission bar (P0 + P1):** MC3b (real traces) + MC4 (Norman) + mc10 (vocab fix) still open; mc5 closed. Remaining ≈ 2 engineer-days + $7 Modal.

## 1b. Revised headline numbers (post-revision pass)

All three regimes now carry bootstrap 95 % CIs (n_boot = 2 000 over task × seed). Key results:

| Regime | Contextual-GP final MSD | Contextual CI vs CMA-ES CI | γ_T (T=30) |
|---|---|---|---|
| Synthetic shared-optimum | 0.00713 [0.00660, 0.00769] | overlaps | 56.17 |
| **Adamson real (simulated probes)** | 0.05720 **[0.04904, 0.06550]** | **overlaps** | 63.10 |
| Task-conditional synthetic | 0.00989 [0.00535, 0.01535] | **does not overlap** (CMA-ES at 0.07500 [0.06375, 0.08625]) | 53.97 |

**Honest headlines now quotable in the social brief and paper:**

- "Contextual BO cleanly falsifies itself on regimes with no routable structure."
- "On a task-conditional synthetic DGP, contextual BO dominates non-contextual ES with 95%-CI significance."
- "On real Adamson pilot data (probes simulated), all three optimizers are statistically indistinguishable; the contribution on real data is the backbone-axis observation (linear's synthetic dominance does not transfer), not an optimizer-level advantage."

See [`artifacts/modal_run/revision/revision_stats.json`](../artifacts/modal_run/revision/revision_stats.json) for full per-optimizer CIs and per-seed final MSDs.

## 3. Decisions owed by the author — LOCKED 2026-04-22

- [x] **D1 — probe strategy on real data: MC3b (live real-trace collection).**
  - Baseline collection landed 2026-04-22 via [`scripts/local/collect_real_probes.py`](../scripts/local/collect_real_probes.py) using the CellForge orchestrator + Nemotron-3-Super-120B (OpenRouter free tier) as severity rater. Output: [`artifacts/real_probes/adamson_probes.json`](../artifacts/real_probes/adamson_probes.json).
  - BioFM-grounded collection on Modal via [`scripts/modal/app_biofm.py`](../scripts/modal/app_biofm.py) uses `microsoft/BioGPT` (Literature agent) + `ctheodoris/Geneformer` (Validator agent) pulled from HuggingFace Hub into a shared volume. Both cached successfully.
  - Rerun of E3-Adamson with live probes is wired through [`scripts/local/rerun_e3_with_real_probes.py`](../scripts/local/rerun_e3_with_real_probes.py).
  - **Outcome on baseline live probes:** all three optimizer CIs still overlap (contextual_gp CI `[0.04939, 0.06606]`, cma_es CI `[0.05008, 0.06721]`, random CI `[0.04864, 0.06421]`); γ_T = 37.36 (down from the 63.10 simulated probes gave us, because real probes are less dispersed in context-space). **Conclusion from live data is the same honest "statistically indistinguishable" finding.**
- [x] **D2 — publication venue: bioRxiv + arXiv preprint + MassGen contribution PR** as the immediate path. ICLR/NeurIPS workshop remains a follow-on once MC4 (Norman 2019) lands.
- [x] **D3 — artifact hosting: Zenodo as canonical DOI.** Figshare used as mirror. OSF BioHackrXiv currently blocked (D3b below); can re-enable once token is refreshed.
- [x] **D3b — OSF_TOKEN invalid as of 2026-04-22 (HTTP 401 on `/v2/users/me/`).** publish.yml has `venues.osf.enabled: true` but `submit_to_venues.py` will warn-and-skip OSF until the token is replaced. Not a blocker; Zenodo + Figshare are the two working DOI venues.
- [ ] **D4 — authorship + affiliations.** `publish.yml` still contains the `Last, First / YOUR_AFFILIATION / 0000-0000-0000-0000` placeholder block. One-line edit by the submitting author required before `submit_to_venues.py all` runs.

## 4. Pre-submission sweep (checked at the end)

| Item | Status |
|---|---|
| 92/92 pytest green | ✅ |
| `poetry build` clean wheel | ✅ |
| `modal run … --step all` reproduces every number | ✅ |
| Figures render inline in markdown viewers | ✅ (PNG) |
| P0 blockers resolved | ⬜ |
| Adamson SHA-256 recorded in README | ⬜ |
| Zenodo DOI minted for artifacts | ⬜ |
| `CITATION.cff` with BibTeX for every cited paper | ⬜ |
| No TODO / FIXME / XXX in shipped code | ⬜ audit |
| License headers on every source file | ⬜ audit |
| `pip install perturb-eval` works on a clean venv | ⬜ |
| CHANGELOG entry for the supplement run | ⬜ |
| README quick-start command renders on GitHub | ⬜ |

## 5. Venue fit (derived from §4 of [`PUBLICATION_CHECKLIST.md`](PUBLICATION_CHECKLIST.md))

Ranked from soonest-out to most-polished:

| Venue | Requires | Effort from now | Payoff |
|---|---|---|---|
| bioRxiv + arXiv preprint | P0 only (MC1 + MC2 + MC3a) | ~2 days | Gets framework in front of the community; citable; iterable in the open. |
| MassGen skill contribution PR | Code only; no paper gate | ~1 day | Evaluation skill lands upstream; widens impact surface. |
| *Nature Methods* Brief Communications | P0 + MC4 | ~5 days + $10 | Wet-lab audience, high-impact framing on the MSD-on-held-out-perturbations story. |
| ICLR / NeurIPS Agent workshop short paper | P0 + P1 (esp. MC3b) | ~5 days + $12 | ML audience, demands real-trace collection for the probe-routing claim. |

Run bioRxiv in parallel with MassGen PR; the rest depends on D2.

## 6. Cadence proposal

- **This week.** Close D1 and D2. Land MC1, MC2, MC3a. Draft a 1-page PR against MassGen. Bootstrap CIs on the headline numbers; update SUPPLEMENT.md in place.
- **Next week.** If D2 = journal/workshop: MC3b (real traces) + MC4 (Norman) in parallel. Rerun E2/E3 on Modal with the fixes. $12 ceiling.
- **Week after.** Polish pass (mc5–mc10), repo-hygiene sweep (§4 above), Zenodo upload, freeze v0.3.0 tag, submit.

Three-week window puts us on a realistic pre-ICLR submission path.

## 7. How to update this tracker

1. When you start a work item, move its status from ⬜ → 🔄 and add your name + date in the **Owner** column.
2. When you finish, flip to ☑ and add the PR / commit hash.
3. If a blocker turns into a non-blocker after fresh evidence (e.g. CIs
   *do* show a real contextual-GP advantage), re-annotate in §2 but
   leave the historical note so we can track how the claim evolved.
4. Keep this file terse. If a discussion gets long, spawn a GitHub
   issue and link to it here.

---

*Last touched: 2026-04-21 (initial consolidation from REVIEWER_CRITIQUE.md + PUBLICATION_CHECKLIST.md).*
