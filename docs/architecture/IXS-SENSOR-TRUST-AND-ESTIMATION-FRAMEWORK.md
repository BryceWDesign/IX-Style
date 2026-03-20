# IX-Style Sensor Trust, Estimator Sanity, and Navigation Confidence Framework

## Document ID

IXS-SENSOR-TRUST-AND-ESTIMATION-FRAMEWORK

## Status

Draft architecture baseline.

## Purpose

This document defines how IX-Style represents trust in raw inputs, derived
state, timing validity, navigation confidence, and estimator sanity.

It exists to answer the following question:

> At this instant, which signals does the system trust, how much, why, and what
> behavior changes when that trust degrades?

This framework is one of the hardest and most important parts of IX-Style.

Without it, the repo cannot credibly claim to handle:
- sensor drift
- stale data
- spoof-suspected navigation inputs
- estimator divergence
- inconsistent subsystem self-reporting
- false confidence after partial recovery

---

## Core Design Principle

IX-Style does **not** treat trust as an invisible assumption.

Trust is an explicit operational signal.

That means the system must be able to represent, at minimum:

- whether an input is fresh enough
- whether an input is plausible
- whether an input agrees with other trusted sources
- whether a derived estimate is still supported by trusted evidence
- whether navigation remains sufficiently corroborated
- whether a subsystem is claiming a state that external observations do not support

The system must also preserve evidence for why trust changed.

---

## Trust Domains

IX-Style separates trust into several domains instead of pretending one global
confidence number can explain everything.

### 1. Sensor Source Trust
Trust in a specific input source.

Examples:
- IMU-like source freshness and plausibility
- position source continuity
- environmental sensor plausibility
- pressure/temperature/state feedback credibility

### 2. Derived State Trust
Trust in state inferred from one or more inputs.

Examples:
- estimated velocity trust
- estimated attitude trust
- estimated resource state trust
- fused pose/state trust

### 3. Navigation Trust
Trust in the navigation picture used for movement or position-sensitive behavior.

Examples:
- corroborated position trust
- heading/course trust
- navigation continuity trust
- spoof-suspected nav degradation

### 4. Timing Trust
Trust that timestamps, update cadence, and ordering assumptions remain valid.

Examples:
- data freshness trust
- monitor update regularity
- control-path timing validity
- evidence ordering trust

### 5. Message Trust
Trust in the origin and integrity of control-relevant or evidence-relevant data.

Examples:
- authenticated source trust
- replay resistance
- sequencing validity
- class-of-message integrity

### 6. Actuator Confidence
Trust that commanded effect will actually occur in a timely and bounded way.

### 7. Assurance Confidence
Trust in the health of the guard, monitors, and evidence path that keep the
overall architecture honest.

These domains are related, but they are not interchangeable.

---

## Trust State Model

IX-Style uses a mixed categorical + scored trust model.

### Why not score-only?
A floating-point trust score is too easy to misuse as fake precision.

### Why not category-only?
Pure categories can hide useful gradient information for trending and evidence.

So each trust record carries both:

1. **trust state**
2. **supporting score and rationale fields**

---

## Trust States

Baseline trust states are:

- `TRUSTED`
- `DEGRADED`
- `SUSPECT`
- `UNTRUSTED`
- `UNAVAILABLE`

### TRUSTED
The input or derived state is currently acceptable for the functions that depend
on it.

### DEGRADED
The input or derived state is still usable for some bounded purposes but should
narrow behavior or trigger increased scrutiny.

### SUSPECT
There is enough concern that the system should behave as though the signal may
be misleading until corroboration improves.

### UNTRUSTED
The signal or derived state shall not be relied upon for functions requiring
meaningful trust.

### UNAVAILABLE
The signal is absent or too stale to treat as present.

---

## Trust Record Structure

Each trust-bearing entity should have a trust record.

A trust record contains at minimum:

