---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-28T00:15
status: created
priority: normal
size: task
subject: "Row 65: items 1-4 BUILT AND FALSIFIED (3abff57, 90cca8e) — the guard now guards with a 12-test registry (AST-discovered, not hand-listed), and all FOUR previously-green gate holes now fail. 864 passed. BOTH amendments are blocked on rulings, not effort: (A) pipeline.project_root() is CHIPSIM_PROJECT_ROOT-overridable and self-documents as 'a JOURNAL DESTINATION AND NOTHING ELSE', so anchoring the guard there is a WORSE bypass than the one we are fixing — need A1 work-tree root / A2 fix-overlap-only / A3; (B) the nine identifiers are PINNED EXPECTED OUTPUTS of canonicalize() asserted against RDKit, so synthetic values either turn the tests RED or make them assert the implementation against itself — the tautology class from item 3. Also disclosed: THREE of my four probes today were broken in a way that produced a PASS."
in_reply_to: null
---

# Row 65: items 1-4 BUILT AND FALSIFIED (3abff57, 90cca8e) — the guard now guards with a 12-test registry (AST-discovered, not hand-listed), and all FOUR previously-green gate holes now fail. 864 passed. BOTH amendments are blocked on rulings, not effort: (A) pipeline.project_root() is CHIPSIM_PROJECT_ROOT-overridable and self-documents as 'a JOURNAL DESTINATION AND NOTHING ELSE', so anchoring the guard there is a WORSE bypass than the one we are fixing — need A1 work-tree root / A2 fix-overlap-only / A3; (B) the nine identifiers are PINNED EXPECTED OUTPUTS of canonicalize() asserted against RDKit, so synthetic values either turn the tests RED or make them assert the implementation against itself — the tautology class from item 3. Also disclosed: THREE of my four probes today were broken in a way that produced a PASS.

Agent: lung-on-chipsim
Ref: 90cca8e, tree clean, 0 behind origin/main (merged 5459098 first).

Row 65 accepted. FOUR of the six items are BUILT AND FALSIFIED. The two amendments each hit a
blocker that is a ruling, not an implementation choice, so they are back with you with the
measurement rather than guessed at.

## MERGE, and the approvals row collided again

origin/main moved to 5459098 and approvals.md conflicted a THIRD time. Resolved by measuring, not
renumbering blind: my five-item ratification is STILL absent from main (grep count 0), main's last
row is 64, and you announced 65 for tonight's ruling - so I took 66 rather than 65 to avoid
colliding with a row that does not exist yet. Say if you want it moved.

## ITEM 1+2 - DONE (3abff57). The guard now guards, and the registry test exists.

`write_compounds` routes through `refuse_unless_declared_output_root` BEFORE any mkdir, and the
docstring now records why the CLI cannot hold that check.
New `tests/test_record_bearing_writers.py`, 12 tests: every registered writer refuses a tracked
destination (parametrized, so a regression names WHICH writer), every registered writer still
accepts a declared root (the mirror - without it a writer that refused everything would pass),
`.dvc`/`.sha256`/`.gitkeep` refused inside a declared root, symlinked destination AND symlinked
ancestor refused, and the TMPDIR=<project> grant withdrawal.
The second half of your r2.20 claim - "no other frame writer has quietly appeared" - is discovered
BY AST from the source, not from a hand-kept list, because a hand-kept list of hand-kept lists is
how the original claim came to be false. Discovery finds exactly four frame writers; two are
registered, two are exempted with their reasons.

FALSIFIED. Neutering the guard (`return` as its first statement - the state you measured as
"suite identical to baseline") now fails SIX of the twelve. Un-wiring `write_compounds` fails the
parametrized test by name.

THREE THINGS I GOT WRONG AND FIXED, disclosed because two are the same class as the week's findings:
(a) My first neuter-probe inserted `return` INSIDE the function docstring, so it neutered nothing
    and reported 12 passed. I would have recorded "the guard is fine" on a probe that did not
    apply. I now verify probe application BY AST before trusting the verdict.
(b) My exempt list named `merge_report.write_merge_report`, written from assumption. That module
    writes MARKDOWN and calls no frame writer at all. My own stale-exemption test rejected it on
    its first run - which is the entire reason I wrote that test.
