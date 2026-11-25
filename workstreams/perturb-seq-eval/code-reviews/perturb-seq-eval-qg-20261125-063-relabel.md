# Quality gate — merge of main, the published 0.6.2 on record, and the 0.6.3 relabel (2026-11-25)

Scope: `git diff origin/main...perturb-seq-eval-haca126-deposit` (base `c42ac57`). Approvals rows 43 (go to publish 0.6.2), 44 (token delivery), 45 (the self-contained manuscript is archived as 0.6.3).

## What the branch does

- Merges `main` (the self-contained rewrite) into the deposit branch. `main` keeps its row 42; this branch's rows 42 and 43 become 43 and 44.
- Keeps 0.6.2 recorded as published (Zenodo 10.5281/zenodo.24518637, Figshare version 8, built from `07a5e57b`), and says on every surface that it holds the wording before the rewrite.
- Relabels the manuscript now in the repository 0.6.3: a new version of Zenodo 24518637 and Figshare version 9, state file `publish.state.v063.json`. Prepared, not published. No venue call was made.
- Changes one clause in two manuscript sentences: "archived before this one" becomes "archived before version 0.6.2", because 0.6.2 discloses the error feedback and is itself an earlier archived version once this text is 0.6.3.

## Review

Four reviewers (code, security, design, test) and the scorer, threshold 80. The review window was bracketed and the tree was unchanged. UX pass skipped: the diff is not user-facing.

- Security: nothing above low. The guard retarget only grew the protected lists.
- Code: no path writes to a published record other than the one new-version request. Breaking each retargeted constant on purpose failed between 1 and 20 tests.
- Twenty findings went to the scorer. Nine scored 80 or more; all nine are fixed.

| Id | Score | Finding | Disposition |
|---|---|---|---|
| F1 | 80 | 24430429, the previous target, was not tested as refused | fixed, `5d3e906` |
| F2 | 88 | a Figshare version 7 base was not tested as refused | fixed, `7371f65`; the test fails when the guard also accepts 7 |
| F3 | 82 | "exactly one latest published release" not checked while 0.6.3 is unpublished | fixed, `88e142e` (two lines repaired in `56773e6`) |
| F4 | 82 | the new test's docstring was wider than its assertions | fixed, `0fa2f06` |
| F5 | 80 | "not published" was checked anywhere in the file | fixed, `6c18151` |
| F7 | 90 | a test name said v7 and asserted v8 | fixed, `86ee0db` |
| F8 | 88 | the `SUPERSEDED` tuple was read by no test | fixed, `b037ada` (removed) |
| F10 | 82 | the draft-id order check had no test (already so on `main`) | fixed, `56773e6`; the case fails when the check is removed |
| F14 | 85 | a test exemption described text that is gone | fixed, `3e872cc` |
| F9 | 65 | after a publish, the revised record's Figshare DOI was unchecked | fixed anyway, `fe86832` |
| F11 | 70 | "reuses or replaces" the stray draft: the submitter can only reuse or stop | fixed anyway, `bb903d4` |
| F12 | 60 | a dated SUBMISSION paragraph contradicted the new one | fixed anyway, `bb903d4` |
| F13 | 50 | Part 4 read as if the 0.6.3 DOI were reserved | fixed anyway, `bb903d4` |
| F6 | 50 | the unpublished branch of one test only checks inequality | rejected: the new test pins the version |
| F15 | 45 | root `CITATION.cff` has `month: 10` beside the new title | rejected: the value predates the branch and cites the concept record |
| F16 | 70 | `research/PUBLISHING_RUNBOOK.md` names old state files | not fixed here: outside the diff, stale since 0.6.2; reported to the CTO |
| F17 | 40 | `docs/hacp/perturb-seq-eval/publish-complete.md` stops at v0.6.0 | not fixed here: a Notion-mirrored page, already a CTO follow-up |
| F18 | 45 | row 45 says "main at c42ac57" | rejected: ledger rows are not edited; the row quotes the card |
| F19 | 20 | row 44 names the secret store | rejected: no value, id or path; row 3 already names it |
| F20 | 20 | internal ids in the repository | rejected: repository convention; none reaches a deposit |

Commits `88e142e` and `fe86832` each carried one line that did not parse (a shell escape written literally), so `tests/test_publish_deposit.py` did not collect between `88e142e` and `56773e6`, which repaired both.

## Not checked

- The PDF was not rebuilt after the manuscript clause change. The deposit build is step 4b, from the landed commit.
- No Zenodo or Figshare call was made, so the state of draft 24519260 was not re-read in this gate.
