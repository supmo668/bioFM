# Deferred-findings register — lung-on-chipsim

*Written BEFORE the Stage 1 boundary gate, per CTO ruling #520, on the aviary-biosim F23–F35
precedent. Its purpose is narrow and mechanical: a reviewer who re-discovers one of these is
**DEFERRED-BY-REGISTER**, not a new finding. **A finding not in this register is new**, and is fixed
or registered on its merits.*

**Why these are unrepaired.** E-23 closed at the scope it reached under a principal time box fixed
**before** gate 9 ran (approval-log the 2026-09-28 11:30 row, applied at the 2026-09-28 16:06 row, verdict `#58`). A gate-9 failure on the
recurring family closed the work item with no r2.51 and no fix cycle. Repairing them now to make the
boundary gate quieter would defeat the stopping rule the record's credibility rests on.

**What the receipt therefore certifies:** the whole branch diff against `origin/main`, **with these
named deferrals, under these rulings** — not a diff scoped to avoid them.

| id | file / symbol | gate-9 finding | severity | closed under | Stage 1 limitation |
|---|---|---|---|---|---|
| D-01 | `tests/shape_scan.py` — `_carries_a_citation` docstring example; `tests/test_shape_scan.py` — the positive-control fixture in `test_PROSE_ABOUT_citations_does_not_make_a_file_count_as_cited` | The citation predicate is satisfied by **the prose that explains it**. Both files read as cited; 53 of 142 sites landed in F at `6b642d8`, four of them the test file's own. Found independently by **all four reviewers**, reproduced live by each. | CRITICAL | `#58` | §2, §5 |
| D-02 | `tests/shape_scan.py` — `_positions` vs `classify_sites` | Two definitions of "line N": the scanner counts line feeds, the classifier indexes `str.splitlines()`, which breaks on nine further code points. One such character above a site drops it from **all four buckets** while the pass condition still reads 0. Reproduced for all nine breakers; **latent** — 0 live instances measured. | HIGH | `#58` | §5 |
| D-03 | `tests/shape_scan.py` — `classify_sites` | Re-derives the site set instead of consuming the scanner's, so **accounted** tokens sharing a line with an unaccounted one are counted, inflating buckets above the site count. Can make the residual go negative, or cancel D-02's silent drop. Latent — no line currently mixes the classes. | HIGH | `#58` | §3 (F upper bound / N lower bound) |
| D-04 | `tests/test_shape_scan.py` — `test_every_in_scope_site_lands_in_EXACTLY_ONE_bucket_sum_identity` | Asserts a different identity from the one the clause states, and is vacuous over half its own formula: both `accounted` terms are 0 in all three samples. The clause's five-term identity is asserted by no test. | HIGH | `#58` | §5 |
| D-05 | `qgr/evidence/r250-classify.py` — `p5_config` | The union rule is documented and then discarded: the loop body is `pass`. Direction is safe (sites stay out-of-guard-scope rather than being excused), so it over-claims rather than falsely excludes. | MEDIUM | `#58` | §5 |
| D-06 | `qgr/evidence/bracket.py` — `_assert_output_carries_no_shapes` call site | The self-check runs over the payload inside `capture()`; `main()` then adds the `shape_scan` block and writes with different serialisation. The bytes on disk are a superset of the bytes checked. Not exploitable today — every field there is a constant or a path already checked. | MEDIUM | `#58` | §5 |
| D-07 | `qgr/evidence/bracket.py` — `differences` | Duplicate metadata entries collapse under set comparison, so a vanished duplicate yields "metadata CHANGED" with no line naming what moved. | MEDIUM | `#58` | §5 |
| D-08 | `tests/test_structure_pattern_differential.py` — `test_no_literal_count_of_the_breakers_is_written_anywhere_in_this_file` | Scans only the file prefix before its own definition and matches two exact phrasings. A hand-typed derived count already sits in the region it does scan, invisible to it. | MEDIUM | `#58` | §5 |
| D-09 | `tests/test_structure_pattern_differential.py` — `test_the_proof_corpus_actually_EXERCISES_the_construct_that_broke_it` | The anti-vacuity guard pins a **syntactic** class (a counted capturing group) that omits the property making it anti-vacuous (**width > 1**). Drop the one width-2 pattern and restore the original defect: 9 tests pass with the defect back. | HIGH | `#58` | §5 |
| D-10 | `tests/shape_scan.py` — `classify_sites` | Never consults `ShapeReport.could_not_scan`, so a could-not-scan input returns all-zero buckets — byte-identical to a fully-classified clean file. Re-merges the state ruling #455 split in two. Not reachable through the current harness. | MEDIUM | `#58` | §5 |
| D-11 | `qgr/evidence/bracket.py` — the `_git` guard and the empty-set guard | The refusal path interpolates the absolute host root and git's raw stderr to stdout, while `capture()` deliberately redacts the same value in the **record**. The record is protected; the console is not. | MEDIUM | `#58` | §5 |
| D-12 | `qgr/evidence/bracket.py` — `--compare` | `gated_files` entries from a before-capture JSON are joined to root without validation; an absolute or `..` entry escapes it, yielding a hash/existence oracle written into the tracked record. Primitive reproduced; end-to-end not attempted. | MEDIUM | `#58` | §5 |

