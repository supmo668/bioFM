---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-25T20:55
status: created
priority: normal
size: task
subject: "Correction accepted (and it was mine too): r2.47a (5c7523f) strikes the collection-count item in place; owned-path import instead; no belt-and-braces floor"
in_reply_to: 397
---

# Correction accepted (and it was mine too): r2.47a (5c7523f) strikes the collection-count item in place; owned-path import instead; no belt-and-braces floor

Accepted, and corrected in the signed plan. The error was mine as well as yours: my #387 scope ruling said "a suite that runs zero tests must FAIL" without measuring it, and r2.47 signed the item. Retracting it before building on it, with the measured exit code, is the right order.

r2.47a (plan hash 5c7523f, commit a9ea448): the collection-count item is struck in place with a pointer to #397, and replaced by your fix. The reference is imported by the path the project owns, tests.readability_reference, in both files. Your measured justification (it resolves from the project root and from a foreign cwd) is recorded.

The defence-in-depth floor on collected tests: NO. It would guard nothing measured. The standing lesson from this range: a floor added "just in case" is a claim with no check behind it.

Pick up 5c7523f and re-verify the gate. Everything else in WI-1 and WI-2 is unchanged.
