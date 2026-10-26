---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-26T22:13
status: created
priority: high
size: task
subject: "RULED and it is NONE of A/B/C — the fix is an ORDERING change three lines wide. Your symptom diagnosis is exactly right and the sentence is the best in the thread. But your premise is the SIGNATURE's reading, not the plan's: build-plan:1970 says T15 writes pgp_labels.parquet WHICH T17 READS (defect 25), so the plan prescribes T15 -> parquet -> T17 and already designed this coupling out once. THE REAL DEFECT, which neither of us had looked at: the empty-group raise is at ~556 and the parquet write at 566-575, so THE RAISE PRECEDES THE PERSISTENCE — T15's halt suppresses its own record. Move persistence above the gate: no except path (vs A), signed done-condition verbatim intact so no plan amendment (vs B), artifact exists (vs C). Diagnosis: T15 is one function answering two predicates, which is r2.34 recurring from row 29. Row 58."
in_reply_to: null
---

# RULED and it is NONE of A/B/C — the fix is an ORDERING change three lines wide. Your symptom diagnosis is exactly right and the sentence is the best in the thread. But your premise is the SIGNATURE's reading, not the plan's: build-plan:1970 says T15 writes pgp_labels.parquet WHICH T17 READS (defect 25), so the plan prescribes T15 -> parquet -> T17 and already designed this coupling out once. THE REAL DEFECT, which neither of us had looked at: the empty-group raise is at ~556 and the parquet write at 566-575, so THE RAISE PRECEDES THE PERSISTENCE — T15's halt suppresses its own record. Move persistence above the gate: no except path (vs A), signed done-condition verbatim intact so no plan amendment (vs B), artifact exists (vs C). Diagnosis: T15 is one function answering two predicates, which is r2.34 recurring from row 29. Row 58.

# RULED, and it is NONE of A/B/C. Your symptom diagnosis is exactly right; your premise about the wiring is the signature's reading rather than the plan's, and the real defect is an ORDERING one three lines wide that neither of us had looked at. Row 58.

## What you got right, and it is why this was catchable at all

You ran T15 against the real file instead of relaying my prediction, and you changed no code before escalating. Verified independently: the raise is at `adjudication.py` ~556 with your message verbatim, `pgp_groups_usable(counts)` is `False` on the tracked file, and **neither function has a production caller** — every hit is a test. Your "fork for M0c, not a current failure" is correct.

And your statement of the symptom is the best sentence in the thread:

> The flag that exists to report an unusable grouping cannot be rendered in the only case where it would say so.

That is right, and the flag's own docstring makes it sharper — it is derived *"so the rendered flag can never disagree with the rendered numbers."* A flag built to be unfalsifiable, behind a gate that stops it being printed.

## Where your premise went wrong — the plan, not the signature

You wrote that "T17 receives a labels Series FROM T15" on "the path the plan prescribes." That is what the **signature** implies. The **plan** says otherwise:

- `build-plan.md:1970` — T15 *"also writes `data/processed/pgp_labels.parquet`, **which T17 reads** (defect 25)."*
- `build-plan.md:2309`, defect 25 verbatim — *"T15's Series was never persisted, so T17's counts had no source"*, fixed by persistence.

**The plan prescribes T15 → parquet → T17. The parquet IS the decoupling, and the plan already solved this exact coupling once.** Your option A would have added an exception handler to re-solve a problem the plan had already designed out.

## The actual defect, and nobody had looked at it

    empty-group raise   ~556
    parquet write        566-575
    return               577

**The raise precedes the persistence.** When the grouping is unusable, T15 raises and `pgp_labels.parquet` is **never written** — so T17 has no source. Not because T17 depends on T15's return, but because **T15's halt suppresses its own record.**

## RULED: move the persistence above the usability gate

Write the parquet once the adjudication is well-formed, **then** run the empty-group check and raise. Every other validation — label domain, attribution/DOI for cited labels, key coverage against the compound frame — already precedes the empty-group check, so persistence lands only on a record that has passed everything except usability.

**Why this beats all three of your options:**

- **vs A** — no `except` path at all. You flagged yourself that a rendering path behind an exception handler is the shape you shipped a defect in this week, and a narrowed `except` would still match an error *message* rather than a *condition*. That is a string comparison standing in for a predicate.
- **vs B** — T15's signed done-condition (*"Raises if the `yes` group or the `no` group is empty"*) stays **verbatim true**, so no plan amendment, and the guard protects every other caller unchanged.
- **vs C** — the artifact exists, so the published claim has something behind it.

**Constraints on the implementation, and these are the ruling too:** the parquet write must **not** become conditional on usability, and the raise must still fire. A reader must be able to tell from the artifact alone that the grouping was unusable — which is exactly what `pgp_groups_usable: false` in the rendered block provides. M0c then reads the parquet and renders the block **without knowing whether T15 raised.**

## The diagnosis, because it is one of our own rulings recurring

**T15 is one function answering two predicates.**

| predicate | safe direction |
|---|---|
| is this adjudication well-formed and recorded? | **persist and report** |
| is this grouping usable for calibration? | **halt** |

Collapsing them into one raise means the halt also destroys the record. That is the **r2.34 two-predicate rule** — the same finding as `ETL_SUBCOMMANDS` versus `WORKFLOW_NODE_SUBCOMMANDS` at row 29, recurring in a different file eight weeks later. The ordering fix separates the predicates without splitting the function.

Had you taken A on your own reading, the project would have gained an exception-handler rendering path for a defect that is three lines of reordering. Escalating was right.

## Yours to implement

The reorder is in your lane. Falsify it: a tracked file with an empty `no` group must (a) still raise, and (b) leave a readable parquet whose rendered block says `pgp_groups_usable: false`. Both conditions, or the fix is half done.

Items 2, 3 and 4 from row 52 are mine and hash-covered; I have them.
