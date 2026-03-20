# IX-Style Reference Implementation Plan

## Document ID

IXS-REFERENCE-IMPLEMENTATION-PLAN

## Status

Draft implementation baseline.

## Purpose

This document defines the initial executable implementation strategy for
IX-Style.

It exists to answer:

- what language stack is used first
- what package boundaries exist
- what responsibilities belong in each package
- what must remain implementation-independent
- how the reference runtime stays honest to the architecture already defined

This commit intentionally starts with the reference layer, not a premature
embedded target.

---

## Implementation Strategy

IX-Style will begin with a **Python reference stack** for:

- executable architecture models
- schema-aware message and evidence handling
- simulation and fault injection
- traceability tooling
- deterministic scenario playback
- verification harnesses

This is the fastest honest path to something serious and testable.

Later, IX-Style may add:

- **Rust** for deterministic receipt generation, message integrity helpers,
  replay-aware event handling, or high-confidence runtime services
- **C++** for platform-facing adapters, cFS-adjacent integration surfaces,
  or embedded/real-time bridges

The important rule is this:

> The architecture stays stable even if implementation languages expand later.

---

## Why Python First

Python is the right first executable layer because IX-Style needs early strength
in:

- simulation
- verification
- traceability audits
- scenario generation
- structured evidence generation
- fast iteration on rules and state transitions

The repo does **not** need to pretend the first executable layer is already the
final flight target.

It needs to demonstrate the architecture honestly.

---

## Package Boundary Philosophy

IX-Style must keep core safety logic reviewable.

That means:

1. shared types must be isolated from UI or platform adapters
2. authority logic must not leak into telemetry formatting
3. guard logic must not depend on presentation code
4. evidence generation must not be buried inside convenience wrappers
5. simulation and fault injection must be able to exercise the same core logic

---

## Initial Python Package Map

### `ix_style.core`
Shared enums, identifiers, core dataclasses, stable contracts, and repository-
wide primitive types.

### `ix_style.authority`
Command-source eligibility, precedence, arbitration, freeze logic, and
authority-restoration rules.

### `ix_style.guard`
Runtime-assurance guard, constraint evaluation, intervention selection, and
containment-biased decision shaping.

### `ix_style.fdir`
Fault records, lifecycle progression, isolation reasoning, mitigation state, and
recovery gating inputs.

### `ix_style.trust`
Sensor trust, navigation trust, estimator sanity, timing trust, and propagation
logic.

### `ix_style.messages`
Envelope validation, schema-aware object creation, replay-aware helpers, and
decision/evidence receipt generation.

### `ix_style.telemetry`
Mission-health snapshots, prioritized safety event stream generation, and
operator rationale summaries.

### `ix_style.verification`
Scenario definitions, fault-injection utilities, invariant checks, traceability
audits, and evidence-package assembly.

### `ix_style.platform`
Target-specific adapters and integration surfaces kept outside the core logic.

---

## First Executable Commit Scope

This commit lays down:

- project packaging
- core enums
- stable ID generation
- core dataclasses for messages, freshness, integrity, and decision receipts
- explicit package-boundary manifest

This is enough to start building real logic in later commits without letting the
repo turn into a loose pile of scripts.

---

## Non-Negotiable Implementation Rules

1. Core safety logic must not depend on UI concerns.
2. Core decision paths must remain serializable to machine-readable evidence.
3. Message handling must keep freshness, ordering, and integrity explicit.
4. Recovery-expanding behavior must remain easy to audit.
5. Package responsibilities must remain separated enough to support later
   property testing and fault injection.

---

## Language Split Guidance

### Python owns first:
- reference behavior
- scenario execution
- schema-aligned object models
- evidence generation
- verification harnesses
- traceability audits

### Rust may later own:
- tamper-evident receipt chaining
- deterministic event indexing
- high-confidence replay-aware message utilities
- performance-sensitive guard helpers if justified

### C++ may later own:
- embedded integration surfaces
- avionics interface shims
- transport bindings
- cFS-adjacent bridges if needed

That split is intentional.
It keeps the repo grounded instead of pretending one language choice solves every problem.

---

## Implementation Posture

The first executable IX-Style code is not trying to look flashy.

It is trying to become:

- structurally clean
- testable
- traceable
- serializable
- simulation-friendly
- serious enough to grow without rewrite chaos

---

## Deferred Items

This commit intentionally does not yet add:

- full authority engine
- full guard evaluator
- full fault lifecycle engine
- trust evaluator logic
- simulation harness
- CI execution logic

Those will land in later commits, each with their own testable scope.

---

## Completion Criteria

The reference implementation plan becomes mature when later commits provide:

1. executable authority logic
2. executable guard logic
3. executable trust evaluation
4. executable FDIR lifecycle handling
5. executable receipt generation
6. executable scenario runner
7. executable traceability and invariant checks
