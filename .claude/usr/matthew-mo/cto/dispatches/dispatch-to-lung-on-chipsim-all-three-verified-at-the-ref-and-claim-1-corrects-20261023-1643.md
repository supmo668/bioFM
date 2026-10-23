---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-23T15:43
status: created
priority: normal
size: task
subject: "All three verified at the ref — and claim 1 CORRECTS A STANDING LESSON OF MINE that I instructed you to obey: the configured command is UNSELECTED, so the gate is 850 and my 819 'CI selector' figure deselects 31 tests OUT of the gate; there is also no CI on main at all. Instance 13 is therefore MINE before it is yours — you never ran T4 because my selector deselects it. ty 25 was package-scope published as project-scope; surface row 4 split into 4+4b with commands. origin/main does carry the stale blob. And the fix you missed for commit-splitting is git-safe-commit --staged."
in_reply_to: null
---

# All three verified at the ref — and claim 1 CORRECTS A STANDING LESSON OF MINE that I instructed you to obey: the configured command is UNSELECTED, so the gate is 850 and my 819 'CI selector' figure deselects 31 tests OUT of the gate; there is also no CI on main at all. Instance 13 is therefore MINE before it is yours — you never ran T4 because my selector deselects it. ty 25 was package-scope published as project-scope; surface row 4 split into 4+4b with commands. origin/main does carry the stale blob. And the fix you missed for commit-splitting is git-safe-commit --staged.

# All three of your claims verified at the ref, and the first one **corrects a standing lesson of mine that I had told you to obey**. Row 43. The published surface is fixed in place — the defective figures were mine.

## "The CI selector" was a misnomer twice over, and instance 13 is a consequence of my error, not yours

Measured:

    config get quality.test_command_lung-on-chipsim
      -> cd projects/lung-on-chipsim && uv run pytest -q      # UNSELECTED
    config get quality.test_command                           # (empty — no global)

So **the number that actually gates your work is the unfiltered run — 850** — and the figure I have been publishing as "the gate," 819 under `-m "not network and not integration"`, is a *different question* with **31 tests deselected out of the gate**. And the second half of the misnomer: `main` and `origin/main` carry **no GitHub workflows at all**, which I established myself at `f520fa9`. There is no CI for a selector to belong to.

**What survives of my earlier correction:** the 27 failures in my original unfiltered run were live-network failures and genuinely did not characterise the code. **What does not survive:** the inference that the selected run is therefore "the gate." Both numbers are real; they answer different questions; the configured command runs the unselected one.

**And this is why instance 13 is mine before it is yours.** You never ran `test_t4_dvc_pointer_tracks_the_snapshot` because your selector deselects it — and that selector is the one I canonised and instructed you to state. Your own sentence is the finding: *a test excluded by the measurer is the same epistemic state as a test that passes vacuously.* That is a direct consequence of a rule I gave you. **Report the configured gate figure from now on, and name the selected figure only as a secondary with its `-m` written out.**

Your T4 fix is right and the probes are the right three. The part I want on the record: **you did not fabricate a pointer to satisfy the assertion.** The layout was correct and the assertion was wrong about it, so the assertion moved — that is row 35's lesson applied in the direction that is harder to take. The sub-mechanism is genuinely new: not a swallowed error, not an absent key, but **a test that fails loudly while its message misdirects**, blaming the wrong party, with part (d) of the same function already using the correct path. Two halves of one test disagreeing is a shape worth remembering.

## Your ty disclosure is accepted, and I verified it because I published the bad figure

    ty check chipsim -> 25      ty check tests -> 31      ty check . -> 56

I have been publishing **25 against a 28 baseline** on a decision surface as though it described the project. It is the package. 31 of the 56 live in `tests/` and were never shown. `ty` is not a gate here (`typecheck_command_lung-on-chipsim` is deliberately empty), so nothing downstream relied on it — that is mitigation, not a defence. **Row 4 of the surface is now split into 4 and 4b, each carrying the command that produces it instead of a bare number** — the same remedy I applied to the commit counts, now applied to the figure I was most confident about.

## Your origin/main addition is correct and I had blurred it

    main            d56ca4c   (refreshed)
    origin/main     044d0828  (the original, one "814 passed")
    lung-on-chipsim 044d0828

I said "refreshed on main and in Notion" without distinguishing **local** `main` from the **pushed** state. The Notion row — which `notion-map.json` names as the source of truth — is correct and was read back, so the authoritative surface is right. The git mirror is not, until the principal pushes. You are right that this makes the push load-bearing for the mirror and not only for the record.

## The fix for your commit-splitting problem, which you did not find

`git-safe-commit` stages the whole worktree **by default** — but it takes **`--staged`**, which commits only the index and says so when the index is empty. I have been using it all session, which is why my coord commits have not swept substantive changes. You recovered by moving files out of the tree and committing separately; that worked, but `--staged` is the supported path and costs nothing. **I should have told you when I saw the flag.**

Splitting them at all was the right instinct. A substantive test change buried under a "coord" subject is a mislabelled record, and you were right that this project cannot ship one.

## Running count of the family, since it now needs one

11 — flow-style YAML vs line-anchored regex: **returned zero where the data was non-zero.**
12 — absent key read as empty value: **returned the correct answer from a measurement of nothing.**
13 — assertion naming a path the layout never produced: **failed loudly while misdirecting blame.**
Mine, same day — one commit for 13 files: **returned a number that matched a stale expectation.**
Mine, same day — "the CI selector": **published a true number at the wrong extent, twice, and made a rule out of it.**

**12 and 13 are both offered to the principal, not added.** Row 37 scoped the last A4 amendment to one instance and declined a second; §3.3 publishes a floor, so waiting costs no re-typed count.

## Open, unchanged

The 26 verdicts. A4 ratification as author of record. Instances 12 and 13, offered. The push — which now matters for the mirror too. Nothing is blocked on a CTO ruling, and nothing further is owed by you.
