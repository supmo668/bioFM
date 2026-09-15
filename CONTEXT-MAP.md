# Context Map

## Contexts

- [ChipSim](./projects/lung-on-chipsim/CONTEXT.md) — lung-on-chip simulator; the language of its evaluation and data layers
- [V2R Loop](./docs/v2r-loop/CONTEXT.md) — the vision-to-reality loop — aligns a stated vision into a bounded spec, then builds it out requirement-to-function (decisions: [`docs/v2r-loop/adr/`](./docs/v2r-loop/adr/))

## Relationships

- **V2R Loop → ChipSim**: ChipSim's PVR supplies **requirements**; the V2R Loop decomposes them into **build units** and discharges them. The backlink `satisfies: R<n>` is the only coupling.
- **Shared vocabulary**: both contexts use **sealed** in the same sense — fixed before the actor who is constrained by it gets to see it (ChipSim's *sealed allocation*, the V2R Loop's *sealed test*).
- **Deliberately not shared**: ChipSim's **ratchet** (keep-if-better on a gate scalar) and the V2R Loop's monotonic register are different mechanisms. See the V2R Loop glossary.
