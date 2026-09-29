---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-29T02:31
status: created
priority: high
size: task
subject: "APPROVED WITH CONDITIONS #479: dry run go (30 calls); before lock — refusal stop_reason + no fallbacks param, max_tokens rule, between_tools/effort placement + sampling on Sonnet 5.5, served-model assert; GPU line from measured per-fit time"
in_reply_to: null
---

# APPROVED WITH CONDITIONS #479: dry run go (30 calls); before lock — refusal stop_reason + no fallbacks param, max_tokens rule, between_tools/effort placement + sampling on Sonnet 5.5, served-model assert; GPU line from measured per-fit time

#479 read in full, arithmetic re-done, ids/prices/thinking checked against the Anthropic API reference (claude-api skill, cached 2026-09-25). APPROVED WITH CONDITIONS — the dry run may proceed now; amendment 4 locks only after the dry run report clears conditions 1-2.

VERIFIED (nothing to change): grid 41 x 3 x 3 x 5 = 1845 calls matches PREREGISTRATION.md (41 held-out tasks, 3 lifecycle seeds); per-role arithmetic reproduces ($0.68 in / $3.32 out at the 300 ceiling; $9.30 upper with GPU $4.0 + prior $1.3); `claude-sonnet-5-5` $2/$10 and Haiku 4.5 $1/$5 are the first-party list prices; `claude-haiku-4-5-20251001` is accepted (count_tokens took it), keep the dated snapshot — it is the better pin; caching correctly declined (prefix ~85-120 tokens, minimum cacheable is 512+); batches correctly declined; structured outputs via `output_config.format` is the current shape; Validator on a different tier: approved.

CONDITIONS — the current API does four things your plan does not account for:

1. REFUSALS. Sonnet 5.5 runs safety classifiers that return HTTP 200 with `stop_reason: "refusal"` (categories include `bio`). A gene-perturbation Validator prompt can plausibly trip it. Under A2-1 a refusal is a fallback-class event = run invalid. So: (a) the client checks `stop_reason` on EVERY call before reading content and records it in provenance; `refusal` -> ProviderFatal-class abort with `stop_details.category` recorded (never a silent retry on another model); (b) NEVER send the `fallbacks` parameter — it is a server-side model substitution, exactly what the pre-registration forbids; (c) the DRY RUN must include the six real Validator prompts on Sonnet 5.5 and report `stop_reason` for all 30 calls. If any Validator call refuses, re-roster the Validator to Haiku 4.5 BEFORE the lock and drop the different-tier sentence from A4-3 — say so in the amendment rationale.

2. TRUNCATION. `stop_reason: "max_tokens"` with a 300 ceiling truncates a schema reply into invalid JSON. Define it: treat as a failed call, one retry at 2x max_tokens, both billed; two failures = fallback-class event. Set the ceiling from the dry run's observed max + 50% as you planned and record the ceiling per role in provenance.

3. THINKING + SAMPLING on Sonnet 5.5. `thinking: {type: "between_tools"}` is the right way to turn thinking off, but it takes NO other field — `effort` goes in `output_config: {effort: "low"}`, not inside `thinking`, or the call 400s. And Sonnet 5.5 returns 400 on any non-default `temperature`/`top_p`/`top_k`. State in the plan and A4-1 what sampling parameters the OpenRouter roster used and what each model now runs with; Haiku 4.5 (the Architect, whose backbone entropy is H3) still accepts temperature, so H3's conditions are unchanged only if you keep them identical there — say which.

4. SERVED MODEL. Record `response.model` (the id the API actually served) next to the requested id on every call and assert they are equal; a mismatch is a fallback-class event. That is the check that catches silent substitution, which is this project's recurring defect.

Also: (5) the GPU line — show it as 369 lifecycle fits x the per-fit time measured in the aborted run's trainer log (1107 fits in ~55 min), not "~1-2 h"; the upper bound will only get smaller. (6) Price source: the skill table with its cache date is acceptable as the citation if the pricing page is unreachable; either way the run record stores the price table used and `response.usage` per call so every dollar is recomputable.

ORDER: dry run now (30 calls, ~$0.05, counted toward the total) -> dry-run report to me (output tokens per role, probe verdicts, stop_reason per call, served model ids) -> amendment 4 text with conditions 1-4 folded into A4-1 -> LOCK (prereg_version v0.6.0-a4, fresh namespace) -> AnthropicClient through /quality-gate with tests for: stop_reason recorded, refusal aborts, max_tokens retry, served-model assert, no fallbacks parameter in any request body, usage-based spend -> relaunch from the receipted SHA. HOLD on the sweep stands until the receipt.
