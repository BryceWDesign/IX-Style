from __future__ import annotations

from datetime import UTC, datetime

from ix_style.core.enums import FreshnessState, IntegrityState, TrustDomain, TrustState
from ix_style.trust import (
    TRUST_CAUSE_DATA_STALE,
    TRUST_CAUSE_NAV_SPOOF_SUSPECTED,
    BasicTrustEvaluator,
    TrustCheckInput,
)


def _now() -> datetime:
    return datetime.now(tz=UTC)


def test_stale_sensor_input_degrades_to_degraded_state() -> None:
    evaluator = BasicTrustEvaluator()
    result = evaluator.evaluate(
        record=None,
        check=TrustCheckInput(
            trust_domain=TrustDomain.SENSOR_SOURCE_TRUST,
            entity_id="sensor.alpha",
            observed_at=_now(),
            freshness_state=FreshnessState.STALE,
        ),
    )

    assert result.record.current_trust_state is TrustState.DEGRADED
    assert result.transition is not None
    assert TRUST_CAUSE_DATA_STALE in result.transition.cause_codes
    assert result.negative_evidence_present is True


def test_nav_spoof_suspected_collapses_navigation_trust() -> None:
    evaluator = BasicTrustEvaluator()
    result = evaluator.evaluate(
        record=None,
        check=TrustCheckInput(
            trust_domain=TrustDomain.NAVIGATION_TRUST,
            entity_id="nav.primary",
            observed_at=_now(),
            cause_codes=(TRUST_CAUSE_NAV_SPOOF_SUSPECTED,),
        ),
    )

    assert result.record.current_trust_state is TrustState.UNTRUSTED
    assert result.transition is not None
    assert result.record.posture_driving is True


def test_integrity_failure_for_message_trust_becomes_untrusted() -> None:
    evaluator = BasicTrustEvaluator()
    result = evaluator.evaluate(
        record=None,
        check=TrustCheckInput(
            trust_domain=TrustDomain.MESSAGE_TRUST,
            entity_id="remote.operator.link",
            observed_at=_now(),
            integrity_state=IntegrityState.INTEGRITY_FAILED,
        ),
    )

    assert result.record.current_trust_state is TrustState.UNTRUSTED
    assert result.transition is not None
    assert result.record.evidence_required is True


def test_recovery_only_advances_one_step_toward_trusted() -> None:
    evaluator = BasicTrustEvaluator()
    degraded = evaluator.evaluate(
        record=None,
        check=TrustCheckInput(
            trust_domain=TrustDomain.SENSOR_SOURCE_TRUST,
            entity_id="sensor.beta",
            observed_at=_now(),
            freshness_state=FreshnessState.STALE,
        ),
    ).record

    recovered = evaluator.evaluate(
        record=degraded,
        check=TrustCheckInput(
            trust_domain=TrustDomain.SENSOR_SOURCE_TRUST,
            entity_id="sensor.beta",
            observed_at=_now(),
        ),
    )

    assert degraded.current_trust_state is TrustState.DEGRADED
    assert recovered.record.current_trust_state is TrustState.TRUSTED

    untrusted = evaluator.evaluate(
        record=None,
        check=TrustCheckInput(
            trust_domain=TrustDomain.NAVIGATION_TRUST,
            entity_id="nav.secondary",
            observed_at=_now(),
            cause_codes=(TRUST_CAUSE_NAV_SPOOF_SUSPECTED,),
        ),
    ).record

    partial_recovery = evaluator.evaluate(
        record=untrusted,
        check=TrustCheckInput(
            trust_domain=TrustDomain.NAVIGATION_TRUST,
            entity_id="nav.secondary",
            observed_at=_now(),
        ),
    )

    assert untrusted.current_trust_state is TrustState.UNTRUSTED
    assert partial_recovery.record.current_trust_state is TrustState.SUSPECT
