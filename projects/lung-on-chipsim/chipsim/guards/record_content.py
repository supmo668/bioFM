"""The record-content guard: what a tracked file may be, and what may excuse it.

Extracted from `chipsim.ingest.drugbank_snapshot` at r2.25 (E6-6). That module is about ingesting a
pinned compound snapshot; this one is about a question with nothing to do with DrugBank — CAN THIS
REPOSITORY'S TRACKED FILES BE READ, who owns them, and which of them are declared. The two had grown
together until the guard was 1200 lines of a 2000-line ingest module.

WHAT THE GUARD KNOWS: containers and their magic, decodability, repository topology, project
ownership, the declaration surface, and the report a human reads.

WHAT IT DOES NOT KNOW, AND MUST NOT: anything about DrugBank. The extraction's one non-mechanical
seam (named in the r2.25 clause) was `undecodable_unallowed` reaching into the DrugBank exclusions.
That is not one question but TWO, and conflating them would be a defect:

  * `readability_waived(root, rel)` — "this file's readability is not this gate's business."
    WHAT IS WAIVED IS THE OWNING PROJECT'S CHOICE, and this docstring must not assert its contents.
    It said, as present fact, that "dispatch payloads are waived by ruling (#122 §3) and never
    scanned either way" — r2.27 E-19 DELETED that clause, and the DrugBank policy today waives
    nothing for readability, so dispatch payloads ARE scanned and, being unowned, DO fail here.
    `drugbank_snapshot` says so in terms while this file said the opposite (r2.27 §11 QG). It
    deliberately does NOT cover the exclusion LEDGER: the ledger's content IS still read, so its
    readability is exactly what this check is for.
  * `content_exempt(rel)` — "this path is ALREADY exempt by the content mechanism", so a declaration
    on top would exempt it twice and make it invisible to both halves of the guard. This one DOES
    cover the ledger.

THE TWO HAVE OPPOSITE SAFE DIRECTIONS, so neither is defaulted. Waiving nothing makes the scan
NOISIER (more files read); exempting nothing makes it QUIETER (the double-exemption defect never
fires, so a declaration holds and its file is cleared). An earlier version of this module defaulted
both to "refuse nothing" and claimed in this docstring that the result was fail-closed. A reviewer
measured the opposite: the default cleared a file the real policy fails. The policy is therefore
REQUIRED at every call site — the same reasoning this module already applies to `recognised`.
"""

from __future__ import annotations

import re
import tempfile
from contextlib import contextmanager

# Aliased: two loops in this module already bind a variable called `field`, and ruff caught the
# shadowing the moment the import arrived.
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from pathlib import Path

import yaml

from chipsim.guards.decoding import (
    _container_magic,
    _is_readable,
    _sha256,
)
from chipsim.guards.errors import (  # noqa: F401
    DeclarationDataUnusable,
    GuardInvariantViolated,
    RecordContentScanError,
    ScanNotPerformed,
)
from chipsim.guards.policy import (  # noqa: F401
    NOTHING_WAIVED,
    ContentPolicy,
    nothing_is_content_exempt,
    nothing_is_waived,
)
from chipsim.guards.repo import (
    _MINIMUM_PLAUSIBLE_TRACKED,
    _tracked_listing,
    materialise_index,
    repo_root,
)

# `RecordContentScanError` is re-exported DELIBERATELY: it is the base of the vocabulary this
# module raises, and callers and tests reach it here. `noqa: F401` because ruff's autofix deleted it
# the moment this file stopped raising the base directly — the same autofix that deleted re-exports
# five tests reached through earlier in this workstream, and which produced an ImportError in the
# SHIPPED command while the suite stayed green, because I ran the formatter after the tests rather
# than before them.
# The policy vocabulary is a LEAF now (r2.29): `ingest` imported this entire ~1,330-line module
# to construct a two-field dataclass, so the seam that exists to keep the guard ignorant of DrugBank
# was forcing DrugBank to depend on the guard. Re-exported because callers and tests reach these
# names here.
# The data types and the renderer moved to `report` (r2.29): it imports no filesystem, no git
# and no YAML, which turns "the renderer decides nothing" from a claim into a check.
from chipsim.guards.report import (  # noqa: F401
    RecordContentScan,
    ScanRow,
    render_path,
    render_scan,
)
from chipsim.journal import source_root

#: Any file in a dispatches/ directory, whatever its suffix. The waiver pattern above is `.md`-only
#: by design; THIS one is the never-declarable class. A non-.md payload is exactly what E6-4 keeps
#: failing here, so matching on the waiver's pattern would have exempted the one file the rule is
#: for — `leak.pdf` walked straight through it.
_DISPATCH_DIRECTORY_RE = re.compile(r"^\.claude/usr/(?:[^/]+/)+dispatches/[^/]+$")


#: This module's project, DERIVED. A bare literal bound to nothing meant that renaming the
#: project directory turned every path this project owns into "somebody else's": failing_undeclared
#: returns [] and THE GATE GOES GREEN — fail-open, reached by a rename nobody would think of as a
#: guard change.
THIS_PROJECT = Path(source_root()).name

#: Which project OWNS a repo-relative path (r2.22, E6-1b). Explicit, because the alternative is a
#: default, and a default here would silently make somebody else responsible for a failure they
#: cannot see. Order matters: the first matching prefix wins.
#:
#: A path matching NOTHING is UNOWNED BY DEFINITION, never "somebody else's" — and unowned FAILS
#: this gate. That rule is LOAD-BEARING FOR E6-4: `.claude/usr/**/dispatches/` belongs to no
#: project, so a non-.md dispatch payload keeps failing here. Without it, scoping would have made
#: `dispatches/leak.pdf` listed and unfailable ANYWHERE — re-opening the hole E6-4 closed one
#: clause above, in the same revision that closed it.
#: The WHOLE map (r2.22 calls it "an explicit map"). `workstreams/` used to be a hardcoded branch
#: below, outside the constant whose docstring calls itself the source of truth, so a reader
#: auditing the map saw two thirds of the rule.
#: (prefix, owner segment index, the tracked file that PROVES the owner exists). The marker is
#: what stops an owner being minted by mkdir: `libs/ghost-lib/payload.bin` used to report
#: `owner=ghost-lib [listed]` and exit 0, so a payload parked under a name nobody owns failed the
#: only gate that exists. The docstring below already condemned exactly this at depth 1
#: (`projects/README.pdf` -> owner "README.pdf"); this is that hole one segment deeper.
_OWNERSHIP_PREFIXES = (
    ("projects/", 1, "pyproject.toml"),  # projects/<owner>/...
    ("libs/", 1, "pyproject.toml"),  # libs/<owner>/...
    ("workstreams/", 1, "plan/build-plan.md"),  # workstreams/<owner>/...
    ("paper_standalone/", 0, "README.md"),  # the directory IS the project
)


