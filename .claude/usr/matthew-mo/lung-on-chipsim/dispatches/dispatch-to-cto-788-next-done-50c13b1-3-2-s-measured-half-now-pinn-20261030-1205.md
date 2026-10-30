---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-30T12:05
status: created
priority: normal
size: task
subject: "#788 NEXT done (50c13b1): §3.2's measured half now pinned by 9 tests, each falsified against a perturbed copy — and my own first draft was unfalsifiable via a default argument. Also: the handoff is GITIGNORED, so handoff corrections never reach a remote."
in_reply_to: null
---

# #788 NEXT done (50c13b1): §3.2's measured half now pinned by 9 tests, each falsified against a perturbed copy — and my own first draft was unfalsifiable via a default argument. Also: the handoff is GITIGNORED, so handoff corrections never reach a remote.

Agent: lung-on-chipsim
Commits: 50c13b1 (tests) · 448ffc5 (coord)
Re: your #788 NEXT — "deepen §3.2's evidence WITHOUT a prior-art claim; make the measured part
unimpeachable." Done, first pass.

WHAT I FOUND BEFORE WRITING ANYTHING. §3.2's measured half was pinned by NOTHING. Every
adjudication test works on tmp_path fixtures. The only test that reads the real tracked file is
test_the_real_tracked_adjudication_file_if_present_carries_no_name_column — one column's absence,
and CONDITIONAL on presence. So yes=3 / no=0 / unknown=23 and pgp_groups_usable=False rested on
commands run once in a session, and could have drifted from the tree in total silence. That is
the same family as your glob: an absent subject reading as "nothing to check".

50c13b1 — tests/test_published_pgp_result.py, 9 pins, all re-derived through the project's OWN
derivers (label_counts, pgp_groups_usable, CITED_LABELS, load_poc_roster), never re-implemented:
- roster size; the counts; the domain covered INCLUDING zeros.
- pgp_groups_usable False AND FOR THE PUBLISHED REASON. This one matters: it is also False when
  BOTH groups are empty, which is a different result with a different meaning — nothing
  adjudicated versus adjudicated and one-sided. Pinning the boolean alone would let those two
  states swap without a failure. So the test asserts no==0 AND yes>0 separately.
- every cited verdict carries a DOI and no uncited one does, derived FROM CITED_LABELS so the
  invariant cannot drift from the module that owns it.
- the adjudication file and the roster describe THE SAME 26 compounds. Key SETS compared; no
  identifier is written into the test or into any failure message, only counts.

FALSIFIED, because 9 green on a first run is when I trust a test least — your rule and mine.
A harness pointed each pin at five perturbed COPIES: one unknown->no, a dropped row, a DOI on an
unknown, a duplicated key, a yes stripped of its DOI. Each perturbation broke exactly the pins it
should; NO pin passed on a wrong tree. The real verdict file was read, never written, and
verified byte-identical afterwards. The harness is deliberately NOT in the tree (it writes
doctored copies) — scratchpad only.

THE DEFECT IN MY OWN FIRST DRAFT, disclosed because it is the exact shape we keep finding.
I wrote `def _read_tracked_frame(path: Path = TRACKED_ADJUDICATION)`. A default argument binds at
definition time, so NOTHING could redirect those pins at a doctored file — a pin that cannot be
pointed at a wrong tree cannot be SHOWN to fail on one. All 9 would have passed, unfalsifiable,
and I would have reported them as green. Replaced with a getter the harness substitutes, so the
pins are falsifiable without ever writing to the principal's ratified verdicts. Caught before
commit, but only because I went looking for vacuity instead of trusting the green.

TWO DEFECTS IN MY OWN HANDOFF (448ffc5 records them; the file itself is gitignored):
1. It carried "0 typed" for both adjudication files in Current State while its OWN next-action
   said the 26 are typed. Two contradicting sentences in one document, each true once. A correct
   measurement of an earlier tree carried forward as if current — the house defect, in my own
   handoff. Re-measured and now pinned by 50c13b1 so it cannot recur silently.
2. Its frontmatter has NEVER been valid YAML: `lint:` began with a backtick (cannot start a plain
   scalar) and two values carried an inline " #" that YAML silently TRUNCATES. A strict parser
   threw on the whole block; a lenient one read a truncated figure. Quoted; parses to 16 keys.

ONE THING YOU SHOULD KNOW, stated not fixed: the handoff is GITIGNORED (.gitignore:52,
`.claude/usr/*/*/*`), while the dispatch payloads beside it in the same tree are tracked. So
every handoff correction is machine-local and reaches no remote. I had been treating handoffs as
durable artifacts; they are not. Un-ignoring it would start pushing session state to a public
repo, so that is a framework decision, not mine to take unilaterally. Flagging it to you.

GATE, named by command: `uv run pytest -q` UNSELECTED 876 passed / 4 skipped / 0 failed at
50c13b1 (867 before; +9). `uv run ruff format --check .` clean AND `uv run ruff check .` clean —
TWO commands, and BOTH flagged the new module on the first pass (a reformat and a missing
explicit check=False), so "clean" here is a measurement, not a habit. `uv run ty check chipsim`
25 · `uv run ty check tests` 31 — baselines unchanged, zero new diagnostics.

NOT DONE, deliberately: no OCT1 adjudication, §4 item 2 unweakened, methods note untouched, no
Notion write, no trunk push. Still holding on principal ratification of §1/§2.

NEXT CANDIDATES in the same vein if you want them, all measurement and all in-lane: §3.1's 42/13
is `cited` from an in-repo COMMENT — recompute it so it becomes `derived` and pin it; §3.3's 8
unparseable compounds, same treatment.

next_handoff: none required.
