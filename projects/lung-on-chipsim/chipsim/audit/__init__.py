"""ChipSim LBM audit — `chipsim-lbm-audit` workstream, A&D r1.4.

This package is the audit, not the simulator. It is deliberately separate from
`chipsim.harmonize` / `chipsim.eval`: the audit asks whether Boltz-2 is sensitive
to *which protein* it is given, and an audit that shares state with the thing it
audits is not one.

**Nothing here is sealed and nothing here has run.** The pre-registration
(`configs/audit/prereg.yaml`) does not exist yet, and by R2 no arm may execute
without it.
"""
