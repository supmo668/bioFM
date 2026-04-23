"""Validator tool belt: pathway enrichment + DEG overlap (stub).

Real impl: wrap ``gseapy.prerank`` with MSigDB / Reactome gene sets.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationReport:
    deg_overlap_at_k: float
    enriched_pathways: tuple[str, ...]
    held_out_auroc: float
    calibration: float
    negative_control_auroc: float


class PathwayTool:
    name = "pathway.enrichment"

    def validate(
        self,
        predicted_up: list[str],
        predicted_down: list[str],
        expected_up: list[str],
        expected_down: list[str],
    ) -> ValidationReport:
        overlap_up = _jaccard(predicted_up, expected_up)
        overlap_down = _jaccard(predicted_down, expected_down)
        overall = 0.5 * overlap_up + 0.5 * overlap_down
        return ValidationReport(
            deg_overlap_at_k=overall,
            enriched_pathways=("Wnt/beta-catenin",) if overall > 0.1 else (),
            held_out_auroc=0.5 + 0.3 * overall,  # smooth, bounded
            calibration=0.85 + 0.1 * overall,
            negative_control_auroc=0.5,  # shuffled labels → chance
        )


def _jaccard(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not (sa | sb):
        return 0.0
    return len(sa & sb) / len(sa | sb)
