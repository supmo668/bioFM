# A7 publication-rigour review — Aviary-BioSim#2 (`whitepaper` @ `c66e64c`)

| | |
|---|---|
| Reviewer | CTO (biofm/matthew-mo/cto), A7 fork |
| Go | principal, 2026-10-09 ("approve") |
| PR | supmo668/Aviary-BioSim#2 — OPEN, draft; head `c66e64c585c145f9f0514962b404af88ca884fc2`, confirmed on the remote at review time (unchanged) |
| Receipt on record | Hash E `2a9b966` (not re-relied on: everything below was re-run) |
| Method | detached scratch worktree of `origin/whitepaper`; nothing in the submodule checkout modified; nothing pushed, committed, dispatched or commented |
| Spec | `docs/superpowers/specs/2026-09-25-v2r-biosim-whitepaper-design.md` (D1–D7, §2 may/may-not-claim, §3 evidence integrity) |

## Verdict: **fix-then-merge**

Every numeral in the text traces to its evidence file and matches; the headline science means
recompute exactly from `per_position_mean`. The two blockers are about the paper's *own*
thesis — a mechanism reporting a property that is absent: (1) the worked example's agent
narrative says things the agent's own artifact contradicts, and (2) the evidence files'
recorded `git_sha` does not identify the code that produced them. Both are fixable in text plus a
cheap re-run (the science scan takes ~10 s).

| Severity | Count |
|---|---|
| BLOCKER | 2 |
| MAJOR | 7 |
| MINOR | 8 |

## 1. Entry condition — re-run, not trusted

| Check | Command (from repo root of the scratch worktree) | Result |
|---|---|---|
| claims traceability | `uv run --script paper/claims.py` | `claims: ok`, rc 0 |
| paper suite, deps as `repo_tests.py` declares them | `uv run --with pytest --with pyyaml --with requests --with matplotlib python -m pytest -q paper/tests` | `122 passed in 5.77s` — matches `repo-tests.json` (122) |
| paper suite, bare | `uv run --with pytest --with pyyaml python -m pytest -q paper/tests` | `6 failed, 116 passed` — `ModuleNotFoundError: No module named 'requests'` (see A7-12) |
| PDF build | `tectonic -X compile main.tex` (scratch copy) | builds; **1 overfull hbox** (8.2 pt, `main.tex:38`), claims-table underfulls only |

## 2. Numbers — traced and recomputed

All 41 claims in `claims.yaml` resolve; values match the evidence. Recomputed independently:

| Claim | Evidence | Recompute |
|---|---|---|
| `subs` 2,090 · `matsubs` 1,634 | science.json | 110×19 = 2,090; 86×19 = 1,634 ✓ |
| `cysmean` −13.02 · `othermean` −5.85 · `othermeanall` −5.53 | science.json `per_position_mean`, cysteines [31,43,95,96,100,109], mature from 25 | −13.02 / −5.85 / −5.53 ✓ |
| `match` all true, `per_position_mean_matches` true | science.json | 10/10 keys true ✓ |
| `meas` 66 · `rounds` 5 · `tokens` 15,115 · `notokens` 1 · `positions` 34 | agent-run.json; raw artifact `science/out/discovery/discovery.json` sha256 `ed9b4e2f…` = recorded digest ✓ | 26+12+16+12+0 = 66; 6905+6304+1087+819 = 15,115; round 5 null ✓; 34 listed ✓ |
| `ctrlA..E` | science.json `c_peptide_controls`; raw artifact | Q62A +1.526, G70A +0.179, P72A +0.171, P79A +1.084, E83A −0.097 ✓ |
| `units` 6 | drain1-from-git.csv | 6 rows, R1→R5 in declared order ✓ |
| `sealed` 75 / `sealedfail` 0 | drain1-rerun.json | total 75, passed 75, skipped 0, unaccounted 0 ✓ |
| `chain` 6 · `closed` 6 · `parked` 0 | drain1-record-check.json | ✓ |
| `plugintests` 219 · `regtests` 60 | plugin-tests.json | ✓ |
| `taxrows` 22 | taxonomy.csv | 22 rows ✓; "two of the rows are about this paper" = T21, T22 ✓ |
| `traceroots` 1 · `tracetotal` 36 | weave-count.json | ✓ (wording, A7-10) |
| seqlen / accession / release / sha | science-input.json | published = fresh digest ✓ |

