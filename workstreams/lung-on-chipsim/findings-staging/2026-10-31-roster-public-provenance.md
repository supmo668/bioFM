---
type: findings-staging
status: DRAFTED — UNRATIFIED, EXCEPT the Ipratropium bromide row, which is RULED (approvals row 87).
  The other 25 rows are `drafted` and the principal ratifies or rejects each.
authorization: principal ruling 2026-10-31, lung approvals rows 80-82 (route: principal), relayed via CTO #834
task: row 81 — public provenance for the 26 roster keys
agent: biofm/matthew-mo/lung-on-chipsim
measured_at: PubChem PUG REST, 2026-10-31, read in this pass
---

# Roster public provenance — DRAFTED, 2026-10-31

Task A of CTO #834, under approvals row 80: a canonical structure identifier beside a substance
name is permitted **when the pair cites a public source**. Every pair below cites PubChem, by CID,
read from PUG REST on 2026-10-31 in this pass. **No key and no CID is written from memory.**

**This note changes nothing.** `configs/poc_compounds.yaml` is untouched: T18 is the principal's
claim, and only their ratification moves the config, under a quality-gate boundary.

## What I measured, and where it DIFFERS from the lead I was given

CTO #834 supplied its own pass as a lead and told me to re-measure. I did, and three things differ:

