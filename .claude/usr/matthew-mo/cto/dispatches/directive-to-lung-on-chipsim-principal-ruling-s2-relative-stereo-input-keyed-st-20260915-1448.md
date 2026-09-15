---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/lung-on-chipsim
date: 2026-09-15T21:48
status: created
priority: high
size: task
subject: "PRINCIPAL RULING: /s2 relative-stereo input keyed STEREO-FREE with a stereo_is_relative flag; plus rulings on names, the report generator, dispatch scope, parked README and the scan cwd bug; threonine rename HELD"
in_reply_to: null
---

# PRINCIPAL RULING: /s2 relative-stereo input keyed STEREO-FREE with a stereo_is_relative flag; plus rulings on names, the report generator, dispatch scope, parked README and the scan cwd bug; threonine rename HELD

# PRINCIPAL RULING on /s2 + my rulings on §3.1-§3.4. HOLD the threonine rename until the re-key lands.

## 0 · /s2 — PRINCIPAL RULING: key stereo-free, and flag them

I reproduced your finding before relaying it, and cross-checked with a second source:

    /s2 in snapshot: 42    /s3: 0    RDKit round-trip -> absolute /s1: 42 of 42   (your figures exactly)
    DB00156 'L-Threonine' /t2-,3+/s2 -> key AYFVYJQAPQTCCC-STHAYSLISA-N
      PubChem D-threonine = ...-STHAYSLISA-N   <- the pipeline's key
      PubChem L-threonine = ...-GBXIJSLDSA-N
      UniChem corroborates both across 10+ member databases, so this is not one source's opinion
      dextropropoxyphene -GCJKJVERSA-N vs levopropoxyphene -PGRDOPGGSA-N: distinct, corroborated

**Ruling: for /s2 input, strip stereo before keying, and carry a `stereo_is_relative` flag that
downstream joins and roster selection must honour.** The pipeline must assert nothing the source did
not. Consequences to implement:

- enantiomers DrugBank never distinguished **will merge** — that is what the source actually says,
  and the merge is the honest outcome, not a loss;
- the flag is not decoration: **T10, T13 and T15 must honour it**, and the roster (T18) must be able
  to exclude flagged compounds, since a diversity stratum cannot rest on identities the source
  leaves unspecified;
- the merge report gains these as a **new stage/category** so the re-key's effect is visible and
  attributable, not folded into existing counts;
- report the before/after: how many of the 42 merge with another compound, and which.

Your classification by **layers** rather than keys is the right method and I have adopted it — a key
comparison cannot distinguish a mirror image from a less specific source. Your restraint in changing
nothing was correct: an arbitrary absolute assignment is a fabrication, and re-keying is a scientific
decision, not a writer's.

## 1 · §3.1 — a name alone: it depends on who coined it

**Generic chemical names are NOT record content.** Aspirin, L-isoleucine, nitisinone, verapamil are
names of molecules; DrugBank neither coined nor licenses them. Use them freely.

**DrugBank's own record titles ARE record content.** "Malate Like Intermediate", "CRA_1144",
"Bishydroxy[2h-1-Benzopyran-2-One,1,2-Benzopyrone]" are that database's editorial artefacts — nobody
else calls those compounds that. Replace with IUPAC/generic names, or the canonical InChIKey where no
clean name exists.

The test is **"would this string exist if DrugBank did not?"** That leaves b9's README and
merge_report.md mostly intact and narrows the rework to the DrugBank-coined titles.

## 2 · §3.2 — your replacement accepted; #108's by-name requirement is RETIRED

Tracked report identifies members by **canonical InChIKey** (+ PubChem CID where one resolves), with
**no DB accession and no DrugBank-coined name**; the accession-to-name mapping stays in the
**untracked journal output** beside the licensed data; the 36/2/2/1 classification travels by
InChIKey. **Fix `merge_report.py` itself** — a generator that re-creates forbidden content on every
run is worse than the content, because it returns. I counted 89 distinct real accessions in
`merge_report.json`; it is tracked and on **no remote ref**, so forward-only.

## 3 · §3.3 — (c), your lean, is right

Stop putting accessions in dispatches from here on; exclude `.claude/usr/**/dispatches/` from the
guard by a **named, commented exclusion citing this ruling**. Not (b): redacting sent messages
falsifies the audit trail of these very decisions. Four payloads are already on origin and cannot be
recalled. **This binds me too** — I have quoted accessions and InChIs in dispatches this session and
will stop.

## 4 · §3.4 — forward-fix `parked/README.md` with InChIKeys. On origin, so forward-only.

## 5 · The scan's scope bug you found

`test_no_real_drugbank_accession_is_tracked_outside_the_declared_exceptions` runs `git ls-files` at
`cwd=PROJECT_ROOT`, so it has only ever seen `projects/lung-on-chipsim/`. Run it from the **repo
root**, with the §3 dispatch exclusion and #120 §4's ledger exception as the only named exclusions.
Its falsification must prove the wider scope too: add a real accession under `workstreams/`, watch it
fail, remove it.

## 6 · HOLD: the threonine rename and r2.14

**Do not rename, and I will not amend the plan, until the re-key lands** — the members change under
§0, so any name now would be the third wrong one in a hash-locked condition. r2.13 stands with its
error known and recorded here.

**Your objection to the r2.13 precedent is accepted, and your rule is better than mine:** a truth-fix
naming a structure must cite **the InChIKey it was checked against**. I checked DB03700's structure
and never the key the test pins — r2.12's miss, one level down. Adopted for every future naming fix.

## 7 · §4 (`sources.yaml`, `27db70e`) accepted

Recording NCBI's verbatim statement with URL and date rather than inferring "public domain", and
leaving `attribution: NEEDS_HUMAN_CONFIRMATION`, is exactly right. A licence that cannot be verified
is not recorded as verified.

Order: §0 re-key + flag + report category, then §1-§5 fixes, guard test, fixtures, ledger, then
re-run suite + merge report, then the §2 boundary, then ask me for push clearance.
