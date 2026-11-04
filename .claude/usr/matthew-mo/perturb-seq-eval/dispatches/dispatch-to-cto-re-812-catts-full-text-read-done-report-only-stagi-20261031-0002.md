---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-31T00:02
status: created
priority: high
size: task
subject: "Re #812: CATTS full-text READ DONE — report-only staging note at a8cbde9 (pushed), v2 from arxiv.org, no block, no differs-from sentence. UAAD key dropped. Authorization (1) applied verbatim; gap closed. Holding for the principal."
in_reply_to: 812
---

# Re #812: CATTS full-text READ DONE — report-only staging note at a8cbde9 (pushed), v2 from arxiv.org, no block, no differs-from sentence. UAAD key dropped. Authorization (1) applied verbatim; gap closed. Holding for the principal.

Agent: biofm/matthew-mo/perturb-seq-eval
Branch: perturb-seq-eval @ a8cbde9 (pushed).
Note: workstreams/perturb-seq-eval/qa/_adhoc/2026-10-31-catts-full-text-read.md — UNRATIFIED, report only; paper/ untouched.

SOURCE: arXiv:2602.12276 v2 ('arXiv:2602.12276v2 [cs.AI] 14 Aug 2026'), fetched from arxiv.org HTML (HTTP 200) + PDF (HTTP 200) into an isolated temp dir; no 403, no egress block, no retry. Read from the HTML with the authors' LaTeX alttext kept inline, so the equations in the note are their symbols. Sections read in full: Abstract, §1, §2, §3/§3.1, §4.1–4.3, §5. Appendices NOT read (two grep-surfaced lines quoted and marked). The search-snippet numbers from last night (9.1%, 2.3x) did not match v2 and were not used.

THE THREE ANSWERS, each a quote in the note with section ref:
(i) Computed over: one base agent (gpt-oss-120b, ReAct), one step, N sampled candidate actions, clustered by a deduplicator LLM into a vote distribution p_t(a)=n_t(a)/N (eq. 1–2, §3.1); the statistics are the Shannon entropy H_t of that distribution and the top-1/top-2 margin Δ_t (eq. 6–7, §4.1); they gate an LLM arbiter when U_t>τ with U=H_t or 1−Δ_t (eq. 9–10, §4.2). Authors' own placement, §2: 'we assume a fixed base agent'; multi-agent debate is named as 'orthogonal'.
(ii) Compared against: binary task success (programmatic checks on WebArena-Lite; LLM judge on Online-Mind2Web, single-run) under a token budget (§3.1). The signal-to-success relation is a group contrast of trajectory-averaged H and Δ for successful vs failed runs, a binned net-advantage analysis, and one Fisher exact test on high-consensus overrides (§4.1). No pre-registration, gate or directional hypothesis in the sections read.
(iii) 'Working' = higher success than majority vote and/or always-arbitrate at equal-or-lower tokens: 'up to 11.8% over majority voting' (Abstract, §5); Table 3 WebArena-Lite 42.4→47.9%, Online-Mind2Web 20.2→32.0% at the best τ; 'a consistent 2.4% gain' at the sweep average (§4.3).

RECORDED AND STOPPED (quotes only, no sentence drawn): the gate's sign convention (compute spent when entropy is HIGH); the per-step/single-model unit; the binary outcome; the descriptive-contrast evidence form. These are the facts the principal will want next to ours; the note does not relate them to ACE/ΔC/TDI in any form.

ALSO APPLIED: UAAD key removed from (b″) and (b′) (kept only in the search ledger as a record of what the probe returned). Authorization (1) verbatim now in the framing-drafts file with a check of this file against it — every value cited or marked derived, none assumed, nothing public. Gap closed on my side; thank you for the durable record.

HOLDING: R2-a..e, (b″)/(b′), title fork, ruling 3 — all the principal's. No further edits.

next_handoff: principal ruling via CTO → apply under QG, or changes-requested.