def marker_backed_owners(paths) -> frozenset[str]:
    """Projects proved to exist by a TRACKED MARKER alone, independent of any declaration.

    This is the set used to answer "may this path be declared HERE?" — deliberately the WIDER of
    the two, because for the placement rule widening is the safe direction. Answering placement
    with the narrowed set made the registry police itself: delisting a project turned its artifacts
    into "unowned" paths, and unowned paths may legally be declared at the repo root, so one edit to
    one file cleared another team's artifacts with no defect reported.

    The marker is evidence the registry does not control, which is what breaks that circle.
    """
    tracked = set(paths)
    found: set[str] = set()
    for prefix, index, marker in _OWNERSHIP_PREFIXES:
        head = prefix.rstrip("/")
        if index == 0:
            if f"{head}/{marker}" in tracked:
                found.add(head)
            continue
        for rel in tracked:
            parts = Path(rel).parts
            if (
                len(parts) > index
                and parts[0] == head
                and f"{head}/{parts[index]}/{marker}" in tracked
            ):
                found.add(parts[index])
    return frozenset(found)


def recognised_owners(paths, surface: DeclarationSurface) -> frozenset[str]:
    """The projects that DEMONSTRABLY exist.

    TWO independent conditions, and an owner needs BOTH (r2.24 E-11):

    * a tracked MARKER, so the directory alone cannot mint an owner — the attacker's own file had
      to create the directory, which makes its existence worth nothing as evidence; and
    * a place in the DECLARED registry at the repo root, once that registry exists.

    The registry NARROWS, never widens. A marker alone does not mint an owner and neither does a
    declaration alone, so minting one means editing a tracked declaration file AND adding a marker —
    both reviewable. Until the registry exists the marker stands alone, and it is a MITIGATION, not
    proof: it is addable by anyone who adds a `pyproject.toml`, and the report says so.
    """
    read = surface
    if read.structural_error:
        # UNKNOWN is not "no registry yet". Treating a BROKEN registry as absent fell back to the
        # wider marker-backed set, so paths under an unregistered owner stopped being unowned and
        # stopped failing — with the report's own banner asserting "more files fail, never fewer"
        # directly above the rows that had just gone fail-OPEN. Unknown narrows to nothing: every
        # path becomes unowned, and unowned fails HERE.
        return frozenset()
    found = marker_backed_owners(paths)
    declared = read.registry
    return found if declared is None else found & declared


def path_owner(rel: str, recognised: frozenset[str]) -> str | None:
    """The project owning a repo-relative path, or None when no project owns it.

    An owner must own a SUBTREE. `projects/README.pdf` used to return "README.pdf" — an invented
    project — so a stray file directly under `projects/` failed NOBODY's gate: listed under a
    fabricated owner, skipped by the accession scan as unreadable, live test green. That is the
    double-exempt hole E6-4 closed, re-opened one function below the comment calling
    unowned-fails-here LOAD-BEARING FOR E6-4. `projects/../configs/x` returned ".." the same way.

    `recognised` is REQUIRED, not defaulted: an optional registry would let any future caller opt
    back into invented owners by omitting it, which is the same shape as the `root=None` parameter
    this revision removed one function below.

    Unowned is the SAFE answer here (it fails this gate), so every doubtful shape returns None.
    """
    parts = Path(rel).parts
    if not parts or ".." in parts or Path(rel).is_absolute():
        return None
    for prefix, index, _marker in _OWNERSHIP_PREFIXES:
        head = prefix.rstrip("/")
        if parts[0] != head:
            continue
        if index == 0:
            return head if head in recognised else None
        # An owner owns a subtree: there must be a segment AFTER the owner segment.
        if len(parts) > index + 1:
            # ...and the owner must EXIST. An unrecognised name is unowned, which fails here,
            # rather than somebody else's problem, which fails nowhere (E-03).
            return parts[index] if parts[index] in recognised else None
        return None
    return None


#: WHERE declarations live. Per-project data following the ingest module's `DRUGBANK_ID_LEDGER`
#: precedent of pointing at `configs/` rather than inlining (r2.21 E6-1) — the precedent stands even
#: though the ledger itself stayed behind in that module at the E6-6 extraction — plus a repo-root
#: surface
#: for paths no project owns (r2.23 E-05). The guard reads the UNION of the two.
#:
#: The placement rule is the whole point of E6-1 and is ENFORCED below, not merely documented: the
#: project file may declare only what THIS project owns, and the repo-root file only what NOBODY
#: owns. 24 paths belonging to other teams were once declared inside this module's source, so
#: another team adding a figure turned this module's gate red and the repair landed in a file they
#: neither own nor can judge.
PROJECT_DECLARATION_FILE = f"projects/{THIS_PROJECT}/configs/record_content_declarations.yaml"
REPO_DECLARATION_FILE = "config/record_content_declarations.yaml"

#: Declaration files are short lists of claims. The bound is what stops an alias-expansion or
#: oversized document from making the gate permanently un-runnable, which is the one denial this
#: mechanism is exposed to.
_MAX_DECLARATION_BYTES = 1 << 20

#: A content pin is exactly 64 lowercase hex characters. Anything else cannot match a sha256 and
#: would sit in the data looking like coverage.
_SHA256_RE = re.compile(r"[0-9a-f]{64}")

#: `why` is required. A declaration is a CLAIM, and "none of these is a DrugBank artifact" in a
#: comment is the thing E6-1 contrasts a checkable claim against.
_DECLARATION_KEYS = frozenset({"path", "sha256", "derived_from", "why"})


