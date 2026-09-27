"""CTO #250 / #251: the label -> gene contract (aliases, structural controls, exclusions).

The fail-closed resolver refuses labels that are not vocabulary symbols. The
contract is the ONLY sanctioned way past it: an explicit alias table where every
entry carries evidence, a structural-control list, and an exclusion list. Every
fixture below is an explicit array; nothing is drawn at random.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import numpy as np
import pytest

from perturb_eval.data.label_contract import (
    ADAMSON_CONTRACT,
    NORMAN_CONTRACT,
    AliasEvidence,
    LabelAlias,
    LabelContract,
)

pytest.importorskip("anndata")
pytest.importorskip("scipy")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONTRACT_SRC = PROJECT_ROOT / "src" / "perturb_eval" / "data" / "label_contract.py"
APP_V05 = PROJECT_ROOT / "scripts" / "modal" / "app_v05.py"
# CTO #253: PERK/IRE1 are excluded with this exact text (3x is now a structural control).
PERK_REASON = (
    "alias not corroborated: target not detected in this subset (control mean 0.0) and the "
    "label pools multiple constructs; excluded rather than aliased."
)


# ---------------------------------------------------------------- evidence ----


def _kd(delta: float = -1.5, n: int = 3) -> AliasEvidence:
    return AliasEvidence(
        method="knockdown",
        n_labelled_cells=n,
        n_control_cells=6,
        mean_log_labelled=0.5,
        mean_log_control=0.5 - delta,
        delta=delta,
        delta_rank_among_genes=1,
    )


def _ens(ensembl_id: str = "ENSG00000172071") -> AliasEvidence:
    return AliasEvidence(
        method="ensembl_identity",
        ensembl_id=ensembl_id,
        source_dataset="fixture_source",
        source_symbol="OLDSYM",
        join_column="ensembl_id",
    )


class TestEvidenceIsMandatory:
    def test_alias_without_evidence_raises(self) -> None:
        with pytest.raises(ValueError, match="evidence"):
            LabelAlias(label="PERK", gene="EIF2AK3", basis="evidence_curated", evidence=())

    @pytest.mark.parametrize("delta", [0.0, 0.25])
    def test_knockdown_with_non_negative_delta_raises(self, delta: float) -> None:
        with pytest.raises(ValueError, match="delta"):
            _kd(delta=delta)

    def test_knockdown_with_no_labelled_cells_raises(self) -> None:
        with pytest.raises(ValueError, match="n_labelled_cells"):
            _kd(n=0)

    def test_knockdown_delta_must_match_means(self) -> None:
        with pytest.raises(ValueError, match="delta"):
            AliasEvidence(
                method="knockdown",
                n_labelled_cells=3,
                n_control_cells=6,
                mean_log_labelled=0.5,
                mean_log_control=2.0,
                delta=-0.2,
                delta_rank_among_genes=1,
            )

    @pytest.mark.parametrize("bad", ["", "ENSMUSG00000000001", "EIF2AK3", "ENSG123"])
    def test_ensembl_identity_requires_ensg_id(self, bad: str) -> None:
        with pytest.raises(ValueError, match="ENSG"):
            _ens(bad)

    def test_ensembl_identity_requires_join_column(self) -> None:
        with pytest.raises(ValueError, match="join_column"):
            AliasEvidence(
                method="ensembl_identity",
                ensembl_id="ENSG00000172071",
                source_dataset="d",
                source_symbol="S",
                join_column="",
            )

    def test_unknown_method_raises(self) -> None:
        with pytest.raises(ValueError, match="method"):
            AliasEvidence(method="literature")  # type: ignore[arg-type]

    def test_stable_id_join_needs_ensembl_identity_evidence(self) -> None:
        with pytest.raises(ValueError, match="ensembl_identity"):
            LabelAlias(label="PERK", gene="EIF2AK3", basis="stable_id_join", evidence=(_kd(),))

    def test_evidence_curated_needs_knockdown_evidence(self) -> None:
        with pytest.raises(ValueError, match="knockdown"):
            LabelAlias(label="OLDSYM", gene="NEWGENE", basis="evidence_curated", evidence=(_ens(),))

    def test_needs_principal_confirmation_only_for_evidence_curated(self) -> None:
        curated = LabelAlias(
            label="PERK", gene="EIF2AK3", basis="evidence_curated", evidence=(_kd(),)
        )
        joined = LabelAlias(
            label="OLDSYM", gene="NEWGENE", basis="stable_id_join", evidence=(_ens(),)
        )
        assert curated.needs_principal_confirmation is True
        assert joined.needs_principal_confirmation is False

    def test_whole_doublet_alias_cannot_be_constructed(self) -> None:
        # Aliases are per tuple component; a '_'-joined label is never an alias key.
        with pytest.raises(ValueError, match="component"):
            LabelAlias(
                label="OLDSYM_FOXL2", gene="NEWGENE", basis="evidence_curated", evidence=(_kd(),)
            )


class TestContractShape:
    def test_label_in_two_categories_raises(self) -> None:
        with pytest.raises(ValueError, match="more than one"):
            LabelContract(aliases={}, structural_controls={"X": "b"}, excluded={"X": "r"})

    def test_alias_key_must_match_alias_label(self) -> None:
        a = LabelAlias(label="PERK", gene="EIF2AK3", basis="evidence_curated", evidence=(_kd(),))
        with pytest.raises(ValueError, match="key"):
            LabelContract(aliases={"IRE1": a}, structural_controls={}, excluded={})

    def test_apply_is_control_is_excluded(self) -> None:
        a = LabelAlias(label="PERK", gene="EIF2AK3", basis="evidence_curated", evidence=(_kd(),))
        c = LabelContract(
            aliases={"PERK": a},
            structural_controls={"CTLX": "shape"},
            excluded={"XLBL": "fixture reason"},
        )
        assert c.apply("PERK") == "EIF2AK3"
        assert c.apply("TFA") == "TFA"
        assert c.is_control("CTLX") and not c.is_control("PERK")
        assert c.is_excluded("XLBL") and not c.is_excluded("PERK")

    def test_provenance_is_json_and_carries_every_evidence_field(self) -> None:
        a = LabelAlias(label="PERK", gene="EIF2AK3", basis="evidence_curated", evidence=(_kd(),))
        b = LabelAlias(label="OLDSYM", gene="NEWGENE", basis="stable_id_join", evidence=(_ens(),))
        prov = LabelContract(
            aliases={"PERK": a, "OLDSYM": b}, structural_controls={}, excluded={}
        ).to_provenance()
        assert json.loads(json.dumps(prov)) == prov
        perk = prov["aliases"]["PERK"]
        assert perk["gene"] == "EIF2AK3"
        assert perk["basis"] == "evidence_curated"
        assert perk["needs_principal_confirmation"] is True
        ev = perk["evidence"][0]
        for k in (
            "method",
            "n_labelled_cells",
            "n_control_cells",
            "mean_log_labelled",
            "mean_log_control",
            "delta",
            "delta_rank_among_genes",
        ):
            assert k in ev
        assert ev["delta"] == -1.5
        old = prov["aliases"]["OLDSYM"]
        assert old["basis"] == "stable_id_join"
        assert old["needs_principal_confirmation"] is False
        ev2 = old["evidence"][0]
        assert ev2["ensembl_id"] == "ENSG00000172071"
        assert ev2["join_column"] == "ensembl_id"
        assert ev2["source_dataset"] == "fixture_source"
        assert ev2["source_symbol"] == "OLDSYM"


class TestModuleConstants:
    def test_adamson_structural_control_basis(self) -> None:
        basis = ADAMSON_CONTRACT.structural_controls["Gal4-4(mod)"]
        assert "resolves to no gene" in basis
        assert "yeast" not in basis.lower()

    def test_adamson_excluded_with_exact_reason(self) -> None:
        # CTO #253 supersedes #250 ruling 3: 3x is a structural control now.
        assert ADAMSON_CONTRACT.excluded == {"PERK": PERK_REASON, "IRE1": PERK_REASON}
        assert "3x" in ADAMSON_CONTRACT.structural_controls

    def test_contract_tables_after_evidence_pass(self) -> None:
        assert dict(ADAMSON_CONTRACT.aliases) == {}
        assert set(NORMAN_CONTRACT.aliases) == {"C3orf72", "C19orf26"}
        assert dict(NORMAN_CONTRACT.structural_controls) == {}
        assert set(NORMAN_CONTRACT.excluded) == {"KIAA1804"}

    def test_composition_is_not_recorded(self) -> None:
        src = CONTRACT_SRC.read_text(encoding="utf-8")
        assert "ATF6" not in src
        assert "UPR" not in src


# ------------------------------------------------------------ h5ad fixtures ----

ADAMSON_GENES = ["EIF2AK3", "TFA", "TFB", "G3"]


def _write_adamson(path: Path, raw_labels: list[str], genes: list[str]) -> None:
    import anndata as ad
    from scipy.sparse import csr_matrix

    n = len(raw_labels)
    # Explicit values: row i is (i+1) * [1, 2, 3, 4] truncated to len(genes).
    base = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], dtype=np.float32)[: len(genes)]
    X = np.stack([base * (i + 1) for i in range(n)]).astype(np.float32)
    adata = ad.AnnData(
        X=csr_matrix(X),
        obs={"perturbation": np.array(raw_labels)},
        var={"gene_symbol": np.array(genes)},
    )
    adata.obs["perturbation"] = adata.obs["perturbation"].astype("category")
    adata.write_h5ad(path)


ADAMSON_CONTRACT_LABELS = (
    ["*"] * 3
    + ["62(mod)_pBA581"] * 2
    + ["Gal4-4(mod)_pBA582"] * 3
    + ["3x_neg_ctrl_pMJ144-1"] * 3
    + ["PERK_only_pMJ146"] * 3
    + ["TFA_pDS263"] * 3
)

ADAMSON_PERK_LABELS = ["*"] * 3 + ["TFA_pDS263"] * 3 + ["OLDTF_pDS100"] * 3
PERK_EXCLUDED = {
    "label": "PERK",
    "reason": PERK_REASON,
    "raw_labels": ["PERK_only_pMJ146"],
    "n_cells": 3,
}


def _perk_contract() -> LabelContract:
    # Mechanism fixture: an evidence_curated alias on a neutral label (OLDTF).
    return LabelContract(
        aliases={
            "OLDTF": LabelAlias(
                label="OLDTF", gene="EIF2AK3", basis="evidence_curated", evidence=(_kd(),)
            )
        },
        structural_controls=dict(ADAMSON_CONTRACT.structural_controls),
        excluded=dict(ADAMSON_CONTRACT.excluded),
    )


class TestAdamsonLoader:
    def test_structural_control_and_exclusion(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.e2_adamson import load_adamson_matrix

        p = tmp_path / "a.h5ad"
        _write_adamson(p, ADAMSON_CONTRACT_LABELS, ADAMSON_GENES)
        ds = load_adamson_matrix(p, max_cells_per_pert=100)
        # Gal4-4(mod) and 3x_neg_ctrl join the control mask; never tasks.
        assert "Gal4-4(mod)" not in ds["perturbations"]
        assert "Gal4-4(mod)" not in ds["target_gene_idx"]
        assert int(ds["control_mask"].sum()) == 3 + 2 + 3 + 3
        assert set(ds["labels"][ds["control_mask"]].tolist()) == {"CTRL"}
        assert "3x" not in ds["perturbations"]
        # PERK is dropped (cells and task) and reported.
        assert "PERK" not in ds["perturbations"]
        assert "PERK" not in ds["labels"].tolist()
        assert ds["X"].shape[0] == len(ADAMSON_CONTRACT_LABELS) - 3
        assert ds["labels_excluded"] == [PERK_EXCLUDED]
        assert ds["perturbations"] == ("TFA",)
        assert ds["label_contract"] == ADAMSON_CONTRACT.to_provenance()
        basis = ds["label_contract"]["structural_controls"]["Gal4-4(mod)"]
        assert "resolves to no gene" in basis

    def test_alias_resolves_to_gene_column_task_label_unchanged(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.e2_adamson import load_adamson_matrix

        p = tmp_path / "a.h5ad"
        _write_adamson(p, ADAMSON_PERK_LABELS, ADAMSON_GENES)
        ds = load_adamson_matrix(p, max_cells_per_pert=100, contract=_perk_contract())
        assert "OLDTF" in ds["perturbations"]
        assert "EIF2AK3" not in ds["perturbations"]
        assert ds["target_gene_idx"]["OLDTF"] == (ADAMSON_GENES.index("EIF2AK3"),)
        assert int((ds["labels"] == "OLDTF").sum()) == 3
        assert ds["label_contract"]["aliases"]["OLDTF"]["gene"] == "EIF2AK3"

    def test_unaliased_unknown_label_still_raises(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.e2_adamson import load_adamson_matrix

        p = tmp_path / "a.h5ad"
        _write_adamson(p, ADAMSON_PERK_LABELS, ADAMSON_GENES)
        with pytest.raises(ValueError, match="OLDTF"):
            load_adamson_matrix(p, max_cells_per_pert=100)

    def test_combined_loader_applies_contract(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.e2_adamson import load_adamson_combined

        p1, p2 = tmp_path / "a1.h5ad", tmp_path / "a2.h5ad"
        _write_adamson(p1, ADAMSON_CONTRACT_LABELS, ADAMSON_GENES)
        _write_adamson(p2, ADAMSON_PERK_LABELS + ["PERK_only_pMJ146"] * 2, ADAMSON_GENES)
        ds = load_adamson_combined([p1, p2], max_cells_per_pert=100, contract=_perk_contract())
        assert ds["target_gene_idx"]["OLDTF"] == (ADAMSON_GENES.index("EIF2AK3"),)
        assert set(ds["perturbations"]) == {"TFA", "OLDTF"}
        assert ds["labels_excluded"] == [{**PERK_EXCLUDED, "n_cells": 3 + 2}]
        assert "PERK" not in ds["labels"].tolist()
        assert "Gal4-4(mod)" not in ds["target_gene_idx"]
        assert ds["label_contract"] == _perk_contract().to_provenance()

    def test_combined_unaliased_unknown_still_raises(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.e2_adamson import load_adamson_combined

        p1 = tmp_path / "a1.h5ad"
        _write_adamson(p1, ADAMSON_PERK_LABELS, ADAMSON_GENES)
        with pytest.raises(ValueError, match="OLDTF"):
            load_adamson_combined([p1], max_cells_per_pert=100)

    def test_task_plan_never_draws_excluded_or_structural_control(self, tmp_path: Path) -> None:
        from perturb_eval.data.subsample import mean_abs_logfc_per_target
        from perturb_eval.experiments.e2_adamson import load_adamson_matrix
        from perturb_eval.experiments.v05_tasks import build_task_lists

        p = tmp_path / "a.h5ad"
        _write_adamson(p, ADAMSON_CONTRACT_LABELS, ADAMSON_GENES)
        ds = load_adamson_matrix(p, max_cells_per_pert=100)
        summary = {
            "adamson_full": mean_abs_logfc_per_target(
                ds["X"], ds["labels"], ds["control_mask"], ds["target_gene_idx"]
            )
        }
        plan = build_task_lists(
            summary,
            [],
            norman_n_singletons=0,
            norman_n_doublets=0,
            adamson_n_per_bin=1,
            adamson_n_bins=1,
            seed=0,
        )
        assert "3x" not in plan.all_tasks
        assert "PERK" not in plan.all_tasks
        assert "Gal4-4(mod)" not in plan.all_tasks
        assert plan.adamson == ("TFA",)


# ----------------------------------------------------------------- Norman ----

# Amendment 2 A2-4: build_provenance requires the trainer grid as run.
_GRID = {
    "backbones": ["linear"],
    "r_sweep": [1],
    "seeds": [0],
    "n_records_per_task": 1,
    "n_distinct_per_task": 1,
    "distinct_by_backbone": {"linear": 1},
    "r_seed_invariant_backbones": ["linear"],
}

NORMAN_GENES = ["NEWGENE", "FOXL2", "TGFBR2", "G3", "G4"]
NORMAN_LABELS = (
    ["non-targeting"] * 3
    + ["OLDSYM_FOXL2"] * 2
    + ["TGFBR2_OLDSYM"] * 2
    + ["OLDSYM"] * 2
    + ["FOXL2"] * 2
)


NEWGENE_ID = "ENSG00000172071"


def _write_norman(path: Path, labels: list[str], genes: list[str]) -> None:
    import anndata as ad
    from scipy.sparse import csr_matrix

    base = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32)[: len(genes)]
    X = np.stack([base * (i + 1) for i in range(len(labels))]).astype(np.float32)
    # 'ensemble_id' is the upstream spelling of the Norman stable-ID column.
    ids = [NEWGENE_ID if g == "NEWGENE" else f"ENSG{i:011d}" for i, g in enumerate(genes)]
    adata = ad.AnnData(
        X=csr_matrix(X),
        obs={"perturbation": np.array(labels)},
        var={"gene_symbol": np.array(genes), "ensemble_id": np.array(ids)},
    )
    adata.obs["perturbation"] = adata.obs["perturbation"].astype("category")
    adata.write_h5ad(path)


def _oldsym_contract(**extra) -> LabelContract:
    return LabelContract(
        aliases={
            "OLDSYM": LabelAlias(
                label="OLDSYM",
                gene="NEWGENE",
                basis="stable_id_join",
                evidence=(
                    AliasEvidence(
                        method="ensembl_identity",
                        ensembl_id=NEWGENE_ID,
                        source_dataset="fixture_source",
                        source_symbol="OLDSYM",
                        join_column="ensemble_id",
                    ),
                ),
            )
        },
        structural_controls={},
        excluded=extra.get("excluded", {}),
    )


class TestNormanPerComponentAlias:
    def test_doublet_alias_applies_per_component_both_orders(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.norman import load_norman_matrix

        p = tmp_path / "n.h5ad"
        _write_norman(p, NORMAN_LABELS, NORMAN_GENES)
        ds = load_norman_matrix(p, contract=_oldsym_contract())
        new, foxl2, tgfbr2 = (NORMAN_GENES.index(g) for g in ("NEWGENE", "FOXL2", "TGFBR2"))
        assert ds["target_gene_idx"]["OLDSYM_FOXL2"] == (new, foxl2)
        assert ds["target_gene_idx"]["TGFBR2_OLDSYM"] == (tgfbr2, new)
        assert ds["target_gene_idx"]["OLDSYM"] == (new,)
        assert ds["target_gene_idx"]["FOXL2"] == (foxl2,)
        # Task labels stay the original strings.
        assert set(ds["perturbations"]) == {"OLDSYM_FOXL2", "TGFBR2_OLDSYM", "OLDSYM", "FOXL2"}
        assert ds["labels_excluded"] == []
        assert ds["label_contract"] == _oldsym_contract().to_provenance()

    def test_unaliased_stale_component_still_raises(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.norman import load_norman_matrix

        p = tmp_path / "n.h5ad"
        _write_norman(p, NORMAN_LABELS, NORMAN_GENES)
        with pytest.raises(ValueError, match="OLDSYM"):
            load_norman_matrix(p)

    def test_default_contract_recorded(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.norman import load_norman_matrix

        p = tmp_path / "n.h5ad"
        _write_norman(p, ["non-targeting"] * 2 + ["FOXL2"] * 2, NORMAN_GENES)
        ds = load_norman_matrix(p)
        assert ds["label_contract"] == NORMAN_CONTRACT.to_provenance()
        assert ds["labels_excluded"] == []

    def test_excluded_whole_label_dropped(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.norman import load_norman_matrix

        p = tmp_path / "n.h5ad"
        _write_norman(p, NORMAN_LABELS, NORMAN_GENES)
        c = _oldsym_contract(excluded={"TGFBR2_OLDSYM": "fixture reason"})
        ds = load_norman_matrix(p, contract=c)
        assert "TGFBR2_OLDSYM" not in ds["perturbations"]
        assert "TGFBR2_OLDSYM" not in ds["labels"].tolist()
        assert ds["labels_excluded"] == [
            {
                "label": "TGFBR2_OLDSYM",
                "reason": "fixture reason",
                "raw_labels": ["TGFBR2_OLDSYM"],
                "n_cells": 2,
            }
        ]


# ------------------------------------------------------ preflight/provenance ----


def _pf_ds(contract: LabelContract, targets: dict, genes: tuple, excluded: list) -> dict:
    return {
        "X": np.zeros((2, len(genes))),
        "labels": np.array(["CTRL", "CTRL"]),
        "control_mask": np.array([True, True]),
        "target_gene_idx": targets,
        "perturbations": tuple(targets),
        "gene_names": genes,
        "label_contract": contract.to_provenance(),
        "labels_excluded": excluded,
    }


def _pf_run(tmp_path: Path, adamson_tasks: tuple, adamson_ds: dict, norman_ds: dict):
    from perturb_eval.experiments.v05_preflight import preflight
    from perturb_eval.experiments.v05_tasks import TaskPlan

    return preflight(
        # Principal directive + CTO #265: a runnable sweep supplies both.
        kwargs={
            "backbones": ("linear",),
            "doublet_delim": "_",
            "llm_key_source": {
                "store": "infisical",
                "project_slug": "syntropyhealth-app",
                "env": "dev",
                "home_project": "biofm",
                "cross_project": True,
            },
            "preregistration": {
                "path": "paper/PREREGISTRATION.md",
                "sha256": "a" * 64,
                "commit": "b" * 40,
            },
        },
        datasets_spec_or_loaded={"adamson_full": adamson_ds, "norman": norman_ds},
        task_plan=TaskPlan(
            adamson=adamson_tasks, norman_singletons=("OLDSYM",), norman_doublets=("OLDSYM_FOXL2",)
        ),
        env={"OPENROUTER_API_KEY": "sk-fixture-key-0123456789"},
        out_dir=tmp_path / "out",
        probe_fn=lambda env: "stub/model",
    )


def _pf_datasets():
    genes_a = ("EIF2AK3", "TFA")
    adamson = _pf_ds(_perk_contract(), {"OLDTF": (0,), "TFA": (1,)}, genes_a, [PERK_EXCLUDED])
    genes_n = ("NEWGENE", "FOXL2")
    norman = _pf_ds(_oldsym_contract(), {"OLDSYM": (0,), "OLDSYM_FOXL2": (0, 1)}, genes_n, [])
    return adamson, norman


class TestPreflightAndProvenance:
    def test_preflight_resolves_aliased_tasks_and_reports_contracts(self, tmp_path: Path) -> None:
        adamson, norman = _pf_datasets()
        rep = _pf_run(tmp_path, ("OLDTF", "TFA"), adamson, norman)
        assert rep.label_contracts == {
            "adamson_full": _perk_contract().to_provenance(),
            "norman": _oldsym_contract().to_provenance(),
        }
        assert rep.labels_excluded == ({"dataset": "adamson_full", **PERK_EXCLUDED},)

    def test_preflight_fails_if_plan_draws_excluded_label(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.v05_preflight import PreflightError

        adamson, norman = _pf_datasets()
        with pytest.raises(PreflightError, match="PERK"):
            _pf_run(tmp_path, ("OLDTF", "PERK"), adamson, norman)

    def test_build_provenance_carries_contract_and_exclusions(self) -> None:
        from perturb_eval.experiments import provenance as pv
        from perturb_eval.experiments.v05_tasks import TaskPlan

        contract = _perk_contract().to_provenance()
        kw = {n: 1 for n in pv.REQUIRED_ENTRYPOINT_KWARGS}
        prov = pv.build_provenance(
            run_id="r",
            git_sha="a" * 40,
            git_dirty=False,
            entrypoint_kwargs=kw,
            datasets=[
                {
                    "name": "adamson_full",
                    "path": "p",
                    "sha256": None,
                    "n_cells": 1,
                    "n_genes": 1,
                    "label_contract": contract,
                }
            ],
            task_plan=TaskPlan(adamson=("OLDTF",), norman_singletons=(), norman_doublets=()),
            tasks_excluded=[],
            labels_excluded=[{"dataset": "adamson_full", **PERK_EXCLUDED}],
            llm_pool=[],
            gpu="A100",
            hourly_usd=1.0,
            budget_cap_usd=1.0,
            lib_versions={},
            trainer_grid=_GRID,  # A2-4: required provenance block
        )
        assert prov["datasets"][0]["label_contract"] == contract
        assert {"dataset": "adamson_full", **PERK_EXCLUDED} in prov["tasks_excluded"]

    def test_build_provenance_rejects_exclusion_without_dataset(self) -> None:
        from perturb_eval.experiments import provenance as pv
        from perturb_eval.experiments.v05_tasks import TaskPlan

        kw = {n: 1 for n in pv.REQUIRED_ENTRYPOINT_KWARGS}
        with pytest.raises(ValueError, match="dataset"):
            pv.build_provenance(
                run_id="r",
                git_sha="a" * 40,
                git_dirty=False,
                entrypoint_kwargs=kw,
                datasets=[],
                task_plan=TaskPlan(adamson=("A",), norman_singletons=(), norman_doublets=()),
                tasks_excluded=[],
                labels_excluded=[{"label": "PERK", "reason": PERK_REASON}],
                llm_pool=[],
                gpu="A100",
                hourly_usd=1.0,
                budget_cap_usd=1.0,
                lib_versions={},
                trainer_grid=_GRID,  # A2-4: required provenance block
            )

    def test_build_provenance_rejects_malformed_label_contract(self) -> None:
        from perturb_eval.experiments import provenance as pv
        from perturb_eval.experiments.v05_tasks import TaskPlan

        kw = {n: 1 for n in pv.REQUIRED_ENTRYPOINT_KWARGS}
        with pytest.raises(ValueError, match="label_contract"):
            pv.build_provenance(
                run_id="r",
                git_sha="a" * 40,
                git_dirty=False,
                entrypoint_kwargs=kw,
                datasets=[
                    {
                        "name": "n",
                        "path": "p",
                        "sha256": None,
                        "n_cells": 1,
                        "n_genes": 1,
                        "label_contract": {"aliases": {}},
                    }
                ],
                task_plan=TaskPlan(adamson=("A",), norman_singletons=(), norman_doublets=()),
                tasks_excluded=[],
                llm_pool=[],
                gpu="A100",
                hourly_usd=1.0,
                budget_cap_usd=1.0,
                lib_versions={},
                trainer_grid=_GRID,  # A2-4: required provenance block
            )

    def test_app_v05_wires_contract_and_exclusions(self) -> None:
        src = APP_V05.read_text(encoding="utf-8")
        ast.parse(src)
        assert 'ds["label_contract"]' in src
        assert "labels_excluded=" in src
        assert '"guides_per_gene": ds["guides_per_gene"]' in src
