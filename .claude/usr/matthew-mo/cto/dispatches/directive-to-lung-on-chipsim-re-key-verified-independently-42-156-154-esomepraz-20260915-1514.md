---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-15T22:14
status: created
priority: high
size: task
subject: "Re-key verified independently (42, 156->154, esomeprazole merge, 3 splits); T13 generated-column class ACCEPTED, T15 RAISE on legacy, T10 refuse unflagged, /b retention ratified; label/structure column HELD on a prevalence measurement"
in_reply_to: null
---

# Re-key verified independently (42, 156->154, esomeprazole merge, 3 splits); T13 generated-column class ACCEPTED, T15 RAISE on legacy, T10 refuse unflagged, /b retention ratified; label/structure column HELD on a prevalence measurement

# Re-key VERIFIED independently. T13/T15/T10 ruled. The label/structure question is HELD on a measurement I am running.

## 0 · I reproduced your re-key rather than taking it on report

    relative (/s2) by string flag: 42
    merge groups  strip OFF: 156  ->  strip ON: 154
    new groups under ON: 1     ['Esomeprazole', 'Omeprazole']
    groups present OFF but not ON: 3   D-/L- cysteine, D-/L- lysine, D-/L- alanine

Figure for figure what you reported, including the esomeprazole merge and exactly three splits.
Also verified: `PERSISTED_COMPOUND_COLUMNS` in `chipsim/ingest/drugbank_snapshot.py` does carry
`stereo_is_relative` — the fix without which the flag could never have reached T5a, and the one I
would have missed, since I first grepped only `chipsim/harmonize/`. And `git grep -P` over the five
files in `1b74814` with the exit status checked explicitly: **exit 1, no real accession entered that
commit**, so your retroactive check holds.

Your three label-error findings check out against PubChem too: the rows labelled D-lysine, D-alanine
and D-cysteine all key to PubChem's **L** structures, and the "L-" rows are the relative ones.

**Your `grep -P` disclosure is the best kind of report.** A guard that reported clean without
executing is the same defect class as the referee signing a skipped suite, and you found it in your
own helper and said so. The rule you adopted — guards use `git grep -P` or Python, and exit status is
checked explicitly rather than folded into `if` — is now standing practice on this branch. It binds
me too.

## 1 · T13 — GENERATED-column class: ACCEPTED as proposed

`GENERATED_COLUMNS = ("stereo_is_relative",)`, written on every regeneration from the current
compounds frame, **never carried** from the prior sheet, **optional on read**, placed after
`snapshot_label`. Your two failure analyses are exactly right: adding it to `WORKSHEET_COLUMNS` locks
a reviewer out of 60-90 minutes of irreplaceable work, and writing it as an undeclared column makes
the never-clobber rule preserve a **stale** flag. A third class is the correct answer, not a
compromise.

Required tests, as you listed them, plus one: a legacy sheet without the column loads and merges; a
stale prior value **is overwritten** (the falsification of the undeclared-column failure); human
columns stay never-clobbered; **and** a regenerated sheet round-trips through `_read_worksheet`
unchanged.

## 2 · T15 — RAISE on a legacy worksheet. Your lean is right.

If `stereo_is_relative` is absent, **raise**; do not write unknown/NA. A label set that silently
lacks the flag is the stale-flag failure one step later, and T17 cannot tell "absent" from "not
relative". The cost is one T13 regeneration, which preserves the reviewer's work — say so **in the
error message**, naming the exact command to run. An error that tells the human how to fix it is not
an obstacle; one that does not is.

## 3 · T10 — refuse an unflagged frame: ACCEPTED

`pgp_substrate_label` raises if `compounds` lacks the column, proving the flag travelled from T5b.
Your reasoning that pooled evidence across a merged stereo-free key is correct under the ruling is
right, and the output stays unchanged.

## 4 · `/b` retained when stripping: RATIFIED

Keeping `/b` while clearing tetrahedral tags is correct and I want it recorded as ratified rather
than resting on your judgement alone: InChI double-bond geometry is absolute, and the `/s` layer
qualifies only the sp3 stereo. The ruling was "assert nothing the source does not" — and the source
*does* assert its double-bond geometry.

## 5 · HELD: the label/structure warning column

You are right that the flag cannot catch it: those rows are absolute, not relative. You also said you
have no measurement of prevalence beyond the three found, and I am not going to rule on a design
change from a sample of three. **I am measuring it now** — every snapshot row with a D-/L- name
prefix, its key compared against PubChem's L and D keys for the same base name — and I will rule when
I have the number. If it is a handful it is a recorded limit; if it is widespread the worksheet needs
the warning column and the roster needs it too.

Do not build that part yet. Everything else in §1-§4 is unblocked.

## 6 · r2.14 is drafted and HELD until that measurement lands

The plan amendment naming the flag, the persisted column, the `relative-stereo` stage and the
threonine members **by InChIKey** is written. I am not signing it until the prevalence measurement
returns, because its note states how many label/structure mismatches the source has, and I will not
hash-lock a count I have not finished measuring. Your own rule, adopted: cite what was checked.

Order unchanged otherwise: §1-§4 now, then #122's §1-§5 fixes, guard test, fixtures, ledger, re-run,
then the §2 boundary. Push stays frozen.
