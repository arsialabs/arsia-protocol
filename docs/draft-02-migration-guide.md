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

- **Idempotency retention (Core §10.2, §10.3).** Reserve the envelope's
  `idempotency.key` atomically before any effect, and keep the association at least
  until the latest of `idempotency.expires_at`, the end of the message's acceptance
  window (`expires_at` plus the clock skew tolerance, that instant included) and
  the determined outcome of the operation. A message without `expires_at` is kept
  for as long as the server would accept it. Store the terminal response, success
  or error; release a reservation for retry only when the attempt has ended, the
  server has established that no effect occurred, no execution remains pending and
  the attempt produced no response or an error response — an undetermined outcome
  keeps the reservation; never after an effect. For an encrypted payload the scope
  uses the `type` of the decrypted payload, taken after the decryption procedure
  (Core §5.3) has succeeded. A duplicate of a reservation without a
  stored response gets `conflict` (a MUST, formerly a SHOULD), and a rejected
  message returns no stored response and releases nothing.
- **Encrypted payloads (Core §5.3).** Any message may be encrypted, errors
  included: the message schema requires the error object only of an unencrypted
  error. After decryption, parse the plaintext strictly and validate the decrypted
  view (the envelope with the decrypted `payload` and `encrypted` taken as
  `false`) against every requirement of an unencrypted message; reject a failed
  decryption with `unauthorized` and an invalid plaintext with `invalid_request`.
  Verify the signature over the received envelope only.
- **Dispute resolution (Core §5.3.1).** Audit records are not individually
  signed; matching hashes show that records identify the same content and do not
  prove transmission or receipt.

## 3. Retention model (BREAKING behaviour)

- Below-floor declarations are **rejected** (`invalid_request` +
  `insufficient_retention` details), never silently clamped — for every profile
  with a `retention_minimum`, not only MiFID-II. Absent `retention` → the profile
  minimum applies. With no declaration and no floor (GDPR-STANDARD, for example), the
  platform default `P90D` applies, recorded as `retention_source: "platform-default"`
  (Core §4.3.10.5; State §7.3).
- Floors are typed calendar durations with calendar arithmetic and an explicit
  anchor (Core §4.3.6.4.1): EU-AI-ACT-HIGH-RISK is `"P6M"` (six calendar months,
  NOT 180 days), MIFID-II/DORA `"P1827D"`, PAC `"P1096D"`, DSA-VLOP `"P1096D"`
  (raised from the Draft-01-era 2-year value after legal triage located the
  retention basis in DSA Art. 34(3), three years), LIMITED `"P90D"`.
- Audit records now carry `compliance_profile_declared` + `compliance_profile_resolved`
  (replacing `compliance_profile`), `declared_retention`, `effective_retention`,
  `retention_anchor`, `retention_source`, and `counterparty_owner_id`. A covered record
  also carries `obligation_resolution`, and its retention fields are derived from it
  (§15). The retention anchor of an audit record is its own `processed_at`, and
  `retained_until` is the anchor plus `effective_retention`.

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

