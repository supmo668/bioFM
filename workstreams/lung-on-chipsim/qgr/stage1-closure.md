# Stage 1 closure — E-23 / lung-on-chipsim

**Authority:** approval-log row 61 (principal, verbatim *"Stop; the mechanism is the result"*), with
CTO #541's disposition: *"If it FAILS again on the same mechanism → Stage 1 CLOSES at the scope
reached: write the closure, the paper is written from the committed record, the branch does not land.
Either outcome is a result; neither is a failure of the rule."*

**Status:** the final gate FAILED on the same mechanism. **No QGR receipt is signed. Nothing is
pushed. The branch does not land.** Stage 1 closes here.

Measured at HEAD `af17cd2`, 0 behind `origin/main`. Hash A
`0219b888500e8a01d09642657a7c49557ffe1c4333780c4023b5a24d817c68f9`, 116 files. Four reviewers on
isolated snapshots plus a read-only pass by the authoring agent. Findings registered as **S-01…S-20**
in `deferred-findings-register.md`, alongside **D-01…D-12** (gate 9) and **R-01…R-24** (round 2).

---

## 1. What this report establishes

One mechanism, stated as plainly as it can be:

> **A fix is verified against the thing that was changed, not against the property the claim names.**

Nine instances are now recorded, dated, in the order introduced. **Six of the nine were introduced by
the repair of a previous instance.** That is what makes it a mechanism and not a list of mistakes: the
repair is one of its vectors.

The three added by this gate are the most useful, because two of them were authored while the author
was describing the mechanism in the same document:

7. **The citation-scheme sentence re-broke itself.** Methods §7 said `#54` was "the sixth-from-last
   row", repaired under H-10 for exactly this error, with a parenthetical boasting the figure was
   "recomputed from the log rather than recounted by hand". It was not recomputed; it was computed
   once. Rows `#60`/`#61` landed and it became wrong again.
8. **The type was verified against the mutant, not the property.** C-3 gave the registered divergence
   a dedicated exception type so nothing else could impersonate it. The agent verified that a bare
   `assert` at the production call site can no longer pass for it — and did not check that a
   **subclass**, or the type under an alias, still can. It can, with the file byte-identical to
   baseline: 39 passed, 9 xfailed, the registered finding witnessed by nothing.
9. **The measurement harness measured the wrong thing, twice, one message apart.** The gate's timing
   command captured `$?` after a pipe to `tail`, so it reported `exit=0` for a suite that had been
   killed at 82%. Having named that defect, the agent reproduced it immediately in the next command,
   on the bracket verification.

## 2. The finding this gate added about the genre

The paper's declared novel contribution is a measurement **of its own approval log** — the route
distribution over a contemporaneous, append-only, hash-locked revision table. Published: 59 numbered
revisions, 63 data rows, 46 standing-delegation. Re-derived with the paper's own instrument at
`af17cd2`: **61 / 65 / 47**.

