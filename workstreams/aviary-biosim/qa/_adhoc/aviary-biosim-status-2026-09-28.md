---
type: status
workstream: aviary-biosim
repo: supmo668/Aviary-BioSim (public; submodule at projects/aviary-biosim)
date: 2026-09-28
verdict: results not ready — no review surface compiled
measured_from: origin/main 274270d · origin/aviary-biosim ab8f6f5 (read-only clone, 2026-09-28)
---

# Aviary-BioSim — status before any review surface

**Verdict.** The white paper's objectives are not met and its results are not ready, so no HACP
review surface was compiled for this project. What exists on the public remote is the hackathon
submission state plus a hardening gate; the paper's evidence files do not exist on any pushed branch.

## What is on the remote

| Branch | Tip | What it holds |
|---|---|---|
| `main` | `274270d` | The AGI House / CoreWeave submission state: `SUBMISSION.md`, `SUBMIT.md`, the v2r-loop skill, `BioSimEnv`, the ESM-2 experiment scripts, the marimo dashboard. |
| `aviary-biosim` | `ab8f6f5` (44 commits ahead of `main`) | The F08 test-isolation gate (five passes), the mutation catalogue (48 live entries), the `esm_tool` accession guard, the deferred-findings register (F08–F35), the HACP floor (`docs/hacp/` L0 index + six L1 pages), and the #272 white-paper implementation plan draft `c885126`. |
| `whitepaper` | **not on the remote** | Per the CTO directive of 2026-09-26 21:08 UTC, all #272 work (A1–A8, B1, W1, P1) lands on a local `whitepaper` branch cut from `ab8f6f5`. None of it is visible from the repository. |

## Where the paper stands against its own plan

| Item | Plan | Visible state |
|---|---|---|
| F08 pr-submit | Directed 2026-09-26; receipt `4217902` verified by the CTO | Branch pushed; `main` unchanged, so the land has not happened |
| A1 — re-run drain 1 through the referee | Unblocked 2026-09-26 21:19 UTC (G1 confirmed against `3d1fd5f`) | `paper/scripts/sealed_suite_results.sh` exists only on the local `whitepaper` branch; no `paper/evidence/drain1-rerun.json` on the remote |
| A3a–c — science numbers from a verified input | Authorised (torch + ESM-2 650M, isolated env) | Not on the remote. Until A3c runs, 2,090 / −13.02 / −5.85 stay **reported**, not measured, because the cache read path had no integrity check when they were computed (F31, held) |
| A4 — the 66-measurement agent run | Trace located 2026-09-26 (plan Task 6) | Not on the remote |
| A7 — claims-traceability check | The review entry condition | Not on the remote |
| W1 — `paper/main.tex` | After A1–A8 | Not started on any visible branch |
| Gates 3–4 — sandbox and live Zenodo deposit | Principal's explicit go | Not reached |

## What the hackathon-era numbers are

These are the figures the submission reports and the HACP `§eval` page on the branch labels by kind:

| Figure | Kind (per `docs/hacp/eval.md` on `aviary-biosim`) |
|---|---|
| 328 science tests, 445 across the loop | measured 2026-09-26 (F08 re-gate) |
| 42 worklist-tool tests | measured 2026-09-25 |
| 2,090 substitutions; −13.02 vs −5.85; 66 measurements | **reported** by the science run, not re-derived |
| Drain 1: 6 closed, 0 parked | **reconstructed** from version control; the register-written record was overwritten by the demo seeder |

## Why this is not ready for a review surface

1. The evidence that the paper is built on (A1–A6) has not been produced on any branch this
   session can read, and the plan's own rule is that a claim with no artifact is cut.
2. The paper's central science numbers are labelled *reported* until A3c re-measures them from
   a hash-recorded input. Compiling them into a review surface now would present reported numbers
   as reviewable results, which is the exact failure the #272 plan's claims check exists to stop.
3. F33 changed the identifier rule for the evidence files (open publication, scoped, 2026-09-26);
   the paper's methods text has to carry that rationale, and it does not exist yet.

## What would make it ready

- The `whitepaper` branch pushed, with `paper/evidence/*.json` carrying provenance blocks and
  `paper/claims.py` passing.
- A1's referee receipt and A3c's match-or-mismatch verdict recorded.
- The CTO's publication-rigour review started (its entry condition is A7 green).

At that point the HACP floor already on the `aviary-biosim` branch (`docs/hacp/`) is the surface to
extend; it should not be duplicated here.
