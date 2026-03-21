"""Executable mission-health snapshot builder for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from ix_style.core.enums import (
    ArbitrationOutcome,
    FaultLifecycleState,
    ReviewSignificance,
    SafetyPosture,
    TrustDomain,
    TrustState,
)
from ix_style.core.ids import IdFactory
from ix_style.fdir.models import FaultPriority, FaultRecord
from ix_style.trust.models import TrustRecord
if TYPE_CHECKING:
    from ix_style.verification.models import VerificationResult


_PRIORITY_ORDER: dict[str, int] = {
    "P1_CONTAINMENT_CRITICAL": 4,
    "P2_HIGH": 3,
    "P3_MODERATE": 2,
    "P4_LOW": 1,
    "NONE": 0,
}


@dataclass(slots=True)
class MissionHealthBuilder:
    """Builds operator-facing mission-health snapshots from verification results."""

    id_factory: IdFactory = field(default_factory=IdFactory)
    schema_version: str = "0.1.0"

    def build_from_verification(self, result: VerificationResult) -> dict[str, Any]:
        """Build a mission-health snapshot from one executed verification result."""
        snapshot_time = _utc_now()
        dominant_posture = result.derived_dominant_safety_posture
        active_fault_records = self._active_fault_records(result.fault_records)
        highest_priority = self._highest_priority(active_fault_records)
        review_significance = self._derive_review_significance(
            dominant_posture=dominant_posture,
            highest_priority=highest_priority,
            decision_outcome=result.evidence_package.decision_receipt["final_outcome"],
        )

        recovery_summary = self._build_recovery_summary(active_fault_records)
        authority_summary = self._build_authority_summary(
            result=result,
            dominant_posture=dominant_posture,
            recovery_summary=recovery_summary,
        )
        trust_summary = self._build_trust_summary(result.trust_records)
        active_fault_summary = self._build_fault_summary(active_fault_records)
        resource_summary = self._build_resource_summary(
            dominant_posture=dominant_posture,
            active_flags=result.derived_active_degradation_flags,
        )
        recent_events = self._build_recent_events(
            result=result,
            dominant_posture=dominant_posture,
            review_significance=review_significance,
        )

        return {
            "schema_version": self.schema_version,
            "snapshot_id": self.id_factory.snapshot_id(),
            "snapshot_time": snapshot_time.isoformat(),
            "mission_phase": result.scenario.mission_phase.value,
            "dominant_safety_posture": dominant_posture.value,
            "containment_status": self._containment_status(
                dominant_posture=dominant_posture,
                active_fault_records=active_fault_records,
            ),
            "review_significance": review_significance.value,
            "authority_summary": authority_summary,
            "trust_summary": trust_summary,
            "active_fault_summary": active_fault_summary,
            "recovery_summary": recovery_summary,
            "resource_summary": resource_summary,
            "recent_critical_event_count": sum(
                1
                for event in recent_events
                if event["review_significance"] == ReviewSignificance.CRITICAL.value
            ),
            "delayed_link_indicator": self._delayed_link_indicator(
                result.derived_active_degradation_flags
            ),
            "recent_events": recent_events,
        }

    @staticmethod
    def _active_fault_records(records: dict[str, FaultRecord]) -> list[FaultRecord]:
        return [
            record
            for record in records.values()
            if record.lifecycle_state is not FaultLifecycleState.CLEARED
        ]

    def _highest_priority(self, active_fault_records: list[FaultRecord]) -> str:
        if not active_fault_records:
            return "NONE"
        return max(
            (record.current_priority.value for record in active_fault_records),
            key=lambda value: _PRIORITY_ORDER[value],
        )

    def _derive_review_significance(
        self,
        *,
        dominant_posture: SafetyPosture,
        highest_priority: str,
        decision_outcome: str,
    ) -> ReviewSignificance:
        if (
            dominant_posture is SafetyPosture.SAFE_HOLD
            or decision_outcome
            in {
                ArbitrationOutcome.VETO.value,
                ArbitrationOutcome.FREEZE.value,
                ArbitrationOutcome.ESCALATE_TO_MODE_CHANGE.value,
            }
        ):
            return ReviewSignificance.CRITICAL

        if dominant_posture in {
            SafetyPosture.ASSURANCE_DEGRADED,
            SafetyPosture.POWER_DEGRADED,
            SafetyPosture.ACTUATION_DEGRADED,
            SafetyPosture.NAV_DEGRADED,
        }:
            return ReviewSignificance.HIGH

        if decision_outcome in {
            ArbitrationOutcome.CLAMP.value,
            ArbitrationOutcome.SUBSTITUTE.value,
            ArbitrationOutcome.REJECT.value,
            ArbitrationOutcome.DEFER.value,
        }:
            return ReviewSignificance.IMPORTANT

        return ReviewSignificance.ROUTINE

    def _containment_status(
        self,
        *,
        dominant_posture: SafetyPosture,
        active_fault_records: list[FaultRecord],
    ) -> str:
        if dominant_posture is SafetyPosture.SAFE_HOLD:
            return "CONTAINMENT_ACTIVE"

        if any(record.lifecycle_state is FaultLifecycleState.LATCHED for record in active_fault_records):
            return "CONTAINMENT_LOCKED"

        if dominant_posture in {
            SafetyPosture.ASSURANCE_DEGRADED,
            SafetyPosture.POWER_DEGRADED,
            SafetyPosture.ACTUATION_DEGRADED,
            SafetyPosture.NAV_DEGRADED,
            SafetyPosture.SENSOR_DEGRADED,
            SafetyPosture.COMMS_DEGRADED,
        }:
            return "CONTAINMENT_ELEVATED"

        return "CONTAINMENT_NONE"

    def _build_authority_summary(
        self,
        *,
        result: VerificationResult,
        dominant_posture: SafetyPosture,
        recovery_summary: dict[str, Any],
    ) -> dict[str, Any]:
        receipt = result.evidence_package.decision_receipt
        final_outcome = receipt["final_outcome"]
        final_source = receipt["final_authoritative_source"]

        if final_outcome == ArbitrationOutcome.FREEZE.value:
            nominal_status = "BLOCKED"
        elif final_outcome in {
            ArbitrationOutcome.CLAMP.value,
            ArbitrationOutcome.SUBSTITUTE.value,
            ArbitrationOutcome.REJECT.value,
            ArbitrationOutcome.VETO.value,
        }:
            nominal_status = "NARROWED"
        else:
            nominal_status = "NORMAL"

        if dominant_posture is SafetyPosture.SAFE_HOLD:
            supervisor_bias = "LOCKED_CONTAINMENT"
        elif final_outcome in {
            ArbitrationOutcome.VETO.value,
            ArbitrationOutcome.FREEZE.value,
            ArbitrationOutcome.ESCALATE_TO_MODE_CHANGE.value,
        }:
            supervisor_bias = "CONTAINMENT_BIASED"
        elif dominant_posture in {
            SafetyPosture.ASSURANCE_DEGRADED,
            SafetyPosture.POWER_DEGRADED,
            SafetyPosture.ACTUATION_DEGRADED,
            SafetyPosture.NAV_DEGRADED,
            SafetyPosture.SENSOR_DEGRADED,
            SafetyPosture.COMMS_DEGRADED,
        }:
            supervisor_bias = "ELEVATED"
        else:
            supervisor_bias = "NORMAL"

        flags = set(result.derived_active_degradation_flags)
        if "command_freshness_low" in flags:
            remote_operator_status = "STALE_REJECTED"
        elif "comms_link_intermittent" in flags:
            remote_operator_status = "LINK_UNAVAILABLE"
        else:
            remote_operator_status = "ACCEPTED"

        frozen_paths: list[str] = []
        if final_outcome == ArbitrationOutcome.FREEZE.value:
            frozen_paths.append(receipt["candidate_action_summary"]["function_class"])

        return {
            "dominant_authoritative_source": final_source,
            "nominal_autonomy_status": nominal_status,
            "contingency_logic_status": (
                "DOMINANT_FOR_SCOPE" if final_source == "CONTINGENCY_LOGIC" else "AVAILABLE"
            ),
            "safety_supervisor_bias": supervisor_bias,
            "remote_operator_command_status": remote_operator_status,
            "frozen_command_paths": frozen_paths,
            "recovery_action_status": self._authority_recovery_status(recovery_summary),
        }

    @staticmethod
    def _authority_recovery_status(recovery_summary: dict[str, Any]) -> str:
        state = recovery_summary["recovery_state"]
        if state == "RECOVERY_QUALIFIED":
            return "QUALIFIED"
        if state == "RECOVERY_UNDER_REVIEW":
            return "UNDER_REVIEW"
        if state == "RECOVERY_BLOCKED":
            return "BLOCKED"
        if state == "RECOVERY_NOT_APPLICABLE":
            return "NOT_APPLICABLE"
        return "ALLOWED"

    def _build_trust_summary(self, records: dict[str, TrustRecord]) -> dict[str, Any]:
        by_domain = {record.trust_domain: record for record in records.values()}
        posture_driving = next(
            (
                record.trust_domain.value
                for record in records.values()
                if record.posture_driving
            ),
            "",
        )

        return {
            "navigation_trust": self._trust_value(by_domain.get(TrustDomain.NAVIGATION_TRUST)),
            "sensor_source_aggregate_trust": self._trust_value(
                by_domain.get(TrustDomain.SENSOR_SOURCE_TRUST)
            ),
            "derived_state_trust": self._trust_value(
                by_domain.get(TrustDomain.DERIVED_STATE_TRUST)
            ),
            "timing_trust": self._trust_value(by_domain.get(TrustDomain.TIMING_TRUST)),
            "actuator_confidence": self._trust_value(
                by_domain.get(TrustDomain.ACTUATOR_CONFIDENCE)
            ),
            "assurance_confidence": self._trust_value(
                by_domain.get(TrustDomain.ASSURANCE_CONFIDENCE)
            ),
            "control_plane_message_trust": self._trust_value(
                by_domain.get(TrustDomain.MESSAGE_TRUST)
            ),
            "posture_driving_trust_domain": posture_driving,
            "recent_trust_transition_summaries": [
                record.rationale_summary
                for record in records.values()
                if record.evidence_required
            ][:5],
        }

    @staticmethod
    def _trust_value(record: TrustRecord | None) -> str:
        return record.current_trust_state.value if record is not None else TrustState.TRUSTED.value

    def _build_fault_summary(self, active_fault_records: list[FaultRecord]) -> dict[str, Any]:
        top_faults = sorted(
            active_fault_records,
            key=lambda record: _PRIORITY_ORDER[record.current_priority.value],
            reverse=True,
        )[:10]

        return {
            "highest_active_fault_priority": self._highest_priority(active_fault_records),
            "active_fault_count": len(active_fault_records),
            "blocking_latched_fault_count": sum(
                1 for record in active_fault_records if record.lifecycle_state is FaultLifecycleState.LATCHED
            ),
            "top_fault_ids": [record.fault_id for record in top_faults],
            "mitigation_in_progress": any(
                record.lifecycle_state
                in {
                    FaultLifecycleState.MITIGATING,
                    FaultLifecycleState.CONTAINED,
                    FaultLifecycleState.RECOVERING,
                }
                for record in active_fault_records
            ),
            "mitigation_failure_flag": any(
                "failed" in record.rationale_summary.lower() for record in active_fault_records
            ),
        }

    def _build_recovery_summary(self, active_fault_records: list[FaultRecord]) -> dict[str, Any]:
        if any(record.lifecycle_state is FaultLifecycleState.RECOVERING for record in active_fault_records):
            return {
                "recovery_state": "RECOVERY_UNDER_REVIEW",
                "blocking_reason_summary": "",
                "related_fault_ids": [
                    record.fault_id
                    for record in active_fault_records
                    if record.lifecycle_state is FaultLifecycleState.RECOVERING
                ],
                "recovery_gate_result": "DEFERRED",
            }

        latched = [
            record for record in active_fault_records if record.lifecycle_state is FaultLifecycleState.LATCHED
        ]
        if latched:
            return {
                "recovery_state": "RECOVERY_BLOCKED",
                "blocking_reason_summary": "one or more blocking latched faults remain active",
                "related_fault_ids": [record.fault_id for record in latched],
                "recovery_gate_result": "FAILED",
            }

        if active_fault_records:
            return {
                "recovery_state": "RECOVERY_BLOCKED",
                "blocking_reason_summary": "active fault containment remains in effect",
                "related_fault_ids": [record.fault_id for record in active_fault_records],
                "recovery_gate_result": "FAILED",
            }

        return {
            "recovery_state": "RECOVERY_NOT_APPLICABLE",
            "blocking_reason_summary": "",
            "related_fault_ids": [],
            "recovery_gate_result": "NOT_APPLICABLE",
        }

    def _build_resource_summary(
        self,
        *,
        dominant_posture: SafetyPosture,
        active_flags: tuple[str, ...],
    ) -> dict[str, Any]:
        flags = set(active_flags)
        power_related = "power_margin_low" in flags or dominant_posture is SafetyPosture.POWER_DEGRADED

        return {
            "resource_posture": (
                SafetyPosture.POWER_DEGRADED.value if power_related else "RESOURCE_NOMINAL"
            ),
            "essential_functions_preserved": True,
            "load_shed_active": power_related,
            "safe_hold_support_capable": "assurance_guard_unhealthy" not in flags,
            "survivability_bias_active": power_related
            or dominant_posture is SafetyPosture.SAFE_HOLD,
        }

    def _build_recent_events(
        self,
        *,
        result: VerificationResult,
        dominant_posture: SafetyPosture,
        review_significance: ReviewSignificance,
    ) -> list[dict[str, Any]]:
        recent_events: list[dict[str, Any]] = []
        decision_receipt = result.evidence_package.decision_receipt

        for item in result.evidence_package.mode_transitions:
            payload = item["payload"]
            recent_events.append(
                {
                    "event_id": item["event_id"],
                    "event_time": item["event_time"],
                    "event_class": "MODE_EVENT",
                    "event_type": "mode.transition",
                    "review_significance": (
                        ReviewSignificance.HIGH.value
                        if payload["new_posture"] != SafetyPosture.NOMINAL.value
                        else ReviewSignificance.IMPORTANT.value
                    ),
                    "summary": item["summary"],
                    "affected_scope": payload["new_posture"],
                    "related_fault_ids": payload["contributing_fault_ids"],
                    "related_trust_record_ids": payload["contributing_trust_record_ids"],
                    "resulting_safety_posture": payload["new_posture"],
                    "resulting_authority_implication": self._authority_implication(
                        dominant_posture
                    ),
                    "linked_evidence_id": decision_receipt["decision_id"],
                }
            )

        for item in result.evidence_package.trust_transitions:
            payload = item["payload"]
            recent_events.append(
                {
                    "event_id": item["event_id"],
                    "event_time": item["event_time"],
                    "event_class": "TRUST_EVENT",
                    "event_type": "trust.transition",
                    "review_significance": (
                        ReviewSignificance.HIGH.value
                        if payload["posture_driving"]
                        else ReviewSignificance.IMPORTANT.value
                    ),
                    "summary": item["summary"],
                    "affected_scope": payload["affected_entity_id"],
                    "related_fault_ids": [],
                    "related_trust_record_ids": [payload["trust_record_id"]],
                    "resulting_safety_posture": dominant_posture.value,
                    "resulting_authority_implication": self._authority_implication(dominant_posture),
                    "linked_evidence_id": decision_receipt["decision_id"],
                }
            )

        for item in result.evidence_package.fault_transitions:
            payload = item["payload"]
            significance = (
                ReviewSignificance.CRITICAL.value
                if payload["priority_after"] == FaultPriority.P1_CONTAINMENT_CRITICAL.value
                else ReviewSignificance.HIGH.value
            )
            recent_events.append(
                {
                    "event_id": item["event_id"],
                    "event_time": item["event_time"],
                    "event_class": "FAULT_EVENT",
                    "event_type": "fault.lifecycle_update",
                    "review_significance": significance,
                    "summary": item["summary"],
                    "affected_scope": payload["fault_id"],
                    "related_fault_ids": [payload["fault_id"]],
                    "related_trust_record_ids": [],
                    "resulting_safety_posture": dominant_posture.value,
                    "resulting_authority_implication": self._authority_implication(dominant_posture),
                    "linked_evidence_id": decision_receipt["decision_id"],
                }
            )

        recent_events.append(
            {
                "event_id": self.id_factory.event_id(),
                "event_time": _utc_now().isoformat(),
                "event_class": "EVIDENCE",
                "event_type": "evidence.decision_receipt",
                "review_significance": review_significance.value,
                "summary": decision_receipt["rationale_summary"],
                "affected_scope": decision_receipt["candidate_action_summary"]["function_class"],
                "related_fault_ids": decision_receipt["related_fault_ids"],
                "related_trust_record_ids": [],
                "resulting_safety_posture": dominant_posture.value,
                "resulting_authority_implication": (
                    decision_receipt["final_authoritative_source"]
                ),
                "linked_evidence_id": decision_receipt["decision_id"],
            }
        )

        recent_events.sort(key=lambda item: item["event_time"], reverse=False)
        return recent_events[-10:]

    @staticmethod
    def _authority_implication(dominant_posture: SafetyPosture) -> str:
        if dominant_posture is SafetyPosture.SAFE_HOLD:
            return "containment_only_actions_allowed"
        if dominant_posture is SafetyPosture.ASSURANCE_DEGRADED:
            return "high_risk_paths_frozen_or_narrowed"
        if dominant_posture in {
            SafetyPosture.POWER_DEGRADED,
            SafetyPosture.ACTUATION_DEGRADED,
            SafetyPosture.NAV_DEGRADED,
            SafetyPosture.SENSOR_DEGRADED,
            SafetyPosture.COMMS_DEGRADED,
        }:
            return "bounded_degraded_operation"
        return "nominal_bounded_operation"

    @staticmethod
    def _delayed_link_indicator(active_flags: tuple[str, ...]) -> bool:
        return "comms_link_intermittent" in set(active_flags)


def _utc_now() -> datetime:
    """Return an aware UTC timestamp."""
    return datetime.now(tz=UTC)
