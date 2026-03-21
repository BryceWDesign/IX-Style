# IX-Style Recovery Gate and Authority Restoration Qualification

## Document ID

IXS-RECOVERY-GATE-AND-AUTHORITY-RESTORATION

## Status

Draft architecture baseline.

## Purpose

This document defines the recovery-gate architecture for IX-Style.

It exists to answer the question:

> When the system appears to be getting healthier, what must be true before
> reduced authority or degraded posture is allowed to expand again?

This matters because many systems are far better at entering degraded behavior
than at leaving it safely.

---

## Core Principle

IX-Style treats authority restoration as a first-class safety decision.

A system should not return to broader authority simply because:

- one sample looks healthier
- a remote operator asks for recovery
- one fault symptom stops momentarily
- a signal becomes present again after being missing

Recovery must be qualified.

---

## What the Recovery Gate Does

The recovery gate evaluates whether a candidate recovery-expanding action is
allowed to proceed.

It looks at:

- current dominant safety posture
- active degradation flags
- active fault records
- posture-driving trust records
- whether the command is a recovery action
- whether communications are strong enough for trusted remote recovery intent

The recovery gate can produce:

- `NOT_APPLICABLE`
- `PASSED`
- `FAILED`
- `DEFERRED`

These are not decorative labels.
They directly affect whether authority can expand.

---

## Recovery Gate Philosophy

### Rule 1 — Recovery is harder than degradation
A degraded system may enter a narrow posture quickly.
Leaving that posture should require stronger justification.

### Rule 2 — Posture-driving trust must be healed enough
If a trust record is still posture-driving and degraded, recovery should not
pretend otherwise.

### Rule 3 — Active significant faults still matter
Contained, latched, mitigating, or high-priority active faults must block or
delay recovery-expanding behavior.

### Rule 4 — Weak comms can defer remote recovery
An operator recovery request over degraded or freshness-uncertain comms should
not automatically gain authority.

### Rule 5 — Recovery gate output must be visible in evidence
A blocked or deferred restoration attempt is itself a review-critical event.

---

## Recovery Gate Statuses

### NOT_APPLICABLE
The current command is not a recovery-expanding action or recovery review is not
relevant to this decision.

### PASSED
Recovery-expanding behavior is permitted to continue into normal authority and
guard evaluation.

### FAILED
Recovery-expanding behavior is blocked because active trust, fault, or posture
conditions still make restoration unsafe.

### DEFERRED
Recovery-expanding behavior is temporarily held because trusted recovery intent
or context is not yet strong enough to proceed.

---

## Baseline Blocking Conditions

The executable baseline blocks recovery when one or more of the following are
true:

- one or more posture-driving trust records remain degraded
- one or more active contained, latched, or actively mitigating faults remain
- one or more active high-priority faults remain unresolved
- active degradation still signals major unresolved posture-driving weakness

Examples:
- `nav_spoof_suspected`
- `nav_corroboration_lost`
- `assurance_guard_unhealthy`
- `power_margin_low`
- `actuator_response_uncertain`
- `sensor_trust_low`

---

## Baseline Deferral Condition

The executable baseline defers operator-issued recovery actions when:

- `comms_link_intermittent` is active, or
- `command_freshness_low` is active

This exists because recovery-expanding behavior should not be granted on weak or
possibly stale remote intent.

---

## Recovery-Expanding Actions

The initial executable baseline treats `RECOVERY_ACTION` function-class commands
as recovery-expanding actions.

Later versions may extend this to include:

- posture-exit requests
- authority-restoration requests
- re-enable requests for previously frozen paths
- safe-hold exit requests
- qualified return-to-nominal requests

---

## Relationship to Other IX-Style Layers

### Recovery Gate vs FDIR
FDIR determines what faults remain active and how serious they are.

### Recovery Gate vs Trust
Trust records determine whether key posture-driving confidence has actually
recovered enough.

### Recovery Gate vs Authority
The recovery gate runs before ordinary authority restoration proceeds.

### Recovery Gate vs Guard
A passed recovery gate does not guarantee the final action is allowed.
It merely permits the candidate to continue into authority and guard review.

---

## Why the Gate Runs Early

The recovery gate should run before ordinary authority and guard handling for
recovery-expanding actions because:

- it filters unsafe restoration attempts early
- it keeps evidence clean about why restoration did not proceed
- it prevents normal command handling from treating recovery like a generic
  action request

---

## Evidence Expectations

A recovery-gate decision should preserve:

- recovery gate status
- blocking fault IDs if any
- blocking trust record IDs if any
- rationale summary
- whether the decision failed or deferred
- whether the candidate was allowed to continue

This is essential for later review.

---

## Deferred Items

This commit intentionally does not yet add:

- numeric persistence timers
- recovery qualification counters
- platform-specific restoration policies
- multi-stage partial restoration
- explicit human approval workflows
- recovery-specific evidence schemas beyond the decision receipt field

Those belong in later commits.

---

## Completion Criteria

This recovery-gate layer is not mature until later commits allocate:

1. explicit persistence windows
2. richer recovery qualification policies by posture
3. multi-step authority restoration
4. stronger integration with mode-exit policy
5. scenario coverage for repeated failed recovery attempts
