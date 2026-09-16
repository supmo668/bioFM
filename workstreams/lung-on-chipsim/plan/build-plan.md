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
- **One interactive session per tree** *(r2.15 item 3)*. A worktree has exactly one interactive
  session that may commit to it; the trunk has exactly one CTO session that may write to it. A
  second session on the same tree **is** the signing hold: the tip moves mid-computation and no
  receipt verifies. **The grill draft's specific resolution of 2026-09-15 is VOID** — it directed
  closing pid `56186` on the worktree and pid `51059` on the trunk, on the premise that each tree
  held a second bare session. Verified by `ps` and `ListAgents`: `56186` **is** the worktree's sole
  writer, and the principal subsequently ruled that `51059` keeps this lane. The **principle**
  stands; its 2026-09-15 application does not. *Lesson recorded because it nearly cost the work: a
  constraint expressed as "close pid X" inherits whatever the premise about X got wrong — identity
  claims must cite the check that produced them.*
- **Approval provenance lives in an append-only log** *(r2.15 item 6)*. `plan-approval.md` is
  tool-owned: `plan-gate sign` regenerates it wholesale and preserves nothing below the frontmatter
  (observed **eight** times). `plan/plan-approval-log.md` is append-only — one entry per sign, with
  revision, hash, route (`human-direct` / `standing-delegation` / `principal-directed`), authorising
  rulings and the prior human-direct hash. Every sign appends. **The quality gate fails when the
  newest entry's hash differs from `plan-approval.md`'s `plan_hash`.**

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

