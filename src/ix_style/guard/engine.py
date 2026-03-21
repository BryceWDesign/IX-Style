"""Baseline runtime-assurance guard for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from ix_style.core.enums import (
    ArbitrationOutcome,
)

from .constraints import BaselineConstraintCatalog
from .models import GuardContext, GuardDecision


class GuardEngine(Protocol):
    """Protocol for runtime-assurance guard engines."""

    def evaluate(self, context: GuardContext) -> GuardDecision:
        """Evaluate whether an authority-approved command remains safe enough to use."""


@dataclass(slots=True)
class SimpleGuardEngine:
    """Baseline guard with explicit named constraint evaluation."""

    constraint_catalog: BaselineConstraintCatalog = field(
        default_factory=BaselineConstraintCatalog
    )

    def evaluate(self, context: GuardContext) -> GuardDecision:
        evaluation = self.constraint_catalog.evaluate(context)
        selected = evaluation.selected_match

        if selected is None:
            return GuardDecision(
                outcome=ArbitrationOutcome.ACCEPT,
                final_authoritative_source=context.authority_decision.final_authoritative_source,
                rationale_summary="guard accepted the candidate command within current bounds",
                policy_evaluation_result="ALLOWED",
                triggered_constraint_ids=("GUARD-BASELINE-ALLOW",),
                command_delta={"change_type": "NONE"},
            )

        recovery_gate_result = selected.metadata.get(
            "recovery_gate_status",
            "NOT_APPLICABLE",
        )
        return GuardDecision(
            outcome=selected.outcome,
            final_authoritative_source=selected.final_authoritative_source,
            rationale_summary=selected.rationale_summary,
            policy_evaluation_result=selected.policy_evaluation_result,
            triggered_constraint_ids=tuple(
                match.constraint_id for match in evaluation.matches
            ),
            mode_escalation_requested=selected.mode_escalation_requested,
            resulting_mode_target=selected.resulting_mode_target,
            command_delta=selected.command_delta,
            recovery_gate_result=recovery_gate_result,
            metadata=selected.metadata,
        )