**Unmapped:** none by the script's regex. **Spelled-out counts are not bound** (A7-5).
**Evidence predating its code (D3):** 8 of 9 evidence files (A7-2).

## 3. Findings

### A7-1 · BLOCKER · the agent narrative is contradicted by the agent's own artifact
`paper/main.tex:21` (abstract), `paper/main.tex:104`

The text says: *"Having found the cysteines, it probed the C-peptide … at every position the evidence
lists for that region: a negative control nobody asked for, in the region where a negative control
belongs"*; abstract: *"ran controls in a region nobody asked it about."*

The raw artifact (`science/out/discovery/discovery.json`, digest matches `agent-run.json`) shows:
- **No "having found" sequence.** Round 1 requests all six cysteines *and* C-peptide positions 70 and 83 together; 62, 72, 79 follow in round 2. The agent targeted the cysteines in its first request — prior knowledge, not a finding.
- **The agent never mentions the C-peptide** (no occurrence in the artifact). Its write-up lists seven "Control positions that tolerate substitution": F25, Q62, D20, P79, P72, G70, E83 — two of them (D20 signal peptide, F25 = B1) outside the C-peptide. The region attribution and "where a negative control belongs" are the author's, not the agent's.
- **"Every position the evidence lists for that region" is circular.** Per `paper/README.md` (Order), `science_rerun.py` picks the C-peptide controls *from the agent's positions* (`agent-run.json:control_positions.c_peptide_positions_from_science_json` = `measured_by_the_agent`). The list covers the agent's choices by construction.

**Fix:** rewrite as reported: the agent probed the six cysteines in its first round; it named seven tolerant positions as controls (\claim-bound count), five of which fall in the C-peptide region as annotated by the scan; it did not refer to the region. Drop "having found", "nobody asked", "where a negative control belongs" from the abstract and §4, or label them explicitly as the author's interpretation. Bind the 7.

### A7-2 · BLOCKER · recorded `git_sha` does not identify the code that produced the evidence (routed D3)
`paper/scripts/_provenance.py:31,85`; `paper/evidence/*.json` `provenance.git_sha`; text claims at `main.tex:30,95,167`

- `science.json` records `git_sha 47afb55` at 21:32:54Z, but its `*_mature` fields only exist in the script committed one minute later in `55e2515` (child of 47afb55). It was produced from an **uncommitted working tree**; `_provenance.py` records no dirty flag (still true at HEAD).
- Commits touching each producer script (or `_provenance.py`) after its evidence's recorded sha: science.json 7 · agent-run 4 · science-input 5 · drain1-rerun 5 (+3 on the referee shell script) · drain1-record-check 5 · plugin-tests 5 · drain1-from-git 4 · repo-tests 0. Several of those commits fix defects that changed what a "measured" label could mean (e.g. `8e89ed7` Q6 "a fresh-fetch mismatch was still labelled measured and exited 0"; `a262129` F04/F08 "dropping any compared headline key but one left science.json saying every field matched").
- `science.json` was then edited by hand after the run (`provenance.model_facts_corrected`, `paths_redacted`) — disclosed inside the file, not in the paper.

The values are right (recomputed in §2); the claim *"every file was produced by one script … that wrote its exact run configuration"* is not.

