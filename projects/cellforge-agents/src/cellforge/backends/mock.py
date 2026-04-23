"""Deterministic mock backend for tests and offline demos.

Route by a keyword in the user prompt so each agent receives a realistic-looking
stubbed response without any network I/O. Good enough to exercise the full
propose → critique → vote loop.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MockBackend:
    name: str = "mock"

    def complete(self, system: str, user: str, *, max_tokens: int = 512) -> str:  # noqa: ARG002
        low = user.lower()
        if "curate" in low or "qc" in low:
            return (
                "{\"dataset_id\": \"GSE12345\", \"n_cells\": 48000, \"n_genes\": 22000, "
                "\"pct_mito_max\": 12.0, \"hvgs\": 3000}"
            )
        if "literature" in low or "prior" in low:
            return (
                "{\"pathways\": [\"Wnt/beta-catenin\", \"PI3K-AKT\"], "
                "\"references\": [\"PMID:11111\", \"PMID:22222\"], "
                "\"expected_up\": [\"AXIN2\", \"MYC\"], \"expected_down\": [\"CTNNB1\"]}"
            )
        if "architecture" in low or "backbone" in low:
            return (
                "{\"backbone\": \"scGPT\", \"head\": \"perturbation_adapter\", "
                "\"d_model\": 512, \"n_layers\": 12, \"rationale\": \"scGPT is pretrained on 33M cells and supports perturbation heads out of the box\"}"
            )
        if "train" in low or "recipe" in low:
            return (
                "{\"optimizer\": \"adamw\", \"lr\": 3e-4, \"epochs\": 10, "
                "\"batch_size\": 128, \"cv_split\": \"by_donor\", \"early_stop\": \"val_loss_plateau_3\"}"
            )
        if "validate" in low or "enrichment" in low:
            return (
                "{\"deg_overlap_at_500\": 0.62, \"enriched_pathways\": [\"Wnt/beta-catenin\"], "
                "\"held_out_auroc\": 0.78, \"calibration\": 0.91}"
            )
        if "critique" in low:
            return (
                "{\"severity\": 0.2, \"comment\": \"looks reasonable; recommend adding donor-level leakage check\"}"
            )
        return "{\"note\": \"mock response\"}"
