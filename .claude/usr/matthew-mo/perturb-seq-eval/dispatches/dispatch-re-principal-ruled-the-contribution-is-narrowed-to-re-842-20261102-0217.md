---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-11-02T02:17
status: created
priority: normal
subject: "Re: PRINCIPAL RULED: the contribution is NARROWED to the multi-agent case (perturb-seq approvals row 11). Draft the narrowed contribution statement on a staging branch; nothing reaches paper/ until ratified"
in_reply_to: 842
---

# Re: PRINCIPAL RULED: the contribution is NARROWED to the multi-agent case (perturb-seq approvals row 11). Draft the narrowed contribution statement on a staging branch; nothing reaches paper/ until ratified

# Row 11 delivered on `perturb-seq-eval-staging` — pushed, ready to mirror. All UNRATIFIED.

**Branch:** `origin/perturb-seq-eval-staging` @ `235b116` (based on `origin/main` 5079a12; never a PR head). Worktree at `worktrees/perturb-seq-eval-staging`, identity `perturb-seq-eval-staging`, coordinator cto.
**Ledger:** `workstreams/perturb-seq-eval/findings-staging/2026-11-02-narrowed-contribution-and-titles.md`.
**Moved there unchanged:** `2026-10-30-paper-framing-drafts.md`, `2026-10-31-catts-full-text-read.md` (now under `findings-staging/`); removed from the working branch by a normal commit, `e3a3a1f` on `perturb-seq-eval` — before any PR is opened from it, as you asked.

## The four items, as drafted (ledger §1–§4)
1. **Narrowed contribution statement** — abstract sentence (replaces `paper.tex:56–59`) + intro bullet, given in BOTH orders (current item 1; R2 item 3) since R2 is itself unratified. Every CATTS fact used is one you verified at the ref (§2 "fixed base agent", §3.1 one base model / one step) plus the abstract's own words "vote distribution" and "compute allocation". Nothing from the me-only rows.
2. **Sweep of `paper/`** — 19 rows, each with file:line, the sentence, verdict, drafted replacement. Replace: S1/S2 (abstract universal claim), S3 ("Every such system today…" → "As operated here…"), S6 (bullet), S9 ((b″)+(b″-D)), S12 (`tab:contrib` "Novel …" → "… authored here"). Keep rows listed so you can see what was checked. Two downstream-only rows: the generated CFF abstract and the author-ratified arXiv override abstract (1906/1920 chars — the drafted sentence is longer, so it needs re-deriving + re-ratifying).
3. **(b″-D): consistent — KEEP, and it is now load-bearing** (it IS the row-11 boundary sentence). **(b″): consistent as written, ONE adjacency flagged:** it cites `morandi2026sprt` as gating compute "from a group of agents"; under the narrowed claim a reader will ask how that group-level signal differs from ours, and we hold only its abstract, which cannot carry a differs-from sentence (#809 r2). Options in §3: (i) full-text read of arXiv:2605.19193, report-only, then a (b″-D)-style sentence if you verify at the ref — not started; (ii) accept the silence; (iii) (b′) — same works, same gap.
4. **Title: over-claims in SCOPE, not in result** — "Agent Confidence Entropy", singular, asks the general single-agent question the ruling gives up (CATTS's case); question form asserts nothing.

## Two things you should see before the Notion row
- **`paper/PREREGISTRATION.md:25–29` locks the question-form title**: "A null or failed outcome on H4/H5 must not be traded back into a claim-form title, abstract or contribution list." So ANY retitle is a post-lock amendment to a pre-registered element and must be disclosed there (Amendment 5 would be the form). The file is hash-pinned by the v0.6.0 run record (`app_v05.py:763`), not by CI — an amendment diverges the live hash from the published record, which is the disclosure, not a break. Ledger §4.2 + "Not established". The three row-12 titles are drafted with this constraint stated per candidate.
- **cs.MA (#848 item 2)** is NOT on staging: config edit, going through `/iteration-start → QG → /iteration-complete → /pr-prep → /pr-submit` on the working branch now. Ledger §6 records the planned diff (`arxiv.toml:63` + its comment; the five `SUBMISSION.md` runbook rows that restate the cross-list — strike those if you consider them out of scope).

Nothing under `paper/`, CITATION.cff, bib, Zenodo, Figshare or HACP touched. No arXiv submission on record.
