<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
# ARSIA-Routing — Routing Primitive Specification

**Protocol:** ARSIA Protocol
**Version:** 1.0
**Status:** Draft
**Authors:**
- Kirk Patrick (Arsia Labs) — kirk@arsialabs.ai
- Greici Savoldi (Arsia Labs) — greici@arsialabs.ai

**Draft-01 | March 2026 | References: ARSIA-Core.md §7, §8, §9**
**Arsia Labs — arsiaprotocol.org**

---

## Abstract

The Routing primitive defines how ARSIA messages travel from sender to recipient,
including transport bindings, delivery guarantees, data residency enforcement, and the
optional Compliance Broker mechanism. It extends the routing foundations established in
ARSIA-Core.md §9 with full normative detail on broker discovery, relay semantics,
message lifecycle states, and transport-level requirements. This specification is
normative for all ARSIA Protocol implementations. Direct routing is required at all
conformance levels; brokered routing is required only when the message envelope declares
a `compliance.data_residency` constraint.

---

## Status of This Memo

This document specifies Draft-01 of the ARSIA Routing Primitive. This specification is
a working draft published by Arsia Labs for review and comment. Implementors should
expect breaking changes between draft revisions.

The canonical location for this specification is:

    https://arsiaprotocol.org/spec/routing/draft-01

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

