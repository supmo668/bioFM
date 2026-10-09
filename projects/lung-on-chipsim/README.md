# ChipSim — M0 Data Spine

Lung-on-chip exposure and barrier-response simulator. This directory currently contains
**slice 1 of milestone M0**: the DrugBank data spine through compound identity and the
barrier-panel layer.

> **Usability status — the pipeline is complete and cannot run.**
>
> Every stage is implemented and tested. Execution stops before the first one, because the
> fetch requires a source commit that only a human may pin (`T2`). This is by design, not a
> defect: five artifacts in this slice are *claims* rather than code, and no agent may
> manufacture them. See [Human-owned artifacts](#human-owned-artifacts).
>
> **What you can do today:** run the full test suite against committed fixtures.
> **What you cannot do:** produce any real data artifact.

---

## Status at a glance

| | |
|---|---|
| Agent-implementable tasks | **29 / 29 complete** |
| Human-owned artifacts | **0 / 5 delivered** |
| Tests (offline) | **284 passed / 6 skipped** |
| Tests (network-marked) | 15 passed / 1 skipped |
| Lint | `ruff check` + `ruff format --check` clean |
| Source / test volume | 1,622 / 3,530 lines |
| Real data artifacts on disk | **none** — `data/raw/drugbank/` absent |
| `configs/barrier_panel.yaml` | `ratified: false` |

Two quality-gate iterations are recorded in
`workstreams/lung-on-chipsim/plan/quality-gate-reports.md` (path from the repository root;
`../../workstreams/...` from this directory). Every test a reviewer proved
vacuous was re-run under mutation after fixing; all 7 that previously passed now fail.

---

## Architecture

Ten subpackages are scaffolded to the full target architecture so later milestones add files
rather than restructure. **Three carry slice 1**; the rest are deliberate placeholders.

```mermaid
graph TB
    subgraph active["Slice 1 — implemented"]
        ingest["<b>ingest/</b><br/>drugbank_snapshot.py<br/><i>465 lines</i>"]
        harmonize["<b>harmonize/</b><br/>ids · pgp_label · adjudication<br/>roster · contracts<br/><i>824 lines</i>"]
        evalpkg["<b>eval/</b><br/>provenance_block.py<br/><i>112 lines</i><br/><i>provenance block only;<br/>frozen evaluator is M0c</i>"]
        pipeline["<b>pipeline.py</b><br/>5-stage CLI entrypoint<br/><i>136 lines</i>"]
    end

    subgraph later["Later milestones — placeholders"]
        transport["transport/<br/><i>M1 · ODE core</i>"]
        occupancy["occupancy/<br/><i>M3 · binding</i>"]
        heads["heads/<br/><i>M2 · ADME heads / M4 · readout</i>"]
        uncertainty["uncertainty/<br/><i>M5 · calibration</i>"]
        acquire["acquire/<br/><i>M6 · acquisition</i>"]
        misc["encoders/ · surface/"]
    end

    pipeline --> ingest
    pipeline --> harmonize
    harmonize --> evalpkg

    classDef live fill:#e0ebe6,stroke:#2f6355,stroke-width:2px,color:#16201c
    classDef stub fill:#f0f2f0,stroke:#9aa8a2,stroke-dasharray:4 3,color:#5b6b64
    class ingest,harmonize,evalpkg,pipeline live
    class transport,occupancy,heads,uncertainty,acquire,misc stub
```

### Module responsibilities

| Module | Responsibility |
|---|---|
| `ingest/drugbank_snapshot.py` | Fetch the pinned snapshot by 40-hex commit; write `SHA256SUMS.json`; verify hashes; parse compound and protein-edge tables |
| `harmonize/ids.py` | Canonical InChIKey — salt strip, neutralize, tautomer canonicalize |
| `harmonize/pgp_label.py` | Three-way P-gp substrate label; resolves ABCB1 **from the panel config**, never hard-coded |
| `harmonize/adjudication.py` | Load human-adjudicated labels; reject a verdict lacking an evidence DOI |
| `harmonize/roster.py` | Validate the PoC compound roster before a human spends time filling it |
| `harmonize/contracts.py` | Provenance contract — nine keys, eight unconditional, conditional rationale |
| `eval/provenance_block.py` | Model-card data-provenance section |
| `pipeline.py` | `argparse` CLI; the entrypoint the n8n ETL export invokes |

---

## Data flow

Five stages, run as subcommands of `python -m chipsim.pipeline`. Nothing is passed in memory
between stages — **every handoff is a file on disk**, which is why a missing fetch halts the
whole chain rather than degrading it.

```mermaid
flowchart LR
    T2["<b>T2 · HUMAN</b><br/>pin 40-hex commit"]:::human
    T2 -.->|"blocks"| fetch

    fetch["<b>1 · fetch</b><br/>3 TSVs by commit"]:::stage
    verify["<b>2 · hash-verify</b><br/>recompute sha256"]:::stage
    parse["<b>3 · parse</b><br/>+ canonicalize"]:::stage
    ptests["<b>4 · provenance-tests</b><br/>pytest subprocess"]:::stage
    write["<b>5 · write</b><br/>parquet + sidecar"]:::stage

    fetch --> verify --> parse --> ptests --> write

    raw[("data/raw/drugbank/<br/>*.tsv + SHA256SUMS.json<br/><b>ABSENT</b>")]:::absent
    out[("drugbank_compounds.parquet<br/>+ .sha256 sidecar<br/><b>ABSENT</b>")]:::absent

    fetch -->|writes| raw
    raw -->|reads| verify
    raw -->|reads| parse
    raw -->|reads| write
    write -->|writes| out

    classDef stage fill:#e0ebe6,stroke:#2f6355,stroke-width:1.5px,color:#16201c
    classDef human fill:#f6e7db,stroke:#a6541f,stroke-width:2px,color:#16201c
    classDef absent fill:#fdf6f1,stroke:#a6541f,stroke-dasharray:5 4,color:#7a4a26
```

Notes that matter when reading the code:

- Stages **3 and 5 each independently re-read and re-canonicalize** from `raw_dir`. There is no
  shared in-memory state between subcommands.
- `write_compounds()` raises if `canonical_inchikey` is missing — canonicalization (`T5b`) must
  run before persistence (`T5a`).
- The parquet is written with `pyarrow` pinned to an exact version, `version="2.6"`,
  `compression=None`, sorted by `canonical_inchikey`. Parquet bytes are not stable across
  pyarrow versions and the `.sha256` sidecar records a digest over the serialized file.
- The parquet is DVC-tracked and gitignored; **the sidecar is git-tracked**, so a substituted
  artifact shows up in review.

---

## Human-owned artifacts

A task is agent-implementable if its done-condition is a test that can fail. A task is
human-owned if its output is a **claim** — something whose wrongness no test in this repository
would catch. A fabricated citation passes every schema check ever written, which is why these
five are absent rather than approximated.

```mermaid
flowchart LR
    T2["<b>T2</b> pin commit<br/><i>2 min</i>"]:::human
    T1["<b>T1</b> licence posture<br/><i>5 min</i>"]:::human
    T8["<b>T8</b> ratify 7 accessions + 7 faces<br/><i>10 min</i>"]:::human
    T18["<b>T18</b> curate roster<br/><i>30–45 min</i>"]:::human
    T14["<b>T14</b> adjudicate labels<br/><i>60–90 min</i>"]:::human

    T4a["T4a · fetch"]:::blocked
    T11["T11 · provenance tests"]:::blocked
    T9["T9 · panel join"]:::blocked
    T13["T13 · worksheet"]:::blocked
    T15["T15 · load labels"]:::blocked

    T20["<b>T20</b> θ priors · 6 fields<br/><i>20–30 min</i>"]:::human
    T28["<b>T28</b> (α, k_sink) prior<br/><i>15–20 min</i>"]:::human
    T21["<b>T21</b> 3–8 reference compounds<br/><i>20–30 min</i>"]:::human

    T23["T23 · M1 fit"]:::blocked
    T27["T27 · M1 gate"]:::blocked

    T2 -->|gates| T4a
    T2 -->|"records hash"| T1
    T1 -->|gates| T11
    T8 -->|gates| T9
    T18 -->|gates| T13
    T14 -->|gates| T15
    T20 -->|gates| T23
    T28 -->|gates| T23
    T21 -->|gates| T27

    classDef human fill:#f6e7db,stroke:#a6541f,stroke-width:2px,color:#16201c
    classDef blocked fill:#f7f9f8,stroke:#9aa8a2,stroke-dasharray:4 3,color:#5b6b64
```

**`T2` is the keystone** — two minutes of work that unblocks the entire provenance and fetch
phase, gating `T4a` and `T1` directly and `T11` transitively.

| Task | What a human must produce | Why not an agent |
|---|---|---|
| `T2` | A 40-char commit SHA personally resolved from `dhimmel/drugbank` | A plausible-looking SHA is indistinguishable from a real one until fetch fails |
| `T1` | Licence posture in your own words, incl. non-commercial commitment | It is a commitment, not a computation |
| `T8` | Seven UniProt accessions **and** seven `face` assignments checked by hand, then `ratified: true`; an entry may be deleted only on positive evidence of absence, never on silence in a database | A wrong accession or face *empties* a join — a failure that looks like success |
| `T18` | 20–40 inhaled/lung-relevant compounds with published exposure | Curation judgement; a roster is a claim about relevance |
| `T14` | Per-compound P-gp verdict with an evidence DOI | A fabricated DOI corrupts the M5 coverage claim invisibly |
| `T20` | Six device and physiology θ fields, each with a citation or an explicit `assumed: true` | A default is an agent-written biological number wearing the costume of a software convenience |
| `T28` | The `(α, k_sink)` transport prior, cited or explicitly uninformative | At three reference compounds the reported value is substantially prior-determined (Finding E), so this does real work on the result |
| `T21` | 3–8 compounds with an **independently published** on-chip transport measurement | It is the yardstick the M1 gate checks the model against; drawing it from the roster would make the test a subset of what is being tested |

**No agent may set `ratified: true`, write a biological number, or invent a DOI.** Genuinely
uncertain compounds stay `unknown` and are excluded from both calibration groups rather than
guessed into one.

---

## Filling the M1 inputs

Three of the five remaining human artifacts are the M1 fit's inputs, and each has a scaffold
an agent wrote and a validator that refuses what an agent must not supply. The scaffolds carry
no values; the validators are the only path into the fit.

```mermaid
flowchart TB
    S13["<b>S13</b> · agent<br/>configs/templates/theta_priors.scaffold.yaml<br/><i>6 fields · every value empty</i>"]:::agent
    S14["<b>S14</b> · agent<br/>configs/templates/transport_prior.scaffold.yaml<br/><i>2 entries · no numbers</i>"]:::agent

    T20["<b>T20</b> · human<br/>configs/theta_priors.yaml<br/><i>value + citation, or assumed with a width</i>"]:::human
    T28["<b>T28</b> · human<br/>configs/transport_prior.yaml"]:::human
    T21["<b>T21</b> · human<br/>configs/m1_reference_compounds.yaml"]:::human

    V1["<b>ThetaConfig.load</b><br/><i>refuses: empty value · wrong unit ·<br/>neither cited nor assumed · misspelled key</i>"]:::guard
    V2["<b>TransportPrior.load</b><br/><i>refuses: zero width ·<br/>uncited and unflagged</i>"]:::guard
    V3["<b>load_reference_compounds</b><br/><i>refuses: outside 3–8 ·<br/>duplicate key · uncited</i>"]:::guard

    FIT["M1 fit · T23"]:::blocked
    GATE["M1 gate · T27"]:::blocked

    S13 -->|"you copy and fill"| T20 --> V1 --> FIT
    S14 -->|"you copy and fill"| T28 --> V2 --> FIT
    T21 --> V3 --> GATE
    FIT --> GATE

    classDef agent fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef human fill:#f6e7db,stroke:#a6541f,stroke-width:2px,color:#16201c
    classDef guard fill:#dbeafe,stroke:#1d4ed8,color:#1e3a8a
    classDef blocked fill:#f7f9f8,stroke:#9aa8a2,stroke-dasharray:4 3,color:#5b6b64
```

```bash
# 1. Emit the scaffolds (idempotent while nothing is filled; refuses to blank your work)
uv run python -m chipsim.pipeline theta-scaffold
uv run python -m chipsim.pipeline transport-prior-scaffold

# 2. Copy them into configs/ YOURSELF and fill them. No agent step creates these paths.
cp configs/templates/theta_priors.scaffold.yaml    configs/theta_priors.yaml
cp configs/templates/transport_prior.scaffold.yaml configs/transport_prior.yaml

# 3. Check your own work the way the fit will, before the fit runs
uv run python -m chipsim.pipeline theta-check --theta configs/theta_priors.yaml
uv run python -m chipsim.pipeline transport-prior-check --prior configs/transport_prior.yaml
uv run python -m chipsim.pipeline reference-compounds-check --reference configs/m1_reference_compounds.yaml
```

`theta-check` exits non-zero on refusal and prints the cited/assumed split either way. **Two of
six fields entering as assumptions is a stated limitation, not a failure** — the run journal
reports the split and the paper carries it. What the validator refuses is silence: a value with
no citation and no `assumed: true` flag, where the reader cannot tell which one the result rests
on.

Three distinctions the validators enforce, each of which was a silent failure elsewhere in this
project before it was named:

| Distinction | What the loader does | Why |
|---|---|---|
| Absent is not unknown | an empty `value` raises; nothing is substituted | a substituted default is indistinguishable from a measurement once it is in the fit |
| Assumed is not cited | a value may enter uncited only with `assumed: true` | that flag is what makes it a stated gap the journal counts, rather than a quiet default |
| Typed is not checked | every `unit` must equal the schema's | a unit declared and never compared is decoration, and a value in the wrong unit would rescale the fit |

---

## Getting started

Supports Python 3.11–3.12 (`requires-python = ">=3.11,<3.13"`; RDKit wheel availability is the
binding constraint on the upper bound). 3.11 is the recommended version and the one the
quickstart below pins. Also needs [`uv`].

```bash
cd projects/lung-on-chipsim
uv venv --python 3.11
uv sync
```

`uv sync` already installs the `dev` dependency group; there is no
`[project.optional-dependencies]` table, so `--all-extras` would do nothing.

### Run the tests — this works today

```bash
uv run pytest -m "not network"     # 284 passed, 6 skipped — fixtures only
uv run pytest -m network           # 15 passed, 1 skipped — hits UniProt
uv run ruff check . && uv run ruff format --check .
```

Skipped tests are keyed to the absent human artifacts and **self-lift** once the artifact
appears — no code change needed.

### Run the pipeline — this does not work yet

```bash
uv run python -m chipsim.pipeline fetch --dest data/raw/drugbank --commit <40-hex>
```

Fails without `T2`'s pinned commit. `fetch_snapshot` raises `ValueError` on anything that is
not 40 hex characters, and it fetches **only** by pinned commit, never by a mutable ref such
as a branch name.

---

## Layout

```
projects/lung-on-chipsim/
├── chipsim/              # the package (3 of 10 subpackages populated)
├── configs/
│   ├── barrier_panel.yaml    # 7 accessions, ratified: false
│   ├── env.yaml              # paths + source coordinates, NON-BIOLOGICAL only
│   └── templates/            # S13/S14 scaffolds — EMPTY value slots, outside configs/ proper
│       ├── theta_priors.scaffold.yaml
│       └── transport_prior.scaffold.yaml
├── data/                 # raw/ interim/ processed/ — bulk payload DVC-tracked + gitignored;
│                         # provenance files, .dvc pointers and .sha256 digests stay git-tracked
├── orchestration/n8n/    # etl_drugbank.json workflow export
├── tests/                # 15 modules + 32 fixtures
├── CONTEXT.md            # domain glossary — read this before the code
└── pyproject.toml
```

`configs/theta_priors.yaml` and `configs/assumptions.yaml` are **deliberately absent**. Every
value in them is a human-entered biological number with a citation; no agent may create them.
Their absence is not a convention but the enforcement mechanism (ruling r2.37(c)), so
`chipsim theta-scaffold` refuses both paths by name and the scaffolds live one directory down in
`configs/templates/`, where no absence guard applies and nothing carries a value.

DVC remote resolves to an absolute path **outside every git worktree**, so that removing a
worktree cannot destroy the only copy of the snapshot.

---

## Provenance and licence

Data comes from [`dhimmel/drugbank`], a public snapshot of **DrugBank 4.2, downloaded
2015-03-19**, archived at `doi:10.5281/zenodo.45579` and redistributed as derived TSVs under
**CC BY-NC 4.0**.

- **Compound identity and drug→transporter/carrier edges only. Never affinities.**
- **Non-commercial only**, inherited from the source licence.
- **ChipSim never redistributes DrugBank.** The snapshot is DVC-tracked and gitignored; a test
  fails if any snapshot byte becomes git-tracked, in file *or* blob form.
- The snapshot **cannot support a coverage claim**. Anywhere the model card says DrugBank it
  must say **DrugBank 4.2 (2015-03-19 snapshot)**.

The staleness matters most for P-gp annotation. The uncertainty stack conditions on P-gp
substrate status, so a stale label would silently redefine the groups a coverage claim is
conditioned on. Hence the three-way label, the rule that absence of an edge is **never** read
as "not a substrate", and human adjudication against current literature.

---

## Known open items

- **`T16a` deferred** — n8n provisioning and end-to-end execution. The workflow JSON export and
  its entrypoint validation are present; standing up n8n is not.
- **`AM-6` unresolved** — the two-group calibration arithmetic. A *calibration point* is one
  curated chip record, never a compound; under that reading the two-group Mondrian veto needs
  ~200–240 records against an M0 target of 60–100. Gates M5 pre-registration, not M0. The
  current recommendation is to **pre-register a sample-size contingency** — evaluate the veto
  only if the sealed conformal bucket yields ≥30 points per group, otherwise report marginal
  coverage with binomial CIs and disclose the downgrade — with the threshold tested against the
  allocation *as written down before reading*, never a post-hoc re-cut.
- **Further ingestors not scheduled** — ChEMBL / BindingDB / TDC / LINCS ingestion is the same
  shape as this slice repeated. The plan's own scope check rules that building more parsers
  first "would feel productive and would move the actual completion date not at all". The next
  slice is **M0b** curation, which is human-owned, then **M0c**, the frozen evaluator.
- **Panel integrity after ratification** — `T7a` closed this: `ratified_panel_sha256` is a
  seal over the panel, its ratification fields and its filename, and `load_ratified_panel`
  raises on a missing or mismatched seal. It is an **unkeyed digest over public content**, so
  it detects a later edit to `configs/barrier_panel.yaml`; it does **not** prove a human
  ratified the panel, and nothing in the repo does.
- **Global Constraint (4) — how much the TTY gate actually buys.** The constraint reserves
  `chipsim panel-seal` to a human. It now has its **first** technical enforcement: sealing
  refuses to run without an interactive terminal on stdin, so a headless agent session fails
  instead of producing a valid live seal. **State the residual limit at its real size.** The
  gate converts an *accident* into a *deliberate circumvention* — that is the entire claim.
  It does not establish who ran the command, it is not evidence a human sealed anything, and
  an agent that deliberately allocates a pty defeats it completely. The digest remains unkeyed
  over public content: it **detects a later edit**, never who ratified it — and an editor who
  removes the seal line bypasses the detection entirely. Closing that
  gap needs real signing against a pinned human-held key, which is a **v2 decision, deferred**.

[`uv`]: https://docs.astral.sh/uv/
[`dhimmel/drugbank`]: https://github.com/dhimmel/drugbank
