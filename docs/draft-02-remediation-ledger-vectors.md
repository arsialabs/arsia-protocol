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
- **Classification:** for structural failures, the individual classification
  required by DR-0.4, made in the vector cycle (VC): defective data, outdated
  expectation, or a case requiring a distinct validation procedure.
- **Coverage:** recorded at audit baseline `51610ac`. PC = crypto-checked; PH =
  hand-coded harness mirror; N = not exercised. No vector was fully covered.

**Annotations.**
- **X (A-39):** expectation contradicted by Draft-02.
- **X — corrected in C0.5:** that contradiction was fixed in C0.5.
- **MAY posture (DR-0.3):** expected-invalid on a MAY.
- **A-65:** the skip-classification document claims harness coverage that
  does not exist.

| ID | Structure | First failure reason | Classification | Coverage | Annotations | Disposition (VC) |
|---|---|---|---|---|---|---|
| INV-07 | pass | — | — | PC | A-65: documented harness coverage does not exist | — |
| INV-08 | pass | — | — | PC | — | — |
| INV-09 | pass | — | — | PC | — | — |
| INV-11 | pass | — | — | N | — | — |
| INV-12 | pass | — | — | PC | — | — |
| ITV-404 | pass | — | — | N | X (A-39) | E (A-39): v 3.0, validator rejects with `not_implemented`; left the skip set |
| ITV-405 | fail | `'2.0' was expected` | distinct validation procedure (VC) | N | — | P: major-2 compatibility procedure; left the skip set |
| ITV-406 | fail | `Additional properties are not allowed ('future_field' was unexpected)` | outdated expectation + distinct procedure (VC) | N | X (A-39) | E+P: v 2.1 with the unknown field; compatibility procedure; left the skip set |
| ITV-408 | pass | — | — | N | — | posture MAY (Core §8.3); executed by R16 |
| ITV-409 | fail | `'security' is a required property` | defective data (VC) | N | — | D: signed; token sub stated |
| ITV-410 | fail | `'security' is a required property` | defective data (VC) | N | — | D: signed; token aud stated |
| ITV-411 | fail | `'security' is a required property` | defective data (VC) | N | — | D: signed; executed by R16 (expired) |
| ITV-412 | fail | `'security' is a required property` | defective data (VC) | N | — | D: signed; token scope stated |
| ITV-413 | fail | `'security' is a required property` | defective data + outdated expectation (VC) | N | — | D+E: signed; min_v 2.1 against server_max 2.0 |
| ITV-414 | fail | `'security' is a required property` | defective data (VC) | N | — | D: signed |
| ITV-416 | fail | `'security' is a required property` | defective data (VC) | N | A-65: documented harness coverage does not exist | D: signed; posture configuration (strict mode) |
| ITV-417 | pass | — | — | PH | — | — |
| ITV-418 | fail | `'security' is a required property` | defective data (VC) | N | A-65: documented harness coverage does not exist | D: signed |
| ITV-421 | pass | — | — | PH | — | — |
| ITV-422 | fail | `'security' is a required property` | defective data (VC) | N | — | D: signed |
| ITV-424 | fail | `'security' is a required property` | defective data (VC) | N | — | D: signed |
| ITV-425 | pass | — | — | N | — | — |
| ITV-426 | pass | — | — | N | — | — |
| ITV-427 | pass | — | — | N | — | — |
| ITV-429 | pass | — | — | N | — | — |
| ITV-431 | pass | — | — | N | — | — |
| ITV-432 | pass | — | — | N | — | — |
| ITV-433 | pass | — | — | N | — | — |
| ITV-434 | pass | — | — | N | — | — |
| ITV-435 | pass | — | — | N | — | — |
| ITV-436 | pass | — | — | N | — | — |
| ITV-437 | pass | — | — | N | — | — |
| ITV-438 | fail | `Additional properties are not allowed ('routing_hint' was unexpected)` | outdated expectation (VC) | N | X (A-39) | E: explicit negative of Core §4.1.1 rule 1; left the skip set |
| ITV-439 | fail | `Additional properties are not allowed ('extended_context', 'telemetry_flags' were unexp…` | outdated expectation + distinct procedure (VC) | N | X (A-39) | E+P: v 2.2; compatibility procedure; left the skip set |
| ITV-440 | pass | — | — | N | — | posture MAY (Core §8.3); executed by R16 |
| ITV-442 | pass | — | — | N | — | — |
| ITV-445 | pass | — | — | N | — | — |
| ITV-446 | pass | — | — | N | — | — |
| ITV-448 | pass | — | — | N | — | — |
| ITV-449 | pass | — | — | N | — | — |
| ITV-450 | pass | — | — | N | — | — |
| ITV-457 | pass | — | — | N | — | — |
| ITV-458 | pass | — | — | N | — | — |
| ITV-459 | pass | — | — | N | — | — |
| ITV-460 | pass | — | — | N | — | — |
| ITV-461 | pass | — | — | N | — | — |
| ITV-462 | pass | — | — | N | — | — |
| ITV-463 | pass | — | — | N | — | — |
| ITV-466 | pass | — | — | N | — | — |
| ITV-467 | pass | — | — | N | — | — |
| ITV-475 | pass | — | — | N | — | — |
| ITV-476 | pass | — | — | N | — | — |
| ITV-477 | fail | `'security' is a required property` | defective data (VC) | N | — | D: signed; external agent_id stated |
| ITV-479 | pass | — | — | N | A-65: documented harness coverage does not exist | correlation re-expressed so the announced negative exists; recipient corrected |
| ITV-487 | pass | — | — | N | — | — |
| ITV-526 | pass | — | — | N | — | — |
| ITV-536 | fail | `'expires_at' is a required property` | defective data (VC) | N | A-65: documented harness coverage does not exist | D: request fields; signed |
| ITV-537 | fail | `'expires_at' is a required property` | defective data (VC) | N | — | D: request fields; signed |
| ITV-538 | fail | `'expires_at' is a required property` | defective data (VC) | N | A-65: documented harness coverage does not exist | D: request fields; signed |
| ITV-539 | fail | `'expires_at' is a required property` | defective data (VC) | N | — | D: request fields; signed; skip_reason without max() |
| ITV-540 | fail | `'expires_at' is a required property` | defective data (VC) | N | — | D: request fields; signed |
| ITV-541 | fail | `'expires_at' is a required property` | defective data (VC) | N | — | D: request fields; signed |
| ITV-543 | fail | `'expires_at' is a required property` | defective data (VC) | PC | — | D: request fields; args; re-signed |
| ITV-544 | fail | `'expires_at' is a required property` | defective data (VC) | PC | — | D: request fields; args; re-signed |
| ITV-545 | fail | `'expires_at' is a required property` | defective data (VC) | N | MAY posture (DR-0.3) | D: request fields; args; signed; posture MAY; executed by R16 |
| ITV-546 | fail | `'b0546001-d4e5-4f60-c123-445566778899' does not match '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4…` | defective data + outdated expectation (VC) | N | X — corrected in C0.5 | D+E: UUID v4; request fields; args; signed; left the skip set (Rule 2 schema-expressible); R16 attributes compliance causes |
| ITV-547 | fail | `'c0547001-e5f6-4071-d234-556677889900' does not match '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4…` | defective data (VC) | PC | — | D: UUID v4; request fields; args; null residency omitted; re-signed; executed by R16 |
| INV-18 | pass | — | — | PC | — | — |
| INV-19 | pass | — | — | PC | — | — |
| ITV-553 | fail | `'capabilities' is a required property` | defective data (VC) | N | — | D: capabilities; signed |
| ITV-554 | fail | `'capabilities' is a required property` | defective data (VC) | N | — | D: capabilities; signed |
| ITV-555 | fail | `'security' is a required property` | defective data (VC) | N | — | D: signed |
| INV-20 | fail | `'security' is a required property` | defective data (VC) | N | — | D: signed |
| INV-22 | fail | `'security' is a required property` | defective data (VC) | N | — | D: signed |
| INV-23 | pass | — | — | N | — | — |
| INV-24 | pass | — | — | N | — | — |
| INV-25 | fail | `'inform' is not one of ['request', 'response', 'event', 'error', 'pending_approval', 'a…` | defective data (VC) | PH | — | D: re-expressed as a conformant approval_decision; signed |
| ITV-563 | pass | — | — | PH | — | — |
| ITV-564 | pass | — | — | PH | — | — |
| ITV-565 | pass | — | — | PH | — | — |
| ITV-566 | pass | — | — | PH | — | — |
| ITV-567 | pass | — | — | PH | — | — |
| ITV-568 | pass | — | — | PH | — | — |
| ITV-570 | pass | — | — | N | — | — |
| ITV-571 | pass | — | — | N | — | — |
| ITV-572 | pass | — | — | N | — | — |
| ITV-575 | pass | — | — | PH | — | — |
| ITV-576 | pass | — | — | PH | — | — |
| ITV-577 | pass | — | — | PH | — | — |
| ITV-578 | pass | — | — | N | A-65: documented harness coverage does not exist | — |
| INV-37 | pass | — | — | N | — | — |
| INV-38 | pass | — | — | N | — | — |
| INV-39 | pass | — | — | N | — | — |
| ITV-579 | pass | — | — | PH | — | — |

**Counts (this register only, 94 rows).**
- Structure: pass 62; fail 32.
- Classification (VC): defective data 26; defective data + outdated expectation 2; outdated expectation 1; outdated expectation + distinct procedure 2; distinct validation procedure 1.
- Coverage at `51610ac`: PC 9; PH 13; N 72; fully covered 0.
- Annotations: X (A-39) 4; X — corrected in C0.5 1; MAY posture 1; A-65 7.
- Disposition (VC), per DR-0.4 for the 32 structural failures: D (defective data) 23;
  D+E 2 (ITV-413, ITV-546); E 1 (ITV-438); E+P 2 (ITV-406, ITV-439); P 1 (ITV-405);
  D re-expression 1 (INV-25); D with posture 2 (ITV-416, ITV-545). Structure after VC:
  every row passes; ITV-404/405/406/438/439/546 left the skip set and are validated as
  ordinary vectors. Per-ID evidence in [§16 of the evidence file](draft-02-remediation-ledger-evidence.md#16-vc-closure-evidence).
