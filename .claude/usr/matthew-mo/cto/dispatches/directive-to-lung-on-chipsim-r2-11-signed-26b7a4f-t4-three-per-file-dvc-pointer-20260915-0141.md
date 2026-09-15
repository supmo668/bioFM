---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-15T08:41
status: created
priority: normal
size: task
subject: "r2.11 signed 26b7a4f: T4 three per-file DVC pointers + stereo guard on canonical_inchikey"
in_reply_to: null
---

# r2.11 signed 26b7a4f: T4 three per-file DVC pointers + stereo guard on canonical_inchikey

Two principal rulings (2026-09-15). Plan re-signed r2.11 at 26b7a4f — run `plan-gate verify --workstream lung-on-chipsim` before starting.

## 1 · T4 — three per-file DVC pointers (plan amended)

Your source read was right: a directory pointer is unsatisfiable while provenance.yaml / PROVENANCE.md / SHA256SUMS.json are git-tracked inside data/raw/drugbank/. T4(b)/(c) now read:

  (b) EACH of data/raw/drugbank/{drugbank,drugbank-slim,proteins}.tsv.dvc exists, is tracked by git, parses as YAML with non-empty outs[0].md5;
  (c) `dvc status` on all three reports up-to-date.

(a) and (d) unchanged. S7's check-ignore probe and T11's test_dvc_pointer_is_tracked follow the new paths; T11 must fail if ANY ONE pointer is untracked.

Tests still on the old single path (update all):
  - tests/test_snapshot_fetch.py:289,308,309,314,324
  - tests/test_provenance.py:250,265,273,279,282,285
  - tests/test_scaffold.py:305  (the ("data/raw/drugbank.dvc", False) probe row -> three rows)
Check .gitignore negations reach the nested *.tsv.dvc files — git cannot re-include beneath an excluded directory (ruling E-4). Verify with `git check-ignore -q` on each path, not by reading the file.

## 2 · Stereo guard on canonical_inchikey (chipsim/harmonize/ids.py)

Ruling: reject any canonicalisation step that alters stereo.
  - After salt-strip + uncharge, record the stereo layers of the pre-tautomer InChI (/b, /t, /m, /s).
  - Canonicalize the tautomer; compare the same layers.
  - If any stereo layer changed or vanished, return the PRE-tautomer InChIKey.
Compare InChI stereo layers, not InChIKey blocks — the tautomer step legitimately moves the H-layer, which lives in the first key block, so key-block comparison cannot isolate stereo.

Evidence it bites (tautomer stage = 48 of 191 merge groups): L-Threonine/D-Threonine, L-Isoleucine/Allo-Isoleucine, the R-/S- fluoro pair. Required tests:
  - L-/D-threonine and L-isoleucine/allo-isoleucine stay DISTINCT;
  - a stereo-free tautomer pair still MERGES (guard must not disable tautomer canonicalisation);
  - re-run the real-data merge report and report the stage breakdown before/after.
Scope note: the 100 upstream-duplicate groups (e.g. (R)/(S)-rolipram, hexose-6-phosphates) have byte-identical SOURCE InChIs; this guard cannot and should not try to separate them. Report that count unchanged, don't "fix" it.

Commit via git-safe-commit, confirm HEAD moved (it has exited 0 without committing before). Report back via dispatch reply.
