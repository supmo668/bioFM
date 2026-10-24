# A fix is verified against the thing that was changed, not against the property the claim names

**Short methods note — Stage 1 closure, lung-on-chipsim (ruling A4, approval-log row 65)**

**Author of record:** the principal (ratifies under the T8 pattern).
**Drafted by:** biofm/matthew-mo/cto, from `workstreams/lung-on-chipsim/qgr/stage1-closure.md`.
**Status:** **RATIFIED 2026-10-20** (principal, verbatim: "approved"), after §4's re-derivation was run and its failure corrected in §4 below. Earlier: content approved 2026-10-18.
**AMENDMENT RATIFIED 2026-10-23** (principal, verbatim: "Ratify instance 11 only, hold 12 and 13"), covering the §3.6 admission of instance 11 and the §3.5 narrowing. **Scope ruled to ONE instance:** two further instances were measured and offered the same day and were **deliberately NOT admitted** — approvals rows 42 and 43 hold them. §3.3 publishes a floor, so the enumeration below understates the measured population by two **by ruling, not by omission**, on the same scope discipline row 37 applied.
**SECOND AMENDMENT RATIFIED 2026-10-24** (principal, 1B1 grill, four recorded rounds): three instances
admitted at **§3.7** completing the instrument-failure taxonomy; one further occurrence recorded at
**§3.6** as a *recurrence* and deliberately **not numbered**; a **third check** added; and §4's single
pin **split in two**. Scope was expanded from the one-instance discipline of rows 37 and 45 **on an
explicit ground**: these three are not three tally marks but one coherent set, and published together
they argue something that drip-feeding them could not.
**Superseded status line:** §4's own rule
requires every figure re-derived and the pin updated at the moment of ratification. Venue (§7) still open.

**Provenance of the approvals, disclosed because it cannot be verified from here.** The rulings arrived
**through the lung-on-chipsim agent's session** (dispatch #675), not through this one. The CTO cannot
independently confirm them, so they are applied as a **work instruction** and every change below is
reversible — the same treatment the agent gave a principal ruling it received through the CTO
(approval-log row 29). If any selection below is not what was chosen, say so and it is reverted.
**Draft due:** 2026-10-17 (row 65). **This draft: 2026-10-18 — one day late.**

**TWO PINS, split 2026-10-24 — because one line was doing two jobs.** §4's own rule is to *"pin its
measurements to a revision **of that process**"*, and this note previously carried a single pin covering
both its prose and figures measured over a different artifact. They move independently:

- **This note's own text:** `a38f161` (bioFM `main`), re-pinned at this amendment. Previous pins
  ~~`d578274`~~ → ~~`bb5d699`~~ → ~~`59a5210`~~.
- **§4's figures:** the approval log at **`e574e79`**, its last content-changing revision. **Unchanged by
  this amendment**, which is the point of separating them — a prose-only edit must not move a pin that
  implies the figures were re-measured. Each measured claim below is pinned to the revision named beside it. **This pin is stale by construction** — see §7 item 6: ratification
re-derives every figure and updates it. Per §4, **every figure in this note must be re-derived at the
moment of ratification, and the pin updated**, or the note commits the defect it documents.

---

## 1. The claim

> **A fix is verified against the thing that was changed, not against the property the claim names.**

**At least fourteen** instances were recorded, dated, with named authorship — nine over four quality-gate
rounds on one branch between 2026-09-29 and 2026-10-02, a tenth dated 2026-10-08 (§3.2), an eleventh dated 2026-10-23 (§3.6), and **three more dated 2026-10-23/24 (§3.7)** which together complete a taxonomy of how an instrument can be wrong. A **fifteenth occurrence is recorded but deliberately NOT numbered** — it is a *recurrence* of §3.6's own published check rather than a new mechanism, and §3.7 explains why that distinction is the finding. The
enumeration is a **floor, not a count** (§3.3): discovery here is reader-dependent, so the honest claim
is *at least* this many. The interesting property is not the count. It is that
**repair is one of the mechanism's vectors**: fixing an instance is itself an occasion for the next
one, because the fix is naturally verified against the thing the fixer just touched.

This note publishes the mechanism and its instances. It deliberately publishes **no claim that the
mechanism was solved**, because it was not: the branch closed at the scope reached, with no quality-gate
receipt, nothing pushed, and the branch not landed (approval-log rows 58 and 61).

## 2. Why this is a mechanism and not a list of mistakes

Three properties distinguish them.

**It survives its own repair.** Instances 5 and 6 were both introduced by the repair of instance 4 —
6 on the same day, caught before commit.

**It is indifferent to who is reasoning.** It was committed by the implementing agent, by its
reviewers, and by the coordinator who wrote the rule against it. Two instances were authored *while
their author was describing the mechanism in the same document*.

**Instruments barely catch it.** Of the ten, **one** was first caught by an instrument, and that one
only during the final gate, when `claims-vs-records.py` refused two numbers the author had just
written that no record emits. Every other instance was found by a **reader** — a reviewer, or the
author re-reading their own work. A 1,257-test suite was green across nineteen independent findings.

