---
type: plugin-feedback
target: aiadlc plugin (bioFM) — skills + coordination surfaces
plugin_version: 0.59.0
reporter: bioFM/matthew-mo/cto
date: 2026-09-19
scope: plugin / operating-system behavior — NOT repo/app work
---

# Human-owned blockers have two states, and the framework only models one of them

Both findings came out of building a `/grill-with-res` skill by hand because the plugin
had no shape for the job. The second is the serious one.

## 🟠 1. No evidence-assembly mode for a human-owned blocker

**File:** `skills/research/SKILL.md`, `skills/grill-me/SKILL.md`; absent skill
**Symptom:** A task marked **H** (human-owned) sits untouched because the only two
sanctioned states are *the agent writes it* (forbidden by the allocation rule) and *the
human writes it cold*. Nothing assembles the evidence that would let the human decide in
five minutes instead of forty-five.

`/research` (MARFI) is the closest fit and is the wrong shape for it: it is a heavyweight
standalone pass that drafts a cross-cutting question set, fans out researcher subagents, and
terminates in a **research brief that `/define` consumes**. It grounds a PVR. It does not
resolve one blocked decision that is already specified.

`/grill-me` and the user-level `/grill-with-docs` are the right *interaction* shape —
relentless, one question at a time, each with a recommended answer — but both resolve
questions from what is already in the room: the user's memory, or the codebase.
`grill-with-docs` states it outright: *"If a question can be answered by exploring the
codebase, explore the codebase instead."* Neither goes outside.

**Root cause:** the skill set models *where an answer comes from* as {the human, the repo}.
For a human-owned claim, the answer often comes from **neither** — it comes from external
literature or data, and the human's job is to *judge* it, not to recall it.

**Fix:** ship a `grill-with-res`-shaped skill in the plugin. Written and in use at
`~/.claude/skills/grill-with-res/SKILL.md` — copy it in. The load-bearing parts:

- inverted routing — *if a question can be answered by external research, research it
  instead of asking me*;
- a hard rule that survives the temptation to be helpful: **research produces evidence, the
  human produces the claim**; the skill never writes the artifact under grill;
- an evidence ledger where every row carries a resolvable source, and `not found` is a row;
- termination in a compact decision surface the human signs off **row by row**, with
  mechanical rows (derived from data the project holds) visually separated from judgement
  rows, because conflating them wastes the attention the skill exists to save.

**Effect:** an H task stops being a wall. The human still makes the claim — which is the
point of marking it H — but makes it against assembled, cited evidence.

**Status:** open (skill exists locally; not in the plugin)

## 🔴 2. Nothing tracks a precondition the COORDINATOR owes the HUMAN

**File:** `tools/blocker-sweep`, `tools/dispatch`, handoff `## Principal Decisions Needed`
**Symptom:** For several days this CTO reported task T18 as *"blocked on the principal"* in
every handoff and status. It was not. The plan specifies that the roster is authored on a
**guarded candidate list handed over by the CTO**, and that the milestone clock runs *"from
the day the guarded candidate list is handed over"*. **No candidate list had ever been
generated. No command existed to produce one. The clock had never started.**

So the principal was waiting on the CTO, the CTO was reporting the principal as the blocker,
and every surface in the framework agreed with the CTO.

**Measured, not inferred:** `configs/poc_compounds.yaml` absent (expected — it is the human
artifact); repo-wide search for a candidate-list generator returns nothing; one dispatch in
the entire history mentions the phrase, as a directive rather than a delivery.

**Root cause:** every blocker surface is **agent-centric and inbound**. `blocker-sweep`
answers *what are my agents waiting on?* The handoff's `## Principal Decisions Needed`
answers *what do I need from the human?* Neither answers **what does the human need from
me?** — and that is exactly the direction that fails silently, because the party who would
notice is the one not being asked.

It compounds with the H-task rule. "Escalate, not simulate" is correct and the agent obeyed
it perfectly. But an escalation that names the human as the blocker, when the coordinator
owes them an undelivered input, is a *correctly-formed* report of a false state. The rule
produces confident wrong answers when a precondition is missing.

**Fix (smallest viable):**

1. Let a plan task declare a precondition the coordinator owes:
   `owed_by: cto` / `owed_to: principal` / `starts_clock: true`.
2. Have `blocker-sweep` emit an `OWED` line for any declared precondition with no delivery
   dispatch — in the same nagging style as `PARKED`, since that nagging is the point.
3. **Refuse the false report:** a boundary or handoff that names a human as the blocker for a
   task whose coordinator-owed precondition is undelivered should fail, or at minimum print
   the contradiction. This is the load-bearing half — items 1 and 2 only help someone who
   goes looking.

**Effect:** the failure that is invisible from both ends becomes visible from one. A
coordinator cannot spend days reporting a human as blocked on a decision that was never
actionable.

**Status:** open

---

**Cross-reference.** This is the same family as the five ambient-state defects filed
2026-09-16/17 (monitor identity from `cwd`, receipt verification from the working copy,
quality-config resolution, the tracked monitor registry, `blocker-sweep` counting resolved
escalations): **a surface derives a correctness-relevant answer from something adjacent to
the thing it describes.** Here the adjacent thing is *direction* — every blocker surface
looks inbound, so an outbound debt is structurally unobservable.
