<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# ARSIA Protocol

**EU regulatory compliance as a protocol primitive for AI agents.**

[![Spec License](https://img.shields.io/badge/spec-CC%20BY--SA%204.0-brightgreen.svg)](licenses/LICENSE-SPEC.md)
[![Artifacts License](https://img.shields.io/badge/artifacts-Apache%202.0-green.svg)](licenses/LICENSE-ARTIFACTS.md)
[![Code License](https://img.shields.io/badge/code-BSL%201.1-blue.svg)](licenses/LICENSE-CODE.md)
[![Version](https://img.shields.io/badge/version-Draft--01-orange.svg)](CHANGELOG.md)
[![Status](https://img.shields.io/badge/status-draft-yellow.svg)](spec/ARSIA-Core.md)

---

AI agents are being deployed across finance, agriculture, healthcare, and government — negotiating contracts, processing claims, and making decisions that affect real people. But no existing agent protocol handles EU regulatory compliance at the wire level.

ARSIA Protocol embeds compliance into the message envelope — the same way TLS moved encryption to the transport layer. Every message carries identity, audit obligations, data residency, human oversight mode, and regulatory basis as first-class fields. The protocol sits above [MCP](https://modelcontextprotocol.io/) and [A2A](https://google.github.io/A2A/) as a compliance layer — it doesn't replace them, it makes them audit-ready.

```json
{
  "v": "1.0",
  "from": "agent:acme.risk-assessor",
  "to": "agent:acme.compliance-checker",
  "intent": "request",
  "compliance": {
    "profile": "MIFID-II",
    "retention_days": 1827,
    "data_residency": "EU",
    "human_oversight": "required_before_execution",
    "audit_required": true,
    "pii_involved": true,
    "legal_basis": "contract"
  },
  "security": {
    "alg": "EdDSA",
    "kid": "agent:acme.risk-assessor#key-1",
    "sig": "..."
  }
}
```

## Quick Start by Role

### For Developers

**New here?** Start with the [Getting Started guide](docs/getting-started.md) — zero to a validated, signed message in 15 minutes. Then explore the [specifications table](#specifications) below for the full protocol design. Validate your implementation against [31 JSON Schemas](schemas/) (Draft 2020-12) and [613 test vectors](test-vectors/) — including real Ed25519, ES256, and RS256 cryptography. Use the [validation scripts](scripts/) to check envelopes and crypto locally.

ARSIA defines three [conformance levels](spec/ARSIA-Core.md#12-conformance-levels) — pick the one that fits your deployment:

| Level | Name | What it covers |
|-------|------|----------------|
| 1 | **Core** | Message envelope, EdDSA signing, discovery, direct routing |
| 2 | **Compliance** | Core + compliance profiles, audit trail, human oversight |
| 3 | **Full** | Compliance + all five primitives, WebSocket, payload encryption |

**Python SDK:** `pip install arsia-protocol` — [arsialabs/arsia-protocol-sdk](https://github.com/arsialabs/arsia-protocol-sdk)

### For Compliance Officers

Start with the [7 compliance profiles](profiles/) that map EU regulation directly to protocol fields — see the [profiles table](#compliance-profiles) below. The [FAQ](docs/FAQ.md) covers common compliance questions, including profile selection, retention semantics, and audit requirements.

Key protocol sections for regulatory review: human oversight workflow ([Actions §3](spec/ARSIA-Actions.md#3-human-oversight)), audit trail requirements ([State §7](spec/ARSIA-State.md#7-audit-trail)), and data residency enforcement ([Routing §2](spec/ARSIA-Routing.md#2-data-residency)). For a deeper understanding, read the full spec sections on oversight, audit, and data residency.

### For Regulators

Six [Requirements Traceability Matrices](docs/rtm/) (2,086 rows) trace every MUST, SHOULD, and MAY in the specification to the corresponding JSON Schema and test vector. [Core §12](spec/ARSIA-Core.md#12-conformance-levels) defines three conformance levels; [Core §13](spec/ARSIA-Core.md#13-security-considerations) covers the threat model and security considerations.

All specifications follow [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) / [BCP 14](https://www.rfc-editor.org/info/bcp14) normative language. The [613 test vectors](test-vectors/) provide machine-verifiable conformance validation with real cryptographic operations. The [Security Model](docs/security.md) provides a standalone summary of the threat model, cryptographic foundation, authorization, and data protection — designed for evaluation without reading the full spec suite.

---

## Specifications

The protocol follows a **5+1 architecture**: one foundational spec — Core — and five domain primitives that spell the name.

| Spec                                         | Domain       | Description                                                                            |
| -------------------------------------------- | ------------ | -------------------------------------------------------------------------------------- |
| **[ARSIA-Core](spec/ARSIA-Core.md)**         | Foundation   | Message envelope, EdDSA signing, discovery, authorization, compliance field, transport |
| **[ARSIA-Actions](spec/ARSIA-Actions.md)**   | **A**ctions  | Capabilities, human oversight, explainability, action registry                         |
| **[ARSIA-Routing](spec/ARSIA-Routing.md)**   | **R**outing  | Message routing, broker topology, data residency enforcement                           |
| **[ARSIA-State](spec/ARSIA-State.md)**       | **S**tate    | State lifecycle, GDPR obligations, compliance profiles, audit trail                    |
| **[ARSIA-Identity](spec/ARSIA-Identity.md)** | **I**dentity | Agent identity, certificates, trust levels, 6-phase onboarding                         |
| **[ARSIA-Assets](spec/ARSIA-Assets.md)**     | **A**ssets   | Transaction validation, escrow, MiFID II / DORA / PSD2 controls                        |

## Compliance Profiles

Seven normative profiles map EU regulation directly to protocol fields:

| Profile                  | Regulation                      | Retention           | Human Oversight           | Audit    |
| ------------------------ | ------------------------------- | ------------------- | ------------------------- | -------- |
| `GDPR-STANDARD`          | GDPR Art. 5, 6                  | Per operator        | Not required              | Optional |
| `EU-AI-ACT-HIGH-RISK`    | EU AI Act Art. 13, 14, 17, 26   | 180 days            | Required before execution | Required |
| `EU-AI-ACT-LIMITED-RISK` | EU AI Act Art. 50               | 90 days             | Not required              | Required |
| `MIFID-II`               | MiFID II Art. 16(7), DORA, PSD2 | 1827 days (5 years) | Required before execution | Required |
| `PAC-AGRICULTURE`        | CAP Reg. 2021/2116              | 1096 days (3 years) | Required post-execution   | Required |
| `DSA-VLOP`               | DSA Art. 15, 34, 37, 40, 42     | 730 days (2 years)  | Required within 24h       | Required |
| `DORA`                   | DORA Art. 5, 17, 19, 28         | 1827 days (5 years) | Required within 24h       | Required |

Source: [arsia-compliance-profiles.json](profiles/arsia-compliance-profiles.json) — defined normatively in [ARSIA-State §6](spec/ARSIA-State.md).

## Artifacts

The protocol is fully machine-verifiable:

| Directory | Content |
|-----------|---------|
| [`spec/`](spec/) | 6 specification documents |
| [`schemas/`](schemas/) | 31 JSON Schemas (Draft 2020-12) |
| [`profiles/`](profiles/) | 7 compliance profiles |
| [`test-vectors/`](test-vectors/) | 613 test vectors (514 valid, 99 invalid, 73 runtime-only) |
| [`docs/rtm/`](docs/rtm/) | 6 Requirements Traceability Matrices (2,086 rows) |
| [`scripts/`](scripts/) | Validation tools |

9 test keypairs are published in [`keypairs.json`](test-vectors/keypairs.json) with real Ed25519, ES256, and RS256 cryptography.

- [`docs/FAQ.md`](docs/FAQ.md) — Frequently Asked Questions: design rationale and decision explanations

## Ecosystem

ARSIA Protocol is not a competitor to MCP or A2A — it's a complement.

```
┌─────────────────────────────────────────────────┐
│  Your Application                               │
├─────────────────────────────────────────────────┤
│  ARSIA Protocol — compliance, identity, audit   │
├─────────────────────────────────────────────────┤
│  A2A — agent-to-agent communication             │
├─────────────────────────────────────────────────┤
│  MCP — tool & data access                       │
├─────────────────────────────────────────────────┤
│  Infrastructure — LLMs, cloud, databases        │
└─────────────────────────────────────────────────┘
```

## Contributing

The specification is in draft. We welcome contributions — see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines and [CLA.md](CLA.md) for the Contributor License Agreement. Feedback via [GitHub Issues](https://github.com/arsialabs/arsia-protocol/issues).

## License

ARSIA Protocol uses different licenses for different types of materials.

Human-readable specification and documentation materials are licensed under
the Creative Commons Attribution-ShareAlike 4.0 International License
(CC BY-SA 4.0). See [LICENSE-SPEC.md](licenses/LICENSE-SPEC.md).

Machine-readable interoperability artifacts, including schemas, profiles,
and test vectors, are licensed under the Apache License 2.0. See
[LICENSE-ARTIFACTS.md](licenses/LICENSE-ARTIFACTS.md).

Software components, including SDKs, reference implementations, scripts,
tools, CI/CD workflows, automation code, and `.github/workflows/validate-vectors.yml`,
are licensed under the Business Source License 1.1. Production use is
permitted except for competitive offerings, as described in
[LICENSE-CODE.md](licenses/LICENSE-CODE.md). Each version converts to the Mozilla
Public License Version 2.0 (MPL-2.0) four years after release.

See [LICENSE.md](LICENSE.md) for an overview and [LICENSING-FAQ.md](licenses/LICENSING-FAQ.md)
for practical examples.

---

ARSIA Protocol ([arsiaprotocol.org](https://arsiaprotocol.org)) | by [Arsia Labs](https://arsialabs.ai)
