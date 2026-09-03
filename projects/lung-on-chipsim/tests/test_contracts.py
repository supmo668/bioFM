"""The A&D §1.2 data-contract test.

Deliberately empty in M0 slice 1 — the data contract covers the harmonized
multi-source S1 artifact and arrives with the ChEMBL plan (defect 29). The file
exists so §4.4's day-one module set is complete and its target is stable.
"""

import pytest


@pytest.mark.skip(reason="ChEMBL plan — the §1.2 data contract covers the harmonized S1 artifact")
def test_harmonized_compounds_satisfy_the_data_contract():
    """(InChIKey, SMILES, logP, pKa, MW, TPSA) conform to the §1.2 contract."""
    raise AssertionError("not implemented until the ChEMBL plan")
