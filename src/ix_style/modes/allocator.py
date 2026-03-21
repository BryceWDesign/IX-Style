"""Executable dominant posture allocator for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Final

from ix_style.core.enums import FaultLifecycleState, SafetyPosture, TrustDomain, TrustState
from ix_style.fdir.models import FaultClass, FaultPriority, FaultRecord
from ix_style.trust.models import TrustRecord

from .models import ModeAllocationInput, ModeAllocationResult, ModeTransition, utc_now

_PRECEDENCE: Final[dict[SafetyPosture, int]] = {
    SafetyPosture.NOMINAL: 0,
    SafetyPosture.COMMS_DEGRADED: 1,
    SafetyPosture.SENSOR_DEGRADED: 2,
    SafetyPosture.NAV_DEGRADED: 3,
    SafetyPosture.ACTUATION_DEGRADED: 4,
    SafetyPosture.POWER_DEGRADED: 5,
    SafetyPosture.ASSURANCE_DEGRADED: 6,
    SafetyPosture.SAFE_HOLD: 7,
    SafetyPosture.INITIALIZING: -1,
}

_DEGRADED_TRUST_STATES: Final[set[TrustState]] = {
    TrustState.DEGRADED,
    TrustState.SUSPECT,
    TrustState.UNTRUSTED,
    TrustState.UNAVAILABLE,
}


@dataclass(slots=True)
class ModeAllocator:
    """Resolves trust, faults, and flags into one dominant safety posture."""

    def evaluate(self, allocation_input: ModeAllocationInput) -> ModeAllocationResult:
        reasons: dict[SafetyPosture, list[str]] = {}
        fault_ids: dict[SafetyPosture, set[str]] = {}
        trust_ids: dict[SafetyPosture, set[str]] = {}
        cause_codes: dict[SafetyPosture, set[str]] = {}

        def register(
            posture: SafetyPosture,
            *,
            reason: str,
            fault_id: str | None = None,
            trust_id: str | None = None,
            code: str | None = None,
        ) -> None:
            reasons.setdefault(posture, []).append(reason)
            fault_ids.setdefault(posture, set())
            trust_ids.setdefault(posture, set())
            cause_codes.setdefault(posture, set())
            if fault_id is not None:
                fault_ids[posture].add(fault_id)
            if trust_id is not None:
                trust_ids[posture].add(trust_id)
            if code is not None:
                cause_codes[posture].add(code)

        base_posture = allocation_input.base_posture
        if base_posture is not SafetyPosture.NOMINAL:
            register(
                base_posture,
                reason="base posture from current operating context remains active",
                code=f"BASE_POSTURE_{base_posture.value}",
            )

        flags = set(allocation_input.active_degradation_flags)
        if base_posture is SafetyPosture.SAFE_HOLD:
            register(
                SafetyPosture.SAFE_HOLD,
                reason="base posture is already safe-hold",
                code="BASE_POSTURE_ALREADY_SAFE_HOLD",
            )

        if "assurance_guard_unhealthy" in flags:
            register(
                SafetyPosture.ASSURANCE_DEGRADED,
                reason="active degradation indicates assurance guard is unhealthy",
                code="FLAG_ASSURANCE_GUARD_UNHEALTHY",
            )
        if "power_margin_low" in flags:
            register(
                SafetyPosture.POWER_DEGRADED,
                reason="active degradation indicates low power or resource margin",
                code="FLAG_POWER_MARGIN_LOW",
            )
        if "actuator_response_uncertain" in flags:
            register(
                SafetyPosture.ACTUATION_DEGRADED,
                reason="active degradation indicates uncertain actuator response",
                code="FLAG_ACTUATOR_RESPONSE_UNCERTAIN",
            )
        if "nav_spoof_suspected" in flags:
            register(
                SafetyPosture.NAV_DEGRADED,
                reason="active degradation indicates spoof-suspected navigation trust collapse",
                code="FLAG_NAV_SPOOF_SUSPECTED",
            )
        elif "nav_corroboration_lost" in flags:
            register(
                SafetyPosture.NAV_DEGRADED,
                reason="active degradation indicates navigation corroboration loss",
                code="FLAG_NAV_CORROBORATION_LOST",
            )
        if "sensor_trust_low" in flags:
            register(
                SafetyPosture.SENSOR_DEGRADED,
                reason="active degradation indicates critical sensor trust weakness",
                code="FLAG_SENSOR_TRUST_LOW",
            )
        if "comms_link_intermittent" in flags:
            register(
                SafetyPosture.COMMS_DEGRADED,
                reason="active degradation indicates intermittent communications",
                code="FLAG_COMMS_LINK_INTERMITTENT",
            )
        if "command_freshness_low" in flags:
            register(
                SafetyPosture.COMMS_DEGRADED,
                reason="active degradation indicates weak command freshness",
                code="FLAG_COMMAND_FRESHNESS_LOW",
            )

        for record in allocation_input.trust_records.values():
            if record.current_trust_state not in _DEGRADED_TRUST_STATES:
                continue

            if record.trust_domain is TrustDomain.ASSURANCE_CONFIDENCE:
                register(
                    SafetyPosture.ASSURANCE_DEGRADED,
                    reason="assurance confidence trust record is degraded",
                    trust_id=record.trust_record_id,
                    code=f"TRUST_{record.trust_domain.value}_{record.current_trust_state.value}",
                )
            elif record.trust_domain is TrustDomain.ACTUATOR_CONFIDENCE:
                register(
                    SafetyPosture.ACTUATION_DEGRADED,
                    reason="actuator confidence trust record is degraded",
                    trust_id=record.trust_record_id,
                    code=f"TRUST_{record.trust_domain.value}_{record.current_trust_state.value}",
                )
            elif record.trust_domain is TrustDomain.NAVIGATION_TRUST:
                register(
                    SafetyPosture.NAV_DEGRADED,
                    reason="navigation trust record is degraded",
                    trust_id=record.trust_record_id,
                    code=f"TRUST_{record.trust_domain.value}_{record.current_trust_state.value}",
                )
            elif record.trust_domain in {
                TrustDomain.SENSOR_SOURCE_TRUST,
                TrustDomain.DERIVED_STATE_TRUST,
            }:
                register(
                    SafetyPosture.SENSOR_DEGRADED,
                    reason="sensor or derived-state trust record is degraded",
                    trust_id=record.trust_record_id,
                    code=f"TRUST_{record.trust_domain.value}_{record.current_trust_state.value}",
                )
            elif record.trust_domain in {
                TrustDomain.MESSAGE_TRUST,
                TrustDomain.TIMING_TRUST,
            }:
                register(
                    SafetyPosture.COMMS_DEGRADED,
                    reason="message or timing trust record is degraded",
                    trust_id=record.trust_record_id,
                    code=f"TRUST_{record.trust_domain.value}_{record.current_trust_state.value}",
                )

        for record in allocation_input.fault_records.values():
            if record.lifecycle_state is FaultLifecycleState.CLEARED:
                continue

            if (
                record.current_priority is FaultPriority.P1_CONTAINMENT_CRITICAL
                and record.lifecycle_state
                in {FaultLifecycleState.CONTAINED, FaultLifecycleState.LATCHED}
            ):
                register(
                    SafetyPosture.SAFE_HOLD,
                    reason="containment-critical fault remains contained or latched",
                    fault_id=record.fault_id,
                    code=f"FAULT_SAFE_HOLD_{record.fault_class.value}",
                )

            if record.fault_class is FaultClass.ASSURANCE_FAULT:
                register(
                    SafetyPosture.ASSURANCE_DEGRADED,
                    reason="assurance fault remains active",
                    fault_id=record.fault_id,
                    code=f"FAULT_{record.fault_class.value}",
                )
            elif record.fault_class is FaultClass.POWER_RESOURCE_FAULT:
                register(
                    SafetyPosture.POWER_DEGRADED,
                    reason="power or resource fault remains active",
                    fault_id=record.fault_id,
                    code=f"FAULT_{record.fault_class.value}",
                )
            elif record.fault_class is FaultClass.ACTUATION_FAULT:
                register(
                    SafetyPosture.ACTUATION_DEGRADED,
                    reason="actuation fault remains active",
                    fault_id=record.fault_id,
                    code=f"FAULT_{record.fault_class.value}",
                )
            elif record.fault_class is FaultClass.NAVIGATION_TRUST_FAULT:
                register(
                    SafetyPosture.NAV_DEGRADED,
                    reason="navigation trust fault remains active",
                    fault_id=record.fault_id,
                    code=f"FAULT_{record.fault_class.value}",
                )
            elif record.fault_class is FaultClass.SENSOR_FAULT:
                register(
                    SafetyPosture.SENSOR_DEGRADED,
                    reason="sensor fault remains active",
                    fault_id=record.fault_id,
                    code=f"FAULT_{record.fault_class.value}",
                )
            elif record.fault_class is FaultClass.COMMUNICATION_FAULT:
                register(
                    SafetyPosture.COMMS_DEGRADED,
                    reason="communication fault remains active",
                    fault_id=record.fault_id,
                    code=f"FAULT_{record.fault_class.value}",
                )

        dominant_posture = self._select_dominant_posture(reasons, base_posture)
        contributing_fault_ids = tuple(sorted(fault_ids.get(dominant_posture, set())))
        contributing_trust_ids = tuple(sorted(trust_ids.get(dominant_posture, set())))
        dominant_causes = tuple(sorted(cause_codes.get(dominant_posture, set())))
        rationale = self._build_rationale(
            base_posture=base_posture,
            dominant_posture=dominant_posture,
            posture_reasons=reasons.get(dominant_posture, []),
        )

        transition = None
        if dominant_posture is not base_posture:
            transition = ModeTransition(
                previous_posture=base_posture,
                new_posture=dominant_posture,
                transition_time=self._transition_time(
                    base_posture=base_posture,
                    dominant_posture=dominant_posture,
                    trust_records=allocation_input.trust_records,
                    fault_records=allocation_input.fault_records,
                    contributing_fault_ids=contributing_fault_ids,
                    contributing_trust_ids=contributing_trust_ids,
                ),
                cause_codes=dominant_causes,
                contributing_fault_ids=contributing_fault_ids,
                contributing_trust_record_ids=contributing_trust_ids,
                rationale_summary=rationale,
            )

        return ModeAllocationResult(
            dominant_posture=dominant_posture,
            transition=transition,
            rationale_summary=rationale,
            active_degradation_flags=allocation_input.active_degradation_flags,
            contributing_fault_ids=contributing_fault_ids,
            contributing_trust_record_ids=contributing_trust_ids,
            metadata={
                "base_posture": base_posture.value,
                "dominant_posture": dominant_posture.value,
            },
        )

    @staticmethod
    def _select_dominant_posture(
        reasons: dict[SafetyPosture, list[str]],
        base_posture: SafetyPosture,
    ) -> SafetyPosture:
        if not reasons:
            return base_posture

        selected = base_posture
        selected_rank = _PRECEDENCE.get(base_posture, 0)

        for posture in reasons:
            rank = _PRECEDENCE.get(posture, 0)
            if rank > selected_rank:
                selected = posture
                selected_rank = rank
        return selected

    @staticmethod
    def _build_rationale(
        *,
        base_posture: SafetyPosture,
        dominant_posture: SafetyPosture,
        posture_reasons: list[str],
    ) -> str:
        if dominant_posture is base_posture:
            return f"mode allocation retained {dominant_posture.value} posture"

        if posture_reasons:
            joined = "; ".join(posture_reasons)
            return (
                f"mode allocation escalated from {base_posture.value} to "
                f"{dominant_posture.value}: {joined}"
            )

        return (
            f"mode allocation escalated from {base_posture.value} to "
            f"{dominant_posture.value}"
        )

    @staticmethod
    def _transition_time(
        *,
        base_posture: SafetyPosture,
        dominant_posture: SafetyPosture,
        trust_records: dict[str, TrustRecord],
        fault_records: dict[str, FaultRecord],
        contributing_fault_ids: tuple[str, ...],
        contributing_trust_ids: tuple[str, ...],
    ) -> datetime:
        if dominant_posture is base_posture:
            return utc_now()

        candidates: list[datetime] = []

        for trust_id in contributing_trust_ids:
            for record in trust_records.values():
                if record.trust_record_id == trust_id:
                    candidates.append(record.last_transition_timestamp)

        for fault_id in contributing_fault_ids:
            for record in fault_records.values():
                if record.fault_id == fault_id:
                    candidates.append(record.latest_update_timestamp)

        return max(candidates) if candidates else utc_now()
