from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from typing import Any

from ix_style.core import (
    ArbitrationOutcome,
    AuthState,
    CommandSource,
    ControlPayload,
    FreshnessMetadata,
    FreshnessState,
    FunctionClass,
    IntegrityMetadata,
    IntegrityState,
    MessageClass,
    MessageEnvelope,
    MissionPhase,
    OrderingMetadata,
    ReplayState,
    SafetyPosture,
)
from ix_style.fdir import FDIRSignal, FaultClass, FaultSeverity
from ix_style.telemetry import MissionHealthBuilder
from ix_style.verification import (
    ScenarioRunner,
    VerificationExpectation,
    VerificationScenario,
)


def _now() -> datetime:
    return datetime.now(tz=UTC)


def _serialize(value: Any) -> Any:
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_serialize(item) for item in value]
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    return value


def main() -> None:
    now = _now()
    envelope = MessageEnvelope(
        schema_version="0.1.0",
        message_id="MSG-EXAMPLE-POWER-000001",
        message_class=MessageClass.CONTROL,
        message_type="control.actuation_request",
        source_id="nominal.autonomy.demo",
        source_kind="nominal_autonomy",
        created_at=now,
        freshness=FreshnessMetadata(
            issued_at=now,
            expires_at=now + timedelta(seconds=5),
            freshness_state=FreshnessState.FRESH,
        ),
        ordering=OrderingMetadata(
            sequence_number=1,
            session_id="SES-EXAMPLE-POWER-000001",
            replay_state=ReplayState.ACCEPTABLE,
        ),
        integrity=IntegrityMetadata(
            integrity_state=IntegrityState.INTEGRITY_VALID,
            auth_state=AuthState.INTEGRITY_VALID,
        ),
        payload=ControlPayload(
            function_class=FunctionClass.ACTUATION_REQUEST,
            requested_action="perform_demo_maneuver",
            command_source=CommandSource.NOMINAL_AUTONOMY,
            policy_context={"override_requested": False},
            requested_scope="vehicle.primary",
            requested_magnitude=1.0,
            requested_duration_ms=150,
            rationale_summary="demo maneuver under power fault clamp",
        ),
    )

    scenario = VerificationScenario(
        scenario_id="EXAMPLE-POWER-CLAMP-001",
        name="power fault clamp demo",
        purpose="demonstrate evidence and mission-health output under power/resource degradation",
        linked_requirements=("IXS-SYS-059",),
        linked_hazards=("IXS-HZ-006",),
        envelope=envelope,
        mission_phase=MissionPhase.ACTIVE,
        safety_posture=SafetyPosture.NOMINAL,
        fault_signals=(
            FDIRSignal(
                fault_class=FaultClass.POWER_RESOURCE_FAULT,
                detection_source="resource_monitor",
                affected_function_scope="actuation_budget",
                observed_at=_now(),
                anomaly_active=True,
                severity_estimate=FaultSeverity.CRITICAL,
            ),
        ),
        expectations=VerificationExpectation(
            expected_final_outcome=ArbitrationOutcome.CLAMP,
            require_fault_transition=True,
            required_active_degradation_flags=("power_margin_low",),
        ),
    )

    runner = ScenarioRunner()
    result = runner.run(scenario)
    snapshot = MissionHealthBuilder().build_from_verification(result)

    output = {
        "passed": result.passed,
        "failures": list(result.failures),
        "evidence_package": _serialize(asdict(result.evidence_package)),
        "mission_health_snapshot": snapshot,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
