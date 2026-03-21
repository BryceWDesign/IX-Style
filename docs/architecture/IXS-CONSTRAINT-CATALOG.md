# IX-Style Constraint Catalog

## Document ID

IXS-CONSTRAINT-CATALOG

## Status

Draft architecture baseline.

## Purpose

This document defines the baseline runtime-assurance constraint catalog for
IX-Style.

It exists to answer the question:

> What explicit rules does the guard evaluate when deciding whether a candidate
> action may proceed, be clamped, be substituted, be frozen, or be vetoed?

This matters because a serious assured-autonomy repo cannot hide its safety
posture inside vague "guard logic" language.
It must name the important constraints explicitly.

---

## Constraint Philosophy

IX-Style does not use one giant monolithic safety rule.

It uses a catalog of explicit constraints that are:

- named
- reviewable
- triggerable
- evidence-producing
- allocatable to hazards, modes, and tests

Each constraint should be understandable as an engineering rule rather than as
mystery behavior.

---

## Constraint Families

The baseline repository groups constraints into the following families:

### CONTAINMENT
Rules that preserve safe bounded posture above mission progress.

### ASSURANCE
Rules that reduce or freeze authority when the assurance layer itself is weak.

### RESOURCE
Rules that preserve essential function under low power or resource margin.

### NAVIGATION_TRUST
Rules that bound movement-related behavior when navigation trust is weak or
collapsing.

### SENSOR_TRUST
Rules that narrow behavior when critical sensing confidence drops.

### ACTUATION_CONFIDENCE
Rules that narrow behavior when control effect cannot be trusted.

### RECOVERY_CONTROL
Rules that prevent unsafe authority expansion or premature recovery.

---

## Executable Baseline Constraints

The following constraints are the first executable set implemented in the
reference guard.

### IXS-CONSTRAINT-001 — SAFE_HOLD_MISSION_PROGRESS_BLOCK

**Family**
CONTAINMENT

**Intent**
Block mission-progress and override-like command classes when the dominant
posture is safe-hold.

**Typical trigger**
- current posture is `SAFE_HOLD`
- requested function class is mission-progress or override oriented

**Typical outcomes**
- `VETO`
- containment posture remains active

**Rationale**
Safe-hold exists to preserve bounded containment, not to quietly allow ordinary
mission behavior to continue.

---

### IXS-CONSTRAINT-002 — ASSURANCE_DEGRADED_HIGH_RISK_FREEZE

**Family**
ASSURANCE

**Intent**
Freeze high-risk command paths when assurance confidence is degraded enough that
the guard itself cannot honestly claim full-strength protection.

**Typical trigger**
- current posture is `ASSURANCE_DEGRADED`
- requested function class is guidance, actuation, resource configuration, or
  policy override

**Typical outcomes**
- `FREEZE`
- authority path remains blocked until assurance health improves

**Rationale**
If the guardrails are weak, the system must narrow behavior rather than pretend
nothing changed.

---

### IXS-CONSTRAINT-003 — POWER_MARGIN_RESOURCE_CLAMP

**Family**
RESOURCE

**Intent**
Clamp resource-costly command classes when power or resource margin is low.

**Typical trigger**
- active degradation includes `power_margin_low`
- requested function class is guidance, actuation, or resource configuration

**Typical outcomes**
- `CLAMP`

**Rationale**
Mission progress must narrow before essential monitoring and containment support
are endangered.

---

### IXS-CONSTRAINT-004 — NAV_SPOOF_SUSPECTED_MOTION_VETO

**Family**
NAVIGATION_TRUST

**Intent**
Veto motion-related commands when navigation trust has collapsed into a spoof-
suspected condition.

**Typical trigger**
- active degradation includes `nav_spoof_suspected`
- requested function class is guidance or actuation

**Typical outcomes**
- `VETO`

**Rationale**
A movement-capable vehicle should not continue treating nav-dependent behavior as
safe when the navigation picture is actively suspect.

