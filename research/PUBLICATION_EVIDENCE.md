# Publication Evidence & Manual-Submission Queue

> Single-source-of-truth record of every venue the **perturb-seq-eval
> v0.4.0** manuscript has landed on, plus a prioritised queue of venues
> still to publish manually.
>
> Maintained at repo root `research/` level so this evidence survives
> project-level reorganisation. Last updated: 2026-04-23.

## 0. Quick evidence table

| Venue | Status | Permanent ID | Live URL | Date |
|---|---|---|---|---|
| **Zenodo concept DOI** (recommended for citation) | ✅ resolves to latest | DOI `10.5281/zenodo.19716140` | <https://doi.org/10.5281/zenodo.19716140> | 2026-04-23 |
| **Zenodo v2** (current paper.pdf with Mangyin Mo / CMU authorship) | ✅ published | DOI `10.5281/zenodo.19721470` | <https://zenodo.org/records/19721470> | 2026-04-23 |
| **Zenodo v1** (superseded, anonymous-author placeholder) | ⚠ retained for provenance | DOI `10.5281/zenodo.19716141` | <https://zenodo.org/records/19716141> | 2026-04-23 |
| **Figshare** | ✅ published | DOI `10.6084/m9.figshare.32086920` | <https://doi.org/10.6084/m9.figshare.32086920> · [figshare article](https://figshare.com/articles/preprint/Agent_Confidence_Entropy_as_an_Empirical_Difficulty_Oracle_for_Multi-Agent_Group_Generation_with_a_Bayesian_Pre-Test_for_Agentic_Hyperparameter_Tuning_on_Perturb-Seq_Experimental_Design/32086920) | 2026-04-23 |
| **OSF BioHackrXiv** | ⏸ draft on OSF (unpublished) | project `wmeuy` · preprint `dhu4z_v1` | <https://osf.io/wmeuy/> · <https://osf.io/preprints/biohackrxiv/dhu4z_v1/> | 2026-04-23 (created) |

Two DOIs live, one OSF draft pending.

### Post-publish remediation (2026-04-23 evening)

A late pass after initial publication caught two defects. Both fixed:

| Issue | Found in | Root cause | Fix |
|---|---|---|---|
| 10 Figshare files (4× paper.pdf + 3× supplement.zip + 3× modal_run_artifacts.zip) | Figshare DOI record | `submit_to_venues.py` Figshare submitter re-uploaded on every `all` / `--dry-run` invocation; Figshare's `/files` GET paginates at 10 so the problem was invisible locally. | Deleted 10 duplicates via `DELETE /v2/account/articles/{id}/files/{file_id}`. Iterated until stable (final count: 3 files). Patched the submitter to query current files and skip by MD5 match before upload. |
| Placeholder URL `https://github.com/REPO/PATH` in Zenodo `related_identifiers` | Zenodo record 19716141 | `publish.yml` template shipped with a placeholder URL never swapped for the real one. | Replaced with `https://github.com/mm-bconscious/bioFM` + added cross-reference `10.6084/m9.figshare.32086920` (scheme: doi, relation: isIdenticalTo). Re-submitted via `/actions/edit` → `PUT metadata` → `/actions/publish`. |

### Authorship patch (2026-04-23 late)

A third defect was found after the dedup / related-URL fix: the
compiled `paper/paper.pdf` carried the template's **Anonymous Authors,
Syntropy Health, `{anonymous}@syntropyhealth.bio`** placeholder in the
`\author{}` block. None of the coherence greps had hit it because the
grep patterns targeted tokens in Markdown / YAML, not LaTeX source.

Fix:

1. `paper/paper.tex` `\author{}` now reads `Mangyin Mo`, `Carnegie Mellon University`, `mangyinm@alumni.cmu.edu`, `ORCID 0009-0009-5233-3142`.
2. `paper.pdf` recompiled (12 pages, 635 940 bytes, md5 `e8eec5ba0a65531842fa14168b41b6b8`).
3. **Zenodo**: created a new version (v2) via `/actions/newversion`; deleted the stale paper.pdf from the draft; uploaded the corrected PDF; added `publication_date` (required field); republished. New record DOI `10.5281/zenodo.19721470`. The **concept DOI** `10.5281/zenodo.19716140` is the canonical citation target — it always resolves to the latest version.
4. **Figshare** (article 32086920, same DOI): deleted the stale paper.pdf via `/files/{id}`; uploaded the new one via the register → chunked-PUT → complete flow. DOI is unchanged; the article is versioned internally by Figshare.
5. **OSF** (project `wmeuy`): deleted old paper.pdf via Waterbutler; uploaded the new one. The unpublished preprint `dhu4z_v1` references the project, so the corrected file will be what appears once OSF's subjects endpoint lets the preprint complete.
6. Infisical: added `AUTHOR_EMAIL = mangyinm@alumni.cmu.edu` under `/research/perturb-seq-eval` in the GTM project.

