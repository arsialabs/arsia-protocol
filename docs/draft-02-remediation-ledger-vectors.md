<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Draft-02 Remediation Ledger — Runtime-Vector Register

Part of the [Draft-02 remediation ledger](draft-02-remediation-ledger.md). This file
holds the runtime-vector register (§6); its section number is that of the main
ledger. Its counts are per register and never merged with those of any other
register.

## 6. Runtime-vector register

Structural results come from `scripts/validate_vectors.py` at execution
baseline `63a233b`, which validates runtime-only (`skip_schema`) vectors
structurally since C0.5. "First failure reason" is the first reported schema
error, truncated.

**Columns.**
- **Classification:** for structural failures, pending the individual
  classification required by DR-0.4.
- **Coverage:** recorded at audit baseline `51610ac`. PC = crypto-checked; PH =
  hand-coded harness mirror; N = not exercised. No vector was fully covered.

**Annotations.**
- **X (A-39):** expectation contradicted by Draft-02.
- **X — corrected in C0.5:** that contradiction was fixed in C0.5.
- **MAY posture (DR-0.3):** expected-invalid on a MAY.
- **A-65:** the skip-classification document claims harness coverage that
  does not exist.

| ID | Structure | First failure reason | Classification | Coverage | Annotations |
|---|---|---|---|---|---|
| INV-07 | pass | — | — | PC | A-65: documented harness coverage does not exist |
| INV-08 | pass | — | — | PC | — |
| INV-09 | pass | — | — | PC | — |
| INV-11 | pass | — | — | N | — |
| INV-12 | pass | — | — | PC | — |
| ITV-404 | pass | — | — | N | X (A-39) |
| ITV-405 | fail | `'2.0' was expected` | pending (DR-0.4) | N | — |
| ITV-406 | fail | `Additional properties are not allowed ('future_field' was unexpected)` | pending (DR-0.4) | N | X (A-39) |
| ITV-408 | pass | — | — | N | — |
| ITV-409 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| ITV-410 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| ITV-411 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| ITV-412 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| ITV-413 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| ITV-414 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| ITV-416 | fail | `'security' is a required property` | pending (DR-0.4) | N | A-65: documented harness coverage does not exist |
| ITV-417 | pass | — | — | PH | — |
| ITV-418 | fail | `'security' is a required property` | pending (DR-0.4) | N | A-65: documented harness coverage does not exist |
| ITV-421 | pass | — | — | PH | — |
| ITV-422 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| ITV-424 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| ITV-425 | pass | — | — | N | — |
| ITV-426 | pass | — | — | N | — |
| ITV-427 | pass | — | — | N | — |
| ITV-429 | pass | — | — | N | — |
| ITV-431 | pass | — | — | N | — |
| ITV-432 | pass | — | — | N | — |
| ITV-433 | pass | — | — | N | — |
| ITV-434 | pass | — | — | N | — |
| ITV-435 | pass | — | — | N | — |
| ITV-436 | pass | — | — | N | — |
| ITV-437 | pass | — | — | N | — |
| ITV-438 | fail | `Additional properties are not allowed ('routing_hint' was unexpected)` | pending (DR-0.4) | N | X (A-39) |
| ITV-439 | fail | `Additional properties are not allowed ('extended_context', 'telemetry_flags' were unexp…` | pending (DR-0.4) | N | X (A-39) |
| ITV-440 | pass | — | — | N | — |
| ITV-442 | pass | — | — | N | — |
| ITV-445 | pass | — | — | N | — |
| ITV-446 | pass | — | — | N | — |
| ITV-448 | pass | — | — | N | — |
| ITV-449 | pass | — | — | N | — |
| ITV-450 | pass | — | — | N | — |
| ITV-457 | pass | — | — | N | — |
| ITV-458 | pass | — | — | N | — |
| ITV-459 | pass | — | — | N | — |
| ITV-460 | pass | — | — | N | — |
| ITV-461 | pass | — | — | N | — |
| ITV-462 | pass | — | — | N | — |
| ITV-463 | pass | — | — | N | — |
| ITV-466 | pass | — | — | N | — |
| ITV-467 | pass | — | — | N | — |
| ITV-475 | pass | — | — | N | — |
| ITV-476 | pass | — | — | N | — |
| ITV-477 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| ITV-479 | pass | — | — | N | A-65: documented harness coverage does not exist |
| ITV-487 | pass | — | — | N | — |
| ITV-526 | pass | — | — | N | — |
| ITV-536 | fail | `'expires_at' is a required property` | pending (DR-0.4) | N | A-65: documented harness coverage does not exist |
| ITV-537 | fail | `'expires_at' is a required property` | pending (DR-0.4) | N | — |
| ITV-538 | fail | `'expires_at' is a required property` | pending (DR-0.4) | N | A-65: documented harness coverage does not exist |
| ITV-539 | fail | `'expires_at' is a required property` | pending (DR-0.4) | N | — |
| ITV-540 | fail | `'expires_at' is a required property` | pending (DR-0.4) | N | — |
| ITV-541 | fail | `'expires_at' is a required property` | pending (DR-0.4) | N | — |
| ITV-543 | fail | `'expires_at' is a required property` | pending (DR-0.4) | PC | — |
| ITV-544 | fail | `'expires_at' is a required property` | pending (DR-0.4) | PC | — |
| ITV-545 | fail | `'expires_at' is a required property` | pending (DR-0.4) | N | MAY posture (DR-0.3) |
| ITV-546 | fail | `'b0546001-d4e5-4f60-c123-445566778899' does not match '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4…` | pending (DR-0.4) | N | X — corrected in C0.5 |
| ITV-547 | fail | `'c0547001-e5f6-4071-d234-556677889900' does not match '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4…` | pending (DR-0.4) | PC | — |
| INV-18 | pass | — | — | PC | — |
| INV-19 | pass | — | — | PC | — |
| ITV-553 | fail | `'capabilities' is a required property` | pending (DR-0.4) | N | — |
| ITV-554 | fail | `'capabilities' is a required property` | pending (DR-0.4) | N | — |
| ITV-555 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| INV-20 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| INV-22 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| INV-23 | pass | — | — | N | — |
| INV-24 | pass | — | — | N | — |
| INV-25 | fail | `'inform' is not one of ['request', 'response', 'event', 'error', 'pending_approval', 'a…` | pending (DR-0.4) | PH | — |
| ITV-563 | pass | — | — | PH | — |
| ITV-564 | pass | — | — | PH | — |
| ITV-565 | pass | — | — | PH | — |
| ITV-566 | pass | — | — | PH | — |
| ITV-567 | pass | — | — | PH | — |
| ITV-568 | pass | — | — | PH | — |
| ITV-570 | pass | — | — | N | — |
| ITV-571 | pass | — | — | N | — |
| ITV-572 | pass | — | — | N | — |
| ITV-575 | pass | — | — | PH | — |
| ITV-576 | pass | — | — | PH | — |
| ITV-577 | pass | — | — | PH | — |
| ITV-578 | pass | — | — | N | A-65: documented harness coverage does not exist |
| INV-37 | pass | — | — | N | — |
| INV-38 | pass | — | — | N | — |
| INV-39 | pass | — | — | N | — |
| ITV-579 | pass | — | — | PH | — |

**Counts (this register only, 94 rows).**
- Structure: pass 62; fail 32.
- Classification: pending (DR-0.4) 32.
- Coverage at `51610ac`: PC 9; PH 13; N 72; fully covered 0.
- Annotations: X (A-39) 4; X — corrected in C0.5 1; MAY posture 1; A-65 7.