def _declaration_document(root: Path, rel: str) -> dict:
    """Parse one declaration file. ABSENT is legitimate and means "nothing declared here"."""
    target = Path(root) / rel
    if not target.is_file():
        return {}
    size = target.stat().st_size
    if size > _MAX_DECLARATION_BYTES:
        # Bounded like every other reader in this guard. `yaml.safe_load` is safe against arbitrary
        # object construction but not against alias expansion or a huge document, and a declaration
        # file nobody can parse is the gate held permanently un-runnable.
        raise DeclarationDataUnusable(
            f"{rel} is {size} bytes, above the {_MAX_DECLARATION_BYTES}-byte bound for declaration "
            f"data. A declaration file is a short list of claims; this is something else."
        )
    try:
        doc = yaml.safe_load(target.read_text(encoding="utf-8"))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        # ValueError covers UnicodeDecodeError, which read_text raises and which is NOT an OSError.
        # One non-UTF-8 byte in a declaration file produced a traceback out of the CLI — exit 1 and
        # no report — from the one command whose contract is that it must never fail silently.
        raise DeclarationDataUnusable(
            f"{rel} could not be read as YAML ({exc}), so the gate cannot tell what is declared. "
            f"Refusing to report: an unreadable declaration file is not an empty one."
        ) from exc
    if doc is None:
        return {}
    if not isinstance(doc, dict):
        raise DeclarationDataUnusable(f"{rel} must be a mapping, got {type(doc).__name__}.")
    # Quoted in the data because tests/test_scaffold.py forbids a bare numeric value anywhere under
    # configs/ — biological numbers are human-owned, and a scanner cannot tell a schema version from
    # a parameter. Checked here so the field is load-bearing: reading a future schema as if it were
    # this one is how a declaration comes to mean something other than what it says.
    version = doc.get("version")
    # `str(version) != "1"` accepted YAML 1.1 integer spellings — 0x1 and 01 both stringify to
    # something a reader would not call version 1. The data files quote it, so require the string.
    if version != "1":
        raise DeclarationDataUnusable(
            f'{rel}: unsupported declaration schema version {version!r} (this gate reads "1"). '
            f"Refusing to interpret it as the schema it is not."
        )
    return doc


def _declaration_entries(root: Path) -> list[tuple[str, dict, str]]:
    """(declared path, entry, which surface declared it), with the SHAPE checked.

    A structurally broken entry raises rather than being skipped: the gate cannot evaluate what it
    cannot parse, and "could not evaluate" must never arrive at the same answer as "nothing to
    declare". That is exit 3, not exit 2 and certainly not a pass.
    """
    return _entries_from(
        {
            PROJECT_DECLARATION_FILE: _declaration_document(root, PROJECT_DECLARATION_FILE),
            REPO_DECLARATION_FILE: _declaration_document(root, REPO_DECLARATION_FILE),
        }
    )


def _entries_from(docs: dict[str, dict]) -> list[tuple[str, dict, str]]:
    """The shape checks, over documents that have already been parsed."""
    entries: list[tuple[str, dict, str]] = []
    seen: dict[str, str] = {}
    for rel, surface in (
        (PROJECT_DECLARATION_FILE, "project"),
        (REPO_DECLARATION_FILE, "repo-root"),
    ):
        doc = docs[rel]
        declared_list = doc.get("declarations") or []
        if not isinstance(declared_list, list):
            raise DeclarationDataUnusable(
                f"{rel}: `declarations` must be a list, got {type(declared_list).__name__}."
            )
        for raw in declared_list:
            if not isinstance(raw, dict):
                raise DeclarationDataUnusable(f"{rel}: every declaration must be a mapping.")
            unknown = set(raw) - _DECLARATION_KEYS
            if unknown:
                raise DeclarationDataUnusable(
                    f"{rel}: unknown declaration key(s) {sorted(map(repr, unknown))}. A key the "
                    f"gate does not "
                    f"understand may be the one a reader believed was doing the work."
                )
            path = raw.get("path")
            if not isinstance(path, str) or not path:
                raise DeclarationDataUnusable(f"{rel}: every declaration needs a `path`.")
            # TYPE before truthiness. `bool(12345)`, `bool(True)` and `bool({"a": 1})` are all
            # true, so a mistyped field passed the exactly-one-claim check below and then crashed on
            # a string operation — a traceback out of the CLI, which tells an operator nothing about
            # which file or which entry to repair. Same defect as the §7 CLI traceback.
            for field, expected in (("sha256", str), ("derived_from", str), ("why", str)):
                value = raw.get(field)
                if value is not None and not isinstance(value, expected):
                    raise DeclarationDataUnusable(
                        f"{rel}: `{path}` has `{field}` of type {type(value).__name__}; it must be "
                        f"a string. YAML supplies whatever was written, and a mistyped field is a "
                        f"claim nobody can evaluate."
                    )
            digest = raw.get("sha256")
            if digest is not None and not _SHA256_RE.fullmatch(digest):
                raise DeclarationDataUnusable(
                    f"{rel}: `{path}` has a `sha256` that is not 64 lowercase hex characters "
                    f"({digest!r}). A pin that cannot match anything would clear nothing while "
                    f"looking like coverage."
                )
            # PRESENCE, not truthiness: `sha256: null` alongside `derived_from` is two claims,
            # and testing bool() silently resolved it to the second one.
            #
            # BUT PRESENCE ALONE WAS ALSO WRONG, IN THE OTHER DIRECTION (r2.27 §11 QG). `sha256:`
            # with NO value and no `derived_from` is `True == False` -> no raise, and the type loop
            # skips None while the hex check is gated on `is not None`. Adjudication then tested
            # `entry.get("sha256")` — truthiness — fell through to the `derived_from` branch, and
            # did `entry["derived_from"]` on an entry that has no such key: an uncaught KeyError,
            # which is not a RecordContentScanError, so it left BOTH entry points as an exit-1
            # traceback rather than exit 3. The comment above was right about the hazard it named
            # and the check it justified did not cover the null it was named for.
            #
            # A claim is a key that is PRESENT AND NOT NULL. That is one rule, and it is the rule
            # adjudication uses, so the two can no longer disagree.
            claims = [key for key in ("sha256", "derived_from") if raw.get(key) is not None]
            if len(claims) != 1:
                raise DeclarationDataUnusable(
                    f"{rel}: `{path}` must carry exactly one of `sha256` (pin the content) or "
                    f"`derived_from` (name a tracked source). Neither is a bare path declaration, "
                    f"which is what E6-3 forbids; both at once is a claim nobody can adjudicate."
                )
            if not raw.get("why"):
                raise DeclarationDataUnusable(
                    f"{rel}: `{path}` needs a `why`. A declaration is a claim, and an unexplained "
                    f"one is the comment E6-1 contrasts a checkable claim against."
                )
            if path in seen:
                raise DeclarationDataUnusable(
                    f"`{path}` is declared twice ({seen[path]} and {surface}); which claim governs "
                    f"is not something the gate may pick."
                )
            seen[path] = surface
            entries.append((path, raw, surface))
    return entries


