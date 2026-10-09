"""Fail when an HACP floor page has drifted from its Notion mirror.

The Notion HACP rows are the source of truth for human review (principal, 2026-10-03); the floor
copies under docs/hacp/<project>/ mirror them. A floor page edited after the sync date recorded in
its project's notion-map.json is drift: the two surfaces no longer say the same thing, and nobody
has claimed otherwise. This check turns that into a CI failure.

Usage:
    python scripts/hacp_sync_check.py docs/hacp/lung-on-chipsim [more project dirs...]

Rules, per project directory holding a notion-map.json:
- every *.md page in the directory has an entry in the map, and every entry's file exists;
- every entry carries a Notion page URL and a `synced` date (YYYY-MM-DD);
- the page's last commit date (git log -1, author date, UTC) is not later than its `synced` date.
  A page changed in the same commit that bumps `synced` passes; a later edit without a re-sync fails.
Files not under git (a fresh, uncommitted page) are reported, not failed: the sync has not had a
chance to run yet.
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import subprocess
import sys

_URL_PREFIX = "https://app.notion.com/p/"


def _last_commit_date(path: pathlib.Path) -> dt.date | None:
    out = subprocess.run(
        ["git", "log", "-1", "--format=%aI", "--", str(path)],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    if not out:
        return None
    return dt.datetime.fromisoformat(out).astimezone(dt.timezone.utc).date()


def check_project(project_dir: pathlib.Path) -> list[str]:
    problems: list[str] = []
    map_path = project_dir / "notion-map.json"
    if not map_path.is_file():
        return [f"{project_dir}: no notion-map.json"]
    entries = json.loads(map_path.read_text(encoding="utf-8")).get("pages", {})
    pages = {p.name for p in sorted(project_dir.glob("*.md"))}
    for name in sorted(pages - set(entries)):
        problems.append(f"{project_dir / name}: not in notion-map.json")
    for name, entry in sorted(entries.items()):
        page = project_dir / name
        if not page.is_file():
            problems.append(f"{page}: listed in notion-map.json but missing")
            continue
        url = str(entry.get("notion", ""))
        synced = str(entry.get("synced", ""))
        if not url.startswith(_URL_PREFIX):
            problems.append(f"{page}: notion url missing or not a Notion page url")
        try:
            synced_date = dt.date.fromisoformat(synced)
        except ValueError:
            problems.append(f"{page}: synced date missing or not YYYY-MM-DD")
            continue
        committed = _last_commit_date(page)
        if committed is None:
            print(f"note: {page} is not committed yet; sync pending")
            continue
        if committed > synced_date:
            problems.append(
                f"{page}: edited {committed} after its last Notion sync {synced_date}; re-mirror and bump synced"
            )
    return problems


def main(argv: list[str]) -> int:
    roots = [pathlib.Path(a) for a in argv[1:]] or [
        pathlib.Path("docs/hacp/lung-on-chipsim")
    ]
    problems: list[str] = []
    for root in roots:
        problems.extend(check_project(root))
    for p in problems:
        print(p)
    if problems:
        print(f"hacp-sync-check: {len(problems)} problem(s)", file=sys.stderr)
        return 1
    print("hacp-sync-check: every floor page matches its recorded Notion sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
