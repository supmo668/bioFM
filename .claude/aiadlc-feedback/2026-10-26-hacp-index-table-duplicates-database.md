---
type: plugin-feedback
target: airdlc plugin (airdlc-plugins/airdlc)
plugin_version: 0.82.0 (cache dir); this repo's framework.version is 0.3.0 — two different numbers, named so they are not conflated
reporter: biofm/matthew-mo/lung-on-chipsim
date: 2026-10-26
scope: plugin / operating-system behavior — NOT repo/app work
---

# HACP L0: the prescribed index table duplicates the `Indexed by`/`Entries` relation, and nothing checks the two agree

## 🔴 1. `REFERENCE-HACP.md` prescribes a hand-maintained index table over membership that is already a relation

**File:** `reference/REFERENCE-HACP.md:294–298` (the **L0** contract, items 5–7 and the rule that follows)

**Symptom.** On `bioFM`'s `lung-on-chipsim` index row
(`https://app.notion.com/p/b7c749bd250d83dab06201f85d61ee49`) the prescribed table — rendered
there as `## AIRDLC index`, five columns, *Phase / Entry / Layer / Holds / State* — had **stopped
tracking the database it duplicates nine days earlier, and nothing failed.** Measured, not
estimated:

| measured | value |
|---|---|
| pages on the index row's `Entries` relation | **20** |
| rows in the hand-maintained table | **14** |
| absences explained in the page's own prose | **1** |
| **silently missing** | **5** |

The five: `stage1-closure-2026-10-18`, `reconciliation-decision-2026-10-20`, `stage2-divergence`,
`unblock-direction-2026-10-23`, `pgp-verdicts-2026-10-24`. **The last two are the project's current
decision surfaces**, and `pgp-verdicts` is the page a principal was linked to for a live
ratification thread one hour before this was found. Page `Updated` was `2026-10-16`; entries kept
landing through `10-24`.

**Root cause** (proven from the reference text, not inferred). The L0 contract asks for a
**Sections** item — *"one line each, tagged, linking down, with its state and the date it was last
updated"* — plus a decisions table, on a page whose membership is **already** the `Indexed by`
relation with `Entries` as its reciprocal (`REFERENCE-HACP.md:348–349`, 391: *"Membership is the
`Indexed by` relation, not a visual sub-item tree"*). So the same fact is stored twice: once as a
relation the platform maintains, once as prose a human or agent must remember to edit. Line **520**
of this very file states the principle being violated — *"A ruleset copied into three skills drifts
into three rulesets."* The index table is that, with membership instead of rules.

**The date requirement makes it worse, not better.** `REFERENCE-HACP.md:296`: *"Every table on an
index page carries a date … A reader must be able to tell a live row from a stale one without
opening it."* Every row in the drifted table **did** carry a date (`· 2026-10-04`,
`renewed · 2026-10-04`). Dates distinguish a stale row from a live one; they say **nothing** about a
row that was never added. A missing row has no date to be stale, so the mechanism meant to expose
staleness certifies the remaining rows as fresh while the table is five entries short. The reader is
*more* confident and *less* correct — which is this defect family exactly: a true signal at the
wrong extent.

**Fix.** Smallest viable change, in the L0 contract:

- Replace the prescribed entries/sections **table** with the **inline database view** of the
  `Indexed by` relation, filtered and sorted for reading. Notion already renders it; it cannot
  drift from itself.
- Keep a table on an index page only for facts the database does **not** hold, and say so.
- Keep the date rule, scoped to those: *a table on an index page carries a date **when it holds
  anything the index database does not** — and membership is never one of those things.*

**Effect.** Index membership becomes underivable-by-hand and therefore undriftable. The 5-missing
case cannot occur, because there is no second copy to forget.

**Status:** open

---

## 🟠 2. No check compares an index page's listed entries to its database membership

**File:** `tools/docs-plan` (subcommands: `add done iteration list none owed place plan probe root`)

**Symptom.** A row can be created, placed and `Indexed by` an index correctly, and never appear in
that index's table. Nothing anywhere reports it. This is how defect 1 reached five.

