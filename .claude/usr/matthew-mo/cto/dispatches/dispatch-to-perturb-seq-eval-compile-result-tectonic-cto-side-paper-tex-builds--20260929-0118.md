---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-29T08:18
status: created
priority: normal
size: task
subject: "Compile result (tectonic, CTO side): paper.tex builds — 15 pages, no undefined refs/citations; 14 overfull hboxes (worst 275 pt, a wide table) + 2 font-shape warnings to fix before pr-prep"
in_reply_to: null
---

# Compile result (tectonic, CTO side): paper.tex builds — 15 pages, no undefined refs/citations; 14 overfull hboxes (worst 275 pt, a wide table) + 2 font-shape warnings to fix before pr-prep

COMPILE RESULT (tectonic 0.17.0, CTO side, your branch tip 0206904, paper/paper.tex, bibtex plainnat over references.bib): SUCCESS — 15 pages, PDF 185 KB. No undefined references, no undefined citations, no missing files, no errors.

Warnings to fix before /pr-prep (cosmetic, but a reviewer sees them):
- Overfull hboxes (14): the worst is 275 pt in a paragraph/table at source lines 10-16 of an \input section (a table wider than the text block), then 115 pt (lines 333-347), 115 pt (351-363), 76 pt (578-585), 47 pt (595-599), 44 pt (573-575), 42 pt (417-423), 31 pt (276-282); the rest under 10 pt. Line numbers are from the log's paragraph ranges; grep the log I attach at pr-submit if you need the file names.
- Font shape warnings: T1/lmr/m/scit and T1/lmr/bx/sc undefined (small caps + italic / bold small caps under Latin Modern) — substitute or drop the combination.
- Two 'h' float specifiers changed to 'ht'.

Nothing here changes a number. I will recompile the merged tree at pr-submit and attach paper.log to the land record; the PDF is not committed (gitignored, as you set).
