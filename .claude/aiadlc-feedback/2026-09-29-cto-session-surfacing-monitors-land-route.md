---
type: plugin-feedback
target: airdlc plugin (airdlc-plugins/airdlc 0.71.0 tools, 0.73.0 skills) + Claude Code harness
plugin_version: 0.71.0 / 0.73.0
reporter: biofm/matthew-mo/cto
date: 2026-09-29
scope: plugin / operating-system behavior — NOT repo/app work
---

# CTO session 2026-09-28/29 — surfacing to Notion/Slack, monitor lifecycle, submodule land, approval-log route

Principal ruling that motivates entries 1–3 (2026-09-29): **"keep HACP to Notion, and Slack message to communicate the Notion URL."** The Artifact fallback silently became the norm in this session; the framework should make Notion the surface and Slack the notifier, and fail loudly when either is not connected.

## 🔴 1. HACP surfacing degrades to a web Artifact silently when the Notion connector is down — and nothing reconnects it
**File:** `reference/REFERENCE-SURFACES.md` §3 (surfacing table); `skills/walkthrough-change/SKILL.md` Step 5; `tools/docs-plan` (`root` reports a ROOT even when no Notion tool is reachable)
**Symptom:** `docs-plan root` reports `ROOT 3e5749bd… (user)`, but every Notion MCP in the CTO session was "not connected" / auth-stub only (claude.ai Notion: `MCP server not connected`; `plugin:airdlc:notion-aiadlc`: `authenticate` stub). The rule says "Artifact, and say not published to the HACP index" — so two walkthroughs (aviary-biosim completion, lung-on-chipsim product cut) and four HACP row updates (lung §decision/§risk/§build/§eval) were surfaced as Artifacts and local files, with rows "owed". The principal explicitly wants Notion as the surface.
**Root cause:** the surfacing table treats a disconnected connector as a working state with a fallback; no step says *reconnect first, then write*. `docs-plan root` does not check reachability, so a session can believe it has a root while it cannot write to it. The fallback is silent at the fleet level (only a sentence in the artifact).
**Fix:** (a) `docs-plan root` gains `--check` that probes the Notion MCP (`notion-fetch` on the root id) and returns `ROOT_UNREACHABLE` (exit 4) when the tool is absent/unauthenticated; (b) `/session-resume` Step 3 for the CTO: if `docs.provider=notion` and `ROOT_UNREACHABLE`, print the connector's authenticate URL (the `mcp__…__authenticate` stub returns one) and **block the turn with a principal prompt** the same way `monitor-health` does — Notion connected is a CTO startup invariant like the dispatch monitor; (c) the Artifact fallback stays, but every fallback publish appends a row to a `docs/hacp/_owed.md` ledger that the next CTO startup drains (write the Notion row, read it back, replace the Artifact link).
**Effect:** the HACP index (Notion) is the surface again; an Artifact becomes a temporary mirror with a tracked debt, not a silent substitute.
**Status:** open

## 🔴 2. Slack notification path is not wired for Notion URLs, and both Slack connectors failed
**File:** `tools/notify` (human-qa only; body = `{channel,text}`), `agency.yaml notifications.slack.*`, `skills/walkthrough-change` (no Slack step)
**Symptom:** the principal asked for the walkthrough "sent to slack" with the Notion URL. `notifications.slack.enabled=false`, no channel, no webhook; the claude.ai Slack connector returned `{"type":"error","error":{"type":"not_found_error","message":"Server not found"}}` on OAuth; `plugin:engineering:slack` produced an OAuth URL the principal still has to complete. `tools/notify` only knows the `human-qa` event and cannot carry a Notion link as a first-class field. The only Slack channel the project names is `paper/publish.yml notify.slack_channel: "#research-approvals"` — not read by any tool.
**Root cause:** notify is a single-event tool; the surfacing chain (local → Notion row → Slack) is not a pipeline anywhere in the skills.
**Fix:** (a) `tools/notify surface --kind <Brief|Presentation|Index> --notion-url <url> --title <t> [--summary-file <path>]` that posts `<title> — <one-line summary> — <Notion URL>` to `notifications.slack.channel` (webhook if set, else prints the payload for the Slack MCP); (b) `docs-plan plan --boundary phase` emits a `NOTIFY slack <channel> <Notion URL>` line after `PROPAGATE notion`, so the CTO's phase close does Notion-then-Slack in one pass; (c) `notifications.slack.channel` seeded from `publish.yml notify.slack_channel` at `/cto-init` when empty; (d) `/session-resume` (CTO) checks the Slack connector the same way as Notion in entry 1.
**Effect:** every surfaced HACP row announces itself once, in Slack, by its Notion URL — the principal's stated protocol.
**Status:** open

