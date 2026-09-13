# /build-loop — requirement-to-function build-out

**Status:** design approved 2026-09-12
**Glossary:** [`docs/build-loop/CONTEXT.md`](../../build-loop/CONTEXT.md) — terms in **bold** below are defined there
**Decisions:** [`docs/build-loop/adr/`](../../build-loop/adr/)

## Goal

One prompt states an objective. The loop turns it into a reviewed branch of working,
individually-tested code, and improves at doing so across successive attempts — without a
human present for anything except a single approval at the start.

## Why this shape

Three properties are load-bearing, and each restates a rule this repo already enforces one
altitude down:

| Invariant | Mechanism | Precedent in this repo |
|---|---|---|
| The actor that does the work never records that the work passed | `register.py close` re-runs the **sealed test** itself | ChipSim's **frozen evaluator** — "outside the agent's write scope" |
| A **drain** is attributable to exactly one builder | **instinct pin**, hashed at drain start | The **replay test**; audit R2 pre-registration |
| Declared floors stop the run | ceilings checked every **iteration** | Audit R1 preflight gate, R9 budget guard |

## Architecture

### Input

```
/build-loop "<objective>"
```

The objective is the only thing the user authors.

### Stage 0 — Preflight and unblock (unattended)

Before anything is decomposed, the loop resolves its own access blockers from the credentials
and MCP servers already available, and refuses to continue if any remain. This is audit R1's
preflight gate generalized: *a run refuses to start unless its declared floors are met.*

| Blocker | Resolution | Status |
|---|---|---|
| Inference compute (GPU) | **W&B Inference** — serverless, OpenAI-compatible; no local GPU on the critical path | resolved |
| `WANDB_API_KEY` | Infisical `biofm/dev` | resolved |
| Trace read access | `wandb` MCP server | resolved |
| Trace write access | `register.py` `@weave.op` spans | **not yet built** |
| Instinct store | `continuous-learning-v2` hooks | **not installed** |

A blocker that cannot be resolved from available credentials **halts before the gate**, and is
reported as a named blocker rather than worked around. The loop never asks a human mid-drain;
it either has what it needs at stage 0 or it does not start.

#### Inference configuration

```python
client = openai.OpenAI(
    base_url="https://api.inference.wandb.ai/v1",
    api_key=os.environ["WANDB_API_KEY"],      # Infisical: biofm/dev
    project="3m-m/Aviary-BioSim",
)
MODEL = "deepseek-ai/DeepSeek-V4-Pro-0813"
```

DeepSeek-V4-Pro is a reasoning model: reasoning tokens are billed against `max_tokens`, so a
small ceiling returns `content: null` with `finish_reason: "length"`. Every call site budgets
for reasoning separately. This is the loop's inference path for any model call it makes
directly; Claude Code subagents remain the implementers and test-authors.

### Stage 1 — Preamble (attended)

Produces the **approved artifact**, three files, then stops:

- `spec.md` — standing **requirements** `R<n>`. Each is a claim about the system that holds
  for the life of the project. Never closed.
- `register.yaml` — **build units** `U-nnn`, each atomic, independently testable, carrying
  `satisfies: R<n>`. One requirement yields one-to-many units.
- `skeleton/` — real modules, real signatures, `NotImplementedError` bodies, one stub per
  unit, committed before any drain starts.

The skeleton exists so the sealed **test-author** and the implementer bind to symbols neither
of them authored. Without it, both produce reasonable but incompatible readings of the same
unit text and the unit parks on `ImportError` forever.

### Stage 2 — The gate (the only human checkpoint)

The user reads the three artifacts once. Approval:

1. **Fixes scope permanently.** No later drain may introduce a unit absent from this register.
2. **Declares ceilings** — `max_drains`, `max_attempts` per unit, `max_wall_clock`, `max_spend`.
3. **Grants standing authorization** to push the worktree branch and open a PR at drain end.

Approving the skeleton means approving the API shape, which is the artifact where human
review most outperforms an agent and where a mistake is most expensive to find late.

### Stage 3 — Drain (unattended)

Runs in an aiadlc worktree, `branch == agent name`. The **instinct pin** is hashed and
written to the **run record** before the first claim and does not change for the duration.

```
while an open build unit remains and no ceiling is breached:
    claim U-nnn
      test-author subagent   → sealed test, from unit text + skeleton ONLY
      implementer subagent   → fills the stub, never sees the test
      register.py close U-nnn
        ├─ re-runs the sealed test itself
        │    pass → commit "U-nnn <summary> (satisfies R<n>)"
        │    fail → retry, up to max_attempts
        └─ budget spent → git branch park/U-nnn
                          git reset --hard <pre-claim>
                          register.py park U-nnn --evidence <test output>
```

Because a **park** reverts the tree, every commit on the branch is green by construction and
the history is bisectable at behaviour granularity.

A park is **local**. It carries no `blocked_by`, triggers no cascade, and implies nothing
about any other unit. A unit needing the parked work fails on its own terms and parks on its
own terms; the parked list is triaged by a human in one pass.

A **halt** — any ceiling breach — abandons the drain. Register, `park/*` branches and run
record all survive, so a halted drain is resumable.