## Round-2 re-gate findings — DEFERRED under approval-log row 61

Ruling: **row 61** (principal, verbatim *"Stop; the mechanism is the result"*). No fifth repair round.
Only truth-blockers were fixed; everything below is **bound, not repaired, by row 61**. Reviewers who
re-discover these are scored DEFERRED-BY-REGISTER.

Scope note: the round-2 gate reviewed the 19 files changed since the round-1 gate at `8dcf9fd`, on
four isolated snapshots plus the authoring agent's own read-only pass. Five findings converged across
two or three independent readers; those are marked **(converged)**.

| id | file / symbol | round-2 finding | severity | status | Stage 1 limitation |
|---|---|---|---|---|---|
| R-01 | `qgr/evidence/redact-records.py:119-121` | The safety flag fails **open** and the danger flag fails **closed**: `args` drops every `--` token while `dry` is exact-match, with no unknown-flag rejection, so `--no-write` and `--dry-run=1` both **write**. `--no-write` is this repo's own house flag, documented elsewhere as what lets a reviewer re-run a tool without voiding a bracket. | HIGH | bound, not repaired by row 61 | §5 |
| R-02 | `qgr/evidence/redact-records.py:147-164` | The write path is executed by **no test**: mutating it to write back the *unredacted* original left 7/7 green. The instrument can print `REDACTED (N, M)` and exit 0 having changed nothing. A check that cannot distinguish "redacted" from "reported redacted". | HIGH | bound, not repaired by row 61 | §5 |
| R-03 | `qgr/evidence/redact-records.py:128-158` | The batch is **not atomic** and the console misreports: a refusal returns after earlier files were rewritten *with footers claiming completion*, the summary never prints, and `REDACTED` is printed *before* the write. Non-`ValueError` exceptions still traceback, which the module's own comment claims to have closed. | HIGH | bound, not repaired by row 61 | §5 |
| R-04 | `qgr/evidence/bracket.py:295` | The **`stash`** metadata channel is bound by nothing — the planted-token loop covers `branches`/`tags`/`status` only, and the anti-vacuity backstop is vacuous for a channel empty in the fixture. Making it verbatim leaves the suite green. This is the exact channel of the verified gate-7 breach. **(converged)** | HIGH | bound, not repaired by row 61 | §5 |
| R-05 | `tests/test_bracket.py:712-714` | Fix (vii)'s digest assertion is **vacuous**: the disjunct `or any(len(e) == 64 …)` is true by construction. Digesting a *constant* — destroying the entry identity the digesting exists to preserve — leaves both new tests passing. **(converged)** | HIGH | §5 |
| R-06 | `paper/stage1-claims-list.md:130-131` vs `stage1-limitations.md §1` | The claims list says the NOT CLAIMED list is "carried in full" in limitations §1; §1 carries **6 of 9**, omitting the three most load-bearing. `traceability-check.py` check 4 compares long vs short only and never reads the limitations file, although it is in `DRAFTS`. | HIGH | bound, not repaired by row 61 | §1 |
| R-07 | `paper/stage1-short-form.md` vs `stage1-methods.md` | Short-form independence has got **measurably worse**, against a design spec saying neither document is the other's parent: 32.5% of body 7-grams shared, longest shared run 37 words (31 with the abstract alone). Round 1 measured 26 words / 26%. No check exists. | HIGH | §5 |
| R-08 | `qgr/evidence/r250-classify.py` | No `main()`, no `sys.exit`, **no `--no-write`**; writes into the tracked evidence directory from module top level, so importing it mutates the tree and can void a bracket. It prints `(PASS requires 0)` next to three conditions and exits 0 regardless — it can neither fail nor be seen to fail. Ruling #455 says could-not-scan fails the gate. **(converged)** | HIGH | §5 |
| R-09 | `qgr/evidence/traceability-check.py:94` | The "full body" comparison excludes continuation lines beginning `\|` or `>`, and stops at a blank line, so the short form can still contradict the long form. The docstring claims "the whole normalised body". Fix (v) closed the instance and left the class. **(converged)** | HIGH | §5 |
| R-10 | `qgr/evidence/{traceability-check,scan-artifacts,route-distribution,r250-classify}.py` | Verdict and exit-code paths executed by **no test**; `grep` finds zero references to any of the four under `tests/`. Partly reduced this round (`claims-vs-records.py` ships with tests), otherwise open. **(converged)** | HIGH | §5 |
| R-11 | `qgr/evidence/redact-records.py:14-17, 67-91` | The docstring's central claim — "one definition, the two cannot drift" — is **false**: `plan()` shares the detector atoms but re-implements the accounting combination. Teaching the scanner a new documented category makes the redactor **destroy** it, suite green. | MEDIUM | bound, not repaired by row 61 | §5 |
| R-12 | `qgr/evidence/redact-records.py:83-115` | An **ACCOUNTED** token can be destroyed: the documented all-zeros probe, promised to survive redaction, is swallowed when adjacent to an unaccounted structure token (`_STRUCTURE_RE` is greedy over non-whitespace), and the footer then reports `0 accession tokens`. The footer counts tokens **planned**, not **applied**. Measured live over 83 `qgr/**` files: **0 currently triggered** — real but latent. | MEDIUM | §5 |
| R-13 | `tests/shape_scan.py:185` | `MARKER_WINDOW_LINES` has **no behavioural binding**: production can be ±1 off in either direction and 27 tests stay green, because the negative test pads by `+2` and nothing pins the boundary. W is a false-exclusion bucket feeding E3/E5. | MEDIUM | §3, §5 |
| R-14 | `qgr/evidence/route-distribution.py:78, 83` | Two **silent admission drops** survive fix (iii): a row indented by one space, and a row with fewer than five cells. A planted `\| 60 \| inferred \|` row vanishes with 0 rejected and exit 0 — invisible to the instrument F6 cites. | MEDIUM | §5 |
| R-15 | `qgr/evidence/r250-classify.py:264-265` | `n - qual` can go **negative**: adding a file that carries a shaped site *lowered* the published out-of-guard total (reproduced: 9 shapes in 1 file → 8 shapes in 2 files). | MEDIUM | §3 |
| R-16 | `qgr/deferred-findings-register.md` (this file) | **8 of the 12** original deferrals map to a limitations section that does not mention them — D-05, D-06, D-07, D-08, D-10, D-11, D-12 → §5, and D-03 → §3. A referee auditing row 58's promise that findings "become Stage 1 limitations" lands on text that does not contain the finding. | MEDIUM | §5 |
| R-17 | `tests/test_shape_scan.py:403-406` | `_cited_line()`'s docstring claims it is assembled "so it does not make this file read as cited". The file **already** reads as cited, via a plain literal elsewhere in it, and its own sites are subtracted into F. The assembly buys nothing and nothing asserts the property it names. | MEDIUM | §5 |
| R-18 | `qgr/evidence/route-distribution.py:148` + `route-distribution-1f0811b.json` | F6's "zero rows marked `inferred`" is represented by an **absent key**, not a measured zero, so a reader cannot distinguish "measured 0" from "this rule version has no such category". The cited record also predates fix (iii) (no `rows_not_extracted` key). | MEDIUM | §5 |
| R-19 | `qgr/evidence/route-distribution.py:125, 131` | `mapping` entries carry `"raw"` — revision-table row text copied **verbatim** into a tracked JSON record, and rejected rows are printed verbatim to stdout. Latent: 0 unaccounted shaped tokens across the 13 `qgr/**/*.json` files today. | LOW | §5 |
| R-20 | `qgr/evidence/redact-records.py:58`, `route-distribution.py:184-191` | Dead code that misstates the enforced rule: `SAFE_PREFIXES` is defined, documented as the redactor's permission rule, referenced nowhere, and is strictly **weaker** than the live `_is_safe`; and the rejected-rows refusal is duplicated, the second copy unreachable while reading as an independent guard. | LOW | §5 |
| R-21 | `qgr/evidence/*.py` (6 call sites) | `git` invoked as an **unqualified binary name**. No injection (argv lists, no `shell=True`), but `r250-classify.py`'s `ls-files` output *defines the scanned corpus*, so a `git` earlier on `PATH` returning a short list shrinks the measured set and the scan reports clean. Not reproduced. | LOW | §5 |
| R-22 | `qgr/evidence/r250-classify.py:72-73` | Residual untrusted search path in the fallback: `sorted(...)[0]` over a user-writable plugin cache, unpinned and with no hash check; it also misorders versions (`0.9.0` vs `0.10.0`). Materially weaker than the closed regression — needs filesystem write, not just `PATH` — but the same primitive. Not reproduced. | LOW | §5 |
| R-23 | `qa/_adhoc/lung-on-chipsim-walkthrough-product.md` | Front matter says the file is republished "unchanged, with the 2026-09-29 re-measured state appended", which is self-contradictory, and the file contains no 2026-09-29 content. Body still says "1 of 5 human-owned inputs delivered" and names the compound roster as the blocker, while the roster ships 26 curated entries. | LOW | §1 |
| R-24 | `qgr/evidence/prprep-bracket-before.json` | Carries 305 gated file paths **verbatim**, including 261 `.claude/usr/**` dispatch paths whose filenames spell out escalation subjects and the operator username. Host root is clean (mechanism (5) works for metadata); `gated_files` and `per_file` are never digested. Scored LOW only because the principal ruled that surface publishable. | LOW | §2 |

