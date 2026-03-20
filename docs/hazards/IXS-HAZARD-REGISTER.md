# IX-Style Preliminary Hazard Register

## Document ID

IXS-HAZARD-REGISTER

## Status

Preliminary repository-level hazard register.

## Purpose

This document identifies the top-level hazards IX-Style must address as an
assured-autonomy reference architecture.

The goal is not to guess a final aircraft or spacecraft hazard analysis.
The goal is to define the classes of safety-relevant failure or trust-collapse
conditions that the repository must explicitly cover through:

- requirements
- monitors
- authority logic
- FDIR
- runtime assurance
- degraded modes
- evidence capture
- verification scenarios

---

## Scope

This register covers architecture-level hazards associated with:

- sensor trust collapse
- estimator inconsistency
- navigation trust degradation
- comms degradation
- timing degradation
- power/resource degradation
- actuator response uncertainty
- command arbitration failure
- policy bypass
- unsafe autonomy action
- evidence loss
- message integrity loss
- monitor failure
- uncontrolled recovery or restoration of authority

This register does **not** yet assign platform-specific quantitative risk values.

---

## Repository Hazard Philosophy

IX-Style treats hazards in three layers:

1. **Unsafe world-state progression**
   - The vehicle enters or approaches an unsafe state.

2. **Unsafe control or autonomy progression**
   - A command, mode, or authority decision makes the situation worse.

3. **Unsafe observability or evidence progression**
   - The system loses the ability to explain, audit, or correctly understand
     what it is doing.

A serious assured-autonomy architecture must address all three.

---

## Hazard Severity Bands

The severity model used here is repository-level only and will be tailored later.

### Catastrophic
Potential loss of vehicle, loss of controlled containment, or unrecoverable
mission-threatening behavior.

### Critical
Major loss of function or containment margin requiring immediate intervention,
degraded operation, or mission abort posture.

### Major
Loss of important capability or trust requiring bounded degraded operation.

### Minor
Noticeable reduction in capability or monitoring quality with limited direct
safety impact if contained.

---

## Hazard Register

### IXS-HZ-001 — Sensor trust collapse causes unsafe continued operation

**Description**  
One or more sensors provide stale, drifting, implausible, missing, or internally
inconsistent data, and the system continues operating with more authority than
is justified.

**Representative causes**
- silent sensor drift
- stale timestamps
- dropouts interpreted as nominal values
- partial corruption
- disagreement between redundant sources
- trust collapse not propagated downstream

**Potential consequences**
- incorrect state estimate
- unsafe command generation
- delayed degraded-mode entry
- false confidence in autonomy outputs

**Minimum architectural responses**
- freshness checks
- plausibility/range checks
- cross-source consistency checks
- confidence degradation rules
- authority reduction on trust collapse
- evidence capture for trust transitions

**Linked requirements**
- IXS-SYS-011
- IXS-SYS-012
- IXS-SYS-013
- IXS-SYS-014
- IXS-SYS-041
- IXS-SYS-046

**Preliminary severity**
Critical to Catastrophic, depending on function affected.

---

### IXS-HZ-002 — Estimator divergence is not detected in time

**Description**  
The system state estimator drifts, jumps, oscillates, or otherwise becomes
unsupported by trusted measurements, yet autonomy continues using it.

**Representative causes**
- filter divergence
- bad initialization
- poor update timing
- stale or inconsistent measurements
- hidden model mismatch
- trust not coupled to innovation/sanity checks

**Potential consequences**
- unsafe position/attitude/velocity inference
- envelope violations
- delayed recovery action
- improper mitigation selection

**Minimum architectural responses**
- estimator sanity checks
- innovation/residual monitoring hooks
- temporal consistency checks
- divergence-triggered degraded mode entry
- evidence record of estimator confidence collapse

**Linked requirements**
- IXS-SYS-015
- IXS-SYS-016
- IXS-SYS-023
- IXS-SYS-028
- IXS-SYS-029

**Preliminary severity**
Critical to Catastrophic.

---

### IXS-HZ-003 — Navigation trust degradation or spoof-suspected condition is mishandled

**Description**  
Navigation inputs become untrustworthy, potentially due to spoofing,
cross-system inconsistency, state jumps, or lack of independent corroboration,
but the system fails to reduce reliance on them appropriately.

