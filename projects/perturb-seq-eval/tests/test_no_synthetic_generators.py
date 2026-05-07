"""Repository-wide guardrail: no synthetic Perturb-seq generators.

The v0.5.0 paper makes a hard claim that every reported number comes from
real Perturb-seq cells (Adamson 2016 + Norman 2019, fetched from the
scPerturb Zenodo bundle). Reintroducing a synthetic-cell generator would
silently undermine that claim. This test fails fast if anyone re-adds:

  * a script named like ``simulate.py`` / ``make_synthetic*.py`` /
    ``generate_synth*.py`` under the project tree;
  * a ``DGP`` dict / ``data-generating process`` block at the top of any
    Python module, OR a function that returns synthetic Perturb-seq cells.

Test fixtures (small synthetic h5ad files written inside ``tmp_path``
during a unit test) are explicitly allowed: they live under ``tests/``
and never leave the test scope.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Paths that are allowed to use the words "synthetic" or "simulate" because
# they are this guardrail or because they document the prohibition.
_ALLOWED = {
    "tests/test_no_synthetic_generators.py",  # this file
    "tests/test_norman_loader.py",            # writes a fixture h5ad
    "tests/test_adamson_combined.py",         # writes a fixture h5ad
    # Paper sections may mention "synthetic" only in the negative
    # (e.g. "no synthetic data is generated"). The paper test below
    # checks that explicitly.
}

_FORBIDDEN_FILENAMES = (
    re.compile(r"^simulate(\.py|_.*\.py)$"),
    re.compile(r"^make_synthetic(\.py|.*\.py)$"),
    re.compile(r"^generate_synth.*\.py$"),
    re.compile(r"^.*synthetic_data.*\.py$"),
)

# Tokens that signal a real-data-violating generator. The combination of
# ``DGP`` (data-generating process) plus ``default_rng`` plus a
# perturb-seq-flavoured term is the giveaway.
_GENERATOR_TRIPLE = (
    re.compile(r"\bDGP\b|data[- ]generating[- ]process", re.IGNORECASE),
    re.compile(r"default_rng\(", re.IGNORECASE),
    re.compile(r"perturbation|perturb[- ]seq|cell|gene", re.IGNORECASE),
)


def _project_python_files() -> list[Path]:
    """All .py files under src/, scripts/, paper/ — skip tests + venvs."""
    roots = [
        PROJECT_ROOT / "src",
        PROJECT_ROOT / "scripts",
        PROJECT_ROOT / "paper",
    ]
    out: list[Path] = []
    for r in roots:
        if not r.exists():
            continue
        for p in r.rglob("*.py"):
            if any(part in {"__pycache__", ".pytest_cache", ".venv", "venv"} for part in p.parts):
                continue
            out.append(p)
    return out


class TestNoSyntheticGeneratorFiles:
    def test_no_simulate_or_make_synthetic_filenames(self) -> None:
        offenders: list[str] = []
        for p in _project_python_files():
            name = p.name
            for pat in _FORBIDDEN_FILENAMES:
                if pat.match(name):
                    offenders.append(str(p.relative_to(PROJECT_ROOT)))
                    break
        assert not offenders, (
            "Synthetic-data generator files reintroduced — v0.5.0 paper claims "
            "no synthetic Perturb-seq generation. Remove these files:\n  "
            + "\n  ".join(offenders)
        )


class TestNoSyntheticGeneratorPatterns:
    def test_no_dgp_plus_perturb_generator_triple(self) -> None:
        """Fail if any single .py file under src/, scripts/, paper/
        contains all three of: a DGP/data-generating-process token,
        a numpy default_rng() call, and a perturb-seq vocabulary token.
        That combination is the signature of a synthetic-cell generator.
        """
        offenders: list[tuple[str, str]] = []
        for p in _project_python_files():
            rel = str(p.relative_to(PROJECT_ROOT))
            if rel in _ALLOWED:
                continue
            try:
                src = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if all(pat.search(src) for pat in _GENERATOR_TRIPLE):
                offenders.append((rel, "DGP+default_rng+perturb"))
        assert not offenders, (
            "Detected synthetic-cell generator pattern in:\n  "
            + "\n  ".join(f"{f}: {why}" for f, why in offenders)
            + "\nv0.5.0 paper requires real-data-only — remove or rewrite."
        )


class TestPaperTexNoSyntheticHeadlineClaim:
    """The paper.tex must NOT advertise a synthetic-data result anywhere
    that a casual reader would interpret as a headline claim."""

    @pytest.fixture
    def paper_tex(self) -> str:
        path = PROJECT_ROOT / "paper" / "paper.tex"
        if not path.exists():
            pytest.skip("paper.tex not present")
        return path.read_text(encoding="utf-8")

    def test_no_300_synthetic_tasks_claim(self, paper_tex: str) -> None:
        # The v0.4.1 abstract said "Across 300 synthetic tasks ...".
        forbidden = re.compile(r"\b300\s+synthetic\s+tasks?\b", re.IGNORECASE)
        assert not forbidden.search(paper_tex), (
            "paper.tex still contains the v0.4.1 '300 synthetic tasks' headline."
        )

    def test_no_all_experiments_synthetic_claim(self, paper_tex: str) -> None:
        forbidden = re.compile(
            r"all\s+(reported\s+)?experiments\s+are\s+synthetic", re.IGNORECASE
        )
        assert not forbidden.search(paper_tex), (
            "paper.tex still claims experiments are synthetic."
        )

    def test_simulate_py_not_referenced_as_pipeline(self, paper_tex: str) -> None:
        """Old reproducibility section pointed at simulate.py; new section
        points at scripts/modal/app_v05.py. This catches accidental revert."""
        forbidden = re.compile(
            r"paper/experiments/simulate\\?\.py", re.IGNORECASE
        )
        assert not forbidden.search(paper_tex), (
            "paper.tex still references the deleted paper/experiments/simulate.py."
        )

    def test_dgp_only_appears_in_retraction_context(self, paper_tex: str) -> None:
        """The acronym DGP may legitimately appear in a retraction sentence
        ('synthetic DGP retracted') but not as a claim about current results."""
        # Find every line containing 'DGP'.
        bad_lines = []
        for i, line in enumerate(paper_tex.splitlines(), start=1):
            if re.search(r"\bDGP\b", line):
                # OK if line is a comment, or contains "retract", "no ",
                # "without", or "Synthetic DGP" in a section title that's
                # been deleted (now wrapped in a comment).
                stripped = line.lstrip()
                if stripped.startswith("%"):
                    continue
                lower = line.lower()
                if any(k in lower for k in ("retract", "no synthetic", "no dgp",
                                            "without", "deleted", "v0.4.1")):
                    continue
                bad_lines.append((i, line.strip()))
        assert not bad_lines, (
            "paper.tex makes a positive DGP claim — synthetic results are forbidden:\n  "
            + "\n  ".join(f"L{i}: {ln}" for i, ln in bad_lines)
        )