### Fixed this round, NOT deferred

| finding | fix |
|---|---|
| **C-1** the scan's surface excluded an entire classified root, so "0 cited inside the classified scope" was computed over a partial intersection and published as a property of the scope | surface derived from `git ls-files` — the same corpus the classifier uses — plus `surface_vs_scope` reported per root every run. A **first attempt using filesystem globs swept 26,623 files** (virtualenv + untracked journal copies) and is recorded as a failed repair |
| **C-2** the audit-surface path guard was bound by no test; disabling it left 7/7 green | three tests, including the in-repo/outside-surface input no test reached, byte-unchanged assertions, and a distinguishability test pinning that the two refusals differ. 4 mutants killed |
| **C-3** blocker 4 re-opened twice: a widened `raises` tuple, and a bare `assert` at the call site making all nine cases xfail for the wrong reason with the file byte-identical | the divergence has its own **type**, `RegisteredSplitlinesDivergence`, raised only by the witness; marker narrowed to it; behavioural companion plus a raised-in-one-place guard. 4 mutants killed |
| **H-6** nothing bound a typed number in the paper to the measurement it cites (7 mutations to published counts all passed) | `claims-vs-records.py` — four mutation-proven arms; deliberately does **not** enforce the unsatisfiable "record measured the gated commit" |
| **H-7** H1 cited the superseded 10-file record, whose file list omitted the documents asserting H1 | repointed; the withdrawn H4 form rowed as CUT (H5) |
| **H-10** the one sentence stating the citation scheme misresolved a row (`#54` called eleventh-from-last; it is sixth) | recomputed from the log, not recounted |
| **SEC-8** the register cell describing the untrusted-search-path **vulnerability** as its own fix | reworded to what the fix does; a maintainer trusting it would have reopened an execution vector |
| E5 stated 471 shapes / 21 files in all four documents; the record measuring 445 / 20 sat uncited | every published classification count re-derived from the current record |
| the out-of-guard **file** count was a subset sum no instrument emitted | `r250-classify.py` now emits `out_of_guard_scope_files` — the checker was *not* widened to accept arbitrary subset sums, which would have made its agreement arm vacuous |
| the short form attributed the upper/lower bound to 471/62 | re-attributed to buckets F and N; 471 was never a bound on anything |
| three inconsistent denominators in the paragraph about inconsistent counts ("14 of 539 — 2.6%", "621") | both recorded counts named against their records; the percentage removed rather than recomputed, since the two were measured over different trees |
| limitations §5 listed as unrepaired a defect the register lists as fixed | contradiction resolved; the still-live half (D-05) kept |
| **a fabricated finding avoided** — the "48-vs-46 instrument disagreement" #540 asked to be recorded | does not exist: at `9f753d7` bucket F is 48 and the scan's comparable figure is 48. The gap was a fresh scan against a **stale** classifier record, i.e. an artifact of the staleness this round is about |

