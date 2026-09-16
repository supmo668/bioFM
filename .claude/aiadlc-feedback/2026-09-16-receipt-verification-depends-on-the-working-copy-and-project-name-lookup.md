# Receipt verification gives a verdict that depends on the *working copy*, and the boundary gate misses receipts signed with a non-default `--project` — reporting the wrong cause

**Tools:** `tools/diff-hash`, `tools/receipt-verify`, `tools/receipt-sign`, `tools/git-safe-commit
--boundary` (plugin 0.56.0)
**Severity:** high for (a) — the safe direction is loud, the unsafe direction is silent
**Observed:** 2026-09-16, §2 iteration boundary (receipt `061f12d`, boundary commit `0c4e181`),
independently by the worktree agent and by the CTO

## (a) The verdict depends on where you stand, not only on the commit

`diff-hash` runs `git diff BASE...HEAD -- .`, and the pathspec `.` is **relative to cwd**. So the
same receipt, the same commit and the same flags produce different answers:

| where it ran | result |
|---|---|
| worktree root (correct) | `✓ Receipt verified … 1 of 14` |
| `projects/lung-on-chipsim/` (subdirectory) | `BLOCKED: … none match current code` |
| the **main checkout** (a different working tree, different branch) | `BLOCKED: Found 12 receipt(s) but none match current code` |

The third row is the CTO's, hit while verifying an agent's boundary — the receipt binds the branch,
which lives in the worktree, but the natural place for a coordinator to stand is the main checkout.
Neither message mentions the working tree or HEAD it actually hashed, so the operator's conclusion is
"the agent's gate is stale" when the truth is "you are standing in the wrong tree".

**The dangerous direction is signing, not verifying.** A false BLOCK is loud and self-correcting. But
a receipt **signed** from a subdirectory binds only that subtree — after which changes outside it
verify clean forever. The gate would be attesting a fraction of the diff while reporting success.

**It recurs under ordinary concurrency.** The agent hit it again minutes later: two parallel shell
calls shared a working directory, so one `receipt-verify` silently ran from the project subdirectory
and reported BLOCKED while the root run verified. Nothing in the output distinguishes the two.

**Suggested fix:** `diff-hash` should resolve `git rev-parse --show-toplevel` and diff from there;
`receipt-verify` and `receipt-sign` should print the working tree and HEAD they hashed, so a
tree-vs-tree mismatch is visible rather than inferred.

## (b) `receipt-sign` accepts any `--project`; the boundary gate looks up by `project.name`

`receipt-sign --project lung-on-chipsim` produced a **valid** receipt — `receipt-verify --file`
confirmed it, Hash E matched. But `git-safe-commit --boundary iteration` calls verification with
`--project` = config `project.name` (`bioFM`), matches receipts **by filename**, found none, and
blocked with:

```
Code changed after the gate ran. Re-run the gate (/pr-prep).
```

That diagnosis is wrong. The code had not changed; the lookup missed. Re-signing with
`--project bioFM` — identical hashes — passed immediately.

**Why it matters:** the obvious response to that message is to re-run a full quality gate, which
costs a cycle and fixes nothing, because the receipt was never the problem.

**Suggested fix:** `receipt-sign` should default `--project` to `project.name` and warn or refuse on
a mismatch; verification should distinguish **"no receipt found for project X"** from **"receipt
found, hash mismatch"**. They are different failures with different remedies.

## (c) `git-safe-commit`: one `--finding` per commit, and `git add -A` by default

1. `--finding` keeps only the last value, so a file carrying fixes for two findings forces
   intermediate file states to keep commits atomic — done three times in one gate.
2. Without `--staged`, `git-safe-commit` runs `git add -A`. In this gate that would have committed
   `config/monitor-pids.json`, a file the agent is barred from touching and which was dirty in its
   worktree because a *monitor* rewrote it.

**Suggested fix:** accept repeated `--finding` (one trailer each); default to staged-only, or refuse
`add -A` when the tree has changes outside the agent's workstream paths.

## Cross-reference

This pairs with `2026-09-16-monitors-inherit-identity-from-cwd-…`: both are cases of a tool deriving
a security- or correctness-relevant identity from ambient shell state (`cwd`) rather than from the
thing it is describing. In one the answer was which agent owns a monitor; here it is which tree a
receipt attests.
