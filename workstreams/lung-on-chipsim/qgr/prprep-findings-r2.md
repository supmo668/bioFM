# PR-prep re-gate (round 2) — consolidated findings. VERDICT: FAIL. No receipt signed.

Base `origin/main` → HEAD `b6d5271`. Hash A `c7622d551939206416f499a548b908cba027e9caac2d82f633b33f69addf3501`,
115 files. Review scope: the 19 files changed since the round-1 gate at `8dcf9fd`, plus the mechanisms
they touch. Roster: reviewer-code, reviewer-security, reviewer-design, reviewer-test, each on its own
`git archive` snapshot (3.7 MB / 263 files, measured at creation), plus my own read-only pass. The
register of 12 deferrals (D-01…D-12) was supplied to each.

**No QGR receipt is signed. Nothing is pushed. Nothing lands.**

Round 1 named seven defect families; all seven were fixed and committed (`8fd4135`, `b6d5271`). This
round asked whether the fixes close the defects. **Four of the seven do not**, and the round-1
headline finding recurs in a new dimension.

---

## The result that matters most: fix (i) reproduced the defect it repaired

Round 1's top finding was *"claim H4 cites a scan record that omits the documents making the claim"* —
the scan reached 14 of 539 files, 2.6% of the published surface, and reported a clean verdict over
"the artifacts". I widened the globs to 622 files and restated H4.

`scan-artifacts.py` PATTERNS glob `workstreams/lung-on-chipsim/{paper,qgr}/**` and `.claude/usr/**`.
They **never glob `projects/lung-on-chipsim/**`**. Line 166 nevertheless defines

    classified_roots = ("projects/lung-on-chipsim/", "workstreams/lung-on-chipsim/")

So the sentence "3 reading as cited — **0 of them inside the classified scope**, i.e. none can swallow
a site" reports the *intersection of the scope with the surface* as though it were the scope.

Measured (reviewer, over the snapshot): 277 files live under the two classified roots; the globs reach
**88 (31.8%)**; 189 are never checked. Seven files inside the classified scope read as cited, all
invisible to the scan. Verified independently by me, running the production predicates directly:

| file (inside the declared classified scope) | reads as cited | buckets |
|---|---|---|
| `projects/lung-on-chipsim/tests/test_parse.py` | True | W 2 / **F 35** |
| `projects/lung-on-chipsim/tests/test_relative_stereo.py` | True | W 8 / **F 7** |
| `projects/lung-on-chipsim/tests/test_shape_scan.py` | True | **F 6** |

Bucket F at the cited commit is **46**. These three supply **48**. Essentially all of F comes from
files that read as cited and that the H4 scan never opens.

The qualifier presented as an honest weakening is what **restored** the original strength over a
surface that was never measured. A limitations entry congratulating the widening was written in the
same commit. **The direction matters: the verdict predicate is wider than the harm set (safe); the
measured population is far narrower than the scope the sentence names (not safe). Only the second
bears on the claim.**

---

## Convergence — found independently by two or more readers

Convergence was the strongest signal at gate 9 and is again here.

| defect | found by | status |
|---|---|---|
| `redact-records.py`'s audit-surface path guard is bound by **no test**: the refusal test points outside the repository and is caught by the earlier `relative_to` ValueError, so `_is_safe`/`--allow` is never reached. Deleting the guard entirely leaves 7/7 green. | security, test | reproduced by mutation, twice |
| `traceability-check.py`'s "full body" comparison excludes continuation lines starting `\|` or `>` (and stops at a blank line), so the short form can still contradict the long form. Docstring claims "the whole normalised body". | design, test | reproduced by mutation |
| The evidence instruments' verdict/exit-code paths are executed by no test — `traceability-check.py`, `scan-artifacts.py`, `route-distribution.py`, `r250-classify.py` have no test of any kind. | security, design, test | grep + reading |
| Fix (vii)'s digest assertion is weakened by an escape-hatch disjunct (`or any(len(e) == 64 …)`) that is true by construction. | design, test | reproduced by mutation |
| `r250-classify.py` has no `--no-write` and writes at module top level, so importing it mutates the tree and can void a bracket. | security, design | reading (`grep -c` = 0) |

---

## CRITICAL

**C-1 — `scan-artifacts.py:40-62` + `:166-168`.** The scan surface excludes an entire classified root.
See above. Asserted at `stage1-methods.md:231-243` and `stage1-claims-list.md:92`.

**C-2 — `redact-records.py:141`, test at `test_redact_records.py:102-108`.** The guard protecting
`projects/**` source and the signed plan from a mechanical rewriter is bound by nothing.
Mutation A (`if not _is_safe(rel) and not allow:` → `if False:`) and mutation B (`return True` as the
first line of `_is_safe`) each left **7 passed, green**. Mutation C (changing the out-of-repo refusal
string) **failed** the test — proving the suite binds only the out-of-repo branch. `--allow` is
executed by no test. Confirmed live: `redact-records.py <plan-approval.md> --allow` rewrites the
signed plan with no confirmation and no covering test.

