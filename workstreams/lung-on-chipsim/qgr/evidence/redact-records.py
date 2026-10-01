"""Mechanically redact licensed-source tokens from audit records. Principal ruling #529/#530.

WHY THIS EXISTS. The pr-prep gate widened the artifact scan to the surface the principal ruled
publishable (`.claude/usr/**`) and it FAILED: dispatch records in this workstream's own audit trail
carry accession- and structure-shaped values, and the coordinator — reading the context with values
masked, which this agent may not do — found some of them paired with compound names. That is the
name-association prohibition, inside the audit trail of the workstream whose subject is that
prohibition. The principal ruled: redact, then publish.

WHY IT IS MECHANICAL. Redaction by hand, or driven by a hand-typed list of files, would be a claim
("I removed the values") with no check beneath it — the failure family this workstream has recorded
nine times. So:

  * the decision to redact a token is made by THE SAME PREDICATES THE SCAN USES, imported from
    `tests/shape_scan.py` (which imports production's detectors), never re-derived here. If the
    scanner would call a token unaccounted, this replaces it; if the scanner accounts for it, this
    leaves it alone. The two cannot drift, because there is one definition;
  * the file list is an ARGUMENT, never a constant. A list baked in here would go stale silently;
  * it is IDEMPOTENT: the placeholders match neither detector, so a second run changes nothing —
    asserted by a test rather than asserted in prose.

WHAT IT DOES NOT DO. It does not touch names, prose, or any other text — only the tokens the
detectors find. It does not decide WHICH files should be redacted; that is the principal's ruling
and the caller's argument list. It never prints a value: counts only, in the output and in the
footer it writes.

USAGE
    redact-records.py <path> [<path> ...] [--dry-run] [--allow]

`--dry-run` reports what would change and writes nothing. `--allow` is required to touch a path
outside `.claude/usr/**` or `workstreams/**/qgr/**`, because a redactor pointed at source code or at
the signed plan would silently damage artifacts whose bytes are hash-covered.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

#: evidence/ -> qgr/ -> lung-on-chipsim/ -> workstreams/ -> repo root. Derived, never hardcoded.
ROOT = Path(__file__).resolve().parents[4]
PROJ = ROOT / "projects/lung-on-chipsim"
sys.path.insert(0, str(PROJ))

from tests.shape_scan import (  # noqa: E402
    _DOCUMENTED_ACCESSION_PROBE,
    _INVENTED_BODY,
    _INVENTED_KEY,
    _STRUCTURE_RE,
    REAL_ACCESSION_RE,
)

ACCESSION_PLACEHOLDER = "<redacted:DB-accession>"
STRUCTURE_PLACEHOLDER = "<redacted:structure>"

#: Paths a redactor may touch without an explicit override.
SAFE_PREFIXES = (".claude/usr/", "workstreams/")


def _is_safe(rel: str) -> bool:
    if rel.startswith(".claude/usr/"):
        return True
    return rel.startswith("workstreams/") and "/qgr/" in rel


def plan(text: str) -> tuple[list[tuple[int, int, str]], int, int]:
    """Spans to replace, and the two counts. Uses the SCAN's OWN accounting, not a second opinion.

    A token the scanner ACCOUNTS FOR is a documented probe or a documented invented form: it denotes
    nothing and must survive redaction, or the records would lose the very examples that make them
    readable. A token the scanner reports as UNACCOUNTED is what the content rule is about.
    """
    spans: list[tuple[int, int, str]] = []
    acc_n = 0
    for m in REAL_ACCESSION_RE.finditer(text):
        if _DOCUMENTED_ACCESSION_PROBE.fullmatch(m.group()):
            continue  # accounted: the documented all-zeros probe
        spans.append((m.start(), m.end(), ACCESSION_PLACEHOLDER))
        acc_n += 1

    str_n = 0
    for m in _STRUCTURE_RE.finditer(text):
        token = m.group()
        if _INVENTED_KEY.fullmatch(token) or _INVENTED_BODY.fullmatch(token):
            continue  # accounted: a documented invented form
        spans.append((m.start(), m.end(), STRUCTURE_PLACEHOLDER))
        str_n += 1

    spans.sort(key=lambda s: s[0])
    return spans, acc_n, str_n


def redact(text: str) -> tuple[str, int, int]:
    spans, acc_n, str_n = plan(text)
    if not spans:
        return text, 0, 0
    out = []
    cursor = 0
    for start, end, placeholder in spans:
        if start < cursor:  # overlapping match: keep the first, never double-replace
            continue
        out.append(text[cursor:start])
        out.append(placeholder)
        cursor = end
    out.append(text[cursor:])
    return "".join(out), acc_n, str_n


def footer(acc_n: int, str_n: int) -> str:
    return (
        f"\n<!-- redacted {date.today().isoformat()} by redact-records.py: {acc_n} accession "
        f"tokens, {str_n} structure tokens replaced by typed placeholders; ruling #529/#530 "
        "(principal, AskUserQuestion) — record otherwise unchanged -->\n"
    )


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    dry = "--dry-run" in argv
    allow = "--allow" in argv
    if not args:
        print(__doc__)
        return 2

    changed = 0
    total_acc = total_str = 0
    for arg in args:
        path = Path(arg)
        if not path.is_absolute():
            path = ROOT / arg
        # A path OUTSIDE the repository is the most dangerous input, so it must be REFUSED, not
        # crash: relative_to() raises for it, and a traceback is not a refusal. Caught by
        # test_the_instrument_REFUSES_a_path_outside_the_audit_surface, which pointed at a tmp dir.
        try:
            rel = str(path.resolve().relative_to(ROOT))
        except ValueError:
            print(f'REFUSED (outside this repository): {path}')
            return 2

        if not _is_safe(rel) and not allow:
            print(f"REFUSED (outside .claude/usr/** and workstreams/**/qgr/**): {rel}")
            print("         pass --allow only if you mean it; a redactor pointed at source code or")
            print("         at the signed plan would damage hash-covered bytes silently.")
            return 2

        text = path.read_text(encoding="utf-8")
        new, acc_n, str_n = redact(text)
        if acc_n == 0 and str_n == 0:
            print(f"  unchanged  {rel}")
            continue
        new = new + footer(acc_n, str_n)
        total_acc += acc_n
        total_str += str_n
        changed += 1
        print(f"  REDACTED   {rel}  ({acc_n} accession, {str_n} structure)")
        if not dry:
            path.write_text(new, encoding="utf-8")

    print(
        f"\n{'would change' if dry else 'changed'}: {changed} file(s); "
        f"{total_acc} accession token(s), {total_str} structure token(s). No value printed, ever."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
