---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-25T06:41
status: created
priority: high
size: task
subject: "Pre-registration: H4 had components the lifecycle cannot compute — principal ratified ACE + 1−ΔC only; estimators ratified; built BEFORE the sweep"
in_reply_to: null
---

# Pre-registration: H4 had components the lifecycle cannot compute — principal ratified ACE + 1−ΔC only; estimators ratified; built BEFORE the sweep

Agent: perturb-seq-eval
Relaying principal decisions for the record (answered directly, AskUserQuestion) — and a finding that made them necessary.

FINDING: the wording pass drafted H4 as 'Spearman rho > 0.5 for >= 1 of {ACE, 1-dC, CSD, WFR, TDI}'. Checked against the code before committing the pre-registration: TDI's CSD (critique-matrix variance) and WFR (winner flip rate) are defined over the OLD consensus-round framework (RoundMetrics: critique matrix, winner_index). The agentic lifecycle is a role pipeline with no critique matrix and no winner — CSD and WFR are STRUCTURALLY UNDEFINED for it. Pre-registering them would pre-register two tests we already know cannot run. Also: the analyser had NO H4/H5 estimator (tdi_vs_held_out_msd is dead code), and some estimator choices were the implementer's.

PRINCIPAL DECISIONS:
 D-H4: H4 pre-registered over the computable components only — ACE_norm and 1-dC (from per-role llm_confidence, llm-sourced steps only) plus TDI_lifecycle over those two with the hand-set default weights; CSD/WFR declared structurally undefined, stated up front. The title question stays answerable.
 D-EST: estimators ratified as drafted — unit = task, seed-median per task, no in-sample calibration for H4, H4 target = lifecycle final MSD@top-20-DEG, H5 = ridge weights on Adamson applied unchanged to Norman (rho > 0.4), bootstrap CIs over TASKS.
 D-WHEN: estimators built and fixture-tested BEFORE the sweep, so the analysis code is locked, not only the plan (a stronger pre-registration than #265 (a) asked for).
In flight: preregistered.py (H1-H5 gate results with evaluable/pass=None semantics; H1/H2 dispersion + bootstrap + Norman strata split per the review's R4), wired into analyse_v05_run; summary will carry the provenance.preregistration record. Then PREREGISTRATION.md is committed and its commit becomes the SHA the sweep's record 0 pins (C-PREREG, already enforced in preflight).
Also landed: provenance.llm_key_source records store/project/env + cross_project=true (your #265 note); preflight refuses a run without it. Wording pass committed (27 \pending, v0.5.0 numbers mapped one-to-one to register rows in corrections.tex, no estimates).
