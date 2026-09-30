---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-29T22:41
status: created
priority: high
size: task
subject: "RULING #523: FAIL accepted, no land. Principal: .claude/usr PUBLISHES (as PR #7; scan must cover it); roster gets principal-supplied retrieval dates (HOLD the file, dates follow). Blockers 3+4 FIX (compare falsification test; xfail raises=); checker defects FIX (H4 record, could_not_scan, row extractor, numbering, contradiction check, W/C, digest); OWN-3 FIX; then re-gate"
in_reply_to: null
---

# RULING #523: FAIL accepted, no land. Principal: .claude/usr PUBLISHES (as PR #7; scan must cover it); roster gets principal-supplied retrieval dates (HOLD the file, dates follow). Blockers 3+4 FIX (compare falsification test; xfail raises=); checker defects FIX (H4 record, could_not_scan, row extractor, numbering, contradiction check, W/C, digest); OWN-3 FIX; then re-gate

RULING #523 — FAIL accepted; no receipt; the branch does not land until re-gated. Routed the two publication decisions to the principal; both answered (AskUserQuestion, this session, verbatim options quoted).

BLOCKER 1 — `.claude/usr/**`: PRINCIPAL: "Yes — same as PR #7". It is a tracked, publishable surface: PR #7 (2026-09-27) published 181 such artifacts to the public remote after a no-secrets scan, with the CTO's own retractions in them; the audit chain IS the paper's evidence. The two incident titles stay as written. CONDITION before the receipt: the artifact scan's glob covers `.claude/usr/**` on this branch (counts and verdicts only — never the values), and the scan record cites the commit. A landed surface no scan covers is exactly what you flagged.

BLOCKER 2 — `configs/poc_compounds.yaml`: PRINCIPAL: "I supply retrieval dates". HOLD the file until the dates arrive (asked now; follow-up dispatch carries them). You add ONLY the `retrieved:` field per entry, mechanically, plus one header line saying the dates were principal-supplied (or read from git, if that is what the principal chooses) — no value changes, no lookups. It then clears the same bar as label_structure_reference.yaml and leaves out-of-guard-scope by construction.

BLOCKER 3 — the verdict mechanism (`--compare` untested; mutation proves "HELD" prints regardless): FIX before re-gate. Your falsification probe becomes the test: a pinned file's bytes replaced → `--compare` must report a difference and exit non-zero; unchanged → HELD; both directions, in --self-test as well. Mechanism (2) applied to the instrument that certifies every gate.

BLOCKER 4 — strict xfail swallows any exception: FIX before re-gate. `xfail(strict=True, raises=AssertionError)` (or the specific divergence exception) so only the registered divergence is accepted and a sanitisation raise FAILS; add the mutant you described (a guard that raises before the assertion) as the regression that proves it.

PAPER-CHECKER DEFECTS (reviewers ×4 + you): these are defects in the instruments the paper's claims rest on, not "making the gate quieter" — FIX them, in this order, after 1-4: (i) H4's scan record regenerated over the CURRENT glob (14 files incl. stage1-methods.md, stage1-short-form.md, the design spec, traceability-check.py) and H4 re-bound to it; (ii) could_not_scan computed from the quantity its name says, with the live .gitkeep instance classified (scanned-and-empty per r2.50b) and a test; (iii) the row extractor reads bolded-label rows (test: a bolded `inferred` row is counted); (iv) one numbering scheme in approval-log citations (numbered rows by number; non-numbered rows by date — say which, once, in the methods); (v) the short-form vs long-form contradiction check made real (test: a contradicting short-form limitation FAILS check 4); (vi) W and C exercised through the classifier with a fixture each; (vii) the digest test made non-vacuous for branches. OWN-3: FIX — never execute an environment-supplied bare name; resolve diff-hash by a fixed relative path from the repo root with an existence check, and if it is absent, FAIL the run loudly (no silent empty P1 bucket). Register anything you choose not to fix, with the reason.

E-23 deferrals: 6 of 12 re-discovered and scored DEFERRED-BY-REGISTER — correct; the register holds.

THEN: re-run /pr-prep over the whole diff against origin/main → receipt → /phase-complete (walkthrough + product cut) → pr-submit. The bracket work was right both halves: "held" AND "the check can tell". Say both every time, as you did.
