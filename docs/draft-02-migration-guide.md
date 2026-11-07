<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# ARSIA Protocol — Draft-01 → Draft-02 Migration Guide

Draft-02 is a **breaking release**: the wire version moves from `1.0` to `2.0`.
Draft-02 supersedes Draft-01 entirely; there is no dual-version wire. A Draft-02
implementation MAY offer Draft-01 support only as an explicitly configured
**compatibility profile** with an isolated verifier — never as a fallback after a
v2 failure — and states its conformance claims separately ("ARSIA v2 conformant";
"ARSIA v1 compatibility enabled"). See Core §4.1.1.

## 1. Signing (BREAKING — every signature changes)

| | Draft-01 | Draft-02 |
|---|---|---|
| Signing input | JCS(envelope with the whole `security` object removed) | JCS(envelope with `security` present, **only the `sig` property removed**) |
| Protected | everything except `security` | everything except the signature value — including `alg`, `kid`, encryption metadata, `authorization` |

A Draft-01 signature never verifies under Draft-02 and vice versa — deliberate:
there is no silent ambiguity. Verifiers MUST NOT retry a failed v2 verification
under the v1 input (diagnostic-only recomputation for logging is acceptable;
acceptance is not). Verification now follows the staged pipeline of Core §5.2
(minimal pre-signature validation; schema/authorization/compliance only after the
signature verifies) and enforces algorithm/key-type coherence.

**Action:** re-sign everything; regenerate stored fixtures with
`scripts/regen_v2.py`-equivalent logic; update verifiers to remove only `sig`.

## 2. Envelope changes

- `v` is `"2.0"`. Media type parameter becomes `application/arsia+json; v=2`.
- **NEW `root_request_id`** (Core §4.2.4): REQUIRED wherever `correlation_id` is
  required; equals the interaction's initiating request `id`; MUST be absent on
  the initiating request. `correlation_id` is normatively the **immediately
  preceding message** (Core §2.2/§4.2.1) — implementations that read Draft-01
  §2.2 as "always the original request" must change `approval_decision` handling.
- **NEW `authorization`** (Core §4.3.9): `{token_hash, proof_type}`; REQUIRED when
  `compliance.data_residency` is set; hash-binds the signed envelope to the
  sender's end-to-end token.
- `compliance.retention_days` (integer) → **`compliance.retention`** (ISO 8601
  calendar duration): `retention_days: 1827` → `retention: "P1827D"`. Same rename
  on StateEntry (§2.1.8) and the ActionDescriptor override.
- Per-message `ai_system_classification` no longer accepts
  `"unacceptable-risk"` (agent-level classification keeps all four values).
- Exactly one payload content field (`args`/`result`/`data`/`error`) — multiple
  or zero content fields are rejected (`invalid_request`), no warn-and-pick.