def _under_an_ownership_prefix(rel: str) -> bool:
    """Is this path inside a directory that BELONGS to somebody, registry or no registry?

    `path_owner` answers "which RECOGNISED project owns this", returning None both for a path nobody
    owns and for a path under an UNREGISTERED project name. Those are different facts, and
    conflating them let `projects/ghost-lib/payload.bin` be declared at the repo-root surface
    precisely BECAUSE the registry refused to recognise `ghost-lib`: registering the name made the
    declaration illegal, and not registering it made it legal.
    """
    parts = Path(rel).parts
    return bool(parts) and any(
        parts[0] == prefix.rstrip("/") for prefix, _i, _m in _OWNERSHIP_PREFIXES
    )


def declaration_defects(
    paths,
    policy: ContentPolicy,
    surface: DeclarationSurface,
) -> list[tuple[str, str]]:
    """Adjudicate every declaration, at most ONCE per (surface, policy). See _adjudicate_once."""
    read = surface
    return _adjudicate_once(paths, policy, read)


def _declaration_defects_uncached(
    paths,
    policy: ContentPolicy,
    surface: DeclarationSurface,
) -> list[tuple[str, str]]:
    """(declared path, what is wrong with the claim) for every entry that does NOT hold.

    These always fail this gate. Both declaration files are OURS — the project file by ownership,
    the repo-root file because an unowned path belongs to nobody — so a defect in either is ours to
    repair, and there is no other gate for it to fall to (E-03).
    """
    tracked = set(paths)
    # TWO owner sets, answering two different questions (DES-1). Placement asks "may this be
    # declared here?" and is judged against the MARKER-BACKED set, which the registry cannot shrink;
    # failure scoping asks "whose gate does this fail?" and uses the narrowed set elsewhere. Using
    # the narrowed set for BOTH let a delisting legalise declaring another team's artifacts.
    placement_owners = marker_backed_owners(paths)
    read = surface
    root = read.root  # FROM THE SURFACE: one source, so a mismatch is unrepresentable (§12)
    defects: list[tuple[str, str]] = []

    for path, entry, where in read.entries:
        owner = path_owner(path, placement_owners)
        if where == "project" and owner != THIS_PROJECT:
            remedy = (
                "Another team's artifact declared here inherits this module's failure mode and "
                "repair path, in a file they neither own nor can judge."
                if owner
                else "An unowned path is declared at the repo-root surface instead (E-05)."
            )
            defects.append(
                (
                    path,
                    f"declared in this project's file, but {owner or 'nobody'} owns it. {remedy}",
                )
            )
        if where == "repo-root" and _under_an_ownership_prefix(path):
            defects.append(
                (
                    path,
                    (
                        f"declared in the repo-root surface, but `{Path(path).parts[0]}/` is an "
                        f"OWNERSHIP PREFIX — the path belongs to a project whether or not that "
                        f"project is in the registry. The repo-root surface is for paths that "
                        f"belong to nobody; delisting an owner must not turn its subtree into one."
                    ),
                )
            )
        if where == "repo-root" and owner is not None:
            defects.append(
                (
                    path,
                    (
                        f"declared in the repo-root surface, but {owner} owns it. The repo-root "
                        f"surface is for paths NOBODY owns; an owned path is declared by its owner."
                    ),
                )
            )
        if path not in tracked:
            defects.append(
                (
                    path,
                    (
                        "declared but not tracked — the file was deleted or renamed and the entry "
                        "stayed behind. A declaration nobody checks reads as coverage and clears "
                        "nothing."
                    ),
                )
            )
            continue

        if _DISPATCH_DIRECTORY_RE.match(path):
            defects.append(
                (
                    path,
                    (
                        "declared, but dispatch payloads are the DOUBLE-EXEMPT path class E6-4 "
                        "closed: `path_owner` returning None for them is what keeps a non-.md "
                        "payload failing here. A declaration on top would make it fail nowhere."
                    ),
                )
            )

        if policy.content_exempt(path):
            defects.append(
                (
                    path,
                    (
                        "declared AND content-excluded. A path may never be exempted twice by two "
                        "different mechanisms: the content scan already skips it, so a declaration "
                        "on top makes it invisible to both halves of the guard — the "
                        "double-exemption shape E6-4 closed for dispatch payloads."
                    ),
                )
            )

        target = Path(root) / path
        if target.is_file():
            head = _container_magic(target)
            if head:
                defects.append(
                    (
                        path,
                        (
                            f"declared, but it is a readable {head} container. A structured container is "
                            f"ALWAYS read, never declared (E6-2) — checked by magic, not by suffix."
                        ),
                    )
                )
                continue

        if target.is_file() and _is_readable(target):
            defects.append(
                (
                    path,
                    (
                        "declared, but the scan CAN read it. A declaration says a file cannot be read; "
                        "declaring a readable file exempts nothing and hides everything."
                    ),
                )
            )
            continue

        if entry.get("sha256"):
            if not target.is_file():
                defects.append((path, "declared with a sha256 but absent from disk."))
                continue
            # The module's own streaming helper, not read_bytes(): every other reader in this
            # guard is bounded, and a declared file is by construction a binary — a pinned PDF or a
            # rendered video is exactly the large-file case.
            actual = _sha256(target)
            if actual != entry["sha256"]:
                defects.append(
                    (
                        path,
                        (
                            f"STALE declaration: pinned {entry['sha256'][:12]}…, file is {actual[:12]}…. "
                            f"Every declared file is a build output, so a path-keyed declaration would have "
                            f"gone on matching this path forever (E6-3)."
                        ),
                    )
                )
            continue

        if not target.is_file():
            defects.append(
                (
                    path,
                    (
                        "claims a tracked source, but the declared file itself is absent from disk, "
                        "so nothing about it has been looked at. `sha256` refuses this case and the "
                        "two forms must agree."
                    ),
                )
            )
            continue

        # WHAT THIS VERIFIES, exactly: that the named source is tracked, readable, owned by the
        # same project, and not itself declared. It does NOT verify that the declared file derives
        # from it — naming an unrelated same-owner file satisfies the check. The derivation is a
        # human claim, and `why` is where it is made; the gate narrows who may make it and keeps the
        # source in scope, which is less than the prose used to imply.
        source = entry["derived_from"]
        if source in {p for p, _e, _s in read.entries}:
            defects.append(
                (
                    path,
                    (
                        f"claims to be derived from `{source}`, which is ITSELF declared. An "
                        f"exemption may not rest on a file this same report may be calling a "
                        f"broken claim in the same run."
                    ),
                )
            )
            continue
        if path_owner(source, placement_owners) != owner:
            defects.append(
                (
                    path,
                    (
                        f"claims to be derived from `{source}`, which belongs to a different owner "
                        f"({path_owner(source, placement_owners) or 'nobody'} vs "
                        f"{owner or 'nobody'}). Any tracked readable file would otherwise satisfy "
                        f"the claim, which puts it back in review — the position `sha256` exists to "
                        f"escape."
                    ),
                )
            )
            continue
        if source not in tracked:
            defects.append(
                (
                    path,
                    (
                        f"claims to be derived from `{source}`, which is not tracked. The claim is only "
                        f"self-maintaining while the source it names is in scope."
                    ),
                )
            )
            continue
        source_target = Path(root) / source
        if not source_target.is_file() or not _is_readable(source_target):
            defects.append(
                (
                    path,
                    (
                        f"claims to be derived from `{source}`, which the scan cannot read — so the source "
                        f"is not in scope and the claim rests on something nobody has checked either."
                    ),
                )
            )
    return defects


