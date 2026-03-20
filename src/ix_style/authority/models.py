"""Authority evaluation models for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass, field

from ix_style.core.enums import (
    ArbitrationOutcome,
    CommandSource,
    MissionPhase,
    SafetyPosture,
)
from ix_style.core.models import ControlPayload, MessageEnvelope


@dataclass(slots=True, frozen=True)
class AuthorityContext:
    """Inputs needed to evaluate whether a control request may proceed."""

    envelope: MessageEnvelope
    mission_phase: MissionPhase
    safety_posture: SafetyPosture
    active_degradation_flags: tuple[str, ...] = ()

    def control_payload(self) -> ControlPayload:
        """Return the typed control payload or raise when the envelope is malformed."""
        payload = self.envelope.payload
        if not isinstance(payload, ControlPayload):
            raise TypeError("authority evaluation requires a ControlPayload")
        return payload


@dataclass(slots=True, frozen=True)
class AuthorityDecision:
    """Outcome of the authority stage before runtime-assurance guard evaluation."""

    outcome: ArbitrationOutcome
    final_authoritative_source: CommandSource
    rationale_summary: str
    policy_evaluation_result: str
    rule_ids: tuple[str, ...] = ()
    frozen_paths: tuple[str, ...] = ()
    mode_escalation_requested: bool = False
    recovery_gate_result: str = "NOT_APPLICABLE"
    stage_name: str = "authority"
    metadata: dict[str, str] = field(default_factory=dict)
