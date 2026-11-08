---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-11-04T20:28
status: created
priority: high
size: task
subject: "RULED: title T1, contribution narrowed, 'gate' rename approved as a disclosed amendment — redesign is a NEW pre-registration, not an edit to this one"
in_reply_to: null
---

# RULED: title T1, contribution narrowed, 'gate' rename approved as a disclosed amendment — redesign is a NEW pre-registration, not an edit to this one

Two of the five #876 rulings are now taken, plus a third instruction that needs a boundary respected. Recorded as perturb-seq-eval approvals **rows 13 and 14**; read both before you touch the paper.

## Ruled — act on these

**Title: T1.** Question form kept, answer added. It is the only one of the three that is a **no-op on the locked rule** at `PREREGISTRATION.md:27-28` — T2 and T3 both engage it, T3 most. Still a disclosed amendment on the file (`:3-4` names the title, the hash diverges), so write it as one. Apply it.

**Contribution: narrowed to the multi-agent case**, as you recommended. The prior art assumes a fixed base agent over one model at one step, so it is prior art for the signal and not for a multi-agent group's distribution. State the novelty as the group distribution. This changes **no** hypothesis, threshold, metric or outcome — H5 still fails at ρ = 0.286 against > 0.4. Concentrate it in related-work and the contribution statement; the abstract's first sentence already carries the framing.

## Ruled with a condition — the "gate" rename

Approved, **but it is not editorial.** `H1`–`H5` and "gate outcomes: 4 of 5 pass" are pre-registered labels, so changing the word is a disclosed post-lock amendment exactly as the title is. Therefore:

- record it as an amendment, keeping the old term in the record so a reader can map old → new;
- every number, hypothesis identity and outcome survives unchanged — **a rename that changed which hypotheses passed would be a result change wearing a vocabulary change**;
- you propose the substitute term (e.g. "pre-registered criterion" / "pre-specified threshold"), one term, used consistently;
- apply it in **one pass** across `paper/`, `PREREGISTRATION.md`, `arxiv.toml`, the abstract and the `SUBMISSION.md` paste block, so the published artefacts cannot disagree with each other.

## The redesign — read this before planning anything

The instruction is *"Re-design experiment to drive towards a potential positive result."* **It is authorised as a new, separately pre-registered follow-up study. It is NOT authorised as an amendment to this one.**

H5's failure has already been observed. Amending a pre-registration after seeing its outcome so that the outcome passes is HARKing, and it would convert a reported negative result into a claim the data do not support — on a public repo, in a paper whose entire stated contribution is being pre-registered and provenance-complete. So:

- the v0.6.0 negative result **stands as reported**; H5 stays failed; the "0 unevaluated" integrity claim stays; the exploratory note that the confidence-entropy point estimates ran against the pre-registered direction stays;
- the follow-up gets **its own** pre-registration, with hypotheses and thresholds fixed **before** any run, and may state plainly that H5's failure motivated it — that is a legitimate and publishable motivation;
- do not re-gate, re-frame or re-open the v0.6.0 result as part of this.

If you think I have read the instruction too narrowly, escalate rather than proceed — do not resolve it yourself in either direction.

## Still parked with the principal

Three of the five #876 rulings are not taken: the **A5 form** (`v0.6.0-a5` tag or untagged), **FINDING 1.1-e** (name CATTS in the abstract — ratify or strike), and the **1916-char override re-ratification**. Also still open: **F1**, the venue contradiction in `SUBMISSION.md` you escalated. Do not guess any of them.

**F2 go-ahead stands** from #892 — the `c0ec931` "held unflushed" and "the LaTeX step has never executed" wording is measurably false and you may correct it.

## Sequence

`/iteration-start` (origin/main is `600e510`, v0.6.0) → apply T1 + the narrowing + the rename + F2 → `/quality-gate` → `/iteration-complete` → `/pr-prep` → `/pr-submit`. Bib entries from the arXiv pages, paste block regenerated.

**Note the receipt trap you yourself found:** your `/pr-submit` will move Hash E again via its own dispatch commit. Sign the `--derived-from` receipt as you did last time and say so in the submit body — I now expect it and verify `git diff --stat` across the gap rather than treating it as a mismatch.
