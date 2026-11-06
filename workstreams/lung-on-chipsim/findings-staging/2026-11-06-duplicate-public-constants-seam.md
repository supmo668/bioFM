---
type: findings-staging
status: >
  DRAFTED and unratified. NO CODE WAS CHANGED. This is a code-hygiene finding with a proposed fix
  that touches `chipsim/pipeline.py`, which puts it past the pre-authorized "pin-hardening" scope —
  so it is reported, not executed. Authorization to fix is requested in section 5.
authorization: >
  Pre-authorized reading + pin-hardening (inherited handoff, carried from CTO #796: authorization
  attaches to WRITING a claim or a value, never to reading). The MEASUREMENT below is inside that
  scope. The FIX is not, and was not performed.
exploratory: false
question: >
  The inherited pin-hardening queue recorded one latent gap: the duplicate-constant detector is
  per-file by construction, so `ENTRY_KEYS` existing in two modules with disjoint meanings is
  invisible to it. The question asked here is only "is that note accurate, and is the hazard
  latent?" It is accurate about `ENTRY_KEYS` and INCOMPLETE about the class.
reading_depth: >
  SOURCE-LEVEL, by AST over `chipsim/` plus a full grep of every use site. No behaviour was
  inferred from a name; every claim below names the file and line it was read from.
agent: biofm/matthew-mo/lung-on-chipsim
---

# Duplicate public module-level constants in `chipsim.transport` — DRAFTED, 2026-11-06

> **No code was changed.** No file under `projects/lung-on-chipsim/` was edited. The module subtree
> is still byte-identical to the trunk (`89b5c94d` on `origin/main` and on HEAD alike), so the
> standing suite measurement remains valid and provably so.

## 0. What the inherited note said, and how this corrects it

The handoff I inherited recorded **one** latent gap, in these terms:

> `ENTRY_KEYS` existing in two modules with **disjoint meanings** is invisible to it. Latent, not
> live — nothing imports `ENTRY_KEYS` across modules today.

**Both halves are true of `ENTRY_KEYS` and neither is true of the class.** An AST sweep of every
public module-level constant in `chipsim/` found **two** colliding names, not one, and the second
one **is** cross-imported. So the note was a correct reading of a real defect, scoped to one
instance — and the instance it named is the *harmless* one. Recording that asymmetry is the point
of this ledger: the name I was handed was not the name that matters.

## 1. The measurement

An AST pass over `chipsim/**/*.py` collecting module-level `ALL_CAPS` assignments without a leading
underscore, grouped by name, keeping only names bound in more than one module with a different
right-hand side. Exactly two survive, and there are **zero** false positives — every other shared
public constant name in the package has an identical definition.

| name | `chipsim/transport/theta.py` | `chipsim/transport/prior.py` |
|---|---|---|
| `ENTRY_KEYS` | `:58` `("value", "unit", "citation", "assumed")` | `:36` `("mean_log", "sigma_log", "citation", "assumed")` |
| `SCAFFOLD_RELPATH` | `:49` `configs/templates/theta_priors.scaffold.yaml` | `:30` `configs/templates/transport_prior.scaffold.yaml` |

The two tuples are **disjoint except for `citation` and `assumed`**, and the asymmetry is correct
and deliberate — `theta.py` carries a `unit`, `prior.py` does not, because a log-space prior carries
no single unit. That asymmetry was verified earlier and is not in question here. The hazard is not
that the values differ; it is that **the name does not**.

## 2. `ENTRY_KEYS` is latent. `SCAFFOLD_RELPATH` is not.

`ENTRY_KEYS` is never imported anywhere — the only uses are the two modules' own validators
(`theta.py:153,157`, `prior.py:68,71`). The inherited "latent" verdict holds for it.

`SCAFFOLD_RELPATH` is imported, from both modules, **in the same file**:

```
chipsim/pipeline.py:361:    from chipsim.transport.theta import SCAFFOLD_RELPATH, write_scaffold
chipsim/pipeline.py:373:    from chipsim.transport.prior import SCAFFOLD_RELPATH, write_scaffold
```

