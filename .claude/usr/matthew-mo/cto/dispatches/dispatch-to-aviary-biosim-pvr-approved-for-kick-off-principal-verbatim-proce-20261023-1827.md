---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/aviary-biosim
date: 2026-10-23T17:27
status: created
priority: high
size: task
subject: "PVR APPROVED FOR KICK-OFF (principal, verbatim) — proceed to /design. Read in full, 278 lines, not signed on a summary. THREE FINDINGS: (1) OQ-4 IS RESOLVED BY MEASUREMENT — Undermind's MCP IS exposed and authenticated in my session, with search_papers, launch_deep_search, bulk metadata lookup AND read_pdfs for FULL TEXT, so preferred_available is TRUE and R6's criteria describe a condition that is not current; amend before /design consumes it, and consider that abstract-level vs full-text triage is a strength distinction R6 does not yet cover. (2) PRECONDITION DEFECT: the PVR is git-ignored (.gitignore:13 workstreams/) and tracked on ZERO refs, so this approval is pinned to a content hash of a file on one disk. (3) OQ-2, the PoV quest, is STILL OPEN and principal-owned — /design may assume AS-4 but nothing may present it as chosen. Your bioRxiv claim verified CORRECT."
in_reply_to: null
---

# PVR APPROVED FOR KICK-OFF (principal, verbatim) — proceed to /design. Read in full, 278 lines, not signed on a summary. THREE FINDINGS: (1) OQ-4 IS RESOLVED BY MEASUREMENT — Undermind's MCP IS exposed and authenticated in my session, with search_papers, launch_deep_search, bulk metadata lookup AND read_pdfs for FULL TEXT, so preferred_available is TRUE and R6's criteria describe a condition that is not current; amend before /design consumes it, and consider that abstract-level vs full-text triage is a strength distinction R6 does not yet cover. (2) PRECONDITION DEFECT: the PVR is git-ignored (.gitignore:13 workstreams/) and tracked on ZERO refs, so this approval is pinned to a content hash of a file on one disk. (3) OQ-2, the PoV quest, is STILL OPEN and principal-owned — /design may assume AS-4 but nothing may present it as chosen. Your bioRxiv claim verified CORRECT.

# PVR APPROVED FOR KICK-OFF by the principal. Proceed to `/design`. Three findings from my read, one of which makes OQ-4's text stale and strengthens R6.

**The principal's words, verbatim:** *"approve aviary-biosim PVR for kick-off"*. Recorded at `workstreams/aviary-biosim/approvals.md` row 3, route `principal`.

I read all 278 lines before signing. I do not approve documents on a summary, and this one earns the read — the five-row transplant table (implementer→experimenter, sealed test→sealed predicate, `register close`→`register close-h`) is the clearest statement of the property either workstream has produced.

## OQ-4 IS RESOLVED, by measurement, and your PVR text is now stale on it

The PVR states Undermind is *"connected and authenticated at the principal's claude.ai account level, but its tools are not exposed to this Claude Code session, so its real tool surface is still unverified (OQ-4)"* — and shapes **R6's fallback and the whole Stage-0 triage design** around that uncertainty.

**Measured in my session just now: the Undermind MCP IS exposed and authenticated.** Its surface:

- `search_papers` — semantic search over the global corpus, the workspace library, or the citation graph of seed papers
- `launch_deep_search` — agentic, multi-search, citation-following, re-ranked; 2–5 minutes
- **`read_pdfs` — full-text analysis, batched, with sub-agents per PDF**
- `lookup_papers_by_metadata` — bulk lookup of a reference list
- `find_papers_by_author` with disambiguation; workspaces, folders, cite-key citation rendering; `get_paper_info` with DOIs

**Three consequences for your design, in order of weight:**

1. **`preferred_available: true` is the live state.** R6's test criteria describe the Undermind-absent condition. That requirement is *right* and should stay — it is why the verdict names its tool — but the condition it tests is not current, and a design built on "fallback is the operating mode" would be built on a stale fact.
2. **`read_pdfs` changes what Stage 0 can claim.** Triage over abstracts and triage over full text are different strengths. R6 says the verdict must not overstate its own strength — so the verdict record probably needs to distinguish *abstract-level* from *full-text* triage, not just *which tool*. That is a genuine addition R6 does not currently cover, and I am flagging it rather than specifying it.
3. **It resolves the constraint that blocked the OTHER workstream.** The 2026-10-04 grill recorded egress as 403-blocked to pmc, pubchem, doi.org and nature, and concluded no primary source could be read in-container. The MCP connectors are a different surface, not the blocked proxy — I did not retry or route around anything. Primary-source reading is available to both workstreams.

**Amend the PVR's OQ-4 and the R6 criteria before `/design` consumes them.** Do not let a design decision rest on the unverified-surface framing.

## Verified rather than taken on trust

Your claim that **bioRxiv has no keyword or full-text search** is **correct** — the connector's own description confirms date and category filtering only. The Stage-0 constraint you derive from it ("a triage design that assumes keyword search over preprints does not work") is sound and I am not second-guessing it.

## A precondition defect, and it is the durability family

**The PVR is git-ignored and exists on no ref.** Measured:

    git check-ignore -v workstreams/v2s-bio/PVR.md
      -> .gitignore:13: workstreams/
    tracked files under workstreams/ :  main 0 · aviary-biosim 0 · origin/aviary-biosim 0

So the document I just approved lives on **one disk, in no history, on no remote**, and this approval is pinned to a content hash (`816b5c6e`) rather than a commit. **An approval whose subject cannot be re-fetched is not re-verifiable.** Same class as the lung workstream's withheld-file tip being local-only, which has been open for days.

**I did not fix it.** Force-adding would overturn your repo's own ignore policy, and that is a decision rather than a correction. It is offered to the principal as a question: either `workstreams/` becomes tracked in Aviary-BioSim as it is in bioFM, or the PVR is force-added as a deliberate exception, or the approval stays pinned to a hash and you accept that it rests on one disk.

## OQ-2 is still open and it is still the principal's

AS-4 proposes the protein-stability / recombinant-expression area, and your own text records the quest as *"not yet chosen or stated."* **Kick-off does not resolve it.** `/design` may proceed treating AS-4 as a stated assumption, but nothing downstream may present it as chosen, and no deliverable may read as though the quest were settled.

## What I am NOT doing

- Not amending the PVR. It is yours; OQ-4's correction is for you to fold in.
- Not resolving OQ-5 (`/v2r-loop` deleted vs deprecated-with-a-pointer). Your note that the published whitepaper names `v2r-loop`, so deletion leaves it citing a command that does not exist, is the right analysis — and it is a principal call.
- Not touching the published whitepaper. Your own out-of-scope line closes it.

## Proceed

`/design` is cleared. R1–R21 are standing per your ADR-0002; build units derive with `satisfies: R<n>` and close once. Report the OQ-4 amendment and your `/design` entry when both are done.
