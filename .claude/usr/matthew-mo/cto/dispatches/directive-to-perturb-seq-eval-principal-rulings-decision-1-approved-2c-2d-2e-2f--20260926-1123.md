---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-26T18:23
status: created
priority: high
size: task
subject: "PRINCIPAL RULINGS: Decision 1 APPROVED; 2c/2d/2e/2f/2g as recommended; entropy-formulation review (F1 blocking: ACE_norm range) -> A2-10/A2-11 pending; Slack channel #research-approvals"
in_reply_to: null
---

# PRINCIPAL RULINGS: Decision 1 APPROVED; 2c/2d/2e/2f/2g as recommended; entropy-formulation review (F1 blocking: ACE_norm range) -> A2-10/A2-11 pending; Slack channel #research-approvals

PRINCIPAL RULINGS, 2026-09-26, given to the CTO directly ("approve all" on the standing list, then specific instructions). Recorded here so amendment 2 can be completed.

DECISION 1: the P0-P5 phase boundary is APPROVED. Make the --boundary phase commit (Hash D = principal approval, cite this dispatch).

DECISION 2, the five still open, all approved AS RECOMMENDED in your brief:
  2c (NEW-1 + C1 backbone): (c) gate H3 on the STATED backbone, omitted fields excluded, executed backbone reported alongside.
  2d C13: (a) one fixed gene universe shared by the trainer and the lifecycle paths for the top-20 DEGs.
  2e C25: (a) amend the text to describe the top-up draw that actually runs; task set unchanged.
  2f C6: (a) dataset and modality in every prompt; each pre-registered version starts with an empty, version-namespaced LLM cache.
  2g C20: (a) state the non-negative-dependence assumption and add the permutation bound.
Together with C1, C3, C2+C8 and C7 (already ruled in the other session), all ten are now ruled.

ONE NEW ITEM FROM THE PRINCIPAL: re-check the mathematical formulations of the agentic entropy measurements. I did the review myself (CTO analysis lane) and committed it on main at:
  workstreams/perturb-seq-eval/qa/_adhoc/2026-09-26-entropy-formulation-review.md  (read it by content: git show main:<path>)
Three findings, the first blocking:
  F1  ACE_norm at tau=1 over confidences in [0,1] has a minimum of about 0.93 for a five-step round (0.89 for three, 0.84 for two): seven percent of its nominal range. With rounded LLM confidences that is a tie machine, and H4/H5 are under-powered by construction. metrics.ace_d already exists with full range and no temperature. RECOMMENDATION A2-10: pre-register ace_d as the ACE_norm feature, softmax version descriptive only. This is a measurand change; I am putting it to the principal now. Draft A2-10 as PENDING with both options stated.
  F2  H3: plug-in entropy is fine at N~138 (Miller-Madow bias about 0.007 nats), but report the corrected value beside it for any breakdown with N<50; h3() hard-codes ceiling ln 3, which is only right if the menu is exactly three: pin the menu (size and members) in the amendment and derive the ceiling from it; state that the 0.5-nat gate sits between an 80/10/10 and a 70/15/15 split; say H3 is a statement about the pool.
  F3  1-dC clips every falling-confidence run to exactly 1.0 (tied with flat runs), discarding the sign. RECOMMENDATION A2-11: pre-register the unclipped dC alongside and use it in the Spearman tests. Also a measurand change; draft as PENDING.
  F1 secondary: ace_norm returns 0.0 for N<=1 while the pre-registration says undefined; per_run_components must enforce "undefined", and the amendment names the test that pins it.

SEQUENCING: fill the five ruled sections now. Add A2-10 and A2-11 as PENDING. I will send the principal's answer on those two, then LOCK amendment 2 (one commit, before any data), then the QG over the measurand-changing fixes, then the #283 sweep from that receipted SHA, conditions unchanged (model_id per call, $12 stop-and-report, $28 kill).

ALSO RESOLVED: the Slack channel for #203's notification is "#research-approvals" (run-variable default may be set to it). The OpenRouter key billing to syntropyhealth-app is confirmed. The author ORCID for publish.yml is on file with me; ask when you build #203's publish.yml and I will supply it into the file (public identifier, not a secret).
