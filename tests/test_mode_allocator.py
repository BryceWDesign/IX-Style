from __future__ import annotations

from datetime import UTC, datetime

from ix_style.core.enums import FaultLifecycleState, SafetyPosture, TrustDomain, TrustState
from ix_style.fdir import (
    FaultClass,
    FaultIsolationConfidence,
    FaultPriority,
    FaultRecord,
    FaultSeverity,
)
from ix_style.modes import ModeAllocationInput, ModeAllocator
from ix_style.trust import TrustRecord


def _now() -> datetime:
    return datetime.now(tz=UTC)


def test_nav_trust_record_drives_nav_degraded_posture() -> None:
    allocator = ModeAllocator()
    trust_record = TrustRecord(
        trust_record_id="TR-TEST-000001",
        trust_domain=TrustDomain.NAVIGATION_TRUST,
        entity_id="nav.primary",
        current_trust_state=TrustState.UNTRUSTED,
        numeric_trust_score=0.1,
        last_transition_timestamp=_now(),
        transition_cause_codes=("TRUST_CAUSE_NAV_SPOOF_SUSPECTED",),
        posture_driving=True,
        evidence_required=True,
        rationale_summary="navigation trust collapsed",
    )

    result = allocator.evaluate(
        ModeAllocationInput(
            base_posture=SafetyPosture.NOMINAL,
            trust_records={"nav.primary": trust_record},
        )
    )

    assert result.dominant_posture is SafetyPosture.NAV_DEGRADED
    assert result.transition is not None
    assert "TR-TEST-000001" in result.contributing_trust_record_ids


def test_contained_p1_fault_escalates_to_safe_hold() -> None:
    allocator = ModeAllocator()
    fault_record = FaultRecord(
        fault_id="FLT-TEST-000001",
        fault_class=FaultClass.ASSURANCE_FAULT,
        lifecycle_state=FaultLifecycleState.CONTAINED,
        detection_source="guard_health_monitor",
        first_detected_timestamp=_now(),
        latest_update_timestamp=_now(),
        affected_function_scope="runtime_assurance",
        severity_estimate=FaultSeverity.CRITICAL,
        confirmation_confidence=0.9,
        isolation_confidence=FaultIsolationConfidence.HIGH,
        active_mitigation_set=(),
        current_priority=FaultPriority.P1_CONTAINMENT_CRITICAL,
        latch_status=False,
        recovery_gate_status="NOT_APPLICABLE",
        rationale_summary="containment-critical assurance fault remains active",
        occurrence_count=2,
        corroborated_count=2,
    )

    result = allocator.evaluate(
        ModeAllocationInput(
            base_posture=SafetyPosture.NOMINAL,
            fault_records={"fault": fault_record},
        )
    )

    assert result.dominant_posture is SafetyPosture.SAFE_HOLD
    assert result.transition is not None
    assert "FLT-TEST-000001" in result.contributing_fault_ids


def test_power_flag_outweighs_comms_flag_by_precedence() -> None:
    allocator = ModeAllocator()

    result = allocator.evaluate(
        ModeAllocationInput(
            base_posture=SafetyPosture.NOMINAL,
            active_degradation_flags=("comms_link_intermittent", "power_margin_low"),
        )
    )

    assert result.dominant_posture is SafetyPosture.POWER_DEGRADED
    assert result.transition is not None
