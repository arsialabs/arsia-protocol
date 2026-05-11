<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
# ARSIA Protocol — Frequently Asked Questions

## Message Envelope

### Why does ARSIA mandate exactly 3-digit millisecond precision for timestamps?

RFC 3339 allows variable fractional precision, but interoperability requires determinism. If one agent sends microseconds and another truncates to seconds, canonicalization (RFC 8785) produces different byte sequences for the same logical timestamp, causing signature verification failures. Mandatory millisecond precision ensures all implementations produce identical canonical forms. This is a deliberate constraint documented in Core §4.1.3.

### Why is payload.version restricted to MAJOR.MINOR instead of full SemVer?

Payload versioning governs wire compatibility between agents, not software release management. MAJOR indicates breaking changes; MINOR indicates backward-compatible additions. PATCH-level changes (bug fixes) don't affect the wire format — they're internal to the implementation. The MAJOR.MINOR format (Core §4.4.2, Actions §2.4) keeps version negotiation simple: agents compare two numbers, not three. The version field in AgentMetadata (Core §7.1) is free-form and MAY use full SemVer for software version tracking — these are distinct fields with different purposes.

### Why is the security field listed under "Optional Fields" if signatures are required?

The security field is structurally optional in the envelope schema because two of the six intent types — event and error — do not require signatures. For the other four intents (request, response, pending_approval, approval_decision), signatures are behaviourally required by Core §5.2. The schema uses conditional validation (allOf/if/then) to enforce this. An informative note in §4.3.5 clarifies this distinction.

### Why does ARSIA use a closed intent enum instead of extensible message types?

A closed enum (six values: request, response, event, error, pending_approval, approval_decision) ensures every ARSIA implementation can route and process any message without understanding payload-specific semantics. Extension happens through payload.type, not through new intents. This separation means the envelope is stable across protocol versions while payloads evolve independently.

---

## Timestamps & Clock Skew

### Why is the default clock skew tolerance 300 seconds (5 minutes)?

This balances two concerns: (1) agents deployed across cloud regions, edge nodes, and on-premise infrastructure have imperfect clock synchronisation, and (2) the tolerance must be narrow enough to limit replay attack windows. 300 seconds is conservative for distributed systems while still providing meaningful expiration enforcement. Compliance profiles can tighten this (e.g., MIFID-II uses 60 seconds) but never loosen it — 300 seconds is both the default and the ceiling (Core §8.3).

### Why can compliance profiles only tighten clock skew, never loosen it?

The 300-second ceiling is a security bound. Loosening it would widen the replay attack window and weaken expiration enforcement — properties that affect all agents in the ecosystem, not just those under a specific compliance profile. Regulated environments (MiFID II, DORA) need tighter tolerances because financial transaction timing has legal significance. The one-way constraint (tighten only) prevents a profile from accidentally degrading security for the entire deployment.

---

## Security & Cryptography

### Why is Ed25519 the required algorithm and not RSA or ECDSA?

Ed25519 provides 128-bit security with 64-byte signatures and 32-byte public keys — significantly smaller than RSA-2048 (256-byte signatures) or ECDSA P-256 (variable-length DER signatures). For a protocol where every message is signed and signatures are included in the envelope, size matters. Ed25519 also has deterministic signing (no random nonce), which eliminates a class of implementation bugs that have historically affected ECDSA. ES256 and RS256 are supported (SHOULD/MAY respectively) for interoperability with existing JOSE infrastructure, but Ed25519 is the normative baseline.

### Why does ARSIA sign the entire envelope minus security, not just the payload?

Signing only the payload would leave envelope fields (from, to, intent, capabilities, compliance) unprotected. An attacker could modify routing, capabilities, or compliance metadata without invalidating the signature. By signing the canonical form of the complete envelope (with security removed), ARSIA ensures that every field the recipient relies on for processing is integrity-protected.

### Why publish test keypairs? Isn't that a security risk?

Publishing test keypairs is standard practice in cryptographic protocol specifications. RFC 7518 (JWA), the Wycheproof test suite, and the JOSE test suite all publish test key material. Test keypairs enable deterministic, reproducible conformance testing across implementations. They are clearly labelled as test material and MUST NOT be used in production — the same convention followed by every major protocol specification.

---

## Capability Model & Authorization

### Why are capabilities strings and not UUIDs or numeric IDs?