@dataclass(frozen=True)
class DeclarationSurface:
    """Everything the declaration data says, read ONCE and then immutable (r2.25 E-14).

    The cheap complaint was nineteen parses per report and a pinned artifact hashed three times. The
    real one: nothing was snapshotted, so an edit landing mid-report produced A SINGLE REPORT THAT
    DISAGREED WITH ITSELF — rows marked FAILS HERE under an owner whose own footer said it fails
    nobody, with an exit code that depended on interleaving. Reading once makes that impossible
    rather than unlikely.

    `structural_error` is E-13. A declaration file that cannot be parsed is NOT "could not scan at
    all": the scan works, only the exemption data is unreadable. So nothing is declared — the
    fail-closed direction, more files fail and never fewer — the listing is still rendered, and the
    reason travels WITH the surface, to be reported beside the listing instead of replacing it.
    """

    #: The tree this surface was READ FROM (r2.29 §12). Without it, `read(root)` discarded its
    #: argument and eight public functions took `root` and `surface` separately — so a surface read
    #: from tree A could be passed with tree B and would return A's verdicts, silently. Every
    #: verdict in the memo is a snapshot of filesystem reads under a root the key never mentioned.
    #: E-14's thesis is that disagreement must be IMPOSSIBLE, not unlikely, and the frozen object
    #: was missing the one field saying what it was frozen FROM.
    #: NO DEFAULTS, for the reason the rest of the scan path has none (§12). `DeclarationSurface()`
    #: used to be publicly constructible and landed on `registry=None` -> MARKER-BACKED-ONLY, which
    #: is the WIDENING direction: more paths acquire an owner and under E-03 an owned path fails
    #: nobody's gate. A real root plus a real listing plus a defaulted surface reported
    #: MARKER-BACKED ONLY over a repository whose registry exists and narrows. `ScanContext` was
    #: given `__post_init__` precisely because "the only sanctioned constructor has to be enforced
    #: by the TYPE rather than by convention", and that argument was not carried one class over.
    #: I then reintroduced it myself, adding `root: Path = Path()` to satisfy field ordering.
    root: Path
    entries: tuple[tuple[str, dict, str], ...]
    registry: frozenset[str] | None
    structural_error: str | None
    #: Adjudication memo, keyed by policy. The YAML was snapshotted but the VERDICTS were not:
    #: `declaration_defects` ran three times per report and re-read the filesystem each time, so a
    #: pinned artifact was hashed three times and an artifact rebuilt between passes produced a
    #: single report that disagreed with itself — the exact failure E-14 claims to prevent,
    #: surviving inside the fix for E-14. Excluded from equality and repr: it is a cache, not state.
    _verdicts: dict = dataclass_field(default_factory=dict, compare=False, repr=False)

    def __post_init__(self) -> None:
        """The two invariants that are stateable about a surface.

        A structural error means NOTHING could be read, so carrying entries or a registry beside one
        would be a surface claiming to have parsed the file it is reporting it could not parse.
        """
        if self.structural_error and (self.entries or self.registry is not None):
            raise GuardInvariantViolated(
                "a surface carrying a structural error must declare nothing: "
                f"{len(self.entries)} entry(ies) and registry={self.registry!r} were kept beside "
                f"{self.structural_error!r}"
            )

    @classmethod
    def require(cls, root: Path) -> DeclarationSurface:
        """RAISES. For a caller asking one rule a direct question.

        SAME PRECONDITIONS AS `read`, different failure CHANNEL — that is the whole rule, and it is
        stateable, which the previous split was not. `require` used to tolerate an ABSENT file while
        `read` refused one, so the function whose name promised strictness was the lenient one: every
        API caller got absent-as-empty and a marker-only registry, which is the WIDENING direction
        (more paths acquire an owner, and under E-03 an owned path fails nowhere). The clause that
        an absent file is not an empty one was enforced on the report path alone.
        """
        refuse_an_absent_declaration_surface(root)
        docs = {
            rel: _declaration_document(root, rel)
            for rel in (PROJECT_DECLARATION_FILE, REPO_DECLARATION_FILE)
        }
        return cls(
            root=Path(root).resolve(),
            entries=tuple(_entries_from(docs)),
            registry=_registry_from(docs[REPO_DECLARATION_FILE]),
            structural_error=None,
        )

    @classmethod
    def read(cls, root: Path) -> DeclarationSurface:
        """NEVER raises; carries the reason instead, so the listing can still be rendered (E-13).

        Used only by the report. Nothing is declared when the data is broken — the fail-closed
        direction, more files fail and never fewer.
        """
        try:
            return cls.require(root)
        except DeclarationDataUnusable as exc:
            return cls(
                root=Path(root).resolve(), entries=(), registry=None, structural_error=str(exc)
            )


