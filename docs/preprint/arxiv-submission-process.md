# arXiv submission — the complete, reusable process

**Scope: any paper, any project.** This document is the venue process. It carries no values
for a specific paper; each paper keeps its own values in `<paper-dir>/arxiv.toml` and its own
decisions in a `SUBMISSION.md` beside it. The companion documents:

| Document | Owns |
|---|---|
| `scripts/README-arxiv.md` | the **tooling** — how the bundle and metadata are produced |
| **this file** | the **venue process** — arXiv's screens, fields and rules, in order |
| `<paper-dir>/SUBMISSION.md` | the **instance** — one paper's values, decisions and status |

Every rule below is quoted or paraphrased from arXiv's own documentation
(`info.arxiv.org/help/submit`, `info.arxiv.org/help/prep`), read directly. Where arXiv does not
state something, this document says so rather than guessing.

---

## Part A — Before you open the form

### A1. The one failure that is silent

**arXiv does not run BibTeX.** If the document uses `\bibliography{...}`, the submitted source
must contain the generated `.bbl`. Omit it and the submission *still compiles, still announces,
and renders every citation as* `[?]` — published and wrong, with nothing in the compile log to
warn you.

Everything in the tooling exists for this one fact. `preflight` fails closed on a missing or
empty `.bbl`; CI asserts the file exists and counts its `\bibitem` entries rather than inferring
it from a successful compile.

### A2. Build the bundle (never hand-assemble it)

```bash
# In CI: Actions -> arxiv-package -> Run workflow -> paper_dir = <paper-dir>
# Download the arxiv-bundle-* artifact.

# Locally, only if a TeX toolchain is installed:
cd <paper-dir> && latexmk -pdf paper.tex          # generates paper.bbl
cd "$(git rev-parse --show-toplevel)"
uv run python scripts/arxiv_package.py build <paper-dir> --out dist/arxiv
```

### A3. Verify the bundle before uploading

```bash
tar tzf <bundle>.tar.gz
```

- Files must sit **at the archive root** — no wrapping directory. Subdirectories such as
  `sections/` and `figures/` are fine; a top-level `paper/` wrapper is not.
- `paper.bbl` must be present and non-empty. If it is missing: **stop**, do not proceed.
- The manifest lists every file with a sha256 prefix. Only files reachable from the root `.tex`
  are included; anything else in the paper directory is deliberately excluded and reported by
  `preflight` as `info [unreferenced]`. **Read those lines** — they are how you discover that a
  figure you believed was in the paper is not.

### A4. Account, authorship, endorsement

- You must be a **registered author**; anonymous submissions are not accepted.
- Prefer the **ORCID-linked** login so the record attaches to your ORCID profile automatically.
- *"If you are a new user or are submitting to a new category, you may be required to find
  endorsements."* A first submission to a category can therefore queue. An **alumni or personal
  address is weaker evidence of current affiliation** than a live institutional one.
- If endorsement blocks you: either request endorsement from an author already publishing in
  that category, or use a preprint server with no endorsement requirement (bioRxiv/medRxiv for
  life sciences).

> **Post to exactly ONE preprint server.** A preprint plus a repository archive (Zenodo,
> Figshare) of the same manuscript is *one work in several places*, which the cross-links in
> Part D assert. The same paper on **two preprint servers** is duplicate publication.

### A5. Source format rules

- Preferred source order: **(La)TeX, AMS(La)TeX, PDFLaTeX**, then PDF, then HTML.
- *"We do not accept dvi, PS, or PDF created from TeX/LaTeX source."* Upload the **source**, not
  a compiled PDF, whenever the paper was written in TeX.
- Figures: PS/EPS require LaTeX processing; **JPEG, GIF, PNG or PDF require PDFLaTeX**. Do not
  mix the two families — mixed figure formats are one of arXiv's four named compile failures.
- Filenames may contain only `a-z A-Z 0-9 _ + - . , =`. Names are **case sensitive** and
  references must match case.
- *"We do not accept submissions with omitted figures, even if you provide links to view
  figures externally."*

---

## Part B — The upload and compile screens, in arXiv's own order

These are arXiv's documented steps. Screen labels occasionally change; the sequence does not.

