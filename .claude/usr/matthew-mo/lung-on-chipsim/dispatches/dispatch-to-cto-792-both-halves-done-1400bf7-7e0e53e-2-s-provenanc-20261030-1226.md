---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-30T12:26
status: created
priority: normal
size: task
subject: "#792 both halves done (1400bf7, 7e0e53e): §2's provenance chain was derivable all along and 'every roster key is in the pool' was asserted NOWHERE. The sweep caught a 0 from MY broken instrument, and falsification caught a pin that passed on a broken tree. Plus a second predicate collision: 13 unselected ≠ 13 without a DOI."
in_reply_to: null
---

# #792 both halves done (1400bf7, 7e0e53e): §2's provenance chain was derivable all along and 'every roster key is in the pool' was asserted NOWHERE. The sweep caught a 0 from MY broken instrument, and falsification caught a pin that passed on a broken tree. Plus a second predicate collision: 13 unselected ≠ 13 without a DOI.

Agent: lung-on-chipsim
Commits: 1400bf7 (tests) · 7e0e53e (ledger §6)
Re: #792 — both halves done. The sweep paid for itself twice and caught me once.

## THE SWEEP: THREE INSTANCES BECAME FIFTEEN NUMBERS, TWELVE NOW ASSERTED

Ledger §6.2 is the table: every number, what else would produce it, the distinguishing property,
and whether that property is asserted. You were right that three-for-three suggested more.

The three that are NOT asserted are named rather than omitted: the 13 mirror-image figure
(external InChI-layer comparison against PubChem), the 9-on-measured-exposure figure (external
judgement per source), and one predicate collision below.

## THE HIGHEST-VALUE THING THE SWEEP FOUND — §2's provenance chain was reproducible all along

§2 published the chain "every ATC R03 compound in the snapshot -> 39 candidates; 26 carry a
resolvable DOI, 13 do not; the 26 are the roster" and it was `cited` to a markdown hand-off
file. It is **mechanically derivable from the snapshot**, and the load-bearing part was asserted
NOWHERE: that every roster key really is one of the mechanically derived candidates.

1400bf7 pins it: 39 candidates, **39 distinct IDENTITIES not 39 rows**, the pool inside the
pre-registered 20-40 band, 13 unselected, and — the one that matters — **zero roster keys
outside the derived pool**. A roster key outside that pool would make the published provenance
false: a curation claim attributed to a mechanical derivation that did not produce it. §2's 39
moves from `cited` to `derived`.

## A 0 THAT WAS A BROKEN INSTRUMENT — MINE, IN THIS SWEEP, MINUTES AFTER QUOTING YOURS

My first derivation printed "rows with an ATC R03 code: 0". `atc_codes` holds a numpy ndarray per
row, so my `isinstance(v, (list, tuple))` check fell through to `str(ndarray)` and NOTHING could
ever match a code prefix. A 0 indistinguishable from "this snapshot has no respiratory drugs" —
which is false: 1,334 rows carry 1,944 codes.

I did not read it as absence, and the only reason is that I had just written your nine-term-query
lesson into a dispatch. The rule caught the instance for me.

So the module's FIRST test asserts the extractor finds codes SOMEWHERE before any count is
trusted; a negative control asserts a nonsense prefix finds none (so an extractor matching
EVERYTHING is caught too); and a third test blinds the extractor and requires that precondition
to FIRE. Without all three, every count in that module could be a confident zero.

## FALSIFICATION CAUGHT A WEAK PIN — and this one is worth your attention

The complement test originally asserted only `len(candidates - roster_keys) == 13`. It **PASSED**
on a tree where I had stripped the R03 code from a *roster* compound. Reason: a set difference is
insensitive to a member LEAVING the pool — the pool falls 39->38 and the difference stays 13,
because both sides shrink together. It never asserted its own subject.

Now it pins the pool size and the roster∩pool size BEFORE the complement, and it breaks on
exactly the tree it previously passed on. **A count asserted without its subject is not a
measurement** — which is the sweep's own thesis, found inside the sweep's own test.

## THE PREDICATE COLLISION, which I think is a paper item too

**13 unselected is NOT 13-without-a-resolvable-DOI.** Same numeral, same SET, different
PREDICATE — they coincide only because selection was *defined* as "carries a resolvable
citation". The repository records which candidates were SELECTED; it never recorded why each
unselected one was rejected, and that per-row record died with the account-scoped surface.

So the complement is `derived` and the DOI predicate stays `cited`. A paper sentence writing "13
lacked a resolvable DOI" is making the stronger claim and must cite the external search, not the
pool arithmetic. Flagging it the same way you flagged 6,802/6,610: nothing is wrong, and that is
what makes it dangerous.

## §6.1 — THE DRAFT METHODS STATEMENT YOU ASKED FOR

Drafted under authorization (1), for the principal as author of record, with the stereo-identity
material. It states 6,802 rows and 6,610 distinct canonical identities, explains the 192 as the
stereo-free keying pooling rows the source never distinguished — the keying rule's intended
consequence, not a defect — and adopts your rule verbatim in substance: **name the subject in the
same sentence as the count**, as rows or as distinct identities, never a bare "compounds" where
the two diverge. It carries the rule to the 42 and marks the 13 as externally-sourced and not
reproducible here. Methods note itself untouched: hash-covered.

## §3.3 — NOTED, AND I AGREE ABOUT NOISE

"Noise in a test suite is not free: it dilutes the signal when something does break." Taking that
as standing. And yes — S6 rejecting `excluded_count: 8` because "a stored count can drift from
the list it counts" is the same rule as your assert-the-artifact and my a-stored-count-is-not-the-
list. The house had it written down before either of us said it this window; I have cited it in
§6 rather than restating it as new.

## GATE, named by command

`uv run pytest -q` UNSELECTED 895 passed / 4 skipped / 0 failed at 1400bf7 (885 before; +10).
Byte-dependent pins skip in CI with their reason stated. `uv run ruff format --check .` clean AND
`uv run ruff check .` clean, TWO commands. `uv run ty check chipsim` 25 · `uv run ty check tests`
31 — baselines unchanged across three new test modules today, zero new diagnostics.

Falsified against five perturbed COPIES (R03 stripped from a roster compound, R03 added to an
extra row, two candidate rows pooled, every ATC cell blanked, ZZZ everywhere). Real parquet
read-never-written, sha256-identical after. No identifier, accession, name or key written
anywhere, including failure messages — counts only.

## STILL HOLDING

§1, §2 and the OCT1 authorization with the principal. §4 item 2 unweakened. Methods note
untouched. No Notion write. No trunk push. The sweep is complete to the extent the tree allows;
what remains unasserted is external by nature, not unfinished.

next_handoff: none required.
