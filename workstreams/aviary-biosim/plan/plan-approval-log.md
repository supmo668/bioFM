# Plan approval log — aviary-biosim

**Append-only.** One entry per plan-gate sign. The approval file the agent verifies against lives in ITS repo worktree (workstreams/ is untracked in Aviary-BioSim); this copy is the coordinating repo's record.

| # | rev | hash | route | signed | plan | notes |
|---|-----|------|-------|--------|------|-------|
| 1 | r1 | `0ab65e9` | principal-directed via CTO | 2026-09-26 13:10 | Aviary-BioSim c885126 docs/superpowers/plans/2026-09-26-v2r-biosim-whitepaper-plan.md | **#272 white-paper plan signed under the principal's 2026-09-26 instruction (approve all; drive results of a rigorous academic publication).** CTO review before signing: structure (Tasks 0-13 map 1:1 to spec §4 + boundary), standing rules, gate table G1-G6, and the done-conditions of the three risk-bearing tasks: A1 (git archive + pytest inside the referee command, no test content reaches the agent), A3c (isolated env, model id + revision + weights sha256 recorded, MISMATCH reported before prose), A7 (fails on unmapped numbers, missing files, mismatches, and reported-phrased-as-measured). G1 was set in agency.yaml before signing. |
