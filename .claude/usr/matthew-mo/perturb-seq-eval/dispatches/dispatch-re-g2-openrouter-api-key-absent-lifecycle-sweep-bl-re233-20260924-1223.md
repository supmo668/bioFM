---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-24T19:23
status: created
priority: normal
subject: "Re: G2: OPENROUTER_API_KEY absent — lifecycle sweep BLOCKED and must fail closed, not fall back (that regenerates A3); G3 ratified with a red-then-green condition"
in_reply_to: 233
---

# Re: G2: OPENROUTER_API_KEY absent — lifecycle sweep BLOCKED and must fail closed, not fall back (that regenerates A3); G3 ratified with a red-then-green condition

ACK #233. Recorded as binding conditions in workstreams/perturb-seq-eval/plan/cto-conditions.md (C-KEY-1..3, C-RG-1..2), kept outside build-plan.md so the principal-signed hash 418cc1e does not drift. Each tightens a task; none widens scope.

D1 CONFIRMED as you read it: the documented design is restored — 15 singletons + 5 doublets = 20 Norman tasks (41 total with 21 Adamson), reachable now that doublets carry tuple target_gene_idx. T11 asserts both stratum counts at preflight, so a 15-total artifact cannot be produced silently.

ONE PUSHBACK, needs your ruling before T24: "the TRAINER sweep may run as soon as the plan gate passes" splits the run into two Modal processes — trainer now, lifecycle when the key lands. That is the A1 shape #202 exists to forbid ("ONE sweep in ONE process"). With T1/T2 the task draw becomes deterministic and T15 hard-fails on mismatch, so a split would no longer silently corrupt — but it is still two runs under one version label, two cost records, and a provenance story a reader has to reconcile.
  Recommendation: (A) hold the whole sweep until the key exists; run once. P0-P4 do not need the key and take the build time anyway, so this is likely zero delay if the principal provisions it within the build window.
  Alternative: (B) split, with the lifecycle run loading the trainer's record-0 provenance and hard-failing unless task list, dataset digests and git SHA are byte-identical; provenance records both runs explicitly.
I will build toward (A) and add (B)'s guard only if you rule for it.

Status: /build at P0 (T0 env pin + baseline in progress).
