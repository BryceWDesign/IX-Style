# IX-Style Fault Class Notes

## Purpose

This document gives short working notes for the baseline fault classes in
IX-Style so later detector, mitigation, and verification commits have a stable
reference.

---

## SENSOR_FAULT

A sensor fault is any condition in which a sensor or sensor-derived input is no
longer trustworthy enough for the functions depending on it.

Common signs:
- stale data
- drift
- disagreement with peer sources
- implausible jumps
- invalid timing

Typical responses:
- reduce dependent autonomy authority
- switch to corroborated sources where possible
- elevate evidence and operator visibility

---

## NAVIGATION_TRUST_FAULT

This class is used when navigation confidence is degraded, not merely when one
navigation sensor is noisy.

Common signs:
- position or state jump
- lost corroboration
- estimator conflict
- spoof-suspected pattern
- freshness failure

Typical responses:
- restrict nav-dependent action
- enter nav-degraded posture
- block risky recovery to full maneuver authority

---

## TIMING_FAULT

This class covers degraded timing assumptions that can poison trust even when
values look superficially normal.

Common signs:
- delayed monitor updates
- stale command path
- clock/timestamp inconsistency
- out-of-sequence evidence

Typical responses:
- reduce authority
- reject stale actions
- preserve timing-validity evidence

---

## COMMUNICATION_FAULT

This class covers degraded external command or supervisory links.

Common signs:
- link loss
- delay spike
- stale operator intent
- incomplete reconnect reconciliation

Typical responses:
- lost-link posture
- reject stale commands
- preserve reconciliation evidence

---

## POWER_RESOURCE_FAULT

This class covers degraded energy or resource margin that threatens continued
safe operation.

Common signs:
- low reserve
- brownout
- unsafe resource forecast
- incorrect load-shed priority consequence

Typical responses:
- preserve essential monitoring and containment functions
- reduce nonessential behavior
- bias toward survivability

---

## ACTUATION_FAULT

This class covers inability to trust that commanded control effect will occur as
expected.

Common signs:
- no response
- partial response
- lag
- mismatch between command and observed effect

Typical responses:
- clamp behavior
- reduce envelope
- escalate to safe-hold if control confidence keeps falling

---

## SOFTWARE_HEALTH_FAULT

This class covers unhealthy software behavior inside the control or monitoring
stack.

Common signs:
- watchdog or heartbeat failure
- stale internal state
- scheduler overrun
- failed internal consistency check

Typical responses:
- reduce authority
- isolate suspect function
- escalate if monitoring integrity is threatened

---

## ASSURANCE_FAULT

This class is special because it affects the very layer meant to keep the system
honest.

Common signs:
- guard loop unhealthy
- intervention path broken
- evidence path degraded
- monitor failure

Typical responses:
- aggressive authority reduction
- assurance-degraded posture
- safe-hold bias

---

## POLICY_AUTHORITY_FAULT

This class covers prohibited or ambiguous command/control situations.

Common signs:
- invalid override attempt
- source not authorized
- unsafe recovery request
- conflicting authority claim

Typical responses:
- reject or freeze
- preserve evidence
- latch if repeated or severe

---

## EVIDENCE_FAULT

This class covers failure of the review trail needed for post-event trust.

Common signs:
- missing evidence record
- append-only failure
- incomplete rationale
- broken ordering

Typical responses:
- reduce assurance confidence
- preserve minimal emergency record path
- potentially elevate to assurance fault if severe

---

## MULTI_FAULT_COMPOUND

This class is used when the interaction among multiple faults is the real risk.

Common signs:
- benign-looking faults whose combined effect is dangerous
- mitigation conflict
- posture oscillation
- simultaneous authority and trust collapse

Typical responses:
- prioritize containment
- resolve mitigation conflicts deterministically
- generate explicit compound-fault evidence

