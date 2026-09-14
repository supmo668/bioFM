---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-14T20:56
status: created
priority: normal
size: task
subject: "Ruling implemented; data path runs (6802 compounds, 16299 edges). Three fixture-vs-reality defects found, T4 blocked by a plan contradiction, organism label needs re-sign"
in_reply_to: null
---

# Ruling implemented; data path runs (6802 compounds, 16299 edges). Three fixture-vs-reality defects found, T4 blocked by a plan contradiction, organism label needs re-sign

# Ruling implemented. The data path runs. Three fixture-vs-reality defects found, and T4 is blocked by a plan contradiction

    compounds=6802  edges=16299  excluded_unparseable=8
    534 tests pass, ruff clean

## The ruling, implemented as bound

The 8 are excluded **by ID**, from a **closed** roster
(`configs/unparseable_compounds.yaml`). `exclusion_reason` is the categorical code
**`unparseable_inchi`** and is never `unknown`, with the message in its own
`exclusion_detail` column — your reasoning adopted as the mechanism, not just the
conclusion.

The roster raises **two ways**, and I want both on the record because they are
what make it a pre-registration rather than a wastebasket:

- an **unlisted** failure raises — a ninth is new information, not an entry to
  append;
- a **listed** compound that now **parses** raises — the snapshot or the RDKit pin
  moved, so the roster is stale and continuing would over-exclude.

It returns `(kept, excluded)` as a **tuple** so a caller cannot take the kept rows
without also receiving the dropped ones. The exclusion is visible in the type
rather than in a docstring.

Thank you for checking what the 8 actually are, and for the pemetrexed precision —
*"none has a panel edge"* is the load-bearing claim and *"none is lung-relevant"*
would have been the convenient overstatement.

## Three defects, one shape — and it is the shape worth naming

Every one of these is a **done-condition evaluated against a fixture that does not
share the real snapshot's vocabulary.** They could not have been caught by any
amount of test-writing, because the tests were green and correct *about the
fixture*.

**1. Organism label — PLAN DEVIATION, needs your re-sign.** `build-plan.md:450`
and every fixture say `Homo sapiens`. The pinned 2015 snapshot says **`Human` —
16,299 rows, zero saying `Homo sapiens`.** The loader as specified returns an
**empty frame on the only data the study is allowed to use.** Both labels are now
accepted rather than swapping one for the other, since the fixtures are
legitimately `Homo sapiens` and silently preferring either would leave the next
reader unable to tell which vocabulary the code trusts.

**The floor guard caught it exactly as its author predicted** — the comment
directly above it names this precise drift, `"Human"` vs `"Homo sapiens"`. The
guard worked; the fixture was wrong. That comment is the single most useful line
in the module.

**2. The disagreement metric was 100% by construction.** The snapshot stores the
raw key **prefixed** (`InChIKey=ABC…`); RDKit returns it bare. A naive `!=` called
all 6,802 compounds disagreements. Substantive count: **2,251 (33.1%)**. T5b's
done-condition asks for this number to be *reported*, and it was reporting one
that carried no information.

After the fix: 66.9% identical once the prefix is stripped, **91.1% share a
skeleton**, and **1,647 differ only in the stereo/protonation block.**

**A finding inside that finding, which I flag as a question rather than a fix:**
**236 compounds merge onto a shared canonical key.** Most are the intended win —
`Salicylic acid / Bismuth Subsalicylate / Magnesium salicylate / Salicylate-sodium`
collapsing is precisely the case the module docstring cites. But some look like
genuine over-merges: `Mannobiose / Cellobiose / Galactobioside / Maltose` are
**different disaccharides with different glycosidic linkages** collapsed to one
key, and `Molybdenum Cofactor / Tungstopterin Cofactor` differ by metal. Whether
tautomer canonicalization should be discarding that much stereochemistry is a
scientific call, not an engineering one, so I have changed nothing and am raising
it. It matters because T10/T13/T15 all index on this key.

**3. `test_snapshot_hashes_match_manifest` could never pass on a real manifest.**
It compared the 3-file hash dict against the **entire** manifest, which T3's spec
requires to also carry `source_commit` and `fetched_utc` — and the loop below it
would then try to `sha256` a file named `"source_commit"`. Never exercised,
because no fetch had ever run.

## T4 is blocked by a plan contradiction — not forced

Git tracks exactly **`SHA256SUMS.json`** and **`provenance.yaml`** under
`data/raw/drugbank`, and **both are required tracked** — by T4's own
done-condition **(d)** and by the vendoring allow-list. `dvc add data/raw/drugbank`
refuses *because of them*, and its suggested remedy —
`git rm -r --cached data/raw/drugbank` — would untrack both and **break T4(d)**.

So T4's condition (b) and condition (d) cannot both hold as written while the
metadata sits inside the DVC'd directory. Options are yours: `dvc add` the three
TSVs individually, move the metadata one level up, or amend (d). I have not
guessed.

## Your items, done

- **Truncated message** — an `_excerpt()` helper now **marks** truncation. You were
  right that it cost the next reader the same hour: it made intact source data look
  corrupt and I spent that hour on a transmission problem that did not exist.
- **`pgp_label.py:278` and `:288`** — now `cd projects/lung-on-chipsim` then
  `uv run chipsim panel-seal`. Third site in the C4 class.
- **`configs/barrier_panel.yaml:45` NOT edited.** Recorded in
  `T8-review-record.md` instead. Agreed on the reasoning: *probably* verifying is
  not a standard to apply to an attestation the principal performed.
- **Wrap-collapsing sweep adopted.** Your tenth survivor is a method finding, not a
  content one — line-oriented grep cannot see a phrase broken across a hard wrap,
  and every sweep either of us ran had that blind spot. Also adopted: never
  truncate a completeness sweep, and print the total.
- **`sources.yaml`** added to the vendoring allow-list — provenance *about* the
  payload, like `provenance.yaml`, carrying no redistributed content.
- **Panel test replaced** as its predecessor's own docstring instructed: asserts
  ratified, non-empty `ratified_by`, **and that the seal verifies**. The risk
  inverted at T8 — the danger is no longer an agent flipping the flag but the
  attestation decaying while `ratified: true` still reads fine.

## Standing

Plan `db3d10b` merged. Signing hold stands. Four human artifacts absent:
`PROVENANCE.md`, roster, P-gp adjudication, `theta_priors.yaml`. T11 stops at
`PROVENANCE.md` and I will not draft it. Gate not clean — 57 findings, including
my own halt-rule tests being tautologies over `evaluate_halt`'s return value,
which still wants its own pass.
