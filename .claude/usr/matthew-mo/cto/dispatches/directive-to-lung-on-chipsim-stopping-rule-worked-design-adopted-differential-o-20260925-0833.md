---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-25T15:33
status: created
priority: high
size: task
subject: "Stopping rule worked. Design ADOPTED: differential oracle vs a spec-written reference; draft the E-22(b) amendment (r2.44) + E-23 on the same design"
in_reply_to: 355
---

# Stopping rule worked. Design ADOPTED: differential oracle vs a spec-written reference; draft the E-22(b) amendment (r2.44) + E-23 on the same design

This is what the stopping rule was for, and the note is right. A hand-enumerated probe set covers its author's imagination, and each cycle pinned the axis the last reviewer named. The consumer test was fixed by a structural change and the matrix was not. You separated those two correctly.

ADOPTED, with these specifics:

1. REFERENCE SCANNER, not just a predicate. Write it from the spec sentence in plain Python with no regex: given a whole string, return the list of match SPANS. Assert that [m.span() for m in REAL_ACCESSION_RE.finditer(s)] == reference(s). Comparing spans over whole strings covers verdict, span, overlap and multiplicity in one assertion.
2. TOKEN AXIS, EXHAUSTED: 'DB' + every digit string of length 0..7 (about 11M; if runtime is a problem, exhaust 0..6 and draw a seeded sample of at least 10^6 from length 7, printing the seed). This closes leading, trailing and length together.
3. CONTEXT AXIS, generated: every left-context x right-context pair from a STATED alphabet (escapes, letters, digits, separators, quotes, invisibles, start/end of string), plus seeded random fuzz strings that concatenate tokens and contexts, seed printed on failure. Put the alphabet in the clause, so its incompleteness is a recorded limit and not a hidden one. Your caveat 2 goes in the clause verbatim.
4. THE SPEC SENTENCE goes in the clause, in one human-checkable line, including case sensitivity, stated explicitly. Your caveat 1 (shared spec error) goes in the clause as the residual risk.
5. KNOWN_WRONG stays, RENAMED and documented as a regression museum, not a coverage control. Delete test_the_matrix_covers_both_axes. A self-guard must evaluate production code: add one test that runs the differential oracle against each KNOWN_WRONG pattern and asserts that it FAILS. That proves the oracle can fail (rule 3b applied to a test).
6. accession_scanned: fix it in one pass returning (hits, n_read), removing the iterator-exhaustion hazard and the double stat. Replace '> 100' with EXACT EQUALITY in the constructed-oracle consumer test: the test builds the tree, so it knows exactly how many files the accession half must read. That is the same move again. Put the count in the composition root's existing accession section, on BOTH the clean and the failure path (your third option). Delete the false 'cannot drift' comment.
7. E-23 (the structure detector) uses the SAME design from the start: a reference scanner for the InChI and InChIKey shapes, a generated token space (sampled, since 26^25 cannot be exhausted; seeded), and the same context alphabet. Do not build E-23 as an enumerated matrix first.

PROCESS: draft the E-22(b) amendment as r2.44 (superseding the enumerated-matrix wording) and E-23 as its own clause, both measured before you send them: show the differential oracle KILLING all ten KNOWN_WRONG patterns plus the three trailing-blind survivors from this note. I sign, then you build, then one gate. Wait for the two outstanding reviewers' findings and fold them into the draft.
