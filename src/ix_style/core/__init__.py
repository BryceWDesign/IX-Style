"""Core types, enums, identifiers, and contracts for IX-Style."""

from .contracts import LANGUAGE_OWNERSHIP, PACKAGE_BOUNDARIES
from .enums import (
    ArbitrationOutcome,
    AuthState,
    CommandSource,
    FaultLifecycleState,
    FreshnessState,
    FunctionClass,
    IntegrityState,
    MessageClass,
    MissionPhase,
    ReplayState,
    ReviewSignificance,
    SafetyPosture,
    TrustDomain,
    TrustState,
)
from .ids import IdFactory, IdPrefix, make_id, validate_prefixed_id
from .models import (
    ControlPayload,
    DecisionReceiptPayload,
    FreshnessMetadata,
    IntegrityMetadata,
    MessageEnvelope,
    OrderingMetadata,
)
from .pipeline import DecisionPipeline, DecisionPipelineContext, PipelineDecision

__all__ = [
    "LANGUAGE_OWNERSHIP",
    "PACKAGE_BOUNDARIES",
    "ArbitrationOutcome",
    "AuthState",
    "CommandSource",
    "DecisionPipeline",
    "DecisionPipelineContext",
    "FaultLifecycleState",
    "FreshnessMetadata",
    "FreshnessState",
    "FunctionClass",
    "IdFactory",
    "IdPrefix",
    "IntegrityMetadata",
    "IntegrityState",
    "MessageClass",
    "MessageEnvelope",
    "MissionPhase",
    "OrderingMetadata",
    "PipelineDecision",
    "ReplayState",
    "ReviewSignificance",
    "SafetyPosture",
    "TrustDomain",
    "TrustState",
    "ControlPayload",
    "DecisionReceiptPayload",
    "make_id",
    "validate_prefixed_id",
]