**Root cause.** The shipped checks verify different properties: `docs-plan place` validates *where a
row belongs*, and the repo-side `hacp_linkcheck.py` / `hacp_sync_check.py` verify *links resolve* and
*floor↔Notion sync dates*. **None compares the set of entries a page lists against the set the
database says it holds.** Each check is correct about its own subject, and the drift lives between
them.

**Fix.** Add `docs-plan audit-index <index-url>`: fetch the index row's `Entries`, extract the
mentions from its body, and exit non-zero on a set difference, printing the missing and the extra
by title. Fail-closed on a fetch error — *"could not read"* must not report as *"nothing
missing"*. (That exact swallow is the finding at `approvals` row 41 in this workstream.)

**Effect.** Drift becomes a failing check instead of something a reader notices five entries late —
and it is the kind of check that cannot be satisfied vacuously, because an empty fetch fails.

**Status:** open

---

## 🟠 3. An anchored-edit tool silently cannot reach a whole class of Notion blocks, and the failure looks like a bad anchor

**File:** the Notion connector's `notion-update-page` `update_content` path, as used by every HACP
write in `skills/` (e.g. `hacp-decision-surface`)

**Symptom.** Four failed edits in one session against Notion **tables** — twice on one page's table,
once against rendered `<b>` output, once against a mirror reworded relative to its source. Paragraphs,
headings and callouts on the same pages matched first time. The operator read it as "my anchor was
slightly wrong" and retried, four times.

**Root cause.** `update_content` matches **text**; a Notion table is **block-structured**, so neither
its rows nor the table as a whole has a text anchor to match. The anchor cannot exist. The tool
reports a miss, which is indistinguishable from a typo'd anchor, so the operator retries instead of
switching strategy.

**Fix.** Two parts, both small. (a) In the HACP surface skills, state that **tables, databases and
other block-structured content are not reachable by text anchor** — amend by replacing the
surrounding prose and strike the block, or hand the deletion to a human in the UI. (b) Where the
connector can tell that the requested anchor lies inside a non-text block, say so — *"anchor falls
inside a block-structured element; not reachable by text match"* — rather than returning a generic
no-match.

**Effect.** The next operator spends one attempt, not four, and learns the real constraint instead of
doubting their own anchor.

**Related, and the reason not to reach for the whole-page route:** `replace_content` is not the
escape hatch it looks like. `notion://docs/enhanced-markdown-spec` is explicit that
`<database url="…">` is an **imperative, not a reference** — *"including it here will MOVE that
database into the current page"* — and that a linked view requires `data-source-url` instead. This
project's index row reads back with `url=` on both embeds, so re-emitting the body **moves** the
canonical membership database and dropping the tag **removes** it. `<page>` carries the same hazard
("removing that `<page>` tag … will REMOVE that child page"). A whole-page rewrite is therefore not a
safe fallback for an unreachable block, and the skills should say that where an agent will look for a
workaround.

**Status:** open

---

## 🔴 4. The Notion connector serves TWO markdown specs that disagree, and following the wrong one writes literal markup onto a human review surface

**File:** the Notion connector's documentation resources, consumed by every HACP write
(`skills/hacp-decision-surface`, and anything calling `notion-update-page`)

**Symptom.** Two agents each quoted a markdown spec verbatim and accurately, reached different
conclusions about the same tag, and each found the other's citation unsupported. One could not resolve
the other's URI at all. Both resources exist:

    notion://docs/enhanced-markdown-spec        → "Enhanced Markdown Specification"
    notion://docs/notion-flavored-markdown-spec → "Notion-flavored Markdown Specification"

**Root cause.** They are different dialects for the same connector, and nothing says which governs.
Measured differences on constructs the HACP skills actually emit:

| construct | Enhanced spec | Notion-flavored spec |
|---|---|---|
| mention | `<mention-page url=…>`, `<mention-database url=…>` | `<mention url=… />`, `type="database"` |
| toggle | `<details><summary>…</summary></details>` | `<toggle heading="h1…h4">` |
| media attribute | `<pdf src=…>`, `<video src=…>` | `<pdf source=…>`, `<video source=…>` |
| empty line | `<empty-block/>` | `<p />` |
| `<database>` hazard | re-emitting an existing `url=` **moves** the database | `<page>`'s rules: **omission** deletes when `allow_deleting_content` is true, else errors |
| other HTML | not addressed | *"Never write other HTML tags (e.g. `<div>`, `<details>` …); they are saved as **literal text**"* |

