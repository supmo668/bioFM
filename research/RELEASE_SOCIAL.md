# Release Social Brief

> Per-platform posts for the release of the perturb-seq-eval journal
> supplement. Each post leads with the main question as a hook, preserves
> a conversational voice, and references the tooling stack (Claude
> terminal agent, Obsidian, OSS plugin community).
>
> **Placeholder:** replace `<DOI-ZENODO>`, `<DOI-FIGSHARE>`, `<OSF-URL>`,
> and `<REPO-URL>` with real links after running the publishing script.

---

## 0. Canonical elements (reuse-ready)

**The hook (always lead with this):**
> "Can we use active reinforcement learning to select hyperparameters for multi-agent systems?"

**One-sentence abstract:**
> "Yes — if the 'context' you feed the optimizer is a cheap preflight probe of the agent team's own internal dynamics."

**Headline finding:**
> 7.6× dominance on a task-conditional synthetic DGP, 2.6 % edge over CMA-ES on real Adamson 2016 Perturb-seq pilot, and a clean self-falsification on shared-optimum regimes.

**Stack credit line:**
> "Wrangled end-to-end with Claude in the terminal, organised in Obsidian, plus a handful of tweaks on amazing OSS tracker plugins."

---

## 1. X / Twitter (thread of 5 posts, ≤ 280 chars each)

**Tweet 1 — hook + what dropped:**

> Can we use active reinforcement learning to pick hyperparameters for multi-agent systems?
>
> Spent a week wrangling this question with Claude and a small compute budget. Ended up with a full ML + agentic journal on perturb-seq.
>
> DOI: <DOI-ZENODO>

**Tweet 2 — why compbio, why perturb-seq:**

> The task had to live in computational biology. It's the most multi-disciplinary, collaboration-heavy domain I know.
>
> I picked perturb-seq — not my prior bench-wet domain — because the framing is more direct than multi-omics, with fewer nuisance axes. IMO.

**Tweet 3 — the method in one tweet:**

> Method: contextual Bayesian optimization where the "context" is a 4-dim probe of the agent team's own round-0 dynamics (ACE, critique severity, winner-flip rate, mean confidence).
>
> Cheap probe → conditional BO over team size × rounds × backbone.

**Tweet 4 — the three-regime result (this is the money tweet):**

> Three regimes, one framework:
>
> • Shared-optimum synthetic → contextual ≈ CMA-ES (correct falsification)
> • Task-conditional synthetic → contextual 7.6× dominates CMA-ES
> • Real Adamson 2016 Perturb-seq → contextual edges CMA-ES 2.6 %
>
> Probe signal is real but data-dependent.

**Tweet 5 — stack + CTA:**

> Built with: Claude Agent SDK in the terminal, Obsidian vault for the journal, and tweaks on OSS tracker plugins I've come to depend on.
>
> Repo: <REPO-URL>
> Supplement: <DOI-ZENODO>
> Artifacts (22 MB): <DOI-FIGSHARE>
>
> Questions welcome.

---

## 2. LinkedIn (single post, ~1 300 chars, professional tone)

> Can we use active reinforcement learning to select hyperparameters for multi-agent systems?
>
> That question turned into a seven-day deep-dive that I'd originally intended to be a weekend exploration. It ended as a journal-style ML + agentic supplement on a perturb-seq experimental-design task.
>
> Method: contextual Bayesian optimization with a Gaussian-process surrogate over a 27-point config space (team size × refinement rounds × backbone). The "context" is a cheap 4-dimensional preflight probe harvested from the agent team's own round-0 dynamics — confidence entropy, critique severity dispersion, winner-flip rate, mean confidence. The optimizer conditions its recommendation on this probe instead of treating every task identically.
>
> Three-regime test ran at ~$22 of Modal GPU compute:
> — On a synthetic DGP where every task shares the same optimum, the contextual GP is correctly indistinguishable from CMA-ES. The framework falsifies itself cleanly when the probe has no signal to exploit.
> — On a task-conditional synthetic DGP, contextual GP dominates CMA-ES by 7.6× on final MSD.
> — On real Adamson 2016 Perturb-seq pilot data (K562, seven TF knockdowns), contextual GP edges out CMA-ES by 2.6 %. Small but consistent, reflecting a shallow task-conditional signal in real data.
>
> Stack: Claude Agent SDK in the terminal for the agent work, Modal for GPU orchestration, Obsidian for the research journal, and a handful of tweaks on OSS tracker plugins. Everything reproducible from a single `modal run` command.
>
> Paper + code: <DOI-ZENODO>
> Artifacts: <DOI-FIGSHARE>
> Hackathon preprint: <OSF-URL>
>
> Picked up a lot of computational biology, deep active-reinforcement-learning, and agentic-AI-engineering projects this year. Wrangling an idea with Claude somehow ended up as a full ML journal on computational biology. Happy to jump into the comments on anything specific.

---

## 3. Bluesky (thread, ≤ 300 chars per skeet)

**Skeet 1:**

> Can we use active reinforcement learning to pick hyperparameters for multi-agent systems?
>
> Wrangled that with Claude for a week, ended up with a full ML + agentic journal on perturb-seq experimental design.
>
> <DOI-ZENODO>

