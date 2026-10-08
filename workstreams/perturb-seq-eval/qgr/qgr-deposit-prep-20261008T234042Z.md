# Quality Gate Report — Iteration DEPOSIT-PREP (CTO #577; prep only, nothing submitted)

Scope: origin/main..HEAD (fbb02a7 substance; fixes a52dfe3 8978c78 b7850fe 1acee59), reviewed at ae58aef in a detached scratch worktree, tree-bracketed.
Reviewers: code 7, design 11, test 9, security 1 (+2 info); scorer: 25 scored, 11 passed (>= 80).
Hash A 5acba3d3a4f4889f2f663db9529bc329a0f7e51b45651ce61a7eeee07239e89a · Hash B 05b9dde04592b8abe42c85cc83da30383e04188710e5d70790f632213a712232 · Hash C 86c69d23a83de3f4b5d946bba3cb2332d85727e78be463579e7f4dd32aa1a43a

| ID | Conf | Finding | Fix |
|---|---|---|---|
| C-F6+D1 | 92 | Figshare submitter would add v0.6 files beside the v0.5 ones in the published article and republish with the old description/author | PublishedRecordError guard (a52dfe3) |
| D3 | 92 | CITATION version 0.5.1 / stale identifier notes next to the v0.6.0 abstract | version 0.6.0, notes corrected; date + new DOIs at deposit (b7850fe) |
| T1 | 88 | guard test reached live Zenodo API when the guard was removed | network stubbed; both venues (1acee59) |
| D4 | 88 | keywords "Bayesian optimization"/"contextual bandit" and reference notes not true of the work | keywords limited to terms in the manuscript, notes corrected, test (b7850fe, 1acee59) |
| D6 | 85 | supplement.zip (v0.5-era docs) unlabelled | labelled SUPERSEDED (b7850fe) |
| D2 | 84 | isNewVersionOf used the unversioned figshare DOI (resolves to the new record after deposit) | .v5 (b7850fe) |
| C-F2+D7 | 80 | pdf not proven built from landed sources; stale log | clean-tree check, HEAD recorded, stale files removed (8978c78) |
| C-F4 | 80 | guard error crashed the per-venue loop | caught and counted (a52dfe3) |
| C-F5+D8 | 80 | new-version procedure only in an error message; state "gitignored" comment wrong | deposit-time sequence in publish.yml; comment fixed (b7850fe) |
| T2 | 80 | first-deposit / resume paths untested | added (1acee59) |
| T3 | 80 | file paths not tied to the build step | tied + tectonic-missing test (1acee59) |

Not fixed, for decision: S1 — the run files carry llm_key_source (Infisical project slug, env); public already in the repo, permanent in a DOI. Principal/CTO: publish as provenance, or redact the staged copies (breaks byte-identity with the committed run).

Checks: pytest 1183 passed; ruff E9/F63/F7/F82 clean; format clean; render --check and fill --check match; tectonic build 0 overfull / 0 undefined (pre-fix build). Failing: 0.
