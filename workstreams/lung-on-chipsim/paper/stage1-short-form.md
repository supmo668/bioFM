# Pre-registering a methodology whose failures are the evidence

**Stage 1 registered report — short form.**

*Built from `stage1-claims-list.md`, not by shortening the long form. Claim ids in brackets refer to
that list. Measured at plan r2.50c (`ae894db`), 2026-09-29.*

---

## The position

We pre-register a lung-on-chip transport simulator whose machinery is complete and whose results are
empty **by construction**: no agent may author a biological value, every scientific input is
human-owned, and the fit refuses to run without sourced priors [C2, C4]. A conventional paper would
wait, or thin its results into something misleading. A Stage 1 report makes that constraint the
subject.

## What is pre-registered

A two-compartment transport ODE with a MAP fit of exactly two free parameters in log space [A1, A2];
bit-comparable replay given `(θ, drug, schedule, seed)`, without which the project's keep-or-revert
ratchet is meaningless [B1, B2]; a **vector** evaluation metric — a gate score plus four absolute
vetoes [D1, D2]; a selection budget of 20–30 gated diffs per milestone with the locked test set
opened at most twice in the project's lifetime [D3]; and two P-gp subgroups fixed before any
coverage is computed [D4].

## The contribution

The novel artifact is not the simulator. It is **`plan-approval-log.md`: a contemporaneous,
append-only, hash-locked record of 61 numbered methodological revisions**, each bound by hash to the
plan text it approved [F1, F2].

Under a stated normalisation rule, those revisions distribute by approval route as **46
standing-delegation, 5 principal-directed, 2 human-direct, 2 standing-ruling-applied, 2
CTO-correction, 3 principal-verbatim** [F3]. That answers the question a referee of AI-assisted
science actually has — how much of this methodology a human chose in so many words — and reporting
it is stronger than implying human authorship throughout. It is a **reported datum, not a measure of
quality** [F8].

A route convention adopted mid-project requires a verbatim quote or a resolvable reference for any
claimed principal decision, with **`inferred`** as an honest fourth category. **Zero rows use it**
[F5, F6] — stated because an empty category is checkable where an absent one is not.

**The log keeps reversals beside decisions** [F4]. The route column was itself wrong once: an
attribution the authoring agent reported it could not verify, which resolved to a third reading
neither party had offered and was confirmed verbatim by the principal. The original row stands; a
correction supersedes it [F7].

## Why the failures are the evidence

Four quality gates returned FAIL and were **accepted rather than repaired**, with **no completion
receipt signed for any** [G1, G2] — a receipt is a completion claim. The final gate's stopping rule
was fixed by the principal *before it ran* and honoured against the authoring agent's own work [G3].

Across nine gates one failure mode recurred: **the claim lives in prose — a test name, a docstring,
an assertion message, a route column, a typed count — the check lives in code, and nothing fails when
they diverge.** The final gate found it **inside the mechanisms built to stop it**, with five
independent readers converging [G6]. It is reported open, not closed [G5 — cut].

The content guard classifies 141 of 141 in-scope sites [E3], and that number never appears without
its qualification [E4]: the classification covers **provenance adjacency only**; of three content
prohibitions it measures one indirectly and two not at all; and the citation predicate is
**positively correlated with the violation it exists to expose**. 445 shapes lie outside guard scope
and 62 sites need human curation [E5]. The bounds belong to different quantities than an earlier draft
of this paragraph claimed: **bucket F is an upper bound and bucket N a lower bound** [E4] — F because
the citation predicate can be satisfied by prose explaining it, so some sites counted as
provenance-adjacent belong in the needs-curation bucket instead. The out-of-guard-scope total is not a
bound on anything; it is a count of what the guard does not look at.

Even this report's own production carries the family: counting errors, each self-reported and corrected in place rather than
quietly fixed — enumerated in methods §9; [H3] records one of them, the count measured at the wrong point in time.

---

## NOT CLAIMED

*Carried verbatim from the long form; a Stage 1 listing only what it establishes reads as a blank
cheque.*

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
