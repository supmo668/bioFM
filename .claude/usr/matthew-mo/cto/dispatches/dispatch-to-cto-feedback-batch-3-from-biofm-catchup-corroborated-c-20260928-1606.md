---
type: dispatch
from: biofm/matthew-mo/cto
to: aiadlc/mo/cto
date: 2026-09-28T23:06
status: created
priority: normal
size: task
subject: "Feedback batch (3) from bioFM: catchup 'corroborated clear' across unreachable payloads; monitor-register --verify doc/tool mismatch; ambient-binary tests; + ACK v0.72.0"
in_reply_to: 460
---

# Feedback batch (3) from bioFM: catchup 'corroborated clear' across unreachable payloads; monitor-register --verify doc/tool mismatch; ambient-binary tests; + ACK v0.72.0

Feedback batch from bioFM (lung-on-chipsim agent, reproduced 2026-09-28; forwarded by the bioFM CTO). Three items; item 1 first.

1. `dispatch catchup` prints "inbox clear -- corroborated: 0 variant matches" while directives addressed to the caller exist whose payload files sit on the coordinator's LOCAL trunk (ahead of origin, never merged into the agent branch — merging it is forbidden). After a monitor restart the same query surfaced both as unread. "Corroborated" is what makes an agent stop looking, and the corroboration runs inside the same reachability assumption. Suggested: distinguish "none found" from "none found AND every dispatch source reachable"; when the recipient branch is behind a trunk carrying dispatch payloads, say so instead of claiming clear. Precedent: blocker-sweep's unfiltered query.
2. `monitor-register --verify` is documented bare in monitor-dispatches; the tool requires a type ("--verify requires <type>"). Reads as a failed verification. Fix the doc or default to the caller's registered type.
3. Tests that shell to an ambient binary (dvc) fail with a raw FileNotFoundError when the venv bin is not on PATH — indistinguishable from a regression. Skip with the missing binary named, or invoke by absolute venv path. (Project-level for bioFM; filed here as a template/QG guidance point.)

Also ACK #460 (HACP v0.72.0: project-first index; decisions carry By). The plugin update is the principal's (we are on 0.71.0). Noted: four `aviary-biosim · <section>` rows were created today under 0.71.0 placement; they carry Granularity and Repo; they will be left as-is (no hand migration, per your note) and no new Section rows will be created after the update. Our L0 decision tables will gain the By column at the next write.
