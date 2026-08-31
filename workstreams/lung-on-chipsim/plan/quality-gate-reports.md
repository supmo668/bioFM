# Quality Gate Reports — lung-on-chipsim

> Kept OUT of `build-plan.md` deliberately. `tools/plan-gate` hash-locks the
> build plan to the human's approval signature (hash `737a8d9`, approved-by
> Matthew Mo). Appending QGRs to it changes that hash and BLOCKS the gate —
> verified: appending this report moved the hash to `abd3ef4` and
> `plan-gate verify` exited 2. Reports live here and the plan stays sealed.

## Quality Gate Reports

| Iteration | Scope | Findings | Result | Commit | Receipt |
|---|---|---|---|---|---|
| P0.1 | S1–S11 scaffold | 20 fixed · 2 rejected false · 1 deferred | ✅ 106 passed / 5 skipped | `cc10f7e` | `qgr/…-iteration-complete-20260831-1059-0653839.md` |

### P0.1 — S1–S11 scaffold (2026-08-31)

**Gate:** `pip install -e . && pytest --collect-only` exits 0 — **PASSED**.
Reviewers: code, security, design, test + own review. Threshold 80.

**All 11 scaffold tasks complete.** Two done-conditions were found to be
**untrue or unfalsifiable as stated** and were made real rather than signed off:

- **S1** — "exits non-zero if any `__init__.py` is removed" was **false**: PEP 420
  namespace packages import fine. A loader-agnostic guard on `PathFinder.find_spec`
  now makes it true (verified: normal import, removal, and zipimport).
- **S3** — "`pytest --collect-only` exits non-zero if `testpaths` is removed" is
  **not achievable via the CLI**: pytest's default `norecursedirs` skips `.venv`,
  so `tests/` is collected either way. Asserted against the parsed config instead.
  **Plan wording needs amending — E-2 below.**

**The gate's most consequential catch (F-01).** `data/raw/*` excluded the
`data/raw/drugbank/` *directory*, and git cannot re-include a file beneath an
excluded directory. This silently git-ignored **T1/T2's `provenance.yaml` and
`PROVENANCE.md`** and **T3/T4's `SHA256SUMS.json`**, making T4 done-condition (d)
unsatisfiable and leaving the plan's most load-bearing human artifacts
unversioned — defect 23 recurring at a different path. **S7's own two probes
passed against the broken form**, because both test only the *flat*
`data/raw/drugbank.dvc`. **E-4 below.**

**F-02.** `.dvc-storage/` was ignored nowhere. The DVC remote resolves there, so
after any `dvc push` it holds DrugBank-derived bytes as extensionless md5 blobs;
`git add -A` would vendor them. T11's planned `test_drugbank_not_vendored` matches
`*.tsv` and would not catch it. Now ignored at the repo root.

**Escalations to the CTO — plan defects, not code defects:**

| # | Issue |
|---|---|
| E-1 | T1/T11 say `provenance.yaml` has **eight** keys non-empty; T2+T1 define **nine**, and T2 requires `commit_change_rationale` to be **empty** when the commits match. Implemented as: nine present, eight always non-empty, rationale non-empty **iff** `source_commit != audited_commit`. **Needs ratification before T11 signs off.** |
| E-2 | S3's done-condition is unachievable as worded (see above). |
| E-3 | S4 prescribes the slice-3 skip reason for `test_monotonicity`, which is an **M1** ODE concern. Accurate reason used. |
| E-4 | S7's probe set is insufficient — it passes on a `.gitignore` that ignores the nested provenance/SHA256SUMS artifacts. Needs extending. |
| E-5 | The DVC remote resolves **inside the git worktree**, so `git worktree remove` destroys the only copy of the snapshot. Plan-specified location; flagged rather than deviated from. |

**Deferred with rationale (D-01).** `barrier_panel_ratified.yaml` carries **real**
UniProt accessions under `ratified: true`. It cannot be made synthetic: T19's
done-condition verifies each accession against the **live UniProt API**, and T9
must accept this fixture. Mitigated instead by a digest+banner copy-escape guard
that makes installing it as a real artifact fail.

**Rejected as false (2).** Two reviewer claims were independently checked and did
not hold: that the DVC remote deviates from the plan's path (it resolves exactly
where the plan intends), and that `env.yaml`'s relative path resolved elsewhere
than DVC's (same directory). The duplicated key was removed regardless.

**Human blockers — artifacts correctly ABSENT:** T2, T1, T8, T18, T14.
