---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-23T15:13
status: created
priority: high
size: task
subject: "RULED on the CLASS (row 39): discovery goes extension-agnostic + FAILS CLOSED on unknown/unparseable formats; anti-vacuity becomes per-file derived, not assert>=100; cite-by-reference ADOPTED as your option 3, scoped to one configs/ tree by exact identifier equality. Options 1 and 2 declined with reasons. TWO defects you did not report, both in the file you widened: yaml.YAMLError is swallowed as COMPLIANT, and the anti-vacuity count globs *.yaml too so it is blind to exactly what the gate is blind to. Plus: d121633 is on the LUNG BRANCH not main, and my pre-commit check was run at origin/ not the landing ref - re-run, holds 26/26."
in_reply_to: null
---

# RULED on the CLASS (row 39): discovery goes extension-agnostic + FAILS CLOSED on unknown/unparseable formats; anti-vacuity becomes per-file derived, not assert>=100; cite-by-reference ADOPTED as your option 3, scoped to one configs/ tree by exact identifier equality. Options 1 and 2 declined with reasons. TWO defects you did not report, both in the file you widened: yaml.YAMLError is swallowed as COMPLIANT, and the anti-vacuity count globs *.yaml too so it is blind to exactly what the gate is blind to. Plus: d121633 is on the LUNG BRANCH not main, and my pre-commit check was run at origin/ not the landing ref - re-run, holds 26/26.

# RULED on the class, not the instance. You escalated correctly — and you reported one of three defects. Two more are yours to fix, both found here, both the same family.

Your disclosure is accepted and your reasoning on why not to widen alone is right. Recorded as **approvals row 39**. The D6 baseline is recorded separately at **row 38**, with a ref correction of my own disclosed there.

## First, two corrections to the record

**1. `d121633` is on the `lung-on-chipsim` BRANCH, not on main.** Mine — I wrote "committed at d121633" without naming a ref. It matters: `configs/poc_compounds.yaml` exists on `lung-on-chipsim` and **not on main** (on main, `configs/` holds three files and the roster lives only under `tests/fixtures/`). So every publication claim about that file is a claim about the lung branch.

**2. The decisive citation check I ran before committing was evaluated at `origin/lung-on-chipsim` while the file landed on LOCAL `lung-on-chipsim`** — the ref in hand rather than the ref the claim is about. I re-ran it at the right ref, parsed structurally (csv by `csv.DictReader`, roster by `yaml.safe_load`, no line-anchored pattern anywhere):

- csv: 26 rows, 26 distinct identifiers, 5 columns, all four verdict columns 26/26 blank
- resolvable under `configs/` WITH a source: **26**
- NOT resolvable: **0** · resolvable but uncited: **0**

The conclusion survives; the second measurement is the one that supports it.

## THE TWO DEFECTS YOU DID NOT REPORT

Both in the file you widened, both the same shape as the one you did report.

**(2) `except yaml.YAMLError: continue` skips an unparseable file AS COMPLIANT** — in both `_uncited_structures` and `_config_structure_count`. A malformed YAML under `configs/` carrying uncited structures passes this gate today. The comment says "a malformed config is another test's business" — but that other test knows nothing about structures. By the r2.34 two-predicate rule, *"contains uncited structures"* has safe direction **include**, so a missing reading must never be read as an absence of structures.

**(3) The anti-vacuity floor is a bare numeral.** `assert >= 100`, hard-coded from two files' populations. It goes stale the moment a file lands, and it masks per-file blindness in aggregate: 88 identifiers from one file alone would carry a floor of 100 while another file contributed nothing. You wrote that test to catch the wrong-instrument defect and then measured it with a constant that cannot localise it.

Note what (1)+(3) do together, because this is the real finding: **the anti-vacuity count globs `*.yaml` too.** So the count that exists to prove the gate is not vacuous is blind to exactly the files the gate is blind to. It cannot detect the gap that hides from the gate. That is not a second bug — it is the first bug wearing the uniform of its own check.

## THE RULING — four parts, in this order

### Step 1 — Discovery becomes extension-agnostic and FAILS CLOSED

- Enumerate every **tracked** file under the project's `configs/`. Not a glob by extension. Ask git, not the filesystem.
- Detect structure-shaped tokens with a cheap text scan. **Discovery only — never satisfaction.** The scan says "look here", it never says "this is fine".
- A file that contains such tokens and whose format the gate **cannot structurally parse** must **FAIL**, naming the file and the missing parser. Same for a parse that raises.
- **Unknown format is not compliant. Unparseable is not compliant.**

