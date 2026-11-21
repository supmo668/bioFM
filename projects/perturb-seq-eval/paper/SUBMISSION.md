# Preprint submission runbook — manual steps, for research approval

**Status: VENUE FINAL — TechRxiv, and only TechRxiv. Row 15 is the principal's ruling for TechRxiv; row 32
(2026-11-21) CLOSES the arXiv path for this paper, as a decision delegated by the principal to the CTO seat, not a
ruling the principal made in those words. POSTING BLOCKED** until the principal's first-hand read of TechRxiv's own terms is
recorded: the principal reported the read on 2026-11-09 (perturb-seq-eval session 74ae8896, "1. read"), and the answers to its four checks are not yet on record: is CC BY 4.0 offered, is an ML
method paper in scope, is a paper already on Zenodo/Figshare accepted, and is a PDF the accepted format. Every TechRxiv fact in Part 7 comes from a
secondary source (the COAR directory), and `techrxiv.org` returned HTTP 403 to the agents on 2026-11-05 (reported,
not retried). **How to read this file now:** **7.5 is the one sequence to follow.** For TechRxiv, Part 0 is only the compile and
bibliography check; its `tar.gz` is arXiv's upload format, and what you upload is the `paper.pdf` from 7.5 step 4a. **Parts 1 and 2 are the
arXiv path and are kept as a record only — do not follow them.** Parts 3–5 give the steps after posting; where they
say arXiv, the venue is TechRxiv. Part 7 is why. **Standing constraint: post to exactly one preprint server** (7.2).
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

The process document covers arXiv's form only. **For this paper's venue, TechRxiv, there is no process document:**
the form is read off the site at 7.5 step 5, and this file is what to type.

**Abstract note:** the arXiv abstract is a *venue-specific override* in `arxiv.toml`, not the
`CITATION.cff` one. The CFF abstract is 2363 characters with 5 non-ASCII characters; arXiv rejects
anything over 1920 and accepts ASCII only. The override is 1914 characters, 0 non-ASCII, with every
number, hypothesis label and the "0 unevaluated" integrity claim preserved. This limit is arXiv's. On TechRxiv use
the `CITATION.cff` abstract unless its form states a limit; if it does, the override is the pre-checked shorter text.

| | |
|---|---|
| Work | *Does a Multi-Agent Group's Confidence Distribution Predict Task Difficulty?* v0.6.0 (retitled by Amendment 5) |
| Already archived | Zenodo concept `10.5281/zenodo.19716140` · Figshare `10.6084/m9.figshare.32086920.v6` (linked `isIdenticalTo`) — v0.6.0, pre-amendment manuscript; **next: `0.6.1`** (7.5 step 4a) |
| Author of record | Mang-yin Mo · ORCID `0009-0009-5233-3142` · Carnegie Mellon University |
| Venue (approvals rows 15 and 32) | **TechRxiv** (IEEE), the one preprint server; posting blocked until the answers to the four checks of the principal's terms read are recorded. **arXiv: closed for this paper (row 32)** |
| Licence | CC BY 4.0 (matches the Zenodo deposit, so the records do not disagree on reuse terms) |

---

## The blocking dependency, stated first

**What blocks posting today is the unrecorded terms read (7.5 step 4), not the build.** The compile check below has
run in CI (run `40985145366`, Part 0 Path A).

**Why the build check exists.** The paper uses
`\bibliography{references}` and **arXiv does not run BibTeX**, so the bundle must contain a generated
`.bbl` or every citation renders as `[?]` in the announced PDF — compiled, published, and wrong, with
no error to warn you. The same check matters for a PDF upload: read the built `paper.pdf` and confirm no `[?]`
before 7.5 step 5.

---

## Part 0 — Obtain the bundle (pick ONE path)

### Path A — CI builds it (recommended; the pipeline exists for this)

The pipeline commit `c0ec931` is on `origin/main` (verified 2026-11-04), so the workflow is available now.

1. Nothing to flush.
2. The `arxiv-package` workflow runs on push. Or trigger it directly:
   **Actions → `arxiv-package` → Run workflow →** `paper_dir` = `projects/perturb-seq-eval/paper`.
