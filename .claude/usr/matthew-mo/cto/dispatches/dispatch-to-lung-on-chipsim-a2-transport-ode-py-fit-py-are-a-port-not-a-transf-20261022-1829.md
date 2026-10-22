---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-22T17:29
status: created
priority: normal
size: task
subject: "A2 transport: ode.py + fit.py are a PORT, not a transfer — they are written against Stage 1's ThetaConfig and HEAD's is accessor-based. Full API mapping measured; implementation is yours."
in_reply_to: null
---

# A2 transport: ode.py + fit.py are a PORT, not a transfer — they are written against Stage 1's ThetaConfig and HEAD's is accessor-based. Full API mapping measured; implementation is yours.

I measured this far and stopped at the role boundary: porting is implementation, which is yours, not the CTO's. Everything below is measured at archive/lung-on-chipsim-stage1 and a2107bb — re-derive before acting.

WHY IT IS BLOCKED AT ALL: run_transport_fit/run_transport_ode were deliberately withheld from the pipeline.py union (see a2107bb's note) because chipsim/transport/ holds only __init__, prior, sourcing, theta here. A2 is correct about exactly ode.py and fit.py: the archived tip holds their only copy.

SAFE TO TRANSFER — screened, not assumed. Both files are CLEAN against the public-repo constraint: zero InChIKey-shaped tokens, zero InChI strings, zero DrugBank-accession-shaped tokens, zero UniProt-shaped tokens. (My SMILES-ish pattern fired only on '=====' comment rules — a false positive from my own regex, not a finding.) archive/lung-on-chipsim-stage1 is on NO remote, so nothing is published by reading from it. ode.py = 235 lines, fit.py = 321.

CLOSURE: ode.py needs numpy (now declared) + chipsim.transport.theta.ThetaConfig. fit.py needs numpy + chipsim.transport.ode + chipsim.transport.prior.TransportPrior (PRESENT, prior.py:109) + ThetaConfig. No other gap.

THE ACTUAL WORK — an interface mismatch, same shape as the numpy and organism-filter defects:
Stage 1's ode.py does 'field = theta[name]' then 'field.value' and 'field.assumed' — attribute access on a value-carrying object. HEAD's ThetaConfig holds 'entries: Mapping[str, Mapping[str, object]]' and exposes ACCESSORS instead:
  theta[name]          -> Mapping[str, object]   (a dict; has NO .value)
  theta.value(name)    -> object
  theta.unit(name)     -> str
  theta.is_assumed(name) -> bool
  theta.cited_count / assumed_count / assumed_fields
So the mapping is: field.value -> theta.value(name); field.assumed -> theta.is_assumed(name). HEAD's ThetaField is a SCHEMA descriptor (name, unit, kind, expected_citable, note), not a value holder — HEAD separates schema from data, which is why a verbatim copy would raise AttributeError on a dict at runtime.

TWO THINGS TO WATCH, because I would get them wrong:
1. fit.py defines its OWN _require_sourced_theta(theta), and HEAD's theta.py ALSO defines _require_sourced_theta with a public alias require_sourced_theta. Two implementations of one guard. Decide which is authoritative and say so; do not leave both.
2. ode.py's _theta_value refuses a field whose value is None as a DISCLOSED GAP ('the solver cannot integrate against a disclosed gap; a human supplies theta values via T20'). That refusal must survive the port intact — it is the standing constraint, not a nicety. Under HEAD's API the equivalent test is theta.is_assumed(name) / theta.value(name) is None.

Bring the paired tests with them (the already-ruled 'items travel with their tests, both ways'), and run the documented loop before you commit: uv sync --all-extras, ruff format, ruff check --fix, ty check chipsim, pytest. Note that ty catches what pytest cannot here: the transport imports were lazy, so the suite was green while two modules were unresolvable. Baseline to beat: ruff clean, ty 25 diagnostics, pytest -m 'not network and not integration' 775 passed / 0 failed / 0 errors.

If any of the above is wrong at the ref it names, say so — you have been right four times on this workstream.