- **Scope grammar (Core §6.1, §6.4 step 4).** `scope` follows RFC 6749 §3.3 in the
  token claims, the token request and the token response: tokens of visible ASCII
  characters other than `"` and `\`, separated by exactly one space, with no leading
  or trailing space. A tab, a line break or two spaces between capabilities, accepted
  before, now make the value invalid. Validate the whole value before splitting it —
  a split on white space would turn an invalid value into granted capabilities — and
  reject a token whose `scope` does not conform with `unauthorized`.

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
- **Asset audit records (Assets §3.2.1, §3.3.2; State §7.1).** Every `asset_transfer`
  record carries `payment_reference`: a plain transfer's own reference, the escrow
  transfer's reference, or, on a reversal record, the original transfer's reference.
  A reversal record is the `asset_transfer` record whose `payload_type` is
  `arsiaprotocol.assets/transfer-reversal`; it also carries `original_audit_id`, the
  `record_id` of the original transfer's record. The reversal receipt keeps its new
  reference (`…-REV-1`), so its `payment_reference` differs from that of the record
  its `audit_id` references. A query by `payment_reference` returns the records of the
  chain, not a single record. `sub_type` stays reserved to escrow.
- **Incident audit records (Assets §6.2.3; State §7.1).** An `ict_incident` record
  carries `incident_type`, `affected_service`, `started_at`, `estimated_impact`,
  `severity` and `original_payment_reference`, with the values, types and limits of
  the event's `payload.data`, and `resolved_at` exactly as in the event (absent, `null`
  or a timestamp).
- **Escrow audit records (Assets §4.3; State §7.1).** Each record's base fields
  (`message_id`, `from_agent`, `to_agent`, `intent`, `payload_type`, `payload_hash`)
  document the message of its transition: the AssetTransferRequest on creation
  (`arsiaprotocol.assets/transfer-request`), the release message on release
  (`payload_type` equal to `release_trigger`), the `escrow-dispute` and `escrow-cancel`
  messages. A timeout has no incoming message: its record documents the request that
  created the escrow and shares its `message_id`, with its own `record_id` and
  `processed_at`. `from_agent`/`to_agent` are envelope agents; the creation record
  carries the payer and payee in the REQUIRED `payer_agent`/`payee_agent`. An
  `escrow_returned` record carries exactly one of `actual_timeout` and
  `cancellation_reason`.
- **Escrow dispute notification (Assets §4.2.3, §4.3.4).** A dispute reaches the
  escrow in two messages. The party sends the dispute to the `arbitration_agent`,
  which checks the signature, that the sender is the payer or the payee and that
  `disputed_by` is the sender. The `arbitration_agent` then notifies the escrow
  holder with a signed request of the same type, carrying the same
  `payment_reference`, `dispute_reason` and `disputed_by`. The escrow becomes
  `DISPUTED` only when the holder has verified that notification. The holder runs
  the Core §5.2 pipeline first (signature and token failures are `unauthorized`,
  an invalid message is `invalid_request`) and looks up no escrow before it; then
  an unknown `payment_reference` is `not_found`, a sender that is not that
  escrow's arbitration agent is `forbidden`, and a `disputed_by` that is no party,
  an escrow that is not `ESCROWED` or a notification received at or after
  `timeout_at` is `invalid_request`. The `escrow_disputed` record documents the
  notification: `from_agent` is the arbitration agent, `to_agent` the holder.
- **Order of escrow events (Assets §4.2, §4.2.1).** While the escrow is
  `ESCROWED`, what counts is the instant at which the holder received a release,
  a cancellation or a dispute notification, on its own clock: received strictly
  before `timeout_at` it precedes the timeout, however long its verification
  takes; received at or after it, it is late. Do not start the return while such
  a message is still being verified. While the escrow is `DISPUTED` the timeout
  is suspended and the arbitration agent may resolve it after the original
  `timeout_at`.
- **Escrow timeout (Assets §4.2.2).** The return is an operation of the holder
  with its payment provider, not an AssetTransferReversal: no reversal message,
  no reversal capability. The 60 seconds bound the timeout check, not the return
  or the receipt. Start the return by one decision that evaluates again that the
  escrow is `ESCROWED`, that `timeout_at` was reached and that every message
  received before it was decided, and reserve it once: a repeated timer or a
  retry after a lost provider answer resumes that same return. Issue the `failed`
  receipt only after the provider has confirmed the return.
- **Escrow release (Assets §4.2.1).** Reserve the release as the escrow's
  financial operation before instructing the provider, and reconcile that same
  operation while its outcome is uncertain: a retry, a cancellation or the
  timeout must not cause a second financial effect, and a return starts only when
  no financial operation is reserved for the escrow. Issue the `completed` receipt
  only after the provider has confirmed the release.

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

- **Entry residency (State §8.3 rule 1; Core §4.3.10.5).** A `data_residency` in the
  SET's `payload.args` is the entry's own zone, and it now has to lie within the
  residency restriction composed for the message: `FR` under a message restricted
  to `EU` is accepted, `FR` under `DE` or `EU` under `FR` is rejected with
  `invalid_request` and `obligation_conflict` on the `residency` axis. The comparison
  uses the composed restriction, which includes a profile default (MIFID-II fills
  `EU`), not only the literal `compliance.data_residency`. Without the argument, an
  entry keeps its own zone, and an entry that has none inherits the message's filled
  value. Session entries are outside this rule (State §1.1). This rejection is not
  `data_residency_violation`, which still reports a permitted zone the store cannot
  serve.
- **Retention is fixed per generation (State §2.1.8, §3.1.2 rule 7, §8.4).** The
  effective retention is resolved when the generation is created, also when it comes
  from a profile floor, and an update never changes it. An update whose retention
  value (`payload.args.retention`, else the envelope's `compliance.retention`)
  produces another instant from `created_at`, or that falls under a floor later than
  the preserved one, is rejected with `invalid_request` and the details
  `retention_fixed`, `entry_retained_until` and `required_retained_until`.
  Equivalent durations are accepted (`P12M` over `P1Y`). An update does not restart
  the period: a version written late is retained only for the remainder of it. A
  different period takes a new generation.
- **SNAPSHOT hash (State §3.2.1; Actions §1.4).** `hash` is `"sha-256:"` followed by
  the lowercase hex SHA-256 of the RFC 8785 form of `{as_of, entries}` as carried in
  the result, in the order carried; `hash` and `timestamp` are not hashed. The prefix
  is `sha-256:` (earlier corpus values used `sha256:` and are now rejected by the
  schema). No order is defined for `entries`, so two implementations may produce
  different values for the same state.
- **QUERY order and pagination (State §3.1.4).** Order results by `created_at`
  and, at equal `created_at`, by `key` as ASCII bytes — a case-sensitive
  comparison, not the collation of the database. Compute `total` and `entries`
  over the same authorised, filtered set and apply `offset` and `limit` after the
  ordering. Each request is evaluated on its own: pages are consistent with each
  other only while the set does not change. For a reading at one instant use
  SNAPSHOT with `as_of`.
- **Keys are not paths (State §10.2).** The key grammar is unchanged and allows
  dots and slashes; `agent:acme.echo-client/agent/../../other/secret` is a valid
  key. A backend that maps keys to paths or object names treats every segment as
  data, keeps each operation inside the storage space authorised for it and maps
  different keys to different objects.

## 10. Broker relay audit and DPoP

- Brokers emit a `broker_relay` audit record for every message received for
  relay. The forwarding fields appear only when forwarding was initiated, and
  `relay_latency_ms` is computed from the two instants (Routing §7.4.2).
- A recipient that requires a DPoP nonce answers with a challenge. The broker
  returns it to the sender as a `recipient_dpop_nonce` relay error and never
  re-sends the message or produces a proof itself; the sender retries with a new
  proof (Routing §2.3.3).
- `relay_id`, in relay receipts and relay errors, and `attestation_id`, in the
  attestation and the `broker_relay` record, are distinct identifiers. No equality,
  inequality or mapping between them is required; do not assume they are equal
  (Routing §2.3.3).
- Receiving agents implement the Identity §3.3 DPoP checks, the nonce challenge,
  and an atomic, shared single-use `jti` store that holds each `jti` until
  `iat` + S.
- **The token's binding decides whether a proof is required (Identity §3.3).** A
  token that carries `cnf.jkt` is DPoP-bound: verify a proof for it and reject it
  with `unauthorized` when it is presented under `Bearer` or without a `DPoP`
  header ([RFC 9449] §7.2). A `cnf` that is present and malformed is rejected,
  never treated as no binding; a token without `cnf.jkt` under the `DPoP` scheme
  is rejected. Identity §7.7 no longer says "Bearer" and no longer leaves the
  verification as a SHOULD.

## 11. Approval decisions and key revocation

- **Verification order (Actions §3.4).** The executing agent verifies an
  `approval_decision`, approved or denied, in the order Actions §3.4 lists. The
  deadline is compared at the instant of receipt, with no clock-skew tolerance.
  Path 3 (deadline expired) applies only while the `pending_approval` is still
  pending.
- **Expiry record (Actions §3.5; State §7.1).** The `approval_expired` audit record
  documents the `pending_approval` whose deadline was reached: it carries that
  message's `message_id`, `timestamp`, `from_agent`, `to_agent`, `intent`,
  `payload_type` and `payload_hash`, its `correlation_id` is the pending's `id`, and
  it is processed no earlier than the `approval_deadline`. `timestamp` is REQUIRED on
  this record.
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
- **Replies that share a parent (Core §4.2.1).** `correlation_id` names the
  message a reply directly answers, not the message most recently exchanged: after
  an `accepted` acknowledgement the terminal result still correlates to the
  request. Do not treat a second reply with the same `correlation_id` as a
  duplicate by that fact alone — a `pending_approval` and the terminal result, an
  acknowledgement and the terminal result, and the decisions of distinct approvers
  share a parent. Apply a reply only as a transition the flow still permits: a
  redelivered `id`, a second terminal result and a second decision of an admitted
  approver change nothing and are logged. Reading the persisted terminal result
  again is not a delivery and is not an error.

## 12. Message parsing and the relay attestation header

- **Strict parsing (Core §5.2 steps 2–4).** A document is valid UTF-8; unpaired
  surrogates and noncharacters, literal or escaped at any depth, are rejected;
  duplicate member names, compared after escape processing, are rejected. A
  failure is `invalid_request`. The steps add no limit on JSON numbers
  ([RFC 7493] is now a normative reference).
- **Nesting depth (Core §5.2 step 2).** A recipient may limit how deeply a document
  nests and rejects the excess with `invalid_request`, in step 2. The limit is never
  lower than 32 levels: each open object or array is one level, the root container
  is level 1 and scalar values add none. Detect the excess before parsing, not
  through a failure of the parser.
- **Patterns (Core §2.3).** Patterns are ECMA-262 regular expressions: `$` matches
  only the end of the value and digits are ASCII (`[0-9]`). With a library whose
  `$` also matches before a final line break (Python's `re`), a value such as
  `"2.0\n"` passed; apply the stated semantics — a full match of an anchored
  pattern — and keep unanchored patterns as searches. A malformed `v` never selects
  the compatibility procedure of a newer minor.
- **Timestamps (Core §4.1.3).** The pattern now limits the month, day, hour, minute
  and second, and the day must exist in its month and year
  (`2026-02-30T00:00:00.000Z` is invalid). ARSIA timestamps admit neither the year
  `0000` nor the second `60` of a leap second. The schema states the calendar rule
  as `format: date-time`: assert that format, or check the calendar yourself.
- **Attestation header (Routing §7.4.1).** A residency-constrained message that
  arrives without the `ARSIA-Relay-Attestation` header is rejected with
  `service_unavailable` (step 1). A present header, even an empty one, goes through
  steps 2–5. The header is non-empty base64url **without padding**; the decoded
  octets pass the Core §5.2 steps 2–4 and the attestation schema before the
  signature is checked. These failures are `unauthorized`, not `invalid_request`.
- **Attestation zone (Routing §7.4.1 step 3).** A broker sets the attestation's
  `residency_zone` to the value of the message's `compliance.data_residency`,
  unchanged. A recipient compares the two as strings and rejects a difference with
  `unauthorized`, before it checks the broker's jurisdiction and capability for that
  zone, which remain required. No containment applies: `"PT"` does not satisfy a
  message that declares `"EU"`, nor the reverse.

## 13. Test vectors and keys (for implementations that use the corpus)

- The corpus header is `version` `2.0.0` (the Draft-01 corpora were 1.0.x).
- `keypairs.json` has 55 signature entries with a `provenance` member: 17 Draft-02
  entries, 35 imported unchanged from the Draft-01.1 catalog, and 3 generated. An
  agent's additional key is indexed by its full `kid`. One X25519 encryption
  keypair is published apart from them, in `encryption_keypairs`, for the
  encrypted-payload vectors (ITV-742, INV-249..251, INV-253, INV-254), whose JWEs
  are real (ECDH-ES direct key agreement, A256GCM).
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
- ITV-91 and INV-242 (`escrow_disputed` records) are rebuilt from the dispute
  notification ITV-746, which the arbitration agent signs with the catalog key
  `agent:arsialabs.demo.arbitrator#key1`; their `from_agent`, `to_agent`,
  `message_id`, `payload_hash`, `disputed_by` and retention fields change, and they
  carry `verified_kid` and `jwks_fetched_at`.
