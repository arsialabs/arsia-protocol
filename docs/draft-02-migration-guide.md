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
  rotation SHOULD emit `arsiaprotocol.identity/key-revocation`.
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

## 9. What did NOT change

Payload-type versioning semantics (only its default and discovery were fixed);
the six-intent model; JCS/RFC 8785 canonicalization; Ed25519 as primary
algorithm; the 7 standard profiles' names; agent-id grammar; the discovery,
JWKS, inbox endpoints; PURGE/GRANT semantics (clarified, not changed).