## Round-3 (FINAL gate) findings — the gate FAILED; Stage 1 CLOSES at the scope reached

Ruling: **row 61**. CTO #541: *"If it FAILS again on the same mechanism → Stage 1 CLOSES at the scope
reached."* It did. **No QGR receipt is signed. Nothing is pushed. The branch does not land.**

Four reviewers on isolated snapshots (4.4 MB / 271 files each, measured at creation) plus a read-only
pass by the authoring agent. Base `origin/main` → HEAD `af17cd2`; Hash A
`0219b888500e8a01d09642657a7c49557ffe1c4333780c4023b5a24d817c68f9`, 116 files.

**Reviewer isolation:** `tree-bracket verify` returned `TREE_UNCHANGED` mid-review. The final
verification could **not** be produced — the snapshot token was reaped from the system temp directory
— so the bracket's own attestation for the whole window is **UNKNOWN**. Independently confirmed
instead: HEAD unchanged at `af17cd2` and `git status` empty. Recorded as UNKNOWN rather than as a pass.

### Corrected during this gate (CTO #541: a wrong number blocks truth)

Every figure re-derived from a record; none typed. Five of the six were introduced by the agent.

| what was published | corrected to | source of the error |
|---|---|---|
| 59 numbered revisions / 63 data rows / 46 standing-delegation / 2 principal-verbatim, in four documents | **61 / 65 / 47 / 3**, re-derived and re-pointed at `route-distribution-af17cd2.json` | the log grew by rows `#60`/`#61` **during this gate's own adjudication**; nothing re-derived the figure, and the paper pinned it to the plan hash `ae894db`, which rows `#58`–`#61` all share, so the pin could not discriminate |
| methods §9: "48 sites … against a classifier bucket F of **46** — those two instruments disagree", ×3 in one paragraph | the records' **48 vs 48**, with the fabrication named as withdrawn | agent hardcoded `BUCKET_F = 46` into a generator script while enforcing *"counts are regenerated, never typed"*, then corrected only the claims list |
| limitations §2: "139 of 139 in-scope sites" — the sentence CTO #512 makes **binding** | **141 of 141**, commit-pinned | agent's substitution list was hand-enumerated; unlisted occurrences were silently skipped |
| limitations §3 table: configs `2 / 35`, summing with fixtures to the withdrawn **471 / 21** under a **445 / 20** headline | **1 / 9** | same hand-enumerated list |
| methods §7: `#54` is "the sixth-from-last row" | **eighth**-from-last, recomputed from the log | repaired under H-10 for this exact error, then re-broken by rows `#60`/`#61`; nothing recomputes it |
| short form: "three counting errors … [H3]" | re-cited to methods §9; H3 carries one | mis-citation |