## 3. The instances

Each row states what was verified and what the claim named. The gap between those two columns *is* the
mechanism.

| # | date | introduced by | what was verified | what the claim names | disposition |
|---|---|---|---|---|---|
| 1 | 2026-09-29 | the **creation** of `redact-records.py` | that a refusal happened | *which* refusal | repaired 2026-09-30 (C-2) |
| 2 | 2026-09-29 | the **repair** of blocker 4 | that the marker carried `raises=` | that only the *registered divergence* is accepted | repaired 2026-09-30 (C-3) |
| 3 | 2026-09-29 | the **repair** of the round-1 scope finding | that `differences()` still reported a change | that each entry *is the digest of its own line* | deferred (R-05) |
| 4 | 2026-09-29 | the **repair** of the round-1 H4 finding | that the glob reached more files | that the measured surface covers *the classified scope* | repaired 2026-09-30 (C-1) |
| 5 | 2026-09-30 | the **repair of instance 4** | that H4 now cites the current record | that claims cite current records | repaired 2026-09-30 (H-7) |
| 6 | 2026-09-30 | the **repair of instance 4** (same day, pre-commit) | that the globs reached the classified roots | that the surface *equals* the scope | repaired same day |
| 7 | gate 9 | the repair H-10, for this exact error | that the figure was "recomputed from the log" | that it is recomputed *per run*, not once | re-broke itself |
| 8 | gate 9 | the repair C-3 | that a bare `assert` can no longer impersonate the divergence | that **nothing** can — a subclass or alias still can | class open (S-09) |
| 9 | gate 9 | — | `exit=0` after a pipe to `tail` | the exit status of the *suite*, which had been killed at 82% | reproduced one message later |
| **10** | **2026-10-08** | the repair commit `d271d80` itself | that the three named failures were fixed, and that the invocation no longer names two files | that the suite is run **whole**, and green | admitted 2026-10-18 (§3.2) |
| **11** | **2026-10-23** | the **instrument**, not a repair — a line-anchored key regex over an inline flow-style YAML file | *that the pattern found nothing* (both parties, independently) | that the property the pattern stands for is absent — a **public-source citation** in one reading, a **name–structure pairing** in the other | admitted 2026-10-23 (§3.6) |
| **12** | **2026-10-23** | the **instrument** — a CSV row filter keyed on a column name present in neither file | *that no row carried a verdict* | that the verdict column is empty — and **the printed answer was CORRECT**, from a measurement of nothing | admitted 2026-10-24 (§3.7) |
| **13** | **2026-10-23** | a **done-condition assertion** naming a single `.dvc` pointer path the three-pointer layout has never produced | *that the named path was absent* | that the task had not run — **blaming the wrong party, loudly**, while part (d) of the same function used the correct path | admitted 2026-10-24 (§3.7) |
| **14** | **2026-10-23** | the **instrument** — a blob comparison run against ONE commit for all thirteen files instead of each file's own | *that eight files differed* | that eight pages had drifted — a figure that **matched a stale expectation already in hand**, so agreement supplied the confidence | admitted 2026-10-24 (§3.7) |

Instances 1–6 are quoted from `paper/stage1-limitations.md` (pinned `ae894db`, measured 2026-09-29);
7–9 from `qgr/stage1-closure.md` (pinned `af17cd2`).

**Row 10's provenance, stated explicitly because it has no prior write-up to pin to.** Unlike rows
1–9 it was found after both source records closed, so its evidence is the primary artifact plus a
reproducible measurement: commit **`d271d80`** — its message, and its workflow diff
(`git show d271d80 -- .github/workflows`, which shows filename-scoping replaced by
`-m "not network and not integration"`) — together with that commit's own reported
**436 passed / 0 failed / 5 skipped / 30 deselected**. The excluding marker's origin is
**`7275c8c`**, an ancestor. Raised in lung-on-chipsim dispatches #662 and #664; admitted 2026-10-18.
The measurement is reproducible from the repository without either closed record.

### 3.1 RULED 2026-10-18 — publish both predicates, each naming its subject

Row 65's "six introduced by repair" is **retired: it matches neither predicate.** The ruling is to
**publish both, distinguished**, because the two readings are different questions and collapsing them
is what produced three irreconcilable figures across the source records.

**RULED 2026-10-18: §3.1 publishes the predicate and its row list. The count is READ OFF §3's table —
this note asserts no standalone numeral.**

| predicate | rows |
|---|---|
| broad — introduced by **a** repair | 2, 3, 4, 5, 6, 7, 8, 10 |
| strict — introduced by the repair of a **previously-enumerated instance** | 5, 6 (→ instance 4); 8 (→ instance 2, via C-3) |

**Why the presentation changed rather than the number.** This figure went stale **twice** — first as
"six", then as "7 of 9", the latter within the same sitting that admitted row 10. The ruling removes the
**recurrence class** instead of correcting the instance: §3.1 already required the figure to be *derived
from the table, not asserted*, and this makes that literal. **A count read off the table cannot go stale
when row 11 lands.**

