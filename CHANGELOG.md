<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Changelog

All notable changes to the ARSIA Protocol specification will be
documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to the versioning scheme described in
[VERSIONING.md](VERSIONING.md).

## [Draft-01.1] — 2026-09-29

Errata to Draft-01: corrections to published artefacts and documentation. The
specification text and the wire version (`1.0`) are unchanged.

### Fixed

- Test vectors: every signature in a valid vector verifies with a published key;
  in invalid vectors, a signature fails to verify only where the signature, key,
  `kid` or `alg` is the object of the test.
- Test vectors: every vector marked valid is now valid by the schema, except
  three version-compatibility vectors (ITV-406, ITV-438, ITV-439) that test
  tolerance of unknown fields.
- Test vectors: INV-25 and ITV-401 no longer carry a second, unintended defect
  besides the one they test.
- Test keypairs: 55 published (51 Ed25519, 2 ES256, 2 RS256), keyed by agent-id,
  or by full `kid` when an agent publishes more than one key.
- Published counts: test-vector counts (415 valid, 125 invalid, 73 runtime-only)
  in the README, security model, getting-started guide, test-vector README and
  the Draft-01 entry below; the `--check-crypto` coverage statement; the RTM
  row count (1,994 requirement rows; the earlier 2,086 counted every table line).
- Links: the security-model links in the README and the getting-started guide,
  and the test-vector and RTM links in the security model.

### Changed

- VERSIONING.md: errata may also correct published artefacts (test vectors,
  keypairs, documentation) without changing the wire version; test vectors carry
  a Semantic Versioning `version` field (the test-vector file is now 1.0.1).
- README version badge shows the current release, Draft-01.1.

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
