# aviary-biosim (bioFM) — review index

<!-- HACP subproject Index · Project=bioFM · L1 — Review · local source. The Notion row
     "aviary-biosim (bioFM) — Index" mirrors this file and is Indexed by "bioFM — Index".
     Written 2026-10-01 by the aviary-biosim worktree agent on the principal's direction.
     Edit here, never in Notion. -->

| | |
|---|---|
| **Project** | `aviary-biosim` — the public Aviary-BioSim submodule (`projects/aviary-biosim`): the `v2r-loop` build loop, the `BioSimEnv` protein-model environment built under it, and the white paper about both |
| **This page** | The bioFM-side index for that work. One screen; it lists the documents that live in *this* repository. The submodule's own documentation is indexed under its own project, `aviary-biosim` |
| **Verdict** | **Delivered and landed.** Aviary-BioSim PR #1 merged to `main` at `301e7fc6` (2026-09-28, no release). The white paper is at Task 13 of 15: its boundary gate is owed, then the CTO's claims review, then the deposit |
| **Protocol** | HACP (`REFERENCE-HACP.md`, shipped with the airdlc plugin). The bioFM-level sections are [`../build.md`](../build.md) … [`../decision.md`](../decision.md) |
| **Public** | The submodule is public. This page names no sequence identifier and no secret |

## Index

| Document | Kind | State |
|---|---|---|
| [Completion walkthrough — product cut](../../../workstreams/_adhoc/aviary-biosim-walkthrough-product.md) | Presentation · §build | current; written by the CTO 2026-09-28, land recorded 2026-09-30 |
| [Completion walkthrough — full technical](../../../workstreams/_adhoc/aviary-biosim-walkthrough.md) | Presentation · §build (sibling of the row above) | current at `ab8f6f5` |

## Where it stands

| Branch | At | State |
|---|---|---|
| `aviary-biosim` | `ab8f6f5` | landed into Aviary-BioSim `main` @ `301e7fc6`; remote branch kept until `whitepaper` is retired |
| `whitepaper` | local, not pushed | plan #272 r2; Tasks 0–12 done; author block, F33 methods and plugin-rename sentence applied 2026-09-29/30; suites re-measured 2026-09-30 (429 green, 48/48 mutants); Task 13 gate owed |

## The applied context — what the environment was built to find out

The v2r loop is a build method; `BioSimEnv` is where it was pointed at a real question. The question
is a drug-manufacturing one: **recombinant human insulin's soluble yield in microbial hosts is limited
by correct folding**, and specifically by forming proinsulin's three disulfide bonds. The computational
counterpart asked here: *does a protein language model, trained only on sequences, treat the six
cysteines that make those bonds as load-bearing?*

```mermaid
flowchart LR
  Q["Manufacturing question<br/><small>what limits soluble insulin yield?</small>"]
  C["Computational counterpart<br/><small>are the disulfide cysteines load-bearing?</small>"]
  E["BioSimEnv<br/><small>ESM-2 over the real UniProt sequence</small>"]
  R["Measured contrast<br/><small>cysteines vs the rest of the mature protein</small>"]
  K["Known biology<br/><small>INS cysteine mutations; Akita Ins2 C96Y</small>"]
  Q --> C --> E --> R
  K -.->|"sets the expected direction<br/>before the run"| C
  R -.->|"agrees with"| K
```
*The expected answer was established independently, before the run. That is what makes this a
validation of the instrument rather than a discovery — and why the paper claims recovery, not biology.*

**Method.** Masked-marginal scan: mask a position, one forward pass, `score(mut) = log P(mut) − log P(wt)`.
110 residues ⇒ 110 passes covering every substitution. Input is fetched live, never bundled.

| What was measured | Value | Label |
|---|---|---|
| Single-residue substitutions scored | 2,090 (1,634 in the mature protein, from position 25) | measured, re-run 2026-09-26 |
| Mean score at the six disulfide cysteines | **−13.02** | measured, re-run |
| Mean score at every other mature residue | **−5.85** (−5.53 including the signal peptide) | measured, re-run |
| Cysteine positions | 31, 43, 95, 96, 100, 109 | measured, re-run |
| Scan runtime | 9.6 s re-run (7.3 s reported for the published run) | measured / reported |

**The control that makes it a result and not a coincidence.** The C-peptide (57–87) is excised during
maturation, so substitutions there should be tolerated. Measured scores at five of its positions:
**+1.53, +1.08, +0.18, +0.17, −0.10** — at or above zero, against −13.02 at the cysteines. *The agent
chose these controls itself; the objective never mentioned the C-peptide.*

**The agent's own run.** 66 measurements over 5 rounds, 34 distinct positions, 15,115 completion tokens
(one round recorded none), one trace root of 36 in the project's trace store. Label: *reported, artifact
counted* — counted from the run artifact, not re-measured for the paper.

**Reproducibility of the figure.** The 2026-09-26 re-run matched the published run on **every** headline
field, at the same device and seed, with the model revision and a SHA-256 of the 2.6 GB weights file
recorded alongside. Input provenance: UniProt P01308, release 2026_03, sequence SHA-256 recorded;
the identifier is published in the clear by ruling (F33) because the association is already public here.

**What this does not claim.** Recovery of a constraint that was already known — ESM-2 has seen insulin;
no new biology, and no wet experiment. The ortholog-embedding comparison the script also computes is
**not** in the evidence set, so it is not a claim of this work. Budget enforcement is built and
sealed-tested but has never run end to end, because no token price is declared. F31 (cache read-path
integrity) is held, so the published numbers' provenance is not verifiable from the repository alone.

Evidence (L3, in the `whitepaper` branch of the submodule): `paper/evidence/science.json` (scan + re-run
match), `paper/evidence/science-input.json` (input provenance), `paper/evidence/agent-run.json` (the
agent's rounds), `paper/claims.yaml` (every number in the paper bound to a file:field, build fails
otherwise). Code: `science/esm_tool.py`, `science/run_experiment.py`, `science/biosim_env.py`,
`science/run_discovery.py`.
