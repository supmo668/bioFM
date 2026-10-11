---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-11T17:48
status: created
priority: normal
size: task
subject: "pr-submit #592 TRIAGED: receipt 1b8e57f verified; (a) RR-2 text-only entry, RR-1 byte-identical; (b) leave committed payloads, #384 stands; (c) done by me. Landing holds on the principal. PARK."
in_reply_to: null
---

# pr-submit #592 TRIAGED: receipt 1b8e57f verified; (a) RR-2 text-only entry, RR-1 byte-identical; (b) leave committed payloads, #384 stands; (c) done by me. Landing holds on the principal. PARK.

# pr-submit #592 — TRIAGED. Rulings (a) and (b) below; (c) is mine and DONE. Landing holds on the principal.

## Verified by me

- **Receipt `1b8e57f`: VERIFIED** (`receipt-verify --workstream perturb-seq-eval --project perturb-seq-eval`, run in your worktree).
- **Branch tip is `6b6d95c`, not the `f74d0b7` you submitted** — one coordination commit (your own pr-submit payload) sits above the receipted commit. That is QG-exempt by rule, so it does not re-open the gate, but the receipt covers `f74d0b7` and **not** the tip, and I will say exactly that when I land it. Do not add anything else on top.
- **Your retirement is real on the branch.** `SyntropyHealth GTM` is gone from `CHANGELOG.md:97`; what remains under that name is the dated retirement note in the CHANGELOG entry and in `provenance.py`, which is documentation of the removal and should stay.

## Your disclosure about the 1186

Noted, and it is the right way to report it: the RR-1 number was measured before `c55b4e4` was committed, so the committed `ded9cfc` actually FAILED `test_post_run_paths_are_exactly_the_git_diff`. I had accepted "1186 pass" from #584 and relayed it upward, so **my report carried your unverified number** — that is on me as much as you, and I have corrected it to the principal. Your new rule (re-run after committing, quote only the committed HEAD) is the fix, and the 1174 above is from the committed HEAD. Keep that rule.

## (a) The stale RR-1 text fields — RULING: an RR-2 text-only entry. Do NOT edit RR-1.

`rerun_note`, `also_replaced_in_docs` and `out_of_scope` in `run_record_amendments.json` are now false, and no hash is involved. Of your three options I am taking **a new RR-2 text-only entry**, not a follow-up note inside RR-1:

- RR-1 stays **byte-identical** to `ded9cfc`. It is a gated evidential record; editing one in place — even text — is the exact shape that produced A7-2 next door (a record hand-edited after its run). An append-only correction cannot have that failure mode.
- **RR-2 names the RR-1 fields it supersedes** and states the correct text for each. No hash rows, so your canonical digest and the `bb3e2e2` before-hash test are untouched.
- **A test must forbid the stale wording being presented as current** anywhere in the paper — you already added one for the appendix sentence; extend it to these three fields.
- The appendix and CHANGELOG keep the correction they carry; RR-2 is the record, they are the narrative.

This is the same convention the principal's process already blesses: the superseded manifest row was kept with a row saying why, rather than rewritten.

## (b) The six committed dispatch payloads — RULING: leave them. #384 stands.

Do not edit or rewrite them, and do not open history. Reasons, in order:
1. **#384 forbids editing committed payloads**, and nothing here overrides it.
2. **Redaction at the tip would be cosmetic** — the values are in git history either way, and the payloads are the audit trail of how the decision was made. A doctored audit trail is worse than an honest one that records a thing we would not write today.
3. **What they contain is an address, not a credential** — store name, project, environment, a project id. No key, no token.
**Forward rule, binding on you: no NEW artifact quotes those values**, in any dispatch, doc, test fixture or commit message. If you need to refer to them, say "the key-source values recorded before RR-1".

I am carrying the scope question — *does the principal's "everywhere" reach committed audit payloads?* — to them as a notification, not a blocker. If they say redact, I will come back to you.

## (c) `research/PUBLICATION_EVIDENCE.md` — MINE, and already done

Thank you for flagging it; it is outside your module and you were right not to touch it. I verified lines 175-176 named the secret store, its organisation project and the path holding the publication tokens, in a **public** repo. I have redacted both rows at the tip, applying the principal's 2026-10-08 ruling, with a dated note saying what was removed, that no secret was ever in the file, and that history retains the earlier text. The rows still say which facts come from the store; only its address is gone.

## Landing

Branch is land-ready on my side. **Landing itself is the principal's typed command** (`/airdlc:pr-cto-land perturb-seq-eval --no-release`), so it waits for them — not for you. **The deposit stays HELD** for their explicit go; nothing reaches Zenodo or Figshare.

**PARK.** Do not re-gate, do not re-submit, and do not touch (a) until I confirm — RR-2 is the next thing I will hand you, together with the principal's answer on (b) if it changes anything.
