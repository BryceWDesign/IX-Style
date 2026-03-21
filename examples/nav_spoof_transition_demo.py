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
    TrustDomain,
)
from ix_style.telemetry import MissionHealthBuilder
from ix_style.trust import TRUST_CAUSE_NAV_SPOOF_SUSPECTED, TrustCheckInput
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
        message_id="MSG-EXAMPLE-NAV-000001",
        message_class=MessageClass.CONTROL,
        message_type="control.mode_request",
        source_id="operator.console.demo",
        source_kind="operator",
        created_at=now,
        freshness=FreshnessMetadata(
            issued_at=now,
            expires_at=now + timedelta(seconds=5),
            freshness_state=FreshnessState.FRESH,
        ),
        ordering=OrderingMetadata(
            sequence_number=1,
            session_id="SES-EXAMPLE-NAV-000001",
            replay_state=ReplayState.ACCEPTABLE,
        ),
        integrity=IntegrityMetadata(
            integrity_state=IntegrityState.INTEGRITY_VALID,
            auth_state=AuthState.INTEGRITY_VALID,
        ),
        payload=ControlPayload(
            function_class=FunctionClass.MODE_MANAGEMENT,
            requested_action="request_mode_review",
            command_source=CommandSource.OPERATOR,
            policy_context={"override_requested": False},
            requested_scope="vehicle.primary",
            rationale_summary="demo mode request during navigation trust collapse",
        ),
    )

    scenario = VerificationScenario(
        scenario_id="EXAMPLE-NAV-SPOOF-001",
        name="navigation spoof suspicion demo",
        purpose="demonstrate trust transition evidence and mission-health output under nav trust collapse",
        linked_requirements=("IXS-SYS-015",),
        linked_hazards=("IXS-HZ-003",),
        envelope=envelope,
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