Root cause of the placeholder escape: the §2.6 coherence audit grep patterns were tuned for Markdown / YAML (`"Last, First"`, `REPO/PATH`, `0000-0000`, etc.) but did not scan LaTeX `\author{}`. Added follow-on grep: `grep -rn "Anonymous\|\\\\anonymous\|Syntropy Health" paper/` to the pre-flight checklist so this class of defect is caught next time.

Bi-directional cross-references now live on both platforms:

- Zenodo → GitHub (`isSupplementTo`) + Figshare DOI (`isIdenticalTo`).
- Figshare → Zenodo DOI + GitHub URL (in `references` field).

Audit script for next time:

```bash
set -a; source .env; set +a
# Figshare dedup scan (uses article endpoint — not paginated)
curl -sS "https://api.figshare.com/v2/account/articles/32086920" \
  -H "Authorization: token $FIGSHARE_TOKEN" \
  | jq '[.files[] | .name] | group_by(.) | map({name: .[0], count: length}) | map(select(.count > 1))'

# Zenodo placeholder scan
curl -sS "https://zenodo.org/api/deposit/depositions/19716141" \
  -H "Authorization: Bearer $ZENODO_TOKEN" \
  | jq '.metadata.related_identifiers' | grep -i "REPO/PATH\|YOUR_\|0000-0000"
```

Empty jq output = clean.

### OSF state detail

At publish time (2026-04-23) OSF's preprint backend returned HTTP 502 on
the subjects-relationship PATCH endpoint, and the primary-file-
relationship endpoint 404'd on our Waterbutler-path GUID format. We
therefore:

