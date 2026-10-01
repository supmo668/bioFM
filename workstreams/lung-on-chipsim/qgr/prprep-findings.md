# PR-prep boundary gate — consolidated findings. VERDICT: FAIL. No receipt signed.

Base `origin/main` → HEAD `8dcf9fd`. Scope: the whole branch diff — 413 commits, 305 files,
+48,882/−289. Hash A `11f21582fcd221c3bb9adf1ecd8c927ef1dcab8a968dc9fd81d4c2a4226712dd`.
Roster: reviewer-code, reviewer-security, reviewer-design, reviewer-test, each on its own
`git archive` snapshot, plus my own pass. Register of 12 prior deferrals supplied to each.

**No QGR receipt is signed.** A receipt is a completion claim and this gate did not pass.
**Nothing is pushed. Nothing lands.**

## The bracket held — and I verified that independently, because the code saying so has no test

`bracket.py --compare` reported HELD over 305 gated files at content `94ebd946`. reviewer-test then
proved **by mutation** that replacing `differences(before, now)` with `[], []` makes that same
command print `bracket HELD` and exit 0 **no matter what changed**, with a fully green suite — the
`--compare` branch is executed by no test and not by `--self-test` either.

So "it said HELD" was not accepted as evidence. I recomputed the content digest from the pinned file
set by an independent route: `94ebd946ea40fa94…`, byte-identical to the capture. I then ran a
falsification probe — replacing one pinned file's bytes — and confirmed the recomputation diverges.
**The bracket held, and the check that says so can distinguish a change.** Both halves were needed.

## Convergence — what multiple independent readers found

| defect | found by | status |
|---|---|---|
| **Claim H4 cites a scan record that omits the documents making the claim.** "Every artifact was scanned … 10 files" cites `scan-artifacts-1f0811b.json`, which does not contain `stage1-methods.md` (the file asserting it), `stage1-short-form.md`, the design spec, or `traceability-check.py`. Two strictly newer records sit beside it; the current glob yields 14. | **all four reviewers + my own pass** | reproduced |
| Three evidence scripts write into the tracked tree with no `--no-write`; re-running one inside a bracketed gate voids the receipt. | security, code, test | reproduced |
| The traceability gate's checks are far narrower than its claims (path check silent on 22 of 40 rows; blind to any section beyond H; CUT-excusal is a substring test that "executed" satisfies). | design, code, test | reproduced |
| `route-distribution.py`'s "identity that makes the table checkable" asserts are tautologies — one increment per row compared against the row count. | design, code, test | reproduced |
| The H4 sentence names three zero-valued fields and omits the one non-zero field, 25 lines above the document stating the rule adopted from exactly that defect. | design, code | reproduced |
| `n - qual` subtracts decoded YAML sites from raw occurrences and can go negative, silently reducing the published out-of-guard total. | security, code | reproduced |

## CRITICAL

- **The verdict mechanism is untested.** `bracket.py --compare` — the code deciding whether a
  reviewer mutated the gated tree — has no test and no self-test coverage. A one-line mutation makes
  it always report HELD. Every gate receipt in this workstream rests on it.
- **Strict xfail swallows any exception.** A realistic input-sanitisation guard added to
  `accession_structure_tuples` makes all nine parametrised cases raise *before* reaching the
  assertion that witnesses the registered gate-6 divergence — pytest counts the raise as the
  expected failure and the file reports **36 passed, 9 xfailed, green**. The finding stops being
  exercised and nothing says so.
- **130 `.claude/usr/**` files are additions in this diff.** Filenames alone carry the operator
  username and live process IDs; two announce, in their titles, an internal content incident and a
  fail-open disclosure of the accession guard. Their contents were in no reviewer's snapshot and are
  matched by no scan glob in this branch. **Landing publishes them.**
- **`configs/poc_compounds.yaml` carries 26 name↔structure associations with a source DOI and no
  retrieval date.** The project's own predicate proves they are ungoverned: with no retrieval key
  they fall to out-of-guard-scope, the bucket the guard does not enforce. The sibling
  `label_structure_reference.yaml` clears the same bar, so the standard is reachable. The paper
  diagnoses this exact shape in its limitations while the file ships.

## HIGH — the paper's claims against its artifacts

- `could_not_scan = 0` is computed from a different quantity than its name: `cns` counts only read
  errors and never consults `ShapeReport.could_not_scan`. **Live instance** — the tracked zero-length
  `configs/.gitkeep` is skipped by `if not n: continue` and never reaches a bucket. Two paper
  sentences assert a zero for a state that was never measured, and ruling #455 makes could-not-scan
  *fail* the gate.
