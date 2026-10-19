# Experiment set-up — the M1 inputs, agent-drafted from cited sources, principal-ratified

**Status: PROPOSED. Nothing in this directory is read by the model until the principal copies it
into `projects/lung-on-chipsim/configs/`.** That copy is the ratification; no agent step performs it.

## Why this directory exists, and what rule it operates under

Global Constraint #1 of the build plan says no coding agent writes a biological number, and S6
enforces it by requiring that `configs/theta_priors.yaml` not exist. On 2026-10-08 the principal
instructed, verbatim:

> *"Resolve tests or CI and research to fill the 6 fields with best effort from known data
> sources. Unbacked data cannot be used and reference must be cited in the experimental design
> for molecular specification. Approximations could be used where metholdogy is supported.
> Create the most informed set-up to initiate the LungChim modelling & simulation"*

That instruction amends the constraint for the M1 inputs to the pattern r2.15 item 1 proposed for
`PROVENANCE.md` and the principal declined there: **agent-drafted from cited sources, principal-
ratified.** Three things keep the amendment honest:

1. **Every number carries its citation and its provenance class.** `cited` means the value is
   quoted from a fetched primary source; `derived` means it is computed from quoted values by a
   stated formula; `assumed` means no citable value was found and a width is stated. The class
   is in the file, not only in the prose.
2. **The files live here, outside `configs/`.** S6's absence guard is untouched and still passes.
   The act of copying a file into `configs/` is the human's ratification, exactly as the scaffold
   flow intended; the validators then accept or refuse it on the same terms as a hand-written one.
3. **The validators are the same ones.** `chipsim theta-check`, `transport-prior-check` and
   `reference-compounds-check` were run on every proposed file before it was committed; the
   output is recorded in `experimental-design.md`.

## Files

| File | Plan task | Validator | Ratify by |
|---|---|---|---|
| `theta_priors.proposed.yaml` | T20 | `chipsim theta-check --theta <path>` | `cp` to `configs/theta_priors.yaml` |
| `transport_prior.proposed.yaml` | T28 | `chipsim transport-prior-check --prior <path>` | `cp` to `configs/transport_prior.yaml` |
| `m1_reference_compounds.proposed.yaml` | T21 | `chipsim reference-compounds-check --reference <path>` | `cp` to `configs/m1_reference_compounds.yaml` |
| `experimental-design.md` | — | — | the document every number above cites into |

## Ratify

```bash
cd projects/lung-on-chipsim
S=../../workstreams/lung-on-chipsim/experiment-setup

# Read the design first. Each value's citation and class is there.
# Then, for each file you accept as written (edit it first if you do not):
cp $S/theta_priors.proposed.yaml            configs/theta_priors.yaml
cp $S/transport_prior.proposed.yaml         configs/transport_prior.yaml
cp $S/m1_reference_compounds.proposed.yaml  configs/m1_reference_compounds.yaml

uv run python -m chipsim.pipeline theta-check               --theta     configs/theta_priors.yaml
uv run python -m chipsim.pipeline transport-prior-check     --prior     configs/transport_prior.yaml
uv run python -m chipsim.pipeline reference-compounds-check --reference configs/m1_reference_compounds.yaml
```

After the copy, `test_s6_human_owned_configs_are_absent` will fail by design: it asserts the
file does not exist. That failure is the signal that T20 is delivered, and the test is to be
replaced by the CTO with the attribution check its sibling (`test_s6_live_panel_ratification_is_
attributed_and_sealed`) now shows the shape of, carrying the approval-log row that records who
ratified and when.
