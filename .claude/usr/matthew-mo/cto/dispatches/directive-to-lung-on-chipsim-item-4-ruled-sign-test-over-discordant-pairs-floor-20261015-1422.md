---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-15T13:22
status: created
priority: normal
size: task
subject: "Item 4 RULED: sign test over discordant pairs, floor fixed BEFORE the model sees labels (coverage + power move to stage 2; the PVR's p=1/2^7 does NOT carry over — unit changed from transporters to pairs). k_sink = B now, C as protocol. Still owed: the t4 DVC question."
in_reply_to: null
---

# Item 4 RULED: sign test over discordant pairs, floor fixed BEFORE the model sees labels (coverage + power move to stage 2; the PVR's p=1/2^7 does NOT carry over — unit changed from transporters to pairs). k_sink = B now, C as protocol. Still owed: the t4 DVC question.

# Item 4 and k_sink RULED. Stage 1's acceptance test is now specified. Build it.

Both from the principal's structured grill, 2026-10-15, recorded in `workstreams/lung-on-chipsim/approvals.md` rows 4 and 5 with verbatim quotes.

## Item 4 — acceptance test: **sign test over discordant pairs, floor fixed BEFORE the model sees the labels**

Verbatim: *"Sign test over discordant pairs, floor set before the model sees labels"*.

The ordering is not a detail, it is the whole mechanism:

1. The principal's 26 P-gp verdicts land.
2. **Count the discordant pairs** — pairs whose two members differ on the efflux call. Only those carry information.
3. **Simulate power at that realised count** and **fix a minimum floor**.
4. **Only then** does any model run. Above the floor, stage 1 is inferential. Below it, stage 1 is **descriptive and says so in the paper**.

**A floor chosen after seeing results is not a floor.** Build steps 2 and 3 so they cannot read a model output — if the power simulation can see a prediction, the pre-registration is decorative.

**The unit of inference has changed, and this matters for the write-up.** The PVR's sign test counts *transporters* — seven of them, giving p = 1/2⁷ ≈ 0.008. This test counts *pairs*. Same test name, different unit, different n, **so the PVR's p-value does not carry over**. Recompute at the realised n and never reproduce 0.008 as if it still applied. Given this project exists to study claims that outlive their evidence, inheriting a p-value whose denominator no longer exists would be the worst possible own goal.

**Moved to stage 2:** the Mondrian / group-conditional coverage criterion and the power ≥ 0.80 floor. They cannot be met at n = 26 and are **not** stage-1 gates. They live where the ~20-conformal-points-per-group sealed allocation exists.

Declined: keeping the PVR criteria unchanged (stage 1 would fail coverage and power by construction — the gate outcome known before the work started); descriptive-only stage 1.

## k_sink — **option B now, option C as the protocol recommendation**

Verbatim: *"B now, C as the protocol recommendation"*.

- **B:** keep the single first-order sink constant, and state the limitation **in the primary source's own quoted words** — *"applying a single constant to describe drug loss in an Organ Chip will not capture these dynamic concentration distributions and may inaccurately describe the dosing window."* Quote it, do not paraphrase it; the quotation is what makes the limitation unarguable.
- **C** is adopted as the **protocol recommendation** for runs not yet performed: pre-equilibrate the device and treat loss as an offset.
- **The `k_sink` prior may now be filled under option B.**

Reasoning recorded: parameter parsimony is the binding constraint at this n, and a model that declares its misspecification serves the validation-barrier thesis better than one hiding it in more terms. Option A was declined for adding two parameters against a calibration set of tens — in exactly the regime where parameter count is the problem.

Remember this is **stage-2 territory** under the two-stage decision, so it does not gate stage 1. It was ruled now so the limitations section can be written.

## Still open, and still not yours

The `test_t4_dvc_pointer_tracks_the_snapshot` question from my kickoff dispatch is unanswered: was your "0 failed" on the design branch real, or did it depend on untracked files in that worktree? **Answer that before building the acceptance test.** A pre-registration built on a suite whose green was environmental would be worth nothing.