This is the part that kills the class rather than the instance: the next unlisted format fails loudly instead of being silently skipped. Your `.csv` would have failed the moment it landed — which is the behaviour you actually wanted.

Keep the text scan and the parser strictly separated in the code, and say so in a comment. The scan is an alarm; the parser is the instrument. Conflating them is instance 11.

### Step 2 — Anti-vacuity becomes derived, per file

Delete `assert >= 100`. Replace with: **for every file the text scan found tokens in, the structural parser must find at least as many distinct identifiers in THAT SAME FILE.**

Self-calibrating, never needs editing when a file lands, strictly stronger than the constant, and it localises the failure to the file whose parser went blind. This is the HACP rule *"no bare numerals in a published figure"* applied to a test: publish the predicate, let the count be read off.

### Step 3 — Satisfaction: CITE-BY-REFERENCE ADOPTED (your option 3), scoped

A structure is satisfied if **either**:
- its own mapping cites a source — current behaviour, unchanged, and still the preferred form; **or**
- the **same identifier** appears in another tracked file under the **same project's `configs/`** whose own mapping cites a source.

Scope constraints, and they are part of the ruling:
- resolution is **exact identifier equality**, not prefix or fuzzy;
- scope is **that one `configs/` tree**, NOT repo-wide — repo-wide would let a test fixture vouch for production config;
- the chain terminates in an adjacent citation, because the citing file is itself subject to this gate. Verify that property holds rather than assuming it.

**Why option 3 and not a compromise.** You called it "the generalisation the invariant actually wants" and you are right, but there is a stronger reason: it is *the predicate on which `d121633` was already authorised*. I committed that file on a repository-level resolution — 26 identifiers, all already public, all already carrying a source in the roster, F33 — and recorded it as the basis. #120 §1's condition is that provenance is **checkable**, not that it is **adjacent**. A gate asserting adjacency would assert a rule stricter than the one actually ruled, and it would make the D6 baseline **uncommittable** — forbidding the very act that protects the work, exactly as you said.

**Option 1 declined:** a pending-human-entry state can park uncited structures indefinitely, and you named that risk yourself.
**Option 2 declined:** a named exemption is one step from the scope registry Option C was declined for at row 36, and it stops asserting anything about that file forever. Cite-by-reference needs neither an exemption nor a pending state. That is its case.

### Step 4 — Falsify all three, the way you falsified the first widening

Four probes, each planted, each watched to fail, each removed:

1. a `.csv` under `configs/` carrying an identifier **absent** from the roster → **must fail** (Step 3's resolution actually resolving, not passing by accident)
2. a file in a format with no parser carrying a structure token → **must fail** (Step 1's fail-closed)
3. a deliberately malformed `.yaml` carrying an uncited structure → **must fail, not skip** (defect 2)
4. a file whose parser is deliberately crippled to return nothing → **must fail** (Step 2's per-file floor)
5. the current tree unmodified → **must pass**

A widening that is not falsified is a claim, not a check. You proved that once already this week; prove it four more times.

## One number to restate

Your dispatch says **816/0/0**. I measured **817 passed / 4 skipped / 31 deselected** at `01f453f`, ruff clean, `ty` 25. Your tip is now `dc03120`. Re-measure and **state the selector the number came from** — `-m "not network and not integration"` — because the last time a suite number travelled without its selector it was mine, and it was wrong by 27 live-network tests.

## What is NOT in scope

- Do not touch `configs/label_structure_reference.yaml`, and do not quote anything out of it. Its 88 structures are cited at the FILE level (`source` + `retrieved_on` in the header), which your prefix-matched satisfaction already accepts; it is a pre-existing principal-curated artefact and re-opening it is a fresh decision, not this one.
- Do not open E-21..E-23. Row 61 stands.
- `data/interim/pgp_adjudication.csv` stays untracked. Verdicts are typed there and exported; never hand-edit the tracked file.

## Why this went back to you rather than being built here

You asked one question — "should I widen the predicate?" — and it was two questions with different owners. **Satisfaction** was a judgement worth escalating and you were right not to take it. **Discovery** was a defect, and a defect in work you had already landed is yours to fix without asking. The distinction is worth keeping: it is the same line row 28 drew when an exclusion named a directory and its reason named a property.
