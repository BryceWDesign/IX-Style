# IX-Style Runtime Assurance Guard Architecture

## Document ID

IXS-RUNTIME-ASSURANCE-GUARD

## Status

Draft architecture baseline.

## Purpose

This document defines the runtime-assurance guard architecture for IX-Style.

It exists to answer the question:

> When nominal autonomy proposes an action, how does IX-Style decide whether
> that action is still safe enough to allow, clamp, replace, or block?

This document is one of the central pillars of the repository.
Without it, IX-Style would still only describe bounded autonomy in words.

---

## Core Role of the Guard

The runtime-assurance guard is the independent supervisory layer that evaluates
candidate behavior against active constraints, trust posture, authority posture,
and containment rules before safety-relevant actions are allowed to proceed.

The guard is responsible for:

- checking candidate commands before execution
- evaluating active safety envelopes
- incorporating current confidence posture
- consulting current safety posture and active degradation flags
- deciding whether to accept, clamp, substitute, veto, freeze, or escalate
- emitting evidence explaining the intervention outcome

The guard is **not** the same thing as nominal autonomy.

Nominal autonomy proposes.
The guard disposes.

---

## Structural Independence Requirement

A central IX-Style rule is that the guard must remain structurally independent
from the nominal autonomy path.

That means:

1. nominal autonomy must not be the only entity deciding whether its own output
   is safe

2. constraint evaluation must not be hidden inside an opaque planner without
   independent observable outputs

3. intervention logic must remain reviewable even if nominal behavior grows more
   complex later

4. degraded assurance posture must be possible if the guard itself becomes weak

This independence is architectural, not merely philosophical.

---

## Guard Placement in the Decision Flow

The baseline decision flow is:

1. inputs arrive
2. trust and timing posture are updated
3. mission logic and nominal autonomy produce candidate intent
4. authority model determines whether the source is even eligible
5. runtime-assurance guard evaluates the candidate against constraints
6. arbitration outcome is finalized
7. allowed output is sent onward
8. evidence is written

The guard sits between candidate action generation and safety-relevant execution.

---

## Guard Inputs

The runtime-assurance guard consumes the following inputs at minimum:

### A. Candidate Action Inputs
- requested command or action
- command source
- function class
- requested magnitude / target / timing
- intended mission effect if available

### B. State and Estimate Inputs
- current estimated state
- estimator confidence
- recent state history as needed for rate checks
- current mission phase

### C. Trust and Timing Inputs
- sensor trust posture
- data freshness status
- timing validity status
- navigation trust posture
- message trust posture

### D. System Health Inputs
- active faults
- active degradation flags
- active safety posture
- actuator confidence
- power/resource posture
- assurance-path self-health

### E. Policy Inputs
- active safety constraints
- recovery gates
- mode restrictions
- function-specific permissions
- containment policies
- override policies

---

## Guard Outputs

The guard produces:

- intervention outcome
- constrained or replacement command if applicable
- triggered constraint identifiers
- confidence/risk rationale
- optional mode escalation request
- evidence payload for post-decision reconstruction

---

## Guard Intervention Outcomes

The guard supports the following baseline intervention outcomes:

- `ALLOW`
- `CLAMP`
- `SUBSTITUTE`
- `VETO`
- `FREEZE`
- `ESCALATE_SAFE_POSTURE`

### ALLOW
The candidate action remains inside active bounds and no stronger containment
rule applies.

### CLAMP
The candidate action is allowed only in a reduced or narrowed form.

Examples:
- lower rate than requested
- lower magnitude than requested
- narrower maneuver envelope
- shorter allowed duration

### SUBSTITUTE
A safer bounded action replaces the proposed one.

Examples:
- hold instead of proceed
- conservative fallback configuration instead of requested change
- reduced-mobility behavior instead of aggressive repositioning

### VETO
The candidate action is explicitly blocked because it would violate an active
constraint or create unacceptable containment risk.

### FREEZE
The affected authority path or controlled function is temporarily frozen because
the system cannot justify forward action safely.

### ESCALATE_SAFE_POSTURE
The attempted command itself contributes to or directly triggers a degraded-mode
or safe-hold transition.

---

## Constraint Model

IX-Style uses a multi-family constraint model rather than one giant safety score.

The guard evaluates candidate actions against several classes of constraints.

### 1. State Envelope Constraints
These bound state variables and their allowed regions.