- **The row extractor drops rows silently.** A row with a **bolded** label — this log's own house
  style — is not extracted, and the output is byte-identical: still 59 revisions, still 0
  UNCLASSIFIED, still no `inferred` category. F2 and F6 both cite this instrument, and **a row marked
  `inferred` would be invisible to the very check F6 relies on.**
- **A short-form limitation can contradict the long form and the gate signs it.** Check 4 compares
  only text before the first period; rewriting the short form's 7th item to assert the *opposite* of
  the long form's still reports 9/9, 0 failures, PASS.
- **Approval-log citations use two incompatible numbering schemes inside one sentence.** "Row 54/55"
  resolve only under physical ordering, "row 58" only under the `#` column. A referee following the
  visible numbering lands on the r2.50 sign, so **the paper's strongest integrity claim — that the
  stopping rule was fixed before the gate ran — does not resolve.** The register inherits it.
- **Buckets W and C are never exercised through the classifier.** Wiring either out leaves the suite
  green, while the published `{W:12, F:46, C:19, N:62}` split is cited by E3 and E5.
- **The digest test is vacuous for branches, and stash and status have no regression at all.**
  `"main" not in metadata["branches"]` is element equality against a list whose entries are `"* main"`
  — it cannot fail. Making branches, stash and status all verbatim leaves `test_bracket.py` green;
  stash subjects and untracked filenames are the two leak paths named as the gate-8 breach.
- Three committed bracket records (gate 6/7/8) land with the absolute host root, the username and
  other workstreams' stash subjects — 10, 12 and 14 `/Users/` occurrences. The pre-write self-check
  passed them because it runs only shape detectors, which have no notion of a host path.
- `gated_files` and `per_file` keys are never digested, so private escalation paths land verbatim in
  every record — including the one this gate produced.
- Five files from `chipsim-lbm-audit`, a different workstream, are in this diff and were reviewed by
  nothing.
- The short form and the methods abstract share a 26-word verbatim run and 26% of 7-grams. **I can
  state the direction the reviewer could only infer: I wrote the short form first, from the claims
  list, and the abstract afterwards, drawing on it.** The short form's header claim is true; the
  abstract is the derived artifact, and design spec §2 forbids either direction.

## My own findings

- **OWN-1.** My review script re-implemented the harness's bucketing and diverged, over-counting N by
  104 and reporting the cited record as STALE when it was consistent. Design rule 1 —
  *delegate, never re-implement* — violated by me, inside a review hunting that exact defect. It
  failed loudly rather than quietly, which is the safe direction, but a reader trusting my first
  output would have chased a phantom.
- **OWN-2.** The scan record cited by H4 predates the register and the later paper edits. Confirmed
  independently by all four reviewers.
- **OWN-3, a regression I introduced.** Replacing the hardcoded `diff-hash` path with an environment
  variable created an untrusted-search-path execution vector: the value is used directly as an
  executable with no validation, defaulting to a bare name resolved through `PATH`. I removed a
  host-path leak and introduced arbitrary code execution. Related: if `diff-hash` merely *fails*,
  `file_hash` returns `""` and the entire P1 bucket empties silently, changing every published number.

## Checked and found SOUND

- The quantitative spine reproduces: the route distribution recounted independently gives exactly
  46/5/2/2/2/2 of 59; bucket arithmetic, the curation table, the claim-row partition and the
  NOT CLAIMED equivalence all reproduce from the artifacts.
- The five CUT claims are genuinely cut, none softened or cited as support.
- "139 of 139" never appears unqualified — all three occurrences carry their qualification.
- Model claims resolve to real symbols at real call sites; `_require_sourced_theta` guards the entry
  point.
- `MARKER_WINDOW_LINES` window arithmetic is off-by-one clean.
- The merge of 51 commits broke nothing: 1257 passed / 4 skipped / 9 xfailed, ruff clean.
- `paper/*.md` carries no shaped content and none reads as cited.

## Why this fails rather than being repaired now

Most of the paper-side findings are one-line repairs against evidence already committed. But the
CRITICAL items are not: two concern **what becomes public on landing**, and are the principal's
decision, not a code fix. And the verdict mechanism being untested means the receipt this gate would
sign rests on a check that cannot currently fail.

Fixing the cheap ones to make the gate quieter, while those stand, is the family.
