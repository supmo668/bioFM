---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-15T14:51
status: created
priority: normal
size: task
subject: "Re #631 D8: STOPPED — image doesn't install modal (client = launching CLI); pin needs a poetry.lock regen (no poetry) or a run-path guard; options i/ii/iii, recommend ii+iii"
in_reply_to: null
---

# Re #631 D8: STOPPED — image doesn't install modal (client = launching CLI); pin needs a poetry.lock regen (no poetry) or a run-path guard; options i/ii/iii, recommend ii+iii

Re #631 D8. STOPPED per your condition: the pin as ruled cannot be done cleanly. Nothing changed, nothing sent.

Facts, measured:
1. The image does NOT install modal. app_v05.py's pip_install list (lines 65-79) has no modal. Modal supplies the in-container client, the one provenance read as 1.5.5, to match the CLI that LAUNCHED the app. So "pin the image" really means pinning the launching client on the host.
2. The host-side pin lives in pyproject's Poetry modal group (modal = ">=0.68"). poetry.lock pins 1.4.2 and was last regenerated at 25fce23 (v0.3.0). Setting "==1.5.5" makes the lock inconsistent with pyproject. Regenerating it needs poetry (not installed; my rule is no installs), and `poetry lock` re-resolves the whole tree, a much wider change than one pin. Evidence of the drift: the uv env I rebuilt resolved modal 1.6.1.
3. docs/SUPPLEMENT.md:23 ("client 1.4.2") is dated 2026-04-23 and belongs to the v0.5-era supplement, which the deposit ships as supplement.zip, labelled SUPERSEDED. The v0.5.0 provenance records no lib versions, so 1.4.2 cannot be shown WRONG for that release, only stale relative to v0.6.0. Editing it would also change the superseded deposit's content.

Options:
(i) pyproject modal "==1.5.5" + regenerate poetry.lock. Needs a poetry install (principal's call) and a broad lock diff.
(ii) Enforcement without touching the lock: app_v05's entrypoint refuses to launch unless modal.__version__ == "1.5.5", named as the recorded run's client. This is a run-path code change, recorded as a new post-land path in land_v060.json, tested, gated.
(iii) Disclosure only: README / paper README record "the run's Modal client was 1.5.5 (provenance); poetry.lock's 1.4.2 dates from v0.3.0". Leave docs/SUPPLEMENT.md as the v0.5 record, with a dated note in the README rather than editing the superseded doc.
I recommend (ii)+(iii): enforcement at the place the version is actually chosen, disclosure where re-runs are documented, and the superseded record left intact.
next_handoff: CTO ruling on D8 (i/ii/iii)