Excluded, and why: **row 1** is a *creation*, not a repair. **Row 9** carries no repair attribution.
**Row 10** is excluded from the **strict** list only — the three failures `d271d80` named (manifest-skip,
vendoring allow-list, s6 panel) are not among the enumerated instances.
**Row 7** is excluded from the strict count only — its repair, **H-10**, is a *registered finding*, not
one of the nine: `qgr/deferred-findings-register.md:77` records it as "the one sentence stating the
citation scheme misresolved a row," and line 110 records this instance's chain, *"repaired under H-10
for this exact error, then re-broken by rows `#60`/`#61`; nothing recomputes it."* Traced to source,
not inferred.

**So §1 keeps "repair is one of its vectors" on 7, and §2 keeps "it survives its own repair" on 3** —
each sentence now carries the count that actually supports it.

**Whose claim each part of this is — stated because "it was in the text they selected" is not the same
as "it is their number."** The **predicate decision** — publish both, distinguished, and retire "six" —
is the **author of record's ruling**: it was the question put, and other options were available. The
**counts and the row assignments are the agent's derivation**, written into the option that was then
selected; the author did not independently re-derive them and had no occasion to. **If the derivation is
wrong, the ruling carries that error.** The CTO independently verified two parts of it — row 7's
exclusion, by tracing H-10 to `deferred-findings-register.md:77` and `:110`, and the row-10 split above —
and not the remaining row assignments. Per §4 the whole derivation is re-done at ratification, which is
the check that would catch it.

**This split has already paid for itself.** When the counts went stale on row 10's admission, fixing them
was a **re-derivation** — the agent's working, correctable — rather than a **re-ruling** of a figure
attributed to the author. Had the counts been recorded as the author's claim, correcting a denominator
would have meant reopening a ruled decision.

An earlier draft of this section said "only 2 of instances 1–6 are strict." That was right for 1–6 and
wrong as a nine-wide figure: row 8 adds a third.

### 3.2 RULED 2026-10-18 — the tenth instance is ADMITTED

Dated **2026-10-08**, the commit date, not the discovery date. **The claim:** commit `d271d80`'s *"The
CI job now **runs it whole** instead of a scoped subset."*

Scoping was **re-expressed**, not removed — filename-scoping became marker-scoping, and
`-m "not network and not integration"` deselects 30 tests. The commit's own numbers say so: **436
passed / 0 failed / 5 skipped / 30 deselected.** The `integration` marker on the T4 test *predates* the
commit (`7275c8c`, an ancestor); `d271d80` added the **selector that excludes it**, then called the
remainder whole. Sharpest form: the comment the commit **deleted** stated the reason for scoping —
*"two need the DVC payload on disk"* — one of those two was fixed at its cause, the other was not and
fell inside the new selector. **It removed the sentence that named the problem and kept the problem.**

**Scope precedent, since instances 1–8 are paper claims and this is a commit message:** instance 9 is
the gate's timing command — instrumentation, not a published claim — so instrumentation is already in
scope. This one's dependent is larger: it is the standing statement of what CI gates, which every later
"the suite is green" inherits.

**A correction that is part of the evidence.** The finder's first formulation — *"the commit resolved
three others; this one it deselected"* — implied the T4 test was a fourth member of the set the commit
claimed to fix. **It was not**, and the finder corrected itself unprompted; those three are genuinely
fixed at their causes. Had it stood, a tenth instance would have entered this note resting on a false
claim, inside the note about claims resting on false verification.

### 3.3 RULED 2026-10-18 — the enumeration is a FLOOR, not a count

The tenth instance was surfaced by a question whose **premise was wrong**: the asker asked whether a
green test was *environmental*; it was *deselected*. An instance found by a mistaken question is still
an instance — but it is evidence that the others were found by the **same kind of luck**, not by a
method. §2 records that only one of ten was first caught by an instrument.

So this note claims **"at least ten"**, and says plainly that discovery is reader-dependent. It does
not publish a number as though the enumeration were complete.

**The sharper form of the same observation, and the reason the floor keeps rising.** On 2026-10-18,
**five separate times**, a *false* premise is what made the next reader look — and each time the look
found a real defect that the false premise had not predicted. A mistaken question about an
"environmental" green found a deselected assertion; a mistaken claim about a stale pin found a mangled
sentence beside it. That is not a method anyone can run on purpose. It is **luck with good manners** —
participants who state premises explicitly enough to be checked, and who check them. A process whose
discovery rate depends on that cannot report its enumeration as complete.

### 3.4 The 2026-10-18 layer evidence — two labelled classes

**RULED 2026-10-18: pre-send catches COUNT, in a separate labelled class**, so the evidence is **graded
by what a reader can check** rather than merged into one inflated figure. The **canonical nine are
untouched** by this ruling, and so is §2's "of the ten".

