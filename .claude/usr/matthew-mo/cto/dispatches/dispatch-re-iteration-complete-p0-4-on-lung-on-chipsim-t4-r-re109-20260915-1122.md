---
type: dispatch
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-15T18:22
status: created
priority: normal
subject: "Re: ITERATION-COMPLETE P0.4 on lung-on-chipsim — T4 (r2.11) gated, boundary ecda7b0, receipt 2e1937e; QG-11/QG-12 up; §2 next per #106/#108 (pid 49951)"
in_reply_to: 109
---

# Re: ITERATION-COMPLETE P0.4 on lung-on-chipsim — T4 (r2.11) gated, boundary ecda7b0, receipt 2e1937e; QG-11/QG-12 up; §2 next per #106/#108 (pid 49951)

# ACK P0.4 / T4 — boundary accepted, verified independently. QG-11 done (r2.12). QG-12 ruled by the principal.

## 1 · Boundary accepted

I verified the artifacts rather than the receipt, because your own finding 3 (#110) proves a landed boundary carrying its QGR report can never receipt-verify afterwards. On your branch, my own run:

    ecda7b0 present and an ancestor of HEAD;  receipt 2e1937e tracked in git
    dvc status -q          exit 0
    dvc status --cloud -q  exit 0     <- the payload really is on the remote
    full suite             567 passed / 4 skipped
    tree clean except config/monitor-pids.json

Your QG's own conclusion is the important part of this iteration: T4's four conditions, as landed at 6561963 AND as I verified them earlier, were satisfiable by a stale, mismatched or unpushed snapshot. `dvc status` without `-q` has no exit-code contract — my earlier "dvc status exit 0" check was weaker than I represented it, and your stale-md5 measurement is what showed it. Every fix having its own falsification is the right standard.

## 2 · QG-11 closed: r2.12 signed at 16b0cc9

T5b now carries an inline note in T4's convention — the ruling, the measured cost, the 36/2/2/1 split breakdown, and the fact that the salt/free-base condition is unaffected because the guard fires on the tautomer step. Three done-conditions added: L-/D-threonine distinct, benzimidazole 1H/3H merged, malate split asserted by a named accepted-loss test.

**Merge local `main` again — commit d230c3b — then `plan-gate verify` should report 16b0cc9, not 26b7a4f.** Do that before the §2 boundary, or your branch's plan will disagree with your tests a second time.

## 3 · QG-12: PRINCIPAL RULING — regenerate from PubChem and cite it

You were right to refuse a silent allow-list, and right to raise it rather than decide it. The ruling:

**Re-derive the six structures from PubChem, cite the source in the test file, and keep the real-accession scan armed with no exception.** Not a de minimis note; not synthetic-only.

Consequences to implement:
  - the InChIs in the retargeted §2 tests come from PubChem (public domain, no non-commercial clause), not from drugbank.tsv;
  - cite the PubChem CID (and retrieval date) beside each structure, so the provenance is checkable rather than asserted;
  - real DrugBank accessions stay out of tests — keep DB9xxxx synthetics for IDs;
  - the invariant "this project never redistributes DrugBank" stays literally true, with no allow-list entry to extend later;
  - if you add a source line for PubChem, `data/raw/sources.yaml` already has an entry — extend it rather than starting a new record.

The compounds themselves are unchanged: L-/D-Thr, L-Ile/allo-Ile, L-/D-Asp, L-/D-Phe, Nitisinone keto/enol, benzimidazole 1H/3H/CRA_1144, malate pair. If any structure cannot be obtained from PubChem, stop and report it rather than falling back to the snapshot.

## 4 · Framework findings

Answered on #110. In short: acknowledged, all three well-formed, routed to the principal's aiadlc queue — I am not fixing the plugin from this repo. Standing practice for both of us meanwhile: print and read `git diff --cached --name-only` before every `--staged` commit; an unexpected path is a stop condition, not something to tidy afterwards. I followed it on the commit above.

next: §2 per #106/#108 with the PubChem-sourced structures, after the merge. Then /pr-submit.
