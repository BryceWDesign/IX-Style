"""Executable trust models for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from ix_style.core.enums import (
    FreshnessState,
    IntegrityState,
    TrustDomain,
    TrustState,
)


def utc_now() -> datetime:
    """Return an aware UTC timestamp."""
    return datetime.now(tz=UTC)


@dataclass(slots=True, frozen=True)
class TrustCheckInput:
    """Inputs used to evaluate one trust-bearing entity."""

    trust_domain: TrustDomain
    entity_id: str
    observed_at: datetime
    source_available: bool = True
    freshness_state: FreshnessState = FreshnessState.FRESH
    integrity_state: IntegrityState | None = None
    plausibility_ok: bool = True
    cross_consistency_ok: bool | None = None
    continuity_ok: bool | None = None
    recovery_requested: bool = False
    cause_codes: tuple[str, ...] = ()
    rationale_hint: str | None = None

    def __post_init__(self) -> None:
        if not self.entity_id.strip():
            raise ValueError("entity_id must not be empty")


@dataclass(slots=True, frozen=True)
class TrustRecord:
    """Persistent trust state for one source or derived entity."""

    trust_record_id: str
    trust_domain: TrustDomain
    entity_id: str
    current_trust_state: TrustState
    numeric_trust_score: float
    last_transition_timestamp: datetime
    transition_cause_codes: tuple[str, ...] = ()
    degradation_streak: int = 0
    recovery_streak: int = 0
    posture_driving: bool = False
    evidence_required: bool = False
    rationale_summary: str = "initial trust state established"

    def __post_init__(self) -> None:
        if not self.trust_record_id.strip():
            raise ValueError("trust_record_id must not be empty")
        if not self.entity_id.strip():
            raise ValueError("entity_id must not be empty")
        if not 0.0 <= self.numeric_trust_score <= 1.0:
            raise ValueError("numeric_trust_score must be between 0.0 and 1.0")
        if self.degradation_streak < 0:
            raise ValueError("degradation_streak must be non-negative")
        if self.recovery_streak < 0:
            raise ValueError("recovery_streak must be non-negative")


@dataclass(slots=True, frozen=True)
class TrustTransition:
    """Machine-readable trust-state change record."""

    trust_record_id: str
    affected_domain: TrustDomain
    affected_entity_id: str
    previous_trust_state: TrustState
    new_trust_state: TrustState
    transition_time: datetime
    cause_codes: tuple[str, ...] = ()
    rationale_summary: str = ""
    posture_driving: bool = False

    def __post_init__(self) -> None:
        if not self.trust_record_id.strip():
            raise ValueError("trust_record_id must not be empty")
        if not self.affected_entity_id.strip():
            raise ValueError("affected_entity_id must not be empty")


@dataclass(slots=True, frozen=True)
class TrustEvaluationResult:
    """Result of one trust evaluation pass."""

    record: TrustRecord
    transition: TrustTransition | None
    rationale_summary: str
    auto_generated_record: bool = False
    negative_evidence_present: bool = False
    metadata: dict[str, str] = field(default_factory=dict)
