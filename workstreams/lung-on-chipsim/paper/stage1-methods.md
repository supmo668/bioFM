# Stage 1 registered report — METHODS

*Written from `stage1-claims-list.md`; every statement below traces to a row there, and rows marked
CUT do not appear as claims. Long form. The short form is written separately from the same list,
never by truncating this document.*

**Measured at:** plan r2.50c (`ae894db`), 2026-09-29. Counts cite the evidence file that recorded
them, never a re-run.

---

## Abstract

We pre-register a lung-on-chip transport simulator whose machinery is complete and whose results are
empty **by construction**: no agent may author a biological value, and the fit refuses to run without
sourced priors [C2, C4]. The pre-registration fixes a two-compartment ODE with a MAP fit of two free
parameters [A1, A2], bit-comparable replay [B1], a **vector** metric of a gate score plus four
absolute vetoes [D1, D2], a selection budget with the locked test set opened at most twice in the
project's lifetime [D3], and two subgroups fixed before any coverage is computed [D4].

The novel contribution is not the simulator but its audit trail: a contemporaneous, append-only,
hash-locked record of **61 numbered methodological revisions**, each bound by hash to the plan text
it approved [F1, F2]. Under a stated normalisation rule those revisions are **47 standing-delegation,
5 principal-directed, 2 human-direct**, and four further categories [F3] — a reported datum, not a
measure of quality [F8], answering how much of a methodology an agent chose under delegation rather
than implying human authorship throughout. A route convention adopted mid-project requires a verbatim
quote for any claimed principal decision and provides `inferred` as an honest fourth category; **zero
rows use it** [F5, F6].

Four quality gates returned FAIL and were accepted rather than repaired, with **no completion
receipt signed for any** [G1, G2], and the final gate's stopping rule was fixed before it ran and
honoured against the authoring agent's own work [G3]. One failure mode recurred across nine gates —
*the claim lives in prose, the check lives in code, and nothing fails when they diverge* — and the
final gate found it **inside the mechanisms built to stop it** [G6]. It is reported open [G5 — cut].

**Not claimed:** no results observed, no fit performed, the ordering gate untested, coverage
uncomputed, no wet-lab validation, a proof-of-concept two-compartment model rather than a
physiological one, a content guard measuring one of three prohibitions indirectly and two not at
all, the recurring defect family open rather than closed, and `self-improvement` as a mechanism
never a measured result.

---

## 1. What this report is, and why the genre was chosen

This is a Stage 1 registered report: methods and a pre-registered analysis plan submitted **before
results exist**. That is not a workaround for having no results — it is a consequence of the
project's central constraint, and the constraint is the subject.

**No agent may author a biological value.** Every scientific input — device physiology, transport
priors, the curated compound set, the evaluator freeze — is human-owned. The agent builds the
schema, the validator, the harness and the guard; a human supplies the science. The fit enforces
this at runtime: `chipsim/transport/fit.py` calls `_require_sourced_theta` and refuses to run
without sourced θ [C2, C4].

So the machinery is complete and the results are empty, by construction. A conventional paper would
have to either wait or thin its results section into something misleading. A Stage 1 report makes
the blocker the *genre* rather than something to route around.

## 2. The model

A two-compartment transport ODE [A1], fitted by MAP estimation of exactly two free parameters in log
space [A2]. It is a proof-of-concept, **not a physiological model** [A3], and that is claimed as a
limitation rather than left for a reader to infer.

No fitted value, goodness of fit, or comparison to data appears anywhere in this report [A4 — CUT:
no fit has been performed].

## 3. Determinism

Given `(θ, drug, schedule, seed)`, replay is bit-comparable [B1]. This is load-bearing rather than
decorative: the project advances by a keep-or-revert ratchet, and a ratchet over a non-deterministic
measurement cannot distinguish an improvement from noise [B2]. The optimiser's start point is
deterministic, with the reason recorded beside it rather than assumed [B3].

## 4. Priors, and the refusal to invent

Every θ entry is SI-typed and carries a citation; an entry without a source is flagged
`assumed: true` rather than silently accepted [C1]. The schema and the validator exist; **the priors
do not** [C3 — CUT: absent, scaffold templates only].

The division of labour is the point. An agent that cannot author a value can still author the thing
that *rejects an unsourced value*, and that is a contribution a human need not repeat.

## 5. Pre-registration

The evaluation metric is a **vector**, not a scalar: a gate score plus vetoes, and vetoes are
absolute [D1]. Four vetoes are held — target-shuffle, cliff-stratified accuracy, non-monotonicity,
and calibration [D2].

The selection budget is fixed in advance: 20–30 gated diffs per milestone, with the locked test set
opened **at most twice in the project's lifetime**, and the gate-evaluation count reported next to
coverage [D3]. The two P-gp subgroups are fixed **before** any coverage is computed [D4].

