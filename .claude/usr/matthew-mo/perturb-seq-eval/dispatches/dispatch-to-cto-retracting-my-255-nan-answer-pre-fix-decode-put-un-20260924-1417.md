---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-24T21:17
status: created
priority: high
size: task
subject: "RETRACTING my #255 'nan' answer: pre-fix decode put unannotated cells INTO real tasks — v0.5.0 YIPF5 ~91% unannotated (held-out + training). DF-10."
in_reply_to: null
---

# RETRACTING my #255 'nan' answer: pre-fix decode put unannotated cells INTO real tasks — v0.5.0 YIPF5 ~91% unannotated (held-out + training). DF-10.

Agent: perturb-seq-eval
MY #255 ANSWER WAS WRONG, and it is now in your review and the register. Retracting it, with the correct mechanism, measured.

What I said (#255): the 2,919 'nan' cells were "neither control nor target" and affected "gene-variance ranking only". That traced every stage DOWNSTREAM of label decoding and never checked the DECODE itself. The 'nan' label I reasoned about is what anndata produces; the pre-fix loader did not use anndata.

What actually ran (@228d354, e2_adamson.load_adamson_matrix :149-152): `labels_raw = [cats[c] for c in codes]` on the raw h5py categorical. A missing annotation is code -1, and cats[-1] is the file's LAST category. So unannotated cells were silently RELABELLED AS A REAL PERTURBATION. Found by the #253 implementer; I verified it locally (pilot) and on Modal (all four files; evidence qgr/evidence/missing-code-decode.json.txt):
  pilot:  10 cells   -> ZNF326  (557 real -> 567)
  10X005: 296 cells  -> YIPF5   (1 real   -> 297)
  10X010: 2,613 cells-> YIPF5   (574 real -> 3,187)
  Norman: 0 missing codes — unaffected.
After the per-file 200 cap, v0.5.0's combined YIPF5 task was ~91% UNANNOTATED CELLS (~363 of 400); ZNF326 ~1.8%.

EXPOSURE — BOTH HALVES, as #255's rule requires:
  HELD-OUT: YIPF5 and ZNF326 are held-out tasks in v0.5.0 lifecycle_runs.jsonl (not the trainer file). YIPF5's lifecycle MSD was measured on a mostly-unannotated population.
  TRAINING INPUTS: both are real symbols, so both were in target_gene_idx and trained every Adamson task — the 21 trainer tasks and the lifecycle tasks — that did not hold them out. YIPF5's 'perturbation mean' was mostly unannotated cells.
  AFFECTED PUBLISHED NUMBERS: Adamson median best-config MSD 0.147 / GATE_ADAMSON (via training inputs — a second route, independent of DF-07's ATF6); and the lifecycle results that include YIPF5/ZNF326 as held-out tasks.
Eighth silent-substitution instance. Registered as DF-10; the DF-06 'nan' note is marked SUPERSEDED BY DF-10 with the reason.

Your review's DF-06/'nan' wording (which you amended from my #255) needs the same correction — the ~410 bound and "HVG ranking only" are both wrong for the path that ran. I am sorry to send you a second correction on the same row; the discipline from #255 applied, but I ran it on the wrong code path. Adding to my own practice: an exposure answer must start from the DECODE of the raw artifact at the pinned revision, not from the first stage I happen to read.

FIXED IN BUILD (WIP a1… committed): code -1 -> 'nan' -> excluded as 'missing perturbation annotation' with its cell count.
ALSO LANDED (#253 a-f): structural construct parser; ATF6 now pools only ATF6_only_pMJ145 (10X005) + ATF6_pBA586 (10X010) — both single-ATF6 constructs; four multi-gene constructs excluded; 3x/Gal4-4(mod)/62(/63( structural controls; Norman stable-ID joins with 'ensemble_id' pinned (loud if renamed) and cross-check verdicts (CBARP corroborated, FOXL2NB inconclusive); KIAA1804 excluded; Adamson exact-fill pinned for 3x7; 97 eligible single-gene Adamson tasks. Suite 623 passed, 0 skipped, 0 failed.
NEXT: memory measurement on Modal through the real loaders, then report before any GPU spend.
