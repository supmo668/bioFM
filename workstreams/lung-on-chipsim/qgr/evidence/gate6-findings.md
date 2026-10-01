# Gate 6 findings — E-23 range `699e495..14d80cf`

**Verdict: FAIL** (dispatch #409). Nothing hashed, no Hash E, no receipt, nothing pushed.

Four reviewers: code, test, security, design, each in its own worktree. **Every finding recorded here
was re-measured by me before it entered the verdict**; where a reviewer's figure differed from mine,
mine is the one recorded and the difference is named. Values are described by SHAPE only; nothing was
looked up, compared against an adjacent literal, or reproduced.

Isolation: content digest `3201f2cfc8b76469` before and after, 16 files, zero per-file differences —
no reviewer mutated a gated file. Details and the metadata delta in `gate6-bracket.md`.

---

## Full-suite survivors — any one of these fails the gate

Measured against the complete five-axis corpus (7,320,676 strings), with the reason nothing could
see each one measured alongside it.

| # | mutant | survives | why nothing sees it (measured) |
| --- | --- | --- | --- |
| S1 | key half + a WIDTH-2 trailing guard `(?![A-Z][A-Z])`, and its leading twin | whole corpus | the two exhaustive code-point axes append exactly ONE code point, so at end-of-string a width-2 lookahead always succeeds; `RIGHT_CONTEXTS` has ZERO two-uppercase entries; every museum entry in this family is width 1 |
| S2 | call site `finditer(line)` → `finditer(line[:200])`, `.pattern` and `.flags` byte-identical | whole suite | longest first line in the 96,900-document seam corpus is **49** chars, zero over 200; longest string in any other axis is **69**. Any ceiling ≥ 70 is invisible |
| S3 | InChI half + an uppercase-body guard | whole corpus and every E-23 test | the invented-body alphabet has NO ASCII uppercase; 400 generated bodies, none starts uppercase; the fixed probe body is the word `placeholder`; there is **no code-point × InChI-BODY axis** — the code-point axis pairs code points with a fresh KEY |
| S4 | InChI body length ceiling (`\S{1,40}`) | all reachable files | longest reachable body in the corpus is ~35 chars |

**S3 is the structurally important one.** A real standard InChI's body opens with its uppercase
formula layer, so S3 misses every real structure of that form. The only things in the repository that
kill it are the out-of-range fixtures holding REAL identifiers — precisely the fixtures clause (i)
directs us to replace with invented ones. **Applying (i) as written would make S3 a full-suite
survivor.** The invented-probe discipline is what blinded the oracle, and the safety net is what the
same clause condemns. Correct order: grow the body axis FIRST, then apply (i). That interaction is
not in the clause and should be.

---

## The (d) axis is blind by construction — my defect

(d) exists because "the pin and the oracle bind a CONSTANT; bind the loop". Its expectation is
`reference_spans(first_line)` — the reference evaluated on the call site's OWN first line — so the one
decision the reference does not share is the one the expectation was reshaped to match.

**Measured: 0 of 96,900 seam documents distinguish `splitlines()` from splitting on LF.** The axis
cannot fail on the defect it exists to catch. Same shape as r2.45(d)'s circularity (a fixture asking
the implementation), one detector over.

Five further call-site mutants survive because the axis carries ONE structure and ONE accession per
document by construction: `near[0]`→`near[-1]`; first-accession-per-line only; dedup on the accession
alone (two forms); one-structure-per-line. The axis's own comment block names the pattern-width gap
and none of these.

---

## Production defects, reproduced

| id | defect | measurement |
| --- | --- | --- |
| P1 | `ledger_tuple_hits` hardcodes a UTF-8 decode while the readability half is UTF-16-aware, so re-saving the ledger in UTF-16 turns the association control OFF | same document: utf-8 → **1** tuple; utf-16 (BOM) → **0**; utf-16-le+BOM → **0**; routed through the real decoder → **1** in all three |
| P2 | `splitlines()` breaks on nine code points besides LF (U+000B, U+000C, U+000D, U+001C, U+001D, U+001E, U+0085, U+2028, U+2029) and the ±2-line window is measured in those units | three vertical tabs, ONE physical line, ZERO newlines → 4 "lines" apart → **0** associations. Generated zero-newline documents: **1,775 of 3,000** associations lost |
| P3 | the reported line number is a `splitlines` index, so the operator is pointed at the wrong line | same root cause as P2 |
| P4 | the ±2-line window misses the ordinary serialisation | `json.dumps(indent=2)` 9 lines → **0**; a 5-line YAML mapping → **0**; compact JSON and a TSV row → 1 |
| P5 | the dispatch waiver removes a file from the accession half AND hands it to nothing — it is not in the set the association loop iterates | dispatch path with both on one line → excluded, **0** hits, **0** files read; identical bytes at `docs/` → 1 hit |
| P6 | parquet's missing-reader path still escapes untranslated as exit 1 with no file named — the exact condition (h) was ruled to remove, in the one of two readers not reparented | a bare `ImportError` reaches the composition root; `errors.py` describes "a container with no reader installed" in the singular and covers both |
| P7 | (h)'s new route interpolates the path RAW, so a tracked filename can forge a standalone report line — r2.28's defect on the route (h) created | a path carrying newlines produced a forged line at column 0 in the exit-3 report. The comment three lines below claims this route escapes via `render_path`; it does not |