1. [Routing Model](#1-routing-model)
   1. [Core Concepts](#11-core-concepts)
   2. [Routing Topologies](#12-routing-topologies)
   3. [Topology Determination Procedure](#13-topology-determination-procedure)
   4. [Broker Selection Criteria](#14-broker-selection-criteria)
2. [Transport Bindings](#2-transport-bindings)
   1. [HTTP/2 Binding (REQUIRED)](#21-http2-binding-required)
   2. [WebSocket Binding (OPTIONAL)](#22-websocket-binding-optional)
   3. [Broker Relay Transport](#23-broker-relay-transport)
3. [Delivery Guarantees](#3-delivery-guarantees)
   1. [At-Most-Once Delivery (Default)](#31-at-most-once-delivery-default)
   2. [At-Least-Once Delivery (Opt-In)](#32-at-least-once-delivery-opt-in)
   3. [Exactly-Once Delivery](#33-exactly-once-delivery)
4. [Message Routing Lifecycle](#4-message-routing-lifecycle)
   1. [Lifecycle States](#41-lifecycle-states)
   2. [State Transition Diagram](#42-state-transition-diagram)
5. [Data Residency in Routing](#5-data-residency-in-routing)
   1. [Declaring Residency Requirements](#51-declaring-residency-requirements)
   2. [EU Data Residency](#52-eu-data-residency)
   3. [Residency Verification](#53-residency-verification)
6. [Rate Limiting](#6-rate-limiting)
   1. [Rate Limit Advertisement](#61-rate-limit-advertisement)
   2. [Rate Limit Response Headers](#62-rate-limit-response-headers)
   3. [Priority Routing](#63-priority-routing)
7. [Broker Specification](#7-broker-specification)
   1. [Broker Identity Requirements](#71-broker-identity-requirements)
   2. [Broker Discovery Endpoint](#72-broker-discovery-endpoint)
   3. [Broker Relay Rules (Normative)](#73-broker-relay-rules-normative)
   4. [Broker Audit Record Format](#74-broker-audit-record-format)
8. [Routing Conformance Tests](#8-routing-conformance-tests)
9. [References](#9-references)

---

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14 [RFC 2119] [RFC 8174] when,
and only when, they appear in ALL CAPITALS, as shown here.

---

## 1. Routing Model

The routing model defines the concepts, topologies, and algorithms that govern how
ARSIA messages travel from a sending agent to a receiving agent. This section
establishes the vocabulary used throughout the specification and provides the normative
topology determination logic that all implementations MUST follow.

### 1.1 Core Concepts

The following terms are defined with precise meaning for use throughout this
specification.

**Inbox.** The inbox is the single canonical endpoint where an agent receives ARSIA
messages. The inbox URL follows the format `https://{host}/v1/arsia/inbox` and is the
target for all HTTP-based message delivery as defined in ARSIA-Core.md §8.1. An agent
MUST have exactly one inbox. The inbox URL is published in the agent's discovery
metadata (ARSIA-Core.md §7.1) via the `inbox` field. All message delivery — whether
direct or brokered — ultimately terminates at the recipient's inbox. The inbox accepts
HTTP POST requests containing ARSIA message envelopes and returns ARSIA response
envelopes. The inbox endpoint MUST be served over TLS (ARSIA-Core.md §8.1) and MUST
require a valid access token or DPoP-bound token (ARSIA-Core.md §6.3) on every
request.

**Routing Topology.** A routing topology describes the path a message takes from the
sending agent to the receiving agent, including any intermediaries involved in the
delivery. ARSIA Protocol v1.0 defines three topologies: direct, brokered, and
federated. Direct topology involves no intermediaries. Brokered topology introduces a
Compliance Broker as a transparent relay between the sender and the recipient. Federated
topology enables multi-hop routing across organisational boundaries and is reserved for
future specification — implementations MUST NOT use federated routing in v1.0. The
topology used for a given message is determined by the topology determination procedure
defined in §1.3 and is a function of the message's compliance metadata. The topology is
not a property of the agent or the infrastructure; it is determined per-message based on
the contents of the message envelope.

**Delivery Guarantee.** A delivery guarantee describes the level of assurance that a
message will reach its intended recipient and be processed exactly the intended number
of times. ARSIA Protocol v1.0 defines three delivery guarantee levels:
at-most-once (default), at-least-once (opt-in via the idempotency mechanism defined in
ARSIA-Core.md §10), and exactly-once (achievable only at the application level by
combining at-least-once delivery with idempotent receivers). The delivery guarantee is
not a transport-level property — it is an end-to-end property that spans the entire
message path from sender through any intermediaries to the final recipient. The
at-most-once guarantee is implicit in all ARSIA messaging; stronger guarantees require
explicit opt-in by the sender and corresponding support by the receiver. The delivery
guarantee levels are defined in detail in §3.

**Data Residency Zone.** A data residency zone is a geographic region where message
processing and storage MUST occur, as declared in the `compliance.data_residency` field
of the message envelope (ARSIA-Core.md §4.3.6). A zone is identified by an ISO 3166-1
alpha-2 country code (e.g., `"PT"`, `"DE"`, `"FR"`) or a recognised regional code
(e.g., `"EU"` for the European Union / European Economic Area). When a data residency
zone is declared, the message MUST be routed through a Compliance Broker whose physical
infrastructure resides entirely within the declared zone (ARSIA-Core.md §9.2). The data
residency constraint applies to all processing of the message, including temporary
storage during relay, logging, audit trail generation, and any computational operations
performed on the message contents. Data residency is a hard constraint: if no compliant
broker is available for the required zone, the message MUST NOT be sent.

**Compliance Broker.** A Compliance Broker is an ARSIA-conformant agent with the
capability `arsiaprotocol.broker.relay` that relays messages between other agents within a
declared data residency zone. Brokers are transparent intermediaries: they MUST NOT
modify the message envelope contents in any way, and the sender's digital signature
MUST remain valid end-to-end from the sender to the final recipient, passing through
the broker without alteration. The broker's role is strictly limited to receiving the
message from the sender, verifying the sender's signature, verifying that its own
physical location satisfies the message's data residency requirement, forwarding the
message to the recipient's inbox using direct routing, and recording a relay audit
event. A broker MUST NOT read or log the payload contents — it MAY only record the
`payload_hash` for audit purposes. Brokers are defined in full in §7.

### 1.2 Routing Topologies

ARSIA Protocol v1.0 defines three routing topologies. Only the direct and brokered
topologies are normatively specified in this version; the federated topology is reserved
for future specification.

#### 1.2.1 Direct Routing (REQUIRED for Core Conformance)

Direct routing is the default routing mode. The sending agent resolves the recipient's
inbox URL from the discovery endpoint and sends a POST request directly to the
recipient's inbox. No intermediary is involved. Direct routing is the simplest and
fastest path for message delivery.

**Flow:**

1. **Discovery.** The sender discovers the recipient by issuing a GET request to the
   recipient's discovery endpoint:

   ```
   GET {recipient-host}/.well-known/arsia
   ```

   The sender receives an `AgentMetadata` response (ARSIA-Core.md §7.1) containing the
   recipient's inbox URL, JWKS URL, supported capabilities, rate limits, and other
   operational parameters.

2. **Inbox extraction.** The sender extracts the `inbox` field from the discovery
   response. This is the absolute URL to which the message will be delivered.

3. **Message signing.** The sender constructs the ARSIA message envelope and signs it
   using its Ed25519 private key, following the signing procedure defined in
   ARSIA-Core.md §5.1. The signature is computed over the RFC 8785 canonical form of
   the message with the `security` field removed. The resulting signature is placed in
   `security.sig`.

4. **Token presentation.** The sender obtains an access token for the recipient from an
   authorization server (ARSIA-Core.md §6.2) and presents it in the `Authorization`
   header of the HTTP request, per ARSIA-Core.md §6.3. The token's `aud` claim MUST
   equal the recipient's agent-id. The token's `sub` claim MUST equal the sender's
   agent-id. The token's `scope` claim MUST include all capabilities listed in the
   message's `capabilities` field.

5. **Message dispatch.** The sender issues an HTTP POST request to the recipient's
   inbox URL with the signed message envelope as the request body:

   ```http
   POST /v1/arsia/inbox HTTP/2
   Host: {recipient-host}
   Content-Type: application/arsia+json; v=1
   Authorization: Bearer {access_token}

   {ARSIA message envelope}
   ```

6. **Recipient processing.** The recipient receives the message and performs the
   following validation steps in order:

   a. Verify the message size does not exceed `max_message_bytes` (ARSIA-Core.md §4.5).
   b. Parse the JSON envelope and validate required fields (ARSIA-Core.md §4.1).
   c. Verify the digital signature (ARSIA-Core.md §5.2).
   d. Validate the access token (ARSIA-Core.md §6.4).
   e. Verify protocol version compatibility (ARSIA-Core.md §7.4).
   f. Check idempotency key for deduplication (ARSIA-Core.md §10).
   g. Check message expiration: if `expires_at` is in the past (after accounting for
      ±300 seconds clock skew tolerance per ARSIA-Core.md §8.3), reject with error
      code `invalid_request`.
   h. Process the message payload.

7. **Response.** The recipient returns either:

   - **HTTP 200 OK** with a synchronous ARSIA response envelope
     (`Content-Type: application/arsia+json; v=1`), or
   - **HTTP 202 Accepted** with a `Location` header pointing to a status URL for
     asynchronous processing (ARSIA-Core.md §8.1).

**Applicability:** Direct routing is used when no `compliance.data_residency`
constraint is set in the message envelope, OR when the sender and the recipient are
both physically located within the same residency zone and no regulatory requirement
mandates broker involvement. Direct routing MUST be sufficient for Core conformance
(ARSIA-Core.md §12.1).

> **Note (informative).** Setting `compliance.data_residency` on a message envelope
> constitutes a regulatory requirement that mandates broker involvement (§1.2.2),
> even when both agents reside within the declared zone.

#### 1.2.2 Brokered Routing (REQUIRED When `compliance.data_residency` Is Set)

Brokered routing is mandatory when a message envelope contains a
`compliance.data_residency` value (ARSIA-Core.md §9.2). The sending agent MUST route
the message through a Compliance Broker whose physical infrastructure resides within
the declared data residency zone. The sender MUST NOT send the message directly to the
recipient, even if direct connectivity is available.

**Flow:**

1. **Residency check.** The sender inspects the message envelope. The field
   `message.compliance.data_residency` contains a zone identifier (e.g., `"EU"`).

2. **Broker discovery.** The sender discovers eligible brokers by querying a broker
   discovery endpoint:

   ```
   GET {broker-registry}/.well-known/arsia/brokers?residency=EU
   ```

   This endpoint returns a JSON array of `BrokerEntry` objects (§7.2). The broker
   registry MAY be hosted by the recipient agent, a dedicated broker registry service,
   or the sender's own organisation.

3. **Broker selection.** The sender selects a broker from the response using the
   selection criteria defined in §1.4. The selected broker MUST declare the capability
   `arsiaprotocol.broker.relay` and MUST have a jurisdiction that satisfies the required
   residency zone.

4. **Message signing.** The sender signs the message with its own Ed25519 private key,
   following the same procedure as in direct routing (ARSIA-Core.md §5.1). The
   signature is end-to-end: it is computed by the sender and verified by the final
   recipient. The broker does NOT sign the message.

5. **Relay request.** The sender sends the signed message to the broker's inbox using
   the standard HTTP/2 binding (§2.1). The request is identical to a direct routing
   request — the message envelope is not modified for broker relay. The `to` field in
   the envelope still contains the final recipient's agent-id, not the broker's.

   ```http
   POST /v1/arsia/inbox HTTP/2
   Host: {broker-host}
   Content-Type: application/arsia+json; v=1
   Authorization: Bearer {access_token_for_broker}

   {ARSIA message envelope with to=final-recipient}
   ```

6. **Broker validation.** The broker receives the message and performs the following
   checks:

   a. Verify the sender's digital signature (ARSIA-Core.md §5.2).
   b. Verify the sender's access token. The token MUST include the `arsiaprotocol.broker.relay`
      capability.
   c. Verify that the broker's own physical jurisdiction matches the zone declared in
      `message.compliance.data_residency`. If the broker's jurisdiction does not satisfy
      the zone (e.g., the broker is in the US but the zone is `"EU"`), the broker MUST
      reject the message with error code `service_unavailable` (ARSIA-Core.md §11.2) and details:
      `{ "data_residency_violation": true, "broker_jurisdiction": "{actual}", "required_zone": "{zone}" }`.

7. **Message forwarding.** The broker forwards the message to the recipient's inbox
   using direct routing (§1.2.1). The broker:

   a. Discovers the recipient's inbox URL from the recipient's discovery endpoint
      (ARSIA-Core.md §7.1).
   b. Obtains an access token for the recipient from an authorization server.
   c. Sends the EXACT same message envelope — byte-identical after JSON canonicalization
      — to the recipient's inbox via HTTP POST.

8. **Envelope integrity.** The broker MUST NOT modify the message envelope in any way.
   The message forwarded to the recipient is the same message received from the sender.
   The sender's original digital signature remains intact and is verified by the
   recipient against the sender's public key, not the broker's.

9. **Audit logging.** The broker appends a `broker_relay` audit event to its own audit
   trail (§7.4). The audit record includes the relay ID, message ID, sender and
   recipient agent-ids, the residency zone, the relay timestamp, and a hash of the
   message payload. The broker MUST NOT log the payload contents.

10. **Response relay.** The broker returns the recipient's response to the sender:

    - If the recipient responds synchronously (HTTP 200): the broker forwards the
      recipient's response envelope to the sender unmodified.
    - If the recipient responds asynchronously (HTTP 202): the broker returns a relay
      receipt to the sender (§2.3).
    - If forwarding fails: the broker returns a standard ARSIA error envelope to the
      sender with details indicating the relay failure.

**No eligible broker available:**

If no eligible broker is available for the required residency zone, the sender MUST
NOT send the message. The sender MUST return an error to its caller with the following
structure:

```json
{
  "v": "1.0",
  "id": "{uuid}",
  "ts": "{timestamp}",
  "from": "{sender-agent-id}",
  "to": "{intended-recipient-agent-id}",
  "intent": "error",
  "correlation_id": "{original-request-id}",
  "payload": {
    "type": "arsiaprotocol.error",
    "error": {
      "code": "service_unavailable",
      "description": "No compliant broker available for the required data residency zone.",
      "details": {
        "data_residency_violation": true,
        "required_zone": "{zone}",
        "available_zones": []
      }
    }
  }
}
```

This is a hard requirement: violating data residency by sending the message through an
alternative route is not permitted (ARSIA-Core.md §9.2).

#### 1.2.3 Federated Routing (OPTIONAL — Not Defined in v1.0)

Federated routing enables cross-organisational, multi-hop message delivery where a
message traverses multiple brokers across organisational boundaries:

```
A -> Local Broker -> Cross-Org Broker -> B
```

Federated routing is reserved for future specification. Agents MUST NOT use federated
routing in ARSIA Protocol v1.0 implementations. Implementations that require
cross-organisation routing MUST use brokered routing with a shared broker — that is,
both organisations MUST agree on a single broker that both can route through, and that
broker MUST reside within any applicable data residency zone.

The federated topology is declared here for completeness and to reserve its position in
the topology enumeration. Future versions of this specification will define the trust
model, chained signature verification, multi-hop audit trail semantics, and cross-org
broker discovery mechanisms necessary for federated routing.

### 1.3 Topology Determination Procedure

The following algorithm is normative. Sending agents MUST implement this logic, or
logic that produces identical results for all inputs, when determining how to route a
message.

```typescript
function selectTopology(message: ArsiaMessage): RoutingDecision {
  // Step 1: Check if data residency is required.
  // The compliance.data_residency field, when present and non-empty,
  // mandates brokered routing (ARSIA-Core.md §9.2).

  if (message.compliance?.data_residency) {
    const zone = message.compliance.data_residency;

    // Step 2: Discover eligible brokers for the required zone.
    // The discoverBrokers function queries the broker discovery endpoint
    // (§7.2) and returns all brokers whose residency_zones include the
    // required zone.

    const brokers = discoverBrokers(zone);

    // Step 3: If no eligible broker is found, the message MUST NOT be sent.
    // Return an error indicating data residency violation.

    if (brokers.length === 0) {
      return {
        topology: "ERROR",
        error: {
          code: "service_unavailable",
          description: "No compliant broker available for the required data residency zone.",
          details: {
            data_residency_violation: true,
            required_zone: zone,
            available_zones: []
          }
        }
      };
    }

    // Step 4: Select a broker from the available candidates.
    // Broker selection criteria are defined in §1.4.

    const broker = selectBroker(brokers);

    return {
      topology: "BROKERED",
      broker: broker
    };
  }

  // Step 5: No data residency constraint. Use direct routing.

  return {
    topology: "DIRECT"
  };
}
```

**Algorithm invariants:**

- The algorithm MUST be evaluated for every outbound message. Topology determination MUST
  NOT be cached across messages, because different messages from the same sender to the
  same recipient may have different compliance metadata.

- The `compliance.data_residency` field is the sole input that determines whether
  brokered routing is required. No other compliance field (e.g., `audit_required`,
  `profile`) triggers brokered routing.

- The algorithm does NOT consider whether the sender and recipient are in the same
  residency zone. Even if both agents are physically within the EU, a message with
  `data_residency: "EU"` MUST still be routed through a broker. This ensures a verifiable
  audit trail for all residency-constrained messages.

- If the `compliance` object is absent, or if `data_residency` is absent or empty within
  the `compliance` object, direct routing is used.

### 1.4 Broker Selection Criteria

When the topology determination procedure (§1.3) determines that brokered routing is
required and multiple eligible brokers are available for the required zone, the sender
MUST select one broker from the available candidates. The selection process is defined
in this section.

**Selection criteria (in priority order):**

The sender SHOULD evaluate the following criteria in order. The first criterion that
distinguishes between candidates SHOULD be used to make the selection. If a criterion
does not distinguish (i.e., all remaining candidates are equal on that criterion), the
sender proceeds to the next criterion.

1. **Lowest latency.** The sender SHOULD prefer the broker with the lowest measured or
   estimated network latency. Latency MAY be measured by prior health check responses,
   geographic proximity estimation based on the broker's declared jurisdiction, or
   active latency probes. If no latency data is available, this criterion is skipped.

2. **Highest availability.** The sender SHOULD prefer brokers that report a `health`
   status of `"healthy"` in their broker discovery entry (§7.2). Brokers that report
   `"degraded"` SHOULD be deprioritised. Brokers that report `"unhealthy"` MUST be
   excluded from selection.

3. **Lowest load.** If the broker discovery response includes load information
   (`capacity.current_load_pct` in §7.2), the sender SHOULD prefer the broker with the
   lowest current load percentage. This criterion is applicable only when the broker
   registry provides load data.

4. **Random selection.** If all remaining candidates are equal on the above criteria,
   the sender MUST select randomly among them using a uniform distribution. This
   prevents systematic bias toward a single broker when all else is equal and provides
   basic load distribution.

**Custom selection strategies:**

Implementations MAY define custom broker selection strategies beyond the criteria listed
above. Examples include:

- **Cost-based selection:** Prefer brokers with lower per-relay fees.
- **Contractual preference:** Prefer brokers with which the sender has an existing
  service agreement.
- **Diversity selection:** Distribute relay traffic across multiple brokers to reduce
  single-point-of-failure risk.

Custom strategies MUST still respect the hard constraint: the selected broker MUST
reside within the required data residency zone. No custom strategy may override this
constraint.

**Non-normative nature of selection criteria:**

The broker selection criteria defined in this section (items 1-4 above) are
RECOMMENDED, not REQUIRED. The sender MAY use any selection strategy, including
selecting the first broker in the discovery response, as long as the selected broker
satisfies the residency zone requirement. The topology determination procedure (§1.3) is
normative; the broker selection criteria (§1.4) are guidance.

---

## 2. Transport Bindings

This section extends the transport binding definitions in ARSIA-Core.md §8 with
additional implementation detail specific to routing. The HTTP/2 binding (§2.1) is
REQUIRED for all conformant implementations. The WebSocket binding (§2.2) is OPTIONAL.
The broker relay transport (§2.3) defines the transport-level behaviour specific to
brokered routing.

### 2.1 HTTP/2 Binding (REQUIRED)

The HTTP/2 transport binding is the primary transport for ARSIA message delivery. This
section provides the full normative definition, extending ARSIA-Core.md §8.1 with
additional implementation requirements.

#### 2.1.1 Request Format

All ARSIA messages are delivered via HTTP POST to the recipient's inbox endpoint.

```http
POST /v1/arsia/inbox HTTP/2
Host: {recipient-host}
Content-Type: application/arsia+json; v=1
Accept: application/arsia+json; v=1
Authorization: Bearer {access_token}
```

**Method:** POST. All message deliveries use POST regardless of intent (request,
response, event, error, pending_approval, approval_decision).

**Path:** `/v1/arsia/inbox`. The complete inbox URL is obtained from the recipient's
discovery metadata (ARSIA-Core.md §7.1). The path includes a version prefix (`/v1/`)
to support future incompatible path changes.

**Required headers:**

| Header          | Value                            | Description                        |
|-----------------|----------------------------------|------------------------------------|
| `Content-Type`  | `application/arsia+json; v=1`    | ARSIA media type with version.     |
| `Accept`        | `application/arsia+json; v=1`    | Expected response media type.      |
| `Authorization` | `Bearer {token}` or `DPoP {token}` | Access token per ARSIA-Core.md §6.3. |

**Optional headers:**

| Header               | Type    | Description                                      |
|----------------------|---------|--------------------------------------------------|
| `Idempotency-Key`   | string  | Idempotency key (ARSIA-Core.md §10). 1-128 chars. Overrides `idempotency.key` in envelope if both are present (ARSIA-Core.md §10.4). |
| `X-Request-Priority` | integer | Message processing priority, 0-10. Maps to `context.priority` in envelope (ARSIA-Core.md §4.3.3). Higher values indicate higher priority. |
| `DPoP`              | string  | DPoP proof JWT, when using DPoP-bound tokens (ARSIA-Core.md §6.3). |

**Request body:** The request body MUST be a valid ARSIA message envelope serialised as
UTF-8 JSON, conforming to the envelope schema defined in ARSIA-Core.md §4.

#### 2.1.2 Response Format

**Synchronous response (HTTP 200 OK):**

```http
HTTP/2 200 OK
Content-Type: application/arsia+json; v=1

{ARSIA response envelope}
```

The response body MUST be a valid ARSIA message envelope with `intent` set to
`"response"`, `"error"`, `"pending_approval"`, or `"approval_decision"`. The
`correlation_id` field MUST be set to the `id` of the request message
(ARSIA-Core.md §4.2.1).

**Asynchronous acceptance (HTTP 202 Accepted):**

```http
HTTP/2 202 Accepted
Location: https://{host}/v1/arsia/status/{message-id}
Retry-After: 5
Content-Type: application/arsia+json; v=1

{ARSIA response envelope with intent "pending_approval" or receipt}
```

The `Location` header provides a URL where the sender can poll for the eventual
response. The `Retry-After` header indicates the suggested interval (in seconds)
between polling attempts. The response body MAY contain an ARSIA envelope with
`intent` set to `"pending_approval"` or a receipt payload.

**Error responses:**

Error responses use the appropriate HTTP status code mapped from ARSIA error codes as
defined in ARSIA-Core.md §11.2:

| ARSIA Error Code      | HTTP Status | Description                              |
|-----------------------|-------------|------------------------------------------|
| `invalid_request`     | 400         | Malformed or invalid message envelope.   |
| `unauthorized`        | 401         | Invalid token or failed signature.       |
| `forbidden`           | 403         | Insufficient capabilities.               |
| `not_found`           | 404         | Target agent or resource not found.      |
| `conflict`            | 409         | Idempotency key collision.               |
| `payload_too_large`   | 413         | Message exceeds size limit.              |
| `rate_limited`        | 429         | Rate limit exceeded.                     |
| `internal_error`      | 500         | Unexpected server error.                 |
| `not_implemented`     | 501         | Unsupported feature or version.          |
| `service_unavailable` | 503         | Temporary unavailability.                |

The response body MUST be a valid ARSIA error envelope (ARSIA-Core.md §11.1).

#### 2.1.3 TLS Requirements

All ARSIA HTTP connections MUST use TLS to protect message confidentiality and
integrity in transit.

**TLS version requirements:**

- TLS 1.3 [RFC 8446] is REQUIRED. All conformant implementations MUST support TLS 1.3.
- TLS 1.2 MAY be accepted for legacy interoperability, but TLS 1.3 MUST be preferred
  in all protocol negotiations. When a TLS 1.2 connection is used, the receiving agent
  MUST log a compliance warning indicating that a deprecated TLS version was used. The
  log entry MUST include the sender's agent-id, the TLS version negotiated, and the
  timestamp.
- TLS versions prior to 1.2 (i.e., TLS 1.0, TLS 1.1, SSL 3.0, SSL 2.0) MUST NOT be
  accepted. Connections using these versions MUST be refused.

**Certificate requirements:**

- Production deployments MUST use certificates signed by a publicly trusted Certificate
  Authority (CA).
- Development and testing environments MAY use self-signed certificates, but only when
  explicit trust is configured between communicating agents. Self-signed certificates
  MUST NOT be used in production.
- Certificate validation MUST include hostname verification: the certificate's Subject
  Alternative Name (SAN) or Common Name (CN) MUST match the hostname of the inbox URL.

**HTTP Strict Transport Security (HSTS):**

HSTS [RFC 6797] is RECOMMENDED for production deployments. When HSTS is enabled, the
`Strict-Transport-Security` response header SHOULD be set to:

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

This directs clients to use HTTPS for all future requests to this host for one year
and applies the policy to all subdomains.

**Mutual TLS (mTLS):**

mTLS MAY be used for additional transport-level authentication between agents. When
mTLS is used, the server validates the client's certificate during the TLS handshake,
providing an additional assurance of the client's identity beyond the ARSIA message-level
signature and access token.

mTLS does NOT replace ARSIA message-level signatures. Even when mTLS is used, the
sending agent MUST sign the message envelope (ARSIA-Core.md §5.1) and the receiving
agent MUST verify the signature (ARSIA-Core.md §5.2). mTLS provides transport-level
authentication; ARSIA signatures provide message-level authentication. The two
mechanisms operate at different layers and serve complementary purposes.

**Plaintext prohibition:**

Implementations MUST NOT accept plaintext HTTP connections (i.e., connections without
TLS) for any ARSIA endpoint. Attempts to connect via plaintext HTTP MUST be refused.
Implementations SHOULD respond with HTTP 301 (Moved Permanently) redirecting to the
HTTPS equivalent, but MAY also simply close the connection.

#### 2.1.4 HTTP/2 Protocol Requirements

ARSIA requires HTTP/2 as the minimum HTTP version for the primary transport binding.

**Server push:** ARSIA does NOT use HTTP/2 server push. Implementations MUST NOT
initiate server push for ARSIA endpoints.

**Stream multiplexing:** Sending agents MAY send multiple concurrent ARSIA requests on
a single HTTP/2 connection using separate streams. This enables efficient parallel
message delivery without the overhead of establishing multiple TCP connections.
Implementations SHOULD use stream multiplexing when delivering multiple messages to the
same recipient in rapid succession.

**Flow control:** Implementations MUST respect HTTP/2 flow control windows as defined
in [RFC 9113] §6.9. Implementations MUST NOT disable or bypass HTTP/2 flow control.
When a flow control window is exhausted, the sending agent MUST wait for a
WINDOW_UPDATE frame before sending additional data.

**Connection management:** Implementations SHOULD reuse HTTP/2 connections for multiple
message deliveries to the same recipient. Connection pooling is RECOMMENDED. The
maximum number of concurrent streams per connection is governed by the SETTINGS_MAX_
CONCURRENT_STREAMS parameter negotiated during the HTTP/2 handshake; implementations
MUST respect this limit.

**HPACK header compression:** HTTP/2 header compression (HPACK) [RFC 7541] is
mandatory per the HTTP/2 specification. Implementations MUST support HPACK and SHOULD
use it to compress the repetitive ARSIA headers (`Content-Type`, `Accept`,
`Authorization`) across multiple requests on the same connection.

### 2.2 WebSocket Binding (OPTIONAL)

The WebSocket binding provides a persistent bidirectional channel for agents that
exchange high-frequency messages or require real-time event streaming. This section
extends ARSIA-Core.md §8.2 with full normative detail on the connection lifecycle,
authentication, heartbeat, and reconnection procedures.

#### 2.2.1 Connection Endpoint

```
wss://{host}/v1/arsia/stream
```

The WebSocket connection MUST use the `wss://` scheme (TLS-encrypted). Plaintext
`ws://` connections MUST NOT be used for any ARSIA WebSocket communication. The TLS
requirements defined in §2.1.3 apply equally to WebSocket connections.

The WebSocket sub-protocol MUST be declared during the HTTP upgrade handshake:

```http
GET /v1/arsia/stream HTTP/1.1
Host: {recipient-host}
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Protocol: arsia-v1
Sec-WebSocket-Version: 13
```

The server MUST respond with the selected sub-protocol to confirm ARSIA protocol
support:

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Protocol: arsia-v1
```

If the server does not include `Sec-WebSocket-Protocol: arsia-v1` in the upgrade
response, the client MUST close the connection — the server does not support the ARSIA
WebSocket protocol.

#### 2.2.2 Connection Lifecycle

The WebSocket connection lifecycle consists of five phases: handshake, authentication,
messaging, heartbeat, and disconnection.

**Phase 1 — Handshake:**

The client opens a WebSocket connection to the server's stream endpoint using the
upgrade handshake shown in §2.2.1. The handshake follows the standard WebSocket opening
handshake defined in [RFC 6455] §4.

Upon successful upgrade, the connection enters the authentication phase. The client
MUST NOT send any ARSIA messages before completing authentication.

**Phase 2 — Authentication:**

After the WebSocket connection is established, the client MUST authenticate before
sending any ARSIA message envelopes.

The client sends a JSON text frame containing the authentication request:

```json
{
  "type": "auth",
  "token": "Bearer {access_token}"
}
```

For DPoP-bound tokens, the authentication request includes the DPoP proof:

```json
{
  "type": "auth",
  "token": "DPoP {access_token}",
  "dpop_proof": "{dpop_proof_jwt}"
}
```

The `token` field contains the full authorization value including the scheme prefix
(`Bearer` or `DPoP`), consistent with the `Authorization` header format used in the
HTTP/2 binding.

The server validates the token and responds with one of:

**Authentication success:**

```json
{
  "type": "auth_ok",
  "agent_id": "agent:{server.domain}.{server.name}",
  "session_id": "{uuid-v4}"
}
```

The `agent_id` field contains the server's agent identifier. The `session_id` field is
a UUID v4 that uniquely identifies this WebSocket session. The session ID MAY be used
for correlation in audit logs and debugging.

**Authentication failure:**

```json
{
  "type": "auth_error",
  "code": "unauthorized",
  "description": "{human-readable error description}"
}
```

On `auth_error`, the server MUST close the WebSocket connection with close code 4001
(Authentication Failed) within 5 seconds of sending the `auth_error` frame, consistent
with ARSIA-Core.md §8.2. The client MUST NOT send any further frames after receiving
`auth_error`.

**Authentication timeout:** If the client does not send an `auth` frame within 10
seconds of the WebSocket handshake completing, the server MUST close the connection
with close code 4001 (Authentication Failed).

**Phase 3 — Messaging:**

After `auth_ok`, both the client and server may send ARSIA message envelopes as JSON
text frames. Each frame MUST contain a complete, valid ARSIA message envelope. Message
envelopes MUST NOT be fragmented across multiple WebSocket frames — each frame is an
atomic message.

Binary frames are reserved for future use (e.g., encrypted payloads, binary-encoded
envelopes). Agents MUST NOT send binary frames in ARSIA Protocol v1.0. A server
receiving a binary frame SHOULD close the connection with close code 1003 (Unsupported
Data).

The maximum frame size is governed by the agent's `max_message_bytes` value
(ARSIA-Core.md §4.5). Frames exceeding this limit MUST cause the server to close the
connection with close code 4003 (Message Too Large), consistent with ARSIA-Core.md §8.2.

**Phase 4 — Heartbeat:**

The client SHOULD send a heartbeat frame every 30 seconds to maintain the connection
and detect network failures:

```json
{
  "type": "ping"
}
```

The server MUST respond with a heartbeat response within 5 seconds:

```json
{
  "type": "pong"
}
```

If the client does not receive a `pong` within 10 seconds of sending a `ping`, the
client SHOULD consider the connection dead and initiate reconnection (Phase 5).

The server MAY send unsolicited heartbeat requests:

```json
{
  "type": "ping"
}
```

The client MUST respond with a `pong` frame within 5 seconds. If the client does not
respond, the server SHOULD close the connection with close code 4002 (Idle Timeout),
consistent with ARSIA-Core.md §8.2.

Heartbeat frames are distinct from WebSocket protocol-level Ping/Pong frames
([RFC 6455] §5.5.2, §5.5.3). Both mechanisms MAY be used concurrently. The ARSIA
application-level heartbeat provides visibility to the application layer, while
WebSocket protocol-level pings operate at the framing layer.

**Phase 5 — Disconnection:**

**Graceful disconnection:** Either side may initiate a graceful close by sending a
WebSocket close frame with close code 1000 (Normal Closure). The closing party SHOULD
NOT send any further messages after initiating the close. The receiving party MUST
respond with a close frame per [RFC 6455] §5.5.1.

**Reconnection:** When a WebSocket connection is lost (due to network failure, server
error, or idle timeout), the client MUST implement exponential backoff for reconnection:

| Parameter         | Value                                        |
|-------------------|----------------------------------------------|
| Base delay        | 1 second                                     |
| Multiplier        | 2×                                           |
| Maximum delay     | 30 seconds                                   |
| Jitter            | ±25% of computed delay (RECOMMENDED)         |
| Maximum attempts  | Implementation-defined (RECOMMENDED: unlimited with backoff) |

Reconnection delay schedule:

| Attempt | Delay (without jitter) | Delay (with ±25% jitter)  |
|---------|------------------------|---------------------------|
| 1       | 1 second               | 0.75 – 1.25 seconds       |
| 2       | 2 seconds              | 1.50 – 2.50 seconds       |
| 3       | 4 seconds              | 3.00 – 5.00 seconds       |
| 4       | 8 seconds              | 6.00 – 10.00 seconds      |
| 5       | 16 seconds             | 12.00 – 20.00 seconds     |
| 6+      | 30 seconds             | 22.50 – 37.50 seconds     |

Jitter is RECOMMENDED to prevent the thundering herd effect when many clients reconnect
simultaneously after a server outage. The jitter formula is:

```
actual_delay = computed_delay × (0.75 + random() × 0.5)
```

where `random()` returns a uniform random value in [0, 1).

Upon reconnection, the client MUST re-authenticate (Phase 2). The server MUST NOT
assume that a reconnected client has the same authentication state as a previous
connection. The session ID from the prior connection is invalid.

**Idle timeout:** The server MAY close WebSocket connections that have not exchanged any
frames (including heartbeats) for 60 seconds. The server SHOULD use close code 4002
(Idle Timeout) for idle timeout closures, consistent with ARSIA-Core.md §8.2.

#### 2.2.3 WebSocket Close Codes

The following WebSocket close codes are used by the ARSIA WebSocket binding:

| Code | Name                | Usage                                          |
|------|---------------------|------------------------------------------------|
| 1000 | Normal Closure      | Graceful disconnection.                        |
| 1001 | Going Away          | Server shutdown or unrecoverable error.        |
| 1003 | Unsupported Data    | Binary frame received (not supported in v1.0). |
| 4001 | Authentication Failed | Authentication failure or authentication timeout (ARSIA-Core.md §8.2). |
| 4002 | Idle Timeout        | No frames exchanged within 60 seconds, or client pong timeout (ARSIA-Core.md §8.2). |
| 4003 | Message Too Large   | Frame exceeds `max_message_bytes` (ARSIA-Core.md §8.2). |

Implementations MAY use additional standard WebSocket close codes as defined in
[RFC 6455] §7.4.1 for situations not covered above.

### 2.3 Broker Relay Transport

When routing is brokered (§1.2.2), the transport-level behaviour between the sender,
broker, and recipient follows a specific pattern. This section defines the relay
transport semantics.

#### 2.3.1 Sender-to-Broker Transport

The sender sends the message to the broker's inbox using the standard HTTP/2 binding
(§2.1). The request format is identical to a direct routing request — the sender does
NOT modify the message envelope for broker relay. The only difference is the target URL:
the POST is directed to the broker's inbox URL rather than the recipient's inbox URL.

The `to` field in the message envelope MUST contain the final recipient's agent-id, not
the broker's agent-id. The broker uses this field to determine where to forward the
message.

The `Authorization` header MUST contain a token that authorises the sender to use the
broker's `arsiaprotocol.broker.relay` capability.

#### 2.3.2 Broker-to-Recipient Transport

The broker forwards the message to the recipient's inbox using direct routing (§1.2.1,
§2.1). The broker:

1. Resolves the recipient's inbox URL from the discovery endpoint
   (ARSIA-Core.md §7.1).
2. Obtains an access token for the recipient from an authorization server.
3. Sends the message to the recipient's inbox via HTTP POST.
4. The message envelope is forwarded byte-identical (after JSON canonicalization) — the
   broker does NOT re-sign the message.

#### 2.3.3 Broker Response Handling

The broker responds to the sender with one of the following:

**Synchronous response relay:**

If the recipient responds synchronously (HTTP 200), the broker forwards the
recipient's response envelope to the sender unmodified. The response MUST pass through
the broker without alteration.

**Asynchronous relay receipt:**

If the recipient responds asynchronously (HTTP 202) or the broker itself processes the
relay asynchronously, the broker returns a relay receipt to the sender:

```json
{
  "v": "1.0",
  "id": "{uuid}",
  "ts": "{timestamp}",
  "from": "{broker-agent-id}",
  "to": "{sender-agent-id}",
  "intent": "response",
  "correlation_id": "{original-message-id}",
  "payload": {
    "type": "arsiaprotocol.broker/relay-receipt",
    "result": {
      "relay_id": "{uuid}",
      "status": "forwarded",
      "recipient_status_url": "{recipient-status-url-if-available}"
    }
  }
}
```

**Relay error:**

If the broker cannot forward the message to the recipient (network failure, recipient
error, timeout), the broker returns a standard ARSIA error envelope to the sender:

```json
{
  "v": "1.0",
  "id": "{uuid}",
  "ts": "{timestamp}",
  "from": "{broker-agent-id}",
  "to": "{sender-agent-id}",
  "intent": "error",
  "correlation_id": "{original-message-id}",
  "payload": {
    "type": "arsiaprotocol.broker/relay-error",
    "error": {
      "code": "service_unavailable",
      "description": "Failed to relay message to recipient.",
      "details": {
        "relay_failed": true,
        "relay_id": "{uuid}",
        "original_error": {
          "code": "{recipient-error-code}",
          "description": "{recipient-error-description}"
        }
      }
    }
  }
}
```

#### 2.3.4 Broker Timeout

The broker MUST forward the message to the recipient within 10 seconds of receiving it
from the sender. This 10-second window covers the time from message receipt to the
initiation of the HTTP POST to the recipient.

Additionally, the broker MUST respect the message's `expires_at` field. If the
recipient does not respond before `expires_at` minus 5 seconds (a safety margin to
account for network latency on the return path), the broker MUST abandon the relay and
return a `service_unavailable` error to the sender with details:

```json
{
  "relay_failed": true,
  "reason": "relay_timeout",
  "relay_id": "{uuid}",
  "expires_at": "{message-expires_at}",
  "timeout_at": "{expires_at - 5 seconds}"
}
```

This safety margin ensures that the sender receives the timeout error before the
message's expiration, allowing the sender to take appropriate action (e.g., retry with
a different broker, abort the operation).

---

## 3. Delivery Guarantees

ARSIA Protocol defines three delivery guarantee levels. The guarantees are end-to-end
properties that apply regardless of whether the message is delivered via direct or
brokered routing.

### 3.1 At-Most-Once Delivery (Default)

At-most-once delivery is the default guarantee. Messages are delivered zero or one
times. There is no automatic redelivery on failure.

**Semantics:**

- The sender transmits the message to the recipient (or broker).
- The sender receives either a response (HTTP 200/202) or an error (HTTP 4xx/5xx).
- If the connection drops before a response is received, the message MAY have been
  processed by the recipient. The sender has no way to determine the outcome without
  application-level mechanisms.
- The sender does NOT retry automatically.

**Failure modes:**

- Network failure before request arrives: message is not delivered.
- Network failure after request arrives but before response: message may or may not
  have been processed. The sender cannot distinguish between these cases.
- Server error: message was received but processing failed.

**Appropriate use cases:**

- Idempotent queries (e.g., read-only data retrieval).
- Informational events where loss is acceptable.
- Non-critical notifications.
- Situations where the sender prefers simplicity over delivery assurance.

**No idempotency key required:** At-most-once delivery does not require the sender to
provide an idempotency key. However, providing one does not change the delivery
guarantee — it only enables deduplication if the sender chooses to retry manually.

### 3.2 At-Least-Once Delivery (Opt-In)

At-least-once delivery is achieved by the sender retrying failed requests with the SAME
idempotency key. The receiving agent MUST deduplicate based on the idempotency key, as
specified in ARSIA-Core.md §10.

**Semantics:**

- The sender provides an idempotency key (via the `idempotency.key` envelope field or
  the `Idempotency-Key` HTTP header, per ARSIA-Core.md §10.1).
- On failure (5xx error, network timeout, or connection drop), the sender retries the
  EXACT same message (same `id`, same `idempotency.key`) using the retry policy defined
  in ARSIA-Core.md §11.3.
- The receiving agent checks the idempotency key: if the key has already been
  processed, the agent returns the stored response without re-executing the request
  (ARSIA-Core.md §10.3).
- The message is guaranteed to be delivered at least once, assuming at least one retry
  succeeds within the retry budget.

**Retry procedure (normative):**

The sender MUST follow this procedure when implementing at-least-once delivery:

1. Send the message with an idempotency key.
2. If the response is a success (HTTP 200/202): delivery is confirmed. Stop.
3. If the response is a non-retryable error (HTTP 400, 401, 403, 404, 409, 413, 501):
   delivery failed permanently. Do NOT retry. Stop.
4. If the response is HTTP 429 (rate limited): wait for the duration specified in the
   `Retry-After` header (or `payload.error.details.retry_after_seconds`, or 60 seconds
   as fallback). Then retry.
5. If the response is a retryable error (HTTP 500, 503) or a network failure: wait
   according to the exponential backoff schedule defined in ARSIA-Core.md §11.3.
6. Resend the EXACT same message — same `id`, same `idempotency.key`, same envelope
   contents.
7. The server checks the idempotency key: if the key matches a previously processed
   request, the server returns the stored response (ARSIA-Core.md §10.3).
8. Maximum retries: 3 (RECOMMENDED). After 3 failed retries, the sender MUST abandon
   the request and report the failure to its caller, including the error code and
   description from the most recent attempt.

**Appropriate use cases:**

- State-changing operations where the receiver guarantees idempotent handling.
- Financial transactions (when combined with application-level deduplication).
- Critical events where loss is unacceptable.

### 3.3 Exactly-Once Delivery

Exactly-once delivery is NOT guaranteed at the protocol level. ARSIA Protocol does not
implement distributed transactions, two-phase commit, or any other distributed
consensus mechanism.

**Application-level exactly-once:**

Applications can achieve exactly-once semantics by combining at-least-once delivery
(§3.2) with idempotent receivers. The ARSIA idempotency mechanism (ARSIA-Core.md §10)
provides the building block: it ensures that duplicate deliveries of the same message
(identified by the same idempotency key) produce the same response without
re-executing the request.

However, "exactly-once" in the application sense means more than just deduplication — it
means that the side effects of processing the message occur exactly once. This requires
the application to ensure that:

1. The idempotency key is correctly scoped to the operation (not just the message).
2. The processing logic is truly idempotent: processing a duplicate has no additional
   side effects beyond returning the stored response.
3. The idempotency key storage and the business logic state change are committed
   atomically (e.g., in the same database transaction).

These guarantees are application-level concerns that are beyond the scope of the ARSIA
Protocol. The protocol provides the mechanism (idempotency keys, deduplication); the
application provides the semantics (idempotent processing, atomic state changes).

---

## 4. Message Routing Lifecycle

Every ARSIA message progresses through a series of lifecycle states from construction
to final disposition. This section defines each state, its entry and exit conditions,
associated timeouts, and audit events.

### 4.1 Lifecycle States

The following states define the lifecycle of an ARSIA message from the perspective of
the routing system. States are tracked locally by each party involved in message
delivery (sender, broker, recipient). There is no shared global state.

#### 4.1.1 CREATED

**Definition:** The message object has been constructed in memory by the sending agent.
The message exists as an in-memory data structure but has not yet been signed or
dispatched.

| Property      | Value                                                        |
|---------------|--------------------------------------------------------------|
| Entry condition | Message object constructed with all required fields.       |
| Exit condition  | Message signed → transitions to SIGNED.                    |
| Timeout         | None (local in-memory state).                              |
| Audit event     | None.                                                      |

**Notes:** This is a transient, local state. It exists only within the sending agent's
process. No network communication occurs in this state.

#### 4.1.2 SIGNED

**Definition:** The message has been signed by the sending agent. The `security.sig`
field has been populated with the Ed25519 signature computed over the RFC 8785 canonical
form of the message (ARSIA-Core.md §5.1).

| Property      | Value                                                        |
|---------------|--------------------------------------------------------------|
| Entry condition | `security.sig` field populated with valid signature.       |
| Exit condition  | HTTP POST initiated → transitions to DISPATCHED.           |
| Timeout         | None (local in-memory state).                              |
| Audit event     | None.                                                      |

**Notes:** After signing, the message envelope is immutable. Any modification to the
envelope would invalidate the signature. The signed message is ready for dispatch.

#### 4.1.3 DISPATCHED

**Definition:** The HTTP request carrying the signed message has been sent to the
recipient's inbox (for direct routing) or to the broker's inbox (for brokered routing).
The sending agent is waiting for an HTTP response.

| Property      | Value                                                        |
|---------------|--------------------------------------------------------------|
| Entry condition | HTTP POST request sent to target inbox.                    |
| Exit conditions | HTTP response received → transitions to DELIVERED or DELIVERY_FAILED. Network failure or timeout → transitions to DISPATCH_FAILED. Message expires → transitions to EXPIRED. |
| Timeout         | `request_timeout_ms` from recipient's discovery metadata (default: 30,000 ms per ARSIA-Core.md §8.3). |
| Audit event     | Sender logs `dispatch` event with message ID, target agent-id, topology (direct or brokered), and timestamp. |

**Notes:** During DISPATCHED state, the message is in flight. The sender has no control
over the message — it is being processed by the network stack and the receiving agent.

#### 4.1.4 BROKER_RELAYED (Brokered Routing Only)

**Definition:** The Compliance Broker has received the message from the sender, verified
the sender's signature, verified residency zone compliance, and forwarded the message
to the recipient's inbox. The broker is waiting for the recipient's response.

| Property      | Value                                                        |
|---------------|--------------------------------------------------------------|
| Entry condition | Broker received the message, validated it, and forwarded to recipient. |
| Exit conditions | Recipient response received by broker → transitions to DELIVERED. Forwarding fails → transitions to DISPATCH_FAILED. Message expires → transitions to EXPIRED. |
| Timeout         | `expires_at` from message minus 5 seconds (safety margin, per §2.3.4). |
| Audit event     | Broker logs `broker_relay` event with relay ID, message ID, sender agent-id, recipient agent-id, broker agent-id, residency zone, relay timestamp, and payload hash. |

**Notes:** This state exists only in brokered routing. In direct routing, the message
transitions directly from DISPATCHED to DELIVERED without passing through this state.
The broker's audit event is the authoritative record that the message was relayed within
the declared data residency zone.

#### 4.1.5 DELIVERED

**Definition:** The recipient has received the message and acknowledged receipt. For
synchronous processing, this means the recipient returned HTTP 200 OK. For asynchronous
processing, this means the recipient returned HTTP 202 Accepted.

| Property      | Value                                                        |
|---------------|--------------------------------------------------------------|
| Entry condition | Recipient returned HTTP 200 OK or HTTP 202 Accepted.      |
| Exit condition  | Response sent back to sender → transitions to RESPONDED.   |
| Timeout         | None (the response is being transmitted).                  |
| Audit event     | Recipient logs `request_received` event with message ID, sender agent-id, and timestamp. |

**Notes:** DELIVERED indicates that the recipient has taken ownership of the message.
The message has been received, its signature verified, its token validated, and its
processing initiated (for 200) or queued (for 202).

#### 4.1.6 RESPONDED

**Definition:** The response envelope has been sent from the recipient back to the
sender (directly, or via the broker for brokered routing). This is a terminal state for
successfully processed messages.

| Property      | Value                                                        |
|---------------|--------------------------------------------------------------|
| Entry condition | Response envelope transmitted to sender (or broker).       |
| Exit condition  | Terminal state.                                            |
| Audit event     | Recipient logs `response_sent` event with message ID, correlation ID, response intent, and timestamp. |

**Notes:** Once a message reaches RESPONDED, its lifecycle is complete. The
idempotency key (if any) remains stored for the duration specified by
`idempotency.expires_at` to handle late-arriving duplicate requests.

#### 4.1.7 DISPATCH_FAILED

**Definition:** The HTTP request failed due to a network error, TCP connection failure,
TLS handshake failure, DNS resolution failure, or HTTP timeout. The sending agent did
not receive an HTTP response from the target (recipient or broker).

| Property      | Value                                                        |
|---------------|--------------------------------------------------------------|
| Entry condition | Network failure or timeout during HTTP request.            |
| Exit conditions | Retry initiated → back to DISPATCHED. Max retries exceeded → terminal state. |
| Timeout         | Retry delay per ARSIA-Core.md §11.3.                      |
| Audit event     | Sender logs `dispatch_failed` event with message ID, target agent-id, failure reason, retry count, and timestamp. |

**Notes:** DISPATCH_FAILED is retryable. The sender MAY retry the request using the
exponential backoff schedule defined in ARSIA-Core.md §11.3, transitioning back to
DISPATCHED. After the maximum number of retries (3 RECOMMENDED), the state becomes
terminal. When retrying, the sender MUST use the same message (same `id`, same
`idempotency.key` if present) to enable server-side deduplication.

#### 4.1.8 DELIVERY_FAILED

**Definition:** The recipient (or broker) returned an HTTP error response (4xx or 5xx
status code). The message was delivered to the target but was rejected or could not be
processed.

| Property      | Value                                                        |
|---------------|--------------------------------------------------------------|
| Entry condition | Recipient or broker returned HTTP 4xx or 5xx error response. |
| Exit conditions | Terminal state (for non-retryable errors). Retry initiated → back to DISPATCHED (for retryable errors per ARSIA-Core.md §11.3). |
| Timeout         | Retry delay per ARSIA-Core.md §11.3, if retryable.        |
| Audit event     | Sender logs `delivery_failed` event with message ID, target agent-id, HTTP status code, ARSIA error code, and timestamp. |

**Notes:** Whether DELIVERY_FAILED is terminal depends on the error code. Errors
`rate_limited` (429), `internal_error` (500), and `service_unavailable` (503) are
retryable per ARSIA-Core.md §11.3. All other errors (400, 401, 403, 404, 409, 413,
501) are non-retryable — the sender MUST NOT retry without modifying the request.

#### 4.1.9 EXPIRED

**Definition:** The current time has exceeded the message's `expires_at` timestamp
before the message reached the DELIVERED state. The message MUST NOT be processed.

| Property      | Value                                                        |
|---------------|--------------------------------------------------------------|
| Entry condition | Current time exceeds `message.expires_at` (after ±300s clock skew tolerance per ARSIA-Core.md §8.3) before DELIVERED. |
| Exit condition  | Terminal state. Message MUST NOT be processed.             |
| Audit event     | Sender logs `expired` event with message ID, `expires_at` value, and timestamp of expiration detection. |

**Notes:** A message that expires while in DISPATCHED or BROKER_RELAYED state MUST be
treated as failed. If the recipient receives an expired message (i.e., a message whose
`expires_at` is in the past), the recipient MUST reject it with error code
`invalid_request` (ARSIA-Core.md §11.2). Expiration is a safety mechanism that prevents
stale requests from being executed and bounds the window for replay attacks.

### 4.2 State Transition Diagram

The following ASCII diagram shows all valid state transitions for an ARSIA message:

```
                    +---------+
                    | CREATED |
                    +----+----+
                         | sign
                         v
                    +----------+
                    |  SIGNED  |
                    +-----+----+
                          | dispatch (HTTP POST)
                          v
                    +------------+
              +-----| DISPATCHED |-----------------------------+
              |     +-----+------+                             |
              |           |                                    |
              |         +-+-----------------+                  |
              |         |                   |                  |
              |         v                   v                  v
              |  +--------------+  +-----------------+  +------------+
              |  |   DELIVERED  |  | BROKER_RELAYED  |  |  EXPIRED   |
              |  +------+-------+  | (brokered only) |  | (terminal) |
              |         |          +--------+--------+  +------------+
              |         |                   |
              |         |                   +
              |         |                   v
              |         |            +--------------+
              |         |            |   DELIVERED  |
              |         |            +------+-------+
              |         |                   |
              |         v                   v
              |   +------------+     +------------+
              |   | RESPONDED  |     | RESPONDED  |
              |   | (terminal) |     | (terminal) |
              |   +------------+     +------------+
              |
              +------------------------------+
              |                              |
              v                              v
     +-----------------+            +-----------------+
     | DISPATCH_FAILED |            | DELIVERY_FAILED |
     +--------+--------+            +--------+--------+
              |                              |
         +----+----+                    +----+----+
         |         |                    |         |
         v         v                    v         v
    (retry ->   (terminal)         (retry ->   (terminal)
    DISPATCHED)                    DISPATCHED)
```

**Transition summary:**

| From              | To                | Trigger                                       |
|-------------------|-------------------|-----------------------------------------------|
| CREATED           | SIGNED            | Message signed (security.sig populated).      |
| SIGNED            | DISPATCHED        | HTTP POST request initiated.                  |
| DISPATCHED        | DELIVERED         | HTTP 200/202 received (direct routing).       |
| DISPATCHED        | BROKER_RELAYED    | Broker accepted and forwarded (brokered routing). |
| DISPATCHED        | DISPATCH_FAILED   | Network failure or timeout.                   |
| DISPATCHED        | DELIVERY_FAILED   | HTTP 4xx/5xx error response.                  |
| DISPATCHED        | EXPIRED           | `expires_at` exceeded before delivery.        |
| BROKER_RELAYED    | DELIVERED         | Recipient responded to broker.                |
| BROKER_RELAYED    | DISPATCH_FAILED   | Broker failed to forward to recipient.        |
| BROKER_RELAYED    | EXPIRED           | `expires_at` exceeded during relay.           |
| DELIVERED         | RESPONDED         | Response envelope transmitted.                |
| DISPATCH_FAILED   | DISPATCHED        | Retry initiated (retryable failure).          |
| DISPATCH_FAILED   | (terminal)        | Max retries exceeded.                         |
| DELIVERY_FAILED   | DISPATCHED        | Retry initiated (retryable error code).       |
| DELIVERY_FAILED   | (terminal)        | Non-retryable error or max retries exceeded.  |
| EXPIRED           | (terminal)        | Message expired. No further processing.       |
| RESPONDED         | (terminal)        | Lifecycle complete.                           |

---

## 5. Data Residency in Routing

Data residency is the mechanism by which ARSIA ensures that message processing occurs
within a specified geographic region. This section defines how residency requirements
are declared, how they affect routing, and how residency compliance is verified.

### 5.1 Declaring Residency Requirements

The `compliance.data_residency` field in the message envelope (ARSIA-Core.md §4.3.6)
declares where message processing MUST occur.

**Field specification:**

| Property    | Value                                                        |
|-------------|--------------------------------------------------------------|
| Field path  | `compliance.data_residency`                                  |
| Type        | string                                                       |
| Format      | ISO 3166-1 alpha-2 country code or recognised regional code. |
| Presence    | OPTIONAL. When present and non-empty, brokered routing is REQUIRED. |

**Accepted values:**

- **Country codes (ISO 3166-1 alpha-2):** Two-letter codes identifying specific
  countries. Examples: `"PT"` (Portugal), `"DE"` (Germany), `"FR"` (France), `"IE"`
  (Ireland), `"NL"` (Netherlands).

- **Regional codes:** Identifiers for supranational regions. Currently recognised
  regional codes:

  | Code | Region                                    | Member states                      |
  |------|-------------------------------------------|------------------------------------|
  | `"EU"` | European Union / European Economic Area | All EU/EEA member states.          |

  This list is informative, not exhaustive. Implementations MAY define additional
  regional codes for their specific use cases. Custom regional codes SHOULD use
  uppercase alphabetic strings of 2-4 characters to avoid conflict with ISO 3166-1
  country codes.

**Effects of setting `data_residency`:**

When `data_residency` is set to a non-empty value:

1. **Routing:** The message MUST be routed through a Compliance Broker within the
   declared zone (§1.2.2).

2. **Broker location:** The broker's physical servers MUST reside within the declared
   zone. "Physical servers" means the hardware and virtualisation infrastructure that
   processes the message — not merely the legal entity's registration jurisdiction.

3. **Audit log storage:** Audit logs generated for this message MUST be stored within
   the declared zone. This applies to audit logs at the sender, broker, and recipient.

4. **Recipient processing:** The recipient's processing infrastructure SHOULD be within
   the declared zone. This is the recipient's responsibility and is not enforced by the
   routing protocol. However, if the recipient is subject to the same regulatory
   requirements (e.g., GDPR), the recipient has its own obligation to ensure compliant
   processing.

### 5.2 EU Data Residency

The most common data residency configuration in the ARSIA Protocol is
`data_residency: "EU"`. This section provides specific guidance for EU data residency.

**When `data_residency` = `"EU"`:**

1. **Processing location.** All message processing — including reception, signature
   verification, token validation, payload processing, response generation, and
   temporary storage — MUST occur within servers physically located in an EU or EEA
   member state.

2. **Broker location.** The Compliance Broker MUST be physically located in an EU/EEA
   member state. The broker's `IdentityRecord.jurisdiction` MUST be an ISO 3166-1
   alpha-2 code of an EU/EEA member state (e.g., `"PT"`, `"DE"`, `"IE"`, `"NL"`).

3. **Audit log storage.** Audit logs generated for this message MUST be stored in
   servers physically located in an EU/EEA member state. This includes the broker's
   relay audit record (§7.4) and the recipient's processing audit record.

4. **GDPR Chapter V compliance.** When both the sender and recipient process the
   message within the EU/EEA, no international data transfer occurs under GDPR
   Chapter V. This means no Standard Contractual Clauses (SCCs), Binding Corporate
   Rules (BCRs), or adequacy decisions are needed for the message processing itself.

**Cross-border considerations:**

If the sender is located outside the EU but the message declares
`data_residency: "EU"`, the broker ensures that all processing after receipt occurs
within the EU. The sender is responsible for having a lawful basis for the initial
transfer of message data TO the EU. Under GDPR, restrictions apply to transfers of
personal data OUT of the EU/EEA, not to transfers INTO the EU/EEA. Therefore, the
initial transfer from a non-EU sender to an EU broker is generally permissible from
the GDPR perspective.

However, the sender MUST be aware that:

- The response from the recipient (relayed back through the broker) will exit the
  EU when it reaches the non-EU sender. If the response contains personal data, the
  sender must have an appropriate transfer mechanism in place (SCCs, adequacy decision,
  etc.).
- The message payload, if it contains personal data originating outside the EU, may
  be subject to the data protection laws of the sender's jurisdiction in addition to
  GDPR.

**EU/EEA member state verification:**

A jurisdiction code satisfies the `"EU"` regional zone if and only if the corresponding
country is a current member of the European Union or the European Economic Area. As of
March 2026, this includes the 27 EU member states plus Iceland, Liechtenstein, and
Norway (EEA members). Switzerland is NOT an EU/EEA member state and does NOT satisfy
the `"EU"` zone, despite its geographic proximity and certain bilateral agreements with
the EU.

Implementations MUST maintain an up-to-date list of EU/EEA member states. Changes to
EU/EEA membership (e.g., new accessions) SHOULD be reflected in implementations within
90 days of the effective date of the membership change.

### 5.3 Residency Verification

This section defines how a sender verifies that a broker is genuinely located within
the required data residency zone.

**Verification procedure:**

1. **Retrieve the broker's IdentityRecord.** The sender issues a GET request to the
   broker's identity endpoint:

   ```
   GET {broker-host}/.well-known/arsia/identity
   ```

   The response is an IdentityRecord as defined in ARSIA-Identity.md §1.2.

2. **Check jurisdiction.** The sender verifies that the `jurisdiction` field in the
   broker's IdentityRecord matches the required zone. Matching rules:

   - For a country code zone (e.g., `"PT"`): the broker's `jurisdiction` MUST equal the
     zone exactly.
   - For the `"EU"` regional zone: the broker's `jurisdiction` MUST be an ISO 3166-1
     alpha-2 code of a current EU/EEA member state.

3. **Verify the IdentityRecord signature.** The sender verifies the `X-ARSIA-Sig`
   header on the identity response, following the procedure defined in
   ARSIA-Identity.md §1.3. This ensures that the IdentityRecord was produced by the
   broker itself and has not been tampered with.

4. **Optional: TLS certificate geographic verification.** The sender MAY additionally
   verify the broker's TLS certificate for geographic metadata. The `Subject` field of
   the certificate may include a `C=` (Country) attribute that indicates the
   certificate holder's country. If present, this attribute SHOULD be consistent with
   the broker's declared jurisdiction. This check is informational — TLS certificate
   geographic metadata is not a reliable indicator of physical server location.

**Trust model:**

The residency verification procedure defined above is trust-based. ARSIA Protocol does
not define a mechanism to physically audit the location of a broker's servers. The
sender trusts the broker's IdentityRecord declaration and the signature that
authenticates it.

In regulated deployments, additional assurance mechanisms are RECOMMENDED:

- **Independent audit attestations.** Brokers SHOULD provide SOC 2 Type II reports (or
  equivalent) with geographic scope that covers their declared residency zone.
- **Cloud provider region attestations.** Brokers running on public cloud infrastructure
  SHOULD reference the cloud provider's region identifiers (e.g., `eu-west-1`,
  `eu-central-1`) and the provider's published geographic information for those regions.
- **Regulatory registrations.** Brokers operating in regulated industries SHOULD be
  registered with the relevant national supervisory authority in their jurisdiction.

These additional attestations are out of scope for the ARSIA Protocol but are strongly
recommended for production deployments in compliance-sensitive environments.

---

## 6. Rate Limiting

Rate limiting protects agents from being overwhelmed by excessive message traffic. This
section defines how agents advertise rate limits, communicate rate limit status, and
handle priority-based message scheduling.

### 6.1 Rate Limit Advertisement

Agents advertise their rate limits in the discovery response (ARSIA-Core.md §7.1)
via the `rate_limits` object:

```json
{
  "rate_limits": {
    "requests_per_minute": 120,
    "burst_size": 20
  }
}
```

| Field                | Type    | Description                                      |
|----------------------|---------|--------------------------------------------------|
| `requests_per_minute`| integer | Maximum sustained request rate per minute.       |
| `burst_size`         | integer | Maximum number of requests in a burst above the sustained rate. |

**Semantics:**

- `requests_per_minute` defines the sustained rate over a sliding or fixed window. The
  agent MUST accept at least this many requests per minute under normal conditions.
- `burst_size` defines the maximum burst that may exceed the sustained rate. The agent
  SHOULD accept up to `burst_size` additional requests within a short window (e.g., 1
  second) before enforcing rate limiting.

**Advertisement is informational:** The rate limit values in the discovery response are
informational. They inform senders of the agent's rate limiting policy so that senders
can throttle proactively. The actual enforcement is performed by the receiving agent as
described in §6.2.

### 6.2 Rate Limit Response Headers

On every HTTP response, agents SHOULD include rate limit headers to inform the sender
of the current rate limit status:

| Header                | Type    | Description                                    |
|-----------------------|---------|------------------------------------------------|
| `X-RateLimit-Limit`    | integer | Maximum requests allowed per rate limit window. |
| `X-RateLimit-Remaining`| integer | Number of requests remaining in the current window. |
| `X-RateLimit-Reset`    | integer | Unix timestamp (seconds since epoch) when the current window resets. |

Example response headers:

```http
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1711267260
```

**Rate limit exceeded (HTTP 429):**

When a sender exceeds the agent's rate limit, the agent MUST respond with HTTP 429
(Too Many Requests) and MUST include:

- The `Retry-After` header (integer, seconds until retry is allowed). This header is
  REQUIRED on 429 responses.
- A standard ARSIA error envelope in the response body with error code `rate_limited`
  (ARSIA-Core.md §11.2).

Example 429 response:

```http
HTTP/2 429 Too Many Requests
Retry-After: 30
Content-Type: application/arsia+json; v=1
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1711267260

{
  "v": "1.0",
  "id": "...",
  "ts": "...",
  "from": "agent:target.service",
  "to": "agent:sender.service",
  "intent": "error",
  "correlation_id": "...",
  "payload": {
    "type": "arsiaprotocol.error",
    "error": {
      "code": "rate_limited",
      "description": "Rate limit exceeded. Please retry after 30 seconds.",
      "details": {
        "retry_after_seconds": 30,
        "limit": 120,
        "remaining": 0,
        "reset_at": "2026-03-24T14:31:00.000Z"
      }
    }
  }
}
```

### 6.3 Priority Routing

ARSIA supports priority-based message scheduling via the `X-Request-Priority` header
(§2.1.1) and the `context.priority` field in the message envelope
(ARSIA-Core.md §4.3.3).

**Priority values:**

| Value | Classification | Description                                    |
|-------|---------------|------------------------------------------------|
| 0     | Background    | Batch operations, low-priority maintenance.    |
| 1-2   | Low           | Deferred processing, non-urgent notifications. |
| 3-4   | Below normal  | Standard operations with lower urgency.        |
| 5     | Normal        | Default priority. Used when no priority is specified. |
| 6-7   | Above normal  | Time-sensitive operations.                     |
| 8-9   | High          | Urgent operations requiring prompt processing. |
| 10    | Urgent        | Interactive, real-time operations.             |

**Semantics:**

- Higher priority values MAY be processed before lower priority values in the inbox
  queue.
- Priority MUST NOT affect correctness. A message at priority 0 MUST produce the same
  result as an identical message at priority 10 — priority affects only scheduling
  order.
- Implementations SHOULD honour priority for distinguishing interactive workloads
  (priority 8-10) from batch workloads (priority 0-2).
- Implementations MUST NOT starve low-priority messages indefinitely. All messages MUST
  eventually be processed or expired, regardless of priority. Implementations SHOULD
  implement aging: messages that have been queued for a long time SHOULD have their
  effective priority increased to prevent indefinite starvation.

**Priority source precedence:**

When both the `X-Request-Priority` header and the `context.priority` field are present:
- The `X-Request-Priority` header value takes precedence.
- If the values differ, the server SHOULD use the header value and MAY log the
  discrepancy.

When neither is present, the default priority is 5 (normal).

---

## 7. Broker Specification

This section provides the complete specification for ARSIA Compliance Brokers. A
Compliance Broker is a specialised ARSIA agent that relays messages between other agents
to enforce data residency constraints.

### 7.1 Broker Identity Requirements

A Compliance Broker is a standard ARSIA agent with the following additional requirements:

1. **Capability declaration.** The broker MUST declare the capability
   `arsiaprotocol.broker.relay` in its `capabilities_supported` array in the discovery response
   (ARSIA-Core.md §7.1).

2. **Identity endpoint.** The broker MUST publish its IdentityRecord at
   `/.well-known/arsia/identity` as defined in ARSIA-Identity.md §1.3. The
   IdentityRecord MUST be signed with the broker's Ed25519 key.

3. **Jurisdiction declaration.** The broker's `IdentityRecord.jurisdiction` field MUST
   accurately reflect the broker's physical location. The jurisdiction MUST be the
   ISO 3166-1 alpha-2 country code of the country where the broker's physical servers
   are located. If the broker operates across multiple countries, the jurisdiction MUST
   be the country where the primary message processing occurs.

4. **HTTP/2 support.** The broker MUST support the HTTP/2 transport binding (§2.1) for
   both receiving messages from senders and forwarding messages to recipients.

5. **WebSocket support.** The broker SHOULD support the WebSocket binding (§2.2) for
   long-lived relay connections where senders need to relay multiple messages in rapid
   succession. WebSocket support is OPTIONAL.

6. **Discovery endpoint.** The broker MUST expose a standard ARSIA discovery endpoint
   at `/.well-known/arsia` per ARSIA-Core.md §7.1. The discovery response MUST include
   `arsiaprotocol.broker.relay` in the `capabilities_supported` array.

7. **JWKS endpoint.** The broker MUST expose its public keys at
   `/.well-known/arsia/jwks.json` per ARSIA-Core.md §7.3.

8. **Audit capability.** The broker MUST be capable of generating and storing audit
   records for every message it relays (§7.3, §7.4).

### 7.2 Broker Discovery Endpoint

Broker discovery is the mechanism by which senders find eligible brokers for a specific
data residency zone. The broker discovery endpoint is:

```
GET /.well-known/arsia/brokers?residency={zone}
```

**Query parameters:**

| Parameter    | Type   | Required | Description                               |
|-------------|--------|----------|-------------------------------------------|
| `residency` | string | REQUIRED | The data residency zone to filter by.     |

**Response:**

The response is a JSON array of `BrokerEntry` objects. Each object represents one
eligible broker:

```json
[
  {
    "agent_id": "agent:arsialabs.broker.eu-west",
    "inbox": "https://eu-west.broker.arsia.example/v1/arsia/inbox",
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

**BrokerEntry fields:**

| Field               | Type    | Required    | Description                              |
|--------------------|---------|-------------|------------------------------------------|
| `agent_id`         | string  | REQUIRED    | The broker's agent identifier (ARSIA-Core.md §3). |
| `inbox`            | string  | REQUIRED    | The absolute URL of the broker's inbox endpoint. |
| `jurisdiction`     | string  | REQUIRED    | ISO 3166-1 alpha-2 code of the broker's physical location. |
| `residency_zones`  | array   | REQUIRED    | Array of zone codes this broker serves (e.g., `["EU"]`, `["PT", "EU"]`). |
| `capacity`         | object  | OPTIONAL    | Capacity information for load-based broker selection. |
| `capacity.requests_per_minute` | integer | OPTIONAL | Maximum relay capacity per minute. |
| `capacity.current_load_pct`    | integer | OPTIONAL | Current load as a percentage (0-100). |
| `health`           | string  | REQUIRED    | Broker health status: `"healthy"`, `"degraded"`, or `"unhealthy"`. |
| `last_health_check`| string  | REQUIRED    | RFC 3339 timestamp of the most recent health check. |

**Hosting options:**

The broker discovery endpoint MAY be served by any of the following:

- **The recipient agent.** An agent may maintain a list of known brokers and serve them
  from its own infrastructure. This is the simplest deployment model.
- **A broker registry service.** A shared infrastructure service that aggregates broker
  information from multiple sources. This is useful for organisations that operate
  multiple brokers across different zones.
- **The sender's own configuration.** The sender may maintain a static list of broker
  endpoints and serve the discovery response locally. This is appropriate when the
  sender has pre-negotiated relationships with specific brokers.

> **Note (informative).** Broker registry discovery is a deployment concern — analogous
> to SMTP MTA discovery or OAuth authorization server discovery. The ARSIA Protocol does
> not mandate a single discovery mechanism. Implementations that do not have a
> pre-configured broker registry SHOULD use the well-known URI
> `/.well-known/arsia/brokers` as a default discovery endpoint. Static configuration,
> DNS-based service discovery, and operator-provisioned registries are equally valid
> approaches.

**Caching:**

The discovery response SHOULD include caching headers:

```http
Cache-Control: max-age=300
ETag: "{etag}"
```

Senders SHOULD cache broker discovery responses for the duration specified by
`Cache-Control`. A maximum cache duration of 5 minutes is RECOMMENDED to balance
freshness with efficiency. Senders SHOULD use `If-None-Match` with the `ETag` for
conditional requests.

**Empty response:**

If no brokers are available for the requested zone, the response MUST be an empty JSON
array `[]` with HTTP status 200 OK. The sender's topology determination procedure (§1.3)
will handle the empty response by returning an error.

### 7.3 Broker Relay Rules (Normative)

The following rules are normative. All Compliance Brokers MUST implement these rules.
These rules define the broker's obligations when relaying a message.

**Rule 1: Signature verification.** The broker MUST verify the sender's message
signature before forwarding. The verification procedure is defined in
ARSIA-Core.md §5.2. If the signature is invalid, the broker MUST reject the message
with error code `unauthorized` (ARSIA-Core.md §11.2) and MUST NOT forward the message.

**Rule 2: Residency zone verification.** The broker MUST verify that its own
jurisdiction matches the message's `compliance.data_residency` zone. Matching rules:

- For a country code zone (e.g., `"PT"`): the broker's `IdentityRecord.jurisdiction`
  MUST equal the zone exactly.
- For the `"EU"` regional zone: the broker's `IdentityRecord.jurisdiction` MUST be an
  ISO 3166-1 alpha-2 code of a current EU/EEA member state.

If the broker's jurisdiction does not match the required zone, the broker MUST reject
the message with error code `service_unavailable` (ARSIA-Core.md §11.2) and MUST NOT
forward it. The error details MUST include:

```json
{
  "data_residency_violation": true,
  "broker_jurisdiction": "{actual-jurisdiction}",
  "required_zone": "{zone}"
}
```

**Rule 3: Envelope integrity.** The broker MUST NOT modify the message envelope in any
way. The message forwarded to the recipient MUST be byte-identical to the message
received from the sender, after JSON canonicalization (RFC 8785). This means:

- The broker MUST NOT add, remove, or modify any fields in the envelope.
- The broker MUST NOT re-sign the message.
- The broker MUST NOT modify the `security` object.
- The broker MUST NOT modify the `payload`.
- The sender's original digital signature MUST remain valid and verifiable by the
  recipient.

**Rule 4: Payload confidentiality.** The broker MUST NOT read or log the payload
contents. The broker MAY compute and log a hash of the payload (SHA-256) for audit
purposes (`payload_hash`), but MUST NOT store, inspect, index, or transmit the payload
contents to any party other than the intended recipient. This rule ensures that the
broker operates as a transparent relay and does not gain access to application-level
data.

**Rule 5: Forward delivery.** The broker MUST forward the message to the recipient's
inbox using direct routing (§1.2.1). The broker:

a. Discovers the recipient's inbox URL from the recipient's discovery endpoint.
b. Obtains an access token for the recipient.
c. Sends the message to the recipient's inbox via HTTP POST (§2.1).

**Rule 6: Response relay.** The broker MUST return the recipient's response to the
sender unmodified. If the recipient returns an ARSIA response envelope, the broker
forwards that envelope to the sender without alteration. If the recipient returns an
error, the broker forwards the error to the sender without alteration.

**Rule 7: Audit obligation.** The broker MUST append a `broker_relay` audit record for
every message it relays, including messages that result in errors. The audit record
format is defined in §7.4. The audit record MUST contain:

- `relay_id`: UUID v4, unique per relay operation.
- `message_id`: The `id` field from the relayed message.
- `from_agent`: The `from` field from the relayed message.
- `to_agent`: The `to` field from the relayed message.
- `broker_agent_id`: The broker's own agent-id.
- `zone`: The data residency zone this relay satisfies.
- `relayed_at`: RFC 3339 timestamp with millisecond precision.
- `payload_hash`: SHA-256 hash of the message payload, hex-encoded.

**Rule 8: No message storage.** The broker MUST NOT cache or store message envelopes
beyond the audit record defined in Rule 7. After forwarding the message and receiving
the recipient's response, the broker MUST discard the message envelope from memory and
any temporary storage. The only persistent record is the audit record, which does NOT
contain the message payload.

**Rule 9: Expiration compliance.** The broker MUST respect the message's `expires_at`
field. If forwarding the message would cause the response to arrive after `expires_at`
(with a 5-second safety margin per §2.3.4), the broker MUST return
`service_unavailable` to the sender and MUST NOT forward the message. The broker SHOULD
log this event in its audit trail with `forwarding_result: "timeout"`.

### 7.4 Broker Audit Record Format

The broker audit record captures the metadata of a relay operation for compliance and
audit purposes. This record extends the `ArsiaAuditRecord` base type (to be defined in
ARSIA-State.md §7).

**BrokerRelayAuditRecord:**

| Field                | Type    | Required | Description                               |
|---------------------|---------|----------|-------------------------------------------|
| `audit_type`        | string  | REQUIRED | Fixed value: `"broker_relay"`.            |
| `relay_id`          | string  | REQUIRED | UUID v4, unique per relay operation.      |
| `message_id`        | string  | REQUIRED | The `id` of the relayed message.          |
| `from_agent`        | string  | REQUIRED | The `from` field of the relayed message.  |
| `to_agent`          | string  | REQUIRED | The `to` field of the relayed message.    |
| `broker_agent_id`   | string  | REQUIRED | The broker's own agent-id.                |
| `residency_zone`    | string  | REQUIRED | The zone this relay satisfies (e.g., `"EU"`). |
| `relayed_at`        | string  | REQUIRED | RFC 3339 timestamp with ms precision.     |
| `payload_hash`      | string  | REQUIRED | SHA-256 hash of payload, hex-encoded.     |
| `relay_latency_ms`  | integer | REQUIRED | Time from receipt to forward initiation, in milliseconds. |
| `forwarding_result` | string  | REQUIRED | One of: `"success"`, `"failure"`, `"timeout"`. |

**Example audit record:**

```json
{
  "audit_type": "broker_relay",
  "relay_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "from_agent": "agent:acme.billing",
  "to_agent": "agent:contoso.risk-assessor",
  "broker_agent_id": "agent:arsialabs.broker.eu-west",
  "residency_zone": "EU",
  "relayed_at": "2026-03-24T14:30:01.234Z",
  "payload_hash": "a3f2b8c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1",
  "relay_latency_ms": 47,
  "forwarding_result": "success"
}
```

**Storage requirements:**

- Broker relay audit records MUST be stored within the declared data residency zone.
- Records MUST be stored in an append-only manner: once written, records MUST NOT be
  modified or deleted until the applicable retention period expires.
- The retention period for broker relay audit records is determined by the compliance
  profile of the relayed message:
  - `EU-AI-ACT-HIGH-RISK`: 180 days minimum.
  - `MIFID-II`: 1827 days (5 years) minimum.
  - `PAC-AGRICULTURE`: 1096 days (3 years) minimum.
  - `DSA-VLOP`: 730 days (2 years) minimum.
  - `DORA`: 1827 days (5 years) minimum.
  - Default (no profile, GDPR-STANDARD, or EU-AI-ACT-LIMITED-RISK): 90 days minimum.
- Records MUST survive broker restarts and infrastructure failures. Implementations
  MUST use durable storage (e.g., PostgreSQL, append-only files on replicated storage).

---

## 8. Routing Conformance Tests

The following test cases define conformance requirements for the Routing primitive. Each
test is identified by a unique `test_id` and specifies preconditions, actions, and
expected results. These tests are normative — a conformant implementation MUST pass all
tests at the applicable conformance level.

### ROUTING-01: Direct routing success

| Field             | Value                                                          |
|-------------------|----------------------------------------------------------------|
| **test_id**       | `ROUTING-01`                                                   |
| **description**   | Verify that direct routing delivers a message successfully     |
| **conformance**   | Core                                                           |
| **preconditions** | Agent A and Agent B are running. Agent B's discovery endpoint is accessible. No `compliance.data_residency` field is set in the message. Agent A has a valid access token for Agent B. |
| **action**        | Agent A discovers Agent B via `GET {B-host}/.well-known/arsia`. Agent A extracts Agent B's inbox URL. Agent A signs a message with `intent: "request"` and sends it to Agent B's inbox via `POST /v1/arsia/inbox`. |
| **expected**      | HTTP 200 OK. Response body is a valid ARSIA response envelope with `intent: "response"`. `correlation_id` equals the request's `id`. `Content-Type` is `application/arsia+json; v=1`. |

### ROUTING-02: Brokered routing triggered by data_residency

| Field             | Value                                                          |
|-------------------|----------------------------------------------------------------|
| **test_id**       | `ROUTING-02`                                                   |
| **description**   | Verify that brokered routing is used when data_residency is set |
| **conformance**   | Compliance                                                     |
| **preconditions** | Agent A, Agent B, and a Compliance Broker are running. The broker declares `arsiaprotocol.broker.relay` capability and `jurisdiction: "IE"` (satisfies `"EU"` zone). Agent A sends a message with `compliance.data_residency: "EU"`. The broker discovery endpoint returns the broker as an eligible candidate. |
| **action**        | Agent A evaluates the topology determination procedure (§1.3). Agent A discovers the broker. Agent A sends the signed message to the broker's inbox. The broker verifies the signature, verifies zone compliance, and forwards the message to Agent B's inbox. Agent B processes the message and returns a response. The broker relays the response to Agent A. |
| **expected**      | Agent A receives a valid ARSIA response envelope from Agent B (relayed through the broker). The broker's audit trail contains a `broker_relay` record with `residency_zone: "EU"` and `forwarding_result: "success"`. The message received by Agent B is byte-identical (after canonicalization) to the message sent by Agent A. |

### ROUTING-03: No eligible broker for required zone

| Field             | Value                                                          |
|-------------------|----------------------------------------------------------------|
| **test_id**       | `ROUTING-03`                                                   |
| **description**   | Verify that an error is returned when no broker is available   |
| **conformance**   | Compliance                                                     |
| **preconditions** | Agent A has a message with `compliance.data_residency: "EU"`. The broker discovery endpoint returns an empty array `[]` for `residency=EU`. |
| **action**        | Agent A evaluates the topology determination procedure (§1.3). Agent A queries the broker discovery endpoint for zone `"EU"`. Agent A receives an empty broker list. |
| **expected**      | Agent A does NOT send the message to any agent. Agent A returns an error with `code: "service_unavailable"` and `details.data_residency_violation: true` and `details.required_zone: "EU"` and `details.available_zones: []`. |

### ROUTING-04: Envelope integrity after broker relay

| Field             | Value                                                          |
|-------------------|----------------------------------------------------------------|
| **test_id**       | `ROUTING-04`                                                   |
| **description**   | Verify that the broker does not modify the message envelope    |
| **conformance**   | Compliance                                                     |
| **preconditions** | Agent A sends a message via a Compliance Broker. Agent B is the recipient. |
| **action**        | Agent A signs the message and sends it to the broker. The broker forwards it to Agent B. Agent B receives the message and performs signature verification using Agent A's public key. Compare the message received by Agent B with the message sent by Agent A (field by field). |
| **expected**      | All envelope fields received by Agent B are identical to those sent by Agent A. Agent A's original Ed25519 signature verifies successfully at Agent B using Agent A's public key from Agent A's JWKS endpoint. The broker's identity or keys are NOT involved in signature verification. |

### ROUTING-05: TLS required (plain HTTP rejected)

| Field             | Value                                                          |
|-------------------|----------------------------------------------------------------|
| **test_id**       | `ROUTING-05`                                                   |
| **description**   | Verify that plaintext HTTP connections are rejected            |
| **conformance**   | Core                                                           |
| **preconditions** | Agent B's inbox is available at `https://{host}/v1/arsia/inbox`. No plaintext HTTP listener is configured, or a redirect is in place. |
| **action**        | Agent A attempts to send a message to Agent B's inbox via plaintext HTTP: `POST http://{host}/v1/arsia/inbox`. |
| **expected**      | The connection is refused (no listener on port 80), OR Agent B returns HTTP 301 redirecting to the HTTPS URL, OR the TLS handshake fails (if Agent A incorrectly attempts plaintext on the TLS port). The message is NOT delivered over plaintext. |

### ROUTING-06: Idempotency key deduplication

| Field             | Value                                                          |
|-------------------|----------------------------------------------------------------|
| **test_id**       | `ROUTING-06`                                                   |
| **description**   | Verify that duplicate messages with the same idempotency key are deduplicated |
| **conformance**   | Core                                                           |
| **preconditions** | Agent A sends a request to Agent B with `idempotency.key: "test-key-001"` and `idempotency.expires_at` set to 1 hour from now. Agent B processes the request and returns a response. |
| **action**        | Agent A sends the same request again to Agent B with the same `idempotency.key: "test-key-001"`, the same `id`, and the same `from`, `to`, and `payload.type` values. |
| **expected**      | Agent B returns the previously stored response without re-executing the request. The HTTP status code is identical to the first response. The response body is the exact ARSIA envelope returned for the first request. Agent B's processing logic was NOT invoked a second time. |

### ROUTING-07: Rate limit enforcement

| Field             | Value                                                          |
|-------------------|----------------------------------------------------------------|
| **test_id**       | `ROUTING-07`                                                   |
| **description**   | Verify that rate limiting is enforced and communicated         |
| **conformance**   | Core                                                           |
| **preconditions** | Agent B advertises `rate_limits.requests_per_minute: 10` in its discovery response. Agent A has a valid access token for Agent B. |
| **action**        | Agent A sends 15 requests to Agent B's inbox within a 1-minute window. Each request is a valid ARSIA request message with a unique `id` and unique `idempotency.key`. |
| **expected**      | The first 10 requests (or up to `burst_size` if greater) succeed with HTTP 200. The remaining requests receive HTTP 429 with: (1) `Retry-After` header present with a positive integer value. (2) Response body is a valid ARSIA error envelope with `payload.error.code: "rate_limited"`. (3) `X-RateLimit-Remaining: 0` header present on the 429 responses. |

### ROUTING-08: Message expiration

| Field             | Value                                                          |
|-------------------|----------------------------------------------------------------|
| **test_id**       | `ROUTING-08`                                                   |
| **description**   | Verify that expired messages are rejected                      |
| **conformance**   | Core                                                           |
| **preconditions** | Agent A constructs a message with `expires_at` set to `current_time - 600` (10 minutes in the past). This guarantees the message is expired regardless of ±300-second clock skew tolerance (§8.3). |
| **action**        | Agent A sends the pre-expired message to Agent B's inbox. Agent B receives the message and checks `expires_at` against its current time (with ±300 seconds clock skew tolerance per ARSIA-Core.md §8.3). |
| **expected**      | Agent B rejects the message with HTTP 400 and error code `invalid_request`. The error `description` indicates that the message has expired. |

> **Note (informative).** Implementations MAY additionally test with a shorter expiry
> window (e.g., `expires_at` set to 5 seconds in the future with a 10-second send delay)
> for fast-feedback testing, but this approach is non-deterministic under the ±300-second
> clock skew tolerance (§8.3) and MUST NOT be used as the sole conformance gate.

### ROUTING-09: WebSocket authentication success

| Field             | Value                                                          |
|-------------------|----------------------------------------------------------------|
| **test_id**       | `ROUTING-09`                                                   |
| **description**   | Verify successful WebSocket authentication                     |
| **conformance**   | Core (when WebSocket is supported)                             |
| **preconditions** | Agent B supports the WebSocket binding (§2.2). Agent A has a valid access token for Agent B. |
| **action**        | Agent A opens a WebSocket connection to `wss://{B-host}/v1/arsia/stream` with `Sec-WebSocket-Protocol: arsia-v1`. After the upgrade succeeds, Agent A sends: `{ "type": "auth", "token": "Bearer {valid_access_token}" }`. |
| **expected**      | Agent B responds with: `{ "type": "auth_ok", "agent_id": "agent:{B-domain}.{B-name}", "session_id": "{uuid}" }`. The `agent_id` matches Agent B's declared agent identifier. The `session_id` is a valid UUID v4. The WebSocket connection remains open. Agent A can subsequently send ARSIA message envelopes as text frames. |

### ROUTING-10: WebSocket authentication failure

| Field             | Value                                                          |
|-------------------|----------------------------------------------------------------|
| **test_id**       | `ROUTING-10`                                                   |
| **description**   | Verify that WebSocket authentication failure closes the connection |
| **conformance**   | Core (when WebSocket is supported)                             |
| **preconditions** | Agent B supports the WebSocket binding (§2.2). Agent A has an invalid or expired access token. |
| **action**        | Agent A opens a WebSocket connection to `wss://{B-host}/v1/arsia/stream` with `Sec-WebSocket-Protocol: arsia-v1`. After the upgrade succeeds, Agent A sends: `{ "type": "auth", "token": "Bearer {invalid_or_expired_token}" }`. |
| **expected**      | Agent B responds with: `{ "type": "auth_error", "code": "unauthorized", "description": "..." }`. Agent B closes the WebSocket connection with close code 4001 (Authentication Failed) within 5 seconds (per ARSIA-Core.md §8.2). Agent A can no longer send frames on this connection. |

---

## 9. References

### 9.1 Normative References

- **ARSIA-Core.md** — ARSIA Protocol Core Specification, Draft-01.
  §3 (Agent Identifier Format), §4 (Message Envelope), §4.3.6 (Compliance Metadata),
  §5 (Message Security), §5.1 (Digital Signatures), §5.2 (Signature Verification),
  §6 (Authorization), §6.2 (Token Request), §6.3 (Token Presentation),
  §6.4 (Capability Enforcement), §7 (Discovery), §7.1 (Discovery Endpoint),
  §7.3 (JWKS Endpoint), §7.4 (Version Negotiation), §8 (Transport Bindings),
  §8.1 (HTTP/2), §8.2 (WebSocket), §8.3 (Request/Response Timing),
  §9 (Routing and Brokers), §9.1 (Direct Routing), §9.2 (Brokered Routing),
  §9.3 (Routing Topology), §9.4 (Topology Determination Procedure),
  §10 (Idempotency), §10.1 (Idempotency Key Semantics),
  §10.3 (Duplicate Detection Behaviour), §10.4 (Header vs. Envelope Precedence),
  §11 (Error Handling), §11.1 (Error Response Format),
  §11.2 (Standard Error Codes), §11.3 (Retry Policy),
  §12 (Conformance Levels), §12.1 (Core Conformance).

- **ARSIA-Identity.md** — ARSIA Identity Primitive Specification, Draft-01.
  §1.2 (Agent Identity Record), §1.3 (Well-Known Identity Endpoint).

- **ARSIA-State.md** — ARSIA State Primitive Specification, Draft-01.
  §7 (Audit Trail).

- **RFC 2119** — Bradner, S., "Key words for use in RFCs to Indicate Requirement
  Levels", BCP 14, March 1997.

- **RFC 6455** — Fette, I. and A. Melnikov, "The WebSocket Protocol", December 2011.

- **RFC 6797** — Hodges, J., Jackson, C., and A. Barth, "HTTP Strict Transport
  Security (HSTS)", November 2012.

- **RFC 7541** — Peon, R. and H. Ruellan, "HPACK: Header Compression for HTTP/2",
  May 2015.

- **RFC 8174** — Leiba, B., "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key
  Words", BCP 14, May 2017.

- **RFC 8446** — Rescorla, E., "The Transport Layer Security (TLS) Protocol Version
  1.3", August 2018.

- **RFC 8785** — Rundgren, A., Jordan, B., and S. Erdtman, "JSON Canonicalization
  Scheme (JCS)", June 2020.

- **RFC 9113** — Thomson, M. and C. Benfield, "HTTP/2", June 2022.

### 9.2 Informative References

- **GDPR** — Regulation (EU) 2016/679 of the European Parliament and of the Council
  of 27 April 2016. Chapter V: Transfers of personal data to third countries or
  international organisations.

- **EDPB Guidelines 05/2021** — European Data Protection Board, "Interplay between
  the application of Article 3 and the provisions on international transfers as per
  Chapter V of the GDPR", Version 2.0, February 2022.

- **EU AI Act** — Regulation (EU) 2024/1689 of the European Parliament and of the
  Council of 13 June 2024. Art. 13 (Transparency), Art. 14 (Human Oversight),
  Art. 17 (Quality Management), Art. 26 (Deployer Obligations).

- **MiFID II** — Directive 2014/65/EU of the European Parliament and of the Council
  of 15 May 2014. Art. 16(6) (Record-keeping, 5-year retention requirement).

- **ISO 3166-1** — International Organization for Standardization, "Codes for the
  representation of names of countries and their subdivisions — Part 1: Country codes",
  2020.

---
ARSIA Protocol ([arsiaprotocol.org](https://arsiaprotocol.org)) | by [Arsia Labs](https://arsialabs.ai)
