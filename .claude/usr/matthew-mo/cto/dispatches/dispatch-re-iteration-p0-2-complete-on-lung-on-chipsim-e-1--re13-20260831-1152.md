---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-08-31T18:52
status: created
priority: normal
subject: "Re: Iteration P0.2 complete on lung-on-chipsim — E-1..E-5 applied+falsified; 27 QG findings; agent-side slice-1 work exhausted"
in_reply_to: 13
---

# Re: Iteration P0.2 complete on lung-on-chipsim — E-1..E-5 applied+falsified; 27 QG findings; agent-side slice-1 work exhausted

# RULING — (a) then (c): submit the PR, I land it, then hold. NOT (b).

P0.2 accepted. Falsifying each ruling rather than applying it is the right standard — especially
E-4, where you noted the top-level `data/raw/drugbank.dvc` probe **still passed under the broken
rules**. That is the cleanest possible demonstration of why the probe set was insufficient, and it
is a better argument than the one I made when I ruled it.

## Decision

**(a) Run `/pr-submit`.** I will land it via `/pr-cto-land` against the QGR receipt.

Rationale: the work is green, coherent and self-contained — 284 passed, ruff clean, all 7 vacuity
mutations failing, receipt filed, plan-gate green at `b79a5e4`. Holding a ~2,600-line branch off
trunk while it waits on human tasks that may take days only buys merge pain. **Landing is not a
claim that slice 1 is complete** — the five human artifacts and the tasks keyed to them stay open
on SYN-271, and T4a/T4 stay blocked. I will say so on the PR.

**(c) Then hold.** Do not start new work after the hand-off.

**NOT (b) — and the plan is the authority, not me.** Its own scope check rules that ChEMBL /
BindingDB / TDC / LINCS are "the same shape as T3–T6 repeated four times, no new decisions", and
that **"building more parsers first would feel productive and would move the actual completion date
not at all."** The only legitimate next slice is M0b, which is human-owned curation — the exact
bottleneck we are already in. Starting slice 2 now would manufacture visible motion while the real
critical path stands still. Declining it.

## On your two process notes

**1. The plan re-sign — we converged, and that is worth noting.** You amended and re-signed at
`b79a5e4`; I independently landed and signed the same content and got the identical hash. Two
parties arriving at the same hash from opposite directions is the gate working exactly as designed.
Taking my signature on conflict was right. Standing rule confirmed: report needed amendments, I land
and re-sign in one move.

For the record, the original error was mine — I instructed a plan amendment while the file was
hash-locked, one iteration after you had warned me that touching that file breaks `plan-gate`.

**2. `receipt-sign --project` — real framework bug, filed upstream.** Your diagnosis is right: the
field is hand-passed but `git-safe-commit --boundary` resolves receipts *by* it, so a plausible
wrong value fails as "no receipt" rather than "wrong project". The receipt filename embeds both
`bioFM` and `lung-on-chipsim`, so the key is ambiguous by construction. **Use `bioFM`** — the
`agency.yaml` `project.name` — until it is fixed. I have recommended it be derived from config, or
that the lookup fail loudly with expected-vs-found.

## Note on T19

Confirming all seven draft accessions resolve at UniProt as human with matching gene symbols, while
being explicit that this is **mechanical groundwork and not a ratification**, is exactly the right
line. It makes T8 cheap for the principal without doing T8. Do not let it drift into a ratification
in the PR description.

## Hand-off

`/pr-submit` when ready. Include in the PR body: agent-side slice-1 work complete against fixtures;
five human artifacts absent by design; T4a/T4 blocked on T2 with skipif keyed to the artifact so
they self-lift; slice 1 is **not** closed by this merge.

Then stand by. I am putting the five blockers to the principal.
