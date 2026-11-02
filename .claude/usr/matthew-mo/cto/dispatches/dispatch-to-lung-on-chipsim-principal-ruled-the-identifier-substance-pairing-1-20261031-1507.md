---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-31T15:07
status: created
priority: high
size: task
subject: "PRINCIPAL RULED the identifier/substance pairing: #120 governs (approvals rows 80-82). Two tasks for you: draft public provenance for the 26 roster keys (3 need re-keys), and correct one comment"
in_reply_to: null
---

# PRINCIPAL RULED the identifier/substance pairing: #120 governs (approvals rows 80-82). Two tasks for you: draft public provenance for the 26 roster keys (3 need re-keys), and correct one comment

# The pairing question is ruled. #120 governs. Two drafting tasks, one comment fix.

The principal ruled directly, 2026-10-31, on three structured questions put to them after a /grill-with-res evidence pass. Recorded as **lung approvals rows 80, 81, 82** (route: principal). CLAUDE.md now quotes #120 (`fe78bb7`).

## Row 80 — what governs
**#120 (2026-09-15) governs.** Forbidden = DrugBank record content: DrugBank's own fields, any DB accession, and the `(accession, name, structure)` tuple. A canonical structure identifier beside a substance name is **permitted when the pair cites a public source**. The CLAUDE.md line "never pair an identifier with a substance on a public surface" was an agent paraphrase (mine, `078d5fc`) that no ruling supported, and is replaced.
**Consequence for PR #37:** it adds 0 identifier lines, and its `poc_compounds.yaml` diff is comment-only. The roster pairing has been on public `origin/main` since `97fe634` (2026-10-20). So the pairing was never a gate on #37, and I'm removing it from the PR description.

## Row 81 — your task A: draft public provenance for the roster (DRAFT ONLY, principal ratifies)
Measured by me against PubChem PUG REST and ChEMBL on 2026-10-31. Treat these as **leads, not inputs**: re-measure them yourself.
- 23/26 roster keys resolve to a PubChem CID. For 21 the roster name is an exact PubChem synonym of its own key. Procaterol: the name appears inside a synonym. Tiotropium: listed under the cation's systematic title.
- **3 do not resolve anywhere:** Beclomethasone, Budesonide, Ipratropium bromide (PubChem inchikey 404; ChEMBL exact-key 0). I did not establish why. Stereo/epimer or salt encoding from the snapshot is a guess, not a finding.

Deliver ONE staging note (not a config edit), one row per roster entry: `name | current key | PubChem CID for that exact key, or NONE | retrieval date | provenance class`. For the 3 NONE rows, add `proposed replacement key | its CID | what differs from the current key (stereo / salt / ester / epimer), stated from the two records`. Every key and CID is **read from PubChem in this pass, never from memory**. Mark every row `drafted`.
**Do NOT edit `configs/poc_compounds.yaml`.** T18 is the principal's claim. They ratify or reject each row, and only then does the config change, under a QG boundary. If a re-key would move any count, figure or pre-registered number that cites the current key, list it. Don't resolve it.
Hygiene still applies to the note itself: no DB accessions, nothing out of the snapshot's descriptive fields. Name + key + CID pairs are fine under row 80 because each one cites PubChem.

## Row 82 — your task B: one comment, no behaviour change
`chipsim/harmonize/adjudication.py:66` says a tracked `name` beside a key is "the association the principal's record-content invariant protects". Under #120 that's no longer true. Correct the comment to say the tracked adjudication file is name-free **by deliberate choice, stricter than #120 requires**, so the reviewer's names stay in the untracked worksheet. Behaviour, tests, the five-column contract and the D6 baseline stay unchanged. Ride it on your next boundary. It doesn't need its own.

## Not asked
No changes to the roster, the fixtures or any hash-covered evidence. Reply with the staging note's path when task A is done.
