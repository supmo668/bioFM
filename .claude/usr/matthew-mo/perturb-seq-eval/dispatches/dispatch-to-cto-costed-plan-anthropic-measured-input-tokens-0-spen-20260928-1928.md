---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-29T02:28
status: created
priority: normal
size: task
subject: "COSTED PLAN (Anthropic, measured input tokens, 0 spend): upper-bound total under $12 with margin; Haiku 4.5 x4 roles + Sonnet 5.5 Validator; amendment 4 draft — approval requested"
in_reply_to: null
---

# COSTED PLAN (Anthropic, measured input tokens, 0 spend): upper-bound total under $12 with margin; Haiku 4.5 x4 roles + Sonnet 5.5 Validator; amendment 4 draft — approval requested

event: COSTED PLAN for CTO approval (per #473/#476) + AMENDMENT 4 draft; 0 spend so far (credits now on the org)
workstream: perturb-seq-eval
plan_doc: workstreams/perturb-seq-eval/qgr/relaunch-costed-plan-anthropic.md
amendment_4_draft: workstreams/perturb-seq-eval/qgr/prereg-amendment-4-DRAFT.md
evidence: workstreams/perturb-seq-eval/qgr/evidence/anthropic-token-measure-20260929.json (free count_tokens on 30 real rendered prompts)

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

ask: approve the plan (and the ~$0.05 dry run) -> I lock amendment 4 -> AnthropicClient through /quality-gate -> relaunch. HOLD stands until your approval.
next_handoff: cto approve/amend
