# IX-Style FDIR Architecture

## Document ID

IXS-FDIR-ARCHITECTURE

## Status

Draft architecture baseline.

## Purpose

This document defines the IX-Style FDIR architecture.

FDIR in IX-Style means:

- fault detection
- fault classification
- fault isolation
- mitigation selection
- safe containment when recovery is not yet justified
- policy-controlled recovery
- evidence preservation throughout the fault lifecycle

This document exists to answer the operational question:

> When something begins going wrong, how does IX-Style move from anomaly to
> justified containment or recovery without hand-waving?

---

## Core Role of FDIR

The FDIR subsystem is responsible for converting raw abnormality into structured
operational meaning.

That includes:

- identifying that something may be wrong
- classifying what kind of problem it resembles
- estimating whether it is transient, persistent, or escalating
- isolating the likely source or affected trust boundary
- choosing mitigation or containment actions
- maintaining fault lifecycle state over time
- supporting recovery only when policy and evidence justify it

FDIR is not just an alarm bucket.

It is the architecture that keeps abnormal conditions from being treated as a
flat stream of unrelated warnings.

---

## Relationship to Other IX-Style Layers

### FDIR vs Runtime Assurance

**FDIR**
- reasons about fault existence and lifecycle
- classifies and prioritizes faults
- selects mitigations and containment posture
- owns recovery logic and fault state memory

**Runtime Assurance Guard**
- evaluates a candidate action right now
- blocks or constrains unsafe commands before execution
- consumes current fault and degradation state from FDIR

### FDIR vs Operational Modes

**FDIR**
- explains why degradation or containment may be needed

**Operational Modes**
- define the posture the system enters because of that reasoning

### FDIR vs Authority Model

**FDIR**
- informs authority reduction, freeze, and restoration logic

**Authority Model**
- determines how control influence changes once those conditions exist

### FDIR vs Evidence

**FDIR**
- generates structured fault lifecycle events and reasoning inputs

**Evidence**
- preserves those lifecycle transitions in auditable form

---

## FDIR Design Principles

### 1. Faults are not binary at first sight
A single bad sample should not necessarily be treated the same as a confirmed
persistent fault.

### 2. Detection and isolation are different jobs
Knowing that something is wrong is not the same as knowing what is wrong.

### 3. Containment may be more honest than optimistic recovery
If recovery is not yet justified, IX-Style prefers bounded degraded operation or
safe-hold over false restoration.

### 4. Fault state must persist across time
The system must remember what has been observed, confirmed, mitigated, latched,
or cleared.

### 5. Recovery must be harder than clearing a threshold once
A fault should not disappear just because one sample looks healthy again.

### 6. Multiple faults can interact
The architecture must represent concurrent faults and mitigation conflicts.

---

## Fault Processing Stages

IX-Style FDIR uses the following processing stages:

1. **Observe**
   - an anomaly indicator or monitor output appears

2. **Screen**
   - determine whether the anomaly is plausible, relevant, and worth tracking

3. **Suspect**
   - create a candidate fault instance with preliminary class and confidence

4. **Confirm**
   - promote the fault when persistence, corroboration, or severity criteria are met

5. **Isolate**
   - identify the likely source, boundary, or affected function class

6. **Mitigate**
   - select the most appropriate response or containment action

7. **Contain**
   - preserve safe bounded operation if full recovery is not justified

8. **Recover**
   - attempt restoration only when policy, evidence, and health checks allow it

9. **Clear or Latch**
   - close the fault or hold it latched pending explicit reset policy

These are process stages, not all necessarily externally visible states.

---

## Fault Lifecycle States

Each fault instance moves through a lifecycle state machine.

### DETECTED
An anomaly signal has been registered.

### SUSPECTED
The system has enough information to track the anomaly as a candidate fault.

### CONFIRMED
The fault is considered operationally real enough to affect posture,
mitigation, or authority.

### ISOLATING
The system is actively refining likely source or affected scope.

### ISOLATED
The most likely source or trust boundary has been identified to the degree
needed for action.

### MITIGATING
A mitigation plan or response is currently active.

### CONTAINED
The system has transitioned into a bounded posture that preserves safety or
survivability while the fault remains active.

### RECOVERING
The system is evaluating whether it is safe to restore reduced capability.

### CLEARED
The fault is no longer active and recovery conditions have been satisfied.

### LATCHED
The fault remains recorded as active or blocking until explicitly cleared under
policy, even if immediate symptoms have subsided.

---

## Latching Philosophy

A latched fault is used when immediate symptom disappearance is not enough to
justify trust restoration.

Typical latching cases:

- assurance-layer failure
- repeated actuator mismatch
- severe navigation trust collapse
- safety-policy violation attempts
- evidence-path failure during a critical event
- repeated oscillation between degraded and nominal states

Latching exists to stop the system from pretending the problem is gone.

---

