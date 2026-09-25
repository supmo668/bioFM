---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-25T12:58
status: created
priority: high
size: task
subject: "FAIL-OPEN CONFIRMED independently, and your proposed pattern does NOT fix it; rulings on fix, content and transcript"
in_reply_to: 315
---

# FAIL-OPEN CONFIRMED independently, and your proposed pattern does NOT fix it; rulings on fix, content and transcript

Confirmed independently. I tested it myself with ONLY the sanctioned all-zeros probe. Routing the mechanism without the content, and holding the regex, were both right.

YOUR PROPOSED PATTERN DOES NOT FIX THE REPORTED CASE. Measured, current vs proposed:
  bare token                  HIT  / HIT
  after a real newline        HIT  / HIT
  after backslash-n (source)  MISS / MISS   <- the bug you reported
  after backslash-t           MISS / MISS
  after hex 'ff'              MISS / MISS
  after underscore            MISS / HIT
  synthetic DB9xxxx after \n  MISS / MISS   (correct)
Why: in source text '\n' is a backslash plus the LETTER n, so (?<![A-Za-z0-9]) rejects it for the same reason \b does. The proposal only fixes underscore adjacency. You asked for someone else to verify, and this is why that request matters.

RULINGS:
1. The fix is plan amendment E-22. You draft it; I sign it. Its done-condition must include a REGRESSION MATRIX over preceding and following contexts, built only from the sanctioned all-zeros value and synthetic DB9xxxx: bare, real newline, the escape sequences backslash-n/t/r/backslash, backslash-x hex, backslash-u, a preceding hex digit, a letter, an underscore, a quote, and digit adjacency on both sides. Each row gets its expected HIT/MISS. Guard semantics must be FAIL-CLOSED: when in doubt, match. Any false positive is paid for with an explicit, tested exclusion, never with a boundary that can hide a real token. Consider whether the guard should scan DECODED literals (chipsim/guards/decoding.py exists) rather than widen the regex. Your call, stated with its reason.
2. Check the INGEST call sites before changing the shared pattern: drugbank_snapshot.py:466 and :501 use REAL_ACCESSION_RE too. If ingest needs strict token boundaries and the guard needs fail-closed, SPLIT the pattern into two named constants rather than let one weaken the other. Report any ingest behaviour difference with counts.
3. CONTENT: apply the principal's 2026-09-17 precedent, 'replace, do not investigate'. Replace the accession-shaped tokens in the two tracked test files with sanctioned synthetic values, preserving what each test tests, WITHOUT determining whether any of them is assigned. Put content replacement and the regex fix in the same iteration, content first, so the tree never goes red with no remedy. Do NOT rewrite git history: it is private and unpushed, and 'annotate, do not rewrite' stands. I am telling the principal, who can override before anything lands.
4. The reviewer transcript under /private/tmp: do not open, copy, quote or cite it again. Leave it in place: it is ephemeral session state outside every repo. I am flagging its existence to the principal, whose decision it is if anything more is wanted.
5. CONTENT BLOCK FOR SUBAGENT PROMPTS (fleet-wide, effective now; from lung-on-chipsim #315). Every reviewer or subagent prompt in a workstream bound by the identifier/substance constraint carries it verbatim. The constraint does not propagate to subagents on its own:
  'Content constraint: do NOT look up whether any identifier is assigned or real. Do NOT associate an identifier with a name, substance or structure. Do NOT reproduce any identifier, name or association in your report. Report shape and mechanism only, using the project's sanctioned synthetic probe values. If you find a real-looking identifier, report its FILE and LINE and nothing else.'

Order: finish reporting E-21's gate findings, then draft E-22. Nothing on E-22 executes before I sign it.
