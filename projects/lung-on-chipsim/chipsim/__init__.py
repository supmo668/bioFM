"""ChipSim — lung-on-chip exposure and barrier-response simulator.

Package skeleton per A&D §4.4 / build-plan S1. Subpackages are created empty at
scaffold time; each is populated by its own milestone plan.

Scaffold integrity
------------------
Since PEP 420, a subdirectory with no ``__init__.py`` still imports, as an
implicit *namespace* package. That is a silent failure mode here: hatchling's
wheel build takes regular packages, so a subpackage that lost its ``__init__.py``
would keep importing from the source tree and vanish from an installed wheel.
The guard below turns that silence into an ImportError at ``import chipsim``,
which is what makes S1's done-condition falsifiable.
"""

from pathlib import Path

__version__ = "0.1.0"

#: The A&D §4.4 layer set. Every entry must be a *regular* package.
SUBPACKAGES = (
    "ingest",
    "harmonize",
    "encoders",
    "heads",
    "transport",
    "occupancy",
    "surface",
    "uncertainty",
    "eval",
    "acquire",
)


def _assert_regular_packages() -> None:
    here = Path(__file__).parent
    missing = [name for name in SUBPACKAGES if not (here / name / "__init__.py").is_file()]
    if missing:
        raise ImportError(
            "chipsim scaffold is incomplete — missing __init__.py in subpackage(s): "
            + ", ".join(missing)
            + ". These would import as PEP 420 namespace packages and be dropped "
            "from a built wheel. Restore them (build-plan S1)."
        )


_assert_regular_packages()
