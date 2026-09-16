---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-16T21:56
status: created
priority: high
size: task
subject: "§2 iteration complete at 0c4e181 — QGR receipt 061f12d signed + verified (8/9 kept findings fixed incl. F-01 false-agrees bug; F-05 needs your ruling); CORRECTION of #130; push frozen pending your written clearance"
in_reply_to: null
---

# §2 iteration complete at 0c4e181 — QGR receipt 061f12d signed + verified (8/9 kept findings fixed incl. F-01 false-agrees bug; F-05 needs your ruling); CORRECTION of #130; push frozen pending your written clearance

event: iteration-complete
workstream: lung-on-chipsim
iteration: "§2"
branch: lung-on-chipsim
commit_hash: 0c4e181
plan_hash: 33b43a9
qgr_receipt: workstreams/lung-on-chipsim/qgr/bioFM-matthew-mo-lung-on-chipsim-lung-on-chipsim-bioFM-qgr-iteration-complete-20260916-1455-061f12d.md
diff_base: ecda7b0
hash_e: 061f12d72315c4642fed6d94fdf98acd90e24a5306853dd29236562a88a98a00
pushed: NO — push frozen until you verify this receipt and clear it in writing
next_handoff: cto verify receipt → written push clearance (or changes-requested)

## 1. Receipt — verify with
    receipt-verify --workstream lung-on-chipsim --project bioFM     (run FROM THE REPO ROOT — see §5)
Verified by me at HEAD 0c4e181: "1 of 14 receipt(s) verified", Hash E 061f12d.
Hashes: A 14a6dba · B a6b7f50 (findings-20260916-s2.md) · C b8b7d89 (triage-20260916-s2.md) · D = C (auto-approved iteration) · E 061f12d.
Evidence, fresh this session on the committed state: 663 passed / 4 skipped / 0 failed (was 646); ruff clean; stale-revert-check exit 0 after merging main 39480b9; plan-gate verified 33b43a9.

SCOPE DISCLOSURE: ecda7b0...HEAD also contains merged trunk content that is NOT this iteration's work — workstreams/lung-on-chipsim/plan/*, .claude/aiadlc-feedback/*, CTO dispatch files. Disclosed, not claimed.

## 2. Quality gate — 9 kept (>=80), 22 dropped (recorded, not fixed)
Atomic commits, one finding each:
- F-01 [HIGH] 7182b85 — worksheet label verdict aggregated over EVERY name sharing a key. RED BEFORE: rows (L-Proline, D-Proline) on the L key read `agrees` when the correct name came first, `disagrees` otherwise.
- F-02 90b6cde — flag pinned on add_canonical_identity_excluding kept AND excluded frames (the path the pipeline calls; a hardcoded False there left the suite green).
- F-03 262a4f0 — label reference: two entries carried CHARGED keys (-L dianion, -K trianion) that can never match a neutralised pipeline key. Re-derived by running PubChem CIDs 5288700 / 25244520 through chipsim canonicalize() → -N keys; PubChem resolves each name to that CID alone. Measured on the snapshot: the L-Phospholactate row (D structure) now reads `disagrees` (was `unresolved`); the L-myo-inositol-1-phosphate row matches neither enantiomer and stays `unresolved` either way. Loader now rejects duplicate base names, equal L/D keys, and any non-neutral key; a test loads the COMMITTED table (every earlier test used a tmp table).
- F-04 22150f5 — strip keeps /b geometry: abscisic acid (CID 5280896) with its layers made /s2 keeps /b6-5+,10-7-, loses /t /m, and keys differently from both its absolute and all-stereo-free keys.
- F-06 98455c4 — roster_label_disagreements(): REPORTS D-/L- name contradictions per #126 §3; never rejects; no reference → reports nothing rather than guessing.
- F-07 8b2544c — live scan uses `git ls-files -z -s`: NUL split, gitlinks (mode 160000) skipped explicitly, unresolvable tracked paths FAIL, anti-vacuity asserts. The old `.split()` silently skipped any whitespace path (latent: 0 such paths tracked today).
- F-08 6118c50 — ledger tuple check proven able to fail (planted tuple per ledger file + non-ledger negative); window pinned at distance 0/1/2 caught, 3 not, both directions; InChIKey-only case.
- F-09 392b955 — README: module table gains label_reference/merge_report, generated columns, T15 legacy raise. Limits gain the #126 §4 figures verbatim from your ruling (11 = a floor, 1 artifact fixed by the re-key, 75 unresolved, of 134) and the treitol blind spot.

## 3. Decisions needed from you
- F-05 (NOT FIXED — plan-level): T14's worksheet carries `name` beside `canonical_inchikey`. If the filled worksheet lands as a TRACKED configs/pgp_adjudication.csv, that is a name↔structure association in a tracked file. Where does the filled T14 sheet live: tracked (names stripped/redacted on commit?) or untracked under data/?
- F-13 (dropped at 70, raised for ruling): per-row PubChem citation in the label reference vs the table-level source + retrieval date it carries now.
- F-14 (dropped at 70, raised for ruling): the reference YAML's `excluded_as_drugbank_coined` block QUOTES the four excluded names in order to record their exclusion. Keep (audit trail) or describe-without-quoting (the approval-log rule)?
- Build plan (yours, hash-locked): the T13 and T15 interface blocks predate the generated columns and the T15 legacy raise, so they no longer describe the code. Flagged, not edited.
- README honesty change for your awareness: I narrowed "the T18 roster validator honours the flag" to what runs. It rejects flagged keys only when a caller passes them, and no pipeline stage does yet.

## 4. CORRECTION of my own earlier claim
In #130 I told you no code path could produce a false `agrees`. That was FALSE — F-01 was exactly such a path (row-order-dependent, first name wins). Fixed in 7182b85 with a red→green test covering both row orders. Anything you ruled on that premise should be rechecked.

## 5. aiadlc feedback (tooling)
(a) receipt-verify is cwd-sensitive: diff-hash diffs `-- .` relative to cwd, so run from a subdirectory it hashes a SUBTREE and reports "none match current code" for a valid receipt. Hit it this session. The false-BLOCK is the benign direction; a receipt SIGNED from a subdirectory would bind only that subtree. Suggest diff-hash cd to the git toplevel.
(b) git-safe-commit --boundary looks receipts up by config project.name (bioFM), while receipt-sign accepts any --project and names the file after it. Signing with --project lung-on-chipsim produced a valid receipt that the boundary gate could not find. Suggest receipt-sign default/validate --project against project.name.
(c) --finding takes one ID; three files carried two findings each, which forced intermediate-state commits to keep commits atomic. Also: without --staged, git-safe-commit runs `git add -A`, which would sweep in config/monitor-pids.json (dirty in this worktree; not mine; untouched).
