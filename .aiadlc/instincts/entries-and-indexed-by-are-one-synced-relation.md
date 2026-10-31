---
name: entries-and-indexed-by-are-one-synced-relation
confidence: 0.700
created: 2026-10-31T00:17:51Z
last_reinforced: 2026-10-31T00:17:51Z
ttl_days: 30
triggers: [Entries, Indexed by, HACP Index, notion-update-page, index membership, hacp]
tags: []
---

In the HACP Index, "Entries" and "Indexed by" are not two properties. They are the two sides of ONE synced Notion relation. Proof measured 2026-10-31: setting ONLY "Indexed by" on a newly created row made it appear in the parent index row's "Entries" without that row being touched.

**Why:** it makes an Entries edit a write to OTHER rows. The human review view filters on "Indexed by" plus Status != Superseded, so dropping a live page from an index's Entries clears that page's "Indexed by" and removes it from human review, with no edit to the page itself and nothing in its own history to show it. The writer contract's "confirm no unintended duplicate ownership" check will not catch it, because nothing was duplicated: something was silently unindexed.

**How to apply:** never set Entries as a whole list. Resolve every member first and confirm each one is a live row you intend to keep. If the goal is to add a page, set that page's "Indexed by" instead and let the relation populate Entries. Only remove an Entries member you have proven is a deleted page, and say so in writing. After any Entries write, re-query the view's own filter, not the relation, to confirm what a human can still see.
