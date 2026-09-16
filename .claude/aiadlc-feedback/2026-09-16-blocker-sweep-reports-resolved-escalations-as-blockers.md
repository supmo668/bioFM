# `blocker-sweep` reports RESOLVED escalations as BLOCKERS — 25 of 26 lines were noise

**Tool:** `tools/blocker-sweep` (plugin 0.56.0), both one-shot and `--watch`
**Severity:** medium — it does not lose information, it buries it

## What happens

On its first `--watch` cycle for the CTO of this repo, the sweep emitted **26 `BLOCKER` lines**.
**Twenty-five of them are marked `resolved` in the same line it prints:**

```
BLOCKER lung-on-chipsim #131 escalation/high/read      <- the only real one
BLOCKER lung-on-chipsim #128 escalation/high/resolved
BLOCKER lung-on-chipsim #124 escalation/normal/resolved
BLOCKER lung-on-chipsim #121 escalation/high/resolved
... 21 more, all /resolved
```

It then emitted a matching `ESCALATE principal #<id>  (agent blocked — clear it or flow up)` line
for each, including the resolved ones — i.e. it proposes escalating 25 closed items to the human.

## Why this matters more than ordinary noise

The tool's stated contract is that it "stays quiet unless a blocker exists, so it only wakes you
when your own agents have something that isn't clearing". That property is what makes its silence
readable — the same trust contract the dispatch monitor documents. Here the signal-to-noise is
**1:26 on the first cycle**, and it grows monotonically with the workstream's history, because
nothing ages out. A genuinely blocked agent is one line among twenty-six identical-looking ones.

This is the failure mode the plugin's own guidance warns about elsewhere: a check whose output
cannot distinguish "needs action" from "already handled" trains the reader to skim it, and the next
real blocker is skimmed with it.

## Stronger evidence, measured an hour later: 27 lines, ZERO actionable

After acting on the only two genuinely open items (`#131`, `#132` — both `read`, both since
resolved), the sweep was re-run:

```
$ blocker-sweep | grep '^BLOCKER' | grep -v '/resolved'     # genuinely open
(no output)
$ blocker-sweep | grep -c '^BLOCKER'                        # lines printed
27
```

**Twenty-seven `BLOCKER` lines, none of them open**, each with a matching
`ESCALATE principal #<id>  (agent blocked — clear it or flow up)` recommending that a closed item be
escalated to the human. The tool's self-nudge header reads "never rest until ALL is clear" — a state
that, with this filter, can never be reached: resolving an item does not remove its line.

## Repro

1. Resolve several escalation-type dispatches (`dispatch resolve <id>`).
2. Run `tools/blocker-sweep` (or `--watch`) as the coordinator those escalations were addressed to.
3. Every resolved escalation is still printed as `BLOCKER …/resolved`, with an `ESCALATE` line.

## Root cause (from the output, not the source)

The blocker query appears to select escalation-type dispatches by **address and type**, without
filtering on `status`. The status is fetched — it is printed in the line — so the filter is
available and simply not applied.

## Suggested fix

- **Exclude `status=resolved` from the blocker set.** An escalation that has been resolved is, by
  definition, cleared.
- Keep `read` in scope: `#131` above is `read` but not resolved, and it *was* a real blocker
  awaiting a ruling — that is exactly the case the tool should surface.
- If the history is wanted, print it under a separate non-actionable heading
  (`recently cleared: 25`), never as `BLOCKER` with an `ESCALATE` recommendation.

## Note on a related strength, so the fix does not remove it

The unfiltered stale-unread query in the same tool is valuable *because* it carries no address
filter — it catches mail that identity/casing bugs hide from the filtered inbox gate. Please do not
"fix" this by adding filters there. The defect is the missing **status** filter on the blocker set,
not the absent **address** filter on the stale-unread sweep.
