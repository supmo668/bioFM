# Academic publication pipeline — design spec

> **Status:** design approved by the principal 2026-09-24; **not implementable yet** —
> blocked on an n8n instance. See §7.
> **Author:** bioFM/matthew-mo/cto. **Platform decision:** n8n. Make.com is explicitly
> out of scope and nothing was ever created there.

## 1. Why this exists

The repo currently has **two** publishers that do overlapping work:

| file | size | venues |
|---|---|---|
| `scripts/publish/submit.py` (+ `publish.yml.template`) | 19 KB | zenodo, zenodo_sandbox, figshare, osf |
| `projects/perturb-seq-eval/scripts/publish/submit_to_venues.py` | 30 KB | zenodo, zenodo_sandbox, figshare, osf |

So "is there a duplicate pipeline already?" — **yes, there are two**, and they cover the
same four venues. This spec does not add a third. It **consolidates those two into one
CLI** and puts n8n in front of it as the orchestrator.

## 2. Architecture — follow the repo's own n8n convention

`projects/lung-on-chipsim/orchestration/n8n/etl_drugbank.json` is the existing precedent,
and it is worth copying exactly. Its five nodes are all
`n8n-nodes-base.executeCommand`, shelling out to a Python entrypoint
(`projects/lung-on-chipsim/README.md:83` — *"the entrypoint the n8n ETL export invokes"*).

**Consequence, and it is the most important decision in this spec:** the venue adapters
live in **Python**, not in n8n HTTP nodes. n8n only sequences, retries and notifies.

Why this is the right shape here:

- **Credentials stay in Infisical → environment.** No secret is duplicated into an n8n
  credential object, so there is one place to rotate. "Create connector and credentials"
  therefore means *a Python adapter plus an Infisical key*, not an n8n credential record.
- **The logic is testable without n8n.** Six venue adapters behind `pytest` beats six
  HTTP nodes you can only exercise by firing the workflow.
- **It is reviewable.** A diff on an adapter is readable; a diff on exported n8n node JSON
  is not.
- **It survives the platform.** If n8n is later replaced, the adapters are untouched.

```
n8n workflow: publish_academic
  [trigger]                     manual | webhook
    -> resolve-run-vars         PUBLICATION_ROOT, TOPIC, VERSION, MODE
    -> validate                 publish validate --all   (fails closed)
    -> fan out per venue:
         publish submit --venue <v> --mode <publish|update>
    -> archive-assets           -> $PUBLICATION_ROOT/<topic>/
    -> notify-slack             one formatted message, success or failure
```

## 3. Venue matrix

**Honest status per venue.** Confidence is mine; anything marked *verify* must be checked
against live API docs by the implementer before a line is written, not taken from here.

| venue | auth | publish | update / new version | confidence |
|---|---|---|---|---|
| **Zenodo** | personal access token, scopes `deposit:write` + `deposit:actions` | deposit → upload → publish | has an explicit new-version action | high — already implemented twice in-repo |
| **Figshare** | personal token | article create → upload → publish | versioned on re-publish | high — already implemented |
| **OSF** | personal access token | node + file upload via `osf.io` API v2 | file/node update | high — already implemented |
| **Dataverse** | API token | native REST **or** SWORD | dataset draft → publish | medium — *verify* which of the two the target installation accepts; they differ per host |
| **Dryad** | API token | v2 REST, DOI minted on publish | versioned | medium — *verify* current v2 surface |
| **Software Heritage** | bearer token | SWORD deposit, returns an SWHID | re-deposit | medium — *verify* SWORD flavour and the metadata schema it demands |
| **OpenAIRE** | — | **see §3.1 — probably do not build this** | — | low |
| **arXiv** | — | **no public submission API** | — | high — submission is a web form; the arXiv API is read/search only |
| **bioRxiv** | — | **no public deposit API** | — | high |

### 3.1 OpenAIRE is probably redundant — flagging before effort is spent

OpenAIRE is principally an **aggregator**: it harvests from repositories rather than
being deposited into, and Zenodo is one of its harvested sources. If the pipeline already
deposits to Zenodo, the record is expected to surface in OpenAIRE **without a separate
connector**. Recommend: **do not build an OpenAIRE adapter.** Instead, after the Zenodo
step, record the expectation and verify the record appears. If a genuine OpenAIRE deposit
path is wanted, that needs its own investigation — it is not a sibling of the others.

### 3.2 arXiv and bioRxiv — prepare-only, and the pipeline must say so

Neither accepts a programmatic submission. The pipeline must **not** pretend otherwise.
For these two, `--mode prepare` only:

1. builds the submission bundle,
2. validates the metadata the venue will demand,
3. writes a manual-upload checklist into the topic folder,
4. reports venue status **`PREPARED (manual upload required)`** — never `PUBLISHED`.

A run where only these two ran is **not** a successful publish, and the Slack message
must not read as one.

## 4. Run variables

| variable | meaning | default |
|---|---|---|
| `PUBLICATION_ROOT` | asset root, the principal's named run variable | `bioML-publication` |
| `TOPIC` | slug naming this publication's folder | **required, no default** |
| `VERSION` | version label recorded in the manifest | required for `update` |
| `MODE` | `publish` \| `update` \| `prepare` | `publish` |
| `VENUES` | subset to run | all enabled |

`TOPIC` has no default deliberately: a defaulted topic silently co-mingles two
publications in one folder, which is unrecoverable after the fact.

