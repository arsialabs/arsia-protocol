<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
# ARSIA-Actions — Actions Primitive Specification

**Protocol:** ARSIA Protocol
**Version:** 2.0
**Status:** Draft
**Authors:**
- Kirk Patrick (Arsia Labs) — kirk@arsialabs.ai
- Greici Savoldi (Arsia Labs) — greici@arsialabs.ai

**Draft-02 | July 2026 | References: ARSIA-Core.md §4.1 (intent enum), §4.2 (conditional
required fields), §4.4 (payload structure), §6.4 (capability enforcement)**
**Arsia Labs — arsiaprotocol.org**

---

## Abstract

The Actions primitive defines what ARSIA Protocol agents can do — the capability model
that governs permissions, the action registry that describes available operations, the
human oversight mechanism that pauses risky actions for human approval before execution,
the explainability framework that makes agent reasoning transparent, and the audit
requirements that ensure every action is traceable. This specification introduces two
message intents — `pending_approval` and `approval_decision` — as the protocol-level
mechanism for human oversight of autonomous AI agents. These intents implement the
requirements of EU AI Act Article 14 (human oversight) and Article 13 (transparency
and provision of information to deployers) as interoperable protocol primitives. Any
ARSIA-conformant agent can participate in the oversight flow regardless of its internal
architecture, framework, or deployment model. The Actions primitive answers the first
letter in the ARSIA acronym: what can agents do, under what constraints, and with what
accountability.

---

## Status of This Memo

This document specifies Draft-02 of the ARSIA Actions Primitive. This specification is
a working draft published by Arsia Labs for review and comment. Implementors should
expect breaking changes between draft revisions.

The canonical location for this specification is:

    https://arsiaprotocol.org/spec/actions/draft-02

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

