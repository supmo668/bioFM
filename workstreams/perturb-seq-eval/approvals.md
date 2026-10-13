# Approval log — perturb-seq-eval

<!-- Written only by tools/approval-log. Rows are never edited: a correction is a new row (Corrects = the row it fixes). A 'Human' route carries its evidence. -->

| # | Date | Decision | Route | By | Evidence | Corrects |
|---|---|---|---|---|---|---|
| 1 | 2026-10-10 | CTO applies S1 to the CODE as well: retire llm_key_source in provenance.py (writer), the v05_preflight C-KEY-SOURCE check, app_v05 _HOME_PROJECT, their test fixtures, the pyproject email and the CHANGELOG line. Rationale: with the field still written by the code, a re-run as documented re-creates it, so the data-only amendment does not satisfy 'everywhere'. The code scope is the CTO's application of the principal's words, not a separate principal ruling. Conditions: (a) the retired preflight check is REMOVED with a dated note, never left silently passing; (b) the RR-1 appendix sentence saying a re-run re-creates the field is corrected in the same iteration; (c) no recorded before/after SHA-256 in run_record_amendments.json changes and the superseded-manifest row stands; (d) ordinary QG + receipt; deposit stays held. | principal | Human | quote: "Remove it everywhere, amend the hash"; session: principal ruling 2026-10-08, relayed as CTO dispatch #582; recorded in cto-handoff.md and plan-approval-log.md row 1 |  |
