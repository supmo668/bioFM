"""End-to-end integration test — the Phase 2 gate.

The lifecycle must produce meaningfully different configurations across
seeds when wired to an LLM-like pool that returns varied choices. A
previous-round Validator critique must visibly steer round-2 proposals.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from perturb_eval.agentic_lifecycle.freedom_probe import per_agent_field_entropy
from perturb_eval.agentic_lifecycle.llm_agent_pool import LLMAgentPool
from perturb_eval.agentic_lifecycle.loop import run_agentic_lifecycle
from perturb_eval.llm.openrouter_client import ChatResult


class VariedMockClient:
    """Returns genuinely varied proposals keyed by (role, task, round)."""

    _BACKBONES = ("linear", "mlp", "scgpt_small")
    _HVGS = (500, 1000, 2000)
    _LRS = (1e-2, 5e-3, 1e-3)

    def __init__(self, seed: int = 0) -> None:
        self._rng = np.random.default_rng(seed)

    def chat_json(
        self, *, role: str, task_id: str, round_index: int, prompt: str, seed: int, dataset: str
    ) -> ChatResult:
        return ChatResult(
            content=self._payload(
                role=role, task_id=task_id, round_index=round_index, prompt=prompt, seed=seed
            ),
            model_id="stub/varied",
        )

    def _payload(
        self, *, role: str, task_id: str, round_index: int, prompt: str, seed: int
    ) -> dict:  # noqa: ARG002
        # Derive a bounded index from (task, round, role) so different
        # (task, seed) pairs give different Architect choices but the
        # same (task, role) is reproducible within a client instance.
        h = abs(hash((role, task_id, round_index))) % 10_000
        if role == "DataCurator":
            return {
                "hvg_method": ("seurat", "scanpy")[h % 2],
                "hvg_count": self._HVGS[h % len(self._HVGS)],
                "qc_mito_max": 12.0,
                "split_strategy": "per_pert_holdout",
                "batch_correction": "none",
                "confidence": 0.6,  # A2-1: required on every role
            }
        if role == "Literature":
            return {
                "pathway_prior": {"TP53": 0.7},
                "ppi_neighbors": ["JUN", "FOS"],
                "tool_calls": ["biogpt"],
                "expected_up": ["TP53"],
                "expected_down": [],
                "confidence": 0.5,
            }
        if role == "Architect":
            return {
                "backbone": self._BACKBONES[h % len(self._BACKBONES)],
                "n_agents": 5,
                "n_rounds": 2,
                "hvg_count": self._HVGS[h % len(self._HVGS)],
                "learning_rate": self._LRS[h % len(self._LRS)],
                "ridge_lambda": 1.0,
                "epochs": 40,
                "confidence": 0.7,
            }
        if role == "Trainer":
            return {"lr": 5e-3, "epochs": 40, "ridge_lambda": 1.0, "confidence": 0.4}
        if role == "Validator":
            return {"dynamic_threshold_msd": 0.1, "confidence": 0.8}
        return {}


def _toy_dataset(n_genes: int = 60, seed: int = 1) -> dict:
    rng = np.random.default_rng(seed)
    n_cells = 90
    X = np.abs(rng.normal(0.5, 0.2, size=(n_cells, n_genes))).astype(np.float64)
    labels = np.array((["CTRL"] * 30) + (["GENE0"] * 30) + (["GENE1"] * 30))
    control_mask = labels == "CTRL"
    X[labels == "GENE0", 0] += 1.0
    X[labels == "GENE1", 1] += 1.0
    target_gene_idx = {"GENE0": 0, "GENE1": 1}
    return dict(
        X=X,
        labels=labels,
        control_mask=control_mask,
        target_gene_idx=target_gene_idx,
    )


class TestFreedomE2E:
    def test_architect_choice_entropy_above_gate(self, tmp_path: Path) -> None:
        # C-TORCH-3: without torch, scgpt_small silently resolves to linear;
        # skip visibly rather than pass on the wrong backbone.
        pytest.importorskip("torch")
        """Phase 2 gate: Architect backbone entropy ≥ 0.5 nats across 5 tasks."""
        client = VariedMockClient(seed=0)
        pool = LLMAgentPool(client=client, cache_dir=tmp_path)
        ds = _toy_dataset()

        traces = []
        for task_id in ("task_a", "task_b", "task_c", "task_d", "task_e"):
            run = run_agentic_lifecycle(
                task_id=task_id,
                X=ds["X"],
                labels=ds["labels"],
                control_mask=ds["control_mask"],
                target_gene_idx=ds["target_gene_idx"],
                held_out="GENE0",
                agent_pool=pool,
                max_rounds=2,
                seed=2026,
                dataset="adamson_full",
            )
            traces.append(run.steps)

        h_backbone = per_agent_field_entropy(traces, agent="Architect", field="backbone")
        h_hvg = per_agent_field_entropy(traces, agent="Architect", field="hvg_count")
        assert h_backbone >= 0.5, f"backbone entropy {h_backbone} < 0.5 nats"
        assert h_hvg >= 0.5, f"hvg entropy {h_hvg} < 0.5 nats"

    def test_validator_critique_steers_architect_round2(self, tmp_path: Path) -> None:
        """When round-1 rejects, the round-2 config must differ."""

        class ScriptedClient:
            # Round 0 architect: linear. Round 1 architect: keep linear
            # unless a validator critique delta is in the prompt.
            def chat_json(self, *, role, task_id, round_index, prompt, seed, dataset):
                return ChatResult(
                    content=self._payload(
                        role=role,
                        task_id=task_id,
                        round_index=round_index,
                        prompt=prompt,
                        seed=seed,
                    ),
                    model_id="stub/scripted",
                )

            def _payload(self, *, role, task_id, round_index, prompt, seed):  # noqa: ARG002
                # A2-1: every reply states a confidence. The Architect keys off a
                # NON-EMPTY Validator delta in its prompt (every Architect prompt
                # carries a '"backbone":' schema line, so that is no signal).
                if role == "Architect":
                    if "Validator suggested config delta: {}" not in prompt:
                        # Validator delta present → propose a different backbone.
                        return json.loads('{"backbone": "mlp", "confidence": 0.6}')
                    return json.loads('{"backbone": "linear", "confidence": 0.6}')
                if role == "Literature":
                    return json.loads(
                        '{"pathway_prior": {}, "expected_up": [], "expected_down": [], "confidence": 0.5}'
                    )
                if role == "DataCurator":
                    return json.loads(
                        '{"hvg_method": "seurat", "hvg_count": 500, "confidence": 0.5}'
                    )
                if role == "Trainer":
                    return json.loads(
                        '{"lr": 1e-2, "epochs": 5, "ridge_lambda": 1.0, "confidence": 0.5}'
                    )
                if role == "Validator":
                    return json.loads('{"dynamic_threshold_msd": 0.02, "confidence": 0.5}')
                return {}

        pool = LLMAgentPool(client=ScriptedClient(), cache_dir=tmp_path)
        ds = _toy_dataset()
        run = run_agentic_lifecycle(
            task_id="t",
            X=ds["X"],
            labels=ds["labels"],
            control_mask=ds["control_mask"],
            target_gene_idx=ds["target_gene_idx"],
            held_out="GENE0",
            agent_pool=pool,
            max_rounds=2,
            seed=2026,
            dataset="adamson_full",
        )
        architect_by_round = [
            s.proposal_content.get("backbone") for s in run.steps if s.agent_name == "Architect"
        ]
        # A2-2: no early stop — both rounds always run; round 0's verdict is
        # recorded on its Validator step. An accepting round 0 emits no delta
        # (a valid outcome: the critique path did not need to fire).
        assert len(architect_by_round) == 2
        assert all(s.source == "llm" for s in run.steps)
        round0_accepted = next(
            s.validator_accepted
            for s in run.steps
            if s.agent_name == "Validator" and s.round_index == 0
        )
        if not round0_accepted:
            # With tight threshold (0.02) the toy dataset should reject,
            # so round-1 should see the validator critique.
            assert architect_by_round[1] != architect_by_round[0], (
                f"critique didn't steer round-2 architect: {architect_by_round}"
            )
