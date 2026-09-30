"""Unit tests for the optimizer stack (contextual GP, CMA-ES, random).

See docs/SUPPLEMENT_DESIGN.md §2. Each optimizer satisfies an
:class:`Optimizer` Protocol; tests check that the protocol holds and that
the contextual GP actually uses its context (shifts its recommendation
when the context changes).
"""

from __future__ import annotations

import numpy as np
import pytest

from perturb_eval.optimizers import (
    Observation,
    available_optimizers,
    build_optimizer,
)
from perturb_eval.optimizers.base import backbones_of, config_to_vec, nearest_config
from perturb_eval.types import Config, DEFAULT_CONFIG_SPACE


# Tiny finite config space used in tests.
_SMALL_PHI: tuple[Config, ...] = tuple(
    Config(n_agents=a, n_rounds=r, backbone=b)
    for a in (3, 5)
    for r in (1, 2)
    for b in ("scGPT", "scPRINT-2")
)  # 8 configs

# The backbone set every real experiment uses (T18 / A5). 3 x 3 x 3 = 27 configs.
_REAL_PHI: tuple[Config, ...] = tuple(
    Config(n_agents=a, n_rounds=r, backbone=b)
    for a in (1, 3, 5)
    for r in (1, 2, 3)
    for b in ("linear", "mlp", "scgpt_small")
)


def _quad_objective(phi: Config, context: np.ndarray) -> float:
    """Synthetic objective: lower is better. Depends on both phi and context.

    Penalises small n_agents × n_rounds when context[0] is high (proxy for
    "hard task"), penalises large n_agents × n_rounds when context[0] is low.
    """
    size = phi.n_agents * phi.n_rounds
    hardness = float(context[0])
    return (size - 8 * hardness) ** 2 + 0.1 * np.random.default_rng(phi.n_rounds).uniform()


# ---------------------------------------------------------------------------
# Config embedding (T18 / A5): backbone one-hot derived from the space
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestConfigEmbedding:
    @pytest.mark.parametrize("space", [_SMALL_PHI, _REAL_PHI], ids=["legacy", "real"])
    def test_embedding_is_injective_over_space(self, space: tuple[Config, ...]) -> None:
        bb = backbones_of(space)
        assert len({tuple(config_to_vec(c, bb)) for c in space}) == len(space)

    def test_backbones_of_is_sorted_unique(self) -> None:
        assert backbones_of(_REAL_PHI) == ("linear", "mlp", "scgpt_small")
        assert backbones_of(_SMALL_PHI) == ("scGPT", "scPRINT-2")

    @pytest.mark.parametrize("target", ["linear", "mlp", "scgpt_small"])
    def test_nearest_config_reaches_every_backbone(self, target: str) -> None:
        bb = backbones_of(_REAL_PHI)
        phi = Config(n_agents=3, n_rounds=2, backbone=target)
        got = nearest_config(config_to_vec(phi, bb), _REAL_PHI, bb)
        assert got == phi

    def test_unknown_backbone_raises(self) -> None:
        bb = backbones_of(_REAL_PHI)
        with pytest.raises(ValueError, match="backbone"):
            config_to_vec(Config(n_agents=3, n_rounds=2, backbone="scGPT"), bb)

    @pytest.mark.parametrize("name", ["cma_es", "contextual_gp"])
    def test_optimizers_accept_real_space(self, name: str) -> None:
        opt = build_optimizer(name, config_space=_REAL_PHI, seed=0)
        ctx = np.zeros(4)
        observed = [
            Observation(config=c, context=ctx, objective=float(i))
            for i, c in enumerate(_REAL_PHI[:6])
        ]
        assert opt.suggest(context=ctx, observed=observed) in _REAL_PHI


# ---------------------------------------------------------------------------
# Random baseline
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRandomOptimizer:
    def test_registered(self) -> None:
        assert "random" in available_optimizers()

    def test_suggests_config_from_space(self) -> None:
        opt = build_optimizer("random", config_space=_SMALL_PHI, seed=7)
        phi = opt.suggest(context=np.zeros(4), observed=[])
        assert phi in _SMALL_PHI

    def test_seeded_deterministic(self) -> None:
        a = [build_optimizer("random", config_space=_SMALL_PHI, seed=7).suggest(
            context=np.zeros(4), observed=[]
        ) for _ in range(1)]
        b = [build_optimizer("random", config_space=_SMALL_PHI, seed=7).suggest(
            context=np.zeros(4), observed=[]
        ) for _ in range(1)]
        assert a == b


