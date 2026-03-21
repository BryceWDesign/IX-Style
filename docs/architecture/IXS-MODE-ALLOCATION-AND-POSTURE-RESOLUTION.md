# IX-Style Mode Allocation and Posture Resolution

## Document ID

IXS-MODE-ALLOCATION-AND-POSTURE-RESOLUTION

## Status

Draft architecture baseline.

## Purpose

This document defines how IX-Style resolves trust outcomes, fault outcomes, and
active degradation flags into one explicit dominant safety posture.

It exists to answer the question:

> When several trust degradations, faults, or containment hints are active at
> once, which safety posture becomes dominant, why, and how is that transition
> recorded?

This matters because an assured-autonomy architecture must not force operators
or downstream logic to guess which problem currently matters most.

---

## Core Principle

IX-Style treats dominant safety posture as a resolved operational truth, not as
an informal interpretation of raw flags.

That means:

- trust outcomes can influence posture
- fault outcomes can influence posture
- active degradation flags can influence posture
- the final dominant posture is selected using explicit precedence
- a posture transition becomes a first-class event

---

## Why Posture Resolution Exists

The repo already represents:

- trust records
- fault records
- degradation flags
- runtime-assurance interventions

But those signals are not the same as one clear posture.

A vehicle might simultaneously have:

- degraded navigation trust
- low power margin
- one active actuator fault
- intermittent comms

Without posture resolution, operators and automation would be left asking:

- which degradation dominates
- which restrictions should take precedence
- whether containment bias should rise
- whether the system is closer to degraded operation or safe-hold

This layer answers that.

---

## Inputs to Posture Resolution

The posture allocator evaluates:

1. base posture from the scenario or current operating context
2. active degradation flags
3. trust records and trust states
4. fault records and lifecycle states
5. fault priority
6. containment significance

The allocator does not invent evidence from nowhere.
It consumes existing structured outputs from trust and FDIR.

---

## Output of Posture Resolution

The allocator produces:

- dominant safety posture
- optional posture transition record
- contributing fault identifiers
- contributing trust record identifiers
- rationale summary
- active degradation flags passed through for downstream use

---

## Resolution Philosophy

### Rule 1 — Stronger containment posture wins
If multiple posture candidates exist, IX-Style chooses the strongest posture by
containment-oriented precedence.

### Rule 2 — Trust can drive posture
A bad trust state is not merely a note; it can become posture-driving.

### Rule 3 — Fault lifecycle matters
A contained or latched critical fault should influence posture more strongly than
a transient detected advisory condition.

### Rule 4 — Safe-hold is not casual
Safe-hold should be selected when containment-critical evidence justifies it,
not merely because one ordinary degradation exists.

### Rule 5 — Posture transitions deserve evidence
A change in dominant posture is itself a reviewable event.

---

## Baseline Posture Precedence

The executable baseline uses the same overall precedence already described in the
mode model:

1. `SAFE_HOLD`
2. `ASSURANCE_DEGRADED`
3. `POWER_DEGRADED`
4. `ACTUATION_DEGRADED`
5. `NAV_DEGRADED`
6. `SENSOR_DEGRADED`
7. `COMMS_DEGRADED`
8. `NOMINAL`

This is a containment-first ordering.

---

## Trust-to-Posture Mapping

### ASSURANCE_CONFIDENCE
States other than `TRUSTED` may drive:
- `ASSURANCE_DEGRADED`

### ACTUATOR_CONFIDENCE
States other than `TRUSTED` may drive:
- `ACTUATION_DEGRADED`

### NAVIGATION_TRUST
States other than `TRUSTED` may drive:
- `NAV_DEGRADED`

### SENSOR_SOURCE_TRUST / DERIVED_STATE_TRUST
States other than `TRUSTED` may drive:
- `SENSOR_DEGRADED`

### MESSAGE_TRUST / TIMING_TRUST
States other than `TRUSTED` may drive:
- `COMMS_DEGRADED`

This mapping exists because trust degradation should affect real behavior, not
just internal bookkeeping.

---

## Fault-to-Posture Mapping

### P1 containment-critical contained or latched fault
May drive:
- `SAFE_HOLD`

### ASSURANCE_FAULT
May drive:
- `ASSURANCE_DEGRADED`

### POWER_RESOURCE_FAULT
May drive:
- `POWER_DEGRADED`

### ACTUATION_FAULT
May drive:
- `ACTUATION_DEGRADED`

### NAVIGATION_TRUST_FAULT
May drive:
- `NAV_DEGRADED`

### SENSOR_FAULT
May drive:
- `SENSOR_DEGRADED`

### COMMUNICATION_FAULT
May drive:
- `COMMS_DEGRADED`

This is a baseline mapping, not a final platform-specific policy table.

---

## Flag-to-Posture Mapping

The allocator also uses important active degradation flags directly.

Examples:

- `assurance_guard_unhealthy` -> `ASSURANCE_DEGRADED`
- `power_margin_low` -> `POWER_DEGRADED`
- `actuator_response_uncertain` -> `ACTUATION_DEGRADED`
- `nav_spoof_suspected` or `nav_corroboration_lost` -> `NAV_DEGRADED`
- `sensor_trust_low` -> `SENSOR_DEGRADED`
- `comms_link_intermittent` or `command_freshness_low` -> `COMMS_DEGRADED`

Flags do not replace trust or fault reasoning.
They provide direct posture hints for downstream control.

---

## Safe-Hold Escalation Baseline

The executable baseline selects `SAFE_HOLD` when one or more of the following
are true:

- the base posture is already `SAFE_HOLD`
- a containment-critical fault is active in `CONTAINED` or `LATCHED`
- a multi-fault or assurance-related containment posture is already explicitly
  signaling safe-hold conditions

This is intentionally conservative.

---

## Posture Transition Record

When dominant posture changes, IX-Style produces a posture transition record.

The record should include:

- previous posture
- new posture
- transition time
- contributing fault IDs
- contributing trust record IDs
- cause codes
- rationale summary

This allows later review to answer:

- what changed
- what drove it
- whether the transition was justified

---

## Why Transition Records Matter

A posture transition is one of the most operator-relevant events in the system.

Without an explicit record, later review becomes guesswork:
- did the system silently narrow behavior
- which fault or trust collapse actually mattered
- when did the posture escalate
- was recovery or escalation justified

IX-Style should never make those questions hard to answer.

---

## Deferred Items

This commit intentionally does not yet add:

- numeric severity-to-posture tuning
- vehicle-specific posture tailoring
- richer multi-fault aggregation logic
- explicit safe-hold split between soft and hard safe-hold
- posture-specific substitute-action catalogs

Those belong in later commits.

---

## Completion Criteria

This posture-resolution layer is not mature until later commits allocate:

1. richer multi-fault escalation rules
2. more detailed recovery-to-posture relationships
3. explicit traceability records for posture-allocation rules
4. stronger scenario coverage for overlapping posture drivers
5. posture-aware telemetry compression policies