**Why "don't count" was not the conservative option.** Canonical **instance 6** of the ruled nine is
*itself* a pre-send catch — `paper/stage1-limitations.md:211` records it as *"same day, **caught before
commit**"*, and §2 repeats it. Excluding pre-send catches would therefore have contradicted the canonical
nine's own composition, and cascaded: instance 6 sits in **both** §3.1 lists, so striking it would have
moved broad to rows 2–5,7,8,10 and strict to rows 5,8, and turned §2's "of the ten" into "of the nine".
§2 already names "the author re-reading their own work" as a discovery route. The ruling keeps the note
self-consistent.

#### Class A — RECORDED (independently checkable from the dispatch record) — eight

| # | author | the claim, and the subject it was actually verified against |
|---|---|---|
| 1 | agent | the DVC pointer "was never committed" — verified against the **path the assertion names**, concluded about **reproducibility** |
| 2 | CTO | accepted (1) — with the three real pointers **already present in the CTO's own earlier output** |
| 3 | CTO | "reproducible from the committed repository" — verified on the **ref in hand**, not the ref the claim was about |
| 4 | agent | the replacement recommendation — read a historical note about **S7's probes** as a description of **this test** |
| 5 | CTO | "the test is correct, no flat-path reference" — read the **plural r2.11 test** on one branch, concluded about the **singular test that failed** on another |
| 6 | CTO | "40 behind the trunk" — measured against a local ref **named** `main` that is 61 commits *ahead* of the published trunk |
| 7 | agent | **shipped**: asserted this note was "still pinned `3a7f186`" having printed only lines 1–14; verified on DRAFT 1, asserted of DRAFT 2 |

#### Class B — DISCLOSED PRE-SEND (author-only; rests on the author's disclosure)

**Five**, all the agent's, all the same predicate — a correct search, correctly executed,
**under-specified in its subject**, producing a confident false negative about work that had been done:
the `audit/` path probe (`lung-on-chipsim/audit/` against the real `chipsim/audit/`); `'^| 10 '` missing
the bolded `| **10** |` row; a search for the author's own phrasing rather than for the section heading;
and the two disclosed earlier.

**Presentation note (a CTO call, not a ruling):** the former layer 7 — the `audit/` probe — moves out of
the sequential list into Class B, and the shipped pin error takes the seventh recorded slot.

#### How the two classes are told apart — and a defect in this section, now fixed

**RULED 2026-10-20.** The classes are defined by **verifiability**, not by discovery: Class A is what a
reader can check **from the record**, Class B is what rests on **the author's disclosure alone**.
*"Caught by the next reader"* was only ever a description of how Class A's members happened to be found.

**This section previously used two criteria for one taxonomy** — the class headings test verifiability
while an earlier paragraph reasoned from discovery, declaring one case homeless because it was *"neither
Class A (caught by the next reader) nor Class B (never sent)."* Under the stated membership test that
case was never homeless: a claim made in one dispatch and corrected in the next **rests on the record**,
so it is **Class A**. The third class dissolves, **Class A becomes eight**, and *who caught it* is
preserved as a **per-row attribute** rather than a class boundary:

| class member | caught by |
|---|---|
| A1–A6 (the original layers) | the next reader |
| A7 — the shipped pin error | the next reader |
| **A8 — a stale figure passed forward in a dispatch, corrected in the following one** | **its own author** |

That drift is worth recording rather than quietly repairing: a taxonomy whose headings state one test
while its prose applies another is the same defect this note documents, committed in the act of
classifying the note's own evidence.

### 3.5 The one check that would have caught all of them

Approved into this note on 2026-10-18.

Every instance above, and every layer in §3.4, is a **correct reading of real evidence attributed to the
wrong subject**: the path an assertion names rather than the property it claims; the ref in hand rather
than the ref the claim is about; a historical note about one probe read as a description of another; two
refs sharing a name. **None was a misreading.** That is why no instrument caught any of them — an
instrument that checks *does the code say what you claim* passes every one.

> **The check:** every claim about a ref, a path or a probe must **name its subject explicitly**, so a
> reader can ask *"about what?"* of the claim itself rather than of its author.

§3.1's ruling is that check applied to this note's own headline figure — two predicates, each named,
each with its own count. It is the first use of the instrument **before** publication rather than after.

**AMENDED 2026-10-23 — this section's heading overclaims, and instance 11 is why.** "The one check that
would have caught all of them" was true of instances 1–10 and is **false of instance 11**. In that case
both parties named their subject correctly and stated it explicitly; the defect was that the *reading
itself was manufactured by the wrong instrument*, so a check on how a claim is phrased cannot reach it.
The scope is therefore narrowed, not the check withdrawn: **it catches subject-attribution errors, which
is what instances 1–10 are, and it does not catch instrument errors.** §3.6 adds the second check,
which is addressed at the tool rather than at the sentence.

### 3.6 ADMITTED 2026-10-23 — the eleventh instance, and the first where the INSTRUMENT produced the reading

**Two authors, one file, one hour, opposite confident verdicts, one cause.** On `configs/poc_compounds.yaml`
the CTO ran a line-anchored regex over citation field names, found zero, and reported *"the public-source
condition DOES NOT HOLD"* — a **false violation**, one step from escalation. The lung-on-chipsim agent
independently ran a line-anchored `^\s*name:`, found zero, and reported that the identifier was **not**
paired with a name — a **false absence**. The two conclusions are opposites and both are wrong.