**Representative causes**
- spoof-like state discontinuities
- trust imbalance between sources
- missing corroboration
- stale navigation updates
- implausible rates or position changes

**Potential consequences**
- unsafe guidance decisions
- path deviation
- containment loss
- incorrect autonomous mission progression

**Minimum architectural responses**
- navigation trust state
- corroboration-aware trust reduction
- navigation-degraded mode
- authority clamp for nav-dependent actions
- explicit evidence of spoof suspicion handling

**Linked requirements**
- IXS-SYS-015
- IXS-SYS-024
- IXS-SYS-032
- IXS-SYS-042
- IXS-SYS-047

**Preliminary severity**
Critical to Catastrophic.

---

### IXS-HZ-004 — Communication loss or intermittency causes unsafe authority assumptions

**Description**  
Loss or degradation of communications leads the system to assume operator
availability, stale command validity, or unsafe restoration of authority.

**Representative causes**
- link loss
- intermittent link
- delayed command arrival
- stale operator intent
- asynchronous mode assumptions
- reconnection without authority reconciliation

**Potential consequences**
- conflicting control assumptions
- missed contingency response
- operator surprise
- uncontrolled command acceptance after reconnect

**Minimum architectural responses**
- comms-degraded mode
- freshness-aware command acceptance
- authority freeze or downgrade on stale intent
- explicit reconnect reconciliation
- delayed-link telemetry behavior
- evidence capture for command acceptance/rejection

**Linked requirements**
- IXS-SYS-007
- IXS-SYS-010
- IXS-SYS-032
- IXS-SYS-040
- IXS-SYS-050
- IXS-SYS-058

**Preliminary severity**
Major to Critical.

---

### IXS-HZ-005 — Timing degradation invalidates safety decisions

**Description**  
Monitors, control updates, commands, or evidence events become late, out of
sequence, or mis-timestamped, but the system continues acting as though timing
assumptions remain valid.

**Representative causes**
- clock drift
- delayed monitor updates
- asynchronous message ordering
- scheduler overload
- stale evidence or control events

**Potential consequences**
- late vetoes
- expired commands executed as current
- incorrect fault confirmation
- loss of confidence posture integrity

**Minimum architectural responses**
- timing validity as first-class signal
- freshness thresholds
- missed-update detection
- timing-aware authority reduction
- timing-aware evidence model

**Linked requirements**
- IXS-SYS-013
- IXS-SYS-035
- IXS-SYS-038
- IXS-SYS-057
- IXS-SYS-058

**Preliminary severity**
Critical.

---

### IXS-HZ-006 — Power brownout or resource degradation disables safety before autonomy

**Description**  
The vehicle enters a power- or resource-degraded condition and sheds or loses
the wrong functions first, leaving nominal autonomy active while critical
monitoring or containment functions are reduced.

**Representative causes**
- incorrect load-shed priority
- monitor starvation
- telemetry overload in low-power state
- unsafe sequencing of function disablement

**Potential consequences**
- inability to detect constraint violations
- loss of safe-hold capability
- unsafe continued operation under weak observability

**Minimum architectural responses**
- essential-function definition
- power-degraded mode
- priority preservation for monitors and mode management
- resource-aware shedding policy
- evidence capture of load-shed decisions

**Linked requirements**
- IXS-SYS-024
- IXS-SYS-032
- IXS-SYS-059
- IXS-SYS-060

**Preliminary severity**
Critical to Catastrophic.

---

### IXS-HZ-007 — Actuator non-response or partial response is not contained

**Description**  
A commanded function does not respond, responds only partially, or behaves in a
manner inconsistent with the commanded action, and the system continues assuming
normal execution.

**Representative causes**
- stuck actuator
- degraded actuator authority
- lag outside assumptions
- false-positive completion report
- missing feedback confirmation

**Potential consequences**
- command mismatch
- runaway compensation
- envelope violation
- incorrect recovery logic

**Minimum architectural responses**
- actuator confidence tracking
- command/response correlation checks
- escalation to degraded or safe-hold mode
- mitigation substitution logic where applicable
- evidence capture of command-to-response mismatch

