# IX-Style Review Artifact Packages

## Document ID

IXS-REVIEW-ARTIFACT-PACKAGES

## Status

Draft verification baseline.

## Purpose

This document defines the review-artifact packaging layer for IX-Style.

It exists to answer the question:

> Once IX-Style has produced a decision receipt, evidence bundle, mission-health
> snapshot, and operator-facing summary, how are those artifacts exported in a
> stable review package that another engineer can inspect later?

This matters because good internal structure still needs a clean handoff format.

---

## Core Principle

IX-Style review packages are export-oriented collections of already-generated
artifacts.

They should be:

- machine-readable
- easy to archive
- easy to compare
- easy to inspect offline
- grounded in the exact structured artifacts already produced by the runtime

The export layer should not invent new truth.
It should package existing truth cleanly.

---

## Package Contents

A baseline review package includes:

- manifest
- verification result
- evidence package
- decision receipt
- mission-health snapshot
- operator safety summary
- evidence bundle

This is the minimum useful review set for the current executable repo.

---

## Manifest Purpose

The manifest exists so a reviewer can answer:

- what scenario this package belongs to
- when it was exported
- which files are present
- whether the scenario passed
- what dominant posture resulted
- what the final decision outcome was

The manifest should be the first file a reviewer opens.

---

## Export Principles

### Rule 1 — JSON first
The baseline export format is JSON because it is easy to inspect, validate, diff,
and automate.

### Rule 2 — Stable filenames
The export layer should use stable, predictable filenames inside one package
directory.

### Rule 3 — Preserve structured fidelity
The exported files should preserve the original structured content rather than
flattening it into prose only.

### Rule 4 — Keep human summary alongside machine artifacts
A reviewer should not need to parse only raw events; the operator-facing summary
should be exported too.

### Rule 5 — Do not silently omit evidence
If a scenario produced an evidence bundle, it belongs in the package.

---

## Baseline Filenames

The baseline export package uses these filenames:

- `manifest.json`
- `verification_result.json`
- `evidence_package.json`
- `decision_receipt.json`
- `mission_health_snapshot.json`
- `operator_safety_summary.json`
- `evidence_bundle.json`

This naming is intentionally plain and review-friendly.

---

## Import Intent

The baseline import layer should support:

- loading exported JSON artifacts
- reconstructing a review package object
- checking that required files exist
- basic bundle validation during review if requested

This supports future comparison, audit, and archival tooling.

---

## Why This Layer Matters

A serious aerospace repo needs to show it can hand over evidence in a reviewable
form, not just generate it transiently in memory.

This layer helps IX-Style move from:
- executable scenario logic

to:
- review-ready scenario outputs

That is an important difference.

---

## Deferred Items

This commit intentionally does not yet add:

- signed export manifests
- ZIP bundling
- PDF review reports
- HTML dashboards
- cross-package diff tooling
- long-term archive indexing

Those belong in later commits if needed.

---

## Completion Criteria

This review-package layer is not mature until later commits allocate:

1. signed manifests
2. package comparison tooling
3. archive indexing
4. richer scenario collections
5. optional compressed bundle export
