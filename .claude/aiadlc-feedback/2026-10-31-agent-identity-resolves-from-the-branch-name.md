---
type: plugin-feedback
target: airdlc plugin
plugin_version: 0.87.0
reporter: biofm/matthew-mo/cto
date: 2026-10-31
scope: plugin / operating-system behavior — NOT repo/app work
---

## 🟠 1. Agent identity resolves from the branch name, so a commit on a staging branch is attributed to an agent that does not exist
**File:** agent identity resolution used by `git-safe-commit` (commit subject prefix + `Co-Authored-By` trailer)
**Symptom:** The lung-on-chipsim agent committed `d6e7763` on `lung-on-chipsim-staging` from a scratch worktree. The commit is attributed to `lung-on-chipsim-staging/lung-on-chipsim-staging for matthew-mo`, with a `Co-Authored-By: lung-on-chipsim-staging` trailer. No such agent exists. The principal ruled on 2026-10-31 (lung approvals rows 84, 87; CLAUDE.md) that every agent keeps unratified findings on a dedicated `<agent>-staging` branch, so this now happens on every staging commit by design.
**Root cause:** Identity is derived from the current branch name, not from the agent registry. A branch that is not the agent's working branch produces a name that matches no agent.
**Fix:** Resolve identity from the agent registry (`agency.yaml` agents + worktree ownership) and treat the branch as data. Failing that, strip a known suffix (`-staging`) and refuse to commit when the resolved name matches no registered agent, rather than inventing one.
**Effect:** Durable commit records stop naming non-existent authors, and staging branches become safe to use as ruled.
**Status:** open (filed against airdlc 0.87.0)
