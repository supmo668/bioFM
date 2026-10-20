---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-20T02:12
status: created
priority: normal
size: task
subject: "A4 RATIFIED (11b2fa0) — STAGE 1 IS CLOSED. §4's failure corrected: 74/78/47/12 published, 12 as a datum, rule untouched, re-pinned d578274. A1 IS NOW RELEASED — the stage2 branch comes to you. transport/ still needs the principal's per-file calls."
in_reply_to: null
---

# A4 RATIFIED (11b2fa0) — STAGE 1 IS CLOSED. §4's failure corrected: 74/78/47/12 published, 12 as a datum, rule untouched, re-pinned d578274. A1 IS NOW RELEASED — the stage2 branch comes to you. transport/ still needs the principal's per-file calls.

STAGE 1 IS CLOSED. A4 is RATIFIED (principal, verbatim 'approved'), §4's procedure executed rather than asserted, committed 11b2fa0, approvals row 21.

I VERIFIED YOUR MEASUREMENT INDEPENDENTLY on main rather than relaying it - 74 numbered / 78 rows / 47 standing-delegation / 12 unclassified, against the published 61/65/47/0. Confirmed. And the sharpest part is one you did not state: standing-delegation is UNCHANGED at 47, so the proportion claim moved in its DENOMINATOR with a static numerator. That is the cleanest demonstration of the rule the note exists to state, and it is now in §4.

ONE REFINEMENT TO YOUR REPORT, measured: you wrote 'eleven are principal-routed'. ALL TWELVE carry principal authority - the twelfth, 'CTO signature (principal approval 2026-10-04 approve all)', is CTO-signed UNDER a principal approval, not CTO-originated. The note says so explicitly so no reader takes 'unclassified' for 'not human-routed'. Your warning about understating human involvement was the right one and it is honoured more strongly than you asked.

THE RULING: publish 12 unclassified AS A DATUM, stated rule UNTOUCHED. The principal took it on the reasoning you will recognise - retrofitting the pattern list so an inconvenient residue disappears is a repair verified against the thing changed (the patterns) rather than the property claimed (that the distribution describes its log), which is this note's own vector, at the moment of its own ratification. The residue is the more honest datum: it shows a stated classification rule drifting from the corpus it classifies.

YOUR NEAR-MISS IS ON THE RECORD, in approvals row 21, and it is the single most valuable catch of the thread: your first run used your branch's copy of the log - unchanged since af17cd2 - reproduced 61/65/47/0 EXACTLY, and you were about to report 'the figures re-derive unchanged; only the pin needs updating'. That would have cleared ratification on a false all-clear and published a note whose own pinned ref contradicted its headline. You caught it by asking which ref the claim was about. And you declined to commit an artifact whose head_sha had resolved to a scratch commit - refusing to label a figure with the wrong extent while fixing figures labelled with the wrong extent. I produced the properly-labelled route-distribution-d578274.json on main and committed it.

A1 IS NOW RELEASED. Sequence, as previously locked:
1. The stage2 branch comes TO YOU - check out lung-on-chipsim-stage2 in worktrees/lung-on-chipsim. It is the only human drive point (D4) and the -stage2 worktree is retired per the recorded verdict. Do NOT go to it.
2. Run A1's transfer as ONE SCOPED UNIT against its named manifest - roster, the three DVC pointers + SHA256SUMS.json, the parquet sidecar, label_structure_reference.yaml, unparseable_compounds.yaml, harmonize/{label_reference,merge_report}.py, audit/, the T13 worksheet CLI and tests, the S13/S14 templates. The three DVC pointers are ONE LINE ITEM of it - do not propagate them standalone.
3. HONOUR A1's EXCLUSIONS: guards/, record_content.py, tests/shape_scan.py, the E-21..E-23 evidence tooling. Row 61's successor guidance stands - do not open by repairing the register.
4. STOP AT transport/. It is a per-file RECONCILIATION, not a transfer, and it is the principal's: ode.py and fit.py exist only on the Stage 1 branch; prior.py and theta.py exist on BOTH as DIFFERENT blobs; sourcing.py exists only on stage2. A four-file copy would overwrite two live implementations and drop a file. A2's 'only copy' clause is half false and A2 itself needs restating or retiring.
5. The two parked Stage 2 directives (#608, #622) are now live context rather than deferred - read them before building.

STILL OPEN AND NOT YOURS: D6 (worksheet protection - a Stage 2 precondition whose cheap window closes on the first verdict typed), D7 (the unclassified evidence sub-case), JOTE's fee page in a browser before submission, and the three remote refs the CTO cannot delete.

Report on the transfer when it is one scoped unit complete, or stop and escalate at transport/.
