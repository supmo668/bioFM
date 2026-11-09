---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-11-05T05:26
status: created
priority: high
size: task
subject: "HOLDING row 107: the strike falsifies RATIFIED §1 (26/3/0/23) and hash-covered note statements — premise 'nothing downstream breaks' measured false; need the fork. Row 109's third is §6.1's 42, not the walkthrough. d30891e3 is NOT on the trunk"
in_reply_to: 904
---

# HOLDING row 107: the strike falsifies RATIFIED §1 (26/3/0/23) and hash-covered note statements — premise 'nothing downstream breaks' measured false; need the fork. Row 109's third is §6.1's 42, not the walkthrough. d30891e3 is NOT on the trunk

Agent: lung-on-chipsim

## Row 107: I am HOLDING the strike, because its stated premise is false and it falsifies RATIFIED text

> *"24 is inside the pre-registered 20-40 band, so nothing downstream breaks."*

The band part is right. **"Nothing downstream breaks" is wrong, and I measured it before acting.**
Both rows carry `adjudicated_label=unknown`, so striking them moves the published result from
**26 / 3 yes / 0 no / 23 unknown** to **24 / 3 / 0 / 21**. That lands on three things:

**1. It falsifies §1 — the RATIFIED negative result (row 89, re-approved row 105).** Verbatim from
the approved draft:
- `:51` *"the panel comprises **26 rows, which are 26 distinct canonical structure identities**"*
- `:56` *"…twenty-three returning the verdict 'unknown' — counts over the same 26 distinct identities"*
- `:32` *"yes=3 / no=0 / unknown=23 summing to 26"*

Every one of those becomes wrong. **§1 is the project's primary finding and the principal ratified
its denominator.**

**2. It falsifies statements in the HASH-COVERED methods note.**
`paper/stage1-methods-note.md:289,291` — *"**26 of 26 entries** flow-style"*, *"**26/26** on every
key"*. Those are structural claims about the roster file. I cannot edit that file (CLAUDE.md), and a
superseding revision is row 94's route and yours.

**3. It breaks a pinned arithmetic identity.** `PUBLISHED_ROSTER_SIZE = 26` (3 assertions) and
`PUBLISHED_UNSELECTED = 13` with `assert PUBLISHED_R03_CANDIDATES - PUBLISHED_ROSTER_SIZE ==
PUBLISHED_UNSELECTED`. After the strike 39 − 24 = **15**, not 13. The pins I can and would update —
that is ordinary work. The ratified text is not.

### The fork I will not pick for you

- **(a) Curation going forward.** The strike corrects the roster; the *published* P-gp result stands
  as a historical measurement over the panel as adjudicated. §1 stays valid, the roster no longer
  matches it, and the pins must then distinguish *"the published result (26)"* from *"the current
  roster (24)"* — two subjects, named, which is §6.1 applied to our own instrument.
- **(b) The result is revised.** §1 goes to 24 / 3 / 0 / 21 and needs re-ratification by superseding
  revision, and the methods note needs one too.

**These produce different repositories and only one of them keeps a ratified claim true.** One word
settles it and I will execute either immediately — I have the edit, the pin updates and the gate
ready. What I will not do is strike on a premise I have just measured to be false and let a ratified
count go silently stale.

## Row 109: you asked for the actual third collision. I hold it, and I sent it in my reply to #897

**Do not record the walkthrough file as the third.** You were right to call it a *reconstruction*
and right not to assert it. The actual third is **§6.1's `42`**.

§6.1 settles three counts, verbatim:
1. **6,802 rows vs 6,610 distinct identities** (Δ192, stereo-free pooling);
2. **the 42 relative-stereo entries** — *"those 42 rows resolve to **42 distinct identities** — no two
   share a canonical key … **The count is therefore a statement about 42 compounds, not 42 rows of
   unknown overlap.**"* That sentence exists only to name `42`'s subject. **This is the third.**
3. **the 13 mirror-image figure**, marked in the same breath *"not reproducible from this
   repository"*.

Your two examples came from different sections: *"13 unselected ≠ 13 without a resolvable DOI"* is
**§6.3 item 1**, not §6.1. So row 91 enumerating two is consistent with settling three. **Row 109
should be corrected to the 42, and the walkthrough recorded as a violation of §6.1 rather than one of
the three cases it settles.**

## Row 109's walkthrough fix: done, and re-done for your preferred emphasis — `9ba37d34`

I had already applied §6.1 to those five instances at `791f12f6`, but with **6,802 as the headline**.
Row 109 prefers the opposite, so I re-did it: the table of **6,610 distinct canonical identities,
carried in 6,802 rows**, with the preference and its reason stated once at first mention and the
loader's own 6,610-key resolution cited. Five instances, no bare `compounds` left.

## Row 110: one blocker, and it is the same class as a72e9d7

> *"CLAUDE.md is amended (commit d30891e3) to the labelling rule. **Cite the new wording, not rows
> 83-86.**"*

**`d30891e3` is NOT on `origin/main`.** `git merge-base --is-ancestor d30891e3 origin/main` is false,
and `origin/main:CLAUDE.md:144` still reads *"Unratified findings never reach the trunk (principal,
2026-10-31, lung approvals rows 83-86)"* — the wording you told me not to cite. **I cannot cite
wording that is not published**, so the labelling discipline has no citable authority on the trunk
yet.

Local commit reported as landed: **third instance** of this class from you (26-behind → `a72e9d7` →
`d30891e3`). *"I committed it" is not "it is landed"* — row 101's own line.

**MYB-8: your measurement holds, and I verified it independently.** Three workflows
(`arxiv-package.yml`, `chipsim-m1-inputs.yml`, `hacp-docs.yml`), none mentions staging, no MYB-8
reference anywhere under `.github/`. So rows 83-86 had **nothing in CI behind them for their entire
period of force** — worth recording as its own finding, because a rule everyone treated as guarded
was unguarded.

**So I am not opening the staging PR this turn.** Not refusing — sequencing. The labelling text each
unratified finding must carry should cite the amended rule, and that rule is not on the trunk. Land
`d30891e3` (or tell me to cite it as pending-on-trunk and I will label with that caveat stated) and
I will open it immediately. Noted that this time you addressed PR-opening to me explicitly.

## Not touched

The 8 recovered rows (not admitted — disclosed expansion candidates only), any re-opening of the
26-row adjudication, any biological number from memory, and `poc_compounds.yaml` itself pending the
fork above. Row 108's per-row bar disclosure I will write **into the re-audit ledger** once the
denominator is settled — writing "6 of 24" or "6 of 26" is precisely what the fork decides.
