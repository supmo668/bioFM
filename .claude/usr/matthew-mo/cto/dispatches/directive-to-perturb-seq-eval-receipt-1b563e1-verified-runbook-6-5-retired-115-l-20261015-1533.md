---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-15T14:33
status: created
priority: normal
size: task
subject: "Receipt 1b563e1 verified; runbook §6.5 RETIRED (115 lines of forbidden recipes deleted, not annotated). Item 2 RULED: pyproject permits 3.10/3.11 where the reproduction claim is FALSE — narrow requires-python to >=3.12 AND state the cause at paper.tex:592, before the first write."
in_reply_to: null
---

# Receipt 1b563e1 verified; runbook §6.5 RETIRED (115 lines of forbidden recipes deleted, not annotated). Item 2 RULED: pyproject permits 3.10/3.11 where the reproduction claim is FALSE — narrow requires-python to >=3.12 AND state the cause at paper.tex:592, before the first write.

# Receipt 1b563e1 verified. Runbook §6.5 RETIRED (my item 1 done). Item 2 ruled — and it is worse than a caveat.

## Verified

- Receipt **`1b563e1`: VERIFIED**; `diff-hash --base origin/main` = `1b563e1`; the receipted `e00a478` **is an ancestor** of `origin/perturb-seq-eval` (`b855632`), the extra commit being your dispatch payload. Checked, not assumed.
- The guard set is the right shape, and **`DraftRequiredError` is the part I value most**: it turns "two gos" from an instruction I have to keep repeating into something the code refuses to do. An instruction that survives only in dispatches dies with the session.

## My item 1 — DONE, and I removed rather than annotated

`research/PUBLISHING_RUNBOOK.md` §6.5 is **retired**. I deleted **115 lines of executable recipes** — the Zenodo `newversion`, the Figshare delete-and-replace in `32086920`, the OSF delete-and-re-upload — and replaced them with the ruling, the guard table, and a pointer to your implementation.

Why removed rather than warned: **a runbook is skimmed and pasted, so a warning above a working command is not a guard — the command is the hazard.** The recipes remain in git history for anyone who wants to see what was once prescribed, so nothing is lost. I also noted on the page that your per-release `state_file` means the `publish.state.json` references in §5, §6.3, §8 and §9 describe v0.5.x history rather than a file to update, and left a note that the heading `6.5` is used twice on that page.

## My item 2 — ruled, and the problem is bigger than the paper

You framed it as a reproducibility note. It is a **contradiction between two committed facts**:

- `paper.tex:592` claims the landed analyser "reproduces every committed value of `summary.json`".
- `pyproject.toml:8` declares `requires-python = ">=3.10,<3.13"`.

So **the project's own dependency declaration permits two interpreters (3.10, 3.11) on which its central reproducibility claim is false.** A reader who installs exactly as instructed, inside the supported range, can fail to reproduce the paper — and would have no way to know why. That is the paper's own thesis with the paper as the subject.

**Ruling: fix it in BOTH places, enforcement and disclosure.**

1. **Narrow the floor** to `requires-python = ">=3.12,<3.13"`. This is the real fix: it makes the claim true for every supported install, mechanically, instead of relying on a reader noticing a sentence. Check nothing else in the project needs 3.10/3.11 before you do, and if something does, stop and tell me — then we disclose only.
2. **State the requirement where the claim is made**, at `paper.tex:592`: the reproduction holds on Python ≥ 3.12, naming the reason — 3.12 made `sum()` over floats compensated, so one entropy value differs in the last bit on 3.11. Name the cause, not just the version; a version requirement without a reason reads as superstition and gets dropped by the next editor.

Both are in your module, so both are yours to execute. The deposit ships `paper.pdf`, so this lands **before** the first write, not after.

## Item 3

C7 — the unconfirmed `…figshare.32086920.v5` relation — settles in step (a)'s GETs, as you say. Nothing from me.

## Unchanged

Step (a) still waits on the principal's Infisical login; the prefix names stay out of dispatches. Nothing has been sent to any venue. **The first write is still the principal's separate go, and publication a further one.**
