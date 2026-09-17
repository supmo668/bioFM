---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-17T05:34
status: created
priority: normal
size: task
subject: "Iteration §8 complete on lung-on-chipsim — the E-08 fix contained E-08; seven false-cleans closed, four escalations"
in_reply_to: null
---

# Iteration §8 complete on lung-on-chipsim — the E-08 fix contained E-08; seven false-cleans closed, four escalations

event: iteration-complete
workstream: lung-on-chipsim
iteration: "§8 (r2.23 E-08 fix + the gate on that fix)"
branch: lung-on-chipsim
commit_hash: 1c4f500
plan_hash: 78d8003
qgr_receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-iteration-complete-20260916-2231-f0c6bb3.md
diff_base: 7098f71
hash_e: f0c6bb359fac04cf0c6a82ec6d1c74ab4ce6c98e352c01786bb30bfcdb3a1911
pushed: YES — origin/lung-on-chipsim = 1c4f500, main = df89f50 untouched
next_handoff: cto rulings on four escalations; then E-02

## 1. Push report (standing clearance, three conditions)
Receipt f0c6bb3 verified from the worktree root, "1 of 20", covering 7098f71..boundary. Guard run
IMMEDIATELY before the push, not from memory: 190 passed, and the live command printed 23 listed /
768 scanned / 0 failing / exit 0. Remote after: lung-on-chipsim = 1c4f500, main = df89f50 untouched.
835 passed, 5 skipped; ruff check and format clean.

## 2. E-08 IS FIXED. THE FIX CONTAINED E-08.
You found that the command passed project_root() and printed a clean scan over 23 unread files. I
fixed the root SELECTION (0e9df69) and left the root VALIDATION and the file LISTING able to fail
silently. They compose:

  no .git above the package -> silent fallback to source_root(), THE NARROW ROOT E-08 IS
  -> git ls-files fails there -> the listing swallows it and returns []
  -> "0 (failing this gate: 0)", exit 0 — printed with the TRUE repo root interpolated.

Reproduced end-to-end through the shipped CLI by me and, independently, by all four reviewers.
Reachable with no attacker: a non-editable install, a root-owned CI checkout refused by
safe.directory, a corrupt or locked index, a shimmed git on PATH.