def valid_declarations(
    paths,
    policy: ContentPolicy,
    surface: DeclarationSurface,
) -> frozenset[str]:
    """The declared paths whose claim actually HOLDS. Only these clear a file."""
    read = surface
    broken = {path for path, _ in declaration_defects(paths, policy, read)}
    return frozenset(path for path, _, _ in read.entries if path not in broken)


def _adjudicate_once(paths, policy: ContentPolicy, surface: DeclarationSurface):
    """`declaration_defects`, computed at most once per (surface, policy).

    Every caller inside one report shares the verdict, so the rows, the header count and the defect
    section cannot be drawn from three different readings of the same files.
    """
    # The POLICY OBJECT, not its id(): the surface holds no reference to it, so a collected
    # policy and a new one allocated at the same address would share a memo entry.
    key = (policy, tuple(paths))
    if key not in surface._verdicts:
        surface._verdicts[key] = _declaration_defects_uncached(paths, policy, surface)
    return surface._verdicts[key]


def declared_owner_registry(root: Path) -> frozenset[str] | None:
    """The owner names the repo-root surface declares, or None when no registry exists yet."""
    return _registry_from(_declaration_document(root, REPO_DECLARATION_FILE))


def _registry_from(doc: dict) -> frozenset[str] | None:
    owners = doc.get("owners")
    if owners is None:
        return None
    if not isinstance(owners, list) or not all(isinstance(o, str) and o for o in owners):
        raise DeclarationDataUnusable(
            f"{REPO_DECLARATION_FILE}: `owners` must be a list of project names."
        )
    return frozenset(owners)


def assert_no_container_is_declared(root: Path) -> None:
    """Raise when a DECLARED path is a readable structured container (r2.21 E6-2).

    Checked by MAGIC, not by suffix: a suffix filter is name-based dispatch, the anti-pattern this
    module condemns for parquet 170 lines above, and a container named `blob.dat` walked straight
    through it. Reads the declaration DATA — before r2.24 it read a constant that was permanently
    empty, so it could not have failed.
    """
    containers = []
    for rel, _entry, _surface in _declaration_entries(root):
        target = Path(root) / rel
        if not target.is_file():
            continue
        if _container_magic(target):
            containers.append(rel)
    if containers:
        # NOT `assert`: `python -O` strips assert statements, so the guard would not weaken under
        # optimisation, it would VANISH, and a declared container would be cleared in silence. And
        # AssertionError is a test-shaped exception; this is a production refusal, so it raises the
        # module's own error like every other refusal here.
        raise DeclarationDataUnusable(
            f"declared readable container(s): {containers}. A structured container is ALWAYS read, "
            "never declared (r2.21 E6-2) — only rendered artifacts may be declared."
        )


def _refuse_a_scan_that_cannot_see_itself(root: Path, paths: list[str]) -> None:
    """The listing must be a listing of THIS tree, and a plausible one. Fatal — exit 3.

    Kills together: a root that is some unrelated enclosing repository (a dotfiles `$HOME`, a
    wrapper monorepo), a root whose index was read from elsewhere, and a listing emptied or
    truncated by any means. The suite has asserted exactly this about ITSELF since it was written;
    the command could not, which is why every wrong root read as clean.

    A path that is tracked but ABSENT FROM DISK is deliberately NOT refused here — see
    `unresolvable_tracked`. Making that fatal (as I first shipped it) makes the report unrunnable in
    a legitimate sparse or partial checkout, and a control nobody can run is not a control
    (r2.24 E-10).
    """
    here = Path(__file__).resolve()
    try:
        witness = here.relative_to(root).as_posix()
    except ValueError:
        raise ScanNotPerformed(
            f"{root} does not contain this package ({here}), so it is not the repository this "
            f"report can speak for."
        ) from None
    if witness not in set(paths):
        raise ScanNotPerformed(
            f"the listing for {root} does not contain this module's own file ({witness}), so it "
            f"is not a listing of the tree this package lives in. Refusing to report."
        )
    if len(paths) < _MINIMUM_PLAUSIBLE_TRACKED:
        raise ScanNotPerformed(
            f"only {len(paths)} tracked path(s) under {root}, which is below the floor of "
            f"{_MINIMUM_PLAUSIBLE_TRACKED}: this is a listing that went wrong, not a repository "
            f"with nothing in it. Refusing to report."
        )


def refuse_an_absent_declaration_surface(root: Path) -> None:
    """Both declaration files must EXIST. Parsing and the schema check belong to `require`.

    It used to parse here as well, and the parse moved so the surface is read once (E-14) — but the
    docstring went on promising "parse, and declare a schema this gate reads", which for a DIRECT
    caller had become false in the fail-open direction.

    An absent file used to read as an empty one, which silently reverted the owner registry to the
    pre-r2.24 marker-only mitigation — with the same exit code as a healthy run. This module already
    says "an unreadable declaration file is not an empty one"; an ABSENT one is not either.

    Without this, "the surface exists" is precisely what "declared" was before the surface was
    built: a state the code can describe and cannot verify. `declarations: []` is a claim somebody
    made on purpose and the gate checked; a missing file is a scan that could not be performed.
    """
    for rel in (PROJECT_DECLARATION_FILE, REPO_DECLARATION_FILE):
        if not (Path(root) / rel).is_file():
            raise DeclarationDataUnusable(
                f"the declaration surface {rel} is ABSENT. An empty `declarations: []` is a claim "
                f"made on purpose; a missing file is a scan that could not be performed. Refusing "
                f"to report."
            )
        # Existence only. The PARSE happens once, in DeclarationSurface.require, rather than here
        # and again there — the surface is supposed to be read once (E-14).