Nothing in this section has been exercised. The 3-fold ordering gate is untested and coverage is
uncomputed [D5 — CUT].

## 6. Integrity: a content guard whose blind spots are measured

The project must keep licensed source content out of a public repository. Three prohibitions: no
real accessions, no database-coined titles, and no name-to-identifier associations.

The guard fails closed [E1]. The claim worth a referee's attention is not that it works, but that
**its blind spots are measured rather than asserted** [E2] — across nine quality gates, each gate
attempting to break the guard and recording what it found.

### What the classification does and does not establish

At the measured commit the guard classifies **141 of 141 in-scope sites** into four buckets — W
(citation adjacent to the site), F (citation elsewhere in the file), C (structurally inert probe), N
(needs human curation) — with 0 unclassified and 0 could-not-scan [E3, recorded in
`qgr/evidence/r250-classify-87d5c46.json`].

That sentence **may not stand alone**, and the qualification travels with it [E4]:

- W and F test **provenance adjacency only**. Of the three prohibitions, the guard measures the
  first indirectly and the other two **not at all**.
- The accession detector is shaped for one database; another database's accession form is
  structurally invisible to it. The production module already disclaims the name half outright:
  names are an unbounded vocabulary and there is no detector for them.
- The citation predicate is **positively correlated with the violation it exists to leave visible**.
  A block naming a compound beside its source identifier, its structure and a retrieval date is
  simultaneously the strongest citation match and a textbook name-to-identifier association. A site
  can be excluded from scrutiny *because* it sits beside the thing the rule forbids.

**445 shapes in 20 files sit outside guard scope**, and **62 sites in 14 files need human curation**
[E5]. F is an upper bound and N a lower bound, because the predicate that produced them was shown
defective and the defect was bound rather than repaired.

The claim that the guard prevents all three prohibitions is **cut, not softened** [E6 — CUT;
replaced by the qualified E4].

## 7. The audit trail — the methodology variational analysis

This is the contribution that is unusual, and it is why the report is worth writing before results
exist.

`plan-approval-log.md` is a **contemporaneous, append-only, hash-locked** record of methodological
revisions. Each row names what changed, why, and by which route it was approved, and each revision
is cryptographically bound to the plan text it approved via `plan-gate` [F1]. Most papers reconstruct
their design rationale afterwards; this one was written as the decisions were made.

**How rows are cited in this report, stated once.** The log interleaves two kinds of row, and they
are keyed differently. **Numbered** revisions carry a `#` column and are cited here as `#N`.
**Non-numbered** rows — principal rulings and convention entries appended between revisions — have
no number and are cited here by their timestamp. The two schemes disagree: the four non-numbered
rows sit at physical positions 54-57, so `#54` is data row 58 of 65 — the 8th-from-last — not the fifty-fourth. (An earlier draft of this sentence said "`11`th-from-last", which resolves to `#53`. The one sentence stating the citation scheme misresolved a row, inside the repair for misresolved citations; the figure above is recomputed from the log rather than recounted by hand.)
A bare "row 54" therefore resolves to the r2.50 signature under the `#` column and to the time-box
ruling under physical position. Two non-numbered rows also share the timestamp `2026-09-29 00:25`,
so those are cited with a qualifier (`(route correction)`, `(log convention)`). An earlier draft of
this report used physical positions for two rows and the `#` column for two others **in one
sentence**, which meant its sharpest integrity claim [G3] resolved under neither reading alone. The
log's own route text at `#54` and `#58` has the same defect — both say "row 54" meaning the time
box — and because the log is append-only and hash-locked, that text is left uncorrected and
recorded as a limitation rather than edited (limitations §5).


### Route distribution, and why it is reported

At the measured commit the log carries **61 numbered revisions plus 4 non-numbered rows — 65 data
rows** [F2]. Under a stated first-match-wins normalisation rule
[`qgr/evidence/route-distribution-af17cd2.json`], the numbered revisions distribute as [F3]:

| route category | count |
|---|---:|
| standing-delegation | 46 |
| principal-directed | 5 |
| human-direct | 2 |
| standing-ruling-applied | 2 |
| CTO-correction | 2 |
| principal-verbatim | 3 |

This answers the question a referee of AI-assisted science actually has: **how much of this
methodology was chosen by a human in so many words, and how much by an agent under a standing
delegation?** Reporting 46 under delegation and 2 human-direct is stronger than implying human
authorship throughout.

It is a **reported datum, not a measure of quality** [F8]. A high delegation count is neither good
nor bad on its face; it is a fact a reader is entitled to, and the alternative — not reporting it —
is what this section exists to refuse.

### The convention, and the category that has never been used

