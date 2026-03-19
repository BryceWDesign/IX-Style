# IX-Style Project Charter

## Status

IX-Style is a ground-up reference architecture repository for **assured autonomy**
in aerospace and adjacent safety-critical mobility systems.

It is intended to become a serious, reviewable, implementation-oriented repo for:

- bounded autonomy
- flight-software safety structure
- fault detection, isolation, and recovery (FDIR)
- runtime assurance and envelope protection
- degraded-mode supervision
- auditable autonomy decisions
- mission-health telemetry and operator support
- verification evidence that can survive technical review

IX-Style is **not** a claim of completed certification for any specific aircraft,
spacecraft, rover, or uncrewed platform.

---

## Mission

Design a reusable autonomy architecture that helps keep a vehicle inside safe
operating bounds when the world stops being clean.

The repo exists to answer one hard question:

> Can an autonomy stack continue operating safely when sensors drift, comms drop,
> power browns out, navigation becomes suspect, timing degrades, or a subsystem
> begins providing untrustworthy outputs — and can it leave a clear evidence trail
> showing exactly why it acted?

IX-Style will treat that question as an engineering problem, not a marketing claim.

---

## Primary Objectives

1. **Bound autonomous behavior**
   - No autonomy output is allowed to directly influence safety-critical behavior
     without passing policy, authority, and envelope checks.

2. **Detect and isolate faults**
   - The system must detect abnormal conditions, identify likely fault classes,
     and route mitigations through deterministic logic.

3. **Fail safely**
   - Loss of confidence must reduce authority, not expand it.

4. **Preserve evidence**
   - Safety-relevant decisions, mode changes, overrides, vetoes, and degraded-mode
     transitions must leave machine-readable, auditable records.

5. **Support operators**
   - The system must expose mission health, confidence, and rationale in a form
     that helps operators understand what changed and why.

6. **Be testable**
   - The repo must support simulation, fault injection, requirements tracing,
     and repeatable verification artifacts.

---

## Non-Negotiables

IX-Style will not be considered complete unless it demonstrates all of the following:

1. **FDIR**
   - Fault detection
   - Fault isolation
   - Recovery or safe containment
   - Clear fault-class definitions

2. **Runtime assurance**
   - Safety guard independent from the nominal autonomy path
   - Constraint and envelope enforcement
   - Command veto / downgrade / substitution capability

3. **Safe degraded modes**
   - Explicit mode-entry rules
   - Explicit mode-exit rules
   - Deterministic transitions
   - Latched safety behavior where appropriate

4. **Mission-health telemetry**
   - State confidence
   - Fault status
   - resource posture
   - command source / authority state
   - operator-facing event stream

5. **Secure flight-software messaging**
   - deterministic message contracts
   - integrity checks
   - authenticated control-plane events
   - replay-aware command and evidence paths

6. **Verification evidence**
   - hazards
   - requirements
   - monitors
   - mitigations
   - tests
   - traceability

---

## System Principles

### 1. Determinism before cleverness
If a capability cannot be bounded, monitored, and tested, it does not belong on
the flight-critical path.

### 2. Confidence is a first-class signal
IX-Style will reason not only about values, but about confidence in values,
confidence in timing, and confidence in the consistency of multiple data sources.

### 3. Safety layers must be structurally independent
The nominal autonomy path and the safety guard must not collapse into the same
opaque logic block.

### 4. Evidence must survive scrutiny
Every meaningful safety-relevant autonomy decision must be reconstructible after
the fact.

### 5. Graceful degradation beats brittle brilliance
Reduced capability with preserved control is preferable to high performance with
fragile trust assumptions.

### 6. Human operators still matter
Operator understanding, intervention, and post-event review are design inputs,
not afterthoughts.

---

## Initial Fault / Hazard Classes

IX-Style is expected to address, at minimum, the following categories:

- sensor disagreement
- sensor drift
- stale or missing data
- estimator divergence or implausible state jumps
- navigation spoof suspicion or trust collapse
- comms loss or comms intermittency
- clock / timing degradation
- power brownout or energy-priority degradation
- actuator non-response or partial response
- subsystem self-report inconsistency
- command-source conflict
- policy violation attempts
- thermal, load, or resource envelope excursions

These classes are architecture anchors, not final implementation limits.

---

## What IX-Style Is

IX-Style is intended to become all of the following:

- a reference architecture
- a safety-case-oriented repo
- a deterministic mode-management design
- a fault-management framework
- a decision-evidence framework
- a simulation and fault-injection harness
- a traceability-first engineering package

---

## What IX-Style Is Not

IX-Style is not intended to be:

- a vague “AI for aerospace” concept repo
- an end-to-end certified product by declaration
- an opaque end-to-end ML autopilot
- a self-modifying flight-critical controller
- an offensive cyber or stealth-focused platform
- a weapons repo
- a replacement for vehicle-specific verification, validation, or certification

---

## Completion Standard for This Repository

The repo will only be considered complete when it contains, in coherent form:

1. a requirements baseline
2. a hazard register
3. an operational mode model
4. a command / authority model
5. an autonomy boundary definition
6. an FDIR architecture
7. a runtime assurance guard design
8. a degraded-mode supervisor
9. deterministic message schemas
10. an evidence / receipt model for critical decisions
11. a telemetry and operator-support model
12. a simulation and fault-injection harness
13. a verification matrix with requirements-to-test traceability
14. CI checks appropriate to the maturity of the implementation
15. final public README written last

---

## Repo Posture

Public presentation should emphasize:

- assured autonomy
- bounded behavior
- safety and mission assurance
- reviewability
- evidence generation
- integration readiness
- seriousness over hype

If a future design choice makes IX-Style look more impressive but less testable,
the more testable option wins.

---

## Working Rule

The purpose of IX-Style is not to appear futuristic.

The purpose of IX-Style is to make an autonomy architecture that serious people
can inspect without rolling their eyes.
