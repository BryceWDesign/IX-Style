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
