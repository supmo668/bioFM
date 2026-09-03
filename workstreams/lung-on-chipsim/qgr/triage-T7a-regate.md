# QGR Stage-2 triage — T7a re-gate

Disposition for every finding in `findings-T7a-regate.md`. **29 findings, 28
accepted and fixed, 1 INFO requiring no change, 0 deferred.**

Every fix that changes behaviour was mutation-verified: the guard was removed and
the named test had to go RED. Mutations that survived are recorded as such, with
what I changed in response — a fix I could not kill is a fix I have not shown to
work.

## Code review

| # | Disposition | Fix + verification |
|---|---|---|
| 1 | ACCEPT | `render_panel_ratification` now calls `load_ratified_panel` and renders three states (verified / PRESENT BUT FAILS VERIFICATION / ABSENT). |
| 2 | ACCEPT | `ratified = doc.get("ratified") is True and bool(by)`. An unattributable ratification renders NOT RATIFIED, matching what every other component does with it. |
| 3 | ACCEPT | `_configs_boundary` requires `root_real in configs_real.parents` — strictly inside. Equality is never legitimate for `configs/`. New test: `test_configs_symlinked_to_the_project_root_itself_is_refused`. |
| 4 | ACCEPT | `_resolve_seed` uses the same `_configs_boundary` helper, so the two call sites cannot drift. |
| 5 | ACCEPT | Added an `else:` arm raising for any `*.y[a]ml` entry that is neither a directory nor a regular file; `os.open` now takes `O_NONBLOCK` so `fstat` runs before any blocking wait. New test: `test_a_fifo_named_like_a_config_is_refused_not_skipped`. |
| 6 | ACCEPT | `_read_confirmation` selects with a 120 s timeout and fails closed. **Mutation: `if not ready:` → `if False:` — the test HUNG rather than failing, which is the kill: without the guard it blocks forever on an empty pipe.** |
| 7 | ACCEPT | `RuntimeError` for non-mapping/unreadable panels; absent-`ratified` and `ratified: false` render as distinct sentences. |
| 8 | ACCEPT | Corrected, and the retraction left visible rather than silently deleted. New test greps the package for the false claim — mutation-killed. Note the retraction *paraphrases* the old wording rather than quoting it, so the grep needs no exemption clause (see the note under T3 about loose matchers). |
| 9 | ACCEPT | Message now says the panel was not modified and the attempt **is** journalled. Mutation-killed. |
| 10 | ACCEPT | Prompt to stderr. Mutation-killed. |
| 11 | ACCEPT | Split into target-missing vs target-exists-but-not-regular, with separate messages. |
| 12 | ACCEPT | `panel` has no default; `None` renders an explicit "Not supplied" notice. **First mutation SURVIVED** — removing the default is not enough on its own, because no test asserted the `None` branch renders anything. Added `test_omitting_the_panel_renders_a_visible_gap_not_a_silent_one`; now killed. Wiring remains M0c's, and the test is what stands in for the missing production caller. |
| 13 | ACCEPT | Backticks in `ratified_by` neutralised before interpolation. |
| 14 | ACCEPT | A seal that is not 64 lowercase hex renders `**Seal: MALFORMED**` with its actual length, and no ellipsis. Verification alone did not fix this: the FAILS-VERIFICATION branch still printed `sealed[:16]…`, so the card compared two things only one of which existed. Mutation-killed across 4 parametrised cases. |
| 15 | NO CHANGE | INFO. Reviewer's ruling accepted: `strip()` is load-bearing, `lower()` costs nothing against a published literal. Added `test_the_confirmation_is_case_insensitive` so the behaviour the ruling endorses is pinned rather than incidental (T11). |

## Test review

