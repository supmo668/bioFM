"""End-to-end smoke test — real data, real LLM, real metrics.

Pipeline:
    1. Load .env and validate the OpenRouter key.
    2. Read Adamson2016 h5ad via adamson_loader.
    3. Synthesise a minimal 5-agent 2-round trace with Adamson-derived task names.
    4. Rate each AgentVote.reason via OpenRouter + Nemotron.
    5. Project into a RunTrace, roll up metrics, persist artifacts.

Usage:
    python3 scripts/live_smoke.py [--config configs/live.yaml]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from perturb_eval._env import load_env_file  # noqa: E402
from perturb_eval.adamson_loader import load_adamson_h5ad, perturbation_as_task_name  # noqa: E402
from perturb_eval.backends.openrouter import OpenRouterBackend  # noqa: E402
from perturb_eval.instrumentation import round_trace_from_consensus_round, run_trace_from_consensus  # noqa: E402
from perturb_eval.metrics import run_metrics  # noqa: E402
from perturb_eval.types import RoundTrace, RunTrace  # noqa: E402


@dataclass
class FakeProposal:
    agent: str
    confidence: float


@dataclass
class FakeCritique:
    from_agent: str
    on_agent: str
    severity: float


@dataclass
class FakeRound:
    proposals: list[FakeProposal]
    critiques: list[FakeCritique]


@dataclass
class FakeConsensus:
    rounds: list[FakeRound]
    converged: bool


AGENT_NAMES = ("DataCurator", "Literature", "Architect", "Trainer", "Validator")


def synthesise_trace(task_name: str) -> FakeConsensus:
    """A minimal 5-agent × 2-round propose-critique-vote trace for smoke testing.

    We synthesise confidences that rise round-over-round (convergent case).
    Critique severities are placeholders; the live LLM will overwrite them in
    a fuller integration. For the smoke test we only exercise the rater on
    sample reason strings (see main()).
    """
    rd0 = FakeRound(
        proposals=[FakeProposal(a, 0.55 + 0.03 * i) for i, a in enumerate(AGENT_NAMES)],
        critiques=[],
    )
    rd1 = FakeRound(
        proposals=[FakeProposal(a, 0.70 + 0.04 * i) for i, a in enumerate(AGENT_NAMES)],
        critiques=[],
    )
    # Leave critiques empty here; we'll attach LLM-rated ones in main().
    return FakeConsensus(rounds=[rd0, rd1], converged=True)


def render_prompt(prompt_path: Path, *, voter_id: str, voted_for: str,
                  answer_labels: str, reason_text: str) -> tuple[str, str]:
    body = prompt_path.read_text(encoding="utf-8")
    system_part, _, user_part = body.partition("## User")
    system = system_part.replace("## System", "").strip()
    user = user_part.format(
        voter_id=voter_id,
        voted_for=voted_for,
        answer_labels=answer_labels,
        reason_text=reason_text,
    ).strip()
    return system, user


def run(args: argparse.Namespace) -> int:
    load_env_file(PROJECT_ROOT.parent.parent / ".env")

    cfg_path = Path(args.config)
    # Minimal YAML parser (stdlib only); we treat the config as documentation
    # of intent, and read the few actually-needed values directly. This keeps
    # the smoke test dependency-light.
    _ = cfg_path.read_text(encoding="utf-8")

    # --- 1. data -----------------------------------------------------------
    h5ad = PROJECT_ROOT / "data" / "Adamson2016_pilot.h5ad"
    if not h5ad.exists():
        print(f"[FAIL] {h5ad} missing — run scripts/fetch_adamson.py first", file=sys.stderr)
        return 1
    qc = load_adamson_h5ad(h5ad)
    tasks = [perturbation_as_task_name(p) for p in qc.perturbation_names
             if not p.startswith("*") and not p.startswith("62(")]
    print(f"[data] Adamson2016 — {qc.n_cells} cells, {qc.n_genes} genes, "
          f"{len(tasks)} non-control perturbations")

    # --- 2. LLM backend ----------------------------------------------------
    backend = OpenRouterBackend.from_env()
    print(f"[llm] model={backend.model} base={backend.base_url}")

    # --- 3. Synthesise trace for the first real task ----------------------
    task_name = tasks[0]  # e.g. "BHLHE40 knockdown"
    consensus = synthesise_trace(task_name)

    # --- 4. Build a small set of realistic critique reasons and rate them -
    sample_reasons = [
        ("Architect", "DataCurator", "The proposed QC thresholds are too strict for K562 and drop valid CRISPRi cells."),
        ("Trainer",   "Architect",   "Picking scGPT is fine, but the perturbation-head rank of 8 may underfit BHLHE40's sparse response."),
        ("Validator", "Literature",  "Expected-up gene list is too short; missing HSPA5 / DDIT3 which are canonical UPR markers."),
        ("Literature","Trainer",     "By-donor CV is irrelevant in a K562 clonal cell line; use by-guide instead."),
        ("DataCurator","Validator",  "Reported pathway enrichment does not control for the guide-RNA batch effect."),
    ]
    prompt_path = PROJECT_ROOT / "massgen_skill_draft" / "prompts" / "severity_rater.md"

    artifacts_dir = PROJECT_ROOT / "artifacts" / "live"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    trace_log = artifacts_dir / "llm_calls.jsonl"

    rated: list[FakeCritique] = []
    with trace_log.open("a", encoding="utf-8") as fh:
        for src, tgt, reason in sample_reasons:
            system, user = render_prompt(
                prompt_path,
                voter_id=src, voted_for=tgt, answer_labels=",".join(AGENT_NAMES),
                reason_text=reason,
            )
            t0 = time.time()
            try:
                # Nemotron Super models emit chain-of-thought; give them room
                # to think and still produce a final numeric verdict.
                out = backend.complete(system=system, user=user, max_tokens=96, temperature=0.0)
            except Exception as e:
                print(f"[llm] ERROR on ({src}→{tgt}): {e}", file=sys.stderr)
                out = ""
            elapsed = time.time() - t0
            # The prompt instructs the model to put the decimal on the
            # FIRST line — parse that. Fall back to "last parseable float in
            # [0,1]" so a reasoning model that adds the number at the end
            # still works.
            sev = 0.2
            import re
            first = (out.split("\n", 1)[0] or "").strip()
            m = re.match(r"^(-?\d+(?:\.\d+)?)\s*$", first)
            if m:
                try:
                    v = float(m.group(1))
                    if 0.0 <= v <= 1.0:
                        sev = v
                except ValueError:
                    pass
            if sev == 0.2:
                for m in re.finditer(r"(?<![A-Za-z_])(-?\d+(?:\.\d+)?)", out):
                    try:
                        v = float(m.group(1))
                    except ValueError:
                        continue
                    if 0.0 <= v <= 1.0:
                        sev = v  # keep overwriting so we end on the last match
            fh.write(json.dumps({
                "task": task_name, "voter": src, "target": tgt, "reason": reason,
                "raw_response": out, "parsed_severity": sev,
                "elapsed_sec": round(elapsed, 2),
                "model": backend.model, "ts": time.time(),
            }) + "\n")
            print(f"[rate] {src:11s} → {tgt:11s}  sev={sev:.2f}  ({elapsed:.1f}s)")
            rated.append(FakeCritique(src, tgt, sev))

    # --- 5. Attach the LLM-rated critiques and project into RunTrace ------
    # For this smoke test we attach the *same* critiques to both rounds.
    consensus.rounds[0].critiques = rated
    consensus.rounds[1].critiques = rated

    # Instrumentation expects per-proposal .agent, .confidence and
    # per-critique .from_agent, .on_agent, .severity — our Fake* fulfil these.
    run_trace = run_trace_from_consensus(consensus, task_id=task_name, backbone="scGPT")
    metrics = run_metrics(run_trace)

    # --- 6. Persist a final report ----------------------------------------
    report = {
        "task": task_name,
        "dataset": "Adamson2016_pilot",
        "n_real_perturbations": len(qc.perturbation_names),
        "sample_reasons_rated": len(sample_reasons),
        "metrics": {
            "tdi": round(metrics.tdi, 3),
            "delta_ace": round(metrics.delta_ace, 3),
            "delta_mean_confidence": round(metrics.delta_mean_confidence, 3),
            "winner_flip_rate": round(metrics.winner_flip_rate, 3),
            "final_consensus_score": round(metrics.final_consensus_score, 3),
            "n_rounds": len(metrics.per_round),
        },
        "model": backend.model,
    }
    (artifacts_dir / "last_run.json").write_text(json.dumps(report, indent=2))
    print("\n=== Live run summary ===")
    print(json.dumps(report, indent=2))
    print(f"\n[ok] artifacts in {artifacts_dir}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(PROJECT_ROOT / "configs" / "live.yaml"))
    return run(ap.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