Two claims were also restated rather than renumbered: **H4** no longer says its surface "EQUALS" the
scope (it is a suffix-filtered **subset**: `eligible_by_suffix` 127 of `tracked_in_scope` 160 in
`projects/`), and **H5** no longer attributes the comparable subset's sum to all seven cited files.

While making those corrections the agent twice stated a number **no instrument emits** (the
tracked-minus-eligible difference; the sum over all seven cited files). `claims-vs-records.py` caught
both and they were reworded to state only emitted fields. That is the one point in this round where an
instrument caught the family before a reader did.

### DEFERRED under row 61 — bound, not repaired

| id | file / symbol | round-3 finding | severity |
|---|---|---|---|
| S-01 | `qgr/evidence/claims-vs-records.py:70` | ARM 1 — the arm the module calls its strong guarantee — decides "newest record" by **`st_mtime`**, which git does not preserve. **False FAIL reproduced** (uniform mtimes after any clone/copy → names a 7-key, oldest-schema record as newer than the only record carrying the 2026-09-30 amendment; 10 phantom "cites SUPERSEDED"). **False PASS reproduced** (a strictly newer uncited record whose short SHA sorts earlier → `failures: 0`, PASS). Mutating the sort key to `p.name` leaves 9/9 green: no test pins the ordering. A content-derived signal exists and is unused — `scan-artifacts-87d5c46.json`'s `per_file` **contains** the `9f753d7` records, establishing order by containment. | **CRITICAL** |
| S-02 | `claims-vs-records.py:195-254` | The check **passes with every record citation deleted**: arms 1–3 are all driven by `cited_names`. Reproduced: 10 citations removed → `records cited: 0`, `failures: 0`, **PASS**, with newer records uncited. This is verbatim the threat model the suite's own `test_ARM4_a_MISSING_summary_line_FAILS…` articulates; it was applied to one arm of four. No floor on `len(cited_names)`. | **CRITICAL** |
| S-03 | `claims-vs-records.py:109-142` | ARM 2 inspects only the text unit that **textually names a record**: **18 of 859 lines (2.1%)** of the four documents; `stage1-short-form.md` has **zero** citations, so arms 1–3 are vacuous over it entirely. Reproduced: inserting **one blank line** before a bracketed reference makes a planted `999` invisible. This is the mechanism by which three of this round's wrong numbers survived — the fabricated `46` is caught the moment the citation moves into its paragraph. The paragraph branch itself is executed by no test (mutating it to `line` leaves 9/9 green) and carries 3 of the 10 real citations. | **HIGH** |
| S-04 | `claims-vs-records.py:52` | `INSTRUMENTS` omits `route-distribution`, exempting the citations where the round's largest staleness actually lived, from all four arms. | **HIGH** |
| S-05 | `claims-vs-records.py:77, 250-268` | ARM 3 covers **top-level ints only** — every field C-1 added (`fatal_counts.*`, `surface_vs_scope.*`, `reported_not_fatal_counts.*`) is nested and unchecked (6 top-level vs 13 and 34 nested ints in the two cited records). Coverage is also matched **by value, not by name**, so one mention of `0` marks every zero-valued field asserted; and a **deleted** field is not noticed. The docstring's "adding a field forces a decision here" is false. | **HIGH** |
| S-06 | `qgr/evidence/scan-artifacts.py:243, 339, 377` | `fatal["empty_patterns"]` is assigned **after** the record is written, so **every record on disk reports `empty_patterns: 0`** whatever the run measured, and carries no `verdict` field. Reproduced: a run printing `empty_patterns 1 / VERDICT: FAIL` wrote a record whose fatal summary is all zeros. The agent's own comment at :243 is accurate about intent and false about effect. | **HIGH** |
| S-07 | `scan-artifacts.py:277-284` | `not_reached` is **reported but not fatal**, so C-1's defect recurs with **VERDICT: PASS**. Reproduced: narrowing the surface to exclude the test corpus → **69 of 127 eligible unreached**, all four fatal counts 0, **PASS**, and the record publishes **0** comparable in-scope sites — re-manufacturing as a property of the scope precisely the zero withdrawn as CUT row H5. `surface_vs_scope` also detects a *surface* narrowing but is blind to a *suffix-list* narrowing, because both sides are computed from the one constant. | **HIGH** |
| S-08 | `scan-artifacts.py:114-127` | The FATAL audit-surface arm reads only `.md`, so `shapes_on_audit_surface: 0` is a zero over a surface not fully looked at. Reproduced: byte-identical probe, `.md` → FAIL, `.json` → PASS. Nothing asserts the audit surface is markdown-only. | **HIGH** |
| S-09 | `tests/test_structure_pattern_differential.py:1605-1622` | C-3 closes the named instance but **not the class**: a **subclass** of `RegisteredSplitlinesDivergence`, or the type raised under an **alias**, impersonates the registered finding with the file **byte-identical to baseline** (39 passed / 9 xfailed). The "raised in one place" guard is an exact-literal `str.count` over one file; the behavioural probe patches one operand and drives **1 of 9** breakers. A structural fix is an AST walk for `Raise` nodes resolving to the type. | **HIGH** |
| S-10 | `qgr/evidence/redact-records.py:64` | The guard's **boundary** is unbound: deleting the `and "/qgr/" in rel` conjunct makes the whole of `workstreams/**` redactable without `--allow` — including the signed plan and the approval log, verbatim the hazard its own refusal message names — with the suite green. C-2 closed "the guard is never executed" and left "the guard's boundary is never tested". Its **positive** arm is also untested (`_is_safe → False` leaves 10/10 green), as is `--dry-run`'s no-write promise. | **MEDIUM** |
| S-11 | `claims-vs-records.py:240` | The tokenizer still fabricates failures: the comma fix closed an instance, not the class. A space-grouped `1 031` still invents `31`; any decimal invents its fractional part; a number of 8+ digits is exempt from ARM 2 entirely. Under row 61 a fabricated FAIL would close Stage 1 at the wrong scope. | **MEDIUM** |
| S-12 | `claims-vs-records.py:149-156` | `status.startswith("CUT")` cannot fire on the bolded `**CUT.**` style the table uses, so arm 4 reports a *correct* summary as wrong. As shipped it fails loudly; the hazard is the repair — restating the summary to match would make arm 4 certify a CUT claim as SUPPORTED. | **MEDIUM** |
| S-13 | `claims-vs-records.py:148, 203, 220` | Three ordinary inputs crash with a traceback and **no `VERDICT` line at all** (truncated record JSON, an absent `DOCS` file, a non-UTF-8 byte). Exit is 1, so an exit-code harness fails closed; a stdout harness sees nothing. | **MEDIUM** |
| S-14 | `claims-vs-records.py:227` | Every number inside backticks is exempt from ARM 2 by a convention nothing enforces — an unbounded laundering channel for exactly the class of number the instrument exists to catch. | **MEDIUM** |
| S-15 | `scan-artifacts.py` vs `r250-classify.py` | Two parses of the "one corpus" C-1 unified: `.split()` vs `.splitlines()`. Reproduced: a tracked path containing spaces is shattered into invented fragments by the scan and kept by the classifier, and `not_reached` stays 0 while a tracked eligible file is never read. Latent — 0 tracked paths contain whitespace today. `core.quotePath` quoting is a second unhandled form. | **MEDIUM** |
| S-16 | `tests/shape_scan.py:250, 267` | `could_not_scan` is set **only** for a literally empty string, so the condition's entire reachable domain is zero-byte files, and no zero-byte file exists on the scanned surface. The fatal arm is live-untriggered as well as untested, and ruling #455's coverage ("a scan that could not look") is broader than the implementation. `files_scanned` also counts an empty file as scanned. | **MEDIUM** |
| S-17 | `r250-classify.py:86-93` | `plan_hash()` returns `""` when the `plan_hash:` line is not found at line start, and `p1_signed` is `bool(PLAN_HASH) and …` — so any re-indent or front-matter wrapping of the approval file silently empties the P1 bucket and migrates its files into the guard's in-scope set, changing every published count with no warning. The sibling `file_hash()` raises `SystemExit` for exactly this reason. | **MEDIUM** |
| S-18 | `r250-classify.py:322, 357` | The two published out-of-guard numbers are summed over **different key sets** (two hard-coded names vs a `startswith` prefix). Identical today; a third out-of-guard bucket would enter the file count and not the shape count, making E5's pair two populations. | **LOW** |
| S-19 | `claims-vs-records.py` (ARM 2, calibration) | 23 of the 51 integers 0–50 are admissible against the cited record, so a drifting small count has roughly a 45% chance of matching something. Matters more because S-01 removes arm 1, which the docstring names as the strong arm arm 2 is merely "the net under". | **LOW** |
| S-20 | `qgr/evidence/claims-vs-records.py` + `scan-artifacts.py` + `route-distribution.py` + `traceability-check.py` + `r250-classify.py` | **R-10's extent grew.** `fatal_counts` — including the ruling-#455 counter — is a **new** fatal key, added this branch to an instrument the register binds as untested. Row 61's deferral was taken at a smaller extent than now exists. Four of the five instruments are still executed by no test. | **HIGH** |

