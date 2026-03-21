# IX-Style Review Walkthrough

## Document ID

IXS-REVIEW-WALKTHROUGH

## Status

Draft review baseline.

## Purpose

This document gives a reviewer a practical walkthrough for inspecting one
IX-Style scenario result or exported review-artifact package.

It exists because review quality drops fast when a repo has strong internals but
no clear inspection order.

---

## Review Goal

A good IX-Style review should answer five questions quickly:

1. what scenario was executed
2. what dominant posture resulted
3. what happened to the candidate command
4. why did the system choose that outcome
5. can the evidence chain be trusted as untampered

---

## Best Review Order

When reviewing one exported package, open files in this order:

1. `manifest.json`
2. `operator_safety_summary.json`
3. `mission_health_snapshot.json`
4. `decision_receipt.json`
5. `evidence_package.json`
6. `evidence_bundle.json`
7. `verification_result.json`

This order is intentional.
It moves from human summary toward machine detail.

---

## Step 1 — Manifest

Open `manifest.json` first.

Confirm:

- scenario ID
- scenario name
- passed status
- final outcome
- dominant safety posture
- list of files present

If the manifest already looks inconsistent with the scenario purpose, the review
has found a serious problem early.

---

## Step 2 — Operator Safety Summary

Open `operator_safety_summary.json`.

Look at:

- headline
- decision rationale
- operational why
- authority statement
- recovery statement
- operator focus
- timeline markers
- review significance

This file tells you whether IX-Style can explain itself to a human without
making them reverse-engineer the whole state machine.

---

## Step 3 — Mission Health Snapshot

Open `mission_health_snapshot.json`.

Confirm:

- mission phase
- dominant safety posture
- containment status
- review significance
- authority summary
- trust summary
- active fault summary
- recovery summary
- recent events

This file tells you the current operational picture the system claims to be in.

---

## Step 4 — Decision Receipt

Open `decision_receipt.json`.

Confirm:

- decision ID
- candidate action summary
- final outcome
- final authoritative source
- safety posture
- triggered constraint IDs
- recovery-gate result
- rationale summary
- command delta

This is the main answer to:
> what happened to the command and why

If this file is weak, IX-Style is weak no matter how many other artifacts exist.

---

## Step 5 — Evidence Package

Open `evidence_package.json`.

Confirm:

- generated event IDs
- expected outcomes
- actual observed outcomes
- trust transitions
- fault transitions
- mode transitions
- pass/fail result

This is where you see whether the scenario produced the expected supporting
evidence around the main decision.

---

## Step 6 — Evidence Bundle

Open `evidence_bundle.json`.

Confirm:

- bundle ID
- head chain hash
- item count
- ordered bundle items
- presence of decision receipt and transition items

This file exists to answer:
> can the evidence be checked for tampering or silent rewriting

The bundle should not be treated as decorative.

---

## Step 7 — Verification Result

Open `verification_result.json`.

Confirm:

- scenario passed
- derived active degradation flags
- derived dominant safety posture
- pipeline trace

The pipeline trace is especially useful because it shows whether:

- recovery gate ran
- authority evaluation ran
- guard evaluation ran

This is one of the cleanest ways to inspect control progression.

---

## What to Cross-Check

A strong review cross-checks these links:

### Operator summary vs mission health
The headline and operator focus should match the dominant posture.

### Mission health vs decision receipt
The dominant posture and authority picture should match the decision outcome.

### Decision receipt vs evidence package
Triggered constraints, related faults, and posture drivers should align with the
events produced.

### Evidence package vs evidence bundle
The evidence bundle should contain the core review items without tamper errors.

### Verification result vs invariants
The pipeline trace should make the invariant outcomes believable.

---

## Red Flags

A reviewer should treat the following as serious red flags:

- operator summary says one thing while mission health says another
- decision receipt rationale is vague or empty
- recovery action shows `NOT_APPLICABLE` for recovery-gate result
- dominant posture changed with no mode transition record
- evidence bundle fails validation
- pipeline trace says authority or guard ran after blocked recovery
- recent events do not support the claimed posture

These are not cosmetic issues.
They go straight to credibility.

---

## What a Good Package Feels Like

A good IX-Style review package should feel like:

- the command outcome is clear
- the driving posture is clear
- the fault/trust story is visible
- the authority story is visible
- the recovery story is visible
- the evidence can be checked for tampering

That is the target.

---

## Current Baseline Review Scenarios

The current repo baseline is especially easy to review through:

### Power fault clamp
Look for:
- `POWER_DEGRADED`
- clamp outcome
- resource-related operator focus
- evidence bundle with fault transition

### Navigation spoof transition
Look for:
- `NAV_DEGRADED`
- navigation-trust-driven posture
- trust transition evidence
- mode transition evidence

### Recovery deferred over weak comms
Look for:
- deferred outcome
- explicit recovery-gate result
- no authority or guard progression after deferral
- operator statement reflecting weak remote trust

---

## Reviewer Exit Criteria

A reviewer should be able to finish with confidence that they can answer:

1. what happened
2. why it happened
3. what posture dominated
4. whether recovery was relevant
5. whether the evidence package still verifies cleanly

If those are answerable, the review walkthrough succeeded.