Hierarchical dot-separated strings (e.g., notes.read, eu.mifid.risk.assess) are human-readable, self-documenting, and support namespace delegation without a central registry. An operator reading an audit trail can understand what a capability grants without looking up a UUID mapping. The reverse-domain convention for application capabilities ensures global uniqueness without coordination.

### What is the difference between capability strings and payload.type?

Capabilities use forward domain notation with dots only (e.g., eu.mifid.risk.assess) and represent authorization — what an agent is permitted to do. payload.type uses reverse domain notation with optional slash-separated path segments that may contain hyphens and underscores (e.g., eu.mifid.risk/assess) and identifies the payload schema — what the message contains. The action_id field in ActionDescriptors follows the payload.type format. Both Core §4.4.1 and Actions §1.1 contain informative notes explaining this distinction.

### How does wildcard matching work? Does notes.* match notes.admin.reset?

Yes. Wildcard matching is prefix-based with no depth limit. A token scope entry notes.* satisfies any capability that starts with notes. followed by at least one character. The protocol supports a single wildcard suffix per expression — notes.*.read is invalid. This is documented in Actions §1.2 with examples.

### Why can't wildcards grant arsiaprotocol.state.purge or arsiaprotocol.oversight.approve?

These capabilities are designated as non-delegable (Actions §1.4). Purge permanently and irreversibly destroys data (bypassing retention safeguards), snapshot exposes historical data that may have been logically deleted, and oversight.approve authorises decisions for high-risk operations. A token with arsiaprotocol.* covers all delegable capabilities but MUST NOT satisfy non-delegable ones — they require an exact string match in the token scope. This is enforced at both the Authorization Server (token issuance) and the receiving agent (PEP). See Actions §1.2 condition 3.

### Why doesn't Core §6.4 mention wildcard matching?

Core §6.4 defines capability enforcement at the envelope layer, where matching is exact string comparison. Wildcard expansion operates at the authorization layer and is defined in Actions §1.2. Core §6.4 contains an informative note cross-referencing Actions §1.2. The separation exists because envelope validation and token scope evaluation are logically distinct operations — an agent that only implements Core (without Actions) uses exact matching exclusively.

---

## Compliance Profiles

### Why does GDPR-STANDARD have retention_days: null?

GDPR does not prescribe a specific retention period for audit records. Art. 5(1)(e) establishes the "storage limitation" principle — data should be kept only as long as necessary for the processing purpose — but does not mandate a numeric duration. When retention_days is null, retention is governed by expires_at from the message envelope or by the platform's default policy (90 days recommended). Profiles with explicit regulatory retention requirements (MIFID-II: 1827 days, DORA: 1827 days, PAC-AGRICULTURE: 1096 days) set concrete values.

### Why do retention values use 1827 instead of 1825 for 5-year retention?

Calendar years contain leap years. The naive formula 365 × 5 = 1825 undercounts by 1-2 days depending on the span. For regulatory compliance, the worst case matters: a 5-year span can contain 2 leap years (e.g., 2024-2028), yielding 1827 days. Similarly, 3-year retention uses 1096 (1 leap year possible), and 2-year uses 731. Using the mathematically precise worst-case value eliminates the risk of retention falling short by a day at audit time.

### Why don't compliance profiles have per-profile versioning?

Profiles are protocol artefacts that evolve with the spec version (Draft-01, Draft-01.1, Draft-02). A per-profile version mechanism would introduce negotiation complexity — sender and receiver would need to agree on which version of GDPR-STANDARD they both support. The protocol already has v in the envelope for version compatibility. If a profile needs breaking changes, the pattern is to create a new profile with a distinct name, not to version the existing one.

### All EU profiles operate under GDPR — is GDPR-STANDARD redundant?

No. GDPR applies cumulatively to all EU operations. GDPR-STANDARD is the baseline that applies when no sector-specific regulation adds further requirements. A message with profile: "MIFID-II" is subject to both MiFID II and GDPR simultaneously — MIFID-II adds retention (1827 days), human oversight, and audit requirements on top of the GDPR baseline. GDPR-STANDARD exists for deployments where GDPR is the only applicable regulation.

---

## Identity & Onboarding

### Why does ARSIA use a structured onboarding flow instead of simple API key exchange?

API keys provide authentication but not compliance verification. The onboarding flow (Identity §7) verifies three things that API keys cannot: (1) cryptographic identity — the agent controls the private key it claims, (2) compliance conformance — the agent correctly implements the protocol's requirements, and (3) capability scoping — the agent receives only the permissions defined by the organization's policy. This structured evaluation creates an auditable trust chain that satisfies EU AI Act transparency requirements.