**Root cause, measured on the published blob:** the file uses inline flow-style mappings,
`- {canonical_inchikey: …, name: …, evidence_doi: …}`, one entry per line — **26 of 26 entries flow-style,
0 block-style, and zero line-anchored keys in the whole file.** A line-anchored pattern can see nothing
inside any entry. Only structural parsing settled it: 26/26 on every key.

**Why this instance is different in kind from 1–10, and why it earns its own sub-section.** Those ten are
each a *correct reading of real evidence attributed to the wrong subject* — the reading was sound and its
subject was wrong. Here the reading was **never sound**: an instrument that encodes an assumption about
formatting returned a result about a file it could not read, and **it failed silently by returning zero
rather than erroring.** A zero from a pattern is indistinguishable from a zero in the data.

> **The second check, addressed at the tool rather than the sentence:** for a structured file, parse the
> structure. A pattern-match over a serialisation encodes an assumption the file is free to violate, and
> its failure mode is a confident empty result. Before trusting a count of zero, establish that the
> instrument can see a non-zero.

**Disposition and provenance.** Neither error reached a published claim or a ruling; each was caught by
the other party within the hour, and both are disclosed in the approval log (row 34) with the structural
re-measurement. Reproducible without either disclosure: parse the file at
`origin/lung-on-chipsim:projects/lung-on-chipsim/configs/poc_compounds.yaml` and count flow-style entries
against line-anchored keys. **This is the first instance in this note with two independent authors**, and
the first where the floor rose because an instrument — not a reader — was wrong.

**AMENDED 2026-10-24 — THIS CHECK WAS PUBLISHED AND THEN DID NOT FIRE, and the author is who it did not
fire for.** Within hours of this section being written, its own author ran an over-specified literature
query, received **zero**, and read that zero as absence — the precise failure this check's last sentence
forbids. The minimal form of the same query returned **thirteen**. The occurrence is **deliberately not
numbered** among the instances above, because it is not a new mechanism: it is a *recurrence* of the
mechanism already described here, and what is new is that **a correct, published, specific check made no
difference to the person who wrote it.** That observation is general rather than local — it applies to
§3.5 equally — so it is argued in **§3.7** rather than here, and this paragraph exists so a reader of
§3.6 learns that the check below has a known miss rate of at least one, by its own author, on the day it
was published.

### 3.7 ADMITTED 2026-10-24 — three instances that complete the taxonomy, and the check that neither §3.5 nor §3.6 could be

**What the first two checks have in common, and why it is a limit rather than a feature.** §3.5 is
addressed at a *sentence*: name your subject so a reader can ask *"about what?"*. §3.6 is addressed at a
*tool*: for a structured file, parse the structure. **Both require that something prompt a look.** §3.5
needs a reader to interrogate the claim; §3.6 needs an author to doubt an empty result. Each is sound
where that prompt exists. The three instances below are the cases where **nothing prompted anything.**

**Instance 12 — the instrument measured nothing and returned the right answer.** Verifying the P-gp
adjudication state, the lung-on-chipsim agent filtered rows on a column name present in **neither** the
five-column tracked file nor the nine-column working copy. `csv.DictReader.get` returned `None` for all
twenty-six rows, every row filtered out, and the instrument printed *"verdicts typed: 0"*. **That answer
was true.** Re-derived with the key asserted present before counting: twenty-six rows, zero non-blank
verdicts, on both files. The conclusion survives; the measurement that produced it did not exist.
**Instances 1–11 all leave a discrepancy a careful reader can hit. This one leaves none** — the output
is indistinguishable from a real measurement, so no downstream reader, review or test can ever catch it.
Only the instrument's own precondition assertion can.

**Instance 13 — the instrument failed loudly and blamed the wrong party.** A done-condition asserted a
single `data/raw/drugbank.dvc` pointer. The layout tracks **three** per-file pointers under
`data/raw/drugbank/`, and the glob matches nothing, so the named path has never existed in this layout.
The assertion therefore failed for the layout's entire life while printing *"T4 has not run: …
is absent"* — **wrong subject and wrong party**, and part (d) of the same function already used the
correct directory, so the two halves of one test disagreed with each other. It is the only instance in
this note that is **not silent**, which is why it needed admitting: a loud failure whose message
misdirects is not caught by being loud. It stayed invisible for a second reason that belongs to the
measurer rather than the test — the selector in routine use **deselected it**, and §3.5's check cannot
help, because the assertion *did* name its subject explicitly. It named one that was not there.
**Standing lesson: a test excluded by the measurer is in the same epistemic state as a test that passes
vacuously.**

