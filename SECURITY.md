<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# ARSIA Protocol — Security Model

**Status:** Informative summary. See normative spec sections for authoritative requirements.

This document summarizes the security architecture of the ARSIA Protocol for CTOs, security architects, and regulators who need to evaluate the protocol's security properties without reading the full specification suite. Every claim references the normative spec section where the authoritative requirement is defined.

---

## 1. Cryptographic Foundation

ARSIA secures every message through digital signatures that provide authentication, integrity, and non-repudiation (Core §5).

**Signing algorithms.** The primary algorithm is Ed25519 (EdDSA over Curve25519), which all implementations MUST support. ECDSA P-256 (ES256) is recommended for interoperability with existing PKI infrastructure. RSA PKCS#1 (RS256, minimum 2048-bit keys) is permitted only for legacy interoperability (Core §5.1).

**Signature process.** Before signing, the message envelope is canonicalized using the JSON Canonicalization Scheme (RFC 8785) to produce a deterministic byte sequence regardless of field ordering or whitespace. The `security` field is excluded from the signing input to avoid circular dependency — the signature covers every other field in the envelope. The resulting signature is base64url-encoded and placed in the `security.sig` field (Core §5.1).

**Key format.** Agent public keys are published as JWK Sets (RFC 7517) at the well-known endpoint `/.well-known/arsia/jwks.json`. Each key entry includes a key identifier (`kid`) following the format `{agent-id}#{key-index}` (Identity §2.2, §2.3).

**Key lifecycle.** Key rotation follows a defined overlap procedure: the new key is added to the JWKS, both keys remain valid for at least 24 hours (72 hours recommended), and the old key is retired after the overlap period. Maximum recommended key lifetime is 90 days. For immediate revocation, the compromised key is removed from the JWKS without an overlap period (Identity §2.4, §2.5).

**Private key storage.** Private keys MUST NOT be stored in plaintext in production. HSMs or cloud KMS services are recommended; OS-level encrypted key storage is acceptable. Raw environment variables are prohibited in production (Identity §2.1).

**Payload encryption.** For messages requiring confidentiality beyond transport-level TLS — such as messages routed through compliance brokers — ARSIA supports optional JWE payload encryption. The recommended configuration is ECDH-ES key agreement with AES-256-GCM content encryption. Signatures cover the encrypted payload, allowing intermediaries to verify envelope integrity without decrypting content (Core §5.3).

---

## 2. Threat Model

The ARSIA threat model considers six categories of adversary and attack vector (Core §13.1). For each, the protocol defines specific mitigations.

### 2.1 Network Interception

**Threat:** An adversary on the network path intercepts messages in transit to read contents, extract credentials, or correlate message patterns.

**Mitigations:** All HTTP connections require TLS 1.3 or later, providing forward secrecy. WebSocket connections require the `wss://` scheme. HSTS is recommended to prevent TLS stripping. For end-to-end confidentiality through intermediaries, payload encryption (Core §5.3) protects message content independently of the transport layer (Core §13.2.1).

### 2.2 Replay Attacks

**Threat:** An adversary captures a valid signed message and re-transmits it to cause duplicate processing or re-execute transactions.

**Mitigations:** Four independent defenses work in concert. Message expiration (`expires_at`) bounds the replay window. Idempotency keys (Core §10) ensure that even successful replays within the window return cached responses without re-executing actions. Short-lived access tokens limit credential reuse. DPoP proof JWTs (Core §6.3) include unique `jti` claims that prevent proof replay (Core §13.2.2).

### 2.3 Capability Escalation

**Threat:** An adversary with a limited-scope access token attempts to invoke capabilities beyond the token's authorized scope.

**Mitigations:** The receiving agent verifies the access token's `scope` claim independently of the message envelope's `capabilities` field. The token scope — signed by the Authorization Server — is the authoritative source of granted capabilities and cannot be modified without invalidating its signature. The message's own digital signature prevents modification of the `capabilities` field after signing (Core §13.2.3).

### 2.4 Timing Attacks

**Threat:** An adversary exploits clock differences between agents to bypass message expiration, extend token lifetimes, or manipulate audit timestamps.

**Mitigations:** A global clock skew tolerance of ±300 seconds applies to all timestamp validation. Compliance profiles for regulated environments may define stricter tolerances, but none may exceed the 300-second ceiling. All timestamps use absolute UTC values (RFC 3339 with `Z` suffix). NTP synchronization is recommended, with multiple time sources for compliance-sensitive environments (Core §13.2.4).

### 2.5 Compromised Agents

**Threat:** An adversary gains control of an agent's private keys and impersonates the agent.

**Mitigations:** Regular key rotation (90-day recommended maximum lifetime) limits the window of exposure. Short token lifetimes — 1 hour maximum, 5 minutes for high-risk profiles — limit credential reuse. DPoP binding (Core §6.3) ties tokens to the holder's private key, preventing use of stolen tokens by other parties. Per-message signatures mean that compromising an access token alone is insufficient to forge messages — the adversary must also possess the signing key (Core §13.2.5).

