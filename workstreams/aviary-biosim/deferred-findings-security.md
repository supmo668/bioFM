# Deferred findings — security detail (private)

The public register at `aviary-biosim/docs/deferred-findings.md` carries security rows as
id + severity + "held". The detail lives here until the fix ships, then the full row moves
to the public register and this entry is deleted.

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