**The last two rows are the damaging ones.** The Enhanced spec *prescribes* `<details>` for toggles;
the Notion-flavored spec names `<details>` as a tag saved as **literal text**. An agent following the
wrong spec gets no error — it gets visible raw markup on a page a human reviews. The
`hacp-decision-surface` skill already warns that *"raw `<strong>`/`<em>` inside table cells render as
visible markup"*; that trap is plausibly **this**, diagnosed as a formatting quirk rather than as two
specs.

**How to tell which governs, since the docs do not say:** read the dialect back off a real page. The
page in finding 1 emits bare `<mention url="…" />` — the Notion-flavored form, absent from the
Enhanced spec. **The readback is the authority; the resource listing is not.**

**Fix.** (a) Have the connector serve **one** spec, or state on each which implementation it
describes and which is current. (b) Until then, the HACP skills should say: *determine the dialect by
fetching the target page and reading its own markup back, not by fetching a spec.* (c) `docs-plan
probe` is the natural place to record the detected dialect once per session, next to the connector
health it already records.

**Effect.** Two agents reading "the spec" converge instead of diverging, and a wrong-dialect write
fails loudly instead of shipping literal tags to a reviewer.

**Status:** open

---

## 🟠 5. `tools/module-context` is `eval`-ed into a shell where `module_path` is a RESERVED zsh parameter

**File:** `tools/module-context`, as consumed by `skills/pr-prep` step 2 (and any other skill using
the same `eval` idiom)

**Symptom.** `skills/pr-prep` documents:

    eval "$(.../tools/module-context)"
    # is_submodule, module_path, trunk, diff_base now set

Run in this repo (non-submodule), the tool emits **only** `is_submodule=false`. Reading the other
three afterwards under **zsh** gives:

    module_path=/usr/lib/zsh/5.9     trunk=     diff_base=

`module_path` is zsh's own reserved parameter for module loading — it was already set before the
`eval` and the tool never touches it. Under `bash` the same call leaves it empty, so the behaviour
differs by shell. This session's shell is zsh.

**Root cause.** The tool communicates "not applicable" by **omitting** a variable, and the consumer
reads it unconditionally out of the ambient environment. Omission is indistinguishable from
"inherited from the shell" — and for this particular name the shell always has a value. A guard of
the form `if [ -n "$module_path" ]` is therefore **true when it should be false**, and it points at a
real, existing directory, so a path check downstream would not catch it either.

**Not a live failure here**, stated so it is not over-read: `is_submodule=false` means `pr-prep` uses
the parent diff and never reads `module_path`. The trap is latent, and it is in the error-free path
of a tool used by every PR gate.

**Fix.** Any of three, cheapest first: (a) have `module-context` **always** emit every key, with
explicit empty values (`module_path=`), so omission never means "ask the shell"; (b) rename the
variable to something unreserved (`aiadlc_module_path`); (c) in the consumer, derive everything from
`is_submodule` and never read the others when it is false. (a) is one line in the tool and fixes
every consumer at once.

**Effect.** "Not applicable" stops being spelled the same way as "whatever your shell already had."

**Status:** open

---

## Provenance

Found while a principal ruled *"'AIRDLC index' should not exist in project index .tables should not
be used, only database"* (recorded at `workstreams/lung-on-chipsim/approvals.md`, route `principal`).
The counts above were re-derived here against `docs/hacp/lung-on-chipsim/notion-map.json` and the
live index row rather than quoted from that ruling. The repo-local half of the fix — deleting the
section, amending the `Surface skill` property and `notion-map.json`'s `rule` — is dispatched to the
CTO, since Notion writes and `docs/hacp/` are outside this agent's lane. **This entry is the
framework half: without it, the next project's index is built the same way.**
