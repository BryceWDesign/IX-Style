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
    freshness_state: FreshnessState = FreshnessState.FRESH,
) -> MessageEnvelope:
    now = _now()
    return MessageEnvelope(
        schema_version="0.1.0",
        message_id="MSG-TEST-000001",
        message_class=MessageClass.CONTROL,
        message_type="control.actuation_request",
        source_id="nominal-autonomy",
        source_kind="nominal_autonomy",
        created_at=now,
        freshness=FreshnessMetadata(
            issued_at=now,
            expires_at=now + timedelta(seconds=5),
            freshness_state=freshness_state,
        ),
        ordering=OrderingMetadata(
            sequence_number=1,
            session_id="SES-TEST-000001",
            replay_state=ReplayState.ACCEPTABLE,
        ),
        integrity=IntegrityMetadata(
            integrity_state=IntegrityState.INTEGRITY_VALID,
            auth_state=AuthState.INTEGRITY_VALID,
        ),
        payload=ControlPayload(
            function_class=function_class,
            requested_action="perform_bounded_action",
            command_source=command_source,
            policy_context={"override_requested": False},
            requested_magnitude=1.0,
            requested_duration_ms=100,
        ),
    )


def test_stale_control_message_is_rejected_by_authority_stage() -> None:
    pipeline = DecisionPipeline()
    envelope = _make_control_envelope(
        command_source=CommandSource.OPERATOR,
        function_class=FunctionClass.MODE_MANAGEMENT,
        freshness_state=FreshnessState.STALE,
    )
    context = DecisionPipelineContext(
        envelope=envelope,
        mission_phase=MissionPhase.ACTIVE,
        safety_posture=SafetyPosture.NOMINAL,
    )

    result = pipeline.evaluate(context)

    assert result.authority_decision.outcome is ArbitrationOutcome.REJECT
    assert result.guard_decision is None
    assert result.receipt_payload.final_outcome is ArbitrationOutcome.REJECT
    assert result.receipt_payload.final_authoritative_source is CommandSource.NONE


def test_safe_hold_vetoes_mission_progress_actuation() -> None:
    pipeline = DecisionPipeline()
    envelope = _make_control_envelope(
        command_source=CommandSource.NOMINAL_AUTONOMY,
        function_class=FunctionClass.ACTUATION_REQUEST,
    )
    context = DecisionPipelineContext(
        envelope=envelope,
        mission_phase=MissionPhase.ACTIVE,
        safety_posture=SafetyPosture.SAFE_HOLD,
    )

    result = pipeline.evaluate(context)

    assert result.authority_decision.outcome is ArbitrationOutcome.ACCEPT
    assert result.guard_decision is not None
    assert result.guard_decision.outcome is ArbitrationOutcome.VETO
    assert result.receipt_payload.final_outcome is ArbitrationOutcome.VETO
    assert result.receipt_payload.final_authoritative_source is CommandSource.SAFETY_SUPERVISOR


def test_nominal_operator_mode_request_can_pass_pipeline() -> None:
    pipeline = DecisionPipeline()
    envelope = _make_control_envelope(
        command_source=CommandSource.OPERATOR,
        function_class=FunctionClass.MODE_MANAGEMENT,
    )
    context = DecisionPipelineContext(
        envelope=envelope,
        mission_phase=MissionPhase.ACTIVE,
        safety_posture=SafetyPosture.NOMINAL,
    )

    result = pipeline.evaluate(context)

    assert result.authority_decision.outcome is ArbitrationOutcome.ACCEPT
    assert result.guard_decision is not None
    assert result.guard_decision.outcome is ArbitrationOutcome.ACCEPT
    assert result.receipt_payload.final_outcome is ArbitrationOutcome.ACCEPT
    assert result.receipt_payload.final_authoritative_source is CommandSource.OPERATOR
