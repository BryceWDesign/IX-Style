"""Baseline authority engine for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Protocol

from ix_style.core.enums import (
    ArbitrationOutcome,
    AuthState,
    CommandSource,
    FreshnessState,
    FunctionClass,
    IntegrityState,
    MessageClass,
    SafetyPosture,
)

from .models import AuthorityContext, AuthorityDecision

_ALLOWED_SOURCES: Final[dict[FunctionClass, frozenset[CommandSource]]] = {
    FunctionClass.MODE_MANAGEMENT: frozenset(
        {
            CommandSource.OPERATOR,
            CommandSource.CONTINGENCY_LOGIC,
            CommandSource.SAFETY_SUPERVISOR,
        }
    ),
    FunctionClass.MISSION_INTENT: frozenset(
        {
            CommandSource.OPERATOR,
            CommandSource.MISSION_LOGIC,
        }
    ),
    FunctionClass.GUIDANCE_REQUEST: frozenset(
        {
            CommandSource.NOMINAL_AUTONOMY,
            CommandSource.CONTINGENCY_LOGIC,
            CommandSource.OPERATOR,
            CommandSource.SAFETY_SUPERVISOR,
        }
    ),
    FunctionClass.ACTUATION_REQUEST: frozenset(
        {
            CommandSource.NOMINAL_AUTONOMY,
            CommandSource.CONTINGENCY_LOGIC,
            CommandSource.OPERATOR,
            CommandSource.SAFETY_SUPERVISOR,
        }
    ),
    FunctionClass.RESOURCE_CONFIGURATION: frozenset(
        {
            CommandSource.MISSION_LOGIC,
            CommandSource.CONTINGENCY_LOGIC,
            CommandSource.OPERATOR,
            CommandSource.SAFETY_SUPERVISOR,
        }
    ),
    FunctionClass.RECOVERY_ACTION: frozenset(
        {
            CommandSource.OPERATOR,
            CommandSource.CONTINGENCY_LOGIC,
            CommandSource.SAFETY_SUPERVISOR,
        }
    ),
    FunctionClass.POLICY_OVERRIDE: frozenset(
        {
            CommandSource.OPERATOR,
            CommandSource.SAFETY_SUPERVISOR,
        }
    ),
    FunctionClass.EVIDENCE_CONTROL: frozenset(
        {
            CommandSource.SAFETY_SUPERVISOR,
        }
    ),
}


class AuthorityEngine(Protocol):
    """Protocol for authority evaluation engines."""

    def evaluate(self, context: AuthorityContext) -> AuthorityDecision:
        """Evaluate whether the candidate command may proceed to guard review."""


@dataclass(slots=True)
class StaticAuthorityEngine:
    """Small, deterministic authority engine aligned to the current repo baseline."""

    def evaluate(self, context: AuthorityContext) -> AuthorityDecision:
        envelope = context.envelope

        if envelope.message_class is not MessageClass.CONTROL:
            return AuthorityDecision(
                outcome=ArbitrationOutcome.REJECT,
                final_authoritative_source=CommandSource.NONE,
                rationale_summary="non-control message cannot enter the control pipeline",
                policy_evaluation_result="DENIED",
                rule_ids=("AUTH-MSG-CLASS-CONTROL-ONLY",),
            )

        try:
            payload = context.control_payload()
        except TypeError:
            return AuthorityDecision(
                outcome=ArbitrationOutcome.REJECT,
                final_authoritative_source=CommandSource.NONE,
                rationale_summary="control message payload is not a typed ControlPayload",
                policy_evaluation_result="DENIED",
                rule_ids=("AUTH-PAYLOAD-TYPE-CHECK",),
            )

        if envelope.freshness is None or envelope.freshness.freshness_state is not FreshnessState.FRESH:
            return AuthorityDecision(
                outcome=ArbitrationOutcome.REJECT,
                final_authoritative_source=CommandSource.NONE,
                rationale_summary=(
                    "control message freshness is not acceptable for authority use"
                ),
                policy_evaluation_result="DENIED",
                rule_ids=("AUTH-FRESHNESS-CHECK",),
                metadata={
                    "freshness_state": (
                        envelope.freshness.freshness_state.value
                        if envelope.freshness is not None
                        else "MISSING"
                    )
                },
            )

        if envelope.integrity.integrity_state is IntegrityState.INTEGRITY_FAILED:
            return AuthorityDecision(
                outcome=ArbitrationOutcome.REJECT,
                final_authoritative_source=CommandSource.NONE,
                rationale_summary="control message integrity verification failed",
                policy_evaluation_result="DENIED",
                rule_ids=("AUTH-INTEGRITY-CHECK",),
            )

        if envelope.integrity.auth_state is AuthState.AUTH_INVALID:
            return AuthorityDecision(
                outcome=ArbitrationOutcome.REJECT,
                final_authoritative_source=CommandSource.NONE,
                rationale_summary="control message origin authentication is invalid",
                policy_evaluation_result="DENIED",
                rule_ids=("AUTH-ORIGIN-CHECK",),
            )

        allowed_sources = _ALLOWED_SOURCES.get(payload.function_class, frozenset())
        if payload.command_source not in allowed_sources:
            return AuthorityDecision(
                outcome=ArbitrationOutcome.REJECT,
                final_authoritative_source=CommandSource.NONE,
                rationale_summary=(
                    f"{payload.command_source.value} is not permitted for "
                    f"{payload.function_class.value}"
                ),
                policy_evaluation_result="DENIED",
                rule_ids=("AUTH-FUNCTION-CLASS-PERMISSION",),
            )

        if (
            context.safety_posture is SafetyPosture.INITIALIZING
            and payload.function_class
            not in {
                FunctionClass.MODE_MANAGEMENT,
                FunctionClass.RECOVERY_ACTION,
            }
        ):
            return AuthorityDecision(
                outcome=ArbitrationOutcome.REJECT,
                final_authoritative_source=CommandSource.NONE,
                rationale_summary=(
                    "initializing posture only permits bounded mode or recovery actions"
                ),
                policy_evaluation_result="DENIED",
                rule_ids=("AUTH-INITIALIZING-POSTURE-RESTRICTION",),
            )

        return AuthorityDecision(
            outcome=ArbitrationOutcome.ACCEPT,
            final_authoritative_source=payload.command_source,
            rationale_summary=(
                "authority evaluation accepted the candidate command for guard review"
            ),
            policy_evaluation_result="ALLOWED",
            rule_ids=("AUTH-BASELINE-ACCEPT",),
        )