3. Download the **`arxiv-bundle-*`** artifact. It contains:
   - `perturb-seq-eval-arxiv-<date>.tar.gz` ← arXiv's upload format (**not uploaded to TechRxiv**; see 7.5 step 5)
   - `perturb-seq-eval-arxiv-<date>.manifest.txt` — the file list with sha256 prefixes
   - `arxiv-metadata.txt` — the paste-ready block, identical to Part 2 below
   - `paper.pdf` — the CI-compiled PDF (latexmk). The workflow now asserts it is non-empty and uploads it;
     measured present in the artifact of run `42408464580`. An earlier run (`40985145366`) lacked it, and that
     gap is fixed. **It is a compile check, not the file to post**: the posted PDF is the `build_deposit.py`
     (tectonic) build from 7.5 step 4a.
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

> **CLOSED for this paper (approvals row 32, 2026-11-21). Record only — do not follow.** arXiv needs a named `cs.LG`
> endorser (7.1); the venue is TechRxiv.

1. Log in at <https://arxiv.org/login> (or register). **Use the ORCID-linked route if available** —
   it attaches `0009-0009-5233-3142` to the submission and is what makes the record show up under
   your ORCID profile automatically.
2. Confirm the author profile carries the full name as it appears on the paper: **Mang-yin Mo**.

**Endorsement risk, stated plainly.** arXiv's own submission documentation states that new users, or
users posting to a new category, *"may be required to find endorsements"*, and that *"We only accept
submissions from registered authors"*. The address of record is the **alumni** address recorded in
[`CITATION.cff`](../CITATION.cff) — weaker evidence of current affiliation than a live
institutional one.

**Row 15 left one arXiv route; row 32 closed it.** What row 15 said, kept as the record: since 2026-01-21 an institutional address alone no
longer qualifies, the address of record is an alumni address, and there is no prior accepted arXiv paper,
so arXiv was reachable only through a **named `cs.LG` endorser** (Path 2), and that endorsement had to come
*before* any preprint was posted. Once the paper is on TechRxiv, arXiv is a second preprint server and is
closed (see the box below).

> **Post to EXACTLY ONE preprint server.** Two preprints of one paper is duplicate publication —
> the standing constraint on this project is that duplicate research is either fully deleted or
> superseded as a revision, never left as two live records. TechRxiv **and** arXiv (or bioRxiv) is a
> violation. A preprint **and** the existing Zenodo/Figshare archives is not, because Zenodo and Figshare are
> archives, not preprint servers, and neither counts as the one server: an archive and a preprint of the same
> work are one work in two places, which is exactly what the cross-links in Part 4 assert.

---

## Part 2 — The submission form, field by field

> **CLOSED for this paper (approvals row 32). Record only — do not follow.** These are arXiv's form fields. The live
> source of the title, authors, licence and abstract for TechRxiv is `CITATION.cff`; the 1914-character ASCII abstract is an arXiv limit,
> and TechRxiv's own limit is to be read off its form.

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
  Pre-registered study; pre-registration and provenance manifests included. Archived with full data and code at doi:10.5281/zenodo.19716140 (concept DOI). The same release is deposited on Figshare as doi:10.6084/m9.figshare.32086920.v6.

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

> **Parts 3–5 were first written for arXiv; the steps below are stated for the venue, TechRxiv.** Where a later
> paragraph still says arXiv, read the venue. TechRxiv mints its own DOI (Part 7.2, a secondary-source fact until
> the terms read is recorded).

Record the assigned identifier: the venue DOI, written `<venue DOI>` below.

**Check the posted record for:** title and author rendering, the licence showing CC BY 4.0, and a visible link or
reference to the Zenodo concept DOI `10.5281/zenodo.19716140` wherever the form allows one.

Then tell me the venue DOI and I will update `CITATION.cff` (both the root and the project file),
the two READMEs, and `docs/hacp/perturb-seq-eval/publish-complete.md` so the repository states the
preprint alongside the two archive DOIs. That part *is* mine.

---

## Part 4 — Reciprocal linking on Zenodo (do not skip; this is what prevents "two papers")

> **Target record (principal, 2026-11-08):** link the preprint to the **`0.6.1`** Zenodo version
> deposited at 7.5 step 4a, not to v0.6.0 (`10.5281/zenodo.23422745`). v0.6.0 carries the pre-amendment
> title and manuscript, so `isIdenticalTo` against it would assert something false. Read "arXiv" below as the venue (TechRxiv).

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

