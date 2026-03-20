# IX-Style Operational Mode Model

## Document ID

IXS-OPERATIONAL-MODE-MODEL

## Status

Draft architecture baseline.

## Purpose

This document defines the operational mode model for IX-Style.

It exists to answer a simple but critical question:

> When confidence drops, capability degrades, or containment risk rises,
> exactly how does the system change posture?

The mode model is one of the main places where assured autonomy becomes
concrete. A serious repo cannot merely say "it degrades safely." It must define:

- what modes exist
- what triggers entry
- what blocks exit
- what authority is reduced
- what actions are still permitted
- how multiple degradations are represented
- how the system avoids silent restoration of trust

---

## Core Design Rule

IX-Style does **not** use one flat mode enum to represent everything.

A flat mode list breaks down too quickly once multiple faults happen at once.

Instead, IX-Style uses three coordinated layers:

1. **Mission Phase**
   - what the vehicle is trying to do

2. **Safety Posture**
   - how much trust/capability is currently available

3. **Active Degradation Flags**
   - which specific trust or subsystem problems are currently active

This structure allows the system to be honest about multi-fault reality while
still exposing one dominant safety posture to operators and downstream logic.

---

## Mode Model Overview

### Layer 1 — Mission Phase

Mission phase describes intent, not trust.

The initial repository baseline uses these generic mission phases:

- `BOOTSTRAP`
- `READY`
- `ACTIVE`
- `CONTINGENCY`
- `QUIESCENT`

Mission phase may vary by target platform later, but the safety-posture model
below is expected to remain broadly stable.

---

### Layer 2 — Safety Posture

Safety posture describes the dominant current operational trust state.

Only **one** dominant safety posture may be active at a time.

Baseline safety postures are:

- `INITIALIZING`
- `NOMINAL`
- `SENSOR_DEGRADED`
- `NAV_DEGRADED`
- `COMMS_DEGRADED`
- `POWER_DEGRADED`
- `ACTUATION_DEGRADED`
- `ASSURANCE_DEGRADED`
- `SAFE_HOLD`

These are not just labels. Each one implies bounded behavior.

---

### Layer 3 — Active Degradation Flags

Specific degradations are tracked independently as flags so concurrent faults
can be represented without inventing endless compound modes.

Examples:

- `sensor_trust_low`
- `sensor_data_stale`
- `nav_corroboration_lost`
- `comms_link_intermittent`
- `power_margin_low`
- `actuator_response_uncertain`
- `assurance_guard_unhealthy`
- `evidence_path_degraded`

The dominant safety posture is derived from these flags using precedence rules.

---

## Why This Structure Exists

This hybrid structure is intentional.

A vehicle can be:

- in mission phase `ACTIVE`
- with dominant safety posture `POWER_DEGRADED`
- while also carrying active flags for intermittent comms and sensor trust loss

That is far more truthful than pretending one string fully describes reality.

---

## Safety Posture Definitions

### INITIALIZING

The system is not yet allowed to present itself as nominally ready.

**Purpose**
- establish basic self-health
- validate critical configuration
- confirm monitor availability
- confirm timing baseline
- initialize evidence path
- establish initial authority posture

**Allowed behavior**
- self-tests
- bounded setup actions
- no unrestricted mission autonomy

**Entry conditions**
- power-up
- controlled restart
- reset from major containment state where restart is permitted

**Exit conditions**
- required monitors alive
- essential timing valid
- essential message/evidence functions alive
- no blocking latched fault
- ready criteria satisfied

---

### NOMINAL

The system has sufficient confidence and capability to operate with full
repository-defined nominal behavior, still within explicit autonomy boundaries.

**Purpose**
- perform intended mission behavior under bounded autonomy

**Allowed behavior**
- nominal planning and execution
- normal operator interaction
- standard runtime-assurance supervision
- normal evidence generation

**Entry conditions**
- no dominant degradation posture active
- no unresolved blocking fault
- no recovery gate pending
- required confidence posture above configured thresholds

