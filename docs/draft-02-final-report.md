<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Draft-02 Final Findings-Resolution Report

Closes the remediation of the Draft-01 audit (`docs/auditoria-spec-draft-01.md`,
SHA-256 `abc61eba97d59c1bb319fc637524171c8377d205170e92e55e711aa437252472`,
committed at `e557f83`). Per-finding detail (evidence, alternatives, impacts,
residual risks) lives in `docs/draft-02-decisions.md` (DR-*); reproduction
evidence in `docs/draft-02-findings-status.md`. The audit document itself is
preserved unmodified — resolution is recorded here, not by rewriting history.

**Verification (all reproducible):** `validate_vectors.py` 649 vectors / 0 fail;
`--check-meta`, `--check-errors` clean; `--check-crypto` 83/83 under the v2
signing profile; `check_consistency.py` ALL PASSED; `runtime_harness.py` R1–R13
ALL PASSED; `rtm_counts.py` 1903 rows / 1109 MUST+MUST_NOT (earlier figures
1994/1153 counted 91 duplicate Assets rows — see DR-P8; figures of 1108 predate
the ROUTE-§2.2.2-12 heartbeat SHOULD→MUST harmonization). Wire version: 2.0.

**Post-release-candidate sweep (2026-07-29, DR-P8):** an evidence-level double
check of every resolution found secondary sites still restating superseded rules
(12 material + a set of minor residuals — worst: Routing's transport table
re-authorizing the M-25 header override; the SCA overclaim surviving in Assets
§6.3; onboarding-decision vectors still on the abolished intent). All fixed,
two new CI guards added; per-item detail in DR-P8.

## Blockers (8/8 resolved)

| ID | Resolution | Record |
|----|-----------|--------|
| B-01 | correlation = immediate causal parent; NEW required `root_request_id`; unknown/duplicate/late rules | DR-B01 |
| B-02 | global reject, no clamp; typed calendar durations end-to-end | DR-D1 |
| B-03 | 1827 standardized; anti-regression check in CI | DR-B03 |
| B-04 | Actions §1.4 = closed normative registry (+echo/health/onboarding.evaluate/broker.use) | DR-B04 |
| B-05 | dual authorization + hash-bound relay attestation; Core §6.4 unchanged; bypass detectable | DR-D2 |
| B-06 | canonical oversight contract only (`payload.args`; approved\|denied / denied\|expired) | DR-B06 |
| B-07 | one matching algorithm (Actions §1.2); reserved namespace never wildcard-matched | DR-B07 |
| B-08 | JSON value semantics; decimal-string amounts; I-JSON range rule | DR-D4 |

## High findings (22/22 resolved; 3 by the blocker decisions)

| ID | Resolution | Record |
|----|-----------|--------|
| A-01 | Core §6.6 registry-based agent resolution (deterministic, fail-closed) | DR-A17/A01-MIN |
| A-02 | per-intent signature matrix + compliance-event MUST-sign carve-out | DR-P2 |
| A-03 | strict mode defined; `strict_compliance` discovery flag (+schema) | DR-P2, DR-P7 |
| A-04 | certificate codes registered in Core §11.2 (401, non-retryable) | DR-P2 |
| A-05 | declared vs resolved profile + retention resolution fields in audit records | DR-D1, DR-P2 |
| A-06 | `counterparty_owner_id`; append-record backfill | DR-P2 |
| A-07 | version-handling model: exact-minor schemas + runtime wire tolerance | DR-A07-MIN/D5 |
| A-08 | hard content-field exclusivity (prose aligned to schema) | DR-P2 |
| A-09 | Rule 3 checks EFFECTIVE oversight; schema conditional removed | DR-P2 |
| A-10 | MiFID records immutable; `updated_at` removed (prose + schema + vectors) | DR-P2, DR-P5 |
| A-11 | subsequent-receipt delivery mechanism (new request + idempotency + fallback) | DR-P2 |
| A-12 | `regulated_entity` IdentityRecord field + deterministic trigger fallback | DR-P2 |
| A-13 | audit_required overrides session no-audit (both paths tested, harness R12) | DR-P2, DR-P7 |
| A-14 | threat model +6 adversaries with explicit residuals; Routing §5.1/§5.2 modal clash resolved | DR-P2 |
| A-15 | resolved by D1 (floors runtime, schemas format-only) | DR-D1 |
| A-16 | signing input = envelope minus only `security.sig`; staged pipeline; alg/key coherence | DR-D3/D5-REGEN |
| A-17 | Core §6.5 issuer trust configuration; `iss` validated; fail closed (harness R11) | DR-A17/A01-MIN, DR-P7 |
| A-18 | 3600 s cache ceiling; JWKS-removal revocation; key-revocation event; fetch-timestamp audit (harness R13) | DR-P2, DR-P7 |
| A-19 | PSD2/SCA claims requalified (controls, not satisfaction; subject to legal review) | DR-P2 |
| A-20 | resolved by D4 (fixed ISO 4217 scale; JPY/EUR/KWD vectors) | DR-D4 |
| A-21 | GDPR language conditional; linkability assessed in context | DR-P2 |
| A-22 | tamper-evidence scope statement (detected vs not); overclaiming prohibited | DR-P2 |

