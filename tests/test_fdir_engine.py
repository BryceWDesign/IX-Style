from __future__ import annotations

from datetime import UTC, datetime

from ix_style.core.enums import FaultLifecycleState
from ix_style.fdir import (
    BasicFDIREngine,
    FDIRSignal,
    FaultClass,
    FaultPriority,
    FaultSeverity,
    MitigationCategory,
)


def _now() -> datetime:
    return datetime.now(tz=UTC)


def test_sensor_fault_progresses_from_detected_to_confirmed() -> None:
    engine = BasicFDIREngine()

    first = engine.evaluate(
        record=None,
        signal=FDIRSignal(
            fault_class=FaultClass.SENSOR_FAULT,
            detection_source="sensor_trust_monitor",
            affected_function_scope="guidance",
            observed_at=_now(),
            anomaly_active=True,
            severity_estimate=FaultSeverity.MAJOR,
        ),
    )
    assert first.record.lifecycle_state is FaultLifecycleState.DETECTED

    second = engine.evaluate(
        record=first.record,
        signal=FDIRSignal(
            fault_class=FaultClass.SENSOR_FAULT,
            detection_source="sensor_trust_monitor",
            affected_function_scope="guidance",
            observed_at=_now(),
            anomaly_active=True,
            severity_estimate=FaultSeverity.MAJOR,
        ),
    )
    assert second.record.lifecycle_state is FaultLifecycleState.SUSPECTED

    third = engine.evaluate(
        record=second.record,
        signal=FDIRSignal(
            fault_class=FaultClass.SENSOR_FAULT,
            detection_source="sensor_trust_monitor",
            affected_function_scope="guidance",
            observed_at=_now(),
            anomaly_active=True,
            corroborated=True,
            severity_estimate=FaultSeverity.MAJOR,
        ),
    )
    assert third.record.lifecycle_state is FaultLifecycleState.CONFIRMED
    assert third.transition is not None


def test_assurance_fault_can_jump_directly_to_contained() -> None:
    engine = BasicFDIREngine()

    result = engine.evaluate(
        record=None,
        signal=FDIRSignal(
            fault_class=FaultClass.ASSURANCE_FAULT,
            detection_source="guard_health_monitor",
            affected_function_scope="runtime_assurance",
            observed_at=_now(),
            anomaly_active=True,
            mitigation_requested=True,
            containment_required=True,
            severity_estimate=FaultSeverity.CRITICAL,
            authority_relevant=True,
        ),
    )

    assert result.record.lifecycle_state is FaultLifecycleState.CONTAINED
    assert result.record.current_priority is FaultPriority.P1_CONTAINMENT_CRITICAL
    assert MitigationCategory.ENTER_SAFE_HOLD in result.record.active_mitigation_set


def test_transient_detected_fault_can_clear() -> None:
    engine = BasicFDIREngine()

    active = engine.evaluate(
        record=None,
        signal=FDIRSignal(
            fault_class=FaultClass.COMMUNICATION_FAULT,
            detection_source="link_monitor",
            affected_function_scope="remote_operator_commands",
            observed_at=_now(),
            anomaly_active=True,
            severity_estimate=FaultSeverity.MINOR,
        ),
    )

    cleared = engine.evaluate(
        record=active.record,
        signal=FDIRSignal(
            fault_class=FaultClass.COMMUNICATION_FAULT,
            detection_source="link_monitor",
            affected_function_scope="remote_operator_commands",
            observed_at=_now(),
            anomaly_active=False,
            severity_estimate=FaultSeverity.MINOR,
        ),
    )

    assert active.record.lifecycle_state is FaultLifecycleState.DETECTED
    assert cleared.record.lifecycle_state is FaultLifecycleState.CLEARED


def test_contained_fault_requires_recovery_gate_before_clear() -> None:
    engine = BasicFDIREngine()

    contained = engine.evaluate(
        record=None,
        signal=FDIRSignal(
            fault_class=FaultClass.POWER_RESOURCE_FAULT,
            detection_source="resource_monitor",
            affected_function_scope="actuation_budget",
            observed_at=_now(),
            anomaly_active=True,
            mitigation_requested=True,
            containment_required=True,
            severity_estimate=FaultSeverity.CRITICAL,
        ),
    )
    assert contained.record.lifecycle_state is FaultLifecycleState.CONTAINED

    blocked = engine.evaluate(
        record=contained.record,
        signal=FDIRSignal(
            fault_class=FaultClass.POWER_RESOURCE_FAULT,
            detection_source="resource_monitor",
            affected_function_scope="actuation_budget",
            observed_at=_now(),
            anomaly_active=False,
            recovery_requested=False,
            recovery_permitted=False,
            severity_estimate=FaultSeverity.CRITICAL,
        ),
    )
    assert blocked.record.lifecycle_state is FaultLifecycleState.CONTAINED
    assert blocked.record.recovery_gate_status == "BLOCKED"

    recovering = engine.evaluate(
        record=blocked.record,
        signal=FDIRSignal(
            fault_class=FaultClass.POWER_RESOURCE_FAULT,
            detection_source="resource_monitor",
            affected_function_scope="actuation_budget",
            observed_at=_now(),
            anomaly_active=False,
            recovery_requested=True,
            recovery_permitted=True,
            severity_estimate=FaultSeverity.CRITICAL,
        ),
    )
    assert recovering.record.lifecycle_state is FaultLifecycleState.RECOVERING

    cleared = engine.evaluate(
        record=recovering.record,
        signal=FDIRSignal(
            fault_class=FaultClass.POWER_RESOURCE_FAULT,
            detection_source="resource_monitor",
            affected_function_scope="actuation_budget",
            observed_at=_now(),
            anomaly_active=False,
            recovery_requested=True,
            recovery_permitted=True,
            severity_estimate=FaultSeverity.CRITICAL,
        ),
    )
    assert cleared.record.lifecycle_state is FaultLifecycleState.CLEARED
    assert cleared.record.recovery_gate_status == "PASSED"