def unresolvable_tracked(root: Path, paths) -> list[str]:
    """Tracked paths that are not present on disk, so the scan cannot read them.

    Sparse checkout, `skip-worktree`, or a partial clone that never fetched the blob. THE PAYLOAD IS
    STILL IN THE REPOSITORY — which is the thing the invariant protects — while the worktree simply
    does not have it, so `undecodable_unallowed` walked straight past it with
    `if not target.is_file(): continue` and the report said nothing at all.

    Counted and reported ALWAYS; scoping the count would repeat E-08. The FAILURE is scoped by
    ownership, which is E6-1b exactly (r2.24 E-10).
    """
    return sorted(rel for rel in paths if not (Path(root) / rel).is_file())


def render_undeclared_report(policy: ContentPolicy) -> tuple[str, int]:
    """The report a HUMAN reads, and the exit code this project's gate would produce.

    "Listing that reaches no one is functionally a silent skip" (CTO, §6 boundary) — a report only
    ever asserted on inside tests is the declare-and-skip problem wearing a different coat.

    It takes NO argument. The defect was a caller passing the wrong root, and a `root=None`
    parameter removes the caller's obligation to choose without removing its ability to choose
    wrongly. Narrowed scans are `_render_for_root`, whose underscore says that a narrowed scan is
    not a supported product behaviour.
    """
    # WORKTREE: this is the human-facing listing, which describes the files as they sit on
    # disk and says so in its header. A commit gate goes through `enforce_record_content`
    # with byte_source="staged".
    return _render_for_root(repo_root(), policy, "worktree")


@dataclass(frozen=True)
class ScanContext:
    """Everything a scan needs, REQUIRED everywhere and RESOLVABLE NOWHERE (r2.27 E-17).

    What makes state ambient is not aggregation but IMPLICIT RESOLUTION. Six defects in this
    codebase came from a value that could find itself: a tmp root from `$TMPDIR`, an agent identity
    from the cwd, a quality config from the cwd, a monitor registry from a tracked file, a scan root
    from `project_root()`, and a declaration surface from a `None` default. Every one was a
    correctness-relevant answer derived from something nobody passed.

    So this has no default, no `None`, no module-level instance and no `current()`. A caller must
    build one, which means the dependency is visible in the call graph instead of resolved behind it.
    """

    root: Path
    #: WHERE THE BYTES COME FROM, which is not always the tree being reported on. In `staged` mode
    #: this points at a materialised copy of the index — the bytes a commit would carry — while
    #: `root` stays the repository the report NAMES. They are equal in `worktree` mode.
    read_root: Path
    #: "staged" | "worktree". REQUIRED: which copy the gate certifies is exactly the kind of
    #: decision that must not be resolvable by omission.
    byte_source: str
    paths: tuple[str, ...]
    submodules: tuple[str, ...]
    policy: ContentPolicy
    surface: DeclarationSurface

    def __post_init__(self) -> None:
        """The anti-vacuity refusal runs on EVERY context, not only the ones `build` made.

        It used to live in `build` alone, so `ScanContext(root=real_root, paths=(), ...)` —
        constructible by anyone, through a public non-underscore API — produced exit 0 naming the
        correct root over an empty listing. That is E-08 verbatim ("a scan over the wrong or an
        empty list reports clean"), reachable where before the only door was `_render_for_root`,
        which always checked. "The only sanctioned constructor" has to be enforced by the type
        rather than by convention — the same argument this class makes about `None` defaults.
        """
        _refuse_a_scan_that_cannot_see_itself(self.root, list(self.paths))

    # NOTE ON THE LAYER BELOW: every function this composes takes `surface` as a REQUIRED argument.
    # It was optional with a resolving fallback until r2.27 §11, which made E-17's own sixth defect
    # — "a declaration surface from a `None` default" — survive inside the fix for it, in seven
    # public functions. Worse than untidy: the fallback built the surface with `require` (RAISES)
    # while `build` below uses `read` (carries `structural_error`), so ONE broken declaration file
    # produced exit 2 through the scan and exit 3 through the direct API. E-13's ruling held on one
    # path and was inverted on the other, decided by whether a caller remembered an argument.

    @classmethod
    def for_worktree(cls, root: Path, policy: ContentPolicy) -> ScanContext:
        """The files AS THEY SIT ON DISK. What a human inspecting their own tree wants.

        This is the mode E-10 belongs to: a tracked path can be absent from the worktree, and
        "tracked but NOT PRESENT ON DISK" is a real state here. It is not a state the staged mode
        can produce, and the two are kept apart rather than one inheriting the other's failures.
        """
        return cls._of(root, policy, byte_source="worktree", read_root=root)

    @classmethod
    def for_staged(cls, root: Path, policy: ContentPolicy, staged_root: Path) -> ScanContext:
        """THE BYTES A COMMIT WOULD CARRY, materialised from the index (r2.28).

        `staged_root` comes from `scan_context`, which owns its lifetime — the context is a frozen
        dataclass and must not own a resource.

        Two named constructors rather than one `build(..., byte_source, read_root)`: that form let a
        caller pass `byte_source="staged"` with a worktree read_root and get a scan that LIED about
        which copy it certified. Two fields that can contradict each other is the shape this module
        keeps removing; the name carries the decision instead.
        """
        return cls._of(root, policy, byte_source="staged", read_root=staged_root)

    @classmethod
    def _of(
        cls, root: Path, policy: ContentPolicy, byte_source: str, read_root: Path
    ) -> ScanContext:
        """Read the tree ONCE and freeze it. Reached through the two named constructors."""
        root = Path(root).resolve()
        read_root = Path(read_root).resolve()
        paths, submodules = _tracked_listing(root)
        return cls(
            root=root,
            read_root=read_root,
            byte_source=byte_source,
            paths=tuple(paths),
            submodules=tuple(submodules),
            policy=policy,
            # FROM THE COPY BEING CERTIFIED. The surface carries the root it was read from (§12.1)
            # and every reader takes its root from the surface — so binding it here is what makes
            # the whole declaration path follow the byte source, with no second parameter to keep in
            # sync and no way for the two to disagree.
            surface=DeclarationSurface.read(read_root),
        )


@contextmanager
def scan_context(root: Path, policy: ContentPolicy, byte_source: str):
    """A `ScanContext` for either byte source, owning the temporary tree when there is one.

    The context is a FROZEN DATACLASS and must not own a resource — so the temporary directory's
    lifetime lives here, in a context manager, rather than in the data. In `worktree` mode nothing
    is materialised and this is just a constructor.
    """
    if byte_source == "staged":
        with tempfile.TemporaryDirectory(prefix="chipsim-staged-") as tmp:
            staged = materialise_index(Path(root).resolve(), Path(tmp))
            yield ScanContext.for_staged(root, policy, staged)
        return
    if byte_source != "worktree":
        raise GuardInvariantViolated(
            f"byte_source={byte_source!r} is neither 'staged' nor 'worktree'"
        )
    yield ScanContext.for_worktree(root, policy)


