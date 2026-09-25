---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-25T09:50
status: created
priority: normal
subject: "Re: YES for the quality gates, on three conditions; the sweep is NOT covered by this"
in_reply_to: 281
---

# Re: YES for the quality gates, on three conditions; the sweep is NOT covered by this

ACK #281 — gates proceeding under your three conditions (AIADLC_TRUNK_REF=origin/main: stale-revert-check exit 0, 'branch includes trunk (origin/main)'; stage only perturb-seq-eval paths; no PR until the push).
SWEEP — the three confirmations you asked for, for your go (I will not start it without it):
 1. HVG lead 4: RULED — your #227, option (ii). Trainer-path fix LANDED on this branch: T8b in 18f32b1 (train-only HVG per held-out task in Adamson single-file, Adamson combined, Norman and the lifecycle; targets force-included; hvg_mode/hvg_n/n_forced/n_params recorded), red-then-green evidence qgr/evidence/C-RG-1-hvg-*.txt.
 2. OPENROUTER_API_KEY: PRESENT in syntropyhealth-app/dev (presence-only check just now; value not read). Injected via infisical run, OPENROUTER_KEY_SOURCE=infisical:syntropyhealth-app:dev; preflight refuses without it or without the pinned pre-registration (0c2932a).
 3. PRICE: estimate ~4 A100-h ~ $5-6 (41 tasks, ~2,214 trainer cells + 123 lifecycle runs, A100-40GB @ $1.32/h) — under the #202 envelope ($28 soft cap; in-loop kill). Memory measured 17.99/32 GiB both-resident (plan/run-precheck.md).
Holding the sweep for your go. Gates next.
