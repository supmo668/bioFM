---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-14T20:21
status: created
priority: normal
size: task
subject: "T8 seal verified independently; T4a PASS and the data path RAN — halted at T5b on 8 unparseable InChIs (0.117%), a plan gap routed to the principal"
in_reply_to: null
---

# T8 seal verified independently; T4a PASS and the data path RAN — halted at T5b on 8 unparseable InChIs (0.117%), a plan gap routed to the principal

# T8 verified independently. Data path RAN for the first time — and halted on a plan gap at T5b

Merged trunk. Reporting by dispatch, not leaving it in the log.

## T8 — verified rather than taken on report

    load_ratified_panel(configs/barrier_panel.yaml)  -> seal VERIFIED
      entries      7
      ratified_by  mo
      ratified_on  2026-09-12
      seal         1aba18e62b017b0c...
      ABCB1        -> P08183

Matches your figures exactly. The seal machinery I built in T7a passes on a real
human ratification, which is the first time it has been exercised outside fixtures.

## T4a PASS — the snapshot has now actually been fetched

    3 TSVs on disk, recomputed sha256 == SHA256SUMS.json  (all three)
    source_commit 3e87872db5fca5ac427ce27464ab945c0ceb4ec6 == the pin
    hash-verify: verified 3 file(s) against the manifest

**Your stop condition did not trigger** — the resolved commit equals the audited
2015 pin, so nothing about the pin was touched. The fetch self-journalled through
S12 (it printed *"delegating to `python -m chipsim.pipeline fetch` so the run is
journalled"*), which is that machinery working unprompted on its first real run.

Real data shape: **7,759 compounds, 19,906 protein edges.** `proteins.tsv` carries
an `actions` column with values including `inhibitor` — so the roster schema's
insistence that `inhibitor` stay separate from `substrate` is already reflected in
the upstream data rather than being an abstraction we impose.

## THE BLOCKER — `chipsim parse` halts, and it is the R4/G1 defect class again

    CanonicalizationError: 8 compound(s) failed canonicalization

**8 of 6,810 compounds carrying an InChIKey — 0.117%.** The full list, because a
blocker without its identifiers cannot be adjudicated:

    DB01929  DB02177  DB02223  DB02377  DB02912  DB03245  DB03304  DB03907

**These are genuinely unparseable, not a display artefact.** I checked the raw TSV
directly: the InChIs are complete in the source. `DB02377` is
`InChI=1S/C5H4N5O/c6-5-9-3-2(4(11)10-5)7-1-8-3/h1H,(H3,6,8,9,10,11)` — intact, and
the pinned RDKit 2026.3.5 refuses it. The truncation appeared only in the error
message, which is itself worth fixing since it made the data look corrupt.

**Why this is a plan gap rather than a bug.** T5b's spec says only *"Adds
`canonical_inchikey`. Raises if any value is null."* and `add_canonical_identity`
does exactly that. But the plan's done-conditions were written against fixtures
that all canonicalize, so **the specification never had to say what happens when
real data does not.** The design has a strong and correct principle — never
silently drop a record — and no stated path for when it fires. Named behaviour,
unspecified branch: the same class as R4's `effect`, G1's radicality metric, and
G2's cost estimator.

**Three options, and they are not equivalent.** Routed to the principal because
each changes what the study *is*:

1. **Refuse the snapshot** — current behaviour. Defensible and makes the study
   impossible on its own pinned data.
2. **Exclude the 8, recorded by ID** in the run journal and on the model card as a
   named exclusion. Consistent with *"an absent result must be visible where the
   result would have been"*, and it changes the cohort definition.
3. **Retain them with `canonical_inchikey = null`** and let downstream joins treat
   them as `unknown` — which **collides with the P-gp `unknown` label**, whose
   whole point is "no evidence" rather than "we could not parse it". This
   programme has defended that distinction repeatedly, so I flag it as the option
   with a hidden cost.

I have not implemented any of them. My read is (2), but the cohort definition is
not mine to change.

## Also from your dispatch

- **`chipsim` PATH defect (C4 recurrence)** — agreed, and the fix is a plan edit:
  T8's command becomes `uv run chipsim panel-seal …`. Flagging for your re-sign
  under the standing delegation rather than editing a signed plan myself.
- **Licence facts carried, not re-derived.** ChEMBL CC BY-SA 3.0 with ShareAlike
  propagating to BindingDB's ChEMBL-sourced portion; UniProt recorded
  `NEEDS_HUMAN_CONFIRMATION` and **I will not fill it from memory** — a provenance
  file recording an unverified licence is precisely the failure it exists to
  prevent.
- **Roster schema read.** One row per (compound, transporter); `interaction` in
  {substrate, inhibitor, non_substrate, unknown}; D1–D9 acceptance criteria noted.
  I will not touch anything roster-shaped.
- **T11 stops at `PROVENANCE.md`**, which is yours/his to write. I will run up to
  it and stop, not draft it.

## Standing

98 tests, ruff clean. Signing hold stands. Gate still NOT clean — 57 findings,
the heaviest being that my own halt-rule tests are tautologies over
`evaluate_halt`'s return value. Four human artifacts remain: `PROVENANCE.md`, the
roster, the P-gp adjudication, `theta_priors.yaml`.
