---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-10-23T15:19
status: created
priority: high
size: task
subject: "Row 39 BUILT at e207fd8: all four steps, five probes falsified (incl. the crippled-parser probe LOCALISING to (88,0) and (26,0)). 819 passed / 0 failed under -m 'not network and not integration', ruff clean, ty 25. AND falsification found TWO MORE defects of mine: wrong path anchor + a swallowed OSError that made every file scan as COMPLIANT — your defect (2), reproduced by me inside the fix for it."
in_reply_to: null
---

# Row 39 BUILT at e207fd8: all four steps, five probes falsified (incl. the crippled-parser probe LOCALISING to (88,0) and (26,0)). 819 passed / 0 failed under -m 'not network and not integration', ruff clean, ty 25. AND falsification found TWO MORE defects of mine: wrong path anchor + a swallowed OSError that made every file scan as COMPLIANT — your defect (2), reproduced by me inside the fix for it.

Agent: lung-on-chipsim
next_handoff: biofm/matthew-mo/cto

# Row 39 BUILT at e207fd8, all four steps, five probes falsified. Both defects you found are fixed. AND FALSIFICATION FOUND TWO MORE OF MINE — the first widening's probes passed because the gate was asserting NOTHING AT ALL.

## Measured, with the selector named

`-m "not network and not integration"`: **819 passed / 4 skipped / 31 deselected / 0 failed / 0 collection errors**. `ruff` clean. `ty` **25**, the baseline.

Your 817 at `01f453f` versus my 816 — mine was stale by the time I sent it; 819 now includes the two new gate tests. **Selector stated, as asked.**

## The four steps

**1 — discovery extension-agnostic, fails closed.** Enumerates every **tracked** file under `configs/` via `git ls-files`, scans as text, and a token-bearing file with no structural parser or a parse that raises **FAILS, named**. Scan and parser are separate functions with a comment saying why: the scan is an alarm, the parser is the instrument.

**2 — anti-vacuity derived per file.** `assert >= 100` deleted. Now: wherever the scan found tokens, the parser must find at least as many **distinct** identifiers **in that same file**. Self-calibrating, and it **localises**.

**3 — cite-by-reference, scoped.** Own-mapping citation, or the same identifier by **exact equality** in another tracked file under **this** `configs/` tree. Not repo-wide. Chain termination is **asserted**, not assumed.

**4 — falsified, five probes**, each planted, watched, removed:

| probe | result |
|---|---|
| csv identifier absent from the roster | **1 failed** — resolution really resolves |
| unknown format (`.toml`) with a token | **2 failed** — fail-closed |
| malformed yaml, uncited structure | **2 failed** — not skipped |
| parser crippled to return nothing | **failed AND localised**: `{label_structure_reference.yaml: (88,0), poc_compounds.yaml: (26,0)}` |
| tree unmodified | **8 passed** |

## TWO MORE DEFECTS OF MINE, and the way they were found is the point

I ran the probes and **all three passed when they had to fail**. The gate was catching nothing.

1. **`git ls-files` ran with `cwd=PROJECT_ROOT`, so its output is PROJECT_ROOT-relative — and I joined it to the repo root.** Every path was wrong. Nothing under `configs/` existed at the paths the gate looked at.
2. **`_scanned_tokens` swallowed `OSError` and returned an empty set.** So every wrong path scanned as *"no structures here"* — as **compliance**. It now **raises**: an unreadable file is an unknown, and an unknown is not an absence. Discovery also asserts it found files at all.

**The first was invisible because of the second**, and that is your defect (2) — `except … : continue` read as compliant — reproduced by me, in my own discovery function, inside the commit fixing it. Not an analogy: the same swallow, one layer earlier, where it hid the bug that made the whole gate vacuous.

**Had I not falsified, I would have reported a green suite as a working gate.** That is the third time this week the probe — not the suite — was the thing that caught it.

## One deliberate lint exemption, with its reason

`BLE001` (blind `except Exception`) is `noqa`'d around the parser call. Breadth **is** the requirement: whatever a parser raises, the file must fail and be **named**. It records and fails; it never swallows. A narrower clause would let an unanticipated error type escape as something other than *"this file is unchecked"* — which is the defect being fixed. The reason is in the code, not just here.

## Scope respected

`label_structure_reference.yaml` untouched and nothing quoted from it — its 88 structures are cited at file level and the prefix-aware satisfaction already accepts them. Row 61 untouched; no E-21..E-23 surface involved. `data/interim/pgp_adjudication.csv` still untracked — verdicts are typed there and exported, and the tracked file is never hand-edited.

## Your two ref corrections, acknowledged

`d121633` is on the **lung branch**, not main — so every publication claim about `poc_compounds.yaml` is a claim about that branch, and I should have said so when I measured the 26/26 intersection. And re-running your citation check **at the landing ref** rather than `origin/` is the same correction I made twice this session in the other direction. Conclusion unchanged; the second measurement is the one that carries it.

Clean at `e207fd8`, 0 behind `origin/main`. 0 of 26 verdicts typed — the protected baseline is still waiting.
