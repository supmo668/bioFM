"""Label -> gene contract for perturbation labels (CTO #250, #251).

The fail-closed resolver (:func:`perturb_eval.data.perturbations.resolve_target_indices`)
refuses any label that is not a symbol in the dataset's gene vocabulary. A
:class:`LabelContract` is the only sanctioned way past it, and it is an explicit
table, never a fuzzy match:

* ``aliases`` — ``label -> gene``. Every entry carries :class:`AliasEvidence`;
  an alias without evidence cannot be constructed. Two bases exist:
  ``stable_id_join`` (a structural join — the label symbol's Ensembl ID in one
  dataset's ``var`` equals the gene's Ensembl ID in the target dataset's
  ``var``) and ``evidence_curated`` (a measured knockdown of the gene's own
  column in the labelled cells; used only when no stable-ID join exists, and
  flagged ``needs_principal_confirmation``).
* ``structural_controls`` — ``label -> basis``: labels that join the control
  mask, with the recorded structural reason.
* ``excluded`` — ``label -> reason``: labels dropped from the task pool (and
  their cells from the matrix), reported as ``ds["labels_excluded"]``.

Aliases are applied PER TUPLE COMPONENT: a ``_``-joined doublet has each
component looked up on its own, so an alias key is always a single component.

Rule of evidence: an entry records only what the code and the data demonstrate.
"""

from __future__ import annotations

import math
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, fields
from types import MappingProxyType
from typing import Any, Literal

from perturb_eval.data.perturbations import parse_perturbation, resolve_target_indices

AliasMethod = Literal["knockdown", "ensembl_identity"]
AliasBasis = Literal["stable_id_join", "evidence_curated"]

_METHODS: frozenset[str] = frozenset({"knockdown", "ensembl_identity"})
_BASES: frozenset[str] = frozenset({"stable_id_join", "evidence_curated"})
_ENSG_RE = re.compile(r"ENSG\d{11}(\.\d+)?")
_KNOCKDOWN_FIELDS = (
    "n_labelled_cells",
    "n_control_cells",
    "mean_log_labelled",
    "mean_log_control",
    "delta",
    "delta_rank_among_genes",
)
_ENSEMBL_FIELDS = ("ensembl_id", "source_dataset", "source_symbol", "join_column")
# |delta - (mean_log_labelled - mean_log_control)| tolerance (rounded evidence).
_DELTA_ABS_TOL = 1e-4
# Component delimiter the loaders use for doublets; an alias key never contains it.
COMPONENT_DELIM = "_"


def _fail(msg: str) -> None:
    raise ValueError(msg)


def _is_int(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _is_finite(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


@dataclass(frozen=True)
class AliasEvidence:
    """One piece of evidence for an alias. Invalid evidence raises ``ValueError``.

    ``method="knockdown"``: in the labelled cells the candidate gene's own
    column is lower than in control cells — ``delta = mean_log_labelled -
    mean_log_control < 0`` over ``n_labelled_cells > 0`` cells, with
    ``delta_rank_among_genes`` (1 = most negative delta of all genes).

    ``method="ensembl_identity"``: ``source_symbol``'s Ensembl ID in
    ``source_dataset``'s ``var[join_column]`` is ``ensembl_id`` (``ENSG...``),
    equal to the candidate gene's ID in the target dataset.
    """

    method: AliasMethod
    # knockdown
    n_labelled_cells: int | None = None
    n_control_cells: int | None = None
    mean_log_labelled: float | None = None
    mean_log_control: float | None = None
    delta: float | None = None
    delta_rank_among_genes: int | None = None
    # ensembl_identity
    ensembl_id: str | None = None
    source_dataset: str | None = None
    source_symbol: str | None = None
    join_column: str | None = None

    def __post_init__(self) -> None:
        if self.method not in _METHODS:
            _fail(f"AliasEvidence.method must be one of {sorted(_METHODS)}, got {self.method!r}")
        own, other = (
            (_KNOCKDOWN_FIELDS, _ENSEMBL_FIELDS)
            if self.method == "knockdown"
            else (_ENSEMBL_FIELDS, _KNOCKDOWN_FIELDS)
        )
        stray = [f for f in other if getattr(self, f) is not None]
        if stray:
            _fail(f"{self.method} evidence must not set {stray}")
        missing = [f for f in own if getattr(self, f) is None]
        if missing:
            _fail(f"{self.method} evidence is missing {missing}")
        if self.method == "knockdown":
            self._validate_knockdown()
        else:
            self._validate_ensembl()

    def _validate_knockdown(self) -> None:
        if not _is_int(self.n_labelled_cells) or self.n_labelled_cells <= 0:  # type: ignore[operator]
            _fail(f"knockdown n_labelled_cells must be an int > 0, got {self.n_labelled_cells!r}")
        if not _is_int(self.n_control_cells) or self.n_control_cells <= 0:  # type: ignore[operator]
            _fail(f"knockdown n_control_cells must be an int > 0, got {self.n_control_cells!r}")
        for f in ("mean_log_labelled", "mean_log_control", "delta"):
            if not _is_finite(getattr(self, f)):
                _fail(f"knockdown {f} must be a finite number, got {getattr(self, f)!r}")
        if not self.delta < 0:  # type: ignore[operator]
            _fail(f"knockdown delta must be < 0 (a knockdown lowers the gene), got {self.delta!r}")
        implied = self.mean_log_labelled - self.mean_log_control  # type: ignore[operator]
        if not math.isclose(self.delta, implied, rel_tol=1e-6, abs_tol=_DELTA_ABS_TOL):  # type: ignore[arg-type]
            _fail(
                f"knockdown delta={self.delta!r} != mean_log_labelled - mean_log_control "
                f"= {implied!r}"
            )
        rank = self.delta_rank_among_genes
        if not _is_int(rank) or rank < 1:  # type: ignore[operator]
            _fail(f"knockdown delta_rank_among_genes must be an int >= 1, got {rank!r}")

    def _validate_ensembl(self) -> None:
        if not isinstance(self.ensembl_id, str) or not _ENSG_RE.fullmatch(self.ensembl_id):
            _fail(f"ensembl_identity needs a human ENSG... gene id, got {self.ensembl_id!r}")
        for f in ("source_dataset", "source_symbol", "join_column"):
            v = getattr(self, f)
            if not isinstance(v, str) or not v.strip():
                _fail(f"ensembl_identity {f} must be a non-empty str, got {v!r}")

    def to_dict(self) -> dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self)}


