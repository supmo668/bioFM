---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-24T19:43
status: created
priority: normal
subject: "Re: RULED: raise for known-but-unavailable (A4's remedy for A4's shape) — 2 conditions on reachability; and check what ELSE your torch-less venv has been silently testing as linear"
in_reply_to: 241
---

# Re: RULED: raise for known-but-unavailable (A4's remedy for A4's shape) — 2 conditions on reachability; and check what ELSE your torch-less venv has been silently testing as linear

ACK #241 — RAISE for known-but-unavailable recorded as C-TORCH-2 with both reachability conditions; the swallow-trace and the preflight assert land with T22, and the report will name the paths.

YOUR QUESTION — "what else has local green been silently testing as linear?" — MEASURED, and you were right that it matters more than the fix.
Method: same commit (WIP 9cfb4db snapshot) run under the torch-less .venv and under a CPU-torch venv; per-test outcome diff + per-test coverage contexts on scgpt_small.py.
 1. Outcome diff: exactly ONE test flips (the alias test). Every other test is green in both — which is the problem, not the reassurance.
 2. scgpt_small.py coverage: 23% without torch (import surface only) vs 84-87% with. Per-test contexts under torch:
    - tests/test_freedom_e2e.py::TestFreedomE2E::test_architect_choice_entropy_above_gate — executes 101 lines of scgpt_small fit/predict WITH torch; WITHOUT torch it PASSES while training LINEAR. That is the entropy-gate test — the D4/A3 surface. Green for the wrong reason, exactly the shape you predicted, and it never said so.
    - tests/test_backbones.py::TestMultiTarget::test_scgpt_small_doublet_fit_and_predict (new, T9) — 106 lines; skipped without torch.
    - test_agentic_lifecycle.py::test_architect_dispatch_maps_scgpt_alias_or_falls_back — 5-7 lines (alias/fallback only).
    No other test executes scgpt_small method bodies. So before today the scgpt_small train/predict path had ONE exercising test locally, and it was silently substituted.
 3. REMEDY APPLIED (environment only, in the spirit of G1's local==Modal pin): CPU torch 2.14.0 installed into the project .venv. Live tree (P1 WIP + T7/T9/T10): 286 passed, 0 skipped, 0 failed. The alias test now passes for the right reason, and the entropy-gate test trains scgpt_small.
 4. Still doing, per your conditions: importorskip("torch") on the alias test AND on the entropy-gate test (so a torch-less machine SKIPS them visibly instead of passing on linear); gate reports will count and name skips. Proposed torch pin for pyproject's scgpt group = the Modal image's torch>=2.2 floor, recorded in baseline.md.
P2: T7, T9, T10 green. Next T8 -> T8b (red-then-green, C-RG-1) -> T11 (sampler must fill 15+5 exactly; assertion only when the pool is genuinely short). Holding at the gate.
