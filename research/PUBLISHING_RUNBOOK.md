# Publishing Runbook — From Green Build to DOIs

> Operator-facing runbook. Pairs with:
>
> - [`PUBLISHING_VENUES.md`](PUBLISHING_VENUES.md) — per-venue API reference
> - [`projects/perturb-seq-eval/publish.yml`](../projects/perturb-seq-eval/publish.yml) — single metadata source
> - [`projects/perturb-seq-eval/scripts/publish/submit_to_venues.py`](../projects/perturb-seq-eval/scripts/publish/submit_to_venues.py) — scripted orchestrator
> - [`projects/perturb-seq-eval/docs/SUPPLEMENT.md`](../projects/perturb-seq-eval/docs/SUPPLEMENT.md) — the supplement being released
>
> Follow this end-to-end and you will land three DOIs (Zenodo / Figshare /
> OSF-BioHackrXiv) in under 15 minutes wall time, plus a human-driven
> bioRxiv / arXiv queue for community reach. Human steps and automatable
> steps are tagged 👤 and 🤖.

## 0. Pre-flight coherence checklist (run before anything else)

Before you touch tokens or a submit button, confirm the four deliverables
are **internally consistent**. A preprint's headline abstract, PDF body,
supplement document, and raw artefacts must agree. If they don't, fix
the divergence first — it is much cheaper than withdrawing a DOI.

- [ ] 👤 **Revision pass landed.** Every P0 item in
      [`docs/INTERNAL_FOLLOWUP.md`](../projects/perturb-seq-eval/docs/INTERNAL_FOLLOWUP.md)
      §2 shows ☑. If any P0 still shows ⬜ or 🔄, stop and close it first.
- [ ] 👤 **Abstract matches SUPPLEMENT conclusion.**
      Open `publish.yml` and
      [`docs/SUPPLEMENT.md`](../projects/perturb-seq-eval/docs/SUPPLEMENT.md)
      §7 side by side. The `description:` field in `publish.yml` must
      quote the same qualitative claims (CIs overlap / non-overlap, γ_T
      numbers, backbone-axis observation) that §7 defends. If numbers
      differ by more than rounding, fix `publish.yml` or re-run the
      revision analysis.
- [ ] 👤 **Paper PDF and SUPPLEMENT do not contradict each other.**
      - `paper/paper.pdf` is the synthetic-DGP peer-review-style manuscript.
      - `docs/SUPPLEMENT.md` is the Adamson + revision-pass companion.
      They are allowed to cover different scopes, but any claim that
      appears in both must agree (e.g. metric definitions, drop rules,
      config space). If `paper.pdf` quotes a number that has since been
      retracted, regenerate it (§6.4 of this runbook).
- [ ] 👤 **Figures are the Wong-palette + CI-banded versions.** Spot-check
      `artifacts/modal_run/figures/fig{2,3,4}_*.png`: trajectory lines
      should show shaded CI bands. Pre-revision versions without bands
      still exist on disk under other timestamps — do **not** ship those.
- [ ] 👤 **References list is complete.** Every method cited in
      `SUPPLEMENT.md` body (Krause & Ong 2011, Krause-Singh-Guestrin 2008,
      Snell 2024, Archon/Saad-Falcon 2024, Hansen CMA-ES 2016, Rechenberg
      one-fifth-success, CPA/Lotfollahi 2023, GEARS/Roohani 2024,
      scGPT/Cui 2024, Adamson 2016) must be in the **References** section
      of `SUPPLEMENT.md` and in `paper/references.bib` (for the LaTeX).
      If a citation is used only in `SUPPLEMENT.md`, that's fine — the
      supplement has its own References block.
- [ ] 👤 **No retracted claims anywhere.** Grep the candidate bundle for
      the three retracted claim patterns:

      ```bash
      cd projects/perturb-seq-eval
      grep -rn "5/7\|5 / 7\|scgpt_small wins" docs/ publish.yml
      grep -rn "2\.6 %\|2\.6%\|by 2\.6" docs/ publish.yml
      grep -rn "beats CMA-ES on real\|real-data routing" docs/ publish.yml
      ```

      Any match outside the **Deviation Log** or the **Reviewer
      Critique** doc is a bug — either remove it or prefix it with
      "previously claimed / retracted".
