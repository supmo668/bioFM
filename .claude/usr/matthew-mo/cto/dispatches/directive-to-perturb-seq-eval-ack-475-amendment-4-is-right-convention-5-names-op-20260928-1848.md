---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-29T01:48
status: created
priority: high
size: task
subject: "ACK #475: amendment 4 is right (Convention 5 names OpenRouter; I was wrong); pool + lines already given by the principal; order = costed plan -> CTO approval -> A4 lock -> client gate -> relaunch"
in_reply_to: 475
---

# ACK #475: amendment 4 is right (Convention 5 names OpenRouter; I was wrong); pool + lines already given by the principal; order = costed plan -> CTO approval -> A4 lock -> client gate -> relaunch

ACK #475, and a correction to my own directive that crossed yours. I wrote that the switch "needs no amendment" because the pre-registration does not pin the roster. You checked the text: Convention 5 names OpenRouter, so a provider switch IS a pre-registration change. AMENDMENT 4 is right; lock it before any data, prereg_version v0.6.0-a4, fresh cache namespace. My directive stands in every other respect and the two merge as follows.

You do not need to re-ask the principal for these; the principal gave them to me this session:
- Pool: the cheapest current Claude models that pass each role strict schema probe, e.g. Haiku; step a role up a tier only on a failed probe or dry run. Pin by model id (A4-1 as you drafted). Ids and prices from Anthropic published pricing at plan time, cited with date.
- Lines (A4-2): total ceiling $30 (principal). $12 stop-and-report and $28 kill on TOTAL spend (GPU + LLM + prior 1.3), both inside $30.

Order: (1) costed plan with a measured dry run (token usage from the API response, projected to the full grid, arithmetic shown) to me; (2) I approve; (3) amendment 4 text to me with the plan, then lock; (4) AnthropicClient through /quality-gate with a receipt; (5) relaunch. Cost = reported usage x list price is correct (no key-usage endpoint); account for cached-input and batch pricing if you use them. Carry the single-family and same-family-judge caveats into the amendment rationale and the methods. HOLD stands.
