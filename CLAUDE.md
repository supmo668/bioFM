# bioFM — agent operating instructions

Read this before you write anything. It is short on purpose; each section points at the document
that owns the rule.

## Orientation

| Need | Go to |
|---|---|
| What the contexts are and how they relate | [`CONTEXT-MAP.md`](CONTEXT-MAP.md) |
| What the repository is and how to run it | [`README.md`](README.md) |
| Project state, decisions, risks (human review surface) | [`docs/hacp/`](docs/hacp/) — mirrors Notion, which is the source of truth |
| Per-module substance and quality gate | the worktree agents in [`.claude/agents/`](.claude/agents/) |

## HACP — read the contract before any update

**Any write to an HACP surface — a Notion row under the HACP Index, or a file under
`docs/hacp/` — requires reading the operating contract first:**

| Document | Where | What it governs |
|---|---|---|
| **HACP — Governance & Index Design** | <https://app.notion.com/p/313fda9448094029904f344523d5bd01> | the operative contract: the L0–L3 layer ladder, the human review pattern, the writer contract, the canonical property ontology, index view membership |
| **HACP Index** (database) | <https://app.notion.com/p/3e5749bd250d806899f1d04b1053d1e7> | membership, ownership (`Indexed by`), `Granularity`, `Status` |
| **Project sync map** | e.g. [`docs/hacp/lung-on-chipsim/notion-map.json`](docs/hacp/lung-on-chipsim/notion-map.json) | every floor page's Notion URL and last `synced` date |

`reference/REFERENCE-HACP.md` is cited by the governance page but ships with the airdlc plugin and
is **not in this checkout** — the Notion page above is the surface to read.

### The writer contract, in force on every HACP write

1. **Before writing** — load the current page, the data-source schema, the owning index and the
   relevant view. Resolve `Indexed by` → `Granularity` → `Surface skill` → source identity. Reuse a
   canonical artifact rather than create a duplicate. If a required control cannot be resolved,
   **stop and state the gap** rather than inventing metadata.
2. **While writing** — keep the human explanation at its declared level, put detail behind inline
   entries, preserve unsupported blocks and source pointers, use only existing canonical properties.
3. **After writing** — reload the affected pages, query the owning index, and check membership,
   depth, source identity, inline-link destinations and human-view visibility. **Confirm no
   unintended duplicate ownership or higher-level detail dump was introduced.** This step is not
   optional and it is the one that gets skipped.

### What a layer may hold

| Layer | Reader's task | Page contract |
|---|---|---|
| L0 — Overview | find the right topic | current direction and a small set of entry points; no implementation dump |
| L1 — Review | understand and decide | takeaway, compact explanation, material risks, the explicit ask, inline drill-downs |
| L2 — Detail | understand and execute | requirements, designs, plans, interfaces, algorithms, operating rules |
| L3 — Evidence | verify a claim | sources, tests, receipts, runs, appendices, historical snapshots |

Each indexed page declares **exactly one** `Granularity`. Mixed-depth material is **split**, never
accommodated by expanding a human surface. Aim for one-screen comprehension.

### An index is navigation, not administration

An **Index** page carries entry points and nothing else: no status table, no timeline, no decision
history, no prose summary of what a child page says. *Inline entries are navigation, not copied
artifact content.* If you find yourself writing a number, a date or a verdict onto an index, it
belongs on the page that owns it — create or reuse that page and link it.

> **Recorded failure mode (2026-10-14).** The ChipSim index had accumulated a header property
> table, a status table, a timeline, a nineteen-row decision history and two prose summaries: 175
> lines on a navigation surface. Nothing in the repository told an agent to read the governance
> contract before an HACP write, and the after-writing check above was never run. The content was
> moved to `docs/hacp/lung-on-chipsim/status-and-history.md`; this file is the amendment.

### A review surface is a Notion row. In-app-only artifacts are BANNED

**Principal ruling, 2026-10-31:** *"'artifacts' should now just be notion links organized in HACP
index, completely ban in-app only artifacts as that's not the designed destination review surface."*

So: **no review surface may exist only as a `claude.ai/artifact/...` page.** Every human review
surface is a Notion row under the HACP Index, reached from its project index. An artifact may be a
rendering on the way there; it is never the destination, and it is never what a document cites.

