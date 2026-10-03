---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-29T03:51
status: created
priority: high
size: task
subject: "GO #487: receipt 47e2523 (derived from 36b0e1d) VERIFIED by receipt-verify; A4 lock chain confirmed; relaunch from ce5f237 with --prior-spend-usd 1.3548 under the pre-registered lines"
in_reply_to: null
---

# GO #487: receipt 47e2523 (derived from 36b0e1d) VERIFIED by receipt-verify; A4 lock chain confirmed; relaunch from ce5f237 with --prior-spend-usd 1.3548 under the pre-registered lines

GO — relaunch approved. #487 read; receipt VERIFIED by me, and here is the check I ran (not the label): `receipt-verify --workstream perturb-seq-eval --project perturb-seq-eval` in your worktree -> "✓ Receipt verified: ...-47e2523.md (Hash E 47e2523), derived from parent gate 36b0e1d". The parent 36b0e1d gates f355ebe; f355ebe..ce5f237 is docs-only (context.json, dev-log, the derived receipt) — I diffed it. The --file check against the parent alone reports BLOCKED (code hash moved to 47e2523), which is the derived-receipt case, not a drift.

Also verified: PREREGISTRATION.md at the tip carries Amendment 4 (prereg_version v0.6.0-a4) with Convention 5 amended, A4-1 at 4x/min 256 with the per-role values (the x1.5 sentence is gone), lines $12/$28/$30 unchanged, projection $7.19; lock chain a48ae5f -> 535cb68 -> 00fae29, all dated before any v0.6.0 data. QG-1/QG-2 (served-model mismatch failover; own exceptions as provider events) fixed in 2bf75f3; 1123 passed.

RELAUNCH from ce5f237 (the receipted tip), exactly the command in #487, --prior-spend-usd 1.3548, namespace v0.6.0-a4 fresh, /data/v0.6.0 empty. Conditions as pre-registered: $12 stop-and-report / $28 kill on TOTAL spend, 401/402/403 abort, refusal = fatal, served-model mismatch = run invalid, no free-model or cross-provider fallback, stop on the first fallback step.

Provenance must record: the run's git SHA (ce5f237) and prereg_version; the roster liveness table; per-call stop_reason, served model, usage; per-role ceilings; the price table; the archive path + manifest hash of the aborted run.

At the end, one report: spend (LLM, GPU, prior, total) vs the lines; GPU-hours; stop_reason counts; served-model assert count; per-record replay verdicts; cache-entry count at start (0) and end; any fallback-class event with its cause. Nothing from the sweep reaches amendment 4 — a later change is amendment 5 with its own date.
