# Plan approval log — lung-on-chipsim

**Append-only.** One entry per `plan-gate sign`, newest last. `plan-approval.md` beside this file
is tool-owned and is rewritten from scratch on every sign; **this file is the provenance**. The
quality gate fails when the newest entry's `hash` differs from `plan-approval.md`'s `plan_hash`.
Routes: `human-direct` (the principal signed or instructed the sign in so many words) ·
`standing-delegation` (CTO invoked under the delegation recorded 2026-09-10, `fd2c00d`; the
judgement was the principal's, the invocation was not) · `principal-directed` (pre-delegation
form of the same thing). Introduced by r2.15 item 6; entries before it are reconstructed from
`git log -p plan-approval.md` and marked *(reconstructed)*.

| # | rev | hash | route | signed | commit | authorising rulings / notes |
|---|-----|------|-------|--------|--------|-----------------------------|
| 1 | r2 | `737a8d9` | human-direct | 2026-08-30 16:53 | `1132fda` | G4 "Over and out" in /grill-me; build authorized. Last **human-direct** hash until #10. *(reconstructed)* |
| 2 | r2.x | `b79a5e4` | principal-directed | 2026-08-31 | `817485c` | re-sign notified to agent; standing rule on hash-locked plan. *(reconstructed)* |
| 3 | r2.5/6 | `a44e523` → `594301b` | principal-directed | 2026-09-01 20:05 / 21:04 | `76f494f` / `f3dc780` | reframe hold; S12 landing. *(reconstructed)* |
| 4 | r2.7 | `bc61506` | principal-directed, cto-invoked | 2026-09-03 01:56 | `a9c8629` | signed on principal instruction; B4 provenance block added. 02:08 agent re-sign stripped B4 (incident, `d4151eb`); restored `8d3df2c`/`7c21302`. *(reconstructed)* |
| 5 | r2.8 | `373931c` | standing-delegation | 2026-09-10 12:40 | `fd2c00d` | delegation of `plan-gate sign` recorded — invocation delegated, judgement is not; panel seal explicitly excluded. *(reconstructed)* |
| 6 | r2.9 | `db3d10b` | standing-delegation | 2026-09-14 13:28 | `d5b243f` | 10th reframe survivor + C4 uv-run fix; 8 unparseable compounds ruled. *(reconstructed)* |
| 7 | r2.10 | `de4b812` | standing-delegation | 2026-09-14 15:24 | `d191421` | principal 2026-09-14 organism-label ruling (accept `Human` and `Homo sapiens`). Marker stripped a 3rd time and restored. *(reconstructed)* |
| 8 | r2.10 | `de4b812` | **human-direct** | 2026-09-15 01:01 | `0b8d0c3` | principal: "approve r2.10 sign". Same hash as #7; supersedes its route. Prior human-direct: `737a8d9`. |
| 9 | r2.11 | `26b7a4f` | standing-delegation | 2026-09-15 01:40 | `3d8be06` | principal 2026-09-15 T4 ruling: three per-file DVC pointers. Marker stripped a 5th time and restored. *(reconstructed)* |
| 10 | r2.12 | `16b0cc9` | standing-delegation | 2026-09-15 11:19 | `d230c3b` | principal 2026-09-15 stereo-layer ruling: `/t /m /s` only, `/b` excluded. Marker stripped a 6th time and restored. *(reconstructed)* |
| 11 | r2.13 | `ebc5542` | standing-delegation | 2026-09-15 12:43 | `a673207` | T5b names L-threonine vs D-allothreonine (DrugBank mislabels DB03700). Marker stripped a 7th time; no-ruling gap disclosed. *(reconstructed)* |
| 12 | r2.14 | `d83fceb` | standing-delegation | 2026-09-15 15:19 | `6add2ec` | relative-stereo (/s2) handling, flag persisted, roster members pinned by InChIKey. *(reconstructed)* |
| 13 | r2.15 | _pending_ | _pending_ | — | — | nine-decision grill 2026-09-15 (session biofm-14): artifact authorship split; roster after guard; one session per tree; sequence; panel signing at M1; this log; principal's 3-day window; AM-6 and theta_priors editorial. |
