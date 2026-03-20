"""Core dataclasses for IX-Style message and evidence objects."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import UTC, datetime
from typing import Any

from .enums import (
    ArbitrationOutcome,
    AuthState,
    CommandSource,
    FreshnessState,
    FunctionClass,
    IntegrityState,
    MessageClass,
    MissionPhase,
    ReplayState,
    SafetyPosture,
)


def utc_now() -> datetime:
    """Return an aware UTC timestamp."""
    return datetime.now(tz=UTC)


def _primitive(value: Any) -> Any:
    """Convert dataclasses, enums, and datetimes into JSON-friendly primitives."""
    if is_dataclass(value):
        return {key: _primitive(item) for key, item in asdict(value).items()}
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, list):
        return [_primitive(item) for item in value]
    if isinstance(value, dict):
        return {key: _primitive(item) for key, item in value.items()}
    return value


@dataclass(slots=True)
class FreshnessMetadata:
    issued_at: datetime
    expires_at: datetime | None
    freshness_state: FreshnessState
    freshness_cause_codes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.expires_at is not None and self.expires_at < self.issued_at:
            raise ValueError("expires_at must be greater than or equal to issued_at")


@dataclass(slots=True)
class OrderingMetadata:
    sequence_number: int
    session_id: str
    replay_state: ReplayState
    parent_message_id: str | None = None
    supersedes_message_id: str | None = None

    def __post_init__(self) -> None:
        if self.sequence_number < 0:
            raise ValueError("sequence_number must be non-negative")
        if not self.session_id.strip():
            raise ValueError("session_id must not be empty")


@dataclass(slots=True)
class IntegrityMetadata:
    integrity_state: IntegrityState
    auth_state: AuthState
    trust_domain_id: str | None = None
    signature_present: bool = False
    verified_at: datetime | None = None
    verification_rationale: str | None = None


@dataclass(slots=True)
class ControlPayload:
    function_class: FunctionClass
    requested_action: str
    command_source: CommandSource
    policy_context: dict[str, Any]
    requested_scope: str | None = None
    requested_magnitude: float | None = None
    requested_rate: float | None = None
    requested_duration_ms: int | None = None
    rationale_summary: str | None = None

    def __post_init__(self) -> None:
        if not self.requested_action.strip():
            raise ValueError("requested_action must not be empty")
        if self.requested_duration_ms is not None and self.requested_duration_ms < 0:
            raise ValueError("requested_duration_ms must be non-negative")


@dataclass(slots=True)
class MessageEnvelope:
    schema_version: str
    message_id: str
    message_class: MessageClass
    message_type: str
    source_id: str
    source_kind: str
    created_at: datetime
    freshness: FreshnessMetadata | None
    ordering: OrderingMetadata
    integrity: IntegrityMetadata
    payload: dict[str, Any] | ControlPayload
    causality: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.schema_version.strip():
            raise ValueError("schema_version must not be empty")
        if not self.message_id.strip():
            raise ValueError("message_id must not be empty")
        if not self.message_type.strip():
            raise ValueError("message_type must not be empty")
        if not self.source_id.strip():
            raise ValueError("source_id must not be empty")
        if not self.source_kind.strip():
            raise ValueError("source_kind must not be empty")
        if self.message_class is MessageClass.CONTROL and self.freshness is None:
            raise ValueError("CONTROL messages require freshness metadata")

    def as_dict(self) -> dict[str, Any]:
        return _primitive(self)


@dataclass(slots=True)
class DecisionReceiptPayload:
    decision_id: str
    candidate_action_summary: dict[str, Any]
    final_outcome: ArbitrationOutcome
    final_authoritative_source: CommandSource
    mission_phase: MissionPhase
    safety_posture: SafetyPosture
    policy_evaluation_result: str
    rationale_summary: str
    active_degradation_flags: list[str] = field(default_factory=list)
    trust_posture_summary: dict[str, str] = field(default_factory=dict)
    related_fault_ids: list[str] = field(default_factory=list)
    triggered_constraint_ids: list[str] = field(default_factory=list)
    recovery_gate_result: str = "NOT_APPLICABLE"
    command_delta: dict[str, Any] = field(default_factory=dict)
    mode_escalation_requested: bool = False
    resulting_mode_target: str | None = None

    def __post_init__(self) -> None:
        if not self.decision_id.strip():
            raise ValueError("decision_id must not be empty")
        if not self.rationale_summary.strip():
            raise ValueError("rationale_summary must not be empty")
        if not self.candidate_action_summary:
            raise ValueError("candidate_action_summary must not be empty")

    def as_dict(self) -> dict[str, Any]:
        return _primitive(self)
