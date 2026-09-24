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

---

## 10. n8n connection notes (2026-09-24)

### 10.1 The instance exists — T16a is partly resolved

Probed without credentials:

| probe | result | meaning |
|---|---|---|
| `POST https://n8n.syntropyhealth.bio/mcp-server/http` | **401** | host, TLS and path are all correct; auth required |
| `GET https://n8n.syntropyhealth.bio/` | **200** | n8n is up and serving |

This contradicts `projects/lung-on-chipsim/README.md:267`, which records T16a as deferred
because *"standing up n8n is not"* present. **It now is.** That README line is stale and
should be corrected when lung-on-chipsim next touches it — the deferred half of T16a is
now only the *end-to-end execution*, not the provisioning.

### 10.2 Connecting the MCP server — the token is the only blocker

The configuration supplied by the principal carries a **placeholder**
(`<YOUR_ACCESS_TOKEN_HERE>`), so it cannot be used as-is. The real bearer token is needed.

**Add it with the CLI rather than by hand-editing JSON**, so the token never passes through
a session transcript:

```bash
claude mcp add --transport http n8n-mcp \
  https://n8n.syntropyhealth.bio/mcp-server/http \
  --header "Authorization: Bearer <REAL_TOKEN>"
```

**Scope matters, for a reason that is easy to miss.** Use the default (`local`) or
`--scope user` — both store in `~/.claude.json`, outside the repo. Do **not** use
`--scope project`: that writes `.mcp.json` into the repo, and `.mcp.json` is **not** covered
by `.gitignore` (checked), so a bearer token placed there is one `git add` away from being
committed. If a project-scoped server is ever wanted, add `.mcp.json` to `.gitignore` first.

Existing user-level MCP servers, for reference: `heygen`, `infisical`, `kapso`, `logfire`,
`vibiz`, `wandb`. No n8n server is configured yet.

### 10.3 Migration — staged, and the removal is gated

The principal's instruction is to **place these notes now** and **migrate, removing the
existing pipeline, after the workflow is created in n8n**. Sequenced:

| stage | gate to enter it |
|---|---|
| 1. Connect the n8n MCP server | the real bearer token |
| 2. Create the workflow in n8n | MCP connected |
| 3. Prove it end-to-end on **Zenodo sandbox** | workflow exists; principal's go for any live deposit |
| 4. **Remove the superseded pipeline** | stage 3 demonstrably passed |

**Stage 4 must not precede stage 3.** `scripts/publish/submit.py` and
`projects/perturb-seq-eval/scripts/publish/submit_to_venues.py` are 49 KB of working code
covering four venues; deleting them before the replacement has published something leaves
no path to publish at all. Removal should also be its own reviewable commit, not folded
into the migration, so it can be reverted independently.

### 10.4 An architectural tension the principal should resolve at stage 2

§2 of this spec put the venue adapters in **Python**, with n8n only sequencing, following
the `etl_drugbank.json` precedent. "Remove the pipeline" may mean either:

- **(a) remove the *duplication*** — consolidate the two publishers into one CLI that n8n
  calls. §2 stands unchanged; "the pipeline" that goes away is the redundant second copy.
- **(b) remove Python entirely** — reimplement all six venues as n8n HTTP nodes.

These are materially different, and (b) has costs worth naming before it is chosen: every
credential gets duplicated into an n8n credential object, so there are two places to rotate
instead of one; the venue logic becomes untestable without a live n8n; node-JSON diffs are
not meaningfully reviewable; and the adapters do not survive a change of platform. (b) also
departs from the repo's only existing n8n precedent.

I recommend **(a)**. But this is the principal's call, and it should be made **before**
stage 2, because the workflow built in n8n differs completely between the two.

**Dispatch #203 is written for (a)** and is therefore **on hold** pending this decision —
it would otherwise have the agent consolidate a CLI that (b) would delete.

---

## 11. n8n instance inventory (2026-09-24, post-connection)

**Connected.** `n8n-mcp` registered at **user scope** in `~/.claude.json` (outside the repo,
so no token is committable). `claude mcp list` reports `✔ Connected`. Server identifies as
**n8n MCP Server v1.1.0** and advertises 26 tools, including `create_workflow_from_code`,
`validate_workflow`, `test_workflow`, `publish_workflow`, `list_credentials` and
`get_sdk_reference`. Token stored as `N8N_MCP_TOKEN` in Infisical `bioFM/dev` (v1).

The server's own instructions state: *"You MUST call `get_sdk_reference` … before writing
workflow code. Do not guess."* Whoever builds the workflow: do that first.

### 11.1 This is shared production infrastructure, not a sandbox

**82 workflows, 49 credentials**, most of them live. The instance hosts at least four
distinct tenants:

