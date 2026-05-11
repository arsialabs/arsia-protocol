<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
# Compliance Profiles

This directory contains the ARSIA Protocol compliance profiles registry.

## Files

| File | Description |
|------|-------------|
| `arsia-compliance-profiles.json` | All 7 compliance profiles with defaults and regulatory references |

## Profiles

All profiles are **active** in the current specification (Draft-02).

| Profile | Regulation | Retention | Description |
|---------|------------|-----------|-------------|
| `GDPR-STANDARD` | GDPR Art. 5, 6 | None (per operator) | Baseline — default when no profile is declared |
| `EU-AI-ACT-HIGH-RISK` | EU AI Act Annex III | 180 days | High-risk AI systems per Art. 13, 14, 17, 26 |
| `EU-AI-ACT-LIMITED-RISK` | EU AI Act Art. 50 | 90 days | Limited-risk AI systems — transparency obligations |
| `MIFID-II` | MiFID II Art. 16(7) | 1827 days | Agent-assisted financial services |
| `PAC-AGRICULTURE` | CAP Reg. 2021/2116 | 1096 days | EU Common Agricultural Policy compliance |
| `DSA-VLOP` | DSA Art. 15, 34, 37, 40, 42 | 730 days | Digital Services Act for Very Large Online Platforms |
| `DORA` | DORA Art. 5, 17, 19, 28 | 1827 days | Digital Operational Resilience Act |

Profiles are defined normatively in [ARSIA-State §6](../spec/ARSIA-State.md). Retention values account for leap years in the worst case.

## Schema

The profiles registry is validated by [`arsia-compliance-profiles.schema.json`](../schemas/arsia-compliance-profiles.schema.json).
