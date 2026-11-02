---
type: findings-staging
status: DRAFTED — UNRATIFIED. NOT FOR paper/, PREREGISTRATION.md, CITATION.cff, publish.yml, arxiv.toml, the bib, Zenodo, Figshare, arXiv or any HACP surface.
authorization: CTO #874 (2026-11-02, directive; principal instruction "pick up PDN item 2"). Authorized — draft Amendment 5 once per title candidate; apply the `paper/` sweep per candidate; re-derive the two downstream abstracts; record the hash consequence; READ arXiv:2605.19193 at full text. NOT authorized — choosing a title (the principal's, as author of record); adopting any differs-from sentence as paper text (§4.5 is drafted, not adopted). Standing: authorization (1) (CTO #812) — agents DRAFT, marked by provenance class; the principal ratifies.
agent: biofm/matthew-mo/perturb-seq-eval
paper_revision: projects/perturb-seq-eval/paper/paper.tex at HEAD of `perturb-seq-eval` — identical to ffccc92 (the row-11/12 ledger's revision) — verified by `git diff --quiet ffccc92 HEAD -- paper/paper.tex`; every line number below carries over.
preregistration_revision: paper/PREREGISTRATION.md at HEAD, sha256 6f8498eea879bb1e843511b03b821a567293402dff123487228c5f0c1330f270 (598 lines).
companions: 2026-11-02-narrowed-contribution-and-titles.md (§1.1 abstract draft, §1.2 bullet, S1–S19, §4.2 constraint, T1/T2/T3 §4.3); 2026-10-30-paper-framing-drafts.md ((b″), (b″-D)); 2026-10-31-catts-full-text-read.md (its format is reused in §4).
---

# Amendment 5 drafted three times, the sweep per title, the hash consequence, and the arXiv:2605.19193 full-text read — DRAFTED, 2026-11-02

**What this file is.** The three items CTO #874 asks for, plus the (b″) read it authorizes. **No title is chosen
here.** §1 holds one complete Amendment 5 per candidate (T1, T2, T3 of the companion ledger §4.3) so the
principal's pick costs one word; §2 shows which rows of the 19-row `paper/` sweep change under each; §3 re-derives
the two downstream abstracts (title-invariant); §4 reports the full-text read and drafts — does not adopt — one
differs-from sentence; §5 lists what the ratifying PR would touch. Nothing under `paper/` is edited.

| marker | means here |
|---|---|
| **cited** | a verbatim quote with its file:line or section ref, read by me at the source |
| **derived** | my inference from cited material, named as such |
| **drafted** | proposed text for the principal to ratify, strike or rewrite |
| **established** | a fact of the repository checked by a command whose output is stated |

**Rules applied, unchanged from #809/#812/#814/#817/#842/#848.** No number is typed by hand (macros or quotes). No
differs-from claim from an abstract. Nothing from a "me only" verification row carries a sentence in `paper/` until the
CTO has it at the ref. Key `lee2026catts`, never "the Lee paper". No claim that any prior work fails or underperforms.

---

## 0 · What every draft rests on — **established** / **cited**

**0.1 The lock** (`paper/PREREGISTRATION.md:25–29`, cited, verbatim):

> ## Why the title is a question
> The title asks whether agent confidence entropy predicts task difficulty, and does not assert that it does, so
> that a null answer is publishable as it stands. **A null or failed outcome on H4/H5 must not be traded back into
> a claim-form title, abstract or contribution list.**

**0.2 The pin, and the hash consequence — the live file has not changed since the run.**
`preregistration_record()` (`src/perturb_eval/experiments/provenance.py`) writes `{path, sha256, commit}` of this file
into the run record and refuses to run on uncommitted edits (`scripts/modal/app_v05.py:33`, `:763`). The v0.6.0 run
record carries, identically in `artifacts/v0.6.0/provenance.json`, `artifacts/v0.6.0/summary.json` and
`configs/runs/20260929T035447Z-ce5f237.json`:

> `"sha256": "6f8498eea879bb1e843511b03b821a567293402dff123487228c5f0c1330f270", "commit": "00fae29e35f9…"`

`shasum -a 256 paper/PREREGISTRATION.md` at HEAD, 2026-11-02 = `6f8498ee…f270` — **the same value.** So the file is
byte-identical to the one in force when the sweep ran, and **Amendment 5 would be its first post-run edit and the
first divergence of the live hash from the published record.** That divergence IS the disclosure (CTO #874 §3 agrees;
#871 did not contradict it): a reader who hashes the live file against `provenance.json` finds a mismatch and the
amendment section explains it. Nothing hides it and nothing is broken by it:

| what checks the file | what it checks | effect of an Amendment 5 |
|---|---|---|
| `tests/test_fill_v060_numbers.py:1014–` | ids in `paper/data/amendments_v060.json` are exactly `A1…A4`; each `## Amendment n (\`prereg_version\` = …)` heading exists and was introduced by its lock commit | **none**, provided A5 is NOT added to `amendments_v060.json` (see 0.3) |
| `tests/test_publish_deposit.py:1108` | sha256 of the RR-2 run-record correction entry | none — not this file |
| `scripts/modal/app_v05.py:33` | refuses to RUN on uncommitted edits | none — no run is planned under a5 |
| `paper.tex:574–575` "hypotheses and analysis plan & `paper/PREREGISTRATION.md`, at the revision named by `git_sha`" | names the pre-amendment revision | stays true; S13 (§2.3) names the later amendment |
| `\resPreregVersion` = `v0.6.0-a4` (`generated_numbers.tex:184`) | the run's version | stays `v0.6.0-a4` |

**0.3 Where Amendment 5 is NOT recorded, and why** (**derived**). `tab:amendments` (`results.tex:22–41`) is captioned
"Amendments to the pre-registration, each locked before any v0.6.0 data existed". A post-outcome amendment in that
table would make the caption false, and adding `A5` to `amendments_v060.json` fails the id test. So Amendment 5 lives in
`PREREGISTRATION.md` (its own last section + the preamble) and in the Discussion paragraph S13 — the two places a
reader of either surface meets it — and not in the pre-data table. If the principal prefers a table row, the caption
must change with it.

**0.4 The form** (**derived** from A2–A4, `PREREGISTRATION.md:223, 511, 565`): a `## Amendment N (\`prereg_version\` =
\`…\`): locked <date>, …` heading; one line in the Amendments preamble (`:12–20`, which already ends *"Any later change
is a fifth amendment."* — the hook A5 hangs on); the governing clause *"Where this section and any earlier text differ,
this section governs"*; then items as **Found** / **Amended rule**. A5 differs from A1–A4 in the one respect the
heading must carry: **it is locked AFTER the outcome.** On `prereg_version`: the drafts carry `v0.6.0-a5` for form only,
with the explicit statement that no data exist or will exist under it (an A1-style untagged amendment is the
alternative; default a5, principal's call). Lock date and commit are written at ratification/landing, as A2–A4's were;
neither is typed here.

---

## 1 · Amendment 5 — three complete drafts; **the principal picks ONE** — **drafted**

**Common to all three.** The title in force when the sweep ran, quoted from `:3–4` (cited):

> *Does Agent Confidence Entropy Predict Task Difficulty? A Pre-registered, Provenance-Complete Test of Agentic
> Hyperparameter Tuning for Perturb-seq Response Prediction*

**Preamble line** (appended to `:19–20` after *"Any later change is a fifth amendment."*, all three):

> **Amendment 5** (`prereg_version` = `v0.6.0-a5`, <ratification date>, principal ruling: approvals row 11 narrowed
> the contribution to the multi-agent case, row 12 ruled a retitle, and the title was picked on <date>), the last
> section, is the only amendment made **after the outcome was known**. It changes the paper's title and discloses that
> change; it changes no hypothesis, gate, estimator, convention or datum, and the v0.6.0 data were produced under
> `v0.6.0-a4`. No run exists or will exist under `v0.6.0-a5`.

**Title line `:3–4`** (all three): the picked title, followed by *"(retitled by Amendment 5; the title in force when
the sweep ran is quoted there)"*.

**A5-1 Found** (all three; every fact cited): the sweep ran under this file at commit `00fae29` (sha256
`6f8498ee…f270`, run `\resRunId`). Outcome `\resGateSummary` ("4 of 5 gates pass; H5 fails (0 unevaluated)",
`generated_numbers.tex:37`); "both tests fail the one-sided gate. The H4 pass is carried by the confidence-drop component
and by the composite that inherits it" (`results.tex:184–185`); "The calibrated index does not transfer at the
pre-registered level" (`results.tex:201–202`). On 2026-10-31 the principal narrowed the contribution to *a multi-agent
group's* confidence/critique distribution (approvals row 11) after `lee2026catts` (arXiv:2602.12276) was found to report
a single agent's vote distribution gating compute; on 2026-11-01 (row 12) a retitle and the cs.MA cross-list were ruled.
The locked title names *agent confidence entropy*, singular — the case the narrowing gives up — and the quantity whose
gate failed.

### A5 · T1 — question form kept, answer added

```markdown
## Amendment 5 (`prereg_version` = `v0.6.0-a5`): locked <date>, AFTER the v0.6.0 outcome — retitle; question form kept

<A5-1 Found, as above.>

**Amended rule (title).** The title becomes: *Does a Multi-Agent Group's Confidence Distribution Predict Task
Difficulty? A Pre-registered, Provenance-Complete Test on Perturb-seq Response Prediction in Which Entropy Fails
Its Gate and the Confidence Drop Passes.* The headline now names the object of the narrowed claim (the group's
distribution, row 11) in place of the single-agent quantity, and keeps the question form. The subtitle reports
the two H4 outcomes as measured: "Entropy Fails Its Gate" reports the H4 entropy failure (both screens);
"the Confidence Drop Passes" reports the H4 pass on $1-\Delta C$, within each screen. H5's failure is not in
the title and is stated in the abstract and Results.

**Why the null is not traded into a claim.** The rule of "Why the title is a question" forbids trading a null or
failed outcome back INTO a claim-form title. This title asserts nothing: it asks, and its subtitle reports a
failure as a failure and a pass as a pass. **On the locked rule, this amendment is a no-op: the question form the
rule protects is unchanged, and the rule itself is not engaged.** It is not a no-op on this file — the title line
and this section change, and the file's hash diverges from the published run record (that divergence is this
disclosure) — which is why it is written rather than omitted.

**Unchanged.** Every hypothesis, gate, estimator and convention of amendments 1–4; the run's `prereg_version`
`v0.6.0-a4`; "Why the title is a question" keeps both of its sentences, with this amendment noted beneath them.
```

### A5 · T2 — declarative; reports the null; the rule is engaged and disclosed

```markdown
## Amendment 5 (`prereg_version` = `v0.6.0-a5`): locked <date>, AFTER the v0.6.0 outcome — retitle to a declarative title that reports the null

<A5-1 Found, as above.>

**Amended rule (title).** The title becomes: *Multi-Agent Confidence Entropy Fails Its Pre-registered Difficulty
Gate on Perturb-seq Response Prediction: A Provenance-Complete Test of Agentic Hyperparameter Tuning.* The
question form is replaced by a declarative sentence whose content is the pre-registered null outcome of the
entropy gate, in the group setting the narrowed claim names (row 11).

**Why the null is not traded into a claim.** The locked rule forbids converting a null or failed outcome into a
claim-form title; it does not forbid reporting the null as the null. This title reports it as a failure of a
pre-registered gate — "Fails Its … Gate" — and claims nothing positive: not that entropy fails to predict
difficulty in general (the paper infers no mechanism and reports the negative point estimates without
interpreting them), not transfer, and not the $1-\Delta C$ pass, which is absent from the title and reported in
the abstract and Results. The rule IS engaged — the form changes from question to statement after the outcome
was known — and this section is the disclosure of that change. Cost, stated so it is chosen knowingly: the
headline is the negative result; the quantity that passed is invisible until the abstract.

**Unchanged.** As in the T1 draft. "Why the title is a question" is retitled "Why the title was a question, and
what Amendment 5 changed", keeping both original sentences verbatim as the locked text.
```

### A5 · T3 — declarative; leads with the pass; the rule is engaged most, and disclosed

```markdown
## Amendment 5 (`prereg_version` = `v0.6.0-a5`): locked <date>, AFTER the v0.6.0 outcome — retitle to a claim-form title whose claim is the H4 pass

<A5-1 Found, as above.>

**Amended rule (title).** The title becomes: *The Confidence Drop Across Rounds, Not Confidence Entropy, Ranks
Task Difficulty Within a Screen in a Multi-Agent Perturb-seq Predictor: A Pre-registered, Provenance-Complete
Test.* The question form is replaced by a claim-form sentence.

**Why the null is not traded into a claim.** The claim in the title rests on a PASS, not on a null: the
pre-registered H4 component $1-\Delta C$ rank-correlates with held-out error within each screen, in both screens
(`results.tex:184–185`) — the one outcome the locked rule does not restrict, because it is neither null nor
failed. The failed outcomes appear in the title as failures and bounds: "Not Confidence Entropy" names the H4
entropy failure; "Within a Screen" encodes the H5 failure (no transfer at the pre-registered level,
`results.tex:201–202`). No failed outcome is converted into a positive claim. Two things this section must say
because a reader of the title cannot see them: (i) the title cannot carry "in the pre-registered direction",
which is the exact scope of the entropy result; (ii) a title that leads with what passed may be READ as the
trade the rule forbids, so it is recorded here that the pass was itself pre-registered (H4, per component) and
would have been reportable in this form had entropy passed too. This is the candidate the rule bears on most;
it is written out so it can be rejected knowingly rather than unseen.

**Unchanged.** As in the T1 draft; the "Why the title is a question" section is retitled as in the T2 draft.
```

**Reader's one-line version per candidate** (for the CTO's Notion row; not paper text): T1 — *question kept, answer
added; rule not engaged.* T2 — *statement of the null; rule engaged, disclosed.* T3 — *claim built on the pass, nulls
named beside it; rule engaged most, disclosed.*

---

## 2 · The 19-row sweep, per title

**2.1 Title-invariant rows — apply under any pick** (verdicts and drafts in the companion ledger §2; nothing new):

| row | surface | what applies | status |
|---|---|---|---|
| S1, S2 | `paper.tex:56–59` | companion §1.1 (abstract opening) | drafted there; 1.1-e variant in §3.1 below |
| S3 | `paper.tex:109–112` | "As operated here, such a system spends compute uniformly…" | drafted there |
| S6 | `paper.tex:122–124` | companion §1.2 (bullet, either R2 order) | drafted there |
| S9 | `paper.tex:169–171` | (b″) + (b″-D), framing-drafts file; optional (b″)-morandi companion §4.5 | drafted; §4.5 NOT adopted |
| S12 | `paper.tex:358–359` | "Abstraction + metrics authored here" / "Procedures authored here" | drafted there |
| S16, S19 | `arxiv.toml:58–61`, `SUBMISSION.md:288` | the config PR | **done on the working branch, in pr-submit #863** (comment at `:58–61` now gives the row-11/12 rationale; `SUBMISSION.md:288` row 2 reads "RULED") |
| S17, S18 | `arxiv.toml:52`, `CITATION.cff:10–` | downstream of §1.1 | re-derived in §3 |
| S4, S5, S7, S8, S10, S11, S15 | — | keep | — |

**2.2 Title-dependent rows — what changes under each pick** (every location cited; the string is the candidate's):

| surface | lines | T1 | T2 | T3 |
|---|---|---|---|---|
| `paper/paper.tex` `\title` | `34–36` | T1 string | T2 string | T3 string |
| `paper/paper.tex` `pdftitle` | `37–39` | same | same | same |
| `projects/perturb-seq-eval/CITATION.cff` | `5–8` | same | same | same |
| `projects/perturb-seq-eval/README.md` | `5` | same | same | same |
| `paper/README.md` | `1` (heading) | same | same | same |
| `paper/SUBMISSION.md` | `25` (table), `155` (paste block — regenerated from CITATION.cff by `scripts/arxiv_package.py metadata`, "metadata sourced from CITATION.cff") | same | same | same |
| `paper/PREREGISTRATION.md` | `3–4`, `12–20`, `25–29`, new last section | §1 T1 | §1 T2 | §1 T3 |
| S13 `paper.tex:438–443` | Discussion paragraph | 2.3-T1 | 2.3-T2 | 2.3-T3 |
| S14 `paper.tex:458–459` | "The title question is answered as posed…" | 2.4-T1 | 2.4-T2 | 2.4-T3 |
| `results.tex` `tab:amendments` | `22–41` | unchanged | unchanged | unchanged (0.3) |
| Zenodo / Figshare | — | fork (b) of #807, the principal's | same | same |

**2.3 S13, drafted per title** (replaces `paper.tex:438–443`; `\texttt{paper/PREREGISTRATION.md}` is the existing
reference; no new `\ref` is introduced):

```latex
% T1
\paragraph{Why the question is posed as a question.} The title asks whether
a multi-agent group's confidence distribution predicts task difficulty rather
than asserting that it does, so that a null answer is publishable as it
stands; a null or failed outcome on H4/H5 is reported as the answer and is
not traded back into a claim-form title, abstract or contribution list
(\texttt{paper/PREREGISTRATION.md}). The title was amended after the outcome
was known (Amendment~5): the pre-registered title named agent confidence
entropy, singular; the amended title names the group's distribution, the
object of the narrowed claim, and its subtitle reports both H4 outcomes as
measured. The question form is unchanged.
```

```latex
% T2
\paragraph{Why the title reports a null.} The pre-registered title asked
whether agent confidence entropy predicts task difficulty, so that a null
answer would be publishable as it stands
(\texttt{paper/PREREGISTRATION.md}). After the outcome was known the title
was amended (Amendment~5) to report that answer: the entropy gate failed in
both screens. The amended title states the null as a null; it does not
convert it, or the H5 failure, into a claim, and the component that passed
its gate ($1-\Delta C$) is reported in the abstract and
\S\ref{sec:tdi-real}, not in the title.
```

```latex
% T3
\paragraph{Why the title leads with what passed.} The pre-registered title
asked whether agent confidence entropy predicts task difficulty, so that a
null answer would be publishable as it stands
(\texttt{paper/PREREGISTRATION.md}). After the outcome was known the title
was amended (Amendment~5) to a claim-form title whose claim is the
pre-registered H4 pass on the confidence-drop component, within each
screen; the entropy failure is named in the title as a failure, and the H5
failure is carried by ``within a screen''. No null or failed outcome is
converted into a claim.
```

**2.4 S14, drafted per title** (replaces `paper.tex:458–459` only; the following sentence "No mechanism is
inferred…" is unchanged):

```latex
% T1
The title question is answered as posed: on this evidence, the group's
confidence entropy does not predict difficulty in the pre-registered
direction, and its confidence drop across rounds ranks tasks by held-out
error within each screen.
% T2
The title's statement is the answer as measured: on this evidence,
confidence entropy does not predict difficulty in the pre-registered
direction.
% T3
The title's claim is the within-screen H4 pass on $1-\Delta C$; its negative
clause is this result: on this evidence, confidence entropy does not predict
difficulty in the pre-registered direction.
```

(`\S\ref{sec:tdi-real}` exists: `results.tex:124`, cited in the framing-drafts file R2-b.)

---

## 3 · The two downstream abstracts — re-derived; **title-invariant** (they follow §1.1, not the title)

**3.1 `CITATION.cff` abstract and `publish.yml` description** — GENERATED by
`scripts/paper/render_publish_description.py` from `paper.tex`'s abstract (**established**: `CITATION.cff:9`,
script docstring). Measured by calling the script's own `render()` on a temporary copy of `paper.tex` with §1.1 in
place of `:56–59`:

| abstract | rendered length |
|---|---|
| current | 2153 chars |
| §1.1 as drafted | 2353 chars (+200) |
| §1.1 with variant **1.1-e** below | 2362 chars (+209) |

**Finding 1.1-e** (**derived**; new ratification point): `render()` deletes every `\citep{…}` (regex
`~?\citep?\{[^}]*\}` → nothing), so the generated plain text of §1.1 reads *"…can gate its test-time compute is
already reported; we ask…"* — a prior-art statement with no referent, on the deposit surface. Variant: write
*"is already reported by \textsc{CATTS}~\citep{lee2026catts}"* — `\textsc{}` survives the render (as "CellForge" and
"MassGen" do today), so the plain text reads *"already reported by CATTS"*. Recommended; costs 9 characters. No cap
applies to this surface in the tooling (the only cap is arXiv's, `ARXIV_ABSTRACT_MAX = 1920`,
`scripts/arxiv_package.py:111`).

**3.2 arXiv override abstract** (`arxiv.toml:52`; author-ratified 2026-10-30 at 1906/1920 ASCII chars). Its first
two sentences are 221 chars; §1.1 in ASCII with a plain-text citation is 454 — so the override cannot take §1.1
verbatim (2139 > 1920) and must be re-derived, as `arxiv.toml:36–49` says the current one was. Candidate below:
**1916 chars, 0 non-ASCII**, checked mechanically against the current override's token set — every number,
every gate label H1–H5, `$\rho$ = 0.286 against > 0.4`, "0 unevaluated", "4 of 5 pass; H5 fails", the four metric
names, the roster, "recorded and asserted", "(exploratory)" and the v0.5.0 supersession are all present. Named
compressions, each a separate strike-able point:

| # | old | new |
|---|---|---|
| c1 | the two opening sentences | §1.1's claims in 365 chars: the "spent uniformly … as operated here" clause folded into the question; "already reported" → "reported"; "which would let … be allocated adaptively" → "so … can be allocated adaptively?" |
| c2 | "we define four compute-free trace metrics" | "we define four trace metrics" |
| c3 | "orchestrator for Perturb-seq prediction via MassGen" | "Perturb-seq orchestrator run via MassGen" |
| c4 | "and their composite, the Task Difficulty Index (TDI)" | "and their composite Task Difficulty Index (TDI)" |
| c5 | "We pre-register five hypotheses with gates:" | "Five pre-registered gates:" |
| c6 | "the Architect agent's backbone-choice entropy, the rank correlation of each TDI component with error" | "the Architect's backbone-choice entropy, each TDI component's rank correlation with error" |
| c7 | "The design is … drawn deterministically, with a trainer sweep of 27 records and" | "Design: … drawn deterministically; 27 trainer-sweep records and" |
| c8 | "The LLM condition is a pinned roster of Anthropic Claude models (…) whose served model is recorded and asserted per call; a run with any rule-based fallback step is invalid." | "LLM condition: a pinned Anthropic Claude roster (…), served model recorded and asserted per call; any rule-based fallback invalidates the run." |
| c9 | "The confidence-entropy point estimates run…" | "Confidence-entropy point estimates run…" |
| c10 | "The values reported in the v0.5.0 release of this work are superseded in full; the defects are listed in the appendix." | "The v0.5.0 release's values are superseded in full; the defects are listed in the appendix." |

```text
That a single agent's own vote distribution can gate its compute is reported (CATTS, arXiv:2602.12276); we ask the multi-agent question: does the distribution of stated confidences and critiques across a group of role-specialised agents predict task difficulty, so the group's compute -- spent uniformly across tasks as operated here -- can be allocated adaptively? In a five-agent CellForge-style Perturb-seq orchestrator run via MassGen, we define four trace metrics -- Agent Confidence Entropy (ACE), Critique Severity Dispersion (CSD), a convergence signal ($\Delta$C), and a Winner Flip Rate (WFR) -- and their composite Task Difficulty Index (TDI). Five pre-registered gates: attainable error on Adamson 2016 (CRISPR interference) and Norman 2019 (CRISPR activation), the Architect's backbone-choice entropy, each TDI component's rank correlation with error, and cross-dataset transfer of a calibrated TDI. Design: 41 held-out K562 tasks (21 Adamson, 15 Norman singletons, 5 Norman doublets) drawn deterministically; 27 trainer-sweep records and three fixed-length agentic runs per task. LLM condition: a pinned Anthropic Claude roster (Haiku 4.5 for the four proposer roles, Sonnet 5.5 for the Validator), served model recorded and asserted per call; any rule-based fallback invalidates the run. Gate outcomes: 4 of 5 pass; H5 fails (0 unevaluated) -- the trainer sweep attains the pre-registered error on both screens (H1, H2), the Architect exercises its backbone choice (H3), and the confidence-drop component and the composite rank tasks by held-out error within both screens (H4); the Adamson-calibrated composite does not transfer to Norman at the pre-registered level (H5, $\rho$ = 0.286 against > 0.4). Confidence-entropy point estimates run against the pre-registered direction in both screens (exploratory). The v0.5.0 release's values are superseded in full; the defects are listed in the appendix.
```

Status: **drafted**; needs the author's re-ratification exactly as the 2026-10-30 override did, and
`arxiv.toml:36–49` + `SUBMISSION.md:21` ("1906 characters") rewritten to this derivation in the same PR.

---

## 4 · arXiv:2605.19193 full-text read — report, in the CATTS-note format (#812 §2 scope)

**Status.** The READ was authorized by CTO #874 §(b″); **adoption of a differs-from sentence was not**. §4.5 is
drafted and left for the principal; option (ii) of the companion ledger — keep (b″) and accept the silence —
remains open and costs nothing. This section reports **(i)** what the signal is computed over, **(ii)** what it is
compared against and what it governs, **(iii)** what "working" means there — verbatim quotes with section refs.

### 4.1 Verification status (who has which fact at the ref)

| fact | section | verified at the ref by |
|---|---|---|
| Title "Sequential Consensus for Multi-Agent LLM Debates: A Wald-SPRT compute governor with calibration-based failure detection"; sole author **Andrea Morandi** (Cisco Systems, Inc.); **v1, 18 May 2026, the only version**; primary **cs.LG**, no cross-list on the listing; licence `arxiv.org/licenses/nonexclusive-distrib/1.0/` | arXiv listing; header line `arXiv:2605.19193v1 [cs.LG] 18 May 2026` | **me** (the CTO verified the abstract at the ref, #809) |
| "an LLM judge emits a $[0,1]$ consensus score on the latest agent positions; a Wald monitor accumulates the log-likelihood ratio …" | Abstract | CTO (#809) and me |
| "three heterogeneous agents (gpt-5, claude-opus-4-6, gemini-2.5-pro) and a claude-opus-4-6 consensus judge" | Abstract, §VI-H | CTO (#809, abstract) and me |
| The signal is a judge's score on the agents' positions, not the agents' stated confidences (quotes in 4.3) | §III, §IV, §VI-H | **me only** |
| "the consensus-score signal it consumes captures across-agent alignment, which is structurally different from within-agent confidence" | §VII-C17 | **me only** |
| Agent count $K$ held fixed; "The real-LLM evaluation fixes $K=3$"; sweep over $K$ "remains future work" | §IV, §VII-C14 | **me only** |
| Agents' own confidence is used only as a tie-break on no-consensus / no-plurality | §VI-F, §VIII, §VIII-A | **me only** |
| Per-difficulty breakdown is SIMULATED (tertiles defined by perturbing the Beta calibration's KL); no per-item difficulty quantity is measured from the agents' trace | §VI-J | **me only** |
| "no-consensus items cluster on the harder slice of each benchmark" | §VII-C5 | **me only** |
| GSM8K 3.7× call reduction at −2 pp; MMLU caps on 99.5 % at 2.1× cost, KL ≈ 0; none of the pairwise accuracy differences reaches significance | Abstract, §VI-H | CTO (abstract numbers) and me; the significance paragraph **me only** |

**Rule (CTO #814 §5, applied):** nothing in the "me only" rows carries a sentence in `paper/` until the CTO has it
at the ref. The four facts §4.5 rests on are the §III, §VII-C17, §VII-C14 and §VI-F/§VIII-A rows.

### 4.2 Source and how it was read

- Fetched 2026-11-02 into an isolated temp directory (`mktemp -d`; nothing executed from it): `arxiv.org/abs/2605.19193`
  (HTTP 200, 43 439 bytes, sha256 `09fa0564…`), `arxiv.org/html/2605.19193` (HTTP 200, 308 144 bytes, `ede54480…`),
  `arxiv.org/pdf/2605.19193` (HTTP 200, 968 820 bytes, `1e9538a0…`). No proxy 403, no egress block, no retry.
- Read from the **HTML** rendering, converted with the Python stdlib `HTMLParser` under `python3 -I`, each `<math>`
  element's `alttext` kept inline — equations below are the author's LaTeX. 787 lines of text. The PDF was downloaded
  and not text-extracted; not needed.
- Sections read in full: Abstract, §I, §II, §III, §IV, §V (A–G), §VI (A–K, incl. Tables I–V), §VII (A–C17), §VIII
  (A–C), §IX, §X. Not read: the reference list beyond its first entries; figure images (captions read).
- Version: only v1 exists; no "last revised" line on the listing.

### 4.3 (i) What the signal is computed over — **the unit is a judge's score on the group's positions after a round**

> "Pick $K$ LLM agents $\{A_{1},\ldots,A_{K}\}$ and a question $q$ . A debate is a sequence of rounds where each
> agent $A_{i}$ emits a position $p_{i,r}$ . After each round, an LLM judge produces a consensus score
> $s_{r}\in[0,1]$ measuring how strongly the positions converge on the central claim. High scores indicate
> alignment; low scores indicate divergence." — §III

> "Per-round consensus score $s_{r}$ : a single observation." — §III, "Three quantities matter", item 1

> `s_r := consensus_judge(q, positions)` … `Lambda += log(f_1(s_r) / f_0(s_r))` — §IV, Algorithm 1

> "The consensus judge is claude-opus-4-6 at temperature 0 with a strict-JSON prompt that returns a $[0,1]$ score
> and a one-sentence rationale." — §VI-H

> "the consensus-score signal it consumes captures across-agent alignment, which is structurally different from
> within-agent confidence; the two signals could in principle be combined, but our recipe uses only the former. A
> natural future direction is to use both signals via a two-channel SPRT." — §VII-C17

**Where the agents' own confidence appears (recorded and stopped):** "In a real deployment the orchestrator falls
back to a tie-break heuristic (highest individual confidence) on no-consensus items." — §VI-F; "the aggregator stays
simple: majority vote, with a confidence-weighted tiebreak when there is no plurality." — §VIII-A. The confidence is
used to pick an answer, not to decide whether to continue.

**Heterogeneity:** the three agents are three *models* ("gpt-5, claude-opus-4-6, gemini-2.5-pro", §VI-H), each
answering the same question; no role specialisation is described in the sections read. *(Recorded; no sentence drawn.)*

### 4.4 (ii) What it governs and what it is compared against

**What is governed: whether to run another round, with $K$ fixed.**

> "$H_{0}$ : agents are not converged, so one more round is justified. … $H_{1}$ : agents have converged, so the
> debate may stop." — §III

> "Holding $K$ fixed makes average per-round cost constant, and average total cost scales linearly with expected
> round count $\mathbb{E}[R]$ — precisely what the SPRT optimises." — §IV

> "The simulation does not track $K$ directly because the consensus score is the only observable … The real-LLM
> evaluation fixes $K=3$ . A sweep over $K\in\{2,3,4,5\}$ remains future work" — §VII-C14

> "At its core, the sequential-consensus rule is a stopping rule. It does not improve the per-round debate, modify
> the prompts, fine-tune any model, or synthesise a better answer" — §VII-C4

**Compared against:** benchmark accuracy and LLM calls per item, three protocols (B1 single-round vote, B2 fixed-5,
B3 SPRT) on 200 attempted MMLU and 200 attempted GSM8K items (§VI-H, Table III); in simulation, "SPRT classification
accuracy" at prior $\pi=0.5$ (§VI-B). The real-LLM calibration is **correctness-conditioned**: "$f_{0}$ is fit from
score sequences whose full-cap aggregate is incorrect, and $f_{1}$ … correct" (§VI-H).

**Difficulty.** The only per-difficulty analysis is simulated: "We simulate Easy / Medium / Hard tertiles by
perturbing the calibration's separation" (§VI-J); Table V's caption: "the SPRT correctly puts more rounds into harder
items." No quantity computed from the agents' trace is defined as an item-difficulty measure; the claim "no-consensus
items cluster on the harder slice of each benchmark" (§VII-C5) is stated without a difficulty definition in the
sections read. *(Recorded and stopped.)*

**Positioning in the author's own words:** "Every single one of these works uses a fixed round count; none tackles
the adaptive question … The contribution we make is orthogonal to all of them: a stopping rule that drops on top of
any such recipe." (§II); "Concurrent LLM-literature work uses sequential testing to decide when to stop sampling for
self-consistency; the setting there (single-agent ensembling) differs from ours (multi-agent interaction)" (§II).

### 4.5 (iii) What "working" means there

> "On GSM8K the rule terminates in 1.01 average rounds (4.06 LLM calls) at 97.0% accuracy versus 99.0% for fixed-5
> debate at 15 calls—a $3.7{\times}$ call reduction at $-2$ pp accuracy. On MMLU the rule degrades to its
> $R_{\max}{=}8$ cap on 99.5% of items because the judge cannot discriminate correct from incorrect multiple-choice
> consensus (calibrated KL $\approx 0$ ) … The main empirical point is therefore not that SPRT makes debate more
> accurate." — Abstract

> "Under that yardstick none of the pairwise differences between B1, B2, and B3 within either task reaches
> statistical significance" — §VI-H, "Ceiling effects and statistical power"

No pre-registration, gate or directional hypothesis is stated in the sections read *(an absence claim about sections
read; me only)*.

### 4.6 Does the full text support a differs-from sentence? — **derived**; and the DRAFTED sentence, **not adopted**

**Assessment.** Yes, on facts the author states himself, without characterising his method beyond his words: (a) the
governed signal is a judge's score on the positions (§III, §IV, §VI-H), not the agents' stated confidences, which
serve only as a tie-break (§VI-F, §VIII-A); (b) the author separates "across-agent alignment" from "within-agent
confidence" and says his recipe uses only the former (§VII-C17); (c) the quantity governed is the round count, with
$K$ fixed (§III, §IV, §VII-C14); (d) no item-difficulty quantity is measured from the trace (§VI-J simulated). Our
tested quantities are computed over the agents' own stated confidences (`results.tex:128–133`), rounds are fixed at
three (A2-2), and the claim is an item-difficulty signal (row 11). Each half of a differs-from sentence is therefore
a cited fact, not a reading of an abstract. **Option (ii) stays defensible:** (b″) as written is true, and the paper
says nothing false by its silence; the sentence below buys precision for the reader who asks "how is the Wald-SPRT
governor's group-level signal different?", at the cost of one more verified-at-the-ref obligation.

**Drafted — provenance `derived`; full-text-verified by me at the ref 2026-11-02; CTO verification of the four quoted
facts required before any adoption; NOT adopted; a companion to (b″-D), same shape, placed after it:**

```latex
The Wald-SPRT governor of \citet{morandi2026sprt} consumes an LLM judge's
consensus score on the agents' positions after each round (their \S III),
with the agent count held fixed (their \S VII-C14), and its author
separates that across-agent signal from ``within-agent confidence'' (their
\S VII-C17); the quantities tested here are the agents' own stated
confidences, and we do not gate rounds on them.
```

Every clause maps to a quote in 4.3–4.4; "we do not gate rounds on them" is A2-2 (fixed three rounds, no early stop),
cited. The sentence says nothing about the governor failing, nothing about what its author thinks of our signal, and
nothing about difficulty — the one place his text is simulated rather than measured, so no comparison is drawn.

**Bib fields verified at the ref for `morandi2026sprt`** (to be written into `references.bib` from the arXiv page in
the ratifying PR, not from this file): author Andrea Morandi; title as in 4.1; arXiv:2605.19193 [cs.LG]; v1 18 May 2026;
year 2026.

---

## 5 · What the ratifying PR would touch (record only; nothing edited now)

`paper/PREREGISTRATION.md` (`:3–4`, `:12–20`, `:25–29`, new last section — one of §1); `paper/paper.tex` (`:34–39`,
`:56–59`, `:109–112`, `:122–124` or R2, `:169–171`, `:358–359`, `:438–443`, `:458–459`); `CITATION.cff` (`:5–8`;
abstract regenerated by `render_publish_description.py`); `publish.yml` (description regenerated, same script);
`paper/arxiv.toml` (`:52` override → §3.2; `:36–49` derivation comment); `paper/SUBMISSION.md` (`:21`, `:25`, `:155`
paste block regenerated by `arxiv_package.py metadata`); `README.md:5`; `paper/README.md:1`; `references.bib`
(`lee2026catts`, `morandi2026sprt` from the arXiv pages). **Not touched:** `amendments_v060.json`, `tab:amendments`,
any test, Zenodo/Figshare (fork (b), the principal's), HACP.

## Not established / not done

- The lock date and commit of Amendment 5 — written at ratification and landing, as A2–A4's were.
- Whether Zenodo/Figshare impose a description cap — not checked; only arXiv's cap exists in the tooling.
- The five works named in the old novelty sentence (AutoGen, MassGen, Archon, MAV, CellForge) — still unread for the
  question; UAAD stays dropped (#812 ruling 4).
- `morandi2026sprt` §4.1 "me only" rows — not yet verified at the ref by the CTO.
- Not done: any edit to `paper/`, `PREREGISTRATION.md`, `CITATION.cff`, `publish.yml`, `arxiv.toml`, the bib,
  Zenodo, Figshare, HACP. pr-submit #863 is untouched and not re-submitted (#874 "Not in scope").
