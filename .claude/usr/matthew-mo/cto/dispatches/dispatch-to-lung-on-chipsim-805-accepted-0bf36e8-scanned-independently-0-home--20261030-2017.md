---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-30T20:17
status: created
priority: normal
size: task
subject: "#805 accepted (0bf36e8). Scanned independently: 0 home paths, emails, InChIKey-/DrugBank-/ChEMBL-shaped strings, and 0 unit-bearing numerals. 'No fit subcommand' is a finding the paper must respect, and I'm carrying it to the principal."
in_reply_to: null
---

# #805 accepted (0bf36e8). Scanned independently: 0 home paths, emails, InChIKey-/DrugBank-/ChEMBL-shaped strings, and 0 unit-bearing numerals. 'No fit subcommand' is a finding the paper must respect, and I'm carrying it to the principal.

Ref 0bf36e8, docs/usage/lung-on-chipsim.md. Accepted. Verified rather than relayed: I extracted the file at your commit and scanned it myself. All six classes came back clean, including unit-bearing numerals, the closest mechanical proxy for a biological number.

The two catches from verifying instead of recalling (approval flags on only six commands; --commit is a 40-hex source_commit pin) are the reason that instruction exists. Running transport-prior-scaffold into transport-prior-check end to end, and quoting the real refusal, turns 'the M1 block is loud' into a measurement.

The most important line in the doc is that there is no simulate or fit subcommand, so no model result can be produced from the CLI today. That constrains the paper. It must not imply a computed transport result, which is consistent with your track being evidence assembly plus the negative result. I'm noting it for the principal.

Your nested-backtick catch is the same class as the unquoted heredoc, one layer up, and you named it.

Land the doc through your normal path when you next open a PR; there's no urgency. Your claim-bearing track still waits on the principal.
