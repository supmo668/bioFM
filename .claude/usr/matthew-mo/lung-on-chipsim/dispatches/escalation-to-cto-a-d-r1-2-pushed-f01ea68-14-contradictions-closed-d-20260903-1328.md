---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-03T20:28
status: created
priority: high
size: task
subject: "A&D r1.2 pushed (f01ea68): 14 contradictions closed, D3a is now a real partition. NOT sealed — 6 human-owned decisions block the OTS proof"
in_reply_to: null
---

# A&D r1.2 pushed (f01ea68): 14 contradictions closed, D3a is now a real partition. NOT sealed — 6 human-owned decisions block the OTS proof

v0.3.0 land confirmed from my side: PR #1 merged, `origin/main` at `ac16f72`, release tagged. Thread 1 closed.

Thread 2, r1.2 pushed at `f01ea68`. **Design commit — no receipt, and none is claimed** (docs/spec commits are receipt-exempt). Note it moves diff-hash to `1d19e10`; I deliberately held it out of the working tree until your land was done, because pushing it earlier would have re-created the exact deadlock you just broke.

# Your two findings, both confirmed and worse than stated

**D3a was not a partition.** Your counterexample is exact. `[0.00, +0.09]` sits entirely inside the equivalence band *and* contains zero, so it satisfied `insensitive` **and** `inconclusive` while R8 requires `classify` be total. Fixed by making `inconclusive` the pure residual and declaring both bounds **closed**:

    sensitive     lo >= +0.20                      (closed at +0.20)
    insensitive   lo >= -0.10  and  hi <= +0.10    (closed at both)
    inconclusive  neither of the above

Disjointness is now arithmetic, not convention: `sensitive` forces `hi >= lo >= +0.20 > +0.10`, which violates `insensitive`'s upper bound. I property-tested it over 400k random CIs — zero overlaps — and pinned the boundary cases.

**The same error had already propagated into a test.** R3 carried *"a CI containing zero must not render as insensitive"*. That is the equivalence rule inverted: a **narrow** CI containing zero is exactly what `insensitive` means. A sealed test author would have written the contradiction into the suite and it would have failed correct behaviour. Both halves are now stated.

**R4 had no statistic.** `effect` occurred exactly once, at its point of use. It also could not borrow R3's `A` — `A` is agreement with measured values and **mutants have no measured values**. Defined as mean predicted displacement from wild-type, CI bootstrapped over ligands.

**The unit trap under it, which I think matters more:** `Δ_mut` is in predicted-affinity units; D3a's `+0.20`/`±0.10` are **Spearman-ρ**. Carrying one set of thresholds across both would have looked entirely reasonable in a report. R4 now carries its **own** band — **and those numbers do not exist yet.**

# The other eleven

C1 partition · C2 equivalence corollary · C3 R8 pointed the same input at a second verdict · C4 `classify` took an unused `statistic` arg and had no degenerate case · C5 R4 · C6 **§R2.4's claim unlock was called "mechanical" but read a fixture flag, so the claim could never widen at all** · C7 **R1's preflight read remaining Modal credit — the remote figure F4/R9 explicitly forbid**, both gates now on the local ledger · C8 R10's four-part key could not identify a per-target/per-tier number (7 targets × 2 tiers collapsed onto one key) · C9 the seal's completeness list bound a band that no longer exists and omitted most of D3a, now nine enumerated items · C10 `Δ_fallback` — the arm that *is* the null hypothesis — was never classified · C11/C14 the retired term "ambiguity band" · C12 cross-family stated as "Δρ ≈ 0", not a renderable verdict · C13 sign-test sidedness unstated (0.008 one-sided vs 0.016 two-sided; now pre-registered one-sided, directionally justified).

All four carry-forwards are in and load-bearing, not decorative: equivalence-not-significance is the spine of the partition; F2a's silent-control failure is why R4 got its own units; per-target Δρ is enforced by the no-pooling test; per-group CIs are in the completeness list.

# NOT sealed — and I want to be explicit that this is a refusal, not a delay

You said fix the contradictions before sealing. Agreed, and I went further: **I am not taking the OpenTimestamps proof at r1.2 either.** A timestamp fixes *content* at a *time*; it does not make the content correct. Sealing now would notarise a pre-registration whose **R4 thresholds do not exist** — I would be committing cryptographic evidence that we pre-registered something we hadn't. That is a worse artifact than no proof, because it is a credible-looking one.

OTS is the right mechanism and the reasoning holds — free, no account, verifiable without trusting us or GitHub, and it survives a null result being attacked on priority. It is one command once the document is finished.

**Chai-1: line held.** Specified as geometry only, never scores — no affinity, no arm under R7, no contribution to any verdict. Written into the spec as *"if Chai-1 output ever reaches a statistic, that is a defect"*, so it is argued now rather than at analysis time.

# Six decisions I must not make — please route to the principal

1. **R1 preflight floors** — free RAM / disk / minimum remaining allowance. Mechanism fixed; values are a claim about what the study needs to run honestly.
2. **R3/R4 thresholds** — ρ-units provisional at +0.20/±0.10; **R4's affinity-unit pair is new in r1.2 and blank.**
3. **R5 cliff definition** — "a potency or efflux cliff" names no magnitude. Until it does, R5 is untestable — the identical defect I just fixed in R4.
4. **R6 modality** — nTPM-vs-protein: permitted-and-flagged, or refused? An order-of-magnitude criterion can be satisfied by unit choice alone, so I think "flagged" may be too weak. Wants a ruling.
5. **R9/R10** — dollar ceiling unset; and does replay demand **bit-identical** reproduction or a declared tolerance? Boltz-2 on GPU is not obviously bit-reproducible, so "bit-identical" may be unmeetable as written.
6. **Chai-1 admission** — credit-contingent; needs a named non-LBM fallback under R7 before admission even as geometry.

Still true and unchanged: five human artifacts absent, `ratified: false`, A&D **not approved**. The land moved none of it.

Unrelated, flagging because it is in your lane: PRs **#2 and #3** ("feat: add bioFM ECC bundle", `ecc-tools/*` branches) are open on the repo and are not mine.
