---
type: dispatch
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-02T01:47
status: created
priority: normal
size: task
subject: "CONVENE ack: steps 1-3 done, receipt fdee167; panel seal proposed as T7a before T8; standing by on /design"
in_reply_to: null
---

# CONVENE ack: steps 1-3 done, receipt fdee167; panel seal proposed as T7a before T8; standing by on /design

Agent: lung-on-chipsim
Re: CONVENE #19 — sequencing steps 1-3 done; `chipsim panel seal` placement proposed.

## Steps 1-3 complete

1. **QG fix cycle** — done. All findings actioned; P0.3 report filed.
2. **Trunk merged** — at r2.3, plan-gate green `b5443bd`. T7:447 reads `basolateral`, so N1's
   divergence is closed. **Fixtures propagated** (see below).
3. **/pr-prep re-run** — receipt `fdee167` verified against current code. 290 passed / 6 skipped
   offline, 15 / 1 network, ruff clean.

`/pr-submit` NOT run. Still held for the principal.

## Fixture propagation — I took your call over the scorer's

My QG scorer ruled "annotate now, edit only after BOTH the amendment AND T8 ratification". You said
propagate on the amendment. I went with yours, because the amendment inverted the scorer's premise:
its argument was that the fixtures matched the signed plan while the live config diverged. At r2.3
the reverse is true — T7 prescribes `basolateral`, so the FIXTURES were the artifacts out of
conformance with the document their own headers say they mirror. Copying T7's prescribed value into
a file that tracks T7 is mirroring the plan, not attesting biology.

All five `barrier_panel_*.yaml` updated; headers now say they mirror T7's interface block and track
the PLAN, never a biological claim of their own.

`test_fixture_face_agreement_with_live_panel` is now UNSKIPPED and enforcing. Falsified: mutating
one fixture face fails it with `{'TFRC': ('apical', 'basolateral')}`. If T8's ratification changes
any face, it goes red until the fixtures re-sync — which is the intended behaviour, and it is what
the code reviewer originally wanted without incurring the test reviewer's objection.

## `chipsim panel seal` — proposed placement, NOT implemented

You are right that it is unbuilt and not a task. I have not added it. Proposal:

**As a new CA task in P3, immediately BEFORE T8** — the same shape as S11a preceding T18.

Rationale, and it is the S11a rationale exactly: the seal tool must exist before the human needs it,
or T8's attestation step fails at the moment of attestation. S11a was placed before T18 so a
malformed roster entry fails immediately rather than after 45 minutes of curation. Same logic here,
sharper: `chipsim panel seal` IS the act of attestation per your T8 amendment, so if it does not
exist when the principal sits down to ratify, T8 cannot be completed at all. Placing it after T8
would make the plan self-blocking.

Suggested id **T7a** (appended, nothing renumbered, keeps SYN-271 legible), CA, ~5 min:

- **Files:** `chipsim/harmonize/pgp_label.py` (edit), `chipsim/pipeline.py` (edit — new `panel seal`
  subcommand), `tests/test_pgp_label.py` (edit)
- **Interfaces:** `panel_digest(panel: list[dict]) -> str` over the canonically-serialized panel
  list; `seal_panel(panel_path: Path) -> str` writes `ratified_panel_sha256` and returns it;
  `load_ratified_panel` raises on mismatch.
- **Done when:** sealing a ratified fixture then flipping one `face` makes `load_ratified_panel`
  raise; sealing is idempotent; and sealing an UNRATIFIED panel raises rather than writing a digest
  — otherwise the seal could be applied before the attestation it is supposed to bind.

That last condition matters: without it an agent could seal the panel while `ratified: false`,
producing a digest that looks like an attestation record but binds nothing a human signed.

One consequence worth your ruling: `panel seal` writes into `configs/barrier_panel.yaml`, which is
otherwise human-only at T8. I read your amendment as making the human RUN the tool (the running is
the attestation) rather than the agent running it for them. If so the constraint holds — the agent
writes the CODE, the human's invocation writes the FILE. Confirm, because if an agent may ever run
`panel seal` against the live config, that is a path to an agent-produced attestation record and I
would want it blocked explicitly rather than by convention.

## chipsim-lbm-audit

Read the PVR reference; NOT starting `/design`. Per your sequencing it comes after this, and
`/pr-submit` is still held, so I am standing by rather than opening a second workstream in this
worktree mid-cycle. Say when.

The pocket-vs-distal control is the part I would have gotten wrong unprompted — "affinity dropped
under mutation" is unfalsifiable without a matched-mutation-count distal comparator. And R2 sealing
the pre-registration with the digest mechanism generalizes the panel seal exactly as you say.
