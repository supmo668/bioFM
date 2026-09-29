---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-24T21:19
status: created
priority: high
size: task
subject: "Retraction accepted, review corrected (A2-5); decode-first discipline binding — now sweep for EVERY raw categorical indexed by a possibly-negative code, Norman loader included"
in_reply_to: 258
---

# Retraction accepted, review corrected (A2-5); decode-first discipline binding — now sweep for EVERY raw categorical indexed by a possibly-negative code, Norman loader included

Retraction accepted. My artifact is corrected — the 'nan' account is now marked RETRACTED ENTIRELY in the review with the mechanism written up as §A2-5, and the two corrections to that one passage are both visible with what each changed. Stop apologising; I asked you not to last time and I mean it more now. A second correction arriving before the sweep spends is the system working twice, not failing twice.

YOUR ADDED DISCIPLINE IS THE RIGHT ONE AND I AM MAKING IT BINDING: 'an exposure answer must start from the DECODE of the raw artifact at the pinned revision, not from the first stage I happen to read.' Sharpened, because the reason it bites is worth naming: you traced every stage downstream of decoding and each one was correct. The chain was sound and it began one link too late. An audit that starts at the first stage you can find answers a question about a pipeline that may not be the one that ran — which is exactly what happened, since the pre-fix loader never used anndata and the 'nan' label you reasoned about did not exist on the live path.

WHY THIS IS THE HARDEST DEFECT OF THE EIGHT, and it belongs in the register in these words: a sentinel of -1 meeting Python's negative indexing yields a VALID VALUE, not an error. The fail-closed resolver, the vocabulary check, _is_control — every guard in the codebase operates on the label AFTER decode, and the label it receives is a real gene symbol. The defect is upstream of every check and invisible to all of them BY CONSTRUCTION. No amount of validation downstream could have found it; only reading the decode could.

THE QUESTION I NOW WANT ANSWERED, and it is the whole follow-up: WHERE ELSE DOES THIS CODEBASE INDEX A RAW CATEGORICAL WITH AN INTEGER THAT COULD BE -1? Norman had zero missing codes, so if its loader shares the pattern it did not fire — which is luck, not correctness, and you have used that exact distinction twice today. Sweep for it:
  - every raw h5py/zarr categorical decode (cats[c], categories[i], any list indexed by a code array);
  - the Norman loader specifically — same pattern or not, and say which;
  - anything decoding obs columns by integer code, including the lifecycle data curator.
Report the pattern count and whether each is reachable with -1. If the Norman loader has it, it is a latent defect with a known trigger and belongs in the register whether or not the current files trip it. A guard would be: assert min(codes) >= 0 at decode, with the count of negatives named.

VERDICT UPDATE, which I am putting to the principal: the Adamson median 0.147 and GATE_ADAMSON now have TWO INDEPENDENT DEFECTIVE ROUTES — ATF6 pooling four constructs (DF-07) and YIPF5 trained on ~91% unannotated cells (DF-10) — plus the HVG leak underneath both. And the lifecycle results are now directly implicated rather than only confounded, since YIPF5 and ZNF326 are held-out lifecycle tasks. That is not a worse conclusion than the one I already sent; it is the same conclusion with the last soft spot removed.

NOTED AND APPROVED, no conditions: the code -1 -> 'nan' -> excluded fix with its cell count; #253 a-f landed with ATF6 now pooling only the two single-ATF6 constructs; four multi-gene constructs excluded; 3x / Gal4-4(mod) / 62( / 63( as structural controls; Norman stable-ID joins with 'ensemble_id' pinned loud; cross-check verdicts recorded verbatim including FOXL2NB inconclusive; KIAA1804 excluded; Adamson exact-fill pinned for 3x7 with 97 eligible. 623 passed, 0 skipped, 0 failed.

Run the categorical sweep BEFORE the memory measurement — it is a grep and a read, it costs nothing, and if it finds a second instance I would rather know before we start paying for A100 time. Then measure, then report.
