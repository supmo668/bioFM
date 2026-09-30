"""T7 — perturbation label parsing (A4 / D1).

Norman doublets are ``_``-joined in the scPerturb bundle (``CBL_UBASH3A``);
the old loader tested ``"+"`` and silently fell back to a random gene index.
These helpers parse labels and resolve target columns, raising on any miss.
"""

from __future__ import annotations

import pytest

from perturb_eval.data.perturbations import (
    is_control,
    is_doublet,
    parse_perturbation,
    resolve_target_indices,
)


class TestParse:
    def test_doublet_underscore(self) -> None:
        assert parse_perturbation("CBL_UBASH3A") == ("CBL", "UBASH3A")

    def test_singleton_is_one_tuple(self) -> None:
        assert parse_perturbation("BAK1") == ("BAK1",)

    def test_custom_delim_honoured(self) -> None:
        assert parse_perturbation("A+B", delim="+") == ("A", "B")
        # With "+" as delim, an underscore is part of the symbol.
        assert parse_perturbation("A_B", delim="+") == ("A_B",)

    def test_parts_are_stripped(self) -> None:
        assert parse_perturbation(" CBL _ UBASH3A ") == ("CBL", "UBASH3A")

    @pytest.mark.parametrize("bad", ["", "   ", "A__B", "_A", "A_"])
    def test_empty_parts_raise(self, bad: str) -> None:
        with pytest.raises(ValueError):
            parse_perturbation(bad)


class TestIsDoublet:
    def test_doublet(self) -> None:
        assert is_doublet("CBL_UBASH3A") is True

    def test_singleton(self) -> None:
        assert is_doublet("BAK1") is False

    def test_custom_delim(self) -> None:
        assert is_doublet("A+B", delim="+") is True
        assert is_doublet("A_B", delim="+") is False

    def test_triplet_raises(self) -> None:
        with pytest.raises(ValueError, match="triplet|3 parts|Norman"):
            is_doublet("A_B_C")


class TestIsControl:
    @pytest.mark.parametrize(
        "label",
        ["ctrl", "control", "CTRL", "non-targeting", "nontargeting", "NT", "ntc", "NTC", "*", "62(mod)_pBA581"],
    )
    def test_loader_control_labels(self, label: str) -> None:
        assert is_control(label) is True

    @pytest.mark.parametrize("label", ["BAK1", "CBL_UBASH3A", "NTRK1", "CTRL1"])
    def test_non_controls(self, label: str) -> None:
        assert is_control(label) is False


class TestResolve:
    VOCAB = {"CBL": 7, "UBASH3A": 2, "BAK1": 11, "SAMD1": 0, "ZBTB1": 5}

    def test_indices_exact_in_label_order(self) -> None:
        out = resolve_target_indices(["CBL_UBASH3A", "BAK1", "UBASH3A_CBL"], self.VOCAB)
        assert out == {"CBL_UBASH3A": (7, 2), "BAK1": (11,), "UBASH3A_CBL": (2, 7)}

    def test_controls_skipped(self) -> None:
        out = resolve_target_indices(["ctrl", "BAK1", "non-targeting", "*"], self.VOCAB)
        assert out == {"BAK1": (11,)}

    def test_custom_delim(self) -> None:
        out = resolve_target_indices(["SAMD1+ZBTB1"], self.VOCAB, delim="+")
        assert out == {"SAMD1+ZBTB1": (0, 5)}

    def test_missing_gene_raises_with_label_and_gene(self) -> None:
        with pytest.raises(ValueError) as exc:
            resolve_target_indices(["BAK1", "CBL_FOXF1"], self.VOCAB)
        msg = str(exc.value)
        assert "CBL_FOXF1" in msg and "FOXF1" in msg
        assert str(len(self.VOCAB)) in msg

    def test_all_misses_listed(self) -> None:
        with pytest.raises(ValueError) as exc:
            resolve_target_indices(["XBP1", "CBL_FOXF1", "SRP72_ATF6"], self.VOCAB)
        msg = str(exc.value)
        for label, gene in [("XBP1", "XBP1"), ("CBL_FOXF1", "FOXF1"), ("SRP72_ATF6", "SRP72"), ("SRP72_ATF6", "ATF6")]:
            assert repr((label, gene)) in msg

    def test_never_substitutes(self) -> None:
        # A miss must never produce a partial/random mapping.
        with pytest.raises(ValueError):
            resolve_target_indices(["NOPE"], {"A": 0})