### 2.6 Broker Compromise

**Threat:** An adversary gains control of a Compliance Broker and attempts to modify, drop, inject, or exfiltrate relayed messages.

**Mitigations:** ARSIA's signing model is end-to-end: the sender signs, and the final recipient verifies against the sender's public key. Brokers are transparent to signature verification and cannot modify envelopes without causing verification failure. Payload encryption prevents a compromised broker from reading encrypted content. Mandatory broker audit records enable forensic detection of misbehavior. Topology determination (Core §9.4) allows senders to choose which broker to use, reducing single-point-of-failure risk (Core §13.2.6).

### 2.7 Out-of-Scope Threats

The ARSIA threat model does not address: physical server compromise beyond key material, side-channel attacks on cryptographic implementations, social engineering of human operators, denial-of-service at the network layer, or vulnerabilities in the underlying LLM or AI model. These are considered infrastructure or application-layer concerns outside the protocol's scope.

---

## 3. Authorization Model

ARSIA uses OAuth 2.0 with the client credentials grant for agent-to-agent authorization (Core §6).

**Token structure.** Access tokens are JWTs (RFC 7519) with required claims: issuer (`iss`), subject agent (`sub`), audience agent (`aud`), expiration (`exp`), issued-at (`iat`), unique identifier (`jti`), and capability scope (`scope`). The `sub` must match the message's `from` field; the `aud` must match the `to` field (Core §6.1).

**Token lifetimes.** Maximum 1 hour is recommended for general use. Maximum 5 minutes is recommended for high-risk compliance profiles. All tokens are signed by the Authorization Server using EdDSA, ES256, or RS256 (Core §6.1).

**Proof-of-possession.** DPoP (RFC 9449) binds tokens to the holder's private key. When DPoP is used, the token includes a confirmation claim (`cnf`) with the JWK thumbprint of the agent's DPoP key. The agent must present a DPoP proof JWT alongside the access token. The receiving agent verifies that the proof's signing key matches the token's thumbprint, that the HTTP method and URL match, and that the proof's `jti` has not been seen before. DPoP is recommended for high-risk deployments (Core §6.3).

**Capability enforcement.** The receiving agent extracts the `scope` claim from the token, compares it against the capabilities listed in the message, and rejects the message if any required capability is missing. Matching is exact string comparison — no wildcards at the envelope level (Core §6.4).

**Client authentication.** Three methods are supported for the token request: client secret, mutual TLS (RFC 8705), and private key JWT (RFC 7523, recommended) (Core §6.2).

---

## 4. Data Protection

ARSIA addresses data protection across five dimensions.

**Transport encryption.** TLS 1.3 is mandatory for all connections. WebSocket connections require `wss://`. HSTS is recommended (Core §8.1, §8.2).

**Payload encryption.** Optional JWE encryption provides end-to-end confidentiality through intermediaries. Signatures cover the encrypted payload, enabling integrity verification without decryption. Payload hashes in audit records use the ciphertext, so audit trail integrity does not require access to plaintext (Core §5.3).

**Data residency.** The `compliance.data_residency` field declares a geographic zone where all message processing must occur. When set, messages must be routed through a Compliance Broker physically located within the declared zone. Audit logs for the message must also be stored within the zone. For EU data residency, this means all processing — reception, verification, response generation, and storage — occurs within EU/EEA member states, eliminating the need for GDPR Chapter V international transfer mechanisms (Routing §5).

**Audit trail immutability.** Audit records are append-only. No update or delete operations are permitted within the retention period. Implementations must enforce insert-only semantics at the storage level. A recommended cryptographic hash chain provides tamper detection. Audit records store payload hashes rather than raw payloads, which means they are not subject to GDPR Art. 17 erasure rights — the hashes are not personal data under GDPR Recital 26 (State §7.2).

**GDPR data operations.** The State primitive provides protocol-level mechanisms for GDPR compliance: erasure via purge operations (Art. 17), access control via grant and revoke operations, legal basis declaration and enforcement (Art. 6), PII classification, and data elements that map to Art. 30 records of processing activities. When personal data is involved, the protocol rejects operations that lack a declared legal basis (State §5).

**Retention policies.** Each compliance profile defines minimum retention periods — from 90 days (EU AI Act limited-risk) to 1,827 days (MiFID II, DORA). Audit records carry a `retained_until` timestamp computed from the applicable profile. After the retention period, records may be archived but must remain available for regulatory inspection for an additional 12 months (State §7.3).

---

## 5. Human Oversight

ARSIA implements human oversight as a first-class protocol mechanism, addressing EU AI Act Article 14 requirements for high-risk AI systems (Actions §3).

**Pre-execution oversight.** When an agent receives a request for an action marked `human_oversight_required: true`, it must not execute the action. Instead, it responds with a `pending_approval` message describing the proposed action, its risk level, and an approval deadline. A separate agent with the `arsiaprotocol.oversight.approve` capability then issues an `approval_decision` message to approve or deny the action. The executing agent verifies the approver's capability, checks the deadline, and validates the correlation chain before proceeding (Actions §3.2, §3.3, §3.4).

