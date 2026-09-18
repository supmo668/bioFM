---
type: plugin-feedback
target: aiadlc plugin (aiadlc-plugins)
plugin_version: 0.56.0
reporter: biofm/matthew-mo/cto
date: 2026-09-17
scope: plugin / operating-system behavior — NOT repo/app work
---

# `instinct capture` discards a correction and reinforces the stale body

Surfaced while auditing `/v2r-loop` against the run it produced in
`projects/aviary-biosim` (five captured instincts, one of which carries a
hand-written workaround note for this exact defect).

## 🔴 1. `capture` on an existing name throws away `--body`, raises confidence, and exits 0

**File:** `tools/instinct`, `cmd_add` — lines 206–209

```python
    slug = slugify(name)
    path = os.path.join(store_dir(), f"{slug}.md")
    if os.path.isfile(path):
        # reinforce instead of clobbering
        return cmd_reinforce([slug])
```

**Symptom.** An agent that has learned a *better* version of a lesson re-captures
it under the same name. The tool reports success, the corrected text is silently
dropped, and confidence in the **superseded** text goes up.

**Root cause — proven, not guessed.** `cmd_add` short-circuits to `cmd_reinforce`
whenever the file exists. `--body` has already been parsed at that point and is
simply never used. `cmd_reinforce` then bumps `confidence` and `last_reinforced`.
The comment's intent ("don't clobber") is right; the implementation converts a
correction into a reinforcement of the thing being corrected.

**Repro** (isolated throwaway repo, plugin 0.56.0, verbatim):

```
$ instinct capture --name repro-lesson --confidence 0.6 \
    --body "ORIGINAL BODY: this text is WRONG and needs correcting."
captured: repro-lesson (confidence 0.60) -> .aiadlc/instincts/repro-lesson.md
exit=0
confidence: 0.600
ORIGINAL BODY: this text is WRONG and needs correcting.

$ instinct capture --name repro-lesson --confidence 0.6 \
    --body "CORRECTED BODY: this is the fixed lesson that must replace the original."
reinforced: repro-lesson -> confidence 0.70
exit=0
confidence: 0.700
ORIGINAL BODY: this text is WRONG and needs correcting.        <-- unchanged
```

`exit=0` both times. The only signal that the correction was refused is the word
`reinforced:` instead of `captured:` on stdout — which no caller checks, because
both are success.

**Why this is 🔴 rather than 🟠.** The store is not inert: `cmd_surface` injects
every instinct above `instincts.min_confidence` (default 0.6) into SessionStart
context. So a wrong lesson that an agent *tried to fix* crosses the surfacing
threshold **because** it was fixed, and is then injected into every future session
as higher-confidence guidance. There is no in-tool path to correct it — the
`capture · reinforce · match · list · surface · decay · prune · export` verb set
has no "revise". The only remedy is hand-editing the file, which is what the
Aviary-BioSim run had to do; that instinct now carries this note verbatim:

> Tooling note: `instinct capture` on an existing name only REINFORCES it; it does
> not replace the body. To correct an instinct's text, edit the file.

A memory layer whose documented correction procedure is "bypass the tool" is not
yet a memory layer.

**Fix.** Two parts, smallest viable:

1. **Never reinforce on a call that supplied a different body.** In `cmd_add`:

   ```python
   if os.path.isfile(path):
       existing = parse_instinct(path)
       if existing.get("_body", "").strip() == body.strip():
           return cmd_reinforce([slug])          # genuine recurrence
       sys.stderr.write(
           f"instinct capture: '{slug}' exists with a different body.\n"
           f"  revise it:  instinct revise --name {slug} --body ...\n"
           f"  or edit:    {path}\n"
           f"Not reinforced — a correction is not a recurrence.\n")
       return 1
   ```

2. **Add `revise`**, which replaces `_body` (and optionally `triggers`/`tags`)
   while preserving `created` and the confidence lineage, and does **not** bump
   `last_reinforced` — revising is not evidence the pattern recurred.

**Effect once applied.** A corrected lesson can be recorded through the tool
instead of around it; confidence stops accumulating on text that nobody actually
re-observed; and `instinct_pin` (see the companion report on run records) starts
meaning "this content", not "this filename".

**Related:** `.claude/aiadlc-feedback/2026-09-12-instinct-layer-has-no-discovery-or-pin.md`
covers reinforcement-without-discovery and the missing pin primitive. This is a
third, distinct defect in the same tool: **reinforcement instead of correction.**

**⚠ Prior art — this is a re-find, disclosed.** The same defect was already filed on
2026-09-13 as item 🟠 3 of
`2026-09-13-spend-cap-is-declared-but-never-metered.md`, with the same root cause and
the same "correction registers as a recurrence" insight, observed live on the same
v2r stage-4 instinct. I missed it because my duplicate check matched on file titles
and that entry lives under an unrelated one. What this filing adds: a deterministic
repro, the threshold arithmetic that makes it 🔴 rather than 🟠, and the `revise`
design that was implemented. **Convention lesson: one defect per file** — a real
defect buried as item N under someone else's title is functionally unfiled.

**Status:** fixed in aiadlc PR #107 (`cto/instinct-revise`) — open until it lands.
On landing, `capture` with a differing body **fails** instead of reinforcing; any
caller relying on capture-as-upsert must move to `instinct revise`. Checked
2026-09-17: bioFM has no such caller — the Stop hook (`instincts-reinforce.sh`)
calls `reinforce`, and every other reference is prose.
