---
type: plugin-feedback
target: airdlc plugin
plugin_version: 0.88.0
reporter: biofm/matthew-mo/aviary-biosim
date: 2026-10-31
scope: plugin / operating-system behavior — NOT repo/app work
---

## 🟠 1. HACP: the ruling that supersedes the governance contract is recorded outside it, in a per-project notion-map.json
**File:** the governance contract page `313fda9448094029904f344523d5bd01`, versus `docs/hacp/<project>/notion-map.json` `.rule`
**Symptom:** `CLAUDE.md` §HACP orders every agent to read the governance contract before an HACP write. I did, then wrote a hand-maintained entry table onto `docs/hacp/index.md` — the exact failure mode `CLAUDE.md` records for the ChipSim index. The rule that forbids it (*"the index row is NAVIGATION ONLY … and NO hand-maintained entry table (principal, 2026-10-26), superseding the 2026-10-14 wording which mandated the table and forbade it in the same sentence"*) is not on the contract. I found it only because I opened a **sibling project's** sync map, `docs/hacp/lung-on-chipsim/notion-map.json`, looking for a file-format convention.
**Root cause:** The contract is the designated read-before-write surface, but a ruling that amends it gets written wherever it was discovered — here, into one project's sync map. The amendment even names the defect in the wording it replaces (self-contradictory in a single sentence), so the contract is known-wrong at a known date and still serves that wording to the next reader. Nothing links the two surfaces in the direction an agent travels.
**Fix:** Give the contract page an `Amendments` section: one dated row per ruling, naming the superseded wording verbatim. Then `notion-map.json`'s `rule` string *points at* it instead of restating it, so the per-project file stops being a second, partial copy of the contract.
**Effect:** Reading the one surface the contract designates becomes sufficient — which is what `CLAUDE.md` already promises.
**Status:** open (filed against airdlc 0.88.0)

## 🟠 2. HACP: sync discipline ships as a rule with no portable guard, so every new project namespace starts unmonitored
**File:** `CLAUDE.md` §HACP *Sync discipline*; `scripts/hacp_linkcheck.py`, `scripts/hacp_sync_check.py`, `.github/workflows/hacp-docs.yml` (parent bioFM repo)
**Symptom:** §HACP prescribes those two scripts and states *"an un-mirrored edit fails CI"*. Measured in the `Aviary-BioSim` repo: **none of the three exists**, and the parent's workflow is pinned to `docs/hacp/lung-on-chipsim`. Consequence, measured: `docs/hacp/index.md` was pinned to `a553165` while `HEAD` was **103 commits** later, and nothing surfaced it — the staleness was found by hand, not by a check.
**Root cause:** The HACP contract is plugin-governed, but its enforcement is repo-local hand-wiring: two scripts and a path-filtered workflow written for the first namespace. A second namespace therefore inherits the rule and none of the enforcement, and inherits it silently — there is no state in which the project declares that it is unguarded.
**Fix:** Ship the guard with the plugin as `tools/hacp-sync-check <project-dir>` (and `tools/hacp-linkcheck`), taking the namespace as an argument rather than a constant; have the HACP init path register the new namespace in the workflow's path filter. Until then, require `notion-map.json` to carry an `automation` block, so an unguarded namespace at least says so.
**Effect:** A namespace can no longer be created carrying the rule but not the check, and a 103-commit drift is caught by CI on the push that causes it.
**Status:** open (filed against airdlc 0.88.0)

## 🟠 3. notion-update-page cannot match an old_str that spans an inline mention block
**File:** `mcp__plugin_airdlc_notion-aiadlc__notion-update-page`, `command: update_content`
**Symptom:** On page `313fda9448094029904f344523d5bd01`, one `old_str` returned `no_match` while twelve others in the same session applied. The failing string was the only one whose text spanned two inline `<mention>` blocks, copied verbatim out of the immediately preceding `notion-fetch`. Re-targeting the plain-text runs on either side of the mentions applied cleanly.
**Root cause:** **Proven:** text that `notion-fetch` renders for an inline mention is not matchable by `update_content`, so a verbatim copy of fetched content is not a safe `old_str`. **Inferred, not proven:** the matcher works against a representation in which the mention is a node rather than its rendered text. I did not read the server, so I am not asserting the mechanism.
**Fix:** State the constraint in the tool description — *an `old_str` may not span an inline mention; target adjacent text* — since that is cheap and correct regardless of mechanism. Better: normalise mentions to their rendered form before matching, so round-tripping `notion-fetch` output works.
**Effect:** The operator stops spending a failed write to discover that fetched text is not matchable text, on a surface where writes are governed.
**Status:** open (filed against airdlc 0.88.0)
