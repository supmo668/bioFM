"""T6: the v0.5 lifecycle sweep passes the seed through to run_agentic_lifecycle.

``scripts/modal/app_v05.py`` imports ``modal`` at module top, so the loop body
lives in :mod:`perturb_eval.experiments.v05_sweep` where it can be tested.
"""

from __future__ import annotations

import numpy as np
import pytest

from perturb_eval.agentic_lifecycle.types import LifecycleRun
from perturb_eval.experiments.v05_sweep import lifecycle_record

_RECORD_KEYS = {
    "task_id",
    "steps",
    "final_msd_topk",
    "final_validator_agreement",
    "n_rounds",
    "n_agents",
    "backbone_used",
    # T8b provenance fields on LifecycleRun.
    "hvg_n_per_round",
    "hvg_n_forced_per_round",
    "hvg_mode",
    "n_params",
    # QG C15: (backbone, n_params) per round.
    "n_params_per_round",
    # Amendment 2: A2-2 per-round MSD, A2-3 applied config per round.
    "msd_per_round",
    "applied_config_per_round",
    # A2-5: the task's evaluation genes (shared with the trainer record).
    "eval_gene_idx",
    "n_eval_genes",
    "dataset",
    "seed",
    "wall_sec",
}


def _ds() -> dict:
    return {
        "X": np.zeros((4, 3)),
        "labels": np.array(["ctrl", "ctrl", "GENEA", "GENEA"]),
        "control_mask": np.array([True, True, False, False]),
        "target_gene_idx": {"GENEA": 1},
    }


class _StubRun:
    """Records the kwargs of each call and returns a minimal LifecycleRun."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def __call__(self, **kwargs) -> LifecycleRun:
        self.calls.append(kwargs)
        return LifecycleRun(
            task_id=kwargs["task_id"],
            steps=(),
            final_msd_topk=0.5,
            final_validator_agreement=0.9,
            n_rounds=1,
            n_agents=5,
            backbone_used="linear",
        )


def test_lifecycle_record_passes_seed_and_records_it() -> None:
    stub = _StubRun()
    pool = object()
    ds = _ds()
    rec = lifecycle_record(
        task="GENEA", dataset_name="adamson", ds=ds, seed=7, pool=pool, run_fn=stub
    )

    assert len(stub.calls) == 1
    call = stub.calls[0]
    assert call["seed"] == 7
    assert call["dataset"] == "adamson"  # QG C6: the lifecycle knows its dataset
    assert call["task_id"] == "GENEA"
    assert call["held_out"] == "GENEA"
    assert call["agent_pool"] is pool
    assert call["max_rounds"] == 3
    assert call["X"] is ds["X"]
    assert call["labels"] is ds["labels"]
    assert call["control_mask"] is ds["control_mask"]
    assert call["target_gene_idx"] is ds["target_gene_idx"]

    assert rec["seed"] == 7
    assert rec["dataset"] == "adamson"
    assert rec["task_id"] == "GENEA"
    assert set(rec) == _RECORD_KEYS
    assert rec["wall_sec"] >= 0.0


def test_lifecycle_record_forwards_extra_lifecycle_kwargs() -> None:
    stub = _StubRun()
    lifecycle_record(
        task="GENEA",
        dataset_name="adamson",
        ds=_ds(),
        seed=11,
        pool=object(),
        run_fn=stub,
        max_rounds=3,  # A2-2: the only accepted value (any other is refused)
        backbone_override="mlp",
    )
    assert stub.calls[0]["max_rounds"] == 3
    assert stub.calls[0]["backbone_override"] == "mlp"
    assert stub.calls[0]["seed"] == 11


def test_lifecycle_record_requires_seed() -> None:
    with pytest.raises(TypeError):
        lifecycle_record(  # type: ignore[call-arg]
            task="GENEA", dataset_name="adamson", ds=_ds(), pool=object(), run_fn=_StubRun()
        )


# ---------------------------------------------------------------- A2-8 / QG-1
class TestDeriveStatusReplay:
    """``derive_status`` marks a REPLAY when given the cache info (A2-8); the
    original signature (no cache info) is unchanged."""

    def _rows(self, *hits: bool) -> list[dict]:
        return [
            {
                "task_id": "T0",
                "steps": [
                    {"agent_name": "Architect", "source": "llm", "cache_hit": h} for h in hits
                ],
            }
        ]

    def test_signature_backward_compatible(self) -> None:
        from perturb_eval.experiments.v05_sweep import derive_status

        assert derive_status(self._rows(True), cost_usd=1.0, kill_usd=28.0) == "ok"

    def test_cache_hit_marks_replay(self) -> None:
        from perturb_eval.experiments.v05_sweep import derive_status

        assert (
            derive_status(
                self._rows(False, True), cost_usd=1.0, kill_usd=28.0, llm_cache_entries_at_start=0
            )
            == "replay"
        )

    def test_entries_at_start_marks_replay(self) -> None:
        from perturb_eval.experiments.v05_sweep import derive_status

        assert (
            derive_status(
                self._rows(False), cost_usd=1.0, kill_usd=28.0, llm_cache_entries_at_start=3
            )
            == "replay"
        )

    def test_clean_cache_stays_ok(self) -> None:
        from perturb_eval.experiments.v05_sweep import derive_status

        assert (
            derive_status(
                self._rows(False), cost_usd=1.0, kill_usd=28.0, llm_cache_entries_at_start=0
            )
            == "ok"
        )

    def test_fallback_and_stop_beat_replay(self) -> None:
        from perturb_eval.experiments.v05_sweep import derive_status

        fb = [{"task_id": "T0", "steps": [{"source": "fallback", "cache_hit": True}]}]
        assert (
            derive_status(fb, cost_usd=1.0, kill_usd=28.0, llm_cache_entries_at_start=3)
            == "failed_fallback"
        )
        assert (
            derive_status(
                self._rows(True),
                cost_usd=1.0,
                kill_usd=28.0,
                stop_reason="spend_stop",
                llm_cache_entries_at_start=0,
            )
            == "partial"
        )
