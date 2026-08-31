FIXTURE — SYNTHETIC. NOT A DrugBank REDISTRIBUTION.

These TSVs mimic the *schema* of the dhimmel/drugbank 4.2 snapshot so T5/T5b/T6's
parse logic is testable while T2 (the pinned commit) and T4a (the fetch) are
outstanding. They carry no DrugBank content: identifiers are FIXTURE-prefixed and
the structures are common, unencumbered small molecules used only to exercise
RDKit canonicalization.

ChipSim never redistributes DrugBank. Real data lands under data/raw/, which is
git-ignored and DVC-tracked. No pipeline path reads this directory.
