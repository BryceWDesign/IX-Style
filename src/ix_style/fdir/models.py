"""Executable FDIR models for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from ix_style.core.enums import FaultLifecycleState


class FaultClass(StrEnum):
    SENSOR_FAULT = "SENSOR_FAULT"
    NAVIGATION_TRUST_FAULT = "NAVIGATION_TRUST_FAULT"
    TIMING_FAULT = "TIMING_FAULT"
    COMMUNICATION_FAULT = "COMMUNICATION_FAULT"
    POWER_RESOURCE_FAULT = "POWER_RESOURCE_FAULT"
    ACTUATION_FAULT = "ACTUATION_FAULT"
    SOFTWARE_HEALTH_FAULT = "SOFTWARE_HEALTH_FAULT"
    ASSURANCE_FAULT = "ASSURANCE_FAULT"
    POLICY_AUTHORITY_FAULT = "POLICY_AUTHORITY_FAULT"
    EVIDENCE_FAULT = "EVIDENCE_FAULT"
    MULTI_FAULT_COMPOUND = "MULTI_FAULT_COMPOUND"


class FaultSeverity(StrEnum):
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"
    CATASTROPHIC = "CATASTROPHIC"


class FaultPriority(StrEnum):
    P1_CONTAINMENT_CRITICAL = "P1_CONTAINMENT_CRITICAL"
    P2_HIGH = "P2_HIGH"
    P3_MODERATE = "P3_MODERATE"
    P4_LOW = "P4_LOW"


class FaultIsolationConfidence(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class MitigationCategory(StrEnum):
    OBSERVE_ONLY = "OBSERVE_ONLY"
    DEGRADE_FUNCTION = "DEGRADE_FUNCTION"
    REDUCE_AUTHORITY = "REDUCE_AUTHORITY"
    SWITCH_SOURCE = "SWITCH_SOURCE"
    CLAMP_BEHAVIOR = "CLAMP_BEHAVIOR"
    FREEZE_PATH = "FREEZE_PATH"
    ENTER_DEGRADED_MODE = "ENTER_DEGRADED_MODE"
    ENTER_SAFE_HOLD = "ENTER_SAFE_HOLD"
    LATCH_AND_REQUIRE_RESET = "LATCH_AND_REQUIRE_RESET"
    RECOVERY_GATE_EVALUATION = "RECOVERY_GATE_EVALUATION"


def utc_now() -> datetime:
    """Return an aware UTC timestamp."""
    return datetime.now(tz=UTC)


@dataclass(slots=True, frozen=True)
class FDIRSignal:
    """One abnormal-condition observation or healthy recovery observation."""

    fault_class: FaultClass
    detection_source: str
    affected_function_scope: str
    observed_at: datetime
    anomaly_active: bool = True
    corroborated: bool = False
    containment_required: bool = False
    mitigation_requested: bool = False
    latch_required: bool = False
    recovery_requested: bool = False
    recovery_permitted: bool = False
    severity_estimate: FaultSeverity = FaultSeverity.MAJOR
    evidence_critical: bool = False
    authority_relevant: bool = False
    rationale_hint: str | None = None
    cause_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.detection_source.strip():
            raise ValueError("detection_source must not be empty")
        if not self.affected_function_scope.strip():
            raise ValueError("affected_function_scope must not be empty")


@dataclass(slots=True, frozen=True)
class FaultRecord:
    """Persistent record for one fault instance."""

    fault_id: str
    fault_class: FaultClass
    lifecycle_state: FaultLifecycleState
    detection_source: str
    first_detected_timestamp: datetime
    latest_update_timestamp: datetime
    affected_function_scope: str
    severity_estimate: FaultSeverity
    confirmation_confidence: float
    isolation_confidence: FaultIsolationConfidence
    active_mitigation_set: tuple[MitigationCategory, ...] = ()
    current_priority: FaultPriority = FaultPriority.P4_LOW
    latch_status: bool = False
    recovery_gate_status: str = "NOT_APPLICABLE"
    rationale_summary: str = ""
    occurrence_count: int = 0
    corroborated_count: int = 0

    def __post_init__(self) -> None:
        if not self.fault_id.strip():
            raise ValueError("fault_id must not be empty")
        if not self.detection_source.strip():
            raise ValueError("detection_source must not be empty")
        if not self.affected_function_scope.strip():
            raise ValueError("affected_function_scope must not be empty")
        if not 0.0 <= self.confirmation_confidence <= 1.0:
            raise ValueError("confirmation_confidence must be between 0.0 and 1.0")
        if self.occurrence_count < 0:
            raise ValueError("occurrence_count must be non-negative")
        if self.corroborated_count < 0:
            raise ValueError("corroborated_count must be non-negative")


@dataclass(slots=True, frozen=True)
class FaultTransition:
    """Machine-readable fault lifecycle transition."""

    fault_id: str
    fault_class: FaultClass
    previous_state: FaultLifecycleState
    new_state: FaultLifecycleState
    transition_time: datetime
    priority_before: FaultPriority
    priority_after: FaultPriority
    cause_codes: tuple[str, ...] = ()
    rationale_summary: str = ""

    def __post_init__(self) -> None:
        if not self.fault_id.strip():
            raise ValueError("fault_id must not be empty")


@dataclass(slots=True, frozen=True)
class FDIREvaluationResult:
    """Result of one FDIR evaluation step."""

    record: FaultRecord
    transition: FaultTransition | None
    rationale_summary: str
    auto_generated_record: bool = False
    negative_evidence_present: bool = False
    metadata: dict[str, str] = field(default_factory=dict)
