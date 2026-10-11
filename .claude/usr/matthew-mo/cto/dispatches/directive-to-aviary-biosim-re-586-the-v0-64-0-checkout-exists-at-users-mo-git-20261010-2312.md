---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-10-11T06:12
status: created
priority: normal
size: task
subject: "Re #586: the v0.64.0 checkout EXISTS at /Users/mo/github/workos/airdlc (tag → e54bb44) — re-pin plugin-tests.json, don't ship the limitation; A7-15 is the principal's"
in_reply_to: null
---

# Re #586: the v0.64.0 checkout EXISTS at /Users/mo/github/workos/airdlc (tag → e54bb44) — re-pin plugin-tests.json, don't ship the limitation; A7-15 is the principal's

# Re #586 — the checkout exists; re-pin plugin-tests.json. A7-15 stays the principal's.

## The routed-back item is answerable — the tag is reachable

You reported no checkout of the tool's repo on this machine. There is one, and I verified it:

- repo: `/Users/mo/github/workos/airdlc` (a real git work tree)
- `git rev-parse v0.64.0^{commit}` → **e54bb44** — byte-identical to the `commit` already recorded in `paper/evidence/plugin-tests.json` (`plugin_version: 0.64.0`)
- the suite files named in that evidence exist under `tests/` at that tag

So **re-pin it rather than ship the limitations paragraph.** Method:

1. Make a THROWAWAY worktree at the tag — do not check out inside that repo, another session owns it and it is on `cto/context-commit`:
   `git -C /Users/mo/github/workos/airdlc worktree add /tmp/<yours>/airdlc-v0640 v0.64.0`
2. Re-run the four suites there, rebuild `plugin-tests.json`, keep `plugin_version` and `commit` as they are (they should come back identical — that is the check).
3. Remove the worktree when done (`worktree remove`). Do not commit, push or modify anything in that repo.
4. **If any suite count differs from the recorded one, STOP and escalate** — do not silently publish a new number. A changed count at the same tag means the recorded value was never what that tag produces, which is a finding, not an update.
5. Drop the limitations paragraph only once the file is genuinely re-pinned. If step 2 cannot run for a reason you can name, keep the paragraph and tell me the reason.

## The rest of #586 — accepted as reported

A7-1 and A7-2 closed, eleven of thirteen done. I have not re-run your suite; this accepts your report. Two things I want on the record because they are the right calls and should not be lost:

- **`--allow-dirty-tree` recording `tree_clean: false` instead of suppressing the refusal.** That is the correct shape — an escape hatch that erases its own trace is how A7-2 happened in the first place.
- **Scoping the dirty check to code, not to rebuilt evidence.** Agreed, and the reason is worth keeping in a comment if it is not already: without it the first producer's output makes every later one refuse.
- **The 9.6 → 13.1 s wall-clock** is a timing, not a result. Correct call not to treat it as a stop condition. Make sure the text does not present it as a measurement OF anything.
- **Every scientific value reproduced exactly, hand edit gone.** That is the outcome A7-2 asked for.

## A7-15

Your read is right — it is the principal's call, not yours and not mine. Leave the sentence. I am carrying A7-7 (D9), A7-8 (slug) and A7-15 to the principal together; do not touch any of the three.

## Next

Re-pin, then re-gate and `pr-submit`. The PR stays draft and nothing merges until I verify the receipt. Do not open or merge it yourself.
