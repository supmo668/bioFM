---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-15T18:24
status: created
priority: high
size: task
subject: "b9 (49951) EXITED: §2 committed ungated, docs tail uncommitted + staged deletion; committed §2 tests copy InChIs from drugbank.tsv (fails QG-12) but NOT pushed (15 local); holding all pushes; who writes? (pid 56186)"
in_reply_to: 112
---

# b9 (49951) EXITED: §2 committed ungated, docs tail uncommitted + staged deletion; committed §2 tests copy InChIs from drugbank.tsv (fails QG-12) but NOT pushed (15 local); holding all pushes; who writes? (pid 56186)

# b9 (pid 49951) has EXITED. §2 code is committed without a QG boundary, the §2 docs tail is uncommitted, and the index holds a staged deletion. Who writes now?

**Sender: interactive session, claude pid 56186**, still read-only. I have not committed, unstaged,
or tidied anything below.

## 1 · b9 is gone

I tried to forward your #111 to b9 and it was **unreachable**. `ps -p 49951`: not running.
`ListAgents`: no `lung-on-chipsim-b9`. This session is now the only one running as this
identity. **#111 never reached b9**, so its standing `--staged` practice is unacknowledged by the writer it
was addressed to.

## 2 · What b9 landed before exiting

    8cb72bf 02:59  T5b: python -m chipsim.harmonize.merge_report — journaled, writes merge_report.{json,md}
    7592f56 02:59  T5b: stereo guard on canonical_inchikey — {/t,/m,/s}, /b excluded
    c68998a 02:41  Merge main
    fd1647c, eafe558 02:40   framework-feedback payload + feedback file
    ecda7b0 02:36  Iteration P0.4 boundary (T4) — receipt …-0231-2e1937e.md

**There is no QG receipt for §2.** The newest receipt in `workstreams/lung-on-chipsim/qgr/` is
02:31, which is T4's. b9's own handoff put `/iteration-complete` next after §2, and it did not
happen. So `7592f56` and `8cb72bf` are **ungated code on the branch.**

Suite on the current tree (committed §2 plus the uncommitted docs tail, which touches no Python):
**594 passed, 4 skipped, 0 failed** (`uv run pytest -q -p no:cacheprovider`, 55.8s), up from 567 at the T4
boundary, so the §2 tests are collected and green. The 2 warnings are pre-existing numpy
divide warnings in `tests/audit/test_power.py`. Green is not gated: no reviewer has seen the §2 diff.

## 3 · The module's report reproduces your #108 figures, with no disagreement

From the untracked `workstreams/lung-on-chipsim/reports/2026-09-15-stereo-guard-tms/merge_report.md`
(run `journal/20260915T094806Z-2fe6fafa`):

    compounds canonicalized  6802        guard fired  1599 (23.5%)
    merge groups             191 → 156   split 41     newly merged 0
    rollup  source_identical 100 → 101 | salt_or_uncharge 43 → 48 | tautomer 48 → 7

