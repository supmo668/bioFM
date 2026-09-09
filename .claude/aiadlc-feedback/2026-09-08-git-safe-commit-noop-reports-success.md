# `git-safe-commit` exits 0 and logs "success" having committed nothing

**Tool:** `tools/git-safe-commit` (plugin 0.52.0), lines 306–314
**Severity:** high — receipt/authorship integrity, not convenience
**Found by:** `biofm/matthew-mo/lung-on-chipsim`; confirmed by `biofm/matthew-mo/cto`

## What happens

```bash
if [ -z "$(git status --porcelain)" ]; then
    log_warn_v "Nothing to commit, working tree clean"
    ... log_end "$RUN_ID" "success" 0 0 "Nothing to commit"; exit 0
...
if [ -z "$(git diff --cached --name-only)" ]; then
    log_warn_v "No staged changes to commit"
    ... log_end "$RUN_ID" "success" 0 0 "No staged changes"; exit 0
```

Three properties compound:

1. **Exit 0** — a caller's `set -e` cannot trip.
2. **The logged outcome is the literal string `"success"`** — telemetry agrees with the
   false belief, so an audit of the run log later also reads success.
3. **The warning is `log_warn_v`, verbose-only** — in default mode the tool prints
   **nothing at all**.

## How it bit us

Two writers shared a worktree. Writer A ran `git add -A`, sweeping writer B's working-tree
edits into A's commit. B then staged the same edits and ran `git-safe-commit`: nothing was
left to stage, so the tool exited 0 silently, B's `set -e` did not trip, B pushed, and
**B's commit never happened.**

B reported the work as committed to the coordinator. B was doing everything correctly —
checking the exit code, reading the output, trusting the tool whose entire purpose is to
make commits safe. The work existed in the tree, so it *looked* done.

```
git log --grep="band ruling folded in"   ->  empty
grep "anti-vacuity" A-and-D.md           ->  present
```

This does **not** require two writers. It fires whenever anything else stages first — a
hook, a prior tool invocation, a `--amend`, a concurrent process.

## Why it matters more than a normal no-op

An agent's report of its own work is the coordinator's primary evidence. A commit tool that
reports success having committed nothing lets an agent **truthfully believe, and honestly
report, that it committed work it did not commit.** It manufactures unreliable authorship
records out of correct agent behaviour, which is precisely what the receipt chain exists to
prevent.

It is also the same defect class the framework already rules against elsewhere: a refusal or
no-op that is indistinguishable from success by exit status. Under cron/n8n, where stderr is
discarded, even a non-verbose warning would be invisible.

## Suggested fix — deliberately NOT `exit 1`

A hard failure would break legitimate idempotent callers that commit only when there is
something to commit. Make the outcome **unmistakable** instead:

- print the "nothing to commit" notice **unconditionally**, not `log_warn_v`;
- log the outcome as **`noop`**, never `success`, so a caller can distinguish "committed"
  from "had nothing to commit" without parsing prose;
- optionally add `--require-commit` for callers that treat a no-op as an error.

## Caller-side mitigation until fixed

```bash
before=$(git rev-parse HEAD)
"$T/git-safe-commit" "msg" --no-work-item
[ "$(git rev-parse HEAD)" != "$before" ] || { echo "COMMIT DID NOT LAND"; exit 1; }
```
