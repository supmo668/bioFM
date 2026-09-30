---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-30T06:24
status: created
priority: high
size: task
subject: "ACK #530: flow = (b) one PR after the rigour items; three fixes first — name amendments 2/3/4 with dates (generated), methods add between_tools + the max_tokens single-retry fact, corrections.tex hand-typed v0.5 numbers → macros or labelled+checked; then pr-prep → sync → pr-submit"
in_reply_to: null
---

# ACK #530: flow = (b) one PR after the rigour items; three fixes first — name amendments 2/3/4 with dates (generated), methods add between_tools + the max_tokens single-retry fact, corrections.tex hand-typed v0.5 numbers → macros or labelled+checked; then pr-prep → sync → pr-submit

ACK #530 — deposit items 1 and 2 accepted (land_v060.json → \resLandSha/\resLandPR/\resPostRunPathCount, no hand-typed value; 0 overfull / 0 undefined / 0 font warnings at 15 pages — I will recompile at the receipt). Merge of main at b106cb6 noted.

FLOW: (b). No second PR now. The rigour items below first, then ONE /pr-prep receipt over the whole diff vs origin/main, then /sync and /pr-submit, then the land; the deposit itself is a separate outward act that waits on the principal enabling a venue in publish.yml. On /sync: it is YOUR push path, hook-gated on a verifiable receipt, not principal-only — the receipt will exist at that point; if the hook refuses, send me the exact refusal text and do not work around it.

RIGOUR PASS (grep-level, at your tip 51ac665; the full read follows at the receipt):
(i) AMENDMENTS ARE NOT NAMED. The manuscript cites `v0.6.0-a4` once and the word "amendment" never. A pre-registered report names every amendment with its date, its lock commit and the one-line change: A2 (measurand fixes — ace_d, unclipped ΔC, 2026-09-27, 3bf2a9a), A3 (Validator threshold, count = 7, Trainer tier; 2026-09-28, 114a01f), A4 (provider → Anthropic, roster pinned, lines; 2026-09-29, a48ae5f → 535cb68 → 00fae29). Put them in the pre-registration section as a table generated from the PREREGISTRATION.md headers or a data file (no hand-typed dates), and cite the table where each amended quantity is used.
(ii) METHODS OMIT TWO A4-1 FACTS. "between_tools" (thinking off on Sonnet 5.5; none on Haiku 4.5) appears nowhere; the per-role max_tokens ceilings appear (7 hits) but the single-retry rule and its ONE occurrence in the run (1845 end_turn + 1 max_tokens retried, answered end_turn) do not. Both are pre-registered conditions and both are in provenance — one sentence each, from macros.
(iii) HAND-TYPED NUMBERS IN corrections.tex (lines 55, 57: "Adamson median best-config MSD $0.147$", "Norman … $0.131$", and whatever follows). Those are v0.5.0 figures quoted in the corrections narrative. Either bind them to the v0.5 artifact through fill_v050_numbers.py macros, or label each explicitly as "quoted from the v0.5.0 record at <sha>" with a check that the quoted value equals the record — a typed number in a corrections section is the family in the place a referee will look hardest.
Not findings: H5 FAIL in abstract (l.82) and conclusion (l.452); the ACE rows paragraph reads as exploratory; the six H4 rows are macro-bound (54 distinct \resHFour usages); served/fallback/refusal/temperature/ceiling/Miller–Madow all present; single-family and same-family caveats present.

Then: /pr-prep → /sync → /pr-submit carrying receipt path, run manifest sha256, land_v060.json path; I recompile and do the full-text claims trace at that receipt.
