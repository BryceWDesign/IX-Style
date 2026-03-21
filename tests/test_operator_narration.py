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
from ix_style.telemetry import OperatorRationaleFormatter, SafetySummaryNarrator
from ix_style.trust import TrustRecord
from ix_style.core.enums import TrustState
from ix_style.verification import (
    ScenarioRunner,
    build_nav_spoof_transition_scenario,
    build_power_fault_clamp_scenario,
)


def _now() -> datetime:
    return datetime.now(tz=UTC)


def _make_recovery_envelope() -> MessageEnvelope:
    now = _now()
    return MessageEnvelope(
        schema_version="0.1.0",
        message_id="MSG-TEST-OPERATOR-RECOVERY-000001",
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
            session_id="SES-TEST-OPERATOR-RECOVERY-000001",
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


def test_power_fault_summary_calls_out_power_degraded_and_operator_focus() -> None:
    result = ScenarioRunner().run(build_power_fault_clamp_scenario())
    summary = SafetySummaryNarrator().summarize_verification(result)

    assert summary.headline == "POWER DEGRADED"
    assert "essential functions" in summary.operator_focus.lower()
    assert "SAFETY_SUPERVISOR" in summary.authority_statement
    assert summary.review_significance == "HIGH"


def test_nav_spoof_summary_calls_out_navigation_degraded() -> None:
    result = ScenarioRunner().run(build_nav_spoof_transition_scenario())
    summary = SafetySummaryNarrator().summarize_verification(result)

    assert summary.headline == "NAVIGATION DEGRADED"
    assert "NAVIGATION_TRUST" in summary.operational_why or "navigation" in summary.operational_why.lower()
    assert len(summary.timeline_markers) >= 1
    assert "Command was accepted" in summary.decision_rationale


def test_recovery_blocked_formatter_says_recovery_was_blocked() -> None:
    pipeline = DecisionPipeline()
    trust_record = TrustRecord(
        trust_record_id="TR-OPERATOR-RECOVERY-000001",
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

    formatted = OperatorRationaleFormatter().decision_rationale(
        result.receipt_payload.as_dict()
    )

    assert result.receipt_payload.final_outcome is ArbitrationOutcome.REJECT
    assert "Recovery expansion was blocked" in formatted
