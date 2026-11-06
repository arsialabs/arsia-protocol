<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Draft-02 Skip Classification

Every `skip_schema` vector in `test-vectors/arsia-test-vectors.json`, individually
classified per the Draft-02 plan. A skip is a vector whose requirement is real but
not expressible in JSON Schema; the classification records WHY, what verification
method covers it instead, and the residual risk of leaving it without full
automation. A skip exempts only the runtime expectation: every vector below is still
validated structurally against its schema, and `scripts/validate_vectors.py` reports
0 failures for all of them.

**Coverage.** The last column states, in a closed vocabulary, what this repository
actually executes for the vector (evidence at the vector cycle, VC):
- `executed: Rn` — harness rule Rn of `scripts/runtime_harness.py` loads this vector
  (its `test_metadata` scenario, or a lookup by ID) and checks its stated expectation;
- `equivalent: Rn "<check>"` — the named harness check applies the same rule to the
  vector's decisive inputs, without reading the vector;
- `partial: Rn "<check>" — <not exercised>` — the named check exercises the rule
  with other inputs, or only part of the expectation;
- `executed: --check-crypto` — a signature negative (`crypto.expect_signature:
  "invalid"`) whose decisive expectation is the signature failure, asserted by
  `scripts/validate_vectors.py --check-crypto`; it covers no other runtime
  expectation of the vector;
- `none — <method>` — no automation here; the method is a conformance test against
  an implementation, or `integration` (two communicating implementations, through
  the conformance tests CORE-*/ACTIONS-*/IDENTITY-*/STATE-*/ROUTING-*/ASSETS-* of the
  specs, executed against a real deployment).

`check_consistency.py` verifies the column: one row per runtime vector, every
`executed` row backed by a scenario its rule consumes, every quoted check present in
the harness. **Automation candidate** is `yes` where automation is still to be
written and `—` where the vector is executed or has an equivalent check.

**Category totals:** amount-scale: 2, capability: 5, compliance-resolution: 32, cross-object: 12, crypto-behaviour: 15, executor-oversight: 63, numeric: 2, other: 16, retention-floor: 6, temporal: 16, token: 17, transport: 11, x509: 7 — total 204.

