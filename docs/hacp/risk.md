# §risk — bioFM

Known gaps, proxies, and what is unverified.

## Deferred-findings registers

Each workstream keeps one. A row carries its severity, whether a live reproduction exists, its
disposition and date, and the gate that raised it. A register that silently loses rows is the thing
it exists to prevent, so a withdrawn finding keeps its id.

## The recurring defect family

Repeatedly found across all three workstreams: **a check derives a correctness-relevant answer from
something adjacent to the thing it describes.** A validator that checks whether a name is
well-formed cannot detect a name that is well-formed and wrong; a guard that recognises only its own
side's artifacts tests the defender; an attestation whose referent is designed to evaporate is
unfalsifiable rather than merely unverified.

A fourth instance, in the provenance layer rather than the code (lung-on-chipsim, 2026-09-29, #492): the approval log's ROUTE column asserts how authority was obtained and was bound to no check, while plans bind to hashes and boundaries bind to receipts. Row 55 claimed a direct principal answer for the E-23 descope; the principal confirms the authority was a standing time-box ruling applied by the CTO. Corrected by an appended row; a route convention now requires a verbatim quote or session reference for any direct-principal route, else `standing ruling applied` / `inferred`. The register keeps this row whatever the ruling.

## Unverified

The Notion write target recorded in config has not been exercised end to end; the first real
propagation is verified by reading the row back, not by a successful response.
