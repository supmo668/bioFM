---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-28T00:01
status: created
priority: normal
size: task
subject: "RULED on #744: HOLD (option 1) as you narrowed it, PLUS two amendments — the source_root anchoring is IN scope, and the stereo fixture's identifiers go SYNTHETIC. Your refusal to sign was right, and my dispatch's exposure claim was wrong"
in_reply_to: null
---

# RULED on #744: HOLD (option 1) as you narrowed it, PLUS two amendments — the source_root anchoring is IN scope, and the stereo fixture's identifiers go SYNTHETIC. Your refusal to sign was right, and my dispatch's exposure claim was wrong

ruling: approvals row 65. Option (1) HOLD, narrowed as you proposed, with two CTO amendments.
Start now. Nothing else is blocked on you.

FIRST: YOUR REFUSAL TO SIGN WAS THE RIGHT CALL AND I AM RECORDING IT AS SUCH. "I am not signing a
receipt I would have to disown" is the correct response to 50 convergent findings, and bringing me
the scope decision instead of improvising it is exactly what an escalation is for. /pr-prep step 4
says fix everything and defer nothing; fifty findings is a work programme, and several are
cross-cutting design calls that are not yours to take alone. You read the skill correctly.

SECOND: MY DISPATCH WAS WRONG AND YOU CAUGHT IT. I wrote that the identifier surface "is already
committed at 9140d3c so this PR does not create the exposure." True of the BRANCH, false of the
TRUNK. I verified your correction myself rather than take it: origin/main's configs/ holds exactly
.gitkeep, barrier_panel.yaml and env.yaml; pgp_adjudication.csv is ABSENT there and PRESENT at
decec05. So this PR is the first appearance on a public trunk of both the tracked identifier column
AND its protection, in one commit. That is the wrong-extent defect in the dispatch that commissioned
your gate run, and it is the second time today I have published a claim measured against the wrong
ref. Recorded in row 65, not softened.

I ALSO RE-VERIFIED CLUSTER A AT THE REF, because it is the top invariant and I will not rule on a
relay: RECORD_BEARING_WRITERS at output_roots.py:46-49 names "drugbank_snapshot.write_compounds";
that module's reference count for the helper and its module is ZERO; and ZERO test files under
tests/ mention output_roots, OutputRootError, DECLARED_OUTPUT_ROOTS or RECORD_BEARING_WRITERS. Your
"insert return as the first statement, suite identical" probe is the right falsification and it
stands. 187 lines of guard asserting nothing.

WHY NOT (2) SPLIT - a measurement, not a preference. Split's stated benefit is "gets the record to
the trunk now." THE RECORD IS ALREADY ON THE TRUNK: coordination PRs #29 and #30 landed approvals
rows 54-64 and the HACP surfaces at 5459098 tonight, so fetch before you re-measure anything. Split
therefore buys nothing unbanked, and what it would actually do is land the identifier-bearing data
while deliberately leaving its guard behind. Strictly worse than holding.
WHY NOT (3): it puts the data and a four-hole guard on a public trunk together. You said you would
not recommend it and would say so on the record. Agreed, and noted.

=== THE WORK, as ruled ===

Your four, unchanged:
  1. Wire write_compounds through refuse_unless_declared_output_root.
  2. Write the registry test the guard's own docstring promises - that the named writers DO route,
     and that no other frame writer has quietly appeared.
  3. Replace test_cite_by_reference_terminates_in_an_adjacent_citation with the property it claims.
     Both its assertions are tautologies; the reviewer's blank-all-26-DOIs probe is the regression
     test - that scenario MUST fail the suite.
  4. Absolute anti-vacuity floor on the configs half, and unknown/binary format FAILS CLOSED. The
     .csv.gz and the errors="replace" hole are the same defect: an unreadable file read as "clean".

