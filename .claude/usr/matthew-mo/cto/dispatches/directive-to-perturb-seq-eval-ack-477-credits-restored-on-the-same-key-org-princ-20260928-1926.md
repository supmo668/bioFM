---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-29T02:26
status: created
priority: high
size: task
subject: "ACK #477: credits restored on the SAME key/org (principal); retry count_tokens, bounded dry run (5 calls, <= $0.50), then costed plan + amendment 4 per #476; ids re-cited and verified; HOLD stands"
in_reply_to: null
---

# ACK #477: credits restored on the SAME key/org (principal); retry count_tokens, bounded dry run (5 calls, <= $0.50), then costed plan + amendment 4 per #476; ids re-cited and verified; HOLD stands

ACK #477. Stopping at zero spend on a 400 credit refusal was right, and rendering the 30 prompts first means the count is instant once the door opens.

PRINCIPAL ANSWER (2026-09-28, this session): "balance restored for the project." Same org, same Infisical entry (ANTHROPIC_API_KEY, project syntropyhealth-app, env dev) — no different key. Presence-check it again under `infisical run`; never print the value.

DO NOW, in order:
1. Retry the free count_tokens on the 30 rendered prompts. If it is still refused, report the exact status + message and stop (do not switch entries on your own).
2. MEASURED DRY RUN — authorised, bounded: at most ONE real call per role on the Haiku default (5 calls), max_tokens capped, structured outputs on, total dry-run spend ≤ $0.50. Record reported usage per call. That spend counts toward the $30 total and appears as its own line in the plan. Nothing beyond those 5 calls before approval.
3. Costed plan to me per #476: projection from observed tokens x list price x the full grid, arithmetic shown, cached-input accounted, both lines on TOTAL (GPU + LLM + prior $1.3 + dry run): $12 stop-and-report, $28 kill, ceiling $30. Model ids and prices RE-CITED against Anthropic's published pricing page at plan time with the date — the ids in #477 came from a cached table and one of them I cannot confirm exists; verify each id against the models endpoint before it goes in the plan, and name the endpoint you used.
4. Amendment 4 text with the plan (A4-1 roster pinned by model id + liveness; A4-2 lines as above); Validator on a different tier from the roles it judges if the budget allows, said in the plan and the methods; single-family + same-family-judge caveats carried.

HOLD stands for the sweep itself until I approve the plan. Order after approval: A4 lock → AnthropicClient /quality-gate receipt → relaunch from the receipted SHA with --prior-spend-usd updated to include the dry run.
