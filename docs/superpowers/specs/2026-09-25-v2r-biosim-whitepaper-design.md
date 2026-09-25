# Design — v2r-loop / BioSim white paper (publication-rigour)

**Status:** approved by principal 2026-09-25 (approach A + claims-traceability script).
**Owner of substance:** `aviary-biosim` worktree agent (Aviary-BioSim repo, `paper/`).
**CTO role:** coordination + publication-rigour review; lands nothing it wrote.

## 1. Decisions already taken (do not relitigate)

| # | Decision | Chosen |
|---|---|---|
| D1 | Evidence base | **Drain 1 as it ran** + the BioSim science run. No new drain. |
| D2 | CoreWeave | **Venue framing only.** Compute was Apple MPS + W&B Inference (SUBMIT.md honesty note stands). |
| D3 | Audience | **ML-focused computational biologists.** |
| D4 | Teaching spine | **The loop as a lab method**: spec ≈ pre-registration, sealed test ≈ blinded assessment, run record/trace ≈ lab notebook, instinct ≈ protocol amendment. BioSim/ESM-2 is the worked experiment threaded through every section. |
| D5 | Self-improvement | **Mechanism, not result.** Designed and shown; pass-to-pass improvement was **never measured** and the paper says so. "Self-improving" is not a result claim in the title or abstract. |
| D6 | Venue | arXiv-style preprint (cs.LG, cross-list q-bio.QM), 10–14 pp LaTeX. **Zenodo DOI** (sandbox first) for PDF + frozen repo snapshot + evidence. arXiv = **PREPARED**, manual upload. |
| D7 | Publish path | The consolidated publish CLI + n8n orchestration (option **(a)** in §10.4 of `research/PUBLICATION_PIPELINE_SPEC.md`). This paper is the pipeline's first real project. **No live deposit without the principal's explicit go.** |

## 2. The paper's contributions (what it may claim)