---

### IXS-CONSTRAINT-005 — NAV_DEGRADED_MOTION_CLAMP

**Family**
NAVIGATION_TRUST

**Intent**
Clamp motion-related behavior when navigation trust is degraded but not yet in a
hard spoof-suspected collapse state.

**Typical trigger**
- active degradation includes `nav_corroboration_lost`
- requested function class is guidance or actuation

**Typical outcomes**
- `CLAMP`

**Rationale**
Not every nav degradation requires a hard veto, but weakened navigation should
still narrow behavior.

---

### IXS-CONSTRAINT-006 — SENSOR_TRUST_MOTION_CLAMP

**Family**
SENSOR_TRUST

**Intent**
Clamp motion-related behavior when critical sensor trust is low.

**Typical trigger**
- active degradation includes `sensor_trust_low`
- requested function class is guidance or actuation

**Typical outcomes**
- `CLAMP`

**Rationale**
Critical sensing weakness should reduce maneuver confidence even if one clean
value still appears plausible.

---

### IXS-CONSTRAINT-007 — ACTUATION_UNCERTAIN_MOTION_CLAMP

**Family**
ACTUATION_CONFIDENCE

**Intent**
Clamp motion-related behavior when control effect is uncertain.

**Typical trigger**
- active degradation includes `actuator_response_uncertain`
- requested function class is guidance or actuation

**Typical outcomes**
- `CLAMP`

**Rationale**
If commanded effect cannot be trusted fully, the system should narrow behavior
rather than keep issuing full-strength requests.

---

### IXS-CONSTRAINT-008 — COMMS_DEGRADED_OPERATOR_RECOVERY_DEFER

**Family**
RECOVERY_CONTROL

**Intent**
Defer remote operator recovery actions when communications are degraded or
staleness concerns remain active.

**Typical trigger**
- active degradation includes `comms_link_intermittent` or `command_freshness_low`
- command source is `OPERATOR`
- requested function class is `RECOVERY_ACTION`

**Typical outcomes**
- `DEFER`

**Rationale**
Recovery-expanding behavior should not proceed on weak or possibly stale remote
intent.

---

## Constraint Evaluation Rules

### Rule 1 — Constraints may stack
Multiple constraints may trigger on the same candidate action.

### Rule 2 — Stronger constraints win
If multiple constraints apply, the guard selects the strongest outcome according
to containment-first precedence.

### Rule 3 — All triggered constraints matter
Even if only one outcome is selected, all triggered constraint IDs should appear
in evidence where practical.

### Rule 4 — Constraints are posture-aware
The same function class may be allowed in one posture and blocked in another.

### Rule 5 — Constraints are trust-aware
Trust degradation is not cosmetic. It must narrow behavior.

---

## Outcome Strength Ordering

The baseline executable precedence is:

1. `ESCALATE_TO_MODE_CHANGE`
2. `VETO`
3. `FREEZE`
4. `SUBSTITUTE`
5. `CLAMP`
6. `DEFER`
7. `ACCEPT`

This ordering is containment-biased by design.

---

## Why a Constraint Catalog Matters

The constraint catalog exists so IX-Style can support:

- reviewable runtime-assurance logic
- explicit traceability
- testable rule evaluation
- evidence that cites named constraints
- later extension without logic sprawl

Without this catalog, the guard is too easy to dismiss as a bundle of hidden
conditionals.

---

## Deferred Items

This commit intentionally does not yet add:

- numeric envelope instances
- vehicle-specific limit values
- substitute-action libraries
- formal constraint-expression language
- timing-budget-based constraint tuning

Those belong in later commits.

---

## Completion Criteria

The constraint catalog is not mature until later commits allocate:

1. more constraint IDs tied to specific hazards and modes
2. executable envelope instances
3. stronger substitution logic
4. verification scenarios that challenge overlapping constraints
5. traceability mappings for each important constraint
