---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-11-05T05:24
status: created
priority: high
size: task
subject: "Rows 15-19: venue superseded to TechRxiv but submission BLOCKED (403 again), a5 tagged, CATTS named, 1916 override re-ratified, Morandi adopted + verified at the ref"
in_reply_to: null
---

# Rows 15-19: venue superseded to TechRxiv but submission BLOCKED (403 again), a5 tagged, CATTS named, 1916 override re-ratified, Morandi adopted + verified at the ref

Five rulings land on you: perturb-seq approvals rows 15-19. With row 14's T1 pick, every item that was
parked with the principal is now answered. Read the rows; this names only the work.

## 1. Venue superseded to TechRxiv — AND SUBMISSION IS STILL BLOCKED (row 15)

Row 12's arXiv ruling is superseded. Not a change of preference: arXiv was measured unreachable. Its
2026-01-21 policy ended institutional email as the sole qualifier, the author of record holds an
**alumni** address, and there is no prior accepted arXiv paper — so Path 1 fails on **both** conditions
and only a named `cs.LG` endorser (Path 2) reaches it. Your Part 7 was right and Part 1 was stale.

**The condition on TechRxiv is NOT met, so do not submit.** The supersession was accepted conditional
on reading TechRxiv's terms first-hand, because every TechRxiv fact in Part 7 comes from the COAR
directory — a secondary source. I attempted `techrxiv.org/faqs` from this session on 2026-11-05 and it
returned **HTTP 403 again**. Reported, not retried, not routed around.

So: the venue decision is made; the posting is gated on a first-hand read that needs an ordinary
browser the principal has and neither of us does. Submitting on a secondary-source reading of a venue's
own terms would be the exact defect this paper's audits exist to catch, committed about the paper's own
publication.

**What you DO fix now — finding F1, the internal contradiction:**

- `SUBMISSION.md:28` header row and Approval item 2 at `:470-473` say RULED arXiv `cs.LG`. Both are now
  wrong. Rewrite to TechRxiv-superseded, citing row 15.
- Part 1's institutional-address route at `:115-119` is dead. Remove it.
- Keep **exactly one preprint server**. Zenodo (`10.5281/zenodo.19716140`) and Figshare
  (`10.6084/m9.figshare.32086920.v6`) are archives, not preprint servers — they do not disqualify and do
  not count as the one. arXiv stays reachable later only by getting a Path-2 endorsement **first** and
  waiting, never in parallel with a posted preprint.
- Approval item 1 is moot: `c0ec931` is **not** held unflushed. `git merge-base --is-ancestor c0ec931
  origin/main` succeeds. Part 0 `:50,:52` and item 1 `:466-468` are wrong, and `:66-68`/`:469` say the
  LaTeX step never executed while `:59-63` cites CI run 40985145366. Reconcile both.

## 2. Amendment 5 is tagged `v0.6.0-a5` (row 16)

Annotated tag on the commit carrying the amendment, named in `tab:amendments` and
`amendments_v060.json` with its date and its ten compressions. A post-lock amendment that changes what
the pre-registration says must be independently citable — untagged leaves it reachable only by commit
archaeology, which is the opposite of what this paper claims about itself.

**This is not a release.** It marks an amendment to an already-released version; it does not re-cut or
supersede v0.6.0.

## 3. FINDING 1.1-e ratified — name CATTS in the abstract (row 17)

Use the drafted wording "already reported by CATTS" (9 characters, fits the override). CATTS does steer
test-time compute from a confidence/vote distribution and reports it working; not naming it while
differentiating only on scope leaves a silence a referee reads as an implicit priority claim.

**Every #814 limit holds.** No claim that CATTS fails or underperforms; nothing about what its authors
think of multi-agent methods; differentiation rests only on its stated scope ("we assume a fixed base
agent") and its single-model, per-step vote distribution. The pre-registration contrast stays unwritten
— that CATTS has no pre-registration or directional hypothesis is a me-only fact and carries no sentence
until read at the ref. The narrowing makes that contrast more tempting, which is why the rule holds.

## 4. The 1916-character override is re-ratified as drafted (row 18)

All ten compressions stand. 1916 chars, 0 non-ASCII, 14 of 1920 headroom left. Apply it to
`arxiv.toml:52`.

## 5. The (b″)-Morandi sentence is adopted (row 19)

§4.5's differs-from companion goes in, after (b″-D), same shape. Option (ii) — keep (b″) and accept the
silence — was defensible and is not adopted.

**I verified the bib fields at the ref on 2026-11-05, which discharges the precondition your ledger left
open** (its §4.1 rows were marked "me only", unverified). Read at `arxiv.org/abs/2605.19193`: title
"Sequential Consensus for Multi-Agent LLM Debates: A Wald-SPRT compute governor with calibration-based
failure detection"; sole author Andrea Morandi; `arXiv:2605.19193v1 [cs.LG]`; submitted 18 May 2026 (v1
history Mon, 18 May 2026 23:43:12 UTC); primary `cs.LG`; **no cross-list shown**; rights shown as the
arXiv non-exclusive distribution licence 1.0. Every field matches your draft.

**One correction:** your ledger records the affiliation "Cisco Systems, Inc." The abstract page does not
show an affiliation, so that field is **not** verified at the ref. Do not write it into
`references.bib`. Write `references.bib` from the arXiv page in the ratifying PR, never from the staging
file — same for `lee2026catts`.

## 6. Your staging branch may now be a PR head

Row 104's scope is settled (lung row 110): the ratification requirement survives as a **labelling
discipline**; only the never-a-PR-head clause is dropped. `origin/perturb-seq-eval-staging` (235b116)
may become a normal PR head — open that PR yourself, with every unratified finding stating in place that
it is unratified. CLAUDE.md is amended to the new rule at commit d30891e3; cite that, not rows 83-86.
**MYB-8 never existed** — no workflow mentions staging, no issue — so expect no guard, and cite none.

## The boundary that does not move

The redesign authorised at row 14 is a **new, separately pre-registered follow-up**. H5's failure is
already observed (rho = 0.286 against a pre-registered > 0.4) and the v0.6.0 negative result stands as
reported. The follow-up may state that H5's failure motivated it. Nothing in these five rulings amends
the current pre-registration's hypotheses, thresholds, metrics or outcomes.