**Why this is a correctness rule, not a preference.** A `claude.ai` artifact URL is
**account-scoped**, not merely ephemeral. It resolves for its author and for nobody else. So an
artifact citation is unreadable for every other reader the moment it is written, and dead for every
reader of a published paper from the moment of publication. The failure is silent: the author sees
the page and assumes everyone does.

**Recorded instance (2026-10-31).** `projects/lung-on-chipsim/configs/poc_compounds.yaml` cited an
artifact for its full per-row evidence table. The artifact no longer resolves, and the table is
**unrecoverable** — the 13 rejection reasons and the per-row confidence tiers are gone; only the
aggregate counts survived because they had been written into a tracked file. The pointer was removed
rather than re-pointed, and no substitute source was invented. That loss is what this rule exists to
prevent.

**On a write:** put the content in the Notion row. If a rendering helps a human read it, publish one
and link it **from** the row, never the reverse. **Never cite an artifact URL from a tracked file, a
paper, a config, or any page that outlives the session.** Migrating the artifact-only surfaces that
predate this ruling is open work, not a licence to create more.

### Sync discipline

Notion is the source of truth for human review and communication (principal, 2026-10-03). The floor
under `docs/hacp/` mirrors it. After editing a floor page, mirror it to its Notion row and bump
`synced` in that project's `notion-map.json`, then:

```bash
uv run python scripts/hacp_linkcheck.py docs/hacp
uv run python scripts/hacp_sync_check.py docs/hacp/lung-on-chipsim
```

`.github/workflows/hacp-docs.yml` runs the sync check on every push and pull request touching
`docs/hacp/`, so an un-mirrored edit fails CI.

## Standing scientific constraints

These are not style preferences. They are the project's integrity model, and a validator enforces
each one.

- **No coding agent writes a biological number.** The agent writes the schema and the validator
  that rejects an unsourced entry. *A fabricated citation passes every schema check ever written.*
  Amended 2026-10-08 for M1 inputs only: an agent may **draft** a value from a source it has read,
  marked with its provenance class, and a principal ratifies it. Drafted is not delivered.
- **Unbacked data cannot be used.** Every filled row declares `cited`, `derived` or `assumed`;
  `cited`/`derived` need a verbatim quote and a confirmed DOI, `assumed` needs a stated width and
  must carry no quote. Enforced by `chipsim.transport.sourcing`.
- **Never write an InChIKey or a DrugBank accession from memory, and never publish DrugBank record
  content.** Principal ruling #120 (2026-09-15), re-affirmed as governing 2026-10-31 (lung approvals
  row 80): record content is DrugBank's own fields — names, synonyms, descriptions, targets — **any
  DB accession**, and the `(accession, name, structure)` tuple. *"A bare canonical structure
  identifier is NOT record content"*: a structure beside a substance name is permitted **when the
  pair cites a public source** (PubChem CID + retrieval date). This replaces a broader agent-written
  line ("never pair an identifier with a substance", 2026-10-14) that no ruling supported.
- **Never edit hash-covered evidence** under `workstreams/lung-on-chipsim/qgr/` or
  `workstreams/lung-on-chipsim/paper/`.
- **`configs/theta_priors.yaml` and `configs/assumptions.yaml` must not exist** in
  `projects/lung-on-chipsim/` — the S6 absence guard asserts it.
- **Unratified findings never reach the trunk** (principal, 2026-10-31, lung approvals rows 83-86). A
  findings-staging ledger lives on a dedicated `<agent>-staging` branch that is never a PR head; the CTO
  mirrors it to a Notion row, where the principal ratifies; accepted content then moves to its real
  destination through a normal PR and the staging file is deleted. MYB-8 adds the CI guard.
- **A proxy 403 or egress block is reported, never retried or routed around.** See
  `/root/.ccr/README.md`. Do not write a value out of a search snippet; read the primary source.

## Housekeeping

Each module under `projects/` owns its `pyproject.toml` and `uv.lock`; there is no root project.
Run the loop from the module directory:

```bash
cd projects/lung-on-chipsim
uv sync --all-extras                        # dependencies, incl. the sandbox extra
uv run ruff format . && uv run ruff check --fix .
uv run ty check chipsim                     # types
uv run pytest -q                            # the suite
```

Repository-level scripts run from the root with `uv run python <script>` (no project needed).
Run the module loop before every commit. Prefer `uv` over bare `pip`/`python`. CI mirrors it; a
local pass is the cheap half of the loop.
