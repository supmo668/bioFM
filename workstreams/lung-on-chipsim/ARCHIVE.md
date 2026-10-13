# Stage 1 archive — the bundle of record

**Written by the CTO 2026-10-13**, closing the single-disk exposure that ruling A2 (2026-10-04)
raised. A2 asked for a push to `archive/lung-on-chipsim-stage1` on `origin`; the principal chose a
**bundle** instead on 2026-10-13, because `origin` is public and the archived tip still carries the
five files ruling A3 withheld from `main`. A branch is no less public than a trunk, so the push
would have performed what A3 forbids. The bundle preserves the history off this repository without
publishing anything.

## What exists

| | |
|---|---|
| File | `~/bioFM-archives/lung-on-chipsim-stage1-f66fbf7-20261013.bundle` (NOT in this repo — it carries the withheld five) |
| Size | 46 MB |
| SHA-256 | `f6748010ecff8538e2ea9fbcddeb3e7cda600403a64ca5c238c0cb48d927a87d` |
| Branch | `lung-on-chipsim` @ `f66fbf73d0221dc8f1cc27b64a367b92bd46292c` |
| History | complete and standalone (`git bundle verify`: *"records a complete history"*) |

## Restore, and what the restore proved

```bash
git clone --branch lung-on-chipsim \
  ~/bioFM-archives/lung-on-chipsim-stage1-f66fbf7-20261013.bundle <dest>
```

Run on 2026-10-13 into a scratch directory, then deleted. The clone came back with tip `f66fbf7`,
**1303 commits**, the four `chipsim/transport/{ode,fit,prior,theta}.py` files at **920 lines**, and
all five withheld files. Verification alone would not have established this: a bundle can verify and
still not be the thing you needed, so the archive was restored rather than assumed.

## What it is for

`transport/{ode,fit,prior,theta}.py` existed **only** on one machine: the remote
`lung-on-chipsim` is still at `c04e701`, 618 commits behind this tip, and holds none of them.
Stage 2's M1 fit depends on that code (ruling A1 brings `transport/` over by content once A2 made it
reachable). The bundle is what makes A1 possible without a public push.

## Still owed by the principal

**One file on one disk is not an archive.** Copy the bundle off this machine — another disk, or
private storage. Until that copy exists, the exposure is reduced (it survives a repo mishap) but
not closed (it does not survive the disk). Re-verify after copying:

```bash
shasum -a 256 <copy>   # must equal the SHA-256 above
git bundle verify <copy>
```
