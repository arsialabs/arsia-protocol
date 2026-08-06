<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Changelog

All notable changes to the ARSIA Protocol specification will be
documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to the versioning scheme described in
[VERSIONING.md](VERSIONING.md).

## [Draft-02] — 2026-07-22

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
- Audit records: `compliance_profile` → declared/resolved pair + retention resolution fields + `counterparty_owner_id`; every asset receipt has an audit record; MiFID records immutable (`updated_at` removed); `dora_incident` → `ict_incident` with candidate-based trigger.

### Added
- Core §4.3.9 `authorization`, §6.5 issuer trust, §6.6 agent resolution, §12.4 CORE-COMPLIANCE-04..09; reserved-capability registry additions (`echo`, `health`, `onboarding.evaluate`, `broker.use`); ActionDescriptor `supported_versions`; extension profiles via reverse-domain names; relay-attestation schema; IdentityRecord `regulated_entity`; discovery `iso4217_edition` + `strict_compliance`; subsequent-receipt delivery mechanism; key-revocation event; threat model +6 adversaries; in-repo conformance tooling (`check_consistency.py`, `runtime_harness.py`, `regen_v2.py`, `rtm_counts.py`); 649-vector suite (83 crypto-verified) with 94 classified runtime skips.

### Fixed
- All 8 blocking, 22 high, 31 medium (2 partial-by-repo-state), and 8 low findings of the Draft-01 audit (`docs/auditoria-spec-draft-01.md`), plus 10 newly found defects — resolution evidence in `docs/draft-02-decisions.md`.

## [Draft-01] — 2026-04-01

Initial public release of the ARSIA Protocol specification.

### Specification Documents

- **ARSIA-Core** — Core envelope structure, message security (Ed25519,
  JCS, JWE), authorization (JWT, DPoP), compliance profiles, transport
  bindings, discovery, conformance levels, and security considerations.
- **ARSIA-Identity** — Agent identity, key management (JWKS), signature
  verification, identity records, certificates, and onboarding.
- **ARSIA-Actions** — Action execution, human oversight (pre-execution
  and post-execution), risk classification, and action lifecycle.
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
- 613 test vectors (514 valid, 99 invalid)
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
