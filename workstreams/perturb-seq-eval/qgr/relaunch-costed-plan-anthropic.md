# Costed plan — v0.6.0 sweep on the Anthropic API (CTO #473/#474/#476; principal 2026-09-29: Anthropic, < $30, Haiku where it passes)

Measured on 2026-09-29 with the FREE `count_tokens` endpoint on the REAL role prompts rendered by the lifecycle on the local
Adamson pilot (2 tasks x 3 rounds x 5 roles = 30 prompts; schema-valid recording stub, no generation, 0 spend).
Evidence: `workstreams/perturb-seq-eval/qgr/evidence/anthropic-token-measure-20260929.json`.
Prices: Anthropic first-party list prices from the `claude-api` skill's model table (cached 2026-09-25): Haiku 4.5 $1.00 in / $5.00 out
per MTok (cache read ~10%); Sonnet 5.5 $2.00 / $10.00 (cache read $0.20). Model ids as served by `GET /v1/models` on 2026-09-29:
`claude-haiku-4-5-20251001` (pinned dated snapshot), `claude-sonnet-5-5`.

## 1. Roster per role (cheapest model that passes the role's STRICT schema probe; step up only on a failed probe / dry run)
| role | model | why |
|---|---|---|
| DataCurator | claude-haiku-4-5-20251001 | cheapest; schema has no free-text reasoning |
| Literature | claude-haiku-4-5-20251001 | cheapest |
| Architect | claude-haiku-4-5-20251001 | cheapest; on-menu backbone enforced by structured outputs |
| Trainer | claude-haiku-4-5-20251001 | cheapest |
| Validator | claude-sonnet-5-5 | DIFFERENT TIER from the roles it judges (same-family-judge caveat, #473): the judge is not the same model as the proposers |
Failover: every role fails over to the other model (Haiku <-> Sonnet 5.5) — "a rotating pool with failover" (Convention 5) inside one family.
Structured outputs (`output_config.format` = the role's JSON schema, `additionalProperties: false`, required fields incl. confidence and, for
the Validator, `dynamic_threshold_msd`; for the Architect the backbone enum = the pinned menu) make every reply schema-valid by construction:
no reformat retries, no parse fallbacks. Thinking: omitted on Haiku 4.5 (none); `thinking: {type: "between_tools"}` + `effort: low` on Sonnet 5.5
(thinking off — thinking tokens are billed output). Preflight probes each role's models with the role's schema (as now); liveness table in provenance.

## 2. Cost estimate (arithmetic shown; grid = 41 tasks x 3 seeds = 123 runs x 3 rounds x 5 roles = 1845 calls)
| role | model | calls | measured mean input tok (max) | input $ | output $ at the 300-tok ceiling |
|---|---|---|---|---|---|
| DataCurator | claude-haiku-4-5-20251001 | 369 | 320 (354) | 0.12 | 0.55 |
| Literature | claude-haiku-4-5-20251001 | 369 | 273 (307) | 0.10 | 0.55 |
| Architect | claude-haiku-4-5-20251001 | 369 | 300 (303) | 0.11 | 0.55 |
| Trainer | claude-haiku-4-5-20251001 | 369 | 240 (274) | 0.09 | 0.55 |
| Validator | claude-sonnet-5-5 | 369 | 353 (396) | 0.26 | 1.11 |
| **LLM total** | | 1845 | | **0.68** | **3.32** |

- LLM upper bound (every reply at the 300-token ceiling): **$4.00**. Realistic (observed schema replies ~120 tokens): **$2.01**.
- GPU: the aborted run's trainer phase took ~55 min ($1.32/h A100 = $1.2); the lifecycle phase adds ~1-2 h of fits (linear/mlp/scgpt_small
  per round) — planned at **$4.0** (upper) for the whole run.
- Prior spend carried in: **$1.3** (aborted run).
- **Projected total (upper): $9.30; realistic: $7.31** — inside the $12 stop line with ≥ $2.70 margin at the upper bound; the $28 kill and the $30 ceiling are far.
- Per-call worst case with failover retries (each retry re-bills input; output unchanged): +0.68 at most if every call retried once — still inside the line.

## 3. Cost levers (measured effect)
- Prompt caching: NOT effective here — the shared per-role prefix is only ~120 tokens (measured), below the minimum cacheable prefix; no breakpoints set,
  nothing promised. (Reads would be billed at ~10% if it applied; it does not.)
- Message Batches (50% off): NOT used — a run's rounds are sequential (round r+1 prompts depend on round r's replies) and per-call provenance /
  replay detection must stay exact; batching would restructure the lifecycle. Declined on the CTO's own condition.
- max_tokens ceiling per role: 300 tokens for the upper bound above; set from the dry run's observed maximum + 50% margin before the run.
- Structured outputs: removes the reformat retry (which re-billed input + output) — the one real saving.
- Dry run before the sweep (on approval): 2 tasks x 3 rounds x 5 roles = 30 real calls ≈ $0.05, to measure OUTPUT tokens per role and confirm
  each role's Haiku probe; if Haiku fails a role's schema at run time, that role steps up to Sonnet 5.5 (+ about $0.30 per role at the ceiling).

## 4. Lines
$12 stop-and-report and $28 kill on TOTAL spend (GPU + LLM + prior $1.3), both inside the principal's $30 ceiling. LLM cost = API-reported usage
(input, output, cache_read, cache_creation) x the pinned prices, accumulated per call — not an estimate. 401/402/403 abort (never fall back).
The sweep stops on the first fallback step (as gated).

## 5. Key handling
Holder: Infisical, project syntropyhealth-app, env dev, entry name ANTHROPIC_API_KEY (one entry; presence verified by name under `infisical run`);
used only via `infisical run`; never printed, logged, committed or dispatched. The org now has credits (principal, 2026-09-29).

## 6. Client
`AnthropicClient` (official `anthropic` SDK, pinned in pyproject + the Modal image) with the same `chat_json` contract: model_id per call recorded,
structured outputs, cooldown-wait on 429/5xx/overloaded (as gated for OpenRouter), 401/402/403 -> ProviderFatalError, cache-hit replay detection
unchanged (same disk cache keyed by model_id), spend meter reading `response.usage`. Through /quality-gate with a receipt before the run; tests for
model_id provenance, 402-abort, replay detection, usage-based spend.

## Scientific caveats (carried into amendment 4 and the methods)
- Single model family: all five roles are Claude models; results cannot claim cross-family generality, and the choice-entropy measurand (H3) may be
  lower than a multi-family pool would give. Stated plainly in the methods.
- Same-family judge: the Validator judges proposals from the same family; the plan puts the Validator on a different TIER (Sonnet 5.5) from the four
  proposer roles (Haiku 4.5) and reports it as such; residual same-family bias is acknowledged.


---
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
