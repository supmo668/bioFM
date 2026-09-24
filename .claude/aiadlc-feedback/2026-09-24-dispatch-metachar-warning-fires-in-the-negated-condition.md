---
type: plugin-feedback
target: aiadlc plugin (bioFM) — tools/dispatch
plugin_version: 0.56.0
reporter: bioFM/matthew-mo/cto
date: 2026-09-24
scope: plugin / operating-system behavior — NOT repo/app work
---

# 🟠 `dispatch create`'s metacharacter warning is emitted exactly when there is no problem, and silent exactly when there is

**File:** `tools/dispatch`, lines 84–96 (the inline-body guard)
**Reported by:** `biofm/matthew-mo/aviary-biosim` in dispatch #208, self-caught.

## Symptom

An agent passed a dispatch body as a double-quoted shell argument. It contained a
backticked phrase. The caller's shell ran it as command substitution, printed
`command not found: import`, substituted empty — and **`dispatch create` reported ✓
with the sentence silently blanked.** The recipient (me) read a dispatch whose text
was not what the sender wrote: `"...a plain  then resolves by collection order."`

The sender caught it only by re-reading the written file afterwards rather than
trusting the ✓.

## Root cause — and the guard cannot fix itself

The tool's own comment is honest about this and worth quoting, because it names the
inversion precisely:

```
# Warn when an INLINE body still carries shell metacharacters. By the time we see
# the value the caller's shell has already run any substitution, so this cannot
# catch the dangerous case directly — what it catches is the AUTHORING HABIT that
# produces it (metachars surviving means they were quoted this time; next time
# they may not be). Advisory only: never blocks a send.
```

So the condition the guard tests — *metacharacters are still present in the received
value* — is **inversely correlated** with the fault:

| what happened | metachars in received value? | warning fires? | body correct? |
|---|---|---|---|
| properly quoted (heredoc / single quotes) | **yes** | **yes** | yes |
| substitution fired (double-quoted arg) | **no** — consumed by the shell | **no** | **NO** |

The warning is therefore emitted in the safe case and suppressed in the broken one.
As an authoring-habit nudge it is defensible and it did help me — I received it
earlier this session and switched to heredocs, which is why my own bodies survived.
As a guard against the failure it describes, it is structurally incapable, and its
presence makes silence feel meaningful when silence is precisely what the bad case
produces.

This is the same family as the ambient-state defects filed 2026-09-16/17 and
2026-09-20: **a check derives a correctness-relevant answer from something adjacent
to the thing it describes.** Here the adjacent thing is a proxy that is *anti*-correlated
with the fault, which is worse than an unreliable proxy.

## Why it matters beyond one sentence

The sender notes this is the third occurrence of one shape — the other two were
commit-message failures during the #152 gate: **a step reported success while the
content it was meant to carry was not what was written.** A dispatch is the only
channel between a coordinator and an agent; a send that succeeds with altered text
produces a ruling made on text nobody authored. In this instance the loss was one
clause and the sender caught it. The same mechanism can delete a negation.

## Suggested fixes, in order

1. **Make `--body-file` the documented path, and eventually the only one.**
   `--body-file` **already exists** — 15 references in `tools/dispatch` in both 0.56.0
   and 0.60.0, with `--body-file -` reading stdin, commented at line 320 as "read the
   body with ZERO shell interpolation". So this is not a feature request. Deprecating
   `--body` in favour of it removes the entire class instead of warning about it.
2. **Echo what was received.** On success, print the stored body's byte count and a
   short SHA256 prefix. A caller who knows they wrote 4,812 bytes can see 4,796 and
   look. This is the cheapest fix that works for callers who keep using `--body`.
3. **Reword the current warning so its silence is not read as assurance.** It should
   say that it cannot detect the dangerous case — that absence of the warning means
   nothing. Right now an agent who has seen the warning once reasonably infers that
   not seeing it means the body was fine.
4. Optionally, detect the *artifacts* of a failed substitution in the received body
   (e.g. a stray `command not found`, or a collapsed double space where a backticked
   span was) and flag for review. Weak and heuristic, but non-zero.

## Amendment (same day) — the real gap is DISCOVERY, not capability

Reported by the same agent in dispatch #212, and verified: **`dispatch create --help`
does not list `--body-file`.** Its usage line is

```
Usage: dispatch create --to <addr> --subject <text> --body <text> [--type <type>] ...
```

so the only safe path is invisible unless you read the source or happen to trip the
guard at line 98, whose error text does mention it. The agent reached "`--body-file`
does not exist" from `--help` alone — a reasonable inference from the documentation
as shipped.

**This is the cheapest and highest-value fix in this file: one line of usage string.**
It is a different ticket from item 1 and should not be bundled with it — "document the
flag you have" ships today, "deprecate the unsafe flag" needs a migration.

## Related shell trap, same session, worth its own note

The same agent reached its wrong conclusion partly through a second exit-status
inversion, which reproduces here:

```bash
grep -q "NO_SUCH_STRING" file | head -2   # exit 0 — SUCCESS
grep "NO_SUCH_STRING" file | head -2 || echo "not found"   # prints NOTHING
```

**A pipeline's exit status is the last command's**, so `| head` discards grep's
"no match" signal and any `||` fallback never fires. This is the same shape as the
metacharacter guard above — an instrument whose reassuring output is uncorrelated with
the thing it appears to report — and it is worth a line in the operator guidance
wherever `git grep && commit` is already warned about.

## Status

open. Locally mitigated by convention only: bodies go through a single-quoted
heredoc and `--body-file`, never a double-quoted `--body`. The receiving agent has
added the same rule to its `shell-gate-must-test-the-property-not-the-exit-code`
instinct.
