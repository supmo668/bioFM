---
name: never-quote-the-redacted-thing-in-its-own-commit-message
confidence: 1.000
created: 2026-10-30T18:41:54Z
last_reinforced: 2026-10-31T00:12:16Z
ttl_days: 30
triggers: [git-safe-commit, --amend, redact, commit message, pre-publication scan]
tags: []
---

When a commit removes something from a public surface (a home path, an identifier paired with a substance), the commit message explaining the removal tends to quote the thing removed. It happened twice in one session: a literal home path in the message describing its own redaction, then a fixture identifier paired with a real substance name in a knowledge-graph rebuild message (amended before push). It then happened a THIRD time while writing this instinct, whose first draft quoted the very pairing it warns against. The diff scan passes; the message (or the lesson note) re-publishes the content. **Why:** git history is public and permanent, and a message or tracked note is as visible as the diff. **How to apply:** scan commit MESSAGES and any tracked note as well as the diff before a push, and describe the class removed rather than the instance. When amending by text replacement, assert exactly one match first, because wrapped lines silently defeat a one-line anchor.
