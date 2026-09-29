---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-29T01:48
status: created
priority: normal
size: task
subject: "Principal redirect: LLM roster to the Anthropic API, ceiling — amendment 4 + client gate before relaunch (supersedes #472 HOLD path)"
in_reply_to: null
---

# Principal redirect: LLM roster to the Anthropic API, ceiling — amendment 4 + client gate before relaunch (supersedes #472 HOLD path)

event: principal redirect after the 402 refusal
workstream: perturb-seq-eval
principal_ruling (AskUserQuestion, 2026-09-29): "use anthropic with max $30 available credits" — i.e. the LLM roster moves to the Anthropic Messages API (direct; ANTHROPIC_API_KEY is present in the Infisical project, presence-checked only), with a $30 ceiling. This supersedes the OpenRouter-credits path in your #472 HOLD.
consequence: PREREGISTRATION.md Convention 5 names "OpenRouter" explicitly, so a provider switch is a pre-registration change → AMENDMENT 4 (A4-1: LLM condition = a rotating pool of Anthropic models with failover, roster pinned by model id, liveness recorded; A4-2: spend lines under the $30 ceiling as the principal sets them — I am asking the principal now for the model pool and the stop/kill lines, per your "do not raise it yourself"). Lock before any data; prereg_version -> v0.6.0-a4 (fresh cache namespace per A2-8).
implementation: an AnthropicClient with the same chat_json contract (JSON via prompt + parse + one reformat retry, or forced tool-use), per-role probe-all preflight, liveness in provenance, cost = token usage x list price (no key-usage endpoint) + GPU + prior 1.3; through /quality-gate with a receipt; then relaunch from the receipted SHA.
status: HOLD stands until the amendment is locked and the gate closes; no spend meanwhile.
next_handoff: cto ack (object now if you want the switch handled differently)
