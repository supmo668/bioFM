# Preprint and Publication Venue APIs — Research Dossier

> Last surveyed: 2026-04-21. Maintained at **repo-root level** under
> `research/` so it's not coupled to any single project.
>
> Goal: catalogue every venue where a manuscript + artifacts can be
> published **without a peer-review approval turnaround**, ordered from
> fastest to slowest, with concrete API / manual-step instructions.
>
> Scope: non-peer-reviewed preprints and open-data archives that issue
> a DOI. Paid / peer-reviewed journals are out of scope unless their
> review-free path (e.g. "In Review") is fast.

## 0. TL;DR recommendation

For this repository (bio × ML, hackathon-origin, code + data + PDF) the
fastest path to a citable DOI is:

1. **Zenodo** for the artifact bundle + PDF (5 min signup → DOI in < 1 min after upload, fully API-driven, no moderation).
2. **Figshare** as a parallel mirror if you want a second DOI target (same-day, API).
3. **OSF Preprints / BioHackrXiv** for community visibility (OSF API submission, 0–24 h light moderation; BioHackrXiv explicitly accepts hackathon outputs).
4. **bioRxiv** once you want biology-community reach (24–72 h screening, no submission API — web form only).
5. **arXiv** only if you have endorsement already — new 2026 policy made first-time submission much harder (see §3.9).

`GitHub release → Zenodo → Figshare → OSF Preprints` is the four-step
flow I'd automate first. All four have submission APIs and zero or
minimal moderation.

## 1. Ranked table

| Rank | Venue | Domain | Submission API? | Moderation | Time signup → DOI | Cost | Notes |
|---|---|---|---|---|---|---|---|
| 1 | **Zenodo** | any (CERN-operated) | ✅ REST | none | **~1 min after upload** | free | Pair with GitHub releases for 1-click auto-archive |
| 2 | **Figshare** | any | ✅ REST | none (light spam check) | **~5 min** | free tier | FTPS + REST for large files |
| 3 | **OSF Preprints** (via `osf.io/preprints/*`) | multi-server | ✅ JSON:API v2 | community-dependent, usually < 24 h | **0–24 h** | free | Servers: MetaArXiv, PsyArXiv, SocArXiv, MindRxiv, BioHackrXiv, etc. |
| 3a | **BioHackrXiv** (OSF) | biology / bioinformatics | ✅ (OSF API) | light | **< 24 h** | free | Explicit hackathon fit; requires hackathon provenance |
| 4 | **Preprints.org** (MDPI) | multidisciplinary | ❌ web form only | yes, 24 h SLA | **~24 h** | free | Free DOI, good abstract indexing |
| 5 | **bioRxiv** | biology | ❌ web form only | yes, 24–72 h typically 24–48 h | **1–3 days** | free | Strong biology community; rejects purely computational work sometimes |
| 6 | **medRxiv** | medical / clinical | ❌ web form only | yes, similar to bioRxiv | **1–3 days** | free | Medical-oriented; gated for clinical trials |
| 7 | **Research Square** (Springer Nature In Review) | any with SN journal submission | ❌ web form only (expedited: 48 h) | yes | **2 days (expedited) – 3 weeks** | free | Tied to journal submissions via In Review |
| 8 | **SSRN** (Elsevier) | social sci + CS/econ subset | ❌ web form only | yes, ~days | **2–5 days** | free | Readonly API via Elsevier Scopus |
| 9 | **ChemRxiv** | chemistry | ❌ web form only | yes | **~24–48 h** | free | Chemistry-gated; probably wrong fit here |
| 10 | **HAL** (CNRS) | any, strong in EU | ✅ partial SWORD API | yes, varies | **1–3 days** | free | Institutional; more bureaucratic |
| 11 | **TechRxiv** (IEEE) | engineering / CS | ❌ | **platform transition in progress (Mar 2026) — submissions temporarily closed** | — | free | Skip until migration ends |
| 12 | **arXiv** | physics / math / CS | ❌ web form only | **endorsement required for first submitters** | **days to weeks** (endorsement) | free | 2026-01-21 policy update tightened endorsement requirements |

Any item marked ❌ for submission API still has a read API for metadata
retrieval (Crossref, Europe PMC, OpenAlex cover most).

## 2. What to use when

