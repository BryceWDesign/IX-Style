# IX-Style Developer Onboarding and Quickstart

## Document ID

IXS-DEVELOPER-ONBOARDING-AND-QUICKSTART

## Status

Draft developer baseline.

## Purpose

This document gives a new engineer a fast, accurate path to:

- understand what IX-Style is trying to prove
- install the reference environment
- execute the baseline verification flow
- export review-ready artifacts
- inspect results in a useful order

This document exists because a serious repo should not force a reviewer to guess
how to enter the system.

---

## What IX-Style Is

IX-Style is an assured-autonomy reference architecture and executable baseline
for the problem:

> can we prove that when trust degrades, faults accumulate, recovery is requested,
> or authority becomes risky, the vehicle stays inside a safe envelope and leaves
> a usable evidence trail showing why it acted

The current repository baseline includes:

- command authority logic
- runtime-assurance guard logic
- trust evaluation
- FDIR lifecycle handling
- dominant posture allocation
- recovery gating
- mission-health generation
- operator-facing summary generation
- tamper-evident evidence bundles
- review-artifact export
- invariant checking

---

## What This Repo Is Not

At the current baseline, IX-Style is not yet:

- a flight-qualified implementation
- a real-time embedded target
- a full cFS application set
- a hardware-in-the-loop campaign
- a platform-specific certification package

It is a serious reference architecture and executable review baseline.

---

## Recommended Reading Order

A new engineer should read in this order:

1. `docs/PROJECT_CHARTER.md`
2. `docs/requirements/IXS-SYS-REQ-BASELINE.md`
3. `docs/hazards/IXS-HAZARD-REGISTER.md`
4. `docs/architecture/IXS-COMMAND-AUTHORITY-MODEL.md`
5. `docs/architecture/IXS-RUNTIME-ASSURANCE-GUARD.md`
6. `docs/architecture/IXS-SENSOR-TRUST-AND-ESTIMATION-FRAMEWORK.md`
7. `docs/architecture/IXS-FDIR-ARCHITECTURE.md`
8. `docs/architecture/IXS-MODE-ALLOCATION-AND-POSTURE-RESOLUTION.md`
9. `docs/architecture/IXS-RECOVERY-GATE-AND-AUTHORITY-RESTORATION.md`
10. `docs/architecture/IXS-TAMPER-EVIDENT-EVIDENCE-BUNDLES.md`
11. `docs/operations/IXS-MISSION-HEALTH-AND-OPERATOR-SUPPORT.md`
12. `docs/operations/IXS-OPERATOR-RATIONALE-AND-SUMMARY-LAYER.md`
13. `docs/verification/IXS-VERIFICATION-AND-TRACEABILITY-STRATEGY.md`
14. `docs/verification/IXS-INVARIANT-CHECKS-AND-PROPERTY-LAYER.md`
15. `docs/review/IXS-REVIEW-WALKTHROUGH.md`

That order moves from purpose -> hazards -> architecture -> execution -> review.

---

## Baseline Environment

The executable reference baseline currently targets:

- Python 3.11
- editable local install
- pytest
- jsonschema
- PyYAML
- repo-local scripts for self-audit, scenario runs, invariants, and export

---

## Install

From the repository root:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

First Execution Path

A new engineer should run these commands in order.

1. Repository sanity check
python scripts/run_repo_self_audit.py

2. Baseline scenario execution
python scripts/run_sample_scenarios.py

3. Invariant checks
python scripts/run_invariant_checks.py

4. Review-artifact export
python scripts/export_sample_review_artifacts.py

5. Full onboarding flow
python scripts/run_quickstart_flow.py

The last command is the best single-command onboarding path once dependencies are installed.

What Each Script Does
run_repo_self_audit.py

Checks that the important docs, schemas, scripts, and seed traceability artifacts
exist and load correctly.

run_sample_scenarios.py

Executes baseline sample scenarios and validates mission-health output.

run_invariant_checks.py

Evaluates architecture-level non-negotiables over the baseline scenarios.

export_sample_review_artifacts.py

Exports review-ready JSON artifact packages for the baseline scenarios.

run_quickstart_flow.py

Runs the baseline onboarding flow end-to-end and exports review artifacts.

Current Baseline Scenarios

The repository currently emphasizes three baseline executable review scenarios:

Power fault clamp

Shows that low power/resource posture narrows actuation behavior.

Navigation spoof transition

Shows that navigation trust collapse drives posture and evidence generation.

Recovery deferred over weak comms

Shows that recovery-expanding remote intent is deferred when comms trust is weak.

These are not the full future scenario set.
They are the current serious baseline.

Where the Main Logic Lives
src/ix_style/core

Shared data structures, enums, IDs, and pipeline scaffolding.

src/ix_style/authority

Command-source eligibility and authority evaluation.

src/ix_style/guard

Constraint-driven runtime-assurance intervention logic.

src/ix_style/trust

Trust record creation, degradation, and bounded recovery logic.

src/ix_style/fdir

Fault lifecycle and mitigation posture logic.

src/ix_style/modes

Dominant safety posture allocation and posture transition records.

src/ix_style/recovery

Recovery-gate evaluation for authority restoration.

src/ix_style/messages

Schemas, receipts, tamper-evident chains, and evidence bundles.

src/ix_style/telemetry

Mission-health snapshots and operator-facing narration.

src/ix_style/verification

Scenario execution, audits, invariants, exports, and review packages.

What to Inspect First After Running Quickstart

After the onboarding flow succeeds, inspect:

quickstart JSON output in the terminal
exported package directories under the quickstart output root
manifest.json for each exported scenario
operator_safety_summary.json
mission_health_snapshot.json
decision_receipt.json
evidence_bundle.json

That order gives a clean human-to-machine descent.

What “Good” Looks Like

A healthy baseline run should show:

self-audit passed
scenario execution passed
invariant checks passed
evidence bundle validation passed
exported review package directories created
mission-health posture aligned with scenario intent
operator summary aligned with receipt and snapshot state
Common Failure Interpretation
Self-audit failure

Usually means a required file path, schema, or artifact is missing.

Scenario failure

Usually means a decision outcome or required degradation flag did not match the scenario expectation.

Invariant failure

Usually means an architecture truth was violated, such as:

recovery blocked too late
required evidence missing
posture changed without a mode transition
bundle integrity failed
Bundle validation failure

Usually means exported evidence was altered, malformed, or chained incorrectly.

Onboarding Exit Criteria

A new engineer is meaningfully onboarded when they can:

explain the repo purpose in one sentence
run the baseline flow without guessing commands
find the decision receipt for a scenario
find the dominant posture for a scenario
verify that the evidence bundle validates
explain why a scenario outcome occurred using the exported artifacts

That is the real quickstart finish line.

Deferred Items

This document intentionally does not yet add:

containerized onboarding
Windows-specific automation wrappers
Makefile targets
extended scenario packs
full reviewer FAQ

Those can come later if useful.
