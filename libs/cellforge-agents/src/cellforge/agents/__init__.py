from cellforge.agents.architect import ArchitectAgent
from cellforge.agents.base import BaseAgent
from cellforge.agents.data_curator import DataCuratorAgent
from cellforge.agents.literature import LiteratureAgent
from cellforge.agents.trainer import TrainerAgent
from cellforge.agents.validator import ValidatorAgent

__all__ = [
    "ArchitectAgent",
    "BaseAgent",
    "DataCuratorAgent",
    "LiteratureAgent",
    "TrainerAgent",
    "ValidatorAgent",
]


def build_default_team() -> list[BaseAgent]:
    """Factory: return the canonical 5-agent CellForge team."""
    return [
        DataCuratorAgent(),
        LiteratureAgent(),
        ArchitectAgent(),
        TrainerAgent(),
        ValidatorAgent(),
    ]