- trust record identifier
- trust domain
- source or derived entity identifier
- current trust state
- numeric trust score
- freshness status
- plausibility status
- cross-consistency status
- timing-validity status
- last transition timestamp
- transition cause codes
- supporting rationale summary
- degradation persistence status
- recovery persistence status

This record is what later drives mode changes, authority reduction, and evidence.

---

## Detection Families for Trust Degradation

IX-Style trust evaluation supports multiple families of checks.

### 1. Freshness Checks
Questions:
- has the source updated recently enough
- is the current sample within timing validity bounds
- is the data too old for this function

Typical outputs:
- fresh
- stale
- missing
- timing invalid

---

### 2. Plausibility Checks
Questions:
- is the value inside physically or operationally plausible bounds
- is the rate of change plausible
- does the change violate posture-conditioned expectations

Typical outputs:
- plausible
- implausible
- marginal

---

### 3. Cross-Consistency Checks
Questions:
- does this source agree with independent sources closely enough
- does subsystem self-report align with observed state
- do fused or peer measurements support the same story

Typical outputs:
- corroborated
- weakly corroborated
- inconsistent
- conflicting

---

### 4. Temporal Continuity Checks
Questions:
- does the signal evolve smoothly enough over time
- did the estimate jump without support
- did state continuity break in a way that suggests corruption or spoof-like behavior

Typical outputs:
- continuous
- discontinuous
- oscillatory
- unstable

---

### 5. Innovation / Residual Checks
These are especially important for estimator sanity.

Questions:
- does the predicted state align with incoming measurements closely enough
- are residuals or innovations persistently too large
- are corrections becoming unstable or implausible

Typical outputs:
- innovation nominal
- innovation elevated
- innovation divergent

---

### 6. Diversity / Independence Checks
Questions:
- are the corroborating sources meaningfully independent
- is the same bad assumption contaminating multiple signals
- has independent cross-check support disappeared

Typical outputs:
- independently corroborated
- weak diversity
- single-trust-domain dependence

---

### 7. Configuration / Integrity Checks
Questions:
- is the source configured as expected
- are message-integrity assumptions still valid
- has the input path or trust boundary changed unexpectedly

Typical outputs:
- integrity valid
- integrity degraded
- integrity failed

---

## Trust Evaluation Philosophy

IX-Style does not require one bad check to immediately drive `UNTRUSTED`.

However, it also does not allow repeated weak indicators to be ignored forever.

The framework supports:

- immediate hard-fail triggers for severe cases
- persistence windows for noisy or intermittent cases
- corroboration-driven promotion or demotion
- trust decay under unresolved ambiguity
- harder recovery than initial trust grant

This is what prevents both overreaction and wishful thinking.

---

## Trust Transition Rules

### Rule 1 — Trust may degrade faster than it recovers
A severe contradiction can drop trust quickly.
Recovery requires persistence and corroboration.

### Rule 2 — Severe integrity failure can bypass gradual degradation
Some conditions should move directly to `UNTRUSTED` or `UNAVAILABLE`.

### Rule 3 — One weak source does not automatically poison everything
Trust propagation must be scoped, not hysterical.

### Rule 4 — Derived-state trust must depend on source trust
A beautiful estimate built on rotten inputs is not trusted.

### Rule 5 — Recovery must require evidence, not hope
A single healthy-looking sample is not enough to restore full trust.

---

## Trust Propagation

IX-Style explicitly propagates trust effects through the architecture.

### Upstream to Downstream Propagation
If a source becomes weak:
- dependent derived states may degrade
- dependent guidance or control actions may narrow
- relevant authority may reduce
- degraded mode entry may become appropriate

### Scoped Propagation
Trust loss should propagate to affected functions, not indiscriminately to the
entire vehicle.

Example:
A degraded environmental sensor should not necessarily collapse navigation trust.

### Compound Propagation
Multiple mild degradations across different sources may justify stronger posture
change than any one alone.

---

## Estimator Sanity Framework

