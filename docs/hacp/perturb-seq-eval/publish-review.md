# perturb-seq-eval (bioFM) — v0.6.0 publication: review and decision

<!-- HACP subproject page · Project=bioFM · L1 — Review/Decision · local source. Written 2026-10-16
     by the perturb-seq-eval worktree agent on the principal's direction ("provide HACP review
     surface for 4"). The Notion mirror is a CTO write. Edit here, never in Notion. -->

| | |
|---|---|
| **Question** | Publish v0.6.0 as the next version of the existing Zenodo and Figshare records? |
| **Verdict asked of you** | **D-2: publish** (once the last Figshare file finishes processing) or **hold** |
| **State now** | Both revisions prepared and **unpublished**; v0.5.x untouched; no duplicate record anywhere (all read-only checks below, 2026-10-16) |

## What publishing does — and that it cannot be undone

| Venue | On publish | Afterwards |
|---|---|---|
| Zenodo | draft `23422745` becomes the **new version** under concept `10.5281/zenodo.19716140`; DOI `10.5281/zenodo.23422745` is registered | the concept DOI resolves to v0.6.0; v0.5.0–v0.5.2 stay reachable as earlier versions |
| Figshare | article `32086920` is published as **version 6**; DOI `10.6084/m9.figshare.32086920.v6` | the article page shows v0.6.0; versions 1–5 stay reachable |

A minted DOI is permanent. Zenodo allows owner deletion only within 30 days of publication (then a justified support request, tombstone retained); a Figshare personal account cannot unpublish. Everything below was checked so that the record is right the first time.

## The payload

| Field | Value |
|---|---|
| Title | Does Agent Confidence Entropy Predict Task Difficulty? A Pre-registered, Provenance-Complete Test of Agentic Hyperparameter Tuning for Perturb-seq Response Prediction |
| Version | 0.6.0 |
| Author | Zenodo `Mo, Mang-yin` (Family, Given) · Figshare `Mang-yin Mo` (your profile) — different forms **on purpose** |
| Licence · type | CC-BY-4.0 · preprint |
| Zenodo relations | isNewVersionOf `10.5281/zenodo.20074427` (v0.5.2) · isNewVersionOf `10.6084/m9.figshare.32086920.v5` · isSupplementedBy the repository at the run's commit `ce5f237` |
| Zenodo note | "v0.6.0 is the next version of this record (concept DOI 10.5281/zenodo.19716140): the pre-registered v0.6.0 study supersedes v0.5.x, whose versions remain available." |
| Figshare references | `https://doi.org/10.5281/zenodo.19716140` · the repository at `ce5f237` |

| File | md5 (identical on both venues and to the local build) |
|---|---|
| `paper.pdf` (built from `3635f9d`, 0 overfull / 0 undefined) | `f137dab214e85aa21606604cc29dae20` |
| `paper_build.log` | `4019b884bd77275564293c5b727957d8` |
| `v060_run_artifacts.zip` (the run + SHA256SUMS) | `5b41a91947966426611b99c20ea14311` |
| `supplement.zip` — labelled SUPERSEDED | `52edb3d08ad0157e373977c8ded96d48` |
| `v050_run_artifacts.zip` — labelled SUPERSEDED | `f1c1fccc1aa99eaa2d90d1c8f386adb8` |

## Pre-publish checks (read-only, run 2026-10-16)

| Check | Result |
|---|---|
| 1 · Figshare author is exactly `Mang-yin Mo` | **PASS** (draft and public view) |
| 2 · every Figshare file reads `available` | **PENDING** — 4/5 available; `v060_run_artifacts.zip` still `ic_success` (processing). The publish run **refuses** until it reads `available`; a background read-only poll is watching it |
| 3 · records being revised are untouched | **PASS** — Zenodo 20074427 published, same 3 files, still the latest in the concept; Figshare public view still v5 with its 3 original files |
| No duplicate anywhere | **PASS** — the two standalone drafts are deleted (404); your Figshare account holds only 32086920; your Zenodo account holds only draft 23422745 |
| Code that will act | gated: receipts `ae02b6b` (guards), `8795772` (availability gate); 1218 tests pass |

## Clean-up for your publication profile (things I cannot, or must not, delete)

Nothing on Zenodo or Figshare needs deleting: the two standalone drafts are gone (their reserved DOIs were never registered), and v0.5.x becomes *earlier versions of the same record*, which is how a version chain is meant to look — not a duplicate. What can still confuse a reader lives elsewhere:

1. **OSF preprint `dhu4z_v1` (project `wmeuy`, BioHackrXiv) — the one real source of confusion.** It is a separate record carrying the v0.5 work (ids from `publish.state.json`), and the deposit script is deliberately barred from touching it. *Its live state is unverified: the OSF API did not respond to read-only requests on 2026-10-16 — check it on osf.io.* If it is public, do one of these after v0.6.0 is published (logged in as the owner):
   - **Recommended — supersede it in place:** open the preprint → *Edit* → *Create new version* → upload the v0.6.0 `paper.pdf` and, in the description, add "Superseded by v0.6.0: https://doi.org/10.5281/zenodo.19716140". The old version stays reachable under the same preprint.
   - **Or withdraw it:** preprint page → *Withdraw* → reason "superseded by v0.6.0 at 10.5281/zenodo.19716140". Moderated; a withdrawal notice (tombstone) remains.
   - **At minimum:** edit project `wmeuy`'s description to point to the Zenodo concept DOI.
2. **ORCID** (if your record imports from DataCite): versions may appear as separate works. In *Works*, the entries that share an identifier are grouped — set the v0.6.0 / concept-DOI entry as **preferred**, and *hide* any older stand-alone entries.
3. **Google Scholar**: if v0.5 and v0.6 show as two articles, select both in your profile → *Merge*.
4. **Repository** (mine, after publish): set `CITATION.cff` `date-released` and the new DOIs, gated.

## Decision

| # | Decision | Options | Recommended |
|---|---|---|---|
| D-2 | Publish v0.6.0 as the next version on Zenodo and Figshare | **Publish** — I run both publish commands once check 2 passes (they refuse otherwise), verify by GET, then update `CITATION.cff` · **Hold** | **Publish** |
