---
type: plugin-feedback
target: aiadlc plugin (aiadlc-plugins)
plugin_version: 0.56.0
reporter: biofm/matthew-mo/cto
date: 2026-09-17
scope: plugin / operating-system behavior — NOT repo/app work
---

# Run records carry no provenance, so a seeded record reads as an observed drain

Surfaced while auditing `/v2r-loop` against the run it produced in
`projects/aviary-biosim`, where fixture run records sat in the store looking
exactly like real ones and I could only tell them apart by diffing against the
script that wrote them.

## 🟠 1. `drain-end` writes no marker saying the record came from an observed drain

**File:** `tools/register`, `cmd_drain_end` — lines 512–525

```python
    record = {
        "drain": run.get("drain"),
        "register_sha": "sha256:" + sha256_file(store_path()),
        "instinct_pin": run.get("instinct_pin"),
        "seed": run.get("seed"),
        "ceilings": run.get("ceilings", {}),
        "closed": [u["id"] for u in data.get("units", []) if u["state"] == CLOSED],
        "parked": [u["id"] for u in data.get("units", []) if u["state"] == PARKED],
        "outcome": args.outcome,
    }
```

**Symptom.** Nothing in the record states how it was produced. Any process that
writes a file of this shape into the store directory is indistinguishable from
`drain-end`'s own output — and SKILL.md Stage 4 step 1 reads exactly these files
as the evidence substrate:

> **Read the run record** (`run-record-<n>.json`) and the park evidence: which
> units parked, at which attempt, on what category. **That substrate always
> exists.**

"Always exists" is true. "Describes a drain that happened" is not checked.

**Root cause.** The record has no `produced_by` field and no integrity binding.
`register_sha` digests the *register*, not the record, so it neither proves the
tool wrote the record nor detects a hand-edit. The legitimate producer is unique;
nothing marks its output as such.

**Evidence this is not hypothetical.** In `projects/aviary-biosim`:

- `dashboard/seed_demo_run.py` writes `.v2r/run-record-{1,2,3}` with this exact
  schema, and `.v2r/register.yaml` with 23 units whose statements match the
  seeder's `UNITS` list one for one.
- Those records are what the marimo dashboard deliverable renders.
- They are **provably not tool output**, but only by inference after the fact:
  every `sealed_test_sha`, `pre_claim_sha` and `evidence` is `null`; records 2
  and 3 are byte-identical; and record 1 lists `U-014`, `U-015` and `U-017` in
  **both** `closed` and `parked` — a state `cmd_drain_end` cannot emit, since it
  derives both lists from the same mutually-exclusive `u["state"]`. That
  impossibility is the cleanest proof available that the tool did not write them,
  and it is reasoning no consumer performs.
- The real drain (6 units) left **no** run record in the repo at all, so the only
  records present are the synthetic ones.
- `docs/DEMO.md` compensates with prose, telling the presenter to say out loud
  which run is on screen: *"a judge who catches you presenting fixture data as
  live has stopped listening."* A documentation workaround for a data-model gap.

**Why it matters beyond one repo.** `/v2r-loop`'s own **Never** list says *"Present
a predicted number as a measured one"* and Stage 5 says *"Every figure comes from a
run that happened."* Those rules bind the agent; nothing binds the tooling, so the
one artifact Stage 4 and Stage 5 both consume cannot answer "did this run?".
This is the same defect shape the framework has now hit repeatedly — a mechanism
reporting success while the property it exists to guarantee is absent (cf.
`git-safe-commit` no-op success; the referee signing a fully-skipped suite).

**Fix.** Smallest viable, additive:

1. `cmd_drain_end` stamps the record:

   ```python
   "produced_by": f"tools/register@{VERSION}",
   "recorded_at": iso(now()),
   "record_sha": "sha256:" + sha256_of(canonical_json(record_without_this_field)),
   ```

2. Stage 4 (and any dashboard) treats a record lacking `produced_by`, or whose
   `record_sha` does not verify, as **unverified** — read it if you like, but
   label it, and never let it close the "did this improve?" question.

3. Optionally have the seeder path set `"produced_by": "seed/demo"` explicitly, so
   demo data is self-declaring rather than merely unmarked.

**Effect once applied.** A synthesized or hand-edited record can no longer be read
as evidence that a drain occurred; the honesty rule that currently lives in prose
gets a mechanical backstop; and presenting a dashboard becomes safe by
construction rather than by the presenter remembering a caveat.

**Status:** open
