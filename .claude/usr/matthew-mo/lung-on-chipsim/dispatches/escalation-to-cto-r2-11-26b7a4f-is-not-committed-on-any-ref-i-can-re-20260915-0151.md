---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-15T08:51
status: created
priority: high
size: task
subject: "r2.11 (26b7a4f) is not committed on any ref I can reach; plan-gate still verifies de4b812. Not building. Guard measured read-only meanwhile"
in_reply_to: 98
---

# r2.11 (26b7a4f) is not committed on any ref I can reach; plan-gate still verifies de4b812. Not building. Guard measured read-only meanwhile

# r2.11 (`26b7a4f`) is not committed on any ref I can reach — not building until it is

You asked me to run `plan-gate verify --workstream lung-on-chipsim` before starting. It verifies
**`de4b812` (r2.10)**, not `26b7a4f`:

    ✓ Plan-gate verified: lung-on-chipsim (hash de4b812)

I checked where r2.11 could be before concluding it is absent — twice today I have mistaken
"not where I looked" for "not there":

    git fetch origin                                   (clean)
    git log --oneline lung-on-chipsim..origin/main     (empty)
    git log --oneline lung-on-chipsim..main            (empty — main tip df89f50, PR #6)
    git log --all --oneline -S26b7a4f                  (empty — no commit on ANY ref adds or removes the string)
    git log --all --oneline --grep=r2.11               (empty)

A content search (`-S`) finds the hash wherever it was recorded, regardless of commit subject.
So r2.11's amended T4(b)/(c) and the stereo-guard ruling exist in your dispatch but not in
any signed plan on disk. Building either against `de4b812` would be implementing an unsigned
plan. **Most likely it is committed in your checkout but not yet on `main`** — could you land
or push it?

## Not idle meanwhile — measuring the guard read-only on the real snapshot

No module is edited. I re-implemented the guard exactly as ruled in a scratch script and ran
it over all kept compounds. A full report follows in a separate dispatch once one question is
settled; the headline is in now because it bears on the ruling itself:

- **The guard achieves its target:** tautomer-stage merge groups go from 48 to 4. L/D-Thr,
  L-Ile/allo-Ile, and the L/D amino-acid pairs all separate.
- **It fires on a quarter of the snapshot**, not a handful — every L-amino acid, plus drugs
  such as valsartan and ramipril. Firing mostly changes nothing about merges, but 44 existing
  groups split.
- **Open question before I report further:** some splits look like **true tautomers of one
  compound** (the benzimidazole 1H/3H pair; a keto/enol trio differing only in E/Z geometry).
  If those split because the ruling counts `/b` (double-bond geometry) as stereo, then "reject
  any step that alters stereo" is broader than the examples it was written for. I am measuring
  that per layer now, not asserting it.

Canonicalization untouched. T4 not executed.
