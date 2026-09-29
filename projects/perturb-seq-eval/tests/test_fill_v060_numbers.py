"""The manuscript's result values come ONLY from the committed v0.6.0 artifacts (CTO #491)."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "paper" / "sections" / "generated_numbers.tex"
TEX_INPUTS = [
    ROOT / "paper" / "paper.tex",
    ROOT / "paper" / "sections" / "results.tex",
    ROOT / "paper" / "sections" / "experimental_setup.tex",
    ROOT / "paper" / "sections" / "corrections.tex",
]
# Pre-registered constants and design facts that may appear as literals (never sweep results).
ALLOWED_LITERALS = {
    "0.20",
    "0.30",
    "0.5",
    "0.4",
    "0.02",
    "0.3",
    "2.35",
    "4.71",
    "5.84",
    "0.0475",
    "1.32",
    "1.07",
    "0.92",
    "0.35",
    "0.25",
    "1.0",
    "2.1",
    "0.1",
}


def _macros() -> dict[str, str]:
    return dict(
        re.findall(r"\\newcommand\{\\(res[A-Za-z]+)\}\{(.*)\}$", GEN.read_text(), flags=re.M)
    )


def test_generated_file_is_fresh():
    r = subprocess.run(
        [sys.executable, "scripts/paper/fill_v060_numbers.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr + r.stdout


def test_macro_values_match_the_artifacts():
    s = json.loads((ROOT / "artifacts/v0.6.0/summary.json").read_text())["preregistered"]
    p = json.loads((ROOT / "artifacts/v0.6.0/provenance.json").read_text())
    m = _macros()
    assert (
        m["resHOneMedian"] == f"{s['H1']['value']:.3f}"
        and m["resHTwoMedian"] == f"{s['H2']['value']:.3f}"
    )
    assert (
        m["resHThreeEntropy"] == f"{s['H3']['value']:.3f}"
        and m["resHFiveRho"] == f"{s['H5']['value']:.3f}"
    )
    six = {(r["dataset"], r["component"]): r for r in s["H4"]["all_six"]}
    assert m["resHFourAdaAceRho"] == f"{six[('adamson_full', 'ace_norm')]['rho']:.3f}"
    assert m["resHFourNorTdiRho"] == f"{six[('norman', 'tdi_lifecycle')]['rho']:.3f}"
    assert (
        m["resSpendTotal"] == f"{p['cost_usd_actual']:.2f}" and m["resGitSha"] == p["git_sha"][:7]
    )
    assert m["resHFiveVerdict"] == r"\textbf{FAIL}" and m["resHFourVerdict"] == r"\textbf{PASS}"
    assert m["resNFallback"] == "0" and m["resCacheHits"] == "0" and m["resServedMismatch"] == "0"


def test_no_pending_placeholders_remain():
    for f in TEX_INPUTS:
        assert "\\pending{" not in f.read_text(), f.name


def test_every_result_macro_used_is_defined():
    defined = set(_macros())
    for f in TEX_INPUTS:
        used = set(re.findall(r"\\(res[A-Za-z]+)", f.read_text()))
        missing = used - defined
        assert not missing, (f.name, sorted(missing))


@pytest.mark.parametrize("rel", ["sections/results.tex", "sections/experimental_setup.tex"])
def test_no_hand_typed_result_numbers(rel):
    """Any decimal literal in the result/setup prose must be a pre-registered constant, not a sweep value."""
    text = (ROOT / "paper" / rel).read_text()
    text = re.sub(r"(?<!\\)%.*", "", text)  # comments
    text = re.sub(r"p\{[\d.]+\\linewidth\}", "", text)  # tabular column widths
    text = re.sub(r"(Haiku|Sonnet)\s*\d\.\d", "", text)  # model family versions
    literals = set(re.findall(r"(?<![\w\\.])\d+\.\d+(?!\.\d)", text))
    stray = literals - ALLOWED_LITERALS
    assert not stray, sorted(stray)


def test_braces_balanced_in_generated_and_results():
    for f in [
        GEN,
        ROOT / "paper/sections/results.tex",
        ROOT / "paper/sections/experimental_setup.tex",
    ]:
        t = re.sub(r"(?<!\\)%.*", "", f.read_text())
        assert t.count("{") == t.count("}"), f.name