| # | Disposition | Fix + verification |
|---|---|---|
| T1 | ACCEPT | Docstring rewritten to record that half (b) IS load-bearing and that the earlier "appears REDUNDANT" conclusion was wrong. Fixture no longer uses `env.yaml`; `match=` is the half-(b) message specifically. Re-verified: the mutant now dies. |
| T2 | ACCEPT | Rewritten to scan **rendered output** for polarity, sharing one scanner with the source test. Mutation A (reviewer's overclaiming card) initially **SURVIVED** — the pattern list covered the verb `proves` but not the noun `proof`, so "the seal is proof a human checked every accession" passed. Added the noun form; both the overclaim and the negation-flip are now killed. |
| T3 | ACCEPT | `normalize()` closes the `" "` seam. The reviewer's exact bypass (an overclaim split across a concatenation) is now killed. This is also why #8's grep paraphrases instead of quoting: a matcher loose enough to need an exemption clause is the same bug in a new place. |
| T4 | ACCEPT | The journal redirect is now an **autouse** fixture — a protection that must be requested is one that will eventually not be. The 86 polluted records were deleted (all 86 confirmed test-authored by argv; gitignored, never committed) and a full suite run now produces zero. |
| T5 | ACCEPT | Asserts `after != before` and that the digest equals `panel_digest(doc, panel)`. |
| T6 | ACCEPT | `_tree_snapshot` compares the whole directory, catching restore-in-place, sidecars and leftovers. `journal/` is excluded because a refused attempt *does* write there by design — and `_journal_records` asserts that positively, so neither half of "what may change" is waived. |
| T7 | ACCEPT | `TypeError` added to the except tuple. Mutation-killed. |
| T8 | ACCEPT | **Mutation initially SURVIVED.** Cause: the handler was written out twice and my test reaches only the non-selectable arm. Factored into one `_readline_or_empty()`. Two copies of a fail-closed rule are two places it can independently stop being fail-closed. Now killed. |
| T9 | ACCEPT | Both refusal tests assert `"confirmation not given"` in stderr, so they cannot silently pass on the TTY gate. |
| T10 | ACCEPT | `_FakeStdin` default is `""`; the TTY test passes `answer="seal\n"` explicitly and its docstring says it clears both gates. |
| T11 | ACCEPT | See #15. |
| T12 | ACCEPT | Case-insensitive, asserting the semantic pair (status token + reason). |
| T13 | ACCEPT | Same as #12. |
| T14 | ACCEPT | **First test SURVIVED the mutant** — it linked outside the project root, which both bounds refuse. Rewritten to the discriminating case (`configs/linked -> proj/deploy`: outside `configs/`, inside the root) and asserts on the path the refusal NAMES — the walk names the directory, the file gate names the file. Now killed. Also fixed a stale message this exposed: the refusal said "outside the project root {root_real}" while `root_real` is `configs/`, so it told operators that `configs/` is the project root. |

## Checks

| Check | Result |
|---|---|
| Format (`ruff format`) | clean, 39 files |
| Lint (`ruff check`) | All checks passed |
| Typecheck | **N/A — no typechecker configured** for this project (`mypy` is not in the environment). Recorded as absent, not as passing. |
| Tests | **419 passed, 7 skipped, 0 failed** |
| Mutation sweep | 9 mutants, 9 killed, 0 survivors (2 survived on first attempt and were fixed — see #12 and T8) |
| Journal pollution | 0 records after a full suite run |

---

## Re-gate over the bumped tip (`f0bb4c1`) — what this second signature does and does not attest

The CTO landed `framework.version` 0.2.0 → 0.3.0 **ahead** of the gate this time,
to break a documented deadlock: `pr-create` requires both a bumped version and a
receipt matching current code, while the skill's own Step 4 → Step 5 order bumps
*after* the gate and so invalidates the receipt it then demands. With the bump
behind the gate, nothing mutates between signing and landing.

**No new review was run, and this receipt does not claim one.** The delta from
the gated tip is a single line of `agency.yaml`, verified by `git diff efb5c93
f0bb4c1`:

    -  version: "0.2.0"
    +  version: "0.3.0"

No Python changed. Re-dispatching four reviewers over a byte-identical codebase
would produce findings indistinguishable from the ones already in this file while
consuming a full review cycle, and a second identical Stage-1 pass reported as
new work would inflate what the receipt appears to cover.

So **Hash B is unchanged, deliberately.** The findings document is the same
document because the findings are the same findings. Rewriting it to obtain a
fresh digest would be manufacturing distinctness, which is the specific
dishonesty the A/B/C/E format exists to prevent — a receipt is worth exactly what
its hashes are computed over, and a hash that moved because I edited prose is a
hash that attests to nothing.

**Hash C moves, legitimately**, because this section is real new content: it
records a decision (not to re-review) and the verification below.

**What WAS re-run, on the bumped tip, in this session:**

| Check | Result on `f0bb4c1` |
|---|---|
| `ruff format --check` | 39 files already formatted |
| `ruff check` | All checks passed |
| `pytest` | **419 passed, 7 skipped, 0 failed** |
| `diff-hash --base origin/main` | `679ee2c`, 178 files — matches the CTO's `pr-create` reading exactly |

One note on that last row, because it nearly went wrong: the first attempt
returned `92b37f0` over 81 files. The shell was still inside
`projects/lung-on-chipsim` from the test run, so `diff-hash` scoped the diff to
that subdirectory. A hash computed from the wrong working directory looks exactly
like a legitimate hash — same shape, same tool, no error — and would have been
signed into a receipt attesting to a subset of the change. It was caught only
because the file count moved. Re-run from the repository root it returns
`679ee2c`, independently matching the value the CTO's blocked `pr-create`
reported, which is what makes it a cross-check rather than my own arithmetic
agreeing with itself.

**Hash A for this receipt is `cd36fc0`** — the previously gated state. That is
literally the artifact entering this re-gate, and the A→E diff is the one-line
bump above: auditable in a single command, by anyone, without trusting this file.