**C-3 — `test_structure_pattern_differential.py:1568`.** Round-1 blocker 4 re-opens. The guard reads

    assert raises is AssertionError or (isinstance(raises, tuple) and AssertionError in raises)

A tuple `(AssertionError, Exception)` satisfies it while making the strict xfail accept **every**
exception. Reviewer widened the tuple and injected a plausible sanitisation `ValueError` upstream:
**37 passed, 9 xfailed — byte-identical to baseline**. The registered gate-6 divergence is then
exercised by nothing. Verified by me by reading line 1568. The test is named
`…accepts_ONLY_the_registered_divergence_not_any_exception`.

---

## HIGH

**H-1 — `redact-records.py:119-121`: the safety flag fails OPEN, the danger flag fails CLOSED.**
`args = [a for a in argv if not a.startswith("--")]` drops every `--` token; `dry = "--dry-run" in
argv` is exact-match; there is no unknown-flag rejection. `--no-write` and `--dry-run=1` both **write**.
`--allow` is also exact-match and therefore fails closed — exactly inverted. `--no-write` is this
repo's house flag, and `scan-artifacts.py:66-68` documents its purpose as letting a reviewer re-run a
tool without voiding a bracket. The one tool with write access to the audit trail accepts it and
ignores it. Verified by me by reading.

**H-2 — `redact-records.py:147-164`: the write path is executed by no test.** Mutating `if not dry:` →
`if True:` *and* writing back the **unredacted** original left **7 passed, green**. The instrument can
print `REDACTED <file> (N accession, M structure)` and exit 0 having written the file back unredacted.
A check that cannot distinguish "redacted" from "reported redacted".

**H-3 — `redact-records.py:128-158`: the batch is not atomic and the console lies.** A refusal
`return 2` fires after earlier files were already rewritten *with footers claiming completion*, and the
summary line never prints — an operator reading "REFUSED, rc 2" concludes nothing happened. `:156`
prints `REDACTED` *before* the write at `:158`. Non-`ValueError` exceptions still traceback, which the
module's own comment at `:132-134` claims to have closed. Verified by me by reading.

**H-4 — `bracket.py:295`: the `stash` channel is bound by nothing, and it is the channel of the
verified gate-7 breach.** The planted-token loop covers `branches`, `tags`, `status` only; the
anti-vacuity backstop is vacuous for any channel empty in the fixture, and `_throwaway_repo` never
creates a stash. Mutation `"stash": _digest_lines(` → `"stash": sorted(` stayed green; the same
mutation on `worktrees` and `status` was killed.

**H-5 — fix (vii) is vacuous** (`test_bracket.py:712-714`). The second disjunct is true by
construction. Mutating `bracket.py:225` to digest a **constant** — destroying every entry's identity,
the property the digesting exists to preserve — leaves both new (vii) tests passing. I reported this
fix as mutation-proven; my mutation targeted `differences()`, not the identity property the test names.

**H-6 — no instrument compares any typed count in the paper to any evidence record.** Seven mutations
all PASS, including restoring the withdrawn stronger claim `0 reading as cited — 3` **verbatim**.

**H-7 — `stage1-claims-list.md:89`: H1 still cites the superseded 10-file record**, whose `per_file`
omits `stage1-methods.md`, `stage1-short-form.md`, the design spec, `traceability-check.py` and the
register. This is round-1's finding, repaired at H4 and left standing at its sibling one row above.

**H-8 — `stage1-claims-list.md:130-131`** claims the NOT CLAIMED list is "carried in full in
limitations §1". §1 carries **6 of 9**, omitting the three most load-bearing. Check 4 never looks at
the limitations file, although it is in `DRAFTS`.

**H-9 — short-form independence has got measurably worse**, against a design spec saying neither
document is the other's parent: **32.5%** of body 7-grams shared, longest shared run **37 words**
(31 with the abstract alone). Round 1 measured 26 words / 26%.

**H-10 — `stage1-methods.md:147`: the sentence stating the citation scheme misresolves a row.** It
says `#54` is the "eleventh-from-last" row; `#54` is at physical position **58 of 63** — the **sixth**
from last. Verified by me by recomputing over the log. "Eleventh-from-last" resolves to `#53`.

**H-11 — four evidence instruments have no test of any kind**, including three with real verdict
paths; and **`r250-classify.py` states a PASS condition it never evaluates and always exits 0** — it
has no `main()`, no `sys.exit`. Its verdict is a human reading stdout. It can neither fail nor be seen
to fail.

---

## MEDIUM (selected)

- `redact-records.py` docstring's central claim — "one definition, the two cannot drift" — is false:
  `plan()` shares the atoms but re-implements the accounting combination. Teaching the scanner a new
  documented category makes the redactor **destroy** it, suite green.
