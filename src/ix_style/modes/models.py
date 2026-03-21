"""Executable mode-allocation models for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from ix_style.core.enums import SafetyPosture
from ix_style.fdir.models import FaultRecord
from ix_style.trust.models import TrustRecord


def utc_now() -> datetime:
    """Return an aware UTC timestamp."""
    return datetime.now(tz=UTC)


@dataclass(slots=True, frozen=True)
class ModeAllocationInput:
    """Inputs needed to resolve the dominant safety posture."""

    base_posture: SafetyPosture
    active_degradation_flags: tuple[str, ...] = ()
    trust_records: dict[str, TrustRecord] = field(default_factory=dict)
    fault_records: dict[str, FaultRecord] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ModeTransition:
    """Machine-readable dominant posture transition."""

    previous_posture: SafetyPosture
    new_posture: SafetyPosture
    transition_time: datetime
    cause_codes: tuple[str, ...] = ()
    contributing_fault_ids: tuple[str, ...] = ()
    contributing_trust_record_ids: tuple[str, ...] = ()
    rationale_summary: str = ""

    def __post_init__(self) -> None:
        if not self.rationale_summary.strip():
            raise ValueError("rationale_summary must not be empty")


@dataclass(slots=True, frozen=True)
class ModeAllocationResult:
    """Resolved dominant posture and optional transition record."""

    dominant_posture: SafetyPosture
    transition: ModeTransition | None
    rationale_summary: str
    active_degradation_flags: tuple[str, ...] = ()
    contributing_fault_ids: tuple[str, ...] = ()
    contributing_trust_record_ids: tuple[str, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.rationale_summary.strip():
            raise ValueError("rationale_summary must not be empty")
