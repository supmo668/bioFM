"""Guards: tracked DECLARATIONS of what is permitted, plus a refusal, plus a registry.

ONE module lives here on this branch: `output_roots`, which owns WHERE record-bearing output may
be WRITTEN. It is a **tracked declaration** of what is allowed (`DECLARED_OUTPUT_ROOTS`), a
**refusal** rather than a computation — its job is to say no and say why, not to return a value a
caller may interpret — and a **registry** (`RECORD_BEARING_WRITERS`) that makes omission visible,
so a new writer cannot silently opt out.

WHICH HALF THIS PACKAGE ENFORCES, AND WHICH IT DOES NOT. `output_roots` enforces the NAME half of
the principal's identifier invariant: it stops a payload carrying a compound NAME beside a
structure from reaching a tracked path at all. It does not scan content and makes no claim about
accessions already in the tree. That other half was the repo-wide scan, work item E-21…E-23, which
**closed at scope reached with 36 registered findings**; the successor guidance (plan-approval-log
row 61) is *do not open by repairing the register*. Its six modules — `record_content`, `decoding`,
`errors`, `policy`, `repo`, `report` — are therefore ABSENT BY RULING, not by oversight, and this
package must not be used as the hook that reintroduces them.

WHY THIS FILE IS SHORT. The Stage 1 version of this docstring described seven modules and the whole
E-23 architecture, and it recorded that it had **gone stale three times** — each time because "a
change audits what it wrote and not what it invalidated", and a charter is the file least likely to
be re-read and most likely to be believed. Restoring that text here would have described six modules
this branch does not contain, committing the exact defect the file documents. It is rewritten to the
present extent instead. If a module is added back, this docstring is part of that change.
"""