**Instance 14 — the instrument was wrong and agreed with me.** Measuring whether thirteen mirrored pages
had drifted, the CTO compared every page against **one** commit — the last to touch the first file —
rather than against each page's own pre-sync commit, and obtained *"five identical, eight differ"*. The
figure **eight matched a stale count already in hand**, so the wrong instrument *confirmed an
expectation* and felt like verification. Re-run per file against each page's own pre-sync commit:
**thirteen identical, zero differ** — the entire drift report was false positives. This is the most
dangerous member of the family and the reason is not subtlety: **a result that contradicts you invites a
second look, and a result that agrees with you removes the only prompt the first two checks depend on.**

> **The third check, addressed at the measurement rather than the sentence or the tool.** *Assert the
> instrument's preconditions, and distrust agreement.* Before believing an output, establish that the
> thing measured **exists** — the key, the path, the population — because a measurement of an absent
> subject still returns a value, and that value can be correct by coincidence. And give a result that
> **confirms** your expectation no less scrutiny than one that contradicts it: re-derive it by an
> independent route. The first two checks fire when something looks wrong. This one has to fire when
> nothing does.

**And the claim this section exists to make, which is about enforcement rather than method.** §3.6's
check is correct, specific, and was published hours before its own author committed the defect it names
(§3.6, amended 2026-10-24). §3.5's check could not reach instance 13 although it was written for exactly
that shape. **A check that lives in prose does not run.** The operative form, first stated by the
lung-on-chipsim agent and adopted here: *naming a defect class does not inoculate the next instrument;
only an assertion that fires does.* Every instance in this note was caught by a probe, an assertion, or
the next reader — **not one was caught by a passing suite, and not one was prevented by a published
rule.** That is a finding about this note's own utility, and publishing it is the only honest response to
having written three checks in two days and then needed all three.

**Disposition and provenance.** All three instances are disclosed in the approval log — 12 at row 42, 13
at row 43, 14 at row 40 — with their re-derivations. Each is reproducible from its row without this
section. Two are the CTO's (13's selector cause and 14 entirely) and one is the lung-on-chipsim agent's
(12), self-disclosed within the hour. The unnumbered recurrence is the CTO's and is recorded at §3.6 and
in row 49.

## 4. The contribution: an artifact that measures its own approval process must pin and re-derive

Stage 1's declared novel contribution was a measurement **of its own approval log** — the route
distribution over a contemporaneous, append-only, hash-locked revision table. It published 59
revisions / 63 rows / 46 standing-delegation, and a re-derivation at `af17cd2` gave **61 / 65 / 47**.

**Re-derived again at ratification, on `main` at `d578274`, as §4 requires — and it did not reproduce:**

| | published | at `af17cd2` | **at ratification (`d578274`)** |
|---|---|---|---|
| numbered revisions | 59 | 61 | **74** |
| total data rows | 63 | 65 | **78** |
| standing-delegation | 46 | 47 | **47** |
| **unclassified** | — | 0 | **12** |

**The standing-delegation count is unchanged at 47, so the proportion claim moves in its denominator
without its numerator moving at all** — the clearest possible demonstration of why this note's rule
exists.

**RE-DERIVED AGAIN at the 2026-10-23 amendment, as §4 requires — and THIS TIME IT REPRODUCED.**
Numbered revisions **74**, total data rows **78**, measured structurally at the amendment ref and
matching `route-distribution-d578274.json` exactly. The amendment that added instance 11 edited only
the *decision text* of two rows in the revision table and **no route cell**, so the category counts
cannot have moved. **That a re-derivation reproduces is a result, not a formality** — it is what the
rule is for, and the previous run failing is what makes this run worth stating.

**RE-DERIVED A THIRD TIME AT THE AMENDMENT'S RATIFICATION (2026-10-23, `59a5210`), as §4 requires — and
THREE OF THE FOUR FIGURES REPRODUCE, INCLUDING ONE THIS NOTE HAD RECORDED AS IRREPRODUCIBLE.** Measured
by structural parse of the revision table — a pipe row whose first cell is a bare integer — not by a
line-anchored pattern, for the reason §3.6 gives:

| | published | **at ratification (`59a5210`)** | result |
|---|---|---|---|
| numbered revisions | 74 | **74** | reproduces |
| total data rows | 78 | **78** | reproduces |
| unclassified | 12 | **12** | **reproduces, and derived directly** |
| standing-delegation | 47 | **not recoverable from the log** | bounded, see below |

**This run is a stronger test than the last one, because the corpus moved underneath it.** The approval
log *was* edited between the amendment and this ratification — `e574e79` amended A1 and A2 in place
across two rows of this very table — and the counts held anyway. They held for a checkable reason: that
edit rewrote *decision text* and **no route cell and no row boundary**, so neither a count of rows nor a
distribution over routes could have moved. A re-derivation that survives an intervening edit, for a
stated reason, is worth more than one over a frozen corpus.

**The 12 unclassified reproduce by DIRECT derivation, which closes half the gap recorded below.** A raw
count of the route column gives exactly **eleven** rows reading `principal (same grill; "Over and out")
folded by the CTO` and exactly **one** reading `CTO signature (principal approval 2026-10-04 "approve
all")` — 11 + 1 = **12**, matching the published figure without needing the classification instrument at
all.