def scan_record_content(context: ScanContext) -> RecordContentScan:
    """Run the gate and return its verdict as data. No formatting, no printing, no exit."""
    root, paths, policy, surface = (
        # `read_root` for anything that touches bytes; `context.root` is what the report NAMES.
        context.read_root,
        list(context.paths),
        context.policy,
        context.surface,
    )

    report = undeclared_report(paths, policy, surface)
    failing = set(failing_undeclared(paths, policy, surface))

    # Tracked but absent from disk. Listed always; failing only where we own it or nobody does —
    # the same predicate failing_undeclared uses, because "unowned fails here" is load-bearing for
    # E6-4 and a missing file is no different in that respect.
    recognised = recognised_owners(paths, surface)
    missing = [(rel, path_owner(rel, recognised)) for rel in unresolvable_tracked(root, paths)]
    failing |= {rel for rel, owner in missing if owner is None or owner == THIS_PROJECT}

    # A declaration whose claim does not hold fails this gate outright: both surfaces are ours, so
    # there is no other gate for a broken claim to fall to (E-03).
    defects = declaration_defects(paths, policy, surface)
    failing |= {path for path, _ in defects}

    def mark(rel: str) -> str:
        return "FAILS HERE" if rel in failing else "listed"

    rows: list[ScanRow] = []
    rows += [ScanRow(rel, owner, "undecodable", mark(rel)) for rel, owner in report]
    rows += [ScanRow(rel, owner, "missing-on-disk", mark(rel)) for rel, owner in missing]
    # The PLACEMENT set, not the narrowed one: that is the set the defect was adjudicated against
    # (r2.25 DES-1), so attributing the row with `recognised` made the row contradict its own
    # `detail` — and under a structural error it made every broken row read `owner=None`.
    placement = marker_backed_owners(paths)
    rows += [
        ScanRow(path, path_owner(path, placement), "broken-declaration", "FAILS HERE", why)
        for path, why in defects
    ]

    entries = surface.entries
    counts = (
        sum(1 for _, _, where in entries if where == "project"),
        sum(1 for _, _, where in entries if where == "repo-root"),
        len({path for path, _ in defects}),
    )
    return RecordContentScan(
        root=context.root,
        byte_source=context.byte_source,
        package=Path(__file__).resolve(),
        tracked_count=len(paths),
        # Derived from the SAME rows the exit code is derived from, so the header number and the
        # verdict cannot drift apart (r2.27 §11 QG).
        failing_count=sum(1 for row in rows if row.disposition == "FAILS HERE"),
        rows=tuple(rows),
        declaration_counts=counts,
        defect_count=len(defects),
        submodules=context.submodules,
        declaration_files=(PROJECT_DECLARATION_FILE, REPO_DECLARATION_FILE),
        registry_state=(
            "unreadable"
            if surface.structural_error
            else ("declared" if surface.registry is not None else "marker-backed-only")
        ),
        structural_error=surface.structural_error,
        exit_code=2 if failing or surface.structural_error else 0,
    )


def _render_for_root(root: Path, policy: ContentPolicy, byte_source: str) -> tuple[str, int]:
    """Kept as the one-call form the CLI and the composition root use."""
    with scan_context(root, policy, byte_source) as context:
        return render_scan(scan_record_content(context))


def undeclared_report(
    paths,
    policy: ContentPolicy,
    surface: DeclarationSurface,
) -> list[tuple[str, str | None]]:
    """(path, owning project) for every undeclared undecodable file, repo-wide (r2.22, E6-1b).

    The LISTING is never scoped — "listing is what may never be skipped; failing is what is
    scoped" — so another team's artifacts stay visible and countable here even though they do not
    fail this gate.
    """
    # The registry is built from the SAME listing the report is rendered from, so an owner cannot
    # be recognised on the strength of a file that this scan never saw.
    read = surface
    recognised = recognised_owners(paths, read)
    return sorted(
        (rel, path_owner(rel, recognised)) for rel in undecodable_unallowed(paths, policy, read)
    )


def failing_undeclared(
    paths,
    policy: ContentPolicy,
    surface: DeclarationSurface,
) -> list[str]:
    """The subset of the report that fails THIS project's gate: files this project owns, plus
    every file no project owns.

    Measured before this scoping existed: of 24 declared paths, 0 belonged to this project, and
    removing them as E6-1 required made this module's live test fail on 24 files owned by two
    other teams — inverting the coupling instead of removing it.
    """
    return [
        rel
        for rel, owner in undeclared_report(paths, policy, surface)
        if owner is None or owner == THIS_PROJECT
    ]


def undecodable_unallowed(
    paths,
    policy: ContentPolicy,
    surface: DeclarationSurface,
) -> list[str]:
    """Tracked paths the scan cannot read AND whose declaration does not hold (r2.24 E-02).

    A skipped file is an UNCHECKED file: "no hits" from a file the scan never read is the
    false-clean this project keeps rediscovering. Reporting them is what makes the scan's silence
    mean something.

    Dispatch payloads are skipped — they are waived by ruling (#122 §3) and never scanned either
    way, so reporting them would be unactionable noise. The LEDGER pair is NOT skipped: its content
    IS still read (`ledger_tuple_hits`), so its readability is exactly what this check is for. The
    exclusions exist for accession CONTENT, not for readability.
    """
    declared = valid_declarations(paths, policy, surface)
    root = surface.root  # FROM THE SURFACE (§12), never a separately-passed argument
    unreadable: list[str] = []
    for rel in paths:
        if policy.readability_waived(root, rel):
            continue
        if rel in declared:
            continue
        target = Path(root) / rel
        if not target.is_file():
            # Not silent any more: unresolvable_tracked() counts these and the report gives them
            # their own section. Skipping HERE is right — there is nothing to read — but the skip
            # was the whole defect for as long as nothing said it had happened (r2.24 E-10).
            continue
        if not _is_readable(target):
            unreadable.append(rel)
    return sorted(unreadable)
