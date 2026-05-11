<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
# ARSIA-Identity — Identity Primitive Specification

**Protocol:** ARSIA Protocol
**Version:** 1.0
**Status:** Draft
**Authors:**
- Kirk Patrick (Arsia Labs) — kirk@arsialabs.ai
- Greici Savoldi (Arsia Labs) — greici@arsialabs.ai

**Draft-01 | March 2026 | References: ARSIA-Core.md §3, §5, §7**
**Arsia Labs — arsiaprotocol.org**

---

## Abstract

The Identity primitive defines how ARSIA Protocol agents establish, publish, and verify
their identity. Built on three layers — technical, cryptographic, and compliance — it
answers four questions: who is this agent (technical identity), how can its messages be
verified (cryptographic identity), who is legally responsible for it (compliance
identity), and what regulatory classification applies to it (a compliance-layer property
under the EU AI Act). The primitive binds these three layers into a single verifiable
record called the IdentityRecord, served at a well-known endpoint and signed with the
agent's Ed25519 key. Additionally, it defines
the six-phase onboarding flow through which external agents are evaluated, scoped, and
admitted into corporate ARSIA deployments. This specification is normative for all ARSIA
Protocol implementations at Compliance Conformance level or above.

---

## Status of This Memo

This document specifies Draft-01 of the ARSIA Identity Primitive. This specification is
a working draft published by Arsia Labs for review and comment. Implementors should
expect breaking changes between draft revisions.

The canonical location for this specification is:

    https://arsiaprotocol.org/spec/identity/draft-01

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

