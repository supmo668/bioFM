# Context Map

## Contexts

- [ChipSim](./projects/lung-on-chipsim/CONTEXT.md) — lung-on-chip simulator; the language of its evaluation and data layers
- [Build Loop](./docs/build-loop/CONTEXT.md) — the requirement-to-function build-out loop that constructs the other contexts' code (decisions: [`docs/build-loop/adr/`](./docs/build-loop/adr/))

## Relationships

- **Build Loop → ChipSim**: ChipSim's PVR supplies **requirements**; the Build Loop decomposes them into **build units** and discharges them. The backlink `satisfies: R<n>` is the only coupling.
- **Shared vocabulary**: both contexts use **sealed** in the same sense — fixed before the actor who is constrained by it gets to see it (ChipSim's *sealed allocation*, the Build Loop's *sealed test*).
- **Deliberately not shared**: ChipSim's **ratchet** (keep-if-better on a gate scalar) and the Build Loop's monotonic register are different mechanisms. See the Build Loop glossary.