| ID | Anchor | Reason (abridged) | Category | Requirement class | Automation candidate | Coverage |
|---|---|---|---|---|---|---|
| INV-07 | Identity §4.2, Core §4.3.8 Rule 3 | Runtime constraint — high-risk requirement set over the composed oversight set (Core §4.3.8 Rule 3, §4.3.10; I | compliance-resolution | behavioural-runtime | — | executed: R10 |
| INV-08 | Core §4.3.8 Rule 4 | Runtime constraint — calendar retention-floor comparison (Core §4.3.8 Rule 4); Draft-02 moved floors from sche | retention-floor | behavioural-runtime | yes | partial: R2 "R2 ITV-563 MIFID P365D rejected" — same MIFID-II floor; the declared P90D is not exercised |
| INV-09 | — | Runtime constraint — currency precision enforced programmatically | other | behavioural-runtime | yes | none — conformance test against an implementation |
| INV-11 | — | Runtime constraint — kid↔from cryptographic binding | other | behavioural-runtime | yes | none — conformance test against an implementation |
| INV-12 | — | Runtime semantic constraint — reversal requires original transfer status completed | other | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-408 | — | Runtime constraint — clock skew comparison not enforceable by JSON Schema | temporal | behavioural-runtime | — | executed: R16 |
| ITV-409 | — | Runtime constraint — token sub comparison not enforceable by JSON Schema | token | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-410 | — | Runtime constraint — token aud comparison not enforceable by JSON Schema | token | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-411 | — | Runtime constraint — timestamp expiration comparison not enforceable by JSON Schema | temporal | behavioural-runtime | — | executed: R16 |
| ITV-412 | — | Runtime constraint — token scope verification not enforceable by JSON Schema | token | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-413 | — | Runtime constraint — recipient version comparison not enforceable by JSON Schema | other | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-414 | — | Runtime constraint — cross-field timestamp comparison not enforceable by JSON Schema | temporal | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-416 | — | Runtime constraint — strict-mode profile name validation not enforceable by JSON Schema | compliance-resolution | behavioural-runtime | yes | none — conformance test against an implementation; the reference resolver implements strict-mode `unknown_profile`, but no check exercises it |
| ITV-417 | Core §4.3.8 Rule 4 | Runtime constraint — calendar retention-floor comparison (Core §4.3.8 Rule 4); Draft-02 moved floors from sche | retention-floor | behavioural-runtime | — | equivalent: R2 "R2 ITV-563 MIFID P365D rejected" |
| ITV-418 | — | Runtime constraint — cross-reference to IdentityRecord classification not enforceable by JSON Schema | compliance-resolution | behavioural-runtime | yes | none — conformance test against an implementation; the reference resolver implements `classification_escalation`, but no check exercises it |
| ITV-421 | Core §4.3.8 Rule 3, A-09 | Runtime constraint — Rule 3 checks the EFFECTIVE human_oversight (per-message OR profile default); the schema  | compliance-resolution | behavioural-runtime | yes | partial: R10 "R10 high-risk + MIFID-II, no mode declared: default counts (A-23)" — the EU-AI-ACT-HIGH-RISK default is not exercised |
| ITV-422 | — | Runtime constraint — payload type recognition is implementation-specific, not schema-enforceable | other | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-424 | — | Runtime constraint — message size enforcement not expressible in JSON Schema | other | behavioural-runtime | yes | none — conformance test against an implementation; the vector does not materialize a message above the limit |
| ITV-425 | — | Runtime constraint — RSA key size validation not enforceable by JSON Schema (JWK schema does not define RSA ke | other | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-426 | — | Runtime constraint — signature byte length validation not enforceable by JSON Schema (sig is type:string) | crypto-behaviour | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-427 | — | Runtime constraint — JWE header vs security field algorithm comparison not enforceable by JSON Schema | transport | integration | yes | none — integration (two communicating implementations) |
| ITV-429 | — | Runtime constraint — JWE decryption success not verifiable by JSON Schema | other | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-431 | — | Runtime constraint — token sub vs. message from cross-check requires access token context unavailable to JSON  | token | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-432 | — | Runtime constraint — token aud vs. message to cross-check requires access token context unavailable to JSON Sc | token | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-433 | — | Runtime constraint — token scope vs. message capabilities cross-check requires access token context unavailabl | token | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-434 | — | Runtime constraint — token expiration requires time comparison unavailable to JSON Schema | temporal | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-435 | — | Runtime constraint — token issued-at time comparison requires clock unavailable to JSON Schema | temporal | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-436 | — | Runtime constraint — enforcement procedure step 3 requires token context unavailable to JSON Schema | token | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-437 | — | Runtime constraint — enforcement procedure step 3 requires token context and receiver identity unavailable to  | token | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-440 | — | Runtime constraint — timestamp freshness requires clock comparison unavailable to JSON Schema | temporal | behavioural-runtime | — | executed: R16 |
| ITV-442 | — | Runtime constraint — Content-Type header v parameter vs. envelope v field comparison is HTTP-level, not messag | transport | integration | yes | none — integration (two communicating implementations) |
| ITV-445 | §3.1 step 3 | Runtime constraint — kid-prefix-to-from cross-field comparison not enforceable by JSON Schema | cross-object | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-446 | — | Runtime constraint — cross-object comparison between message compliance and IdentityRecord not enforceable by  | cross-object | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-448 | ±300s clock skew per Core §8.3 | Runtime constraint — iat temporal validation (±300s clock skew per Core §8.3) not enforceable by JSON Schema | temporal | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-449 | — | Runtime constraint — nbf temporal validation not enforceable by JSON Schema; the claims schema accepts the additional nbf claim | temporal | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-450 | — | Runtime constraint — nbf temporal validation not enforceable by JSON Schema; schema does not define nbf field | temporal | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-457 | — | Runtime constraint — X.509 certificate content validation not enforceable by JSON Schema | x509 | integration | yes | none — integration (two communicating implementations) |
| ITV-458 | — | Runtime constraint — X.509 certificate content validation not enforceable by JSON Schema | x509 | integration | yes | none — integration (two communicating implementations) |
| ITV-459 | — | Runtime constraint — X.509 certificate content validation not enforceable by JSON Schema | x509 | integration | yes | none — integration (two communicating implementations) |
| ITV-460 | — | Runtime constraint — X.509 certificate content validation not enforceable by JSON Schema | x509 | integration | yes | none — integration (two communicating implementations) |
| ITV-461 | — | Runtime constraint — X.509 certificate content validation not enforceable by JSON Schema | x509 | integration | yes | none — integration (two communicating implementations) |
| ITV-462 | — | Runtime constraint — X.509 certificate content validation not enforceable by JSON Schema | x509 | integration | yes | none — integration (two communicating implementations) |
| ITV-463 | — | Runtime constraint — X.509 certificate content validation not enforceable by JSON Schema | x509 | integration | yes | none — integration (two communicating implementations) |
| ITV-466 | — | Runtime constraint — trust level acceptance policy not enforceable by JSON Schema | other | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-467 | — | Runtime constraint — trust level acceptance for all levels not enforceable by JSON Schema | other | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-475 | — | Runtime constraint — Ed25519 signature verification over identity record not enforceable by JSON Schema | crypto-behaviour | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-476 | — | Runtime constraint — kid-prefix-to-agent_id cross-artifact comparison not enforceable by JSON Schema | other | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-477 | — | Runtime constraint — cross-message from-field to agent_id comparison not enforceable by JSON Schema | other | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-479 | — | Runtime constraint — cross-message correlation_id matching not enforceable by JSON Schema | capability | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-487 | — | Runtime constraint — verify-token endpoint response behavior not enforceable by JSON Schema | token | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-526 | — | Runtime constraint — cross-object audit-record-to-message comparison: plaintext_hash presence depends on secur | token | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-536 | — | Runtime inheritance — schema cannot validate that entry.data_residency was inherited from compliance.data_resi | compliance-resolution | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-537 | — | Runtime precedence — schema cannot validate field precedence between envelope and args | other | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-538 | — | Runtime inheritance — schema cannot validate retention field propagation | retention-floor | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-539 | — | Runtime precedence — payload.args.retention applies over compliance.retention and is then resolved against the | other | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-540 | — | Runtime validation — schema cannot validate cross-field between compliance.legal_basis and pii_classification | cross-object | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-541 | — | Runtime profile loading — schema cannot validate profile default resolution | compliance-resolution | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-543 | — | Transport-specific runtime behaviour — WebSocket idempotency uses envelope field only, not HTTP header | transport | integration | yes | none — integration (two communicating implementations) |
| ITV-544 | — | Runtime duplicate detection — requires multi-message context and transport state | transport | integration | yes | none — integration (two communicating implementations) |
| ITV-545 | — | Runtime clock skew validation — schema cannot compare ts against current time or profile tolerance | temporal | behavioural-runtime | — | executed: R16 |
| ITV-547 | — | Runtime clock skew validation — schema cannot compare ts against current time or profile tolerance | temporal | behavioural-runtime | — | executed: R16 |
| INV-18 | — | Runtime signature verification — schema cannot validate cryptographic correctness of ECDSA signatures | crypto-behaviour | behavioural-runtime | — | executed: --check-crypto |
| INV-19 | — | Runtime signature verification — schema cannot validate cryptographic correctness of RSA signatures | crypto-behaviour | behavioural-runtime | — | executed: --check-crypto |
| ITV-553 | — | Runtime constraint — audit_required override is runtime behaviour not enforceable by JSON Schema | token | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-554 | — | Runtime constraint — audit_required override is runtime behaviour not enforceable by JSON Schema | token | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-555 | — | Runtime constraint — cross-object validation between payload.args.pii_classification and compliance.legal_basi | cross-object | behavioural-runtime | yes | none — conformance test against an implementation |
| INV-20 | — | Runtime constraint — cross-object validation between payload.args.pii_classification and compliance.legal_basi | cross-object | behavioural-runtime | yes | none — conformance test against an implementation |
| INV-22 | — | Runtime constraint — schema cannot enforce mutual exclusion (MUST NOT be present when not sensitive) | other | behavioural-runtime | yes | none — conformance test against an implementation |
| INV-23 | — | Runtime constraint — wildcard matching exclusion for non-delegable capabilities is not schema-enforceable | capability | behavioural-runtime | yes | partial: R3 "R3 reserved root wildcard satisfies nothing" — arsiaprotocol.state.purge is not exercised |
| INV-24 | — | Runtime constraint — wildcard matching exclusion for non-delegable capabilities is not schema-enforceable | capability | behavioural-runtime | yes | partial: R3 "R3 reserved root wildcard satisfies nothing" — arsiaprotocol.state.snapshot is not exercised |
| INV-25 | — | Runtime constraint — wildcard matching exclusion for non-delegable capabilities is not schema-enforceable | capability | behavioural-runtime | — | equivalent: R3 "R3 reserved via wildcard (ITV-567)" |
| ITV-563 | Core §4.3.8 Rule 4 | Runtime constraint — calendar retention-floor comparison (Core §4.3.8 Rule 4); schema validates format only | retention-floor | behavioural-runtime | — | equivalent: R2 "R2 ITV-563 MIFID P365D rejected" |
| ITV-564 | Core §4.3.6.4.1 | Runtime constraint — calendar retention-floor comparison with month arithmetic (Core §4.3.6.4.1) | retention-floor | behavioural-runtime | — | equivalent: R2 "R2 ITV-564 P180D < P6M rejected" |
| ITV-565 | Core §4.3.7 | Runtime constraint — retention resolution from profile minimum (Core §4.3.7) | retention-floor | behavioural-runtime | — | equivalent: R2 "R2 ITV-565 absent -> profile minimum" |
| ITV-566 | Actions §1.2 | Runtime constraint — token-scope wildcard matching (Actions §1.2); token not part of the envelope | token | behavioural-runtime | — | equivalent: R3 "R3 wildcard valid (ITV-566)" |
| ITV-567 | Actions §1.2 condition 3 | Runtime constraint — reserved-namespace exact-match rule (Actions §1.2 condition 3) | other | behavioural-runtime | — | equivalent: R3 "R3 reserved via wildcard (ITV-567)" |
| ITV-568 | Actions §1.1 Rule 5 / §1.4 | Runtime constraint — reserved-registry membership (Actions §1.1 Rule 5 / §1.4) | capability | behavioural-runtime | — | equivalent: R4 "R4 unknown reserved rejected (ITV-568)" |
| ITV-570 | Routing §7.4.1 step 1 | Runtime constraint — relay attestation header presence and decoding at the recipient (Routing §7.4.1 steps 1-2) | transport | behavioural-runtime | — | executed: R22 |
| ITV-571 | Core §6.4, Routing §1.2.2 | Runtime constraint — token/transport behaviour outside the envelope (Core §6.4, Routing §1.2.2) | token | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-572 | Routing §1.2.2, Core §6.4/§6.5 | Runtime constraint — token audience/scope checks (Routing §1.2.2, Core §6.4/§6.5) | token | behavioural-runtime | yes | none — conformance test against an implementation |
| ITV-575 | Assets §3.1.1 | Runtime constraint — per-currency fixed scale requires the ISO 4217 catalog (Assets §3.1.1) | amount-scale | behavioural-runtime | — | equivalent: R5 "R5 EUR 1500.0 rejected (ITV-575)" |
| ITV-576 | Assets §3.1.1 | Runtime constraint — per-currency fixed scale requires the ISO 4217 catalog (Assets §3.1.1) | amount-scale | behavioural-runtime | — | equivalent: R5 "R5 JPY 1500.00 rejected (ITV-576)" |
| ITV-577 | State §2.1.2 | Runtime constraint — I-JSON number-range rule (State §2.1.2); JSON Schema cannot distinguish 2^53+1 reliably | numeric | behavioural-runtime | — | equivalent: R8 "R8 2^53+1 rejected (ITV-577)" |
| ITV-578 | State §2.1.2 | Runtime constraint — value-semantics round-trip behaviour (State §2.1.2) | numeric | behavioural-runtime | yes | none — conformance test against an implementation |
| INV-37 | Core §5.2 | Runtime constraint — signature verification behaviour (Core §5.2); tamper cannot be expressed as a schema outc | crypto-behaviour | behavioural-runtime | — | executed: --check-crypto |
| INV-38 | Core §5.2 | Runtime constraint — signature verification behaviour (Core §5.2) | crypto-behaviour | behavioural-runtime | — | executed: --check-crypto |
| INV-39 | Core §5.2 Step 3 | Runtime constraint — signing-profile downgrade prohibition (Core §5.2 Step 3) | crypto-behaviour | behavioural-runtime | — | executed: --check-crypto |
| INV-111 | Core §5.2 Step 5 | Runtime signature verification — algorithm coherence (Core §5.2 Step 5): the declared alg is incompatible with | crypto-behaviour | behavioural-runtime | — | executed: --check-crypto |
| INV-112 | Core §5.2 Step 5 | Runtime signature verification — algorithm coherence (Core §5.2 Step 5): the declared alg is incompatible with | crypto-behaviour | behavioural-runtime | — | executed: --check-crypto |
| INV-113 | Core §4.3.9 | Runtime constraint — token binding: SHA-256 of the presented token against authorization.token_hash (Core §4.3 | token | behavioural-runtime | — | executed: R21 |
| INV-114 | Core §4.3.9 | Runtime constraint — token binding: SHA-256 of the presented token against authorization.token_hash (Core §4.3 | token | behavioural-runtime | — | executed: R21 |
| INV-115 | Routing §7.4.1 | Runtime constraint — recipient verification of the relay attestation (Routing §7.4.1) | cross-object | behavioural-runtime | — | executed: R22 |
| INV-116 | Routing §7.4.1 | Runtime constraint — recipient verification of the relay attestation (Routing §7.4.1) | cross-object | behavioural-runtime | — | executed: R22 |
| INV-117 | Routing §7.4.1 | Runtime constraint — recipient verification of the relay attestation (Routing §7.4.1) | cross-object | behavioural-runtime | — | executed: R22 |
| INV-118 | Routing §7.4.1 | Runtime constraint — recipient verification of the relay attestation (Routing §7.4.1) | cross-object | behavioural-runtime | — | executed: R22 |
| INV-119 | Routing §7.4.1 | Runtime constraint — recipient verification of the relay attestation (Routing §7.4.1) | temporal | behavioural-runtime | — | executed: R22 |
| INV-120 | Routing §7.4.1 | Runtime constraint — recipient verification of the relay attestation (Routing §7.4.1) | temporal | behavioural-runtime | — | executed: R22 |
| INV-121 | Routing §7.4.1 | Runtime constraint — recipient verification of the relay attestation (Routing §7.4.1) | cross-object | behavioural-runtime | — | executed: R22 |
| INV-122 | Routing §7.4.1 | Runtime constraint — recipient verification of the relay attestation (Routing §7.4.1) | cross-object | behavioural-runtime | — | executed: R22 |
| INV-123 | Routing §7.4.1 | Runtime constraint — recipient verification of the relay attestation (Routing §7.4.1) | cross-object | behavioural-runtime | — | executed: R22 |
| INV-124 | Routing §7.4.1 | Runtime constraint — recipient verification of the relay attestation (Routing §7.4.1) | crypto-behaviour | behavioural-runtime | — | executed: R22 |
| INV-125 | Routing §7.4.1 | Runtime constraint — recipient verification of the relay attestation (Routing §7.4.1) | crypto-behaviour | behavioural-runtime | — | executed: R22 |
| ITV-579 | Core §4.3.7/§4.3.8 Rule 3 | Runtime constraint — effective-oversight resolution across profile defaults (Core §4.3.7/§4.3.8 Rule 3) | compliance-resolution | behavioural-runtime | yes | partial: R10 "R10 A-32 absent profile: rejected high_risk_missing_oversight" — classification declared in the message is not exercised |
| ITV-603 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-604 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-605 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-606 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-607 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-608 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-609 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-610 | Identity §7.7 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-611 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-612 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-613 | Identity §7.7 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-614 | Identity §7.7 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-615 | Identity §7.7 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-616 | Identity §7.7 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-617 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-618 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-619 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-620 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-621 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-622 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-623 | Identity §7.2 Step 7, CHECK-05 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-624 | Identity §7.2 Step 7, CHECK-05 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-625 | Identity §7.2 Step 7, CHECK-05 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-626 | Identity §7.7 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-627 | Identity §7.7 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | — | executed: R10 |
| ITV-640 | Actions §3.2, §3.7; Core §4.3.10.2 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-641 | Actions §3.2, §3.7; Core §4.3.10.2 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-642 | Actions §3.2, §3.7; Core §4.3.10.2 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-643 | Actions §3.2, §3.7; Core §4.3.10.2 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-644 | Actions §3.2, §3.7; Core §4.3.10.2 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-645 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-646 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-647 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-648 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-649 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-650 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-651 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-652 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-653 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-654 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-655 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-656 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-657 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-658 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-659 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-660 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-661 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-662 | Actions §3.4, §3.6 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-663 | Actions §3.4, §3.6 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-664 | Actions §3.4, §3.6 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-665 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-666 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-667 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-668 | Identity §7.7, §9.1 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-669 | Identity §7.7, §9.1 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-670 | Identity §7.3 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-671 | Identity §7.3 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-672 | Assets §5.2 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-673 | Assets §5.2 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-674 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-694 | Actions §3.4; Core §5.2 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-695 | Actions §3.4 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-696 | Actions §3.4, §3.6 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-705 | Actions §3.4 Path 3 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-706 | Actions §3.4 Path 3 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-126 | Actions §3.4 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-127 | Actions §3.4 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-128 | Actions §3.4 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-129 | Actions §3.4 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-130 | Actions §3.4 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-131 | Actions §3.4 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-132 | Actions §3.4 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-133 | Actions §3.4 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-134 | Actions §3.4 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-135 | Actions §3.4 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-136 | Actions §3.4 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-137 | Actions §3.4 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-138 | Actions §3.4 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-139 | Actions §3.4 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-140 | Actions §3.4 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-148 | Identity §2.5 | Runtime constraint — key-revocation event authentication and cache invalidation (Identity §2.5, Core §5.2); in | crypto-behaviour | behavioural-runtime | — | executed: R13 |
| INV-149 | Identity §2.5 | Runtime constraint — key-revocation event authentication and cache invalidation (Identity §2.5, Core §5.2); in | crypto-behaviour | behavioural-runtime | — | executed: R13 |
| INV-150 | Identity §2.5 | Runtime constraint — key-revocation event authentication and cache invalidation (Identity §2.5, Core §5.2); in | crypto-behaviour | behavioural-runtime | — | executed: R13 |
| INV-151 | Identity §2.5 | Runtime constraint — key-revocation event authentication and cache invalidation (Identity §2.5, Core §5.2); in | crypto-behaviour | behavioural-runtime | — | executed: R13 |
| INV-152 | Actions §3.4 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-153 | Actions §3.4 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-154 | Actions §3.4; Core §5.2 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-707 | Actions §3.4 Path 3 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| ITV-708 | Actions §3.9.3; State §7.1 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-155 | Actions §3.4; Core §5.2 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-156 | Actions §3.4; Core §6.1 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-157 | Actions §3.4; Core §6.1 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | — | executed: R15 |
| INV-171 | Core §8.3 | Runtime clock skew validation — schema cannot compare ts against current time or profile tolerance | temporal | behavioural-runtime | — | executed: R16 |
| ITV-498 | Core §4.2.2; Routing §4.1.9 | Runtime expiry validation — schema cannot compare expires_at against the recipient's clock (Core §4.2.2) | temporal | behavioural-runtime | — | executed: R16 |
| ITV-518 | Core §4.2.2; Routing §4.1.9 | Runtime expiry validation — schema cannot compare expires_at against the recipient's clock (Core §4.2.2) | temporal | behavioural-runtime | — | executed: R16 |
| INV-172 | Routing §7.4.1 step 2 | Runtime constraint — relay attestation header presence and decoding at the recipient (Routing §7.4.1 steps 1-2) | transport | behavioural-runtime | — | executed: R22 |
| INV-173 | Routing §7.4.1 step 2 | Runtime constraint — relay attestation header presence and decoding at the recipient (Routing §7.4.1 steps 1-2) | transport | behavioural-runtime | — | executed: R22 |
| INV-174 | Routing §7.4.1 step 2 | Runtime constraint — relay attestation header presence and decoding at the recipient (Routing §7.4.1 steps 1-2) | transport | behavioural-runtime | — | executed: R22 |
| INV-175 | Routing §7.4.1 step 2 | Runtime constraint — relay attestation header presence and decoding at the recipient (Routing §7.4.1 steps 1-2) | transport | behavioural-runtime | — | executed: R22 |
| INV-176 | Routing §7.4.1 step 2 | Runtime constraint — relay attestation header presence and decoding at the recipient (Routing §7.4.1 steps 1-2) | transport | behavioural-runtime | — | executed: R22 |
| INV-177 | Routing §7.4.1 step 2 | Runtime constraint — relay attestation header presence and decoding at the recipient (Routing §7.4.1 steps 1-2) | transport | behavioural-runtime | — | executed: R22 |

## Residual risk statement

- Vectors whose coverage is `executed` or `equivalent` have executable reference
  logic; the residual risk is divergence between an implementation and the reference
  logic — mitigated by the conformance tests that bind implementations to the same
  vectors. `partial` and `none` rows carry the residual risk of their method.
- `token`, `transport`, `x509`, and `cross-object` categories, and the `temporal`
  vectors R16 does not execute, require live systems; they are covered by the in-spec
  conformance test definitions and MUST be executed against a deployment before a
  conformance claim. Leaving them without suite automation risks drift between spec text and
  deployed behaviour — bounded by the release gate: "all executable critical tests
  pass + every non-executable requirement has a documented verification procedure".
- **Documented non-tested behaviours (integration-class, recorded per the adversarial
  review):** (a) subsequent-receipt delivery + its `receipt:{payment_reference}:{status}`
  dedup (Assets §3.2.1) — normative text and idempotency rules exist; end-to-end
  delivery requires two live agents; (b) audit tamper DETECTION behaviour
  (altered/removed/truncated trails, State §7.2) — since DR-5, harness R14 verifies
  chains against a held head and the tampered vectors ITV-597..599 fail with their
  stated reason; a deployed verifier still needs its own independent chain head; (c) DORA business-vs-infrastructure
  discrimination (Assets §6.2) — the criteria are normative, the classification is
  the operator's compliance function by design. All three are release-gated by
  documented verification procedures, not suite tests.
