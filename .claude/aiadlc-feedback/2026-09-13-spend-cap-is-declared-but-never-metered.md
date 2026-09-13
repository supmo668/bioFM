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
