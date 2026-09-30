"""CTO #253 (a-f + additions): structural Adamson construct parser + Norman stable-ID joins.

Fixture labels are the REAL raw ``obs.perturbation`` labels of the scPerturb
files (workstreams/perturb-seq-eval/qgr/evidence/raw-label-inventory.json.txt).
Expression values are explicit arrays; nothing is drawn at random.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("anndata")
pytest.importorskip("scipy")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONTRACT_SRC = PROJECT_ROOT / "src" / "perturb_eval" / "data" / "label_contract.py"

MULTI_GENE_REASON = "multi-gene construct; unsupported by D1"
PERK_IRE1_REASON = (
    "alias not corroborated: target not detected in this subset (control mean 0.0) and the "
    "label pools multiple constructs; excluded rather than aliased."
)
NAN_REASON = "missing perturbation annotation (raw label 'nan')"
KIAA1804_REASON = "target gene not locatable in the dataset vocabulary under either name"

# ---- real raw labels (full inventory) ------------------------------------------------

REAL_PILOT = [
    "*", "62(mod)_pBA581", "BHLHE40_pDS258", "CREB1_pDS269", "DDIT3_pDS263", "EP300_pDS268",
    "SNAI1_pDS266", "SPI1_pDS255", "ZNF326_pDS262",
]
# 10X005: all 21 labels; 'nan' is the missing-annotation category (code -1 in the h5ad).
REAL_10X005 = [
    "*", "3x_neg_ctrl_pMJ144-1", "3x_neg_ctrl_pMJ144-2", "ATF4_pBA576", "ATF6_IRE1_pMJ152",
    "ATF6_PERK_IRE1_pMJ158", "ATF6_PERK_pMJ150", "ATF6_only_pMJ145", "C7orf26_pDS004",
    "Gal4-4(mod)_pBA582", "IER3IP1_pDS003", "IRE1_only_pMJ148", "PERK_IRE1_pMJ154",
    "PERK_only_pMJ146", "PSMA1_pDS007", "PSMD12_pDS009", "SNAI1_pDS266", "XBP1_pBA578",
    "XBP1_pBA579", "YIPF5_pDS001",
]
REAL_10X010 = [
    "*", "62(mod)_pBA581", "63(mod)_pBA580", "AARS_pDS381", "AMIGO3_pDS434", "ARHGAP22_pDS458",
    "ASCC3_pDS051", "ASCC3_pDS052", "ATF4_pBA576", "ATF4_pBA577", "ATF4_pBA608", "ATF6_pBA586",
    "ATP5B_pDS055", "C7orf26_pDS004", "CAD_pDS468", "CARS_pDS460", "CCND3_pDS005",
    "CCND3_pDS006", "CHERP_pDS024", "COPB1_pDS065", "COPZ1_pDS462", "DAD1_pDS499",
    "DARS_pDS495", "DDOST_pDS382", "DDRGK1_pDS041", "DERL2_pDS042", "DHDDS_pDS383",
    "DNAJC19_pDS026", "DNAJC19_pDS074", "EIF2AK3_pBA572", "EIF2AK3_pBA573", "EIF2B2_pDS463",
    "EIF2B3_pDS508", "EIF2B4_pDS491", "EIF2S1_pDS386", "ERN1_pBA574", "ERN1_pBA575",
    "FARSB_pDS390", "FECH_pDS494", "GBF1_pDS043", "GBF1_pDS044", "GMPPB_pDS391",
    "GNPNAT1_pDS506", "Gal4-4(mod)_pBA582", "HARS_pDS466", "HSD17B12_pDS087", "HSPA5_pDS017",
    "HSPA5_pDS371", "HSPA9_pDS088", "HYOU1_pDS089", "IARS2_pDS090", "IARS2_pDS091",
    "IDH3A_pDS393", "IER3IP1_pDS002", "IER3IP1_pDS003", "IER3IP1_pDS110", "KCTD16_pDS096",
    "MANF_pDS027", "MARS_pDS394", "MRGBP_pDS124", "MRPL39_pDS498", "MTHFD1_pDS395",
    "NEDD8_pDS396", "OST4_pDS353", "P4HB_pDS397", "PDIA6_pDS029", "PPWD1_pDS398",
    "PSMA1_pDS007", "PSMD12_pDS008", "PSMD12_pDS009", "PSMD4_pDS488", "PTDSS1_pDS478",
    "QARS_pDS510", "SAMM50_pDS156", "SARS_pDS467", "SCYL1_pDS159", "SCYL1_pDS160",
    "SEC61A1_pDS031", "SEC61A1_pDS032", "SEC61B_pDS033", "SEC61B_pDS162", "SEC61G_pDS440",
    "SEC63_pDS218", "SEL1L_pDS373", "SLC35B1_pDS046", "SLC39A7_pDS219", "SLMO2_pDS433",
    "SOCS1_pDS479", "SPCS2_pDS401", "SPCS3_pDS402", "SRP68_pDS403", "SRP72_pDS505",
    "SRPRB_pDS404", "SRPR_pDS482", "STT3A_pDS010", "STT3A_pDS011", "SYVN1_pDS442",
    "TARS_pDS405", "TELO2_pDS496", "TIMM23_pDS284", "TIMM44_pDS430", "TMED10_pDS036",
    "TMED2_pDS175", "TMEM167A_pDS038", "TTI1_pDS407", "TTI2_pDS408", "UFL1_pDS410",
    "UFM1_pDS040", "XBP1_pBA578", "XBP1_pBA579", "XRN1_pDS411", "YIPF5_pDS001",
    "YIPF5_pDS186", "YIPF5_pDS226",
]

ATF6_CONSTRUCTS_10X005 = [
    "ATF6_only_pMJ145", "ATF6_IRE1_pMJ152", "ATF6_PERK_pMJ150", "ATF6_PERK_IRE1_pMJ158",
]
MULTI_GENE_10X005 = [
    "ATF6_IRE1_pMJ152", "ATF6_PERK_IRE1_pMJ158", "ATF6_PERK_pMJ150", "PERK_IRE1_pMJ154",
]


# ---------------------------------------------------------------- parser (a) ----

class TestParseAdamsonConstruct:
    def test_single_gene_with_plasmid(self) -> None:
        from perturb_eval.experiments.e2_adamson import parse_adamson_construct

        c = parse_adamson_construct("XBP1_pBA578")
        assert (c.raw, c.components, c.kind, c.plasmid) == (
            "XBP1_pBA578", ("XBP1",), "gene", "pBA578")

    def test_only_marker_stripped(self) -> None:
        from perturb_eval.experiments.e2_adamson import parse_adamson_construct

        c = parse_adamson_construct("ATF6_only_pMJ145")
        assert (c.components, c.kind, c.plasmid) == (("ATF6",), "gene", "pMJ145")

    @pytest.mark.parametrize("raw,comps", [
        ("ATF6_IRE1_pMJ152", ("ATF6", "IRE1")),
        ("ATF6_PERK_pMJ150", ("ATF6", "PERK")),
        ("ATF6_PERK_IRE1_pMJ158", ("ATF6", "PERK", "IRE1")),
        ("PERK_IRE1_pMJ154", ("PERK", "IRE1")),
    ])
    def test_multi_gene_components_as_written(self, raw: str, comps: tuple) -> None:
        from perturb_eval.experiments.e2_adamson import parse_adamson_construct

        c = parse_adamson_construct(raw)
        assert c.kind == "multi_gene"
        assert c.components == comps

    @pytest.mark.parametrize("raw,plasmid", [
        ("*", None),
        ("62(mod)_pBA581", "pBA581"),
        ("63(mod)_pBA580", "pBA580"),
        ("3x_neg_ctrl_pMJ144-1", "pMJ144-1"),
        ("3x_neg_ctrl_pMJ144-2", "pMJ144-2"),
        ("Gal4-4(mod)_pBA582", "pBA582"),
    ])
    def test_real_controls(self, raw: str, plasmid) -> None:
        from perturb_eval.experiments.e2_adamson import parse_adamson_construct

        c = parse_adamson_construct(raw)
        assert c.kind == "control"
        assert c.plasmid == plasmid

    @pytest.mark.parametrize("raw", [
        "nan", "", "TFA", "TFA_pds1", "ATF6_only_extra_pMJ1", "(odd)_pDS1", "A__B_pDS1",
        " TFA_pDS1", "only_pDS1",
    ])
    def test_unparseable_raises_naming_label(self, raw: str) -> None:
        from perturb_eval.experiments.e2_adamson import parse_adamson_construct

        with pytest.raises(ValueError) as exc:
            parse_adamson_construct(raw)
        assert repr(raw) in str(exc.value)

    def test_every_real_label_classifies(self) -> None:
        from perturb_eval.experiments.e2_adamson import parse_adamson_construct

        kinds: dict[str, set[str]] = {"gene": set(), "multi_gene": set(), "control": set()}
        for raw in dict.fromkeys(REAL_PILOT + REAL_10X005 + REAL_10X010):
            kinds[parse_adamson_construct(raw).kind].add(raw)
        assert kinds["control"] == {
            "*", "62(mod)_pBA581", "63(mod)_pBA580", "3x_neg_ctrl_pMJ144-1",
            "3x_neg_ctrl_pMJ144-2", "Gal4-4(mod)_pBA582",
        }
        assert kinds["multi_gene"] == set(MULTI_GENE_10X005)

    def test_old_normaliser_is_gone(self) -> None:
        from perturb_eval.experiments import e2_adamson

        assert not hasattr(e2_adamson, "_normalise_pert_label")


# ------------------------------------------------------- loader on real 10X005 ----

GENES_10X005 = [
    "ATF4", "ATF6", "C7orf26", "IER3IP1", "PSMA1", "PSMD12", "SNAI1", "XBP1", "YIPF5",
    "EIF2AK3", "ERN1", "G1",
]
CELLS_PER_LABEL = 2
N_NAN = 3


def _write_real_labels(path: Path, raw_labels: list[str], genes: list[str],
                       n_nan: int = N_NAN) -> None:
    """Every raw label gets CELLS_PER_LABEL cells; ``n_nan`` cells get a missing label."""
    import anndata as ad
    import pandas as pd
    from scipy.sparse import csr_matrix

    cells = [lbl for lbl in raw_labels for _ in range(CELLS_PER_LABEL)]
    obs_vals = cells + [None] * n_nan
    n = len(obs_vals)
    base = np.arange(1, len(genes) + 1, dtype=np.float32)
    X = np.stack([base * ((i % 7) + 1) for i in range(n)]).astype(np.float32)
    adata = ad.AnnData(
        X=csr_matrix(X),
        obs=pd.DataFrame({"perturbation": pd.Categorical(obs_vals, categories=sorted(raw_labels))},
                         index=[f"c{i}" for i in range(n)]),
        var=pd.DataFrame({"gene_symbol": genes}, index=[f"g{i}" for i in range(len(genes))]),
    )
    adata.write_h5ad(path)


@pytest.fixture
def ds_10x005(tmp_path: Path) -> dict:
    from perturb_eval.experiments.e2_adamson import load_adamson_matrix

    p = tmp_path / "Adamson2016_10X005.h5ad"
    _write_real_labels(p, REAL_10X005, GENES_10X005)
    return load_adamson_matrix(p, max_cells_per_pert=100)


class TestAdamsonLoaderReal10X005:
    def test_atf6_pools_only_the_single_gene_construct(self, ds_10x005: dict) -> None:
        # DF-07: before #253 the 'ATF6' task pooled all four ATF6_* constructs.
        ds = ds_10x005
        assert int((ds["labels"] == "ATF6").sum()) == CELLS_PER_LABEL
        assert ds["guides_per_gene"]["ATF6"] == ["pMJ145"]
        excluded = {e["label"]: e for e in ds["labels_excluded"]}
        for raw in MULTI_GENE_10X005:
            assert excluded[raw]["reason"] == MULTI_GENE_REASON
            assert excluded[raw]["raw_labels"] == [raw]
            assert excluded[raw]["n_cells"] == CELLS_PER_LABEL
            assert raw not in ds["labels"].tolist()

    def test_task_set(self, ds_10x005: dict) -> None:
        assert set(ds_10x005["perturbations"]) == {
            "ATF4", "ATF6", "C7orf26", "IER3IP1", "PSMA1", "PSMD12", "SNAI1", "XBP1", "YIPF5",
        }

    def test_same_gene_plasmids_pool_into_one_task(self, ds_10x005: dict) -> None:
        ds = ds_10x005
        assert ds["guides_per_gene"]["XBP1"] == ["pBA578", "pBA579"]
        assert int((ds["labels"] == "XBP1").sum()) == 2 * CELLS_PER_LABEL
        assert ds["target_gene_idx"]["XBP1"] == (GENES_10X005.index("XBP1"),)

    def test_controls(self, ds_10x005: dict) -> None:
        ds = ds_10x005
        # '*', 3x_neg_ctrl x2, Gal4-4(mod)
        assert int(ds["control_mask"].sum()) == 4 * CELLS_PER_LABEL
        assert set(ds["labels"][ds["control_mask"]].tolist()) == {"CTRL"}
        assert "3x" not in ds["perturbations"]

    def test_perk_ire1_excluded_with_exact_reason(self, ds_10x005: dict) -> None:
        excluded = {e["label"]: e for e in ds_10x005["labels_excluded"]}
        assert excluded["PERK"] == {"label": "PERK", "reason": PERK_IRE1_REASON,
                                    "raw_labels": ["PERK_only_pMJ146"],
                                    "n_cells": CELLS_PER_LABEL}
        assert excluded["IRE1"] == {"label": "IRE1", "reason": PERK_IRE1_REASON,
                                    "raw_labels": ["IRE1_only_pMJ148"],
                                    "n_cells": CELLS_PER_LABEL}
        assert "PERK" not in ds_10x005["perturbations"]

    def test_missing_annotation_excluded_with_cell_count(self, ds_10x005: dict) -> None:
        # h5ad categorical code -1 must never be read as the last category.
        ds = ds_10x005
        excluded = {e["label"]: e for e in ds["labels_excluded"]}
        assert excluded["nan"] == {"label": "nan", "reason": NAN_REASON,
                                   "raw_labels": ["nan"], "n_cells": N_NAN}
        assert "nan" not in ds["perturbations"]
        assert int((ds["labels"] == "YIPF5").sum()) == CELLS_PER_LABEL
        n_kept = (len(REAL_10X005) - 4 - 2) * CELLS_PER_LABEL
        assert ds["X"].shape[0] == n_kept

    def test_provenance_is_json(self, ds_10x005: dict) -> None:
        ds = ds_10x005
        json.dumps({"labels_excluded": ds["labels_excluded"],
                    "guides_per_gene": ds["guides_per_gene"],
                    "label_contract": ds["label_contract"]})

    def test_combined_loader_merges_guides_and_exclusions(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.e2_adamson import load_adamson_combined

        p1, p2 = tmp_path / "a.h5ad", tmp_path / "b.h5ad"
        _write_real_labels(p1, REAL_10X005, GENES_10X005)
        _write_real_labels(p2, ["*", "ATF6_pBA586", "XBP1_pBA578", "63(mod)_pBA580"],
                           GENES_10X005, n_nan=5)
        ds = load_adamson_combined([p1, p2], max_cells_per_pert=100)
        assert ds["guides_per_gene"]["ATF6"] == ["pBA586", "pMJ145"]
        assert ds["guides_per_gene"]["XBP1"] == ["pBA578", "pBA579"]
        nan = [e for e in ds["labels_excluded"] if e["label"] == "nan"]
        assert nan == [{"label": "nan", "reason": NAN_REASON, "raw_labels": ["nan"],
                        "n_cells": N_NAN + 5}]


class TestEligibleAdamsonGenes:
    def test_real_inventory_count(self) -> None:
        from perturb_eval.experiments.e2_adamson import eligible_adamson_genes

        genes = eligible_adamson_genes({
            "Adamson2016_pilot.h5ad": REAL_PILOT + ["nan"],
            "Adamson2016_10X005.h5ad": REAL_10X005 + ["nan"],
            "Adamson2016_10X010.h5ad": REAL_10X010 + ["nan"],
        })
        assert genes == sorted(set(genes))
        for g in ("PERK", "IRE1", "nan", "3x", "Gal4-4(mod)", "62(mod)", "63(mod)"):
            assert g not in genes
        assert "ATF6" in genes and "EIF2AK3" in genes and "ERN1" in genes
        assert len(genes) >= 21


# ---------------------------------------------------------- contract (d, e) ----

class TestAdamsonContract:
    def test_3x_is_structural_control(self) -> None:
        from perturb_eval.data.label_contract import ADAMSON_CONTRACT

        assert ADAMSON_CONTRACT.structural_controls["3x"] == (
            "label text classifies it as a negative-control construct ('3x_neg_ctrl'); "
            "resolves to no gene in the dataset vocabulary"
        )
        assert "3x" not in ADAMSON_CONTRACT.excluded
        assert "Gal4-4(mod)" in ADAMSON_CONTRACT.structural_controls

    def test_perk_ire1_excluded_verbatim(self) -> None:
        from perturb_eval.data.label_contract import ADAMSON_CONTRACT

        assert dict(ADAMSON_CONTRACT.excluded) == {"PERK": PERK_IRE1_REASON,
                                                   "IRE1": PERK_IRE1_REASON}
        assert dict(ADAMSON_CONTRACT.aliases) == {}

    def test_supersession_noted(self) -> None:
        import perturb_eval.data.label_contract as lc

        assert "#253 supersedes #250 ruling 3" in (lc.__doc__ or "")

    def test_no_claim_that_symbols_differ(self) -> None:
        src = CONTRACT_SRC.read_text(encoding="utf-8")
        assert "is not EIF2AK3" not in src
        assert "is not ERN1" not in src


# ------------------------------------------------------ Norman contract ----

class TestExpressionCrosscheck:
    def _xc(self, **kw):
        from perturb_eval.data.label_contract import AliasEvidence

        base = dict(method="expression_crosscheck", direction_expected="up", delta=0.3013,
                    delta_rank_among_genes=33690, n_genes=33694, verdict="corroborated")
        base.update(kw)
        return AliasEvidence(**base)

    def test_valid(self) -> None:
        ev = self._xc()
        assert ev.verdict == "corroborated"

    @pytest.mark.parametrize("kw", [
        {"direction_expected": "sideways"},
        {"verdict": "maybe"},
        {"delta_rank_among_genes": 0},
        {"delta_rank_among_genes": 33695},
        {"n_genes": 0},
        {"delta": float("nan")},
        {"delta": -0.3, "verdict": "corroborated"},  # corroborated needs the expected sign
    ])
    def test_invalid_raises(self, kw: dict) -> None:
        with pytest.raises(ValueError):
            self._xc(**kw)

    def test_crosscheck_cannot_stand_in_for_join_or_knockdown(self) -> None:
        from perturb_eval.data.label_contract import LabelAlias

        with pytest.raises(ValueError, match="ensembl_identity"):
            LabelAlias(label="C19orf26", gene="CBARP", basis="stable_id_join",
                       evidence=(self._xc(),))
        with pytest.raises(ValueError, match="knockdown"):
            LabelAlias(label="C19orf26", gene="CBARP", basis="evidence_curated",
                       evidence=(self._xc(),))


class TestNormanContract:
    def test_aliases(self) -> None:
        from perturb_eval.data.label_contract import NORMAN_CONTRACT

        a = NORMAN_CONTRACT.aliases
        assert {k: v.gene for k, v in a.items()} == {"C3orf72": "FOXL2NB", "C19orf26": "CBARP"}
        for label, ensg in (("C3orf72", "ENSG00000206262"), ("C19orf26", "ENSG00000099625")):
            assert a[label].basis == "stable_id_join"
            ens = [e for e in a[label].evidence if e.method == "ensembl_identity"]
            assert len(ens) == 1
            assert ens[0].ensembl_id == ensg
            assert ens[0].join_column == "ensemble_id"
            assert ens[0].source_dataset == "Adamson2016_*.h5ad"
            assert ens[0].source_symbol == label

    def test_crosscheck_values(self) -> None:
        from perturb_eval.data.label_contract import NORMAN_CONTRACT

        def xc(label):
            (e,) = [e for e in NORMAN_CONTRACT.aliases[label].evidence
                    if e.method == "expression_crosscheck"]
            return e

        cbarp, foxl2nb = xc("C19orf26"), xc("C3orf72")
        assert cbarp.direction_expected == "up" and foxl2nb.direction_expected == "up"
        assert cbarp.delta == pytest.approx(0.301, abs=1e-3)
        assert (cbarp.delta_rank_among_genes, cbarp.n_genes) == (33690, 33694)
        assert cbarp.verdict == "corroborated"
        assert foxl2nb.delta == pytest.approx(0.006, abs=1e-3)
        assert (foxl2nb.delta_rank_among_genes, foxl2nb.n_genes) == (29770, 33694)
        assert foxl2nb.verdict == "inconclusive"

    def test_provenance_wording_and_inconclusive_never_corroborated(self) -> None:
        from perturb_eval.data.label_contract import NORMAN_CONTRACT

        prov = NORMAN_CONTRACT.to_provenance()
        assert json.loads(json.dumps(prov)) == prov
        foxl2nb = prov["aliases"]["C3orf72"]
        assert foxl2nb["corroboration"] == "join structural, expression cross-check inconclusive"
        assert foxl2nb["basis"] == "stable_id_join"
        assert "corroborated" not in json.dumps(foxl2nb)
        cbarp = prov["aliases"]["C19orf26"]
        assert cbarp["corroboration"] == "join structural, expression cross-check corroborated"
        assert cbarp["basis"] == "stable_id_join"

    def test_kiaa1804_excluded(self) -> None:
        from perturb_eval.data.label_contract import NORMAN_CONTRACT

        assert dict(NORMAN_CONTRACT.excluded) == {"KIAA1804": KIAA1804_REASON}
        assert dict(NORMAN_CONTRACT.structural_controls) == {}


NORMAN_GENES = ["FOXL2NB", "FOXL2", "TGFBR2", "CBARP", "G5"]
NORMAN_IDS = ["ENSG00000206262", "ENSG00000183770", "ENSG00000163513", "ENSG00000099625",
              "ENSG00000000005"]
NORMAN_REAL_LABELS = (
    ["control"] * 2 + ["C3orf72_FOXL2"] * 2 + ["TGFBR2_C19orf26"] * 2 + ["C3orf72"] * 2
    + ["C19orf26"] * 2 + ["KIAA1804"] * 3 + ["FOXL2"] * 2
)


def _write_norman(path: Path, labels: list[str], id_column: str = "ensemble_id",
                  ids: list[str] = NORMAN_IDS) -> None:
    import anndata as ad
    import pandas as pd
    from scipy.sparse import csr_matrix

    base = np.arange(1, len(NORMAN_GENES) + 1, dtype=np.float32)
    X = np.stack([base * (i + 1) for i in range(len(labels))]).astype(np.float32)
    adata = ad.AnnData(
        X=csr_matrix(X),
        obs=pd.DataFrame({"perturbation": pd.Categorical(labels)},
                         index=[f"c{i}" for i in range(len(labels))]),
        var=pd.DataFrame({"gene_symbol": NORMAN_GENES, id_column: ids},
                         index=[f"g{i}" for i in range(len(NORMAN_GENES))]),
    )
    adata.write_h5ad(path)


class TestNormanLoaderStableIdJoin:
    def test_real_doublets_resolve_per_component(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.norman import load_norman_matrix

        p = tmp_path / "n.h5ad"
        _write_norman(p, NORMAN_REAL_LABELS)
        ds = load_norman_matrix(p)
        col = {g: i for i, g in enumerate(NORMAN_GENES)}
        tgi = ds["target_gene_idx"]
        assert tgi["C3orf72_FOXL2"] == (col["FOXL2NB"], col["FOXL2"])
        assert tgi["TGFBR2_C19orf26"] == (col["TGFBR2"], col["CBARP"])
        assert tgi["C3orf72"] == (col["FOXL2NB"],)
        assert tgi["C19orf26"] == (col["CBARP"],)
        assert "KIAA1804" not in ds["perturbations"]
        assert ds["labels_excluded"] == [{"label": "KIAA1804", "reason": KIAA1804_REASON,
                                          "raw_labels": ["KIAA1804"], "n_cells": 3}]

    def test_missing_ensemble_id_column_raises_naming_expected_and_found(
        self, tmp_path: Path
    ) -> None:
        from perturb_eval.experiments.norman import load_norman_matrix

        p = tmp_path / "n.h5ad"
        _write_norman(p, NORMAN_REAL_LABELS, id_column="ensembl_id")
        with pytest.raises(ValueError) as exc:
            load_norman_matrix(p)
        msg = str(exc.value)
        assert "'ensemble_id'" in msg
        assert "ensembl_id" in msg and "gene_symbol" in msg

    def test_id_mismatch_raises(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.norman import load_norman_matrix

        p = tmp_path / "n.h5ad"
        bad = list(NORMAN_IDS)
        bad[NORMAN_GENES.index("CBARP")] = "ENSG00000000099"
        _write_norman(p, NORMAN_REAL_LABELS, ids=bad)
        with pytest.raises(ValueError, match="CBARP"):
            load_norman_matrix(p)

    def test_column_not_required_when_no_alias_used(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.norman import load_norman_matrix

        p = tmp_path / "n.h5ad"
        _write_norman(p, ["control"] * 2 + ["FOXL2"] * 2, id_column="ensembl_id")
        ds = load_norman_matrix(p)
        assert ds["perturbations"] == ("FOXL2",)
