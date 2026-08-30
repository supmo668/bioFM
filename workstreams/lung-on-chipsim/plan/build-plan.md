# Build Plan — ChipSim M0 Data Spine (slice 1)

**Workstream:** `lung-on-chipsim` · **Module:** `projects/lung-on-chipsim` (project root — every `Files:` path below is relative to it, per A&D AM-4)
**Source:** [Plan — ChipSim M0 Data Spine: Agent vs Human Implementation Roadmap](https://app.notion.com/p/2be47ffc30a34400ab31077cc57b3ffd)
**Implements:** the DrugBank clause of Design §1's S1 layer + §1.4's access ruling (see Scope check and A&D amendment AM-5). **Not** §1.2 beyond identity, **not** §1.3 splits/leakage, **not** S2–S8.
**Upstream:** [A&D](../A-and-D.md) · [PVR](../PVR.md)
**Revision:** r2 — 33 plan-validity defects and the scaffold hole folded in. See §7 Revision log.

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

Python 3.11 · pandas · **pyarrow (pinned — parquet engine; T5a/T15 write parquet)** · RDKit
(**used by T5b for canonical identity**) · PyYAML · pytest · DVC (data tracking) · requests ·
n8n Community Edition (ETL workflow export) · git. **No GPU in this plan.**

## Global Constraints

- **No coding agent writes a biological number.** Every value in `configs/theta_priors.yaml`
  and `configs/assumptions.yaml` is human-entered with a citation. The agent writes the schema
  and the validator that *rejects* an unsourced entry.
- **No coding agent curates the compound roster.** Which compounds are lung-relevant is a
  *claim* (T18), not a filter result. The agent writes the schema and the validator.
- **Non-commercial only.** Inherited from CC BY-NC 4.0 on DrugBank-derived data. Recorded in
  the model card, not assumed.
- **ChipSim never redistributes DrugBank.** Snapshot lands in `data/raw/`, DVC-tracked and git-ignored.
- **Nothing in this plan touches the frozen evaluator.** It does not exist yet; it is built in
  the M0 slice-3 plan and frozen by human signature.
- Every task is one action with a checkable done condition. **No `TODO`, no `TBD`.**
- **Every CA done-condition must be evaluable without a human artifact.** Where a task's real
  input is human-gated (T1/T2/T8/T14/T18), its done-condition runs against a committed fixture
  under `tests/fixtures/`; the live-data check is a separate *integration* condition, explicitly
  deferred and reported at the human boundary. (Defect 33.)

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
to write Python to change a mechanism, the architecture is wrong. **This is why T10 resolves the
ABCB1 accession from `barrier_panel.yaml` rather than hard-coding it** (defect 4 / AM-2).

**The anti-pattern this rule prevents.** A coding agent asked to populate `theta_priors.yaml`
will produce fluent, plausible values with citation-shaped strings attached. Some of those
citations will not exist. That is fatal here because θ priors are load-bearing for every
downstream claim.

> **Three things a coding agent may never do, at any phase.** (1) Write a number into
> `theta_priors.yaml` or `assumptions.yaml`. (2) Create, edit or extend a curated chip record,
> or the curated compound roster. (3) Modify the frozen evaluator, the split definitions, or the
> sealed allocation after signature.

## 2 · Phase ownership map (M0–M6)

| Phase | What gets built | CA builds | H owns | XB |
|---|---|---|---|---|
| **M0a** Data spine | ingest, harmonize, identity, barrier panel | all parsers, contracts, tests, n8n ETL workflow | licence ruling, UniProt panel ratification, compound roster, P-gp adjudication | — |
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
`data/drugbank-slim.tsv` (approved small molecules → **the candidate pool**, *not* the PoC set —
see below) · `data/proteins.tsv` (drug→protein edges categorised target/enzyme/**transporter**/
**carrier** — *the barrier panel layer, the reason to use this at all*) · `data/pubchem-mapping.tsv`
· `data/mapping.tsv.gz` (UniChem → 30 resources).

> **Candidate pool ≠ PoC compound set.** `drugbank-slim.tsv` is an automatic approved-small-molecule
> filter of order 10³ rows. The **PoC compound set is the 20–40 hand-curated lung-relevant compounds
> of PVR §4 / CONTEXT.md**, and it is produced by **T18 (H)**, never by a filter. Conflating the two
> made T13's done-condition uncheckable and mis-estimated T14's human cost by ~50×. (Defect 3.)

**Not fetched in slice 1:** `mapping.tsv.gz` and `pubchem-mapping.tsv` are consumed by no task
here; they arrive with the ChEMBL plan. `SNAPSHOT_FILES` fetches three files, not four. (Minor note D.)

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

## 4 · Execution order

Scaffold first, then provenance, then data. **T2 precedes T1** (T1 records the hash T2 resolves —
defect 16). The fetch is an explicit task (T4a), not an assumption (defect 8).

| Phase | Tasks | Gate |
|---|---|---|
| **P0 · Scaffold** | S1 → S2 → S3 → S4 → S5 → S6 → S7 → S8 → S9 → S10 → S11 | `pip install -e . && pytest --collect-only` exits 0 |
| **P1 · Provenance & fetch** | T2(H) → T1(H) → T3 → T4a → T4 → T11 | provenance tests green against fixtures |
| **P2 · Parse & identity** | T5 → T5b → T5a → T6 | compound frame persists with canonical InChIKey |
| **P3 · Barrier panel** | T7 → T19 → T8(H) → T9 | panel join non-empty against a ratified fixture |
| **P4 · P-gp labels** | T10 → T12 → S11a → T18(H) → T13 → T14(H) → T15 | label domain + group-population checks green |
| **P5 · Card & ETL** | T17 → T16 | provenance block renders; workflow JSON validates |

**T4a precedes T4** — `dvc add` has nothing to track until the fetch has run.
**S11a precedes T18** — the roster validator must exist before the human fills the roster, so a
malformed entry fails immediately rather than after 45 minutes of curation.

---

## 5 · Scaffold tasks — S1–S11 (CA, run before everything)

> **Why these exist.** Ten of the seventeen original tasks wrote under directories that no task
> created, and four required tools were never installed or configured. Verified on the branch:
> `projects/lung-on-chipsim/` contains only `CONTEXT.md`, `.aiadlc-agent` and `.claude/`. S-ids are
> used so every original T-id stays stable for SYN-271.

### S1 · Create the package skeleton — **CA · 4 min**
- **Files:** `chipsim/__init__.py` (new) and `__init__.py` under `ingest/ harmonize/ encoders/ heads/ transport/ occupancy/ surface/ uncertainty/ eval/ acquire/` (new), per A&D §4.4 + AM-4
- **Done when** `python -c "import chipsim, chipsim.ingest, chipsim.harmonize, chipsim.eval"` exits 0 from the project root, and exits non-zero if any `__init__.py` is removed.

### S2 · Write `pyproject.toml` with the full dependency set — **CA · 5 min**
**`pyarrow` is included because T5a/T15 write parquet and the original Tech Stack omitted a parquet
engine (defect 26); its version is pinned because parquet bytes are not stable across versions
(defect 27).**
- **Files:** `pyproject.toml` (new)
- **Interfaces:** `requires-python = ">=3.11,<3.13"`; dependencies `pandas`, `pyarrow==<pinned>`,
  `PyYAML`, `requests`, `rdkit`; dev group `pytest`, `pytest-cov`, `ruff`, `dvc`
- **Done when** `pip install -e .` succeeds and `python -c "import pandas, pyarrow, yaml, requests, rdkit"` exits 0.

### S3 · Configure pytest — **CA · 2 min**
- **Files:** `pyproject.toml` (edit: `[tool.pytest.ini_options]`, `testpaths = ["tests"]`, markers `network`, `integration`)
- **Done when** `pytest --collect-only` exits 0 from the project root; exits non-zero if `testpaths` is removed.

### S4 · Create the test package and the day-one modules — **CA · 4 min**
A&D §4.4 requires the three day-one tests. **`test_provenance.py` is a new file, distinct from
`test_contracts.py`** — §4.4 reserves `test_contracts.py` for the §1.2 *data*-contract test, and
T11's provenance checks are a different kind (defect 29).
- **Files:** `tests/conftest.py` (new, `project_root` + fixture loaders) · `tests/test_provenance.py` · `tests/test_contracts.py` · `tests/test_leakage.py` · `tests/test_monotonicity.py` (new; leakage and monotonicity carry `pytest.mark.skip(reason="M0 slice 3 — splits/ODE not yet built")`)
- **Done when** `pytest --collect-only` discovers all four modules and `conftest.py`'s fixtures resolve.

### S5 · Create the committed test fixtures — **CA · 5 min**
These make every human-gated CA done-condition evaluable (Global Constraints / defect 33). They are
**fixtures, not simulated human artifacts** — they live under `tests/`, never under `configs/` or
`data/`, and no pipeline path reads them.
- **Files:** `tests/fixtures/barrier_panel_ratified.yaml` · `tests/fixtures/barrier_panel_unratified.yaml` · `tests/fixtures/provenance.yaml` · `tests/fixtures/pgp_adjudication_filled.csv` · `tests/fixtures/pgp_adjudication_blank.csv` · `tests/fixtures/poc_compounds.yaml` (new)
- **Done when** every fixture parses, and `test_fixtures_are_not_configs` asserts no fixture path is referenced outside `tests/`.

### S6 · Create `configs/` — **CA · 2 min**
Only the non-biological file is written. `theta_priors.yaml` and `assumptions.yaml` are
**deliberately absent** — H-owned, no agent may create them.
- **Files:** `configs/env.yaml` (new) · `configs/.gitkeep`
- **Done when** `configs/env.yaml` parses as YAML, and `configs/theta_priors.yaml` and `configs/assumptions.yaml` do **not** exist.

### S7 · Create the data tree and the project `.gitignore` — **CA · 3 min**
The ignore rule must **not** swallow the `.dvc` pointer files, which are the one thing that must be
committed (defect 10c).
- **Files:** `data/raw/.gitkeep` · `data/interim/.gitkeep` · `data/processed/.gitkeep` · `.gitignore` (**new** — per AM-4 this is `projects/lung-on-chipsim/.gitignore`, which did not exist) containing `data/raw/*`, `data/interim/*`, `data/processed/*`, plus `!*.dvc`, `!.gitkeep`, `!data/processed/*.sha256`
- **Done when** `git check-ignore -q data/raw/probe.tsv` exits 0, and `git check-ignore -q data/raw/drugbank.dvc` exits **1**.

### S8 · Initialize DVC — **CA · 3 min**
`dvc init --subdir` is required because the project root is a subdirectory of an existing git repo
(defect 10b). Without this, T4's done-condition is unfalsifiable.
- **Files:** `.dvc/config` (new, generated) · `.dvcignore`
- **Done when** `.dvc/config` exists **and** `dvc status` exits 0.

### S9 · Configure a DVC remote — **CA · 2 min**
Nothing in r1 configured storage, so `dvc pull` could never succeed (defect 11).
- **Files:** `.dvc/config` (edit: `dvc remote add -d local ../../.dvc-storage`)
- **Done when** `dvc remote list` names a default remote and `dvc push` followed by `dvc pull` on a clean cache round-trips the snapshot.

### S10 · Create `orchestration/n8n/` — **CA · 1 min**
- **Files:** `orchestration/n8n/.gitkeep` (new)
- **Done when** the directory exists and is tracked by git.

### S11 · Create the module files every later task marks "(edit)" — **CA · 3 min**
T3/T5/T6 edit `drugbank_snapshot.py`; T10 edits `pgp_label.py`; T5b edits `ids.py`; T17 edits the
provenance block. None existed (defects 12, 13).
- **Files:** `chipsim/ingest/drugbank_snapshot.py` · `chipsim/harmonize/ids.py` · `chipsim/harmonize/pgp_label.py` · `chipsim/harmonize/contracts.py` · `chipsim/eval/provenance_block.py` (all new, empty or stub)
- **Done when** all five import cleanly.

---

## 6 · Tasks — M0 slice 1

### T2 · Pin the snapshot commit — **H · 2 min** *(now first — defect 16)*
Resolve the current head of the repository's `gh-pages` branch to a full 40-character SHA. The
commit observed during the §1.4 access audit was `3e87872db5fca5ac427ce27464ab945c0ceb4ec6`.
Record **both** values: if you replace it, you must say why (defect 17).
- **Interfaces** — written into `data/raw/drugbank/provenance.yaml`:
  ```yaml
  source_commit:            <40-hex, the one you resolved>
  audited_commit:           3e87872db5fca5ac427ce27464ab945c0ceb4ec6
  commit_change_rationale:  ""   # REQUIRED non-empty if source_commit != audited_commit
  ```
- **Done when** `source_commit` matches `^[0-9a-f]{40}$` and, if it differs from `audited_commit`, `commit_change_rationale` is non-empty.

### T1 · Ratify the licence posture — **H · 5 min**
Read the two licence statements (CC BY-NC 4.0 on the derived data; DrugBank ToS) and write the
decision in your own words. **The artifact is split in two** (defect 15): a structured YAML that
T11 can parse, and your prose.
- **Files:** `data/raw/drugbank/provenance.yaml` (edit — structured) · `data/raw/drugbank/PROVENANCE.md` (new, hand-written prose)
- **Interfaces** — `provenance.yaml` must carry, in addition to T2's three keys:
  ```yaml
  source_repo:      https://github.com/dhimmel/drugbank
  upstream_version: "4.2"          # structured, NOT a display string — defect 14
  snapshot_date:    "2015-03-19"
  licence:          CC BY-NC 4.0 (DrugBank content and derivatives)
  attribution:                      # a list, so it parses
    - Wishart et al., Nucleic Acids Res (2014), doi:10.1093/nar/gkt1068
    - Himmelstein et al., Zenodo, doi:10.5281/zenodo.45579
    - Licence discussion: doi:10.15363/thinklab.d213
  non_commercial_commitment: "<one sentence you would defend>"
  ```
- **Done when** `yaml.safe_load` yields all eight keys non-empty, `attribution` has three entries, and `PROVENANCE.md` exists.

### T3 · Write the fetch script — **CA · 5 min**
- **Files:** `chipsim/ingest/drugbank_snapshot.py` (edit)
- **Interfaces:**
  ```python
  SNAPSHOT_FILES = ("drugbank.tsv", "drugbank-slim.tsv", "proteins.tsv")

  def fetch_snapshot(dest: Path, commit: str) -> dict[str, str]:
      """Download SNAPSHOT_FILES from raw.githubusercontent at `commit`, writing each
      to `dest/<basename>` — FLAT, no nested data/ level (defect 7).
      Returns {basename: sha256}.
      Also writes `dest/SHA256SUMS.json` (git-tracked, NOT DVC):
        {"source_commit": <40-hex>, "fetched_utc": <iso8601>, "files": {<basename>: <sha256>}}
      Raises ValueError unless `commit` matches ^[0-9a-f]{40}$.
      Never writes outside `dest`; leaves `dest` untouched when it raises.
      """
  ```
- **Done when** it raises `ValueError` on a 39-char string **and** on a 40-char non-hex string (defect 32), leaves `dest` empty in both cases, and on a valid commit returns three hashes with `SHA256SUMS.json` matching the files on disk.

### T4a · Run the pinned fetch — **CA · 2 min** *(new — defect 8)*
r1 had no task that actually pulled the data, yet T4–T10 all presumed it existed. It runs **before**
T4, because `dvc add` has nothing to track until the snapshot is on disk.
- **Interfaces:** `python -m chipsim.ingest.drugbank_snapshot --dest data/raw/drugbank --commit <source_commit from provenance.yaml>`
- **Done when** the three TSVs exist under `data/raw/drugbank/` and their recomputed sha256s equal `SHA256SUMS.json`.
- **Blocked-by:** T2 (the commit). Until T2 lands, the *unit* done-conditions of T3 run against fixtures; this task is reported blocked.

### T4 · Track the snapshot in DVC, not git — **CA · 4 min**
- **Files:** `data/raw/drugbank.dvc` (new, generated by `dvc add`)
- **Done when** all four hold (defects 5, 10):
  (a) `git status --porcelain` lists no `.tsv`;
  (b) `data/raw/drugbank.dvc` exists, **is tracked by git**, parses as YAML with a non-empty `outs[0].md5`;
  (c) `dvc status data/raw/drugbank.dvc` reports up-to-date;
  (d) `SHA256SUMS.json` is tracked by git.

### T11 · Write the provenance contract tests — **CA · 5 min**
Lives in `tests/test_provenance.py`, **not** `tests/test_contracts.py` — §4.4 reserves the latter
for the §1.2 *data*-contract test, which arrives with the ChEMBL plan (defect 29).
- **Files:** `tests/test_provenance.py` (edit)
- **Interfaces:**
  ```python
  def test_provenance_complete():
      """provenance.yaml parses and carries all eight keys non-empty;
      source_commit matches ^[0-9a-f]{40}$; attribution has three entries."""

  def test_provenance_commit_substitution_is_justified():
      """source_commit == audited_commit, OR commit_change_rationale is non-empty
      (defect 17) — a silent snapshot swap fails here."""

  def test_snapshot_hashes_match_manifest():
      """Recomputed sha256 of each fetched file equals SHA256SUMS.json (defect 2).
      Fails if any fetched file is mutated after fetch."""

  def test_drugbank_not_vendored():
      """`git ls-files` matches no .tsv under data/raw/ — recursive, so a nested
      layout cannot hide one (defect 7)."""

  def test_dvc_pointer_is_tracked():
      """data/raw/drugbank.dvc IS tracked by git — the blanket ignore must not
      swallow the one file that makes the snapshot recoverable (defect 10c)."""
  ```
- **Done when** all five pass against `tests/fixtures/provenance.yaml`, `test_drugbank_not_vendored` fails if you `git add -f` a TSV, and `test_dvc_pointer_is_tracked` fails if the pointer is untracked.
- **Blocked-by:** T1/T2 for the *live* provenance file; the unit conditions above run against the fixture.

### T5 · Parse the compound table — **CA · 5 min**
- **Files:** `chipsim/ingest/drugbank_snapshot.py` (edit)
- **Interfaces:**
  ```python
  def load_compounds(raw_dir: Path) -> pd.DataFrame:
      """`raw_dir` contains drugbank.tsv, drugbank-slim.tsv, proteins.tsv at its TOP LEVEL.
      Columns: drugbank_id, name, type, groups (list[str]),
      atc_codes (list[str]), inchi, inchikey.
      Drops rows with no InChIKey. Does not canonicalise — that is T5b / harmonize/ids.py.
      """
  ```
- **Done when** `df.inchikey.notna().all()`, `groups` is a list rather than a pipe-joined string, **and `len(df) > 1000`** — the row-count floor is what makes the condition non-vacuous on an empty frame (defect 9).

### T5b · Canonicalize compound identity — **CA · 5 min** *(new — defect 31)*
A&D §1.2 requires "canonical InChIKey from RDKit after salt stripping, neutralization, tautomer
canonicalization. **Never join on name or raw SMILES.**" r1 declared RDKit in the stack and used it
nowhere, so the plan's own Goal — "through the compound-identity layer" — was unmet while all 17
done-conditions passed.
- **Files:** `chipsim/harmonize/ids.py` (edit)
- **Interfaces:**
  ```python
  def canonical_inchikey(inchi: str) -> str:
      """RDKit: salt strip -> neutralize -> tautomer canonicalize -> InChIKey."""

  def add_canonical_identity(compounds: pd.DataFrame) -> pd.DataFrame:
      """Adds `canonical_inchikey`. Raises if any value is null."""
  ```
  **T10, T13 and T15 index on `canonical_inchikey`, not the raw snapshot key.**
- **Done when** a known salt / free-base pair collapses to one `canonical_inchikey`, the column is non-null on every row, and a raw-vs-canonical disagreement count is reported.

### T5a · Persist the compound frame — **CA · 3 min** *(new — defect 26)*
- **Interfaces:**
  ```python
  def write_compounds(df: pd.DataFrame, out: Path) -> None:
      """Declared column order and dtypes, sorted by canonical_inchikey.
      pyarrow, version='2.6', compression=None."""
  ```
- **Files:** `data/processed/drugbank_compounds.parquet` — **not** `compounds.parquet`, which A&D §1
  reserves for the harmonized multi-source S1 artifact `(InChIKey, SMILES, logP, pKa, MW, TPSA)`
  (defect 30)
- **Done when** the parquet round-trips to a frame identical to the input, and `data/processed/drugbank_compounds.sha256` (git-tracked) records its digest.

### T6 · Parse the protein-edge table — **CA · 5 min**
- **Interfaces:**
  ```python
  def load_protein_edges(raw_dir: Path) -> pd.DataFrame:
      """Columns: drugbank_id, uniprot_id, category, organism.
      `category` is one of target, enzyme, transporter, carrier.
      Filters to organism == 'Homo sapiens'.
      """
  ```
- **Done when** `len(df) > 0`, `set(df.category) == {target, enzyme, transporter, carrier}` (**equality, not subset** — defect 9), and a golden-row assertion holds: a named reference drug with a known ABCB1 transporter edge is present. The golden row is what catches a silent species-filter mismatch that empties the frame.

### T7 · Draft the barrier panel accession list — **CA · 3 min**
`ratified` is a **real, file-level** key — not a comment, not per-entry (defects 1, 18). A wrong
accession silently empties a join and produces an *empty* rather than *wrong* result.
- **Files:** `configs/barrier_panel.yaml` (new)
- **Interfaces:**
  ```yaml
  ratified: false        # real top-level key; H flips it in T8
  ratified_by: ""
  ratified_on: ""
  panel:
    - {symbol: ABCB1,   uniprot: P08183, alias: "P-gp / MDR1",  face: apical}
    - {symbol: ABCG2,   uniprot: Q9UNQ0, alias: "BCRP",         face: apical}
    - {symbol: ABCC1,   uniprot: P33527, alias: "MRP1",         face: basolateral}
    - {symbol: TFRC,    uniprot: P02786, alias: "TfR1",         face: apical}
    - {symbol: FCGRT,   uniprot: P55899, alias: "FcRn",         face: apical}
    - {symbol: SLC15A1, uniprot: P46059, alias: "PepT1",        face: apical}
    - {symbol: SLCO2B1, uniprot: O94956, alias: "OATP2B1",      face: basolateral}
  ```
- **Done when** `yaml.safe_load(...)["ratified"] is False` (a *parsed boolean*, which the r1 comment form could never satisfy) and every entry carries `symbol`, `uniprot`, `alias`, `face`.

### T19 · Write the panel verification script — **CA · 4 min** *(new — defect 19)*
T8's r1 done-condition was pure attestation ("you have personally opened seven UniProt pages"),
leaving the barrier panel's only control unverifiable. This gives T8 a checkable surrogate.
- **Files:** `tests/test_barrier_panel.py` (new, `pytest.mark.network`)
- **Interfaces:** for every entry, assert `rest.uniprot.org/uniprotkb/<acc>.json` resolves, `organism.taxonId == 9606`, and the primary gene name equals the entry's `symbol`.
- **Done when** the test passes against `tests/fixtures/barrier_panel_ratified.yaml` and **fails** when one accession is mutated to a valid-but-wrong human accession.

### T8 · Ratify the panel accessions — **H · 10 min**
Check each accession against UniProt. Correct any that are wrong, delete any not expressed in
airway epithelium, then set `ratified: true` and fill `ratified_by` / `ratified_on`.
- **Done when** `ratified: true`, `ratified_by` and `ratified_on` are non-empty, **and T19 passes against the live file** (defect 19).
- **Note for T10:** if you delete or re-accession ABCB1, T10 now raises rather than silently labelling everything `unknown` (defect 4).

### T9 · Join edges to the panel — **CA · 4 min**
- **Interfaces:**
  ```python
  def barrier_panel_edges(edges: pd.DataFrame, panel_path: Path) -> pd.DataFrame:
      """Inner-join protein edges onto the ratified panel.
      Raises RuntimeError unless ratified is True AND ratified_by is non-empty.
      A MISSING `ratified` key raises — absence is not consent (defect 1).
      Columns: drugbank_id, uniprot_id, symbol, category, face.
      """
  ```
- **Done when** it raises on `ratified: false`, raises on a file with the key **absent**, raises on `ratified: true` with an empty `ratified_by`, and returns a non-empty frame against `tests/fixtures/barrier_panel_ratified.yaml`.

### T10 · Derive the three-way P-gp label — **CA · 5 min**
- **Files:** `chipsim/harmonize/pgp_label.py` (edit)
- **Interfaces:**
  ```python
  def pgp_substrate_label(
      compounds: pd.DataFrame,
      panel_edges: pd.DataFrame,
      panel_path: Path,
  ) -> pd.Series:
      """Index: canonical_inchikey. Values: 'yes' | 'unknown'.

      Resolves the ABCB1 accession FROM THE RATIFIED PANEL by symbol == 'ABCB1'.
      Never hard-codes P08183 (defect 4 / AM-2: composition is configuration, not code).
      Raises RuntimeError if the ratified panel has no ABCB1 entry.

      'yes'      -> an ABCB1 edge of category 'transporter' exists in the snapshot.
      'unknown'  -> no such edge. NEVER returns 'no' from absence of evidence.

      'no' is assignable only by adjudicate_pgp_labels() with a citation.
      """
  ```
- **Done when** the function cannot emit `'no'`, and raises when ABCB1 is absent from the panel — both asserted in T12.

### T12 · Write the label-safety tests — **CA · 4 min**
r1's two tests were both satisfied by `return pd.Series("unknown", index=...)`, which is precisely
how defect 4's silent degradation went unnoticed (defect 20).
- **Interfaces:**
  ```python
  def test_pgp_label_never_infers_negative():
      """A compound with zero protein edges is 'unknown', not 'no'."""

  def test_pgp_label_domain():
      """set(labels) <= {'yes', 'unknown'} before adjudication."""

  def test_pgp_label_positive_case():
      """A compound with an (ABCB1, transporter) edge is labelled 'yes'.
      This is the test a constant-'unknown' implementation fails."""

  def test_pgp_label_ignores_non_transporter_edges():
      """An ABCB1 edge of category 'enzyme' yields 'unknown'."""

  def test_pgp_label_requires_abcb1_in_panel():
      """A ratified panel with ABCB1 removed raises RuntimeError."""
  ```
- **Done when** all five pass.

### T18 · Curate the PoC compound roster — **H · 30–45 min** *(new — defect 3)*
Which 20–40 compounds are "lung-relevant with published exposure" is a **claim**, so by this plan's
own allocation rule it is human-owned. An auto-filter of `drugbank-slim.tsv` is not a substitute.
- **Files:** `configs/poc_compounds.yaml` (new, hand-curated, git-tracked)
- **Interfaces:** 20–40 entries of `{canonical_inchikey, name, evidence_doi}`. **Identity and
  citation only — no biological numbers.**
- **Done when** the roster has 20–40 entries, every entry carries a non-empty `canonical_inchikey`
  and `evidence_doi`, and every `canonical_inchikey` resolves in the parsed snapshot.

### S11a · Write the roster validator — **CA · 3 min** *(paired with T18)*
- **Interfaces:** `load_poc_roster(path) -> pd.DataFrame`, rejecting a roster outside 20–40 entries, any entry with an empty `canonical_inchikey` or `evidence_doi`, and any key absent from the snapshot.
- **Done when** each of those four rejection cases raises, verified against `tests/fixtures/poc_compounds.yaml`.

### T13 · Emit the adjudication worksheet — **CA · 5 min**
- **Interfaces:**
  ```python
  def write_adjudication_worksheet(
      labels: pd.Series,
      compounds: pd.DataFrame,     # needed for `name` — r1's signature could not produce it (defect 21)
      out: Path,
  ) -> int:
      """Write a CSV: canonical_inchikey, name, snapshot_label, adjudicated_label,
      evidence_doi, adjudicated_by, adjudicated_on. Last four empty for H.

      NEVER CLOBBERS (defect 22): if `out` exists, merge on canonical_inchikey and
      preserve every non-empty adjudicated_*/evidence_doi cell. Raises if a
      previously-adjudicated key has disappeared from `labels`.
      Raises if any label index is missing from `compounds`.
      Returns row count.
      """
  ```
- **Files:** `data/interim/pgp_adjudication.csv` (generated draft)
- **Done when** the CSV has exactly one row per T18 roster entry (`20 <= n <= 40`), the four verdict columns are empty, **and re-running against a partially-filled worksheet preserves every filled cell** — the condition that protects T14's 60–90 minutes from a single ETL re-run.

### T14 · Adjudicate the P-gp labels — **H · 60–90 min**
Fill `adjudicated_label` and `evidence_doi` for every row. This is the task that makes the M5
grouping variable trustworthy, and it **cannot be delegated** — a fabricated DOI here would
corrupt the coverage claim invisibly. Leave genuinely uncertain compounds as the explicit string
`unknown`; they are **excluded from both calibration groups** rather than guessed into one.
- **Files:** on completion, move to `configs/pgp_adjudication.csv` — **git-tracked**. r1 left this
  in `data/interim/`, which is git-ignored and DVC-tracked, leaving the plan's most load-bearing
  human artifact unversioned and unattributable (defect 23).
- **Done when** every row has a verdict and a DOI, or an explicit `unknown`, and the file is tracked by git.

### T15 · Load adjudicated labels with provenance — **CA · 5 min**
- **Interfaces:**
  ```python
  def adjudicate_pgp_labels(worksheet: Path) -> pd.Series:
      """Index: canonical_inchikey. Values: 'yes' | 'no' | 'unknown'.

      Raises if NO row has a non-empty adjudicated_label (a wholly unadjudicated
      worksheet — r1 returned all-'unknown' and looked identical to a completed
      one, defect 6).
      Raises if ANY row has an empty adjudicated_label (partial adjudication).
      Raises if any value is outside {'yes','no','unknown'}.
      Raises if any 'yes'/'no' row lacks evidence_doi or adjudicated_by.
      Raises if the 'yes' group or the 'no' group is empty (defect 24) — the M5
      grouping variable is unusable with only one populated group.

      Also writes data/processed/pgp_labels.parquet, which T17 reads (defect 25).
      """
  ```
  An empty cell is an *incomplete* verdict; the literal string `unknown` is a *completed* one.
- **Done when** a wholly-blank worksheet raises, a partially-filled worksheet raises, an all-`unknown`
  worksheet raises, a `no` row with an empty DOI raises, a fully-adjudicated fixture returns a Series
  over `{yes, no, unknown}`, and the parquet round-trips to an identical Series.

### T17 · Render the data-provenance block — **CA · 4 min**
Changed from **(edit)** to **(new)**: `chipsim/eval/card.py` did not exist and no plan creates it;
M0c owns the card (defect 13). This task builds the block and unit-tests it; wiring it into the
card moves to M0c.
- **Files:** `chipsim/eval/provenance_block.py` (edit)
- **Interfaces:**
  ```python
  def render_data_provenance(provenance: Path, labels: pd.Series) -> str:
      """Composes the display string FROM upstream_version + snapshot_date —
      never hard-coded (defect 14). Renders source, commit, licence, the three
      label counts, and pgp_groups_usable computed from those counts (defect 24).
      """
  ```
- **Done when**, against `tests/fixtures/provenance.yaml` and a fixture label Series, the output contains the literal `DrugBank 4.2 (2015-03-19 snapshot)` and three integer counts; **and changing `upstream_version` in the fixture changes the rendered string** — the assertion that proves the value is composed, not hard-coded.

### T16 · Export the ETL workflow — **CA · 5 min** ⚠️ **DESCOPED — see §7**
r1 required a provisioned, running n8n instance with a Python execution path, and a "byte-identical"
done-condition that was unfalsifiable (no committed baseline, no remote, parquet bytes not stable
across versions). Both are out of reach in slice 1 (defects 27, 28).
- **Files:** `orchestration/n8n/etl_drugbank.json` (new, exported)
- **Interfaces:** five node definitions — fetch → hash-verify → parse → **provenance-tests** → write. The node is named `provenance-tests`, not `contract tests`: §4.5 sanctions *data*-contract tests, which arrive with the ChEMBL plan (defect 29).
- **Done when** the JSON validates against the n8n workflow schema, **each of the five nodes names a CLI entrypoint that exists in the installed package**, and the recorded sha256 of `data/processed/drugbank_compounds.parquet` equals `data/processed/drugbank_compounds.sha256`.
- **Not in slice 1:** provisioning n8n and executing the workflow end-to-end. Tracked as **T16a**, deferred.

---

## 7 · Revision log (r1 → r2)

**33 plan-validity defects** and the scaffold hole, folded in per CTO directives of 2026-08-26 and
2026-08-30. The six previously enumerated are D1–D6 below; the rest were re-derived in an
independent audit of r1 against the A&D, PVR and CONTEXT.md.

| # | Tasks | Defect | Resolution |
|---|---|---|---|
| 1 | T7/T9 | `ratified` emitted as a YAML **comment** — T9's guard could never fire | real top-level key; missing key also raises |
| 2 | T3/T11 | hashes returned, never persisted — T11 unwritable | T3 writes `SHA256SUMS.json` |
| 3 | T13/T14 | "PoC compound set" meant both drugbank-slim (~10³) and PVR's curated 20–40 | roster is H-owned **T18**; slim is renamed *candidate pool* |
| 4 | T10 | hard-coded P08183 that T8 may delete → silent all-`unknown`, T12 still green | resolve from ratified panel; raise if ABCB1 absent |
| 5 | T4 | done-condition passed with DVC never initialized | 4-part condition incl. `.dvc` pointer + `dvc status` |
| 6 | T15 | wholly unadjudicated worksheet raised nothing | explicit completeness gate |
| 7 | T3/T5/T6 | `SNAPSHOT_FILES` keys implied a nested `data/` level T5/T6 did not expect | flat writes; `raw_dir` contract stated |
| 8 | T4–T10 | **no task ever performed the fetch** | new **T4a** |
| 9 | T5/T6 | both done-conditions vacuously true on an empty frame | row-count floors, set **equality**, golden row |
| 10 | T4 | `.gitignore` "(edit)" on a nonexistent file; no `--subdir`; blanket ignore swallowed the `.dvc` pointer | S7 + S8 |
| 11 | T4/T16 | no DVC remote — `dvc pull` could never work | new **S9** |
| 12 | T11 | `tests/test_contracts.py` "(edit)" on a nonexistent file; no `pyproject.toml`, no package | S1–S4 |
| 13 | T17 | `chipsim/eval/card.py` "(edit)" on a file no plan creates | retargeted to `provenance_block.py` (new) |
| 14 | T17/T1 | rendered string ≠ stored string; a wrong `upstream:` still rendered correctly | structured `upstream_version` + `snapshot_date`, composed |
| 15 | T1 | done-condition vacuous; free-form Markdown unparseable by T11 | split into `provenance.yaml` + prose |
| 16 | T1/T2 | **ordering error** — T1 required a value T2 produces | T2 now precedes T1 |
| 17 | T2/T11 | commit is a mutable-branch head; only a shape regex guarded it | `audited_commit` + required rationale |
| 18 | T7/T8/T9 | `ratified` per-entry in prose, file-level elsewhere | ruled file-level; prose corrected |
| 19 | T8 | done-condition was pure attestation | new **T19** UniProt verification script |
| 20 | T12 | both tests passed on a constant-`unknown` implementation | positive + category + panel-absence cases |
| 21 | T10/T13 | T13 needed a `name` column T10's Series could not supply | signature takes `compounds` |
| 22 | T13/T14 | regenerating the worksheet silently destroyed the adjudication | merge-preserve, never clobber |
| 23 | T14 | the worksheet lived git-ignored and unversioned | completed file moves to `configs/`, git-tracked |
| 24 | T14/T15 | nothing checked the adjudication yielded two usable groups | T15 raises on an empty group; card renders `pgp_groups_usable` |
| 25 | T15/T17 | T15's Series was never persisted, so T17's counts had no source | writes `pgp_labels.parquet` |
| 26 | T16 | no task wrote the parquet; no parquet engine in the stack | new **T5a**; `pyarrow` added |
| 27 | T16 | "byte-identically" unfalsifiable | recorded sha256 over a canonical serialization; `pyarrow` pinned |
| 28 | T16 | n8n never provisioned; no Python path from a node | **descoped** to JSON + entrypoint validation; T16a deferred |
| 29 | T11/T16 | "contract test" named two different things | `test_provenance.py` split out; node renamed |
| 30 | T16 | `compounds.parquet` collided with A&D §1's harmonized S1 artifact | renamed `drugbank_compounds.parquet` |
| 31 | T5/T10–T15 | **no canonical InChIKey** — RDKit declared, used nowhere; the plan's own Goal unmet | new **T5b**; all downstream keyed on `canonical_inchikey` |
| 32 | T3 | done-condition tested half its own contract | 39-char **and** non-hex cases |
| 33 | T9/T11/T17 | human-gated done-conditions the agent was told it could not evaluate | fixtures in S5 + deferred integration conditions |

**AM conformance.** AM-1 ✓ · AM-2 ✓ (defect 4 fixed: composition is configuration) · AM-3 ✓
(defect 1 fixed: `ratified` is a real field) · AM-4 ✓ (defects 10/12/13 fixed: every "(edit)"
target now exists) · AM-5 ✓ (T5b is §1.2 *identity*, inside the boundary) · **AM-6 OPEN**.

> **AM-6 pointer.** The two-group calibration arithmetic remains **open and with the principal**;
> it is **non-blocking for M0 slice 1** — no task here depends on the group-size threshold — but
> **M5 pre-registration is gated on it.** Defect 24's fix means T15/T17 now *measure* the `yes`/`no`
> populations, so AM-6 can be closed against real counts rather than estimates.

## 8 · Scope check

This plan stops at the identity and barrier-panel layer: **29 CA tasks and 5 human tasks**
(r1: 13 CA / 4 H), roughly 2 hours of agent work and 2 hours of human work.

Three adjacent things are **deliberately not here**:

1. **M0b — curation of 60–100 chip records.** Human-only, needs a protocol document rather than a task list, and it is the project's critical path. Its own plan.
2. **M0c — the frozen evaluator**, and the model card that T17's block plugs into. Cannot be specified until the splits exist. Its own plan.
3. **ChEMBL, BindingDB, TDC, LINCS ingestion**, plus the §1.2 *data*-contract test and `mapping.tsv.gz`. One plan covering all four, after this one proves the pattern.

> **The next plan should be M0b, not the other ingestors.** The ingestion pattern is now proven
> and mechanical; curation is unproven, human-bound, and gates M5 and M6 both. Building more
> parsers first would feel productive and would move the actual completion date not at all.

---

## Agent execution notes (AIADLC)

- **CA tasks (29)** — S1–S11, S11a, T3, T4, T4a, T5, T5a, T5b, T6, T7, T9, T10, T11, T12, T13, T15, T16, T17, T19. Each has a failing-test done-condition evaluable against committed fixtures.
- **H tasks** — **T2, T1, T8, T14, T18** (five, up from four). These are blockers the agent must **escalate, not simulate**. T2 gates T1 and T4a; T1 gates T11; T8 gates T9; T18 gates T13; T14 gates T15. The agent builds the code and tests around them, leaves the human artifacts absent, and reports the blocked set at the boundary.
- **T18 is new and is a human blocker.** It exists because pinning "PoC compound set" to the PVR's curated 20–40 makes the roster a curation claim no agent may write.
- **The hard rule stands:** no agent-written biological numbers, no agent-created curated records or rosters, no agent edits to the frozen evaluator. T7's panel is drafted `ratified: false` **by design** — drafting accessions is allowed; ratifying them is not.
- **Fixtures are not human artifacts.** `tests/fixtures/*` exist so CA done-conditions can fail honestly while T1/T2/T8/T14/T18 are outstanding. They live under `tests/`, are never read by a pipeline path, and S5 asserts that.
