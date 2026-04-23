"""End-to-end demo — everything wired up with synthetic data.

Run:  python examples/end_to_end.py
"""

from __future__ import annotations

from perturb_eval.bayesian import BayesianRecommender
from perturb_eval.calibration import fit_tdi_coefficients
from perturb_eval.metrics import run_metrics, tdi
from perturb_eval.probe import signature_from_round
from perturb_eval.types import Config, RoundTrace, RunTrace


def _round(
    round_index: int,
    confidences: tuple[float, ...],
    severities: tuple[tuple[float, ...], ...],
    winner: int,
    cs: float,
) -> RoundTrace:
    return RoundTrace(
        round_index=round_index,
        agent_names=("DataCurator", "Literature", "Architect", "Trainer", "Validator"),
        confidences=confidences,
        critique_severities=severities,
        winner_index=winner,
        consensus_score=cs,
    )


def _build_easy_trace(task_id: str) -> RunTrace:
    rounds = (
        _round(0, (0.5, 0.6, 0.5, 0.55, 0.75), ((0.15, 0.15, 0.15, 0.15),) * 5, 4, 0.55),
        _round(1, (0.6, 0.7, 0.65, 0.75, 0.92), ((0.1, 0.1, 0.1, 0.1),) * 5, 4, 0.82),
    )
    return RunTrace(task_id=task_id, rounds=rounds, converged=True, backbone="scGPT")


def _build_hard_trace(task_id: str) -> RunTrace:
    rounds = (
        _round(0, (0.5, 0.55, 0.5, 0.52, 0.5), ((0.7, 0.8, 0.6, 0.9),) * 5, 1, 0.1),
        _round(1, (0.52, 0.5, 0.55, 0.5, 0.52), ((0.65, 0.75, 0.6, 0.85),) * 5, 2, 0.12),
        _round(2, (0.5, 0.53, 0.51, 0.54, 0.5), ((0.6, 0.7, 0.55, 0.8),) * 5, 3, 0.15),
    )
    return RunTrace(task_id=task_id, rounds=rounds, converged=False, backbone="scGPT")


def main() -> None:
    easy = _build_easy_trace("GSK3B_KO")
    hard = _build_hard_trace("SETD2_SMARCA4_dual_KO")

    print("=== Per-run metrics ===")
    for trace in (easy, hard):
        m = run_metrics(trace)
        print(
            f"  {trace.task_id:30s}  TDI={m.tdi:.3f}  ΔACE={m.delta_ace:+.3f}  "
            f"ΔC={m.delta_mean_confidence:+.3f}  WFR={m.winner_flip_rate:.2f}  "
            f"consensus={m.final_consensus_score:.2f}"
        )

    print("\n=== TDI coefficients fitted on a tiny labelled set ===")
    labelled = [(easy, 0.0), (hard, 1.0)] * 5
    coeffs = fit_tdi_coefficients(labelled)
    for k, v in coeffs.as_dict().items():
        print(f"  {k}: {v:.3f}")

    refit = tdi(tuple(run_metrics(easy).per_round), coeffs=coeffs.as_dict())
    print(f"  TDI(easy) with fitted coeffs = {refit:.3f}")

    print("\n=== Preflight → Bayesian recommendation ===")
    easy_probe = signature_from_round(easy.rounds[0])
    hard_probe = signature_from_round(hard.rounds[0])
    # Build a tiny calibration set mapping probe → observed optimal config.
    small = Config(n_agents=3, n_rounds=1, backbone="scGPT")
    large = Config(n_agents=5, n_rounds=3, backbone="scGPT")
    calib = [(easy_probe, small)] * 8 + [(hard_probe, large)] * 8
    rec = BayesianRecommender().fit(calib)

    for label, probe in (("easy probe", easy_probe), ("hard probe", hard_probe)):
        r = rec.recommend(probe)
        print(
            f"  {label:14s}  -> n_agents={r.config.n_agents} n_rounds={r.config.n_rounds} "
            f"backbone={r.config.backbone}  log_post={r.log_posterior:.2f}"
        )


if __name__ == "__main__":
    main()
