"""Reusable executable sample scenarios for IX-Style."""

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

from .models import VerificationExpectation, VerificationScenario


def _now() -> datetime:
    """Return an aware UTC timestamp."""
    return datetime.now(tz=UTC)


def _message_type_for(function_class: FunctionClass) -> str:
    """Return the baseline message type for a function class."""
    mapping = {
        FunctionClass.MODE_MANAGEMENT: "control.mode_request",
        FunctionClass.MISSION_INTENT: "control.mode_request",
        FunctionClass.GUIDANCE_REQUEST: "control.guidance_request",
        FunctionClass.ACTUATION_REQUEST: "control.actuation_request",
        FunctionClass.RESOURCE_CONFIGURATION: "control.resource_configuration_request",
        FunctionClass.RECOVERY_ACTION: "control.recovery_action_request",
        FunctionClass.POLICY_OVERRIDE: "control.policy_override_request",
        FunctionClass.EVIDENCE_CONTROL: "control.policy_override_request",
    }
    return mapping[function_class]


def _source_kind_for(command_source: CommandSource) -> str:
    """Return the baseline source kind string for a command source."""
    mapping = {
        CommandSource.OPERATOR: "operator",
        CommandSource.MISSION_LOGIC: "mission_logic",
        CommandSource.NOMINAL_AUTONOMY: "nominal_autonomy",
        CommandSource.CONTINGENCY_LOGIC: "contingency_logic",
        CommandSource.SAFETY_SUPERVISOR: "safety_supervisor",
        CommandSource.NONE: "infrastructure",
    }
    return mapping[command_source]


def _make_control_envelope(
    *,
    command_source: CommandSource,
    function_class: FunctionClass,
    requested_action: str,
    requested_scope: str,
    requested_magnitude: float | None = None,
    requested_duration_ms: int | None = None,
) -> MessageEnvelope:
    """Build a baseline control envelope for reusable sample scenarios."""
    now = _now()
    return MessageEnvelope(
        schema_version="0.1.0",
        message_id="MSG-SAMPLE-000001",
        message_class=MessageClass.CONTROL,
        message_type=_message_type_for(function_class),
        source_id=f"{_source_kind_for(command_source)}.sample",
        source_kind=_source_kind_for(command_source),
        created_at=now,
        freshness=FreshnessMetadata(
            issued_at=now,
            expires_at=now + timedelta(seconds=5),
            freshness_state=FreshnessState.FRESH,
        ),
        ordering=OrderingMetadata(
            sequence_number=1,
            session_id="SES-SAMPLE-000001",
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
            requested_scope=requested_scope,
            requested_magnitude=requested_magnitude,
            requested_duration_ms=requested_duration_ms,
            rationale_summary="sample scenario command",
        ),
    )


def build_power_fault_clamp_scenario() -> VerificationScenario:
    """Return the reusable power/resource degradation sample scenario."""
    return VerificationScenario(
        scenario_id="EXAMPLE-POWER-CLAMP-001",
        name="power fault clamp demo",
        purpose=(
            "demonstrate evidence and mission-health output under power/resource"
            " degradation"
        ),
        linked_requirements=("IXS-SYS-059",),
        linked_hazards=("IXS-HZ-006",),
        envelope=_make_control_envelope(
            command_source=CommandSource.NOMINAL_AUTONOMY,
            function_class=FunctionClass.ACTUATION_REQUEST,
            requested_action="perform_demo_maneuver",
            requested_scope="vehicle.primary",
            requested_magnitude=1.0,
            requested_duration_ms=150,
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


def build_nav_spoof_transition_scenario() -> VerificationScenario:
    """Return the reusable navigation trust collapse sample scenario."""
    return VerificationScenario(
        scenario_id="EXAMPLE-NAV-SPOOF-001",
        name="navigation spoof suspicion demo",
        purpose=(
            "demonstrate trust transition evidence and mission-health output under"
            " navigation trust collapse"
        ),
        linked_requirements=("IXS-SYS-015",),
        linked_hazards=("IXS-HZ-003",),
        envelope=_make_control_envelope(
            command_source=CommandSource.OPERATOR,
            function_class=FunctionClass.MODE_MANAGEMENT,
            requested_action="request_mode_review",
            requested_scope="vehicle.primary",
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


def build_recovery_deferred_scenario() -> VerificationScenario:
    """Return a reusable recovery-action scenario deferred by weak communications."""
    return VerificationScenario(
        scenario_id="EXAMPLE-RECOVERY-DEFERRED-001",
        name="recovery deferred over weak comms demo",
        purpose=(
            "demonstrate that recovery expansion is deferred when remote recovery"
            " intent arrives under degraded communications"
        ),
        linked_requirements=("IXS-SYS-034",),
        linked_hazards=("IXS-HZ-010",),
        envelope=_make_control_envelope(
            command_source=CommandSource.OPERATOR,
            function_class=FunctionClass.RECOVERY_ACTION,
            requested_action="request_recovery_review",
            requested_scope="vehicle.primary",
            requested_duration_ms=100,
        ),
        mission_phase=MissionPhase.ACTIVE,
        safety_posture=SafetyPosture.COMMS_DEGRADED,
        active_degradation_flags=("comms_link_intermittent",),
        expectations=VerificationExpectation(
            expected_final_outcome=ArbitrationOutcome.DEFER,
            required_active_degradation_flags=("comms_link_intermittent",),
        ),
    )
