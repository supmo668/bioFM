---
type: pr-submit
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-11-04T16:33
status: created
priority: high
size: task
subject: "Ready for PR landing (DRAFT requested): lung-on-chipsim coordination flush @ 56de8669, diff-hash da83b30, receipt verified — 9 QG findings fixed incl. a personal-email leak; precondition 4 tool-blocked on the known branch-name defect; F-15 public-surface question is yours"
in_reply_to: null
---

# Ready for PR landing (DRAFT requested): lung-on-chipsim coordination flush @ 56de8669, diff-hash da83b30, receipt verified — 9 QG findings fixed incl. a personal-email leak; precondition 4 tool-blocked on the known branch-name defect; F-15 public-surface question is yours

Agent: lung-on-chipsim · **requesting a DRAFT PR, not ready-for-merge** — reason in §Draft below.

## Ready for PR landing — coordination flush

| | |
|---|---|
| branch | `lung-on-chipsim` |
| SHA | **56de8669** |
| pushed to | `origin/lung-on-chipsim-stage3` = **56de8669** (equals HEAD exactly) |
| diff-hash | **da83b30** vs `origin/main` (600e510b) |
| receipt | `workstreams/lung-on-chipsim/qgr/…-qgr-pr-prep-20261104-1611-da83b30.md` — `receipt-verify` ✓ |
| migrations | none (`migration-delta` empty) |
| draft | **true** |

**Scope:** 19 files, all markdown/metadata, **zero code**. 16 dispatch payloads (rows 95/97/100/102,
OCT1 pass 2, the 26-row re-audit, the SSH escalation and its withdrawal), 1 feedback-ledger entry,
2 hook-written instinct counters. Nothing under `projects/` or `workstreams/` except the receipt
itself; `projects/lung-on-chipsim` subtree byte-identical to the trunk (`89b5c94d` both sides).

## Precondition 4 is TOOL-BLOCKED, and I am not claiming it passed

```
receipt-verify --require-pushed
BLOCKED: origin/lung-on-chipsim (c04e701) and HEAD (56de866) have DIVERGED — reconcile, then re-gate.
```

**This is the defect already filed at
`.claude/aiadlc-feedback/2026-10-31-require-pushed-resolves-the-remote-by-branch-name.md`** — the
check resolves the remote by **branch name**, so it compares HEAD against
`origin/lung-on-chipsim` = **c04e7019**, the *frozen Stage-1 archive*, instead of my actual push
target. Measured: `origin/lung-on-chipsim-stage3` == HEAD == `56de8669`. **The precondition's purpose
— the remote holds the commits the gate saw — is satisfied; the tool's resolution is wrong.**

I have **not** forced it, not re-pointed the remote, and not touched the frozen refs. Flagging it the
same way as last time rather than working around it; you ruled it a framework defect then.

## Gate result: 15 raw findings → 9 survivors ≥80 → all 9 fixed

**One receipt blocker, and it was mine:** three personal email addresses in a dispatch payload headed
for a repo the security reviewer confirmed **PUBLIC**. Redacted to `account A/B/C` at `2131eb25`. The
scorer strengthened it past "no precedent": every commit in this repository uses the
`users.noreply.github.com` identity, so this broke a deliberate, uniformly applied privacy control.
The document's argument needed only that the three accounts were *distinct*, so the literals carried
nothing. **Disclosure: the pre-redaction content is still in `origin/lung-on-chipsim-stage3` history
(pushed before the gate caught it). Scrubbing a pushed branch is outside my lane. Separately,
`origin/main:workstreams/lung-on-chipsim/approvals.md:57` already carries an absolute home path plus
an email, live and public, predating this diff — a remediation item for the principal.**

**Eight prose corrections, most against my own work.** The sharpest: **my own "sound replacement
check" was unsound.** Of its three prescribed grep literals, two are NOT findable to a line-oriented
grep because CLAUDE.md hard-wraps through them — so executed as a grep it reports a *landed* fix as
unlanded, the identical shape the dispatch existed to retire. The genuinely sound check
(`merge-base --is-ancestor`) was in that dispatch's own first paragraph and I labelled the weaker one
sound. Also: a failure rate whose stated band excluded every sample (61.5%, not "~50%"), a file count
presented as a commit count (**51**, per the squash commit's own message), and a misquote I made
while correcting myself.

**The scorer corrected three of the fixes before I applied them** — worth your attention, because as
filed each would have introduced a *new* error: F-11's figure (51, not my 54); "split the feedback
file" (wrong — 8 trunk entries are multi-defect, and CLAUDE.md's split rule governs HACP pages, not
feedback entries); and "no `## Status` section" (**dropped** — the convention appears in 7/57 entries
all within a 3-day window ending 2026-09-26, and the cited lesson does not exist; filing it would
have sent a false convention upstream).

**3 false positives dropped** (45/35/30), one of them mine.

**Checks, all run fresh in the signing turn:** tests **909 passed / 4 skipped / 0 failing** ·
`ruff format --check` 88 files clean · `ruff check` all passed · typecheck **NOTSCOPED** for this
role, reported rather than silently skipped.

## Draft, and why — this is the F-15 question, for you not me

The security reviewer surfaced a public-surface asymmetry and found **your own governing precedent**
on trunk: *"Your instinct not to widen a public surface without my review was right."*

My §1 paper draft deliberately withheld the positive compounds and their DOIs because "including them
would widen a public surface for no gain". But **18 added lines in this PR name Salbutamol and
Pirbuterol with the DOI and reproduce the full 6/18/2/0 verdict split** — on a confirmed-public repo,
while those verdicts are still unratified. Rows 83-86 name the staging *ledger* as the controlled
artifact and dispatches are normal committable coordination exhaust, so I do **not** assert a
violation. But I applied a stricter standard to the paper draft than to my own dispatches, and the
decision-owner is you.

**So: draft PR.** Rule on the asymmetry first; if you want those lines trimmed before merge, say so
and I will re-gate. If you rule them fine as coordination exhaust, flip it to ready.

## CTO action list

1. Decide the F-15 public-surface question (above) — the reason this is a draft.
2. Open the PR as a **draft** from `origin/lung-on-chipsim-stage3` @ `56de8669`.
3. Note that `--require-pushed` will block for you too on the branch-name defect; the substantive
   check is `origin/lung-on-chipsim-stage3` == HEAD.
4. Version bump and landing are yours; I have not touched `framework.version` (trunk is 0.6.0 after
   PR #41).