@dataclass(frozen=True)
class LabelAlias:
    """``label -> gene`` with its basis and non-empty evidence (else ``ValueError``).

    ``stable_id_join`` requires >= 1 ``ensembl_identity`` evidence;
    ``evidence_curated`` requires >= 1 ``knockdown`` evidence and is the only
    basis that ``needs_principal_confirmation``.
    """

    label: str
    gene: str
    basis: AliasBasis
    evidence: tuple[AliasEvidence, ...]

    def __post_init__(self) -> None:
        for name in ("label", "gene"):
            v = getattr(self, name)
            if not isinstance(v, str) or not v.strip() or v != v.strip():
                _fail(f"LabelAlias.{name} must be a non-empty, unpadded str, got {v!r}")
        for name in ("label", "gene"):
            if COMPONENT_DELIM in getattr(self, name):
                _fail(
                    f"LabelAlias.{name}={getattr(self, name)!r} contains {COMPONENT_DELIM!r}: "
                    "aliases apply per tuple component, never to a whole joined label"
                )
        if self.label == self.gene:
            _fail(f"LabelAlias {self.label!r} maps to itself")
        if self.basis not in _BASES:
            _fail(f"LabelAlias.basis must be one of {sorted(_BASES)}, got {self.basis!r}")
        ev = tuple(self.evidence) if self.evidence is not None else ()
        object.__setattr__(self, "evidence", ev)
        if not ev:
            _fail(f"LabelAlias {self.label!r} -> {self.gene!r} has no evidence; "
                  "an alias without evidence cannot be constructed")
        if not all(isinstance(e, AliasEvidence) for e in ev):
            _fail(f"LabelAlias {self.label!r} evidence must be AliasEvidence instances")
        methods = {e.method for e in ev}
        if self.basis == "stable_id_join" and "ensembl_identity" not in methods:
            _fail(f"LabelAlias {self.label!r}: basis stable_id_join needs at least one "
                  "ensembl_identity evidence")
        if self.basis == "evidence_curated" and "knockdown" not in methods:
            _fail(f"LabelAlias {self.label!r}: basis evidence_curated needs at least one "
                  "knockdown evidence")

    @property
    def needs_principal_confirmation(self) -> bool:
        return self.basis == "evidence_curated"

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "gene": self.gene,
            "basis": self.basis,
            "needs_principal_confirmation": self.needs_principal_confirmation,
            "evidence": [e.to_dict() for e in self.evidence],
        }


def _str_map(m: Mapping[str, str], what: str) -> Mapping[str, str]:
    out: dict[str, str] = {}
    for k, v in dict(m).items():
        if not isinstance(k, str) or not k.strip():
            _fail(f"{what} label must be a non-empty str, got {k!r}")
        if not isinstance(v, str) or not v.strip():
            _fail(f"{what}[{k!r}] must be a non-empty str")
        out[k] = v
    return MappingProxyType(out)


