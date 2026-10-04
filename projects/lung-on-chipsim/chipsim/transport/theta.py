"""θ container and validator — build-plan T24, consuming S13's template.

Global Constraint #1: **no coding agent writes a biological number.** This module is
that rule's mechanical form for θ. It declares which fields the M1 fit reads and what
each is measured in, emits a template whose every value slot is empty, and refuses a
filled file in which any field is neither cited nor declared an assumption.

Three distinctions carry the contract, and each was a silent failure elsewhere in this
project before it was named here:

- **Absent is not unknown.** An empty `value` is an *incomplete* entry, never a
  default. Nothing here substitutes a number, because a substituted number is
  indistinguishable from a measured one once it is inside the fit.
- **Assumed is not cited.** A field no one can cite may still enter, but only flagged
  `assumed: true`. The flag is what makes it a stated gap (T1's "unsourced values
  flagged `assumed: true`" rule) rather than a quiet default, and it is what the run
  journal counts when it reports how much of θ was assumed.
- **Typed is not checked.** A unit declared in a schema and never compared against the
  file is decoration. Every entry's `unit` must equal the schema's, so a value entered
  in the wrong unit fails here rather than rescaling the fit.

**Naming.** The build plan (T24) specifies `ThetaConfig` in this module; the Stage 1
paper and the HACP decision ledger both cite the guard as `_require_sourced_theta` and
place it in `chipsim/transport/fit.py`. The guard lives here, next to the schema it
checks, and `fit.py` is expected to import it rather than redefine it — the one reading
that satisfies both names without a second copy of the rule. Reconciling the two
documents is a CTO item at the A1 branch cut.

**S6.** `configs/theta_priors.yaml` and `configs/assumptions.yaml` must not exist; their
absence is the enforcement mechanism (ruling r2.37(c)). The template writer therefore
refuses those two paths by name, and S13's scaffold lives at
`configs/templates/theta_priors.scaffold.yaml`, outside the guarded namespace.
"""

from __future__ import annotations

import numbers
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

import yaml

#: The literal the file's top-level mapping is keyed by.
THETA_ROOT = "theta"

#: S13's scaffold, relative to the project root. Outside `configs/` proper.
SCAFFOLD_RELPATH = Path("configs/templates/theta_priors.scaffold.yaml")

#: The two paths S6's absence guard owns. No writer in this package may create them.
S6_FORBIDDEN_RELPATHS = (
    Path("configs/theta_priors.yaml"),
    Path("configs/assumptions.yaml"),
)

#: The keys one entry may carry (S13). Anything else is a typo or a smuggled field.
ENTRY_KEYS = ("value", "unit", "citation", "assumed")


@dataclass(frozen=True)
class ThetaField:
    """One θ field: its name, its unit, its type, and why it is in the fit.

    `expected_citable` records whether the project believes a published value exists.
    It is a planning annotation and never an admissibility rule: a field annotated
    citable may still enter as an assumption, and one annotated otherwise may still
    arrive with a citation. Encoding it as a rule would let the schema decide a
    question only evidence can.
    """

    name: str
    unit: str
    kind: str  # "numeric" | "categorical"
    expected_citable: bool
    note: str


#: The six A&D §1 row-S5 fields the M1 fit reads, in the order the template emits them.
THETA_FIELDS: tuple[ThetaField, ...] = (
    ThetaField("flow_ul_min", "uL/min", "numeric", True, "channel flow rate"),
    ThetaField("membrane_um", "um", "numeric", True, "membrane thickness"),
    ThetaField("porosity", "fraction", "numeric", False, "membrane porosity"),
    ThetaField("strain_pct", "percent", "numeric", True, "cyclic strain amplitude"),
    ThetaField("area_mm2", "mm^2", "numeric", False, "exchange area"),
    ThetaField(
        "coating",
        "categorical",
        "categorical",
        True,
        "membrane coating, named as the source names it; not a measurement",
    ),
)

FIELD_NAMES: tuple[str, ...] = tuple(f.name for f in THETA_FIELDS)
_BY_NAME: Mapping[str, ThetaField] = MappingProxyType({f.name: f for f in THETA_FIELDS})


class ThetaError(RuntimeError):
    """A θ file or template operation violates T24's contract."""


class ThetaSourceError(ThetaError):
    """A θ field carries neither a citation nor `assumed: true`.

    Raised as its own type because this is the one constraint the validator exists for,
    and a caller may want to catch exactly it rather than every schema complaint.
    """


class ThetaTemplateError(ThetaError):
    """Writing a template would destroy human work, or land where no file may live."""


