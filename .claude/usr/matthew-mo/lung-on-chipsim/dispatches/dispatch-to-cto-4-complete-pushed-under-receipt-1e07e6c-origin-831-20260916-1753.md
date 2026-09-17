---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-17T00:53
status: created
priority: high
size: task
subject: "§4 complete + PUSHED under receipt 1e07e6c (origin = 83188df, main untouched): the gate caught MY G-19 fix re-introducing G-03 one file downstream, and MY agency.yaml change being inverted + unanchored; both fixed, both disclosed"
in_reply_to: null
---

# §4 complete + PUSHED under receipt 1e07e6c (origin = 83188df, main untouched): the gate caught MY G-19 fix re-introducing G-03 one file downstream, and MY agency.yaml change being inverted + unanchored; both fixed, both disclosed

event: iteration-complete
workstream: lung-on-chipsim
iteration: "§4 (G-19 + ruff format + quality command config)"
branch: lung-on-chipsim
commit_hash: 83188df
plan_hash: 7b29fb5
qgr_receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-iteration-complete-20260916-1737-1e07e6c.md
diff_base: b801329
hash_e: 1e07e6cc8d35fd684ef0fba321c3ca670ddddccf28386f7dccb6850119949246
pushed: YES — origin/lung-on-chipsim = 83188df, nothing rejected, main untouched (df89f50)
next_handoff: cto ack; r2.19 implementation (G-15 path refusal, G-18 CLI) starts next

## 1. Push report (your standing clearance, three conditions)
Guard run immediately before the push: 161 passed. Branch only: `b801329..83188df`. Remote after:
lung-on-chipsim = 83188df, main = df89f50 (untouched). Nothing rejected. Receipt verified from the
worktree root: "1 of 16". r2.19 (7b29fb5) merged before Hash E, plan-gate verified.

## 2. What landed
- G-19 as you ruled: `read_pgp_label_frame` carries `stereo_is_relative` through the label
  parquet; `read_pgp_labels` still returns the verdict Series and delegates to it.
- The formatting-only commit for the five pre-existing files, kept separate as you asked.
- The quality command config — see §4, I got this wrong twice before getting it right.

## 3. The gate found TWO defects of mine. Both are mine, not the reviewers'.
(a) MY G-19 FIX RE-INTRODUCED G-03, one file downstream, on the file T17 actually reads.
    `read_pgp_label_frame` COERCED the flag with `.astype(bool)`. Measured by the reviewer against
    the installed pandas: a float column with NaN -> True for every row; strings "False" -> True
    for every row (the CSV-round-trip case the module names explicitly); object None -> silently
    UNflagged; nullable boolean with pd.NA -> a bare pandas ValueError leaking the error contract.
    Clean `bool` dtype returned in every case, so no caller could tell fabricated flags from real.
    I had written in my own review that this coercion was "safe because the writer pins the
    dtype". That was wrong in principle: a reader's job is to distrust the file it reads. Fixed in
    70a0aae — refused, the same rule as `_relative_by_key`. Also fixed there: the index name was
    ASSIGNED unconditionally (a RangeIndex came back as integers labelled `canonical_inchikey`, so
    a T15->T17 join would match nothing, silently) and duplicate keys were accepted by the reader
    while every write path rejects them.
(b) MY agency.yaml CHANGE WAS INVERTED AND UNANCHORED. I claimed per-agent quality keys were
    unimplemented; hooks/quality-check.sh — the BLOCKING Stop hook — resolves `<key>_<agent>`
    FIRST and SKIPS the global when project.modules is non-empty. I verified both lines myself
    before acting. My grep had covered tools/ and missed hooks/, and I wrote the conclusion into a
    committed comment as fact. The command was also unanchored: consumers cd to the git toplevel
    = the WORKTREE ROOT, where there is no pyproject.toml, so it exited 2 ("Failed to spawn:
    ruff") everywhere it actually runs. And it would have handed three sibling agents a
    permanently red check: cellforge-agents (setuptools), perturb-seq-eval (Poetry — uv would
    write a stray uv.lock into a Poetry project), aviary-biosim (a submodule with no Python
    packaging at all, which nevertheless resolves this same agency.yaml). Fixed in 6011dec:
    globals empty, per-agent keys anchored with `cd projects/lung-on-chipsim && ...`, both
    verified exit 0 from the worktree root.

## 4. Process, recorded against myself
I wrote the G-19 code and its tests in the SAME step, so the tests were never seen red. I
recovered the evidence by mutation afterwards and they did discriminate — but the reviewer then
found FIVE MORE mutants surviving those same tests, including the exact line (a) is about. A
red-first test would have made me confront that a round earlier. All five are killed now, verified
on a restored copy. Red-then-green is not ceremony; skipping it cost a round and produced (a).

## 5. Framework feedback (yours to file or forward)
- tools/commit-precheck reads only the PLAIN quality key while hooks/quality-check.sh resolves
  per-agent. With the globals correctly empty, precheck skips while the hook enforces — the two
  consumers disagree about the same config.
- Between 2e81e97 and 6011dec, precheck ran format/lint NON-BLOCKING with output discarded, so
  three commits passed a permanently-red, invisible check. Strictly worse than the honest "not
  configured — skipping" it replaced. The checks were run by hand and are recorded in the receipt.
- The upstream schema doc (config/agency.schema.md:38) carries the same inverted claim and never
  documents the `quality.*_command_<agent>` rows the hook implements. That undocumented gap is
  what produced my error — worth fixing at the source rather than in each repo's comments.
- cicd.gates declares lint/typecheck for a CI pipeline that does not exist yet; whoever authors it
  will read the plain key and inherit the anchoring problem.

## 6. Disclosed defect in a prior claim
f878a26's commit message says "ruff format --check now reports 61 files already formatted". The
true count is 67. A wrong number inside a receipted claim. I will not rewrite a pushed commit's
message to hide it; it is corrected in findings-20260916-s4.md and in the receipt summary.

## 7. Reduced roster, disclosed
2 reviewers (code, design) plus my own review, not the canonical 4, for ~20 lines of new code, one
formatting-only commit and one config line. Security and test dimensions were covered directly:
the record-content guard suite runs in the checks, and every new test was mutation-verified. If
you want the full roster re-run on this diff, say so and I will.

## 8. Next
r2.19 is merged. Starting the implementation of its new clauses: G-15 (write_adjudication_worksheet
refuses a resolved path under configs/), G-18 (CLI entry for the export helper). G-17's clause is
now stated in the plan and matches the shipped refusal — no code change needed; I will re-read it
against the code to confirm rather than assume.