- `payload.version` absent now means exactly `"1.0"` (was: "latest known to
  receiver").

## 3. Retention model (BREAKING behaviour)

- Below-floor declarations are **rejected** (`invalid_request` +
  `insufficient_retention` details), never silently clamped — for every profile
  with a `retention_minimum`, not only MiFID-II. Absent `retention` → the profile
  minimum applies.
- Floors are typed calendar durations with calendar arithmetic and an explicit
  anchor (Core §4.3.6.4.1): EU-AI-ACT-HIGH-RISK is `"P6M"` (six calendar months,
  NOT 180 days), MIFID-II/DORA `"P1827D"`, PAC `"P1096D"`, DSA-VLOP `"P1096D"`
  (raised from the Draft-01-era 2-year value after legal triage located the
  retention basis in DSA Art. 34(3), three years), LIMITED `"P90D"`.
- Audit records now carry `compliance_profile_declared` + `compliance_profile_resolved`
  (replacing `compliance_profile`), `declared_retention`, `effective_retention`,
  `retention_anchor`, `retention_source`, and `counterparty_owner_id`.

## 4. Amounts (BREAKING wire type)

All asset amounts (`amount`, `actual_amount`, `reversal_amount` — request,
receipt, reversal, escrow, audit records) change from JSON **number** to
**canonical decimal string**: `1500.00` → `"1500.00"`. Currency amounts use the
**fixed ISO 4217 scale** — exactly the minor-unit digits: EUR `"1500.00"`, JPY
`"1500"`, KWD `"1500.000"`; `"1500"`, `"1500.0"`, `"1500.000"` are all invalid
for EUR. No exponent/sign/leading zeros/thousands separators; no negative
amounts anywhere (reversals are an operation with a positive `reversal_amount`).
Numeric amounts fail schema validation loudly. Process amounts with decimal or
integer minor-unit arithmetic — never binary floats. Declare your ISO 4217
catalog edition via the new discovery field `iso4217_edition`.

## 5. Broker relay (Draft-01 flow was unexecutable — replaced)

- Senders request `arsiaprotocol.broker.use` (new, delegable) — never
  `broker.relay` (broker-only role, like all reserved capabilities now
  non-delegable).
- Sender obtains the normal end-to-end token (sub=sender, aud=recipient), binds
  it into the signed envelope (`authorization.token_hash`), and sends it with
  the message (`ARSIA-Recipient-Token`, optional `ARSIA-Recipient-DPoP`).
- The broker forwards the byte-identical envelope with that token verbatim plus
  a signed **relay attestation** (`ARSIA-Relay-Attestation`,
  `arsia-relay-attestation.schema.json`). Recipient validation of tokens is
  unchanged (sub==from, aud==to).
- Recipients MUST require the attestation for residency-constrained messages —
  direct delivery of a `data_residency` message is now rejected (bypass
  detection).
- The `BrokerRelayAuditRecord` type is retired; relay audit is an
  `ArsiaAuditRecord` with `event_type: "broker_relay"` (Routing §7.4.2).
- RFC 8693 token exchange is an OPTIONAL profile (Routing §2.3.2.1).

## 6. Authorization & identity

- Token validation now validates `iss` against an explicit issuer trust
  configuration (Core §6.5) and resolves keys only from the configured origin.
- Agent-id → origin resolution is an explicit registry mechanism (Core §6.6);
  heuristic DNS guessing is prohibited.
- Capability matching is one algorithm (Actions §1.2, referenced by Core §6.4):
  wildcard scopes never satisfy `arsiaprotocol.` capabilities; `arsiaprotocol.*`
  scope entries satisfy nothing. Reserved names outside the Actions §1.4
  registry (now including `echo`, `health`, `onboarding.evaluate`,
  `broker.use`) are rejected.
- JWKS cache ceiling is 3600 s; key removal is the revocation signal; emergency
  rotation SHOULD emit `arsiaprotocol.identity/key-revocation`, which a recipient
  acts on only after authenticating it (§11).
- The onboarding decision no longer reuses `approval_decision`: it is a `request`
  with payload `arsiaprotocol.onboarding/decision`.
- The unsigned `Idempotency-Key` header no longer overrides the signed
  `idempotency.key` (replay-defence fix).
- Wildcard audiences are removed; new IdentityRecord fields: `regulated_entity`.

## 7. Approval & assets flows

- `pending_approval`/`approval_decision` use only the canonical Actions §3.2/§3.3
  contract (`payload.args`; `approved|denied`; `denied|expired` statuses) — the
  Assets-specific `payload.result` shape and `rejected`/`timeout` values are gone.
- Subsequent receipts (pending→completed/failed; escrow outcomes) are delivered
  as new `request` messages with payload `arsiaprotocol.assets/transfer-receipt`
  and idempotency `receipt:{payment_reference}:{status}` (Assets §3.2.1).
- MiFID audit records are immutable: `updated_at` removed; corrections append.
- The DORA incident event is renamed `ict_incident`
  (`arsiaprotocol.ict/incident`) and fires on incident-candidate criteria, not on
  any single provider timeout.
- MiFID retention constant is uniformly 1827 days (was 1825 in three documents).

## 8. Compliance profiles

- Extension profiles use reverse-domain names (`com.example.profile`),
  published as catalog documents, advertised via
  `compliance_profiles_supported`. Unknown names: warn+GDPR-STANDARD default, or
  reject under strict mode (`strict_compliance` discovery flag).
- Data-residency codes are a closed set: ISO 3166-1 alpha-2 ∪ `"EU"`; custom
  regional codes are removed.

## 9. State entries: generations and retention-protected PURGE

- **Generations (State §2.1.14, §8.4).** Every StateEntry and every `state_set`,
  `state_delete` and `state_purge` audit record carries `generation`. A SET may
  carry `expected_generation` (a conditional write); a mismatch is rejected with
  the State §8.4 details, including `entry_live: false` when no live entry exists.
  Keep the highest generation of a key while any information of it is held.
- **PURGE and retention (State §3.2.2, §8.4).** A PURGE is evaluated against the
  stored retention of every generation of the entry. Within retention it is
  rejected with the State §8.4 retention details unless the request carries a
  `retention_override`. `state_purge` records carry `within_retention`,
  `entry_retained_until` and, when used, `retention_override`.

## 10. Broker relay audit and DPoP

- Brokers emit a `broker_relay` audit record for every message received for
  relay. The forwarding fields appear only when forwarding was initiated, and
  `relay_latency_ms` is computed from the two instants (Routing §7.4.2).
- A recipient that requires a DPoP nonce answers with a challenge. The broker
  returns it to the sender as a `recipient_dpop_nonce` relay error and never
  re-sends the message or produces a proof itself; the sender retries with a new
  proof (Routing §2.3.3).
- Receiving agents implement the Identity §3.3 DPoP checks, the nonce challenge,
  and an atomic, shared single-use `jti` store that holds each `jti` until
  `iat` + S.

## 11. Approval decisions and key revocation

- **Verification order (Actions §3.4).** The executing agent verifies an
  `approval_decision`, approved or denied, in the order Actions §3.4 lists. The
  deadline is compared at the instant of receipt, with no clock-skew tolerance.
  Path 3 (deadline expired) applies only while the `pending_approval` is still
  pending.
- **Rejected decisions.** A decision that fails verification, arrives late or is
  a duplicate is logged as a `decision_rejected` audit record, with its
  `rejection_code` (Core §4.2.1; State §7.1). The log is now a MUST; the replies to
  the sender stay SHOULD. Rejected post-execution review decisions are logged the
  same way (Actions §3.9.3).
- **Verification evidence (Core §5.2; State §7.1).** For compliance-relevant
  messages whose signatures the log owner successfully verified, the audit record
  carries `verified_kid` and `jwks_fetched_at`, the instant of the JWKS fetch that
  supplied the key. Records of messages whose signatures were not verified or
  failed verification carry neither.
- **Key revocation (Identity §2.5).** The `arsiaprotocol.identity/key-revocation`
  event has its own payload schema (`arsia-key-revocation.schema.json`). A
  recipient acts on it only after authenticating it: its signature verifies with
  another key of the sender, never the revoked one. An unauthenticated event is
  rejected and invalidates nothing. An authenticated event invalidates the cached
  key at once.

## 12. Message parsing and the relay attestation header

- **Strict parsing (Core §5.2 steps 2–4).** A document is valid UTF-8; unpaired
  surrogates and noncharacters, literal or escaped at any depth, are rejected;
  duplicate member names, compared after escape processing, are rejected. A
  failure is `invalid_request`. The steps add no limit on JSON numbers
  ([RFC 7493] is now a normative reference).
- **Attestation header (Routing §7.4.1).** A residency-constrained message that
  arrives without the `ARSIA-Relay-Attestation` header is rejected with
  `service_unavailable` (step 1). A present header, even an empty one, goes through
  steps 2–5. The header is non-empty base64url **without padding**; the decoded
  octets pass the Core §5.2 steps 2–4 and the attestation schema before the
  signature is checked. These failures are `unauthorized`, not `invalid_request`.

## 13. Test vectors and keys (for implementations that use the corpus)

- The corpus header is `version` `2.0.0` (the Draft-01 corpora were 1.0.x).
- `keypairs.json` has 54 entries with a `provenance` member: 17 Draft-02 entries,
  35 imported unchanged from the Draft-01.1 catalog, and 2 generated. An agent's
  additional key is indexed by its full `kid`.
  The RSA-1024 key `agent:acme.legacy-system#rsa1024` is deliberately below the
  protocol's minimum key size. ITV-425 carries a mathematically valid signature
  that a conformant verifier rejects for insufficient key size.
- A signature outside a `crypto` block verifies with the catalog key of its `kid`,
  unless the vector declares `signature_expectation`. That field declares a
  signature negative, with its cause and condition.
- A vector whose envelope carries `authorization` and no explicit presented token
  binds `synthetic-token:<ID>`.
- In runtime-only schema-ref vectors, `expected` is the structural result and the
  runtime outcome is `expected_error`.
- INV-21 is a schema-ref vector against `#/$defs/set-args`.

## 14. What did NOT change

Payload-type versioning semantics (only its default and discovery were fixed);
the six-intent model; JCS/RFC 8785 canonicalization; Ed25519 as primary
algorithm; the 7 standard profiles' names; agent-id grammar; the discovery,
JWKS, inbox endpoints; GRANT semantics (clarified, not changed). PURGE is
**not** unchanged: it now honours stored retention and `retention_override` (§9).
