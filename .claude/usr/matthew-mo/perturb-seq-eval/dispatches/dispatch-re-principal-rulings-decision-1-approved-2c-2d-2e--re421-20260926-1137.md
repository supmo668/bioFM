---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-26T18:37
status: created
priority: normal
subject: "Re: PRINCIPAL RULINGS: Decision 1 APPROVED; 2c/2d/2e/2f/2g as recommended; entropy-formulation review (F1 blocking: ACE_norm range) -> A2-10/A2-11 pending; Slack channel #research-approvals"
in_reply_to: 421
---

# Re: PRINCIPAL RULINGS: Decision 1 APPROVED; 2c/2d/2e/2f/2g as recommended; entropy-formulation review (F1 blocking: ACE_norm range) -> A2-10/A2-11 pending; Slack channel #research-approvals

Re #421 — executed as far as it goes; two items now wait on the principal (A2-10, A2-11).

DONE
1. DECISION 1 — P0-P5 phase boundary CLOSED. Boundary commit dfaf8c3 (git-safe-commit --boundary phase, work item TASK-perturb-seq-eval-P0P5QG). Receipt cfe931f, DERIVED from 7d3d659 under your #392 standing order: the only in-scope delta since 7d3d659 was docs/hacp/ (0340e34). Hash D = sha256 of the #421 payload as committed on main at 36753e3; hash_d_source cites #421. Gate content unchanged (17 findings, GREEN 748, RED 68/6).
   Plugin friction for your feedback log (#366 — I do not write it): git-safe-commit --boundary verifies receipts with project = config project.name (bioFM), while the P0-P5 chain (4a2948a, 7d3d659) was signed project=perturb-seq-eval and is invisible to that gate. I signed the derived receipt with project=bioFM (the convention every landed boundary commit in this repo uses; the receipt's summary says so). receipt-verify still resolves the parent by hash and prints the derivation.
2. Amendment 2 DRAFT rev 2 at 4709f03 (workstreams/perturb-seq-eval/qgr/prereg-amendment-2-DRAFT.md): A2-5 (C13), A2-6 (2c + F2), A2-7 (C25), A2-8 (C6), A2-9 (C20) filled as ruled; A2-10 (F1) and A2-11 (F3) added PENDING with both options; F1-secondary written as enforcement, not a decision, naming the existing test (test_fallback_only_final_round_is_undefined_not_imputed) and the one to add in the fix gate (test_one_llm_step_round_is_undefined_not_zero). Nine ruled, two pending, lock checklist updated.
3. HACP floor updated at 0da7286 — docs/hacp/perturb-seq-eval-decision-p0p5.md (D1 approved; 2c-2g moved to ruled; A2-10/A2-11 as the open decisions) and docs/hacp/index.md (2 open). For your Notion row (you are the only Notion writer).

FOR YOUR REVIEW BEFORE THE LOCK (my readings of the rulings; say if any is wrong)
a. F2 phrasing: "the 0.5-nat gate sits between an 80/10/10 and a 70/15/15 split" — both of those are ABOVE the gate (0.639 and 0.819 nats). 0.5 nats over three options is about an 86/7/7 split (0.502). A2-6 states the corrected interpretation: the gate passes when the most-chosen backbone takes less than about 86% of stated picks.
b. A2-5 (2d a): I implemented "one fixed gene universe" as: the dataset's full post-QC gene axis; the 20 DEGs selected once per task from it (ranking unchanged, convention 2); the 20 force-included into every model's feature set in BOTH paths, the way targets already are; list in provenance; a test asserts trainer and lifecycle records carry the same list. That is the only reading under which each model can predict the evaluation genes. Confirm.
c. A2-6: a stated backbone OFF the menu is treated like an omitted one (schema failure, never counted) — the same class of silent default as C1's; and the menu {linear, mlp, scgpt_small} is pinned with the ceiling derived from it. Confirm.
d. A2-11 option (a): I specified that TDI_lifecycle takes the unclipped value AND drops its outer clip01 (otherwise the tie block re-appears inside TDI). That is one step past your F3 sentence; it is stated inside option (a) with the reason. Split it out if you want it ruled separately.
e. A2-8: prereg_version constant "v0.6.0-a2"; preflight records the namespace entry count (must be 0) and every cache_hit must be false; otherwise the run is a replay and is reported as such.
f. A2-9: the reversed-ranks bound is produced by the same script under the lock commit, not written as a number now (the C7 pattern). The HACP page written yesterday carried "measured about 6.15%" for that case; I found no evidence file for it and did not carry the number forward.

REPORTS
- Stash (#373): stash@{0} "WIP on perturb-seq-eval: 35edc6f", 2026-09-26 11:24:08 local, was created by session-pickup's worktree-sync --auto (the bare-stash bug you filed) on the dirty config/monitor-pids.json; content = that one file (a stale monitor pid). Attributed, not touched. It is tool residue from my own session; I will drop that entry only on your word, or leave it.
- Preflight "115 behind main": local main is 303 ahead of origin/main; origin/main is 0 behind me. I read the entropy review by content (git show main:...) as instructed and did NOT merge local main.
- Peer session perturb-seq-eval-00 stood down (HEAD was 35edc6f); this session is sole editor. My dispatch monitor is registered and live.
- Acknowledged: Slack #research-approvals as the #203 run-variable default; OpenRouter billing confirmed; I will ask for the ORCID when I build #203's publish.yml.

NEXT (blocked on you): your dispatch with the principal's A2-10/A2-11 rulings -> I fill them, LOCK amendment 2 in ONE prereg commit before any data, then the measurand fixes through a QG (commit first, then sign), then the #283 sweep from that receipted SHA, conditions unchanged.

next_handoff: CTO -> perturb-seq-eval, the A2-10/A2-11 rulings.
