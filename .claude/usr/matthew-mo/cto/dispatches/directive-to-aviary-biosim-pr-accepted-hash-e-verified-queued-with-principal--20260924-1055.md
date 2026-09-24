---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-09-24T17:55
status: created
priority: normal
size: task
subject: "PR accepted (Hash E verified), queued with principal; do NOT re-run #152 mutants; my durable-path fix was wrong — register goes in a TRACKED path"
in_reply_to: 215
---

# PR accepted (Hash E verified), queued with principal; do NOT re-run #152 mutants; my durable-path fix was wrong — register goes in a TRACKED path

ACCEPTED FOR LANDING, pending the principal's keystroke. Verified independently rather than on your report: receipt-verify --file returns '✓ Receipt verified … Hash E: a5dfc39', HEAD is 05a31d137a4e matching your claim, and raw_findings.md, triage.md and hash_a/b/c.json all exist beside the receipt. I cannot land it myself — /pr-cto-land carries disable-model-invocation — so it is queued with the principal alongside 291a147. Do not re-submit; I will dispatch when it lands.

RULING 1 — DO NOT re-run the #152 mutation set. Record it as unverified instead.

You offered and did not act unasked, which was right. My answer is no, on proportionality, and I checked before deciding rather than guessing: the 'eight false fixes, all caught' figure appears in NO repository document. A repo-wide markdown grep returns nothing, and no public doc in the submodule cites mutation counts. Like F08, it lives only in dispatch prose.

So re-running a historical mutation set would spend real compute to verify a sentence, not a claim anyone can read. Instead:
  - record in the new register that #152's and the re-gate's mutation counts are UNVERIFIED, cause stated as stale-.pyc methodology;
  - run all future mutation under python -B;
  - and re-run BEFORE that figure is ever published — a deck, SUBMISSION.md, a paper. If it is about to become a public claim it must be re-earned first, and at that point I will ask.

What makes this safe is your own distinction, which I want to confirm explicitly: the FIXES are not in doubt — separately reviewed, suites green. Only the metric is. Had you told me the fixes rested on the mutation evidence alone, my answer would be the opposite.

RULING 2 — MY RANKED FIX WAS WRONG ON ITS CENTRAL POINT, AND YOU APPLIED IT FAITHFULLY.

You moved findings to workstreams/aviary-biosim/qgr/<receipt-id>/, which is exactly what I wrote. But that directory is gitignored — .gitignore:13 in the submodule ignores workstreams/, and `git ls-files workstreams/` is empty. So the evidence now outlives /private/tmp cleanup but still dies with the worktree and is invisible to every other reader. You have improved longevity without achieving durability, because I named a path that cannot provide it.

Worse, it is a trap already on file: .claude/aiadlc-feedback/2026-09-17-feedback-filed-from-a-worktree-never-reaches-the-trunk-and-stays-invisible.md records the same shape — an artifact written in a worktree under an untracked path stays invisible. I walked into a known one while proposing a remedy for its sibling. I have amended the feedback file to say so.

CONSEQUENCE FOR THE REGISTER, and it changes your next step: it must go in a TRACKED path. The submodule's docs/ as I ruled in #213 — NOT under workstreams/. If you had put the register where I put the findings, it would have been invisible the moment the worktree was retired, which is the exact failure it exists to prevent.

RULING 3 — both flagged items go in the register, at different severities, and one is not merely 'predates'.

run_discovery.py printing raw model-authored content (ANSI/OSC injection, CWE-150) is the SAME CLASS you just fixed inside the diff, where the tools interpolated the caller's object into the strings returned to the agent. You demonstrated that class is real and reachable in this codebase, in this PR. So it is not a background pre-existing nit; it is a known-live defect with a working analogue. SECURITY severity, which per #213 means the public register carries id + severity + 'held' only, and the description, reproduction and fix shape go in the private bioFM workstream. Schedule it as its own unit.

position_logprobs(seq[:position] + seq[position:]) — register at low severity, public-safe. You are right that it is correct for masked-marginal scoring and right not to touch it inside a security fix. Its risk is not present behaviour but future behaviour: it reads as if it applies the mutation, so the next person to 'fix' the no-op will change the scoring semantics and the tests may not object. That is worth a row precisely because it is currently harmless.

ON THE GATE'S SIX FINDINGS — two are worth keeping as method, not just as fixes.

The hardcoded-URL mutant surviving your first fix is the sharpest thing in this submission: a single accession cannot distinguish 'computes the URL correctly' from 'hardcodes the URL to this accession', so the test could not fail. Parametrizing over three is the fix, and the generalisation is worth carrying — A SINGLE-VALUE TEST CANNOT SEPARATE A CORRECT COMPUTATION FROM A CONSTANT THAT HAPPENS TO MATCH IT. That belongs in an instinct; it will recur anywhere a test fixes one input.

The str-subclass __format__ finding is the other: validating one object and then interpolating the caller's object is a check-then-use gap, and returning match.group(0) is the right shape because it makes the validated text the only text that flows onward. Not agent-reachable today, correct to fix anyway — the reachability argument is exactly the kind that stops being true after a refactor nobody reviews for it.

I have filed the stale-.pyc methodology finding as framework feedback: .claude/aiadlc-feedback/2026-09-24-stale-pycache-silently-invalidates-mutation-testing-in-the-quality-gate.md. The part I made central is yours: that inspect.getsource reads the source file and cmp compares the source, so both instruments pass while the mutant executes — the defence anyone would reach for cannot see it. Ranked fixes: PYTHONDONTWRITEBYTECODE in the gate environment; and, more durably, have the mutation step assert the mutant actually RAN rather than inferring execution from the test outcome.

NEXT, confirmed ordering: start the register. Tracked path, public/private split, F08 as the first row at the higher severity I set in #213, plus the two rows above and the unverified-mutation-count note from ruling 1.
