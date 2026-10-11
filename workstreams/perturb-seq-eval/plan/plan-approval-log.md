# Approval log — perturb-seq-eval

Append-only. One row per approval or dated amendment; the plan itself is signed in
`plan-approval.md` (`plan_hash` 418cc1e), which no row below re-signs.

| # | date | kind | route | hash | notes |
|---|------|------|-------|------|-------|
| 1 | 2026-10-08 | run-record amendment RR-1 | principal ruling, relayed by CTO #582 | plan 418cc1e unchanged; run manifest 323af965b631ce83 -> 70be925de94bfb37 | llm_key_source removed from 6 run files; details below |

## 2026-10-08 — RR-1: LLM key-storage record removed from the v0.6.0 run record

- **Ruling:** principal, 2026-10-08, relayed by the CTO in dispatch #582: "Remove it everywhere, amend the hash."
- **Removed:** `llm_key_source` (secret-store name, organisation project slug, environment name, home
  project, cross-project flag; no secret value), at top level and under `entrypoint_kwargs`, from
  `artifacts/v0.6.0/{provenance.json, trainer_runs.jsonl, lifecycle_runs.jsonl}` and the three run
  manifests in `configs/runs/` (the valid run plus the aborted and preflight-refused attempts). No other field
  changed; each file was re-serialised in its original format.
- **Why:** the field supports no claim: a key's storage location tells a referee nothing about
  validity. It named an organisation project, an environment and a cross-project key practice that a DOI
  would make permanently citable.
- **Not removed:** `llm_cache_dir` / `llm_cache_namespace` (`/biofm_cache/...`) are container paths
  naming the public repository's cache volume, not an organisation, environment or key practice.
- **Hashes:** the run manifest `configs/runs/20260929T035447Z-ce5f237.json` goes from SHA-256 prefix
  `323af965b631ce83` (superseded, as published in the run report and PR #8) to `70be925de94bfb37`.
  Every file's before/after SHA-256 is in `projects/perturb-seq-eval/paper/data/run_record_amendments.json`.
  The paper prints both prefixes (Results, run record; Reproducibility; corrections appendix).
- **Unchanged:** every result. The analyser, re-run on the amended run files, reproduces every committed
  value of `summary.json` (test `test_landed_analyser_reproduces_the_committed_summary`).
