<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Changelog

All notable changes to the ARSIA Protocol specification will be
documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to the versioning scheme described in
[VERSIONING.md](VERSIONING.md).

## [Draft-02] — Unreleased

Draft-02 supersedes Draft-01. **Breaking release: wire version 2.0.** Full details:
[migration guide](docs/draft-02-migration-guide.md) ·
[decision records](docs/draft-02-decisions.md) ·
[findings status](docs/draft-02-findings-status.md) ·
[known limitations](docs/draft-02-known-limitations.md).

### Breaking
- Signing input now covers the envelope minus only `security.sig` (protects `alg`/`kid`/encryption metadata/`authorization`); staged verification pipeline; no v1 fallback (Core §5.1-§5.2).
- Wire version `2.0`; media type `v=2`; schemas validate exactly the 2.0 minor; explicit version-handling model (Core §4.1.1).
- New required-with-correlation envelope field `root_request_id`; `correlation_id` normatively = immediately preceding message (Core §2.2/§4.2).
- `retention_days` → `retention` (ISO 8601 calendar durations); below-floor declarations rejected for all floored profiles — no clamping; calendar arithmetic with end-of-month rule; EU-AI-ACT-HIGH-RISK floor is `P6M` (calendar), DSA-VLOP `P1096D` (Core §4.3.6.4/§4.3.8 R4, State §6).
- Asset amounts become canonical decimal strings with fixed ISO 4217 scale (JPY/EUR/KWD expressible); float `multipleOf` removed; no negative amounts.
- Brokered routing replaced by an executable dual-authorization model with signed relay attestations and envelope↔token hash binding; recipients reject residency-constrained messages without attestation; `BrokerRelayAuditRecord` retired (Routing §1.2.2/§2.3/§7.4).
- Canonical oversight contract only (`payload.args`; `approved|denied`/`denied|expired`); Assets-specific approval shape removed; onboarding decisions no longer reuse `approval_decision`.
- Signed `idempotency.key` overrides the transport header (replay-defence fix); per-message classification drops `unacceptable-risk`; content-field exclusivity is a hard reject; residency codes closed to ISO + `EU`.
- State SET (Issue #2): a `payload.args.data_residency` must lie within the residency restriction composed for the message (a subset of it), otherwise `invalid_request` with `obligation_conflict` on the `residency` axis; precedence no longer widens the envelope's zone (State §8.3; Core §4.3.10.5).
- State SET (Issue #2): the retention of an entry is fixed when its generation is created; an update that states another retention, or that falls under a higher floor, is rejected with `invalid_request` and `retention_fixed` details, and an update does not restart the period (State §2.1.8, §3.1.2 rule 7, §8.4).
- SNAPSHOT `hash` (Issue #2) is now defined: `"sha-256:"` + lowercase hex SHA-256 over the RFC 8785 form of `{as_of, entries}` as carried, in the order carried; the schema enforces the format (State §3.2.1).
- Relay attestation (Issue #2): `residency_zone` is the value of the message's `compliance.data_residency`, set unchanged by the broker; the recipient rejects with `unauthorized`, at step 3, an attestation whose zone is not equal to it as a string, with no containment in either direction (Routing §7.4.1).
- Asset and incident audit records (Issue #2): every `asset_transfer` record carries `payment_reference`, the reference of the transfer it belongs to. A reversal record (`event_type` `asset_transfer` with `payload_type` `arsiaprotocol.assets/transfer-reversal`) carries the original transfer's `payment_reference` and, in `original_audit_id`, the `record_id` of the original record; the reversal receipt keeps its new reference. An `ict_incident` record carries the incident event's `payload.data` fields with the same values (six required, `resolved_at` as in the event) (Assets §3.3.2, §6.2.3; State §7.1).
- Compliance rejection details: the `details` of the seven Core §4.3.10.6 diagnostics are closed objects carrying exactly the members their rule defines (`arsia-message.schema.json` `error-details-<diagnostic>`, applied to `invalid_request` when the diagnostic member is present, which must be `true`). State §5.2's `missing_legal_basis` details carry the indicator and an optional `pii_classification`, with no `message` member: the explanation is `payload.error.description` (Core §4.3.10.6, §11.1; State §5.2).
- Escrow audit records: each record documents the message of its transition — `payload_type` `arsiaprotocol.assets/transfer-request` on creation and on timeout (a timeout record documents the request that created the escrow), the `release_trigger` on release, `arsiaprotocol.assets/escrow-dispute` and `arsiaprotocol.assets/escrow-cancel`; `from_agent`/`to_agent` are the envelope agents, and the creation record adds REQUIRED `payer_agent`/`payee_agent`; an `escrow_returned` record carries exactly one of `actual_timeout` and `cancellation_reason` (Assets §4.3, State §7.1).
- State SET at the envelope: a SET of a `sensitive` entry that declares a legal basis declares an Art. 9(2) ground, and `pii_special_categories` is present exactly when the entry is `sensitive`; the message, `set-args` and state-entry schemas enforce both (Core §4.3.8 Rule 8, State §2.1.11).
- Audit query responses: a response that contains a tombstone is a chain response — every entry MUST carry `chain_id` and `chain_seq`, and `next_cursor`, when present, MUST be an integer `chain_seq`; matching the query parameters stays a runtime obligation (State §7.4).
- Audit records: `compliance_profile` → declared/resolved pair + retention resolution fields + `counterparty_owner_id`; every asset receipt has an audit record; MiFID records immutable (`updated_at` removed); `dora_incident` → `ict_incident` with candidate-based trigger.
- Approval expiry audit records: the `approval_expired` record documents the `pending_approval` whose deadline was reached — its `message_id`, `timestamp`, `from_agent`, `to_agent`, `intent`, `payload_type` and `payload_hash`, `correlation_id` the pending's `id`, processed no earlier than the `approval_deadline`; `timestamp` is REQUIRED and the schema fixes `intent` `pending_approval` and `payload_type` `arsiaprotocol.oversight/pending` (Actions §3.5; State §7.1).
- Idempotency (Core §10.2, §10.3): the receiver reserves the envelope's `idempotency.key` atomically before any effect and keeps the association at least until the latest of `idempotency.expires_at`, the end of the message's acceptance window (`expires_at` plus the clock skew tolerance; for a message without `expires_at`, for as long as the server would accept it) and the determined outcome of the operation; the terminal response is stored, success or error; a reservation is released for retry only when the attempt has ended, the server has established that no effect occurred, no execution remains pending and the attempt produced no response or an error response, never after an effect; for an encrypted payload the scope uses the `type` of the decrypted payload, taken after the decryption procedure of §5.3 has succeeded; a duplicate of a reservation without a stored response is rejected with `conflict` (MUST, formerly SHOULD); a rejected message returns no stored response and releases nothing.
- DPoP (Identity §3.3, §7.7, §9.2; Core §6.3): whether a proof is required follows from the token's binding (`cnf.jkt`), not from the presented scheme — a DPoP-bound token presented as Bearer or without a `DPoP` header is rejected with `unauthorized` ([RFC 9449] §7.2), as are a malformed `cnf` and a token without `cnf.jkt` under the `DPoP` scheme; Identity §7.7 no longer requires Bearer presentation nor leaves the verification as a SHOULD.
- Encrypted payloads (Core §5.3): after decryption the plaintext is parsed strictly and the decrypted view — the envelope with the decrypted `payload` and `security.encrypted` taken as `false` — satisfies every requirement of an unencrypted message; a failed decryption is `unauthorized`, an invalid plaintext `invalid_request`; the signature is verified over the received envelope only.

- Timestamps (Core §4.1.3; every `rfc3339-ms-utc` field): the pattern limits the month (01–12), day (01–31), hour (00–23), minute and second (00–59), and the value MUST be a real calendar instant — the day exists in that month of that year. ARSIA profile: no year `0000` and no second `60`. The `$def` carries `format: date-time` for the calendar rule.
- Scope (Core §6.1, §6.4; `arsia-jwt-claims.schema.json`): `scope` follows RFC 6749 §3.3 in the token claims, the token request and the token response — tokens of visible ASCII characters other than `"` and `\`, separated by exactly one space, no leading or trailing space; a token whose `scope` does not conform is rejected with `unauthorized` before the value is split, and other white space is never normalised into separators.
- Nesting depth (Core §5.2 step 2): a recipient MAY limit the nesting depth of the documents it parses and MUST reject the excess with `invalid_request` in step 2; the limit MUST NOT be lower than 32 levels (each open object or array one level, the root container level 1).
- Escrow disputes (Assets §4.2.3, §4.3.4): after it accepts a dispute, the `arbitration_agent` MUST notify the escrow holder with a signed `arsiaprotocol.assets/escrow-dispute` request; the escrow becomes `DISPUTED` when the holder has verified that notification, with effect from the instant the holder received it. The holder processes it through Core §5.2 and then checks, in order, the escrow (`not_found`), the sender (`forbidden`), and the party, state and deadline (`invalid_request`). The `escrow_disputed` record documents the notification: its `from_agent` is the arbitration agent.
- Escrow timeout and order of events (Assets §4.2, §4.2.1, §4.2.2): while an escrow is `ESCROWED`, a release, cancellation or dispute notification received strictly before `timeout_at` precedes the timeout however long its verification takes, and one received at or after it is late; the release check uses the instant of reception. The return on timeout is an operation of the holder with its provider, not an AssetTransferReversal; it is started by one decision that evaluates its conditions again, takes effect at most once, and the `failed` receipt is issued only after the provider has confirmed it. The release is bound the same way (§4.2.1): the holder MUST reserve it as the escrow's financial operation before instructing the provider and reconcile that same operation while its outcome is uncertain; a retry, cancellation or timeout MUST NOT cause a second financial effect; the `completed` receipt is issued only after the provider confirms the release. A return starts only when no financial operation is reserved for the escrow.
- QUERY order (State §3.1.4): results are ordered by `created_at` and, at equal `created_at`, by `key` in ascending order of its ASCII bytes (case-sensitive); `total` and `entries` are computed over the same authorised, filtered set, ordered before `offset` and `limit` apply. Pages of successive requests are consistent only while that set does not change; SNAPSHOT with `as_of` gives a reading at one instant.

### Added
- Core §4.3.9 `authorization`, §6.5 issuer trust, §6.6 agent resolution, §12.4 CORE-COMPLIANCE-04..09; reserved-capability registry additions (`echo`, `health`, `onboarding.evaluate`, `broker.use`); ActionDescriptor `supported_versions`; extension profiles via reverse-domain names; relay-attestation schema; IdentityRecord `regulated_entity`; discovery `iso4217_edition` + `strict_compliance`; subsequent-receipt delivery mechanism; key-revocation event; threat model +6 adversaries; in-repo conformance tooling (`check_consistency.py`, `runtime_harness.py`, `regen_v2.py`, `rtm_counts.py`); 987-vector suite (168 crypto blocks checked: 156 signatures verified, 9 signature negatives) with 211 classified runtime skips and 54 published test keypairs.

### Changed
- Core §11.1: `details.localized_description` is accepted in every `details` object,
  including those whose members are otherwise fixed (Core §4.3.10.6; State §8.4).
- Assets §6.2.2 (Issue #2): `resolved_at` of the ICT incident event is typed "string or
  null" in the prose, as the schema and the §6.2.5 example already allowed; absent or
  `null` means the incident is ongoing.
- Routing §2.3.3 (Issue #2): `relay_id` and `attestation_id` are stated as distinct
  identifiers; no equality, inequality or mapping between them is required, and a
  consumer MUST NOT assume they are equal.
- Core §4.2.1, §2.2: `correlation_id` names the message a reply directly answers — its causal parent, not the message most recently exchanged. Rules 1–3 apply to delivered messages of the reply intents; a reply takes effect only as a transition its flow permits. A `pending_approval` and the terminal result, an `accepted` acknowledgement and the terminal result, and the decisions of distinct approvers legitimately share a parent; a redelivery, a second terminal result and a second decision of an admitted approver do not take effect. Reading the persisted terminal result again is not a delivery. An `event` with a `correlation_id` follows the section that defines it.
- State §10.2: a key is a logical identifier, not a path — `.` and `..` are ordinary segments. A backend that maps keys to a hierarchical namespace MUST treat every segment as data, MUST keep each operation confined to the storage space authorised for it and MUST map different keys to different stored objects. The key grammar is unchanged.
- Identity §7.8 (informative example): the gateway of the auditor example verifies the trust level and, separately, that the certified identity is the admitted authority's, before the policy is evaluated; `conditions` describes that configuration and restricts nothing.

### Fixed
- All 8 blocking, 22 high, 31 medium (2 partial-by-repo-state), and 8 low findings of the Draft-01 audit (`docs/auditoria-spec-draft-01.md`), plus 10 newly found defects — resolution evidence in `docs/draft-02-decisions.md`.
- Encrypted errors: `arsia-message.schema.json` required an object `payload` of every `intent: error` message and a string `payload` of every encrypted one, so an encrypted error was impossible; the error object is now required of an unencrypted error, and of the decrypted view of an encrypted one (Core §5.3).
- Core §5.3.1 dispute resolution and the audit-record schema description no longer present audit records as individually signed, matching hashes as proof of receipt, or records as exempt from GDPR Art. 17 (ARSIA-State.md §7.2); SECURITY.md is reviewed against Draft-02 (signing profile, twelve adversaries, idempotency retention, DPoP binding, audit chain scope, residency limits, `compliance.retention`).
- Test vectors: no vector uses an `arsiaprotocol.*` payload type that the specification does not define, apart from three declared negatives of the type itself, the declared plaintext of the encrypted negative INV-251 and two types the specification names only in examples (`arsiaprotocol.compliance/check`, `arsiaprotocol.onboarding/ping`; an open finding); application payloads use non-reserved types, and error responses carry the type of the original request (Core §11.1).
- Pattern dialect (Core §2.3): patterns are ECMA-262 regular expressions — `$` matches only the end of the value, digits are ASCII and written `[0-9]` in every schema and specification pattern. The validation tools matched patterns with Python's defaults, under which `"2.0\n"` selected the compatibility procedure of a newer minor and an `id` or `from` followed by a line feed passed; they now apply the stated semantics, also for a schema reached through `$ref`.
- Strict parser of the tools: a document nested beyond the limit is rejected in step 2 before it is parsed (1100 nested arrays raised an interpreter error), and the interpreter-wide integer digit limit is no longer changed during a parse.
- Assets §4.2.2 no longer calls the return of an escrow timeout an AssetTransferReversal, which §3.3.1 allows only for a completed transfer; State §10.2 no longer says that the key character set prevents directory traversal (dots and slashes are allowed); State §3.1.4 no longer claims deterministic pagination from an ordering by `created_at` alone.
- Findings of the Draft-02 remediation cycles, registered and closed in `docs/draft-02-remediation-ledger.md`.
- Draft-01.1 errata ([Draft-01.1] below) reconciled into Draft-02: its test-vector and keypair corrections are carried into the Draft-02 corpus (including the second defects of ITV-201, ITV-266, ITV-423 and ITV-482), the Core table-of-contents link to §10.4 and the §4.4.1 errata note's example locations are taken over, and each correction Draft-02 had already resolved, resolves differently or does not need is recorded in the remediation ledger.

## [Draft-01.1] — 2026-09-29

Errata to Draft-01: corrections to published artefacts and documentation.
Specification version labels and the Core §4.4.1 errata label were updated; the
errata note's example locations and the Core table-of-contents link to §10.4
were corrected; no normative text changed, and the wire version (`1.0`) is
unchanged.

### Fixed

- Test vectors: every signature in a valid vector verifies with a published key;
  in invalid vectors, a signature fails to verify only where the signature, key,
  `kid` or `alg` is the object of the test.
- Test vectors: every vector marked valid is now valid by the schema, except
  three version-compatibility vectors (ITV-406, ITV-438, ITV-439) that test
  tolerance of unknown fields.
- Test vectors: INV-25 and ITV-401 no longer carry a second, unintended defect
  besides the one they test.
- Test vectors: ITV-498 and ITV-518, whose `expires_at` is earlier than `ts`, are
  now invalid runtime-only vectors (`invalid_request`, Core §4.2.2); CTV-03 is now
  a conforming AssetTransferRequest (Assets §3.1).
- Test vectors: invalid vectors that also lacked `security` (ITV-201, ITV-266,
  ITV-409 to ITV-414, ITV-416, ITV-418, ITV-422 to ITV-424, ITV-477, INV-20,
  INV-22), `capabilities` (ITV-402) or a UUID v4 `id` (ITV-550) now carry only
  the defect they test.
- Test vectors: ITV-448 and ITV-450, a token `iat` or `nbf` in the future, are
  now expected invalid, as their descriptions and Identity §3.2 state; ITV-449's
  skip reason no longer claims that the schema rejects `nbf`.
- Test vectors: ITV-546 is now a valid vector: a `ts` 90 seconds in the past is
  within the EU-AI-ACT-HIGH-RISK profile's 120-second clock skew tolerance
  (Core §8.3).
- Test vectors: INV-21 is now a signed runtime-only vector, like INV-20 and
  INV-22; its description no longer claims a schema conditional (State §2.1.10,
  §2.1.11).
- Test keypairs: 57 published (53 Ed25519, 2 ES256, 2 RS256), keyed by agent-id,
  or by full `kid` when an agent publishes more than one key.
- Published counts: test-vector counts (413 valid, 123 invalid, 75 runtime-only)
  in the README, security model, getting-started guide, FAQ and test-vector
  README; the Draft-01 entry below states the Draft-01 corpus as the tools
  report it (415 valid, 125 invalid, 73 runtime-only); the `--check-crypto`
  coverage statement; the RTM row count (1,903 requirement rows; the earlier
  2,086 counted every table line).
- RTM coverage-gap tables: every figure is recomputed from the requirement rows
  of the Core, Identity, Actions, State and Assets RTMs; the Assets gap list now
  includes ASSETS-§4.2.3-03 and ASSETS-§4.2.3-04.
- Links: the security-model links in the README and the getting-started guide,
  and the test-vector and RTM links in the security model.
- Documentation: the profiles README names the current release; the
  getting-started guide states what the validation script checks; the security
  model's data-protection count; the README's oversight and data-residency
  links; the test-vector README's verification snippets; the Draft-01 entry's
  oversight attribution; the getting-started guide's cookbook recipe count;
  where the test-vector README's Python snippets run.

### Changed

- VERSIONING.md: errata may also correct published artefacts (test vectors,
  keypairs, documentation) without changing the wire version; test vectors carry
  a Semantic Versioning `version` field (the test-vector file is now 1.0.1);
  schemas are no longer listed among the files with a `version` field; errata
  retrocompatibility applies to the specification text.
- README version badge shows the current release, Draft-01.1.

### Removed

- Test vector ITV-545: its invalid outcome rests on a MAY (Core §8.3: a message
  whose `ts` exceeds the clock skew tolerance "MAY be rejected"), which the
  test-vector format cannot declare. Its ID is not reused.
- Test vector ITV-482: Draft-01 gives an onboarding `approval_decision` two
  incompatible `capabilities` values (Actions §3.3 requires
  `arsiaprotocol.oversight.approve`; Identity §7.6 specifies
  `arsiaprotocol.onboarding.evaluate`), and resolving this needs a wire change
  that an erratum cannot make. Its ID is not reused.

## [Draft-01] — 2026-04-01

Initial public release of the ARSIA Protocol specification.

### Specification Documents

- **ARSIA-Core** — Core envelope structure, message security (Ed25519,
  JCS, JWE), authorization (JWT, DPoP), compliance profiles and human
  oversight modes, transport bindings, discovery, conformance levels, and
  security considerations.
- **ARSIA-Identity** — Agent identity, key management (JWKS), signature
  verification, identity records, certificates, and onboarding.
- **ARSIA-Actions** — Action execution, pre-execution human oversight,
  risk classification, and action lifecycle.
- **ARSIA-Routing** — Topology selection, broker-assisted routing, data
  residency, delivery lifecycle, rate limiting, and priority resolution.
- **ARSIA-State** — State operations (set, get, delete), GDPR data
  operations (purge, grant, revoke), audit trail, retention policies,
  and breach notification.
- **ARSIA-Assets** — Asset transfers, escrow lifecycle, reversal,
  MiFID II audit, SCA compliance, DORA incident reporting, and
  idempotency.

### Artifacts

- 31 JSON Schemas (Draft 2020-12)
- 613 test vectors (415 valid, 125 invalid, 73 runtime-only)
- 7 compliance profiles: GDPR-STANDARD, EU-AI-ACT-HIGH-RISK,
  EU-AI-ACT-LIMITED-RISK, MIFID-II, PAC-AGRICULTURE, DSA-VLOP, DORA
- 6 Requirements Traceability Matrices (RTMs)
- Reference keypairs for test vector validation

### Documentation

- Getting started guide
- Security model summary
- FAQ (39 questions)
- RTM format documentation

### Governance

- Tri-licensing: CC BY-SA 4.0 (spec), Apache 2.0 (artifacts), BSL 1.1 (code)
- Contributor License Agreement (CLA)
- Contributing guidelines
- Versioning policy

---

_ARSIA Protocol ([arsiaprotocol.org](https://arsiaprotocol.org)) | by [Arsia Labs (Arsia Tecnologia Unipessoal Lda)](https://arsialabs.ai)_
