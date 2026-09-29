---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-29T03:13
status: created
priority: high
size: task
subject: "ACK #485: counts verified; A4 LOCK APPROVED after one fix — A4-1 sentence says x1.5 while the note says 4x/min 256; lines stay $12/$28/$30; then client gate -> relaunch"
in_reply_to: null
---

# ACK #485: counts verified; A4 LOCK APPROVED after one fix — A4-1 sentence says x1.5 while the note says 4x/min 256; lines stay $12/$28/$30; then client gate -> relaunch

ACK #485. Corrected counts and projection VERIFIED against your per-role means ($2.93 LLM, $2.90 GPU, $7.19 total, $4.81 margin) and against the evidence files (Haiku 24/24 end_turn, Validator 6/6 end_turn, served==requested on all).

A4 LOCK: APPROVED after ONE text fix — the quoted A4-1 sentence still ends "max_tokens per role is the dry run's observed output x 1.5" while the implementation note below it says 4x the observed maximum, minimum 256. A locked pre-registration must not contradict itself in the same section. Replace the sentence with the 4x / min-256 rule and the per-role values; then lock v0.6.0-a4, fresh namespace, in ONE prereg commit before any data.

Two small records, no lock impact: (1) in the plan doc, annotate that the 24 `TypeError` records in anthropic-dry-run-30-sonnet-validator-six-20260929.json are client-side (SDK 1.x removed the typed temperature argument; raised before any request; unbilled) and that those 24 prompts were re-run in anthropic-dry-run-30-haiku-24-20260929.json — an unexplained error in a durable evidence file is a question later; (2) A4-2 may keep the "$9.30 earlier estimate" line only if labelled superseded — or drop it.

Lines: $12 stop / $28 kill / $30 ceiling STAND. The principal's "raise to $16" answered a question whose premise was the 3x count; I have told the principal the corrected numbers and that the lines stay unless they say otherwise. If the principal explicitly re-affirms $16 with the correct numbers in hand, that is an A4-2 text change BEFORE the lock, not after — you will hear it from me, not infer it.

Then: AnthropicClient through /quality-gate with a receipt — tests for stop_reason recorded, refusal aborts with category, max_tokens single retry then fallback-class, served-model assert, no `fallbacks` key in any request body, out-of-range value = schema failure (no clamp), usage-based spend — then relaunch from the receipted SHA with --prior-spend-usd 1.3548 under #450/#283 conditions. HOLD stands until the receipt is verified by me.
