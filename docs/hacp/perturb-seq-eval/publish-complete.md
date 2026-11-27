# perturb-seq-eval (bioFM) — publication: completion review (latest published: 0.6.3)

<!-- HACP subproject page · Project=bioFM · L1 — Review (completion) · local source. Written 2026-10-16
     by the perturb-seq-eval worktree agent on the principal's direction ("share the HACP completion
     review link (to zenodo)"). The Notion mirror is a CTO write. Edit here, never in Notion. -->

| | |
|---|---|
| **Outcome** | **0.6.3 published, 2026-11-25**, the latest of four next versions of the existing records on both venues (v0.6.0 on 2026-10-16, 0.6.1 on 2026-11-22, 0.6.2 and 0.6.3 on 2026-11-25) — no duplicate record |
| **Share this link** | **https://doi.org/10.5281/zenodo.19716140** — the concept DOI; it always resolves to the latest version (now 0.6.3) |
| **Decisions closed** | D-1 = B (revise, don't duplicate) · D-2 = publish |

## The records

| Venue | Record | DOI | Link |
|---|---|---|---|
| Zenodo | concept (always the latest) | `10.5281/zenodo.19716140` | https://doi.org/10.5281/zenodo.19716140 |
| Zenodo | **0.6.3** (version 9 under the concept) | `10.5281/zenodo.24519260` | https://zenodo.org/records/24519260 |
| Figshare | article 32086920, **version 9** (0.6.3) | `10.6084/m9.figshare.32086920.v9` | https://doi.org/10.6084/m9.figshare.32086920.v9 |
| Zenodo | 0.6.2 (version 8) | `10.5281/zenodo.24518637` | https://zenodo.org/records/24518637 |
| Figshare | article 32086920, version 8 (0.6.2) | `10.6084/m9.figshare.32086920.v8` | https://doi.org/10.6084/m9.figshare.32086920.v8 |
| Zenodo | 0.6.1 (version 7) | `10.5281/zenodo.24430429` | https://zenodo.org/records/24430429 |
| Figshare | article 32086920, version 7 (0.6.1) | `10.6084/m9.figshare.32086920.v7` | https://doi.org/10.6084/m9.figshare.32086920.v7 |
| Zenodo | v0.6.0 (version 6) | `10.5281/zenodo.23422745` | https://zenodo.org/records/23422745 |
| Figshare | article 32086920, version 6 (v0.6.0) | `10.6084/m9.figshare.32086920.v6` | https://doi.org/10.6084/m9.figshare.32086920.v6 |

0.6.1, 0.6.2 and 0.6.3 are manuscript revisions; the v0.6.0 run and every outcome are unchanged. Earlier versions stay reachable as the history of the same records: Zenodo v0.5.2 `20074427` (still published), Figshare version 5 (still listed with its 3 original files).

**Closed 2026-11-25:** the Zenodo 0.6.1, 0.6.2 and 0.6.3 records carry `isIdenticalTo` their Figshare version DOIs (v7, v8, v9), as v0.6.0's record does, each added by a metadata-only edit with no file or other metadata changed (HACA-141; `CITATION.cff`, lineage comment).

## Verified after the v0.6.0 publish (public, unauthenticated read-back)

*The checks and the incident below are those of the v0.6.0 publish, 2026-10-16. The 0.6.1, 0.6.2 and 0.6.3 read-backs are recorded in `projects/perturb-seq-eval/CITATION.cff`.*

| Check | Result |
|---|---|
| Zenodo 23422745 | `published`, version 0.6.0, published 2026-10-16, creator `Mo, Mang-yin` |
| Zenodo concept latest | resolves to `23422745` |
| Zenodo relations | **isIdenticalTo `10.6084/m9.figshare.32086920.v6`** · isNewVersionOf `10.5281/zenodo.20074427` · isNewVersionOf `10.6084/m9.figshare.32086920.v5` · isSupplementedBy the repository at `ce5f237` |
| | *The `isIdenticalTo` relation was added by a metadata-only edit on 2026-10-25 and is CTO-verified live on the record (2026-10-29). **This row previously omitted it**, and it is the relation that matters most for discovery: it tells DataCite and downstream indexers that the Zenodo and Figshare deposits are ONE work rather than two papers.* |
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
> **Also applied 2026-10-25, and this paragraph was MISSING FROM THIS FILE while present on its own
> Notion mirror — recorded here 2026-10-29 to restore the declared direction of the mirror.** A
> metadata-only edit added `isIdenticalTo 10.6084/m9.figshare.32086920.v6` to the Zenodo v6 record,
> so the two deposits now cross-reference in both directions. Figshare was deliberately left
> untouched — republishing it would mint a v7 for a link that already exists. Applied and read back
> by the perturb-seq-eval agent (dispatch #734); DOI, version and all five file checksums unchanged,
> and no new Zenodo version was created. **The CTO holds no venue tokens and verified none of that
> edit** — but the resulting relation WAS independently confirmed live on the record by the CTO on
> 2026-10-29, which is why the Relations row above now names it.
>
> *The drift itself is worth keeping: this page's own header says "Edit
> `docs/hacp/perturb-seq-eval/publish-complete.md`, never this page", and yet the Notion side had
> carried a dated addendum its source never received. Same class as the ChipSim index finding — a
> Notion "mirror" can diverge from its source, and here it diverged in the direction that made the
> declared source the incomplete copy.*
>
> All three are the **principal's own actions**, reported in session 2026-10-25/26. The CTO holds no
> venue tokens and verified none of them. Recorded at perturb-seq-eval approvals row 9.

### What was owed (original text, superseded above)

1. **OSF preprint `dhu4z_v1` / project `wmeuy`** — the only separate record of the v0.5 work. Recommended: *Edit → Create new version* with the v0.6.0 `paper.pdf` and a description line "Superseded by v0.6.0: https://doi.org/10.5281/zenodo.19716140". Alternatives: withdraw, or at least point project `wmeuy`'s description at the concept DOI.
2. **ORCID** — in *Works*, set the v0.6.0 / concept-DOI entry as **preferred** in its group; hide older stand-alone entries.
3. **Google Scholar** — if v0.5 and v0.6 appear as two articles, select both → *Merge*.

## Repository

`projects/perturb-seq-eval/CITATION.cff` names 0.6.3 as the latest published release (`version: "0.6.3"`, `date-released: 2026-11-25`) and lists the DOIs of every published version. The published state of each release is recorded in its own state file: `publish.state.v060.json` (v0.6.0), `publish.state.v061.json` (0.6.1), `publish.state.v062.json` (0.6.2) and `publish.state.v063.json` (0.6.3, still the `state_file` in `publish.yml`).
