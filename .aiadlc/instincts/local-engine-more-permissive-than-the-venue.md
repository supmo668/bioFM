---
name: local-engine-more-permissive-than-the-venue
confidence: 0.750
created: 2026-10-30T18:41:54Z
last_reinforced: 2026-11-02T02:26:19Z
ttl_days: 30
triggers: [pdflatex, tectonic, xelatex, latex-action, arxiv, claims.py, U+2212, metadata]
tags: []
---

A local toolchain that accepts more than the destination produces builds that are green locally and fail at the venue. Both papers in the fleet hit U+2212 MINUS SIGN independently: perturb-seq-eval in its arXiv metadata (ASCII only) and aviary-biosim in LaTeX source, where claims.py deliberately wrote a Unicode minus that XeTeX/tectonic accepts and pdflatex rejects. The configuration form was latexmk running DVI mode via latex while arXiv uses pdflatex. **Why:** the local pass is evidence about the local engine only. **How to apply:** compile and validate with the venue's own engine and limits (pdflatex with -pdf; arXiv's ASCII and 1920-char abstract rules), and fix generated output at its generator, never in the 'do not edit' file. Tickets: MYB-6.
