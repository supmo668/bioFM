---
type: plugin-feedback
target: airdlc plugin (tools/handoff)
plugin_version: 0.82.0
reporter: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-30
scope: plugin / operating-system behavior — NOT repo/app work
---

# Handoff frontmatter is never parsed, so this agent's has never been valid YAML

## 🟠 1. `tools/handoff` validates the required SECTION but never parses the frontmatter it demands

**File:** `tools/handoff:242-262` (the section check) · `tools/handoff:313-315` (the instruction)

**Symptom.** `lung-on-chipsim`'s handoff frontmatter has **never** parsed as YAML. Two
independent causes, both invisible:

```
lint: `uv run ruff format --check .` clean AND `uv run ruff check .` clean — TWO commands
      ^ a backtick cannot start a plain scalar → yaml.scanner.ScannerError on the WHOLE block

suite_configured: 867 passed / 4 skipped / 0 failed   # `uv run pytest -q`
                                                      ^ an inline " #" silently TRUNCATES
```

So a strict consumer throws on the entire block, and a lenient one reads a **truncated**
figure — `suite_configured` resolves to `867 passed / 4 skipped / 0 failed` with the command
that produced it discarded. Nobody noticed in either direction, for weeks, because **nothing
asserted the parse.**

**Root cause (measured, not guessed).** The tool already has the right hook location and
simply does not use it for this:

```
$ grep -cE 'python|yaml\.safe_load' tools/handoff
0
$ grep -n 'Principal Decisions Needed' tools/handoff
259:    if echo "$normalized" | grep -qxE '## Principal Decisions Needed'; then
262:    echo "WARNING: handoff missing required '## Principal Decisions Needed' section."
```

The handoff is written by the **agent**, prompted by the message at line 315 ("Use `type:` …
in YAML frontmatter", "include `agent:` … in YAML frontmatter"). The tool therefore *requires*
YAML, *checks a markdown section*, and *never checks the YAML*. A requirement with no
corresponding assertion is a convention, not a contract.

**Fix.** Beside the existing section check, assert the parse. Smallest viable form:

```bash
# Detect handoff frontmatter that does not parse as YAML.
if python3 - "$HANDOFF_PATH" <<'PY'
import pathlib, sys
try:
    import yaml
except ImportError:
    sys.exit(2)                      # checker absent — report, never pass silently
parts = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").split("---\n")
sys.exit(0 if len(parts) >= 3 and isinstance(yaml.safe_load(parts[1]), dict) else 1)
PY
then :; else
  case $? in
    2) echo "WARNING: cannot verify handoff frontmatter — pyyaml unavailable. UNKNOWN, not ok." ;;
    *) echo "WARNING: handoff frontmatter does not parse as YAML. A leading backtick cannot start a plain scalar, and an inline ' #' silently TRUNCATES the value — quote it: key: \"...\"" ;;
  esac
fi
```

**Note the distinct exit 2.** A missing `pyyaml` must report **UNKNOWN**, not success — an
absent checker reading as a pass is the same defect one layer up, and this repo has a standing
rule about it (`reference`: the error path of a discovery function is part of the check).

**Effect.** The frontmatter contract becomes enforced rather than merely stated, and the class
of silent truncation above becomes impossible to introduce unnoticed. Cheap: one check, at a
location that already exists.

**Status:** open

## Context — a related finding, already escalated by the CTO, NOT re-filed here

The same investigation found that **every handoff on this machine is on zero refs**:
`.gitignore:52` (`.claude/usr/*/*/*`) ignores handoffs while `.gitignore:53`
(`!.claude/usr/*/*/dispatches/`) explicitly un-ignores dispatch payloads beside them. The
asymmetry is **deliberate**, not an oversight — so the fix is not "track it" (this is a PUBLIC
repo and handoffs carry session state, absolute paths and internal reasoning) but either a
private durable location or a redaction contract.

That is a principal + framework decision and **the CTO has already escalated it and is filing
its own framework feedback** (dispatch #790). Recorded here only so a reader of finding 1 knows
the durability question is live and is not duplicated by this file.
