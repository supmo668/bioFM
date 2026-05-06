"""End-to-end demo that compares all four strategies on a single prompt.

Run:
    python examples/ttc_sweep.py --prompt ATGCGTACGT
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ttc.config import RunConfig, SamplingConfig, StrategyName
from ttc.runner import run_strategy


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="ATGCGTACGT")
    parser.add_argument("--n", type=int, default=8)
    parser.add_argument("--max-new-tokens", type=int, default=64)
    parser.add_argument("--out", type=Path, default=Path("results.jsonl"))
    args = parser.parse_args()

    strategies = [
        StrategyName.GREEDY,
        StrategyName.BEST_OF_N,
        StrategyName.SELF_CONSISTENCY,
        StrategyName.TEMPERATURE_SWEEP,
    ]

    with args.out.open("w", encoding="utf-8") as fh:
        for s in strategies:
            cfg = RunConfig(
                strategy=s,
                prompt=args.prompt,
                n_samples=args.n,
                sampling=SamplingConfig(max_new_tokens=args.max_new_tokens),
            )
            result = run_strategy(cfg)
            fh.write(
                json.dumps(
                    {
                        "strategy": s.value,
                        "compute_budget": result.compute_budget,
                        "winner": result.winner.text[:200],
                        "best_score": max(result.scores),
                        "mean_score": sum(result.scores) / len(result.scores),
                    }
                )
                + "\n"
            )
            print(f"{s.value:22s} budget={result.compute_budget:5d}  best={max(result.scores):.4f}")


if __name__ == "__main__":
    main()
