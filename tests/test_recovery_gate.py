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
    TrustDomain,
)
from ix_style.recovery import RecoveryGateStatus
from ix_style.trust import TrustRecord
from ix_style.core.enums import TrustState


def _now() -> datetime:
    return datetime.now(tz=UTC)


def _make_recovery_envelope(
    *,
    command_source: CommandSource = CommandSource.OPERATOR,
) -> MessageEnvelope:
    now = _now()
    return MessageEnvelope(
        schema_version="0.1.0",
        message_id="MSG-TEST-RECOVERY-000001",
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
            session_id="SES-TEST-RECOVERY-000001",
            replay_state=ReplayState.ACCEPTABLE,
        ),
        integrity=IntegrityMetadata(
            integrity_state=IntegrityState.INTEGRITY_VALID,
            auth_state=AuthState.INTEGRITY_VALID,
        ),
        payload=ControlPayload(
            function_class=FunctionClass.RECOVERY_ACTION,
            requested_action="request_recovery_review",
            command_source=command_source,
            policy_context={"override_requested": False},
            requested_scope="vehicle.primary",
            requested_duration_ms=100,
        ),
    )


def test_recovery_action_fails_when_posture_driving_nav_trust_remains_bad() -> None:
    pipeline = DecisionPipeline()
    trust_record = TrustRecord(
        trust_record_id="TR-RECOVERY-000001",
        trust_domain=TrustDomain.NAVIGATION_TRUST,
        entity_id="nav.primary",
        current_trust_state=TrustState.UNTRUSTED,
        numeric_trust_score=0.1,
        last_transition_timestamp=_now(),
        transition_cause_codes=("TRUST_CAUSE_NAV_SPOOF_SUSPECTED",),
        posture_driving=True,
        evidence_required=True,
        rationale_summary="navigation trust remains untrusted",
    )

    result = pipeline.evaluate(
        DecisionPipelineContext(
            envelope=_make_recovery_envelope(),
            mission_phase=MissionPhase.ACTIVE,
            safety_posture=SafetyPosture.NAV_DEGRADED,
            trust_records={"nav.primary": trust_record},
        )
    )

    assert result.recovery_decision is not None
    assert result.recovery_decision.gate_status is RecoveryGateStatus.FAILED
    assert result.authority_decision is None
    assert result.guard_decision is None
    assert result.receipt_payload.final_outcome is ArbitrationOutcome.REJECT
    assert result.receipt_payload.recovery_gate_result == "FAILED"


def test_recovery_action_is_deferred_when_comms_are_weak() -> None:
    pipeline = DecisionPipeline()

    result = pipeline.evaluate(
        DecisionPipelineContext(
            envelope=_make_recovery_envelope(),
            mission_phase=MissionPhase.ACTIVE,
            safety_posture=SafetyPosture.COMMS_DEGRADED,
            active_degradation_flags=("comms_link_intermittent",),
        )
    )

    assert result.recovery_decision is not None
    assert result.recovery_decision.gate_status is RecoveryGateStatus.DEFERRED
    assert result.authority_decision is None
    assert result.guard_decision is None
    assert result.receipt_payload.final_outcome is ArbitrationOutcome.DEFER
    assert result.receipt_payload.recovery_gate_result == "DEFERRED"


def test_recovery_action_can_pass_when_no_blockers_remain() -> None:
    pipeline = DecisionPipeline()

    result = pipeline.evaluate(
        DecisionPipelineContext(
            envelope=_make_recovery_envelope(),
            mission_phase=MissionPhase.ACTIVE,
            safety_posture=SafetyPosture.SENSOR_DEGRADED,
        )
    )

    assert result.recovery_decision is not None
    assert result.recovery_decision.gate_status is RecoveryGateStatus.PASSED
    assert result.authority_decision is not None
    assert result.guard_decision is not None
    assert result.receipt_payload.final_outcome is ArbitrationOutcome.ACCEPT
    assert result.receipt_payload.recovery_gate_result == "PASSED"
