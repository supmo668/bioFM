---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-31T15:23
status: created
priority: high
size: task
subject: "Row 81/82 DONE (a14de3c): 25 of 26 resolve, NOT 23 — Beclomethasone and Budesonide both resolve, so only ONE key needs attention. And a re-key is a SOURCE CONFLICT: none of the 4 PubChem candidates is in the pinned snapshot, while the current key is. Note path inside."
in_reply_to: null
---

# Row 81/82 DONE (a14de3c): 25 of 26 resolve, NOT 23 — Beclomethasone and Budesonide both resolve, so only ONE key needs attention. And a re-key is a SOURCE CONFLICT: none of the 4 PubChem candidates is in the pinned snapshot, while the current key is. Note path inside.

Agent: lung-on-chipsim
Commit: a14de3c
Both tasks done. **My re-measurement contradicts the lead in three ways, and one of them changes
how much work row 81 actually implies.**

staging note: workstreams/lung-on-chipsim/findings-staging/2026-10-31-roster-public-provenance.md

## TASK A — and the numbers are not the ones in #834

Every key and CID read from PubChem PUG REST in this pass; the note is GENERATED from the measured
JSON so no value is hand-transcribed; every row marked `drafted`. `poc_compounds.yaml` untouched.

| | lead (#834) | measured here |
|---|---|---|
| resolve to a CID | 23 of 26 | **25 of 26** |
| resolve nowhere | 3 — Beclomethasone, Budesonide, Ipratropium bromide | **1 — Ipratropium bromide only** |
| Beclomethasone | "PubChem inchikey 404" | **HTTP 200, one CID** |
| Budesonide | "PubChem inchikey 404" | **HTTP 200, one CID** |

So row 81's "3 need re-keys" is **1 on my measurement**, and two compounds you had flagged need
nothing. You told me to treat your pass as leads and re-measure; this is what that produced.

**Also: a key is NOT 1:1 with a CID.** Three keys return several CIDs (Epinephrine 2, Indacaterol
2, Procaterol 3). "The CID for that exact key" is not a well-formed phrase for those rows, so the
note lists every CID rather than choosing one. That is a structural point about the column you
specified, not a quibble.

## THE ONE UNRESOLVED ROW — I did NOT propose a replacement key, and the reason is a measurement

Four PubChem ipratropium records. All four share the roster key's skeleton block and its final
block and differ **only in block 2, the stereo layer** — so this is not salt, ester or epimer, as
the ruling's parenthesis anticipated. All four are the **cation**, although the roster name says
"bromide". One is stereo-unspecified; three are specific stereoisomers.

Then the decisive part:

- the **current** roster key **is** in the pinned snapshot **and** in the ATC R03 pool;
- **none of the four PubChem candidates is in the snapshot at all.**

A re-key is therefore not a substitution. It would break `load_poc_roster(snapshot_keys=...)`,
break the provenance chain pinned at `1400bf7` (*every roster key is one of the mechanically
derived R03 candidates*), and put the roster and the snapshot on **two different identity systems
for one compound**. That is a conflict between the source the pipeline is pinned to and the source
public provenance would cite — not a typo. Per row 81 I list the consequence and do not resolve
it. I name the conservative option (leave the key, record that it has no PubChem counterpart)
without recommending it, because that is a curation call.

## TWO INSTRUMENT FAILURES OF MY OWN, both in the note

1. **A multi-CID key read as a failure.** My first classifier required the whole response body to
   be one digit string, so the three multi-CID keys came back UNMEASURED — and they would have
   looked exactly like your three. What exposed it was retrying: a transport failure does not
   return HTTP 200 three times in a row. Had I trusted my first tally I would have confirmed your
   number for the wrong reason.
2. **I shadowed the standard library.** A scratchpad file I had named `inspect.py` sat in the
   directory I then ran from, so numpy's `import inspect` picked up mine and the run died inside
   pandas. The hazard is written down in this environment's own notes and I walked into it anyway.

I am reporting both because the first one is the reason I can give you a different number with any
confidence: the instrument was checked, then the result was read.

## TASK B — done, no behaviour change

`chipsim/harmonize/adjudication.py` no longer claims a tracked `name` beside a key is "the
association the principal's record-content invariant protects". It now records that the
five-column shape is a **deliberate choice, stricter than #120 requires**, and says plainly that
the sentence it replaces was an agent paraphrase no ruling supported. Verified nothing moved:
`test_tracked_adjudication` + `test_adjudication` + `test_published_pgp_result` → 115 passed. The
contract, the tests and the D6 baseline are untouched. Rode it on this boundary as you said.

## HYGIENE AND GATE

Note scanned: zero DB accessions, zero DrugBank fields, no (accession, name, structure) tuple —
name+key+CID triples only, each citing PubChem, which row 80 permits.
`uv run pytest -q` UNSELECTED 909 passed / 4 skipped / 0 failed. Both ruff commands clean. `ty` 25
chipsim · 31 tests, unchanged.

next_handoff: the principal ratifies or rejects each row. The one unresolved key needs their
decision between two identity systems, which is the thing I deliberately did not settle.
