"""Reviewer-isolation BRACKET, captured to a file BEFORE reviewers start.

WHY IT EXISTS. Gate 4's verdict had exactly one gap: I could state that no reviewer mutated
tracked content, because I re-checked each reviewer worktree directly, but I could NOT re-derive
the numeric digest captured before the review -- my context was compacted mid-gate and the
bracket command did not survive it. A bracket that lives only in a transcript is not a bracket.

WHAT IT CAPTURES, in one file, so a re-run after the review can be diffed against it:
  * the exact command line that produced it (so the "after" half is reproducible, not remembered)
  * the gated file list and a per-file digest, plus one content digest over all of them
  * metadata COUNTS AND CONTENTS: worktrees, branches, stash entries, tags

WHAT IT DOES NOT DO. It never writes into the repository it measures and never mutates anything.
It is read-only by construction; the only file it writes is the evidence file you name.

RULE 3b. A bracket nobody has seen fail is not evidence. `--self-test` builds a throwaway git
repo, captures, mutates one tracked byte, re-captures, and asserts the two disagree -- then
restores and asserts they agree again. Run it before trusting a silent bracket.

ONE COPY, SHARED (r2.49 (g)). Gates 6 and 7 each carried their own `gate<N>-bracket.py`, and by the
end the two files were BYTE-IDENTICAL -- so no differential between them could ever have reported the
duplication, and neither copy had any check beyond a `--self-test` a human remembered to run. This is
now the single implementation; copy it again and `tests/test_bracket.py` fails. That test also runs
`--self-test`, which moves rule 3b out of memory and into the suite.

Each gate's evidence record still publishes the command it really ran, naming its own deleted copy.
That is deliberate: a record states what happened. Each one therefore carries a canonical
`PINNED-BYTES: sha256 <64hex> at <rev>:<path>` line, and the test resolves the pin, re-hashes the
blob, and cross-checks the hash against that gate's own `*-bracket-before.json`. Reproducibility of a
past gate does NOT depend on this file's current bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


class BracketUnusable(RuntimeError):
    """The bracket could not be taken. NEVER reported as "held".

    Found by gate 6's design review, and it was the instrument's own version of the defect this
    whole workstream keeps catching: `_git` used to RETURN an error string instead of raising, so a
    run in a directory that is not a git repository produced a one-element file list holding that
    string, a digest over it, and the words "bracket HELD" at exit 0. A bracket whose silence can
    mean "I could not look" is not evidence of anything. The six original self-tests all ran inside
    a working repo, so none of them could see it.
    """


def _git(root: Path, *args: str) -> str:
    out = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=False
    )
    if out.returncode != 0:
        raise BracketUnusable(
            f"git {' '.join(args)} failed rc={out.returncode} in {root}: {out.stderr.strip()}"
        )
    return out.stdout


#: The shape scan lives with the project it measures; the bracket is a workstream tool. Resolved by
#: path rather than by package, because there is no import route between the two trees.
_PROJECT_ROOT = Path(__file__).resolve().parents[4] / "projects/lung-on-chipsim"


#: The reason the shape-scan tool last failed to load, or None. Kept so a could-not-scan verdict
#: can SAY WHY rather than leaving a reader to re-run the import by hand.
_LOAD_FAILURE: str | None = None


def _load_shape_scan():
    """Return the shape-scan module, or None if it cannot be loaded.

    None is NOT an error here -- it becomes could-not-scan for every gated file, which fails the
    gate (ruling #455 item 2). A bracket that quietly skipped the scan because an import failed
    would certify content it never looked at, which is the exact failure this instrument exists to
    prevent and the one its `BracketUnusable` class was added for.
    """
    global _LOAD_FAILURE
    try:
        if str(_PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(_PROJECT_ROOT))
        from tests import shape_scan

        _LOAD_FAILURE = None
        return shape_scan
    except Exception as exc:  # noqa: BLE001 — any failure to load is could-not-scan, never a skip
        # r2.50a: the CAUSE is kept, not discarded (gate 8, MEDIUM). A bare `except Exception` that
        # threw the reason away turned every distinct failure -- a missing dependency, a syntax
        # error, a renamed module -- into the same silent None, so the one thing a reader needed in
        # order to act was the one thing the instrument dropped. The type and message are recorded;
        # no value from the tree is echoed.
        _LOAD_FAILURE = f"{type(exc).__name__}: {exc}"
        return None


def shape_scan_gated(root: Path, names: list[str]) -> dict:
    """Run the identifier-SHAPE scan over the gated files. Counts and lines only, never a value.

    r2.49 (e) requirement 3. TWO HALVES, and only one of them is live:

      * could-not-scan FAILS. A file the scan could not read, decode, or reach -- or a scan tool
        that could not be loaded at all -- is reported with its reason and fails the gate.
      * unaccounted shapes are COUNTED AND REPORTED, and do NOT yet fail. Measured on this tree:
        1,028 unaccounted shapes across 44 files, of which 892 (87%) sit in files governed by
        something other than clause (i) -- signed plan bytes, the signature ledger, human-only
        fixtures, generated reports, citation-governed configs. Making them fatal BEFORE the
        scope-by-property rules are signed (r2.50b, CTO ruling #455 item 1) would produce a gate
        that fails on every run, and a gate that always fails is a gate someone turns off. The
        verdict half lands with the re-sign, together with marker subtraction.

    Reporting them now is deliberate: the counts are visible every run, so the 892 are never hidden,
    which is the sum identity #455 asks the claim to become.
    """
    module = _load_shape_scan()
    per_file: dict[str, dict] = {}
    unreadable: dict[str, str] = {}
    absent: list[str] = []
    scanned_empty: list[str] = []

    for rel in sorted(names):
        path = root / rel
        # ABSENT IS NOT COULD-NOT-SCAN. A path the gated change DELETED holds no shapes, and there
        # is nothing there to fail to read. Found by running this instrument for real against the
        # very change that added it: r2.49 (g) deletes `gate7-bracket.py`, that path is in the diff
        # set, and the first version called it `unreadable: FileNotFoundError` and exited 3. Every
        # change that removes a file would have failed the gate, and a gate that cries wolf is the
        # failure this file's own docstring warns about.
        #
        # `is_symlink()` first, deliberately: a DANGLING symlink is an entry that exists and cannot
        # be read through, which is genuinely could-not-scan. `exists()` alone follows the link and
        # would call it absent, hiding it -- the same confusion the ledger reader hit in r2.49 (d1).
        if not (path.is_symlink() or path.exists()):
            absent.append(rel)
            continue
        if module is None:
            unreadable[rel] = "the shape-scan tool could not be loaded"
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            unreadable[rel] = f"unreadable: {type(exc).__name__}"
            continue
        # SCANNED-AND-EMPTY IS NOT COULD-NOT-SCAN (r2.50b, gate-8 C-2; found by the security and
        # code reviewers and by my own pass). The SCANNER takes a string and cannot tell "" that
        # came from a successful read of a zero-byte file from "" that came from a failed one, so
        # it rightly refuses to certify either: clause (e) binds it to could-not-scan. THIS caller
        # opened the file and therefore knows. A tracked path that exists and reads as zero bytes
        # was looked at, holds no shapes, and is clean -- six `.gitkeep` files are tracked, so
        # treating them as could-not-scan failed the gate at exit 3 on every run, and a gate that
        # always fails is a gate someone turns off. A file that could NOT be read stays fatal:
        # that is the distinction, and losing it is exactly the "nothing to find" vs "could not
        # look" confusion this instrument exists to prevent.
        if not text:
            scanned_empty.append(rel)
            continue
        acc = module.scan_accession_shapes(text)
        sha = module.scan_structure_shapes(text)
        reasons = [r for r in (acc.could_not_scan, sha.could_not_scan) if r]
        if reasons:
            unreadable[rel] = reasons[0]
            continue
        if acc.unaccounted or sha.unaccounted:
            per_file[rel] = {
                "accession_unaccounted": acc.unaccounted,
                "accession_lines": list(acc.lines),
                "structure_unaccounted": sha.unaccounted,
                "structure_lines": list(sha.lines),
            }

    total = sum(f["accession_unaccounted"] + f["structure_unaccounted"] for f in per_file.values())
    return {
        "tool_loaded": module is not None,
        "files_scanned": len(names) - len(unreadable) - len(absent),
        "files_with_unaccounted": len(per_file),
        "unaccounted_shapes": total,
        "per_file": per_file,
        "could_not_scan": unreadable,
        # Reported, never dropped: silently ignoring an absent path is how a deletion passes a
        # bracket unnoticed, which is the opposite failure to the cry-wolf one above.
        "absent_from_worktree": sorted(absent),
        # Reported so a reader can see the gate looked and found nothing, rather than inferring it
        # from an absence of complaint.
        "scanned_and_empty": sorted(scanned_empty),
        "verdict_half_live": "could-not-scan only; unaccounted pending r2.50b marker subtraction",
    }


def _strip_stash_index(line: str) -> str:
    """Drop the `stash@{n}: ` label so a renumbering is not reported as a difference."""
    head, sep, rest = line.partition(": ")
    return rest if sep and head.startswith("stash@{") else line


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "surrogateescape")).hexdigest()


def _digest_lines(lines: list[str]) -> list[str]:
    """Per-entry digests instead of verbatim text (r2.50a mechanism 5, gate-8 H-3).

    This file writes a TRACKED evidence record. It used to copy `git worktree list`, `git branch`,
    `git stash list` and `git status --porcelain` in VERBATIM: absolute host paths, untracked
    filenames, and commit subjects belonging to OTHER WORKSTREAMS. Verified: gate 7's committed
    artifact carries a perturb-seq-eval stash subject. Gate 8's was clean BY LUCK, not by a
    control -- the instrument that enforces the record-content constraint was an unguarded write
    path into the surface it protects.

    Digesting PER ENTRY rather than over the whole list is deliberate: `differences()` compares
    these as SETS, so reviewer-isolation addendum 3d still gets what it needs -- WHICH entries
    appeared or vanished -- while the text itself never reaches the file. Identity is preserved;
    content is not carried.

    Every entry is digested, not just the ones judged "foreign". Deciding which entries belong to
    this workstream would be an exclusion predicate, and a wrong one silently drops an entry from
    the record -- the false-exclusion failure this revision exists to stop. A uniform rule has no
    such classifier to get wrong.
    """
    return sorted(_digest(line) for line in lines)


def _assert_output_carries_no_shapes(payload: dict) -> None:
    """Run the PRODUCTION detectors over what we are about to write. A hit is could-not-write.

    #463 item (5): the instrument runs the detectors over its own output BEFORE writing, and a hit
    fails the gate. Refusing to write is the honest outcome -- the alternative is an evidence file
    that breaches the very constraint the evidence exists to demonstrate.
    """
    module = _load_shape_scan()
    if module is None:
        raise BracketUnusable(
            "the shape-scan tool could not be loaded, so this record cannot be checked against the "
            "content constraint before being written. Refusing to write an unchecked record. "
            f"Cause: {_LOAD_FAILURE}. (The detectors import the production module, so this tool "
            "must run under the project environment -- e.g. the project's own interpreter.)"
        )
    blob = json.dumps(payload, sort_keys=True)
    acc = module.scan_accession_shapes(blob)
    sha = module.scan_structure_shapes(blob)
    hits = acc.unaccounted + sha.unaccounted
    if hits:
        raise BracketUnusable(
            f"COULD NOT WRITE: this bracket record carries {hits} unaccounted shaped value(s) of "
            "its own. The instrument that enforces the record-content constraint must not breach "
            "it. No value is echoed here, by design -- re-run with the capture inspected locally."
        )


def capture(root: Path, base: str, head: str = "HEAD", names: list[str] | None = None) -> dict:
    """Read-only. Returns the bracket as plain data, so two captures can be compared as dicts.

    `names` PINS the file set. The after-half passes the before-half's list rather than recomputing
    the diff, because a file committed between the two halves -- the evidence record itself, for
    one -- would otherwise show up as a change no reviewer made. A bracket that cries wolf is
    worse than no bracket: it teaches you to ignore it.
    """
    if names is None:
        names = [n for n in _git(root, "diff", "--name-only", base, head).splitlines() if n]

    per_file = {}
    for rel in sorted(names):
        path = root / rel
        try:
            per_file[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as exc:
            # A listed path that is absent from the worktree is a FACT about the tree, recorded
            # rather than skipped: skipping it would let a deletion pass the bracket unnoticed.
            per_file[rel] = f"<unreadable: {type(exc).__name__}>"

    if not names:
        raise BracketUnusable(
            f"the gated file set is EMPTY for {base}..{head} in {root}. A digest over nothing "
            "compares equal to a digest over nothing, so this would report 'held' while measuring "
            "no content at all."
        )

    content_digest = _digest(json.dumps(per_file, sort_keys=True))

    # r2.50a mechanism (5): digests and counts, never verbatim foreign text. See _digest_lines.
    metadata = {
        "worktrees": _digest_lines(_git(root, "worktree", "list").splitlines()),
        "branches": _digest_lines(_git(root, "branch", "--list").splitlines()),
        # KEYED BY CONTENT, NOT BY INDEX. The stash list labels each entry `stash@{n}`, and the
        # stack is SHARED with every other worktree in this repo: one push by another agent
        # renumbers everything below it, and an index-keyed comparison then reports the WHOLE
        # stack as gone and new. Measured on gate 6's own after-half: 26 lines of delta for one
        # entry actually added. Addendum 3d wants a stash delta INVESTIGATED rather than ignored,
        # which is only possible if the delta names the entries that really moved.
        "stash": _digest_lines(
            [_strip_stash_index(x) for x in _git(root, "stash", "list").splitlines()]
        ),
        "tags": _digest_lines(_git(root, "tag").splitlines()),
        "status": _digest_lines(_git(root, "status", "--porcelain").splitlines()),
    }

    payload = {
        # The absolute root is a HOST PATH and does not belong in a tracked record; the invocation
        # is reproducible from the base/head pair plus the repo it is committed in.
        "command": f"bracket.py --root <repo-root> --base {base} --head {head}",
        "base": base,
        "head_sha": _git(root, "rev-parse", head).strip(),
        "gated_files": sorted(names),
        "per_file": per_file,
        "content_digest": content_digest,
        "metadata": metadata,
        "metadata_counts": {k: len(v) for k, v in metadata.items()},
        "metadata_digest": _digest(json.dumps(metadata, sort_keys=True)),
    }
    _assert_output_carries_no_shapes(payload)
    return payload


def differences(before: dict, after: dict) -> tuple[list[str], list[str]]:
    """(content differences, metadata differences) — SEPARATED, because they mean different things.

    THE VERDICT IS THE CONTENT HALF (#410 ruling 4). A content difference means a reviewer mutated
    the tree that was hashed, which voids the gate. A metadata difference usually means a reviewer
    EXISTED: worktree agents create their own worktree and branch, and other sessions push and pop
    the shared stash stack throughout. Gate 6's own run reported "BRACKET BROKEN" and exited 1 for
    two reviewer branches and two reviewer worktrees while the content digest was IDENTICAL — the
    tool's own docstring warns that a bracket which cries wolf teaches you to ignore it, and its
    metadata half was doing exactly that.

    The metadata half is not dropped: it is the only place an unexplained worktree or a vanished
    branch surfaces at all, and reviewer-isolation addendum 3d requires such an entry to be
    investigated and reported rather than removed. It is REPORTED, and it does not decide the exit
    code.
    """
    content: list[str] = []
    if before["content_digest"] != after["content_digest"]:
        content.append("content digest CHANGED")
        for rel in sorted(set(before["per_file"]) | set(after["per_file"])):
            b, a = before["per_file"].get(rel), after["per_file"].get(rel)
            if b != a:
                content.append(f"  file changed: {rel}")
    metadata: list[str] = []
    if before["metadata_digest"] != after["metadata_digest"]:
        metadata.append("metadata CHANGED")
        for key in sorted(set(before["metadata"]) | set(after["metadata"])):
            b = set(before["metadata"].get(key, []))
            a = set(after["metadata"].get(key, []))
            for gone in sorted(b - a):
                metadata.append(f"  {key} GONE: {gone}")
            for new in sorted(a - b):
                metadata.append(f"  {key} NEW: {new}")
    return content, metadata


def _self_test() -> int:
    """Rule 3b: prove the bracket can fail, in BOTH directions, before trusting its silence."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for args in (
            ("init", "-q", "-b", "main"),
            ("config", "user.email", "t@t"),
            ("config", "user.name", "t"),
        ):
            _git(root, *args)
        (root / "a.txt").write_text("one\n")
        _git(root, "add", "a.txt")
        _git(root, "commit", "-qm", "base")
        base = _git(root, "rev-parse", "HEAD").strip()
        (root / "b.txt").write_text("two\n")
        _git(root, "add", "b.txt")
        _git(root, "commit", "-qm", "work")

        before = capture(root, base)
        if before["gated_files"] != ["b.txt"]:
            print(f"FAIL: expected the gated set to be ['b.txt'], got {before['gated_files']}")
            return 1

        ok = True

        # Direction 1: a tracked byte changes -> the bracket must say so, and name the file.
        (root / "b.txt").write_text("two-MUTATED\n")
        diff, _ = differences(before, capture(root, base))
        if not any("content digest CHANGED" in d for d in diff) or not any(
            "b.txt" in d for d in diff
        ):
            print(f"FAIL: a mutated tracked file did not break the bracket. diff={diff}")
            ok = False
        else:
            print(f"  ok: mutated tracked file detected, and named -> {diff}")

        # Restore -> silence must come back, or the bracket is noise rather than a signal.
        (root / "b.txt").write_text("two\n")
        diff, _ = differences(before, capture(root, base))
        if diff:
            print(f"FAIL: restoring the file left the bracket dirty: {diff}")
            ok = False
        else:
            print("  ok: restoring the file returns the bracket to silence")

        # Direction 2: metadata moves -> the bracket must say so. A tag is the cheapest mutation
        # that touches neither the worktree nor the shared stash stack.
        _git(root, "tag", "probe-tag")
        # r2.50a mechanism (5): the record carries DIGESTS, never verbatim text, so the delta
        # identifies the moved entry by its digest rather than by its name. The property under
        # test is unchanged and is the one addendum 3d needs -- WHICH entry moved must still be
        # identifiable -- so the expectation is the digest of the entry we just created. Asserting
        # the digest rather than merely "something changed" is what keeps this test binding: a
        # bracket that reported a change without identifying it would pass the weaker form.
        probe_digest = _digest("probe-tag")
        _, diff = differences(before, capture(root, base))
        if not any("metadata CHANGED" in d for d in diff) or not any(
            probe_digest in d for d in diff
        ):
            print(f"FAIL: a new tag did not break the bracket. diff={diff}")
            ok = False
        else:
            print("  ok: metadata delta detected, and the moved entry is identified BY DIGEST")

        if any("probe-tag" in d for d in diff):
            print("FAIL: the record carried the tag name VERBATIM; mechanism (5) forbids it")
            ok = False
        else:
            print("  ok: the entry's TEXT never reaches the record, only its digest")

        _git(root, "tag", "-d", "probe-tag")
        _, diff = differences(before, capture(root, base))
        if diff:
            print(f"FAIL: removing the tag left the bracket dirty: {diff}")
            ok = False
        else:
            print("  ok: removing the tag returns the bracket to silence")

        # Direction 3: the PINNED set. A file committed between the two halves must NOT register
        # as a change, because no reviewer made it -- while a mutation to a pinned file still must.
        # This is the property that makes the evidence record committable mid-gate.
        (root / "evidence.json").write_text("{}\n")
        _git(root, "add", "evidence.json")
        _git(root, "commit", "-qm", "the evidence record, committed after the before-capture")
        after = capture(root, base, names=before["gated_files"])
        diff, _ = differences(before, after)
        if diff:
            print(f"FAIL: a file committed after the capture broke the pinned bracket: {diff}")
            ok = False
        else:
            print("  ok: a file added after the capture does NOT break the pinned bracket")
        (root / "b.txt").write_text("two-MUTATED-AGAIN\n")
        after = capture(root, base, names=before["gated_files"])
        if not any("b.txt" in d for d in differences(before, after)[0]):
            print("FAIL: pinning the set also stopped it noticing a real mutation")
            ok = False
        else:
            print("  ok: pinning does not blind it to a real mutation of a pinned file")
        (root / "b.txt").write_text("two\n")

        # Direction 4: the instrument's OWN failure. A bracket that cannot see the tree must say
        # so, never "held". This is the direction the first six checks structurally could not
        # cover, because every one of them ran inside a working repo.
        # OUTSIDE the throwaway repo, or `git -C` walks up and finds it -- my first version of
        # this check put the directory INSIDE `root`, so it passed by hitting the empty-set guard
        # instead of the git-failure guard, and its label claimed a direction it never tested.
        # Caught because both messages came out identical.
        with tempfile.TemporaryDirectory() as outside:
            try:
                capture(Path(outside), "HEAD")
                print("FAIL: a capture in a NON-REPOSITORY succeeded and would be read as held")
                ok = False
            except BracketUnusable as exc:
                assert "git " in str(exc), f"refused for the wrong reason: {exc}"
                print(f"  ok: a non-repository is refused BY THE GIT GUARD -> {str(exc)[:58]}")
        try:
            capture(root, "HEAD", "HEAD")  # an empty range: no gated files at all
            print("FAIL: an EMPTY gated set was accepted; a digest over nothing compares equal")
            ok = False
        except BracketUnusable as exc:
            print(f"  ok: an empty gated set is refused -> {str(exc)[:60]}")

        # Direction 5: the #410 ruling-4 property. A metadata-only move is REPORTED and is NOT a
        # verdict; a content change still is. Gate 6's own run exited 1 for two reviewer worktrees
        # while the content digest was identical, which is the behaviour this direction pins shut.
        _git(root, "tag", "verdict-probe")
        content_half, metadata_half = differences(
            before, capture(root, base, names=before["gated_files"])
        )
        if content_half or not metadata_half:
            print(f"FAIL: a metadata-only move must be metadata-only. content={content_half}")
            ok = False
        else:
            print("  ok: a metadata-only move is reported and is NOT a content verdict")
        (root / "b.txt").write_text("two-MUTATED-WITH-METADATA\n")
        content_half, metadata_half = differences(
            before, capture(root, base, names=before["gated_files"])
        )
        if not content_half:
            print("FAIL: a content change alongside a metadata move must still be a verdict")
            ok = False
        else:
            print("  ok: a content change is still a verdict even when metadata moved too")
        (root / "b.txt").write_text("two\n")
        _git(root, "tag", "-d", "verdict-probe")

        # Direction 6: a stash RENUMBERING is not a difference. The stack is shared, so another
        # agent pushing one entry renumbers every entry below it; keying by index turned that into a
        # whole-stack delta (measured on gate 6's after-half: 26 lines for one real change), which is
        # the cry-wolf failure this tool's own docstring warns about.
        same_entry = "WIP on branch: 1234567 some commit subject"
        if _strip_stash_index(f"stash@{{0}}: {same_entry}") != _strip_stash_index(
            f"stash@{{7}}: {same_entry}"
        ):
            print("FAIL: the same stash entry at two indices still compares as different")
            ok = False
        else:
            print("  ok: a stash renumbering is not reported as a difference")
        untouched = "not a stash line: leave me alone"
        if _strip_stash_index(untouched) != untouched:
            print("FAIL: a non-stash line was rewritten by the stash key")
            ok = False
        else:
            print("  ok: a non-stash line passes through the stash key unchanged")

        print("SELF-TEST PASSED" if ok else "SELF-TEST FAILED")
        return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, help="repository to measure (read-only)")
    ap.add_argument("--base", help="diff base for the gated set")
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--out", type=Path, help="write the capture here as JSON")
    ap.add_argument(
        "--compare", type=Path, help="compare against an earlier capture and exit 1 on any delta"
    )
    ap.add_argument("--self-test", action="store_true", help="prove the bracket can fail (rule 3b)")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    if not args.root or not args.base:
        ap.error("--root and --base are required unless --self-test is given")

    try:
        now = capture(args.root, args.base, args.head)
    except BracketUnusable as exc:
        print(f"BRACKET UNUSABLE (this is NOT 'held'): {exc}")
        return 2

    if args.compare:
        before = json.loads(args.compare.read_text())
        # Re-measure the PINNED set, not a fresh diff (see `capture`).
        try:
            now = capture(args.root, args.base, args.head, names=before["gated_files"])
        except BracketUnusable as exc:
            print(f"BRACKET UNUSABLE (this is NOT 'held'): {exc}")
            return 2
        content, metadata = differences(before, now)
        if metadata:
            # Reported ALWAYS, and never fatal. Read it: addendum 3d says an unexplained entry is
            # investigated and reported, never dropped.
            print("METADATA MOVED (not a verdict — read it, then explain each line):")
            for line in metadata:
                print("  " + line)
        if content:
            print("BRACKET BROKEN — a gated file CHANGED during the review. The gate is VOID:")
            for line in content:
                print("  " + line)
            return 1
        print(
            f"bracket HELD: content {now['content_digest'][:8]} over "
            f"{len(now['gated_files'])} gated files unchanged"
            + (
                "; metadata moved, see above"
                if metadata
                else f"; metadata {now['metadata_counts']}"
            )
        )
        return 0

    shapes = shape_scan_gated(args.root, now["gated_files"])
    now["shape_scan"] = shapes

    text = json.dumps(now, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
        print(f"wrote {args.out}")
    print(
        f"content digest {now['content_digest'][:8]} over {len(now['gated_files'])} gated files "
        f"(base {args.base}, head {now['head_sha'][:8]}); metadata {now['metadata_counts']}"
    )
    print(
        f"shape scan: {shapes['files_scanned']} scanned, "
        f"{shapes['unaccounted_shapes']} unaccounted shapes in "
        f"{shapes['files_with_unaccounted']} files "
        f"({shapes['verdict_half_live']})"
    )
    if shapes["absent_from_worktree"]:
        print(
            f"  absent from the worktree, so not scanned — deleted by the gated change "
            f"({len(shapes['absent_from_worktree'])}): " + ", ".join(shapes["absent_from_worktree"])
        )
    if shapes["could_not_scan"]:
        # The gate FAILS here, and says which files and why. Ruling #455 item 2: the fix is to make
        # the file scannable or exclude it by a signed property, never to drop it from the set.
        print(
            f"SHAPE SCAN COULD NOT LOOK at {len(shapes['could_not_scan'])} gated file(s). A scan "
            "that could not look certifies nothing, so this is a FAILURE, not a skip:"
        )
        for rel, reason in sorted(shapes["could_not_scan"].items()):
            print(f"  {rel}: {reason}")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
