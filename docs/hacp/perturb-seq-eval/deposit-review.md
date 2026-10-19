# perturb-seq-eval (bioFM) — v0.6.0 deposit: review and decision

<!-- HACP subproject page · Project=bioFM · L1 — Review/Decision · local source. Written 2026-10-16
     by the perturb-seq-eval worktree agent on the principal's direction ("provide on HACP review
     surface"). The Notion mirror is a CTO write. Edit here, never in Notion. -->

| | |
|---|---|
| **Question** | How v0.6.0 enters the public record without **duplicate research** (principal, 2026-10-16) |
| **Verdict asked of you** | Pick **A** or **B** below. **Recommended: B** — revise the existing records; discard the two unpublished v0.6.0 drafts |
| **State now** | Nothing published. Two **unpublished** v0.6.0 drafts exist; both v0.5.x records are untouched (confirmed by you and by read-only GETs) |

## What exists today

| Venue | Record | State | Notes |
|---|---|---|---|
| Zenodo | concept `10.5281/zenodo.19716140` → latest **v0.5.2** `20074427` (2026-05-07) | published | chain: v1 19716141 · v0.5.0 19748260 · v0.5.1 20060974 · v0.5.2 20074427 |
| Figshare | article `10.6084/m9.figshare.32086920`, **version 5** | public | [record page](https://figshare.com/articles/preprint/Agent_Confidence_Entropy_as_an_Empirical_Difficulty_Oracle_for_Multi-Agent_Group_Generation_with_a_Bayesian_Pre-Test_for_Agentic_Hyperparameter_Tuning_on_Perturb-Seq_Experimental_Design/32086920); its paper.pdf is md5-identical to Zenodo v0.5.2's |
| Zenodo | **draft** `23411021` (DOI 10.5281/zenodo.23411021 reserved, not registered) | unsubmitted | v0.6.0 as a *new standalone* record (ruling #620) |
| Figshare | **draft** `34562538` (DOI 10.6084/m9.figshare.34562538 reserved) | private | v0.6.0 as a *new* article; one author (profile name, still "Mangyin Mo") |

The standing ruling (#620, 2026-10-15) was **new standalone records** on both venues. Published as such, v0.6.0 would sit beside v0.5.x as a second record of the same study — the duplicate you want to avoid.

## The two options you named

### A — fully delete the previous records, publish v0.6.0 as the only record
- **Not achievable as "fully".** Zenodo lets an owner delete a record only within 30 days of publication; ours are from April–May 2026, so deletion needs a justified support request, and a **tombstone page with the DOI remains** ([Zenodo: manage records](https://help.zenodo.org/docs/deposit/manage-records); [Zenodo FAQ](https://support.zenodo.org/help/en-gb/1-upload-deposit/215-can-i-delete-my-record-after-publishing)). Figshare personal accounts **cannot unpublish**; it takes a support take-down ticket and also leaves a tombstone ([Figshare: unpublishing items](https://support.figshare.com/support/solutions/articles/6000225217-unpublishing-items)).
- Removes citable records that others may already reference (DOIs on the paper's own corrections appendix point at the v0.5.0 record).
- Depends on two support teams' discretion and timing.

### B — remove the current drafts, supersede the existing records with a new revision **(recommended)**
- **Zenodo:** discard draft `23411021`; create a **new version** from v0.5.2 `20074427` under the same concept DOI, replace its files with the v0.6.0 set, set the v0.6.0 metadata, publish → the concept DOI resolves to v0.6.0; v0.5.x stays reachable as earlier versions.
- **Figshare:** discard draft `34562538`; edit article `32086920` (title, description, files replaced by the v0.6.0 set), publish → **version 6** of the same article; versions 1–5 stay reachable. Figshare itself advises a new version rather than unpublishing.
- One record per venue, one version chain, no duplicate, nothing deleted that anyone cites.

## What B changes in the repository (before any write)
1. **Reverses ruling #620** (standalone records) — your call; the CTO to record it.
2. **Code:** the submitter refuses published records today (`PublishedRecordError`, `SUPERSEDED_RECORDS`). B needs a gated, explicit *revision* path: Zenodo `newversion` from the latest version + file replacement; Figshare metadata update + file replacement on `32086920`. The two-go rule stays: a dry run prepares the new version **unpublished** (on Figshare the public v5 stays visible until publish), a separate go publishes. The submitter's earlier finding — Figshare sends metadata only on create — is handled by this path explicitly.
3. **Discard both drafts** (deleting an *unpublished* Zenodo draft and a *private* Figshare article is permitted; their reserved DOIs were never registered).
4. Relations/notes revert to version-chain form (no "standalone record" note); `publish.state.v060.json` records the new-version ids.
5. Normal quality gate; then the payload comes back to you for the first write, and publication is a further separate go.

## Still owed regardless of A/B
- **Figshare profile rename** to exactly `Mang-yin Mo` — the publish run refuses any other author (`expected_author`).
- Fresh read-only GET of the v0.5.x records immediately before any publish.

## Decision

| # | Decision | Options | Recommended |
|---|---|---|---|
| D-1 | How v0.6.0 avoids duplicating v0.5.x | **A** delete previous (support requests, tombstones remain) · **B** new revision of the existing records, drafts discarded | **B** |
