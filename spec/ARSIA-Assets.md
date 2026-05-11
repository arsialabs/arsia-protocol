<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
# ARSIA-Assets — Assets Primitive Specification

**Protocol:** ARSIA Protocol
**Version:** 1.0
**Status:** Draft
**Authors:**
- Kirk Patrick (Arsia Labs) — kirk@arsialabs.ai
- Greici Savoldi (Arsia Labs) — greici@arsialabs.ai

**Draft-01 | March 2026 | References: ARSIA-Core.md §4 (message envelope), §10 (idempotency),
§11 (error handling), ARSIA-Actions.md §2 (risk levels), §3 (human oversight —
pending_approval/approval_decision), ARSIA-Identity.md §3.3 (DPoP for proof of possession),
ARSIA-State.md §6 (compliance profiles), §7 (audit trail format)**
**Arsia Labs — arsiaprotocol.org**

---

## Abstract

The Assets primitive defines how ARSIA Protocol agents represent, request, and record
value transfer events. ARSIA does not execute payments — it defines the message envelope
for value transfer intent, the receipt format, the escrow signaling mechanism, and the
audit trail format required by the Markets in Financial Instruments Directive (MiFID II,
Directive 2014/65/EU), the Digital Operational Resilience Act (DORA, Regulation
2022/2554/EU), and the revised Payment Services Directive (PSD2, Directive 2015/2366/EU)
for agent-assisted financial operations. This separation of concerns is intentional:
ARSIA is infrastructure, not a payment processor. Implementations that execute payments
using this protocol MUST obtain appropriate regulatory licences independently of their
ARSIA conformance status. The Assets primitive answers the second A in the ARSIA acronym:
how do agents transact, under what constraints, and with what accountability.

---

## Status of This Memo

This document specifies Draft-01 of the ARSIA Assets Primitive. This specification is
a working draft published by Arsia Labs for review and comment. Implementors should
expect breaking changes between draft revisions.

The canonical location for this specification is:

    https://arsiaprotocol.org/spec/assets/draft-01

Comments and issues should be directed to:

    https://github.com/arsialabs/arsia-protocol/issues

---

## Copyright Notice

Copyright (c) 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda).
This specification is licensed under the Creative Commons
Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0).
See LICENSE-SPEC.md for full terms.

---

## Table of Contents

