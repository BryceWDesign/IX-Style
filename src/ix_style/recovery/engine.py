"""Baseline recovery-gate engine for IX-Style."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Protocol

from ix_style.core.enums import FaultLifecycleState, FunctionClass, TrustState
from ix_style.fdir.models import FaultPriority

from .models import RecoveryGateContext, RecoveryGateDecision, RecoveryGateStatus

_BLOCKING_FLAGS: Final[frozenset[str]] = frozenset(
    {
        "assurance_guard_unhealthy",
        "power_margin_low",
        "actuator_response_uncertain",
        "nav_spoof_suspected",
        "nav_corroboration_lost",
        "sensor_trust_low",
    }
)

_DEFERRAL_FLAGS: Final[frozenset[str]] = frozenset(
    {
        "comms_link_intermittent",
        "command_freshness_low",
    }
)

_BLOCKING_LIFECYCLE_STATES: Final[frozenset[FaultLifecycleState]] = frozenset(
    {
        FaultLifecycleState.CONTAINED,
        FaultLifecycleState.LATCHED,
        FaultLifecycleState.MITIGATING,
        FaultLifecycleState.CONFIRMED,
        FaultLifecycleState.ISOLATING,
        FaultLifecycleState.ISOLATED,
    }
)

_BLOCKING_PRIORITIES: Final[frozenset[FaultPriority]] = frozenset(
    {
        FaultPriority.P1_CONTAINMENT_CRITICAL,
        FaultPriority.P2_HIGH,
    }
)

_BLOCKING_TRUST_STATES: Final[frozenset[TrustState]] = frozenset(
    {
        TrustState.DEGRADED,
        TrustState.SUSPECT,
        TrustState.UNTRUSTED,
        TrustState.UNAVAILABLE,
    }
)


class RecoveryGateEngine(Protocol):
    """Protocol for recovery-gate engines."""

    def evaluate(self, context: RecoveryGateContext) -> RecoveryGateDecision:
        """Evaluate whether a recovery-expanding candidate may proceed."""


@dataclass(slots=True)
class BasicRecoveryGateEngine:
    """Deterministic first-pass recovery gate for IX-Style."""

    def evaluate(self, context: RecoveryGateContext) -> RecoveryGateDecision:
        payload = context.control_payload()

        if (
            payload.function_class is not FunctionClass.RECOVERY_ACTION
            or context.envelope.message_type != "control.recovery_action_request"
        ):
            return RecoveryGateDecision(
                gate_status=RecoveryGateStatus.NOT_APPLICABLE,
                allow_progression=True,
                rationale_summary=(
                    "recovery gate is not applicable unless the envelope explicitly carries"
                    " a recovery-action request"
                ),
            )

        flags = set(context.active_degradation_flags)

        if payload.command_source.value == "OPERATOR" and _DEFERRAL_FLAGS.intersection(flags):
            return RecoveryGateDecision(
                gate_status=RecoveryGateStatus.DEFERRED,
                allow_progression=False,
                rationale_summary=(
                    "recovery action deferred because communications or command freshness"
                    " remain too weak for trusted remote restoration intent"
                ),
                metadata={"deferral_reason": "WEAK_REMOTE_RECOVERY_INTENT"},
            )

        blocking_fault_ids = tuple(
            sorted(
                record.fault_id
                for record in context.fault_records.values()
                if record.lifecycle_state in _BLOCKING_LIFECYCLE_STATES
                or (
                    record.current_priority in _BLOCKING_PRIORITIES
                    and record.lifecycle_state is not FaultLifecycleState.CLEARED
                    and record.lifecycle_state is not FaultLifecycleState.RECOVERING
                )
            )
        )

        blocking_trust_record_ids = tuple(
            sorted(
                record.trust_record_id
                for record in context.trust_records.values()
                if record.posture_driving
                and record.current_trust_state in _BLOCKING_TRUST_STATES
            )
        )

        blocking_flags = tuple(sorted(_BLOCKING_FLAGS.intersection(flags)))

        if blocking_fault_ids or blocking_trust_record_ids or blocking_flags:
            return RecoveryGateDecision(
                gate_status=RecoveryGateStatus.FAILED,
                allow_progression=False,
                rationale_summary=(
                    "recovery action blocked because posture-driving trust, active faults,"
                    " or major degradation flags still make authority restoration unsafe"
                ),
                blocking_fault_ids=blocking_fault_ids,
                blocking_trust_record_ids=blocking_trust_record_ids,
                metadata={
                    "blocking_flags": ",".join(blocking_flags),
                },
            )

        return RecoveryGateDecision(
            gate_status=RecoveryGateStatus.PASSED,
            allow_progression=True,
            rationale_summary=(
                "recovery gate passed because no blocking trust, fault, or major"
                " degradation condition remains active"
            ),
        )