## 5. Asset layout

```
bioML-publication/                        <- $PUBLICATION_ROOT
  <topic>/                                <- e.g. agent-confidence-entropy/
    manifest.json                         run vars, git SHA, UTC timestamps, per-venue outcome
    bundle/                               exactly what was uploaded, byte-for-byte
    receipts/
      zenodo.json                         DOI, record id, concept DOI, response
      figshare.json
      osf.json
      ...
      arxiv.checklist.md                  prepare-only venues land a checklist, not a receipt
    logs/
      <utc-timestamp>-<mode>.log
```

Two rules that make this worth having:

- **`bundle/` is what was actually sent**, not what was meant to be sent. It is the only
  way to answer "what is in DOI X?" a year later.
- **`manifest.json` records the git SHA and every resolved run variable.** This is the
  same standing rule that the perturb-seq-eval artifacts violated (see dispatch #202):
  a run that does not record its own config cannot be reproduced. Do not repeat it here.
- Re-running the same `TOPIC` **appends** a receipt and a log; it never overwrites one.

## 6. Slack notification

One message per run, posted after all venues resolve. It must state the failures as
plainly as the successes — a notification that only reports good news is the silent-failure
pattern this repo has filed against itself repeatedly.

```
📦 bioML-publication · <topic> · <MODE>
Version <version> · <git-sha-short> · <utc timestamp>

✅ Zenodo      10.5281/zenodo.NNNNNN
✅ Figshare    10.6084/m9.figshare.NNNNNN
✅ OSF         osf.io/xxxxx
⚠️  Dryad       PREPARED — awaiting manual step
❌ Dataverse   FAILED — 401 from <host> (token scope?)
📋 arXiv       PREPARED (manual upload required)

3 published · 2 prepared · 1 failed
Assets: bioML-publication/<topic>/
```

- Overall status is **failure if any enabled venue failed**, regardless of successes.
- `PREPARED` never counts toward `published`.
- Never put a token, or a URL containing one, in the message.

## 7. Blockers — nothing can be built past the adapters until these clear

1. **No n8n instance.** `projects/lung-on-chipsim/README.md:267` already records this as
   deferred **T16a**: *"n8n provisioning and end-to-end execution. The workflow JSON export
   and its entrypoint validation are present; standing up n8n is not."* This pipeline
   inherits that blocker. Needs: an instance (cloud or self-hosted) plus its API
   key / MCP endpoint.
2. **No n8n MCP server in the session.** Confirmed by search. The principal has stated one
   will be connected.
3. **Slack is not connected** — only `authenticate` / `complete_authentication` stubs are
   present, so no channel can be posted to yet. Needs the OAuth completion and a target
   channel.
4. **Credentials.** Six venues need six tokens. Only Zenodo is asserted to exist (§8).

**What is NOT blocked, and should therefore be built first:** the consolidated Python
`publish` CLI and its venue adapters, with the six adapters behind tests and a dry-run
mode. That is the majority of the work, it needs no n8n, and it is what the n8n workflow
will call.

## 8. Credential map — names only

n8n is **not** given credential objects (§2). Adapters read the environment; Infisical is
the source of truth and `.env` is a generated local convenience, never hand-maintained.

| env var | Infisical key | status |
|---|---|---|
| `ZENODO_TOKEN` | `ZENODO_TOKEN` | principal states it is present — **unverified, see below** |
| `ZENODO_SANDBOX_TOKEN` | same | unknown |
| `FIGSHARE_TOKEN` | same | not established |
| `OSF_TOKEN` | same | not established |
| `DATAVERSE_TOKEN` + `DATAVERSE_BASE_URL` | same | not established |
| `DRYAD_TOKEN` | same | not established |
| `SWH_TOKEN` | same | not established |

**Correction on record.** An earlier CTO statement that `ZENODO_TOKEN` was "absent from
all three Infisical environments" was **wrong**. The local Infisical CLI is authenticated
as a principal who is **not a member** of the bioFM project and returns
`403 Forbidden — You are not a member of this project`; an exit-code existence check read
that fetch failure as absence. The Infisical **MCP** identity does have project access.
The token's presence is therefore **unverified, not absent**, and it will be read through
the MCP at credential-configuration time rather than now — so the value stays out of the
session transcript.

This is the same defect family as the five ambient-state findings already filed in
`.claude/aiadlc-feedback/`: *a check derived a correctness-relevant answer from something
adjacent to the thing it described.* Here the adjacent thing was an exit code that
conflated "no such secret" with "no such membership".

## 9. Build order

1. Consolidate `scripts/publish/submit.py` + `submit_to_venues.py` into one CLI. Resolve
   their behavioural differences explicitly rather than picking one — they are 19 KB and
   30 KB of overlapping logic and the differences are where the bugs are.
2. Adapters for the three established venues, behind tests, with `--dry-run`.
3. Adapters for Dataverse, Dryad, Software Heritage — **verify each API surface first**.
4. `prepare` mode for arXiv / bioRxiv, emitting checklists.
5. Asset archive + `manifest.json` (git SHA, resolved vars).
6. Slack formatter — unit-tested against a failure case, not only a success case.
7. `orchestration/n8n/publish_academic.json`, matching the `etl_drugbank.json` convention.
8. Stand up n8n; import; end-to-end on **Zenodo sandbox** before any live deposit.

Step 8 is the first step that can touch a live repository. Nothing before it publishes
anything.