- INV-20, INV-22 and ITV-555 are no longer runtime-only: the message schema executes
  the Rule 8 basis and the `pii_special_categories` exclusion on a SET.
- No vector uses an `arsiaprotocol.*` payload type that the specification does not
  define, apart from three declared negatives of the type itself (ITV-265, ITV-266,
  ITV-480), the declared plaintext of the encrypted negative INV-251, and `arsiaprotocol.compliance/check` and `arsiaprotocol.onboarding/ping`,
  which the specification names only in examples. Application payloads use
  non-reserved types (`com.example.*`, `eu.mifid.risk/assess`), and error responses
  carry the type of the original request (Core §11.1).

## 14. Oversight authority and post-execution review

- **Who can require oversight (Actions §3.7; Core §4.3.10.2).** The executing agent
  resolves the effective oversight before any effect of the action, from every
  authenticated and authorized source, including its own `executor-policy` sources: the
  ActionDescriptor, the gateway's CapabilityPolicy and its risk assessment. Whether
  prior approval applies follows that effective set, not the ActionDescriptor alone. A
  `false` in one source no longer cancels a requirement from another.
- **Gateway policy in the token (Core §6.1; Identity §7.4, §8).** When the token scope
  includes a capability the CapabilityPolicy marks `oversight_required`, the token
  carries the `arsia_oversight` claim with the requirement and the policy's
  identification.
