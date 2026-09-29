---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-29T02:39
status: created
priority: high
size: task
subject: "ACK #483: conditions MET; the $16.37 is a 3x count error (123 runs / 369 rounds, not 369/1107) — projected ~$7.2, NO line change, withdraw the principal ask; corrected plan -> A4 lock -> client gate -> relaunch"
in_reply_to: null
---

# ACK #483: conditions MET; the $16.37 is a 3x count error (123 runs / 369 rounds, not 369/1107) — projected ~$7.2, NO line change, withdraw the principal ask; corrected plan -> A4 lock -> client gate -> relaunch

ACK #483. Conditions 1-4 are MET on the evidence (no refusals on the six Validator prompts, served==requested on 35/35, between_tools + effort in output_config, temperature 0.3 on Haiku identical to the OpenRouter roster, ceilings 4x/min 256, schema adaptation in A4-1). Good report.

THE $16.37 IS AN ARITHMETIC ERROR — NO MARGIN DECISION IS NEEDED. WITHDRAW the (a) ask to the principal now; (b) declined; (c) moot.

The count: PREREGISTRATION.md gives 41 held-out tasks x 3 lifecycle seeds = 123 lifecycle RUNS, x 3 rounds = 369 ROUNDS, = 369 calls per role (the 369 you correctly used in #479 and #481). #483 used "369 runs x 3 rounds = 1107" — the trainer grid's 1107 (41 tasks x 27 records) leaked into the lifecycle count, tripling three lines:
- LLM: your "$8.78" = 3 x $2.93. Re-done from your own per-role means x 369: DataCurator 0.20+0.08, Literature 0.24+0.46, Architect 0.22+0.10, Trainer 0.17+0.06, Validator 0.63+0.77 => about $2.93.
- Lifecycle fits: 369 fits x 3.05 s = 18.8 min => about $0.41 (not $1.24).
- LLM latency while the A100 is held: 9.2 s x 369 rounds = 0.94 h => about $1.25 (not $3.75).
- Trainer re-run $1.24 is right (that one IS 1107 fits).
Corrected: LLM ~2.93 + GPU ~2.90 + prior 1.3548 => PROJECTED ~$7.2, inside the $12 line with ~$4.8 margin. Cap-worst-case LLM ~$9.7 (input 1.46 + Haiku caps 2084 tok x 369 x $5 = 3.85 + Validator 1192 x 369 x $10 = 4.40), not $29.10.

Redo the table with exact figures and put the count derivation in the plan as one line citing the pre-registration rows (41 tasks; 3 seeds; 3 rounds). The number changed shape between #481 and #483 while the grid did not — that is this project's defect family, and the plan must make it impossible to repeat: the calls-per-role figure appears ONCE, derived, and every cost line multiplies it.

Keep the lifecycle sequential — no concurrency change inside the GPU function (per-call provenance and replay detection stay exact; the saving is ~$0.9 and not worth a change in the trusted path before a pre-registered run).

APPROVED, in this order: corrected plan (same doc) -> A4 text with the corrected projected total -> LOCK v0.6.0-a4, fresh namespace -> AnthropicClient /quality-gate (#480 test list + range-failure test + no-fallbacks-in-body test) -> relaunch from the receipted SHA with --prior-spend-usd 1.3548, $12 stop / $28 kill / $30 ceiling unchanged. Report spend, GPU-hours, stop_reason counts, served-model asserts, and per-record replay verdicts at the end as before.
