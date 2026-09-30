---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-29T03:12
status: created
priority: normal
size: task
subject: "CORRECTION (#484): count error fixed — 123 runs / 369 rounds / 1845 calls; projected ≈ $7.5, margin > $4; no line change; principal ask withdrawn; A4 text corrected — lock approval requested"
in_reply_to: null
---

# CORRECTION (#484): count error fixed — 123 runs / 369 rounds / 1845 calls; projected ≈ $7.5, margin > $4; no line change; principal ask withdrawn; A4 text corrected — lock approval requested

event: CORRECTION accepted (#484) — my 3x count error; projections re-done; principal ask withdrawn; no line change
workstream: perturb-seq-eval
plan_doc: workstreams/perturb-seq-eval/qgr/relaunch-costed-plan-anthropic.md (CORRECTION section)
amendment_4_draft: workstreams/perturb-seq-eval/qgr/prereg-amendment-4-DRAFT.md (A4-2 corrected)

## CORRECTION (CTO #484, 2026-09-29): the dry-run report's counts were 3x too high — projections re-done

The report above used 369 runs / 1107 rounds. The grid is **41 tasks x 3 seeds = 123 runs x 3 rounds = 369 rounds = 1845 calls**
(369 calls per role; 369 lifecycle fits). The measured per-call usage, latencies, stop reasons, served-model checks and probe verdicts are unchanged.

| role | model | in mean | out mean | out max | ceiling | latency s | $ projected (369 calls) | $ at the cap |
|---|---|---|---|---|---|---|---|---|
| DataCurator | claude-haiku-4-5-20251001 | 550 | 45 | 45 | 256 | 1.3 | 0.29 | 0.68 |
| Literature | claude-haiku-4-5-20251001 | 655 | 248 | 329 | 1316 | 3.0 | 0.70 | 2.67 |
| Architect | claude-haiku-4-5-20251001 | 593 | 55 | 57 | 256 | 1.2 | 0.32 | 0.69 |
| Trainer | claude-haiku-4-5-20251001 | 450 | 35 | 35 | 256 | 1.2 | 0.23 | 0.64 |
| Validator | claude-sonnet-5-5 | 850 | 208 | 298 | 1192 | 2.5 | 1.39 | 5.03 |
| **LLM** | | | | | | | **2.93** | 9.70 |

- GPU from the aborted run's trainer log (3.05 s/fit): trainer phase re-run $1.24; lifecycle fits 369 x 3.05 s = $0.41;
  LLM latency while the A100 is held 9.2 s x 369 rounds = 57 min = $1.25. **GPU $2.90.**
- **Total projected: $7.19** = LLM 2.93 + GPU 2.90 + prior 1.30 + dry run 0.0548. Margin to the $12 stop line: **$4.81**.
  Worst case if every reply generated to its cap: $13.96 (implausible under structured outputs; the $12 stop-and-report line catches it).
- **No line change** ($12 stop / $28 kill / $30 ceiling). The principal ask about raising the stop line, made on the wrong count, is withdrawn.
- `--prior-spend-usd` = 1.3 + 0.0548 = **1.3548**.

principal: I had already put the (wrong-premise) stop-line question to the principal, who chose 'raise to $16'; I am telling the principal the premise was a counting error, that the projection is under $8 with a $4+ margin, and that the lines stay $12/$28/$30 per your #484 unless the principal objects. Nothing changes in A4-2.
ask: approve the corrected A4 text -> I LOCK v0.6.0-a4 (fresh namespace) -> AnthropicClient /quality-gate (#480 tests + range-failure test) -> relaunch from the receipted SHA with --prior-spend-usd 1.3548. HOLD stands.
next_handoff: cto approve A4 lock
