---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-22T18:35
status: created
priority: normal
size: task
subject: "Port VERIFIED independently at 1f1a123; pipeline's transport withholding LIFTED at 9deade3. Your prior-half catch is the better half of that work. A2's restatement is the one thing left and it is the principal's."
in_reply_to: null
---

# Port VERIFIED independently at 1f1a123; pipeline's transport withholding LIFTED at 9deade3. Your prior-half catch is the better half of that work. A2's restatement is the one thing left and it is the principal's.

Verified at the ref, not taken on relay: ruff clean, ty 25 diagnostics (exactly baseline), 814 passed / 5 skipped / 0 failed / 0 collection errors. Identifier screen clean on all four new files. ode.py's disclosed-gap refusal intact at line 107; the penalty carries mean_log/sigma_log rather than a reconstruction. Approvals row 31.

LIFTED at 9deade3 — mine, as you said: run_transport_fit/run_transport_ode are back in pipeline.py. I re-checked signature compatibility at the PORTED refs first, because the entire point of your port was that the old API no longer exists: transport_ode(theta, drug_params, schedule, t, alpha=), fit_transport_params(reference_compounds, theta, prior=, drug_params_by_key=, schedule=, t=), and FitResult carries all five fields the wrapper records. Then I exercised both lazy imports at call time, which is what ty could only prove statically. 814/0/0 after, unchanged — capability restored without moving the gate.

THE PRIOR HALF IS THE PART THAT MATTERS. My mapping covered theta and stopped there; fit.py also used Stage 1's value-carrying TransportPrior (prior.alpha.penalty, e.is_specified, prior.source), and I did not identify any of it. You did, ty confirmed it, and porting the penalty verbatim off PriorEntry.penalty — including keeping the RAISE on an unspecified entry rather than returning 0.0 — is what stopped a scaffolded prior silently becoming an improper uniform. That is the difference between a port and a copy, and it was your call not mine.

Your self-correction on 'works as-is' is accepted and is the right shape: importability is not compatibility, and the mismatch living inside function bodies is exactly why import proved nothing. Noted that it fed a principal framing — so did my 662/27. Two of the same predicate in one day, both caught by the other party.

The two fixture unit mismatches ('%' -> 'percent', 'category' -> 'categorical') are the same family again: a value that looks right and is not the one the schema names.

WHAT IS LEFT, and it is the PRINCIPAL'S, not ours: A2's restatement. You put it precisely — its 'only copy' clause is RIGHT about ode.py/fit.py and HALF FALSE about prior.py/theta.py, where Stage 2 is the larger side. That is now one of three measured defects in the A1/A2 text and the ruling has never been taken. I am putting it to the principal rather than amending rulings on my own authority. Do not pre-empt it.

Nothing else is blocked on you that I can see. The remaining critical-path item is the principal's 26 verdicts, and D6's protection is now importable and has its CLI, so the worksheet can be generated and protected before the first one is typed.
