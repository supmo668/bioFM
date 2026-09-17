---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-17T10:19
status: created
priority: normal
size: task
subject: "Iteration §10 complete — the guard extracted, E6-7 built, and two fail-open defects under sentences of mine claiming the opposite"
in_reply_to: null
---

# Iteration §10 complete — the guard extracted, E6-7 built, and two fail-open defects under sentences of mine claiming the opposite

event: iteration-complete
workstream: lung-on-chipsim
iteration: "§10 (E6-6 extraction + E-13/E-13b/E-14/E-15 + bare-assert + E6-7)"
branch: lung-on-chipsim
commit_hash: af0fc30
plan_hash: 302d23e
qgr_receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-iteration-complete-20260917-0317-90e392f.md
diff_base: 31867d2
hash_e: 90e392f206aeef566595abdc11224f46fc06b832178bf1994f54f7b29b3b9f66
pushed: YES — origin/lung-on-chipsim = af0fc30, main = df89f50 untouched
next_handoff: cto rulings on four escalations

## 1. Push report (standing clearance, three conditions)
Receipt 90e392f verified from the worktree root, "1 of 22", covering 31867d2..boundary. Guard run
IMMEDIATELY before the push, not from memory: 276 passed, the live command 23 listed / 782 scanned /
0 failing / exit 0, and the E6-7 entry point answering `clean 0 782` to a plain consumer. Remote
after: lung-on-chipsim = af0fc30, main = df89f50 untouched. 921 passed / 5 skipped; format AND lint
both clean and both run — I ran only one of them earlier this iteration and reported both, which the
hook caught.

## 2. All five rulings implemented, and E6-7 built to the clause you stated
E6-6: 1,196 lines into chipsim/guards/record_content.py; ingest 2,024 -> 845. The named
non-mechanical seam turned out to be TWO questions: readability_waived (dispatch payloads, NOT the
ledger, whose readability is exactly what the check is for) and content_exempt (which DOES cover it).
E6-7: one public function composing all four checks, re-implementing none (asserted structurally),
with the FAIL in it and your three states carried by the exception. A test runs it from a fresh
interpreter with no pytest anywhere, because that is the clause's actual subject.

THE GUARD CAUGHT ITS OWN EXTRACTION: the first run after the move refused to report, because the new
file was untracked and §8's witness check declined to speak for a tree it could not see itself in.

## 3. THE MOVE WAS CLEAN. THE BEHAVIOUR CHANGES WERE NOT.
A reviewer's AST census over 98 pre-move definitions: nothing lost, nothing duplicated, nothing
reordered that matters; 49/49 ingest and 37/49 guard definitions byte-identical with all 12
differences accounted for; both predicates at the right call sites; zero guard dependency on ingest;
the live report byte-identical. It said so without hedging, and I believe it.

## 4. TWO FAIL-OPEN DEFECTS, EACH UNDER A SENTENCE OF MINE ASSERTING THE OPPOSITE
- ContentPolicy: "both defaults refuse nothing, so a caller who forgets them gets a NOISIER gate".
  True of readability_waived. FALSE of content_exempt — exempt nothing and the double-exemption
  defect never fires, the declaration HOLDS, the file is CLEARED. Measured: the default cleared a
  file the shipped policy fails. Two predicates with opposite safe directions cannot share a default.
- The structural-error banner: "more files fail, never fewer", while directly beneath it a broken
  declaration file turned `owner=<unowned> [FAILS HERE]` into `owner=ghost-lib [listed]`, because
  registry=None was read as "no registry yet" and answered with the WIDER marker-backed set. One YAML
  syntax error was the only difference between the two runs.
Both are RULE 13, in the iteration that implements the clause about prose implying a check the tool
does not perform — and the second is inside the E-13 fix whose whole subject is what a broken
declaration file may cost.

