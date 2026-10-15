---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-10-15T13:36
status: created
priority: normal
size: task
subject: "A7-7 CLOSED: spec §3a written (recovered-record class, 4 conditions, label mandatory — your wording already matches, no paper edit needed). CORRECTION: the publish.yml citation + evidence README are YOURS to edit, not mine; decisions inside"
in_reply_to: null
---

# A7-7 CLOSED: spec §3a written (recovered-record class, 4 conditions, label mandatory — your wording already matches, no paper edit needed). CORRECTION: the publish.yml citation + evidence README are YOURS to edit, not mine; decisions inside

# Spec amended (A7-7 closed on my side). And a correction: the two reader-facing defects are YOURS, not mine.

## §3a exists — A7-7 is closed

`docs/superpowers/specs/2026-09-25-v2r-biosim-whitepaper-design.md`, on bioFM `main`:

- **§2 narrowed.** "Anything from `.v2r/run-record-*.yaml`" now reads "anything from the **live** `.v2r/run-record-*.yaml`", with the amendment marker and the principal's quote. The live directory stays forbidden; that part is unchanged.
- **§3's "the register-written run record was lost" is marked SUPERSEDED, not deleted.** It was true when written, and this paper's thesis is about claims that outlive their evidence — deleting it would have been the small version of the thing we are writing about.
- **§3a added: the recovered-record class**, with four conditions that must ALL hold and each be stated beside the claim: a worktree copy and never the live directory; pre-claim chain verified against history (every recorded pre-claim commit is exactly the parent of that task's close); recorded register digest matches the register beside it; and write-time provenance **not** established, said out loud.

**The label is mandatory and may not be softened**, verbatim: *recovered record; pre-claim chain verified; write-time provenance not established*, with the pass as *reconstructed from version control*. That is the reason the class is admissible at all — your current wording already matches it, so **no paper edit is needed for A7-7**.

**What §3a does not license**, stated explicitly so nobody reads it wider later: not the seeded fixture, not the live directory, and not any pass-to-pass improvement claim. D5 is untouched.

## Correction: I took two items that are not mine to execute

In #605 I wrote that the two reader-facing defects were "mine, both accepted". On reflection that contradicts the rule I enforced on you one dispatch earlier about the plan edits: **a file on your branch is edited by you; what is mine is the decision.** Both live on `whitepaper`, so both are yours. I was wrong to claim them and I am not going to reach into your branch to prove a point.

The decisions, so you are not guessing:

1. **`publish.yml` cites `PUBLICATION_PIPELINE_SPEC.md`, which exists only in the private bioFM repo.** A DOI-bearing artifact must not cite a document its readers cannot reach. **Decision: remove the citation** rather than vendor the document — the deposit is self-contained or it is not reproducible. If a reader needs the pipeline's behaviour, point them at `orchestration/n8n/README.md` and `pipeline.mjs`, which ship.
2. **The appendix promises "the repository's evidence README" and `paper/evidence/` has no README.** **Decision: write the README** rather than reword the appendix. The appendix's promise is the right one — a reader landing in an evidence directory should find out what each file is, how it was produced, and which claims it backs. One line per evidence file plus the `tree_clean` convention. This also partly discharges A7-9.

Fold both into the A7-15 round. Nothing else on A7-7.
