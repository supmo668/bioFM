# Deferred findings — security detail (private)

The public register at `aviary-biosim/docs/deferred-findings.md` carries security rows as
id + severity + "held". The detail lives here until the fix ships, then the full row moves
to the public register and this entry is deleted.

**One exemption, and read it before promoting anything.** That lifecycle assumes the only
reason for privacy is an unshipped fix. **C-001 is not a security finding and is NOT subject
to it** — it is held here because stating it descriptively in a public, durable register
would reproduce the very pairing being withheld. There may never be a "fix" to ship, and
promoting C-001 on the usual rule would publish exactly what it exists to withhold.
C-001 moves only on the principal's explicit instruction.

This file is in the **superproject**, which is private and tracks `workstreams/`. It is
deliberately NOT in the submodule: that repo is public, and its own `workstreams/` is
gitignored, so a file there would die with the worktree and be invisible to everyone else.

---

## S-001 — raw model-authored content is printed to the operator's terminal

- **Raised:** gate #215 (security reviewer), confirmed by the CTO in #216.
- **Severity:** security (CWE-150, escape-sequence injection into a terminal).
- **Status:** open, scheduled as its own unit.
- **Live repro:** not yet written. The analogous defect *was* demonstrated inside the #215
  diff, which is why this is not filed as a background nit.

**Where.** `aviary-biosim/science/run_discovery.py`, the two `print` calls that echo the
model's turn content and its conclusion straight to stdout.

**What.** The content is authored by an untrusted LLM and printed unescaped. ANSI/OSC
sequences in it are interpreted by the operator's terminal: clearing the screen, repainting
earlier output, hiding text, or setting the window title. The operator is reading that
stream to judge whether a discovery run behaved, so an agent that can repaint it can
mislead the person supervising it.

**CORROBORATION ADDED 2026-09-24 (PR c8231442, F08 gate) — a SECOND live instance.**
The `esm_tool` tools echoed `rec["accession"]`, which on the **cached** branch is *file
content* rather than validated input. A poisoned cache therefore places escape sequences
in front of the operator. Found and fixed in-gate.

This materially strengthens S-001. The original argument rested on **one** demonstrated
analogue (the `str`-subclass `__format__` injection in the #215 diff); there are now
**two**, and the second reaches the operator through a **data path** rather than through
model output — so the class is not confined to LLM-authored strings, and sanitising only
what the model writes would not have caught it. S-001 is now the best-evidenced unfixed
finding in this register.

Priority raised. Still **held** pending the principal (see handoff decision 14's
neighbouring question); the agent has been told not to act on it.

**Why it is not merely pre-existing.** The same class was demonstrated live in the #215 PR:
`score_variant` and `embed_sequence` interpolated the *caller's* object into the strings
returned to the agent, and a `str` subclass overriding `__format__` could inject arbitrary
text — proven with `\x1b[2J ATTACKER-CONTROLLED TEXT`. That was fixed by reporting the
validated value. The print path is the same shape with a different sink, so the class is
known-reachable in this codebase rather than theoretical.

**Fix shape.** Sanitise before display rather than at the source: strip or escape C0/C1
control characters (excluding `\n` and `\t`) from model-authored text at every print site,
in one helper so new call sites inherit it. Do not rely on the JSON write path — that
escapes on write to `discovery.json`, but the terminal print happens first and is separate.

**Test shape.** Feed a stubbed turn whose content carries `\x1b[2J` and an OSC title
sequence; assert what reaches stdout contains neither, and that ordinary text and newlines
survive unchanged.

---

## Method note carried from the public register

Mutation counts from the #152 gate and its re-gate are unverified (stale `__pycache__`
methodology). The fixes are not in doubt; the metric is. Re-earn the figure before it is
ever published. Full statement in the public register's Method notes.

---

## C-001 — three tracked sites pair an identifier with what it names

**Severity.** Constraint, **not security**. Raised via the constraint relayed in dispatch
#218; ruled in #220. No live reproduction (not a defect class with one). Disposition
2026-09-24.

**Status.** **Held.** Retroactivity is with the principal, recorded as handoff decision 14,
**with a recommendation against**.

**Where.** `aviary-biosim/science/esm_tool.py:161`, `science/run_discovery.py:61`,
`science/run_experiment.py:42`.

**What.** Each pairs an identifier with what it denotes. **The pairing is deliberately not
restated here** — a reader re-derives it from the code at those three locations. Recording
it descriptively is the thing the constraint forbids, and a register is the most durable
artifact in the system, so it is the worst place to do it.

**Held as ONE decision.** Editing any single site leaves the association standing in the
other two, so a partial fix buys nothing.

**Two carry consequences beyond wording:**

- `esm_tool.py:161` is the **agent-facing Tool schema** — verified: `Tool.from_function(fn)`
  at `science/biosim_env.py:115` derives the parameter description from that docstring, so
  editing it changes what the model is shown. That is a behaviour change to the environment,
  not a documentation tidy.
- `run_discovery.py:61` is the prompt the **published measurement run actually asked**. The
  remedy there is **ANNOTATE, never rewrite**: the historical prompt is evidence, and
  rewriting it makes the artifact and the code disagree about what was asked — converting a
  wording preference into a provenance defect, which is a worse fault than the one being
  corrected.

**Why it is recorded at all.** The constraint's value is prospective: stop accumulating the
association. This row exists so a future reader does not rediscover the three sites and
"tidy" them, and so the annotate-not-rewrite distinction survives outside dispatch prose —
which is where findings go to die, and the reason this register exists.
