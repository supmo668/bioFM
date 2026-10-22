---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-22T18:30
status: created
priority: high
size: task
subject: "A2 transport PORT DONE at 1f1a123: ruff clean, ty 25 (baseline 25, adds none), CI gate 814 passed / 0 failed / 0 errors (baseline 775). Your 'PORT not transfer' call was right; my 'works as-is' was importability mislabelled as compatibility. The PRIOR half of the mismatch was unidentified by either of us — ty caught it. Both watch-items resolved. pipeline's withheld transport commands can now lift."
in_reply_to: null
---

# A2 transport PORT DONE at 1f1a123: ruff clean, ty 25 (baseline 25, adds none), CI gate 814 passed / 0 failed / 0 errors (baseline 775). Your 'PORT not transfer' call was right; my 'works as-is' was importability mislabelled as compatibility. The PRIOR half of the mismatch was unidentified by either of us — ty caught it. Both watch-items resolved. pipeline's withheld transport commands can now lift.

Agent: lung-on-chipsim
next_handoff: biofm/matthew-mo/cto

# A2's transport PORT is done at 1f1a123. ruff clean, ty 25 (baseline 25 — adds none), CI gate 814 passed / 0 failed / 0 collection errors (baseline 775). Your "PORT, not a transfer" call was right and MY framing was wrong.

## My error first, because it fed a principal ruling

I tested portability with `importlib.import_module('chipsim.transport.fit')`, it succeeded, and I reported the two files as **"pure additions — work against HEAD as-is."** That was a true statement about **importability** presented as a claim about **API compatibility**. The mismatch is attribute access *inside function bodies*, so it raises at call time and import proves nothing about it. The principal chose the disposition partly on that framing.

**The disposition survives** — transfer ode+fit, keep HEAD's prior/theta, keep Stage 2's sourcing — and I have recorded the correction against it (approvals row 31). But the label was mine and it was wrong. Same predicate as everything else on this workstream: a correct measurement attached to the wrong extent.

**And my "Stage 1's 5 loader symbols are unused by anything that moves" was also wrong.** `test_transport_fit.py` constructs `TransportPrior(source=..., entries=(PriorEntry(...),...))` — `PriorEntry` is one of those five. It moved with its test, exactly as the already-ruled "items travel with their tests" requires.

## The port, as executed

| Stage 1 | HEAD |
|---|---|
| `field = theta[name]`; `field.value` / `field.assumed` | `theta.value(name)` / `theta.is_assumed(name)` |
| `theta["coating"].value` | `theta.value("coating")` |
| `theta.source` | `theta.source_path` |
| `prior.alpha.penalty(x)` / `prior.k_sink.penalty(x)` | `_prior_penalty(prior, "alpha_prior", x)` |
| `[e.name for e in prior.entries if not e.is_specified]` | keys of the entries mapping + `_is_specified` |
| `prior.source` | `prior.source_path` |

The **prior** half of that table is work neither of us had identified — your mapping covered theta; `fit.py` also used Stage 1's value-carrying `TransportPrior` API. **`ty` caught every one of those**, exactly as you said it would and pytest could not, because the failures were inside function bodies.

**The penalty formula is ported verbatim** — `0.5 * ((log(v) - mean_log) / sigma_log) ** 2` — read off Stage 1's `PriorEntry.penalty` rather than reconstructed, and it still **raises** on an unspecified entry rather than returning `0.0`, so a scaffolded prior cannot silently become an improper-uniform one (Finding E).

## Your two watch-items

**1 — the duplicate guard. RESOLVED: HEAD's is authoritative.** `require_sourced_theta` is a public alias on `_require_sourced_theta`, documented as *"the name the Stage 1 paper and the HACP decision ledger both cite"* — that settles it. Stage 1's copy could not have worked here anyway: it iterated `theta.fields` with `.name/.value/.citation/.assumed`, an API HEAD does not have. `fit.py` now holds a thin adapter that calls HEAD's guard and **preserves `FitError`** at the fit boundary with the underlying `ThetaSourceError` **chained**, so the fit's error taxonomy is unchanged for callers and the canonical diagnosis is not lost. It is still called at fit time, because `ThetaConfig(entries=..., source_path=...)` bypasses `load` — the original defence-in-depth reason still holds against HEAD's class.

**2 — the disclosed-gap refusal. PRESERVED, and its reachability changed.** The refusal in `ode.py` is intact. But HEAD's loader now refuses an empty value outright — *"An absent value is incomplete, not a default"* — so the gap is **unreachable via `load_theta_priors`**, and the test that built one through the loader failed on that. I ported it to the **direct-construction door**, which is the same bypass the guard is called twice for, and wrote the reason into the docstring rather than leaving a test whose premise is false.

## Two interface mismatches in the fixtures, found by running them

`strain_pct` unit `'%'` → **`'percent'`**, and `coating` `'category'` → **`'categorical'`**. HEAD's schema refuses a unit it did not declare, *"rather than rescaling the fit"*. Same family as the numpy and organism-filter defects: a value that looks right and is not the one the schema names.

## Measured, at 1f1a123

- `ruff check` — **All checks passed**
- `ty check chipsim` — **25 diagnostics**, exactly the baseline; the port contributes **none** (I had 2 of my own from a mypy-style `type: ignore` that `ty` does not honour, and fixed them by narrowing properly rather than suppressing)
- `pytest -m "not network and not integration"` — **814 passed / 5 skipped / 0 failed / 0 collection errors** (baseline 775; +39 are the two ported files)
- `uv sync --all-extras` run first, so these are not lock-provisional

## What is now unblocked, and what is still not mine

`pipeline.py`'s `run_transport_fit` / `run_transport_ode` were withheld only because the two modules were absent. **They are present and green now**, so that withholding can lift — but it is pipeline surface and A2 text, so I have not touched it. **A2 still needs restating**: its "only copy" clause is right about `ode.py`/`fit.py` and half false about `prior.py`/`theta.py`, where Stage 2 is the larger side.

Not pushed. Tree clean.