> **On TechRxiv (2026-11-08).** The Scholar path is the venue's record, as below with "arXiv" read as
> TechRxiv. That TechRxiv is Scholar-indexed comes from the COAR directory (secondary; 7.2) — confirm it in
> the principal's step-4 read. Checklist, in order:
> 1. **Before posting, nothing to do in Scholar.** There is no crawled record yet (7.0); a manual edit now
>    only adds a second profile-only entry.
> 2. **After the TechRxiv DOI is minted:** ORCID → add the TechRxiv DOI and the `0.6.1` Zenodo DOI by
>    identifier (7.3 #1), so the author record carries both. Keep the concept-DOI entry as the preferred source
>    in the grouped Work (`docs/hacp/perturb-seq-eval/publish-complete.md`).
> 3. **When the crawled TechRxiv entry appears in Scholar (days to weeks):** merge it with the manual entry,
>    crawled entry primary (step 1 below). Check its title is the Amendment-5 title and its author is
>    "Mang-yin Mo". If it never appears, check the TechRxiv landing page exposes `citation_title`,
>    `citation_author`, `citation_publication_date` and `citation_pdf_url` (Scholar inclusion guidelines).
> 4. **Semantic Scholar / OpenAlex:** claim the author pages and confirm the Work (7.3 #2–#3); they follow
>    the DOI and need no submission.

Scholar's crawler reads Highwire `citation_*` / Dublin Core / Eprints meta tags and needs, at
minimum, title + authors + date. **arXiv emits these correctly**, which is the entire reason to post
a preprint for Scholar visibility: it is indexed and accrues citations.

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

## Part 7 — Visibility when arXiv endorsement is unavailable

This part is why the venue is TechRxiv and why Part 1 is closed. It also changes what Part 5 can deliver.

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
It follows from the venue, ruled TechRxiv (approvals rows 15 and 32), and it is blocked on the same thing: the
principal's first-hand read of TechRxiv's terms.

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

### 7.2 Endorsement-free venues — and the constraint that eliminates most of them

> **Post to EXACTLY ONE preprint server.** This is the project's standing constraint, unchanged:
> duplicate research is either fully deleted or superseded as a revision, never left as two live
> records. An archive (Zenodo, Figshare) plus one preprint is *one work in several places*, which is
> what the Part 4 cross-links assert. Two preprint servers is duplicate publication.

| Venue | Endorsement | Topical fit for *this* claim | Scholar-indexed | The fact that decides it |
|---|---|---|---|---|
| **TechRxiv** (IEEE) | **none** — moderated only | **good** — electrical engineering, computer science and related technology; the contribution is a compute-allocation method claim | **yes** (listed) | moderation is a scope/plagiarism/English screen, not technical merit; posting in **~4 business days**; **CC BY 4.0 available**, so it matches the Zenodo licence grant; **DOI minted**, and a revised version keeps the DOI with a version indicator |
| **bioRxiv** | **none** | **weak** — the claim is about allocating test-time compute, not about biology | yes | *"Manuscripts already present on other preprint servers will not be posted."* A Zenodo/Figshare **archive** is not a preprint server, so this should not disqualify — but it is the sentence to read before assuming. Also: *"bioRxiv welcomes computational papers"*, yet *"Simple automated/computational analyses of public data, molecular modeling, sequence alignments"* are *"generally not sufficient"* — a real scope risk for a method paper over public Perturb-seq screens |
| **arXiv** | **required, and unavailable** (7.1) | best | yes | needs a named `cs.LG` endorser |
| preprints.org (MDPI), Research Square, OSF Preprints, SSRN | **unknown** | — | — | **Not verified. I did not read their policies, so this document makes no claim about them.** |

**Recommendation: TechRxiv.** It is the only venue measured to be *both* endorsement-free *and*
topically correct; CC BY 4.0 keeps the venue and the archive from disagreeing on reuse terms; and the
minted DOI makes Part 4's reciprocal link work unchanged.

**Honest limit on that recommendation.** `techrxiv.org/faqs` returned **HTTP 403** to the session
that wrote this. Per the standing rule the block is reported, not retried or routed around — so
**every TechRxiv fact in the row above comes from the COAR Directory of Open Access Preprint
Repositories entry, a secondary source.** Before uploading, read on `techrxiv.org` yourself: the
licence list, the moderation criteria, the accepted file format, and whatever it says about material
already deposited in a repository. That is a five-minute read and it is the one thing in this part
that was not measured at the primary source.

**arXiv is closed for this paper (approvals row 32, 2026-11-21).** Row 15 had left it open through a Path-2
endorsement obtained *first*. That option is withdrawn: an endorser search has no date, and once a preprint is up on
TechRxiv a later arXiv posting would be a second live preprint, because a revision on one server cannot supersede a
posting on another. If the terms read fails a check, the fallback is to reopen the endorser route by a new approvals
row — never a second server.

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
| 3 | ~~Principal decides the venue~~ **Decided: TechRxiv only; arXiv closed** (approvals rows 15 and 32) | 7.1, 7.2 |
| 4 | **Record the principal's answers to the four checks of the terms read — is CC BY 4.0 offered, is an ML method paper in scope, is a paper already on Zenodo/Figshare accepted, is a PDF the accepted format. BLOCKS step 5.** The read was reported on 2026-11-09; agents get HTTP 403 and cannot stand in for it. A failed check means a new approvals row, not a second server | 3 |
| 4a | **Archive the revised paper as version `0.6.1`** (principal, 2026-11-08): `build_deposit.py`, then `submit_to_venues.py zenodo --dry-run` and `figshare --dry-run` under the principal's `infisical run` invocation (approvals rows 2–3), review the drafts, then a **separate go** to publish, then `publish.yml` deposit-time step 5 (CITATION version and DOIs, CHANGELOG, Zenodo `isIdenticalTo` Figshare v7). The v0.6.0 records carry the pre-amendment paper and title, so step 6's `isIdenticalTo` would be false against them | nothing (can run in parallel with 4) |
| 5 | Post on TechRxiv. **Upload the same `paper.pdf` that 4a deposited** — the `build_deposit.py` build, md5-identical, not a CI rebuild (the Part 0 CI bundle is LaTeX source) — so "identical" is literally true. This holds only if step 4 records that a PDF is the accepted format; if TechRxiv wants source, stop and re-plan | 4, 4a |
| 6 | Part 4 reciprocal link with the venue DOI, `isIdenticalTo`, once, **on the `0.6.1` Zenodo record** (not v0.6.0 `10.5281/zenodo.23422745`) | 5 |
| 7 | Part 5 Scholar merge, once the crawled record appears (days to weeks) | 5 |
| 8 | Semantic Scholar: add the paper to the claimed author page | 5 |
| 9 | Part 6 OSF cleanup | nothing — independent, and still live and wrong |

**One format caveat on step 5.** Part 0 exists because arXiv compiles from LaTeX source and does not
run BibTeX, so a missing `.bbl` publishes every citation as `[?]`. With a PDF upload that failure mode does not
apply in the same form — you upload the PDF you have already read. **The accepted format is the fourth check
answered at step 4, not something this document establishes**; getting it wrong is the one error in this runbook
that is invisible after publication.

### What Part 7 does not establish

- **That any venue will accept the paper.** Moderation is a human decision made after submission.
- **TechRxiv's rules first-hand.** `techrxiv.org/faqs` returned 403; the row above is secondary-source.
- **preprints.org, Research Square, OSF Preprints or SSRN policies.** Not read. No claim is made.
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
- COAR Directory of Open Access Preprint Repositories, TechRxiv entry — <https://doapr.coar-repositories.org/repositories/techrxiv/> (secondary source; `techrxiv.org/faqs` returned HTTP 403)
- ORCID support, *Add works using an identifier* — <https://support.orcid.org/hc/en-us/articles/360022298153-Add-works-using-an-identifier>

---

## Approval required before posting (7.5 step 5)

Three items: two closed, and one that blocks posting (item 2).

1. **Flush `c0ec931` — CLOSED.** The commit is on `origin/main` and the workflow's LaTeX step has run
   successfully (run `40985145366`; see Part 0, Path A). Path A is available.
2. **Venue — FINAL: TechRxiv only (approvals rows 15 and 32); posting BLOCKED on the recorded terms read.** arXiv was
   measured unreachable without a named `cs.LG` endorser (Part 7.1), so row 12's arXiv ruling is
   superseded. The venue is not conditional; **posting** is, on the principal's first-hand read of TechRxiv's terms
   (licence, scope, prior-posting rule, file format). A failed check means a new approvals row, not a return to row 12. Every TechRxiv fact here comes from a secondary source, and the
   agents' fetch returned HTTP 403. The principal reported the read on 2026-11-09; the answers to its four checks are not yet recorded. Do not submit until they are. Row 32 closes the arXiv path for this paper.
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
  evidence, not proof. Read the `paper.pdf` you upload at 7.5 step 5 before submitting, and the venue's preview after.
- **Any claim about the paper's scientific content.** This is a publication-logistics document.
