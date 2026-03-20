# IX-Style Fault Injection Campaign Plan

## Purpose

This document defines the baseline campaign structure for fault injection in
IX-Style.

It does not yet implement the harness.
It defines what the harness must challenge.

---

## Campaign Goals

The campaign exists to prove that IX-Style:

- detects important abnormal conditions
- moves faults through meaningful lifecycle states
- narrows authority when trust weakens
- intervenes before unsafe execution
- enters degraded posture or safe-hold when required
- preserves decision and event evidence even under stress
- blocks premature recovery

---

## Campaign Structure

Each campaign scenario should define:

- scenario ID
- scenario family
- injected condition(s)
- initial posture
- expected trust changes
- expected fault lifecycle changes
- expected authority effects
- expected mode effects
- expected evidence artifacts
- forbidden outcomes

---

## Seed Scenario List

### TEST-TRUST-001 — Stale critical sensor input
**Family**
TRUST_SCENARIO

**Injected conditions**
- critical sensor updates stop
- value remains numerically plausible but freshness fails

**Expected behavior**
- trust drops based on freshness
- dependent functions narrow
- no silent acceptance of stale value as current truth

**Expected evidence**
- trust transition event
- decision receipt if affected control request occurs

**Forbidden outcomes**
- source remains effectively trusted for critical control use

---

### TEST-TRUST-004 — Navigation continuity break with corroboration loss
**Family**
TRUST_SCENARIO

**Injected conditions**
- position/state jump
- independent corroboration lost
- estimator/nav disagreement increases

**Expected behavior**
- nav trust drops sharply
- nav-dependent authority narrows
- dominant posture likely becomes NAV_DEGRADED or stronger

**Expected evidence**
- trust event
- mode transition event
- decision receipt for any blocked/clamped movement request

**Forbidden outcomes**
- aggressive nav-dependent action proceeds as normal

---

### TEST-AUTH-003 — Unsafe nominal autonomy actuation request
**Family**
GUARD_SCENARIO

**Injected conditions**
- nominal autonomy proposes action exceeding active envelope

**Expected behavior**
- guard vetoes, clamps, or substitutes
- final authoritative source reflects safety supervisor involvement
- receipt explains triggered constraints

**Expected evidence**
- decision receipt
- optional intervention receipt

**Forbidden outcomes**
- raw unsafe command reaches allowed execution path

---

### TEST-AUTH-005 — Out-of-sequence or replay-suspected remote command
**Family**
AUTHORITY_SCENARIO

**Injected conditions**
- delayed or replay-suspected remote operator control message

**Expected behavior**
- message is rejected, deferred, or quarantined
- stale remote intent does not gain authority
- comms posture may influence handling

**Expected evidence**
- arbitration receipt
- event stream item for rejection/defer result

**Forbidden outcomes**
- stale message becomes current authoritative control

---

### TEST-RESOURCE-001 — Resource margin collapse
**Family**
RESOURCE_SCENARIO

**Injected conditions**
- low power/resource threshold crossed
- nonessential and essential functions both active

**Expected behavior**
- system preserves essential monitoring and containment functions
- high-cost nonessential behavior is rejected or clamped
- posture becomes POWER_DEGRADED or SAFE_HOLD if needed

**Expected evidence**
- mode transition event
- decision receipt for rejected resource-costly action
- mission-health snapshot showing survivability bias

**Forbidden outcomes**
- essential safety support degrades before nonessential mission behavior

---

### TEST-ASSURANCE-003 — Evidence path degradation during serious event
**Family**
EVIDENCE_SCENARIO

**Injected conditions**
- evidence sink becomes degraded during active intervention sequence

**Expected behavior**
- assurance confidence degrades
- authority narrows
- system preserves minimal critical review path if possible
- containment bias increases

**Expected evidence**
- evidence-path health event
- posture change if triggered
- explicit rationale showing evidence weakness affected assurance posture

**Forbidden outcomes**
- system continues full-risk behavior as though assurance remained strong

---

### TEST-RECOVERY-002 — Recovery request while trust persistence incomplete
**Family**
RECOVERY_SCENARIO

**Injected conditions**
- degraded trust condition appears improved for only a short interval
- recovery request is issued

**Expected behavior**
- recovery gate blocks restoration
- no silent return to nominal
- rationale explains persistence/corroboration shortfall

**Expected evidence**
- recovery receipt
- decision receipt or mode event if applicable

**Forbidden outcomes**
- direct return to full authority after one apparently healthy sample

---

### TEST-MULTI-002 — Concurrent actuation degradation and low-resource posture
**Family**
MULTI_FAULT_SCENARIO

**Injected conditions**
- actuator response uncertainty rises
- resource margin simultaneously low

**Expected behavior**
- mitigation conflict is resolved deterministically
- maneuver authority narrows
- survivability and containment bias dominate mission progress
- posture may escalate beyond one simple degraded flag

**Expected evidence**
- fault events for both conditions
- decision receipt for constrained action
- mission-health snapshot reflecting multi-fault reality

**Forbidden outcomes**
- contradictory mitigations or ambiguous authority outcome

---

## Forbidden Outcome Classes

Across the campaign, the following outcome classes should be treated as serious failures:

- unsafe command bypass
- stale authority acceptance
- silent authority restoration
- missing critical evidence
- ambiguous control source
- containment escalation missing when required
- evidence ordering corruption during critical scenario
- assurance degradation ignored

---

## Campaign Maturity Ladder

Campaign maturity should progress in this order:

1. scenario definitions exist
2. expected outcomes documented
3. traceability links defined
4. simulation harness executes scenario
5. evidence package captured
6. pass/fail judgment recorded
7. repeated automated execution possible
8. stressed timing or HIL-oriented variant added

This keeps the repo honest about what is designed versus what is executed.

---

## Notes

The fault-injection campaign is one of the clearest ways IX-Style can separate
itself from "nice concept" repos.

It forces the architecture to prove that degradation logic is real.
