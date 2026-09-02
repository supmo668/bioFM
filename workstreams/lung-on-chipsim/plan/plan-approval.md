---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: 50dbaec
approved: true
approved_by: Matthew Mo
date: 2026-09-01T18:48
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.4: T7a (CA, 5 min) builds chipsim panel seal, placed before T8 because the seal IS the attestation and a missing tool makes T8 uncompletable. Adds Global Constraint (4): an agent may never run panel seal against the live config. One CA task added (T7a); human-blocker count unchanged at five.