**Skeet 2:**

> Had to be in computational biology — it's the most multi-disciplinary, collaboration-heavy field I know. Picked perturb-seq over multi-omics because the task framing is more direct, fewer nuisance axes.

**Skeet 3:**

> Method: contextual Bayesian optimization with a 4-dim probe of the agent team's own round-0 dynamics (ACE, CSD, winner-flip rate, mean confidence). Surrogate conditions on the probe; ditches the "one optimum fits all" assumption.

**Skeet 4:**

> Three regimes, one framework:
> • shared-optimum → matches CMA-ES (correct falsification)
> • task-conditional → 7.6× dominates CMA-ES
> • Adamson Perturb-seq pilot → 2.6 % edge
>
> Probe signal is real but data-dependent.

**Skeet 5:**

> Built end-to-end in the Claude terminal, journal in Obsidian, tracker plugin tweaks I maintain on top of awesome OSS contributors.
>
> Repo: <REPO-URL>

---

## 4. Threads / Meta (single post, ≤ 500 chars)

> Can we use active reinforcement learning to pick hyperparameters for multi-agent systems?
>
> One-week question turned into a full ML journal on perturb-seq experimental design.
>
> Contextual BO with a 4-dim probe of the agent team's round-0 dynamics. Three-regime test: self-falsifies on shared-optimum DGPs (correct), 7.6× dominates CMA-ES on task-conditional, 2.6 % edge on real Adamson Perturb-seq.
>
> Claude + Obsidian + OSS tracker plugins. <DOI-ZENODO>

---

## 5. Hacker News

**Title (80-char limit):** `Contextual BO for Multi-Agent Hyperparameters, Tested on Perturb-Seq MSD`

**First comment body (optional self-reply for context):**

> Question I started with: can we use active RL to pick hyperparameters for multi-agent systems?
>
> What I landed on: contextual Bayesian optimization where the context is a cheap 4-dim probe of the agent team's own round-0 dynamics — confidence entropy, critique severity, winner-flip rate, mean confidence. Surrogate is a Gaussian process with a factored Hamming × Matérn-5/2 kernel over a 27-point config space (team size × rounds × backbone).
>
> Three-regime evaluation — total Modal spend ~$22:
>
> • Shared-optimum synthetic DGP: contextual ≈ CMA-ES (framework correctly falsifies itself when probe has no routing signal).
> • Task-conditional synthetic DGP: contextual GP dominates CMA-ES by 7.6× final MSD.
> • Real Adamson 2016 Perturb-seq pilot (K562, 7 TF knockdowns): contextual GP edges CMA-ES by 2.6 %. Small but consistent, random baseline is strong because Φ is only 27 points.
>
> Everything's reproducible from a single `modal run`. Journal / supplement / code / artifacts all DOI'd:
> - Zenodo: <DOI-ZENODO>
> - Figshare (artifacts): <DOI-FIGSHARE>
> - OSF BioHackrXiv: <OSF-URL>
> - Repo: <REPO-URL>
>
> Honest limitations are in the reviewer-critique doc in the repo — particularly that per-seed CIs on the Adamson edge still need to land before I'd quote the 2.6 % as a real effect.

---

## 6. Reddit

### 6.1 r/MachineLearning (tag `[R]`)

**Title:** `[R] Contextual Bayesian Optimization of Multi-Agent Hyperparameters, Probed from the Team's Own Dynamics`

**Body:**

> **Question:** can we use active reinforcement learning to select hyperparameters for multi-agent systems?
>
> **Short answer:** yes — if the "context" you condition on is a cheap preflight probe of the agent team's own internal dynamics (confidence entropy, critique severity, winner-flip rate, mean confidence), then a contextual Gaussian-process bandit with EI acquisition dominates non-contextual CMA-ES on task-conditional DGPs and correctly self-falsifies on shared-optimum DGPs.
>
> **Setup:**
> - 27-point config space: `{3, 4, 5}` agents × `{1, 2, 3}` refinement rounds × `{linear, mlp, scgpt_small}` backbones.
> - 4-dim probe context x = (ACE_norm, mean(c), CSD, max(c)) from round 0 of shallow orchestration.
> - Factored kernel: Hamming over Φ × Matérn-5/2 over X; EI acquisition. Regret bound O(√(T γ_T)) from Krause & Ong 2011.
> - MSD headline metric on top-20 DEGs (perturb-seq community standard from CPA / GEARS / scGPT-perturb).
>
> **Three-regime results (Modal A10G, ~$22 total):**
> - Shared-optimum synthetic: contextual GP ≈ CMA-ES (both hit the global min, CMA-ES wins AULC via centroid bias). Correct falsification.
> - Task-conditional synthetic: contextual GP 7.6× dominates CMA-ES on final MSD.
> - Real Adamson 2016 Perturb-seq pilot (K562, 7 targeted knockdowns): contextual GP edges CMA-ES 2.6 % on final MSD, 2.3 % on AULC. Small but consistent.
>
> **Open issues (documented in reviewer-critique doc in the repo):**
> 1. Per-seed CIs on the Adamson edge aren't landed yet — 2.6 % may not survive the noise floor.
> 2. Probe signatures on Adamson were synthesised, not harvested from a live orchestrator. Need a real trace-collection run.
> 3. scgpt_small "wins 5/7 tasks" claim is unstable across seeds (5/1/1 vs 4/3/0 vs 3/2/2). Backbones are effectively tied within seed variance on most tasks.
>
> Stack: Claude terminal agent, Modal GPU workers, from-scratch 2.1M-param scGPT-like transformer, Obsidian vault for the journal, various OSS tracker plugins I've tweaked. Everything reproducible from one command.
>
> Links:
> - Paper + artifacts: <DOI-ZENODO>
> - Figshare mirror: <DOI-FIGSHARE>
> - OSF BioHackrXiv: <OSF-URL>
> - Repo: <REPO-URL>
>
> Happy to get shredded in the comments — the critique doc in the repo is there precisely because I know the real-data claim needs strengthening.