- **Executor provenance (Core §4.4.8).** A `pending_approval`, and the `response` or
  `error` that reports the outcome of a resolved action (asynchronous terminal result
  included), carry `payload.obligation_resolution`. A message that carries it must be
  signed by the executing agent, and the receiver treats an unverifiable resolution as
  absent. An approval is bound to the presented request by `request_payload_hash`.
- **Post-execution review (Actions §3.9).** `required_within_24h` and
  `required_post_execution` now have a protocol mechanism:
  - The executing agent needs a review endpoint, an escalation destination and, for
    `required_post_execution`, the ActionDescriptor's `post_execution_review_period`.
    If one is missing, the request is rejected with code `invalid_request` and the
    diagnostic `obligation_conflict` in `details`, before any effect (§3.9.1).
  - Deadlines run from the execution instant: the `ts` of the terminal result, in the
    asynchronous pattern too. The initial acknowledgment (`status: "accepted"`) never
    opens a review. `required_within_24h` is exactly 24 hours; `required_post_execution`
    adds `post_execution_review_period`; when both apply, both obligations are kept
    (§3.9.2).
  - The review uses `event` messages with payload types
    `arsiaprotocol.oversight/review-pending`, `review-decision` and `review-overdue`
    (§3.9.3). An objection starts the operator's remediation procedure but never
    changes the execution's terminal state or its records (§3.9.4).
  - A deadline reached without a verified decision is recorded as a `review_overdue`
    fact, and the overdue notice is escalated separately (§3.9.4).
