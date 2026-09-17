"""The report, and the data it is a view of — a module that CANNOT read anything.

"The renderer decides nothing" was, until this split, a property a reviewer had to verify by reading
the code, and it had already been broken twice while the words stayed true: the exit code was
recomputed here for a while, and the header's failing-count was still being re-derived from a
narrower partition than the exit code as late as r2.27 §11.

Here it is mechanically checkable. This module imports `errors` — a leaf — and the standard library,
and NOTHING else: no `subprocess`, no `yaml`, no `open`, no `os`. A test asserts that import list. A
renderer that cannot reach a file cannot decide anything about one; it can only describe the scan it
was handed.

The data types live here WITH the renderer rather than beside the scanning logic, because they are
what the renderer is a view OF, and putting them here is what lets the dependency point one way:
`record_content` imports this module, and this module imports nothing from `record_content`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from chipsim.guards.errors import GuardInvariantViolated


def render_path(rel: str) -> str:
    """A tracked path as it may safely be PRINTED.

    `git ls-files -z` emits names unquoted, and newline and ESC are legal in paths. A reviewer
    forged a complete clean report out of one filename: a leading `ESC[2J ESC[H` cleared the
    terminal and the rest of the name drew a fake header and a fake all-clear, with three
    payload-bearing files still listed underneath where no human would ever see them. A newline
    alone splits one real entry into two innocuous-looking rows.

    With no CI consumer of the exit code, THE PRINTED LISTING IS THE CONTROL, so it must not be
    writable by whoever can add a file.
    """
    if rel.isprintable():
        return rel
    return rel.encode("unicode_escape").decode("ascii") + "  [name contains control characters]"


@dataclass(frozen=True)
class ScanRow:
    """One file, and what this gate has decided about it.

    `disposition` is the answer a reader came for, and it is a FIELD rather than a mark embedded in a
    formatted line — so "what fails" can be asked of the data instead of reassembled by grepping four
    sections of prose.
    """

    path: str
    owner: str | None
    #: "undecodable" | "missing-on-disk" | "broken-declaration"
    category: str
    #: "FAILS HERE" | "listed"
    disposition: str
    #: Only for a broken declaration: why the claim does not hold.
    detail: str | None = None

    def __post_init__(self) -> None:
        """EVERY interpolated field is escaped, not just the path (r2.28).

        r2.24 escaped `path` after a reviewer forged a complete clean report out of one filename.
        `detail` and `owner` were left raw — and `detail` is built from `derived_from`, an arbitrary
        string out of a tracked YAML file, while `owner` is a directory name out of the tracked
        listing. A STRUCTURALLY VALID declaration file therefore rendered a forged clean-report line
        at column 0: the same attack, one column over, reachable without even a broken file.

        Escaping happens HERE rather than in the renderer so that no future section can reintroduce
        it by forgetting — the renderer's own call sites are now belt-and-braces, and `render_path`
        is idempotent because its output is printable by construction.

        `disposition` is validated because it is one bit spelled as two strings, and the invariant on
        `RecordContentScan` counts rows by matching it: a typo would silently stop a row counting as
        failing.
        """
        if self.disposition not in {"FAILS HERE", "listed"}:
            raise GuardInvariantViolated(
                f"{self.path}: disposition {self.disposition!r} is neither 'FAILS HERE' nor "
                f"'listed'. The scan's failing-count matches on this string."
            )
        object.__setattr__(self, "path", render_path(self.path))
        if self.owner is not None:
            object.__setattr__(self, "owner", render_path(self.owner))
        if self.detail is not None:
            # A multi-line detail collapses to one escaped line rather than becoming free-standing
            # report rows, which is exactly what the structural-error path had to be taught.
            object.__setattr__(self, "detail", render_path(self.detail))


@dataclass(frozen=True)
class RecordContentScan:
    """The verdict as DATA. Rendering derives from this and decides nothing.

    `exit_code` lives HERE, not inside a string. Its living only in the renderer is *why* E-13b
    happened: no test could reach it cheaply, so twelve mutants survived while every defect test
    asserted on a validator's return value instead.
    """

    root: Path
    package: Path
    tracked_count: int
    #: How many rows FAIL THIS GATE — derived once, beside `exit_code`, for the same reason
    #: `exit_code` lives here: a number the renderer recomputes is a number that can disagree
    #: with the verdict it sits next to (r2.27 §11 QG).
    failing_count: int
    rows: tuple[ScanRow, ...]
    declaration_counts: tuple[int, int, int]  # (project, repo-root, distinct defective)
    defect_count: int
    submodules: tuple[str, ...]
    #: "declared" | "marker-backed-only" | "unreadable". A bool flattened the third into the
    #: second, so a repository whose registry could not be PARSED printed "no `owners` list in
    #: <file>" — false, the file has one — beside a claim that the marker mitigation was in force,
    #: when in fact every owner had been narrowed away.
    #: WHICH COPY the bytes came from: "staged" (what a commit would carry) or "worktree" (what
    #: is on disk). Carried as data because a reader cannot check a verdict without knowing what was
    #: verified — E6-5 applied to which BYTES rather than which HALF.
    byte_source: str
    registry_state: str
    #: The two declaration files this scan READ, in (project, repo-root) order. Carried as data for
    #: the same reason `exit_code` is: the renderer named them by reaching for module constants
    #: derived from `source_root()` — resolution from the IMPORT LOCATION — so a report module could
    #: never be free of the filesystem while it had to look them up. A report describes what the
    #: scan read; it should not re-derive where the scan looked.
    declaration_files: tuple[str, str]
    structural_error: str | None
    exit_code: int

    def __post_init__(self) -> None:
        """The contract `render_scan` relies on, checked from the DATA side.

        `render_scan` returns `exit_code` verbatim and recomputes nothing — which is right, and
        which means nothing anywhere noticed if the two disagreed. A hand-built scan with a
        FAILS HERE row and `exit_code=0` rendered that row and returned 0.
        """
        should_fail = bool(self.structural_error) or any(
            row.disposition == "FAILS HERE" for row in self.rows
        )
        # MEMBERSHIP, not truthiness (r2.27 §11 QG). `bool(exit_code) != should_fail` accepted
        # exit_code=1 beside a failing row: constructed, rendered, and returned verbatim by
        # `render_scan`. 1 is outside the three states this system declares (clean 0 / files-fail 2
        # / could-not-scan 3), so the contract was escapable from the DATA side and not only
        # through the uncaught-exception path. An invariant that checks one BIT of a value is not
        # checking the value.
        if self.exit_code not in {0, 2}:
            raise GuardInvariantViolated(
                f"scan carries exit_code={self.exit_code}, which is not one of the two codes a "
                f"SCAN can produce (0 clean, 2 files-fail). Exit 3 belongs to the composition "
                f"root, which raises rather than building a scan."
            )
        if self.byte_source not in {"staged", "worktree"}:
            raise GuardInvariantViolated(
                f"scan carries byte_source={self.byte_source!r}; a scan reads either the staged "
                f"blobs or the working tree, and which one is not resolvable by omission."
            )
        counted = sum(1 for row in self.rows if row.disposition == "FAILS HERE")
        if self.failing_count != counted:
            raise GuardInvariantViolated(
                f"scan is internally inconsistent: failing_count={self.failing_count} with "
                f"{counted} row(s) marked FAILS HERE. The header prints this number beside the "
                f"word FAILING; it must be the rows."
            )
        if bool(self.exit_code) != should_fail:
            raise GuardInvariantViolated(
                f"scan is internally inconsistent: exit_code={self.exit_code} with "
                f"{sum(1 for r in self.rows if r.disposition == 'FAILS HERE')} failing row(s) and "
                f"structural_error={self.structural_error!r}"
            )


def render_scan(scan: RecordContentScan) -> tuple[str, int]:
    """PRESENTATION. It may reorder, group or drop; it may not decide.

    The exit code it returns is the one the scan computed — it is not recomputed here, because a
    verdict that exists in two places is a verdict that can disagree with itself.
    """
    undecodable = [r for r in scan.rows if r.category == "undecodable"]
    missing = [r for r in scan.rows if r.category == "missing-on-disk"]
    broken = [r for r in scan.rows if r.category == "broken-declaration"]
    # NOT recomputed here (r2.27 §11 QG). The renderer used to derive this from `undecodable +
    # missing`, which EXCLUDES every broken-declaration row — and those are FAILS HERE by
    # construction. A scan with one broken declaration therefore headed with
    # "(failing this gate: 0)" and returned exit 2: the number standing beside the word FAILING
    # was not the number of failing rows, and the divergence was silent. The rule "the renderer
    # decides nothing" held for the exit code and broke one field to its left.
    project_count, repo_count, defective = scan.declaration_counts
    project_declaration_file, repo_declaration_file = scan.declaration_files

    lines = [
        (
            f"undeclared undecodable files: {len(undecodable)} "
            f"(failing this gate: {scan.failing_count}"
            f"{'; DECLARATION DATA UNREADABLE, so nothing is declared' if scan.structural_error else ''}) "
            f"— scanned {scan.tracked_count} tracked files under {render_path(str(scan.root))} "
            f"[{'STAGED bytes (what a commit would carry)' if scan.byte_source == 'staged' else 'WORKTREE bytes (the files as they sit on disk)'}], "
            f"{len(missing)} not present on disk"
        ),
        (
            # A count of ZERO and a count that COULD NOT BE TAKEN must not print the same glyph.
            # E-20 put the structural error on line one and left this line reading "0 whose claim
            # does not hold" at the moment no claim could be evaluated at all.
            "  declarations read: UNREADABLE — the declaration data could not be parsed, so "
            "nothing is declared"
            if scan.structural_error
            else (
                f"  declarations read: {project_count + repo_count} "
                f"({project_count} from {project_declaration_file}, "
                f"{repo_count} from {repo_declaration_file}), "
                f"{defective} whose claim does not hold ({scan.defect_count} defect(s))"
            )
        ),
        f"  (scan run from package {render_path(str(scan.package))})",
    ]
    if scan.structural_error:
        lines.append(
            "  DECLARATION DATA COULD NOT BE READ, so NOTHING IS DECLARED — every undecodable file "
            "is reported below as if it had never been declared, which is the fail-closed "
            "direction: more files fail, never fewer. This is exit 2, not exit 3: the scan worked, "
            "only the exemption data is unreadable."
        )
        # Indented line by line: the message is multi-line PyYAML output whose continuation
        # lines land at column 0, so attacker-chosen printable text from a tracked file appeared as
        # free-standing report lines. Every path goes through `render_path` for this reason; this
        # string was the one interpolation that did not.
        for line in str(scan.structural_error).splitlines():
            lines.append(f"    {render_path(line)}")
    for row in undecodable:
        lines.append(
            f"  {render_path(row.path)}  owner={row.owner or '<unowned>'}  [{row.disposition}]"
        )
    if not undecodable:
        lines.append("  (none)")
    if broken:
        lines.append("  DECLARATIONS WHOSE CLAIM DOES NOT HOLD — these clear nothing:")
        for row in broken:
            lines.append(f"    {render_path(row.path)}  [{row.disposition}]  {row.detail}")
    if missing:
        lines.append(
            "  tracked but NOT PRESENT ON DISK, so the scan could not read them (sparse or partial "
            "checkout). The payload is still in the repository:"
        )
        for row in missing:
            lines.append(
                f"    {render_path(row.path)}  owner={row.owner or '<unowned>'}  [{row.disposition}]"
            )
    known = {"undecodable", "missing-on-disk", "broken-declaration"}
    unknown = [r for r in scan.rows if r.category not in known]
    if unknown:
        # A listing that reaches no one is functionally a silent skip — this module's own standard.
        # Partitioning by three literal strings with no catch-all dropped any future category from
        # every section of the text while it still counted toward the exit code.
        lines.append("  ROWS IN AN UNRECOGNISED CATEGORY — the renderer does not know how to group")
        lines.append("  these, and a row that reaches no reader is a silent skip:")
        for row in unknown:
            lines.append(
                f"    {render_path(row.path)}  category={row.category!r}  [{row.disposition}]"
            )
    if scan.submodules:
        lines.append(
            f"  {len(scan.submodules)} submodule(s) NOT scanned (another repository, not files "
            f"here): {', '.join(render_path(rel) for rel in scan.submodules)}"
        )
    if scan.registry_state == "declared":
        lines.append(
            f"  owner registry: DECLARED in {repo_declaration_file}, intersected with the tracked "
            "marker — an owner needs both, so neither a declaration nor a file alone mints one."
        )
    elif scan.registry_state == "unreadable":
        lines.append(
            # DOES NOT NAME A FILE (r2.28 §11 QG). It used to assert `REPO_DECLARATION_FILE`, but
            # `registry_state` is derived from `surface.structural_error`, which is set by EITHER
            # declaration file failing to parse. With only the PROJECT file broken, the report
            # named the repo-root file here while the structural-error section named the project
            # file correctly — so one report gave two answers and the operator was sent to repair
            # a file that was fine. The section above names the file; this line states the
            # CONSEQUENCE, which is what it is for.
            "  owner registry: UNREADABLE — the declaration data could not be parsed (the file is "
            "named above), so EVERY owner was narrowed away and every path is unowned. This is "
            "not the marker-backed mitigation; it is the absence of any registry at all."
        )
    else:
        lines.append(
            f"  owner registry: MARKER-BACKED ONLY — no `owners` list in {repo_declaration_file}. "
            "A tracked marker is louder than `mkdir` but is addable by anyone who adds a "
            "pyproject.toml, so this is a MITIGATION, not proof (E-11)."
        )
    lines.append(
        "  exit 2 when a file owned by this project, or owned by none, is undeclared. Files listed "
        "against another project fail NO gate today: no other project implements this check, so "
        "`owner=` names who should care, not who is enforcing (E-03)."
    )
    return "\n".join(lines), scan.exit_code
