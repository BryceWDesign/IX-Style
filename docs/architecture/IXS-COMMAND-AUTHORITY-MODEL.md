# IX-Style Command Authority Model

## Document ID

IXS-COMMAND-AUTHORITY-MODEL

## Status

Draft architecture baseline.

## Purpose

This document defines how IX-Style handles command authority, command-source
precedence, and deterministic arbitration.

It exists to answer the following questions:

- who is allowed to influence a controlled function
- when authority must be reduced, frozen, or transferred
- how conflicts are resolved
- how stale or untrusted commands are rejected
- how the system proves which source actually won

This is a core assured-autonomy document. If authority is vague, the repo is
not serious.

---

## Core Principle

IX-Style does not allow "shared vibes" authority.

At every decision point, one of the following must be true:

1. a single source is authoritative
2. a higher-order safety function has explicitly constrained the output
3. the command is rejected
4. the system enters or remains in a degraded or containment posture

There is no acceptable ambiguous mixed-authority state for the same controlled
function at the same decision instant.

---

## Authority Layers

IX-Style defines five command-source layers.

### 1. Operator
Human-issued commands or supervising external control intent.

**Examples**
- approve mode transition
- request hold
- request recovery
- issue bounded mission directive
- apply policy-permitted override

**Notes**
Operator commands are not automatically supreme. They must still pass freshness,
policy, and safety checks.

---

### 2. Mission Logic
Deterministic mission-sequencing or task-management logic.

**Examples**
- advance a mission phase
- schedule a nominal activity
- request a resource-sensitive action
- request contingency branch entry

**Notes**
Mission logic expresses mission intent, not final safety authority.

---

### 3. Nominal Autonomy
Planning, guidance, decision-support, or adaptive mission behavior operating
within approved bounds.

**Examples**
- propose a maneuver
- select a route or next action
- recommend resource usage
- propose a response to a changing environment

**Notes**
Nominal autonomy is never the final authority for safety-relevant actuation.
Its outputs are candidates until checked.

---

### 4. Contingency Logic
Deterministic fallback logic for abnormal situations.

**Examples**
- lost-link response
- degraded navigation containment behavior
- power-preservation posture
- fallback reconfiguration request

**Notes**
Contingency logic exists to preserve control or survivability when nominal paths
are no longer acceptable.

---

### 5. Safety Supervisor
The highest-priority authority layer for safety-relevant intervention.

**Examples**
- veto command
- clamp command
- substitute safer command
- freeze authority
- force degraded mode
- force safe-hold entry

**Notes**
Safety supervisor authority is special. It does not "compete" in the same way
other sources compete. It can constrain or override the command outcome when
required by policy or hazard posture.

---

## Controlled Function Classes

Authority is evaluated per controlled function class rather than as one giant
global switch.

Initial function classes are:

- `MODE_MANAGEMENT`
- `MISSION_INTENT`
- `GUIDANCE_REQUEST`
- `ACTUATION_REQUEST`
- `RESOURCE_CONFIGURATION`
- `RECOVERY_ACTION`
- `POLICY_OVERRIDE`
- `EVIDENCE_CONTROL`

Different function classes may have different source permissions.

Example:
An operator may be allowed to request `MODE_MANAGEMENT`, while nominal autonomy
may only propose `GUIDANCE_REQUEST`.

---

## Authority State Components

IX-Style represents authority using the following components:

1. **command source**
2. **function class**
3. **requested action**
4. **trust/freshness status of source**
5. **current mission phase**
6. **current safety posture**
7. **active degradation flags**
8. **policy status**
9. **candidate decision outcome**
10. **final arbitration outcome**

This ensures command arbitration is based on current operational truth, not just
a static ranking table.

---

## High-Level Authority Rules

### Rule A — Safety always constrains final outcome
No source may force a safety-relevant action past the safety supervisor if the
action violates an active constraint, degraded-mode rule, or containment policy.

### Rule B — Operator commands must still be trusted
Operator input that is stale, unauthenticated, out of sequence, or prohibited by
current policy is not valid authority.

### Rule C — Nominal autonomy proposes; it does not self-certify
Nominal autonomy can request behavior but cannot directly declare its own
requests safe.

