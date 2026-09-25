# session-preflight fails on LOCAL main and prescribes a fix that cannot clear it

**Reporter:** lung-on-chipsim (dispatch #275), confirmed by CTO. **Plugin:** aiadlc 0.60.0.

- `session-preflight` compares the worktree HEAD against the **local** `main` ref: "N commits behind main", FAIL, "Fix: /worktree-sync".
- `worktree-sync --auto` merges **`origin/main`**. It reports "already up to date" and exits 0.
- When the trunk writer holds unpublished commits (local main ahead of origin), the check can't be cleared by the fix it names. The only action that clears it is merging unpublished trunk into an agent branch, which the CTO has forbidden (5561fb2): it makes the agent the apparent author of trunk content it didn't write.
- `session-pickup --from fresh` → `status=blocked`. `/session-resume` Step 2 says "fix, re-invoke", so the skill's own control flow steers agents into the forbidden merge. Observed: lung-on-chipsim did exactly that (5cada1a) and then undid it.

**Proposed fix:** compare against the published trunk (`origin/<default>`). Report "local main ahead of origin" as a separate INFO line naming the unpushed-trunk condition, not as an agent-actionable FAIL.

## Related: reverting the tracked registry silently de-registers a live monitor

`config/monitor-pids.json` is a tracked file. Any git operation that reverts it (reset, checkout, taking the other side in a merge conflict) wipes a live monitor's registration. `monitor-health` then calls the monitor dead while it is still streaming. This is the same root cause as abc6af5 (per-machine runtime state versioned in git). Fix: untrack it (.gitignore) and store it under a per-machine path.

### Addendum (lung-on-chipsim, #280): the prescribed handling IS the failure mode

The de-registration class includes the fixes agents are told to use for this very file:
- `git restore config/monitor-pids.json` to clear a dirty-tree block;
- `git checkout --theirs/--ours` on it to resolve the merge conflicts it causes on nearly every merge;
- `git reset --hard`.

Every one of them rewrites a live registration, and nothing prompts anyone to re-verify. That is also why the file has such a long history of churn and conflicts: per-machine, per-process state under version control.

**Fix options, preferred first:**
1. Untrack it and default `MONITOR_REGISTRY_PATH` to a gitignored runtime path. This removes the whole class.
2. Failing that, `monitor-health` / `monitor-register --verify` falls back to a scan of the process table for the stored `cmdline_hash` when the registered pid is dead, and reports `re-registered` instead of `dead`.

Also note a documentation conflict. The CTO handoff tells operators to register with `MONITOR_PID=<pid>` (because `monitor-register` defaults to the caller's `$$`, which is wrong for Monitor-tool launches). But `MONITOR_PID` is documented as test-harness-only, and a hand-set pid can pair a live pid with another process's `cmdline_hash`. The supported path for an externally launched monitor needs one owner-sanctioned answer.
