# IX-Style Glossary

## Purpose

This glossary fixes working definitions for IX-Style so later documents use the
same language consistently.

---

## Terms

### assured autonomy
Autonomy that is bounded by explicit safety structure, monitor logic, authority
control, and reviewable evidence rather than being trusted as an opaque actor.

### autonomy boundary
The explicit limit beyond which nominal autonomy is not allowed to directly
control a safety-relevant function without passing through additional checks.

### authority state
The current description of who or what is allowed to influence a controlled
function.

### command source
An origin of commands or intent, such as operator input, mission logic, nominal
autonomy, safety supervisor, or contingency logic.

### confidence posture
The current trust state of the system with respect to data validity, timing,
message integrity, estimator consistency, subsystem health, and control
authority.

### contingency logic
Deterministic logic responsible for entering or supporting a fallback path when
nominal operation is no longer acceptable.

### degraded mode
A reduced-authority operating state entered to preserve safety or controllability
when confidence, resources, or subsystem capability decline.

### deterministic
Predictable in structure and intended behavior, with explicitly defined outcomes
for relevant inputs and conditions.

### evidence record
A machine-readable record that captures why a safety-relevant decision, veto,
mode change, override, or mitigation occurred.

### fault
A defect, failure, inconsistency, or abnormal condition that can degrade trust,
capability, or safety posture.

### FDIR
Fault detection, isolation, and recovery. In IX-Style this also includes safe
containment when full recovery is unavailable or undesirable.

### isolation reasoning
The process of narrowing likely fault origin or class based on available
symptoms, trust relationships, and consistency checks.

### latched fault
A fault state that remains active until explicitly cleared under allowed policy
conditions, even if the immediate trigger disappears.

### mission health
A compact operational picture of current system mode, authority, confidence,
active faults, mitigation status, and resource posture.

### nominal autonomy
The non-safety-supervisory autonomy logic responsible for mission progress,
planning, or vehicle behavior within allowed bounds.

### operator
A human user or supervising control function external to the autonomy runtime.

### policy
A defined rule set governing authority, permitted transitions, intervention
thresholds, reset conditions, or acceptable operating posture.

### replay-aware
Able to detect or limit the effect of repeated or out-of-sequence safety-relevant
messages or events.

### runtime assurance
A supervisory function that monitors active behavior against safety constraints
and intervenes when nominal logic would exceed allowed bounds.

### safe-hold
A containment-oriented state intended to preserve control, stability, or mission
survivability while higher-function autonomy is reduced or suspended.

### safety-relevant
Any decision, state, message, event, or action that can materially affect safe
operation, authority, or containment posture.

### sensor trust
An explicit representation of how much the system currently trusts one or more
input sources based on freshness, plausibility, consistency, timing, and related
checks.

### state estimator
A function that produces system state estimates from one or more measurements,
models, and assumptions.

### subsystem self-report inconsistency
A condition in which a subsystem’s claimed state, health, or behavior conflicts
with external observations, timing expectations, or corroborating data.

### tamper-evident
Structured so that unauthorized modification of important records becomes
detectable.

### traceability
The ability to connect a requirement to hazards, design elements, tests, and
evidence artifacts.

### veto
A supervisory rejection of a candidate action before it is allowed to affect a
controlled function.
