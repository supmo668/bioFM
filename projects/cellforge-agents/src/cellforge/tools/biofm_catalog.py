"""Architect tool belt: query the BioFM catalog assembled in research/MODELS.md."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BackboneSuggestion:
    name: str
    modality: str
    note: str


class BioFMCatalog:
    """Tiny in-memory mirror of `research/MODELS.md`.

    Keeping it in Python rather than parsing the markdown avoids a test-time
    filesystem dependency — the catalog is small and the source of truth is
    the markdown doc, updated by humans.
    """

    name = "biofm.catalog"

    _CATALOG: dict[str, list[BackboneSuggestion]] = {
        "scRNA-seq": [
            BackboneSuggestion("scGPT", "scRNA-seq", "33M cells; supports perturbation head out of the box"),
            BackboneSuggestion("Geneformer", "scRNA-seq", "rank-value tokens; strong on network biology"),
            BackboneSuggestion("scFoundation", "scRNA-seq", "50M cells; denoising reconstruction objective"),
            BackboneSuggestion("scPRINT-2", "scRNA-seq", "350M cells, 16 organisms; SOTA denoising + cell typing"),
            BackboneSuggestion("UCE", "scRNA-seq", "zero-shot across species"),
        ],
        "scATAC-seq": [
            BackboneSuggestion("Nicheformer", "scRNA+spatial", "110M cells incl. spatial"),
            BackboneSuggestion("CellPLM", "scRNA+spatial", "cell language model beyond single cells"),
        ],
        "CITE-seq": [
            BackboneSuggestion("scGPT", "multi-omics", "native multi-omics heads"),
        ],
        "DNA": [
            BackboneSuggestion("BioFM-265M", "DNA", "annotation-aware tokens; CPU-friendly"),
            BackboneSuggestion("Evo 2", "DNA", "1M context; cross-domain variant scoring"),
            BackboneSuggestion("Nucleotide Transformer", "DNA", "multi-species, 2.5B"),
        ],
        "protein": [
            BackboneSuggestion("ESM-2", "protein", "battle-tested embeddings"),
            BackboneSuggestion("ESM-3", "protein multimodal", "sequence+structure+function"),
            BackboneSuggestion("SaProt", "protein", "structure-aware tokens"),
        ],
    }

    def suggest(self, modality: str) -> list[BackboneSuggestion]:
        return list(self._CATALOG.get(modality, []))

    def read_markdown(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")
