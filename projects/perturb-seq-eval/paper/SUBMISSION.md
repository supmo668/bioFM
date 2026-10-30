# Preprint submission runbook — manual steps, for research approval

**Status: READY TO EXECUTE, BLOCKED ON TWO PRINCIPAL DECISIONS (see "Approval required").**
**Owner: the principal. None of this is delegable to an agent** — arXiv has no deposit API for
individual authors, and the license grant is a legal act by a person.

This is the paper-specific **instance**. Three documents divide the work:

| Document | Owns |
|---|---|
| [`scripts/README-arxiv.md`](../../../scripts/README-arxiv.md) | the **tooling** — how the bundle and metadata are produced |
| [`docs/preprint/arxiv-submission-process.md`](../../../docs/preprint/arxiv-submission-process.md) | the **venue process** — every arXiv screen and field, reusable for any paper |
| **this file** | the **instance** — this paper's values, decisions and status |

The pipeline automates everything up to the Submit button; the process document is the button,
and this file is what to type.

**Abstract note:** the arXiv abstract is a *venue-specific override* in `arxiv.toml`, not the
`CITATION.cff` one. The CFF abstract is 2153 characters with 5 non-ASCII characters; arXiv rejects
anything over 1920 and accepts ASCII only. The override is 1906 characters, 0 non-ASCII, with every
number, gate label and the "0 unevaluated" integrity claim preserved. Use the generated block.

| | |
|---|---|
| Work | *Does Agent Confidence Entropy Predict Task Difficulty?* v0.6.0 |
| Already archived | Zenodo concept `10.5281/zenodo.19716140` · Figshare `10.6084/m9.figshare.32086920.v6` (linked `isIdenticalTo`) |
| Author of record | Mang-yin Mo · ORCID `0009-0009-5233-3142` · Carnegie Mellon University |
| Proposed venue | arXiv, primary `cs.LG`, cross-list `q-bio.QM` |
| Licence | CC BY 4.0 (matches the Zenodo deposit, so the records do not disagree on reuse terms) |

---

## The blocking dependency, stated first

**The submission bundle does not exist yet, and cannot be built on this machine.** The paper uses
`\bibliography{references}` and **arXiv does not run BibTeX**, so the bundle must contain a generated
`.bbl` or every citation renders as `[?]` in the announced PDF — compiled, published, and wrong, with
no error to warn you. Generating a `.bbl` needs a TeX toolchain and there is none here (`pdflatex`,
`latexmk`, `bibtex`, `biber` all absent).

So **Part 0 must complete before Part 2 is possible.** There is no workaround that preserves the
bibliography.

---

## Part 0 — Obtain the bundle (pick ONE path)

### Path A — CI builds it (recommended; the pipeline exists for this)

Requires pushing commit `c0ec931`, which is currently held unflushed for your review.

1. Flush the commit (I open a coordination PR on your word — `tools/git-push main` refuses by design).
2. The `arxiv-package` workflow runs on push. Or trigger it directly:
   **Actions → `arxiv-package` → Run workflow →** `paper_dir` = `projects/perturb-seq-eval/paper`.
3. Download the **`arxiv-bundle-*`** artifact. It contains:
   - `perturb-seq-eval-arxiv-<date>.tar.gz` ← **this is what you upload to arXiv**
   - `perturb-seq-eval-arxiv-<date>.manifest.txt` — the file list with sha256 prefixes
   - `arxiv-metadata.txt` — the paste-ready block, identical to Part 2 below
   - **`paper.pdf` is NOT in the artifact** — the workflow asked for it but the upload
     reported only 3 files, and the job asserted `paper.bbl` while never asserting the PDF, so
     its absence passed silently. Measured, not assumed, on run `40985145366`. It costs nothing
     here: arXiv compiles from source and shows you its *own* PDF to preview, which is the one
     that matters. Tracked as a pipeline gap.
4. The job summary carries the same metadata block, so you can read it without downloading.

**The workflow's LaTeX step has never executed.** It is adapted from the working
`paper_standalone/.github/workflows/latex.yml`, but its first real run will be this one. If it fails,
that is a pipeline bug to fix, not a reason to hand-assemble a bundle.

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

