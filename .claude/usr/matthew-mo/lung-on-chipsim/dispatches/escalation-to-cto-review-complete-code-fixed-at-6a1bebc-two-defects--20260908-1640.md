---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-08T23:40
status: created
priority: normal
size: task
subject: "REVIEW COMPLETE. Code fixed at 6a1bebc; two defects defeated the halt rule SILENTLY, and the gate found a FIFTH instance in the A&D that falsifies my own r1.6b claim"
in_reply_to: null
---

# REVIEW COMPLETE. Code fixed at 6a1bebc; two defects defeated the halt rule SILENTLY, and the gate found a FIFTH instance in the A&D that falsifies my own r1.6b claim

Review complete — the one trigger you named. Four reviewers, the peer session, and my own
pass. Code fixed and committed at 6a1bebc; A&D findings NOT yet applied. Nothing signed.

TWO DEFECTS DEFEATED THE HALT RULE SILENTLY — both in the optimistic direction

1. ONE-SHOT ITERABLE -> deff BELOW 1.  was iterated three times, so a generator
   exhausted after the first pass and m_A came out 0, giving deff = 1 - icc. A design
   effect below 1 claims MORE independent information than the roster holds. At the
   natural call site — design_effect((len(v) for v in cluster_by_scaffold(s).values()),
   0.5) — it returned 0.5 where correct is 5.4. An 11x optimistic error, no exception.

2. NaN icc PASSED THE GUARD. 'icc < 0 or icc > 1' is False for NaN. deff and n_eff
   became nan, and 'if n_eff < required: halt' never fires, because nan < 20 is False.
   NaN silently authorises the spend. power.py already had the correct form. The two
   halves of the same gate disagreed on their own domain guard.

Neither was reachable through the tests. Both are now fixed with a deff >= 1
post-condition and the NaN-rejecting form.

THE PEER SESSION FOUND THE ONE THAT MATTERS MOST, AND CORRECTED ITSELF DOING IT
Six homologous fatty acids (C8-C13) measured as singleton_fraction 1.0, n_eff(icc=0.8)
= 6.0 — a textbook analog series reported as FULLY INDEPENDENT. Murcko is blind to
acyclic series, and blindness is not evidence of independence. It lands precisely on
transporter substrates: carnitine, choline, amino acids, polyamines. The peer had
earlier recorded a checked negative that acyclic compounds do not wrongly MERGE, and
never asked whether they wrongly SEPARATE — it flagged that gap itself. n_acyclic and
clustering_is_lower_bound now surface it, and every band row carries
n_eff_is_upper_bound so n_eff cannot be read without it.

MY TEST SUITE WAS THE WORST FINDING AGAINST ME
12 tests passed while TEN mutations survived. test_unequal_sizes_beat_the_arithmetic_
mean was FULLY VACUOUS — it recomputed m_A inline and asserted Cauchy-Schwarz against
itself, never calling the implementation. Proven by replacing design_effect with
NotImplementedError: the test still passed. And my 'anti-vacuity guard', assert
max_cluster > 1, was dead code implied by assert max_cluster == 4 four lines above.
Anti-vacuity theatre, written in the same session I spent fixing anti-vacuity theatre.
Root cause: the only exact-value assertion sat at [5]*8, the single point where mean,
size-weighted mean and max all coincide. Rebuilt: 51 tests, m_A backed OUT of the
implementation, membership asserted rather than sizes, all six re-run mutations caught.

A FIFTH INSTANCE, AND IT FALSIFIES MY OWN r1.6b TEXT
The cross-family tier runs at n=20; every power figure governing it was computed at
n=40. My r1.6b fix re-based that tier onto the sign test — which by my own section is
fully exposed to effective n. Measured with the shipped code: 0.69 exchangeable, 0.21
at icc 0.8, against 0.95/0.46 at n=40. So my sentence 'thinning to 20 costs nothing
that was reachable at 40' is true of the CI and FALSE of the sign test, which is now
the tier's conclusion. A tier at 0.21 power can absolutely lose a verdict it would
otherwise have rendered. Introduced by my correction to the fourth instance, exactly
as the fourth was introduced by the correction to the second.

THREE MORE A&D DEFECTS, NOT YET APPLIED
- A&D:1059 STILL SAYS 'the measured icc' — the identical sentence r1.6 excised 250
  lines later, sitting inside the halt rule itself, where it defines the precondition
  of spend. The r1.6 sweep corrected the P7 clause and did not sweep the G3 block.
- Standing-check row 4 gives 'power under the roster's MEASURED clustering (0.46-0.95)'.
  0.95 is P7's series-size-1 icc-0.0 row — the EXCHANGEABLE case, i.e. the exact
  quantity the same cell condemns, one column to its right. It also contradicts
  'realised power is UNKNOWN' since T18 is absent and nothing has been measured on any
  roster. Should read UNKNOWN.
- ASSUMPTIONS A7 still carries 'compound selection MUST maximise diversity' — the
  pre-registration r1.6b withdrew. r1.6b swept the A&D and not the ledger, which is the
  artifact that outlives A&D revisions.

TWO PROVENANCE FINDINGS YOU SHOULD RULE ON
- P7's power table has NO seed, trial count, or driver anywhere in the repo. The n_eff
  column reproduces exactly; the power column does not — (5, 0.8) returns 0.497/0.467/
  0.477/0.520 across seeds, never the recorded 0.46. Within Monte-Carlo noise, so not
  fabrication — but 0.46 is the single number that flips PROCEED to HALT, in a repo
  that enforces seed capture everywhere else.
- The principal's seed-4242 cross-check (half-widths 0.342-0.421 / 0.167-0.206) is
  recorded in the A&D and promoted into ASSUMPTIONS 'Facts established', with no
  dispatch id, receipt, script or output anywhere in the repo. Not disputed — but a
  peer-reported measurement carried as an established fact is the category the
  no-fabrication rule covers. Cite the source or demote it.

INTEGRITY EVENT, REPORTED BY THREE INDEPENDENT SOURCES
Both reviewers and the peer session each received a FALSE report that series.py had
changed on disk — one showing the error guard inverted to return '', one showing every
compound keyed as its own singleton, and the peer told me my tree was dirty. All three
would have produced the OPTIMISTIC, exchangeable answer. All three were false: md5 of
the working file is identical to the committed blob and git status was clean. Every
reviewer verified before acting and none filed a fabricated finding. Recording it
because in a provenance repo a phantom edit presented as fact is itself the threat
model, and because the failure mode was uniform in direction.

470 passed, ruff clean, 6a1bebc. Nothing signed, no batch, nothing sealed, A&D not
approved, five human artifacts absent, ratified false, R2 not started.

next_handoff: rule on the two provenance items (P7 seed, cross-check citation). A&D
fixes are mine and go in the next pass.
