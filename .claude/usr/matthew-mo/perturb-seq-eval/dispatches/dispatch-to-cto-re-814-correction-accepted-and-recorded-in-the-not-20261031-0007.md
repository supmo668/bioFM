---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-31T00:07
status: created
priority: high
size: task
subject: "Re #814: correction accepted and recorded in the note (my 'orthogonal' gloss was an inference, withdrawn). The one authorized sentence is written, derived, on §2 + §3.1 only — 30fc8f8 (pushed). Verification-status table separates CTO-verified from me-only; §4 carries nothing. Holding."
in_reply_to: 814
---

# Re #814: correction accepted and recorded in the note (my 'orthogonal' gloss was an inference, withdrawn). The one authorized sentence is written, derived, on §2 + §3.1 only — 30fc8f8 (pushed). Verification-status table separates CTO-verified from me-only; §4 carries nothing. Holding.

Agent: biofm/matthew-mo/perturb-seq-eval
Branch: perturb-seq-eval @ 30fc8f8 (pushed). paper/ untouched. Everything UNRATIFIED.

1. CORRECTION, recorded where it happened. In qa/_adhoc/2026-10-31-catts-full-text-read.md the §2 gloss now reads: 'these training-based and architectural improvements' has no fixed referent in the text; the preceding sentence names multi-agent debate, so the referent is probable by sentence order — probable is not a quote. A dated CORRECTION block names my #813 sentence verbatim and withdraws it. Lesson recorded in the same block, in your words: a correct reading of a real sentence attributed to a referent the text does not fix is the same failure class as a method claim from an abstract. I'd rather carry that one than hide it.

2. VERIFICATION STATUS, now a table at the top of the note: CTO-and-me at the ref — title, 'up to 11.8%', the §2 'fixed base agent' sentence (exact), the §3.1 one-model-one-step vote construction. ME ONLY — eq. 6–7/9–10, the §4.1 trajectory contrast + Fisher p=0.026 + binned net advantage, Table 3 figures, 'consistent 2.4% gain', and the ABSENCE of any pre-registration/gate/directional hypothesis in the sections read (appendices unread). Rule from your §5 is written under the table: nothing in the me-only rows carries a sentence in paper/ until one of us has it at the ref; the pre-registration contrast is written nowhere.

3. THE ONE SENTENCE — (b″-D) in the framing-drafts file, companion to (b″), provenance 'derived':
   \textsc{CATTS}~\citep{lee2026catts} computes its uncertainty statistics over $ candidate actions sampled from one base model at a single step (their \S3.1), under the stated assumption of a fixed base agent'' (their \S2); the quantities tested here are computed over the stated confidences of the five role-specialised agents of one run, within and across rounds (\S\ref{sec:tdi-real}).
   Rests on: CATTS §2 (verbatim quoted), CATTS §3.1 (verbatim quoted), results.tex:128–133 for our side. Says nothing about CATTS's view of multi-agent methods; nothing about CATTS failing or not generalising. If 'within and across rounds' reads as more than results.tex:129–133 supports (ACE of the final round; ΔC first→last), strike those three words — the sentence stands without them.

4. STANDING, as I now hold it: your #809 escalation is withdrawn; refuted = 'no prior work steers test-time compute on an internal confidence distribution' ((b″) stands); not refuted = a multi-agent GROUP's confidence/critique distribution as an item-difficulty signal. 'Negative replication' is a choice, not a consequence. Recorded in the drafts file header.

HOLDING: R2-a..e, (b″)/(b″-D)/(b′), title fork, ruling 3 — the principal's.

next_handoff: principal ruling via CTO → apply under QG, or changes-requested.
