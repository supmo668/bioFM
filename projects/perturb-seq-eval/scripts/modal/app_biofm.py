"""Modal app for BioFM-grounded live-trace collection on Adamson.

Completes the user's expanded MC3b requirement: CellForge agents must
have access to real BioFMs pulled from HuggingFace so the rationales +
validator outputs are grounded in pretrained biological models, not in
rule-based canned strings. The resulting round-0 trace is then rated by
an OpenRouter LLM into a 4-dim probe signature per Adamson
perturbation.

Layout
------
    biofm_cache_volume   persistent volume for HF weights (BioGPT + Geneformer)
    cache_biofms()       one-shot function that warms the weights cache
    collect_probes()     runs CellForge orchestrator + LLM rating per
                         Adamson task, using BioFM-backed tools, and
                         writes /data/real_probes/adamson_probes_biofm.json
    entrypoint           dispatcher — `cache | collect`

Deployment
----------
    cd projects/perturb-seq-eval
    modal deploy scripts/modal/app_biofm.py
    modal run scripts/modal/app_biofm.py::entrypoint --step cache
    modal run scripts/modal/app_biofm.py::entrypoint --step collect

Budget estimate: BioGPT (347 MB) + Geneformer (small) cached once.
Inference per task ≈ 25 LLM calls + a handful of transformer forwards.
7 tasks. Should complete in < 15 min wall clock on a T4/A10 under $2.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import modal

try:
    PROJECT_DIR_HOST = Path(__file__).resolve().parents[2]
except IndexError:
    PROJECT_DIR_HOST = Path(__file__).resolve().parent
# v0.5.0: cellforge-agents now lives under libs/ at the repo root.
# Fall back to legacy projects/ layout if libs/ isn't present.
try:
    REPO_ROOT_HOST = Path(__file__).resolve().parents[3]
    CELLFORGE_DIR_HOST = REPO_ROOT_HOST / "libs" / "cellforge-agents"
    if not CELLFORGE_DIR_HOST.exists():
        CELLFORGE_DIR_HOST = PROJECT_DIR_HOST.parent / "cellforge-agents"
except Exception:  # noqa: BLE001
    CELLFORGE_DIR_HOST = PROJECT_DIR_HOST.parent / "cellforge-agents"


image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "build-essential")
    .pip_install(
        "numpy>=1.26",
        "typer>=0.12",
        "pandas>=2.2",
        "pyarrow>=16",
        "scipy>=1.11",
        "h5py>=3.10",
        "scikit-learn>=1.3",
        "torch>=2.2",
        "transformers>=4.42",
        "huggingface_hub>=0.24",
        "sentencepiece>=0.2",  # BioGPT tokenizer
        "sacremoses>=0.1",     # BioGPT tokenizer (Moses)
        "accelerate>=0.30",    # device_map="auto"
    )
    # Exclude transient directories that may change during build.
    .add_local_dir(
        str(PROJECT_DIR_HOST), remote_path="/app", copy=True,
        ignore=["artifacts/**", ".venv/**", ".pytest_cache/**", ".ruff_cache/**",
                "**/__pycache__/**", ".publish_work/**"],
    )
    .add_local_dir(
        str(CELLFORGE_DIR_HOST),
        remote_path="/app_cellforge", copy=True,
        ignore=["**/__pycache__/**", ".pytest_cache/**", ".ruff_cache/**"],
    )
    .workdir("/app")
    .run_commands(
        "pip install -e . && pip install -e /app_cellforge",
    )
)


app = modal.App("perturb-eval-biofm")
DATA_VOL = modal.Volume.from_name("perturb-eval-data", create_if_missing=True)
BIOFM_VOL = modal.Volume.from_name("biofm-cache", create_if_missing=True)

MOUNTS = {"/data": DATA_VOL, "/biofm_cache": BIOFM_VOL}


def _inject_openrouter_env() -> dict:
    """Surface the .env-provided OpenRouter settings into the Modal env."""
    return {
        "OPENROUTER_API_KEY": os.environ.get("OPENROUTER_API_KEY", ""),
        "OPENROUTER_MODEL": os.environ.get(
            "OPENROUTER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free"
        ),
        "OPENROUTER_BASE_URL": os.environ.get(
            "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
        ),
        "OPENROUTER_REFERER": os.environ.get(
            "OPENROUTER_REFERER", "https://github.com/supmo668/bioFM"
        ),
        "OPENROUTER_APP_TITLE": "perturb-seq-eval",
        "HF_CACHE_DIR": "/biofm_cache",
        "TRANSFORMERS_CACHE": "/biofm_cache",
        "HF_HOME": "/biofm_cache",
    }


# ---------------------------------------------------------------------------
# Cache warming — one-shot
# ---------------------------------------------------------------------------


@app.function(
    image=image, cpu=2.0, memory=8192, timeout=1800, volumes=MOUNTS,
    secrets=[modal.Secret.from_dict(_inject_openrouter_env())],
)
def cache_biofms() -> dict:
    """Pull BioGPT + Geneformer into the shared volume.

    Called once; subsequent ``collect_probes`` invocations reuse the
    cached weights.
    """
    from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer

    Path("/biofm_cache").mkdir(parents=True, exist_ok=True)
    results: dict[str, dict] = {}

    # ---- BioGPT (causal LM) ----
    t0 = time.time()
    try:
        AutoTokenizer.from_pretrained("microsoft/BioGPT", cache_dir="/biofm_cache")
        AutoModelForCausalLM.from_pretrained("microsoft/BioGPT", cache_dir="/biofm_cache")
        results["biogpt"] = {"status": "cached", "wall_s": round(time.time() - t0, 1)}
    except Exception as e:  # noqa: BLE001
        results["biogpt"] = {"status": "error", "error": str(e)}

    # ---- Geneformer (encoder) ----
    t0 = time.time()
    try:
        AutoTokenizer.from_pretrained(
            "ctheodoris/Geneformer", cache_dir="/biofm_cache", trust_remote_code=True,
        )
        AutoModel.from_pretrained(
            "ctheodoris/Geneformer", cache_dir="/biofm_cache", trust_remote_code=True,
        )
        results["geneformer"] = {"status": "cached", "wall_s": round(time.time() - t0, 1)}
    except Exception as e:  # noqa: BLE001
        results["geneformer"] = {"status": "error", "error": str(e)}

    BIOFM_VOL.commit()
    return results


# ---------------------------------------------------------------------------
# Collection — BioFM-backed agents + LLM rating
# ---------------------------------------------------------------------------


@app.function(
    image=image, gpu="T4", cpu=4.0, memory=16384, timeout=3600, volumes=MOUNTS,
    secrets=[modal.Secret.from_dict(_inject_openrouter_env())],
)
def collect_probes() -> dict:
    """Run orchestrator with BioFM-backed tools; rate with OpenRouter; save probes."""
    import numpy as np

    from perturb_eval.backends.openrouter import OpenRouterBackend
    from perturb_eval.experiments.common import probe_signature_from_trace
    from perturb_eval.experiments.e2_adamson import load_adamson_matrix
    from perturb_eval.types import RoundTrace, RunTrace

    # --- BioFM tools (imported here so the cache warming can run without torch)
    from perturb_eval.biofm_tools.biogpt_literature import BioGPTMechanismTool
    from perturb_eval.biofm_tools.geneformer_validator import GeneformerValidatorTool

    # --- CellForge
    from cellforge.agents.architect import ArchitectAgent
    from cellforge.agents.data_curator import DataCuratorAgent
    from cellforge.agents.literature import LiteratureAgent
    from cellforge.agents.trainer import TrainerAgent
    from cellforge.agents.validator import ValidatorAgent
    from cellforge.orchestrator import Orchestrator
    from cellforge.problem import Modality, Problem

    out_dir = Path("/data/real_probes")
    out_dir.mkdir(parents=True, exist_ok=True)
    trace_log = out_dir / "adamson_traces_biofm.jsonl"
    if trace_log.exists():
        trace_log.unlink()

    # --- Build BioFM tools (shared across all perturbations for speed)
    biogpt_tool = BioGPTMechanismTool()
    biogpt_tool._ensure_loaded()  # type: ignore[attr-defined]
    geneformer_tool = GeneformerValidatorTool()
    geneformer_tool._ensure_loaded()  # type: ignore[attr-defined]

    # --- Load Adamson perturbations
    ds = load_adamson_matrix("/data/adamson/Adamson2016_pilot.h5ad", n_top_hvg=500, max_cells_per_pert=50)
    perts = list(ds["perturbations"])
    print(f"BioFM probe collection for {len(perts)} perturbations: {perts}")

    # --- LLM rater
    backend = OpenRouterBackend.from_env()
    print(f"Rater model: {backend.model}")

    import re
    final_re = re.compile(r"FINAL\s*=\s*([01](?:\.[0-9]+)?)")

    def rate(sys_p: str, user_p: str, fallback: float) -> tuple[float, str]:
        try:
            raw = backend.complete(system=sys_p, user=user_p, max_tokens=512, temperature=0.0)
        except Exception as e:  # noqa: BLE001
            return fallback, f"llm_err: {e}"
        m = final_re.search(raw)
        if m:
            return max(0.0, min(1.0, float(m.group(1)))), raw
        for tok in raw.split():
            try:
                v = float(tok.strip(".,;:"))
                if 0.0 <= v <= 1.0:
                    return v, raw
            except ValueError:
                continue
        return fallback, raw

    conf_sys = (
        "You rate how confident the author of a proposal should be in their "
        "proposal, based on the proposal's rationale alone. "
        "0.0 = no information. 0.5 = reasonable but unverified. "
        "1.0 = strongly evidenced. End with: FINAL=<float in [0,1]>"
    )
    sev_sys = (
        "You rate how severe a critique is: how much it damages the target "
        "proposal's chance of being accepted. "
        "0.0 = no damage. 0.5 = real concern. 1.0 = fatal flaw. "
        "End with: FINAL=<float in [0,1]>"
    )

    probes: dict[str, list[float]] = {}
    raw_rounds: dict[str, dict] = {}

    for i, pert in enumerate(perts, 1):
        print(f"[{i}/{len(perts)}] {pert}")
        # Build the agents with BioFM-backed tools on each run so the
        # LiteratureAgent and ValidatorAgent consult real models.
        lit = LiteratureAgent(tool=biogpt_tool)  # type: ignore[arg-type]
        val = ValidatorAgent()                    # Validator uses its own tool signature
        # Monkey-patch the validator to consult Geneformer for DEG agreement.
        # CellForge's ValidatorAgent has a ``tool`` attribute; we inject ours.
        if hasattr(val, "tool"):
            val.tool = geneformer_tool  # type: ignore[attr-defined]

        orch = Orchestrator(
            agents=[
                DataCuratorAgent(),
                lit,
                ArchitectAgent(),
                TrainerAgent(),
                val,
            ],
            max_rounds=1,
            consensus_threshold=0.99,
        )
        t_pert = time.time()
        result = orch.run(Problem(
            perturbation=f"{pert} knockdown",
            modality=Modality.SCRNA,
            cell_type_hint="K562",
        ))
        round0 = result.rounds[0]
        raw_rounds[pert] = {
            "proposals": [
                {"agent": p.agent, "rationale": p.rationale, "rule_confidence": float(p.confidence)}
                for p in round0.proposals
            ],
            "critiques": [
                {"from": c.from_agent, "on": c.on_agent, "comment": c.comment, "rule_severity": float(c.severity)}
                for c in round0.critiques
            ],
        }

        agent_order = [p.agent for p in round0.proposals]
        agent_idx = {n: i for i, n in enumerate(agent_order)}
        n = len(agent_order)

        # Rate confidences
        confs: list[float] = []
        with trace_log.open("a") as logf:
            for p in round0.proposals:
                v, raw = rate(
                    conf_sys,
                    f"Perturbation: {pert} knockdown in K562\nAgent: {p.agent}\nRationale:\n{p.rationale}",
                    fallback=float(p.confidence),
                )
                confs.append(v)
                logf.write(json.dumps({
                    "perturbation": pert, "kind": "confidence", "agent": p.agent,
                    "rule_value": float(p.confidence), "llm_value": v,
                    "raw_tail": raw[-200:],
                }) + "\n")
            # Severity matrix
            sev = [[0.0] * n for _ in range(n)]
            for c in round0.critiques:
                i_, j_ = agent_idx[c.from_agent], agent_idx[c.on_agent]
                v, raw = rate(
                    sev_sys,
                    f"Perturbation: {pert}\nCritic: {c.from_agent}\nTarget: {c.on_agent}\nComment:\n{c.comment}",
                    fallback=float(c.severity),
                )
                sev[i_][j_] = v
                logf.write(json.dumps({
                    "perturbation": pert, "kind": "severity", "from": c.from_agent,
                    "on": c.on_agent, "rule_value": float(c.severity), "llm_value": v,
                    "raw_tail": raw[-200:],
                }) + "\n")

        off_diag = tuple(tuple(sev[i_][j_] for j_ in range(n) if j_ != i_) for i_ in range(n))
        rt = RoundTrace(
            round_index=0,
            agent_names=tuple(agent_order),
            confidences=tuple(confs),
            critique_severities=off_diag,
            winner_index=0,
            consensus_score=float(np.mean(confs)),
        )
        run = RunTrace(task_id=pert, rounds=(rt,), converged=False, backbone="live-biofm")
        probe = [float(x) for x in probe_signature_from_trace(run)]
        probes[pert] = probe
        print(f"  probe = [{probe[0]:.3f}, {probe[1]:.3f}, {probe[2]:.3f}, {probe[3]:.3f}]"
              f"  wall={time.time() - t_pert:.1f}s")

    (out_dir / "adamson_probes_biofm.json").write_text(json.dumps(probes, indent=2))
    (out_dir / "adamson_raw_rounds_biofm.json").write_text(json.dumps(raw_rounds, indent=2))
    DATA_VOL.commit()
    return {
        "n_perts": len(perts),
        "probes": probes,
        "probes_path": str(out_dir / "adamson_probes_biofm.json"),
    }


@app.local_entrypoint()
def entrypoint(step: str = "collect") -> None:
    if step == "cache":
        out = cache_biofms.remote()
    elif step == "collect":
        out = collect_probes.remote()
    elif step == "all":
        print(json.dumps(cache_biofms.remote(), indent=2))
        out = collect_probes.remote()
    else:
        raise SystemExit(f"unknown step {step!r}")
    print(json.dumps(out, indent=2, default=str))