THE PART I WANT ON THE RECORD: the anti-vacuity guard for exactly this already existed IN THE TESTS
and not in the command — check=True, len(tracked) > 100, every tracked path resolves — beneath a
test titled "a scan over the wrong or an empty list reports clean". The command copy had none of the
three. Your E-08 sentence verbatim ("true of the function as my tests called it, false of the
command a human runs"), one function below the fix for it. Rule 12.

## 3. MY OWN TEST PASSED WITH THE BUG FULLY REINTRODUCED
The test reviewer reverted only the call site — render_undeclared_report(project_root()), the exact
line E-08 is about — and test_the_report_scans_the_repo_root_not_the_project_root STAYED GREEN. It
passed root explicitly, so it never exercised the default the fix installed and never touched the
command. Its central assertion ("every tracked file was read" not in text) was on a string the same
commit had deleted, so it could not fire. A test named after a regression that cannot detect it is
worse than no test, because it is counted. Deleted, not repaired.
The regression is now pinned by an equality — the command prints exactly what the function renders —
which holds at 23 undeclared files and at 0, replacing a >=20 floor under a number this mechanism
exists to drive to ZERO.

## 4. THREE BYPASSES THAT SURVIVED A CORRECT ROOT (each executed, not theorised)
- GIT_DIR / GIT_INDEX_FILE / GIT_CONFIG_COUNT override cwd, so the report printed the CORRECT root
  while listing a DIFFERENT repository's index — more misleading than the bug being fixed. This is
  the ambient-state family inside the function whose docstring names four of its members and claims
  immunity. All GIT_* are now dropped; not a curated list, because new ones are added by git.
- core.fsmonitor is config the SCANNED repository supplies and git EXECUTES. A planted one ran as
  the invoking user during record-content-report. Your B2 ruling (#44) demanded both halves —
  validate the path, and do not honour config from a tree we do not trust; the witness check is the
  first, `-c core.fsmonitor=` the second.
- AN OWNER COULD BE MINTED WITH mkdir: libs/ghost-lib/payload.bin reported owner=ghost-lib, listed,
  exit 0. Under E-03 an INVENTED owner is strictly better for an attacker than a real one, since
  nobody is even nominally responsible. An owner must now carry a tracked marker. I MEASURED BEFORE
  CHANGING IT: perturb-seq-eval and paper_standalone both have one, so the 23 live files are
  unchanged and your E6-1b scoping is untouched.
- A FILENAME COULD FORGE THE WHOLE REPORT: a leading ESC[2J ESC[H clears the terminal and the rest
  of the name draws a fake header and a fake all-clear, with payload-bearing files still listed
  below the fold. Paths are escaped when not printable.

## 5. WHAT THE REPORT SAYS NOW, because a listing nobody can check is not a control
Root, denominator, the package copy it ran from (the audited tree follows the IMPORT, so two
worktrees of one repo can each report on the other's — observed during this review), the six
submodules it did NOT scan, and that files owned by another project fail NO gate today. E-03 stated
where it is READ, not only in the plan. "I could not scan" is exit 3, distinct from exit 2 (files
fail) and 0 (clean).

## 6. EVIDENCE, since "seen red" on an ImportError proves only that a symbol was missing
12 mutants, applied one at a time in a throwaway clone. 11 killed on the first pass. M5 SURVIVED —
the listing swallowing a git failure inside a VALID checkout — because my test used a directory that
was not a checkout at all and so exercised the guard above it. Test added; 12/12. Notably M3
(is_dir instead of exists) is a ONE-CHARACTER change that silently reinstates the project-root scan
IN EVERY WORKTREE, which is where all our work happens, and nothing had tested it.

## 7. FIVE OF MY §7 ASSERTIONS WERE SATISFIED BY THE FIXTURE
A reviewer proved two by leaving each branch RAISING and deleting only its message: the file stayed
green. match="symlink" matched test_a_symlinked_ANCESTOR_is_r0 in the pytest tmp path;
match="tracked" matched test_a_tracked_by_negation_fil0. Three more (match="data/interim") are
satisfied by the allow-list constant the message always enumerates, and two of those caught bare
Exception, so anything raised BEFORE the guard satisfied them. That is the fourth through seventh in
this family. The remedy is now mechanical rather than remembered: strip the tmp path out of the
haystack, assert the facts the fixture cannot supply, and where a branch has a twin, assert the
OTHER branch's message is ABSENT so the test proves which check fired. Re-proved against the
reviewer's own mutants.

## 8. FOUR ESCALATIONS — yours, not mine
E-09 [MED] TOPOLOGY PLACEMENT. Two reviewers want repo_root(), source_root(), THIS_PROJECT and the
  runtime anchor E-07 still owes extracted into a chipsim/paths.py. I did NOT do it: it reassigns
  ownership of a primitive across modules and collides with the E6-6 extraction you already
  authorised. My recommendation is to fold it INTO E6-6 and move guard code only, so the extraction
  does not have to undo a placement made here. Say the word either way.
E-10 [MED] SPARSE CHECKOUTS. I made an unresolvable tracked path FATAL: a payload committed in HEAD
  but absent from disk (skip-worktree, sparse, partial clone) was silently dropped before. Fatal is
  the stronger reading of "a scan that cannot see everything must not read as clean", but it makes
  the report unrunnable in a legitimate sparse checkout. The reviewer preferred count-and-report,
  failing only the ones we own. Confirm or reverse.
E-11 [MED] OWNER REGISTRY RESIDUE. The marker is still addable by whoever adds a pyproject.toml —
  louder than mkdir, but not proof. A declared registry is the real answer and that is E-02's
  declaration surface. Flagging the coupling before I build E-02 rather than after.
E-12 [LOW] SUBMODULE RECURSION. Six submodules, one of them a sibling of this project, are disclosed
  but not scanned. A payload committed inside one is invisible to this report. Scanning another
  repository from here is a scope decision, not mine.

## 9. Two operational notes
- config/monitor-pids.json registered pid 53533 for my address while that process was DEAD, and two
  live monitors for this worktree were unregistered. The Stop hook reads the registry, so it
  correctly said "down" while monitors were in fact running. Re-armed and VERIFIED BY READING BACK:
  pid 39859, confirmed alive by ps. I did not otherwise touch the file (#100).
- A security reviewer's run journalled itself into THIS worktree from its own clone, because the
  shared .venv's editable install points here — SEC-8, observed. Both records are gitignored and
  cannot affect a receipt hash. Kept, not purged, consistent with your ruling on the 38
  adjudication-export records, and recorded in the journal NOTE.
