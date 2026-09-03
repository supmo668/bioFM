# QGR Stage-1 findings — T7a re-gate (model card + E-3/E-4 hardening)

Base: `origin/main` @ `228d354`. Gate opened at `c7018b7`.

Two reviewers, run sequentially against the T7a work. Both reports were recovered
verbatim from their session transcripts before this file was written; nothing here
is reconstructed from memory. Source transcripts:

- code review — `agent-a709a81ea1938f5f5.jsonl` (15 findings, all reproduced by
  execution, repro scripts named in the report)
- test review — `agent-a2544ddc586b9191e.jsonl` (14 findings, mutation-based)

## Integrity caveat on Hash A — stated because it weakens the receipt

Hash A describes the tree at `c7018b7`, which is what the **code** reviewer read.
It does **not** cleanly describe what the **test** reviewer read: that agent ran
for ~25 minutes while I was applying the code reviewer's fixes, and reported
observing the tree change under it (`403 passed` → `402 passed, 1 failed` →
`405 passed`). Its findings are therefore anchored to a moving state, and a
single Hash A cannot attest to what it reviewed.

Nothing in its report turned out to depend on the drift — every finding I acted
on I re-verified by mutation against the current tree, and those verifications
are recorded in the triage. But the receipt would overstate its own coverage if
this were left implicit, so it is stated here instead.

---

## Reviewer: code (15 findings)

| # | Sev | Location | Finding |
|---|-----|----------|---------|
| 1 | CRITICAL | `eval/provenance_block.py` | `render_panel_ratification` printed `ratified_panel_sha256` **without verifying it**. A panel with one `face` flipped after sealing — the exact tamper the seal detects — rendered a byte-identical card, four lines above the sentence claiming the seal detects modification. The loader refused the same file. |
| 2 | HIGH | `eval/provenance_block.py` | `ratified: true` with empty `ratified_by` rendered `**Status: ratified** (no ratifier recorded)`, contradicting `pgp_label.py` ("an unattributable ratification is not a ratification"), which refuses it. A panel with zero supporting evidence got the word "ratified" in bold. |
| 3 | HIGH | `journal.py` | The `configs_real != root_real` disjunct exempted `ln -s . configs`, restoring the pre-E-3 bound. Reproduced: snapshot walked the project root and copied `deploy/prod-credentials.yaml` into the published record. |
| 4 | HIGH | `journal.py` | E-3 was applied to the snapshot loop only; `_resolve_seed` still used `project_root.resolve()`. Two different boundaries for the same directory in the same module. Reproduced: `panel-seal` opened and parsed an in-project file the boundary declares out of bounds. |
| 5 | HIGH | `journal.py` | A FIFO or socket named `*.yaml` under `configs/` was **silently skipped** — the one failure the walk exists to prevent, occurring inside the walk. Also: `_open_verified_config`'s `S_ISREG` guard could never fire on a FIFO, because `os.open` blocks before `fstat`. |
| 6 | MED-HIGH | `pipeline.py` | `sys.stdin.readline()` had no timeout: an open pty with no writer blocks indefinitely. Reproduced with a real pty. Backgrounded under an inherited controlling terminal it stops on SIGTTIN — no output, no exit code. |
| 7 | MEDIUM | `eval/provenance_block.py` | Three degradation defects: non-mapping panel raised bare `AttributeError` (sibling raises `RuntimeError`); missing file/directory raised raw OS errors; an **absent** `ratified` key rendered "ships `ratified: false`" — a positive false statement about a field that is not there. |
| 8 | MEDIUM | `pipeline.py` | Docstring claimed "removing the seal line bypasses the check entirely". False since `load_ratified_panel` began refusing an unsealed ratified panel. An under-claim that a guard does not exist is the same defect class as an overclaim. |
| 9 | MEDIUM | `pipeline.py` | `"Nothing was written."` is false — `main` journals the invocation before dispatching, and fails closed if it cannot. Recording the aborted attempt is correct; denying it in the operator-facing message is not. |
| 10 | MEDIUM | `pipeline.py` | The prompt went to **stdout** with `end=""`, concatenating with the success line; a caller taking `stdout.splitlines()[0]` gets the prompt banner. |
| 11 | MEDIUM | `journal.py` | The dangling-symlink branch misdiagnosed any link to a non-regular file: `configs/dev.yaml -> /dev/null` reported "broken symlink — names a config that does not exist". The target exists. |
| 12 | MEDIUM | `eval/provenance_block.py` | `panel=None` default, and **no production caller of `render_data_provenance` anywhere**. The limit statement is unreachable today, and the realistic failure is a card published with the bounding paragraph silently absent because a kwarg was forgotten. |
| 13 | LOW | `eval/provenance_block.py` | `ratified_by` interpolated into a markdown code span unescaped; a backtick in the value breaks the span and lets the remainder render as body text. |
| 14 | LOW | `eval/provenance_block.py` | A non-hex seal rendered as a plausible digest: `true` → `` `True…` ``, `abc` → `` `abc…` ``. The ellipsis announces truncation of 64 hex characters that were never there. |
| 15 | INFO | `pipeline.py` | Ruling requested on `strip().lower()`: reviewer judged it correct and would not change it. `strip()` is load-bearing (a pty in canonical mode delivers `seal\r\n`); `lower()` cannot help an attacker against a published literal token. |

