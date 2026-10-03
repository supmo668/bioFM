---
type: escalation
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-24T20:54
status: created
priority: high
size: task
subject: "Escalation: 4 real Adamson labels are not gene symbols (PERK, IRE1, 3x, Gal4-4(mod)) — resolver refused; rule the aliases before spend"
in_reply_to: null
---

# Escalation: 4 real Adamson labels are not gene symbols (PERK, IRE1, 3x, Gal4-4(mod)) — resolver refused; rule the aliases before spend

Agent: perturb-seq-eval
Blocking question (data contract — yours to rule, not mine to invent):
The fail-closed target resolver (T7/T8) caught a REAL defect on first contact with the actual Adamson data, during the #245 memory measurement on Modal:
  ValueError: 4 perturbation target gene(s) absent from the gene vocabulary (len=32738); refusing to substitute.
  Missing (label, gene): ('3x','3x'), ('PERK','PERK'), ('IRE1','IRE1'), ('Gal4-4(mod)','Gal4-4(mod)')
Under the old code (e2_adamson.py random-gene fallback) each of these would have been given a RANDOM target gene if sampled — A4 in Adamson, a sixth silent-substitution instance. Checked: NONE of the four appears in the v0.5.0 trainer/lifecycle/summary artifacts, so the published numbers are not contaminated by this one — by sampling luck, not by design. T22's preflight would have refused the sweep on it before any GPU time.

Proposed dispositions (each needs your ruling):
 1. PERK -> EIF2AK3, IRE1 -> ERN1: HGNC symbols for the same genes (Adamson 2016 uses the common names). Implement as an explicit ADAMSON_LABEL_ALIASES table in e2_adamson, applied before resolve, recorded in provenance (label_aliases). Never a fuzzy match.
 2. Gal4-4(mod): a guide against yeast Gal4 — no human target, i.e. a non-targeting control construct. Add to _is_control (alongside '*' and '62(...)'), recorded.
 3. 3x: I believe it is Adamson's triple UPR-sensor knockdown (ATF6 + ERN1 + EIF2AK3), but I cannot confirm from the code, and T7 deliberately rejects triplets. Recommend EXCLUDE from the eligible pool with reason "multi-target construct (3x); triplets unsupported by D1" in provenance.tasks_excluded. Alternative: a 3-tuple target — widens D1, needs your ruling.
 Optional evidence I can collect in the same CPU pass (~cents): mean log-expression of EIF2AK3 in PERK-labelled cells and of ERN1 in IRE1-labelled cells vs control — a knockdown confirms the alias empirically rather than by name.
Context: this is the design working as intended (loud failure before spend). The memory measurement proceeds on Norman meanwhile.
Reply path: rule 1-3 (+ evidence yes/no) -> I implement with a red-then-green test -> rerun the measurement -> hold at the gate.
next_handoff: cto rule adamson labels
