---
type: plugin-feedback
target: aiadlc plugin (aiadlc-plugins)
plugin_version: 0.54.0
reporter: bioFM/main/cto
date: 2026-09-13
scope: plugin / operating-system behavior — NOT repo/app work
---

# The autonomous loops declare a spend cap that nothing measures

## 🔴 1. `/ceo-loop`'s spend cap is unenforceable — there is no meter

**File:** `skills/ceo-loop/SKILL.md:86, 92, 159`; `tools/` (absent); `agency.yaml` (absent)

**Symptom:** An armed `/ceo-loop` run declares `spend<=<cap>`, promises to "stop at the
spend cap", and is required to report "spend-to-date against the cap" in each hourly
ledger. None of those three things can actually happen. The cap is a substring inside an
authorization string, compared against nothing.

**Root cause:** Proven by absence, checked three ways:

```
$ ls tools | grep -i 'spend\|budget\|cost\|credit'     # (nothing)
$ grep -i 'spend\|budget\|cost\|credit\|ceiling' agency.yaml   # (nothing)
$ grep -rn -i 'spend\|budget' skills/ceo-loop/SKILL.md  # 4 hits, all prose obligations
```

There is no tool that records a cost, no config key that holds a cap, and no state file
that accumulates a running total. The skill text imposes an obligation on the agent to
self-report a number it has no way to obtain — so in practice the agent either omits it,
or estimates it, which is worse: an estimated spend-to-date reads exactly like a measured
one in the ledger.

