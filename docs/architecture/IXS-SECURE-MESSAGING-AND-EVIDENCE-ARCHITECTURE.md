# IX-Style Secure Messaging and Evidence Architecture

## Document ID

IXS-SECURE-MESSAGING-AND-EVIDENCE-ARCHITECTURE

## Status

Draft architecture baseline.

## Purpose

This document defines the messaging and evidence architecture for IX-Style.

It exists to answer the following questions:

- how are safety-relevant messages structured
- how does the system distinguish control data from telemetry and evidence
- how are freshness, origin, ordering, and replay concerns represented
- what must be captured when the system accepts, rejects, clamps, substitutes,
  freezes, or escalates a command
- how does IX-Style preserve auditable decision evidence without mixing it into
  routine telemetry noise

This architecture is one of the main reasons IX-Style can claim "evidence trail"
instead of empty explainability language.

---

## Core Principle

IX-Style does not treat all messages as equal.

A safety-relevant control event, a routine advisory update, and an auditable
decision receipt are different things and must remain structurally distinct.

That means IX-Style explicitly separates:

- advisory traffic
- control-plane traffic
- posture and fault events
- trust transitions
- evidence records

This separation is mandatory because otherwise:
- stale control intent can be mistaken for current authority
- safety-relevant records can be buried in noise
- replay risk becomes harder to reason about
- post-event review becomes muddy and weak

---

## Messaging Objectives

The IX-Style messaging layer shall support:

1. deterministic contracts for safety-relevant communication
2. explicit message-class separation
3. freshness-aware handling for control-plane traffic
4. authenticated source representation for safety-relevant events
5. replay-aware handling
6. sequence and causality tracking
7. machine-readable evidence records for decisions and state changes
8. append-only or tamper-evident evidence patterns
9. delayed-link and intermittent-link survivability for event review

---

## Message Class Model

IX-Style defines the following baseline message classes.

### ADVISORY
Routine informational traffic that is useful but not directly authoritative for
safety-relevant control decisions.

Examples:
- noncritical status summaries
- background telemetry summaries
- debug-level simulation notes

### CONTROL
Messages that propose or carry safety-relevant commands or command-like intent.

Examples:
- actuation request
- guidance request
- resource configuration request
- recovery action request

### MODE_EVENT
Messages that represent operational mode or posture transitions.

Examples:
- entered nav degraded
- exited sensor degraded
- entered safe-hold
- recovery gate blocked return to nominal

### TRUST_EVENT
Messages that represent trust-state transitions or trust-evaluation findings.

Examples:
- navigation trust dropped to suspect
- actuator confidence degraded
- freshness invalidated a control source
- assurance confidence degraded

### FAULT_EVENT
Messages that represent FDIR lifecycle activity.

Examples:
- fault created
- fault confirmed
- mitigation started
- fault latched
- fault cleared

### EVIDENCE
Messages that are preserved as review-critical records for decisions, command
arbitration, interventions, or recovery-related actions.

Examples:
- decision receipt
- arbitration receipt
- intervention receipt
- recovery qualification receipt

---

## Message Handling Philosophy

IX-Style uses different handling rules depending on message class.

### ADVISORY
- may tolerate delay better than control-plane data
- must not be mistaken for authority
- lower review criticality unless promoted by policy

### CONTROL
- freshness-sensitive
- origin-sensitive
- replay-sensitive
- schema-validity-sensitive
- may be rejected even if transport delivery succeeded

### MODE_EVENT / TRUST_EVENT / FAULT_EVENT
- must preserve ordering and causality where practical
- may influence later authority and posture decisions
- must be identifiable as event records, not commands

### EVIDENCE
- must remain tamper-evident or append-only in design intent
- must preserve enough fields for post-event reconstruction
- must not be silently rewritten by downstream convenience systems

---

## Common Message Envelope

All IX-Style messages use a common envelope concept.

The common envelope exists so tooling, validation, replay awareness, and
ordering logic can behave consistently across message classes.