At drain end: `gh pr create` on the worktree branch, handed to the CTO. **The loop never
writes `main` and never lands its own PR.**

### Stage 4 — Between drains

1. `query_weave_traces_tool` over the drain's spans — which units parked, at which attempt,
   on what failure.
2. `instinct capture` per durable lesson, via aiadlc's `tools/instinct`, with the drain's
   touched paths as `--triggers` so the Stop hook reinforces them on recurrence.
3. Commit `.aiadlc/instincts`; the new **instinct pin** is `git rev-parse HEAD:.aiadlc/instincts`.
4. Drain *n+1* retries **only parked units**.

The learning substrate is aiadlc's instinct layer — store `.aiadlc/instincts`, SessionStart
surface, Stop-hook reinforcement, `agency.yaml instincts.*` (already `enabled: true`).
`continuous-learning-v2` is deliberately **not** installed here: it would run a second store
with different confidence semantics and its own SessionStart surface, leaving neither
authoritative.

Terminates when a drain closes zero new units, or `max_drains` is reached. Remaining parked
units are reported for human triage.

## Components and boundaries

| Component | Owns | Never |
|---|---|---|
| `register.py` | every state transition; re-running sealed tests; ceiling checks; run record | judging whether work is good |
| preamble stage | spec, register, skeleton | running any unit |
| test-author subagent | the sealed test, from unit text + skeleton | seeing the implementation |
| implementer subagent | filling one stub | seeing the sealed test; editing `tests/sealed/` |
| drain driver (`SKILL.md`) | claiming, dispatching subagents, drain sequencing | asserting a close |

`register.py` is the only component whose correctness the rest of the system trusts. It is
small, has no LLM in it, and every transition it performs is independently verifiable.

## Data shapes

```yaml
# register.yaml
units:
  - id: U-014
    satisfies: R9
    statement: "SpendTracker.record accumulates per-call cost"
    stub: skeleton/spend_tracker.py::SpendTracker.record
    state: parked            # open | closed | parked
    attempts: 3
    evidence: parked/U-014.pytest.out
    park_branch: park/U-014

# run-record.yaml — one per drain
drain: 2
register_sha: sha256:…
instinct_pin: d4e5f6
seed: 1337
ceilings: {max_drains: 3, max_attempts: 3, max_wall_clock: 6h, max_spend: 25}
closed: [U-001, U-002, U-016]
parked: [U-014, U-015]
outcome: completed          # completed | halted
```

## Error handling

| Condition | Response |
|---|---|
| Sealed test fails | Retry to `max_attempts`, then **park** |
| Unit parks | Branch + revert + evidence; continue to next unit |
| Ceiling breached | **Halt**; preserve everything; report |
| `close` cannot run the test at all | Halt, not park — a gate that cannot execute is a broken gate, not a failed unit |
| Implementer writes into `tests/sealed/` | Blocked by the existing `test-seal` PreToolUse hook |
| Drain closes zero units | Terminate the outer loop and report |

## Testing

`register.py` carries the trust, so it is tested directly and adversarially:

- `close` refuses when the sealed test fails, is missing, or errors on collection.
- `close` refuses when the test file was modified after authoring.
- `park` leaves the tree byte-identical to its pre-claim state.
- `park` preserves the attempt on `park/U-nnn`.
- Ceiling breach produces a halt, never a park.
- A drain replays: same register, same instinct pin, same seed → same closed and parked sets.

The drain driver is tested against a fixture register with deliberately unsatisfiable units,
asserting the parked list and the green-commit invariant.

## Known gaps

1. **Weave will capture nothing automatically.** It auto-traces SDK calls; Claude Code
   subagents are not SDK calls. `register.py` must emit its own `@weave.op` spans per
   iteration — unit text, attempt count, test output, outcome — or stage 4 has no input.
   This is implementation work, not configuration.
2. ~~The W&B MCP server is not installed.~~ **Resolved 2026-09-12** — connected at user
   scope; `WANDB_API_KEY` and `WANDB_PROJECT` stored in Infisical project `biofm`, env `dev`.
   The key was pasted in plaintext and should be rotated.
3. **No instinct discovery without a human.** aiadlc reinforces instincts someone already
   captured; it never discovers one. During an unattended drain nobody runs
   `/instinct-capture`, so stage 4 must capture explicitly from trace evidence. Automatic
   observation is filed as upstream feedback to aiadlc. `.aiadlc/instincts` does not exist
   yet, so drain 1 runs against an empty pin — which is correct, not a defect.
4. **Two trace backends.** Logfire is already wired as the session-tracing sink. W&B for
   iteration analysis and Logfire for sessions is defensible, but it should be a decision
   rather than an accident.

## Out of scope

- Landing the PR — the CTO lands; the loop hands over a branch.
- Widening scope between drains — new work needs a new prompt and a new approval.
- Dependency graphs, `blocked_by`, cascade — priced and declined; see ADR-0004.
- A headless `--detach` runtime — the register is already the state file, so this is a later
  addition rather than a rewrite.
- The aviary drug-discovery environment itself. `/build-loop`'s first real target, and its
  own spec. Target repo: `3m-m/Aviary-BioSim`.