**Linked requirements**
- IXS-SYS-018
- IXS-SYS-021
- IXS-SYS-026
- IXS-SYS-027
- IXS-SYS-041

**Preliminary severity**
Critical to Catastrophic.

---

### IXS-HZ-008 — Conflicting command sources are not arbitrated deterministically

**Description**  
Multiple command sources attempt to influence the same controlled function
without a deterministic authority outcome.

**Representative causes**
- operator/autonomy conflict
- safety supervisor not dominant
- stale remote command competing with local logic
- contingency logic and nominal autonomy issuing incompatible actions

**Potential consequences**
- oscillatory control
- unsafe control races
- operator confusion
- hidden authority takeover

**Minimum architectural responses**
- explicit authority model
- precedence rules
- single authoritative command output
- evidence of source and arbitration outcome
- no ambiguous mixed-authority state

**Linked requirements**
- IXS-SYS-006
- IXS-SYS-007
- IXS-SYS-008
- IXS-SYS-009
- IXS-SYS-010

**Preliminary severity**
Critical.

---

### IXS-HZ-009 — Runtime assurance fails to block an unsafe nominal command

**Description**  
Nominal autonomy proposes an unsafe action and the runtime-assurance layer does
not detect, veto, clamp, substitute, or otherwise contain it in time.

**Representative causes**
- incomplete constraint model
- monitor disabled
- intervention path failure
- actuator confidence not considered
- insufficient timing margin
- nominal and safety logic not truly independent

**Potential consequences**
- direct unsafe action
- envelope violation
- loss of containment
- mode escalation too late to help

**Minimum architectural responses**
- independent safety guard
- pre-execution intervention
- fail-safe intervention outcomes
- timing-sensitive verification
- monitor health and intervention evidence

**Linked requirements**
- IXS-SYS-023
- IXS-SYS-024
- IXS-SYS-025
- IXS-SYS-026
- IXS-SYS-056

**Preliminary severity**
Catastrophic.

---

### IXS-HZ-010 — Unsafe restoration of full authority after degradation

**Description**  
The system returns to full authority too early, too quietly, or without
sufficient policy checks after a safety-relevant confidence collapse.

**Representative causes**
- automatic silent reset
- insufficient persistence checks
- operator not informed
- latched fault bypass
- recovered signal trusted immediately

**Potential consequences**
- repeated unsafe oscillation between modes
- brittle recovery behavior
- hidden trust assumption reintroduction

**Minimum architectural responses**
- explicit exit rules
- policy-controlled recovery
- persistence and corroboration checks
- operator-visible restoration rationale
- no silent full-authority restoration

**Linked requirements**
- IXS-SYS-019
- IXS-SYS-030
- IXS-SYS-033
- IXS-SYS-034
- IXS-SYS-047

**Preliminary severity**
Critical.

---

### IXS-HZ-011 — Policy violation or bypass allows prohibited control action

**Description**  
A command or mode transition violates a policy boundary but is still accepted or
executed.

**Representative causes**
- bad policy evaluation
- incomplete policy map
- missing authority check
- insecure override path
- stale policy context

**Potential consequences**
- prohibited unsafe action
- invalid override acceptance
- improper mission progression
- loss of review trust

**Minimum architectural responses**
- policy gate for safety-relevant actions
- authenticated override handling
- evidence records for approvals and denials
- policy violation fault classification

**Linked requirements**
- IXS-SYS-002
- IXS-SYS-003
- IXS-SYS-017
- IXS-SYS-037
- IXS-SYS-041

**Preliminary severity**
Critical.

---

### IXS-HZ-012 — Message integrity loss corrupts control-plane trust

**Description**  
Safety-relevant control or mode-management messages are altered, forged,
misattributed, replayed, or otherwise accepted without justified trust.

**Representative causes**
- integrity failure
- origin authentication failure
- replay acceptance
- incorrect message class handling
- trust not tied to message source

**Potential consequences**
- unauthorized control influence
- false mode change
- spurious evidence entries
- degraded operator trust in records

**Minimum architectural responses**
- integrity checks
- authenticated origin
- replay-aware handling
- command/evidence data-class separation
- authority impact rules for message trust loss

