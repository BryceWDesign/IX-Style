"""Executable runtime-assurance constraint catalog for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from ix_style.core.enums import (
    ArbitrationOutcome,
    CommandSource,
    FunctionClass,
    SafetyPosture,
)

from .models import ConstraintEvaluation, ConstraintMatch, GuardContext

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

_MOTION_FUNCTIONS: Final[frozenset[FunctionClass]] = frozenset(
    {
        FunctionClass.GUIDANCE_REQUEST,
        FunctionClass.ACTUATION_REQUEST,
    }
)

_RESOURCE_SENSITIVE_FUNCTIONS: Final[frozenset[FunctionClass]] = frozenset(
    {
        FunctionClass.GUIDANCE_REQUEST,
        FunctionClass.ACTUATION_REQUEST,
        FunctionClass.RESOURCE_CONFIGURATION,
    }
)

_OUTCOME_STRENGTH: Final[dict[ArbitrationOutcome, int]] = {
    ArbitrationOutcome.ACCEPT: 0,
    ArbitrationOutcome.DEFER: 1,
    ArbitrationOutcome.CLAMP: 2,
    ArbitrationOutcome.SUBSTITUTE: 3,
    ArbitrationOutcome.FREEZE: 4,
    ArbitrationOutcome.VETO: 5,
    ArbitrationOutcome.ESCALATE_TO_MODE_CHANGE: 6,
}


@dataclass(slots=True)
class BaselineConstraintCatalog:
    """Named, reviewable constraint rules for the reference guard."""

    def evaluate(self, context: GuardContext) -> ConstraintEvaluation:
        payload = context.control_payload()
        flags = set(context.active_degradation_flags)
        matches: list[ConstraintMatch] = []

        if (
            context.safety_posture is SafetyPosture.SAFE_HOLD
            and payload.function_class in _SAFE_HOLD_BLOCKED_FUNCTIONS
        ):
            matches.append(
                ConstraintMatch(
                    constraint_id="IXS-CONSTRAINT-001",
                    outcome=ArbitrationOutcome.VETO,
                    rationale_summary=(
                        "safe-hold containment posture blocks mission-progress or"
                        " override-oriented command classes"
                    ),
                    policy_evaluation_result="DENIED",
                    resulting_mode_target=SafetyPosture.SAFE_HOLD,
                    command_delta={
                        "change_type": "BLOCKED",
                        "final_summary": "command blocked by safe-hold containment rule",
                    },
                )
            )

        if (
            context.safety_posture is SafetyPosture.ASSURANCE_DEGRADED
            and payload.function_class in _ASSURANCE_DEGRADED_HIGH_RISK_FUNCTIONS
        ):
            matches.append(
                ConstraintMatch(
                    constraint_id="IXS-CONSTRAINT-002",
                    outcome=ArbitrationOutcome.FREEZE,
                    rationale_summary=(
                        "assurance-degraded posture freezes high-risk command paths"
                        " until guard health is restored"
                    ),
                    policy_evaluation_result="DENIED",
                    resulting_mode_target=SafetyPosture.ASSURANCE_DEGRADED,
                    command_delta={
                        "change_type": "FROZEN",
                        "final_summary": "command path frozen under assurance-degraded posture",
                    },
                )
            )

        if "power_margin_low" in flags and payload.function_class in _RESOURCE_SENSITIVE_FUNCTIONS:
            matches.append(
                ConstraintMatch(
                    constraint_id="IXS-CONSTRAINT-003",
                    outcome=ArbitrationOutcome.CLAMP,
                    rationale_summary=(
                        "power-margin degradation narrows resource-sensitive behavior"
                    ),
                    policy_evaluation_result="CONDITIONALLY_ALLOWED",
                    command_delta={
                        "change_type": "CLAMPED",
                        "final_summary": "command accepted only in reduced bounded form",
                    },
                )
            )

        if "nav_spoof_suspected" in flags and payload.function_class in _MOTION_FUNCTIONS:
            matches.append(
                ConstraintMatch(
                    constraint_id="IXS-CONSTRAINT-004",
                    outcome=ArbitrationOutcome.VETO,
                    rationale_summary=(
                        "spoof-suspected navigation collapse vetoes motion-related commands"
                    ),
                    policy_evaluation_result="DENIED",
                    resulting_mode_target=SafetyPosture.NAV_DEGRADED,
                    command_delta={
                        "change_type": "BLOCKED",
                        "final_summary": "motion command blocked due to spoof-suspected nav posture",
                    },
                )
            )
        elif "nav_corroboration_lost" in flags and payload.function_class in _MOTION_FUNCTIONS:
            matches.append(
                ConstraintMatch(
                    constraint_id="IXS-CONSTRAINT-005",
                    outcome=ArbitrationOutcome.CLAMP,
                    rationale_summary=(
                        "navigation corroboration loss narrows motion-related commands"
                    ),
                    policy_evaluation_result="CONDITIONALLY_ALLOWED",
                    resulting_mode_target=SafetyPosture.NAV_DEGRADED,
                    command_delta={
                        "change_type": "CLAMPED",
                        "final_summary": "motion command narrowed by degraded navigation trust",
                    },
                )
            )

        if "sensor_trust_low" in flags and payload.function_class in _MOTION_FUNCTIONS:
            matches.append(
                ConstraintMatch(
                    constraint_id="IXS-CONSTRAINT-006",
                    outcome=ArbitrationOutcome.CLAMP,
                    rationale_summary=(
                        "critical sensor trust degradation narrows motion-related behavior"
                    ),
                    policy_evaluation_result="CONDITIONALLY_ALLOWED",
                    resulting_mode_target=SafetyPosture.SENSOR_DEGRADED,
                    command_delta={
                        "change_type": "CLAMPED",
                        "final_summary": "motion command narrowed by degraded sensor trust",
                    },
                )
            )

        if "actuator_response_uncertain" in flags and payload.function_class in _MOTION_FUNCTIONS:
            matches.append(
                ConstraintMatch(
                    constraint_id="IXS-CONSTRAINT-007",
                    outcome=ArbitrationOutcome.CLAMP,
                    rationale_summary=(
                        "actuation uncertainty narrows motion-related behavior"
                    ),
                    policy_evaluation_result="CONDITIONALLY_ALLOWED",
                    resulting_mode_target=SafetyPosture.ACTUATION_DEGRADED,
                    command_delta={
                        "change_type": "CLAMPED",
                        "final_summary": "motion command narrowed by actuation uncertainty",
                    },
                )
            )

        if (
            payload.command_source is CommandSource.OPERATOR
            and payload.function_class is FunctionClass.RECOVERY_ACTION
            and {"comms_link_intermittent", "command_freshness_low"}.intersection(flags)
        ):
            matches.append(
                ConstraintMatch(
                    constraint_id="IXS-CONSTRAINT-008",
                    outcome=ArbitrationOutcome.DEFER,
                    rationale_summary=(
                        "operator recovery action is deferred while comms degradation or"
                        " freshness uncertainty remains active"
                    ),
                    policy_evaluation_result="DEFERRED",
                    command_delta={
                        "change_type": "DEFERRED",
                        "final_summary": "recovery action deferred pending trusted comms state",
                    },
                    metadata={"recovery_gate_status": "DEFERRED"},
                )
            )

        selected = self._select_strongest_match(matches)
        return ConstraintEvaluation(matches=tuple(matches), selected_match=selected)

    @staticmethod
    def _select_strongest_match(
        matches: list[ConstraintMatch],
    ) -> ConstraintMatch | None:
        selected: ConstraintMatch | None = None
        selected_strength = -1
        for match in matches:
            strength = _OUTCOME_STRENGTH[match.outcome]
            if strength > selected_strength:
                selected = match
                selected_strength = strength
        return selected