The baseline envelope contains:

- schema version
- message identifier
- message class
- message type
- source identifier
- source kind
- creation timestamp
- timing/freshness fields
- sequence and ordering fields
- causal linkage fields
- integrity metadata
- payload

---

## Required Envelope Fields

### schema_version
Version of the contract used to validate the message.

### message_id
Globally unique identifier for the message instance.

### message_class
One of:
- ADVISORY
- CONTROL
- MODE_EVENT
- TRUST_EVENT
- FAULT_EVENT
- EVIDENCE

### message_type
More specific type within the class.

Examples:
- control.actuation_request
- trust.navigation_transition
- fault.lifecycle_update
- evidence.decision_receipt

### source_id
Identifier for the message origin.

### source_kind
Category of origin.

Examples:
- operator
- mission_logic
- nominal_autonomy
- contingency_logic
- safety_supervisor
- subsystem
- infrastructure

### created_at
Creation time of the message record.

### freshness
Structured freshness information for handling.

### ordering
Sequence and session-related ordering metadata.

### causality
Optional linkage to parent message, triggering event, candidate action, or fault.

### integrity
Structured integrity and authentication metadata.

### payload
Message-type-specific content.

---

## Freshness Model

IX-Style does not treat arrival as proof of relevance.

A message can be:
- delivered successfully
- syntactically valid
- authenticated
- and still be operationally stale

The messaging layer therefore represents freshness explicitly.

Freshness fields should support:

- issue time
- validity window or expiry time
- freshness state
- freshness evaluation cause
- last-known trusted session context if applicable

Freshness states include:

- `FRESH`
- `STALE`
- `EXPIRED`
- `TIMING_INVALID`
- `UNKNOWN`

Control-plane messages that are not fresh enough for their function class must
not be treated as current authority.

---

## Ordering and Replay Awareness

IX-Style requires replay-aware handling for safety-relevant control and evidence
traffic.

The architecture therefore represents:

- sequence number or monotonic event index
- session identifier or epoch identifier
- optional parent event identifier
- optional supersedes identifier
- replay evaluation result

Replay-related states include:

- `NOT_EVALUATED`
- `ACCEPTABLE`
- `DUPLICATE`
- `OUT_OF_SEQUENCE`
- `REPLAY_SUSPECTED`

This is not just for security posture.
It also protects operational trust and post-event reconstruction.

---

## Integrity Metadata

IX-Style message integrity representation is intentionally structured, even if
the exact cryptographic implementation is chosen later.

Integrity metadata should support:

- origin authentication result
- integrity verification result
- key or trust-domain identifier if applicable
- signature or authenticator presence
- verification time
- verification status rationale

Integrity states include:

- `INTEGRITY_VALID`
- `INTEGRITY_DEGRADED`
- `INTEGRITY_FAILED`
- `AUTH_UNVERIFIED`
- `AUTH_INVALID`

Transport delivery alone is not enough.

---

## Command Message Requirements

Safety-relevant control-plane messages must carry enough structure for the
authority model and runtime-assurance guard to evaluate them.

At minimum, a control message must express:

- function class
- requested action
- requested target or scope
- requested magnitude/rate/duration if relevant
- command source
- policy-relevant context
- freshness
- integrity
- ordering
- candidate rationale if available

A control message is not automatically authoritative because it exists.
It becomes authoritative only after arbitration and guard processing.

---

## Event Message Requirements

Mode, trust, and fault events must carry enough structure to explain change.

At minimum, these event classes should represent:

- previous state
- new state
- transition cause codes
- affected entity or scope
- triggering condition or linked message
- related fault or trust IDs if applicable
- event priority or review significance
- human-readable rationale summary

These event messages are still structured data first, readable text second.

---

## Evidence Model

IX-Style evidence messages are the review-critical records that explain why
safety-relevant decisions occurred.

Evidence records should be treated as:
- append-only in intent
- independently reviewable
- machine-readable
- causally linked to commands, events, faults, and interventions

