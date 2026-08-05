<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Compliance Profile Gap Analysis — Candidate EU Profiles Beyond the Draft-02 Seven

**Date:** 2026-07-29 · **Status:** informative — no decision taken; adding any
profile is a normative change (GitHub Issue before PR, CONTRIBUTING.md §4) and its
regulatory statements join the owner's legal-review queue.

## Context

Draft-02 ships 7 normative profiles (`profiles/arsia-compliance-profiles.json`
v2.0.0, defined in ARSIA-State §6): `GDPR-STANDARD`, `EU-AI-ACT-HIGH-RISK`,
`EU-AI-ACT-LIMITED-RISK`, `MIFID-II`, `PAC-AGRICULTURE`, `DSA-VLOP`, `DORA`.
Coverage is strong for financial services (MiFID II + DORA), AI-system
obligations, platform moderation, and agriculture — and generic for GDPR. This
document records the gap analysis of widely used EU regimes not yet covered,
ranked by expected demand from real AI-agent deployments.

## Tier 1 — highest-demand gaps

| Candidate | Regulation | Rationale | Likely retention floor |
|---|---|---|---|
| `PSD2-PAYMENTS` (or PSR when it lands) | PSD2 Art. 94-97 / upcoming PSR | The most conspicuous gap. Agentic payments are the fastest-growing agent use case (the AP2 territory). ARSIA already carries the full SCA machinery (Assets §5-§6.3) and PSD2 obligations currently surface only *inside* the MIFID-II profile — a PSP that is not a MiFID firm has no profile to declare. | `P1827D` (5 years, AML-aligned), `retention_basis: conservative_policy` pending legal review |
| `AML-KYC` | AMLD5 / new AMLR (record-keeping, Art. 77 class) | Inseparable companion of payments: any agent doing financial onboarding or value transfer hits CDD/KYC. **Spec impact beyond the catalog:** the 5-year retention is anchored at the **end of the business relationship** — an anchor the D1 model (anchor = creation/registration instant of the retention-bearing object) cannot express today. Requires a `retention_anchor` extension decision in Core §4.3.6.4 before the profile can be honest. | `P1827D` from relationship end |
| `NIS2` | NIS2 Art. 21/23 | DORA is the financial-sector *lex specialis* of NIS2; essential/important entities in energy, transport, health, and digital infrastructure have no profile. The `ict_incident` candidate-event model (M-27) generalizes almost directly; the 24 h early-warning / 72 h notification cadence maps onto the existing `required_within_24h` oversight mode. | `P1827D` (`conservative_policy` — common practice, not a literal statutory floor) |

## Tier 2 — strong sectoral candidates

| Candidate | Regulation | Rationale |
|---|---|---|
| `MICA-CASP` | MiCA Art. 68 | Crypto-asset service providers: 5-year record-keeping; the Assets primitive (transfer/escrow/reversal) serves nearly unchanged. Natural adjacency for MIFID-II adopters. |
| `EIDAS-IDENTITY` | eIDAS 2.0 / EUDI Wallet | Agents verifying identity or consuming wallet attestations. Pairs with the Identity primitive and the 6-phase onboarding — likely lands as an Identity-spec extension more than a pure profile. |
| `HEALTH-EHDS` | EHDS + GDPR Art. 9 | Health agents: special-category data (the Art. 9(2) `legal_basis` values already exist post-N-06), strong oversight. Caveat: medical-record retention is **national** (10-30 years) — any floor would be `retention_basis: technical_default` with a conservative value, never a regulatory claim. |

**Lower priority:** Data Act / DGA (access/porting obligations, little wire-level
surface), ePrivacy (still a directive), CRA / GPSR (product security, not
message-level compliance).

## Architectural observations (recorded so they are not re-derived)

1. **The cost of a profile is not the JSON — it is D1 honesty.** Every new profile
   needs a defensible `retention_basis` / `retention_reference` /
   `retention_interpretation`, a justified oversight mode, and a clock-skew
   choice. `AML-KYC` additionally needs a spec decision (relationship-end
   retention anchor). The catalog being small is a feature, not a backlog.
2. **H1 already provides the escape valve.** Operators can publish reverse-domain
   extension profiles (e.g. `com.acme.aml-kyc`) today, discoverable via
   `compliance_profiles_supported`, without any spec change (Core §4.3.6.1).
   The bar for entering the canonical catalog should be demonstrated horizontal
   demand — not regulatory completeness.
3. **Governance path.** New profile ⇒ GitHub Issue first (CONTRIBUTING.md §4) ⇒
   decision record ⇒ catalog + State §6 prose + schemas + vectors + RTM rows in
   one consistent change (the CI parity checks will enforce the catalog↔prose
   agreement) ⇒ qualified regulatory language, subject to legal review.

## Recommended sequence (if and when expansion is decided)

1. `PSD2-PAYMENTS` — machinery ready, maximum demand.
2. `NIS2` — cheap generalization of the DORA/incident machinery.
3. `AML-KYC` — highest value, but carries the retention-anchor spec decision.
4. Then `MICA-CASP`, `EIDAS-IDENTITY`, `HEALTH-EHDS` by adoption signal.
