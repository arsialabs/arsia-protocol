<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
# ARSIA-State — State Primitive Specification

**Protocol:** ARSIA Protocol
**Version:** 1.0
**Status:** Draft
**Authors:**
- Kirk Patrick (Arsia Labs) — kirk@arsialabs.ai
- Greici Savoldi (Arsia Labs) — greici@arsialabs.ai

**Draft-01 | March 2026 | References: ARSIA-Core.md §4 (message envelope), §4.3.6 (compliance
field definition), §4.3.7 (field inheritance), §4.3.8 (validation rules), §6.4 (capability
enforcement), §9.2 (brokered routing — data residency), ARSIA-Identity.md §1.2 (IdentityRecord)**
**Arsia Labs — arsiaprotocol.org**

---

## Abstract

The State primitive defines how ARSIA Protocol agents declare, access, and manage
persistent memory. It does not mandate a storage backend — it mandates the interface,
the data shapes, the compliance obligations around retained data, and the GDPR
mechanisms (including right to erasure) that every compliant implementation MUST
provide. State is the primitive that answers: what does an agent remember, who can
access it, for how long must it be kept, and where must it be stored. ARSIA sits above
storage engines — PostgreSQL, Redis, S3, or any other backend may implement the State
interface — and below the application layer where agents consume and produce stateful
data. This separation is deliberate: ARSIA is a protocol, not a database.

---

## Status of This Memo

This document specifies Draft-01 of the ARSIA State Primitive. This specification is
a working draft published by Arsia Labs for review and comment. Implementors should
expect breaking changes between draft revisions.

The canonical location for this specification is:

    https://arsiaprotocol.org/spec/state/draft-01

Comments and issues should be directed to:

    https://github.com/arsialabs/arsia-protocol/issues

---

## Copyright Notice

Copyright (c) 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda).
This specification is licensed under the Creative Commons
Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0).
See LICENSE-SPEC.md for full terms.

---

## Table of Contents

