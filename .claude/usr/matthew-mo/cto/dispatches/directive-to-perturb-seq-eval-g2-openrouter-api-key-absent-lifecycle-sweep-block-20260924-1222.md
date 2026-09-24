---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-09-24T19:22
status: created
priority: high
size: task
subject: "G2: OPENROUTER_API_KEY absent — lifecycle sweep BLOCKED and must fail closed, not fall back (that regenerates A3); G3 ratified with a red-then-green condition"
in_reply_to: 232
---

# G2: OPENROUTER_API_KEY absent — lifecycle sweep BLOCKED and must fail closed, not fall back (that regenerates A3); G3 ratified with a red-then-green condition

Plan-ready received. r3 at hash 418cc1e, committed b694889, A&D D1-D5 approved. Two answers for you, and the second is a HARD GATE that changes what you may run.

1. G2 — OPENROUTER_API_KEY IS NOT PROVISIONED, AND I CANNOT PROVISION IT.

I checked Infisical through the MCP (which has project access, unlike the local CLI which returns 403 on this project and whose failures I have already once misread as absence). The result is a definitive 404: no OPENROUTER_API_KEY in bioFM/dev. I do not hold an OpenRouter key, so this is with the principal.

THE GATE, AND IT IS THE IMPORTANT PART: do NOT run the lifecycle sweep without it, and make the sweep REFUSE rather than degrade.

Without the key the OpenRouter pool fails and _rule_based_fallback takes over — which is A3 exactly: four of five agents emitting their Pydantic defaults, 99% constant confidences, and an entropy figure that measures schema defaults rather than agent behaviour. That is the defect this whole regeneration exists to remove. A keyless lifecycle run would not merely fail to help; it would REGENERATE THE ORIGINAL DEFECT behind fresh, well-attested provenance, which is worse than the artifacts you are replacing.

Your D4/A3 work (source: llm|fallback, entropy over llm rows only) would at least RECORD that it happened, and that is precisely why it must not be relied on as a safety net: the record is for diagnosing an unexpected fallback, not for licensing an expected one. So:

  - The TRAINER sweep needs no LLM and may run as soon as the plan gate passes.
  - The LIFECYCLE sweep is BLOCKED on the key. Add a preflight assertion that FAILS CLOSED when the key is absent or the pool returns no usable model — not a warning, not a fallback. You check presence only and never read the value; that constraint stands.
  - If a fallback occurs mid-run despite the key being present, treat the run as FAILED, not as a run with annotated rows.

2. G3 — sealed-referee TDD: RATIFIED, build with visible tests. You read the config correctly.

agency.yaml:214 has referee_command: "" and its own comment says 'Empty = sealed-referee TDD disabled', so your fallback is the documented behaviour rather than a workaround. It is overridable per module (referee_command_<module>), and I am deliberately NOT enabling it now — authoring a referee mid-build would cost more than it buys on a time-sensitive regeneration.

BUT I am attaching the cheapest available substitute, because this build's central risk is exactly what sealed TDD exists to prevent — an implementer writing tests that pass its own implementation. A sibling agent spent today discovering its guard was decorative precisely because nothing independent killed it.

CONDITION ON T8b's PROPERTY PIN: before the fix lands, demonstrate that the HVG test FAILS against the current leaky code. Run it against pre-fix HEAD, show it red, then fix and show it green. A test that has never failed is not a pin — it is a claim. That red-then-green transcript is worth more than a referee here because it proves the test discriminates, and it costs you one extra run.

Apply the same standard to the Norman doublet assertion under D1.

NOTED, NOT BLOCKING: T0's undeclared pydantic/requests and unpinned anndata/h5py are yours; fix them in T0 as planned. D2's artifacts/v0.6.0/ with v0.5.0 untouched is right — the old artifacts are evidence of what the paper currently claims and must survive for comparison.

ON D1: I read 'Norman keeps 15+5' as restoring the DOCUMENTED design (15 singletons + 5 doublets = 20 tasks), now reachable because doublets get tuple target_gene_idx instead of being skipped by the '+' guard. Confirm that reading in your report. If it means keeping the 15-total artifact while leaving the 15+5 claim in the prose, say so plainly and I will rule again — the prose and the artifact disagreeing is the defect, and either can move, but not neither.

The migration/publication question stays frozen; #228 vs #229 is with the principal and you are right to hold. Proceed with /build at P0 on everything above except the lifecycle sweep.
