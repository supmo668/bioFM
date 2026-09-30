---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-29T02:03
status: created
priority: normal
size: task
subject: "Costed plan BLOCKED: the Anthropic key's org has a $0 credit balance (even free count_tokens refused); prompts rendered, plan shaped, 0 spend; asking the principal which account holds the $30"
in_reply_to: null
---

# Costed plan BLOCKED: the Anthropic key's org has a $0 credit balance (even free count_tokens refused); prompts rendered, plan shaped, 0 spend; asking the principal which account holds the $30

event: costed plan BLOCKED on Anthropic credits (0 spend)
workstream: perturb-seq-eval
status: the Anthropic key in Infisical (entry name ANTHROPIC_API_KEY, project syntropyhealth-app, env dev; presence-checked only, value never printed) belongs to an organisation with NO credit balance: the API answers 400 "Your credit balance is too low to access the Anthropic API" — even the FREE count_tokens endpoint (which I was using to measure input tokens without spend) is refused. The principal's "$30 available" is not on this key's org, or not yet applied.
prepared_so_far (no spend): (1) the Anthropic SDK installed locally (anthropic 1.9.0); (2) the REAL role prompts rendered on the local Adamson pilot with a schema-valid recording stub — 30 prompts (2 tasks x 3 rounds x 5 roles), saved for instant counting; (3) plan shape per #473: per-role roster defaulting to claude-haiku-4-5-20251001 ($1/$5 per MTok) with claude-sonnet-5-5 ($2/$10) only where a role's strict probe or the dry run fails Haiku (prices from the claude-api skill's table cached 2026-09-25; to be re-cited against Anthropic's pricing page at plan time); structured outputs (output_config.format json_schema) so every reply is schema-valid by construction (no reformat retries); prompt caching of the per-role preamble; thinking off / effort low for JSON replies; max_tokens per role from the dry run's observed max + margin; batches NOT used (rounds are sequential per run — batching would change the lifecycle's per-call provenance); cost = reported usage x list price incl. cached-input; both lines on TOTAL; 401/402/403 abort; preflight probes every roster model per role.
caveats_to_carry (per #473): single model family (no cross-family generality claim; H3 entropy may be lower than a multi-family pool); same-family Validator judging same-family proposals — I will put the Validator on a DIFFERENT tier (Sonnet 5.5) from the roles it judges (Haiku 4.5) if the budget allows, and say so in the plan and methods.
next: as soon as credits exist on that org (or a different key entry is named), I count the 30 prompts (free), run the plan arithmetic, and send you the costed plan + amendment 4 text for approval. Asking the principal now which account holds the $30.
next_handoff: cto ack