**Exit conditions**
- any confirmed degradation requiring reduced authority
- safe-hold trigger
- assurance-path loss requiring containment posture

---

### SENSOR_DEGRADED

Sensor quality or trust is reduced enough that mission behavior must be narrowed.

**Purpose**
- preserve safe behavior under reduced input trust

**Typical triggers**
- stale data
- missing data
- sensor disagreement
- plausibility failure
- confidence collapse in one or more critical inputs

**Expected behavior**
- reduce or freeze autonomy functions dependent on weak inputs
- clamp actions requiring unsupported state knowledge
- elevate evidence generation around trust changes
- increase operator visibility of what is no longer trusted

**Exit conditions**
- degraded sensor conditions cleared
- corroboration restored
- persistence timer satisfied
- recovery policy permits restoration

---

### NAV_DEGRADED

Navigation trust is reduced below the level required for full mission behavior.

**Purpose**
- prevent unsafe behavior when the vehicle no longer has justified confidence in
  navigation state or external reference integrity

**Typical triggers**
- navigation state jump
- corroboration loss
- spoof-suspected condition
- estimator/nav mismatch
- navigation freshness failure

**Expected behavior**
- restrict nav-dependent actions
- block or clamp aggressive movement dependent on untrusted positioning
- prefer containment-oriented or locally bounded behavior
- increase confidence/evidence reporting for navigation posture

**Exit conditions**
- trusted corroboration restored
- navigation consistency recovered
- persistence and policy checks passed

---

### COMMS_DEGRADED

The link to an external operator, peer, or supervising control source is weak,
intermittent, or lost.

**Purpose**
- prevent unsafe assumptions about command freshness and operator availability

**Typical triggers**
- link loss
- excessive delay
- intermittent connectivity
- command freshness violation
- reconciliation incomplete after reconnect

**Expected behavior**
- no assumption of immediate operator availability
- freeze or downgrade authority tied to stale remote intent
- obey pre-approved lost-link behavior only
- reject or quarantine stale commands
- retain compact event history for later review

**Exit conditions**
- link quality restored
- command freshness restored
- reconciliation completed
- policy allows re-entry from comms degradation

---

### POWER_DEGRADED

Power or resource margin is low enough that capability must be reduced to
preserve containment and essential safety functions.

**Purpose**
- preserve the minimum safe function set before autonomy convenience features

**Typical triggers**
- low energy reserve
- brownout events
- critical resource margin violation
- resource budget forecast below safe threshold

**Expected behavior**
- shed nonessential loads first
- preserve monitoring, authority management, safe-hold, and evidence paths
- derate high-cost behaviors
- bias toward containment and survivability
- surface explicit resource posture to operator view

**Exit conditions**
- energy or resource margin restored
- essential functions stable
- recovery policy allows authority restoration

---

### ACTUATION_DEGRADED

The system can no longer assume commanded actions are being executed with the
expected timing, magnitude, or fidelity.

**Purpose**
- contain behavior when control effectiveness is uncertain

**Typical triggers**
- actuator non-response
- partial response
- excessive lag
- inconsistent subsystem self-report
- command/response mismatch

**Expected behavior**
- reduce maneuver or response envelope
- clamp commands to conservative levels
- substitute bounded fallback actions where allowed
- escalate to safe-hold if control confidence drops too far

**Exit conditions**
- actuator confidence restored
- response correlation normal
- persistence and policy checks passed

---

### ASSURANCE_DEGRADED

The safety guard, monitor network, or evidence path is itself degraded enough
that the system cannot honestly claim full assurance posture.

**Purpose**
- prevent false confidence when the assurance layer is weak

**Typical triggers**
- runtime-assurance loop unhealthy
- monitor watchdog failure
- evidence sink unavailable
- guard timing violation
- failed intervention path self-test

**Expected behavior**
- reduce authority aggressively
- block behaviors that depend on unavailable safety supervision
- elevate operator visibility
- transition toward safe-hold if containment assurance is not credible