Examples:
- position or region validity
- orientation/attitude limits
- speed/velocity bounds
- altitude/depth corridor
- thermal state bounds
- resource floor limits

### 2. Rate and Transition Constraints
These bound how quickly the system may change.

Examples:
- maximum rate of change
- maximum turn or slew rate
- recovery transition pacing
- mode transition sequencing rules

### 3. Trust-Conditioned Constraints
These tighten behavior when trust collapses.

Examples:
- reduced authority when navigation trust is weak
- reduced maneuvering when sensor disagreement is high
- blocking commands when freshness is invalid
- disallowing recovery while assurance confidence is degraded

### 4. Resource and Survivability Constraints
These preserve essential function under low margin.

Examples:
- prohibit high-cost actions during power-degraded posture
- preserve safe-hold function budget
- restrict reconfiguration that threatens monitoring continuity

### 5. Policy and Authority Constraints
These prevent actions that are disallowed regardless of raw physics.

Examples:
- invalid source for a function class
- prohibited override path
- action not allowed in current posture
- recovery request before gate satisfaction

### 6. Containment Constraints
These are stronger emergency-like rules used when the system must preserve
control or survivability above all else.

Examples:
- enter safe-hold
- freeze actuation expansion
- reject mission-progress actions
- lock out authority restoration

---

## Constraint Evaluation Philosophy

IX-Style does not assume every unsafe action can be identified by a single
numeric threshold.

The guard therefore evaluates constraints using a combination of:

- direct threshold checks
- temporal checks
- trust-conditioned policy checks
- posture-conditioned permission checks
- cross-signal consistency checks
- recovery-gate checks

This makes the guard more reviewable than an opaque risk score.

---

## Guard Decision Layers

The runtime-assurance guard evaluates candidate actions in five internal layers.

### Layer 1 — Eligibility Gate
Before anything else, determine whether the action is even eligible for further
consideration.

Questions:
- is the source permitted for this function class
- is the command fresh enough
- is the message trusted enough
- is the system in a posture where this action type is allowed

If no, the action is rejected or frozen before envelope checks.

---

### Layer 2 — Constraint Screening
Check whether the requested action violates explicit active constraints.

Questions:
- would this exceed active state bounds
- would this exceed rate bounds
- would this violate posture restrictions
- would this violate resource preservation rules

If yes, a later layer decides whether to clamp, substitute, veto, or escalate.

---

### Layer 3 — Confidence Conditioning
Evaluate whether the requested action assumes more trust than the system
currently has.

Questions:
- does this maneuver depend on trusted nav that is not currently available
- does this action require actuator confidence we do not have
- does this action depend on stale or conflicting data
- is assurance-path health good enough to permit this risk

This layer is one of the main ways IX-Style turns confidence into behavior.

---

### Layer 4 — Containment Bias
Evaluate whether the current situation demands containment-oriented behavior.

Questions:
- is safe-hold already active
- is escalation already pending
- are multiple degradations interacting
- is the assurance layer itself suspect

If yes, containment bias may push the outcome toward substitute, freeze, veto,
or escalation.

---

### Layer 5 — Intervention Selection
Choose the final outcome and produce evidence.

Questions:
- can the action be safely clamped
- is there a safer substitute defined
- is veto cleaner than risky reduction
- does the attempted action indicate the current mode is no longer sufficient

The selected outcome must be deterministic and explainable.

---

## Guard and Safety Posture Interaction

The runtime-assurance guard is posture-aware.

### NOMINAL
The guard still constrains action, but with the widest allowable envelope.

### SENSOR_DEGRADED
The guard narrows behaviors dependent on weakened sensors.

### NAV_DEGRADED
The guard strongly limits navigation-dependent action.

### COMMS_DEGRADED
The guard rejects stale remote influence and favors pre-approved contingency logic.

### POWER_DEGRADED
The guard biases toward survivability and safe function preservation.

### ACTUATION_DEGRADED
The guard narrows control authority and may substitute safer control behavior.

### ASSURANCE_DEGRADED
The guard may no longer be fully trustworthy itself, which is why assurance-
degraded posture must aggressively reduce authority and may force safe-hold.

### SAFE_HOLD
The guard operates in strongest containment mode and blocks mission-progress
behavior unless explicitly allowed by policy.

---

## Guard and FDIR Interaction

The runtime-assurance guard and FDIR are related but not identical.

### FDIR focuses on:
- detecting faults
- classifying faults
- isolating likely causes
- tracking fault lifecycle
- driving mitigation and recovery posture