1. [Agent Identity Model](#1-agent-identity-model)
   1. [Three-Layer Identity](#11-three-layer-identity)
   2. [Agent Identity Record](#12-agent-identity-record)
   3. [Well-Known Identity Endpoint](#13-well-known-identity-endpoint)
2. [Key Management](#2-key-management)
   1. [Key Pair Requirements](#21-key-pair-requirements)
   2. [Key Identifier Format](#22-key-identifier-format)
   3. [JWKS Structure](#23-jwks-structure)
   4. [Key Rotation](#24-key-rotation)
   5. [Key Revocation](#25-key-revocation)
3. [Authentication Flow](#3-authentication-flow)
   1. [Message-Level Authentication (EdDSA)](#31-message-level-authentication-eddsa)
   2. [Token-Based Authorization (OAuth 2.0)](#32-token-based-authorization-oauth-20)
   3. [DPoP (Proof of Possession)](#33-dpop-proof-of-possession)
4. [Identity in the Compliance Context](#4-identity-in-the-compliance-context)
   1. [Owner Accountability](#41-owner-accountability)
   2. [Classification Consistency Rule](#42-classification-consistency-rule)
   3. [Cross-Border Identity](#43-cross-border-identity)
   4. [Deployer vs Owner Distinction](#44-deployer-vs-owner-distinction)
5. [Identity Conformance Tests](#5-identity-conformance-tests)
6. [Certificate Trust Levels](#6-certificate-trust-levels)
   1. [Level 1 — Self-Signed (Default)](#61-level-1--self-signed-default)
   2. [Level 2 — CA-Signed (Enterprise)](#62-level-2--ca-signed-enterprise)
   3. [Level 3 — Qualified Certificate (eIDAS)](#63-level-3--qualified-certificate-eidas)
   4. [Verification Procedure](#64-verification-procedure)
   5. [IdentityRecord Extension](#65-identityrecord-extension)
   6. [Conformance Tests](#66-conformance-tests)
   7. [Sandbox CA Integration](#67-sandbox-ca-integration)
   8. [Security Considerations](#68-security-considerations)
7. [External Agent Onboarding](#7-external-agent-onboarding)
   1. [Onboarding Model Overview](#71-onboarding-model-overview)
   2. [Phase 1 — Discovery & Identity Verification](#72-phase-1--discovery--identity-verification)
   3. [Phase 2 — Compliance Conformance Test](#73-phase-2--compliance-conformance-test)
   4. [Phase 3 — Capability Scoping](#74-phase-3--capability-scoping)
   5. [Phase 4 — Provenance Verification](#75-phase-4--provenance-verification)
   6. [Phase 5 — Onboarding Decision](#76-phase-5--onboarding-decision)
   7. [Phase 6 — Operational Phase](#77-phase-6--operational-phase)
   8. [Example — Regulatory Auditor Onboarding](#78-example--regulatory-auditor-onboarding)
8. [Capability Policy](#8-capability-policy)
   1. [Policy Structure](#81-policy-structure)
   2. [CapabilityRule](#82-capabilityrule)
   3. [Policy Evaluation Procedure](#83-policy-evaluation-procedure)
9. [Onboarding Security Considerations](#9-onboarding-security-considerations)
   1. [Token Scope Limitation](#91-token-scope-limitation)
   2. [Token Theft Mitigation](#92-token-theft-mitigation)
   3. [Audit Trail Integrity](#93-audit-trail-integrity)
   4. [Off-Boarding and Token Revocation](#94-off-boarding-and-token-revocation)
10. [Onboarding Conformance Tests](#10-onboarding-conformance-tests)
11. [References](#11-references)
12. [Multi-Organization Onboarding (BYOA)](#12-multi-organization-onboarding-byoa)

---

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14 [RFC 2119] [RFC 8174] when,
and only when, they appear in ALL CAPITALS, as shown here.

---

## 1. Agent Identity Model

### 1.1 Three-Layer Identity

ARSIA Protocol identity is structured as three layers, each serving a distinct purpose.
All three layers MUST be present and consistent for an agent to be considered fully
identified within the protocol.

**Layer 1 — Technical Identity.** The agent-id string as defined in ARSIA-Core.md §3.
This is the addressing layer. It provides a globally unique identifier that tells other
agents WHERE to send messages. The agent-id follows the format `agent:{domain}.{name}`
with optional path segments, as specified by the ABNF grammar in ARSIA-Core.md §3.1.

**Layer 2 — Cryptographic Identity.** The Ed25519 key pair bound to that agent-id,
published via a JWK Set at the agent's JWKS endpoint (ARSIA-Core.md §7.3). This is the
verification layer. It tells any recipient HOW to verify that a message genuinely
originated from the agent identified in the `from` field. Every outbound message carries
a digital signature in the `security` field (ARSIA-Core.md §5.1), and the corresponding
public key is retrievable from the JWKS endpoint.

**Layer 3 — Compliance Identity.** The legal entity that owns and operates the agent,
plus its regulatory classification under the EU AI Act. This is the accountability
layer. It tells regulators, auditors, and counterparty agents WHO is legally responsible
for this agent's actions and what obligations apply to its operation.

All three layers MUST be consistent. Consistency means that a message from
`agent:acme.billing` MUST be signed by a key whose `kid` starts with
`agent:acme.billing#`, and that key MUST be published at the JWKS endpoint hosted by
the same infrastructure that owns the `acme` domain. The IdentityRecord served at
`/.well-known/arsia/identity` on that same domain MUST declare the legal entity that
owns `agent:acme.billing` via the `owner_id` and `owner_name` fields.

Furthermore, if the IdentityRecord declares `ai_system_classification` as `"high-risk"`,
all outbound request and response messages from that agent MUST carry appropriate
compliance metadata (see §4.2 for the classification consistency rule). A receiving
agent that detects an inconsistency between the three layers — for example, a message
signed by a key not present in the sender's JWKS, or a high-risk agent sending messages
without the required compliance profile — MUST reject the message or log a compliance
warning, depending on the specific violation.

### 1.2 Agent Identity Record

The IdentityRecord is a JSON object that binds the three identity layers together. It
is the authoritative declaration of an agent's identity within the ARSIA Protocol.

The IdentityRecord contains the following fields:

**`agent_id`** (string, REQUIRED)
:   The agent's unique identifier, in the format defined by ARSIA-Core.md §3. This
    field binds the IdentityRecord to the technical identity layer.

**`owner_id`** (string, REQUIRED)
:   Legal entity identifier of the entity that owns and operates the agent. While the
    ARSIA Protocol's compliance layer focuses on EU regulation, the identity layer is
    jurisdiction-agnostic — agents MAY be owned by entities registered in any country.
    The `owner_id` MUST be a verifiable legal entity identifier in one of the following
    formats:

    - **EU VAT number** — two-letter country code followed by the number (e.g.
      `"PT501234567"` for Portugal, `"DE123456789"` for Germany).
    - **US Employer Identification Number (EIN)** — format `"84-1234567"`.
    - **LEI (Legal Entity Identifier, ISO 17442)** — globally unique, issued by GLEIF.
      Format: `"urn:lei:5493001KJTIIGC8Y1R12"`.
    - **DUNS Number** — globally recognized business identifier issued by Dun &
      Bradstreet. Format: `"urn:duns:123456789"`.
    - **National company registration number** — any jurisdiction's official company
      registry number.
    - **Other URN** — any URN following a documented and publicly verifiable scheme.

    Implementations SHOULD prefer LEI when the entity has one, as it is the only globally
    standardized legal entity identifier. This field establishes legal accountability.

**`owner_name`** (string, REQUIRED)
:   Human-readable legal name of the entity that owns and operates the agent. This MUST
    be the registered legal name, not a trading name or brand.

**`jurisdiction`** (string, REQUIRED)
:   ISO 3166-1 alpha-2 country code of the entity's legal registration (e.g. `"PT"` for
    Portugal, `"DE"` for Germany). This determines which national supervisory authority
    has jurisdiction over the agent's operator.

**`ai_system_classification`** (string, REQUIRED)
:   Agent-level classification per EU AI Act Annex III categories. MUST be one of:
    `"minimal-risk"`, `"limited-risk"`, `"high-risk"`, or `"unacceptable-risk"`. This is
    the worst-case classification across all intended uses of this agent. Per-message
    classification (in the `compliance.ai_system_classification` envelope field) MAY be
    equal to or lower than this value but MUST NEVER be higher.

**`deployer_id`** (string, OPTIONAL)
:   Legal entity identifier of the deploying entity, when the deployer differs from the
    owner. For example, a SaaS provider deploying an agent on behalf of a client. Same
    format requirements as `owner_id`.

**`deployer_name`** (string, OPTIONAL — REQUIRED if `deployer_id` is set)
:   Human-readable legal name of the deploying entity. This field MUST be present
    whenever `deployer_id` is present.

**`created_at`** (string, REQUIRED)
:   Timestamp of when this identity record was created, in RFC 3339 format with
    millisecond precision (e.g. `"2026-03-24T10:00:00.000Z"`).

**`valid_until`** (string, OPTIONAL)
:   Expiry timestamp of this identity record, in RFC 3339 format with millisecond
    precision. After this timestamp, the record MUST be refreshed by the agent operator.
    RECOMMENDED: 90 days from `created_at`.

**`contact_email`** (string, OPTIONAL — RECOMMENDED for high-risk agents)
:   Operational contact email address for this agent. MUST be a role-based address (e.g.
    `ops@acme.example`), not a personal address. Used for incident reporting per the
    Digital Operational Resilience Act (DORA).

The formal JSON Schema for the IdentityRecord is defined in
`arsia-identity-record.schema.json`.

### 1.3 Well-Known Identity Endpoint

An ARSIA-compliant agent MUST serve its IdentityRecord at:

    GET /.well-known/arsia/identity

This endpoint MUST be available alongside the discovery endpoint defined in
ARSIA-Core.md §7.1. It MUST be served over TLS 1.3 or higher.

The response MUST include the following header:

    X-ARSIA-Sig: {base64url-encoded Ed25519 signature over SHA-256 hash of response body}

The `X-ARSIA-Sig` header allows any party to verify that the identity record was
produced by the agent itself, not by a proxy, CDN, or man-in-the-middle. Verification
proceeds as follows:

1. Compute the SHA-256 hash of the raw response body bytes (before any decompression
   or transcoding).
2. Base64url-decode the value of the `X-ARSIA-Sig` header.
3. Retrieve the agent's public key from its JWKS endpoint (ARSIA-Core.md §7.3).
4. Verify the Ed25519 signature over the SHA-256 hash using the retrieved public key.

If the signature does not verify, the identity record MUST be treated as untrusted.

> **Note (informative):** The protocol uses two distinct signing input preparations.
> For the identity endpoint (this section), the raw response body bytes are SHA-256
> hashed and the resulting 32-byte digest is signed with Ed25519. This is an
> HTTP-layer integrity mechanism: the server produces both the body and the signature,
> so no canonicalization is needed, and any intermediary (CDN, proxy, TLS-terminating
> load balancer) that alters the response bytes will be detected. For message
> envelopes (ARSIA-Core.md §5.1), the JSON envelope minus the `security` block is
> canonicalized via JCS ([RFC 8785]) and the canonical bytes are signed directly with
> Ed25519 — no intermediate hash. JCS is necessary there because sender and recipient
> may serialize identical JSON objects differently; canonicalization ensures both sides
> compute the same signing input. Using the wrong input preparation in either context
> will produce signature verification failures.

The response SHOULD include caching headers:

    Cache-Control: max-age=3600, must-revalidate
    ETag: "{hash-based etag}"

Clients SHOULD respect these caching headers. Clients SHOULD refetch the identity
record when a message signature verification fails, to handle recent key rotations or
identity updates.

---

## 2. Key Management

### 2.1 Key Pair Requirements

The REQUIRED signing algorithm for ARSIA Protocol v1.0 is Ed25519 (EdDSA over
Curve25519). This is the only REQUIRED algorithm. Implementations MAY support additional
algorithms listed in ARSIA-Core.md §5.1, but Ed25519 MUST be supported.

Key size is 256 bits (fixed for Ed25519 — 32-byte private scalar, 32-byte public point).

Private key storage requirements:

- Private keys MUST NOT be stored in plaintext on disk in production environments.
- RECOMMENDED: Hardware Security Module (HSM) or cloud Key Management Service (AWS KMS,
  GCP Cloud KMS, Azure Key Vault).
- ACCEPTABLE: Encrypted at rest using OS-level key management (e.g. macOS Keychain,
  Linux kernel keyring, Windows DPAPI).
- PROHIBITED: Environment variables containing raw private key bytes in production
  deployments. Development environments MAY use environment variables for convenience,
  but this MUST NOT be carried to production.

Public key publication: The agent's public key MUST be published at
`/.well-known/arsia/jwks.json` as specified in ARSIA-Core.md §7.3.

### 2.2 Key Identifier Format

The `kid` (Key ID) field in JWK entries MUST follow the pattern:

    {agent-id}#{key-index}

Where:

- `{agent-id}` is the full agent identifier as defined in ARSIA-Core.md §3.
- `#` is a literal hash character acting as a separator.
- `{key-index}` is a short alphanumeric identifier (e.g. `"key1"`, `"key2"`,
  `"2026q1"`).

Examples:

    agent:acme.billing#key1
    agent:arsialabs.demo.risk-assessor#key2
    agent:contoso.finance.trading#2026q1

The `kid` MUST be globally unique within the JWKS of a given agent. A `kid` MUST NOT be
reused after the corresponding key has been retired, even if a new key is generated with
identical key material (which SHOULD be avoided).

### 2.3 JWKS Structure

The agent's public keys are published as a standard JWK Set per RFC 7517.

Each Ed25519 key entry MUST contain the following fields:

| Field | Value                | Description                                    |
|-------|----------------------|------------------------------------------------|
| `kty` | `"OKP"`             | Key type: Octet Key Pair                       |
| `crv` | `"Ed25519"`          | Curve identifier                               |
| `kid` | string               | Key identifier per §2.2                        |
| `x`   | string               | Base64url-encoded 32-byte public key, no padding |
| `use` | `"sig"` (REQUIRED)   | Key usage                                      |

Example JWKS:

```json
{
  "keys": [
    {
      "kty": "OKP",
      "crv": "Ed25519",
      "kid": "agent:acme.billing#key1",
      "x": "11qYAYKxCrfVS_7TyWQHOg7hcvPapiMlrwIaaPcHURo",
      "use": "sig"
    }
  ]
}
```

### 2.4 Key Rotation

Key rotation MUST follow this procedure:

1. Generate a new Ed25519 key pair.
2. Add the new key to the JWKS with a new `kid` (e.g. `"key2"`).
3. Both the old key (`"key1"`) and the new key (`"key2"`) MUST be present in the JWKS
   simultaneously for the duration of the overlap period.
4. The overlap period MUST be at least 24 hours. A 72-hour overlap period is
   RECOMMENDED.
5. Begin signing all new outbound messages with the new key.
6. During the overlap period, recipients MUST accept signatures from BOTH keys. JWKS
   caching (see §3.1) ensures that recipients will eventually discover the new key.
7. After the overlap period has elapsed, remove the old key from the JWKS.
8. Log a `key_rotation` audit event (ARSIA-State.md §7).

Key rotation SHOULD be automated. Recommended triggers:

- Key age exceeding 90 days (RECOMMENDED maximum key lifetime).
- Suspected or confirmed key compromise.
- Change in compliance policy requiring a key refresh.

### 2.5 Key Revocation

ARSIA Protocol v1.0 does not define an explicit Certificate Revocation List (CRL) or
OCSP-like revocation mechanism.

Implementations SHOULD achieve revocation through the following approach:

1. Use short key validity periods (90 days RECOMMENDED).
2. For immediate revocation: remove the compromised key from the JWKS AND rotate to a
   new key immediately, without an overlap period.
3. Log a `key_rotation` audit event with `reason: "revocation"`.

Recipients that cache JWKS responses (see §3.1) SHOULD refetch JWKS on signature
verification failure. This provides near-immediate revocation propagation, bounded by
the recipient's JWKS cache TTL (RECOMMENDED maximum: 1 hour).

Future versions of this specification MAY define a formal revocation mechanism if
operational experience demonstrates the need.

---

## 3. Authentication Flow

### 3.1 Message-Level Authentication (EdDSA)

Every ARSIA message MUST carry a `security` object with `alg`, `kid`, and `sig` fields
as defined in ARSIA-Core.md §5.1.

A recipient MUST verify the message signature using the following procedure:

1.  Extract `security.kid` from the incoming message.
2.  Parse the `kid` to extract the agent-id prefix — everything before the `#`
    character.
3.  Verify that the extracted agent-id matches `message.from`. If it does not, reject
    the message with error code `"unauthorized"`.
4.  Retrieve the sender's JWKS from `GET /.well-known/arsia/jwks.json` on the sender's
    domain.
5.  Find the JWK entry with a matching `kid`.
6.  If no matching key is found, reject the message with error code `"unauthorized"`.
7.  Clone the message object and remove the `"security"` field from the clone.
8.  Canonicalize the clone using JSON Canonicalization Scheme (JCS) per RFC 8785.
9.  Verify the Ed25519 signature (from `security.sig`, base64url-decoded) over the
    canonicalized bytes using the public key from step 5.
10. If signature verification fails, reject the message with error code `"unauthorized"`.

**JWKS caching.** Recipients SHOULD cache JWKS responses for up to 1 hour (respecting
`Cache-Control` headers if present). On signature verification failure with a cached
key, the recipient SHOULD refetch the JWKS once before rejecting the message. This
handles the case where the sender has recently rotated keys and the recipient's cache
is stale.

> **Note:** Implementations that support a sandbox or development mode (e.g., open
> registration) MAY relax the EdDSA verification requirement for unauthenticated
> requests in non-production environments. When verification is relaxed,
> implementations MUST log a warning indicating that the request was processed without
> cryptographic verification. Production deployments MUST NOT use open registration
> mode.

### 3.2 Token-Based Authorization (OAuth 2.0)

For messages with `intent` of `"request"`, the sender MUST also present a Bearer or
DPoP-bound access token as defined in ARSIA-Core.md §6.

The receiving agent MUST verify the access token using the following procedure:

1. Extract the access token from the `Authorization` header of the HTTP request.
2. Verify the JWT signature (the token MUST be issued by a trusted Authorization
   Server).
3. Verify the `exp` claim (token MUST NOT be expired). Verify the `iat` claim (MUST NOT
   be in the future beyond the clock skew tolerance defined in ARSIA-Core.md §8.3).
   Verify the `nbf` claim if present (token MUST NOT be used before this time).
4. Verify that the `aud` claim equals `message.to` (the receiving agent's agent-id).
5. Verify that the `sub` claim equals `message.from` (the sending agent's agent-id).
6. Verify that the `scope` claim contains ALL strings listed in `message.capabilities`.
7. If any check fails, reject the request with error code `"unauthorized"` (for
   authentication failures) or `"forbidden"` (for insufficient scope/capabilities).

### 3.3 DPoP (Proof of Possession)

Demonstrating Proof of Possession (DPoP) per RFC 9449 is RECOMMENDED for all token
presentations. DPoP prevents token theft and replay attacks by binding the access token
to the sender's cryptographic key.

**DPoP proof JWT structure:**

Header:
```json
{
  "typ": "dpop+jwt",
  "alg": "EdDSA",
  "jwk": { "kty": "OKP", "crv": "Ed25519", "x": "{sender-public-key}" }
}
```

Payload:
```json
{
  "jti": "{UUID v4 — unique identifier for this proof}",
  "htm": "POST",
  "htu": "{HTTP target URI of the inbox endpoint}",
  "iat": 1711267200,
  "ath": "{base64url-encoded SHA-256 hash of the access token}"
}
```

**Verification by receiving agent:**

1. Verify the DPoP proof JWT signature using the `jwk` embedded in the proof header.
2. Verify that `htu` matches the inbox URL that received the request.
3. Verify that `htm` equals `"POST"`.
4. Verify that `iat` is within ±300 seconds of the current time.
5. Verify that `ath` equals the base64url-encoded SHA-256 hash of the access token.
6. Verify that the `jwk` in the proof header matches the `cnf` (confirmation) claim in
   the access token.

If any check fails, the receiving agent MUST reject the request with error code
`"unauthorized"`.

---

## 4. Identity in the Compliance Context

### 4.1 Owner Accountability

For any message where `compliance.audit_required` is `true`:

- The `IdentityRecord.owner_id` of BOTH the sender and receiver MUST be retrievable
  via their respective `/.well-known/arsia/identity` endpoints.
- The `owner_id` of both parties MUST be included in the corresponding audit record
  (ARSIA-State.md §7).
- This satisfies EU AI Act Art. 26(1): deployers of high-risk AI systems must use AI
  systems in accordance with the instructions for use, and the identity of the deployer
  must be determinable.

Implementations SHOULD cache identity records with the same policy as JWKS (up to 1
hour). For audit purposes, the identity record as retrieved at the time of message
processing MUST be used — not a stale cached version from a prior interaction.

### 4.2 Classification Consistency Rule

If `IdentityRecord.ai_system_classification` is `"high-risk"`:

- Every outbound `request` and `response` message from this agent MUST have
  `compliance.profile` set to at least `"EU-AI-ACT-HIGH-RISK"`.
- **Exception:** Messages with `intent` of `"error"` or `"event"` are exempt from this
  requirement, as these are informational and do not represent substantive agent actions.
- **Violation handling:** A receiving agent SHOULD log a compliance warning if a
  high-risk agent sends a message without the expected compliance profile. A receiving
  agent MAY reject such messages with error code `"invalid_request"` and
  `details: { "classification_mismatch": true }`.

If `IdentityRecord.ai_system_classification` is `"unacceptable-risk"`:

- The agent MUST NOT be deployed. This classification value exists solely for
  documentation and regulatory completeness.
- A receiving agent MUST reject ALL messages from an agent whose IdentityRecord declares
  `ai_system_classification` as `"unacceptable-risk"`, with error code `"forbidden"`.

### 4.3 Cross-Border Identity

When the sender's `jurisdiction` differs from the recipient's `jurisdiction`:

- Both agents' IdentityRecords MUST be independently verifiable. Each agent serves its
  own `/.well-known/arsia/identity` endpoint.
- Data residency constraints (`compliance.data_residency`) still apply as defined in
  ARSIA-Core.md §9.2. The sender's jurisdiction does NOT automatically determine data
  residency — residency is declared per message in the `compliance` field.
- No identity federation mechanism is defined in ARSIA Protocol v1.0. Cross-border
  identity verification relies on each party independently fetching and verifying the
  other's IdentityRecord and JWKS.

### 4.4 Deployer vs Owner Distinction

When `deployer_id` is set and differs from `owner_id`, the IdentityRecord declares a
split responsibility model:

- The **deployer** is the entity that operates the agent infrastructure on behalf of the
  owner. EU AI Act Art. 26 obligations (operational responsibilities — monitoring,
  logging, human oversight) fall on the deployer.
- The **owner** (referred to as "provider" in the EU AI Act) is the entity that designed
  or commissioned the AI system. EU AI Act Art. 16 obligations (design-time
  responsibilities — risk management, data governance, technical documentation) fall on
  the owner.
- Both `deployer_id` and `owner_id` MUST be recorded in audit events for messages
  involving this agent.
- **Example:** A SaaS company (`deployer_id: "DE812345678"`) operates a risk assessment
  agent on behalf of a bank (`owner_id: "PT501234567"`). The SaaS company is responsible
  for operational monitoring; the bank is responsible for the agent's design-time
  compliance.

---

## 5. Identity Conformance Tests

The following test cases define conformance requirements for the Identity primitive. Each
test is identified by a unique `test_id` and specifies preconditions, actions, and
expected results. These tests are normative — a conformant implementation MUST pass all
tests at the applicable conformance level.

### IDENTITY-01: Valid identity record retrieval

| Field           | Value                                                    |
|-----------------|----------------------------------------------------------|
| **test_id**     | `IDENTITY-01`                                            |
| **description** | Verify that the identity endpoint returns a valid record |
| **preconditions** | Agent is running with a valid IdentityRecord configured |
| **action**      | Send `GET /.well-known/arsia/identity` to the agent      |
| **expected**    | HTTP 200 OK. Response body is valid JSON conforming to `arsia-identity-record.schema.json`. Response includes `X-ARSIA-Sig` header with a non-empty base64url value. `Content-Type` is `application/json`. |

### IDENTITY-02: Identity record signature verification

| Field           | Value                                                              |
|-----------------|--------------------------------------------------------------------|
| **test_id**     | `IDENTITY-02`                                                      |
| **description** | Verify that X-ARSIA-Sig correctly signs the identity record        |
| **preconditions** | IdentityRecord served with `X-ARSIA-Sig` header                  |
| **action**      | Compute SHA-256 of response body. Base64url-decode `X-ARSIA-Sig`. Retrieve agent's public key from JWKS. Verify Ed25519 signature over the hash. |
| **expected**    | Signature verification succeeds.                                   |

### IDENTITY-03: Message signature verification (valid)

| Field           | Value                                                    |
|-----------------|----------------------------------------------------------|
| **test_id**     | `IDENTITY-03`                                            |
| **description** | Verify that a correctly signed message is accepted       |
| **preconditions** | Agent A has a valid key pair published in JWKS. Agent A sends a signed message to Agent B. |
| **action**      | Agent B performs signature verification per §3.1.        |
| **expected**    | Verification succeeds. Message is accepted for processing. |

### IDENTITY-04: Message signature verification (invalid signature)

| Field           | Value                                                        |
|-----------------|--------------------------------------------------------------|
| **test_id**     | `IDENTITY-04`                                                |
| **description** | Verify that a message with a corrupted signature is rejected |
| **preconditions** | Message with a valid structure but corrupted `security.sig` value (one or more bytes altered). |
| **action**      | Receiving agent attempts signature verification per §3.1.    |
| **expected**    | Verification fails. Message is rejected with error code `"unauthorized"`. |

### IDENTITY-05: kid mismatch (from agent ≠ key prefix)

| Field           | Value                                                          |
|-----------------|----------------------------------------------------------------|
| **test_id**     | `IDENTITY-05`                                                  |
| **description** | Verify that a kid not matching the sender agent-id is rejected |
| **preconditions** | Message `from` is `agent:acme.billing`. Message `security.kid` is `agent:contoso.crm#key1`. |
| **action**      | Receiving agent performs step 3 of §3.1 (kid prefix check).   |
| **expected**    | kid prefix `agent:contoso.crm` does not match `message.from` `agent:acme.billing`. Message is rejected with error code `"unauthorized"`. |

### IDENTITY-06: Classification consistency (high-risk without compliance profile)

| Field           | Value                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **test_id**     | `IDENTITY-06`                                                         |
| **description** | Verify classification consistency check for high-risk agents          |
| **preconditions** | Sender agent's IdentityRecord has `ai_system_classification: "high-risk"`. Sender sends a `request` message without `compliance.profile`. |
| **action**      | Receiving agent retrieves sender's IdentityRecord and checks classification consistency per §4.2. |
| **expected**    | Receiving agent logs a compliance warning. Receiving agent MAY reject the message with error code `"invalid_request"` and `details: { "classification_mismatch": true }`. |

### IDENTITY-07: Key rotation (both keys valid during overlap)

| Field           | Value                                                             |
|-----------------|-------------------------------------------------------------------|
| **test_id**     | `IDENTITY-07`                                                     |
| **description** | Verify that both old and new keys are accepted during overlap     |
| **preconditions** | Agent has rotated from `key1` to `key2`. Both keys are present in JWKS. Overlap period (24h minimum) has not elapsed. |
| **action**      | Send a message signed with `key1`. Then send a message signed with `key2`. |
| **expected**    | Both messages are accepted. Both signatures verify successfully.  |

### IDENTITY-08: Key rotation (old key rejected after overlap)

| Field           | Value                                                             |
|-----------------|-------------------------------------------------------------------|
| **test_id**     | `IDENTITY-08`                                                     |
| **description** | Verify that an old key is rejected after the overlap period       |
| **preconditions** | Overlap period (24h+) has elapsed. `key1` has been removed from JWKS. Only `key2` remains. |
| **action**      | Send a message signed with `key1`.                                |
| **expected**    | Receiving agent fetches JWKS and finds no entry for `key1`. Message is rejected with error code `"unauthorized"`. |

---

## 6. Certificate Trust Levels

Certificate trust levels extend the base EdDSA identity model defined in §2.
Level 1 (self-signed) is the default and requires no changes to existing agents.
Levels 2 and 3 add verifiable organisational identity on top of cryptographic
signing.

The ARSIA Protocol defines three trust levels for agent identity. Each level builds
on the previous one, adding stronger identity assurance. Implementations MUST support
Level 1. Implementations SHOULD support Level 2. Implementations MAY support Level 3.

### 6.1 Level 1 — Self-Signed (Default)

Level 1 is the current protocol behaviour as defined in §1–§3 above. No changes
are required to support Level 1.

**Identity model.** The agent generates an Ed25519 keypair, publishes the public key
via its JWKS endpoint (`/.well-known/arsia/jwks.json`), and signs all outbound
messages with the corresponding private key. The IdentityRecord served at
`/.well-known/arsia/identity` does not contain a `certificate_chain` field, or the
field is present but empty.

**Trust model.** The EdDSA signature proves that the message was produced by the
holder of the private key corresponding to the public key in the JWKS. It does NOT
prove WHO holds that key. Level 1 provides message integrity and sender consistency,
but no external identity assurance.

**Use cases.** Development, sandbox environments, prototypes, internal agents behind
a trusted network boundary, and scenarios where identity assurance beyond cryptographic
consistency is not required.

**Verification.** EdDSA signature validation per §3.1 above. No additional
steps.

### 6.2 Level 2 — CA-Signed (Enterprise)

Level 2 adds a certificate chain to the IdentityRecord, where a Certificate Authority
(CA) vouches for the binding between an agent's identity and its public key.

**Certificate requirements.** The leaf certificate in the chain MUST meet the following
requirements:

- **Subject Alternative Name (SAN):** MUST contain the agent's `agent_id` as a
  Uniform Resource Identifier (URI) in the format `agent:{domain}.{name}`. For
  example, `URI:agent:acme.billing`.

- **Subject — Organization (O):** MUST match the `owner_name` field from the agent's
  IdentityRecord, or the `owner_id` field if the Organization is encoded as a legal
  entity identifier.

- **Key Usage:** The `digitalSignature` bit MUST be set. The `keyCertSign` bit MUST
  NOT be set (the agent certificate is an end-entity certificate, not a CA).

- **Basic Constraints:** `CA:FALSE` MUST be set with the `critical` flag.

- **Public key:** The public key encoded in the certificate MUST be identical to the
  Ed25519 public key published at the agent's JWKS endpoint. Specifically, the raw
  32-byte public key extracted from the certificate MUST equal the base64url-decoded
  value of the `x` field of the JWK entry whose `kid` matches the agent's current
  signing key.

- **Extended Key Usage:** `id-kp-serverAuth` is OPTIONAL. Implementations SHOULD NOT
  require it.

**Trust model.** The CA vouches for the binding between the `agent_id`, the legal
entity (`owner_id`/`owner_name`), and the public key. The strength of this binding
depends on the CA's certificate policy and issuance practices. Enterprise CAs, consortium
CAs, and sandbox CAs all qualify for Level 2.

**Use cases.** Agents deployed within an enterprise, agents operated by business
partners sharing a common CA, and sandbox environments demonstrating the certificate
flow.

**Verification.** EdDSA signature validation (Level 1) PLUS certificate chain
validation PLUS public key consistency check. See §6.4.1 for the full procedure.

### 6.3 Level 3 — Qualified Certificate (eIDAS)

Level 3 provides legal-grade identity binding under EU Regulation 910/2014 (eIDAS).
The certificate is issued by a Qualified Trust Service Provider (QTSP) listed on a
Member State's Trusted List.

**Certificate requirements.** All Level 2 requirements apply, plus:

- **QcStatements extension:** The leaf certificate MUST include the `QcStatements`
  extension per ETSI EN 319 412-5, indicating that it is a qualified certificate for
  electronic seals (`id-etsi-qcs-QcCompliance`).

- **Issuer:** The issuing CA MUST be a QTSP listed on the Trusted List of the Member
  State where the QTSP is established, published in accordance with Commission
  Implementing Decision (EU) 2015/1505.

- **Owner identity verification:** The `owner_id` in the IdentityRecord MUST be
  verifiable against official registers. For EU VAT numbers, verification against VIES
  (VAT Information Exchange System). For LEIs, verification against the GLEIF database.
  The QTSP is responsible for performing this verification at certificate issuance time.

**Trust model.** The certificate holder is a legally identified entity. Under eIDAS
Art. 35, a qualified electronic seal has the legal presumption of integrity and
correctness of origin. This is the strongest identity assurance available in the
ARSIA Protocol.

**Use cases.** Regulated agents, interactions with EU public authorities, formal
compliance evidence, cross-border agent interactions requiring legal identity
assurance, and scenarios where audit trails must reference legally verifiable entities.

**ARSIA Protocol scope.** The ARSIA Protocol does NOT operate as a Certificate
Authority and does NOT issue certificates at any level. This specification defines
WHAT constitutes a valid certificate at each level and HOW to verify it. The
acquisition of certificates from CAs or QTSPs is an operational concern outside the
protocol's scope.

**Future considerations.** Integration with the EU Digital Identity Wallet framework
(eIDAS 2.0, European Digital Identity Regulation, anticipated 2026-2027) is expected
to simplify Level 3 adoption by providing a standardised mechanism for presenting
qualified certificates and verifiable credentials.

**Verification.** All Level 2 verification steps PLUS OCSP/CRL revocation status
check PLUS QcStatements validation. See §6.4.1 for the full procedure.

### 6.4 Verification Procedure

#### 6.4.1 Step-by-Step Verification

A verifier MUST execute the following steps when processing a message from a peer
agent:

1. **EdDSA signature validation.** Verify the message signature per
   §3.1 above. If verification fails, reject the message with error code
   `"unauthorized"`. If verification succeeds, proceed.

2. **Retrieve the peer's IdentityRecord.** Fetch the peer's IdentityRecord from
   `GET /.well-known/arsia/identity` (respecting cache headers). Extract the
   `certificate_chain` field.

3. **If `certificate_chain` is absent or empty:** The computed `trust_level` is **1**.
   Verification is complete. No further certificate checks are required.

4. **If `certificate_chain` is present and non-empty:**

   a. **Parse leaf certificate.** Parse the PEM-encoded certificate at index 0 of the
      chain. If parsing fails, reject with error code `"certificate_invalid"` and
      `details: { "reason": "malformed_leaf_certificate" }`.

   b. **Validate certificate chain.** Verify that each certificate in the chain is
      signed by the next certificate in the chain (or by a certificate in the local
      trust store for the last certificate). If chain validation fails, reject with
      error code `"certificate_invalid"` and
      `details: { "reason": "chain_validation_failed" }`.

   c. **Verify certificate validity period.** Check that the leaf certificate's
      `notBefore` is in the past and `notAfter` is in the future. If the certificate
      is expired, reject with error code `"certificate_expired"`.

   d. **Verify public key consistency.** Extract the public key from the leaf
      certificate. Compare it to the public key published at the peer's JWKS endpoint
      (the key identified by the `kid` used in the message's `security` field). The
      raw 32-byte Ed25519 public keys MUST be identical. If they differ, reject with
      error code `"key_mismatch"`.

   e. **Verify agent_id in SAN.** Check that the leaf certificate's Subject
      Alternative Name (SAN) extension contains the peer's `agent_id` as a URI entry.
      The URI value MUST match the `agent_id` field from the peer's IdentityRecord.
      If the agent_id is not found in the SAN, reject with error code
      `"certificate_invalid"` and `details: { "reason": "agent_id_not_in_san" }`.

   f. **Determine trust level.** If all checks in steps (a) through (e) pass, the
      computed `trust_level` is **2**.

   g. **Check for QcStatements.** If the leaf certificate contains a `QcStatements`
      extension per ETSI EN 319 412-5, indicating a qualified certificate, the
      computed `trust_level` is **3**. Proceed to step (h).

   h. **Revocation check (Level 3 only).** For Level 3 certificates, the verifier
      MUST check the certificate's revocation status via OCSP or CRL. If the
      certificate is revoked, reject with error code `"certificate_revoked"`.
      OCSP stapling is RECOMMENDED to reduce latency. If OCSP and CRL are both
      unavailable and the certificate includes the `id-pe-authorityInfoAccess`
      extension, the verifier SHOULD treat the certificate as potentially revoked
      and MAY downgrade to Level 2.

#### 6.4.2 Trust Store Configuration

Each ARSIA-compliant agent that supports Level 2 or Level 3 verification MUST
maintain a local trust store containing the CA certificates it trusts.

Trust store configuration is an operational concern — the ARSIA Protocol does not
mandate a specific trust store format, location, or management mechanism.
Implementations SHOULD support at least one of the following:

- A directory of PEM-encoded CA certificate files.
- An operating system trust store (e.g., macOS Keychain, Linux ca-certificates).
- A configuration property listing trusted CA certificate PEM strings.

**Policy enforcement.** An agent MAY enforce a minimum trust level policy, rejecting
messages from agents below a configured threshold. For example, an agent in a
regulated environment MAY require `trust_level >= 2` for all incoming requests.

An agent MUST NOT reject messages solely because `trust_level` is 1 unless the agent
has been explicitly configured with a minimum trust level policy. The default behaviour
MUST be to accept messages at all trust levels.

#### 6.4.3 Error Handling

The following error codes are defined for certificate-related verification failures.
These error codes are used in the ARSIA error message format defined in
ARSIA-Core.md §8.

| Error Code               | Condition                                            |
|--------------------------|------------------------------------------------------|
| `"certificate_invalid"`  | Malformed certificate, chain validation failure, or agent_id not in SAN |
| `"certificate_expired"`  | Leaf certificate `notAfter` is in the past           |
| `"key_mismatch"`         | Public key in certificate does not match JWKS key    |
| `"certificate_revoked"`  | OCSP or CRL indicates the certificate is revoked     |

All certificate error responses MUST include a `details` object with a `reason`
string providing a human-readable explanation of the specific failure. Error responses
SHOULD be signed with the receiving agent's own key, following the standard ARSIA
error message format.

### 6.5 IdentityRecord Extension

#### 6.5.1 New Field: certificate_chain

**`certificate_chain`** (array of strings, OPTIONAL)
:   An ordered array of PEM-encoded X.509 certificates forming the certificate chain
    for this agent's identity.

    The array MUST be ordered as follows:
    1. **Index 0:** The leaf (end-entity) certificate — the agent's own certificate.
    2. **Index 1 .. n-1:** Intermediate CA certificates, ordered from the certificate
       that signed the leaf to the certificate closest to the root.
    3. **Index n (last):** The root CA certificate. The root MAY be omitted if it is a
       well-known CA whose certificate is expected to be in the verifier's trust store.

    Each string in the array MUST be a complete PEM-encoded certificate, including the
    `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----` markers.

    When `certificate_chain` is absent or empty, the agent is at trust Level 1
    (self-signed). When present and valid, the agent is at trust Level 2 or Level 3,
    depending on the certificate contents.

    All certificates in the chain MUST be valid at the time the IdentityRecord is
    served. An agent MUST NOT serve an IdentityRecord containing expired certificates.
    An agent SHOULD update its IdentityRecord when any certificate in the chain is
    within 30 days of expiry.

#### 6.5.2 Trust Level Computation

The trust level is a property computed by the verifier, NOT declared by the agent.
Agents MUST NOT include a `trust_level` field in their IdentityRecord. The
`trust_level` is the output of the verification procedure defined in §6.4.1.

| Condition                                                | Trust Level |
|----------------------------------------------------------|-------------|
| `certificate_chain` absent or empty                      | 1           |
| Valid chain, all §6.2 checks pass, no QcStatements       | 2           |
| Valid chain, all §6.2 checks pass, QcStatements present  | 3           |

A verifier MAY cache the computed trust level for the duration of the IdentityRecord's
`Cache-Control` header, but MUST recompute it when the IdentityRecord is refreshed.

#### 6.5.3 Schema Update

The following property is added to `arsia-identity-record.schema.json`:

```json
"certificate_chain": {
  "type": "array",
  "items": {
    "type": "string",
    "pattern": "^-----BEGIN CERTIFICATE-----"
  },
  "description": "PEM-encoded X.509 certificate chain. Leaf certificate first, intermediates next, root last (or omitted if well-known). Defined in ARSIA-Identity.md §6.5.1."
}
```

This field is OPTIONAL. The `required` array in the schema is unchanged. The addition
is fully backward-compatible — existing IdentityRecords without `certificate_chain`
remain valid.

### 6.6 Conformance Tests

The following test cases extend the conformance tests defined in §5 above.
Each test is normative — a conformant implementation that claims Level 2 support MUST
pass tests IDENTITY-09 through IDENTITY-12.

#### IDENTITY-09: certificate_chain field accepted

| Field           | Value                                                              |
|-----------------|--------------------------------------------------------------------|
| **test_id**     | `IDENTITY-09`                                                      |
| **description** | Verify that a Level 1 agent processes messages normally when the peer's IdentityRecord contains a certificate_chain |
| **preconditions** | Agent A is Level 1 (no certificate). Agent B is Level 2 (has certificate_chain). |
| **action**      | Agent A sends a correctly signed message to Agent B. Agent B retrieves Agent A's IdentityRecord (no certificate_chain). |
| **expected**    | Agent B accepts the message. The absence of `certificate_chain` does not cause rejection. Computed `trust_level` for Agent A is 1. |

#### IDENTITY-10: Level 2 certificate chain verification

| Field           | Value                                                              |
|-----------------|--------------------------------------------------------------------|
| **test_id**     | `IDENTITY-10`                                                      |
| **description** | Verify that a CA-signed certificate chain is validated correctly    |
| **preconditions** | Agent A has a valid certificate chain (leaf + CA cert). Agent B's trust store contains the CA certificate. |
| **action**      | Agent A sends a signed message. Agent B retrieves Agent A's IdentityRecord, validates the certificate chain per §6.4.1. |
| **expected**    | Chain validation succeeds. Public key in certificate matches JWKS key. `agent_id` found in SAN. Computed `trust_level` is 2. |

#### IDENTITY-11: Public key mismatch detection

| Field           | Value                                                              |
|-----------------|--------------------------------------------------------------------|
| **test_id**     | `IDENTITY-11`                                                      |
| **description** | Verify that a certificate with a different public key than JWKS is rejected |
| **preconditions** | Agent A has a certificate chain, but the public key in the leaf certificate does NOT match the public key in Agent A's JWKS. |
| **action**      | Agent B retrieves Agent A's IdentityRecord and performs §6.4.1 verification. |
| **expected**    | Verification fails at step 4d. Agent B rejects with error code `"key_mismatch"`. |

#### IDENTITY-12: Certificate expiry detection

| Field           | Value                                                              |
|-----------------|--------------------------------------------------------------------|
| **test_id**     | `IDENTITY-12`                                                      |
| **description** | Verify that an expired certificate is rejected                     |
| **preconditions** | Agent A has a certificate chain where the leaf certificate's `notAfter` is in the past. |
| **action**      | Agent B retrieves Agent A's IdentityRecord and performs §6.4.1 verification. |
| **expected**    | Verification fails at step 4c. Agent B rejects with error code `"certificate_expired"`. |

### 6.7 Sandbox CA Integration

#### 6.7.1 Sandbox CA Behaviour

The ARSIA sandbox local CA (`packages/sandbox/local-ca/`) is a Level 2 CA designed
for development and testing. It demonstrates the full certificate-based trust flow
without requiring external CA infrastructure.

**Certificate issuance.** The sandbox CA issues certificates to agents connecting to
the sandbox environment. Issued certificates comply with §6.2:

- SAN includes the agent's `agent_id` as a URI.
- Subject Organization (O) is set to the agent's `owner_name`.
- Key Usage includes `digitalSignature`.
- Basic Constraints: `CA:FALSE`.
- Certificate validity: 90 days.
- Public key: the Ed25519 public key extracted from the agent's JWKS.

**API.** The sandbox CA exposes:

- `POST /issue` — Issue a certificate for an agent. Request body includes `agent_id`
  and `public_key_pem`. Response includes `certificate_pem`, `chain` (array containing
  the leaf certificate and the CA certificate), `agent_id`, `valid_days`, and
  `serial_number`.
- `GET /ca-cert` — Return the root CA certificate in PEM format.
- `GET /health` — Health check.

**Security warning.** The sandbox CA is a development-only tool. It performs NO
identity verification on certificate requests. It generates a new root keypair on
every startup. Certificates issued by the sandbox CA MUST NOT be trusted outside the
sandbox environment. Production deployments MUST use a properly operated CA with
appropriate certificate policies.

#### 6.7.2 Sandbox Trust Store

The sandbox test agent is pre-configured to trust the sandbox CA certificate. The
sandbox dashboard displays the certificate status for connected agents, showing
`"Local Sandbox CA (Level 2)"` for agents with sandbox-issued certificates.

The sandbox environment demonstrates:

- Automatic certificate issuance on agent registration.
- IdentityRecord population with `certificate_chain`.
- Level 2 verification between the test agent and the dashboard API.
- Certificate status display in the dashboard UI.

### 6.8 Security Considerations

**Level 1 limitations.** Self-signed identity (Level 1) provides cryptographic
message integrity and sender consistency, but NO identity assurance. Any entity that
can serve an IdentityRecord and JWKS can impersonate any agent_id. Level 1 is
appropriate for development and trusted environments, but SHOULD NOT be relied upon
for identity verification in production deployments handling sensitive data or
regulated operations.

**Level 2 trust dependencies.** CA-signed identity (Level 2) is only as trustworthy
as the issuing CA. Enterprise CAs are not publicly audited and their certificate
policies are not standardised. Agents relying on Level 2 SHOULD understand the
issuance practices of the CAs in their trust store. Certificate pinning
(associating a specific CA certificate or public key with an agent, rather than
trusting any CA in the trust store) is RECOMMENDED for Level 2 deployments in
production environments.

**Level 3 legal standing.** Qualified certificates (Level 3) under eIDAS carry legal
presumptions of integrity and origin. However, these presumptions apply to the
certificate holder's identity, not to the correctness of the AI agent's outputs.
Level 3 assures WHO is operating the agent, not WHAT the agent does.

**Private key protection.** At all trust levels, the private key MUST NOT be
transmitted or included in any protocol message or IdentityRecord. Only the
certificate (containing the public key) is shared. The private key storage
requirements defined in §2.1 above apply regardless of trust level.

**OCSP stapling.** For Level 3 verification, OCSP stapling (where the certificate
holder periodically fetches and caches OCSP responses, presenting them alongside the
certificate) is RECOMMENDED. This reduces the privacy risk of verifiers contacting
OCSP responders directly (which would reveal which agents are communicating) and
reduces verification latency.

**Certificate lifecycle.** Agents SHOULD monitor their certificate's validity period
and initiate renewal before expiry. A certificate that expires while the agent is
operational will cause verification failures for all peers. Agents SHOULD update
their IdentityRecord with the new certificate chain before the old certificate
expires, allowing for a transition period.

---

## 7. External Agent Onboarding

This section defines the normative onboarding flow for external AI agents
entering a corporate ARSIA deployment. It composes the Identity, Compliance,
Actions, Routing, and audit primitives defined in §1-§6 and in the companion
specifications into a six-phase evaluation and admission protocol.

### 7.1 Onboarding Model Overview

#### 7.1.1 Roles

The onboarding flow involves three distinct agent roles. Each role has specific protocol
obligations.

**External Agent.** An ARSIA-conformant agent operated by an individual or third party,
requesting access to a corporate ARSIA deployment. The external agent MUST serve all
discovery endpoints specified in ARSIA-Core.md §7: the discovery endpoint
(`/.well-known/arsia`), the JWKS endpoint (`/.well-known/arsia/jwks.json`), and the
identity endpoint (`/.well-known/arsia/identity` per ARSIA-Identity.md §1.3). The
external agent MUST have a valid IdentityRecord (ARSIA-Identity.md §1.2) with all
REQUIRED fields populated, including `ai_system_classification`. The external agent
SHOULD expose an audit trail query endpoint (`/.well-known/arsia/audit` per ARSIA-State.md
§7.4) to enable provenance verification.

**Onboarding Gateway.** An ARSIA agent operated by the receiving organization that
evaluates external agents through the six-phase onboarding flow defined in §7.2–§7.7 of this
specification. The gateway MUST have the capability `arsiaprotocol.onboarding.evaluate` declared
in its discovery response (ARSIA-Core.md §7.2). The gateway MUST be authorized to issue
scoped access tokens on behalf of the organization's infrastructure. The gateway MUST
record all onboarding decisions as audit records per ARSIA-State.md §7.1.

**Infrastructure Router.** An ARSIA agent operated by the receiving organization that
enforces capability restrictions on admitted agents during the operational phase. The
infrastructure router MUST verify Bearer tokens presented by external agents by calling
the gateway's token verification endpoint (`/v1/arsia/verify-token`). The router MUST
reject any request whose required capabilities are not present in the token's scope,
responding with error code `"forbidden"` (ARSIA-Core.md §11.2). The router MUST NOT
accept messages from agents that have not completed the onboarding flow.

#### 7.1.2 Trust Model

External agents are UNTRUSTED by default. No prior configuration, verbal agreement, or
manual approval establishes trust. Trust is established exclusively through protocol-level
verification during the six-phase onboarding flow.

The trust establishment proceeds as follows:

1. **Identity trust** is established when the gateway successfully verifies the external
   agent's IdentityRecord signature (Phase 1). This confirms that the agent controls the
   Ed25519 private key corresponding to the public key published in its JWKS.

2. **Compliance trust** is established when the external agent passes all five conformance
   checks (Phase 2). This confirms that the agent correctly implements the ARSIA Protocol's
   compliance semantics — envelope structure, signature verification, human oversight
   signaling, audit trail generation, and classification consistency.

3. **Capability trust** is established when the gateway applies its CapabilityPolicy to
   scope the agent's effective permissions (Phase 3). The agent is granted only the
   intersection of its declared capabilities and the organization's policy.

4. **Operational trust** is maintained through token-scoped enforcement by the
   infrastructure router (Phase 6). Every request is verified against the token's scope.
   Trust is revocable at any time by revoking the token.

The gateway MUST NOT grant trust based on out-of-band information such as email
confirmations, verbal agreements, or manual configuration entries. All trust decisions
MUST be traceable through the audit trail.

#### 7.1.3 Relationship to Existing Primitives

The onboarding flow does NOT define new message types, new envelope fields, or new error codes.
It composes existing ARSIA primitives into a structured flow:

- **`approval_decision` intent** (ARSIA-Core.md §4.1, ARSIA-Actions.md §3.3) is used for
  the onboarding decision in Phase 5.
- **`pending_approval` intent** (ARSIA-Core.md §4.1, ARSIA-Actions.md §3.2) is used for
  human oversight signaling during the conformance test in Phase 2.
- **The `compliance` envelope field** (ARSIA-Core.md §4.3.6) carries regulatory metadata
  on all onboarding-related messages.
- **The capability model** (ARSIA-Actions.md §1) governs capability scoping in Phase 3 and
  enforcement in Phase 6.
- **The IdentityRecord** (ARSIA-Identity.md §1.2) provides identity verification in
  Phase 1.
- **The ArsiaAuditRecord** (ARSIA-State.md §7.1) provides the audit trail format for
  all onboarding events.

Implementations MAY extend the onboarding flow with additional organization-specific
checks, provided the six normative phases defined in §7.2–§7.7 are executed in order and their
results are recorded in the audit trail.

### 7.2 Phase 1 — Discovery & Identity Verification

The onboarding flow consists of six phases executed sequentially by the onboarding gateway.
Each phase has specific success and failure criteria. If any of Phases 1 through 4 fails,
the gateway MUST proceed directly to Phase 5 and emit a denial decision. Phases MUST NOT
be reordered or skipped.

The gateway initiates onboarding by verifying the external agent's discovery endpoints and
identity record. The gateway MUST perform the following steps in order:

**Step 1 — Discovery metadata.** Fetch `GET {agent_base_url}/.well-known/arsia` and
verify that the response is valid JSON conforming to the ARSIA discovery response format
(ARSIA-Core.md §7.1). The response MUST include `agent_id`, `protocol_version`, and
`capabilities` fields. If the fetch fails or the response is invalid, the gateway MUST
deny onboarding with `denial_reason = "discovery_failed"`.

**Step 2 — Identity record retrieval.** Fetch `GET {agent_base_url}/.well-known/arsia/identity`
and verify that the response is valid JSON conforming to `arsia-identity-record.schema.json`
(ARSIA-Identity.md §1.2). The response MUST include the `X-ARSIA-Sig` header. If the
fetch fails or the response does not conform to the schema, the gateway MUST deny
onboarding with `denial_reason = "identity_verification_failed"`.

**Step 3 — JWKS retrieval.** Fetch `GET {agent_base_url}/.well-known/arsia/jwks.json` and
verify that the response is a valid JWK Set per RFC 7517 containing at least one Ed25519
key entry (ARSIA-Identity.md §2.3). If the fetch fails or no valid Ed25519 key is found,
the gateway MUST deny onboarding with `denial_reason = "identity_verification_failed"`.

**Step 4 — Identity signature verification.** Verify the `X-ARSIA-Sig` header on the
identity record response using the procedure defined in ARSIA-Identity.md §1.3:

1. Compute the SHA-256 hash of the raw response body bytes.
2. Base64url-decode the value of the `X-ARSIA-Sig` header.
3. Retrieve the agent's public key from the JWKS obtained in Step 3.
4. Verify the Ed25519 signature over the SHA-256 hash.

If verification fails, the gateway MUST deny onboarding with
`denial_reason = "identity_verification_failed"`.

**Step 5 — kid consistency check.** Verify that the `kid` prefix (everything before the
`#` character) in at least one JWKS entry matches the `agent_id` in the identity record.
This ensures the cryptographic identity is bound to the technical identity per
ARSIA-Identity.md §1.1. If no match is found, the gateway MUST deny onboarding with
`denial_reason = "identity_verification_failed"`.

**Step 6 — Classification check.** Verify that the `ai_system_classification` field in
the IdentityRecord is NOT `"unacceptable-risk"`. Per ARSIA-Identity.md §4.2, agents
classified as unacceptable-risk MUST NOT be deployed. If the classification is
`"unacceptable-risk"`, the gateway MUST deny onboarding with
`denial_reason = "unacceptable_risk_classification"`.

If all six steps succeed, Phase 1 passes and the gateway proceeds to Phase 2.

### 7.3 Phase 2 — Compliance Conformance Test

The gateway runs five conformance checks against the external agent to verify that it
correctly implements ARSIA Protocol compliance semantics. Each check produces a result
object with the following structure:

```json
{
  "test_id": "CHECK-01",
  "status": "pass",
  "details": "Response envelope validated successfully",
  "duration_ms": 42.5
}
```

The `status` field MUST be one of `"pass"`, `"fail"`, or `"skip"`. A check MAY be skipped
only when its preconditions are not met (e.g., CHECK-05 is skipped when the agent is not
classified as high-risk).

**CHECK-01 — Envelope validity.** The gateway sends a `request` message to the external
agent with a known payload type (e.g., `"arsiaprotocol.onboarding/ping"`) and verifies the
response:

- The response MUST have `intent` set to `"response"`.
- The response MUST have `correlation_id` set to the request's `id`.
- The `id` field MUST be a valid UUID.
- The `v`, `ts`, `from`, and `to` fields MUST be present.
- The `from` field MUST match the external agent's `agent_id`.

If any condition is not met, the check fails.

**CHECK-02 — Signature verification.** The gateway verifies the response's `security.sig`
against the external agent's public key using the verification procedure from
ARSIA-Identity.md §3.1:

1. Extract `security.kid` from the response.
2. Verify that the kid prefix matches `message.from`.
3. Look up the corresponding public key in the agent's JWKS.
4. Remove the `security` field from a clone of the response, canonicalize per RFC 8785.
5. Verify the Ed25519 signature over the canonicalized bytes.

If verification fails, the check fails.

**CHECK-03 — Human oversight compliance.** The gateway sends a `request` message for a
capability that the gateway's policy marks as `oversight_required`. The external agent
MUST respond with a `pending_approval` message (ARSIA-Actions.md §3.2), NOT with a direct
`response`. This verifies that the agent implements human oversight signaling per EU AI
Act Article 14.

- The `pending_approval` message MUST have `intent` set to `"pending_approval"`.
- The `correlation_id` MUST match the request's `id`.
- The `payload.type` SHOULD be `"arsiaprotocol.oversight/pending"`.
- The `expires_at` field MUST be present and set to a future timestamp.

If the agent responds with a direct `response` instead of `pending_approval`, the check
fails. This indicates the agent executes without waiting for human approval on actions
that require oversight.

**CHECK-04 — Audit trail format.** The gateway fetches
`GET {agent_base_url}/.well-known/arsia/audit` (ARSIA-State.md §7.4) and verifies:

- The response MUST be a JSON array of audit records.
- Each record MUST include the fields defined in ArsiaAuditRecord
  (ARSIA-State.md §7.1): `record_id`, `message_id`, `event_type`, `from_agent`,
  `to_agent`, `intent`, `payload_type`, `payload_hash`, `compliance_profile`,
  `processed_at`, `retained_until`, `operator_id`.
- Records MUST use `payload_hash` (a hash of the payload), NOT the raw payload content.
  This satisfies ARSIA-State.md §7.1 immutability requirements.

If the endpoint is not available (HTTP 404), this check is marked as `"skip"` — the audit
trail endpoint is RECOMMENDED but not REQUIRED at Core Conformance level
(ARSIA-Core.md §12.1). If the endpoint returns data that does not conform, the check
fails.

**CHECK-05 — Classification consistency.** This check applies only when the external
agent's `ai_system_classification` (from the IdentityRecord retrieved in Phase 1) is
`"high-risk"`. Per ARSIA-Identity.md §4.2:

- The gateway verifies that the response from CHECK-01 includes
  `compliance.profile` set to at least `"EU-AI-ACT-HIGH-RISK"`.
- If the agent is classified as high-risk but sends messages without the required
  compliance profile, the check fails.

If the agent is not classified as high-risk, this check is marked as `"skip"`.

**Aggregate result.** ALL checks with status `"pass"` or `"skip"` MUST be achieved for
Phase 2 to pass. If any check has status `"fail"`, the gateway MUST deny onboarding with
`denial_reason = "conformance_failed"` and include the full check results in the denial
payload.

### 7.4 Phase 3 — Capability Scoping

The gateway applies its CapabilityPolicy (defined in §8) to determine the external
agent's effective permissions within the corporate deployment.

The gateway evaluates each capability declared in the external agent's discovery response
(`capabilities` array from ARSIA-Core.md §7.2) against the CapabilityPolicy. Each
capability falls into one of three categories:

- **`allowed`** — The agent MAY invoke this capability without additional oversight during
  the operational phase.
- **`oversight_required`** — The agent MAY invoke this capability, but each invocation
  MUST trigger a `pending_approval` flow (ARSIA-Actions.md §3.2) before execution.
- **`prohibited`** — The agent MUST NOT invoke this capability. The infrastructure router
  MUST reject requests for prohibited capabilities with error code `"forbidden"`.

The **effective capabilities** granted to the agent are computed as:

```
effective_capabilities = (agent_declared ∩ policy_allowed) ∪ (agent_declared ∩ policy_oversight_required)
```

That is, the intersection of the agent's declared capabilities with the capabilities
listed in the policy as either `allowed` or `oversight_required`. Capabilities not listed
in the policy are excluded by default (**deny-by-default**). Capabilities listed in the
policy as `prohibited` are always excluded, even if the agent declares them.

The gateway MUST partition the effective capabilities into two lists:

- `freely_allowed` — capabilities with policy status `allowed`.
- `oversight_required` — capabilities with policy status `oversight_required`.

Both lists are included in the onboarding decision (Phase 5) and encoded in the issued
token's scope.

### 7.5 Phase 4 — Provenance Verification

The gateway records the external agent's provenance — temporal evidence of the agent's
existence and operational history. Provenance provides additional context for the
onboarding decision but is not a pass/fail gate.

The gateway MUST record:

- **`identity_created_at`** — The `created_at` field from the agent's IdentityRecord
  (ARSIA-Identity.md §1.2). This establishes when the agent's identity was first created.

- **`earliest_audit_record`** — The `processed_at` timestamp of the earliest audit record
  returned by the agent's audit endpoint (`/.well-known/arsia/audit`), if available. This
  establishes the earliest known operational activity of the agent.

- **`provenance_verified`** — Set to `true` if both `identity_created_at` and
  `earliest_audit_record` are present, are valid RFC 3339 timestamps, and
  `earliest_audit_record` is not earlier than `identity_created_at` (an agent cannot have
  audit records from before its identity was created). Set to `false` otherwise.

Provenance verification is informational. A `provenance_verified: false` result SHOULD be
logged as a warning but MUST NOT automatically deny onboarding. The organization's human
oversight process MAY use provenance information as an input to the approval decision.

### 7.6 Phase 5 — Onboarding Decision

After completing Phases 1–4, the gateway emits an ARSIA message with intent
`"approval_decision"` (ARSIA-Actions.md §3.3) to communicate the onboarding decision to
the external agent.

The decision message MUST conform to the following structure:

**Envelope fields:**

| Field            | Value                                                        |
|------------------|--------------------------------------------------------------|
| `v`              | `"1.0"`                                                      |
| `id`             | Unique UUID v4                                               |
| `ts`             | Current timestamp in RFC 3339 format                         |
| `from`           | Gateway's agent-id                                           |
| `to`             | External agent's agent-id                                    |
| `intent`         | `"approval_decision"`                                        |
| `correlation_id` | The `id` of the initial onboarding request message           |
| `capabilities`   | `["arsiaprotocol.onboarding.evaluate"]`                              |
| `payload`        | See below                                                    |
| `compliance`     | REQUIRED — with the organization's applicable profile        |
| `security`       | REQUIRED — signed with gateway's Ed25519 key                 |

**Payload structure:**

```json
{
  "type": "arsiaprotocol.onboarding/decision",
  "result": {
    "decision": "approved",
    "effective_capabilities": ["arsiaprotocol.code.review", "arsiaprotocol.test.unit"],
    "freely_allowed": ["arsiaprotocol.code.review"],
    "oversight_required": ["arsiaprotocol.test.unit"],
    "conformance_result": {
      "checks": [
        { "test_id": "CHECK-01", "status": "pass", "duration_ms": 42.5 },
        { "test_id": "CHECK-02", "status": "pass", "duration_ms": 18.3 },
        { "test_id": "CHECK-03", "status": "pass", "duration_ms": 156.0 },
        { "test_id": "CHECK-04", "status": "skip", "details": "Audit endpoint not available" },
        { "test_id": "CHECK-05", "status": "skip", "details": "Agent is not high-risk" }
      ],
      "all_passed": true,
      "total_duration_ms": 259.3
    },
    "provenance": {
      "identity_created_at": "2026-03-15T08:00:00.000Z",
      "earliest_audit_record": "2026-03-15T09:00:00.000Z",
      "provenance_verified": true
    },
    "policy_version": "finco-2026-q1",
    "token": "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9...",
    "token_expires_at": "2026-03-25T18:00:00.000Z"
  }
}
```

**Approval.** When `decision` is `"approved"`:

- The `token` field MUST contain a valid JWT access token whose `scope` claim includes
  exactly the `effective_capabilities`.
- The `token_expires_at` field MUST be present and set to the token's expiry time in
  RFC 3339 format.
- The `effective_capabilities`, `freely_allowed`, and `oversight_required` arrays MUST
  be present and non-empty (an approval with zero capabilities is meaningless).

**Denial.** When `decision` is `"denied"`:

- The `denial_reason` field MUST be present. Standard denial reasons are:
  - `"discovery_failed"` — Phase 1, Steps 1 failed.
  - `"identity_verification_failed"` — Phase 1, Steps 2–5 failed.
  - `"unacceptable_risk_classification"` — Phase 1, Step 6 failed.
  - `"conformance_failed"` — Phase 2 failed.
- The `token` field MUST NOT be present.
- The `conformance_result` SHOULD be included to provide feedback to the external agent
  operator about which checks failed.

The gateway MUST record the onboarding decision as an ArsiaAuditRecord
(ARSIA-State.md §7.1) with `event_type` set to `"approval_decision"` and
`payload_type` set to `"arsiaprotocol.onboarding/decision"`.

### 7.7 Phase 6 — Operational Phase

After receiving an approved onboarding decision, the external agent enters the operational
phase. During this phase:

**Token presentation.** The external agent MUST present the issued token as a Bearer token
in the `Authorization` header when sending messages through the infrastructure router, per
ARSIA-Core.md §6.3. The token contains the agent's effective capabilities as the `scope`
claim.

**Token verification.** The infrastructure router MUST verify the token on every incoming
request by calling the gateway's token verification endpoint:

    POST {gateway_base_url}/v1/arsia/verify-token

The request body MUST contain the token to be verified. The response indicates whether
the token is valid and returns the associated scope (effective capabilities). If the
token is invalid, expired, or revoked, the router MUST reject the message with error code
`"unauthorized"` (ARSIA-Core.md §11.2).

**Capability enforcement.** The router MUST verify that the requested capabilities
(from the message's `capabilities` field per ARSIA-Core.md §4.2) are a subset of the
token's scope. If the message requests capabilities not present in the token's scope, the
router MUST reject the message with error code `"forbidden"` (ARSIA-Core.md §11.2).

**Risk-level enforcement.** When a capability in the token's scope carries a
`max_risk_level` constraint (from the CapabilityPolicy, §8.2), the infrastructure router
MUST verify that the invoked action's `risk_level` (from its ActionDescriptor,
ARSIA-Actions.md §2.1) does not exceed that constraint. If the action's `risk_level`
exceeds the capability's `max_risk_level`, the router MUST reject the request with error
code `"forbidden"` (ARSIA-Core.md §11.2) and
`details: { "risk_level_exceeded": true, "max_risk_level": <N>, "action_risk_level": <M> }`.

**Oversight-required capabilities.** When the message requests a capability marked as
`oversight_required` in the onboarding decision, the router SHOULD annotate the message
or signal to the receiving internal agent that oversight is required. The receiving agent
MUST respond with `pending_approval` per ARSIA-Actions.md §3.2 before executing the
action.

**DPoP binding.** External agents SHOULD use DPoP (ARSIA-Identity.md §3.3) when
presenting tokens to the infrastructure router, to prevent token theft and replay. The
router SHOULD verify DPoP proofs when present.

**Token renewal.** When the token approaches expiry, the external agent MAY re-initiate
the onboarding flow to obtain a new token. Implementations MAY provide a lightweight
renewal mechanism that skips Phases 1–4 if the agent's identity and compliance posture
have not changed, but this optimization is NOT REQUIRED and is outside the scope of this
specification.

### 7.8 Example — Regulatory Auditor Onboarding

> **Informative note.** This subsection is entirely informative. It illustrates how
> existing protocol mechanisms combine to onboard a regulatory auditor. No new
> requirements are introduced.

A financial supervisory authority (e.g., BaFin) needs to grant one of its auditor agents
read-only access to the audit trail of a regulated high-risk agent operating within a
MiFID II deployment. The auditor agent requests a single capability:
`arsiaprotocol.audit.read` (ARSIA-Actions.md §1.4).

**Phase 1 — Discovery.** The auditor agent fetches the target agent's discovery endpoint
at `/.well-known/arsia/agent.json` (ARSIA-Core.md §7.1). The response includes the
target's `agent_id`, `protocol_version`, and `capabilities` array. The auditor also
retrieves the target's IdentityRecord at `/.well-known/arsia/identity` to confirm the
`owner_id`, `jurisdiction`, and `ai_system_classification` fields. These fields inform
the trust assessment performed by the auditor's own internal policy engine.

**Phase 2 — Credential presentation.** The auditor agent publishes its own Ed25519
public key at its JWKS endpoint (§2.1) and serves an IdentityRecord that includes the
supervisory authority's legal entity identifier as `owner_id`. The gateway fetches these
endpoints to verify the auditor's cryptographic identity and institutional affiliation.
An institutional attestation — such as a Level 2 CA-signed certificate (§6.2) issued to
the supervisory authority — strengthens the trust signal during policy evaluation.

**Phase 3 — Capability request.** The auditor agent initiates onboarding by sending a
message with `intent: "request"` and declaring `capabilities:
["arsiaprotocol.audit.read"]` in its discovery response. The capability string follows the
grammar defined in ARSIA-Actions.md §1.1: a dot-separated hierarchical identifier within
the reserved `arsiaprotocol.` namespace.

**Phase 4 — Policy evaluation.** The target organization's gateway evaluates the request
against its CapabilityPolicy (§8). A policy that grants audit access to agents with
institutional attestation looks like:

```json
{
  "policy_version": "regulated-entity-2026-q2",
  "token_lifetime_seconds": 300,
  "capabilities": [
    {
      "capability": "arsiaprotocol.audit.read",
      "status": "allowed",
      "conditions": "Supervisory authority agents with Level 2+ certificate"
    }
  ]
}
```

The policy evaluation procedure (§8.3) matches `arsiaprotocol.audit.read` against the
rule, finds `status: "allowed"`, and places it in the `freely_allowed` list. The short
`token_lifetime_seconds` (300 seconds) reflects the sensitive nature of audit data
(ARSIA-Actions.md §1.4, recommended maximum for `arsiaprotocol.audit.read` tokens).

**Phase 5 — Token issuance.** Upon approval, the gateway issues a scoped JWT containing
`scope: ["arsiaprotocol.audit.read"]`, `sub` set to the auditor's agent-id, `exp` set to
300 seconds from issuance, and `iss` set to the gateway's agent-id. The token structure
follows the requirements in §9.1. The gateway records an `approval_decision` audit event
per §9.3.

**Phase 6 — Audit access.** The auditor agent presents the Bearer token to the target
agent's audit endpoint (ARSIA-State.md §7.4):

```
GET /.well-known/arsia/audit?event_type=approval_decision&after=2026-04-01T00:00:00Z&before=2026-04-30T23:59:59Z&limit=100
Authorization: Bearer <scoped-jwt>
```

The target agent verifies the token, confirms that `arsiaprotocol.audit.read` is present
in the token's scope, and returns the matching `ArsiaAuditRecord` entries. The auditor
agent processes these records for its supervisory review without any write access to the
target's state or operational capabilities.

---

## 8. Capability Policy

### 8.1 Policy Structure

The CapabilityPolicy is a JSON document maintained by the receiving organization that
defines which capabilities are available to external agents and under what conditions.
The policy is an input to Phase 3 of the onboarding flow.

```json
{
  "policy_version": "finco-2026-q1",
  "token_lifetime_seconds": 3600,
  "capabilities": [
    {
      "capability": "arsiaprotocol.code.review",
      "status": "allowed",
      "conditions": "Read-only analysis, no code modification"
    },
    {
      "capability": "arsiaprotocol.code.refactor",
      "status": "prohibited",
      "conditions": "Code modification not permitted for external agents"
    },
    {
      "capability": "arsiaprotocol.test.unit",
      "status": "oversight_required",
      "max_risk_level": 3,
      "conditions": "Unit test execution requires human approval"
    }
  ]
}
```

The policy MUST include the following fields:

**`policy_version`** (string, REQUIRED)
:   A version identifier for the policy. This value is included in the onboarding
    decision to establish which version of the policy was applied at the time of
    onboarding. Implementations SHOULD use a semantically meaningful version string
    (e.g., `"finco-2026-q1"`, `"v2.1"`).

**`token_lifetime_seconds`** (integer, REQUIRED)
:   The lifetime in seconds of access tokens issued to approved external agents.
    RECOMMENDED minimum: 900 (15 minutes). RECOMMENDED maximum: 86400 (24 hours).
    Tokens MUST NOT be issued with a lifetime exceeding this value.

**`capabilities`** (array of CapabilityRule, REQUIRED)
:   An array of capability rules defining the organization's policy for each capability.
    See §8.2 for the CapabilityRule structure.

### 8.2 CapabilityRule

Each entry in the `capabilities` array defines the policy for a single capability string.

**`capability`** (string, REQUIRED)
:   The capability string, conforming to the ARSIA capability naming grammar
    (ARSIA-Actions.md §1.1). Wildcard capabilities (e.g., `"arsiaprotocol.test.*"`) are NOT
    permitted in policy rules — each rule MUST specify an exact capability.

**`status`** (string, REQUIRED)
:   One of `"allowed"`, `"oversight_required"`, or `"prohibited"`. The semantics of each
    value are defined in §7.4.

**`max_risk_level`** (integer, OPTIONAL)
:   The maximum risk level (per ARSIA-Actions.md §2.2) at which this capability may be
    invoked. If the action's declared risk level exceeds this value, the invocation MUST
    be treated as `prohibited` regardless of the `status` field. Range: 0–10.

**`conditions`** (string, OPTIONAL)
:   A human-readable description of the conditions under which this capability is
    available. This field is informational and included in audit records. It is NOT
    machine-enforced.

### 8.3 Policy Evaluation Procedure

The gateway MUST evaluate the CapabilityPolicy against the external agent's declared
capabilities using the following algorithm:

```
INPUT:  agent_capabilities   — list of capability strings from the agent's discovery response
INPUT:  policy               — the CapabilityPolicy
OUTPUT: freely_allowed       — list of {capability, max_risk_level?}
OUTPUT: oversight_required   — list of {capability, max_risk_level?}

freely_allowed     = []
oversight_required = []

FOR EACH capability IN agent_capabilities:
    rule = FIND rule IN policy.capabilities WHERE rule.capability == capability
    IF rule IS NOT FOUND:
        CONTINUE                            # deny-by-default
    IF rule.status == "prohibited":
        CONTINUE                            # explicitly denied
    IF rule.status == "allowed":
        APPEND {capability, rule.max_risk_level} TO freely_allowed
    IF rule.status == "oversight_required":
        APPEND {capability, rule.max_risk_level} TO oversight_required

effective_capabilities = freely_allowed + oversight_required
```

If `effective_capabilities` is empty after evaluation, the gateway SHOULD deny onboarding
with `denial_reason = "no_permitted_capabilities"`. An agent with no effective capabilities
cannot perform any useful work within the deployment.

---

## 9. Onboarding Security Considerations

### 9.1 Token Scope Limitation

Tokens issued by the gateway MUST be scoped to exactly the `effective_capabilities`
determined in Phase 3. The token's `scope` claim (as defined in ARSIA-Core.md §6.1) MUST
contain the union of `freely_allowed` and `oversight_required` capabilities and no
additional capabilities. Tokens MUST have an `exp` claim set to the current time plus
`policy.token_lifetime_seconds`. Tokens MUST NOT be issued without an expiry time.

The token's `sub` claim MUST be set to the external agent's agent-id. The token's `iss`
claim MUST be set to the gateway's agent-id. The token's `aud` claim SHOULD be set to the
infrastructure router's agent-id or a wildcard audience representing all internal agents.

### 9.2 Token Theft Mitigation

DPoP (Demonstrating Proof of Possession) per RFC 9449, as specified in ARSIA-Identity.md
§3.3, is RECOMMENDED for all token presentations by external agents. DPoP prevents token
theft and replay attacks by binding the access token to the sender's cryptographic key.

When DPoP is in use:

- The external agent MUST present a DPoP proof JWT alongside the access token.
- The infrastructure router MUST verify the DPoP proof before accepting the request.
- The token MUST contain a `cnf` claim binding it to the agent's Ed25519 key.

Organizations with high-security requirements SHOULD mandate DPoP for all external agents
by rejecting Bearer tokens that are not accompanied by a valid DPoP proof.

### 9.3 Audit Trail Integrity

All onboarding-related events MUST be recorded as ArsiaAuditRecord entries per
ARSIA-State.md §7.1. The following events MUST be audited:

| Event                          | `event_type`        | `payload_type`                      |
|--------------------------------|---------------------|-------------------------------------|
| Onboarding initiated           | `"request"`         | `"arsiaprotocol.onboarding/initiate"`       |
| Identity verification result   | `"response"`        | `"arsiaprotocol.onboarding/identity"`       |
| Conformance test result        | `"response"`        | `"arsiaprotocol.onboarding/conformance"`    |
| Capability scoping result      | `"response"`        | `"arsiaprotocol.onboarding/capabilities"`   |
| Onboarding decision            | `"approval_decision"` | `"arsiaprotocol.onboarding/decision"`     |
| Token revocation               | `"response"`        | `"arsiaprotocol.onboarding/revocation"`     |

All audit records MUST use `payload_hash` (a hash of the payload content), NOT the raw
payload. This satisfies the immutability requirements of ARSIA-State.md §7.2.

Audit records for onboarding decisions MUST be retained for at least the duration
specified by the applicable compliance profile's `retention_days` field. For MiFID II
deployments, this is 1825 days (5 years) per ARSIA-State.md §6.3.

### 9.4 Off-Boarding and Token Revocation

An organization MAY revoke an external agent's access at any time by revoking its token.
Revocation is performed by the gateway and propagated to the infrastructure router through
the token verification endpoint.

When a token is revoked:

1. The gateway MUST record a `"arsiaprotocol.onboarding/revocation"` audit event.
2. The gateway's `/v1/arsia/verify-token` endpoint MUST return an invalid/revoked status
   for the revoked token.
3. The infrastructure router MUST reject subsequent requests presenting the revoked token
   with error code `"unauthorized"`.
4. The audit trail for the agent's operational period MUST be retained per the applicable
   compliance profile's retention requirements, even after revocation.

---

## 10. Onboarding Conformance Tests

The following test cases define conformance requirements for the onboarding flow. Each
test is identified by a unique `test_id` and specifies preconditions, actions, and
expected results. These tests are normative — a conformant implementation MUST pass all
tests.

### IDENTITY-13: Happy path — full onboarding succeeds

| Field             | Value                                                              |
|-------------------|--------------------------------------------------------------------|
| **test_id**       | `IDENTITY-13`                                                      |
| **description**   | Verify that a compliant external agent completes onboarding successfully |
| **preconditions** | External agent serves valid discovery, identity, and JWKS endpoints. Agent correctly implements ARSIA envelope, EdDSA signatures, human oversight signaling, and audit trail. Gateway has a CapabilityPolicy with at least one `allowed` and one `oversight_required` capability matching the agent's declared capabilities. |
| **action**        | Gateway executes the full six-phase onboarding flow against the external agent. |
| **expected**      | Phase 1 passes (identity verified). Phase 2 passes (all 5 checks pass or skip). Phase 3 produces non-empty `effective_capabilities`. Phase 4 records provenance. Phase 5 emits `approval_decision` with `decision: "approved"`, a valid JWT token, `effective_capabilities`, `freely_allowed`, and `oversight_required` lists. An ArsiaAuditRecord with `event_type: "approval_decision"` is created. |

### IDENTITY-14: Rejection — agent lacks required compliance profile

| Field             | Value                                                              |
|-------------------|--------------------------------------------------------------------|
| **test_id**       | `IDENTITY-14`                                                      |
| **description**   | Verify that a high-risk agent without compliance profile is rejected |
| **preconditions** | External agent's IdentityRecord has `ai_system_classification: "high-risk"`. Agent sends response messages without `compliance.profile` field. |
| **action**        | Gateway executes Phase 1 (passes) and Phase 2. CHECK-05 (classification consistency) evaluates the agent's responses. |
| **expected**      | CHECK-05 fails. Phase 2 fails. Gateway emits `approval_decision` with `decision: "denied"` and `denial_reason: "conformance_failed"`. The `conformance_result` includes CHECK-05 with `status: "fail"`. |

### IDENTITY-15: Rejection — identity signature verification fails

| Field             | Value                                                              |
|-------------------|--------------------------------------------------------------------|
| **test_id**       | `IDENTITY-15`                                                      |
| **description**   | Verify that an agent with an invalid identity signature is rejected |
| **preconditions** | External agent serves an IdentityRecord with an `X-ARSIA-Sig` header whose value does not match the SHA-256 hash of the response body when verified against the agent's JWKS public key (e.g., the record was tampered with after signing). |
| **action**        | Gateway executes Phase 1, Step 4 (identity signature verification). |
| **expected**      | Signature verification fails. Gateway denies onboarding with `denial_reason: "identity_verification_failed"`. Phase 2 is not executed. An ArsiaAuditRecord is created with the denial. |

### IDENTITY-16: Rejection — agent executes without waiting for oversight approval

| Field             | Value                                                              |
|-------------------|--------------------------------------------------------------------|
| **test_id**       | `IDENTITY-16`                                                      |
| **description**   | Verify that an agent that bypasses human oversight is rejected      |
| **preconditions** | Gateway's CapabilityPolicy marks capability `arsiaprotocol.test.unit` as `oversight_required`. External agent is configured to respond directly with `intent: "response"` instead of `intent: "pending_approval"` when receiving a request for `arsiaprotocol.test.unit`. |
| **action**        | Gateway executes Phase 2, CHECK-03 (human oversight compliance). Gateway sends a request for `arsiaprotocol.test.unit`. |
| **expected**      | CHECK-03 fails because the agent responded with `intent: "response"` instead of `intent: "pending_approval"`. Phase 2 fails. Gateway emits `approval_decision` with `decision: "denied"` and `denial_reason: "conformance_failed"`. |

### IDENTITY-17: Capability scoping — prohibited capability rejected post-onboarding

| Field             | Value                                                              |
|-------------------|--------------------------------------------------------------------|
| **test_id**       | `IDENTITY-17`                                                      |
| **description**   | Verify that a prohibited capability is rejected by the infra router |
| **preconditions** | External agent has completed onboarding with `effective_capabilities: ["arsiaprotocol.code.review"]`. The CapabilityPolicy marks `arsiaprotocol.code.refactor` as `prohibited`. The agent attempts to send a request with `capabilities: ["arsiaprotocol.code.refactor"]` through the infrastructure router. |
| **action**        | Infrastructure router receives the request and checks the token's scope against the requested capabilities. |
| **expected**      | Router determines that `arsiaprotocol.code.refactor` is not in the token's scope. Router rejects the request with error code `"forbidden"` (ARSIA-Core.md §11.2). |

### IDENTITY-18: Capability scoping — oversight-required capability triggers pending_approval

| Field             | Value                                                              |
|-------------------|--------------------------------------------------------------------|
| **test_id**       | `IDENTITY-18`                                                      |
| **description**   | Verify that an oversight-required capability triggers the oversight flow |
| **preconditions** | External agent has completed onboarding. Capability `arsiaprotocol.test.unit` is in the token's scope and marked as `oversight_required`. Agent sends a request with `capabilities: ["arsiaprotocol.test.unit"]` through the infrastructure router to an internal agent. |
| **action**        | Internal agent receives the request and checks that `arsiaprotocol.test.unit` requires oversight. |
| **expected**      | Internal agent responds with `intent: "pending_approval"` per ARSIA-Actions.md §3.2. The action is NOT executed until an `approval_decision` with `decision: "approved"` is received. |

### IDENTITY-19: Token expiry — expired token rejected by infrastructure router

| Field             | Value                                                              |
|-------------------|--------------------------------------------------------------------|
| **test_id**       | `IDENTITY-19`                                                      |
| **description**   | Verify that an expired token is rejected by the infrastructure router |
| **preconditions** | External agent has completed onboarding and received a token with `token_expires_at` in the past (token has expired). Agent attempts to send a request through the infrastructure router. |
| **action**        | Infrastructure router calls the gateway's `/v1/arsia/verify-token` endpoint with the expired token. |
| **expected**      | Gateway returns an invalid/expired status. Router rejects the request with error code `"unauthorized"` (ARSIA-Core.md §11.2). |

### IDENTITY-20: Off-boarding — revoked token rejected, audit trail retained

| Field             | Value                                                              |
|-------------------|--------------------------------------------------------------------|
| **test_id**       | `IDENTITY-20`                                                      |
| **description**   | Verify that token revocation works and audit trail is preserved     |
| **preconditions** | External agent has completed onboarding and has an active (non-expired) token. The organization revokes the agent's token through the gateway. |
| **action**        | 1. Gateway revokes the token and records an audit event. 2. Agent attempts to send a request through the infrastructure router with the revoked token. 3. Verify that audit records from the agent's operational period are still accessible. |
| **expected**      | 1. Gateway records an ArsiaAuditRecord with `payload_type: "arsiaprotocol.onboarding/revocation"`. 2. Router calls `/v1/arsia/verify-token`, receives revoked status, rejects the request with error code `"unauthorized"`. 3. Audit records from the agent's operational period remain accessible via the audit query endpoint and are retained per the compliance profile's `retention_days`. |

---

## 11. References

### Normative References

- **ARSIA-Core.md** — ARSIA Protocol Core Specification, Draft-01.
  §3 (Agent Identifier Format), §4.1 (intent — request, approval_decision),
  §4.2 (correlation_id, expires_at, capabilities), §5 (Message Security),
  §5.1 (Digital Signatures), §5.2 (Signature Verification), §6 (Authorization),
  §6.4 (Capability Enforcement), §7 (Discovery), §7.1 (Discovery Endpoint),
  §7.2 (Capability Discovery), §7.3 (JWKS Endpoint), §8 (Error Handling),
  §9.2 (Brokered Routing), §11.2 (Standard Error Codes), §12 (Conformance Levels).
- **ARSIA-Actions.md** — ARSIA Actions Primitive, Draft-01.
  §1 (Capability Model), §1.1 (Capability Naming), §2.2 (Risk Level to EU AI Act
  Mapping), §3 (Human Oversight Signaling), §3.2 (The pending_approval Message),
  §3.3 (The approval_decision Message).
- **ARSIA-State.md** — ARSIA State Primitive Specification, Draft-01.
  §6 (Compliance Profiles), §6.3 (MIFID-II), §7 (Audit Trail),
  §7.1 (ArsiaAuditRecord Structure), §7.2 (Immutability Requirements),
  §7.4 (Audit Trail Query Endpoint).
- **RFC 2119** — Key words for use in RFCs to Indicate Requirement Levels.
- **RFC 5280** — Internet X.509 Public Key Infrastructure Certificate and
  Certificate Revocation List (CRL) Profile.
- **RFC 6960** — X.509 Internet Public Key Infrastructure Online Certificate Status
  Protocol — OCSP.
- **RFC 7517** — JSON Web Key (JWK).
- **RFC 7519** — JSON Web Token (JWT).
- **RFC 8174** — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words.
- **RFC 8785** — JSON Canonicalization Scheme (JCS).
- **RFC 9449** — OAuth 2.0 Demonstrating Proof of Possession (DPoP).

### Informative References

- **EU AI Act** — Regulation (EU) 2024/1689, Annex III (high-risk AI system categories),
  Art. 13 (transparency), Art. 14 (human oversight), Art. 16 (provider obligations),
  Art. 26 (deployer obligations).
- **EU Regulation 910/2014 (eIDAS)** — Electronic Identification, Authentication
  and Trust Services. Art. 28 (qualified certificates for electronic seals), Art. 35
  (legal effects of qualified electronic seals).
- **EU Digital Identity Regulation (eIDAS 2.0)** — Proposal for a Regulation amending
  Regulation 910/2014 (anticipated 2026-2027).
- **ETSI EN 319 412-5** — Electronic Signatures and Infrastructures (ESI); Certificate
  Profiles; Part 5: QCStatements.
- **Commission Implementing Decision (EU) 2015/1505** — Technical specifications and
  formats relating to trusted lists.
- **GDPR** — Regulation (EU) 2016/679, Art. 5(1)(f) (integrity and confidentiality),
  Art. 30 (records of processing activities).
- **MiFID II** — Directive 2014/65/EU. Art. 16(5) (Record-keeping requirements for
  investment firms using algorithmic trading systems).
- **DORA** — Regulation (EU) 2022/2554, Digital Operational Resilience Act (incident
  reporting requirements).
- **ISO 3166-1** — Codes for the representation of names of countries (alpha-2 codes).
- **VIES** — VAT Information Exchange System, European Commission.
- **GLEIF** — Global Legal Entity Identifier Foundation.

---

## 12. Multi-Organization Onboarding (BYOA)

An agent already registered with Organization A (for example, a financial services firm)
may also need to operate within Organization B (for example, a regulatory sandbox or a
partner institution). The agent retains its existing Ed25519 keypair throughout this
process — there is no need to generate new key material.

The agent initiates a standard onboarding flow (§7) with Organization B, presenting its
existing public key via its JWKS endpoint. Organization B's gateway independently verifies
the agent's identity record, fetches its JWKS, validates conformance, and evaluates
capabilities against its own CapabilityPolicy (§8). On approval, Organization B issues
its own scoped access token. The agent now holds valid tokens from both organizations,
each independently issued and each bound to the same cryptographic key.

The protocol does not require a one-to-one mapping between keypairs and organizations.
An agent's identity is anchored to its Ed25519 keypair, not to any single organization.
Each organization independently verifies and attests the agent through its own onboarding
evaluation. The two onboarding decisions are entirely independent — approval by
Organization A has no bearing on Organization B's evaluation, and revocation by one
organization does not affect the other's token.

Messages signed by this agent are verifiable by recipients in both organizations, since
all signature verification resolves to the same JWKS endpoint. The agent's effective
capabilities differ per organization, scoped by each organization's CapabilityPolicy.
Audit records for each organization's interactions are recorded independently by the
respective gateways.

---
ARSIA Protocol ([arsiaprotocol.org](https://arsiaprotocol.org)) | by [Arsia Labs](https://arsialabs.ai)
