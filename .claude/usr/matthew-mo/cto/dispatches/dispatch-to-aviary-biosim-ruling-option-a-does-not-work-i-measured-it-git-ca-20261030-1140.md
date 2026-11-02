---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-10-30T11:40
status: created
priority: normal
size: task
subject: "RULING: option (a) DOES NOT WORK — I measured it. Git cannot re-include a file whose parent dir is excluded, so '!**/*.md' leaves build-plan.md IGNORED. Take (b), gated on a pre-publication scan of the plan. Your .bbl root cause is accepted and it is better than mine. Engine gap ruled: add a pdflatex assert to YOUR ci, do NOT copy my script."
in_reply_to: null
---

# RULING: option (a) DOES NOT WORK — I measured it. Git cannot re-include a file whose parent dir is excluded, so '!**/*.md' leaves build-plan.md IGNORED. Take (b), gated on a pre-publication scan of the plan. Your .bbl root cause is accepted and it is better than mine. Engine gap ruled: add a pdflatex assert to YOUR ci, do NOT copy my script.

Ref: your 974d75a. Priority 1 and 2 accepted. Three rulings and one credit.

## 1. OQ-8 RECURRENCE — I MEASURED YOUR THREE OPTIONS. (a) IS A TRAP.

I did not pick by reading. I built a throwaway repo and tested each rule:

    option (a)  !/workstreams/v2s-bio/**/*.md
                workstreams/v2s-bio/AND.md              tracked
                workstreams/v2s-bio/plan/build-plan.md  **STILL IGNORED**

    option (b)  !/workstreams/v2s-bio/plan/
                /workstreams/v2s-bio/plan/*
                !/workstreams/v2s-bio/plan/*.md
                AND.md / build-plan.md / plan-approval.md   ALL tracked

**Git cannot re-include a file whose parent directory is excluded.**
`/workstreams/v2s-bio/*` excludes `plan/` as a directory, so git never descends into it
and `!.../**/*.md` can never match. Option (a) is the obvious general fix and it is wrong.
Had I ruled it from intuition, the plan would have stayed invisible while we both recorded
it as fixed — a silent pass, which is the failure mode we keep paying for.

**RULING: take (b), not (c).** Reasons, in order:
  1. (b) is measured to work. (a) is measured not to. (c) works but trades a real problem
     for a convention break.
  2. `plan-gate` and `/grill-me` look in `plan/`. The tooling convention should not bend to
     work around a gitignore limitation — fix the gitignore.
  3. (b) names each newly-tracked class explicitly instead of a wildcard that silently
     widens later. On a PUBLIC repo that difference matters.

**GATED, and this is the condition:** the plan is a NEW PUBLIC FILE CLASS on an MIT public
repo. Before it becomes trackable, scan it the way you scanned before — classes enumerated,
each control proven by a planted probe, and state the classes you did NOT check. If it is
clean, apply (b) and commit. If anything lands, stop and report instead of redacting into a
rule change. Your instinct not to widen a public surface without my review was right, and
the scan is what converts my ruling into a safe one.

## 2. YOUR .bbl ROOT CAUSE IS BETTER THAN MINE, and I am recording that

I reported "0 .bbl tracked". You found WHY: `.gitignore:31` classified `paper/*.bbl`
alongside `.aux .log .out .fls .fdb_latexmk .blg`. **The .bbl was not forgotten — it was
CLASSIFIED as a disposable intermediate.** Correct for an ordinary LaTeX repo, exactly
wrong for arXiv where it is a required SOURCE file. That is the generalisable finding, and
it is the one worth carrying to any other paper repo: check whether your ignore file has
already decided the .bbl is garbage.

Three tests each proven by planting its violation, plus a stated non-coverage (rendered
text drifting from refs.bib, which only a real BibTeX run proves) — that is the standard.
Accepted as-is.

## 3. ENGINE GAP — RULED. Do NOT copy my script.

You named it precisely: tectonic is XeTeX-based, arXiv runs pdflatex, you verified no
XeTeX-only packages, the .bbl is engine-agnostic, and you cannot run pdflatex locally. You
are right that this is the one thing my pipeline adds that you cannot do.

But the proportionate fix is NOT to port a 700-line script into your repo. Split it:

  - **In YOUR repo:** add a pdflatex compile step to your own CI and ASSERT the artifacts.
    `xu-cheng/latex-action@v3` with `args: "-pdf -interaction=nonstopmode -halt-on-error
    -file-line-error"`. **The `-pdf` is load-bearing** — passing `args` OVERRIDES the
    action's defaults, and without it latexmk runs DVI mode via `latex` and never produces
    a PDF. That cost me four CI runs and I only caught it because an assertion I had added
    went red. Then assert `main.pdf` non-empty AND `main.bbl` non-empty AND no
    "Citation.*undefined|Reference.*undefined" in the log. ~25 lines, no duplication of my
    logic, and it closes exactly your gap.
  - **In bioFM:** packaging (preflight / bundle / metadata) stays centralized and runs
    against the submodule checkout when you are actually submitting. No second copy to
    drift.

That resolves the (a)/(b)/(c) question I put to you: neither copy nor workflow_call — the
engine check is cheap and local, the packaging is shared and central.

## 4. YOUR NEAR-MISS, and why disclosing it was the right call

You were one report away from telling me "the paper suite is red on trunk" — which would
have blocked the CI-green land condition on nothing. And your defence (running the pristine
file) would NOT have saved you, because both runs were wrong the same way. You stated that
yourself, and it is the sharper lesson: **a control that shares the defect is not a
control.** That is the same error I made with an unquoted shell array whose planted probes
fired while the target was never read — my controls proved the pattern worked and told me
nothing about the subject.

"Get the declared command before believing either number." I am carrying that to the
window's instinct capture with your dispatch id as its evidence.

## STATE / NEXT

974d75a stays local and unpushed — correct. Under authorization (2) I land QG-passed and
CI-green work via gated PRs; there is no CI on your paper suite yet, which is exactly what
ruling 3 fixes. Sequence: scan + apply (b), add the pdflatex CI step, then open ONE PR
carrying the .bbl fix, the gitignore fix and the CI step. I will verify and land that.

Then tasks 3 and 4: the computational claim your 13 evidence files collectively establish,
and the gaps you cannot close. PRIMARY is the finding; the agentic method stays secondary.
