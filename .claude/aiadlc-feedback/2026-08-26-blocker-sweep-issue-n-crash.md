---
type: plugin-feedback
target: aiadlc plugin (aiadlc-plugins/aiadlc)
plugin_version: 0.48.0
reporter: biofm/matthew-mo/lung-on-chipsim
date: 2026-08-26
scope: plugin / operating-system behavior — NOT repo/app work
---

## 🟠 1. `tools/blocker-sweep` crashes when there are zero open issues (`ISSUE_N` becomes `"0\n0"`)

**File:** `tools/blocker-sweep` line 160 (symptoms at lines 203, 217, 223)

**Symptom:** Running the /session-resume stale-unread safety net
(`blocker-sweep | grep -E 'PARKED|WAKE'`) as a worktree agent crashes:

```
line 203: 0
0: syntax error in expression (error token is "0")
line 217: [: 0
0: integer expression expected
line 223: _total: unbound variable
```

The safety net is unusable — the PARKED/WAKE report never prints.

**Root cause (proven):** Line 160:

```sh
ISSUE_N="$(printf '%s' "$ISSUES" | grep -c . 2>/dev/null || echo 0)"
```

`grep -c .` prints `0` to stdout **and** exits non-zero when there are no
matches. The `|| echo 0` then appends a *second* `0`, so `ISSUE_N` holds the
two-line string `0\n0`. That poisons:
- line 203 `_total=$((N + ISSUE_N + STALE_N))` → arithmetic syntax error;
  under `set -u` the failed assignment leaves `_total` unbound (line 223 error)
- line 217 `[ "$ISSUE_N" -gt 0 ]` → "integer expression expected"

The sibling counter `STALE_N` (lines 176–177) already uses the correct
pattern — `|| true` plus a numeric-sanitizing `case` guard — which is why only
`ISSUE_N` breaks.

**Fix:** Make line 160 match the STALE_N pattern:

```sh
ISSUE_N="$(printf '%s' "$ISSUES" | grep -c . 2>/dev/null || true)"
case "$ISSUE_N" in ''|*[!0-9]*) ISSUE_N=0 ;; esac
```

**Effect:** `blocker-sweep` runs cleanly in the zero-open-issues case (the
common case for a fresh worktree agent), restoring the identity-filter-immune
stale-unread safety net that /session-resume Step 3 depends on.

**Status:** open
