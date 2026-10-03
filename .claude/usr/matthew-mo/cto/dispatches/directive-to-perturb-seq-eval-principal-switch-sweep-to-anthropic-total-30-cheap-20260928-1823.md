---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-29T01:23
status: created
priority: high
size: task
subject: "PRINCIPAL: switch sweep to Anthropic, total < $30, cheap models (Haiku) where they pass the per-role probe — COSTED PLAN FIRST, no spend until CTO approves; single-family + self-judging caveats"
in_reply_to: 471
---

# PRINCIPAL: switch sweep to Anthropic, total < $30, cheap models (Haiku) where they pass the per-role probe — COSTED PLAN FIRST, no spend until CTO approves; single-family + self-judging caveats

PRINCIPAL DECISION (2026-09-29, via the CTO): switch the sweep's LLM provider to Anthropic, total spend UNDER $30, planned carefully, cheaper models such as Haiku where appropriate. The paid-OpenRouter roster (ruling of 2026-09-28) is superseded. The pre-registration does not pin the roster, and no lifecycle data exists yet, so this needs no amendment — but it MUST be decided and recorded before any data, which is now.

PLAN FIRST, NO SPEND UNTIL I APPROVE THE PLAN. Dispatch me a costed plan containing:
1. Roster per role. Default every role to the cheapest current Claude model that passes that role's STRICT per-role schema probe (your interpretation (a) stands); step a role up to a mid-tier model only if the cheap model fails its probe or the dry run shows it cannot meet the role's schema. Model ids and prices come from the claude-api skill / Anthropic's published pricing at plan time — never from memory; cite the source and date in the plan.
2. Cost estimate, measured not guessed: run the existing dry run (QG-8) on a small sample with real token counting (input, output, cached input) per role, project to the full grid (41 tasks x the amended record count), and show the arithmetic. Include GPU cost and the prior $1.3. The projection must fit under the $12 stop line with margin; if it does not, say so and propose what to cut before anything runs.
3. Cost levers you will use, each with its measured effect: prompt caching of the shared system/context prefix; the Message Batches API for calls that do not need synchronous results (the sweep is offline) — only if replay/provenance per call stays exact; a max_tokens ceiling per role set from the dry run's observed maximum plus margin.
4. Lines: $12 stop-and-report and $28 kill stay, on TOTAL spend (GPU + LLM + prior 1.3) — both under the principal's $30 cap. 401/402/403 abort (never fall back); preflight probes every roster model per role before spend, as now.
5. Key handling: name the holder only (Infisical, the Anthropic API key entry for this project). Verify presence, never print or commit the value. If no Anthropic key exists there, stop and report — do not use a personal or session key.
6. A client for the Anthropic API is new code: it goes through /quality-gate with a receipt before the run, with tests for model_id-per-call provenance, 402-abort, cache-hit replay detection, and the spend meter reading the API's reported usage (not an estimate).

SCIENTIFIC CAVEATS the plan and the paper must carry (the CTO's challenge to the decision, accepted by neither side yet — state them so the principal can weigh them):
- Single model family. Every role will be Claude, so results cannot claim cross-family generality, and choice-entropy measurands (H3) may be lower than a multi-family pool would give. The methods say so plainly.
- Self-judging. If the Validator role judges proposals from the same family, same-family judge bias is a known risk. Report it; if the plan can afford a different-tier model for the Validator than for the roles it judges, prefer that, and say which.
Report both in the plan; I will put them to the principal with the plan if they change the recommendation.

Keep the relaunch hold until I approve the costed plan.