@dataclass(frozen=True)
class LabelContract:
    """Explicit label table: aliases, structural controls, exclusions (disjoint)."""

    aliases: Mapping[str, LabelAlias]
    structural_controls: Mapping[str, str]
    excluded: Mapping[str, str]

    def __post_init__(self) -> None:
        aliases = dict(self.aliases)
        for key, alias in aliases.items():
            if not isinstance(alias, LabelAlias):
                _fail(f"aliases[{key!r}] must be a LabelAlias")
            if key != alias.label:
                _fail(f"aliases key {key!r} != alias.label {alias.label!r}")
        controls = _str_map(self.structural_controls, "structural_controls")
        excluded = _str_map(self.excluded, "excluded")
        seen: dict[str, str] = {}
        for cat, keys in (("aliases", aliases), ("structural_controls", controls),
                          ("excluded", excluded)):
            for k in keys:
                if k in seen:
                    _fail(f"label {k!r} is in more than one category ({seen[k]}, {cat})")
                seen[k] = cat
        object.__setattr__(self, "aliases", MappingProxyType(aliases))
        object.__setattr__(self, "structural_controls", controls)
        object.__setattr__(self, "excluded", excluded)

    def apply(self, label: str) -> str:
        """The alias gene for a single component ``label``, else ``label`` itself."""
        alias = self.aliases.get(label)
        return alias.gene if alias is not None else label

    def gene_label(self, label: str, delim: str = COMPONENT_DELIM) -> str:
        """``label`` with :meth:`apply` run on EACH ``delim``-joined component."""
        return delim.join(self.apply(c) for c in parse_perturbation(label, delim))

    def is_control(self, label: str) -> bool:
        return label in self.structural_controls

    def is_excluded(self, label: str) -> bool:
        return label in self.excluded

    def to_provenance(self) -> dict[str, Any]:
        """JSON-serialisable record of the whole contract, every evidence field included."""
        return {
            "aliases": {k: self.aliases[k].to_dict() for k in sorted(self.aliases)},
            "structural_controls": {k: self.structural_controls[k]
                                    for k in sorted(self.structural_controls)},
            "excluded": {k: self.excluded[k] for k in sorted(self.excluded)},
        }


PROVENANCE_KEYS: tuple[str, ...] = ("aliases", "structural_controls", "excluded")


def alias_genes_from_provenance(prov: Mapping[str, Any]) -> dict[str, str]:
    """``{label: gene}`` from a :meth:`LabelContract.to_provenance` record."""
    missing = [k for k in PROVENANCE_KEYS if k not in prov]
    if missing:
        _fail(f"label_contract provenance is missing {missing}")
    return {str(k): str(v["gene"]) for k, v in dict(prov["aliases"]).items()}


def gene_label_from_provenance(
    label: str, prov: Mapping[str, Any], delim: str = COMPONENT_DELIM
) -> str:
    """Per-component alias of ``label`` using a provenance record (preflight side)."""
    genes = alias_genes_from_provenance(prov)
    return delim.join(genes.get(c, c) for c in parse_perturbation(label, delim))


def resolve_with_contract(
    perturbations: Iterable[str],
    gene_to_idx: Mapping[str, int],
    contract: LabelContract,
    *,
    delim: str = COMPONENT_DELIM,
) -> dict[str, tuple[int, ...]]:
    """:func:`resolve_target_indices` after per-component aliasing, keyed by TASK label.

    The task label stays the original string; only the gene lookup is aliased.
    Anything still absent from the vocabulary raises (unchanged fail-closed).
    """
    labels = list(perturbations)
    gene_labels = {lbl: contract.gene_label(lbl, delim) for lbl in labels}
    resolved = resolve_target_indices(list(dict.fromkeys(gene_labels.values())),
                                      gene_to_idx, delim=delim)
    return {lbl: resolved[g] for lbl, g in gene_labels.items() if g in resolved}


ADAMSON_EXCLUDED_3X_REASON = (
    "multi-target construct; composition unconfirmed; triplets unsupported by D1"
)

ADAMSON_CONTRACT = LabelContract(
    aliases={},  # filled from the evidence pass (CTO #250/#251)
    structural_controls={
        "Gal4-4(mod)": (
            "resolves to no gene in the dataset vocabulary; matches the existing "
            "control-construct label shape handled by _is_control"
        ),
    },
    excluded={"3x": ADAMSON_EXCLUDED_3X_REASON},
)

NORMAN_CONTRACT = LabelContract(aliases={}, structural_controls={}, excluded={})


__all__ = [
    "ADAMSON_CONTRACT",
    "ADAMSON_EXCLUDED_3X_REASON",
    "COMPONENT_DELIM",
    "NORMAN_CONTRACT",
    "PROVENANCE_KEYS",
    "AliasEvidence",
    "LabelAlias",
    "LabelContract",
    "alias_genes_from_provenance",
    "gene_label_from_provenance",
    "resolve_with_contract",
]
