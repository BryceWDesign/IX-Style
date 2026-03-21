# IX-Style

IX-Style is an assured-autonomy reference architecture and executable review baseline for this aerospace question:

**When trust degrades, faults accumulate, comms weaken, recovery is requested, or a subsystem lies, can the vehicle stay inside a bounded safe envelope and leave a usable evidence trail showing why it acted?**

This repository is built to answer that question in a structured, reviewable way.

## What IX-Style currently does

The current baseline includes:

- command authority evaluation
- runtime-assurance guard logic with explicit named constraints
- trust degradation and bounded trust recovery logic
- FDIR lifecycle handling
- dominant safety-posture allocation
- recovery-gate evaluation before authority restoration
- mission-health snapshot generation
- operator-facing concise safety summaries
- tamper-evident evidence bundles with hash chaining
- review-ready JSON artifact package export
- executable invariant checks over baseline scenarios

## What IX-Style is not

At the current baseline, IX-Style is **not**:

- flight-qualified software
- a real-time embedded deployment
- a complete cFS flight application set
- a certification package
- a hardware-in-the-loop campaign

It is a serious **reference implementation and review baseline**.

## Why this repo exists

A lot of autonomy work looks fine until one of these happens:

- navigation trust collapses
- sensor confidence degrades
- actuation confidence weakens
- power margin drops
- comms become intermittent or stale
- recovery is requested too early
- evidence is weak or easy to rewrite

IX-Style is designed around the idea that those are not edge cases.  
They are exactly where the architecture has to prove itself.

## Quickstart

From the repository root:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python scripts/run_quickstart_flow.py

That quickstart flow runs the repo self-audit, executes the baseline scenarios, checks invariants, and exports review-ready artifact packages.

Recommended first commands

Run these in order if you want to inspect the repo step by step:

python scripts/run_repo_self_audit.py
python scripts/run_sample_scenarios.py
python scripts/run_invariant_checks.py
python scripts/export_sample_review_artifacts.py
python scripts/run_quickstart_flow.py
Current baseline scenarios

IX-Style currently ships three main executable review scenarios:

1. Power fault clamp

Shows that low power/resource posture narrows mission-progress behavior.

2. Navigation spoof transition

Shows that navigation trust collapse drives degraded posture and evidence generation.

3. Recovery deferred over weak comms

Shows that remote recovery-expanding intent is deferred when communications trust is weak.

What gets produced

A successful scenario run can produce:

decision receipt
trust transitions
fault transitions
mode transitions
mission-health snapshot
operator safety summary
tamper-evident evidence bundle
exported review package
Review order

If you open one exported review package, inspect files in this order:

manifest.json
operator_safety_summary.json
mission_health_snapshot.json
decision_receipt.json
evidence_package.json
evidence_bundle.json
verification_result.json

That sequence moves from fast human understanding to detailed machine evidence.

Repository map
Core architecture and execution
src/ix_style/core
src/ix_style/authority
src/ix_style/guard
src/ix_style/trust
src/ix_style/fdir
src/ix_style/modes
src/ix_style/recovery
Evidence, telemetry, and review outputs
src/ix_style/messages
src/ix_style/telemetry
src/ix_style/verification
Docs
docs/architecture
docs/operations
docs/verification
docs/developer
docs/review
Scripts
scripts/run_repo_self_audit.py
scripts/run_sample_scenarios.py
scripts/run_invariant_checks.py
scripts/export_sample_review_artifacts.py
scripts/run_quickstart_flow.py
Recommended reading order

For a serious technical read, go in this order:

docs/PROJECT_CHARTER.md
docs/requirements/IXS-SYS-REQ-BASELINE.md
docs/hazards/IXS-HAZARD-REGISTER.md
docs/architecture/IXS-COMMAND-AUTHORITY-MODEL.md
docs/architecture/IXS-RUNTIME-ASSURANCE-GUARD.md
docs/architecture/IXS-SENSOR-TRUST-AND-ESTIMATION-FRAMEWORK.md
docs/architecture/IXS-FDIR-ARCHITECTURE.md
docs/architecture/IXS-MODE-ALLOCATION-AND-POSTURE-RESOLUTION.md
docs/architecture/IXS-RECOVERY-GATE-AND-AUTHORITY-RESTORATION.md
docs/architecture/IXS-TAMPER-EVIDENT-EVIDENCE-BUNDLES.md
docs/operations/IXS-MISSION-HEALTH-AND-OPERATOR-SUPPORT.md
docs/operations/IXS-OPERATOR-RATIONALE-AND-SUMMARY-LAYER.md
docs/verification/IXS-VERIFICATION-AND-TRACEABILITY-STRATEGY.md
docs/verification/IXS-INVARIANT-CHECKS-AND-PROPERTY-LAYER.md
docs/developer/IXS-DEVELOPER-ONBOARDING-AND-QUICKSTART.md
docs/review/IXS-REVIEW-WALKTHROUGH.md
Current technical posture

IX-Style is strongest today as:

an assured-autonomy architecture repo
a verification-oriented reference implementation
a review artifact generator
a foundation for future platform-specific integration

It is designed to be taken seriously by engineers who care about:

FDIR
runtime assurance
degraded-mode behavior
authority containment
recovery gating
operator decision support
evidence quality
review survivability under scrutiny
CI

The repository includes CI that runs:

unit tests
repository self-audit
sample scenarios
invariant checks

See:
.github/workflows/ci.yml
Exported artifacts

Quickstart and export scripts write review packages under:
artifacts/review_packages
artifacts/quickstart_review_packages

Each package includes the baseline machine and human-facing outputs needed for technical inspection.

Current maturity statement

The repo is now at the point where a reviewer can:

run the baseline flow
inspect scenario outcomes
verify posture and authority behavior
validate evidence bundles
review operator-facing summaries
inspect exported artifact packages without guessing the intended order

That is the current bar IX-Style is aiming to clear.

License
IX-Style is licensed under the Apache License 2.0.

See:
LICENSE
NOTICE

Author: Bryce Lovell
