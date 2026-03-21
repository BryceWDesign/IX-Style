from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta

from ix_style.core import (
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
from ix_style.verification import (
    InvariantChecker,
    ScenarioRunner,
    VerificationExpectation,
    VerificationScenario,
    build_nav_spoof_transition_scenario,
    build_power_fault_clamp_scenario,
    build_recovery_deferred_scenario,
)


def _now() -> datetime:
    return datetime.now(tz=UTC)


def _make_operator_recovery_scenario_with_weak_comms() -> VerificationScenario:
    now = _now()
    envelope = MessageEnvelope(
        schema_version="0.1.0",
        message_id="MSG-INV-RECOVERY-000001",
        message_class=MessageClass.CONTROL,
        message_type="control.recovery_action_request",
        source_id="operator.console",
        source_kind="operator",
        created_at=now,
        freshness=FreshnessMetadata(
            issued_at=now,
            expires_at=now + timedelta(seconds=5),
            freshness_state=FreshnessState.FRESH,
        ),
        ordering=OrderingMetadata(
            sequence_number=1,
            session_id="SES-INV-RECOVERY-000001",
            replay_state=ReplayState.ACCEPTABLE,
        ),
        integrity=IntegrityMetadata(
            integrity_state=IntegrityState.INTEGRITY_VALID,
            auth_state=AuthState.INTEGRITY_VALID,
        ),
        payload=ControlPayload(
            function_class=FunctionClass.RECOVERY_ACTION,
            requested_action="request_recovery_review",
            command_source=CommandSource.OPERATOR,
            policy_context={"override_requested": False},
            requested_scope="vehicle.primary",
            requested_duration_ms=100,
        ),
    )
    return VerificationScenario(
        scenario_id="TEST-INV-RECOVERY-000001",
        name="recovery invariant scenario",
        purpose="exercise recovery-gate invariants under weak comms",
        linked_requirements=("IXS-SYS-034",),
        linked_hazards=("IXS-HZ-010",),
        envelope=envelope,
        mission_phase=MissionPhase.ACTIVE,
        safety_posture=SafetyPosture.COMMS_DEGRADED,
        active_degradation_flags=("comms_link_intermittent",),
        expectations=VerificationExpectation(
            required_active_degradation_flags=("comms_link_intermittent",),
        ),
    )


def test_invariant_checker_passes_power_fault_scenario() -> None:
    result = ScenarioRunner().run(build_power_fault_clamp_scenario())
    report = InvariantChecker().evaluate(result)

    assert result.passed is True
    assert report.passed is True
    assert all(check.passed for check in report.checks)


def test_invariant_checker_passes_nav_spoof_scenario() -> None:
    result = ScenarioRunner().run(build_nav_spoof_transition_scenario())
    report = InvariantChecker().evaluate(result)

    assert result.passed is True
    assert report.passed is True
    assert all(check.passed for check in report.checks)


def test_invariant_checker_passes_recovery_deferred_scenario() -> None:
    result = ScenarioRunner().run(build_recovery_deferred_scenario())
    report = InvariantChecker().evaluate(result)

    assert result.passed is True
    assert report.passed is True
    assert all(check.passed for check in report.checks)
    assert result.pipeline_trace["recovery_gate_status"] == "DEFERRED"


def test_invariant_checker_detects_tampered_bundle() -> None:
    result = ScenarioRunner().run(build_power_fault_clamp_scenario())
    tampered_bundle = dict(result.evidence_package.evidence_bundle)
    tampered_items = list(tampered_bundle["items"])
    tampered_items[0] = dict(tampered_items[0])
    tampered_items[0]["data"] = dict(tampered_items[0]["data"])
    tampered_items[0]["data"]["rationale_summary"] = "tampered after export"
    tampered_bundle["items"] = tampered_items

    tampered_evidence = replace(result.evidence_package, evidence_bundle=tampered_bundle)
    tampered_result = replace(result, evidence_package=tampered_evidence)

    report = InvariantChecker().evaluate(tampered_result)

    assert report.passed is False
    assert any(check.invariant_id == "IXS-INV-006" and not check.passed for check in report.checks)


def test_recovery_gate_invariant_shows_no_authority_progression_after_deferral() -> None:
    result = ScenarioRunner().run(_make_operator_recovery_scenario_with_weak_comms())
    report = InvariantChecker().evaluate(result)

    assert result.pipeline_trace["recovery_gate_status"] == "DEFERRED"
    assert result.pipeline_trace["authority_decision_present"] is False
    assert result.pipeline_trace["guard_decision_present"] is False
    assert report.passed is True
