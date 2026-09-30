---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-29T22:41
status: created
priority: high
size: task
subject: "Blocker 2 value (principal, verbatim): retrieval dates = each entry's git commit date, read from git, with one header line; apply mechanically and release the hold on poc_compounds.yaml"
in_reply_to: null
---

# Blocker 2 value (principal, verbatim): retrieval dates = each entry's git commit date, read from git, with one header line; apply mechanically and release the hold on poc_compounds.yaml

BLOCKER 2 VALUE — principal ruled (AskUserQuestion, this session, verbatim option: "Use the file's git commit date for all 26").

Apply mechanically: for each of the 26 entries in configs/poc_compounds.yaml, add `retrieved: <date>` where <date> is the date the entry entered the tree, read from git (the first commit that introduced that entry's line — `git log --diff-filter=A --follow --format=%cs` per line, or the file's introducing commit if all 26 arrived together; say which you used). Add ONE header comment: 'retrieved: dates are the date of record — the git commit date at which each entry entered the tree, an upper bound on when the DOI was consulted; principal-ruled 2026-09-29'. No value changes, no lookups, no typed dates. Then the file clears the same bar as label_structure_reference.yaml; confirm by running the classifier and citing its record.

Release the HOLD on that file once applied. Everything else in #524 stands.
