"""The COMMITTED label/structure reference table is usable — QG F-03.

Every other label test loads a synthetic table in tmp_path, so nothing checked the file the
worksheet actually reads. Measured against the snapshot, two committed entries carried
CHARGED-form InChIKeys (ending `-L` and `-K`). Pipeline keys are neutralised and always end in
`-N`, so those entries could never match: the snapshot row labelled "L-Phospholactate", whose
structure is the D form, reported `unresolved` where it should report `disagrees`.

The loader also let a repeated `base_name` silently overwrite the earlier entry, and never
checked that an entry's L and D keys differ — equal keys would make every row on that base name
read `agrees`, the one verdict the tri-state column must never produce falsely.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from chipsim.harmonize.label_reference import LabelReferenceError, load_label_reference

PROJECT_ROOT = Path(__file__).resolve().parent.parent
COMMITTED = PROJECT_ROOT / "configs" / "label_structure_reference.yaml"


def test_the_committed_table_loads_with_every_entry():
    doc = yaml.safe_load(COMMITTED.read_text(encoding="utf-8"))
    reference = load_label_reference(COMMITTED)
    assert len(doc["entries"]) >= 40, "anti-vacuity: the committed table must not be near-empty"
    assert len(reference.entries) == len(doc["entries"]), "a base name was silently overwritten"


def test_every_committed_key_is_neutral_so_it_can_match_a_pipeline_key():
    reference = load_label_reference(COMMITTED)
    charged = [
        (base, form, key)
        for base, keys in reference.entries.items()
        for form, key in keys.items()
        if not key.endswith("-N")
    ]
    assert charged == [], f"charged-form keys can never match a neutralised pipeline key: {charged}"


def test_every_committed_entry_has_distinct_l_and_d_keys_sharing_a_skeleton():
    reference = load_label_reference(COMMITTED)
    for base, keys in reference.entries.items():
        assert keys["l_inchikey"] != keys["d_inchikey"], f"{base}: L and D keys are equal"
        assert keys["l_inchikey"].split("-")[0] == keys["d_inchikey"].split("-")[0], base


def _table(tmp_path: Path, entries: list[dict]) -> Path:
    path = tmp_path / "ref.yaml"
    path.write_text(
        yaml.safe_dump({"retrieved_on": "2026-09-16", "source": "x", "entries": entries})
    )
    return path


L = "AAAAAAAAAAAAAA-LLLLLLLLLL-N"
D = "AAAAAAAAAAAAAA-DDDDDDDDDD-N"


def test_the_loader_rejects_a_repeated_base_name(tmp_path):
    entries = [{"base_name": "proline", "l_inchikey": L, "d_inchikey": D}] * 2
    with pytest.raises(LabelReferenceError, match="proline"):
        load_label_reference(_table(tmp_path, entries))


def test_the_loader_rejects_equal_l_and_d_keys(tmp_path):
    entries = [{"base_name": "proline", "l_inchikey": L, "d_inchikey": L}]
    with pytest.raises(LabelReferenceError, match="proline"):
        load_label_reference(_table(tmp_path, entries))


def test_the_loader_rejects_a_charged_form_key(tmp_path):
    entries = [{"base_name": "proline", "l_inchikey": L, "d_inchikey": D[:-1] + "K"}]
    with pytest.raises(LabelReferenceError, match="proline"):
        load_label_reference(_table(tmp_path, entries))