(c) The parametrized refusal test, when the guard is BROKEN, performs the very write the guard
    exists to refuse - into tracked configs/. The first run left
    configs/FIXTURE_registry_probe.{parquet,sha256} behind (FIXTURE-valued, untracked, deleted).
    It now cleans up in `finally`: a test of a refusal must not depend on the refusal working in
    order to leave the tree clean. Verified - the failing probe now leaves zero residue.

## ITEM 3+4 - DONE (90cca8e). Four scenarios that used to pass now fail.

- The scan NO LONGER GATES THE PARSER. Format and readability are checked first; every parseable
  tracked file is parsed regardless of what the regex saw.
- Strict UTF-8 replaces `errors="replace"`, so "cannot read this as text" can no longer decay into
  "no structures here".
- Unknown format fails closed whether or not a token was seen.
- Exemption is BY MEASURED EMPTINESS, never by name: a zero-byte file provably carries no
  identifier, and the moment anything is written into `configs/.gitkeep` it stops being exempt. A
  name allow-list would have exempted it forever - the shape this gate has been bitten by twice.
- ABSOLUTE floor, DERIVED from the roster: every canonical key `load_poc_roster` declares must be a
  structure the gate actually parsed. Not a constant, so it cannot go stale the way `>= 100` would.
- The tautological chain test is replaced by the property it claimed, with the
  `key.endswith("inchikey")` escape hatch - the thing that made it unfalsifiable - deleted. It now
  skips with a stated reason if nothing is satisfied by reference, rather than passing silently.

FALSIFIED, all four previously-green scenarios:
  blank all 26 evidence_doi            -> FAILS (was: chain test green with zero citations anywhere)
  git rm the four structure configs    -> FAILS at the new roster floor (was: 8 passed)
  tracked .csv.gz with every identifier-> FAILS closed (was: 8 passed)
  YAML-folded identifier past the regex-> PARSED, found uncited, FAILS (was: 8 passed)
  clean tree                           -> 9 passed, zero residue

AND A FOURTH PROBE DEFECT OF MINE, which is the sharpest thing in this report: probes 3 and 4 first
reported "9 passed" because I wrote `git add -f -q` and `-q` is not a valid `git add` flag. The add
failed, the files were never tracked, `git ls-files` discovery never saw them, and the verdict was
meaningless. I only caught it because the error text was in the output. THREE of my four probes
today were broken in a way that produced a PASS. The standing rule I am adopting and recommending:
A PROBE MUST ASSERT ITS OWN PRECONDITION BEFORE ITS VERDICT IS READABLE. Mine now print
"precondition verified: <path> IS tracked" before the suite runs. "I falsified it" is a claim at the
wrong extent unless the probe is shown to have landed - which is row 65's lesson, one level down.

## AMENDMENT A - BLOCKED ON A RULING, because the anchor the finding names is WORSE

You ruled this is conformance to r2.23 E-07, not a new design decision, and the design reviewer
named `pipeline.project_root()` as "the runtime root the plan means". I read it before using it:

    pipeline.project_root() docstring, verbatim: "WHERE THE JOURNAL IS WRITTEN ... Overridable with
    CHIPSIM_PROJECT_ROOT ... It is a JOURNAL DESTINATION AND NOTHING ELSE. It does not select the
    tree git is read from - see journal.source_root, which is not overridable."

So anchoring the security guard there would make the allow-list redirectable by an ordinary
environment variable - a BYPASS STRICTLY WORSE than the `PYTEST_CURRENT_TEST`+`TMPDIR` one we are
fixing, and the exact shape `declared_output_roots`' own docstring refuses ("a default location that
can be redirected by an environment variable is one an operator cannot reason about").

The correct anchor for "is this path tracked?" is the GIT WORK TREE ROOT - the tracked unit is the
work tree, not the Python package directory, which is precisely why a tracked SIBLING of
`projects/lung-on-chipsim/` passed the overlap check. But: there is no work tree under a non-editable
wheel install, and E-07's stated complaint is that anchoring to the package tree makes a wheel
install refuse every write. So the two candidate anchors each have a stated defect and E-07's phrase
"the project root discovered at RUNTIME" does not disambiguate them.

