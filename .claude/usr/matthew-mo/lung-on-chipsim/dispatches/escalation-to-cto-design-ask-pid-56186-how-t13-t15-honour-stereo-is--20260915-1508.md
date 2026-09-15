---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-15T22:08
status: created
priority: normal
size: task
subject: "Design ask (pid 56186): how T13/T15 honour stereo_is_relative without breaking human worksheets. Proposal: generated-column class, never carried, optional on read; T15 carries flag to parquet (raise vs NA on legacy?); T10 refuses unflagged frames. Building roster/helper/persistence pin meanwhile"
in_reply_to: 122
---

# Design ask (pid 56186): how T13/T15 honour stereo_is_relative without breaking human worksheets. Proposal: generated-column class, never carried, optional on read; T15 carries flag to parquet (raise vs NA on legacy?); T10 refuses unflagged frames. Building roster/helper/persistence pin meanwhile

# Design ask before I touch the human worksheet: how T13/T15 honour `stereo_is_relative`. Building the unambiguous parts (roster, helper, persistence pin) meanwhile.

**Sender: claude pid 56186, writer.** No push. No accessions in this dispatch.

## Why I am asking, not building

#122 §0 says T10, T13 and T15 "must honour" the flag, and that T18's roster "must be able to
exclude flagged compounds". For T18 and the helper the meaning is clear, and I am building them
test-first now (§3). **For T13/T15, "honour" collides with the module that protects
irreplaceable human work, and there are two obvious implementations that are both wrong:**

1. **Add `stereo_is_relative` to `WORKSHEET_COLUMNS`.** `_read_worksheet` requires every
   declared column, so **every existing human worksheet without it becomes unreadable**
   ("missing column(s)"). That locks a reviewer out of T14 work the module docstring prices at
   60–90 minutes.
2. **Write it as an extra column, outside `WORKSHEET_COLUMNS`.** The T13 merge treats any
   non-declared column as **human-added** and carries a prior non-blank value OVER the fresh one.
   So the first regeneration after a snapshot or ruling change would keep a **stale flag
   silently**. That is the never-clobber rule working correctly in a case it was not designed for.

You have said that for fixtures and human artefacts you would "rather rule on the approach than
have it inferred". This is the same kind of decision, so here is a concrete proposal.

## Proposal

**T13 — a new GENERATED-column class in the worksheet.**
- `GENERATED_COLUMNS = ("stereo_is_relative",)`, written on every regeneration from the current
  compounds frame (per key: True if any member is flagged), **never carried** from the prior sheet,
  and **optional on read**, so older worksheets still load.
- Placed after `snapshot_label` so the reviewer sees it beside the evidence it qualifies.
- Tests: a legacy worksheet without the column still loads and merges; a stale prior value is
  **overwritten** by the regenerated one, which is the falsification of option 2's failure; human
  columns remain never-clobbered.

**T15 — carry the flag into the label output.**
- `adjudicate_pgp_labels` reads `stereo_is_relative` from the worksheet when present and writes it
  into `pgp_labels.parquet` beside `adjudicated_label`, so T17 receives it. The returned Series stays
  a Series (no API break).
- **Open question for you:** if the column is **absent** (a legacy worksheet), should T15 raise
  (forcing a T13 regeneration first) or write the flag as unknown/NA? I lean **raise**, because a
  label set that silently lacks the flag is the stale-flag failure one step later. But that means
  a reviewer's completed legacy sheet needs one T13 regeneration before T15 will accept it. The
  regeneration preserves their work.

**T10 — refuse a frame without the flag.**
- `pgp_substrate_label` raises if `compounds` lacks `stereo_is_relative`, proving the flag travelled
  from T5b. The output is unchanged: the label is evidence, and evidence pooled across a merged
  stereo-free key is correct under the ruling.

## One interaction to decide alongside: labels that contradict structure

The re-key exposed three snapshot rows **labelled "D-" whose structures are L** (lysine, alanine,
cysteine; #123 §3). The T13 worksheet renders `name` from `compounds.drop_duplicates(key)`, so a
reviewer can be shown **"D-Lysine" beside L-lysine's key**. The flag does not catch this, because
those rows are absolute, not relative. Should T13 also surface a label/structure warning column, or
is recording it as a limit enough? I have no measurement of how common this is beyond the three
found.

## Building now (does not touch human artefacts)

- **`relative_stereo_keys(compounds)`**: canonical keys with any flagged member. It **raises** on a
  frame lacking the column, so a pre-re-key frame cannot pass as "none flagged".
- **T18 `load_poc_roster(..., relative_stereo_keys=None, allow_relative_stereo=False)`**: a roster
  naming a flagged key is **rejected loudly, listing the keys**, unless explicitly allowed. It is
  never silently filtered, because the roster is a human claim and the module validates but never
  generates.
- **A literal pin on `PERSISTED_COMPOUND_COLUMNS`.** The old persistence test compared the written
  columns against the tuple's own symbol, which is why adding the flag broke nothing, and why
  dropping it would also have passed.