This is the same defect class the framework already guards against elsewhere. ChipSim's
**R1 preflight gate** ("refuses to start unless free RAM, free disk, and remaining Modal
credit each exceed a declared floor") and **R9 budget guard** ("spend is tracked and the
run halts before exceeding the declared credit") both presuppose a meter. The framework
asks domain work to meter its floors while its own loops do not meter theirs.

**Fix:** A small `tools/spend`, mirroring the shape of `tools/instinct` — a single-file
CLI over an in-repo JSON state file, with config under `agency.yaml`:

```
spend record --usd <amount> --label "<what>"   # accumulate
spend total                                    # running total for the current window
spend check --cap <usd>                        # exit 0 under cap, non-zero over
spend reset --window <arm-id>                  # new window when a loop is armed
```

```yaml
spend:
  enabled: true
  store_path: ".aiadlc/spend.json"
  default_cap_usd: 25
```

`/ceo-loop` and `/cto-loop` call `spend check` each iteration and halt on non-zero;
`spend total` supplies the ledger's spend-to-date. The halt-on-breach semantics should
match the existing ceiling discipline: a cap breach **halts the loop**, it does not
retire one work item.

**Effect:** The cap becomes real. An armed overnight loop stops at the declared number
instead of promising to, and the ledger reports a measured figure instead of an estimate.

**Provenance / offer:** bioFM's `/v2r-loop` has the identical hole —
`check_ceilings(data, started_at, spend_usd)` takes spend as a caller-supplied parameter
because nothing measures it. A tested `SpendTracker` is being built now in
`supmo668/Aviary-BioSim` (record / total / declared floor from config / raises above the
floor / survives a process restart, each closed by an independent sealed test). It is the
right shape to port into `tools/spend` rather than writing the same component twice, and
we will offer it upstream once its sealed tests close.

### Port specification (conventions checked against `tools/instinct`)

This is a re-expression, not a copy — `tools/instinct` is **stdlib-only, zero-pip**, so the
ported tool must be too. What transfers is the behaviour set and the sealed tests that pin
it; the implementation is rewritten to match house style:

- `#!/usr/bin/env python3`, stdlib only, `TOOL_VERSION` constant
- `cfg("spend.store_path", ".aiadlc/spend.json")` via the existing config helper
- `main(argv)` dispatch with `--help` / `--version`, matching `tools/instinct`
- Header block stating what / why / lifecycle / store / provenance

| Behaviour (sealed-tested in Aviary-BioSim) | `tools/spend` surface |
|---|---|
| records per-call cost, accumulating | `spend record --usd <n> --label "<what>"` |
| totals what was recorded | `spend total` |
| declared floor loads from config | `cfg("spend.default_cap_usd", 25)` |
| refuses above the declared floor | `spend check --cap <usd>` → non-zero over |
| survives a process restart | the JSON store itself |
| new window when a loop arms | `spend reset --window <arm-id>` |

**Does NOT port:** the aviary `Tool.from_function` exposure. That is environment-specific
and stays in Aviary-BioSim.

**Call sites to wire once the tool exists:**
- `skills/ceo-loop/SKILL.md:86` — the `spend<=<cap>` authorization becomes a real cap
- `skills/ceo-loop/SKILL.md:92` — the ⛔ SPEND rule gains an enforcement path
- `skills/ceo-loop/SKILL.md:159` — the ledger's "spend-to-date" becomes `spend total`
- `skills/cto-loop/SKILL.md` — same halt-on-breach check per iteration

**Status:** open — implementation available to port

## 🟠 2. `worktree-create --coordinator` is documented but not implemented

**File:** `skills/worktree-agent-create/SKILL.md` (Step 2); `tools/worktree-create`

**Symptom:** Following `/worktree-agent-create` verbatim fails. Step 2 says to run
`tools/worktree-create --submodule <subdir> --agent <name> --coordinator "$OWNER"`; the
tool does not accept `--coordinator` and responds by printing its help text, which reads
as a successful no-op unless you check for the worktree afterwards.

**Root cause:** The skill documents a flag the shipped tool's option list does not
include — the docs are ahead of the tool at 0.54.0. Auto-assignment works correctly
without it (the worktree reported `Coordinator: cto` and wrote `.aiadlc-coordinator`), so
the flag is redundant rather than missing functionality.

**Fix:** Either accept and honour `--coordinator` in `tools/worktree-create`, or drop it
from the skill's Step 2 and rely on the auto-assignment the tool already performs.

**Effect:** The documented happy path works first time instead of silently printing help.

**Status:** open

## 🟠 3. `instinct capture` on an existing name reinforces it and silently keeps the stale body

**File:** `tools/instinct` (`capture`); `skills/instinct-capture/SKILL.md`

**Symptom:** An agent that learns its earlier instinct was wrong re-runs `instinct capture`
with the same `--name` and a corrected `--body`, sees the command succeed, and believes the
lesson is updated. It is not. Confidence is bumped, the body is unchanged, and the stale
text is what surfaces at the next SessionStart — with *higher* confidence than before,
because the correction registered as a recurrence of the thing it was correcting.

**Root cause:** `capture` on an existing name takes the reinforce path. That is correct for
its designed use — the Stop hook reinforcing a recurring pattern — but `capture` is also the
only documented way an agent records a lesson, so it is what an agent reaches for when the
lesson has *changed*. The skill does not say the two cases diverge, and nothing in the output
distinguishes "reinforced, body kept" from "captured".

Observed live: a stage-4 instinct written during drain 1 said the drain's spans were
unreadable. When the underlying defect was fixed, re-capturing under the same name left the
"until then, unreadable" text in place, now carrying more confidence. It was caught only
because the agent opened the file.

**Fix:** Smallest version — make the outcome legible and the update path documented:

- `capture` on an existing name prints `reinforced <name> (body unchanged; edit the file or
  pass --replace to update it)` rather than reporting a plain capture.
- Add `--replace` to overwrite the body while preserving confidence and history.
- One line in `skills/instinct-capture/SKILL.md` stating that re-capturing an existing name
  reinforces rather than replaces, and naming the update path.

**Effect:** A corrected lesson actually corrects. Today the failure is silent and
self-reinforcing, which is the worst shape for a memory layer: the more often an agent tries
to fix a wrong instinct, the more confident the wrong instinct becomes.

**Status:** open

