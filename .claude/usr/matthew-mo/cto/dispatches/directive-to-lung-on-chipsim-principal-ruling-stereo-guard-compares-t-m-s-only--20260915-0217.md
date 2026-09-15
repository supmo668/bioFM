---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-15T09:17
status: created
priority: high
size: task
subject: "PRINCIPAL RULING: stereo guard compares {t,m,s} only, /b excluded; keep-stereo not adopted; canonicality measurement stood down"
in_reply_to: null
---

# PRINCIPAL RULING: stereo guard compares {t,m,s} only, /b excluded; keep-stereo not adopted; canonicality measurement stood down

# PRINCIPAL RULING: the guard compares {/t, /m, /s} only. /b is OUT.

Decided 2026-09-15 on 56186's per-layer table (#104). **This supersedes my #98 wording**, which said four layers including /b. That was my misreading of "stereo", not the principal's words, and the measurement is what caught it.

**The blocking canonicality measurement is STOOD DOWN.** keep-stereo is not adopted, so its input-dependence rate is no longer needed. Don't spend on it. If 56186 has already produced it, send it as a footnote and stop there.

## What to implement (b9 / 49951 — you are the writer)

1. Un-park `workstreams/lung-on-chipsim/parked/2026-09-15-stereo-guard-red-tests.patch` and retarget it to {/t,/m,/s}.
2. In `canonical_inchikey`: after salt-strip + uncharge, record the pre-tautomer InChI's /t, /m and /s layers; canonicalize the tautomer; if ANY of those three changed or vanished, return the PRE-tautomer InChIKey. **/b is not compared** — a double-bond geometry change alone must NOT trigger fallback.
3. Tests, all against real snapshot InChIs:
   - L-/D-Thr, L-Ile/allo-Ile, L-/D-Asp, L-/D-Phe: DISTINCT.
   - Nitisinone keto/enol DB00348/DB08307: still MERGED (unaffected by this layer set).
   - Benzimidazole 1H/3H/CRA_1144: still MERGED — this is the case /b would have wrongly split, so it is the regression test for the ruling.
   - **Malate Ion | Malate Like Intermediate: asserted to SPLIT, as an accepted known loss.** Name the test so it reads as deliberate (e.g. `test_malate_pair_splits_known_accepted_loss`) with the reason in the docstring: they are tautomers of one compound whose pre-tautomer skeleton hashes already differ (BJEPYKJPYRNKOW vs QFBHYOKSQPPXHZ); the guard cannot keep them together without also re-merging true stereoisomers. A known loss with a test is a recorded limit; a known loss without one is a latent surprise.

   Correction for your records: #104 said that pair "differs only in protonation (/p-2 vs /p-1)". I checked the source strings — they also differ in the H layer (`h2,5H,1H2,(H,6,7)(H,8,9)` vs `h1-2,5-7H,(H,8,9)`) and their pre-tautomer first blocks differ. Tautomers, not one compound at two protonation states. The decision is unchanged; the description was wrong.
4. Re-run the merge report on the real snapshot and report the stage breakdown before/after. Expected from 56186's table: tautomer-stage groups 48 -> 7, merge groups 191 -> 156, 41 splits, 0 new merges. **Report what you measure, not what is expected here** — if it disagrees, that disagreement is the finding.
5. Report the source-identical count exactly (100 unguarded; 101 or 102 depending on option, by reclassification not new merges). Do not write "unchanged".
6. Record the malate loss and the aldose/ketose scope question in the limits section of the docs, separately — the second is NOT part of this ruling and stays open.

git-safe-commit, confirm HEAD moved, then the QG receipt. **T4's boundary receipt is still owed to me separately.**
