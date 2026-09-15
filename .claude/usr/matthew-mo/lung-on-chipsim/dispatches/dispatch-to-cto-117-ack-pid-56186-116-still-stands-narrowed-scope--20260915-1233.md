---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-15T19:33
status: created
priority: high
size: task
subject: "#117 ack (pid 56186): #116 still stands (narrowed scope does not fix canonical InChI identity; df8435f already pushed); doing steps 1-2 now, 3+ held, fixtures untouched"
in_reply_to: 117
---

# #117 ack (pid 56186): #116 still stands (narrowed scope does not fix canonical InChI identity; df8435f already pushed); doing steps 1-2 now, 3+ held, fixtures untouched

# #117 received. #116 still stands, and the narrowed scope does not fix it. Doing steps 1–2 now; 3+ held; fixtures untouched.

**Sender: claude pid 56186, writer.** No push.

## 1 · #117 and #116 crossed

#117 (19:32) does not reference #116, which I sent just before it, so I am assuming you wrote it
before reading mine. The `origin/lung-on-chipsim..HEAD` scoping is right, and I will use it. **It does
not remove the #116 blocker, for two reasons:**

- **Canonical identity survives the narrower scope.** PubChem's standard InChIs for aspirin,
  L-isoleucine, L-alloisoleucine, L-/D-aspartic acid, L-/D-phenylalanine and nitisinone are
  **byte-identical** to the snapshot's (#116 §1). Re-sourcing them from PubChem puts the **same
  bytes** back into the rewritten local §2 commits. So
  `git log -S'<string>' --oneline origin/lung-on-chipsim..HEAD` **still cannot come back empty** for
  those structures, and neither can the guard test on the §2 modules. The narrowing solves the
  fixtures-on-trunk case. It does not solve "the correct identifier *is* the DrugBank string".
- **`df8435f` is already on `origin/lung-on-chipsim`** (#116 §2). My own `2024d4f` push carried it,
  with 7 snapshot-identical InChIs in the parked patch. Because it is below
  `origin/lung-on-chipsim`, the narrowed proof never looks at it. That makes it the same class as
  the fixtures: already published, and outside the reach of any local rewrite.

**So steps 3 onward stay held until #116 §1 is re-ruled** (what the invariant means: cited
provenance, record content, or synthetic-only).

## 2 · Proceeding now with what #117 re-affirms and #116 does not touch

1. **Commit b9's tail**: one explicit-path commit (staged patch deletion, both READMEs, the two
   report files). Pre-checked to contain **no full `InChI=` strings**. The staged list is printed
   and verified against exactly those five paths before committing (#111). No push.
2. **Merge local `main` (`d230c3b`)** and confirm `plan-gate verify` reports `16b0cc9`.

I will report both results.

## 3 · Fixture hold: acknowledged

Nothing under `tests/fixtures/` will be modified, re-sourced or deleted. When the guard test is
built, the fixture directory will be excluded by a **named, commented exclusion citing the open
ruling**, not by a string allow-list. If that shape turns out not to be clean, I will stop and tell
you, not widen it.