- **Assets approvals (Assets §5.2).** A denied or expired transfer approval answers with
  the `error` of Actions §3.4 Path 2 or Path 3. No AssetTransferReceipt is issued for a
  transfer that never executed.

## 15. Effective obligation resolution

- **One resolution procedure (Core §4.3.10).** Compliance obligations are resolved per
  axis (oversight, audit, explainability, retention, residency) from identified
  sources. Profile names are never ranked against each other. The obligation rules
  are published in `profiles/arsia-obligation-rules.json`. In the provenance, a rule
  entry or a profile floor is identified by the SHA-256 of its RFC 8785 form, and an
  identity fact by the agent-id and its identity evidence (§4.3.10.2).
- **Composition (Core §4.3.10.5).**
  - Retention floors are compared by the `retained_until` instant each one produces
    from the same anchor.
  - Residency restrictions are intersected; an empty intersection is a conflict.
  - Oversight is a set of modes.
  - A profile default is not an obligation.
  - With no declaration and no floor, retention is the platform default `P90D`.
- **High-risk requests (Core §4.3.8 Rule 3; §4.3.10.3).** The composed oversight set
  must contain a mode other than `"not_required"`. A declared lower classification
  never lowers obligations, because this specification defines no authorized reduction.
- **Provenance in the audit record (State §7.1).** Covered records carry
  `obligation_resolution`. Their `declared_retention`, `effective_retention`,
  `retention_anchor`, `retention_source` and `retained_until` are derived from it and
  must not diverge from it.
