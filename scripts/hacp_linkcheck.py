"""Check that every relative link in the HACP floor pages resolves to a file.

HACP floor copies are the local source that Notion Section rows mirror. A relative link or a
`Local path` that points at a file which does not exist is a claim that looks true and is not,
so this script fails CI on any dangling relative link.

Usage:
    python scripts/hacp_linkcheck.py docs/hacp [more roots...]

Rules:
- Only relative links are checked. Anything with a scheme (`https:`, `mailto:`), a bare
  fragment (`#section`), or an absolute path is skipped.
- Links inside fenced code blocks are ignored.
- A fragment suffix (`file.md#heading`) is stripped before resolving.
- Exit 0 when every link resolves; exit 1 with one line per missing target otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_FENCE = re.compile(r"^\s*(```|~~~)")


def _relative_links(text: str) -> list[str]:
    """Return the link targets in `text`, skipping fenced code blocks."""
    targets: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if _FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in _LINK.finditer(line):
            target = match.group(1)
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue  # scheme: http, https, mailto, notion, ...
            if target.startswith(("#", "/")):
                continue  # in-page fragment or absolute path
            targets.append(target)
    return targets


def check(roots: list[Path]) -> list[tuple[Path, str, Path]]:
    """Return (source file, link text, resolved path) for every link that does not exist."""
    missing: list[tuple[Path, str, Path]] = []
    for root in roots:
        files = [root] if root.is_file() else sorted(root.rglob("*.md"))
        for md in files:
            for target in _relative_links(md.read_text(encoding="utf-8")):
                bare = target.split("#", 1)[0]
                if not bare:
                    continue
                resolved = (md.parent / bare).resolve()
                if not resolved.exists():
                    missing.append((md, target, resolved))
    return missing


def main(argv: list[str]) -> int:
    roots = [Path(a) for a in argv[1:]] or [Path("docs/hacp")]
    for root in roots:
        if not root.exists():
            print(f"hacp-linkcheck: root does not exist: {root}", file=sys.stderr)
            return 2
    missing = check(roots)
    for md, target, resolved in missing:
        print(f"{md}: dangling link `{target}` -> {resolved}")
    if missing:
        print(f"hacp-linkcheck: {len(missing)} dangling link(s)", file=sys.stderr)
        return 1
    print("hacp-linkcheck: every relative link resolves")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
