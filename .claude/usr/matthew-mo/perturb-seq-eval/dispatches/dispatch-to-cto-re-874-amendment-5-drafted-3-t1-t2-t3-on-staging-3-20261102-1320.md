---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-11-02T13:20
status: created
priority: normal
size: task
subject: "Re #874: Amendment 5 drafted ×3 (T1/T2/T3) on staging @ 3711ac6; sweep + both abstracts per title; live prereg hash == run record (A5 = first divergence); morandi full text READ — differs-from sentence drafted, NOT adopted, silence still open"
in_reply_to: null
---

# Re #874: Amendment 5 drafted ×3 (T1/T2/T3) on staging @ 3711ac6; sweep + both abstracts per title; live prereg hash == run record (A5 = first divergence); morandi full text READ — differs-from sentence drafted, NOT adopted, silence still open

Agent: perturb-seq-eval. In reply to #874 (and #871, read; nothing requested there). Working branch untouched at d731370 (one misc instinct commit over the 0a69a20 PAUSE); pr-submit #863 untouched, not re-submitted.

## Staging ref
origin/perturb-seq-eval-staging @ 3711ac6 (aa96e6c + a one-line fixup), based on origin/main 5079a12, never a PR head (rows 83-86). File: workstreams/perturb-seq-eval/findings-staging/2026-11-02-amendment-5-drafts-and-morandi-read.md (502 lines). Every item marked cited / derived / drafted / established. Nothing under paper/, PREREGISTRATION.md, CITATION.cff, publish.yml, arxiv.toml, the bib, Zenodo, Figshare or HACP is edited.

## 1. Amendment 5, three complete drafts (file §1) — the principal picks one heading; I pick none
Form derived from A2-A4 (heading + preamble line + 'this section governs' + Found/Amended rule), with the one thing A1-A4 never had carried in the heading: 'locked <date>, AFTER the v0.6.0 outcome'. Common Found (all cited): run under commit 00fae29, outcome \resGateSummary, results.tex:184-185 / 201-202, rows 11 and 12.
- T1 (question form kept, answer added): on the locked rule :27-28 the amendment is a NO-OP — stated explicitly, as you asked, not omitted. It is not a no-op on the file (:3-4 names the title; the hash diverges), which is why it is written.
- T2 (declarative, reports the null): the rule IS engaged (question -> statement after the outcome). The draft says the rule forbids trading a null INTO a claim and does not forbid reporting the null as the null; names the cost (the pass is invisible until the abstract).
- T3 (claim-form, leads with the H4 pass): engaged most. The claim rests on the pre-registered PASS (1-DeltaC within screen, both screens); the failures appear as failures ('Not Confidence Entropy', 'Within a Screen' = H5). The draft records the two things a title cannot carry so it can be rejected knowingly.
Form choices I defaulted and flagged: prereg_version = v0.6.0-a5 for form only, with 'no run exists or will exist under it; the data were produced under v0.6.0-a4' (A1-style untagged is the alternative). Lock date/commit written at ratification/landing, not typed.
Where A5 is NOT recorded, and why (file §0.3): NOT in paper/data/amendments_v060.json (test_fill_v060_numbers.py:1017 pins ids == [A1..A4]) and NOT in tab:amendments (results.tex:22-41; caption asserts 'each locked before any v0.6.0 data existed' — a post-outcome row would make it false). Disclosed in the file itself and in Discussion S13.

## 2. Sweep per title (file §2)
Title-invariant (any pick): S1/S2 -> §1.1, S3, S6 -> §1.2, S9 -> (b″)+(b″-D), S12; S16/S19 are already DONE in #863; S17/S18 downstream (below). Title-dependent, per candidate: the 7 title surfaces (paper.tex:34-39, project CITATION.cff:5-8, README.md:5, paper/README.md:1, SUBMISSION.md:25 and :155 paste block regenerated from CITATION.cff), PREREGISTRATION.md :3-4/:12-20/:25-29 (+ new last section), S13 (paper.tex:438-443) and S14 (:458-459) — S13 and S14 DRAFTED per title in LaTeX (file §2.3, §2.4; no new \ref introduced).

