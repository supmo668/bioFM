"""LungMembraneEnv — the virtual lung membrane exposed as an aviary Environment.

Written to the same contract as `BioSimEnv` in supmo668/Aviary-BioSim (`science/biosim_env.py`):
two abstract methods, `Tool.from_function` over plain functions whose docstrings are the schema,
`filter_invalid_tool_calls` for unknown calls, and `ToolResponseMessage.from_call` for replies.
Three of its decisions are carried over deliberately, because each was load-bearing there:

- **Reward is 0.0 and says so.** aviary carries a reward because it is an RL gym. This is
  tool-mediated experiment design, not training, and inventing a scalar to fill the slot would
  be a fabricated signal.
- **The refusal happens before the tool runs and outside the error handler.** In `BioSimEnv`
  that kept a budget refusal from being reported as a tool failure. Here the same structure
  keeps a *readiness* refusal from being reported as one.
- **The agent cannot write the ledger.** It is offered a read-only remaining-budget tool and no
  tool that records spend.

What differs is what the environment is for. `BioSimEnv` measures: its tools run a real protein
model and return the number that comes out. This environment **cannot measure yet**, and its
first duty is to say so precisely. `predict_exposure` consults `readiness.assess` on every call
and, while any blocking artifact is absent, returns the artifact-by-artifact refusal instead of
a number. That is not a stub: it is the project's thesis made executable. An agent exploring
this environment learns which six quotes and which signature stand between it and a prediction,
which is a more useful thing to learn than a plausible fabricated exposure.

`fhaviary` is imported at module level, so this module is optional: `chipsim.sandbox.readiness`
and `chipsim.sandbox.interpretability` are importable and testable without it.
"""

from __future__ import annotations

import json
from pathlib import Path

from aviary.core import (
    Environment,
    Frame,
    Message,
    Tool,
    ToolRequestMessage,
    ToolResponseMessage,
)

from chipsim.sandbox import readiness
from chipsim.sandbox.interpretability import Abstention, ParameterProvenance

#: Bumped when the environment's contract changes, and reported in every payload. A result
#: whose producing version is unknown cannot be reproduced or retracted.
ENV_VERSION = "0.1.0-prewired"


def _is_refusal(result: object) -> bool:
    """True when a tool result declined rather than answered.

    Counted so `export_frame` can distinguish a rollout that produced results from one that
    spent every round being refused — two outcomes a single transcript length would blur.
    Checks both shapes a refusal arrives in: the plain-text readiness refusal, and the JSON
    abstention from `predict_exposure`. Keying on only the first is how the counter read zero
    while every call was in fact declined.
    """
    if not isinstance(result, str):
        return False
    if result.startswith("REFUSED"):
        return True
    try:
        return json.loads(result).get("kind") == "abstention"
    except (ValueError, AttributeError):
        return False


class NotReady(RuntimeError):
    """The sandbox lacks a blocking input. Raised before any tool runs, never from inside one."""


class LungMembraneState:
    """What the environment knows. Hidden from the agent except through observations."""

    def __init__(self, max_rounds: int) -> None:
        self.round = 0
        self.max_rounds = max_rounds
        self.done = False
        #: Every tool call and its result, in order — the audit trail, as in BioSimEnv.
        self.transcript: list[str] = []
        #: Calls refused for readiness, counted separately: a rollout that spent all its rounds
        #: being refused is a different outcome from one that produced results, and a single
        #: transcript would blur them.
        self.refusals = 0


