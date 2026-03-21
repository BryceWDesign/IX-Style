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
    freshness_state: FreshnessState = FreshnessState.FRESH,
) -> MessageEnvelope:
    now = _now()
    return MessageEnvelope(
        schema_version="0.1.0",
        message_id="MSG-VERIFY-000001",
        message_class=MessageClass.CONTROL,
        message_type="control.actuation_request",
        source_id="scenario-source",
        source_kind="nominal_autonomy",
        created_at=now,
        freshness=FreshnessMetadata(
            issued_at=now,
            expires_at=now + timedelta(seconds=5),
            freshness_state=freshness_state,
        ),
        ordering=OrderingMetadata(
            sequence_number=1,
            session_id="SES-VERIFY-000001",
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


def test_runner_builds_passing_evidence_package_for_power_fault_clamp() -> None:
    runner = ScenarioRunner()
    scenario = VerificationScenario(
        scenario_id="TEST-RESOURCE-EXEC-001",
        name="power fault clamps actuation request",
        purpose="verify that active power/resource degradation narrows mission-progress behavior",
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

    assert result.passed is True
    assert result.evidence_package.pass_fail_result is True
    assert result.evidence_package.decision_receipt["final_outcome"] == "CLAMP"
    assert "power_margin_low" in result.derived_active_degradation_flags
    assert len(result.evidence_package.fault_transitions) == 1


def test_runner_tracks_navigation_trust_transition_even_when_command_is_allowed() -> None:
    runner = ScenarioRunner()
    scenario = VerificationScenario(
        scenario_id="TEST-TRUST-EXEC-001",
        name="navigation spoof suspicion creates trust transition",
        purpose="verify trust transition evidence and derived nav degradation flags",
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

    assert result.passed is True
    assert result.evidence_package.pass_fail_result is True
    assert result.evidence_package.decision_receipt["final_outcome"] == "ACCEPT"
    assert "nav_spoof_suspected" in result.derived_active_degradation_flags
    assert len(result.evidence_package.trust_transitions) == 1
