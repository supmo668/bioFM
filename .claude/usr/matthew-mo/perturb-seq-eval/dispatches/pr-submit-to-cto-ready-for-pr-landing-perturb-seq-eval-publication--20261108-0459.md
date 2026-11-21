---
type: pr-submit
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-11-08T04:59
status: created
priority: high
size: task
subject: "Ready for PR landing: perturb-seq-eval — publication prep (Morandi qualified, disclaimer narrowed, deposit 0.6.1, Scholar runbook); rows 28-31 to record"
in_reply_to: null
---

# Ready for PR landing: perturb-seq-eval — publication prep (Morandi qualified, disclaimer narrowed, deposit 0.6.1, Scholar runbook); rows 28-31 to record

Publication prep. The principal's instruction (2026-11-08, session 74ae8896): "unblock this with best judgement , until publication step is ready (include google scholar) as well".

branch: perturb-seq-eval
sha: aeaae2fa (pushed; origin == HEAD)
diff_hash: 31f07eb (vs origin/main 1f3344ac, merged in)
receipt: workstreams/perturb-seq-eval/qgr/bioFM-matthew-mo-perturb-seq-eval-perturb-seq-eval-perturb-seq-eval-qgr-pr-prep-20261108-0458-31f07eb.md (verifies --require-pushed)
draft: false
migrations_pending: none

## Principal rulings to record (approvals rows 28-31)
All were answered through AskUserQuestion in session 74ae8896 on 2026-11-08. Verify them in the transcript as you did for #913: ~/.claude/projects/-Users-mo-github-personal-bioFM-worktrees-perturb-seq-eval/74ae8896-0ac6-400e-9699-d4a8c3fbf0bb.jsonl
- Row 28 — Morandi §4.6: "Insert qualified (Recommended)". This ratifies sub-item 4.6-K and lifts row 24's hold.
  - Basis: two independent verbatim reads of arXiv:2605.19193v1, one by the aviary-biosim session on 2026-11-07 and a fresh one on 2026-11-08.
  - Both find §III and §VII-C17 verified. §VII-C14 reads "The real-LLM evaluation fixes K=3", and a sweep over K is future work.
- Row 29 — archive: "New version 0.6.0-a5 (Recommended)". The version string was then RE-RULED to "0.6.1 (Recommended)".
  - Reason: the tag v0.6.0-a5 does not contain the Morandi sentence, PREREGISTRATION says the tag "marks an amendment, not a release", and SemVer sorts 0.6.0-a5 below 0.6.0.
  - So deposit 0.6.1 is a manuscript revision of v0.6.0, made before the preprint so that Part 4's isIdenticalTo is true.
- Row 30 — (b″) disclaimer: "Narrow it (Recommended)". The text becomes: "we have read the sections cited below and have not reproduced or re-derived their methods; beyond the design differences stated below, we make no claim about how our signal relates to theirs".
- Row 31 — TechRxiv: "Open tabs for me". I opened techrxiv.org/faqs and the home page in the principal's Chrome. No agent read the content. The terms read is still the principal's (row 15's condition).

## What lands
- paper.tex:
  - The Morandi sentence, with the K clause "held fixed in its real-LLM evaluation (their \S VII-C14)".
  - The narrowed (b″).
  - tectonic build: 17 pp, 0 unresolved citations.
- Deposit tooling, retargeted v0.6.0 -> 0.6.1:
  - ALLOWED_REVISIONS = zenodo 23422745 (newversion only) and figshare 32086920 (base v6).
  - 20074427 is now an ordinary superseded record.
  - New LINEAGE_STATE_FILES guard: publish.state.json and publish.state.v060.json are refused by name, by case variant and by hard link.
  - revision_of is int-typed.
  - publish.yml: version 0.6.1, state publish.state.v061.json, notes declare the Morandi sentence, and step 5 is spelled out.
- Runbooks:
  - SUBMISSION.md: archive-first step 4a, Part 4 rewritten for the 0.6.1 record, a TechRxiv Google Scholar checklist (Part 5), and the title item closed.
  - research/PUBLISHING_RUNBOOK.md: §6.5 and §8 updated.
- Gate: a 4-reviewer roster plus a delta review; every finding at or above the threshold is fixed. Tests: 1097 passed, 0 failed.
  - Deferred, because it predates this diff: a test that every \cite key is in references.bib.
  - Deferred: the D5 config-driven-lineage refactor.

## CTO actions
1. Verify the quotes, then record rows 28-31.
2. Land this as a normal PR. --no-bump is your call.
3. After merge, the principal's remaining steps, none of which is agent-executable:
   (a) the TechRxiv terms read;
   (b) the infisical run invocation (names only) for the 0.6.1 dry run, followed by a separate go to publish;
   (c) posting on TechRxiv with the build_deposit.py paper.pdf;
   (d) the Scholar, ORCID and OpenAlex steps in SUBMISSION Part 5.
