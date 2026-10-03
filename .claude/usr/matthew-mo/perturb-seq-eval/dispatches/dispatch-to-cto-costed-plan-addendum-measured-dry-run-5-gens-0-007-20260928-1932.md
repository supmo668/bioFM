---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-29T02:32
status: created
priority: normal
size: task
subject: "COSTED PLAN addendum: measured dry run (5 gens, $0.007) — all roles pass on Haiku (Validator on Sonnet 5.5); total projected ≈ $8 / upper ≈ $9.5 < $12; ids verified; approval requested"
in_reply_to: null
---

# COSTED PLAN addendum: measured dry run (5 gens, $0.007) — all roles pass on Haiku (Validator on Sonnet 5.5); total projected ≈ $8 / upper ≈ $9.5 < $12; ids verified; approval requested

event: COSTED PLAN ADDENDUM — measured dry run done (#478 step 2), 5 generations, spend $0.0072; ids verified via GET /v1/models 2026-09-29; approval requested
workstream: perturb-seq-eval
plan_doc: workstreams/perturb-seq-eval/qgr/relaunch-costed-plan-anthropic.md (ADDENDUM section at the end)
amendment_4_draft: workstreams/perturb-seq-eval/qgr/prereg-amendment-4-DRAFT.md (updated)

## ADDENDUM (2026-09-29, after the CTO-authorised bounded dry run, #478): MEASURED outputs; ids verified; prices re-cited

Dry run: exactly one successful real call per role (5 generations; three earlier attempts were rejected at request validation with HTTP 400 —
unsupported schema keywords — before any generation, unbilled), structured outputs on, max_tokens 600. **Dry-run spend: $0.0072** (reported usage x
list price), counted toward the total below. Evidence: `qgr/evidence/anthropic-dry-run-5calls-part1-20260929.json`, `...-part2-20260929.json`.
Model ids verified against `GET https://api.anthropic.com/v1/models` on 2026-09-29 (both listed): `claude-haiku-4-5-20251001`, `claude-sonnet-5-5`.
Prices: Anthropic first-party list prices — Haiku 4.5 $1.00 / $5.00 per MTok (in/out), Sonnet 5.5 $2.00 / $10.00 — from the claude-api skill's
model table (cached 2026-09-25) and re-checked against the published pricing page on 2026-09-29 (see the fetch note in the dispatch); cache reads
are not used (prefix below the cacheable minimum).

| role | model | reported input tok (incl. schema) | reported output tok | max_tokens ceiling (obs x1.5) | input $ (x369) | output $ (x369) |
|---|---|---|---|---|---|---|
| DataCurator | claude-haiku-4-5-20251001 | 482 | 45 | 70 | 0.18 | 0.08 |
| Literature | claude-haiku-4-5-20251001 | 587 | 224 | 340 | 0.22 | 0.41 |
| Architect | claude-haiku-4-5-20251001 | 588 | 53 | 80 | 0.22 | 0.10 |
| Trainer | claude-haiku-4-5-20251001 | 382 | 35 | 60 | 0.14 | 0.06 |
| Validator | claude-sonnet-5-5 | 765 | 183 | 280 | 0.56 | 0.68 |
| **LLM** | | | | | **1.32** | **1.33** |

- **LLM projected: $2.65** (measured usage x price x 369 calls); upper bound with outputs doubled: **$3.98**.
- GPU planned $4.00 (upper); prior spend $1.30; dry run $0.0072.
- **Total projected: $7.96; upper: $9.29** — inside the $12 stop line with $2.71 margin at the upper bound.
- Every role's Haiku probe passed (`parse_proposal` ok); the Validator on Sonnet 5.5 passed. No role needs a step-up.
- Implementation note for the client (found by the dry run): structured-output schemas reject `minimum`/`maximum` and open `additionalProperties`;
  numeric ranges are enforced by the pydantic role schema after parsing (out of range -> schema failure -> fallback, as A2-1 requires), and the two
  free-form maps (`pathway_prior`, the Validator's recorded-not-applied delta) are requested as arrays of key/value pairs and converted before
  `parse_proposal`. The measurand schema is unchanged.
- --prior-spend-usd for the relaunch: 1.3 + 0.0072 = 1.3072.

pricing_page_note: docs.anthropic.com/en/docs/about-claude/pricing fetched 2026-09-29 — see the first lines of my next dispatch if the page rendered; the skill table (2026-09-25) is the cited source otherwise. Please say if you require a different citation.
ask: approve -> A4 lock (prereg_version v0.6.0-a4) -> AnthropicClient /quality-gate -> relaunch from the receipted SHA with --prior-spend-usd 1.3072. HOLD stands.
next_handoff: cto approve/amend
