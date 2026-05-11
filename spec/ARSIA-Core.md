<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
# ARSIA Protocol — Core Specification

**Protocol:** ARSIA Protocol
**Version:** 1.0
**Status:** Draft
**Authors:**
- Kirk Patrick (Arsia Labs) — kirk@arsialabs.ai
- Greici Savoldi (Arsia Labs) — greici@arsialabs.ai

**Draft-01**
**March 2026**
**Arsia Labs — arsiaprotocol.org**

---

## Abstract

ARSIA (Actions, Routing, State, Identity, Assets) is an open protocol for secure,
compliant communication between autonomous AI agents. The protocol defines a
structured message envelope, cryptographic identity, capability-based authorization,
and extensible compliance semantics. ARSIA operates above transport protocols such as
the Model Context Protocol (MCP), Agent-to-Agent Protocol (A2A), HTTP, and gRPC, and
below the application layer where agent frameworks execute business logic. Its primary
differentiator is native European Union regulatory compliance — including the EU AI Act
(Regulation 2024/1689), the General Data Protection Regulation (GDPR, Regulation
2016/679), and the Markets in Financial Instruments Directive (MiFID II, Directive
2014/65/EU) — encoded as first-class protocol primitives rather than application-level
features.

---

## Status of This Memo

This document specifies Draft-01 of the ARSIA Protocol Core Specification. This
specification is a working draft published by Arsia Labs for review and comment by
the developer and standards community. This draft is not intended for production
deployment. Implementors should expect breaking changes between draft revisions.

The canonical location for this specification is:

    https://arsiaprotocol.org/spec/core/draft-01

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