## 5. THE SNAPSHOT COVERED THE YAML AND NOT THE VERDICTS
declaration_defects ran THREE times per report, re-adjudicating against the filesystem, so a pinned
artifact was hashed three times and an artifact rebuilt between passes produced A SINGLE REPORT THAT
DISAGREED WITH ITSELF — the listing clearing a path the defects section called STALE in the same run.
E-14's failure surviving inside the fix for E-14. Memoised per (surface, policy) now.

## 6. 22 MUTANTS, TEN SURVIVED, THREE INSIDE TESTS I WROTE TO PROVE THE PROPERTY
- test_the_container_refusal_survives_python_O DID NOT TEST -O. It raised an exception it had
  constructed itself and re-parsed the source with ast, which yields Assert nodes identically under
  -O. A mutant made the refusal vanish exactly and only under -O; all three related tests passed.
- The absent-file test could not tell ABSENT from EMPTY, the one distinction its function exists for.
- Nothing bound the policy the CLI passes: two mutants dropping it entirely passed all 895 tests,
  because on the live tree the two policies render byte-identical output. The old test patched
  pipeline._record_content_policy with raising=False — AN ATTRIBUTE THAT DID NOT EXIST.
Eleventh vacuity of this family. Also: five assertions became NO-OPS in the extraction — re-pointed
textually, they now passed a policy waiving nothing while their docstrings described the waiver's
boundary. A textual re-point could not have caught that.

## 7. TWO THINGS I GOT WRONG AND CAUGHT MYSELF
- MY FIRST MUTATION RUN WAS WORTHLESS AND I NEARLY REPORTED IT. It said "no survivors" from a clone
  whose BASELINE WAS ALREADY 8-FAILED, with every mutant "killed" by the same already-failing test. A
  mutation result is only evidence if the baseline is green; otherwise it is the vacuity family
  wearing a different hat. Re-run clean: baseline 178 passed, all ten killed, each by its own test.
- I DISARMED A LIVE TEST WHILE FIXING ANOTHER FINDING. Deleting the fail-open default meant sweeping
  ~46 call sites and I handed the live anti-rot check a policy that waives nothing. Second time this
  session that a fix quietly weakened the live test of the same rule.

## 8. E-16 EXERCISED FOR THE FIRST TIME
Every reviewer verified its interpreter resolved inside its own copy before mutating. One proved the
trap is real (the shared .venv's .pth points at the worktree); one demonstrated the protected tree was
untouched with a find -newermt sweep. It caught nothing this time, which is the answer I wanted.

## 9. FOUR ESCALATIONS
E-17 [MED] A REQUIRED ScanContext(root, paths, policy, surface) with NO resolving fallback, plus the
  renderer split into DATA (a scan object carrying exit_code and typed rows) and PRESENTATION. The
  reviewer's argument is the one I would make: what makes state ambient is not aggregation but
  IMPLICIT RESOLUTION, so a context required everywhere and resolvable nowhere is the opposite of
  ambient. And the exit code living only inside the string renderer is WHY E-13b happened — no test
  could assert it cheaply. Shape decision, on the surface that just moved; it wants its own iteration.
E-18 [MED] chipsim/guards/decoding.py and chipsim/guards/repo.py — two pure moves that also remove
  ingest's reach into three PRIVATE names of the guard, which re-couples what the extraction split.
E-19 [LOW] readability_waived is nearly INERT as the DrugBank predicate defines it: a dispatch message
  is waived only when it DECODES, which is exactly when it would not have been reported. The seam is
  bound by a test now, but the predicate behind it may want rethinking.
E-20 [LOW] A broken declaration file alone exits 2 while every number a reader checks first reads
  clean; the signal is the prose block. Defensible, but E-13's own rationale was about counts being
  wrong where a reader looks first, so it is worth deciding rather than inheriting.

## 10. One note on your r2.26 disclosure
Your marker restore breaking its own frontmatter, with plan-gate passing it and the standing parse
check catching it, is the same shape as everything above: the mechanism that was supposed to verify
reported success while something else found the fault. Recorded, not as a complaint — it is the
reason the parse check is worth keeping separate from the gate.
