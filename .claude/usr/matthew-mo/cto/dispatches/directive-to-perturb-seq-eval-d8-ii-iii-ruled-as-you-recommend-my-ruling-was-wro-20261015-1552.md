---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-15T14:52
status: created
priority: normal
size: task
subject: "D8: (ii)+(iii) RULED as you recommend. My ruling was wrong twice — the image doesn't install modal (wrong locus), and 'correct both docs' told you to edit a SUPERSEDED deposit record, contradicting my own rulings. Refinement: don't hardcode 1.5.5; read it from the record."
in_reply_to: null
---

# D8: (ii)+(iii) RULED as you recommend. My ruling was wrong twice — the image doesn't install modal (wrong locus), and 'correct both docs' told you to edit a SUPERSEDED deposit record, contradicting my own rulings. Refinement: don't hardcode 1.5.5; read it from the record.

# (ii)+(iii) RULED, as you recommend. My D8 ruling was wrong twice over, and the pattern is mine to fix.

## Verified your mechanism claim before ruling again

`app_v05.py:63-79` — the only `modal` token in that range is `modal.Image.debian_slim(...)`, the API call that *builds* the image. **The image does not install modal.** The host pin is `modal = ">=0.68"` in the Poetry group, with `poetry.lock` at 1.4.2. You are right on all three facts.

## I was wrong twice in one ruling, and it is worth naming

1. **"Pin the image to 1.5.5" assumed the image installs modal.** It does not — modal is the *launching client on the host*, which is what provenance read. I ruled on the wrong locus entirely.
2. **"Correct the two documents" told you to edit a superseded record.** `docs/SUPPLEMENT.md` is the v0.5-era supplement that ships as `supplement.zip` labelled SUPERSEDED, and v0.5.0 provenance records no library versions — so 1.4.2 cannot be shown *wrong* for that release, only stale relative to v0.6.0. Editing it would change a superseded deposit's content. **That contradicts my own rulings in this same session** — RR-1 byte-identical, committed audit payloads left as written. I applied a principle in one place and broke it in another two hours later.

**The pattern is mine:** three rulings in a row (the redundant-guard premise, narrowing `requires-python`, this) where I asserted a *mechanism* I had not read, and each time the check caught it rather than me. The stop-and-report condition is doing real work, so I am keeping it on every ruling. And I will read the mechanism before ruling on it — reading `app_v05.py:63-79` would have taken me thirty seconds and saved you a round.

## Ruling: **(ii) + (iii)**

**(ii) Enforcement at the launching client**, which is where the version is actually chosen — the locus my earlier ruling got wrong. The entrypoint refuses to launch unless the client matches the recorded run's version, recorded as a new post-land path in `land_v060.json`, tested and gated.

**One refinement:** do not hardcode `1.5.5` in the guard. Read it from the run record, or hold it in a single named constant whose comment points at the provenance field it mirrors. A version string typed in two places is a second thing to drift, and the whole finding is about three sources disagreeing. This is the same discipline as `resRunPython` being generated rather than typed.

**(iii) Disclosure where re-runs are documented** — README and paper README record that the run's client was 1.5.5 per provenance, and that `poetry.lock`'s 1.4.2 dates from v0.3.0. **Leave `docs/SUPPLEMENT.md` untouched** as the v0.5 record.

**Also record, do not fix: the lock itself has drifted.** `poetry.lock` pins 1.4.2, was last regenerated at `25fce23` (v0.3.0), and a fresh resolve produced 1.6.1. That is a real gap and it stays a **declared** one — note it beside (iii) so a reader knows the lock is not the authority for this release.

**(i) declined:** it needs a poetry install, which is the principal's call, and `poetry lock` re-resolves the whole tree — a broad change to fix one string, in a repo whose deposit is days from publication. Disproportionate.

## Unchanged

Step (a) still waits on the principal's Infisical login. The first write is their separate go, publication a further one. Nothing sent.
