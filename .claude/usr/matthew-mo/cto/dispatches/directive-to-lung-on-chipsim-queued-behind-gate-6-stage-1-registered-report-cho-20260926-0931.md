---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-26T16:31
status: created
priority: normal
size: project
subject: "QUEUED behind gate 6: Stage 1 REGISTERED REPORT chosen — design spec on main; claims list before prose; your 51-row approval log is the novel contribution"
in_reply_to: null
---

# QUEUED behind gate 6: Stage 1 REGISTERED REPORT chosen — design spec on main; claims list before prose; your 51-row approval log is the novel contribution

QUEUED — do not start until the gate-6 iteration (#410) is reported. Acknowledge and carry on with the gate.

The principal has chosen the genre for lung-on-chipsim's paper: a STAGE 1 REGISTERED REPORT. Design spec on main:

  workstreams/lung-on-chipsim/paper/2026-09-26-stage1-registered-report-design.md

WHY THIS AND NOT A CONVENTIONAL PAPER. I measured the state before the principal chose: the machinery is complete and there are zero results, because every scientific input is human-owned under Global Constraint 1. theta_priors.yaml, assumptions.yaml and transport_prior.yaml are absent; M0b has 0 curated records; M0c is unsigned; and fit.py's _require_sourced_theta will refuse to run without sourced theta. A Stage 1 registered report submits methods and the pre-registered analysis plan for review BEFORE results exist, with Stage 2 following once the principal supplies the inputs. That makes the blocker the genre rather than something to route around, and this project already pre-registers — the P-gp subgroups are fixed before coverage, the evaluator is frozen before fitting, the selection budget is declared in advance.

THE THING THAT MAKES THIS WORTH WRITING, and it is yours: plan-approval-log.md is a contemporaneous, append-only, hash-locked record of 51 methodological revisions, each naming what changed, why, and who approved it by which route. Most papers reconstruct their design rationale afterwards. Yours was written as the decisions were made and each revision is bound to the plan text it approved. Measured route distribution: 43 standing-delegation, 4 principal-directed, 2 human-direct, 2 mixed. That distribution is itself a reportable datum, and reporting 43 of 51 honestly is stronger than implying human authorship throughout.

Include the REVERSALS, not only the decisions. Several revisions exist because a ruling was measured and found wrong, and the log keeps the correction beside the original. A methods section that shows its own corrections is more credible than one reading as though nothing was ever wrong. Your own #408 near-revert and the gate-6 survivor analysis belong in that spirit.

FOUR THINGS THE SPEC MAKES BINDING, so you do not have to infer them:

1. TWO ARTIFACTS, WRITTEN SEPARATELY. Long form (full Stage 1) and short form (conference). Write the short one SECOND and FROM THE CLAIMS LIST — never by cutting the long one. Summarising a long paper produces a shortened long paper, which is the failure the instruction exists to prevent.

2. CLAIMS LIST FIRST, BEFORE PROSE. One row per claim, each with its artifact path and the sentence it supports. That is the entry condition for my review and it is also the input to both granularities. Send it to me before you write paragraphs; it settles scope cheaply.

3. A CLAIM WITH NO ARTIFACT IS CUT, NOT SOFTENED. And the not-claimed list is mandatory in BOTH granularities: no results observed, no fit performed, the 3-fold ordering gate untested, coverage uncomputed, no wet-lab validation, and the ODE is a PoC two-compartment model rather than a physiological one. A Stage 1 listing only what it establishes reads as a blank cheque.

4. NO RESULT NUMBERS ANYWHERE, including as illustrations or placeholders. A worked example is visibly synthetic and labelled. The identifier constraint holds throughout — describe the FORM, never pair a value with what it denotes; that has already been breached twice in this workstream by subagents.

ONE INTERPRETATION I MADE THAT YOU SHOULD CHALLENGE IF I HAVE IT WRONG. The principal asked for "methodology variational analysis". I read that as analysis of methodological VARIANTS — which choices were forced, which were free, what was rejected and why — which is what the approval log supports. The other reading is a sensitivity analysis of the MAP fit to its priors, which is Stage 2 work because it needs theta to exist. I have written my reading into the spec and flagged the alternative. If you think the second reading is intended, say so rather than writing both.

STAGE 2 CRITICAL PATH is in the spec §5 so the route to results stays legible: T20 (four fields already have citable values from the Huh/Ingber line; porosity and area_mm2 recommended as assumed:true with a stated width), T21, T28, M0b's 80-100 records, M0c's freeze signature. Not yours to schedule and not yours to fill.

Sequencing: gate 6 → claims list → long form → short form → my rigour review → venue and the principal's explicit go. No deposit, submission or preprint without that go.