The two new rows are `#60` (the scope ruling this gate requested) and `#61` (*"Stop; the mechanism is
the result"*). **Both were written by this gate's own adjudication.** Deciding whether to accept the
report changed the quantity the report publishes.

The first draft of this closure called that a fixed point — a claim that could not be simultaneously
true and approved. **That was an overstatement and is withdrawn.** A claim pinned to a *commit* is
stable against any number of later rulings. The actual defect is narrower and more instructive: the
paper pinned its figure to the **plan hash** `ae894db`, and rows `#58`–`#61` all carry that same hash
"(unchanged)", so the pin could not discriminate. The lesson is about choosing an identifier that
moves when the measured thing moves — not about an impossibility.

What remains true, and is the contribution: **an artifact that measures the process which approves it
must pin its measurements to a revision of that process, and must re-derive them at the moment of
approval.** This report did neither, which is why the figure was two rows stale at the moment of its
own closure.

## 3. What was corrected before closing

A closure that publishes false numbers would be worse than one that publishes none. Six corrections,
all re-derived from records, **five of them errors the authoring agent introduced**: the route counts
(59/63/46/2 → 61/65/47/3, re-pointed at `route-distribution-af17cd2.json`); methods §9's fabricated
"48 vs **46** instruments disagree", which the claims list and register both already certified as a
*fabricated finding avoided*; limitations §2's "139 of 139" in the sentence CTO #512 makes binding;
limitations §3's table that reconstructed the withdrawn 471/21 under a 445/20 headline; methods §7's
position; and a mis-citation of H3.

Two claims were restated rather than renumbered. **H4** no longer asserts a surface that "EQUALS" its
scope — it is a suffix-filtered subset (`eligible_by_suffix` 127 of `tracked_in_scope` 160 in
`projects/`). **H5** no longer attributes the comparable subset's sum to all seven cited files.

And one claim was weakened on evidence: H5 said the two instruments "AGREE" at 48. They do, but that
is **not corroboration** — both figures are `classify_sites()` summed over the same files, and that
function's F counter is guarded by the file reading as cited, so a non-zero F implies a cited file and
the classifier's bucket F is composed of exactly those files. One function computed twice cannot
independently confirm a count. No second measurement of that quantity exists.

## 4. What held

Recorded because a closure that lists only failures is not a measurement either.

- **C-2** closes its defect — the audit-surface guard cannot be deleted green (4 mutants killed).
- **C-3** closes its named instance — the mutant that previously left the file byte-identical now
  fails loudly. The *class* remains open (S-09).
- **All four arms** of the new instrument kill the mutants its tests drive, and its fixture's
  monkeypatching has not made them vacuous.
- **C-1's surface equals its scope today** — 236 eligible, 236 reached, dedup correct, 724 = 236 + 488
  with no double count. The defect is that the equality is reported and not enforced (S-07).
- **`could_not_scan` is reachable and genuinely fatal** (ruling #455), driven directly.
- **No deferral was re-opened**; R-02 was genuinely reduced.
- **Every number the gate brief named was correct.** Every wrong number was one the brief did not name
  — which is itself the mechanism, applied to the brief.
- The relaxed-rule disclosure is adequate and discoverable without a diff.
- **G3 and H2 resolve end to end** from the committed files alone.
- No command-injection surface; the `AIADLC_DIFF_HASH` regression was not reintroduced.

## 5. What a reader should not conclude

This is **not** evidence that the r2.50 mechanisms work. Six of the nine instances were introduced by
the repairs those mechanisms authorise, and of the nine, **one** was first caught by an instrument —
and that one was caught during this gate, when `claims-vs-records.py` refused two numbers the author
had just written that no record emits. Every other instance was found by a reader: a reviewer, or the
author re-reading their own work.

It is also not evidence that the content guard is sound. Its headline is qualified by ruling (E4), two
of three prohibitions are measured by nothing, the citation predicate is positively correlated with the
violation it exists to expose, and the gate that certifies the surface can report `PASS` over a 69-file
blind spot (S-07) and writes `empty_patterns: 0` into every record regardless of measurement (S-06).

What it is evidence of: **the family is open, it survives repair, and repair is one of its vectors.**
That claim is now supported by nine dated instances with named authorship, which is a stronger
evidentiary base than the report had at gate 9, and it was obtained at the cost of not shipping.

## 6. Disposition

- No receipt. No push. The branch does not land.
- The paper is written from the committed record: `stage1-methods.md`, `stage1-claims-list.md`
  (41 rows / 35 supported / 6 CUT), `stage1-limitations.md`, `stage1-short-form.md`.
- 20 round-3 findings registered as S-01…S-20; 36 registered findings stand in total.
- **S-01, S-02, S-06, S-07 and S-20 are the items a successor should read first.** S-01 and S-02 make
  the newest instrument's verdict unreproducible from the repository; S-06 and S-07 let a failing run
  publish a clean record; S-20 records that R-10's deferral was taken at a smaller extent than now
  exists.
- The 36 registered findings are the inheritance. A successor should not begin by repairing them — on
  this branch's record, repair is how six of nine instances arrived.
