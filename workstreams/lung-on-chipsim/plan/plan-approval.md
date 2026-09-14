---
workstream: lung-on-chipsim
plan_path: workstreams/lung-on-chipsim/plan/build-plan.md
plan_hash: de4b812
approved: true
approved_by: Matthew Mo
date: 2026-09-14T15:24
---

# Plan approval: lung-on-chipsim

The human's 1B1 "Over and out" lock in /grill-me IS the final human
plan-review gate. This file records it so /build can verify it.

## Summary
r2.10 (defect fix, NO scope change) — CTO-invoked under the standing delegation, on the principal's explicit ruling of 2026-09-14. T4's edge loader specified organism == 'Homo sapiens'. The pinned 2015 snapshot carries 16,299 rows saying 'Human' and ZERO saying 'Homo sapiens' (verified against the fetched TSV), so the loader as specified returned an EMPTY FRAME on the only data the study is permitted to use. Every fixture said 'Homo sapiens', so no test could have caught it. Principal ruled: accept BOTH labels rather than swapping — the fixtures are legitimately 'Homo sapiens' and preferring either silently would leave the next reader unable to tell which vocabulary the code trusts. Defect class: a done-condition evaluated against a fixture that does not share the real snapshot's vocabulary. No task added, removed or altered.
