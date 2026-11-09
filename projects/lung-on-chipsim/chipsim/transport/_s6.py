"""The S6 absence guard, shared by every scaffold writer in this package.

Why this module exists rather than the constant living in `theta.py`: it DID live in
`theta.py`, and only theta's writer consulted it. Measured 2026-11-08 —
`prior.write_scaffold(configs/theta_priors.yaml)` returned normally and wrote 766 bytes,
creating the file whose ABSENCE is the mechanical form of "no coding agent writes a
biological number" (build-plan S6). `prior.py` never referenced the constant at all.

**A guard that one of two sibling writers calls is not a guard.** One definition, one
refusal, every caller — so a third writer added later inherits it instead of having to
remember it.
"""

from pathlib import Path

#: The two paths S6's absence guard owns. No writer in this package may create them.
S6_FORBIDDEN_RELPATHS = (
    Path("configs/theta_priors.yaml"),
    Path("configs/assumptions.yaml"),
)


def forbidden_match(path: Path) -> Path | None:
    """The S6 path `path` would land on, or None if it lands on neither.

    Two properties, both deliberate:

    `path.resolve()` FIRST, so a symlink is judged by its TARGET and not by its own
    spelling — `tmp/x.yaml -> configs/theta_priors.yaml` is refused. Preserved verbatim
    from theta.py's original check, which had it right.

    Comparison is case-FOLDED, which the original was not. The development filesystem
    here is APFS and case-insensitive, so `configs/Theta_Priors.yaml` is the same inode
    as the forbidden name: a case-sensitive compare skips the refusal on macOS and fires
    on a case-sensitive Linux CI. A guard whose verdict depends on the platform is worse
    than one that is merely strict, so this errs strict.
    """
    parts = tuple(p.casefold() for p in Path(path).resolve().parts)
    for forbidden in S6_FORBIDDEN_RELPATHS:
        want = tuple(p.casefold() for p in forbidden.parts)
        if len(parts) >= len(want) and parts[-len(want) :] == want:
            return forbidden
    return None
