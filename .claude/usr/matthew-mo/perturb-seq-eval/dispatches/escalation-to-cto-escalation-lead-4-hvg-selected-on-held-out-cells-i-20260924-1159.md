---
type: escalation
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-24T18:59
status: created
priority: high
size: task
subject: "Escalation: lead 4 (HVG selected on held-out cells) is verified and on the sweep's trainer path — rule before spend"
in_reply_to: 202
---

# Escalation: lead 4 (HVG selected on held-out cells) is verified and on the sweep's trainer path — rule before spend

Agent: perturb-seq-eval
Re: #202 (regeneration authorised) — one ruling needed BEFORE the sweep spends money. The A6/A2/A4/A5/A7/provenance build proceeds in parallel and does not wait on this.

Blocking question:
1. Lead 4 from #201's unverified list is now VERIFIED: src/perturb_eval/experiments/e2_adamson.py:183-186 computes gene_var over the entire loaded matrix (all perturbations, held-out cells included) and takes top-n_top_hvg BEFORE the held-out split at :251 (train_mask = labels != held). The same ds (via dataset_cache, :243) is reused per held-out task, so every "held-out" MSD the sweep produces is computed on a feature set ranked with the held-out cells' variance. This is on the trainer path #202 tells me to re-run.
   Options: (i) run as-is and report it as a stated limitation in provenance + report; (ii) authorise the fix in this build — HVG on training cells only, recomputed per held-out task (feature space then differs per task; ~36-41 extra variance passes, cheap); (iii) defer to a later run.
   Principal's instruction (1B1 today): escalate before spending rather than choose. My recommendation is (ii) — it is a ~15-line change on one function, the run is happening anyway, and (i) knowingly regenerates a leak.

Context: the other six leads are reported verified/not in the #202 report-back (1 VERIFIED, 2 PARTIAL, 3 VERIFIED, 4 VERIFIED, 5 VERIFIED, 6 PARTIAL — 4 CSVs not 6, 7 VERIFIED). None of the others touches the sweep.

Reply path: rule (i)/(ii)/(iii) → I add or omit the task in the build plan before /grill-me signs it → sweep runs once.