1. [State Scope Taxonomy](#1-state-scope-taxonomy)
   1. [Session Scope](#11-session-scope)
   2. [Agent Scope](#12-agent-scope)
   3. [Shared Scope](#13-shared-scope)
   4. [Global Scope](#14-global-scope)
   5. [Scope Summary](#15-scope-summary)
2. [State Entry Format](#2-state-entry-format)
   1. [StateEntry Object](#21-stateentry-object)
   2. [Key Naming Conventions](#22-key-naming-conventions)
   3. [Value Constraints](#23-value-constraints)
   4. [Version Semantics](#24-version-semantics)
3. [State Operations](#3-state-operations)
   1. [Core Operations](#31-core-operations)
   2. [Compliance Operations](#32-compliance-operations)
   3. [Shared State Access Grants](#33-shared-state-access-grants)
   4. [Operation Summary](#34-operation-summary)
4. [Retention and Data Residency](#4-retention-and-data-residency)
   1. [Retention Policy](#41-retention-policy)
   2. [Data Residency Enforcement](#42-data-residency-enforcement)
   3. [Archival](#43-archival)
5. [GDPR Obligations](#5-gdpr-obligations)
   1. [Records of Processing Activities (Art. 30)](#51-records-of-processing-activities-art-30)
   2. [Legal Basis (Art. 6)](#52-legal-basis-art-6)
   3. [Right to Erasure (Art. 17)](#53-right-to-erasure-art-17)
   4. [Data Minimisation (Art. 5(1)(c))](#54-data-minimisation-art-51c)
   5. [Data Portability (Art. 20)](#55-data-portability-art-20)
   6. [Art. 9 Special Categories](#56-art-9-special-categories)
   7. [Breach Notification (Art. 33/34)](#57-breach-notification-art-3334)
6. [Compliance Profiles](#6-compliance-profiles)
   1. [GDPR-STANDARD (Default Baseline)](#61-gdpr-standard-default-baseline)
   2. [EU-AI-ACT-HIGH-RISK](#62-eu-ai-act-high-risk)
   3. [MIFID-II](#63-mifid-ii)
   4. [PAC-AGRICULTURE](#64-pac-agriculture)
   5. [EU-AI-ACT-LIMITED-RISK](#65-eu-ai-act-limited-risk)
   6. [DSA-VLOP](#66-dsa-vlop)
   7. [DORA](#67-dora)
7. [Audit Trail](#7-audit-trail)
   1. [ArsiaAuditRecord Structure](#71-arsiaauditrecord-structure)
   2. [Immutability Requirements](#72-immutability-requirements)
   3. [Audit Record Retention](#73-audit-record-retention)
   4. [Audit Trail Query Endpoint](#74-audit-trail-query-endpoint)
8. [State in the ARSIA Message Envelope](#8-state-in-the-arsia-message-envelope)
   1. [Payload Type Prefix](#81-payload-type-prefix)
   2. [Required Capabilities](#82-required-capabilities)
   3. [Compliance Inheritance](#83-compliance-inheritance)
   4. [Error Codes](#84-error-codes)
9. [State Conformance Tests](#9-state-conformance-tests)
10. [Security Considerations](#10-security-considerations)
    1. [Access Control](#101-access-control)
    2. [Injection and Abuse](#102-injection-and-abuse)
    3. [Side-Channel Risks](#103-side-channel-risks)
    4. [Encryption at Rest](#104-encryption-at-rest)
11. [Implementation Guidance (Informative)](#11-implementation-guidance-informative)
    1. [Storage Backend Selection](#111-storage-backend-selection)
    2. [Temporal Storage](#112-temporal-storage)
    3. [Performance Considerations](#113-performance-considerations)
    4. [Hash Chain (RECOMMENDED)](#114-hash-chain-recommended)
12. [References](#12-references)
    1. [Normative References](#121-normative-references)
    2. [Informative References](#122-informative-references)

---

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14 [RFC 2119] [RFC 8174] when,
and only when, they appear in ALL CAPITALS, as shown here.

---

## 1. State Scope Taxonomy

ARSIA defines four state scopes. Each scope determines the lifecycle, visibility,
persistence requirements, and compliance obligations of the data it contains. Scopes
are hierarchical in terms of durability and compliance burden: session state has the
least obligation, global state has the most restricted access model.

Every state entry (§2) MUST declare exactly one scope. The scope is immutable after
creation — an entry's scope MUST NOT be changed. To move data between scopes, the
agent MUST create a new entry in the target scope and delete the original.

### 1.1 Session Scope

**Purpose.** Session-scoped state holds temporary data bounded to a single
request/response cycle. It exists to support multi-step reasoning chains,
intermediate computations, and transient context that is meaningful only within
the lifecycle of a single interaction.

**Lifetime.** Session state is bound to a correlation chain — the set of messages
linked by `correlation_id` fields (ARSIA-Core.md §4.2.1). A session begins when the
initial request message is sent and ends when one of the following conditions is met:

1. A final response (with `intent` of `"response"`) is delivered to the original
   requester and acknowledged.
2. An error (with `intent` of `"error"`) terminates the chain.
3. The request's `expires_at` timestamp (ARSIA-Core.md §4.2.2) is reached without a
   response.
4. An implementation-defined session timeout elapses. The session timeout MUST NOT
   exceed 24 hours. A session timeout of 1 hour is RECOMMENDED.

When the session ends, all session-scoped state entries associated with that
correlation chain MUST be eligible for immediate removal. Implementations SHOULD
remove session state entries promptly after session termination.

**Visibility.** Session state is visible only to the two agents participating in the
request/response exchange — the agent identified in the `from` field and the agent
identified in the `to` field of the originating request message. No other agent,
including compliance brokers, MAY access session-scoped entries.

**Persistence.** Implementations MUST NOT persist session state to durable storage
under normal operating conditions. Session state SHOULD be held in volatile memory
(RAM, in-process cache, or equivalent). If an implementation must use durable storage
for operational reasons (e.g., process restart recovery during a long-running session),
the implementation MUST delete the session state entries upon session termination and
MUST NOT include session state in backup or replication processes.

**Compliance obligations.** Session state carries no retention obligation. Session
state entries MUST NOT generate audit events. Session state entries are not subject to
`compliance.retention_days` or `compliance.data_residency` from the message envelope.
Session state is ephemeral by design — its entire purpose is to hold data that does
not need to outlive the interaction that created it.

**PII in session state.** Despite the ephemeral nature of session state, agents MUST
still declare `pii_classification` on session-scoped entries. If `pii_classification`
is `"personal"`, the agent SHOULD prefer processing the data in-memory without
materialising it to any persistent medium. Implementations MUST ensure that session
state containing personal data is not inadvertently captured in application logs,
debug dumps, or crash reports.

**Example uses.**

- Intermediate computation results during a multi-step reasoning chain.
- Temporary context accumulated during a conversation turn.
- Scratch space for a risk assessment agent computing a score from multiple data
  sources within a single request.

### 1.2 Agent Scope

**Purpose.** Agent-scoped state is persistent data belonging to a single agent's
identity. This is the agent's private memory — its configuration, learned preferences,
accumulated knowledge, and operational data. Agent-scoped state is the most common
scope for long-lived data.

**Lifetime.** Agent-scoped state persists until one of the following conditions is met:

1. The owning agent explicitly deletes the entry via the DELETE operation (§3.1).
2. The owning agent explicitly purges the entry via the PURGE operation (§3.2).
3. The entry's `expires_at` timestamp is reached, and the retention period has also
   elapsed.
4. The retention period (either the entry's `retention_days` or the compliance
   profile's default retention) expires, and no regulatory hold prevents deletion.

Agent-scoped state MUST survive agent restarts, infrastructure migrations, and routine
maintenance operations. Loss of agent-scoped state due to operational events (as
opposed to explicit deletion or expiry) constitutes a data integrity failure.

**Visibility.** Agent-scoped state is private by default. Only the owning agent — the
agent whose `agent_id` matches the `owner_agent_id` field of the StateEntry — MAY
read or write agent-scoped entries. Access by other agents is prohibited unless an
explicit grant has been issued (§3.3). When a grant is active, the grantee agent MAY
access the entry according to the grant's `access_level` (read or read-write). Even
with a grant, the entry remains owned by the original agent — grants do not transfer
ownership.

**Persistence.** Agent-scoped state MUST be persisted to durable storage. "Durable
storage" means a storage medium that survives process termination, machine restart,
and — for regulated deployments — single-node failure. The specific durability
guarantee (e.g., synchronous replication, WAL-based recovery, multi-region
replication) is an implementation decision, not a protocol requirement. The protocol
requires only that the data is not lost under normal operational conditions.

**Compliance obligations.** Agent-scoped state is subject to the following compliance
rules:

1. **Retention.** The entry's effective retention period is governed by
   `StateEntry.retention_days` (if set) or the active compliance profile's
   `retention_days` (if the entry was created in a compliance context). The entry
   MUST NOT be physically deleted before the effective retention period expires,
   except via PURGE for GDPR erasure (§5.3). See §4.1 for the complete retention
   policy.

2. **Audit.** If the compliance profile's `audit_required` field is `true` for the
   context in which this entry was created or modified, every SET and DELETE operation
   on this entry MUST generate an audit event. The audit event format is defined in
   §7. At minimum, the audit event MUST
   include: the operation type (`state_set`, `state_delete`), the entry key, the
   `owner_agent_id`, the agent that performed the operation, a timestamp, and the
   entry's new version number. The audit event MUST NOT include the entry's value
   unless the compliance profile explicitly requires value-level auditing.

3. **Data residency.** If `StateEntry.data_residency` is set (either explicitly or
   inherited from the compliance profile), the storage backend for this entry MUST
   physically reside within the declared zone. See §4.2 for the complete data
   residency enforcement rules.

**Example uses.**

- Agent configuration and operational parameters.
- Learned preferences from prior interactions.
- Accumulated knowledge and context from previous conversations.
- Client records maintained by a financial advisory agent.
- Model fine-tuning metadata and version history.

### 1.3 Shared Scope

**Purpose.** Shared-scoped state is persistent data that has been explicitly shared
between two or more agents. Shared state enables collaborative workflows where
multiple agents need access to common context — for example, a risk assessment agent
and a compliance checking agent collaborating on a MiFID II workflow, or a team of
agents sharing a common knowledge base.

Shared state is not a broadcast mechanism. It is a controlled, auditable sharing
model where the owning agent explicitly grants access to specific agents for specific
keys or key patterns.

**Lifetime.** Shared-scoped state persists until one of the following conditions is
met:

1. The owning agent explicitly deletes the entry via the DELETE operation (§3.1).
2. The owning agent explicitly purges the entry via the PURGE operation (§3.2).
3. The entry's `expires_at` timestamp is reached, and the retention period has also
   elapsed.
4. The retention period expires, and no regulatory hold prevents deletion.

Grants on shared-scoped entries have their own lifecycle (§3.3). Revoking a grant
does not delete the underlying entry — it merely removes the grantee's access. The
entry continues to exist and is accessible to the owner and any remaining grantees.

**Visibility.** Shared-scoped entries are accessible by:

1. The owning agent (full read-write access, always).
2. Any agent with an active grant for the entry's key or a matching key pattern
   (§3.3). The grant specifies the access level: `"read"` for read-only access or
   `"read_write"` for full read-write access.

Agents without an active grant MUST NOT be able to access shared-scoped entries, even
if they can guess or enumerate the entry's key. Implementations MUST enforce access
control at the operation level, not merely at the key discovery level.

**Persistence.** Shared-scoped state MUST be persisted to durable storage with the
same durability guarantees as agent-scoped state. Loss of shared state is particularly
impactful because it affects multiple agents' workflows.

**Compliance obligations.** Shared-scoped state carries the same compliance
obligations as agent-scoped state (retention, audit, data residency), with the
following additions:

1. **Grant audit.** When `audit_required` is `true`, the creation, modification, and
   revocation of grants on shared-scoped entries MUST generate audit events. The grant
   audit event MUST include: the grant ID, the key pattern, the grantee agent ID, the
   access level, the granting agent ID, and a timestamp. This is necessary to maintain
   a complete access trail for regulatory inspection.

2. **Cross-agent PII.** When a shared entry has `pii_classification` of `"personal"`,
   `"sensitive"`, or `"pseudonymised"`, the GDPR Art. 30 records of processing activities (§5.1) MUST
   include all grantee agents as recipients of the personal data. This means that
   granting access to personal data creates a new processing relationship that must be
   documented.

**Example uses.**

- Shared context between a risk assessment agent and a compliance checking agent in a
  MiFID II workflow.
- Common knowledge base shared across a team of specialised agents.
- Cross-agent session state for multi-agent collaboration patterns.
- Shared configuration for agents operated by the same organisation.

### 1.4 Global Scope

**Purpose.** Global-scoped state is read-only ambient context available to all agents
in a deployment. Global state serves as a shared reference layer — it contains data
that all agents may need but that no individual agent owns or controls. Global state
is managed by the platform operator, not by agents.

**Lifetime.** Global state is managed entirely by the platform operator. Agents MUST
NOT create, modify, or delete global-scoped entries through the ARSIA State operations.
The platform operator creates and maintains global state through administrative
channels outside the scope of this specification. Global entries persist until the
platform operator removes them.

**Visibility.** All agents in the deployment MAY read global-scoped entries. No agent
MAY write to global-scoped entries through ARSIA State operations. Global state is
inherently read-only from the perspective of ARSIA agents.

**Persistence.** Platform-managed. The platform operator is responsible for ensuring
appropriate durability, availability, and consistency of global state. The ARSIA
protocol does not prescribe persistence requirements for global state beyond requiring
that it be available for reading by all agents.

**Compliance obligations.** The platform operator is responsible for all compliance
obligations related to global state, including:

1. **Retention and residency.** The platform operator MUST ensure that global state
   entries comply with applicable retention and data residency requirements. ARSIA
   agents treat global state as external reference data and are not responsible for
   its compliance posture.

2. **PII.** Global state SHOULD NOT contain personal data. If global state must
   contain personal or pseudonymised data (which is NOT RECOMMENDED), the platform
   operator bears full GDPR responsibility. Global entries that contain personal data
   MUST have `pii_classification` set to `"personal"`, `"sensitive"`, or
   `"pseudonymised"` so that consuming agents can apply appropriate handling.

3. **Audit.** Read operations on global state do not generate audit events unless the
   consuming agent's compliance profile requires auditing of all data access. The
   platform operator is responsible for auditing modifications to global state through
   administrative channels.

**Example uses.**

- Market data feeds (e.g., real-time currency exchange rates, stock prices).
- Regulatory lookup tables (e.g., EU AI Act Annex III high-risk categories).
- Compliance profile definitions (the canonical set of profiles available in this
  deployment).
- Geographic zone definitions for data residency enforcement.
- Platform-wide configuration (rate limits, feature flags, maintenance windows).

### 1.5 Scope Summary

The following table summarises the four scopes:

| Property             | Session              | Agent                | Shared               | Global               |
|----------------------|----------------------|----------------------|----------------------|----------------------|
| **Creator**          | Any agent            | Owning agent         | Owning agent         | Platform operator    |
| **Writable by**      | Participating agents | Owning agent         | Owner + grantees     | Platform operator    |
| **Readable by**      | Participating agents | Owning agent         | Owner + grantees     | All agents           |
| **Persistence**      | Volatile (memory)    | Durable              | Durable              | Platform-managed     |
| **Max lifetime**     | Session duration     | Until deleted/expired| Until deleted/expired| Platform-managed     |
| **Retention**        | None                 | Profile-governed     | Profile-governed     | Operator-governed    |
| **Audit required**   | Never                | If profile says so   | If profile says so   | Operator-managed     |
| **Data residency**   | N/A                  | If set               | If set               | Operator-managed     |
| **PII allowed**      | Yes (ephemeral)      | Yes                  | Yes                  | Not recommended      |

---

## 2. State Entry Format

### 2.1 StateEntry Object

A StateEntry is the fundamental unit of state in the ARSIA Protocol. It is a JSON
object that contains the stored data, its metadata, and its compliance context. Every
state operation (§3) reads, writes, or queries StateEntry objects.

The StateEntry object contains the following fields:

#### 2.1.1 `key` — Entry Key

- **Type:** string
- **REQUIRED.**
- **Format:** Namespaced key in the format `{agent-id}/{scope}/{local-key}`.
- **Pattern:** `^[a-zA-Z0-9:._/\-]+$`
- **Maximum length:** 512 characters.
- **Constraints:** The key is the globally unique identifier for a state entry within
  a deployment. The namespaced format ensures that entries from different agents and
  scopes cannot collide.

  The key consists of three segments separated by forward slashes:

  1. **Agent identifier prefix.** The `agent-id` of the owning agent, as defined in
     ARSIA-Core.md §3. This prefix ensures that an agent can only create entries under
     its own namespace. Implementations MUST reject SET operations where the agent-id
     prefix in the key does not match the `from` field of the request message.

  2. **Scope segment.** One of `"session"`, `"agent"`, `"shared"`, or `"global"`.
     This segment MUST match the entry's `scope` field.

  3. **Local key.** An application-defined identifier for the specific data item. The
     local key MAY contain additional forward slashes to create a hierarchical
     structure (e.g., `mifid/client-profile/12345`).

  Examples:

  ```
  agent:acme.billing/agent/client-preferences
  agent:acme.billing/session/corr-550e8400/temp-calc
  agent:acme.billing/shared/risk-context-2026Q1
  agent:acme.billing/agent/mifid/client-profile/PT501234567
  ```

  For session-scoped entries, the local key SHOULD include the `correlation_id` (or a
  derivative) of the originating request to ensure uniqueness across concurrent
  sessions:

  ```
  agent:acme.billing/session/{correlation_id}/step-1-result
  ```

  For global-scoped entries, the agent-id prefix SHOULD be the platform operator's
  agent-id or a reserved platform identifier:

  ```
  agent:platform.operator/global/exchange-rates/EUR-USD
  agent:platform.operator/global/compliance-profiles/EU-AI-ACT-HIGH-RISK
  ```

#### 2.1.2 `value` — Entry Value

- **Type:** Any valid JSON value (object, array, string, number, boolean, or null).
- **REQUIRED** for SET operations. Present in GET and QUERY responses. Absent in
  DELETE and PURGE responses.
- **Maximum serialized size:** 1,048,576 bytes (1 MiB) when serialized to a UTF-8
  JSON string.
- **Constraints:** The value is the stored data. It is opaque to the ARSIA protocol —
  the protocol does not interpret, validate, or transform the value in any way. The
  semantics of the value are entirely application-defined. Implementations MUST store
  and return the value exactly as provided, preserving JSON type fidelity (e.g., a
  number stored as `1.0` MUST NOT be returned as `1` if the original serialization
  included the decimal point — however, implementations MAY normalize numbers per
  standard JSON parsing rules).

  Implementations MUST reject SET operations where the serialized value exceeds the
  maximum size with error code `payload_too_large` (ARSIA-Core.md §11.2).

  For entries with `pii_classification` of `"personal"`, `"sensitive"`, or
  `"pseudonymised"`, implementations SHOULD encrypt the value at rest (§10.4). The encryption is
  transparent to the ARSIA protocol — the value is encrypted in the storage layer and
  decrypted on read, with no impact on the StateEntry structure visible to agents.

#### 2.1.3 `owner_agent_id` — Owner Agent Identifier

- **Type:** string
- **REQUIRED.**
- **Format:** Agent identifier as defined in ARSIA-Core.md §3.
- **Constraints:** The `owner_agent_id` identifies the agent that created this entry.
  This field is set by the implementation when the entry is first created and is
  immutable thereafter — it MUST NOT be changed by any operation, including SET
  updates.

  Ownership determines access control: only the owning agent (or agents with active
  grants) may access the entry. Ownership also determines compliance responsibility:
  the owning agent's IdentityRecord (ARSIA-Identity.md §1.2) provides the legal
  entity information required for GDPR Art. 30 records.

  For global-scoped entries, `owner_agent_id` is the platform operator's agent
  identifier.

#### 2.1.4 `scope` — Entry Scope

- **Type:** string
- **REQUIRED.**
- **Allowed values:** `"session"`, `"agent"`, `"shared"`, `"global"`
- **Constraints:** The scope determines the lifecycle, visibility, and compliance
  obligations of the entry, as defined in §1. The scope MUST match the scope segment
  of the entry's key (§2.1.1). The scope is immutable after creation — it MUST NOT be
  changed by any operation.

#### 2.1.5 `created_at` — Creation Timestamp

- **Type:** string
- **REQUIRED.**
- **Format:** RFC 3339 date-time with millisecond precision and UTC timezone
  designator.
- **Pattern:** `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$`
- **Constraints:** The timestamp of when this entry was first created. Set by the
  implementation at creation time and immutable thereafter. Used as the baseline for
  retention period calculation (§4.1).

#### 2.1.6 `updated_at` — Last Modification Timestamp

- **Type:** string
- **REQUIRED.**
- **Format:** RFC 3339 date-time with millisecond precision and UTC timezone
  designator.
- **Pattern:** `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$`
- **Constraints:** The timestamp of the most recent modification to this entry. For
  newly created entries, `updated_at` equals `created_at`. Updated by the
  implementation on every SET operation that modifies the entry.

#### 2.1.7 `expires_at` — Expiry Timestamp

- **Type:** string
- **OPTIONAL.**
- **Format:** RFC 3339 date-time with millisecond precision and UTC timezone
  designator.
- **Pattern:** `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$`
- **Constraints:** The explicit expiry timestamp for this entry. After this timestamp,
  the entry MAY be garbage-collected by the implementation, subject to the following
  rules:

  1. If the entry has an effective retention period (from `retention_days` or the
     compliance profile), the entry MUST NOT be removed until BOTH the `expires_at`
     timestamp has passed AND the retention period (measured from `created_at`) has
     elapsed.

  2. If `expires_at` is `null` (not set), the entry's lifecycle is governed solely by
     the retention period from the compliance profile. If neither `expires_at` nor a
     compliance profile retention period applies, the entry persists indefinitely until
     explicitly deleted.

  3. For session-scoped entries, `expires_at` SHOULD be set to the `expires_at` value
     of the originating request message or the session timeout, whichever is earlier.

  4. Expired entries MUST NOT be returned by GET or QUERY operations. Expired entries
     MAY be returned by SNAPSHOT operations (§3.2) if they existed at the requested
     point in time and the retention period has not elapsed.

#### 2.1.8 `retention_days` — Retention Override

- **Type:** integer
- **OPTIONAL.**
- **Minimum value:** 1
- **Constraints:** An explicit retention period in days for this specific entry,
  overriding the compliance profile's default retention. The effective retention
  period is calculated as follows:

  ```
  effective_retention = max(
    entry.retention_days ?? 0,
    compliance_profile.retention_days ?? 0
  )
  ```

  The effective retention MUST NOT be less than the compliance profile's minimum.
  Setting `retention_days` on an individual entry can EXTEND retention beyond the
  profile minimum but MUST NOT REDUCE it below the profile minimum.

  Retention is measured from `created_at`. An entry is "within retention" when:

  ```
  now < created_at + (effective_retention * 86400 seconds)
  ```

  Entries within retention MUST NOT be physically deleted, except via PURGE for GDPR
  erasure (§5.3).

#### 2.1.9 `data_residency` — Data Residency Zone

- **Type:** string
- **OPTIONAL.**
- **Format:** ISO 3166-1 alpha-2 country code or supranational identifier (e.g.,
  `"EU"`, `"PT"`, `"DE"`, `"US"`).
- **Constraints:** The geographic zone where this entry MUST be stored. When set, the
  storage backend for this entry MUST physically reside within the declared zone. See
  §4.2 for the complete enforcement rules.

  If `data_residency` is not set on the entry, it is inherited from the
  `compliance.data_residency` field of the message envelope that created or last
  modified the entry. If neither the entry nor the compliance envelope specifies data
  residency, no geographic constraint applies.

#### 2.1.10 `pii_classification` — PII Classification

- **Type:** string
- **REQUIRED.**
- **Allowed values:** `"none"`, `"pseudonymised"`, `"personal"`, `"sensitive"`
- **Constraints:** The classification of the data in this entry for GDPR purposes.
  This field determines the compliance obligations that apply to the entry:

  **`"none"`** — The entry does not contain personal data. No GDPR-specific
  obligations apply beyond standard retention and residency rules. This is the
  default classification and SHOULD be used for all non-personal data.

  **`"pseudonymised"`** — The entry contains personal data that has been
  pseudonymised as defined in GDPR Art. 4(5). Pseudonymised data is still personal
  data under GDPR and is subject to GDPR obligations, but the reduced identifiability
  may affect the risk assessment. Pseudonymised entries MUST still comply with data
  residency requirements and retention policies. Implementations SHOULD encrypt
  pseudonymised data at rest.

  **`"personal"`** — The entry directly identifies or can be used to identify a
  natural person. This is the highest classification and triggers the full set of GDPR
  obligations:

  1. The `compliance.legal_basis` field MUST be set in the message envelope that
     creates or updates this entry (§5.2). SET operations for `"personal"` entries
     without a legal basis MUST be rejected.
  2. `data_residency` MUST be set (either on the entry or inherited from the
     compliance profile). Personal data without a declared residency zone is a
     compliance risk. Implementations SHOULD warn when personal data is stored
     without an explicit residency constraint, though this is not a hard rejection
     to accommodate transitional deployments.
  3. The entry is subject to the right to erasure via PURGE (§5.3).
  4. The entry MUST be included in GDPR Art. 30 records of processing activities
     (§5.1).
  5. Implementations MUST encrypt personal data at rest (§10.4).

  **`"sensitive"`** — The entry contains special category data as defined in GDPR
  Art. 9(1): data revealing racial or ethnic origin, political opinions, religious or
  philosophical beliefs, trade union membership, genetic data, biometric data for
  identification, data concerning health, or data concerning sex life or sexual
  orientation. All obligations of `"personal"` apply, plus:

  1. The `compliance.legal_basis` MUST be one of the Art. 9(2) grounds (see
     Core §4.3.6.8). Art. 6(1) grounds are insufficient for special category data.
  2. The `pii_special_categories` field MUST be present and contain at least one
     category value (§2.1.11).
  3. Implementations MUST encrypt sensitive data at rest.
  4. The entry is subject to stricter access control — implementations SHOULD restrict
     read access to agents with explicit authorization for the specific category of
     sensitive data.

  The `pii_classification` field is immutable within a single version of an entry.
  To change the classification, the agent MUST issue a new SET operation that creates
  a new version with the updated classification. This ensures that the compliance
  context of each version is unambiguous.

#### 2.1.11 `pii_special_categories` — Special Category Types

- **Type:** array of strings
- **REQUIRED** when `pii_classification` is `"sensitive"`. MUST NOT be present when
  `pii_classification` is not `"sensitive"`.
- **Allowed values:** `"health"`, `"biometric"`, `"genetic"`, `"racial_ethnic"`,
  `"political"`, `"religious"`, `"trade_union"`, `"sexual_orientation"`
- **Constraints:** MUST contain at least one value. Values are drawn from GDPR
  Art. 9(1). This field enables implementations to populate GDPR Art. 30 records of
  processing activities with the specific categories of special data processed.

#### 2.1.12 `version` — Entry Version

- **Type:** integer
- **Minimum value:** 1
- **Set by:** Implementation (not by the agent).
- **Constraints:** The version number provides optimistic concurrency control for
  state entries. The version is set to `1` when the entry is first created and is
  incremented by `1` on every successful SET operation that modifies the entry.

  The version number is used in conjunction with the `expected_version` parameter
  of the SET operation (§3.1) to detect concurrent modifications. When a SET request
  includes `expected_version`, the implementation MUST verify that the current
  version of the entry equals `expected_version` before applying the modification.
  If the versions do not match, the SET MUST fail with error code `"conflict"`
  (§8.4).

  The version number is monotonically increasing and MUST NOT be reset, even if the
  entry is deleted and recreated with the same key. When an entry is deleted via
  DELETE (§3.1) and subsequently recreated via SET, the new entry starts with
  version `1` — but the implementation MUST retain the version history of the
  deleted entry for SNAPSHOT purposes (§3.2) if the compliance profile requires
  temporal storage.

#### 2.1.13 `deleted` — Deletion Flag

- **Type:** boolean
- **Set by:** Implementation.
- **Constraints:** When `true`, the entry has been logically deleted via the DELETE
  operation (§3.1). Logically deleted entries are not returned by GET or QUERY
  operations but MAY be returned by SNAPSHOT operations if requested for a point in
  time when the entry was still active. The `deleted` flag is set by the
  implementation when a DELETE operation is processed and MUST NOT be set directly
  by agents.

  Logically deleted entries remain in storage for the duration of their effective
  retention period, available for audit and SNAPSHOT purposes. After the retention
  period expires, the implementation MAY physically remove the entry.

  The `deleted` field is OPTIONAL in the StateEntry representation returned to
  agents. Implementations SHOULD omit it from GET and QUERY responses (since those
  operations never return deleted entries). It is REQUIRED in SNAPSHOT responses
  when the entry was deleted at the requested point in time.

### 2.2 Key Naming Conventions

This section defines RECOMMENDED naming conventions for the local-key segment of
state entry keys. These conventions are not normative — agents MAY use any key format
that conforms to the pattern defined in §2.1.1 — but following them promotes
consistency and interoperability across ARSIA deployments.

#### General Rules

1. **Lowercase with hyphens.** Use lowercase letters and hyphens for word separation.
   Avoid camelCase, PascalCase, or underscores.

   RECOMMENDED: `client-preferences`
   NOT RECOMMENDED: `clientPreferences`, `client_preferences`

2. **Descriptive names.** Use descriptive, self-documenting names. Avoid abbreviations
   or opaque identifiers.

   RECOMMENDED: `risk-assessment-2026Q1`
   NOT RECOMMENDED: `ra1`

3. **Domain prefix.** For entries that relate to a specific regulatory framework or
   business domain, prefix the local key with the domain identifier.

   Examples:
   ```
   mifid/client-profile
   mifid/risk-assessment/2026Q1
   eu-ai-act/classification-history
   gdpr/consent-records/user-12345
   ```

4. **Temporal suffix.** For entries that are inherently temporal (e.g., assessments,
   snapshots, reports), include a date or period suffix.

   Examples:
   ```
   market-data/daily-summary/2026-03-24
   risk-report/quarterly/2026Q1
   ```

5. **Identifier inclusion.** When an entry relates to a specific external entity
   (e.g., a client, a transaction, a document), include the entity's identifier in
   the key.

   Examples:
   ```
   client/PT501234567/profile
   transaction/TX-2026-03-24-001/status
   ```

#### Reserved Prefix

The prefix `arsiaprotocol.` is reserved for protocol-managed state. Agents MUST NOT create
entries with local keys that start with `arsiaprotocol.` — these keys are used internally by
the implementation for grants (§3.3), metadata, and protocol-level bookkeeping.

Reserved key patterns include:

```
arsiaprotocol.grants/{grant-id}        — Grant records (§3.3)
arsia.meta/schema-version      — State schema version metadata
arsia.meta/migration-log       — Migration history
```

Implementations MUST reject SET operations from agents that attempt to write to keys
with the `arsiaprotocol.` prefix, with error code `"forbidden"`.

> **Note (informative).** This restriction applies to agent-initiated SET operations
> received via the protocol. Internal implementation storage (grant management per
> §3.3.1, audit records per §7.1) MAY use the `arsiaprotocol.` prefix for
> system-managed keys.

### 2.3 Value Constraints

The `value` field of a StateEntry is opaque to the ARSIA protocol. However, the
following constraints apply:

1. **JSON validity.** The value MUST be a valid JSON value per [RFC 8259]. Binary data
   MUST be base64-encoded before storage. Implementations MUST NOT accept non-JSON
   values.

2. **Size limit.** The serialized JSON representation of the value MUST NOT exceed
   1,048,576 bytes (1 MiB). This limit applies to the `value` field alone, not to the
   entire StateEntry. For larger data, agents SHOULD use the reference pattern: store
   the data externally (e.g., in object storage) and store a reference (URL, path, or
   identifier) in the StateEntry value.

3. **No executable content.** Values MUST NOT contain executable code (JavaScript,
   Python, shell commands, etc.) that is intended to be evaluated by the receiving
   agent. Values are data, not instructions. Agents that interpret value contents as
   executable code are responsible for sandboxing and security — the ARSIA protocol
   provides no protection against code injection via state values.

4. **Encoding.** All string values within the JSON MUST be valid UTF-8. Implementations
   MUST reject values containing invalid UTF-8 sequences.

### 2.4 Version Semantics

The version field provides an optimistic concurrency control mechanism that allows
agents to detect and handle concurrent modifications without distributed locks.

#### Version Lifecycle

1. **Creation.** When a new entry is created via SET, the version is set to `1`.

2. **Update.** Each subsequent SET on the same key increments the version by exactly
   `1`. The version after the Nth successful SET is `N`.

3. **Deletion.** A DELETE operation does not change the version — the entry retains
   its last version number. The `deleted` flag is set to `true`.

4. **Recreation.** If a deleted key is recreated via SET, the new entry starts at
   version `1`. The previous version history is retained in the temporal store for
   SNAPSHOT purposes.

#### Optimistic Concurrency Control

The `expected_version` parameter on the SET operation (§3.1) enables optimistic
concurrency control:

1. Agent A reads an entry and observes `version: 3`.
2. Agent A sends a SET with `expected_version: 3` and a new value.
3. If no other agent has modified the entry since Agent A's read, the entry is at
   version 3, the SET succeeds, and the new version is `4`.
4. If another agent has modified the entry (version is now `4` or higher), the SET
   fails with error code `"conflict"`. Agent A must re-read the entry, resolve the
   conflict, and retry.

The `expected_version` parameter is OPTIONAL. When omitted, the SET operation is
unconditional — it overwrites the current value regardless of concurrent
modifications. Unconditional SET is appropriate when the agent is the sole writer
for a key or when last-write-wins semantics are acceptable.

#### Version History

Implementations that support the SNAPSHOT operation (§3.2) MUST retain historical
versions of entries for the duration of the effective retention period. Each version
MUST be associated with:

- The version number.
- The value at that version.
- The `updated_at` timestamp of that version.
- The agent that performed the write.

This version history forms the temporal dimension of the state store and enables
point-in-time queries.

---

## 3. State Operations

State operations are expressed as standard ARSIA messages. Each operation is a
request/response pair using the message envelope defined in ARSIA-Core.md §4. This
means state operations benefit from all ARSIA primitives: digital signatures
(ARSIA-Core.md §5), capability enforcement (ARSIA-Core.md §6.4), compliance metadata
(ARSIA-Core.md §4.3.6), and audit trail generation (§7).

The target agent for state operations is the agent (or service) that implements the
state store. This may be the agent itself (if it implements its own state backend),
a dedicated state service agent within the deployment, or any ARSIA-conformant agent
that advertises state capabilities. The ARSIA protocol does not prescribe the
deployment topology — it defines only the message interface.

All state operations require appropriate capabilities in the sender's access token
(ARSIA-Core.md §6.1). The capability model is defined in §8.2.

### 3.1 Core Operations

#### 3.1.1 GET — Retrieve a State Entry

The GET operation retrieves a single state entry by its key.

**Request message:**

| Field                | Value                                   |
|----------------------|-----------------------------------------|
| `intent`             | `"request"`                             |
| `capabilities`       | `["arsiaprotocol.state.read"]`                  |
| `payload.type`       | `"arsiaprotocol.state/get"`                     |
| `payload.args`       | `{ "key": "{entry-key}" }`              |

The `key` field in `payload.args` MUST be the full namespaced key of the entry to
retrieve (§2.1.1).

**Response message (entry found):**

| Field                | Value                                   |
|----------------------|-----------------------------------------|
| `intent`             | `"response"`                            |
| `correlation_id`     | `{id of the request message}`           |
| `payload.type`       | `"arsiaprotocol.state/get"`                     |
| `payload.result`     | `{StateEntry object}`                   |

The `payload.result` contains the complete StateEntry object as defined in §2.1.

**Response message (entry not found):**

| Field                | Value                                   |
|----------------------|-----------------------------------------|
| `intent`             | `"response"`                            |
| `correlation_id`     | `{id of the request message}`           |
| `payload.type`       | `"arsiaprotocol.state/get"`                     |
| `payload.result`     | `null`                                  |

A `null` result indicates that the key does not exist, has been logically deleted,
or has expired. The response does not distinguish between these cases — from the
caller's perspective, the entry is simply not available.

**Access control:**

- The requesting agent MUST have the `arsiaprotocol.state.read` capability in its access
  token.
- The requesting agent MUST be either: (a) the owning agent of the entry, or (b) an
  agent with an active grant (§3.3) that covers the requested key.
- For global-scoped entries, all agents with `arsiaprotocol.state.read` are permitted to read.
- For session-scoped entries, the requesting agent MUST be one of the two agents in
  the session (the `from` or `to` of the originating request).
- If access is denied, the implementation MUST return an error with code `"forbidden"`.

**Audit:**

GET operations do not generate audit events under normal compliance profiles. However,
implementations MAY generate audit events for GET operations if the compliance profile
or deployment configuration explicitly requires read-level auditing.

#### 3.1.2 SET — Create or Update a State Entry

The SET operation creates a new state entry or updates an existing one.

**Request message:**

| Field                | Value                                   |
|----------------------|-----------------------------------------|
| `intent`             | `"request"`                             |
| `capabilities`       | `["arsiaprotocol.state.write"]`                 |
| `payload.type`       | `"arsiaprotocol.state/set"`                     |
| `payload.args`       | See below                               |

The `payload.args` object for SET contains:

| Field                | Type     | Required    | Description                                |
|----------------------|----------|-------------|--------------------------------------------|
| `key`                | string   | REQUIRED    | Full namespaced key (§2.1.1).              |
| `value`              | any JSON | REQUIRED    | The data to store.                          |
| `scope`              | string   | REQUIRED    | One of: `"session"`, `"agent"`, `"shared"`. |
| `pii_classification` | string   | REQUIRED    | One of: `"none"`, `"pseudonymised"`, `"personal"`, `"sensitive"`. |
| `expires_at`         | string   | OPTIONAL    | RFC 3339 expiry timestamp.                  |
| `retention_days`     | integer  | OPTIONAL    | Retention period override (minimum 1).     |
| `data_residency`     | string   | OPTIONAL    | ISO 3166 zone override.                    |
| `expected_version`   | integer  | OPTIONAL    | For optimistic concurrency control.        |

The `scope` field MUST NOT be `"global"` — agents cannot create global-scoped entries
through the SET operation. Attempting to SET a global-scoped entry MUST result in an
error with code `"forbidden"`.

**Response message (success):**

| Field                | Value                                   |
|----------------------|-----------------------------------------|
| `intent`             | `"response"`                            |
| `correlation_id`     | `{id of the request message}`           |
| `payload.type`       | `"arsiaprotocol.state/set"`                     |
| `payload.result`     | `{StateEntry object}`                   |

The `payload.result` contains the complete StateEntry after the SET operation,
including the updated `version`, `updated_at`, and any implementation-set fields.

**Validation rules:**

1. The agent-id prefix of the `key` MUST match the `from` field of the request
   message. An agent can only write to its own namespace.

2. The `scope` segment of the `key` MUST match the `scope` field in `payload.args`.

3. If `pii_classification` is `"personal"` or `"sensitive"`, the compliance envelope
   of the request message MUST contain `legal_basis`. If `legal_basis` is missing, the
   SET MUST be rejected with error code `"invalid_request"` and details
   `{ "missing_legal_basis": true }`. For `"sensitive"` entries, the `legal_basis`
   MUST additionally be an Art. 9(2) ground (Core §4.3.8, Rule 8).

4. If `expected_version` is set and does not match the current version of the entry,
   the SET MUST be rejected with error code `"conflict"` and details
   `{ "current_version": {N}, "expected_version": {M} }`.

5. If `data_residency` is set and the implementation cannot store the entry in the
   declared zone, the SET MUST be rejected with error code `"invalid_request"` and
   details `{ "data_residency_violation": true, "required_zone": "{zone}" }`.

6. If the serialized `value` exceeds 1,048,576 bytes, the SET MUST be rejected with
   error code `"payload_too_large"`.

**Behaviour on create vs. update:**

- If the key does not exist (or has been logically deleted), SET creates a new entry
  with `version: 1`, `created_at` set to the current time, and `updated_at` equal to
  `created_at`.
- If the key exists and is not deleted, SET updates the entry: increments `version`,
  sets `updated_at` to the current time, and replaces the `value`. The `created_at`,
  `owner_agent_id`, and `scope` fields are NOT modified.
- If the key exists but the `scope` in the request differs from the existing entry's
  scope, the SET MUST be rejected with error code `"invalid_request"` and details
  `{ "scope_mismatch": true, "existing_scope": "{scope}" }`.

**Audit:**

If `audit_required` is `true` in the compliance context, the SET operation MUST
generate an audit event of type `"state_set"` containing:

| Audit field          | Value                                   |
|----------------------|-----------------------------------------|
| `event_type`         | `"state_set"`                           |
| `key`                | The entry key.                          |
| `owner_agent_id`     | The owning agent.                       |
| `actor_agent_id`     | The agent that performed the SET.       |
| `version`            | The new version number.                 |
| `pii_classification` | The entry's PII classification.         |
| `timestamp`          | RFC 3339 timestamp of the operation.    |

The audit event MUST NOT include the entry's `value` unless the compliance profile
explicitly requires value-level auditing (which is NOT RECOMMENDED for entries with
`pii_classification` of `"personal"`, `"sensitive"`, or `"pseudonymised"`).

#### 3.1.3 DELETE — Logical Delete

The DELETE operation marks a state entry as logically deleted. The entry is no longer
returned by GET or QUERY operations but remains in storage for audit and SNAPSHOT
purposes until its retention period expires.

**Request message:**

| Field                | Value                                   |
|----------------------|-----------------------------------------|
| `intent`             | `"request"`                             |
| `capabilities`       | `["arsiaprotocol.state.write"]`                 |
| `payload.type`       | `"arsiaprotocol.state/delete"`                  |
| `payload.args`       | `{ "key": "{entry-key}" }`              |

**Response message (success):**

| Field                | Value                                   |
|----------------------|-----------------------------------------|
| `intent`             | `"response"`                            |
| `correlation_id`     | `{id of the request message}`           |
| `payload.type`       | `"arsiaprotocol.state/delete"`                  |
| `payload.result`     | `{ "deleted": true, "key": "{entry-key}" }` |

**Behaviour:**

1. The entry's `deleted` flag is set to `true`.
2. The entry's `updated_at` is set to the current time.
3. The entry's `version` is NOT incremented — deletion is not a value change.
4. The entry remains in storage, subject to its effective retention period.
5. Subsequent GET requests for the same key return `null`.
6. Subsequent SNAPSHOT requests for the same key at a point in time before the
   deletion return the entry with its last value and `deleted: false`.

**DELETE is fundamentally different from PURGE (§3.2):**

| Property             | DELETE                 | PURGE                  |
|----------------------|------------------------|------------------------|
| Type                 | Logical                | Physical               |
| Reversible           | Yes (via SNAPSHOT)     | No                     |
| Value retained       | Yes (for audit)        | No (permanently gone)  |
| Subject to retention | Yes                    | Overrides retention    |
| Audit event          | `"state_delete"`       | `"state_purge"`        |
| GDPR mechanism       | No                     | Yes (Art. 17)          |
| Required capability  | `arsiaprotocol.state.write`    | `arsiaprotocol.state.purge`    |

**Access control:**

- The requesting agent MUST be the owning agent of the entry.
- Grantees with `"read_write"` access MUST NOT be permitted to DELETE entries —
  DELETE is an owner-only operation.
- If the requesting agent is not the owner, the implementation MUST return an error
  with code `"forbidden"`.

**Retention protection:**

DELETE is a logical operation — it does not physically remove data. However,
implementations SHOULD respect the distinction between "the entry is logically
deleted and hidden from normal queries" and "the entry's data can be physically
removed." The physical removal of a logically deleted entry's data is governed by
the retention policy (§4.1).

If the entry is within its effective retention period:
- The logical delete succeeds (the entry is hidden from GET/QUERY).
- The entry's data MUST NOT be physically removed until the retention period expires.
- The entry remains available via SNAPSHOT.

If the entry is past its effective retention period:
- The logical delete succeeds.
- The implementation MAY physically remove the entry's data immediately.

**Audit:**

If `audit_required` is `true`, the DELETE operation MUST generate an audit event of
type `"state_delete"` containing:

| Audit field          | Value                                   |
|----------------------|-----------------------------------------|
| `event_type`         | `"state_delete"`                        |
| `key`                | The entry key.                          |
| `owner_agent_id`     | The owning agent.                       |
| `actor_agent_id`     | The agent that performed the DELETE.    |
| `version`            | The entry's version at time of deletion.|
| `timestamp`          | RFC 3339 timestamp of the operation.    |

#### 3.1.4 QUERY — Search State Entries

The QUERY operation searches state entries by filter criteria and returns a paginated
list of matching entries.

**Request message:**

| Field                | Value                                   |
|----------------------|-----------------------------------------|
| `intent`             | `"request"`                             |
| `capabilities`       | `["arsiaprotocol.state.read"]`                  |
| `payload.type`       | `"arsiaprotocol.state/query"`                   |
| `payload.args`       | See below                               |

The `payload.args` object for QUERY contains:

| Field                | Type     | Required    | Description                                |
|----------------------|----------|-------------|--------------------------------------------|
| `scope`              | string   | OPTIONAL    | Filter by scope.                           |
| `owner_agent_id`     | string   | OPTIONAL    | Filter by owning agent.                    |
| `key_prefix`         | string   | OPTIONAL    | Filter by key prefix (prefix match).       |
| `pii_classification` | string   | OPTIONAL    | Filter by PII classification.              |
| `created_after`      | string   | OPTIONAL    | RFC 3339 — entries created after this time.|
| `created_before`     | string   | OPTIONAL    | RFC 3339 — entries created before this time.|
| `limit`              | integer  | OPTIONAL    | Maximum entries to return. Default: 100. Maximum: 1000. |
| `offset`             | integer  | OPTIONAL    | Number of entries to skip. Default: 0.     |

All filter fields are combined with AND logic. When no filters are provided, the
query returns all entries accessible to the requesting agent.

**Response message:**

| Field                | Value                                   |
|----------------------|-----------------------------------------|
| `intent`             | `"response"`                            |
| `correlation_id`     | `{id of the request message}`           |
| `payload.type`       | `"arsiaprotocol.state/query"`                   |
| `payload.result`     | See below                               |

The `payload.result` object for QUERY contains:

| Field                | Type     | Description                                |
|----------------------|----------|--------------------------------------------|
| `entries`            | array    | Array of StateEntry objects matching the filters. |
| `total`              | integer  | Total number of matching entries (before pagination). |
| `limit`              | integer  | The limit used for this query.             |
| `offset`             | integer  | The offset used for this query.            |

**Access control:**

QUERY respects the same access control rules as GET:

- The requesting agent can only see entries it owns, entries it has grants for, and
  global-scoped entries.
- The implementation MUST NOT return entries that the requesting agent is not
  authorised to access, regardless of the filter criteria.
- If the requesting agent queries with `owner_agent_id` set to another agent's ID
  (without a grant covering the matching entries), the result MUST be empty — not an
  error.

**Ordering:**

Results MUST be ordered by `created_at` in ascending order (oldest first). This
provides deterministic pagination. Implementations MAY support additional ordering
options in future versions of this specification.

**Performance considerations:**

Implementations SHOULD optimise QUERY for the common case of prefix-based key
lookup. The `key_prefix` filter is expected to be the most frequently used filter
and SHOULD be indexed accordingly.

Implementations MUST enforce the maximum `limit` of 1000 entries per query. Requests
with `limit` exceeding 1000 MUST be clamped to 1000 — not rejected.

### 3.2 Compliance Operations

#### 3.2.1 SNAPSHOT — Point-in-Time State Retrieval

The SNAPSHOT operation retrieves state entries as they existed at a specific point in
time. SNAPSHOT is a compliance-oriented operation that enables regulatory inspection,
audit trail reconstruction, and historical analysis.

**Request message:**

| Field                | Value                                   |
|----------------------|-----------------------------------------|
| `intent`             | `"request"`                             |
| `capabilities`       | `["arsiaprotocol.state.snapshot"]`              |
| `payload.type`       | `"arsiaprotocol.state/snapshot"`                |
| `payload.args`       | See below                               |

The `payload.args` object for SNAPSHOT contains:

| Field                | Type     | Required    | Description                                |
|----------------------|----------|-------------|--------------------------------------------|
| `as_of`              | string   | REQUIRED    | RFC 3339 timestamp — the point in time to snapshot. |
| `filter`             | object   | OPTIONAL    | Same filter fields as QUERY (§3.1.4).      |

The `as_of` timestamp determines the temporal context of the snapshot. The
implementation MUST return entries as they existed at `as_of`, including:

- Entries that were active at `as_of` but have since been deleted or modified.
- The values and metadata of entries as they were at `as_of`, not their current state.
- Entries with `deleted: true` if they were deleted before `as_of` and the deletion
  occurred within the temporal window of the snapshot.

**Response message:**

| Field                | Value                                   |
|----------------------|-----------------------------------------|
| `intent`             | `"response"`                            |
| `correlation_id`     | `{id of the request message}`           |
| `payload.type`       | `"arsiaprotocol.state/snapshot"`                |
| `payload.result`     | See below                               |

The `payload.result` object for SNAPSHOT contains:

| Field                | Type     | Description                                |
|----------------------|----------|--------------------------------------------|
| `as_of`              | string   | The `as_of` timestamp from the request (echoed back). |
| `entries`            | array    | Array of StateEntry objects as they existed at `as_of`. |

**Temporal storage requirement:**

Implementations MUST support the SNAPSHOT operation if `audit_required` is `true` in
any compliance profile active in the deployment. Supporting SNAPSHOT requires temporal
storage — the ability to retain historical versions of entries and query them by
timestamp.

The temporal storage MUST retain historical versions for at least the effective
retention period of each entry. After the retention period expires, historical versions
MAY be purged from the temporal store.

Implementations that do not support SNAPSHOT MUST return error code
`"not_implemented"` with details `{ "feature": "temporal_storage" }` when a SNAPSHOT
request is received.

**Constraints on `as_of`:**

1. The `as_of` timestamp MUST NOT be in the future (beyond the clock skew tolerance
   of ±300 seconds per ARSIA-Core.md §8.3). Requests with a future `as_of` MUST be
   rejected with error code `"invalid_request"`.

2. The `as_of` timestamp MUST NOT predate the oldest retained version in the temporal
   store. If the requested point in time is older than the available history, the
   implementation MUST return an error with code `"invalid_request"` and details
   `{ "snapshot_unavailable": true, "oldest_available": "{RFC 3339 timestamp}" }`.

**Access control:**

SNAPSHOT requires the elevated `arsiaprotocol.state.snapshot` capability. This capability
is intended for audit, compliance, and regulatory inspection purposes. It MUST NOT
be included in wildcard capability grants (§8.2).

SNAPSHOT respects the same ownership and grant-based access control as GET and QUERY.
The requesting agent can only see historical versions of entries it is authorised to
access.

**Audit:**

SNAPSHOT operations SHOULD generate audit events when `audit_required` is `true`. The
audit event records that a temporal query was performed, which is relevant for
regulatory oversight (knowing who accessed historical data and when).

#### 3.2.2 PURGE — Physical Erasure

The PURGE operation permanently and irreversibly deletes a state entry and all of its
historical versions. PURGE is the ARSIA Protocol's mechanism for satisfying GDPR
Art. 17 (right to erasure).

**PURGE is fundamentally different from DELETE.** DELETE is a logical operation that
hides an entry from normal queries while retaining it for audit and compliance
purposes. PURGE is a physical operation that removes the entry's value from all
storage, including the temporal store. After a PURGE, the entry's value is
unrecoverable.

**Request message:**

| Field                | Value                                   |
|----------------------|-----------------------------------------|
| `intent`             | `"request"`                             |
| `capabilities`       | `["arsiaprotocol.state.purge"]`                 |
| `payload.type`       | `"arsiaprotocol.state/purge"`                   |
| `payload.args`       | `{ "key": "{entry-key}" }`              |

**Response message (success):**

| Field                | Value                                   |
|----------------------|-----------------------------------------|
| `intent`             | `"response"`                            |
| `correlation_id`     | `{id of the request message}`           |
| `payload.type`       | `"arsiaprotocol.state/purge"`                   |
| `payload.result`     | See below                               |

The `payload.result` object for PURGE contains:

| Field                | Type     | Description                                |
|----------------------|----------|--------------------------------------------|
| `purged`             | boolean  | Always `true` on success.                  |
| `key`                | string   | The key of the purged entry.               |
| `purged_at`          | string   | RFC 3339 timestamp of the purge operation. |

**Purge procedure (normative):**

The implementation MUST execute the following steps when processing a PURGE request:

1. **Validate access.** Verify that the requesting agent has the `arsiaprotocol.state.purge`
   capability and is the owning agent of the entry. If either check fails, reject the
   request with error code `"forbidden"`.

2. **Record the purge event.** Before deleting any data, create a PURGE audit event
   (see below). This event records THAT a purge occurred but MUST NOT contain the
   purged value.

3. **Delete the current entry value.** Remove the entry's `value` from the primary
   storage. The key, metadata fields (without the value), and the PURGE audit event
   are retained.

4. **Delete all historical versions.** Remove all historical values from the temporal
   store for this key. After this step, SNAPSHOT queries for this key at any point in
   time MUST return `null` for the entry's value.

5. **Propagate to replicas.** If the entry has been replicated (within the allowed
   data residency zone), initiate purge propagation to all replicas. Replicas SHOULD
   complete the purge within 24 hours. Full propagation, including backup media
   rotation, SHOULD complete within 30 days.

6. **Revoke grants.** If the entry has any active grants (§3.3), those grants MUST be
   automatically revoked as part of the PURGE operation. Grant revocation audit events
   MUST be generated for each revoked grant.

**Purge audit event:**

Every PURGE operation MUST generate an audit event, regardless of the compliance
profile's `audit_required` setting. PURGE audit events are always mandatory because
they serve the accountability requirement of GDPR Art. 5(2).

| Audit field          | Value                                   |
|----------------------|-----------------------------------------|
| `event_type`         | `"state_purge"`                         |
| `key`                | The key of the purged entry.            |
| `owner_agent_id`     | The owning agent of the purged entry.   |
| `initiator_agent_id` | The agent that requested the PURGE.     |
| `purged_at`          | RFC 3339 timestamp of the purge.        |
| `pii_classification` | The PII classification of the purged entry. |
| `reason`             | OPTIONAL — reason for the purge (e.g., `"gdpr_erasure"`, `"data_subject_request"`). |

**Critical constraint:** The PURGE audit event MUST NOT contain the purged value.
The entire purpose of PURGE is to erase the data — recording it in the audit event
would defeat that purpose. The audit event records the fact of erasure, not the
content that was erased.

**Retention override:**

PURGE overrides all retention policies. An entry that is within its retention period
(e.g., a MiFID II entry with 1827-day retention that is only 100 days old) CAN be
purged if GDPR erasure is required. The conflict between retention and erasure is
addressed in §5.3.

**Elevated capability:**

The `arsiaprotocol.state.purge` capability is elevated. It MUST NOT be included in wildcard
capability grants:

- `arsiaprotocol.state.*` grants `arsiaprotocol.state.read` + `arsiaprotocol.state.write` but does NOT
  grant `arsiaprotocol.state.purge`.
- `arsiaprotocol.state.purge` MUST be explicitly granted in the access token's scope.

This restriction exists because PURGE is an irreversible, destructive operation that
bypasses retention safeguards. It should be available only to agents that have been
specifically authorised for erasure operations.

**Idempotency:**

PURGE is idempotent. If a PURGE request is received for a key that has already been
purged, the implementation MUST return a successful response (not an error) with the
same `purged_at` timestamp as the original purge. A second PURGE on the same key
MUST NOT generate a second audit event.

### 3.3 Shared State Access Grants

Grants enable controlled sharing of agent-scoped state with other agents. The grant
mechanism provides fine-grained access control that is auditable, time-bounded, and
revocable.

#### 3.3.1 GRANT — Share State with Another Agent

The GRANT operation creates an access grant that allows another agent to read or
read-write specific state entries owned by the granting agent.

**Request message:**

| Field                | Value                                   |
|----------------------|-----------------------------------------|
| `intent`             | `"request"`                             |
| `capabilities`       | `["arsiaprotocol.state.write"]`                 |
| `payload.type`       | `"arsiaprotocol.state/grant"`                   |
| `payload.args`       | See below                               |

The `payload.args` object for GRANT contains:

| Field                | Type     | Required    | Description                                |
|----------------------|----------|-------------|--------------------------------------------|
| `key_pattern`        | string   | REQUIRED    | The key or key prefix to share.            |
| `grantee_agent_id`   | string   | REQUIRED    | Agent identifier of the recipient.         |
| `access_level`       | string   | REQUIRED    | `"read"` or `"read_write"`.                |
| `valid_until`        | string   | OPTIONAL    | RFC 3339 expiry timestamp for the grant. `null` means no expiry (revoke manually). |

**Key pattern semantics:**

The `key_pattern` field specifies which entries the grant covers. It supports two
matching modes:

1. **Exact match.** When the pattern does not end with `*`, it matches a single
   specific key.

   Example: `"agent:acme.billing/agent/risk-context-2026Q1"` — grants access to
   exactly that one key.

2. **Prefix match.** When the pattern ends with `*`, it matches all keys that start
   with the pattern (excluding the trailing `*`).

   Example: `"agent:acme.billing/agent/risk-*"` — grants access to all keys under
   the granting agent's namespace that start with `agent:acme.billing/agent/risk-`.

The pattern MUST start with the granting agent's agent-id prefix. An agent MUST NOT
grant access to keys it does not own. Implementations MUST reject GRANT requests
where the key pattern prefix does not match the `from` field of the request message.

**Response message:**

| Field                | Value                                   |
|----------------------|-----------------------------------------|
| `intent`             | `"response"`                            |
| `correlation_id`     | `{id of the request message}`           |
| `payload.type`       | `"arsiaprotocol.state/grant"`                   |
| `payload.result`     | See below                               |

The `payload.result` object for GRANT contains:

| Field                | Type     | Description                                |
|----------------------|----------|--------------------------------------------|
| `grant_id`           | string   | UUID v4 identifier for this grant.         |
| `key_pattern`        | string   | The key pattern (echoed from request).     |
| `grantee_agent_id`   | string   | The grantee agent (echoed from request).   |
| `access_level`       | string   | The access level (echoed from request).    |
| `valid_until`        | string   | The grant expiry (echoed from request, or `null`). |
| `created_at`         | string   | RFC 3339 timestamp of grant creation.      |

**Internal storage:**

Grants are stored internally as StateEntry objects in the granting agent's namespace
with scope `"agent"` and the reserved key prefix `arsiaprotocol.grants/`:

```
agent:acme.billing/agent/arsiaprotocol.grants/{grant-id}
```

The value of a grant entry is a JSON object containing the grant metadata (key
pattern, grantee, access level, valid_until, created_at). This storage model means
that grants are subject to the same durability and retention guarantees as any other
agent-scoped entry.

**Grant enforcement:**

When a grantee agent sends a state operation (GET, SET, QUERY) for an entry it does
not own, the implementation MUST verify that an active grant exists:

1. Find all grants from the entry's owner to the requesting agent.
2. For each grant, check if the entry's key matches the grant's `key_pattern` (exact
   or prefix match).
3. Verify that the grant's `access_level` permits the requested operation (e.g.,
   `"read"` permits GET but not SET).
4. Verify that the grant has not expired (`valid_until` is `null` or in the future).
5. If no matching active grant is found, reject the operation with error code
   `"forbidden"`.

Grant enforcement occurs at operation time, not at connection time. A grant that
expires between two operations within the same session will cause the second
operation to fail.

**Audit:**

If `audit_required` is `true`, GRANT operations MUST generate an audit event of type
`"state_grant"` containing:

| Audit field          | Value                                   |
|----------------------|-----------------------------------------|
| `event_type`         | `"state_grant"`                         |
| `grant_id`           | The UUID of the grant.                  |
| `key_pattern`        | The key pattern shared.                 |
| `grantor_agent_id`   | The agent that issued the grant.        |
| `grantee_agent_id`   | The agent that received the grant.      |
| `access_level`       | `"read"` or `"read_write"`.             |
| `valid_until`        | The grant expiry or `null`.             |
| `timestamp`          | RFC 3339 timestamp of the operation.    |

#### 3.3.2 REVOKE — Remove an Access Grant

The REVOKE operation removes a previously issued grant, immediately terminating the
grantee's access.

**Request message:**

| Field                | Value                                   |
|----------------------|-----------------------------------------|
| `intent`             | `"request"`                             |
| `capabilities`       | `["arsiaprotocol.state.write"]`                 |
| `payload.type`       | `"arsiaprotocol.state/revoke"`                  |
| `payload.args`       | `{ "grant_id": "{grant-uuid}" }`        |

**Response message (success):**

| Field                | Value                                   |
|----------------------|-----------------------------------------|
| `intent`             | `"response"`                            |
| `correlation_id`     | `{id of the request message}`           |
| `payload.type`       | `"arsiaprotocol.state/revoke"`                  |
| `payload.result`     | `{ "revoked": true, "grant_id": "{grant-uuid}" }` |

**Behaviour:**

1. Revocation is immediate. The grantee loses access on the next operation. Any
   in-flight operations that were initiated before the revocation but arrive after
   it MUST be rejected.

2. The grant entry in internal storage is logically deleted (not purged). The grant
   metadata remains available for audit purposes.

3. Revocation of a non-existent or already-revoked grant MUST return a successful
   response (idempotent). It MUST NOT generate a second revocation audit event.

**Access control:**

Only the grantor agent (the agent that issued the original GRANT) MAY revoke a grant.
Implementations MUST verify that the `from` field of the REVOKE request matches the
grantor of the specified grant. If the requesting agent is not the grantor, the
implementation MUST return an error with code `"forbidden"`.

**Audit:**

If `audit_required` is `true`, REVOKE operations MUST generate an audit event of type
`"state_revoke"` containing:

| Audit field          | Value                                   |
|----------------------|-----------------------------------------|
| `event_type`         | `"state_revoke"`                        |
| `grant_id`           | The UUID of the revoked grant.          |
| `grantor_agent_id`   | The agent that revoked the grant.       |
| `grantee_agent_id`   | The agent that lost access.             |
| `timestamp`          | RFC 3339 timestamp of the revocation.   |

### 3.4 Operation Summary

The following table summarises all state operations:

| Operation  | Payload type            | Capability              | Description                    |
|------------|------------------------|-------------------------|--------------------------------|
| GET        | `arsiaprotocol.state/get`      | `arsiaprotocol.state.read`      | Retrieve entry by key          |
| SET        | `arsiaprotocol.state/set`      | `arsiaprotocol.state.write`     | Create or update entry         |
| DELETE     | `arsiaprotocol.state/delete`   | `arsiaprotocol.state.write`     | Logical delete                 |
| QUERY      | `arsiaprotocol.state/query`    | `arsiaprotocol.state.read`      | Search entries by filter       |
| SNAPSHOT   | `arsiaprotocol.state/snapshot` | `arsiaprotocol.state.snapshot`  | Point-in-time retrieval        |
| PURGE      | `arsiaprotocol.state/purge`    | `arsiaprotocol.state.purge`     | Physical erasure (GDPR)        |
| GRANT      | `arsiaprotocol.state/grant`    | `arsiaprotocol.state.write`     | Share state with another agent |
| REVOKE     | `arsiaprotocol.state/revoke`   | `arsiaprotocol.state.write`     | Remove a shared access grant   |

---

## 4. Retention and Data Residency

### 4.1 Retention Policy

Retention policy determines how long state entries MUST be kept before they may be
physically removed. Retention is a compliance-critical concern: financial regulations
(MiFID II), AI governance regulations (EU AI Act), and general data protection
regulations (GDPR) all impose specific retention requirements that vary by regulation,
sector, and use case.

#### 4.1.1 Retention Hierarchy

The effective retention period for a state entry is determined by the following
hierarchy, from highest to lowest priority:

1. **Regulatory minimum.** The compliance profile's `retention_days` value sets the
   regulatory floor. This is the minimum retention required by the applicable
   regulation. The entry MUST NOT be physically deleted before this period expires,
   regardless of other settings.

2. **Entry-level override.** The `StateEntry.retention_days` field, if set, overrides
   the profile default — but only upward. The entry-level retention MUST NOT reduce
   retention below the regulatory minimum.

3. **Entry expiry.** The `StateEntry.expires_at` field sets an explicit expiry
   timestamp. The entry becomes eligible for removal when BOTH `expires_at` has
   passed AND the effective retention period has elapsed.

The effective retention is calculated as:

```
profile_retention   = compliance_profile.retention_days ?? 0
entry_retention     = state_entry.retention_days ?? 0
effective_retention = max(profile_retention, entry_retention)
```

The entry is "within retention" when:

```
now < state_entry.created_at + (effective_retention * 86400 seconds)
```

When the effective retention is zero (no compliance profile and no entry-level
retention), the entry has no minimum retention period and may be deleted at any time.

#### 4.1.2 Default Retention per Compliance Profile

The following retention defaults are defined for the standard ARSIA compliance
profiles. These values are normative for this specification and will be formally
defined in §6:

**GDPR-STANDARD:**

| Parameter              | Value                                  |
|------------------------|----------------------------------------|
| `retention_days`       | None (no mandatory minimum).           |
| Behaviour              | Entries expire per their `expires_at` field. If no `expires_at` is set, the platform-defined default applies. |
| RECOMMENDED default    | 90 days when no `expires_at` is set.   |
| Rationale              | GDPR Art. 5(1)(e) — storage limitation principle. Data should not be kept longer than necessary. |

**EU-AI-ACT-HIGH-RISK:**

| Parameter              | Value                                  |
|------------------------|----------------------------------------|
| `retention_days`       | 180                                    |
| Behaviour              | Entry data MUST NOT be physically removed before 180 days from creation. Logical deletion (§3.1.3) is permitted — it hides the entry from GET/QUERY but the data is retained in the temporal store. |
| Rationale              | EU AI Act Art. 26(6) — deployers of high-risk AI systems must keep automatically generated logs for a period appropriate to the intended purpose of the high-risk AI system, of at least six months. |
| Exception              | PURGE for GDPR erasure (§5.3) overrides the 180-day minimum. |

**MIFID-II:**

| Parameter              | Value                                  |
|------------------------|----------------------------------------|
| `retention_days`       | 1827 (5 years, accounts for leap years) |
| Behaviour              | Entry data MUST NOT be physically removed before 1827 days from creation. Logical deletion is permitted — data is retained in temporal store. |
| Rationale              | MiFID II Art. 16(7) — investment firms must keep records of all services, activities, and transactions for a minimum of five years. |
| Exception              | PURGE for GDPR erasure overrides, but the PURGE audit event itself is retained for the full 1827-day period. |

**PAC-AGRICULTURE:**

| Parameter              | Value                                  |
|------------------------|----------------------------------------|
| `retention_days`       | 1096 (3 years, accounts for leap years) |
| Behaviour              | Entry data MUST NOT be physically removed before 1096 days from creation. Logical deletion is permitted — data is retained in temporal store. |
| Rationale              | EU 2021/2116 Art. 60 — recovery of undue payments requires records for at least 3 years, covering the full cycle of payment verification and potential recovery actions. |
| Exception              | PURGE for GDPR erasure overrides.      |

**EU-AI-ACT-LIMITED-RISK:**

| Parameter              | Value                                  |
|------------------------|----------------------------------------|
| `retention_days`       | 90                                     |
| Behaviour              | Entry data MUST NOT be physically removed before 90 days from creation. Logical deletion is permitted — data is retained in temporal store. |
| Rationale              | EU AI Act Art. 50 does not prescribe a retention period. 90 days covers a reasonable compliance verification period for transparency obligations. |
| Exception              | PURGE for GDPR erasure overrides.      |

**DSA-VLOP:**

| Parameter              | Value                                  |
|------------------------|----------------------------------------|
| `retention_days`       | 730 (2 years)                          |
| Behaviour              | Entry data MUST NOT be physically removed before 730 days from creation. Logical deletion is permitted — data is retained in temporal store. |
| Rationale              | DSA Art. 37 — annual independent audit. 730 days covers two consecutive audit cycles, enabling cross-reference between risk assessments and verification of mitigation measures. |
| Exception              | PURGE for GDPR erasure overrides.      |

**DORA:**

| Parameter              | Value                                  |
|------------------------|----------------------------------------|
| `retention_days`       | 1827 (5 years, accounts for leap years) |
| Behaviour              | Entry data MUST NOT be physically removed before 1827 days from creation. Logical deletion is permitted — data is retained in temporal store. |
| Rationale              | DORA Art. 6(5) — annual ICT risk management review. 5 years aligns with European financial sector retention floors (CRD IV, Solvency II, IORP II) and covers at least 5 review cycles. |
| Exception              | PURGE for GDPR erasure overrides, but the PURGE audit event itself is retained for the full 1827-day period. |

#### 4.1.3 Post-Retention Lifecycle

After the effective retention period expires, the entry enters the post-retention
phase. The implementation MAY handle post-retention entries in one of two ways:

1. **Archival.** Move the entry to cold storage (lower-cost, higher-latency storage
   tier). Archived entries MUST remain available for regulatory inspection via the
   SNAPSHOT operation for an additional 12 months after archival. After the 12-month
   archival period, the entry MAY be permanently deleted.

2. **Deletion.** Permanently delete the entry. This is appropriate when no archival
   requirement applies and the entry has no further regulatory value.

Implementations MUST document their post-retention behaviour in their operational
documentation. Regulated deployments SHOULD prefer archival over immediate deletion
to provide a buffer for late-arriving regulatory requests.

#### 4.1.4 Retention and Logical Deletion

When an entry is logically deleted via the DELETE operation (§3.1.3) while still
within its retention period:

1. The entry is hidden from GET and QUERY operations (logical deletion takes effect
   immediately).
2. The entry's data MUST be retained in the temporal store for the remainder of the
   retention period.
3. The entry remains accessible via SNAPSHOT for the retention period.
4. After the retention period expires, the entry MAY be physically removed.

This means that logical deletion does not accelerate physical removal. An agent can
hide data from normal operations, but cannot circumvent regulatory retention
requirements through logical deletion.

### 4.2 Data Residency Enforcement

Data residency enforcement ensures that state entries are stored in the geographic
zone declared by the entry's `data_residency` field or the compliance profile's
`data_residency` field. This is a hard requirement: violating data residency is a
compliance failure.

#### 4.2.1 Residency Determination

The effective data residency for a state entry is determined as follows:

1. If `StateEntry.data_residency` is set, it takes precedence.
2. If not set, the `compliance.data_residency` from the message envelope that created
   or last modified the entry is used.
3. If neither is set, no geographic constraint applies.

When a data residency constraint is active:

1. **Storage location.** The storage backend for this entry MUST physically reside
   within the declared zone. "Physically reside" means that the primary storage
   location of the data is within the geographic boundaries of the zone. This
   includes all storage tiers: primary storage, replicas, backups, and WAL/journal
   files.

2. **Replication.** Cross-zone replication of the entry is PROHIBITED unless all
   replicas are within the declared zone. For example, an entry with
   `data_residency: "EU"` may be replicated between `eu-west-1` and `eu-central-1`,
   but MUST NOT be replicated to `us-east-1`.

3. **Processing.** The data MUST be processed (read, transformed, aggregated) within
   the declared zone. Processing the data outside the zone — even transiently —
   violates the residency constraint.

4. **Backup.** Backup copies of the data MUST be stored within the declared zone.
   Backup media that leaves the zone (e.g., for offsite disaster recovery) MUST be
   encrypted, and the encryption keys MUST be managed within the zone.

#### 4.2.2 Residency Verification

Implementations MUST provide a mechanism for operators and auditors to verify that
data residency constraints are enforced. The following verification approaches are
RECOMMENDED:

1. **Self-declaration.** The implementation documents its storage regions in its
   IdentityRecord (ARSIA-Identity.md §1.2) or its discovery metadata
   (ARSIA-Core.md §7.1). This is the minimum acceptable verification.

2. **Attestation.** For regulated deployments, SOC 2 Type II or equivalent third-party
   attestation covering the geographic scope of the storage infrastructure. This is
   RECOMMENDED for implementations that handle personal data under GDPR or financial
   data under MiFID II.

3. **Technical enforcement.** Infrastructure-level controls (e.g., cloud provider
   region pinning, network policies that prevent cross-region data transfer) that
   make residency violations technically impossible rather than merely policy-
   prohibited.

#### 4.2.3 Residency Violation Handling

If an implementation cannot honour a data residency constraint (because it does not
have storage infrastructure in the declared zone), it MUST reject the SET operation
with error code `"invalid_request"` and the following details:

```json
{
  "data_residency_violation": true,
  "required_zone": "EU",
  "available_zones": ["US", "AP"]
}
```

Implementations MUST NOT silently store data in the wrong zone. A clear, deterministic
failure is always preferable to a silent compliance violation.

### 4.3 Archival

Archival is the process of moving state entries from primary (hot) storage to
secondary (cold) storage after the initial retention period has passed but before
the data is permanently deleted.

#### 4.3.1 Archival Triggers

An entry becomes eligible for archival when:

1. The effective retention period has expired (§4.1.1).
2. The entry has not been accessed (GET, QUERY) for a configurable inactivity period.
   The RECOMMENDED inactivity threshold is equal to the effective retention period.

Implementations MAY archive entries proactively based on storage capacity or cost
constraints, even before the inactivity threshold is reached, as long as the entry
remains accessible via SNAPSHOT for the required archival period.

#### 4.3.2 Archival Guarantees

Archived entries MUST remain available for regulatory inspection via the SNAPSHOT
operation for an additional 12 months after the archival date. During this 12-month
archival period:

1. SNAPSHOT queries that include the archived entry's time range MUST return the
   entry.
2. The implementation MAY increase the response latency for archived entries (cold
   storage is expected to be slower).
3. The implementation SHOULD document the expected latency for archived entry access.

After the 12-month archival period, the entry MAY be permanently deleted.

#### 4.3.3 Archival and PURGE

PURGE (§3.2.2) overrides archival. When an entry is purged:

1. The entry's value MUST be removed from both primary and archival storage.
2. The archival record (if any) MUST be purged along with the primary record.
3. Only the PURGE audit event is retained.

---

## 5. GDPR Obligations

This section maps ARSIA State primitives to specific GDPR articles and defines the
normative requirements for implementations that process personal data. ARSIA provides
the protocol mechanisms — the operator bears the legal responsibility for GDPR
compliance.

### 5.1 Records of Processing Activities (Art. 30)

GDPR Art. 30 requires controllers to maintain a record of processing activities under
their responsibility. When state entries have `pii_classification` of `"personal"`,
`"sensitive"`, or `"pseudonymised"`, the ARSIA State primitive provides the raw data necessary to
populate Art. 30 records.

**Data elements available from ARSIA:**

| Art. 30 Requirement              | ARSIA Source                                       |
|----------------------------------|----------------------------------------------------|
| Controller identity              | `owner_agent_id` → IdentityRecord → `owner_id`, `owner_name` |
| Categories of data subjects      | Derivable from key naming conventions (§2.2) and application context |
| Categories of personal data      | `pii_classification` + key naming + application context |
| Purpose of processing            | `payload.type` of the message that created the entry |
| Categories of recipients         | Active grants on the entry (§3.3) → grantee agent IDs → IdentityRecords |
| Transfers to third countries     | `data_residency` + grantee jurisdictions (from IdentityRecords) |
| Retention period                 | `retention_days` or compliance profile default      |
| Security measures                | Encryption at rest (§10.4), access control (§10.1)   |

**Operator responsibility:** ARSIA provides the raw data elements listed above. The
operator MUST maintain the actual Art. 30 register — ARSIA does not generate the
register automatically. The operator is responsible for:

1. Aggregating the data elements from ARSIA into a coherent Art. 30 record.
2. Maintaining the register in the format required by their supervisory authority.
3. Making the register available to the supervisory authority on request.
4. Updating the register when processing activities change (e.g., when new grants
   are issued or revoked).

Implementations SHOULD provide tooling (reports, exports, APIs) that facilitate the
operator's Art. 30 compliance, but such tooling is outside the scope of this
specification.

### 5.2 Legal Basis (Art. 6)

GDPR Art. 6 requires that the processing of personal data has a lawful basis.
The ARSIA Protocol enforces this requirement through the `compliance.legal_basis`
field in the message envelope.

**Normative requirement:** When `pii_classification` is `"personal"` or `"sensitive"`
on a SET operation, the `compliance.legal_basis` field in the message envelope that
carries the SET request MUST be set. For `"personal"` entries, the basis MUST be one
of the following values, corresponding to GDPR Art. 6(1) sub-paragraphs:

| Value                    | GDPR Article | Description                          |
|--------------------------|-------------|--------------------------------------|
| `"consent"`              | Art. 6(1)(a) | Data subject has given consent.      |
| `"contract"`             | Art. 6(1)(b) | Necessary for contract performance.  |
| `"legal_obligation"`     | Art. 6(1)(c) | Necessary for a legal obligation.    |
| `"vital_interests"`      | Art. 6(1)(d) | Necessary to protect vital interests.|
| `"public_task"`          | Art. 6(1)(e) | Necessary for a public interest task.|
| `"legitimate_interests"` | Art. 6(1)(f) | Necessary for legitimate interests.  |

For `"sensitive"` entries, the basis MUST be one of the Art. 9(2) grounds defined in
Core §4.3.6.8: `"explicit_consent"`, `"employment_social_security"`,
`"vital_interests_incapacity"`, `"legitimate_activities"`, `"manifestly_public"`,
`"legal_claims"`, `"substantial_public_interest"`, `"health_medicine"`,
`"public_health"`, `"archiving_research"`. An Art. 6(1) ground is insufficient for
special category data and MUST be rejected (Core §4.3.8, Rule 8).

**Enforcement:** Implementations MUST reject SET operations for entries with
`pii_classification` of `"personal"` or `"sensitive"` when `compliance.legal_basis` is missing from
the message envelope. The error response MUST use error code `"invalid_request"` with
details:

```json
{
  "missing_legal_basis": true,
  "pii_classification": "personal",
  "message": "GDPR Art. 6 requires a legal basis for processing personal data."
}
```

**Legal basis for pseudonymised data:** The `legal_basis` requirement applies only
to entries with `pii_classification` of `"personal"`. Entries with
`pii_classification` of `"pseudonymised"` SHOULD include a legal basis but are not
required to. This reflects the reduced (but not eliminated) GDPR obligations for
pseudonymised data.

**Legal basis immutability:** The legal basis declared in the message envelope that
creates a state entry is recorded as part of the entry's compliance context. If the
legal basis for processing changes (e.g., a data subject withdraws consent), the
operator MUST either delete the entry or update it with a new SET that carries the
new legal basis.

### 5.3 Right to Erasure (Art. 17)

GDPR Art. 17 grants data subjects the right to obtain the erasure of personal data
concerning them without undue delay. The ARSIA PURGE operation (§3.2.2) is the
protocol-level mechanism for fulfilling this right.

#### 5.3.1 Erasure Procedure

The following procedure is normative for fulfilling a GDPR Art. 17 erasure request
through the ARSIA Protocol:

**Step 1: Request reception.** A data subject (or their representative) submits an
erasure request to the operator. The mechanism for receiving erasure requests is
outside the scope of this specification — it may be a web form, an email, a postal
letter, or any other channel the operator provides.

**Step 2: Identification.** The operator identifies all StateEntry objects that
contain the data subject's personal data. This may involve:

- Querying entries by `pii_classification` of `"personal"`.
- Searching entry values for identifiers associated with the data subject.
- Consulting the Art. 30 register to determine which processing activities involve
  the data subject's data.

The identification process is the operator's responsibility. ARSIA provides the QUERY
operation (§3.1.4) to facilitate this, but the operator must determine which entries
to purge.

**Step 3: Exception check.** The operator determines whether any exceptions under
GDPR Art. 17(3) apply. Exceptions include:

- (a) Exercise of the right of freedom of expression and information.
- (b) Compliance with a legal obligation.
- (c) Reasons of public interest in the area of public health.
- (d) Archiving purposes in the public interest, scientific or historical research,
  or statistical purposes.
- (e) Establishment, exercise, or defence of legal claims.

If an exception applies, the operator MAY decline the erasure request (in whole or
in part) and MUST inform the data subject of the grounds for refusal.

**Step 4: PURGE execution.** For each identified entry where no exception applies,
the operator issues a PURGE request (§3.2.2). The PURGE operation physically deletes
the entry's value from all storage, including the temporal store.

**Step 5: Backup propagation.** The implementation SHOULD complete purge propagation
to backup media within 30 days (RECOMMENDED). This timeline accounts for normal
backup rotation cycles. The operator MUST document the expected backup propagation
timeline and communicate it to the data subject if requested.

**Step 6: Confirmation.** The operator confirms the erasure to the data subject. The
operator may reference the PURGE audit events as evidence of erasure.

#### 5.3.2 Conflict: Erasure vs. Retention

GDPR Art. 17 erasure may conflict with regulatory retention requirements (e.g.,
MiFID II 5-year retention). This conflict is a well-known tension in European
regulatory compliance. The ARSIA Protocol handles this conflict as follows:

**Protocol position:** ARSIA provides the PURGE mechanism but does not adjudicate the
legal conflict. The operator MUST make the legal determination based on the specific
circumstances.

**Practical guidance (informative):**

1. **GDPR generally prevails over retention** when the data subject's erasure right
   is not overridden by one of the Art. 17(3) exceptions. However, Art. 17(3)(b)
   ("compliance with a legal obligation which requires processing by Union or Member
   State law to which the controller is subject") may itself provide a basis for
   retaining the data.

2. **For MiFID II:** Art. 16(7) retention is a legal obligation under Art. 17(3)(b).
   An operator MAY argue that MiFID II retention takes precedence and decline erasure.
   However, the operator SHOULD consider pseudonymisation as an alternative that
   satisfies both requirements: pseudonymise the data (removing direct identifiers)
   to satisfy the spirit of the erasure request while retaining the pseudonymised
   record to satisfy MiFID II retention.

3. **For EU AI Act:** Art. 26(6) logging requirements may also constitute a legal
   obligation under Art. 17(3)(b). The same pseudonymisation approach applies.

4. **When erasure proceeds despite retention:** If the operator determines that
   erasure prevails, the PURGE operation is executed. The PURGE audit event is
   retained for the full retention period of the compliance profile. This audit event
   records that erasure occurred, providing an audit trail that satisfies the
   retention regulation's requirement for records even when the underlying data has
   been erased.

**Key design principle:** ARSIA provides the mechanism (PURGE for erasure, retention
policies for regulatory retention, audit events for accountability). The legal
determination of which obligation prevails in a specific case is the operator's
responsibility. The protocol is designed to support any lawful outcome.

### 5.4 Data Minimisation (Art. 5(1)(c))

GDPR Art. 5(1)(c) requires that personal data be "adequate, relevant and limited to
what is necessary in relation to the purposes for which they are processed." The ARSIA
State primitive supports data minimisation through the following mechanisms:

**Agent-level limits.** Implementations SHOULD enforce configurable limits per agent:

| Limit                        | RECOMMENDED default | Description                    |
|------------------------------|---------------------|--------------------------------|
| Maximum entry count          | 10,000              | Total state entries per agent. |
| Maximum total storage size   | 100 MiB             | Total value bytes per agent.   |
| Maximum personal data entries| 1,000               | Entries with `pii_classification` of `"personal"`. |

These limits are implementation-defined and SHOULD be configurable by the platform
operator. They are not protocol-level limits — the protocol does not enforce them
directly. However, implementations SHOULD apply them as safeguards against unbounded
data accumulation.

**Session state enforcement.** Session-scoped entries (§1.1) MUST expire when the
session ends. This is a structural data minimisation measure: data that is only needed
for a single interaction is automatically removed when the interaction completes.

**Expiry defaults.** Implementations SHOULD apply a default expiry to entries that do
not have an explicit `expires_at` or `retention_days`:

- Session scope: session duration (MUST).
- Agent scope: 90 days (RECOMMENDED).
- Shared scope: 90 days (RECOMMENDED).

These defaults ensure that forgotten data does not accumulate indefinitely. Agents
that need longer retention MUST explicitly set `expires_at` or `retention_days`.

> **Informative note — why State uses RECOMMENDED, not MUST, for the 90-day default.**
> State entries serve application-level purposes, so the data owner controls retention
> policy. By contrast, broker relay audit records (ARSIA-Routing.md §7.4) carry a
> mandatory 90-day minimum within a MUST-level storage block, because they prove routing
> compliance and carry regulatory weight. Compliance profiles can override both defaults
> via the `retention_days` field.

**Warnings.** Implementations SHOULD issue warnings (via ARSIA event messages or
operational logging) when an agent approaches its storage limits. The warning SHOULD
be issued when the agent reaches 80% of any configured limit.

### 5.5 Data Portability (Art. 20)

GDPR Art. 20 grants data subjects the right to receive their personal data in a
structured, commonly used, and machine-readable format. The ARSIA QUERY operation
(§3.1.4), combined with PII classification filtering, provides the mechanism for data
portability requests.

**Procedure (informative):**

1. The operator identifies entries containing the data subject's personal data (same
   identification process as §5.3.1, Step 2).
2. The operator uses QUERY with appropriate filters to extract the entries.
3. The StateEntry JSON format is itself a structured, machine-readable format. The
   operator exports the entries and provides them to the data subject.

ARSIA does not define a specific export format for portability — the StateEntry JSON
structure is the native format. Operators MAY transform entries into other formats
(CSV, XML, etc.) as required by their data subject access request procedures.

> **Informative note — JSON as Art. 20 format.** The StateEntry JSON structure is
> itself "structured, commonly used, and machine-readable" as required by
> Art. 20(1). The protocol therefore satisfies the portability format obligation
> natively — no additional export format is required at the protocol level.
> Operators may provide sector-specific formats (e.g., FHIR for healthcare,
> ISO 20022 for finance) as a convenience, but this is an application-layer concern.

### 5.6 Art. 9 Special Categories

State entries with `pii_classification` of `"sensitive"` carry special category data as
defined in GDPR Art. 9(1). The `pii_special_categories` array (§2.1.11) identifies which
specific categories of sensitive data the entry contains (e.g., `"health"`,
`"biometric"`, `"genetic"`).

The cross-object validation rule in Core §4.3.8, Rule 8 ensures that SET operations
for sensitive entries declare an Art. 9(2) legal basis in the compliance envelope.
Art. 6(1) grounds are insufficient for special category data — the SET is rejected if
an Art. 6(1) basis is provided.

Implementations creating GDPR Art. 30 records of processing activities (§5.1) SHOULD
include the `pii_special_categories` values in the "categories of personal data" field
of the record. This enables regulators to verify that the operator has identified and
documented the special categories of data being processed.

### 5.7 Breach Notification (Art. 33/34)

GDPR Art. 33 requires the controller to notify the competent supervisory authority
of a personal data breach without undue delay and, where feasible, not later than
72 hours after becoming aware of it. Art. 34 requires the controller to communicate
the breach to the affected data subjects when the breach is likely to result in a
high risk to their rights and freedoms. The ARSIA Protocol provides a structured
message format for breach notifications between agents within the ARSIA network.

**Payload type:** `arsiaprotocol.compliance/breach-notification`
**Intent:** `"event"` (fire-and-forget, one-way)
**Schema:** `arsia-breach-notification.schema.json`

The `notification_target` field acts as a discriminator:

- `"supervisory_authority"` — controller agent notifying a DPA liaison agent
  (Art. 33 notification).
- `"data_subject"` — controller agent notifying a data subject communication agent
  (Art. 34 notification).

**REQUIRED fields:** `notification_target`, `breach_id`, `nature_of_breach`,
`awareness_timestamp`, `likely_consequences`, `measures_taken`. These fields
correspond to the minimum information required by both Art. 33(3) and Art. 34(2).

**SHOULD fields for supervisory authority notifications:** `categories_of_data`,
`categories_of_data_subjects`, `approximate_data_subject_count`,
`approximate_record_count`, `dpo_contact`. These fields carry the detailed
information that Art. 33(3)(a)/(b) expects in notifications to the supervisory
authority.

**SHOULD fields for data subject notifications:** `remediation_advice`. Art. 34(2)
requires the controller to describe the measures taken and recommend steps the data
subject can take to protect themselves.

The `breach_id` field enables correlation of multiple notifications about the same
breach — for example, an initial notification followed by updates as more
information becomes available, per Art. 33(4).

> **Informative note — operational vs. protocol scope.** The 72-hour deadline
> (Art. 33(1)) is an operational obligation of the controller. The ARSIA Protocol
> carries the notification payload between agents; enforcement of the deadline is
> the controller's responsibility. The `awareness_timestamp` field provides the
> reference point from which the 72-hour window is measured.

---

## 6. Compliance Profiles

A compliance profile is a named set of default values for the compliance
sub-fields defined in ARSIA-Core.md §4.3.6, plus a list of regulatory
references that the profile addresses. Profiles are defined in
`arsia-compliance-profiles.json` and loaded by the receiving agent at startup
or on first reference. Profile defaults are applied per ARSIA-Core.md §4.3.7.

### 6.1 GDPR-STANDARD (Default Baseline)

**Applied when:** No profile is explicitly declared in the `compliance` field, or when
`compliance.profile` is `"GDPR-STANDARD"`. This is the minimum compliance level. Every
ARSIA agent with a `compliance` field defaults to this profile.

**Defaults:**

| Field                     | Default Value     |
|---------------------------|-------------------|
| `audit_required`          | `false`           |
| `retention_days`          | `null`            |
| `human_oversight`         | `"not_required"`  |
| `explainability_required` | `false`           |
| `pii_involved`            | `false`           |
| `data_residency`          | `null`            |

When `retention_days` is `null`, audit record retention (if audit records are generated)
is governed by `expires_at` from the message envelope or by the platform's default
retention policy. A retention period of 90 days is RECOMMENDED as a platform default.

**Regulatory mapping:**

- **GDPR Art. 5** — Principles relating to processing of personal data (lawfulness,
  fairness, transparency, purpose limitation, data minimisation, accuracy, storage
  limitation, integrity and confidentiality, accountability). These principles apply to
  all processing of personal data, regardless of profile.
- **GDPR Art. 6** — Lawfulness of processing. The `legal_basis` field (§2.1.8)
  implements the requirement that processing must have a lawful basis.

When this profile is active and `pii_involved` is `true`:

- `legal_basis` MUST be set (enforced by §8.3, Rule 3).
- The operator SHOULD maintain GDPR Article 30 records of processing activities for all
  interactions involving personal data. The `ArsiaAuditRecord` (§7.1) provides the
  protocol-level component of this record; the operator must supplement it with
  controller-specific information (purpose of processing, categories of data subjects,
  categories of recipients).
- `audit_required` is always effectively `true`, even when the profile default is
  `false` or the sender explicitly sets it to `false`. The receiving agent overrides
  the value and logs a compliance warning (Core §4.3.8, Rule 7). This ensures GDPR
  Article 5(2) accountability: processing of personal data must produce evidence of
  compliance.

### 6.2 EU-AI-ACT-HIGH-RISK

**Applied when:** `compliance.profile` is `"EU-AI-ACT-HIGH-RISK"`. For agents classified
as high-risk AI systems under EU AI Act Annex III.

**Defaults:**

| Field                     | Default Value                    |
|---------------------------|----------------------------------|
| `audit_required`          | `true`                           |
| `retention_days`          | `180`                            |
| `human_oversight`         | `"required_before_execution"`    |
| `explainability_required` | `true`                           |
| `pii_involved`            | `false`                          |
| `data_residency`          | `null`                           |

The `data_residency` default is `null` because the EU AI Act does not mandate data
residency. However, `"EU"` is RECOMMENDED for agents deployed by EU-based operators, as
it ensures audit records remain accessible to national supervisory authorities.

**Regulatory mapping:**

**EU AI Act Art. 13 — Transparency and provision of information to deployers.**
`explainability_required` defaults to `true`. Every response to a message under this
profile MUST include a `payload.explanation` object with `reasoning`, `confidence`, and
`inputs_used` fields as defined in ARSIA-Actions.md §5.2. This implements the
requirement that high-risk AI systems be "designed and developed in such a way as to
ensure that their operation is sufficiently transparent to enable deployers to interpret
the system's output and use it appropriately."

**EU AI Act Art. 14 — Human oversight.** `human_oversight` defaults to
`"required_before_execution"`. This triggers the `pending_approval` /
`approval_decision` flow defined in ARSIA-Actions.md §3. The action MUST NOT execute
until a human approves it through an agent with the `arsiaprotocol.oversight.approve` capability.
This implements Article 14(4)(d): the oversight measures must "enable the natural person
to whom oversight is assigned to be able to decide, in any particular situation, not to
use the high-risk AI system or to otherwise disregard, override or reverse the output of
the high-risk AI system."

**EU AI Act Art. 17 — Quality management system.** `audit_required` defaults to `true`.
Every action under this profile generates an `ArsiaAuditRecord` (§7.1). The audit trail
serves as the quality management record required by Article 17, which mandates
"procedures for record-keeping, documentation, and logging."

**EU AI Act Art. 12 — Record-keeping.** The logging capabilities required by Article 12
are satisfied by the ARSIA audit trail (§7). High-risk AI systems MUST be designed with
automatic event logging — the `ArsiaAuditRecord` structure implements this requirement.
Article 12 complements Article 17 (quality management): Article 17 mandates the
management system, Article 12 mandates the technical logging within it.

**EU AI Act Art. 26(6) — Deployer logging obligations.** `retention_days` defaults to
`180`. Audit records are retained for a minimum of six months, satisfying Article 26(6):
"deployers of high-risk AI systems shall keep the logs automatically generated by that
high-risk AI system to the extent such logs are under their control, for a period
appropriate to the intended purpose of the high-risk AI system, of at least six months."

**EU AI Act Annex III — List of high-risk AI systems.** The agent's
`IdentityRecord.ai_system_classification` MUST be `"high-risk"`
(ARSIA-Identity.md §1.2) for this profile to be applicable. A receiving agent that
detects a mismatch between the profile and the agent-level classification SHOULD log
a compliance warning per ARSIA-Identity.md §4.2.

> **Note on `pii_involved` default.** The default is `false` because the EU AI Act does
> not universally require personal data processing. However, many Annex III categories
> inherently involve personal data (biometric identification, employment,
> creditworthiness assessment, access to public services). Operators deploying agents in
> these categories SHOULD set `pii_involved` to `true` per-message and provide an
> appropriate `legal_basis`. The `false` default avoids imposing GDPR obligations on
> high-risk AI applications that do not process personal data (e.g., industrial safety
> systems, environmental monitoring).

### 6.3 MIFID-II

**Applied when:** `compliance.profile` is `"MIFID-II"`. For agent-assisted financial
services subject to the Markets in Financial Instruments Directive.

**Defaults:**

| Field                     | Default Value                    |
|---------------------------|----------------------------------|
| `audit_required`          | `true`                           |
| `retention_days`          | `1827`                           |
| `human_oversight`         | `"required_before_execution"`    |
| `explainability_required` | `true`                           |
| `pii_involved`            | `true`                           |
| `legal_basis`             | `"contract"`                     |
| `data_residency`          | `"EU"`                           |

**Regulatory mapping:**

**MiFID II Art. 16(7) — Record-keeping obligations.** `retention_days` defaults to
`1827` (5 years). Commission Delegated Regulation (EU) 2017/565, Article 72 (commonly
cited as RTS 22), requires investment firms to "retain all the records required under
this Regulation and under Directive 2014/65/EU for a period of at least five years."
This applies to all services, activities, and transactions — including those executed
or assisted by autonomous agents. The value 1827 accounts for the worst case of two
leap years within any five consecutive calendar years, ensuring the retention floor is
never shorter than five calendar years.

**DORA Art. 17 — ICT-related incident management.** Infrastructure failures during
financial operations generate incident events as defined in ARSIA-Assets.md §6.2.
The ARSIA audit trail captures these events; the operator's incident management process
consumes them for DORA Article 17 compliance.

**DORA Art. 19 — Reporting of major ICT-related incidents.** Major incidents MUST be
reported to competent authorities. ARSIA generates the structured incident event
(ARSIA-Assets.md §6.2.2); the reporting obligation falls on the operator. ARSIA
provides the data — it does not perform the regulatory submission.

**PSD2 Art. 97 — Strong customer authentication.** Financial operations that require
strong customer authentication (SCA) under PSD2 are satisfied through the human
oversight flow (ARSIA-Assets.md §6.3). The `"required_before_execution"` oversight mode
ensures that a human approves financial operations before execution, which constitutes
one element of an SCA framework. Full SCA compliance requires additional measures
(multi-factor authentication) at the implementation level.

**GDPR Art. 6(1)(b) — Contractual basis.** `legal_basis` defaults to `"contract"`
because financial services processing is typically necessary for the performance of a
contract between the financial institution and its client.

**MIFID-II profile interaction with ARSIA-Assets.md:** When this profile is active, all
`AssetTransferRequest` messages (ARSIA-Assets.md §3.1) MUST generate MiFID II audit
records per ARSIA-Assets.md §6.1. The audit record MUST contain all fields specified in
ARSIA-Assets.md §6.1.1.

### 6.4 PAC-AGRICULTURE

**Applied when:** `compliance.profile` is `"PAC-AGRICULTURE"`. For agents operating
under the EU Common Agricultural Policy — subsidy management, paying agency interactions,
and conditionality verification.

**Defaults:**

| Field                     | Default Value                |
|---------------------------|------------------------------|
| `audit_required`          | `true`                       |
| `retention_days`          | `1096`                       |
| `human_oversight`         | `"required_post_execution"`  |
| `explainability_required` | `true`                       |
| `pii_involved`            | `false`                      |
| `data_residency`          | `"EU"`                       |

**Regulatory mapping:**

**EU 2021/2116 Art. 60 — Recovery of undue payments.** Records must be retained for at
least 3 years (1096 days) to support the recovery of undue payments by paying agencies.
This is the basis for the `retention_days` default. The 3-year minimum aligns with the
limitation period for recovery proceedings and ensures that audit evidence is available
for the full cycle of payment verification, on-the-spot checks, and potential recovery
actions. The value 1096 accounts for the worst case of one leap year within any three
consecutive calendar years, ensuring the retention floor is never shorter than three
calendar years.

**EU 2021/2116 Art. 47 — Accreditation of paying agencies.** `audit_required` defaults
to `true`. The audit trail serves as evidence for paying agency certification. Paying
agencies must demonstrate that their management and control systems provide reasonable
assurance of the legality and regularity of underlying transactions — the
`ArsiaAuditRecord` (§7.1) provides the protocol-level component of this evidence.

**EU 2021/2116 Art. 54 — Annual performance clearance.** `explainability_required`
defaults to `true`. Performance reports submitted to the European Commission require
explanation of expenditure compliance. Agent actions that affect subsidy calculations or
eligibility determinations MUST produce explanations that can feed into the annual
performance clearance process.

**EU 2021/2116 Art. 59 — Protection of EU financial interests.** Member states must
take all necessary measures to protect the financial interests of the Union. The
combination of `audit_required: true`, the 3-year retention floor, and mandatory
explainability implements this obligation at the protocol level.

**Human oversight — `"required_post_execution"`.** CAP operations (subsidy calculations,
payment processing, eligibility checks) execute and are then audited post-hoc by paying
agencies and certification bodies. Pre-execution approval is not mandated at the
individual transaction level; the oversight model is ex-post verification, consistent
with the CAP assurance framework.

**Data residency — `"EU"`.** The Common Agricultural Policy is EU-internal. All CAP
data — subsidy calculations, eligibility records, payment data — must be processed and
stored within the EU.

**PII — `false` as default.** CAP primarily deals with farm data, subsidy amounts, and
compliance records. When farmer personal data is involved, the sender SHOULD set
`pii_involved` to `true` per-message and provide an appropriate `legal_basis`.

> **Note on EU 2021/2115 (CAP Strategic Plans).** The conditionality framework
> referenced by EU 2021/2116 is defined in EU Regulation 2021/2115, which establishes
> the strategic plan requirements and conditionality rules that paying agencies must
> verify.

### 6.5 EU-AI-ACT-LIMITED-RISK

**Applied when:** `compliance.profile` is `"EU-AI-ACT-LIMITED-RISK"`. For agents
classified as limited-risk AI systems under EU AI Act Art. 50.

**Defaults:**

| Field                     | Default Value     |
|---------------------------|-------------------|
| `audit_required`          | `true`            |
| `retention_days`          | `90`              |
| `human_oversight`         | `"not_required"`  |
| `explainability_required` | `true`            |
| `pii_involved`            | `false`           |
| `data_residency`          | `null`            |

**Regulatory mapping:**

**EU AI Act Art. 50(1) — Chatbot disclosure.** Providers of AI systems intended to
interact directly with natural persons must ensure that the AI system is designed and
developed in such a way that the natural person is informed that they are interacting
with an AI system. This is the core transparency obligation for limited-risk systems.

**EU AI Act Art. 50(2) — Synthetic content marking.** Providers of AI systems that
generate synthetic audio, image, video, or text content must ensure that the outputs
are marked in a machine-readable format and are detectable as artificially generated or
manipulated.

**EU AI Act Art. 50(3) — Emotion recognition and biometric categorisation disclosure.**
Deployers of emotion recognition systems or biometric categorisation systems must
inform the natural persons exposed thereto of the operation of the system.

**EU AI Act Art. 50(4) — Deepfake disclosure.** Deployers of AI systems that generate
or manipulate image, audio, or video content constituting a deep fake must disclose that
the content has been artificially generated or manipulated.

**Explainability — `true`.** The core Art. 50 obligation IS transparency. Every
response under this profile MUST include a `payload.explanation` object with
`reasoning`, `confidence`, and `inputs_used` fields as defined in ARSIA-Actions.md
§5.2. For Art. 50 systems, the explanation serves as both the transparency mechanism
and the compliance evidence.

**Human oversight — `"not_required"`.** Art. 50 imposes transparency obligations, not
human oversight requirements. Unlike high-risk systems (Art. 14), limited-risk systems
do not require human-in-the-loop or human-on-the-loop mechanisms.

**Audit — `true`.** Evidence of compliance with transparency obligations must be
retained. The audit trail answers: did the system disclose its AI nature? Did it mark
synthetic content? The `ArsiaAuditRecord` (§7.1) captures this evidence.

**Retention — 90 days.** Art. 50 does not prescribe a retention period. 90 days covers
a reasonable compliance verification period and aligns with the GDPR-STANDARD
recommendation for general-purpose retention.

### 6.6 DSA-VLOP

**Applied when:** `compliance.profile` is `"DSA-VLOP"`. For agents operating as or on
behalf of Very Large Online Platforms under the Digital Services Act (EU 2022/2065).

**Defaults:**

| Field                     | Default Value          |
|---------------------------|------------------------|
| `audit_required`          | `true`                 |
| `retention_days`          | `730`                  |
| `human_oversight`         | `"required_within_24h"`|
| `explainability_required` | `true`                 |
| `pii_involved`            | `true`                 |
| `legal_basis`             | `"legal_obligation"`   |
| `data_residency`          | `null`                 |

**Regulatory mapping:**

**DSA Art. 34 — Risk assessment.** VLOPs must identify, analyse, and assess systemic
risks stemming from the design, functioning, and use of their services at least once a
year. Agent actions that affect content moderation, recommendation, or advertising
systems MUST produce audit records that feed into the annual risk assessment.

**DSA Art. 35 — Mitigation of risks.** VLOPs must put in place reasonable,
proportionate, and effective mitigation measures tailored to the systemic risks
identified under Art. 34. The audit trail provides evidence that mitigation measures
were implemented and effective.

**DSA Art. 37 — Independent audit.** VLOPs must be subject to an independent audit at
least once a year to assess compliance with Chapter III obligations. `retention_days`
defaults to `730` (2 years) — this covers two consecutive annual audit cycles, enabling
cross-reference between risk assessments and verification that mitigation measures from
the prior audit were implemented.

**DSA Art. 38 — Recommender system transparency.** VLOPs must offer at least one
option for each recommender system that is not based on profiling. `explainability_required`
defaults to `true` — agent actions involving recommendation must explain the basis of
the recommendation.

**DSA Art. 42 — Transparency reporting.** VLOPs must publish transparency reports at
least every six months. The audit trail provides the data for these reports.

**DSA Art. 15 — Transparency reporting (all providers).** Basic transparency reporting
obligations apply to all intermediary service providers and are strengthened for VLOPs.

**DSA Art. 40 — Data access for researchers.** VLOPs must provide vetted researchers
access to data for the purpose of conducting research on systemic risks. The audit trail
and state entries may be subject to researcher access requests.

**Human oversight — `"required_within_24h"`.** Content moderation decisions require
timely human review. Art. 17 requires a statement of reasons for every content
moderation decision, and Art. 20 requires an internal complaint-handling system —
both imply human involvement within a reasonable timeframe.

**PII — `true`.** VLOPs inherently process user personal data. Content moderation,
advertising, and recommendation all involve personal data processing.

**Legal basis — `"legal_obligation"`.** DSA compliance is a legal obligation under
EU law. Processing of personal data in the course of DSA compliance falls under
GDPR Art. 6(1)(c).

**Data residency — `null`.** The DSA does not mandate EU-only data storage.
GDPR data residency requirements apply separately and should be set per-message
when applicable.

### 6.7 DORA

**Applied when:** `compliance.profile` is `"DORA"`. For agents operating within ICT
incident management workflows for financial entities subject to the Digital Operational
Resilience Act (EU 2022/2554).

**Defaults:**

| Field                     | Default Value          |
|---------------------------|------------------------|
| `audit_required`          | `true`                 |
| `retention_days`          | `1827`                 |
| `human_oversight`         | `"required_within_24h"`|
| `explainability_required` | `false`                |
| `pii_involved`            | `false`                |
| `data_residency`          | `"EU"`                 |
| `clock_skew_seconds`      | `60`                   |

**Regulatory mapping:**

**DORA Art. 5 — ICT risk management governance.** The management body of the financial
entity must define, approve, oversee, and be accountable for the implementation of the
ICT risk management framework. `audit_required` defaults to `true` — all ICT incident
management actions produce audit records for governance review.

**DORA Art. 6 — ICT risk management framework.** Financial entities must establish and
maintain an ICT risk management framework that is reviewed at least annually.
Art. 6(5) requires that the framework be reviewed on the basis of lessons learnt from
the implementation and monitoring — 5 years of incident records ensures coverage of at
least 5 review cycles.

**DORA Art. 11 — Response and recovery.** Financial entities must put in place an ICT
business continuity policy and ICT response and recovery plans. Agent actions within
incident response workflows feed into this obligation.

**DORA Art. 17 — ICT-related incident management process.** Financial entities must
define, establish, and implement an ICT-related incident management process to detect,
manage, and notify ICT-related incidents. The ARSIA audit trail captures the
protocol-level component of this process.

**DORA Art. 18 — Classification of ICT-related incidents.** Financial entities must
classify ICT-related incidents based on specified criteria including duration, number
of users affected, and data losses. The `ArsiaAuditRecord` (§7.1) captures the
classification metadata.

**DORA Art. 19 — Reporting of major ICT-related incidents.** Initial notification to
competent authorities must occur within 4 hours of classification as a major incident.
ARSIA generates structured incident events; the reporting obligation falls on the
operator.

**DORA Art. 28 — General principles for third-party ICT risk.** Financial entities must
manage ICT third-party risk as an integral component of their ICT risk management
framework. Agent interactions with third-party services produce audit records for the
third-party risk register.

**Retention — 1827 days (5 years).** DORA entities are financial entities subject to
European financial sector retention floors (CRD IV for banks, Solvency II for insurers,
IORP II for pensions). 5 years aligns with the sector baseline and ensures coverage of
at least 5 annual ICT risk management review cycles per Art. 6(5). The value 1827
accounts for the worst case of two leap years within any five consecutive calendar
years, ensuring the retention floor is never shorter than five calendar years.

**Human oversight — `"required_within_24h"`.** Art. 19 mandates initial notification
within 4 hours for major incidents, implying rapid human involvement. 24 hours is the
protocol default for the profile; major incidents would override per-message with a
tighter timeframe.

**Explainability — `false`.** DORA is about operational resilience, not AI transparency.
ICT incident records require completeness and accuracy, not explainability in the
AI Act sense.

**PII — `false` as default.** ICT incident records may or may not contain personal
data. When an incident involves personal data (e.g., a data breach), the sender SHOULD
set `pii_involved` to `true` per-message and provide an appropriate `legal_basis`.

**Clock skew — 60 seconds.** Art. 19's 4-hour notification deadline demands clock
precision in incident timestamping. This matches the MIFID-II profile's
`clock_skew_seconds` value, reflecting the shared financial sector requirement for
temporal accuracy.

**Data residency — `"EU"`.** DORA applies to EU financial entities. ICT incident
records must be processed and stored within the EU.

---

## 7. Audit Trail

The audit trail is the backbone of ARSIA compliance. Every compliance-relevant event
produces an `ArsiaAuditRecord` — a structured, immutable, queryable record that links
the event to the originating message, the participating agents, the compliance profile,
and the human oversight status. The audit trail enables regulators, auditors, and
operators to reconstruct the full lifecycle of any regulated interaction.

> **Transport Independence.** Audit record generation applies to all
> ARSIA messages regardless of the underlying transport mechanism
> (HTTP, WebSocket, or any future transport). The audit layer operates
> on the ARSIA envelope, not on the transport frame. See ARSIA-Core.md
> §8.2 for transport-specific semantics.

### 7.1 ArsiaAuditRecord Structure

The `ArsiaAuditRecord` is a JSON object with the following fields. All fields are
REQUIRED unless marked OPTIONAL.

#### `record_id`

- **Type:** string (UUID v4)
- **REQUIRED.**
- **Description:** Unique identifier for this audit record. Generated by the agent that
  creates the record.

#### `message_id`

- **Type:** string (UUID v4)
- **REQUIRED.**
- **Description:** The `id` field of the ARSIA message that this record documents.
  Links the audit record to the originating message.

#### `event_type`

- **Type:** string
- **Enum:** `"request"`, `"response"`, `"event"`, `"error"`, `"pending_approval"`,
  `"approval_decision"`, `"approval_expired"`, `"state_set"`, `"state_delete"`,
  `"state_grant"`, `"state_revoke"`, `"state_purge"`, `"asset_transfer"`,
  `"broker_relay"`, `"key_rotation"`, `"rollback"`, `"dora_incident"`
- **REQUIRED.**
- **Description:** The type of event being audited. Values correspond to protocol
  operations:

  `"request"` — An inbound request message was processed.
  `"response"` — A response message was generated.
  `"event"` — An event intent message (unidirectional notification, e.g. consent withdrawal, breach alert). No response expected.
  `"error"` — An error occurred during processing.
  `"pending_approval"` — An action was held for human oversight.
  `"approval_decision"` — A human oversight decision was made.
  `"approval_expired"` — An approval deadline expired without a decision (ARSIA-Actions.md §3.4).
  `"state_set"` — A state entry was created or modified (§3.1.2).
  `"state_delete"` — A state entry was logically deleted (§3.1.3).
  `"state_grant"` — Access was granted to a state entry (§3.3.1).
  `"state_revoke"` — Access was revoked from a state entry (§3.3.2).
  `"state_purge"` — A state entry was purged under GDPR Art. 17 (§3.2).
  `"asset_transfer"` — An asset transfer was processed (ARSIA-Assets.md §3).
  `"broker_relay"` — A message was relayed by a Compliance Broker
  (ARSIA-Routing.md §7.4).
  `"key_rotation"` — A key rotation or revocation occurred
  (ARSIA-Identity.md §2.4, §2.5).
  `"rollback"` — An action was rolled back (ARSIA-Actions.md §4.2).
  `"dora_incident"` — A DORA incident was recorded (ARSIA-Assets.md §6.2.3).

#### `from_agent`

- **Type:** string (agent-id)
- **REQUIRED.**
- **Description:** The agent-id of the message sender.

#### `to_agent`

- **Type:** string (agent-id)
- **REQUIRED.**
- **Description:** The agent-id of the message recipient.

#### `intent`

- **Type:** string
- **REQUIRED.**
- **Description:** The `intent` field from the originating message (ARSIA-Core.md §4.1).

#### `payload_type`

- **Type:** string
- **REQUIRED.**
- **Description:** The `payload.type` field from the originating message.

#### `payload_hash`

- **Type:** string
- **REQUIRED.**
- **Description:** SHA-256 hash of the payload from the originating message. When
  `security.encrypted` is `false` or absent, this is `SHA-256(RFC8785(payload))` —
  the hash of the RFC 8785 canonicalized payload JSON object. When
  `security.encrypted` is `true`, this is `SHA-256(UTF-8(payload))` — the hash of
  the JWE Compact Serialization string as it appears in the envelope. The audit
  trail stores the hash, not the raw payload. Any party with access to the message
  can verify integrity without decryption keys. See ARSIA-Core.md §5.3.1.

#### `plaintext_hash`

- **Type:** string (64-char lowercase hex)
- **OPTIONAL.** Present ONLY when the originating message has `security.encrypted`
  set to `true`. MUST NOT be present when `security.encrypted` is `false` or absent.
- **Description:** SHA-256 hash of the RFC 8785 canonicalized plaintext payload JSON
  object. Computed by the sender before encryption and by the recipient after
  decryption. Enables dispute resolution over encrypted content: matching
  `plaintext_hash` values in both parties' audit records prove consensus on the
  communicated content. See ARSIA-Core.md §5.3.1.

#### `compliance_profile`

- **Type:** string
- **REQUIRED.**
- **Description:** The compliance profile name from the message's `compliance.profile`
  field, or `"none"` if the message had no `compliance` field.

#### `human_oversight_status`

- **Type:** string
- **Enum:** `"not_required"`, `"pending"`, `"approved"`, `"denied"`, `"expired"`
- **OPTIONAL.**
- **Description:** The status of human oversight for this event.

  `"not_required"` — Human oversight was not triggered for this event.
  `"pending"` — The event is awaiting human approval.
  `"approved"` — A human approved the action.
  `"denied"` — A human denied the action.
  `"expired"` — The approval deadline passed without a decision.

#### `approver_id`

- **Type:** string (agent-id)
- **OPTIONAL.**
- **Description:** The agent-id of the agent that issued the `approval_decision`, when
  `human_oversight_status` is `"approved"` or `"denied"`. This field provides
  accountability for oversight decisions.

#### `processed_at`

- **Type:** string (RFC 3339 with millisecond precision and UTC timezone designator)
- **REQUIRED.**
- **Description:** The timestamp at which this event was processed and the audit record
  was created.

#### `retained_until`

- **Type:** string (RFC 3339 with millisecond precision and UTC timezone designator)
- **REQUIRED.**
- **Description:** The date until which this audit record MUST be retained. Computed
  as `processed_at` + effective `retention_days`. After this date, the record MAY be
  archived (§7.3) or deleted, subject to the archival rules.

#### `data_residency`

- **Type:** string
- **OPTIONAL.**
- **Description:** The geographic zone where this audit record is stored. When present,
  MUST match the message's `compliance.data_residency` value. Audit records for
  messages with data residency constraints MUST be stored within the declared zone.

#### `operator_id`

- **Type:** string
- **REQUIRED.**
- **Description:** The `owner_id` from the IdentityRecord (ARSIA-Identity.md §1.2) of
  the agent that owns this audit log. This establishes legal accountability for the
  audit record.

> **Note.** Implementations SHOULD use organisational identifiers (LEI, VAT number,
> DUNS) rather than personal identifiers for `operator_id`. When a personal identifier
> is unavoidable (e.g., sole proprietor), deployments SHOULD use pseudonymisation
> (e.g., a non-reversible reference identifier) to avoid conflicts between the
> append-only audit requirement (§7.2) and data subject erasure obligations
> (GDPR Art. 17). Where pseudonymisation is not feasible, retention obligations under
> applicable financial regulation (e.g., MiFID II Art. 72) prevail over erasure
> requests per GDPR Art. 17(3)(b).

### 7.2 Immutability Requirements

Audit records MUST be append-only. The following requirements are normative.

**No UPDATE operations.** Once an `ArsiaAuditRecord` is written, it MUST NOT be
modified. If additional information becomes available after the record is created (for
example, a `human_oversight_status` transitioning from `"pending"` to `"approved"`), the
implementation MUST create a new audit record for the new event rather than updating the
existing record. The two records are linked by `message_id` and can be correlated during
audit queries.

**No DELETE operations.** Audit records MUST NOT be deleted before `retained_until`,
with the sole exception of archival after `retained_until` as defined in §7.3.
Implementations MUST NOT provide any mechanism — API, administrative tool, or database
operation — to delete audit records within the retention period.

**Append-only storage.** Implementations MUST use an append-only storage mechanism for
audit records. The audit store MUST enforce INSERT-only semantics — application roles
MUST NOT have permission to UPDATE or DELETE audit records. The store MUST provide
durable persistence with replication. PostgreSQL is one suitable backend; alternative
implementations (append-only log stores, immutable object storage) are acceptable
provided they satisfy these constraints.

**Cryptographic chain (RECOMMENDED).** Implementations SHOULD include a `hash_chain`
field in each audit record containing the SHA-256 hash of the previous record's
`record_id` concatenated with its `payload_hash`. This provides tamper detection: if any
record in the chain is modified or removed, subsequent hash verifications will fail. The
`hash_chain` field is OPTIONAL in v1.0 but is expected to become REQUIRED in a future
version.

**GDPR Art. 17 interaction.** Audit records are NOT subject to GDPR Article 17 (right
to erasure) because they do not contain personal data — the `payload_hash` field stores
a cryptographic hash, not the original payload. GDPR Recital 26 excludes information
that "does not relate to an identified or identifiable natural person" or that has been
"rendered anonymous in such a manner that the data subject is not or no longer
identifiable." A SHA-256 hash of a canonicalized JSON payload is not reversible and does
not identify a natural person. Furthermore, GDPR Article 17(3)(b) exempts processing
that is "necessary for compliance with a legal obligation" — audit records required by
the EU AI Act, MiFID II, or DORA fall under this exemption. If an operator determines
that an audit record's `payload_hash` could theoretically be linked to personal data
through correlation with other data sources, the record is still retained, but the
operator MUST document this in their GDPR Article 30 register.

### 7.3 Audit Record Retention

Retention periods are governed by the compliance profile active at the time the audit
record was created (§6):

| Profile              | Minimum Retention          |
|----------------------|----------------------------|
| EU-AI-ACT-HIGH-RISK  | 180 days                   |
| MIFID-II             | 1827 days (5 years)        |
| PAC-AGRICULTURE      | 1096 days (3 years)        |
| DSA-VLOP             | 730 days (2 years)         |
| DORA                 | 1827 days (5 years)        |
| Default              | 90 days                    |

The **Default** row applies when no profile is active, or when the active profile is
GDPR-STANDARD or EU-AI-ACT-LIMITED-RISK (neither of which defines a retention period
exceeding the platform minimum).

**After `retained_until`:** Records MAY be moved to cold storage (archive). Archived
records MUST remain available for regulatory inspection for an additional 12 months
after the archival date. This grace period ensures that records are not lost during
transitions between retention periods and regulatory inspections.

**After 12 months in archive:** Records MAY be permanently deleted. Deletion of
archived records is at the operator's discretion and SHOULD be documented in the
operator's data retention policy.

**Extending retention:** An operator MAY extend retention beyond the profile minimum by
setting a higher `retention_days` value per-message or by configuring a platform-wide
retention policy. Extended retention does not require protocol-level signaling — the
operator simply retains the records for longer.

### 7.4 Audit Trail Query Endpoint

Implementations that support the Compliance conformance level MUST serve the audit trail
at the following well-known URI:

```
GET /.well-known/arsia/audit
```

**Required capability:** `arsiaprotocol.audit.read` (ARSIA-Actions.md §1.4).

**Query parameters:**

| Parameter              | Type    | Description                                          |
|------------------------|---------|------------------------------------------------------|
| `from_agent`           | string  | Filter by sender agent-id (exact match).             |
| `to_agent`             | string  | Filter by recipient agent-id (exact match).          |
| `after`                | string  | RFC 3339 timestamp — return records after this time. |
| `before`               | string  | RFC 3339 timestamp — return records before this time.|
| `event_type`           | string  | Filter by event type (exact match).                  |
| `compliance_profile`   | string  | Filter by compliance profile (exact match).          |
| `human_oversight_status` | string | Filter by oversight status (exact match).           |
| `payment_reference`    | string  | Filter by payment reference (for asset audit — ARSIA-Assets.md §6.1.4). |
| `limit`                | integer | Maximum records to return. Default: 100. Maximum: 1000. |
| `after_record_id`      | string  | Cursor-based pagination — return records created after this `record_id`. |

**Response format:**

```json
{
  "records": [ ... ArsiaAuditRecord objects ... ],
  "total": 42,
  "has_more": true,
  "next_cursor": "record-id-of-last-returned-record"
}
```

The `records` array contains `ArsiaAuditRecord` objects ordered by `processed_at`
ascending. The `total` field contains the total number of records matching the query
filters (regardless of `limit`). The `has_more` field indicates whether additional
records exist beyond the current page. The `next_cursor` field, when present, contains
the `record_id` of the last record in the current page and can be passed as
`after_record_id` in the next request for cursor-based pagination.

**Access control.** The receiving agent MUST verify that the requesting agent holds the
`arsiaprotocol.audit.read` capability. Access tokens with this scope SHOULD have a short
lifetime (RECOMMENDED maximum: 300 seconds) to limit exposure of sensitive audit data.
Implementations MAY enforce additional record-level access controls: for example,
restricting a requesting agent to audit records within a specific time range, compliance
profile, or set of agent-ids, based on the Authorization Server's policy.

---

## 8. State in the ARSIA Message Envelope

State operations are expressed as standard ARSIA messages, transmitted through the
same channels and subject to the same validation as any other ARSIA message. This
section defines the payload type conventions, capability model, compliance inheritance
rules, and error codes specific to state operations.

### 8.1 Payload Type Prefix

All state operations use the payload type prefix `arsiaprotocol.state/`. The complete set of
payload types is:

| Payload type             | Operation | Description                      |
|--------------------------|-----------|----------------------------------|
| `arsiaprotocol.state/get`        | GET       | Retrieve entry by key.           |
| `arsiaprotocol.state/set`        | SET       | Create or update entry.          |
| `arsiaprotocol.state/delete`     | DELETE    | Logical delete.                  |
| `arsiaprotocol.state/purge`      | PURGE     | Physical erasure.                |
| `arsiaprotocol.state/query`      | QUERY     | Search entries by filter.        |
| `arsiaprotocol.state/snapshot`   | SNAPSHOT  | Point-in-time retrieval.         |
| `arsiaprotocol.state/grant`      | GRANT     | Share state access.              |
| `arsiaprotocol.state/revoke`     | REVOKE    | Remove shared access.            |

The `arsiaprotocol.state/` prefix is reserved by the ARSIA Protocol. Implementations MUST NOT
define custom state operations under this prefix. Extensions to the state primitive
MUST use a different prefix (e.g., `com.example.state/custom-operation`).

### 8.2 Required Capabilities

State operations require the following capabilities in the sender's access token:

| Capability              | Operations                           | Description                    |
|------------------------|--------------------------------------|--------------------------------|
| `arsiaprotocol.state.read`     | GET, QUERY                           | Read state entries.            |
| `arsiaprotocol.state.write`    | SET, DELETE, GRANT, REVOKE           | Modify state entries and grants. |
| `arsiaprotocol.state.purge`    | PURGE                                | Physical erasure (elevated).   |
| `arsiaprotocol.state.snapshot`  | SNAPSHOT                             | Temporal queries (elevated).   |

#### 8.2.1 Capability Hierarchy

The `arsiaprotocol.state.*` wildcard capability grants:

- `arsiaprotocol.state.read`
- `arsiaprotocol.state.write`

The `arsiaprotocol.state.*` wildcard does NOT grant:

- `arsiaprotocol.state.purge`
- `arsiaprotocol.state.snapshot`

These elevated capabilities MUST be explicitly granted in the access token's `scope`
claim. They cannot be obtained through wildcards. This restriction is normative and
MUST be enforced by both Authorization Servers (when issuing tokens) and by state
implementations (when validating tokens).

**Rationale:** PURGE is an irreversible, destructive operation that overrides
retention safeguards. SNAPSHOT provides access to historical data that may have been
logically deleted. Both operations require explicit authorisation because their misuse
has regulatory consequences.

> **Note (informative).** Defence-in-depth: the non-delegable capability mechanism
> defined in ARSIA-Actions.md §1.2 (condition 3) and §1.4 provides protocol-level
> enforcement of this restriction at the PEP layer, complementing the Authorization
> Server policy described above.

#### 8.2.2 Capability Enforcement

State implementations MUST enforce capabilities per ARSIA-Core.md §6.4. The
enforcement procedure is:

1. Extract the access token from the request (ARSIA-Core.md §6.3).
2. Verify the token (ARSIA-Core.md §6.4, steps 1-3).
3. Extract the `scope` claim and parse it into a set of capability strings.
4. Verify that the required capability for the requested operation is present in the
   scope set.
5. If the required capability is missing, reject the request with error code
   `"forbidden"` and details:

   ```json
   {
     "required_capabilities": ["arsiaprotocol.state.purge"],
     "provided_capabilities": ["arsiaprotocol.state.read", "arsiaprotocol.state.write"]
   }
   ```

### 8.3 Compliance Inheritance

When a state operation message carries a `compliance` object in the envelope, the
compliance metadata applies to the state entry being created or modified. The
following inheritance rules are normative:

1. **Data residency.** If the SET request envelope contains
   `compliance.data_residency` and the `payload.args` does not contain
   `data_residency`, the entry MUST inherit the envelope's data residency value. If
   both are set, the `payload.args` value MUST take precedence.

2. **Retention.** If the SET request envelope contains `compliance.retention_days` and
   the `payload.args` does not contain `retention_days`, the entry MUST inherit the
   envelope's retention value. If both are set, the effective retention MUST be
   computed as:

   ```
   max(payload.args.retention_days, compliance.retention_days)
   ```

3. **Legal basis.** The `compliance.legal_basis` field from the envelope MUST be checked
   when `pii_classification` is `"personal"` (§5.2). The legal basis MUST NOT be stored
   on the StateEntry itself — it is part of the message's compliance context and MUST be
   recorded in the audit event.

4. **Audit.** If the envelope's `compliance.audit_required` is `true`, all state
   operations in that message MUST generate audit events, regardless of the
   implementation's default audit configuration.

5. **Compliance profile.** If the envelope references a `compliance.profile`, the
   profile's defaults MUST be applied for any compliance fields not explicitly set.

### 8.4 Error Codes

State operations use the standard ARSIA error codes defined in ARSIA-Core.md §11.2,
plus the following state-specific error codes:

| Error code         | HTTP status | Description                                 |
|--------------------|------------|----------------------------------------------|
| `conflict`         | 409        | Optimistic concurrency conflict. The entry's current version does not match `expected_version`. |
| `invalid_request`  | 400        | Validation failure. Details object specifies the reason (e.g., `missing_legal_basis`, `scope_mismatch`, `data_residency_violation`, `snapshot_unavailable`). |
| `forbidden`        | 403        | Access denied. The requesting agent does not own the entry and has no active grant, or lacks the required capability. |
| `payload_too_large`| 413        | The serialized value exceeds 1 MiB.          |
| `not_implemented`  | 501        | The requested operation is not supported (e.g., SNAPSHOT when temporal storage is not available). |
| `unauthorized`     | 401        | Authentication failure. Invalid or missing access token. |

**Conflict error details:**

When a SET fails due to an optimistic concurrency conflict, the error response MUST
include the following details:

```json
{
  "current_version": 5,
  "expected_version": 3,
  "updated_at": "2026-03-24T15:30:00.000Z",
  "updated_by": "agent:acme.risk-assessor"
}
```

This information allows the requesting agent to understand the conflict and resolve
it (e.g., by re-reading the entry and merging the changes).

---

## 9. State Conformance Tests

The following test cases define conformance requirements for the State primitive. Each
test is identified by a unique `test_id` and specifies preconditions, actions, and
expected results. These tests are normative — a conformant implementation MUST pass
all tests at the applicable conformance level.

### STATE-01: SET and GET round-trip

| Field           | Value                                                              |
|-----------------|--------------------------------------------------------------------|
| **test_id**     | `STATE-01`                                                         |
| **description** | Verify that a state entry can be created and retrieved.            |
| **preconditions** | Agent A has capabilities `arsiaprotocol.state.write` and `arsiaprotocol.state.read`. No entry exists at key `agent:a.test/agent/config`. |
| **action**      | 1. Agent A sends SET with key `"agent:a.test/agent/config"`, value `{ "theme": "dark" }`, scope `"agent"`, pii_classification `"none"`. 2. Agent A sends GET with key `"agent:a.test/agent/config"`. |
| **expected**    | GET returns a StateEntry with: `key` = `"agent:a.test/agent/config"`, `value` = `{ "theme": "dark" }`, `scope` = `"agent"`, `owner_agent_id` = `"agent:a.test"`, `pii_classification` = `"none"`, `version` = `1`, `created_at` and `updated_at` are equal and are valid RFC 3339 timestamps. |

### STATE-02: DELETE hides entry from GET

| Field           | Value                                                              |
|-----------------|--------------------------------------------------------------------|
| **test_id**     | `STATE-02`                                                         |
| **description** | Verify that a logically deleted entry is not returned by GET.      |
| **preconditions** | Entry exists at key `"agent:a.test/agent/temp-data"` with value `{ "temp": true }`. |
| **action**      | 1. Agent A sends DELETE with key `"agent:a.test/agent/temp-data"`. 2. Agent A sends GET with key `"agent:a.test/agent/temp-data"`. |
| **expected**    | DELETE returns `{ "deleted": true, "key": "agent:a.test/agent/temp-data" }`. GET returns `null`. |

### STATE-03: PURGE removes entry permanently and creates audit event

| Field           | Value                                                              |
|-----------------|--------------------------------------------------------------------|
| **test_id**     | `STATE-03`                                                         |
| **description** | Verify that PURGE physically removes data and generates an audit event without the value. |
| **preconditions** | Entry exists at key `"agent:a.test/agent/gdpr/user-12345"` with `pii_classification` = `"personal"`, value `{ "name": "João Silva", "vat": "PT501234567" }`. Agent A has `arsiaprotocol.state.purge` capability. Compliance profile has `audit_required` = `true`. |
| **action**      | 1. Agent A sends PURGE with key `"agent:a.test/agent/gdpr/user-12345"`. 2. Agent A sends GET with key `"agent:a.test/agent/gdpr/user-12345"`. 3. Query the audit trail for events with key `"agent:a.test/agent/gdpr/user-12345"`. |
| **expected**    | PURGE returns `{ "purged": true, "key": "agent:a.test/agent/gdpr/user-12345", "purged_at": "{timestamp}" }`. GET returns `null`. Audit trail contains a `"state_purge"` event with `key`, `owner_agent_id`, `initiator_agent_id`, `purged_at`, and `pii_classification`. The audit event MUST NOT contain the value `{ "name": "João Silva", "vat": "PT501234567" }`. |

### STATE-04: QUERY with scope filter

| Field           | Value                                                              |
|-----------------|--------------------------------------------------------------------|
| **test_id**     | `STATE-04`                                                         |
| **description** | Verify that QUERY correctly filters entries by scope.              |
| **preconditions** | Agent A owns 5 entries with scope `"agent"` and 3 entries with scope `"shared"`. All entries are active (not deleted, not expired). |
| **action**      | Agent A sends QUERY with `scope` = `"agent"`.                     |
| **expected**    | Response contains `entries` with exactly 5 StateEntry objects, all with `scope` = `"agent"`. `total` = `5`. No entries with `scope` = `"shared"` are included. |

### STATE-05: Retention enforcement — entry protected before retention expires

| Field           | Value                                                              |
|-----------------|--------------------------------------------------------------------|
| **test_id**     | `STATE-05`                                                         |
| **description** | Verify that entries are protected during their retention period.   |
| **preconditions** | Entry created with `retention_days` = `180`. Compliance profile is `EU-AI-ACT-HIGH-RISK` (profile `retention_days` = `180`). Entry was created less than 180 days ago. Implementation supports SNAPSHOT. |
| **action**      | 1. Agent A sends DELETE for the entry. 2. Agent A sends GET for the entry. 3. Agent A sends SNAPSHOT with `as_of` = 1 second after the entry's `created_at`. |
| **expected**    | DELETE succeeds (returns `{ "deleted": true, ... }`). GET returns `null` (entry is logically deleted). SNAPSHOT returns the entry with its original value (entry's data is still retained in temporal storage). The implementation MUST NOT physically remove the entry before 180 days from `created_at`. |

### STATE-06: Data residency violation rejected

| Field           | Value                                                              |
|-----------------|--------------------------------------------------------------------|
| **test_id**     | `STATE-06`                                                         |
| **description** | Verify that a SET with a data residency constraint that cannot be honoured is rejected. |
| **preconditions** | Implementation storage is configured for zone `"US"` only. No EU storage backend is available. |
| **action**      | Agent A sends SET with key `"agent:a.test/agent/eu-data"`, value `{ "data": "test" }`, scope `"agent"`, pii_classification `"none"`, data_residency `"EU"`. |
| **expected**    | Error response with code `"invalid_request"` and details containing `{ "data_residency_violation": true, "required_zone": "EU" }`. No entry is created. |

### STATE-07: Shared state grant and cross-agent access

| Field           | Value                                                              |
|-----------------|--------------------------------------------------------------------|
| **test_id**     | `STATE-07`                                                         |
| **description** | Verify that a grant enables cross-agent read access.               |
| **preconditions** | Agent A owns entry at key `"agent:a.test/agent/shared-data"` with value `{ "context": "risk-assessment" }`. Agent B (`agent:b.test`) has `arsiaprotocol.state.read` capability but no grant from Agent A. |
| **action**      | 1. Agent B sends GET for key `"agent:a.test/agent/shared-data"`. (Should fail.) 2. Agent A sends GRANT with `key_pattern` = `"agent:a.test/agent/shared-data"`, `grantee_agent_id` = `"agent:b.test"`, `access_level` = `"read"`. 3. Agent B sends GET for key `"agent:a.test/agent/shared-data"`. (Should succeed.) |
| **expected**    | Step 1: Error with code `"forbidden"`. Step 2: GRANT returns `{ "grant_id": "{uuid}", ... }`. Step 3: GET returns the StateEntry with value `{ "context": "risk-assessment" }`. |

### STATE-08: SNAPSHOT returns correct point-in-time state

| Field           | Value                                                              |
|-----------------|--------------------------------------------------------------------|
| **test_id**     | `STATE-08`                                                         |
| **description** | Verify that SNAPSHOT returns historical state, not current state.  |
| **preconditions** | Implementation supports temporal storage. Entry created at T1 with value `"v1"`. Entry updated at T2 (where T2 > T1) with value `"v2"`. Agent has `arsiaprotocol.state.snapshot` capability. |
| **action**      | Agent A sends SNAPSHOT with `as_of` = T1 + 1 second (a time between T1 and T2). |
| **expected**    | SNAPSHOT returns the entry with value `"v1"` (the state at the requested point in time, before the T2 update). The entry's `version` in the snapshot is `1`, and `updated_at` is approximately T1. |

### STATE-09: Personal data requires legal basis

| Field           | Value                                                              |
|-----------------|--------------------------------------------------------------------|
| **test_id**     | `STATE-09`                                                         |
| **description** | Verify that SET rejects personal data without a legal basis.       |
| **preconditions** | Agent A has `arsiaprotocol.state.write` capability.                       |
| **action**      | Agent A sends SET with key `"agent:a.test/agent/personal/user-99"`, value `{ "email": "user@example.com" }`, scope `"agent"`, pii_classification `"personal"`. The message envelope does NOT contain `compliance.legal_basis`. |
| **expected**    | Error response with code `"invalid_request"` and details `{ "missing_legal_basis": true }`. No entry is created. |

### STATE-10: Optimistic concurrency control (conflict detection)

| Field           | Value                                                              |
|-----------------|--------------------------------------------------------------------|
| **test_id**     | `STATE-10`                                                         |
| **description** | Verify that SET with `expected_version` detects concurrent modifications. |
| **preconditions** | Entry exists at key `"agent:a.test/agent/counter"` with value `{ "count": 1 }`, version `1`. |
| **action**      | 1. Agent A reads the entry (version = 1). 2. Agent B updates the entry to `{ "count": 2 }` (version becomes 2). 3. Agent A sends SET with key `"agent:a.test/agent/counter"`, value `{ "count": 10 }`, `expected_version` = `1`. |
| **expected**    | Agent A's SET fails with error code `"conflict"` and details `{ "current_version": 2, "expected_version": 1 }`. The entry retains Agent B's value `{ "count": 2 }` at version `2`. |

### STATE-11: Profile defaults applied when field is missing

| Field             | Value                                                               |
|-------------------|---------------------------------------------------------------------|
| **test_id**       | `STATE-11`                                                          |
| **description**   | Verify that profile defaults fill missing compliance sub-fields     |
| **preconditions** | Message has `compliance.profile = "EU-AI-ACT-HIGH-RISK"` but no `audit_required` field. |
| **action**        | Receiving agent processes the message and determines the effective `audit_required` value. |
| **expected**      | `audit_required` defaults to `true` (from EU-AI-ACT-HIGH-RISK profile). An `ArsiaAuditRecord` is generated for this message. |

### STATE-12: Per-message override of profile default

| Field             | Value                                                               |
|-------------------|---------------------------------------------------------------------|
| **test_id**       | `STATE-12`                                                          |
| **description**   | Verify that per-message values override profile defaults            |
| **preconditions** | Message has `compliance.profile = "EU-AI-ACT-HIGH-RISK"` and `compliance.retention_days = 365`. |
| **action**        | Receiving agent processes the message and computes `retained_until`. |
| **expected**      | Audit record has `retained_until` = `processed_at` + 365 days (not 180). The per-message value of 365 exceeds the profile minimum of 180, so it is accepted. |

### STATE-13: MIFID-II retention floor enforced

| Field             | Value                                                               |
|-------------------|---------------------------------------------------------------------|
| **test_id**       | `STATE-13`                                                          |
| **description**   | Verify that MIFID-II retention floor of 1827 days is enforced       |
| **preconditions** | Message has `compliance.profile = "MIFID-II"` and `compliance.retention_days = 365`. |
| **action**        | Receiving agent validates retention per §8.3, Rule 2.               |
| **expected**      | Message is rejected with error code `"invalid_request"` and `details: { "insufficient_retention": true, "required": 1827, "provided": 365 }`. |

### STATE-14: Audit record immutability

| Field             | Value                                                               |
|-------------------|---------------------------------------------------------------------|
| **test_id**       | `STATE-14`                                                          |
| **description**   | Verify that audit records cannot be updated or deleted              |
| **preconditions** | An `ArsiaAuditRecord` has been created for a processed message.     |
| **action**        | Attempt to UPDATE the `human_oversight_status` field of the existing record. Attempt to DELETE the record. |
| **expected**      | Both operations are rejected. The implementation does not provide UPDATE or DELETE operations on audit records. New oversight events generate new audit records linked by `message_id`. |

### STATE-15: Audit trail query with filters

| Field             | Value                                                               |
|-------------------|---------------------------------------------------------------------|
| **test_id**       | `STATE-15`                                                          |
| **description**   | Verify that the audit query endpoint returns correctly filtered results |
| **preconditions** | 20 audit records exist. 5 have `compliance_profile = "MIFID-II"`.   |
| **action**        | `GET /.well-known/arsia/audit?compliance_profile=MIFID-II&limit=10` |
| **expected**      | Response contains exactly 5 records. `has_more` is `false`. `total` is `5`. All returned records have `compliance_profile = "MIFID-II"`. |

---

## 10. Security Considerations

### 10.1 Access Control

State access control is layered:

1. **Transport-level authentication.** All state operation messages are ARSIA messages
   and MUST be transmitted over TLS 1.3 or later (ARSIA-Core.md §8.1).

2. **Message-level authentication.** All state operation messages MUST be signed per
   ARSIA-Core.md §5.1. The signature proves the identity of the requesting agent.

3. **Token-based authorization.** All state operation messages MUST carry a valid
   access token with the required capabilities (§8.2).

4. **Entry-level access control.** The state implementation enforces ownership and
   grant-based access control per the rules defined in §3.1 and §3.3.

These layers are cumulative. An agent must pass all four layers to perform a state
operation. A failure at any layer results in rejection.

**Principle of least privilege.** Agents SHOULD request only the capabilities they
need. An agent that only reads state SHOULD request `arsiaprotocol.state.read` only, not
`arsiaprotocol.state.*`. An agent that never needs to purge data SHOULD NOT be granted
`arsiaprotocol.state.purge`.

### 10.2 Injection and Abuse

**Key injection.** The key format (§2.1.1) restricts allowed characters to
`[a-zA-Z0-9:._/\-]`. This prevents directory traversal attacks, null byte injection,
and other key manipulation attacks. Implementations MUST validate keys against the
pattern before processing any operation.

**Value injection.** State values are opaque JSON. Implementations MUST NOT interpret
or execute value contents. Values MUST be treated as data, not as code or commands.
Agents that consume state values MUST validate and sanitise the values before using
them in any context where injection is possible (SQL queries, shell commands, HTML
rendering, etc.).

**Denial of service.** The per-agent storage limits (§5.4) and per-query result limits
(§3.1.4) mitigate unbounded resource consumption. Implementations SHOULD additionally
enforce rate limits on state operations, consistent with the agent's `rate_limits`
from its discovery metadata (ARSIA-Core.md §7.1).

**Enumeration attacks.** An agent SHOULD NOT be able to discover the existence of
entries it cannot access. QUERY and GET operations MUST return empty results (not
errors) when the agent lacks access to matching entries, unless the access failure is
due to a missing capability (in which case `"forbidden"` is returned).

### 10.3 Side-Channel Risks

**Timing attacks.** Implementations SHOULD use constant-time comparison for key
lookups when the key may reveal information about other agents' entries. In practice,
this is most relevant for the QUERY operation where an agent queries with a
`key_prefix` that could match entries owned by other agents.

**Storage size inference.** Agents SHOULD NOT be able to infer the storage usage of
other agents. QUERY result counts MUST only reflect entries accessible to the
requesting agent, not the total number of entries in the system.

### 10.4 Encryption at Rest

Implementations MUST encrypt state entry values at rest when `pii_classification` is
`"sensitive"`. All obligations of `"personal"` apply, plus: implementations MUST use
authenticated encryption (per §2.1.10). Implementations MUST encrypt state entry
values at rest when `pii_classification` is `"personal"`. Implementations SHOULD
encrypt values at rest when `pii_classification` is `"pseudonymised"`. Encryption at
rest for entries with `pii_classification` of `"none"` is RECOMMENDED but not
required.

**Key management.** Encryption keys for at-rest encryption MUST be managed according
to the same key management requirements as ARSIA signing keys
(ARSIA-Identity.md §2.1): no plaintext storage in production, HSM or cloud KMS
RECOMMENDED.

**Encryption scope.** At-rest encryption applies to the `value` field of the
StateEntry. Metadata fields (key, scope, timestamps, version) are NOT required to be
encrypted, as they are needed for index operations. However, implementations SHOULD
encrypt the `key` field when it may contain PII-derived identifiers (e.g., keys that
include client tax numbers).

---

## 11. Implementation Guidance (Informative)

This section provides non-normative guidance for implementors. The recommendations
are based on operational experience with state management in regulated environments.

### 11.1 Storage Backend Selection

The ARSIA State primitive is intentionally storage-agnostic. The following table
provides guidance on storage backend selection:

| Backend          | Suitable for                           | Temporal storage | Notes                        |
|------------------|----------------------------------------|-----------------|------------------------------|
| PostgreSQL       | Agent/Shared scope, regulated          | Yes (via temporal tables or event sourcing) | Best for compliance-heavy deployments. Supports SNAPSHOT natively with temporal features. |
| Redis            | Session scope, high-throughput         | No (without custom extension) | Excellent for session state with TTL-based expiry. Not suitable for compliance-requiring durability. |
| S3 / Object store| Large values, archival                 | Yes (via versioning) | Good for archival and large binary-referenced data. Higher latency for reads. |
| SQLite           | Development, single-agent              | Limited          | Suitable for development and testing. Not recommended for production regulated deployments. |
| DynamoDB         | Cloud-native, auto-scaling             | Yes (via point-in-time recovery) | Good for cloud deployments with configurable region pinning for data residency. |
| CockroachDB      | Multi-region, strong consistency       | Yes (via AS OF SYSTEM TIME) | Excellent for multi-region deployments with data residency requirements. |

Implementations MAY use multiple backends — for example, Redis for session state and
PostgreSQL for agent and shared state. The ARSIA interface is uniform regardless of
the backend.

### 11.2 Temporal Storage

SNAPSHOT support requires temporal storage — the ability to query historical versions
of entries. Several approaches are available:

1. **Temporal tables (PostgreSQL).** PostgreSQL's system-versioned temporal tables
   (SQL:2011) provide native point-in-time queries. This is the RECOMMENDED approach
   for PostgreSQL-based implementations.

2. **Event sourcing.** Store every state change as an immutable event. Reconstruct
   state at any point in time by replaying events up to the desired timestamp. This
   approach is more complex but provides a complete, immutable audit trail.

3. **Version table.** Maintain a separate table of (key, version, value, timestamp)
   tuples. SNAPSHOT queries filter by timestamp. Simpler than event sourcing but
   requires periodic cleanup.

4. **Object store versioning.** S3 and compatible object stores support object
   versioning natively. Each version has a timestamp. SNAPSHOT queries list versions
   and select the appropriate one.

The choice of temporal storage approach is an implementation decision. The ARSIA
protocol requires only that the SNAPSHOT operation returns correct results per §3.2.1.

### 11.3 Performance Considerations

**Key indexing.** The `key` field MUST be indexed for efficient GET operations. The
`key_prefix` filter in QUERY benefits from a prefix index (e.g., a B-tree index on
the key column in PostgreSQL, or a range key in DynamoDB).

**Pagination.** The QUERY operation supports offset-based pagination. For large result
sets, offset-based pagination can be inefficient. Implementations MAY additionally
support cursor-based pagination as a non-standard extension, using a custom field in
the `payload.args`.

**Caching.** Implementations MAY cache frequently-read entries (especially
global-scoped entries) in memory. Cache invalidation MUST respect version semantics:
a cached entry MUST be invalidated when a SET operation changes the entry. For
global-scoped entries that change infrequently, a TTL-based cache with a 60-second
refresh interval is RECOMMENDED.

**Batch operations.** This specification does not define batch SET or batch DELETE
operations. Implementations that need batch operations for performance reasons MAY
define them as extensions under a custom payload type prefix. Batch operations MUST
generate individual audit events for each affected entry — a single batch audit event
is not sufficient for regulatory compliance.

### 11.4 Hash Chain (RECOMMENDED)

This specification RECOMMENDS a `hash_chain` field linking each audit record to its
predecessor via SHA-256, providing tamper evidence without external infrastructure
(§7.2). Implementations that include hash chain support enable offline tamper detection
and cross-system audit verification.

---

## 12. References

### 12.1 Normative References

- **ARSIA-Core.md** — ARSIA Protocol Core Specification, Draft-01.
  §3 (Agent Identifier Format), §4 (Message Envelope), §4.2.1 (Correlation ID),
  §4.2.2 (Expiration), §4.3.6 (Compliance Field Definition),
  §4.3.7 (Field Inheritance), §4.3.8 (Validation Rules),
  §5 (Message Security), §6.4 (Capability Enforcement),
  §8.1 (HTTP/2 Transport), §8.3 (Timing),
  §9.2 (Brokered Routing — Data Residency), §11.2 (Error Codes).

- **ARSIA-Identity.md** — ARSIA Identity Primitive, Draft-01.
  §1.2 (IdentityRecord — `owner_id`, `owner_name` for Art. 30 records),
  §2.1 (Key Pair Requirements — key management for encryption at rest).

- **ARSIA-Actions.md** — ARSIA Actions Primitive, Draft-01.
  §1.1 (Capability Naming).

- **RFC 2119** — Key words for use in RFCs to Indicate Requirement Levels.
  Bradner, S. March 1997. BCP 14.

- **RFC 3339** — Date and Time on the Internet: Timestamps.
  Klyne, G. and C. Newman. July 2002.

- **RFC 8174** — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words.
  Leiba, B. May 2017. BCP 14.

- **RFC 8259** — The JavaScript Object Notation (JSON) Data Interchange Format.
  Bray, T. December 2017.

- **RFC 8785** — JSON Canonicalization Scheme (JCS).
  Rundgren, A., Jordan, B., and S. Erdtman. June 2020.

- **RFC 9562** — Universally Unique IDentifiers (UUIDs).
  Davis, K., Peabody, B., and P. Leach. May 2024.

### 12.2 Informative References

- **GDPR** — Regulation (EU) 2016/679 of the European Parliament and of the Council.
  - Art. 4(5) — Definition of pseudonymisation.
  - Art. 5(1)(c) — Data minimisation principle.
  - Art. 5(1)(e) — Storage limitation principle.
  - Art. 5(2) — Accountability principle.
  - Art. 6 — Lawfulness of processing.
  - Art. 17 — Right to erasure ('right to be forgotten').
  - Art. 20 — Right to data portability.
  - Art. 30 — Records of processing activities.

- **EU AI Act** — Regulation (EU) 2024/1689.
  - Art. 13 — Transparency and provision of information to deployers.
  - Art. 14 — Human oversight.
  - Art. 26(6) — Obligations of deployers — automatic logging retention (6 months).

- **MiFID II** — Directive 2014/65/EU.
  - Art. 16(7) — Record retention for investment firms (5 years minimum).

- **Common Agricultural Policy (CAP)** — Regulation (EU) 2021/2116.
  - Record-keeping requirements for agricultural subsidies and payments.

- **Commission Delegated Regulation (EU) 2017/565** — supplementing MiFID II as regards
  organisational requirements and operating conditions for investment firms.
  - Art. 72 (retention of records — commonly cited as RTS 22).

- **DORA** — Regulation (EU) 2022/2554 of the European Parliament and of the Council
  of 14 December 2022 on digital operational resilience for the financial sector.
  - Art. 17 (ICT-related incident management).
  - Art. 19 (reporting of major ICT-related incidents).

- **PSD2** — Directive (EU) 2015/2366 of the European Parliament and of the Council of
  25 November 2015 on payment services in the internal market.
  - Art. 97 (strong customer authentication).

- **ISO 3166-1** — Codes for the representation of names of countries and their
  subdivisions — Part 1: Country codes. Alpha-2 codes used for data residency zones.

- **SQL:2011** — ISO/IEC 9075:2011. Temporal features (system-versioned temporal
  tables) referenced in implementation guidance (§11.2).

---
ARSIA Protocol ([arsiaprotocol.org](https://arsiaprotocol.org)) | by [Arsia Labs](https://arsialabs.ai)
