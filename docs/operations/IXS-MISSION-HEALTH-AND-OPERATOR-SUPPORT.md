# IX-Style Mission Health and Operator Decision-Support Architecture

## Document ID

IXS-MISSION-HEALTH-AND-OPERATOR-SUPPORT

## Status

Draft architecture baseline.

## Purpose

This document defines the mission-health and operator decision-support model for
IX-Style.

It exists to answer the following questions:

- what operational picture should IX-Style expose to a human operator
- how should active faults, trust posture, mode state, and authority state be
  summarized without burying what matters
- what event stream should be preserved for near-real-time review
- how should the system explain why it rejected, clamped, substituted, or froze
  a command
- how should delayed-link and intermittent-link operation affect operator views

This document is necessary because a system can have good autonomy logic and
still fail operationally if the human-facing picture is misleading, noisy, or
late in the wrong ways.

---

## Core Principle

IX-Style operator support is not a cosmetic dashboard layer.

It is part of the safety architecture.

A serious operator view must help a human answer, quickly and correctly:

1. what posture is the system in
2. what changed recently
3. what is trusted and what is not
4. what faults are active
5. who currently has effective authority
6. what the system is blocking or narrowing
7. whether recovery is possible, blocked, or unsafe right now

If the operator cannot answer those questions, the architecture is not done.

---

## Mission Health Definition

Mission health in IX-Style is a compact operational picture of the system’s
current safety-relevant condition.

Mission health is not the same as raw telemetry.

Mission health should summarize:

- mission phase
- dominant safety posture
- active degradation flags
- active high-priority faults
- trust posture summary
- current authority posture
- current guard/intervention posture
- current recovery posture
- resource posture
- recent safety-relevant event activity

Mission health is intended to support both:
- live supervision
- post-event reconstruction

---

## Operator Support Objectives

IX-Style operator support shall aim to:

1. make active hazards obvious
2. make containment posture obvious
3. make command authority obvious
4. make recent safety-relevant changes obvious
5. make trust degradation visible without drowning the operator in raw checks
6. explain blocked or modified actions clearly enough for action review
7. preserve enough context to support delayed review after intermittent links
8. separate safety-critical status from background noise

---

## Human Factors Posture

IX-Style assumes that under stress:

- operators have limited time
- operators may be on delayed or intermittent links
- operators may see incomplete history unless the system preserves summaries well
- operators should not need to reverse-engineer the autonomy stack from raw logs

Therefore IX-Style favors:

- prioritized summaries
- stateful event feeds
- compact rationale messages
- explicit authority presentation
- clear blocked/recovery status
- stable labels over clever wording

---

## Mission Health Layers

The IX-Style operator picture is organized into five layers.

### Layer 1 — Topline Safety Summary
The smallest, highest-priority summary.

It should show at minimum:
- mission phase
- dominant safety posture
- authority state
- containment status
- recovery status
- most severe active fault priority
- current review-significance level

This layer answers:
> Are we okay, degraded, or containing something serious right now?

---

### Layer 2 — Trust and Fault Summary
The next layer down.

It should show:
- navigation trust summary
- sensor trust summary
- timing trust summary
- actuator confidence summary
- assurance confidence summary
- count and identities of active important faults
- recent trust transitions

This layer answers:
> What part of the machine do we currently not trust?

---

### Layer 3 — Authority and Control Summary
This layer explains who currently matters in the control loop.

It should show:
- current authoritative source by function class where relevant
- currently frozen or restricted command paths
- policy override status
- stale-command rejection status
- recovery-gate status
- current guard intervention bias if non-nominal

This layer answers:
> Who is actually in charge right now, and what paths are blocked?

---

### Layer 4 — Resource and Survivability Summary
This layer shows whether survivability constraints are driving behavior.

It should show:
- power/resource posture
- essential-function preservation status
- load-shed or resource-clamp status
- safe-hold support capability
- any active survivability bias affecting decisions