## 3. Downstream abstracts re-derived — title-invariant, they follow §1.1 (file §3)
- CITATION.cff / publish.yml (generated): measured with the script's own render(): 2153 -> 2353 chars. FINDING 1.1-e: render() deletes every \citep{}, so the deposit text would read 'is already reported;' with no referent. Variant: 'already reported by \textsc{CATTS}~\citep{lee2026catts}' survives the render (2362 chars). Recommended; new ratification point.
- arXiv override (arxiv.toml:52, 1906/1920 today): §1.1 verbatim in ASCII is 454 chars vs 221 it replaces -> 2139, cannot fit. Re-derived candidate: 1916 chars, 0 non-ASCII; checked mechanically against the current override's token set — every number, H1-H5, rho = 0.286 against > 0.4, '0 unevaluated', the four metric names, the roster, 'recorded and asserted', '(exploratory)', the v0.5.0 supersession all present. Ten named compressions, each strikeable. Needs the author's re-ratification exactly as the 2026-10-30 one did.

## 4. Hash consequence (file §0.2) — established, not inferred
shasum -a 256 of the live PREREGISTRATION.md at HEAD = 6f8498ee…f270 = the sha256 in artifacts/v0.6.0/provenance.json, summary.json and configs/runs/20260929T035447Z-ce5f237.json (commit 00fae29). The file is byte-identical to the one in force when the sweep ran; Amendment 5 would be its FIRST post-run edit and the first divergence of the live hash from the published record. That divergence is the disclosure. Nothing in the suite pins the live hash (test_publish_deposit.py:1108 pins RR-2's digest, not this file); app_v05.py:33 refuses to RUN on uncommitted edits, nothing refuses to commit; paper.tex:574-575 ('at the revision named by git_sha') stays true.

## 5. (b″) outcome — READ done; sentence DRAFTED, NOT adopted; option (ii) still open (file §4, CATTS-note format)
Source: arXiv:2605.19193 v1 (the only version), 'Sequential Consensus for Multi-Agent LLM Debates: A Wald-SPRT compute governor with calibration-based failure detection', sole author Andrea Morandi (Cisco), 18 May 2026, primary cs.LG, no cross-list. Fetched abs/html/pdf into an isolated temp dir, HTTP 200 x3, no 403, no retry; read from the HTML with the stdlib parser under python3 -I, math alttext kept; sections read in full: Abstract, I-X.
Does the full text support a differs-from claim? YES, on the author's own words, with no characterisation beyond them: (a) the governed signal is an LLM judge's [0,1] consensus score on the agents' positions after each round (§III, Algorithm 1, §VI-H: judge = claude-opus-4-6 at temperature 0); the agents' own confidence is used only as a tie-break (§VI-F, §VIII-A); (b) §VII-C17 verbatim: 'the consensus-score signal it consumes captures across-agent alignment, which is structurally different from within-agent confidence; … our recipe uses only the former'; (c) what is governed is the round count with K fixed (§IV, §VII-C14 'The real-LLM evaluation fixes K=3'); (d) the only per-difficulty analysis is SIMULATED by perturbing the Beta calibration (§VI-J) — no item-difficulty quantity is measured from the trace. Drafted sentence (provenance derived; full-text-verified by me at the ref; a (b″-D)-shaped companion):
  'The Wald-SPRT governor of \citet{morandi2026sprt} consumes an LLM judge's consensus score on the agents' positions after each round (their §III), with the agent count held fixed (their §VII-C14), and its author separates that across-agent signal from "within-agent confidence" (their §VII-C17); the quantities tested here are the agents' own stated confidences, and we do not gate rounds on them.'
It says nothing about the governor failing and nothing about difficulty. The four facts it rests on are 'me only' rows in the verification table — per #814 §5 they carry no sentence in paper/ until you have them at the ref. Option (ii) — keep (b″), accept the silence — remains defensible and costs nothing; both are offered, the principal decides.
Bib fields verified at the ref for morandi2026sprt are recorded (file §4.6) for the PR to write from the arXiv page.

## Not done
No title chosen. Nothing adopted. Nothing under paper/ or any deposit surface. #863 untouched.

next_handoff: CTO -> principal. Five rulings, each one word or one strike: (1) title T1/T2/T3; (2) A5 form: a5 tag (default) or untagged; (3) 1.1-e (name CATTS in the abstract) ratify/strike; (4) the 1916-char override re-ratification; (5) (b″)-morandi sentence adopt / accept the silence. On the title pick + ratification I run /iteration-start -> apply to paper/ + PREREGISTRATION.md -> /quality-gate -> /iteration-complete -> /pr-prep -> /pr-submit on the working branch, bib entries from the arXiv pages, SUBMISSION.md paste block regenerated. HOLD until then.
