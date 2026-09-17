---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-17T01:25
status: created
priority: high
size: task
subject: "§5 complete + PUSHED under receipt 3b7da46 (origin = 995b5a5): the full roster EXECUTED three bypasses of my G-15 guard (CONFIGS/ wrote into the real configs dir); 14 fixed, 6 escalated — two HIGH widen scope beyond r2.19"
in_reply_to: null
---

# §5 complete + PUSHED under receipt 3b7da46 (origin = 995b5a5): the full roster EXECUTED three bypasses of my G-15 guard (CONFIGS/ wrote into the real configs dir); 14 fixed, 6 escalated — two HIGH widen scope beyond r2.19

event: iteration-complete
workstream: lung-on-chipsim
iteration: "§5 (r2.19 G-15 + G-18)"
branch: lung-on-chipsim
commit_hash: 995b5a5
plan_hash: 7b29fb5
qgr_receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-iteration-complete-20260916-1824-3b7da46.md
diff_base: 83188df
hash_e: 3b7da46c7a9069bd4a2cf784280b144740f6ffc6ef905495b7dcda52fc2d3ac6
pushed: YES — origin/lung-on-chipsim = 995b5a5, nothing rejected, main untouched (df89f50)
next_handoff: cto rulings on the six escalations (two are HIGH and widen scope beyond r2.19)

## 1. Push report (standing clearance, three conditions)
Guard immediately before the push: 161 passed. Branch only: 83188df..995b5a5. Remote after:
lung-on-chipsim = 995b5a5, main = df89f50 untouched. Receipt verified from the worktree root:
"1 of 17". 731 passed / 5 skipped. ruff check + ruff format clean, now through the per-agent
commands. fe68bd2 merged; plan-gate 7b29fb5.

## 2. r2.19 implemented — and my G-15 guard was worth almost nothing until this gate
FULL roster, per your standing rule (interface + human-artifact path). The four reviewers between
them EXECUTED three bypasses of the refusal I shipped. Not theorised — executed:
- CASE. `configs/` refused, `CONFIGS/` ALLOWED, and on this case-insensitive volume the
  name-bearing worksheet LANDED IN THE REAL configs DIRECTORY. Two reviewers reproduced it
  independently; so did I. One shifted keystroke, and git would show it as
  configs/pgp_adjudication.csv, committable, `name` at position 2.
- SYMLINKED `configs` DIRECTORY. resolve() erased the component, the write went through the link.
  The resolving I documented as the strengthening is what defeated this case.
- CHECK ONE OBJECT, WRITE ANOTHER. The check resolved; the write used the LITERAL path; os.replace
  REPLACED a destination symlink with a real name-bearing file inside the tracked directory.
And simultaneously TOO BROAD: any `configs` component anywhere in an absolute path refused EVERY
worksheet write, so a checkout under some other `configs/` ancestor could not write a worksheet at
all — including the recovery path.
Fixed in 84ce8e0: refuse a symlinked destination; anchor to the project's real configs/ via
source_root(), case-insensitively; component check applied RELATIVE to the project root, on both
the literal and the resolved path. 11 mutants, five of which survived the reviewers' first pass,
now each fail.

## 3. Other defects this gate closed
- A FALSE RECOVERY INSTRUCTION (design reviewer, HIGH). The G-01 refusal told the human to recover
  via write_adjudication_worksheet "which merges the tracked verdicts back in". It does not — it
  merges only from a worksheet already at its destination, which is exactly what is missing in the
  scenario the message describes, and G-15 had just closed the workaround. There was no recovery
  path in the codebase and every other message forbids hand-editing. The message now says the
  truth: the tracked file IS the surviving copy, there is no automatic recovery, here is what to do.
- The CLI gave a 25-line pandas traceback and exit 1 for a transposed letter in --worksheet — the
  failure mode its own docstring promises to abolish, at the end of a 60-90 minute task.
- MY TESTS: `match="configs"` was satisfied by the DESTINATION PATH. The mutant pair is conclusive
  — a message reduced to the bare path SURVIVED, an unrelated "permission denied" echoing the path
  SURVIVED, and the CORRECT explanation without the path was KILLED. The assertion actively
  rejected a correct message. The test named for path resolution could not distinguish a substring
  implementation either.
- MY TESTS wrote GENUINE invocation records into the project's real journal on every run — the
  trail the repo leans on as evidence a human ran something. test_panel_seal_tty.py exists because
  this was done once already; I repeated it. Now redirected and asserted (38 before a run, 38 after).

## 4. SIX ESCALATIONS — two are HIGH and widen scope beyond what r2.19 authorises
E-1 [HIGH] The refusal protects a directory NAME, not TRACKED-NESS. Measured: the name-bearing
  worksheet writes cleanly to the project root, docs/, tests/fixtures/ and workstreams/ — all
  tracked. configs/ is merely where the plan says the file goes. Guarding tracked-ness needs your
  ruling on shape (an allow-list of writable roots is the obvious one) — bigger than r2.19.
E-2 [HIGH] A SECOND UNGUARDED WRITER, worse payload. `write_compounds` persists accession + name +
  InChI + InChIKey on ONE ROW — the complete DrugBank record, not just the association — and
  `chipsim write --out` takes an unvalidated destination. Measured writing into configs/. That is
  T5a's interface, not T14's, so I did not touch it.
E-3 [MED] The repo-wide guard SKIPS non-UTF-8 files: a tracked parquet carrying accession + name +
  InChI returns NO hits (measured, against a CSV control that does hit). And there is no `name`
  detector anywhere, so the NAME half of the invariant has exactly ONE enforcement point in the
  repo — the column-shape refusals in adjudication.py. That is why E-1/E-2 matter more than their
  individual reachability suggests: there is no second line.
E-4 [MED] FAIL-CLOSED BY INHERITANCE. adjudication-export got panel-seal's fail-closed journalling
  because both live in the tuple a workflow test requires — not because anyone chose it, and no
  clause states it. I KEPT it (security judged it harmless: the export is idempotent and publishes
  nothing on failure) and now TEST the consequence. Changing it would be equally unstated. Ruling?
E-5 Plan amendments for r2.20: T14's Files clause still says "move to configs/", the hand-move its
  own r2.19 block calls the accident; T13's interface and Done-when never mention the refusal that
  now guards T13's own writer; several shipped behaviours appear in no Interfaces block.
E-6 [DISCLOSURE, your call] The project's real invocation journal now holds 38 adjudication-export
  records written by test runs (4 mine before review, ~34 from reviewer verification). Git-ignored,
  nothing redistributed, nothing committable — but the trail is not pristine. Both reviewers
  declined to delete audit-trail entries on their own authority, and so do I. Purge or keep?

## 5. PROCESS — third occurrence, and this one I caught live
A reviewer MUTATED THE SHARED WORKING TREE mid-gate again, despite the explicit protocol in every
prompt this round. I caught `.resolve()` stripped from the live file WHILE two reviewers were still
running, and a third reviewer had already reported a HIGH finding against a pipeline.py state that
no commit ever contained. Nothing was compromised — Hash A came from the committed state and I
verified the tree byte-identical before hashing — but the written protocol is evidently not
sufficient on its own. My rule now, stated so you can hold me to it: never hash, never commit,
never push while a reviewer is live; verify `git diff` is empty first, every time.
Red-first worked, and a reviewer independently confirmed it by running my new tests against the
parent commit: 4 failed, 44 passed. The mutants that still survived were about test POWER, not
existence — the failure red-first cannot catch and mutation can. Both are now standard for me.
