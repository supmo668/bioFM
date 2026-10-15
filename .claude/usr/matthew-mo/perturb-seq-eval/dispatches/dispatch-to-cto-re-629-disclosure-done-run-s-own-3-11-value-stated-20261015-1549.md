---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-15T14:49
status: created
priority: normal
size: task
subject: "Re #629: disclosure done (run's own 3.11 value stated, receipt fcc1a9a); requires-python NOT narrowed — 4 Modal images need 3.11; options a/b/c, recommend (a)"
in_reply_to: null
---

# Re #629: disclosure done (run's own 3.11 value stated, receipt fcc1a9a); requires-python NOT narrowed — 4 Modal images need 3.11; options a/b/c, recommend (a)

Re #629 item 2. Disclosure DONE; narrowing NOT done. Your condition fired: something in the project needs 3.11. Nothing sent to any venue.

Branch perturb-seq-eval @ 102dc1dbbdb200f46725fddd54a68c1311583ba1 (pushed). Receipt fcc1a9a; QGR qgr-py312-*.

WHY NOT NARROWED: four Modal apps build on debian_slim(python_version="3.11") and run "pip install -e .": app_v05.py:63/93, app_biofm.py, app_lifecycle.py, app_lifecycle_optimizer.py. A >=3.12 floor breaks the documented sweep re-run. The pre-registered run itself ran on Python 3.11.0 (provenance). Nothing else needs 3.10/3.11 (poetry.lock markers only; modal accepts >=3.10).
Options for you (the design reviewer's D7):
(a) leave requires-python and keep the split: sweep on 3.11, bit-exact analyser re-run on 3.12, disclosed. This is what is on the branch now.
(b) move the Modal images to 3.12. Re-runs would then no longer recreate the recorded run's interpreter, which matters for a pre-registered run.
(c) make _plugin_entropy order-independent with math.fsum (preregistered.py:476). Same value on every Python, but it changes pre-registered estimator code after the run, and the analyser would disagree with the run's provenance value.
I recommend (a).

DISCLOSURE (paper.tex Reproducibility and results.tex run record, same sentence):
"This holds on Python 3.12: Python 3.12 made the built-in sum() over floats compensated, and before Python 3.12 the backbone entropy (stated and executed, which coincide here; five keys of summary.json) comes out one unit in the last place higher. The run itself ran on Python \resRunPython, and provenance.json records that higher value. No reported figure or gate outcome changes."
- The gate's top finding (D1, 80): the run itself computed and recorded the 3.11 value, so 3.11 is the run's own interpreter, not an outlier. The sentence now says so, with resRunPython (3.11.0) generated from provenance.
- "No reported figure or gate outcome changes" is measured: generated_numbers.tex is identical when built from the 3.11 summary.
- The README, paper README and CHANGELOG carry the note too (T5, 80).
- Tests: the exact sentence must follow the claim in both files, and the CHANGELOG claim must carry it. Before 3.12, each of the five keys must be exactly +1 ulp and all equal; that passes on a real 3.11 interpreter. 1189 tests pass on 3.12; tectonic 0 overfull / 0 undefined.

ALSO FOR YOU (D8, out of scope): modal drift. poetry.lock and docs/SUPPLEMENT.md say 1.4.2, the run's provenance records 1.5.5, and the image installs modal unpinned.

Unchanged: step (a) GETs wait on the principal's Infisical login (names out of band). The first write is the principal's separate go.
next_handoff: CTO: requires-python option (a/b/c) + modal drift; principal: Infisical login
