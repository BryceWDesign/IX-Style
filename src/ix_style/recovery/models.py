"""Executable recovery-gate models for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from ix_style.core.enums import MissionPhase, SafetyPosture
from ix_style.core.models import ControlPayload, MessageEnvelope
from ix_style.fdir.models import FaultRecord
from ix_style.trust.models import TrustRecord


class RecoveryGateStatus(StrEnum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    PASSED = "PASSED"
    FAILED = "FAILED"
    DEFERRED = "DEFERRED"


@dataclass(slots=True, frozen=True)
class RecoveryGateContext:
    """Inputs required for recovery-gate evaluation."""

    envelope: MessageEnvelope
    mission_phase: MissionPhase
    safety_posture: SafetyPosture
    active_degradation_flags: tuple[str, ...] = ()
    trust_records: dict[str, TrustRecord] = field(default_factory=dict)
    fault_records: dict[str, FaultRecord] = field(default_factory=dict)

    def control_payload(self) -> ControlPayload:
        """Return the typed control payload or raise when the envelope is malformed."""
        payload = self.envelope.payload
        if not isinstance(payload, ControlPayload):
            raise TypeError("recovery-gate evaluation requires a ControlPayload")
        return payload


@dataclass(slots=True, frozen=True)
class RecoveryGateDecision:
    """Outcome of recovery-gate qualification."""

    gate_status: RecoveryGateStatus
    allow_progression: bool
    rationale_summary: str
    blocking_fault_ids: tuple[str, ...] = ()
    blocking_trust_record_ids: tuple[str, ...] = ()
    stage_name: str = "recovery_gate"
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.rationale_summary.strip():
            raise ValueError("rationale_summary must not be empty")
