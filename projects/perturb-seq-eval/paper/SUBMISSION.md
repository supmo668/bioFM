# Preprint submission runbook — manual steps, for research approval

**Status: VENUE = arXiv `cs.LG`, BY PERSONAL ENDORSEMENT (approvals row 34, principal, 2026-11-21). POSTING BLOCKED
until one arXiv endorser agrees.** TechRxiv is closed for submissions: its own notice, quoted by the principal, says it
is "preparing a transition to a new platform" with submissions "temporarily closed", and no IEEE source gives a
reopening date. Row 34 reverses row 32's closure of arXiv and makes rows 15 and 32–33 (TechRxiv) history.
**Fallback if no endorser agrees within 14 days: Research Square**, and only after the principal reads its licence
terms (its pages did not confirm CC BY 4.0 or computer-science scope). **How to read this file now:** Parts 0–5 are
live again and are the arXiv path; **7.5 is the one sequence to follow.** Part 7 is the venue history and the
measurements behind it. **Standing constraint: post to exactly one preprint server** (7.2).
**2026-11-08 (principal):** the row-19 Morandi sentence is in `paper.tex`, with its K clause qualified to the
real-LLM evaluation after two independent primary-source reads, and the (b″) disclaimer is narrowed to match ("we have
read the sections cited below …"). The revised paper is archived as Zenodo / Figshare version **`0.6.1`** — a
manuscript revision of v0.6.0; the run and every outcome are unchanged, and `v0.6.0-a5` stays the pre-registration
amendment tag only — **before** the preprint is posted (7.5 step 4a), so that Part 4's `isIdenticalTo` is true.
**Owner: the principal. None of this is delegable to an agent** — the venue submission and its licence grant are
legal acts by a person.

This is the paper-specific **instance**. Three documents divide the work:

| Document | Owns |
|---|---|
| [`scripts/README-arxiv.md`](../../../scripts/README-arxiv.md) | the **tooling** — how the bundle and metadata are produced |
| [`docs/preprint/arxiv-submission-process.md`](../../../docs/preprint/arxiv-submission-process.md) | the **venue process** — every arXiv screen and field, reusable for any paper |
| **this file** | the **instance** — this paper's values, decisions and status |

The pipeline automates everything up to the Submit button; the process document is the button,
and this file is what to type.

**Abstract note:** the arXiv abstract is a *venue-specific override* in `arxiv.toml`, not the
`CITATION.cff` one. The CFF abstract is 2363 characters with 5 non-ASCII characters; arXiv rejects
anything over 1920 and accepts ASCII only. The override is 1914 characters, 0 non-ASCII, with every
number, hypothesis label and the "0 unevaluated" integrity claim preserved. Use the generated block.

| | |
|---|---|
| Work | *Does a Multi-Agent Group's Confidence Distribution Predict Task Difficulty?* v0.6.0 run and results; the manuscript posted is revision `0.6.1` (retitled by Amendment 5) |
| Already archived | Zenodo concept `10.5281/zenodo.19716140` · Figshare `10.6084/m9.figshare.32086920.v6` (linked `isIdenticalTo`) — v0.6.0, pre-amendment manuscript; **next: `0.6.1`** (7.5 step 4a) |
| Author of record | Mang-yin Mo · ORCID `0009-0009-5233-3142` · Carnegie Mellon University |
| Venue (approvals row 34, reversing row 32) | **arXiv**, primary `cs.LG`, cross-lists `q-bio.QM` and `cs.MA`, by personal endorsement. Fallback after 14 days: Research Square, once the principal has read its licence terms. TechRxiv: closed for submissions |
| Licence | CC BY 4.0 (matches the Zenodo deposit, so the records do not disagree on reuse terms) |

---

## The blocking dependency, stated first

**What blocks posting today is the endorsement (Part 1), not the build.** The compile check below has
run in CI (run `40985145366`, Part 0 Path A).

**Why the build check exists.** The paper uses
`\bibliography{references}` and **arXiv does not run BibTeX**, so the bundle must contain a generated
`.bbl` or every citation renders as `[?]` in the announced PDF — compiled, published, and wrong, with
no error to warn you. On arXiv the check is arXiv's own preview PDF (Part 2 step 4). On the Research Square fallback, read the 4a
`paper.pdf` before uploading it.

---

## Part 0 — Obtain the bundle (pick ONE path)

### Path A — CI builds it (recommended; the pipeline exists for this)

The pipeline commit `c0ec931` is on `origin/main` (verified 2026-11-04), so the workflow is available now.

1. Nothing to flush.
2. The `arxiv-package` workflow runs on push. Or trigger it directly:
   **Actions → `arxiv-package` → Run workflow →** `paper_dir` = `projects/perturb-seq-eval/paper`.
3. Download the **`arxiv-bundle-*`** artifact. It contains:
   - `perturb-seq-eval-arxiv-<date>.tar.gz` ← **this is what you upload to arXiv** (arXiv rejects a PDF made from TeX)
   - `perturb-seq-eval-arxiv-<date>.manifest.txt` — the file list with sha256 prefixes
   - `arxiv-metadata.txt` — the paste-ready block, identical to Part 2 below
   - `paper.pdf` — the CI-compiled PDF (latexmk). The workflow now asserts it is non-empty and uploads it;
     measured present in the artifact of run `42408464580`. An earlier run (`40985145366`) lacked it, and that
     gap is fixed. **It is a compile check, not a file you upload**: on arXiv the posted PDF is arXiv's own
     compile of the `tar.gz`; the archived PDF is the `build_deposit.py` (tectonic) build from 7.5 step 4a, which is
     also the upload on the Research Square fallback.
4. The job summary carries the same metadata block, so you can read it without downloading.

**The workflow's LaTeX step has executed.** Run `40985145366` (2026-10-30) completed "Compile LaTeX
(generates the .bbl)" and "Assert the .bbl exists and no citation is undefined" with success, and the
run on `origin/main` `600e510` (2026-11-04) succeeded as well. If a later run fails, that is a pipeline
bug to fix, not a reason to hand-assemble a bundle.

### Path B — Build locally (only if you have TeX Live installed)

```bash
cd projects/perturb-seq-eval/paper
latexmk -pdf paper.tex                      # generates paper.bbl
cd "$(git rev-parse --show-toplevel)"      # back to the repo root
uv run python scripts/arxiv_package.py build projects/perturb-seq-eval/paper --out dist/arxiv
```

`build` runs the preflight first and **refuses** to produce a bundle that would fail on arXiv.

### Verify the bundle before uploading (30 seconds, worth it)

```bash
tar tzf perturb-seq-eval-arxiv-<date>.tar.gz
```

Expect **exactly 7 files, flat at the root** (no wrapping directory — arXiv requires this):

```
paper.bbl  paper.tex  references.bib
sections/corrections.tex  sections/experimental_setup.tex
sections/generated_numbers.tex  sections/results.tex
```

If `paper.bbl` is absent or 0 bytes, **stop** — that is the failure this whole runbook exists to
prevent. The three `sections/v050_*.tex` files, the five figure PDFs and the `tables/` directory are
**correctly absent**: nothing in the paper references them (see "Known state of the paper" below).

---

## Part 1 — Account and endorsement

> **LIVE (approvals row 34, 2026-11-21).** Follow the steps below in order.

1. Log in at <https://arxiv.org/login> (or register). **Use the ORCID-linked route if available** —
   it attaches `0009-0009-5233-3142` to the submission and is what makes the record show up under
   your ORCID profile automatically.
2. Confirm the author profile carries the full name as it appears on the paper: **Mang-yin Mo**.
3. Start a new submission and select `cs.LG`. arXiv emails you an endorsement request with a link and a
   six-character code. **Keep this submission; you resume it at Part 2 once endorsed.**
4. Find endorsers: open recent `cs.LG` or `cs.MA` abstracts and use "Which authors of this paper are endorsers?"
   at the foot of each.
5. Send an endorser the code with a short request. arXiv's help page says "it is inappropriate to email large
   numbers of potential endorsers at once", and endorsers are not obliged to act. **Project advice, not arXiv's:**
   ask one or two at a time, and move to the next after a few days of silence.
6. "At least one positive endorsement is required." Endorsement "is not peer review". Then continue at Part 2.

**Why endorsement is the only arXiv route.** Since 2026-01-21 the institutional route needs both an institutional
email and a prior accepted arXiv paper. The address of record is an alumni address and there is no prior arXiv
paper, so arXiv is reachable only through a **named `cs.LG` endorser** (Path 2). Post nowhere else while the
request is out: any other preprint server would make arXiv a second server.

> **Post to EXACTLY ONE preprint server.** Two preprints of one paper is duplicate publication —
> the standing constraint on this project is that duplicate research is either fully deleted or
> superseded as a revision, never left as two live records. arXiv **and** any other preprint server (Research Square, bioRxiv, TechRxiv) is a
> violation. A preprint **and** the existing Zenodo/Figshare archives is not, because Zenodo and Figshare are
> archives, not preprint servers, and neither counts as the one server: an archive and a preprint of the same
> work are one work in two places, which is exactly what the cross-links in Part 4 assert.

---

## Part 2 — The submission form, field by field

> **LIVE (approvals row 34).** These are arXiv's form fields; use the generated block below.

Start at **arxiv.org → START NEW SUBMISSION**. Values below are generated from
`projects/perturb-seq-eval/CITATION.cff` via the pipeline, so the paper, the repository and this form
cannot drift. Regenerate at any time with:

```bash
uv run --with pyyaml python scripts/arxiv_package.py metadata projects/perturb-seq-eval/paper
```

| Form step | What to do |
|---|---|
| **1. Licence** | Select **CC BY 4.0**. This is an irrevocable grant and a legal act — it is why this step is yours. |
| **2. Archive / category** | Primary **`cs.LG`**; add cross-lists **`q-bio.QM`** and **`cs.MA`**. |
| **3. Upload** | Upload the **`.tar.gz`**. Do *not* upload `paper.pdf` — arXiv compiles from source, and a PDF-only submission discards the LaTeX. |
| **4. Process** | Let arXiv compile. **Open the generated PDF and check the bibliography renders** — if you see `[?]` anywhere, the `.bbl` is missing and you must stop and rebuild. |
| **5. Metadata** | Paste from the block below. |
| **6. Preview → Submit** | Submit. Moderation follows; announcement is typically the next scheduled mailing. |

### Paste-ready metadata

```text
# metadata sourced from CITATION.cff — single source of truth

=== PASTE INTO THE ARXIV SUBMISSION FORM ===

Title:      Does a Multi-Agent Group's Confidence Distribution Predict Task Difficulty? A Pre-registered, Provenance-Complete Test on Perturb-seq Response Prediction in Which Entropy Fails Its Criterion and the Confidence Drop Passes
Authors:    Mang-yin Mo
Primary:    cs.LG
Cross-list: q-bio.QM, cs.MA
License:    CC BY 4.0

Comments:
  Pre-registered study; pre-registration and provenance manifests included. Archived with full data and code at doi:10.5281/zenodo.19716140 (concept DOI). The same work is deposited on Figshare as doi:10.6084/m9.figshare.32086920 (all versions).

Abstract:
  That a single agent's own vote distribution can gate its compute is reported
  (CATTS, arXiv:2602.12276); we ask the multi-agent question: does the
  distribution of stated confidences and critiques across a group of
  role-specialised agents predict task difficulty, so the group's compute --
  spent uniformly across tasks as operated here -- can be allocated adaptively?
  In a five-agent CellForge-style Perturb-seq orchestrator run via MassGen, we
  define four trace metrics -- Agent Confidence Entropy (ACE), Critique Severity
  Dispersion (CSD), a convergence signal ($\Delta$C), and a Winner Flip Rate
  (WFR) -- and their composite Task Difficulty Index (TDI). Five pre-registered
  criteria: attainable error on Adamson 2016 (CRISPR interference) and Norman
  2019 (CRISPR activation), the Architect's backbone-choice entropy, each TDI
  component's rank correlation with error, and cross-dataset transfer of a
  calibrated TDI. Design: 41 held-out K562 tasks (21 Adamson, 15 Norman
  singletons, 5 Norman doublets) drawn deterministically; 27 trainer-sweep
  records and three fixed-length agentic runs per task. LLM condition: a pinned
  Anthropic Claude roster (Haiku 4.5 for the four proposer roles, Sonnet 5.5 for
  the Validator), served model recorded and asserted per call; any rule-based
  fallback invalidates the run. Outcomes: 4 of 5 pass; H5 fails (0 unevaluated)
  -- the trainer sweep attains the pre-registered error on both screens (H1,
  H2), the Architect exercises its backbone choice (H3), and the confidence-drop
  component and the composite rank tasks by held-out error within both screens
  (H4); the Adamson-calibrated composite does not transfer to Norman at the
  pre-registered level (H5, $\rho$ = 0.286 against > 0.4). Confidence-entropy
  point estimates run against the pre-registered direction in both screens
  (exploratory). The v0.5.0 release's values are superseded in full; the defects
  are listed in the appendix.

=== END ===

Reminder: arXiv submission is a WEB FORM. There is no deposit API for individual
authors, the license grant is a legal act by a person, and a first submission to a
category may require endorsement. This block exists so the manual step is
copy-paste and reproducible from the repository, not so it can be skipped.
```

> **Regenerate, never patch.** This block is the output of the command in the lead-in above. After ANY change to `arxiv.toml` or `CITATION.cff`, re-run it and replace the whole block; a hand-edited line is how it drifted once already (the abstract here was the non-ASCII CFF one, which arXiv rejects, until 2026-11-02).

**CORRECTED 2026-10-30 — the `DOI` field.** I previously said to leave it empty, on the grounds
that it means a *published journal version*. **That was wrong.** arXiv's own wording is broader:
*"Use only for a DOI that resolves to another version of the article, such as the journal version."*
"such as" is an example, not a restriction. The Zenodo deposit **is** another version of this
article, so its DOI belongs there.

- **`DOI`** → `10.5281/zenodo.19716140`. Do **not** add the arXiv-assigned DOI; that is automatic.
- **`Journal-ref`** → leave **EMPTY**. That field is only for a work that has already appeared in a
  journal or proceedings, and a repository is neither. My reasoning on this half was right.
- Keeping the DOI in **Comments** as well is harmless and makes it visible in the abstract listing.

---

## Part 3 — Immediately after announcement

Record the assigned identifier. arXiv mints both:

- arXiv ID — `arXiv:NNNN.NNNNN`
- arXiv DOI — `10.48550/arXiv.NNNN.NNNNN` (written `<venue DOI>` below)

**Check the announced abstract page for:** title and author rendering, the Comments line carrying
`doi:10.5281/zenodo.19716140`, the licence showing CC BY 4.0, and the cross-lists to `q-bio.QM` and `cs.MA`.

Then tell me the venue DOI and I will update `CITATION.cff` (both the root and the project file),
the two READMEs, and `docs/hacp/perturb-seq-eval/publish-complete.md` so the repository states the
preprint alongside the two archive DOIs. That part *is* mine.

---

## Part 4 — Reciprocal linking on Zenodo (do not skip; this is what prevents "two papers")

> **Target record (principal, 2026-11-08):** link the preprint to the **`0.6.1`** Zenodo version
> deposited at 7.5 step 4a, not to v0.6.0 (`10.5281/zenodo.23422745`). v0.6.0 carries the pre-amendment
> title and manuscript, so `isIdenticalTo` against it would assert something false.

At deposit the `0.6.1` Zenodo record carries `isNewVersionOf` `10.5281/zenodo.23422745` and
`10.6084/m9.figshare.32086920.v6`, and `isSupplementedBy` the repository. The post-publish step
(`publish.yml` deposit-time sequence, step 5) adds `isIdenticalTo` the Figshare v7 DOI, as was done for v6 on
2026-10-25. Add the venue record the same way:

1. Zenodo → the `0.6.1` record → **Edit** (metadata-only edit; it does **not** mint a new version).
2. Under **Related works**, add:
   - **`is identical to`** → `<venue DOI>`
3. Publish the metadata edit.

**Relation choice is a judgment call, so here is the reasoning rather than just the answer.**
`isIdenticalTo` is recommended because it is what the Figshare link already uses, and the arXiv
source and the Zenodo deposit are the same manuscript — one work in three places, consistently
asserted. The alternative is `hasPreprint` → arXiv, which additionally asserts that Zenodo is the
*archival* record and arXiv the *preprint*. That is defensible and arguably more precise, but it
makes a venue-hierarchy claim the Zenodo deposit does not otherwise make. **Pick one and use it
consistently; do not add both.**

---

## Part 5 — Google Scholar

> **Checklist for the arXiv record, in order** (the runbook's own statement that arXiv is Scholar-indexed was not
> re-measured on 2026-11-21: arXiv's help page for it returned 404):
> 1. **Before posting, nothing to do in Scholar.** There is no crawled record yet (7.0); a manual edit now
>    only adds a second profile-only entry.
> 2. **After the arXiv DOI is minted:** ORCID → add the arXiv DOI and the `0.6.1` Zenodo DOI by
>    identifier (7.3 #1), so the author record carries both. Keep the concept-DOI entry as the preferred source
>    in the grouped Work (`docs/hacp/perturb-seq-eval/publish-complete.md`).
> 3. **When the crawled arXiv entry appears in Scholar (days to weeks):** merge it with the manual entry,
>    crawled entry primary (step 1 below). Check its title is the Amendment-5 title and its author is
>    "Mang-yin Mo". If it never appears, check the arXiv abstract page exposes `citation_title`,
>    `citation_author`, `citation_publication_date` and `citation_pdf_url` (Scholar inclusion guidelines).
> 4. **Semantic Scholar / OpenAlex:** claim the author pages and confirm the Work (7.3 #2–#3); they follow
>    the DOI and need no submission.

Scholar's crawler reads Highwire `citation_*` / Dublin Core / Eprints meta tags and needs, at
minimum, title + authors + date. This runbook's earlier statement that arXiv emits these correctly was **not re-measured on 2026-11-21**;
if the arXiv entry has not appeared in Scholar after several weeks, check the abstract page's meta tags.

**Read Part 7.0 first:** Zenodo is not indexed by Google Scholar, so there is currently nothing crawled to merge onto.

Two cleanups once the arXiv record is indexed (typically days to weeks):

1. **Merge the duplicate entries.** The existing Scholar entry for this work was added **manually**,
   which means it is **profile-only — not indexed, and it accrues no citations.** Scholar → your
   profile → select both the manual entry and the newly-crawled arXiv entry → **Merge**. Keep the
   crawled one as the primary.
2. **The manual entry records *Journal = Zenodo*, which is wrong** — Zenodo is a repository. Merging
   onto the crawled arXiv record fixes this; if you instead keep the manual entry, correct the field.

---

## Part 6 — OSF cleanup (pre-existing, unrelated to arXiv, but it is live and wrong)

Two stale OSF objects exist:

- Draft **`dhu4z_v1`** — delete it, or
- **`wmeuy`** — point it at the Zenodo **concept** DOI `10.5281/zenodo.19716140`

A stale draft pointing at a superseded version is the duplicate-research failure mode in miniature.
Either resolve it or delete it; leaving it is the one option the project's own standing constraint
rules out.

---

## Part 7 — Venue history and visibility measurements

This part is the venue history: why arXiv needs an endorser, why TechRxiv was ruled, and what was measured when it closed. It also changes what Part 5 can deliver.

### 7.0 The fact that reframes the question: Zenodo is not in Google Scholar

Zenodo's own support page states it plainly: **"Google Scholar are therefore not indexing
Zenodo."** The reasons given there: Google Scholar indexes text articles only, so other resource
types fall outside its scope; Scholar infers resource type from URL patterns, and Zenodo permits a
record's resource type to change after publishing, which Zenodo says would conflict with stable
links and repository best practice. Zenodo has met with Google over the years and **"so far there is
no resolution."** Google Search and Google **Dataset** Search *do* index Zenodo, via the schema.org
metadata embedded in record landing pages — neither of which is Scholar.

So the two deposits this work already has — Zenodo `10.5281/zenodo.19716140` and Figshare
`10.6084/m9.figshare.32086920.v6` — buy **zero Google Scholar presence**, and the existing Scholar
entry is the manual one described in Part 5, which is **profile-only: not indexed, accruing no
citations.**

**Therefore: this work currently has no indexed Scholar record at all, and no amount of follow-up
produces one without a Scholar-indexed venue.** Scholar visibility is not a post-submission chore.
It follows from the venue, now arXiv by endorsement (approvals row 34), and it is blocked on the same thing: one
endorser saying yes.

### 7.1 Why Part 1 has one route — the endorsement gate tightened on 2026-01-21

arXiv's own blog post of 2026-01-21 states that arXiv **"will no longer accept institutional email
addresses"** as **"the sole qualifier of endorsement for new authors."** Two paths remain:

- **Path 1 — both conditions:** *"an institutional email address from an academic/research
  institution"* **and** *"previous authorship on an existing paper which has been accepted to the
  arXiv"* in the relevant endorsement domain.
- **Path 2 — one condition only:** seek *"personal endorsement directly from an established arXiv
  author in the same endorsement domain."*

Effective *"As of January 21, 2026"*, covering *"all categories"* for new submitters. Endorsement
domains are the high-level subject areas, *"with the notable exception of physics"*, where the
individual subject classes are the domains. Authors already endorsed in a category *"will still be
endorsed in that category."*

arXiv's endorsement help page adds the endorser-side constraints: *"arXiv requires that users be
endorsed before submitting their first paper to arXiv or a new category"*; *"At least one positive
endorsement is required per endorsement category"*; endorsers *"must have authored a certain number
of papers within the endorsement domain"*, counted only from papers *"submitted between three months
and five years ago"*; and a prospective endorser *"must also have an active positive endorsement to
that area"* themselves.

**Measured against this paper:** the address of record is the **alumni** address in `CITATION.cff`,
and there is no prior accepted arXiv paper. Path 1 fails on **both** conditions, not one. So arXiv
is unavailable *except* by Path 2 — a named human in `cs.LG` who agrees to endorse. That is a
decision about people, not a step in a runbook, and nothing in this repository can advance it.

An earlier framing in this file (that a first `cs.LG` submission *may* land in the endorsement queue) was
written against the pre-2026 rule and was too soft. Under the current policy the queue is the
default, not the risk case.

### 7.2 Venues compared — and the constraint that eliminates most of them

> **Post to EXACTLY ONE preprint server.** This is the project's standing constraint, unchanged:
> duplicate research is either fully deleted or superseded as a revision, never left as two live
> records. An archive (Zenodo, Figshare) plus one preprint is *one work in several places*, which is
> what the Part 4 cross-links assert. Two preprint servers is duplicate publication.

**Snapshot as written 2026-11-03 to 11-05, before row 34. Superseded by the measured table below; kept as history.**

| Venue | Endorsement | Topical fit for *this* claim | Scholar-indexed | The fact that decides it |
|---|---|---|---|---|
| **TechRxiv** (IEEE) — **closed for submissions since this was written** | **none** — moderated only | **good** — electrical engineering, computer science and related technology; the contribution is a compute-allocation method claim | **yes** (listed) | moderation is a scope/plagiarism/English screen, not technical merit; posting in **~4 business days**; **CC BY 4.0 available**, so it matches the Zenodo licence grant; **DOI minted**, and a revised version keeps the DOI with a version indicator |
| **bioRxiv** | **none** | **weak** — the claim is about allocating test-time compute, not about biology | yes | *"Manuscripts already present on other preprint servers will not be posted."* A Zenodo/Figshare **archive** is not a preprint server, so this should not disqualify — but it is the sentence to read before assuming. Also: *"bioRxiv welcomes computational papers"*, yet *"Simple automated/computational analyses of public data, molecular modeling, sequence alignments"* are *"generally not sufficient"* — a real scope risk for a method paper over public Perturb-seq screens |
| **arXiv** | **required** (7.1); now the path, by personal endorser (row 34) | best | yes | needs a named `cs.LG` endorser |
| preprints.org (MDPI), SSRN | **unknown** | — | — | **Not read (HTTP 403 on 2026-11-21). No claim is made.** Research Square and OSF Preprints: see the measured table below |

**History: TechRxiv was the recommendation, then the ruled venue (rows 15, 32–33), and is now closed for
submissions.** Every TechRxiv fact in the row above came from the COAR directory, a secondary source;
`techrxiv.org` returned HTTP 403 to agents. On 2026-11-21 the principal quoted its own notice: "We are currently
preparing a transition to a new platform. Submissions are temporarily closed during this process."

**Agent-measured on 2026-11-21 at each server's own pages.** Row 34 records the principal's decision; these
measurements are the agent's, read through a fetch tool that can paraphrase, so check a quote at its source before
relying on it. Sources are listed at the end of Part 7.

| Server | Open | What decides it |
|---|---|---|
| **arXiv `cs.LG`** | yes | best fit; personal endorser required; takes LaTeX source, "We do not accept … PDF created from TeX/LaTeX source" |
| **Research Square** | yes | free, PDF, "posted within 24-48 hrs.", "indexed through Crossref, Europe PMC, Google Scholar"; CC BY 4.0 and CS scope **not found** on its pages; "cannot be removed" |
| **bioRxiv** | yes | may screen the paper out as not biology; bars papers "already present on other preprint servers" without saying whether Zenodo or Figshare count |
| **Qeios** | yes | CC BY 4.0 and "Computer Science" confirmed; it is a journal with public peer review; each revision gets a new DOI |
| **engrXiv** | no | "not accepting submissions at this time"; excludes AI-only work |
| **OSF Preprints** (general) | no | suspended "indefinitely" |
| **Preprints.org, SSRN** | unknown | HTTP 403 to the agent; **not read, no claim made** |

**arXiv by endorsement is the path (row 34). Fallback after 14 days with no endorser: Research Square**, once the
principal has read its licence terms. Never two servers.

### 7.3 Channels that are not venues — unlimited, and carry no duplication risk

Indexes and author profiles are not publication venues. A record in them is not a second preprint,
so none of these competes with the one-venue rule.

1. **ORCID — do this now; it waits on nothing.** Works → **Add** → *Add DOI* → enter
   `10.5281/zenodo.19716140` → the form pre-populates from DataCite → check the fields, fill any
   gaps, set visibility to **Public**, save. (DataCite auto-update covers only the first ten authors
   of a work; single-author here, so auto-update would apply anyway — the manual add is simply
   immediate.)
2. **OpenAlex.** OpenAlex harvests *"Crossref, DataCite, PubMed, and others, plus thousands of
   repositories"*, and the Zenodo DOI is DataCite-registered, so the deposit is **probably already a
   Work**. Claim the author profile, then add anything missing *"by searching titles, pasting DOIs or
   OpenAlex IDs, or uploading your CV."* If a work is missing **entirely**, file a ticket at
   `openalex.org/contact` **with the DOI**. Metadata errors are fixed **upstream** — *"check Crossref
   first — fixes there flow into OpenAlex automatically"* — never patched in OpenAlex.
3. **Semantic Scholar — there is nothing to do before the venue step.** Its FAQ: content is sourced
   *"via web indexing and from partnerships with scientific journals, indexes, and content
   providers"*; an author page is generated *"Once Semantic Scholar discovers a publicly accessible
   publication on the internet"*; and *"If your paper is discoverable on Semantic Scholar, you can
   add it to your claimed author page."* **No submission form for an undiscovered paper is
   documented.** So: claim the author page now if you like, and add the paper *after* the preprint is
   live and discoverable.
4. **Google Scholar profile** — the merge in Part 5, once the crawled venue record appears. Unchanged
   by this part, but note it is now contingent on 7.2: with no Scholar-indexed venue there is nothing
   to merge *onto*.
5. **Do not upload the PDF to ResearchGate or Academia.edu to buy indexing.** CC BY permits it, but
   it creates another full-text record that Scholar may index as a separate paper — the exact
   "two papers" failure Part 4 exists to prevent. Link to the DOI from a profile; do not host a copy.

### 7.4 Self-hosting: a real fallback, and strictly worse

Google Scholar's inclusion guidelines state the requirements for a site to be crawled. Files must be
*"either in the HTML or in the PDF format"*, PDFs *"must have searchable text"*, and *"Each file must
not exceed 5MB in size."* *"Each paper must have its own unique URL in order for it to be included"*;
pages must be *"reachable from the homepage by following at most ten simple HTML links"*; the site
must *"provide a way to list them by the date of publication or the date of record entry"*; and
robots.txt *"must not block Google's search robots from accessing your articles or your browse
URLs."* Scholar reads Highwire `citation_*` tags (Dublin Core *"as a last resort"*) and needs **at
least three fields** — title, the full name of at least the first author, and the publication year:
*"Pages that don't provide any one of these three fields will be processed as if they had no meta
tags at all."* For PDFs, *"specify the locations of all full text versions using citation_pdf_url or
DC.identifier tags."* Preprints are explicitly in scope. For an individual author Scholar says
*"it works best to simply upload your paper to your website"* and that it *"should normally find your
paper and include it in Google Scholar within several weeks"* — while also stating that
*"we're unable to make exceptions to any of the stated guidelines."*

A GitHub Pages site can satisfy every line of that. **It is still the wrong answer unless every
endorsement-free venue rejects the paper on scope**: no DOI, no moderation record, no venue, and a
self-hosted full text alongside a preprint is another candidate "second paper". Treat it as the
fallback it is, not as a way around the venue decision.

### 7.5 Order of operations

| # | Step | Depends on |
|---|---|---|
| 1 | ORCID: add the Zenodo DOI (7.3 #1) | nothing — do it today |
| 2 | OpenAlex: claim the author profile; confirm the Work exists (7.3 #2) | nothing |
| 3 | ~~Principal decides the venue~~ **Decided: arXiv `cs.LG` by personal endorsement** (approvals row 34; fallback Research Square after 14 days) | 7.1, 7.2 |
| 4 | **Get one arXiv endorsement (Part 1). BLOCKS step 5.** Start the `cs.LG` submission to receive the code, then ask endorsers one or two at a time (Part 1). **The 14-day fallback clock starts when the first request is sent** | 3 |
| 4a | **Archive the revised paper as version `0.6.1`** (principal, 2026-11-08): `build_deposit.py`, then `submit_to_venues.py zenodo --dry-run` and `figshare --dry-run` under the principal's `infisical run` invocation (approvals rows 2–3), review the drafts, then a **separate go** to publish, then `publish.yml` deposit-time step 5 (CITATION version and DOIs, CHANGELOG, Zenodo `isIdenticalTo` Figshare v7). The v0.6.0 records carry the pre-amendment paper and title, so step 6's `isIdenticalTo` would be false against them | nothing (can run in parallel with 4) |
| 5 | Parts 0–2: upload the CI `tar.gz` (LaTeX source) to arXiv. **Build it from the commit the 4a PDF was built from** — the SHA printed in `build/deposit/paper_build.log`. Ask the CTO to tag that commit `v0.6.1`, run the `arxiv-package` workflow on the tag, and confirm the run's head SHA matches, so the arXiv record and the `0.6.1` archive are the same manuscript. **Before pasting the metadata block, re-run `arxiv_package.py metadata`** so the Comments line is current. Open arXiv's preview PDF: any `[?]` means stop. Then Part 3: record the arXiv ID and DOI | 4, 4a |
| 5′ | **Fallback, only if no endorser has agreed 14 days after the first request.** (1) The principal reads Research Square's licence terms; stop if CC BY 4.0 is not offered. (2) Delete the unsubmitted arXiv submission and tell any endorser you asked that the request is withdrawn — a late endorsement must not lead to a second server. (3) Upload the 4a `paper.pdf` to Research Square. A posted preprint there "cannot be removed". (4) Parts 3–5 then apply with the Research Square DOI as `<venue DOI>`; the arXiv-only checks (Comments line, cross-lists) do not | 4, 4a |
| 6 | Part 4 reciprocal link with the venue DOI, `isIdenticalTo`, once, **on the `0.6.1` Zenodo record** (not v0.6.0 `10.5281/zenodo.23422745`) | 5 |
| 7 | Part 5 Scholar merge, once the crawled record appears (days to weeks) | 5 |
| 8 | Semantic Scholar: add the paper to the claimed author page | 5 |
| 9 | Part 6 OSF cleanup | nothing — independent, and still live and wrong |

**One format caveat on step 5.** arXiv compiles from LaTeX source and does not run BibTeX, so a missing `.bbl`
publishes every citation as `[?]`. The bundle carries the `.bbl`; arXiv's preview PDF is where you confirm it. The
archived `paper.pdf` (tectonic) and arXiv's PDF (its own TeX Live) are two renderings of one source, which is what
`isIdenticalTo` asserts here. On the Research Square fallback the upload is the 4a `paper.pdf` itself.

### What Part 7 does not establish

- **That any venue will accept the paper.** Moderation is a human decision made after submission.
- **TechRxiv's rules first-hand.** `techrxiv.org/faqs` returned 403; the 7.2 row is secondary-source, and TechRxiv is closed for submissions.
- **Preprints.org and SSRN.** Both returned HTTP 403 on 2026-11-21. Not read; no claim is made.
- **That an endorser will agree, or when.** Endorsers are not obliged to act.
- **Research Square's licence and scope.** Its pages did not confirm CC BY 4.0 or that computer science is in scope; the principal reads its terms before the fallback is used.
- **That Scholar will index a self-hosted copy.** Their guidelines state requirements, not outcomes.
- **Anything about the paper's scientific content.** This remains a publication-logistics document.

### Sources read for Part 7

- arXiv, *Attention Authors: Updated Endorsement Policy*, 2026-01-21 — <https://blog.arxiv.org/2026/01/21/attention-authors-updated-endorsement-policy/>
- arXiv endorsement help — <https://info.arxiv.org/help/endorsement.html>
- Zenodo support, *Is Zenodo indexed by Google Scholar?* — <https://support.zenodo.org/help/en-gb/18-general/61-is-zenodo-indexed-by-google-scholar>
- Google Scholar inclusion guidelines — <https://scholar.google.com/intl/en/scholar/inclusion.html>
- bioRxiv FAQ — <https://www.biorxiv.org/about/FAQ>
- Semantic Scholar FAQ — <https://www.semanticscholar.org/faq>
- OpenAlex help, *Fixing authors* / *Fixing data errors* / *Getting indexed* — <https://help.openalex.org/>
- Read 2026-11-21 (agent): arXiv endorsement help <https://info.arxiv.org/help/endorsement.html>; Research Square support articles <https://support.researchsquare.com/>; bioRxiv FAQ <https://www.biorxiv.org/about/FAQ>; Qeios <https://www.qeios.com/publishing-policy>, <https://www.qeios.com/plans>; engrXiv <https://engrxiv.org/about>; OSF Preprints suspension <https://help.osf.io/article/687-osf-preprints-suspension>. Not read (HTTP 403): preprints.org, ssrn.com, techrxiv.org
- COAR Directory of Open Access Preprint Repositories, TechRxiv entry — <https://doapr.coar-repositories.org/repositories/techrxiv/> (secondary source; `techrxiv.org/faqs` returned HTTP 403)
- ORCID support, *Add works using an identifier* — <https://support.orcid.org/hc/en-us/articles/360022298153-Add-works-using-an-identifier>

---

## Approval required before posting (7.5 step 5)

Three items: two closed, and one that blocks posting (item 2).

1. **Flush `c0ec931` — CLOSED.** The commit is on `origin/main` and the workflow's LaTeX step has run
   successfully (run `40985145366`; see Part 0, Path A). Path A is available.
2. **Venue — arXiv `cs.LG` by personal endorsement (approvals row 34, principal, 2026-11-21); posting BLOCKED until
   one endorser agrees.** History: row 12 ruled arXiv; row 15 superseded it to TechRxiv; rows 32–33 closed arXiv;
   TechRxiv then closed for submissions and row 34 reversed row 32. Fallback after 14 days: Research Square, after
   the principal's read of its licence terms.
3. **Title — RULED T1 (CTO #896, 2026-11-04) — CLOSED.** The question-form T1 title and row 11's narrowed
   contribution are applied in `paper.tex` and recorded as Amendment 5 of `PREREGISTRATION.md`. They landed on
   `origin/main` in PR #42 (tag `v0.6.0-a5`). The Morandi-sentence change landed in PR #46; the compile check runs in
   CI on every change to the paper.

A fourth decision is adjacent and does not block submission, but affects what gets submitted:

4. **The five figure PDFs** — wire them into the paper, retire them, or leave them unreferenced. If
   you wire them in, the bundle changes and Part 0 must be re-run.

---

## Known state of the paper, so nothing here is a surprise at submission time

- **The paper references no figures at all.** `graphicx` is loaded but unused; all six tables are
  inline `tabular` environments; `\includegraphics` count is **zero**. The five figure PDFs and the
  entire `tables/` directory are v0.5-era orphans, as are the three `sections/v050_*.tex` files. The
  7-file bundle is therefore *complete* for what this paper is.
- **v0.5.0 values are superseded in full** and the defects behind each are listed in the paper's
  appendix (`sections/corrections.tex`, which **is** in the bundle).
- The preflight passes 10 checks and states what it does **not** check: whether the document
  compiles (CI does that), and anything about arXiv moderation or endorsement outcomes.

## What this runbook does not establish

- **That the submission will be accepted.** Moderation (and, on arXiv, endorsement) are human decisions
  made by the venue after you submit. Nothing here predicts them.
- **That the posted PDF renders as intended on the venue.** CI compiling the source and the 4a build are strong
  evidence, not proof. On arXiv, read arXiv's preview PDF before submitting (Part 2 step 4); on the Research Square fallback, read the 4a `paper.pdf` before uploading.
- **Any claim about the paper's scientific content.** This is a publication-logistics document.