| Step | Screen | What to do |
|---|---|---|
| 1 | **Prepare Files** | **Choose File** → select the `.tar.gz` → **Upload**. Use zip or tar.gz for multiple files, subfolders or ancillary files. Review the file list and delete anything unnecessary (trashcan icon; **Delete All** restarts). |
| 2 | **Check Files** | Click **Check Files**. arXiv analyses the upload to identify the processor, the top-level TeX file and extraneous files. |
| 3 | **Compiler** | Confirm the auto-detected compiler, or pick another from the dropdown. |
| 4 | **Top-Level TeX file** | Confirm the auto-detected root. Only files containing `\documentclass` are listed. Selecting several concatenates their output in order — for a single-document paper, **exactly one** must be selected. |
| 5 | **Auto-detected Notes** | Review files arXiv recommends deleting. **Uncheck anything you want to keep.** `paper.bbl` must survive this screen. **Return to Upload Step** restarts. |
| 6 | **Accept and Continue** | Proceed. |
| 7 | **Deletion confirmation** | Confirm the deletion list in the pop-up → **Confirm**. Last chance to save a file arXiv wanted to drop. |
| 8 | **Compilation result** | Read the log. If it compiled, **Preview your PDF** — then actually open it (see B1). **Continue** goes to Metadata. |
| 9 | **Metadata** | Part C. |
| 10 | **Verify and submit** | *"be sure to carefully check the title and abstract (metadata) and the processed files"* → **Submit Article**. |

### B1. What to check in the previewed PDF — the step people skip

1. **The bibliography renders.** Any `[?]` means the `.bbl` is missing or was deleted at step 5.
   Stop and fix; do not submit.
2. **Every figure appears**, and in the right place.
3. **The title and author line** match what you will type in Part C.
4. **No LaTeX error artifacts** — stray `??`, missing symbols, overfull boxes that break a table.

### B1a. Compile with the engine arXiv will use

arXiv routes **PS/EPS figures through LaTeX** and **JPEG/GIF/PNG/PDF figures through
PDFLaTeX**. If your CI compiles with a different engine than arXiv will choose, a green CI
build is weak evidence about the submission.

Concretely: `latexmk` with no `-pdf` runs in **DVI mode** — it calls `latex`, writes a `.dvi`,
and produces no PDF at all. In `xu-cheng/latex-action`, passing `args` **overrides** the
default argument list, so omitting `-pdf` silently drops you into DVI mode. This happened
here and went unnoticed until an assertion on `paper.pdf` was added. Always pass `-pdf`
(or set the xelatex/lualatex input) and **assert the PDF exists** rather than inferring it
from a successful compile.

### B2. arXiv's four named compile failures

- Mixed figure formats (EPS with PDFLaTeX, or PDF/PNG/JPEG with LaTeX).
- `hyperref` option clashes — *look further down the log*, the real error is below the clash.
- Missing or differing style files — bundle any non-standard `.sty`.
- Missing, misnamed, or **absolute-path** figure files. `preflight`'s `no-absolute-paths` and
  `no-parent-escape` checks exist to catch this before upload.

---

## Part C — The metadata form, field by field

**All metadata fields accept ASCII only:** *"Our metadata fields only accept ASCII input."*
Curly quotes, long dashes and `fi`/`ff` ligatures pasted from a PDF cause `Bad character(s)`
errors. Accented characters may be typed directly or entered as TeX (`\'e`, `\c{C}`, ISO
Latin-1 only).

| Field | Rules |
|---|---|
| **Title** (required) | Not all uppercase. **Unicode not allowed**; some MathJax is. Expand opaque TeX macros. Accent commands allowed. |
| **Authors** (required) | `Firstname Lastname` or `Firstname Middlename Lastname`. List **all** authors — never `et al.` Separate with a comma or `and`. No honorifics or degree suffixes; `Jr.` attaches without a comma. Affiliations in **parentheses**, at most city and country. Shared affiliations use numbered notation: `Author One (1), Author Two (1 and 2)` then `((1) Institution One, (2) Institution Two)`. Generative AI cannot be an author. Roles (editor, appendix author) go in **Comments**, not here. |
| **Abstract** (required) | **Over 1920 characters is rejected.** Do not include the word "Abstract". Hard line breaks are stripped *unless the next line starts with leading whitespace* — that is how you make paragraphs. Omit TeX formatting commands (`\em`, spacing); some math works via MathJax. **Unicode not supported.** Avoid blank lines. |
| **Categories** | One **primary** category plus zero or more **cross-lists**. Categories decide which mailings announce the paper and which searches find it. No documented cross-list limit. |
| **Comments** (optional, recommended) | Page and figure counts; "submitted to" / "to be published in"; author roles; for a replacement, the nature and severity of changes. **URLs are allowed** — put a space after a URL before any punctuation or it is read as part of the URL. **Do not put copyright statements here.** Frozen after announcement; changeable only via a replacement, and replacement comments are **not cumulative**. |
| **Journal-ref** | **Only** for a full bibliographic reference to a journal or proceedings where the article has **already appeared** — volume, year, pages. No URLs. If not yet published, leave empty and use Comments. Can be added later via the journal-reference facility. |
| **DOI** | *"Use only for a DOI that resolves to another version of the article, such as the journal version."* **Do not** add the arXiv-assigned DOI — that is automatic. Separate multiple DOIs with a space, nothing else. |
| **Report-no** | Only if your institution assigned one. The local number alone, e.g. `EFI-94-11`. |
| **ACM-class** | `cs` archives only. ACM CCS codes, separated by `; ` — e.g. `F.2.2; I.2.7`. |
| **MSC-class** | `math` archives only. e.g. `14J60 (Primary) 14F05, 14J26 (Secondary)`. |

