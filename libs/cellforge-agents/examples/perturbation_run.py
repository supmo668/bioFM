"""End-to-end demo: run the 5-agent team on a GSK3B-KO perturbation problem."""

from __future__ import annotations

import json

from cellforge.agents import build_default_team
from cellforge.orchestrator import Orchestrator
from cellforge.problem import Modality, Problem


def main() -> None:
    problem = Problem(
        perturbation="GSK3B knockout",
        modality=Modality.SCRNA,
        cell_type_hint="hepatocyte",
    )
    orch = Orchestrator(build_default_team(), max_rounds=2, consensus_threshold=0.7)
    result = orch.run(problem)

    print(f"converged            = {result.converged}")
    print(f"consensus_score      = {result.consensus_score:.3f}")
    print(f"winner_agent         = {result.winner.agent}")
    print(f"winner_confidence    = {result.winner.confidence:.2f}")
    print(f"n_rounds             = {len(result.rounds)}")
    print(f"n_proposals          = {len(result.all_proposals)}")
    print(f"n_critiques          = {len(result.all_critiques)}")
    print("\n--- proposals per agent ---")
    for p in result.rounds[-1].proposals:
        print(f"  [{p.agent:13s}] conf={p.confidence:.2f}  "
              f"tools={','.join(p.tools_used)}")
        print(f"                  rationale: {p.rationale}")
    print("\n--- winner.content ---")
    print(json.dumps(result.winner.content, indent=2, default=str))


if __name__ == "__main__":
    main()