Examples of evidence records:
- command arbitration receipt
- runtime-assurance intervention receipt
- mode transition receipt
- trust transition receipt
- recovery qualification receipt
- operator override receipt

---

## Decision Receipt

The central evidence artifact in IX-Style is the decision receipt.

A decision receipt records, at minimum:

- decision identifier
- candidate action summary
- final outcome
- final authoritative source
- active mission phase
- active safety posture
- active degradation flags
- trust posture summary
- related fault identifiers
- triggered constraint identifiers
- policy evaluation result
- recovery gate result if relevant
- rationale summary
- command delta if clamped or substituted
- evidence ordering fields

A decision receipt exists so that later nobody has to guess:
- who asked for what
- what the system knew
- why the action changed or failed
- whether posture or authority changed because of it

---

## Separation of Telemetry and Evidence

IX-Style explicitly separates high-volume telemetry from review-critical evidence.

### Telemetry
- optimized for monitoring and trend visibility
- may be summarized, buffered, or downsampled

### Evidence
- optimized for post-event trust, audit, and causality
- must preserve review-critical fidelity
- should not depend on routine telemetry retention policies

A system that stores everything in one giant stream often ends up preserving
nothing that matters clearly enough.

---

## Causality Model

IX-Style message contracts should support causal linkage.

Examples:
- a control request caused an arbitration receipt
- an arbitration receipt caused a guard intervention receipt
- a trust drop caused a mode event
- a fault confirmation caused a safe-hold transition

Useful causality fields include:

- parent_message_id
- triggering_event_id
- related_fault_ids
- related_trust_record_ids
- candidate_action_id
- supersedes_message_id

This is what turns a pile of events into a reconstructable chain.

---

## Evidence Severity / Review Significance

Evidence records may carry review significance levels to support operator tooling
and post-event triage.

Baseline levels:
- `ROUTINE`
- `IMPORTANT`
- `HIGH`
- `CRITICAL`

Examples:
- ordinary clamp during a mild degraded mode may be `IMPORTANT`
- rejected recovery from assurance-degraded posture may be `HIGH`
- forced safe-hold due to guard-health collapse may be `CRITICAL`

---

## Append-Only / Tamper-Evident Intent

IX-Style evidence architecture requires tamper-evident design intent.

That means later implementations should support one or more of:

- append-only logs
- chained hashes
- signed receipts
- immutable event export paths
- independently verifiable receipt bundles

This commit does not force one mechanism yet.
It does force the architectural expectation that evidence must resist silent
rewriting.

---

## Delayed-Link and Intermittent-Link Behavior

IX-Style assumes that some environments will not provide continuous connectivity.

Therefore the messaging/evidence architecture should support:

- delayed review of accumulated evidence
- preservation of ordering metadata across reconnect
- explicit reconciliation events after link restoration
- no silent rewriting of earlier authoritative decisions after delayed delivery

A late message may explain history.
It must not rewrite history.

---

## Message Contract Non-Negotiables

IX-Style messaging is not complete unless:

1. message classes are explicitly separated
2. safety-relevant control traffic carries freshness and integrity metadata
3. replay-aware fields exist for control and evidence traffic
4. decision receipts capture rationale and outcome
5. evidence remains separable from routine telemetry
6. causality between commands, events, and evidence can be represented
7. stale delivery is not mistaken for valid authority

---

## Deferred Items

This commit intentionally does not yet finalize:

- specific transport middleware
- exact cryptographic algorithms
- exact key-management approach
- target-platform serialization format
- final evidence retention policy
- final compression or batching approach for delayed links

Those belong in later commits and target integration work.

---

## Completion Criteria

This messaging/evidence architecture is not mature until later commits allocate:

1. concrete schema files for major message classes
2. exact field validation rules and enums
3. reference code scaffolding for message validation
4. reference code scaffolding for receipt generation
5. verification scenarios for stale, replayed, out-of-sequence, and invalid messages
6. integration of decision receipts with guard, FDIR, and authority paths
