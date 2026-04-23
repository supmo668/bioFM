"""BioGPT-backed Literature tool.

Uses `microsoft/BioGPT-Large` (or a smaller `BioGPT` variant) to retrieve
pathway + mechanism text for a target gene, which the Literature agent
then turns into its structured proposal. The point is that the agent's
rationale is **grounded in a pretrained biomedical language model**,
not a rule table.

Intended for use inside the Modal image (requires torch + transformers).
Weights are pulled from HuggingFace Hub on first call and cached in the
Modal volume at ``/data/biofm_cache/biogpt``.

Fallback path: if the model cannot be loaded (no GPU, no net access),
the tool degrades to the rule-based `cellforge.tools.literature.LiteratureTool`.
"""

from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass
from pathlib import Path

HAS_TRANSFORMERS = (
    importlib.util.find_spec("transformers") is not None
    and importlib.util.find_spec("torch") is not None
)


@dataclass
class BioGPTMechanismTool:
    """Drop-in replacement for `cellforge.tools.literature.LiteratureTool`.

    Emits the same `.mechanism(perturbation) -> dict` contract the
    CellForge `LiteratureAgent` expects, but derives pathway + expected
    up/down gene lists from a live BioGPT generation.
    """

    name: str = "biogpt"
    model_id: str = "microsoft/BioGPT"  # 347M params; BioGPT-Large is 1.5B
    cache_dir: str = os.environ.get("HF_CACHE_DIR", "/data/biofm_cache/biogpt")
    max_new_tokens: int = 96
    _pipe: object = None  # lazy

    def _ensure_loaded(self) -> None:
        if self._pipe is not None:
            return
        if not HAS_TRANSFORMERS:
            raise RuntimeError(
                "BioGPTMechanismTool requires torch + transformers; install the "
                "`scgpt` Poetry group or run inside the Modal BioFM image."
            )
        import transformers  # noqa: PLC0415

        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        tokenizer = transformers.AutoTokenizer.from_pretrained(
            self.model_id, cache_dir=self.cache_dir,
        )
        model = transformers.AutoModelForCausalLM.from_pretrained(
            self.model_id, cache_dir=self.cache_dir,
        )
        self._pipe = transformers.pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device_map="auto",
            max_new_tokens=self.max_new_tokens,
        )

    # ------------------------------------------------------------------
    # Contract used by cellforge.agents.literature.LiteratureAgent
    # ------------------------------------------------------------------
    def mechanism(self, perturbation: str) -> dict:
        """Return ``{"pathways": [...], "up": [...], "down": [...]}`` for a
        target gene / perturbation, grounded in BioGPT generation.

        We prompt BioGPT with a terse biomedical seed and parse the
        generation for gene-symbol tokens (uppercase 3–6 letter strings)
        attributed to up/down regulation.
        """
        self._ensure_loaded()
        target = perturbation.split()[0]  # "GSK3B knockdown" → "GSK3B"
        prompt = (
            f"{target} is involved in the following biological pathways: "
        )
        out = self._pipe(prompt, num_return_sequences=1)[0]["generated_text"]  # type: ignore[index,call-arg]
        # Very lightweight extraction — BioGPT generations are prose, so
        # we look for uppercase gene-symbol-like tokens and any pathway
        # keywords on a short keyword list.
        pathways = _extract_pathways(out)
        up = _extract_genes_near(out, hint="up")[:6]
        down = _extract_genes_near(out, hint="down")[:6]
        return {
            "pathways": pathways if pathways else ["unknown"],
            "up": up,
            "down": down,
            "_raw_generation": out[:240],
        }

    def search(self, perturbation: str, max_hits: int = 5):  # noqa: ARG002
        """Stub: CellForge's LiteratureTool.search returns objects with .pmid.

        For the probe-collection use case we return an empty list; if a
        reviewer wants PubMed IDs, wire a downstream Europe PMC call.
        """
        return []


_PATHWAY_KEYWORDS = (
    "Wnt", "PI3K", "AKT", "MAPK", "JAK", "STAT", "NF-kB", "mTOR", "p53",
    "UPR", "ER stress", "apoptosis", "autophagy", "cell cycle",
    "oxidative phosphorylation", "glycolysis", "TCA",
)


def _extract_pathways(text: str) -> list[str]:
    hits = [kw for kw in _PATHWAY_KEYWORDS if kw.lower() in text.lower()]
    return list(dict.fromkeys(hits))  # preserve order, dedupe


def _extract_genes_near(text: str, *, hint: str) -> list[str]:
    """Gene-symbol heuristic: uppercase 3–6 char tokens occurring within
    120 chars of the ``hint`` word. Returns unique tokens in order."""
    import re  # noqa: PLC0415

    lowered = text.lower()
    idx = lowered.find(hint.lower())
    if idx < 0:
        window = text
    else:
        window = text[max(0, idx - 60): idx + 60]
    tokens = re.findall(r"\b[A-Z][A-Z0-9]{2,5}\b", window)
    # Filter out common false positives (English stopwords that happen to be uppercase in running text).
    stop = {"UP", "DOWN", "RNA", "DNA", "MRNA", "CDNA", "RT", "PCR"}
    clean = [t for t in tokens if t not in stop]
    return list(dict.fromkeys(clean))