class LungMembraneEnv(Environment[LungMembraneState]):
    """A lung-membrane transport workbench exposed as an aviary Environment.

    Args:
        objective: what the agent is being asked to find out.
        project_root: the ChipSim project directory whose artifacts decide readiness.
        max_rounds: rollout length.
    """

    def __init__(
        self,
        objective: str,
        project_root: Path | str = ".",
        max_rounds: int = 8,
    ) -> None:
        self.objective = objective
        self.project_root = Path(project_root)
        self.state = LungMembraneState(max_rounds)
        self.tools: list[Tool] = []
        # name -> callable, held here rather than read back off Tool: aviary exposes no public
        # accessor for a Tool's function, only the private `_tool_fn`. (Same note as BioSimEnv.)
        self._fns: dict = {}

    # -- the tools offered to the agent ------------------------------------- #

    def readiness_report(self) -> str:
        """Report whether the simulator may produce a number, and what is blocking it.

        Returns one line per required input: the artifact, the plan task that owns it, who must
        supply it, and what its absence blocks. Call this first.
        """
        report = readiness.assess(self.project_root)
        if report.can_predict:
            lines = ["READY: every blocking input is present and accepted."]
            lines += [f"  - {s.key}: {s.detail}" for s in report.statuses]
            if report.degradations:
                lines.append("Degradations that change how results must be read:")
                lines += [f"  - {d}" for d in report.degradations]
            return "\n".join(lines)
        return report.refusal()

    def parameter_provenance(self) -> str:
        """Report, per device parameter, whether its value is cited, derived or assumed.

        A prediction's trustworthiness is bounded by its least-supported input, so this is
        reported separately from any result and can be called before committing to one.
        """
        report = readiness.assess(self.project_root)
        theta = next(s for s in report.statuses if s.key == "theta")
        if not theta.present:
            return (
                "No device parameters are available: configs/theta_priors.yaml is absent, which "
                "is the enforced state until a human ratifies a filled file (build-plan S6). "
                "The six fields it must carry are flow_ul_min, membrane_um, porosity, "
                "strain_pct, area_mm2 and coating; each needs a citation or an explicit "
                "assumed flag."
            )
        if theta.accepted is False:
            return f"Device parameters present but REFUSED by the validator: {theta.detail}"
        return f"Device parameters accepted — {theta.detail}"

    def predict_exposure(self, compound_inchikey: str, dose_umol_per_l: float) -> str:
        """Predict drug exposure at the tissue face of the barrier, with its interpretation.

        Returns a JSON object carrying the prediction, its interval and the basis that gives the
        interval meaning, the provenance of every parameter used, and the supporting evidence —
        or a structured abstention naming what is missing. It never returns a bare number.

        Args:
            compound_inchikey: canonical InChIKey of the compound to predict for.
            dose_umol_per_l: applied concentration in the perfused channel, in micromolar.
        """
        report = readiness.assess(self.project_root)
        if not report.can_predict:
            # An abstention, not an error: the caller is owed the reason and the remedy in the
            # same shape a prediction would have arrived in.
            missing = [s.artifact.plan_task for s in report.blocking_absent]
            abstention = Abstention(
                reason=report.refusal(),
                what_would_change_it=(
                    "Ratified values for the blocking artifacts above. In plan terms: "
                    + ", ".join(missing)
                    + ". Each is human-owned; no agent step can supply one."
                ),
                parameters=(
                    ParameterProvenance(
                        name="theta",
                        provenance="assumed",
                        note=(
                            "not consulted: the file is absent, so no parameter was read and "
                            "none was substituted"
                        ),
                    ),
                ),
                domain_note=(
                    f"requested compound {compound_inchikey!r} at {dose_umol_per_l} uM was not "
                    "evaluated; the request is recorded and nothing was computed"
                ),
            )
            payload = abstention.as_dict()
            payload["model_version"] = ENV_VERSION
            return json.dumps(payload, indent=2)
        # The ready branch is deliberately not implemented: the model it would call does not
        # exist, and a placeholder that returned a shaped number would be indistinguishable
        # from a real one in every downstream artifact. Reaching here means the inputs landed
        # and the surrogate is the next thing to build.
        raise NotImplementedError(
            "Inputs are ratified, so the transport surrogate is now the blocking work. Wire "
            "chipsim.transport here and return an interpretability.Prediction; do not return "
            "a bare float."
        )

    def declared_contract(self) -> str:
        """Report what every result from this environment is guaranteed to carry.

        Useful to an agent deciding whether this environment can answer its question at all.
        """
        return (
            "Every result is a decision object, never a bare measurement. A prediction carries: "
            "the quantity and unit; a point and an interval; a coverage basis stating the "
            "nominal level, the calibration-set size, the subgroup it is conditional on, and "
            "whether the guarantee is group-conditional or marginal; the provenance of every "
            "parameter used, as cited, derived or assumed, with a citation required for the "
            "first two; the supporting curated records; and a model version. An abstention is a "
            "first-class outcome carrying the same obligations. Reward is always 0.0: this "
            "environment is for tool-mediated experiment design, not reinforcement learning, "
            "and a fabricated scalar would be worse than an absent one."
        )

    # -- the aviary contract ------------------------------------------------- #

    async def reset(self) -> tuple[list[Message], list[Tool]]:
        self.state = LungMembraneState(self.state.max_rounds)
        # One list builds both the offered tools and the callables that run them, so the two
        # cannot drift — the BioSimEnv pattern. No tool writes any artifact: every input this
        # environment depends on is human-owned.
        fns = [
            self.readiness_report,
            self.parameter_provenance,
            self.predict_exposure,
            self.declared_contract,
        ]
        self.tools = [Tool.from_function(fn) for fn in fns]
        self._fns = {tool.info.name: fn for tool, fn in zip(self.tools, fns)}
        report = readiness.assess(self.project_root)
        status = (
            "The simulator is READY: every blocking input is present."
            if report.can_predict
            else (
                "The simulator is NOT ready and will refuse to predict. "
                f"{len(report.blocking_absent)} blocking input(s) are absent; call "
                "readiness_report for the artifact-by-artifact reason. Do not attempt to work "
                "around the refusal — the inputs are human-owned claims, not computations."
            )
        )
        obs = [
            Message(
                content=(
                    f"{self.objective}\n\n"
                    "You are at a virtual lung-membrane workbench. Its tools report what the "
                    "simulator may do and, when permitted, predict drug exposure at the tissue "
                    "face with the interval, the parameter provenance and the evidence that "
                    "make the number actionable. Every result is a decision object; no tool "
                    "returns a bare number, and no tool invents a value.\n\n"
                    f"{status}\n\n"
                    f"You have {self.state.max_rounds} rounds."
                )
            )
        ]
        return obs, self.tools

    async def step(self, action: Message) -> tuple[list[Message], float, bool, bool]:
        self.state.round += 1
        if not isinstance(action, ToolRequestMessage) or not action.tool_calls:
            return self.default_no_tool_calls_response

        valid, invalid = self.filter_invalid_tool_calls(action)
        responses: list[Message] = []
        for call in valid.tool_calls:
            fn = self._fns[call.function.name]
            try:
                result = fn(**call.function.arguments)
            except NotImplementedError as exc:
                # Surfaced as a tool result rather than crashing the rollout: it is a statement
                # about the project's state, which the agent should be able to read and report.
                result = f"not implemented: {exc}"
            except Exception as exc:  # noqa: BLE001 — a tool that fails says so, never a number
                result = f"tool error: {type(exc).__name__}: {exc}"
            if _is_refusal(result):
                self.state.refusals += 1
            self.state.transcript.append(
                f"{call.function.name}({call.function.arguments}) -> {result}"
            )
            responses.append(ToolResponseMessage.from_call(call, str(result)))
        for call in invalid.tool_calls:
            responses.append(ToolResponseMessage.from_call(call, "no such tool"))

        truncated = self.state.round >= self.state.max_rounds
        self.state.done = truncated
        # Reward stays 0.0 on purpose — see the module docstring.
        return responses, 0.0, self.state.done, truncated

    def export_frame(self) -> Frame:
        return Frame(
            state={
                "round": self.state.round,
                "tool_calls": len(self.state.transcript),
                "readiness_refusals": self.state.refusals,
            },
            info={"objective": self.objective, "env_version": ENV_VERSION},
        )
