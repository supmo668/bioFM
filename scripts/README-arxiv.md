# Preprint packaging and arXiv submission pipeline

A reusable pipeline that takes any LaTeX paper in this repo to the edge of an arXiv
submission: it assembles the source bundle, refuses to build one that would fail on
arXiv, and emits the metadata to paste into the submission form.

**Nothing in it is specific to one paper.** A paper opts in with a config file.

| Piece | Path | Role |
|---|---|---|
| The tool | `scripts/arxiv_package.py` | preflight · build · metadata · self-test |
| The CI job | `.github/workflows/arxiv-package.yml` | compiles LaTeX (the only place the `.bbl` can be made), runs the tool, uploads the bundle |
| Per-paper config | `<paper-dir>/arxiv.toml` | the only paper-specific file |

## Adding a paper — the whole procedure

1. Put an `arxiv.toml` beside the paper's root `.tex` (see the keys below).
2. Push. The CI job finds it automatically by globbing for `arxiv.toml`.
3. Download the `arxiv-bundle` artifact; the job summary carries the metadata block.

There is no step that edits `arxiv_package.py` or the workflow. If you find yourself
editing either to onboard a paper, that is a gap in the config schema — widen the
schema rather than special-casing the paper.

## Why the last step is manual, and will stay manual

**arXiv has no deposit API for individual authors.** Per
`info.arxiv.org/help/submit`: submission starts by selecting "START NEW SUBMISSION"
in the web interface, *"We only accept submissions from registered authors"*, a new
author or a new category *"may be required to find endorsements"*, *"All submissions
are subject to a moderation process"*, and authors must grant arXiv an irrevocable
license. arXiv's public API is read-only; the interoperability path for bulk deposit
is a partner arrangement for institutional repositories, not an author credential.

So the honest boundary is: **everything up to the Submit button is automated, and the
button is pressed by a person.** This pipeline exists to make that press a single
paste from a reproducible artifact rather than an afternoon of assembling files.

## The check that justifies the whole pipeline

**arXiv does not run BibTeX.** A paper using `\bibliography{...}` must ship the
generated `.bbl` inside its bundle. Omit it and the submission still compiles, still
announces, and renders every citation as `[?]` — published and wrong, with no error
anywhere to warn you. `preflight` fails closed on a missing or empty `.bbl`, and the
CI job asserts the file exists and counts its `\bibitem` entries rather than
inferring its presence from a successful compile.

This is also why the pipeline is CI-shaped rather than a local Makefile: generating
the `.bbl` needs a TeX toolchain, and this repo's dev machines have none — no
`pdflatex`, `latexmk`, `bibtex` or `biber`.

## `arxiv.toml` keys

```toml
root_tex    = "paper.tex"            # required — the document root, relative to this file
bundle_name = "my-project"           # optional — tarball name prefix; defaults to the dir name
citation_cff = "../CITATION.cff"     # optional — source for title / authors / abstract

license  = "CC BY 4.0"               # arXiv's license menu wording
comments = "..."                     # the Comments field; the only place to state an external DOI
acknowledge_packages = []            # packages the pipeline does not vouch for, accepted by the author

title = "..."                        # optional overrides for the CFF-sourced fields
authors = "..."
abstract = "..."

[categories]                         # KEEP THIS TABLE LAST — see the trap below
primary    = "cs.LG"
cross_list = ["q-bio.QM"]
```

### Two traps worth knowing about

**TOML table scoping.** A table header captures every key that follows it, so a
scalar written after `[categories]` silently becomes `categories.license` and reads as
absent everywhere — the only symptom is a metadata field that renders empty, which is
exactly the kind of hole someone pastes into a form without noticing. This bit the
first config written against this pipeline. `load_config` now fails closed on it and
names the fix, and the convention is to keep `[categories]` last in the file.

**Title and abstract live in `CITATION.cff`, not here.** Setting `title` in
`arxiv.toml` is supported but means the repo then carries two answers to one question,
and they will drift. Prefer fixing the CFF.

## What ships in the bundle

**Only files reachable from `root_tex`** — transitively through `\input`/`\include`,
plus `\includegraphics` targets, the `.bbl`, and the `.bib`. Everything else in the
paper directory is left out and reported as `info [unreferenced]`.

That rule is deliberate: a paper directory accumulates superseded sections and
orphaned figures, and shipping them to arXiv publishes dead weight as though it were
part of the work. Read the `unreferenced` lines on every run — they are how you learn
that a figure you thought was in the paper is not. (On `perturb-seq-eval` they
revealed that the v0.6.0 paper references **no figures at all**: `graphicx` is loaded
but unused, all six tables are inline `tabular` environments, and the five figure PDFs
plus the whole `tables/` directory are v0.5-era orphans.)

## What `preflight` checks, and what it does not

Checks, each proven live by `self-test`:

| Check | Fails when |
|---|---|
| `root-tex-exists` | `root_tex` is not there |
| `input-resolves` | an `\input`/`\include` target does not resolve inside the paper dir |
| `graphics-resolve` | an `\includegraphics` target does not resolve |
| `graphics-format` | a figure is not a pdflatex-supported format |
| `no-absolute-paths` | any include or graphic uses an absolute path |
| `no-parent-escape` | any target escapes the bundle via `..` |
| `bbl-present` | `\bibliography` is used and the `.bbl` is missing or empty |
| `packages-vouched` | a `\usepackage` name is outside the vouched TeX Live set and not acknowledged |
| `no-shell-escape` | the document uses `\write18` / `\ShellEscape` |
| `walk-reached-sources` | the root references `\input` files but the parse resolved none |

**Not checked, stated plainly:** whether the document *compiles* — that needs a TeX
toolchain, and the CI job compiles before calling the tool — and anything about arXiv
moderation or endorsement outcomes, which are human decisions made after submission.

`walk-reached-sources` exists because the expensive failure mode of a checker is not a
false alarm but a silent pass: if the parser breaks, every file-resolution check
passes vacuously on a paper it never read. That check asserts the parse found
something before the result is allowed to mean anything.

For the same reason the CI job runs `self-test` **before** it runs `preflight`. Each
case plants one violation and asserts that check fires, and a mirror case asserts a
clean paper still passes, so the suite catches both a dead check and one that fires on
everything. A checker that cannot be made to fail is not evidence.

## Local use

`preflight` and `metadata` need only Python 3.11+ and `pyyaml`:

Run from the repository root, the way CLAUDE.md invokes every repo-level script.
`preflight`, `build` and `self-test` are **stdlib-only**; `metadata` is the one
subcommand that needs `pyyaml`, to read `CITATION.cff`:

```bash
uv run python scripts/arxiv_package.py self-test                    # prove the checks fire
uv run python scripts/arxiv_package.py preflight projects/<p>/paper # expect a .bbl failure locally
uv run --with pyyaml python scripts/arxiv_package.py metadata projects/<p>/paper
```

`build` will refuse locally until a `.bbl` exists, which is correct — without a TeX
toolchain there is no way to make a valid bundle on this machine, and the right answer
is to let CI do it rather than to ship one without a bibliography.

## Endorsement, and the fallback

A first submission to a category can land in arXiv's endorsement queue. The address of
record for this work is an **alumni** address, which is likelier to need endorsement
than a current institutional one. **bioRxiv has no endorsement requirement** and is
the fallback if `cs.LG` stalls — but post to exactly one preprint server. Two
preprints of one paper is duplicate publication, which is the failure this project
already guards against elsewhere.

After the preprint is live, add the reciprocal relation on the Zenodo record
(`isPreprintOf` / `isIdenticalTo`) so the two records read as one work in two places
rather than as two papers.