### How does a regulatory auditor get access to audit trails?

Through the standard onboarding flow. Identity §7.8 provides a complete informative example: the auditor agent requests arsiaprotocol.audit.read, the gateway evaluates the request against its CapabilityPolicy, and upon approval issues a short-lived token (300 seconds recommended) scoped to audit read access. The auditor then queries GET /.well-known/arsia/audit with the token. No special mechanism exists — auditor onboarding uses the same primitives as any other external agent.

### Why doesn't ARSIA define a token refresh mechanism?

Token refresh is explicitly deferred (Identity §7): "this optimization is NOT REQUIRED and is outside the scope of this specification." Agents re-initiate the onboarding flow to obtain new tokens. This is analogous to how RFC 9200 handles token lifecycle in constrained environments. The protocol provides the primitives; lightweight renewal is an implementation optimization.

### Can an agent operate in multiple organizations simultaneously?

Yes. Identity §12 ("Multi-Organization Onboarding — BYOA") describes this scenario. The agent retains its existing Ed25519 keypair and independently onboards with each organization. Each organization issues its own scoped token bound to the same cryptographic key. Messages signed by the agent are verifiable by recipients in both organizations since all verification resolves to the same JWKS endpoint. Effective capabilities differ per organization, scoped by each organization's CapabilityPolicy.

### Why must kid follow the {agent-id}#{key-index} pattern?

