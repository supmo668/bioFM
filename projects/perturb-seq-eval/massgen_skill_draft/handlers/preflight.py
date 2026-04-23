"""Preflight handler — called on ``on_session_start``.

Reads the round-0 coordination snapshot, projects it to a ``RoundTrace``,
derives the probe signature, and queries the Bayesian recommender. Writes
a ``recommendation.json`` artifact.

MassGen integration note: the actual ``run`` signature will be determined by
the skill host in MassGen; for now we use a simple dict-in / dict-out shape
compatible with massgen_adapter.preflight_skill.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def run(payload: dict[str, Any]) -> dict[str, Any]:
    from perturb_eval.massgen_adapter import preflight_skill

    result = preflight_skill(payload)
    out = Path(payload.get("output_dir", ".")) / "recommendation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    return {"recommendation_path": str(out), **result}
