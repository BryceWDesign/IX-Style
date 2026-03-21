# IX-Style Tamper-Evident Evidence Bundles

## Document ID

IXS-TAMPER-EVIDENT-EVIDENCE-BUNDLES

## Status

Draft architecture baseline.

## Purpose

This document defines the tamper-evident evidence-bundle architecture for
IX-Style.

It exists to answer the question:

> Once IX-Style produces decision receipts, trust transitions, fault transitions,
> and posture transitions, how are those records grouped and protected so later
> review can detect tampering or silent rewriting?

This matters because evidence that can be silently rewritten is weak evidence.

---

## Core Principle

IX-Style treats review-critical evidence as append-oriented material that should
be protected by deterministic integrity structure.

The baseline executable approach is:

- canonical serialization
- per-item content hashing
- ordered hash chaining
- bundle head hash
- bundle verification that detects tampering

This does not claim absolute immutability.
It does provide a clear tamper-evident baseline.

---

## Why Bundles Exist

Single receipts are useful, but real review usually needs a coherent set of
related records:

- the decision receipt
- trust transitions
- fault transitions
- mode transitions
- later, additional evidence artifacts

An evidence bundle groups those related records into one integrity-checked
package.

---

## Bundle Objectives

IX-Style evidence bundles should support:

1. deterministic content hashing
2. deterministic ordering
3. reviewable item-by-item chain records
4. bundle-level head hash
5. detection of modified, removed, or reordered content
6. transportable review artifacts

---

## Bundle Structure

A baseline evidence bundle contains:

- bundle identifier
- schema version
- creation timestamp
- scenario identifier
- integrity metadata
- ordered bundle items

Each bundle item contains:

- item index
- item type
- item identifier
- canonical item hash
- previous chain hash
- current chain hash
- original data payload

This structure allows a reviewer or tool to verify both:
- item integrity
- ordering integrity

---

## Canonicalization Requirement

Hashing only works cleanly when the same logical content always becomes the same
byte representation.

Therefore IX-Style uses canonical JSON-style serialization intent:

- sorted keys
- compact separators
- stable enum serialization
- stable datetime serialization

If canonicalization changes, the resulting hashes change.
That is expected and should be versioned deliberately.

---

## Hash Chaining Model

For each bundle item:

1. canonicalize the item payload
2. hash the canonical payload
3. combine:
   - item index
   - item type
   - item identifier
   - previous chain hash
   - item hash
4. hash that combined string to form the current chain hash

The final item’s chain hash becomes the bundle head hash.

---

## Genesis Concept

The first item uses a fixed genesis marker instead of a previous item hash.

This makes the chain deterministic and self-starting without requiring external
state.

---

## What Tamper-Evidence Detects

The baseline chain can detect:

- changed payload content
- reordered items
- deleted items
- inserted items without recomputing the chain
- corrupted chain metadata

This does **not** by itself prove who changed the content.
It proves the bundle no longer matches its declared chain.

---

## Bundle Verification

Bundle verification should check:

- required integrity fields exist
- item count matches the number of items
- each item hash recomputes correctly
- each chain hash recomputes correctly
- each previous-chain reference is consistent
- final head hash matches the declared bundle head hash

Any mismatch means the bundle integrity check fails.

---

## Why This Matters for IX-Style

This layer is important because IX-Style specifically claims that the system can
leave an evidence trail showing why it acted.

A serious audience will reasonably ask:

- how do you know the trail was not rewritten later
- how do you know the ordering was preserved
- how do you know the decision receipt still matches the original evidence

This bundle layer is the first executable answer to those questions.

---

## Relationship to Other Layers

### Decision Receipts
Decision receipts remain the central explanatory artifact.

### Trust / Fault / Mode Events
Transition events provide the surrounding chain of operational context.

### Verification Evidence Packages
An evidence package can now include a tamper-evident bundle instead of only a
plain collection of records.

### Future Signed Evidence
Later implementations may add signatures, external anchoring, or archival
systems on top of this baseline.

---

## Deferred Items

This commit intentionally does not yet add:

- digital signatures
- external timestamp authorities
- immutable storage backends
- receipt notarization across machines
- Merkle-tree bundle variants
- multi-bundle archival indexes

Those belong in later commits.

---

## Completion Criteria

This evidence-bundle layer is not mature until later commits allocate:

1. signature support
2. bundle export/import tooling
3. bundle retention policy
4. bundle comparison tools
5. scenario coverage for corrupted or reordered multi-item bundles