(h) is otherwise **well bound for HDF5**: four exception-hierarchy mutants were each killed by the
binding test — reverting the parent class, reparenting to the wrong class, deleting the propagating
re-raise, and dropping the path from the message.

---

## Claims wider than their checks

| id | claim | what actually backs it |
| --- | --- | --- |
| C1 | `_one_edit_near_misses`: "closes the key SHAPE … ASCII uppercase only" | closed over **7 sampled substitute characters**, not the code-point space. Four mutants widening a segment's letter class by one non-ASCII character survive all 7,320,676 strings; É, an en dash and digit-widening are killed. It is r2.47b's **retracted** "closed" claim re-introduced on E-23's own token axis. Survivors over-match, so fail-closed: a false sentence, not an open leak |
| C2 | the clause cites `qgr/evidence/e23-draft-measure.py` as the harness that measured every signed figure | the file has **no driver**: `disagreements`, `any_dis` and its museum are defined and never called; it prints one line, exits 0, and emits a SyntaxWarning. The figures are true — reproduced from the shipped tests — so this is a citation defect |
| C3 | signed "museum 17 of 18 killed" | shipped museum is 16 + 1 dropped = 17; the harness has 18. Two harness entries absent with no recorded reason, one new. One of the two silently dropped is the digit-widening entry — the only artefact pointing at the key's internal-alphabet dimension |
| C4 | the reference reads as distinguishing "`S/` present but body empty" from "no `S`, then `/`" | that fall-through is **provably dead**: if `S/` matched at `j` then `/` cannot match at `j`. Same species as E-22's two dead reference clauses |
| C5 | test name "…really IS equivalent and not merely unkilled" | the body asserts corpus non-rejection, i.e. exactly "merely unkilled". The proof in its docstring is sound and checkable, and is not checked |
| C6 | test name "…agrees with the spec sentence everywhere" | agreement over a generated corpus, while the clause records three open dimensions three lines away. The E-22 sibling scopes its name correctly; E-23 dropped the suffix in the overclaiming direction |
| C7 | the clause's CLASS SWEEP: "the other 9 are anchored validators, not content detectors" | false for three of them — the accession detector plus two unanchored 64-hex content detectors. The narrow claim (no `\b` remains anywhere in the package) does hold |
| C8 | two tests named for "the pattern" | compile their own `\s` / `[A-Z]` and never reference the shipped pattern; they measure a property of CPython's `re` |
| C9 | "a hyphen" on both sides means U+002D only, so no corpus can expose the choice | a shared error the differential is blind to by construction. The file's prose classifies an en-dashed key as a near-miss that must not match — a ruling nobody took |
| C10 | the bracket's silence means the tree was untouched | it reported `bracket HELD`, exit 0, in a directory that is **not a git repository**. Fixed in `4a05573`, eight self-test directions now. Separately it exits 1 for a benign metadata delta, which is reported and NOT fixed because it changes the gate's decision rule |

---

## Content constraint — counted by shape only

Eight structure-shaped tokens outside the documented invented-probe convention, in three tracked
files. Nothing looked up, nothing compared against an adjacent literal, no value reproduced:

| file | lines |
| --- | --- |
| `workstreams/lung-on-chipsim/plan/build-plan.md` | 1230, 1262 |
| `workstreams/lung-on-chipsim/plan/plan-approval-log.md` | 24, 27 |
| `projects/lung-on-chipsim/tests/test_record_content_guard.py` | 219, 278 |

Reviewers independently name further sites in `test_record_content_guard.py`,
`test_accession_pattern_matrix.py` and `test_merge_report_record_content.py`.

`build-plan.md` is the file that CARRIES clause (i) — about thirty lines from tokens that violate it.
The values are pre-existing; what this range introduces is the unsatisfied clause. **Untouched**:
editing signed plan text would forge its hash, and per S3 two of those fixtures are the only thing
killing the uppercase-body mutant.

**Files the range ADDS are clean**: 0 non-probe tokens. Every probe is invented by construction with
a stated comment — repeated-letter keys, a seeded generator whose seed prints before the corpus,
placeholder bodies, and the documented all-zeros accession assembled from fragments.

---

## The generalisation worth keeping

Six gates have failed on "a claim wider than the check behind it". Gate 6 adds a variant: **three of
the four survivors are invisible BECAUSE OF a discipline the clause imposes.** Invented probes keep
real identifiers out of the tree, and they are drawn from alphabets narrow enough that the oracle
never explores the shapes real identifiers have. The generated-axis design did not fail here; the
GENERATORS did, each sampling the space its author imagined while the prose says "exhausted".

**For every axis, state the alphabet and the width, and require a mutant at the edge of each.**
Width-1 contexts invited a width-2 guard. A lowercase-only body alphabet invited an uppercase-body
guard. A 49-character corpus invited a 200-column ceiling. In each case the missing test was one line
from the one that was written.
