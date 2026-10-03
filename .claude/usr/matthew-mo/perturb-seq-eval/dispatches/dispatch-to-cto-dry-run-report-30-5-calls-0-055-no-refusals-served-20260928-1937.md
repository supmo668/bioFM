---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-29T02:37
status: created
priority: normal
size: task
subject: "DRY-RUN REPORT: 30+5 calls, $0.055, no refusals, served==requested, all probes pass; A4 text updated; GPU line re-derived (LLM latency) -> ≈$10.5 sequential — margin decision needed"
in_reply_to: null
---

# DRY-RUN REPORT: 30+5 calls, $0.055, no refusals, served==requested, all probes pass; A4 text updated; GPU line re-derived (LLM latency) -> ≈$10.5 sequential — margin decision needed

event: DRY-RUN REPORT (#480/#482) — 30 calls + 5 done, $0.0549; NO refusals; served==requested on all; all probes pass; conditions folded into A4-1; GPU line re-derived (LLM latency dominates) -> projected ≈ $10.5 sequential, thin margin: decision needed
workstream: perturb-seq-eval
plan_doc: workstreams/perturb-seq-eval/qgr/relaunch-costed-plan-anthropic.md (DRY-RUN REPORT section)
amendment_4_draft: workstreams/perturb-seq-eval/qgr/prereg-amendment-4-DRAFT.md (A4-1 implementation notes added)

## DRY-RUN REPORT (CTO #480/#482; 2026-09-29): 30 calls done + the earlier 5 — every condition measured

Calls: the six Validator prompts (2 tasks x 3 rounds) on `claude-sonnet-5-5` and the 24 Haiku prompts (4 roles x 2 tasks x 3 rounds) on `claude-haiku-4-5-20251001`, plus the five
first-pass calls (#478). Evidence: `workstreams/perturb-seq-eval/qgr/evidence/anthropic-dry-run-30-sonnet-validator-six-20260929.json`, `.../anthropic-dry-run-30-haiku-24-20260929.json`,
`.../anthropic-dry-run-5calls-part{1,2}-20260929.json`. **Dry-run spend (all passes): $0.0548**, counted in the prior spend.

| role | model | n | in mean | out mean | out max | ceiling (4x max, min 256) | latency mean s | stop_reason | served==requested | probe |
|---|---|---|---|---|---|---|---|---|---|---|
| DataCurator | claude-haiku-4-5-20251001 | 6 | 550 | 45 | 45 | 256 | 1.3 | ['end_turn'] | True | ['schema ok'] |
| Literature | claude-haiku-4-5-20251001 | 6 | 655 | 248 | 329 | 1316 | 3.0 | ['end_turn'] | True | ['schema ok'] |
| Architect | claude-haiku-4-5-20251001 | 6 | 593 | 55 | 57 | 256 | 1.2 | ['end_turn'] | True | ['schema ok'] |
| Trainer | claude-haiku-4-5-20251001 | 6 | 450 | 35 | 35 | 256 | 1.2 | ['end_turn'] | True | ['schema ok'] |
| Validator | claude-sonnet-5-5 | 6 | 850 | 208 | 298 | 1192 | 2.5 | ['end_turn'] | True | ['schema ok'] |

- **Refusals (#480-1): none.** All 30 + 5 calls `end_turn`; no `refusal` on any Validator prompt. Client rule anyway: `stop_reason` checked and recorded on every
  call; `refusal` -> ProviderFatal-class abort with `stop_details.category` recorded; **no `fallbacks` parameter in any request body** (test in the gate).
  The Validator stays on Sonnet 5.5 (different tier from the proposers); A4-3 keeps the different-tier sentence.
- **Ceilings (#482-2):** 4x observed max, min 256 — per role above; recorded per role in provenance. `stop_reason: "max_tokens"` -> one retry at 2x (both billed);
  two -> fallback-class event, recorded. Worst case if EVERY call generated to its cap: LLM $29.10 (implausible under structured outputs; the $12 line catches it).
- **Thinking/effort/sampling (#480-3):** Sonnet 5.5: `thinking: {"type": "between_tools"}` (no other field) + `output_config: {"effort": "low", "format": ...}`,
  no sampling parameters (API default; non-default rejected). Haiku 4.5: no thinking; **`temperature: 0.3` sent in the raw request body (the SDK 1.x removed the typed
  argument; the API accepted it on all 24 calls)** — identical to the OpenRouter roster's `temperature: 0.3` for every role, so H3's Architect sampling condition is unchanged.
- **Served model (#480-4):** `response.model` recorded and equal to the requested id on all 30 + 5 calls; the client asserts equality per call (mismatch = fallback-class event).
- **Schema adaptation (#482-4):** the wire schema omits `minimum`/`maximum` (unsupported) and expresses the two free-form maps (`pathway_prior`, the Validator's
  recorded-not-applied delta) as arrays of key/value pairs converted before `parse_proposal`; numeric ranges are enforced by the pydantic role schema after parsing
  (out of range -> schema failure -> fallback-class event, never a clamp; test in the gate). Written into A4-1.
- **GPU line (#480-5 / #482-5), from the aborted run's trainer log:** 1107 fits in 56.4 min => 3.05 s/fit. Lifecycle: 369 runs x 3 rounds = 1107 fits =>
  $1.24; trainer phase re-run (output dir empty): $1.24; **LLM latency while the A100 is held: 9.2 s per round x 1107 rounds = 2.84 h => $3.75.**
  GPU sequential total: **$6.23** (the latency term dominates — the earlier "$4.00" was low).
- **Totals:** LLM measured $8.78; GPU $6.23; prior 1.30; dry run 0.0548 => **$16.37 projected (sequential)**; cap-worst-case $36.68.
  Margin to the $12 stop line: $-4.37 projected — thin. Options for the CTO/principal: (a) raise the stop line to $16 (kill $28, ceiling $30) — a principal
  decision, not mine; (b) overlap LLM latency by running 4 lifecycle runs concurrently inside the GPU function (GPU => $3.42, total => $13.56) — a code
  change in `iter_lifecycle_records` that would join the client gate; (c) accept $16.37 and rely on stop-and-report.
- **Price citation:** skill model table (cached 2026-09-25) + the pricing page fetched 2026-09-29 (JS-rendered; prices not machine-readable) — the run record stores
  the price table used and `response.usage` per call.
- `--prior-spend-usd` for the relaunch: 1.3 + 0.0548 = **1.3548**.

ask: (1) which of (a)/(b)/(c) for the thin margin — I am asking the principal about (a) in parallel and will relay; (2) with that settled, approve the A4 text -> LOCK v0.6.0-a4 -> AnthropicClient gate (#480 test list + range-failure test) -> relaunch. HOLD stands.
next_handoff: cto approve/amend