Estimator sanity is a first-class concept in IX-Style.

An estimator may be numerically stable and still operationally unsafe if it is
being fed untrusted or contradictory inputs.

IX-Style estimator sanity checks should support:

- innovation/residual magnitude monitoring
- innovation persistence monitoring
- state jump detection
- derivative/rate plausibility checking
- covariance or uncertainty trend monitoring if available
- consistency with corroborating measurements
- reset/reinitialization event tracking
- divergence suspicion flags

### Estimator Sanity States

Baseline estimator sanity states:

- `ESTIMATOR_NOMINAL`
- `ESTIMATOR_ELEVATED_UNCERTAINTY`
- `ESTIMATOR_SUSPECT`
- `ESTIMATOR_DIVERGENT`
- `ESTIMATOR_UNAVAILABLE`

### Typical consequences

**ESTIMATOR_NOMINAL**
- normal bounded use permitted

**ESTIMATOR_ELEVATED_UNCERTAINTY**
- behavior may be narrowed
- operator visibility increased

**ESTIMATOR_SUSPECT**
- trust-conditioned constraints tighten
- nav or guidance behavior may reduce

**ESTIMATOR_DIVERGENT**
- estimator-dependent autonomy must be sharply reduced or blocked
- degraded posture likely
- containment bias increases

**ESTIMATOR_UNAVAILABLE**
- estimator-dependent mission behavior not allowed

---

## Navigation Confidence Framework

Navigation confidence deserves its own explicit model because a vehicle can have
some healthy sensors and still have an untrustworthy navigation picture.

### Navigation Confidence Inputs
At minimum, nav confidence should consider:

- navigation source freshness
- navigation continuity
- corroboration from independent references
- estimator/navigation consistency
- position/velocity/heading plausibility
- spoof-suspected discontinuities
- timing and ordering validity
- source diversity

### Navigation Trust States

Baseline nav trust states:

- `NAV_TRUSTED`
- `NAV_DEGRADED`
- `NAV_SUSPECT`
- `NAV_UNTRUSTED`
- `NAV_UNAVAILABLE`

### Example triggers

**NAV_DEGRADED**
- mild corroboration weakness
- moderate innovation elevation
- intermittent nav timing issues

**NAV_SUSPECT**
- repeated continuity anomalies
- estimator/nav disagreement
- weak or lost independent corroboration

**NAV_UNTRUSTED**
- spoof-suspected jump
- persistent contradiction
- severe integrity failure
- nav source accepted by transport but not by trust logic

---

## Subsystem Self-Report Trust

IX-Style does not blindly trust a subsystem just because it says it is healthy.

Subsystem self-report trust checks compare:
- claimed mode/state
- observed effect
- timing expectations
- peer signals
- authority context

Example:
If an actuator subsystem reports successful completion but external effect does
not match, self-report trust degrades even if the message format is valid.

This matters because lying subsystems are not always malicious.
Sometimes they are simply broken.

---

## Trust-Conditioned Behavior Mapping

Trust states must affect behavior.

### TRUSTED
- normal bounded use for allowed functions

### DEGRADED
- narrower envelopes
- increased guard scrutiny
- elevated evidence verbosity
- possible function-specific derating

### SUSPECT
- containment bias increases
- autonomy authority narrows sharply for dependent functions
- stronger cross-check requirements
- degraded mode entry likely for critical functions

### UNTRUSTED
- dependent critical actions blocked or substituted
- mode escalation likely
- operator visibility elevated
- recovery lockout likely until corroboration returns

### UNAVAILABLE
- treat as missing, not silently zero or healthy
- dependent functions must explicitly handle absence

---

## Trust and Mode Interaction

Trust transitions may drive mode changes, but not every small trust movement
requires dominant posture change.