### Rule D — Contingency logic has elevated precedence during abnormal states
When active degraded or contingency posture exists, contingency logic may outrank
mission logic and nominal autonomy for relevant function classes.

### Rule E — Recovery is harder than action
Recovery actions that expand authority require explicit checks and usually need
operator approval or policy-qualified automatic approval.

### Rule F — Evidence is mandatory
Every safety-relevant arbitration outcome must record who requested what, what
constraints were active, and why the final outcome occurred.

---

## Baseline Source Permissions by Function Class

### MODE_MANAGEMENT
Allowed sources:
- operator
- contingency logic
- safety supervisor

Nominal autonomy may request mode-related recommendations indirectly, but may
not directly command safety posture transitions.

---

### MISSION_INTENT
Allowed sources:
- operator
- mission logic

Nominal autonomy may contribute planning proposals, but mission intent must pass
through mission logic or operator authority.

---

### GUIDANCE_REQUEST
Allowed sources:
- nominal autonomy
- contingency logic
- operator
- safety supervisor

Final actuation remains separately bounded.

---

### ACTUATION_REQUEST
Allowed sources:
- nominal autonomy
- contingency logic
- operator
- safety supervisor

All actuation requests pass through runtime assurance and authority checks.

---

### RESOURCE_CONFIGURATION
Allowed sources:
- mission logic
- contingency logic
- operator
- safety supervisor

Nominal autonomy may recommend but not finalize safety-relevant resource
reconfiguration unless explicitly delegated by policy.

---

### RECOVERY_ACTION
Allowed sources:
- operator
- contingency logic
- safety supervisor

Recovery that expands authority must satisfy recovery gate logic.

---

### POLICY_OVERRIDE
Allowed sources:
- operator
- safety supervisor

Policy override is tightly controlled and must be authenticated, justified, and
recorded.

---

### EVIDENCE_CONTROL
Allowed sources:
- safety supervisor
- system infrastructure

External suppression or mutation of safety-relevant evidence is not allowed.

---

## Baseline Precedence Model

IX-Style uses a function-aware precedence model, not a single universal ranking.

However, for most safety-relevant functions, the baseline precedence is:

1. `SAFETY_SUPERVISOR`
2. `CONTINGENCY_LOGIC`
3. `OPERATOR`
4. `MISSION_LOGIC`
5. `NOMINAL_AUTONOMY`

This is not a popularity ranking.
It is a containment-first ranking.

### Why operator is not always above contingency logic

In a degraded or delayed-link context, an operator command may be stale, while
deterministic contingency logic is the only current trustworthy source aligned
to safe containment.

Operator authority still matters, but not blindly.

---

## Arbitration Flow

Every command candidate follows this baseline flow:

1. source identified
2. function class identified
3. syntax/schema validity checked
4. authentication / origin trust checked
5. freshness / timing validity checked
6. source permission checked for that function class
7. current safety posture consulted
8. active degradation flags consulted
9. policy gate evaluated
10. conflicting candidates compared
11. runtime-assurance constraints applied
12. final outcome selected
13. evidence record written

If any required stage fails, the command is rejected, downgraded, substituted,
or routed into degraded-mode handling.

---

## Arbitration Outcomes

A candidate command may result in one of the following outcomes:

- `ACCEPT`
- `REJECT`
- `VETO`
- `CLAMP`
- `SUBSTITUTE`
- `DEFER`
- `FREEZE`
- `ESCALATE_TO_MODE_CHANGE`

### Outcome meanings

**ACCEPT**  
The command is permitted and remains within active constraints.

**REJECT**  
The command is not allowed due to trust, freshness, schema, source permission,
or policy failure.

**VETO**  
The command would create an unsafe condition and is explicitly blocked by the
safety supervisor.

**CLAMP**  
The command is accepted only in reduced form.

**SUBSTITUTE**  
A safer command replaces the original candidate.

**DEFER**  
The command is temporarily held pending reconciliation, confirmation, or higher-
priority decision.

**FREEZE**  
The command path or affected function is frozen to prevent ambiguous or unsafe
progression.

**ESCALATE_TO_MODE_CHANGE**  
The command attempt itself triggers or contributes to a degraded-mode or
containment transition.

---

## Authority Behavior by Safety Posture

### INITIALIZING
- operator input may be limited to setup, hold, or abort-like functions
- nominal autonomy has no unrestricted authority
- mission logic remains bounded
- safety supervisor may prevent exit from initialization

