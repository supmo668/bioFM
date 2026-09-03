"""ChipSim — lung-on-chip exposure and barrier-response simulator.

Package skeleton per A&D §4.4 / build-plan S1. Subpackages are created empty at
scaffold time; each is populated by its own milestone plan.

Scaffold integrity
------------------
Since PEP 420, a subdirectory with no ``__init__.py`` still imports, as an
implicit *namespace* package. Nothing announces the downgrade, so the guard below
turns it into an ImportError — which is what makes S1's "exits non-zero if any
``__init__.py`` is removed" a real, falsifiable condition rather than a vacuous one.

Why a namespace subpackage is worth failing on:

* A namespace package merges across every matching directory on ``sys.path``, so
  an unrelated ``chipsim/`` elsewhere on the path can silently contribute or
  shadow modules — the imported ``chipsim.eval`` is then not necessarily this one.
* A subpackage whose ``__init__.py`` was its only file disappears from a built
  wheel entirely, because an empty directory is not packaged.

(An earlier revision of this docstring claimed a missing ``__init__.py`` drops the
subpackage's *other* modules from the wheel. That is false for this build backend:
hatchling's ``packages = ["chipsim"]`` copies the tree file-by-file, so sibling
modules are still included. Corrected so nobody debugging this chases a
packaging failure that will not occur.)

The check uses the import system rather than the filesystem, so it stays correct
under zipimport and other non-filesystem loaders, where probing for an
``__init__.py`` path would report a false failure.
"""

from importlib.machinery import PathFinder

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
    """Raise ImportError if any A&D §4.4 subpackage is missing or a namespace package.

    A regular package's spec has a concrete ``origin`` (its ``__init__``); a PEP 420
    namespace package's spec has ``origin is None``. That distinction is exactly what
    we need, and it is loader-agnostic.
    """
    broken = []
    for name in SUBPACKAGES:
        spec = PathFinder.find_spec(f"{__name__}.{name}", __path__)
        if spec is None:
            broken.append(f"{name} (absent)")
        elif spec.origin is None:
            broken.append(f"{name} (namespace package — no __init__.py)")
    if broken:
        raise ImportError(
            "chipsim scaffold is incomplete — "
            + ", ".join(broken)
            + ". A namespace subpackage merges across sys.path and can be shadowed by "
            "another chipsim/, and a subpackage left with no files at all is dropped "
            "from a built wheel. Restore the __init__.py (build-plan S1)."
        )


_assert_regular_packages()
