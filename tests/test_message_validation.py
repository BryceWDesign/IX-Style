from __future__ import annotations

from datetime import UTC, datetime, timedelta

from ix_style.core import (
    ArbitrationOutcome,
    AuthState,
    CommandSource,
    ControlPayload,
    DecisionReceiptPayload,
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
from ix_style.messages import (
    CONTROL_MESSAGE_SCHEMA,
    DECISION_RECEIPT_SCHEMA,
    DecisionReceiptBuilder,
    SchemaValidator,
)


def _now() -> datetime:
    return datetime.now(tz=UTC)


def test_control_message_validates_against_schema() -> None:
    now = _now()
    envelope = MessageEnvelope(
        schema_version="0.1.0",
        message_id="MSG-TEST-VALIDATE-000001",
        message_class=MessageClass.CONTROL,
        message_type="control.actuation_request",
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
            session_id="SES-TEST-VALIDATE-000001",
            replay_state=ReplayState.ACCEPTABLE,
        ),
        integrity=IntegrityMetadata(
            integrity_state=IntegrityState.INTEGRITY_VALID,
            auth_state=AuthState.INTEGRITY_VALID,
        ),
        payload=ControlPayload(
            function_class=FunctionClass.ACTUATION_REQUEST,
            requested_action="perform_bounded_action",
            command_source=CommandSource.OPERATOR,
            policy_context={"override_requested": False},
            requested_scope="vehicle.primary",
            requested_magnitude=1.0,
            requested_rate=0.5,
            requested_duration_ms=100,
            rationale_summary="bounded test action",
        ),
    )

    validator = SchemaValidator()
    errors = validator.validate(CONTROL_MESSAGE_SCHEMA, envelope.as_dict())

    assert errors == ()


def test_decision_receipt_builder_emits_schema_valid_document() -> None:
    payload = DecisionReceiptPayload(
        decision_id="DEC-TEST-000001",
        candidate_action_summary={
            "function_class": "ACTUATION_REQUEST",
            "requested_action": "perform_bounded_action",
            "requested_by": "OPERATOR",
            "requested_scope": "vehicle.primary",
            "requested_magnitude": 1.0,
            "requested_duration_ms": 100,
        },
        final_outcome=ArbitrationOutcome.CLAMP,
        final_authoritative_source=CommandSource.SAFETY_SUPERVISOR,
        mission_phase=MissionPhase.ACTIVE,
        safety_posture=SafetyPosture.POWER_DEGRADED,
        active_degradation_flags=["power_margin_low"],
        trust_posture_summary={"actuator_confidence": "TRUSTED"},
        related_fault_ids=["FLT-TEST-000001"],
        triggered_constraint_ids=["RESOURCE-POWER-MARGIN-CLAMP"],
        policy_evaluation_result="CONDITIONALLY_ALLOWED",
        recovery_gate_result="NOT_APPLICABLE",
        command_delta={
            "change_type": "CLAMPED",
            "original_summary": "perform_bounded_action",
            "final_summary": "reduced bounded action",
        },
        mode_escalation_requested=False,
        rationale_summary="power-margin degradation narrows the requested action",
    )

    document = DecisionReceiptBuilder().build(
        payload=payload,
        session_id="SES-TEST-RECEIPT-000001",
        sequence_number=7,
    )

    validator = SchemaValidator()
    errors = validator.validate(DECISION_RECEIPT_SCHEMA, document)

    assert errors == ()
    assert document["message_class"] == "EVIDENCE"
    assert document["message_type"] == "evidence.decision_receipt"
