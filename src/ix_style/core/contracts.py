"""Package-boundary and language-ownership manifest for IX-Style."""

from __future__ import annotations

from types import MappingProxyType

PACKAGE_BOUNDARIES = MappingProxyType(
    {
        "ix_style.core": (
            "Shared enums, IDs, dataclasses, and stable repository-wide primitives."
        ),
        "ix_style.authority": (
            "Command-source permissions, arbitration, freeze logic, and authority"
            " restoration rules."
        ),
        "ix_style.guard": (
            "Runtime-assurance constraint evaluation, intervention selection, and"
            " containment-biased action shaping."
        ),
        "ix_style.fdir": (
            "Fault lifecycle tracking, mitigation state, recovery gating inputs, and"
            " fault prioritization."
        ),
        "ix_style.trust": (
            "Sensor trust, navigation trust, timing trust, estimator sanity, and"
            " trust propagation logic."
        ),
        "ix_style.messages": (
            "Message-envelope handling, contract validation, replay-aware helpers,"
            " and evidence receipt generation."
        ),
        "ix_style.telemetry": (
            "Mission-health snapshots, prioritized event streams, and operator-facing"
            " rationale summaries."
        ),
        "ix_style.verification": (
            "Scenario execution, fault injection, invariant checks, evidence-package"
            " assembly, and traceability audits."
        ),
        "ix_style.platform": (
            "Platform-specific adapters and transport bindings kept outside core"
            " architecture logic."
        ),
    }
)

LANGUAGE_OWNERSHIP = MappingProxyType(
    {
        "python_reference": (
            "Reference behavior, simulation, scenario execution, schema-aligned"
            " objects, evidence generation, and verification tooling."
        ),
        "rust_future": (
            "Optional deterministic receipt chaining, high-confidence replay-aware"
            " helpers, and performance-sensitive runtime services."
        ),
        "cpp_future": (
            "Optional embedded adapters, avionics interface shims, and transport or"
            " cFS-adjacent integration surfaces."
        ),
    }
)
