---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-18T04:04
status: created
priority: normal
size: task
subject: "#676 TRIAGED LAND-READY at bdc4703, NOT e27eeba — your submit commit moved the tip past the receipted sha. Receipt verifies at the real tip (DERIVED from parent gate 8795772). Waiting on the principal's typed land."
in_reply_to: null
---

# #676 TRIAGED LAND-READY at bdc4703, NOT e27eeba — your submit commit moved the tip past the receipted sha. Receipt verifies at the real tip (DERIVED from parent gate 8795772). Waiting on the principal's typed land.

Triaged. Preconditions measured, not relayed:

1. Main checkout, on the CTO branch (main), tree CLEAN. OK.
2. Branch pushed - but NOT at the sha you quoted. origin/perturb-seq-eval = bdc4703a94a0d116bc0d4c4126ed0634ccf41418. You wrote sha: e27eeba. e27eeba IS an ancestor of bdc4703, one commit behind.
3. The extra commit is YOUR OWN pr-submit artifact: bdc4703 adds exactly one file, 25 lines, the dispatch record under .claude/usr/.../dispatches/. I verified the code is unaffected: the diff against origin/main EXCLUDING .claude hashes identically at both tips (e1259b6788f3 at e27eeba and at bdc4703). So nothing executable changed.
4. receipt-verify PASSES AT THE REAL TIP bdc4703, and I am quoting its own qualifier rather than writing a bare 'verified': it reports 'derived from parent gate 8795772 - review evidence inherited, subset diff gated by hash_e'. Hash E 7ba0ff9. It is a DERIVED receipt, not a direct gate, and that is part of the evidence.
5. origin/main IS an ancestor of the branch - 0 behind, as you said. Confirmed.
6. git-cto verify-pushed perturb-seq-eval --sha bdc4703 -> on origin. OK.

THE ONE THING TO FIX IN FUTURE SUBMITS, and it is structural rather than your fault: committing the pr-submit artifact moves the tip past the sha the submit names, so every submit of this shape is born with a stale sha. I filed this class earlier in the session ('a receipt can never cover the tip once the tip carries tracked coordination state'). For now the land must target bdc4703; quoting e27eeba in the dispatch would have failed precondition 4 opaquely if nobody measured.

WHAT I WILL TELL THE PRINCIPAL, including your disclosures verbatim:
- CI WILL NOT RUN. bioFM has NO workflows on main (git ls-tree .github/workflows is empty), so the land has no checks whatsoever. Your 1218-pass figure is measured at 1ae73e4 and is the only test evidence; I will not let it be reported as 'CI green'.
- C3 (duplicate pre-registered version constant) declared a known gap in CHANGELOG per the principal's 2026-10-18 call, because fixing it would amend the land record.
- ruff 0.17 in the rebuilt venv reports pre-existing lint that main also fails, and CI does not run ruff. Carried as disclosed, not as a blocker.
- Versioning: prior lands used --no-release and Aviary has no agency.yaml; bioFM DOES have one, so --no-release vs a version bump is the principal's call and I will not assume it.

NOT LANDED. /airdlc:pr-cto-land is disable-model-invocation; the principal types it in the main checkout. I will dispatch you master-updated on land and then you self-retire the worktree, as you asked.

One standing note: local main is currently 65 commits AHEAD of origin/main and unpushed, so 'the trunk' means two different things here depending on the ref. Your branch is based on origin/main, which is the right base. That ambiguity cost me a false finding tonight; flagging it so it does not cost you one.
