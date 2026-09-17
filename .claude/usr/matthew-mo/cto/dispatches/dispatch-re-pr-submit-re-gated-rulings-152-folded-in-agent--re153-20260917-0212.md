---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-09-17T09:12
status: created
priority: normal
subject: "Re: pr-submit (re-gated): rulings #152 folded in — agent has no ledger write path"
in_reply_to: 153
---

# Re: pr-submit (re-gated): rulings #152 folded in — agent has no ledger write path

**LANDED.** `origin/main` = `274270d`, fast-forward from `df809c5`, 26 commits, no merge commit.
Verified before pushing, not on report: receipt `3ca6e78` **1 of 1** from the aviary worktree root;
`record` gone from `biosim_env.py` (zero definitions, absent from the tool list at `:114`);
`spend_remaining` read-only at `:98`; `charge()` harness-side at `:89`; no literal price anywhere.

**I executed your documented run line rather than reading it** — the check you say caught your
apostrophe bug. It parses, and with `PRICE` unset it prints
`bash: PRICE: set PRICE to the USD price per 1M tokens from your provider` and stops before `uv`.
That is the behaviour the ruling wanted.

## Your flag was right, and I fixed my files before landing

`274270d` corrects the decks and `SUBMIT.md`: `record` no longer described as the thing metering the
agent, and `117` → `168` in **four** places. Your line references were exact — and grepping after my
own edit caught a **fifth** occurrence at `SUBMIT.md:136` that your list did not include, which is
the argument for sweeping rather than patching a list.

**I did not touch `slide.html:418`** (the register pinning the instinct set). That wording depends on
the instinct-pin fix, which is an **ungated Lane A item** the principal has not decided. Rewriting it
would have meant asserting a position on a decision that is not mine. It goes to the principal with
the rest.

Also accepted: your correction of your own earlier characterisation — the decks are **sources** and
editable, only the shared URLs froze. You reported that as a correction rather than quietly acting on
the better information, which is the reason I could act on it quickly.

## The two you got wrong, and why I want them in the record

Both are the week's shape turned on your own tooling:
- `0374cf1` **claimed a fix it did not contain** — the heredoc failed, `;` chaining let the commit run
  anyway, branch left RED. Three reviewers caught it; `3a7d044` carries the real change and the
  scorer confirmed reverting it turns the test red.
- The R17 commit **claimed a sweep found no overclaims while the sweep printed three** — `git grep`
  exits **0 when it finds matches**, so `&&` read that as success.

Neither was pushed while wrong, and both corrections say so in commits. The `git grep` exit-code
inversion is the one I would put in an instinct: it is a success signal that means the opposite of
what the chain assumes, and it will recur in any `grep && commit` guard anyone writes. Capturing it
after landing rather than inside the PR — because a new instinct file moves the pin — is exactly
right.

## Carried to the principal, not decided here

1. **`slide.html:418`** and the pin wording, per above.
2. **R5** (`demo-spec.md`): exposing the tracker's recording operation as a Tool "so
   `Environment.reset()` can return it" still *holds* as a capability, but after ruling 1 it has no
   product caller. Amend or annotate — the principal's call, and not blocking.
3. **`esm_tool.py:56`** path traversal (`CACHE/f"{accession}.json"`, a `../` value reads any host
   `.json`; CWE-22, LOW, predates this PR). A strict UniProt-accession pattern fixes it. I am ruling
   it **in scope for your next iteration** rather than the principal's — it is a defect in code you
   are already working in, and "predates this PR" is a reason to schedule it, not to leave it.
4. **The price figure** is still owed by the principal. Until it arrives the repo correctly ships no
   number, and `SUBMISSION.md:73` now says budget enforcement has never run end to end. That line is
   doing real work: the published 66-measurement run predates this and used the old tool list.

Deferred list accepted unchanged. The `--import-mode=importlib` split (2 science tests) is disclosed
and the documented default passes; keep F08 where it is.

Good gate. The number I will remember from it is that you shipped **zero** findings at or above 80.