1. [Introduction](#1-introduction)
   1. [Motivation](#11-motivation)
   2. [Design Goals](#12-design-goals)
   3. [Protocol Stack Position](#13-protocol-stack-position)
2. [Conventions and Terminology](#2-conventions-and-terminology)
   1. [RFC 2119 Keywords](#21-rfc-2119-keywords)
   2. [Definitions](#22-definitions)
3. [Agent Identifier Format](#3-agent-identifier-format)
   1. [ABNF Grammar](#31-abnf-grammar)
   2. [Examples](#32-examples)
   3. [Rules](#33-rules)
4. [Message Envelope](#4-message-envelope)
   1. [Required Fields](#41-required-fields)
   2. [Conditional Required Fields](#42-conditional-required-fields)
   3. [Optional Fields](#43-optional-fields)
      1. [`min_v`](#431-min_v--minimum-protocol-version)
      2. [`idempotency`](#432-idempotency--idempotency-configuration)
      3. [`context`](#433-context--distributed-context)
      4. [`payload`](#434-payload--message-payload)
      5. [`security`](#435-security--security-metadata)
      6. [`compliance`](#436-compliance--compliance-metadata)
         1. [`profile`](#4361-profile)
         2. [`data_residency`](#4362-data_residency)
         3. [`audit_required`](#4363-audit_required)
         4. [`retention_days`](#4364-retention_days)
         5. [`human_oversight`](#4365-human_oversight)
         6. [`explainability_required`](#4366-explainability_required)
         7. [`pii_involved`](#4367-pii_involved)
         8. [`legal_basis`](#4368-legal_basis)
         9. [`ai_system_classification`](#4369-ai_system_classification)
      7. [Field Inheritance and Defaults](#437-field-inheritance-and-defaults)
      8. [Compliance Field Validation Rules](#438-compliance-field-validation-rules)
   4. [Payload Structure](#44-payload-structure)
   5. [Message Size Limits](#45-message-size-limits)
5. [Message Security](#5-message-security)
   1. [Digital Signatures (EdDSA)](#51-digital-signatures-eddsa)
   2. [Signature Verification](#52-signature-verification)
   3. [Payload Encryption (Optional)](#53-payload-encryption-optional)
6. [Authorization](#6-authorization)
   1. [Access Token Structure](#61-access-token-structure)
   2. [Token Request (OAuth 2.0 Client Credentials)](#62-token-request-oauth-20-client-credentials)
   3. [Token Presentation](#63-token-presentation)
   4. [Capability Enforcement](#64-capability-enforcement)
7. [Discovery](#7-discovery)
   1. [Discovery Endpoint](#71-discovery-endpoint)
   2. [Capability Discovery](#72-capability-discovery)
   3. [JWKS Endpoint](#73-jwks-endpoint)
   4. [Version Negotiation](#74-version-negotiation)
8. [Transport Bindings](#8-transport-bindings)
   1. [HTTP/2 (REQUIRED)](#81-http2-required)
   2. [WebSocket (OPTIONAL)](#82-websocket-optional)
   3. [Request/Response Timing](#83-requestresponse-timing)
9. [Routing and Brokers](#9-routing-and-brokers)
   1. [Direct Routing](#91-direct-routing)
   2. [Brokered Routing](#92-brokered-routing)
   3. [Routing Topology](#93-routing-topology)
   4. [Topology Determination Procedure](#94-topology-determination-procedure)
10. [Idempotency](#10-idempotency)
    1. [Idempotency Key Semantics](#101-idempotency-key-semantics)
    2. [Server-Side Storage Requirements](#102-server-side-storage-requirements)
    3. [Duplicate Detection Behaviour](#103-duplicate-detection-behaviour)
    4. [Header vs. Envelope Precedence](#104-header-vs-envelope-precedence)
11. [Error Handling](#11-error-handling)
    1. [Error Response Format](#111-error-response-format)
    2. [Standard Error Codes](#112-standard-error-codes)
    3. [Retry Policy](#113-retry-policy)
12. [Conformance Levels](#12-conformance-levels)
    1. [Core Conformance](#121-core-conformance)
    2. [Compliance Conformance](#122-compliance-conformance)
    3. [Full Conformance](#123-full-conformance)
    4. [Compliance Field Conformance Tests](#124-compliance-field-conformance-tests)
13. [Security Considerations](#13-security-considerations)
    1. [Threat Model](#131-threat-model)
    2. [Mitigations](#132-mitigations)
    3. [Privacy Considerations](#133-privacy-considerations)
14. [IANA Considerations](#14-iana-considerations)
    1. [Media Type Registration](#141-media-type-registration)
    2. [Well-Known URI Registration](#142-well-known-uri-registration)
15. [References](#15-references)
    1. [Normative References](#151-normative-references)
    2. [Informative References](#152-informative-references)
A. [Complete Message Examples](#appendix-a--complete-message-examples)
   1. [Minimal Request](#a1-minimal-request)
   2. [Full Request with Compliance Profile](#a2-full-request-with-eu-ai-act-high-risk-compliance-profile)
   3. [Error Response](#a3-error-response)
B. [ARSIA as a Compliance Layer for MCP and A2A](#appendix-b--arsia-as-a-compliance-layer-for-mcp-and-a2a)
   1. [ARSIA as a Compliance Layer for MCP](#b1-arsia-as-a-compliance-layer-for-mcp)
   2. [ARSIA as a Compliance Layer for A2A](#b2-arsia-as-a-compliance-layer-for-a2a)
   3. [AAIF (Agent Interoperability Forum) Submission Positioning](#b3-aaif-agent-interoperability-forum-submission-positioning)
---

## 1. Introduction

### 1.1 Motivation

The rapid deployment of autonomous AI agents in enterprise environments has exposed a
critical gap in existing agent communication protocols. Protocols such as the Model
Context Protocol (MCP) and the Agent-to-Agent Protocol (A2A) provide robust mechanisms
for agent discovery, capability invocation, and message transport. However, none of
these protocols address the regulatory requirements that govern the deployment of AI
systems within the European Union.

The EU AI Act (Regulation 2024/1689), which entered into force in August 2024 with
phased compliance deadlines extending through 2027, imposes specific obligations on
providers and deployers of AI systems. Article 13 requires transparency obligations,
mandating that high-risk AI systems be designed and developed in such a way that their
operation is sufficiently transparent to enable deployers to interpret the system's
output and use it appropriately. Article 14 requires human oversight measures,
stipulating that high-risk AI systems shall be designed and developed in such a way
that they can be effectively overseen by natural persons during the period in which
they are in use. Article 17 mandates a quality management system that includes
procedures for record-keeping and documentation, including logging of agent decisions
and actions. Article 26 places obligations on deployers of high-risk AI systems,
requiring them to implement appropriate technical and organisational measures to
ensure that high-risk AI systems are used in accordance with their instructions for
use, including monitoring and logging.

Beyond the AI Act, the General Data Protection Regulation (GDPR, Regulation 2016/679)
imposes data residency and processing constraints that directly affect how agent
messages may be routed and stored across jurisdictions. The Markets in Financial
Instruments Directive (MiFID II, Directive 2014/65/EU) requires financial services
firms to retain records of all communications for a minimum of five years, including
algorithmic communications between automated systems.

Today, an AI agent operating under MiFID II obligations has no protocol-level mechanism
to declare its audit retention requirements to a counterparty agent. A high-risk AI
system subject to EU AI Act Article 14 has no standardised way to signal that a
human-in-the-loop approval is required before executing a requested action. An agent
processing personal data subject to GDPR has no transport-level constraint to ensure
that messages remain within a declared data residency zone.

These are not application-level concerns that can be addressed by individual agent
implementations. They are systemic requirements that must be expressed at the protocol
level to ensure consistent, verifiable, and auditable compliance across heterogeneous
agent ecosystems. ARSIA was designed to fill this gap.

Security was once an application-layer concern. Each application implemented its own
encryption, key exchange, and certificate verification. The result was a landscape of
vulnerabilities and incompatibilities that persisted for decades. TLS moved security to
the transport layer, making it universal, verifiable, and interoperable. Applications
that adopt TLS do not need to implement their own cryptographic protocols — they declare
a security level and the transport layer enforces it. ARSIA does the same for regulatory
compliance: it moves compliance from the application layer to the protocol layer, making
it universal, verifiable, and interoperable across agent frameworks. An agent declares a
compliance profile and the protocol layer fills defaults, validates constraints, and
generates audit records. The developer's burden is reduced to a single field declaration;
the regulatory burden is satisfied by the protocol.

The following table compares protocol-level compliance (as defined by this specification)
with application-level compliance (as implemented by existing agent frameworks) across
five dimensions. The comparison is informative and intended to clarify the design
rationale.

**Verifiability.** Protocol-level compliance enables receiving agents to inspect the
`compliance` field and enforce requirements mechanically — the field is present or
absent, the profile name is known or unknown, the retention period meets the minimum or
it does not. Application-level compliance requires receiving agents to trust the sender's
claims with no verification mechanism; a sender may assert "GDPR compliant" without any
inspectable evidence in the message.

**Interoperability.** Protocol-level compliance ensures that all compliant agents use
the same field names, profile names, and validation rules as defined in §4.3.6 of this
specification. Application-level compliance leaves each framework to invent its own
compliance vocabulary — one framework calls it `gdpr_mode`, another calls it
`eu_compliance`, a third has no concept of it at all. Cross-framework interactions
produce compliance gaps.

**Audit consistency.** Protocol-level compliance produces audit records in a single
canonical format — the `ArsiaAuditRecord` defined in ARSIA-State.md §7.1 — across
all agents, frameworks, and deployment models. Application-level compliance produces
heterogeneous log formats that auditors must reconcile manually. Reconciliation across
formats is error-prone and does not scale.

**Developer burden.** Protocol-level compliance reduces the developer's obligation to
declaring a profile name. The protocol fills defaults from the profile definition,
validates constraints (§4.3.8), and generates audit records automatically.
Application-level compliance requires developers to research each regulation
independently, implement requirements from scratch, and maintain that implementation as
regulations evolve.

**Regulatory risk.** Protocol-level compliance provides guarantees by construction: if
an implementation conforms to the profile requirements, it satisfies the corresponding
regulatory obligations at the protocol level. Application-level compliance is only as
good as the weakest agent in a multi-agent interaction — a single non-compliant agent
breaks the audit chain and creates systemic risk for every participant.

The EU AI Act entered into force in August 2024, with high-risk provisions applicable
from August 2025. GDPR has been enforced since May 2018. MiFID II has been enforced
since January 2018. European enterprises cannot deploy autonomous AI agents without
satisfying these regulations. A protocol that ignores them is a protocol that cannot be
adopted in the European Union's €16 trillion economy — the world's second-largest
single market. ARSIA's compliance extension is not a feature that can be deferred to a
later version. It is the minimum viable protocol for European enterprise adoption.

### 1.2 Design Goals

The ARSIA Protocol is designed around five complementary goals that together define its
scope and character.

The first goal is interoperability above existing transports. ARSIA does not define a
new transport protocol. Instead, it defines a structured message envelope and a set of
compliance, identity, and audit semantics that can be carried over any underlying
transport mechanism. An ARSIA message may be transmitted over MCP, A2A, plain HTTP/2,
gRPC, WebSocket, or any future transport that can carry a JSON payload. This design
ensures that ARSIA can be adopted incrementally within existing agent ecosystems without
requiring migration away from established transport protocols.

The second goal is EU regulatory compliance as a first-class protocol primitive. In
ARSIA, compliance is not an afterthought or a plugin. The message envelope includes a
dedicated compliance object that carries regulatory metadata — the applicable compliance
profile, data residency constraints, audit requirements, retention periods, human
oversight requirements, explainability obligations, and legal basis declarations. These
fields are defined in the core envelope schema and are available to every conformant
implementation. This design ensures that compliance metadata travels with the message
itself, is visible to intermediaries such as compliance brokers, and can be verified
independently of the application payload.

The third goal is a minimal core that is extensible via compliance profiles. The ARSIA
core specification defines only the envelope structure, security mechanisms, discovery
protocol, transport bindings, and error handling. Regulatory requirements are encoded in
named compliance profiles — such as EU-AI-ACT-HIGH-RISK, MIFID-II, or PAC-AGRICULTURE —
that specify default values for the compliance object fields. This separation allows the
protocol to accommodate new regulations, new jurisdictions, and new industry verticals
without modifying the core specification.

The fourth goal is auditability by default. Every ARSIA message carries a unique
identifier, a cryptographic signature, and a timestamp with millisecond precision. The
protocol defines correlation identifiers for request-response pairs, trace identifiers
for distributed tracing, and idempotency keys for duplicate detection. These mechanisms
provide the raw material for a complete audit trail without requiring additional
instrumentation at the application layer.

The fifth goal is developer adoption through simplicity. Despite its regulatory
capabilities, the ARSIA core protocol is designed to be straightforward to implement. A
minimal conformant agent requires only the ability to parse and produce JSON messages,
verify Ed25519 signatures, expose a discovery endpoint, and handle the ten standard
error codes. The compliance layer is opt-in: agents that do not operate under regulatory
constraints can use ARSIA as a simple, secure messaging protocol without engaging with
the compliance extensions.

### 1.3 Protocol Stack Position

ARSIA occupies a specific position in the agent communication stack. It sits above
transport protocols and below the application layer:

```
+------------------------------------------------------+
|  Application Layer                                   |
|  (LangChain, CrewAI, AutoGen, OpenClaw, custom)      |
+------------------------------------------------------+
|  ARSIA Protocol -- Compliance Layer    <- this spec  |
|  (envelope, identity, security, compliance, routing) |
+------------------------------------------------------+
|  Transport Layer                                     |
|  (MCP / A2A / HTTP/2 / gRPC / WebSocket)             |
+------------------------------------------------------+
```

ARSIA does not replace transport protocols. It wraps them with compliance, identity,
and audit semantics that are independent of the underlying transport mechanism. An
application framework such as LangChain or CrewAI consumes and produces ARSIA message
envelopes. The ARSIA layer handles envelope validation, signature verification,
capability enforcement, compliance checking, and routing decisions. The validated
message is then delivered to the receiving agent over the transport protocol of the
deployment's choice.

This layered architecture means that two agents can communicate using ARSIA semantics
regardless of whether the underlying transport is MCP, A2A, raw HTTP, or any other
protocol that can carry a JSON payload. The transport layer is responsible for
delivery; ARSIA is responsible for meaning.

ARSIA compliance sits above transport protocols — including Anthropic MCP, Google A2A,
HTTP, and gRPC — and does not replace them. It wraps them. Any agent using MCP or A2A
MAY add ARSIA compliance by including the `compliance` field in its ARSIA message
envelope. The transport protocol continues to handle tool calling, task delegation, or
message delivery as before. The ARSIA envelope adds compliance semantics, identity
verification, and audit trail generation on top of the transport layer.

The wrapping mechanism is intentionally simple. For MCP: the MCP tool call payload
becomes the payload of an ARSIA message with `payload.type = "arsiaprotocol.mcp/tool-call"`.
The ARSIA envelope adds the `compliance` field (profile, audit obligations, human
oversight mode, data residency), the `security` field (EdDSA signature, key identifier),
and identity semantics (agent-id, owner accountability). The MCP server processes the
tool call normally — it does not need to understand ARSIA. For A2A: the A2A task object
becomes the payload of an ARSIA message with `payload.type = "arsiaprotocol.a2a/task"`. The
same approach applies. Neither MCP nor A2A need to be modified. ARSIA is additive.

---

## 2. Conventions and Terminology

### 2.1 RFC 2119 Keywords

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14 [RFC 2119] [RFC 8174] when,
and only when, they appear in all capitals, as shown here.

### 2.2 Definitions

The following terms are used throughout this specification with the precise meanings
defined below.

**Agent.** An agent is an autonomous software entity that sends and receives ARSIA
messages. An agent is identified by a unique agent identifier (§3) and exposes a
discovery endpoint (§7.1) and an inbox endpoint (§8.1) through which it participates
in the ARSIA protocol. An agent may be a fully autonomous AI system, a
semi-autonomous system with human oversight, or a deterministic software service. The
ARSIA protocol does not prescribe the internal architecture of an agent; it defines
only the external communication interface. An agent MUST be capable of producing and
consuming ARSIA message envelopes, verifying digital signatures, and responding to
discovery requests.

**Message.** A message is the atomic unit of communication in the ARSIA protocol. Each
message is a self-contained JSON object that conforms to the ARSIA message envelope
schema defined in §4. A message carries an intent (request, response, event, error,
pending_approval, or approval_decision), a payload containing the application-specific
data, and metadata fields for identity, security, tracing, and compliance. Messages
are immutable once signed: no intermediary, including compliance brokers, is permitted
to modify a signed message envelope.

**Envelope.** The envelope is the outer structure of an ARSIA message. It contains all
metadata fields defined in §4 — including the protocol version, message identifier,
timestamp, sender and recipient identifiers, intent, security information, compliance
metadata, and the payload. The envelope is the unit of validation: a receiving agent
validates the envelope as a whole before processing the enclosed payload. The term
"envelope" and "message" are used interchangeably in this specification when the
context is unambiguous; where a distinction is necessary, "envelope" refers
specifically to the metadata structure exclusive of the payload contents.

**Capability.** A capability is a named permission that authorises an agent to perform
a specific action on a target agent. Capabilities are expressed as dot-separated
strings following the grammar defined in ARSIA-Actions.md §1.1 (e.g.,
`com.example.notes.read`, `arsiaprotocol.echo`). Capabilities are declared in the
message envelope's `capabilities` field and enforced by verifying that the sender's
access token (§6) includes a matching scope. The capability model is additive: an
agent must explicitly request each capability it needs, and the receiving agent must
verify that the presented token authorises all requested capabilities.

**Compliance Profile.** A compliance profile is a named set of regulatory defaults
that pre-populate the compliance object fields in a message envelope. Each profile
corresponds to a specific regulatory framework or industry vertical — for example,
`EU-AI-ACT-HIGH-RISK`, `MIFID-II`, or `PAC-AGRICULTURE`. Profiles are defined in
ARSIA-State.md §6 and specify default values for fields such as `audit_required`,
`retention_days`, `human_oversight`, `explainability_required`, and
`data_residency`. When a compliance profile is referenced in a message, the receiving
agent MUST apply the profile's defaults for any compliance fields not explicitly
overridden in the message.

**Compliance Broker.** A compliance broker is an ARSIA-conformant agent that relays
messages between other agents within the constraints of a declared data residency
zone. A compliance broker operates as a transparent intermediary: it MUST NOT modify
the contents of the message envelope, and it MUST append an audit record for every
message it relays. Compliance brokers are required only when a message's compliance
object specifies a `data_residency` constraint (§9.2). A compliance broker declares
its capability to relay messages via the `arsiaprotocol.broker.relay` capability and
advertises its residency zone through the broker discovery endpoint (§9.2).

**Authorization Server.** An authorization server is an OAuth 2.0 compliant
server that issues access tokens for ARSIA agents. The authorization server
authenticates agents, evaluates capability requests, and issues JWT-formatted access
tokens (§6.1) that encode the granted capabilities as scopes. The authorization server
is a separate service from the agents themselves; a single authorization server MAY
serve multiple agents within an organisation, or each agent MAY use a dedicated
authorization server.

**Inbox.** The inbox is the single canonical HTTP endpoint where an agent receives
ARSIA messages. The inbox URL is advertised in the agent's discovery metadata (§7.1)
and serves as the target for all HTTP-based message delivery (§8.1). Each agent MUST
expose exactly one inbox endpoint. The inbox endpoint accepts POST requests containing
ARSIA message envelopes and returns ARSIA response envelopes.

**Correlation ID.** A correlation identifier is a UUID v4 string that links a response
message to its originating request message. When an agent sends a response, error,
pending_approval, or approval_decision message, it MUST include a `correlation_id`
field whose value equals the `id` field of the original request message. Correlation identifiers enable
request-response matching in asynchronous communication patterns and provide the
linkage necessary for audit trail reconstruction.

**Idempotency Key.** An idempotency key is a unique string, between 1 and 128
characters in length, that ensures duplicate requests produce the same result without
re-execution. Idempotency keys are scoped to the tuple of (sender agent-id, recipient
agent-id, payload type): the same key value sent by different senders or for different
payload types is treated as a distinct request. Servers MUST store idempotency keys
for the duration specified by the `idempotency.expires_at` field and MUST return the
original response for any duplicate key received within that window (§10).

**Data Residency Zone.** A data residency zone is a geographic region — typically an
ISO 3166-1 alpha-2 country code or a supranational identifier such as "EU" — where
message processing and storage MUST occur. When a message envelope specifies a data
residency zone in the `compliance.data_residency` field, the message MUST be routed
through a compliance broker whose physical infrastructure resides entirely within the
declared zone (§9.2). The data residency constraint applies to all processing of the
message, including temporary storage, logging, and audit trail generation.

---

## 3. Agent Identifier Format

### 3.1 ABNF Grammar

Agent identifiers in the ARSIA protocol conform to the following grammar, specified
using the Augmented Backus-Naur Form (ABNF) notation per [RFC 5234]:

```abnf
agent-id         = "agent:" org-segment 1*("." sub-segment) ["/" resource-segment]

org-segment      = 1*(ALPHA / DIGIT / "-")

sub-segment      = 1*(ALPHA / DIGIT / "-")

resource-segment = 1*(ALPHA / DIGIT / "-" / "_")
```

The `agent-id` production defines a hierarchical identifier consisting of a mandatory
`agent:` scheme prefix, an organisational segment, one or more sub-segments separated
by periods, and an optional resource segment separated by a forward slash.

The `org-segment` identifies the organisation that operates the agent. It MUST consist
of one or more ASCII letters, digits, or hyphens. The `org-segment` MUST NOT begin or
end with a hyphen.

Each `sub-segment` further qualifies the agent within the organisation's namespace. At
least one sub-segment is required, separated from the org-segment by a period. Each
sub-segment follows the same character rules as the org-segment: one or more ASCII
letters, digits, or hyphens, with no leading or trailing hyphens.

The optional `resource-segment` identifies a specific resource or channel within an
agent. When present, it is separated from the preceding segments by a forward slash.
The resource-segment permits underscores in addition to letters, digits, and hyphens.

### 3.2 Examples

The following are valid ARSIA agent identifiers:

```
agent:acme.billing
```

This identifies the billing agent operated by the organisation "acme". The org-segment
is "acme" and the single sub-segment is "billing".

```
agent:contoso.crm/notifications
```

This identifies the notifications resource within the CRM agent operated by "contoso".
The org-segment is "contoso", the sub-segment is "crm", and the resource-segment is
"notifications".

```
agent:arsialabs.demo.risk-assessor
```

This identifies the risk assessor demo agent operated by "arsia". The org-segment is
"arsia" and the sub-segments are "demo" and "risk-assessor", forming a three-level
hierarchy.

```
agent:europa.mifid.compliance-checker
```

This identifies a MiFID compliance checker agent operated by "europa". The org-segment
is "europa" and the sub-segments are "mifid" and "compliance-checker".

### 3.3 Rules

The following rules govern ARSIA agent identifiers:

1. **Maximum length.** An agent identifier MUST NOT exceed 256 characters in total
   length, including the `agent:` prefix.

2. **Uniqueness.** An agent identifier MUST be globally unique within a deployment.
   The mechanism for ensuring uniqueness is outside the scope of this specification,
   but implementations SHOULD use a registry or namespace authority to prevent
   collisions.

3. **No personally identifiable information.** An agent identifier MUST NOT contain
   personally identifiable information (PII). Agent identifiers are transmitted in
   cleartext in message envelopes, discovery responses, audit logs, and error
   messages. Including PII in agent identifiers would violate the privacy requirements
   specified in §13.3.

4. **Case sensitivity.** Agent identifiers are case-sensitive. The identifiers
   `agent:acme.billing` and `agent:Acme.Billing` are distinct. Implementations SHOULD
   use lowercase identifiers to avoid confusion, but MUST NOT normalise case during
   comparison.

   ARSIA agents are software — they do not produce accidental capitalisation variations
   the way human users might. Case-sensitive comparison prevents identity collisions:
   two agents registered as `agent:acme.billing` and `agent:Acme.Billing` are
   cryptographically distinct (different JWKS entries, different Ed25519 keys). Silent
   case normalisation by a broker or intermediary could route messages to the wrong
   agent — a security violation. The lowercase recommendation ensures visual consistency
   in logs and interoperability with systems that normalise case (DNS, HTTP headers).

5. **Mandatory prefix.** The `agent:` prefix is mandatory and MUST be present in all
   contexts where an agent identifier is used — including the `from` and `to` fields
   of message envelopes, the `sub` and `aud` claims of access tokens, discovery
   metadata, and error responses.

6. **Character restrictions.** Only ASCII letters (`A-Z`, `a-z`), digits (`0-9`),
   hyphens (`-`), underscores (`_`, in resource-segment only), periods (`.`, as
   segment separators), and forward slashes (`/`, as resource separator) are permitted
   after the `agent:` prefix. No whitespace, no Unicode characters outside the ASCII
   range.

7. **Segment restrictions.** Neither the org-segment nor any sub-segment MAY begin or
   end with a hyphen. The resource-segment, if present, MUST NOT be empty (i.e., a
   trailing slash with no following characters is invalid).

8. **Validation pattern.** Implementations MAY use the following regular expression
   for agent identifier validation:

   ```
   ^agent:[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*(\/[a-zA-Z0-9][a-zA-Z0-9_-]*)?$
   ```

   This pattern enforces the `agent:` prefix, the segment structure, the hyphen
   restrictions, and the optional resource-segment.

---

## 4. Message Envelope

An ARSIA message envelope is a JSON object that conforms to the structure defined in
this section. The envelope is the unit of transmission, validation, and audit in the
ARSIA protocol. Every ARSIA message — regardless of intent, transport, or compliance
context — is represented as an envelope.

The envelope fields are divided into three categories: required fields that MUST be
present in every message (§4.1), conditional required fields that MUST be present when
certain conditions hold (§4.2), and optional fields that MAY be present (§4.3).

### 4.1 Required Fields

The following fields MUST be present in every ARSIA message envelope. A message that
is missing any of these fields is invalid and MUST be rejected with error code
`invalid_request` (§11.2).

#### 4.1.1 `v` — Protocol Version

- **Type:** string
- **Format:** Major and minor version, dot-separated.
- **Pattern:** `^\d+\.\d+$`
- **Current value:** `"1.0"`
- **Constraints:** The `v` field declares the protocol version used to construct this
  message. The version string consists of a major version number and a minor version
  number separated by a period. Both numbers are non-negative integers with no leading
  zeros (except for the value "0" itself). The current protocol version is `"1.0"`.
  Implementations MUST reject messages whose major version exceeds the maximum major
  version they support. Minor version differences within the same major version MUST
  be handled gracefully: unknown fields introduced in a later minor version SHOULD be
  ignored by implementations that do not recognise them.

#### 4.1.2 `id` — Message Identifier

- **Type:** string
- **Format:** UUID version 4 per [RFC 9562].
- **Pattern:** `^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$`
- **Constraints:** The `id` field is a universally unique identifier for this message.
  It MUST be a valid UUID version 4 string in the canonical 8-4-4-4-12 hexadecimal
  format with lowercase or uppercase hex digits (implementations SHOULD produce
  lowercase). The UUID MUST be generated using a cryptographically secure random
  number generator. The `id` is used for correlation (§4.2.1), audit trail linkage,
  idempotency conflict detection, and log correlation. Message identifiers MUST NOT
  be sequential or predictable.

#### 4.1.3 `ts` — Timestamp

- **Type:** string
- **Format:** RFC 3339 [RFC 3339] date-time with mandatory millisecond precision and
  UTC timezone designator.
- **Pattern:** `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$`
- **Example:** `"2026-03-24T14:30:00.000Z"`
- **Constraints:** The `ts` field records the moment the sender constructed this
  message. The timestamp MUST be expressed in UTC (indicated by the `Z` suffix) with
  exactly three fractional digits (millisecond precision). Implementations MUST NOT
  use local timezone offsets. Recipients MAY reject messages whose `ts` value differs
  from the recipient's current time by more than the clock skew tolerance defined in
  §8.3 (±300 seconds).

#### 4.1.4 `from` — Sender Agent Identifier

- **Type:** string
- **Format:** Agent identifier as defined in §3.
- **Constraints:** The `from` field identifies the agent that constructed and signed
  this message. The value MUST be a valid ARSIA agent identifier conforming to the
  grammar in §3.1. The `from` field MUST match the `sub` claim of the access token
  presented with the message (§6.1). If the `from` field does not match the token's
  `sub` claim, the receiving agent MUST reject the message with error code
  `unauthorized` (§11.2).

#### 4.1.5 `to` — Recipient Agent Identifier

- **Type:** string
- **Format:** Agent identifier as defined in §3.
- **Constraints:** The `to` field identifies the intended recipient of this message.
  The value MUST be a valid ARSIA agent identifier conforming to the grammar in §3.1.
  The `to` field MUST match the `aud` claim of the access token presented with the
  message (§6.1). If the `to` field does not match the token's `aud` claim, the
  receiving agent MUST reject the message with error code `unauthorized` (§11.2). In
  brokered routing scenarios (§9.2), the `to` field always contains the identifier of
  the final recipient, not the broker.

#### 4.1.6 `intent` — Message Intent

- **Type:** string
- **Format:** Enumerated value.
- **Allowed values:** `"request"`, `"response"`, `"event"`, `"error"`,
  `"pending_approval"`, `"approval_decision"`
- **Constraints:** The `intent` field declares the semantic purpose of this message.
  Each intent value has specific semantics and field requirements:

  - **`"request"`**: A message requesting an action from the recipient. REQUIRES
    `capabilities` (§4.2.3) and `expires_at` (§4.2.2). The sender expects a
    `"response"` or `"error"` message in reply.

  - **`"response"`**: A message carrying the result of a previously received request.
    REQUIRES `correlation_id` (§4.2.1) referencing the original request's `id`.

  - **`"event"`**: A one-way notification that does not expect a reply. Events are
    fire-and-forget: the sender SHOULD NOT expect a response.

  - **`"error"`**: A message indicating that processing of a prior message failed.
    REQUIRES `correlation_id` (§4.2.1) referencing the original message's `id`.
    The `payload.error` object MUST be present (§4.4).

  - **`"pending_approval"`**: A message indicating that the recipient's action
    requires human oversight approval before execution. REQUIRES `correlation_id`
    (§4.2.1) and `expires_at` (§4.2.2). The full semantics of `pending_approval`
    are defined in ARSIA-Actions.md §3.

  - **`"approval_decision"`**: A message carrying the human oversight decision
    (approve or reject) for a prior `pending_approval` message. REQUIRES
    `correlation_id` (§4.2.1) and `capabilities` (§4.2.3). The full semantics
    of `approval_decision` are defined in ARSIA-Actions.md §3.

### 4.2 Conditional Required Fields

The following fields are REQUIRED under specific conditions. If the condition holds
and the field is absent, the message is invalid and MUST be rejected with error code
`invalid_request` (§11.2).

#### 4.2.1 `correlation_id` — Correlation Identifier

- **Type:** string
- **Format:** UUID version 4 per [RFC 9562].
- **Pattern:** `^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$`
- **Condition:** REQUIRED when `intent` is `"response"`, `"error"`,
  `"pending_approval"`, or `"approval_decision"`.
- **Constraints:** The `correlation_id` MUST equal the `id` field of the original
  message to which this message is a reply. This linkage enables request-response
  matching, audit trail reconstruction, and distributed tracing. An agent receiving a
  response or error message with a `correlation_id` that does not match any known
  outstanding request SHOULD log the discrepancy and MAY discard the message.

#### 4.2.2 `expires_at` — Expiration Timestamp

- **Type:** string
- **Format:** RFC 3339 [RFC 3339] date-time with mandatory millisecond precision and
  UTC timezone designator.
- **Pattern:** `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$`
- **Condition:** REQUIRED when `intent` is `"request"` or `"pending_approval"`.
- **Constraints:** The `expires_at` field declares the absolute timestamp after which
  this message MUST NOT be processed. The timestamp format is identical to the `ts`
  field (§4.1.3). The `expires_at` value MUST be strictly greater than the `ts`
  value. Recipients MUST reject messages whose `expires_at` is in the past (after
  accounting for the clock skew tolerance of ±300 seconds defined in §8.3) with
  error code `invalid_request`. The `expires_at` field serves two purposes: it
  prevents stale requests from being executed, and it bounds the window during which
  replay attacks using captured messages could succeed.

#### 4.2.3 `capabilities` — Required Capabilities

- **Type:** array of strings
- **Format:** Each string is a capability identifier conforming to the grammar defined
  in ARSIA-Actions.md §1.1. Each capability string in this field MUST be a concrete
  capability (`concrete-cap` per Actions §1.1). Wildcard capabilities (`wildcard-cap`)
  are not permitted in the message envelope's `capabilities` field — wildcards are
  reserved for access token scopes (Actions §1.2).
- **Condition:** REQUIRED when `intent` is `"request"` or `"approval_decision"`.
- **Constraints:** The `capabilities` array MUST contain at least one element. Each
  element MUST be unique within the array (no duplicate capability strings). The
  capabilities listed in this field declare what permissions the sender is requesting
  from the recipient in order to fulfil this request. For `approval_decision`, the
  field asserts the authority under which the approver is acting (see
  ARSIA-Actions.md §3.3). The receiving agent MUST verify
  that the sender's access token (§6.1) includes a scope that covers all listed
  capabilities (§6.4). If any listed capability is not covered by the token's scope,
  the receiving agent MUST reject the message with error code `forbidden` (§11.2).

### 4.3 Optional Fields

The following fields are OPTIONAL. Their absence does not affect envelope validity.
When present, they MUST conform to the formats and constraints defined below.

#### 4.3.1 `min_v` — Minimum Protocol Version

- **Type:** string
- **Format:** Major and minor version, dot-separated.
- **Pattern:** `^\d+\.\d+$`
- **Constraints:** The `min_v` field declares the minimum protocol version that the
  sender is willing to accept in a response. If the recipient's maximum supported
  version is less than `min_v`, the recipient MUST reject the message with error code
  `not_implemented` (§11.2), including the recipient's supported version range in the
  error details (§7.4). If `min_v` is absent, the sender accepts any protocol version
  up to and including the version declared in `v`.

#### 4.3.2 `idempotency` — Idempotency Configuration

- **Type:** object
- **Constraints:** The `idempotency` object contains two fields:

  - **`key`** (string, REQUIRED within this object): The idempotency key. MUST be
    between 1 and 128 characters in length (inclusive). MUST be unique per the tuple
    (`from`, `to`, `payload.type`). The key MAY contain any printable ASCII characters
    (code points 0x20 through 0x7E). The full semantics of idempotency are defined in
    §10.

  - **`expires_at`** (string, REQUIRED within this object): The absolute timestamp
    after which the server MAY discard the stored idempotency record. Format is
    identical to the `ts` field (§4.1.3): RFC 3339 with millisecond precision and UTC
    timezone designator. The `expires_at` value MUST be strictly greater than the
    message's `ts` value.

#### 4.3.3 `context` — Distributed Context

- **Type:** object
- **Constraints:** The `context` object carries distributed tracing and localisation
  metadata. All fields within the context object are OPTIONAL:

  - **`trace_id`** (string): A trace identifier conforming to the W3C Trace Context
    specification [W3C-TraceContext]. The value MUST be a 32-character lowercase
    hexadecimal string representing a 128-bit trace identifier.
    Pattern: `^[0-9a-f]{32}$`

  - **`span_id`** (string): A span identifier conforming to the W3C Trace Context
    specification. The value MUST be a 16-character lowercase hexadecimal string
    representing a 64-bit span identifier.
    Pattern: `^[0-9a-f]{16}$`

  - **`flags`** (integer): Trace flags as defined in W3C Trace Context. The value
    MUST be an integer between 0 and 255 (inclusive), representing an 8-bit field.
    The least significant bit (0x01) indicates that the trace is sampled.

  - **`locale`** (string): A BCP 47 language tag [BCP 47] indicating the preferred
    locale for the message content and any human-readable responses. Examples:
    `"en-GB"`, `"pt-PT"`, `"de-DE"`. Implementations MAY use this field to select
    the language of error descriptions or human-readable output.

  - **`priority`** (integer): A priority hint for message processing, expressed as
    an integer from 0 (lowest priority) to 10 (highest priority). The default priority
    when this field is absent is 5. Implementations MAY use this field to influence
    queue ordering but are not required to guarantee priority-based processing.

#### 4.3.4 `payload` — Message Payload

- **Type:** object
- **Constraints:** The `payload` object carries the application-specific content of
  the message. Its structure is defined in §4.4. When the `payload` field is absent,
  the message carries only metadata (which is valid for certain event types or
  acknowledgements).

#### 4.3.5 `security` — Security Metadata

- **Type:** object
- **Constraints:** The `security` object carries digital signature and encryption
  metadata for the message. When the `security` object is present, all three core
  signature fields (`alg`, `kid`, `sig`) are REQUIRED within it. The full signing
  and verification procedures are defined in §5.

  - **`alg`** (string, REQUIRED within this object): The cryptographic algorithm used
    to produce the digital signature. MUST be one of the following values:
    - `"EdDSA"` — Ed25519 digital signature algorithm. Conformant implementations
      MUST support this algorithm.
    - `"ES256"` — ECDSA using the P-256 curve and SHA-256 hash. Conformant
      implementations SHOULD support this algorithm.
    - `"RS256"` — RSASSA-PKCS1-v1_5 using SHA-256. Conformant implementations MAY
      support this algorithm for legacy interoperability only.

  - **`kid`** (string, REQUIRED within this object): The key identifier of the signing
    key. The `kid` value MUST correspond to a key published in the sender's JWKS
    endpoint (§7.3). The format MUST be `{agent-id}#{keyN}` (e.g.,
    `"agent:acme.billing#key1"`).

  - **`sig`** (string, REQUIRED within this object): The digital signature, encoded as
    a base64url string without padding per [RFC 4648] §5. For Ed25519 signatures, this
    is a 64-byte value that encodes to 86 base64url characters. The signing input is
    the RFC 8785 canonical form of the message with the `security` field removed, as
    defined in §5.1.

  - **`encrypted`** (boolean, OPTIONAL): Indicates whether the `payload` field is
    encrypted. Defaults to `false` when absent. When `true`, the `payload` field
    contains a JWE compact serialization string rather than a JSON object (§5.3).

  - **`enc_alg`** (string, conditionally REQUIRED): The key encryption algorithm used
    for payload encryption. REQUIRED when `encrypted` is `true`. Values are drawn from
    the JOSE registry [RFC 7518]: `"ECDH-ES"`, `"ECDH-ES+A256KW"`, `"RSA-OAEP-256"`,
    etc.

  - **`enc_method`** (string, conditionally REQUIRED): The content encryption method
    used for payload encryption. REQUIRED when `encrypted` is `true`. Values are
    drawn from the JOSE registry: `"A256GCM"`, `"A128CBC-HS256"`, etc.

> **Note (informative).** Although structurally optional in
> the envelope schema, the `security` field is effectively
> required for messages with `intent` values of `request`,
> `response`, `pending_approval`, and `approval_decision`
> (§5.2). It is optional only for `event` and `error`
> intents.

#### 4.3.6 `compliance` — Compliance Metadata

- **Type:** object
- **OPTIONAL.**
- **Constraints:** The `compliance` object is an OPTIONAL field in every ARSIA message
  envelope. When present, it declares the regulatory requirements that apply to the
  processing of this specific message. The formal JSON Schema for the `compliance`
  field is defined in `arsia-compliance-field.schema.json`.

> **Note (informative):** The `compliance` object permits additional properties beyond
> the sub-fields listed below. This is intentional — compliance profiles (§1.2) can
> define profile-specific fields (e.g., `clock_skew_seconds`) without requiring changes
> to this schema. Implementations are encouraged to validate known field names at the
> application layer to detect typos in standard field names.

The `compliance` object contains the following sub-fields:

#### 4.3.6.1 `profile`

- **Type:** string
- **OPTIONAL.** Default: `"GDPR-STANDARD"` when the `compliance` field is present but
  `profile` is not set.
- **Description:** The name of the compliance profile to apply. Known profile names
  are: `"GDPR-STANDARD"`, `"EU-AI-ACT-HIGH-RISK"`, `"MIFID-II"`, `"PAC-AGRICULTURE"`,
  `"EU-AI-ACT-LIMITED-RISK"`, `"DSA-VLOP"`, `"DORA"`. Unknown profile names SHOULD
  trigger a compliance warning; in strict mode, unknown profile names MUST be rejected
  with error code `"invalid_request"` and `details: { "unknown_profile": true }`.

#### 4.3.6.2 `data_residency`

- **Type:** string
- **Format:** ISO 3166-1 alpha-2 country code or supranational identifier (e.g.,
  `"EU"`, `"DE"`, `"PT"`).
- **OPTIONAL.**
- **Description:** The geographic zone where this message MUST be processed and stored.
  When set, the routing layer MUST use brokered routing through a Compliance Broker
  whose infrastructure resides within the declared zone (§9.2). The
  value `"EU"` indicates that any EU/EEA member state's infrastructure satisfies the
  requirement.

#### 4.3.6.3 `audit_required`

- **Type:** boolean
- **OPTIONAL.** Default: per profile (ARSIA-State.md §6).
- **Description:** Whether this message MUST generate an `ArsiaAuditRecord` (ARSIA-State.md §7.1).
  When `true`, the receiving agent MUST create and persist an audit record before
  acknowledging the message. When `false`, audit record generation is OPTIONAL.

#### 4.3.6.4 `retention_days`

- **Type:** integer
- **Minimum:** 1
- **OPTIONAL.** Default: per profile (ARSIA-State.md §6).
- **Description:** The minimum number of days that the audit record for this message
  MUST be retained. Per-message values override the profile default but MUST NOT be
  less than the profile's minimum. If a per-message value is lower than the profile
  minimum, the receiving agent MUST use the profile minimum and SHOULD log a compliance
  warning.

#### 4.3.6.5 `human_oversight`

- **Type:** string
- **Enum:** `"not_required"`, `"required_before_execution"`, `"required_within_24h"`,
  `"required_post_execution"`
- **OPTIONAL.** Default: per profile (ARSIA-State.md §6).
- **Description:** The human oversight mode required for actions triggered by this
  message.

  `"not_required"` — No human oversight is needed for this message. The agent MAY
  execute actions autonomously.

  `"required_before_execution"` — The action MUST NOT execute until a human approves
  it. This triggers the `pending_approval` / `approval_decision` flow defined in
  ARSIA-Actions.md §3. The receiving agent MUST respond with a `pending_approval`
  message and wait for an `approval_decision` from an agent with the
  `arsiaprotocol.oversight.approve` capability.

  `"required_within_24h"` — The action MAY execute immediately, but a human MUST
  review the action and its results within 24 hours of execution. If no review occurs
  within 24 hours, the implementation MUST log a compliance warning with event type
  `"oversight_timeout"`. This mode is suitable for time-sensitive actions where
  blocking is impractical but post-hoc review is mandated.

  `"required_post_execution"` — The action executes immediately. Results are audited
  and made available for human review. No blocking occurs, and no timeout enforcement
  is applied. This mode is suitable for low-risk actions under profiles that require
  traceability but not pre-approval.

#### 4.3.6.6 `explainability_required`

- **Type:** boolean
- **OPTIONAL.** Default: per profile (ARSIA-State.md §6).
- **Description:** Whether responses to this message MUST include a
  `payload.explanation` object conforming to ARSIA-Actions.md §5.2. When `true`, the
  response MUST include an explanation with `reasoning`, `confidence`, and `inputs_used`
  fields. This field implements EU AI Act Article 13 transparency obligations at the
  message level.

#### 4.3.6.7 `pii_involved`

- **Type:** boolean
- **OPTIONAL.** Default: `false`.
- **Description:** Whether this message contains or triggers processing of personal
  data as defined by GDPR Article 4(1). When `true`, the `legal_basis` field MUST be
  set (§4.3.8, Rule 2). Agents processing messages with `pii_involved: true` MUST apply
  appropriate data protection measures as defined by GDPR Article 5(1)(f) and SHOULD
  ensure the data is encrypted in transit and at rest.

#### 4.3.6.8 `legal_basis`

- **Type:** string
- **Enum:** `"consent"`, `"contract"`, `"legal_obligation"`, `"vital_interests"`,
  `"public_task"`, `"legitimate_interests"`
- **OPTIONAL.** REQUIRED when `pii_involved` is `true`.
- **Description:** The GDPR Article 6(1) legal basis for processing personal data.
  Each value maps to a specific sub-paragraph:

  `"consent"` — Art. 6(1)(a): the data subject has given consent.
  `"contract"` — Art. 6(1)(b): processing necessary for performance of a contract.
  `"legal_obligation"` — Art. 6(1)(c): processing necessary for compliance with a
  legal obligation.
  `"vital_interests"` — Art. 6(1)(d): processing necessary to protect vital interests.
  `"public_task"` — Art. 6(1)(e): processing necessary for a task carried out in the
  public interest.
  `"legitimate_interests"` — Art. 6(1)(f): processing necessary for legitimate
  interests pursued by the controller.

  When the state entry being created or updated has `pii_classification` of `"sensitive"`
  (ARSIA-State.md §2.1.10), the `legal_basis` MUST be one of the following Art. 9(2)
  grounds:

  `"explicit_consent"` — Art. 9(2)(a): data subject has given explicit consent for one
  or more specified purposes.
  `"employment_social_security"` — Art. 9(2)(b): processing necessary for employment,
  social security, and social protection law obligations.
  `"vital_interests_incapacity"` — Art. 9(2)(c): processing necessary to protect vital
  interests where data subject is physically or legally incapable of giving consent.
  `"legitimate_activities"` — Art. 9(2)(d): processing by a foundation, association, or
  not-for-profit body with a political, philosophical, religious, or trade-union aim,
  relating solely to members or former members.
  `"manifestly_public"` — Art. 9(2)(e): processing relates to personal data manifestly
  made public by the data subject.
  `"legal_claims"` — Art. 9(2)(f): processing necessary for the establishment, exercise,
  or defence of legal claims.
  `"substantial_public_interest"` — Art. 9(2)(g): processing necessary for reasons of
  substantial public interest, on the basis of Union or Member State law.
  `"health_medicine"` — Art. 9(2)(h): processing necessary for preventive or
  occupational medicine, medical diagnosis, or the provision of health or social care.
  `"public_health"` — Art. 9(2)(i): processing necessary for reasons of public interest
  in the area of public health, such as cross-border health threats.
  `"archiving_research"` — Art. 9(2)(j): processing necessary for archiving purposes in
  the public interest, scientific or historical research, or statistical purposes.

#### 4.3.6.9 `ai_system_classification`

- **Type:** string
- **Enum:** `"minimal-risk"`, `"limited-risk"`, `"high-risk"`, `"unacceptable-risk"`
- **OPTIONAL.**
- **Description:** Per-message EU AI Act risk classification. This field allows a
  message to declare a risk classification that differs from the agent-level
  classification in `IdentityRecord.ai_system_classification`
  (ARSIA-Identity.md §1.2), subject to the constraint defined in §4.3.7. A high-risk
  agent MAY send a minimal-risk message (classification downgrade). A minimal-risk agent
  MUST NOT send a high-risk message (classification escalation is prohibited).

#### 4.3.7 Field Inheritance and Defaults

The effective value of each compliance sub-field is determined by the following
precedence chain. Higher-priority sources override lower-priority sources.

**Priority 1 — Per-message field value (highest).** An explicit value set in the
message's `compliance` object takes precedence over all other sources. This is the
mechanism by which individual messages can override profile defaults for specific
interactions.

**Priority 2 — Profile defaults.** When the message declares a `compliance.profile`,
the profile's default values (from `arsia-compliance-profiles.json`, ARSIA-State.md §6) fill any
sub-field that is not explicitly set in the message. Profile defaults provide the
baseline compliance posture for the declared regulatory context.

**Priority 3 — GDPR-STANDARD defaults.** When the `compliance` field is present but
no `profile` is declared, the `GDPR-STANDARD` profile defaults apply. This ensures
that any message with a `compliance` field receives at least baseline GDPR coverage.

**Priority 4 — No compliance (lowest).** When the `compliance` field is entirely
absent from the message envelope, no compliance obligations apply at the protocol level.
The message is processed under Core conformance only (§12.1). This is
the default for agents that do not operate in regulated environments.

Profile defaults fill any field not explicitly set in the message. Per-message values
override profile defaults for that specific message only — they do not modify the
profile definition.

**`ai_system_classification` constraint.** The per-message `ai_system_classification`
field interacts with the agent-level classification in
`IdentityRecord.ai_system_classification` (ARSIA-Identity.md §1.2) as follows:

- If `IdentityRecord.ai_system_classification` is `"high-risk"` and the message's
  `compliance.ai_system_classification` is `"minimal-risk"`: this is ALLOWED. A
  high-risk agent may perform actions that are individually classified as minimal-risk.

- If `IdentityRecord.ai_system_classification` is `"minimal-risk"` and the message's
  `compliance.ai_system_classification` is `"high-risk"`: this is PROHIBITED.
  Receiving agents MUST reject the message with error code `"invalid_request"` and
  `details: { "classification_escalation": true }`. An agent cannot escalate its own
  classification per-message — this would allow agents to claim regulatory capabilities
  they have not been assessed for.

**`retention_days` floor enforcement.** When a per-message `retention_days` value is
lower than the profile's minimum, the effective value MUST be the profile's minimum.
Implementations SHOULD log a compliance warning when this override occurs.

#### 4.3.8 Compliance Field Validation Rules

Receiving agents MUST validate the compliance field according to the following rules.
Validation MUST occur after message signature verification (§5.2) and
before payload processing. A message that fails compliance validation MUST be rejected
with the specified error code.

**Rule 1 — Profile name validation.** If `compliance.profile` is set, it MUST be a
known profile name as defined in ARSIA-State.md §6 or in a future extension of this specification. If
the profile name is not known:

- In non-strict mode (default): the agent MUST log a compliance warning and apply
  `GDPR-STANDARD` defaults.
- In strict mode (implementation-configurable): the agent MUST reject the message with
  error code `"invalid_request"` and `details: { "unknown_profile": true }`.

**Rule 2 — PII requires legal basis.** If `compliance.pii_involved` is `true` and
`compliance.legal_basis` is not set, the message MUST be rejected with error code
`"invalid_request"` and `details: { "missing_legal_basis": true }`. This enforces
GDPR Article 6(1): processing of personal data requires a lawful basis.

**Rule 3 — High-risk requires human oversight.** If the effective
`compliance.ai_system_classification` is `"high-risk"`, the effective
`compliance.human_oversight` MUST NOT be null or absent. If no human oversight mode is
declared (neither per-message nor via profile defaults), the message MUST be rejected
with error code `"invalid_request"` and
`details: { "high_risk_missing_oversight": true }`. This enforces EU AI Act
Article 14.

**Rule 4 — MiFID II retention floor.** If `compliance.profile` is `"MIFID-II"`, the
effective `retention_days` (after applying per-message override or profile default)
MUST be at least 1827 (5 years). If the effective value is less than 1827, the message
MUST be rejected with error code `"invalid_request"` and
`details: { "insufficient_retention": true, "required": 1827, "provided": N }` where
`N` is the effective value. This enforces MiFID II Article 16(7) as implemented via
Commission Delegated Regulation (EU) 2017/565, Article 72.

**Rule 5 — Data residency triggers brokered routing.** If `compliance.data_residency`
is set, the message MUST be routed through a Compliance Broker whose infrastructure
resides within the declared zone (§9.2). The compliance layer
validates that `data_residency` is a well-formed ISO 3166-1 alpha-2 code or
supranational identifier. The routing layer enforces the broker requirement.

**Rule 6 — Classification escalation prohibition.** The effective
`compliance.ai_system_classification` MUST NOT exceed
`IdentityRecord.ai_system_classification` (ARSIA-Identity.md §1.2). The classification
hierarchy from lowest to highest is: `"minimal-risk"` < `"limited-risk"` <
`"high-risk"` < `"unacceptable-risk"`. If the per-message classification exceeds the
agent-level classification, the message MUST be rejected with error code
`"invalid_request"` and `details: { "classification_escalation": true }`.

**Rule 7 — PII requires audit trail.** When the effective `compliance.pii_involved` is
`true`, the effective `audit_required` MUST be `true`, regardless of the per-message
value or profile default. If a sender explicitly sets `audit_required` to `false` on a
message with `pii_involved` set to `true`, the receiving agent MUST override
`audit_required` to `true` and SHOULD log a compliance warning with `event_type`
`"compliance_warning"`. This enforces GDPR Article 5(2) accountability: processing of
personal data must produce evidence of compliance.

**Rule 8 — Sensitive data requires Art. 9(2) legal basis.** When a SET operation
creates or updates a state entry with `pii_classification` of `"sensitive"`, the
`compliance.legal_basis` in the message envelope MUST be one of the Art. 9(2) grounds:
`"explicit_consent"`, `"employment_social_security"`,
`"vital_interests_incapacity"`, `"legitimate_activities"`, `"manifestly_public"`,
`"legal_claims"`, `"substantial_public_interest"`, `"health_medicine"`,
`"public_health"`, `"archiving_research"`. If an Art. 6(1) ground is provided for a
sensitive entry, the SET MUST be rejected with error code `"invalid_request"` and
`details: { "sensitive_requires_art9_basis": true }`. This enforces GDPR Article 9(2):
processing of special categories of personal data requires a stricter legal basis than
ordinary personal data.

### 4.4 Payload Structure

The `payload` object within the envelope carries the application-specific content of
the message. When present, the `payload` object MUST contain a `type` field and MAY
contain additional fields depending on the message intent.

#### 4.4.1 `type` — Payload Type Identifier

- **Type:** string
- **REQUIRED** within the `payload` object.
- **Format:** Reverse domain notation with an optional action path.
- **Pattern:** `^[a-zA-Z][a-zA-Z0-9]*(\.[a-zA-Z][a-zA-Z0-9]*)*(\/[a-zA-Z][a-zA-Z0-9_-]*)*$`
- **Examples:**
  - `"com.example.notes/get"` — Retrieve notes from the example.com notes service.
  - `"arsiaprotocol.echo"` — The ARSIA echo capability (used in conformance testing).
  - `"eu.mifid.risk/assess"` — Request a MiFID II risk assessment.
  - `"com.acme.billing/create-invoice"` — Create an invoice in Acme's billing system.
  - `"com.example.notes/create/rollback"` — Rollback request for a previously
    executed `com.example.notes/create` action (see ARSIA-Actions.md §4.2).
- **Constraints:** The `type` field uniquely identifies the payload schema and
  semantics. The reverse domain notation ensures global uniqueness across
  organisations. The optional path segments (after the first `/`) identify a
  specific action or resource within the domain; additional `/`-separated segments
  MAY be used to address sub-actions such as the rollback convention defined in
  ARSIA-Actions.md §4.2. Implementations MUST reject messages with payload types
  they do not recognise, responding with error code `not_implemented` (§11.2).
- **Errata (Draft-01.1, ERRATA-01):** The Draft-01 pattern published on
  2026-04-10 was `^[a-zA-Z][a-zA-Z0-9]*(\.[a-zA-Z][a-zA-Z0-9]*)*(\/[a-zA-Z][a-zA-Z0-9_]*)?$`,
  which (a) omitted the hyphen from the path-segment character class and (b)
  allowed at most one path segment. Both restrictions contradicted the spec's
  own normative examples (`com.acme.billing/create-invoice` and
  `com.example.notes/create/rollback` in ARSIA-Actions.md §4.2). The corrected
  pattern above is a strict superset of the Draft-01 pattern — every previously
  valid `payload.type` value remains valid. This is a text correction only; the
  wire protocol version remains `1.0`.

> **Informative note.** The `payload.type` format is distinct from the capability string
> grammar defined in ARSIA-Actions.md §1.1. See that section for a comparison of the two
> formats.

#### 4.4.2 `version` — Payload Version

- **Type:** string
- **OPTIONAL.**
- **Format:** Major and minor version, dot-separated.
- **Pattern:** `^\d+\.\d+$`
- **Constraints:** The `version` field indicates the version of the payload schema
  identified by `type`. When absent, the version is assumed to be the latest version
  known to the receiving agent. Senders SHOULD include this field when communicating
  with agents that may support multiple payload schema versions.

#### 4.4.3 `args` — Request Arguments

- **Type:** any valid JSON value (object, array, string, number, boolean, or null)
- **OPTIONAL.** SHOULD be present when `intent` is `"request"` or
  `"pending_approval"`.
- **Constraints:** The `args` field carries the input parameters for the requested
  action. The structure and semantics of `args` are defined by the payload type
  schema and are outside the scope of this specification.

#### 4.4.4 `result` — Response Result

- **Type:** any valid JSON value
- **OPTIONAL.** SHOULD be present when `intent` is `"response"`.
- **Constraints:** The `result` field carries the output of a successfully processed
  request. The structure and semantics of `result` are defined by the payload type
  schema.

#### 4.4.5 `data` — Event Data

- **Type:** any valid JSON value
- **OPTIONAL.** SHOULD be present when `intent` is `"event"`.
- **Constraints:** The `data` field carries the content of an event notification. The
  structure and semantics of `data` are defined by the payload type schema.

#### 4.4.6 `error` — Error Details

- **Type:** object
- **REQUIRED** when `intent` is `"error"`.
- **Constraints:** The `error` object describes why processing of a prior message
  failed. It contains the following fields:

  - **`code`** (string, REQUIRED): One of the standard error codes defined in §11.2.

  - **`description`** (string, REQUIRED): A human-readable description of the error.
    This description is intended for developers and operators; it MUST NOT contain
    sensitive information such as internal stack traces, database queries, or
    credentials.

  - **`details`** (object, OPTIONAL): A structured object containing additional
    context about the error. The content of `details` varies by error code. For
    example, a `forbidden` error MUST include `required_capabilities` and
    `provided_capabilities` arrays (§6.4). A `not_implemented` error MUST include
    `supported_versions` (§7.4). A `rate_limited` error SHOULD include
    `retry_after_seconds`.

#### 4.4.7 Mutual Exclusivity of Content Fields

Only one of `args`, `result`, `data`, or `error` SHOULD be present per message. The
correspondence between intent and content field is:

| Intent               | Expected content field | Notes                        |
|----------------------|-----------------------|------------------------------|
| `request`            | `args`                | Input parameters             |
| `response`           | `result`              | Output value                 |
| `event`              | `data`                | Event notification content   |
| `error`              | `error`               | Error description            |
| `pending_approval`   | `args`                | Same as request              |
| `approval_decision`  | `result`              | Approval or rejection result |

Implementations SHOULD warn (via logging, not via protocol error) if more than one
content field is present, but MUST process the field corresponding to the message
intent and MUST ignore the others.

### 4.5 Message Size Limits

The default maximum size of an ARSIA message envelope, serialized as a UTF-8 JSON
string, is 1,048,576 bytes (1 MiB). This limit applies to the entire serialized
envelope, including all fields and whitespace.

Implementations MAY increase this limit to accommodate use cases that require larger
payloads (e.g., document processing, image analysis metadata). The actual maximum
message size supported by an agent MUST be advertised in the agent's discovery
metadata via the `max_message_bytes` field (§7.1).

Sending agents SHOULD check the recipient's `max_message_bytes` value before sending
messages that may approach or exceed the default limit. Receiving agents MUST reject
messages that exceed their advertised limit with error code `payload_too_large`
(§11.2).

For payloads that inherently exceed practical message size limits, implementations
SHOULD use a reference pattern: include a URL or identifier in the `args` or `result`
field that points to the large content stored externally, rather than embedding the
content directly in the message envelope.

---

## 5. Message Security

ARSIA messages are secured through digital signatures that provide authentication,
integrity, and non-repudiation. This section defines the normative procedures for
signing and verifying ARSIA messages, as well as the optional payload encryption
mechanism.

### 5.1 Digital Signatures (EdDSA)

The primary signing algorithm for ARSIA is Ed25519, an Edwards-curve Digital Signature
Algorithm (EdDSA) using Curve25519. Implementations MUST use a standards-compliant
Ed25519 implementation. The reference implementation uses the `@noble/ed25519` library
for TypeScript and equivalent verified implementations for other languages.

Message canonicalization prior to signing uses the JSON Canonicalization Scheme (JCS)
defined in [RFC 8785]. JCS produces a deterministic byte sequence from any JSON value,
ensuring that semantically identical messages produce identical signing inputs
regardless of field ordering, whitespace, or numeric representation differences in the
original serialization.

#### Signing Procedure (Normative)

The following procedure MUST be followed to produce a digital signature for an ARSIA
message:

**Step 1: Clone the message object.** Create a deep copy of the complete message
envelope as a JSON-compatible object. This copy will be modified for signing; the
original message is preserved.

**Step 2: Remove the `security` field.** Delete the `security` field from the cloned
object. If the `security` field is not present in the clone (because the message has
not yet been signed), this step is a no-op. The `security` field is excluded from the
signing input because it will contain the signature itself; including it would create
a circular dependency.

**Step 3: Canonicalize the remaining object.** Apply the JSON Canonicalization Scheme
[RFC 8785] to the modified clone. This produces a deterministic byte sequence (a
UTF-8 encoded string) that serves as the signing input. The JCS procedure:
- Serializes the JSON value with no whitespace.
- Orders object members lexicographically by their member names (Unicode code point
  order).
- Represents numbers in their shortest form per ECMAScript rules.
- Escapes string characters as required by [RFC 8785] §3.2.2.

**Step 4: Sign the canonicalized bytes.** Compute the Ed25519 signature over the
canonicalized byte sequence using the sender's Ed25519 private key. The Ed25519
algorithm produces a 64-byte signature value.

**Step 5: Encode the signature.** Encode the 64-byte signature using base64url encoding
without padding, as specified in [RFC 4648] §5. The resulting string is 86 characters
long.

**Step 6: Populate the `security` object.** Set the following fields in the message's
`security` object:
- `alg`: Set to `"EdDSA"`.
- `kid`: Set to the key identifier of the signing key, as published in the sender's
  JWKS endpoint (§7.3).
- `sig`: Set to the base64url-encoded signature string from Step 5.

#### Supported Algorithms

The ARSIA protocol supports three digital signature algorithms, with the following
conformance levels:

| Algorithm   | Identifier | Key Type     | Conformance | Notes                   |
|-------------|-----------|--------------|-------------|--------------------------|
| Ed25519     | `EdDSA`   | OKP/Ed25519  | MUST        | Primary algorithm        |
| ECDSA P-256 | `ES256`   | EC/P-256     | SHOULD      | Broad ecosystem support  |
| RSA PKCS#1  | `RS256`   | RSA (≥2048)  | MAY         | Legacy interop only      |

All conformant ARSIA implementations MUST support Ed25519 signature generation and
verification. ES256 support is RECOMMENDED for interoperability with systems that have
existing ECDSA infrastructure. RS256 support is permitted only for legacy
interoperability and MUST NOT be used for new deployments unless required by external
constraints.

When ES256 is used, the signing and verification procedures are identical to those
described above except that:
- Step 4 uses ECDSA with the P-256 curve and SHA-256 hash per [RFC 7518] §3.4.
- Step 5 produces a signature of exactly 86 characters (64 bytes in the R||S fixed-length concatenation format per [RFC 7515] §A.3).
- Step 6 sets `alg` to `"ES256"`.

When RS256 is used:
- Step 4 uses RSASSA-PKCS1-v1_5 with SHA-256 per [RFC 7518] §3.3.
- The RSA key MUST be at least 2048 bits.
- Step 6 sets `alg` to `"RS256"`.

### 5.2 Signature Verification

Receiving agents MUST verify digital signatures on all messages with `intent` values
of `"request"`, `"response"`, `"pending_approval"`, and `"approval_decision"`.
Signature verification on `"event"` messages is RECOMMENDED but not required, to
accommodate high-throughput event streams where verification latency may be
prohibitive. Signature verification on `"error"` messages is RECOMMENDED.

#### Verification Procedure (Normative)

The following procedure MUST be followed to verify the digital signature of an ARSIA
message:

**Step 1: Extract the signature.** Read the `security.sig` field from the message
envelope. Decode the base64url-encoded string (without padding) to obtain the raw
signature bytes. For Ed25519, this MUST produce exactly 64 bytes. If decoding fails or
produces an unexpected length, reject the message with error code `unauthorized`.

**Step 2: Resolve the public key.** Read the `security.kid` field from the message
envelope. Resolve the corresponding public key by fetching the sender's JWKS endpoint
(§7.3) — identified by the agent identifier in the `from` field — and locating the JWK
entry whose `kid` matches `security.kid`. If the key identifier cannot be resolved
(sender's JWKS is unreachable, or no matching `kid` is found), reject the message with
error code `unauthorized`. Implementations SHOULD cache JWKS responses according to
the `Cache-Control` headers returned by the JWKS endpoint.

**Step 3: Clone and strip.** Create a deep copy of the complete message envelope and
remove the `security` field from the copy. This produces the same object that was used
as signing input by the sender.

**Step 4: Canonicalize.** Apply the JSON Canonicalization Scheme [RFC 8785] to the
modified clone, producing the canonical byte sequence.

**Step 5: Verify.** Using the public key resolved in Step 2 and the algorithm
identified by `security.alg`, verify the signature from Step 1 against the canonical
byte sequence from Step 4. For Ed25519, use the Ed25519 verify function. For ES256,
use ECDSA verify with P-256/SHA-256. For RS256, use RSASSA-PKCS1-v1_5 verify with
SHA-256.

**Step 6: Accept or reject.** If verification succeeds, proceed with message
processing. If verification fails, the receiving agent MUST reject the message with
error code `unauthorized` (§11.2). The error response SHOULD NOT include details about
why verification failed, to avoid leaking information useful to an attacker. The
implementation SHOULD log the failure with sufficient detail for operational debugging
(key ID, algorithm, sender identity).

#### Verification Caching

Implementations MAY cache the result of JWKS lookups and public key resolution to
avoid repeated network requests. Cached JWKS entries MUST be refreshed:
- When a `kid` is encountered that is not present in the cached JWKS.
- When the cached JWKS's `Cache-Control` max-age has expired.
- At least once every 24 hours, regardless of cache headers.

### 5.3 Payload Encryption (Optional)

ARSIA supports optional payload encryption for messages that carry sensitive content
requiring confidentiality beyond what TLS provides (e.g., end-to-end encryption
through compliance brokers).

When payload encryption is enabled, the `security.encrypted` field MUST be set to
`true`, and the `security.enc_alg` and `security.enc_method` fields MUST be present.

#### Encryption Procedure

When `security.encrypted` is `true`:

1. The `payload` field MUST contain a JWE Compact Serialization string [RFC 7516]
   rather than a JSON object. The JWE MUST be produced using the algorithm specified
   in `security.enc_alg` for key encryption and `security.enc_method` for content
   encryption.

2. The RECOMMENDED key encryption algorithm is `ECDH-ES` (Elliptic Curve
   Diffie-Hellman Ephemeral Static) per [RFC 7518] §4.6. The RECOMMENDED content
   encryption method is `A256GCM` (AES-256-GCM) per [RFC 7518] §5.3.

3. The recipient's public encryption key MUST be obtained from the recipient's JWKS
   endpoint (§7.3). Encryption keys are identified by `"use": "enc"` in the JWK
   entry (as opposed to `"use": "sig"` for signing keys).

4. The signing procedure (§5.1) operates on the message with the encrypted payload
   string — the signature covers the JWE string, not the plaintext payload. This
   ensures that brokers and intermediaries can verify the signature without decrypting
   the payload.

#### Decryption Procedure

Recipients receiving a message where `security.encrypted` is `true`:

1. MUST first verify the digital signature per §5.2 (on the envelope containing the
   encrypted payload string).
2. MUST then decrypt the `payload` JWE string using their private encryption key and
   the algorithm specified in `security.enc_alg` and `security.enc_method`.
3. MUST parse the decrypted plaintext as a JSON object conforming to §4.4.
4. If decryption fails, the recipient MUST reject the message with error code
   `unauthorized` (§11.2).

#### Encryption Algorithms

The following combinations are defined:

| `enc_alg`          | `enc_method`     | Conformance   | Notes                     |
|--------------------|-----------------|---------------|---------------------------|
| `ECDH-ES`         | `A256GCM`       | RECOMMENDED   | Best performance          |
| `ECDH-ES+A256KW`  | `A256GCM`       | MAY           | Multi-recipient support   |
| `RSA-OAEP-256`    | `A256GCM`       | MAY           | Legacy interop            |

#### 5.3.1 Payload Hashing Under Encryption

When `security.encrypted` is `true`, the `payload` field contains a JWE Compact
Serialization string rather than a JSON object. RFC 8785 (JSON Canonicalization
Scheme) does not apply to strings. Audit records and integrity verification MUST
use the following rules:

**`payload_hash`.** When `security.encrypted` is `true`, `payload_hash` MUST be
`SHA-256(UTF-8(payload))` where `payload` is the JWE Compact Serialization string
as it appears in the message envelope. This hash is verifiable by any party that
observes the message (sender, broker, recipient) without requiring decryption keys.
When `security.encrypted` is `false` or absent, the existing rule applies:
`payload_hash` is `SHA-256(RFC8785(payload))` where `payload` is the canonicalized
JSON object.

**`plaintext_hash`.** When `security.encrypted` is `true`, the sender SHOULD
include a `plaintext_hash` field in its audit record. The value is
`SHA-256(RFC8785(plaintext))` where `plaintext` is the unencrypted payload JSON
object before encryption. The recipient SHOULD include the same field in its audit
record after decryption. `plaintext_hash` MUST NOT be present when
`security.encrypted` is `false` or absent — in that case, `payload_hash` already
contains the hash of the plaintext.

**Dispute resolution.** In the event of a dispute over the content of an encrypted
message:

1. Both parties export their signed audit records.
2. `payload_hash` values MUST match — they prove the same ciphertext was
   transmitted and received.
3. `plaintext_hash` values, if both present and matching, prove consensus on the
   plaintext content.
4. If `plaintext_hash` values diverge, the Ed25519 signature on each audit record
   establishes which party's record is authentic, without requiring a trusted third
   party.

---

## 6. Authorization

ARSIA uses OAuth 2.0 [RFC 6749] with the client credentials grant for agent-to-agent
authorization. Access tokens are JSON Web Tokens (JWTs) [RFC 7519] that encode the
granted capabilities as scopes. This section defines the token structure, request
flow, presentation mechanism, and enforcement rules.

### 6.1 Access Token Structure

ARSIA access tokens are JWTs conforming to [RFC 7519] with the following required
claims:

| Claim   | Type    | Description                                              | Required |
|---------|---------|----------------------------------------------------------|----------|
| `iss`   | string  | Identifier of the Authorization Server that issued the token. | REQUIRED |
| `sub`   | string  | Agent identifier (§3) of the requesting agent.           | REQUIRED |
| `aud`   | string  | Agent identifier (§3) of the target agent.               | REQUIRED |
| `exp`   | number  | Expiration time (NumericDate per [RFC 7519] §2).         | REQUIRED |
| `iat`   | number  | Issued-at time (NumericDate per [RFC 7519] §2).          | REQUIRED |
| `jti`   | string  | Unique token identifier (UUID v4).                       | REQUIRED |
| `scope` | string  | Space-separated list of capability strings.               | REQUIRED |

The following claim is OPTIONAL:

| Claim   | Type    | Description                                              | Required |
|---------|---------|----------------------------------------------------------|----------|
| `cnf`   | object  | Confirmation claim for proof-of-possession per [RFC 9449]. | OPTIONAL |

The `sub` claim MUST match the `from` field of any message presented with this token.
The `aud` claim MUST match the `to` field of any message presented with this token.
The `scope` claim MUST contain, as a space-separated string, capability identifiers
that cover all capabilities listed in the `capabilities` field of any message presented
with this token.

Token lifetime SHOULD be short — a maximum of 3600 seconds (1 hour) is RECOMMENDED.
For high-risk compliance profiles, a maximum of 300 seconds (5 minutes) is
RECOMMENDED.

#### Token Signing

Access tokens MUST be signed by the Authorization Server using one of the algorithms
defined in §5.1 (EdDSA, ES256, or RS256). The Authorization Server's signing key MUST
be discoverable via a standard JWKS endpoint (e.g., `{AS_URL}/.well-known/jwks.json`).
Recipients MUST verify the token signature before extracting claims.

### 6.2 Token Request (OAuth 2.0 Client Credentials)

Agents obtain access tokens from an Authorization Server using the OAuth 2.0 client
credentials grant [RFC 6749] §4.4.

#### Request

The agent sends an HTTP POST request to the Authorization Server's token endpoint:

```http
POST /token HTTP/2
Host: as.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id=agent%3Aacme.billing
&scope=com.example.notes.read+com.example.notes.write
&audience=agent%3Acontoso.crm
```

Request parameters:

| Parameter      | Type   | Description                                         | Required |
|----------------|--------|-----------------------------------------------------|----------|
| `grant_type`   | string | MUST be `"client_credentials"`.                     | REQUIRED |
| `client_id`    | string | The requesting agent's identifier (§3). URL-encoded.| REQUIRED |
| `scope`        | string | Space-separated list of requested capabilities.      | REQUIRED |
| `audience`     | string | The target agent's identifier (§3). URL-encoded.     | REQUIRED |

Client authentication is performed using one of:
- `client_secret` parameter (for symmetric secrets).
- Mutual TLS (mTLS) client certificate per [RFC 8705].
- Private key JWT per [RFC 7523] §2.2 (RECOMMENDED for ARSIA).

#### Response

On success, the Authorization Server responds:

```http
HTTP/2 200 OK
Content-Type: application/json
Cache-Control: no-store

{
  "access_token": "eyJhbGciOiJFZERTQSIs...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "com.example.notes.read com.example.notes.write"
}
```

Response fields:

| Field          | Type   | Description                                         | Required |
|----------------|--------|-----------------------------------------------------|----------|
| `access_token` | string | The JWT access token.                               | REQUIRED |
| `token_type`   | string | MUST be `"Bearer"` or `"DPoP"`.                     | REQUIRED |
| `expires_in`   | number | Token lifetime in seconds.                          | REQUIRED |
| `scope`        | string | The granted scope (may differ from requested scope). | REQUIRED |

If the Authorization Server denies the request, it responds with an OAuth 2.0 error
per [RFC 6749] §5.2:

```http
HTTP/2 400 Bad Request
Content-Type: application/json

{
  "error": "invalid_scope",
  "error_description": "The requested capability 'com.example.admin' is not available for the target agent."
}
```

### 6.3 Token Presentation

Agents present access tokens to receiving agents via HTTP headers. Two presentation
mechanisms are supported:

#### Bearer Token (Standard)

The simplest presentation mechanism. The access token is sent in the `Authorization`
header:

```http
Authorization: Bearer eyJhbGciOiJFZERTQSIs...
```

Bearer tokens are susceptible to token theft: any party that intercepts the token can
use it. TLS 1.3 (§8.1) mitigates this risk for direct connections. However, for
high-security deployments or when tokens may traverse intermediaries, DPoP is
RECOMMENDED.

#### DPoP (Demonstrating Proof-of-Possession)

DPoP [RFC 9449] binds the access token to the sender's private key, preventing token
replay by other parties. When DPoP is used:

1. The Authorization Server issues a token with `token_type: "DPoP"` and includes a
   `cnf` claim containing the `jkt` (JWK Thumbprint) of the agent's DPoP key.

2. The agent constructs a DPoP proof JWT per [RFC 9449] §4, signed with the same key
   whose thumbprint is in the token's `cnf.jkt` claim.

3. The agent sends both headers:

```http
Authorization: DPoP eyJhbGciOiJFZERTQSIs...
DPoP: eyJ0eXAiOiJkcG9wK2p3dCIs...
```

4. The receiving agent verifies:
   - The DPoP proof JWT signature.
   - The `jkt` in the token's `cnf` claim matches the DPoP proof's signing key.
   - The `htm` and `htu` claims in the DPoP proof match the HTTP method and URL.
   - The `iat` claim is within the clock skew tolerance (±300 seconds).
   - The `jti` claim has not been seen before (replay protection).

Implementations SHOULD use DPoP for proof-of-possession security, especially when
the compliance profile requires high-risk controls.

### 6.4 Capability Enforcement

The receiving agent MUST enforce capability-based authorization for every request
message. The enforcement procedure is as follows:

1. **Extract the access token** from the `Authorization` header (§6.3).

2. **Verify the token signature** using the Authorization Server's public key.

3. **Validate standard JWT claims:**
   - `exp` MUST be in the future (with clock skew tolerance of ±300 seconds).
   - `iat` MUST be in the past (with clock skew tolerance).
   - `sub` MUST equal the message's `from` field.
   - `aud` MUST equal the message's `to` field (the receiving agent's own identifier).

4. **Extract the granted scope** from the token's `scope` claim. Parse the
   space-separated string into a set of capability strings.

5. **Compare against required capabilities.** For each capability listed in the
   message's `capabilities` array (§4.2.3), verify that the granted scope set
   contains a matching capability string. Matching is exact string comparison (no
   wildcards, no hierarchical expansion).

> **Note (informative).** This exact-match rule applies to
> the `capabilities` field in the message envelope.
> Wildcard expansion for access token scopes is defined in
> ARSIA-Actions.md §1.2 and operates at the authorization
> layer, not at message validation.

6. **Accept or reject:**
   - If all required capabilities are present in the granted scope: proceed with
     message processing.
   - If any required capability is missing: reject the message with error code
     `forbidden` (§11.2). The error response MUST include the following fields in
     `payload.error.details`:

     ```json
     {
       "required_capabilities": ["com.example.notes.read", "com.example.notes.write"],
       "provided_capabilities": ["com.example.notes.read"]
     }
     ```

     The `required_capabilities` array lists all capabilities from the message's
     `capabilities` field. The `provided_capabilities` array lists the capabilities
     that were present in the token's scope. This information helps the requesting
     agent or its operator diagnose the authorization failure.

---

## 7. Discovery

ARSIA defines a discovery mechanism that allows agents to advertise their capabilities,
security configuration, compliance support, and operational parameters. Discovery is
the foundation of interoperability: before sending a message, a sender can query the
recipient's discovery endpoints to determine supported capabilities, protocol versions,
public keys, and rate limits.

### 7.1 Discovery Endpoint

Every ARSIA-conformant agent MUST expose a discovery endpoint at the following
well-known URI:

```
GET /.well-known/arsia
```

The discovery endpoint returns an `AgentMetadata` JSON object with the following
fields:

#### Required Fields

| Field                           | Type     | Description                                    |
|---------------------------------|----------|------------------------------------------------|
| `agent_id`                      | string   | The agent's identifier (§3).                   |
| `name`                          | string   | Human-readable display name of the agent.      |
| `version`                       | string   | The agent's software version (e.g., `"2.1.0"`). |
| `protocol_version`              | string   | The ARSIA protocol version supported (e.g., `"1.0"`). |
| `inbox`                         | string   | The absolute URL of the agent's inbox endpoint (§8.1). |
| `jwks`                          | string   | The absolute URL of the agent's JWKS endpoint (§7.3). |
| `capabilities_supported`        | array    | Array of capability strings that this agent accepts. |
| `max_message_bytes`             | integer  | Maximum message size in bytes that this agent accepts. |
| `request_timeout_ms`            | integer  | Maximum time in milliseconds that this agent will spend processing a request before timing out. |
| `server_min`                    | string   | Minimum ARSIA protocol version this agent supports (e.g., `"1.0"`). |
| `server_max`                    | string   | Maximum ARSIA protocol version this agent supports (e.g., `"1.0"`). |

#### Optional Fields

| Field                           | Type     | Description                                    |
|---------------------------------|----------|------------------------------------------------|
| `features`                      | object   | Feature flags indicating optional protocol support. |
| `rate_limits`                   | object   | Rate limiting parameters.                      |
| `compliance_profiles_supported` | array    | Array of compliance profile name strings.      |

The `features` object, when present, contains:

| Field              | Type    | Default | Description                            |
|--------------------|---------|---------|----------------------------------------|
| `async_responses`  | boolean | `false` | Whether the agent supports asynchronous responses (HTTP 202). |
| `batch_requests`   | boolean | `false` | Whether the agent supports batch request processing. |
| `encryption`       | boolean | `false` | Whether the agent supports payload encryption (§5.3). |

The `rate_limits` object, when present, contains:

| Field                | Type    | Description                                    |
|----------------------|---------|------------------------------------------------|
| `requests_per_minute`| integer | Maximum number of requests accepted per minute. |
| `burst_size`         | integer | Maximum number of requests accepted in a burst. |

The `compliance_profiles_supported` array lists the names of compliance profiles that
this agent can apply when processing messages. Example: `["EU-AI-ACT-HIGH-RISK",
"MIFID-II"]`.

#### Response Headers

The discovery endpoint SHOULD set the following HTTP response headers:

- **`Cache-Control`**: Implementations SHOULD set a `max-age` directive appropriate
  for the rate of change of the agent's metadata. A value of `max-age=3600` (1 hour)
  is RECOMMENDED.

- **`ETag`**: Implementations SHOULD set an `ETag` header to enable conditional
  requests. Clients SHOULD use `If-None-Match` to avoid unnecessary data transfer.

- **`Content-Type`**: MUST be `application/json`.

- **`Access-Control-Allow-Origin`**: Implementations SHOULD set this header to enable
  discovery from browser-based agents. A value of `"*"` is acceptable for public
  agents; restricted agents SHOULD list specific origins.

#### Example Discovery Response

```json
{
  "agent_id": "agent:acme.billing",
  "name": "Acme Billing Service",
  "version": "2.1.0",
  "protocol_version": "1.0",
  "inbox": "https://billing.acme.example/v1/arsia/inbox",
  "jwks": "https://billing.acme.example/.well-known/arsia/jwks.json",
  "capabilities_supported": [
    "com.acme.billing.invoice.create",
    "com.acme.billing.invoice.get",
    "com.acme.billing.invoices.list"
  ],
  "features": {
    "async_responses": true,
    "batch_requests": false,
    "encryption": true
  },
  "rate_limits": {
    "requests_per_minute": 120,
    "burst_size": 20
  },
  "max_message_bytes": 1048576,
  "request_timeout_ms": 30000,
  "compliance_profiles_supported": [
    "EU-AI-ACT-HIGH-RISK",
    "MIFID-II"
  ],
  "server_min": "1.0",
  "server_max": "1.0"
}
```

### 7.2 Capability Discovery

ARSIA-conformant agents SHOULD expose a capability discovery endpoint that provides
detailed information about each supported capability:

```
GET /.well-known/arsia/capabilities
```

The response is a JSON array of capability descriptor objects. Each object contains:

| Field                       | Type    | Description                                | Required |
|-----------------------------|---------|--------------------------------------------|----------|
| `capability`                | string  | The capability identifier string.          | REQUIRED |
| `description`               | string  | Human-readable description of the capability. | REQUIRED |
| `risk_level`                | integer | Risk level from 0 (no risk) to 10 (critical). | REQUIRED |
| `rate_limit`                | integer | Per-capability rate limit (requests/minute). | OPTIONAL |
| `requires`                  | array   | Array of prerequisite capability strings.  | OPTIONAL |
| `human_oversight_required`  | boolean | Whether human approval is required.        | REQUIRED |

The `risk_level` field provides a standardised indication of the risk associated with
invoking this capability. Risk levels inform compliance decisions:

| Range | Classification | Examples                                    |
|-------|---------------|---------------------------------------------|
| 0-2   | Low           | Read-only queries, echo, health checks      |
| 3-5   | Medium        | Data modification, configuration changes    |
| 6-8   | High          | Financial transactions, PII processing      |
| 9-10  | Critical      | System administration, irreversible actions |

The `requires` field, when present, lists capabilities that MUST also be present in
the request's `capabilities` array when this capability is invoked. For example, a
`com.acme.billing.refund` capability might require `com.acme.billing.invoice.get` as a
prerequisite.

The `human_oversight_required` field indicates whether the receiving agent will
require human approval (via `pending_approval` / `approval_decision` intents) before
executing this capability, regardless of the compliance profile. When `true`, the
sending agent SHOULD be prepared to handle a `pending_approval` response.

#### Example Capability Discovery Response

```json
[
  {
    "capability": "com.acme.billing.invoice.create",
    "description": "Create a new invoice for a customer account.",
    "risk_level": 6,
    "rate_limit": 30,
    "requires": [],
    "human_oversight_required": false
  },
  {
    "capability": "com.acme.billing.refund",
    "description": "Process a refund for an existing invoice.",
    "risk_level": 8,
    "rate_limit": 10,
    "requires": ["com.acme.billing.invoice.get"],
    "human_oversight_required": true
  }
]
```

### 7.3 JWKS Endpoint

Every ARSIA-conformant agent MUST expose a JSON Web Key Set (JWKS) endpoint that
publishes the agent's public keys for signature verification:

```
GET /.well-known/arsia/jwks.json
```

The response is a JWK Set per [RFC 7517], containing one or more JWK entries.

#### Ed25519 Key Format

Each Ed25519 public key is represented as a JWK with the following fields:

| Field | Type   | Value                                          | Required |
|-------|--------|------------------------------------------------|----------|
| `kty` | string | `"OKP"` (Octet Key Pair)                       | REQUIRED |
| `crv` | string | `"Ed25519"`                                    | REQUIRED |
| `kid` | string | Key identifier, unique within this JWKS.       | REQUIRED |
| `x`   | string | Base64url-encoded 32-byte public key (no padding). | REQUIRED |
| `use` | string | `"sig"` for signing keys.                      | REQUIRED |

The `kid` (key identifier) MUST follow the pattern `{agent-id}#{keyN}`,
where `{agent-id}` is the agent's full identifier (§3) and `{keyN}` is a sequential
key label. For example:

```
agent:acme.billing#key1
agent:acme.billing#key2
```

This format ensures that key identifiers are globally unique and can be unambiguously
resolved to the owning agent.

#### EC Key Format (for ES256)

Each P-256 public key is represented as a JWK with:

| Field | Type   | Value                                          | Required |
|-------|--------|------------------------------------------------|----------|
| `kty` | string | `"EC"`                                         | REQUIRED |
| `crv` | string | `"P-256"`                                      | REQUIRED |
| `kid` | string | Key identifier.                                | REQUIRED |
| `x`   | string | Base64url-encoded x-coordinate.                | REQUIRED |
| `y`   | string | Base64url-encoded y-coordinate.                | REQUIRED |
| `use` | string | `"sig"` for signing keys.                      | REQUIRED |

#### Encryption Keys

Agents that support payload encryption (§5.3) MUST also publish their encryption
public keys in the JWKS with `"use": "enc"`:

| Field | Type   | Value                                          |
|-------|--------|------------------------------------------------|
| `kty` | string | `"OKP"` or `"EC"` depending on algorithm.     |
| `crv` | string | `"X25519"` for ECDH-ES with Curve25519, or `"P-256"`. |
| `kid` | string | Key identifier (distinct from signing keys).   |
| `x`   | string | Base64url-encoded public key material.         |
| `use` | string | `"enc"` for encryption keys.                  |

#### Key Rotation

Agents MUST support key rotation to limit the impact of key compromise. The following
rules govern key rotation:

1. When rotating keys, the agent MUST publish both the old and new signing keys in
   the JWKS simultaneously for a minimum overlap period of **24 hours**. This ensures
   that messages signed with the old key can still be verified during the transition.

2. After the overlap period, the old key MAY be removed from the JWKS. Messages
   signed with a removed key that arrive after removal will fail verification and
   be rejected.

3. Agents SHOULD generate new signing keys at least every 90 days, even if no
   compromise is suspected.

4. If a key compromise is detected, the compromised key MUST be removed from the
   JWKS immediately (overriding the 24-hour overlap). All tokens and signatures
   produced with the compromised key MUST be considered invalid.

5. The JWKS endpoint SHOULD set `Cache-Control: max-age=3600` to balance freshness
   with caching efficiency. In the event of emergency key rotation, implementations
   SHOULD reduce the max-age temporarily.

#### Example JWKS Response

```json
{
  "keys": [
    {
      "kty": "OKP",
      "crv": "Ed25519",
      "kid": "agent:acme.billing#key1",
      "x": "11qYAYKxCrfVS_7TyWQHOg7hcvPapiMlrwIaaPcHURo",
      "use": "sig"
    },
    {
      "kty": "OKP",
      "crv": "Ed25519",
      "kid": "agent:acme.billing#key2",
      "x": "VTt6kGWJSIWhmR2xJP3HKjfMbNKz7GGretzJ7EQgYzs",
      "use": "sig"
    },
    {
      "kty": "OKP",
      "crv": "X25519",
      "kid": "agent:acme.billing#enc1",
      "x": "Knbm_BcdQr7WIoz-uqit7MlYDw6lSacs-eEhSC4_oeM",
      "use": "enc"
    }
  ]
}
```

### 7.4 Version Negotiation

ARSIA supports version negotiation between agents that may support different protocol
versions. The negotiation mechanism uses the `v` and `min_v` fields in the message
envelope and the `server_min` and `server_max` fields in the discovery response.

#### Negotiation Procedure

1. **Sender preparation.** The sending agent sets:
   - `v`: The protocol version used to construct this message (the sender's preferred
     version).
   - `min_v` (optional): The minimum protocol version the sender is willing to accept
     in a response.

2. **Recipient validation.** The receiving agent checks:
   - `v` against its own supported range (`server_min` through `server_max`).
   - If `min_v` is present, checks that its own `server_max` ≥ `min_v`.

3. **Negotiation succeeds** if and only if both conditions hold:
   - `server_min` ≤ `v` (the recipient supports the sender's version or an earlier
     version in the same range).
   - `min_v` ≤ `server_max` (the recipient's maximum version meets the sender's
     minimum requirement). If `min_v` is absent, this condition is trivially
     satisfied.

4. **Negotiation fails** if either condition is violated. The recipient MUST respond
   with error code `not_implemented` (§11.2) and MUST include the following fields in
   `payload.error.details`:

   ```json
   {
     "supported_versions": {
       "min": "1.0",
       "max": "1.0"
     },
     "requested_version": "2.0",
     "requested_min_version": "1.5"
   }
   ```

#### Backward Compatibility Rules

- Agents MUST accept messages with `v` values within their supported range, even if
  the message contains fields they do not recognise (which were introduced in a later
  minor version). Unknown fields MUST be preserved if the message is forwarded (e.g.,
  by a broker) and SHOULD be ignored during processing.

- Agents MUST NOT send messages with a `v` value higher than the recipient's
  `server_max`, as determined from the discovery endpoint (§7.1). Senders SHOULD
  query the recipient's discovery endpoint before first contact and cache the result.

---

## 8. Transport Bindings

ARSIA is transport-agnostic: the message envelope and all protocol semantics defined
in this specification are independent of the underlying transport mechanism. This
section defines normative bindings for two transports: HTTP/2 (REQUIRED) and WebSocket
(OPTIONAL).

Implementations MAY define additional transport bindings (e.g., gRPC, MQTT, AMQP) as
long as the bindings preserve the full ARSIA message envelope without modification and
enforce the security requirements defined in §5 and §6.

### 8.1 HTTP/2 (REQUIRED)

The HTTP/2 transport binding is the primary transport for ARSIA and MUST be supported
by all conformant implementations.

#### Request

Messages are delivered to the recipient's inbox via HTTP POST:

```http
POST /v1/arsia/inbox HTTP/2
Host: billing.acme.example
Content-Type: application/arsia+json; v=1
Authorization: Bearer eyJhbGciOiJFZERTQSIs...
Idempotency-Key: acme-billing-inv-20260324-001
X-Request-Priority: 7

{ARSIA message envelope as JSON body}
```

**Method:** POST. All message deliveries use POST, regardless of the message intent.

**Path:** `/v1/arsia/inbox`. This is the canonical inbox path. The complete inbox URL
is advertised in the discovery metadata (§7.1). The path includes a version prefix
(`/v1/`) to support future incompatible path changes.

**Content-Type:** `application/arsia+json; v=1`. The media type is
`application/arsia+json` (§14.1) with a required `v` parameter indicating the major
protocol version. Implementations MUST reject requests with an unsupported Content-Type
with HTTP status 415 (Unsupported Media Type).

**Authorization:** Per §6.3. Either `Bearer {token}` or `DPoP {token}` with an
accompanying `DPoP` header.

**Optional Headers:**

| Header               | Type    | Description                                    |
|----------------------|---------|------------------------------------------------|
| `Idempotency-Key`   | string  | Idempotency key (§10). 1-128 characters.       |
| `X-Request-Priority` | integer | Message processing priority, 0-10.             |

> **Note (informative).** When both the `X-Request-Priority` header and the
> `context.priority` envelope field are present, the header value takes precedence.
> See ARSIA-Routing.md §6.3 for the full precedence rule.

#### Response — Synchronous

When the receiving agent processes the request synchronously:

```http
HTTP/2 200 OK
Content-Type: application/arsia+json; v=1

{ARSIA response envelope as JSON body}
```

The response body MUST be a valid ARSIA message envelope with `intent` set to
`"response"`, `"error"`, or `"pending_approval"`, and `correlation_id` set to the
`id` of the request message.

#### Response — Asynchronous

When the receiving agent cannot complete processing within the request timeout but
accepts the message for asynchronous processing:

```http
HTTP/2 202 Accepted
Location: https://billing.acme.example/v1/arsia/status/550e8400-e29b-41d4-a716-446655440000
Retry-After: 5
```

The `Location` header provides a URL where the sender can poll for the eventual
response. The `Retry-After` header indicates the suggested interval (in seconds)
between polling attempts.

The status endpoint MUST return:
- HTTP 202 if processing is still in progress.
- HTTP 200 with the ARSIA response envelope if processing is complete.
- HTTP 410 (Gone) if the status resource has expired.

#### TLS Requirements

All ARSIA HTTP connections MUST use TLS 1.3 [RFC 8446] or later. TLS 1.2 MAY be
accepted as a fallback, but TLS 1.3 MUST be preferred.

HTTP Strict Transport Security (HSTS) [RFC 6797] is RECOMMENDED. When HSTS is enabled,
the `Strict-Transport-Security` header SHOULD include `max-age=31536000` (1 year) and
`includeSubDomains`.

Implementations MUST NOT accept plaintext HTTP connections for any ARSIA endpoint.

### 8.2 WebSocket (OPTIONAL)

The WebSocket transport binding provides a persistent bidirectional channel for
agents that exchange high-frequency messages or require real-time event streaming.

#### Connection Endpoint

```
wss://host/v1/arsia/stream
```

The WebSocket connection MUST use the `wss://` scheme (TLS-encrypted). Plaintext
`ws://` connections MUST NOT be used.

The WebSocket sub-protocol MUST be declared during the HTTP upgrade handshake:

```http
GET /v1/arsia/stream HTTP/1.1
Host: billing.acme.example
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Protocol: arsia-v1
Sec-WebSocket-Version: 13
```

The server MUST respond with the selected sub-protocol:

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Protocol: arsia-v1
```

#### Authentication Handshake

After the WebSocket connection is established, the client MUST authenticate before
sending any ARSIA messages:

**Step 1:** Client sends an authentication frame:

```json
{
  "type": "auth",
  "token": "Bearer eyJhbGciOiJFZERTQSIs..."
}
```

The `token` field contains the full Authorization header value (including the scheme
prefix).

**Step 2:** Server validates the token and responds:

On success:

```json
{
  "type": "auth_ok",
  "agent_id": "agent:acme.billing"
}
```

On failure:

```json
{
  "type": "auth_error",
  "code": "unauthorized",
  "description": "Invalid or expired access token."
}
```

If authentication fails, the server MUST close the WebSocket connection with close
code 4001 (Authentication Failed) within 5 seconds of sending the `auth_error` frame.

**Step 3:** After successful authentication, both sides may send ARSIA message
envelopes as JSON text frames. Binary frames MUST NOT be used for ARSIA messages.

#### Heartbeat

The client MUST send a heartbeat frame every 30 seconds to maintain the connection:

```json
{
  "type": "ping"
}
```

The server MUST respond within 5 seconds:

```json
{
  "type": "pong"
}
```

If the server does not receive a ping within 60 seconds, it SHOULD close the
connection with close code 4002 (Idle Timeout). If the client does not receive a pong
within 10 seconds of sending a ping, it SHOULD close the connection and initiate
reconnection.

#### Reconnection

When a WebSocket connection is lost, the client SHOULD attempt to reconnect using
exponential backoff:

| Attempt | Delay     |
|---------|-----------|
| 1       | 1 second  |
| 2       | 2 seconds |
| 3       | 4 seconds |
| 4       | 8 seconds |
| 5       | 16 seconds|
| 6+      | 30 seconds|

The maximum delay between reconnection attempts is 30 seconds. Jitter of ±25% of the
delay value is RECOMMENDED to avoid thundering herd effects when many clients reconnect
simultaneously.

Upon reconnection, the client MUST re-authenticate (Step 1 above). The server MUST NOT
assume that a reconnected client has the same authentication state as a previous
connection.

#### Frame Size

The maximum WebSocket frame size for ARSIA messages is governed by the agent's
`max_message_bytes` value (§4.5). Frames exceeding this limit MUST cause the server to
close the connection with close code 4003 (Message Too Large).

#### Idempotency over WebSocket

The `Idempotency-Key` HTTP header (§10.1) is not available over WebSocket
connections. Agents sending messages over WebSocket MUST use the `idempotency.key`
envelope field (§4.3.2) as the sole mechanism for providing idempotency keys. The
header-vs-envelope precedence rule (§10.4) does not apply to WebSocket transport —
the envelope field is authoritative.

All other idempotency requirements (§10.2, §10.3) apply to WebSocket transport with
the following adaptation: for duplicate detection (§10.3), the server MUST return the
previously stored response envelope as a JSON text frame. The HTTP status code
requirement in §10.3 applies only to HTTP transport.

### 8.3 Request/Response Timing

This section defines the timing parameters that govern ARSIA message exchange.

#### Request Timeout

The default request timeout is **30,000 milliseconds (30 seconds)**. This is the
maximum time a sending agent should wait for a synchronous response before considering
the request failed.

Each agent advertises its actual request timeout via the `request_timeout_ms` field in
the discovery metadata (§7.1). Sending agents SHOULD respect the recipient's advertised
timeout and set their client-side timeout accordingly.

If a synchronous response is not received within the timeout period:
- The sending agent SHOULD treat the request as failed.
- The sending agent SHOULD NOT retry immediately (see §11.3 for retry policy).
- If the agent supports asynchronous responses (§8.1), it MAY check the status URL
  if one was provided.

#### WebSocket Idle Timeout

WebSocket connections that have not exchanged any frames (including heartbeats) for
**60 seconds** are considered idle and SHOULD be closed by the server.

#### Clock Skew Tolerance

ARSIA allows a default clock skew tolerance of **±300 seconds (5 minutes)** for all
timestamp validation. When the applicable compliance profile defines a
`clock_skew_seconds` value, that value MUST be used instead. The profile value MUST NOT
exceed 300 seconds — compliance profiles can only tighten the tolerance, never loosen
it. This tolerance applies to:

- The `ts` field (§4.1.3): A message with a `ts` that differs from the recipient's
  current time by more than 300 seconds MAY be rejected.
- The `expires_at` field (§4.2.2): A message is considered expired when the
  recipient's current time exceeds `expires_at` + 300 seconds.
- Access token `exp` and `iat` claims (§6.1): Token validation applies the same
  ±300-second tolerance.

When a compliance profile specifies `clock_skew_seconds`, the profile-specific tolerance
replaces the 300-second default for all timestamp validation listed above. For example, a
message processed under the MIFID-II profile with `clock_skew_seconds: 60` uses ±60
seconds for `ts` validation, `expires_at` expiration, and access token `exp`/`iat`
claims. Messages without a compliance profile or with a profile that omits
`clock_skew_seconds` use the default ±300-second tolerance.

Implementations SHOULD synchronise their system clocks using NTP or an equivalent
time synchronisation protocol. Agents operating in compliance-sensitive environments
SHOULD use multiple NTP sources and SHOULD log clock drift exceeding 10 seconds.

---

## 9. Routing and Brokers

ARSIA supports multiple routing topologies to accommodate different deployment
scenarios. This section defines the routing modes, broker requirements, and the
algorithm for selecting the appropriate topology.

### 9.1 Direct Routing

Direct routing is the default and simplest routing mode. In direct routing, Agent A
sends a message directly to Agent B's inbox endpoint via HTTP POST (§8.1). No
intermediary is involved.

```
+---------+    POST /v1/arsia/inbox      +---------+
| Agent A | ---------------------------> | Agent B |
+---------+                              +---------+
```

Direct routing MUST be sufficient for Core conformance (§12.1). An agent that
supports only direct routing and meets all other Core conformance requirements is a
valid ARSIA implementation.

Direct routing requirements:

1. The sending agent MUST resolve the recipient's inbox URL from the discovery
   endpoint (§7.1).

2. The sending agent MUST present a valid access token (§6.3) with the request.

3. The sending agent MUST sign the message (§5.1).

4. The receiving agent MUST verify the signature (§5.2), validate the access token
   (§6.4), and process the message.

5. The receiving agent MUST return a response synchronously (HTTP 200) or indicate
   asynchronous processing (HTTP 202).

### 9.2 Brokered Routing

Brokered routing introduces a Compliance Broker as an intermediary between the sending
and receiving agents. Brokers are used to enforce data residency constraints.

**Decision [CONFIRMED]:** Compliance brokers are OPTIONAL in the ARSIA protocol. They
are REQUIRED only when the `compliance.data_residency` field is set in the message
envelope.

```
+---------+    POST    +----------------+    POST    +---------+
| Agent A  | --------> |   Compliance   | -------->  | Agent B  |
|          |           |     Broker     |            |          |
+---------+            |  (EU zone)     |            +---------+
                       +----------------+
```

When a message envelope contains a `compliance.data_residency` value:

1. **Mandatory broker routing.** The sending agent MUST route the message through a
   Compliance Broker whose physical servers reside entirely within the declared
   residency zone. The sending agent MUST NOT send the message directly to the
   recipient, even if direct connectivity is available.

2. **Broker capability.** A Compliance Broker is an ARSIA-conformant agent that
   declares the capability `arsiaprotocol.broker.relay` in its discovery metadata (§7.1). The
   `arsiaprotocol.broker.relay` capability indicates that the agent is authorised to receive
   messages destined for other agents and relay them to the final recipient.

3. **Envelope integrity.** Brokers MUST NOT modify the contents of the message
   envelope in any way. The message forwarded by the broker to the recipient MUST be
   byte-identical to the message received from the sender (after JSON
   canonicalization). This ensures that the sender's digital signature remains valid
   end-to-end — the recipient verifies the signature against the sender's public key,
   not the broker's.

4. **Audit obligation.** Brokers MUST append an audit record for every message they
   relay. The audit record MUST include at minimum: the message `id`, `from`, `to`,
   `ts`, the broker's own agent identifier, the relay timestamp, and the data
   residency zone. The audit record format is defined in ARSIA-State.md §7.

5. **Broker discovery.** Sending agents discover available brokers by querying:

   ```
   GET /.well-known/arsia/brokers?residency={zone}
   ```

   This endpoint MAY be hosted by any ARSIA infrastructure service (e.g., a central
   registry, the sender's own organisation, or a third-party broker directory). The
   response is a JSON array of `BrokerEntry` objects (ARSIA-Routing.md §7.2):

   ```json
   [
     {
       "agent_id": "agent:arsialabs.broker.eu-west",
       "inbox": "https://eu-west.broker.arsiaprotocol.org/v1/arsia/inbox",
       "jurisdiction": "IE",
       "residency_zones": ["EU"],
       "capacity": {
         "requests_per_minute": 10000,
         "current_load_pct": 42
       },
       "health": "healthy",
       "last_health_check": "2026-03-24T10:00:00.000Z"
     }
   ]
   ```

6. **No broker available.** If the sending agent cannot discover a Compliance Broker
   for the required residency zone, it MUST NOT send the message. Instead, the sending
   agent MUST return an error to its caller with error code `service_unavailable`
   (§11.2) and the following details:

   ```json
   {
     "data_residency_violation": true,
     "required_zone": "EU",
     "message": "No compliant broker available for the required data residency zone."
   }
   ```

   This is a hard requirement: violating data residency by sending the message through
   an alternative route is not permitted.

### 9.3 Routing Topology

ARSIA defines three routing topologies:

#### Direct Topology

```
A -> B
```

The default topology. Agent A sends directly to Agent B. No intermediary. Available for
all messages that do not declare a `compliance.data_residency` constraint.

#### Brokered Topology

```
A -> Broker -> B
```

Required when `compliance.data_residency` is set. Agent A sends to a Compliance Broker
within the declared residency zone, and the Broker forwards to Agent B. The Broker MUST
reside within the residency zone.

#### Federated Topology

```
A -> Local Broker -> Cross-Org Broker -> B
```

A multi-hop topology for cross-organisational communication where both organisations
operate their own broker infrastructure. The federated topology is OPTIONAL and is
**out of scope for ARSIA v1.0**. Future versions of this specification may define the
federated topology in ARSIA-Routing.md.

### 9.4 Topology Determination Procedure

The following algorithm is normative. Sending agents MUST implement this logic (or
equivalent) when determining how to route a message:

```
function selectTopology(message):
    // Check if data residency is required
    if message.compliance is present
       AND message.compliance.data_residency is present
       AND message.compliance.data_residency is not empty:

        zone = message.compliance.data_residency

        // Attempt to discover a compliant broker
        broker = discoverBroker(zone)

        if broker is null:
            // No compliant broker available — MUST NOT send
            return ERROR(
                code: "service_unavailable",
                details: {
                    data_residency_violation: true,
                    required_zone: zone
                }
            )

        // Route through the discovered broker
        return BROKERED(broker)

    else:
        // No data residency constraint — direct routing
        return DIRECT
```

The `discoverBroker(zone)` function queries the broker discovery endpoint (§9.2,
step 5) and returns the first available broker in the specified zone, or `null` if
none is found. Implementations MAY implement more sophisticated broker selection
strategies (e.g., load balancing, latency-based selection, failover) as long as the
selected broker resides within the required zone.

---

## 10. Idempotency

Idempotency ensures that duplicate message deliveries — caused by network retries,
client timeouts, or infrastructure failures — do not result in duplicate processing.
ARSIA defines an idempotency mechanism based on unique keys that scope duplicate
detection to a specific sender-recipient-payload tuple.

### 10.1 Idempotency Key Semantics

An idempotency key is a string between 1 and 128 characters in length (inclusive). The
key MUST be unique within the scope of the tuple (`from`, `to`, `payload.type`). That
is, the same idempotency key value may be used by different senders, for different
recipients, or for different payload types without conflict.

The idempotency key MAY contain any printable ASCII character (code points 0x20
through 0x7E). Implementations SHOULD use identifiers that are meaningful to the
sender's domain — for example, an invoice number, a transaction reference, or a UUID.

Idempotency keys may be provided in two locations:

1. **Envelope field:** The `idempotency.key` field within the message envelope
   (§4.3.2).
2. **HTTP header:** The `Idempotency-Key` header in the HTTP request (§8.1).

> **Note:** The HTTP header mechanism is available only over HTTP transport (§8.1).
> Over WebSocket transport (§8.2), the envelope field is the only available mechanism.
> See §8.2 for transport-specific idempotency rules.

### 10.2 Server-Side Storage Requirements

Receiving agents that support idempotency — which is REQUIRED for Core conformance
(§12.1) — MUST implement the following storage behaviour:

1. When a message with an idempotency key is received and processed successfully, the
   server MUST store the association between the idempotency key (scoped to the
   `from`, `to`, `payload.type` tuple) and the complete response envelope.

2. The stored association MUST be retained for the duration specified by
   `idempotency.expires_at` (§4.3.2). If the idempotency key is provided only via
   the HTTP header (without a corresponding envelope field), the server MUST retain
   the association for a minimum of 24 hours.

3. The storage mechanism is implementation-defined. Options include in-memory caches,
   database tables, or distributed key-value stores. The storage MUST survive server
   restarts within the retention window for production deployments.

4. After the retention window expires, the server MAY delete the stored association.
   A subsequent request with the same key after expiry is treated as a new request.

### 10.3 Duplicate Detection Behaviour

When a server receives a message with an idempotency key that matches an existing
stored association (same key, same `from`, same `to`, same `payload.type`):

1. The server MUST return the previously stored response without re-executing the
   request.

2. The HTTP status code of the duplicate response MUST be identical to the original
   response (HTTP transport only — over WebSocket, the stored response envelope is
   returned as a JSON text frame; see §8.2).

3. The response body MUST be the exact ARSIA envelope that was stored when the
   original request was processed.

4. If the original request is still being processed (i.e., the server has received the
   key but has not yet produced a response), the server SHOULD return HTTP 409
   (Conflict) with error code `conflict` and a `Retry-After` header suggesting when
   to retry.

### 10.4 Header vs. Envelope Precedence (HTTP Transport)

When both the HTTP header `Idempotency-Key` and the envelope field `idempotency.key`
are present in the same request:

1. The HTTP header value takes precedence for duplicate detection purposes.

2. If the header value and envelope value differ, the server MUST use the header value
   and SHOULD log the discrepancy for operational monitoring.

3. The `idempotency.expires_at` field from the envelope is used as the retention
   duration regardless of which key source is used for detection.

> **Note:** This section applies only to HTTP transport (§8.1). Over WebSocket
> transport (§8.2), the `Idempotency-Key` header is not available and the envelope
> field is authoritative.

---

## 11. Error Handling

ARSIA defines a structured error handling framework that provides consistent error
semantics across all implementations. This section specifies the error response format,
the standard error code registry, and the retry policy for transient failures.

### 11.1 Error Response Format

An ARSIA error response is a message envelope with the following characteristics:

- **`intent`**: MUST be `"error"`.
- **`correlation_id`**: MUST be set to the `id` of the original message that caused
  the error (§4.2.1).
- **`from`**: The agent identifier of the agent reporting the error.
- **`to`**: The agent identifier of the agent that sent the original message.
- **`payload.type`**: SHOULD be the same as the original message's `payload.type`, or
  `"arsiaprotocol.error"` if the original type is unknown or unparseable.
- **`payload.error`**: MUST be present and MUST conform to §4.4.6.

The `payload.error` object contains:

| Field         | Type   | Description                                    | Required |
|---------------|--------|------------------------------------------------|----------|
| `code`        | string | One of the standard error codes (§11.2).       | REQUIRED |
| `description` | string | Human-readable error description.              | REQUIRED |
| `details`     | object | Structured error context (varies by code).     | OPTIONAL |

The `description` field is intended for developers and operators. It MUST be written
in English. It MUST NOT contain sensitive information such as internal implementation
details, stack traces, database queries, file system paths, or credentials.

The `details` field provides machine-readable context that helps the sender diagnose
and resolve the error. The content of `details` varies by error code; specific
requirements are noted in §11.2 below.

### 11.1.1 Scope of Error Envelopes

The error envelope format defined in §11.1 applies to protocol-level errors exchanged
between ARSIA agents. HTTP transport-level errors returned by gateways and servers (such
as 401 Unauthorized or 403 Forbidden) MAY use plain JSON responses with appropriate HTTP
status codes and headers (e.g., `WWW-Authenticate` per RFC 6750 for 401 responses).
These transport-level responses are not ARSIA protocol messages and are not subject to
the envelope signing requirement.

Implementations SHOULD include a machine-readable error body with at minimum: a `status`
field and a human-readable `reason` field.

### 11.2 Standard Error Codes

The following error codes are defined by the ARSIA protocol. Implementations MUST use
these codes for the described conditions. Implementations MAY define additional
application-specific error codes using the reverse domain notation (e.g.,
`com.example.insufficient-funds`), but MUST NOT redefine the meaning of standard codes.

> **Naming conventions.** Standard ARSIA error codes use `snake_case` (e.g.,
> `invalid_request`). Custom application-specific codes use reverse domain notation with
> dot separators and hyphens (e.g., `com.example.insufficient-funds`). This distinction
> ensures that custom codes are visually and syntactically distinct from standard codes
> and cannot collide with future standard code additions.

| Code                  | HTTP Status | Description                                 | Retryable |
|-----------------------|-------------|---------------------------------------------|-----------|
| `invalid_request`     | 400         | The message envelope is malformed, missing required fields, or contains values that violate the constraints defined in §4. | No |
| `unauthorized`        | 401         | The access token is missing, expired, malformed, or the digital signature verification failed. | No |
| `forbidden`           | 403         | The access token is valid but does not include sufficient capabilities for the requested action. | No |
| `not_found`           | 404         | The target agent or the requested resource does not exist. | No |
| `conflict`            | 409         | The idempotency key collides with an in-progress request, or a state conflict prevents processing. | No † |
| `payload_too_large`   | 413         | The message exceeds the recipient's `max_message_bytes` limit (§4.5). | No |
| `rate_limited`        | 429         | The sender has exceeded the recipient's rate limit. | Yes |
| `internal_error`      | 500         | An unexpected error occurred during message processing. | Yes |
| `not_implemented`     | 501         | The requested feature, capability, payload type, or protocol version is not supported by the recipient. | No |
| `service_unavailable` | 503         | The recipient is temporarily unable to process requests (maintenance, overload, dependency failure). | Yes |

† See §11.3 exception for idempotent in-progress signals.

#### Error-Specific Detail Requirements

The following error codes have specific requirements for the `details` object:

**`forbidden`:** The `details` object MUST include:
```json
{
  "required_capabilities": ["cap.one", "cap.two"],
  "provided_capabilities": ["cap.one"]
}
```

**`not_implemented`:** The `details` object MUST include:
```json
{
  "supported_versions": {
    "min": "1.0",
    "max": "1.0"
  }
}
```
When the error is due to an unsupported payload type, `details` SHOULD also include:
```json
{
  "unsupported_type": "com.example.unknown/action"
}
```

**`rate_limited`:** The `details` object SHOULD include:
```json
{
  "retry_after_seconds": 30,
  "limit": 120,
  "remaining": 0,
  "reset_at": "2026-03-24T14:31:00.000Z"
}
```

**`payload_too_large`:** The `details` object SHOULD include:
```json
{
  "max_message_bytes": 1048576,
  "actual_bytes": 2097152
}
```

**`service_unavailable`:** When caused by a data residency violation (§9.2), the
`details` object MUST include:
```json
{
  "data_residency_violation": true,
  "required_zone": "EU"
}
```

### 11.3 Retry Policy

This section defines the normative retry behaviour for ARSIA agents when requests
fail.

#### Non-Retryable Errors (4xx except 429)

Errors with codes `invalid_request`, `unauthorized`, `forbidden`, `not_found`,
`conflict`, `payload_too_large`, and `not_implemented` indicate a problem with the
request itself. Retrying the identical request will produce the same error. Sending
agents MUST NOT retry requests that receive these error codes without modifying the
request to address the reported issue.

Exception: when a `conflict` error response includes a `Retry-After` header indicating
that an idempotent request is still in-progress (§10.3), the sending agent SHOULD retry
the identical request after the indicated delay, as the original request has not been
rejected.

#### Rate-Limited Errors (429)

When a `rate_limited` error is received:

1. The sending agent MUST NOT retry immediately.
2. If the HTTP response includes a `Retry-After` header, the sending agent MUST wait
   at least the specified number of seconds before retrying.
3. If `payload.error.details.retry_after_seconds` is present, the sending agent SHOULD
   use this value if no `Retry-After` header is present.
4. If neither value is available, the sending agent SHOULD wait at least 60 seconds.

#### Server Errors (5xx)

When an `internal_error` or `service_unavailable` error is received, the sending agent
SHOULD retry using exponential backoff:

| Parameter     | Value                      |
|---------------|----------------------------|
| Base delay    | 1 second                   |
| Multiplier    | 2x                         |
| Maximum delay | 32 seconds                 |
| Maximum retries | 3                        |
| Jitter        | RECOMMENDED: ±25% of delay |

The retry schedule is:

| Retry | Delay (without jitter) | Delay (with ±25% jitter)  |
|-------|----------------------|---------------------------|
| 1     | 1 second             | 0.75 – 1.25 seconds      |
| 2     | 2 seconds            | 1.50 – 2.50 seconds      |
| 3     | 4 seconds            | 3.00 – 5.00 seconds      |

After 3 failed retries, the sending agent MUST abandon the request and report the
failure to its caller. The failure report SHOULD include the error code and description
from the most recent attempt.

Jitter is RECOMMENDED to prevent synchronized retries from multiple agents
overwhelming a recovering server (thundering herd effect). Implementations SHOULD use
uniform random jitter: `actual_delay = base_delay * (0.75 + random() * 0.5)`.

---

## 12. Conformance Levels

ARSIA defines three conformance levels that allow implementations to progressively
adopt protocol features. Each level builds upon the previous one.

### 12.1 Core Conformance

An ARSIA implementation that claims Core conformance MUST implement the following:

| Requirement                  | Specification Section | Notes                     |
|------------------------------|----------------------|---------------------------|
| Agent identifier format      | §3                   | Parse and produce valid agent-ids. |
| Message envelope validation  | §4                   | Validate all required, conditional, and optional fields. |
| EdDSA digital signatures     | §5.1, §5.2          | Sign outgoing messages and verify incoming messages using Ed25519. |
| Authorization                | §6                   | Request, present, and validate OAuth 2.0 access tokens with capability scopes. |
| Discovery endpoint           | §7.1                 | Expose `/.well-known/arsia` with all required fields. |
| JWKS endpoint                | §7.3                 | Expose `/.well-known/arsia/jwks.json` with Ed25519 public keys. |
| Version negotiation          | §7.4                 | Implement the version negotiation procedure. |
| HTTP/2 transport             | §8.1                 | Accept and send messages via `POST /v1/arsia/inbox` over TLS 1.3. |
| Direct routing               | §9.1                 | Route messages directly to recipients. |
| Idempotency                  | §10                  | Store and enforce idempotency keys. |
| Error handling               | §11                  | Produce error responses using standard codes and support the retry policy. |

Core conformance does NOT require:
- Compliance field processing (§4.3.6).
- Brokered routing (§9.2).
- WebSocket transport (§8.2).
- Payload encryption (§5.3).
- Capability discovery endpoint (§7.2).
- ES256 or RS256 signature support.

An implementation that meets Core conformance provides a secure, interoperable agent
communication layer without regulatory compliance features.

### 12.2 Compliance Conformance

An ARSIA implementation that claims Compliance conformance MUST meet all Core
conformance requirements (§12.1) and additionally implement the following:

| Requirement                        | Specification Section           | Notes                    |
|------------------------------------|---------------------------------|--------------------------|
| Compliance field processing        | §4.3.6                          | Parse, validate, and enforce the compliance object in message envelopes. |
| At least one compliance profile    | ARSIA-State.md §6               | Implement at least one named compliance profile (e.g., `EU-AI-ACT-HIGH-RISK`). |
| Audit trail                        | ARSIA-State.md §7               | Generate and persist audit records for messages that require auditing. |
| Human oversight signaling          | ARSIA-Actions.md §3             | Support the `pending_approval` and `approval_decision` intents. |
| Brokered routing (conditional)     | §9.2                            | Route through compliant brokers when `data_residency` is set. |
| Capability discovery endpoint      | §7.2                            | Expose `/.well-known/arsia/capabilities` with risk levels and oversight flags. |

Compliance conformance is the minimum level required for agents operating under EU
regulatory obligations. An implementation at this level can participate in
compliance-governed agent ecosystems.

### 12.3 Full Conformance

An ARSIA implementation that claims Full conformance MUST meet all Compliance
conformance requirements (§12.2) and additionally implement the following:

| Requirement                        | Specification Section           | Notes                    |
|------------------------------------|---------------------------------|--------------------------|
| Identity primitive                 | ARSIA-Identity.md               | Full agent identity lifecycle management. |
| Routing primitive                  | ARSIA-Routing.md                | Advanced routing including broker failover and topology negotiation. |
| Actions primitive                  | ARSIA-Actions.md                | Full capability model including hierarchical capabilities, risk-based enforcement, and human oversight workflow. |
| State primitive                    | ARSIA-State.md                  | Agent state management, checkpointing, and recovery. |
| Assets primitive                   | ARSIA-Assets.md                 | Digital asset tracking and transfer between agents. |
| All compliance profiles            | ARSIA-State.md §6               | Implement all defined compliance profiles. |
| WebSocket transport                | §8.2                            | Support persistent bidirectional communication. |
| Payload encryption                 | §5.3                            | Support end-to-end payload encryption. |
| ES256 signature support            | §5.1                            | Support ECDSA P-256 in addition to EdDSA. |
| Conformance test runner            | @arsia-protocol/conformance-test         | Pass the conformance test suite at 100%. |

Full conformance represents a complete implementation of the ARSIA protocol, suitable
for deployment as a reference implementation or as the basis for a commercial agent
platform.

### 12.4 Compliance Field Conformance Tests

The following test cases define conformance requirements for the compliance field
processing defined in §4.3.6–§4.3.8. Each test is identified by a unique `test_id`
and specifies preconditions, actions, and expected results. These tests are normative —
a conformant implementation MUST pass all tests at the Compliance conformance level.

#### CORE-COMPLIANCE-01: pii_involved without legal_basis rejected

| Field             | Value                                                               |
|-------------------|---------------------------------------------------------------------|
| **test_id**       | `CORE-COMPLIANCE-01`                                                |
| **description**   | Verify that pii_involved = true without legal_basis is rejected     |
| **preconditions** | Message has `compliance.pii_involved = true` and no `compliance.legal_basis` field. |
| **action**        | Receiving agent validates the compliance field per §4.3.8, Rule 2.  |
| **expected**      | Message is rejected with error code `"invalid_request"` and `details: { "missing_legal_basis": true }`. |

#### CORE-COMPLIANCE-02: Classification escalation rejected

| Field             | Value                                                               |
|-------------------|---------------------------------------------------------------------|
| **test_id**       | `CORE-COMPLIANCE-02`                                                |
| **description**   | Verify that per-message classification cannot exceed agent-level classification |
| **preconditions** | Agent's `IdentityRecord.ai_system_classification` is `"minimal-risk"`. Message has `compliance.ai_system_classification = "high-risk"`. |
| **action**        | Receiving agent validates classification per §4.3.8, Rule 6.        |
| **expected**      | Message is rejected with error code `"invalid_request"` and `details: { "classification_escalation": true }`. |

#### CORE-COMPLIANCE-03: MCP wrapping preserves compliance

| Field             | Value                                                               |
|-------------------|---------------------------------------------------------------------|
| **test_id**       | `CORE-COMPLIANCE-03`                                                |
| **description**   | Verify that an MCP tool call wrapped in an ARSIA envelope retains compliance enforcement |
| **preconditions** | An MCP tool call is wrapped in an ARSIA message with `payload.type = "arsiaprotocol.mcp/tool-call"` and `compliance.profile = "EU-AI-ACT-HIGH-RISK"`. |
| **action**        | The ARSIA layer processes the message: validates compliance, generates an audit record, and forwards the MCP tool call to the MCP server. |
| **expected**      | An `ArsiaAuditRecord` is generated with `compliance_profile = "EU-AI-ACT-HIGH-RISK"` and `payload_type = "arsiaprotocol.mcp/tool-call"`. The MCP tool call executes normally on the MCP server. Compliance is enforced by the ARSIA layer, not by MCP. |

---

## 13. Security Considerations

This section identifies the primary security threats to ARSIA deployments and
specifies the mitigations provided by the protocol.

### 13.1 Threat Model

The ARSIA threat model considers the following adversaries and attack vectors:

1. **Network interception.** An adversary positioned on the network path between two
   agents (or between an agent and a broker) intercepts ARSIA messages in transit.
   The adversary may attempt to read message contents, extract credentials, or
   correlate message patterns.

2. **Replay attacks.** An adversary captures a valid, signed ARSIA message and
   re-transmits it at a later time to cause duplicate processing, re-execute
   financial transactions, or exploit time-sensitive authorizations.

3. **Capability escalation.** An adversary obtains a valid access token with limited
   scope and attempts to invoke capabilities beyond the token's authorised scope, either
   by modifying the message's `capabilities` field or by exploiting loose enforcement
   in the receiving agent.

4. **Timing attacks.** An adversary exploits clock differences between agents to
   bypass message expiration, extend token lifetimes, or manipulate audit timestamps.

5. **Compromised agents.** An adversary gains control of an agent's private keys
   and uses them to impersonate the agent — signing messages, consuming capabilities,
   and accessing resources authorised for the compromised identity.

6. **Broker compromise.** An adversary gains control of a Compliance Broker and
   attempts to modify relayed messages, drop messages, inject forged messages, or
   exfiltrate message contents while the broker is trusted as an intermediary.

### 13.2 Mitigations

#### 13.2.1 Network Interception

ARSIA mitigates network interception through mandatory transport encryption:

- All HTTP connections MUST use TLS 1.3 or later (§8.1). TLS 1.3 provides
  forward secrecy, ensuring that compromise of long-term keys does not expose
  previously transmitted messages.
- WebSocket connections MUST use the `wss://` scheme (§8.2), which operates over TLS.
- HTTP Strict Transport Security (HSTS) is RECOMMENDED (§8.1) to prevent TLS
  stripping attacks.
- For messages requiring confidentiality beyond transport-level encryption (e.g.,
  through compliance brokers), payload encryption (§5.3) provides end-to-end
  confidentiality.

#### 13.2.2 Replay Attacks

ARSIA provides multiple defences against replay attacks:

- **Message expiration.** Every request and pending_approval message MUST include an
  `expires_at` timestamp (§4.2.2). Recipients MUST reject messages whose `expires_at`
  has passed (with clock skew tolerance). This bounds the window during which a
  captured message can be replayed.

- **Idempotency keys.** Idempotency (§10) ensures that even if a message is
  successfully replayed within the expiration window, the receiving agent returns the
  previously stored response without re-executing the action.

- **Token expiration.** Access tokens have limited lifetimes (§6.1). A replayed
  message with an expired token will be rejected at the authorization stage.

- **DPoP proof.** When DPoP is used (§6.3), the proof JWT includes a unique `jti`
  claim that prevents proof replay.

#### 13.2.3 Capability Escalation

ARSIA mitigates capability escalation through independent verification:

- The receiving agent verifies the access token's `scope` claim independently of the
  message envelope's `capabilities` field (§6.4). The token scope is the authoritative
  source of granted capabilities.

- Even if an adversary modifies the `capabilities` field in the message envelope, the
  token's scope — which is signed by the Authorization Server and cannot be modified
  without invalidating the signature — determines what the agent is actually
  authorised to do.

- The message's digital signature (§5.1) prevents modification of the `capabilities`
  field after signing. Any modification invalidates the signature.

#### 13.2.4 Timing Attacks

ARSIA mitigates timing-based attacks through:

- **Clock skew tolerance.** A tolerance of ±300 seconds is applied to all timestamp
  validation (§8.3). This tolerance is conservative enough to accommodate typical
  clock drift while narrow enough to limit the window for time-based exploits.
  Compliance profiles for regulated environments (e.g., MIFID-II, EU-AI-ACT-HIGH-RISK)
  MAY define stricter tolerances via the `clock_skew_seconds` profile default (§8.3).
  The 300-second global default serves as both the fallback and the ceiling — no profile
  may exceed it.

- **NTP synchronisation.** Implementations SHOULD synchronise system clocks using NTP
  or equivalent (§8.3). Agents operating in compliance-sensitive environments SHOULD
  use multiple time sources.

- **Absolute timestamps.** All ARSIA timestamps use absolute UTC values (RFC 3339 with
  `Z` suffix), avoiding ambiguity from timezone offsets or relative time expressions.

#### 13.2.5 Compromised Agents

ARSIA provides mechanisms to limit the impact and duration of agent compromise:

- **Key rotation.** Agents MUST support key rotation (§7.3). Regular key rotation
  (every 90 days RECOMMENDED) limits the window during which compromised keys are
  useful. In the event of detected compromise, keys MUST be revoked immediately.

- **Short token lifetimes.** Access tokens SHOULD have short lifetimes — 1 hour
  maximum, 5 minutes for high-risk profiles (§6.1). Short lifetimes limit the duration
  during which a stolen token can be used.

- **DPoP binding.** DPoP (§6.3) binds tokens to the holder's private key, preventing
  use of stolen tokens by parties that do not possess the corresponding key.

- **Per-message signatures.** Every message is individually signed (§5.1). Compromise
  of an access token alone does not allow message forgery; the adversary must also
  possess the signing key.

#### 13.2.6 Broker Compromise

ARSIA's architecture limits the damage a compromised broker can inflict:

- **Envelope integrity.** Brokers MUST NOT modify message envelopes (§9.2). The
  sender's digital signature is verified by the final recipient against the sender's
  public key, not the broker's. A compromised broker that modifies a message will
  cause signature verification failure at the recipient.

- **End-to-end signatures.** The signing model is end-to-end: the sender signs, and
  the final recipient verifies. Brokers are transparent to the signature verification
  process.

- **Payload encryption.** When payload encryption (§5.3) is used, the payload is
  encrypted with the final recipient's public key. A compromised broker cannot read
  the encrypted payload.

- **Audit trail.** Brokers MUST produce audit records (§9.2). These records, combined
  with end-to-end signatures, allow forensic analysis to detect broker misbehaviour
  (e.g., dropped messages, delayed forwarding).

- **Broker selection.** The topology determination procedure (§9.4) allows senders to
  choose which broker to use. Organisations can operate their own brokers or use
  trusted third-party brokers, reducing reliance on any single broker.

### 13.3 Privacy Considerations

The ARSIA protocol incorporates the following privacy protections:

1. **Agent identifiers contain no PII.** Agent identifiers (§3) are opaque
   organisational identifiers that MUST NOT contain personally identifiable
   information. There is no protocol-level association between an agent identifier
   and a natural person.

2. **Message identifiers are random.** Message identifiers (§4.1.2) are UUID v4
   values generated from cryptographically secure random sources. They do not encode
   sequential information, timestamps, or other metadata that could be used to infer
   message patterns or volumes.

3. **Distributed tracing is opt-in.** The `context.trace_id` and `context.span_id`
   fields (§4.3.3) are OPTIONAL. Agents that do not wish to participate in distributed
   tracing simply omit these fields. Tracing infrastructure MUST NOT be required for
   protocol compliance.

4. **Audit log retention is governed by compliance profiles.** The
   `compliance.retention_days` field (§4.3.6) explicitly controls how long audit
   records are retained. This allows agents to comply with data minimisation
   requirements (GDPR Article 5(1)(e)) while meeting sector-specific retention
   obligations.

5. **PII flag.** The `compliance.pii_involved` field (§4.3.6) allows messages to
   declare that they contain or trigger processing of personally identifiable
   information. This flag enables receiving agents to apply appropriate data
   protection measures, including encryption at rest, access logging, and data
   subject access request support.

6. **Legal basis declaration.** The `compliance.legal_basis` field (§4.3.6)
   allows messages to declare the GDPR legal basis for processing, supporting
   accountability requirements under GDPR Article 5(2).

---

## 14. IANA Considerations

### 14.1 Media Type Registration

This specification defines the following media type, to be registered with IANA per
[RFC 6838]:

| Parameter          | Value                           |
|--------------------|---------------------------------|
| Type name          | application                     |
| Subtype name       | arsia+json                      |
| Required parameter | `v` (version string, e.g., "1") |
| Optional parameters| none                            |
| Encoding           | UTF-8                           |
| Security considerations | See §13 of this specification. |
| Interoperability   | This media type is used for ARSIA Protocol messages as defined in this specification. |
| Published spec     | This document.                  |
| Fragment identifier| Per [RFC 6901] (JSON Pointer).  |

Usage example:

```
Content-Type: application/arsia+json; v=1
```

The `v` parameter indicates the major protocol version. Recipients MUST verify that
the `v` parameter equals the major version component of the `v` field within the
message envelope (i.e., the portion before the period). A mismatch SHOULD be treated
as an `invalid_request` error.

### 14.2 Well-Known URI Registration

This specification registers the following well-known URI suffix with IANA per
[RFC 8615]:

| Parameter          | Value                                |
|--------------------|--------------------------------------|
| URI suffix         | arsia                                |
| Change controller  | Arsia Labs                           |
| Specification      | §7.1 of this document.               |
| Related information| Used for ARSIA Protocol agent discovery. |

The well-known URI `/.well-known/arsia` serves the agent discovery metadata defined
in §7.1. Sub-paths under `/.well-known/arsia/` serve additional discovery resources:

| Path                             | Description                      | Section |
|----------------------------------|----------------------------------|---------|
| `/.well-known/arsia`             | Agent metadata                   | §7.1    |
| `/.well-known/arsia/capabilities`| Capability details               | §7.2    |
| `/.well-known/arsia/jwks.json`   | JWK Set (public keys)            | §7.3    |
| `/.well-known/arsia/brokers`     | Broker discovery (query param)   | §9.2    |

---

## 15. References

### 15.1 Normative References

**[RFC 2119]** Bradner, S., "Key words for use in RFCs to Indicate Requirement
Levels", BCP 14, RFC 2119, DOI 10.17487/RFC2119, March 1997.

**[RFC 3339]** Klyne, G. and C. Newman, "Date and Time on the Internet: Timestamps",
RFC 3339, DOI 10.17487/RFC3339, July 2002.

**[RFC 4648]** Josefsson, S., "The Base16, Base32, and Base64 Data Encodings",
RFC 4648, DOI 10.17487/RFC4648, October 2006.

**[RFC 5234]** Crocker, D., Ed. and P. Overell, "Augmented BNF for Syntax
Specifications: ABNF", STD 68, RFC 5234, DOI 10.17487/RFC5234, January 2008.

**[RFC 6749]** Hardt, D., Ed., "The OAuth 2.0 Authorization Framework", RFC 6749,
DOI 10.17487/RFC6749, October 2012.

**[RFC 6797]** Hodges, J., Jackson, C., and A. Barth, "HTTP Strict Transport
Security (HSTS)", RFC 6797, DOI 10.17487/RFC6797, November 2012.

**[RFC 6838]** Freed, N., Klensin, J., and T. Hansen, "Media Type Specifications and
Registration Procedures", BCP 13, RFC 6838, DOI 10.17487/RFC6838, January 2013.

**[RFC 6901]** Bryan, P., Ed., Zyp, K., and M. Nottingham, Ed., "JavaScript Object
Notation (JSON) Pointer", RFC 6901, DOI 10.17487/RFC6901, April 2013.

**[RFC 7515]** Jones, M., Bradley, J., and N. Sakimura, "JSON Web Signature (JWS)",
RFC 7515, DOI 10.17487/RFC7515, May 2015.

**[RFC 7516]** Jones, M. and J. Hildebrand, "JSON Web Encryption (JWE)", RFC 7516,
DOI 10.17487/RFC7516, May 2015.

**[RFC 7517]** Jones, M., "JSON Web Key (JWK)", RFC 7517, DOI 10.17487/RFC7517,
May 2015.

**[RFC 7518]** Jones, M., "JSON Web Algorithms (JWA)", RFC 7518,
DOI 10.17487/RFC7518, May 2015.

**[RFC 7519]** Jones, M., Bradley, J., and N. Sakimura, "JSON Web Token (JWT)",
RFC 7519, DOI 10.17487/RFC7519, May 2015.

**[RFC 7523]** Jones, M., Campbell, B., and C. Mortimore, "JSON Web Token (JWT)
Profile for OAuth 2.0 Client Authentication and Authorization Grants", RFC 7523,
DOI 10.17487/RFC7523, May 2015.

**[RFC 8174]** Leiba, B., "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key
Words", BCP 14, RFC 8174, DOI 10.17487/RFC8174, May 2017.

**[RFC 8446]** Rescorla, E., "The Transport Layer Security (TLS) Protocol Version
1.3", RFC 8446, DOI 10.17487/RFC8446, August 2018.

**[RFC 8615]** Nottingham, M., "Well-Known Uniform Resource Identifiers (URIs)",
RFC 8615, DOI 10.17487/RFC8615, May 2019.

**[RFC 8705]** Campbell, B., Bradley, J., Sakimura, N., and T. Lodderstedt, "OAuth
2.0 Mutual-TLS Client Authentication and Certificate-Bound Access Tokens", RFC 8705,
DOI 10.17487/RFC8705, February 2020.

**[RFC 8785]** Rundgren, A., Jordan, B., and S. Erdtman, "JSON Canonicalization
Scheme (JCS)", RFC 8785, DOI 10.17487/RFC8785, June 2020.

**[RFC 9449]** Fett, D., Campbell, B., Bradley, J., Lodderstedt, T., Jones, M., and
D. Waite, "OAuth 2.0 Demonstrating Proof of Possession (DPoP)", RFC 9449,
DOI 10.17487/RFC9449, September 2023.

**[RFC 9562]** Davis, K., Peabody, B., and P. Leach, "Universally Unique Identifiers
(UUIDs)", RFC 9562, DOI 10.17487/RFC9562, May 2024.

**[W3C-TraceContext]** W3C, "Trace Context", W3C Recommendation, February 2020.
https://www.w3.org/TR/trace-context/

**[BCP 47]** Phillips, A., Ed. and M. Davis, Ed., "Tags for Identifying Languages",
BCP 47, RFC 5646, September 2009.

### 15.2 Informative References

**[EU-AI-Act]** European Parliament and Council, "Regulation (EU) 2024/1689 laying
down harmonised rules on artificial intelligence (Artificial Intelligence Act)",
Official Journal of the European Union, L series, 12 July 2024.

**[GDPR]** European Parliament and Council, "Regulation (EU) 2016/679 on the
protection of natural persons with regard to the processing of personal data and on
the free movement of such data (General Data Protection Regulation)", Official Journal
of the European Union, L 119, 4 May 2016.

**[MiFID-II]** European Parliament and Council, "Directive 2014/65/EU on markets in
financial instruments (MiFID II)", Official Journal of the European Union, L 173,
12 June 2014.

---

## Appendix A — Complete Message Examples

This appendix provides three complete, valid ARSIA message examples that conform to
the envelope structure defined in §4. These examples serve as reference for
implementors and as the basis for conformance test vectors.

### A.1 Minimal Request

This example shows a minimal ARSIA request message containing only required fields,
the `payload` with a simple echo action, and the `security` object with an EdDSA
signature.

```json
{
  "v": "1.0",
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "ts": "2026-03-24T14:30:00.000Z",
  "from": "agent:arsialabs.demo.client",
  "to": "agent:arsialabs.demo.echo-server",
  "intent": "request",
  "expires_at": "2026-03-24T14:30:30.000Z",
  "capabilities": [
    "arsiaprotocol.echo"
  ],
  "payload": {
    "type": "arsiaprotocol.echo",
    "args": {
      "message": "Hello, ARSIA!"
    }
  },
  "security": {
    "alg": "EdDSA",
    "kid": "agent:arsialabs.demo.client#key1",
    "sig": "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk_2Gk7wEeLGSRBNaXrHHf4wECH8hmVJjbfXFBMfiZkAQ"
  }
}
```

**Field analysis:**

| Field          | Value                                      | Requirement     |
|----------------|--------------------------------------------|-----------------|
| `v`            | `"1.0"`                                    | §4.1.1 REQUIRED |
| `id`           | UUID v4                                    | §4.1.2 REQUIRED |
| `ts`           | RFC 3339 with milliseconds and Z           | §4.1.3 REQUIRED |
| `from`         | Valid agent-id with `agent:` prefix        | §4.1.4 REQUIRED |
| `to`           | Valid agent-id with `agent:` prefix        | §4.1.5 REQUIRED |
| `intent`       | `"request"`                                | §4.1.6 REQUIRED |
| `expires_at`   | Required for `intent: "request"` (§4.2.2)  | §4.2.2 COND. REQ. |
| `capabilities` | Required for `intent: "request"` (§4.2.3)  | §4.2.3 COND. REQ. |
| `payload`      | Present with `type` and `args`             | §4.3.4, §4.4 OPTIONAL |
| `security`     | Present with `alg`, `kid`, `sig`           | §4.3.5 OPTIONAL |

Note: The `security.sig` value in this example is illustrative. In a real
implementation, it would be the base64url-encoded Ed25519 signature computed over the
RFC 8785 canonical form of the message without the `security` field, as specified in
§5.1.

### A.2 Full Request with EU-AI-ACT-HIGH-RISK Compliance Profile

This example shows a complete ARSIA request message using all optional fields,
including the compliance object with the `EU-AI-ACT-HIGH-RISK` profile, distributed
tracing context, and idempotency configuration.

```json
{
  "v": "1.0",
  "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "ts": "2026-03-24T10:15:30.000Z",
  "from": "agent:europa.mifid.risk-engine",
  "to": "agent:europa.mifid.compliance-checker",
  "intent": "request",
  "min_v": "1.0",
  "expires_at": "2026-03-24T10:16:00.000Z",
  "capabilities": [
    "eu.mifid.risk.assess",
    "eu.mifid.compliance.check"
  ],
  "idempotency": {
    "key": "risk-assessment-2026-03-24-client-7291",
    "expires_at": "2026-03-25T10:15:30.000Z"
  },
  "context": {
    "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
    "span_id": "00f067aa0ba902b7",
    "flags": 1,
    "locale": "pt-PT",
    "priority": 8
  },
  "payload": {
    "type": "eu.mifid.risk/assess",
    "version": "1.0",
    "args": {
      "client_id": "CLT-7291",
      "instrument_type": "derivative",
      "notional_value": 500000.00,
      "currency": "EUR",
      "counterparty_jurisdiction": "DE",
      "assessment_type": "pre-trade",
      "requested_checks": [
        "concentration_risk",
        "counterparty_risk",
        "market_risk"
      ]
    }
  },
  "security": {
    "alg": "EdDSA",
    "kid": "agent:europa.mifid.risk-engine#key1",
    "sig": "XYZ789abc123def456ghi789jkl012mno345pqr678stu901vwx234yza567bcd890efg123hij456klm789nA"
  },
  "compliance": {
    "profile": "EU-AI-ACT-HIGH-RISK",
    "data_residency": "EU",
    "audit_required": true,
    "retention_days": 180,
    "human_oversight": "required_before_execution",
    "explainability_required": true,
    "pii_involved": false,
    "legal_basis": "legal_obligation",
    "ai_system_classification": "high-risk"
  }
}
```

**Field analysis:**

| Field            | Value                                       | Requirement      |
|------------------|---------------------------------------------|------------------|
| `v`              | `"1.0"`                                     | §4.1.1 REQUIRED  |
| `id`             | UUID v4                                     | §4.1.2 REQUIRED  |
| `ts`             | RFC 3339 with milliseconds and Z            | §4.1.3 REQUIRED  |
| `from`           | Valid agent-id                              | §4.1.4 REQUIRED  |
| `to`             | Valid agent-id                              | §4.1.5 REQUIRED  |
| `intent`         | `"request"`                                 | §4.1.6 REQUIRED  |
| `min_v`          | `"1.0"`                                     | §4.3.1 OPTIONAL  |
| `expires_at`     | 30 seconds after `ts`                       | §4.2.2 COND. REQ.|
| `capabilities`   | 2 capabilities, unique                      | §4.2.3 COND. REQ.|
| `idempotency`    | Key + 24h expiry                            | §4.3.2 OPTIONAL  |
| `context`        | Full W3C trace + locale + priority          | §4.3.3 OPTIONAL  |
| `payload`        | With type, version, and args                | §4.3.4, §4.4     |
| `security`       | EdDSA signature                             | §4.3.5 OPTIONAL  |
| `compliance`     | Full EU-AI-ACT-HIGH-RISK profile            | §4.3.6 OPTIONAL  |

**Compliance field analysis:**

| Field                      | Value                           | Effect                   |
|----------------------------|---------------------------------|--------------------------|
| `profile`                  | `"EU-AI-ACT-HIGH-RISK"`        | Loads profile defaults   |
| `data_residency`           | `"EU"`                          | Triggers brokered routing (§9.2) |
| `audit_required`           | `true`                          | Audit record MUST be generated |
| `retention_days`           | `180`                           | 180-day audit retention  |
| `human_oversight`          | `"required_before_execution"`   | Recipient MUST obtain human approval before executing |
| `explainability_required`  | `true`                          | Response MUST include decision explanation |
| `pii_involved`             | `false`                         | No PII in this message   |
| `legal_basis`              | `"legal_obligation"`            | GDPR Art. 6(1)(c)       |
| `ai_system_classification` | `"high-risk"`                   | EU AI Act high-risk system |

Because `compliance.data_residency` is set to `"EU"`, the topology determination procedure
(§9.4) requires this message to be routed through an EU-based Compliance Broker.
Because `compliance.human_oversight` is `"required_before_execution"`, the recipient is
expected to respond with a `pending_approval` message before executing the risk
assessment.

### A.3 Error Response

This example shows an error response to the minimal request in §A.1. The error
indicates that the sender's access token does not include sufficient capabilities.

```json
{
  "v": "1.0",
  "id": "b8c96a3e-2d4f-4e8a-9b1c-3f5e7d9a0c2b",
  "ts": "2026-03-24T14:30:00.125Z",
  "from": "agent:arsialabs.demo.echo-server",
  "to": "agent:arsialabs.demo.client",
  "intent": "error",
  "correlation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "payload": {
    "type": "arsiaprotocol.echo",
    "error": {
      "code": "forbidden",
      "description": "The access token does not include the required capability. The token scope covers 'arsiaprotocol.health' but the request requires 'arsiaprotocol.echo'. Obtain a new token with the correct scope from the Authorization Server.",
      "details": {
        "required_capabilities": [
          "arsiaprotocol.echo"
        ],
        "provided_capabilities": [
          "arsiaprotocol.health"
        ]
      }
    }
  },
  "security": {
    "alg": "EdDSA",
    "kid": "agent:arsialabs.demo.echo-server#key1",
    "sig": "ABC123def456ghi789jkl012mno345pqr678stu901vwx234yza567bcd890efg123hij456klm789nBcdef0Q"
  }
}
```

**Field analysis:**

| Field            | Value                                         | Requirement       |
|------------------|-----------------------------------------------|-------------------|
| `v`              | `"1.0"`                                       | §4.1.1 REQUIRED   |
| `id`             | UUID v4 (new, unique to this response)        | §4.1.2 REQUIRED   |
| `ts`             | 125ms after the request's `ts`                | §4.1.3 REQUIRED   |
| `from`           | The echo server (responder)                   | §4.1.4 REQUIRED   |
| `to`             | The client (original sender)                  | §4.1.5 REQUIRED   |
| `intent`         | `"error"`                                     | §4.1.6 REQUIRED   |
| `correlation_id` | Matches `id` of the request in §A.1           | §4.2.1 COND. REQ. |
| `payload.type`   | Same as original request                      | §4.4.1 REQUIRED   |
| `payload.error`  | Contains `code`, `description`, `details`     | §4.4.6 REQUIRED   |
| `security`       | EdDSA signature from the echo server          | §4.3.5 OPTIONAL   |

**Error detail analysis:**

The `forbidden` error code maps to HTTP status 403 (§11.2). Per §6.4, the error
details MUST include `required_capabilities` and `provided_capabilities` arrays. In
this example:

- `required_capabilities`: `["arsiaprotocol.echo"]` — the capabilities listed in the
  original request's `capabilities` field.
- `provided_capabilities`: `["arsiaprotocol.health"]` — the capabilities present in the
  sender's access token scope.

This error is not retryable (§11.3). The sending agent must obtain a new access token
from the Authorization Server with the `arsiaprotocol.echo` capability in scope before
re-sending the request.

---

## Appendix B — ARSIA as a Compliance Layer for MCP and A2A

### B.1 ARSIA as a Compliance Layer for MCP

MCP (Model Context Protocol), developed by Anthropic, defines structured communication
between AI models and tools. MCP excels at tool calling — describing available tools,
invoking them with structured arguments, and returning results. However, MCP has no
compliance fields, no audit trail, no human oversight signaling, and no data residency
constraints. An MCP tool call that triggers a high-risk financial operation produces no
audit record, requires no human approval, and imposes no data residency requirement at
the protocol level.

An MCP message wrapped in an ARSIA envelope gains all of these capabilities. The
wrapping is mechanical and requires no modification to MCP itself. The MCP tool call
becomes the payload of an ARSIA message: `payload.type` is set to
`"arsiaprotocol.mcp/tool-call"` and `payload.args` contains the MCP tool call object. The ARSIA
envelope adds the `compliance` field (profile, audit requirements, oversight mode,
residency zone), the `security` field (EdDSA signature, key identifier), and identity
semantics (agent-id, owner accountability via the IdentityRecord). The MCP server
processes the tool call normally — it does not need to understand ARSIA. The ARSIA layer
intercepts the message before it reaches the MCP server, logs the audit record, enforces
compliance validation, and triggers the human oversight flow if required.

This approach requires no changes to MCP itself. An existing MCP deployment can adopt
ARSIA compliance incrementally: wrap the messages that require compliance, leave the rest
unchanged. The ARSIA layer is a middleware that sits between the MCP client and the MCP
server. Over time, as the operator's compliance requirements grow, more messages can be
wrapped — up to and including all messages in a full-compliance deployment.

### B.2 ARSIA as a Compliance Layer for A2A

A2A (Agent-to-Agent Protocol), developed by Google, defines task delegation between
agents. A2A is effective at expressing multi-step workflows where one agent delegates
subtasks to another. Like MCP, A2A lacks compliance primitives — there are no fields for
audit obligations, regulatory profiles, human oversight, or data residency.

Wrapping follows the same pattern as MCP. The A2A task object becomes the payload of an
ARSIA message: `payload.type` is set to `"arsiaprotocol.a2a/task"` and `payload.args` contains
the A2A task object. The ARSIA envelope adds compliance, security, and identity
semantics. The A2A receiving agent processes the task normally.

A2A's task lifecycle — submitted, working, completed — maps naturally to ARSIA's message
lifecycle. An A2A task that requires human oversight maps to ARSIA's
`pending_approval` flow: the ARSIA layer intercepts the task submission, determines that
oversight is required (based on the compliance profile or per-message `human_oversight`
field), responds with a `pending_approval` message, and holds the A2A task in a
"submitted" state until an `approval_decision` is received. Once approved, the A2A task
proceeds to "working" and eventually "completed," with each state transition generating
an audit record.

### B.3 AAIF (Agent Interoperability Forum) Submission Positioning

ARSIA is not a competitor to protocols developed by AAIF members. It is a compliance
extension that sits above them. This is the key message for the AAIF submission: ARSIA
provides the compliance layer that AAIF protocols currently lack, without requiring any
modification to those protocols.

AAIF members — including Anthropic, OpenAI, Google, Microsoft, and AWS — declared in
December 2025 that identity and governance are "works in progress" and invited external
contributions. ARSIA provides a ready-made, open-source compliance layer
that any AAIF member can adopt. The compliance profiles defined in ARSIA-State.md §6 of this
specification implement the EU AI Act, GDPR, MiFID II, and (planned) CAP requirements
that European enterprises must satisfy. No AAIF member would need to independently
implement these requirements in their own protocol — they can adopt ARSIA's compliance
envelope and profiles directly.

The value proposition to AAIF is quantifiable. The EU single market represents a €16
trillion economy with over 450 million consumers. The EU AI Act, GDPR, and MiFID II
apply to any AI agent operating within this market, regardless of where the agent's
developer or operator is based. Adopting ARSIA compliance profiles gives AAIF protocols
access to this market without each member having to build, validate, and maintain
EU-specific compliance infrastructure independently. The ARSIA Protocol is licensed under CC BY-SA 4.0 — there are no licensing barriers to adoption.

*End of ARSIA Protocol Core Specification — Draft-01*

---
ARSIA Protocol ([arsiaprotocol.org](https://arsiaprotocol.org)) | by [Arsia Labs](https://arsialabs.ai)
