<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Changelog

All notable changes to the ARSIA Protocol specification will be
documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to the versioning scheme described in
[VERSIONING.md](VERSIONING.md).

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
- Test keypairs: 57 published (53 Ed25519, 2 ES256, 2 RS256), keyed by agent-id,
  or by full `kid` when an agent publishes more than one key.
- Published counts: test-vector counts (413 valid, 124 invalid, 74 runtime-only)
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
  oversight attribution.

### Changed

- VERSIONING.md: errata may also correct published artefacts (test vectors,
  keypairs, documentation) without changing the wire version; test vectors carry
  a Semantic Versioning `version` field (the test-vector file is now 1.0.1).
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
