"""Trainer tool belt: produce a reproducible training recipe."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TrainingRecipe:
    optimizer: str
    lr: float
    epochs: int
    batch_size: int
    cv_split: str
    early_stop_rule: str
    grad_accum: int = 1


class TrainerTool:
    name = "trainer.recipe"

    def build(self, n_cells: int, backbone: str, budget_seconds: int) -> TrainingRecipe:
        # Simple heuristics — enough for a PoC.
        big = n_cells > 100_000
        return TrainingRecipe(
            optimizer="adamw",
            lr=1e-4 if big else 3e-4,
            epochs=5 if budget_seconds < 60 else 10,
            batch_size=64 if big else 128,
            cv_split="by_donor",
            early_stop_rule="val_loss_plateau_3",
            grad_accum=2 if big else 1,
        )
