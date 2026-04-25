"""Tests for the per-agent choice-entropy probe used in §5 of the paper."""

from __future__ import annotations

import math

import numpy as np

from perturb_eval.agentic_lifecycle.freedom_probe import (
    choice_entropy,
    per_agent_field_entropy,
    summarise_choice_distribution,
)


def _trace(agent: str, field_name: str, value):
    """Minimal LifecycleStep-like dict for the probe."""
    return {
        "agent_name": agent,
        "proposal_content": {field_name: value},
    }


class TestChoiceEntropy:
    def test_zero_entropy_on_single_value(self) -> None:
        assert choice_entropy(["a", "a", "a"]) == 0.0

    def test_uniform_two_values_log2(self) -> None:
        h = choice_entropy(["a", "b", "a", "b"])
        # Shannon entropy in nats → ln(2) ≈ 0.693.
        assert math.isclose(h, math.log(2), rel_tol=1e-6)

    def test_handles_numeric_bins(self) -> None:
        values = [1e-2, 1e-3, 1e-2, 1e-3]
        h = choice_entropy(values)
        assert h > 0

    def test_empty_sequence_returns_zero(self) -> None:
        assert choice_entropy([]) == 0.0


class TestPerAgentFieldEntropy:
    def test_counts_across_multiple_traces(self) -> None:
        traces = [
            [_trace("Architect", "backbone", "linear")],
            [_trace("Architect", "backbone", "mlp")],
            [_trace("Architect", "backbone", "scgpt_small")],
        ]
        h = per_agent_field_entropy(traces, agent="Architect", field="backbone")
        assert h > 0.5, f"expected diverse architect choices, got {h} nats"

    def test_zero_when_all_same(self) -> None:
        traces = [
            [_trace("Architect", "backbone", "linear")],
            [_trace("Architect", "backbone", "linear")],
        ]
        h = per_agent_field_entropy(traces, agent="Architect", field="backbone")
        assert h == 0.0

    def test_ignores_other_agents(self) -> None:
        traces = [
            [
                _trace("Architect", "backbone", "linear"),
                _trace("Trainer", "backbone", "mlp"),
            ],
            [
                _trace("Architect", "backbone", "linear"),
                _trace("Trainer", "backbone", "linear"),
            ],
        ]
        h = per_agent_field_entropy(traces, agent="Architect", field="backbone")
        assert h == 0.0


class TestSummariseChoiceDistribution:
    def test_returns_distribution_dict(self) -> None:
        traces = [
            [_trace("Architect", "backbone", "linear")],
            [_trace("Architect", "backbone", "linear")],
            [_trace("Architect", "backbone", "mlp")],
        ]
        dist = summarise_choice_distribution(traces, agent="Architect", field="backbone")
        assert dist["linear"] == 2
        assert dist["mlp"] == 1

    def test_gate_v05_phase2_choice_entropy_threshold(self) -> None:
        """Phase 2 gate: Architect must vary across ≥3 distinct backbones."""
        rng = np.random.default_rng(2026)
        backbones = ["linear", "mlp", "scgpt_small"]
        traces = []
        for _ in range(15):
            bb = rng.choice(backbones)
            traces.append([_trace("Architect", "backbone", str(bb))])
        h = per_agent_field_entropy(traces, agent="Architect", field="backbone")
        assert h >= 0.5  # nats — the plan's gate
