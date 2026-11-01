<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Draft-02 Skip Classification

Every `skip_schema` vector in `test-vectors/arsia-test-vectors.json`, individually
classified per the Draft-02 plan. A skip is a vector whose requirement is real but
not expressible in JSON Schema; the classification records WHY, what verification
method covers it instead, and the residual risk of leaving it without full
automation. No skip hides a failure: the suite reports 0 failures with every skip
accounted for below.

**Verification methods:** `harness Rn` = executable reference-logic test in
`scripts/runtime_harness.py`; `integration` = requires two communicating
implementations (covered by the documented conformance tests CORE-*/ACTIONS-*/
IDENTITY-*/STATE-*/ROUTING-*/ASSETS-* in the specs, executed against a real
deployment); `deployment inspection` / `operational evidence` = release-gate
procedures, not suite tests (see Core §12.3).

**Category totals:** amount-scale: 2, capability: 5, compliance-resolution: 32, cross-object: 5, crypto-behaviour: 7, executor-oversight: 35, forward-compat: 4, numeric: 2, other: 17, retention-floor: 6, temporal: 12, token: 15, transport: 5, x509: 7 — total 154.

| ID | Anchor | Reason (abridged) | Category | Requirement class | Runtime-test candidate / coverage |
|---|---|---|---|---|---|
| INV-07 | Identity §4.2, Core §4.3.8 Rule 3 | Runtime constraint — high-risk requirement set over the composed oversight set (Core §4.3.10) | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| INV-08 | Core §4.3.8 Rule 4 | Runtime constraint — calendar retention-floor comparison (Core §4.3.8 Rule 4); Draft-02 moved floors from sche | retention-floor | behavioural-runtime | covered: harness R2 |
| INV-09 | — | Runtime constraint — currency precision enforced programmatically | other | behavioural-runtime | yes |
| INV-11 | — | Runtime constraint — kid↔from cryptographic binding | other | behavioural-runtime | yes |
| INV-12 | — | Runtime semantic constraint — reversal requires original transfer status completed | other | behavioural-runtime | yes |
| INV-18 | — | Runtime signature verification — schema cannot validate cryptographic correctness of ECDSA signatures | crypto-behaviour | behavioural-runtime | yes |
| INV-19 | — | Runtime signature verification — schema cannot validate cryptographic correctness of RSA signatures | crypto-behaviour | behavioural-runtime | yes |
| INV-20 | — | Runtime constraint — cross-object validation between payload.args.pii_classification and compliance.legal_basi | cross-object | behavioural-runtime | yes |
| INV-22 | — | Runtime constraint — schema cannot enforce mutual exclusion (MUST NOT be present when not sensitive) | other | behavioural-runtime | yes |
| INV-23 | — | Runtime constraint — wildcard matching exclusion for non-delegable capabilities is not schema-enforceable | capability | behavioural-runtime | covered: harness R3/R4 |
| INV-24 | — | Runtime constraint — wildcard matching exclusion for non-delegable capabilities is not schema-enforceable | capability | behavioural-runtime | covered: harness R3/R4 |
| INV-25 | — | Runtime constraint — wildcard matching exclusion for non-delegable capabilities is not schema-enforceable | capability | behavioural-runtime | covered: harness R3/R4 |
| INV-37 | Core §5.2 | Runtime constraint — signature verification behaviour (Core §5.2); tamper cannot be expressed as a schema outc | crypto-behaviour | behavioural-runtime | yes |
| INV-38 | Core §5.2 | Runtime constraint — signature verification behaviour (Core §5.2) | crypto-behaviour | behavioural-runtime | yes |
| INV-39 | Core §5.2 Step 3 | Runtime constraint — signing-profile downgrade prohibition (Core §5.2 Step 3) | crypto-behaviour | behavioural-runtime | yes |
| ITV-404 | — | Runtime constraint — major version comparison not enforceable by JSON Schema pattern | other | behavioural-runtime | yes |
| ITV-405 | Core §4.1.1 rules 2-3 | Forward-compat — the published schema validates exactly the 2.0 minor; a 2.1 message is accepted via the major | forward-compat | behavioural-runtime | yes |
| ITV-406 | — | Forward-compatibility — spec requires ignoring unknown fields but schema uses additionalProperties:false | forward-compat | behavioural-runtime | yes |
| ITV-408 | — | Runtime constraint — clock skew comparison not enforceable by JSON Schema | temporal | behavioural-runtime | yes |
| ITV-409 | — | Runtime constraint — token sub comparison not enforceable by JSON Schema | token | behavioural-runtime | yes |
| ITV-410 | — | Runtime constraint — token aud comparison not enforceable by JSON Schema | token | behavioural-runtime | yes |
| ITV-411 | — | Runtime constraint — timestamp expiration comparison not enforceable by JSON Schema | temporal | behavioural-runtime | yes |
| ITV-412 | — | Runtime constraint — token scope verification not enforceable by JSON Schema | token | behavioural-runtime | yes |
| ITV-413 | — | Runtime constraint — recipient version comparison not enforceable by JSON Schema | other | behavioural-runtime | yes |
| ITV-414 | — | Runtime constraint — cross-field timestamp comparison not enforceable by JSON Schema | temporal | behavioural-runtime | yes |
| ITV-416 | — | Runtime constraint — strict-mode profile name validation not enforceable by JSON Schema | compliance-resolution | behavioural-runtime | covered: harness R10 (partial) |
| ITV-417 | Core §4.3.8 Rule 4 | Runtime constraint — calendar retention-floor comparison (Core §4.3.8 Rule 4); Draft-02 moved floors from sche | retention-floor | behavioural-runtime | covered: harness R2 |
| ITV-418 | — | Runtime constraint — cross-reference to IdentityRecord classification not enforceable by JSON Schema | compliance-resolution | behavioural-runtime | covered: harness R10 (partial) |
| ITV-421 | Core §4.3.8 Rule 3, A-09 | Runtime constraint — Rule 3 checks the EFFECTIVE human_oversight (per-message OR profile default); the schema  | compliance-resolution | behavioural-runtime | covered: harness R10 (partial) |
| ITV-422 | — | Runtime constraint — payload type recognition is implementation-specific, not schema-enforceable | other | behavioural-runtime | yes |
| ITV-424 | — | Runtime constraint — message size enforcement not expressible in JSON Schema | other | behavioural-runtime | yes |
| ITV-425 | — | Runtime constraint — RSA key size validation not enforceable by JSON Schema (JWK schema does not define RSA ke | other | behavioural-runtime | yes |
| ITV-426 | — | Runtime constraint — signature byte length validation not enforceable by JSON Schema (sig is type:string) | crypto-behaviour | behavioural-runtime | yes |
| ITV-427 | — | Runtime constraint — JWE header vs security field algorithm comparison not enforceable by JSON Schema | transport | integration | yes |
| ITV-429 | — | Runtime constraint — JWE decryption success not verifiable by JSON Schema | other | behavioural-runtime | yes |
| ITV-431 | — | Runtime constraint — token sub vs. message from cross-check requires access token context unavailable to JSON  | token | behavioural-runtime | yes |
| ITV-432 | — | Runtime constraint — token aud vs. message to cross-check requires access token context unavailable to JSON Sc | token | behavioural-runtime | yes |
| ITV-433 | — | Runtime constraint — token scope vs. message capabilities cross-check requires access token context unavailabl | token | behavioural-runtime | yes |
| ITV-434 | — | Runtime constraint — token expiration requires time comparison unavailable to JSON Schema | temporal | behavioural-runtime | yes |
| ITV-435 | — | Runtime constraint — token issued-at time comparison requires clock unavailable to JSON Schema | temporal | behavioural-runtime | yes |
| ITV-436 | — | Runtime constraint — enforcement procedure step 3 requires token context unavailable to JSON Schema | token | behavioural-runtime | yes |
| ITV-437 | — | Runtime constraint — enforcement procedure step 3 requires token context and receiver identity unavailable to  | token | behavioural-runtime | yes |
| ITV-438 | — | Forward-compatibility — schema uses additionalProperties:false but §7.4 mandates acceptance of unknown fields  | forward-compat | behavioural-runtime | yes |
| ITV-439 | — | Forward-compatibility — schema uses additionalProperties:false but §7.4 requires ignoring and preserving unkno | forward-compat | behavioural-runtime | yes |
| ITV-440 | — | Runtime constraint — timestamp freshness requires clock comparison unavailable to JSON Schema | temporal | behavioural-runtime | yes |
| ITV-442 | — | Runtime constraint — Content-Type header v parameter vs. envelope v field comparison is HTTP-level, not messag | transport | integration | yes |
| ITV-445 | §3.1 step 3 | Runtime constraint — kid-prefix-to-from cross-field comparison not enforceable by JSON Schema | cross-object | behavioural-runtime | yes |
| ITV-446 | — | Runtime constraint — cross-object comparison between message compliance and IdentityRecord not enforceable by  | cross-object | behavioural-runtime | yes |
| ITV-448 | ±300s clock skew per Core §8.3 | Runtime constraint — iat temporal validation (±300s clock skew per Core §8.3) not enforceable by JSON Schema | temporal | behavioural-runtime | yes |
| ITV-449 | — | Runtime constraint — nbf temporal validation not enforceable by JSON Schema; schema does not define nbf field  | temporal | behavioural-runtime | yes |
| ITV-450 | — | Runtime constraint — nbf temporal validation not enforceable by JSON Schema; schema does not define nbf field | temporal | behavioural-runtime | yes |
| ITV-457 | — | Runtime constraint — X.509 certificate content validation not enforceable by JSON Schema | x509 | integration | yes |
| ITV-458 | — | Runtime constraint — X.509 certificate content validation not enforceable by JSON Schema | x509 | integration | yes |
| ITV-459 | — | Runtime constraint — X.509 certificate content validation not enforceable by JSON Schema | x509 | integration | yes |
| ITV-460 | — | Runtime constraint — X.509 certificate content validation not enforceable by JSON Schema | x509 | integration | yes |
| ITV-461 | — | Runtime constraint — X.509 certificate content validation not enforceable by JSON Schema | x509 | integration | yes |
| ITV-462 | — | Runtime constraint — X.509 certificate content validation not enforceable by JSON Schema | x509 | integration | yes |
| ITV-463 | — | Runtime constraint — X.509 certificate content validation not enforceable by JSON Schema | x509 | integration | yes |
| ITV-466 | — | Runtime constraint — trust level acceptance policy not enforceable by JSON Schema | other | behavioural-runtime | yes |
| ITV-467 | — | Runtime constraint — trust level acceptance for all levels not enforceable by JSON Schema | other | behavioural-runtime | yes |
| ITV-475 | — | Runtime constraint — Ed25519 signature verification over identity record not enforceable by JSON Schema | crypto-behaviour | behavioural-runtime | yes |
| ITV-476 | — | Runtime constraint — kid-prefix-to-agent_id cross-artifact comparison not enforceable by JSON Schema | other | behavioural-runtime | yes |
| ITV-477 | — | Runtime constraint — cross-message from-field to agent_id comparison not enforceable by JSON Schema | other | behavioural-runtime | yes |
| ITV-479 | — | Runtime constraint — cross-message correlation_id matching not enforceable by JSON Schema | capability | behavioural-runtime | covered: harness R3/R4 |
| ITV-487 | — | Runtime constraint — verify-token endpoint response behavior not enforceable by JSON Schema | token | behavioural-runtime | yes |
| ITV-526 | — | Runtime constraint — cross-object audit-record-to-message comparison: plaintext_hash presence depends on secur | token | behavioural-runtime | yes |
| ITV-536 | — | Runtime inheritance — schema cannot validate that entry.data_residency was inherited from compliance.data_resi | compliance-resolution | behavioural-runtime | covered: harness R10 (partial) |
| ITV-537 | — | Runtime precedence — schema cannot validate field precedence between envelope and args | other | behavioural-runtime | yes |
| ITV-538 | — | Runtime inheritance — schema cannot validate retention field propagation | retention-floor | behavioural-runtime | covered: harness R2 |
| ITV-539 | — | Runtime max() computation — schema cannot validate arithmetic on field values | other | behavioural-runtime | yes |
| ITV-540 | — | Runtime validation — schema cannot validate cross-field between compliance.legal_basis and pii_classification | cross-object | behavioural-runtime | yes |
| ITV-541 | — | Runtime profile loading — schema cannot validate profile default resolution | compliance-resolution | behavioural-runtime | covered: harness R10 (partial) |
| ITV-543 | — | Transport-specific runtime behaviour — WebSocket idempotency uses envelope field only, not HTTP header | transport | integration | yes |
| ITV-544 | — | Runtime duplicate detection — requires multi-message context and transport state | transport | integration | yes |
| ITV-545 | — | Runtime clock skew validation — schema cannot compare ts against current time or profile tolerance | temporal | behavioural-runtime | yes |
| ITV-546 | — | Runtime clock skew validation — schema cannot compare ts against current time or profile tolerance | temporal | behavioural-runtime | yes |
| ITV-547 | — | Runtime clock skew validation — schema cannot compare ts against current time or profile tolerance | temporal | behavioural-runtime | yes |
| ITV-553 | — | Runtime constraint — audit_required override is runtime behaviour not enforceable by JSON Schema | token | behavioural-runtime | yes |
| ITV-554 | — | Runtime constraint — audit_required override is runtime behaviour not enforceable by JSON Schema | token | behavioural-runtime | yes |
| ITV-555 | — | Runtime constraint — cross-object validation between payload.args.pii_classification and compliance.legal_basi | cross-object | behavioural-runtime | yes |
| ITV-563 | Core §4.3.8 Rule 4 | Runtime constraint — calendar retention-floor comparison (Core §4.3.8 Rule 4); schema validates format only | retention-floor | behavioural-runtime | covered: harness R2 |
| ITV-564 | Core §4.3.6.4.1 | Runtime constraint — calendar retention-floor comparison with month arithmetic (Core §4.3.6.4.1) | retention-floor | behavioural-runtime | covered: harness R2 |
| ITV-565 | Core §4.3.7 | Runtime constraint — retention resolution from profile minimum (Core §4.3.7) | retention-floor | behavioural-runtime | covered: harness R2 |
| ITV-566 | Actions §1.2 | Runtime constraint — token-scope wildcard matching (Actions §1.2); token not part of the envelope | token | behavioural-runtime | yes |
| ITV-567 | Actions §1.2 condition 3 | Runtime constraint — reserved-namespace exact-match rule (Actions §1.2 condition 3) | other | behavioural-runtime | yes |
| ITV-568 | Actions §1.1 Rule 5 / §1.4 | Runtime constraint — reserved-registry membership (Actions §1.1 Rule 5 / §1.4) | capability | behavioural-runtime | covered: harness R3/R4 |
| ITV-570 | Routing §7.4.1 | Runtime constraint — transport-header presence and recipient enforcement (Routing §7.4.1) | transport | integration | yes |
| ITV-571 | Core §6.4, Routing §1.2.2 | Runtime constraint — token/transport behaviour outside the envelope (Core §6.4, Routing §1.2.2) | token | behavioural-runtime | yes |
| ITV-572 | Routing §1.2.2, Core §6.4/§6.5 | Runtime constraint — token audience/scope checks (Routing §1.2.2, Core §6.4/§6.5) | token | behavioural-runtime | yes |
| ITV-575 | Assets §3.1.1 | Runtime constraint — per-currency fixed scale requires the ISO 4217 catalog (Assets §3.1.1) | amount-scale | behavioural-runtime | covered: harness R5 |
| ITV-576 | Assets §3.1.1 | Runtime constraint — per-currency fixed scale requires the ISO 4217 catalog (Assets §3.1.1) | amount-scale | behavioural-runtime | covered: harness R5 |
| ITV-577 | State §2.1.2 | Runtime constraint — I-JSON number-range rule (State §2.1.2); JSON Schema cannot distinguish 2^53+1 reliably | numeric | behavioural-runtime | covered: harness R8 |
| ITV-578 | State §2.1.2 | Runtime constraint — value-semantics round-trip behaviour (State §2.1.2) | numeric | behavioural-runtime | covered: harness R1/R8 |
| ITV-579 | Core §4.3.7/§4.3.8 Rule 3 | Runtime constraint — effective-oversight resolution across profile defaults (Core §4.3.7/§4.3.8 Rule 3) | compliance-resolution | behavioural-runtime | covered: harness R10 (partial) |
| ITV-603 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-604 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-605 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-606 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-607 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-608 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-609 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-610 | Identity §7.7 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-611 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-612 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-613 | Identity §7.7 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-614 | Identity §7.7 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-615 | Identity §7.7 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-616 | Identity §7.7 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-617 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-618 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-619 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-620 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-621 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-622 | Core §4.3.10 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-623 | Identity §7.2 Step 7, CHECK-05 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-624 | Identity §7.2 Step 7, CHECK-05 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-625 | Identity §7.2 Step 7, CHECK-05 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-626 | Identity §7.7 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-627 | Identity §7.7 | Runtime constraint — effective obligation resolution (Core §4.3.10); input and expected result in test_metadat | compliance-resolution | behavioural-runtime | covered: harness R10 (test_metadata scenario) |
| ITV-640 | Actions §3.2, §3.7; Core §4.3.10.2 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-641 | Actions §3.2, §3.7; Core §4.3.10.2 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-642 | Actions §3.2, §3.7; Core §4.3.10.2 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-643 | Actions §3.2, §3.7; Core §4.3.10.2 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-644 | Actions §3.2, §3.7; Core §4.3.10.2 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-645 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-646 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-647 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-648 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-649 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-650 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-651 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-652 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-653 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-654 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-655 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-656 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-657 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-658 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-659 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-660 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-661 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-662 | Actions §3.4, §3.6 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-663 | Actions §3.4, §3.6 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-664 | Actions §3.4, §3.6 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-665 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-666 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-667 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-668 | Identity §7.7, §9.1 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-669 | Identity §7.7, §9.1 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-670 | Identity §7.3 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-671 | Identity §7.3 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-672 | Assets §5.2 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-673 | Assets §5.2 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |
| ITV-674 | Actions §3.9 | Runtime constraint — executor oversight and post-execution review (Actions §3, §3.9; Core §4.3.10.2); input an | executor-oversight | behavioural-runtime | covered: harness R15 (test_metadata scenario) |

## Residual risk statement

- Categories covered by the harness (retention-floor, capability, amount-scale,
  numeric, compliance-resolution in part) have executable reference logic; the
  residual risk is divergence between an implementation and the reference logic —
  mitigated by the conformance tests that bind implementations to the same vectors.
- `temporal`, `token`, `transport`, `broker-relay`, `x509`, and `cross-object`
  categories require live systems; they are covered by the in-spec conformance
  test definitions and MUST be executed against a deployment before a conformance
  claim. Leaving them without suite automation risks drift between spec text and
  deployed behaviour — bounded by the release gate: "all executable critical tests
  pass + every non-executable requirement has a documented verification procedure".
- The single `transitional` skip (INV-36 class) is scheduled automation, not a gap.
- **Documented non-tested behaviours (integration-class, recorded per the adversarial
  review):** (a) subsequent-receipt delivery + its `receipt:{payment_reference}:{status}`
  dedup (Assets §3.2.1) — normative text and idempotency rules exist; end-to-end
  delivery requires two live agents; (b) audit tamper DETECTION behaviour
  (altered/removed/truncated trails, State §7.2) — the scope statement is normative
  and ITV-95 covers the hash_chain format; detection itself requires a stateful
  verifier holding an independent chain head; (c) DORA business-vs-infrastructure
  discrimination (Assets §6.2) — the criteria are normative, the classification is
  the operator's compliance function by design. All three are release-gated by
  documented verification procedures, not suite tests.
