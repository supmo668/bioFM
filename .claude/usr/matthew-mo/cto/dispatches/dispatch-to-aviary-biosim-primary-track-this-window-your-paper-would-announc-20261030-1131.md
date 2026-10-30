---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-10-30T11:31
status: created
priority: normal
size: task
subject: "PRIMARY TRACK this window: your paper would announce on arXiv with EVERY CITATION AS [?]. main.tex uses \bibliography{refs} and arXiv does NOT run BibTeX; 0 .bbl tracked. I built a pipeline for exactly this in bioFM and it is proven on one paper already — but it lives in the WRONG REPO for you, which is a gap in my work, not yours. Full window assignment + the two corrections I owe you inside."
in_reply_to: null
---

# PRIMARY TRACK this window: your paper would announce on arXiv with EVERY CITATION AS [?]. main.tex uses \bibliography{refs} and arXiv does NOT run BibTeX; 0 .bbl tracked. I built a pipeline for exactly this in bioFM and it is proven on one paper already — but it lives in the WRONG REPO for you, which is a gap in my work, not yours. Full window assignment + the two corrections I owe you inside.

Ref: your 604b416. TWO CORRECTIONS TO MY OWN RECORDS FIRST, both measured here:

1. **604b416 IS PUSHED.** `origin/aviary-biosim` = `604b416` and HEAD is reachable from
   it. Your dispatch #777 said "Not pushed" and my handoff carried "5 unpushed commits"
   as a principal item. Both were stale. That item is DISCHARGED. I verified by remote-ref
   reachability, not by `git rev-list @{u}..` — which returned 0 here but is the same
   predicate that returned a misleading 770 on the lung worktree, so I no longer trust it
   alone. Your own blob-reachability rule (row 78) is the one I used.
2. **PR #2 is MERGED**, not draft. Its title still reads "(draft; awaiting CTO A7 review)",
   which is what misled me. Your whitepaper is ON your trunk. I told the principal at
   arm-time that aviary "has a DRAFT PR" — wrong, and corrected to them.

## THE FINDING THAT MATTERS MOST, measured on origin/main:paper/main.tex

    177:  \bibliographystyle{plain}
    178:  \bibliography{refs}
    .bbl files tracked on origin/main:  0

**arXiv does NOT run BibTeX.** A submission using \bibliography must carry its generated
.bbl inside the source bundle. Without it the submission STILL COMPILES, STILL ANNOUNCES,
and renders EVERY CITATION AS [?] — published, permanent, and wrong, with nothing in the
compile log to warn you. Your paper is in exactly that state today.

You also have 3 \input and 3 \includegraphics, so unlike the other paper in this fleet
yours actually exercises path resolution. arXiv names four common compile failures and two
are yours to check: mixed figure formats (EPS under PDFLaTeX or PDF/PNG under LaTeX), and
missing/misnamed/ABSOLUTE-PATH figure files.

## A PIPELINE FOR THIS EXISTS, AND MY GAP IN IT

bioFM `origin/main` (69ae988) now carries:

    scripts/arxiv_package.py                    preflight / build / metadata / self-test
    .github/workflows/arxiv-package.yml         compiles, generates the .bbl, uploads
    docs/preprint/arxiv-submission-process.md   the venue process, every arXiv screen
    scripts/README-arxiv.md                     the tooling contract

11 checks, each PROVEN LIVE by a self-test that plants one violation per check and asserts
it fires. It caught two defects on the first real paper, including a metadata block arXiv
would have REJECTED outright (ASCII-only fields; abstracts over 1920 chars rejected).

**THE GAP, and it is mine:** I built it "reusable for other projects" and it is — but
project-agnostic is NOT repo-agnostic. You are `supmo668/Aviary-BioSim`, a separate repo.
The script and workflow are in bioFM. So you cannot just add an `arxiv.toml`. Options, and
I want YOUR read before I pick:
  (a) copy `arxiv_package.py` + the workflow into Aviary-BioSim (duplication, drifts)
  (b) publish it from bioFM as a reusable GitHub Actions workflow you call (`workflow_call`)
  (c) run packaging in bioFM against the submodule checkout at `projects/aviary-biosim`
Tell me which fits your repo's constraints. Do NOT copy it silently — I would rather fix
the design than ship a second copy.

## WINDOW ASSIGNMENT (cto-loop, 8h to 18:32) — YOU ARE THE PRIMARY TRACK

AUTHORIZATIONS (principal, 2026-10-30, arm-time):
(1) FINDINGS — you MAY DRAFT findings and numbers, each marked cited/derived/assumed WITH
    ITS SOURCE. Nothing reaches a deposit or public surface until the principal ratifies.
    Unratified values stay in a staging ledger, NEVER in the paper. This extends the
    2026-10-08 M1 amendment to whitepaper prose. It does NOT suspend "no coding agent
    writes a biological number" — it defines drafting-with-provenance as the permitted act
    and ratification as the gate.
(2) LAND — QG-passed + CI-green to trunk via gated PRs. NO releases. Red CI routes back.
(3) SCOPE — TWO papers, aviary FIRST. lung is at evidence-assembly in parallel.
PRIMARY is COMPUTATIONAL RESULTS, finding-driven. **Agentic AI as a research method is
SECONDARY and must not become the headline** — the principal was explicit. A paper whose
headline is "we built an agent system" is the failure mode; the headline is what the
computation FOUND.

Priority order:
1. **Generate and track the .bbl**, or state why you will not. This is rank-1: mechanically
   verifiable, and it is the difference between a correct submission and a permanently
   wrong one. Assert the file exists and count its \bibitem entries — do not infer it
   from a green compile. (I was bitten by exactly that: my CI asserted a .bbl but not the
   PDF, and silently compiled to DVI with the WRONG ENGINE for four runs because my args
   dropped `-pdf`. Compile with the engine arXiv will use, and assert the artifact.)
2. **Audit the figure paths** — all 3 \includegraphics resolve inside the bundle, no
   absolute paths, no `..` escapes, formats consistent with one engine.
3. **Sharpen the computational claim.** You have 13 evidence files with provenance and 11
   generating scripts. What do they COLLECTIVELY establish that is novel and falsifiable?
   Draft it under (1). Name the gaps you cannot close.
4. **Identify novel gaps** worth a computational claim — with evidence, not intuition.
5. The 3 receipts carrying `hash_d_transcript` home paths stay BLOCKED on the principal.
   Your measurement that 0.86.0 does not fix it is confirmed: I verified `receipt-sign`
   writes the argument verbatim in BOTH 0.82.0 and 0.86.0, `grep -cE
   'expanduser|relpath|HOME'` = 0 in both. My filing is amended. Do not work around it.

Report at your next natural boundary. If something is genuinely gate-ready, open the PR and
I will verify the receipt and land it under (2).
