---
type: escalation
from: biofm/matthew-mo/lung-on-chipsim
to: biofm/matthew-mo/cto
date: 2026-09-14T22:31
status: created
priority: high
size: task
subject: "T4 ruling needs an amendment after all: (b)/(c) name data/raw/drugbank.dvc, which cannot exist while any tracked file is inside (dvc source, both backends). Not executed."
in_reply_to: 95
---

# T4 ruling needs an amendment after all: (b)/(c) name data/raw/drugbank.dvc, which cannot exist while any tracked file is inside (dvc source, both backends). Not executed.

# T4 ruling needs an amendment after all — (b) and (c) name a file the ruling cannot create. Not executed.

r2.10 merged, `plan-gate verify` passes on `de4b812`. Organism ruling acknowledged.
Canonicalization untouched while the over-merge question is open.

## 1. The ruling satisfies (a) and (d) — and cannot satisfy (b) or (c) as signed

Individual adds produce **three pointers inside the directory**:

    data/raw/drugbank/drugbank.tsv.dvc
    data/raw/drugbank/drugbank-slim.tsv.dvc
    data/raw/drugbank/proteins.tsv.dvc

T4 as signed at `build-plan.md:363-364`:

    (b) data/raw/drugbank.dvc exists, is tracked by git, parses with non-empty outs[0].md5
    (c) dvc status data/raw/drugbank.dvc reports up-to-date

Neither file exists under the ruling. Reporting T4 done would mean passing a different
layout off as the signed one — the exact "done-condition met by renaming it" shape we have
spent this workstream removing. So I have **not** executed, and "no signed done-condition
needs amending" does not hold.

## 2. A single `data/raw/drugbank.dvc` is impossible while any tracked file is inside — from source, both backends

`dvc/output.py:670` raises `OutputAlreadyTrackedError` when `scm.is_tracked(self.fspath)`.
`is_tracked` on the directory is true if **any** tracked file lies under it:

    scmrepo/git/backend/gitpython.py:341   return bool(self.repo.git.ls_files(path))
    scmrepo/git/backend/dulwich/__init__.py:452
        return any(p == rel or p.startswith(rel_dir) for p in self.repo.open_index())

(pygit2 raises NotImplementedError and falls through.) Both implementing backends agree.
**`.dvcignore` cannot help** — the check reads git's index, not dvc's ignore rules. This is
read from the installed source (dvc 3.67.1), not inferred from the error message.

Your correction is right that `provenance.yaml` **alone** is sufficient to cause the
collision, and that the pointer is a sibling so never part of it.

## 3. `SHA256SUMS.json` — we were each right about a different ref

- **trunk (`main`):** not tracked. Your `ls-files` is correct.
- **`lung-on-chipsim`:** tracked since **`b16385c`** (T4a) — `git ls-files` lists it; it
  simply has not landed. So on my branch T4(d) is **already met**, and the collision
  there involves both files, which is what I reported.

Neither changes the conclusion in §2 — one tracked file is enough.

## 4. The choice, which is yours (or the principal's)

- **(i) Amend (b)/(c)** to the three per-file pointers, each tracked, each with non-empty
  `outs[0].md5`, `dvc status` clean on all three. Smallest change; metadata stays where
  the loader, `.gitignore:27,33`, and T11's tests expect it.
- **(ii) Keep (b)/(c) verbatim; move `provenance.yaml` + `SHA256SUMS.json` out of the
  directory** (e.g. `data/raw/drugbank.provenance.yaml`). Signed conditions untouched, but it
  moves a contract-bound human artifact and touches the loader, `.gitignore`, the vendoring
  allow-list, and T11 — more surface.

I lean (i): it amends a condition's *filename*, not its substance, and (ii) edits a sealed
human artifact's location to preserve a path string. But that is a plan edit, so it needs
a signature. **Ready to execute either within minutes of a ruling.**

## Also

Four of my five duplicate monitors were running from plugin **0.52.0** — they survived an
upgrade, which is why every "restart" stacked another. Stopped; one live monitor now
(pid 53533, 0.54.0).
