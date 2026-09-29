# Build Plan — ChipSim M0 Data Spine (slice 1)

**Workstream:** `lung-on-chipsim` · **Module:** `projects/lung-on-chipsim` (project root — every `Files:` path below is relative to it, per A&D AM-4)
**Source:** [Plan — ChipSim M0 Data Spine: Agent vs Human Implementation Roadmap](https://app.notion.com/p/2be47ffc30a34400ab31077cc57b3ffd)
**Implements:** the DrugBank clause of Design §1's S1 layer + §1.4's access ruling (see Scope check and A&D amendment AM-5). **Not** §1.2 beyond identity, **not** §1.3 splits/leakage, **not** S2–S8.
**Upstream:** [A&D](../A-and-D.md) · [PVR](../PVR.md)
**Revision:** r2 — 33 plan-validity defects and the scaffold hole folded in. See §7 Revision log.

## Goal

Build the ChipSim data spine through the **compound-identity and barrier-panel layer**,
sourcing DrugBank from a pinned public 2015 snapshot instead of an application-gated licence,
so that M0's contract tests go green with **zero administrative lead time**.

## Architecture

Three actors with a single allocation rule: a coding agent writes anything whose "done" is a
test that can fail, a human owns anything whose output is a *claim*, and ChipSim's own
experiment brain touches none of this until the spine exists. DrugBank enters as a frozen,
provenance-stamped snapshot pulled at build time by commit hash — **never vendored into the
repo** — and contributes drug→transporter edges only, **never affinities**.

## Tech Stack

Python 3.11 · pandas · **pyarrow (pinned — parquet engine; T5a/T15 write parquet)** · RDKit
(**used by T5b for canonical identity**) · PyYAML · pytest · DVC (data tracking) · requests ·
n8n Community Edition (ETL workflow export) · git. **No GPU in this plan.**

## Global Constraints

- **No coding agent writes a biological number.** Every value in `configs/theta_priors.yaml`
  and `configs/assumptions.yaml` is human-entered with a citation. The agent writes the schema
  and the validator that *rejects* an unsourced entry.
- **No coding agent curates the compound roster.** Which compounds are lung-relevant is a
  *claim* (T18), not a filter result. The agent writes the schema and the validator.
- **Non-commercial only.** Inherited from CC BY-NC 4.0 on DrugBank-derived data. Recorded in
  the model card, not assumed.
- **ChipSim never redistributes DrugBank.** Snapshot lands in `data/raw/`, DVC-tracked and git-ignored.
- **Nothing in this plan touches the frozen evaluator.** It does not exist yet; it is built in
  the M0 slice-3 plan and frozen by human signature.
- Every task is one action with a checkable done condition. **No `TODO`, no `TBD`.**
- **Every CA done-condition must be evaluable without a human artifact.** Where a task's real
  input is human-gated (T1/T2/T8/T14/T18), its done-condition runs against a committed fixture
  under `tests/fixtures/`; the live-data check is a separate *integration* condition, explicitly
  deferred and reported at the human boundary. (Defect 33.)
- **One interactive session per tree** *(r2.15 item 3)*. A worktree has exactly one interactive
  session that may commit to it; the trunk has exactly one CTO session that may write to it. A
  second session on the same tree **is** the signing hold: the tip moves mid-computation and no
  receipt verifies. **The grill draft's specific resolution of 2026-09-15 is VOID** — it directed
  closing pid `56186` on the worktree and pid `51059` on the trunk, on the premise that each tree
  held a second bare session. Verified by `ps` and `ListAgents`: `56186` **is** the worktree's sole
  writer, and the principal subsequently ruled that `51059` keeps this lane. The **principle**
  stands; its 2026-09-15 application does not. *Lesson recorded because it nearly cost the work: a
  constraint expressed as "close pid X" inherits whatever the premise about X got wrong — identity
  claims must cite the check that produced them.*
- **Record-bearing writers check an ALLOW-LIST of untracked output roots** *(r2.20)*. Any function
  whose payload can carry DrugBank record content — `write_adjudication_worksheet` (`name` beside a
  key) and `write_compounds` (accession + name + InChI + InChIKey **on one row**, the complete
  record) — must resolve its destination through **one shared helper** and refuse unless it is
  contained in a declared untracked root (`data/interim/`, `data/processed/`, the test tmp root),
  taken relative to the project root.
  **Checked on both the literal and the resolved path, by directory IDENTITY, refusing a symlinked
  destination or any symlinked ancestor, by containment — never by substring.** *(identity replaces
  "case-insensitively", r2.23 E-04: for an ALLOW-list, case-folding is the PERMISSIVE direction —
  the opposite of its effect on the deny-list it replaced, where folding closed the `CONFIGS/`
  bypass. The agent implemented identity and disclosed the deviation rather than leaving a signed
  clause contradicted by a docstring, which is the correct order of operations.)*
  **Identity requires the root to EXIST, so the guard distinguishes two failures with two messages**
  *(r2.23 E-06)*: a destination outside every declared root is **refused**; a declared root that is
  **missing** is a configuration error that fails loudly naming that root. They have different
  remedies, and one message for both would send a legitimate writer looking for a bug in its own
  path. *E-04's fix is what creates E-06 — identity buys precision and pays in an existence
  requirement; the pair is ruled together because neither reads correctly alone.*
  **Roots anchor to the project root discovered at RUNTIME, never to the installed package tree**
  *(r2.23 E-07)*: a non-editable install otherwise refuses every record-bearing write. Fifth in the
  ambient-state family — see the listing clause below, which had the same defect.
  **Operator-chosen destinations (`--dest`, `--out`) resolve through the SAME helper** *(r2.23
  E-01)*, and the declared roots cover the project's real untracked output locations — `data/raw/`
  (DVC-tracked, git-ignored) and the run journal — which were always legitimate and merely
  undeclared. **Why this is not a widening:** the invariant is *not written to a tracked path*, and
  both are untracked; leaving them out did not make them safe, it made the two most record-bearing
  writers in the project — `fetch_snapshot` (the raw DrugBank tables) and `merge_report.main` (the
  `--out` behind the 89-accession incident) — invisible to the helper entirely.
  **Why an allow-list and not a forbidden directory:** r2.19 guarded the *name* `configs/`. The §5
  reviewers executed **three** bypasses — `CONFIGS/` (which on a case-insensitive volume landed the
  name-bearing worksheet in the **real** `configs/`), a symlinked `configs` directory that
  `resolve()` erased, and check-one-object-write-another where `os.replace` swapped a destination
  symlink for a real file inside the tracked directory. It was simultaneously **too broad**,
  refusing every worksheet write under any `configs` ancestor, including the recovery path. A
  deny-list can only enumerate the attacks someone thought of; the invariant is *not written to a
  tracked path*, so the rule must name where writing IS allowed.
  **A registry test enumerates record-bearing writers and asserts each calls the helper**, so a new
  writer cannot silently opt out — the pattern that caught the unregistered fixture file.
- **Declarations are owned by the project whose artifacts they describe** *(r2.21, E6-1)*. Files the
  scan cannot decode are declared in **per-project declaration data** — a file in that project,
  following this module's own `DRUGBANK_ID_LEDGER` precedent of pointing at `configs/` rather than
  inlining — and the guard reads the union. Each entry carries **`path -> sha256`**, not a bare path
  *(E6-3)*: every declared file is a build output, so a path-keyed declaration goes silent forever
  the moment the artifact is regenerated with different content. An entry may instead assert
  **"derived from tracked source S, and S is in scope"**, which is self-maintaining and, unlike a
  comment saying "none of these is a DrugBank artifact", is a claim a reader can check.
  **Why:** 24 paths belonging to `perturb-seq-eval` and `paper_standalone` were declared inside
  lung-on-chipsim's source, so another team adding a figure turned this module's gate red and the
  repair landed in a file they neither own nor can judge.
  *A decision that looks like bookkeeping is still a shape decision if it assigns ownership.*
- **The FAILURE is scoped per-project; the LISTING is repo-wide; UNOWNED paths fail HERE**
  *(r2.22, E6-1b)*. An undeclared undecodable file **fails** the gate of the project that owns it —
  for this module, `projects/lung-on-chipsim/**` and `workstreams/lung-on-chipsim/**`. A path owned
  by **another** project (`projects/<other>/**`, `paper_standalone/**`) is **still listed**, with its
  owning project named, in a report the test prints and asserts on, but does not fail this gate.
  **A path owned by NO project — `.claude/**` and every other repo-root location — fails THIS gate**,
  so that scoping can never make a file unfailable everywhere. Ownership is read from an explicit
  map, and **a path matching no owner is unowned by definition, never "somebody else's"**.
  The **accession scan itself stays repo-wide and does not shrink** — this scopes only who a missing
  *declaration* blocks.
  **Unowned paths need a DECLARATION SURFACE, or the rule has no remedy** *(r2.23 E-05)*. Because
  unowned means every repo-root location (`docs/`, `config/`, `research/`, `tools/`, `.claude/`), a
  new `docs/architecture.png` from anyone fails **this** gate, and E6-1's "do not re-declare on
  their behalf" left no legitimate way to clear it. So: a **repo-root declaration file**, carrying
  the same `path -> sha256` or derived-from-source claim, which this gate reads. That is not
  re-declaring another team's artifacts — **an unowned path belongs to nobody, so there is no one
  else whose ownership is being assumed**, and this is the only gate that reads it. Rule 9 applies:
  state where declaring IS permitted rather than leaving the permitted case unreachable.
  **The declaration DATA itself is still unbuilt and that is not closed** *(r2.23 E-02)*. Nothing
  reads a union and E6-3's `sha256` pinning does not exist; only the removal half shipped, and
  E6-1b's scoping keeps the suite green without the rest — *which is exactly why it was easy to
  miss, and the agent found it by re-reading the clause against the code rather than by a failing
  test.* Build it for **this project's own** undecodable files and for the repo-root surface above.
  Do **not** author declaration files inside other projects.
  **The OWNER REGISTRY is part of that declaration surface** *(r2.24, E-11)*. A tracked marker is
  louder than `mkdir` but is still addable by anyone who adds a `pyproject.toml`, so it is a
  **mitigation, not proof**, and the report says so until the declared registry exists. The coupling
  was flagged **before** E-02 was built rather than discovered after — build the registry and the
  declaration surface together, as one thing.
  **The declaration data loads ONCE per report, through a snapshot** *(r2.25, E-14)*. Ruled on the
  correctness half, not the 19 redundant YAML parses: with no snapshot, a concurrent edit yields a
  **self-contradictory single report** — rows marked FAILS HERE under an owner the footer says fails
  nobody. A report that disagrees with itself is worse than a slow one. It lives in the guards module
  so E6-6's extraction is not complicated by it, and it is the home for the **two owner sets** below.
  **The registry may not police itself** *(r2.25)*. Placement was judged against the owner set
  defined in *the very file whose declarations it constrains*, so **delisting a project made its
  subtree unowned and therefore repo-root-declarable** — one edit, one file, another team's artifacts
  cleared, zero defects reported, demonstrated end-to-end against the shipped command (exit 2 → exit
  0 with a payload present). Two questions now use **two sets**: a path under an ownership prefix
  belongs to a project **whether or not that project is registered**.
  **An ABSENT declaration file is not an EMPTY one** *(r2.25)*, exactly as this module already says an
  unreadable one is not — reading absent as empty silently reverted the registry to the pre-r2.24
  marker-only mitigation with a healthy exit code. *E-02 reproduced inside the fix for E-02.*
  **Every defect in an entry is reported in one pass** *(r2.25, E-15)*: a reader who learns their
  entry's next problem one gate run at a time is being made to bisect their own data.
  **Topology placement folds into E6-6** *(r2.24, E-09)*. `repo_root()`, `source_root()`,
  `THIS_PROJECT` and E-07's runtime anchor are **not** extracted into a new `chipsim/paths.py` now:
  placement reassigns ownership of a primitive across modules, which is a shape decision (rule 10),
  and doing it here would force the already-authorised E6-6 extraction to undo it. E6-6 moves guard
  code only, and takes the anchors with it when it runs.
  **This clause is load-bearing for E6-4:** `.claude/usr/**/dispatches/` belongs to no project, so a
  non-`.md` dispatch payload keeps failing here. Drafted without the unowned rule, E6-1b silently
  re-opened the `dispatches/leak.pdf` hole that E6-4 had closed one clause above — found by reading
  the two against each other before signing, which is the check r2.17 did not get.
  **Why:** E6-1 and the r2.20 fail-closed clause did not compose. Measured in the merged tree: of 24
  declared paths **0 belong to this project**; removing them as E6-1 requires, with no declaration
  data yet existing in the owning projects, made this module's live test fail on **24 files owned by
  two other teams**. That inverts the coupling instead of removing it — before, another team *adding*
  a figure turned this gate red; after, another team *not yet having adopted the rule* turned it red
  on day one. The repair still landed where the knowledge is not.
  **The residual risk is stated, not hidden:** a genuinely undecodable file outside this module's
  paths is neither read nor declaration-gated here. E6-2 shrinks that set to *rendered* artifacts
  only, since every readable structured container is now read repo-wide wherever it lives. What
  remains is visible and countable in the report.
  **"It fails their owner's gate" is FICTION today, and the plan says so** *(r2.23 E-03)*. No other
  project implements this gate, so the 23 listed files fail **nowhere** — they are listed here and
  gated by no one. That is the true state and the honest reading of "the repair lands with the
  owner": the owner has no gate to land it in yet. **The listing is therefore the whole mechanism,
  not a courtesy**, which is why the next clause makes rendering it non-optional. The CTO wrote
  "the owning team's to close" in r2.22; the agent measured that no such closing exists and said so.
- **The listing must be RENDERED, at the REPO root, by a shipped command** *(r2.23 E-08)*. A listing
  asserted on only inside tests reaches nobody, and a listing reaches nobody is a silent skip with
  extra steps — the precise thing r2.20 forbids. `chipsim record-content-report` prints every
  undeclared undecodable file with its owner and exits non-zero when any falls to **this** gate.
  **It takes the REPO root, never the project root.**
  **The command must also prove it SCANNED something** *(r2.24, E-08b)*. Fixing the root *selection*
  left the root *validation* and the file *listing* able to fail silently, and they composed: no
  `.git` above the package → silent fallback to the narrow root → `git ls-files` fails there → the
  listing swallows the failure and returns `[]` → *"0 (failing this gate: 0)"*, exit 0, **printed
  with the true repo root interpolated**. So: `check=True` on the git call, a floor on the tracked
  count, and every tracked path resolves — the anti-vacuity guard that **already existed in the
  tests and not in the command**. Reachable with no attacker: a non-editable install, a root-owned
  CI checkout refused by `safe.directory`, a corrupt index, a shimmed `git`.
  **The environment may not steer the listing** *(r2.24)*: all `GIT_*` variables are dropped (not a
  curated list — git adds new ones), and config the scanned tree supplies and git *executes*
  (`core.fsmonitor`) is disabled, satisfying both halves of the `#44` B2 ruling. **An owner may not
  be minted with `mkdir`** — an owner must carry a tracked marker, since under E-03 an *invented*
  owner is strictly better for an attacker than a real one, nobody being even nominally
  responsible. **Paths are escaped when not printable**, because a filename beginning `ESC[2J ESC[H`
  drew a complete fake all-clear over the real report.
  **An unresolvable tracked path is COUNTED AND REPORTED always, and FAILS only when we own it**
  *(r2.24, E-10)*. A payload committed in HEAD but absent from disk (sparse, `skip-worktree`,
  partial clone) must never be silently dropped — that is the original sin — but making it fatal
  outright makes the report unrunnable in a legitimate sparse checkout. Scoping the *failure* by
  ownership is exactly E6-1b; scoping the *count* would repeat E-08. Exit 3 stays reserved for
  "could not scan at all", distinct from exit 2 (files fail) and 0 (clean).
  **A BROKEN DECLARATION FILE IS NOT "could not scan at all"** *(r2.25, E-13)*. The scan works; only
  the exemption data is unreadable. So: **treat nothing as declared** (the fail-closed direction —
  more files fail, never fewer), **still render the listing**, and **exit 2 with the structural error
  reported alongside, naming the file**. Turning the whole gate to exit 3 hid which file actually
  failed. **The header counts declaration defects and undecodable files SEPARATELY**, so the first
  line adds up on its own; mixing two categories into one `failing` number makes the summary
  unreadable exactly where a reader checks it first.
  **Assertions bind the OBSERVABLE the consumer sees, not only the function's return value**
  *(r2.25, E-13b)*. **12 mutants survived the entire 851-test suite**, including this work's own
  headline claim that a declaration whose claim does not hold fails the gate — every defect test
  asserted on the validator's return and none on the **exit code**, so the command could pass while
  the function was correct. This is E-08's function-versus-command split reappearing as a testing
  habit rather than a call site.
  **Reviewer isolation gains a PER-REVIEWER copy and a verified interpreter** *(r2.25, E-16)*. The
  shared `.venv`'s editable install points at the **worktree**, so a reviewer running a script from
  the wrong cwd exercises *the tree being hashed* rather than its own copy — a reviewer hit exactly
  that and disclosed it, and a concurrent reviewer had already destroyed a shared copy mid-session.
  One throwaway copy **per reviewer**, and each verifies its **interpreter resolves inside that
  copy** before mutating anything. *Sixth in the ambient-state family — the throwaway-copy rule
  telling us its next requirement.*
  **E-16 IS SATISFIABLE SUPERFICIALLY, AND WAS — VERIFY THROUGH THE ENTRY POINT THAT MEASURES**
  *(agent-found, drafted by the worktree agent at the CTO's request, signed r2.41)*.
  The clause above says "verifies its interpreter resolves inside that copy". That was satisfied
  literally — with `python -c` — and the measurement was then taken with **`pytest`**, which
  imported the **original worktree anyway**: the copied `.venv` carries the *editable install*
  with it, and an editable install points at the tree it was created for, not at whatever
  directory now contains it. **Four mutants were scored without ever being loaded.** The check
  passed, the run was meaningless, and nothing in the wording caught it.
  **The rule therefore has two halves and both are required:** (1) **rebuild the environment in
  the copy** (`rm -rf .venv && uv sync`) so no editable install survives the copy; and (2) run the
  verification **through the same entry point as the measurement** — if the mutants are scored by
  `pytest`, the interpreter check must be made by `pytest`, not by a `python -c` that resolves
  differently. A verification that takes a different path from the thing it verifies is not a
  verification of it.
  **THE GENERAL SHAPE, WHICH IS WHY THIS IS WORTH A PLAN AMENDMENT RATHER THAN A NOTE**: a rule
  that NAMES a hazard can still be satisfied by a check that does not REACH it, and it then reads
  as protection while providing none. E-16 named the editable-install hazard in its own first
  sentence and was still satisfied superficially by the person who wrote the check. *Seventh in
  the ambient-state family, and the first where the defect was in the guard's own wording rather
  than in a missing guard.*
  **Mutating in place in the live worktree avoids the hazard entirely** (nothing is copied, so
  nothing can resolve to the wrong tree) and is what the M1 transport work used. That is a
  CLAIM about a run, though, so it was checked rather than assumed: `m.__file__` resolves to the
  file the mutation script rewrites, and 10 of 11 mutants in that file were killed — positive
  proof that a mutation of it reaches the test run. Either discipline is acceptable; what is not
  is a copy whose environment was never rebuilt.
- **E6-7 — ONE ENTRY POINT A NON-PYTEST CONSUMER CAN CALL, AND THE FAIL LIVES IN IT** *(stated
  r2.26; authorised verbally at r2.21 and, until now, WRITTEN NOWHERE HASH-LOCKED)*. Today the four
  pieces — readability, declarations, ownership, accession content — are composed by the **test
  suite** and by the **report renderer**, so the invariant is enforced for whoever runs `pytest` and
  for nobody else. E6-7 is a single public function that runs all four and **fails**, callable by CI,
  a pre-commit hook, or another project. It **composes** the existing checks and re-implements none
  of them, so there stays one definition of each. Its outcomes follow the exit-code contract already
  ruled *(E-13)*: clean, files-fail, could-not-scan — three states, not a boolean.
  **E6-7 IS NOT YET SATISFIED, and the CTO accepted evidence that it was** *(r2.28)*. The shipped
  `record-content-report` composes **three** of the four — readability, declarations, ownership —
  and `real_accession_hits` / `ledger_tuple_hits` are **unreachable from it**; `enforce_record_content`
  has **no caller outside its own test file**. The accession half is enforced by `pytest` and by
  nothing a consumer runs. **The CTO cited that command's `23 listed / N scanned / 0 failing / exit 0`
  as compliance evidence in reports and verifications; it is not that evidence.** The tree *is* clean
  on accessions — the live-repo scans at `test_record_content_guard.py:170` and `:244` establish that
  — but the conclusion rests on the suite, and was attributed to the command. Wire the accession half
  into the entry point, or the clause is unmet. *E6-5 applied to the CTO: a mechanism enforcing three
  halves may not be cited for the fourth.*
- **"IS AN ETL RUN" AND "MAY BE INVOKED UNATTENDED" ARE TWO PREDICATES AND MUST NOT SHARE A TUPLE**
  *(r2.34)*. `SUBCOMMANDS` / `NON_ETL_SUBCOMMANDS` encode a **conjunction**: the comment says
  *"NOT ETL stages **and** must never appear in the n8n workflow"*, and the ETL list's own comment says
  *"the workflow export is checked against these keys"*. So the scheme can express *ETL + node* and
  *non-ETL + non-node*, and **cannot express the combination T13 actually has.**
  **T13 (`adjudication-worksheet`) is the proof, and the agent's ETL classification is CORRECT**: it
  reads the snapshot and writes a derived artifact, so it earns the per-run config snapshot and the
  §16 approval prompt, and it is *not* human-reserved the way `panel-seal` is — it produces a draft
  **for** a human. **But it must not be a node in an unattended chain**, which could regenerate a
  worksheet mid-adjudication. Forced to pick one tuple, the correct ETL answer buys a wrong node
  answer.
  **This is the rule this plan already carries — *two predicates with opposite safe directions may not
  share a source* — applied to a tuple rather than a default.** The safe direction for journalling is
  **include** (more run-records cost nothing); for unattended invocation it is **exclude** (fewer
  automated entry points). One membership test cannot serve both.
  **Required:** split into two independent predicates, and have the workflow-export check compare
  against the **node** list, not the ETL list. Record each command's reason separately — `panel-seal`
  is non-node because Global Constraint 4 **reserves it to a human**; T13 is non-node because
  **regenerating mid-adjudication destroys the premise of a 60–90 minute human task**. Same answer,
  different reasons, and a reader who sees only the tuple cannot recover either.
  **Severity — CORRECTED IN PLACE, r2.35. The original sentence was false.** It read: *"T13 ships in
  the ETL list, so it IS currently exported as a node."* **It was not exported.**
  `orchestration/n8n/etl_drugbank.json` carries exactly five nodes — `fetch`, `hash-verify`, `parse`,
  `provenance-tests`, `write` — and `adjudication-worksheet` is not among them. Measured by parsing the
  JSON, after the agent reported the error. The conflated tuple made T13 node-**ELIGIBLE**, and nothing
  forced the JSON to carry a node per ETL command (`test_t16_has_the_five_nodes_in_order` pins it to its
  own constant), so the hazard was **LATENT — waiting for the next regeneration from the conflated
  list — not live.** The never-clobber observation stands: a guard written for a different purpose
  would have been the only thing between an automated chain and the human's work, which is defence by
  coincidence. **The required fix is unchanged.** Only the urgency was overstated.
- **CHOOSING THE UNCOMFORTABLE READING IS NOT MEASURING, AND A RULING CAN BE RIGHT ABOUT A DEFECT AND
  WRONG ABOUT WHETHER IT HAS FIRED** *(r2.35)*. The CTO wrote r2.34's severity sentence as the
  deliberately *un*comfortable version, on the reasoning that a coordinator should not minimise a
  hazard in its own ruling. **That reasoning is correct and it did not make the sentence true.** It
  asserted that an export had happened, without opening the exported file — substituting a disposition
  (be conservative) for evidence, which is the same substitution as assuming the comfortable reading,
  wearing more respectable clothes. **A pessimistic claim is still a claim and still needs a
  measurement.**
  Stated as the agent put it, because it is the better phrasing: *accepting the uncomfortable-sounding
  version without checking is the same failure as accepting the comfortable one.* Both parties have now
  done this in the same section — the agent over-claimed "could never fire" in r2.27 E-19 and corrected
  it; the CTO over-claimed "is currently exported" here. **It is not a failure mode that respects which
  direction the error flatters.**
  **Operational rule:** a severity claim naming a live state — *is exported, is invoked, is reachable*
  — is checked against the artifact that would carry it before it is signed, exactly as a done-condition
  naming a path is checked against that path (r2.33). Severity is a done-condition about the world.
- **A GUARD'S SILENCE IS NOT THE PLAN'S APPROVAL, AND THE INFERENCE GETS EASIER THE MORE GUARDS
  EXIST** *(r2.33)*. T5a's artifact was first written to `data/interim/compounds.parquet` — the wrong
  directory **and** the exact filename this plan forbids by name (A&D §1 reserves `compounds.parquet`
  for the harmonized multi-source S1 artifact, defect 30). **The output-root guard correctly allowed
  it**, because `data/interim` IS a declared root. That guard answers *where a record-bearing payload
  may land*; it has never answered *which artifact the plan asked for*, and it was never built to.
  **The failure mode is the inference, not the guard.** "It passed the gates" is a cheap and
  increasingly available substitute for reading the done-condition, and this workstream has spent five
  iterations making the gates more trustworthy — which makes the substitution *more* tempting, not
  less. A hardened gate is a MECHANISM; the artifact the plan named is the COVERAGE.
  **Deliberately NO new mechanism.** A path-shape check would encode the plan's prose into the guard
  and rot on the next revision, and it would answer a question the guard is not the right owner of.
  What is required instead: **a done-condition naming a path is checked against that path, by reading
  the plan, before the step is called complete.** Caught here only by going to look.
- **THE STAGED TREE MAY NOT LIVE INSIDE THE TREE IT CERTIFIES** *(r2.32)*. The staged reader
  materialises **every tracked blob**, and `tempfile` honours `$TMPDIR`. A staged root that resolves
  inside the scanned working tree — or under any `DECLARED_OUTPUT_ROOT` — is therefore **REFUSED**.
  Without this, pointing one environment variable at the repository makes the gate write a complete
  copy of the tracked corpus **into the tree it is about to scan**: a self-referential scan, and a
  copy `git add -A` would stage. **Resolve both sides; never prefix-match** — a staged root reaching
  the tree through a symlink shares no string prefix with it, and the string-comparison mutant dies
  on a test for exactly that route.
  **`declared_output_roots()` is NOT the predicate here.** Under pytest it appends a `$TMPDIR` grant
  so record-bearing writers may write to tmp during tests; reusing it made the refusal reject every
  staged tree the suite builds, and the suite caught it on the first run. The grant answers *may this
  writer write here*; this check answers *may the gate read here*. Two predicates, opposite safe
  directions — they may not share a source, per the rule already in this plan.
  **The SIGKILL residual is ACCEPTED, documented, and deliberately NOT swept.** The tree is mode
  0700, holds a copy of **tracked** blobs already at rest in the same repository, and the OS reclaims
  the system temp dir; an unattended destructive sweep is a worse risk than a bounded residual, and
  the standing constraint is PoC-minimal. **Named explicitly so it is not discovered later: when the
  gate FAILS, the residual holds the record-bearing blob being refused.** That is not an escalation —
  the blob is in the index either way, which is the thing being refused — but it is stated.
- **A LISTED PATH WITH NO MATERIALISED BLOB IS FATAL IN STAGED MODE, REGARDLESS OF OWNER — AND
  GITLINKS ARE OUTSIDE THAT DOMAIN** *(r2.32)*. E-10's ownership escape hatch ("another project owns
  it, mark it listed") described a state that **cannot arise legitimately** under the blob reader, so
  it was an escape hatch for what is always a scan defect. *An escape hatch for an impossible state is
  an inert mechanism, and inert mechanisms are read as permission by whoever arrives next* — the
  lesson §12 and §13 both paid for.
  **Recorded with it, because the predicate is owner-blind and the repository has submodules:** a
  gitlink names a **commit, never a blob**, so mode `160000` entries are excluded from materialisation
  *before* the predicate applies, and submodules are **DISCLOSED** in the report as "N not scanned"
  rather than dropped. Measured: **six** gitlink entries here, including `projects/aviary-biosim`.
  Six repositories silently unscanned inside a confident "798 tracked" header would be this guard's
  own failure mode. The mutant that stops excluding `160000` dies on a test.
  **The carried refactor's REASON TO EXIST, written down so nobody deletes it as unmotivated:** the
  listing and the materialisation are **two `ls-files` calls an instant apart**, and threading one
  enumeration through both is what closes that race. The fatal predicate makes the race *non-silent*;
  it does not close it. The refactor is deferred because `_tracked_listing` is monkeypatched with a
  one-arg lambda in ~40 tests — a deliberate cost decision, not an oversight.
- **THE EXCLUSION SET IS NOT WIDENED FOR COORDINATION FILES** *(r2.31)*. `workstreams/**/plan/**`
  stays **in scope**. Excluding the coordination files that record the guard's own decisions is the
  same hole as excluding the test file that tests the scan, ruled against one revision earlier — and
  the gate would then be blind to exactly the surface where its rulings are written down.
  **The fix is not to write accession literals into tracked prose in the first place.** Describe the
  *form* ("an all-zeros five-digit body"), never the value.
  **And remembering is demonstrably not enough: the CTO wrote two literals into the approval log while
  recording the ruling that forbids them.** So this is enforced on the **commit path** —
  `plan-gate` / the coordination-commit route — and **not** by adding paths to the guard's exclusion
  set. A rule whose only enforcement is the author's attention has already failed once here.
  **This was the accession half's FIRST LIVE CATCH, and it caught the CTO.** Before §11 the shipped
  command composed three of four halves and would have reported this tree **clean at exit 0** — the
  very exit 0 both parties had been citing as evidence. E6-7 earned itself on coordination content
  written by the person who ruled it.
- **THE TEST FILE IS IN SCOPE, AND ITS ASSEMBLED CONSTANT IS LOAD-BEARING** *(r2.30)*. The guard's
  own test fixture is **not excluded** from the accession scan — deliberately, because *excluding the
  file that tests the scan is a bigger hole than an assembled constant*, and it is the exact shape of
  defect this iteration repeatedly found. Consequently **any literal shape-valid non-synthetic form in
  that file turns the live gate RED**, whatever value it holds. Measured: `is_accession_excluded(<the
  test file>)` → `False`; `REAL_ACCESSION_RE` matches a literal five-digit non-synthetic form → `True`.
  **So the fragment assembly stays.** The *value* was the problem and has been replaced with an
  obviously-unassigned one; the assembly never was.
  **Why this is written down:** the CTO ruled "drop the fragment-assembly and the comment explaining
  it" **without establishing why the assembly existed**, and the agent measured before complying and
  refused the half that was wrong. Anyone tidying this later will have the same instinct. The comment
  now carries **both** reasons, not only the original one.
- **E6-7 IS NOW MET, and the CTO verified it by FALSIFICATION rather than by reading the call site**
  *(r2.29)*. `enforce_record_content` is reached from the shipped command, and disconnecting it kills
  `test_the_shipped_command_fails_on_a_real_accession_in_tracked_content` — a test that names the
  **command**, not the function. The binding is a fixture clean on the other three halves, so exit 2
  can only arrive via the accession half. *The CTO read a call site and called it verified once
  already; reading the code is how the previous claim passed.*
- **E-21 — A CONSUMER TEST THAT ONLY EVER ASSERTS THE HAPPY PATH CANNOT SEE A DISABLED GATE**
  *(r2.42, agent-drafted #303, signed verbatim)*. *Found by rule 4 (#298): disabling
  `enforce_record_content` outright left `test_a_non_pytest_consumer_can_call_it` GREEN, because it
  asserts `"STATUS clean EXIT 0"` and a disabled gate returns exactly that. The contract itself
  remains bound by `test_the_shipped_command_fails_on_a_real_accession_in_tracked_content` (E6-7,
  r2.29, MET and re-corroborated by the same run), so this is a redundant test providing no binding,
  not an unmet obligation.* **Done when:** the non-pytest consumer test runs a fresh interpreter, with
  no pytest imported, against a tree that MUST fail, and asserts the consumer OBSERVES the violation —
  `RecordContentViolation` raised or a non-zero exit, **and** the violation named in the consumer's
  own output. The existing clean-path assertion is KEPT; one direction is half a contract, and
  deleting the happy path to add the sad one would just move the hole. **Verified by:** re-running
  rule 4 in a scratch git worktree and showing `test_record_content_entry_point.py`'s survivors drop
  **2 → 1**, the remaining survivor named as `test_it_RE_IMPLEMENTS_none_of_the_pieces` *[CORRECTED r2.47 (f)5: that test was renamed and the survivor count is now 2 → 0; see E-22 r2.47]* and stated
  as correctly scoped (a negative assertion over source text, a different property, which cannot and
  should not notice a disable). Kill set and exit code per mutant, no pipe; live + retired + reasons
  form.
- **E-22 — THE ACCESSION PATTERN APPLIES A WORD BOUNDARY TO TEXT WHERE AN ESCAPE IS TWO
  CHARACTERS, AND IS THEREFORE FAIL-OPEN** *(r2.43; agent-drafted #332, signed with ONE CTO
  change, marked)*. *`REAL_ACCESSION_RE` is `\bDB(?!9\d{4}\b)\d{5}\b`. The scanner reads SOURCE
  TEXT, where an escaped newline is a backslash plus the letter `n`; a word character before the
  token means `\b` does not hold, the token is not matched, and the guard reports clean. Measured
  with the documented synthetic probes only. The agent's first proposed fix `(?<![A-Za-z0-9])` did
  NOT fix it (the `n` of `\n` is still a letter), and was caught by the CTO's independent
  re-measurement.* **The pattern is ONE constant** — measured: three occurrences, all in
  `drugbank_snapshot.py` (:306 definition, :466 `real_accession_hits`, :501
  `accession_structure_tuples`), both call sites detectors, zero parsers, zero consumers elsewhere,
  so no split is warranted.
  **Done when:** (a) the accession pattern is FAIL-CLOSED — no leading boundary AND no trailing
  digit guard: `DB(?!9\d{4})\d{5}` *(CTO change: the agent's candidate kept `(?![0-9])` and left
  the trailing-digit row open; ruled HIT, because a boundary that can hide a real token is never the
  price. CTO-measured: removing it keeps the synthetic DB9xxxx family excluded in every position
  tested, including six-digit and digit-preceded forms)*; (b) a **regression matrix test** pins,
  with synthetic values ONLY, these rows — **HIT** for the all-zeros value: bare; after a real
  newline; after backslash-`n`, `t`, `r`; after a `\x` hex escape; after a `\u` escape; after a hex
  digit pair; after a letter; after an underscore; after a quote; digit immediately before; digit
  immediately after — **MISS** for the DB9xxxx synthetic: bare; after backslash-`n`; followed by a
  digit; six-digit form; digit immediately before; (c) any false positive the widening creates is
  paid for by an explicit, tested exclusion entry, never by re-narrowing the boundary; (d) the two
  tracked test files carrying accession-shaped tokens in escape-adjacent position are replaced with
  documented synthetic values **first**, in their own commit, preserving what each test tests and
  WITHOUT determining whether any token is assigned (principal's 2026-09-17 precedent, "replace, do
  not investigate"; the principal may override before landing).
  **Verified by:** the matrix test failing on the pre-fix pattern and passing after (red→green
  shown, not asserted); the live guard re-run reporting the count of newly-visible hits (expected
  zero after (d)); and `git worktree list` plus tree digests bracketing the work.
  **Explicitly NOT in scope:** scanning decoded literals rather than source text — considered and
  declined with reason: the defect is the boundary, not the decoding; a decoded scan changes what
  "the bytes a commit carries" means (§12.8) and earns its own clause if wanted.
- **E-22(b) AMENDED — THE MATRIX IS REPLACED BY A DIFFERENTIAL ORACLE AGAINST A SPEC-WRITTEN
  REFERENCE** *(r2.44; agent-drafted #370 after three failed enumerated matrices; signed with ONE
  CTO change, marked; SUPERSEDES E-22 done-condition (b)'s enumerated-row wording. E-22 (a), (c),
  (d) and the pattern itself are unchanged)*. *Three enumerated matrices each pinned the axis the
  last reviewer named and left the unnamed one. Decisive: a 9-way alternation of the matrix's own
  probe bodies passed every test in the file. An enumerated probe set's coverage is its author's
  imagination.*
  **SPEC SENTENCE** *(CTO change: the agent's draft said "exactly five digits, the first of which is
  not `9`". CTO-measured that the shipped pattern matches the first five digits of a six-digit run and
  matches a leading Arabic-Indic nine. Both are fail-closed and correct, but the sentence as drafted
  described neither, and the sentence is the one thing a human checks)*: **an accession is the two
  ASCII characters `DB` (case-sensitive) followed by five characters that are each a Unicode decimal
  digit, the first of which is not the ASCII digit `9`; digits beyond the fifth are not part of the
  match; it is recognised whatever precedes or follows it; scanning is left to right and matches do
  not overlap.** Residual risk: reference and regex share a wrong spec. That is smaller than a wrong
  implementation, and checkable by reading this line.
  **Done when:** (a) a reference scanner implements the spec sentence in plain Python with **no
  regex**, returning match spans for a whole string; (b) the test asserts
  `[m.span() for m in REAL_ACCESSION_RE.finditer(s)] == reference(s)` over whole strings (verdict,
  span, overlap and multiplicity in one assertion); (c) input is GENERATED, not listed. **Axis 1:**
  `DB` + every digit string of length 0..6, exhausted, bare context (default tier, ~~~1.1M strings,
  ~0.8 s measured~~ *[CORRECTED r2.47 (f)1: the figure described the extended tier; the default tier measured 1..5 lengths, 248,111 total; off-by-one fixed in r2.47 (e)]*). **Extended tier: length 0..7, required in every quality gate run and recorded in
  the receipt.** *[r2.47 (e): measured that NO prior gate ran it; now wired as a Step 8 command]* **Axis 2:** every left × right pair from the stated alphabet, crossed with a seeded
  body sample. **Axis 3:** seeded fuzz, **seed printed before the run starts**. The body samples on
  axes 2/3 include non-ASCII decimal digits; (d) `KNOWN_WRONG` is RENAMED as a regression museum,
  documented as inheriting the oracle's coverage and not extending it, and a test asserts the oracle
  **fails** on every entry (rule 3b applied to a test); (e) `test_the_matrix_covers_both_axes` is
  DELETED.
  **Measured before signing (#370):** ~~7,466,645 generated strings~~ *[CORRECTED r2.47 (f)1: reproduced by neither tier; origin not established; in-tree numbers recorded in r2.47]*; the shipped pattern agrees with
  the reference (0 disagreements); all 17 known-wrong patterns are killed, including the
  lookup-table pattern (4,458,001 disagreements), the three trailing-blind survivors, `\d{4}[0-8]`,
  and the `(?![a-z])` and `(?![0-9])` trailing guards (killed behaviourally: on a token followed by a lowercase letter, and on a token followed by a sixth digit).
  **STATED CONTEXT ALPHABET, on BOTH sides** (its incompleteness is a recorded limit): empty, letter,
  digit, underscore, quote, hyphen, dot, comma, colon, paren, space, newline, backslash-`n`/`t`/`r`,
  a `\x` hex escape, a `\u` escape, a hex digit pair. **RECORDED LIMIT:** ~~the token axis is closed;~~ *[RETRACTED r2.47 (f)2: the default tier did not even kill the original defect on axis 1; see r2.47 (b) for what is and is not closed]*
  the context axis is unbounded and covered only as far as this alphabet reaches.
  **SHAPES, NOT VALUES (r2.44 re-sign):** plan, clause and dispatch text describes example tokens by
  SHAPE (e.g. "a token followed by a lowercase letter"), never as contiguous accession-shaped values.
  Concrete values live only in test code, under the assembled-fragment convention
  (`test_record_content_guard.py:70-74`). Dispatches are content-exempt, so a value that looks safe
  there becomes a live-gate failure when it is copied into a non-exempt file. Never pay for an example
  with a ledger exemption of the plan itself.
  **DOCSTRING RULE:** every sentence in a test docstring that asserts a property names the test or
  measurement that establishes it, or the sentence goes.
  **RECORDED NEGATIVES (do not re-argue):** the seeded oracle cannot degenerate; `_failures` runs
  production, so a self-guard ignoring the pattern cannot be written by accident; the span pin
  catches span-shifting mutants; the end-to-end scanner row is kept; the three-state taxonomy cannot
  be collapsed without a test going red.
  **NOT in this clause:** the consumer-contract half (randomised bytes, a constructed clean tree,
  recording doubles, exact `accession_scanned`, the must-match probe at `:107`). It is signed
  separately as r2.45, once its byte-sniff-stub kill is MEASURED.
- **E-22(c) — THE CONSUMER CONTRACT IS BOUND BY A CONSTRUCTED ORACLE, NOT BY THE IMPLEMENTATION'S
  OWN OUTPUT** *(r2.45; agent-drafted #377, the third attempt at this file; signed with ONE CTO
  change to (d), marked)*. *An assertion whose input the implementation chooses is not a binding.
  Substring-matching a renderer's format string cannot tell "the gate computed this" from "something
  printed this", and randomising file NAMES while payloads are constants leaves every cheap byte
  proxy able to separate the classes.*
  **Done when:** (a) collaborators are observed by **recording doubles** (each called exactly once;
  the report equal to the renderer's output unmodified), never by scanning source for forbidden
  substrings, which is evadable by spelling and steers a cheat toward sniffing; (b) the clean
  direction is asserted against a **constructed** tree with exact counts, never the live repository;
  (c) the failing direction randomises **bytes**, carries a second offender class that fails via the
  ACCESSION half, and asserts `set(reported) == set(constructed)` on **both** halves; (d) *(CTO
  change)* payload classes are classified by an **INDEPENDENT REFERENCE readability predicate**,
  written in plain Python from a one-line READABILITY SPEC SENTENCE (the guard's documented decoding
  rule: accepted encodings, BOM handling, size bound), with **no import of production decoding code**,
  and a loud failure if a class comes up empty. A **differential test** asserts that production
  `scan_chunks` agrees with the reference over a generated byte corpus. *The agent's draft classified
  payloads with production `scan_chunks`. The CTO verified that `_classify` imports it, so a mutant
  replacing `scan_chunks` with a NUL/length proxy would reclassify the fixture consistently with
  itself and pass: ground truth routed through the implementation, the defect this clause exists to
  remove, one layer down.* **The readability spec sentence and its measurement arrive as r2.46; the
  gate over this range may not run before r2.46 is signed**; (e) `accession_scanned` is counted in the
  same pass that reads the bytes, carried on **both** result and violation, reported in the
  composition root's own section, and asserted by **exact equality**; (f) the seed is printed
  **before** the run starts.
  **Verified by:** the byte-sniff stub (own-tree shortcut + NUL/length/ASCII proxies) KILLED by all
  three consumer-contract tests, with the kill reasons recorded (#377, measured at `cc5142b`), and,
  for (d), r2.46's measurement: the `scan_chunks`-replaced-by-proxy mutant KILLED by the differential
  test.
  **Recorded:** BOM-less UTF-16/32 is excluded as a decoy (E-24 owns it). A fixture must not encode
  a belief about the decoder; the agent measured that its hand-picked "undecodable" payloads were
  silently readable. A character ALPHABET adjacent in source can trip the live guard just as an
  example token can: shapes-not-values extends to alphabets (assemble them).
- **E-22(d) AMENDED — THE FIXTURE'S READABILITY GROUND TRUTH COMES FROM AN INDEPENDENT REFERENCE,
  NOT FROM THE DECODER** *(r2.46; agent-drafted #379, supersedes r2.45(d); signed with CTO changes,
  marked)*. *r2.45(d) was already corrected once. The draft measured it: with the decoder replaced by
  a byte proxy, the old fixture's classes merely MOVED (from four and four to five and one) and every
  set equality held. The independent reference kills that mutant.*
  **READABILITY SPEC SENTENCE** *(plain byte files only, not parquet/HDF5 datasets. CTO change: the
  draft said "UTF-16 if BOM; failing that as UTF-8", which reads as a fallback. The CTO read
  `guards/decoding.py::_decode_text` and found a BOM-prefixed file that fails UTF-16 is NOT text,
  with no fallback. The two numbers are stated here because the module documents them only as "a low
  printable ratio" and a code constant)*: **a plain file is READABLE TEXT when it is at most 256 MiB
  on disk and EITHER its bytes begin with a UTF-16 byte-order mark (either byte order) and decode as
  UTF-16, in which case there is no other route: a BOM-prefixed file that fails UTF-16 is not text;
  OR they do not begin with one and decode as UTF-8 ~~(with or without a UTF-8 BOM)~~ *[REMOVED r2.47 (f)3: a UTF-8 BOM is itself valid UTF-8, so a second attempt is unreachable, measured 0 disagreements over 5,018 inputs; do not re-add]*; OR, failing
  UTF-8, they contain no NUL byte and, decoded as latin-1, are non-empty with at least nine tenths of
  their characters printable or tab, carriage return or line feed. Everything else, including any
  file over the ceiling, is not text and is reportable rather than scanned.** This is CURRENT
  behaviour, including BOM-less UTF-16/32, which currently decodes as UTF-8 when the bytes happen to
  be valid UTF-8. **E-24 changes that, and E-24 must update this sentence and the reference in the
  same commit.**
  **Done when:** (a) a reference readability predicate implements the sentence in plain Python,
  importing NO production decoding code; (b) the consumer fixture classifies its payload classes with
  the REFERENCE, failing loudly if a class is empty; (c) a differential test asserts production
  `scan_chunks` agrees with the reference over a generated, seeded byte corpus (seed printed before
  the run), and the corpus MUST include *(CTO change)* the boundary shapes: empty file; BOM followed
  by invalid UTF-16 (odd length, lone surrogate); UTF-8-BOM files; latin-1 exactly at and just below
  the nine-tenths ratio; a NUL in otherwise valid UTF-8; and the size ceiling, exactly at and one byte
  over it (sparse files, so the test stays cheap); (d) `_decode_text`'s docstring is updated to state
  the ratio and cite the ceiling constant, so the documentation owns the numbers the reference
  depends on; (e) E-24 is named as the clause that must change sentence and reference together.
  **Verified by:** the decoder-replaced-by-byte-proxy mutant KILLED by the differential test. The
  disagreement count and corpus size are recorded FROM THE IN-TREE RUN *(CTO change: the draft's
  figures did not reconcile, a 6,016-string corpus against "451 of 3,009"; a signed clause does not
  carry a number that disagrees with itself)*. Production agrees with the reference on the full corpus.
  **Recorded:** the reference's two numbers were read from code constants, not prose. This clause is
  what makes them documented rule, and (d) closes the gap at the source.
- **E-22 r2.47 — DETECTOR AND GATE CORRECTNESS (WI-1)** *(agent-drafted #388 after gate 4 FAILED
  (#386); every done-condition MEASURED in tree before drafting; signed as drafted, including the
  agent's three measured corrections to the CTO's scope)*. *Gate 4's finding: the checks built to
  close "a claim wider than its check" were themselves wider than what they checked: a
  one-character trailing guard beat the oracle; a 5x cut to the ceiling passed the whole suite; a
  signed exit-code ruling was collapsed; the signed corpus figure was unreproducible.*
  **(a) PATTERN PIN over TEXT AND FLAGS.** A test asserts `REAL_ACCESSION_RE.pattern` equals the
  signed pattern string exactly AND `REAL_ACCESSION_RE.flags == re.UNICODE`. *Agent correction:
  an `IGNORECASE` compile has byte-identical `.pattern` and survived both axes. A text-only pin is
  itself a claim wider than its check.* Plus a lowercase-prefix behavioural row. The failure
  message says that changing the detector is a deliberate act touching pin, clause and oracle
  together. The pin makes a change VISIBLE; the differential oracle proves the SIGNED pattern
  meets the spec.
  **(b) CONTEXT AXIS: every single code point**, left and right, one body per side (2,228,224
  strings, 2.1 s, measured; runs unconditionally, no tier), plus the multi-character alphabet.
  Measured: shipped pattern 0 disagreements; the trailing guards that survived the old corpus are
  KILLED, and so is the rejected lookbehind fix. **Still open, written exactly:** multi-character
  contexts outside the stated alphabet. ~~"Closed" is used only for single-code-point contexts.~~ *[CORRECTED r2.47b (1), gate 5 R05: true only around the PROBE body. Single code point around the probe body: CLOSED. Around other bodies: COVERED, NOT CLOSED (a guard sparing one exact body survived both tiers). Context x body: OPEN (exhausting it is about 10^5 x 2.2M)]*
  Prefix case is closed by (a), not by (b).
  **(c) CEILING FROM BELOW.** Three sparse rows: one byte below and exactly at the ceiling are READ;
  one byte over is REPORTED. The constant-equality assertion is legitimate because the reference
  is written from this clause, and its message says so. Measured: the 48 MiB mutant that passed
  the entire suite now fails two rows plus the equality *[PRECISION r2.47b (3): for the CONSTANT form only. A TRUNCATING read survived homogeneous-NUL rows until gate 5 R08 made each row end in the probe token, which only a full read sees]*. **Recorded cost:** the at-ceiling row
  raises peak RSS by about 511 MiB (read_bytes plus decode), documented in the row for
  memory-capped environments. The reference's verdict for that row is derived from the sentence,
  not computed over 256 MiB.
  **(d) E-13 TAXONOMY RESTORED.** No catch on the base class in the composition root.
  Declaration-data-unusable exits 2 with the file named; guard-invariant violations PROPAGATE and
  are never converted; could-not-scan (exit 3) is reserved for scan failure. `accession_scanned`
  is `int | None` and is `None` when the half was never attempted, never 0. Each branch proven on
  a constructed tree.
  **(e) TIERS.** The axis-1 off-by-one is fixed, and the empty body is generated explicitly (the
  bare prefix is present). The extended tier is WIRED as a documented Step 8 command whose
  invocation line is recorded in the receipt. Post-fix corpus sizes are recorded from a run, not
  from arithmetic.
  **(f) SIGNED-TEXT CORRECTIONS**, each marked in place above with strike-through and a pointer,
  never silently edited: (1) the r2.44 corpus figure and tier sizes; (2) the retracted "token axis
  is closed"; (3) the unreachable UTF-8-BOM phrase removed from the r2.46 sentence; (4) the
  non-empty check is an implementation guard (divide-by-zero), not a spec line; (5) E-21's
  Verified-by survivor name and count.
  **(g) RATIO ROWS THAT REACH THE RULE:** invalid-UTF-8, NUL-free latin-1 high-byte rows at, just
  below and just above nine tenths. Measured: they kill the 0.95, 0.99 and 0.50 mutants that the
  old ASCII rows missed *[PRECISION r2.47b (3): the old ROWS missed them; the old FILE still killed all three through `generated_bytes`. Also, per gate 5 R09, no finite row resolution pins a threshold, so the comparison is additionally bound structurally (an AST check for `>=` against the named constant)]*. Production's ratio becomes a NAMED constant, where it is currently an
  inline literal that nothing can reference.
  **Evidence discipline:** before any gate, the bracket command and its digests are written to
  `qgr/evidence/` BEFORE the reviewers start, so compaction cannot lose them.
  **WI-2 (no clause)** is acknowledged as scoped: false docstrings and messages; two literals
  replaced by the documented probe; ~~a collection-count assertion (a suite that collects zero tests
  FAILS)~~ *[CORRECTED r2.47a (#397): pytest EXITS 2 on a collection error, measured; there is no silent
  pass. The premise was an unmeasured consequence that both the agent's verdict and the CTO's scope
  ruling repeated. Replaced by: import the reference by the path the project owns
  (`tests.readability_reference`), which resolves regardless of import mode, from a foreign cwd,
  and if `tests/` ever gains an `__init__.py`]*; the empty-payload recorder; try/finally on sparse files; coverage-line format; a grep
  showing every property claim names an existing test.
- **E-22 r2.47b — CORRECTIONS FROM GATE 5 + (h)** *(gate 5 PASSED after its fix cycle: receipt Hash E
  `8f2d12e`, CTO-verified; the extended tier was run by its wired command and recorded in the receipt).*
  Four passages are corrected IN PLACE above, with markers: (1) r2.47(b)'s "closed" is scoped to the
  probe body; (2) pointers from r2.28's three-state sentence and r2.29's exit-3 sentence to r2.47(d)'s
  propagation; (3) precision on the (c) and (g) measurements. Gate 5's in-gate fixes that change
  meaning: the error for an unusable ledger is rendered BESIDE the scan and never replaces it (R01, a
  regression the build introduced); both SCANNER call sites are driven over generated contexts
  through a no-disk seam, because the pin and the oracle bind only the constant (R06); the ceiling rows
  end in the probe token (R08); there is a code point x body axis (R05); and the ratio comparison is
  bound by an AST check (R09).
  **(h) NEW (pre-existing, found in gate 5):** `errors.py` documents "a container with no reader
  installed" as could-not-scan (exit 3), but `MissingContainerReader` subclasses `RuntimeError`, is
  never translated, and exits 1. **Ruled: the documented behaviour is right** (a container that cannot
  be read IS a scan that was not performed, a repository condition and not a guard defect). Done when
  `MissingContainerReader` is translated to could-not-scan (exit 3) with the file named, proven on a
  constructed tree, and the docstring cites the binding test. Implemented in the E-23 iteration.
- **E-23 — THE STRUCTURE DETECTOR IS FAIL-CLOSED, PROVEN BY A DIFFERENTIAL ORACLE** *(r2.48; agent-drafted
  #404, every figure measured in tree before drafting (harness `qgr/evidence/e23-draft-measure.py`,
  seeded); same design as E-22 from the start; signed with ONE CTO addition, marked)*. `_STRUCTURE_RE`
  is the ONLY control on the exempt ledger files, and its InChIKey half carried a word boundary at both
  ends: the E-22 defect in its last instance.
  **SPEC SENTENCE:** *a STRUCTURE IDENTIFIER is (i) an InChI: the seven ASCII characters `InChI=1`,
  case-sensitive, then optionally `S`, then `/`, then one or more characters none of which is
  whitespace, running to the next whitespace character or the end of the text; or (ii) an InChIKey:
  fourteen ASCII uppercase letters, a hyphen, ten ASCII uppercase letters, a hyphen, and one ASCII
  uppercase letter. Either is recognised whatever precedes or follows it; scanning is left to right,
  (i) is tried before (ii) at each position, and matches do not overlap.*
  **Done when:** (a) the key half loses both boundaries, the InChI half is unchanged, and the pattern
  is PINNED over text AND flags (`re.UNICODE`), with a lowercase-key behavioural row; (b) a reference
  scanner is written from the sentence in plain Python with no regex, with the coincidence of `\s`/`isspace`
  and `[A-Z]`/ASCII uppercase MEASURED over all code points (0 disagreements each, measured); (c)
  generated input, seeded with the seed printed first: a token axis of seeded keys, each with its one-edit
  near-misses, plus InChI prefix variants; the E-22 context alphabet on both sides; every single code
  point around a probe key AND a probe InChI; code point x seeded key; and fuzz (breadth only: it kills
  nothing here, and the clause does not claim it does); (d) the ONE call site,
  `accession_structure_tuples`, driven through the seam; (e) a regression museum, each entry proven
  killed. The swapped-alternation survivor is PROVABLY EQUIVALENT (an InChI's second character is
  lowercase; every key character is uppercase) and is dropped with that reason; (h) (from r2.47b)
  `MissingContainerReader` translates to could-not-scan (exit 3), file named, proven on a constructed
  tree.
  **(i) PROBE PROVENANCE** *(CTO addition: InChIs and InChIKeys are STRUCTURE identifiers, and this
  workstream forbids associating an accession with a structure. The draft did not say where its probe
  structures come from)*: every InChI and InChIKey in tests and harnesses ~~is~~ *[SCOPED r2.48a (#406): in the DETECTOR and GUARD
  tests and harnesses, meaning E-23's own tests, its measurement harness, the record-content guard tests, and any
  test pairing a structure with an accession probe, where only the SHAPE matters. It does NOT reach the
  domain chemistry fixtures (parsing, stereo, adjudication), which parse real chemistry by design and
  carry no accession; nor the sanctioned ledger file. The CTO's original wording was broader than
  intended]* is **invented by construction
  and visibly synthetic**: keys generated from a stated rule (for example, a single repeated letter per
  segment, or a seeded generator whose seed is printed); InChI bodies are chemically meaningless
  placeholder text. **Never copied from any data file, ledger, fixture, dispatch or external source,
  and never checked against any database to see whether it is real.** A comment at each probe
  definition states that it is invented. The same rule governs the committed harness in
  `qgr/evidence/`. The shapes-not-values rule applies to plan and dispatch text for structures as for
  accessions.
  *[AMENDED r2.48b (#412) — agent-drafted sequencing + scope, with two CTO additions.*
  ***(i) SEQUENCING.*** *(i) is applied only AFTER the code-point x InChI-body axis exists, because until
  then the fixtures (i) condemns are the only oracle for the uppercase-body guard, and applying (i) first
  converts a killed mutant into a full-suite survivor with no signal that it has. The axis landed at
  `2400abc`; (i) is unblocked by that commit and by nothing earlier.*
  ***(i) SCOPE — BY THE PROPERTY UNDER TEST, NOT BY FILE.*** *(i) governs a structure value where only its
  SHAPE is under test. Where a test needs real chemistry — canonicalisation, stereo discrimination,
  InChIKey equality — the PubChem-citation rule governs instead and (i) does not reach it; such a value is
  real, cited by CID and retrieval date, and carries no accession outside the documented synthetic range
  and no coined name. **Where both apply, the citation rule governs.** A test that cannot say which of the
  two it needs is a test whose purpose is unclear, and that is the defect to fix first. **The r2.48a file
  list above is ILLUSTRATIVE, not definitional** — that list is what led an agent to a compliant fixture,
  so the property is primary and the list is only an example of it.*
  ***(i) DECLARATION (CTO addition).*** *Every value either rule governs carries an inline marker naming
  which rule governs it. Without one the clause is interpretive: a reader must re-derive the test's purpose
  before applying it, and that is precisely the step that failed in #412. With one, the clause is auditable
  by reading.*
  ***(i) PROBE CORRECTNESS (CTO addition).*** *Any shape count offered in support of a claim under this
  clause MUST exclude the documented synthetic range, and that exclusion belongs in the shared scanning
  tool rather than in each invocation. The #412 near-miss came from a count wider than the claim it was
  used for — the same defect family this whole range exists to close.]*

  **Measured before signing (#404):** tokens 508,004 (old pattern 30,000 disagreements, new 0); context
  alphabet 108,000 (34,500 / 0); every code point x both probes 4,456,448 (267,096 / 0); code point x
  seeded key 2,228,224 (267,096 / 0); museum 17 of 18 killed (the 18th is provably equivalent); live-tree
  ledger tuples 0 old and 0 new, and newly visible pairs 0, so no exclusions are needed. About 21 s per
  oracle pass.
  **RECORDED LIMITS, exact:** single-code-point contexts are CLOSED around the two probes and COVERED,
  NOT CLOSED around other tokens; multi-character contexts outside the alphabet are OPEN; the key space
  is SAMPLED, not exhausted.
  **CLASS SWEEP (re-derived):** all 10 `re.compile` sites in `chipsim/`. Only `_STRUCTURE_RE` carried a
  boundary or a lookbehind; the other 9 are anchored validators, not content detectors. With E-23 the
  `\b`-on-source-text CLASS is closed in this module.
- **E-23 r2.49 — A SMALLER TREE: delete what rejects nothing unique, bind by construction what no corpus
  can see, fix the two ledger defects, make the shape scan a control** *(agent-drafted #445 after gate 7
  FAILED (#442); every done-condition measured in tree before drafting; signed AS DRAFTED, including the
  agent's measured correction to the CTO's scope: the default suite the CTO specified would have left one
  museum entry unrejected, and 38 hand-written non-ASCII-whitespace rows (0.000 s) cover it instead of an
  axis)*. Measured: today 7 axes, 9,585,016 strings, 54.9 s, 0 unrejected; proposed default 652,123
  strings, 7.7 s, 0 unrejected. 94% fewer strings, 86% less time, zero coverage lost.
  **(a)** `_axis_code_point_by_key` and `_axis_code_point_by_inchi_body` are DELETED;
  `_axis_single_code_point` moves to the EXTENDED tier. The unique-rejection table (tokens 4;
  ascii_pairs 2; the three code-point axes 0; contexts/fuzz 0) is recorded here, and a test asserts the
  property: deleting any axis must leave at least one museum entry unrejected, or the clause says why it
  is kept anyway. **(b)** Three clauses no corpus can see are bound by three constructed documents, each
  measured to distinguish its mutant: each (line, accession) pair reported once; no whole-document bound
  (a pair at the end of a 6,333-byte, 402-line document); the FIRST structure in document order (two
  in-window structures at different distances, the earlier one farther). Each mutant joins
  `_CALL_SITE_MUSEUM`. **(c)** The association spec sentence is rewritten FROM THIS CLAUSE, not from the
  production docstring; where the clause was silent, the rule is stated here first: pairs are reported
  once per (line, accession); a document has no size bound; the structure named is the first in document
  order within the window; the window is `_TUPLE_WINDOW`, which every module imports and none restates.
  **(d1)** The ledger reader uses `link_bytes`, never `read_bytes` (§12.8): a dangling link whose target
  string carries a pair is a HIT; a live link is not read through. **(d2)** The exempt ledger is YAML by
  construction, so `ledger_tuple_hits` scans the UNION of the raw lines and the `yaml.safe_load`-decoded
  scalars; a wrapped scalar recovering a key is a HIT. A ledger-specific rendering rule, separate from
  E-24's encoding rule. Both red-then-green. **(e)** `shape_scan` becomes a control or is deleted:
  exact-match placeholder rule; a `could-not-scan` state distinct from clean, and an empty input is
  could-not-scan *[CLARIFIED r2.50b (#504) — read against the r2.50 entry: this sentence binds the SCANNER, which receives
  a string and cannot tell a zero-byte read from a failed one, so given nothing it certifies nothing; the BRACKET, which
  opens the file and knows whether the read succeeded, classifies a tracked file that exists and reads as zero bytes as
  SCANNED-AND-EMPTY (zero shapes, clean, never exit 3) and a file it could not read as could-not-scan (fatal). Both
  directions carry a false-exclusion test: a zero-byte tracked file must NOT fail the gate; an unreadable file MUST.]*; the gate bracket CALLS it and fails on could-not-scan or any unaccounted shape; it
  implements r2.48b scope-by-property so the 37-file unaccounted count reaches 0 by MARKING; a test fails
  on any unmarked shaped value. *[AMENDED r2.50 (#454, #458, #461, #463, #500) — the full-scope guard is DESCOPED BY THE PRINCIPAL under
  the #444 time box (approval-log row 54, applied at row 55, route corrected 2026-09-29 after #492). Requirement 4 read
  "implements r2.48b scope-by-property so the 37-file unaccounted count reaches 0 by MARKING"; measured, that count is
  1,028 shapes across 44 files, of which 87% are structurally unmarkable. It is NARROWED to: the guard ENFORCES the
  in-scope Python and prose sites only — measured 136 shapes in 18 files — and PASSES iff every in-scope site is CLASSIFIED into exactly one accounting bucket (see
  requirement 5 below; a needs-curation site is classified, counted and reported, not marked) AND could-not-scan = 0
  *[r2.50c (#506): 'in-scope unaccounted = 0' is no longer the pass condition — measured, it cannot be reached truthfully]*. The five ruled properties of #454/#455 become PLAN TEXT here rather than deferring to a document
  that does not exist: P1 signed text (the file's own hash equals the recorded plan_hash); P2 signature ledger (the file
  says of itself that it is the approval log); P4 generated output (a generator-written stamp in a STRUCTURAL position —
  a substring match is a measured false exclusion); P5 citation-governed config, judged on the ENCLOSING MAPPING and never
  on the line (measuring P5 by line reported 0 of 123 qualifying; by mapping it is 88 — a checker bug, not a property the
  tree fails). Each is reported with its count every run. P3 (fixture PROVENANCE.md) is MOOT for E-23: no PROVENANCE.md is
  required to close this clause and no retrieval date is invented. Fixtures (19 files, 436 shapes) and non-qualifying
  configs (2 files, 35) are OUT-OF-GUARD-SCOPE — reported with their counts every run and recorded as a STATED LIMITATION
  in the Stage 1 registered report. The sum identity is asserted by a test: total = in-scope accounted + in-scope
  unaccounted + Σ out-of-scope(P_k) + out-of-guard-scope + could-not-scan. Config sites are classified from the UNION of
  the raw lines and the yaml-decoded scalars; a site the decode cannot reach is classified from its line, never dropped
  (measured: 1 such site, borne by a YAML comment). Requirement 5 is DESCOPED TO REPORTING by the principal (r2.50c, #506, AskUserQuestion 2026-09-29, option chosen
  verbatim: "Descope req 5 to reporting; file-level counts; 56 → limitation"): every in-scope site is classified into
  exactly one of four buckets, reported by count and file every run — (W) accounted by a marker on the site's own line or
  within MARKER_WINDOW_LINES lines immediately above it; (F) accounted by a FILE-LEVEL citation header (CID + retrieval
  date in the module docstring or file header), judged on the enclosing file the way P5 is judged on the enclosing
  mapping — the by-line rule was a measured false exclusion (45 sites at the r2.50c measurement) and an inline restatement
  would be a second copy of a claim with nothing checking the two agree; (C) a constructed shape-only probe governed by
  clause (i), classifiable by the agent WITHOUT comparing any constant against an adjacent structure literal or looking
  any identifier up; (N) NEEDS-CURATION — a site with no citation in the file whose status (real chemistry needing a
  citation, or a synthetic value that looks real) can only be decided by the comparison the agent is forbidden to make.
  (N) sites are NEVER marked; they are counted, listed by file in the harness output, recorded as a STATED LIMITATION in
  the Stage 1 registered report next to the out-of-guard-scope count, and carried as the PRINCIPAL'S Stage 2 curation
  item (a curation claim, like the compound roster). The sum identity gains the four buckets: in-scope = W + F + C + N.
  No marker is written on a guess. MARKER_WINDOW_LINES = 2 — one constant,
  defined once, imported everywhere, never restated, with a test that FAILS if a second literal appears (the same
  discipline and value as _TUPLE_WINDOW). EVERY COUNT IN THIS AMENDMENT (1,028 / 44; 136 / 18; 436 / 19; 35 / 2; 88;
  123; 1) is the measurement at the r2.50 sign (2026-09-29, tree as scanned by tests/shape_scan.py) — a dated observation
  recorded so a reader can see what was descoped, NEVER a target: the harness regenerates each of them every run, the
  done-condition is the derived identity above, and a drift from these numbers is reported, not tolerated and not a
  failure in itself (clause (f) governs).]* **(f)** "CLOSED" is struck wherever the clause says COVERED, NOT CLOSED
  (third recurrence); the equivalence proof reads `_STRUCTURE_RE` or is deleted and the survivor carried
  as unproven; the column witness records 2,086 and [2049, 2085] as closed; counts are regenerated by the
  harness, never typed; the strict xfail is parametrised so every break character runs. **(g)** One shared
  `qgr/evidence/bracket.py`, tested once; the per-gate copies are deleted.
  **STOPPING RULE (CTO, #444):** if gate 8 fails on the same family, no patch: a one-page design note, and
  E-23's scope goes to the principal for a time box.
- **E-23 r2.50 — MECHANISMS, NOT REPAIRS: a claim that cannot outrun its check** *(agent-drafted #500 from the
  gate-8 design note §3 after gate 8 FAILED (#461) on the same family; the #444 stopping rule engaged and the principal's
  time box (row 54) applied; signed AS DRAFTED with one CTO addition, marked)*. Gate 8 found the family SIX times in one
  change set and THREE times independently across four reviewers; the sharpest instance was inside the fix written to
  stop it. Patching the instances is instance 47, so r2.50 spends its single revision on the mechanisms that make a claim
  checkable. **(1) DERIVED QUANTIFIERS.** Any test name or message containing *every / any / all / N* is backed by a
  parametrisation whose cardinality is DERIVED from the artefact it quantifies over. The nine break characters were right
  only because the set was enumerated from `str.splitlines()`; the four tails were wrong because the set was
  hand-written. **(2) FALSE-EXCLUSION TESTS.** Every exclusion predicate carries a FALSE-EXCLUSION test as well as a
  false-inclusion test. Three of gate 8's worst findings are exclusions that silently removed real sites; a false
  exclusion reads exactly like a clean result, which is why no differential caught any of them. **(3) RAISE-PROMISES
  PROVEN.** A helper that promises to raise is PROVEN to raise by a property test over regex constructs (counted groups,
  MIN_REPEAT, anchors, lookarounds, SUBPATTERN), not by a hand-maintained list of node types — and `_characters_at` is
  fixed under that test. The hole was in the arm that LOOKED handled. **(4) DERIVATIONS CONSUME THE WHOLE ARTEFACT.** A
  derivation takes the compiled object — pattern AND flags — or asserts the flags it assumes. The equivalence proof reads
  `.pattern` and is blind to `.flags`, 640 lines after the same file states that an IGNORECASE compile has an identical
  `.pattern`. **(5) THE INSTRUMENT IS INSIDE THE SCOPE IT ENFORCES.** `bracket.py` records digests and counts, never
  verbatim foreign stash subjects, untracked filenames or host paths, and runs the production detectors over its OWN
  output before writing; a hit is could-not-write and the gate fails. Gate 7's committed artifact carries a
  perturb-seq-eval stash subject; gate 8's is clean by luck, not by a control. **THE THREE CONVERGENT DEFECTS ARE PINNED
  AS INSTANCES** of the mechanisms above, each with a regression test: the exact-match placeholder rule still accounts an
  alphanumeric tail (all four reviewers) → (2); an EMPTY tracked file is SCANNED-AND-EMPTY, never exit 3, with six
  `.gitkeep` tracked (security, code, me) → (2); the equivalence proof is blind to regex flags (code, me) → (4).
  *[CTO addition, r2.50 sign (#463); corrected r2.50a (#502) — clause (f) forbids typed counts:]* **MARKER SUBTRACTION is the
  closure mechanism for the in-scope shapes** — each is accounted by a marker on its own line or within MARKER_WINDOW_LINES
  above it, per the amended clause (e). The DONE-CONDITION is derived and only derived *[r2.50c]*: every in-scope site is in exactly one of
  W / F / C / N (in_scope_unclassified == 0) AND could_not_scan == 0; N is reported, never marked. The harness regenerates every count every run and reports, beside the pass, the shapes subtracted per
  in-scope file and the out-of-guard-scope total it does not touch, so the descope is visible in the same table that shows
  the pass and any drift from the at-sign measurement is visible rather than tolerated. This is a checkable obligation on
  the harness's OUTPUT and gate 9 holds the build to it. **RETROACTIVITY:** the committed gate-7
  evidence is NOT edited — retroactive edits are the principal's (#463 item 4). It is recorded in the approval log and in
  the Stage 1 limitations as an observed instance of the family; mechanism (5) prevents recurrence. **STOPPING RULE
  (principal's time box, row 54):** gate 9 is the LAST gate on E-23 and runs on the five mechanisms and the four-bucket
  reporting (r2.50c). A gate-9 fail on the same family closes E-23 at the scope it reached — no r2.51 — and the remaining findings go to the Stage 1 limitations, with the counts as regenerated by
  the harness at gate 9, not just the category.
- **The error taxonomy is TWO classes, not three** *(r2.29)*. "**Scan could not be performed**"
  (exit 3) and "**declaration data unusable**" (exit 2) already have different exit semantics and are
  today distinguished only by which call site happens to catch them. A third class for topology buys
  nothing, because **no caller treats a topology failure differently from a decoding one**. The
  deciding evidence is not that `pytest.raises(RuntimeError)` is broad — that is a test defect with a
  test fix — but that `RecordContentScan.__post_init__` raises the same class for an **internal
  invariant violation**, which surfaces as exit 3 *"your checkout could not be scanned"* *[SUPERSEDED r2.47(d), pointer added r2.47b (2): guard-invariant violations now PROPAGATE (exit 1, measured) and are never converted]* for what is
  a programming error inside the guard. The exception lives in a **dependency-free `guards/errors.py`**:
  the previous placement rule — *"the exception belongs with the layer that raises it"* — was
  **post-hoc justification for a cycle constraint**, and `repo.py` raises it 5 times against
  `record_content.py`'s 20.
- **Fix the signatures BEFORE extracting the modules** *(r2.29)*. Splitting a module whose interior
  signatures are wrong **exports the wrong signature**: five public functions still take
  `(root, paths, policy, surface)` — `ScanContext` minus submodules — and the anti-vacuity invariant
  runs on none of them. Order: **signatures and the root/surface binding first**, then `errors.py` and
  `policy.py`, then the report. `policy.py` outranks the original ordering because
  `drugbank_snapshot` imports the **entire ~1100-line guard** to construct a two-field dataclass.
  *Report grouping is WITHDRAWN* — remedies are per-category, two dispositions give a filter rather
  than a grouping, and the real defect was the header count, already fixed.
- **`derived_from` MUST PIN THE DECLARED FILE'S BYTES** *(r2.29, E6-3 substance)*. It currently names
  a source without pinning the declared artifact, so the **form-level ban on a bare path is satisfied
  while E6-3's substance is not** — the claim a reader was promised they could check remains
  uncheckable. This is a clause of the CTO's whose letter was implemented and whose purpose was not.
- **A COMMIT GATE READS THE BYTES IT CERTIFIES** *(r2.28, index-vs-worktree; scheduled §12)*. The guard lists
  `git ls-files -s` — the **index** — and then reads `root/rel` from the **worktree**. Reproduced
  end-to-end in a throwaway repo: index held the payload, disk held clean text, the guard read clean,
  and the commit would have carried the payload. **A gate certifying bytes other than the ones being
  committed is not a gate.** So: when run as a commit gate it reads the **staged blob**
  (`git cat-file` / `git show :path`), never the working file. Divergence is **not** made a refusal —
  that would break ordinary in-progress development, which was the agent's reason for escalating
  rather than fixing, and it was right to escalate.
  **The report may still inspect the worktree, but it must SAY which bytes it read** — the same
  discipline as E6-5, applied to *which copy* rather than *which half*. A reader cannot check a
  verdict without knowing what was verified.
  **Composition note, stated so it is not discovered later:** reading staged blobs means a tracked
  path always HAS content, so **E-10's unresolvable-path handling applies to the worktree-inspection
  mode only**. The two modes have different failure sets and the clause says so rather than leaving
  one to inherit the other's rules.
- **A THREE-STATE CONTRACT ADMITS NO FOURTH STATE** *(r2.28)*. `sha256: null` passed the
  exactly-one-claim check — which tests key PRESENCE, not value — and then raised `KeyError`, exiting
  **1**, outside the ruled clean / files-fail / could-not-scan set. The scan invariant also compares
  **truthiness**, so an `exit_code=1` object constructs and renders. Every path out of the entry point
  lands in one of the three states *[QUALIFIED r2.47(d), pointer added r2.47b (2): every path for a REPOSITORY condition. A guard-invariant violation (a programming error inside the guard) propagates as exit 1 by design and is outside the three-state taxonomy]*, and the type makes the fourth unrepresentable rather than merely
  untested.
- **EVERY INTERPOLATED FIELD IS ESCAPED, not just paths** *(r2.28)*. r2.24 escaped unprintable
  **paths** after a filename drew a fake all-clear. `ScanRow.detail` is interpolated **raw**, and a
  **structurally valid declaration** rendered a forged clean-report line at column 0. Escaping one
  field and not its neighbours is the same error one column over.
  **Why this clause exists as a clause:** the CTO authorised "E6-6/E6-7" in four separate dispatches
  while E6-7 appeared **zero times** in the signed plan — its only record was the phrase *"a combined
  entry point with the FAIL in the API"* in provenance log row 20. The agent stopped rather than
  build to its own reconstruction of the CTO's words across a compaction boundary, which is the
  correct refusal: *an agent asked to implement a clause that does not exist is being asked to
  approve it.* This is the project's own "an invariant that lives only in prose" failure, committed
  by the party that wrote the warning.
- **Two predicates with opposite safe directions MAY NOT SHARE A DEFAULT** *(r2.27)*. `ContentPolicy`
  carried one comment for both: *"both defaults refuse nothing, so a caller who forgets them gets a
  NOISIER gate."* True of `readability_waived`. **False of `content_exempt`** — exempt nothing and the
  double-exemption defect never fires, the declaration **holds**, and the file is **cleared**.
  Measured: the default cleared a file the shipped policy fails. Each predicate states its own safe
  direction and carries its own default, because "fail-closed" is not a property of a dataclass, it
  is a property of each question it answers.
- **A structural error is carried by the HEADER COUNTS, not only by prose** *(r2.27, E-20)*. A broken
  declaration file alone exits 2 while every number a reader checks first reads clean, leaving the
  signal in a paragraph. That is E-13's own rationale — counts must be right where a reader looks
  first — applied to the case E-13 created.
- **`readability_waived` is measured, and removed if it never fires** *(r2.27, E-19)*. As the
  DrugBank predicate defines it, a dispatch message is waived only when it **decodes** — which is
  exactly when it would not have been reported, so the waiver may be inert. Measure it against the
  live tree; if it never fires, **delete it and say why in the clause**. An inert mechanism is worse
  than an absent one because it reads as coverage (rule 13).
- **E-17 — a REQUIRED `ScanContext`, and the renderer split into DATA and PRESENTATION** *(r2.27,
  its own iteration, after E-18)*. `ScanContext(root, paths, policy, surface)` is required everywhere
  and **resolvable nowhere** — no fallback. *What makes state ambient is not aggregation but
  IMPLICIT RESOLUTION*, so a context that cannot resolve itself is the opposite of ambient state, and
  this is the sixth defect in that family. The scan returns an object carrying `exit_code` and typed
  rows; presentation renders it. **The exit code must be assertable without parsing a string** —
  its living only inside the renderer is *why* E-13b happened, since no test could reach it cheaply
  and every defect test therefore asserted on a return value instead.
- **E-18 — `chipsim/guards/decoding.py` and `chipsim/guards/repo.py`** *(r2.27, do FIRST)*. Two pure
  moves that also remove `ingest`'s reach into **three private names** of the guard — a re-coupling of
  exactly what E6-6 split.
- **A production guard may not be a bare `assert`** *(r2.26; enforcement corrected r2.27)*. `python -O` **strips assert
  statements**, so under optimisation such a guard does not weaken — it **vanishes**, and in this
  module a declared readable container would have been cleared in silence. Guards raise the module's
  own error type explicitly; `AssertionError` is a test-shaped exception and must not surface from
  production code. Enforced two ways, because one of them can rot: a test that **parses this module's
  source** and asserts no bare `assert` appears in it, and a test that **starts a child interpreter
  with `-O` and observes the GUARD REFUSING**. *(r2.27: the first implementation did neither — it
  raised an exception it had constructed itself and re-parsed the source with `ast`, which yields
  `Assert` nodes identically under `-O`. A mutant that made the refusal vanish **exactly and only
  under `-O`** passed all three related tests. A test must observe the behaviour, never re-derive
  it.)*
  **For E6-6:** `undecodable_unallowed` reaching into the DrugBank exclusions is the **one
  non-mechanical part** of that extraction. It moves by judgement, not cut-and-paste, and the clause
  says so rather than letting a mechanical move carry it silently.
  **Submodules are NOT scanned from here** *(r2.24, E-12)*. A submodule is a different repository
  with its own gate obligation; scanning it would be the E-03 fiction inverted — gating what we do
  not own. The six are **named in the report** as unscanned, and this is a stated gap, not a covered
  one. *A payload committed inside one is invisible to this report.*
  **Why stated this explicitly:** as first shipped the command passed `project_root()`, so it
  scanned only `projects/lung-on-chipsim/**`, found nothing, and printed *"0 — every tracked file
  was read"* while **23 files had never been read**. The reporting surface built to prevent a false
  clean produced one. `#122` had already ruled this exact defect — *"the accession scan ran
  `git ls-files` at `cwd=PROJECT_ROOT`, so it never saw `workstreams/` or `.claude/` — run it from
  the repo root"* — so this is that ruling rebuilt one clause later, in the fix for the gap it
  describes. CTO-verified by running both roots: `project_root()` → 0, repo root → 23.
  *Scoping a failure is an ownership assignment, so it is a shape decision — rule 10 applied to the
  rule that produced rule 10.*
- **A readable structured container is always READ, never declared** *(r2.21, E6-2)*. Parquet, HDF5
  and `h5ad` are scanned — parquet including its **footer metadata**, HDF5 including string datasets
  and attributes. Only *rendered* artifacts (figures, typeset PDFs) may be declared, and the two
  kinds are named distinctly so a structured container cannot be filed among figures where nobody
  registers it.
  **Why:** a parquet's footer carried accession + coined name + structure while the file scanned as
  `",harmless\n0,1\n"` — present, invisible to both halves, and certified clean by the guard's own
  green tests. Metadata stamping is ordinary; several engines do it by default.
- **The dispatch waiver covers MESSAGES, not bytes** *(r2.21, E6-4)*. `#122 §3` waives
  `.claude/usr/**/dispatches/` because redacting a sent message falsifies the audit trail. That
  reasoning covers **`.md` payloads only**; any other file type under a dispatch directory is **in
  scope**. Proven: a tracked `dispatches/leak.pdf` carrying raw bytes and a real accession was
  double-exempt — undecodable *and* waived — with the suite green.
- **Which half each mechanism enforces is stated, and neither claims the other's** *(r2.21, E6-5)*.
  The repo-wide scan enforces the **accession** half. The r2.20 writer allow-list enforces the
  **name** half. A structure plus a name with no accession is invisible to the scan **by design**,
  not by oversight — an overclaim about what a guard sees is worse than the gap it hides.
- **The repo-wide record-content guard may not skip a file silently** *(r2.20, scope fixed r2.22)*.
  Any file it cannot decode is **listed** — always, repo-wide — and **fails** the gate of the project
  that owns it, per E6-1b, unless it is declared. Listing is the part that may never be skipped;
  failing is the part that is scoped. Parquet is read with pandas and scanned as a frame. Measured at §5: a tracked parquet carrying accession + name +
  InChI returned **no hits**, against a CSV control that did hit. *A skipped file is an unchecked
  file, and "no hits" from a file that was never read is a false clean.*
- **Approval provenance lives in an append-only log** *(r2.15 item 6)*. `plan-approval.md` is
  tool-owned: `plan-gate sign` regenerates it wholesale and preserves nothing below the frontmatter
  (observed **eight** times). `plan/plan-approval-log.md` is append-only — one entry per sign, with
  revision, hash, route (`human-direct` / `standing-delegation` / `principal-directed`), authorising
  rulings and the prior human-direct hash. Every sign appends. **The quality gate fails when the
  newest entry's hash differs from `plan-approval.md`'s `plan_hash`.**

---

## 1 · The three actors

| Actor | Who it is | Produces | When it acts |
|---|---|---|---|
| **CA · Coding agent** | Claude Code (the `lung-on-chipsim` worktree agent) | repository code, schemas, validators, workflows, tests | build time, now |
| **H · Human** | the principal | curated records, ratified constants, sealed splits, licence posture, freezes | build time, and at every gate |
| **XB · Experiment brain** | ChipSim's runtime orchestrator (A&D §2A) | mechanism diffs, journal entries, wet-condition nominations | **after** the spine and evaluator exist |

> **The allocation rule.** A task is **agent-implementable iff its done-condition is a test that
> can fail.** A task is **human-owned if its output is a claim** — something defended in the model
> card, or something whose wrongness no test in the repository would catch. Curation is human
> because a fabricated record passes every schema check ever written. Parsing is agent because a
> broken parser fails loudly.

**The corollary that shapes the code.** Anything XB may edit at runtime — mechanism hypotheses,
priors, panel composition, link functions — must be **configuration, not code**. If XB would have
to write Python to change a mechanism, the architecture is wrong. **This is why T10 resolves the
ABCB1 accession from `barrier_panel.yaml` rather than hard-coding it** (defect 4 / AM-2).

**The anti-pattern this rule prevents.** A coding agent asked to populate `theta_priors.yaml`
will produce fluent, plausible values with citation-shaped strings attached. Some of those
citations will not exist. That is fatal here because θ priors are load-bearing for every
downstream claim.

> **Four things a coding agent may never do, at any phase.** (1) Write a number into
> `theta_priors.yaml` or `assumptions.yaml`. (2) Create, edit or extend a curated chip record,
> or the curated compound roster. (3) Modify the frozen evaluator, the split definitions, or the
> sealed allocation after signature. (4) **Run `chipsim panel-seal` against the live
> `configs/barrier_panel.yaml`** — the agent writes the tool, the *human's invocation* writes the
> file, because that file is human-only (CTO ruling, dispatch #21; corrected #27).
>
> **The seal is tamper-evidence, never proof that a human attested (CTO ruling, dispatch #27).**
> An earlier revision of this constraint said "running the seal **is** the act of attestation."
> That was wrong and is retracted. `ratified_panel_sha256` is an **unkeyed digest over public
> content**: it shows the panel has not changed since sealing, and it can never show *who* sealed
> it. The attestation is `ratified_by` plus the human's act — the digest only protects it from
> silent edit afterwards. **Nothing in code, config, CLI help, plan or model card may describe the
> seal as authenticating a human.**
>
> Constraint (4) is therefore a **stated rule with no technical enforcement** — like (1)–(3), and
> more so. The r2.4 hardening (preimage bound to `ratified`/`ratified_by`/`ratified_on` **and the
> panel filename**, fixture panels marked `[FIXTURE]` so they cannot coincide with the live one)
> closes **replay**, demonstrated as a real attack: the fixture panel was byte-identical to the
> live panel, so sealing a fixture — a sanctioned agent action — yielded the valid live seal. It
> does **not** close **forgery**: anything that can write `ratified: true` can compute the digest
> over what it wrote. Real signing (minisign/age/GPG against a pinned human key) is the only option
> that would give (4) technical force, and it is now **decided: minisign, at the M1
> re-ratification** *(r2.15 item 5)* — when the three provisional faces (TFRC, FCGRT, SLCO2B1) are
> re-checked, so the panel is signed **once, settled**, rather than signed now and re-signed weeks
> later against a changed panel. Until that happens the quality gate checks this rule, reviewers
> treat an agent-run seal as a gate failure, and the limitation is stated wherever the ratification
> is claimed — the plan, the run journal's provenance block (T17) and any model card — **carrying
> this sentence verbatim: "digest-sealed, human-ratified, not cryptographically signed."**

## 2 · Phase ownership map (M0–M6)

| Phase | What gets built | CA builds | H owns | XB |
|---|---|---|---|---|
| **M0a** Data spine | ingest, harmonize, identity, barrier panel | all parsers, contracts, tests, n8n ETL workflow | licence ruling, UniProt panel ratification, compound roster, P-gp adjudication | — |
| **M0b** Chip-record curation | **80–100** on-domain records, sealed **three-way** allocation (AM-6 resolved) | the schema, the sealing tool, the hash ledger | **every record, every seal** | — |
| **M0c** Frozen evaluator | splits, metrics, three controls | all of it | **ratifies and signs the freeze** | — |
| **M1** ODE core | solver, θ plumbing, fit routine | solver and fit code | the priors, with citations | — |
| **M2** ADME heads | P1–P3, CV harness | all of it | accepts/rejects the ρ ≥ 0.6 gate | — |
| **M3** Occupancy engine | Boltz-2 wrapper, Hill transform, cache | all of it | panel composition | first diffs proposed here |
| **M4** Readout head | one channel, FiLM conditioning, adversary | all of it | picks the channel; reads adversary result | proposes |
| **M5** Uncertainty stack | L0–L3 as amended | all of it | **pre-registers the two P-gp groups before any coverage is computed** | proposes |
| **M6** Acquisition | BALD, diversity, replay harness | all of it | releases sealed records on schedule | proposes and ranks |

## 3 · The DrugBank ruling

**Decision.** Use **dhimmel/drugbank** — a public snapshot of **DrugBank 4.2, downloaded
2015-03-19**, archived at `doi:10.5281/zenodo.45579`, redistributed as derived TSVs under
**CC BY-NC 4.0** (original repo content CC0 1.0). Take **compound identity and
drug→transporter/carrier edges only. Never affinities.**

**What the snapshot gives:** `data/drugbank.tsv` (identity, approved-status filter) ·
`data/drugbank-slim.tsv` (approved small molecules → **the candidate pool**, *not* the PoC set —
see below) · `data/proteins.tsv` (drug→protein edges categorised target/enzyme/**transporter**/
**carrier** — *the barrier panel layer, the reason to use this at all*) · `data/pubchem-mapping.tsv`
· `data/mapping.tsv.gz` (UniChem → 30 resources).

> **Candidate pool ≠ PoC compound set.** `drugbank-slim.tsv` is an automatic approved-small-molecule
> filter of order 10³ rows. The **PoC compound set is the 20–40 hand-curated lung-relevant compounds
> of PVR §4 / CONTEXT.md**, and it is produced by **T18 (H)**, never by a filter. Conflating the two
> made T13's done-condition uncheckable and mis-estimated T14's human cost by ~50×. (Defect 3.)

**Not fetched in slice 1:** `mapping.tsv.gz` and `pubchem-mapping.tsv` are consumed by no task
here; they arrive with the ChEMBL plan. `SNAPSHOT_FILES` fetches three files, not four. (Minor note D.)

**What it does not give:** no binding affinities (those come from ChEMBL/BindingDB/Papyrus),
no approvals after 2015, no current transporter annotations.

**Staleness ruling.** DrugBank 4.2 is eleven years behind 5.1.22. Acceptable **here and only
here** because the PoC compound set is well-characterised reference compounds whose transporter
annotations are stable. The snapshot **cannot support any coverage claim** — the model card must
say **DrugBank 4.2 (2015-03-19 snapshot)** everywhere it says DrugBank.

> **🚨 The collision nobody would notice until M5.** The uncertainty stack conditions Mondrian
> coverage on **P-gp substrate status** — the pre-registered grouping variable the calibration
> veto fires on. If that label is derived from a 2015 snapshot by a script, **a stale annotation
> silently redefines the groups the entire coverage claim is conditioned on**, and a coverage
> failure will look like miscalibration when it is actually mislabelling. Three mandatory
> consequences: the label is derived **three-way (yes / no / unknown)**; absence of an edge is
> **never** read as "not a substrate"; every group assignment for the PoC compound set is
> **adjudicated by H against current literature** before pre-registration (~20–40 judgements).

---

## 4 · Execution order

Scaffold first, then provenance, then data. **T2 precedes T1** (T1 records the hash T2 resolves —
defect 16). The fetch is an explicit task (T4a), not an assumption (defect 8).

| Phase | Tasks | Gate |
|---|---|---|
| **P0 · Scaffold** | S1 → S2 → S3 → S4 → S5 → S6 → S7 → S8 → S9 → S10 → S11 | `pip install -e . && pytest --collect-only` exits 0 |
| **P1 · Provenance & fetch** | T2(H) → T1(H) → T3 → T4a → T4 → T11 | provenance tests green against fixtures |
| **P2 · Parse & identity** | T5 → T5b → T5a → T6 | compound frame persists with canonical InChIKey |
| **P3 · Barrier panel** | T7 → T19 → T8(H) → T9 | panel join non-empty against a ratified fixture |
| **P4 · P-gp labels** | T10 → T12 → S11a → T18(H) → T13 → T14(H) → T15 | label domain + group-population checks green |
| **P5 · Card & ETL** | T17 → T16 | provenance block renders; workflow JSON validates |

**T4a precedes T4** — `dvc add` has nothing to track until the fetch has run.
**S11a precedes T18** — the roster validator must exist before the human fills the roster, so a
malformed entry fails immediately rather than after 45 minutes of curation.

---

## 5 · Scaffold tasks — S1–S11 (CA, run before everything)

> **Why these exist.** Ten of the seventeen original tasks wrote under directories that no task
> created, and four required tools were never installed or configured. Verified on the branch:
> `projects/lung-on-chipsim/` contains only `CONTEXT.md`, `.aiadlc-agent` and `.claude/`. S-ids are
> used so every original T-id stays stable for SYN-271.

### S1 · Create the package skeleton — **CA · 4 min**
- **Files:** `chipsim/__init__.py` (new) and `__init__.py` under `ingest/ harmonize/ encoders/ heads/ transport/ occupancy/ surface/ uncertainty/ eval/ acquire/` (new), per A&D §4.4 + AM-4
- **Done when** `python -c "import chipsim, chipsim.ingest, chipsim.harmonize, chipsim.eval"` exits 0 from the project root, and exits non-zero if any `__init__.py` is removed.

### S2 · Write `pyproject.toml` with the full dependency set — **CA · 5 min**
**`pyarrow` is included because T5a/T15 write parquet and the original Tech Stack omitted a parquet
engine (defect 26); its version is pinned because parquet bytes are not stable across versions
(defect 27).**
- **Files:** `pyproject.toml` (new)
- **Interfaces:** `requires-python = ">=3.11,<3.13"`; dependencies `pandas`, `pyarrow==<pinned>`,
  `PyYAML`, `requests`, `rdkit`; dev group `pytest`, `pytest-cov`, `ruff`, `dvc`
- **Done when** `pip install -e .` succeeds and `python -c "import pandas, pyarrow, yaml, requests, rdkit"` exits 0.

### S3 · Configure pytest — **CA · 2 min**
- **Files:** `pyproject.toml` (edit: `[tool.pytest.ini_options]`, `testpaths = ["tests"]`, markers `network`, `integration`)
- **Done when** `pytest --collect-only` exits 0 from the project root, **and** a test asserts against the
  *parsed* config that `[tool.pytest.ini_options].testpaths == ["tests"]` and that both markers are
  registered. **(CTO ruling E-2.)** The r2 wording — "exits non-zero if `testpaths` is removed" — was
  false as written and could never fail: pytest's default `norecursedirs` already skips `.venv`, so
  collection still exits 0 with `testpaths` absent. Asserting on the parsed config tests the real thing.

### S4 · Create the test package and the day-one modules — **CA · 4 min**
A&D §4.4 requires the three day-one tests. **`test_provenance.py` is a new file, distinct from
`test_contracts.py`** — §4.4 reserves `test_contracts.py` for the §1.2 *data*-contract test, and
T11's provenance checks are a different kind (defect 29).
- **Files:** `tests/conftest.py` (new, `project_root` + fixture loaders) · `tests/test_provenance.py` · `tests/test_contracts.py` · `tests/test_leakage.py` · `tests/test_monotonicity.py` (new). **Each skip names its own blocker — CTO ruling E-3:**
  `test_leakage.py` carries `pytest.mark.skip(reason="M0 slice 3 — splits not yet built")`;
  `test_monotonicity.py` carries `pytest.mark.skip(reason="M1 ODE solver not yet built")`. Monotonicity
  waits on the **M1 ODE solver**, not on slice-3 splits — a skip reason that misnames its own blocker
  sends the next reader to the wrong milestone.
- **Done when** `pytest --collect-only` discovers all four modules and `conftest.py`'s fixtures resolve.

### S5 · Create the committed test fixtures — **CA · 5 min**
These make every human-gated CA done-condition evaluable (Global Constraints / defect 33). They are
**fixtures, not simulated human artifacts** — they live under `tests/`, never under `configs/` or
`data/`, and no pipeline path reads them.
- **Files:** `tests/fixtures/barrier_panel_ratified.yaml` · `tests/fixtures/barrier_panel_unratified.yaml` · `tests/fixtures/provenance.yaml` · `tests/fixtures/pgp_adjudication_filled.csv` · `tests/fixtures/pgp_adjudication_blank.csv` · `tests/fixtures/poc_compounds.yaml` (new)
- **Done when** every fixture parses, and `test_fixtures_are_not_configs` asserts no fixture path is referenced outside `tests/`.

### S6 · Create `configs/` — **CA · 2 min**
Only the non-biological file is written. `theta_priors.yaml` and `assumptions.yaml` are
**deliberately absent** — H-owned, no agent may create them.
- **Files:** `configs/env.yaml` (new) · `configs/.gitkeep`
- **Done when** `configs/env.yaml` parses as YAML, and `configs/theta_priors.yaml` and `configs/assumptions.yaml` do **not** exist.

### S7 · Create the data tree and the project `.gitignore` — **CA · 3 min**
The ignore rule must **not** swallow the `.dvc` pointer files, which are the one thing that must be
committed (defect 10c).
- **Files:** `data/raw/.gitkeep` · `data/interim/.gitkeep` · `data/processed/.gitkeep` · `.gitignore` (**new** — per AM-4 this is `projects/lung-on-chipsim/.gitignore`, which did not exist) containing `data/raw/*`, `data/interim/*`, `data/processed/*`, plus `!*.dvc`, `!.gitkeep`, `!data/processed/*.sha256`
- **Done when** the probe set below passes. **A top-level-only probe is not a probe of this rule (CTO
  ruling E-4)** — `data/raw/*` excludes the *directory* `data/raw/drugbank/`, and **git cannot re-include
  a file beneath an excluded directory**: negations below an excluded directory are inert. The r2 probes
  passed against a `.gitignore` that silently ignored T1/T2's human artifacts and T4's done-condition (d).
  So the probes MUST assert on **nested** paths explicitly:
  - `git check-ignore -q data/raw/probe.tsv` exits **0** (bulk data ignored)
  - `git check-ignore -q data/raw/drugbank/probe.tsv` exits **0** (nested bulk data ignored)
  - each of these exits **1** (tracked — must NOT be ignored):
    `data/raw/drugbank/provenance.yaml`, `data/raw/drugbank/PROVENANCE.md`,
    `data/raw/drugbank/SHA256SUMS.json`, and each `data/raw/drugbank/{drugbank,drugbank-slim,proteins}.tsv.dvc` (r2.11)

### S8 · Initialize DVC — **CA · 3 min**
`dvc init --subdir` is required because the project root is a subdirectory of an existing git repo
(defect 10b). Without this, T4's done-condition is unfalsifiable.
- **Files:** `.dvc/config` (new, generated) · `.dvcignore`
- **Done when** `.dvc/config` exists **and** `dvc status` exits 0.

### S9 · Configure a DVC remote — **CA · 2 min**
Nothing in r1 configured storage, so `dvc pull` could never succeed (defect 11).

**The remote MUST live at an absolute path OUTSIDE every git tree. CTO ruling E-5 — this is a
data-loss fix, not a preference. Do not "simplify" it back inside the tree.**

- **Files:** `.dvc/config` (edit, committed) — declares the remote **by name only, with no url**.
  `.dvc/config.local` (**gitignored, never committed**) carries the url, which each contributor sets
  to their own absolute path outside every git tree:
  ```
  # .dvc/config.local — local only, never committed
  ['remote "local"']
      url = <absolute path outside every git tree, e.g. ~/.aiadlc/biofm/dvc-storage expanded>
  ```
  **Do not commit a literal home path (CTO ruling, dispatch #18 — refines E-5).** E-5 was right that
  the store must be absolute and external; committing *this machine's* path was the wrong mechanism.
  It ships an account name and home layout to a public remote, and — worse — DVC's local remote
  **creates the directory on push**, so every other contributor and CI gets a silent empty success on
  push and nothing on pull, instead of a clean "no remote configured" error. That is the same
  silent-success failure class E-5 exists to prevent, reintroduced one layer over.
- **Why (do not remove this rationale):**
  1. **A relative url destroys the data.** r2 specified `../../../.dvc-storage`, which from
     `projects/lung-on-chipsim/.dvc/` resolves to **`worktrees/lung-on-chipsim/.dvc-storage`** — *inside*
     the worktree. `git worktree remove` is a routine operation here (there is a `/worktree-delete`
     skill), so as specified **a routine cleanup destroys the only copy of the snapshot.**
  2. **Absolute, not `~`-relative.** DVC does not reliably expand `~` in `.dvc/config`.
  3. **Beside the ISCP database**, following the convention already in `agency.yaml`
     (`iscp.db_path_template: ~/.aiadlc/{repo}/iscp.db`). It survives worktree removal, survives branch
     switches, and is outside every git tree so it can never be vendored.
  4. **It needs no `.gitignore` entry at all**, and it retires F-02 as a live risk rather than merely
     ignoring it: extensionless md5 blobs cannot be `git add -A`'d if they are not under the repo.
     Keep the F-02 ignore rule anyway as belt-and-braces, and keep the widened
     `test_drugbank_not_vendored` — matching only `*.tsv` would never have caught blob-form bytes.
- **Done when** `dvc remote list` names a default remote whose url is that absolute external path, the
  configured url resolves outside the repository root, and `dvc push` followed by `dvc pull` on a clean
  cache round-trips the snapshot.

### S10 · Create `orchestration/n8n/` — **CA · 1 min**
- **Files:** `orchestration/n8n/.gitkeep` (new)
- **Done when** the directory exists and is tracked by git.

### S11 · Create the module files every later task marks "(edit)" — **CA · 3 min**
T3/T5/T6 edit `drugbank_snapshot.py`; T10 edits `pgp_label.py`; T5b edits `ids.py`; T17 edits the
provenance block. None existed (defects 12, 13).
- **Files:** `chipsim/ingest/drugbank_snapshot.py` · `chipsim/harmonize/ids.py` · `chipsim/harmonize/pgp_label.py` · `chipsim/harmonize/contracts.py` · `chipsim/eval/provenance_block.py` (all new, empty or stub)
- **Done when** all five import cleanly.

---

## 6 · Tasks — M0 slice 1

### T2 · Pin the snapshot commit — **H · 2 min** *(now first — defect 16)*
Resolve the current head of the repository's `gh-pages` branch to a full 40-character SHA. The
commit observed during the §1.4 access audit was `3e87872db5fca5ac427ce27464ab945c0ceb4ec6`.
Record **both** values: if you replace it, you must say why (defect 17).
- **Interfaces** — written into `data/raw/drugbank/provenance.yaml`:
  ```yaml
  source_commit:            <40-hex, the one you resolved>
  audited_commit:           3e87872db5fca5ac427ce27464ab945c0ceb4ec6
  commit_change_rationale:  ""   # REQUIRED non-empty if source_commit != audited_commit
  ```
- **Done when** `source_commit` matches `^[0-9a-f]{40}$` and, if it differs from `audited_commit`, `commit_change_rationale` is non-empty.

### T1 · Ratify the licence posture — **H · 5 min**
Read the two licence statements (CC BY-NC 4.0 on the derived data; DrugBank ToS) and write the
decision in your own words. **The artifact is split in two** (defect 15): a structured YAML that
T11 can parse, and your prose.
- **Files:** `data/raw/drugbank/provenance.yaml` (edit — structured) · `data/raw/drugbank/PROVENANCE.md` (new, hand-written prose)

> **r2.15 — PROVENANCE.md stays human-authored; a proposal to let the CTO draft it was put and
> declined.** The 2026-09-15 grill draft (item 1) proposed the T8 pattern — CTO drafts, principal
> ratifies and seals — reasoning that the licence *decision* was already the principal's (1B1
> 2026-09-09, recorded verbatim in `provenance.yaml`'s `non_commercial_commitment`), so the prose
> would restate a decided claim rather than make one. **The principal was shown both readings
> explicitly and chose human-only.** "Hand-written prose" above is therefore unchanged, a
> CTO-drafted `PROVENANCE.draft.md` committed at `5147281` was removed at `6557487`, and **no agent
> may draft this file**. The argument is recorded rather than discarded so that a future reader sees
> it was considered, not overlooked.
- **Interfaces** — `provenance.yaml` must carry, in addition to T2's three keys:
  ```yaml
  source_repo:      https://github.com/dhimmel/drugbank
  upstream_version: "4.2"          # structured, NOT a display string — defect 14
  snapshot_date:    "2015-03-19"
  licence:          CC BY-NC 4.0 (DrugBank content and derivatives)
  attribution:                      # a list, so it parses
    - Wishart et al., Nucleic Acids Res (2014), doi:10.1093/nar/gkt1068
    - Himmelstein et al., Zenodo, doi:10.5281/zenodo.45579
    - Licence discussion: doi:10.15363/thinklab.d213
  non_commercial_commitment: "<one sentence you would defend>"
  ```
- **Done when** `yaml.safe_load` yields the contract in the form ratified by **CTO ruling E-1**:
  **nine keys present; eight always non-empty; `commit_change_rationale` non-empty IFF
  `source_commit != audited_commit`.** `attribution` has three entries, and `PROVENANCE.md` exists.
  The r2 wording ("all eight keys non-empty") contradicted T2, which *requires*
  `commit_change_rationale` to be empty when `source_commit == audited_commit`. This conditional is
  strictly **more** checkable than "all non-empty", because it makes the *empty* case an assertion
  rather than an exemption.

### T3 · Write the fetch script — **CA · 5 min**
- **Files:** `chipsim/ingest/drugbank_snapshot.py` (edit)
- **Interfaces:**
  ```python
  SNAPSHOT_FILES = ("drugbank.tsv", "drugbank-slim.tsv", "proteins.tsv")

  def fetch_snapshot(dest: Path, commit: str) -> dict[str, str]:
      """Download SNAPSHOT_FILES from raw.githubusercontent at `commit`, writing each
      to `dest/<basename>` — FLAT, no nested data/ level (defect 7).
      Returns {basename: sha256}.
      Also writes `dest/SHA256SUMS.json` (git-tracked, NOT DVC):
        {"source_commit": <40-hex>, "fetched_utc": <iso8601>, "files": {<basename>: <sha256>}}
      Raises ValueError unless `commit` matches ^[0-9a-f]{40}$.
      Never writes outside `dest`; leaves `dest` untouched when it raises.
      """
  ```
- **Done when** it raises `ValueError` on a 39-char string **and** on a 40-char non-hex string (defect 32), leaves `dest` empty in both cases, and on a valid commit returns three hashes with `SHA256SUMS.json` matching the files on disk.

### T4a · Run the pinned fetch — **CA · 2 min** *(new — defect 8)*
r1 had no task that actually pulled the data, yet T4–T10 all presumed it existed. It runs **before**
T4, because `dvc add` has nothing to track until the snapshot is on disk.
- **Interfaces:** `python -m chipsim.ingest.drugbank_snapshot --dest data/raw/drugbank --commit <source_commit from provenance.yaml>`
- **Done when** the three TSVs exist under `data/raw/drugbank/` and their recomputed sha256s equal `SHA256SUMS.json`.
- **Blocked-by:** T2 (the commit). Until T2 lands, the *unit* done-conditions of T3 run against fixtures; this task is reported blocked.

### T4 · Track the snapshot in DVC, not git — **CA · 4 min**
- **Files:** `data/raw/drugbank/{drugbank,drugbank-slim,proteins}.tsv.dvc` (three new pointers, one `dvc add` per TSV)
- **Done when** all four hold (defects 5, 10; (b)/(c) amended r2.11):
  (a) `git status --porcelain` lists no `.tsv`;
  (b) **each** of the three `.tsv.dvc` pointers exists, **is tracked by git**, parses as YAML with a non-empty `outs[0].md5`;
  (c) `dvc status` on all three pointers reports up-to-date;
  (d) `SHA256SUMS.json` is tracked by git.

> **r2.11 — a directory pointer cannot exist here; three file pointers can.** r2 specified one
> `data/raw/drugbank.dvc` over the whole directory. DVC refuses to track a directory while any file
> inside it is tracked by git (`dvc/output.py:670`, both scmrepo backends) — and this directory
> *deliberately* holds three git-tracked files: `provenance.yaml`, `PROVENANCE.md`,
> `SHA256SUMS.json`. So (b)/(c) as signed were **unsatisfiable**, not merely awkward. The CTO first
> ruled that no signed condition needed amending; the worktree agent disproved that from source.
> **Principal ruling 2026-09-15: one pointer per TSV.** (a) and (d) are unchanged; S7's ignore
> probe and T11's pointer test follow the new paths.

### T11 · Write the provenance contract tests — **CA · 5 min**
Lives in `tests/test_provenance.py`, **not** `tests/test_contracts.py` — §4.4 reserves the latter
for the §1.2 *data*-contract test, which arrives with the ChEMBL plan (defect 29).
- **Files:** `tests/test_provenance.py` (edit)
- **Interfaces:**
  ```python
  def test_provenance_complete():
      """provenance.yaml parses and carries all NINE keys present, with the eight
      unconditional keys non-empty; source_commit matches ^[0-9a-f]{40}$;
      attribution has three entries. (CTO ruling E-1.)"""

  def test_provenance_commit_substitution_is_justified():
      """The conditional contract, ratified E-1: commit_change_rationale is
      non-empty IFF source_commit != audited_commit. Both directions assert —
      a silent snapshot swap fails (rationale missing), AND a rationale offered
      for an unchanged commit fails too (defect 17)."""

  def test_snapshot_hashes_match_manifest():
      """Recomputed sha256 of each fetched file equals SHA256SUMS.json (defect 2).
      Fails if any fetched file is mutated after fetch."""

  def test_drugbank_not_vendored():
      """`git ls-files` matches no .tsv under data/raw/ — recursive, so a nested
      layout cannot hide one (defect 7)."""

  def test_dvc_pointer_is_tracked():
      """Each of the three data/raw/drugbank/*.tsv.dvc pointers IS tracked by git
      (r2.11) — the blanket ignore must not swallow the files that make the
      snapshot recoverable (defect 10c)."""
  ```
- **Done when** all five pass against `tests/fixtures/provenance.yaml`, `test_drugbank_not_vendored` fails if you `git add -f` a TSV, and `test_dvc_pointer_is_tracked` fails if **any one** of the three pointers is untracked.
- **Blocked-by:** T1/T2 for the *live* provenance file; the unit conditions above run against the fixture.
- **Sign-off note (CTO ruling E-1):** T11 is **unblocked for sign-off against fixtures** even though
  T1/T2's real artifacts are absent, because the conditional contract is testable in both directions
  from fixtures alone.

### T5 · Parse the compound table — **CA · 5 min**
- **Files:** `chipsim/ingest/drugbank_snapshot.py` (edit)
- **Interfaces:**
  ```python
  def load_compounds(raw_dir: Path) -> pd.DataFrame:
      """`raw_dir` contains drugbank.tsv, drugbank-slim.tsv, proteins.tsv at its TOP LEVEL.
      Columns: drugbank_id, name, type, groups (list[str]),
      atc_codes (list[str]), inchi, inchikey.
      Drops rows with no InChIKey. Does not canonicalise — that is T5b / harmonize/ids.py.
      """
  ```
- **Done when** `df.inchikey.notna().all()`, `groups` is a list rather than a pipe-joined string, **and `len(df) > 1000`** — the row-count floor is what makes the condition non-vacuous on an empty frame (defect 9).

### T5b · Canonicalize compound identity — **CA · 5 min** *(new — defect 31)*
A&D §1.2 requires "canonical InChIKey from RDKit after salt stripping, neutralization, tautomer
canonicalization. **Never join on name or raw SMILES.**" r1 declared RDKit in the stack and used it
nowhere, so the plan's own Goal — "through the compound-identity layer" — was unmet while all 17
done-conditions passed.
- **Files:** `chipsim/harmonize/ids.py` (edit)
- **Interfaces:**
  ```python
  def canonical_inchikey(inchi: str) -> str:
      """RDKit: salt strip -> neutralize -> tautomer canonicalize -> InChIKey."""

  def add_canonical_identity(compounds: pd.DataFrame) -> pd.DataFrame:
      """Adds `canonical_inchikey`. Raises if any value is null."""
  ```
  **T10, T13 and T15 index on `canonical_inchikey`, not the raw snapshot key.**
- **Done when** a known salt / free-base pair collapses to one `canonical_inchikey`, the column is non-null on every row, and a raw-vs-canonical disagreement count is reported. **Plus (r2.12, corrected r2.13, extended r2.14):**
  (i) the benzimidazole 1H/3H tautomers stay merged, and the malate pair's split is asserted by a named accepted-loss test;
  (ii) **relative-stereo handling:** a source InChI declaring `/s2` is keyed with its **tetrahedral stereo stripped** (`/b` retained — double-bond geometry is always absolute), `stereo_is_relative` is emitted as a `bool` column by both `add_canonical_identity` paths, **is listed in `PERSISTED_COMPOUND_COLUMNS`** so T5a cannot drop it, and `MERGE_STAGES` carries a `relative-stereo` stage immediately after `parse`;
  (iii) the threonine test pins its members **by InChIKey, not by name** — the stereo-free threonine key (PubChem CID 205) and `AYFVYJQAPQTCCC-PWNYCUMCSA-N` (D-allothreonine, CID 90624).

> **r2.14 — the source's own stereo flag, and why the condition now names keys instead of compounds.**
> An InChI's `/s` layer declares whether its sp3 stereo is absolute (`/s1`) or **relative** (`/s2`).
> The snapshot holds **42 `/s2` strings and no `/s3`**, and the pipeline keyed **all 42 as absolute**
> — RDKit reads `/s2` as `/m0`. Of the 31 with comparable centre sets, **13 received the mirror
> image**, including single-enantiomer drugs (dextropropoxyphene, dexetimide, dolutegravir, ethinyl
> estradiol, mestranol). Nothing errored: this is the key T10/T13/T15 join on. **Principal ruling
> 2026-09-15: assert nothing the source does not — strip tetrahedral stereo for `/s2` input and flag
> it.** Accepted consequence, stated rather than buried: **esomeprazole now merges with omeprazole**,
> because DrugBank records esomeprazole with relative stereo, so on this snapshot's evidence the
> study cannot distinguish the single S-enantiomer from the racemate. Three relative rows also
> *separate* from absolute rows they had matched by RDKit's arbitrary assignment.
> **The source's D-/L- labels are wrong at scale, measured and then classified.** Of 134 rows whose
> name carries a `D-`/`L-` prefix, 59 resolve against PubChem for both enantiomers. Of those, **11
> are genuine label errors on rows whose stereo is absolute** — D-leucine, D-alanine, D-glutamine,
> D-glutamic acid, D-proline, D-cysteine, D-lysine, D-treitol, D-tyrosine and D-arginine all carry
> **L** structures, and one `L-`-prefixed boronic-acid alanine keys as **D**. The re-key does not
> touch these: they were absolute already, and they key the same before and after. A twelfth
> contradiction, "L-Threonine", **was** an artifact of the old absolute reading of a relative string
> and is fixed by (ii). A thirteenth is unresolved and not counted. A further 75 rows could not be
> resolved either way, so **11 is a floor, not a total**.
> This is why (iii) pins InChIKeys: **a condition that names a compound inherits the source's
> labelling errors, and this source mislabels a substantial fraction of its stereoisomers.** Every
> label-bearing output — worksheet `name`, roster entries, model cards — must be treated as
> unreliable wherever the label disagrees with the key, **and the key is what joins**. The two
> classes must not be conflated: one is a source defect the pipeline can only report, the other was
> a pipeline defect the pipeline has fixed.

> **r2.13 — the snapshot mislabels its *D-Threonine* row, and r2.12 inherited the error.** r2.12's
> condition said "L-/D-threonine". The snapshot row titled *D-Threonine* carries
> `.../t2-,3-/m1/s1` — which is **byte-identical to PubChem's D-allothreonine** (CID 90624,
> `AYFVYJQAPQTCCC-PWNYCUMCSA-N`), while true D-threonine (CID 69435, `AYFVYJQAPQTCCC-STHAYSLISA-N`)
> is `.../t2-,3+/m0/s1` and matches no snapshot row. The row titled *L-Threonine* is also a
> non-standard InChI. So the test exercises **L-threonine vs
> D-allothreonine** — genuinely different stereoisomers, so the guard's behaviour and every measured
> figure stand unchanged; only the naming was wrong. Verified against PubChem PUG REST by the CTO,
> 2026-09-15, after the worktree agent found it. A true L-/D-threonine case needs both structures
> sourced from PubChem and is optional, not required here. **Lesson for done-conditions: a condition
> that names a compound inherits the source's labelling errors unless the label is checked against
> the structure.**

> **r2.16 — accessions removed from this plan (wording only).** The r2.13 note above named two
> DrugBank accessions beside their record titles and structures — the `(accession, name, structure)`
> association the principal's 2026-09-15 record-content re-ruling protects — and one accession sat in
> `plan-approval-log.md` row 11. Found by the worktree agent's repo-wide scan before it built the
> guard test (#131); ruled by the CTO 2026-09-16 under that re-ruling and the standing "no accessions
> in coordination records" rule (#122 §3), which binds the plan too. **Rows are named by their title
> and pinned by InChIKey; the log row is corrected in place with the correction disclosed (the row-12
> precedent), so the guard test carries no exclusion for plan files.** No condition, task or figure
> changes. r2.16 has no principal ruling of its own — a truth-fix under the r2.8/r2.9 precedent,
> disclosed here and in the marker.

> **r2.12 — the stereo guard, and what it costs.** Principal ruling 2026-09-15: tautomer
> canonicalisation must not change stereo. Compare the pre- and post-tautomer InChI's **`/t`, `/m`
> and `/s`** layers only — **`/b` (double-bond geometry) is excluded** — and return the
> **pre-tautomer** key when any of the three changes or vanishes. **Measured on the guard alone,
> before r2.14's relative-stereo re-key** (CTO re-ran it independently): fired on **1,599 of 6,802**
> compounds (23.5%), merge groups **191 → 156**, tautomer-stage groups **48 → 7**, **41 groups
> split, zero new merges**.
>
> **r2.16 — those figures are historical, and this plan stopped restating figures from memory.**
> With the re-key in place the committed report gives **1,576 fired (23.2%), 192 → 154 merge groups,
> 43 split, 0 newly merged** over the same 6,802. The two sets differ because the re-key changes
> which keys exist *before* the guard runs — neither measurement was wrong, but r2.14 and r2.15 both
> presented the earlier set as current after the re-key had landed, and the **worktree agent caught
> stale numbers inside hash-locked text**. **Source of record for every such figure:**
> `workstreams/lung-on-chipsim/reports/2026-09-15-stereo-guard-tms/merge_report.json`, regenerated by
> `python -m chipsim.harmonize.merge_report`. Prose in this plan **cites** it; it does not restate it.
> Of the original 41 (the classification below has **not** been re-run against the post-re-key 43,
> and must not be quoted as though it had):
> **36** clean stereo separations, **2** ambiguous keto/enol pairs whose stereo does not correspond
> between forms, **2** incidental aldose/ketose, and **1 accepted known loss** — the malate tautomer
> pair, whose source forms already differ in skeleton hash. The salt/free-base condition above is
> unaffected: the guard fires on the tautomer step, not the salt-strip step. The first reading of the
> ruling compared four layers including `/b`; that split 3 true-tautomer groups and was refuted by
> per-layer measurement before any code was written. Aldose/ketose merging is a **separate, open**
> scope question and is not decided here.

### T5a · Persist the compound frame — **CA · 3 min** *(new — defect 26)*
- **Interfaces:**
  ```python
  def write_compounds(df: pd.DataFrame, out: Path) -> None:
      """Declared column order and dtypes, sorted by canonical_inchikey.
      pyarrow, version='2.6', compression=None.

      **(r2.20) VALIDATES `out` through the shared record-bearing-writer helper**
      (see Global Constraints) and refuses a destination outside the declared
      untracked roots. This frame is the WORST payload in the project: accession,
      name, InChI and InChIKey on ONE ROW — the complete DrugBank record, not merely
      the (name, structure) association. Until r2.20 it validated its columns and
      never its destination, and `chipsim write --out <any path>` reached it with no
      validation at all; writing into `configs/` was measured at §5. The CLI inherits
      the refusal through this function — it does NOT get a second check of its own,
      because two checks drift and the second becomes the one people trust."""
  ```
- **Files:** `data/processed/drugbank_compounds.parquet` — **not** `compounds.parquet`, which A&D §1
  reserves for the harmonized multi-source S1 artifact `(InChIKey, SMILES, logP, pKa, MW, TPSA)`
  (defect 30)
- **Done when** the parquet round-trips to a frame identical to the input, and `data/processed/drugbank_compounds.sha256` (git-tracked) records its digest.

### T6 · Parse the protein-edge table — **CA · 5 min**
- **Interfaces:**
  ```python
  def load_protein_edges(raw_dir: Path) -> pd.DataFrame:
      """Columns: drugbank_id, uniprot_id, category, organism.
      `category` is one of target, enzyme, transporter, carrier.
      Filters to organism in {'Human', 'Homo sapiens'} — BOTH, deliberately.
      """
  ```
- **Done when** `len(df) > 0`, `set(df.category) == {target, enzyme, transporter, carrier}` (**equality, not subset** — defect 9), and a golden-row assertion holds: a named reference drug with a known ABCB1 transporter edge is present. The golden row is what catches a silent species-filter mismatch that empties the frame.

> **r2.10 — the mismatch was real, and the golden row is why we know.** The spec said
> `organism == 'Homo sapiens'`. The pinned 2015 snapshot says **`Human`: 16,299 rows, and
> exactly zero saying `Homo sapiens`** (verified against the fetched TSV, 2026-09-14). As
> written the loader returned an **empty frame on the only data the study is permitted to
> use** — and every fixture said `Homo sapiens`, so no test could have caught it. **Accept
> both labels**, rather than swapping one for the other: the fixtures are legitimately
> `Homo sapiens`, and silently preferring either would leave the next reader unable to tell
> which vocabulary the code trusts. The class is *a done-condition evaluated against a
> fixture that does not share the real snapshot's vocabulary* — green tests, correct about
> the fixture, wrong about the world.

### T7 · Draft the barrier panel accession list — **CA · 3 min**
`ratified` is a **real, file-level** key — not a comment, not per-entry (defects 1, 18). A wrong
accession silently empties a join and produces an *empty* rather than *wrong* result.
- **Files:** `configs/barrier_panel.yaml` (new)
- **Interfaces:**
  ```yaml
  ratified: false        # real top-level key; H flips it in T8
  ratified_by: ""
  ratified_on: ""
  panel:
    - {symbol: ABCB1,   uniprot: P08183, alias: "P-gp / MDR1",  face: apical}
    - {symbol: ABCG2,   uniprot: Q9UNQ0, alias: "BCRP",         face: apical}
    - {symbol: ABCC1,   uniprot: P33527, alias: "MRP1",         face: basolateral}
    - {symbol: TFRC,    uniprot: P02786, alias: "TfR1",         face: basolateral}   # was apical — see N1 note
    - {symbol: FCGRT,   uniprot: P55899, alias: "FcRn",         face: apical}
    - {symbol: SLC15A1, uniprot: P46059, alias: "PepT1",        face: apical}
    - {symbol: SLCO2B1, uniprot: O94956, alias: "OATP2B1",      face: basolateral}
  ```
- **Done when** `yaml.safe_load(...)["ratified"] is False` (a *parsed boolean*, which the r1 comment form could never satisfy) and every entry carries `symbol`, `uniprot`, `alias`, `face`, **and the file carries a `ratified_panel_sha256` key** (empty until T8 seals it).

> **N1 — TFRC `face` corrected apical → basolateral (CTO ruling, dispatch #18).** r2.2 prescribed
> `apical`. The principal ruled `basolateral` on measured basolateral:apical localization ratios —
> MDCK I ~800:1, MDCK II ~300:1 (Fuller & Simons 1986), Caco-2 ~40:1, HepG2 ~3:1, BeWo ~2:1;
> direction unanimous. **Two caveats travel with it and must not be dropped:** none of those systems
> is airway epithelium, so this is extrapolation across polarized epithelia with airway magnitude
> unmeasured; and the ratio spans ~400×, so at the low end this is a *preference*, not exclusive
> localization. T8 authorizes correcting accessions and deleting entries — it did **not** authorize
> a `face` change, so the live config briefly diverged from the signed plan. This amendment is what
> makes the value authorized; the plan leads the artifact, never the reverse.

### T19 · Write the panel verification script — **CA · 4 min** *(new — defect 19)*
T8's r1 done-condition was pure attestation ("you have personally opened seven UniProt pages"),
leaving the barrier panel's only control unverifiable. This gives T8 a checkable surrogate.
- **Files:** `tests/test_barrier_panel.py` (new, `pytest.mark.network`)
- **Interfaces:** for every entry, assert `rest.uniprot.org/uniprotkb/<acc>.json` resolves, `organism.taxonId == 9606`, and the primary gene name equals the entry's `symbol`.
- **Done when** the test passes against `tests/fixtures/barrier_panel_ratified.yaml` and **fails** when one accession is mutated to a valid-but-wrong human accession.

### T7a · Build the panel seal tool — **CA · 5 min** *(new — CTO ruling, dispatch #21)*
> **AMENDMENT r2.7 (principal, 2026-09-02) — the seal gets its first actual enforcement.**
> `chipsim panel-seal` **must refuse to run without an interactive terminal** (no TTY on stdin →
> exit non-zero, write nothing). A headless agent session has no TTY, so the sanctioned-action path
> that currently yields a valid live seal simply fails. Until now Global Constraint (4) had **zero**
> technical enforcement; this is the first.
> **State the residual limit on the model card and do not overstate it:** the seal proves the file
> is unmodified, never who ratified it, and an agent that deliberately allocates a pty defeats this
> guard. It converts an accident into a deliberate circumvention — that is the honest claim, and it
> is the whole claim. Real signing with a human-held key is a v2 decision, deferred.

T8's attestation step invokes `uv run chipsim panel-seal`, which did not exist as a task. **Placed
before T8 deliberately**, on the S11a-before-T18 precedent and for a sharper reason: the seal is the
**tamper-evidence the human's ratification depends on** — it is *not itself* the attestation
(dispatch #27; this sentence was the **tenth** survivor of that reframe, found 2026-09-14 by a
wrap-aware sweep after line-oriented greps missed it for two weeks). If the tool is missing when the
principal sits down to ratify, T8 cannot be completed at all — the plan would be self-blocking.

- **Files:** `chipsim/harmonize/pgp_label.py` (edit) · `chipsim/pipeline.py` (edit — `panel seal`
  subcommand) · `tests/test_pgp_label.py` (edit)
- **Interfaces:**
  ```python
  def panel_digest(panel: list[dict]) -> str:
      """sha256 over the canonically-serialized panel list."""

  def seal_panel(panel_path: Path) -> str:
      """Write ratified_panel_sha256 and return it.
      Raises if the panel is not ratified — see the third done-condition.
      """
  ```
  `load_ratified_panel` verifies the digest and **raises on mismatch**.
- **Done when** (all three):
  1. sealing a ratified fixture, then flipping one `face`, makes `load_ratified_panel` raise;
  2. sealing is idempotent;
  3. **sealing an UNRATIFIED panel raises rather than writing a digest.** Without (3) a digest could
     be produced while `ratified: false` — an attestation record binding nothing a human signed.
- **Constraint:** an agent may build and test this tool against **fixtures only**. Running it against
  the live `configs/barrier_panel.yaml` is forbidden by Global Constraint (4).

### T8 · Ratify the panel accessions and faces — **H · 15–20 min**
Check each accession against UniProt, **and check each `face`**. Correct anything wrong, then set
`ratified: true` and fill `ratified_by` / `ratified_on`.

**Deletion criterion — CTO ruling, dispatch #16 (was a trap).** r2.1 said "delete any not expressed
in airway epithelium". Read literally against UniProt tissue-specificity comments, **five of seven
entries have no lung mention — including ABCB1**, the P-gp keystone the entire M5 grouping variable
rests on. UniProt's tissue comment is a *curated sample, not an expression atlas*, so silence there
is a curation gap, not absence of expression — the same epistemic error the three-way P-gp label
exists to prevent, against a different source.

> **Delete ONLY on positive evidence of absence from airway epithelium. Silence is not evidence.**

**What ratification attests to.** Identity (`symbol`, `uniprot`, `alias`) **and `face`** — nothing
more. It does **not** endorse seven modelled carrier terms: per AM-3 the panel holds *identity* and
`theta_priors.yaml` holds *quantity*, and in slice 1 the panel is consumed only by T9's edge join
and T10's ABCB1 resolution. PVR §2E's "two carrier terms" is a θ constraint at M1 under the 5–8
identifiable-parameter budget — seven join targets cost zero parameters; seven *fitted abundances*
would blow that budget. Nobody may later read a ratified seven-entry panel as endorsing seven
mechanisms.

**Optional `airway_evidence:` per entry (`DOI` or `PMID`).** Under the criterion above, "kept" means
*no positive evidence of absence* — weaker than *positive evidence of presence*, and the two states
are otherwise indistinguishable in the file. Supplying `airway_evidence` upgrades an entry to the
strong claim. **Optional by design** so it does not inflate this task; **absent means the weak claim
explicitly**, never the strong one. Human-only — an agent may never populate it.

- **Seal the panel (CTO ruling, dispatch #18).** After setting the attestation fields, run
  `uv run chipsim panel-seal` **from `projects/lung-on-chipsim`** — `uv run`, because `chipsim` is a
  console script inside the project venv and is never on a system PATH; the principal hit
  `zsh: command not found: chipsim` running the bare form on 2026-09-12, which is the **C4
  self-blocking defect recurring one layer down** after the entry point itself was added. It writes
  `ratified_panel_sha256` over the canonically-serialized panel
  list. `load_ratified_panel` verifies it and **raises on mismatch**. Without this, `ratified: true`
  attests to nothing checkable — after T8 any post-ratification edit (a `face` flip, an accession
  swap, a deleted entry) is invisible, which is exactly how N1 went unnoticed until a scorer read the
  plan text. The digest is **not a biological number**, so Global Constraint 1 does not apply.
  **The seal is tamper-evidence, NOT attestation** (CTO ruling, dispatch #27; this line was a
  survivor of that reframe, found 2026-09-09 while preparing T8). `ratified_panel_sha256` is an
  unkeyed digest over public content: it shows the panel has not changed since sealing and can
  **never** show *who* sealed it. The attestation is `ratified_by` plus your act; the digest only
  protects that from silent edit afterwards. Sealing is reserved to you because the **file** is
  human-only — not because the digest establishes identity. Read the Global Constraints block
  above before you seal; it governs, and this task previously contradicted it.
- **Done when** `ratified: true`, `ratified_by` and `ratified_on` are non-empty, every `face` has
  been checked, `ratified_panel_sha256` is populated and verifies, **and T19 passes against the live
  file** (defect 19).
- **Note for T10:** if you delete or re-accession ABCB1, T10 now raises rather than silently
  labelling everything `unknown` (defect 4).
- **Known schema limit (deferred to M1, not a T8 concern):** the `{apical, basolateral}` binary
  cannot represent a two-faced transporter, and two of seven are (FCGRT transcytoses
  bidirectionally; SLCO2B1 is basal/basolateral/apical). Widen the schema at M1 when directional
  transport actually consumes the field.

### T9 · Join edges to the panel — **CA · 4 min**
- **Interfaces:**
  ```python
  def barrier_panel_edges(edges: pd.DataFrame, panel_path: Path) -> pd.DataFrame:
      """Inner-join protein edges onto the ratified panel.
      Raises RuntimeError unless ratified is True AND ratified_by is non-empty.
      A MISSING `ratified` key raises — absence is not consent (defect 1).
      Columns: drugbank_id, uniprot_id, symbol, category, face.
      """
  ```
- **Done when** it raises on `ratified: false`, raises on a file with the key **absent**, raises on `ratified: true` with an empty `ratified_by`, and returns a non-empty frame against `tests/fixtures/barrier_panel_ratified.yaml`.

### T10 · Derive the three-way P-gp label — **CA · 5 min**
- **Files:** `chipsim/harmonize/pgp_label.py` (edit)
- **Interfaces:**
  ```python
  def pgp_substrate_label(
      compounds: pd.DataFrame,
      panel_edges: pd.DataFrame,
      panel_path: Path,
  ) -> pd.Series:
      """Index: canonical_inchikey. Values: 'yes' | 'unknown'.

      Resolves the ABCB1 accession FROM THE RATIFIED PANEL by symbol == 'ABCB1'.
      Never hard-codes P08183 (defect 4 / AM-2: composition is configuration, not code).
      Raises RuntimeError if the ratified panel has no ABCB1 entry.

      'yes'      -> an ABCB1 edge of category 'transporter' exists in the snapshot.
      'unknown'  -> no such edge. NEVER returns 'no' from absence of evidence.

      'no' is assignable only by adjudicate_pgp_labels() with a citation.
      """
  ```
- **Done when** the function cannot emit `'no'`, and raises when ABCB1 is absent from the panel — both asserted in T12.

### T12 · Write the label-safety tests — **CA · 4 min**
r1's two tests were both satisfied by `return pd.Series("unknown", index=...)`, which is precisely
how defect 4's silent degradation went unnoticed (defect 20).
- **Interfaces:**
  ```python
  def test_pgp_label_never_infers_negative():
      """A compound with zero protein edges is 'unknown', not 'no'."""

  def test_pgp_label_domain():
      """set(labels) <= {'yes', 'unknown'} before adjudication."""

  def test_pgp_label_positive_case():
      """A compound with an (ABCB1, transporter) edge is labelled 'yes'.
      This is the test a constant-'unknown' implementation fails."""

  def test_pgp_label_ignores_non_transporter_edges():
      """An ABCB1 edge of category 'enzyme' yields 'unknown'."""

  def test_pgp_label_requires_abcb1_in_panel():
      """A ratified panel with ABCB1 removed raises RuntimeError."""
  ```
- **Done when** all five pass.

### T18 · Curate the PoC compound roster — **H · 30–45 min** *(new — defect 3)*
Which 20–40 compounds are "lung-relevant with published exposure" is a **claim**, so by this plan's
own allocation rule it is human-owned. An auto-filter of `drugbank-slim.tsv` is not a substitute.
- **Files:** `configs/poc_compounds.yaml` (new, hand-curated, git-tracked)
- **Interfaces:** 20–40 entries of `{canonical_inchikey, name, evidence_doi}`. **Identity and
  citation only — no biological numbers.**
- **Done when** the roster has 20–40 entries, every entry carries a non-empty `canonical_inchikey`
  and `evidence_doi`, and every `canonical_inchikey` resolves in the parsed snapshot.

> **r2.15 items 2 and 7 — the hand-off, and the window it starts.** The candidate list is generated
> **only on guarded keys**: after the r2.12 stereo guard and the r2.14 relative-stereo re-key have
> landed, with the disagreement report regenerated, so the principal authors a roster on keys that
> will not move again in slice 1. *(Both have landed — `7592f56`/`8cb72bf`, re-keyed at `1b74814` —
> so the hand-off is unblocked on the CTO's timing.)* Entries stay keyed by `canonical_inchikey`;
> **`drugbank_id` is carried alongside for traceability, never as the key** — this source mislabels
> at least 11 of its stereoisomers, so the key is identity and the name is annotation.
> **Milestone, counted from the day the guarded candidate list is handed over:** the roster (T18) by
> **working day 2**, the P-gp adjudication (T14) by **working day 3**. The plan carries the hand-off
> date and both due dates; **a slip is reported in the dev-log and never back-filled by an agent
> draft.** The candidate list must also carry the tri-state `label_disagrees_with_key` column, so the
> principal sees where the source's own name contradicts the structure he is selecting on.

### S11a · Write the roster validator — **CA · 3 min** *(paired with T18)*
- **Interfaces:** `load_poc_roster(path) -> pd.DataFrame`, rejecting a roster outside 20–40 entries, any entry with an empty `canonical_inchikey` or `evidence_doi`, and any key absent from the snapshot.
- **Done when** each of those four rejection cases raises, verified against `tests/fixtures/poc_compounds.yaml`.

### S12 · Build the run journal (environment + seeds) — **CA · 15 min** *(new — principal requirement; CTO ruling, dispatch #35; rescoped by principal 2026-09-02)*
> **SCOPE AMENDMENT r2.7 (principal, 2026-09-02).** Two removals, one addition. See A&D 4.4a-ii.
>
> **REMOVED — git state.** No `_git_state()`, no shelling out to `git` at runtime. Capturing the
> commit and dirty flag required running `git` with a caller-supplied cwd, and `git` honours
> repo-local config — an arbitrary command execution path (QG blocker B2, reproduced three times).
> **The feature is deleted, not hardened**: a PoC run journal has no need to run `git`, and removal
> takes the attack surface to zero where a defence only shrinks it. Record the code version from
> what the installed package reports. **Accepted cost, stated plainly: a run record can no longer
> prove the tree was clean when it ran.** Do not paper over this in the record's documentation.
>
> **REMOVED — diff and veto state.** Both are v3 exploration-loop artifacts. v0+v1 runs no loop, so
> they would be structurally null for the PoC's whole life — the 'key present, value meaningless'
> shape QG blocker B3 showed is untestable.
>
> **ADDED — seeds.** The seed is resolved from the run config and its resolved value recorded.
> Previously `environment.seeds` was null and nothing ever set a seed, so no replay claim was
> supportable at all.
>
> **The replay test splits in two and the two must never be conflated.** The **v3 form** — 're-run
> any kept diff from journal + seed' — tests the exploration loop and is **not applicable to the
> PoC**; its absence here is not a defect, and S12 never claimed to close it. The **PoC form**,
> which S12 does close: *same config + same seed reproduces the same scores exactly.*

**Partial gap-closure, not a feature.** A&D §4.4 specifies `journal/` as *"append-only run records — diff,
seeds, scores, veto state"* and §5 requires a **replay test**: *"re-run any kept diff from journal +
seed and reproduce the trajectory exactly."* The record spec **names no configuration**, and
`journal/` does not exist. So a replay reading "diff + seed" picks up whatever `configs/` holds **at
replay time**, reproduces *a* trajectory, and **reports success** — the control cannot fail for the
reason it exists. It bites precisely here: `pyarrow` and `rdkit` are `==`-pinned because parquet
bytes are sha256'd and rdkit computes the canonical InChIKey every join and the sealed allocation
key on; a record omitting resolved versions cannot show two runs were the same computation.

It also creates `journal/`, which AM-4's tree lists and **no task creates** — the same gap class as
the original scaffold hole, which is why this is an S-task.

- **Files:** `chipsim/journal.py` (new) · `chipsim/pipeline.py` (edit — open a run in each ETL stage) · `tests/test_journal.py` (new)
- **Interfaces:**
  ```python
  def start_run(command: str, project_root: Path) -> Path:
      """Called BEFORE any work. Creates journal/<run_id>/, COPIES every
      configs/*.yaml into journal/<run_id>/configs/, writes manifest.json.
      Raises if the run directory already exists.
      """
  def read_manifest(run_dir: Path) -> dict:
      """Verify manifest_sha256 and return the manifest.
      REFUSES a manifest carrying no manifest_sha256 — never loads unverified.
      """
  ```
- **Manifest records:** run_id · UTC start · exact argv · git commit **and** dirty flag with the
  dirty file list · python + platform · resolved versions of the output-determining packages
  (`pyarrow`, `rdkit`, `pandas`, `numpy`, `PyYAML`) · per-config sha256 · `CHIPSIM_SEED` /
  `PYTHONHASHSEED` / `SOURCE_DATE_EPOCH` where set.
- **Copies, never references.** A config edited tomorrow must not change what yesterday's run says
  it used. That is the whole requirement in one sentence.
- **A dirty tree is RECORDED, never hidden or refused.** A run from a dirty tree is not reproducible
  from its commit alone; the honest response is to say so in the record — the same posture as
  `unknown` in the P-gp label, where the third state survives into the schema.
- **`panel-seal` is journalled as record type `invocation`, not `run`** — argv, environment,
  timestamp, **no digest**. Recording every invocation is what makes a Global Constraint (4)
  violation *detectable*, which is the enforcement gap (4) otherwise leaves open. The record is an
  audit trail, **never** the attestation.
- **Honesty clause (carried from the seal ruling).** The manifest digest detects modification of a
  run record; it does **not** prove who wrote it. No wording in module, docstring or CLI may imply
  the journal authenticates anyone.
- **Done when** (all six, fixture-testable):
  1. a run snapshots every `configs/*.yaml` and the copies' digests match the manifest;
  2. editing a config **after** a run does not change what that run's snapshot says it used;
  3. re-using a run id **raises** rather than overwriting;
  4. a tampered `manifest.json` fails `read_manifest()`;
  5. a crashed run leaves no `outcome.json`, so it cannot read as success;
  6. a `panel-seal` invocation record carries **no** digest field.

> **Delegation of approve-on-execute authority (r2.38, principal-directed, 2026-09-22).** S12's
> approve-on-execute flag (`--yes`, `test_run_approval.py`) is a **different mechanism from
> Global Constraint (4)/T7a's panel-seal TTY gate**, which stays absolute — no flag path exists
> for it, this delegation does not create one. S12's flag path was always designed to be
> legitimate (`test_yes_approves_and_is_RECORDED_as_a_flag_not_as_a_human` — the run **succeeds**
> on the flag, distinctly logged); the open question was **who currently holds standing authority
> to supply it**, surfaced when the CTO directed the worktree agent to run T13 with `--yes`
> without noticing that directive reversed the CTO's own prior ruling (dispatch #181: *"the
> principal's call, not mine or yours"*) — caught and held by the agent before acting, per its own
> reading of §16's purpose (dispatch #185).
>
> **Ruled, on the record, not inferred from a task line**: the principal delegates `--yes`
> authority for S12-gated, CA-classified tasks (T13 first) to the CTO. **Same shape as the
> `plan-gate sign` delegation** (`fd2c00d`, 2026-09-10) — *the invocation is delegated, the
> judgement is not.* This delegation covers supplying the flag once a task is already
> CA-classified and gated only by S12; it does **not** reach classification decisions (whether a
> given command should be ETL/CA at all — that stays a plan-authorship ruling, e.g. r2.34/r2.35's
> T13 ETL-vs-node question) and it does **not** touch Global Constraint (4) in any form. A run
> approved this way is recorded as CTO-approved by explicit delegation, not as principal-approved
> and not as unattended — the record must say which.
>
> **The record cannot yet say which (r2.40, agent-found, ruled).** T13's first real run under
> this delegation showed `approval.json` records `mode="flag"`, `stdin_was_a_tty=false` — **byte-
> for-byte what an unsupervised agent run produces**, with no field distinguishing "CTO-approved
> by explicit delegation" from "nobody was ever asked." The agent correctly declined to patch this
> itself: the approval schema is S12/r2.34 territory, and r2.38's delegation explicitly does not
> reach mechanism changes — inventing a field to satisfy an instruction would be the same shape as
> defaulting Finding D's prior to satisfy a required argument. **New T29 below, ruling the agent's
> own proposed fix**: an explicit `--approved-by <string>`, recorded **verbatim**, **no default**,
> **no inference from identity** — the honesty clause already governing this file (*"the manifest
> digest... does not prove who wrote it"*) extends to this field rather than being quietly eroded
> by it. Absent the flag, `mode="flag"` keeps meaning exactly what it means today; nothing here
> changes T13's own already-completed run, whose provenance for now lives in its commit body.

### T29 · Record who supplied approve-on-execute, when it isn't the operator — **CA · 3 min** *(new, r2.40, agent-found; Files corrected r2.41 — landed at `chipsim/pipeline.py`, not `journal.py`)*
- **Files:** `chipsim/pipeline.py` (edit — `_write_approval_record`, where `approval.json`'s
  `mode`/`stdin_was_a_tty` fields are actually written; r2.40's `journal.py` was wrong, caught by
  the agent reading the done-condition against the real path, same check as S13/S6) ·
  `tests/test_run_approval.py` (edit)
- **Interfaces:** an optional `--approved-by <string>` CLI flag, threaded through to
  `approval.json` as a new field, recorded **exactly as given** — never derived from
  `agent-identity`, never defaulted, never inferred from `mode` or the absence of a TTY. Omitting
  the flag leaves the field absent; `mode`/`stdin_was_a_tty` keep their current meaning
  unconditionally, this is additive only.
- **Done when** (1) `--approved-by cto` records `approved_by: "cto"` verbatim alongside the
  existing `mode`/`stdin_was_a_tty` fields; (2) omitting the flag leaves `approved_by` absent, not
  a default string; (3) every existing `test_run_approval.py` assertion still passes unmodified
  (additive, not a rewrite of the existing contract).

### T13 · Emit the adjudication worksheet — **CA · 5 min**
- **Interfaces:**
  ```python
  def write_adjudication_worksheet(
      labels: pd.Series,
      compounds: pd.DataFrame,     # needed for `name` — r1's signature could not produce it (defect 21)
      out: Path,
  ) -> int:
      """Write a CSV: canonical_inchikey, name, snapshot_label, adjudicated_label,
      evidence_doi, adjudicated_by, adjudicated_on. Last four empty for H.

      **GENERATED COLUMNS (r2.17), a third class beside declared and human-added:**
      `stereo_is_relative` and `label_disagrees_with_key` (tri-state:
      disagrees / agrees / unresolved). Recomputed on EVERY regeneration from the
      current compounds frame, NEVER carried from a prior sheet, OPTIONAL on read
      so legacy worksheets still load, and placed after `snapshot_label` so the
      reviewer sees them beside the evidence they qualify. `label_disagrees_with_key`
      is computed from the COMMITTED `configs/label_structure_reference.yaml`, never
      a live lookup, so a worksheet regenerates identically offline. The verdict must
      cover EVERY name sharing a key, not the first one encountered (F-01).

      NEVER CLOBBERS (defect 22): if `out` exists, merge on canonical_inchikey and
      preserve every non-empty adjudicated_*/evidence_doi cell. Raises if a
      previously-adjudicated key has disappeared from `labels`.
      Raises if any label index is missing from `compounds`.
      Returns row count.
      """
  ```
- **Files:** `data/interim/pgp_adjudication.csv` (generated draft)
- **Done when** the CSV has exactly one row per T18 roster entry (`20 <= n <= 40`), the four verdict columns are empty, **and re-running against a partially-filled worksheet preserves every filled cell** — the condition that protects T14's 60–90 minutes from a single ETL re-run.

### T14 · Adjudicate the P-gp labels — **H · 60–90 min**
Fill `adjudicated_label` and `evidence_doi` for every row. This is the task that makes the M5
grouping variable trustworthy, and it **cannot be delegated** — a fabricated DOI here would
corrupt the coverage claim invisibly. Leave genuinely uncertain compounds as the explicit string
`unknown`; they are **excluded from both calibration groups** rather than guessed into one.

> **r2.19 (G-20) — do not type a compound name into any cell.** `adjudicated_by` takes the
> reviewer's name; `evidence_doi` takes a DOI. A DrugBank compound name typed into either reaches
> the **tracked** file and re-creates the `(name, structure)` association the five-column shape
> exists to prevent. **No column check can catch this** — the column is legitimate, only the value
> is wrong — so it is stated here as an instruction and recorded as a limit rather than claimed as
> enforced. Work from `canonical_inchikey`; the generated worksheet shows you the name beside it.
- **Files (r2.20):** on completion, publish with **`chipsim adjudication-export`** — not by hand.
  The CLI is the only sanctioned way the filled worksheet becomes `configs/pgp_adjudication.csv`;
  r2.19 called the hand-move "the accident it exists to prevent" while this clause still said
  "move to", which is the drift r2.19 itself was repairing. **The export journals fail-closed**
  *(r2.20, stating a behaviour that until now was inherited from tuple membership in a workflow
  test rather than chosen)*: it is idempotent and publishes nothing on failure, so refusing to
  proceed when the journal cannot be written costs nothing and preserves the record. **Still
  git-tracked**: r1 left this
  in `data/interim/`, which is git-ignored and DVC-tracked, leaving the plan's most load-bearing
  human artifact unversioned and unattributable (defect 23).
- **Interfaces (r2.18):**
  ```python
  # (r2.19) CLI entry, on the `chipsim panel-seal` precedent (C4): a helper whose only
  # invocation is a Python call loses to hand-deleting columns — the accident it exists to
  # prevent. `chipsim adjudication-export --worksheet <p> --out <p>`.
  #
  # (r2.19, G-15) `write_adjudication_worksheet` REFUSES to write to any resolved path under
  # `configs/`; `export_tracked_adjudication` is the ONLY writer permitted to target it.
  # Refuse by PATH, not by shelling out to `git ls-files` from library code — that is slow,
  # environment-dependent and wrong in a non-git checkout. The worksheet shape carries `name`
  # at position 2; without this refusal it can be written straight to the tracked path, which
  # is what makes the r2.18 split load-bearing rather than decorative.
  #
  # (r2.19, G-01) The export REFUSES to overwrite a filled tracked file. Measured before the
  # refusal existed: a BLANK worksheet exported over a filled file left 0 of 24 verdicts and
  # RETURNED 24 — destruction reporting success. It needs no carelessness: lose `data/interim/`,
  # T13 regenerates the worksheet blank without error, and a re-export destroys the adjudication.
  # Defect 22's never-clobber rule covered the worksheet and left the published record unguarded.
  def export_tracked_adjudication(worksheet: Path, out: Path) -> int:
      """Project the reviewer's filled worksheet to the five tracked columns:
      canonical_inchikey, adjudicated_label, evidence_doi, adjudicated_by,
      adjudicated_on. Returns rows written.

      REFUSES (raises) on any extra human-added column rather than dropping it
      silently — a reviewer who added a column meant something by it, and a
      projection that discards it without saying so loses their work invisibly.
      Generated columns (`name`, `snapshot_label`, `stereo_is_relative`,
      `label_disagrees_with_key`) are dropped by design and named in the docstring
      so the omission is legible.
      """
  ```
  **Why a helper rather than a manual step:** "move to `configs/`" would otherwise mean a human
  deleting columns by hand, which is exactly how a `name` column reaches a tracked file by accident.
  With the helper, a tracked file carrying `name` has to be written deliberately.
- **Done when** every row has a verdict and a DOI, or an explicit `unknown`, and the file is tracked by git **carrying no `name` column** (r2.17).

> **r2.17 — the tracked adjudication file drops `name`; the worksheet keeps it.** The worktree agent
> raised it (F-05): the filled sheet pairs a DrugBank `name` with a `canonical_inchikey`, and if that
> lands tracked it is exactly the `(name, structure)` association the principal's record-content
> invariant protects. Both halves matter, so they are separated rather than traded: **tracked**
> `configs/pgp_adjudication.csv` carries `canonical_inchikey`, `adjudicated_label`, `evidence_doi`,
> `adjudicated_by`, `adjudicated_on` — **no `name`** — preserving defect 23's fix that a human
> artifact must be versioned and attributable; the **generated, untracked** worksheet keeps `name`
> beside the evidence, because a reviewer adjudicating 60–90 minutes of labels cannot work from keys
> alone. T13/T15's interfaces above are amended in the same revision to match the code that now
> exists (generated columns; the legacy raise) — they had drifted, which the agent flagged rather
> than edited, the plan being hash-locked and the CTO's.

### T15 · Load adjudicated labels with provenance — **CA · 5 min**
- **Interfaces:**
  ```python
  def adjudicate_pgp_labels(
      adjudication: Path,          # the TRACKED five-column file T14 defines (r2.18)
      compounds: pd.DataFrame,
      parquet_out: Path | None = None,
  ) -> pd.Series:
      """Index: canonical_inchikey. Values: 'yes' | 'no' | 'unknown'.

      **(r2.18) Reads the TRACKED file, and RECOMPUTES `stereo_is_relative` from
      `compounds`** — per key, True if any member is flagged, exactly as T13 generates
      it. The flag is a *generated* column: never carried, therefore never stale.
      RAISES if `compounds` lacks `stereo_is_relative` (the same refusal as T10/T13),
      and RAISES if any adjudicated key is absent from `compounds`.

      *(r2.17 said this function read the worksheet and raised when the WORKSHEET
      lacked the flag. That contradicted T14 as amended in the same revision: the
      tracked five-column file has no such column, so T15 would have raised every
      time. Two clauses were amended without checking the composition — the
      plan-level form of the F-01 defect. Caught by the worktree agent before any
      code was written; the alternatives were rejected as recorded under T14.)*

      The flag is written into `pgp_labels.parquet` as a real boolean so T17
      receives it.

      Raises if NO row has a non-empty adjudicated_label (a wholly unadjudicated
      **tracked file** — r1 returned all-'unknown' and looked identical to a
      completed one, defect 6). *(r2.19: said "worksheet" until the composition
      check caught it — the fourth clause in this task still describing the input
      r2.18 changed.)*
      Raises if ANY row has an empty adjudicated_label (partial adjudication).
      Raises if any value is outside {'yes','no','unknown'}.
      Raises if any 'yes'/'no' row lacks evidence_doi or adjudicated_by.
      Raises if the 'yes' group or the 'no' group is empty (defect 24) — the M5
      grouping variable is unusable with only one populated group.

      Also writes data/processed/pgp_labels.parquet, which T17 reads (defect 25).
      """
  ```
  An empty cell is an *incomplete* verdict; the literal string `unknown` is a *completed* one.
- **Done when** (r2.19 — the clause now names the **tracked adjudication file**, which is what T15
  reads since r2.18; it had still said "worksheet" three times) a wholly-blank **tracked file**
  raises, a partially-filled one raises, an all-`unknown` one raises, a `no` row with an empty DOI
  raises, a fully-adjudicated fixture returns a Series over `{yes, no, unknown}`, the parquet
  round-trips to an identical Series, **and `stereo_is_relative` survives that round-trip** — the
  module's own reader must not drop the flag T15 writes "so T17 receives it" (G-19). Plus: a tracked
  file carrying **any column outside the five** raises (G-17 — the only checkable reading of
  "five-column", and a human `cp` bypasses the export helper entirely).

### T17 · Render the data-provenance block — **CA · 4 min**
Changed from **(edit)** to **(new)**: `chipsim/eval/card.py` did not exist and no plan creates it;
M0c owns the card (defect 13). This task builds the block and unit-tests it; wiring it into the
card moves to M0c.
- **Files:** `chipsim/eval/provenance_block.py` (edit)
- **Interfaces:**
  ```python
  def render_data_provenance(provenance: Path, labels: pd.Series) -> str:
      """Composes the display string FROM upstream_version + snapshot_date —
      never hard-coded (defect 14). Renders source, commit, licence, the three
      label counts, and pgp_groups_usable computed from those counts (defect 24).
      """
  ```
- **Done when**, against `tests/fixtures/provenance.yaml` and a fixture label Series, the output contains the literal `DrugBank 4.2 (2015-03-19 snapshot)` and three integer counts; **and changing `upstream_version` in the fixture changes the rendered string** — the assertion that proves the value is composed, not hard-coded.

### T16 · Export the ETL workflow — **CA · 5 min** ⚠️ **DESCOPED — see §7**
r1 required a provisioned, running n8n instance with a Python execution path, and a "byte-identical"
done-condition that was unfalsifiable (no committed baseline, no remote, parquet bytes not stable
across versions). Both are out of reach in slice 1 (defects 27, 28).
- **Files:** `orchestration/n8n/etl_drugbank.json` (new, exported)
- **Interfaces:** five node definitions — fetch → hash-verify → parse → **provenance-tests** → write. The node is named `provenance-tests`, not `contract tests`: §4.5 sanctions *data*-contract tests, which arrive with the ChEMBL plan (defect 29).
- **Done when** the JSON validates against the n8n workflow schema, **each of the five nodes names a CLI entrypoint that exists in the installed package**, and the recorded sha256 of `data/processed/drugbank_compounds.parquet` equals `data/processed/drugbank_compounds.sha256`.
- **Not in slice 1:** provisioning n8n and executing the workflow end-to-end. Tracked as **T16a**, deferred.

---

## 6a · Tasks — M1 slice (ODE core) — **r2.36, first pass**

**Scope note (r2.36).** `§8 Scope check` ruled *"the next plan should be M0b, not the other
ingestors"* — that ruling stands for M2–M6, which need ChEMBL/BindingDB/TDC affinity and ADME
data this plan never fetches. **M1 is the one exception**: A&D §5 scopes it to *"ODE core with
literature θ, reference compounds"* — it needs only `theta_priors.yaml` (A&D §1 row S5, device/
physiology literature) and a handful of reference compounds with **published** on-chip transport
data, neither of which depends on the ingestors plan or on M0b's 80–100 chip-record curation.
**Principal-directed, 2026-09-22**: scope M1 to full task level now; M2–M6 stay stubs (§6b) until
their own data dependencies clear. **First pass, same standing as M0's own r1**: written from
the A&D spec before any M1 implementation exists to push back against it, so expect the same
defect-driven revision M0 went through (§7), not correctness on the first read. Signed under
standing-delegation, same as r2.32–r2.35 — this is a plan-authorship act, not a claim that every
interface below has been implementation-tested.

**Two literature-curation tasks this milestone needs, and neither is T18.** T20 (θ priors) and
T21 (reference compounds + published ordering) are **new H-owned artifacts**, following the same
shape as T1/T14/T18 — an agent may research-assist (evidence, cited, `not found` is a valid row)
but the human signs the claim. **T21's reference-compound set is not T18's PoC roster** — T18 was
curated for lung-relevance and P-gp evidence; T21 needs compounds with an independently
*published on-chip transport measurement* to check the M1 gate against. Some overlap is
plausible, none is assumed. Conflating two compound lists is exactly defect 3's shape from the
M0 revision log (§7) — named here so it is not rediscovered the same way.

### S13 · Scaffold a θ-priors template — **CA · 3 min** *(r2.37 — retargeted, see below)*
> **Correction, r2.37.** As first written (r2.36) this task's `Files:` was
> `configs/theta_priors.yaml` — the exact path `S6`'s done-condition asserts **does not exist**
> (*"deliberately absent — H-owned, no agent may create them"*, enforced by
> `test_s6_human_owned_configs_are_absent`, green before this task ran). The agent caught it
> before implementing, read S6 against the path S13 named rather than assuming a fresh task
> section had already reconciled with an old one, and declined to weaken a passing Global
> Constraint guard to make a task line true. **Ruled (c) of the three options raised**: absence
> stays the enforcement mechanism for `configs/theta_priors.yaml` itself; the scaffold moves
> **outside** `configs/`, where S6's guard says nothing. Global Constraint 1's own text already
> permits this — *"the agent writes the schema"* — the collision was with S6's chosen
> *mechanism* (file absence), never with the constraint's substance, and (c) is the one option
> of the three that leaves that mechanism at full strength rather than trading it for a weaker
> content check. This is r2.36's first defect, exactly as its own text said to expect, caught
> before implementation rather than after.
- **Files:** `configs/templates/theta_priors.scaffold.yaml` (new — field scaffold, no values;
  outside `configs/` proper so S6's absence guard is untouched)
- Declares one entry per A&D §1 row-S5 field (`flow_ul_min`, `membrane_um`, `porosity`,
  `strain_pct`, `area_mm2`, `coating`), each as `{value: null, unit: <str>, citation: null,
  assumed: true}` — the "unsourced values flagged `assumed: true`" rule (A&D §1.2), scaffolded
  before any value exists rather than retrofitted.
- **Done when** the YAML parses, has exactly the six declared fields, every field starts
  `assumed: true` with `value: null`, **and `configs/theta_priors.yaml` still does not exist**
  (the S6 invariant, asserted here too so a regression is caught at the task that could cause it,
  not only at S6's own test).

### T20 · Source literature θ priors — **H · 20–30 min** *(materializes r2.37's template)*
- **Files:** `configs/theta_priors.yaml` (new — **the human's own copy of S13's template**,
  `configs/templates/theta_priors.scaffold.yaml`, filled in). The human copies the template into
  `configs/`, then fills it — no agent step creates this path, so S6's absence guard covers the
  full time between S13 and T20, not just up to S13.
- Fills `value` + `citation` for each field from OSP PK-Sim / PBPK-on-chip-review literature
  (A&D §1 row S5's source list); sets `assumed: false` only where a citation is recorded. A
  field left `assumed: true` is a stated gap, not an error — same posture as T14's `unknown`.
- **Done when** every filled field carries a resolvable citation, and the file re-parses under
  T24's validator without raising.

### T21 · Curate M1 reference compounds + published on-chip ordering — **H · 20–30 min**
- **Files:** `configs/m1_reference_compounds.yaml` (new — schema mirrors T18's roster: a
  top-level `compounds:` key wrapping `{canonical_inchikey, name, published_transport_value,
  evidence_doi}` flow-maps)
- 3–8 well-characterized compounds with a **published** on-chip (organ-on-chip / microfluidic)
  transport or permeability measurement — the thing T27's gate checks the model against. Not
  drawn from T18 by default (see scope note above).
- **Done when** the file has `3 <= n <= 8` entries, every `evidence_doi` resolves, and no
  `canonical_inchikey` duplicates.

### T22 · Build the transport ODE core — **CA · 5 min**
- **Files:** `chipsim/transport/ode.py` (new)
- **Interfaces:**
  ```python
  def transport_ode(
      theta: "ThetaConfig",        # T24 — validated, every field cited or assumed=True
      drug_params: dict,           # P_app / f_u / sink; M1 uses literature defaults, ADME
                                    # heads (M2) supply them for real later
      schedule: dict,
      t: "np.ndarray",
  ) -> "np.ndarray":
      """Two-compartment ODE, 6 parameters — only alpha and the sink coefficient
      free (A&D §2, objective T3); every other field is FIXED at theta's value.
      Returns C_free(t) at the tissue face, the ONLY interface a downstream
      module reads (A&D 'whole design in one picture'). Deterministic given
      (theta, drug_params, schedule): no unseeded randomness anywhere in solve.
      """
  ```
- **Done when** (1) a smoke fixture integrates to a fixed point for a literature-typical theta
  without raising; (2) two calls with identical inputs return bit-identical arrays (A&D §2B
  determinism requirement); (3) increasing schedule dose strictly increases cumulative C_free
  AUC (the sanity floor T26 exercises for real).

### T23 · Fit routine — MAP in log space — **CA · 5 min**
> **Finding D (r2.39) — the (alpha, k_sink) prior's home, ruled.** A&D §2 T3 reads *"MAP fit ...
> with `theta_priors.yaml` prior"*, which the agent correctly showed cannot mean what it appears
> to: S13/T24 (r2.37) scaffold `theta_priors.yaml` with **exactly** the six A&D §1 row-S5 fields,
> equality-enforced, not containment — a deliberate choice (a superset field is a parameter
> nobody sourced) that leaves no room for `alpha`/`k_sink` in that file without breaking the S6/
> S13/T24 guards r2.37 just finished protecting. **Ruled: the A&D sentence means "the fit uses
> theta's fixed values", not "theta_priors.yaml contains the alpha/k_sink prior."** The prior gets
> its **own** artifact — **new S14 + T28 below**, same scaffold/fill split as S13/T20, because
> this is the third occurrence of that exact shape (S13 itself, Finding B, now D) and deserves the
> pattern rather than a fourth ad hoc answer. **The agent's interim implementation is ratified,
> not just accepted**: `prior` as a **required keyword argument with no default** was the only
> form that invents nothing — a default here would be the single most consequential unsourced
> number in the module, exactly what T24 exists to refuse, and would have silently pre-answered
> this ruling. Keep it required even after T28 exists; T28 supplies the value, the signature does
> not get a default.
- **Files:** `chipsim/transport/fit.py` (new)
- **Interfaces:**
  ```python
  def fit_transport_params(
      reference_compounds: "pd.DataFrame",  # T21
      theta: "ThetaConfig",                 # T24
      prior: "TransportPrior",              # T28 — REQUIRED, no default (Finding D, r2.39)
  ) -> "FitResult":
      """MAP fit in log space. Only alpha and the sink coefficient are free
      (A&D §2 T3) — every other theta field stays FIXED at its prior, never a
      fit target. RAISES if reference_compounds has fewer than 3 rows (A&D
      §1.3 — no split is meaningful below that), and RAISES if any theta
      field lacks a citation and is not explicitly assumed=True (never fits
      against a silently-unsourced prior).
      """
  ```
- **Done when** fitting a synthetic fixture with a known-recoverable `(alpha, sink)` pair
  recovers both within a stated tolerance; fitting raises on `<3` reference rows; fitting raises
  on an uncited, unmarked theta field. **Plus (Finding E, r2.39, noted not ruled)**: at the A&D
  §1.3 minimum of 3 reference rows, `(alpha, k_sink)` is only weakly identifiable — the two
  parameters trade off along a near-degenerate ridge, so the reported pair is substantially
  prior-determined, not a defect but a property T28's human must weigh seriously, not
  rubber-stamp. `FitResult` carries its `prior` and `n_reference` so this is never silently lost.
  If the pair needs to be strongly identified, the lever is T21's schema (more than one
  observable per compound) — an H-owned change, the principal's call, not a fit-routine fix.

### S14 · Scaffold a transport-prior template — **CA · 2 min** *(new, r2.39, Finding D)*
- **Files:** `configs/templates/transport_prior.scaffold.yaml` (new — same S13 pattern: outside
  `configs/` proper, so no absence guard is needed or created for a file S6 never named)
- Declares `alpha_prior: {mean_log: null, sigma_log: null, citation: null, assumed: true}` and
  `k_sink_prior: {mean_log: null, sigma_log: null, citation: null, assumed: true}`.
- **Done when** the YAML parses with exactly those two entries, both `assumed: true`.

### T28 · Source the transport-core MAP prior — **H · 15–20 min** *(new, r2.39, Finding D)*
- **Files:** `configs/transport_prior.yaml` (new — the human's copy of S14's template, filled)
- Fills `mean_log`/`sigma_log`/`citation` for `alpha` and `k_sink` from whatever literature
  supports a transport rate-constant prior for the M1 reference compounds (T21), or states an
  explicit uninformative prior with `assumed: true` and a stated width — either is legitimate,
  silence is not. **Read Finding E above before treating this as a formality**: at 3 reference
  compounds the reported `(alpha, k_sink)` is substantially prior-determined, so this number does
  real work on the M1 result, not just on satisfying a required argument.
- **Done when** both fields load through a `TransportPrior` validator (same shape as T24's
  `ThetaConfig`: value+citation or `assumed: true`, nothing silently absent).

### T24 · θ container + validator — **CA · 3 min**
- **Files:** `chipsim/transport/theta.py` (new)
- **Interfaces:**
  ```python
  @dataclass(frozen=True)
  class ThetaConfig:
      """Loads and validates configs/theta_priors.yaml. Every field carries a
      unit and EITHER a value with a citation OR assumed=True — never silently
      absent. RAISES on a field missing both (the T1 'unsourced values flagged
      assumed: true' rule, enforced here rather than only stated in prose).
      """
  ```
- **Done when** loading a fixture with a field missing both citation and `assumed: true` raises;
  loading a complete fixture succeeds with every field accessible by name; loading is idempotent.

### T25 · Wire the run journal into fit/predict — **CA · 3 min**
> **Finding C (r2.39), ruled.** T25 is **function-level wiring only** — it adds no CLI
> subcommand. It calls `journal.start_run` from inside `chipsim/pipeline.py`'s existing
> `fit_transport_params`/`transport_ode` call path; there is no new `chipsim fit` or
> `chipsim predict` verb at M1. Consequently **r2.34's `ETL_SUBCOMMANDS`/node-vs-non-node split
> and `NON_NODE_REASONS` do not apply to T25** — nothing to declare, because nothing is exposed.
> If a later milestone (M2+) does add a CLI entry point for fit/predict, *that* task earns the
> three declarations at the time it's written, not retroactively here. Stated explicitly because
> the agent was right that guessing "function-level" to dodge the declarations is exactly how a
> command later appears with no reason recorded — this is a ruling, not a guess.
- **Files:** `chipsim/pipeline.py` (edit)
- Every `fit_transport_params` / `transport_ode` invocation opens a run via S12's
  `journal.start_run` before touching theta or reference data — the PoC replay form from A&D
  §4.4a-ii: *same config + same seed reproduces the same scores exactly.* No new journal
  mechanism; this is the integration point into the one S12 already built.
- **Done when** two runs from the same config + seed produce manifests whose per-config digests
  match and whose recorded scores are bit-identical; a run killed mid-fit leaves no
  `outcome.json` (crash detection — S12 done-when 5, exercised here for real).

### T26 · Implement `test_monotonicity.py` — **CA · 4 min**
> **Finding B (r2.39), ruled.** "Literature-typical theta ... never a mock" is retargeted:
> a **committed synthetic fixture** under `tests/fixtures/` is permitted, ratified here as a
> general rule rather than a one-off — the agent's own recommendation, and correct for the reason
> it gave. Global Constraint 1 forbids an agent writing a value into `configs/theta_priors.yaml`
> (or `configs/assumptions.yaml`) and forbids treating an unsourced number as biology; it does not
> and was never meant to forbid a dimensionally-plausible, **clearly-labelled-synthetic** fixture
> whose only job is to exercise a *sign*, not stand in for a citation. T26's three assertions are
> about direction (dose↑→exposure↑, flow↑→flux↓, membrane↑→flux↓), never about magnitude, so a
> synthetic fixture proves the code without anyone leaning on its numbers as physics. **Binding
> conditions, so this permission cannot be read back into T20 or theta_priors.yaml itself**: the
> fixture must (1) live under `tests/fixtures/`, never `configs/`; (2) be loaded through the real
> `ThetaConfig`/`transport_ode`, never a mock of either (the "never a mock" clause was right about
> *this*); (3) carry a filename and an in-file comment stating it is synthetic and not
> literature-sourced, so no later reader mistakes it for T20's work.
>
> **General rule, stated because this is the third occurrence of the same shape (S13, this, and
> Finding D)**: before a CA done-condition ships, check whether the artifact or value it names is
> already claimed by a standing guard elsewhere in this plan. The agent's own proposed check — "a
> cheap read at plan-revision time" — is adopted as practice for future §6-family revisions, not
> written into the plan as new machinery (this plan already has enough process for its own sake;
> the fix is reading before writing, not another script).
- **Files:** `tests/test_monotonicity.py` (edit — currently `pytest.mark.skip(reason="M1 — ODE
  solver not yet built")`, S4's own placeholder, now buildable)
- Replaces the `raise AssertionError("not implemented")` stub with three real assertions against
  T22's `transport_ode`, using a **clearly-synthetic, dimensionally-plausible** theta fixture from
  T24 (never a mock of T24 or T22 themselves): (1) exposure is non-decreasing in dose; (2) higher
  flow lowers cumulative flux; (3) thicker membrane lowers flux. Sign-knowledge only (A&D §2,
  objective T7) — no learned monotonicity weight yet; that arrives with M4.
- **Done when** the skip marker is removed and all three assertions run against real code (real
  `ThetaConfig`, real `transport_ode`) fed a fixture that is honestly synthetic, not fixtures
  standing in for the code under test.

### T27 · M1 gate check — **CA · 4 min**
- **Files:** `chipsim/eval/m1_gate.py` (new), `tests/test_m1_gate.py` (new)
- **Interfaces:**
  ```python
  def check_m1_gate(
      predicted: "pd.Series",    # transport_ode output, exposure-ranked, indexed by
                                  # canonical_inchikey
      reference: "pd.DataFrame", # T21's published ordering
  ) -> "GateResult":
      """The M1 milestone gate (A&D §5): predicted on-chip ordering must
      reproduce the published ordering WITHIN 3-FOLD per compound — not a
      rank correlation, not an average. Returns per-compound fold-error and
      a pass/fail veto; never averages away one compound that misses.
      """
  ```
- **Done when** a fixture where every compound is within 3-fold passes; a fixture with one
  compound at 3.5-fold fails, **naming that compound** in the result.

---

## 6b · M2–M6 — scoping stubs (blocked; sequenced behind M0b + the ingestors plan)

Per `§8 Scope check`'s standing ruling, task-level detail for M2–M6 waits on the ChEMBL/
BindingDB/TDC/LINCS ingestion plan (affinity + ADME labels) and, for M5's pre-registration, on
M0b's curated chip records. Listed here only as a shape, not a commitment — each earns the same
iterative-ruling treatment M0 and M1 got, when its data dependency clears.

| Milestone | What it needs first | Anticipated task shape |
|---|---|---|
| **M2** ADME heads (P1–P3) | TDC ADME labels (ingestors plan) | CA: train/CV P_app, f_u, sink heads; H: none anticipated — labels are public benchmark data, not a curated claim |
| **M3** Occupancy engine | Affinity data (ingestors plan) + M1's theta plumbing | CA: Kd lookup + Boltz-2 fallback + Hill transform; H: panel composition (already T8-adjacent) |
| **M4** Readout head | M3's occupancy vector; L1000 (ingestors plan, S6) | CA: one channel (barrier_integrity) + FiLM conditioning + adversary; H: channel selection, adversary-result read |
| **M5** Uncertainty stack | M0b's curated records (AM-6 arithmetic re-check, §7) | CA: L0–L3 per A&D §2D; H: pre-registers the two P-gp groups **before** any coverage is computed |
| **M6** Acquisition (retrospective replay only) | M5 complete | CA: BALD/BatchBALD over the sealed paper-lab pool; H: releases sealed records on schedule |

---

## 7 · Revision log (r1 → r2)

**33 plan-validity defects** and the scaffold hole, folded in per CTO directives of 2026-08-26 and
2026-08-30. The six previously enumerated are D1–D6 below; the rest were re-derived in an
independent audit of r1 against the A&D, PVR and CONTEXT.md.

| # | Tasks | Defect | Resolution |
|---|---|---|---|
| 1 | T7/T9 | `ratified` emitted as a YAML **comment** — T9's guard could never fire | real top-level key; missing key also raises |
| 2 | T3/T11 | hashes returned, never persisted — T11 unwritable | T3 writes `SHA256SUMS.json` |
| 3 | T13/T14 | "PoC compound set" meant both drugbank-slim (~10³) and PVR's curated 20–40 | roster is H-owned **T18**; slim is renamed *candidate pool* |
| 4 | T10 | hard-coded P08183 that T8 may delete → silent all-`unknown`, T12 still green | resolve from ratified panel; raise if ABCB1 absent |
| 5 | T4 | done-condition passed with DVC never initialized | 4-part condition incl. `.dvc` pointer + `dvc status` |
| 6 | T15 | wholly unadjudicated worksheet raised nothing | explicit completeness gate |
| 7 | T3/T5/T6 | `SNAPSHOT_FILES` keys implied a nested `data/` level T5/T6 did not expect | flat writes; `raw_dir` contract stated |
| 8 | T4–T10 | **no task ever performed the fetch** | new **T4a** |
| 9 | T5/T6 | both done-conditions vacuously true on an empty frame | row-count floors, set **equality**, golden row |
| 10 | T4 | `.gitignore` "(edit)" on a nonexistent file; no `--subdir`; blanket ignore swallowed the `.dvc` pointer | S7 + S8 |
| 11 | T4/T16 | no DVC remote — `dvc pull` could never work | new **S9** |
| 12 | T11 | `tests/test_contracts.py` "(edit)" on a nonexistent file; no `pyproject.toml`, no package | S1–S4 |
| 13 | T17 | `chipsim/eval/card.py` "(edit)" on a file no plan creates | retargeted to `provenance_block.py` (new) |
| 14 | T17/T1 | rendered string ≠ stored string; a wrong `upstream:` still rendered correctly | structured `upstream_version` + `snapshot_date`, composed |
| 15 | T1 | done-condition vacuous; free-form Markdown unparseable by T11 | split into `provenance.yaml` + prose |
| 16 | T1/T2 | **ordering error** — T1 required a value T2 produces | T2 now precedes T1 |
| 17 | T2/T11 | commit is a mutable-branch head; only a shape regex guarded it | `audited_commit` + required rationale |
| 18 | T7/T8/T9 | `ratified` per-entry in prose, file-level elsewhere | ruled file-level; prose corrected |
| 19 | T8 | done-condition was pure attestation | new **T19** UniProt verification script |
| 20 | T12 | both tests passed on a constant-`unknown` implementation | positive + category + panel-absence cases |
| 21 | T10/T13 | T13 needed a `name` column T10's Series could not supply | signature takes `compounds` |
| 22 | T13/T14 | regenerating the worksheet silently destroyed the adjudication | merge-preserve, never clobber |
| 23 | T14 | the worksheet lived git-ignored and unversioned | completed file moves to `configs/`, git-tracked |
| 24 | T14/T15 | nothing checked the adjudication yielded two usable groups | T15 raises on an empty group; card renders `pgp_groups_usable` |
| 25 | T15/T17 | T15's Series was never persisted, so T17's counts had no source | writes `pgp_labels.parquet` |
| 26 | T16 | no task wrote the parquet; no parquet engine in the stack | new **T5a**; `pyarrow` added |
| 27 | T16 | "byte-identically" unfalsifiable | recorded sha256 over a canonical serialization; `pyarrow` pinned |
| 28 | T16 | n8n never provisioned; no Python path from a node | **descoped** to JSON + entrypoint validation; T16a deferred |
| 29 | T11/T16 | "contract test" named two different things | `test_provenance.py` split out; node renamed |
| 30 | T16 | `compounds.parquet` collided with A&D §1's harmonized S1 artifact | renamed `drugbank_compounds.parquet` |
| 31 | T5/T10–T15 | **no canonical InChIKey** — RDKit declared, used nowhere; the plan's own Goal unmet | new **T5b**; all downstream keyed on `canonical_inchikey` |
| 32 | T3 | done-condition tested half its own contract | 39-char **and** non-hex cases |
| 33 | T9/T11/T17 | human-gated done-conditions the agent was told it could not evaluate | fixtures in S5 + deferred integration conditions |

**AM conformance.** AM-1 ✓ · AM-2 ✓ (defect 4 fixed: composition is configuration) · AM-3 ✓
(defect 1 fixed: `ratified` is a real field) · AM-4 ✓ (defects 10/12/13 fixed: every "(edit)"
target now exists) · AM-5 ✓ (T5b is §1.2 *identity*, inside the boundary) · **AM-6 resolved**
(ADR-0002, 2026-09-02; the arithmetic is re-checked at M0b against real counts — r2.15 item 8).

> **AM-6 pointer** *(r2.15 item 8, editorial).* **AM-6 is resolved by ADR-0002** (accepted
> 2026-09-02). What remains is not the decision but the **arithmetic re-check against real M0b
> records**, which cannot happen before curation — so: *"AM-6 resolved (ADR-0002); arithmetic
> re-checked at M0b against real counts."* It stays **non-blocking for M0 slice 1** — no task here
> depends on the group-size threshold — while **M5 pre-registration remains gated on the re-check**.
> Defect 24's fix means T15/T17 *measure* the `yes`/`no` populations, so the check runs against real
> counts rather than estimates.

## 7a · Amendment r2 → r2.1 — CTO rulings E-1…E-5 (dispatch #11, 2026-08-31)

Five rulings from the CTO on the P0.1 report, re-issued by the principal. **No scope change** — four
wording corrections and one config path. Each is recorded inline at the section it amends.

| Ruling | Section | Change |
|---|---|---|
| **E-1** RATIFIED | T1, T11 | Nine keys present; eight always non-empty; `commit_change_rationale` non-empty **IFF** `source_commit != audited_commit`. Resolves a genuine self-contradiction between T1's "all eight non-empty" and T2's requirement that the rationale be empty on an unchanged commit. **T11 sign-off unblocked against fixtures.** |
| **E-2** RATIFIED | S3 | Assert against the *parsed* config. The old done-condition could never fail — pytest's default `norecursedirs` already skips `.venv`. |
| **E-3** RATIFIED | S4 | `test_monotonicity` skip reason names the **M1 ODE solver**, its actual blocker — not slice-3 splits. |
| **E-4** RULED (defect) | S7 | Probe set extended to **nested** paths. A top-level-only probe does not test the rule that git cannot re-include a file beneath an excluded directory. |
| **E-5** RULED (**data-loss fix**), **refined @ #18** | S9 | DVC remote must be absolute and outside every git tree — the r2 relative url resolved *inside* the worktree, so `git worktree remove` destroyed the only copy of the snapshot. **Refinement:** the url lives in gitignored `.dvc/config.local`, not committed `.dvc/config`. Committing a literal home path disclosed the account name to a public remote and gave other contributors a silent empty success on push — the same silent-success class E-5 exists to prevent. |

**Approval provenance:** these amendments were dictated by the CTO's ratified rulings and re-issued
verbatim by the principal in-session on 2026-08-31 with the instruction to apply them and continue.
They were not authored by the agent. `plan-approval.md` is re-signed to `r2.1` on that basis; the
hash moves `737a8d9 → <r2.1>`.

---

## 8 · Scope check

This plan stops at the identity and barrier-panel layer: **29 CA tasks and 5 human tasks**
(r1: 13 CA / 4 H), roughly 2 hours of agent work and 2 hours of human work. **r2.36–r2.40 add M1
(§6a): 9 more CA tasks (S13, S14, T22–T27, T29) and 3 more H tasks (T20, T21, T28)** — see §6a's
scope note for why M1 alone doesn't wait on the items below, and the r2.37/r2.39/r2.40 amendments
inline for the defects the agent's read-before-implementing caught (S13/S6, T26's fixture question, and the
(alpha, k_sink) prior's home).

Three adjacent things are **deliberately not here**:

1. **M0b — curation of 80–100 chip records** *(range narrowed by principal 2026-09-02, AM-6 resolved:
   the active-learning pool is v3 and leaves the PoC's sealed allocation, making it three-way —
   δ-calibration / conformal calibration / locked test — at ~20 conformal points per group, two
   groups. The Mondrian claim stays conditional; §5E forbids marginal coverage in terms. Every
   coverage figure is reported **with its confidence interval, per group**.)** Human-only, needs a protocol document rather than a task list, and it is the project's critical path. Its own plan.
2. **M0c — the frozen evaluator**, and the model card that T17's block plugs into. Cannot be specified until the splits exist. Its own plan.
3. **ChEMBL, BindingDB, TDC, LINCS ingestion**, plus the §1.2 *data*-contract test and `mapping.tsv.gz`. One plan covering all four, after this one proves the pattern.

> **The next plan should be M0b, not the other ingestors.** The ingestion pattern is now proven
> and mechanical; curation is unproven, human-bound, and gates M5 and M6 both. Building more
> parsers first would feel productive and would move the actual completion date not at all.
> **This ruling stands for M2–M6 (§6b).** M1 is scoped in §6a as the one exception, because its
> data dependency (theta_priors literature + a handful of reference compounds) doesn't run
> through the ingestors plan or M0b at all — see §6a's scope note for the argument, not just
> the conclusion.

---

## Agent execution notes (AIADLC)

- **CA tasks (29, M0 slice 1)** — S1–S11, S11a, T3, T4, T4a, T5, T5a, T5b, T6, T7, T9, T10, T11, T12, T13, T15, T16, T17, T19. Each has a failing-test done-condition evaluable against committed fixtures. **Plus 9 in §6a's M1 slice (r2.36–r2.40)** — S13, S14, T22–T27, T29.
- **H tasks** — **T2, T1, T8, T14, T18** (five, up from four) in M0 slice 1. **Plus 3 in §6a's M1 slice (r2.36–r2.39)** — T20, T21, T28. These are blockers the agent must **escalate, not simulate**. T2 gates T1 and T4a; T1 gates T11; T8 gates T9; T18 gates T13; T14 gates T15; T20/T21 gate T23/T27 (M1); T28 gates T23. The agent builds the code and tests around them, leaves the human artifacts absent, and reports the blocked set at the boundary.
- **T18 is new and is a human blocker.** It exists because pinning "PoC compound set" to the PVR's curated 20–40 makes the roster a curation claim no agent may write.
- **The hard rule stands:** no agent-written biological numbers, no agent-created curated records or rosters, no agent edits to the frozen evaluator. T7's panel is drafted `ratified: false` **by design** — drafting accessions is allowed; ratifying them is not.
- **Fixtures are not human artifacts.** `tests/fixtures/*` exist so CA done-conditions can fail honestly while T1/T2/T8/T14/T18 are outstanding. They live under `tests/`, are never read by a pipeline path, and S5 asserts that.
