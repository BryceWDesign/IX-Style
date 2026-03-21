# IX-Style Invariant Checks and Property Layer

## Document ID

IXS-INVARIANT-CHECKS-AND-PROPERTY-LAYER

## Status

Draft verification baseline.

## Purpose

This document defines the executable invariant-check layer for IX-Style.

It exists to answer the question:

> Beyond scenario-specific expected outcomes, what architecture truths are
> automatically checked every time a result is produced?

This matters because a serious assured-autonomy repo should not rely only on
example-by-example judgment.
It should also enforce a set of always-important truths.

---

## Core Principle

An invariant is a condition that should remain true whenever the relevant part
of the architecture is exercised.

IX-Style invariants are grounded in the current executable baseline.
They are not aspirational claims beyond what the repo can honestly evaluate yet.

---

## Why This Layer Exists

Scenarios answer:
- what happened in this case

Invariants answer:
- did we violate a system truth we said we care about

This layer helps IX-Style prove its non-negotiables more consistently.

---

## Baseline Executable Invariants

The current executable layer checks the following baseline invariants.

### IXS-INV-001 — Recovery gate blocks before authority progression
If recovery gate status is `FAILED` or `DEFERRED`, authority evaluation and guard
evaluation must not proceed.

### IXS-INV-002 — Authority-accepted commands reach guard evaluation
If a candidate command passes recovery gating and authority returns `ACCEPT`,
guard evaluation must occur.

### IXS-INV-003 — Recovery actions must carry explicit recovery-gate evidence
If the requested function class is `RECOVERY_ACTION`, the decision receipt must
not report `NOT_APPLICABLE` for recovery-gate status.

### IXS-INV-004 — Dominant posture changes must emit a mode transition record
If the resolved dominant posture differs from the scenario base posture, the
evidence package must contain at least one mode transition record.

### IXS-INV-005 — Decision receipts must carry required explanatory fields
At minimum the receipt must carry:
- decision ID
- final outcome
- rationale summary
- recovery-gate result
- candidate action summary

### IXS-INV-006 — Evidence bundles must validate cleanly
If an evidence bundle is exported, its hash chain must validate without errors.

These are baseline executable invariants, not the final full set.

---

## Property-Style Checking Intent

The current repo uses deterministic property-style checking over generated
scenario results.

That means the invariant layer checks properties of the result such as:

- whether certain stages were skipped or executed
- whether required evidence exists
- whether bundle integrity still holds
- whether posture transitions are visible when required

This is lighter-weight than a full theorem prover, but still materially useful.

---

## Why This Matters

A reviewer can now ask:

- did recovery stop before authority when it should
- did accepted commands always reach the guard
- did posture escalation create explicit evidence
- did the evidence bundle remain tamper-evident

And IX-Style can answer those questions automatically for executed scenarios.

---

## Deferred Items

This commit intentionally does not yet add:

- randomized fuzz/property generation
- symbolic execution
- formal proof tooling
- invariant coverage metrics
- cross-package review diffs based on invariants

Those belong in later commits if needed.

---

## Completion Criteria

This invariant layer is not mature until later commits allocate:

1. broader invariant coverage
2. more recovery-specific invariant families
3. more message-ordering and replay invariants
4. batch invariant reporting across larger scenario suites
5. stronger property-style stress generation
