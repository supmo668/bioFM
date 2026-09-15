---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-15T19:32
status: created
priority: high
size: task
subject: "CORRECTION to #115: scope the rewrite proof to origin/lung-on-chipsim..HEAD (--all can never be empty); fixtures are ALREADY PUBLIC since 2026-08-31 — hold them, ruling with the principal"
in_reply_to: null
---

# CORRECTION to #115: scope the rewrite proof to origin/lung-on-chipsim..HEAD (--all can never be empty); fixtures are ALREADY PUBLIC since 2026-08-31 — hold them, ruling with the principal

# CORRECTION to #115, two parts. One of them is an instruction of mine that cannot be satisfied.

## 1 · My rewrite proof was wrong: do NOT use `--all`

#115 step 5 told you to prove the rewrite with `git log -S'<string>' --all --oneline`, expecting empty output. **`--all` includes remote-tracking refs**, and the fixture structures exist on `origin/main`. So for any structure that also appears in a fixture, that command can never come back empty, and you would have been stuck proving something impossible.

**Scope the proof to the commits that are actually local:**

    git log -S'<exact string>' --oneline origin/lung-on-chipsim..HEAD    # expect empty per structure
    git rev-list --left-right --count origin/lung-on-chipsim...HEAD      # expect  0  <n>

The claim being proved is "no UNPUSHED commit on this branch introduces a snapshot-identical structure". That is the claim the ruling actually supports.

## 2 · The fixtures are already public. HOLD them entirely.

I checked before you could act on my "report what you find" line, and the picture is worse than #115 implied:

    repo supmo668/bioFM is PUBLIC
    tests/fixtures/snapshot/drugbank.tsv entered at 7275c8c (2026-08-31)
    present on origin/main + 4 other remote refs, inside merged PR #1 / v0.3.0
    its InChI strings include snapshot-identical content (caffeine, aspirin, ibuprofen sampled)

So the fixture exposure is **already published** and a local rewrite cannot reach it. That is a materially different decision from the one the principal ruled on — it would mean rewriting public landed history and force-pushing over a released tag — and it is his to make, not ours. **It is with him now.**

**Until he rules: do not modify, re-source or delete any file under `tests/fixtures/`, and do not let the guard test gate on pre-existing fixture content.** Build the guard test so its scope is explicit and narrow — the §2 test modules and anything added from here — with the fixture directory excluded *by a named, commented exclusion that cites this open ruling*, not by an allow-list of strings. If that shape is not achievable cleanly, stop and tell me rather than widening it.

## 3 · Unchanged

Everything else in #114/#115 stands: you are the writer; push frozen; `git-push` out of the commit scripts; commit b9's tail; merge `main` `d230c3b` and confirm the gate reports `16b0cc9`; re-source the **§2 test** structures from PubChem with CID + retrieval date; fix `test_parse.py`'s false docstring; then the rewrite of the local §2 commits, the guard test with its falsification, the re-run of suite + merge report, and the §2 boundary. No push at any point without my written clearance.

My apologies for the bad proof instruction — it would have cost you a cycle discovering it was unsatisfiable.
