---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-16T21:00
status: created
priority: high
size: task
subject: "Session restarted: writer is now pid 80498 (verified; 56186 is gone). README limits fix landed 4ef9e9b. Repo-wide scan: r2.15 plan files carry real accessions (build-plan.md 3, plan-approval-log.md 1) — ruling needed before the guard test"
in_reply_to: null
---

# Session restarted: writer is now pid 80498 (verified; 56186 is gone). README limits fix landed 4ef9e9b. Repo-wide scan: r2.15 plan files carry real accessions (build-plan.md 3, plan-approval-log.md 1) — ruling needed before the guard test

# Session restarted: this writer is now pid 80498 (verified). README limits fix landed at 4ef9e9b. Repo-wide scan finds real accessions in r2.15's plan files — need a ruling before the guard test.

**Sender: this session, pid 80498** — verified by `ps -o pid,ppid,tty,lstart,command -p $PPID`:

    80498  1327 ttys010  Wed Sep 16 13:58:05 2026  claude

**pid 56186 is gone** — that was the previous process, which ended. Every dispatch I signed "56186"
was correct at the time; from here the writer is 80498. Stating it explicitly because #127 nearly had
the writer closed on an identity claim nobody re-checked. `dispatch catchup` on restart: inbox clear.
Monitor re-armed.

## 1 · Landed

- `49d3724` — DrugBank-coined titles out of tracked tests (#122 §1): `CRA_1144` → `BENZIMIDAZOLE_NEUTRAL`
  citing PubChem CID 1506 by IUPAC name (noting PubChem's own Title for 1506 is also "Cra_1144", a
  depositor code); the malate pair renamed by charge state. Swept the rest: generic names only.
- `4ef9e9b` — **README limits text corrected**. It cited 1,599 fired / 191→156 / 41 split while the
  committed `merge_report.md` it points at says **1,576 (23.2%) / 192→154 / 43 split**, run
  `20260915T221645Z-cc3521ea`. Rewritten against the report, re-checked line for line after writing,
  with a note that the figures supersede (not correct) the earlier run. Also removed the retired
  "lists every split group by name" claim, replaced the two coined titles, and added the
  relative-stereo re-key as a measured limit — the section predated it.
- r2.15 merged; `plan-gate verify` reports **`67a1897`**.

## 2 · Needs a ruling: the plan files carry real DrugBank accessions

Before building the repo-wide guard test (#122 §5, #120 §2), I measured what it would flag today.
`git grep -c -P '\bDB(?!9\d{4}\b)\d{5}\b'` over every tracked file:

    projects/lung-on-chipsim/configs/unparseable_compounds.yaml     9   sanctioned ledger (#120 §4)
    projects/lung-on-chipsim/tests/test_unparseable_exclusions.py  16   sanctioned ledger (#120 §4)
    .claude/usr/**/dispatches/  (12 payloads)                       1–13 named exclusion (#122 §3)
    workstreams/lung-on-chipsim/plan/build-plan.md                  3   <- NEW, arrived with r2.15
    workstreams/lung-on-chipsim/plan/plan-approval-log.md           1   <- NEW, arrived with r2.15

**The last two are hash-locked plan artifacts you own.** A repo-wide guard would fail on them the
moment it exists, and I cannot forward-fix them — editing `build-plan.md` breaks the signature, and the
approval log is append-only by design. Options, for your call:

- **(a)** forward-fix in r2.16: replace the accessions with InChIKeys, as done for `parked/README.md`;
- **(b)** a second named exclusion for `workstreams/**/plan/`, on the same reasoning as dispatches —
  coordination records, not a data product — citing a ruling;
- **(c)** something else.

I lean **(a)** for `build-plan.md` (a plan is read as a spec, and the invariant should hold where
people copy from) and **(b)** for the append-only log (rewriting a log falsifies it, the same argument
that ruled out redacting dispatches). **Not building the guard test until this is ruled**, so it is not
born failing or born with an exclusion nobody authorised.

## 3 · Queue after the ruling (#122 order)

Repo-root scan (#122 §5) — noting `DRUGBANK_ID_EXCEPTIONS` is keyed **project-relative**, so moving the
scan to the repo root would silently stop matching the sanctioned ledger unless the exceptions move to
repo-root paths in the same change; the falsification (plant an accession under `workstreams/`, watch it
fail) is what proves the wider scope took effect. Then the guard test, the fixture forward-fix, the
ledger change, re-run, §2 boundary, and the 57-finding gate pass.

Push stays frozen. No receipted landing attempted.
