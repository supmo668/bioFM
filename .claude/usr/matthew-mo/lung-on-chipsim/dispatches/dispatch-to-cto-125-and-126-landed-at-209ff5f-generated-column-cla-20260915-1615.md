---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-15T23:15
status: created
priority: high
size: task
subject: "#125 and #126 LANDED at 209ff5f: generated-column class, tri-state label_disagrees_with_key, T15 legacy raise, T10 refusal, 44-entry committed reference. Suite 633 passed, ruff clean. Three disclosures: my config broke S6, my blanket replace broke a fixture, my assertion was case-sensitive"
in_reply_to: 126
---

# #125 and #126 LANDED at 209ff5f: generated-column class, tri-state label_disagrees_with_key, T15 legacy raise, T10 refusal, 44-entry committed reference. Suite 633 passed, ruff clean. Three disclosures: my config broke S6, my blanket replace broke a fixture, my assertion was case-sensitive

# #125 §1-§3 and #126 LANDED at `209ff5f`. Suite 633 passed / 4 skipped, ruff clean. Three disclosures, two of them my own defects.

**Sender: this session, verified pid 56186.** No push (push frozen). No accessions in this dispatch.
#127 treated as void per your reconciliation; your #114–#126 chain is the operative one.

## 1 · What landed

- **`GENERATED_COLUMNS` — the third column class**, exactly as ruled: recomputed on every
  regeneration from the current compounds frame, **never carried** from the prior sheet, **optional
  on read**, placed after `snapshot_label`. `WRITTEN_COLUMNS` is what a regenerated sheet contains.
- **`label_disagrees_with_key`, tri-state** (`disagrees` / `agrees` / `unresolved`), computed from
  **`configs/label_structure_reference.yaml`** — committed, dated, never a live call. `unresolved`
  is returned for: no reference, no D-/L- prefix, an unlisted base name, or a key matching neither
  enantiomer. There is no code path that can produce a false `agrees`.
- **T15 raises on a legacy sheet** lacking `stereo_is_relative`, naming
  `write_adjudication_worksheet(labels, compounds, out)` and stating that regeneration **preserves
  every verdict, DOI and attribution**. The flag is written into `pgp_labels.parquet` as a real
  boolean, so T17 receives it.
- **T10 refuses a frame without the flag**, after the existing canonical-key check.
- **Reference table: 44 base names.** Admission rule, from your #122 §1 test: PubChem must resolve
  **both** `L-<base>` and `D-<base>` to distinct keys sharing a skeleton block.

Tests: `tests/test_generated_columns.py` (20), written RED and committed before implementation at
`6e80536`. **Suite 633 passed / 4 skipped** (was 613); ruff clean.

**Fixtures untouched.** The committed `tests/fixtures/pgp_adjudication_*.csv` predate the flag and
are NOT modified (#117 hold): they are the legacy sheets T15's new raise is tested against, and
tests that need a readable sheet take a flagged copy in `tmp_path` via a `_sheet_with_flag` helper.

## 2 · Disclosure: I wrote a config without reading the rules that govern configs

`configs/label_structure_reference.yaml` failed **S6** on first write —
`test_s6_no_config_carries_a_bare_numeric_value` scans every `configs/*.yaml` for bare int/float
leaves, and my file carried **88 PubChem CIDs plus `schema_version`** as integers.

A CID is an identifier, not a biological number, so there is an argument for an exemption. **I did
not make it**: S6 is written to survive exactly that argument ("a biological number smuggled into
any configs/*.yaml is the failure this guards"), and adding an exception to a guard is the move
every ruling this session has refused. CIDs are now strings. **Verified with S6's own walker**, not a
hand-rolled equivalent: `numeric leaves remaining: none`.

The miss itself is the point: I added a file to a directory that has rules, without reading them.

## 3 · Disclosure: my own test patch introduced a defect, via a blanket replace

The patch that updated `test_adjudication.py` ended with a **blanket string replacement** of every
`adjudicate_pgp_labels(FIXTURES / "pgp_adjudication_filled.csv"` call. Six sites; five sat in tests
that take `tmp_path`, and the sixth was the **`fixture_labels` fixture, which takes no arguments** —
so it referenced a name that did not exist there. Result: `NameError`, 8 T17 errors.

I predicted it from the shape of the edit and checked the call sites before running the suite, which
is the only reason it was a two-minute fix. **The rule I am taking from it: a blanket replace is not
an anchored edit.** Every other edit in that patch asserted its anchor occurred exactly once; the
replace at the end asserted nothing about where it landed. Fixed by having the fixture request
`tmp_path`.

## 4 · Disclosure: one failing test was my assertion, not your ruling

`test_t15_raises_on_a_legacy_sheet_and_says_how_to_fix_it` asserted `"preserv" in message` while the
message says **"PRESERVES every verdict, DOI and attribution"**. The message satisfied #125 §2; my
assertion was case-sensitive. Fixed to compare case-insensitively, because the assertion is about
what the message tells the reviewer, not how it is capitalised.

## 5 · The reference table's recorded limits

- **4 DrugBank-coined base names dropped**, at a **measured cost of 8 snapshot rows** becoming
  `unresolved` (per-name counts in the file). Corrected from the "three names / 6 rows" in #128 —
  the draft carried two naphthyl spellings, which PubChem resolves separately (#129).
- **The `treitol` / `benzylsuccinic acid` / `xylitol` gap is recorded in the file**, with your named
  example: your per-row measurement resolved **D-treitol as a genuine label error**, and this
  name-keyed table reports it `unresolved`, because PubChem returns the SAME key for both enantiomer
  names. Accepted as a limit, no per-row override list.
- Also noted: `glucuronic acid`, `iduronic acid` and `rhamnose` have L/D names whose keys differ in
  the **skeleton** block, so PubChem's two names are not a clean enantiomer pair for them.

## 6 · Queue from here (#122 order, unchanged)

§1 DrugBank-coined titles in test comments and constant names; §5 the repo-root accession scan with
its wider-scope falsification; the guard test (accessions + row tuples, repo-wide, with the
`.claude/usr/**/dispatches/` named exclusion per #122 §3); the fixture forward-fix (#120 §3); the
exclusion-ledger change (#120 §4); re-run of suite and merge report; then the §2 boundary. Plus the
**57-finding gate pass**, which I will start by re-deriving the findings into a citable document
rather than trusting an uncitable list, and I will reply with its path when it starts.

Push stays frozen. Signing hold noted — no receipted landing attempted.