### The guard focuses on:
- evaluating a candidate action right now
- preventing unsafe action from proceeding
- applying current constraints and trust posture
- selecting intervention outcome

In practice:
- FDIR updates the system’s fault and degradation state
- the guard consumes that state to bound action
- the guard may also generate signals that contribute back into FDIR or mode
  escalation

---

## Guard and Recovery Interaction

The guard is intentionally conservative about recovery-expanding actions.

Recovery-expanding actions include:
- return to nominal posture
- restoration of previously reduced authority
- re-enable previously blocked command path
- exit safe-hold
- accept restored comms authority
- accept restored nav trust

These actions shall receive stronger scrutiny than ordinary nominal actions
because they expand capability and therefore expand risk if taken too early.

---

## Guard Health and Self-Monitoring

IX-Style must treat the guard itself as a monitored subsystem.

The following guard-health concerns must be represented:

- guard loop not updating
- guard timing budget violation
- intervention path unavailable
- stale constraint set
- evidence emission failure
- internal inconsistency in intervention decision path

If guard health degrades below an acceptable threshold:

- authority must reduce
- mission-progress actions may be blocked
- assurance-degraded posture may become dominant
- safe-hold escalation may be required

This is what keeps IX-Style honest when its own guardrails weaken.

---

## Safety Envelope Structure

The baseline repository envelope structure uses the following hierarchy:

### Envelope Family
Broad class of constraints.
Examples:
- state
- rate
- resource
- posture
- authority
- containment

### Envelope Rule
Specific rule within a family.
Examples:
- maximum_allowed_velocity_for_posture
- no_recovery_without_gate
- no_high_cost_action_below_resource_floor
- no_nav_dependent_action_when_nav_trust_low

### Envelope Instance
Concrete configured version of a rule for a target platform or simulation.

This structure keeps the repo general enough for reuse while still being
allocatable later.

---

## Guard Evidence Requirements

Every guard decision affecting safety-relevant output must emit evidence
sufficient to reconstruct:

- candidate action summary
- command source
- function class
- active mission phase
- active safety posture
- active degradation flags
- triggered constraint IDs
- relevant trust posture signals
- intervention outcome
- final command if changed
- whether mode escalation was requested
- concise rationale string or structured rationale object

No guard intervention should become a mystery later.

---

## Timing Expectations

IX-Style does not hardcode platform numbers here, but the architecture requires:

1. guard evaluation must occur before safety-relevant execution
2. stale guard decisions must not be reused as though current
3. timing validity must influence confidence and authority
4. intervention latency must become a verification target later

This document defines the structure that later timing tests must validate.

---

## Reference Guard Diagram

```mermaid
flowchart TD
    A[Candidate Action] --> B[Eligibility Gate]
    B -->|not eligible| X[Reject / Freeze / Evidence]
    B -->|eligible| C[Constraint Screening]
    C --> D[Confidence Conditioning]
    D --> E[Containment Bias]
    E --> F[Intervention Selection]

    F -->|ALLOW| G[Forward Allowed Command]
    F -->|CLAMP| H[Forward Clamped Command]
    F -->|SUBSTITUTE| I[Forward Substitute Command]
    F -->|VETO| J[Block Command]
    F -->|FREEZE| K[Freeze Authority Path]
    F -->|ESCALATE| L[Request Mode Escalation]

    G --> M[Evidence Record]
    H --> M
    I --> M
    J --> M
    K --> M
    L --> M

Guard Non-Negotiables

IX-Style runtime assurance is not complete unless:

the guard is structurally independent from nominal autonomy

posture and trust affect action permission

unsafe candidate actions can be blocked before execution

recovery-expanding actions receive stronger scrutiny

guard self-health can degrade assurance posture

evidence is always produced for safety-relevant interventions

Deferred Items

This commit intentionally does not yet finalize:

numeric envelope thresholds

target-platform dynamics-specific rules

exact substitute-command library

exact recovery gate timings

exact guard implementation language/runtime

exact formal methods strategy for rule checking

Those belong in later commits.

Completion Criteria

This guard architecture is not mature until later commits allocate:

concrete constraint identifiers

concrete message schemas for candidate actions and intervention outcomes

code scaffolding for guard evaluation

verification scenarios covering allow/clamp/substitute/veto/freeze/escalate

explicit mapping from hazards and postures into constraint rules
