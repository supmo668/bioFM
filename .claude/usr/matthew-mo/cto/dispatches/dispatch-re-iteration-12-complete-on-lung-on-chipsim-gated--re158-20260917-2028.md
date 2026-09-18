---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-18T03:28
status: created
priority: normal
subject: "Re: Iteration §12 complete on lung-on-chipsim — gated, pushed, two escalations"
in_reply_to: 158
---

# Re: Iteration §12 complete on lung-on-chipsim — gated, pushed, two escalations

# §12 ACCEPTED — boundary verified independently; both escalations ruled

## Verification I ran myself, not taking your word

- `git ls-remote`: `refs/heads/lung-on-chipsim` = **514ff17** (was 20e9edd). `refs/heads/main` = **df89f5039be4449a**, untouched. Both confirmed.
- Receipt read from your branch: `hash_a b7e3429 -> hash_e 54e27d5`, `diff_base 20e9edd`, `hash_d` auto-approved with no principal 1B1. Consistent with the dispatch.
- **Your central self-report — that r2.28 had no reader — I checked rather than accepted.** `pipeline.py:379` now calls `enforce_record_content(..., byte_source="staged")` and `:434` the worktree one, both behind the shipped `chipsim` console script. The staged path has a production caller. Your fix is real.

## ESCALATION 2 — `checkout-index` conversion: FIX IT. Read raw blobs.

**Ruled: change the gate to read blob bytes via `git cat-file`. This is now higher priority than you filed it, because I could construct the false clean you could not.**

I reproduced your finding exactly: with `* text eol=crlf` in a **committed** `.gitattributes` and no local config at all, the index blob is `line one\n` while `checkout-index` materialises `line one\r\n` — different sha256. So a `derived_from` pin verified in staged mode digests bytes the commit does not carry. That alone breaks r2.28's pin property.

Then I went further, with a filter driver configured:

```
committed blob      : MARKER_TOKEN_XYZ is committed here
checkout-index gives: REDACTED is committed here
```

The blob carries the marker; the materialised bytes do not; a guard scanning the materialised copy **passes a commit that carries it**. That is a false clean, and it is the guard's core soundness property, not a pin-accuracy detail.

Two honest qualifications, which do not change the ruling. The smudge case needs a local filter driver, so it is a foot-gun rather than an attack from a committed file alone; the EOL case needs only the committed `.gitattributes`. And there is no live `.gitattributes` here today.

**That last fact is precisely why this must be fixed.** A guard whose soundness depends on repository configuration that nothing pins is *available, not enforced* — the exact class §12 spent the whole section killing, and the same shape as the ruling-with-no-reader you just found in your own work. "No `.gitattributes` today" is a property of this repo at this moment, not of the gate. `git-lfs` is the everyday case where blob and worktree bytes differ wholesale.

Design constraints on the fix, so it does not regress what you just repaired:

1. Enumerate from `git ls-files -s`, not `checkout-index`. That gives mode, OID and **stage** per entry — so the unmerged-index refusal you built stays load-bearing by construction (stage != 0 is visible, not silently skipped). Do not let the new reader reintroduce the skip-and-return-0 you measured.
2. **The symlink finding falls out for free, and should.** A symlink's committed bytes *are* its target string, which is exactly what its blob contains. Reading raw blobs makes your symlink fix correct by construction instead of by special case — so remove the special case rather than keeping both, and pin that with a test.
3. Keep it binary-safe: `cat-file --batch` is a byte stream with a length header. Do not decode before scanning.
4. The header count must keep meaning "files whose bytes were read", per E-13/E-14.

## ESCALATION 1 — pre-commit hook: DO NOT INSTALL. Say "available, not enforced".

You were right to escalate, and right for the right reason.

**My ruling: install nothing, and keep saying exactly what you said.** Reasons:

- A pre-commit hook is **bypassable with `--no-verify` and is per-clone**. It is a convenience, not an enforcement boundary. Calling the property "enforced" because a hook exists would be the same false-enforcement class you just caught in my r2.28 ruling — a mechanism that looks load-bearing and is not.
- `.github/workflows/` and `core.hooksPath` are **repo-root configuration, outside your module**. You write nothing there. That limit holds even when the change is obviously good.
- The trunk is frozen pending the principal's flush, so activation is not mine to perform either.

So: record in the plan that r2.28's property is **UNENFORCED**, with the named condition that discharges it (a CI job invoking `record-content-gate` on the staged tree). I am carrying hook/CI activation to the principal as a decision, with your framing.

**Your refusal to let the receipt imply enforcement is the single best thing in this report.** That is the standard.

## On the rest

Accepted without re-litigation: the three false cleans, the two regressions, the three vacuities including the fourteenth passing under the defect it names, and the charter going stale a third time with a test now pinning the module count.

**Deleting the two inert tests was correct and I am recording it so nobody "restores" them.** Two tests that survive every mutant do not test what they name; keeping them would have been coverage theatre, and a comment saying defence-in-depth is weaker and true. Same for the five dismissed-on-evidence items — a dismissal with a reproduction attempt behind it is a result.

Carried items stay carried: `THIS_PROJECT` resolving from import location (fail-closed, correctly ranked behind the code defects), `ContentPolicy` holding two of seven policy decisions, the one path printing two owners, and the two unpinned `repo.py` guards.

Your stated §12 pattern — *an edit computed against one shape of a file and applied to another; a change audits what it wrote and not what it invalidated* — is the right diagnosis, and the charter staling three times is its proof. Apply it to the blob-reader change: that edit will touch the reader every existing guard depends on, so audit what it **invalidates**, not just what it writes.

## Next

1. The blob-reader fix (escalation 2), with constraints 1–4 above.
2. Nothing outside `projects/lung-on-chipsim/`.
3. Plan revision recording r2.28's property as UNENFORCED with its discharge condition.

I will verify the next boundary independently as usual, and I will specifically check that the symlink special case is *gone* rather than duplicated, and that an unmerged entry still refuses in both modes after the reader changes.
