---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-11-02T02:17
status: created
priority: normal
subject: "Re: PRINCIPAL RULED (perturb-seq row 12): retitle from three drafts, keep primary cs.LG, ADD cs.MA cross-list"
in_reply_to: 848
---

# Re: PRINCIPAL RULED (perturb-seq row 12): retitle from three drafts, keep primary cs.LG, ADD cs.MA cross-list

# Row 12: item 1 is on staging; item 2 entering the boundary now.

**(1) Three titles** — `origin/perturb-seq-eval-staging` @ `235b116`, ledger `workstreams/perturb-seq-eval/findings-staging/2026-11-02-narrowed-contribution-and-titles.md` §4.3. T1 keeps the locked question form and adds the answer; T2 is declarative and reports the null; T3 leads with the $1-\Delta C$ pass, "Within a Screen" encoding H5. Each carries one line on what it claims and what it does not; none implies a yes for entropy; none says first/novel/new. §4.2 surfaces the constraint that bears on the pick: `PREREGISTRATION.md:25–29` forbids trading a null into a claim-form title, so any retitle is a disclosed post-lock amendment (details in my #842 reply). §5 lists every surface a title change touches, including that the root `CITATION.cff:21` is the REPOSITORY title, not the paper's — the project CFF has one work-title field (`:5–8`); the "two" title fields are `\title` and `pdftitle` at `paper.tex:34–39`.

**(2) cs.MA cross-list** — working branch, `/iteration-start` now; `pr-submit` will reference this dispatch. Planned diff: `arxiv.toml:63` → `["q-bio.QM", "cs.MA"]` + comment rewrite (the comment currently calls the contribution "a method claim … under a confidence-entropy statistic"); the `SUBMISSION.md` runbook rows that restate the cross-list (`:28, :142, :158, :224, :288`). `arxiv_package.py` reads the list; no test pins it. Title fields, CFF and `paper.tex:34–36` untouched until the pick.

Leaving this open until the pr-submit closes item 2.
