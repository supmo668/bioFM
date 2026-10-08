"""Render the deposit description from the manuscript abstract (CTO #577 (a)).

The description deposited with a DOI is the manuscript's abstract, rendered to plain text
with every ``\\res...`` macro replaced by its generated value
(``paper/sections/generated_numbers.tex``). No number is typed by hand. The rendered text is
written into ``publish.yml`` (``description``) and ``CITATION.cff`` (``abstract``);
``--check`` fails if either differs from a fresh render.

    .venv/bin/python scripts/paper/render_publish_description.py [--check]
"""

from __future__ import annotations

import argparse
import re
import sys
import textwrap
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PAPER = PROJECT_ROOT / "paper" / "paper.tex"
GEN = PROJECT_ROOT / "paper" / "sections" / "generated_numbers.tex"
PUBLISH = PROJECT_ROOT / "publish.yml"
CITATION = PROJECT_ROOT / "CITATION.cff"
MARK = "# GENERATED from paper/paper.tex's abstract by scripts/paper/render_publish_description.py -- do not edit by hand."


def macros() -> dict[str, str]:
    raw = dict(
        re.findall(r"^\\newcommand\{\\(res[A-Za-z]+)\}\{(.*)\}$", GEN.read_text(), flags=re.M)
    )
    return {k: _value(v) for k, v in raw.items()}


def _value(v: str) -> str:
    v = re.sub(r"\\ensuremath\{-(.*)\}", lambda x: "\u2212" + x.group(1), v)
    v = re.sub(r"\\textbf\{(.*)\}", r"\1", v)
    return v.replace("\\,", ",").replace("\\_", "_").replace("\\textemdash", "\u2014")


def _math(m: re.Match) -> str:
    s = m.group(1)
    s = s.replace("\\Delta ", "\u0394").replace("\\Delta", "\u0394").replace("\\rho", "\u03c1")
    s = re.sub(r"\s*=\s*", " = ", s)
    s = re.sub(r"^\s*>\s*", "> ", s)
    return s.strip()


def render() -> str:
    tex = PAPER.read_text()
    body = tex[
        tex.index("\\begin{abstract}") + len("\\begin{abstract}") : tex.index("\\end{abstract}")
    ]
    m = macros()
    body = re.sub(r"(?<!\\)%.*", "", body)
    body = re.sub(r"~?\\citep?\{[^}]*\}", "", body)
    body = re.sub(r"\\textsc\{([^}]*)\}", r"\1", body)
    body = re.sub(r"\\(res[A-Z][A-Za-z]*)(\{\})?", lambda x: m[x.group(1)], body)
    body = re.sub(r"\$([^$]*)\$", _math, body)
    body = body.replace("---", "\u2014").replace("--", "\u2013")
    body = re.sub(r"\s+", " ", body).strip()
    body = re.sub(r"\(\s+", "(", body)
    body = re.sub(r"\s+([,.;)])", r"\1", body)
    leftover = re.findall(r"[\\${}~]", body)
    if leftover:
        raise ValueError(f"unconverted LaTeX left in the description: {sorted(set(leftover))}")
    return body


def _block(text: str, indent: str) -> list[str]:
    return [
        indent + line
        for line in textwrap.wrap(text, width=76, break_on_hyphens=False, break_long_words=False)
    ]


def _replace_block(lines: list[str], key: str, text: str, indent: str, head: str) -> list[str]:
    i = next(n for n, line in enumerate(lines) if re.match(rf"^{key}:", line))
    j = i + 1
    while j < len(lines) and (lines[j].startswith(" ") or lines[j] == ""):
        j += 1
    while j > i + 1 and lines[j - 1] == "":
        j -= 1
    k = i
    while k > 0 and lines[k - 1].startswith("#"):
        k -= 1  # drop the comment block directly above the key (rewritten below)
    return lines[:k] + [MARK, f"{key}: {head}"] + _block(text, indent) + lines[j:]


def build_files() -> dict[Path, str]:
    text = render()
    out: dict[Path, str] = {}
    pub = PUBLISH.read_text().splitlines()
    out[PUBLISH] = "\n".join(_replace_block(pub, "description", text, "  ", "|")) + "\n"
    cit = CITATION.read_text().splitlines()
    out[CITATION] = "\n".join(_replace_block(cit, "abstract", text, "  ", ">-")) + "\n"
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    files = build_files()
    stale = [p for p, t in files.items() if p.read_text() != t]
    if a.check:
        for p in stale:
            print(
                f"{p.name} description is stale: run render_publish_description.py", file=sys.stderr
            )
        if not stale:
            print("publish.yml and CITATION.cff descriptions match the manuscript abstract")
        return 1 if stale else 0
    for p, t in files.items():
        p.write_text(t)
    print(f"wrote {', '.join(p.name for p in files)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
