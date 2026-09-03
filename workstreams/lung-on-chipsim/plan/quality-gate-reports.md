# Quality Gate Reports — lung-on-chipsim

> Kept OUT of `build-plan.md` deliberately. `tools/plan-gate` hash-locks the
> build plan to the human's approval signature (currently hash `b79a5e4` = r2.1,
> approved-by Matthew Mo; previously `737a8d9` = r2). Appending QGRs to it changes
> that hash and BLOCKS the gate — verified: appending a report moved the hash to
> `abd3ef4` and `plan-gate verify` exited 2. Reports live here and the plan stays
> sealed.
>
> **Standing rule (CTO directive, 2026-08-31):** the worktree agent does not amend
> `build-plan.md` on its own initiative. When a CTO ruling requires a plan
> amendment, make the change, say so in the next dispatch, and the CTO lands it on
> trunk and re-signs in the same move — so the signature always attaches to the
> plan actually being built.

## Quality Gate Reports

| Iteration | Scope | Findings | Result | Commit | Receipt |
|---|---|---|---|---|---|
| P0.1 | S1–S11 scaffold | 20 fixed · 2 rejected false · 1 deferred | ✅ 106 passed / 5 skipped | `cc10f7e` | `qgr/…-iteration-complete-20260831-1059-0653839.md` |
| P0.2 | T5–T19, S11a + E-1…E-5 | 27 fixed (15 correctness · 12 test-validity) · 1 accepted-as-is | ✅ 284 passed / 6 skipped · 15 network | `b18d097` | see below |

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

---

### P0.2 — T5–T19 + S11a against fixtures; CTO rulings E-1…E-5 (2026-08-31)

**Gate:** `ruff check` + `ruff format --check` clean; `pytest -m "not network"`
**284 passed / 6 skipped**; `pytest -m network` **15 passed / 1 skipped**.
Reviewers: code-correctness, test-quality (both mutation-driven), plus own review.

#### Rulings E-1…E-5 applied

| Ruling | Applied | Falsified? |
|---|---|---|
| E-1 | Conditional provenance contract in `contracts.py`; T11 signs off against fixtures | ✅ both directions asserted — a rationale for an unchanged commit fails too |
| E-2 | S3 asserts against the parsed config | ✅ (the CLI form is unachievable; recorded) |
| E-3 | `test_monotonicity` names the M1 ODE solver | ✅ each skip names its own blocker |
| E-4 | Nested probe set | ✅ re-introduced the r2 top-level-only `.gitignore` → 4 fail |
| E-5 | absolute external `url` (machine-specific; now in gitignored `.dvc/config.local`) + 2 guards | ✅ re-introduced `../../../.dvc-storage` → guards fail |

**E-5 verified empirically:** the store resolves inside **no git repository at all**
(`git -C … rev-parse` → `fatal: not a git repository`), beside the ISCP state files.
The F-02 belt-and-braces `.dvc-storage/` ignore rule is retained at the repo root.

**Note on E-4's own evidence:** under the broken top-level-only `.gitignore`, the
probe on `data/raw/drugbank.dvc` **still passed**. That is precisely the CTO's point
— a top-level probe does not test the rule.

#### The gate's most consequential catches

**F-03 (HIGH, data loss).** The never-clobber guard keyed on `adjudicated_label`
alone, but `HUMAN_OWNED_COLUMNS` has four. A row with `evidence_doi` and
`adjudicated_by` filled and the verdict still blank — **the exact state a reviewer
is in mid-session**, because DOIs get collected first and verdicts entered last —
was invisible to the guard and silently dropped. Reproduced: the row vanished with
no error. This is the 60–90 minutes of T14 the module exists to protect, and my own
adversarial probe missed it because I only tested with the verdict column filled.

**F-04 (CRITICAL, test validity).** The never-clobber *test* was satisfied by a
merge that **did nothing at all** (`if out.exists(): return len(existing)`). It was
driven by `labels` derived from the same fixture already on disk, so "preserved" and
"never written" were indistinguishable. Root cause was the fixture pair: columns 1–3
of `pgp_adjudication_partial.csv` and `..._filled.csv` are byte-identical.

