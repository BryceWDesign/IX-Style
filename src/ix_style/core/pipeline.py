"""Executable decision pipeline skeleton for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ix_style.authority.engine import AuthorityEngine, StaticAuthorityEngine
from ix_style.authority.models import AuthorityContext, AuthorityDecision
from ix_style.guard.engine import GuardEngine, SimpleGuardEngine
from ix_style.guard.models import GuardContext, GuardDecision

from .enums import (
    ArbitrationOutcome,
    CommandSource,
    MessageClass,
    MissionPhase,
    SafetyPosture,
)
from .ids import IdFactory
from .models import ControlPayload, DecisionReceiptPayload, MessageEnvelope


@dataclass(slots=True, frozen=True)
class DecisionPipelineContext:
    """Inputs required to execute the IX-Style decision pipeline."""

    envelope: MessageEnvelope
    mission_phase: MissionPhase
    safety_posture: SafetyPosture
    active_degradation_flags: tuple[str, ...] = ()
    related_fault_ids: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class PipelineDecision:
    """Structured result from one pipeline evaluation."""

    decision_id: str
    authority_decision: AuthorityDecision
    guard_decision: GuardDecision | None
    receipt_payload: DecisionReceiptPayload


@dataclass(slots=True)
class DecisionPipeline:
    """Reference decision pipeline: authority -> guard -> receipt."""

    authority_engine: AuthorityEngine = field(default_factory=StaticAuthorityEngine)
    guard_engine: GuardEngine = field(default_factory=SimpleGuardEngine)
    id_factory: IdFactory = field(default_factory=IdFactory)

    def evaluate(self, context: DecisionPipelineContext) -> PipelineDecision:
        """Run one candidate control message through the reference decision path."""
        decision_id = self.id_factory.decision_id()

        authority_context = AuthorityContext(
            envelope=context.envelope,
            mission_phase=context.mission_phase,
            safety_posture=context.safety_posture,
            active_degradation_flags=context.active_degradation_flags,
        )
        authority_decision = self.authority_engine.evaluate(authority_context)

        if authority_decision.outcome is not ArbitrationOutcome.ACCEPT:
            receipt = self._build_receipt_from_authority_stage(
                decision_id=decision_id,
                context=context,
                authority_decision=authority_decision,
            )
            return PipelineDecision(
                decision_id=decision_id,
                authority_decision=authority_decision,
                guard_decision=None,
                receipt_payload=receipt,
            )

        guard_context = GuardContext(
            envelope=context.envelope,
            mission_phase=context.mission_phase,
            safety_posture=context.safety_posture,
            authority_decision=authority_decision,
            active_degradation_flags=context.active_degradation_flags,
        )
        guard_decision = self.guard_engine.evaluate(guard_context)
        receipt = self._build_receipt_from_guard_stage(
            decision_id=decision_id,
            context=context,
            authority_decision=authority_decision,
            guard_decision=guard_decision,
        )
        return PipelineDecision(
            decision_id=decision_id,
            authority_decision=authority_decision,
            guard_decision=guard_decision,
            receipt_payload=receipt,
        )

    def _build_receipt_from_authority_stage(
        self,
        *,
        decision_id: str,
        context: DecisionPipelineContext,
        authority_decision: AuthorityDecision,
    ) -> DecisionReceiptPayload:
        payload = self._candidate_action_summary(context.envelope)
        return DecisionReceiptPayload(
            decision_id=decision_id,
            candidate_action_summary=payload,
            final_outcome=authority_decision.outcome,
            final_authoritative_source=authority_decision.final_authoritative_source,
            mission_phase=context.mission_phase,
            safety_posture=context.safety_posture,
            active_degradation_flags=list(context.active_degradation_flags),
            trust_posture_summary={},
            related_fault_ids=list(context.related_fault_ids),
            triggered_constraint_ids=list(authority_decision.rule_ids),
            policy_evaluation_result=authority_decision.policy_evaluation_result,
            recovery_gate_result=authority_decision.recovery_gate_result,
            command_delta={"change_type": "NONE"},
            mode_escalation_requested=authority_decision.mode_escalation_requested,
            rationale_summary=authority_decision.rationale_summary,
        )

    def _build_receipt_from_guard_stage(
        self,
        *,
        decision_id: str,
        context: DecisionPipelineContext,
        authority_decision: AuthorityDecision,
        guard_decision: GuardDecision,
    ) -> DecisionReceiptPayload:
        payload = self._candidate_action_summary(context.envelope)
        payload["requested_by"] = authority_decision.final_authoritative_source.value

        return DecisionReceiptPayload(
            decision_id=decision_id,
            candidate_action_summary=payload,
            final_outcome=guard_decision.outcome,
            final_authoritative_source=guard_decision.final_authoritative_source,
            mission_phase=context.mission_phase,
            safety_posture=context.safety_posture,
            active_degradation_flags=list(context.active_degradation_flags),
            trust_posture_summary={},
            related_fault_ids=list(context.related_fault_ids),
            triggered_constraint_ids=list(guard_decision.triggered_constraint_ids),
            policy_evaluation_result=guard_decision.policy_evaluation_result,
            recovery_gate_result=guard_decision.recovery_gate_result,
            command_delta=guard_decision.command_delta,
            mode_escalation_requested=guard_decision.mode_escalation_requested,
            resulting_mode_target=(
                guard_decision.resulting_mode_target.value
                if guard_decision.resulting_mode_target is not None
                else None
            ),
            rationale_summary=guard_decision.rationale_summary,
        )

    @staticmethod
    def _candidate_action_summary(envelope: MessageEnvelope) -> dict[str, Any]:
        """Build a compact action summary for evidence generation."""
        if envelope.message_class is not MessageClass.CONTROL:
            return {
                "function_class": "UNKNOWN",
                "requested_action": envelope.message_type,
                "requested_by": CommandSource.NONE.value,
            }

        payload = envelope.payload
        if not isinstance(payload, ControlPayload):
            return {
                "function_class": "UNKNOWN",
                "requested_action": envelope.message_type,
                "requested_by": CommandSource.NONE.value,
            }

        return {
            "function_class": payload.function_class.value,
            "requested_action": payload.requested_action,
            "requested_by": payload.command_source.value,
            "requested_scope": payload.requested_scope,
            "requested_magnitude": payload.requested_magnitude,
            "requested_duration_ms": payload.requested_duration_ms,
        }