| | lead (CTO #834) | measured here |
|---|---|---|
| keys resolving to a CID | 23 of 26 | **25 of 26** |
| keys resolving nowhere | 3 — Beclomethasone, Budesonide, Ipratropium bromide | **1 — Ipratropium bromide only** |
| Beclomethasone | "PubChem inchikey 404" | **resolves**, HTTP 200, one CID |
| Budesonide | "PubChem inchikey 404" | **resolves**, HTTP 200, one CID |

I am not claiming the lead was careless — I hit the same class of error myself in this pass, twice,
and both are recorded at the foot of this note. The point is only that the ratifiable number is the
re-measured one.

**A key is not 1:1 with a CID.** 3 keys return MORE THAN ONE CID: Epinephrine (2), Indacaterol (2), Procaterol (3).
Where that happens every CID is listed; the pair still cites a public source, but "the CID for
that key" is not a well-formed phrase for those rows and the note does not pretend otherwise.

## The 26 rows

| name | current key | PubChem CID(s) for that exact key | retrieved | class |
|---|---|---|---|---|
| Aclidinium | `ASMXXROZKSBQIH-VITNCHFBSA-N` | 11434515 | 2026-10-31 | drafted |
| Amlexanox | `SGRYPYWGNKJSDL-UHFFFAOYSA-N` | 2161 | 2026-10-31 | drafted |
| Beclomethasone | `IBIIDGIPJPTFBZ-XYWKZLDCSA-N` | 90726180 | 2026-10-31 | drafted |
| Bitolterol | `FZGVEKPRDOIXJY-UHFFFAOYSA-N` | 35330 | 2026-10-31 | drafted |
| Budesonide | `UNISKOOZAQCSPC-KWVAZRHASA-N` | 91218137 | 2026-10-31 | drafted |
| Clenbuterol | `STJMRWALKKWQGH-UHFFFAOYSA-N` | 2783 | 2026-10-31 | drafted |
| Dyphylline | `KSCFJBIXMNOVSH-UHFFFAOYSA-N` | 3182 | 2026-10-31 | drafted |
| Epinephrine | `UCTWMZQNUQWSLP-VIFPVBQESA-N` | 5816, 139148732 | 2026-10-31 | drafted |
| Flunisolide | `XSFJVAJPIHIPKU-XWCQMRHXSA-N` | 82153 | 2026-10-31 | drafted |
| Fluticasone Propionate | `WMWTYOKRWGGJOA-CENSZEJFSA-N` | 444036 | 2026-10-31 | drafted |
| Formoterol | `BPZSYCZIITTYBL-UHFFFAOYSA-N` | 3410 | 2026-10-31 | drafted |
| Ibudilast | `ZJVFLBOZORBYFE-UHFFFAOYSA-N` | 3671 | 2026-10-31 | drafted |
| Indacaterol | `QZZUEBNBZAPZLX-QFIPXVFZSA-N` | 6918554, 86314533 | 2026-10-31 | drafted |
| Ipratropium bromide | `OEXHQOGQTVQTAT-JRNQLAHRSA-N` | **none for this exact key.** Source of record: **pinned snapshot**; no PubChem record for this exact stereo descriptor, 2026-10-31. Nearest public matches (same skeleton, differing stereo layer): CIDs 657309, 3746, 6604365, 25897919 | 2026-10-31 | **RULED — approvals row 87** |
| Isoetarine | `HUYWAWARQUIQLE-UHFFFAOYSA-N` | 3762 | 2026-10-31 | drafted |
| Montelukast | `UCHDWCPVSPXUMX-TZIWLTJVSA-N` | 5281040 | 2026-10-31 | drafted |
| Nedocromil | `RQTOOFIXOKYGAN-UHFFFAOYSA-N` | 50294 | 2026-10-31 | drafted |
| Pirbuterol | `VQDBNKDJNJQRDG-UHFFFAOYSA-N` | 4845 | 2026-10-31 | drafted |
| Procaterol | `FKNXQNWAXFXVNW-BLLLJJGKSA-N` | 688561, 5311369, 51599621 | 2026-10-31 | drafted |
| Roflumilast | `MNDBXUUTURYVHR-UHFFFAOYSA-N` | 449193 | 2026-10-31 | drafted |
| Salbutamol | `NDAUXUAQIAJITI-UHFFFAOYSA-N` | 2083 | 2026-10-31 | drafted |
| Salmeterol | `GIIZNNXWQWCKIB-UHFFFAOYSA-N` | 5152 | 2026-10-31 | drafted |
| Terbutaline | `XWTYSIMOBUGWOL-UHFFFAOYSA-N` | 5403 | 2026-10-31 | drafted |
| Theophylline | `ZFXYFBGIUFBOJW-UHFFFAOYSA-N` | 2153 | 2026-10-31 | drafted |
| Tiotropium | `LERNTVKEWCAPOY-KYQOMENCSA-N` | 3086655 | 2026-10-31 | drafted |
| Triamcinolone | `GFNANZIMVAIWHM-OBYCQNJPSA-N` | 31307 | 2026-10-31 | drafted |

## The one row that does not resolve, and why a re-key is NOT a substitution

**Ipratropium bromide** — current key `OEXHQOGQTVQTAT-JRNQLAHRSA-N`, PubChem PUG REST **HTTP 404** for that exact key.

A name lookup for `ipratropium` returns four records. Read from PubChem in this pass:

| CID | key | differs from the roster key in | formula |
|---|---|---|---|
| 657309 | `OEXHQOGQTVQTAT-BZQJJPTISA-N` | block 2 | `C20H30NO3+` |
| 3746 | `OEXHQOGQTVQTAT-UHFFFAOYSA-N` | block 2 | `C20H30NO3+` |
| 6604365 | `OEXHQOGQTVQTAT-SSZRJXQFSA-N` | block 2 | `C20H30NO3+` |
| 25897919 | `OEXHQOGQTVQTAT-PPAWOBCPSA-N` | block 2 | `C20H30NO3+` |

**What differs, stated from the records:** all four share the roster key's **skeleton block** and
its final block, and differ **only in block 2 — the stereo layer**. So this is not a salt, ester or
epimer difference in the connectivity: it is a stereo-descriptor difference. All four PubChem
records are the **cation** (`C20H30NO3+`), not a bromide salt, although the roster name says
"bromide". CID 3746 is the stereo-UNSPECIFIED record (`UHFFFAOYSA`); the other three are specific
stereoisomers whose IUPAC names PubChem gives as (1R,5S), (1S,5R)/(2R) and (1S,5R)/(2S).

### RULED, 2026-10-31 — approvals row 87 (corrects row 81)

**The principal ruled: the key STAYS.** The pinned snapshot is the source of record for this row,
and the four PubChem CIDs are recorded as *nearest public matches* rather than as replacements.
The ruling extends #120 §7 to **this one roster row only**.

So the identity-system conflict below is resolved in favour of the snapshot, and the row now reads
`source of record: pinned snapshot; no PubChem record for this exact stereo descriptor,
2026-10-31`. Nothing in `configs/poc_compounds.yaml` changes yet: the other 25 rows still await
ratification, and the config changes **once**, after that, under a quality-gate boundary.

The analysis that produced the ruling is kept below unchanged, because the ruling rests on it.

### Why I did NOT propose one of them as the replacement

Measured against the pinned snapshot:

- the **current** roster key **is** in the snapshot (6,610 distinct keys) **and** in the ATC R03 pool (39);
- **none of the four PubChem candidate keys is in the snapshot at all** — all four `in_snapshot=False`.

So a re-key to any PubChem-sourced key would not be a substitution. It would:

1. break `load_poc_roster(snapshot_keys=...)`, because the roster must resolve in the pinned snapshot;
2. break the published provenance chain *every roster key is one of the mechanically derived ATC R03
   candidates* — the claim pinned at `1400bf7` — since the new key is not in the pool;
3. put the roster and the pinned snapshot on **two different identity systems** for one compound.

That is a conflict between two sources, not a typo: the snapshot's key is what the pipeline is
pinned to, and PubChem's keys are what public provenance would cite. **Choosing between them is a
curation decision and it is the principal's** — and choosing among the three specific stereoisomers
is a second curation claim on top. Per the ruling I list the consequence and do not resolve it.

**The conservative option, named but not recommended by me:** leave the key as it is and record
that it has no PubChem counterpart, which is a true statement about a snapshot-derived identity and
costs nothing downstream. The 25 other rows are unaffected either way.

## Two instrument failures of my own, in this pass

Recorded because both would have produced a confident wrong answer, and because this project's
standing lesson is that the instrument is checked before the result is read.

1. **A multi-CID key read as a failure.** My first classifier required the whole response body to be
   one digit string, so the three keys returning several CIDs were classed UNMEASURED. Retrying
   showed HTTP 200 every time, which is what exposed it: a transport failure does not return 200
   three times in a row. Had I trusted the first tally I would have reported 22 resolving and three
   unmeasured, and the three would have looked like the lead's three.
2. **I shadowed the standard library.** A scratchpad file I had named `inspect.py` sat in the
   directory I then ran scripts from, so numpy's `import inspect` picked up mine and the run died
   inside pandas. Renamed. The hazard is documented in this environment's own notes and I walked
   into it anyway.

## What this note does NOT establish

1. **Nothing here is ratified.** Every row is `drafted`. The config is untouched.
2. **A resolving CID is not a confirmation that the roster name is right for that key.** I measured
   key→CID. The lead reported synonym matching for 21 of 26 and two partial cases; I did not
   re-measure that and make no claim about it.
3. **No DrugBank record content appears here** — no accession, no DrugBank field, no
   `(accession, name, structure)` tuple. Name+key+CID triples only, each citing PubChem, which
   approvals row 80 permits.
4. **I did not establish why the one key has no PubChem counterpart.** Stereo encoding is what the
   records show differs; *why* the snapshot carries that descriptor is not something I measured.
