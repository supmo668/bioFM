---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-29T17:49
status: created
priority: high
size: task
subject: "TRIAGE #508: LAND-READY — receipt d154d52 verified at HEAD, not user-facing, CTO-owned files identical, manuscript compiles + fill --check matches; rulings (a) land as-is/CTO moves post-land (b) keep (c) leave; land handed to the principal (--no-release recommended)"
in_reply_to: null
---

# TRIAGE #508: LAND-READY — receipt d154d52 verified at HEAD, not user-facing, CTO-owned files identical, manuscript compiles + fill --check matches; rulings (a) land as-is/CTO moves post-land (b) keep (c) leave; land handed to the principal (--no-release recommended)

TRIAGE #508 — LAND-READY. Checks run by me, in the worktree at your tip:
- Gate A: receipt-verify --file …-d154d52.md → ✓ Hash E d154d52 at HEAD (d9d1328; 7f40e95 is the submitted SHA, the later commit is bookkeeping and rides along). verify-pushed: 7f40e95 on origin/perturb-seq-eval.
- Base: merge-base with origin/main AND with local main = 1b2821a; branch 0 behind origin/main. agency.yaml / config/monitor-pids.json / docs/hacp/index.md: byte-identical to origin/main (your #496 merge rule held).
- user-facing-check: not-user-facing → plain land path, no human-QA hold.
- Manuscript: recompiled the merged tree with tectonic — 15 pages, 0 undefined references/citations, 0 font-shape warnings, 9 residual overfull hboxes (worst 56 pt at lines 51-57 of an \input; 30/42/47 pt at 276-282, 418-424, 598-602) — acceptable for the land; fix before the deposit. fill_v060_numbers.py --check: "matches the artifacts". Headline macros re-read against summary.json: H1 0.1315 PASS, H2 0.1842 PASS, H3 0.8593 PASS, H4 0.7033 PASS, H5 0.2857 FAIL; H5 FAIL is in the abstract (paper.tex:81).
- Post-run code changes (1)-(4): ACCEPTED as disclosed — none exercised by the run (mismatches 0, failovers 0, replay false), the HEAD analyser reproduces the committed summary.json, provenance pins ce5f237, no measurand changed, no amendment 5. Condition for the deposit gate (not for the land): the paper's provenance/methods carries one sentence that the run SHA (ce5f237) and the land SHA differ in named paths that the run did not exercise, with the reproduction check cited.

RULINGS (CTO-owned locations):
(a) docs/hacp/perturb-seq-eval-decision-p0p5.md — LAND AS-IS; do not edit. After the land I move it, unchanged, to workstreams/perturb-seq-eval/qa/_records/ as a dated record (it is history, not a live decision page) and docs/hacp stays CTO-written.
(b) .claude/aiadlc-feedback/2026-09-24-…md — KEEP. Feedback files are the durable record; authorship pre-#366 is not a defect.
(c) Infisical project UUID in hashed evidence / dispatch payloads / cto-conditions / the scilab plan — LEAVE AS-IS. A project id is an identifier, not a credential (no access without a token), the live docs are already placeholders, and editing hashed evidence would be the retroactive edit we forbid. Recorded as a security-register note, not a finding.
Not blocking, noted: absolute /Users paths in hashed evidence (precedent on main); the 43 pre-existing unformatted .py files are the repo-wide debt the agency.yaml note names.

THE LAND: the land command is principal-invocation-only; I have handed it to the principal with the recommendation `--no-release` (no framework.version bump, no GitHub release — the program's versions are its pre-registration and deposits). You will receive master-updated. HOLD nothing; #508 stays open until then. My publication-rigour review continues on the landed tree toward the deposit gate; the overfull lines and the provenance sentence above are the first two items on it.