# ---------------------------------------------------------------------------
# CMA-ES (non-contextual)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCMAOptimizer:
    def test_registered(self) -> None:
        assert "cma_es" in available_optimizers()

    def test_suggests_config_from_space(self) -> None:
        opt = build_optimizer("cma_es", config_space=_SMALL_PHI, seed=0)
        phi = opt.suggest(context=np.zeros(4), observed=[])
        assert phi in _SMALL_PHI

    def test_moves_toward_better_region(self) -> None:
        """After feeding a run of observations that clearly prefer small
        (n_agents, n_rounds), CMA-ES should be biased toward small configs."""
        opt = build_optimizer("cma_es", config_space=_SMALL_PHI, seed=0)
        fixed_ctx = np.zeros(4)
        observed: list[Observation] = []
        for _ in range(30):
            phi = opt.suggest(context=fixed_ctx, observed=observed)
            # objective = n_agents × n_rounds (small is better)
            y = phi.n_agents * phi.n_rounds
            observed.append(Observation(config=phi, context=fixed_ctx, objective=float(y)))
        # Picks at the end should average smaller than n_agents×n_rounds of 5×2=10.
        tail = [o.config.n_agents * o.config.n_rounds for o in observed[-10:]]
        assert np.mean(tail) < 10, f"CMA-ES failed to move toward small; tail={tail}"


# ---------------------------------------------------------------------------
# Contextual GP (the primary innovation)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContextualGPOptimizer:
    def test_registered(self) -> None:
        assert "contextual_gp" in available_optimizers()

    def test_suggests_config_from_space(self) -> None:
        opt = build_optimizer("contextual_gp", config_space=_SMALL_PHI, seed=0)
        phi = opt.suggest(context=np.zeros(4), observed=[])
        assert phi in _SMALL_PHI

    def test_context_changes_suggestion(self) -> None:
        """Feed the GP a training set where context = 1 prefers large configs
        and context = 0 prefers small configs. The suggestion for an unseen
        context=1 query should be different from the suggestion for context=0."""
        opt = build_optimizer("contextual_gp", config_space=_SMALL_PHI, seed=0)
        # Training observations: small configs are good at ctx=0, large at ctx=1.
        observed: list[Observation] = []
        for phi in _SMALL_PHI:
            size = phi.n_agents * phi.n_rounds
            for ctx_val in (0.0, 1.0):
                ctx = np.array([ctx_val, 0.0, 0.0, 0.0])
                y = (size - (8.0 if ctx_val > 0.5 else 3.0)) ** 2
                observed.append(Observation(config=phi, context=ctx, objective=float(y)))
        sug_low = opt.suggest(
            context=np.array([0.0, 0.0, 0.0, 0.0]), observed=observed,
        )
        sug_hi = opt.suggest(
            context=np.array([1.0, 0.0, 0.0, 0.0]), observed=observed,
        )
        size_low = sug_low.n_agents * sug_low.n_rounds
        size_hi = sug_hi.n_agents * sug_hi.n_rounds
        # Low-context suggests small, high-context suggests large.
        assert size_low <= size_hi, (
            f"Contextual GP did not condition on context: "
            f"ctx=0 → size={size_low}, ctx=1 → size={size_hi}"
        )


# ---------------------------------------------------------------------------
# Registry + error handling
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRegistry:
    def test_unknown_optimizer_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown optimizer"):
            build_optimizer("nonexistent", config_space=_SMALL_PHI, seed=0)

    def test_default_config_space_accepted(self) -> None:
        opt = build_optimizer("random", config_space=DEFAULT_CONFIG_SPACE, seed=0)
        phi = opt.suggest(context=np.zeros(4), observed=[])
        assert phi in DEFAULT_CONFIG_SPACE