- [ ] 👤 **LaTeX placeholder scan (authorship + affiliation).** The
      §2.6 grep below covers Markdown / YAML; LaTeX `\author{}` needs
      its own scan because it doesn't use `Last, First` syntax:

      ```bash
      grep -rn "Anonymous\|\\\\anonymous\|{anonymous}\|YourName\|Syntropy Health" paper/ | grep -v ".aux\|.bbl\|.log"
      ```

      Empty output = clean. Any hit means `paper/paper.tex` still
      carries a template placeholder that will end up in the
      compiled PDF and propagate to every platform that hosts it.
      This class of defect escaped the initial audit on 2026-04-23
      (v0.4.0 → v0.4.1 authorship patch); the rule above exists
      so it doesn't happen again.
- [ ] 👤 **`publish.yml` file list covers every supplement asset** (see §2.5
      below). Missing docs/ or revision artifacts at submit time means
      reviewers get a broken bundle.

If any box stays unchecked, do not proceed to §1.

## 1. One-time setup — tokens

All three API-driven venues need personal access tokens. Minting each
token takes < 2 minutes.

### 1.1 Zenodo

1. 👤 Sign up at <https://zenodo.org/signup> (GitHub/ORCID SSO works).
2. 👤 Navigate to **Settings → Applications → Personal access tokens**.
3. 👤 Click **New token**. Name: `perturb-eval-publish`. **Scopes**: tick `deposit:write` **and** `deposit:actions`.
4. 👤 Copy the token (only shown once). Export as `ZENODO_TOKEN`.

Optional but recommended: toggle on the **GitHub ↔ Zenodo** integration
so future releases mint DOIs automatically. Go to **Settings → GitHub**,
flip the switch next to the repository.

### 1.2 Figshare

1. 👤 Sign up at <https://figshare.com>.
2. 👤 Click the **user icon → Applications → Personal tokens → Create Personal Token**.
3. 👤 Copy the token. Export as `FIGSHARE_TOKEN`.

### 1.3 OSF (for BioHackrXiv)

1. 👤 Sign up at <https://osf.io> (ORCID SSO works).
2. 👤 **Settings → Personal access tokens → Create token**. **Scope**: `osf.full_write`.
3. 👤 Copy the token. Export as `OSF_TOKEN`.

### 1.4 Where to put the three tokens

1. 👤 Copy the committed template to a local (gitignored) `.env` at the repo root:

   ```bash
   cp .env.example .env
   ```

2. 👤 Open `.env` and paste your tokens in, replacing `REPLACE_ME`:

   ```env
   ZENODO_TOKEN=...your-real-zenodo-token...
   FIGSHARE_TOKEN=...your-real-figshare-token...
   OSF_TOKEN=...your-real-osf-token...
   ```

   Leave tokens you don't have as `REPLACE_ME` — the script treats those
   as placeholders and skips only the matching venue.

3. That's it. The script auto-discovers `.env` by walking upward from
   your current working directory — no `source`, no `export`. The file
   is protected from being committed by the repo-level `.gitignore`
   (`.env` blocked; `!.env.example` allow-listed).

Alternative if you already use a secret manager (Infisical / Vault /
1Password): export the three variables in your shell before running
the script. The script consults `os.environ` first, so real env vars
override `.env` values.

## 2. One-time setup — publish.yml

The metadata file is [`projects/perturb-seq-eval/publish.yml`](../projects/perturb-seq-eval/publish.yml).
Edit the following fields **before** your first real run (everything
else has sensible defaults):

| Field | What to put |
|---|---|
| `creators[0].name` | your real `Last, First` |
| `creators[0].affiliation` | your institution |
| `creators[0].orcid` | real ORCID or remove the field |
| `venues.osf.subjects` | at least one real OSF subject taxonomy ID (query `https://api.osf.io/v2/subjects/?filter[provider]=biohackrxiv` to find the right one) |
| `files[*].path` | point at the real paths (defaults match the supplement run, so likely nothing to change) |

For the first run, flip `venues.zenodo.sandbox: true` if you want a test
DOI on `sandbox.zenodo.org` before committing to a production DOI.

## 2.5 Supplement bundle inventory 📦

Every venue receives the same **three-artefact bundle**. This is what
reviewers expect to find.