This layer answers:
> Are we restricting behavior to survive rather than to progress mission goals?

---

### Layer 5 — Safety Event Stream
A compact rolling stream of safety-relevant transitions.

It should include:
- mode transitions
- trust transitions
- fault lifecycle changes
- command arbitration outcomes
- guard interventions
- recovery gate results
- operator override attempts and results
- link reconciliation events

This layer answers:
> What just happened, in what order, and why?

---

## Topline Mission Health Fields

A baseline mission-health snapshot should include:

- snapshot identifier
- snapshot time
- mission phase
- dominant safety posture
- containment status
- current review significance
- authority summary
- trust summary
- active fault summary
- recovery summary
- resource summary
- recent critical event count
- delayed-link indicator if applicable

These fields are compact by design.

---

## Containment Status Model

IX-Style separates containment posture from simple mode naming.

Baseline containment states:

- `CONTAINMENT_NONE`
- `CONTAINMENT_ELEVATED`
- `CONTAINMENT_ACTIVE`
- `CONTAINMENT_LOCKED`

### CONTAINMENT_NONE
No active containment bias beyond standard runtime assurance.

### CONTAINMENT_ELEVATED
Containment bias is increasing due to degradation or rising risk.

### CONTAINMENT_ACTIVE
The system is actively holding to bounded degraded or safe-hold behavior.

### CONTAINMENT_LOCKED
The system is in a deliberately sticky containment condition where authority
expansion is blocked pending explicit recovery qualification.

This helps operators understand the seriousness of the posture without needing
to infer it from one mode label alone.

---

## Recovery Status Model

Operators must know not only whether a fault seems better, but whether the
system is actually allowed to restore capability.

Baseline recovery states:

- `RECOVERY_NOT_APPLICABLE`
- `RECOVERY_BLOCKED`
- `RECOVERY_PENDING_EVIDENCE`
- `RECOVERY_UNDER_REVIEW`
- `RECOVERY_QUALIFIED`
- `RECOVERY_EXECUTED`

### Why this matters

A system may look healthier than it did 30 seconds ago but still be blocked
from returning to nominal due to:
- insufficient persistence
- missing corroboration
- active higher-priority fault
- degraded assurance confidence
- policy lockout

The operator must see that distinction clearly.

---

## Authority Summary Model

The mission-health view must summarize authority in plain operational terms.

At minimum, the operator should be able to see:

- current dominant authoritative source
- whether nominal autonomy is narrowed
- whether contingency logic is active
- whether safety supervisor intervention bias is elevated
- whether remote operator commands are being accepted, deferred, or rejected
- whether any command paths are frozen

Authority ambiguity is one of the easiest ways to confuse an operator.
IX-Style should therefore prefer an explicit summary like:

- `authority: safety_supervisor_constrained_nominal_autonomy`
- `remote_operator_control: stale_rejected`
- `recovery_actions: blocked_pending_gate`

That is more useful than vague green/yellow indicators.

---

## Trust Summary Model

The trust summary should compress domain-specific trust into operator-usable
signals without losing the ability to drill deeper.

Minimum trust summary domains:

- navigation trust
- sensor-source aggregate trust
- derived-state trust
- timing trust
- actuator confidence
- assurance confidence
- message/control-plane trust

Each domain should expose:
- current state
- recent trend
- last transition cause if significant
- whether the trust issue is posture-driving

This lets the operator separate:
- background degradation
from
- the specific trust problem driving containment

---

## Active Fault Summary Model

The operator support layer shall distinguish between:

- active high-priority faults
- active lower-priority bounded faults
- latched blocking faults
- recent cleared important faults

The summary should not be a wall of fault codes.

Instead it should prioritize:
- highest priority
- containment relevance
- authority relevance
- trust relevance
- recovery relevance

Example summary fields:
- highest_active_fault_priority
- active_fault_count
- blocking_latched_fault_count
- top_fault_ids
- mitigation_in_progress
- mitigation_failure_flag