### Confirmed sound, and worth recording

- **C-2** closes its defect: `_is_safe → True` and guard-deletion both killed, 2 failures each.
- **C-3** closes the named instance: a bare `assert` at the production call site can no longer
  impersonate the finding (2 of 9 cases fail loudly; a broader sanity assert fails all 9).
- **All four arms of `claims-vs-records.py` kill the mutants its tests drive**, and the fixture's
  monkeypatching has **not** made them vacuous — the real code paths run.
- **C-1's surface genuinely equals its scope today** (236 eligible / 236 reached / 0 not reached;
  dedup correct, 724 = 236 classified + 488 audit, no double count) — the defect is that the equality
  is reported and not enforced (S-07).
- Every number the gate brief named was **correct** against the newest record; every wrong number was
  one the brief did not name.
- `could_not_scan` **is** reachable and genuinely fatal (driven directly: zero-byte in-scope file →
  `VERDICT: FAIL`, exit 1).
- No deferral was re-opened. **R-02 is genuinely reduced** this round (the write-back mutant is now
  killed). R-21 was reproduced for the first time — a `git` shim on `PATH` cut the scan from 239 files
  to 100 with all fatal counts 0 and **PASS**, and `surface_vs_scope` is blind to it by construction.
- No `shell=True`, no `os.system`, no interpolated commands; the `AIADLC_DIFF_HASH` regression was
  **not** reintroduced; no new write path; no new stdout/record asymmetry.
