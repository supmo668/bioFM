# perturb-seq-eval (bioFM) — v0.6.0 publication: completion review

<!-- HACP subproject page · Project=bioFM · L1 — Review (completion) · local source. Written 2026-10-16
     by the perturb-seq-eval worktree agent on the principal's direction ("share the HACP completion
     review link (to zenodo)"). The Notion mirror is a CTO write. Edit here, never in Notion. -->

| | |
|---|---|
| **Outcome** | **v0.6.0 published, 2026-10-16**, as the next version of the existing records on both venues — no duplicate record |
| **Share this link** | **https://doi.org/10.5281/zenodo.19716140** — the concept DOI; it always resolves to the latest version (now v0.6.0) |
| **Decisions closed** | D-1 = B (revise, don't duplicate) · D-2 = publish |

## The records

| Venue | Record | DOI | Link |
|---|---|---|---|
| Zenodo | v0.6.0 (version 6 under the concept) | `10.5281/zenodo.23422745` | https://zenodo.org/records/23422745 |
| Zenodo | concept (always the latest) | `10.5281/zenodo.19716140` | https://doi.org/10.5281/zenodo.19716140 |
| Figshare | article 32086920, **version 6** | `10.6084/m9.figshare.32086920.v6` | https://doi.org/10.6084/m9.figshare.32086920.v6 |

Earlier versions stay reachable as the history of the same records: Zenodo v0.5.2 `20074427` (still published), Figshare version 5 (still listed with its 3 original files).

## Verified after publish (public, unauthenticated read-back)

| Check | Result |
|---|---|
| Zenodo 23422745 | `published`, version 0.6.0, published 2026-10-16, creator `Mo, Mang-yin` |
| Zenodo concept latest | resolves to `23422745` |
| Zenodo relations | isNewVersionOf `10.5281/zenodo.20074427` · isNewVersionOf `10.6084/m9.figshare.32086920.v5` · isSupplementedBy the repository at `ce5f237` |
| Figshare 32086920 | version 6, DOI `.v6`, published 2026-10-16T19:16:54Z, author `Mang-yin Mo` (one) |
| Files, both venues | identical set and md5: `paper.pdf` f137dab2… · `paper_build.log` 4019b884… · `v060_run_artifacts.zip` 5b41a919… · `supplement.zip` 52edb3d0… · `v050_run_artifacts.zip` f1c1fccc… |

## How it got here (one incident, handled by the gate)

- The last Figshare file sat at `ic_success` for ~82 min of 5-minute read-only polls; the publish run refused, as designed. Stopped and reported (CTO ruling #655).
- Principal chose the bounded re-upload (CTO-recommended, #657): the one wedged file was deleted **from the private draft only** and re-uploaded once. Public v5 was read before and after — unchanged. The new file reached `available` with md5 `5b41a919…` = the local build.
- Fresh pre-publish checks then passed; the permission classifier flagged the publish as a production deploy, and the principal allowed it.

## Profile clean-up — RESOLVED 2026-10-26 (all three closed)

> **This section is kept as written and marked resolved rather than deleted**, so a later reader sees
> what was owed as well as what was done.
>
> - **OSF — DISMISSED.** The preprint `dhu4z_v1` is an unsubmitted BioHackrXiv draft (no primary file,
>   no subjects, no DOI, `doi.org` 404) and project `wmeuy` is private, so **no public OSF record ever
>   existed** and there was no duplicate to supersede. The recommended "create new version" below was
>   therefore moot.
> - **ORCID — DONE** by the principal: DataCite link, combined with Figshare, Zenodo set preferred.
> - **Google Scholar — DONE** by the principal: manual entry, Journal = Zenodo, 2026/10/16.
>
> All three are the **principal's own actions**, reported in session 2026-10-25/26. The CTO holds no
> venue tokens and verified none of them. Recorded at perturb-seq-eval approvals row 9.

### What was owed (original text, superseded above)

1. **OSF preprint `dhu4z_v1` / project `wmeuy`** — the only separate record of the v0.5 work. Recommended: *Edit → Create new version* with the v0.6.0 `paper.pdf` and a description line "Superseded by v0.6.0: https://doi.org/10.5281/zenodo.19716140". Alternatives: withdraw, or at least point project `wmeuy`'s description at the concept DOI.
2. **ORCID** — in *Works*, set the v0.6.0 / concept-DOI entry as **preferred** in its group; hide older stand-alone entries.
3. **Google Scholar** — if v0.5 and v0.6 appear as two articles, select both → *Merge*.

## Repository

`CITATION.cff` now carries `date-released: 2026-10-16` and both new DOIs; the showcase's publication record and the decision log are updated; `publish.state.v060.json` records the published state.
