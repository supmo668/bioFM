---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-23T09:33
status: created
priority: normal
size: task
subject: "RULED (row 36): widen the identifier gate to configs/. Condition already HOLDS by content — 26/26 and 88/88 — so this converts curation into a check. Option C (scope registry) DECLINED as the shape E-23 closed on. Implementation is yours."
in_reply_to: null
---

# RULED (row 36): widen the identifier gate to configs/. Condition already HOLDS by content — 26/26 and 88/88 — so this converts curation into a check. Option C (scope registry) DECLINED as the shape E-23 closed on. Implementation is yours.

Principal ruled your finding 2, verbatim 'Widen it (Recommended)'. Approvals row 36. Implementation is the worktree agent's; specifying it was mine.

WHAT TO BUILD: extend tests/test_fixture_sources.py beyond its current glob (tests/fixtures/snapshot/*.tsv, line 36) to cover configs/, asserting a public-source pointer per structure.

THE CONDITION ALREADY HOLDS — measured structurally by me, so this should go green without touching data:
 - configs/poc_compounds.yaml      : 26 identifiers, 26 evidence_doi, 26 retrieved. Entry keys are canonical_inchikey, name, evidence_doi, retrieved.
 - configs/label_structure_reference.yaml : 88 identifiers (44 entries x l_inchikey + d_inchikey), 88 pubchem_cid (l_ and d_), plus a header-level source and retrieved_on.
So the two files use DIFFERENT citation mechanisms — evidence_doi versus pubchem_cid — and the gate must accept both per file rather than assume one vocabulary.

PARSE THE STRUCTURE, DO NOT GREP LINES. This is the direct lesson of row 34 and it will bite you here specifically: poc_compounds.yaml is INLINE FLOW STYLE, '- {canonical_inchikey: ..., name: ..., evidence_doi: ...}', 26 of 26 entries, with ZERO line-anchored keys in the whole file. A line-anchored pattern sees nothing and returns 0, silently. Use yaml.safe_load. Both of us already failed this exact way on this exact file.

OPTION C WAS DECLINED, and the reason matters for how you build it: a declared scope registry is the shape E-23 closed on (row 61). Widen the glob and assert per structure; do NOT add a registry of which files are in scope.

ALSO WORTH KNOWING, from the same screen: poc_compounds.yaml pairs canonical_inchikey WITH name in all 26 entries and is ALREADY PUBLIC on origin/lung-on-chipsim. That is permitted - principal-curated input, #120 section 1 satisfied, F33 precedent - and is now recorded at approvals row 33 with its disposition. Your gate should NOT fail on the pairing; it checks the public-source condition only.

Run the documented loop before committing: uv sync --all-extras, ruff format, ruff check --fix, ty check chipsim, pytest -m 'not network and not integration'. Baseline to hold: ruff clean, ty 25, 814 passed / 0 failed / 0 collection errors.

SEPARATELY, and not yours: the principal also ruled the D6 protection route (row 35) and an A4 amendment (row 37). On row 35 I found a blocker before the principal ran it - there is NO tracked destination configured for the adjudication export, because the project .gitignore ignores data/{raw,interim,processed}/** and negates only *.dvc, .gitkeep, three named raw files and data/processed/*.sha256, with no .csv negation anywhere, and the tracked tests only ever write to tmp_path. So an export under data/ is ignored and would never commit. Flagging it to you because it touches the file layout you work in; the fix is the principal's to approve.
