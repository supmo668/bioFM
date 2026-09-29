"""Relaunch fixes after the aborted v0.6.0 run (CTO #467; principal 2026-09-28: paid, cheapest JSON-capable tier).

1. The roster has NO :free endpoints (they died / rate-limit into fallbacks, and A2-1 makes a fallback fatal);
   every role names 3 preferred models that are in the pool; the pool spans >= 5 families.
2. A 429 / 5xx never becomes a fallback while a model is merely cooling: chat_json WAITS (bounded) for the
   earliest cooldown, then retries; it raises only when the wait budget is exhausted or nothing is cooling.
3. Preflight probes EVERY roster model with the Validator JSON schema, records a liveness table, refuses when
   any role has < 2 live preferred models, and FAILS when it probed fewer models than the roster lists.
4. The liveness table (id, probed_at, verdict) is recorded in provenance; app_v05 passes it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

from perturb_eval.llm import openrouter_client as oc
from perturb_eval.llm.openrouter_client import DEFAULT_POOL, LLMPool, ModelSpec, OpenRouterClient

ROLES = ("DataCurator", "Literature", "Architect", "Trainer", "Validator")


# ------------------------------------------------------------------ 1. roster
class TestRoster:
    def test_no_free_endpoints_three_prefs_per_role_five_families(self) -> None:
        ids = [m.model_id for m in DEFAULT_POOL.models]
        assert ids and not any(i.endswith(":free") for i in ids), ids
        assert len(set(ids)) == len(ids)
        for role in ROLES:
            prefs = DEFAULT_POOL.role_preferences[role]
            assert len(prefs) == 3 and len(set(prefs)) == 3
            assert set(prefs) <= set(ids), (role, prefs)
        assert len({m.family for m in DEFAULT_POOL.models}) >= 5


# ------------------------------------------------------- 2. bounded cooldown wait
class _Resp:
    def __init__(self, status: int, content: str | None) -> None:
        self.status_code = status
        self._content = content

    def json(self) -> dict:
        if self._content is None:
            raise ValueError("no body")
        return {"choices": [{"message": {"content": self._content}}]}


class _Session:
    """Scripted responses per model id, consumed in order; the last one repeats."""

    def __init__(self, script: dict[str, list[_Resp]]) -> None:
        self.script = {k: list(v) for k, v in script.items()}
        self.calls: list[str] = []

    def post(self, url, headers=None, json=None, timeout=None):  # noqa: ANN001
        mid = json["model"]
        self.calls.append(mid)
        q = self.script[mid]
        return q.pop(0) if len(q) > 1 else q[0]


def _two_model_pool() -> LLMPool:
    a = ModelSpec(model_id="x/a", family="fa", param_count_b=1, strengths=())
    b = ModelSpec(model_id="x/b", family="fb", param_count_b=1, strengths=())
    return LLMPool(models=(a, b), role_preferences={r: ("x/a", "x/b") for r in ROLES})


def _client(
    tmp_path: Path, session: _Session, **kw
) -> tuple[OpenRouterClient, list[float], list[float]]:
    clock = [1000.0]
    slept: list[float] = []

    def fake_sleep(s: float) -> None:
        slept.append(s)
        clock[0] += s

    c = OpenRouterClient(
        api_key="k",
        cache_dir=tmp_path,
        pool=_two_model_pool(),
        cooldown_sec=10.0,
        session=session,
        sleep=fake_sleep,
        clock=lambda: clock[0],
        **kw,
    )
    return c, slept, clock


class TestCooldownWait:
    def test_waits_for_cooldown_then_succeeds_instead_of_falling_back(self, tmp_path: Path) -> None:
        good = '{"confidence": 0.5, "dynamic_threshold_msd": 0.1}'
        sess = _Session(
            {
                "x/a": [_Resp(429, None), _Resp(200, good)],
                "x/b": [_Resp(429, None), _Resp(429, None)],
            }
        )
        c, slept, _ = _client(tmp_path, sess, max_wait_sec=60.0)
        res = c.chat_json(
            role="Validator", task_id="t", round_index=0, prompt="p", seed=0, dataset="d"
        )
        assert res.content["confidence"] == 0.5 and res.model_id == "x/a" and res.cache_hit is False
        assert slept and sum(slept) <= 60.0  # it waited for the cooldown rather than raising

    def test_raises_only_after_wait_budget_exhausted(self, tmp_path: Path) -> None:
        sess = _Session({"x/a": [_Resp(429, None)], "x/b": [_Resp(503, None)]})
        c, slept, _ = _client(tmp_path, sess, max_wait_sec=25.0)
        with pytest.raises(oc.OpenRouterError):
            c.chat_json(
                role="Validator", task_id="t", round_index=0, prompt="p", seed=0, dataset="d"
            )
        assert 20.0 <= sum(slept) <= 25.0 + 10.0

    def test_dead_models_do_not_wait(self, tmp_path: Path) -> None:
        sess = _Session({"x/a": [_Resp(404, None)], "x/b": [_Resp(404, None)]})
        c, slept, _ = _client(tmp_path, sess, max_wait_sec=60.0)
        with pytest.raises(oc.OpenRouterError, match="404"):
            c.chat_json(
                role="Validator", task_id="t", round_index=0, prompt="p", seed=0, dataset="d"
            )
        assert slept == []  # nothing is cooling: no point waiting

    def test_probe_model_reports_live_and_verdict(self, tmp_path: Path) -> None:
        good = '{"confidence": 0.5, "dynamic_threshold_msd": 0.1}'
        sess = _Session({"x/a": [_Resp(200, good)], "x/b": [_Resp(404, None)]})
        c, _, _ = _client(tmp_path, sess)
        live, verdict, parsed = c.probe_model("x/a", "p")
        assert live and parsed["confidence"] == 0.5
        live_b, verdict_b, parsed_b = c.probe_model("x/b", "p")
        assert not live_b and "404" in verdict_b and parsed_b is None


# ------------------------------------------------------------- 3. preflight
from tests.test_v05_preflight import _POOL, _liveness, _run  # noqa: E402


class TestPreflightProbesEveryRosterModel:
    def test_probing_fewer_models_than_the_roster_fails(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.v05_preflight import PreflightError

        partial = _liveness()
        del partial[_POOL.models[-1].model_id]  # one model never probed at all
        with pytest.raises(PreflightError, match=r"probed 2 of 3 roster models"):
            _run(tmp_path, probe_fn=lambda env: partial)

    def test_role_with_fewer_than_two_live_preferred_models_fails(self, tmp_path: Path) -> None:
        from perturb_eval.experiments.v05_preflight import PreflightError

        table = _liveness(live=["stub/one"])  # Architect prefs = (one, two, three): only one live
        with pytest.raises(PreflightError, match=r"Architect.*1 live preferred"):
            _run(tmp_path, probe_fn=lambda env: table)

    def test_report_carries_liveness_table_with_probe_dates(self, tmp_path: Path) -> None:
        rep = _run(tmp_path)
        assert set(rep.roster_liveness) == {m.model_id for m in _POOL.models}
        for e in rep.roster_liveness.values():
            assert (
                e["live"] is True
                and re.match(r"\d{4}-\d{2}-\d{2}T", e["probed_at"])
                and e["verdict"]
            )

    def test_default_probe_uses_the_validator_schema_on_every_model(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """openrouter_probe_all probes every DEFAULT_POOL model and applies parse_proposal('Validator')."""
        from perturb_eval.experiments import v05_preflight as pf

        probed: list[str] = []

        def fake_probe_model(self, model_id, prompt):  # noqa: ANN001
            probed.append(model_id)
            ok = not model_id.endswith("-dead")
            return (
                ok,
                "ok" if ok else "http 404",
                ({"confidence": 0.5, "dynamic_threshold_msd": 0.1} if ok else None),
            )

        monkeypatch.setattr(OpenRouterClient, "probe_model", fake_probe_model)
        table = pf.openrouter_probe_all({"OPENROUTER_API_KEY": "k"})
        assert probed == [m.model_id for m in DEFAULT_POOL.models]
        assert all(table[m]["live"] for m in probed)

    def test_default_probe_marks_schema_invalid_reply_as_not_live(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        from perturb_eval.experiments import v05_preflight as pf

        monkeypatch.setattr(
            OpenRouterClient, "probe_model", lambda self, m, p: (True, "ok", {"confidence": 0.5})
        )
        table = pf.openrouter_probe_all(
            {"OPENROUTER_API_KEY": "k"}
        )  # threshold missing -> schema failure (A3-3)
        assert all(not e["live"] and "schema" in e["verdict"] for e in table.values())


# ------------------------------------------------------------ 4. provenance
class TestLivenessInProvenance:
    def test_build_provenance_records_liveness(self) -> None:
        from tests.test_provenance import _prov

        table = {"m/one": {"live": True, "verdict": "ok", "probed_at": "2026-09-28T23:00:00+00:00"}}
        p = _prov(llm_roster_liveness=table)
        assert p["llm_roster_liveness"] == table
        assert "llm_roster_liveness" in _prov()  # always present (None when not supplied)

    def test_build_provenance_rejects_malformed_liveness(self) -> None:
        from tests.test_provenance import _prov

        with pytest.raises(ValueError, match="llm_roster_liveness"):
            _prov(llm_roster_liveness={"m/one": {"live": "yes"}})

    def test_app_v05_passes_liveness_to_provenance(self) -> None:
        src = (Path(__file__).resolve().parents[1] / "scripts" / "modal" / "app_v05.py").read_text()
        assert "llm_roster_liveness=report.roster_liveness" in src