**F-05 (CRITICAL).** T15 asserted only `set(series)` and a count, so reversing the
verdict column — every compound receiving a *different* compound's verdict — passed
the entire suite. Same defect class as r1's constant-`unknown` label: right
aggregate, wrong mapping.

**F-06 (CRITICAL).** `test_drugbank_not_vendored_catches_a_forced_tsv` re-declared
the allow-list inline and rebuilt the comprehension, so it exercised a Python list
comprehension and imported no production code. Widening the real allow-list to
permit `.tsv` left it passing. The rule now lives in
`drugbank_snapshot.vendored_offenders()` and both tests call it.

**F-07 (HIGH).** No golden InChIKey existed anywhere in `tests/`. `pyproject` pins
rdkit precisely because "an unpinned rdkit can silently repartition the splits while
every recorded sha256 and every test stays green" — which was a literally accurate
description of this suite: `canonical_inchikey` returning a constant passed.

#### Findings

| # | Sev | Finding | Disposition |
|---|---|---|---|
| F-03 | HIGH | Never-clobber guard keyed on one of four human columns | Fixed — guards on ANY human cell |
| F-08 | HIGH | Worksheet written in place; failed write destroyed merged human work | Fixed — staged + `os.replace` |
| F-09 | HIGH | Duplicate `canonical_inchikey` → contradictory verdicts on a non-unique index | Fixed — rejected on read and on the labels index |
| F-10 | HIGH | Empty panel join returned silently → everything `unknown` | Fixed — raises |
| F-11 | HIGH | `load_protein_edges` had no floor and only a subset category check | Fixed — floor + post-filter equality |
| F-12 | MED | Null/blank canonical keys dropped by `groupby`; empty frame → empty Series | Fixed |
| F-13 | MED | Header-only worksheet raised a bare `KeyError` | Fixed |
| F-14 | MED | Human-added columns discarded on regeneration | Fixed — carried through |
| F-15 | MED | `label_counts` silently projected away out-of-domain values and NaN | Fixed — raises |
| F-16 | MED | Empty-frame `apply` reported a nonexistent malformed structure | Fixed — early return |
| F-17 | LOW | Pre-adjudication domain guard was a bare `assert` (vanishes under `-O`) | Fixed — raises |
| F-18 | LOW | Sidecar stem collision undetectable | Fixed — verifies the recorded filename |
| F-19 | LOW | Roster validated stripped values but stored raw ones | Fixed |
| F-04…F-07 | CRIT/HIGH | Four tests satisfied by wrong implementations (above) | Fixed |
| F-20 | HIGH | 40-hex commit + attribution-count branches were dead code | Fixed — rejection tests added |
| F-21 | HIGH | `_split_list_cell`'s empty branch unreachable from the fixture | Fixed — DB90009 row + direct unit tests |
| F-22 | MED | Parquet round-trip normalized by its own reader; `snapshot_url` never checked per-file; atomicity assertion short-circuited; roster `name` untested | Fixed |

**Accepted as-is (1).** `fetch_snapshot` publishes with sequential `shutil.move`,
so a failure *between moves* can leave a mixed tree. Download staging means nothing
reaches `dest` unless every file downloaded (now tested against an existing
snapshot), and `verify_snapshot` detects the residual window. The docstring, which
previously over-promised, now states the actual guarantee. Directory-swap publishing
is deferred, not silently dropped.

#### Mutation re-verification

Every mutation the reviewers used to prove a test was vacuous was re-run after the
fix cycle. **All 7 that previously passed now fail:** verdict permutation, no-op
merge, `label_counts` yes/no swap, constant `canonical_inchikey`, widened vendoring
allow-list, naive pipe split, and subset-only category check.

#### Human blockers — still absent, nothing fabricated

T2, T1, T8, T18, T14 remain undelivered. No provenance file, commit SHA, UniProt
ratification, roster entry or evidence DOI was invented. `configs/barrier_panel.yaml`
ships `ratified: false`. The T4a/T4 legs were changed from an unconditional `skip`
to a `skipif` keyed on the artifact, so they **self-lift** when T2 lands rather than
staying silently green. T19 confirmed all seven draft accessions resolve as human
with matching gene symbols — mechanical groundwork for T8, **not** a ratification.

---

### P0.3 — pr-prep gate (2026-09-01)

