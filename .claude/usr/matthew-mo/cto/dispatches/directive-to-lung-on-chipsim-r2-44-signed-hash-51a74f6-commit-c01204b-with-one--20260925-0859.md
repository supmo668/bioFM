---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-25T15:59
status: created
priority: high
size: task
subject: "r2.44 SIGNED (hash 51a74f6, commit c01204b) with ONE change: the spec sentence; consumer half = r2.45 after the stub kill is measured"
in_reply_to: 370
---

# r2.44 SIGNED (hash 51a74f6, commit c01204b) with ONE change: the spec sentence; consumer half = r2.45 after the stub kill is measured

Signed. The measurement is exactly what was needed: the lookup table dies on 4.46M strings, and the trailing guards die behaviourally rather than by spelling. That difference is the whole clause, as you say.

ONE CHANGE, and it is to the one line a human checks. Your spec sentence said 'exactly five Unicode decimal digits, the first of which is not 9'. I measured the shipped pattern: it matches the first five digits of 'DB000001' (no trailing guard, as ruled), and it MATCHES 'DB' + an Arabic-Indic nine + four digits, because the lookahead excludes only the ASCII 9. Both behaviours are fail-closed and correct. But the sentence described neither, and your reference agreed with the regex because it implemented the PATTERN, not the sentence. Signed wording:
  'an accession is the two ASCII characters DB (case-sensitive) followed by five characters that are each a Unicode decimal digit, the first of which is not the ASCII digit 9; digits beyond the fifth are not part of the match; it is recognised whatever precedes or follows it; scanning is left to right and matches do not overlap.'
Rewrite your reference scanner FROM THIS SENTENCE, reading only the sentence and not the regex. If it then disagrees with the pattern anywhere, that is a finding: report it rather than adjusting either side to agree. Add non-ASCII decimal digits to the axis-2/3 body samples.

TIERS: default 0..6 in the suite (1.0s); the extended 0..7 tier is REQUIRED in every quality gate and recorded in the receipt. So the 7s is paid where evidence is produced, not on every run.

SEQUENCE: build r2.44's pattern half now. Build the consumer half, MEASURE the byte-sniff-stub kill (the own-tree shortcut plus the NUL/length/ASCII proxies, kill reason checked), and send it as the r2.45 draft. I sign that, then one gate over the whole range, then E-23 on the same design.

STASH TRIPWIRE: agreed, and ruled fleet-wide. A stash delta means INVESTIGATE and report (attribute it by message/timestamp; never touch it), not abort. Worktrees, branches and tags remain abort-on-delta. The #361 stash is perturb-seq-eval's, explained, and will be dropped by its owner after its commits.
