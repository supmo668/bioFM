---
name: verify-the-subject-not-just-the-source
confidence: 1.000
created: 2026-10-31T02:49:16Z
last_reinforced: 2026-10-31T04:13:52Z
ttl_days: 30
triggers: [abstract, artifact, citation, attributed, referent, per-row, line number, cites, source]
tags: []
---

A correct reading of a real source, attributed to the wrong subject, is indistinguishable from a finding. Three instances in one window:

1. An agent read Lee 2022, correctly, and concluded it occupied a section of ours. It did not; the reading was right and the subject was wrong.
2. An agent reported a paper "names multi-agent debate as orthogonal". The sentence says orthogonal to "these training-based and architectural improvements" and the text never fixes what "these" means. The quote was real; the referent was inferred.
3. I read an artifact, found its table intact, and declared a claim about a DIFFERENT artifact false - then issued a STOP on a ratification. Both artifacts carried "per-row tiers", which is what let me conflate them. The paper cited a dead venue ledger at a specific line; what I read was a live roster table cited from a config.

**Why:** the usual check is "is the source real and did I read it correctly", and all three passed that. The missing check is "is this source the one the claim is about". Shared vocabulary between two sources - per-row tiers, the same author surname, an adjacent sentence - is what makes the substitution invisible. Instance 3 did active harm: a wrong STOP blocks a correct action, so a false negative here is not merely noise.

**How to apply:** resolve the subject by its OWN identifier before judging the claim - the line number, the file path, the exact id - not by topic match. When a claim says "the file at line N cites X", open line N. When two sources share a vocabulary, say which one you opened. And when a claim and a source seem to match on theme, that resemblance is the warning, not the confirmation.
