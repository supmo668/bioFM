"""Evaluate handler — called on ``on_session_end``.

Reads the full coordination snapshot, projects every round to a
``RoundTrace``, rolls them up into a ``RunTrace`` + ``RunMetrics``, and
writes a ``run_metrics.json`` artifact.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def run(payload: dict[str, Any]) -> dict[str, Any]:
    from perturb_eval.massgen_adapter import evaluate_skill

    result = evaluate_skill(payload)
    out = Path(payload.get("output_dir", ".")) / "run_metrics.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    return {"run_metrics_path": str(out), **result}
