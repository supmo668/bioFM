"""Transport-core MAP prior — build-plan T28, consuming S14's template.

Finding D made this prior a required argument with no default; **Finding E is why it
matters.** At three reference compounds (T21's floor) the reported `(alpha, k_sink)` is
substantially prior-determined, so this file does real work on the M1 result rather than
merely satisfying a signature. A default here would be an agent-written biological
number wearing the costume of a software convenience, which is exactly the thing
Global Constraint #1 forbids.

Each of the two priors is log-normal: `mean_log` and `sigma_log`, plus the `citation`
that supports them, or `assumed: true` for an explicitly uninformative prior. Either is
legitimate; **silence is not**, and that is the whole content of the validator.

`configs/transport_prior.yaml` is not named by S6, so no absence guard exists or is
created for it (S14). The scaffold lives beside θ's at
`configs/templates/transport_prior.scaffold.yaml`.
"""

from __future__ import annotations

import numbers
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

import yaml

#: S14's scaffold, relative to the project root.
SCAFFOLD_RELPATH = Path("configs/templates/transport_prior.scaffold.yaml")

#: The two entries the fit reads, in the order the scaffold emits them.
PRIOR_NAMES = ("alpha_prior", "k_sink_prior")

#: The keys one entry may carry (S14).
ENTRY_KEYS = ("mean_log", "sigma_log", "citation", "assumed")

#: What each entry parameterises, for the message the validator raises.
_PARAMETER_OF = {
    "alpha_prior": "alpha, the transport scaling term",
    "k_sink_prior": "k_sink, the sink rate constant",
}


class TransportPriorError(RuntimeError):
    """A transport-prior file violates T28's contract."""


class TransportPriorSourceError(TransportPriorError):
    """An entry carries neither a citation nor `assumed: true`."""


class TransportPriorTemplateError(TransportPriorError):
    """Writing the scaffold would destroy human work."""


def _blank(value: object) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _is_numeric(value: object) -> bool:
    return isinstance(value, numbers.Number) and not isinstance(value, bool)


def _check_entry(name: str, entry: object) -> dict:
    if not isinstance(entry, dict):
        raise TransportPriorError(f"`{name}` is not a mapping; got {type(entry).__name__}.")
    unknown = sorted(set(entry) - set(ENTRY_KEYS))
    if unknown:
        raise TransportPriorError(
            f"`{name}` carries unknown key(s) {unknown}. Permitted: {list(ENTRY_KEYS)}."
        )

    for key in ("mean_log", "sigma_log"):
        if _blank(entry.get(key)):
            raise TransportPriorError(
                f"`{name}.{key}` is empty. A prior on {_PARAMETER_OF[name]} with no "
                f"{key} is not a prior; at T21's floor of three reference compounds the "
                "reported value is substantially prior-determined (Finding E), so there "
                "is no harmless default to fall back on."
            )
        if not _is_numeric(entry[key]):
            raise TransportPriorError(
                f"`{name}.{key}` must be a number on the log scale; got {entry[key]!r}."
            )

    if entry["sigma_log"] <= 0:
        raise TransportPriorError(
            f"`{name}.sigma_log` is {entry['sigma_log']!r}; a log-normal width must be "
            "positive. A zero width is a point mass, which would fix the parameter "
            "rather than prior it."
        )

    assumed = entry.get("assumed")
    if assumed not in (True, False, None):
        raise TransportPriorError(f"`{name}.assumed` is {assumed!r}; it must be true or false.")
    if assumed is not True and _blank(entry.get("citation")):
        raise TransportPriorSourceError(
            f"`{name}` carries numbers with no `citation` and is not flagged "
            "`assumed: true`. Either cite the literature the prior comes from, or "
            "declare it an explicit uninformative prior with its width stated. Both are "
            "legitimate; leaving it unmarked is not, because the reader cannot tell "
            "which one the reported result rests on."
        )
    return {**entry, "assumed": assumed is True}


@dataclass(frozen=True)
class TransportPrior:
    """A validated `(alpha, k_sink)` MAP prior (T28).

    Same posture as `ThetaConfig`: value plus citation, or an explicit assumption with
    a stated width, nothing silently absent. Frozen, so the fit cannot adjust the prior
    it was handed.
    """

    entries: Mapping[str, Mapping[str, object]]
    source_path: Path

    @classmethod
    def load(cls, path: Path) -> TransportPrior:
        path = Path(path)
        doc = yaml.safe_load(path.read_text())
        if not isinstance(doc, dict):
            raise TransportPriorError(f"{path} does not parse as a YAML mapping.")
        unknown = sorted(set(doc) - set(PRIOR_NAMES))
        if unknown:
            raise TransportPriorError(
                f"{path} declares entr(ies) the fit does not read: {unknown}. "
                f"Permitted: {list(PRIOR_NAMES)}."
            )
        missing = [n for n in PRIOR_NAMES if n not in doc]
        if missing:
            raise TransportPriorError(
                f"{path} is missing {missing}. The fit priors both parameters; a file "
                "carrying one would leave the other defaulted, and there is no default."
            )
        entries = {name: _check_entry(name, doc[name]) for name in PRIOR_NAMES}
        frozen = MappingProxyType({k: MappingProxyType(dict(v)) for k, v in entries.items()})
        return cls(entries=frozen, source_path=path)

    def __getitem__(self, name: str) -> Mapping[str, object]:
        return self.entries[name]

    def is_assumed(self, name: str) -> bool:
        return self.entries[name]["assumed"] is True

    def assumed_entries(self) -> tuple[str, ...]:
        """Which priors entered as explicit assumptions, for the provenance block."""
        return tuple(n for n in PRIOR_NAMES if self.is_assumed(n))


def scaffold_text() -> str:
    """S14's template: two entries, no numbers, both flagged assumed."""
    lines = [
        "# Transport-core MAP prior — SCAFFOLD for build-plan T28 (S14). HUMAN-OWNED.",
        "#",
        "# Copy this to configs/transport_prior.yaml and fill it. Both entries are",
        "# log-normal: write `mean_log` and `sigma_log` with the `citation` that supports",
        "# them, or state an explicitly uninformative prior and leave `assumed: true`.",
        "#",
        "# Read Finding E before treating this as a formality: at three reference",
        "# compounds the reported (alpha, k_sink) is substantially prior-determined, so",
        "# these numbers do real work on the M1 result. No agent filled them in.",
        "",
    ]
    for name in PRIOR_NAMES:
        lines += [
            f"{name}:",
            f"  # prior on {_PARAMETER_OF[name]}",
            "  mean_log:",
            "  sigma_log:",
            "  citation:",
            "  assumed: true",
            "",
        ]
    return "\n".join(lines).rstrip() + "\n"


def _carries_human_content(path: Path) -> bool:
    try:
        doc = yaml.safe_load(path.read_text())
    except yaml.YAMLError:
        return True
    if not isinstance(doc, dict):
        return bool(doc)
    for entry in doc.values():
        if not isinstance(entry, dict):
            if not _blank(entry):
                return True
            continue
        for key in ("mean_log", "sigma_log", "citation"):
            if not _blank(entry.get(key)):
                return True
    return False


def write_scaffold(path: Path, *, force: bool = False) -> Path:
    """Write S14's template to `path`, refusing to blank filled entries."""
    path = Path(path)
    if path.exists() and not force and _carries_human_content(path):
        raise TransportPriorTemplateError(
            f"refusing to overwrite {path}: it already carries filled prior entries. "
            "Pass force=True only to discard them deliberately."
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(scaffold_text(), encoding="utf-8")
    return path