**Fix (cheap):** add a dirty-tree refusal plus a `tree_clean` field to `_provenance.py` (perturb-seq-eval's `build_deposit.py` already refuses a dirty tree); re-run all eight producers from one clean commit in the README's order (science ~10 s); re-run `claims.py`; if the principal rules otherwise on D3, add a sentence to §6 saying the recorded commits precede later script fixes and name the hand-corrections.

### A7-3 · MAJOR · missing limitation: model and agent both had prior knowledge of the answer
`main.tex:87–89`, §6

ESM-2 (UR50) was trained on sequences that include insulin, and the agent's LLM targeted the cysteines before any measurement (A7-1). `SUBMIT.md:65` already says so ("ESM-2 has seen insulin, so this recovers known constraint"). The paper's "known answer" framing is fine for testing the *loop*, but §6 must state that the experiment says nothing about the model or the agent discovering anything (spec §2: "any biology beyond what science/out/ and the run trace support" may not be claimed).
**Fix:** one paragraph in §6.

### A7-4 · MAJOR · citation overreach: "Mutations at the six cysteines … cause permanent neonatal diabetes"
`main.tex:87`, `refs.bib` `stoy2007insulin`

Støy et al. 2007 reports a set of *INS* mutations in PND probands, some at or creating cysteines. It does not establish that mutations at **all six** cysteines cause PND. Verify against the paper's mutation table before publishing.
**Fix:** "Mutations at or creating cysteines in proinsulin, such as C96Y, cause permanent neonatal diabetes through misfolding~\cite{stoy2007insulin}", or whatever the table supports.

### A7-5 · MAJOR · the paper asserts that spelled-out counts are bound, but they are not
`main.tex:30`: *"Counts the evidence holds are bound the same way even where English would spell them out."*

`claims.py` matches digits only. Unbound counts that the evidence holds: "six cysteines" (`science.json:cysteine_positions`, len 6; lines 87, 95, 104, 134), "Six of the … shapes" (134), "Two of the rows" (138; taxonomy T21/T22), "Three review passes" (140; `deferred-findings.md` F08 passes 2–4), "one pass" (144). This is the paper's own failure shape: an assertion that a property holds when it does not.
**Fix:** bind them (`\claimncys` etc.), or soften line 30 to "digits".

### A7-6 · MAJOR · a signed receipt is claimed, not shipped, and it binds a different tree (routed D17)
`main.tex:106` — *"the referee signed a receipt (measured, re-run, dated)"*

`drain1-rerun.json` carries only the hash `6ad70cd` and a note: *"Hash E on the referee's receipt binds the CURRENT tree; the suite ran over the archived pass-end tree."* A reader cannot verify the receipt, and the receipt does not bind the `2e00aa3` tree that was tested.
**Fix:** ship the receipt file under `paper/evidence/` and state in the text which tree it binds, or drop "signed a receipt" from the measured claim.

### A7-7 · MAJOR · recovered-record claims conflict with the spec (routed D9, CTO-owned)
`main.tex:146` (`\claimchain`, `\claimclosed`, `\claimparked`)

Spec §2 "May NOT claim … anything from `.v2r/run-record-*.yaml`" and §3 prescribes "the register-written run record was lost". The paper now cites a record recovered from a worktree `.v2r`, under a careful new label. The paper is more honest than the spec, but the two disagree.
**Fix:** CTO spec amendment admitting the *recovered record* class (worktree copy, chain-verified, write-time unestablished). Otherwise remove the three claims.

### A7-8 · MAJOR · public-safety: tracker entity slug in shipped evidence
`paper/evidence/weave-count.json:4` — `"project": "<tracker-org>/Aviary-BioSim" (slug redacted here; pending the S1 ruling)`

The paper text is clean: the accession appears only in the methods (§4) and `evidence/`, per the F33 ruling, and there are no secrets, home paths or emails besides the author's. The org/entity slug, however, ships in evidence that the deposit includes (`publish.yml` artifacts: `evidence/`). The principal ruled this class out for perturb-seq-eval (S1, 2026-10-08: "remove it everywhere"). Whether S1 extends here is the **principal's** call. Do not apply it by analogy.
**Fix:** route to the principal. If yes, replace it with a neutral project descriptor and re-run `claims.py`.

### A7-9 · MAJOR · reproduction appendix points at a moving repository (routed D18)
`main.tex:166–167`

The appendix says "the repository's evidence README lists … the exact command" but pins no commit, tag or snapshot. Spec D6 requires a Zenodo frozen repo snapshot alongside the PDF. With D18 open, a reader of the PDF cannot reach the tree that produced the evidence.
**Fix:** print the release commit (or a tag) in the appendix and bind it as a claim; resolve D18 (frozen snapshot) before any deposit.

### A7-10 · MINOR · trace count wording mixes roots and traces
`main.tex:104` — *"1 root trace for the discovery run among 36 in the project"*. 36 is all traces; the project has 4 roots (`weave-count.json:project_roots`).
**Fix:** "one of the project's 4 root traces (36 traces in all)".

### A7-11 · MINOR · seven claims in the appendix are never used; the mutation count is promised but not given
`claims.yaml`: `othermeanall`, `scitests`, `wltests`, `papertests`, `mutlive`, `mutkilled`, `mutretired` appear in the appendix table only. `main.tex:140` says *"The count is reported as live entries plus retired entries"*, then reports no count.
**Fix:** cite `\claimmutkilled{}/\claimmutlive{} live, \claimmutretired{} retired` at line 140; drop or use the rest.

### A7-12 · MINOR · the paper suite's dependencies are undeclared in-tree
A bare `pytest paper/tests` fails 6 tests (`requests`, `matplotlib`). The only declaration is the `PAPER` list inside `repo_tests.py`. This is taxonomy row T12's shape (an undeclared reagent).
**Fix:** state the test command in `paper/README.md`, or add a PEP 723 / requirements file the tests use.

### A7-13 · MINOR · `entry_version` holds the sequence version
`paper/scripts/science_input.py:65` parses `SV=` (sequence version) into `entry_version` (`science-input.json`: `"1"`). Not cited in the text.
**Fix:** rename the field to `sequence_version`.

### A7-14 · MINOR · overfull hbox
`main.tex:38` (loop schematic), 8.2 pt.

### A7-15 · MINOR · compute/venue sentence (spec D2)
`main.tex:148` — *"a serverless inference endpoint. The venue that framed the work supplied no compute for it."* The endpoint is W&B Inference (`run_discovery.py`, `SUBMISSION.md:60`), and W&B is a CoreWeave company. The sentence is accurate under D2 (no venue grant or hardware). Naming the endpoint would pre-empt the question a reviewer will ask. Principal's call.

### A7-16 · MINOR · causal claim from an untested counterfactual
`main.tex:158` — *"closed first try only because its prompt named the answer"* (taxonomy T08, `docs/drain-1-notes.md`). n = 1, and the counterfactual was never run.
**Fix:** "closed first try, and its prompt named the answer (T08)".

### A7-17 · MINOR · label mixing in Figure 1
`main.tex:67` — the caption labels the figure *reconstructed*, but "none set aside" comes from the *recovered record* (`parked_count`). The git reconstruction has no park information.
**Fix:** attribute "none set aside" to the recovered record, or drop it from the caption.

## 4. Claims discipline — what passed

- Self-improvement is framed as a mechanism, never as a result (abstract, §6 first paragraph, §7) ✓
- Drain 1 is as-run only; no second pass is claimed ✓
- The seeded `.v2r/` fixture is described only as a limitation and is never cited as evidence ✓
- CoreWeave is not named as compute ✓ (see A7-15)
- Budget enforcement is disclosed as never run end to end ✓
- The cache integrity gap (F31) is disclosed under reproducibility ✓
- Author block: Mang-yin Mo / Independent researcher / mangyinm@alumni.cmu.edu ✓, plus ORCID 0009-0009-5233-3142 (check digit valid). `publish.yml` matches.

## 5. Routed findings × paper text

| Routed | Touches the text? | Where |
|---|---|---|
| D1 publish.yml ↔ submitter | no (deposit interface) | — |
| D3 evidence git_sha predates script edits | **yes** | A7-2 → lines 30, 95, 167 |
| D9 spec §2 vs recovered-record class | **yes** | A7-7 → line 146 |
| D15/D16 signed-plan checkboxes + verify keys | no | — |
| D17 referee receipt not shipped | **yes** | A7-6 → line 106 |
| D18 no frozen snapshot | **yes** | A7-9 → lines 166–167 |