Mid-project the route convention was tightened [F5]: a row claiming a direct principal decision must
carry a **verbatim quote** of the principal's words or a resolvable session reference; a decision
taken by applying a standing ruling is recorded as such; and a decision without quotable evidence is
recorded as **`inferred`**.

**Zero rows are marked `inferred`** [F6]. That is stated explicitly because the category exists
precisely so an unevidenced decision can be recorded honestly, and because its emptiness is
checkable where its absence would not have been.

### Reversals, recorded beside decisions

The log keeps corrections **beside** what they correct rather than in place of it [F4]. Two
instances:

- A revision that was signed but never landed is kept as its own row, with the row that superseded
  it recorded separately — so the record shows an approval that produced nothing.
- **The route column was itself wrong once** [F7]. A row attributed a decision to a principal
  answer; the authoring agent reported that it could not distinguish two readings of that
  attribution and did **not** assert the record was false. The answer was a third reading neither
  had offered — a standing ruling applied by the coordinator — and the principal confirmed it
  verbatim. The original row stands; a correction row supersedes its route.

That episode produced the convention in the preceding subsection. A methods section that shows its
own corrections is more credible than one reading as though nothing was ever wrong.

## 8. The stopping rule, and four failures kept in the record

Quality gates 6, 7, 8 and 9 each returned **FAIL**, and each was **accepted rather than repaired**
[G1]. **No completion receipt was signed for any of them** [G2] — a receipt is a completion claim,
and these gates did not pass. Their absence is the honest signal.

Gate 9's stopping rule was fixed by the principal **before the gate ran** and honoured against the
authoring agent's own work [G3]: a failure on the recurring family closed the work item at the scope
it had reached, with no further revision. Reviewer isolation held throughout — a content digest over
a pinned file set, unchanged across the review [G4].

**The recurring family was not closed** [G5 — CUT; replaced by G6]. Across nine gates one failure
mode recurred: *the claim lives in prose — a test name, a docstring, an assertion message, a route
column, a typed count — the check lives in code, and nothing fails when they diverge.* Gate 9 found
it inside the mechanisms built to stop it, with five readers converging on the same instance [G6].

## 9. This report's own production

Claims about the report itself are held to the same standard as claims about the model.

No agent authored a biological value here [H1]. Every artifact was scanned for shaped content and
checked against the very citation predicate gate 9 found defective: **724 files scanned,
0 unreadable, 30 carrying unaccounted shapes, 10 reading as cited — 7 of
them inside the classified scope** [H4, recorded in `qgr/evidence/scan-artifacts-87d5c46.json`].

**This claim has now been restated twice, and the second restatement is the informative one.** Its
first form measured 10 files and reported 0 reading as cited — true of those 10, false of "every
artifact". Widening the globs raised *scanned* to 622 and *cited* to 3, and the restated claim added
the qualifier "0 of them inside the classified scope". That qualifier was **false**, and it failed in
a way worth recording precisely: the predicate's scope named `projects/lung-on-chipsim/` and
`workstreams/lung-on-chipsim/`, while the scan's globs reached neither in full — `projects/` not at
all. The zero was therefore computed over a partial intersection of scope and surface, and published
as a property of the scope. Measured over the whole scope the figure is **7**. The claim is
withdrawn and carried as CUT row H5 [H5 — CUT, named here, not relied on].

The repair was not a wider glob. Widening the radius is what produced the second failure. The surface
is now derived from **the same enumeration the classifier uses** (`git ls-files` over the classified
roots), so surface and scope cannot drift apart without the record saying so: `surface_vs_scope`
reports reached-versus-eligible per root on every run — `projects/` 127 of
127, `workstreams/` 109 of 109,
0 not reached. A first attempt at this fix used filesystem
globs and swept 26,623 files including the virtualenv, which is the same defect once more: two
enumerations of one named set, never compared.