| Situation | Recommended venue |
|---|---|
| "I need a citable DOI in the next 15 minutes." | Zenodo |
| "I want GitHub release → permanent archive on every tag." | Zenodo (via GitHub integration) |
| "I want a second DOI for the data tables separately from the PDF." | Figshare (artifact) + Zenodo (paper) |
| "It's a hackathon output; I want to flag that." | BioHackrXiv (via OSF) |
| "I want a biology-community-visible preprint." | bioRxiv (accept the 1–3 day moderation) |
| "I want an ML-community-visible preprint." | arXiv (if endorsed) or OpenReview (venue-gated) |
| "I want cross-disciplinary visibility with an editorial sheen." | Preprints.org |

## 3. Per-venue detail

### 3.1 Zenodo — PRIMARY RECOMMENDATION

- **Home**: <https://zenodo.org>
- **Dev docs**: <https://developers.zenodo.org/>
- **Sandbox**: <https://sandbox.zenodo.org> (test DOIs with 10.5072 prefix; production uses 10.5281)
- **API base**: `https://zenodo.org/api`

#### Signup + token

1. Register at <https://zenodo.org/signup> (GitHub / ORCID login supported; takes < 1 min).
2. Go to **Settings → Applications → Personal access tokens**.
3. Click **New token**. Scopes needed: `deposit:write`, `deposit:actions` (and optionally `deposit:actions` for publish).
4. Copy the token (only shown once). Export as `ZENODO_TOKEN`.

#### Submit via API — minimum working example

```bash
export ZENODO_TOKEN=...
BASE=https://zenodo.org/api

# 1. Create empty deposition
DEP=$(curl -s -X POST "$BASE/deposit/depositions" \
  -H "Authorization: Bearer $ZENODO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}')
BUCKET=$(jq -r '.links.bucket' <<< "$DEP")
DEP_ID=$(jq -r '.id' <<< "$DEP")

# 2. Upload files (new bucket API, streams, no 100 MB limit)
curl -s -X PUT "$BUCKET/paper.pdf" \
  -H "Authorization: Bearer $ZENODO_TOKEN" \
  --data-binary @paper.pdf
curl -s -X PUT "$BUCKET/supplement.zip" \
  -H "Authorization: Bearer $ZENODO_TOKEN" \
  --data-binary @supplement.zip

# 3. Attach metadata
curl -s -X PUT "$BASE/deposit/depositions/$DEP_ID" \
  -H "Authorization: Bearer $ZENODO_TOKEN" \
  -H "Content-Type: application/json" \
  -d @metadata.json

# 4. Publish to mint the DOI
curl -s -X POST "$BASE/deposit/depositions/$DEP_ID/actions/publish" \
  -H "Authorization: Bearer $ZENODO_TOKEN"
```

`metadata.json` must contain `metadata.upload_type`, `metadata.title`,
`metadata.creators`, `metadata.description`. See
<https://developers.zenodo.org/#representation> for the full schema.

#### GitHub ↔ Zenodo auto-archive

- Sign in to Zenodo with GitHub; toggle your repo **on** in the GitHub integration page.
- Every time you create a **release** on GitHub, Zenodo auto-archives the tarball and mints a DOI.
- Zero further action required per release.

Docs: <https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content>.

#### Gotchas

- A published deposition is immutable; new versions mint new DOIs via the **New Version** action.
- API rate limit: 60 req/min (anonymous), 100 req/min (authenticated).

### 3.2 Figshare

- **Home**: <https://figshare.com>
- **API docs**: <https://docs.figshare.com>
- **API base**: `https://api.figshare.com/v2`

#### Signup + token

1. Register at <https://figshare.com>.
2. **User icon → Applications → Create Personal Token** (note it; non-recoverable).
3. Export as `FIGSHARE_TOKEN`.

#### Submit via API

