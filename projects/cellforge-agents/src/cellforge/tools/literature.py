"""Literature-agent tool belt: PubMed / bioRxiv retrieval + mechanism hypothesis.

Stubbed for offline usage; swap in ``Bio.Entrez.esearch`` for production.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LiteratureHit:
    pmid: str
    title: str
    year: int
    gene_mentions: tuple[str, ...]


class LiteratureTool:
    name = "literature.pubmed"

    # a tiny curated stub so the agent has something deterministic to reason over
    _MECHANISMS: dict[str, dict[str, list[str]]] = {
        "gsk3b": {
            "pathways": ["Wnt/beta-catenin", "PI3K-AKT", "Insulin signalling"],
            "up": ["AXIN2", "MYC", "CCND1"],
            "down": ["CTNNB1"],
        },
        "lps": {
            "pathways": ["TLR4/NF-kB", "Type I IFN"],
            "up": ["TNF", "IL6", "CXCL10"],
            "down": [],
        },
        "il6": {
            "pathways": ["JAK-STAT3"],
            "up": ["SOCS3", "STAT3"],
            "down": [],
        },
    }

    def search(self, query: str, *, max_hits: int = 5) -> list[LiteratureHit]:
        return [
            LiteratureHit(
                pmid=f"PMID:{30_000_000 + i}",
                title=f"Mechanistic study of {query} (stub)",
                year=2023 + (i % 3),
                gene_mentions=tuple(self._mechanism_for(query).get("up", [])),
            )
            for i in range(max_hits)
        ]

    def mechanism(self, perturbation: str) -> dict[str, list[str]]:
        return self._mechanism_for(perturbation)

    # ------------------------------------------------------------------
    def _mechanism_for(self, perturbation: str) -> dict[str, list[str]]:
        key = perturbation.lower()
        for k, v in self._MECHANISMS.items():
            if k in key:
                return v
        return {"pathways": ["unknown"], "up": [], "down": []}
