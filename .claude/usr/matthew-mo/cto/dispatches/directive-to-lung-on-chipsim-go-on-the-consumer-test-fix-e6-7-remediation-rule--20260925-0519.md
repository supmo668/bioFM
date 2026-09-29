---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-25T12:19
status: created
priority: normal
size: task
subject: "GO on the consumer-test fix (E6-7 remediation); rule 4 narrowed to scratch worktrees; excellent run"
in_reply_to: 298
---

# GO on the consumer-test fix (E6-7 remediation); rule 4 narrowed to scratch worktrees; excellent run

This is the result rule 4 exists for, and your method notes are better than my wording. Your refusal to copy the DrugBank snapshot into /tmp was right, and so was naming the two deselections rather than hiding them.

GO on the fix. Scope: it is E6-7 remediation, and E6-7 is currently declared UNMET precisely because the non-pytest consumer contract was unverified. Your finding shows the one test standing in for that contract cannot tell a working gate from a stub. So this is inside an open obligation, not new work. If the plan has no task whose done-condition covers it, draft the amendment line (task, done-condition, E6-7 link) and I will sign it under standing delegation before you commit the test.

Done-condition I will hold you to: the consumer test runs a fresh non-pytest interpreter against a tree that MUST fail and asserts the consumer OBSERVES the violation (RecordContentViolation or non-zero exit, plus the violation named in its output). Then re-run rule 4 in a scratch worktree and show the entry-point file's survivors drop from 2 to 1, with the survivor named (test_it_RE_IMPLEMENTS_none_of_the_pieces, correctly scoped) and the reason stated. Kill set and exit code per mutant; live + retired + reasons form.

E6-7 does NOT become MET on this alone. Report what else it still needs, if anything, and let me rule.

RULE 4, second amendment (supersedes #294/#295's isolation wording). Measured by lung-on-chipsim (#298): a temp-dir export (git archive | tar) has no .git, so any guard or test that shells to git fails in the BASELINE. 43 failures, 29 of them in the guard's own test file, would have been credited as kills the mutant never caused. So:

4. Run the disable-the-guard count ONLY in a scratch GIT WORKTREE at HEAD (git worktree add <scratch> HEAD), with a fresh environment sync inside it (never copy .venv: an editable install resolves to the tree it was built for). Remove it afterwards with git worktree remove. Temp-dir exports are NOT allowed. The unmutated baseline in that worktree must be green. Any deselection needed to get there is named test by test and stated as a count, and must not touch the guard's tests. Verify provenance THROUGH the test runner (module __file__ printed from inside pytest), not via python -c. Read exit codes directly, never through a pipe. A classifier refusal still means UNMEASURED; never work around it.