## Fault Classes

IX-Style defines the following baseline fault classes.

### SENSOR_FAULT
Examples:
- stale data
- missing data
- drift
- disagreement
- implausible value

### NAVIGATION_TRUST_FAULT
Examples:
- spoof-suspected state change
- nav corroboration loss
- estimator/nav mismatch
- navigation freshness failure

### TIMING_FAULT
Examples:
- missed monitor update
- stale decision path
- timing budget violation
- out-of-sequence event stream

### COMMUNICATION_FAULT
Examples:
- link loss
- excessive delay
- command freshness violation
- incomplete reconciliation after reconnect

### POWER_RESOURCE_FAULT
Examples:
- brownout
- unsafe energy margin
- resource-floor violation
- unsafe load-shed outcome

### ACTUATION_FAULT
Examples:
- non-response
- partial response
- lag beyond assumptions
- command/response mismatch

### SOFTWARE_HEALTH_FAULT
Examples:
- application heartbeat loss
- internal consistency failure
- stale internal state
- scheduler overrun indication

### ASSURANCE_FAULT
Examples:
- guard loop unhealthy
- intervention path unavailable
- evidence sink degraded
- safety monitor failure

### POLICY_AUTHORITY_FAULT
Examples:
- invalid override attempt
- prohibited action request
- ambiguous authority conflict
- unauthorized source for function class

### EVIDENCE_FAULT
Examples:
- missing decision receipt
- ordering failure
- append-only path unavailable
- rationale payload incomplete

### MULTI_FAULT_COMPOUND
Examples:
- sensor trust loss during power degradation
- comms loss during navigation degradation
- actuator degradation during safe-hold transition

---

## Fault Severity and Priority

Each fault instance carries at minimum:

- severity estimate
- confirmation confidence
- detectability difficulty indicator
- affected function scope
- containment urgency
- recovery difficulty
- evidence criticality
- current priority

### Initial Priority Bands

- `P1_CONTAINMENT_CRITICAL`
- `P2_HIGH`
- `P3_MODERATE`
- `P4_LOW`

### Priority Principles

1. containment-critical faults outrank mission-progress faults
2. faults affecting the assurance layer get elevated priority
3. concurrent faults may elevate each other
4. fault priority may change as confirmation or isolation improves
5. a low-level anomaly can become high-priority if it persists or combines with
   another degradation

---

## Detection Sources

FDIR may ingest anomaly signals from:

- sensor trust monitors
- estimator sanity monitors
- timing validity monitors
- message integrity checks
- authority arbitration failures
- runtime-assurance interventions
- subsystem self-health monitors
- resource margin monitors
- operator-acknowledged discrepancies
- evidence pipeline health checks

Not all signals are equal.
Some are advisory.
Some are containment-critical immediately.

---

## Detection Rules

IX-Style detection logic should support:

- threshold-based detection
- persistence-based detection
- rate-of-change detection
- cross-consistency detection
- heartbeat/time-gap detection
- state-machine violation detection
- policy violation detection
- compound-condition detection

This mix exists because many real safety problems are not visible from one
simple threshold alone.

---

## Isolation Model

Isolation in IX-Style means narrowing the likely source or trust boundary of the
fault enough to choose an appropriate mitigation.

Isolation may target:

- a specific sensor
- a specific estimator pathway
- a message source
- a subsystem application
- an actuator chain
- an authority path
- the assurance layer itself
- a broader trust domain rather than a single component

Isolation confidence may be:

- `LOW`
- `MEDIUM`
- `HIGH`

IX-Style does not require perfect root-cause knowledge before containment.
It requires enough justified isolation to avoid foolish mitigation.

---

## Mitigation Categories

FDIR mitigations are grouped into categories.

### OBSERVE_ONLY
Track but do not yet alter posture.

### DEGRADE_FUNCTION
Reduce capability for a specific function or trust-dependent behavior.

### REDUCE_AUTHORITY
Lower command authority or narrow accepted commands.

### SWITCH_SOURCE
Prefer a healthier source, pathway, or bounded fallback path.

### CLAMP_BEHAVIOR
Constrain magnitude, rate, duration, or scope.

### FREEZE_PATH
Prevent further command progression through a suspect path.

### ENTER_DEGRADED_MODE
Change dominant safety posture to a degraded mode.

### ENTER_SAFE_HOLD
Escalate to containment-oriented posture.

### LATCH_AND_REQUIRE_RESET
Keep the fault active until explicit qualified reset.

### RECOVERY_GATE_EVALUATION
Allow the fault to move into recovery review, not instant restoration.

---

## Fault-to-Mode Interaction

Faults do not directly equal modes, but they often drive them.

Examples:

- confirmed sensor trust fault may drive `SENSOR_DEGRADED`
- confirmed nav trust fault may drive `NAV_DEGRADED`
- critical assurance fault may drive `ASSURANCE_DEGRADED`
- severe multi-fault compound may drive `SAFE_HOLD`

