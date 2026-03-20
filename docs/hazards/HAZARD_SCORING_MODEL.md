# IX-Style Hazard Scoring Model

## Purpose

This document defines the preliminary scoring model used in IX-Style to discuss
risk posture before any vehicle-specific certification tailoring exists.

The model is intentionally simple and traceability-friendly.

It exists to support:

- triage of hazard attention
- monitor allocation
- degraded-mode allocation
- verification prioritization

It does **not** replace a program-specific safety analysis method.

---

## Scoring Dimensions

IX-Style uses four dimensions for early architectural triage.

### 1. Severity

How bad is the outcome if the hazard is realized and not contained?

- **4 — Catastrophic**
- **3 — Critical**
- **2 — Major**
- **1 — Minor**

### 2. Detectability Difficulty

How difficult is it to detect the problem correctly and in time?

- **4 — Very hard to detect before harm**
- **3 — Hard**
- **2 — Moderate**
- **1 — Easy**

### 3. Control Dependency

How strongly does safe containment depend on successful control, arbitration, or
runtime-assurance intervention?

- **4 — Immediate active intervention required**
- **3 — Strong dependence on timely intervention**
- **2 — Partial dependence**
- **1 — Limited control dependence**

### 4. Evidence Criticality

How important is high-quality evidence capture to safe review, operator trust,
or post-event reconstruction of this hazard?

- **4 — Essential**
- **3 — High**
- **2 — Useful**
- **1 — Limited**

---

## Preliminary Priority Heuristic

IX-Style will use the following rough triage heuristic until a later, more
formal risk matrix is introduced.

### Priority A
Hazards with:
- Severity 4, or
- Severity 3 plus Detectability Difficulty 3 or 4, or
- Severity 3 plus Control Dependency 4

These hazards must receive direct monitor, mitigation, and verification
attention early.

### Priority B
Hazards with:
- Severity 3 and moderate detectability/control complexity, or
- Severity 2 but high evidence criticality and strong operational consequence

These hazards must receive architecture coverage and later verification.

### Priority C
Hazards with:
- Severity 1 or 2 and low complexity, where bounded containment is easier

These hazards still matter, but they should not steal attention from Priority A.

---

## Working Rules

1. A hazard with weak detectability should not be hand-waved because its
   initiating event seems rare.

2. If safe containment depends heavily on runtime assurance, the hazard must
   drive guard design and timing verification.

3. If evidence quality is essential to understanding the event, then evidence
   design is part of the safety response, not a logging convenience.

4. Hazards involving authority ambiguity are automatically treated as elevated
   concern because they create operator confusion and unsafe behavior races.

5. Concurrent-fault scenarios should be treated as more serious than the sum of
   their individual parts when mitigations can conflict.

---

## Initial High-Priority Hazard Families

The following hazard families should be treated as early Priority A candidates in
IX-Style:

- sensor trust collapse
- estimator divergence
- navigation trust degradation
- runtime-assurance intervention failure
- unsafe authority arbitration
- power/resource degradation that disables safety functions
- unnoticed failure of the assurance layer itself

---

## Planned Future Extension

A later commit should replace or extend this simple model with:

- monitor coverage mapping
- mode allocation mapping
- verification-scenario mapping
- pass/fail evidence expectations
- optional platform-tailoring notes