**The standing-delegation figure of 47 is now BOUNDED rather than merely unverifiable, and it still does
not reproduce.** A direct count of the route column gives **45** cells reading exactly
`standing-delegation`, and **51** cells that mention `standing` or `delegat` at all — the difference
being six compound cells such as `principal + standing-delegation` and `CTO correction, agent-raised
(#502); standing-delegation`. **47 lies strictly between 45 and 51.** So the published figure is an
output of the ordered first-match-wins instrument that absorbs *some* compound cells and not others, and
**which two it absorbs cannot be determined from the corpus.** Reconstructing them by guesswork was
available and is **declined on this note's own grounds**: inferring an instrument's behaviour from the
answer it produced is verification against the thing changed rather than the property claimed. The datum
published here is the bound and the reason, not a recovered 47.

**RE-DERIVED A FOURTH TIME AT THE 2026-10-24 AMENDMENT, and it reproduced — but this run is WEAKER
EVIDENCE than the last one and the difference is worth naming.** Measured structurally at `a38f161`:
numbered revisions **74**, total data rows **78**, unclassified **12** (eleven *same-grill* cells plus
one *CTO-signature* cell, derived directly), and the standing-delegation figure bounded at **45** exact /
**51** mentioning as before. **The approval log did not change between the previous pin and this one.**
So unlike the 2026-10-23 run — which held *despite* `e574e79` editing two rows of this very table, for a
checkable reason — this run is over a frozen corpus and is therefore **a formality rather than a test**.
A re-derivation reported without saying whether its corpus moved is a number without its conditions,
which is what §4 exists to prevent; so the condition is stated instead of the reassurance.

**One limit on that re-derivation, stated rather than glossed.** The structural figures (74 / 78) were
re-measured directly. The category figures (**47** standing-delegation, **12** unclassified) were
**not independently re-derived**, because the evidence artifact states its rule — *ordered
`CATEGORY_PATTERNS`, first match wins, order is part of the rule* — **without embedding the patterns
themselves.** So the classification is reproducible only by whoever still holds the instrument. That is
the same defect family as instance 11 one level up: **an evidence artifact that names its method and
omits its instrument.** Recorded here as a gap in this note's own evidence, not repaired in this
amendment.

**The 12 unclassified rows are published as a datum, and the stated rule is left untouched.** They are
rows 63–74: eleven read `principal (same grill; "Over and out") folded by the CTO`, and one reads
`CTO signature (principal approval 2026-10-04 "approve all")`. **All twelve carry principal authority** —
the twelfth is CTO-signed *under* a principal approval, not CTO-originated — so a reader must not read
"unclassified" as "not human-routed."

Retrofitting the pattern list to absorb them was available and was **declined**: extending a stated rule
so an inconvenient residue disappears is a repair verified against *the thing changed* (the patterns)
rather than *the property claimed* (that the distribution describes its log) — this note's own
documented vector, at the moment of its own ratification. **The residue is the more honest datum:** it
shows a stated classification rule drifting from the corpus it classifies. Evidence artifact:
`qgr/evidence/route-distribution-d578274.json`.

The two extra rows were written **by the adjudication of the report itself**: the scope ruling the
final gate requested, and the ruling *"Stop; the mechanism is the result."* Deciding whether to accept
the report changed the quantity the report published.

An earlier draft of the closure called this a fixed point — a claim that could not simultaneously be
true and approved. **That was an overstatement and was withdrawn**, and the withdrawal is part of the
finding. A claim pinned to a *commit* is stable against any number of later rulings. The real defect is
narrower and more useful: the figure was pinned to the **plan hash** `ae894db`, and rows 58–61 all
carry that same hash "(unchanged)", so **the pin could not discriminate.**

> **The rule:** an artifact that measures the process which approves it must pin its measurements to a
> revision **of that process**, and must re-derive them at the moment of approval. Choose an identifier
> that moves when the measured thing moves.

Stage 1 did neither, which is why its headline figure was two rows stale at the moment of its own
closure. §3.1 of this note is the same hazard, caught before publication rather than after.

## 5. What a reader should not conclude

- **Not** evidence that the Stage 1 mechanisms work. Instances were introduced by the very repairs
  those mechanisms authorise.
- **Not** evidence that the content guard is sound: its headline is qualified by ruling, two of three
  prohibitions are measured by nothing, the citation predicate is positively correlated with the
  violation it exists to expose, and the certifying gate can report `PASS` over a 69-file blind spot.
- **Not** a negative result about the people or the tooling. The same mechanism was committed by
  implementer, reviewers and coordinator alike.

What it **is** evidence of: *the family is open, it survives repair, and repair is one of its vectors* —
supported by **at least ten** dated instances with named authorship — a floor, not a count — obtained
at the cost of not shipping.

## 6. Inheritance