- **Rejections (Core §4.3.10.6).** The wire error code stays `invalid_request`, with
  the specific diagnostic in `details`. Every compliance rejection, for any intent,
  produces an audit record with `rejection_cause: "compliance"`, whatever
  `audit_required` the message declares.
- **Rejection details (Core §4.3.10.6, §11.1; State §5.2, §8.4).** Each diagnostic's
  `details` carry exactly the members its rule defines, with the diagnostic member
  `true`, and may add `localized_description`. `missing_legal_basis` details have no
  `message` member; for a SET they may carry the entry's `pii_classification`. The
  closed details of State §8.4 also accept `localized_description`.
- **Onboarding (Identity §7.2 Step 7).** The gateway prepares the agent's authenticated
  context in Phase 1, CHECK-05 verifies it, and it is bound to the admission. It is
  one of the sources of the resolution.

## 16. Audit hash chain and tombstones

- **Construction (State §7.2).** Each chain value is the lowercase hex SHA-256 of the
  RFC 8785 form of `{"previous_chain_value": P, "record": R'}`. `R'` is the complete
  record, chain context included, without its own `hash_chain`; `P` is the previous
  entry's chain value, or `null` for the first entry. The four chain fields
  (`hash_chain`, `chain_id`, `chain_seq`, `chain_format`) are present together or not
  at all.
- **Conformance (State §7.2; Core §12).** Chaining is REQUIRED at the Compliance and
  Full levels and RECOMMENDED at Core.
- **Chains and queries (State §7.4).** A log may hold several chains. The query
  endpoint retrieves a chain by `chain_id`, ordered by `chain_seq`, with
  `after_chain_seq` as the cursor. A response that contains a tombstone is a chain
  response: every entry carries `chain_id` and `chain_seq`, and `next_cursor` is the
  integer `chain_seq`.
- **Permanent deletion (State §7.2, §7.3).** Only an operator-controlled maintenance
  path, separate from application roles, deletes a chained record. It writes a
  tombstone (`arsia-audit-chain-tombstone.schema.json`) carrying only the chain
  context, the position, the deleted record's chain value and the previous value.
- **Onboarding (Identity CHECK-04).** CHECK-04 requires the chain fields and verifies
  each returned chain.
- **Declared limits (State §7.2).** On its own, the chain does not detect a complete
  rewrite by the log owner, write-time omission or forks. Tail truncation goes
  undetected when the verifier holds no later head. A withheld chain can be noticed
  only against the operator's documented chains or an independently held head of
  that chain. A tombstone attests that a deletion occurred, not that it was
  legitimate.

## 17. What did NOT change

Payload-type versioning semantics (only its default and discovery were fixed);
the six-intent model; JCS/RFC 8785 canonicalization; Ed25519 as primary
algorithm; the 7 standard profiles' names; agent-id grammar; the discovery,
JWKS, inbox endpoints; GRANT semantics (clarified, not changed). The intent enum
stays the same: post-execution review uses `event` messages (§14). PURGE is
**not** unchanged: it now honours stored retention and `retention_override` (§9).
