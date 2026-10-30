# Using ChipSim (`lung-on-chipsim`)

What you can **do** with the `chipsim` command line today: the commands that exist, what each one
needs from you, and what each produces. It does not explain how the pipeline works internally, and
it reports no scientific result — this is a how-to-use document, not the paper.

**Verified at commit `ac2e2e8`.** Every command below was confirmed by running its own `--help` at
that commit, not from recollection. If a command here does not exist in your checkout, your
checkout is not this commit.

## Running it

Each module under `projects/` owns its dependencies; there is no root project. Run everything from
the module directory:

```bash
cd projects/lung-on-chipsim
uv sync --all-extras          # dependencies, including the sandbox extra
uv run chipsim --help         # the command list, straight from the tool
```

`uv run chipsim` is the console script; `uv run python -m chipsim.pipeline` is the same program.

## Two kinds of command, and the difference matters

**Approval-gated** — `fetch`, `hash-verify`, `parse`, `provenance-tests`, `write`,
`adjudication-worksheet`. Each prompts before it runs and accepts:

- `--yes` — approve without the prompt. The run journal records that the approval was
  non-interactive, so an unattended run is never indistinguishable from an answered one.
- `--approved-by WHO` — who approved, when it was not the operator at the terminal. Recorded
  **verbatim**; omit it and the field is simply absent. It is never defaulted and never inferred.

**Not gated** — `adjudication-export`, `panel-seal`, the two `*-scaffold` commands, and the four
`*-check` commands. The checks are read-only; the scaffolds write only empty templates.

## What each command takes and produces

| Command | You give it | You get |
|---|---|---|
| `fetch` | `--dest`, `--commit` | the pinned source snapshot downloaded to `--dest` |
| `hash-verify` | `--dest` | sha256s recomputed against the manifest; a mismatch is reported, never repaired |
| `parse` | `--raw-dir` | compounds and protein edges parsed from the snapshot |
| `write` | `--raw-dir`, `--out` | the compound frame persisted to `--out` (a parquet) |
| `provenance-tests` | `--tests` (optional) | the provenance contract suite, run |
| `adjudication-worksheet` | `--raw-dir`, `--roster`, `--panel`, `--out`, `--exclusions`, optional `--label-reference` | one worksheet row per roster entry, for a human reviewer to fill |
| `adjudication-export` | `--worksheet`, `--out` | the filled worksheet projected to the five tracked columns |
| `panel-seal` | `--panel` | a tamper-evident digest written over a ratified panel |
| `theta-scaffold` | `--out`, `--force` | an **empty** theta template — six fields, every value and citation blank |
| `transport-prior-scaffold` | `--out`, `--force` | an **empty** transport-prior template |
| `theta-check` | `--theta` | validation of a filled theta file, exactly as the fit would read it |
| `transport-prior-check` | `--prior` | validation of a filled transport-prior file |
| `reference-compounds-check` | `--reference` | validation of the M1 reference-compound file |
| `sourcing-check` | `--worksheet` | validation that no value in a sourcing worksheet lacks its quote, DOI and confirmed-DOI flag |

Two further tools are run as modules rather than subcommands:

```bash
uv run python -m chipsim.harmonize.merge_report --raw-dir … --out …   # merge report
uv run python -m chipsim.ingest.drugbank_snapshot --dest … --commit … # snapshot ingest
```

## The ordinary path

```bash
uv run chipsim fetch       --dest data/raw/drugbank --commit <40-hex source commit>
uv run chipsim hash-verify --dest data/raw/drugbank
uv run chipsim parse       --raw-dir data/raw/drugbank
uv run chipsim write       --raw-dir data/raw/drugbank --out data/processed/drugbank_compounds.parquet
```

`--commit` is the 40-hex `source_commit` recorded in the snapshot's `provenance.yaml`; it is a pin,
not a label, and the ingest tool will tell you where it reads it from.

## Steps a person must do, which no command will do for you

- **Fill the adjudication worksheet.** `adjudication-worksheet` emits it and
  `adjudication-export` publishes it, but the verdicts are a human judgement. The export
  **refuses** any extra column a reviewer added rather than silently dropping it, and **refuses to
  blank a verdict** the tracked file already carries. It drops the compound-name column by design:
  a name beside a structure key is not tracked here.
- **Seal a ratified panel.** `panel-seal` **requires an interactive terminal** and refuses to run
  when stdin is not a TTY, so a headless path fails rather than quietly producing a seal. Read its
  `--help` before relying on it: the digest is unkeyed over public content, so it records
  tampering but does **not** prove a human ran it.
- **Fill the M1 inputs.** The scaffolds write templates with every value blank and every field
  flagged `assumed`. Filling them is reserved to a person.

## What is NOT usable yet — stated, not implied

- **There is no simulate or fit subcommand.** The transport model exists as library code, but
  `chipsim --help` exposes no command that runs it. You cannot produce a model result from this
  CLI today.
- **The M1 input path is deliberately empty.** `theta-scaffold` and `transport-prior-scaffold`
  produce blank templates, and the matching `*-check` commands refuse an unfilled one — by design,
  with a reason. Verified at this commit: running `transport-prior-check` on a fresh scaffold
  exits with ``transport prior REFUSED: `alpha_prior.mean_log` is empty.`` So everything
  downstream of those inputs is blocked until a person fills them, and the block is loud.
- **`theta-scaffold` will not write two specific paths.** It refuses `configs/theta_priors.yaml`
  and `configs/assumptions.yaml`. Their absence is itself an enforcement mechanism: no agent
  writes a scientific value into this project, and a guard asserts those files do not exist.

## Things worth knowing before you run anything

- **A mismatch is reported, never routed around.** `hash-verify` and the `*-check` commands are
  built to refuse and explain, not to repair. A refusal is the product.
- **Fixtures under `tests/fixtures` are read-only**, and `PROVENANCE.md` is human-authored only.
- **Every run is journalled**, including which approval mode was used.
- Before committing, run the module loop: `uv run ruff format .`, `uv run ruff check --fix .`,
  `uv run ty check chipsim`, `uv run pytest -q`. Note that `pytest -q` is **unselected** and
  includes tests that reach a live remote endpoint; `-m "not network and not integration"`
  deselects those, and some tests also need snapshot bytes that are not in the repository.

## Where to look next

- [`README.md`](../../README.md) — what the repository is.
- [`docs/hacp/lung-on-chipsim/`](../hacp/lung-on-chipsim/) — project state, decisions and risks,
  mirroring Notion, which is the source of truth for review.