**Linked requirements**
- IXS-SYS-036
- IXS-SYS-037
- IXS-SYS-038
- IXS-SYS-039
- IXS-SYS-040

**Preliminary severity**
Critical.

---

### IXS-HZ-013 — Safety-relevant evidence is incomplete, mutable, or missing

**Description**  
The system takes a safety-relevant action but does not preserve enough evidence
to reconstruct what happened and why.

**Representative causes**
- missing decision receipt
- telemetry/evidence commingling
- event overwrite
- mutable logs
- insufficient rationale fields
- lost ordering information

**Potential consequences**
- inability to audit decision path
- weak post-event analysis
- weak operator trust
- weak certification or review posture

**Minimum architectural responses**
- dedicated evidence records
- append-only or tamper-evident storage pattern
- explicit rationale schema
- ordering and authority-state fields
- separation from routine telemetry

**Linked requirements**
- IXS-SYS-041
- IXS-SYS-042
- IXS-SYS-043
- IXS-SYS-044
- IXS-SYS-045

**Preliminary severity**
Major to Critical.

---

### IXS-HZ-014 — Operator support obscures active hazards or mitigation status

**Description**  
Mission-health displays or event streams fail to communicate active hazard,
authority, or mitigation posture clearly enough for informed operator review.

**Representative causes**
- poor prioritization
- buried active faults
- unclear mode labels
- insufficient rationale presentation
- too much nominal noise

**Potential consequences**
- delayed human response
- incorrect override attempt
- misunderstanding of vehicle posture
- weak post-event confidence

**Minimum architectural responses**
- prioritized mission-health model
- compact safety-relevant event stream
- visible authority and confidence state
- explicit rationale summaries

**Linked requirements**
- IXS-SYS-046
- IXS-SYS-047
- IXS-SYS-048
- IXS-SYS-049

**Preliminary severity**
Major.

---

### IXS-HZ-015 — Safety monitor or evidence subsystem failure goes unnoticed

**Description**  
The very subsystem responsible for safety supervision, monitoring, or evidence
capture partially fails, and the system does not recognize that its own
assurance posture has degraded.

**Representative causes**
- dead monitor loop
- invalid watchdog assumptions
- evidence sink unavailable
- self-health not monitored
- failed intervention path masked as nominal

**Potential consequences**
- false confidence in assurance layer
- undetected unsafe command pass-through
- invisible loss of evidence

**Minimum architectural responses**
- monitor self-health signals
- evidence-path health signals
- degraded assurance posture state
- fail-safe authority reduction when the guard itself is suspect

**Linked requirements**
- IXS-SYS-023
- IXS-SYS-028
- IXS-SYS-041
- IXS-SYS-056
- IXS-SYS-057

**Preliminary severity**
Critical to Catastrophic.

---

### IXS-HZ-016 — Concurrent faults overwhelm prioritization or mode logic

**Description**  
Two or more faults occur together and the system handles them as isolated events
without coherent prioritization or containment.

**Representative causes**
- sensor fault during power degradation
- comms loss during navigation uncertainty
- actuator degradation during safe-hold entry
- conflicting mitigation logic
- no multi-fault priority policy

**Potential consequences**
- unstable mode switching
- contradictory mitigations
- hidden escalation
- unsafe containment failure

**Minimum architectural responses**
- concurrent fault representation
- prioritization model
- deterministic mitigation precedence
- conflict-resolving degraded-mode logic
- multi-fault verification scenarios

**Linked requirements**
- IXS-SYS-020
- IXS-SYS-021
- IXS-SYS-029
- IXS-SYS-052
- IXS-SYS-055

**Preliminary severity**
Critical.

---

## Cross-Cutting Hazard Themes

The following themes recur across most hazards and must become first-class design
concepts in later commits:

- trust is degradable
- authority must be explicit
- timing validity matters
- evidence is part of safety
- degraded modes must be deterministic
- safety supervision must remain effective when the nominal path is wrong
- recovery must be policy-controlled, not wishful

---

## Required Next Allocations

This hazard register is not complete until later documents allocate each hazard to:

1. one or more requirements
2. one or more monitor concepts
3. one or more mode or authority behaviors
4. one or more mitigation patterns
5. one or more verification scenarios

That allocation is intentionally deferred to later commits.