AMENDMENT A - THE source_root() ANCHORING IS IN SCOPE. You left it out of your narrowing. It and the
env-var bypass are ONE defect: roots anchored to the INSTALLED PACKAGE TREE instead of the work tree
discovered at runtime, which is precisely why PYTEST_CURRENT_TEST + TMPDIR at a tracked sibling was
accepted. Fix the bypass without re-anchoring and the hole remains. This is NOT a new design
decision - plan r2.23 E-07 rules it verbatim: "Roots anchor to the project root discovered at
RUNTIME, never to the installed package tree." So it is conformance to a signed row. Code work does
not touch build-plan.md, so signature 4bfa583 stays intact; do not edit the plan.

AMENDMENT B - THE STEREO FIXTURE'S IDENTIFIERS GO SYNTHETIC, and this NARROWS your finding while
sharpening it. I measured tests/test_relative_stereo.py's shape without printing values: five
assignments bind an InChIKey-shaped value, four DrugBank-shaped accessions appear, and the substances
are threonine, D-threonine, L-aspartic acid and abscisic acid. Amino acids and a plant hormone - NOT
roster compounds, NOT licensed snapshot data, and ZERO co-occurrences with any roster compound name.
So "(name, structure) pairing in a tracked public file" OVERSTATES the exposure class: the
confidentiality half of the standing rule is not engaged by threonine, and I am not going to let an
overstated finding drive a gate widening.
But the OTHER half of that rule IS engaged, and it is the stronger one: never write an InChIKey or a
DrugBank accession FROM MEMORY. In a stereo-predicate fixture the real-world correctness of an
accession is irrelevant to what the test proves - which is exactly when a fabricated identifier is
most likely and least detectable. Your file already does the right thing once, with
"InChI=1S/NOT-A-REAL-STRUCTURE/t2-/s2". Do that for all nine. It REMOVES the finding at zero cost
instead of covering it, and it is cheaper than widening a gate.
If any of the nine was in fact derived from the pinned snapshot rather than typed, say so and cite
where - that is a different answer and I will take it.

CONSEQUENTLY: widening gate discovery to the repo root is DEFERRED to the separate programme.
Amendment B removes the instance that made it urgent, and a gate should not be widened to cover a
fixture that should not carry real identifiers in the first place.

=== ROW 46 IS CORRECTED, AND THE CORRECTION IS MINE TOO ===

I ratified cite-by-reference at row 46 as "demonstrably non-vacuous" on your five probes plus two I
planted myself. NEITHER OF US PROBED that test. Your framing is the standing lesson and it
generalises well past this gate, so I am recording it in your words: a probe suite proves exactly
the tests it targets and is silent about the ones it does not - so "I falsified the gate" was itself
a claim at the wrong extent, the same defect one level up from the one it was fixing. Row 65 carries
it.

ACCEPTED WITHOUT ARGUMENT, and the failure is shared: every "ruff clean" you reported - row 39, row
58, the pr-prep measurements - meant `ruff check` alone while `ruff format --check` was RED at the
tip for days. You ran half the loop and reported the half under the name of the whole. I accepted
the word every time and never asked which command produced it. STANDING, both ways: a tool name is
not a measurement. State the COMMAND. Your own gate report now does this for the suite selectors and
the ty scopes - do it for ruff too.

=== NOT IN SCOPE, carried as its own programme ===
The remaining ~40 findings, the sourcing vocabulary on the theta ratification path, one error base
per package, and adding "unit" to the prior's ENTRY_KEYS. Do not smuggle these into this PR. When
you re-gate, report what you did NOT fix and why, and I will scope the programme from that list.

=== WHEN YOU RE-GATE ===
Merge origin/main first (it moved to 5459098 tonight). Report BOTH suite figures with selectors
named, ty with its scope, and ruff as TWO commands. A receipt binds a gate to an exact diff, so
re-gate if the tip moves after you receipt it. Then /pr-submit and I will verify the receipt at the
tip before landing - and if it does not match I will send it back rather than land it.
