"""Closes MC3b — collect real round-0 agent traces on Adamson perturbations.

Architecture:
    1. For each of 7 targeted-knockdown perturbations in Adamson 2016 pilot,
       construct a ``cellforge.problem.Problem`` and run the 5-agent
       CellForge orchestrator with ``max_rounds=1``. This produces
       5 structured proposals + 20 pairwise critiques with free-text
       rationales and comments.
    2. Use OpenRouter Nemotron free-tier to rate each proposal's confidence
       and each critique's severity from its free-text field. The rater
       prompt forces a ``FINAL=<float>`` sentinel that works through the
       reasoning-model output format.
    3. Build a ``RoundTrace`` from the LLM-rated numerics and project to
       the 4-dim probe signature via ``probe_signature_from_trace``.
    4. Persist per-perturbation probes + raw trace records for audit.

Output:
    artifacts/real_probes/adamson_probes.json          {perturbation: [a, b, c, d]}
    artifacts/real_probes/adamson_traces.jsonl         one record per LLM call (for audit)

Run::

    python scripts/local/collect_real_probes.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

# Ensure repo-local imports work even if the package isn't pip-installed.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT.parent / "cellforge-agents" / "src"))

from perturb_eval.backends.openrouter import OpenRouterBackend  # noqa: E402
from perturb_eval.experiments.common import probe_signature_from_trace  # noqa: E402
from perturb_eval.experiments.e2_adamson import load_adamson_matrix  # noqa: E402
from perturb_eval.types import RoundTrace, RunTrace  # noqa: E402


ADAMSON_H5AD = ROOT / "data" / "Adamson2016_pilot.h5ad"
OUT_DIR = ROOT / "artifacts" / "real_probes"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# .env auto-loader so this runs standalone without `source .env`.
# ---------------------------------------------------------------------------


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_dotenv(ROOT.parent.parent / ".env")  # repo-root .env


# ---------------------------------------------------------------------------
# LLM rater
# ---------------------------------------------------------------------------


_CONFIDENCE_SYSTEM = (
    "You rate how confident the author of a proposal should be in their "
    "proposal, based on the proposal's rationale alone. "
    "0.0 = no information / pure speculation. "
    "0.5 = reasonable but unverified. "
    "1.0 = strongly evidenced, unambiguous. "
    "After any reasoning, end your reply with a line: FINAL=<float in [0,1]>"
)

_SEVERITY_SYSTEM = (
    "You rate how severe a critique is: how much it damages the target "
    "proposal's chance of being accepted. "
    "0.0 = no damage, essentially approval. "
    "0.5 = a real concern, not a blocker. "
    "1.0 = fatal flaw identified. "
    "After any reasoning, end your reply with a line: FINAL=<float in [0,1]>"
)


_FINAL_RE = re.compile(r"FINAL\s*=\s*([01](?:\.[0-9]+)?)")


def rate_float(backend: OpenRouterBackend, system: str, user: str, fallback: float) -> tuple[float, str]:
    """Call the LLM, parse the FINAL=<float> sentinel, fall back on parse error."""
    try:
        raw = backend.complete(system=system, user=user, max_tokens=512, temperature=0.0)
    except Exception as e:  # noqa: BLE001
        return fallback, f"error: {e}"
    m = _FINAL_RE.search(raw)
    if not m:
        # Try plain-float prefix as a backup.
        for tok in raw.split():
            try:
                v = float(tok.strip(".,;:"))
                if 0.0 <= v <= 1.0:
                    return v, raw
            except ValueError:
                continue
        return fallback, raw
    return max(0.0, min(1.0, float(m.group(1)))), raw


# ---------------------------------------------------------------------------
# CellForge orchestrator runner
# ---------------------------------------------------------------------------


def build_agents():
    """Instantiate the 5 CellForge agents with their default rule-based tools."""
    from cellforge.agents.architect import ArchitectAgent  # noqa: PLC0415
    from cellforge.agents.data_curator import DataCuratorAgent  # noqa: PLC0415
    from cellforge.agents.literature import LiteratureAgent  # noqa: PLC0415
    from cellforge.agents.trainer import TrainerAgent  # noqa: PLC0415
    from cellforge.agents.validator import ValidatorAgent  # noqa: PLC0415

    return [
        DataCuratorAgent(),
        LiteratureAgent(),
        ArchitectAgent(),
        TrainerAgent(),
        ValidatorAgent(),
    ]


def run_round_zero(perturbation: str) -> dict:
    """Run one orchestrator round (propose + critique, no voting refinement)."""
    from cellforge.orchestrator import Orchestrator  # noqa: PLC0415
    from cellforge.problem import Modality, Problem  # noqa: PLC0415

    orch = Orchestrator(agents=build_agents(), max_rounds=1, consensus_threshold=0.99)
    result = orch.run(
        Problem(
            perturbation=f"{perturbation} knockdown",
            modality=Modality.SCRNA,
            cell_type_hint="K562",
        )
    )
    round0 = result.rounds[0]
    proposals = [
        {
            "agent": p.agent,
            "rationale": p.rationale,
            "rule_confidence": float(p.confidence),
        }
        for p in round0.proposals
    ]
    critiques = [
        {
            "from_agent": c.from_agent,
            "on_agent": c.on_agent,
            "comment": c.comment,
            "rule_severity": float(c.severity),
        }
        for c in round0.critiques
    ]
    return {"proposals": proposals, "critiques": critiques}


# ---------------------------------------------------------------------------
# Probe assembly
# ---------------------------------------------------------------------------


def assemble_probe(
    perturbation: str,
    round0: dict,
    backend: OpenRouterBackend,
    trace_log: Path,
) -> tuple[list[float], dict]:
    """Rate each proposal + critique via LLM; build a RoundTrace; project to probe."""
    agent_order = [p["agent"] for p in round0["proposals"]]
    agent_idx = {name: i for i, name in enumerate(agent_order)}

    # Rate proposal confidences
    confidences: list[float] = []
    with trace_log.open("a") as logf:
        for p in round0["proposals"]:
            user = (
                f"Perturbation: {perturbation} knockdown in K562 cells\n"
                f"Agent: {p['agent']}\n"
                f"Rationale:\n{p['rationale']}"
            )
            v, raw = rate_float(backend, _CONFIDENCE_SYSTEM, user, fallback=p["rule_confidence"])
            confidences.append(v)
            logf.write(json.dumps({
                "perturbation": perturbation,
                "kind": "confidence",
                "agent": p["agent"],
                "rule_value": p["rule_confidence"],
                "llm_value": v,
                "raw_tail": raw[-200:],
            }) + "\n")

        # Build a NxN severity matrix (diag=0); fill off-diagonals from LLM
        n = len(agent_order)
        severity_matrix: list[list[float]] = [[0.0] * n for _ in range(n)]
        for c in round0["critiques"]:
            i = agent_idx[c["from_agent"]]
            j = agent_idx[c["on_agent"]]
            user = (
                f"Perturbation: {perturbation} knockdown in K562 cells\n"
                f"Critic: {c['from_agent']}\n"
                f"Target: {c['on_agent']}\n"
                f"Comment:\n{c['comment']}"
            )
            v, raw = rate_float(backend, _SEVERITY_SYSTEM, user, fallback=c["rule_severity"])
            severity_matrix[i][j] = v
            logf.write(json.dumps({
                "perturbation": perturbation,
                "kind": "severity",
                "from": c["from_agent"],
                "on": c["on_agent"],
                "rule_value": c["rule_severity"],
                "llm_value": v,
                "raw_tail": raw[-200:],
            }) + "\n")

    # Convert NxN with diag to Nx(N-1) off-diagonal rows.
    off_diag = tuple(
        tuple(severity_matrix[i][j] for j in range(n) if j != i)
        for i in range(n)
    )

    rt = RoundTrace(
        round_index=0,
        agent_names=tuple(agent_order),
        confidences=tuple(confidences),
        critique_severities=off_diag,
        winner_index=0,
        consensus_score=float(sum(confidences) / n),
    )
    run = RunTrace(task_id=perturbation, rounds=(rt,), converged=False, backbone="live")
    probe = probe_signature_from_trace(run)
    return [float(x) for x in probe], {
        "confidences": confidences,
        "severity_matrix": severity_matrix,
        "agent_order": agent_order,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main() -> int:
    if "OPENROUTER_API_KEY" not in os.environ:
        print("OPENROUTER_API_KEY missing — check .env at repo root.", file=sys.stderr)
        return 2

    ds = load_adamson_matrix(ADAMSON_H5AD, n_top_hvg=500, max_cells_per_pert=50)
    perturbations = list(ds["perturbations"])
    print(f"Adamson perturbations to probe: {perturbations}")

    backend = OpenRouterBackend.from_env()
    print(f"Using model: {backend.model}")

    trace_log = OUT_DIR / "adamson_traces.jsonl"
    if trace_log.exists():
        trace_log.unlink()

    probes: dict[str, list[float]] = {}
    raw_rounds: dict[str, dict] = {}
    audit: dict[str, dict] = {}
    t_total = time.perf_counter()
    for i, pert in enumerate(perturbations, 1):
        print(f"[{i}/{len(perturbations)}] {pert}")
        t0 = time.perf_counter()
        round0 = run_round_zero(pert)
        raw_rounds[pert] = round0
        probe, extras = assemble_probe(pert, round0, backend, trace_log)
        probes[pert] = probe
        audit[pert] = extras
        print(f"  probe = [{probe[0]:.3f}, {probe[1]:.3f}, {probe[2]:.3f}, {probe[3]:.3f}]"
              f"  wall={time.perf_counter() - t0:.1f}s")

    (OUT_DIR / "adamson_probes.json").write_text(json.dumps(probes, indent=2))
    (OUT_DIR / "adamson_raw_rounds.json").write_text(json.dumps(raw_rounds, indent=2))
    (OUT_DIR / "adamson_audit.json").write_text(json.dumps(audit, indent=2))
    print(f"\nWrote real probes for {len(probes)} perturbations to "
          f"{OUT_DIR / 'adamson_probes.json'} (total {time.perf_counter() - t_total:.1f}s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
