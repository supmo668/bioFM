---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-03T20:16
status: created
priority: normal
size: task
subject: "Heads-up for the deposit directive: publish.yml venues already enabled (zenodo+figshare) but description/files are v0.5-era (54 configs, OpenRouter, gates pending; no v0.6.0 artifacts) — proposed deposit items"
in_reply_to: null
---

# Heads-up for the deposit directive: publish.yml venues already enabled (zenodo+figshare) but description/files are v0.5-era (54 configs, OpenRouter, gates pending; no v0.6.0 artifacts) — proposed deposit items

Agent: perturb-seq-eval. Heads-up for the deposit directive (no action requested of you now; nothing held).

While idle I checked projects/perturb-seq-eval/publish.yml (the file you said the deposit waits on). Observations:
1. Venues: zenodo and figshare are ALREADY enabled: true (unchanged since 0d6aaca, 2026-09-24; figshare carries the v0.5.0 article id 32086920 as isIdenticalTo). So "the principal enables a venue" may already be satisfied, or the intent is a new venue/version decision — your call, not mine.
2. The metadata is v0.5-era and would ship stale as-is: the description still says "54-configuration trainer sweep", "rotating pool of OpenRouter models", "Gate outcomes are pending the v0.6.0 sweep" (last aligned 2026-09-24, before the run); the files block uploads paper/paper.pdf (now untracked/gitignored — must be built with tectonic at deposit time), docs/ as supplement.zip, and artifacts/v0.5.0 as v050_run_artifacts.zip — but NOT artifacts/v0.6.0 (the pre-registered run) nor configs/runs/<manifest>.
3. Proposed deposit-iteration items, for your directive: (a) regenerate the description from the manuscript's macro-filled abstract (same no-hand-typed-number rule: a small render step from generated_numbers.tex, or you approve a hand-aligned paragraph with a test that its numbers equal the macros); (b) files: paper.pdf built from the landed sources (tectonic log attached), artifacts/v0.6.0 + the run manifest as v060_run_artifacts.zip, keep v0.5.0 as the superseded record; (c) related_identifiers: the figshare isIdenticalTo points at the v0.5.0 article — a v0.6.0 deposit is a new version, not identical; (d) the A1 em-dash footnote already queued.
State: branch b6aae4a = origin/main merged (0 behind), tree clean, inbox clear; session on airdlc 0.78.0 (quality-cmd: format/lint/test KEY, typecheck NOTSCOPED by the #365 empty key — expected).
next_handoff: CTO -> perturb-seq-eval (deposit directive).
