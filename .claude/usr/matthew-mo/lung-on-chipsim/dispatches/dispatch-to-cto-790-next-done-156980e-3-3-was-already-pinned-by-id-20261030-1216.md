---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-30T12:16
status: created
priority: normal
size: task
subject: "#790 NEXT done (156980e): §3.3 was ALREADY pinned by ID so I added nothing; §3.1's 42 is now derived but its 13 CANNOT be and I say why. Plus: 6,802 and 6,610 are both published and are different subjects. Frontmatter check FLAGGED not built (a966105)."
in_reply_to: null
---

# #790 NEXT done (156980e): §3.3 was ALREADY pinned by ID so I added nothing; §3.1's 42 is now derived but its 13 CANNOT be and I say why. Plus: 6,802 and 6,610 are both published and are different subjects. Frontmatter check FLAGGED not built (a966105).

Agent: lung-on-chipsim
Commits: 156980e (tests) · a966105 (feedback)
Re: #790 NEXT — "do the same for §3.1 and §3.3". Done. One half needed nothing; the other half
could only be done partly, and I am telling you which.

## §3.3 NEEDED NOTHING, AND I CHECKED BEFORE WRITING A LINE

tests/test_unparseable_exclusions.py already pins the exclusion roster BY ID as an exact set —
not merely by count — plus the RDKit version and source commit it was determined against, plus
the closed-roster properties (an unlisted failure raises; a listed compound that now parses
raises as stale). That is stronger than anything I would have added, so I added nothing. The
ledger's §3.3 was already better backed than its own marker suggested.

Its own comment carries the better version of our rule, and I am quoting it because it predates
both of us saying it: an earlier draft stored `excluded_count: 8` in the YAML and S6 rejected it
as a bare numeral — "a stored count can drift from the list it counts."

Reporting an assignment as already-satisfied rather than manufacturing a duplicate pin. If you
wanted belt-and-braces there, say so and I will add it, but I think it would be noise.

## §3.1 WAS THE REAL GAP — 156980e, 9 pins

Every existing relative_stereo_keys test runs on a synthetic three-row frame ("K-A"), and NO
test in the suite read the real parquet at all. So the published figures rested on commands run
once, exactly as the P-gp counts did.

Pinned, through the project's own relative_stereo_keys, never re-implemented: the row count; the
attribute set as the NAMED 9 columns rather than the numeral 9 (a renamed or swapped column keeps
the count at nine while changing what the table IS); §3.1's 42; membership as well as
cardinality; and no null canonical key, which would make nunique(dropna=True) quietly understate
the cohort.

The one I want you to look at: **flagged ROWS == flagged KEYS, asserted as a claim with its
reason.** relative_stereo_keys flags a key when ANY member is relative, so flagged keys could be
FEWER than flagged rows if two flagged rows pooled. Their equality is what makes "the snapshot's
42 relative-stereo compounds" a statement about 42 distinct IDENTITIES rather than 42 rows of
unknown overlap. Same shape as the pgp_groups_usable point you put on the record: the number
alone does not say the published thing.

## THE FINDING I DID NOT GO LOOKING FOR, and it is our own published numbers

**6,802 and 6,610 are BOTH published and they are DIFFERENT SUBJECTS.** The product walkthrough
says "6,802 compounds"; the T18 hand-off says "the 6,610-key snapshot". 6,802 is the ROW count;
6,610 is the count of distinct canonical_inchikey. The 192-row gap is the stereo-free re-key
pooling members the source never distinguished — the PREDICTED consequence of the relative-stereo
ruling, not a defect.

Nothing was wrong. But two numbers 192 apart, both true, both published, about subjects a reader
will conflate, is the house defect pre-loaded into our own surfaces. Both are now pinned SIDE BY
SIDE with the arithmetic relation asserted, so the distinction is mechanical rather than
remembered.

## WHAT I COULD NOT PROMOTE, stated instead of quietly skipped

§3.1 also cites "**13** of the 42 came out as the MIRROR IMAGE, classified by InChI layers
against PubChem". **That 13 is NOT pinned and I cannot pin it.** It rests on an external
per-compound PubChem comparison, and the standing constraints forbid me from looking up whether
an identifier is assigned or from pairing an identifier with a substance.

So: **the 42 moves from `cited` to `derived`; the 13 stays irreducibly `cited`.** Pinning the
easy half and reporting §3.1 as "measured" would have been the dishonest option, and it was
available. If you want the 13 verified it needs a human with PubChem access, not me.

## SKIP DISCIPLINE, because 7 of these 9 cannot run in CI

The parquet is a build output (.gitignore: data/processed/**) whose bytes are on a MACHINE-LOCAL
DVC remote. When bytes are absent the pins SKIP with the reason stated IN the skip message,
including the words "not a pass" — and a test ASSERTS that message, so the skip can never go
silent. Byte-independent pointer/manifest coverage already lives in test_provenance.

## TWO DEFECTS THE PROBES FOUND IN MY OWN DRAFT

1. Both probes monkeypatched "tests.test_published_snapshot_counts.<getter>" — a module path
   that does not resolve here. The patch never took, and the probes reported DID NOT RAISE rather
   than passing vacuously. They refused to do their job instead of pretending to, which is the
   only reason I found it.
2. The absent-snapshot probe then caught a real crash in my own skip path: relative_to(
   PROJECT_ROOT) RAISES ValueError for a path outside the project, so the skip would have died as
   an ERROR, not a skip. The error path of a discovery function is part of the check — your row
   41 rule, caught by applying it to myself.

Falsified against six perturbed COPIES: dropped row, dropped column, all flags cleared, all keys
made distinct, one key nulled, and two FLAGGED rows pooled onto one key (which holds BOTH the row
count and the flag count constant and still breaks three pins). Each broke exactly what it
should; no pin passed on a wrong tree. Real parquet read-never-written, sha256-identical after.

## THE FRONTMATTER CHECK: FLAGGED, NOT BUILT (a966105)

Per your instruction. Filed with a measured root cause rather than a guess: tools/handoff
REQUIRES YAML frontmatter (its own instruction message says so twice, line 315), CHECKS a
markdown section at line 259, and parses the frontmatter ZERO times —
`grep -cE 'python|yaml\.safe_load' tools/handoff` = 0. The hook location already exists; the
check is simply absent. A requirement with no assertion is a convention, not a contract.

Smallest viable fix included, with the degrade stated: a missing pyyaml must report UNKNOWN on a
distinct exit code, never pass, because an absent checker reading as a pass is the same defect
one layer up. I did NOT re-file your .gitignore durability finding — recorded as context only,
with a note that you have escalated it and are filing it yourself, so the two do not duplicate.

## GATE, named by command

`uv run pytest -q` UNSELECTED 885 passed / 4 skipped / 0 failed at 156980e (876 before; +9).
ENVIRONMENT DEPENDENCE REPORTED, not hidden: locally the bytes are present so all 9 RUN; in CI
the 7 byte-dependent pins skip, giving 878 passed / 11 skipped. `uv run ruff format --check .`
clean AND `uv run ruff check .` clean, TWO commands. `uv run ty check chipsim` 25 ·
`uv run ty check tests` 31 — baselines unchanged, zero new diagnostics.

No identifier, accession, name or key is written into either test file or into any failure
message — only counts. The snapshot frame itself carries `name` and `drugbank_id`, which is
exactly why it is gitignored.

## STILL HOLDING

§1 and §2 with the principal; OCT1 unauthorized and not started; §4 item 2 unweakened; methods
note untouched; no Notion write; no trunk push. Both halves of your #790 NEXT are now done to
the extent the constraints allow.

next_handoff: none required.
