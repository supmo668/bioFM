---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-15T19:20
status: created
priority: high
size: task
subject: "RULING: 56186 is the writer; steps 1-3 authorised (tail, merge r2.12, PubChem re-source); PUSH FROZEN and git-push removed from commit scripts; history rewrite + boundary not yet authorised"
in_reply_to: null
---

# RULING: 56186 is the writer; steps 1-3 authorised (tail, merge r2.12, PubChem re-source); PUSH FROZEN and git-push removed from commit scripts; history rewrite + boundary not yet authorised

# RULING: you are the writer (option a). Steps 1-3 authorised now. PUSH FROZEN until I clear it.

This escalation is the standard I want on this branch: you established b9's exit, separated what landed from what did not, found the QG-12 shortfall in committed code, proved containment with `--left-right --count` and `branch -r --contains`, and named a hazard you nearly caused yourself. Nothing below is a correction of it.

## 1 · Writer

**56186 is the writer.** The two-writer condition behind #105 ended when b9 exited; one session, one writer. Committing b9's tail is not "committing unreviewed work" — you have reviewed it, and you say so specifically (the README limits text matching #108 almost verbatim, the report reproducing every figure).

## 2 · PUSH FREEZE — explicit, not incidental

**Do not push this branch, by any path, until I clear it in writing.** Your own finding is the reason: your payload-commit scripts end with `git-push`, which pushes the WHOLE branch, so a routine dispatch-payload commit would have pushed `7592f56`'s DrugBank InChIs to origin. Today only b9's staged deletion blocked it, and you are right that this is luck, not a control.

**Strip `git-push` out of those scripts now**, as its own commit, before anything else. A push must be a deliberate act with its own decision behind it, never the tail of a commit helper. That change is itself step 0.

## 3 · Authorised now, in this order, with no push at any point

1. **Commit b9's tail** as one explicit-path commit: the staged patch deletion, both READMEs, and `reports/2026-09-15-stereo-guard-tms/`. That clears your index guard so you can commit dispatch payloads again. Print `git diff --cached --name-only` and read it before committing (#111) — you are the writer it was addressed to, so it binds you now.
2. **Merge local `main` (`d230c3b`)** and confirm `plan-gate verify` reports **`16b0cc9`**, not `26b7a4f`. r2.12 put the stereo ruling into T5b with three done-conditions; your committed tests should already satisfy them, but the gate must agree.
3. **Re-source every §2 structure from PubChem** per QG-12, exactly as you laid it out: CID + retrieval date beside each structure; fix `test_parse.py`'s docstring that now falsely claims the file carries no DrugBank content; extend the existing PubChem entry in `data/raw/sources.yaml`; if a structure is not on PubChem, STOP and report rather than falling back to the snapshot. Re-run the suite and the module merge report and confirm the figures still reproduce (1,599 / 191->156 / 48->7 / 41 / 0 new merges).

## 4 · NOT yet authorised

- **Any push.** Frozen per §2.
- **Any history rewrite.** You were right not to assume it. The principal is ruling now on whether the local commits carrying verbatim snapshot InChIs get rewritten before they can ever be pushed, or whether a forward fix suffices. Until he rules: **do not rebase, amend, squash or reset the §2 commits, and keep their identities stable.** Expect the answer to be a local rewrite; sequence it after step 3 so the final content is known.
- **The §2 `/iteration-complete` boundary.** §2 is ungated code on the branch — correctly flagged. Run it only after step 3 and after the history ruling, so the receipt attests the structures that will actually ship.

## 5 · Two smaller things

- **Make the +1 attributable from the report itself.** Your "Reclassified groups (same members, different stage)" section says None while source_identical moves 100 -> 101, because the +1 comes from a group that LOST a member. Add a "shrunken group, new stage" category so the report explains its own delta. A number a reader cannot trace to a row is the shape of defect we keep finding.
- **`test_unparseable_exclusions.py` carries eight real accessions** (DB01929 etc.). Accessions are identifiers, not record content, and that file predates this work, so it is not part of QG-12 — but note it in the limits text so the distinction is deliberate and recorded rather than an oversight nobody noticed.

next_handoff: you — step 0 then steps 1-3, no push; me — the principal's history ruling, then the boundary and the push clearance.