RULING NEEDED - which does E-07 mean:
  (A1) WORK-TREE ROOT, discovered by walking up for `.git` as a pure path computation (handling the
       worktree case where `.git` is a FILE). Fixes the sibling hole properly. Needs a stated answer
       for the no-work-tree case - refuse all record-bearing writes, or fall back to the package
       tree and accept E-07's complaint there.
  (A2) KEEP `source_root()` as the anchor and fix ONLY the overlap check, by refusing a temp root
       that shares any ancestor with the work tree rather than requiring containment. Smaller, does
       not touch E-07's wheel case, but leaves roots anchored where E-07 says they must not be.
  (A3) Something else you have in mind.
I have changed NOTHING here. Guessing between these is choosing a security anchor by taste.

## AMENDMENT B - THE DIFFERENT ANSWER YOU INVITED, with evidence

You said: "If any of the nine was in fact derived from the pinned snapshot rather than typed, say so
and cite where - that is a different answer and I will take it." It is a different answer, and not
the one you listed.

MEASURED, without reproducing any value: the five `*_KEY` constants are PINNED EXPECTED OUTPUTS of
`canonicalize()`, asserted against it:

    result = canonicalize(THREONINE_RELATIVE)
    assert result.inchikey == THREONINE_STEREO_FREE_KEY

RDKit computes the key from the InChI literal in the SAME FILE and the test compares. So they are
not written from memory: each is the deterministic output of a computation over an adjacent input,
and the suite passing IS the standing proof of reproducibility. Two carry an inline PubChem CID in a
comment as their provenance; I did not verify those mappings, because the standing constraint forbids
me from comparing a constant against an adjacent structure literal or looking up whether an
identifier is assigned.

Making them synthetic therefore does one of two bad things:
  - replace the EXPECTED values only -> RDKit still computes the real key from the real InChI and
    every one of these tests goes RED; or
  - replace the INPUT InChI literals too -> then the expected key must be whatever RDKit computes
    from the synthetic input, i.e. the test asserts the implementation against itself. That is the
    tautology class I was just caught on in item 3, deliberately introduced.
A third option exists - hand-build synthetic but VALID InChI strings carrying real `/t`, `/m`, `/s`
and `/b` layers so the stereo predicates are still exercised - but authoring valid InChI by hand is
writing structure data from memory, which is the rule we are enforcing.

Your narrowing stands and I accept it: threonine, D-threonine, L-aspartic acid and abscisic acid are
not roster compounds and the confidentiality half is not engaged, so my "(name, structure) pairing in
a tracked public file" OVERSTATED the class and I withdraw that framing.

RULING NEEDED: accept the constants as DERIVED-AND-REPRODUCIBLE rather than typed (my
recommendation - it is what they are, and the suite re-proves it on every run), or rule the third
option and I will build synthetic InChI inputs. I have changed NOTHING in that file.

## GATE, selectors and commands NAMED, per your standing instruction both ways

    configured gate   cd projects/lung-on-chipsim && uv run pytest -q    864 passed / 4 skipped / 0 failed
                      (851 before this work: +12 registry, +1 roster floor)
    selected          uv run pytest -q -m "not network and not integration"   re-measured at re-gate
    uv run ruff format --check .      85 files already formatted
    uv run ruff check .               All checks passed
    uv run ty check chipsim           re-measured at re-gate
    uv run ty check tests             re-measured at re-gate
Two ruff COMMANDS, not the word "ruff". Adopted.

## NOT FIXED, and why - for the programme you will scope

Everything outside your six: the ~40 remaining findings, the theta sourcing vocabulary, one error
base per package, `unit` in the prior's ENTRY_KEYS. Plus two I hit while working and deliberately
left: `declared_output_roots()` never checks root EXISTENCE, so a missing `data/interim/` degrades
into the generic refusal instead of E-06's two-message split; and `CONFIGS` is defined TWICE in
test_fixture_sources.py. Neither is in scope and I am not smuggling them in.

NO RECEIPT IS SIGNED. I will re-gate and /pr-submit once A and B are ruled, since both touch files
in the diff and a receipt binds to an exact tip.

next_handoff: rulings on A (A1/A2/A3) and B.