**Post-execution oversight.** Compliance profiles may specify `required_post_execution` or `required_within_24h` oversight modes, where actions execute immediately but are subject to subsequent human review. The oversight mode is declared in the `compliance.human_oversight` field of the message envelope (Core §4.3.6).

**Timeout guarantees.** Every `pending_approval` message carries an `approval_deadline`. If no valid `approval_decision` arrives before the deadline, the action expires automatically — it is never executed. Late-arriving approvals are rejected regardless of their decision value (Actions §3.4).

**Auditability.** Every step in the oversight flow — the original request, the `pending_approval`, the `approval_decision`, and the final response — is a signed ARSIA message logged in the audit trail. The `approver_id` field in audit records provides accountability for oversight decisions (Actions §3.5, State §7.1).

**Regulatory alignment.** This mechanism directly addresses Art. 14(4)(d) of the EU AI Act, which requires that a human can "decide, in any particular situation, not to use the high-risk AI system or to otherwise disregard, override or reverse the output." The protocol-level implementation ensures that oversight is interoperable across agent frameworks and verifiable through audit trail analysis (Actions §3.1).

---

## 6. Conformance and Auditability

ARSIA defines three conformance levels that allow implementations to progressively adopt security and compliance features (Core §12).

**Level 1 — Core.** Message envelope validation, Ed25519 signing and verification, OAuth 2.0 authorization, discovery endpoints, HTTP/2 transport over TLS 1.3, direct routing, idempotency, and error handling. This level provides a secure, interoperable agent communication layer without regulatory compliance features.

**Level 2 — Compliance.** All Core requirements plus compliance field processing, at least one compliance profile, audit trail generation, human oversight signaling, brokered routing for data residency, and capability discovery. This is the minimum level for agents operating under EU regulatory obligations.

**Level 3 — Full.** All Compliance requirements plus all five domain primitives (Identity, Routing, Actions, State, Assets), all compliance profiles, WebSocket transport, payload encryption, ES256 signature support, and 100% conformance test suite passage.

**Traceability.** Six Requirements Traceability Matrices (2,086 rows) in [`docs/rtm/`](rtm/) map every MUST, SHOULD, and MAY in the specifications to the corresponding JSON Schema and test vector.

**Validation.** 613 test vectors (514 valid, 99 invalid, 73 runtime-only) in [`test-vectors/`](../test-vectors/) provide machine-verifiable conformance validation with real Ed25519, ES256, and RS256 cryptographic operations.

---

## 7. Privacy Considerations

ARSIA incorporates six privacy protections into the protocol design (Core §13.3).

Agent identifiers are opaque organizational identifiers that must not contain personally identifiable information. Message identifiers are UUID v4 values generated from cryptographically secure random sources — they encode no sequential information, timestamps, or metadata useful for pattern analysis. Distributed tracing (`trace_id`, `span_id`) is opt-in; agents that do not wish to participate simply omit these fields.

Audit log retention is explicitly governed by the `compliance.retention_days` field, supporting GDPR Art. 5(1)(e) data minimization. The `compliance.pii_involved` flag allows messages to declare that they contain or trigger processing of personal data, enabling receiving agents to apply appropriate protections. The `compliance.legal_basis` field supports GDPR Art. 5(2) accountability by declaring the lawful basis for processing at the message level.

---

## 8. References

| Topic | Spec | Section | Description |
|-------|------|---------|-------------|
| Message security overview | Core | §5 | Signing, verification, and encryption |
| Digital signatures | Core | §5.1 | Ed25519 signing procedure and supported algorithms |
| Signature verification | Core | §5.2 | Verification procedure and caching |
| Payload encryption | Core | §5.3 | JWE encryption for end-to-end confidentiality |
| Authorization | Core | §6 | OAuth 2.0 tokens, DPoP, capability enforcement |
| Transport security | Core | §8.1, §8.2 | TLS 1.3, WebSocket over TLS |
| Idempotency | Core | §10 | Replay protection via idempotency keys |
| Conformance levels | Core | §12 | Core, Compliance, and Full conformance |
| Threat model | Core | §13.1 | Adversaries and attack vectors |
| Mitigations | Core | §13.2 | Protocol defenses for each threat |
| Privacy considerations | Core | §13.3 | PII, data minimization, legal basis |
| Key management | Identity | §2 | Key pairs, JWKS, rotation, revocation |
| Data residency | Routing | §5 | Geographic processing constraints |
| Human oversight | Actions | §3 | Approval workflow for EU AI Act Art. 14 |
| GDPR obligations | State | §5 | Erasure, legal basis, Art. 30 mapping |
| Audit trail | State | §7 | Immutability, retention, query endpoint |

---

ARSIA Protocol ([arsiaprotocol.org](https://arsiaprotocol.org)) | by [Arsia Labs](https://arsialabs.ai)
