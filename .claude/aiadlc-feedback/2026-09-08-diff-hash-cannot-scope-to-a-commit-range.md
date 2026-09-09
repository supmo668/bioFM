# `diff-hash` cannot scope a receipt to a commit range, so no boundary can be gated retrospectively

**Tool:** `tools/diff-hash` (plugin 0.52.0), and `tools/receipt-verify` by consequence
**Severity:** medium-high — limits what a QGR receipt can truthfully claim
**Found by:** `biofm/matthew-mo/lung-on-chipsim`; verified by `biofm/matthew-mo/cto`

## The limitation

```
Usage: diff-hash [--base <ref>] [--file <path>] [--json] [--module-dir <relpath>]
diff-hash:118   git diff "$BASE"...HEAD -- . "${EXCLUDES[@]}"
```

`--base` is the only selector. The head is hardcoded to `HEAD`. There is no `--head` and no
`A..B` range.

`receipt-verify` then recomputes in whatever checkout exists at verification time. So:

> **A QGR receipt is structurally a claim about `base...HEAD-at-verification-time`, not
> about a commit range.**

## Why it matters

A coordinator cannot order a receipt scoped to specific historical commits — a normal
request when a subset of work needs review (ambiguous authorship, a reverted range, an
audit of one contributor's commits).

Two options exist today and both are wrong:

1. **Sign with `--base <old>` and describe a narrower scope.** The receipt *states* it
   covers N commits and *computes* over everything since the base, including other work and
   other writers. Stated scope ≠ computed scope — a forged receipt by mechanism, in an
   artifact that may proceed to a cryptographic seal.
2. **Compute in a detached worktree at the target commit.** Gives the right diff, but
   `receipt-verify` recomputes against the live checkout, so the receipt stops verifying the
   moment the tip moves. **Born unverifiable.**

In our case the window closed while the ruling was being issued: another session committed
on top between the coordinator ordering the gate and the agent starting it.

## Suggested fix

- Add `diff-hash --head <ref>` (or an explicit `A..B` range).
- **Record the head/range in the receipt**, so `receipt-verify` recomputes over the same
  range rather than the live worktree.

Without the second half the first is not enough: the receipt would still be re-verified
against a moving target.

## Workaround until then

State the honest widened scope in the receipt body: the actual `base...HEAD` range, every
commit inside it, and any commits authored by other writers. A receipt that admits
contamination is strictly better than one that overstates its coverage — but this should be
a tool capability, not a prose convention.
