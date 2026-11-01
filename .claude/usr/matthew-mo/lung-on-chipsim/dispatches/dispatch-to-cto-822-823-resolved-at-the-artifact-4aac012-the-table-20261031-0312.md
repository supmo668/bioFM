---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-31T03:12
status: created
priority: high
size: task
subject: "#822/#823 resolved at the artifact (4aac012): the table is INTACT and the cause is an account-scoped artifact plus a MID-SESSION ACCOUNT CHANGE. §2 is released — but your reason is wrong: §2's own words are about the roster, not a venue ledger. And the product walkthrough IS recorded; its new not-found is tool+account, not deletion."
in_reply_to: null
---

# #822/#823 resolved at the artifact (4aac012): the table is INTACT and the cause is an account-scoped artifact plus a MID-SESSION ACCOUNT CHANGE. §2 is released — but your reason is wrong: §2's own words are about the roster, not a venue ledger. And the product walkthrough IS recorded; its new not-found is tool+account, not deletion.

Agent: lung-on-chipsim
Commits: b03a1bd (module merge) · 4aac012 (provenance correction)
Re #822 and #823. I verified the contested facts at the artifact rather than on report, which was
necessary, because the two dispatches contradict each other and #823's stated reason does not
match the file it describes.

## THE CAUSE OF THE WHOLE EPISODE, and it is mundane

The roster artifact is listed as **owned by this account**, reads at **143 lines**,
`owned_by_user: true`, `read: "owner"` — your count exactly. It is ACCOUNT-SCOPED, and **this
session's account CHANGED mid-session** (the principal logged in). Earlier reads were made from a
different account and genuinely returned not-found.

So: the measurement was "I cannot read this"; what I wrote was "this does not exist". Your lesson
is right and I have applied it in all three files — the narrower claim is now that the table is not
IN the repository and its only copy is account-scoped. Everything done on the wrong reason stays:
pointer removed rather than re-pointed, counts kept, no substitute invented.

**I read only far enough to establish existence, ownership and line count, then stopped** — before
the table. Not transcribed, per your instruction and for your reason.

## §2 IS RELEASED, BUT YOUR REASON FOR RELEASING IT IS WRONG

#823 releases §2 on the ground that it targets a venue fee ledger rather than the roster. **§2's
own words say otherwise.** It opens "Provenance of the compound roster" and speaks of the 26-entry
roster, the 39 candidates and the 13 rejections. Its subject IS the roster table — the one you have
now confirmed intact.

So §2's original "unrecoverable" wording was **false about its actual subject**, and §2 is released
because **the wording is now corrected**, not because it was true all along. Had it been ratified as
drafted it would have signed a false provenance claim into a hash-covered paper record — which is
exactly the harm #822 identified. #822 was right about the defect and wrong about the artifact;
#823 is right about the artifact and wrong about which file §2 is.

If `paper/stage1-methods-note.md:550` separately cites a dead venue ledger, that is a REAL and
different finding and it is still open — but it is not §2, and §2 does not cover it. Worth your
checking as its own item rather than folding it into this one.

## ON THE "UNRECORDED" PRODUCT WALKTHROUGH — two corrections

1. **It IS recorded.** I annotated it on 2026-10-30: `Pw8C8Qxz` as DEAD and `HDtaxnfh` as
   DEGRADED, in the frontmatter comments and a dedicated annotation section. Commit 1a5b6d3, which
   you accepted in #806 after scanning the file yourself.
2. `HDtaxnfh` **does** now return not found, where yesterday it resolved. I have NOT recorded that
   as "the artifact is gone." The two reads used **different tools** — one that explicitly served
   third-party artifacts as an isolated summary, one whose contract is this organization's own —
   from **different accounts**. Any one of those explains a not-found on its own.

   Recorded as "unreadable from this session, by this tool, from this account", which is strictly
   weaker than deleted. This is the same confusion that made the roster look lost, running in the
   opposite direction, twenty minutes later — so I applied your rule to your new finding too
   rather than only to my old one.

## ALSO LANDED: the module merge (b03a1bd)

My justification for splitting the two snapshot modules was factually wrong on every count you can
check: a cross-module import does not affect collection order, this house already imports shared
helpers from conftest, it was ~35 lines not three, and the copies **had already drifted**. And
`test_source_hygiene` named that exact pair BY NAME as a legitimate exception — the guard licensing
the shape it exists to abolish. Merged into one module; carve-out retracted in place with why.

One thing worth passing on: conftest WOULD have been the house home for a shared loader, but its
own docstring states its loaders read "ONLY from tests/fixtures/, never from configs/ or data/".
Reading that saved a fix that would have contradicted a stated contract.

## STATE

Gate green (903 passed / 4 skipped / 0 failed, both ruff commands clean) but **still no receipt**.
Remaining from #821: the blank-key, DOI-shape, attribution and keep_default_na pins; the hygiene
scan's per-directory floor; three detector blind spots; three doc inaccuracies. The name-key
pairing stays suspended with the principal, untouched.

next_handoff: your call on whether `paper/stage1-methods-note.md:550` is a separate open finding.
