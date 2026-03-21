from __future__ import annotations

from datetime import UTC, datetime, timedelta

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
    TrustDomain,
)
from ix_style.fdir import FDIRSignal, FaultClass, FaultSeverity
from ix_style.messages import MISSION_HEALTH_SNAPSHOT_SCHEMA, SchemaValidator
from ix_style.telemetry import MissionHealthBuilder
from ix_style.trust import TRUST_CAUSE_NAV_SPOOF_SUSPECTED, TrustCheckInput
from ix_style.verification import (
    ScenarioRunner,
    VerificationExpectation,
    VerificationScenario,
)


def _now() -> datetime:
    return datetime.now(tz=UTC)


def _make_control_envelope(
    *,
    command_source: CommandSource,
    function_class: FunctionClass,
) -> MessageEnvelope:
    now = _now()
    return MessageEnvelope(
        schema_version="0.1.0",
        message_id="MSG-TEST-MISSION-HEALTH-000001",
        message_class=MessageClass.CONTROL,
        message_type="control.actuation_request",
        source_id="scenario-source",
        source_kind="nominal_autonomy",
        created_at=now,
        freshness=FreshnessMetadata(
            issued_at=now,
            expires_at=now + timedelta(seconds=5),
            freshness_state=FreshnessState.FRESH,
        ),
        ordering=OrderingMetadata(
            sequence_number=1,
            session_id="SES-TEST-MISSION-HEALTH-000001",
            replay_state=ReplayState.ACCEPTABLE,
        ),
        integrity=IntegrityMetadata(
            integrity_state=IntegrityState.INTEGRITY_VALID,
            auth_state=AuthState.INTEGRITY_VALID,
        ),
        payload=ControlPayload(
            function_class=function_class,
            requested_action="perform_test_action",
            command_source=command_source,
            policy_context={"override_requested": False},
            requested_magnitude=1.0,
            requested_duration_ms=100,
        ),
    )


def test_power_fault_scenario_builds_valid_power_degraded_snapshot() -> None:
    runner = ScenarioRunner()
    scenario = VerificationScenario(
        scenario_id="TEST-MISSION-HEALTH-POWER-001",
        name="power-degraded mission-health snapshot",
        purpose="verify that mission-health reflects resource degradation and clamp behavior",
        linked_requirements=("IXS-SYS-059",),
        linked_hazards=("IXS-HZ-006",),
        envelope=_make_control_envelope(
            command_source=CommandSource.NOMINAL_AUTONOMY,
            function_class=FunctionClass.ACTUATION_REQUEST,
        ),
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

    result = runner.run(scenario)
    snapshot = MissionHealthBuilder().build_from_verification(result)

    validator = SchemaValidator()
    errors = validator.validate(MISSION_HEALTH_SNAPSHOT_SCHEMA, snapshot)

    assert errors == ()
    assert snapshot["dominant_safety_posture"] == "POWER_DEGRADED"
    assert snapshot["resource_summary"]["load_shed_active"] is True
    assert snapshot["authority_summary"]["safety_supervisor_bias"] == "ELEVATED"


def test_nav_spoof_scenario_builds_valid_nav_degraded_snapshot() -> None:
    runner = ScenarioRunner()
    scenario = VerificationScenario(
        scenario_id="TEST-MISSION-HEALTH-NAV-001",
        name="nav-degraded mission-health snapshot",
        purpose="verify that mission-health reflects navigation trust collapse",
        linked_requirements=("IXS-SYS-015",),
        linked_hazards=("IXS-HZ-003",),
        envelope=_make_control_envelope(
            command_source=CommandSource.OPERATOR,
            function_class=FunctionClass.MODE_MANAGEMENT,
        ),
        mission_phase=MissionPhase.ACTIVE,
        safety_posture=SafetyPosture.NOMINAL,
        trust_checks=(
            TrustCheckInput(
                trust_domain=TrustDomain.NAVIGATION_TRUST,
                entity_id="nav.primary",
                observed_at=_now(),
                cause_codes=(TRUST_CAUSE_NAV_SPOOF_SUSPECTED,),
            ),
        ),
        expectations=VerificationExpectation(
            expected_final_outcome=ArbitrationOutcome.ACCEPT,
            require_trust_transition=True,
            required_active_degradation_flags=("nav_spoof_suspected",),
        ),
    )

    result = runner.run(scenario)
    snapshot = MissionHealthBuilder().build_from_verification(result)

    validator = SchemaValidator()
    errors = validator.validate(MISSION_HEALTH_SNAPSHOT_SCHEMA, snapshot)

    assert errors == ()
    assert snapshot["dominant_safety_posture"] == "NAV_DEGRADED"
    assert snapshot["trust_summary"]["navigation_trust"] == "UNTRUSTED"
    assert len(snapshot["recent_events"]) >= 2
