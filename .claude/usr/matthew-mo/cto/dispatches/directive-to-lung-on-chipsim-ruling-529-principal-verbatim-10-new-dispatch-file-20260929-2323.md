---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-30T06:23
status: created
priority: high
size: task
subject: "RULING #529 (principal, verbatim): 10 new dispatch files REDACT THEN PUBLISH; 7 already-public CTO files redacted on main by the CTO via coord PR — write ONE detector-driven redact-records.py (idempotent, footer line, two tests), send me its path first; probes accounted under (i); then checker fixes, re-gate"
in_reply_to: null
---

# RULING #529 (principal, verbatim): 10 new dispatch files REDACT THEN PUBLISH; 7 already-public CTO files redacted on main by the CTO via coord PR — write ONE detector-driven redact-records.py (idempotent, footer line, two tests), send me its path first; probes accounted under (i); then checker fixes, re-gate

RULING #529 — you were right that PR #7's precedent was a no-secrets scan, not a shape scan, and right not to narrow the globs. I reproduced your scan myself in your worktree (project venv, --no-write): 540 files, 21 with shapes, 3 read-as-cited, FAIL. Then I did the part you may not: I read the flagged files' context with the values masked. Of the 21: 7 are CTO dispatches ALREADY PUBLIC on origin/main (PR #7/#9), 3 are untracked handoff history (not in the diff), 2 are workstream files with synthetic probe shapes, and 10 are YOUR dispatch/escalation records new in this diff — and those carry licensed-source CONTENT, not only shapes: accessions paired with compound names and InChI layers (a keto/enol pair, a bis-enol/diketo pair with layers, a name/CID/accession table, a row of eight accessions, three names resolved to keys). The name-association prohibition, in the audit trail of the workstream whose subject is that prohibition.

PRINCIPAL RULINGS (AskUserQuestion, this session; verbatim options):
1. The 10 new files: "Redact then publish". 
2. The 7 already-public CTO files: "Redact at the tip via a coordination PR" — mine to do, on main.

YOUR ACTIONS, in order:
(1) Write ONE mechanical redaction instrument, qgr/evidence/redact-records.py, driven by the SAME detectors the scan uses (REAL_ACCESSION_RE, _STRUCTURE_RE from chipsim.ingest.drugbank_snapshot; the InChIKey/InChI shapes as the scan defines them) — never by hand, never by a hand-typed list of files: input = file paths; every real-accession token → `<redacted:DB-accession>`, every structure token → `<redacted:structure>`, names and all other text untouched; idempotent (a second run changes nothing); appends ONE footer line per changed file: `<!-- redacted 2026-09-30 by redact-records.py: N accession tokens, M structure tokens replaced by typed placeholders; ruling #529/#530 (principal, AskUserQuestion) — record otherwise unchanged -->`; refuses to run on a file outside `.claude/usr/**` or `workstreams/**/qgr/**` without --allow; false-exclusion test: a planted real-shaped token in a fixture IS replaced; false-inclusion test: a placeholder and a synthetic probe are NOT.
(2) Run it over the 10 new files (list them by path in the reply; counts only). The two workstream files (findings-20260917-s7.md's `SECRET-DRUG-NAME` example line; e23-draft-measure.py's PROBE_INCHI shapes) are constructed probes — account them under clause (i) with a marker, do not redact them, and say so.
(3) Re-run the artifact scan over `.claude/usr/**`: it must PASS on the new files; the 7 CTO files will still fail on your branch until my main-side redaction reaches origin — report them by path as "CTO-owned, redaction pending on main (#530)", not as your failure, and do NOT touch them.
(4) Send me the instrument's path + its two tests' names FIRST (before the paper-checker fixes), so I can run the identical instrument on the 7 files on main and land that as a coordination PR; your re-gate then runs against an origin/main whose 7 files are clean.
Then the paper-checker fixes (i)-(vii) per #524, then re-gate → receipt → /phase-complete → pr-submit.

Blockers 2/3/4 + OWN-3: accepted as proven (compare mutants killed both ways; raises= with its regression; 26 dates from e59cb3d blame-verified — the "which route" answer is exactly what I asked for; bare-name override refused, failing diff-hash aborts). Hold on poc_compounds.yaml released as you said.

Recorded: the scan's old globs reached 2.6% of the surface. That number goes in the Stage 1 limitations under the family, dated.
