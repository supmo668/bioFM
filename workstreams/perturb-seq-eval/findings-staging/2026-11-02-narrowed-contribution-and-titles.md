---
type: findings-staging
status: DRAFTED — UNRATIFIED. NOT FOR paper/, CITATION.cff, the bib, Zenodo, Figshare, arXiv or any HACP surface.
authorization: principal rulings 2026-10-31 (perturb-seq-eval approvals row 11, "approve to narrow the
  contribution to multi-agent case") and 2026-11-01 (row 12, "Retitle + cs.LG + cs.MA (Recommended)"),
  relayed via CTO #842 and #848. Authorization (1) (CTO #812): agents may DRAFT, each item marked with its
  provenance class; nothing reaches a deposit or public surface until the principal ratifies.
agent: biofm/matthew-mo/perturb-seq-eval
paper_revision: projects/perturb-seq-eval/paper/paper.tex at ffccc92 (identical to 69ae988 — verified by
  `git diff --quiet 69ae988 HEAD -- paper/paper.tex`); every line number below is at that revision.
companions: 2026-10-30-paper-framing-drafts.md (R2-a..e, (b″), (b″-D), (b′)), 2026-10-31-catts-full-text-read.md
  — both moved into this directory from qa/_adhoc on the working branch, unchanged.
---

# Narrowed contribution, sweep of `paper/`, (b″)/(b″-D) check, and three title candidates — DRAFTED, 2026-11-02

> **Ratification status, labelled in place 2026-11-07 (approvals row 26).** Each item below carries a `Status (2026-11-07)` line. Vocabulary: **RATIFIED + APPLIED** (a row rules it and it is on `origin/main`), **RATIFIED, HELD** (ruled, deliberately not applied), **APPLIED UNDER A DIRECTION RULING** (on `origin/main` under a row that rules the direction, not this wording), **NOT ADOPTED**, **SUPERSEDED**, **UNRATIFIED** (no row in perturb-seq-eval approvals 1–26 rules on it), **REPORT / RECORD** (evidence; nothing to ratify). Rows are cited from `workstreams/perturb-seq-eval/approvals.md`; rows 20–26 were committed on the CTO's local `main` and were not on `origin/main` at labelling time, so they are cited by content as well as number. `origin/main` = `7c293c0a` (PR #42 merge). Nothing in this file is ratified by being labelled.

**What this file is.** The four items CTO #842 asked for under row 11, plus the three title candidates
row 12 asks for (#848 item 1). The principal ratifies or strikes each numbered item; nothing here edits
`paper/`. The cs.MA cross-list (#848 item 2) is a config edit and does **not** live here — it goes through
`/iteration-start → /quality-gate → /iteration-complete → /pr-prep → /pr-submit` on the working branch
(§6 records what that PR touches, so this ledger and the PR cannot disagree).

| marker | means here |
|---|---|
| **cited** | a verbatim quote with its file:line, or a fact of the CATTS source that the CTO has verified at the ref (#814, #817) |
| **derived** | my inference from cited material; the inference is named as such |
| **drafted** | proposed paper text for the principal to ratify, strike or rewrite |

**Rules applied, unchanged from #809/#812/#814/#817.** No number is typed by hand (macros only). No
differs-from claim about any work is made from an abstract. Nothing from the "me only" rows of the CATTS
verification table (no pre-registration in CATTS; the Fisher test; the binned analysis; the Table 3
figures) carries a sentence anywhere below. The citation key is `lee2026catts` (Nicholas Lee, 2026,
cs.AI) — never "the Lee paper"; "Lee 2022" is a failure name in this project. No claim that CATTS fails,
underperforms, or regards multi-agent methods as anything.

**What the ruling fixes (row 11, cited).** Ours: *a multi-agent group's confidence/critique distribution
as an explicit item-difficulty signal.* Not ours: *that an internal confidence/vote distribution can
steer test-time compute at all* — CATTS does it. Differentiation rests only on CATTS's stated scope
("we assume a fixed base agent", their §2) and its single-model, per-step vote distribution (their §3.1).

---

## 1 · The narrowed contribution statement — **drafted**

### 1.1 Abstract (replaces `paper.tex:56–59`, the first two sentences)

> **Status (2026-11-07):** **RATIFIED + APPLIED, in part by name.** The direction is rows 11 and 13. Finding 1.1-e is ratified by name (row 17), and the override wording by rows 18 and 23. It is on `origin/main` at `paper.tex:56–60` (`9eab7f25`, PR #42). No row ratifies the other 1.1 sentences by name.

Current (cited, `paper.tex:56–59`):

> Multi-agent group-generation systems spend test-time compute uniformly across tasks. We ask whether
> the agents' own confidence-and-critique trace predicts how hard a task is, which would let the compute
> be allocated adaptively.

Drafted replacement:

```latex
A multi-agent group-generation system, as operated here, spends test-time
compute uniformly across tasks. That a single agent's own vote distribution
can gate its test-time compute is already reported~\citep{lee2026catts}; we
ask the multi-agent question: whether the distribution of stated confidences
and critiques across a group of role-specialised agents predicts how hard a
task is, which would let the group's compute be allocated adaptively.
```

What changed and why, each a separate ratification point:

- **1.1-a** "Multi-agent … systems spend … uniformly" (a universal claim about every such system) becomes
  "as operated here" — a claim about our runs only, which the design supports ("three fixed-length agentic
  lifecycle runs per task", `paper.tex:72–73`, cited). The universal form was never evidenced and is not
  needed by the narrowed claim.
- **1.1-b** The single-agent case is stated as already reported and cited. Only abstract-level, CTO-verified
  facts are used: "vote distribution" and "compute allocation" are the CATTS abstract's own words (#809,
  #812). No characterisation beyond that.
- **1.1-c** "the agents' own confidence-and-critique trace" becomes "the distribution of stated confidences
  and critiques across a group of role-specialised agents" — the narrowed object, matching
  `results.tex:128–133` (cited: "with $C(r)$ the confidences of the LLM-sourced steps in round $r$";
  "five-role lifecycle").
- **1.1-d (consequence, not a choice).** `CITATION.cff:10–` is GENERATED from this abstract by
  `scripts/paper/render_publish_description.py` (cited, `CITATION.cff:9`) and would regenerate. The
  arXiv override abstract at `arxiv.toml:52` is author-ratified (2026-10-30), 1906 of 1920 allowed ASCII
  characters (cited, `arxiv.toml:40–49`); the drafted sentence is longer than the one it replaces, so the
  override would have to be re-derived and re-ratified. Both are downstream of this item, not part of it.

### 1.2 Introduction contribution bullet

> **Status (2026-11-07):** **APPLIED UNDER A DIRECTION RULING** (row 13). It is on `origin/main` at `paper.tex:126–136` (`f2bb1933`, PR #42).

Given in both orders, because R2 (the reorder) is itself unratified.

**If R2 is struck — replaces current item 1, `paper.tex:122–124`:**

```latex
  \item We test whether a \emph{multi-agent group's} confidence/critique
        distribution is an explicit item-difficulty signal. We formalise four
        easy-to-compute observables of such a run --- ACE, CSD,
        $\Delta C$/$\Delta$ACE, and WFR --- over the stated confidences and
        critiques of $N$ role-specialised agents, within and across rounds,
        and combine them into a scalar Task Difficulty Index (TDI). That an
        agent's own vote distribution can gate test-time compute is reported
        by \textsc{CATTS}~\citep{lee2026catts}, whose statistics are computed
        over $N$ candidate actions sampled from one base model at a single
        step (their \S3.1) under the stated assumption of ``a fixed base
        agent'' (their \S2); we claim nothing about that case.
```

**If R2 is ratified — replaces the first two sentences of R2's item 3** (the metrics item; its outcome
sentence "Of these, the lifecycle traces supply two: …" is unchanged and follows directly):

```latex
  \item We test whether a \emph{multi-agent group's} confidence/critique
        distribution is an explicit item-difficulty signal, formalising four
        easy-to-compute observables of such a run --- ACE, CSD,
        $\Delta C$/$\Delta$ACE, and WFR --- over the stated confidences and
        critiques of $N$ role-specialised agents, within and across rounds,
        and combining them into a scalar Task Difficulty Index (TDI). That an
        agent's own vote distribution can gate test-time compute is reported
        by \textsc{CATTS}~\citep{lee2026catts}, whose statistics are computed
        over $N$ candidate actions sampled from one base model at a single
        step (their \S3.1) under the stated assumption of ``a fixed base
        agent'' (their \S2); we claim nothing about that case.
```

Provenance of every CATTS fact in the bullet: §2 "we assume a fixed base agent" and §3.1 "$N$ candidate
actions from the base model" at one time step — both **cited**, CTO-verified at the ref (#814 §1, table
rows 3–4 of the CATTS note). "within and across rounds" — kept per #817 §2 (ACE on the final round; $\Delta C$
first→last). The bullet says nothing CATTS's authors think, nothing about CATTS's results.

**Reader's one-line version** (for the CTO's Notion row; not paper text): *We claim the multi-agent group's
confidence/critique distribution as a difficulty signal. We do not claim that confidence can steer
test-time compute — a single agent's vote distribution already does that in CATTS.*

---

## 2 · Sweep of `paper/` — every sentence claiming the general case or implying priority

> **Status (2026-11-07):** **APPLIED UNDER A DIRECTION RULING** (row 13), in `f2bb1933` (PR #42). Its commit message is "contribution narrowed to the multi-agent group". The S1–S19 rows were **not** re-verified one by one in this labelling pass.

Method: read in full `paper.tex` §Abstract, §1, §2, §3, §7 (Discussion), §9 (Conclusion) and the
contribution-audit table; grep over `paper.tex`, `sections/*.tex`, `paper/README.md`, `SUBMISSION.md`
and the module `README.md` for `first|novel|to our knowledge|no prior|unlike|introduce|propose|analogue|
allocat|steer|govern`. Listed in file order. **Nothing is edited.** "Keep" rows are listed so the
principal can see what was checked, not only what changed.

| # | Where (cited) | Sentence today | Verdict | Drafted replacement |
|---|---|---|---|---|
| S1 | `paper.tex:56–57` | "Multi-agent group-generation systems spend test-time compute uniformly across tasks." | **Replace** — universal claim about the field, unevidenced | §1.1 |
| S2 | `paper.tex:57–59` | "We ask whether the agents' own confidence-and-critique trace predicts how hard a task is…" | **Replace** — does not name the group; reads as the general case | §1.1 |
| S3 | `paper.tex:109–112` | "Every such system today spends compute \emph{uniformly}: the same number of agents for the same number of rounds regardless of whether the task is…" | **Replace** — "every such system today" is a universal absence claim | "As operated here, such a system spends compute \emph{uniformly}: the same number of agents for the same number of rounds regardless of whether the task is…" (rest unchanged) |
| S4 | `paper.tex:113–115` | "\emph{This paper asks whether the group's own internal dynamics carry enough signal to allocate its compute adaptively}, and tests that question under a pre-registered design…" | **Keep** — already the multi-agent question | — |
| S5 | `paper.tex:117–119` | "…all within the empirical frame of Perturb-seq response prediction… but generalising to any propose-critique-vote system" | **Keep** — a scope claim about multi-agent systems, not a priority claim | — |
| S6 | `paper.tex:122–124` | contribution item 1, "We formalise four easy-to-compute observables of a multi-agent run…" | **Replace** — carries the narrowing and the CATTS sentence | §1.2 |
| S7 | `paper.tex:125–128` | contribution item 2, "We introduce a \emph{preflight probe}…" | **Keep under R2-c** ("proposed here and not validated"); the probe is a single-round *group* probe, inside the narrowed scope | — (R2) |
| S8 | `paper.tex:160–162` | "\citet{snell2024scaling} is the primary reference for the difficulty-conditional compute-optimal idea that our work extends to the group setting." | **Keep** — "the group setting" is the narrowed claim; the single-agent extension (CATTS) is placed two paragraphs later by (b″)/(b″-D) rather than here, so the related-work paragraph on multi-agent TTC carries it once | — |
| S9 | `paper.tex:169–171` | "None of these works, to our knowledge, use the group's internal confidence/critique distribution as an explicit difficulty signal." | **Replace** — the refuted-at-corpus-level novelty sentence | (b″) + (b″-D), companion file; see §3 |
| S10 | `paper.tex:202–205` | "\emph{Agentic hyperparameter tuning} is the problem of… the multi-agent analogue of \citet{snell2024scaling}'s compute-optimal single-chain allocation." | **Keep** — defines a problem in the multi-agent setting; no priority claim | — |
| S11 | `paper.tex:326–327` | "We separate our work into three buckets --- novel contribution, thin adapter over existing infrastructure, and explicitly-scoped future work" | **Keep, flag** — "novel" here means *authored in this repository* versus adapted; the bucket is a code audit, not a field-priority claim. Optional tightening: "our own contribution" for "novel contribution" | optional |
| S12 | `paper.tex:358–359` (Table `tab:contrib`) | "Novel abstraction + metrics"; "Novel procedures" | **Replace (low-stakes)** — in a table column headed "Kind", "Novel … metrics" can be read as a claim that the metrics are new to the field, which the narrowing withdraws for the single-agent case | "Abstraction + metrics authored here"; "Procedures authored here" |
| S13 | `paper.tex:438–443` | "The title asks whether agent confidence entropy predicts task difficulty rather than asserting that it does…" | **Title-dependent** — rewrite only after the principal picks a title (§4); if a question-form title (T1) is picked the paragraph survives with the quantity renamed | after §4 |
| S14 | `paper.tex:458–459` | "The title question is answered as posed: on this evidence, confidence entropy does not predict difficulty in the pre-registered direction." | **Title-dependent** — survives T1; under T2/T3 "The title question" has no referent | after §4 |
| S15 | `paper.tex:638–642` | "We have proposed ACE, CSD, … as a four-feature lens on multi-agent group-generation traces, … and positioned the TDI and its probe as the multi-agent analogue of \citet{snell2024scaling}…" | **Keep** — "proposed" and "multi-agent analogue" are inside the narrowed scope | — |
| S16 | `arxiv.toml:58–59` (comment) | "cs.LG primary: the contribution is a method claim about hyperparameter allocation under a confidence-entropy statistic." | **Replace in the config PR** — names the general case and the quantity that failed its gate; also needs the cs.MA line | §6 |
| S17 | `arxiv.toml:52` (override abstract) | same two opening sentences as S1/S2 | **Downstream of §1.1** — re-derive and re-ratify under the 1920-character cap | after §1.1 |
| S18 | `CITATION.cff:10–` (generated abstract) | same | **Downstream of §1.1** — regenerates | after §1.1 |
| S19 | `SUBMISSION.md:288–290` | "arXiv `cs.LG` + `q-bio.QM` is the recommendation (better fit for a method claim about compute allocation…" | **Replace in the config PR** — runbook restates the old cross-list and the general-case framing | §6 |

Checked and clean (no general-case or priority claim found): `sections/results.tex`,
`sections/experimental_setup.tex`, `sections/corrections.tex` (the only hits are "first published" at
`corrections.tex:99` and "first round" at `results.tex:132`, both temporal), `paper/README.md`, module
`README.md` (title strings only — §5).

---

## 3 · (b″) and (b″-D) against the narrowed claim

> **Status (2026-11-07):** **RECORD.** The two sentences' own status is in `2026-10-30-paper-framing-drafts.md` Item 3.

**(b″-D) — consistent; KEEP. It is now load-bearing, not optional.** Row 11 says the differentiation
"rests ONLY on CATTS's stated scope ('we assume a fixed base agent') and its single-model, per-step vote
distribution" — which is exactly, and only, what (b″-D) says (companion file, Item 3). Under the
narrowing (b″-D) is the sentence that *states* the narrowed claim's boundary in related work, so it should
be ratified with the narrowing rather than left as an optional companion. Provenance unchanged: **derived**
from two CTO-verified CATTS facts and `results.tex:128–133`.

**(b″) — consistent as written; one adjacency FLAGGED.** (b″) makes no relation claim ("we make no claim
here about how our signal relates to theirs"), so it cannot contradict the narrowing. But it cites
`morandi2026sprt` (arXiv:2605.19193) as gating compute on a signal "from a group of agents". The
narrowed claim is *a multi-agent group's confidence/critique distribution as a difficulty signal*; a
reader will ask how the Wald-SPRT governor's group-level signal differs from ours. What we hold on that
work is its abstract only (companion file, ledger row 3: "an LLM judge emits a [0,1] consensus score on
the latest agent positions"). Under #809 ruling 2 that abstract cannot carry a differs-from sentence —
so **(b″) + §1 together leave one unresolved adjacency, and the paper would say so by silence.**

Three ways to close it; the choice is the principal's/CTO's:

- **3-i** Full-text read of arXiv:2605.19193 (reading a primary source is not principal-gated, #812 §2),
  report-only in the CATTS-note format, then — if the CTO verifies the relevant facts at the ref — a
  second differentiation sentence of the (b″-D) kind. *Not done; not started.*
- **3-ii** Keep (b″) and accept the silence, with the "we make no claim about how our signal relates" clause
  doing the honest work.
- **3-iii** Use (b′) (the minimal variant) instead of (b″) — it names the same two works, so it does not
  remove the adjacency; listed for completeness only.

**(b′) — consistent** for the same reason as (b″).

---

## 4 · Title

### 4.1 Does the current title over-claim under the narrowing? — **Yes, in scope; not in result.**

Current (cited, `paper.tex:34–36`; identical in `CITATION.cff:5–8`):

> Does Agent Confidence Entropy Predict Task Difficulty? A Pre-registered, Provenance-Complete Test of
> Agentic Hyperparameter Tuning for Perturb-seq Response Prediction

- **Scope:** "Agent Confidence Entropy", singular, does not name the group. Under row 11 the claimed object
  is *a multi-agent group's* distribution; a single agent's confidence distribution is the case the ruling
  gives up, and it is the case CATTS occupies. The headline therefore asks the general question the paper
  no longer claims.
- **Result:** question form asserts nothing, so it does not over-claim a result. But the named quantity,
  confidence entropy, is the one whose gate failed in both screens (cited: "both tests fail the one-sided
  gate", `results.tex:184`; point estimates "against the pre-registered positive direction",
  `results.tex:181–183`), and the quantity that passed ($1-\Delta C$, `results.tex:184–185`) is not named.
  Row 12's basis ("a title must not imply a yes") is met by the question form; the title just withholds
  the answer. (Unchanged from the companion file, Item 1.)

### 4.2 A constraint on every candidate — **flag for the principal**

> **Status (2026-11-07):** **RESOLVED** by row 14: T1 does not engage the `PREREGISTRATION.md:27–28` lock.

`paper/PREREGISTRATION.md:25–29` (cited, verbatim):

> ## Why the title is a question
> The title asks whether agent confidence entropy predicts task difficulty, and does not assert that it
> does, so that a null answer is publishable as it stands. **A null or failed outcome on H4/H5 must not
> be traded back into a claim-form title, abstract or contribution list.**

Two consequences, both for the principal as author of record:

1. **Any retitle is a post-lock change to a pre-registered element.** The pre-registration locked the
   question form; the data are in. Whichever title is picked, `PREREGISTRATION.md` would carry a dated
   amendment saying the title changed after the outcome was known and why (the narrowing ruled at row 11),
   and `paper.tex:438–443` (S13) would say the same. A title change that is not disclosed there would be
   the thing the sentence forbids.
2. **The rule bounds the form.** A title may *report* the answer (entropy's gate failed; the drop's
   passed). It may not convert the H4 entropy failure or the H5 failure into a positive claim. T1 keeps
   the locked question form and adds the answer; T2 reports the null; T3 is a claim-form title built on
   the H4 *pass* (the one outcome the rule does not restrict) with the failure named beside it — the rule
   bears on T3 most, and it is listed so the principal can reject it knowingly rather than not see it.

### 4.3 Three candidates — **drafted; the principal picks, I do not**

> **Status (2026-11-07):** T1 is **RATIFIED + APPLIED** (row 14; `paper.tex:34`, `f2bb1933`). T2 and T3 are **NOT ADOPTED**.

Each states the narrowed (multi-agent) claim and its answer, and none implies a "yes" for entropy.
"Pre-registered, Provenance-Complete" is retained from the current subtitle in all three since it is the
design claim the paper most wants to carry.

**T1 — question form kept, answer added (closest to the pre-registration)**

> Does a Multi-Agent Group's Confidence Distribution Predict Task Difficulty? A Pre-registered,
> Provenance-Complete Test on Perturb-seq Response Prediction in Which Entropy Fails Its Gate and the
> Confidence Drop Passes

- *Claims:* the multi-agent scope; that the test was pre-registered and provenance-complete; the two H4
  outcomes as reported (ACE fails its gate in both screens; $1-\Delta C$ passes in both,
  `results.tex:184–185`).
- *Does not claim:* cross-screen transfer (H5 fail is silent, not hidden — "Passes" is within-screen and
  the abstract says so); that compute allocation works; anything about the single-agent case.
- *Cost:* longest of the three; the subtitle carries a result clause, which the current subtitle does not.

**T2 — declarative, reports the null, names the group**

> Multi-Agent Confidence Entropy Fails Its Pre-registered Difficulty Gate on Perturb-seq Response
> Prediction: A Provenance-Complete Test of Agentic Hyperparameter Tuning

- *Claims:* the multi-agent scope; that the entropy gate failed (a report of the pre-registered outcome,
  `generated_numbers.tex:37` "4 of 5 gates pass; H5 fails"; `results.tex:184`); pre-registration and
  provenance.
- *Does not claim:* that entropy does not predict difficulty in general (gate failure is not absence of
  effect — `paper.tex:459–461`: "No mechanism is inferred; the negative point estimates are reported, not
  interpreted"); the $\Delta C$ pass (absent from the title); transfer.
- *Cost:* the headline is the negative result, and the quantity that passed is invisible until the
  abstract.

**T3 — declarative, leads with what passed, within-screen stated**

> The Confidence Drop Across Rounds, Not Confidence Entropy, Ranks Task Difficulty Within a Screen in a
> Multi-Agent Perturb-seq Predictor: A Pre-registered, Provenance-Complete Test

- *Claims:* the multi-agent scope; that $1-\Delta C$ rank-correlates with held-out error within each
  screen (H4 pass on that component in both screens, `results.tex:184–185`); that entropy did not, in
  the pre-registered direction; "Within a Screen" encodes the H5 failure (the calibrated composite "does
  not transfer at the pre-registered level", `results.tex:201–202`).
- *Does not claim:* transfer; a mechanism; that the drop is a sufficient allocation signal; anything
  about the single-agent case.
- *Cost:* the "Not Confidence Entropy" clause stands on the failed gate and a title cannot footnote
  "in the pre-registered direction"; this is the candidate §4.2 bears on most.

**Not drafted, on purpose:** any title containing "first", "novel", or "new"; any title naming CATTS; any
title whose headline is the general single-agent question.

---

## 5 · Surfaces a title change touches (for after the pick; nothing edited)

> **Status (2026-11-07):** **RECORD.** Executed for T1 in PR #42.

| surface | lines (cited) | note |
|---|---|---|
| `paper/paper.tex` | `34–36` (`\title`), `37–39` (`pdftitle`) | the two title fields in the source |
| `projects/perturb-seq-eval/CITATION.cff` | `5–8` | the work's title; the only work-title field in the project CFF (the other `title:` keys are references) |
| root `CITATION.cff` | `21` | carries the *repository* title ("bioFM — a living workspace…"), not the paper's — listed so "both CITATION.cff" is not read as this file |
| `projects/perturb-seq-eval/README.md` | `5` | quotes the title |
| `paper/README.md` | `1` | heading is the title |
| `paper/SUBMISSION.md` | `25`, `155` | runbook table and paste-ready metadata |
| `paper/PREREGISTRATION.md` | `25–29` | the locked rationale for the question form — amendment, not silent edit (§4.2) |
| `paper/paper.tex` | `438–443`, `458–459` | S13, S14 |
| Zenodo / Figshare records | — | fork (b) in #807 (retitle + new deposit version) is the principal's; not touched |

---

## 6 · The cs.MA cross-list — what the config PR touches (record only; the edit is on the working branch)

> **Status (2026-11-07):** **RATIFIED + APPLIED** (row 12; `arxiv.toml:75`, on `origin/main`). Row 15 has since **SUPERSEDED** the arXiv venue with TechRxiv, and submission stays BLOCKED until the principal reads the TechRxiv terms first-hand.

Row 12: keep `primary = "cs.LG"`, add `cs.MA` beside `q-bio.QM`. Planned diff, so the ledger and the PR
agree:

- `paper/arxiv.toml:63` → `cross_list = ["q-bio.QM", "cs.MA"]`; comment at `:58–61` rewritten to give the
  cs.MA rationale (the narrowed claim is a multi-agent one, row 12) and to stop describing the
  contribution as "a method claim … under a confidence-entropy statistic" (S16).
- `paper/SUBMISSION.md:28`, `:142`, `:158`, `:224`, `:288` — the runbook rows that restate the cross-list,
  so a human following the runbook pastes the ruled categories. Flagged in the `pr-submit` as in-scope
  consistency edits; the CTO can strike them.
- `scripts/arxiv_package.py` reads `cross_list` as a list (`:444`) and its `self-test` fixture (`:735`)
  pins only `primary`; no test pins the cross-list, so no test changes.
- Not touched: the title, CITATION.cff, the abstract, the bib, anything under `paper/` other than the two
  files above.

---

## Not established / not done

> **Status (2026-11-07):** **RECORD.**

- **Not done:** full-text read of arXiv:2605.19193 (§3-i). Not done: reading the five works named in the
  old novelty sentence (AutoGen, MassGen, Archon, MAV, CellForge) for the question — still unverified, as
  recorded in the companion file.
- **Not done:** any edit to `paper/`, `CITATION.cff`, the bib, PREREGISTRATION.md, Zenodo, Figshare, or
  any HACP surface. The bib entries for `lee2026catts` and `morandi2026sprt` are still to be written from
  the arXiv pages, in the PR that applies the ratified text.
- **Established (cited), bearing on §4.2:** `PREREGISTRATION.md` IS hash-pinned, by the run record, not by
  CI. `scripts/modal/app_v05.py:33` requires it "tracked and committed with no local edits" at run time and
  `:763` writes `preregistration_record(...)` — its sha256 and commit — into the v0.6.0 run record. The
  tests pin only fixtures (`tests/test_qg_p0p5_fixes.py:30–34`, `"a"*64`) and the amendment headings
  (`tests/test_fill_v060_numbers.py:1022`); no test compares the live file to the published record. So a
  post-lock amendment does not break the suite, but it makes the live file's hash diverge from the one the
  published run record carries — which is exactly the disclosure the pre-registration mechanism is for.
  A new "Amendment 5" heading with its own `prereg_version` would be the form the existing amendments use
  (`PREREGISTRATION.md:223, 511, 565`). **Not drafted; the principal's call.**
- **Not a defect, noted (#842):** `arxiv.toml` primary stays cs.LG; the nearest prior art is cs.AI.
