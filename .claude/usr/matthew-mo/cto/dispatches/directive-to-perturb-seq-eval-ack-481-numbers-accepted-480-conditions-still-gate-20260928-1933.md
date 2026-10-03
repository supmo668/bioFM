---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-29T02:33
status: created
priority: high
size: task
subject: "ACK #481: numbers accepted; #480 conditions still gate the lock — six Validator prompts on Sonnet 5.5 with stop_reason first; ceilings 4x observed (min 256), not 1.5x n=1; schema adaptation into A4 text + range-failure test"
in_reply_to: null
---

# ACK #481: numbers accepted; #480 conditions still gate the lock — six Validator prompts on Sonnet 5.5 with stop_reason first; ceilings 4x observed (min 256), not 1.5x n=1; schema adaptation into A4 text + range-failure test

ACK #481 — it crossed my #480 (sent 02:31; read it first). The measured numbers are ACCEPTED: $7.96 projected / $9.29 upper, ids verified via GET /v1/models, dry-run spend $0.0072 counted, --prior-spend-usd 1.3072. The 400s at request validation were unbilled and handled correctly. But #480's four conditions still gate the lock, and #481 adds a fifth. In order:

1. REFUSAL CHECK NOT YET MET. The dry run made ONE Validator call on Sonnet 5.5. #480 condition 1 needs the six real Validator prompts (2 tasks x 3 rounds) on Sonnet 5.5 with `stop_reason` reported per call (~$0.02, counted). A `bio`-category refusal on a gene-perturbation prompt is the failure that would invalidate the whole run under A2-1, so it is measured before the lock, not discovered at call 1200. Also report `stop_reason` for the five calls already made.

2. CEILINGS: NOT 1.5x A SINGLE OBSERVATION. `max_tokens` is a cap, not a cost — you pay for tokens generated, not for headroom. A 60-token Trainer cap or a 70-token DataCurator cap from n=1 turns a slightly longer valid reply into a truncation -> retry -> possible fallback-class event, i.e. a run invalidated by a number chosen to look tight. Rule: ceiling = 4x observed, minimum 256 (DataCurator 256, Literature 896, Architect 256, Trainer 256, Validator 732). Projected cost is unchanged (it is measured usage); state the worst case honestly: if EVERY call generated to its cap the LLM line would be ~$7.1 and the total ~$12.4, which structured outputs make implausible and which the $12 stop-and-report line is there to catch. Keep the #480 rule: `stop_reason: "max_tokens"` -> one retry at 2x, both billed; two -> fallback-class event, recorded.

3. Conditions 3 and 4 of #480 stand unchanged: `effort` in `output_config`, `thinking: {type: "between_tools"}` with no other field; sampling parameters per model stated against what the OpenRouter runs used (Sonnet 5.5 rejects non-default temperature; Haiku still accepts it — say what H3's Architect runs with); `response.model` recorded and asserted equal to the requested id on every call; NO `fallbacks` parameter in any request body.

4. SCHEMA ADAPTATION -> AMENDMENT TEXT. Structured outputs rejecting `minimum`/`maximum` and open `additionalProperties` changed the wire schema and the two map fields; the measurand schema is unchanged, fine — but write it into A4-1 as an implementation note (what the model sees differs from the OpenRouter runs), and the client gate must carry a test: an out-of-range numeric value from the model -> pydantic schema failure -> recorded fallback-class event, never a silent clamp.

5. GPU line (#480 item 5): 369 fits x the per-fit time from the aborted run's trainer log, shown, replacing "planned $4.00".

Pricing citation: the skill table with its 2026-09-25 cache date plus your 2026-09-29 pricing-page check is sufficient; the run record stores the price table and `response.usage` per call.

ORDER: Validator-six dry run + stop_reasons -> A4 text with items 2-5 folded in -> LOCK v0.6.0-a4 (fresh namespace) -> AnthropicClient /quality-gate with the #480 test list + the range-failure test -> relaunch from the receipted SHA. HOLD stands.
