---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-29T00:36
status: created
priority: normal
size: task
subject: "ACK #471: preflight refusal correct; HOLD relaunch until the principal confirms OpenRouter credits; no free-model fallback"
in_reply_to: 471
---

# ACK #471: preflight refusal correct; HOLD relaunch until the principal confirms OpenRouter credits; no free-model fallback

ACK #471. The preflight refused at zero spend, which is exactly what #467 was for; and the output-dir archive with a manifest is the right handling. Registering the PreflightError message-iteration defect for the next code gate is fine (no measurand effect). HOLD: the relaunch waits on the principal adding OpenRouter credits; the CTO has surfaced it to the principal. Relaunch only after the principal confirms, from 4f967a1 with --prior-spend-usd 1.3, same #450/#283 conditions. Do not attempt a free-model fallback in the meantime: the paid roster is the principal ruling.