### NOMINAL
- normal source permissions apply
- nominal autonomy may propose guidance and actuation requests
- safety supervisor remains final constraint layer

### SENSOR_DEGRADED
- actions depending on degraded sensors are restricted
- nominal autonomy authority narrows according to trust loss
- operator commands still pass trust and policy checks
- contingency logic may outrank mission logic for affected functions

### NAV_DEGRADED
- nav-dependent requests are strongly bounded
- contingency logic may dominate movement-related requests
- recovery actions require explicit evidence and recovery qualification

### COMMS_DEGRADED
- stale remote operator commands are rejected or deferred
- pre-approved lost-link logic may temporarily outrank absent/stale operator input
- authority restoration on reconnect requires reconciliation

### POWER_DEGRADED
- resource-intensive requests are clamped or rejected
- preservation of essential functions outranks mission progress
- operator requests that threaten safe function preservation are not accepted

### ACTUATION_DEGRADED
- command magnitude and maneuver authority narrow
- substitution and clamp outcomes become more common
- repeated mismatch may force safe-hold escalation

### ASSURANCE_DEGRADED
- nominal autonomy authority reduces sharply
- commands depending on unavailable guard functions are blocked
- safe-hold bias increases

### SAFE_HOLD
- only containment-compatible actions are allowed
- mission-progress actions are suspended or heavily constrained
- exit requires explicit recovery qualification
- operator requests cannot bypass safe-hold policy gates

---

## Authority Freeze Conditions

Authority freeze is used when continuing to accept commands would be more
dangerous than temporarily holding state.

Typical freeze triggers include:

- unresolved conflicting command sources
- active trust ambiguity
- stale control intent with no safe refresh path
- evidence-path uncertainty during safety-critical transition
- mode transition in progress
- degraded timing invalidating arbitration confidence

Freeze is not the same as safe-hold, but freeze may lead to safe-hold.

---

## Authority Restoration Conditions

Authority restoration is not automatic.

Authority may be restored only when:

- the triggering degradation is cleared
- the recovery gate is satisfied
- the restored source is authenticated and fresh
- policy allows restoration
- no higher-priority containment condition remains
- restoration evidence is written

This is especially important after:
- comms restoration
- navigation recovery
- assurance-path recovery
- manual override completion

---

## Conflict Examples

### Example 1 — Operator vs nominal autonomy
- operator requests hold
- nominal autonomy requests maneuver continuation
- safety posture is nominal

**Outcome**  
Operator request wins for allowed function scope, subject to safety checks.

---

### Example 2 — Stale operator command vs contingency logic during link degradation
- operator request arrives late
- comms are degraded
- contingency logic requests bounded lost-link behavior

**Outcome**  
Late operator command is rejected or deferred.
Contingency logic wins if policy permits.

---

### Example 3 — Nominal autonomy requests unsafe actuation
- nominal autonomy proposes aggressive command
- runtime assurance detects envelope issue

**Outcome**  
Safety supervisor vetoes, clamps, or substitutes.
Nominal autonomy does not win.

---

### Example 4 — Recovery request from operator while assurance layer is degraded
- operator requests return to nominal
- assurance path self-health is still weak

**Outcome**  
Recovery rejected or deferred.
Assurance degradation blocks authority expansion.

---

## Evidence Requirements for Arbitration

Every safety-relevant arbitration decision must record:

- decision identifier
- timestamp / ordering metadata
- command source
- function class
- requested action summary
- source trust/freshness result
- active mission phase
- active safety posture
- active degradation flags
- policy result
- arbitration outcome
- final authoritative source
- rationale summary

This requirement exists because arbitration without evidence becomes mythology.

---

## Deferred Items

This document intentionally does not yet finalize:

- platform-specific command classes
- numeric freshness limits
- exact lost-link timing thresholds
- cryptographic implementation details
- exact per-function authority matrices for all target vehicles
- detailed recovery-approval policies

Those belong in later allocations.

---

## Completion Criteria

This authority model is not mature until later commits allocate:

1. message schemas to function classes
2. degraded modes to authority restrictions
3. evidence schema fields to arbitration outcomes
4. verification scenarios to conflict cases
5. reference code paths to this model