| Artefact | Source path (relative to `projects/perturb-seq-eval/`) | Content | Size today |
|---|---|---|---|
| 1. Manuscript PDF | `paper/paper.pdf` | Peer-review-style write-up of the synthetic-DGP experiments. Built from `paper/paper.tex` + `paper/references.bib`. | ~0.63 MB |
| 2. Supplement documentation | `docs/` (auto-zipped to `supplement.zip`) | [`SUPPLEMENT.md`](../projects/perturb-seq-eval/docs/SUPPLEMENT.md), [`SUPPLEMENT_DESIGN.md`](../projects/perturb-seq-eval/docs/SUPPLEMENT_DESIGN.md), [`REVIEWER_CRITIQUE.md`](../projects/perturb-seq-eval/docs/REVIEWER_CRITIQUE.md), [`THESIS.md`](../projects/perturb-seq-eval/docs/THESIS.md), [`DESIGN.md`](../projects/perturb-seq-eval/docs/DESIGN.md), [`MODAL.md`](../projects/perturb-seq-eval/docs/MODAL.md), [`PUBLICATION_CHECKLIST.md`](../projects/perturb-seq-eval/docs/PUBLICATION_CHECKLIST.md), [`INTERNAL_FOLLOWUP.md`](../projects/perturb-seq-eval/docs/INTERNAL_FOLLOWUP.md). | ~0.05 MB |
| 3. Reproducibility archive | `artifacts/modal_run/` (auto-zipped to `modal_run_artifacts.zip`) | Raw E1 / E2-synthetic / E2-Adamson / E3 / E3b JSON and JSONL under `results/`, the revision-pass bootstrap-CI and γ_T outputs under `revision/revision_stats.json`, plus `figures/fig{1..5}_*.{png,pdf,html}`. | ~7.3 MB |

Per-venue differences:

- **Zenodo** (DOI → `10.5281/zenodo.*`): all three artefacts uploaded to the same deposition; one DOI for the whole bundle.
- **Figshare** (DOI → `10.6084/m9.figshare.*`): all three uploaded to the same article; one DOI. Figshare's categorisation = `Preprint`.
- **OSF / BioHackrXiv** (DOI → `10.17605/OSF.IO/*`): `paper.pdf` goes as the *primary file*; the other two archives ride alongside on the same OSF node.

`publish.yml → files:` already encodes this mapping. If you add a new
artefact to the supplement, append it there and re-run §3 validate.

## 2.6 Coherence audit 🔍

Skim these five checks right after §2.5. Total time ~ 5 minutes.

1. **Numbers:** any MSD, CI, or γ_T quoted in `publish.yml` `description` matches `docs/SUPPLEMENT.md` §7 exactly. Grep the description for floats:

   ```bash
   grep -oE "[0-9]+\.[0-9]+" projects/perturb-seq-eval/publish.yml
   ```

   Every hit should map to a value in the SUPPLEMENT (§5.3, §5.4, §6.4).

2. **Figures:** every figure referenced by `docs/SUPPLEMENT.md` exists in `artifacts/modal_run/figures/`:

   ```bash
   grep -oE 'fig[1-5]_[a-z_]+' projects/perturb-seq-eval/docs/SUPPLEMENT.md | sort -u
   ls projects/perturb-seq-eval/artifacts/modal_run/figures/
   ```

   The two lists must match.

3. **References:** every first-author name mentioned in the SUPPLEMENT body appears in the References section at the bottom of the same doc:

   ```bash
   grep -oE '[A-Z][a-z]+ (&|and) [A-Z][a-z]+ [12][0-9]{3}' projects/perturb-seq-eval/docs/SUPPLEMENT.md
   ```

   Cross-check each hit against the References list in §References.

4. **Script / doc linkage:** the scripts referenced in `SUPPLEMENT.md` §9 (Deviation log) exist where the doc says they do:

   ```bash
   grep -oE 'scripts/[a-z_/]+\.py' projects/perturb-seq-eval/docs/SUPPLEMENT.md | sort -u | while read p; do
     test -f "projects/perturb-seq-eval/$p" || echo "MISSING: $p"
   done
   ```

   No `MISSING:` lines means linkage is intact.

