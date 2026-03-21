"""Runtime-assurance guard models for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ix_style.authority.models import AuthorityDecision
from ix_style.core.enums import (
    ArbitrationOutcome,
    CommandSource,
    MissionPhase,
    SafetyPosture,
)
from ix_style.core.models import ControlPayload, MessageEnvelope


@dataclass(slots=True, frozen=True)
class GuardContext:
    """Inputs required by the runtime-assurance guard."""

    envelope: MessageEnvelope
    mission_phase: MissionPhase
    safety_posture: SafetyPosture
    authority_decision: AuthorityDecision
    active_degradation_flags: tuple[str, ...] = ()

    def control_payload(self) -> ControlPayload:
        """Return the typed control payload or raise when the envelope is malformed."""
        payload = self.envelope.payload
        if not isinstance(payload, ControlPayload):
            raise TypeError("guard evaluation requires a ControlPayload")
        return payload


@dataclass(slots=True, frozen=True)
class ConstraintMatch:
    """One triggered runtime-assurance constraint."""

    constraint_id: str
    outcome: ArbitrationOutcome
    rationale_summary: str
    policy_evaluation_result: str
    final_authoritative_source: CommandSource = CommandSource.SAFETY_SUPERVISOR
    mode_escalation_requested: bool = False
    resulting_mode_target: SafetyPosture | None = None
    command_delta: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.constraint_id.strip():
            raise ValueError("constraint_id must not be empty")
        if not self.rationale_summary.strip():
            raise ValueError("rationale_summary must not be empty")
        if not self.policy_evaluation_result.strip():
            raise ValueError("policy_evaluation_result must not be empty")


@dataclass(slots=True, frozen=True)
class ConstraintEvaluation:
    """Aggregated result of evaluating the constraint catalog."""

    matches: tuple[ConstraintMatch, ...] = ()
    selected_match: ConstraintMatch | None = None


@dataclass(slots=True, frozen=True)
class GuardDecision:
    """Outcome of the guard stage after authority has allowed a candidate through."""

    outcome: ArbitrationOutcome
    final_authoritative_source: CommandSource
    rationale_summary: str
    policy_evaluation_result: str
    triggered_constraint_ids: tuple[str, ...] = ()
    mode_escalation_requested: bool = False
    resulting_mode_target: SafetyPosture | None = None
    command_delta: dict[str, Any] = field(default_factory=dict)
    recovery_gate_result: str = "NOT_APPLICABLE"
    stage_name: str = "guard"
    metadata: dict[str, str] = field(default_factory=dict)