| family | examples | state |
|---|---|---|
| XEOs content/social | `00-MAIN: Unified Publisher v5 (master)`, `XEOs — Subwf: <platform> Publisher` ×11 | mostly active |
| CRA | `cra-w1-cal-sync` … `cra-w8-escalation` | all active |
| GTM | `[GTM] instrument-read service`, `[GTM] Eden Main Character` | mixed |
| scratch / held | `ZZ-TEMP …`, `ZZ RELEASE …`, `ZZ-SCRATCH …`, `[template] …` | inactive by convention |

**Consequences for this pipeline, and they are not cosmetic:**

- **Do not create anything unprefixed.** The instance has a working naming convention
  (`00-MAIN:` masters, `01-` … `06-` stage prefixes, `XEOs — Subwf:` for sub-workflows,
  `[GTM]` for tenancy, `ZZ-` for scratch). An unlabelled workflow is invisible to the
  people maintaining the other 82.
- **bioFM is a different product from SyntropyHealth/XEOs.** Recommend a tenancy prefix:
  **`[bioFM] 03-PUBLISH: Academic Repositories`**, following the `[GTM]` precedent, and
  `[bioFM] Subwf: <venue>` for per-venue children if it is split.
- **Build inactive, and prefer a `ZZ-`/`[template]` name until proven**, per the instance's
  own convention for unproven work. Do not `publish_workflow` until stage 3 of §10.3 passes.
- **Other agents operate here** (gtm-xeos, cra, GTM coordinators). Creating or renaming in
  this instance is a cross-team action, not a private one.

### 11.2 Two blockers resolved, one narrowed

- **Slack is no longer blocked.** A `Slack Bot — NoiseMaker` (`slackApi`) credential already
  exists in n8n. §6's notification can be built entirely inside n8n using it — the
  Claude-side Slack MCP (which is still only `authenticate` stubs) is **not needed**. Still
  needed from the principal: **which channel** to post to.
- **Asset storage has an existing path.** A `Google Drive account` credential exists, and
  `04-MEDIA: Drive Bundle (per-round subfolder + assets)` already implements
  per-run-subfolder asset bundling. If `bioML-publication/<topic>/` should live in Drive
  rather than on disk, that sub-workflow is the precedent to copy — worth a look before
  reimplementing.
- **No academic venue credential exists.** Of 49, none is Zenodo, Figshare, OSF, Dryad,
  Dataverse or Software Heritage. All six still need tokens. Note the instance already has
  an Infisical-sourcing convention (`Bing Webmaster API key (Infisical…)`), so follow it.

### 11.3 No academic publishing pipeline exists here — the duplicate question is settled

The instance has a rich *social/content* publishing family — `Unified Publisher v5`,
`Article Publisher (Ghost + Substack)`, `Social Publisher V3`, eleven per-platform
publishers. **None of them deposits to an academic repository.** So:

- in **n8n**: no duplicate. Nothing to reuse directly, though `Unified Publisher v5`'s
  master/fan-out shape and `Drive Bundle`'s asset convention are the right patterns to copy.
- in the **repo**: two duplicates, as §1 records.

### 11.4 Still blocking

1. **The (a)/(b) fork of §10.4 is unresolved** — consolidate Python vs reimplement in n8n.
   Nothing should be created in a production instance until this is settled, because the two
   branches produce entirely different workflows.
2. **Slack target channel** — unnamed.
3. **Five of six venue tokens** absent; Zenodo asserted to be in Infisical but still
   unverified (§8).

---

## 12. Generalisation — one pipeline, any project, knowledge carried in the workflow

Principal's requirement (2026-09-24): the pipeline must serve **any project**, not just
`perturb-seq-eval`, and the **instructions, credential requirements and notes — including
the human arXiv gap — must live in the workflow itself**, not only in this document.

### 12.1 The per-project contract already exists — generalise it, do not invent one

`scripts/publish/publish.yml.template` is already the right shape: `title`, `description`,
`version`, `license`, `related_url`, `authors` (with ORCID and affiliation), `keywords`,
`artifacts` (path + description), and a per-venue block carrying each venue's own
vocabulary (`upload_type`, `defined_type`, `provider`, `subjects`, licence ids). It even
says "keep sensitive tokens out of this file". **Build on it.** Four changes make it
project-agnostic:

1. **Move it from repo root to the project.** Today it is copied to `./publish.yml`, one
   per *repo*. It becomes `<project>/publish.yml`, one per *project*, and the pipeline
   takes `PROJECT_PATH` as its input. That is the whole of "works for any project".
2. **Make `artifacts[].path` project-relative**, so a project directory is self-contained
   and portable rather than carrying repo-root paths.
3. **Add `topic:`** — required, **no default** (§4: a defaulted topic silently co-mingles
   two publications in one folder). It names the asset folder.
4. **Add the remaining venue blocks**, plus a `manual:` section for the prepare-only
   venues (§12.3).

