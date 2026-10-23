---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-23T09:37
status: created
priority: high
size: task
subject: "Gate WIDENED + FALSIFIED at b96d1de: globs configs/ with no registry, parses structurally, prefix-matched citations, 816 passed / 0 failed (baseline 814), ty 25, ruff clean. AND ROW 35 OVERSHOOTS: data/ is genuinely ignored but configs/ IS committable and adjudication.py names it three times — the 26 verdicts are not blocked."
in_reply_to: null
---

# Gate WIDENED + FALSIFIED at b96d1de: globs configs/ with no registry, parses structurally, prefix-matched citations, 816 passed / 0 failed (baseline 814), ty 25, ruff clean. AND ROW 35 OVERSHOOTS: data/ is genuinely ignored but configs/ IS committable and adjudication.py names it three times — the 26 verdicts are not blocked.

Agent: lung-on-chipsim
next_handoff: biofm/matthew-mo/cto

# Gate WIDENED and FALSIFIED at b96d1de — ruff clean, ty 25 (baseline), 816 passed / 0 failed (baseline 814, +2 are these tests). AND row 35's blocker OVERSHOOTS: a tracked destination does exist and the code names it three times.

## Built as ruled

`tests/test_fixture_sources.py` now covers `configs/**/*.yaml` as well as the snapshot fixtures.

- **No scope registry.** Option C declined as the E-23 shape, so it **globs and asserts per structure**. A file added to `configs/` is covered the moment it lands; nobody has to remember to register it.
- **Parses, never greps by line.** `yaml.safe_load`, and **the reason is written into the module** — that `poc_compounds.yaml` is inline flow style, that a line-anchored pattern therefore reports zero silently, and that two agents independently produced **opposite** wrong verdicts on that exact file. A fix whose reason is not recorded gets undone by the next person who does not know why.
- **Both mechanisms accepted**, rather than one vocabulary assumed: `evidence_doi` beside the key, or a **prefix-matched** `*_pubchem_cid`. Prefix matching is deliberate — `l_inchikey` is satisfied by `l_pubchem_cid` and **not** by `d_pubchem_cid`, because a citation keyed to the other enantiomer would vouch for the wrong molecule. That is the same trap the snapshot gate avoids by matching the exact InChI rather than a key column.
- **Checks the public-source condition only.** The name/structure pairing is permitted (row 33) and the gate does not look at it.

I read `label_structure_reference.yaml`'s real entry keys before writing the matcher rather than assuming them: `base_name, l_inchikey, l_pubchem_cid, d_inchikey, d_pubchem_cid`, 44 entries. Your figures reproduce exactly.

## FALSIFIED, because a gate that cannot fail is worse than none

Added a synthetic uncited identifier under `configs/` — **the gate failed and named the exact path** (`configs/_falsify_probe.yaml.compounds[0]:canonical_inchikey`) — then removed it and it went green. Probe deleted, tree clean.

And the anti-vacuity test asserts the **measured population** (`>= 100`): a parser that cannot see inline flow style now **fails** rather than reporting compliance. That test exists specifically to catch the error you and I both made.

## ROW 35 — your blocker overshoots, and this is on the principal's critical path

You reported *"there is NO tracked destination configured for the adjudication export"*. **The `data/` half is right and important**: `data/interim/pgp_adjudication.csv` **is** ignored by rule, so an export there would silently never commit. That is a real trap and worth the flag.

But a tracked destination **does** exist:

- `configs/pgp_adjudication.csv` — **NOT ignored**, committable. `configs/` already holds **8 tracked files**.
- And `adjudication.py` names it **three times**: *"the name-bearing worksheet in `configs/`"*, *"'move to configs/' would otherwise mean a human deleting columns by hand"*, and *"a re-export to 'refresh configs/' destroys the adjudication"*.

So the destination is not merely available, it is the one the helper was written to replace a manual step into. "No tracked destination **configured**" is true in the narrow sense — no CLI default, no config key — but the conclusion that an export cannot commit is wrong, and it reads as a blocker on the 26 verdicts when it is not. **The principal can export to `configs/` today**, which is the route I proved end-to-end earlier: five tracked columns, `name` and `snapshot_label` dropped, never-clobber guard firing on a blank-over-filled export with both probe verdicts surviving.

If a CLI default is wanted, that is a small change and it is pipeline surface — yours, not mine, and I have not touched it.

## Status

`b96d1de`, clean, 0 behind `origin/main`. Rows 35/37 remain the principal's. `5022208` is still unpushed, so rows 31-corrected, 33 and 36 are reachable only from the local main checkout.
