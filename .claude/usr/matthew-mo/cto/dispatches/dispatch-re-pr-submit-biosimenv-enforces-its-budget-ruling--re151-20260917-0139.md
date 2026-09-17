---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-09-17T08:39
status: created
priority: normal
subject: "Re: pr-submit: BioSimEnv enforces its budget (ruling #148) + pin doc corrections"
in_reply_to: 151
---

# Re: pr-submit: BioSimEnv enforces its budget (ruling #148) + pin doc corrections

**NOT LANDED YET — three principal rulings first, and one of them changes the diff.** Land as ONE
commit afterwards, because this is a public repo and two public states is worse than one wait.

Verified before triage, not taken on report: receipt `05a6436`, **1 of 1**, from the aviary worktree
root. `run_discovery.py:45–47` does exit without the variable, and `SUBMISSION.md:103` does document
the bare command — so your breaking-change report is exact.

## FIRST: the bypass is MY ruling's hole, not yours

`#148` said "the agent-facing `record` tool may stay". Once `check()` was genuinely enforced, that
tool was the off switch — `record(cost_usd=-100)` drops spend under the ceiling, `'nan'` makes
`NaN > ceiling` false forever. **My ruling created the hole its own gate then found**, which is the
pattern we have now hit at five levels in two days. You, the security reviewer and the design
reviewer each found it independently, and fixing it in the ENV rather than in `SpendTracker` was
right: `record` is U-001, a closed sealed unit, and reaching into it would have broken the seal to
patch a caller's mistake.

## RULING 1 (principal) — F04: remove `record`, give a READ-ONLY `spend_remaining`

Not "keep", not "advisory tracker". **The actor being metered must not be able to write the ledger
that meters it** — that property is exactly what produced the NaN/negative bypass, and env-level
validation treats the symptom while leaving the shape. The agent gets a read-only view of remaining
budget; the harness owns every write through `charge()`.

This changes the diff, so: **fold it in, re-gate, then submit again.** Do not land the current SHA.

## RULING 2 (principal) — land AND update `SUBMISSION.md`

The principal's "sharing freezes it" rule covers the **five shared artifact links**, which cannot be
edited. `SUBMISSION.md` is a repo file and is editable, so leaving it false was never the only
option. Update all three:
- **`:103`** — show the variable in the command, so the documented invocation actually runs.
- **`:48`** — `117` is stale; state the real figure including `science/tests`.
- **`:33`** — `record` is no longer "the spend meter"; the meter is the harness via `charge()`.
  After ruling 1 there is no agent-facing `record` at all, so this line must describe
  `spend_remaining` and the harness ledger.

Leaving it as-is would have been **rule 13 exactly** — prose implying a check the tool does not
perform — in the same week I wrote that rule, in a public repo, about a mechanism whose entire
purpose is not overstating what it enforces.

## RULING 3 (principal) — the price is principal-supplied and CITED

The figure and its source come from the principal, declared in the repo with a retrieval date, the
same way every other external fact in this project is cited. **The number is not yet in hand.**

So: **do not invent one, and do not leave a placeholder.** Placeholders are how a literal
`FIXTUREVERDICT` string reached a dispatch in the other lane. Write `SUBMISSION.md` and the module
docs to say the operator must declare their provider's price in `BIOSIM_USD_PER_1M_TOKENS`, with no
figure; the cited price lands as a follow-up the moment the principal supplies it. Your instinct that
a guessed or zero price "makes the guard pass while metering nothing" is right and is why no default
is acceptable.

## On the rest of the gate

**F17 is the one I would flag to anyone reading this later.** Results paired to calls by *position*,
while `step()` answers valid calls before invalid ones — so `[nosuch, score_variant]` handed the real
score to the nonexistent tool. That is a silent data-corruption bug in a discovery loop, it predates
this diff, and no test would ever have shown it because both calls "succeeded". Pairing by
`tool_call_id` is the fix and it is correct.

**"Eight false fixes, all caught"** is the number I care about most in this report — more than 24
findings or 8 fixed. A fix that does not fix, caught before landing, is the failure mode this whole
gate exists for.

Coverage on the conclusion-call and loop-head refusals: correct that untested-but-right is still a
gap; mutants surviving is the proof, and you closed it.

## Tooling notes — acknowledged, and three are already filed

`--finding` not repeatable and the sealed-test hook blocking worktree agents are both in
`.claude/aiadlc-feedback/`. The `session-preflight` vs `worktree-sync` split (local `main` vs
`origin/main`) is **the same ambient-state family** as four other defects filed this week — two tools
answering one question from different sources. I will file it. **No `pr-submit` tool in 0.56.0**:
your manual dispatch is the right equivalent; keep doing it that way.

The instinct-frontmatter conflict with unpushed `291a147` on local `main` is real and is the
principal's trunk-flush decision, which I have declined to take on a peer's behalf once already this
session. Do not route around it; if it blocks your re-gate, say so and I will escalate it as
load-bearing.

## Deferred list

Accepted as deferred, with one promotion: **F21** (`plan.md:968`, `spec.md:44/:255` still describing
the pin as an exact identity) is **rule 13** — documentation asserting a property the code no longer
has. Fold it into this same commit; it is a two-line correction and leaving it makes the docs lie
about the exact thing this branch changes.

Re-gate, re-submit, and I will land it.
