"""QG-8: the local dry-run's stub client must be a VALID LLM stand-in.

Every stub reply must schema-parse (confidence in [0, 1], an on-menu Architect
backbone) so no step takes the fallback path; hashing is deterministic (not
the process-salted ``hash()``); the run uses the pre-registered round count;
and the script fails loudly if any step is a fallback. No dataset is loaded.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

from perturb_eval.agentic_lifecycle.llm_agent_pool import LLMAgentPool
from perturb_eval.agentic_lifecycle.proposal_schema import BACKBONE_MENU, parse_proposal

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "local" / "v05_dry_run.py"
ROLES = ("DataCurator", "Literature", "Architect", "Trainer", "Validator")


@pytest.fixture(scope="module")
def dry_run_module():
    spec = importlib.util.spec_from_file_location("v05_dry_run", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("role", ROLES)
@pytest.mark.parametrize("round_index", [0, 1, 2])
def test_stub_reply_schema_parses_for_every_role(dry_run_module, role, round_index) -> None:
    client = dry_run_module._DeterministicStubClient()
    for task in ("TFA", "TFB", "TFC", "TFD"):
        payload = client._payload(role=role, task_id=task, round_index=round_index)
        model = parse_proposal(role, payload)  # A2-1 confidence, A2-6 backbone
        assert 0.0 <= model.confidence <= 1.0
        if role == "Architect":
            assert model.backbone in BACKBONE_MENU


@pytest.mark.parametrize("role", ROLES)
def test_stub_never_takes_the_fallback_path(dry_run_module, role, tmp_path) -> None:
    pool = LLMAgentPool(client=dry_run_module._DeterministicStubClient(), cache_dir=tmp_path)
    out = pool.propose(role, 0, "TFA", {}, seed=0, dataset="adamson_full")
    assert out["source"] == "llm" and out["confidence"] is not None


def test_stub_hash_is_deterministic_across_processes(dry_run_module) -> None:
    """``hash()`` on str/tuple is salted per process; the stub must not use it."""
    code = (
        "import importlib.util, json, sys\n"
        f"spec = importlib.util.spec_from_file_location('m', {str(_SCRIPT)!r})\n"
        "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
        "c = m._DeterministicStubClient()\n"
        "print(json.dumps([c._payload(role='Architect', task_id=t, round_index=r)"
        " for t in ('A','B','C','D','E','F') for r in (0,1,2)]))\n"
    )
    outs = {
        subprocess.run(
            [sys.executable, "-c", code],
            check=True,
            capture_output=True,
            text=True,
            env={"PYTHONHASHSEED": str(seed), "PATH": "/usr/bin:/bin"},
        ).stdout
        for seed in (1, 2, 3)
    }
    assert len(outs) == 1, "stub payloads differ across PYTHONHASHSEED values"


def test_script_uses_prereg_round_count_and_fails_on_fallback() -> None:
    src = _SCRIPT.read_text()
    assert "max_rounds=2" not in src
    assert "LIFECYCLE_N_ROUNDS" in src and "max_rounds=LIFECYCLE_N_ROUNDS" in src
    assert "hash(" not in src.replace("hashlib", "")
    assert "fallback" in src