---

## Safety Event Stream Requirements

IX-Style requires a compact safety-relevant event stream.

The safety event stream is not raw telemetry.
It is an ordered operational narrative.

Each event should include at minimum:
- event identifier
- event time
- event class
- event type
- review significance
- short summary
- affected scope
- related fault IDs if present
- related trust IDs if present
- resulting safety posture
- resulting authority implication if relevant
- evidence linkage if available

### Event stream design goals

1. compact enough to scan quickly
2. structured enough for machine tooling
3. causally linkable to detailed evidence
4. stable under delayed-link operation
5. prioritized so the operator sees what matters first

---

## Event Prioritization Rules

Events should be prioritized using a significance-first approach.

Baseline priorities:

### CRITICAL
Use for:
- safe-hold entry
- containment lock
- assurance-path collapse
- rejected or frozen recovery during serious degradation
- multi-fault escalation threatening containment

### HIGH
Use for:
- dominant posture change
- nav trust collapse
- actuator confidence collapse
- high-priority fault confirmation
- policy override denial in degraded state

### IMPORTANT
Use for:
- clamp/substitute interventions
- degraded trust transition
- comms reconciliation result
- mitigation start or failure
- recovery gate pass/fail

### ROUTINE
Use for:
- bounded advisory posture update
- non-posture-driving local degradation
- informational evidence generation markers

---

## Operator Rationale Requirements

Whenever IX-Style changes or denies behavior in a safety-relevant way, the
operator should be given a compact rationale summary.

A good rationale summary answers:

- what changed
- why it changed
- what the new limitation is
- what would need to improve for restoration

Examples:

- `nav trust collapsed due to continuity break and corroboration loss; movement authority narrowed`
- `remote recovery request deferred; assurance confidence remains degraded`
- `resource posture low; nonessential maneuver rejected to preserve safe-hold capability`

This is far better than:
- `error 42`
- `request invalid`
- `system unsafe`

---

## Delayed-Link and Intermittent-Link Support

IX-Style assumes links may be delayed or intermittent.

Therefore operator support shall preserve:

- snapshot sequence continuity
- event ordering continuity
- reconciliation events after reconnect
- explicit stale-data indication on received views
- last confirmed authority state before link loss
- no silent overwriting of prior critical decisions

A reconnecting operator should be able to see:
- what happened while disconnected
- what posture the system entered
- whether commands were rejected while stale
- what the current recovery posture is

---

## Recommended Operator View Layout

This repository does not lock a UI design, but it does recommend a structured
presentation order.

### Recommended order

1. safety posture banner
2. containment and recovery status
3. authority summary
4. trust summary
5. active high-priority faults
6. current mitigation summary
7. recent safety event stream
8. drill-down to detailed evidence receipts

This order is intentional.
It puts “what matters now” before “what happened eventually in detail.”

---

## Mission Health Non-Negotiables

IX-Style mission health and operator support are not complete unless:

1. dominant safety posture is obvious
2. current authority state is obvious
3. trust degradation is visible in compact form
4. active high-priority faults are obvious
5. containment and recovery status are explicit
6. recent safety-relevant events are preserved in ordered form
7. rationale summaries explain blocked or modified actions
8. delayed-link operation does not silently confuse history

---

## Deferred Items

This commit intentionally does not yet finalize:

- specific UI implementation
- color usage or visual design tokens
- exact dashboard transport
- exact screen layouts by vehicle type
- alert sound or attention management
- exact aggregation windows for summary compression

Those belong in later commits or UI-specific work.

---

## Completion Criteria

This mission-health architecture is not mature until later commits allocate:

1. concrete mission-health snapshot schema
2. concrete safety event schema
3. reference code scaffolding for snapshot generation
4. reference code scaffolding for event prioritization
5. verification scenarios covering operator-visible transitions
6. sample simulated outputs showing degraded and containment cases
