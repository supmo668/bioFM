---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-08-26T18:43
status: created
priority: high
size: task
subject: "Escalation: 6 architecture contradictions block G4 sign on ChipSim M0 slice-1 plan"
in_reply_to: null
---

# Escalation: 6 architecture contradictions block G4 sign on ChipSim M0 slice-1 plan

Agent: lung-on-chipsim
Re: G4 grill of workstreams/lung-on-chipsim/plan/build-plan.md

Principal authorized /grill-me and I am running it. Splitting the findings by lane:
I am grilling the 16 plan-validity defects + the scaffold hole myself. The 6 items
below are ARCHITECTURE, not plan-executability — /design's lane, not mine. I am not
absorbing them into the plan and I will not sign G4 until they are resolved.

Cross-check method: independent agent read build-plan.md (331L), A-and-D.md (457L),
PVR.md (292L) and verified every referenced path on disk.

## BLOCKING — architecture contradictions (need /design amendment)

A1. SCOPE CLAIM CITES A NONEXISTENT SECTION
    Plan L5: "Implements: Design SS1 and SS1.4 only."
    A&D has NO SS1.4. SS1 contains only SS1.2 (L271) and SS1.3 (L281).
    The scope claim cannot be verified against the A&D as written.

A2. SCOPE CLAIM IS FALSE IN BOTH DIRECTIONS
    Plan delivers ONE CELL of SS1's S1 (the DrugBank clause, A&D L260), while
    reaching OUTSIDE SS1 into SS2B (L91 binding-site inventory) and SS2D (L202
    Mondrian P-gp groups).
    Uncovered inside the SS1 it claims: ALL of SS1.3 (four splits + leakage traps,
    L281-293); canonical InChIKey + salt-strip/neutralize/tautomer (L273) --
    explicitly DECLINED at plan L174 with ids.py created by no task; isoform
    collapse + audit side-column (L274); duplicate median-aggregation + IQR s_i
    (L277); SI units + assumed:true + A1-A13 linkage (L279); context.yaml (S8
    L267); structures/ (S4), tox.parquet (S7); and ALL THREE "must exist from
    day one" tests (L406-410: data-contract, leakage, monotonicity).
    Note SS1.3 is circularly deferred: plan L317 defers the evaluator because
    "splits do not exist yet" -- but SS1.3 IS the splits, is inside SS1, and the
    plan claims SS1.

A3. ROLE INVERSION ON PANEL COMPOSITION
    Plan L77 (M3 row): "H owns ... panel composition"
    A&D L55-56:        "The agent may edit mechanism hypotheses, priors, link
                        functions, loss weights, PANEL COMPOSITION and
                        acquisition policy."
    Direct contradiction. Related: plan puts the panel in configs/barrier_panel.yaml
    (L194), but A&D L400 lists only theta_priors.yaml, assumptions.yaml, env.yaml
    under configs/, and A&D L91 assigns the binding-site inventory to theta_priors.yaml.

A4. n8n IS GIVEN A GATING DECISION THE A&D FORBIDS IT
    Plan T16 L296: "five nodes: fetch -> hash-verify -> parse -> CONTRACT TESTS
                    -> write data/processed/"
    A&D L76-78:    "n8n is not a second brain. It computes no metric, weighs no
                    veto... If a decision ever appears inside an n8n workflow, it
                    moves into the evaluator or into the agent's proposal space."
    A&D L341 also puts ETL on "laptop CPU", and A&D L69 scopes exported n8n JSON
    to the DISPATCH verb of the experiment loop, not ETL.
    A&D L443 lists "n8n becomes a second brain" in its own RISK REGISTER. T16 as
    written implements that named risk.

A5. GROUP-SIZE ARITHMETIC CANNOT CLOSE  <-- the one I would fix first
    A&D L202: "two pre-registered groups on one axis -- P-gp substrate status,
               >=30 calibration points EACH, binomial CI on every coverage figure"
    => requires >=60 adjudicated yes/no verdicts.
    PVR L149: PoC compounds = "20-40 inhaled/lung-relevant drugs".
    Plan L110: "~20-40 judgements".
    Plan L281-282: 'unknown' compounds are EXCLUDED FROM BOTH GROUPS, shrinking
    the usable set further below 20-40.
    20-40 total, minus unknowns, cannot yield 2 x >=30. Either the PoC set grows,
    the >=30 threshold changes, or the M5 coverage claim is rescoped. That is a
    design decision. No done-condition in T10-T15 references >=30/group or
    binomial CIs at all.

A6. REPOSITORY ROOT IS AMBIGUOUS -- affects EVERY "Files:" line in the plan
    A&D SS4.4 L386-405 roots a top-level chipsim/ PROJECT dir with the package
    nested at chipsim/chipsim/ingest/, and data/ configs/ orchestration/ tests/
    as siblings INSIDE that project dir.
    Plan writes chipsim/ingest/drugbank_snapshot.py (L142) and chipsim/eval/card.py
    (L302) -- treating chipsim/ as the PACKAGE -- while writing data/raw/ (L122),
    configs/ (L194), tests/ (L243), orchestration/n8n/ (L298) as REPO-ROOT-relative.
    Under the A&D tree both cannot be right. No task states which root applies.
    Compounding: plan L3 and PVR L3 both declare "Module: projects/lung-on-chipsim",
    but the real dir is projects/Lung-on-ChipSIM (case differs), it contains only
    .aiadlc-agent, and it is NOT a submodule (absent from .gitmodules).

## FYI — what I am handling myself (no CTO action needed)

16 plan-validity defects incl.: T7 emits `ratified` as a YAML COMMENT so T9's
RuntimeError guard can never fire; T3 RETURNS hashes but nothing PERSISTS them so
T11's hash-comparison test is unwritable; "PoC compound set" has two incompatible
definitions (drugbank-slim ~1500 auto-filtered rows vs PVR's curated 20-40) making
T13's done-condition uncheckable; T10 hard-codes P08183 which T8 is authorized to
delete -- every label then silently becomes 'unknown' AND T12 still passes; T4's
done-condition passes with DVC never initialized; T15's gate does not detect a
wholly unadjudicated worksheet.
Plus the scaffold hole: 10 of 17 tasks write under directories NO task creates
(chipsim/, tests/, configs/, data/, orchestration/, .dvc/ -- all verified missing);
no pyproject.toml task; no dvc init; no pytest config; no parquet engine in the
stack list though T16 must write parquet. T11 and T17 are marked "(edit)" on files
that do not exist and that no task creates.

## Reply path

Rule on A1-A6 (or route to /design --co-design if any touch another module), then
dispatch me. I will fold the rulings into the grill and only then collect the
principal's "Over and out" for plan-gate sign.

Standing by on the architecture half; grilling the rest with the principal now.
