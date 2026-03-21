"""Baseline trust evaluator for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, Protocol

from ix_style.core.enums import (
    FreshnessState,
    IntegrityState,
    TrustDomain,
    TrustState,
)
from ix_style.core.ids import IdFactory

from .cause_codes import (
    TRUST_CAUSE_DATA_STALE,
    TRUST_CAUSE_INTEGRITY_FAILED,
    TRUST_CAUSE_NAV_CONTINUITY_BREAK,
    TRUST_CAUSE_NAV_SPOOF_SUSPECTED,
    TRUST_CAUSE_RECOVERY_STEP,
    TRUST_CAUSE_SOURCE_DISAGREEMENT,
    TRUST_CAUSE_SOURCE_UNAVAILABLE,
    TRUST_CAUSE_TIMING_INVALID,
    TRUST_CAUSE_VALUE_IMPLAUSIBLE,
)
from .models import (
    TrustCheckInput,
    TrustEvaluationResult,
    TrustRecord,
    TrustTransition,
)

_STATE_SCORES: Final[dict[TrustState, float]] = {
    TrustState.TRUSTED: 1.0,
    TrustState.DEGRADED: 0.7,
    TrustState.SUSPECT: 0.4,
    TrustState.UNTRUSTED: 0.1,
    TrustState.UNAVAILABLE: 0.0,
}

_RECOVERY_STEPS: Final[dict[TrustState, TrustState]] = {
    TrustState.UNAVAILABLE: TrustState.SUSPECT,
    TrustState.UNTRUSTED: TrustState.SUSPECT,
    TrustState.SUSPECT: TrustState.DEGRADED,
    TrustState.DEGRADED: TrustState.TRUSTED,
    TrustState.TRUSTED: TrustState.TRUSTED,
}


class TrustEvaluator(Protocol):
    """Protocol for trust evaluation engines."""

    def evaluate(
        self,
        record: TrustRecord | None,
        check: TrustCheckInput,
    ) -> TrustEvaluationResult:
        """Evaluate one trust-bearing entity and return updated state."""


@dataclass(slots=True)
class BasicTrustEvaluator:
    """Deterministic first-pass trust evaluator for IX-Style."""

    id_factory: IdFactory = field(default_factory=IdFactory)

    def evaluate(
        self,
        record: TrustRecord | None,
        check: TrustCheckInput,
    ) -> TrustEvaluationResult:
        auto_generated_record = record is None
        current = record or self._new_record(check)

        target_state, cause_codes, rationale, negative_evidence = self._determine_target(
            current,
            check,
        )
        posture_driving = self._is_posture_driving(check.trust_domain, target_state)

        if target_state == current.current_trust_state:
            updated = TrustRecord(
                trust_record_id=current.trust_record_id,
                trust_domain=current.trust_domain,
                entity_id=current.entity_id,
                current_trust_state=current.current_trust_state,
                numeric_trust_score=_STATE_SCORES[current.current_trust_state],
                last_transition_timestamp=current.last_transition_timestamp,
                transition_cause_codes=current.transition_cause_codes,
                degradation_streak=(
                    current.degradation_streak + 1 if negative_evidence else 0
                ),
                recovery_streak=(
                    current.recovery_streak + 1 if not negative_evidence else 0
                ),
                posture_driving=posture_driving,
                evidence_required=current.evidence_required or posture_driving,
                rationale_summary=rationale,
            )
            return TrustEvaluationResult(
                record=updated,
                transition=None,
                rationale_summary=rationale,
                auto_generated_record=auto_generated_record,
                negative_evidence_present=negative_evidence,
                metadata={"target_state": target_state.value},
            )

        transition = TrustTransition(
            trust_record_id=current.trust_record_id,
            affected_domain=check.trust_domain,
            affected_entity_id=check.entity_id,
            previous_trust_state=current.current_trust_state,
            new_trust_state=target_state,
            transition_time=check.observed_at,
            cause_codes=cause_codes,
            rationale_summary=rationale,
            posture_driving=posture_driving,
        )
        updated = TrustRecord(
            trust_record_id=current.trust_record_id,
            trust_domain=current.trust_domain,
            entity_id=current.entity_id,
            current_trust_state=target_state,
            numeric_trust_score=_STATE_SCORES[target_state],
            last_transition_timestamp=check.observed_at,
            transition_cause_codes=cause_codes,
            degradation_streak=1 if negative_evidence else 0,
            recovery_streak=0 if negative_evidence else current.recovery_streak + 1,
            posture_driving=posture_driving,
            evidence_required=True,
            rationale_summary=rationale,
        )
        return TrustEvaluationResult(
            record=updated,
            transition=transition,
            rationale_summary=rationale,
            auto_generated_record=auto_generated_record,
            negative_evidence_present=negative_evidence,
            metadata={"target_state": target_state.value},
        )

    def _new_record(self, check: TrustCheckInput) -> TrustRecord:
        return TrustRecord(
            trust_record_id=self.id_factory.trust_record_id(),
            trust_domain=check.trust_domain,
            entity_id=check.entity_id,
            current_trust_state=TrustState.TRUSTED,
            numeric_trust_score=_STATE_SCORES[TrustState.TRUSTED],
            last_transition_timestamp=check.observed_at,
            transition_cause_codes=(),
            rationale_summary="initial trust record created",
        )

    def _determine_target(
        self,
        record: TrustRecord,
        check: TrustCheckInput,
    ) -> tuple[TrustState, tuple[str, ...], str, bool]:
        cause_codes = list(check.cause_codes)

        if not check.source_available:
            cause_codes.append(TRUST_CAUSE_SOURCE_UNAVAILABLE)
            return (
                TrustState.UNAVAILABLE,
                tuple(dict.fromkeys(cause_codes)),
                "source is unavailable and cannot be used as present trustable data",
                True,
            )

        if check.integrity_state is IntegrityState.INTEGRITY_FAILED:
            cause_codes.append(TRUST_CAUSE_INTEGRITY_FAILED)
            return (
                TrustState.UNTRUSTED,
                tuple(dict.fromkeys(cause_codes)),
                "integrity failure prevents trust in this source or derived entity",
                True,
            )

        if (
            check.trust_domain is TrustDomain.NAVIGATION_TRUST
            and TRUST_CAUSE_NAV_SPOOF_SUSPECTED in cause_codes
        ):
            return (
                TrustState.UNTRUSTED,
                tuple(dict.fromkeys(cause_codes)),
                "spoof-suspected navigation behavior forces navigation trust collapse",
                True,
            )

        if (
            check.trust_domain is TrustDomain.NAVIGATION_TRUST
            and check.continuity_ok is False
        ):
            cause_codes.append(TRUST_CAUSE_NAV_CONTINUITY_BREAK)
            return (
                TrustState.SUSPECT,
                tuple(dict.fromkeys(cause_codes)),
                "navigation continuity break makes current navigation picture suspect",
                True,
            )

        if check.freshness_state is FreshnessState.STALE:
            cause_codes.append(TRUST_CAUSE_DATA_STALE)
            degraded_target = (
                TrustState.SUSPECT
                if check.trust_domain
                in {
                    TrustDomain.NAVIGATION_TRUST,
                    TrustDomain.MESSAGE_TRUST,
                    TrustDomain.ASSURANCE_CONFIDENCE,
                }
                else TrustState.DEGRADED
            )
            return (
                degraded_target,
                tuple(dict.fromkeys(cause_codes)),
                "freshness failure weakens trust even if values remain superficially plausible",
                True,
            )

        if check.freshness_state is FreshnessState.TIMING_INVALID:
            cause_codes.append(TRUST_CAUSE_TIMING_INVALID)
            return (
                TrustState.SUSPECT,
                tuple(dict.fromkeys(cause_codes)),
                "timing validity is broken, so trust must narrow sharply",
                True,
            )

        if not check.plausibility_ok:
            cause_codes.append(TRUST_CAUSE_VALUE_IMPLAUSIBLE)
            return (
                TrustState.SUSPECT,
                tuple(dict.fromkeys(cause_codes)),
                "plausibility failure means the value cannot be treated as fully trustworthy",
                True,
            )

        if check.cross_consistency_ok is False:
            cause_codes.append(TRUST_CAUSE_SOURCE_DISAGREEMENT)
            return (
                TrustState.SUSPECT,
                tuple(dict.fromkeys(cause_codes)),
                "cross-consistency failure indicates unresolved disagreement across trust sources",
                True,
            )

        target_state = _RECOVERY_STEPS[record.current_trust_state]
        if target_state != record.current_trust_state:
            cause_codes.append(TRUST_CAUSE_RECOVERY_STEP)
            return (
                target_state,
                tuple(dict.fromkeys(cause_codes)),
                "healthy evidence allows only one bounded recovery step toward full trust",
                False,
            )

        return (
            TrustState.TRUSTED,
            tuple(dict.fromkeys(cause_codes)),
            check.rationale_hint or "trust remains acceptable under current checks",
            False,
        )

    @staticmethod
    def _is_posture_driving(
        trust_domain: TrustDomain,
        trust_state: TrustState,
    ) -> bool:
        if trust_domain in {TrustDomain.NAVIGATION_TRUST, TrustDomain.ASSURANCE_CONFIDENCE}:
            return trust_state in {
                TrustState.DEGRADED,
                TrustState.SUSPECT,
                TrustState.UNTRUSTED,
                TrustState.UNAVAILABLE,
            }

        return trust_state in {TrustState.SUSPECT, TrustState.UNTRUSTED, TrustState.UNAVAILABLE}
