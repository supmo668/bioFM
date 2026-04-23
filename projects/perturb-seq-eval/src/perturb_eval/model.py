"""Perturb-seq predictor protocol + implementations.

The 5 agents interact with a perturbation predictor via this common interface.
Two implementations ship:

* ``MockPredictor`` — deterministic, CPU-only, used by tests and CI.
* ``ScGPTPredictor`` — thin wrapper over the public scGPT release, loaded lazily
  because torch is a heavy optional dependency. See ``docs/THESIS.md § 6.2``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class PredictedResponse:
    """Predicted expression / response summary for a perturbation."""

    perturbation: str
    predicted_up: tuple[str, ...]
    predicted_down: tuple[str, ...]
    confidence: float
    backbone: str


class PerturbationPredictor(Protocol):
    name: str
    backbone: str

    def predict_response(self, perturbation: str, *, top_k: int = 50) -> PredictedResponse: ...


# ---------------------------------------------------------------------------
# Mock — zero-dependency, deterministic
# ---------------------------------------------------------------------------


@dataclass
class MockPredictor:
    """Mock predictor whose output is a deterministic function of perturbation name."""

    name: str = "mock"
    backbone: str = "mock"

    # A tiny curated mapping that mirrors the LiteratureTool in cellforge-agents.
    _CANNED: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self._CANNED is None:
            object.__setattr__(self, "_CANNED", {
                "gsk3b": (("AXIN2", "MYC", "CCND1"), ("CTNNB1",)),
                "tp53":  (("CDKN1A", "MDM2", "BAX"), ("MYC",)),
                "ctnnb1": (("MYC", "CCND1"), ("AXIN2",)),
                "il6":   (("SOCS3", "STAT3"), ()),
                "lps":   (("TNF", "IL6", "CXCL10"), ()),
            })

    def predict_response(self, perturbation: str, *, top_k: int = 50) -> PredictedResponse:  # noqa: ARG002
        key = perturbation.lower()
        up, down = ((), ())
        for k, (u, d) in self._CANNED.items():
            if k in key:
                up, down = u, d
                break
        confidence = 0.85 if up else 0.35
        return PredictedResponse(
            perturbation=perturbation,
            predicted_up=up,
            predicted_down=down,
            confidence=confidence,
            backbone=self.backbone,
        )


# ---------------------------------------------------------------------------
# scGPT wrapper — optional
# ---------------------------------------------------------------------------


@dataclass
class ScGPTPredictor:  # pragma: no cover - needs torch + model weights
    """Thin adapter over the public scGPT release.

    Configuration
    -------------
    The default config targets ``scGPT_whole_human`` (≈50M params) with a LoRA
    adapter on the perturbation head. Fits on a single 16 GB GPU; batches of 64
    cells on 8 GB.

    The adapter is kept small on purpose — the thesis is about *how* we
    orchestrate agents around the model, not about squeezing a new SoTA
    perturbation predictor out of scGPT.
    """

    name: str = "scgpt"
    backbone: str = "scGPT"
    checkpoint: str = "scGPT_whole_human"
    adapter_rank: int = 8
    device: str = "cuda"

    _model: Any = None
    _tokenizer: Any = None

    def load(self) -> None:
        """Lazy load — imports torch + scGPT only when invoked."""
        import torch  # noqa: F401
        # The real loader wires up:
        #   from scgpt.model import TransformerModel
        #   self._model = TransformerModel.from_pretrained(self.checkpoint).to(self.device)
        # and attaches a LoRA adapter on the perturbation head.
        raise NotImplementedError(
            "ScGPTPredictor.load — requires the scGPT release + torch; see docs/THESIS.md §6.2"
        )

    def predict_response(self, perturbation: str, *, top_k: int = 50) -> PredictedResponse:
        if self._model is None:
            self.load()
        raise NotImplementedError