- An **ACCOUNTED** token can be destroyed: the documented all-zeros probe, promised to "survive
  redaction", is swallowed when adjacent to an unaccounted structure token (`_STRUCTURE_RE` is greedy
  over non-whitespace). Footer then claims `0 accession tokens`. Measured live over 83 `qgr/**` files:
  **0 currently triggered** — real but latent.
- The deferred register's "already fixed" row describes the untrusted-search-path fix as "`diff-hash`
  resolved from the environment" — **that is the vulnerability, not the fix**. A maintainer trusting
  the register would re-open the execution vector. (This register is mine.)
- `MARKER_WINDOW_LINES` has no behavioural binding: production can be ±1 off in either direction and
  27 tests stay green. W is a false-exclusion bucket feeding E3/E5.
- Fix (iii) left two silent admission drops (an indented row; a row with <5 cells). A planted
  `| 60 | inferred |` row vanishes with 0 rejected, exit 0.
- E3/E5/F2/F3/F6 cite records predating fixes (ii)/(iii) — proven by record **schema** (missing
  `scanned_and_empty` / `rows_not_extracted` keys), which is stronger than commit order. F6's "zero
  inferred rows" is an **absent key**, not a measured zero.
- `limitations.md:129-130` states as unrepaired a defect the register lists as already fixed.
- Three typed counts disagree across documents: **621 vs 622**; "14 of 539" vs "10"; **539 appears in
  no artifact anywhere**.
- The short form reassigns the upper/lower bound from F/N to 471/62 — unrelated quantities.
- **8 of 12 deferrals** map to a limitations section that does not mention them.
- `_cited_line()`'s docstring claims it is assembled so the file does not read as cited; the file
  already reads as cited via a literal at `test_shape_scan.py:385`, and its own 6 sites are subtracted
  into F.
- `SAFE_PREFIXES` is dead, strictly weaker than the live guard, and sits directly above it looking
  like the guard.
- Residual untrusted search path: `r250-classify.py:72-73` selects the lexicographically first version
  directory under a user-writable plugin cache, unpinned.

---

## Not in doubt — what the fixes DID bind

Fix **(vi)** is genuinely mutation-proof: wiring out `cited_in_window` or `is_structurally_inert` at
the classifier call site kills tests in both directions (4 mutants, all killed). Fix **(v)** catches 5
of 7 constructed scenarios — dropped item, invented item, plain contradicting continuation,
duplicate lead, long-form-only — and correctly does not cry wolf on whitespace/emphasis-only variation.
Fix **(iii)**'s bolded-label repair works and the stated first-match-wins rule reproduces the published
table exactly (59 numbered, 4 non-numbered, 46/5/2/2/2/2, 0 unclassified), independently re-derived.
Fix **(iv)** succeeded at its target: **G3 now resolves end to end** from these files alone.
Blocker-3's `--compare` verdict family is closed. **No fix re-opened a registered deferral**
(D-01…D-12 re-derived, none worsened).

The `§3` bucket arithmetic, the 14-file curation table, the 1,031/44 totals, the 40/35/5 claim
partition and the 9/9 NOT CLAIMED equivalence all reconcile against the artifacts today.

---

## The pattern, stated plainly

Across four rounds the same failure recurs, and it is now better evidenced than any individual defect:
**a fix is verified against the thing that was changed, not against the property the claim names.**

- (i) widened the globs and did not check that the widened surface covers the scope the sentence names.
- (vii) mutated `differences()` and did not check the identity property the test asserts.
- The path-guard test exercised a refusal and did not check *which* refusal.
- Blocker 4 added `raises=` and did not check that `raises=` cannot be widened.
- H4 was repointed and H1, one row above, was not.

That is one mechanism, five instances, four of them introduced by the repair of the previous instance.
It is the report's own subject reproducing inside the report's own production, which is evidence of a
kind a methodology paper can legitimately use — and it is **not** evidence that the mechanisms work.

---

## Two questions for adjudication — NOT settled here

1. **Scope.** The 2026-09-28 16:06 principal ruling descopes the unaccounted-shape guard "to in-scope
   Python/prose sites" — narrowed, not abolished. Must `scan-artifacts.py` glob
   `projects/lung-on-chipsim/**`, and must its verdict fail on unaccounted shapes there? Widening will
   surface substantially more cited files and may reopen E-23, which `#58` closed at the scope reached.
   The reading that makes this gate pass is the narrow one; that is precisely why it is not mine to
   choose.
2. **Whether to continue repairing in this branch**, or to stop and record the pattern above as the
   Stage 1 result. Four rounds of repair have produced four instances of the same mechanism. A fifth
   round is a reasonable decision and so is stopping; both are the principal's call, not the agent's.

Pending that, the branch is **not** PR-ready and no receipt exists.
