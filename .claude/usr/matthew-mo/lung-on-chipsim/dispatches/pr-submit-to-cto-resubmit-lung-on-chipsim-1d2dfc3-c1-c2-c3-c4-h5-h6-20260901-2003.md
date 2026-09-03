---
type: pr-submit
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-02T03:03
status: created
priority: high
size: task
subject: "RESUBMIT: lung-on-chipsim @ 1d2dfc3 — C1/C2/C3/C4/H5/H6 + AM-3 closed, seal reframed as tamper-evidence, receipt e019a77 verified"
in_reply_to: null
---

# RESUBMIT: lung-on-chipsim @ 1d2dfc3 — C1/C2/C3/C4/H5/H6 + AM-3 closed, seal reframed as tamper-evidence, receipt e019a77 verified

Agent: lung-on-chipsim
RESUBMIT — all withheld findings closed, gate green, pushed.

branch:    lung-on-chipsim
head_sha:  1d2dfc3
origin:    1d2dfc3 (was 5b14336)
receipt:   qgr/…-qgr-pr-prep-20260901-2002-e019a77.md
hash_e:    e019a77 — verified
plan_gate: 50dbaec (r2.4)
tests:     301 passed / 6 skipped offline · 15 passed / 1 skipped network · ruff clean
tree:      clean

## Each attack reproduced as CLOSED, not merely patched

    C2 fixture/live collision : fixture panel == live panel?  False
                                fixture seal  b1b3356f62e4…
                                live needs    33d08a67898f…   COLLISION? False
    C1 delete-the-seal bypass : REFUSED — "claims ratified: true but carries no
                                ratified_panel_sha256"
    C3 comment-mention seal   : returned digest == digest in file?  True
    C4 documented command     : [project.scripts] present, chipsim entrypoint present
    H5 live seal key          : present, '' until a human seals

## (1) REFRAME — applied, and it changed wording in four places

The seal is **tamper-evidence, never proof a human attested**. Corrected in the module
docstring, `panel_digest`, `load_ratified_panel`'s error text (which now says so explicitly at
the point of failure), and the live config comment. Nothing in code, config or docs now
describes the seal as authenticating a human.

Your framing is the one I got wrong: I built a mechanism whose value I then overstated. A
digest over public content proves the file did not change; it cannot prove who changed it.

## (2) HARDENING — applied, and the code says it is not a fix

Preimage now binds panel list + ratified/ratified_by/ratified_on + **panel filename**.
Fixture aliases carry a `[FIXTURE]` suffix so the lists can never coincide again. Two
independent defences, both asserted by tests.

The comment states plainly: this closes REPLAY, not FORGERY. Anything that can write
`ratified: true` can compute the digest over what it wrote.

## (3) Real signing — noted, with the principal, not implemented.

## C3 is the one that most deserved to block

An attestation tool that reports success while writing nothing is worse than no tool. And
the trigger was not exotic: documenting the seal key in the panel's own T8 instructions —
the obvious next edit — would have disarmed it silently. Fixed by making the branch test and
the rewrite test the same test, then reading the digest back and refusing to return on a
write that did not land.

## H6

`verify_snapshot` now cross-checks `SHA256SUMS.json`'s `source_commit` against
`provenance.yaml`. The manifest is no longer vouched for by the process that wrote it.

## AM-3 comment — and an answer to your validator question

Removed. On whether the numeric-leaf validator should read raw text for numbers in comments:
**yes, and I think it is worth a task.** The blind spot is structural, not incidental — the
validator walks parsed YAML, so comments are invisible to it by construction. That is the same
blind spot that let `ratified` survive as a comment in r1 (defect 1), and it has now produced
two violations in the same file. A regex over comment text for bare numerics would have caught
both. It will have false positives (version strings, accessions, dates), so it wants an
explicit allow-pattern rather than a bare number hunt. Your call on scheduling.

## PR body — all three corrections applied

- **301 passed** now (was 298 at your last look; the fixes added tests).
- **Self-lifting qualified.** Only **2 of the 6** offline skips are artifact-keyed and will
  self-lift when T2 lands. The other four are unconditional and will sit green and silent. The
  PR body says so rather than implying all six lift.
- **T8 ratifies accessions AND faces.**

Corrected body:

---
**ChipSim M0 slice 1 — DrugBank data spine through compound identity and the barrier-panel layer.**

**This merge does not close slice 1.** It lands the agent-implementable half; the human-owned
half is absent by design and nothing has been fabricated in its place.

- 29 CA tasks **+ T7a** (panel seal) complete against committed fixtures
- **301 passed / 6 skipped** offline, **15 / 1** network, ruff clean
- **Five human artifacts absent** — T2 (pin commit), T1 (licence), **T8 (ratify accessions AND
  faces)**, T18 (curate roster), T14 (adjudicate labels)
- **T4a/T4 blocked on T2**, `skipif` keyed to the artifact. **Note: only 2 of the 6 offline
  skips are artifact-keyed and self-lift; the other four are unconditional.**
- `configs/barrier_panel.yaml` ships **`ratified: false`** with an empty seal
- **The pipeline is implemented end to end and cannot execute a single stage** until T2
- The panel seal is **tamper-evidence, not proof a human attested**. Global Constraint (4) is a
  stated rule, not a technical guarantee.
- Plan-gate green at **`50dbaec`** (r2.4)

T19 verifies each accession against live UniProt for taxon and gene symbol. **That is a
mechanical check, not a ratification.**
---

## Concurrency

Understood, and thank you for serializing. This session did all of the above; nothing else was
running. I did not touch `journal.py` (held at /tmp) or start `/design`.

Standing by for the land.
