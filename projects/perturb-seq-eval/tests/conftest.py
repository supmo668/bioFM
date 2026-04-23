"""Shared fixtures: synthetic RoundTraces and RunTraces for every test."""

from __future__ import annotations

import pytest

from perturb_eval.types import RoundTrace, RunTrace


@pytest.fixture
def agent_names() -> tuple[str, ...]:
    return ("DataCurator", "Literature", "Architect", "Trainer", "Validator")


@pytest.fixture
def easy_round(agent_names: tuple[str, ...]) -> RoundTrace:
    """Decisive winner: one agent confidently high, others low; low critique severity."""
    return RoundTrace(
        round_index=0,
        agent_names=agent_names,
        confidences=(0.4, 0.5, 0.45, 0.55, 0.95),
        critique_severities=(
            (0.1, 0.1, 0.1, 0.1),
            (0.1, 0.1, 0.1, 0.1),
            (0.1, 0.1, 0.1, 0.1),
            (0.1, 0.1, 0.1, 0.1),
            (0.1, 0.1, 0.1, 0.1),
        ),
        winner_index=4,
        consensus_score=0.85,
    )


@pytest.fixture
def hard_round(agent_names: tuple[str, ...]) -> RoundTrace:
    """No winner: confidences clustered, critiques all high."""
    return RoundTrace(
        round_index=0,
        agent_names=agent_names,
        confidences=(0.5, 0.55, 0.48, 0.52, 0.5),
        critique_severities=(
            (0.7, 0.8, 0.6, 0.9),
            (0.8, 0.7, 0.9, 0.6),
            (0.9, 0.6, 0.7, 0.8),
            (0.6, 0.9, 0.8, 0.7),
            (0.9, 0.8, 0.7, 0.6),
        ),
        winner_index=1,
        consensus_score=0.2,
    )


@pytest.fixture
def converging_run(agent_names: tuple[str, ...]) -> RunTrace:
    """A 3-round run where confidence rises and entropy falls each round."""
    rounds = (
        RoundTrace(0, agent_names, (0.5, 0.5, 0.5, 0.5, 0.5),
                   ((0.5, 0.5, 0.5, 0.5),) * 5, winner_index=0, consensus_score=0.3),
        RoundTrace(1, agent_names, (0.6, 0.7, 0.65, 0.7, 0.8),
                   ((0.3, 0.3, 0.3, 0.3),) * 5, winner_index=4, consensus_score=0.5),
        RoundTrace(2, agent_names, (0.7, 0.8, 0.75, 0.85, 0.95),
                   ((0.15, 0.15, 0.15, 0.15),) * 5, winner_index=4, consensus_score=0.8),
    )
    return RunTrace(task_id="converging", rounds=rounds, converged=True, backbone="scGPT")


@pytest.fixture
def thrashing_run(agent_names: tuple[str, ...]) -> RunTrace:
    """Winner flips every round; confidence does not rise."""
    rounds = (
        RoundTrace(0, agent_names, (0.5, 0.6, 0.45, 0.55, 0.5),
                   ((0.6, 0.6, 0.6, 0.6),) * 5, winner_index=1, consensus_score=0.1),
        RoundTrace(1, agent_names, (0.6, 0.45, 0.5, 0.55, 0.5),
                   ((0.6, 0.6, 0.6, 0.6),) * 5, winner_index=0, consensus_score=0.1),
        RoundTrace(2, agent_names, (0.5, 0.55, 0.6, 0.45, 0.5),
                   ((0.6, 0.6, 0.6, 0.6),) * 5, winner_index=2, consensus_score=0.1),
    )
    return RunTrace(task_id="thrashing", rounds=rounds, converged=False, backbone="scGPT")