A project is then publishable iff it has a valid `publish.yml`. Nothing else about it
needs to be known — no per-project workflow, no fork, no new nodes.

### 12.2 Where the knowledge lives — three surfaces, all inside the workflow

n8n mechanisms verified against the live instance before specifying them:
`n8n-nodes-base.stickyNote` exists, as does `n8n-nodes-base.slack`.

| surface | carries | why there |
|---|---|---|
| workflow `description` | one paragraph: what this publishes, what it **cannot** do, where the contract lives | it is what a reader sees before opening anything |
| **sticky notes** on canvas | four blocks, below | visible without reading a single node's parameters |
| per-node `notes` | that venue's API, auth mechanism, publish-vs-update semantics, and **confidence level** | the detail belongs beside the thing it describes |

The four sticky notes, and they are not decoration — each answers a question an operator
asks at 2am:

- **RUN VARIABLES** — `PROJECT_PATH`, `TOPIC`, `VERSION`, `MODE`, `VENUES`,
  `PUBLICATION_ROOT`; which are required; that `TOPIC` has no default and why.
- **CREDENTIALS REQUIRED** — §12.4. Names and scopes only.
- **⚠ THE HUMAN GAP** — §12.3. Its own note, not a footnote on another.
- **FAILURE SEMANTICS** — a run is a failure if any *enabled* venue failed;
  `PREPARED` never counts as published; partial success is still failure.

Plus one **preflight node** that emits a capability report before anything is sent: which
credentials are present, which venues are therefore reachable, which are prepare-only. A
pipeline that can tell you what it is able to do today is worth more than a document that
says what it could do in principle.

### 12.3 The human arXiv gap is a first-class element, not a caveat

arXiv's public API is read/search only — submission is a web form. bioRxiv has no deposit
API. **This is permanent and the pipeline must be built as though it is**, because the
failure mode is a run that *looks* complete.

Four mechanisms, and all four are needed — any one alone degrades:

1. **Its own sticky note**, worded so nobody has to infer it: *"arXiv and bioRxiv cannot
   be automated. No API exists. This pipeline prepares the bundle and a checklist; a human
   uploads it. A run where only these ran has published nothing."*
2. **A dedicated node** that always runs for these venues and always produces the
   checklist — never a branch that can be skipped when the rest succeeds.
3. **A status vocabulary in which `PUBLISHED` is unreachable for them.** They can only
   emit `PREPARED (manual upload required)`. Make it structurally impossible rather than
   conventionally avoided.
4. **Separate counting everywhere** — the Slack summary's `3 published · 2 prepared · 1
   failed` (§6) must never fold prepared into published, and the manifest records them as
   distinct outcomes.

The checklist lands at `<PUBLICATION_ROOT>/<topic>/receipts/arxiv.checklist.md` with the
bundle path, the validated metadata the venue will demand, and the submission URL — so
the human step is five minutes of copying, not a re-derivation.

### 12.4 Credentials: requirements in the workflow, values never

"Keep creds known in the workflow" reads two ways and only one is safe. **The
requirements are documented in the workflow; the secrets are not in it.**

- The CREDENTIALS sticky note lists, per venue: the **credential name**, the **scopes**
  needed (e.g. Zenodo's `deposit:write` + `deposit:actions`), and the **Infisical key** it
  is sourced from. Names and scopes only — never a value, never a fragment of one.
- Under (a), adapters read the environment, sourced from Infisical; n8n holds **no venue
  credential at all**, so there is one place to rotate. Under (b), n8n holds a credential
  object per venue, referenced by id — still never a literal in the workflow JSON.
- The instance already has this convention: a credential named `Bing Webmaster API key
  (Infisical…)` states its source in its own name. Follow it.
- **A missing credential must fail by name**: *"venue `dryad` skipped — credential
  `DRYAD_TOKEN` not found"*, never a silent skip and never a generic auth error. The
  preflight node reports this before the run rather than during it.

### 12.5 What this changes about the open (a)/(b) decision

It shifts one argument and leaves the others standing, so I am recording it rather than
quietly re-recommending.

**For (b):** "knowledge lives in the pipeline" is *easier* under all-HTTP-nodes, because
there is only one artifact to read.

**Unchanged for (a):** one place to rotate credentials; venue logic testable without a
live n8n; reviewable diffs; adapters that survive a change of platform.

**The synthesis I would actually build, and it resolves the tension:** keep the adapters
in Python (a), and make the workflow's sticky notes and node `notes` **generated from the
adapter source** rather than hand-written. Each adapter declares its API, auth, scopes,
publish/update semantics and confidence in one structured place; a build step renders
those into the workflow JSON. Single source of truth, displayed *in* the pipeline, and it
cannot drift — which hand-maintained documentation in either design always does. That is
the only version of this requirement that stays true six months later.

**Still blocked on the principal**, and this section does not unblock it.
