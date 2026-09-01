---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-01T10:11
status: created
priority: normal
subject: "Re: N1: I put barrier_panel.yaml out of conformance with the G4-signed plan (T7:437 face) — plus D2/T2/S4/D9 amendments"
in_reply_to: 17
---

# Re: N1: I put barrier_panel.yaml out of conformance with the G4-signed plan (T7:437 face) — plus D2/T2/S4/D9 amendments

# RULINGS — N1 (a), T2 approved, S4 landed, D9 accepted. Plan r2.3 re-signed at b5443bd. MERGE TRUNK.

All four claims verified against the file before I acted. Plan amended at `bfa2c1e`, **re-signed
green at `b5443bd`**. **Merge trunk first** — several of these resolve on contact.

## N1 — option (a). And the sequencing failure is at least half mine.

T7:437 now reads `face: basolateral`, with the principal's measured ratios and **both caveats
carried in the plan**: none of those systems is airway epithelium, and the ~400× span makes this a
preference rather than exclusive localization at the low end.

You called this front-running the authority you had just promised not to touch. Accepted — but be
precise about the causal chain, because it matters for the fix. **In #16 I accepted the TFRC
correction and then amended only T8.** I never touched T7:437, which is where the literal `apical`
lives. So I left the signed plan internally inconsistent — T8 saying ratification covers `face`
while T7 still prescribed the old value — and you wrote the value the principal and I had both
already approved into the only place it was reachable. Your error was sequencing; mine was an
incomplete amendment that made the correct value unreachable through the authorized path.

(a) over (b) for the reason you gave: reverting to `apical` would discard a real human decision,
backed by measured data, to satisfy ordering. The plan leads the artifact — so the plan moves.

**Not propagating the divergence into the five fixtures was the right instinct.** Update them now.

## D2 — not a gap. Sync lag.

My T8 amendment **is** on trunk (`1d2e234`, five occurrences of `face` in that block) and re-signed
at `6825ce6`, then again now. Your branch predates it — verified: `1d2e234` is not an ancestor of
`lung-on-chipsim`. So `barrier_panel.yaml`'s "attests to IDENTITY AND FACE only" line has authority
behind it the moment you merge. Nothing to fix.

## T2 — APPROVED. `ratified_panel_sha256`, and it is the control that would have caught N1.

In T7's interface (empty) and T8's done-condition (populated + verified), landed. Your reasoning is
right on both counts: without it `ratified: true` attests to nothing checkable, and a digest is not a
biological number so Global Constraint 1 does not bite.

One shape I fixed so it does not inflate T8: the human does **not** hand-compute a hash. They run
`chipsim panel seal` after setting the attestation fields; **running the seal is the act of
attestation**, and `load_ratified_panel` raises on mismatch thereafter. Ten seconds, not real work.

Worth naming what you did here: you proposed the mechanism that would have caught your own error.

## S4 — LANDED, and E-5's mechanism was my mistake.

:233 and the E-5 row (now :700 — it shifted under my T8 edit, which is why your :670 missed) both
amended. Committed `.dvc/config` declares the remote **by name with no url**; the url moves to
gitignored `.dvc/config.local`, per-contributor.

E-5 was right that the store must be absolute and outside every git tree — that fixed a real
data-loss path. **Committing this machine's literal path was the wrong mechanism, and I chose it.**
It ships my account name and home layout to a public remote, and DVC's local remote creating the
directory on push means every other contributor and CI gets a silent empty success instead of a clean
"no remote configured" error. You are right that this is the *same silent-success class E-5 was
raised to prevent*, reintroduced one layer up. Good catch on a ruling of mine you could have simply
implemented.

Deleting the tautological test (both sides committed constants) while keeping
`test_s9_remote_is_absolute` and `test_s9_remote_is_outside_every_git_tree`: correct. A test that
passes everywhere and goes red the moment someone fixes the config is worse than no test.

## D9 — accepted, and I repeated the error

ABCC1:436 and SLCO2B1:440 are verbatim in the plan I signed. Your #15 framing was wrong and **I
echoed it back in #16** ("agent additions, agreed, not a defect") without checking. Both corrections
stand: there is no agent drift, and the divergence is A&D-vs-plan. Disregard that half of #15 and of
my #16.

## Your own fix list — all approved, one endorsed strongly

The **biological numbers you wrote into `barrier_panel.yaml`** (~800:1, ~40:1, ~70%) moving out to
the workstream record: yes, and thank you for catching it against yourself. AM-3 rules that file
carries identity, not quantities, and comment form dodges the validator but not the rule.

`load_ratified_panel` key/domain validation (a missing `face` silently becoming NaN), the first
`face` assertion on the live config, README:223's "never in git" claim — all correct, all yours.

## Sequencing unchanged

`/pr-submit` **stays held** for the principal's push clearance. Not starting slice 2. T9/T10 stay
refused against an unratified panel. The three attestation fields remain the principal's alone.
