# IX-Style Operator Rationale and Safety Summary Layer

## Document ID

IXS-OPERATOR-RATIONALE-AND-SUMMARY-LAYER

## Status

Draft operations baseline.

## Purpose

This document defines the operator-facing rationale and concise safety-summary
layer for IX-Style.

It exists to answer the question:

> Once the system has already performed trust evaluation, fault handling, mode
> allocation, authority decisions, guard intervention, and evidence generation,
> how does it explain the situation to a human in a compact way that is useful
> under stress?

This matters because a system can have strong internals and still fail the human
interface if it speaks in raw fields, enum names, and scattered event fragments.

---

## Core Principle

IX-Style operator narration is derived from structured truth.

That means the summary layer must not invent reasons or smooth over ambiguity.
It should compress what the system already knows into a concise operational
message.

The narration layer should help an operator answer:

- what posture are we in
- why are we in it
- who currently has effective authority
- is recovery blocked, deferred, or not relevant
- what should the operator focus on next

---

## Why This Layer Exists

Mission-health snapshots are structured and machine-friendly.
Decision receipts are explanatory and auditable.

But operators still need a concise summary that can be read quickly.

Without a dedicated narration layer, they are forced to infer meaning from:

- posture enums
- review-significance labels
- fault IDs
- trust IDs
- command delta fields
- recovery gate fields

That is too much mental translation under stress.

---

## Inputs to the Summary Layer

The baseline executable narration layer uses:

- mission-health snapshot
- decision receipt
- recent event summaries
- review significance
- trust summary
- authority summary
- recovery summary

It does not bypass the structured system state.
It compresses it.

---

## Output of the Summary Layer

The baseline executable summary produces:

- headline
- decision rationale sentence
- operational why sentence
- authority statement
- recovery statement
- operator focus statement
- concise narrative paragraph
- timeline markers
- review significance

This is meant to be compact enough for operator surfaces and simulations while
still remaining grounded.

---

## Design Rules

### Rule 1 — Stay faithful to evidence
The narration must remain grounded in the actual receipt and snapshot state.

### Rule 2 — Prefer stable wording
Aerospace review audiences dislike cute phrasing in safety-critical contexts.

### Rule 3 — Say what changed
If authority narrowed, recovery deferred, or containment escalated, the summary
should say so plainly.

### Rule 4 — Make the next focus obvious
A good summary should leave the operator knowing what to pay attention to next.

### Rule 5 — Avoid fake certainty
If recovery is blocked or deferred, the summary should say that directly.

---

## Baseline Headline Mapping

The executable baseline uses these headline patterns:

- `SAFE_HOLD` -> `SAFE HOLD ACTIVE`
- `ASSURANCE_DEGRADED` -> `ASSURANCE DEGRADED`
- `POWER_DEGRADED` -> `POWER DEGRADED`
- `ACTUATION_DEGRADED` -> `ACTUATION DEGRADED`
- `NAV_DEGRADED` -> `NAVIGATION DEGRADED`
- `SENSOR_DEGRADED` -> `SENSOR DEGRADED`
- `COMMS_DEGRADED` -> `COMMUNICATIONS DEGRADED`
- `NOMINAL` -> `NOMINAL BOUNDED OPERATION`
- `INITIALIZING` -> `INITIALIZING`

---

## Decision Rationale Intent

The decision rationale should summarize what the system just did.

Examples:
- command was clamped due to resource margin degradation
- recovery was deferred because comms freshness remained weak
- movement command was vetoed because navigation was spoof-suspected

This is not meant to repeat every field.
It is meant to answer:
> What happened to the candidate action?

---

## Operational Why Intent

The operational why statement should summarize what is driving the posture.

Examples:
- posture is being driven by navigation trust collapse
- highest active fault priority remains containment critical
- power protection is actively shedding nonessential behavior

This is meant to answer:
> Why is the system in this posture?

---

## Authority Intent

The authority statement should summarize:

- dominant authoritative source
- safety-supervisor bias
- remote operator command status

This is meant to answer:
> Who currently matters in the loop?

---

## Recovery Intent

The recovery statement should summarize the recovery state cleanly.

Examples:
- recovery expansion is blocked
- recovery qualification is under review
- recovery expansion is not currently relevant

This is meant to answer:
> Can we restore more authority yet?

---

## Operator Focus Intent

The operator focus statement should tell the operator what matters next.

Examples:
- preserve essential functions before resuming mission progress
- avoid nav-dependent maneuver expansion until trust is restored
- do not rely on weak remote intent until comms freshness is healthy

This is guidance, not policy override.

---

## Timeline Markers

The baseline summary may include a few recent event summaries as timeline markers.
These are intentionally short and should help the operator see the recent chain
of relevant changes without dumping the full event stream.

---

## Deferred Items

This commit intentionally does not yet add:

- voice-oriented phrasing variants
- alert-priority sound mapping
- platform-specific phrasing policies
- multilingual output
- adaptive verbosity based on operator role

Those belong in later commits if needed.

---

## Completion Criteria

This summary layer is not mature until later commits allocate:

1. more scenario coverage across posture types
2. optional formatting profiles by operator role
3. richer linkage to future UI surfaces
4. longer-form drilldown narratives