## Reviewer: test (14 findings)

| # | Sev | Location | Finding |
|---|-----|----------|---------|
| T1 | CRITICAL | `tests/test_journal.py` | Answered the open half-(b) question: the guard **is** load-bearing. My mutation test passed on a coincidence — the fixture was named `env.yaml`, the one filename `_resolve_seed` independently opens, and that call site was still on the old bound; a *different* guard raised a message that happened to share the matched substring. Instrumented proof that the exfiltration had already completed into staging before that raise. |
| T2 | CRITICAL | `tests/test_provenance.py` | `test_card_never_claims_the_seal_proves_authorship` **does not detect overclaiming**. Four presence-only substring checks; a card rewritten to claim the seal proves a human checked every accession satisfies all four ("does establish who" contains `establish who`; "not authentication in the pedantic sense" contains `not authentication`). Whole suite stayed green. Its docstring delegated the negative half to a scan whose file list did not include the card module. |
| T3 | CRITICAL | `tests/test_journal.py` | The negation scan is bypassed by **implicit string concatenation**. It collapses `\s+` but not the `" "` seam, which is the dominant wrapping style in the files it governs. Demonstrated: an overclaim split across a seam printed to stderr verbatim while the scan passed. |
| T4 | HIGH | `tests/test_panel_seal_tty.py` | Three E-4 tests used a module-level helper instead of the fixture, lost the `CHIPSIM_PROJECT_ROOT` redirect, and wrote agent-authored `panel-seal` records into the **real** Constraint (4) audit trail. 86 records, 100% from those tests. |
| T5 | HIGH | `tests/test_panel_seal_tty.py` | `assert "ratified_panel_sha256" in panel.read_text()` is satisfied by an untouched file. A `panel-seal` that never called `seal_panel` passed. Verbatim regression of a defect a sibling test's own comment records as already fixed once. |
| T6 | HIGH | `tests/test_panel_seal_tty.py` | Byte comparison is insufficient: a seal that writes, copies the result to a sidecar, then restores the original bytes passed every test. Also, re-sealing the fixture correctly would make two tests permanently green regardless of behaviour. |
| T7 | HIGH | `chipsim/pipeline.py` | Live: `select` raises `TypeError` for an object with no `fileno`, uncaught — suite red. |
| T8 | MEDIUM | `chipsim/pipeline.py` | The read's `except` handler returning `""` was untested; mutating it to `"seal"` (Ctrl-C ⇒ consent) survived the suite. |
| T9 | MEDIUM | `tests/test_panel_seal_tty.py` | Neither refusal test can tell which gate refused — both return 2. Removing the `_stdin_is_interactive` patch left both green, refused by the TTY gate, never reaching the confirmation read they are named for. |
| T10 | MEDIUM | `tests/test_panel_seal_tty.py` | `_FakeStdin(answer="seal\n")` default **consents** — wrong polarity for a fail-closed module. Plus a now-false docstring: the TTY test clears two gates and names one. |
| T11 | LOW | `chipsim/pipeline.py` | `.lower()` untested; dropping it survived. |
| T12 | LOW | `tests/test_provenance.py` | `assert "NOT RATIFIED" in text` is case-sensitive: brittle against harmless rewording, blind to hostile rewording. |
| T13 | LOW | `eval/provenance_block.py` | Confirms code-review #12 independently: deleting the panel wiring kills nothing. |
| T14 | LOW | `chipsim/journal.py` | The directory-walk half of bound (a) is unproven: reverting the argument to `project_root.resolve()` survives all tests. Near-equivalent — still refused, but by the per-file gate, not the walk. |
