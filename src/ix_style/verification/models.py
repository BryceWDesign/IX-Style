"""Verification scenario and evidence-package models for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ix_style.core.enums import ArbitrationOutcome, MissionPhase, SafetyPosture
from ix_style.core.models import MessageEnvelope
from ix_style.fdir.models import FDIRSignal, FaultRecord
from ix_style.trust.models import TrustCheckInput, TrustRecord


@dataclass(slots=True, frozen=True)
class VerificationExpectation:
    """Expected outcomes for one executable verification scenario."""

    expected_final_outcome: ArbitrationOutcome | None = None
    require_trust_transition: bool = False
    require_fault_transition: bool = False
    required_active_degradation_flags: tuple[str, ...] = ()
    required_receipt_fields: tuple[str, ...] = (
        "decision_id",
        "final_outcome",
        "rationale_summary",
    )


@dataclass(slots=True, frozen=True)
class VerificationScenario:
    """Executable verification scenario definition."""

    scenario_id: str
    name: str
    purpose: str
    linked_requirements: tuple[str, ...]
    linked_hazards: tuple[str, ...]
    envelope: MessageEnvelope
    mission_phase: MissionPhase
    safety_posture: SafetyPosture
    trust_checks: tuple[TrustCheckInput, ...] = ()
    fault_signals: tuple[FDIRSignal, ...] = ()
    active_degradation_flags: tuple[str, ...] = ()
    expectations: VerificationExpectation = VerificationExpectation()
    limitations_or_assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.scenario_id.strip():
            raise ValueError("scenario_id must not be empty")
        if not self.name.strip():
            raise ValueError("name must not be empty")
        if not self.purpose.strip():
            raise ValueError("purpose must not be empty")


@dataclass(slots=True, frozen=True)
class EvidencePackage:
    """Structured evidence package emitted after one scenario execution."""

    scenario_id: str
    scenario_name: str
    linked_requirements: tuple[str, ...]
    linked_hazards: tuple[str, ...]
    generated_event_ids: tuple[str, ...]
    generated_receipt_ids: tuple[str, ...]
    expected_outcomes: dict[str, Any]
    actual_observed_outcomes: dict[str, Any]
    decision_receipt: dict[str, Any]
    trust_transitions: tuple[dict[str, Any], ...] = ()
    fault_transitions: tuple[dict[str, Any], ...] = ()
    mode_transitions: tuple[dict[str, Any], ...] = ()
    evidence_bundle: dict[str, Any] = field(default_factory=dict)
    pass_fail_result: bool = False
    rationale: str = ""
    limitations_or_assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.scenario_id.strip():
            raise ValueError("scenario_id must not be empty")
        if not self.scenario_name.strip():
            raise ValueError("scenario_name must not be empty")


@dataclass(slots=True, frozen=True)
class VerificationResult:
    """Result returned by the executable scenario runner."""

    scenario: VerificationScenario
    evidence_package: EvidencePackage
    passed: bool
    failures: tuple[str, ...]
    derived_active_degradation_flags: tuple[str, ...]
    derived_dominant_safety_posture: SafetyPosture = SafetyPosture.NOMINAL
    trust_records: dict[str, TrustRecord] = field(default_factory=dict)
    fault_records: dict[str, FaultRecord] = field(default_factory=dict)
