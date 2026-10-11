---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-11T04:37
status: created
priority: normal
size: task
subject: "RULING: retire llm_key_source in the code too (4 conditions); then pr-prep/sync/pr-submit; deposit stays held"
in_reply_to: null
---

# RULING: retire llm_key_source in the code too (4 conditions); then pr-prep/sync/pr-submit; deposit stays held

# Ruling — retire `llm_key_source` in the CODE too (re #584, RR-1 @ ded9cfc)

RR-1 accepted as reported: the 6 run files amended, byte-exact re-serialization, manifest 323af965b631ce83 → 70be925de94bfb37 with the superseded row kept, before/after hashes in `run_record_amendments.json` tested against bb3e2e2, 1186 tests, lint clean, tectonic 0 overfull. I have NOT re-run the suite myself; this triage reads your report plus the files in the worktree.

## The ruling

**Retire it in the code.** The principal's words were *"Remove it everywhere, amend the hash"* (2026-10-08, relayed as #582). I verified the field is still live in:
`src/perturb_eval/experiments/provenance.py`, `src/perturb_eval/experiments/v05_preflight.py` (C-KEY-SOURCE), `scripts/modal/app_v05.py`, and the fixtures in `tests/test_provenance.py`, `tests/test_v05_preflight.py`, `tests/test_publish_deposit.py`, `tests/test_label_contract.py`, `tests/test_qg_p0p5_fixes.py`, plus the pyproject email and the CHANGELOG line.

While the writer still exists, a re-run **as documented** re-creates the field. A data-only amendment therefore does not satisfy "everywhere" — it leaves the artifact clean and the pipeline dirty. The code scope is **my application of the principal's words**, not a separate principal ruling; recorded that way in `approvals.md` (row 1, route principal, quoted).

## Conditions (all four)

1. **The retired preflight check is REMOVED, with a dated note saying why** — never left present-but-always-passing. A gate that silently stops checking is worse than no gate; that is this project's own founding finding.
2. **Correct the RR-1 appendix sentence** that says a re-run re-creates the field — in the SAME iteration as the code change, or the paper ships a false statement about its own pipeline.
3. **No recorded hash moves.** Every before/after SHA-256 in `run_record_amendments.json` stays as-is, the bb3e2e2 before-hash test keeps passing, and the superseded-manifest row stands. You are retiring a writer, not re-amending a record. If anything in the amendment record would have to change, STOP and escalate instead.
4. **Ordinary QG + receipt.** This is code, so it takes the normal gate; no new amendment row is needed because the run record does not change.

## Sequence

Code retirement first, then `/pr-prep` → `/sync` → `/pr-submit` as the principal chose — one branch, one receipt, both changes in it. **The deposit stays HELD** for the principal's explicit go; nothing reaches Zenodo or Figshare. `PublishedRecordError` stays named in the publish.yml sequence.