What the 7 in-scope cited files mean is REPORTED rather than adjudicated (CTO #540 (1b)). They
account **48** sites into bucket F over the **5** of them the classifier also
places in F, against a classifier bucket F of **48**. An earlier draft of this paragraph reported a
`48`-vs-`46` **instrument disagreement**; that figure was a fresh scan compared against a superseded
classifier record, it is recorded as a **fabricated finding avoided** rather than a result [H5 — CUT, named here, not relied on], and
it should not have survived into this paragraph — it did, through three rounds, because the checker
that binds typed numbers to records only inspects paragraphs that textually name a record file.

**And the agreement is not corroboration.** Both figures are `classify_sites()` summed over the same
files, and in that function the F counter is guarded by the file reading as cited — so a non-zero F
*implies* a cited file, and the classifier's bucket F is composed of exactly these files. One function
computed twice cannot independently confirm a count. Summing the record's per-file `sites_into_F` over **every** cited in-scope file gives a larger
total that is not comparable to bucket F, because it includes a config and snapshot fixtures the
classifier scopes out by property; the instrument marks the comparable subset so the figure cannot be
taken from the wrong population, but no second measurement of it exists.

A report *about* that defect tripping it would be the defect one level up, so the check is recorded
rather than asserted — and on this claim it has now tripped twice, both times found by a reader.

Identifier-shaped lines flagged in two hash-covered plan files were escalated by the authoring agent
rather than investigated — resolving them required a comparison the agent is forbidden to make —
then inspected by the coordinator and ruled on by the principal, with the ruling recorded in the log
[H2].

And a count published in a gate verdict was measured at the wrong **point in time**, making a stated
comparison like-for-unlike; it was self-reported and corrected inline [H3]. A second count, in the
claims list's own summary, was typed and wrong by four, caught by counting the rows. A third — the
route distribution — mixed two matching rules in one sentence and was corrected by producing the
artifact in §7.

Three counting errors in the report *about* counting errors. They are recorded rather than quietly
fixed, because a methodology whose self-description is curated is exactly the thing this report
argues against.

The coordinator's two rigour-review passes were run **against the tree, not against the labels**
(#516, #518): claim ids were resolved to rows, artifact paths opened on disk, the route distribution
independently recounted, the traceability check re-run in the working tree, and both granularities
searched for result-shaped numbers and for the verbatim not-claimed list. Pass 1 failed three claims
for being bound to an instrument or an action rather than a stored measurement; pass 2 passed and
found a fourth defect **in the summary of this section's own evidence** — a preamble reporting three
zero-valued fields and omitting the one non-zero field beside them. A summary that reports only its
zeros is the same family at the preamble, and the rule adopted from it is: name every non-zero field,
every time.

---

## 10. Discussion: what a methodology record is evidence *of*

The claim this report rests on is narrow and worth stating exactly. It is **not** that agent-assisted
methodology is good, nor that this guard works, nor that the delegation distribution is healthy. It
is that a methodology can be recorded **while it is being decided**, in a form a third party can
check, and that doing so changes what the record is capable of showing.

Three properties do that work, and each is checkable rather than asserted.

**It is contemporaneous.** Rows were written at the moment of the decision and bound by hash to the
plan text they approved [F1]. A rationale reconstructed afterwards cannot be distinguished from a
rationale invented afterwards; one written before the outcome was known can.

**It keeps corrections beside what they correct** [F4]. The sharpest instance is the route column
being wrong about itself [F7]: an attribution the authoring agent could not verify, reported as
*unverifiable* rather than asserted false, which resolved to a reading neither party had offered.
Had the agent asserted the record was wrong, it would have been wrong. Had it stayed silent, the
error would stand. The convention that followed — a verbatim quote or a resolvable reference, with
`inferred` for anything less [F5] — exists because that episode happened, and its empty count [F6] is
now a checkable fact rather than an absence.

**It records what it failed to do.** Four gates failed and none produced a completion receipt
[G1, G2]. The stopping rule for the last one was fixed by a human before it ran and honoured against
the authoring agent's own work [G3] — which is the only arrangement under which an agent's report of
its own failure carries weight.

### The finding that generalises

One failure mode recurred across all nine gates: **a claim in prose with no check beneath it**. It
survived because prose and code are read by different faculties and compared by nothing. Five
independent readers converged on the same instance [G6], and that instance was the citation predicate
being satisfied by the worked example inside its own docstring — and by the positive control of the
test written to prove it could not happen.

That is worth more than a repair would have been. A defect found inside the mechanism built against
it is evidence about the *class* of mechanism, not about one bug. Our unrepaired count stands at
eight distinct instances across this report's own production, each surfaced only by measuring rather
than by reading — including three in the documents describing the other five.

### What a referee should not conclude

This report does not establish that the guard is sufficient; it establishes what the guard measures
and, more usefully, what it does not [E4]. It does not establish that delegation at 47 of 61 is
appropriate; it establishes that the figure exists and can be checked [F8]. And it does not
establish that the recurring family is tractable — only that it is **visible**, which is a weaker and
more defensible claim than the one a cleaner record would have invited.

---

## NOT CLAIMED — carried in full, and repeated verbatim in the short form

- **No results observed.** No simulation has been run.
- **No fit performed.** No parameter value, uncertainty or goodness-of-fit exists.
- **The 3-fold ordering gate is untested.**
- **Coverage is uncomputed**, and no calibration claim is made.
- **No wet-lab validation** of any kind.
- **The ODE is a proof-of-concept two-compartment model**, not a physiological one.
- **The content guard measures one of three prohibitions**, indirectly; the name-association and
  coined-title prohibitions are measured by nothing here.
- **The recurring defect family is open**, not closed.
- **`self-improvement` is a mechanism, never a measured result.**
