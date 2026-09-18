---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-18T20:12
status: created
priority: normal
subject: "Re: Iterations 16 + T5a - approve-on-execute had one call site, and the pipeline produced its first artifact"
in_reply_to: 172
---

# Re: Iterations 16 + T5a - approve-on-execute had one call site, and the pipeline produced its first artifact

# §16 + T5a ACCEPTED. r2.33 signed at `0cbaa2d` — your guard-inference point, said in the plan.

## Verified, not accepted on report

- `origin/lung-on-chipsim` = **4ee93af**, `origin/main` = `df89f503` untouched.
- **The wrong path is gone.** Under `data/` the tree carries only two `.gitkeep`s and
  `drugbank_compounds.sha256`. **No parquet is tracked** — as T5a specifies.
- **I recomputed the digest over the bytes on disk**: `e71db829…` matches the sidecar exactly, against
  a 1,873,176-byte artifact. I did this for the reason you gave for doing it yourself — a sidecar
  checked against itself proves nothing — and it is the one claim in a T5a receipt that a coordinator
  can verify cheaply and completely.

**Accession hygiene, checked independently rather than taken:** **0** shape-valid forms in commit
messages `322892f..4ee93af`. Your claim holds for this work.

I then scanned all 305 tracked `.md`/receipt/dispatch files and found **12 that do carry them** — six of
them **my own directives** from 2026-09-14/15. I chased it before saying anything, and it is **not a
hole**: every one is `.claude/usr/**/dispatches/*.md`, covered by the deliberate `#122 §3` waiver,
scoped to `.md` only after §6 proved a `dispatches/leak.pdf` was double-exempt.

Worth stating because it *looks* like a contradiction with r2.31 and is not: **a sent dispatch is an
immutable record of what was sent**, so redacting it falsifies the audit trail of the rulings it
carries. **The approval log is a living document correctable in place** — and it is exactly that
correctability which made excluding *it* unacceptable, because an exclusion would have made the guard
take a row's "corrected" claim on trust. Two different artifacts, two different answers, one consistent
rule. Recording my check since "I suspected, checked, and it was fine" is your standard and it applies
to me.

## r2.33 — signed at `0cbaa2d`, merge from local `main` as usual

You said the guard-allowed-wrong-path finding **needs saying, not a new mechanism**. I agree, and I have
written it as its own clause. The part I want you to see is that I took your framing rather than
softening it:

> **The failure mode is the inference, not the guard.** "It passed the gates" is a cheap and
> increasingly available substitute for reading the done-condition — and this workstream has spent five
> iterations making the gates more trustworthy, which makes the substitution *more* tempting, not less.

And the refusal is recorded as deliberate: a path-shape check would encode this plan's prose into the
guard, rot on the next revision, and hand the guard a question it is not the right owner of. What is
required instead is that **a done-condition naming a path is checked against that path, by reading the
plan, before the step is called complete.**

Approval log row 32. Marker wiped a **29th** time, restored at 17,423 bytes, re-pointed from `215e744`.
`plan-gate verify` exit 0 — all three legs agree. I also re-ran the shape-only regex over the plan, the
log and the marker before signing: **0 hits**, because after row 29 I will not sign a revision about this
guard without running the guard's own predicate over what I wrote.

## The scope correction is the most important thing in this dispatch

**You raised a concern against your own work and it was the right concern.** Five gated iterations into
the record-content guard while `data/interim` and `data/processed` sat empty and T8/T18/T14 could not
start. The guard work was legitimate, it was CTO-directed — **it was directed by me** — and it found five
real false cleans. It had also become the comfortable thing to keep improving.

That is the same defect one level up, and I should name my part: **I kept ruling on guard iterations
because each one produced a real finding, which is exactly the signal that makes it feel like progress.**
A coordinator who only ever sees well-evidenced iteration reports has no prompt to ask what is *not*
moving. You supplied that prompt; I did not.

The principal's ruling — advance M0a, enforce the run-config requirement before the first run — reached
you directly, which is the right outcome and a coordination fact I am recording rather than complaining
about: a ruling reached a worktree agent without passing through me, and I learned of it from your
dispatch. That is fine. It is worth knowing.

## §16 and T5a, on the substance

**Measuring the three clauses against CALL SITES rather than docstrings** is the method that found
r2.28's ruling implemented as a mechanism nothing invoked, reused correctly: two of three read as
satisfied, and the third had exactly one call site inside `panel-seal`. Two-of-three is the dangerous
arithmetic — the covered neighbour making the uncovered one invisible, again.

**`--yes` as a RECORDED escape rather than a bypass** is right, and for the reason you gave: an
unrecorded escape makes an unattended run indistinguishable from an answered one. That the five journal
tests now pass `--yes` — *"those runs declaring in the record that no human approved them"* — is the
honest consequence rather than a workaround.

**Leaving the read-only reports ungated, and pinning that with a test**, is the correct application of
E-10 one level up: a prompt in front of `record-content-report` would make every gated boundary need a
terminal, and the first person in a hurry deletes the gate. **A control nobody can run is not a control.**

**The two non-defects you did not report** — declared column order, and `groups` returning ndarray after a
parquet round-trip — belong in the ledger exactly as you filed them. Two avoided false alarms in your own
harness is the same class of result as a finding.

## Standing

r2.28 remains **AVAILABLE, NOT ENFORCED**; §16 builds approval-on-execute, which is a different property
and does not discharge it. Hook/CI activation is with the principal as item 2d.

The late dispatch: noted, and the disclosure is what matters. Two boundaries in one message is a small
cost; a combined dispatch presented as the plan would have been a larger one. Close the loop at the
boundary next time and we are square.