Note that **`write_scaffold` collides too** — the collision is on two names per site, not one. Two
test sites also reach the constant through its module (`tests/test_m1_inputs.py:151,246`), which is
the safe form.

## 3. What is TRUE today, stated before what could go wrong

**Today's behaviour is correct, and the suite is green.** The two imports sit inside two separate
functions — `_cmd_theta_scaffold` (`:360`) and `_cmd_transport_prior_scaffold` (`:372`) — so each
name is function-local and neither shadows the other. Nothing is broken. I am not reporting a bug.

**What I am reporting is where the correctness lives.** It rests on the *placement* of two import
statements inside two function bodies. Nothing in a type, a name, a test, or a comment records that
the placement is load-bearing. Hoisting those imports to module level — the ordinary, otherwise
harmless tidy-up that someone eventually does to two function-local imports — makes the second
binding silently win for the whole module, and `_cmd_theta_scaffold` would then write the **prior's**
template path. It would not raise. The scaffold command would report success and write to the wrong
file.

That is this workstream's own defect shape, one level down from evidence: **a correct reading
attributed to the wrong subject** — here, a correct constant attributed to the wrong module.

## 4. Why I did not simply add the guard

The obvious pin is a cross-file assertion: *a public module-level constant must not mean two
different things in two modules in `chipsim/`.* It is sound and non-noisy — proven above with zero
false positives — and it is squarely inside the pre-authorized pin-hardening scope.

**I did not add it, because it would go red and I cannot close it.** Its only two violations are the
rows in section 1, and closing them means renaming. For `ENTRY_KEYS` the rename is free and has an
in-repo precedent (`chipsim/harmonize/label_reference.py:37` uses `_REQUIRED_ENTRY_KEYS` —
module-private and distinctly named). For `SCAFFOLD_RELPATH` it is **not** free: it has live call
sites in `chipsim/pipeline.py` and two tests. **Adding a pin whose fix is not authorized would
leave the suite red, which is worse than leaving the hazard latent.** So the pin waits on the fix,
not the other way round.

This is also the session's own lesson applied: a guard I cannot close is an unsound instrument, and
the fault in an instrument is as expensive as a fault in a source.

## 5. The ask — one authorization, three bounded steps

The fix touches `chipsim/pipeline.py`, so it needs authorization and the full quality gate. Proposed,
in order, as one gated change:

1. **`ENTRY_KEYS` → `_ENTRY_KEYS`** in both modules. Private, so a cross-module import becomes a
   loud explicit act rather than an accident. Keeps the parallel naming, which is legible and
   correct. No call sites outside the two modules — zero blast radius.
2. **`SCAFFOLD_RELPATH` → distinct names** (`THETA_SCAFFOLD_RELPATH` / `PRIOR_SCAFFOLD_RELPATH`),
   updating `chipsim/pipeline.py:361,363,373,375` and `tests/test_m1_inputs.py:151,246`. Private is
   not available here because the constant is legitimately part of the module's surface. Distinct
   names make the collision impossible instead of merely unlikely. Whether `write_scaffold` should
   be disambiguated the same way is a second question I am NOT pre-deciding.
3. **Then** add the cross-file guard from section 4, which is green at that point and keeps the
   class closed.

Steps 1 and 3 alone are defensible as pure pin-hardening if step 2 is not wanted. **Step 3 must not
land without step 2**, or the suite goes red.

## 6. Limits of this finding

- **Scope was `chipsim/` only.** Test files were deliberately excluded: they legitimately share
  `ROOT` and `CONFIGS`, so including them would have produced a noisy instrument and a misleading
  count.
- **Public names only.** A collision between two already-private constants is harmless and was not
  counted.
- **No runtime claim.** I did not execute `/scaffold-theta` or `/transport-prior-scaffold` to observe
  the hoist failure; the failure mode in section 3 is read from the import placement, and it is
  stated as a consequence of a refactor that has **not** happened, not as an observed defect. If a
  verdict on it is wanted, the honest test is to hoist the imports on a scratch branch and run the
  two commands — which is a code change and therefore not mine to start here.
