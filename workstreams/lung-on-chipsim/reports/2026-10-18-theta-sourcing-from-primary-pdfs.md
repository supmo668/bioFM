# θ sourcing from primary PDFs — 2026-10-18

**Author:** biofm/matthew-mo/cto · **Status:** values extracted and quoted; **AWAITING PRINCIPAL RATIFICATION**
**Authority:** principal, 2026-10-18, verbatim: *"use undermind research tool to fill the 6 fields and
leverage the pdf provided here /Users/mo/Documents/Huh10…pdf and /Users/mo/Documents/Huh12b…pdf"*
**Governing directive:** `origin/claude/inspiring-archimedes-h0we1b` (39351f3)
`workstreams/lung-on-chipsim/experiment-setup/experimental-design.md`, which governs where it
conflicts with earlier reasoning (principal, 2026-10-18).

**Device lock applied (directive §3a):** θ describes **one** device — the Huh 2010 alveolar chip, with
Huh 2012 as the corroborating device description. Benam 2016 (rigid polyester membrane) and
Emulate-era commercial figures are excluded. No value below comes from any other device.

## 1 · What changed, and the honest correction

The directive recorded that **no flow candidate "survived scrutiny"** and that **Huh 2010 names the ECM
"only generically, without type or concentration."** Both statements are **true of Huh 2010 and of
search snippets** — I verified them against the paper. They are **no longer true once Huh 2012 is
readable**, and Huh 2012 is the paper that settles both.

So the egress block, not the evidence, was the binding constraint. The directive was right to refuse
to write the values; with the PDF in hand they are citable.

**The correction that matters is attribution, not value.** My earlier Q1 answer recorded
`flow = 50 µl/h` and `coating = fibronectin` as coming from **Huh 2010/2012 jointly, "According to
PubMed," with no quote.** Both values are right; the attribution was wrong and unquoted — they are
**Huh 2012**, and Huh 2010 supports neither. A right number with a wrong citation is the defect this
workstream exists to study, so it is corrected in place with this disclosure rather than left standing.

**A trap avoided.** Huh 2012 also states a flow of **~200 µl/min** — that is the **TBAF etchant during
fabrication**, not perfusion. A third figure, 0.5 ml/min, is the **whole-mouse-lung** perfusion. Either
would have been a plausible-looking `flow_ul_min`, and both are exactly the contamination class §3a
warns about (a simulation input, a flush, or a different system).

## 2 · The six fields

| Field | Value | Status | Source + verbatim quote |
|---|---|---|---|
| `membrane_um` | **10** µm | **cited** | Huh 2010: *"a 10 μm-thick porous PDMS membrane (containing 10 μm-wide pentagonal pores)"*; and *"separated by a 10 μm-thick PDMS membrane containing an array of through-holes with an effective diameter of 10 μm"*. Corroborated by Huh 2012: *"a thin (10 μm), porous, flexible membrane coated with ECM"* |
| `strain_pct` | **10 %** at **0.2 Hz** | **cited** | Huh 2010: *"Application of physiological cyclic strain (10% at 0.2 Hz)"*; restated *"(10% strain at 0.2 Hz)"*. Physiological range given as *"physiological levels of strain (5~15%)"*; a separate figure panel uses 15% for visualising cell distortion |
| `flow_ul_min` | **50 µl/h** = **0.833 µl/min** | **cited** | Huh 2012: *"After cell attachment, steady flows of culture media were driven in both the upper and lower channels at 50 μl/h (fluid shear stress ~ 0.2 dyne/cm²)."* Seeding perfusion stated separately as *"a syringe pump at a volumetric flow rate of 50 μl/h"* |
| `coating` | **fibronectin, 5 µg/ml in carbonate buffer** | **cited** | Huh 2012: *"the porous membranes embedded in the central culture channels were coated with fibronectin (5 μg/ml in carbonate buffer)."* Huh 2010 is deliberately weaker: *"coated with ECM (fibronectin or collagen)"* — a disjunction with no concentration |
| `porosity` | — | **UNRESOLVED → `assumed: true` + stated width** | Pore size is cited (10 µm effective diameter, **pentagonal**), but **neither paper states a pitch, spacing, or pore density**, so §4's formula has no input |
| `area_mm2` | — | **UNRESOLVED** | Channel cross-section **is** cited — Huh 2012: *"The cross-sectional size of the microchannels is 400 μm (width) × 100 μm (height) for the central culture channels"* — but **no overlap length and no culture area** appears in either paper, so no product can be formed |

**Cross-check available for `flow`.** The quoted shear stress (~0.2 dyne/cm²) is an independent anchor
on the same sentence, so the flow row can be validated rather than merely transcribed. Note this is
*two orders of magnitude* below the 15 dyne/cm² in Huh 2010 — that figure is an **endothelial
pre-conditioning** step, not device perfusion, and must not be used as θ.

## 3 · Two overrides this read adds to the directive

**(a) §4's porosity formula does not apply as written.** It offers square and hexagonal lattices of
**circular** pores. The pores here are **pentagonal** with a 10 µm *effective* diameter, produced by an
*"array of 50 μm-tall circular posts"* pressed through a spin-coated layer. So even with a pitch, the
circular-pore area term would be wrong for this membrane. The honest entry remains `assumed: true` with
a width wide enough to span plausible pentagonal packings — not a lattice formula applied to the wrong
pore shape.

**(b) `area_mm2` needs Huh 2013, which was not supplied.** Huh 2010 offers only an order of magnitude —
channels *"only millimeters in width"* — which cannot produce a product. This is the one field where
the directive's prognosis holds exactly: it needs the Nature Protocols device layout.

## 4 · Undermind was NOT used — it is not connected

The instruction named the Undermind research tool. It is **unavailable in this session**: the MCP server
reports `not connected`. I did not substitute a web search for it, because the directive's whole point
is that a search summary cannot settle a θ value — *"a citation assembled from search snippets is the
same object with a better alibi."* So the two unresolved fields stay unresolved.

**Note on the device lock for whoever runs Undermind next.** The directive calls Stucki 2015's SI
"open access and useful for cross-checking method" — and it **does** state a pore density. It must
**not** be used for `porosity` here: Stucki is a different device with a much thinner elastic membrane,
and importing its pore density would produce a merged θ describing no real chip.

## 5 · What this unblocks, and what it does not

**Unblocked:** four of six θ rows can go to `cited` with quotes, which is enough to parameterise the
diffusive path (`membrane_um`), the mechanical modulation (`strain_pct`), the residence time
(`flow_ul_min`), and the barrier condition (`coating`).

**Still blocking a fully `cited` M1:** `porosity` (needs a pitch for this device, or a ratified
`assumed` width) and `area_mm2` (needs Huh 2013 or any paper stating this device's culture area or
overlap length). Both are *scale* terms on the transfer coefficient, so with `α` fitted rather than
predicted they degrade the interpretation of `α` rather than blocking the fit.

**`doi_confirmed` remains unset.** The PDFs establish the *content*; I did not confirm DOI strings
against a resolver, because `doi.org` is one of the 403-blocked hosts.

## 6 · Ratification

Every value above is quoted, so the worksheet validator's condition (no value without its backing) is
satisfiable. Under standing practice no agent writes a biological or device number into the record on
its own authority: **these rows need the principal's ratification before they enter
`sourcing-worksheet.yaml`**, which currently lives only on the unlanded branch 39351f3.
