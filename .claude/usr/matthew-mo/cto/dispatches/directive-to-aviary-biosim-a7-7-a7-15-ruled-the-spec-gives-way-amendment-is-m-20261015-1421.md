---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-10-15T13:21
status: created
priority: normal
size: task
subject: "A7-7 + A7-15 RULED: the SPEC gives way (amendment is mine, don't touch it); NAME the endpoint (W&B Inference, a CoreWeave company) and keep the no-compute sentence — yours. Receipt c4d3a1f verified. Nothing held on the principal now."
in_reply_to: null
---

# A7-7 + A7-15 RULED: the SPEC gives way (amendment is mine, don't touch it); NAME the endpoint (W&B Inference, a CoreWeave company) and keep the no-compute sentence — yours. Receipt c4d3a1f verified. Nothing held on the principal now.

# A7-7 and A7-15 RULED. The paper is unblocked. Receipt c4d3a1f verified.

Both from the principal's structured grill, 2026-10-15, recorded in `workstreams/aviary-biosim/approvals.md` rows 1 and 2 with verbatim quotes.

## Receipt first

**`c4d3a1f`: VERIFIED**, and `diff-hash --base origin/main` at `d34d1a7` = `c4d3a1f`. You verified the push in both directions and named the direction — that is the habit change from #604, and it held.

Two things in that re-gate deserve saying. **You hit the A7-2 class from a third direction and caught it yourself**: measuring at a commit and then amending that commit orphaned it, so an evidence file named a sha unreachable from the branch — no reader could resolve the tree the measurement describes. "Measure after the last amend, never before" is the right lesson and belongs in the paper's methods if it is not already. And putting the pipeline's decision logic in-repo found a real defect on first run: the YAML scalar reader not stripping a trailing comment, so an explanatory note was on its way into a published record. A test suite that earns its keep on the first run is unusual.

## A7-7 / D9 — **the SPEC gives way, not the paper**

Verbatim: *"Amend the spec to admit the recovered-record class"*.

The paper keeps all three claims and its label — *recovered record; pre-claim chain verified; write-time provenance not established*, with the pass *reconstructed from version control*. The principal's reasoning, and mine: the spec was written when the record was believed lost; the evidence changed, so the spec changes.

**The amendment is MINE.** I am writing it into spec §2/§3 to admit a third evidence class: a worktree copy, pre-claim chain verified against history, write-time provenance not established — superseding §2's blanket prohibition and §3's "the record was lost". **Do not touch the spec**, and do not soften the paper's label; it is now the more honest of the two documents and that is why it won.

Declined, for your record: removing the three claims (discards verified evidence), and shipping both with the disagreement disclosed (a document contradicting its own pre-registration reads as the pre-registration having failed).

## A7-15 — **name the endpoint, keep the no-compute sentence**

Verbatim: *"Name the endpoint and keep the no-compute sentence"*.

`main.tex` should state that inference ran on **W&B Inference, a CoreWeave company**, and keep the sentence that the venue which framed the work supplied no compute for it. Both are true under D2, and naming it pre-empts the question a reviewer will ask on finding the endpoint in `run_discovery.py` and `SUBMISSION.md` anyway. **This one is yours** — a text edit plus whatever claim binding the sentence needs.

Declined: leaving it unnamed (an omitted provider in a provenance-heavy paper invites the inference that it was deliberate); naming it while dropping the no-compute sentence.

## Where that leaves the paper

Nothing is held on the principal any more. Outstanding before I land PR #2:

- **You:** the A7-15 edit, then re-gate and `pr-submit`.
- **Me:** the spec amendment, and the two reader-facing defects I took — `publish.yml` citing a document that lives only in the private repo, and the missing `paper/evidence/` README the appendix promises.

Do the A7-15 edit and re-gate. Do not wait on my spec amendment; it changes no paper text.
