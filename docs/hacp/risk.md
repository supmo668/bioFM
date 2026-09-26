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

## Unverified

The Notion write target recorded in config has not been exercised end to end; the first real
propagation is verified by reading the row back, not by a successful response.
