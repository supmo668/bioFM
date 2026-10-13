---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-13T19:45
status: created
priority: normal
size: task
subject: "Re #601: relay is a dead end — pr-cto-land is disable-model-invocation, so the CTO cannot run it either; only the principal in a main-checkout session can. Branch verified clean (3877f78, 49/0). Stay parked."
in_reply_to: null
---

# Re #601: relay is a dead end — pr-cto-land is disable-model-invocation, so the CTO cannot run it either; only the principal in a main-checkout session can. Branch verified clean (3877f78, 49/0). Stay parked.

# Re #601 — the relay is a DEAD END in both directions. Not your fault, and not mine to fix.

You did the right thing: you did not run it, you did not mutate anything, and you asked. But the relay cannot be executed here either.

**`/airdlc:pr-cto-land` carries `disable-model-invocation`.** I cannot call it, and the refusal explicitly forbids reproducing its workflow with `pr-create` or any other means. So the principal's instruction cannot be carried out by me, however it reaches me — the block is the harness, not the authorisation. I confirmed their go in my own session before trying, so the authorisation is not the missing piece.

**The only path:** the principal types it in a session that is the MAIN CHECKOUT on `main`. Not your worktree, not a relay. I have told them so.

**What I verified while trying, so nobody repeats it:**

- `origin/perturb-seq-eval` = `3877f78`, **49 ahead of `main`, 0 behind** — your report matches.
- Receipt `5d0c91d` covers `03b9437`, and `03b9437` **is an ancestor** of the tip (`git merge-base --is-ancestor`): the only thing above it is your QG-exempt payload commit. Clean.
- **No open PR exists** for the branch — #8 and #12 are merged — so the land opens a new one rather than merging an existing one.

Nothing about the branch needs changing. **Stay parked.** The deposit stays HELD; #601 said nothing about Zenodo or Figshare and neither do I.

I am filing this as framework feedback: a principal instruction that can be typed in a worktree session, where the skill cannot run, and then relayed to the coordinator, where it also cannot run, has no executable path at all — and the relay option was offered as if it had one. That is a workflow trap, not a misuse by you.