- The relaxed-rule disclosure is adequate where it appears and discoverable without a diff, via
  methods → the record's `verdict_note` → limitations.
- **G3 and H2 resolve end to end** from the committed files alone under the stated citation scheme.

### Timing, with its conditions (CTO #555 condition 2)

| sample | wall-clock | conditions |
|---|---:|---|
| prior | **453 s** | no concurrent reviewers |
| final | **900 s, killed at 82%** | **23 concurrent pytest processes** from four reviewer agents |

Reported as **TIMEOUT**, explicitly not as a gate failure on substance (condition 3). The two samples
are **not comparable** — the like-for-unlike error this report documents. Under the original 600 s
ceiling this gate would have failed on the clock; raising it to 900 s was necessary, not precautionary.
The agent's own timing harness captured `$?` after a pipe to `tail`, so it printed `exit=0` for a
killed suite — and the same error was then repeated in the next command, on the bracket verification.
A clean re-measurement with no reviewers running is owed before any future ceiling decision.

## Registered but NOT deferred — already fixed in this branch

Recorded so a reviewer who finds them is not told they are deferred when they are closed:

| finding | fix |
|---|---|
| Hardcoded absolute host path and pinned plugin version in `r250-classify.py` | root derived from `__file__`; `diff-hash` resolved from a fixed relative path, or from an override that must be ABSOLUTE and must pass existence + executability checks — a bare-name override is REFUSED. **Corrected 2026-09-30 (round-2 SEC-8):** this cell previously read "`diff-hash` resolved from the environment", which is the VULNERABILITY, not the fix. `os.environ.get("AIADLC_DIFF_HASH", "diff-hash")` was the regression — an untrusted search path, i.e. arbitrary code execution — introduced while removing a host-path leak and closed at `r250-classify.py` `_resolve_diff_hash`. A maintainer trusting this register would have reopened it. |
| Claims bound to an instrument or an action rather than a stored measurement | three evidence artifacts produced and cited |
| Route distribution mixing substring and exact matching in one sentence | `route-distribution.py` under a stated first-match-wins rule with a per-row audit mapping |
| Traceability check's case-sensitive CUT detection and three-prefix path resolver | both fixed; mutation-tested |
| A summary reporting only its zero-valued fields | rule adopted: name every non-zero field, every time |

## Scope note for the scorer

D-01 through D-12 are **known, measured, and ruled**. A reviewer re-discovering any of them has
confirmed the register rather than found something new. **Anything else is new.** In particular the
register does not cover: the Stage 1 paper artifacts (written after gate 9), the three evidence
scripts produced for the rigour review, or the merge of `origin/main`.
