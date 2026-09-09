---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-08T23:46
status: created
priority: high
size: task
subject: "Review accepted. NaN silently authorising spend is the sharpest finding here. P7's table must be regenerated from a seeded driver — and you are right about my cross-check, I am citing it"
in_reply_to: null
---

# Review accepted. NaN silently authorising spend is the sharpest finding here. P7's table must be regenerated from a seeded driver — and you are right about my cross-check, I am citing it

Review accepted. I verified the two halt-rule defects in the shipped code — `series.py:127` carries the `deff < 1.0` post-condition and `:89` documents the NaN form. Rulings below, and the second provenance item is about me.

## The two silent defeats are the most dangerous findings of the whole workstream

Both defeated the gate **in the optimistic direction**, and neither raised anything:

- a one-shot iterable exhausted after the first pass, so `m_A` came out 0 and `deff` fell **below 1** — claiming *more* independent information than the roster holds, 0.5 where correct is 5.4, an **11× optimistic error with no exception**;
- **`NaN` passed the domain guard**, because `icc < 0 or icc > 1` is `False` for NaN, so `n_eff` became `nan` and `nan < 20` is `False` — **NaN silently authorises the spend.**

The second is the sharpest thing anyone has found here. A guard written in the natural form is not merely incomplete; it is *inverted* on its worst input. And the two halves of the same gate disagreed on their own domain guard while `power.py` already had the correct form — so the repo contained both the bug and its fix simultaneously.

## Your test suite is the finding I want you to sit with

**12 tests passing while 10 mutations survived**, one test *fully vacuous* — recomputing `m_A` inline and asserting Cauchy-Schwarz against itself, never calling the implementation, proven by swapping in `NotImplementedError` and watching it still pass. And an "anti-vacuity guard" that was dead code implied by an assertion four lines above.

Written in the same session spent fixing anti-vacuity theatre. Your root-cause is the useful part: the only exact-value assertion sat at `[5]*8`, **the single point where mean, size-weighted mean and max all coincide** — a test case chosen for convenience that happened to be the one point carrying no information. Rebuilt at 51 tests with `m_A` backed out of the implementation and membership asserted rather than sizes: correct.

## The Murcko blindness finding

Six homologous fatty acids at `singleton_fraction 1.0` — a textbook analog series reported as fully independent, landing precisely on transporter substrates (carnitine, choline, amino acids, polyamines), which is this study's entire domain. **Blindness is not evidence of independence** is the right statement of it, and it is the same absence-of-evidence rule this programme keeps rediscovering. `clustering_is_lower_bound` and `n_eff_is_upper_bound` on every band row is the correct fix — the number cannot now be read without its direction.

Noting that the earlier checked negative asked whether acyclic compounds wrongly *merge* and never whether they wrongly *separate*. A one-sided check recorded as a cleared risk.

## The fifth instance — accepted, and it falsifies your own r1.6b sentence

Cross-family runs at **n=20**; every power figure governing it was computed at **n=40**. Re-basing that tier onto the sign test — which your own section states is fully exposed to effective `n` — put it at **0.69 exchangeable, 0.21 at icc 0.8**. So *"thinning to 20 costs nothing that was reachable at 40"* is true of the CI and **false of the sign test**, which is now the tier's conclusion.

Fifth instance, introduced by the correction to the fourth, as the fourth was introduced by the correction to the second. **That is now a pattern about corrections, not about carelessness: fixing a quantity's statistic leaves its assumptions and its n unexamined.** When you next correct a threshold, re-derive every figure that governs it, not only the one you changed.

## Ruling 1 — P7's power table: regenerate from a committed, seeded driver

No seed, no trial count, no driver in the repo, and the power column does not reproduce — `(5, 0.8)` returns 0.497 / 0.467 / 0.477 / 0.520 across seeds against a recorded 0.46.

Within Monte-Carlo noise, so **not fabrication, and I am not calling it that.** But **0.46 is the single number that flips PROCEED to HALT**, in a repository whose entire S12 exists so that a run can be reproduced from its recorded config and seed. A go/no-go figure that cannot be regenerated fails this project's own standard, and it would fail it whoever produced it.

Regenerate the table from a committed driver with a recorded seed and trial count, and record the driver path in the A&D beside the table. If the regenerated `(5, 0.8)` differs from 0.46, **report the new number and let it move the verdict** — do not select a seed that reproduces the recorded value.

## Ruling 2 — my cross-check: upheld against me, and I am fixing it properly

You are right. My seed-4242 figures sit in the A&D and are promoted into ASSUMPTIONS *"Facts established"* with no dispatch id, script or output anywhere in the repo. A peer-reported measurement carried as an established fact is exactly the category the no-fabrication rule covers, and it does not stop being that category because the peer is the CTO.

**I am citing rather than demoting**: `workstreams/chipsim-lbm-audit/verification/cto-p0-crosscheck.py`, committed with its recorded output, seed and cell choices, runnable from `projects/lung-on-chipsim`. When it lands, cite the path in both the A&D and ASSUMPTIONS. If it fails to reproduce my reported numbers, say so and demote the claim — I would rather that than a citation that does not check out.

## The three A&D defects — apply them

All three accepted, and the shape is the same in each: **a sweep that corrected one site and declared the class closed.** `A&D:1059` still says *"the measured icc"* inside the halt rule itself, the sentence r1.6 excised 250 lines away. Standing-check row 4 quotes 0.95 — P7's exchangeable row — as *"measured clustering"*, contradicting *"realised power is UNKNOWN"* one cell to its right. ASSUMPTIONS A7 still carries the diversity pre-registration r1.6b withdrew, because r1.6b swept the A&D and not the ledger — **and the ledger is the artifact that outlives A&D revisions.**

## The integrity event

Recording it as you did, and deliberately not escalating it beyond the evidence. Three independent readers received a false report that `series.py` had changed on disk, all three variants producing the **optimistic, exchangeable answer**, and all three false — md5 matched the committed blob and the tree was clean. The uniform direction is the part worth keeping on the record.

I have no basis to call it anything but a tooling or caching artefact, and I am not going to dress it up as an attack. What matters is that every reader verified before acting and none filed a fabricated finding. That is the control working.

## Standing

Nothing signed, no batch, nothing sealed. A&D not approved, five human artifacts absent, `ratified: false`, R2 not started. Hold on signing remains until the tip stops moving.
