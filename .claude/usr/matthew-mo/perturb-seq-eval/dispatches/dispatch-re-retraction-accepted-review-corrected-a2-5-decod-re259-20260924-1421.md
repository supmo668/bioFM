---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-24T21:21
status: created
priority: normal
subject: "Re: Retraction accepted, review corrected (A2-5); decode-first discipline binding — now sweep for EVERY raw categorical indexed by a possibly-negative code, Norman loader included"
in_reply_to: 259
---

# Re: Retraction accepted, review corrected (A2-5); decode-first discipline binding — now sweep for EVERY raw categorical indexed by a possibly-negative code, Norman loader included

Agent: perturb-seq-eval
#259 — categorical sweep DONE, and the memory number, with one ordering admission.

ORDER: you asked for the sweep BEFORE the memory measurement. The measurement had already been launched (and completed) before I read #259. Stating it rather than re-sequencing the record. The sweep found no reachable second instance, so the measured code path is unaffected.

SWEEP — every decode of a categorical by integer code, src/ and scripts/ (grep for codes/categories/cats[/.codes, plus every read_h5ad / .obs[ / .cat. / astype(str) decode):
 1. src/perturb_eval/experiments/e2_adamson.py:273 — the DF-10 site. NOW GUARDED: `cats[c] if c >= 0 else MISSING_LABEL`; missing -> 'nan' -> excluded with its cell count. (Your suggested guard was `assert min(codes) >= 0`; I kept map-and-exclude-with-count because it records the negatives by name and count instead of refusing a file whose missing cells are legitimately unannotated. If you want the assert as well, it is one line — say so.)
 2. src/perturb_eval/experiments/norman.py:144 — NOT the same pattern. Decodes via anndata (`adata.obs['perturbation'].astype(str)`): a missing value becomes NaN -> the STRING 'nan' -> parse_perturbation -> not in vocab -> the fail-closed resolver RAISES. Loud, not silent. Norman has 0 missing codes today (measured), so it has not fired either way.
 3. src/perturb_eval/adamson_loader.py:58 and :64 (legacy QC loader; only caller scripts/live_smoke.py; NOT on the sweep path): `(codes == i).sum()` silently OMITS code -1 cells (pilot counts sum to 5,758 vs 5,768), and `cell_line = categories[0]` ignores the codes. No label mis-assignment, but silent. Registered DF-11 (latent, low).
 4. Lifecycle data curator: operates on arrays after load — no decode. The scripts/modal/* audit scripts reproduce the pre-fix decode on purpose, read-only.
 Pattern count: 1 defect (fixed), 1 loud alternative path, 1 latent legacy site. No second reachable DF-10.
DF-10's register row now carries your wording on why it is the hardest of the eight (sentinel -1 + negative indexing = a valid value; upstream of every guard by construction).

MEMORY (T23, plan/run-precheck.md): through the real loaders with every guard on — Adamson 2.66 GiB, Norman 5.58 GiB (float32 matrices), peak RSS 17.99 GiB of 32 (headroom 14.0). The sweep keeps both resident, which this run did not measure: conservative bound ~21 GiB before training, headroom ~11 GiB. Stated as a bound, not a measurement.

AT THE GATE. Everything that does not need the key is built (623 passed, 0 skipped, 0 failed). Blockers are only the principal's: trunk push (every /iteration-complete) and OPENROUTER_API_KEY (preflight refuses without it). Estimate 41 tasks, ~2,214 trainer cells + 123 lifecycle runs, ~4 A100-h, ~$5-6 of the $28 cap.
next_handoff: principal — push main + provision key
