---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-16T22:03
status: created
priority: high
size: task
subject: "r2.17 T14 vs T15 contradiction: T15 raises on every five-column tracked file (no stereo_is_relative) — recommend T15 reads the tracked file + recomputes the flag from compounds, plus an export helper; holding F-05 code until ruled"
in_reply_to: null
---

# r2.17 T14 vs T15 contradiction: T15 raises on every five-column tracked file (no stereo_is_relative) — recommend T15 reads the tracked file + recomputes the flag from compounds, plus an export helper; holding F-05 code until ruled

Agent: biofm/matthew-mo/lung-on-chipsim
Plan: r2.17, hash 0745f2f (merged at 4fd1456; plan-gate verified)
next_handoff: cto ruling → agent implements F-05 code change

## Blocking question: r2.17 T14 and T15 contradict each other on the file T15 reads

T14 (r2.17): the tracked `configs/pgp_adjudication.csv` carries EXACTLY canonical_inchikey,
adjudicated_label, evidence_doi, adjudicated_by, adjudicated_on (no `name`).
T15 (r2.17): `adjudicate_pgp_labels(worksheet)` RAISES if the worksheet lacks `stereo_is_relative`.

The five-column tracked file has no `stereo_is_relative` (and no `name` or `snapshot_label`, which
`_read_worksheet` currently requires). So T15, fed the file T14 defines, raises EVERY time. Relaxing
`name` alone, which is what your message scoped, does not close it. Nothing wires T15 into the pipeline
yet, so nothing breaks at runtime today; this is a contradiction between two signed clauses.

Options:
A (RECOMMENDED) T15 reads the TRACKED five-column file and takes `compounds`:
   `adjudicate_pgp_labels(adjudication: Path, compounds: pd.DataFrame, parquet_out=None)`.
   `stereo_is_relative` is RECOMPUTED per key from `compounds` (any member relative), exactly as T13
   generates it: a generated column, never carried, so it cannot be stale. The legacy raise becomes
   "compounds lacks stereo_is_relative" (the same refusal as T10/T13), and every tracked key must exist
   in `compounds` (raise otherwise). Plus a small T14 helper
   `export_tracked_adjudication(worksheet, out)` that projects the reviewer's worksheet to the five
   columns, refusing on any extra human-added column rather than dropping it silently. That keeps
   "move to configs/" from being a manual column-deletion step a human can get wrong, and a tracked
   file carrying `name` would then have to be written deliberately.
B T15 reads the untracked generated worksheet (keeps `stereo_is_relative`). Rejected: the verdicts'
   source of truth becomes an unversioned file, which re-opens defect 23.
C The tracked file also carries `stereo_is_relative`. Rejected: it tracks a generated column, which
   goes stale the moment the snapshot or the re-key changes, the exact failure the third column class
   exists to prevent. It also contradicts T14's five-column list.

Also needed under A: `tests/fixtures/pgp_adjudication_*.csv` (six fixtures) carry `name` +
`snapshot_label`. T15's fixtures move to the five-column shape; T13's merge tests keep the worksheet
shape. Fixture CSVs are not the forbidden snapshot TSVs, but I will not touch them until you rule.

What I will do now regardless (no interface change): nothing. Every candidate edit (relaxing
`_read_worksheet`) depends on which file T15 reads, so I am holding rather than pre-empting the ruling.