def _blank(value: object) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _is_numeric(value: object) -> bool:
    # bool is a numbers.Number; a strain of True is a typo, not a measurement.
    return isinstance(value, numbers.Number) and not isinstance(value, bool)


def _require_sourced_theta(entries: Mapping[str, Mapping[str, object]]) -> None:
    """Refuse any θ field that is neither cited nor declared an assumption.

    The name the Stage 1 paper and the HACP decision ledger both cite. Called last,
    after the schema is known good, so its message is never a side effect of a
    malformed file. Public alias: `require_sourced_theta`.
    """
    for name in FIELD_NAMES:
        entry = entries[name]
        if entry.get("assumed") is True:
            continue
        if _blank(entry.get("citation")):
            raise ThetaSourceError(
                f"θ field `{name}` carries a value with no `citation` and is not flagged "
                "`assumed: true`. No agent writes a biological number and no fit runs on "
                "one nobody stands behind: add the citation, or declare it an assumption "
                "so the run journal reports it as a stated gap."
            )


#: The guard under the name callers outside this package should use.
require_sourced_theta = _require_sourced_theta


def _check_entry(name: str, entry: object) -> dict:
    field = _BY_NAME[name]
    if not isinstance(entry, dict):
        raise ThetaError(f"θ field `{name}` is not a mapping; got {type(entry).__name__}.")

    unknown = sorted(set(entry) - set(ENTRY_KEYS))
    if unknown:
        raise ThetaError(
            f"θ field `{name}` carries unknown key(s) {unknown}. Permitted: "
            f"{list(ENTRY_KEYS)}. A permissive loader ignores a misspelled key, which is "
            "how `citaton:` passes for a citation."
        )

    if _blank(entry.get("value")):
        raise ThetaError(
            f"θ field `{name}` has an empty `value`. An absent value is incomplete, not a "
            "default: this loader substitutes nothing."
        )

    if field.kind == "numeric" and not _is_numeric(entry["value"]):
        raise ThetaError(
            f"θ field `{name}` expects a number in {field.unit}; got {entry['value']!r}. "
            "A quoted number is a string and would not scale."
        )
    if field.kind == "categorical" and not isinstance(entry["value"], str):
        raise ThetaError(
            f"θ field `{name}` expects a string naming the setting as its source names it; "
            f"got {type(entry['value']).__name__}."
        )

    declared = str(entry.get("unit") or "").strip()
    if declared != field.unit:
        raise ThetaError(
            f"θ field `{name}` declares unit {declared!r} but the schema requires "
            f"{field.unit!r}. A value entered in another unit fails here rather than "
            "rescaling the fit."
        )

    assumed = entry.get("assumed")
    if assumed not in (True, False, None):
        raise ThetaError(
            f"θ field `{name}` has `assumed: {assumed!r}`; it must be true or false. A "
            "truthy string would flag every field as assumed and silence the guard."
        )
    return {**entry, "assumed": assumed is True}


@dataclass(frozen=True)
class ThetaConfig:
    """A validated θ set, loaded from a human-written file (T24).

    Every field carries a unit and EITHER a value with a citation OR `assumed: true` —
    never silently absent. Construction is the only way to obtain one, and it raises on
    a field missing both, so there is no path through this module that yields θ the
    guard has not cleared. Instances are frozen and the mapping is read-only: the fit
    cannot adjust a prior it was handed.
    """

    entries: Mapping[str, Mapping[str, object]]
    source_path: Path

    @classmethod
    def load(cls, path: Path) -> ThetaConfig:
        path = Path(path)
        doc = yaml.safe_load(path.read_text())
        if not isinstance(doc, dict) or THETA_ROOT not in doc:
            raise ThetaError(f"{path} has no top-level `{THETA_ROOT}` mapping.")
        raw = doc[THETA_ROOT]
        if not isinstance(raw, dict):
            raise ThetaError(f"{path}: `{THETA_ROOT}` is not a mapping.")

        unknown = sorted(set(raw) - set(FIELD_NAMES))
        if unknown:
            raise ThetaError(
                f"{path} declares θ field(s) the fit does not read: {unknown}. "
                f"Permitted: {list(FIELD_NAMES)}."
            )
        missing = [n for n in FIELD_NAMES if n not in raw]
        if missing:
            raise ThetaError(
                f"{path} is missing θ field(s) {missing}. The fit reads all "
                f"{len(FIELD_NAMES)}; a partial file would fit a different model than the "
                "one the plan registered."
            )

        entries = {name: _check_entry(name, raw[name]) for name in FIELD_NAMES}
        _require_sourced_theta(entries)
        frozen = MappingProxyType({k: MappingProxyType(dict(v)) for k, v in entries.items()})
        return cls(entries=frozen, source_path=path)

    def __getitem__(self, name: str) -> Mapping[str, object]:
        return self.entries[name]

    def value(self, name: str) -> object:
        """The value of one field, by name."""
        return self.entries[name]["value"]

    def unit(self, name: str) -> str:
        return str(self.entries[name]["unit"])

    def is_assumed(self, name: str) -> bool:
        return self.entries[name]["assumed"] is True

    @property
    def cited_count(self) -> int:
        return sum(1 for n in FIELD_NAMES if not self.is_assumed(n))

    @property
    def assumed_count(self) -> int:
        return sum(1 for n in FIELD_NAMES if self.is_assumed(n))

    def assumed_fields(self) -> tuple[str, ...]:
        """The fields entering as stated gaps, for the run journal's provenance block.

        Reported, never asserted: a PoC in which two of six θ fields are assumed is a
        stated limitation, not a failure, and the reader is owed the list.
        """
        return tuple(n for n in FIELD_NAMES if self.is_assumed(n))


