---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-02T04:02
status: created
priority: high
size: task
subject: "S12 task has NOT landed — requesting it; declining to build against approval-in-principle (N1 lesson). Starting /design meanwhile."
in_reply_to: null
---

# S12 task has NOT landed — requesting it; declining to build against approval-in-principle (N1 lesson). Starting /design meanwhile.

Agent: lung-on-chipsim
S12 has not landed as a task — requesting it, and NOT building against approval-in-principle.

## The blocker

Merged trunk. Plan-gate green at `a44e523` (r2.5). Grepped `build-plan.md` for `S12` and for
`journal`: **no S12 task exists.** The only `journal` hit is the XB actor row at :55.

You approved the concept, ruled all four of my design questions, and said "Do not proceed further
on this until S12 lands." It has not landed. So I am not building it.

Being explicit about why, because the principal has asked me to proceed with S12 and I am declining
the code half: building a subsystem that no plan task authorizes is **N1 exactly** — the error that
cost four gate cycles today. The standing rule you wrote after it says the plan is the authority.
Approval-in-principle from you is not a task, and I would rather ask twice than front-run the plan
again.

## What I am requesting

`S12 · Build the run journal — CA`, in the P0 scaffold series (it creates `journal/`, which AM-4's
tree lists and no task creates — the same gap class as the original scaffold hole).

Module is written, 250 lines, held at /tmp/journal.py, unchanged since your ruling. Shape as you
ruled it:

- `start_run()` called BEFORE any work: creates `journal/<run_id>/`, COPIES every `configs/*.yaml`
  into `journal/<run_id>/configs/`, writes `manifest.json`
- manifest records run_id, UTC start, exact argv, git commit AND dirty flag with the dirty file
  list, python + platform, resolved versions of the output-determining packages
  (pyarrow, rdkit, pandas, numpy, PyYAML), per-config sha256, and CHIPSIM_SEED / PYTHONHASHSEED /
  SOURCE_DATE_EPOCH where set
- run directories IMMUTABLE — creating one that exists raises
- `manifest_sha256` verified by `read_manifest()`; `outcome.json` written last so a crashed run is
  distinguishable from a silent success
- a dirty tree is RECORDED, never hidden or refused
- `panel-seal` journalled as record type **`invocation`**, not `run`: argv, environment, timestamp,
  **no digest**, per your overrule — recording every invocation is what makes a Constraint (4)
  violation detectable

Suggested done-conditions, all fixture-testable:

1. a run snapshots every `configs/*.yaml` and the copies' digests match the manifest;
2. editing a config AFTER a run does not change what that run's snapshot says it used;
3. re-using a run id RAISES rather than overwriting;
4. a tampered `manifest.json` fails `read_manifest()`;
5. a crashed run leaves no `outcome.json`, so it cannot read as success;
6. a `panel-seal` invocation record carries no digest field.

## What I have applied from this cycle, unprompted

Two things I will build in from the start rather than have a gate find them:

- **(4)-style honesty:** the manifest digest detects modification of a run record. It does not prove
  who wrote it. The docstring will say so, and no wording anywhere will imply the journal
  authenticates anyone.
- **Mandatory, not opt-in:** `read_manifest()` will REFUSE a manifest with no `manifest_sha256`
  rather than loading it unverified — C1's lesson. A record whose verification can be removed by
  deleting a line is not a record.

## Sequencing

Starting `/design` for `chipsim-lbm-audit` now, which you released and which needs no push. If S12
lands mid-design I will finish the document phase before switching — interleaving two workstreams
in one worktree is how N1's conformance drift happened.

Not pushing until the land completes.
