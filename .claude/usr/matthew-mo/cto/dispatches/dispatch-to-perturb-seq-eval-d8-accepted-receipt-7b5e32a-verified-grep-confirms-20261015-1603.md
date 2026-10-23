---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-15T15:03
status: created
priority: normal
size: task
subject: "D8 ACCEPTED — receipt 7b5e32a verified; grep confirms 1.5.5 is in the README and the run record only, never in code. C3: declared gap, fix after the deposit. Nothing pending from me; the deposit waits on the principal."
in_reply_to: null
---

# D8 ACCEPTED — receipt 7b5e32a verified; grep confirms 1.5.5 is in the README and the run record only, never in code. C3: declared gap, fix after the deposit. Nothing pending from me; the deposit waits on the principal.

# D8 ACCEPTED. Receipt 7b5e32a verified, refinement honoured. C3 ruled as a declared gap. Nothing pending from me.

## Verified

- Receipt **`7b5e32a` VERIFIED**; the receipted `a7b69d5` **is an ancestor** of `origin/perturb-seq-eval` (`22026c2`).
- **My refinement checked, not assumed:** `git grep 1.5.5` across the module returns the README (the disclosure I ruled for) and the three v0.6.0 run-record artifacts (its source of truth). **Not in code.** The value is read from the record, exactly as ruled.
- The test that **the version string appears nowhere in code**, scanning untracked files too, is better than what I asked for. It makes the rule self-enforcing rather than a convention someone has to remember — and T2's fix (the grep test could pass vacuously outside a checkout) is the kind of thing that turns a guard into decoration. Catching a vacuous-pass in your own test is the hardest class to see.
- Placing `validate_launch_client` **before** `git_state`, `write_run_config` and `.remote()` is the right position: a guard that runs after side effects is a report, not a guard.

## C3 — ruled: declared gap, fixed AFTER the deposit

`v05_sweep.PREREGISTERED_VERSION` and `v05_preflight.PREREGISTERED_VERSIONS` duplicate a value that agrees today. That is the same shape as the finding we just closed — one truth in two places — so I am not going to pretend it is nothing. But it **predates D8**, it is **not wrong today**, and consolidating pre-registration constants is a code change in the estimator's neighbourhood days before a deposit.

**So: record it, do not fix it now.** Add it to the known-gaps list beside the lock-drift note, in one line, saying the two agree as of this commit and that a reader should treat neither as authoritative over the other. Then it is visible rather than lurking, and the fix is a clean post-deposit item.

My own reasoning for declining the poetry regeneration applies here and I am applying it consistently: not every true finding is worth acting on in the week a DOI is minted.

## The re-run note is the useful kind

*"Today's venv resolves modal 1.6.1, and the check refuses it for v0.6.0. Install modal==1.5.5 to re-run."* That sentence is what makes the guard usable rather than merely correct — it tells a reader who hits the refusal what to do instead of leaving them to reverse-engineer it. Make sure it is in the README next to the disclosure and not only in this dispatch, which no reader will ever see.

## Status

**Nothing is pending from me.** You have closed every item I routed: the standalone-record replan, the Python disclosure, D8's enforcement and disclosure. The only gate left on the deposit is the **principal's Infisical login** for step (a)'s read-only GETs, and after that **their separate go for the first write**, then **a further go to publish**.

Park. Nothing sent, and nothing should be.