The same fault may:
- remain local without changing dominant posture
- reduce only a specific function class
- trigger a full degraded mode
- escalate directly to safe-hold

That choice depends on severity, scope, trust impact, and containment urgency.

---

## Fault-to-Authority Interaction

FDIR may trigger:

- authority reduction
- source freeze
- recovery lockout
- stale-command rejection bias
- loss of nominal autonomy permission for certain function classes
- override restrictions

The authority model consumes these changes.
FDIR does not directly bypass the authority model.
It informs and drives it.

---

## Concurrent Fault Handling

IX-Style must support multiple active fault instances simultaneously.

Concurrent fault handling requires:

1. representation of each active fault separately
2. grouping by shared impact if appropriate
3. a priority ordering
4. mitigation conflict detection
5. dominant containment bias selection
6. multi-fault evidence outputs

### Example

Active faults:
- confirmed sensor fault
- confirmed comms fault
- suspected actuator fault

Possible consequence:
- command acceptance narrows
- stale operator influence blocked
- maneuver envelope clamped
- escalation to safe-hold considered

This is why IX-Style cannot use a single flat "health = bad" flag.

---

## Fault Escalation Rules

A fault should escalate when one or more of the following occur:

- persistence exceeds allowed window
- severity increases
- corroborating evidence appears
- trust impact expands
- mitigation fails
- a second interacting fault appears
- the fault affects the assurance layer
- the fault threatens containment margin

Escalation may increase priority, tighten mitigation, or drive a stronger mode.

---

## Fault Recovery Rules

Recovery is a structured evaluation, not an emotional reset.

A fault may enter recovery review only when:

- the initiating abnormal condition is no longer active
- corroborating signals remain healthy for a required persistence window
- mitigation success is demonstrated where applicable
- no higher-priority interacting fault blocks restoration
- policy allows recovery
- evidence for recovery evaluation is recorded

Recovery outcomes include:

- remain active
- remain contained
- move to recovery observation
- clear
- latch pending manual or policy-controlled reset

---

## Fault Record Structure

Each fault instance must record at minimum:

- fault identifier
- fault class
- current lifecycle state
- detection source
- first-detected timestamp
- latest-update timestamp
- affected function scope
- severity estimate
- confirmation confidence
- isolation confidence
- active mitigation set
- current priority
- latch status
- recovery gate status
- rationale summary

This is required for both machine action and operator review.

---

## FDIR Evidence Requirements

The FDIR subsystem must emit evidence for:

- fault creation
- confirmation
- isolation update
- mitigation start
- mitigation failure
- containment posture entry
- recovery evaluation start
- fault clear
- latching and unlatching
- priority changes for active high-risk faults

This preserves the "why" behind fault posture, not just the final label.

---

## Baseline Fault Lifecycle Diagram

```mermaid
stateDiagram-v2
    [*] --> DETECTED
    DETECTED --> SUSPECTED : anomaly worth tracking
    SUSPECTED --> CONFIRMED : persistence / corroboration / severity
    SUSPECTED --> CLEARED : transient not justified
    CONFIRMED --> ISOLATING : refine source / scope
    CONFIRMED --> MITIGATING : immediate action needed
    ISOLATING --> ISOLATED : source narrowed enough
    ISOLATING --> MITIGATING : action needed before perfect isolation
    ISOLATED --> MITIGATING : mitigation selected
    MITIGATING --> CONTAINED : bounded posture established
    MITIGATING --> RECOVERING : mitigation appears successful
    CONTAINED --> RECOVERING : recovery gate evaluation begins
    RECOVERING --> CLEARED : restoration justified
    RECOVERING --> CONTAINED : recovery failed or blocked
    CONTAINED --> LATCHED : policy requires explicit reset
    MITIGATING --> LATCHED : severe or repeated fault
    LATCHED --> RECOVERING : explicit qualified recovery attempt
    LATCHED --> CLEARED : policy-cleared after validation

FDIR Non-Negotiables

IX-Style FDIR is not complete unless:

faults have lifecycle state, not just alert text

confirmation and isolation are distinct concepts

mitigations can reduce function, authority, or mode

containment exists when recovery is not justified

latching is available for serious conditions

concurrent faults are represented coherently

all major lifecycle transitions emit evidence

Deferred Items

This commit intentionally does not yet finalize:

platform-specific fault thresholds

exact fault scoring math

exact detector algorithms

exact mitigation catalog by vehicle type

exact recovery timer values

exact software package boundaries for implementation

Those will be allocated later.

Completion Criteria

This FDIR architecture is not mature until later commits allocate:

concrete fault identifiers

detector-to-fault mappings

fault-to-mode mappings

fault-to-authority restrictions

verification scenarios for lifecycle progression

reference code scaffolding for fault records and state transitions
