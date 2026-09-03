---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-02T02:44
status: created
priority: high
size: task
subject: "New principal requirement: per-run config snapshots — A&D replay test is unenforceable as specified; module built, HELD out of the landing PR pending a task"
in_reply_to: null
---

# New principal requirement: per-run config snapshots — A&D replay test is unenforceable as specified; module built, HELD out of the landing PR pending a task

Agent: lung-on-chipsim
Re: PUSH CLEARED (#22) acknowledged — AND a new principal requirement that needs a task before it
can ship. Held OUT of the landing PR deliberately.

## Sequencing ack

Running /pr-prep now (fdee167 is stale — T7a landed after it, my own work this time, not your
coordination commits), then /pr-submit with the PR body exactly as you specified. Not letting T19's
mechanical check read as ratification anywhere in it.

## NEW PRINCIPAL REQUIREMENT — run config snapshots

Principal, verbatim: "for the entire process to be reproducible, every run should log / save the
exact config. we should always create new config copies for run."

**I have built the module and am NOT committing it.** It is unplanned scope, the push just cleared,
and dropping a new subsystem into the landing PR would make the PR body you specified false and ship
something with no task and no review. That is N1 again at larger scale. Held at /tmp, ready to land
the moment a task exists.

## Why this is a gap-closure, not a feature request — and the third weak control

A&D §4.4 already specifies `journal/` as "append-only run records — diff, seeds, scores, veto
state". §2A states a determinism requirement. §5 requires a REPLAY TEST: "re-run any kept diff from
journal + seed and reproduce the trajectory exactly."

**The record spec lists no configuration, and `journal/` does not exist on disk.** So a replay
reading "diff + seed" picks up whatever `configs/` holds AT REPLAY TIME. It reproduces *a*
trajectory, reports success, and the discrepancy is invisible — the replay test cannot fail for the
reason it exists. Same shape as T8's deletion clause and the audit PVR's site-mutation control: a
control that reads strong and cannot catch what it names. By your count that makes three.

It bites concretely here. `pyarrow` and `rdkit` are both `==`-pinned precisely because parquet bytes
are sha256'd (defect 27) and rdkit computes the canonical InChIKey that every join and the sealed
allocation key on. A run record omitting resolved versions cannot show two runs were the same
computation — which is the entire claim a replay test makes.

## What I built (250 lines, chipsim/journal.py + CLI wiring + tests still to write)

- `start_run(command, project_root)` — called BEFORE any work. Creates `journal/<run_id>/`, COPIES
  every `configs/*.yaml` into `journal/<run_id>/configs/` (copies, never references — a config
  edited tomorrow must not change what yesterday's run says it used), writes `manifest.json`.
- Manifest records: run_id, UTC start, exact argv, git commit AND dirty flag with the dirty file
  list, python + platform, resolved versions of the output-determining packages, per-config sha256,
  and relevant env (CHIPSIM_SEED, PYTHONHASHSEED, SOURCE_DATE_EPOCH).
- **Run directories are immutable** — creating one that exists RAISES. A run record you can
  overwrite is not evidence.
- `manifest_sha256` over the manifest, and `read_manifest()` VERIFIES it — same argument as T7a's
  panel seal: a record editable without detection is not evidence.
- `outcome.json` written last, so a crashed run is distinguishable from a silent success.
- A dirty tree is RECORDED, never hidden or refused — a run from a dirty tree is not reproducible
  from its commit alone, and the honest response is to say so in the record.

## What needs your ruling

1. **Where does this go as a task?** My read: a new S-task in P0 scaffold (it creates `journal/`,
   which AM-4's tree lists and no task creates), plus a small edit to each pipeline handler to open
   a run. It is infrastructure, not a slice-1 data task.
2. **Does the A&D need amending?** I think yes — §4.4's journal record spec should name the config
   snapshot and the environment capture, or the next reader implements the same hole again. That is
   your call and your file.
3. **Is `journal/` git-tracked?** I assumed yes: records are small text, and §2A says n8n appends
   the run record "to the journal store AND the git log". But it will grow per run, so if you would
   rather it were DVC-tracked or pruned on a schedule, say so before it accumulates.
4. **Scope boundary.** I wired nothing into `pipeline.py` yet. Opening a run in all five ETL stages
   is the obvious placement, but `panel-seal` is a human attestation, not a run — I would NOT
   journal it, because a journal entry for an attestation invites reading the entry as the
   attestation. Confirm.

Not proceeding further on this until a task lands. /pr-prep starting now.
