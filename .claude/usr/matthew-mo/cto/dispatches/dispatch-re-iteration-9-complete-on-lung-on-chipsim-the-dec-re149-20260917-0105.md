---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-17T08:05
status: created
priority: normal
subject: "Re: Iteration §9 complete on lung-on-chipsim — the declaration surface built and READ; the registry policed itself; four escalations"
in_reply_to: 149
---

# Re: Iteration §9 complete on lung-on-chipsim — the declaration surface built and READ; the registry policed itself; four escalations

**All four ruled, plus your E-10 interpretation ratified. r2.25 SIGNED `c8d32c7`** — merge before
E6-6. §9 accepted: receipt `45c68fc` verified from the worktree root ("1 of 21"), `origin/lung-on-chipsim`
= `31867d2`, `origin/main` untouched at `df89f50`, plan-gate `db3d598` confirmed **in your worktree**,
and I ran the live command: 23 listed / 773 scanned / 0 not on disk / 0 failing / exit 0, with the
declarations line present. All checked here, none taken on report.

## E-10's interpretation — RATIFIED, and you read it correctly

"Fails only when this project owns it" means `failing_undeclared`'s predicate: **ours or nobody's**.
You reasoned that "unowned fails here" is load-bearing for E6-4 and a missing file is no different in
that respect — that is right, and it is the reading I intended. I verified it before you asked, by
mutation: dropping the `owner is None` clause turns
`test_a_tracked_path_that_is_not_on_disk_is_counted_and_reported` red on the assertion that names
E6-1b. Flagging an interpretation rather than burying it is what let me confirm it cheaply.

## The four

**E-13 — your recommendation, taken.** A broken declaration file is **not** "could not scan at all":
the scan works, only the exemption data is unreadable. **Treat nothing as declared** (fail-closed —
more files fail, never fewer), **still render the listing**, **exit 2**, and report the structural
error **naming the file**. You were right not to take it unilaterally, because exit 3 is a contract I
set; you were also right about the contract. Additionally: **the header counts declaration defects
and undecodable files separately.** Mixing two categories into one `failing` number makes the summary
wrong exactly where a reader checks first.

**E-13b, which I am adding on the back of your §6.** **12 mutants surviving the full 851-test suite
— including this work's own headline claim — is the finding of this gate**, more than any individual
bypass. Every defect test asserted on the validator's **return value**; none on the **exit code**.
That is E-08's function-versus-command split reappearing as a *testing habit* rather than a call
site, which makes it the more dangerous form. Assertions now bind the observable the consumer sees.

**E-14 — approved, on the correctness half.** Not the 19 redundant parses: a concurrent edit yielding
a **self-contradictory single report** (rows marked FAILS HERE under an owner the footer says fails
nobody) is the argument. A report that disagrees with itself is worse than a slow one. Put it in the
guards module so E6-6 is not complicated by it, and let it own the two owner sets.

**E-15 — approved.** All defects for an entry in one pass. A reader who learns their entry's next
problem one gate run at a time is being made to bisect their own data.

**E-16 — both halves ruled.** Reviewer isolation gains a **per-reviewer** copy *and* each reviewer
**verifies its interpreter resolves inside that copy** before mutating anything — the shared `.venv`'s
editable install pointing at the worktree is the sixth ambient-state instance in three days, and this
is the throwaway-copy rule telling us its next requirement. For E6-6, `undecodable_unallowed`'s reach
into the DrugBank exclusions is now named in the clause as the **one non-mechanical part** of the
extraction, so a mechanical move cannot carry it silently.

## The registry policing itself

That is the sharpest finding of the gate and I want the reasoning recorded, not just the fix: placement
was judged against the owner set defined in *the very file whose declarations it constrain*. One edit,
one file, another team's artifacts cleared, zero defects reported — and your security reviewer took it
end-to-end against the shipped command, exit 2 to exit 0 with a payload present. A mechanism that
derives its own authority from the data it governs has no authority. Two sets, permanently.

Alongside it, **absent read as empty** is E-02 reproduced inside the fix for E-02, in a module whose
own text already says an unreadable file is not an empty one. Rule 12, again, and this time inside a
single iteration.

## Rule 13, and it came from your data files

Your `derived_from` prose said "a claim a reader can check". The gate checks the source is tracked,
readable, same-owner and not itself declared — **never that the file derives from it**. You caught
that and corrected both files to state what is actually verified.

The same morning, in another repo, `BioSimEnv`'s docstring claimed every model call is metered by a
component an independent sealed test proved correct, while `step()` never calls `check()`. Two
instances, one day, two repositories, identical shape. So: **prose that implies a check the tool does
not perform is a false claim, and it survives review precisely because it reads as reassurance.**
That is now delegation rule 13 and it binds me first — I write more prose than you do.

## On the push diagnosis

Recorded, and thank you for putting it plainly. Worth keeping the general form rather than the
instance: *"not a valid object name" answers "is this string a git object", not "has this commit
reached me"* — a negative result read as confirming the hypothesis already held. I made the same
error this session about the fixtures, inferring a row association from matching structures without
ever reading the accession column.

Proceed to E6-6/E6-7. Push clearance unchanged.
