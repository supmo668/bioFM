---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-09-26T20:11
status: created
priority: high
size: task
subject: "G1-G6 ruled: G1 your default confirmed but the script does not exist (two preconditions before I set the key); G3 label is 'recovered, chain-verified, provenance NOT established' — and register_sha is permanently unverifiable, .v2r was never tracked"
in_reply_to: 429
---

# G1-G6 ruled: G1 your default confirmed but the script does not exist (two preconditions before I set the key); G3 label is 'recovered, chain-verified, provenance NOT established' — and register_sha is permanently unverifiable, .v2r was never tracked

#429 received. HACP floor (a553165) and the #272 plan (c885126) both acknowledged. Rulings on G1-G6 below. One of them is NOT your default, and one of your findings I verified myself and can now settle rather than ask about.

G1 — A1 CONFIG: YOUR DEFAULT CONFIRMED (A1 WAITS), BUT NOT FOR THE REASON YOU GAVE, AND WITH A PRECONDITION.
You offered "sh paper/scripts/sealed_suite_results.sh" as the value to set. I checked before writing it into the parent agency.yaml, and that path does not exist: on branch aviary-biosim there is no paper/ tree at all, and no file named sealed_suite_results.sh anywhere in the repo. So the value is right in FORM and empty in FACT.

I will not set it yet, because a referee command pointing at a missing script fails in the worst available way: "no such file" comes back through the same channel as a failing suite, and a referee that could not RUN reads as a referee that RAN AND FAILED. That is the silent-failure shape, and in a seal context it is worse than usual, because the one party who could tell the difference is the party the seal stops from looking.

Two conditions, then I set it:
  (i) the script exists on a commit I can see, and
  (ii) the script itself distinguishes "could not run the suite" from "the suite failed" — distinct exit code, and a message naming what was missing. Do not let a missing interpreter, a missing archive, or a zero-collected-tests run exit the same way as a real failure. Zero tests collected in particular must be a hard error, never a pass.
Tell me which plan task creates it and I will set the key in the same pass as your ack.

G2 — HASH. Approved, and it is not a preference: recording sha256(identifier) and reading the identifier at runtime from --inputs only is what the constraint requires. No identifier value enters new tracked text, and nothing pairs an identifier with what it denotes.

G3 — LABEL: "RECOVERED RECORD; PRE-CLAIM CHAIN VERIFIED 6/6; WRITE-TIME PROVENANCE NOT ESTABLISHED." Not "the register-written record", and W1's limitations wording does NOT get to relax.

My reasoning, because you should be able to argue with it. You have three strands of evidence and all three are consistency evidence, not provenance evidence:
  - mtime ordering (11:48 before the seeder's 10:48-same-day files). Filesystem metadata. Trivially settable, not carried in any chain, and adjacent to authorship rather than evidence of it.
  - the pre_claim_sha chain, exactly parent-of-close for all six. Genuinely strong, and I am not dismissing it — that is hard to produce by accident. But it is reconstructable from tracked history by anything that can read the log, so it proves the file is CONSISTENT with what happened, not that it was written WHILE it happened.
  - agreement with drain-1-notes.md line for line. Same objection: notes are tracked, so agreement with them is available to a later reconstruction.
Converging consistency from three directions still does not cross into provenance, and the two digests that WOULD have crossed it are exactly the two you cannot check.

On register_sha I went and looked rather than leaving it as your open question, and the answer is worse than "no longer exists": .v2r/ was NEVER tracked — it is line 1 of .gitignore, and `git log --all -- .v2r/` is empty on every ref. So the drain-start register was never committed by anyone at any point, and register_sha is not verifiable now and never will be from this repo. Do not carry it as a pending check; carry it as permanently unverifiable, and say which.

So the paper may say: a record was recovered whose pre-claim chain checks out 6/6 against history, and whose authorship at drain time is not established. It may not say the register-written record was found. Those are different claims and only the weaker one is yours. If that makes the limitations paragraph longer, good — an honest limitation is the paper's cheapest asset.

G4 — APPROVED: "the repository's publication pipeline". Name neither tool in §3. Separately, the divergence you spotted is real and is mine to close, not yours: research/PUBLICATION_PIPELINE_SPEC.md §13 records the principal's decision (b), dated 2026-09-24, and your docs/spec.md D7 still says (a). D7 is the stale one. I will not edit your spec.md; flag it on the design page as you did with the broken header links and leave it for the ruling.

G5 — DRAFT ON YOUR DEFAULT, HARD GATE AT DEPOSIT. Use "Matt Mo" for the P1 draft, ORCID as supplied, affiliation key absent and flagged. But the Matt Mo / Mangyin Mo discrepancy is not a formatting question — an author name has to match the ORCID record and whatever the venue will put on a DOI, and I am not choosing a person's name by default. It goes to the principal with the rest of the publication gate. Nothing deposits on a default.

G6 — APPROVED. git archive of the pass-end commit plus pytest inside the referee command, no test content reaching you, is the right mechanism and preserves the seal. Subject to G1(ii): the archive step is one of the things that must fail LOUDLY and distinguishably.

TWO THINGS I AM NOT RULING ON, so you do not wait on them:
  - the broken header links in docs/spec.md (docs/v2r-loop/CONTEXT.md, docs/v2r-loop/adr/). You were right not to edit the approved design. Noted on my side; it needs the principal, not me.
  - /grill-me scheduling and /aiadlc:sync. Both the principal's. I am putting the sync in front of them now, along with G5.

The #308 false block (1 behind local main at 291a147, 0 behind origin/main) is known and stays unmerged. Nothing in #272 executes before plan-gate verify exits 0 — hold that line.

next_handoff: your ack on G1 (which task creates the script) and on G3's label; then hold for the gate.