def load_theta_priors(path: Path) -> ThetaConfig:
    """Convenience wrapper over `ThetaConfig.load`, for callers that read as a verb."""
    return ThetaConfig.load(path)


def scaffold_text() -> str:
    """S13's template as text: six fields, every value empty, every unit declared.

    Declaring the field list and the units is schema work. Filling a value would be a
    biological number written by an agent, so every `value` and every `citation` below
    is empty and every field starts `assumed: true` — a stated gap until a human
    replaces it with a citation.
    """
    lines = [
        "# θ priors — SCAFFOLD for build-plan T20 (S13). No values: HUMAN-OWNED.",
        "#",
        "# Copy this to configs/theta_priors.yaml yourself and fill it. No agent step",
        "# creates that path: its absence is how Global Constraint #1 is enforced",
        "# (build-plan S6, ruling r2.37(c)).",
        "#",
        "# Per field: write `value` in the `unit` declared, and the `citation` that",
        "# supports it. Where no published value exists, leave `assumed: true` and no",
        "# citation — that is a stated gap the run journal reports, not an error.",
        "# chipsim.transport.theta.ThetaConfig.load refuses this file while any value is",
        "# empty, any unit differs from the schema, or any field is neither cited nor",
        "# flagged assumed. Nothing below was filled in by an agent.",
        "",
        f"{THETA_ROOT}:",
    ]
    for field in THETA_FIELDS:
        lines += [
            f"  {field.name}:",
            f"    # {field.note}",
            "    value:",
            f"    unit: {field.unit}",
            "    citation:",
            "    assumed: true",
            "",
        ]
    return "\n".join(lines).rstrip() + "\n"


def _carries_human_content(path: Path) -> bool:
    """True when an existing file has any filled value or citation.

    T13 learned this the expensive way: a routine re-emit that blanked human cells
    destroyed 60-90 minutes of literature work with no error (defect 22). The same
    re-emit here would destroy the θ entries, so the writer looks before it writes.
    An unparseable file counts as carrying content: refusing to judge it blank is the
    safe reading.
    """
    try:
        doc = yaml.safe_load(path.read_text())
    except yaml.YAMLError:
        return True
    if not isinstance(doc, dict):
        return bool(doc)
    for entry in (doc.get(THETA_ROOT) or {}).values():
        if not isinstance(entry, dict):
            if not _blank(entry):
                return True
            continue
        if not _blank(entry.get("value")) or not _blank(entry.get("citation")):
            return True
    return False


def write_scaffold(path: Path, *, force: bool = False) -> Path:
    """Write S13's template to `path`. Refuses S6's paths, and refuses to destroy work.

    `force` overwrites a file that already carries filled entries. It exists for the one
    legitimate case, regenerating a template nobody has started, and is a flag a person
    passes — never a default.
    """
    path = Path(path)
    resolved = path.resolve()
    for forbidden in S6_FORBIDDEN_RELPATHS:
        if resolved.parts[-len(forbidden.parts) :] == forbidden.parts:
            raise ThetaTemplateError(
                f"refusing to write {path}: `{forbidden.as_posix()}` is human-owned and "
                "its ABSENCE is the mechanical form of the rule that no agent writes a "
                "biological number (build-plan S6). The scaffold belongs at "
                f"{SCAFFOLD_RELPATH.as_posix()}."
            )
    if path.exists() and not force and _carries_human_content(path):
        raise ThetaTemplateError(
            f"refusing to overwrite {path}: it already carries filled θ entries. "
            "Re-emitting would blank a human's cited values with no error, which is "
            "defect 22's failure mode. Pass force=True only to discard them deliberately."
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(scaffold_text(), encoding="utf-8")
    return path
