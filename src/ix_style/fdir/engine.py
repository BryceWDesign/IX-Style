"""Baseline executable FDIR lifecycle engine for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, Protocol

from ix_style.core.enums import FaultLifecycleState
from ix_style.core.ids import IdFactory

from .models import (
    FDIREvaluationResult,
    FDIRSignal,
    FaultClass,
    FaultIsolationConfidence,
    FaultPriority,
    FaultRecord,
    FaultSeverity,
    FaultTransition,
    MitigationCategory,
)

_CONFIDENCE_BY_STATE: Final[dict[FaultLifecycleState, float]] = {
    FaultLifecycleState.DETECTED: 0.20,
    FaultLifecycleState.SUSPECTED: 0.40,
    FaultLifecycleState.CONFIRMED: 0.70,
    FaultLifecycleState.ISOLATING: 0.75,
    FaultLifecycleState.ISOLATED: 0.85,
    FaultLifecycleState.MITIGATING: 0.80,
    FaultLifecycleState.CONTAINED: 0.90,
    FaultLifecycleState.RECOVERING: 0.60,
    FaultLifecycleState.CLEARED: 0.10,
    FaultLifecycleState.LATCHED: 0.95,
}


class FDIREngine(Protocol):
    """Protocol for FDIR engines."""

    def evaluate(
        self,
        record: FaultRecord | None,
        signal: FDIRSignal,
    ) -> FDIREvaluationResult:
        """Evaluate one fault signal and update lifecycle state."""


@dataclass(slots=True)
class BasicFDIREngine:
    """Deterministic first-pass FDIR lifecycle engine for IX-Style."""

    id_factory: IdFactory = field(default_factory=IdFactory)

    def evaluate(
        self,
        record: FaultRecord | None,
        signal: FDIRSignal,
    ) -> FDIREvaluationResult:
        auto_generated_record = record is None
        current = record or self._new_record(signal)

        if auto_generated_record:
            next_state = current.lifecycle_state
            rationale = self._initial_rationale(signal, next_state)
        else:
            next_state, rationale = self._determine_next_state(current, signal)

        next_priority = self._priority_for(signal, next_state)
        next_mitigations = self._mitigations_for(signal, next_state)
        next_isolation = self._isolation_for(signal, next_state)

        if signal.anomaly_active:
            occurrence_count = current.occurrence_count + 1
            corroborated_count = current.corroborated_count + (1 if signal.corroborated else 0)
        else:
            occurrence_count = current.occurrence_count
            corroborated_count = current.corroborated_count

        transition: FaultTransition | None = None
        if auto_generated_record and signal.anomaly_active:
            transition = FaultTransition(
                fault_id=current.fault_id,
                fault_class=current.fault_class,
                previous_state=FaultLifecycleState.CLEARED,
                new_state=next_state,
                transition_time=signal.observed_at,
                priority_before=FaultPriority.P4_LOW,
                priority_after=next_priority,
                cause_codes=signal.cause_codes,
                rationale_summary=rationale,
            )
        elif (
            next_state != current.lifecycle_state
            or next_priority != current.current_priority
            or current.active_mitigation_set != next_mitigations
        ):
            transition = FaultTransition(
                fault_id=current.fault_id,
                fault_class=current.fault_class,
                previous_state=current.lifecycle_state,
                new_state=next_state,
                transition_time=signal.observed_at,
                priority_before=current.current_priority,
                priority_after=next_priority,
                cause_codes=signal.cause_codes,
                rationale_summary=rationale,
            )

        updated = FaultRecord(
            fault_id=current.fault_id,
            fault_class=current.fault_class,
            lifecycle_state=next_state,
            detection_source=current.detection_source,
            first_detected_timestamp=current.first_detected_timestamp,
            latest_update_timestamp=signal.observed_at,
            affected_function_scope=current.affected_function_scope,
            severity_estimate=signal.severity_estimate,
            confirmation_confidence=_CONFIDENCE_BY_STATE[next_state],
            isolation_confidence=next_isolation,
            active_mitigation_set=next_mitigations,
            current_priority=next_priority,
            latch_status=next_state is FaultLifecycleState.LATCHED,
            recovery_gate_status=self._recovery_gate_status(signal, next_state),
            rationale_summary=rationale,
            occurrence_count=occurrence_count,
            corroborated_count=corroborated_count,
        )

        return FDIREvaluationResult(
            record=updated,
            transition=transition,
            rationale_summary=rationale,
            auto_generated_record=auto_generated_record,
            negative_evidence_present=signal.anomaly_active,
            metadata={
                "next_state": next_state.value,
                "next_priority": next_priority.value,
            },
        )

    def _new_record(self, signal: FDIRSignal) -> FaultRecord:
        initial_state = self._initial_state(signal)
        return FaultRecord(
            fault_id=self.id_factory.fault_id(),
            fault_class=signal.fault_class,
            lifecycle_state=initial_state,
            detection_source=signal.detection_source,
            first_detected_timestamp=signal.observed_at,
            latest_update_timestamp=signal.observed_at,
            affected_function_scope=signal.affected_function_scope,
            severity_estimate=signal.severity_estimate,
            confirmation_confidence=_CONFIDENCE_BY_STATE[initial_state],
            isolation_confidence=self._isolation_for(signal, initial_state),
            active_mitigation_set=self._mitigations_for(signal, initial_state),
            current_priority=self._priority_for(signal, initial_state),
            latch_status=initial_state is FaultLifecycleState.LATCHED,
            recovery_gate_status=self._recovery_gate_status(signal, initial_state),
            rationale_summary="initial fault record created",
            occurrence_count=0,
            corroborated_count=0,
        )

    def _initial_state(self, signal: FDIRSignal) -> FaultLifecycleState:
        if not signal.anomaly_active:
            return FaultLifecycleState.CLEARED

        if signal.containment_required and signal.mitigation_requested:
            return FaultLifecycleState.CONTAINED

        if signal.mitigation_requested and signal.severity_estimate in {
            FaultSeverity.CRITICAL,
            FaultSeverity.CATASTROPHIC,
        }:
            return FaultLifecycleState.MITIGATING

        if signal.corroborated and signal.severity_estimate in {
            FaultSeverity.CRITICAL,
            FaultSeverity.CATASTROPHIC,
        }:
            return FaultLifecycleState.CONFIRMED

        return FaultLifecycleState.DETECTED

    def _initial_rationale(
        self,
        signal: FDIRSignal,
        lifecycle_state: FaultLifecycleState,
    ) -> str:
        if lifecycle_state is FaultLifecycleState.CLEARED:
            return signal.rationale_hint or "fault record initialized in cleared state"
        if lifecycle_state is FaultLifecycleState.CONTAINED:
            return (
                "initial abnormal evidence already requires containment and active mitigation"
            )
        if lifecycle_state is FaultLifecycleState.MITIGATING:
            return "initial abnormal evidence entered the lifecycle with mitigation already active"
        if lifecycle_state is FaultLifecycleState.CONFIRMED:
            return "initial abnormal evidence was already corroborated at critical severity"
        return signal.rationale_hint or "initial abnormal evidence opened the fault lifecycle"


    def _determine_next_state(
        self,
        current: FaultRecord,
        signal: FDIRSignal,
    ) -> tuple[FaultLifecycleState, str]:
        if not signal.anomaly_active:
            return self._determine_recovery_state(current, signal)

        if current.lifecycle_state is FaultLifecycleState.LATCHED:
            return (
                FaultLifecycleState.LATCHED,
                "fault remains latched until explicit qualified recovery is requested",
            )

        if signal.latch_required and current.lifecycle_state in {
            FaultLifecycleState.CONTAINED,
            FaultLifecycleState.MITIGATING,
            FaultLifecycleState.CONFIRMED,
        }:
            return (
                FaultLifecycleState.LATCHED,
                "fault severity or repetition requires latching until explicit reset policy permits release",
            )

        if signal.containment_required and signal.mitigation_requested:
            return (
                FaultLifecycleState.CONTAINED,
                "containment is required and mitigation is active, so the fault is treated as contained",
            )

        if current.lifecycle_state is FaultLifecycleState.DETECTED:
            return (
                FaultLifecycleState.SUSPECTED,
                "repeated active anomaly promotes the fault from detected to suspected",
            )

        if current.lifecycle_state is FaultLifecycleState.SUSPECTED:
            if (
                signal.corroborated
                or current.occurrence_count >= 2
                or signal.severity_estimate in {FaultSeverity.CRITICAL, FaultSeverity.CATASTROPHIC}
            ):
                return (
                    FaultLifecycleState.CONFIRMED,
                    "persistence, corroboration, or severity justifies confirmed fault status",
                )
            return (
                FaultLifecycleState.SUSPECTED,
                "fault remains suspected while evidence accumulates",
            )

        if current.lifecycle_state is FaultLifecycleState.CONFIRMED:
            if signal.mitigation_requested:
                return (
                    FaultLifecycleState.MITIGATING,
                    "confirmed fault now has active mitigation in progress",
                )
            return (
                FaultLifecycleState.CONFIRMED,
                "fault remains confirmed while awaiting mitigation or containment",
            )

        if current.lifecycle_state in {
            FaultLifecycleState.MITIGATING,
            FaultLifecycleState.ISOLATING,
            FaultLifecycleState.ISOLATED,
        }:
            if signal.containment_required:
                return (
                    FaultLifecycleState.CONTAINED,
                    "mitigation has shifted into bounded containment posture",
                )
            return (
                FaultLifecycleState.MITIGATING,
                "fault remains under active mitigation",
            )

        if current.lifecycle_state is FaultLifecycleState.CONTAINED:
            return (
                FaultLifecycleState.CONTAINED,
                "fault remains actively contained while abnormal conditions persist",
            )

        if current.lifecycle_state is FaultLifecycleState.RECOVERING:
            return (
                FaultLifecycleState.CONTAINED,
                "renewed abnormal evidence during recovery forces the fault back into containment",
            )

        if current.lifecycle_state is FaultLifecycleState.CLEARED:
            return (
                FaultLifecycleState.DETECTED,
                "new abnormal evidence reopens the fault lifecycle from detected state",
            )

        return (
            current.lifecycle_state,
            signal.rationale_hint or "fault state unchanged under current evidence",
        )

    def _determine_recovery_state(
        self,
        current: FaultRecord,
        signal: FDIRSignal,
    ) -> tuple[FaultLifecycleState, str]:
        if current.lifecycle_state in {
            FaultLifecycleState.DETECTED,
            FaultLifecycleState.SUSPECTED,
        }:
            return (
                FaultLifecycleState.CLEARED,
                "transient low-confidence fault evidence has cleared without needing containment",
            )

        if current.lifecycle_state is FaultLifecycleState.RECOVERING:
            if signal.recovery_requested and signal.recovery_permitted:
                return (
                    FaultLifecycleState.CLEARED,
                    "recovery evaluation succeeded and the fault is cleared",
                )
            return (
                FaultLifecycleState.RECOVERING,
                "fault remains in recovery review while full clearance is not yet justified",
            )

        if current.lifecycle_state in {
            FaultLifecycleState.CONFIRMED,
            FaultLifecycleState.MITIGATING,
            FaultLifecycleState.CONTAINED,
            FaultLifecycleState.LATCHED,
            FaultLifecycleState.ISOLATING,
            FaultLifecycleState.ISOLATED,
        }:
            if signal.recovery_requested and signal.recovery_permitted:
                return (
                    FaultLifecycleState.RECOVERING,
                    "fault symptoms have eased and recovery gate evaluation is now active",
                )
            return (
                current.lifecycle_state,
                "fault symptoms may have eased, but recovery gate conditions are not yet satisfied",
            )

        return (
            current.lifecycle_state,
            signal.rationale_hint or "no active anomaly and no lifecycle change required",
        )

    @staticmethod
    def _priority_for(
        signal: FDIRSignal,
        lifecycle_state: FaultLifecycleState,
    ) -> FaultPriority:
        if lifecycle_state in {FaultLifecycleState.CLEARED}:
            return FaultPriority.P4_LOW

        if signal.containment_required or signal.fault_class is FaultClass.ASSURANCE_FAULT:
            return FaultPriority.P1_CONTAINMENT_CRITICAL

        if signal.severity_estimate in {FaultSeverity.CRITICAL, FaultSeverity.CATASTROPHIC}:
            return FaultPriority.P1_CONTAINMENT_CRITICAL

        if signal.authority_relevant or signal.evidence_critical:
            return FaultPriority.P2_HIGH

        if signal.severity_estimate is FaultSeverity.MAJOR:
            return FaultPriority.P3_MODERATE

        return FaultPriority.P4_LOW

    @staticmethod
    def _mitigations_for(
        signal: FDIRSignal,
        lifecycle_state: FaultLifecycleState,
    ) -> tuple[MitigationCategory, ...]:
        if lifecycle_state is FaultLifecycleState.CLEARED:
            return ()

        mitigations: list[MitigationCategory] = []

        if lifecycle_state in {FaultLifecycleState.DETECTED, FaultLifecycleState.SUSPECTED}:
            mitigations.append(MitigationCategory.OBSERVE_ONLY)

        if signal.authority_relevant:
            mitigations.append(MitigationCategory.REDUCE_AUTHORITY)

        if signal.mitigation_requested and lifecycle_state in {
            FaultLifecycleState.CONFIRMED,
            FaultLifecycleState.MITIGATING,
        }:
            mitigations.append(MitigationCategory.CLAMP_BEHAVIOR)

        if signal.containment_required and lifecycle_state is FaultLifecycleState.CONTAINED:
            mitigations.append(
                MitigationCategory.ENTER_SAFE_HOLD
                if signal.severity_estimate in {FaultSeverity.CRITICAL, FaultSeverity.CATASTROPHIC}
                or signal.fault_class is FaultClass.ASSURANCE_FAULT
                else MitigationCategory.ENTER_DEGRADED_MODE
            )

        if lifecycle_state is FaultLifecycleState.LATCHED:
            mitigations.append(MitigationCategory.LATCH_AND_REQUIRE_RESET)

        if lifecycle_state is FaultLifecycleState.RECOVERING:
            mitigations.append(MitigationCategory.RECOVERY_GATE_EVALUATION)

        deduped: list[MitigationCategory] = []
        for item in mitigations:
            if item not in deduped:
                deduped.append(item)
        return tuple(deduped)

    @staticmethod
    def _isolation_for(
        signal: FDIRSignal,
        lifecycle_state: FaultLifecycleState,
    ) -> FaultIsolationConfidence:
        if lifecycle_state in {
            FaultLifecycleState.CONTAINED,
            FaultLifecycleState.LATCHED,
        }:
            return FaultIsolationConfidence.HIGH
        if lifecycle_state in {
            FaultLifecycleState.CONFIRMED,
            FaultLifecycleState.MITIGATING,
            FaultLifecycleState.RECOVERING,
        }:
            return FaultIsolationConfidence.MEDIUM
        if signal.corroborated:
            return FaultIsolationConfidence.MEDIUM
        return FaultIsolationConfidence.LOW

    @staticmethod
    def _recovery_gate_status(
        signal: FDIRSignal,
        lifecycle_state: FaultLifecycleState,
    ) -> str:
        if lifecycle_state is FaultLifecycleState.RECOVERING:
            return "UNDER_REVIEW"
        if lifecycle_state is FaultLifecycleState.CLEARED:
            return "PASSED"
        if not signal.anomaly_active and not signal.recovery_permitted:
            return "BLOCKED"
        return "NOT_APPLICABLE"