Thirty-six registered findings stand. A successor should **not** begin by repairing them: on this
branch's record, repair is how most instances arrived. Read first: **S-01, S-02** (they make the newest
instrument's verdict unreproducible from the repository), **S-06, S-07** (they let a failing run publish
a clean record), and **S-20** (R-10's deferral was taken at a smaller extent than now exists).

## 7. Open items for the author of record

1. **RULED 2026-10-18** — §3.1 predicate: publish both, broad and strict, each named; "six" retired.
2. **RULED 2026-10-18** — §3.2 tenth instance admitted; §3.3 enumeration published as a **floor**;
   §3.5 instrument adopted.
3. **RULED 2026-10-18** — §3.1 now publishes the **predicate and its row list** and asserts **no
   standalone numeral**; the count is read off §3's table, so row 11 cannot stale it. The predicate
   ruling itself is untouched.
4. **RULED 2026-10-18** — pre-send catches **count, in a separate labelled class**: Class A RECORDED
   (independently checkable, seven entries) and Class B DISCLOSED PRE-SEND (five, author-only). This
   also admitted the shipped pin error into Class A, closing the eighth-row question.
5. **RULED 2026-10-18/20 — VENUE: *Journal of Trial and Error*.** Chosen on scope, not convenience:
   its stated scope names this note's genre directly — negative or null results, **"studies where
   notable methodological errors occurred"**, reflections on failed research, meta-research, any
   discipline. **No word limit**, so §3's table and both §3.4 classes survive uncompressed. **Rolling
   submission**, so ratification is not rushed. **Fallback:** JORS *Issues in Research Software*
   (3,000–4,000 words, experience reports named in its formats, **£891 APC** waivable only via the
   submission cover letter).
   **Three structural additions JOTE requires, and nothing is cut:** a structured abstract of 150–250
   words; a purpose section capped at 250 words; a take-home message of at most three sentences / 50
   words. Preprints are accepted at CC BY 4.0 or more permissive, which this public repo already allows.
   **ICSE 2027 NIER and MSR 2027 were declined knowingly.** NIER closed 23 Oct 2026 AoE at **4 pages
   inclusive**, **double-anonymous**, with a mandatory *Future Plans* section, and its scope does not
   name negative results. Accepting it would have required **stripping the named authorship that is
   this note's evidence base**, and ratifying inside roughly 96 hours — on a note arguing that figures
   go stale when the measured thing moves and nobody re-derives. The cascade was put in the option text
   so the choice was made against it rather than into it.
   **ONE GAP NAMED AND NOT CLOSED — JOTE's fees are UNVERIFIED AT SOURCE.** DOAJ reports no APCs and
   CC BY, but that is a **search summary**: the journal's for-authors page, its FAQ and the DOAJ record
   all return **HTTP 403**, and the record is roughly 13 months old. It was deliberately **not** filled
   from recollection. **Open the fee page in a browser before submitting.** Comparison page, carrying a
   per-row verification ledger (read-at-source vs search-only vs blocked):
   https://claude.ai/artifact/BQqQQCqcrfpysujpLxhLez
6. **RULED 2026-10-20 — the sub-case is Class A, and the taxonomy's drift is fixed.** It was never
   homeless: the classes test **verifiability**, and a claim made in one dispatch and corrected in the
   next rests on **the record**. The third class dissolves, Class A becomes **eight**, and *who caught
   it* is preserved as a per-row **attribute** rather than a class boundary. §3.4 previously stated one
   test in its headings and applied another in its prose — that drift is recorded in §3.4 rather than
   quietly repaired.
7. **RATIFIED 2026-10-20, and §4's procedure was EXECUTED, not asserted.** The re-derivation was run
   on `main` and **failed**: 74 numbered / 78 rows / 47 standing-delegation / **12 unclassified**
   against the published 61 / 65 / 47 / 0. §4 now carries the corrected table, the 12 published as a
   datum with their contents named, and the pin moved to `d578274`. **The rule caught a stale headline
   figure in the note whose subject is stale headline figures — one step before publication.** The
   residual honesty, unchanged: of the §3.1 derivation only row 7's exclusion and the row-10 split were
   independently checked; the rest were verified by their author alone.
8. **Superseded note on what ratification required:** §4's rule binds this note — at ratification,
   **re-derive every figure and update the pin.** That includes the route-distribution figures (published 59/63/46,
   re-derived 61/65/47 at `af17cd2` — both now stale themselves) and §3's row lists. The pin on this
   draft is `f2bb28c` and is stale already. **Note what ratification is actually covering:** of the
   agent's §3.1 derivation, the CTO has independently verified row 7's exclusion and the row-10 split;
   the remaining row assignments have been verified by nobody but their author.

**Sources (all committed):** `qgr/stage1-closure.md`; `paper/stage1-limitations.md` (instance 6's
pre-commit catch at :211); `paper/stage1-methods.md`; `paper/stage1-claims-list.md` (41 rows / 35
supported / 6 CUT); `paper/stage1-short-form.md`; `qgr/deferred-findings-register.md` (H-10 at :77,
instance 7 at :110); `plan/plan-approval-log.md` rows 58, 59, 61, 65; approvals rows 6-18;
lung-on-chipsim dispatches #662, #664, #675, #680, #682, #683.