5. **Retracted claims:** nothing in the outbound bundle quotes the retracted "5/7 wins" or "2.6 % edge" claims **outside** an explicit reframe / deviation-log / critique context. This grep pattern intentionally hits the reframes too — any match requires manual classification:

   ```bash
   grep -rnE "5/7|wins 5|\b2\.6 ?%" projects/perturb-seq-eval/publish.yml \
       projects/perturb-seq-eval/docs/ \
     | grep -vE 'REVIEWER_CRITIQUE|INTERNAL_FOLLOWUP|RELEASE_SOCIAL|Deviation|retract|previously|artefact of|would be statistically unsupported'
   ```

   Empty output = clean. Non-empty = read each hit and decide: is this prose standing behind a retracted claim, or is it describing why we retracted it?

If a check fails, fix the source (don't paper over in `publish.yml`) and
rerun.

## 3. Dry-run validation 🤖

```bash
cd projects/perturb-seq-eval
python scripts/publish/submit_to_venues.py validate
```

What this does (no network calls):

- Auto-loads `.env` (walks upward from cwd until found).
- Loads `publish.yml`.
- Zips any directory-typed `files[*]` into `.publish_work/*.zip`, computes sizes + md5s.
- Flags placeholder creator names and missing ORCIDs.
- Per venue: checks the token env var (`ZENODO_TOKEN`, `FIGSHARE_TOKEN`, `OSF_TOKEN`). **Placeholder values like `REPLACE_ME` count as missing.**
- Exits non-zero if anything is wrong.

A successful validate looks like:

```text
loaded env: /path/to/.env
✓ zenodo   enabled   ZENODO_TOKEN     set
✓ figshare enabled   FIGSHARE_TOKEN   set
✓ osf      enabled   OSF_TOKEN        set
```

A partial run (only Zenodo token present) looks like:

```text
✓ zenodo   enabled   ZENODO_TOKEN     set
✗ figshare enabled   FIGSHARE_TOKEN   placeholder/missing
    → will be skipped: fill FIGSHARE_TOKEN in .env or set `enabled: false` in publish.yml
✗ osf      enabled   OSF_TOKEN        placeholder/missing
    → will be skipped: fill OSF_TOKEN in .env or set `enabled: false` in publish.yml
```

The subsequent publish run **skips any venue with a missing token**
instead of aborting, so you can submit to Zenodo first and come back
for the others later.

## 4. Create drafts — `--dry-run` 🤖

```bash
cd projects/perturb-seq-eval
python scripts/publish/submit_to_venues.py all --dry-run
```

Expected output:

```text
[zenodo] DRY-RUN — deposit 12345678 left in draft state
[figshare] DRY-RUN — article 987654 left in draft
[osf] DRY-RUN — preprint abcde left unpublished
final state: { "zenodo": {...}, "figshare": {...}, "osf": {...} }
```

👤 **Inspect drafts** in each provider's web UI:

- Zenodo: <https://zenodo.org/deposit>
- Figshare: <https://figshare.com/account/articles>
- OSF: <https://osf.io/dashboard>

If something is wrong, fix `publish.yml` (or adjust in the web UI), then
rerun. The state file keeps deposition IDs so the script updates instead
of duplicating.

## 5. Commit — publish for real 🤖

```bash
python scripts/publish/submit_to_venues.py all
```

Expected:

```text
[zenodo] published: https://doi.org/10.5281/zenodo.XXXXXXX
[figshare] published: https://doi.org/10.6084/m9.figshare.XXXXXXX
[osf] published: https://osf.io/preprints/biohackrxiv/YYYYY
```

OSF's DOI is minted after publication; for BioHackrXiv it usually lands
in under an hour (often minutes).

The DOIs are recorded in `publish.state.json`. Commit that file so the
next run knows everything is already out the door.

## 6. Manual-only venues 👤

> **Evidence ledger for venues already submitted lives in
> [`research/PUBLICATION_EVIDENCE.md`](PUBLICATION_EVIDENCE.md) §0.**
> That file also carries the prioritised queue for the venues below,
> plus an explicit "venues I deliberately skip" list (ChemRxiv, medRxiv,
> TechRxiv, OpenReview, ResearchGate) with rationale.
>
> Submission priority: §6.1 bioRxiv → §6.2 Preprints.org → §6.3 arXiv
> (if endorsed) → §6.5 Research Square → §6.6 SSRN → §6.7 HAL. Stop
> whenever the audience is already covered.

These have no submission API. The script does **not** handle them. Run
§5 first so you have the Zenodo DOI in hand — manual venues want it as
"related content" on their upload forms.

### 6.1 bioRxiv (biology reach)

1. 👤 Open <https://submit.biorxiv.org>; register + sign in.
2. 👤 **New submission** → upload in this order:
   - **Main manuscript**: `paper/paper.pdf` (required).
   - **Source files**: zip of `paper/paper.tex` + `paper/references.bib` + `paper/figures/` + `paper/tables/` + `paper/sections/`. bioRxiv needs this for their production.
   - **Supplementary materials** (as separate uploads):
     - `artifacts/publish/supplement.zip` ← generated by the script; contains `docs/` tree
     - `artifacts/publish/modal_run_artifacts.zip` ← generated by the script; reproducibility archive
3. 👤 Populate the submission form **from `publish.yml`** (copy-paste, do not retype):
   - `title` → publish.yml `title`
   - abstract → publish.yml `description`
   - keywords → publish.yml `keywords`
   - authors → publish.yml `creators[*]`
4. 👤 Licence: **CC BY 4.0** (matches publish.yml).
5. 👤 In the **Data / related content** field, paste **all three DOIs** from `publish.state.json`: Zenodo (primary), Figshare, OSF.
6. 👤 Category: `Bioinformatics` (primary) + `Systems Biology` (secondary).
7. 👤 Submit. Screening 24–48 h (72 h over weekends).

bioRxiv occasionally bounces purely-computational work to arXiv. If
that happens, point them at the Zenodo DOI and note the paper contains
the Adamson 2016 pilot as a real-data experiment in §5.3 of the
supplement.

### 6.2 Preprints.org (multidisciplinary, 24 h SLA)

1. 👤 Register at <https://www.preprints.org>.
2. 👤 New preprint. Upload in order:
   - **PDF**: `paper/paper.pdf`.
   - **Supplementary**: `artifacts/publish/supplement.zip` + `artifacts/publish/modal_run_artifacts.zip`.
3. 👤 Metadata from `publish.yml` (title, abstract, keywords, authors).
4. 👤 Category: `Biology, Medicine & Life Sciences → Bioinformatics`.
5. 👤 Data availability: paste Zenodo DOI + GitHub repo link.
6. 👤 Submit. Screening within 24 h.

### 6.3 arXiv (only if endorsed)

1. 👤 Check whether any co-author already has arXiv endorsement in `cs.LG` or `q-bio.QM`: <https://arxiv.org/a/LASTNAME>.
2. 👤 If endorsed:
   - <https://arxiv.org/submit>.
   - **Primary category**: `cs.LG` (ML) with `q-bio.QM` as cross-list.
   - Upload: LaTeX source tarball from `paper/` (include `paper.tex`, `references.bib`, `figures/`, `sections/`, `tables/`). arXiv builds the PDF itself.
   - Abstract: paste `publish.yml` `description` verbatim.
   - **Comments field**: note the Zenodo DOI + "Supplement available at `<DOI-ZENODO>`" so reviewers know where the CIs + γ_T live.
   - No direct supplementary upload — arXiv does not support it. Point at Zenodo/OSF for anything beyond the LaTeX.
3. 👤 If not endorsed: email 2–3 established arXiv authors in `cs.LG` for endorsement, Zenodo DOI attached. See
   [`PUBLISHING_VENUES.md §3.9`](PUBLISHING_VENUES.md#39-arxiv--new-2026-endorsement-policy).

### 6.5 Research Square (Springer Nature "In Review") 👤

Best as a side-effect of submitting to a Springer-Nature journal — Research Square's expedited posting (48 h) is tied to an In Review enrollment on the journal side.

1. 👤 Open <https://www.researchsquare.com/submit>.
2. 👤 Upload `paper/paper.pdf`. Fill title + authors from `publish.yml`.
3. 👤 Pick *In Review* if you are also submitting to a SN journal; otherwise pick standalone (2–3 week SLA).
4. 👤 Link the Zenodo DOI as supplementary reference.

Skip if you are not submitting to a Springer-Nature journal — the standalone path is slow and duplicates reach we already have from Zenodo + bioRxiv.

### 6.6 SSRN (Elsevier) — CompSciRN / StatisticsRN 👤

Useful for econometric / statistical-methods crowd and for HPO / agentic ML researchers who track Elsevier networks.

1. 👤 Open <https://hq.ssrn.com/submission>.
2. 👤 Upload PDF + select networks: `CompSciRN` (methodology) + `StatisticsRN` (γ_T formalism). Optionally `EconomicsRN` if the BO framing is of interest there.
3. 👤 Moderation: 2–5 business days.
4. 👤 Cite Zenodo DOI in the abstract.

### 6.7 HAL (CNRS / France) 👤

European preprint reach; SWORD API exists but only for affiliated institutions. Carnegie Mellon is not HAL-affiliated, so use the individual web path.

1. 👤 Open <https://hal.science/deposit> and sign in with ORCID.
2. 👤 Upload `paper.pdf` + metadata (mirror `publish.yml`).
3. 👤 Pick domain: `Computer Science → Artificial Intelligence` cross-listed with `Life Sciences → Bioinformatics`.
4. 👤 Moderation: 1–3 business days.

Skip if no European co-author and no EU grant reporting need — Zenodo is already HAL-indexed via the OpenAIRE pipeline.

### 6.4 Regenerating `paper.pdf` when LaTeX drifts from the supplement 🔧

If the pre-flight coherence audit (§0, §2.6) flagged a mismatch between
`paper/paper.pdf` and `docs/SUPPLEMENT.md` — most likely because the
revision pass updated the supplement with bootstrap CIs / γ_T / probe
disclosure but the LaTeX body still carries pre-revision numbers — do
this **before** running the bundle upload:

1. 👤 Open `paper/paper.tex`. Locate any sentence that quotes a number
   from the E3/E3-Adamson/E3b experiments.
2. 👤 Replace each number with the post-revision equivalent from
   `artifacts/modal_run/revision/revision_stats.json` (final MSD means,
   95 % CIs, cumulative regret, γ_T). Add the CI width in square
   brackets next to every point estimate; this matches the SUPPLEMENT
   convention.
3. 👤 Retract any prose that claims:
   - "scgpt_small wins 5/7 tasks" → replace with "all three backbones
     are statistically indistinguishable per task within ±1 seed-SE on
     5/7 Adamson tasks".
   - "contextual GP beats CMA-ES by 2.6 % on Adamson" → replace with
     "contextual GP, one+λ-ES, and random are statistically
     indistinguishable on Adamson at n_tasks = 7, n_seeds = 20".
   - "routing on real Adamson data" → reframe as "routing on real-Adamson
     MSDs with simulated probe signatures" and cite MC3b as future work.
4. 👤 Rename any occurrence of `CMA-ES` that actually refers to our
   `(1+λ)-ES` implementation (mc7).
5. 👤 Rebuild:

   ```bash
   cd projects/perturb-seq-eval/paper
   pdflatex -interaction=nonstopmode paper.tex
   bibtex paper
   pdflatex -interaction=nonstopmode paper.tex
   pdflatex -interaction=nonstopmode paper.tex
   ```

6. 👤 Sanity-check: `grep -E "2\.6%|5/7|wins 5" paper.tex` should return
   no hits outside a "previously claimed / retracted" disclaimer.

Commit the updated `paper.tex` + `paper.pdf` before continuing to §5.

### 6.5 Updating an already-published paper 🔧🤖

Once a paper is live on any venue you may discover defects (see 2026-04-23
`paper.pdf` authorship patch; v0.4.0 → v0.4.1). The class of change
determines what's cheap to push and what forces a new DOI.

| Change class | Example | API-driven? | Creates a new DOI? |
|---|---|---|---|
| Text (body, references, figures inside PDF) | authorship fix, typo, new result | Zenodo ❌ / Figshare ✅ / OSF ✅ | **Zenodo yes** (concept DOI stable); Figshare no (internal versions); OSF no (file replace) |
| Bib-file hygiene (orphan removal only) | no visible change in compiled PDF | All ❌ — do not re-upload | — |
| Metadata (related-ID, subject, keyword) | add a cross-reference | All ✅ | No |

**Zenodo — create a new version** (the only flow that mints a new DOI):

```bash
set -a; source .env; set +a
python3 <<'PY'
import os, requests, datetime, json
t = os.environ['ZENODO_TOKEN']
h = {'Authorization': f'Bearer {t}'}
current_id = json.load(open('projects/perturb-seq-eval/publish.state.json'))['zenodo']['deposit_id']
base = f'https://zenodo.org/api/deposit/depositions/{current_id}'

# 1. Fork the current version → new draft with the metadata copied in.
r = requests.post(f'{base}/actions/newversion', headers=h, timeout=60); r.raise_for_status()
draft_url = r.json()['links']['latest_draft']
new_id = draft_url.rsplit('/',1)[-1]

# 2. Delete the stale file from the new draft's bucket, upload the replacement.
d = requests.get(draft_url, headers=h).json()
bucket = d['links']['bucket']
for f in d['files']:
    if f['filename'] == 'paper.pdf':
        requests.delete(f"{draft_url}/files/{f['id']}", headers=h)
with open('projects/perturb-seq-eval/paper/paper.pdf','rb') as fh:
    requests.put(f'{bucket}/paper.pdf', headers=h, data=fh.read())

# 3. publication_date is a required field on new versions.
meta = requests.get(draft_url, headers=h).json()['metadata']
meta['publication_date'] = datetime.date.today().isoformat()
requests.put(draft_url, headers={**h,'Content-Type':'application/json'},
             json={'metadata': meta})

# 4. Publish. Concept DOI 10.5281/zenodo.19716140 auto-redirects to the new
#    record; update publish.state.json.zenodo.deposit_id / doi.
out = requests.post(f'{draft_url}/actions/publish', headers=h).json()
print('new record DOI:', out['doi'], 'concept DOI:', out.get('conceptdoi'))
PY
```

**Figshare — replace file in place** (DOI unchanged):

```bash
python3 <<'PY'
import os, requests, hashlib
t = os.environ['FIGSHARE_TOKEN']
h = {'Authorization': f'token {t}'}
art = 'https://api.figshare.com/v2/account/articles/32086920'
pdf = open('projects/perturb-seq-eval/paper/paper.pdf','rb').read()
md5 = hashlib.md5(pdf).hexdigest(); size = len(pdf)

# 1. Find + delete the old paper.pdf.
cur = next(f for f in requests.get(art, headers=h).json()['files']
            if f['name']=='paper.pdf')
requests.delete(f"{art}/files/{cur['id']}", headers=h)

# 2. Upload replacement via register → chunked PUT → complete.
reg = requests.post(f'{art}/files',
                    headers={**h,'Content-Type':'application/json'},
                    json={'name':'paper.pdf','size':size,'md5':md5}).json()
fid = int(reg['location'].rsplit('/',1)[-1])
info = requests.get(f'{art}/files/{fid}', headers=h).json()
parts = requests.get(info['upload_url'], headers=h).json()['parts']
for p in parts:
    requests.put(f"{info['upload_url']}/{p['partNo']}",
                 data=pdf[p['startOffset']:p['endOffset']+1], headers=h)
requests.post(f'{art}/files/{fid}', headers=h)  # complete
PY
```

**OSF — delete + re-upload via Waterbutler**:

```bash
python3 <<'PY'
import os, requests
t = os.environ['OSF_TOKEN']; h = {'Authorization': f'Bearer {t}'}
proj = 'wmeuy'
files_api = 'https://files.osf.io/v1'
for f in requests.get(f'{files_api}/resources/{proj}/providers/osfstorage/', headers=h).json()['data']:
    if f['attributes']['name'] == 'paper.pdf':
        path = f['attributes']['path']
        requests.delete(f"{files_api}/resources/{proj}/providers/osfstorage{path}", headers=h)
requests.put(f'{files_api}/resources/{proj}/providers/osfstorage/?kind=file&name=paper.pdf',
             headers=h, data=open('projects/perturb-seq-eval/paper/paper.pdf','rb').read())
PY
```

#### Manual-only venue updates 👤

For every web-form venue there is **no replace-file API** — updates are
full resubmits. Use this matrix:

| Venue | Portal | How to update | Turnaround |
|---|---|---|---|
| **bioRxiv** | <https://submit.biorxiv.org> | Log in → find manuscript → **Submit revised manuscript** button → upload new PDF + source → new version attached to same DOI | 24–48 h re-screening |
| **arXiv** | <https://arxiv.org/submit> (via [your account](https://arxiv.org/user/)) | Manuscript page → **Replace** → upload new tarball → new version (v2, v3…) keeps arXiv ID, appends version | usually < 12 h |
| **Preprints.org** | <https://www.preprints.org/user> | Manuscript dashboard → **Submit revision** → upload + brief revision note → new version | ≤ 24 h |
| **Research Square** (via SN In Review) | <https://www.researchsquare.com> | Manuscript page → **Update preprint** → upload new PDF | 48 h |
| **SSRN** | <https://hq.ssrn.com/> | My Papers → select paper → **Edit My Paper** → **Replace Full Text** → upload | 2–5 d |
| **HAL** | <https://hal.science> | User dashboard → deposit → **Add a new version** | 1–3 d |

Rule of thumb: any body-text change propagates to every venue. A
metadata-only change (e.g. new related-ID, author correction) can
usually be made inline without a new version — check per-venue.

## 7. Post-publication 🤖

Once the three API DOIs land, Claude automates the rest. The minimum
required stitch-together:

- Create `CITATION.cff` at repo root (does not exist yet) with the three DOIs + Zenodo as the canonical identifier.
- Add `CHANGELOG.md` entry (`v0.3.0-supplement` + DOIs + date).
- Replace the four `<PLACEHOLDER>` tokens in [`research/RELEASE_SOCIAL.md`](RELEASE_SOCIAL.md) with the real DOIs before posting.
- Rewrite `docs/SUPPLEMENT.md` §8 artifact table with real DOIs (currently references the local `artifacts/modal_run/` tree; post-publication it should point at the Zenodo DOI).
- Open a PR against upstream MassGen citing the published supplement (see [`docs/PUBLICATION_CHECKLIST.md §4.1`](../projects/perturb-seq-eval/docs/PUBLICATION_CHECKLIST.md#41-preprint--massgen-contribution-immediate)).

Scripted next-step, paste into a fresh session:

```text
"read projects/perturb-seq-eval/publish.state.json. Update:
 (1) CITATION.cff at repo root with Zenodo / Figshare / OSF DOIs.
 (2) CHANGELOG.md at repo root with a v0.3.0-supplement entry.
 (3) research/RELEASE_SOCIAL.md <PLACEHOLDER>s with the real DOIs.
 (4) projects/perturb-seq-eval/docs/SUPPLEMENT.md §8 artifacts table.
Then stage a single PR with those four files touched."
```

## 8. Resume / recovery

The state file is idempotent. If the script is interrupted between
venues, rerunning with the same `publish.state.json` in place picks up
where it left off — existing deposition IDs are reused.

| Failure mode | What the script does on retry |
|---|---|
| Network blip mid-upload | Re-uploads missing files; deposition IDs preserved |
| `FIGSHARE_TOKEN` expires | Mint new, re-export, rerun — article ID preserved |
| Zenodo metadata validation error | Fix `publish.yml`, rerun; metadata PUT is idempotent |
| Production vs sandbox mix-up | Flip `sandbox:` flag; clear only the `zenodo` section of `publish.state.json` |

Delete the state file entirely only for a genuinely fresh start.

## 9. What Claude needs from you to run this unattended

Copy-paste prompt for a fresh session:

> "Tokens are in `.env` at repo root. `publish.yml` creators/ORCID/subjects are filled in. Walk through `research/PUBLISHING_RUNBOOK.md` §0 pre-flight and §2.6 coherence audit; report any failure instead of proceeding. If all green, run `projects/perturb-seq-eval/scripts/publish/submit_to_venues.py validate`, then `--dry-run`, then `all`. Then execute the §7 post-publication scripted next-step."

That's the whole prompt. No MCP needed; the script runs via plain HTTP.

Manual venues (bioRxiv / Preprints.org / arXiv) are flagged 👤 in §6 —
Claude will not attempt them without an explicit browser-automation
session. The runbook hands you the exact file list + field mappings so
the manual submissions take < 10 minutes each.

## 10. Reference — what the script calls

Every request the script makes is documented per venue in
[`PUBLISHING_VENUES.md`](PUBLISHING_VENUES.md):

- Zenodo — [§3.1](PUBLISHING_VENUES.md#31-zenodo--primary-recommendation)
- Figshare — [§3.2](PUBLISHING_VENUES.md#32-figshare)
- OSF / BioHackrXiv — [§3.3](PUBLISHING_VENUES.md#33-osf-preprints-metaarxiv-psyarxiv-socarxiv-biohackrxiv-)

Read those sections if you need to debug a 400 or add a new venue.

## 11. Budget

Zero cost. All three API venues are free for the upload volumes
relevant here (< 25 GB). No Modal spend either — this runs locally.

---

*Last updated: 2026-04-22. Maintained at repo-root `research/` because it
is a cross-project concern.*