Examples:
- one noncritical source goes `DEGRADED` and only local function derates
- critical navigation trust goes `SUSPECT` and dominant posture becomes `NAV_DEGRADED`
- assurance confidence goes `UNTRUSTED` and `ASSURANCE_DEGRADED` becomes dominant
- multi-domain trust collapse pushes directly toward `SAFE_HOLD`

---

## Trust and Authority Interaction

Trust can reduce authority in several ways:

- reject stale operator command
- narrow autonomy guidance request acceptance
- block recovery action
- freeze a suspect command path
- reduce maneuver envelope due to weak actuator confidence
- require contingency logic to outrank nominal autonomy

The authority model consumes trust posture rather than assuming all permitted
sources remain equally valid forever.

---

## Trust Recovery Rules

Trust recovery is intentionally conservative.

A degraded trust record may recover only when:

- the degrading condition is no longer active
- corroborating checks remain healthy for a persistence window
- no stronger conflicting evidence remains
- recovery policy allows restoration
- evidence is written for the trust transition

Typical recovery paths:
- `UNAVAILABLE -> SUSPECT -> DEGRADED -> TRUSTED`
- `UNTRUSTED -> SUSPECT -> DEGRADED -> TRUSTED`

Direct jump from `UNTRUSTED` to `TRUSTED` should be rare and policy-controlled.

---

## Hysteresis and Anti-Flapping Rules

IX-Style must avoid trust flapping.

The framework therefore supports:

- entry persistence thresholds
- exit persistence thresholds
- stronger evidence required for recovery than for degradation
- transition counters
- recent-transition memory
- optional latching for repeated severe cases

This reduces oscillation and operator confusion.

---

## Trust Evidence Requirements

For each safety-relevant trust transition, IX-Style must be able to record:

- trust record identifier
- previous trust state
- new trust state
- affected domain
- affected source or derived entity
- transition time
- active cause codes
- supporting check results
- related fault IDs if present
- affected posture if any
- rationale summary

This is the difference between “we lost trust” and “we can prove why we lost trust.”

---

## Example Scenarios

### Scenario 1 — Stale source with otherwise plausible value
- freshness fails
- plausibility remains nominal
- cross-consistency unavailable

Result:
- trust degrades based on timing, not value
- dependent actions narrow
- system does not pretend the value is okay just because it looks reasonable

### Scenario 2 — Spoof-suspected navigation jump
- nav continuity fails
- corroboration disappears
- estimator/nav disagreement rises

Result:
- nav trust drops sharply
- nav-dependent behavior is clamped or blocked
- `NAV_DEGRADED` or stronger posture likely

### Scenario 3 — Actuator self-report mismatch
- actuator reports success
- observed state change does not match
- timing also weakens

Result:
- self-report trust degrades
- actuator confidence degrades
- actuation authority narrows

### Scenario 4 — Apparent recovery after one clean sample
- previous contradiction existed
- one new sample looks healthy

Result:
- no instant full-trust restoration
- source may move only one step upward if recovery policy allows
- persistence window still required

---

## Trust Non-Negotiables

IX-Style trust architecture is not complete unless:

1. trust is explicit, not implicit
2. trust states affect behavior
3. derived-state trust depends on source trust
4. navigation trust is modeled separately from generic sensor trust
5. trust recovery is harder than trust degradation
6. trust transitions generate evidence
7. subsystem self-report is challengeable
8. estimator sanity is treated as first-class

---

## Deferred Items

This commit intentionally does not yet finalize:

- numeric thresholds for freshness, plausibility, or innovations
- vehicle-specific estimator algorithms
- exact covariance interpretation rules
- exact source-diversity weighting logic
- exact persistence timer values
- exact confidence-scoring math

Those belong in later commits and target-platform tailoring.

---

## Completion Criteria

This trust framework is not mature until later commits allocate:

1. concrete trust record schemas
2. concrete trust cause codes
3. detector-to-trust-transition mappings
4. posture rules driven by trust states
5. verification scenarios for trust degradation and recovery
6. reference code scaffolding for trust evaluation