**Exit conditions**
- assurance-path health restored
- required self-health checks pass
- restoration allowed by policy
- no higher-priority degradation active

---

### SAFE_HOLD

The system has entered a containment-oriented posture intended to preserve
control, survivability, or stable bounded behavior while higher-function mission
autonomy is reduced or suspended.

**Purpose**
- keep the vehicle in the safest practical bounded state available

**Typical triggers**
- critical containment risk
- multiple interacting degradations
- failed or suspect assurance layer
- unsafe command path detected
- severe power/resource threat
- policy-directed containment

**Expected behavior**
- suspend or sharply narrow mission autonomy
- preserve stabilization / containment / essential health monitoring
- preserve authority and evidence traceability
- expose clear mode rationale
- require explicit recovery qualification before leaving

**Exit conditions**
- root conditions no longer active
- minimum essential functions stable
- recovery gate satisfied
- policy permits exit
- authority restoration explicitly performed, not assumed

---

## Dominant Safety Posture Precedence

When multiple degradation flags are active, IX-Style chooses the dominant safety
posture using the following default precedence:

1. `SAFE_HOLD`
2. `ASSURANCE_DEGRADED`
3. `POWER_DEGRADED`
4. `ACTUATION_DEGRADED`
5. `NAV_DEGRADED`
6. `SENSOR_DEGRADED`
7. `COMMS_DEGRADED`
8. `NOMINAL`

This precedence is a repository baseline, not a final platform-specific truth.

### Rationale

- If containment posture is required, `SAFE_HOLD` wins.
- If the assurance layer itself is untrustworthy, that is more serious than
  ordinary nominal degradation because the system loses confidence in its own
  guardrails.
- Resource and actuation degradations can directly threaten containment.
- Navigation degradation is usually more safety-relevant than generic comms loss.
- Comms degradation matters, but many systems can remain safe under a valid
  lost-link policy if other trust channels remain healthy.

---

## Mode Transition Rules

### Rule 1 — Detection is not enough by itself
A raw anomaly does not automatically change safety posture unless mode-entry
criteria are satisfied.

### Rule 2 — Confirmation may be required
Transient noise should not cause chaotic mode flapping. Entry may require
confirmation windows, persistence checks, or corroboration logic.

### Rule 3 — Escalation must be fast
Once a confirmed risk threatens containment, the system shall prefer rapid
escalation over optimistic delay.

### Rule 4 — Exit must be harder than entry
A degraded mode must not clear simply because one sample looks healthy again.

### Rule 5 — No silent authority restoration
Leaving a degraded posture must not silently restore full authority.

### Rule 6 — SAFE_HOLD is sticky by design
Leaving safe-hold requires explicit recovery qualification and policy approval.

---

## Recovery Gate

IX-Style separates **hazard clearing** from **authority restoration**.

A mode may become technically clear before the system is allowed to re-expand
behavior authority.

Recovery gate conditions typically include:

- the triggering condition is no longer present
- corroborating signals remain healthy for a persistence window
- no higher-priority degradation remains active
- latched faults are cleared under allowed policy
- command authority restoration is explicitly evaluated
- evidence is written for the restoration event

This recovery gate exists to prevent brittle oscillation and false trust rebound.

---

## Allowed Direct Transitions

The following direct transition patterns are permitted at the baseline level:

- `INITIALIZING -> NOMINAL`
- `INITIALIZING -> SAFE_HOLD`
- `NOMINAL -> *_DEGRADED`
- `NOMINAL -> SAFE_HOLD`
- `*_DEGRADED -> SAFE_HOLD`
- `*_DEGRADED -> different *_DEGRADED` when precedence changes
- `*_DEGRADED -> NOMINAL` only after recovery gate satisfaction
- `SAFE_HOLD -> *_DEGRADED` only if containment posture can be safely relaxed
- `SAFE_HOLD -> NOMINAL` only after explicit recovery qualification

Direct transitions that bypass containment logic or recovery qualification are
not allowed.

