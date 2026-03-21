from __future__ import annotations

from datetime import UTC, datetime, timedelta

from ix_style.core import (
    ArbitrationOutcome,
    AuthState,
    CommandSource,
    ControlPayload,
    DecisionPipeline,
    DecisionPipelineContext,
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


def _now() -> datetime:
    return datetime.now(tz=UTC)


def _make_control_envelope(
    *,
    command_source: CommandSource,
    function_class: FunctionClass,
    requested_action: str = "perform_bounded_action",
) -> MessageEnvelope:
    now = _now()
    return MessageEnvelope(
        schema_version="0.1.0",
        message_id="MSG-TEST-CONSTRAINT-000001",
        message_class=MessageClass.CONTROL,
        message_type="control.actuation_request",
        source_id="test.source",
        source_kind="nominal_autonomy",
        created_at=now,
        freshness=FreshnessMetadata(
            issued_at=now,
            expires_at=now + timedelta(seconds=5),
            freshness_state=FreshnessState.FRESH,
        ),
        ordering=OrderingMetadata(
            sequence_number=1,
            session_id="SES-TEST-CONSTRAINT-000001",
            replay_state=ReplayState.ACCEPTABLE,
        ),
        integrity=IntegrityMetadata(
            integrity_state=IntegrityState.INTEGRITY_VALID,
            auth_state=AuthState.INTEGRITY_VALID,
        ),
        payload=ControlPayload(
            function_class=function_class,
            requested_action=requested_action,
            command_source=command_source,
            policy_context={"override_requested": False},
            requested_magnitude=1.0,
            requested_duration_ms=100,
        ),
    )


def test_nav_spoof_flag_vetoes_motion_request() -> None:
    pipeline = DecisionPipeline()
    envelope = _make_control_envelope(
        command_source=CommandSource.NOMINAL_AUTONOMY,
        function_class=FunctionClass.ACTUATION_REQUEST,
    )
    context = DecisionPipelineContext(
        envelope=envelope,
        mission_phase=MissionPhase.ACTIVE,
        safety_posture=SafetyPosture.NOMINAL,
        active_degradation_flags=("nav_spoof_suspected",),
    )

    result = pipeline.evaluate(context)

    assert result.guard_decision is not None
    assert result.guard_decision.outcome is ArbitrationOutcome.VETO
    assert "IXS-CONSTRAINT-004" in result.guard_decision.triggered_constraint_ids
    assert result.receipt_payload.final_outcome is ArbitrationOutcome.VETO


def test_sensor_trust_low_clamps_motion_request() -> None:
    pipeline = DecisionPipeline()
    envelope = _make_control_envelope(
        command_source=CommandSource.NOMINAL_AUTONOMY,
        function_class=FunctionClass.GUIDANCE_REQUEST,
    )
    context = DecisionPipelineContext(
        envelope=envelope,
        mission_phase=MissionPhase.ACTIVE,
        safety_posture=SafetyPosture.NOMINAL,
        active_degradation_flags=("sensor_trust_low",),
    )

    result = pipeline.evaluate(context)

    assert result.guard_decision is not None
    assert result.guard_decision.outcome is ArbitrationOutcome.CLAMP
    assert "IXS-CONSTRAINT-006" in result.guard_decision.triggered_constraint_ids
    assert result.receipt_payload.final_outcome is ArbitrationOutcome.CLAMP


def test_operator_recovery_action_is_deferred_under_comms_degradation() -> None:
    pipeline = DecisionPipeline()
    envelope = _make_control_envelope(
        command_source=CommandSource.OPERATOR,
        function_class=FunctionClass.RECOVERY_ACTION,
        requested_action="request_recovery_review",
    )
    context = DecisionPipelineContext(
        envelope=envelope,
        mission_phase=MissionPhase.ACTIVE,
        safety_posture=SafetyPosture.COMMS_DEGRADED,
        active_degradation_flags=("comms_link_intermittent",),
    )

    result = pipeline.evaluate(context)

    assert result.guard_decision is not None
    assert result.guard_decision.outcome is ArbitrationOutcome.DEFER
    assert "IXS-CONSTRAINT-008" in result.guard_decision.triggered_constraint_ids
    assert result.receipt_payload.final_outcome is ArbitrationOutcome.DEFER
    assert result.receipt_payload.recovery_gate_result == "DEFERRED"
