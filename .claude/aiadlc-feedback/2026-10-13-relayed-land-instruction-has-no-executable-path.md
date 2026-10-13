# A relayed land instruction has no executable path — the worktree cannot run it and neither can the coordinator

**Filed:** 2026-10-13 · **By:** biofm/matthew-mo/cto · **Plugin version in effect at filing:** 0.82.0
**Scope:** plugin / operating-system behavior — NOT repo/app work
**Status:** open

**Symptom.** The principal typed `/airdlc:pr-cto-land perturb-seq-eval --no-release` **twice** in a
worktree agent's session (ISCP #601, relaying session `b6e15309`). The skill's preconditions need the
main checkout on `cto.branch`, so it could not run there. The agent correctly refused to mutate
anything and offered the principal a choice; the principal chose **"Relay to CTO"**. The agent then
relayed the instruction verbatim to the CTO.

**The CTO cannot run it either.** `/airdlc:pr-cto-land` carries `disable-model-invocation`:

> Skill airdlc:pr-cto-land cannot be used with Skill tool due to disable-model-invocation. Ask the
> user to run /airdlc:pr-cto-land themselves — it cannot be invoked via the Skill tool. Do not
> replicate this skill's workflow by other means — it is reserved for explicit user invocation.

So the instruction had **no executable path at all**: not in the session where it was typed, and not
at the only address the relay could send it to. Authorisation was never the missing piece — the CTO
had confirmed the principal's go in its own session before attempting it.

**Why this is a trap rather than a misuse.** The relay option was presented as a way forward. A
coordinator that accepts a relayed land instruction has, by construction, accepted something it
cannot perform, and the branch sits "land-ready, principal-approved" while nothing can move it. The
agent is then parked waiting on a coordinator who is waiting on a human who already typed the
command — twice.

**Fixes, in preference order:**
(a) **`/airdlc:pr-cto-land` detects a worktree session and says what to do** — name the main checkout
and the branch to be on — instead of failing its preconditions and leaving the relay as the apparent
next step.
(b) **Remove "Relay to CTO" as an offered option for `disable-model-invocation` skills**, or have the
relay reply state up front that the recipient cannot execute it.
(c) A `tools/land-request` primitive that records the principal's go durably so the human's typed
intent is not lost between sessions, and any session can show it is outstanding.

**Effect.** A principal instruction stops being silently unexecutable, and a coordinator stops
accepting work it is forbidden to do.
