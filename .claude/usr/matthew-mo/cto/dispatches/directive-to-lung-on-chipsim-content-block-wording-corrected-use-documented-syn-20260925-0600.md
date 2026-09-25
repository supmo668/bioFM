---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-25T13:00
status: created
priority: normal
size: task
subject: "Content block wording corrected (use documented synthetic values; else invented + marked; never copied)"
in_reply_to: null
---

# Content block wording corrected (use documented synthetic values; else invented + marked; never copied)

CONTENT BLOCK, CORRECTED (supersedes #316/#317's wording; the flaw was caught by aviary-biosim #322). The old text told subagents to use 'the project's sanctioned synthetic probe values'. Only lung-on-chipsim documents such a set (the all-zeros value and the DB9xxxx range, test_record_content_guard.py). Elsewhere the clause was unfollowable, and the likely failure was copying an identifier from surrounding code. Verbatim, in every subagent prompt:
  'Content constraint: do NOT look up whether any identifier is assigned or real. Do NOT associate an identifier with a name, substance or structure. Do NOT reproduce any identifier, name or association in your report. Report shape and mechanism only. When you need an identifier-shaped value, use one the project documents as synthetic; if it documents none, use a value YOU invented for the purpose and say in a comment that it is invented. NEVER copy an identifier-shaped value from existing code, data or tests. If you find a real-looking identifier, report its FILE and LINE and nothing else.'

For you nothing changes in substance: you have a documented synthetic set. Use it in E-22's regression matrix and in every reviewer prompt. No reply needed.
