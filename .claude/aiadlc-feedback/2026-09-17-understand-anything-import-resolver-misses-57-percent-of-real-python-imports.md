# `understand-anything`'s Python import resolver misses **57% of real internal imports** — and the two causes are the idioms of the frameworks it lists as supported

**Plugin:** `understand-anything` 2.8.0
**Component:** `skills/understand/extract-import-map.mjs` (`resolvePythonImport`, and the module-level-only import walk)
**Severity:** high — the dependency graph is the product, and it silently understates the real graph by more than half
**Observed:** 2026-09-17, bioFM, during a full `/understand` run. Found by the project-scanner subagent, reproduced on a synthetic fixture, and quantified independently by the assemble-reviewer with an AST pass.

## The measurement

Independent ground truth was built by walking all 277 scanned files with an AST pass that resolves absolute, relative **and** src-layout module paths, and that counts function-scoped imports:

| | count |
|---|---|
| Real internal Python import pairs | **235** |
| Present in the produced graph | 100 |
| **Absent** | **135 (57%)** |

| project | absent | cause A (src-layout) | cause B (function-scoped) |
|---|---|---|---|
| `perturb-seq-eval` | 116 | 67 | 48 (+1 both) |
| `lung-on-chipsim` | 19 | 1 | 18 |

The absence is **uniform** — analyzers were instructed not to compensate, and the produced `imports` edges are exactly the 100 pairs the tool emitted: 0 invented, 0 missing relative to tool output.

## Cause A — only module-level imports are collected

The extractor walks module-level imports only. An identical import moved inside a `def` body is lost. Confirmed on a 5-file synthetic fixture holding importer/target constant and varying only nesting:

| fixture case | result |
|---|---|
| top-level `from pkg.mod import X`, importer inside `src/` | resolves |
| same import, function-scoped | **`[]`** |
| top-level, importer outside `src/` | **`[]`** |

**Why this is not an edge case.** Modal — which this plugin's own framework detection lists — requires imports inside the remote function body so they execute in the container image. In this repo `scripts/modal/app_biofm.py` has 22 import lines of which **6** are module-level; `app_v05.py` has 17 of which 7. The entire remote execution layer is written in the idiom the extractor cannot see.

It is not Modal-specific either: `chipsim/pipeline.py`, an ordinary Typer CLI, has 17 import lines and 8 at module level — lazy imports in subcommands are a standard CLI startup-time pattern. That accounts for 18 of lung-on-chipsim's 19 missing edges.

## Cause B — the src-layout is never probed

`resolvePythonImport` (around `extract-import-map.mjs:752-760`) resolves an absolute import by walking **ancestors of the importer's directory**:

```js
const importerParts = importerDir ? importerDir.split('/').filter(Boolean) : [];
for (let i = importerParts.length; i >= 0; i--) {
  const rootParts = importerParts.slice(0, i);
  const candidateModule = rootParts.concat(tailSegments);
  ...
}
```

For an importer at `projects/perturb-seq-eval/scripts/local/x.py` the candidates are `scripts/local/`, `scripts/`, `perturb-seq-eval/`, `projects/`, root. The package lives at `projects/perturb-seq-eval/src/perturb_eval/`. **`src/` is a sibling of `scripts/`, never an ancestor, so it cannot be reached.**

The layout is declared, and the resolver does not read the declaration:

```toml
packages = [{ include = "perturb_eval", from = "src" }]
```

Poetry's `src` layout is standard and the plugin lists Poetry as a detected framework. Every importer outside `src/` — `scripts/`, `examples/`, `tests/` — is affected.

## Why it matters more than the number suggests

A missing edge and a real absence are indistinguishable in the output. In this repo the graph shows `perturb_eval` as a package nothing outside itself imports, when `scripts/` is its entire driver layer. A reader — or a downstream fan-in metric — concludes the execution layer is dead code.

This is the failure mode the tool exists to prevent: it produces a confident, complete-looking artifact whose gaps are invisible at the point of use.

## Suggested fixes, in order

1. **Walk nested imports.** Collect `Import`/`ImportFrom` at any depth, not just module scope. Optionally tag them (`scope: "function"`) so consumers can weight them differently, but collect them.
2. **Read the packaging declaration.** Parse `pyproject.toml` for `tool.poetry.packages[].from`, and the equivalent setuptools `package-dir` / hatch `packages`, and add those roots to the candidate set.
3. **Failing (2), probe sibling `src/`.** A `src/` directory beside the nearest `pyproject.toml` is a near-universal convention and a cheap fallback.
4. **Report the gap.** `scan-result.json` should carry a count of import statements *seen but not resolved*. A resolver that silently returns `[]` gives a downstream consumer no way to know whether a file has no imports or unresolvable ones — which is what made this take an AST pass to quantify.

## Related, same run

`merge-batch-graphs.py` globs every `batch-*.json` in `intermediate/` with no provenance check. An abandoned earlier run (2026-08-22, Phase 7 cleanup never reached) left six batch files there; today's run wrote `batch-1.json` while the stale run had left `batch-1-part-1.json` and `batch-1-part-2.json`, which nothing in the new run would overwrite. Merging would have mixed a month-old graph of a different file set into the new one, and dedup-by-ID would have concealed it. Suggested: record the git commit hash or run id in each batch file and have the merge refuse or ignore foreign ones.