## Medium findings (31/31 closed)

M-01 (D1), M-02 (P731D), M-03 (kid form), M-04 (field/path), M-05 (D2
unification), M-06 (operational-log classification), M-07 (escrow taxonomy +
field names), M-08 (scope table + shared-vs-grant), M-09 (`arsiaprotocol.meta/`),
M-10 (sync-response list), M-11 (closed residency registry), M-12 (UUID case),
M-13 (wildcard audience removed), M-14 (4/5 anchors fixed; item 2 NOT-REPRODUCED
in this tree), M-15 (`supported_versions`; single-entry migration), M-16
(onboarding decision payload), M-17 (universal receipt audit record), M-18
(in-repo runner + CORE-COMPLIANCE-04..09), M-19 (extension fields in prose),
M-20 (risk_level ≥ 0), M-21 (one async mechanism, two surfaces), M-22 (partial:
results half superseded; §2.1.10 contradiction fixed), M-23 (per-message enum),
M-24 (ALREADY-FIXED upstream), **M-25 (RECLASSIFIED HIGH; signed key
authoritative)**, M-26 (delivery terminology), M-27 (`ict_incident` + candidate
trigger), M-28/M-29 (anchors verified: §5.2/§4.4), M-30 (role model), M-31
(folded into D1: P6M calendar). → DR-D1/D2/P3.

## Low findings (8/8 individually closed)

X-01 (org-segment), X-02 (version pattern), X-03 (`arsiaprotocol.` wording),
X-04 (§10.4 rewrite + AEAD), X-05 (personal or sensitive), X-06 (stale phrase),
X-07 (RTM summaries regenerated from actual rows; Routing gains a coverage
section; Draft-02 delta tables added to all six), X-08 (English SHOULD +
localized details). → DR-P3, Phase 6.

## New defects found and fixed during remediation (not in the audit)

N-01 (audit-query-response drift → `$ref`), N-02 (catalog schema-invalid →
fixed + CI-validated), N-03 (float `multipleOf` → decimal strings), N-04
(descriptor-rule drift → registry rule + `$ref`), N-05 (relative `$id` →
uniform v2.0 scheme, strict-resolver verified), N-06 (Art. 9(2) bases in
prose), N-07/N-08/N-09 (descriptions/dead rule/timestamp), N-10 (3-decimal
currencies → D4); plus the 17 adversarial-review findings of DR-P7 (all fixed).

## Hypotheses

H1: extension profiles via reverse-domain namespacing (defined). H2: gaps fixed
(deterministic default, proactive discovery, uniform rules). H3: no new
mechanism needed after B-01 (assessed). H4: bitemporality deferred, recorded as
known limitation. → DR-H.

## Compatibility

Draft-02 is breaking (wire 2.0): signing input, `retention` durations,
decimal-string amounts, `root_request_id`, `authorization` binding, broker
model, enum changes. Full mapping: `docs/draft-02-migration-guide.md`.
Residual risks: `docs/draft-02-known-limitations.md`. Release status:
`docs/draft-02-release-checklist.md` (all 26 acceptance criteria met; owner
actions listed). Work is uncommitted pending the owner's instruction; no push,
publication, licence, or governance change was made.