**Gate:** `ruff check` + `ruff format --check` clean; `pytest -m "not network"`
**289 passed / 7 skipped**; `pytest -m network` **15 passed / 1 skipped**.
Reviewers: code, security, design, test + scorer + own review. Threshold 80.
Receipt: `qgr/…-qgr-pr-prep-20260901-0321-7768719.md`.

Scope reviewed: the delta `b18d097..HEAD` (README, barrier panel, CONTEXT). Earlier
commits carry the P0.1/P0.2 receipts. **Most findings were against material added in
this cycle, not against the 29 gated tasks** — the gate caught the reviewer.

#### The scorer's own finding (N1) — the one four reviewers missed

`build-plan.md` T7's interface block prescribed `TFRC … face: apical`; the live
config had been changed to `basolateral`. T8 authorizes correcting *accessions* and
*deleting* entries — never a `face` change. The value was written **ahead of the
plan amendment**, putting the config out of conformance with a G4-signed document,
with nothing mechanically guarding it. Escalated (#17), ruled option (a) (#18): T7
now prescribes `basolateral` with both caveats carried in the plan, re-signed
`b5443bd`. Sequencing error, recorded rather than quietly corrected.

#### Most consequential catches

**S1 — the DVC remote fix reintroduced the failure class E-5 existed to prevent.**
The committed absolute url named one developer's home directory and shipped to a
public remote. Worse than disclosure: DVC's local remote *creates* the directory on
push, so every other contributor and CI got a **silent empty success** on push and
nothing on pull, rather than a clean misconfiguration error. Moved to the
already-gitignored `.dvc/config.local`.

**S3 — a test that blocked its own fix.** `test_s9_remote_matches_the_ruled_path`
compared a committed constant against a value parsed from a committed file: it
passed on every machine, verified nothing, and went red the moment anyone corrected
the config. Deleted; the two machine-independent guards survive and now skip cleanly
when no url is configured.

**T1 — the live barrier panel had no `face` assertion of any kind.** The only
entry-schema check read the *fixture*. `face: appical`, a dropped key, or a
duplicated symbol passed the entire offline **and** network suite.

**T4 — a single missing `face` became `NaN`, not an error.** `pd.DataFrame` over a
list of dicts fills a partially-missing key silently; only an all-entries-missing
key raised. Inert while `ratified: false`, live the instant T8 flips it — and a
human editing one row is exactly who drops one key. Validation added at load.

**D1 — biological numbers written into an identity-only file.** Localization ratios
(~800:1 … ~2:1) were placed in `configs/barrier_panel.yaml` comments. AM-3 defines
that file as carrying no numbers; comment form dodges the numeric-leaf validator but
not the rule. Relocated to `T8-review-record.md`.

**C2 — README claimed `data/` is "never in git".** False, and verbatim the
misconception that produced F-01: `.gitignore` deliberately re-includes provenance
files, `.dvc` pointers and `.sha256` digests.

#### Reviewer conflict, resolved by the scorer

Code review said update the five fixtures' TFRC face (an M1 test written against the
fixture would bake in the reversed direction, since `load_ratified_panel` refuses the
unratified live config and forces every offline consumer onto the fixture). Test
review said do **not** — fixtures are independent and updating implies an attestation
they cannot make. Ruling: **annotate now, edit later.** Fixtures gain a header saying
`face` is schema filler; a **skipped** fixture-vs-config agreement test names T8 as
its blocker and makes the divergence self-announcing. The fixtures currently match
the signed plan — editing them now would turn one divergence into six.

#### Rejected after verification (2)

**D8** — two of three cited lines were wrong and the third uses the canonical
glossary term. **D12** — the Layout section correctly omits directories that do not
exist on disk; adding them would be the defect.

#### Escalated, not fixed here

`build-plan.md` amendments (G4 hash-locked — N1, T8 `face` scope, `ratified_panel_sha256`,
the E-5 mechanism, D9's correction), all landed by the CTO at `bfa2c1e`/`87c74c5`.
`config/monitor-pids.json` (framework-owned, commits live PIDs). `LICENSE` — absent, but
licence posture is human-owned T1 and an agent authoring one would simulate a blocked task.

**Human blockers — artifacts correctly ABSENT:** T2, T1, T8, T18, T14.
