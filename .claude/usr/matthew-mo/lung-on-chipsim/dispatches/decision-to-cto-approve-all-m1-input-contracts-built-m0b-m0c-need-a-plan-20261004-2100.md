---
type: decision
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-04T21:00
status: created
priority: high
size: task
subject: "APPROVE ALL recorded (2026-10-04): plan r3 + the agent-side prep. M1 input contracts BUILT (S13, S14, T21, T24, T28 — 45 tests, ruff/ty clean, CI job added). M0b/M0c NOT built: the build plan gives them no done-conditions, so a plan draft goes to the principal instead. New HACP row §experiment"
in_reply_to: null
---

# APPROVE ALL recorded; M1 input contracts built; M0b/M0c need a plan before code

The principal followed the twelve rulings with **"approve all"** in the same session
(`session_0181c6Cgx1w4D61dgPg73r7f`), after the grill's own lock "Over and out". Carry it into
`plan-approval-log.md` beside the twelve rulings. It covers folding the rulings as **r3**, cutting
the successor branch on that signature, and the agent-side preparation the rulings authorise.

It does **not** cover, and cannot: **A2** (a `git push` only the principal's machine can perform),
your trunk writes, and M0b/M0c code — see below.

## Built, on `claude/inspiring-archimedes-h0we1b`, ready to take by content at the A1 cut

Everything here has a done-condition in the plan, so none of it required a new specification.

| Plan task | Artifact |
|---|---|
| S13 | `configs/templates/theta_priors.scaffold.yaml` — six fields, every `value`/`citation` empty, all `assumed: true` |
| S14 | `configs/templates/transport_prior.scaffold.yaml` — two log-normal entries, no numbers |
| T24 | `chipsim/transport/theta.py` — `ThetaConfig`, frozen and read-only |
| T28 | `chipsim/transport/prior.py` — `TransportPrior` |
| T21 | `chipsim/harmonize/reference_compounds.py` — mirrors S11a |
| — | five non-ETL CLI subcommands, registered in `NON_ETL_SUBCOMMANDS` so T16's export check still compares against the ETL list exactly |
| — | `tests/test_m1_inputs.py` (31 tests) + 13 sentinel fixtures registered in `test_fixtures.py` |
| — | `.github/workflows/chipsim-m1-inputs.yml` |

**Measured:** 434 passed / 3 failed / 4 skipped / 30 deselected. The 3 failures are pre-existing
and were measured on a stashed tree before this work: two need the DVC payload on disk, and
`test_s6_live_panel_stays_unratified_until_a_human_signs` fails because the human ratification of
2026-09-12 outran its own test — **that one is yours to resolve**, since the test's own docstring
says to replace it with a `ratified_by` non-empty check rather than delete it. `ruff check`,
`ruff format --check` and `ty check` are clean; `ty` is now in the dev group and the lock.

### Two naming discrepancies for you to rule at the A1 cut

1. **`_require_sourced_theta`** is cited by `paper/stage1-methods.md`, the claims list and the HACP
   ledger, and placed by those documents in `fit.py`. The build plan's T24 specifies `ThetaConfig`
   in `theta.py` and never names the guard. The guard now lives in `theta.py` beside the schema it
   checks, with `require_sourced_theta` as its public alias, so the archived `fit.py` can import it
   rather than redefine it when A2 makes that file reachable. A test asserts the name exists.
2. **`load_adjudicated_labels`** is cited by the ledger and the checklist; the plan's T15 function is
   `adjudicate_pgp_labels`. Nothing was renamed. Flagging it so the ledger can be corrected rather
   than the code bent to match a document.

Also noted and **not** acted on: `chipsim/harmonize/adjudication.py` is at a pre-r2.17 state
(no `stereo_is_relative`, no `label_disagrees_with_key`, `adjudicate_pgp_labels` still takes
`worksheet` rather than r2.18's `(adjudication, compounds, parquet_out)`), `export_tracked_adjudication`
does not exist, and `configs/label_structure_reference.yaml` is absent. That is T13/T14/T15 drift on
hash-covered task definitions; the successor guidance is *do not open by repairing the register*, so
it is reported, not repaired.

## NOT built: M0b and M0c

The grill approved agent preparation for both. The build plan assigns them to the agent in the
ownership table (lines 1012–1013) and then says, for each, **"Its own plan."** There is no file
path, no field list, no signature format and no done-condition for the chip-record schema, the
sealing tool, the hash ledger, the splits or the freeze.

Writing that code would have meant inventing the specification and then verifying the code against
the specification it invented — the Stage 1 closure's mechanism, and six of its nine instances
arrived exactly that way. So instead:

`workstreams/lung-on-chipsim/plan/m0b-m0c-plan-draft-2026-10-04.md` — eight proposed tasks with
done-conditions a human can refuse, owners marked, and **one open methodological question for the
principal**: does the sealed allocation seal record *identities* or record *slots*? Only slots are
consistent with sealing before any record is read, so the draft specifies slots and flags the
choice rather than burying it.

Please fold it as **r3b** (or return it), after the principal rules the allocation question.

## Review surface

New HACP row: **§experiment — ChipSim: the M1 input contracts, built**,
`3ef749bd250d81a78efffdbadd500d29`, Kind Section, Section build, L2, indexed by the ChipSim index,
`Local path` set. The index row's Entries, Index table, Sections table and Status-at-a-glance all
carry it, and `notion-map.json` registers `experiment.md` so the drift check and the weekly sync
routine cover it. Both checkers pass.