---

## Multi-Fault Representation

IX-Style will treat concurrent degradations as:

- one dominant safety posture
- plus an active set of degradation flags
- plus a fault priority ordering

Example:

- mission phase: `ACTIVE`
- dominant safety posture: `POWER_DEGRADED`
- active flags:
  - `power_margin_low`
  - `comms_link_intermittent`
  - `sensor_data_stale`

This allows operator views, logs, and tests to remain readable without lying
about concurrent conditions.

---

## Mode Responsibilities

Each safety posture must eventually allocate all of the following:

1. entry conditions
2. exit conditions
3. blocked actions
4. allowed actions
5. authority restrictions
6. evidence requirements
7. operator-display requirements
8. verification scenarios

This document defines the structural baseline.
Later commits will allocate exact authority restrictions and transition tests.

---

## Mode-Related Architectural Constraints

1. The nominal autonomy path must not self-declare full nominal posture without
   independent criteria being satisfied.

2. Safety posture is not merely cosmetic; it must affect command acceptance,
   intervention behavior, and operator visibility.

3. The system must be able to explain why a mode changed.

4. Recovery must be more conservative than optimism.

5. Multiple degradation flags must not produce ambiguous authority outcomes.

---

## Initial Mode Diagram

```mermaid
stateDiagram-v2
    [*] --> INITIALIZING
    INITIALIZING --> NOMINAL : readiness criteria satisfied
    INITIALIZING --> SAFE_HOLD : blocking fault / assurance failure

    NOMINAL --> SENSOR_DEGRADED : sensor trust reduced
    NOMINAL --> NAV_DEGRADED : nav trust reduced
    NOMINAL --> COMMS_DEGRADED : link freshness degraded
    NOMINAL --> POWER_DEGRADED : resource margin low
    NOMINAL --> ACTUATION_DEGRADED : control response uncertain
    NOMINAL --> ASSURANCE_DEGRADED : guard/evidence unhealthy
    NOMINAL --> SAFE_HOLD : containment risk

    SENSOR_DEGRADED --> SAFE_HOLD : escalation
    NAV_DEGRADED --> SAFE_HOLD : escalation
    COMMS_DEGRADED --> SAFE_HOLD : escalation
    POWER_DEGRADED --> SAFE_HOLD : escalation
    ACTUATION_DEGRADED --> SAFE_HOLD : escalation
    ASSURANCE_DEGRADED --> SAFE_HOLD : escalation

    SENSOR_DEGRADED --> NOMINAL : recovery gate satisfied
    NAV_DEGRADED --> NOMINAL : recovery gate satisfied
    COMMS_DEGRADED --> NOMINAL : recovery gate satisfied
    POWER_DEGRADED --> NOMINAL : recovery gate satisfied
    ACTUATION_DEGRADED --> NOMINAL : recovery gate satisfied
    ASSURANCE_DEGRADED --> NOMINAL : recovery gate satisfied

    SAFE_HOLD --> SENSOR_DEGRADED : qualified relaxation
    SAFE_HOLD --> NAV_DEGRADED : qualified relaxation
    SAFE_HOLD --> COMMS_DEGRADED : qualified relaxation
    SAFE_HOLD --> POWER_DEGRADED : qualified relaxation
    SAFE_HOLD --> ACTUATION_DEGRADED : qualified relaxation
    SAFE_HOLD --> ASSURANCE_DEGRADED : qualified relaxation
    SAFE_HOLD --> NOMINAL : explicit recovery qualification

Deferred Items

This commit intentionally does not yet finalize:

command-source precedence details

exact authority masks per mode

exact monitor thresholds

vehicle-specific lost-link behavior

exact safe-hold control laws

recovery timer values

mission-phase tailoring

Those are separate allocations, not missing thought.

Completion Notes

The mode model will not be considered mature until later commits map:

hazards to mode-entry triggers

requirements to mode responsibilities

authority restrictions to each posture

verification scenarios to each transition
