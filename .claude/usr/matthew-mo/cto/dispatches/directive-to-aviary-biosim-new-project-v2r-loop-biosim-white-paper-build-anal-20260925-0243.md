---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-09-25T09:43
status: created
priority: high
size: project
subject: "NEW PROJECT: v2r-loop/BioSim white paper — build + analysis toward publication rigour (spec eb6e6ff)"
in_reply_to: null
---

# NEW PROJECT: v2r-loop/BioSim white paper — build + analysis toward publication rigour (spec eb6e6ff)

The principal approved a publication-grade white paper on the v2r-loop and the BioSim worked experiment. It is written for ML-focused computational biologists and taught as a lab method. You own the substance, in the Aviary-BioSim repo under paper/. I review it for publication rigour and do not write it.

SPEC (read in full before you plan): bioFM docs/superpowers/specs/2026-09-25-v2r-biosim-whitepaper-design.md at commit eb6e6ff. main is not pushed, so read it with: git -C <bioFM> show eb6e6ff:docs/superpowers/specs/2026-09-25-v2r-biosim-whitepaper-design.md

WHAT YOU WOULD OTHERWISE GET WRONG:

1. Your .v2r/ run records are NOT drain 1. dashboard/seed_demo_run.py overwrote the live .v2r/ with a seeded 23-unit, 3-drain fixture: placeholder register_sha ...1eef, pins d4e5f6a1b2c3 and 9a8b7c6d5e4f, and U-014/15/17 listed as both closed and parked. register verify-record returns UNVERIFIED on all three. The seeded data shows pass-to-pass improvement, which the paper is forbidden to claim. Do not cite any of it. Drain-1 evidence is git (28af3c4 U-001 ... 2e00aa3 U-006), docs/drain-1-notes.md, the six instincts, and any recoverable Weave traces. Fix the seeder so it cannot write into a live .v2r/ (B1).

2. Self-improvement is MECHANISM, NOT RESULT. Only one drain ran, it closed 6/6, and nothing was set aside, so no improvement between passes was ever measured. Neither the title nor the abstract may claim it as a result.

3. CoreWeave is only the venue. Compute was MPS plus W&B Inference. Budget enforcement has never run end to end.

4. The claims-traceability script (A7) is the entry condition for my review. Every number in the TeX maps to a file:field under paper/evidence/ with a label (measured / reconstructed / reported / documented). A 'reported' claim phrased as measured fails the check.

5. Reproduce rather than copy. A1 re-runs the six sealed tests today through tools/referee. A3 recomputes the science numbers from science/out/esm/results.json. A6 re-runs the plugin suite. Every run saves its exact config (SHA, model ids, seeds, versions) next to its output.

6. Plain language in the paper. Say 'pass', not drain; 'task', not build unit; 'setting work aside', not parking; 'independent test', not sealed test (the Stage 5 rule).

7. The accession/substance constraint applies prospectively to all new text. Do not edit the three pre-existing sites (handoff item 14, still with the principal).

SEQUENCE: plan -> /grill-me plan gate -> B1, then A1-A8 -> W1 draft -> P1 publish.yml -> /iteration-complete -> pr-submit to me. publish.yml: topic is required with no default. Authors/ORCID are supplied by the principal at the publish gate, so leave the field for the principal to fill; do not invent a value.

NOT AUTHORISED: new drains, CoreWeave runs, the instinct-pin fix, any venue deposit (including the sandbox), OpenAIRE, n8n workflow creation. The publish CLI and n8n workflow are perturb-seq-eval's #203 (option (a) ruled). The paper will be its first real project once that lands.

REPORT BACK at the plan gate with: the plan; what A4 found (does the 66-measurement trace exist?); and whether A1 reproduced 6/6.