1. [Scope and Non-Scope](#1-scope-and-non-scope)
   1. [In Scope](#11-in-scope)
   2. [Explicitly Out of Scope](#12-explicitly-out-of-scope)
   3. [Scope Boundary Enforcement](#13-scope-boundary-enforcement)
2. [Asset Types](#2-asset-types)
   1. [Currency](#21-currency)
   2. [Token](#22-token)
   3. [Entitlement](#23-entitlement)
   4. [Service Unit](#24-service-unit)
   5. [Asset Type Registry](#25-asset-type-registry)
3. [Message Types](#3-message-types)
   1. [AssetTransferRequest](#31-assettransferrequest)
   2. [AssetTransferReceipt](#32-assettransferreceipt)
   3. [AssetTransferReversal](#33-assettransferreversal)
4. [Escrow Mechanism](#4-escrow-mechanism)
   1. [Escrow Intent](#41-escrow-intent)
   2. [Escrow Lifecycle](#42-escrow-lifecycle)
   3. [Escrow Audit Trail](#43-escrow-audit-trail)
5. [Capability Model for Financial Operations](#5-capability-model-for-financial-operations)
   1. [Reserved Capabilities](#51-reserved-capabilities)
   2. [Two-Party Authorisation for Financial Operations](#52-two-party-authorisation-for-financial-operations)
6. [Compliance Obligations](#6-compliance-obligations)
   1. [MiFID II Audit Trail](#61-mifid-ii-audit-trail)
   2. [DORA Incident Reporting Hooks](#62-dora-incident-reporting-hooks)
   3. [PSD2 Strong Authentication](#63-psd2-strong-authentication)
7. [Assets Conformance Tests](#7-assets-conformance-tests)
8. [References](#8-references)
   1. [Normative References](#81-normative-references)
   2. [Informative References](#82-informative-references)

---

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14 [RFC 2119] [RFC 8174] when,
and only when, they appear in ALL CAPITALS, as shown here.

---

## 1. Scope and Non-Scope

The Assets primitive defines a precise boundary between protocol-level concerns and
provider-level concerns. This boundary is not a convenience — it is a regulatory
necessity. The activities on one side of this boundary (intent, receipt, audit) do not
require payment licences. The activities on the other side (execution, settlement,
account management) require licences under PSD2 Article 11 and national transpositions.
ARSIA occupies the first side of that boundary and explicitly excludes the second.

This scope boundary is permanent for the Assets primitive. It is not a limitation of
Draft-01 that will be relaxed in future versions. It is a design decision that reflects
the protocol's architectural position: ARSIA sits above transport protocols and below
the application layer. Payment execution is an application-layer concern that is
delegated to licensed providers.

### 1.1 In Scope

The following concerns are within the scope of the Assets primitive. Each is listed with
the rationale for its inclusion.

#### 1.1.1 AssetTransferRequest Message Type

Defines the intent to transfer value from one agent to another.

**Rationale.** The request is protocol infrastructure — it expresses who wants to pay
whom, how much, in what unit, under what regulatory profile, and with what idempotency
guarantees. The request does not move funds. It declares intent. Intent is a protocol
concern because counterparty agents, compliance brokers, and audit systems must be able
to inspect, route, and record transfer intent before any execution occurs. Without a
standardised request format, every agent framework would invent its own, making
cross-framework audit trail reconstruction impossible.

#### 1.1.2 AssetTransferReceipt Message Type

Confirms or denies a transfer request.

**Rationale.** The receipt provides the auditable proof that a transfer was attempted,
succeeded, or failed. Receipts are the cornerstone of the MiFID II audit trail (§6.1):
they link the ARSIA protocol's view of a transaction to the external payment provider's
transaction identifier, creating a verifiable chain from intent through execution to
settlement. Without a standardised receipt format, auditors would need to reconcile
across heterogeneous provider-specific formats for every agent interaction.

#### 1.1.3 AssetTransferReversal Message Type

Requests reversal of a previously completed transfer.

**Rationale.** Reversals are a MiFID II audit requirement — the chain of events must be
traceable from the original transfer through the reversal request to the reversal
outcome. Commission Delegated Regulation (EU) 2017/565, Article 76, requires firms to
maintain records of all transactions including cancellations and modifications. A
standardised reversal message ensures that the reversal event is captured in the same
audit trail as the original transfer, regardless of which payment provider executed
the reversal.

#### 1.1.4 Escrow Signaling

Defines conditional release intent — value held until a condition is met.

**Rationale.** Escrow is a protocol-level coordination pattern, not a payment execution
detail. The escrow mechanism defines the signaling between agents: who holds, who
releases, what triggers release, and what happens on timeout. The actual holding of
funds is delegated to the payment provider. ARSIA defines the message types that
coordinate the escrow lifecycle — creation, release, timeout, and dispute — so that
all parties and auditors can observe the escrow state transitions through protocol-level
messages.

#### 1.1.5 Capability Model for Financial Operations

Defines which capabilities are needed to initiate, approve, and reverse transfers.

**Rationale.** Capability enforcement is a core ARSIA primitive (ARSIA-Core.md §6.4,
ARSIA-Actions.md §1). Financial operations require specific, elevated capabilities
because they carry direct monetary risk. The capability model for assets follows the
same grammar, hierarchy, and enforcement semantics as the general ARSIA capability
model, but introduces capabilities with elevated risk levels that trigger mandatory
audit and human oversight requirements.

#### 1.1.6 Audit Trail Format for MiFID II Compliance

Defines what MUST be logged for every financial operation.

**Rationale.** This is the primary value proposition of ARSIA in financial services.
MiFID II Article 16(7), as implemented through Commission Delegated Regulation (EU)
2017/565, Articles 72-76 (commonly referred to as RTS 22), requires investment firms to
retain records of all services, activities, and transactions sufficient to enable
competent authorities to fulfil their supervisory tasks. The audit trail format
defined in this specification maps ARSIA protocol fields to the specific data points
required by RTS 22, ensuring that firms can satisfy their record-keeping obligations
through protocol-level audit records without additional instrumentation.

#### 1.1.7 DORA Incident Reporting Hooks

Defines how infrastructure failures during financial operations are signaled.

**Rationale.** The Digital Operational Resilience Act (DORA, Regulation 2022/2554/EU)
requires financial entities to establish ICT-related incident management processes
(Article 17) and to report major ICT-related incidents to competent authorities
(Article 19). When a payment provider is unreachable, a network failure disrupts a
transfer, or a broker relay fails during a financial operation, ARSIA agents MUST
generate structured incident events that can be routed to the entity's DORA reporting
system. Without protocol-level incident hooks, infrastructure failures during financial
operations would be invisible to DORA reporting processes.

#### 1.1.8 PSD2 Strong Authentication Requirements

Maps ARSIA's human oversight mechanism to PSD2's Strong Customer Authentication (SCA).

**Rationale.** PSD2 Article 97 requires payment service providers to apply strong
customer authentication when a payer initiates an electronic payment transaction. Strong
customer authentication requires at least two of three factors: knowledge (something the
user knows), possession (something the user has), and inherence (something the user is).
ARSIA's existing `pending_approval` and `approval_decision` mechanism (ARSIA-Actions.md
§3) already provides two of these factors through EdDSA signature verification. This
section maps the existing mechanism to PSD2 requirements, demonstrating that ARSIA's
human oversight flow satisfies SCA at the protocol level without requiring additional
authentication infrastructure.

### 1.2 Explicitly Out of Scope

The following concerns are explicitly excluded from the Assets primitive. Each exclusion
is permanent for this primitive and is listed with the rationale for its exclusion.

#### 1.2.1 Account Creation or Management

Creation, modification, or deletion of accounts at financial institutions or payment
providers.

**Excluded because:** Account management requires integration with specific financial
institutions and is governed by institution-specific onboarding processes, KYC/AML
requirements, and contractual relationships. These are provider-specific concerns that
vary across jurisdictions, institutions, and account types. They cannot be standardised
at the protocol level without imposing specific provider dependencies. ARSIA agents
reference accounts through opaque identifiers provided by the payment provider; the
protocol does not interpret, validate, or manage these identifiers.

#### 1.2.2 Payment Execution

The actual movement of funds between accounts.

**Excluded because:** Payment execution requires payment institution authorisation under
PSD2 Article 11 (or equivalent national legislation for non-EU jurisdictions). An
entity that executes payments without authorisation commits a regulatory offence. ARSIA
is a protocol, not a payment institution. ARSIA agents delegate execution to licensed
payment providers and record the result via AssetTransferReceipt. The protocol defines
the envelope for communicating with providers, not the provider's internal execution
logic.

#### 1.2.3 Settlement Mechanisms

Clearing and settlement of financial transactions — the process by which the transfer
of ownership of financial instruments or funds is finalised.

**Excluded because:** Clearing and settlement are domain-specific processes governed by
Central Securities Depositories (CSDs) under the CSD Regulation (Regulation 909/2014/EU)
and by payment system operators under the Settlement Finality Directive (Directive
98/26/EC). These processes involve multilateral netting, delivery-versus-payment
mechanisms, and settlement cycles (T+1, T+2) that are specific to the asset class,
market, and CSD. They are transport-level financial infrastructure that operates below
ARSIA's protocol layer.

#### 1.2.4 Clearing Networks

Integration with clearing and payment networks such as SWIFT, SEPA, TARGET2, TIPS,
CHAPS, Fedwire, or equivalent systems.

**Excluded because:** Clearing networks are transport-level financial infrastructure.
ARSIA operates at the compliance and messaging layer above transport. Integration with
clearing networks is the responsibility of the licensed payment provider that executes
the transfer. The provider reports the result back to the ARSIA agent via the
AssetTransferReceipt message, which includes the provider's transaction reference for
reconciliation. ARSIA does not prescribe which clearing network the provider uses.

#### 1.2.5 Cryptocurrency or DeFi Protocols

Transfer of cryptocurrency, digital assets on distributed ledgers, or interaction with
decentralised finance (DeFi) protocols.

**Excluded because:** ARSIA v1.0 focuses on regulated fiat currency transfers and
application-defined value units (tokens, entitlements, service units). Cryptocurrency
and DeFi protocols introduce regulatory ambiguity (the MiCA Regulation, Regulation
2023/1114/EU, is still in phased implementation), technical complexity (blockchain
consensus, gas fees, smart contract interaction), and jurisdictional fragmentation that
would complicate the core protocol without serving the primary use case. Future versions
of the Assets primitive MAY introduce a `crypto` asset type with appropriate regulatory
mappings once MiCA implementation is mature.

#### 1.2.6 Cross-Currency Conversion

Foreign exchange (FX) operations — converting one currency to another as part of a
transfer.

**Excluded because:** FX operations require specific licences (money exchange office
registration under national transpositions of PSD2), access to real-time market data
feeds, and execution against FX counterparties. These are provider-level concerns. An
ARSIA agent that needs to transfer value across currencies MUST delegate the conversion
to a licensed FX provider and record two separate AssetTransferReceipt messages: one for
the debit in the source currency and one for the credit in the target currency. This
approach preserves the audit trail while keeping FX complexity out of the protocol.

### 1.3 Scope Boundary Enforcement

Implementations MUST NOT embed payment execution logic within ARSIA messages. The
`payload.args` of an AssetTransferRequest MUST NOT contain:

- Account numbers, IBANs, sort codes, or other financial account identifiers.
- Card numbers, CVVs, or other payment card data.
- Banking API credentials, API keys, or authentication tokens for financial
  institutions.
- Wire transfer instructions, SWIFT MT messages, or clearing network payloads.

These data elements belong to the provider integration layer, not the protocol layer. If
an implementation needs to transmit financial account identifiers between agents, it MUST
do so through a separate, encrypted channel that is not part of the ARSIA message
envelope. The `provider` field in AssetTransferRequest (§3.1) identifies the licensed
payment provider to route through; the actual provider interaction occurs outside the
ARSIA protocol.

Implementations SHOULD validate that `payload.args` does not contain patterns matching
financial account identifiers (e.g., IBAN format `^[A-Z]{2}\d{2}[A-Z0-9]{4,}$`, card
number patterns) and SHOULD reject such messages with error code `invalid_request`.

---

## 2. Asset Types

The ARSIA Protocol defines four asset types that represent the categories of value that
agents can transfer. These types form a normative enumeration: conformant implementations
MUST support all four types and MUST NOT define additional types outside this
enumeration. Future versions of this specification MAY extend the enumeration.

The asset type determines the precision requirements, the applicable regulatory
framework, and the audit obligations for a transfer. Implementations MUST validate that
the `amount` field in an AssetTransferRequest conforms to the precision requirements of
the declared `asset_type`.

### 2.1 Currency

**Identifier:** `"currency"`

**Definition.** A unit of fiat currency as defined by ISO 4217 [ISO 4217]. The
`currency_or_unit` field MUST contain a valid ISO 4217 alphabetic code (three uppercase
ASCII letters). Examples: `"EUR"` (Euro), `"USD"` (United States Dollar), `"GBP"`
(Pound Sterling), `"CHF"` (Swiss Franc), `"SEK"` (Swedish Krona).

**Precision.** The `amount` field MUST have at most 2 decimal places for currency
transfers. This constraint is REQUIRED and non-negotiable: implementations MUST reject
AssetTransferRequest messages with `asset_type: "currency"` where the `amount` has more
than 2 decimal places. The 2-decimal-place constraint reflects the minor unit of the
vast majority of ISO 4217 currencies. For the small number of currencies with 0 or 3
minor units (e.g., JPY with 0, KWD with 3), implementations SHOULD use the ISO 4217
minor unit count but MUST NOT exceed 2 decimal places in the ARSIA message. Rounding
is the responsibility of the payment provider.

**Regulatory applicability.** Currency transfers are subject to:

- **MiFID II** (Directive 2014/65/EU): When the transfer relates to investment services
  or activities, MiFID II record-keeping obligations apply (§6.1).
- **PSD2** (Directive 2015/2366/EU): Payment execution requires authorisation under
  PSD2 Article 11. ARSIA agents delegate execution to licensed providers.
- **DORA** (Regulation 2022/2554/EU): ICT-related incidents during currency transfers
  MUST be reported per §6.2.

**Validation.**

```
asset_type = "currency"
currency_or_unit MUST match ^[A-Z]{3}$
amount MUST be > 0
amount MUST have ≤ 2 decimal places
```

### 2.2 Token

**Identifier:** `"token"`

**Definition.** An application-defined unit of value that is not a fiat currency and
does not represent an access right or a quantifiable service delivery unit. Tokens are
general-purpose value units whose semantics are defined by the issuing application.
Examples: API credits, compute units, SaaS subscription tokens, loyalty points,
in-application virtual currency.

**Precision.** The `amount` field MAY have up to 8 decimal places. Implementations MUST
reject amounts with more than 8 decimal places.

**Regulatory applicability.** Token transfers are subject to general ARSIA audit
requirements (audit_required, retention_days) as determined by the applicable compliance
profile. Tokens are NOT subject to financial regulation under MiFID II, PSD2, or DORA
unless the token qualifies as an electronic money instrument under the Electronic Money
Directive (EMD2, Directive 2009/110/EC) or as a payment instrument under PSD2. The
determination of whether a specific token qualifies as a regulated instrument is the
responsibility of the token issuer and is outside the scope of ARSIA.

**Warning.** If a token is exchangeable for fiat currency at a fixed or market rate, it
may qualify as electronic money under EMD2 Article 2(2). In such cases, the token issuer
SHOULD classify the transfer as `asset_type: "currency"` and apply the corresponding
regulatory framework. ARSIA does not make this determination — it is the responsibility
of the operator.

**Validation.**

```
asset_type = "token"
currency_or_unit MUST be a non-empty string, maxLength 32
amount MUST be > 0
amount MUST have ≤ 8 decimal places
```

### 2.3 Entitlement

**Identifier:** `"entitlement"`

**Definition.** An access right, subscription, or licence that grants the holder
permission to use a service, access a resource, or exercise a privilege. Entitlements
are discrete grants — they are typically counted in integer units (seats, months,
licences) rather than fractional amounts. Examples: SaaS seat licences, data feed
subscriptions, premium tier access grants, conference passes, support plan activations.

**Precision.** The `amount` field SHOULD be an integer (no decimal places). Fractional
entitlements are permitted (e.g., 0.5 of a licence representing a half-year
subscription) but are NOT RECOMMENDED. When fractional amounts are used, precision
MUST NOT exceed 2 decimal places.

**Regulatory applicability.** Entitlement transfers are subject to general ARSIA audit
requirements. Entitlements are not financial instruments and are not subject to MiFID II,
PSD2, or DORA. If an entitlement has monetary value and is tradeable on a secondary
market, the operator SHOULD evaluate whether it qualifies as a financial instrument
under MiFID II Annex I Section C and reclassify accordingly.

**Validation.**

```
asset_type = "entitlement"
currency_or_unit MUST be a non-empty string, maxLength 32
amount MUST be > 0
amount SHOULD be an integer
amount MUST have ≤ 2 decimal places if fractional
```

### 2.4 Service Unit

**Identifier:** `"service_unit"`

**Definition.** A quantifiable unit of service delivery that has been consumed or is
being allocated. Service units represent measurable work or resource usage. Examples:
API calls completed, compute hours consumed, storage GB-months provisioned, bandwidth
TB transferred, inference tokens processed, GPU-hours allocated.

**Precision.** The `amount` field MAY have up to 4 decimal places. This accommodates
fine-grained metering (e.g., 0.0001 GPU-hours) while preventing excessive precision
that would complicate reconciliation.

**Regulatory applicability.** Service unit transfers are subject to general ARSIA audit
requirements. Service units are not financial instruments and are not subject to MiFID
II, PSD2, or DORA. However, service unit transfers that form part of a billing
workflow that results in a currency payment SHOULD reference the corresponding
AssetTransferRequest for the currency payment via the `metadata` field, enabling
end-to-end audit trail reconstruction.

**Validation.**

```
asset_type = "service_unit"
currency_or_unit MUST be a non-empty string, maxLength 32
amount MUST be > 0
amount MUST have ≤ 4 decimal places
```

### 2.5 Asset Type Registry

The following table summarises the normative properties of each asset type:

| Asset Type     | Identifier       | Unit Format         | Max Decimals | MiFID II | PSD2 | DORA | Audit |
|----------------|------------------|---------------------|--------------|----------|------|------|-------|
| Currency       | `"currency"`     | ISO 4217 code       | 2            | YES      | YES  | YES  | MUST  |
| Token          | `"token"`        | Application-defined | 8            | NO*      | NO*  | NO*  | SHOULD |
| Entitlement    | `"entitlement"`  | Application-defined | 2            | NO       | NO   | NO   | SHOULD |
| Service Unit   | `"service_unit"` | Application-defined | 4            | NO       | NO   | NO   | SHOULD |

*Unless the token qualifies as an electronic money instrument under EMD2 or a payment
instrument under PSD2, in which case the operator MUST apply the corresponding regulatory
framework.

---

## 3. Message Types

The Assets primitive defines three message types for the transfer lifecycle: request,
receipt, and reversal. These message types use the ARSIA message envelope
(ARSIA-Core.md §4) and follow the payload structure conventions (ARSIA-Core.md §4.4).

All three message types MUST be signed using the sender's Ed25519 key
(ARSIA-Core.md §5.1). Unsigned asset transfer messages MUST be rejected.

### 3.1 AssetTransferRequest

The AssetTransferRequest message expresses an agent's intent to transfer value to
another agent. It does not execute the transfer — it declares the transfer parameters
and routes the request to the appropriate payment provider or receiving agent.

**Envelope configuration:**

| Field          | Value                                                              |
|----------------|--------------------------------------------------------------------|
| `intent`       | `"request"`                                                        |
| `capabilities` | MUST include `"arsiaprotocol.assets.transfer.initiate"`                    |
| `expires_at`   | REQUIRED (ARSIA-Core.md §4.2.2)                                   |
| `idempotency`  | REQUIRED — see `idempotency_key` below                             |
| `security`     | REQUIRED — message MUST be signed                                  |
| `compliance`   | RECOMMENDED for currency transfers; OPTIONAL for other asset types |

**Payload type:** `"arsiaprotocol.assets/transfer-request"`

**Payload version:** `"1.0"`

#### 3.1.1 Request Fields — `payload.args`

The `payload.args` object MUST contain the following fields. Unless marked OPTIONAL,
every field is REQUIRED.

##### `amount`

- **Type:** number
- **REQUIRED.**
- **Constraints:** A positive number representing the value to transfer. The value MUST
  be strictly greater than zero. Precision constraints depend on the `asset_type`:
  - `"currency"`: maximum 2 decimal places.
  - `"token"`: maximum 8 decimal places.
  - `"entitlement"`: SHOULD be integer; maximum 2 decimal places if fractional.
  - `"service_unit"`: maximum 4 decimal places.
- **Validation:** Implementations MUST reject requests where `amount` ≤ 0 with error
  code `invalid_request` and description `"amount must be greater than zero"`.
  Implementations MUST reject requests where the decimal precision exceeds the maximum
  for the declared `asset_type` with error code `invalid_request` and description
  `"amount precision exceeds maximum for asset type {asset_type}"`.

##### `currency_or_unit`

- **Type:** string
- **REQUIRED.**
- **Maximum length:** 32 characters.
- **Constraints:** For `asset_type: "currency"`, this field MUST contain a valid ISO
  4217 alphabetic code — three uppercase ASCII letters (e.g., `"EUR"`, `"USD"`, `"GBP"`).
  Implementations SHOULD validate against the ISO 4217 code list. For other asset types,
  this field contains an application-defined identifier (e.g., `"api-credits"`,
  `"compute-hours"`, `"premium-seats"`). Application-defined identifiers MUST be
  lowercase ASCII letters, digits, and hyphens only, and MUST NOT match any ISO 4217
  code to avoid ambiguity.
- **Pattern (currency):** `^[A-Z]{3}$`
- **Pattern (other):** `^[a-z0-9][a-z0-9-]{0,30}[a-z0-9]$`

##### `asset_type`

- **Type:** string
- **REQUIRED.**
- **Allowed values:** `"currency"`, `"token"`, `"entitlement"`, `"service_unit"`
- **Constraints:** Determines the precision requirements, regulatory applicability, and
  audit obligations for this transfer, as defined in §2.

##### `from_agent`

- **Type:** string
- **Format:** Agent identifier (ARSIA-Core.md §3).
- **REQUIRED.**
- **Constraints:** The agent-id of the payer — the entity from which value is debited.
  In the common case, `from_agent` matches the message envelope's `from` field (the
  sender is the payer). However, `from_agent` MAY differ from `from` when the sender
  is acting on behalf of the payer under delegated authority. When `from_agent` differs
  from the envelope's `from`, the sender MUST possess a valid access token that
  authorises the delegation — the mechanism for delegation authorisation is defined by
  the Authorization Server and is outside the scope of this specification.

##### `to_agent`

- **Type:** string
- **Format:** Agent identifier (ARSIA-Core.md §3).
- **REQUIRED.**
- **Constraints:** The agent-id of the payee — the entity to which value is credited.
  The `to_agent` MAY differ from the message envelope's `to` (e.g., when the message
  is addressed to a transfer processing agent that credits a different agent). The
  `to_agent` MUST be a valid ARSIA agent identifier. The receiving agent MUST validate
  that `to_agent` refers to an agent that is known and reachable.

##### `payment_reference`

- **Type:** string
- **REQUIRED.**
- **Maximum length:** 128 characters.
- **Constraints:** A unique reference for this transfer, used for MiFID II traceability,
  audit trail correlation, and reconciliation with the external payment provider. The
  `payment_reference` MUST be unique within the deployment scope — that is, no two
  AssetTransferRequest messages within the same deployment MAY share a
  `payment_reference`. The format is implementation-defined. The RECOMMENDED format is:

  ```
  {org}-{year}-{sequence}
  ```

  Example: `"acme-2026-00042"`

  The `payment_reference` is echoed in the AssetTransferReceipt (§3.2) and the
  AssetTransferReversal (§3.3), providing a stable identifier that links all messages
  in a transfer lifecycle. It is distinct from the message `id` (which is unique per
  message) and from the idempotency key (which prevents duplicate execution).

##### `description`

- **Type:** string
- **REQUIRED.**
- **Maximum length:** 256 characters.
- **Constraints:** A human-readable description of the purpose of this transfer. The
  description is logged in the audit trail (§6.1) and is visible to human oversight
  approvers (§5.2). It SHOULD be specific enough for an auditor or compliance officer
  to understand the business purpose of the transfer without consulting additional
  systems. Examples:
  - `"MiFID II suitability assessment fee for client portfolio rebalance"`
  - `"API usage billing for March 2026 — 42,500 inference tokens"`
  - `"Escrow deposit for delivery of dataset DS-2026-0053"`

##### `provider`

- **Type:** string
- **Format:** Agent identifier (ARSIA-Core.md §3).
- **OPTIONAL.**
- **Constraints:** The agent-id of the licensed payment provider to route the transfer
  through. When present, the transfer MUST be routed to this provider for execution.
  When absent, the receiving agent selects the provider based on its own provider
  selection logic (which is outside the scope of this specification). The provider
  MUST be a licensed payment institution for currency transfers (PSD2 Art. 11). For
  non-currency transfers, the provider is the application-defined entity that manages
  the token, entitlement, or service unit ledger.

##### `escrow_conditions`

- **Type:** object (EscrowConditions — §4.1)
- **OPTIONAL.**
- **Constraints:** When present, the transfer is held in escrow until the conditions
  defined in the EscrowConditions object are met. The escrow mechanism is defined in
  §4. When `escrow_conditions` is present, the initial AssetTransferReceipt MUST have
  `status: "escrowed"` (not `"completed"` or `"pending"`).

##### `idempotency_key`

- **Type:** string
- **REQUIRED.**
- **Maximum length:** 128 characters.
- **Constraints:** REQUIRED for ALL asset transfer requests, regardless of asset type.
  This is stricter than the general ARSIA idempotency mechanism (ARSIA-Core.md §10),
  which makes idempotency OPTIONAL for most message types. For asset transfers,
  idempotency is MANDATORY because duplicate execution has direct financial
  consequences. The `idempotency_key` MUST be placed in the envelope's
  `idempotency.key` field as defined in ARSIA-Core.md §4.3.2. The receiving agent
  MUST implement the duplicate detection behaviour defined in ARSIA-Core.md §10.3:
  if a request is received with an `idempotency_key` that matches a previously
  processed request (same sender, same recipient, same payload type), the agent MUST
  return the original response without re-executing the transfer.

##### `metadata`

- **Type:** object
- **OPTIONAL.**
- **Constraints:** Additional application-specific data that travels with the transfer
  request. The `metadata` object is opaque to the ARSIA protocol — its structure is
  not validated by the protocol. However, the `metadata` object IS subject to audit
  logging: when `audit_required` is true, the audit record MUST include the
  `payload_hash` (SHA-256 of the canonicalized payload, which includes metadata). The
  `metadata` object MUST NOT contain financial account identifiers, payment card data,
  or banking credentials (§1.3).

#### 3.1.2 Complete AssetTransferRequest Example

The following example shows a complete AssetTransferRequest for a MiFID II regulated
currency transfer:

```json
{
  "v": "1.0",
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "ts": "2026-03-24T14:30:00.000Z",
  "from": "agent:acme.billing",
  "to": "agent:acme.transfer-processor",
  "intent": "request",
  "expires_at": "2026-03-24T14:35:00.000Z",
  "capabilities": ["arsiaprotocol.assets.transfer.initiate"],
  "idempotency": {
    "key": "acme-2026-00042",
    "expires_at": "2026-03-25T14:30:00.000Z"
  },
  "context": {
    "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
    "span_id": "00f067aa0ba902b7"
  },
  "security": {
    "alg": "EdDSA",
    "kid": "agent:acme.billing#key1",
    "sig": "..."
  },
  "compliance": {
    "profile": "MIFID-II",
    "data_residency": "EU",
    "audit_required": true,
    "retention_days": 1825,
    "human_oversight": "required_before_execution"
  },
  "payload": {
    "type": "arsiaprotocol.assets/transfer-request",
    "version": "1.0",
    "args": {
      "amount": 1500.00,
      "currency_or_unit": "EUR",
      "asset_type": "currency",
      "from_agent": "agent:acme.billing",
      "to_agent": "agent:contoso.treasury",
      "payment_reference": "acme-2026-00042",
      "description": "MiFID II suitability assessment fee for client portfolio rebalance — Q1 2026",
      "provider": "agent:europa.payments.sepa",
      "idempotency_key": "acme-2026-00042",
      "metadata": {
        "client_portfolio_id": "PF-2026-1234",
        "assessment_id": "RA-2026-5678"
      }
    }
  }
}
```

#### 3.1.3 AssetTransferRequest for Non-Currency Asset

The following example shows an AssetTransferRequest for a token transfer (API credits):

```json
{
  "v": "1.0",
  "id": "a1b2c3d4-5678-4abc-9012-def345678901",
  "ts": "2026-03-24T15:00:00.000Z",
  "from": "agent:acme.billing",
  "to": "agent:acme.credit-ledger",
  "intent": "request",
  "expires_at": "2026-03-24T15:05:00.000Z",
  "capabilities": ["arsiaprotocol.assets.transfer.initiate"],
  "idempotency": {
    "key": "credits-march-2026-tenant-42",
    "expires_at": "2026-03-25T15:00:00.000Z"
  },
  "security": {
    "alg": "EdDSA",
    "kid": "agent:acme.billing#key1",
    "sig": "..."
  },
  "payload": {
    "type": "arsiaprotocol.assets/transfer-request",
    "version": "1.0",
    "args": {
      "amount": 50000,
      "currency_or_unit": "api-credits",
      "asset_type": "token",
      "from_agent": "agent:acme.billing",
      "to_agent": "agent:acme.tenant-42",
      "payment_reference": "credits-march-2026-tenant-42",
      "description": "Monthly API credit allocation — March 2026 — Pro plan",
      "idempotency_key": "credits-march-2026-tenant-42"
    }
  }
}
```

### 3.2 AssetTransferReceipt

The AssetTransferReceipt message confirms or denies an AssetTransferRequest. It is the
auditable proof of the transfer outcome and the linkage between the ARSIA protocol's
view of the transaction and the external payment provider's transaction identifier.

**Envelope configuration:**

| Field            | Value                                                            |
|------------------|------------------------------------------------------------------|
| `intent`         | `"response"`                                                     |
| `correlation_id` | REQUIRED — MUST equal the `id` of the AssetTransferRequest       |
| `security`       | REQUIRED — message MUST be signed                                |
| `compliance`     | SHOULD echo the compliance object from the request               |

**Payload type:** `"arsiaprotocol.assets/transfer-receipt"`

**Payload version:** `"1.0"`

#### 3.2.1 Receipt Fields — `payload.result`

The `payload.result` object MUST contain the following fields. Unless marked OPTIONAL,
every field is REQUIRED.

##### `status`

- **Type:** string
- **REQUIRED.**
- **Allowed values:** `"pending"`, `"completed"`, `"failed"`, `"escrowed"`
- **Constraints:** The terminal state of the transfer from the ARSIA protocol's
  perspective. The semantics of each status are:

  - **`"pending"`**: The transfer request has been accepted and forwarded to the payment
    provider for execution. The transfer has not yet settled. A subsequent
    AssetTransferReceipt with status `"completed"` or `"failed"` SHOULD follow when
    the provider reports the outcome. The `"pending"` status is transient: it indicates
    that the protocol has accepted the request but cannot yet confirm the outcome.

  - **`"completed"`**: The transfer has been executed and settled at the payment
    provider. The funds (or tokens, entitlements, service units) have been credited to
    the `to_agent`. This is a terminal state — no further status updates are expected
    for this transfer unless a reversal is initiated (§3.3).

  - **`"failed"`**: The transfer was rejected by the provider, failed during execution,
    or was rejected by the ARSIA agent for compliance or validation reasons. No value
    was transferred. The `failure_reason` field (below) MUST be present. This is a
    terminal state.

  - **`"escrowed"`**: The transfer has been accepted but the value is held in escrow
    pending the release conditions defined in the request's `escrow_conditions` (§4).
    The value has been debited from `from_agent` but not yet credited to `to_agent`.
    The escrow lifecycle (§4.2) determines the subsequent state transitions.

##### `payment_reference`

- **Type:** string
- **REQUIRED.**
- **Constraints:** Echoed from the AssetTransferRequest. MUST match exactly
  — byte-for-byte string comparison. This field provides the stable identifier
  that links the receipt to the request across the audit trail.

##### `provider_reference`

- **Type:** string
- **OPTIONAL** (present when the provider has processed the request).
- **Maximum length:** 256 characters.
- **Constraints:** The external payment provider's transaction identifier. This field
  links the ARSIA audit record to the provider's records, enabling reconciliation
  between the ARSIA audit trail and the provider's transaction log. For SEPA Credit
  Transfers, this is the end-to-end identification. For SWIFT transfers, this is the
  UETR (Unique End-to-End Transaction Reference). For application-defined providers,
  this is the provider's internal transaction ID. The format is provider-specific and
  opaque to the ARSIA protocol.

##### `amount`

- **Type:** number
- **REQUIRED.**
- **Constraints:** The actual amount processed by the provider. In the common case,
  this equals the requested amount. It MAY differ from the requested amount in cases
  of partial execution — for example, when the provider can only fulfil part of the
  request due to insufficient balance or regulatory limits. When `amount` differs from
  the requested amount, the receipt's `metadata` field SHOULD include a
  `partial_execution_reason` string explaining the discrepancy. Implementations SHOULD
  alert the requesting agent when the receipt amount differs from the request amount.

##### `currency_or_unit`

- **Type:** string
- **REQUIRED.**
- **Constraints:** Echoed from the AssetTransferRequest. MUST match exactly.

##### `initiated_at`

- **Type:** string
- **Format:** RFC 3339 date-time with mandatory millisecond precision and UTC timezone
  designator.
- **REQUIRED.**
- **Constraints:** The timestamp when the transfer was initiated at the payment provider.
  This is the provider's timestamp, not the ARSIA message timestamp. It records when
  the provider began processing the transfer. For MiFID II audit purposes (§6.1), this
  is the transaction timestamp — the moment at which the firm's order was transmitted
  to the execution venue.

##### `settled_at`

- **Type:** string
- **Format:** RFC 3339 date-time with mandatory millisecond precision and UTC timezone
  designator.
- **OPTIONAL.**
- **Constraints:** The timestamp when the transfer was settled — when the value was
  definitively credited to the `to_agent`'s account at the provider. This field is
  NULL (absent) when `status` is `"pending"` or `"escrowed"` because settlement has
  not yet occurred. For `status: "completed"`, this field SHOULD be present. For
  `status: "failed"`, this field MUST be absent (a failed transfer was not settled).

##### `failure_reason`

- **Type:** string
- **Maximum length:** 512 characters.
- **Conditionally REQUIRED:** MUST be present when `status` is `"failed"`. MUST be
  absent when `status` is `"completed"`, `"pending"`, or `"escrowed"`.
- **Constraints:** A human-readable explanation of why the transfer failed. The
  `failure_reason` is logged in the audit trail and is visible to compliance officers.
  It SHOULD be specific enough for an operator to diagnose the failure without
  consulting the provider's logs. Examples:
  - `"Insufficient funds in payer account"`
  - `"Provider timeout — SEPA Credit Transfer endpoint unreachable after 30s"`
  - `"Compliance rejection — data residency constraint violated"`
  - `"Invalid payee agent — agent:contoso.treasury not found in provider registry"`

##### `audit_id`

- **Type:** string
- **Format:** UUID version 4 per [RFC 9562].
- **REQUIRED.**
- **Constraints:** References the audit record for this transfer in the agent's audit
  trail. For asset transfers that meet the conditions in §6.1, an audit record MUST be
  generated regardless of the `audit_required` flag in the compliance object. The `audit_id` provides a direct link from the receipt message to
  the audit storage, enabling auditors to retrieve the full audit record without
  searching by payment_reference or date range.

#### 3.2.2 Complete AssetTransferReceipt Example

The following example shows a complete AssetTransferReceipt for a completed currency
transfer:

```json
{
  "v": "1.0",
  "id": "b2c3d4e5-6789-4bcd-a012-ef4567890123",
  "ts": "2026-03-24T14:30:12.345Z",
  "from": "agent:acme.transfer-processor",
  "to": "agent:acme.billing",
  "intent": "response",
  "correlation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "security": {
    "alg": "EdDSA",
    "kid": "agent:acme.transfer-processor#key1",
    "sig": "..."
  },
  "compliance": {
    "profile": "MIFID-II",
    "data_residency": "EU",
    "audit_required": true,
    "retention_days": 1825
  },
  "payload": {
    "type": "arsiaprotocol.assets/transfer-receipt",
    "version": "1.0",
    "result": {
      "status": "completed",
      "payment_reference": "acme-2026-00042",
      "provider_reference": "SEPA-UETR-2026-03-24-abcdef12",
      "amount": 1500.00,
      "currency_or_unit": "EUR",
      "initiated_at": "2026-03-24T14:30:05.123Z",
      "settled_at": "2026-03-24T14:30:11.456Z",
      "audit_id": "c3d4e5f6-7890-4cde-b123-f56789012345"
    }
  }
}
```

#### 3.2.3 Failed Transfer Receipt Example

```json
{
  "v": "1.0",
  "id": "d4e5f6a7-8901-4def-c234-567890123456",
  "ts": "2026-03-24T14:30:35.678Z",
  "from": "agent:acme.transfer-processor",
  "to": "agent:acme.billing",
  "intent": "response",
  "correlation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "security": {
    "alg": "EdDSA",
    "kid": "agent:acme.transfer-processor#key1",
    "sig": "..."
  },
  "payload": {
    "type": "arsiaprotocol.assets/transfer-receipt",
    "version": "1.0",
    "result": {
      "status": "failed",
      "payment_reference": "acme-2026-00042",
      "amount": 1500.00,
      "currency_or_unit": "EUR",
      "initiated_at": "2026-03-24T14:30:05.123Z",
      "failure_reason": "Provider timeout — SEPA Credit Transfer endpoint unreachable after 30s. Provider: agent:europa.payments.sepa. HTTP status: 504.",
      "audit_id": "e5f6a7b8-9012-4ef0-d345-678901234567"
    }
  }
}
```

### 3.3 AssetTransferReversal

The AssetTransferReversal message requests the reversal of a previously completed
transfer. Reversals are a critical component of the MiFID II audit trail — they ensure
that the chain of events from original transfer through reversal is fully traceable.

**Envelope configuration:**

| Field          | Value                                                              |
|----------------|--------------------------------------------------------------------|
| `intent`       | `"request"`                                                        |
| `capabilities` | MUST include `"arsiaprotocol.assets.transfer.reverse"`                     |
| `expires_at`   | REQUIRED (ARSIA-Core.md §4.2.2)                                   |
| `idempotency`  | REQUIRED — reversals MUST be idempotent                            |
| `security`     | REQUIRED — message MUST be signed                                  |

**Payload type:** `"arsiaprotocol.assets/transfer-reversal"`

**Payload version:** `"1.0"`

#### 3.3.1 Reversal Fields — `payload.args`

##### `original_payment_reference`

- **Type:** string
- **REQUIRED.**
- **Maximum length:** 128 characters.
- **Constraints:** The `payment_reference` of the original AssetTransferRequest that
  this reversal targets. The receiving agent MUST locate the original transfer using
  this reference and verify that the transfer exists, is in status `"completed"`, and
  is within the reversal window. If the original transfer cannot be found, the agent
  MUST respond with error code `not_found` (ARSIA-Core.md §11.2) with description
  `"Original transfer not found for payment_reference: {reference}"`.

##### `reversal_reason`

- **Type:** string
- **REQUIRED.**
- **Maximum length:** 512 characters.
- **Constraints:** A human-readable explanation of why the reversal is being requested.
  This field is logged in the audit trail alongside the original transfer record. It
  MUST be specific enough for a compliance officer to understand the business
  justification for the reversal. Examples:
  - `"Client dispute — service not delivered as agreed"`
  - `"Duplicate payment detected — original reference: acme-2026-00041"`
  - `"Regulatory correction — original assessment invalidated"`

##### `requested_by`

- **Type:** string
- **Format:** Agent identifier (ARSIA-Core.md §3).
- **REQUIRED.**
- **Constraints:** The agent-id of the entity requesting the reversal. This MAY differ
  from the envelope's `from` field when the reversal is requested by a compliance
  officer or dispute resolution agent acting on behalf of the original parties. The
  `requested_by` agent MUST possess the `arsiaprotocol.assets.transfer.reverse` capability.

##### `reversal_amount`

- **Type:** number
- **OPTIONAL.**
- **Constraints:** The amount to reverse. When present and less than the original
  transfer's `amount`, this is a partial reversal. When present and equal to the
  original amount, this is a full reversal. The `reversal_amount` MUST NOT exceed the
  original transfer's `amount`. If `reversal_amount` exceeds the original amount, the
  agent MUST respond with error code `invalid_request` with description
  `"reversal_amount exceeds original transfer amount"`. When absent, the reversal
  defaults to a full reversal of the original amount.

#### 3.3.2 Reversal Constraints

Reversals are subject to time-based constraints that reflect the practical limits of
payment reversal in regulated financial systems.

**Full reversal window.** A full reversal (reversal of the entire original amount) is
only allowed within a provider-defined window. The RECOMMENDED default is T+1 — one
calendar day from the `settled_at` timestamp of the original transfer receipt. The
provider MAY define a shorter or longer window.

**Partial reversal window.** A partial reversal (reversal of less than the original
amount) is allowed within a longer window. The RECOMMENDED default is T+30 — thirty
calendar days from the `settled_at` timestamp. This longer window accommodates billing
disputes and service delivery adjustments that are common in B2B transactions.

**Expired window handling.** When a reversal request is received after the applicable
window has expired, the receiving agent MUST respond with error code `conflict`
(ARSIA-Core.md §11.2) with the following error details:

```json
{
  "payload": {
    "type": "arsiaprotocol.assets/transfer-reversal",
    "error": {
      "code": "conflict",
      "description": "Reversal window has expired for payment reference: acme-2026-00042",
      "details": {
        "reversal_window_exceeded": true,
        "window_days": 1,
        "settled_at": "2026-03-24T14:30:11.456Z",
        "window_expired_at": "2026-03-25T14:30:11.456Z"
      }
    }
  }
}
```

**Multiple reversals.** Multiple partial reversals of the same original transfer are
permitted, provided that the cumulative reversed amount does not exceed the original
transfer amount. The receiving agent MUST track cumulative reversals per
`payment_reference` and reject any reversal that would cause the total reversed amount
to exceed the original. A full reversal MUST NOT be issued if any partial reversal has
already been processed — the remaining unreversed amount is the maximum that can be
reversed.

**Reversal receipt.** The response to an AssetTransferReversal is a standard
AssetTransferReceipt (§3.2) with the following characteristics:

- `correlation_id`: MUST equal the `id` of the AssetTransferReversal message.
- `status`: `"completed"` if the reversal succeeded, `"failed"` if it did not.
- `payment_reference`: A NEW payment reference for the reversal, distinct from the
  original. The RECOMMENDED format is `"{original_reference}-REV-{sequence}"` (e.g.,
  `"acme-2026-00042-REV-1"`).
- `amount`: The amount actually reversed.
- `audit_id`: A NEW audit_id referencing the reversal audit record.

The reversal audit record MUST reference the original transfer's `audit_id` and
`payment_reference` to maintain the chain of custody.

#### 3.3.3 Complete AssetTransferReversal Example

```json
{
  "v": "1.0",
  "id": "f6a7b8c9-0123-4f01-e456-789012345678",
  "ts": "2026-03-25T09:15:00.000Z",
  "from": "agent:acme.compliance-officer",
  "to": "agent:acme.transfer-processor",
  "intent": "request",
  "expires_at": "2026-03-25T09:20:00.000Z",
  "capabilities": ["arsiaprotocol.assets.transfer.reverse"],
  "idempotency": {
    "key": "rev-acme-2026-00042-full",
    "expires_at": "2026-03-26T09:15:00.000Z"
  },
  "security": {
    "alg": "EdDSA",
    "kid": "agent:acme.compliance-officer#key1",
    "sig": "..."
  },
  "compliance": {
    "profile": "MIFID-II",
    "audit_required": true,
    "retention_days": 1825
  },
  "payload": {
    "type": "arsiaprotocol.assets/transfer-reversal",
    "version": "1.0",
    "args": {
      "original_payment_reference": "acme-2026-00042",
      "reversal_reason": "Client dispute — suitability assessment invalidated by senior compliance review. Original assessment RA-2026-5678 retracted.",
      "requested_by": "agent:acme.compliance-officer"
    }
  }
}
```

---

## 4. Escrow Mechanism

The escrow mechanism enables conditional value transfers — transfers where the value is
held by an intermediary until a specified condition is met. Escrow is a protocol-level
coordination pattern: ARSIA defines the signaling between agents (who holds, who
releases, what triggers release, what happens on timeout) while the actual holding of
funds is delegated to the payment provider.

This distinction is critical. ARSIA does not hold funds. ARSIA does not manage escrow
accounts. ARSIA defines the messages that coordinate the escrow lifecycle so that all
parties and auditors can observe escrow state transitions through protocol-level messages.
The payment provider that holds the escrowed value is identified in the
AssetTransferRequest's `provider` field. The provider's escrow implementation is outside
the scope of this specification.

### 4.1 Escrow Intent

The EscrowConditions object is included in the `escrow_conditions` field of an
AssetTransferRequest (§3.1.1). When present, it signals that the transfer should be
held in escrow rather than completed immediately.

#### EscrowConditions Object

The EscrowConditions object MUST contain the following fields. Unless marked OPTIONAL,
every field is REQUIRED.

##### `release_condition`

- **Type:** string
- **REQUIRED.**
- **Maximum length:** 512 characters.
- **Constraints:** A human-readable description of the condition that must be satisfied
  for the escrowed value to be released to the payee. This description is logged in
  the audit trail and is visible to all parties and oversight agents. It SHOULD be
  specific enough for a human auditor to evaluate whether the condition was actually
  met when the release trigger was received.
- **Examples:**
  - `"Delivery of dataset DS-2026-0053 confirmed by receiving agent"`
  - `"Code review completed and merged to production branch"`
  - `"Regulatory approval received from competent authority"`

##### `release_trigger`

- **Type:** string
- **REQUIRED.**
- **Maximum length:** 128 characters.
- **Constraints:** The ARSIA message `payload.type` value that triggers the release of
  the escrowed value when received by the escrow holder. When the escrow holder (the
  agent managing the escrow state) receives a message with `payload.type` equal to
  this value from the authorised `release_agent`, the escrow transitions from
  `ESCROWED` to `RELEASED` (§4.2).
- **Pattern:** Must conform to the payload.type pattern defined in ARSIA-Core.md §4.4.1.
- **Examples:**
  - `"com.example.delivery/confirmed"`
  - `"com.example.review/approved"`
  - `"eu.authority.approval/granted"`

##### `release_agent`

- **Type:** string
- **Format:** Agent identifier (ARSIA-Core.md §3).
- **REQUIRED.**
- **Constraints:** The agent-id of the agent authorised to send the release trigger
  message. ONLY this agent can release the escrow — release trigger messages from any
  other agent MUST be rejected with error code `forbidden` (ARSIA-Core.md §11.2). The
  `release_agent` MUST possess the `arsiaprotocol.assets.escrow.release` capability. The
  `release_agent` SHOULD be a different agent from the `from_agent` (the payer) and the
  `to_agent` (the payee) to ensure third-party verification. However, this is a
  RECOMMENDATION, not a REQUIREMENT — in some workflows the payee or a delegate of
  the payee may be the release agent.

##### `timeout_at`

- **Type:** string
- **Format:** RFC 3339 date-time with mandatory millisecond precision and UTC timezone
  designator.
- **REQUIRED.**
- **Constraints:** The absolute deadline for the escrow. If the escrow has not been
  released by `timeout_at`, the value MUST be returned to the sender automatically
  (§4.2, ESCROWED → RETURNED transition). The `timeout_at` value MUST be strictly
  greater than the message's `ts` value. The RECOMMENDED minimum timeout is 1 hour;
  the RECOMMENDED maximum timeout is 90 days. Implementations MAY enforce minimum and
  maximum timeout constraints.

##### `arbitration_agent`

- **Type:** string
- **Format:** Agent identifier (ARSIA-Core.md §3).
- **OPTIONAL.**
- **Constraints:** The agent-id of an agent that can be invoked if the escrow is
  disputed by either party. The arbitration process itself is OUT OF SCOPE for ARSIA —
  it is an implementation concern that varies by jurisdiction, industry, and contractual
  arrangement. ARSIA defines only the signaling: either party can send a message to the
  `arbitration_agent` to initiate a dispute, and the escrow transitions to the
  `DISPUTED` state (§4.2). If `arbitration_agent` is absent and a dispute arises, the
  escrow MUST timeout normally at `timeout_at` — there is no dispute mechanism.

#### 4.1.1 Complete EscrowConditions Example

```json
{
  "release_condition": "Delivery of dataset DS-2026-0053 confirmed by independent quality assurance agent",
  "release_trigger": "com.example.delivery/confirmed",
  "release_agent": "agent:acme.qa-inspector",
  "timeout_at": "2026-04-07T14:30:00.000Z",
  "arbitration_agent": "agent:europa.dispute-resolution"
}
```

### 4.2 Escrow Lifecycle

An escrow has exactly one initial state and three possible terminal states. The
lifecycle is deterministic: given the escrow conditions and the sequence of messages
received, the terminal state is uniquely determined.

```
                             +-----------+
                             |  ESCROWED |
                             +-----+-----+
                    +-------------+-+-------------+
                    |              |              |
              release_agent    timeout_at   either party
              sends trigger    reached      invokes
              message                       arbitration
                    |              |              |
                    v              v              v
              +----------+   +----------+   +----------+
              | RELEASED |   | RETURNED |   | DISPUTED |
              +----------+   +----------+   +----------+
```

#### 4.2.1 ESCROWED → RELEASED

**Trigger.** The `release_agent` (as specified in the EscrowConditions) sends a message
with `payload.type` matching the `release_trigger` value. The message MUST be signed by
the `release_agent`'s Ed25519 key. The message MUST include the `payment_reference` of
the escrowed transfer in its `payload.args` or `metadata` to link the release to the
specific escrow.

**Validation.** The escrow holder MUST verify:

1. The message's `from` field matches the `release_agent` in the EscrowConditions.
2. The message's `payload.type` matches the `release_trigger` in the EscrowConditions.
3. The message's EdDSA signature is valid.
4. The escrow has not already transitioned to a terminal state.
5. The current time is before `timeout_at`.

If any validation fails, the release MUST be rejected and the escrow remains in the
`ESCROWED` state.

**Result.** Upon successful validation:

1. The escrowed value is released to `to_agent`. The escrow holder instructs the
   payment provider to credit `to_agent`'s account.
2. A new AssetTransferReceipt is generated with `status: "completed"`, replacing the
   original `"escrowed"` receipt.
3. The `settled_at` field in the new receipt records the timestamp of the release.
4. An escrow release audit event is generated (§4.3).

#### 4.2.2 ESCROWED → RETURNED

**Trigger.** The current time reaches or exceeds the `timeout_at` value specified in
the EscrowConditions, and the escrow has not been released or disputed.

**Mechanism.** The escrow holder MUST implement a timeout monitoring mechanism that
detects when `timeout_at` has been reached. The specific implementation (polling, timer,
scheduled task) is outside the scope of this specification. The timeout check MUST
execute within 60 seconds of `timeout_at` — implementations SHOULD NOT allow timeouts
to be delayed by more than 60 seconds.

**Result.** Upon timeout:

1. The escrowed value is returned to `from_agent`. The escrow holder instructs the
   payment provider to reverse the debit from `from_agent`'s account.
2. A new AssetTransferReceipt is generated with:
   - `status`: `"failed"`
   - `failure_reason`: `"Escrow timeout — funds returned to sender"`
3. An automatic AssetTransferReversal is initiated internally (not requiring external
   reversal capability) to reverse the original debit.
4. An escrow timeout audit event is generated (§4.3).

#### 4.2.3 ESCROWED → DISPUTED

**Trigger.** Either the `from_agent` (payer) or the `to_agent` (payee) sends a dispute
message to the `arbitration_agent` specified in the EscrowConditions.

**Precondition.** The `arbitration_agent` field MUST be present in the EscrowConditions.
If `arbitration_agent` is absent, the `DISPUTED` state is unreachable — the escrow can
only transition to `RELEASED` or `RETURNED`.

**Dispute message format:**

| Field          | Value                                        |
|----------------|----------------------------------------------|
| `intent`       | `"request"`                                  |
| `to`           | The `arbitration_agent`                       |
| `payload.type` | `"arsiaprotocol.assets/escrow-dispute"`              |

The dispute message does not require a specific capability. Either party to the escrow
(`from_agent` or `to_agent` from the original AssetTransferRequest) MAY send a dispute.
The `arbitration_agent` MUST verify that the sender is a party to the escrow before
processing the dispute. Dispute messages from agents that are not a party to the escrow
MUST be rejected with error code `"forbidden"`.

The dispute message's `payload.args` MUST include:

- `payment_reference`: The `payment_reference` of the escrowed transfer.
- `dispute_reason`: A human-readable description of the dispute (maxLength 512).
- `disputed_by`: The agent-id of the disputing party.

**Result.** Upon receiving a valid dispute:

1. The escrow is frozen — the `timeout_at` deadline is suspended. The value remains
   held at the provider.
2. The escrow holder generates an AssetTransferReceipt update with status remaining
   `"escrowed"` but with a metadata field `{ "disputed": true }`.
3. An escrow dispute audit event is generated (§4.3).
4. The resolution of the dispute is OUT OF SCOPE for ARSIA. The `arbitration_agent`
   resolves the dispute through an implementation-defined process and communicates the
   resolution by either:
   - Sending the `release_trigger` message (acting as a delegate of the
     `release_agent`) → escrow transitions to `RELEASED`.
   - Sending a `"arsiaprotocol.assets/escrow-cancel"` message → escrow transitions to
     `RETURNED`.

**Note.** ARSIA logs the dispute event but does not define the arbitration process. The
protocol provides the signaling infrastructure; the dispute resolution logic is an
application-layer concern.

#### 4.2.4 ESCROWED → CANCELLED

**Trigger.** The agent that created the escrow (`from_agent`) sends a cancellation
message to the escrow holder.

**Precondition.** The escrow is in the `ESCROWED` state. Cancellation is only permitted
before the escrow transitions to a terminal state (`RELEASED`, `RETURNED`, or a resolved
`DISPUTED` state).

**Cancellation message format:**

| Field          | Value                                    |
|----------------|------------------------------------------|
| `intent`       | `"request"`                              |
| `to`           | The escrow holder agent                  |
| `payload.type` | `"arsiaprotocol.assets/escrow-cancel"`   |
| `capabilities` | `["arsiaprotocol.assets.escrow.cancel"]` |

The cancellation message's `payload.args` MUST include:

- `payment_reference`: The `payment_reference` of the escrowed transfer.

**Result.** Upon receiving a valid cancellation:

1. The escrowed value is returned to `from_agent`. The escrow holder instructs the
   payment provider to reverse the debit from `from_agent`'s account.
2. A new AssetTransferReceipt is generated with `status: "failed"` and
   `failure_reason: "Escrow cancelled by sender"`.
3. An `escrow_returned` audit event is generated (§4.3.3) with an additional
   `cancellation_reason` field.
4. The escrow transitions to the `RETURNED` terminal state.

**Access control.** Only the `from_agent` (the original payer who created the escrow)
MAY cancel an escrow. The escrow holder MUST verify that the sender of the cancellation
message matches the `from_agent` of the original AssetTransferRequest. Cancellation
requests from other agents MUST be rejected with error code `"forbidden"`.

### 4.3 Escrow Audit Trail

Every escrow state transition MUST generate an audit record. These audit records form a
complete, immutable history of the escrow lifecycle that can be reconstructed by
auditors and compliance officers.

#### 4.3.1 Escrow Creation

Generated when the initial AssetTransferReceipt with `status: "escrowed"` is produced.

| Audit Field        | Value                                                       |
|--------------------|-------------------------------------------------------------|
| `event_type`       | `"asset_transfer"`                                          |
| `sub_type`         | `"escrow_created"`                                          |
| `payment_reference`| The transfer's `payment_reference`                          |
| `amount`           | The escrowed amount                                         |
| `currency_or_unit` | The transfer's `currency_or_unit`                           |
| `from_agent`       | The payer's agent-id                                        |
| `to_agent`         | The payee's agent-id                                        |
| `release_agent`    | The authorised release agent's agent-id                     |
| `timeout_at`       | The escrow deadline                                         |
| `audit_id`         | UUID v4 — the audit record identifier                       |
| `timestamp`        | RFC 3339 — when the escrow was created                      |

#### 4.3.2 Escrow Release

Generated when the escrow transitions from `ESCROWED` to `RELEASED`.

| Audit Field        | Value                                                       |
|--------------------|-------------------------------------------------------------|
| `event_type`       | `"asset_transfer"`                                          |
| `sub_type`         | `"escrow_released"`                                         |
| `payment_reference`| The transfer's `payment_reference`                          |
| `released_by`      | The agent-id that sent the release trigger                  |
| `release_trigger`  | The payload.type of the release message                     |
| `original_audit_id`| The `audit_id` from the escrow creation record              |
| `audit_id`         | UUID v4 — new audit record identifier for the release event |
| `timestamp`        | RFC 3339 — when the release occurred                        |

#### 4.3.3 Escrow Timeout/Return

Generated when the escrow transitions from `ESCROWED` to `RETURNED`.

| Audit Field        | Value                                                       |
|--------------------|-------------------------------------------------------------|
| `event_type`       | `"asset_transfer"`                                          |
| `sub_type`         | `"escrow_returned"`                                         |
| `payment_reference`| The transfer's `payment_reference`                          |
| `timeout_at`       | The original deadline that was reached                      |
| `actual_timeout`   | RFC 3339 — the actual time the timeout was processed        |
| `original_audit_id`| The `audit_id` from the escrow creation record              |
| `audit_id`         | UUID v4 — new audit record identifier for the timeout event |
| `timestamp`        | RFC 3339 — when the return was processed                    |

#### 4.3.4 Escrow Dispute

Generated when the escrow transitions from `ESCROWED` to `DISPUTED`.

| Audit Field        | Value                                                       |
|--------------------|-------------------------------------------------------------|
| `event_type`       | `"asset_transfer"`                                          |
| `sub_type`         | `"escrow_disputed"`                                         |
| `payment_reference`| The transfer's `payment_reference`                          |
| `disputed_by`      | The agent-id of the disputing party                         |
| `dispute_reason`   | The human-readable dispute reason                           |
| `arbitration_agent`| The agent-id of the arbitration agent                       |
| `original_audit_id`| The `audit_id` from the escrow creation record              |
| `audit_id`         | UUID v4 — new audit record identifier for the dispute event |
| `timestamp`        | RFC 3339 — when the dispute was raised                      |

---

## 5. Capability Model for Financial Operations

The Assets primitive defines seven reserved capabilities in the `arsiaprotocol.` namespace. These
capabilities follow the grammar, hierarchy, and enforcement semantics defined in
ARSIA-Actions.md §1. Each capability has an assigned risk level that determines the
audit and human oversight requirements per ARSIA-Actions.md §2.2.

### 5.1 Reserved Capabilities

#### 5.1.1 `arsiaprotocol.assets.transfer.initiate`

**Purpose.** Authorises an agent to create an AssetTransferRequest — to express the
intent to transfer value from one agent to another.

**Risk level:** 5 (elevated).

**Audit requirement:** MUST be true. Every transfer initiation generates an audit record
regardless of the compliance profile.

**Human oversight requirement:** MAY be true. Oversight is recommended for currency
transfers above an implementation-defined threshold but is not mandated at this risk
level by the protocol. Operators SHOULD define threshold-based oversight policies.

**Typical holders:** Business logic agents (billing agents, procurement agents, risk
assessors), automated billing systems, subscription management agents.

**Constraints:**

- This capability authorises the creation of a transfer request. It does NOT authorise
  execution — execution occurs at the payment provider, which performs its own
  authorisation checks independently of ARSIA.
- Agents with this capability MUST declare the asset types they support in their action
  registry (ARSIA-Actions.md §2.3) by including an ActionDescriptor with
  `action_id: "arsiaprotocol.assets/transfer-request"` and `category: "financial"`.

#### 5.1.2 `arsiaprotocol.assets.transfer.approve`

**Purpose.** Authorises an agent to approve a pending asset transfer in a two-party
authorisation flow (§5.2).

**Risk level:** 7 (high).

**Audit requirement:** MUST be true.

**Human oversight requirement:** SHOULD be true. Agents with this capability SHOULD
represent human oversight roles — that is, agents through which a natural person
exercises approval authority. This mirrors the constraint on `arsiaprotocol.oversight.approve`
(ARSIA-Actions.md §1.4).

**Typical holders:** Compliance officers, human oversight agents, treasury approval
agents, senior compliance review agents.

**Constraints:**

- Two-party authorisation requires separation of duties: the agent that initiates a
  transfer (holds `arsiaprotocol.assets.transfer.initiate`) MUST NOT be the same agent that
  approves it (holds `arsiaprotocol.assets.transfer.approve`). The Authorization Server MUST
  enforce this separation — it MUST NOT issue a token that contains both
  `arsiaprotocol.assets.transfer.initiate` and `arsiaprotocol.assets.transfer.approve` in its scope.
- An agent MAY hold both `arsiaprotocol.assets.transfer.approve` and `arsiaprotocol.oversight.approve`
  if it serves as a general oversight agent for both financial and non-financial
  operations.

#### 5.1.3 `arsiaprotocol.assets.transfer.reverse`

**Purpose.** Authorises an agent to request reversal of a previously completed asset
transfer.

**Risk level:** 6 (elevated).

**Audit requirement:** MUST be true. Every reversal request generates an audit record
that references the original transfer.

**Human oversight requirement:** MAY be true. Oversight is recommended for reversals of
large amounts or reversals initiated more than 24 hours after the original transfer.

**Typical holders:** Compliance officers, dispute resolution agents, senior billing
agents, regulatory correction agents.

**Constraints:**

- Reversals are subject to the time-based constraints defined in §3.3.2.
- Reversal requests MUST be logged in the audit trail with the original transfer's
  `payment_reference` and `audit_id` for traceability.
- The `arsiaprotocol.assets.transfer.reverse` capability does NOT grant the ability to initiate
  new transfers — it is scoped exclusively to reversals.

#### 5.1.4 `arsiaprotocol.assets.escrow.create`

**Purpose.** Authorises an agent to create an escrow arrangement by including
`escrow_conditions` in an AssetTransferRequest.

**Risk level:** 5 (elevated).

**Audit requirement:** MUST be true.

**Human oversight requirement:** MAY be true.

**Typical holders:** Business logic agents (procurement agents, marketplace agents),
contract management agents, delivery coordination agents.

**Constraints:**

- Creating an escrow requires BOTH `arsiaprotocol.assets.transfer.initiate` AND
  `arsiaprotocol.assets.escrow.create`. The transfer initiation capability alone does not
  authorise escrow creation.
- The agent creating the escrow MUST specify a valid `release_agent` and `timeout_at`
  in the EscrowConditions.

#### 5.1.5 `arsiaprotocol.assets.escrow.release`

**Purpose.** Authorises an agent to trigger the release of escrowed value.

**Risk level:** 7 (high).

**Audit requirement:** MUST be true.

**Human oversight requirement:** SHOULD be true for currency escrows. For non-currency
escrows (tokens, entitlements, service units), human oversight is RECOMMENDED for
amounts above an implementation-defined threshold.

**Typical holders:** Delivery confirmation agents, quality assurance agents, compliance
agents, arbitration resolution agents.

**Constraints:**

- Only the `release_agent` specified in the EscrowConditions may release the escrow.
  Possessing this capability alone is necessary but not sufficient — the agent's
  identity MUST also match the `release_agent` field.
- The release message MUST be signed by the releasing agent's Ed25519 key.

#### 5.1.6 `arsiaprotocol.assets.escrow.cancel`

**Purpose.** Authorises an agent to cancel an escrowed transfer before the release
trigger is received, returning the value to the sender.

**Risk level:** 6 (elevated).

**Audit requirement:** MUST be true.

**Human oversight requirement:** MAY be true.

**Typical holders:** Business logic agents, compliance agents, escrow management agents.

**Constraints:**

- Cancellation is only permitted before the escrow transitions to a terminal state
  (RELEASED, RETURNED, or a resolved DISPUTED state).
- The cancellation message has `payload.type: "arsiaprotocol.assets/escrow-cancel"` and MUST
  include the `payment_reference` of the escrowed transfer.
- Cancellation generates an `escrow_returned` audit event (§4.3.3) with an additional
  `cancellation_reason` field.

#### 5.1.7 `arsiaprotocol.assets.audit.read`

**Purpose.** Authorises an agent to read the asset-specific audit trail — the audit
records generated by asset transfer operations.

**Risk level:** 3 (limited).

**Audit requirement:** SHOULD be true. Audit trail access is itself an auditable event.

**Human oversight requirement:** MAY be false. Read access does not modify state.

**Typical holders:** Auditors, compliance officers, regulatory agents, supervisory
authority agents.

**Constraints:**

- This capability grants read access to audit records generated by the Assets primitive
  only. It does NOT grant access to the general ARSIA audit trail (which requires
  `arsiaprotocol.audit.read` per ARSIA-Actions.md §1.4).
- Access tokens with this scope SHOULD have a short lifetime (RECOMMENDED maximum:
  300 seconds) to limit the window of exposure for sensitive financial audit data.
- The receiving agent MUST enforce record-level access controls: an agent with
  `arsiaprotocol.assets.audit.read` MAY be restricted to audit records within a specific
  date range, payment_reference range, or compliance profile.

### 5.2 Two-Party Authorisation for Financial Operations

When the risk level of a financial operation is ≥ 7 (per ARSIA-Actions.md §2.2, which
classifies risk levels 7-8 as "High Risk" and 9-10 as "Critical Risk"), the transfer
MUST require human oversight before execution. This requirement implements the principle
of dual control for financial operations: no single agent can both initiate and execute
a high-risk financial transaction.

The two-party authorisation flow builds on the human oversight mechanism defined in
ARSIA-Actions.md §3. The following steps describe the complete flow:

#### Step 1: Initiation

The initiating agent sends an AssetTransferRequest with `capabilities:
["arsiaprotocol.assets.transfer.initiate"]`. The request includes all transfer details (amount,
currency, parties, payment_reference, etc.).

#### Step 2: Risk Assessment

The receiving agent (the transfer processor) evaluates the risk level of the requested
operation. The risk assessment SHOULD consider:

- The `amount` and `asset_type` of the transfer.
- The compliance profile (if present).
- The risk level declared in the ActionDescriptor for `arsiaprotocol.assets/transfer-request`.
- Any operator-defined risk policies (amount thresholds, counterparty risk, etc.).

If the assessed risk level is ≥ 7, the receiving agent determines that human oversight
is required.

#### Step 3: Pending Approval

The receiving agent responds with a `pending_approval` message (ARSIA-Actions.md §3.2):

```json
{
  "intent": "pending_approval",
  "correlation_id": "<AssetTransferRequest.id>",
  "expires_at": "<approval deadline>",
  "payload": {
    "type": "arsiaprotocol.oversight/pending",
    "result": {
      "action_id": "arsiaprotocol.assets/transfer-request",
      "risk_level": 8,
      "reason": "Transfer amount EUR 1,500.00 exceeds threshold for automatic execution",
      "human_oversight_required": true,
      "summary": "Transfer EUR 1,500.00 from agent:acme.billing to agent:contoso.treasury via agent:europa.payments.sepa. Purpose: MiFID II suitability assessment fee."
    }
  }
}
```

The `pending_approval` message MUST include a human-readable `summary` of the transfer
to enable the approver to make an informed decision without consulting the original
request.

#### Step 4: Approval Decision

An agent with BOTH `arsiaprotocol.assets.transfer.approve` AND `arsiaprotocol.oversight.approve`
capabilities sends an `approval_decision` message (ARSIA-Actions.md §3.3):

```json
{
  "intent": "approval_decision",
  "correlation_id": "<pending_approval.id>",
  "payload": {
    "type": "arsiaprotocol.oversight/decision",
    "result": {
      "decision": "approved",
      "approver": "agent:acme.senior-compliance",
      "justification": "Transfer approved — within MiFID II client suitability parameters"
    }
  }
}
```

The `approval_decision` message MUST be signed by the approver's Ed25519 key. The
signature provides the possession factor for PSD2 Strong Customer Authentication (§6.3).

#### Step 5: Execution

Only after receiving an `approval_decision` with `decision: "approved"` does the
transfer processor forward the transfer to the payment provider for execution. The
transfer proceeds through the normal receipt flow (§3.2).

If the `approval_decision` has `decision: "rejected"`, the transfer processor responds
with an AssetTransferReceipt with `status: "failed"` and `failure_reason: "Transfer
rejected by human oversight — {justification}"`.

If no `approval_decision` is received before the `pending_approval`'s `expires_at`
deadline, the transfer processor responds with an AssetTransferReceipt with
`status: "failed"` and `failure_reason: "Approval timeout — no approval_decision
received within deadline"`.

#### Two-Party Authorisation and PSD2

This flow satisfies PSD2 Article 97 (Strong Customer Authentication) at the protocol
level. The two authentication factors provided are:

1. **Knowledge factor:** The approver's agent identity is verified through the
   `approval_decision` message's `from` field and the corresponding access token's
   `sub` claim. The Authorization Server has authenticated the approver's identity
   before issuing the token (ARSIA-Core.md §6.2).

2. **Possession factor:** The approver's Ed25519 private key is used to sign the
   `approval_decision` message. The signature proves that the approver possesses the
   private key corresponding to the public key published in their JWKS endpoint
   (ARSIA-Core.md §7.3). The private key is the possession factor.

The protocol does NOT mandate a third factor (inherence — biometric verification).
Implementations MAY add biometric verification in the approval user interface (e.g.,
fingerprint or face recognition before the approval agent sends the `approval_decision`).
This is an implementation concern, not a protocol concern.

---

## 6. Compliance Obligations

The Assets primitive carries specific compliance obligations that go beyond the general
ARSIA compliance framework. These obligations arise from three EU regulations that
directly govern financial operations: MiFID II (record-keeping), DORA (incident
reporting), and PSD2 (strong authentication). This section defines the normative
requirements for each.

### 6.1 MiFID II Audit Trail

For ALL AssetTransferRequest messages where one or more of the following conditions hold:

- The message's `compliance.profile` field is `"MIFID-II"`, OR
- The `asset_type` is `"currency"` AND either the `from_agent` or `to_agent` is an
  EU-regulated entity (as declared in their IdentityRecord per ARSIA-Identity.md §1.2),
  OR
- The `compliance.audit_required` field is `true` AND the transfer relates to
  investment services or activities as defined in MiFID II Annex I Section A

the receiving agent MUST generate a MiFID II audit record with the following fields.
All fields are REQUIRED unless marked OPTIONAL.

#### 6.1.1 MiFID II Audit Record Fields

| Field                    | Type       | Description                                                                                     | Source                                |
|--------------------------|------------|-------------------------------------------------------------------------------------------------|---------------------------------------|
| `audit_id`               | UUID v4    | Unique identifier for this audit record.                                                        | Generated                             |
| `message_id`             | UUID v4    | The `id` of the AssetTransferRequest message.                                                   | Envelope `id`                         |
| `receipt_message_id`     | UUID v4    | The `id` of the AssetTransferReceipt message. OPTIONAL — absent if the receipt has not yet been generated. | Receipt envelope `id`     |
| `from_agent`             | string     | The payer's agent-id.                                                                           | `payload.args.from_agent`             |
| `to_agent`               | string     | The payee's agent-id.                                                                           | `payload.args.to_agent`               |
| `amount`                 | number     | The requested transfer amount.                                                                  | `payload.args.amount`                 |
| `actual_amount`          | number     | The actual amount processed. OPTIONAL — absent if the transfer has not yet completed.            | Receipt `payload.result.amount`       |
| `currency_or_unit`       | string     | The currency code or unit identifier.                                                           | `payload.args.currency_or_unit`       |
| `asset_type`             | string     | The asset type enum value.                                                                      | `payload.args.asset_type`             |
| `payment_reference`      | string     | The unique payment reference.                                                                   | `payload.args.payment_reference`      |
| `provider_reference`     | string     | The external provider's transaction ID. OPTIONAL — absent if the provider has not yet responded. | Receipt `payload.result.provider_reference` |
| `initiated_at`           | RFC 3339   | When the transfer was initiated at the provider.                                                | Receipt `payload.result.initiated_at` |
| `settled_at`             | RFC 3339   | When the transfer was settled. OPTIONAL — absent if not yet settled.                            | Receipt `payload.result.settled_at`   |
| `status`                 | string     | The transfer status: `"pending"`, `"completed"`, `"failed"`, `"escrowed"`.                     | Receipt `payload.result.status`       |
| `failure_reason`         | string     | The reason for failure. OPTIONAL — present only when status is `"failed"`.                      | Receipt `payload.result.failure_reason` |
| `compliance_profile`     | string     | The compliance profile applied to this transfer.                                                | Envelope `compliance.profile`         |
| `data_residency`         | string     | The data residency zone. OPTIONAL.                                                              | Envelope `compliance.data_residency`  |
| `payload_hash`           | string     | SHA-256 hash of the RFC 8785 canonicalized payload. NOT the raw payload — the canonical form ensures deterministic hashing. | Computed                              |
| `human_oversight_status` | string     | `"not_required"`, `"pending"`, `"approved"`, `"rejected"`, or `"timeout"`. Indicates whether human oversight was triggered and its outcome. | Derived from oversight flow           |
| `approver_id`            | string     | The agent-id of the agent that approved the transfer. OPTIONAL — present only when oversight was required and approval was granted. | `approval_decision` envelope `from`   |
| `approval_timestamp`     | RFC 3339   | When the approval was granted. OPTIONAL — present only when `approver_id` is present.           | `approval_decision` envelope `ts`     |
| `exemption_reason`       | string     | SCA exemption justification. OPTIONAL — present when the transfer was exempt from Strong Customer Authentication per §6.3. Records the reason the exemption was applied (e.g., `"low_value_transaction"`, `"trusted_beneficiary"`, `"recurring_transaction"`). | Compliance officer |
| `created_at`             | RFC 3339   | When this audit record was created.                                                             | Generated                             |
| `updated_at`             | RFC 3339   | When this audit record was last updated. Updated when the receipt is received.                   | Generated                             |

#### 6.1.2 Retention

MiFID II Article 16(7), as implemented through Commission Delegated Regulation (EU)
2017/565, Article 72, requires investment firms to retain records of all services,
activities, and transactions for a period of at least five years.

**Retention period:** 1825 days (5 years) MINIMUM.

This retention period applies to:

- The MiFID II audit record itself.
- The AssetTransferRequest message (or its payload_hash if the full message is not
  retained).
- The AssetTransferReceipt message (or its payload_hash).
- The AssetTransferReversal message and its receipt, if applicable.
- All `pending_approval` and `approval_decision` messages related to the transfer.

Implementations MUST ensure that retained audit records are immutable — once written,
they MUST NOT be modified or deleted. Corrections MUST be implemented by appending a
new audit record that references the original (similar to accounting journal entries).

Implementations MUST support extending the retention period beyond 1825 days when
required by national transposition of MiFID II or by the competent authority's specific
requirements. The `retention_days` field in the compliance object (ARSIA-Core.md
§4.3.6) MAY specify a longer period.

#### 6.1.3 Data Residency

When agents are EU-regulated entities, the `compliance.data_residency` field SHOULD be
set to `"EU"`. This ensures that the audit records are stored within the European Union,
satisfying both MiFID II record-keeping requirements (which require records to be
accessible to competent authorities) and GDPR data transfer restrictions (which limit
transfers of personal data to third countries without adequate safeguards).

When `data_residency` is set, the message MUST be routed through a Compliance Broker
whose infrastructure resides within the declared zone (ARSIA-Core.md §9.2).

#### 6.1.4 Query Requirements

MiFID II audit records MUST be queryable by the following fields:

| Query Field          | Type    | Description                                               |
|----------------------|---------|-----------------------------------------------------------|
| `payment_reference`  | string  | Exact match on the payment reference.                     |
| `from_agent`         | string  | Exact match or prefix match on the payer's agent-id.      |
| `to_agent`           | string  | Exact match or prefix match on the payee's agent-id.      |
| `initiated_at`       | range   | Date range query on the transfer initiation timestamp.    |
| `compliance_profile` | string  | Exact match on the compliance profile.                    |
| `status`             | string  | Exact match on the transfer status.                       |
| `amount`             | range   | Range query on the transfer amount.                       |

These query capabilities ensure that competent authorities can retrieve records for
supervisory purposes as required by MiFID II Article 16(7) and Commission Delegated
Regulation (EU) 2017/565, Article 73 (obligation to provide records to competent
authorities on request).

The query interface format is defined in ARSIA-State.md §7.
Implementations MUST support at minimum the query fields listed above for MiFID II
audit records.

### 6.2 DORA Incident Reporting Hooks

The Digital Operational Resilience Act (DORA, Regulation 2022/2554/EU) requires
financial entities to establish and implement an ICT-related incident management process
(Article 17) and to report major ICT-related incidents to competent authorities
(Article 19). When a financial operation fails due to an infrastructure issue (as
opposed to a business logic issue), ARSIA agents MUST generate a structured incident
event that can be routed to the entity's DORA reporting system.

#### 6.2.1 Infrastructure vs. Business Logic Failures

Not all transfer failures trigger DORA incident reporting. The distinction is between
infrastructure failures (which indicate ICT-related incidents) and business logic
failures (which indicate normal operational outcomes).

**Infrastructure failures** — trigger DORA incident event:

| Failure Type           | Description                                                     | `incident_type` Value     |
|------------------------|-----------------------------------------------------------------|---------------------------|
| Provider timeout       | The payment provider did not respond within the timeout period. | `"provider_unavailable"`  |
| Network error          | TCP/TLS connection to the provider or broker failed.            | `"network_failure"`       |
| Database failure       | The agent's local database (audit trail, state) is unavailable. | `"database_failure"`      |
| Broker relay failure   | A Compliance Broker failed to relay the message.                | `"broker_failure"`        |
| TLS handshake failure  | TLS negotiation failed — certificate expired, revoked, or untrusted. | `"tls_failure"`      |
| Unknown infrastructure | An infrastructure failure that does not match the above types.  | `"unknown"`               |

**Business logic failures** — do NOT trigger DORA incident event:

| Failure Type            | Description                                                   |
|-------------------------|---------------------------------------------------------------|
| Insufficient funds      | The payer's account does not have sufficient balance.          |
| Invalid account         | The payee's account is invalid, closed, or unreachable.       |
| Compliance rejection    | The transfer was rejected by a compliance check.              |
| Amount limit exceeded   | The transfer amount exceeds a configured limit.               |
| Duplicate rejection     | The transfer was rejected as a duplicate (idempotency).       |
| Validation failure      | The request payload failed validation.                        |
| Authorization failure   | The requesting agent lacks the required capabilities.         |

The receiving agent MUST classify each failure as infrastructure or business logic and
MUST only generate DORA incident events for infrastructure failures.

#### 6.2.2 DORA Incident Event Format

When an infrastructure failure occurs during a financial operation, the agent MUST
generate a DORA incident event message with the following structure:

**Envelope configuration:**

| Field    | Value                                                                    |
|----------|--------------------------------------------------------------------------|
| `intent` | `"event"`                                                                |
| `to`     | The operator's DORA reporting agent (implementation-defined)             |

**Payload type:** `"arsiaprotocol.dora/incident"`

**Payload version:** `"1.0"`

**Payload data fields:**

##### `incident_type`

- **Type:** string
- **REQUIRED.**
- **Allowed values:** `"provider_unavailable"`, `"network_failure"`,
  `"database_failure"`, `"broker_failure"`, `"tls_failure"`, `"unknown"`
- **Constraints:** Classifies the nature of the ICT-related incident per DORA
  Article 17(1), which requires financial entities to "classify ICT-related incidents
  and determine their impact on the basis of criteria including the number of clients
  affected, the duration of the incident, the geographical spread, the data losses,
  the criticality of the services affected, and the economic impact."

##### `affected_service`

- **Type:** string
- **Format:** Agent identifier (ARSIA-Core.md §3).
- **REQUIRED.**
- **Constraints:** The agent-id of the component that failed. For provider timeouts,
  this is the payment provider's agent-id. For database failures, this is the agent's
  own agent-id. For broker failures, this is the Compliance Broker's agent-id.

##### `started_at`

- **Type:** string
- **Format:** RFC 3339 date-time with mandatory millisecond precision and UTC timezone
  designator.
- **REQUIRED.**
- **Constraints:** When the incident was first detected — typically the timestamp of
  the first failed operation.

##### `resolved_at`

- **Type:** string
- **Format:** RFC 3339 date-time with mandatory millisecond precision and UTC timezone
  designator.
- **OPTIONAL.**
- **Constraints:** When the incident was resolved. Absent if the incident is ongoing
  at the time the event is generated. A subsequent DORA incident event with the same
  `original_payment_reference` and a non-null `resolved_at` SHOULD be sent when the
  incident is resolved.

##### `estimated_impact`

- **Type:** string
- **REQUIRED.**
- **Maximum length:** 512 characters.
- **Constraints:** A human-readable description of the estimated impact of the incident.
  This description SHOULD include:
  - The number of affected transfers (if known).
  - The estimated financial impact (if known).
  - The services affected.
  - The geographic scope (if relevant).

  Examples:
  - `"SEPA Credit Transfer endpoint unreachable — 3 pending transfers affected, estimated EUR 15,000 delayed. Impact limited to EU payment processing."`
  - `"Local audit database unavailable — new transfers cannot be processed until database is restored. 0 transfers lost, all pending transfers preserved in message queue."`

##### `severity`

- **Type:** string
- **REQUIRED.**
- **Allowed values:** `"low"`, `"medium"`, `"high"`, `"critical"`
- **Constraints:** The severity classification of the incident. The mapping from
  incident characteristics to severity levels is implementation-defined, but the
  following RECOMMENDED guidelines apply:

  - **`"low"`**: Transient failure affecting a single transfer. The retry mechanism
    (ARSIA-Core.md §11.3) is expected to resolve the issue. No manual intervention
    required.
  - **`"medium"`**: Persistent failure affecting multiple transfers or a single
    high-value transfer. Manual investigation is required but no immediate escalation.
  - **`"high"`**: Sustained outage of a critical service (payment provider, database)
    affecting all transfers. Immediate manual intervention required.
  - **`"critical"`**: Total loss of payment processing capability. All financial
    operations are blocked. Immediate escalation to senior management and potential
    reporting to competent authority under DORA Article 19.

##### `original_payment_reference`

- **Type:** string
- **REQUIRED.**
- **Constraints:** The `payment_reference` of the transfer that triggered the incident
  detection. This field links the DORA incident event to the specific financial
  operation that was affected, enabling correlation between the DORA incident log and
  the MiFID II audit trail.

#### 6.2.3 DORA Incident Event Routing

DORA incident events MUST be routed to the operator's DORA reporting system. The
mechanism for this routing is implementation-defined. Common approaches include:

1. **Dedicated DORA reporting agent.** The operator deploys an agent
   (e.g., `agent:operator.dora-reporter`) that receives DORA incident events and
   translates them into the format required by the relevant competent authority.

2. **Compliance broker enrichment.** A Compliance Broker intercepts DORA incident
   events during message relay and forwards them to the operator's incident management
   system.

3. **Audit trail query.** DORA incident events are stored in the audit trail with
   `event_type: "dora_incident"` and can be queried by compliance officers and
   regulators through the audit trail query interface.

Regardless of the routing mechanism, the agent generating the DORA incident event MUST
also log the event in its local audit trail with `event_type: "dora_incident"`.

#### 6.2.4 DORA Reporting Obligations

DORA Article 19 requires financial entities to report major ICT-related incidents to the
relevant competent authority. The criteria for classifying an incident as "major" are
defined in DORA Article 18 and the associated Regulatory Technical Standards (RTS)
adopted by the European Supervisory Authorities (ESAs).

ARSIA does not classify incidents as "major" or "minor" — this classification is the
responsibility of the operator's DORA compliance function. ARSIA provides the structured
incident event data that feeds into the operator's incident classification process. The
`severity` field (§6.2.2) provides a protocol-level severity hint, but the final
classification is an operational decision that depends on factors outside the protocol's
scope (number of affected clients, duration, economic impact, etc.).

#### 6.2.5 Complete DORA Incident Event Example

```json
{
  "v": "1.0",
  "id": "a7b8c9d0-1234-4a12-f567-890123456789",
  "ts": "2026-03-24T14:30:35.789Z",
  "from": "agent:acme.transfer-processor",
  "to": "agent:acme.dora-reporter",
  "intent": "event",
  "security": {
    "alg": "EdDSA",
    "kid": "agent:acme.transfer-processor#key1",
    "sig": "..."
  },
  "payload": {
    "type": "arsiaprotocol.dora/incident",
    "version": "1.0",
    "data": {
      "incident_type": "provider_unavailable",
      "affected_service": "agent:europa.payments.sepa",
      "started_at": "2026-03-24T14:30:05.123Z",
      "resolved_at": null,
      "estimated_impact": "SEPA Credit Transfer endpoint unreachable — 1 pending transfer affected (EUR 1,500.00). Retry scheduled. No data loss.",
      "severity": "medium",
      "original_payment_reference": "acme-2026-00042"
    }
  }
}
```

### 6.3 PSD2 Strong Authentication

The revised Payment Services Directive (PSD2, Directive 2015/2366/EU), Article 97,
requires payment service providers to apply strong customer authentication (SCA) when
a payer initiates an electronic payment transaction. SCA requires that the authentication
is based on the use of two or more elements categorised as:

- **Knowledge:** Something only the user knows (e.g., password, PIN).
- **Possession:** Something only the user has (e.g., token, mobile device, private key).
- **Inherence:** Something the user is (e.g., fingerprint, facial recognition).

These elements MUST be independent — the breach of one does not compromise the others
— and MUST be designed to protect the confidentiality of the authentication data.

ARSIA provides two compliant approaches for satisfying PSD2 SCA at the protocol level.
Implementations MUST use one of these approaches for any financial capability with
risk_level ≥ 7 (§5.1).

#### 6.3.1 Option A: Human Oversight Flow

The `pending_approval` → `approval_decision` flow (ARSIA-Actions.md §3, §5.2 of this
specification) provides two authentication factors:

**Factor 1 — Knowledge.** The approver's agent identity is known to the Authorization
Server. The AS authenticates the approver before issuing the access token (ARSIA-Core.md
§6.2). The specific authentication mechanism is implementation-defined, but it MUST
include at least one knowledge factor (password, PIN, passphrase, or equivalent). The
`from` field of the `approval_decision` message carries the authenticated identity. The
`sub` claim of the access token confirms it.

**Factor 2 — Possession.** The approver's Ed25519 private key is used to sign the
`approval_decision` message (ARSIA-Core.md §5.1). The signature proves that the
approver possesses the private key corresponding to the public key published in their
JWKS endpoint (ARSIA-Core.md §7.3). The private key is stored in a secure enclave,
HSM, or file system with appropriate access controls — the specific storage mechanism is
implementation-defined, but the key MUST NOT be extractable in plaintext.

**Applicability.** Option A is RECOMMENDED for human-in-the-loop flows where a natural
person reviews and approves each financial operation. This is the typical pattern for
MiFID II-regulated operations where human oversight is already required by EU AI Act
Article 14.

**Limitations.** Option A does not provide an inherence factor. PSD2 Article 97(1)
requires "two or more" elements from the three categories — it does not require all
three. Two factors (knowledge + possession) satisfy the legal requirement.
Implementations MAY add biometric verification (fingerprint, face recognition) in the
approval user interface to provide a third factor, but this is not mandated by the
ARSIA protocol.

#### 6.3.2 Option B: Multi-Factor Token with `cnf` Claim

For automated flows where human-in-the-loop approval is not practical (e.g., high-
frequency trading, automated billing at scale), ARSIA supports an alternative SCA
mechanism based on hardware-bound tokens.

**Mechanism.** The access token issued by the Authorization Server contains a `cnf`
(confirmation) claim per [RFC 7800] that references a hardware-bound key. The
hardware-bound key is stored in a FIDO2/WebAuthn authenticator, a hardware security
module (HSM), or a Trusted Platform Module (TPM).

**Factor 1 — Knowledge.** The Authorization Server authenticates the agent operator
using a knowledge factor (password, PIN) before issuing the token.

**Factor 2 — Possession.** The DPoP (Demonstrating Proof-of-Possession) mechanism
defined in ARSIA-Identity.md §3.3 proves that the presenter of the token possesses the
hardware-bound key referenced in the `cnf` claim. The DPoP proof is a signed JWT that
includes the HTTP method, URL, and a nonce, preventing token replay.

**Token structure (informative):**

```json
{
  "iss": "https://as.acme.example.com",
  "sub": "agent:acme.auto-billing",
  "aud": "agent:acme.transfer-processor",
  "scope": "arsiaprotocol.assets.transfer.initiate",
  "cnf": {
    "jkt": "NzbLsXh8uDCcd-6MNwXF4W_7noWXFZAfHkxZsRGC9Xs"
  },
  "iat": 1711288200,
  "exp": 1711288500
}
```

The `cnf.jkt` value is the JWK Thumbprint [RFC 7638] of the hardware-bound key. The
DPoP proof accompanying the token proves possession of the corresponding private key.

**Applicability.** Option B is RECOMMENDED for automated flows that require SCA but
cannot include human-in-the-loop approval for each transaction. Implementations using
Option B SHOULD implement transaction risk analysis (TRA) per PSD2 Article 98 to
determine when full SCA is required versus when TRA exemptions apply.

**Limitations.** Option B requires hardware security infrastructure (FIDO2 authenticators,
HSMs, or TPMs). Implementations without hardware-bound keys MUST use Option A.

#### 6.3.3 SCA Exemptions

PSD2 and the associated Regulatory Technical Standards (Commission Delegated Regulation
(EU) 2018/389) define several exemptions from the SCA requirement. The following
exemptions are relevant to agent-assisted financial operations:

| Exemption                  | Condition                                          | Protocol Mapping                                    |
|----------------------------|----------------------------------------------------|-----------------------------------------------------|
| Low-value transactions     | Amount ≤ EUR 30 (cumulative ≤ EUR 100)             | risk_level < 7 → SCA not required                   |
| Trusted beneficiaries      | Payee is on the payer's trusted beneficiary list   | Implementation-defined trust list at the AS          |
| Recurring transactions     | Same amount, same payee, same frequency            | Idempotency key pattern + AS policy                  |
| Transaction risk analysis  | Low-risk based on TRA per Art. 98                  | Risk assessment at Step 2 of §5.2 returns < 7       |

When an SCA exemption applies, the transfer MAY proceed without the two-party
authorisation flow (§5.2). The exemption MUST be recorded in the audit trail with the
`human_oversight_status` set to `"not_required"` and the `exemption_reason` included in
the audit record's metadata.

---

## 7. Assets Conformance Tests

This section defines eight conformance tests for the Assets primitive. Implementations
claiming conformance with this specification MUST pass all eight tests. Test execution
is performed by the ARSIA Conformance Test Runner (`@arsia-protocol/conformance-test`).

Each test specifies a unique identifier, a human-readable description, preconditions,
the action to perform, and the expected result.

### Test ASSETS-01: Transfer Request → Receipt (Happy Path)

**Test ID:** `ASSETS-01`

**Description.** Verifies that a valid AssetTransferRequest for a currency transfer
produces a successful AssetTransferReceipt with all required fields.

**Preconditions:**

1. Agent A has the `arsiaprotocol.assets.transfer.initiate` capability in its access token.
2. Agent B is a transfer processing agent that accepts `arsiaprotocol.assets/transfer-request`
   payload type.
3. Agent B has a configured payment provider (or test stub) that succeeds.
4. The transfer does not require human oversight (risk_level < 7 for this test).

**Action:**

Agent A sends an AssetTransferRequest to Agent B with:

- `amount`: `100.00`
- `currency_or_unit`: `"EUR"`
- `asset_type`: `"currency"`
- `from_agent`: Agent A's agent-id
- `to_agent`: Agent C's agent-id (a valid payee)
- `payment_reference`: `"test-assets-01-001"` (unique)
- `description`: `"Conformance test ASSETS-01 — basic transfer"`
- `idempotency_key`: `"idem-assets-01-001"` (unique)

**Expected Result:**

1. Agent B responds with an AssetTransferReceipt (intent: `"response"`).
2. `correlation_id` equals Agent A's request `id`.
3. `payload.type` is `"arsiaprotocol.assets/transfer-receipt"`.
4. `payload.result.status` is `"completed"`.
5. `payload.result.payment_reference` is `"test-assets-01-001"`.
6. `payload.result.amount` is `100.00`.
7. `payload.result.currency_or_unit` is `"EUR"`.
8. `payload.result.initiated_at` is a valid RFC 3339 timestamp.
9. `payload.result.audit_id` is a valid UUID v4.
10. The message is signed (security.sig present and valid).

### Test ASSETS-02: Missing Idempotency Key Rejected

**Test ID:** `ASSETS-02`

**Description.** Verifies that an AssetTransferRequest without an idempotency key is
rejected with the appropriate error.

**Preconditions:**

1. Agent A has the `arsiaprotocol.assets.transfer.initiate` capability.
2. Agent B is a transfer processing agent.

**Action:**

Agent A sends an AssetTransferRequest to Agent B with all required fields EXCEPT the
`idempotency` object is absent from the envelope (no `idempotency.key`). The
`idempotency_key` field in `payload.args` is also absent.

**Expected Result:**

1. Agent B responds with an error message (intent: `"error"`).
2. `payload.error.code` is `"invalid_request"`.
3. `payload.error.description` contains a reference to the missing idempotency key
   (e.g., `"idempotency_key is required for asset transfer requests"`).
4. No transfer is initiated.
5. No audit record is generated for a successful transfer (an audit record for the
   rejected request MAY be generated).

### Test ASSETS-03: Duplicate Request Returns Original Receipt

**Test ID:** `ASSETS-03`

**Description.** Verifies that a duplicate AssetTransferRequest (same idempotency key)
returns the original receipt without re-executing the transfer.

**Preconditions:**

1. Agent A has the `arsiaprotocol.assets.transfer.initiate` capability.
2. Agent B is a transfer processing agent.
3. Agent A has previously sent an AssetTransferRequest with
   `idempotency_key: "idem-assets-03-001"` and received a successful
   AssetTransferReceipt.

**Action:**

Agent A resends the exact same AssetTransferRequest with
`idempotency_key: "idem-assets-03-001"` (same sender, same recipient, same
payload type, same key).

**Expected Result:**

1. Agent B responds with the SAME AssetTransferReceipt as the first request.
2. `payload.result.audit_id` matches the audit_id from the first response.
3. `payload.result.status` matches the status from the first response.
4. `payload.result.payment_reference` matches the first response.
5. The transfer is NOT executed again — the provider is NOT called a second time.
6. The response MAY have a different envelope `id` and `ts` (since it is a new
   response message) but the `payload.result` content MUST be identical.

### Test ASSETS-04: Escrow Create → Trigger Release → Completed

**Test ID:** `ASSETS-04`

**Description.** Verifies the complete escrow lifecycle: creation, release trigger, and
completion.

**Preconditions:**

1. Agent A has `arsiaprotocol.assets.transfer.initiate` and `arsiaprotocol.assets.escrow.create`
   capabilities.
2. Agent B is a transfer processing agent that supports escrow.
3. Agent D (the release agent) has the `arsiaprotocol.assets.escrow.release` capability.
4. The `release_trigger` is `"com.example.delivery/confirmed"`.
5. The `release_agent` is Agent D's agent-id.
6. `timeout_at` is set to 60 seconds from now (sufficient time for the test).

**Action:**

Phase 1: Agent A sends an AssetTransferRequest with `escrow_conditions`:

```json
{
  "release_condition": "Test delivery confirmed",
  "release_trigger": "com.example.delivery/confirmed",
  "release_agent": "agent:test.release-agent",
  "timeout_at": "2026-03-24T15:01:00.000Z"
}
```

Phase 2: Agent B responds with AssetTransferReceipt with `status: "escrowed"`.

Phase 3: Agent D sends a message to Agent B with
`payload.type: "com.example.delivery/confirmed"` and the `payment_reference` in its
payload.

**Expected Result:**

Phase 1-2:
1. Agent B responds with `payload.result.status` = `"escrowed"`.
2. `payload.result.audit_id` is a valid UUID v4.
3. An escrow creation audit event is generated with `sub_type: "escrow_created"`.

Phase 3:
4. Agent B generates a new AssetTransferReceipt with `status: "completed"`.
5. `payload.result.settled_at` is a valid RFC 3339 timestamp.
6. An escrow release audit event is generated with `sub_type: "escrow_released"`.
7. The `original_audit_id` in the release audit event matches the creation `audit_id`.

### Test ASSETS-05: Escrow Timeout → Funds Returned

**Test ID:** `ASSETS-05`

**Description.** Verifies that an escrow that is not released before the timeout
deadline results in automatic return of funds to the sender.

**Preconditions:**

1. Agent A has `arsiaprotocol.assets.transfer.initiate` and `arsiaprotocol.assets.escrow.create`
   capabilities.
2. Agent B is a transfer processing agent that supports escrow.
3. `timeout_at` is set to 5 seconds from now.

**Action:**

Phase 1: Agent A sends an AssetTransferRequest with `escrow_conditions` where
`timeout_at` is 5 seconds from now. No `arbitration_agent` is specified.

Phase 2: No release trigger message is sent. The test waits for the timeout to elapse.

**Expected Result:**

1. Agent B initially responds with `payload.result.status` = `"escrowed"`.
2. After the timeout elapses (within 60 seconds of `timeout_at`, per §4.2.2):
   - Agent B generates a new AssetTransferReceipt with `status: "failed"`.
   - `payload.result.failure_reason` is `"Escrow timeout — funds returned to sender"`.
3. An escrow timeout audit event is generated with `sub_type: "escrow_returned"`.
4. The funds are returned to `from_agent` (verified through the provider or audit
   trail).

### Test ASSETS-06: Human Oversight Required for High-Risk Financial Action

**Test ID:** `ASSETS-06`

**Description.** Verifies that a financial action with risk_level ≥ 7 triggers the
human oversight flow (pending_approval) rather than immediate execution.

**Preconditions:**

1. Agent A has the `arsiaprotocol.assets.transfer.initiate` capability.
2. Agent B is a transfer processing agent with an ActionDescriptor for
   `arsiaprotocol.assets/transfer-request` that has `risk_level: 9` and
   `human_oversight_required: true`.
3. No approval_decision is sent during the test.

**Action:**

Agent A sends an AssetTransferRequest to Agent B with:

- `amount`: `50000.00`
- `currency_or_unit`: `"EUR"`
- `asset_type`: `"currency"`
- Valid `payment_reference` and `idempotency_key`.

**Expected Result:**

1. Agent B responds with intent `"pending_approval"` (NOT `"response"`).
2. `correlation_id` equals Agent A's request `id`.
3. `payload.type` is `"arsiaprotocol.oversight/pending"`.
4. `payload.result.action_id` is `"arsiaprotocol.assets/transfer-request"`.
5. `payload.result.risk_level` is `9`.
6. `payload.result.human_oversight_required` is `true`.
7. `payload.result.summary` contains a human-readable description of the transfer.
8. No transfer is executed — the payment provider is NOT called.
9. `expires_at` is present and is a valid RFC 3339 timestamp in the future.

### Test ASSETS-07: MiFID II Audit Record Retention

**Test ID:** `ASSETS-07`

**Description.** Verifies that a completed transfer under the MIFID-II compliance
profile generates an audit record with all required MiFID II fields and that the record
is retained and queryable.

**Preconditions:**

1. Agent A sends an AssetTransferRequest with `compliance.profile: "MIFID-II"`.
2. The transfer completes successfully (status: `"completed"`).
3. At least 1 day has elapsed since the transfer (simulated or actual).

**Action:**

Query the audit trail for the `payment_reference` of the completed transfer.

**Expected Result:**

1. The audit record is present and retrievable.
2. The audit record contains ALL required MiFID II fields (§6.1.1):
   - `audit_id` (UUID v4)
   - `message_id` (matches the request's `id`)
   - `from_agent`, `to_agent`
   - `amount`, `currency_or_unit`, `asset_type`
   - `payment_reference`
   - `initiated_at`, `settled_at`
   - `status` = `"completed"`
   - `compliance_profile` = `"MIFID-II"`
   - `payload_hash` (SHA-256 of canonicalized payload)
   - `human_oversight_status`
   - `created_at`
3. The `retention_days` is ≥ 1825 (5 years).
4. The record is queryable by `payment_reference`, `from_agent`, `to_agent`,
   `initiated_at` range, and `compliance_profile`.

### Test ASSETS-08: DORA Incident Event on Infrastructure Failure

**Test ID:** `ASSETS-08`

**Description.** Verifies that when a payment provider is unreachable during a financial
operation, a DORA incident event is generated alongside the failed transfer receipt.

**Preconditions:**

1. Agent A has the `arsiaprotocol.assets.transfer.initiate` capability.
2. Agent B is a transfer processing agent.
3. The payment provider is configured to simulate a network failure (unreachable,
   timeout after configured duration).
4. Agent B is configured with a DORA reporting agent (`agent:test.dora-reporter`).

**Action:**

Agent A sends an AssetTransferRequest to Agent B with a valid currency transfer. The
payment provider call times out (simulated infrastructure failure).

**Expected Result:**

1. Agent B responds with an AssetTransferReceipt with:
   - `status`: `"failed"`
   - `failure_reason`: Contains a reference to the provider timeout.
2. Agent B ALSO generates a DORA incident event (intent: `"event"`) with:
   - `payload.type`: `"arsiaprotocol.dora/incident"`
   - `payload.data.incident_type`: `"provider_unavailable"`
   - `payload.data.affected_service`: The payment provider's agent-id.
   - `payload.data.started_at`: A valid RFC 3339 timestamp.
   - `payload.data.severity`: A valid severity value (`"low"`, `"medium"`, `"high"`,
     or `"critical"`).
   - `payload.data.original_payment_reference`: Matches the transfer's
     `payment_reference`.
3. The DORA incident event is routed to the configured DORA reporting agent.
4. The DORA incident event is logged in the audit trail with
   `event_type: "dora_incident"`.

---

## 8. References

### 8.1 Normative References

**[ARSIA-Core]**
ARSIA Protocol — Core Specification, Draft-01. Arsia Labs, March 2026.
- §4: Message Envelope
- §10: Idempotency
- §11: Error Handling
- §3: Agent Identifier Format
- §5: Message Security
- §6: Authorization
- §7: Discovery
- §9: Routing and Brokers
- §4.3.6: Compliance Field Definition

**[ARSIA-Actions]**
ARSIA-Actions — Actions Primitive Specification, Draft-01. Arsia Labs, March 2026.
- §1: Capability Model
- §2: Action Registry (§2.2: Risk Level to EU AI Act Mapping)
- §3: Human Oversight Signaling (pending_approval / approval_decision)
- §4: Action Execution Semantics

**[ARSIA-Identity]**
ARSIA-Identity — Identity Primitive Specification, Draft-01. Arsia Labs, March 2026.
- §1.2: IdentityRecord
- §3.3: DPoP for Proof of Possession

**[ARSIA-State]**
ARSIA-State — State Extension Specification, Draft-01. Arsia Labs, March 2026.
- §6: Compliance Profiles
- §7: Audit Trail Format

**[RFC 2119]**
Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels", BCP 14,
RFC 2119, DOI 10.17487/RFC2119, March 1997.

**[RFC 8174]**
Leiba, B., "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words", BCP 14,
RFC 8174, DOI 10.17487/RFC8174, May 2017.

**[RFC 3339]**
Klyne, G. and C. Newman, "Date and Time on the Internet: Timestamps", RFC 3339,
DOI 10.17487/RFC3339, July 2002.

**[RFC 9562]**
Davis, K., Peabody, B., and P. Leach, "Universally Unique IDentifiers (UUIDs)",
RFC 9562, DOI 10.17487/RFC9562, May 2024.

**[RFC 8785]**
Rundgren, A., Jordan, B., and S. Erdtman, "JSON Canonicalization Scheme (JCS)",
RFC 8785, DOI 10.17487/RFC8785, June 2020.

**[RFC 7800]**
Jones, M., Bradley, J., and H. Tschofenig, "Proof-of-Possession Key Semantics for
JSON Web Tokens (JWTs)", RFC 7800, DOI 10.17487/RFC7800, April 2016.

**[RFC 7638]**
Jones, M. and N. Sakimura, "JSON Web Key (JWK) Thumbprint", RFC 7638,
DOI 10.17487/RFC7638, September 2015.

**[ISO 4217]**
International Organization for Standardization, "Codes for the representation of
currencies", ISO 4217:2015.

### 8.2 Informative References

**[MiFID II]**
Directive 2014/65/EU of the European Parliament and of the Council of 15 May 2014 on
markets in financial instruments and amending Directive 2002/92/EC and Directive
2011/61/EU (recast). OJ L 173, 12.6.2014, p. 349–496.
- Article 16(7): Record-keeping obligations for investment firms.

**[MiFID II RTS 22]**
Commission Delegated Regulation (EU) 2017/565 of 25 April 2016 supplementing Directive
2014/65/EU of the European Parliament and of the Council as regards organisational
requirements and operating conditions for investment firms and defined terms for the
purposes of that Directive. OJ L 87, 31.3.2017, p. 1–83.
- Article 72: General record-keeping requirements.
- Article 73: Obligation to provide records to competent authorities.
- Article 74: Record of client orders and decisions to deal.
- Article 75: Record of transactions and order processing.
- Article 76: Record of cancellations and modifications.

**[DORA]**
Regulation (EU) 2022/2554 of the European Parliament and of the Council of 14 December
2022 on digital operational resilience for the financial sector and amending Regulations
(EC) No 1060/2009, (EU) No 648/2012, (EU) No 600/2014, (EU) No 909/2014 and (EU)
2016/1011. OJ L 333, 27.12.2022, p. 1–79.
- Article 17: ICT-related incident management process.
- Article 18: Classification of ICT-related incidents.
- Article 19: Reporting of major ICT-related incidents.

**[PSD2]**
Directive (EU) 2015/2366 of the European Parliament and of the Council of 25 November
2015 on payment services in the internal market, amending Directives 2002/65/EC,
2009/110/EC and 2013/36/EU and Regulation (EU) No 1093/2010, and repealing Directive
2007/64/EC. OJ L 337, 23.12.2015, p. 35–127.
- Article 11: Authorisation of payment institutions.
- Article 97: Strong customer authentication.
- Article 98: Regulatory technical standards on authentication and communication.

**[PSD2 SCA RTS]**
Commission Delegated Regulation (EU) 2018/389 of 27 November 2017 supplementing
Directive (EU) 2015/2366 of the European Parliament and of the Council with regard to
regulatory technical standards for strong customer authentication and common and secure
open standards of communication. OJ L 69, 13.3.2018, p. 23–43.

**[EMD2]**
Directive 2009/110/EC of the European Parliament and of the Council of 16 September 2009
on the taking up, pursuit and prudential supervision of the business of electronic money
institutions amending Directives 2005/60/EC and 2006/48/EC and repealing Directive
2000/46/EC. OJ L 267, 10.10.2009, p. 7–17.
- Article 2(2): Definition of electronic money.

**[MiCA]**
Regulation (EU) 2023/1114 of the European Parliament and of the Council of 31 May 2023
on markets in crypto-assets, and amending Regulations (EU) No 1093/2010 and (EU) No
1095/2010 and Directives 2013/36/EU and (EU) 2019/1937. OJ L 150, 9.6.2023, p. 40–205.

**[CSD Regulation]**
Regulation (EU) No 909/2014 of the European Parliament and of the Council of 23 July
2014 on improving securities settlement in the European Union and on central securities
depositories and amending Directives 98/26/EC and 2014/65/EU and Regulation (EU) No
236/2012. OJ L 257, 28.8.2014, p. 1–72.

**[Settlement Finality Directive]**
Directive 98/26/EC of the European Parliament and of the Council of 19 May 1998 on
settlement finality in payment and securities settlement systems. OJ L 166, 11.6.1998,
p. 45–50.

**[EU AI Act]**
Regulation (EU) 2024/1689 of the European Parliament and of the Council of 13 June 2024
laying down harmonised rules on artificial intelligence (Artificial Intelligence Act)
and amending Regulations (EC) No 300/2008, (EU) No 167/2013, (EU) No 168/2013, (EU)
2018/858, (EU) 2018/1139 and (EU) 2019/2144 and Directives 2000/14/EC, 2## 006/42/EC,
2009/48/EC, 2014/53/EU, 2014/68/EU and 2014/90/EU (Artificial Intelligence Act).
OJ L, 12.7.2024.
- Article 13: Transparency and provision of information to deployers.
- Article 14: Human oversight.

**[GDPR]**
Regulation (EU) 2016/679 of the European Parliament and of the Council of 27 April 2016
on the protection of natural persons with regard to the processing of personal data and
on the free movement of such data, and repealing Directive 95/46/EC (General Data
Protection Regulation). OJ L 119, 4.5.2016, p. 1–88.

---

*This specification is part of the ARSIA Protocol suite. For the complete set of
specifications, see https://arsiaprotocol.org/spec.*

---
ARSIA Protocol ([arsiaprotocol.org](https://arsiaprotocol.org)) | by [Arsia Labs](https://arsialabs.ai)
