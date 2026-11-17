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
- Audit records: `compliance_profile` → declared/resolved pair + retention resolution fields + `counterparty_owner_id`; every asset receipt has an audit record; MiFID records immutable (`updated_at` removed); `dora_incident` → `ict_incident` with candidate-based trigger.

### Added
- Core §4.3.9 `authorization`, §6.5 issuer trust, §6.6 agent resolution, §12.4 CORE-COMPLIANCE-04..09; reserved-capability registry additions (`echo`, `health`, `onboarding.evaluate`, `broker.use`); ActionDescriptor `supported_versions`; extension profiles via reverse-domain names; relay-attestation schema; IdentityRecord `regulated_entity`; discovery `iso4217_edition` + `strict_compliance`; subsequent-receipt delivery mechanism; key-revocation event; threat model +6 adversaries; in-repo conformance tooling (`check_consistency.py`, `runtime_harness.py`, `regen_v2.py`, `rtm_counts.py`); 967-vector suite (165 crypto blocks checked: 153 signatures verified, 9 signature negatives) with 209 classified runtime skips and 54 published test keypairs.

### Fixed
- All 8 blocking, 22 high, 31 medium (2 partial-by-repo-state), and 8 low findings of the Draft-01 audit (`docs/auditoria-spec-draft-01.md`), plus 10 newly found defects — resolution evidence in `docs/draft-02-decisions.md`.
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