```bash
export FIGSHARE_TOKEN=...
BASE=https://api.figshare.com/v2

# 1. Create article
ART=$(curl -s -X POST "$BASE/account/articles" \
  -H "Authorization: token $FIGSHARE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My preprint","defined_type":"preprint","tags":["ML","bio"]}')
ART_ID=$(jq -r '.location' <<< "$ART" | awk -F/ '{print $NF}')

# 2. Upload file (multi-step: init upload, send chunks, finalise)
SIZE=$(stat -c%s paper.pdf)
MD5=$(md5sum paper.pdf | cut -d' ' -f1)
FILE=$(curl -s -X POST "$BASE/account/articles/$ART_ID/files" \
  -H "Authorization: token $FIGSHARE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"paper.pdf\",\"size\":$SIZE,\"md5\":\"$MD5\"}")
FILE_ID=$(jq -r '.location' <<< "$FILE" | awk -F/ '{print $NF}')
UPLOAD_URL=$(curl -s "$BASE/account/articles/$ART_ID/files/$FILE_ID" \
  -H "Authorization: token $FIGSHARE_TOKEN" | jq -r '.upload_url')
# loop through the parts returned by GET $UPLOAD_URL and PUT each chunk
# ... (see docs.figshare.com upload example)

# 3. Reserve DOI (Figshare assigns a DOI only after "publish")
curl -s -X POST "$BASE/account/articles/$ART_ID/reserve_doi" \
  -H "Authorization: token $FIGSHARE_TOKEN"

# 4. Publish
curl -s -X POST "$BASE/account/articles/$ART_ID/publish" \
  -H "Authorization: token $FIGSHARE_TOKEN"
```

Full worked Python example: <https://docs.figshare.com/old_docs/api/upload_example/>.

#### Gotchas

- Free-tier storage limit: 20 GB.
- Files > 2 GB must use the multi-part upload flow above.

### 3.3 OSF Preprints (MetaArXiv, PsyArXiv, SocArXiv, BioHackrXiv, …)

