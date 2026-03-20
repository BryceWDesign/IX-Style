"""Baseline runtime-assurance guard for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Protocol

from ix_style.core.enums import (
    ArbitrationOutcome,
    CommandSource,
    FunctionClass,
    SafetyPosture,
)

from .models import GuardContext, GuardDecision

_SAFE_HOLD_BLOCKED_FUNCTIONS: Final[frozenset[FunctionClass]] = frozenset(
    {
        FunctionClass.MISSION_INTENT,
        FunctionClass.GUIDANCE_REQUEST,
        FunctionClass.ACTUATION_REQUEST,
        FunctionClass.RESOURCE_CONFIGURATION,
        FunctionClass.POLICY_OVERRIDE,
    }
)

_ASSURANCE_DEGRADED_HIGH_RISK_FUNCTIONS: Final[frozenset[FunctionClass]] = frozenset(
    {
        FunctionClass.GUIDANCE_REQUEST,
        FunctionClass.ACTUATION_REQUEST,
        FunctionClass.RESOURCE_CONFIGURATION,
        FunctionClass.POLICY_OVERRIDE,
    }
)


class GuardEngine(Protocol):
    """Protocol for runtime-assurance guard engines."""

    def evaluate(self, context: GuardContext) -> GuardDecision:
        """Evaluate whether an authority-approved command remains safe enough to use."""


@dataclass(slots=True)
class SimpleGuardEngine:
    """Baseline guard with deterministic containment-oriented posture handling."""

    def evaluate(self, context: GuardContext) -> GuardDecision:
        payload = context.control_payload()

        if (
            context.safety_posture is SafetyPosture.SAFE_HOLD
            and payload.function_class in _SAFE_HOLD_BLOCKED_FUNCTIONS
        ):
            return GuardDecision(
                outcome=ArbitrationOutcome.VETO,
                final_authoritative_source=CommandSource.SAFETY_SUPERVISOR,
                rationale_summary=(
                    "safe-hold containment posture blocks mission-progress or override"
                    " command classes"
                ),
                policy_evaluation_result="DENIED",
                triggered_constraint_ids=("CONTAINMENT-SAFE-HOLD-BLOCK",),
                resulting_mode_target=SafetyPosture.SAFE_HOLD,
                command_delta={
                    "change_type": "BLOCKED",
                    "final_summary": "command blocked by safe-hold containment rule",
                },
            )

        if (
            context.safety_posture is SafetyPosture.ASSURANCE_DEGRADED
            and payload.function_class in _ASSURANCE_DEGRADED_HIGH_RISK_FUNCTIONS
        ):
            return GuardDecision(
                outcome=ArbitrationOutcome.FREEZE,
                final_authoritative_source=CommandSource.SAFETY_SUPERVISOR,
                rationale_summary=(
                    "assurance-degraded posture freezes high-risk control paths until"
                    " guard health is restored"
                ),
                policy_evaluation_result="DENIED",
                triggered_constraint_ids=("ASSURANCE-DEGRADED-HIGH-RISK-FREEZE",),
                resulting_mode_target=SafetyPosture.ASSURANCE_DEGRADED,
                command_delta={
                    "change_type": "FROZEN",
                    "final_summary": "command path frozen under assurance-degraded posture",
                },
            )

        if "power_margin_low" in context.active_degradation_flags and payload.function_class in {
            FunctionClass.GUIDANCE_REQUEST,
            FunctionClass.ACTUATION_REQUEST,
            FunctionClass.RESOURCE_CONFIGURATION,
        }:
            return GuardDecision(
                outcome=ArbitrationOutcome.CLAMP,
                final_authoritative_source=CommandSource.SAFETY_SUPERVISOR,
                rationale_summary=(
                    "power-margin degradation narrows resource-intensive command scope"
                ),
                policy_evaluation_result="CONDITIONALLY_ALLOWED",
                triggered_constraint_ids=("RESOURCE-POWER-MARGIN-CLAMP",),
                command_delta={
                    "change_type": "CLAMPED",
                    "final_summary": "command accepted only in reduced bounded form",
                },
            )

        return GuardDecision(
            outcome=ArbitrationOutcome.ACCEPT,
            final_authoritative_source=context.authority_decision.final_authoritative_source,
            rationale_summary="guard accepted the candidate command within current bounds",
            policy_evaluation_result="ALLOWED",
            triggered_constraint_ids=("GUARD-BASELINE-ALLOW",),
            command_delta={"change_type": "NONE"},
        )
