<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
# Compliance Profiles

This directory contains the ARSIA Protocol compliance profiles registry.

## Files

| File | Description |
|------|-------------|
| `arsia-compliance-profiles.json` | All 7 compliance profiles with defaults and regulatory references |
| `arsia-obligation-rules.json` | Declarative requirement rules (scope, trigger, requirements, exceptions) interpreted by the effective obligation resolution of ARSIA-Core.md §4.3.10; validated by `arsia-obligation-rules.schema.json` |

## Profiles

All profiles are **active** in the current specification (Draft-02).

| Profile | Regulation | Retention | Description |
|---------|------------|-----------|-------------|
| `GDPR-STANDARD` | GDPR Art. 5, 6 | None (no floor; per operator) | Baseline — default when no profile is declared |
| `EU-AI-ACT-HIGH-RISK` | EU AI Act Annex III | `P6M` (six calendar months) | High-risk AI systems per Art. 13, 14, 17, 26 |
| `EU-AI-ACT-LIMITED-RISK` | EU AI Act Art. 50 | `P90D` (conservative policy) | Limited-risk AI systems — transparency obligations |
| `MIFID-II` | MiFIR Art. 25(1); MiFID II Art. 16(7) (profile floor, ARSIA-State §6.3) | `P1827D` (profile floor) | Agent-assisted financial services |
| `PAC-AGRICULTURE` | CAP Reg. 2021/2116 | `P1096D` | EU Common Agricultural Policy compliance |
| `DSA-VLOP` | DSA Art. 15, 34, 37, 40, 42 | `P1096D` (profile floor) | Digital Services Act for Very Large Online Platforms |
| `DORA` | DORA Art. 5, 17, 19, 28 | `P1827D` (conservative policy) | Digital Operational Resilience Act |

Profiles are defined normatively in [ARSIA-State §6](../spec/ARSIA-State.md). The Retention column is each profile's `defaults.retention_minimum` in [arsia-compliance-profiles.json](arsia-compliance-profiles.json): `P6M` is applied with calendar arithmetic, the others are day counts (ARSIA-Core §4.3.6.4.1); the day counts account for leap years in the worst case.

## Schema

The profiles registry is validated by [`arsia-compliance-profiles.schema.json`](../schemas/arsia-compliance-profiles.schema.json).
