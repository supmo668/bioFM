---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-02T01:43
status: created
priority: high
size: task
subject: "CONVENE — chipsim-lbm-audit PVR approved (queued behind your fix cycle); pr-submit still held; merge trunk to r2.3"
in_reply_to: null
---

# CONVENE — chipsim-lbm-audit PVR approved (queued behind your fix cycle); pr-submit still held; merge trunk to r2.3

# CONVENE — status of every held item, and a new PVR queued behind your current cycle

Principal approved a **new workstream**. Consolidating everything you are holding so nothing sits on
an assumption.

## NEW — `chipsim-lbm-audit` PVR approved, queued for `/design` (NOT now — see sequencing)

`workstreams/chipsim-lbm-audit/PVR.md` @ `b48b192`. Module is you; it is a **separate workstream**
with its own PVR/A&D/Plan, and it does **not** advance the M0–M6 ladder.

**What it is.** The audit that decides whether ChipSim's moiety claim is science or decoration:
does Boltz-2 possess *target and pocket* sensitivity, or only *ligand* sensitivity? Three arms —
Boltz-2 affinity, ESM-2 interface, atlas abundance — each against its named non-LBM fallback, both
arms always reported. Designed so a **negative result is publishable**, answering §7's hardest open
question rather than merely blocking the programme.

Two things in it you will care about:
- **Pocket-vs-distal mutation control.** "Affinity dropped under mutation" proves nothing alone —
  any perturbation moves a prediction. The comparator is a matched distal-surface mutant of equal
  mutation count. If pocket mutations don't move it *more than* distal ones, the model isn't reading
  the pocket.
- **R2 seals the pre-registration** with the same digest mechanism you proposed for the panel — the
  run raises if a threshold was edited after results were seen. Your T2 proposal generalized.

**Envelope:** Modal $30 for Boltz-2 only; everything else local on the M5 Max via PyTorch/MPS.
**LM Studio is not in the model path** — it serves GGUF/llama.cpp; ESM-2 and Boltz-2 are PyTorch.
**No AlphaFold provisioning** — AFDB has the wild-type panel precomputed and co-folding models take
mutants from sequence, so a GCP AlphaFold run would regenerate what you can download.

## SEQUENCING — finish what you are in before you start this

1. **Finish the current QG fix cycle** (config.local move, biological numbers out of
   `barrier_panel.yaml`, `load_ratified_panel` validation, live `face` assertion, README:223).
2. **Merge trunk.** You are behind by four signed plan revisions — `1d2e234`, `bfa2c1e` and the
   dispatch commits. Current gate: **`b5443bd` (r2.3)**. D2 resolves on contact; T7:437 now reads
   `basolateral`, so N1's divergence closes; propagate to the five fixtures.
3. **Re-run `/pr-prep`** — trunk merges keep invalidating your receipt, and my coordination commits
   are the cause. Filed upstream; the workaround stands.
4. **Then `/design` for `chipsim-lbm-audit`.** Not before. It is a document phase and will not touch
   slice-1 code, but interleaving two workstreams in one worktree mid-fix-cycle is how conformance
   drift like N1 happens.

## HELD — unchanged, and why

| Item | State | Waiting on |
|---|---|---|
| `/pr-submit` | **HELD** | principal's clearance to push 34+ commits to a public remote. Not granted. Do not submit. |
| T9 / T10 | correctly refused | a genuinely ratified panel |
| slice 2 | not started | declined by ruling — the plan's own scope check |
| T2, T1, T8, T18, T14 | absent | the principal alone |

**T8 is now specified end to end** (r2.3): seven accessions *and* seven faces, delete only on
positive evidence of absence, `chipsim panel seal` as the act of attestation, optional human-only
`airway_evidence`. I have walked the principal through it and the ~25-minute T2 → T1 → T8 sequence
that takes the build from "cannot execute a stage" to fetching real data against a ratified panel.

**AM-6** — exit-3 (pre-register a sample-size contingency, evaluated on the sealed allocation as
written before reading) is with the principal. Undecided. Gates M5, not M0, and not this audit.

## One correction to carry

`chipsim panel seal` does not exist yet — I specified it in T8 before it was built. It is CA work and
it is yours, but it is **not** in the current plan as a task. Flag it back to me with where you think
it belongs and I will land the amendment and re-sign, per the standing rule. Do not add it yourself.
