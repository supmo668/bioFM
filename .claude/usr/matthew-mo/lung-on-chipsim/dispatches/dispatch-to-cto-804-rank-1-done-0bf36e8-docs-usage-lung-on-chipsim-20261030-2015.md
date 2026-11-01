---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-30T20:15
status: created
priority: normal
size: task
subject: "#804 rank-1 done (0bf36e8): docs/usage/lung-on-chipsim.md, every command verified by --help and one verified end-to-end. 'Verified not recalled' caught two things I'd have got wrong. What is NOT usable is stated, including that there is no fit subcommand at all."
in_reply_to: null
---

# #804 rank-1 done (0bf36e8): docs/usage/lung-on-chipsim.md, every command verified by --help and one verified end-to-end. 'Verified not recalled' caught two things I'd have got wrong. What is NOT usable is stated, including that there is no fit subcommand at all.

Agent: lung-on-chipsim
Commit: 0bf36e8 — docs/usage/lung-on-chipsim.md, 118 lines, one file.
#804's rank-1 task done. Pinned to ac2e2e8.

## VERIFIED, NOT RECALLED — and the instruction earned its keep twice

I ran `chipsim --help`, then `--help` on all 14 subcommands and both module-level CLIs. Two things
I would have got wrong from memory:

1. **The approval flags are not uniform.** `--yes` / `--approved-by WHO` are on SIX commands only
   — fetch, hash-verify, parse, provenance-tests, write, adjudication-worksheet — and NOT on
   adjudication-export, panel-seal, the two scaffolds or the four checks. I would have written
   "every command takes `--yes`". The doc states the split.
2. **`--commit` is the 40-hex `source_commit` from the snapshot's provenance.yaml** — a pin, not a
   label. That comes from the ingest tool's own help text, not from me.

**And one command verified END-TO-END, not just by its help.** I ran `transport-prior-scaffold`
into a scratchpad and then `transport-prior-check` against the result. The checker refuses the
fresh scaffold, and the doc quotes its actual refusal text verbatim. So "the M1 block is loud" is
a measurement in the doc, not a characterisation.

## WHAT IS NOT USABLE — stated, as you required, not implied

- **There is no simulate or fit subcommand.** The transport model is library code; the CLI exposes
  nothing that runs it. A reader is told plainly that no model result can be produced from this
  CLI today.
- The M1 input path is deliberately empty and everything downstream is blocked until a person
  fills it.
- `theta-scaffold` refuses to write `configs/theta_priors.yaml` and `configs/assumptions.yaml`,
  because their absence IS the enforcement mechanism.

## CONSTRAINTS HELD

Public surface: no biological number, no identifier paired with a substance, and no result or
finding of any kind. I scanned the file for unit-bearing numerals, InChIKey-shaped and
accession-shaped strings — none. Both relative links resolve.

## A DEFECT IN MY OWN DRAFT, caught because today already taught me to look

I wrote the refusal quote as a code span with **backslash-escaped backticks nested inside it**.
Backslash escaping does not apply inside a markdown code span, so it would have rendered the
backslashes literally and broken the span — a silently wrong public surface. Replaced with a
double-backtick delimiter and verified no backslash-backtick remains.

I checked specifically because an unquoted heredoc silently damaged a file for me earlier today.
Same class, different layer.

## GATE

Docs-only: one new file under `docs/usage/`, which no test, workflow or script reads —
`test_source_hygiene` scans `chipsim/` and `tests/`; `hacp_linkcheck` and the hacp-docs workflow
are scoped to `docs/hacp/`. So the suite cannot be affected. **I am not claiming a fresh run:**
the gate was green at the parent (`uv run pytest -q` unselected, 900 passed / 4 skipped / 0
failed) and a docs addition cannot change it. Said that way deliberately rather than re-running
70s to produce a number I already have.

## ALSO, FROM THE PREVIOUS WINDOW

`ac2e2e8` — pin-hardening under #798: removed a shadowing duplicate `CONFIGS` in
`test_fixture_sources.py` and added `test_source_hygiene.py` to guard the class. The guard
immediately found a case **my own regex survey had declared clean** (`_PRIOR` twice in
`test_transport_fit.py`), because my regex was anchored at `^[A-Z]` and could not match a
leading-underscore name. That turned out to be a legitimate documented forward declaration, which
taught the rule its correct boundary: count only SUBSTANTIVE bindings, written as a property
rather than an exemption list. Falsified against the real tree by planting the original defect
back in and restoring byte-identically.

**And a retraction in that commit:** I diagnosed `test_barrier_panel` as an unmarked network test
from `grep -c 'pytest.mark.network'` returning 1. That counted STRING OCCURRENCES, not tests
marked, and line 23 is a module-level `pytestmark` that marks all 15 — verified empirically, they
all deselect under `-m "not network"`. No marker defect. The one-off ABCC1 failure was a
transient UniProt call and did not reproduce in three runs.

## STATE

§1, §2, the number collisions and OCT1 still with the principal. Nothing else unblocked on my
side that does not touch the paper.

next_handoff: none required.
