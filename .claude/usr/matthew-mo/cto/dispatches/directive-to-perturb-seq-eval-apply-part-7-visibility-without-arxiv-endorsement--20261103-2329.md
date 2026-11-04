---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-11-03T23:29
status: created
priority: high
size: task
subject: "Apply Part 7 (visibility without arXiv endorsement) to SUBMISSION.md on your branch, push, then HOLD /pr-prep until #40 lands"
in_reply_to: null
---

# Apply Part 7 (visibility without arXiv endorsement) to SUBMISSION.md on your branch, push, then HOLD /pr-prep until #40 lands

## What to do

Apply the Part 7 below to `projects/perturb-seq-eval/paper/SUBMISSION.md` **on your branch**
(`perturb-seq-eval`), which is where the live copy of that file is — main's copy is behind yours and
must not be the edit target.

**Placement:** insert it as a new `## Part 7` **immediately after Part 6** and **before**
`## Approval required before Part 1`. It is written to be read before Part 1, and 7.0/7.1 say so;
do not move that claim into Part 1 itself.

**Two edits to existing text, and nothing else:**

1. In **Part 1**, after the sentence ending "...may therefore land in the endorsement queue.",
   add exactly: `**Superseded by Part 7.1 — the policy changed on 2026-01-21 and the queue is now
   the default, not the risk case.**` Leave the rest of Part 1 as written; Part 7.1 carries the
   correction and the evidence. Do not delete or rewrite the old wording — it is a dated record.
2. In **Part 5**, after the first paragraph, add exactly: `**Read Part 7.0 first:** Zenodo is not
   indexed by Google Scholar, so there is currently nothing crawled to merge onto.`

**Do not** touch `arxiv.toml`, the paste-ready metadata block, the abstract, or any other file.
No biological numbers are involved; this is publication logistics.

## Then, in this order

1. Commit the doc edit (`/git-safe-commit`, docs change, no work item needed if the gate allows it;
   it is a documentation-only change to a file your branch already owns).
2. **Push it.** Your branch is currently 2 commits ahead of `origin/perturb-seq-eval` locally — flush
   those too.
3. **Then STOP and wait for my `master-updated` dispatch.** Do NOT run `/pr-prep` yet.

**Why the wait is not optional.** Coordination PR #40 is open and CI-green; when it merges,
`origin/main` advances by 24 commits. A QGR receipt binds the diff of your branch **against the CTO
branch**, so a receipt cut before #40 lands is stale the moment it lands — which is exactly the
failure the pending land already hit: receipt `...20261102-0247-03e8998` covers `09f42d7`, and your
branch tip is now `78be173` on origin with two more commits locally. Cutting a third stale receipt
costs a cycle for nothing.

When I signal, the sequence is `/iteration-start` (merge `origin/main`) → `/pr-prep` → `/pr-submit`,
and I land it.

## Why this content exists

The principal asked what manual follow-up improves visibility given arXiv endorsement is
unavailable. The answer turned out to invalidate an assumption in your runbook: **Zenodo is not
indexed by Google Scholar** (Zenodo's own support page says so), so the existing archive buys zero
Scholar presence and Part 5 currently has nothing to merge onto. And the arXiv endorsement rule
tightened on 2026-01-21 — institutional email is no longer a sole qualifier — so Part 1's "may land
in the queue" is now too soft. Part 7 records both, names the endorsement-free venues with the
measured facts, keeps the one-preprint-server constraint intact, and separates venue choice (the
principal's, exactly one) from index/profile work (unlimited, no duplication risk).

**One source was not read at the primary source:** `techrxiv.org/faqs` returned HTTP 403 to my
session. Per the standing rule the block is reported, not routed around — the TechRxiv facts are from
the COAR directory, a secondary source, and Part 7 says so twice. Do not upgrade them to measured.

---

# INSERT VERBATIM BELOW

## Part 7 — Visibility when arXiv endorsement is unavailable

**Read this before Part 1.** It changes what Part 1 says is possible, and it changes what Part 5
can deliver.

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
It *is* the venue decision in Part 1, and it is now blocked on the same thing.

### 7.1 Part 1 is out of date — the endorsement gate tightened on 2026-01-21

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

Part 1's framing ("a first `cs.LG` submission *may* therefore land in the endorsement queue") was
written against the pre-2026 rule and is now too soft. Under the current policy the queue is the
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

**arXiv is still reachable — but not in parallel.** Pursuing a Path-2 endorsement is compatible with
everything here, *provided you do not post twice.* If arXiv matters more than months of delay, get
the endorsement **first** and wait. If a preprint is already up elsewhere when the endorsement
arrives, the route is a **superseding revision**, never a second live posting.

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
| 3 | **Principal decides the venue** — exactly one (7.2) | 7.1, 7.2 |
| 4 | Read the chosen venue's own submission rules at the primary source | 3 |
| 5 | Part 0 bundle → the venue's form | 4 |
| 6 | Part 4 reciprocal link with the venue DOI, `isIdenticalTo`, once | 5 |
| 7 | Part 5 Scholar merge, once the crawled record appears (days to weeks) | 5 |
| 8 | Semantic Scholar: add the paper to the claimed author page | 5 |
| 9 | Part 6 OSF cleanup | nothing — independent, and still live and wrong |

**One format caveat on step 5.** Part 0 exists because arXiv compiles from LaTeX source and does not
run BibTeX, so a missing `.bbl` publishes every citation as `[?]`. **If the chosen venue takes a
compiled PDF instead of a source bundle, that failure mode does not apply in the same form** — you
upload the PDF you have already read. **Do not conclude either way from this document**: confirm the
accepted format at step 4, because getting it wrong in this direction is the one error in this
runbook that is invisible after publication.

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
