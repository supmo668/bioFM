"""End-to-end integration test — the Phase 2 gate.

The lifecycle must produce meaningfully different configurations across
seeds when wired to an LLM-like pool that returns varied choices. A
previous-round Validator critique must visibly steer round-2 proposals.
"""

from __future__ import annotations

import json
import zlib
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
        # zlib.crc32, not hash(): str hashes are salted per process (PYTHONHASHSEED).
        h = zlib.crc32(f"{role}|{task_id}|{round_index}".encode()) % 10_000
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
                seed=2026,
                dataset="adamson_full",
            )
            traces.append(run.steps)

        h_backbone = per_agent_field_entropy(traces, agent="Architect", field="backbone")
        h_hvg = per_agent_field_entropy(traces, agent="Architect", field="hvg_count")
        assert h_backbone >= 0.5, f"backbone entropy {h_backbone} < 0.5 nats"
        assert h_hvg >= 0.5, f"hvg entropy {h_hvg} < 0.5 nats"

    def test_validator_critique_steers_architect_round2(self, tmp_path: Path, monkeypatch) -> None:
        """A rejected round's non-empty Validator delta reaches the next round's
        Architect prompt as JSON, and the Architect's stated backbone changes.

        QG-3: rejection is FORCED (``validator_threshold_override=-1.0``: no MSD
        passes), all 3 rounds run (A2-2), and every assertion is unconditional.
        The gate's real delta is captured through a spy, so the assertion is on
        the delta's JSON content, not on one exact prompt string.
        """
        import perturb_eval.agentic_lifecycle.loop as loop_mod

        reports: list = []
        real_gate = loop_mod.score_and_gate

        def spy_gate(**kw):
            rep = real_gate(**kw)
            reports.append(rep)
            return rep

        monkeypatch.setattr(loop_mod, "score_and_gate", spy_gate)

        def last_delta_json() -> str | None:
            if not reports or reports[-1].critique is None:
                return None
            delta = dict(reports[-1].critique.suggested_next_config_delta)
            return json.dumps(delta) if delta else None

        class ScriptedClient:
            # Round 0 architect: linear. Later rounds: switch to mlp only when
            # the previous round's (non-empty) delta JSON is in the prompt.
            def __init__(self) -> None:
                self.prompts: dict[tuple[str, int], str] = {}

            def chat_json(self, *, role, task_id, round_index, prompt, seed, dataset):
                self.prompts[(role, round_index)] = prompt
                return ChatResult(
                    content=self._payload(role=role, prompt=prompt), model_id="stub/scripted"
                )

            @staticmethod
            def _payload(*, role, prompt):
                # A2-1: every reply states a confidence.
                if role == "Architect":
                    delta_json = last_delta_json()
                    if delta_json is not None and delta_json in prompt:
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

        client = ScriptedClient()
        pool = LLMAgentPool(client=client, cache_dir=tmp_path)
        ds = _toy_dataset()
        run = run_agentic_lifecycle(
            task_id="t",
            X=ds["X"],
            labels=ds["labels"],
            control_mask=ds["control_mask"],
            target_gene_idx=ds["target_gene_idx"],
            held_out="GENE0",
            agent_pool=pool,
            seed=2026,
            dataset="adamson_full",
            validator_threshold_override=-1.0,  # force rejection every round
        )
        assert all(s.source == "llm" for s in run.steps)
        assert run.n_rounds == 3  # A2-2: fixed three rounds, no early stop
        assert [s.validator_accepted for s in run.steps if s.agent_name == "Validator"] == [
            False,
            False,
            False,
        ]

        # Round 0 was rejected, so its critique carries a NON-EMPTY delta ...
        assert len(reports) == 3
        round0_delta = dict(reports[0].critique.suggested_next_config_delta)
        assert round0_delta, "a rejected round must emit a non-empty config delta"
        # ... whose JSON must appear in the round-1 Architect prompt (and not in round 0's).
        assert json.dumps(round0_delta) not in client.prompts[("Architect", 0)]
        assert json.dumps(round0_delta) in client.prompts[("Architect", 1)], (
            f"round-1 Architect prompt does not carry round-0's critique delta {round0_delta!r}:\n"
            + client.prompts[("Architect", 1)]
        )

        architect_by_round = [
            s.proposal_content.get("backbone") for s in run.steps if s.agent_name == "Architect"
        ]
        assert len(architect_by_round) == 3
        assert architect_by_round[0] == "linear"
        assert architect_by_round[1] != architect_by_round[0], (
            f"critique didn't steer round-2 architect: {architect_by_round}"
        )