- **Home**: <https://osf.io/preprints>
- **API docs**: <https://developer.osf.io/>
- **API base**: `https://api.osf.io/v2`
- **Format**: [JSON:API 1.0](https://jsonapi.org/)

#### Server selection

OSF hosts many community preprint servers on shared infrastructure. Each server has its own moderation rules but the same API.

- **MetaArXiv** — meta-science.
- **PsyArXiv** — psychology.
- **SocArXiv** — social sciences.
- **BioHackrXiv** — bioinformatics hackathon outputs (requires first/last/corresponding author to have participated in the event). See <https://guide.biohackrxiv.org>.
- **MindRxiv, AgriRxiv, LawArXiv, …** — full list at <https://osf.io/preprints/discover>.

Given this repository originated in the ContextualGenticmen Hackathon, **BioHackrXiv is an explicit fit**.

#### Signup + token

1. Register at <https://osf.io>.
2. **Settings → Personal access tokens → Create token**. Scopes: `osf.full_write`.
3. Export as `OSF_TOKEN`.

#### Submit via API

```bash
export OSF_TOKEN=...
BASE=https://api.osf.io/v2
PROVIDER=biohackrxiv  # or metaarxiv, psyarxiv, socarxiv, etc.

# 1. Upload the PDF into an OSF project (project first, preprint second)
PROJ=$(curl -s -X POST "$BASE/nodes/" \
  -H "Authorization: Bearer $OSF_TOKEN" \
  -H "Content-Type: application/vnd.api+json" \
  -d '{"data":{"type":"nodes","attributes":{"title":"My preprint","category":"project"}}}')
PROJ_ID=$(jq -r '.data.id' <<< "$PROJ")

# Upload file to the project's OSFStorage
curl -s -X PUT "https://files.osf.io/v1/resources/$PROJ_ID/providers/osfstorage/?kind=file&name=paper.pdf" \
  -H "Authorization: Bearer $OSF_TOKEN" \
  --data-binary @paper.pdf

# 2. Create the preprint, link it to the uploaded file and the provider
curl -s -X POST "$BASE/preprints/" \
  -H "Authorization: Bearer $OSF_TOKEN" \
  -H "Content-Type: application/vnd.api+json" \
  -d @preprint_metadata.jsonapi
```

Full example: <https://developer.osf.io/#operation/preprints_create>.

#### Moderation

- BioHackrXiv: manual moderation, typically < 24 h.
- MetaArXiv, PsyArXiv: light moderation, often minutes.

### 3.4 Preprints.org (MDPI)

- **Home**: <https://www.preprints.org>
- **Submission**: <https://www.preprints.org/submit> (web form only)
- **No public submission API.**
- **Moderation**: within 24 h per their SLA.
- **DOI**: Assigned on publication.
- **Cost**: free.

Manual flow:

1. Register at <https://www.preprints.org/user/register>.
2. Click **Submit a Preprint**, follow the six-step form (authors, metadata, files, categories, funding, ethics).
3. Wait up to 24 h for the staff review.

### 3.5 bioRxiv

- **Home**: <https://www.biorxiv.org>
- **Submission portal**: <https://submit.biorxiv.org>
- **Read-only API**: <https://api.biorxiv.org>
- **No submission API.**
- **Screening**: 24–48 h (72 h over weekends/holidays).
- **DOI**: Assigned on screening pass.

Manual flow:

1. Register at <https://submit.biorxiv.org>.
2. Start a new submission; upload PDF (compiled) plus **source** (e.g. `.tex` + figures).
3. Add licence (CC-BY is standard), affiliations, funding.
4. Submit. Expect 1–3 days.

Gotcha: **bioRxiv sometimes rejects purely-computational manuscripts** that have no biological prediction or validation, preferring they go to arXiv. If rejected, the fallback is arXiv (needs endorsement) or a follow-on Zenodo upload.

### 3.6 medRxiv

- **Home**: <https://www.medrxiv.org>
- **Submission portal**: <https://submit.medrxiv.org>
- Same submission flow as bioRxiv.
- Screening typically 24–48 h; **clinical trial content goes through an extra compliance review** which can take a week.

### 3.7 Research Square (Springer Nature "In Review")

- **Home**: <https://www.researchsquare.com>
- **Preprint portal**: <https://www.researchsquare.com/submit>
- **No direct submission API**; expedited posting is possible via the web form (48 h).
- **In Review** service is tied to a Springer Nature journal submission (most useful if you're about to submit to an SN journal anyway).

### 3.8 SSRN

- **Home**: <https://www.ssrn.com>
- Submission via <https://hq.ssrn.com/submission>
- No submission API.
- Moderation 2–5 days.
- Relevant sub-networks: **CompSciRN** (computer science) and **EconomicsRN**.

### 3.9 arXiv — NEW 2026 ENDORSEMENT POLICY

- **Home**: <https://arxiv.org>
- **No submission API.**
- **Endorsement required for first-time submitters** as of 2026-01-21. Two paths:
  1. **Institutional-email + prior-authorship**: you need an academic email address *and* to be a co-author on an already-accepted arXiv paper in the same endorsement domain (e.g. `cs.LG`).
  2. **Personal endorsement**: an existing arXiv author in the target endorsement domain vouches for you via the <https://arxiv.org/user/> endorsement form.

See <https://blog.arxiv.org/2026/01/21/attention-authors-updated-endorsement-policy/>.

Practical implications for this repo:

- If any co-author already has an arXiv paper in `cs.LG` or `q-bio`, use path (1).
- Otherwise, post to Zenodo immediately, then email 2–3 arXiv authors in `cs.LG` with the Zenodo link asking for a personal endorsement. Typical turnaround 1–7 days.

#### Endorsement request etiquette

- Read <https://info.arxiv.org/help/endorsement.html> carefully.
- Send a concise email (≤ 150 words) with: the Zenodo DOI, a 2-sentence abstract, a one-line "would you be willing to endorse me for cs.LG".
- Don't mass-mail; pick endorsers whose recent papers cite similar work.

### 3.10 HAL (CNRS open archive)

- **Home**: <https://hal.science>
- **API**: partial [SWORD protocol](https://swordapp.org) for institutional deposits.
- **Moderation**: varies per institution; typically 1–3 days.
- Useful if a co-author has a French institutional affiliation or you want European indexing.

### 3.11 TechRxiv (IEEE)

- **Home**: <https://www.techrxiv.org>
- **Status (2026-03)**: platform transition in progress; **submissions are temporarily closed**. Skip until the new platform lands.

### 3.12 OpenReview

- **Home**: <https://openreview.net>
- **API docs**: <https://docs.openreview.net>
- **API base**: `https://api2.openreview.net`
- Submissions are **venue-gated** — you submit to a specific venue (ICLR, COLM, …) not to OpenReview-as-a-preprint-server.
- Non-venue public posting exists but requires a venue admin to create the invitation. Not practical for a standalone preprint.

### 3.13 DOI-only paths (no hosting)

If you already self-host the PDF (e.g. on your repo's GitHub Pages) and just need a citable DOI:

- **DataCite Fabrica** — requires institutional membership (fee), not practical for individuals.
- **Zenodo is the effective individual-friendly DataCite DOI issuer.**
- **Crossref** — for journal/conference DOIs, not preprints. Publisher-facing.

Simplest practical answer: just upload to Zenodo and let them mint the DOI.

## 4. Recommended submission order for *this* repo

1. **Immediate (today)**:
   - `git tag -a v0.3.0-supplement -m "Supplement release"` and push to GitHub.
   - If Zenodo↔GitHub integration is enabled, the DOI mints automatically when you create the GitHub **Release** from that tag.
   - Otherwise, `scripts/publish/zenodo_upload.py` (add to repo) with the bucket-API flow from §3.1.
2. **Same-day**:
   - Mirror the artifact to Figshare via the API (§3.2). Second DOI.
3. **This week**:
   - Submit PDF to BioHackrXiv via OSF API (§3.3) tagged as a ContextualGenticmen hackathon output.
4. **Next week**:
   - Submit the biology-polished version to bioRxiv web form (§3.5). Expect 1–3 days.
   - In parallel, request arXiv endorsement (§3.9) with the Zenodo DOI already in hand.

## 5. Automation helper (to write next)

Proposed new script at repo root: `scripts/publish/submit_to_preprint_venues.py`. Planned commands:

```bash
# 1. Local dry-run: build artefact bundle, validate metadata
python scripts/publish/submit_to_preprint_venues.py validate --config publish.yml

# 2. Zenodo — dispatch new deposition + publish
python scripts/publish/submit_to_preprint_venues.py zenodo --config publish.yml

# 3. Figshare — dispatch + publish
python scripts/publish/submit_to_preprint_venues.py figshare --config publish.yml

# 4. OSF Preprints (BioHackrXiv) — dispatch + publish
python scripts/publish/submit_to_preprint_venues.py osf --server biohackrxiv --config publish.yml
```

All three venues share a common `publish.yml` metadata spec; the script
is ~250 lines of straight `httpx` + `pydantic`. See §3.1–3.3 for the
curl equivalents.

## 6. Links worth bookmarking

- [Zenodo developer portal](https://developers.zenodo.org/)
- [Figshare API v2](https://docs.figshare.com)
- [OSF v2 API](https://developer.osf.io/)
- [BioHackrXiv submission guide](https://guide.biohackrxiv.org/submission_guidelines.html)
- [bioRxiv submission guide](https://www.biorxiv.org/about/FAQ)
- [arXiv endorsement explainer](https://info.arxiv.org/help/endorsement.html)
- [arXiv 2026 policy update](https://blog.arxiv.org/2026/01/21/attention-authors-updated-endorsement-policy/)
- [Preprints.org submission guidelines](https://www.preprints.org/help-center/submission-guidelines)
- [OpenReview API docs](https://docs.openreview.net/getting-started/using-the-api)

## Sources

- [Zenodo developer docs](https://developers.zenodo.org/)
- [Figshare API v2 docs](https://docs.figshare.com/)
- [Figshare personal token guide](https://help.figshare.com/article/how-to-get-a-personal-token)
- [OSF Preprints home](https://osf.io/preprints)
- [BioHackrXiv submission guidelines](http://guide.biohackrxiv.org/submission_guidelines.html)
- [OpenReview API](https://docs.openreview.net/getting-started/using-the-api)
- [bioRxiv FAQ (screening 24–48 h)](https://www.biorxiv.org/about/FAQ)
- [bioRxiv API](https://api.biorxiv.org/)
- [arXiv endorsement policy](https://info.arxiv.org/help/endorsement.html)
- [arXiv 2026 endorsement policy update](https://blog.arxiv.org/2026/01/21/attention-authors-updated-endorsement-policy/)
- [Preprints.org submission guidelines](https://www.preprints.org/help-center/submission-guidelines)
- [Research Square preprints help](https://support.researchsquare.com/support/solutions/articles/6000271853-after-opting-in-to-in-review-how-long-will-it-take-for-my-preprint-to-be-posted-on-research-square-)
- [TechRxiv (platform migration 2026-03)](https://www.techrxiv.org/)
