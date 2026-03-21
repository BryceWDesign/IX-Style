"""Executable verification scenario runner for IX-Style."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime
from typing import Any

from ix_style.core import DecisionPipeline, DecisionPipelineContext
from ix_style.core.enums import FaultLifecycleState
from ix_style.core.ids import IdFactory
from ix_style.fdir import BasicFDIREngine, FaultClass
from ix_style.fdir.models import FDIREvaluationResult, FaultRecord
from ix_style.messages import EvidenceBundleBuilder
from ix_style.modes import ModeAllocationInput, ModeAllocator
from ix_style.trust import BasicTrustEvaluator
from ix_style.trust.cause_codes import TRUST_CAUSE_NAV_SPOOF_SUSPECTED
from ix_style.trust.models import TrustEvaluationResult, TrustRecord

from .models import (
    EvidencePackage,
    VerificationResult,
    VerificationScenario,
)


@dataclass(slots=True)
class ScenarioRunner:
    """Runs one IX-Style scenario through trust, FDIR, mode, and decision stages."""

    pipeline: DecisionPipeline = field(default_factory=DecisionPipeline)
    trust_evaluator: BasicTrustEvaluator = field(default_factory=BasicTrustEvaluator)
    fdir_engine: BasicFDIREngine = field(default_factory=BasicFDIREngine)
    mode_allocator: ModeAllocator = field(default_factory=ModeAllocator)
    bundle_builder: EvidenceBundleBuilder = field(default_factory=EvidenceBundleBuilder)
    id_factory: IdFactory = field(default_factory=IdFactory)

    def run(self, scenario: VerificationScenario) -> VerificationResult:
        trust_records: dict[str, TrustRecord] = {}
        fault_records: dict[str, FaultRecord] = {}
        trust_results: list[TrustEvaluationResult] = []
        fault_results: list[FDIREvaluationResult] = []

        for check in scenario.trust_checks:
            key = self._trust_key(check.trust_domain.value, check.entity_id)
            result = self.trust_evaluator.evaluate(trust_records.get(key), check)
            trust_records[key] = result.record
            trust_results.append(result)

        for signal in scenario.fault_signals:
            key = self._fault_key(
                signal.fault_class.value,
                signal.detection_source,
                signal.affected_function_scope,
            )
            result = self.fdir_engine.evaluate(fault_records.get(key), signal)
            fault_records[key] = result.record
            fault_results.append(result)

        derived_flags = self._derive_active_degradation_flags(
            scenario=scenario,
            trust_records=trust_records,
            fault_records=fault_records,
        )
        mode_result = self.mode_allocator.evaluate(
            ModeAllocationInput(
                base_posture=scenario.safety_posture,
                active_degradation_flags=derived_flags,
                trust_records=trust_records,
                fault_records=fault_records,
            )
        )

        related_fault_ids = tuple(
            record.fault_id
            for record in fault_records.values()
            if record.lifecycle_state is not FaultLifecycleState.CLEARED
        )

        pipeline_result = self.pipeline.evaluate(
            DecisionPipelineContext(
                envelope=scenario.envelope,
                mission_phase=scenario.mission_phase,
                safety_posture=mode_result.dominant_posture,
                active_degradation_flags=derived_flags,
                related_fault_ids=related_fault_ids,
                trust_records=trust_records,
                fault_records=fault_records,
            )
        )

        pipeline_trace = {
            "recovery_decision_present": pipeline_result.recovery_decision is not None,
            "recovery_gate_status": (
                pipeline_result.recovery_decision.gate_status.value
                if pipeline_result.recovery_decision is not None
                else "NOT_APPLICABLE"
            ),
            "authority_decision_present": pipeline_result.authority_decision is not None,
            "authority_outcome": (
                pipeline_result.authority_decision.outcome.value
                if pipeline_result.authority_decision is not None
                else None
            ),
            "guard_decision_present": pipeline_result.guard_decision is not None,
            "guard_outcome": (
                pipeline_result.guard_decision.outcome.value
                if pipeline_result.guard_decision is not None
                else None
            ),
        }

        failures = self._evaluate_expectations(
            scenario=scenario,
            pipeline_result=pipeline_result,
            trust_results=trust_results,
            fault_results=fault_results,
            derived_flags=derived_flags,
        )
        passed = not failures

        trust_events = self._build_transition_event_records(trust_results)
        fault_events = self._build_transition_event_records(fault_results)
        mode_events = self._build_transition_event_records([mode_result])

        evidence_bundle = self.bundle_builder.build(
            scenario_id=scenario.scenario_id,
            decision_receipt=pipeline_result.receipt_payload.as_dict(),
            trust_transitions=tuple(trust_events),
            fault_transitions=tuple(fault_events),
            mode_transitions=tuple(mode_events),
        )

        evidence_package = EvidencePackage(
            scenario_id=scenario.scenario_id,
            scenario_name=scenario.name,
            linked_requirements=scenario.linked_requirements,
            linked_hazards=scenario.linked_hazards,
            generated_event_ids=tuple(
                [event["event_id"] for event in trust_events]
                + [event["event_id"] for event in fault_events]
                + [event["event_id"] for event in mode_events]
            ),
            generated_receipt_ids=(pipeline_result.decision_id,),
            expected_outcomes=self._expected_outcomes_dict(scenario),
            actual_observed_outcomes={
                "final_outcome": pipeline_result.receipt_payload.final_outcome.value,
                "final_authoritative_source": (
                    pipeline_result.receipt_payload.final_authoritative_source.value
                ),
                "recovery_gate_result": pipeline_result.receipt_payload.recovery_gate_result,
                "derived_active_degradation_flags": list(derived_flags),
                "derived_dominant_safety_posture": mode_result.dominant_posture.value,
                "trust_transition_count": len(trust_events),
                "fault_transition_count": len(fault_events),
                "mode_transition_count": len(mode_events),
                "related_fault_ids": list(related_fault_ids),
                "pipeline_trace": pipeline_trace,
            },
            decision_receipt=pipeline_result.receipt_payload.as_dict(),
            trust_transitions=tuple(trust_events),
            fault_transitions=tuple(fault_events),
            mode_transitions=tuple(mode_events),
            evidence_bundle=evidence_bundle,
            pass_fail_result=passed,
            rationale=(
                "scenario satisfied all declared expectations"
                if passed
                else "; ".join(failures)
            ),
            limitations_or_assumptions=scenario.limitations_or_assumptions,
        )

        return VerificationResult(
            scenario=scenario,
            evidence_package=evidence_package,
            passed=passed,
            failures=tuple(failures),
            derived_active_degradation_flags=derived_flags,
            derived_dominant_safety_posture=mode_result.dominant_posture,
            trust_records=trust_records,
            fault_records=fault_records,
            pipeline_trace=pipeline_trace,
        )

    @staticmethod
    def _trust_key(domain: str, entity_id: str) -> str:
        return f"{domain}:{entity_id}"

    @staticmethod
    def _fault_key(fault_class: str, detection_source: str, scope: str) -> str:
        return f"{fault_class}:{detection_source}:{scope}"

    def _derive_active_degradation_flags(
        self,
        *,
        scenario: VerificationScenario,
        trust_records: dict[str, TrustRecord],
        fault_records: dict[str, FaultRecord],
    ) -> tuple[str, ...]:
        flags: list[str] = list(scenario.active_degradation_flags)

        for record in trust_records.values():
            if record.current_trust_state.value not in {
                "DEGRADED",
                "SUSPECT",
                "UNTRUSTED",
                "UNAVAILABLE",
            }:
                continue

            if record.trust_domain.value == "NAVIGATION_TRUST":
                if TRUST_CAUSE_NAV_SPOOF_SUSPECTED in record.transition_cause_codes:
                    flags.append("nav_spoof_suspected")
                else:
                    flags.append("nav_corroboration_lost")
            elif record.trust_domain.value == "SENSOR_SOURCE_TRUST":
                flags.append("sensor_trust_low")
            elif record.trust_domain.value == "TIMING_TRUST":
                flags.append("timing_validity_low")
            elif record.trust_domain.value == "MESSAGE_TRUST":
                flags.append("command_freshness_low")
            elif record.trust_domain.value == "ACTUATOR_CONFIDENCE":
                flags.append("actuator_response_uncertain")
            elif record.trust_domain.value == "ASSURANCE_CONFIDENCE":
                flags.append("assurance_guard_unhealthy")

        for record in fault_records.values():
            if record.lifecycle_state is FaultLifecycleState.CLEARED:
                continue

            if record.fault_class is FaultClass.POWER_RESOURCE_FAULT:
                flags.append("power_margin_low")
            elif record.fault_class is FaultClass.ACTUATION_FAULT:
                flags.append("actuator_response_uncertain")
            elif record.fault_class is FaultClass.ASSURANCE_FAULT:
                flags.append("assurance_guard_unhealthy")
            elif record.fault_class is FaultClass.COMMUNICATION_FAULT:
                flags.append("comms_link_intermittent")
            elif record.fault_class is FaultClass.SENSOR_FAULT:
                flags.append("sensor_trust_low")
            elif record.fault_class is FaultClass.NAVIGATION_TRUST_FAULT:
                flags.append("nav_corroboration_lost")

        deduped: list[str] = []
        for item in flags:
            if item not in deduped:
                deduped.append(item)
        return tuple(deduped)

    def _evaluate_expectations(
        self,
        *,
        scenario: VerificationScenario,
        pipeline_result: Any,
        trust_results: list[TrustEvaluationResult],
        fault_results: list[FDIREvaluationResult],
        derived_flags: tuple[str, ...],
    ) -> list[str]:
        failures: list[str] = []
        expectations = scenario.expectations
        receipt = pipeline_result.receipt_payload.as_dict()

        if (
            expectations.expected_final_outcome is not None
            and pipeline_result.receipt_payload.final_outcome
            is not expectations.expected_final_outcome
        ):
            failures.append(
                "expected final outcome "
                f"{expectations.expected_final_outcome.value} but observed "
                f"{pipeline_result.receipt_payload.final_outcome.value}"
            )

        if expectations.require_trust_transition and not any(
            result.transition is not None for result in trust_results
        ):
            failures.append("expected at least one trust transition but none occurred")

        if expectations.require_fault_transition and not any(
            result.transition is not None for result in fault_results
        ):
            failures.append("expected at least one fault transition but none occurred")

        missing_flags = sorted(
            set(expectations.required_active_degradation_flags).difference(derived_flags)
        )
        if missing_flags:
            failures.append(
                "required degradation flags missing: " + ", ".join(missing_flags)
            )

        missing_receipt_fields = sorted(
            field_name
            for field_name in expectations.required_receipt_fields
            if field_name not in receipt
        )
        if missing_receipt_fields:
            failures.append(
                "decision receipt missing required fields: "
                + ", ".join(missing_receipt_fields)
            )

        return failures

    def _build_transition_event_records(self, results: list[Any]) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        for result in results:
            transition = getattr(result, "transition", None)
            rationale_summary = getattr(result, "rationale_summary", "")
            if transition is None:
                continue
            transition_time = getattr(transition, "transition_time")
            events.append(
                {
                    "event_id": self.id_factory.event_id(),
                    "event_time": self._serialize_time(transition_time),
                    "summary": rationale_summary,
                    "payload": self._serialize_dataclass(transition),
                }
            )
        return events

    @staticmethod
    def _serialize_dataclass(value: Any) -> dict[str, Any]:
        if not is_dataclass(value):
            raise TypeError("expected a dataclass instance")
        return ScenarioRunner._serialize_any(asdict(value))

    @staticmethod
    def _serialize_any(value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        if hasattr(value, "value"):
            return value.value
        if isinstance(value, list):
            return [ScenarioRunner._serialize_any(item) for item in value]
        if isinstance(value, tuple):
            return [ScenarioRunner._serialize_any(item) for item in value]
        if isinstance(value, dict):
            return {
                key: ScenarioRunner._serialize_any(item)
                for key, item in value.items()
            }
        return value

    @staticmethod
    def _serialize_time(value: datetime) -> str:
        return value.isoformat()

    @staticmethod
    def _expected_outcomes_dict(scenario: VerificationScenario) -> dict[str, Any]:
        expectations = scenario.expectations
        return {
            "expected_final_outcome": (
                expectations.expected_final_outcome.value
                if expectations.expected_final_outcome is not None
                else None
            ),
            "require_trust_transition": expectations.require_trust_transition,
            "require_fault_transition": expectations.require_fault_transition,
            "required_active_degradation_flags": list(
                expectations.required_active_degradation_flags
            ),
            "required_receipt_fields": list(expectations.required_receipt_fields),
        }