1. Created the OSF project `wmeuy` ([osf.io/wmeuy](https://osf.io/wmeuy/)) and uploaded paper.pdf, supplement.zip, and modal_run_artifacts.zip to it — **all three files are publicly visible on the project page.**
2. Created an **unpublished** preprint record `dhu4z_v1` whose metadata (title + abstract + tags) is live but which is marked `is_preprint_orphan: true` because we couldn't attach a primary_file or subjects.

### Resume path when OSF recovers

```bash
cd projects/perturb-seq-eval
# Flip enabled back on
sed -i 's/enabled: false/enabled: true/' publish.yml
# Resume — state file has project_id, primary_file_id, preprint_id
python3 scripts/publish/submit_to_venues.py osf
```

The script will skip every already-done step and attempt only the two
PATCHes (subjects + primary_file) + the final `is_published: true`.

## 1. Manual-publication queue — prioritised

API-free venues, in the order I would attack them next. The paper PDF
lives at `projects/perturb-seq-eval/paper/paper.pdf`; the supplement is
`projects/perturb-seq-eval/docs/SUPPLEMENT.md`. Both Zenodo + Figshare
DOIs should be cited as **related content** when submitting to each of
these.

### P0 — do this week

1. **bioRxiv** — biology-community preprint reach.
   - Portal: <https://submit.biorxiv.org>
   - Turnaround: 24–48 h (72 h weekends).
   - Required: LaTeX source + compiled PDF, CC-BY-4.0 licence, institutional affiliation (Carnegie Mellon University).
   - Link Zenodo DOI in "Related content".
   - Watch-out: bioRxiv occasionally rejects purely-computational work and re-routes to arXiv. Have an arXiv endorsement ready as fallback (P1 below).

2. **Preprints.org (MDPI)** — multidisciplinary preprint, free DOI.
   - Portal: <https://www.preprints.org/submit>
   - Turnaround: within 24 h per SLA.
   - Category: `Biology, Medicine & Life Sciences → Bioinformatics`.
   - Copy the same abstract from `publish.yml`; Zenodo DOI in data-availability.

### P1 — by end of week, needs arXiv endorsement

3. **arXiv** — ML-community preprint reach (only useful if endorsed).
   - Portal: <https://arxiv.org/submit>
   - Turnaround: days if endorsed, weeks if requesting endorsement.
   - Endorsement: see 2026-01-21 policy update in [`PUBLISHING_VENUES.md §3.9`](PUBLISHING_VENUES.md#39-arxiv--new-2026-endorsement-policy). Two paths:
     - **Institutional**: Carnegie Mellon affiliation + prior arXiv authorship in `cs.LG` or `q-bio.QM`. Most CMU researchers already have endorsement — ask a local ML colleague.
     - **Personal**: email 2–3 arXiv authors in `cs.LG` / `q-bio.QM` with the Zenodo DOI, request endorsement. 1–7 day turnaround.
   - Primary category: `cs.LG` (Machine Learning). Cross-list: `q-bio.QM` (Quantitative Methods).

### P2 — opportunistic

4. **Research Square (Springer Nature "In Review")** — best paired with a Springer-Nature journal submission (e.g. *Nature Methods*, *Nature Machine Intelligence*).
   - Portal: <https://www.researchsquare.com/submit>
   - Turnaround: 48 h expedited (when linked to a Springer-Nature journal submission).
   - Skip standalone submission if you are not submitting to a SN journal.

5. **SSRN CompSciRN / EconomicsRN** — Elsevier network; gives econometric + CS crowd exposure.
   - Portal: <https://hq.ssrn.com/submission>
   - Turnaround: 2–5 d moderation.
   - Network: CompSciRN for methodology, StatisticsRN for γ_T formalism.

6. **HAL (CNRS / France)** — EU preprint archive; SWORD API exists for institutional deposit.
   - Portal: <https://hal.science/deposit> (individual) or institutional SWORD endpoint (if Carnegie Mellon has one — likely not; skip).
   - Turnaround: 1–3 d moderation.
   - Useful if you have a European co-author or want HAL-indexed for EU grant citations.

### P3 — community contributions (not preprints but related exposure)

7. **MassGen upstream skill PR** — land the `cellforge-eval` skill manifest + handlers into [`tools/MassGen/`](../tools/MassGen/). Draft exists at [`projects/perturb-seq-eval/massgen_skill_draft/`](../projects/perturb-seq-eval/massgen_skill_draft/). Opens a `gh pr create` path.
8. **CellForge upstream hook** — PR against [`projects/cellforge-agents/`](../projects/cellforge-agents/) adding the `cellforge preflight` CLI entrypoint that wraps our recommender. The hook is already wired in `src/perturb_eval/instrumentation.py`; it just needs to be exposed as a CellForge subcommand.
9. **BioRxiv → Semantic Scholar indexing** — automatic; will appear within ~1 week of bioRxiv acceptance.

### Venues I deliberately skip

| Venue | Why skip |
|---|---|
| ChemRxiv | Chemistry-only — paper is out of scope. |
| medRxiv | Clinical/medical only; this is computational methods with no patient data. |
| TechRxiv (IEEE) | Platform migration freeze as of 2026-03 — submissions temporarily closed. |
| OpenReview | Venue-gated (ICLR / NeurIPS / workshops); resubmit only when a specific CFP opens. |
| ResearchGate | Not a preprint archive — auto-indexes from other sources anyway. |

## 2. Social announcement

Once any of the above go live, paste the URL into the `<DOI-ZENODO>` /
`<DOI-FIGSHARE>` / `<OSF-URL>` placeholders in
[`research/RELEASE_SOCIAL.md`](RELEASE_SOCIAL.md) and post in the
cadence spelled out in §9 of that document.

## 3. Provenance

| Fact | Source |
|---|---|
| Zenodo API trace | `publish.state.json` at repo root + `scripts/publish/submit_to_venues.py` |
| Figshare API trace | same |
| OSF API trace (partial success) | same — `project_id=wmeuy`, `preprint_id=dhu4z_v1` |
| Author, ORCID, affiliation | Infisical `SyntropyHealth GTM` → `/research/perturb-seq-eval` (dev env) |
| Token storage | Infisical `SyntropyHealth GTM` → `/research/perturb-seq-eval` (dev env) |
| Build version | `CITATION.cff` v0.4.0, tag `v0.4.0-lifecycle`, commit `ba5923c` |
