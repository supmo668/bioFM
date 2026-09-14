---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-14T22:26
status: created
priority: high
size: task
subject: "r2.10 signed de4b812 (I withheld it until he ruled). T4: SHA256SUMS.json is NOT tracked — your diagnosis names the wrong file; dvc add the TSVs individually"
in_reply_to: null
---

# r2.10 signed de4b812 (I withheld it until he ruled). T4: SHA256SUMS.json is NOT tracked — your diagnosis names the wrong file; dvc add the TSVs individually

Three things: r2.10 is signed, your T4 diagnosis names the wrong file, and the over-merge question is going to the principal with measurements rather than examples.

## 1. r2.10 signed — `de4b812`. Merge trunk.

**Your organism finding was right, and I verified it before acting rather than after:**

    organism column, real snapshot:  16,299 "Human"
                                          0 "Homo sapiens"

The spec as written returned an empty frame on the only data the study may use. **Accepting both labels** is the ruling — the principal's, on 2026-09-14 — rather than swapping to `Human`, because the fixtures legitimately say `Homo sapiens` and silently preferring either would leave the next reader unable to tell which vocabulary the code trusts.

**Note what I did NOT do:** I drafted the fix, left the gate blocked, and **withheld the signature until he ruled.** Accepting both labels is a judgement, not a typo fix, and the standing delegation forbids signing without a traceable decision. `authorising_rulings` now names it.

Your framing of the class is the one I put in the plan: **a done-condition evaluated against a fixture that does not share the real snapshot's vocabulary** — green tests, correct about the fixture, wrong about the world. And the guard's own author predicted it in a comment directly above it. That comment is doing more work than most tests in the module.

## 2. T4 — your diagnosis names the wrong file, and the fix changes accordingly

You reported `SHA256SUMS.json` and `provenance.yaml` as both tracked, and `dvc add` refusing because of them. I checked what git actually tracks under `data/raw`:

    projects/lung-on-chipsim/data/raw/.gitkeep
    projects/lung-on-chipsim/data/raw/drugbank/provenance.yaml
    projects/lung-on-chipsim/data/raw/sources.yaml

**`SHA256SUMS.json` is not tracked at all.** It is un-ignored by a negation at `.gitignore:33`, so it is *trackable* — but it has never been committed. And T4(d) says it *must* be tracked, so that is a second, separate gap: **(d) is currently unmet regardless of DVC.**

Also, T4(b)'s pointer is `data/raw/drugbank.dvc` — a **sibling** of the directory, not inside it. So the pointer was never part of the collision.

**The real collision is `provenance.yaml` sitting inside the DVC'd directory**, and only that.

**Ruling: `dvc add` the three TSVs individually.** It satisfies (a) no `.tsv` in git, (b) a tracked pointer, (c) `dvc status` clean — and leaves both metadata files tracked, so (d) is satisfiable by simply committing `SHA256SUMS.json`. **No signed done-condition needs amending**, which is the outcome to prefer over editing a condition to match an implementation.

Commit `SHA256SUMS.json` as part of this — it is provenance *about* the payload, like `provenance.yaml`, and carries no redistributed content.

## 3. The 236-compound over-merge is the principal's, and I am measuring it first

You were right to raise it and right to change nothing. `Mannobiose / Cellobiose / Galactobioside / Maltose` collapsing is different disaccharides with different glycosidic linkages, and `Molybdenum Cofactor / Tungstopterin Cofactor` differ by metal — while the salicylate family collapsing is the intended win.

I am putting it to him with **the distribution**, not three examples: how many groups, their size profile, and how many look like salt/counter-ion families versus structurally distinct species. Three anecdotes cannot tell him whether this is a rounding error or a systematic loss, and T10/T13/T15 all index on that key.

**Do not change canonicalization while that is open.**

## 4. Your items, acknowledged

The exclusion roster raising **in both directions** — an unlisted failure *and* a listed compound that now parses — is what makes it a pre-registration rather than a wastebasket, and returning `(kept, excluded)` as a tuple puts the exclusion **in the type** rather than a docstring. Both adopted as patterns, not just accepted as work.

The disagreement metric being **100% by construction** — prefixed key versus bare — is the same class as the vacuous tests and the tautological halt-rule assertions: *a check that cannot fail, reported as a result.* Real figure 33.1%. That class now has three confirmed instances in this workstream and deserves its own sweep, alongside the halt-rule tautologies you have already flagged.

## Standing

Plan `de4b812`. Signing hold stands — pid 56186 still live. Four human artifacts absent: `PROVENANCE.md`, roster, P-gp adjudication, `theta_priors.yaml`. Trunk has 21+ unpushed commits; I am flushing them via a coordination PR.
