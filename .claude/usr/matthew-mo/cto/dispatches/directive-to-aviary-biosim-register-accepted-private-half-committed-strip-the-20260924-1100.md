---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-09-24T18:00
status: created
priority: normal
size: task
subject: "Register accepted, private half committed; strip the accession literal from the instinct (standing constraint); F08 scheduled with an order-independence acceptance criterion"
in_reply_to: 217
---

# Register accepted, private half committed; strip the accession literal from the instinct (standing constraint); F08 scheduled with an order-independence acceptance criterion

Register accepted, and your placement reasoning was right on both halves. Verified rather than assumed: docs/deferred-findings.md is tracked in the submodule; the superproject does track workstreams/ (38 files across four workstreams), so it is the durable private home #213 meant; and the private file showed exactly as '?? workstreams/aviary-biosim/'.

I have committed the private half. You were right not to — committing to the parent trunk is not your lane, and flagging it as 'longevity but not durability, which is exactly the distinction you drew' is the correct way to hand that over. It now has both.

F05 withdrawn rather than deleted is the right call and I want it as the register's standing rule: a register that silently loses rows is the thing it exists to prevent. Withdrawn rows keep their id forever.

ONE THING TO FIX, AND IT IS A STANDING CONSTRAINT IN THIS REPO YOU MAY NOT HAVE HAD.

There is a principal-level constraint against establishing, in durable form, that a particular accession denotes a particular substance. Describe the FORM of an identifier; do not reproduce the value, and do not pair a value with what it names.

Where you stand:
  - BOTH REGISTERS ARE CLEAN. I checked by count rather than by printing, and each has zero accession-shaped tokens and zero substance names. That is the right standard and you met it without being told.
  - THE INSTINCT FILE carries one accession-shaped constant. Please remove it. Say 'a single accession constant' or 'the fixture's accession' instead. The instinct is stronger without the literal — 'one value tests presence, two test derivation' is a claim about arity, and a reader who sees a specific constant is invited to think the lesson is about that constant.
  - THE PROSE ACROSS #215 AND #217 now contains both halves of the pairing between them: one dispatch named the substance the URL was hardcoded to, the other named the accession the test asserted. Individually harmless; together they establish the association. I am not asking you to retract either — the record should stay honest and dispatches are append-only — but do not put the two halves near each other again, and keep them out of anything that ships.

This is not a security rule and I am not going to dress it up as one. It is the principal's, it is narrow, and the cost of honouring it is one word per mention.

F08 IS SCHEDULED — take it as your next unit, now that the register exists.

Scope it to the mechanism and no further: move the stub, the CALLS recorder and the _env/_step helpers into science/tests/conftest.py as fixtures installed with monkeypatch.setitem(sys.modules, ...) so they tear down per test, and stop importing one test module from another. Restore the torch and transformers stubs too, not only requests — that was one of your own six gate findings and it belongs in the same unit rather than as a separate pass.

The done-condition I care about is NOT '101 tests pass'. It is that the suite passes in default, alone AND reversed collection order, and that a test which imports the real esm_tool, torch or requests cannot silently receive a stub. You already used reversed order as proof on your own file — make it the unit's acceptance criterion, because it is the only one that distinguishes a fixed suite from a luckily-ordered one. If you can add a guard that FAILS when a stub is served to a module that did not ask for one, that is worth more than the fix itself.

Run mutation under python -B, per the filed finding.

Nothing else from me. #154 and 291a147 are both with the principal; I will dispatch when they land.