1. **A lab-method framing of an agentic build loop** for comp-bio: vision → research → spec expansion (standing requirements R<n>) → build units with sealed, independently authored tests → a gate that closes only on an *observed* pass → run records/traces → captured instincts.
2. **The intended agentic plugin tool**: `aiadlc` `/v2r-loop` with `tools/register` (the worklist, and the only thing that may close a unit), `tools/referee` (sealed-suite runner + signed receipts), and `tools/spend` (the loop's own first product). Described as a reusable artifact with version and install instructions.
3. **A failure-mode taxonomy from auditing our own trust core.** Every defect found (7 in `tools/referee`, plus the 0.57–0.60 audit findings) shares one shape: *a mechanism reports success while the property it exists to guarantee is absent.* Each entry gives the symptom, why it passed review, and the regression test that now pins it, plus a named comp-bio analogue (benchmark leakage, silent QC skip, unlogged model identity; cf. the perturb-seq-eval review).
4. **Worked experiment (BioSim):** `BioSimEnv` as an aviary Environment; ESM-2 650M over UniProt proinsulin; 2,090 substitutions; disulfide cysteines at −13.02 vs −5.85 elsewhere; an agent that took 66 measurements and ran C-peptide controls unprompted. Claimed **as reported by that run**, reproduced where the artifacts allow (§4), and labelled where they do not.

**May NOT claim:** measured self-improvement; CoreWeave compute; end-to-end budget enforcement (never run, per `SUBMISSION.md:75`); any biology beyond what `science/out/` and the run trace support; anything from `.v2r/run-record-*.yaml` (see §3).

## 3. Evidence-integrity finding (must appear in the paper's limitations)

The on-disk `.v2r/` state is **not drain 1.** `dashboard/seed_demo_run.py` wrote a seeded 23-unit, 3-drain fixture into the live `.v2r/` directory, overwriting the real (untracked) drain-1 record and register. Its tells: a placeholder `register_sha` ending `…1eef`, pins `d4e5f6a1b2c3` / `9a8b7c6d5e4f`, and record-1 listing U-014/15/17 as both closed and parked. `register verify-record` reports all three records **UNVERIFIED**. The seeded data depicts pass-to-pass improvement, which is the exact claim D5 forbids. The public dashboard artifact already discloses the fixture, so nothing published overclaims.

**Consequences:**
- Drain-1 evidence is git history: the skeleton commit + the close commits `28af3c4` (U-001) … `2e00aa3` (U-006), `docs/drain-1-notes.md`, the six instinct files, and any recoverable Weave traces (project `3m-m/Aviary-BioSim`).
- The paper reports drain 1 as **"reconstructed from version control; the register-written run record was lost"**, not as a verified record.
- **Also:** the cache read path for sequences had no integrity check when the published numbers were computed (F31, private row). The paper states this under reproducibility.
- **Fix (build item B1):** the seeder must refuse to write into a live `.v2r/` (use a separate fixture dir, or refuse when a real register exists). This is itself a taxonomy entry: the paper's own evidence nearly failed the paper's own thesis.

## 4. Build + analysis work (aviary-biosim agent)

| id | work | output | label in paper |
|---|---|---|---|
| B1 | Seeder isolation fix + test | code + test | — |
| A1 | **Reproduce drain 1 today:** check out the drain-end commit, run the six sealed tests through `tools/referee`, record the verdicts | `paper/evidence/drain1-rerun.json` (+ referee receipt) | *measured (re-run, date)* |
| A2 | Reconstruct the drain-1 timeline from git (unit, commit, sealed-test path, statement, R<n>) | `paper/evidence/drain1-from-git.csv` | *reconstructed* |
| A3 | Science numbers **from a verified input** (amended 2026-09-25, #288/F31): fetch the proinsulin record fresh from UniProt, bypassing the cache, and record accession + release + length + sha256 (A3a); compare to the published run's input where recoverable (A3b); re-run ESM-2 650M over the hash-recorded sequence and recompute 2,090 / −13.02 / −5.85 / C-peptide (A3c). Recomputing from `results.json` alone is NOT a measurement: it re-derives outputs and cannot detect a wrong input | `paper/evidence/science.json` + input record | *measured (re-run)* only if A3c matches; mismatch → flag before prose; input unestablished → *reported* |
| A4 | The 66-measurement agent run: locate its trace/log. If found, extract counts + control choices; if not, state so | `paper/evidence/agent-run.json` or a NOT-FOUND note | *measured* / *reported, trace unavailable* |
| A5 | Failure-mode taxonomy table from plugin CHANGELOG 0.56–0.60 + drain-1 notes, each row citing its regression test by path | `paper/evidence/taxonomy.csv` | *documented* |
| A6 | Plugin suite counts at the cited version (re-run, not copied from the changelog) | `paper/evidence/plugin-tests.json` | *measured* |
| A7 | **Claims-traceability script:** `paper/claims.yaml` maps every number and claim in the TeX to `file:field` + a label. `paper/claims.py` fails on any unmapped number, missing file, value mismatch, or *reported* claim phrased as *measured* | script + CI-runnable check | — |
| A8 | Figures generated only from `paper/evidence/` (loop schematic; drain-1 timeline; cysteine score distribution; taxonomy) | `paper/figures/*.pdf` + generating scripts | — |
| W1 | Draft `paper/main.tex` (D3/D4 structure, §5) | TeX + PDF | — |
| P1 | `paper/publish.yml` per `PUBLICATION_PIPELINE_SPEC.md` §12 (`topic` required, no default; authors/ORCID **principal-supplied at the publish gate**, no placeholders) | yml | — |

Every run logs and saves its exact config (git SHA, model ids, seeds, versions) next to its output. This is a standing rule.

## 5. Paper outline

1. Introduction: why comp-bio should treat an agent's build like an experiment.
2. The loop as a lab method (D4 mapping table; the trust boundary: who can close a unit).
3. The plugin tool: architecture, install, the three CLIs.
4. Worked experiment: BioSim (environment, ESM-2 evaluator as the frozen reward channel, results with labels).
5. What the audit found: the failure-mode taxonomy, with comp-bio analogues.
6. Limitations: D5, the §3 evidence finding, MPS/serverless compute, budget enforcement never run end to end, a single drain, instincts not yet shown to change an outcome.
7. Preconditions for measuring improvement (what drain 2 would need; **no protocol executed**).

Appendix: claims table (auto-generated by A7) and reproduction commands.

## 6. Gates

1. Agent plan → `/grill-me` plan gate → build/analysis (A1–A8, B1) → `/iteration-complete`.
2. Draft → **CTO publication-rigour review** (A7 must pass first; every number checked against `paper/evidence/`).
3. Principal: authors/ORCID, Slack channel, and the go for a Zenodo **sandbox** deposit.
4. Principal: explicit go for live Zenodo; the arXiv bundle is handed over for manual upload.

## 7. Out of scope

New drains; CoreWeave runs; the instinct-pin fix (separately gated); any live deposit; OpenAIRE; retroactive edits to the published 66-measurement prompt sites (handoff item 14).
