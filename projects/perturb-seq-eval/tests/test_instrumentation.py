"""Unit tests for instrumentation.py.

Uses lightweight stand-ins instead of depending on the cellforge-agents
package — that keeps the test fast and the module well-isolated.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from perturb_eval.instrumentation import (
    round_trace_from_consensus_round,
    run_trace_from_consensus,
)


@dataclass
class _MockProposal:
    agent: str
    confidence: float


@dataclass
class _MockCritique:
    from_agent: str
    on_agent: str
    severity: float


@dataclass
class _MockRound:
    proposals: list[_MockProposal]
    critiques: list[_MockCritique]


@dataclass
class _MockConsensus:
    rounds: list[_MockRound]
    converged: bool


@pytest.fixture
def mock_round() -> _MockRound:
    proposals = [
        _MockProposal("DataCurator", 0.85),
        _MockProposal("Literature", 0.75),
        _MockProposal("Architect", 0.7),
        _MockProposal("Trainer", 0.8),
        _MockProposal("Validator", 0.95),
    ]
    # All critiques severity 0.1, except DataCurator critiques Architect with 0.6.
    critiques = []
    agents = [p.agent for p in proposals]
    for src in agents:
        for tgt in agents:
            if src == tgt:
                continue
            sev = 0.6 if (src == "DataCurator" and tgt == "Architect") else 0.1
            critiques.append(_MockCritique(src, tgt, sev))
    return _MockRound(proposals=proposals, critiques=critiques)


@pytest.mark.unit
def test_round_trace_preserves_agent_order(mock_round) -> None:  # noqa: ANN001
    rt = round_trace_from_consensus_round(mock_round, round_index=0)
    assert rt.agent_names == ("DataCurator", "Literature", "Architect", "Trainer", "Validator")


@pytest.mark.unit
def test_round_trace_maps_confidences(mock_round) -> None:  # noqa: ANN001
    rt = round_trace_from_consensus_round(mock_round, round_index=0)
    assert rt.confidences == (0.85, 0.75, 0.7, 0.8, 0.95)


@pytest.mark.unit
def test_round_trace_builds_critique_matrix(mock_round) -> None:  # noqa: ANN001
    rt = round_trace_from_consensus_round(mock_round, round_index=0)
    # 5 rows × 4 cols (self-critique dropped)
    assert len(rt.critique_severities) == 5
    assert all(len(r) == 4 for r in rt.critique_severities)
    # The DataCurator→Architect severity = 0.6 should surface.
    # DataCurator=row 0, Architect=agent 2. Projection rule: since tgt(2) > src(0),
    # column = tgt - 1 = 1 in the row-width-4 matrix.
    assert rt.critique_severities[0][1] == pytest.approx(0.6)
    # And there should be no other 0.6-valued entry.
    flat = [v for r in rt.critique_severities for v in r]
    assert flat.count(pytest.approx(0.6)) == 1


@pytest.mark.unit
def test_run_trace_records_round_count(mock_round) -> None:  # noqa: ANN001
    consensus = _MockConsensus(rounds=[mock_round, mock_round], converged=True)
    trace = run_trace_from_consensus(consensus, task_id="t1", backbone="scGPT")
    assert trace.n_rounds == 2
    assert trace.n_agents == 5
    assert trace.converged is True


@pytest.mark.unit
def test_run_trace_token_mismatch_raises(mock_round) -> None:  # noqa: ANN001
    consensus = _MockConsensus(rounds=[mock_round, mock_round], converged=True)
    with pytest.raises(ValueError):
        run_trace_from_consensus(
            consensus, task_id="t1", compute_tokens_per_round=[100],  # wrong length
        )


@pytest.mark.unit
def test_winner_is_high_confidence_low_severity(mock_round) -> None:  # noqa: ANN001
    rt = round_trace_from_consensus_round(mock_round, round_index=0)
    # Validator has highest confidence (0.95) and no outsized critique against it.
    assert rt.agent_names[rt.winner_index] == "Validator"