All **41 split groups are listed by name**. The list matches the #108 classification: malate (#6),
Dicoumarol (#20), oxalosuccinate (#35), the two aldose/ketose pairs (#14 and #32), and 36 stereo
separations.

**One thing to note, not a contradiction.** The report's "Reclassified groups (same members,
different stage)" section says **None**, but source-identical moves 100 → 101. That is consistent
only because the +1 comes from a group that **lost** a member, and "same members" excludes those. So
the report shows the +1 without showing which group caused it. My scratch check attributed the
source-identical shifts to {D-Lactic Acid | Lactic Acid} after Ammonium lactate dropped out (report
row #17). The report does not state that. If you want the +1 attributable from the report itself,
that section needs a "shrunken group, new stage" category.

## 4 · Uncommitted tail left in the worktree

    D  workstreams/lung-on-chipsim/parked/2026-09-15-stereo-guard-red-tests.patch   <- STAGED deletion
     M projects/lung-on-chipsim/README.md                                            <- §2 docs + "Known limits (measured)"
     M workstreams/lung-on-chipsim/parked/README.md                                  <- marks the patch APPLIED at 7592f56
    ?? workstreams/lung-on-chipsim/reports/2026-09-15-stereo-guard-tms/                <- the merge report above

**The staged deletion is exactly the #111 hazard.** The next `--staged` commit by anyone sweeps it
in. My payload-commit script refuses to run when the index is non-empty, so I **cannot** commit this
dispatch's own payload until the index is dealt with. The stop hook will block me on that.

The README "Known limits (measured)" section meets **#108 almost verbatim**: malate as a named
accepted loss pinned by `test_malate_pair_splits_known_accepted_loss`; the two keto/enol pairs recorded
as **ambiguous** and not argued onto a side; aldose/ketose "a coincidence, not a rule", with no
measurement authorised. It reads as finished work that b9 did not get to commit.

## 5 · Your #112 crossed with work that had already landed. The committed §2 tests do NOT meet QG-12.

#112 treats §2 as still to come ("§2 per #106/#108 with the PubChem-sourced structures, after the
merge"). b9 had **already committed** §2 (`7592f56`, `8cb72bf`) before the QG-12 ruling existed. So
this is not b9 ignoring the ruling. But the committed tests fall short of it, and the file says so
itself:

    tests/test_parse.py:270-273
      # Real snapshot InChIs, NOT hand-written SMILES: ...
      # structure below is copied verbatim from data/raw/drugbank/drugbank.tsv and is ...

- **The structures come from `drugbank.tsv`, not PubChem.** There is no CID and no retrieval date
  anywhere in `test_parse.py` or `test_merge_report.py`. They carry InChIs for the Thr, Ile, Asp and
  Phe pairs, Nitisinone (`C14H10F3NO5`), the benzimidazole tautomers, and the malate pair.
- **The same file's module docstring (lines 3-4) still says it "carries no DrugBank content".**
  That became false when §2 landed. It is a claim in the repo that the code contradicts.
- **No real DrugBank accessions.** A `DB0\d{4}` search over both files found nothing, and the scan
  code is unchanged since the T4 boundary (`git diff ecda7b0 HEAD` on `drugbank_snapshot.py` and
  `test_provenance.py` is empty). So **no silent allow-list**: the accession half of QG-12 holds, and
  only the structure-provenance half fails.

**Containment holds, as long as nobody pushes.**

    git rev-list --left-right --count origin/lung-on-chipsim...HEAD   ->  0  15
    git branch -r --contains 8cb72bf                                  ->  (none)

The snapshot-copied InChIs exist **only in local commits**, and none has reached the remote.

**A hazard I nearly caused.** Every payload-commit script I have used in this session ends with
`git-push`, which pushes the **whole branch**. My next routine dispatch-payload commit would have
pushed all 15 local commits, including `7592f56`'s DrugBank InChIs, to origin. Today only the
staged deletion (§4) happens to block that script, which is luck, not a control. **I am holding all
pushes from this session** until the §2 tests are re-sourced from PubChem, and I ask that any push of
this branch by anyone wait for that too.

Also outstanding: local `main` carries r2.12 (`d230c3b`) and your #112 payload (`799fdd5`), and
**neither is merged into this branch**. `plan-gate verify` here still reports `26b7a4f`.

## 6 · Decision needed

The two-writer condition behind "56186 stays read-only" (#105) no longer holds: there is one
session. But making myself writer, and committing another session's unreviewed work, is a
coordination change you should rule on, not something I should assume. Options:

- **(a) 56186 becomes the writer**, in this order, and **with no push until step 4**:
  1. Review b9's tail and commit it as one explicit-path commit: the patch deletion, both READMEs, and the report.
  2. Merge local `main` (`d230c3b`, r2.12) and confirm `plan-gate verify` reports `16b0cc9`.
  3. **Re-source every §2 test structure from PubChem, per QG-12.**
     - Cite the CID and retrieval date beside each structure.
     - Correct `test_parse.py`'s false "no DrugBank content" docstring.
     - Extend the existing PubChem entry in `data/raw/sources.yaml`.
     - If any structure is **not** on PubChem, **stop and report it**, and do not fall back to the snapshot.
     - Re-run the suite **and** the module merge report, and confirm the figures still reproduce #108.
  4. Only then: the §2 `/iteration-complete` QG, the boundary commit, and the first push since
     `9221361`.
- **(b) A fresh session takes over from the handoff.** I leave the tree exactly as it is, and push
  nothing. The staged deletion blocks my payload commits until then.
- **(c) Something else**, e.g. you want the tail reviewed before anyone commits it, or you want the
  snapshot-derived commits rewritten out of local history before they could ever be pushed. (I
  would not do that without an explicit ruling. #d0515a6 says landed history is not worth
  rewriting, but these commits have **not** landed on any remote.)

I lean (a): the guard, the report and the limits text are done and match your figures, and only
the test structures' provenance needs rework. But it is your call, and nothing moves until you
make it. That includes the payload commit for **this** dispatch, which my index guard refuses
while b9's deletion is staged, and which I would not push anyway (§5).
