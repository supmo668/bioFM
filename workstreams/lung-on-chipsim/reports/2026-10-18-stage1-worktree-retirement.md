# Stage 1 worktree retirement + Stage 2 resume — record for review

**Date:** 2026-10-18
**Author:** biofm/matthew-mo/cto
**Status:** **§4 DEFERRED BY PRINCIPAL DIRECTION (2026-10-18) — "approve stage1 first so worktree stays
at lung-on-chipsim."** Nothing in §4 has been executed, and it must not run until Stage 1 is closed.
The Stage 1 worktree **STAYS** in place meanwhile. The sequencing is the principal's and it is the safer
one: A4 is drafted *from* the Stage 1 record, and retiring the tree that holds that record before the
deliverable is ratified would put the source and the draft on opposite sides of a destructive step.
**Blocking item:** ruling A4 (row 65) — draft now at `../paper/stage1-methods-note.md`, awaiting the
author of record. When A4 is ratified, re-verify §2 (the measurements will be stale) and then run §4.
**Defect being resolved:** the lung-on-chipsim agent was working from the **Stage 1** worktree
(`worktrees/lung-on-chipsim`, branch `lung-on-chipsim` @ `f66fbf7`) while its directives (#608, #622)
describe work in the **Stage 2** worktree (`worktrees/lung-on-chipsim-stage2`, branch
`lung-on-chipsim-stage2` @ `c781e9c`).

---

## 1. Two corrections to what I previously told the principal

**(a) The live session is gone.** I reported pid 13641 as a live session parked at a prompt (last
measured 14h13m, state `S+`). It has since **exited**. There is no session to type into and nothing
to kill. The "interact with it or close it" decision is moot.

**(b) `pgp_adjudication.csv` contains NO human work.** I have been calling it "the only
critical-path human input" and warning about "a single-point loss of the only human input." That
overstated it. Measured, without printing any identifier value:

| property | value |
|---|---|
| path (only copy on this machine) | `worktrees/lung-on-chipsim/projects/lung-on-chipsim/data/interim/pgp_adjudication.csv` |
| size / rows | 1943 bytes / 27 lines = header + **26 data rows** |
| sha256 | `679b017221d7ccfd0a62f8e0071402f8e0ce03ad666f880460bc9b32aabe9fe1` |
| mtime | 2026-09-22 21:32 |
| `adjudicated_label` filled | **0 / 26** |
| `evidence_doi` filled | **0 / 26** |
| `adjudicated_by` filled | **0 / 26** |

It is a **blank 26-row scaffold**, regenerable by `write_adjudication_worksheet`
(`chipsim/harmonize/adjudication.py:204`). So today its loss costs a regeneration, not human work.

**This does not retire the protection decision — it re-dates it.** The file becomes irreplaceable the
moment a verdict is typed into it, and at that point there is still:
no git tracking (`projects/lung-on-chipsim/.gitignore:16` → `data/interim/**`), **no `.dvc` file**
(unlike `data/raw/drugbank/*.tsv.dvc`), and **no tracked export yet** (`git ls-files | grep adjudicat`
returns only the `.py`). The code anticipates exactly this loss at `adjudication.py:409-421`:

> "most often the interim worksheet was regenerated empty after `data/interim/` was lost. The tracked
> file at {out} IS the surviving copy of that work: keep it. **There is no automatic recovery** …"

That tracked file does not exist yet. **Protect the file before verdicts are entered, not after.**

---

## 2. Measured state

| item | state |
|---|---|
| lung session pid 13641 | **GONE** (exited) |
| `worktrees/lung-on-chipsim` | branch `lung-on-chipsim` @ `f66fbf7`; tracked tree **clean** |
| — its one untracked tracked-tree file | `workstreams/lung-on-chipsim/qgr/evidence/scan-artifacts-f66fbf7.json` |
| `worktrees/lung-on-chipsim-stage2` | branch `lung-on-chipsim-stage2` @ `c781e9c`; **clean** |
| Stage 2 `data/interim/` | contains **only `.gitkeep`** — the worksheet is NOT there |
| Stage 2 missing | `projects/lung-on-chipsim/.venv`, `projects/lung-on-chipsim/.dvc/config.local`, `.claude/usr/matthew-mo/lung-on-chipsim/lung-on-chipsim-handoff.md` |
| **`f66fbf7` ancestor of `c781e9c`?** | **NO** |
| Stage 1 archive bundle | `~/bioFM-archives/lung-on-chipsim-stage1-f66fbf7-20261013.bundle`, 48,746,994 bytes, single disk copy |

### The ancestry result is the load-bearing one

`f66fbf7` is **not** reachable from the Stage 2 branch. Deleting branch `lung-on-chipsim` would make
the entire Stage 1 history unreachable in this repo, leaving the **one** bundle on **one** disk as the
only copy. **Therefore: remove the worktree, keep the branch.** This record does not delete it.

---

## 3. What is preserved vs destroyed

**Preserved by §4 (migrated to Stage 2 before removal):**
- `data/interim/pgp_adjudication.csv` (the blank scaffold, sha256 above)
- `.claude/usr/matthew-mo/lung-on-chipsim/` — the agent's handoff, `briefings/`, `history/`
- `projects/lung-on-chipsim/.dvc/config.local` (local DVC remote config; not tracked)
- `workstreams/.../qgr/evidence/scan-artifacts-f66fbf7.json` (the untracked scan evidence)
- branch `lung-on-chipsim` @ `f66fbf7` — **untouched**

**Deliberately NOT migrated (regenerable, ~GB of churn):**
`.venv/`, `.ruff_cache/`, `.pytest_cache/`, `__pycache__/`, `.coverage`, `.dvc/cache/`, `.dvc/tmp/`,
`config/monitor-pids.json`, `.claude/logs/`.
`.dvc/cache` is the one judgement call: it is a content-addressed cache re-fetchable from the DVC
remote. If the remote is unreachable, re-fetching fails — **this is the one item worth a second
opinion before removal.**

**Destroyed:** the working directory `worktrees/lung-on-chipsim` itself, and the regenerable items above.

---

## 4. Proposed execution (NOT YET RUN)

```bash
# S0. Re-verify no session holds the worktree (must print GONE)
ps -p 13641 >/dev/null 2>&1 && echo "ALIVE — STOP" || echo "GONE"

# S1. Preserve the worksheet into Stage 2, then verify by hash
SRC=/Users/mo/github/personal/bioFM/worktrees/lung-on-chipsim
DST=/Users/mo/github/personal/bioFM/worktrees/lung-on-chipsim-stage2
cp -n "$SRC/projects/lung-on-chipsim/data/interim/pgp_adjudication.csv" \
      "$DST/projects/lung-on-chipsim/data/interim/pgp_adjudication.csv"
shasum -a 256 "$DST/projects/lung-on-chipsim/data/interim/pgp_adjudication.csv"
# MUST equal 679b017221d7ccfd0a62f8e0071402f8e0ce03ad666f880460bc9b32aabe9fe1

# S2. Second copy OFF the worktree tree (survives any later worktree mistake)
mkdir -p ~/bioFM-archives/lung-interim-20261018
cp -n "$SRC/projects/lung-on-chipsim/data/interim/pgp_adjudication.csv" \
      ~/bioFM-archives/lung-interim-20261018/

# S3. Migrate agent state + local DVC config + scan evidence
cp -Rn "$SRC/.claude/usr/matthew-mo/lung-on-chipsim/." \
       "$DST/.claude/usr/matthew-mo/lung-on-chipsim/" 2>/dev/null || true
cp -n  "$SRC/projects/lung-on-chipsim/.dvc/config.local" \
       "$DST/projects/lung-on-chipsim/.dvc/config.local" 2>/dev/null || true
cp -n  "$SRC/workstreams/lung-on-chipsim/qgr/evidence/scan-artifacts-f66fbf7.json" \
       "$DST/workstreams/lung-on-chipsim/qgr/evidence/" 2>/dev/null || true

# S4. Remove the Stage 1 WORKTREE ONLY — never the branch
cd /Users/mo/github/personal/bioFM
git worktree remove worktrees/lung-on-chipsim      # add --force only if it refuses on ignored files
git worktree prune
git branch --list lung-on-chipsim                  # MUST still list the branch

# S5. Resume the agent in Stage 2
cd "$DST" && claude --agent lung-on-chipsim
#   then, inside that session: /airdlc:session-resume
#   its catch-up sweep delivers #608 and #622, which is the point of the whole exercise
```

### Notes on the commands
- `cp -n` (no-clobber) throughout: if a destination already exists, it is **not** overwritten. S1 is
  therefore safe even if someone has already placed a worksheet in Stage 2 — but then the hash check
  will mismatch, which is the signal to stop and compare by hand rather than overwrite.
- `tools/worktree-delete` is **not** used: it is defective for this repo shape
  (`.claude/aiadlc-feedback/2026-10-17-worktree-delete-resolves-worktree-base-relative-to-the-submodule-repo.md`),
  and the aviary agent hit the same wall yesterday and fell back to raw `git worktree remove`.
- Ordering follows the retirement rule: **worktree first, branch never**.

## 5. Rollback

- S1–S3 are pure copies: rollback is deleting the copies.
- S4 is the only destructive step. If it proves wrong, the worktree is recreatable with
  `git worktree add worktrees/lung-on-chipsim lung-on-chipsim` **because the branch survives** —
  only the regenerable caches and `.venv` would need rebuilding.
- If the branch were ever lost anyway: `git bundle unbundle ~/bioFM-archives/lung-on-chipsim-stage1-f66fbf7-20261013.bundle`
  (restore-tested 2026-10-13: 1303 commits, 4/4 transport files, 920 lines).

## 6. Decisions I need from the principal

1. **Execute §4?** It removes the Stage 1 working directory. The branch, the worksheet and the agent
   state all survive.
2. **`.dvc/cache` — discard or migrate?** Default above is discard as re-fetchable. Say migrate if the
   DVC remote is not reliably reachable.
3. **Worksheet protection, now that it is dated rather than urgent** — the standing open decision.
   Options unchanged: a `.dvc` entry for `data/interim/`, an off-machine encrypted copy, or tracking a
   column-stripped form with `canonical_inchikey` withheld. S2 above is a stopgap, not an answer.
