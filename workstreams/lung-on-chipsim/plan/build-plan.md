# Build Plan — ChipSim M0 Data Spine (slice 1)

**Workstream:** `lung-on-chipsim` · **Module:** `projects/lung-on-chipsim`
**Source:** [Plan — ChipSim M0 Data Spine: Agent vs Human Implementation Roadmap](https://app.notion.com/p/2be47ffc30a34400ab31077cc57b3ffd)
**Implements:** Design §1 and §1.4 only (see Scope check).
**Upstream:** [A&D](../A-and-D.md) · [PVR](../PVR.md)

## Goal

Build the ChipSim data spine through the **compound-identity and barrier-panel layer**,
sourcing DrugBank from a pinned public 2015 snapshot instead of an application-gated licence,
so that M0's contract tests go green with **zero administrative lead time**.

## Architecture

Three actors with a single allocation rule: a coding agent writes anything whose "done" is a
test that can fail, a human owns anything whose output is a *claim*, and ChipSim's own
experiment brain touches none of this until the spine exists. DrugBank enters as a frozen,
provenance-stamped snapshot pulled at build time by commit hash — **never vendored into the
repo** — and contributes drug→transporter edges only, **never affinities**.

## Tech Stack

Python 3.11 · pandas · RDKit · PyYAML · pytest · DVC (data tracking) · requests ·
n8n Community Edition (ETL workflow) · git. **No GPU in this plan.**

## Global Constraints

- **No coding agent writes a biological number.** Every value in `configs/theta_priors.yaml`
  and `configs/assumptions.yaml` is human-entered with a citation. The agent writes the schema
  and the validator that *rejects* an unsourced entry.
- **Non-commercial only.** Inherited from CC BY-NC 4.0 on DrugBank-derived data. Recorded in
  the model card, not assumed.
- **ChipSim never redistributes DrugBank.** Snapshot lands in `data/raw/`, DVC-tracked and git-ignored.
- **Nothing in this plan touches the frozen evaluator.** It does not exist yet; it is built in
  the M0 slice-3 plan and frozen by human signature.
- Every task is one action, 2–5 minutes, with a checkable done condition. **No `TODO`, no `TBD`.**

---

## 1 · The three actors

| Actor | Who it is | Produces | When it acts |
|---|---|---|---|
| **CA · Coding agent** | Claude Code (the `lung-on-chipsim` worktree agent) | repository code, schemas, validators, workflows, tests | build time, now |
| **H · Human** | the principal | curated records, ratified constants, sealed splits, licence posture, freezes | build time, and at every gate |
| **XB · Experiment brain** | ChipSim's runtime orchestrator (A&D §2A) | mechanism diffs, journal entries, wet-condition nominations | **after** the spine and evaluator exist |

> **The allocation rule.** A task is **agent-implementable iff its done-condition is a test that
> can fail.** A task is **human-owned if its output is a claim** — something defended in the model
> card, or something whose wrongness no test in the repository would catch. Curation is human
> because a fabricated record passes every schema check ever written. Parsing is agent because a
> broken parser fails loudly.

**The corollary that shapes the code.** Anything XB may edit at runtime — mechanism hypotheses,
priors, panel composition, link functions — must be **configuration, not code**. If XB would have
to write Python to change a mechanism, the architecture is wrong.

**The anti-pattern this rule prevents.** A coding agent asked to populate `theta_priors.yaml`
will produce fluent, plausible values with citation-shaped strings attached. Some of those
citations will not exist. That is fatal here because θ priors are load-bearing for every
downstream claim.

> **Three things a coding agent may never do, at any phase.** (1) Write a number into
> `theta_priors.yaml` or `assumptions.yaml`. (2) Create, edit or extend a curated chip record.
> (3) Modify the frozen evaluator, the split definitions, or the sealed allocation after signature.

## 2 · Phase ownership map (M0–M6)

| Phase | What gets built | CA builds | H owns | XB |
|---|---|---|---|---|
| **M0a** Data spine | ingest, harmonize, identity, barrier panel | all parsers, contracts, tests, n8n ETL workflow | licence ruling, UniProt panel ratification, P-gp adjudication | — |
| **M0b** Chip-record curation | 60–100 on-domain records, sealed allocation | the schema, the sealing tool, the hash ledger | **every record, every seal** | — |
| **M0c** Frozen evaluator | splits, metrics, three controls | all of it | **ratifies and signs the freeze** | — |
| **M1** ODE core | solver, θ plumbing, fit routine | solver and fit code | the priors, with citations | — |
| **M2** ADME heads | P1–P3, CV harness | all of it | accepts/rejects the ρ ≥ 0.6 gate | — |
| **M3** Occupancy engine | Boltz-2 wrapper, Hill transform, cache | all of it | panel composition | first diffs proposed here |
| **M4** Readout head | one channel, FiLM conditioning, adversary | all of it | picks the channel; reads adversary result | proposes |
| **M5** Uncertainty stack | L0–L3 as amended | all of it | **pre-registers the two P-gp groups before any coverage is computed** | proposes |
| **M6** Acquisition | BALD, diversity, replay harness | all of it | releases sealed records on schedule | proposes and ranks |

## 3 · The DrugBank ruling

**Decision.** Use **dhimmel/drugbank** — a public snapshot of **DrugBank 4.2, downloaded
2015-03-19**, archived at `doi:10.5281/zenodo.45579`, redistributed as derived TSVs under
**CC BY-NC 4.0** (original repo content CC0 1.0). Take **compound identity and
drug→transporter/carrier edges only. Never affinities.**

**What the snapshot gives:** `data/drugbank.tsv` (identity, approved-status filter) ·
`data/drugbank-slim.tsv` (approved small molecules → the PoC shortlist) · `data/proteins.tsv`
(drug→protein edges categorised target/enzyme/**transporter**/**carrier** — *the barrier panel
layer, the reason to use this at all*) · `data/pubchem-mapping.tsv` · `data/mapping.tsv.gz`
(UniChem → 30 resources, joins to ChEMBL without writing a resolver).

**What it does not give:** no binding affinities (those come from ChEMBL/BindingDB/Papyrus),
no approvals after 2015, no current transporter annotations.

**Staleness ruling.** DrugBank 4.2 is eleven years behind 5.1.22. Acceptable **here and only
here** because the PoC compound set is well-characterised reference compounds whose transporter
annotations are stable. The snapshot **cannot support any coverage claim** — the model card must
say **DrugBank 4.2 (2015-03-19 snapshot)** everywhere it says DrugBank.

> **🚨 The collision nobody would notice until M5.** The uncertainty stack conditions Mondrian
> coverage on **P-gp substrate status** — the pre-registered grouping variable the calibration
> veto fires on. If that label is derived from a 2015 snapshot by a script, **a stale annotation
> silently redefines the groups the entire coverage claim is conditioned on**, and a coverage
> failure will look like miscalibration when it is actually mislabelling. Three mandatory
> consequences: the label is derived **three-way (yes / no / unknown)**; absence of an edge is
> **never** read as "not a substrate"; every group assignment for the PoC compound set is
> **adjudicated by H against current literature** before pre-registration (~20–40 judgements).

---

## 4 · Tasks — M0 slice 1

Each task is one action. Done conditions are checkable.

### T1 · Ratify the licence posture — **H · 5 min**
Read the two licence statements (CC BY-NC 4.0 on the derived data; DrugBank ToS) and write the
decision, in your own words, into the provenance file. Include the non-commercial commitment and
the three attribution strings.
- **Files:** `data/raw/drugbank/PROVENANCE.md` (new, hand-written)
- **Interfaces** — must contain these four fields, checked by T11:
  ```
  source_repo:    https://github.com/dhimmel/drugbank
  source_commit:  <40-char hash, pinned in T2>
  upstream:       DrugBank 4.2, downloaded 2015-03-19
  licence:        CC BY-NC 4.0 (DrugBank content and derivatives)
  attribution:    Wishart et al., Nucleic Acids Res (2014), doi:10.1093/nar/gkt1068
                  Himmelstein et al., Zenodo, doi:10.5281/zenodo.45579
                  Licence discussion: doi:10.15363/thinklab.d213
  ```
- **Done when** the file exists and states a non-commercial commitment in a sentence you would defend.

### T2 · Pin the snapshot commit — **H · 2 min**
Resolve the current head of the repository's `gh-pages` branch to a full 40-character SHA and
paste it into `PROVENANCE.md`. The commit observed during the access audit was
`3e87872db5fca5ac427ce27464ab945c0ceb4ec6`; confirm or replace it.
- **Done when** `source_commit` is a 40-character hash you personally resolved.

### T3 · Write the fetch script — **CA · 5 min**
- **Files:** `chipsim/ingest/drugbank_snapshot.py` (new)
- **Interfaces:**
  ```python
  SNAPSHOT_FILES = (
      "data/drugbank.tsv",
      "data/drugbank-slim.tsv",
      "data/proteins.tsv",
      "data/pubchem-mapping.tsv",
  )

  def fetch_snapshot(dest: Path, commit: str) -> dict[str, str]:
      """Download SNAPSHOT_FILES from raw.githubusercontent at `commit`.
      Returns {relative_path: sha256}. Raises if `commit` is not 40 hex chars.
      Never writes outside `dest`.
      """
  ```
- **Done when** `fetch_snapshot` raises `ValueError` on a short commit string and returns four hashes on a valid one.

### T4 · Add the snapshot to DVC, not to git — **CA · 3 min**
Add `data/raw/drugbank/` to DVC tracking and confirm it is covered by `.gitignore`. This is the
technical control that keeps ChipSim from becoming a redistributor.
- **Files:** `.gitignore` (edit: add `data/raw/`) · `data/raw/drugbank.dvc` (new, generated)
- **Done when** `git status` shows no TSV files after a fetch.

### T5 · Parse the compound table — **CA · 5 min**
- **Files:** `chipsim/ingest/drugbank_snapshot.py` (edit)
- **Interfaces:**
  ```python
  def load_compounds(raw_dir: Path) -> pd.DataFrame:
      """Columns: drugbank_id, name, type, groups (list[str]),
      atc_codes (list[str]), inchi, inchikey.
      Drops rows with no InChIKey. Does not canonicalise — that is harmonize/ids.py.
      """
  ```
- **Done when** the frame has a non-null `inchikey` on every row and `groups` is a list, not a pipe-joined string.

### T6 · Parse the protein-edge table — **CA · 5 min**
- **Interfaces:**
  ```python
  def load_protein_edges(raw_dir: Path) -> pd.DataFrame:
      """Columns: drugbank_id, uniprot_id, category, organism.
      `category` is one of target, enzyme, transporter, carrier.
      Filters to organism == 'Homo sapiens'.
      """
  ```
- **Done when** `set(df.category)` is a subset of the four documented values.

### T7 · Draft the barrier panel accession list — **CA · 3 min**
Write the panel file with the accessions below, each marked `ratified: false`. CA drafts; H
ratifies in T8. A wrong accession silently empties a join and produces an *empty* rather than
*wrong* result — the hardest kind of bug to see.
- **Files:** `configs/barrier_panel.yaml` (new)
- **Interfaces:**
  ```yaml
  # ratified: false  — H must flip this after checking every accession
  panel:
    - {symbol: ABCB1,   uniprot: P08183, alias: "P-gp / MDR1",  face: apical}
    - {symbol: ABCG2,   uniprot: Q9UNQ0, alias: "BCRP",         face: apical}
    - {symbol: ABCC1,   uniprot: P33527, alias: "MRP1",         face: basolateral}
    - {symbol: TFRC,    uniprot: P02786, alias: "TfR1",         face: apical}
    - {symbol: FCGRT,   uniprot: P55899, alias: "FcRn",         face: apical}
    - {symbol: SLC15A1, uniprot: P46059, alias: "PepT1",        face: apical}
    - {symbol: SLCO2B1, uniprot: O94956, alias: "OATP2B1",      face: basolateral}
  ```
- **Done when** the file parses and every entry carries `symbol`, `uniprot`, `alias` and `face`.

### T8 · Ratify the panel accessions — **H · 10 min**
Check each of the seven accessions against UniProt by hand. Correct any that are wrong, delete
any not expressed in airway epithelium, then set `ratified: true`.
- **Done when** `ratified: true` and you have personally opened seven UniProt pages.

### T9 · Join edges to the panel — **CA · 4 min**
- **Interfaces:**
  ```python
  def barrier_panel_edges(edges: pd.DataFrame, panel_path: Path) -> pd.DataFrame:
      """Inner-join protein edges onto the ratified panel.
      Raises RuntimeError if the panel file has ratified: false.
      Columns: drugbank_id, uniprot_id, symbol, category, face.
      """
  ```
- **Done when** calling it against an unratified panel raises, and against a ratified one returns a non-empty frame.

### T10 · Derive the three-way P-gp label — **CA · 5 min**
- **Files:** `chipsim/harmonize/pgp_label.py` (new)
- **Interfaces:**
  ```python
  def pgp_substrate_label(
      compounds: pd.DataFrame,
      panel_edges: pd.DataFrame,
  ) -> pd.Series:
      """Index: inchikey. Values: 'yes' | 'unknown'.

      'yes'      -> an ABCB1 (P08183) transporter edge exists in the snapshot.
      'unknown'  -> no edge. NEVER returns 'no' from absence of evidence.

      'no' is assignable only by adjudicate_pgp_labels() with a citation.
      """
  ```
- **Done when** the function cannot emit `'no'` — asserted in T12.

### T11 · Write the provenance contract test — **CA · 4 min**
- **Files:** `tests/test_contracts.py` (edit)
- **Interfaces:**
  ```python
  def test_drugbank_provenance_complete():
      """PROVENANCE.md has all four fields; source_commit matches ^[0-9a-f]{40}$;
      fetched file hashes equal those recorded at fetch time."""

  def test_drugbank_not_vendored():
      """No .tsv under data/raw/ is tracked by git."""
  ```
- **Done when** both tests pass, and `test_drugbank_not_vendored` fails if you `git add -f` a TSV.

### T12 · Write the label-safety test — **CA · 3 min**
- **Interfaces:**
  ```python
  def test_pgp_label_never_infers_negative():
      """Given a compound with zero protein edges, the label is 'unknown', not 'no'."""

  def test_pgp_label_domain():
      """set(labels) is a subset of {'yes', 'unknown'} before adjudication."""
  ```
- **Done when** both pass.

### T13 · Emit the adjudication worksheet — **CA · 4 min**
- **Interfaces:**
  ```python
  def write_adjudication_worksheet(labels: pd.Series, out: Path) -> int:
      """Write a CSV: inchikey, name, snapshot_label, adjudicated_label,
      evidence_doi, adjudicated_by, adjudicated_on.
      Last four columns empty for H to fill. Returns row count.
      """
  ```
- **Files:** `data/interim/pgp_adjudication.csv` (generated, empty verdict columns)
- **Done when** the CSV has one row per PoC compound and four empty columns.

### T14 · Adjudicate the P-gp labels — **H · 60–90 min**
Fill `adjudicated_label` and `evidence_doi` for every row. This is the task that makes the M5
grouping variable trustworthy, and it **cannot be delegated** — a fabricated DOI here would
corrupt the coverage claim invisibly. Leave genuinely uncertain compounds as `unknown`; they are
**excluded from both calibration groups** rather than guessed into one.
- **Done when** every row has a verdict and a DOI, or an explicit `unknown`.

### T15 · Load adjudicated labels with provenance — **CA · 4 min**
- **Interfaces:**
  ```python
  def adjudicate_pgp_labels(worksheet: Path) -> pd.Series:
      """Index: inchikey. Values: 'yes' | 'no' | 'unknown'.
      Raises if any 'yes'/'no' row lacks evidence_doi or adjudicated_by.
      """
  ```
- **Done when** a row labelled `no` with an empty DOI raises.

### T16 · Wire the n8n ETL workflow — **CA · 5 min**
One workflow, five nodes: fetch → hash-verify → parse → contract tests → write `data/processed/`.
Export the JSON to the repo so the pull is replayable.
- **Files:** `orchestration/n8n/etl_drugbank.json` (new, exported)
- **Done when** a fresh clone plus the workflow reproduces `data/processed/compounds.parquet` byte-identically.

### T17 · Add the model-card provenance block — **CA · 3 min**
- **Files:** `chipsim/eval/card.py` (edit)
- **Interfaces:** the card gains a `data_provenance` section rendering source, commit, upstream
  version, snapshot date, licence, and the P-gp adjudication counts as `yes / no / unknown`.
- **Done when** a rendered card shows **DrugBank 4.2 (2015-03-19 snapshot)** and the three label counts.

---

## 5 · Scope check

This plan stops at the identity and barrier-panel layer: **17 tasks, roughly 3 hours of agent
work and 2 hours of human work** — one sitting.

Three adjacent things are **deliberately not here**:

1. **M0b — curation of 60–100 chip records.** Human-only, needs a protocol document rather than a task list, and it is the project's critical path. Its own plan.
2. **M0c — the frozen evaluator.** Cannot be specified until the splits exist, and it needs a human signature ceremony that does not belong in a data-ingest plan. Its own plan.
3. **ChEMBL, BindingDB, TDC, LINCS ingestion.** Same shape as T3–T6 repeated four times, no new decisions. One plan covering all four, after this one proves the pattern.

> **The next plan should be M0b, not the other ingestors.** The ingestion pattern is now proven
> and mechanical; curation is unproven, human-bound, and gates M5 and M6 both. Building more
> parsers first would feel productive and would move the actual completion date not at all.

---

## Agent execution notes (AIADLC)

- **CA tasks (T3–T7, T9–T13, T15–T17)** are the worktree agent's build scope — 13 tasks, each with a failing-test done-condition (17 total − 4 human-owned).
- **H tasks (T1, T2, T8, T14)** are blockers the agent must **escalate, not simulate**. T1/T2 gate T11; T8 gates T9; T14 gates T15. The agent builds the code and tests around them, leaves the human artifacts absent, and reports the blocked set at the boundary.
- **The hard rule stands:** no agent-written biological numbers, no agent-created curated records, no agent edits to the frozen evaluator. T7's panel is drafted `ratified: false` **by design** — drafting accessions is allowed; ratifying them is not.