1. [Capability Model](#1-capability-model)
   1. [Capability Naming](#11-capability-naming)
   2. [Capability Hierarchy](#12-capability-hierarchy)
   3. [Capability Downgrading](#13-capability-downgrading)
   4. [Reserved System Capabilities](#14-reserved-system-capabilities-normative-registry)
2. [Action Registry](#2-action-registry)
   1. [Action Descriptor](#21-action-descriptor)
   2. [Risk Level to EU AI Act Mapping](#22-risk-level-to-eu-ai-act-mapping)
   3. [Action Discovery Endpoint](#23-action-discovery-endpoint)
   4. [Action Versioning](#24-action-versioning)
3. [Human Oversight Signaling (EU AI Act Art. 14)](#3-human-oversight-signaling-eu-ai-act-art-14)
   1. [Rationale](#31-rationale)
   2. [The pending_approval Message](#32-the-pending_approval-message)
   3. [The approval_decision Message](#33-the-approval_decision-message)
   4. [Execution After Approval](#34-execution-after-approval)
   5. [Audit Trail for Oversight](#35-audit-trail-for-oversight)
   6. [Multiple Approval Levels (OPTIONAL)](#36-multiple-approval-levels-optional)
   7. [Execution Without Prior Approval](#37-execution-without-prior-approval)
   8. [Implementation Guidance: Approval Rate Management](#38-implementation-guidance-approval-rate-management)
   9. [Post-Execution Review](#39-post-execution-review)
4. [Action Execution Semantics](#4-action-execution-semantics)
   1. [Execution Lifecycle States](#41-execution-lifecycle-states)
   2. [Rollback (Reversible Actions)](#42-rollback-reversible-actions)
   3. [Execution Timeouts](#43-execution-timeouts)
   4. [Sandboxing Requirements](#44-sandboxing-requirements)
5. [Explainability (EU AI Act Art. 13)](#5-explainability-eu-ai-act-art-13)
   1. [When Required](#51-when-required)
   2. [Explanation Object Format](#52-explanation-object-format)
   3. [Explainability and Audit](#53-explainability-and-audit)
6. [Actions Conformance Tests](#6-actions-conformance-tests)
7. [References](#7-references)
   1. [Normative References](#71-normative-references)
   2. [Informative References](#72-informative-references)

---

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14 [RFC 2119] [RFC 8174] when,
and only when, they appear in ALL CAPITALS, as shown here.

---

## 1. Capability Model

Capabilities are the authorization primitive in the ARSIA Protocol. A capability is a
named permission that authorises an agent to perform a specific action on a target
agent. Capabilities are declared in the message envelope's `capabilities` field
(ARSIA-Core.md §4.2.3) and enforced by verifying that the sender's access token
includes a matching scope (ARSIA-Core.md §6.4).

This section defines the grammar, hierarchy, and semantics of capability strings.

### 1.1 Capability Naming

Capability strings in the ARSIA Protocol conform to the following grammar, specified
using Augmented Backus-Naur Form (ABNF) notation per [RFC 5234]:

```abnf
capability   = concrete-cap / wildcard-cap
concrete-cap = domain-part 1*("." domain-part)
wildcard-cap = domain-part *("." domain-part) ".*"
domain-part  = ALPHA *(ALPHA / DIGIT)
```

The `capability` production defines a dot-separated hierarchical identifier in one of
two forms: a concrete capability consisting of at least two segments (e.g., `notes.read`),
or a wildcard capability consisting of at least one segment followed by the `".*"` suffix
(e.g., `notes.*`). Each segment (`domain-part`) consists of an ASCII letter followed by
zero or more ASCII letters or digits.

**Examples.** The following are valid ARSIA capability strings:

```
notes.read
```

A specific read capability in the `notes` domain. The first segment (`notes`) identifies
the capability domain; the second segment (`read`) identifies the specific permission.

```
notes.write
```

A specific write capability in the `notes` domain.

```
notes.*
```

A wildcard capability that matches all capabilities in the `notes` domain. Wildcard
capabilities are used in access token scopes to grant broad access (§1.2).

```
arsiaprotocol.broker.relay
```

A multi-segment capability in the reserved `arsiaprotocol.` namespace. This capability grants
authority to relay messages as a Compliance Broker (ARSIA-Routing.md §7).

```
arsiaprotocol.oversight.approve
```

A reserved capability that grants authority to issue `approval_decision` messages (§3.3).
This is the most security-sensitive capability in the protocol.

```
payments.charge
```

An application-defined capability for initiating payment charges. Application developers
define their own capability namespaces outside the reserved `arsiaprotocol.` prefix.

```
eu.mifid.risk.assess
```

A multi-segment capability scoped to the EU MiFID regulatory domain. Demonstrates that
capability hierarchies can encode regulatory and organisational structure.

```
com.acme.billing.invoice.create
```

A deeply nested capability demonstrating that hierarchies can have arbitrary depth.

**Rules.** The following rules govern capability string construction and validation:

1. **Minimum segments.** A concrete capability string MUST contain at least two segments
   separated by a dot. A wildcard capability string MUST contain at least one segment
   before the `".*"` suffix. Single-segment capability strings without a wildcard suffix
   (e.g., `"read"`, `"write"`) are invalid and MUST be rejected. This minimum ensures
   that all capabilities are namespaced.

2. **Maximum length.** A capability string MUST NOT exceed 128 characters in total length,
   including all dots and the optional wildcard suffix. Implementations MUST reject
   capability strings that exceed this limit.

3. **Case sensitivity.** Capability strings are case-sensitive. `"Notes.Read"` and
   `"notes.read"` are distinct capabilities. Implementations SHOULD use lowercase by
   convention but MUST NOT perform case-insensitive matching.

4. **Wildcard placement.** The wildcard suffix `".*"` is ONLY allowed as the last two
   characters of a capability string. A wildcard MUST NOT appear in the middle of a
   capability string. For example, `"notes.*.read"` is invalid. A capability string
   MUST NOT consist solely of the wildcard `".*"` — the wildcard MUST be preceded by at
   least one domain-part segment.

5. **Reserved prefix.** The prefix `"arsiaprotocol."` is RESERVED for capabilities defined by
   the ARSIA Protocol specification. Application-defined capabilities MUST NOT use the
   `arsiaprotocol.` prefix. Implementations MUST reject capability requests that use the `arsiaprotocol.`
   prefix unless the capability is one of the reserved system capabilities defined in
   §1.4.

6. **Character restrictions.** Capability segments MUST contain only ASCII letters
   (`A-Z`, `a-z`) and digits (`0-9`). Hyphens, underscores, spaces, and other special
   characters are not permitted within segments. The only permitted special characters
   in a complete capability string are the dot separator (`.`) and the wildcard asterisk
   (`*`) as part of the `".*"` suffix.

> **Informative note.** The capability grammar defined above is distinct from the
> `payload.type` format defined in ARSIA-Core.md §4.4.1. Capabilities use forward domain
> notation with dot separators only (e.g., `eu.mifid.risk.assess`); `payload.type` uses
> reverse domain notation with optional `/`-separated path segments that may contain
> hyphens and underscores (e.g., `com.example.notes/create`). The `action_id` field
> (§2.1) follows the `payload.type` format, not the capability format.

### 1.2 Capability Hierarchy

The ARSIA Protocol supports a single wildcard suffix per capability expression in capability matching.
This mechanism allows access tokens to grant broad permissions using wildcard scopes,
which are then matched against specific capability requests in message envelopes.

**Matching rule.** A token scope entry `S` satisfies a requested capability `R` if and
only if one of the following conditions holds:

1. **Exact match.** `S` is identical to `R` (byte-for-byte string comparison).

2. **Wildcard match.** `S` ends with `".*"`, and `R` starts with the prefix of `S`
   (everything before `".*"`) followed by a dot. Formally: let `P` be the string
   obtained by removing the trailing `".*"` from `S`. Then `S` satisfies `R` if and
   only if `R` starts with `P` followed by `"."` — that is, `R` matches the regular
   expression `^{P}\..*$` where `{P}` is the literal prefix with any regex-special
   characters escaped.

3. **Reserved-namespace exception (non-delegable capabilities).** If `R` is in the
   reserved `arsiaprotocol.` namespace (§1.4), then `S` satisfies `R` if and only
   if condition 1 holds (exact match). Every reserved capability is non-delegable
   in this sense: wildcard matching (condition 2) MUST NOT satisfy any
   `arsiaprotocol.` capability. Authorization Servers MUST NOT issue scope entries
   containing a wildcard within the reserved namespace (e.g. `arsiaprotocol.*`,
   `arsiaprotocol.state.*`); receiving agents MUST treat such scope entries as
   satisfying nothing. Rationale: each reserved capability carries role-restricted
   authority (§1.4) — approver, broker, gateway, administrator — and a wildcard
   grant would silently confer roles the Authorization Server never evaluated.

**Direction of matching.** The token scope is the AUTHORITY. The message's `capabilities`
field is the REQUEST. The receiving agent compares each requested capability against the
authority, not the other way around. A specific scope entry never satisfies a wildcard
request.

**Examples.** The following examples illustrate the matching rule:

| Token scope entry | Requested capability | Result   | Reason                                    |
|-------------------|----------------------|----------|-------------------------------------------|
| `notes.*`         | `notes.read`         | ACCEPTED | Wildcard `notes.*` covers `notes.read`    |
| `notes.*`         | `notes.write`        | ACCEPTED | Wildcard `notes.*` covers `notes.write`   |
| `notes.*`         | `notes.admin.reset`  | ACCEPTED | Wildcard `notes.*` covers all `notes.` prefixed capabilities |
| `notes.*`         | `billing.read`       | REJECTED | Prefix `notes` does not match `billing`   |
| `notes.read`      | `notes.read`         | ACCEPTED | Exact string match                        |
| `notes.read`      | `notes.*`            | REJECTED | Specific scope does not grant wildcard    |
| `notes.read`      | `notes.write`        | REJECTED | No match — different terminal segment     |
| `arsiaprotocol.*`         | `arsiaprotocol.broker.relay` | REJECTED | Reserved namespace — wildcard never satisfies `arsiaprotocol.` capabilities (condition 3) |
| `arsiaprotocol.*`         | `arsiaprotocol.state.purge` | REJECTED | Reserved namespace — requires exact match (condition 3) |
| `arsiaprotocol.*`         | `arsiaprotocol.oversight.approve` | REJECTED | Reserved namespace — requires exact match (condition 3) |
| `payments.*`      | `payments.charge`    | ACCEPTED | Wildcard covers `payments.charge`         |
| `payments.charge` | `payments.refund`    | REJECTED | Exact match fails                         |

**Multi-capability requests.** When a message's `capabilities` array contains multiple
entries, the receiving agent MUST verify that EVERY requested capability is satisfied by
at least one entry in the token's scope. It is acceptable for a single wildcard scope
entry to satisfy multiple requested capabilities. For example, a token with scope
`"notes.*"` satisfies a request for capabilities `["notes.read", "notes.write"]`.

**Scope composition.** A token's scope is a space-separated string of capability entries
(ARSIA-Core.md §6.1). Each entry is evaluated independently against each requested
capability. The union of all satisfactions determines whether the request is authorised.
For example, a token with scope `"notes.read payments.charge"` satisfies a request for
capabilities `["notes.read", "payments.charge"]` because each requested capability is
individually satisfied.

### 1.3 Capability Downgrading

A receiving agent MAY grant fewer capabilities than those requested in the message's
`capabilities` field. This is called **capability downgrading**. Downgrading allows an
agent to accept a request with reduced permissions rather than rejecting it outright.

**When downgrading occurs.** A receiving agent MAY downgrade capabilities when:

- The agent supports the requested action but does not wish to grant all requested
  permissions for policy reasons.
- The requesting agent's trust level or compliance classification does not qualify for
  the full set of requested capabilities.
- Operational constraints (rate limits, quotas, resource availability) warrant reduced
  access.

**Downgrading semantics.** When a receiving agent downgrades capabilities:

1. The response message MUST include an `effective_capabilities` array in the
   `payload.result` object. This array lists the actual capabilities that were granted
   for this interaction.

2. The `effective_capabilities` array MUST be a subset of the original `capabilities`
   array from the request. It MUST NOT contain capabilities that were not present in
   the request.

3. The `effective_capabilities` array MUST contain at least one capability. If the
   receiving agent cannot grant any of the requested capabilities, it MUST reject the
   request with error code `forbidden` (ARSIA-Core.md §11.2) rather than downgrading
   to an empty set.

4. The sender MUST honour the downgraded capabilities and MUST NOT assume broader access
   than what is declared in `effective_capabilities`. If the sender requires a capability
   that was removed during downgrading, it MUST issue a new request explicitly requesting
   that capability.

**Example.** Agent A sends a request with:

<!-- example: arsia-message.schema.json; partial=/v,/id,/ts,/from,/to,/intent -->
```json
{
  "capabilities": ["notes.read", "notes.write", "notes.delete"]
}
```

Agent B accepts the request but downgrades the capabilities. The response includes:

```json
{
  "payload": {
    "type": "com.example.notes/list",
    "result": {
      "notes": [...],
      "effective_capabilities": ["notes.read", "notes.write"]
    }
  }
}
```

Agent A observes that `notes.delete` was not granted and MUST NOT attempt to invoke
delete operations within this interaction without issuing a new request.

**Downgrading and audit.** When capabilities are downgraded, the audit record (if
`audit_required` is true) MUST record both the original requested capabilities and
the effective capabilities that were granted. This provides auditors with visibility
into authorization decisions.

### 1.4 Reserved System Capabilities (Normative Registry)

This section is the **single normative registry** of capabilities in the reserved
`arsiaprotocol.` namespace. A capability with the `arsiaprotocol.` prefix is valid if
and only if it appears in this registry; per §1.1 Rule 5, implementations MUST reject
capability requests using the `arsiaprotocol.` prefix for any name not registered
here. Application-defined capabilities MUST NOT use this prefix. Implementations MUST
recognise the registered capabilities and enforce their semantics as described below.

**Extension rule.** New `arsiaprotocol.` capabilities are registered only by a
revision of this specification. There is no runtime or out-of-band extension
mechanism for the reserved namespace: a name not in this registry is unknown, and
unknown reserved names are rejected — never ignored, never treated as
application-defined. Examples and conformance materials in the ARSIA specifications
MUST only use reserved names from this registry; illustrative application
capabilities use unreserved names (e.g. `code.review`, `com.example.notes.read`).

#### `arsiaprotocol.oversight.approve`

Grants authority to issue `approval_decision` messages (§3.3) and post-execution
review decisions (§3.9.3). This is the most security-sensitive capability in the ARSIA
Protocol because it controls whether high-risk actions proceed to execution and
records the human review of executed actions.

**Constraints:**

- MUST only be granted to agents that represent human oversight roles — that is,
  agents through which a natural person exercises oversight authority. This includes
  agents that serve as interfaces for human decision-makers (e.g., a dashboard agent
  that collects human input and translates it into `approval_decision` messages).
- MUST NOT be granted to fully autonomous agents acting without human supervision.
  The purpose of this capability is to ensure that a natural person is in the decision
  loop, consistent with EU AI Act Article 14(1), which applies to Annex III high-risk
  systems from 2 December 2027.
- The Authorization Server MUST implement additional verification before issuing
  tokens with this scope. The specific verification mechanism (e.g., multi-factor
  authentication, organizational role binding) is implementation-defined.

#### `arsiaprotocol.broker.relay`

Grants authority to relay messages as a Compliance Broker (ARSIA-Routing.md §7).

**Constraints:**

- MUST only be granted to agents that operate as Compliance Brokers within a declared
  data residency zone.
- Agents with this capability MUST NOT modify the contents of relayed message envelopes.
- Agents with this capability MUST append an audit record for every message they relay.

#### `arsiaprotocol.audit.read`

Grants read access to an agent's audit trail. The audit trail format and query
interface are defined in ARSIA-State.md §7.

**Constraints:**

- Typically granted to compliance officers, auditors, regulatory agents, or agents
  acting on behalf of supervisory authorities.
- Access tokens with this scope SHOULD have a short lifetime (RECOMMENDED maximum:
  300 seconds) to limit the window of exposure for sensitive audit data.
- The receiving agent MUST enforce record-level access controls: an agent with
  `arsiaprotocol.audit.read` MAY be restricted to audit records within a specific time range
  or compliance profile, depending on the Authorization Server's policy.

#### `arsiaprotocol.identity.admin`

Grants authority to rotate keys and update the IdentityRecord (ARSIA-Identity.md §2.4,
§1.2).

**Constraints:**

- MUST be tightly controlled — compromise of this capability allows identity takeover.
- SHOULD be restricted to infrastructure management agents or human-operated
  administrative tools.
- Tokens with this scope MUST have the shortest practical lifetime. A maximum of
  60 seconds is RECOMMENDED.
- The Authorization Server SHOULD require additional authentication factors before
  issuing tokens with this scope.

#### `arsiaprotocol.state.read`

Grants read access to agent state. The state model is defined in ARSIA-State.md §3.1
(forward reference).

**Constraints:**

- Read access to state is a prerequisite for audit and debugging operations.
- State entries that contain personally identifiable information (PII) MUST be filtered
  or masked unless the requesting agent also has appropriate GDPR-related authorization,
  as determined by the receiving agent's data protection policy.

#### `arsiaprotocol.state.write`

Grants write access to agent state. The state model is defined in ARSIA-State.md §3.1
(forward reference).

**Constraints:**

- Write access to state allows modification of an agent's persistent memory. This
  capability SHOULD be granted sparingly and only to agents that have a legitimate
  need to modify state.
- State writes MUST be logged when `audit_required` is true for the interaction.

#### `arsiaprotocol.state.purge`

Grants GDPR erasure capability — the ability to request deletion of state entries
containing personal data. The purge mechanism is defined in ARSIA-State.md §3.2.2
(forward reference).

**Constraints:**

- This is an elevated capability that MUST require explicit grant — it MUST NOT be
  implied by `arsiaprotocol.state.write` or any wildcard scope.
- Purge operations are irreversible. The receiving agent MUST log the purge request
  and the identifiers of the deleted state entries in the audit trail before executing
  the deletion.
- This capability supports GDPR Article 17 (right to erasure).

#### Non-Delegable Capabilities

**Every capability in the reserved `arsiaprotocol.` namespace is non-delegable**
(§1.2, condition 3): none may be satisfied by wildcard matching, and each MUST be
explicitly listed in the access token's `scope` claim as an exact string.
Particularly sensitive examples and their rationale:

| Capability | Rationale |
|------------|-----------|
| `arsiaprotocol.state.purge` | Irreversible physical erasure; within retention only under a recorded retention override (ARSIA-State.md §3.2.2). |
| `arsiaprotocol.state.snapshot` | Access to historical data that may have been logically deleted. |
| `arsiaprotocol.oversight.approve` | Authorises approval of human oversight decisions for high-risk actions. |
| `arsiaprotocol.broker.relay` | Confers the Compliance Broker role (Routing §7). |
| `arsiaprotocol.identity.admin` | Key rotation and IdentityRecord control — identity takeover if abused. |

Authorization Servers MUST NOT issue scope entries containing a wildcard within the
reserved namespace and MUST NOT rely on wildcard expansion to grant reserved
capabilities. Receiving agents (PEP) MUST reject capability requests for reserved
capabilities unless the exact capability string is present in the token's `scope`
claim.

#### `arsiaprotocol.state.snapshot`

Grants point-in-time state retrieval for audit purposes. The snapshot mechanism is
defined in ARSIA-State.md §3.2.1 (forward reference).

**Constraints:**

- Snapshots are read-only, immutable captures of state at a specific timestamp.
- Typically granted alongside `arsiaprotocol.audit.read` for regulatory inspection workflows.
- Snapshot responses MUST include the timestamp of the snapshot and a cryptographic
  hash of the state data for integrity verification.

#### `arsiaprotocol.assets.transfer.initiate`

Grants authority to initiate asset transfers. The asset transfer model is defined in
ARSIA-Assets.md §3.1 (forward reference).

**Constraints:**

- This capability authorises the creation of a transfer request. It does not authorise
  execution — execution MAY require a separate approval step depending on the transfer
  amount and risk classification.
- Agents with this capability MUST declare the asset types they support in their
  action registry (§2.3).

#### `arsiaprotocol.assets.transfer.approve`

Grants authority to approve pending asset transfers, implementing two-party
authorization. The approval mechanism is defined in ARSIA-Assets.md §5 (forward
reference).

**Constraints:**

- Two-party authorization means that the agent initiating a transfer MUST NOT be the
  same agent that approves it. The Authorization Server MUST enforce this separation.
- Functionally similar to `arsiaprotocol.oversight.approve` but scoped specifically to asset
  transfers. An agent MAY hold both capabilities if it serves as a general oversight
  agent.

#### `arsiaprotocol.assets.transfer.reverse`

Grants authority to request reversal of a previously completed asset transfer. The
reversal mechanism is defined in ARSIA-Assets.md §3.3 (forward reference).

**Constraints:**

- Reversals are subject to the same constraints as action rollbacks (§4.2): they are
  best-effort and MAY be rejected if the reversal window has elapsed.
- Reversal requests MUST be logged in the audit trail with the original transfer
  identifier for traceability.

#### `arsiaprotocol.assets.escrow.create`

Grants authority to create an escrow arrangement by including `escrow_conditions` in
an AssetTransferRequest. The escrow lifecycle is defined in ARSIA-Assets.md §4
(forward reference).

**Risk level:** 5 (elevated).

**Human oversight:** MAY be required.

**Constraints:**

- Creating an escrow requires BOTH `arsiaprotocol.assets.transfer.initiate` AND
  `arsiaprotocol.assets.escrow.create`. The transfer initiation capability alone does not
  authorise escrow creation.
- The agent creating the escrow MUST specify a valid `release_agent` and `timeout_at`
  in the EscrowConditions.

#### `arsiaprotocol.assets.escrow.release`

Grants authority to trigger the release of escrowed value. The release mechanism is
defined in ARSIA-Assets.md §4.2 (forward reference).

**Risk level:** 7 (high).

**Human oversight:** SHOULD be required for currency escrows. RECOMMENDED for
non-currency escrows above an implementation-defined threshold.

**Constraints:**

- Only the `release_agent` specified in the EscrowConditions may release the escrow
  (or, while the escrow is `DISPUTED`, the `arbitration_agent` — ARSIA-Assets.md §4.1
  dispute resolution exception). Possessing this capability alone is necessary but
  not sufficient — the agent's identity MUST also match the `release_agent` field (or
  that `arbitration_agent`).
- The release message MUST be signed by the releasing agent's Ed25519 key.

#### `arsiaprotocol.assets.escrow.cancel`

Grants authority to cancel an escrowed transfer before the release trigger is
received, returning the value to the sender. The cancellation mechanism is defined in
ARSIA-Assets.md §4.2 (forward reference).

**Risk level:** 6 (elevated).

**Human oversight:** MAY be required.

**Constraints:**

- Cancellation is only permitted before the escrow transitions to a terminal state
  (RELEASED, RETURNED, or a resolved DISPUTED state).
- Cancellation generates an `escrow_returned` audit event (ARSIA-Assets.md §4.3.3)
  with an additional `cancellation_reason` field.

#### `arsiaprotocol.assets.audit.read`

Grants read access to the asset-specific audit trail — the audit records generated by
asset transfer operations. The audit trail format is defined in ARSIA-Assets.md §6.1
(forward reference).

**Risk level:** 3 (limited).

**Human oversight:** Not required.

**Constraints:**

- This capability grants read access to audit records generated by the Assets primitive
  only. It does NOT grant access to the general ARSIA audit trail (which requires
  `arsiaprotocol.audit.read`).
- Access tokens with this scope SHOULD have a short lifetime (RECOMMENDED maximum:
  300 seconds) to limit the window of exposure for sensitive financial audit data.
- The receiving agent MUST enforce record-level access controls: an agent with
  `arsiaprotocol.assets.audit.read` MAY be restricted to audit records within a specific
  date range, payment_reference range, or compliance profile.

#### `arsiaprotocol.compliance.breach.notify`

Grants authority to send breach notification event messages
(`arsiaprotocol.compliance/breach-notification`). Intended for controller agents
that need to notify other agents (DPA liaison agents, data subject communication
agents) about personal data breaches per GDPR Art. 33 and Art. 34. The breach
notification mechanism is defined in ARSIA-State.md §5.7.

**Constraints:**

- SHOULD only be granted to agents acting in a controller role with respect to
  personal data breach management.
- Breach notification events carry sensitive information about security incidents.
  Agents with this capability MUST ensure that breach details are transmitted only
  to authorised recipients.
- The capability authorises sending breach notifications. It does NOT authorise
  the actual notification to supervisory authorities or data subjects — that is
  an operational step outside the protocol.

---

#### `arsiaprotocol.echo`

The ARSIA echo capability, used for connectivity checks and conformance testing
(ARSIA-Core.md §12, Appendix A.1). A request declaring this capability asks the
recipient to return the request payload unchanged in the response.

**Constraints:**

- Implementations at Core conformance level MUST support `arsiaprotocol.echo`.
- Echo handling MUST NOT have side effects beyond standard message processing
  (audit, idempotency); it MUST NOT read or write agent state.
- Authorization Servers MAY grant this capability freely; it carries no elevated
  authority.

#### `arsiaprotocol.health`

Grants access to an agent's health/liveness check (ARSIA-Core.md Appendix A.3). A
request declaring this capability asks the recipient to report its operational
status.

**Constraints:**

- Health responses MUST NOT disclose internal configuration, key material, or
  deployment topology; they report liveness and protocol-level readiness only.
- Authorization Servers MAY grant this capability freely; it carries no elevated
  authority.

#### `arsiaprotocol.onboarding.evaluate`

Grants authority to evaluate onboarding requests as an Onboarding Gateway
(ARSIA-Identity.md §7). The gateway declares this capability when processing an
agent's onboarding flow.

**Constraints:**

- MUST only be granted to agents that operate as Onboarding Gateways for an
  organisation's agent infrastructure.
- Agents with this capability MUST apply the deny-by-default policy of
  ARSIA-Identity.md §7 and MUST record onboarding decisions in the audit trail.

#### `arsiaprotocol.broker.use`

Grants authority to **submit** messages to a Compliance Broker for relay
(ARSIA-Routing.md §2.3). This capability is intentionally distinct from
`arsiaprotocol.broker.relay`: `broker.use` authorises an agent to *use* a broker as
a sender; `broker.relay` authorises an agent to *operate as* a broker.

**Constraints:**

- Delegable: MAY be granted to any agent whose compliance context requires brokered
  routing (e.g. `compliance.data_residency` set).
- Possession of `broker.use` grants no authority to relay, read, or re-sign other
  agents' messages.
- The full brokered-authorization model, including the token audiences and the relay
  attestation, is defined in ARSIA-Routing.md §2.3.

## 2. Action Registry

The Action Registry is the mechanism through which ARSIA-conformant agents advertise
what operations they support. Each operation is described by an ActionDescriptor — a
structured JSON object that declares the operation's identity, risk classification,
capability requirements, human oversight requirements, and audit obligations.

The Action Registry serves two purposes. First, it enables dynamic discovery: a
requesting agent can query the registry to determine what actions are available, what
capabilities are required, and what oversight or compliance constraints apply before
sending a request. Second, it enables static analysis: compliance tools can inspect the
registry to verify that an agent's declared risk levels are consistent with its
compliance profile and that appropriate oversight controls are in place.

### 2.1 Action Descriptor

An ActionDescriptor is a JSON object that describes a single action available at an
ARSIA-conformant agent. Each field is defined below with its type, constraints, and
semantics.

#### `action_id` — Action Identifier

- **Type:** string
- **REQUIRED.**
- **Format:** Reverse domain notation with an optional action path, following the same
  pattern as `payload.type` in ARSIA-Core.md §4.4.1.
- **Pattern:** `^[a-zA-Z][a-zA-Z0-9]*(\.[a-zA-Z][a-zA-Z0-9]*)*(\/[a-zA-Z][a-zA-Z0-9_-]*)*$`
- **Examples:**
  - `"com.example.notes/delete"` — Delete a note in the example.com notes service.
  - `"arsiaprotocol.compliance/check"` — Run a compliance check (ARSIA-defined action).
  - `"eu.mifid.risk/assess"` — Perform a MiFID II risk assessment.
  - `"com.acme.billing/create-invoice"` — Create an invoice.
- **Constraints:** The `action_id` uniquely identifies this action within the agent's
  registry. The reverse domain notation ensures global uniqueness across organisations.
  The optional path segment (after `/`) identifies a specific operation within the
  domain. The `action_id` MUST correspond to a `payload.type` value that the agent
  will accept in request messages.

#### `category` — Action Category

- **Type:** string
- **REQUIRED.**
- **Allowed values:** `"data"`, `"communication"`, `"financial"`, `"system"`,
  `"oversight"`
- **Constraints:** The `category` field provides a high-level classification of the
  action's domain. The enumerated values are defined as follows:

  - **`"data"`**: Actions that read, write, transform, or delete data. Examples:
    database queries, file operations, state mutations, data exports.
  - **`"communication"`**: Actions that send, receive, forward, or relay messages to
    external systems or agents. Examples: email dispatch, notification broadcasting,
    message forwarding, webhook invocation.
  - **`"financial"`**: Actions that involve monetary transactions, asset transfers,
    billing operations, or financial calculations. Examples: payment processing,
    invoice creation, risk assessment, portfolio rebalancing.
  - **`"system"`**: Actions that affect the agent's own infrastructure, configuration,
    or lifecycle. Examples: key rotation, configuration updates, health checks,
    deployment operations.
  - **`"oversight"`**: Actions related to human oversight, approval workflows, and
    compliance checks. Examples: approval requests, compliance validations, audit
    queries, identity verification.

#### `description` — Human-Readable Description

- **Type:** string
- **REQUIRED.**
- **Maximum length:** 512 characters.
- **Constraints:** A concise, human-readable description of what this action does. The
  description MUST be written in English. It SHOULD be sufficiently detailed for a
  human reviewer to understand the action's purpose and potential impact without
  consulting additional documentation. The description is used in oversight workflows
  (§3.2) to help approvers make informed decisions.

#### `risk_level` — Risk Assessment Score

- **Type:** integer
- **REQUIRED.**
- **Minimum:** 0
- **Maximum:** 10
- **Constraints:** The risk assessment score determines the compliance requirements
  that apply to this action. The mapping from risk levels to EU AI Act classifications
  and protocol requirements is defined in §2.2. The risk level MUST be assigned by the
  agent operator based on a risk assessment that considers the action's potential impact
  on individuals, organisations, and systems. The risk level MUST be consistent with the
  agent's `ai_system_classification` in its IdentityRecord (ARSIA-Identity.md §1.2): an
  agent classified as `"minimal-risk"` SHOULD NOT register actions with risk_level ≥ 7.

#### `reversible` — Reversibility Flag

- **Type:** boolean
- **REQUIRED.**
- **Constraints:** When `true`, this action supports rollback via the mechanism defined
  in §4.2. When `false`, the action is considered irreversible once executed — the agent
  does not support undoing the action's effects. The value of this field MUST accurately
  reflect the agent's implementation: declaring `reversible: true` for an action that
  cannot actually be rolled back is a conformance violation.

#### `idempotent` — Idempotency Flag

- **Type:** boolean
- **REQUIRED.**
- **Constraints:** When `true`, executing this action multiple times with identical
  input parameters produces the same result and side effects. When `false`, repeated
  execution may produce different results or cumulative side effects. This field informs
  the requesting agent's retry strategy: idempotent actions are safe to retry on
  transient failures (ARSIA-Core.md §11.3), while non-idempotent actions require
  idempotency keys (ARSIA-Core.md §10) to prevent unintended duplication.

#### `required_capabilities` — Required Capabilities

- **Type:** array of strings
- **REQUIRED.**
- **Constraints:** Each element MUST be a valid capability string conforming to the
  grammar in §1.1. The array lists the capabilities that a requesting agent MUST have
  in its access token scope to invoke this action. The receiving agent enforces this
  requirement per ARSIA-Core.md §6.4. The array MUST contain at least one element.

#### `optional_capabilities` — Optional Capabilities

- **Type:** array of strings
- **Default:** `[]` (empty array)
- **Constraints:** Each element MUST be a valid capability string conforming to the
  grammar in §1.1. Optional capabilities enhance the action's behavior when present but
  are not required for invocation. For example, an action might accept `notes.read` as
  required and `notes.metadata` as optional — when the optional capability is present,
  the response includes additional metadata.

#### `human_oversight_required` — Human Oversight Flag

- **Type:** boolean
- **REQUIRED.**
- **Constraints:** When `true`, the ActionDescriptor demands the oversight mode
  `"required_before_execution"` for every invocation of the action: it is an
  `executor-policy` requirement source (ARSIA-Core.md §4.3.10.2), and the action
  follows the `pending_approval` flow of §3 before execution. When `false`, the
  descriptor demands nothing. It is not a dispensation: the action still requires
  prior approval when another source of the effective oversight set demands it
  (§3.7).

#### `post_execution_review_period` — Post-Execution Review Period

- **Type:** string
- **OPTIONAL.**
- **Format:** ISO 8601 calendar duration per ARSIA-Core.md §4.3.6.4.
- **Constraints:** The period within which a post-execution review required by
  `"required_post_execution"` must be decided, counted from the execution instant with
  the calendar arithmetic of ARSIA-Core.md §4.3.6.4.1 (§3.9.2). It is the executing
  agent's announced review policy for the action. When absent, the action cannot be
  executed under `"required_post_execution"` (§3.9.1). It does not apply to
  `"required_within_24h"`, whose deadline is fixed.

#### `audit_required` — Audit Requirement Flag

- **Type:** boolean
- **REQUIRED.**
- **Constraints:** When `true`, every execution of this action MUST generate an audit
  record in the agent's audit trail. The audit record format is defined in
  ARSIA-State.md §7. The audit record MUST include: the
  action_id, the requesting agent's identity, the timestamp of execution, the request
  parameters (or a hash thereof), and the result (or a hash thereof). When `false`,
  audit logging is OPTIONAL for this action, though the agent's compliance profile
  MAY still require it.

#### `retention` — Audit Retention Override

- **Type:** string
- **OPTIONAL.**
- **Format:** ISO 8601 calendar duration per ARSIA-Core.md §4.3.6.4 (e.g. `"P1827D"`,
  `"P6M"`).
- **Constraints:** When present, this value overrides the retention minimum from
  the applicable compliance profile for audit records generated by this action —
  upward only: a value explicitly below the profile's `retention_minimum` (calendar
  comparison per ARSIA-Core.md §4.3.6.4.1) MUST cause the action registration or the
  message to be rejected per ARSIA-Core.md §4.3.8 Rule 4; it is never silently
  clamped. This field is only meaningful when `audit_required` is `true`. If absent,
  the retention period is determined by the compliance profile. If no compliance
  profile is active, a retention of `"P90D"` is the RECOMMENDED platform default.

#### `supported_versions` — Supported Payload Versions

- **Type:** array of strings
- **OPTIONAL.** Default: `["1.0"]`.
- **Format:** Each entry matches `^(0|[1-9]\d*)\.(0|[1-9]\d*)$`; entries MUST be
  unique.
- **Constraints:** The payload schema versions this agent accepts for this action.
  This is the **proactive discovery surface** for action versioning (§2.4): during
  a migration window the agent lists both versions here (e.g. `["1.0", "2.0"]`) in
  a SINGLE descriptor entry — the version distinction is carried in
  `payload.version`, never in `action_id`. Requests declaring a version not in
  this list are rejected with `not_implemented` and
  `details.supported_versions` (§2.4). Senders SHOULD consult this field before
  invoking a non-base version rather than relying on the reactive error.

#### `explainability_required` — Explainability Flag

- **Type:** boolean
- **REQUIRED.**
- **Constraints:** When `true`, every response to this action MUST include a
  `payload.explanation` object as defined in §5.2. This field implements EU AI Act
  Article 13 transparency obligations at the action level. When the action goes through
  human oversight (§3), the `pending_approval` message SHOULD include a preliminary
  explanation to help the approver make an informed decision.

#### `max_execution_ms` — Maximum Execution Time

- **Type:** integer
- **OPTIONAL.**
- **Default:** `30000` (30 seconds)
- **Minimum:** `100`
- **Constraints:** The maximum time, in milliseconds, that the action should take to
  execute. This value serves as a timeout hint: if execution exceeds this duration, the
  agent MUST respond with error code `service_unavailable` (ARSIA-Core.md §11.2). For
  actions expected to exceed this limit, the async execution pattern defined in §4.3
  SHOULD be used. The receiving agent MUST honour this timeout — it MUST NOT continue
  execution after the timeout has elapsed without client awareness.

#### Complete ActionDescriptor Example

The following example shows a complete ActionDescriptor for a MiFID II risk assessment
action:

<!-- example: arsia-action-descriptor.schema.json -->
```json
{
  "action_id": "eu.mifid.risk/assess",
  "category": "financial",
  "description": "Performs a MiFID II suitability assessment for a proposed investment transaction. Evaluates the client's risk profile against the instrument's risk classification and produces a suitability opinion.",
  "risk_level": 8,
  "reversible": false,
  "idempotent": true,
  "required_capabilities": ["mifid.risk.assess"],
  "optional_capabilities": ["mifid.client.read"],
  "human_oversight_required": true,
  "audit_required": true,
  "retention": "P1827D",
  "explainability_required": true,
  "max_execution_ms": 60000
}
```

### 2.2 Risk Level to EU AI Act Mapping

The following table defines the normative mapping between ARSIA risk levels and EU AI
Act classifications. This mapping determines the minimum compliance requirements that
apply to actions at each risk level. Agent operators MUST assign risk levels consistent
with this mapping. Implementations MUST enforce the MUST-level requirements; violation
constitutes a conformance failure.

#### Risk 0–2 — Minimal Risk

Actions in this range pose negligible risk to individuals, organisations, or systems.

| Requirement                | Level        | Notes                                      |
|----------------------------|--------------|--------------------------------------------|
| `audit_required`           | MAY be false | No audit obligation from the protocol.     |
| `human_oversight_required` | SHOULD be false | Oversight is unnecessary at this level. |
| `explainability_required`  | MAY be false | No transparency obligation.                |

**EU AI Act mapping:** Not classified as high-risk under Annex III. No specific
obligations from Regulation 2024/1689 apply at the protocol level. General-purpose
information retrieval, status checks, health probes, and read-only queries typically
fall in this range.

#### Risk 3–4 — Limited Risk

Actions in this range have moderate impact but do not approach the high-risk threshold.

| Requirement                | Level          | Notes                                    |
|----------------------------|----------------|------------------------------------------|
| `audit_required`           | SHOULD be true | Audit is advisable for traceability.     |
| `human_oversight_required` | MAY be false   | Oversight is optional at this level.     |
| `explainability_required`  | MAY be true    | Transparency aids trust but is optional. |

**EU AI Act mapping:** Limited risk — transparency obligations apply per Article 50.
Agents SHOULD inform counterparties that they are interacting with an AI system.
Actions that modify non-critical data, send non-binding notifications, or produce
advisory outputs typically fall in this range.

#### Risk 5–6 — Elevated Risk

Actions in this range have significant potential impact and approach the high-risk
threshold.

| Requirement                | Level            | Notes                                  |
|----------------------------|------------------|----------------------------------------|
| `audit_required`           | MUST be true     | Full audit trail is mandatory.         |
| `human_oversight_required` | MAY be true      | Oversight is recommended but optional. |
| `explainability_required`  | SHOULD be true   | Transparency is expected.              |

**EU AI Act mapping:** Approaching the high-risk threshold defined in Annex III.
Actions at this level SHOULD be reviewed for potential reclassification as high-risk.
Actions that modify significant data, trigger communications with external parties, or
produce outputs that may influence decisions affecting individuals typically fall in
this range.

#### Risk 7–8 — High Risk

Actions in this range are classified as high-risk. The EU AI Act obligations for
high-risk AI systems (Chapter III, Sections 2 and 3) apply from 2 December 2027 for
Annex III systems (Article 113(c)); the protocol requirements below apply now as ARSIA
controls.

| Requirement                | Level           | Notes                                   |
|----------------------------|-----------------|-----------------------------------------|
| `audit_required`           | MUST be true    | Full audit trail is mandatory.          |
| `human_oversight_required` | SHOULD be true  | ARSIA control anticipating Art. 14 (from 2 Dec 2027). |
| `explainability_required`  | MUST be true    | ARSIA control anticipating Art. 13 (from 2 Dec 2027). |

**EU AI Act mapping:** High-risk per Annex III. Article 14 human oversight obligations
apply from 2 December 2027 for Annex III systems (Article 113(c)): the AI system must
be designed such that it can be effectively overseen by natural persons during the
period in which it is in use. Article 13 transparency obligations apply from
2 December 2027 for Annex III systems (Article 113(c)): the system's operation must be
sufficiently transparent to enable deployers to interpret its output. Article 17
quality management obligations apply from 2 December 2027 for Annex III systems
(Article 113(c)), including systems and procedures for record-keeping of all
relevant documentation and information (Article 17(1)(k)); the automatic recording of
events (logs) is required by Article 12(1). Actions that make financial
recommendations, assess risk profiles, process personal data for automated
decision-making, or affect access to essential services typically fall in this range.

#### Risk 9–10 — Critical Risk

Actions in this range carry the highest potential for harm and require maximum oversight
and control.

| Requirement                | Level           | Notes                                   |
|----------------------------|-----------------|-----------------------------------------|
| `audit_required`           | MUST be true    | Full audit trail is mandatory.          |
| `human_oversight_required` | MUST be true    | Autonomous execution is prohibited.     |
| `explainability_required`  | MUST be true    | Full transparency is mandatory.         |

**EU AI Act mapping:** High-risk with maximum oversight. Actions at risk level 9–10
MUST NOT be executed without prior human approval. Autonomous execution — that is,
execution without an intervening `approval_decision` message with `decision: "approved"`
— is prohibited at this risk level. This is the protocol's strongest interpretation of
Article 14(4)(d), which requires that the oversight measures enable the natural person
to "decide, in any particular situation, not to use the high-risk AI system or to
otherwise disregard, override or reverse the output of the high-risk AI system."

Actions that initiate irreversible financial transactions, modify regulatory
classifications, override safety controls, or make decisions with direct legal
consequences for natural persons typically fall in this range. Implementations MAY
require multiple approvals for risk level 10 actions (§3.6).

### 2.3 Action Discovery Endpoint

Every ARSIA-conformant agent that exposes actions MUST serve its action registry at the
following well-known URI:

```
GET /.well-known/arsia/actions
```

The response MUST be a JSON object with the following structure:

```json
{
  "actions": [
    { ... ActionDescriptor ... },
    { ... ActionDescriptor ... }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

**Response fields:**

| Field     | Type    | Description                                           | Required |
|-----------|---------|-------------------------------------------------------|----------|
| `actions` | array   | Array of ActionDescriptor objects.                    | REQUIRED |
| `total`   | integer | Total number of actions matching the query (before pagination). | REQUIRED |
| `limit`   | integer | Maximum number of actions returned in this response.  | REQUIRED |
| `offset`  | integer | Number of actions skipped (for pagination).           | REQUIRED |

**Query parameters.** The action discovery endpoint MUST support the following query
parameters for filtering and pagination:

| Parameter                    | Type    | Description                                   |
|------------------------------|---------|-----------------------------------------------|
| `category`                   | string  | Filter by action category. Value MUST be one of the allowed category values (§2.1). |
| `human_oversight_required`   | boolean | Filter by human oversight requirement. `true` returns only actions requiring oversight; `false` returns only actions not requiring oversight. |
| `risk_level_min`             | integer | Minimum risk level (inclusive). Range: 0–10.  |
| `risk_level_max`             | integer | Maximum risk level (inclusive). Range: 0–10.  |
| `audit_required`             | boolean | Filter by audit requirement.                  |
| `limit`                      | integer | Maximum number of results to return. Default: 20. Maximum: 100. |
| `offset`                     | integer | Number of results to skip. Default: 0.        |

**Filtering semantics.** When multiple query parameters are provided, they MUST be
combined with logical AND. For example, `?category=financial&risk_level_min=7` returns
only financial actions with risk level 7 or above.

**Caching.** The response SHOULD include caching headers:

```
Cache-Control: max-age=300, must-revalidate
ETag: "{hash-based-etag}"
```

Clients SHOULD respect these caching headers and SHOULD refetch the action registry when
they receive a `not_implemented` error for an action they believed was available.

**Authentication.** The action discovery endpoint SHOULD be publicly accessible without
authentication. If the agent operator wishes to restrict visibility of the action
registry, the endpoint MAY require authentication, in which case a `401 Unauthorized`
response MUST be returned for unauthenticated requests.

**Identification.** A descriptor returned by this endpoint is identified by its
`action_id` and the SHA-256 of its RFC 8785 canonical form. This identification is
recorded when the descriptor acts as a requirement source (ARSIA-Core.md §4.3.10.2),
and each published revision is retained per that section.

### 2.4 Action Versioning

Actions are versioned through the combination of the `payload.type` field (ARSIA-Core.md
§4.4.1) and the `payload.version` field (ARSIA-Core.md §4.4.2). The `payload.type`
identifies the action; the `payload.version` identifies the version of the action's
schema.

**Version format.** Version strings MUST follow the `MAJOR.MINOR` format where both
components are non-negative integers. For example: `"1.0"`, `"2.3"`, `"1.12"`.

**Version bump rules:**

1. **Minor version bump** (e.g., `1.0` → `1.1`): The action's interface has changed in
   a backward-compatible manner. New optional fields have been added to the request or
   response. Existing fields retain their semantics. Implementations that support
   version `1.0` MUST be able to process version `1.1` messages by ignoring unknown
   fields.

2. **Major version bump** (e.g., `1.0` → `2.0`): The action's interface has changed in
   a backward-incompatible manner. Required fields have been added, removed, or
   redefined. Semantics of existing fields have changed. A major version bump MUST be
   treated as a new action for purposes of capability enforcement and action discovery.

**Coexistence during migration.** When a major version bump occurs:

- Both versions of the action MAY coexist in the action registry during a migration
  period. The agent advertises both versions in the `supported_versions` array of the
action's single ActionDescriptor entry (§2.1).
- The old version's `action_id` remains unchanged. The new version's `action_id` also
  remains unchanged — the version distinction is carried in `payload.version`, not in
  `action_id`.
- Agents SHOULD support the latest version and MAY support older versions concurrently.
- The migration period SHOULD be documented in the action's `description` field.

**Version negotiation.** When a requesting agent sends a message without a
`payload.version` field, the version is exactly `"1.0"` (ARSIA-Core.md §4.4.2) — the
receiving agent MUST process the message under version `1.0` semantics, and MUST
respond with `not_implemented` if it no longer supports `1.0`. (Draft-01's "latest
supported version" default was non-deterministic between peers and is removed.) When a `payload.version` field is present and the
receiving agent does not support that version, it MUST respond with error code
`not_implemented` (ARSIA-Core.md §11.2) and include the supported version range in the
error details:

<!-- example: arsia-message.schema.json; partial=/v,/id,/ts,/from,/to,/intent -->
```json
{
  "payload": {
    "type": "com.example.notes/delete",
    "error": {
      "code": "not_implemented",
      "description": "Action version 1.0 is no longer supported",
      "details": {
        "supported_versions": {
          "min": "2.0",
          "max": "2.1"
        }
      }
    }
  }
}
```

---

## 3. Human Oversight Signaling (EU AI Act Art. 14)

### 3.1 Rationale

The EU AI Act (Regulation 2024/1689) establishes human oversight as a fundamental
requirement for high-risk AI systems. Article 14(1) states: "High-risk AI systems
shall be designed and developed in such a way, including with appropriate
human-machine interface tools, that they can be effectively overseen by natural persons
during the period in which they are in use." This is a legal obligation for high-risk
AI systems, applicable from 2 December 2027 for Annex III systems and from 2 August 2028
for Annex I systems (Article 113(c)).

Article 14(4) further specifies the concrete capabilities that oversight measures must
provide. The oversight measures must enable the natural person to whom oversight is
assigned to: (a) correctly understand the relevant capacities and limitations of the
high-risk AI system and be able to duly monitor its operation; (b) remain aware of the
possible tendency of automatically relying on the output produced by a high-risk AI
system (automation bias); (c) be able to correctly interpret the high-risk AI system's
output; and (d) be able to decide, in any particular situation, not to use the
high-risk AI system or to otherwise disregard, override or reverse the output of the
high-risk AI system. Subsection (d) is particularly significant: it requires a
mechanism through which a human can prevent, block, or undo an AI system's action.

Current agent communication protocols do not address these requirements. In existing
protocols such as MCP and A2A, an agent either executes a requested action or refuses
it — there is no protocol-level mechanism for an agent to signal "I intend to execute
this action, but I need a human to approve it first." Without such a mechanism, human
oversight must be implemented entirely at the application layer, which means it is
neither interoperable nor verifiable. One agent framework's oversight implementation
cannot interact with another's. An auditor cannot verify that oversight occurred by
examining protocol-level traces, because the oversight flow is invisible at the
protocol level.

ARSIA fills this gap by defining `pending_approval` and `approval_decision` as
first-class message intents (ARSIA-Core.md §4.1.6). When an agent receives a request
for an action that requires human oversight, it does not execute the action. Instead,
it responds with a `pending_approval` message that describes what will happen if the
action is approved, and waits for an `approval_decision` message from an agent with
the `arsiaprotocol.oversight.approve` capability. This mechanism is fully interoperable: any
ARSIA-conformant agent can participate in the oversight flow, regardless of its
internal architecture, AI framework, or deployment model. The oversight flow is
auditable: every step is a signed ARSIA message with a unique identifier, a timestamp,
and a correlation identifier that links it to the original request. And the oversight
flow is enforceable: an agent that attempts to execute a high-risk action without going
through the oversight flow violates the protocol specification and can be detected
through conformance testing (§6) and audit trail analysis.

### 3.2 The `pending_approval` Message

When an agent receives a `request` message for an action whose effective oversight
set (ARSIA-Core.md §4.3.10.5, with the `executor-policy` sources of §4.3.10.2)
includes `"required_before_execution"`, the agent MUST follow the procedure defined
in this section. Deviation from this procedure is a conformance violation. The
sources that can demand prior approval are the message's declared or profile-filled
mode, the ActionDescriptor (§2.1), the gateway CapabilityPolicy carried by the access
token (ARSIA-Core.md §6.1) and the executing agent's risk assessment
(ARSIA-Assets.md §5.2). A requirement from a dynamic source is communicated by the
`pending_approval` itself, before any effect of the action.

#### Step 1: Do not execute the action.

The receiving agent MUST NOT execute the requested action. The request is acknowledged
but held in a pending state. No side effects of the action may occur before approval
is received. If the action involves external calls, database writes, message
dispatches, or any other observable side effects, none of these may be initiated.

#### Step 2: Construct the `pending_approval` message.

The receiving agent MUST construct and send a response message with the following
characteristics:

**Envelope fields:**

| Field             | Value                                                         |
|-------------------|---------------------------------------------------------------|
| `v`               | `"2.0"` (current protocol version)                           |
| `id`              | A new UUID v4 (unique identifier for this pending_approval)   |
| `ts`              | Current UTC timestamp with millisecond precision              |
| `from`            | The receiving agent's agent-id                                |
| `to`              | The original sender's agent-id (from the request's `from`)    |
| `intent`          | `"pending_approval"`                                          |
| `correlation_id`  | The `id` of the original request message (its immediate causal parent) |
| `root_request_id` | The `id` of the original request message (ARSIA-Core.md §4.2.4) |
| `expires_at`      | The approval deadline (see Step 3 below)                      |
| `security`        | Signed by the receiving agent's Ed25519 key                   |

**Payload fields:**

The `payload` object MUST have the following structure:

```json
{
  "type": "arsiaprotocol.oversight/pending",
  "args": {
    "action_id": "<the action_id from the ActionDescriptor>",
    "original_request_id": "<the id of the original request message>",
    "approval_deadline": "<RFC 3339 timestamp — decisions received from this instant are late>",
    "approver_capability": "arsiaprotocol.oversight.approve",
    "context": "<human-readable description of what will happen if approved>",
    "risk_level": <integer — the action's risk_level from its ActionDescriptor>,
    "request_payload_hash": "<SHA-256 of the original request's payload>"
  },
  "explanation": <object or null — preliminary explanation if explainability_required (§5.2)>,
  "obligation_resolution": { <effective obligation resolution — ARSIA-Core.md §4.4.8> }
}
```

**Field definitions for `payload.args`:**

**`action_id`** (string, REQUIRED): The `action_id` from the ActionDescriptor of the
action being held for approval. This tells the approver which action is pending.

**`original_request_id`** (string, REQUIRED): The `id` field from the original request
message that triggered this oversight flow. This provides traceability from the
approval back to the originating request. It MUST equal the envelope's
`root_request_id` (ARSIA-Core.md §4.2.4); receivers MUST reject a `pending_approval`
whose two values differ with error code `invalid_request`.

**`approval_deadline`** (string, REQUIRED): An RFC 3339 timestamp with millisecond
precision (same format as ARSIA-Core.md §4.1.3) indicating the instant from which an
`approval_decision` is no longer accepted: a decision is in time only when received
strictly before it, on the executing agent's clock (§3.4). From this instant, decisions
newly received are late. Expiry is resolved under §3.4, Path 3, after verification of
the decisions received before the deadline and only while the flow remains pending.
The `approval_deadline` MUST equal the `expires_at` field of the `pending_approval`
envelope. That equality grants no extension of the deadline.

**`approver_capability`** (string, REQUIRED): The capability string required to approve
this action. For v2.0, this MUST be `"arsiaprotocol.oversight.approve"`. This field exists to
support future versions where different actions may require different approval
capabilities.

**`context`** (string, REQUIRED): A human-readable description of what will happen if
the action is approved. This description is intended for the natural person who will
make the approval decision. It MUST be written in plain language, MUST NOT exceed 1024
characters, and SHOULD include: the nature of the action, the key parameters, and the
potential consequences. This field directly supports EU AI Act Article 14(4)(a) — the
requirement that oversight measures enable the natural person to correctly understand
the relevant capacities and limitations of the AI system.

**`risk_level`** (integer, REQUIRED): The `risk_level` from the action's
ActionDescriptor. This allows the approver and the oversight system to apply
risk-appropriate handling (e.g., different UI treatments for risk 7 vs. risk 10
actions).

**`request_payload_hash`** (string, REQUIRED): The SHA-256 (lowercase hex) of the
original request's payload, computed as `payload_hash` in ARSIA-State.md §7.1 (RFC 8785
form, or the JWE string when encrypted). It binds the approval to the parameters
presented to the approver: an `approval_decision` applies only to the request whose
payload has this hash (§3.4).

**Closed field set.** `payload.args` contains exactly the members defined in this
step. A receiver MUST reject a `pending_approval` with any other member in
`payload.args` with error code `invalid_request`.

**Field definition for `payload.obligation_resolution`:**

**`obligation_resolution`** (object, REQUIRED): The effective obligation resolution of
the held request (ARSIA-Core.md §4.4.8). Its oversight axis records the
prior-approval requirement and every source that demanded it, so the requester learns
the effective requirement and its origin before any effect of the action.

**Field definition for `payload.explanation`:**

**`explanation`** (object or null, OPTIONAL but RECOMMENDED): When the action's
ActionDescriptor has `explainability_required: true`, this field SHOULD contain a
preliminary explanation object conforming to §5.2. The preliminary explanation provides
the approver with the agent's reasoning and confidence before the action executes. This
supports Article 14(4)(c) — the ability to correctly interpret the AI system's output.
When `explainability_required` is `false`, this field MAY be `null` or omitted.

#### Step 3: Set the approval deadline.

The `approval_deadline` (and the corresponding `expires_at` envelope field) MUST be set
according to the following rules:

1. The deadline MUST be in the future relative to the `ts` of the `pending_approval`
   message.

2. The deadline MUST NOT exceed 24 hours from the `ts` of the `pending_approval`
   message. This upper bound prevents actions from lingering indefinitely in a pending
   state.

3. The following deadlines are RECOMMENDED based on risk level:

   | Risk level | Recommended deadline | Rationale                              |
   |------------|----------------------|----------------------------------------|
   | 7          | 60 minutes           | Sufficient time for considered review  |
   | 8          | 60 minutes           | Sufficient time for considered review  |
   | 9          | 15 minutes           | Critical actions require prompt review |
   | 10         | 15 minutes           | Critical actions require prompt review |

4. The deadline is configurable per implementation. Agent operators MAY set shorter or
   longer deadlines within the 24-hour upper bound, based on their operational
   requirements and regulatory obligations.

#### Step 4: Deliver the `pending_approval` message.

The `pending_approval` message MUST be delivered to the original sender via the
standard ARSIA message delivery mechanism (ARSIA-Core.md §8). Additionally, the
agent SHOULD deliver the `pending_approval` message to any registered oversight
endpoints — that is, agents or systems that are configured to receive and act on
oversight requests. The mechanism for registering oversight endpoints is
implementation-defined.

### 3.3 The `approval_decision` Message

An `approval_decision` message is sent by an agent with the `arsiaprotocol.oversight.approve`
capability in response to a `pending_approval` message. The `approval_decision` carries
the human oversight decision: approve or deny.

**Envelope fields:**

| Field             | Value                                                           |
|-------------------|-----------------------------------------------------------------|
| `v`               | `"2.0"` (current protocol version)                             |
| `id`              | A new UUID v4 (unique identifier for this decision)            |
| `ts`              | Current UTC timestamp with millisecond precision                |
| `from`            | The approver agent's agent-id                                   |
| `to`              | The executing agent's agent-id (the agent that sent `pending_approval`) |
| `intent`          | `"approval_decision"`                                           |
| `correlation_id`  | The `id` of the `pending_approval` message (NOT the original request's `id`) |
| `root_request_id` | The `id` of the original request that initiated the interaction (equal to the `pending_approval`'s `root_request_id`, ARSIA-Core.md §4.2.4) |
| `capabilities`    | `["arsiaprotocol.oversight.approve"]`                                   |
| `security`        | Signed by the APPROVER's Ed25519 key, NOT the original agent's key |

**Payload fields:**

The `payload` object MUST have the following structure:

<!-- example: arsia-message.schema.json#/$defs/approval-decision-result @/result; template=/request_payload_hash -->
```json
{
  "type": "arsiaprotocol.oversight/decision",
  "result": {
    "decision": "approved",
    "approver_id": "agent:acme.oversight-dashboard",
    "request_payload_hash": "<request_payload_hash of the pending_approval>"
  }
}
```

**Field definitions for `payload.result`:**

**`decision`** (string, REQUIRED): The oversight decision. MUST be one of:
- `"approved"` — the action is approved for execution.
- `"denied"` — the action is denied; it MUST NOT be executed.

**`approver_id`** (string, REQUIRED): The agent-id of the approving agent or
human-authorizing system. This MUST match the `from` field of the `approval_decision`
envelope; a mismatch is rejected with `invalid_request` (§3.4, verification step 4).
This field provides an additional explicit record of who approved the action,
which is important for audit trail completeness.

**`reason`** (string, OPTIONAL but RECOMMENDED when `decision` is `"denied"`): A
human-readable explanation of why the decision was made. Maximum length: 512 characters.
When the decision is `"denied"`, providing a reason is strongly RECOMMENDED to enable
the requesting agent (or its operator) to understand why the action was blocked and
whether a modified request might be approved.

**`conditions`** (array of strings, OPTIONAL): Conditions attached to the approval.
When present, these conditions modify the scope or parameters of the approved action.
The executing agent MUST honour all conditions. Examples:

- `"amount reduced to 1000 EUR"` — the approver has constrained a financial parameter.
- `"valid for single execution only"` — the approval does not carry over to retries.
- `"notify compliance team after execution"` — a post-execution requirement.

**`request_payload_hash`** (string, REQUIRED): The `request_payload_hash` of the
`pending_approval` being decided, as presented to the approver. It binds the decision
to the action, parameters and context presented.

Conditions are free-text strings intended for the executing agent's operator to
interpret and implement. The ARSIA Protocol does not define a structured condition
language in v2.0. Implementations SHOULD document their supported condition formats.

**Capability requirement.** The `approval_decision` message MUST include
`"arsiaprotocol.oversight.approve"` in its `capabilities` array. The receiving agent MUST
verify that the approver's access token includes this capability in its scope. An
`approval_decision` message from an agent without the `arsiaprotocol.oversight.approve`
capability MUST be rejected with error code `forbidden` (ARSIA-Core.md §11.2).

> **Informative note.** The `capabilities` field carries different semantics depending
> on the message intent. On `request` messages, `capabilities` declares the permissions
> the sender is requesting from the receiver. On `approval_decision` messages,
> `capabilities` asserts the authority under which the approver is acting — the receiver
> verifies that the approver's access token scope includes
> `arsiaprotocol.oversight.approve`. This dual use enables runtime verification of the
> approver's credential without introducing a separate field.

**Signature requirement.** The `approval_decision` message MUST be signed by the
approver's Ed25519 key — NOT by the executing agent's key, and NOT by the original
requester's key. This ensures that the approval is cryptographically attributable to
the approving identity. The receiving agent MUST verify the signature per
ARSIA-Identity.md §3.1 (§3.4, verification step 1).

### 3.4 Execution After Approval

This section defines the normative behavior of the executing agent upon receiving an
`approval_decision` message: the verification every decision undergoes, then three
paths — approved, denied, and expired.

#### Verification of an `approval_decision`

Before an `approval_decision` takes effect — whether its `decision` is `"approved"` or
`"denied"` — the executing agent MUST verify, in this order:

1. its signature (ARSIA-Core.md §5.2; ARSIA-Identity.md §3.1) — on failure,
   `unauthorized`;
2. the access token presented with it (ARSIA-Core.md §6.4 steps 2–3, §6.5): its
   signature, a trusted issuer, `exp` and `iat`, `sub` equal to the decision's
   `from`, and `aud` equal to the decision's `to` within the issuer's audience
   policy — an invalid or expired token, or an untrusted issuer, gives
   `unauthorized`;
3. the approver's authority — `arsiaprotocol.oversight.approve` in the token's
   scope, matched exactly as a reserved capability (ARSIA-Core.md §6.4 step 5), and
   in the decision's `capabilities`; otherwise `forbidden`;
4. correlation and binding — `correlation_id` matches the `id` of a
   `pending_approval` the agent sent and still tracks (ARSIA-Core.md §4.2.1, rule
   1); `root_request_id` equals that `pending_approval`'s `root_request_id`
   (ARSIA-Core.md §4.2.4); `request_payload_hash` equals its `request_payload_hash`;
   and `result.approver_id` equals `from`; otherwise `invalid_request`;
5. deadline and pending state — the decision was received before the
   `approval_deadline`, and the `pending_approval` is still pending; otherwise
   `invalid_request`.

**Receipt instant.** Step 5 compares the instant at which the executing agent
receives the decision, on its own clock, with the `approval_deadline` it set: a
decision received strictly before the deadline is in time; one received at or after
the deadline is late. No clock-skew tolerance applies, since both instants are the
agent's own, and the result depends neither on the decision's `ts` nor on when a
timer runs. The tolerance of ARSIA-Core.md §8.3 still applies to the timestamps the
agent validates from other parties, including the token claims of step 2.

A decision received before the deadline keeps its eligibility as to the deadline
however late it is verified: the agent resolves the `pending_approval` as expired
(Path 3) only after every decision it received before the deadline has been
verified, and only if the `pending_approval` is then still pending. This eligibility
concerns the deadline only. Steps 1–3 — the signature with key resolution under
ARSIA-Core.md §5.2, and the token — are evaluated at the instant of verification, on
the agent's clock, never at the receipt instant: a decision received in time is not
exempt from authentication, nor from a revocation or cache refresh that applies when
it is verified.

**Rejected decisions.** A decision that fails a step is rejected with the code of the
first step it fails; a duplicate or late decision is rejected with `invalid_request`
only when it failed no earlier step. It neither approves nor denies the action: it is
not admitted to the flow, does not count toward the required approvals (§3.6), does
not consume its approver, does not resolve the `pending_approval`, and does not
change a recorded outcome. The executing agent MUST log it with an audit record of
`event_type` `"decision_rejected"` (ARSIA-State.md §7.1), whether or not it replies,
and SHOULD reply to the sender with an `error` carrying that code. A decision received
at or after the deadline is further handled per *Late arrival of `approval_decision`*
below; one for a `pending_approval` already resolved, per ARSIA-Core.md §4.2.1,
rules 2 and 3.

A decision that passes every step is admitted to the flow and follows Path 1 or
Path 2.

#### Path 1: Decision is `"approved"`

**Step 1: Verify the decision.** The executing agent MUST NOT execute the action
unless the decision was admitted by the verification above and, under §3.6, the
required approvals have been admitted.

**Step 2: Execute the action.**

If all verification steps pass, the executing agent MUST execute the action with the
parameters of the original request — those whose hash the approval binds — applying
the decision's `conditions` (e.g., reducing an amount, restricting scope). Conditions
only restrict the approved execution. A change of the action or of its parameters
other than one a condition imposes is a material change: the approval does not cover
it, the agent MUST NOT execute the changed action under it, and a new
`pending_approval` is required.

**Step 3: Respond to the original requester.**

After execution completes (successfully or with an error), the executing agent MUST send
a response to the ORIGINAL requester — that is, the agent identified in the `from` field
of the original request message. The response is NOT sent to the approver (unless the
approver and the requester happen to be the same agent). The response is a standard
ARSIA response or error message (ARSIA-Core.md §4.1.6) with `correlation_id` set to the
`id` of the original request message. The response or error carries
`payload.obligation_resolution` (ARSIA-Core.md §4.4.8); in the asynchronous pattern
the terminal result of §4.3 carries it.

**Step 4: Record in audit trail.**

The executing agent MUST log all messages in the audit trail: the original request, the
`pending_approval`, the `approval_decision`, and the final response or error. See §3.5
for the detailed audit requirements.

**Step 5: Open the post-execution review.**

If the effective oversight set also includes `"required_within_24h"` or
`"required_post_execution"`, the executing agent opens the review of §3.9 when
execution ends.

#### Path 2: Decision is `"denied"`

Upon admitting an `approval_decision` with `decision: "denied"` (verification above):

**Step 1: Do not execute the action.**

The executing agent MUST NOT execute the action. No side effects may occur.

**Step 2: Respond to the original requester with an error.**

The executing agent MUST send an error message to the original requester with the
following structure:

<!-- example: arsia-message.schema.json; template=/correlation_id,/root_request_id; partial=/v,/id,/ts,/from,/to -->
```json
{
  "intent": "error",
  "correlation_id": "<id of the original request>",
  "root_request_id": "<id of the original request>",
  "payload": {
    "type": "<original request's payload.type>",
    "error": {
      "code": "forbidden",
      "description": "Action denied by human oversight",
      "details": {
        "oversight_decision": "denied",
        "approver_id": "<agent-id of the approver>",
        "reason": "<reason from the approval_decision, or null>"
      }
    }
  }
}
```

The error code MUST be `"forbidden"` (ARSIA-Core.md §11.2). The `details` object MUST
include `oversight_decision: "denied"` to distinguish this from a standard authorization
failure. The `approver_id` and `reason` fields provide traceability.

**Step 3: Record in audit trail.**

The executing agent MUST log the denial in the audit trail. See §3.5.

#### Path 3: Approval deadline expired

Path 3 applies only to a `pending_approval` still pending: a flow already denied,
expired or proceeding to execution is never resolved again by expiry.

When the `approval_deadline` is reached, on the executing agent's clock, while the
`pending_approval` is still pending — once every decision received before the deadline
has been verified, no denial has been admitted and the required approvals have not been
admitted:

**Step 1: Do not execute the action.**

The executing agent MUST NOT execute the action. The pending state is resolved as
expired.

**Step 2: Respond to the original requester with an error.**

The executing agent MUST send an error message to the original requester with the
following structure:

<!-- example: arsia-message.schema.json; template=/correlation_id,/root_request_id,/payload/type,/payload/error/details/deadline; partial=/v,/id,/ts,/from,/to -->
```json
{
  "intent": "error",
  "correlation_id": "<id of the original request>",
  "root_request_id": "<id of the original request>",
  "payload": {
    "type": "<original request's payload.type>",
    "error": {
      "code": "forbidden",
      "description": "Action approval deadline exceeded",
      "details": {
        "oversight_decision": "expired",
        "deadline": "<the approval_deadline timestamp>"
      }
    }
  }
}
```

The error code MUST be `"forbidden"`. The `details` object MUST include
`oversight_decision: "expired"` and the `deadline` that was exceeded.

**Step 3: Record in audit trail.**

The executing agent MUST log the expiry in the audit trail. See §3.5.

**Late arrival of `approval_decision`.** If an `approval_decision` is received at or
after the `approval_deadline`, the executing agent MUST NOT execute the action
regardless of the decision value. It MUST log the late decision as a rejected
decision (`decision_rejected`, above), with the code the verification determines:
`invalid_request` when no step before the deadline check failed. The executing agent
SHOULD respond to the approver with an `error` carrying that code — for a decision
that failed no earlier step, `invalid_request` with
`details: { "deadline_exceeded": true }`.

### 3.5 Audit Trail for Oversight

Every `pending_approval` → `approval_decision` cycle MUST generate a minimum of four
audit records. These records form a complete, cryptographically linked chain that
enables auditors to reconstruct the full oversight flow. Each record is an
`ArsiaAuditRecord` (ARSIA-State.md §7.1): the tables below list the fields specific to
each step, and every record also carries the base fields defined there.

#### Record 1: Original Request

| Field          | Value                                                        |
|----------------|--------------------------------------------------------------|
| `event_type`   | `"request"`                                                  |
| `message_id`   | The `id` of the original request message                     |
| `timestamp`    | The `ts` of the original request message                     |
| `from_agent`   | The requesting agent's agent-id                              |
| `to_agent`     | The executing agent's agent-id                               |
| `payload_type` | The `payload.type` of the request                            |
| `risk_level`   | The risk_level from the ActionDescriptor                     |
| `payload_hash` | SHA-256 hash of the canonicalized request payload            |

This record captures the initiating event — what was requested, by whom, and when.

#### Record 2: Pending Approval Signal

| Field          | Value                                                        |
|----------------|--------------------------------------------------------------|
| `event_type`   | `"pending_approval"`                                         |
| `message_id`   | The `id` of the pending_approval message                     |
| `timestamp`    | The `ts` of the pending_approval message                     |
| `from_agent`   | The executing agent's agent-id                               |
| `to_agent`     | The original requester's agent-id                            |
| `correlation_id` | The `id` of the original request                           |
| `root_request_id` | The `id` of the original request                          |
| `approval_deadline` | The approval deadline timestamp                          |
| `payload_hash` | SHA-256 hash of the canonicalized pending_approval payload   |

This record captures the moment the agent paused execution and requested human
oversight. The presence of this record proves that the agent did not execute the action
autonomously.

#### Record 3: Approval Decision

| Field          | Value                                                        |
|----------------|--------------------------------------------------------------|
| `event_type`   | `"approval_decision"`                                        |
| `message_id`   | The `id` of the approval_decision message                    |
| `timestamp`    | The `ts` of the approval_decision message                    |
| `from_agent`   | The approver's agent-id                                      |
| `to_agent`     | The executing agent's agent-id                               |
| `correlation_id` | The `id` of the pending_approval message                   |
| `root_request_id` | The `id` of the original request                          |
| `decision`     | `"approved"` or `"denied"`                                   |
| `approver_id`  | The approver's agent-id (from payload.result.approver_id)    |
| `reason`       | The reason field from the decision (if provided, else null)  |
| `payload_hash` | SHA-256 hash of the canonicalized approval_decision payload  |

This record captures who made the oversight decision, what they decided, and why. In the
case of a deadline expiry (Path 3), this record is replaced by a record with
`event_type: "approval_expired"` and `decision: "expired"`.

One Record 3 is written for each `approval_decision` verified and admitted to the flow
(§3.4). A rejected decision is logged as `decision_rejected` and is not a Record 3.

#### Record 4: Final Response or Error

| Field          | Value                                                        |
|----------------|--------------------------------------------------------------|
| `event_type`   | `"response"` or `"error"`                                    |
| `message_id`   | The `id` of the final response or error message              |
| `timestamp`    | The `ts` of the final response or error message              |
| `from_agent`   | The executing agent's agent-id                               |
| `to_agent`     | The original requester's agent-id                            |
| `correlation_id` | The `id` of the original request                           |
| `root_request_id` | The `id` of the original request                          |
| `outcome`      | `"success"`, `"denied"`, `"expired"`, or `"error"`           |
| `payload_hash` | SHA-256 hash of the canonicalized response/error payload     |

This record captures the final outcome — whether the action was executed and what
result was produced.

#### Regulatory support

These four audit records provide technical records that support the operator's
compliance with the following regulatory requirements (statement subject to legal
review). Whether they discharge any obligation in a given deployment is the
operator's legal determination, made within the tamper-evidence scope defined by
ARSIA-State.md §7.2:

**EU AI Act Art. 17 (Quality management system).** Article 17(1)(k) requires that
the quality management system of providers of high-risk AI systems include "systems
and procedures for record-keeping of all relevant documentation and information". The
four-record chain provides a
record of every oversight decision, from request through approval to outcome, with
tamper evidence within the scope defined by ARSIA-State.md §7.2 (mid-chain
modification and removal against an independently held head; see its explicit
exclusions).

**EU AI Act Art. 26(6) (Deployer logging obligations).** Article 26(6) requires
deployers to keep logs automatically generated by the high-risk AI system, to the
extent such logs are under their control, for a period appropriate to the intended
purpose of the high-risk AI system, of at least six months. The ARSIA audit trail
retention mechanism (configured via `retention` in the ActionDescriptor or the
compliance profile's `retention_minimum`) ensures that these records are retained for
the required duration — for EU-AI-ACT-HIGH-RISK, `"P6M"`: six calendar months per
ARSIA-Core.md §4.3.6.4.1, preserving the calendar semantics of Article 26(6).
There is no risk-level-based retention floor: retention minimums come exclusively
from the applicable compliance profile (`retention_minimum`, ARSIA-State.md §6) or
an explicit `retention` override. A high-risk action under EU-AI-ACT-HIGH-RISK is
therefore retained for at least `"P6M"` because of the profile, not because of its
`risk_level`.

**EU AI Act Art. 14(4)(d) (Ability to override).** The denied path (Path 2 in §3.4)
and the expired path (Path 3 in §3.4) demonstrate that a human can prevent an AI system's
action from executing. The audit record for a denied decision explicitly captures the
`approver_id` and `reason`, providing evidence that a natural person exercised their
override authority.

#### Correlation chain integrity

All four records are linked by correlation identifiers:

```
Request (id: R)
    +-- PendingApproval (id: P, correlation_id: R)
          +-- ApprovalDecision (id: D, correlation_id: P)
    +-- Response (id: X, correlation_id: R)
```

Auditors can traverse this chain in either direction: forward from the request to see
what happened, or backward from the response to verify that the oversight flow was
followed. The `payload_hash` fields in each record enable integrity verification: any
modification to a message after it was audited will produce a different hash.

A post-execution review adds the records of §3.9.5; they are not part of the oversight
cycle counted here.

### 3.6 Multiple Approval Levels (OPTIONAL)

For actions with `risk_level` of 10, implementations MAY require multiple independent
approvals before execution. This section defines the protocol-level semantics for
multi-approval workflows. Support for multiple approval levels is OPTIONAL in ARSIA
Protocol v2.0; implementations SHOULD support single-approval for all risk levels at
minimum.

**ActionDescriptor extension.** To support multiple approvals, the ActionDescriptor MAY
include an additional field:

**`required_approvals`** (integer, OPTIONAL, default: 1): The number of independent
`approval_decision` messages with `decision: "approved"` that must be admitted (§3.4)
before the action can execute. Each approval MUST come from a distinct approver — that is,
from agents with different `from` values.

**Flow modification.** When `required_approvals` > 1:

1. The executing agent sends a single `pending_approval` message (as in §3.2).

2. The executing agent waits for `required_approvals` distinct `approval_decision`
   messages admitted (§3.4), each with `decision: "approved"`, each from a different
   approver agent, and each with the `arsiaprotocol.oversight.approve` capability.

3. If a `denied` decision is verified and admitted (§3.4), the action is denied
   immediately — the executing agent does not wait for the remaining approvals. The denial path
   (§3.4, Path 2) applies.

4. If the flow is still pending under the conditions of §3.4, Path 3 — the deadline
   reached, every decision received before it verified, and the required approvals not
   admitted — the action is denied via the expiry path.

5. Every `approval_decision` verified and admitted to the flow (§3.4) MUST be logged
   as a separate audit record (§3.5, Record 3). For a multi-approval flow that ends
   with a decision (all required approvals admitted, or a denial), the total number of
   audit records is N + 3: Record 1, Record 2, one Record 3 for each of the N decisions
   admitted (including any denial), and Record 4; rejected decisions
   (`decision_rejected`) are not counted.

   For a flow that ends by deadline expiry (step 4), the total is N + 4: Record 1,
   Record 2, one Record 3 for each of the N decisions admitted before the expiry, one `approval_expired` record, and Record 4. With N = 0 this is
   the four-record expiry cycle of §3.5.

**Ordering.** Approvals may arrive in any order. The executing agent MUST track the set
of approvers who have approved and MUST NOT accept duplicate approvals from the same
approver.

**Implementation guidance.** Multiple approval levels are intended for actions where a
single point of approval represents unacceptable concentration of authority. Examples
include large financial transactions, changes to regulatory classifications, and
modifications to safety-critical configurations. Most implementations SHOULD start with
`required_approvals: 1` and escalate to multiple approvals only when operational
experience or regulatory guidance demands it.

### 3.7 Execution Without Prior Approval

When the effective oversight set of a request (ARSIA-Core.md §4.3.10.5, with the
`executor-policy` sources of §4.3.10.2) does not include `"required_before_execution"`,
the flow of §3.2–§3.6 does NOT apply and the agent proceeds to execution without
sending a `pending_approval` message.

**Normative procedure:**

1. The receiving agent validates the envelope, verifies authorization per
   ARSIA-Core.md §6.4 and resolves the effective obligations per ARSIA-Core.md
   §4.3.10, including its `executor-policy` sources, before any effect of the action.

2. If validation, authorization and resolution succeed, the agent transitions from
   REQUESTED to EXECUTING (§4.1). No `pending_approval` message is sent, and no
   `approval_decision` is expected.

3. The agent executes the action and reports the outcome with a `response` or `error`
   that carries `payload.obligation_resolution` (ARSIA-Core.md §4.4.8), or with the
   terminal result of §4.3 in the asynchronous pattern.

4. If the effective audit obligation is `true` (ARSIA-Core.md §4.3.10.5), a minimum of
   two audit records MUST be generated: one for the request (`event_type: "request"`)
   and one for the terminal response or error (`event_type: "response"` or
   `"error"`).

5. If the effective oversight set includes `"required_within_24h"` or
   `"required_post_execution"`, the agent opens the review of §3.9 when execution
   ends.

**No source is a veto.** An ActionDescriptor with `human_oversight_required: false`
demands nothing. It does not prohibit prior approval demanded by another source, and
no source removes a requirement contributed by another (ARSIA-Core.md §4.3.10.5).

**Prohibition on unnecessary prior approval.** An agent MUST NOT send a
`pending_approval` message for a request whose effective oversight set does not
include `"required_before_execution"`. An operator that requires prior approval for an
action does so through a source of that set — for example by setting
`human_oversight_required: true` and publishing the revised ActionDescriptor (§2.3).

### 3.8 Implementation Guidance: Approval Rate Management

High-frequency agent interactions can generate a volume of `pending_approval` messages
that overwhelms human approvers. When an approver receives more approval requests than
they can meaningfully evaluate, the quality of human oversight degrades — approvers
begin rubber-stamping decisions without genuine review, which defeats the purpose of the
oversight mechanism defined in §3.2–§3.6. This failure mode is commonly known as
"consent fatigue" or "approval fatigue."

The ARSIA Protocol already provides mechanisms that implementations can combine to
mitigate approval fatigue without changes to the wire protocol:

- **Risk-based prioritization.** The `risk_level` field in the ActionDescriptor (§2.1)
  classifies each action on a 0–10 severity scale. Implementations can use this field
  to route only high-risk approvals (e.g., `risk_level` at or above a
  deployment-defined threshold) to human reviewers, while lower-risk approvals are
  handled through automated policy evaluation or deferred batch review.

- **Deadline-bounded waiting.** The `approval_deadline` field (§3.2, Step 3) ensures
  that no approval request blocks indefinitely. Implementations can use short deadlines
  for time-sensitive actions and longer deadlines for actions that can tolerate batched
  review cycles.

- **Separation of authority.** The `required_approvals` mechanism (§3.6) distributes
  the approval burden across multiple reviewers for the highest-risk actions, reducing
  the likelihood that a single fatigued approver becomes a single point of failure.

Implementations are encouraged to consider additional strategies suited to their
deployment context, such as: aggregating pending approvals into a dashboard view rather
than delivering them as individual notifications; applying per-agent rate limits on
approval request frequency; grouping low-risk approvals into periodic batches for
consolidated review; and routing only escalation-worthy requests (those above a
deployment-specific risk threshold) to human reviewers. The specific thresholds,
grouping algorithms, and routing policies are deployment decisions and are not
prescribed by this specification.

### 3.9 Post-Execution Review

A post-execution review is the human review of an action that executed without prior
approval of its result, required by the modes `"required_within_24h"` and
`"required_post_execution"` (ARSIA-Core.md §4.3.6.5). It is distinct from prior
approval: `pending_approval` keeps meaning that execution is blocked, while a review
concerns an execution that has already occurred. A review never blocks, reopens or
rewrites the execution: the execution lifecycle (§4.1) and the review states
(§3.9.4) are separate. A negative review decision does not make the action not
executed; it starts remediation (§3.9.4). Review deadlines are ARSIA controls:
regulatory notification periods — for example DORA major-incident reporting under
Delegated Regulation (EU) 2025/301 Art. 5 — run independently and never wait for this
review.

#### 3.9.1 Opening Conditions and Configuration

When the effective oversight set of a request includes `"required_within_24h"` or
`"required_post_execution"`, the executing agent MUST, during resolution and before
any effect of the action, establish its review configuration:

- a review endpoint, to which review notices are delivered;
- an escalation destination (§3.9.4);
- for `"required_post_execution"`, the `post_execution_review_period` of the action's
  ActionDescriptor (§2.1).

If an element is missing, the oversight axis has the conflict defined in
ARSIA-Core.md §4.3.10.5 (Review configuration), and the agent MUST reject the request
with error code `invalid_request` and diagnostic `obligation_conflict`
(ARSIA-Core.md §4.3.10.6). The action is not executed, and the rejection is audited
(`rejection_cause: "compliance"`).

The review is opened when execution ends: when the action reaches COMPLETED, or FAILED
after having entered EXECUTING (§4.1). An action that never entered EXECUTING has no
review. When the effective set also includes `"required_before_execution"`, the review
follows the approved execution (§3.4, Path 1 Step 5).

#### 3.9.2 Execution Instant and Review Deadlines

The **terminal result** of an execution is the signed `response` or `error` envelope
that reports its outcome, materialized by the executing agent when the action reaches
COMPLETED or FAILED. In the synchronous pattern it is the message sent to the
requester. In the asynchronous pattern (§4.3) it is the envelope returned by
`result_url`, for completion and failure alike; the initial acknowledgment (`status:
"accepted"`) is not a terminal result and never opens a review. The **execution
instant** is the `ts` of the terminal result, set when the action reaches its terminal
state. Delivery delays, retransmission of the same envelope, polling and later
retrieval change neither the terminal result nor the execution instant.

- For `"required_within_24h"`, the deadline is the execution instant plus 24 hours
  (86 400 seconds); no source extends it.
- For `"required_post_execution"`, the deadline is the execution instant plus
  `post_execution_review_period`, with the calendar arithmetic of ARSIA-Core.md
  §4.3.6.4.1.

When both modes apply, the review carries one obligation per mode, each with its own
deadline, and a single review decision satisfies every open obligation of the review.
The review's `review_deadline` is the earliest obligation deadline.

A review deadline is unrelated to the `expires_at` of any message: `expires_at` bounds
the processing of a message, while a review deadline determines when an obligation is
overdue (§3.9.4).

#### 3.9.3 Messages

The three messages below are `event` messages (ARSIA-Core.md §4.1.6). They are not
operations, so the high-risk requirement set does not apply to them (ARSIA-Core.md
§4.3.10.3). Each MUST be signed by its sender (ARSIA-Core.md §5.1), and its receiver
MUST verify that signature (ARSIA-Core.md §5.2). Each carries `correlation_id` and
`root_request_id` and is audited (§3.9.5). The requirements of §3.3–§3.4 for
`approval_decision` apply to them only where this section states them.

**Review notice.** When the review is opened, the executing agent MUST send an `event`
with payload type `arsiaprotocol.oversight/review-pending` to its review endpoint, and
MAY send it to the original requester. Its `correlation_id` is the `id` of the
terminal result and its `root_request_id` the `id` of the original request.

<!-- example: arsia-message.schema.json#/$defs/review-pending-data @/data; template=/original_request_id,/execution_message_id,/executed_at,/result_hash,/obligations/0/deadline,/review_deadline -->
```json
{
  "type": "arsiaprotocol.oversight/review-pending",
  "data": {
    "action_id": "com.example.moderation/remove-content",
    "original_request_id": "<id of the original request>",
    "execution_message_id": "<id of the terminal result>",
    "executed_at": "<execution instant>",
    "outcome": "success",
    "result_hash": "<SHA-256 of the terminal result's payload>",
    "obligations": [
      { "mode": "required_within_24h", "deadline": "<executed_at + 24 h>", "period_source": null }
    ],
    "review_deadline": "<earliest obligation deadline>",
    "reviewer_capability": "arsiaprotocol.oversight.approve",
    "context": "<plain-language description of what was executed and its result>",
    "risk_level": 6
  }
}
```

`payload.data` contains exactly these members:

- `action_id` (string, REQUIRED);
- `original_request_id` (UUID v4, REQUIRED): equal to `root_request_id`;
- `execution_message_id` (UUID v4, REQUIRED): the terminal result's `id`, equal to
  `correlation_id`;
- `executed_at` (RFC 3339, REQUIRED): the execution instant;
- `outcome` (REQUIRED): `"success"` or `"error"`;
- `result_hash` (string, REQUIRED): the SHA-256 of the terminal result's payload,
  computed as `payload_hash` in ARSIA-State.md §7.1; it identifies the reviewed
  result;
- `obligations` (array, REQUIRED, one entry per post-execution mode): each with `mode`,
  `deadline` and `period_source` — the ActionDescriptor source identification
  (ARSIA-Core.md §4.3.10.2) for `"required_post_execution"`, `null` for
  `"required_within_24h"`;
- `review_deadline` (RFC 3339, REQUIRED);
- `reviewer_capability` (string, REQUIRED): `"arsiaprotocol.oversight.approve"`;
- `context` (string, REQUIRED): a plain-language description of what was executed and
  its result, at most 1024 characters;
- `risk_level` (integer, REQUIRED): from the ActionDescriptor.

**Review decision.** An agent holding `arsiaprotocol.oversight.approve` decides a
review by sending to the executing agent an `event` with payload type
`arsiaprotocol.oversight/review-decision`. Its `correlation_id` is the review notice's
`id`, its `root_request_id` the original request's `id`, its `capabilities`
`["arsiaprotocol.oversight.approve"]`, and it is signed with the reviewer's key.

<!-- example: arsia-message.schema.json#/$defs/review-decision-data @/data; template=/execution_message_id,/result_hash -->
```json
{
  "type": "arsiaprotocol.oversight/review-decision",
  "data": {
    "decision": "confirmed",
    "reviewer_id": "agent:acme.oversight-dashboard",
    "execution_message_id": "<as in the review notice>",
    "result_hash": "<as in the review notice>",
    "reason": null
  }
}
```

`payload.data` contains exactly: `decision` — `"confirmed"` (reviewed, no objection)
or `"objected"` (the reviewer objects to the executed action or its result);
`reviewer_id` — equal to `from`; `execution_message_id` and `result_hash` — equal to
the notice's; and `reason` — string or null, at most 512 characters, RECOMMENDED when
`"objected"`.

**Verification of a review decision.** Before recording a review decision, the
executing agent MUST verify, in this order:

1. its signature (ARSIA-Core.md §5.2) — on failure, `unauthorized`;
2. the token presented with it (ARSIA-Core.md §6.4 step 3, §6.5) — an invalid or
   expired token, or an untrusted issuer, gives `unauthorized`;
3. the reviewer's authority — `arsiaprotocol.oversight.approve` in the token's scope
   and in `capabilities`; otherwise `forbidden`;
4. correlation and binding — `correlation_id` matches a review notice the agent sent
   and still tracks; `root_request_id`, `execution_message_id` and `result_hash` equal
   the notice's; `reviewer_id` equals `from`; otherwise `invalid_request`.

A decision that fails verification is not recorded as a decision: the agent MUST log
it with an audit record of `event_type` `"decision_rejected"` (ARSIA-State.md §7.1)
and SHOULD reply with an `error` carrying the code stated. The first verified
decision decides the review. A later decision for the same review MUST NOT change the
recorded outcome; the agent MUST log it with an audit record of `event_type`
`"decision_rejected"` and SHOULD reply `invalid_request` (ARSIA-Core.md §4.2.1, rule
2). A decision received after an obligation deadline is not rejected for that reason:
it is processed per §3.9.4.

**Overdue notice.** For each obligation that becomes overdue, the executing agent MUST
send to its escalation destination an `event` with payload type
`arsiaprotocol.oversight/review-overdue`. Its `correlation_id` is the review notice's
`id` and its `root_request_id` the original request's `id`; `payload.data` contains
exactly `action_id`, `original_request_id`, `execution_message_id`, `mode` and
`deadline` of the overdue obligation.

#### 3.9.4 Review States and Timing

A review is in one of four states:

- `pending` — opened, no verified decision, no obligation deadline reached;
- `overdue` — at least one obligation deadline reached without a verified decision;
- `completed` — a verified decision was received before every obligation deadline;
- `completed_late` — a verified decision was received at or after an obligation
  deadline.

`completed` and `completed_late` are terminal; `overdue` is not (ARSIA-Core.md
§4.2.1).

**Timing.** An obligation is overdue from its deadline inclusive: a decision received
at an instant equal to or later than the deadline is late for that obligation. The
receipt instant is the instant the executing agent receives the decision, on its own
clock; no clock-skew tolerance applies, since both instants are the agent's own.
Lateness and overdue status depend only on the deadlines and the receipt instant,
never on when a timer runs. When the agent processes a decision received after one or
more obligation deadlines for which it has not yet recorded the overdue fact, it MUST
first record those overdue facts and send their overdue notices, and then record the
decision as late.

**Overdue fact.** When an obligation's deadline is reached without a verified decision,
the executing agent MUST append a `review_overdue` record for that obligation. The
record states the immutable fact that the obligation is overdue; it does not wait for,
or depend on, the escalation.

**Escalation.** For each overdue obligation the agent MUST send the overdue notice to
its escalation destination. The delivery is complete when the destination accepts the
message (HTTP 2xx, or the transport's acceptance under ARSIA-Core.md §8).
ARSIA-Core.md §11.3 applies to this delivery as it applies to a request:
`internal_error`, `service_unavailable`, a timeout or a transport failure are retried
with the backoff of "Server Errors"; `rate_limited` is retried under "Rate-Limited
Errors" — no retry before the `Retry-After` interval (or `retry_after_seconds`, or 60
seconds when neither is given) has elapsed, even when that is later than the next
backoff interval. At most 3 retries are made (4 attempts in all), whichever rule
applies to each retry. Attempts end on acceptance, on a non-retryable error, or when
the retries are exhausted. The agent then appends a `review_escalation` record,
correlated with the `review_overdue` record, stating the result (`"delivered"` or
`"failed"`) and the number of attempts; a `"failed"` result also produces a
`compliance_warning` record. No record is ever modified to reflect a later result
(ARSIA-State.md §7.2). Escalation — attempted, delivered or failed — never completes a
review.

**Decision outcome.** A verified decision received while no obligation deadline has
been reached completes the review as `completed`; received later, it completes it as
`completed_late`, and every `review_overdue` and `review_escalation` record is kept. On
`"objected"`, the executing agent MUST start the operator's remediation procedure for
the action; when the action is reversible, remediation MAY use rollback (§4.2) under
that section's own authorization. An objection never changes the execution's terminal
state or its records. Operational policy MAY impose further measures; the protocol
defines none.

#### 3.9.5 Audit Records

A review adds to the executing agent's audit trail: one `review_pending` record; per
overdue obligation, one `review_overdue` and one `review_escalation` record; one
`review_decision` record for the verified decision; and a `compliance_warning` per
failed escalation. Each carries the base fields of ARSIA-State.md §7.1 and the fields
below.

**`review_pending`:**

| Field                  | Value                                   |
|------------------------|-----------------------------------------|
| `message_id`           | The review notice's `id`                |
| `correlation_id`       | The `execution_message_id`              |
| `root_request_id`      | The original request's `id`             |
| `execution_message_id` | As in the notice                        |
| `result_hash`          | As in the notice                        |
| `review_deadline`      | As in the notice                        |

**`review_overdue`:**

| Field                  | Value                                   |
|------------------------|-----------------------------------------|
| `message_id`           | The overdue notice's `id`               |
| `correlation_id`       | The review notice's `id`                |
| `root_request_id`      | The original request's `id`             |
| `review_mode`          | The overdue obligation's mode           |
| `review_deadline`      | Its deadline                            |

**`review_escalation`:**

| Field                  | Value                                   |
|------------------------|-----------------------------------------|
| `message_id`           | The overdue notice's `id`               |
| `correlation_id`       | The review notice's `id`                |
| `root_request_id`      | The original request's `id`             |
| `review_mode`          | The overdue obligation's mode           |
| `escalation_result`    | `"delivered"` or `"failed"`             |
| `escalation_attempts`  | Integer ≥ 1                             |

**`review_decision`:**

| Field                  | Value                                   |
|------------------------|-----------------------------------------|
| `message_id`           | The decision's `id`                     |
| `correlation_id`       | The review notice's `id`                |
| `root_request_id`      | The original request's `id`             |
| `review_outcome`       | `"confirmed"` or `"objected"`           |
| `reviewer_id`          | As in the decision                      |
| `late`                 | `true` exactly when the decision completed the review as `completed_late` |
| `reason`               | As in the decision, or null             |

---

## 4. Action Execution Semantics

This section defines the lifecycle, rollback, timeout, and sandboxing semantics for
action execution within the ARSIA Protocol.

### 4.1 Execution Lifecycle States

Every action execution passes through a defined sequence of states. The lifecycle is
the same whether the action requires human oversight or not — the oversight flow
(§3) inserts additional states into the sequence but does not alter the terminal
states.

The following states are defined:

#### REQUESTED

**Entry condition:** The executing agent receives a `request` message
(ARSIA-Core.md §4.1.6) with a `payload.type` matching a registered ActionDescriptor.

**Processing:** The executing agent validates the message envelope, verifies
authorization (ARSIA-Core.md §6.4) and resolves the effective obligations
(ARSIA-Core.md §4.3.10), including the `executor-policy` sources.

**Transitions:**
- If validation, authorization or resolution fails → **FAILED**
- If validation, authorization and resolution succeed and the effective oversight set
  includes `"required_before_execution"` → **PENDING_APPROVAL**
- If validation, authorization and resolution succeed and the effective oversight set
  does not include `"required_before_execution"` → **EXECUTING**

#### PENDING_APPROVAL

**Entry condition:** The executing agent has determined that the action requires human
oversight and has sent a `pending_approval` message (§3.2).

**Processing:** The executing agent waits for an `approval_decision` message (§3.3).
No action side effects occur in this state.

**Transitions:**
- If `approval_decision` with `decision: "approved"` admitted (§3.4) and the required
  approvals reached → **EXECUTING**
- If `approval_decision` with `decision: "denied"` admitted (§3.4) → **FAILED**
- If the conditions of §3.4, Path 3 hold — `approval_deadline` reached, every decision
  received before it verified, the flow still pending without the required admitted
  approvals → **FAILED**
- A rejected decision (§3.4) leaves the state unchanged.

**Timeout:** The `approval_deadline` from the `pending_approval` message.

#### EXECUTING

**Entry condition:** The action has been authorized for execution, either directly
(no oversight required) or after receiving approval.

**Processing:** The executing agent performs the action's logic, which may include
external calls, database operations, computations, or any other side effects.

**Transitions:**
- If execution completes successfully → **COMPLETED**
- If execution fails (exception, external error, constraint violation) → **FAILED**
- If execution exceeds `max_execution_ms` → **FAILED** (timeout)

**Timeout:** `max_execution_ms` from the ActionDescriptor (default: 30000ms).

#### COMPLETED

**Entry condition:** The action has executed successfully and produced a result.

**Processing:** The executing agent sends a `response` message (ARSIA-Core.md §4.1.6)
to the original requester with the action result in `payload.result`. If the action's
ActionDescriptor has `audit_required: true`, an audit record MUST be generated. If
`explainability_required: true`, the response MUST include a `payload.explanation`
object (§5).

**Transitions:** Terminal state. No further transitions. The action execution is
complete.

#### FAILED

**Entry condition:** The action has failed due to one of: validation error,
authorization failure, oversight denial, oversight expiry, execution error, or
execution timeout.

**Processing:** The executing agent sends an `error` message (ARSIA-Core.md §4.1.6) to
the original requester. If the action's ActionDescriptor has `audit_required: true`, an
audit record MUST be generated recording the failure. The error message MUST include an
appropriate error code (ARSIA-Core.md §11.2) and a description of the failure.

**Transitions:** Terminal state. No further transitions.

#### ROLLED_BACK

**Entry condition:** A previously COMPLETED action has been successfully reversed via
the rollback mechanism defined in §4.2.

**Processing:** The executing agent has undone the action's side effects. A rollback
audit record MUST be generated.

**Transitions:** Terminal state. No further transitions.

#### State Diagram

```
               +-----------+
               | REQUESTED |
               +-----+-----+
                     |
         +-----------+-----------+
         |           |           |
         v           |           v
+------------------+ |     +-----------+
| PENDING_APPROVAL | |     | EXECUTING |
+--------+---------+ |     +-----+-----+
         |           |           |
    +----+----+      |       +---+---+
    |    |    |      |       |       |
    v    |    v      |       v       v
 EXEC.   |  FAILED   |    COMPLETED FAILED
    |    |           |       |
    |    |           |       v
    |    +-----------+   ROLLED_BACK
    |                         (via §4.2)
    +--> COMPLETED / FAILED
```

The PENDING_APPROVAL state is entered only when the effective oversight set includes
`"required_before_execution"`. A post-execution review has its own states (§3.9.4)
and never changes the states of this lifecycle.

### 4.2 Rollback (Reversible Actions)

When an ActionDescriptor declares `reversible: true`, the executing agent SHOULD support
undoing the action's effects via a rollback request. Rollback is a best-effort mechanism
— agents MUST document which actions support rollback and under what conditions rollback
is possible.

An action is considered reversible if the agent implements a rollback mechanism, even if
rollback success is conditional or partial. Declaring `reversible: true` when no rollback
mechanism exists at all constitutes a conformance violation (§2.1).

#### Rollback Request

To request rollback of a previously completed action, the requesting agent sends a new
ARSIA request message with the following characteristics:

| Field              | Value                                                       |
|--------------------|-------------------------------------------------------------|
| `intent`           | `"request"`                                                 |
| `payload.type`     | `"{original_action_id}/rollback"`                           |
| `payload.args`     | `{ "original_message_id": "{id of the message to roll back}" }` |
| `capabilities`     | The original action's `required_capabilities`               |

The `payload.type` is constructed by appending `/rollback` to the original action's
`action_id`. For example, if the original action is `"com.example.notes/create"`, the
rollback type is `"com.example.notes/create/rollback"`.

The `payload.args` MUST include `original_message_id` — the `id` field of the original
response message that confirmed successful execution. This identifies exactly which
execution to roll back.

#### Rollback Semantics

The following rules govern rollback behavior:

1. **Rollback of a non-reversible action.** If the ActionDescriptor has
   `reversible: false` and a rollback request is received, the executing agent MUST
   respond with error code `not_implemented` (ARSIA-Core.md §11.2) and description
   `"Rollback not supported for this action"`.

2. **Rollback window.** Implementations MAY define a rollback window — a maximum time
   after execution during which rollback is possible. If a rollback request arrives
   after the window has elapsed, the executing agent MUST respond with error code
   `conflict` (ARSIA-Core.md §11.2) and `details: { "rollback_window_exceeded": true }`.

3. **Partial rollback.** If the action's effects can only be partially reversed (e.g.,
   some data was propagated to external systems), the executing agent MAY perform a
   partial rollback. In this case, the response MUST include
   `details: { "partial_rollback": true, "rolled_back": [...], "not_rolled_back": [...] }`
   describing which effects were reversed and which were not.

4. **Rollback of a rolled-back action.** Attempting to roll back an action that is
   already in the ROLLED_BACK state MUST produce error code `conflict` with
   `details: { "already_rolled_back": true }`.

5. **Rollback and oversight.** If the original action required human oversight
   (`human_oversight_required: true`), the rollback request SHOULD also require human
   oversight, unless the agent operator has explicitly configured rollback to bypass
   oversight. The rationale is that undoing a high-risk action is itself a high-risk
   operation.

#### Rollback Audit

When rollback succeeds, the executing agent MUST generate an audit record with
`event_type: "rollback"` that includes:

- The original action's `message_id` and `action_id`, as the extension fields
  `original_message_id` (the value of the rollback request's
  `payload.args.original_message_id`) and `action_id`.
- The rollback request's `message_id`, as the record's `message_id` base field.
- The timestamp of the rollback, as the record's `processed_at` base field.
- Whether the rollback was full or partial, as the boolean extension field
  `partial_rollback` (`true` for a partial rollback per rule 3 above).

These extension fields are REQUIRED on every `rollback` record (ARSIA-State.md §7.1,
per-event-type extension fields).

### 4.3 Execution Timeouts

**Default timeout.** The default execution timeout for all actions is 30000 milliseconds
(30 seconds). This default applies when the ActionDescriptor does not specify a
`max_execution_ms` value.

**ActionDescriptor override.** When the ActionDescriptor specifies `max_execution_ms`,
that value overrides the default timeout for the specific action.

**Timeout behavior.** When execution exceeds the timeout:

1. The executing agent MUST cease execution and release any resources held by the
   action.
2. The executing agent MUST respond with error code `service_unavailable`
   (ARSIA-Core.md §11.2) and description `"Action execution timeout"`.
3. The error response SHOULD include `details: { "timeout_ms": <the timeout value>,
   "elapsed_ms": <approximate elapsed time> }`.
4. If the action has partial side effects that occurred before the timeout, the agent
   SHOULD attempt to roll back those effects if the action is reversible. If rollback
   is not possible, the agent MUST document the partial execution in the audit record.

**Long-running actions.** Actions that are expected to exceed the standard timeout
(or even the maximum configurable timeout) SHOULD use the asynchronous execution
pattern:

1. **Immediate acknowledgment.** The executing agent responds immediately with a
   `response` message containing a status URL. This is the envelope surface of the
   protocol's single asynchronous pattern (ARSIA-Core.md §8.1): over HTTP the
   acknowledgment MUST use 202 + `Location`, and when the envelope-level
   `status_url` is also present the two URLs MUST be identical; over transports
   without HTTP status semantics the envelope surface is the only one.

   <!-- example: arsia-message.schema.json; template=/correlation_id,/payload/type; partial=/v,/id,/ts,/from,/to,/root_request_id,/security -->
   ```json
   {
     "intent": "response",
     "correlation_id": "<original request id>",
     "payload": {
       "type": "<action_id>",
       "result": {
         "status": "accepted",
         "status_url": "https://agent.example.com/status/{execution-id}",
         "estimated_completion_ms": 120000
       }
     }
   }
   ```

2. **Status polling.** The requesting agent polls the `status_url` via HTTP GET. The
   response is a JSON object:

   <!-- example: arsia-message.schema.json#/$defs/long-running-status -->
   ```json
   {
     "status": "running",
     "progress_pct": 45,
     "started_at": "2026-03-24T14:30:00.000Z",
     "estimated_completion_at": "2026-03-24T14:32:00.000Z"
   }
   ```

   The `status` field MUST be one of: `"running"`, `"completed"`, `"failed"`.

3. **Result retrieval.** When `status` is `"completed"`, the response includes a
   `result_url`:

   <!-- example: arsia-message.schema.json#/$defs/long-running-status -->
   ```json
   {
     "status": "completed",
     "progress_pct": 100,
     "completed_at": "2026-03-24T14:31:45.000Z",
     "result_url": "https://agent.example.com/results/{execution-id}"
   }
   ```

   The `result_url` returns a standard ARSIA response envelope containing the action
   result. That envelope is the terminal result (§3.9.2): the executing agent
   materializes and signs it when the action reaches COMPLETED, with `ts` equal to
   `completed_at`, and returns it unchanged on every retrieval. It carries
   `payload.obligation_resolution` (ARSIA-Core.md §4.4.8) and no `expires_at`.

   A retrieved terminal result is a persisted, authenticated result, not a newly
   emitted message. The retriever MUST verify its signature (ARSIA-Core.md §5.2) and
   its binding to the execution — `correlation_id` and `root_request_id` equal to the
   original request's `id` — and the retrieval remains subject to the current
   authorization of the retriever. The retriever MUST NOT reject the result only
   because its `ts` lies outside the clock-skew tolerance of ARSIA-Core.md §8.3. The
   `ts` keeps recording the execution instant and is never renewed.

4. **Failure.** When `status` is `"failed"`, the response includes error details:

   <!-- example: arsia-message.schema.json#/$defs/long-running-status -->
   ```json
   {
     "status": "failed",
     "failed_at": "2026-03-24T14:31:10.000Z",
     "error": {
       "code": "internal_error",
       "description": "Risk model computation failed"
     },
     "result_url": "https://agent.example.com/results/{execution-id}"
   }
   ```

   When `status` is `"failed"` for an action that entered EXECUTING, the status object
   also includes `result_url`, which returns the terminal result: a signed `error`
   envelope that the executing agent materializes when the action reaches FAILED,
   with `ts` equal to `failed_at`, carrying the same `error`,
   `payload.obligation_resolution` and no `expires_at`. It is returned unchanged on
   every retrieval and is processed as a retrieved terminal result (item 3).

### 4.4 Sandboxing Requirements

Actions MUST be executed with isolation guarantees that are commensurate with their
risk level. This section defines the minimum sandboxing requirements for each risk
tier.

#### Risk 0–4 — Standard Isolation

Actions at risk levels 0 through 4 SHOULD use an isolated execution context.

**RECOMMENDED but not REQUIRED:**
- Execution in a separate process or container.
- Process-level resource limits (CPU time, memory).

**Network access:** Unrestricted. The action may make outbound network calls to any
endpoint.

**Filesystem access:** The action SHOULD have access only to its designated working
directory and configuration files. Access to the host filesystem outside the agent's
data directory is NOT RECOMMENDED.

#### Risk 5–7 — Enhanced Isolation

Actions at risk levels 5 through 7 MUST use an isolated execution context.

**REQUIRED:**
- Execution in a separate process or container. In-process execution is not permitted.
- Process or container MUST have a unique identity (e.g., a distinct PID or container
  ID) for audit trail purposes.

**Network egress:** SHOULD be restricted to endpoints declared in the action's
configuration. The set of permitted egress endpoints SHOULD be documented in the
ActionDescriptor's `description` field or in supplementary documentation.

**Memory limit:** SHOULD be set. The specific limit is implementation-defined but MUST
be sufficient for the action's normal operation and MUST prevent unbounded memory
consumption.

**Filesystem access:** Read-only access to configuration and input data. Write access
limited to designated output directories and temporary storage.

#### Risk 8–10 — Maximum Isolation

Actions at risk levels 8 through 10 MUST use an isolated execution context with
explicit, documented resource limits.

**REQUIRED:**
- Execution in a separate container. Process-level isolation alone is not sufficient
  at this risk tier — container-level isolation (e.g., Docker, OCI-compliant runtime)
  is REQUIRED.
- The container MUST have a unique identity for audit trail purposes.

**CPU limit:** MUST be set and SHOULD be documented in supplementary documentation
alongside the ActionDescriptor. The limit MUST prevent the action from monopolizing
host CPU resources.

**Memory limit:** MUST be set and SHOULD be documented. The limit MUST prevent the
action from exhausting host memory. Out-of-memory conditions MUST be caught and
reported as execution failures, not as host-level crashes.

**Network egress:** MUST be restricted to declared endpoints only. The action MUST NOT
be able to make outbound network calls to endpoints that are not explicitly listed in
the action's configuration. Implementations SHOULD use network policy enforcement
(e.g., Kubernetes NetworkPolicy, Docker network isolation) to enforce this restriction.

**Filesystem access:** Read-only, except for designated output directories. The action
MUST NOT have write access to the host filesystem, the agent's configuration files, or
other actions' data directories. Temporary storage MUST be bounded and cleaned up after
execution.

**Execution duration:** MUST be bounded by `max_execution_ms` from the ActionDescriptor.
The container runtime MUST enforce this limit — if the action exceeds the timeout, the
container MUST be terminated.

---

## 5. Explainability (EU AI Act Art. 13)

The EU AI Act Article 13(1) requires that high-risk AI systems be designed and
developed in such a way that their operation is sufficiently transparent to enable
deployers to interpret the system's output and use it appropriately. This section
defines the protocol-level mechanism through which ARSIA agents provide explanations
of their reasoning and decision-making.

### 5.1 When Required

An explanation MUST be provided in the following situations:

1. **Action-level requirement.** When the ActionDescriptor has
   `explainability_required: true`, every `response` message for that action MUST
   include a `payload.explanation` object conforming to §5.2.

2. **Compliance profile requirement.** When the message's compliance object has
   `explainability_required: true` (ARSIA-Core.md §4.3.6), the response MUST include
   a `payload.explanation` object regardless of the ActionDescriptor's setting. The
   compliance profile requirement overrides the action-level setting.

3. **Oversight context.** When an action goes through the human oversight flow (§3),
   the `pending_approval` message SHOULD include a preliminary explanation in the
   `payload.explanation` field. This preliminary explanation helps the approver
   make an informed decision and is distinct from the final explanation in the
   response.

An explanation MAY be provided voluntarily in any response, even when not required.
Agents are encouraged to provide explanations for actions at risk level 5 and above.

### 5.2 Explanation Object Format

The explanation object provides a structured account of the agent's reasoning. It is
included in the `payload` object of response messages as `payload.explanation`.

#### `reasoning` — Human-Readable Reasoning

- **Type:** string
- **REQUIRED.**
- **Maximum length:** 4096 characters.
- **Constraints:** A human-readable explanation of why this action was taken or why
  this result was produced. The reasoning MUST be written in plain language that a
  non-technical person can understand. It SHOULD describe: the inputs that were
  considered, the logic that was applied, and the conclusion that was reached. The
  reasoning MUST NOT contain raw model outputs, token probabilities, or other
  machine-readable representations that are not meaningful to a human reader.

#### `confidence` — Decision Confidence

- **Type:** number
- **REQUIRED.**
- **Minimum:** 0.0
- **Maximum:** 1.0
- **Constraints:** The agent's confidence in the decision or recommendation, expressed
  as a decimal value between 0.0 (no confidence) and 1.0 (absolute confidence). The
  confidence value MUST reflect the agent's actual assessment — it MUST NOT be hardcoded
  to a fixed value. When the agent's internal model does not produce a confidence score,
  the agent SHOULD use a calibrated estimate based on the quality and completeness of
  the available inputs.

#### `inputs_used` — Input Identifiers

- **Type:** array of strings
- **REQUIRED.**
- **Constraints:** A list of identifiers for the inputs that influenced the decision.
  Each string SHOULD be traceable to a specific data source, state entry, or external
  input. Examples: `"state:client-profile/risk-tolerance"`,
  `"message:a1b2c3d4-e5f6-..."`, `"external:bloomberg/AAPL/price"`. The format of
  input identifiers is not prescribed by this specification, but implementations SHOULD
  use a consistent naming convention that enables auditors to locate the referenced
  inputs.

#### `alternatives_considered` — Alternative Options

- **Type:** array of objects
- **OPTIONAL but RECOMMENDED for risk_level ≥ 7.**
- **Constraints:** Each element describes an alternative option that the agent evaluated
  and chose not to pursue. Each element MUST contain:

  - **`option`** (string, REQUIRED): A description of the alternative.
  - **`reason_rejected`** (string, REQUIRED): Why this alternative was not chosen.
  - **`confidence`** (number, REQUIRED): The agent's confidence in this alternative
    (0.0 to 1.0), enabling comparison with the chosen option.

  This field supports EU AI Act Article 14(4)(c) — the ability to correctly interpret
  the AI system's output — by showing not just what the agent decided, but what it
  considered and rejected.

#### `model_version` — Model Version Identifier

- **Type:** string
- **OPTIONAL.**
- **Constraints:** The version identifier of the machine learning model used to make
  this decision, if any. This aids reproducibility and audit: given the same inputs and
  the same model version, the same explanation should be producible. The format is
  implementation-defined but SHOULD include a model name and a version or commit hash.
  Examples: `"gpt-4o-2025-08-06"`, `"risk-model-v2.3.1-abc123"`.

#### `decision_timestamp` — Decision Time

- **Type:** string
- **OPTIONAL.**
- **Format:** RFC 3339 with millisecond precision and UTC timezone designator.
- **Constraints:** The timestamp at which the agent made the decision. This may differ
  from the message's `ts` field if there was a delay between the decision and the
  response construction. When present, this value MUST be earlier than or equal to the
  message's `ts` value.

#### Complete Explanation Example

<!-- example: arsia-explanation.schema.json -->
```json
{
  "reasoning": "The client's risk profile (conservative, score 3/10) is incompatible with the proposed instrument (high-yield emerging market bond, risk score 8/10). MiFID II suitability rules require that the instrument's risk level does not exceed the client's declared risk tolerance by more than 2 points. The gap of 5 points exceeds this threshold. Recommendation: unsuitable.",
  "confidence": 0.94,
  "inputs_used": [
    "state:client/CL-4821/risk-profile",
    "state:instrument/ISIN-XS1234567890/risk-classification",
    "external:ecb/interest-rates/2026-03-24"
  ],
  "alternatives_considered": [
    {
      "option": "Approve with reduced allocation (max 5% of portfolio)",
      "reason_rejected": "Client's risk tolerance does not permit any allocation to instruments rated above 5/10, regardless of position size",
      "confidence": 0.12
    },
    {
      "option": "Request updated risk profile from client",
      "reason_rejected": "Risk profile was updated less than 30 days ago; MiFID II guidelines recommend a minimum 90-day interval between profile updates",
      "confidence": 0.31
    }
  ],
  "model_version": "mifid-suitability-v3.1.0-e8a2f1c",
  "decision_timestamp": "2026-03-24T14:29:58.412Z"
}
```

### 5.3 Explainability and Audit

When `explainability_required` is `true` for an action:

1. **Audit inclusion.** The explanation object MUST be included in the audit record as
   part of the payload. Specifically, the `payload_hash` in the audit record (§3.5) is
   computed over the canonicalized payload that includes the explanation object. This
   ensures that the explanation is tamper-evident — any modification to the explanation
   after the fact will invalidate the payload hash.

2. **Audit retrieval.** Auditors with the `arsiaprotocol.audit.read` capability can retrieve
   the explanation via the audit trail query endpoint (ARSIA-State.md §7). The
   explanation is stored as part of the full message payload, not as a
   separate record.

3. **Regulatory support.** The combination of the explanation object and the audit
   trail provides technical records that support compliance with EU AI Act
   Article 13(1) (statement subject to legal review — Art. 13(1) is a design
   obligation on the provider of the high-risk system, which no protocol layer can
   discharge by itself): the explanation object records the basis of the system's
   operation, and the audit trail preserves the explanation with cryptographic
   integrity, within the tamper-evidence scope of ARSIA-State.md §7.2.

4. **Preliminary vs. final explanation.** When an action goes through human oversight,
   two explanations may exist: the preliminary explanation in the `pending_approval`
   message and the final explanation in the `response` message. Both MUST be preserved
   in the audit trail. They may differ — the agent may refine its reasoning after
   receiving approval conditions (§3.3) or additional context.

---

## 6. Actions Conformance Tests

The following test cases define conformance requirements for the Actions primitive. Each
test is identified by a unique `test_id` and specifies preconditions, actions, and
expected results. These tests are normative — a conformant implementation MUST pass all
tests at the applicable conformance level.

### ACTIONS-01: Action discovery endpoint returns valid descriptors

| Field             | Value                                                     |
|-------------------|-----------------------------------------------------------|
| **test_id**       | `ACTIONS-01`                                              |
| **description**   | Verify that the action discovery endpoint returns a valid response containing ActionDescriptor objects |
| **preconditions** | Agent has 5 registered actions with varying categories and risk levels. |
| **action**        | Send `GET /.well-known/arsia/actions` to the agent.       |
| **expected**      | HTTP 200 OK. Response body is valid JSON with the structure `{ actions: [...], total: 5, limit: integer, offset: 0 }`. Each element of the `actions` array is a valid ActionDescriptor conforming to §2.1 — all REQUIRED fields (`action_id`, `category`, `description`, `risk_level`, `reversible`, `idempotent`, `required_capabilities`, `human_oversight_required`, `audit_required`, `explainability_required`) are present and conform to their type and constraint definitions. |

### ACTIONS-02: Capability enforcement rejects missing required capability

| Field             | Value                                                     |
|-------------------|-----------------------------------------------------------|
| **test_id**       | `ACTIONS-02`                                              |
| **description**   | Verify that a request missing a required capability is rejected |
| **preconditions** | Agent B has action `com.example.notes/create` registered with `required_capabilities: ["notes.write"]`. Agent A has an access token with scope `"notes.read"` (missing `"notes.write"`). |
| **action**        | Agent A sends a `request` message to Agent B with `payload.type: "com.example.notes/create"` and `capabilities: ["notes.read"]`. |
| **expected**      | Agent B responds with `intent: "error"`, `payload.error.code: "forbidden"`. The `payload.error.details` object MUST contain `required_capabilities: ["notes.write"]` and `provided_capabilities: ["notes.read"]`. |

### ACTIONS-03: Wildcard capability satisfies specific capability request

| Field             | Value                                                     |
|-------------------|-----------------------------------------------------------|
| **test_id**       | `ACTIONS-03`                                              |
| **description**   | Verify that a wildcard scope entry satisfies a specific capability request |
| **preconditions** | Agent A has an access token with scope `"notes.*"`. Agent B has action `com.example.notes/get` registered with `required_capabilities: ["notes.read"]`. |
| **action**        | Agent A sends a `request` message to Agent B with `payload.type: "com.example.notes/get"` and `capabilities: ["notes.read"]`. |
| **expected**      | Agent B accepts the request. The wildcard scope `"notes.*"` satisfies the specific capability `"notes.read"`. The action proceeds to execution (or to PENDING_APPROVAL if human_oversight_required). No authorization error is returned. |

### ACTIONS-04: Human oversight triggered for high-risk action

| Field             | Value                                                     |
|-------------------|-----------------------------------------------------------|
| **test_id**       | `ACTIONS-04`                                              |
| **description**   | Verify that an action with `human_oversight_required: true` triggers the pending_approval flow instead of immediate execution |
| **preconditions** | Agent B has action `eu.mifid.risk/assess` registered with `risk_level: 9` and `human_oversight_required: true`. Agent A has a valid access token with the required capabilities. |
| **action**        | Agent A sends a `request` message to Agent B for this action. |
| **expected**      | Agent B responds with `intent: "pending_approval"`. The response MUST NOT contain the action result. The `payload.type` MUST be `"arsiaprotocol.oversight/pending"`. The `payload.args` MUST contain: `action_id` matching the action, `original_request_id` matching the request's `id`, `approval_deadline` in the future, `approver_capability: "arsiaprotocol.oversight.approve"`, `context` (non-empty string), `risk_level: 9`, and `request_payload_hash` equal to the SHA-256 of the request's payload. The `payload.obligation_resolution` MUST record, on the oversight axis, the `executor-policy` source `action-descriptor:eu.mifid.risk/assess`. The `correlation_id` MUST equal the original request's `id`. The `expires_at` envelope field MUST equal the `approval_deadline`. |

### ACTIONS-05: Approval granted leads to action execution

| Field             | Value                                                     |
|-------------------|-----------------------------------------------------------|
| **test_id**       | `ACTIONS-05`                                              |
| **description**   | Verify that an approved action executes and produces a response to the original requester |
| **preconditions** | Agent B has sent a `pending_approval` message (id: P) for a request from Agent A (id: R). Agent C has the `arsiaprotocol.oversight.approve` capability. The `approval_deadline` has not passed. |
| **action**        | Agent C sends an `approval_decision` message to Agent B with `correlation_id: P`, `decision: "approved"`, `request_payload_hash` equal to that of P, and `capabilities: ["arsiaprotocol.oversight.approve"]`. |
| **expected**      | Agent B executes the action. Agent A (the original requester, NOT Agent C) receives a `response` message with `correlation_id: R` containing the action result. Agent B's audit trail contains 4 records: request, pending_approval, approval_decision, and response. |

### ACTIONS-06: Approval denied blocks action execution

| Field             | Value                                                     |
|-------------------|-----------------------------------------------------------|
| **test_id**       | `ACTIONS-06`                                              |
| **description**   | Verify that a denied action produces an error to the original requester |
| **preconditions** | Agent B has sent a `pending_approval` message (id: P) for a request from Agent A (id: R). Agent C has the `arsiaprotocol.oversight.approve` capability. |
| **action**        | Agent C sends an `approval_decision` message to Agent B with `correlation_id: P`, `decision: "denied"`, and `reason: "Risk assessment parameters incomplete"`. |
| **expected**      | Agent B does NOT execute the action. Agent A receives an `error` message with `correlation_id: R`, `payload.error.code: "forbidden"`, `payload.error.description: "Action denied by human oversight"`. The `payload.error.details` MUST contain `oversight_decision: "denied"`, `approver_id` matching Agent C's agent-id, and `reason: "Risk assessment parameters incomplete"`. |

### ACTIONS-07: Approval deadline expiry blocks action execution

| Field             | Value                                                     |
|-------------------|-----------------------------------------------------------|
| **test_id**       | `ACTIONS-07`                                              |
| **description**   | Verify that an action is denied when the approval deadline expires without a decision |
| **preconditions** | Agent B has sent a `pending_approval` message for a request from Agent A, with `approval_deadline` set to 5 seconds in the future. No `approval_decision` is sent. |
| **action**        | Wait for the `approval_deadline` to elapse (5+ seconds).  |
| **expected**      | Agent A receives an `error` message with `payload.error.code: "forbidden"`, `payload.error.description: "Action approval deadline exceeded"`. The `payload.error.details` MUST contain `oversight_decision: "expired"` and `deadline` matching the original `approval_deadline` timestamp. Agent B's audit trail records the expiry. |

### ACTIONS-08: Explainability field present when required

| Field             | Value                                                     |
|-------------------|-----------------------------------------------------------|
| **test_id**       | `ACTIONS-08`                                              |
| **description**   | Verify that responses to actions with `explainability_required: true` include the explanation object |
| **preconditions** | Agent B has action `eu.mifid.risk/assess` registered with `explainability_required: true`. Action does not require human oversight for this test (or oversight has already been approved). |
| **action**        | Agent A sends a valid `request` message for this action. Agent B executes the action. |
| **expected**      | Agent B's response includes `payload.explanation` with all REQUIRED fields: `reasoning` (non-empty string, max 4096 chars), `confidence` (number between 0.0 and 1.0), and `inputs_used` (non-empty array of strings). |

### ACTIONS-09: Rollback of reversible action

| Field             | Value                                                     |
|-------------------|-----------------------------------------------------------|
| **test_id**       | `ACTIONS-09`                                              |
| **description**   | Verify that a reversible action can be rolled back after execution |
| **preconditions** | Agent B has action `com.example.notes/create` registered with `reversible: true`. The action was previously executed successfully, producing a response message with `id: X`. |
| **action**        | Agent A sends a `request` message with `payload.type: "com.example.notes/create/rollback"` and `payload.args: { "original_message_id": "X" }`. |
| **expected**      | Agent B responds with `intent: "response"` confirming rollback success. The action's state transitions to ROLLED_BACK. Agent B's audit trail contains a record with `event_type: "rollback"` referencing the original action's `message_id`. |

### ACTIONS-10: Complete audit trail for oversight cycle

| Field             | Value                                                     |
|-------------------|-----------------------------------------------------------|
| **test_id**       | `ACTIONS-10`                                              |
| **description**   | Verify that a complete oversight cycle produces exactly 4 audit records |
| **preconditions** | Full oversight cycle completed: Agent A requests action → Agent B sends pending_approval → Agent C approves → Agent B executes → Agent A receives response. All agents have `audit_required: true`. |
| **action**        | Query Agent B's audit trail for all records in the correlation chain starting from the original request's `id`. |
| **expected**      | Exactly 4 audit records are returned, in chronological order: (1) `event_type: "request"` with the original request's `message_id`; (2) `event_type: "pending_approval"` with `correlation_id` matching the request; (3) `event_type: "approval_decision"` with `decision: "approved"` and `approver_id` matching Agent C; (4) `event_type: "response"` with the final response's `message_id`. Each record includes a `payload_hash` and `timestamp`. |

### ACTIONS-11: Sandboxing enforced for risk level 8 action

| Field             | Value                                                     |
|-------------------|-----------------------------------------------------------|
| **test_id**       | `ACTIONS-11`                                              |
| **description**   | Verify that risk level 8+ actions execute in an isolated container with resource limits |
| **preconditions** | Agent B has action `eu.mifid.risk/assess` registered with `risk_level: 8`. The agent's runtime environment supports container-level isolation. |
| **action**        | Agent A sends a valid request for this action (with oversight approved if required). The action executes. |
| **expected**      | The action executes in a separate container (not in the agent's main process). The container has CPU and memory limits configured. Network egress is restricted to declared endpoints. The audit record for the execution includes the container identifier. Verification: inspect the agent's runtime to confirm container isolation was used (implementation-specific verification method). |

### ACTIONS-12: Capability downgrading in response

| Field             | Value                                                     |
|-------------------|-----------------------------------------------------------|
| **test_id**       | `ACTIONS-12`                                              |
| **description**   | Verify that a receiving agent can downgrade capabilities and communicate the effective set |
| **preconditions** | Agent B accepts action `com.example.notes/manage` with `required_capabilities: ["notes.read"]` and `optional_capabilities: ["notes.write", "notes.delete"]`. Agent A has a token with scope `"notes.read notes.write notes.delete"`. Agent B's policy restricts `notes.delete` for Agent A's trust level. |
| **action**        | Agent A sends a `request` message with `capabilities: ["notes.read", "notes.write", "notes.delete"]`. |
| **expected**      | Agent B accepts the request (all required capabilities are present). Agent B's response includes `payload.result.effective_capabilities: ["notes.read", "notes.write"]`. The `notes.delete` capability has been removed. Agent A observes the downgrade and does not attempt delete operations. |

### ACTIONS-13: Prior approval demanded by a source other than the descriptor

| Field             | Value                                                     |
|-------------------|-----------------------------------------------------------|
| **test_id**       | `ACTIONS-13`                                              |
| **description**   | Verify that a descriptor with `human_oversight_required: false` does not veto prior approval demanded by another source |
| **preconditions** | Agent B has action `test.unit/run` registered with `human_oversight_required: false`. Agent A's access token lists `test.unit` in its `arsia_oversight` claim (ARSIA-Core.md §6.1). |
| **action**        | Agent A sends a `request` with `capabilities: ["test.unit"]`. |
| **expected**      | Agent B responds with `pending_approval` and does not execute. Its `payload.obligation_resolution` records, on the oversight axis, a requirement for `"required_before_execution"` with the `executor-policy` source `capability-policy:<issuer>/<version>` and the claim's `policy.sha256`. Reference logic: harness R15. |

### ACTIONS-14: Within-24h post-execution review opened and completed

| Field             | Value                                                     |
|-------------------|-----------------------------------------------------------|
| **test_id**       | `ACTIONS-14`                                              |
| **description**   | Verify that a `required_within_24h` action executes, opens a review and records the decision |
| **preconditions** | Agent B has a configured review endpoint and escalation destination. Agent A's request has `human_oversight: "required_within_24h"`; no source demands prior approval. Agent C holds `arsiaprotocol.oversight.approve`. |
| **action**        | Agent A sends the request; Agent B executes it; Agent C sends a `review-decision` with `decision: "confirmed"` before the deadline. |
| **expected**      | The response carries `payload.obligation_resolution`. Agent B sends a `review-pending` event to its review endpoint with `review_deadline` equal to the execution instant + 24 hours. The decision is recorded as a `review_decision` record with `late: false`; the review is `completed`. The execution's records are unchanged. Reference logic: harness R15. |

### ACTIONS-15: Overdue review, escalation and late decision

| Field             | Value                                                     |
|-------------------|-----------------------------------------------------------|
| **test_id**       | `ACTIONS-15`                                              |
| **description**   | Verify the overdue consequence and the handling of a late decision |
| **preconditions** | As ACTIONS-14, with no decision before the deadline. In variant (b), the escalation destination answers every attempt with `service_unavailable`. |
| **action**        | The deadline passes; then Agent C sends a confirmed `review-decision`. |
| **expected**      | (a) A `review_overdue` record is appended at the deadline, then a `review_escalation` record with `escalation_result: "delivered"`; the late decision gives `completed_late` (`late: true`) and both records are kept. (b) After 4 attempts, a `review_escalation` record with `escalation_result: "failed"` and a `compliance_warning` record are appended; the review stays `overdue` until a decision arrives. Reference logic: harness R15. |

### ACTIONS-16: Post-execution mode without review configuration

| Field             | Value                                                     |
|-------------------|-----------------------------------------------------------|
| **test_id**       | `ACTIONS-16`                                              |
| **description**   | Verify that a post-execution mode without its review period is rejected before any effect, preserving declared versus filled provenance |
| **preconditions** | Agent B's ActionDescriptor has no `post_execution_review_period`. (a) The request declares `profile: "PAC-AGRICULTURE"` and omits `human_oversight`. (b) The request declares `human_oversight: "required_post_execution"`. |
| **action**        | Agent A sends each request. |
| **expected**      | Both are rejected with `invalid_request` and `details` `obligation_conflict: true`, `axis: "oversight"`, `required: {"mode": "required_post_execution", "missing": "post_execution_review_period"}`; nothing is executed and each rejection is audited. In (a) the conflict has `declared: null`, the axis `declared` is `{"present": false}` and `fill` has source `profile-default`; in (b) `declared` is `"required_post_execution"` and `fill` has source `message`. In both, `sources` is empty. Reference logic: harness R15. |

### ACTIONS-17: Approval bound to the request payload

| Field             | Value                                                     |
|-------------------|-----------------------------------------------------------|
| **test_id**       | `ACTIONS-17`                                              |
| **description**   | Verify that an approval for another payload does not authorize execution |
| **preconditions** | Agent B has sent a `pending_approval` (id: P) with `request_payload_hash` H. |
| **action**        | Agent C sends an `approval_decision` with `correlation_id: P`, `decision: "approved"` and a `request_payload_hash` different from H. |
| **expected**      | Agent B rejects the decision with `invalid_request` and does not execute the action. Reference logic: harness R15. |

### ACTIONS-18: Multi-approval flow ending by expiry

| Field             | Value                                                     |
|-------------------|-----------------------------------------------------------|
| **test_id**       | `ACTIONS-18`                                              |
| **description**   | Verify the record count of a multi-approval flow that ends by deadline expiry |
| **preconditions** | The ActionDescriptor has `required_approvals: 2`. One approval is received; the second is not. |
| **action**        | The `approval_deadline` elapses. |
| **expected**      | The action is not executed and the requester receives the Path 3 error. The audit trail holds 5 records: Record 1, Record 2, one Record 3, one `approval_expired` record and Record 4 (§3.6). Reference logic: harness R15. |

### ACTIONS-19: Asynchronous terminal result

| Field             | Value                                                     |
|-------------------|-----------------------------------------------------------|
| **test_id**       | `ACTIONS-19`                                              |
| **description**   | Verify that a review in the asynchronous pattern is anchored to the terminal result, not to the acknowledgment or to its retrieval |
| **preconditions** | A `required_within_24h` action uses the asynchronous pattern of §4.3. (a) It completes; (b) it fails after entering EXECUTING. |
| **action**        | The requester retrieves `result_url` three days after completion or failure. |
| **expected**      | The acknowledgment opens no review. The review is opened from the terminal result materialized at `completed_at` (a) or `failed_at` (b), whose `ts` is that instant; the retrieval returns the same envelope, the retriever accepts it after verifying signature and binding although its `ts` is outside the clock-skew tolerance, and the `review_deadline` is unchanged. Reference logic: harness R15. |

---

## 7. References

### 7.1 Normative References

- **ARSIA-Core.md** — ARSIA Protocol Core Specification, Draft-02.
  §4.1 (Required Fields — intent enum), §4.1.6 (intent field definition),
  §4.2 (Conditional Required Fields — correlation_id, expires_at, capabilities),
  §4.3.6 (compliance metadata), §4.4 (Payload Structure — type, version, args, result,
  error), §6.1 (Access Token Structure), §6.4 (Capability Enforcement), §7.1 (Discovery
  Endpoint), §8 (Transport Bindings), §8.3 (Request/Response Timing — clock skew
  tolerance), §10 (Idempotency), §11.2 (Standard Error Codes).

- **ARSIA-Identity.md** — ARSIA Identity Primitive Specification, Draft-02.
  §1.2 (Agent Identity Record), §2.4 (Key Rotation), §3.1 (Message-Level Authentication),
  §4 (Identity in the Compliance Context), §4.2 (Classification Consistency Rule).

- **ARSIA-Routing.md** — ARSIA Routing Primitive Specification, Draft-02.
  §7 (Compliance Broker specification).

- **ARSIA-State.md** — ARSIA State Primitive Specification (forward reference).
  §3.1 (State read/write model), §3.2 (GDPR erasure and snapshot mechanisms),
  §6 (Compliance profiles), §7 (Audit trail format and query interface).

- **ARSIA-Assets.md** — ARSIA Assets Primitive Specification (forward reference).
  §3.1 (Asset transfer initiation), §3.3 (Transfer reversal), §5 (Two-party
  authorization).

- **RFC 2119** — Key words for use in RFCs to Indicate Requirement Levels. S. Bradner.
  March 1997.

- **RFC 5234** — Augmented BNF for Syntax Specifications: ABNF. D. Crocker, P. Overell.
  January 2008.

- **RFC 8174** — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words. B. Leiba.
  May 2017.

- **RFC 8785** — JSON Canonicalization Scheme (JCS). A. Rundgren, B. Jordan, S. Erdtman.
  June 2020.

### 7.2 Informative References

- **EU AI Act** — Regulation (EU) 2024/1689 of the European Parliament and of the
  Council of 13 June 2024 laying down harmonised rules on artificial intelligence
  (Artificial Intelligence Act).
  - Art. 13 — Transparency and provision of information to deployers.
  - Art. 14 — Human oversight.
  - Art. 14(1) — Design requirement for effective human oversight.
  - Art. 14(4) — Specific oversight capabilities required.
  - Art. 14(4)(a) — Understanding system capacities and limitations.
  - Art. 14(4)(c) — Interpreting system output.
  - Art. 14(4)(d) — Ability to override or reverse output.
  - Art. 17 — Quality management system.
  - Art. 17(1)(k) — Systems and procedures for record-keeping of all relevant
    documentation and information.
  - Art. 26 — Obligations of deployers of high-risk AI systems.
  - Art. 26(6) — Deployer logging obligations (minimum 6 months).
  - Art. 50 — Transparency obligations for providers and deployers of certain AI
    systems.
  - Annex III — High-risk AI systems list.
  - Art. 113 — Entry into force and application (point (c) as amended by Regulation
    (EU) 2026/1744).

- **Regulation (EU) 2026/1744** of the European Parliament and of the Council of 8 July
  2026 amending Regulations (EU) 2024/1689, (EU) 2018/1139 and (EU) 2023/1230 as regards
  the simplification of the implementation of harmonised rules on artificial
  intelligence (Digital Omnibus on AI).
  - Art. 1(40) — Amendment of Article 113 of Regulation (EU) 2024/1689.

- **GDPR** — Regulation (EU) 2016/679 of the European Parliament and of the Council
  of 27 April 2016 on the protection of natural persons with regard to the processing
  of personal data and on the free movement of such data.
  - Art. 6(1) — Lawfulness of processing (legal basis).
  - Art. 17 — Right to erasure ('right to be forgotten').
  - Art. 30 — Records of processing activities.

- **MiFID II** — Directive 2014/65/EU of the European Parliament and of the Council
  of 15 May 2014 on markets in financial instruments.
  - Art. 16(6)-(7) — record-keeping; five-year periods for the records covered by
    Art. 16(7) and by MiFIR Art. 25(1). The MIFID-II profile floor `P1827D` is
    defined in ARSIA-State.md §6.3.

- **NIST AI Risk Management Framework 1.0** — National Institute of Standards and
  Technology. January 2023.
  - GOVERN 1.3 — Processes, procedures, and practices are in place to determine the
    needed level of risk management activities based on the assessed risk level,
    including human oversight mechanisms for AI systems.

---
ARSIA Protocol ([arsiaprotocol.org](https://arsiaprotocol.org)) | by [Arsia Labs](https://arsialabs.ai)
