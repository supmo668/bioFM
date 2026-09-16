# Structure sources — snapshot fixtures

Every structure in `drugbank.tsv` and `drugbank-slim.tsv` cites a public source here. The TSVs
follow the upstream TSV schema and cannot carry an inline citation (CTO ruling 2026-09-16).

**Why this file exists.** A bare canonical structure identifier is not DrugBank record content,
but every structure in a tracked file must cite a public source so its provenance is checkable
(principal invariant, CTO #120 §1). `tests/test_fixture_sources.py` fails if any InChI in the
fixture TSVs is missing here, or if a row here no longer matches a fixture — so this file cannot
silently fall behind.

**How the CIDs were obtained.** PubChem PUG REST, `POST /compound/inchi/cids/TXT` with the EXACT
InChI below — not a name lookup, so each CID provably belongs to the string beside it.

**What these fixtures are, stated from the files.** Row IDs are the synthetic `DB9nnnn` range and
names carry a `Fixture-` prefix; neither has ever been a real DrugBank accession or record title,
from the fixtures' first version onward. Six of these structures are byte-identical to the
snapshot's strings for the same molecules, which is expected of canonical identifiers.

| InChI | PubChem CID | Retrieved | Fixture row |
|---|---:|---|---|
| `InChI=1S/C8H10N4O2/c1-10-4-9-6-5(10)7(13)12(3)8(14)11(6)2/h4H,1-3H3` | 2519 | 2026-09-16 | DB90001 Fixture-Caffeine |
| `InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)` | 2244 | 2026-09-16 | DB90002 Fixture-Aspirin |
| `InChI=1S/C13H18O2/c1-9(2)8-11-4-6-12(7-5-11)10(3)13(14)15/h4-7,9-10H,8H2,1-3H3,(H,14,15)` | 3672 | 2026-09-16 | DB90003 Fixture-Ibuprofen |
| `InChI=1S/C27H38N2O4/c1-20(2)27(19-28,22-10-12-24(31-5)26(18-22)33-7)14-8-15-29(3)16-13-21-9-11-23(30-4)25(17-21)32-6/h9-12,17-18,20H,8,13-16H2,1-7H3` | 2520 | 2026-09-16 | DB90004 Fixture-Verapamil-Free-Base |
| `InChI=1S/C27H38N2O4.ClH/c1-20(2)27(19-28,22-10-12-24(31-5)26(18-22)33-7)14-8-15-29(3)16-13-21-9-11-23(30-4)25(17-21)32-6;/h9-12,17-18,20H,8,13-16H2,1-7H3;1H` | 62969 | 2026-09-16 | DB90005 Fixture-Verapamil-Hydrochloride |
| `InChI=1S/C8H9NO2/c1-6(10)9-7-2-4-8(11)5-3-7/h2-5,11H,1H3,(H,9,10)` | 1983 | 2026-09-16 | DB90007 Fixture-Paracetamol |
| `InChI=1S/C14H11Cl2NO2.Na/c15-10-5-3-6-11(16)14(10)17-12-7-2-1-4-9(12)8-13(18)19;/h1-7,17H,8H2,(H,18,19);` | 9818469 | 2026-09-16 | DB90008 Fixture-Diclofenac-Sodium |
| `InChI=1S/C7H6O2/c8-7(9)6-4-2-1-3-5-6/h1-5H,(H,8,9)` | 243 | 2026-09-16 | DB90009 Fixture-No-ATC |
