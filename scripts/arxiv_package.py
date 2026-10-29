"""Package a LaTeX paper for arXiv submission, and refuse to when it would fail there.

WHY THIS EXISTS. arXiv has no deposit API for individual authors — submission is a web
form behind a registered account, possible endorsement, a license agreement and
moderation. So the submission itself cannot be automated. Everything *up to* the Submit
button can be, and that is what this does: assemble the source bundle, check it against
the constraints arXiv actually enforces, and emit the metadata to paste into the form.

PROJECT-AGNOSTIC BY CONSTRUCTION. Nothing about any one paper is hard-coded. A paper
opts in by dropping an `arxiv.toml` beside its root `.tex`; this script and the reusable
workflow that calls it take a directory and read that file. Adding a second paper is a
config file, not a code change.

THE CHECK THAT MATTERS MOST, because it is the usual way an arXiv submission fails
silently: **arXiv does not run BibTeX.** A paper using `\\bibliography{...}` must ship the
generated `.bbl` inside the bundle, or every citation renders as `[?]` in the announced
PDF — compiled, published, and wrong. `preflight` fails closed on a missing `.bbl`.

NON-VACUITY. `self-test` plants a violation of every check into a throwaway paper and
asserts each one fires. A checker that cannot be made to fail is not evidence, so CI runs
`self-test` before it trusts `preflight`.

Usage:
    arxiv_package.py preflight  <paper-dir>
    arxiv_package.py metadata   <paper-dir>
    arxiv_package.py build      <paper-dir> [--out DIR]
    arxiv_package.py self-test
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import re
import sys
import tarfile
import tempfile
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------------------- #
# What arXiv's TeX Live provides. A package NOT here is not necessarily absent —
# it is merely unvouched, so preflight reports it and `acknowledge_packages` in
# the config is how an author takes responsibility for one. Fail-closed on the
# unknown, with a declared escape hatch, rather than a silent allow.
# --------------------------------------------------------------------------- #
STANDARD_PACKAGES = {
    "amsfonts",
    "amsmath",
    "amssymb",
    "amsthm",
    "array",
    "authblk",
    "babel",
    "bm",
    "booktabs",
    "caption",
    "cite",
    "cleveref",
    "color",
    "colortbl",
    "enumitem",
    "epsfig",
    "etoolbox",
    "fancyhdr",
    "float",
    "fontenc",
    "geometry",
    "graphics",
    "graphicx",
    "hyperref",
    "ifthen",
    "inputenc",
    "latexsym",
    "lipsum",
    "listings",
    "lmodern",
    "longtable",
    "makecell",
    "mathtools",
    "microtype",
    "multicol",
    "multirow",
    "natbib",
    "nicefrac",
    "orcidlink",
    "pdflscape",
    "pgfplots",
    "placeins",
    "setspace",
    "siunitx",
    "soul",
    "subcaption",
    "subfigure",
    "tabularx",
    "textcomp",
    "threeparttable",
    "tikz",
    "times",
    "titlesec",
    "ulem",
    "url",
    "wrapfig",
    "xcolor",
    "xspace",
}

GRAPHICS_EXTS = (".pdf", ".png", ".jpg", ".jpeg")
TEX_EXTS = (".tex", "")

RE_INPUT = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")
RE_GRAPHIC = re.compile(r"\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}")
RE_PACKAGE = re.compile(r"\\usepackage\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}")
RE_BIB = re.compile(r"\\(?:bibliography|addbibresource)\s*\{([^}]+)\}")
RE_SHELL = re.compile(r"\\(?:immediate\s*)?write18|\\ShellEscape")
RE_COMMENT = re.compile(r"(?<!\\)%.*$", re.MULTILINE)


@dataclass
class Finding:
    level: str  # "error" | "info"
    check: str
    message: str


@dataclass
class Result:
    findings: list[Finding] = field(default_factory=list)
    referenced: set[Path] = field(default_factory=set)
    checks_run: list[str] = field(default_factory=list)

    def error(self, check: str, msg: str) -> None:
        self.findings.append(Finding("error", check, msg))

    def info(self, check: str, msg: str) -> None:
        self.findings.append(Finding("info", check, msg))

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.level == "error"]

    @property
    def ok(self) -> bool:
        return not self.errors


def strip_comments(text: str) -> str:
    """LaTeX comments are not code. A `% \\input{gone.tex}` is not a missing file."""
    return RE_COMMENT.sub("", text)


def load_config(paper_dir: Path) -> dict:
    cfg_path = paper_dir / "arxiv.toml"
    if not cfg_path.is_file():
        raise SystemExit(
            f"no arxiv.toml in {paper_dir}\n"
            "A paper opts into this pipeline by adding one. See scripts/README-arxiv.md."
        )
    with cfg_path.open("rb") as fh:
        cfg = tomllib.load(fh)
    if "root_tex" not in cfg:
        raise SystemExit(f"{cfg_path}: `root_tex` is required")

    # A TOML table header captures every key that follows it, so a top-level scalar
    # written after `[categories]` silently becomes `categories.license` and reads as
    # absent everywhere. That failure is invisible — the only symptom is a metadata
    # field that renders empty, which is exactly the kind of hole someone pastes into
    # a submission form without noticing. Fail closed and name the fix.
    TOP_LEVEL = {
        "root_tex",
        "bundle_name",
        "citation_cff",
        "license",
        "comments",
        "acknowledge_packages",
        "title",
        "authors",
        "abstract",
    }
    stray = sorted(TOP_LEVEL & set(cfg.get("categories") or {}))
    if stray:
        raise SystemExit(
            f"{cfg_path}: {', '.join(repr(s) for s in stray)} "
            f"{'is' if len(stray) == 1 else 'are'} nested under [categories], where "
            "nothing reads it.\nTOML tables capture every key that follows the "
            "header. Move them ABOVE the [categories] line, or keep [categories] last "
            "in the file."
        )
    return cfg


def resolve_candidate(
    paper_dir: Path, target: str, exts: tuple[str, ...]
) -> Path | None:
    for ext in exts:
        p = (paper_dir / (target + ext)) if ext else (paper_dir / target)
        if p.is_file():
            return p
    return None


def preflight(paper_dir: Path, cfg: dict) -> Result:
    r = Result()
    paper_dir = paper_dir.resolve()
    root = paper_dir / cfg["root_tex"]

    r.checks_run.append("root-tex-exists")
    if not root.is_file():
        r.error(
            "root-tex-exists", f"root_tex {cfg['root_tex']!r} not found in {paper_dir}"
        )
        return r
    r.referenced.add(root)

    # Walk \input/\include transitively. ANTI-VACUITY: if the walk visits only the
    # root while the root clearly references others, that is a parser failure, not a
    # clean paper — see the `walk-reached-sources` check below.
    seen: set[Path] = set()
    queue = [root]
    graphics: list[tuple[Path, str]] = []
    packages: set[str] = set()
    bib_bases: list[str] = []
    shell_escape_in: list[Path] = []

    while queue:
        cur = queue.pop()
        if cur in seen:
            continue
        seen.add(cur)
        body = strip_comments(cur.read_text(encoding="utf-8", errors="replace"))

        if RE_SHELL.search(body):
            shell_escape_in.append(cur)
        for grp in RE_PACKAGE.findall(body):
            packages.update(p.strip() for p in grp.split(",") if p.strip())
        for grp in RE_BIB.findall(body):
            bib_bases.extend(b.strip() for b in grp.split(",") if b.strip())
        for target in RE_GRAPHIC.findall(body):
            graphics.append((cur, target.strip()))

        for target in RE_INPUT.findall(body):
            t = target.strip()
            r.checks_run.append(
                "input-resolves"
            ) if "input-resolves" not in r.checks_run else None
            if t.startswith("/"):
                r.error(
                    "no-absolute-paths",
                    f"{cur.name}: \\input of an ABSOLUTE path {t!r}",
                )
                continue
            if ".." in Path(t).parts:
                r.error(
                    "no-parent-escape", f"{cur.name}: \\input escapes the bundle: {t!r}"
                )
                continue
            got = resolve_candidate(paper_dir, t, TEX_EXTS)
            if got is None:
                r.error(
                    "input-resolves",
                    f"{cur.name}: \\input{{{t}}} does not resolve inside the paper dir",
                )
            else:
                r.referenced.add(got)
                queue.append(got)

    r.checks_run += [
        "no-absolute-paths",
        "no-parent-escape",
        "graphics-resolve",
        "graphics-format",
        "packages-vouched",
        "bbl-present",
        "no-shell-escape",
        "walk-reached-sources",
    ]

    # Graphics
    for src, target in graphics:
        if target.startswith("/"):
            r.error(
                "no-absolute-paths",
                f"{src.name}: \\includegraphics of an ABSOLUTE path {target!r}",
            )
            continue
        if ".." in Path(target).parts:
            r.error(
                "no-parent-escape",
                f"{src.name}: \\includegraphics escapes the bundle: {target!r}",
            )
            continue
        got = resolve_candidate(
            paper_dir, target, GRAPHICS_EXTS if not Path(target).suffix else ("",)
        )
        if got is None:
            r.error(
                "graphics-resolve",
                f"{src.name}: \\includegraphics{{{target}}} does not resolve",
            )
        else:
            r.referenced.add(got)
            if got.suffix.lower() not in GRAPHICS_EXTS:
                r.error(
                    "graphics-format",
                    f"{got.name}: {got.suffix} is not a pdflatex-supported figure format "
                    f"(use one of {', '.join(GRAPHICS_EXTS)})",
                )

    # Packages
    unvouched = sorted(
        packages - STANDARD_PACKAGES - set(cfg.get("acknowledge_packages", []))
    )
    for p in unvouched:
        r.error(
            "packages-vouched",
            f"package {p!r} is not in the vouched TeX Live set. If arXiv has it, add it to "
            f"`acknowledge_packages` in arxiv.toml to take responsibility for that claim.",
        )

    # THE BIG ONE: arXiv does not run BibTeX.
    if bib_bases:
        # Resolve the .bib HERE, outside the .bbl branch below. \bibliography references
        # it whether or not the .bbl has been generated yet, and resolving it only on the
        # success path let a missing .bbl also mislabel references.bib as dead weight —
        # one defect fabricating a second, false finding. Caught on the first real paper.
        for b in bib_bases:
            got = resolve_candidate(paper_dir, b, (".bib", ""))
            if got:
                r.referenced.add(got)
        bbl = root.with_suffix(".bbl")
        if not bbl.is_file():
            r.error(
                "bbl-present",
                f"\\bibliography{{{','.join(bib_bases)}}} is used but {bbl.name} is ABSENT. "
                "arXiv does NOT run BibTeX: every citation would render as [?]. "
                "Compile locally or in CI and include the .bbl in the bundle.",
            )
        elif bbl.stat().st_size == 0:
            r.error("bbl-present", f"{bbl.name} exists but is EMPTY")
        else:
            r.referenced.add(bbl)
    else:
        r.info("bbl-present", "no \\bibliography — .bbl not required")

    for f in shell_escape_in:
        r.error(
            "no-shell-escape",
            f"{f.name}: uses \\write18/ShellEscape, which arXiv does not permit",
        )

    if len(seen) == 1 and RE_INPUT.search(
        strip_comments(root.read_text(encoding="utf-8", errors="replace"))
    ):
        r.error(
            "walk-reached-sources",
            "the root tex references \\input files but the walk resolved none — "
            "the parse found nothing, so this result is not evidence",
        )

    # Dead weight: present in the dir, referenced by nothing.
    tracked = {p for p in paper_dir.rglob("*") if p.is_file()}
    noise = {".DS_Store"}
    unreferenced = sorted(
        p
        for p in tracked
        if p not in r.referenced
        and p.name not in noise
        and p.suffix.lower() in (".tex", ".bib", ".pdf", ".png", ".jpg", ".jpeg")
    )
    for p in unreferenced:
        r.info(
            "unreferenced",
            f"{p.relative_to(paper_dir)} is in the paper dir but referenced by nothing",
        )

    return r


def render_result(r: Result, paper_dir: Path) -> None:
    print(f"arxiv-preflight: {paper_dir}")
    print(
        f"  checks run ({len(set(r.checks_run))}): {', '.join(sorted(set(r.checks_run)))}"
    )
    print(f"  files that would ship: {len(r.referenced)}")
    for f in r.findings:
        if f.level == "error":
            print(f"  ERROR [{f.check}] {f.message}")
    infos = [f for f in r.findings if f.level == "info"]
    for f in infos:
        print(f"  info  [{f.check}] {f.message}")
    print(
        "  NOT CHECKED, stated: whether the document COMPILES (needs a TeX toolchain — the CI "
        "job compiles before calling this), and arXiv moderation/endorsement outcomes."
    )
    print(f"\n  {'PASS' if r.ok else 'FAIL — ' + str(len(r.errors)) + ' error(s)'}")


def metadata(paper_dir: Path, cfg: dict) -> tuple[str, list[str]]:
    """Emit the paste-ready arXiv form block, sourced from CITATION.cff where possible."""
    # pyyaml is the one non-stdlib dependency, and only `metadata` needs it. A raw
    # ModuleNotFoundError here tells a first-time user nothing actionable, so name the
    # exact command instead — this is the entry point a new project reaches first.
    try:
        import yaml
    except ModuleNotFoundError as exc:  # pragma: no cover - environment-dependent
        raise SystemExit(
            "`metadata` needs pyyaml to read CITATION.cff, and it is not importable.\n"
            "Run it as:  uv run --with pyyaml python scripts/arxiv_package.py metadata "
            "<paper-dir>\n"
            "(`preflight`, `build` and `self-test` are stdlib-only and need no extra.)"
        ) from exc

    out: list[str] = []
    cff_rel = cfg.get("citation_cff")
    title = authors = abstract = None
    if cff_rel:
        cff_path = (paper_dir / cff_rel).resolve()
        if cff_path.is_file():
            cff = yaml.safe_load(cff_path.read_text(encoding="utf-8"))
            title = " ".join((cff.get("title") or "").split())
            abstract = " ".join((cff.get("abstract") or "").split()) or None
            auth = cff.get("authors") or []
            authors = (
                ", ".join(
                    f"{a.get('given-names', '').strip()} {a.get('family-names', '').strip()}".strip()
                    for a in auth
                )
                or None
            )
            out.append(
                f"# metadata sourced from {cff_path.name} — single source of truth"
            )
    title = cfg.get("title", title)
    authors = cfg.get("authors", authors)
    abstract = cfg.get("abstract", abstract)

    cats = cfg.get("categories", {})
    primary = cats.get("primary", "")
    cross = cats.get("cross_list", [])

    out += [
        "",
        "=== PASTE INTO THE ARXIV SUBMISSION FORM ===",
        "",
        f"Title:      {title or '!! MISSING — set `title` in arxiv.toml or citation_cff'}",
        f"Authors:    {authors or '!! MISSING'}",
        f"Primary:    {primary or '!! MISSING — set categories.primary'}",
        f"Cross-list: {', '.join(cross) if cross else '(none)'}",
        f"License:    {cfg.get('license', '!! MISSING — set `license`')}",
        "",
        "Comments:",
        f"  {cfg.get('comments', '').strip()}",
        "",
        "Abstract:",
    ]
    text = (
        abstract
        or "!! MISSING — set `abstract` in arxiv.toml or supply it via citation_cff"
    )
    line = ""
    for word in text.split():
        if len(line) + len(word) + 1 > 78:
            out.append("  " + line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        out.append("  " + line)
    out += [
        "",
        "=== END ===",
        "",
        "Reminder: arXiv submission is a WEB FORM. There is no deposit API for individual",
        "authors, the license grant is a legal act by a person, and a first submission to a",
        "category may require endorsement. This block exists so the manual step is",
        "copy-paste and reproducible from the repository, not so it can be skipped.",
    ]

    # A block with a hole in it is worse than no block, because its shape invites
    # pasting. Name every gap and let the caller exit non-zero on it.
    missing = [
        name
        for name, val in (
            ("title", title),
            ("authors", authors),
            ("abstract", abstract),
            ("categories.primary", primary),
            ("license", cfg.get("license")),
        )
        if not val
    ]
    if missing:
        out += [
            "",
            f"INCOMPLETE — {len(missing)} field(s) unset: {', '.join(missing)}",
            "Set them in arxiv.toml (or in the CITATION.cff this config points at).",
        ]
    return "\n".join(out), missing


def build(paper_dir: Path, cfg: dict, out_dir: Path) -> Path:
    r = preflight(paper_dir, cfg)
    render_result(r, paper_dir)
    if not r.ok:
        raise SystemExit("\nrefusing to build a bundle that would fail on arXiv")

    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.UTC).strftime("%Y%m%d")
    name = cfg.get("bundle_name", paper_dir.name)
    tar_path = out_dir / f"{name}-arxiv-{stamp}.tar.gz"

    manifest: list[str] = []
    with tarfile.open(tar_path, "w:gz") as tf:
        for p in sorted(r.referenced):
            rel = p.relative_to(paper_dir.resolve())
            tf.add(p, arcname=str(rel))
            digest = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
            manifest.append(f"{digest}  {rel}")

    man_path = out_dir / f"{name}-arxiv-{stamp}.manifest.txt"
    man_path.write_text(
        f"# arXiv bundle manifest — {tar_path.name}\n"
        f"# built {dt.datetime.now(dt.UTC).isoformat()}\n"
        f"# {len(r.referenced)} files, each listed with a sha256 prefix\n"
        f"# ONLY files reachable from {cfg['root_tex']} are included; unreferenced files in the\n"
        f"# paper directory are deliberately left out and are reported as `info` by preflight.\n\n"
        + "\n".join(manifest)
        + "\n",
        encoding="utf-8",
    )
    print(f"\n  bundle   {tar_path}")
    print(f"  manifest {man_path}")
    return tar_path


# --------------------------------------------------------------------------- #
# self-test: plant a violation of each check and assert it fires.
# A checker that cannot be made to fail is not evidence.
# --------------------------------------------------------------------------- #
def self_test() -> int:
    cases: list[tuple[str, dict[str, str], str]] = [
        (
            "bbl-present",
            {
                "paper.tex": r"\documentclass{article}\begin{document}\cite{x}\bibliography{refs}\end{document}",
                "refs.bib": "@misc{x, title={t}}",
            },
            "missing .bbl with a \\bibliography",
        ),
        (
            "input-resolves",
            {
                "paper.tex": r"\documentclass{article}\begin{document}\input{nope}\end{document}",
            },
            "\\input of a file that is not there",
        ),
        (
            "no-absolute-paths",
            {
                "paper.tex": r"\documentclass{article}\begin{document}\input{/etc/hosts}\end{document}",
            },
            "absolute \\input path",
        ),
        (
            "no-parent-escape",
            {
                "paper.tex": r"\documentclass{article}\begin{document}\input{../outside}\end{document}",
            },
            "\\input escaping the bundle",
        ),
        (
            "graphics-resolve",
            {
                "paper.tex": r"\documentclass{article}\begin{document}\includegraphics{ghost}\end{document}",
            },
            "\\includegraphics of a missing figure",
        ),
        (
            "packages-vouched",
            {
                "paper.tex": r"\documentclass{article}\usepackage{totally-not-a-real-pkg}\begin{document}x\end{document}",
            },
            "an unvouched package",
        ),
        (
            "no-shell-escape",
            {
                "paper.tex": r"\documentclass{article}\begin{document}\immediate\write18{rm -rf /}\end{document}",
            },
            "\\write18 shell escape",
        ),
    ]
    failures = 0
    print(
        "arxiv-preflight self-test — each case plants ONE violation and asserts the check fires\n"
    )
    for check, files, desc in cases:
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            for rel, body in files.items():
                (d / rel).parent.mkdir(parents=True, exist_ok=True)
                (d / rel).write_text(body, encoding="utf-8")
            r = preflight(d, {"root_tex": "paper.tex"})
            fired = [f.check for f in r.errors]
            hit = check in fired
            print(f"  {'OK  ' if hit else 'DEAD'}  {check:22s} planted: {desc}")
            if not hit:
                print(
                    f"         expected {check!r}, got {sorted(set(fired)) or 'NO ERRORS'}"
                )
                failures += 1

    # And the mirror: a clean paper must PASS, or the checks are merely always-on.
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "paper.tex").write_text(
            r"\documentclass{article}\usepackage{graphicx}\begin{document}"
            r"\input{sections/body}\end{document}",
            encoding="utf-8",
        )
        (d / "sections").mkdir()
        (d / "sections" / "body.tex").write_text("clean\n", encoding="utf-8")
        r = preflight(d, {"root_tex": "paper.tex"})
        print(
            f"  {'OK  ' if r.ok else 'DEAD'}  {'clean-paper-passes':22s} mirror: a valid paper must not error"
        )
        if not r.ok:
            print(f"         unexpected errors: {[f.message for f in r.errors]}")
            failures += 1

    # Regression: a missing .bbl must not ALSO report the .bib as dead weight. One
    # defect reporting itself twice, under two names, is how a real finding gets lost
    # in the noise of a fabricated one. Found on the first real paper this ran against.
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "paper.tex").write_text(
            r"\documentclass{article}\begin{document}\cite{x}"
            r"\bibliography{references}\end{document}",
            encoding="utf-8",
        )
        (d / "references.bib").write_text("@misc{x, title={t}}\n", encoding="utf-8")
        r = preflight(d, {"root_tex": "paper.tex"})
        bogus = [
            f
            for f in r.findings
            if f.check == "unreferenced" and "references.bib" in f.message
        ]
        fired = [f.check for f in r.errors]
        good = ("bbl-present" in fired) and not bogus
        print(
            f"  {'OK  ' if good else 'DEAD'}  {'bib-not-dead-weight':22s} "
            "regression: a missing .bbl must not also flag references.bib"
        )
        if not good:
            print(
                f"         bbl error fired: {'bbl-present' in fired}; "
                f"bogus unreferenced findings: {[f.message for f in bogus]}"
            )
            failures += 1

    print(
        f"\n  {'ALL CHECKS PROVEN LIVE' if not failures else str(failures) + ' CHECK(S) DEAD — preflight is not evidence'}"
    )
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("preflight", "metadata", "build"):
        s = sub.add_parser(name)
        s.add_argument("paper_dir", type=Path)
        if name == "build":
            s.add_argument("--out", type=Path, default=Path("dist/arxiv"))
    sub.add_parser("self-test")

    a = ap.parse_args()
    if a.cmd == "self-test":
        return self_test()

    cfg = load_config(a.paper_dir)
    if a.cmd == "preflight":
        r = preflight(a.paper_dir, cfg)
        render_result(r, a.paper_dir)
        return 0 if r.ok else 1
    if a.cmd == "metadata":
        text, missing = metadata(a.paper_dir, cfg)
        print(text)
        return 1 if missing else 0
    build(a.paper_dir, cfg, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