### C1. Where an archive DOI belongs — corrected

If the work is already deposited in a repository (Zenodo, Figshare, an institutional
repository), that deposit **is "another version of the article"**, so its DOI belongs in the
**DOI** field. arXiv's wording says *"such as the journal version"* as an **example**, not a
restriction to journals.

`Journal-ref` is different and must stay **empty**: it is only for a work that has already
appeared in a journal or proceedings, and a repository is neither.

Putting the archive DOI in **Comments as well** is harmless and makes it visible in the abstract
listing, where readers see it without opening the metadata.

---

## Part D — After submission

### D1. Announcement timing

*"New submissions received by 14:00 (Eastern Daylight/Standard Time Zone) are generally made
available at 20:00 (Eastern)."* Submissions and edits completed before 14:00 ET Monday–Friday
should not delay announcement. **All submissions go through moderation**, which can add delay
beyond this schedule.

### D2. Before announcement — fixing things

- **Edits before public announcement do not create a new version.** Correct metadata freely.
- **Unsubmit** (icon on your user page) returns the submission to incomplete status. Announcement
  is then rescheduled from the resubmission time.
- **Never open a second submission for a correction:** *"DO NOT make a new submission for a
  corrected article or for an erratum."* Use **replace**.

### D3. Record the identifiers

arXiv mints both:

- **arXiv ID** — `arXiv:NNNN.NNNNN`
- **arXiv DOI** — `10.48550/arXiv.NNNN.NNNNN` (automatic; never typed into the DOI field)

Check the announced abstract page for: title and author rendering, the Comments line, the
licence, and the cross-list.

### D4. Reciprocal links — what stops "one work" reading as "several papers"

On each repository record (Zenodo, Figshare), add a relation to the arXiv DOI.

- **`isIdenticalTo`** — use when the deposited manuscript and the arXiv source are the same
  work. Consistent with how two repository deposits of one release are normally linked.
- **`hasPreprint`** — additionally asserts that the repository record is archival and arXiv is
  the preprint. More precise, but it makes a venue-hierarchy claim the deposit may not otherwise
  make.

**Pick one and apply it consistently. Never add both.** On Zenodo this is a *metadata-only*
edit — it does **not** mint a new version.

### D5. Google Scholar

Scholar's crawler reads Highwire `citation_*`, Dublin Core and Eprints meta tags, needing at
minimum **title + authors + date**. arXiv emits these correctly, which is the whole reason a
preprint helps discovery.

- A **manually added** Scholar profile entry is **profile-only: not indexed, and it accrues no
  citations.** Once the crawled arXiv record appears, **merge** the manual entry into it and keep
  the crawled one primary.
- A manual entry that records the repository as the *Journal* is wrong — a repository is not a
  journal. Merging onto the crawled record fixes it.

### D6. Update the repository to state the preprint

Add the arXiv ID and DOI to `CITATION.cff` (root and project), the READMEs, and whatever review
surface records publication state, so the repository and the venues agree.

---

## Part E — Reusing this for the next paper

1. Create `<paper-dir>/arxiv.toml`. Keep `[categories]` **last** — a TOML table header captures
   every key that follows it, so a scalar placed after it silently becomes `categories.<key>`
   and reads as absent. `load_config` fails closed on this and names the fix.
2. Point `citation_cff` at the paper's `CITATION.cff` so title, authors and abstract have one
   source and cannot drift.
3. Run `uv run python scripts/arxiv_package.py self-test` — then `preflight`, then `metadata`.
4. Choose the primary category and cross-lists from arXiv's category list; state the reasoning
   in `arxiv.toml` comments, because "why this category" is the question a reviewer asks later.
5. Write a `SUBMISSION.md` beside the paper for the values and decisions. **Do not copy this
   file** — link it.

### E1. Checks the tooling performs, and what it does not

`preflight` runs ten checks — root-tex existence, `\input` resolution, graphics resolution and
format, no absolute paths, no `..` escapes, `.bbl` presence, package vouching, no `\write18`,
and `walk-reached-sources`. Each is **proven live** by `self-test`, which plants one violation
per check and asserts it fires, plus a mirror asserting a clean paper still passes.

**Not checked, stated plainly:** whether the document *compiles* (CI does that before calling
the tool) and anything about arXiv moderation or endorsement outcomes, which are human decisions
made after submission.

`walk-reached-sources` exists because the expensive failure of a checker is not a false alarm
but a **silent pass**: if the parser breaks, every file-resolution check passes vacuously on a
paper it never read. CI runs `self-test` *before* `preflight` for the same reason — a checker
that cannot be made to fail is not evidence.
