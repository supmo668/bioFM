---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-09-26T16:49
status: created
priority: normal
size: task
subject: "HACP: principal-directed Notion rows for bioFM (L0 + perturb-seq-eval P0-P5 decision page); request docs.provider: notion"
in_reply_to: null
---

# HACP: principal-directed Notion rows for bioFM (L0 + perturb-seq-eval P0-P5 decision page); request docs.provider: notion

section: decision
Agent: perturb-seq-eval
FOR YOUR RECORD, and one config request. Principal-directed, answered directly (AskUserQuestion, 2026-09-26) — not a relayed authorisation asking you to act.

1. HACP WRITES DONE BY THIS WORKTREE AGENT (principal's explicit exception to the CTO-only Notion writer rule), under the AI-RDLC root's HACP Index:
   - Added select option Project = 'bioFM' (existing options untouched).
   - Kind=Index    "bioFM — Index" (Repo https://github.com/supmo668/bioFM, Local path docs/hacp/index.md) → https://app.notion.com/p/3e7749bd250d8140a751d01f6a820b7d
   - Kind=Decision "perturb-seq-eval — P0-P5 rulings for pre-registration amendment 2" (Section decision, Local path docs/hacp/perturb-seq-eval-decision-p0p5.md) → https://app.notion.com/p/3e7749bd250d8127b2b0c293fb8c0522
   Find-before-create was run (no bioFM rows existed). Floor copies committed on the branch. Content is a Wiki rendering of Source: qgr/principal-decisions-p0p5.md (fc33ebe) + prereg-amendment-2-DRAFT.md (6e896b9) — the 6 open rulings (Hash D / D1, 2c NEW-1, 2d C13, 2e C25, 2f C6, 2g C20) as option tables with recommendation + what each forecloses; the 4 ruled (C1, C3, C2+C8, C7) as context. The L0 is scoped to perturb-seq-eval only and says so — extending it to the other bioFM workstreams is yours. Repo links are local paths because the branch is not on GitHub (trunk push pending).
   Going forward these rows are yours as single writer; I will not write Notion again without a fresh principal instruction.

2. CONFIG REQUEST (principal chose to route it through you): switch this repo to HACP-on-Notion in agency.yaml — docs.provider: notion (currently 'none', so tools/docs-plan reports PROVIDER none), and pin docs.notion.project: bioFM so every writer uses the namespace above.
next_handoff: cto ack + agency.yaml docs.provider change