The verification procedure (Identity §3.1, step 2) parses the kid to extract the agent-id prefix (everything before #) and verifies it matches the message's from field. This binding prevents a compromised key from being used to sign messages on behalf of a different agent. The format is enforced by the JWK schema pattern and is MUST-level across Core §7.3, Core §4.3.5, and Identity §2.2.

---

## Assets & Financial Operations

### Why doesn't ARSIA execute payments?

By design. The Assets spec (§1) establishes a permanent scope boundary between protocol-level concerns (intent, receipt, audit) and provider-level concerns (execution, settlement, account management). Payment execution requires licences under PSD2 Article 11. ARSIA defines the message envelope for value transfer intent and the audit trail format — it is infrastructure, not a payment processor. This separation is not a limitation of Draft-01; it is an architectural decision.

### Why is escrow dispute resolution out of scope?

Arbitration processes vary by jurisdiction, industry, and contractual arrangement. ARSIA provides the signaling infrastructure (dispute message, DISPUTED state transition, freeze of escrowed funds, audit event) but delegates resolution to the arbitration_agent through implementation-defined processes. This is analogous to how SWIFT/ISO 20022 defines dispute signaling (camt.027/camt.029) without prescribing the resolution process.

### Why are audit requirements SHOULD for tokens/entitlements but MUST for currency?

Currency transfers potentially fall under MiFID II, PSD2, and DORA — three EU regulations with explicit record-keeping obligations. Token, entitlement, and service unit transfers are not financial instruments (unless specifically classified as such) and carry no inherent regulatory audit mandate. The SHOULD allows implementations to enable audit for non-currency transfers based on operational needs without mandating it where regulation doesn't require it.

### Why doesn't the dispute message require a specific capability?

Disputes are available to transaction parties (from_agent or to_agent) by right — they are principals of the escrow, not external agents requesting a privileged operation. The arbitration_agent validates party membership (is the sender a party to this escrow?) rather than checking a capability grant. This avoids requiring every transaction party to hold a separate dispute capability for every escrow they participate in.

---

## State Management

### Why does the arsiaprotocol. key prefix restriction only apply to agent-initiated writes?

State §2.2 says implementations MUST reject SET operations from agents with the arsiaprotocol. prefix. Internal implementation storage (grant management at arsiaprotocol.grants/{grant-id}, audit records) uses this prefix for system-managed keys. The distinction is between protocol-level writes (agent sends a SET request) and implementation-level storage (the system manages internal state). An informative note in §2.2 clarifies this.

### Why are purge and snapshot elevated capabilities that can't be wildcarded?

Purge permanently and irreversibly destroys data, bypassing all retention safeguards. Snapshot provides access to historical data that may have been logically deleted. Both operations have regulatory consequences if misused — premature purge violates retention obligations (MiFID II 5-year requirement), and unauthorized snapshot access exposes data that GDPR deletion was supposed to erase. These capabilities require explicit, auditable authorization — not blanket wildcard grants.

### How does ARSIA handle GDPR Art. 9 special categories (health data, biometrics)?

The pii_classification field supports "sensitive" (State §2.1.10), which inherits all obligations of "personal" plus additional encryption requirements. Compliance validation Rule 8 (Core §4.3.8) requires pii_special_categories and a valid Art. 9(2) legal basis when sensitive data is involved. The protocol enforces that a legal ground exists but does not validate specific category-to-ground mappings, which vary by EU Member State derogation.

### Why can PURGE override retention? Doesn't that violate MiFID II?

GDPR Article 17 (right to erasure) and MiFID II Article 16(7) (5-year retention) can genuinely conflict. The ARSIA Protocol does not resolve this conflict — it provides the mechanisms for both (retention enforcement via retention_days, erasure via PURGE) and leaves the legal determination to the data controller. State §5.3 documents this tension. The PURGE audit event records that erasure occurred (without the purged value) to maintain accountability even when data is destroyed.

---

## Routing & Brokers

### How does a sender discover the broker registry?

Broker registry discovery is a deployment concern, analogous to SMTP MTA discovery or OAuth authorization server discovery. The protocol intentionally uses MAY language for hosting options (Routing §7.2) because different deployments use different mechanisms — well-known URI, static configuration, DNS-based service discovery. Implementations without a pre-configured registry SHOULD use /.well-known/arsia/brokers as the default discovery endpoint.

### Why must messages with data_residency: EU go through a broker even when both agents are in the EU?

Setting compliance.data_residency constitutes a regulatory requirement that mandates broker involvement. The broker ensures data residency compliance by routing through infrastructure that physically resides within the declared zone. Even if both agents are in the EU, the protocol cannot verify this at the wire level — the broker provides the attestation. Routing §1.2.1's qualifying clause ("and no regulatory requirement mandates broker involvement") covers exactly this case.

### Why does X-Request-Priority header take precedence over context.priority?

Transport-layer headers are visible to intermediaries (load balancers, brokers) that may not parse the envelope body. Priority at the transport layer enables routing decisions without deep inspection. The envelope field serves as a fallback for transports that don't support custom headers (e.g., WebSocket). Routing §6.3 defines the precedence; Core §8.1 contains an informative cross-reference.

---

## Conformance & Testing

### Why does Full Conformance require OPTIONAL features?

This follows the standard conformance tier pattern used in protocol specifications. OPTIONAL at the protocol level means an implementation may choose not to support the feature. REQUIRED at the Full conformance tier means an implementation that claims Full conformance must support it. An implementation can be conformant at the Core tier without these features. The tiers provide a progression path: Core → Compliance → Full.

### Why does ARSIA publish 613 test vectors?

Comprehensive test vectors enable deterministic conformance testing across languages and platforms. Each vector tests a specific constraint — valid vectors exercise real schema and protocol rules, invalid vectors verify that implementations correctly reject malformed input. The vectors are the executable specification: if an implementation passes all vectors, it handles the same edge cases as every other conformant implementation. 70+ vectors are marked skip_schema for constraints that require runtime enforcement (cross-object validation, temporal logic, token context).

---

## Architecture & Scope

### Why doesn't ARSIA define a data portability format for GDPR Art. 20?

The StateEntry JSON structure already satisfies Art. 20's requirement for "a structured, commonly used, and machine-readable format." JSON is universally parseable, the schema is published, and the data is self-describing. Defining a separate export format (CSV, XML) would add specification complexity without regulatory benefit. Operators MAY transform StateEntry JSON to other formats as required by their data subject access request procedures. An informative note in State §5.5 confirms this rationale.

### Why doesn't ARSIA define exactly-once delivery?

Exactly-once delivery requires distributed transactions, two-phase commit, or distributed consensus — mechanisms that introduce latency, complexity, and failure modes incompatible with the protocol's design goals. ARSIA provides at-most-once (default) and at-least-once (via idempotency keys) delivery guarantees. Application-layer deduplication on top of at-least-once provides effective exactly-once semantics for most use cases, without protocol-level distributed consensus.

### Why are some conformance tests runtime-only (skip_schema)?

JSON Schema cannot express constraints that span multiple messages, require temporal reasoning, depend on token context, or need cryptographic verification. Examples: "the from field must match the token's sub claim" (requires token parsing), "optimistic concurrency version must match" (requires state), "clock skew tolerance must be applied" (requires current time). These constraints are real and normative — they are tested by the SDK's conformance suite at runtime, not by the schema validator.

---

ARSIA Protocol ([arsiaprotocol.org](https://arsiaprotocol.org)) | by Arsia Labs ([arsialabs.ai](https://arsialabs.ai))