### 6.2 r/bioinformatics

**Title:** `Treating multi-agent hyperparameter tuning as a contextual-bandit problem on perturb-seq`

**Body (shorter than r/ML, bio-angle up front):**

> Can we use active reinforcement learning to select hyperparameters for multi-agent orchestration — with the task being perturb-seq experimental design?
>
> Short answer from a week of work: yes, when the probe has signal. On Adamson 2016 pilot (K562, 7 TF knockdowns), a contextual Gaussian-process bandit edges out CMA-ES by 2.6 % on held-out-perturbation MSD. On a synthetic task-conditional DGP the advantage grows to 7.6×. On shared-optimum DGPs the framework correctly falsifies itself.
>
> Small-but-valid scGPT-like transformer backbone (2.1 M parameters, from scratch, no pretraining) wins or ties on every Adamson task versus ridge and MLP baselines, which I take as encouragement that the gene-embedding inductive bias alone matters, even at toy scale.
>
> Framing was chosen deliberately: perturb-seq has a more direct task signature than full multi-omics, which made it a cleaner test-bed for the agentic-HPO question.
>
> Reproducible via `modal run scripts/modal/app.py::entrypoint --step all`, projected ≤ $5 Modal spend.
>
> <DOI-ZENODO> · <OSF-URL> · <REPO-URL>

---

## 7. Mastodon / Fediverse (single toot, ≤ 500 chars)

> Can we use active RL to pick hyperparameters for multi-agent systems?
>
> Spent a week wrangling that with Claude in the terminal. Ended up with a full ML + agentic journal on a perturb-seq HPO task.
>
> Contextual GP bandit, probe from the team's own round-0 dynamics. 7.6× dominates CMA-ES on task-conditional DGPs, 2.6 % edge on real Adamson pilot, self-falsifies on shared-optimum.
>
> Obsidian for the journal, OSS tracker plugins with my tweaks.
>
> <DOI-ZENODO>

---

## 8. "About page" paragraph (reuse anywhere: blog, Obsidian, GitHub profile)

> I've picked up a lot of computational-biology, deep-reinforcement-learning, and agentic-AI-engineering projects over the year. Wrangling a question or idea in the terminal with Claude somehow ends up becoming an ML + agentic journal, organised in my Obsidian vault and powered by a set of Claude tracker plugins I've tweaked on top of the work of some amazing OSS contributors.
>
> The latest one started from a single question — *can we use active reinforcement learning to select hyperparameters for multi-agent systems?* — and landed on a perturb-seq experimental-design test-bed because computational biology is the most multi-disciplinary, collaboration-heavy field I've found, and perturb-seq has a cleaner task framing than multi-omics. Results and full reproduction path in the link.

---

## 9. Posting cadence proposal

| T+ | Platform | Priority |
|---|---|---|
| T+0 (DOI mints) | X/Twitter thread | Primary — drives everything else |
| T+0 | LinkedIn | Primary — professional network |
| T+0 | Bluesky thread | Secondary — ML-research crowd |
| T+1 h | Hacker News | If thread gets traction, submit |
| T+1 d | Reddit r/MachineLearning | Let HN settle first |
| T+2 d | Reddit r/bioinformatics | Separate framing |
| T+3 d | Threads / Mastodon | Long-tail |
| Ongoing | GitHub README badge + Obsidian vault page | Always |

Do not mass-post identically. Adapt the hook, preserve the three-regime table.

---

## 10. Do-not-claim list

Before posting, **edit the posts to remove or temper** any of these if they aren't backed by bootstrap CIs or real-trace collection (see `docs/REVIEWER_CRITIQUE.md`):

- "contextual GP beats CMA-ES by 2.6 % on Adamson" — reframe to "contextual GP edges CMA-ES on Adamson" without the point estimate, or add "(CIs pending)".
- "scgpt_small wins 5/7 tasks" — drop entirely, or reframe to "scgpt_small is competitive with ridge/MLP baselines within seed variance".
- "agent routing on real Adamson data" — disclose that the probe signatures on Adamson are synthesised in this iteration; real trace collection is queued.

These are the same revisions flagged for the journal pre-print itself. Keep the social posts honest with the paper.