> **Four things a coding agent may never do, at any phase.** (1) Write a number into
> `theta_priors.yaml` or `assumptions.yaml`. (2) Create, edit or extend a curated chip record,
> or the curated compound roster. (3) Modify the frozen evaluator, the split definitions, or the
> sealed allocation after signature. (4) **Run `chipsim panel-seal` against the live
> `configs/barrier_panel.yaml`** — the agent writes the tool, the *human's invocation* writes the
> file, because that file is human-only (CTO ruling, dispatch #21; corrected #27).
>
> **The seal is tamper-evidence, never proof that a human attested (CTO ruling, dispatch #27).**
> An earlier revision of this constraint said "running the seal **is** the act of attestation."
> That was wrong and is retracted. `ratified_panel_sha256` is an **unkeyed digest over public
> content**: it shows the panel has not changed since sealing, and it can never show *who* sealed
> it. The attestation is `ratified_by` plus the human's act — the digest only protects it from
> silent edit afterwards. **Nothing in code, config, CLI help, plan or model card may describe the
> seal as authenticating a human.**
>
> Constraint (4) is therefore a **stated rule with no technical enforcement** — like (1)–(3), and
> more so. The r2.4 hardening (preimage bound to `ratified`/`ratified_by`/`ratified_on` **and the
> panel filename**, fixture panels marked `[FIXTURE]` so they cannot coincide with the live one)
> closes **replay**, demonstrated as a real attack: the fixture panel was byte-identical to the
> live panel, so sealing a fixture — a sanctioned agent action — yielded the valid live seal. It
> does **not** close **forgery**: anything that can write `ratified: true` can compute the digest
> over what it wrote. Real signing (minisign/age/GPG against a pinned human key) is the only option
> that would give (4) technical force, and it is now **decided: minisign, at the M1
> re-ratification** *(r2.15 item 5)* — when the three provisional faces (TFRC, FCGRT, SLCO2B1) are
> re-checked, so the panel is signed **once, settled**, rather than signed now and re-signed weeks
> later against a changed panel. Until that happens the quality gate checks this rule, reviewers
> treat an agent-run seal as a gate failure, and the limitation is stated wherever the ratification
> is claimed — the plan, the run journal's provenance block (T17) and any model card — **carrying
> this sentence verbatim: "digest-sealed, human-ratified, not cryptographically signed."**

## 2 · Phase ownership map (M0–M6)

| Phase | What gets built | CA builds | H owns | XB |
|---|---|---|---|---|
| **M0a** Data spine | ingest, harmonize, identity, barrier panel | all parsers, contracts, tests, n8n ETL workflow | licence ruling, UniProt panel ratification, compound roster, P-gp adjudication | — |
| **M0b** Chip-record curation | **80–100** on-domain records, sealed **three-way** allocation (AM-6 resolved) | the schema, the sealing tool, the hash ledger | **every record, every seal** | — |
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
- **Done when** `pytest --collect-only` exits 0 from the project root, **and** a test asserts against the
  *parsed* config that `[tool.pytest.ini_options].testpaths == ["tests"]` and that both markers are
  registered. **(CTO ruling E-2.)** The r2 wording — "exits non-zero if `testpaths` is removed" — was
  false as written and could never fail: pytest's default `norecursedirs` already skips `.venv`, so
  collection still exits 0 with `testpaths` absent. Asserting on the parsed config tests the real thing.

### S4 · Create the test package and the day-one modules — **CA · 4 min**
A&D §4.4 requires the three day-one tests. **`test_provenance.py` is a new file, distinct from
`test_contracts.py`** — §4.4 reserves `test_contracts.py` for the §1.2 *data*-contract test, and
T11's provenance checks are a different kind (defect 29).
- **Files:** `tests/conftest.py` (new, `project_root` + fixture loaders) · `tests/test_provenance.py` · `tests/test_contracts.py` · `tests/test_leakage.py` · `tests/test_monotonicity.py` (new). **Each skip names its own blocker — CTO ruling E-3:**
  `test_leakage.py` carries `pytest.mark.skip(reason="M0 slice 3 — splits not yet built")`;
  `test_monotonicity.py` carries `pytest.mark.skip(reason="M1 ODE solver not yet built")`. Monotonicity
  waits on the **M1 ODE solver**, not on slice-3 splits — a skip reason that misnames its own blocker
  sends the next reader to the wrong milestone.
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
- **Done when** the probe set below passes. **A top-level-only probe is not a probe of this rule (CTO
  ruling E-4)** — `data/raw/*` excludes the *directory* `data/raw/drugbank/`, and **git cannot re-include
  a file beneath an excluded directory**: negations below an excluded directory are inert. The r2 probes
  passed against a `.gitignore` that silently ignored T1/T2's human artifacts and T4's done-condition (d).
  So the probes MUST assert on **nested** paths explicitly:
  - `git check-ignore -q data/raw/probe.tsv` exits **0** (bulk data ignored)
  - `git check-ignore -q data/raw/drugbank/probe.tsv` exits **0** (nested bulk data ignored)
  - each of these exits **1** (tracked — must NOT be ignored):
    `data/raw/drugbank/provenance.yaml`, `data/raw/drugbank/PROVENANCE.md`,
    `data/raw/drugbank/SHA256SUMS.json`, and each `data/raw/drugbank/{drugbank,drugbank-slim,proteins}.tsv.dvc` (r2.11)

### S8 · Initialize DVC — **CA · 3 min**
`dvc init --subdir` is required because the project root is a subdirectory of an existing git repo
(defect 10b). Without this, T4's done-condition is unfalsifiable.
- **Files:** `.dvc/config` (new, generated) · `.dvcignore`
- **Done when** `.dvc/config` exists **and** `dvc status` exits 0.

### S9 · Configure a DVC remote — **CA · 2 min**
Nothing in r1 configured storage, so `dvc pull` could never succeed (defect 11).

**The remote MUST live at an absolute path OUTSIDE every git tree. CTO ruling E-5 — this is a
data-loss fix, not a preference. Do not "simplify" it back inside the tree.**

- **Files:** `.dvc/config` (edit, committed) — declares the remote **by name only, with no url**.
  `.dvc/config.local` (**gitignored, never committed**) carries the url, which each contributor sets
  to their own absolute path outside every git tree:
  ```
  # .dvc/config.local — local only, never committed
  ['remote "local"']
      url = <absolute path outside every git tree, e.g. ~/.aiadlc/biofm/dvc-storage expanded>
  ```
  **Do not commit a literal home path (CTO ruling, dispatch #18 — refines E-5).** E-5 was right that
  the store must be absolute and external; committing *this machine's* path was the wrong mechanism.
  It ships an account name and home layout to a public remote, and — worse — DVC's local remote
  **creates the directory on push**, so every other contributor and CI gets a silent empty success on
  push and nothing on pull, instead of a clean "no remote configured" error. That is the same
  silent-success failure class E-5 exists to prevent, reintroduced one layer over.
- **Why (do not remove this rationale):**
  1. **A relative url destroys the data.** r2 specified `../../../.dvc-storage`, which from
     `projects/lung-on-chipsim/.dvc/` resolves to **`worktrees/lung-on-chipsim/.dvc-storage`** — *inside*
     the worktree. `git worktree remove` is a routine operation here (there is a `/worktree-delete`
     skill), so as specified **a routine cleanup destroys the only copy of the snapshot.**
  2. **Absolute, not `~`-relative.** DVC does not reliably expand `~` in `.dvc/config`.
  3. **Beside the ISCP database**, following the convention already in `agency.yaml`
     (`iscp.db_path_template: ~/.aiadlc/{repo}/iscp.db`). It survives worktree removal, survives branch
     switches, and is outside every git tree so it can never be vendored.
  4. **It needs no `.gitignore` entry at all**, and it retires F-02 as a live risk rather than merely
     ignoring it: extensionless md5 blobs cannot be `git add -A`'d if they are not under the repo.
     Keep the F-02 ignore rule anyway as belt-and-braces, and keep the widened
     `test_drugbank_not_vendored` — matching only `*.tsv` would never have caught blob-form bytes.
- **Done when** `dvc remote list` names a default remote whose url is that absolute external path, the
  configured url resolves outside the repository root, and `dvc push` followed by `dvc pull` on a clean
  cache round-trips the snapshot.

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

> **r2.15 — PROVENANCE.md stays human-authored; a proposal to let the CTO draft it was put and
> declined.** The 2026-09-15 grill draft (item 1) proposed the T8 pattern — CTO drafts, principal
> ratifies and seals — reasoning that the licence *decision* was already the principal's (1B1
> 2026-09-09, recorded verbatim in `provenance.yaml`'s `non_commercial_commitment`), so the prose
> would restate a decided claim rather than make one. **The principal was shown both readings
> explicitly and chose human-only.** "Hand-written prose" above is therefore unchanged, a
> CTO-drafted `PROVENANCE.draft.md` committed at `5147281` was removed at `6557487`, and **no agent
> may draft this file**. The argument is recorded rather than discarded so that a future reader sees
> it was considered, not overlooked.
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
- **Done when** `yaml.safe_load` yields the contract in the form ratified by **CTO ruling E-1**:
  **nine keys present; eight always non-empty; `commit_change_rationale` non-empty IFF
  `source_commit != audited_commit`.** `attribution` has three entries, and `PROVENANCE.md` exists.
  The r2 wording ("all eight keys non-empty") contradicted T2, which *requires*
  `commit_change_rationale` to be empty when `source_commit == audited_commit`. This conditional is
  strictly **more** checkable than "all non-empty", because it makes the *empty* case an assertion
  rather than an exemption.

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
- **Files:** `data/raw/drugbank/{drugbank,drugbank-slim,proteins}.tsv.dvc` (three new pointers, one `dvc add` per TSV)
- **Done when** all four hold (defects 5, 10; (b)/(c) amended r2.11):
  (a) `git status --porcelain` lists no `.tsv`;
  (b) **each** of the three `.tsv.dvc` pointers exists, **is tracked by git**, parses as YAML with a non-empty `outs[0].md5`;
  (c) `dvc status` on all three pointers reports up-to-date;
  (d) `SHA256SUMS.json` is tracked by git.

> **r2.11 — a directory pointer cannot exist here; three file pointers can.** r2 specified one
> `data/raw/drugbank.dvc` over the whole directory. DVC refuses to track a directory while any file
> inside it is tracked by git (`dvc/output.py:670`, both scmrepo backends) — and this directory
> *deliberately* holds three git-tracked files: `provenance.yaml`, `PROVENANCE.md`,
> `SHA256SUMS.json`. So (b)/(c) as signed were **unsatisfiable**, not merely awkward. The CTO first
> ruled that no signed condition needed amending; the worktree agent disproved that from source.
> **Principal ruling 2026-09-15: one pointer per TSV.** (a) and (d) are unchanged; S7's ignore
> probe and T11's pointer test follow the new paths.

### T11 · Write the provenance contract tests — **CA · 5 min**
Lives in `tests/test_provenance.py`, **not** `tests/test_contracts.py` — §4.4 reserves the latter
for the §1.2 *data*-contract test, which arrives with the ChEMBL plan (defect 29).
- **Files:** `tests/test_provenance.py` (edit)
- **Interfaces:**
  ```python
  def test_provenance_complete():
      """provenance.yaml parses and carries all NINE keys present, with the eight
      unconditional keys non-empty; source_commit matches ^[0-9a-f]{40}$;
      attribution has three entries. (CTO ruling E-1.)"""

  def test_provenance_commit_substitution_is_justified():
      """The conditional contract, ratified E-1: commit_change_rationale is
      non-empty IFF source_commit != audited_commit. Both directions assert —
      a silent snapshot swap fails (rationale missing), AND a rationale offered
      for an unchanged commit fails too (defect 17)."""

  def test_snapshot_hashes_match_manifest():
      """Recomputed sha256 of each fetched file equals SHA256SUMS.json (defect 2).
      Fails if any fetched file is mutated after fetch."""

  def test_drugbank_not_vendored():
      """`git ls-files` matches no .tsv under data/raw/ — recursive, so a nested
      layout cannot hide one (defect 7)."""

  def test_dvc_pointer_is_tracked():
      """Each of the three data/raw/drugbank/*.tsv.dvc pointers IS tracked by git
      (r2.11) — the blanket ignore must not swallow the files that make the
      snapshot recoverable (defect 10c)."""
  ```
- **Done when** all five pass against `tests/fixtures/provenance.yaml`, `test_drugbank_not_vendored` fails if you `git add -f` a TSV, and `test_dvc_pointer_is_tracked` fails if **any one** of the three pointers is untracked.
- **Blocked-by:** T1/T2 for the *live* provenance file; the unit conditions above run against the fixture.
- **Sign-off note (CTO ruling E-1):** T11 is **unblocked for sign-off against fixtures** even though
  T1/T2's real artifacts are absent, because the conditional contract is testable in both directions
  from fixtures alone.

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
- **Done when** a known salt / free-base pair collapses to one `canonical_inchikey`, the column is non-null on every row, and a raw-vs-canonical disagreement count is reported. **Plus (r2.12, corrected r2.13, extended r2.14):**
  (i) the benzimidazole 1H/3H tautomers stay merged, and the malate pair's split is asserted by a named accepted-loss test;
  (ii) **relative-stereo handling:** a source InChI declaring `/s2` is keyed with its **tetrahedral stereo stripped** (`/b` retained — double-bond geometry is always absolute), `stereo_is_relative` is emitted as a `bool` column by both `add_canonical_identity` paths, **is listed in `PERSISTED_COMPOUND_COLUMNS`** so T5a cannot drop it, and `MERGE_STAGES` carries a `relative-stereo` stage immediately after `parse`;
  (iii) the threonine test pins its members **by InChIKey, not by name** — the stereo-free threonine key (PubChem CID 205) and `AYFVYJQAPQTCCC-PWNYCUMCSA-N` (D-allothreonine, CID 90624).

> **r2.14 — the source's own stereo flag, and why the condition now names keys instead of compounds.**
> An InChI's `/s` layer declares whether its sp3 stereo is absolute (`/s1`) or **relative** (`/s2`).
> The snapshot holds **42 `/s2` strings and no `/s3`**, and the pipeline keyed **all 42 as absolute**
> — RDKit reads `/s2` as `/m0`. Of the 31 with comparable centre sets, **13 received the mirror
> image**, including single-enantiomer drugs (dextropropoxyphene, dexetimide, dolutegravir, ethinyl
> estradiol, mestranol). Nothing errored: this is the key T10/T13/T15 join on. **Principal ruling
> 2026-09-15: assert nothing the source does not — strip tetrahedral stereo for `/s2` input and flag
> it.** Accepted consequence, stated rather than buried: **esomeprazole now merges with omeprazole**,
> because DrugBank records esomeprazole with relative stereo, so on this snapshot's evidence the
> study cannot distinguish the single S-enantiomer from the racemate. Three relative rows also
> *separate* from absolute rows they had matched by RDKit's arbitrary assignment.
> **The source's D-/L- labels are wrong at scale, measured and then classified.** Of 134 rows whose
> name carries a `D-`/`L-` prefix, 59 resolve against PubChem for both enantiomers. Of those, **11
> are genuine label errors on rows whose stereo is absolute** — D-leucine, D-alanine, D-glutamine,
> D-glutamic acid, D-proline, D-cysteine, D-lysine, D-treitol, D-tyrosine and D-arginine all carry
> **L** structures, and one `L-`-prefixed boronic-acid alanine keys as **D**. The re-key does not
> touch these: they were absolute already, and they key the same before and after. A twelfth
> contradiction, "L-Threonine", **was** an artifact of the old absolute reading of a relative string
> and is fixed by (ii). A thirteenth is unresolved and not counted. A further 75 rows could not be
> resolved either way, so **11 is a floor, not a total**.
> This is why (iii) pins InChIKeys: **a condition that names a compound inherits the source's
> labelling errors, and this source mislabels a substantial fraction of its stereoisomers.** Every
> label-bearing output — worksheet `name`, roster entries, model cards — must be treated as
> unreliable wherever the label disagrees with the key, **and the key is what joins**. The two
> classes must not be conflated: one is a source defect the pipeline can only report, the other was
> a pipeline defect the pipeline has fixed.

> **r2.13 — the snapshot mislabels its *D-Threonine* row, and r2.12 inherited the error.** r2.12's
> condition said "L-/D-threonine". The snapshot row titled *D-Threonine* carries
> `.../t2-,3-/m1/s1` — which is **byte-identical to PubChem's D-allothreonine** (CID 90624,
> `AYFVYJQAPQTCCC-PWNYCUMCSA-N`), while true D-threonine (CID 69435, `AYFVYJQAPQTCCC-STHAYSLISA-N`)
> is `.../t2-,3+/m0/s1` and matches no snapshot row. The row titled *L-Threonine* is also a
> non-standard InChI. So the test exercises **L-threonine vs
> D-allothreonine** — genuinely different stereoisomers, so the guard's behaviour and every measured
> figure stand unchanged; only the naming was wrong. Verified against PubChem PUG REST by the CTO,
> 2026-09-15, after the worktree agent found it. A true L-/D-threonine case needs both structures
> sourced from PubChem and is optional, not required here. **Lesson for done-conditions: a condition
> that names a compound inherits the source's labelling errors unless the label is checked against
> the structure.**

> **r2.16 — accessions removed from this plan (wording only).** The r2.13 note above named two
> DrugBank accessions beside their record titles and structures — the `(accession, name, structure)`
> association the principal's 2026-09-15 record-content re-ruling protects — and one accession sat in
> `plan-approval-log.md` row 11. Found by the worktree agent's repo-wide scan before it built the
> guard test (#131); ruled by the CTO 2026-09-16 under that re-ruling and the standing "no accessions
> in coordination records" rule (#122 §3), which binds the plan too. **Rows are named by their title
> and pinned by InChIKey; the log row is corrected in place with the correction disclosed (the row-12
> precedent), so the guard test carries no exclusion for plan files.** No condition, task or figure
> changes. r2.16 has no principal ruling of its own — a truth-fix under the r2.8/r2.9 precedent,
> disclosed here and in the marker.

> **r2.12 — the stereo guard, and what it costs.** Principal ruling 2026-09-15: tautomer
> canonicalisation must not change stereo. Compare the pre- and post-tautomer InChI's **`/t`, `/m`
> and `/s`** layers only — **`/b` (double-bond geometry) is excluded** — and return the
> **pre-tautomer** key when any of the three changes or vanishes. **Measured on the guard alone,
> before r2.14's relative-stereo re-key** (CTO re-ran it independently): fired on **1,599 of 6,802**
> compounds (23.5%), merge groups **191 → 156**, tautomer-stage groups **48 → 7**, **41 groups
> split, zero new merges**.
>
> **r2.16 — those figures are historical, and this plan stopped restating figures from memory.**
> With the re-key in place the committed report gives **1,576 fired (23.2%), 192 → 154 merge groups,
> 43 split, 0 newly merged** over the same 6,802. The two sets differ because the re-key changes
> which keys exist *before* the guard runs — neither measurement was wrong, but r2.14 and r2.15 both
> presented the earlier set as current after the re-key had landed, and the **worktree agent caught
> stale numbers inside hash-locked text**. **Source of record for every such figure:**
> `workstreams/lung-on-chipsim/reports/2026-09-15-stereo-guard-tms/merge_report.json`, regenerated by
> `python -m chipsim.harmonize.merge_report`. Prose in this plan **cites** it; it does not restate it.
> Of the original 41 (the classification below has **not** been re-run against the post-re-key 43,
> and must not be quoted as though it had):
> **36** clean stereo separations, **2** ambiguous keto/enol pairs whose stereo does not correspond
> between forms, **2** incidental aldose/ketose, and **1 accepted known loss** — the malate tautomer
> pair, whose source forms already differ in skeleton hash. The salt/free-base condition above is
> unaffected: the guard fires on the tautomer step, not the salt-strip step. The first reading of the
> ruling compared four layers including `/b`; that split 3 true-tautomer groups and was refuted by
> per-layer measurement before any code was written. Aldose/ketose merging is a **separate, open**
> scope question and is not decided here.

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
      Filters to organism in {'Human', 'Homo sapiens'} — BOTH, deliberately.
      """
  ```
- **Done when** `len(df) > 0`, `set(df.category) == {target, enzyme, transporter, carrier}` (**equality, not subset** — defect 9), and a golden-row assertion holds: a named reference drug with a known ABCB1 transporter edge is present. The golden row is what catches a silent species-filter mismatch that empties the frame.

> **r2.10 — the mismatch was real, and the golden row is why we know.** The spec said
> `organism == 'Homo sapiens'`. The pinned 2015 snapshot says **`Human`: 16,299 rows, and
> exactly zero saying `Homo sapiens`** (verified against the fetched TSV, 2026-09-14). As
> written the loader returned an **empty frame on the only data the study is permitted to
> use** — and every fixture said `Homo sapiens`, so no test could have caught it. **Accept
> both labels**, rather than swapping one for the other: the fixtures are legitimately
> `Homo sapiens`, and silently preferring either would leave the next reader unable to tell
> which vocabulary the code trusts. The class is *a done-condition evaluated against a
> fixture that does not share the real snapshot's vocabulary* — green tests, correct about
> the fixture, wrong about the world.

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
    - {symbol: TFRC,    uniprot: P02786, alias: "TfR1",         face: basolateral}   # was apical — see N1 note
    - {symbol: FCGRT,   uniprot: P55899, alias: "FcRn",         face: apical}
    - {symbol: SLC15A1, uniprot: P46059, alias: "PepT1",        face: apical}
    - {symbol: SLCO2B1, uniprot: O94956, alias: "OATP2B1",      face: basolateral}
  ```
- **Done when** `yaml.safe_load(...)["ratified"] is False` (a *parsed boolean*, which the r1 comment form could never satisfy) and every entry carries `symbol`, `uniprot`, `alias`, `face`, **and the file carries a `ratified_panel_sha256` key** (empty until T8 seals it).

> **N1 — TFRC `face` corrected apical → basolateral (CTO ruling, dispatch #18).** r2.2 prescribed
> `apical`. The principal ruled `basolateral` on measured basolateral:apical localization ratios —
> MDCK I ~800:1, MDCK II ~300:1 (Fuller & Simons 1986), Caco-2 ~40:1, HepG2 ~3:1, BeWo ~2:1;
> direction unanimous. **Two caveats travel with it and must not be dropped:** none of those systems
> is airway epithelium, so this is extrapolation across polarized epithelia with airway magnitude
> unmeasured; and the ratio spans ~400×, so at the low end this is a *preference*, not exclusive
> localization. T8 authorizes correcting accessions and deleting entries — it did **not** authorize
> a `face` change, so the live config briefly diverged from the signed plan. This amendment is what
> makes the value authorized; the plan leads the artifact, never the reverse.

### T19 · Write the panel verification script — **CA · 4 min** *(new — defect 19)*
T8's r1 done-condition was pure attestation ("you have personally opened seven UniProt pages"),
leaving the barrier panel's only control unverifiable. This gives T8 a checkable surrogate.
- **Files:** `tests/test_barrier_panel.py` (new, `pytest.mark.network`)
- **Interfaces:** for every entry, assert `rest.uniprot.org/uniprotkb/<acc>.json` resolves, `organism.taxonId == 9606`, and the primary gene name equals the entry's `symbol`.
- **Done when** the test passes against `tests/fixtures/barrier_panel_ratified.yaml` and **fails** when one accession is mutated to a valid-but-wrong human accession.

### T7a · Build the panel seal tool — **CA · 5 min** *(new — CTO ruling, dispatch #21)*
> **AMENDMENT r2.7 (principal, 2026-09-02) — the seal gets its first actual enforcement.**
> `chipsim panel-seal` **must refuse to run without an interactive terminal** (no TTY on stdin →
> exit non-zero, write nothing). A headless agent session has no TTY, so the sanctioned-action path
> that currently yields a valid live seal simply fails. Until now Global Constraint (4) had **zero**
> technical enforcement; this is the first.
> **State the residual limit on the model card and do not overstate it:** the seal proves the file
> is unmodified, never who ratified it, and an agent that deliberately allocates a pty defeats this
> guard. It converts an accident into a deliberate circumvention — that is the honest claim, and it
> is the whole claim. Real signing with a human-held key is a v2 decision, deferred.

T8's attestation step invokes `uv run chipsim panel-seal`, which did not exist as a task. **Placed
before T8 deliberately**, on the S11a-before-T18 precedent and for a sharper reason: the seal is the
**tamper-evidence the human's ratification depends on** — it is *not itself* the attestation
(dispatch #27; this sentence was the **tenth** survivor of that reframe, found 2026-09-14 by a
wrap-aware sweep after line-oriented greps missed it for two weeks). If the tool is missing when the
principal sits down to ratify, T8 cannot be completed at all — the plan would be self-blocking.

- **Files:** `chipsim/harmonize/pgp_label.py` (edit) · `chipsim/pipeline.py` (edit — `panel seal`
  subcommand) · `tests/test_pgp_label.py` (edit)
- **Interfaces:**
  ```python
  def panel_digest(panel: list[dict]) -> str:
      """sha256 over the canonically-serialized panel list."""

  def seal_panel(panel_path: Path) -> str:
      """Write ratified_panel_sha256 and return it.
      Raises if the panel is not ratified — see the third done-condition.
      """
  ```
  `load_ratified_panel` verifies the digest and **raises on mismatch**.
- **Done when** (all three):
  1. sealing a ratified fixture, then flipping one `face`, makes `load_ratified_panel` raise;
  2. sealing is idempotent;
  3. **sealing an UNRATIFIED panel raises rather than writing a digest.** Without (3) a digest could
     be produced while `ratified: false` — an attestation record binding nothing a human signed.
- **Constraint:** an agent may build and test this tool against **fixtures only**. Running it against
  the live `configs/barrier_panel.yaml` is forbidden by Global Constraint (4).

### T8 · Ratify the panel accessions and faces — **H · 15–20 min**
Check each accession against UniProt, **and check each `face`**. Correct anything wrong, then set
`ratified: true` and fill `ratified_by` / `ratified_on`.

**Deletion criterion — CTO ruling, dispatch #16 (was a trap).** r2.1 said "delete any not expressed
in airway epithelium". Read literally against UniProt tissue-specificity comments, **five of seven
entries have no lung mention — including ABCB1**, the P-gp keystone the entire M5 grouping variable
rests on. UniProt's tissue comment is a *curated sample, not an expression atlas*, so silence there
is a curation gap, not absence of expression — the same epistemic error the three-way P-gp label
exists to prevent, against a different source.

> **Delete ONLY on positive evidence of absence from airway epithelium. Silence is not evidence.**

**What ratification attests to.** Identity (`symbol`, `uniprot`, `alias`) **and `face`** — nothing
more. It does **not** endorse seven modelled carrier terms: per AM-3 the panel holds *identity* and
`theta_priors.yaml` holds *quantity*, and in slice 1 the panel is consumed only by T9's edge join
and T10's ABCB1 resolution. PVR §2E's "two carrier terms" is a θ constraint at M1 under the 5–8
identifiable-parameter budget — seven join targets cost zero parameters; seven *fitted abundances*
would blow that budget. Nobody may later read a ratified seven-entry panel as endorsing seven
mechanisms.

**Optional `airway_evidence:` per entry (`DOI` or `PMID`).** Under the criterion above, "kept" means
*no positive evidence of absence* — weaker than *positive evidence of presence*, and the two states
are otherwise indistinguishable in the file. Supplying `airway_evidence` upgrades an entry to the
strong claim. **Optional by design** so it does not inflate this task; **absent means the weak claim
explicitly**, never the strong one. Human-only — an agent may never populate it.

- **Seal the panel (CTO ruling, dispatch #18).** After setting the attestation fields, run
  `uv run chipsim panel-seal` **from `projects/lung-on-chipsim`** — `uv run`, because `chipsim` is a
  console script inside the project venv and is never on a system PATH; the principal hit
  `zsh: command not found: chipsim` running the bare form on 2026-09-12, which is the **C4
  self-blocking defect recurring one layer down** after the entry point itself was added. It writes
  `ratified_panel_sha256` over the canonically-serialized panel
  list. `load_ratified_panel` verifies it and **raises on mismatch**. Without this, `ratified: true`
  attests to nothing checkable — after T8 any post-ratification edit (a `face` flip, an accession
  swap, a deleted entry) is invisible, which is exactly how N1 went unnoticed until a scorer read the
  plan text. The digest is **not a biological number**, so Global Constraint 1 does not apply.
  **The seal is tamper-evidence, NOT attestation** (CTO ruling, dispatch #27; this line was a
  survivor of that reframe, found 2026-09-09 while preparing T8). `ratified_panel_sha256` is an
  unkeyed digest over public content: it shows the panel has not changed since sealing and can
  **never** show *who* sealed it. The attestation is `ratified_by` plus your act; the digest only
  protects that from silent edit afterwards. Sealing is reserved to you because the **file** is
  human-only — not because the digest establishes identity. Read the Global Constraints block
  above before you seal; it governs, and this task previously contradicted it.
- **Done when** `ratified: true`, `ratified_by` and `ratified_on` are non-empty, every `face` has
  been checked, `ratified_panel_sha256` is populated and verifies, **and T19 passes against the live
  file** (defect 19).
- **Note for T10:** if you delete or re-accession ABCB1, T10 now raises rather than silently
  labelling everything `unknown` (defect 4).
- **Known schema limit (deferred to M1, not a T8 concern):** the `{apical, basolateral}` binary
  cannot represent a two-faced transporter, and two of seven are (FCGRT transcytoses
  bidirectionally; SLCO2B1 is basal/basolateral/apical). Widen the schema at M1 when directional
  transport actually consumes the field.

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

> **r2.15 items 2 and 7 — the hand-off, and the window it starts.** The candidate list is generated
> **only on guarded keys**: after the r2.12 stereo guard and the r2.14 relative-stereo re-key have
> landed, with the disagreement report regenerated, so the principal authors a roster on keys that
> will not move again in slice 1. *(Both have landed — `7592f56`/`8cb72bf`, re-keyed at `1b74814` —
> so the hand-off is unblocked on the CTO's timing.)* Entries stay keyed by `canonical_inchikey`;
> **`drugbank_id` is carried alongside for traceability, never as the key** — this source mislabels
> at least 11 of its stereoisomers, so the key is identity and the name is annotation.
> **Milestone, counted from the day the guarded candidate list is handed over:** the roster (T18) by
> **working day 2**, the P-gp adjudication (T14) by **working day 3**. The plan carries the hand-off
> date and both due dates; **a slip is reported in the dev-log and never back-filled by an agent
> draft.** The candidate list must also carry the tri-state `label_disagrees_with_key` column, so the
> principal sees where the source's own name contradicts the structure he is selecting on.

### S11a · Write the roster validator — **CA · 3 min** *(paired with T18)*
- **Interfaces:** `load_poc_roster(path) -> pd.DataFrame`, rejecting a roster outside 20–40 entries, any entry with an empty `canonical_inchikey` or `evidence_doi`, and any key absent from the snapshot.
- **Done when** each of those four rejection cases raises, verified against `tests/fixtures/poc_compounds.yaml`.

### S12 · Build the run journal (environment + seeds) — **CA · 15 min** *(new — principal requirement; CTO ruling, dispatch #35; rescoped by principal 2026-09-02)*
> **SCOPE AMENDMENT r2.7 (principal, 2026-09-02).** Two removals, one addition. See A&D 4.4a-ii.
>
> **REMOVED — git state.** No `_git_state()`, no shelling out to `git` at runtime. Capturing the
> commit and dirty flag required running `git` with a caller-supplied cwd, and `git` honours
> repo-local config — an arbitrary command execution path (QG blocker B2, reproduced three times).
> **The feature is deleted, not hardened**: a PoC run journal has no need to run `git`, and removal
> takes the attack surface to zero where a defence only shrinks it. Record the code version from
> what the installed package reports. **Accepted cost, stated plainly: a run record can no longer
> prove the tree was clean when it ran.** Do not paper over this in the record's documentation.
>
> **REMOVED — diff and veto state.** Both are v3 exploration-loop artifacts. v0+v1 runs no loop, so
> they would be structurally null for the PoC's whole life — the 'key present, value meaningless'
> shape QG blocker B3 showed is untestable.
>
> **ADDED — seeds.** The seed is resolved from the run config and its resolved value recorded.
> Previously `environment.seeds` was null and nothing ever set a seed, so no replay claim was
> supportable at all.
>
> **The replay test splits in two and the two must never be conflated.** The **v3 form** — 're-run
> any kept diff from journal + seed' — tests the exploration loop and is **not applicable to the
> PoC**; its absence here is not a defect, and S12 never claimed to close it. The **PoC form**,
> which S12 does close: *same config + same seed reproduces the same scores exactly.*

**Partial gap-closure, not a feature.** A&D §4.4 specifies `journal/` as *"append-only run records — diff,
seeds, scores, veto state"* and §5 requires a **replay test**: *"re-run any kept diff from journal +
seed and reproduce the trajectory exactly."* The record spec **names no configuration**, and
`journal/` does not exist. So a replay reading "diff + seed" picks up whatever `configs/` holds **at
replay time**, reproduces *a* trajectory, and **reports success** — the control cannot fail for the
reason it exists. It bites precisely here: `pyarrow` and `rdkit` are `==`-pinned because parquet
bytes are sha256'd and rdkit computes the canonical InChIKey every join and the sealed allocation
key on; a record omitting resolved versions cannot show two runs were the same computation.

It also creates `journal/`, which AM-4's tree lists and **no task creates** — the same gap class as
the original scaffold hole, which is why this is an S-task.

- **Files:** `chipsim/journal.py` (new) · `chipsim/pipeline.py` (edit — open a run in each ETL stage) · `tests/test_journal.py` (new)
- **Interfaces:**
  ```python
  def start_run(command: str, project_root: Path) -> Path:
      """Called BEFORE any work. Creates journal/<run_id>/, COPIES every
      configs/*.yaml into journal/<run_id>/configs/, writes manifest.json.
      Raises if the run directory already exists.
      """
  def read_manifest(run_dir: Path) -> dict:
      """Verify manifest_sha256 and return the manifest.
      REFUSES a manifest carrying no manifest_sha256 — never loads unverified.
      """
  ```
- **Manifest records:** run_id · UTC start · exact argv · git commit **and** dirty flag with the
  dirty file list · python + platform · resolved versions of the output-determining packages
  (`pyarrow`, `rdkit`, `pandas`, `numpy`, `PyYAML`) · per-config sha256 · `CHIPSIM_SEED` /
  `PYTHONHASHSEED` / `SOURCE_DATE_EPOCH` where set.
- **Copies, never references.** A config edited tomorrow must not change what yesterday's run says
  it used. That is the whole requirement in one sentence.
- **A dirty tree is RECORDED, never hidden or refused.** A run from a dirty tree is not reproducible
  from its commit alone; the honest response is to say so in the record — the same posture as
  `unknown` in the P-gp label, where the third state survives into the schema.
- **`panel-seal` is journalled as record type `invocation`, not `run`** — argv, environment,
  timestamp, **no digest**. Recording every invocation is what makes a Global Constraint (4)
  violation *detectable*, which is the enforcement gap (4) otherwise leaves open. The record is an
  audit trail, **never** the attestation.
- **Honesty clause (carried from the seal ruling).** The manifest digest detects modification of a
  run record; it does **not** prove who wrote it. No wording in module, docstring or CLI may imply
  the journal authenticates anyone.
- **Done when** (all six, fixture-testable):
  1. a run snapshots every `configs/*.yaml` and the copies' digests match the manifest;
  2. editing a config **after** a run does not change what that run's snapshot says it used;
  3. re-using a run id **raises** rather than overwriting;
  4. a tampered `manifest.json` fails `read_manifest()`;
  5. a crashed run leaves no `outcome.json`, so it cannot read as success;
  6. a `panel-seal` invocation record carries **no** digest field.

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

      **GENERATED COLUMNS (r2.17), a third class beside declared and human-added:**
      `stereo_is_relative` and `label_disagrees_with_key` (tri-state:
      disagrees / agrees / unresolved). Recomputed on EVERY regeneration from the
      current compounds frame, NEVER carried from a prior sheet, OPTIONAL on read
      so legacy worksheets still load, and placed after `snapshot_label` so the
      reviewer sees them beside the evidence they qualify. `label_disagrees_with_key`
      is computed from the COMMITTED `configs/label_structure_reference.yaml`, never
      a live lookup, so a worksheet regenerates identically offline. The verdict must
      cover EVERY name sharing a key, not the first one encountered (F-01).

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
- **Done when** every row has a verdict and a DOI, or an explicit `unknown`, and the file is tracked by git **carrying no `name` column** (r2.17).

> **r2.17 — the tracked adjudication file drops `name`; the worksheet keeps it.** The worktree agent
> raised it (F-05): the filled sheet pairs a DrugBank `name` with a `canonical_inchikey`, and if that
> lands tracked it is exactly the `(name, structure)` association the principal's record-content
> invariant protects. Both halves matter, so they are separated rather than traded: **tracked**
> `configs/pgp_adjudication.csv` carries `canonical_inchikey`, `adjudicated_label`, `evidence_doi`,
> `adjudicated_by`, `adjudicated_on` — **no `name`** — preserving defect 23's fix that a human
> artifact must be versioned and attributable; the **generated, untracked** worksheet keeps `name`
> beside the evidence, because a reviewer adjudicating 60–90 minutes of labels cannot work from keys
> alone. T13/T15's interfaces above are amended in the same revision to match the code that now
> exists (generated columns; the legacy raise) — they had drifted, which the agent flagged rather
> than edited, the plan being hash-locked and the CTO's.

### T15 · Load adjudicated labels with provenance — **CA · 5 min**
- **Interfaces:**
  ```python
  def adjudicate_pgp_labels(worksheet: Path) -> pd.Series:
      """Index: canonical_inchikey. Values: 'yes' | 'no' | 'unknown'.

      **(r2.17) RAISES if the worksheet lacks `stereo_is_relative`** — a legacy sheet
      predating the flag. The error must name `write_adjudication_worksheet` and state
      that regeneration PRESERVES every verdict, DOI and attribution, so the reviewer
      is told how to fix it. NA was rejected: a label set silently missing the flag is
      the stale-flag failure one step later, and T17 cannot tell 'absent' from 'not
      relative'. The flag is written into `pgp_labels.parquet` as a real boolean so
      T17 receives it.

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
target now exists) · AM-5 ✓ (T5b is §1.2 *identity*, inside the boundary) · **AM-6 resolved**
(ADR-0002, 2026-09-02; the arithmetic is re-checked at M0b against real counts — r2.15 item 8).

> **AM-6 pointer** *(r2.15 item 8, editorial).* **AM-6 is resolved by ADR-0002** (accepted
> 2026-09-02). What remains is not the decision but the **arithmetic re-check against real M0b
> records**, which cannot happen before curation — so: *"AM-6 resolved (ADR-0002); arithmetic
> re-checked at M0b against real counts."* It stays **non-blocking for M0 slice 1** — no task here
> depends on the group-size threshold — while **M5 pre-registration remains gated on the re-check**.
> Defect 24's fix means T15/T17 *measure* the `yes`/`no` populations, so the check runs against real
> counts rather than estimates.

## 7a · Amendment r2 → r2.1 — CTO rulings E-1…E-5 (dispatch #11, 2026-08-31)

Five rulings from the CTO on the P0.1 report, re-issued by the principal. **No scope change** — four
wording corrections and one config path. Each is recorded inline at the section it amends.

| Ruling | Section | Change |
|---|---|---|
| **E-1** RATIFIED | T1, T11 | Nine keys present; eight always non-empty; `commit_change_rationale` non-empty **IFF** `source_commit != audited_commit`. Resolves a genuine self-contradiction between T1's "all eight non-empty" and T2's requirement that the rationale be empty on an unchanged commit. **T11 sign-off unblocked against fixtures.** |
| **E-2** RATIFIED | S3 | Assert against the *parsed* config. The old done-condition could never fail — pytest's default `norecursedirs` already skips `.venv`. |
| **E-3** RATIFIED | S4 | `test_monotonicity` skip reason names the **M1 ODE solver**, its actual blocker — not slice-3 splits. |
| **E-4** RULED (defect) | S7 | Probe set extended to **nested** paths. A top-level-only probe does not test the rule that git cannot re-include a file beneath an excluded directory. |
| **E-5** RULED (**data-loss fix**), **refined @ #18** | S9 | DVC remote must be absolute and outside every git tree — the r2 relative url resolved *inside* the worktree, so `git worktree remove` destroyed the only copy of the snapshot. **Refinement:** the url lives in gitignored `.dvc/config.local`, not committed `.dvc/config`. Committing a literal home path disclosed the account name to a public remote and gave other contributors a silent empty success on push — the same silent-success class E-5 exists to prevent. |

**Approval provenance:** these amendments were dictated by the CTO's ratified rulings and re-issued
verbatim by the principal in-session on 2026-08-31 with the instruction to apply them and continue.
They were not authored by the agent. `plan-approval.md` is re-signed to `r2.1` on that basis; the
hash moves `737a8d9 → <r2.1>`.

---

## 8 · Scope check

This plan stops at the identity and barrier-panel layer: **29 CA tasks and 5 human tasks**
(r1: 13 CA / 4 H), roughly 2 hours of agent work and 2 hours of human work.

Three adjacent things are **deliberately not here**:

1. **M0b — curation of 80–100 chip records** *(range narrowed by principal 2026-09-02, AM-6 resolved:
   the active-learning pool is v3 and leaves the PoC's sealed allocation, making it three-way —
   δ-calibration / conformal calibration / locked test — at ~20 conformal points per group, two
   groups. The Mondrian claim stays conditional; §5E forbids marginal coverage in terms. Every
   coverage figure is reported **with its confidence interval, per group**.)** Human-only, needs a protocol document rather than a task list, and it is the project's critical path. Its own plan.
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
