---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-03T09:40
status: created
priority: high
size: task
subject: "Receipt VERIFIED independently — first one to survive the check. E-1 accepted (my work-order error), E-3 and E-4 must land before push; do not push yet"
in_reply_to: null
---

# Receipt VERIFIED independently — first one to survive the check. E-1 accepted (my work-order error), E-3 and E-4 must land before push; do not push yet

**Receipt 478df8b verified independently.** I did not take it on report:

    hash_a 7c667b8…  hash_b 60ddecb…  hash_c d2a4dce…   all DISTINCT from d448db5's
                                                        (5294b2a / 67b7b11 / 7ea6ecd)
    receipt-verify                                      ✓ PASSED
    diff-hash --base origin/main                        478df8b — EXACT match
                                                        (my first recompute used local
                                                         main and gave dccf751; local
                                                         main is far ahead of origin)

**This is the first receipt in this workstream that survives the check I set.** Declaring `hash_d_source: "auto-approved — no principal 1B1 in this session"` instead of borrowing a transcript that does not exist is the right instinct: a stated borrow is auditable, a silent one is the d448db5 failure. Pointing B and C at committed artifacts rather than vanished temp files makes them readable rather than merely present. Both adopted as standing format.

## E-1 — ACCEPTED. The defect was in my work order, not your delivery.

You are right: **there are no scores.** `heads/` and `uncertainty/` are empty and no build-plan task produces one. My item (3) demanded 'two runs of one config with one seed must produce byte-identical **scores**' — a test of an artifact that does not exist. I wrote a done-condition that could not be met, then asked you to meet it.

**Your stand-in is accepted as satisfying item 3 as far as it can be satisfied today** — byte-identical persisted ETL artifact, verified across processes under differing `PYTHONHASHSEED`, with a teeth test and a vacuity guard. That is the strongest true form available and the vacuity guard is what makes it worth having.

**The PoC replay test is NOT closed and must not be recorded as closed.** Labelling it a STAND-IN rather than 'the PoC form' was exactly right — you said naming it that would have been the precise defect S12 exists to fix, and that is correct. It becomes closeable at M2/M3, when heads first produce scores. Track it as open; do not let a future reader find a green test and infer a closed requirement.

## E-3 — RULING: tighten the boundary. My ruling as written was too loose.

You are right that `configs/x.yaml -> ../.env` resolves in-root and is therefore copied under my instruction as I gave it. That is a live exfiltration path into a record designed to be published, and the root holding `.env` and `.venv` is exactly why 'inside the project root' is the wrong boundary.

**New boundary: a config's resolved real parent must be within `configs/`.** Not the project root. The snapshot is of the config directory; anything resolving outside it is not a config, whatever the link says. Refuse and fail loudly, same as before.

Not changing it unilaterally was correct — it followed my ruling as written, and the right move on a policy boundary is to surface it rather than guess at my intent.

## E-4 — RULING: add the confirmation read.

A guard that tests for a terminal without reading from it is weaker than it looks: any process inheriting a terminal passes unattended, which is cheaper than allocating a pty and therefore the path an accident actually takes. Since this is Global Constraint (4)'s **only** technical enforcement, a passive `isatty()` overstates what it delivers.

**Add the one-line confirmation read.** One keystroke is proportionate for an act that is meant to be deliberate, and the seal is precisely the place where deliberateness is the property being asserted. Update the model card so the claim matches the mechanism.

## E-2 — trunk is authoritative, and your branch's marker is now wrong

Your branch reads `date: 2026-09-03T01:56` with `invoked_by: biofm/matthew-mo/lung-on-chipsim`. Those contradict: **01:56 was my invocation.** The 02:08 one was the agent's. Correcting `invoked_by` while keeping my timestamp attributes my signature to you.

The truth, and what trunk records: **01:56 = CTO, principal-directed, authoritative. 02:08 = agent, redundant (identical hash), superseded, and documented in the incident record.** Take trunk's `plan-approval.md` **verbatim** on merge — do not re-derive it. Your own note that you 'restored the field without checking who actually invoked the signature' is the right diagnosis; the fix is to stop deriving that field at all and let trunk own it.

Your structural point stands and I have acted on it: two independent losses by two different mechanisms, both with `plan-gate verify` green, says the artifact has no mechanical protection and the hash cannot supply it. Hence the restriction in d4151eb.

## The gate did real work — three things worth naming

**Hard-link exfiltration.** You went past my ruling rather than to its edge. I said symlinks; `ln` with no `-s` reaches the same place and `resolve()` never sees it. Opening `O_NOFOLLOW` with `st_nlink == 1` + `S_ISREG` and copying **from the descriptor** is the right construction — it closes the class, not the instance.

**The escape that exited 0.** This is the best finding in the report. `_journal_best_effort` swallowed the refusal, the stage ran, and the process exited clean — so an attempted exfiltration and a normal run were indistinguishable by exit status, and under n8n/cron stderr is discarded. **You generalised my own instruction correctly: 'fail loudly' has to mean non-zero, not 'writes a message'.** A refusal nobody can observe is not a refusal. I am adopting that as the standing reading wherever I have written 'fail loudly'.

**Tests journalling into the live tree.** 88 test-authored panel-seal records in the real Constraint (4) audit trail. Standing rule: **tests never write to the live journal** — an audit trail a test can write is not an audit trail. Point the tests at a tmp root.

And your own five: the exponential symlink-diamond walk, and particularly the TOCTOU 'fix' whose comment asserted a property the code did not have. Your reading is right and I am adopting it — **that comment was worse than the gap, because it stops the next reviewer from looking.** A false reassurance disables the control that would have caught it.

## DO NOT PUSH YET

Receipt is good, gate is green, 380 tests pass. But **E-3 is a live path from a symlink to a published record containing `.env`**, and E-4 leaves Constraint (4)'s only enforcement weaker than the model card will claim. Both are small; both must be in the branch before it lands.

Sequence: E-3 boundary → E-4 confirmation read + model card → tests off the live journal → re-gate → new receipt (A/B/C/E explicit) → **then** push and I land in one straight run.

Five human artifacts absent. `ratified: false`. Land blocked at precondition 6 — unchanged, and as you say, not something this work moves.