1. Log in at <https://arxiv.org/login> (or register). **Use the ORCID-linked route if available** —
   it attaches `0009-0009-5233-3142` to the submission and is what makes the record show up under
   your ORCID profile automatically.
2. Confirm the author profile carries the full name as it appears on the paper: **Mang-yin Mo**.

**Endorsement risk, stated plainly.** arXiv's own submission documentation states that new users, or
users posting to a new category, *"may be required to find endorsements"*, and that *"We only accept
submissions from registered authors"*. The address of record is the **alumni** address recorded in
[`CITATION.cff`](../CITATION.cff) — weaker evidence of current affiliation than a live
institutional one. A
first `cs.LG` submission may therefore land in the endorsement queue.

If it does, you have two routes, and **you must pick one, not both**:
- **Seek endorsement** from a CMU-affiliated arXiv author in `cs.LG` (arXiv shows the endorsement
  request flow in-form), or register with a current institutional address if one exists.
- **Fall back to bioRxiv**, which has **no endorsement requirement**. `q-bio.QM`-shaped work is in
  scope there.

> **Post to EXACTLY ONE preprint server.** Two preprints of one paper is duplicate publication —
> the standing constraint on this project is that duplicate research is either fully deleted or
> superseded as a revision, never left as two live records. arXiv **and** bioRxiv is a violation;
> arXiv **and** the existing Zenodo archive is not, because an archive and a preprint of the same
> work are one work in two places, which is exactly what the cross-links in Part 4 assert.

---

## Part 2 — The submission form, field by field

Start at **arxiv.org → START NEW SUBMISSION**. Values below are generated from
`projects/perturb-seq-eval/CITATION.cff` via the pipeline, so the paper, the repository and this form
cannot drift. Regenerate at any time with:

```bash
uv run --with pyyaml python scripts/arxiv_package.py metadata projects/perturb-seq-eval/paper
```

| Form step | What to do |
|---|---|
| **1. Licence** | Select **CC BY 4.0**. This is an irrevocable grant and a legal act — it is why this step is yours. |
| **2. Archive / category** | Primary **`cs.LG`**; add cross-list **`q-bio.QM`**. |
| **3. Upload** | Upload the **`.tar.gz`**. Do *not* upload `paper.pdf` — arXiv compiles from source, and a PDF-only submission discards the LaTeX. |
| **4. Process** | Let arXiv compile. **Open the generated PDF and check the bibliography renders** — if you see `[?]` anywhere, the `.bbl` is missing and you must stop and rebuild. |
| **5. Metadata** | Paste from the block below. |
| **6. Preview → Submit** | Submit. Moderation follows; announcement is typically the next scheduled mailing. |

### Paste-ready metadata

