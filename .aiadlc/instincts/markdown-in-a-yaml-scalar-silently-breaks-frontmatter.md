---
name: markdown-in-a-yaml-scalar-silently-breaks-frontmatter
confidence: 0.700
created: 2026-11-02T12:09:33Z
last_reinforced: 2026-11-02T12:09:33Z
ttl_days: 30
triggers: [handoff.md, cto-handoff, frontmatter, next-action, yaml.safe_load, handoff write]
tags: []
---

A markdown value written straight into a YAML frontmatter key breaks the WHOLE document's frontmatter, and nothing warns you. A leading '**' makes YAML scan an alias ('*'), so safe_load raises and every field — type, agent, date — becomes unreadable, not just the offending one. Writing a long bold-led summary into 'next-action:' did exactly this and survived a full session undetected because the file still LOOKED right to a reader and to grep. **Why:** the handoff contract is machine-read (type: session, agent: <addr>); a human eyeballing the file cannot see a parse failure, and heading-order greps pass happily while the frontmatter is dead. Markdown's '**', '*', '#', ':' and '[' are all YAML-significant. **How to apply:** put any multi-line or markdown value in a block scalar ('key: |-' with the body indented two spaces), never bare after the colon. Then PROVE it with yaml.safe_load and print the keys back — a heading-order check is not a frontmatter check. When a grep for '^## ' returns a hit inside the frontmatter region, that is the tell: a wrapped scalar is impersonating a heading.
