const fs = require('fs');
const ROOT = '/Users/mo/github/personal/bioFM';
const SKILL_DIR = '/Users/mo/.claude/plugins/cache/understand-anything/understand-anything/2.8.0/skills/understand';
const b = JSON.parse(fs.readFileSync(ROOT + '/.understand-anything/intermediate/batches.json', 'utf8'));
const s = JSON.parse(fs.readFileSync(ROOT + '/.understand-anything/intermediate/scan-result.json', 'utf8'));
const name = s.projectName || s.name || 'bioFM';
const desc = (s.description || s.projectDescription || '').replace(/ Note: this project has over 100.*$/, '');
const langs = (s.languages || []).join(', ');
const LANG = '> **Language directive**: Generate all textual content (summaries, descriptions, tags, titles, languageNotes, languageLesson) in **English**. Maintain technical accuracy while using natural, native-level phrasing in the target language. Keep technical terms in English when no standard translation exists (e.g., "middleware", "hook", "barrel").';
for (const x of b.batches) {
  const i = x.batchIndex;
  const files = x.files.map((f, k) => `${k + 1}. \`${f.path}\` (${f.sizeLines} lines, language: \`${f.language}\`, fileCategory: \`${f.fileCategory}\`)`).join('\n');
  const out = `Analyze these files and produce GraphNode and GraphEdge objects.
Project root: \`${ROOT}\`
Project: \`${name}\` — ${desc}
Languages: \`${langs}\`
Batch: \`${i}/${b.totalBatches}\`
Skill directory (for bundled scripts): \`${SKILL_DIR}\`
Output: write to \`${ROOT}/.understand-anything/intermediate/batch-${i}.json\` (single-file mode) OR \`batch-${i}-part-<k>.json\` (split mode, per Step B of your output protocol).

**IMPORTANT — output file naming:** the output file MUST be named exactly \`batch-${i}.json\` (or \`batch-${i}-part-<k>.json\`). Any other name is silently dropped by the merge script.

**Additional context from main session:**

Project: \`${name}\` — ${desc}
Languages: \`${langs}\`
Frameworks: PyTorch, Transformers, scikit-learn, Pydantic, Typer, pytest, Modal

${LANG}

Pre-resolved import data for this batch (use directly — do NOT re-resolve imports from source):
\`\`\`json
${JSON.stringify(x.batchImportData ?? {}, null, 1)}
\`\`\`

Cross-batch neighbors with their exported symbols (confidence boost for cross-batch edges):
\`\`\`json
${JSON.stringify(x.neighborMap ?? {}, null, 1)}
\`\`\`

Files to analyze in this batch (every entry MUST be passed through to \`batchFiles\` with all four fields — \`path\`, \`language\`, \`sizeLines\`, \`fileCategory\`):
${files}
`;
  fs.writeFileSync(`${ROOT}/.understand-anything/tmp/prompt-${i}.md`, out);
}
console.log('wrote', b.batches.length, 'prompt files');