```text
# metadata sourced from CITATION.cff — single source of truth

=== PASTE INTO THE ARXIV SUBMISSION FORM ===

Title:      Does Agent Confidence Entropy Predict Task Difficulty? A Pre-registered, Provenance-Complete Test of Agentic Hyperparameter Tuning for Perturb-seq Response Prediction
Authors:    Mang-yin Mo
Primary:    cs.LG
Cross-list: q-bio.QM
License:    CC BY 4.0

Comments:
  Pre-registered study; pre-registration and provenance manifests included. Archived with full data and code at doi:10.5281/zenodo.19716140 (concept DOI). The same release is deposited on Figshare as doi:10.6084/m9.figshare.32086920.v6.

Abstract:
  Multi-agent group-generation systems spend test-time compute uniformly across
  tasks. We ask whether the agents' own confidence-and-critique trace predicts
  how hard a task is, which would let the compute be allocated adaptively.
  Taking as testbed a five-agent orchestrator for Perturb-seq response
  prediction inspired by CellForge and operated via MassGen, we define four
  compute-free trace metrics — Agent Confidence Entropy (ACE), Critique Severity
  Dispersion (CSD), a convergence signal (ΔC), and a Winner Flip Rate (WFR) —
  and their composite, the Task Difficulty Index (TDI). We pre-register five
  hypotheses with gates: attainable error on Adamson 2016 (CRISPR interference)
  and Norman 2019 (CRISPR activation), the Architect agent's backbone-choice
  entropy, the rank correlation of each TDI component with held-out error, and
  cross-dataset transfer of a calibrated TDI. The design is 41 held-out K562
  tasks (21 Adamson, 15 Norman singletons, 5 Norman doublets) drawn
  deterministically, a trainer sweep of 27 records per task and three
  fixed-length agentic lifecycle runs per task, all in one process. The LLM
  condition is a pinned roster of Anthropic Claude models (Haiku 4.5 for the
  four proposer roles, Sonnet 5.5 for the Validator) whose served model is
  recorded and asserted per call; a run with any rule-based fallback step is
  invalid. Every run records its git revision, resolved configuration, library
  versions, dataset SHA-256 digests, task plan and label contract. Gate
  outcomes: 4 of 5 gates pass; H5 fails (0 unevaluated) — the trainer sweep
  attains the pre-registered error on both screens (H1, H2), the Architect
  exercises its backbone choice (H3), and the confidence-drop component and the
  composite rank tasks by held-out error within both screens (H4); the
  Adamson-calibrated composite does not transfer to Norman at the pre-registered
  level (H5, ρ = 0.286 against > 0.4). The confidence-entropy point estimates
  run against the pre-registered direction in both screens (exploratory; no
  claim is made). The values reported in the v0.5.0 release of this work are
  superseded in full; the defects behind each are listed in the appendix.

=== END ===

Reminder: arXiv submission is a WEB FORM. There is no deposit API for individual
authors, the license grant is a legal act by a person, and a first submission to a
category may require endorsement. This block exists so the manual step is
copy-paste and reproducible from the repository, not so it can be skipped.
```

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
- arXiv DOI — `10.48550/arXiv.NNNN.NNNNN`

**Check the announced abstract page for:** title and author rendering, the Comments line carrying
`doi:10.5281/zenodo.19716140`, the licence showing CC BY 4.0, and the cross-list to `q-bio.QM`.

Then tell me the arXiv ID and I will update `CITATION.cff` (both the root and the project file),
the two READMEs, and `docs/hacp/perturb-seq-eval/publish-complete.md` so the repository states the
preprint alongside the two archive DOIs. That part *is* mine.

---

## Part 4 — Reciprocal linking on Zenodo (do not skip; this is what prevents "two papers")

The Zenodo record currently carries `isIdenticalTo 10.6084/m9.figshare.32086920.v6`,
`isNewVersionOf` ×2, and `isSupplementedBy` the repository. Add the arXiv record the same way:

1. Zenodo → the v6 record → **Edit** (metadata-only edit; it does **not** mint a new version).
2. Under **Related works**, add:
   - **`is identical to`** → `10.48550/arXiv.NNNN.NNNNN`
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

Scholar's crawler reads Highwire `citation_*` / Dublin Core / Eprints meta tags and needs, at
minimum, title + authors + date. **arXiv emits these correctly**, which is the entire reason to post
a preprint for Scholar visibility: it is indexed and accrues citations.

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

## Approval required before Part 1

Two decisions are mine to ask and yours to make:

1. **Flush `c0ec931`?** Without it CI cannot build the bundle, so Path A is unavailable and the whole
   runbook stalls at Part 0. The honest risk in flushing: the workflow's LaTeX step has never run.
2. **Venue — arXiv or bioRxiv?** arXiv `cs.LG` + `q-bio.QM` is the recommendation (better fit for a
   method claim about compute allocation, and Scholar indexes it well), with the endorsement risk in
   Part 1. bioRxiv avoids endorsement entirely but is a worse topical fit for the contribution.
   **Exactly one.**

A third decision is adjacent and does not block submission, but affects what gets submitted:

3. **The five figure PDFs** — wire them into the paper, retire them, or leave them unreferenced. If
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

- **That the submission will be accepted.** Moderation and endorsement are human decisions made by
  arXiv after you submit. Nothing here predicts them.
- **That the LaTeX compiles on arXiv's TeX Live.** CI compiling it is strong evidence, not proof —
  arXiv's toolchain is its own. Part 2 step 4 is where you find out, and it is why you read the
  generated PDF before submitting rather than after.
- **Any claim about the paper's scientific content.** This is a publication-logistics document.