## 🟠 3. The Monitor tool caps at 30 minutes; three CTO monitors must be re-armed by hand every 30 min, and `monitor-health` blocks the turn when one lapses
**File:** `skills/monitor-dispatches/SKILL.md` ("Start monitoring" — assumes a persistent watch), `skills/session-resume/SKILL.md` Step 3, `hooks/monitor-health.sh`, `tools/monitor-register` (pid semantics)
**Symptom:** each Monitor call expires at `timeout_ms` max 1,800,000 ms; in a 9-hour CTO session the dispatch/issue/blocker monitors expired ~18 times each; every expiry produced a notification, a re-arm turn, and a `monitor-register` call with `MONITOR_PID=<real pid>` (because `monitor-register` without it registers the calling shell's pid — filed earlier at `3dd5cd5`). Once, the dispatch monitor lapsed between turns and the `monitor-health` Stop hook blocked with "your dispatch monitor is not running".
**Root cause:** the skill's mental model is "start once"; the harness's Monitor is a ≤30-min watch. Nothing in the plugin re-arms.
**Fix:** (a) document the cap in `/monitor-dispatches` and prescribe the re-arm loop: on the expiry notice, re-arm immediately and re-register issue/blocker with `MONITOR_PID` (dispatch self-registers); (b) better: `tools/dispatch-monitor --supervise` that runs the three monitors under one process and emits a single line on the Monitor stream, so ONE Monitor call covers all three and one re-arm per 30 min suffices; (c) `monitor-health` should tolerate a monitor that died < 60 s ago when a re-arm is in flight (grace), instead of blocking the turn; (d) `monitor-register` defaults `MONITOR_PID` to the newest process matching the tool's cmdline, not `$$`.
**Effect:** CTO sessions spend turns on coordination instead of monitor hygiene; the Stop hook stops firing on the harness's own 30-min cap.
**Status:** open

## 🟠 4. `dispatch-monitor` / `dispatch catchup` "VARIANT of your identity" warning counts the coordinator's own OUTBOUND mail
**File:** `tools/dispatch-monitor.py` (reconcile), `tools/dispatch` catchup
**Symptom:** every 900 s reconcile printed `⚠ … 6 unread match a VARIANT of your identity — do NOT treat this as clear` for six dispatches **from** `biofm/matthew-mo/cto` **to** `aiadlc/mo/cto` (the plugin maintainer). Verified with `dispatch list --all`. The CTO had to add `grep -v 'VARIANT of your identity'` to the Monitor command, which also hides a genuine variant.
**Root cause:** the variant query matches `to LIKE '%cto%'` (or the namespace form) without excluding `from == self`.
**Fix:** in the variant query, add `AND from_addr != <self>`; print the matched ids in the warning so a reader can dismiss or act in one look.
**Effect:** the warning means something again; the `grep -v` goes away.
**Status:** open (also raised in the 2026-09-27 stand-down handoff)

## 🟠 5. `blocker-sweep` escalation branch has no status guard → permanently red (36 resolved escalations listed every cycle)
**File:** `tools/blocker-sweep` (filter `type=="escalation" || status=="unread"`)
**Symptom:** `ESCALATE principal #4 … #192` for 36 already-resolved escalations, every 15 min; `REMAINING: 71 blocker(s)`. The CTO runs the sweep through an awk status filter (`$4 !~ /\/(resolved|closed)$/`).
**Fix:** `(type=="escalation" && status not in (resolved, closed)) || status=="unread"`.
**Status:** open (filed at `6ad07ad`; still present in 0.71.0)

## 🟠 6. `receipt-verify --file <parent receipt>` reports BLOCKED when the tip carries a derived receipt; the workstream-mode call verifies it — the two disagree and the skill names only `--file`
**File:** `tools/receipt-verify`; `skills/pr-cto-land/SKILL.md` Step 3 ("verify it via `receipt-verify --file <receipt>`")
**Symptom:** perturb-seq-eval A4CLIENT: `--file …-36b0e1d.md` → `BLOCKED: Receipt Hash E does not match current code. Current: 47e2523`; `--workstream perturb-seq-eval --project perturb-seq-eval` → `✓ Receipt verified: …-47e2523.md (derived from parent gate 36b0e1d)`. A CTO following the skill literally would reject a valid hand-off. (The 2026-09-28 handoff records the mirror error: a CTO wrote "verified" for a derived receipt before reading the output.)
**Fix:** `--file` on a parent receipt should say "a DERIVED receipt <path> (Hash E <h>) exists for the current tip — verifying that" and verify it (or point to it); the pr-cto-land skill Step 3 should name the workstream-mode call.
**Status:** open

## 🟠 7. Submodule land with `--no-release`: `pr-create` refuses (requires a version bump), `git-cto sync-main` refuses inside the submodule (local `main` diverged), `bump-gitlink` reads the submodule HEAD
**File:** `tools/pr-create` (guarantee 3), `tools/git-cto sync-main`, `tools/git-cto bump-gitlink`, `skills/pr-cto-land` "Submodule monorepo" section
**Symptom:** landing aviary-biosim (submodule `projects/aviary-biosim`, principal-directed no version bump, no release): `pr-create` cannot be used (it requires `framework.version` bumped vs default and reads the parent's agency.yaml; the submodule repo has none) → the CTO used `gh pr create` directly. After `pr-merge`, `git-cto sync-main` inside the submodule failed with "main has diverged from origin/main" because the submodule checkout's local `main` was a stale branch (`291a147`, 1 ahead / 26 behind) — the same stale-local-main that produced the #308 false preflight. `bump-gitlink <app>` read the submodule HEAD (still old) and said "nothing to bump" until `--sha <merge commit>` was passed.
**Fix:** (a) `pr-create --no-bump` (or honour `--no-release`) for principal-directed lands, and `--repo <owner/name>` for submodule repos; (b) `git-cto sync-main --module-dir <p>` that fetches and checks out `origin/<trunk>` detached in a submodule (the correct state for a gitlink) instead of fast-forwarding a local branch; (c) `bump-gitlink` should default `--sha` to the submodule's `origin/<trunk>` after a fetch, not the checkout's HEAD; (d) the skill's submodule section should give the exact sequence.
**Effect:** a submodule land is one path, not four workarounds.
**Status:** open

## 🟠 8. The plan-approval log's ROUTE column is prose with no check — a row claimed a direct principal answer that was actually a standing ruling applied
**File:** `tools/plan-gate` (writes/verifies the plan hash; does not touch the log), the approval-log convention (per-workstream markdown), `skills/grill-me` (records principal choices)
**Symptom:** lung-on-chipsim #492: row 55 read "principal (AskUserQuestion, CTO session)"; the principal, asked directly, confirmed the authority was the 11:30 time-box ruling (row 54) applied by the CTO at 16:06. Plans bind to hashes, boundaries to receipts, counts to harnesses — the route (the field asserting *a human decided this*) binds to nothing. For a workstream whose paper's novel contribution IS this log, that is the recurring defect family in the provenance layer.
**Fix (adopted as a convention in bioFM 2026-09-29; proposing it for the framework):** a route claiming a direct principal decision carries a verbatim quote of the principal's words or a resolvable session reference, else `standing ruling applied (row N)` or `inferred`. Mechanically: `AskUserQuestion` results and `/grill-me` decisions should be written by a tool (`tools/approval-log append --route principal --quote "<verbatim>" --session <id>`) that refuses `--route principal` without `--quote`/`--session`; `plan-gate verify` lints the log for route rows without evidence.
**Effect:** the route distribution becomes a reportable datum with a check behind it.
**Status:** open

## 🟢 9. Things that worked and should stay
- `dispatch catchup`, `dispatch fetch` (read-only peek with the "not marked read — addressed to X" guard), `dispatch resolve`, the `--body-file` discipline.
- `receipt-verify` workstream mode with the "derived from parent" line.
- `git-cto verify-pushed --module-dir`, `pr-merge --principal-approved` (true merge), `post-land --into main` (read-only audit).
- `handoff write --lightweight` as a cheap boundary marker; `handoff write --trigger …` archive + signal.
- The Skill tool now accepts `/airdlc:pr-cto-land` when the principal types it (the 0.64.0 refusal is gone).
