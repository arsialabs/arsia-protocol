<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Draft-02 Conformance Report

Generated: 2026-08-05 · branch `draft-02` · reproducible via the commands shown.
Supersedes the stale Draft-01 report noted by audit finding M-22 (`results/` was
empty at the Draft-02 baseline).

## Executable suite

`python3 scripts/validate_vectors.py --format summary`

```
Schema                                        Valid Invalid  Pass  Fail
arsia-action-descriptor.schema.json              15       5    20     0
arsia-action-discovery-response.schema.json       1       1     2     0
arsia-asset-transfer-receipt.schema.json          6       0     6     0
arsia-asset-transfer-request.schema.json          9      18    27     0
arsia-asset-transfer-reversal.schema.json         0       1     1     0
arsia-audit-query-response.schema.json            1       1     2     0
arsia-audit-record.schema.json                   39       8    47     0
arsia-broker-discovery-request.schema.json        1       1     2     0
arsia-broker-entry.schema.json                    3       1     4     0
arsia-capability-descriptor.schema.json           1       1     2     0
arsia-capability-policy.schema.json               2       1     3     0
arsia-compliance-field.schema.json                4       5     9     0
arsia-discovery-response.schema.json              1       1     2     0
arsia-dora-incident.schema.json                   6       1     7     0
arsia-dpop-proof.schema.json                      2       1     3     0
arsia-escrow-conditions.schema.json               1       3     4     0
arsia-identity-record.schema.json                 4       1     5     0
arsia-jwk-entry.schema.json                       4       3     7     0
arsia-jwt-claims.schema.json                      4       2     6     0
arsia-message.schema.json                       205      59   264     0
arsia-mifid-audit-record.schema.json              5       1     6     0
arsia-onboarding-decision.schema.json             3       1     4     0
arsia-relay-attestation.schema.json               1       2     3     0
arsia-state-entry.schema.json                    19       2    21     0
arsia-state-operations.schema.json               75      16    91     0
arsia-websocket-frame.schema.json                 6       1     7     0
(skipped: runtime-only)                                        94      
TOTAL                                           418     137   649     0
```

- Meta-schema check: `TOTAL                                           418     137   649     0` (0 failures)
- Error-path verification: `Error-path mismatches: 0`
- Cryptographic verification (Draft-02 signing profile — envelope minus only
  `security.sig`): `Crypto: 83 vectors checked, 83 passed, 0 failed`

## Repository consistency

`python3 scripts/check_consistency.py` → `ALL CHECKS PASSED`

Covers: 31 schema meta-validations, uniform `$id` scheme + strict `$ref`
resolution, profiles-catalog validity, B-03/M-02 constant anti-regression,
retention-minimum and clock-skew parity, wire-2.0 coherence, capability-registry
parity (Actions §1.4 ↔ descriptor schema), prose-enum ↔ schema-enum parity
(legal_basis, human_oversight, ai_system_classification, audit event_type,
§11.2 error-code registry), `retention_days` narration guards (schema + vector
descriptions), duplicate-RTM-ID guard, and the cross-document **RTM drift
linter** (near-identical requirements with diverging modal strength/polarity or
embedded values; self-tested against synthetic drift so the detector can never
go silently dead).

## Runtime-rule harness

`python3 scripts/runtime_harness.py` → `ALL RUNTIME RULES PASSED`

Reference implementations + tests for the deterministic runtime algorithms
(calendar arithmetic, retention floors, capability matching, amount scale,
idempotency precedence, correlation/root chains, I-JSON range, content
exclusivity, effective oversight, issuer trust, session-scope audit precedence,
revocation under the JWKS cache ceiling) — the rules JSON Schema cannot express.

## Normative examples in spec prose

`python3 scripts/extract_examples.py` → `ALL EXAMPLES OK`

```
blocks=76 full=71 fragments=5 envelope-validated=9 failures=0
```

Every ```json block in spec/*.md parses as a standalone document or is a
recognized deliberate fragment (placeholder/ellipsis/property fragment);
envelope-shaped examples additionally validate against
`arsia-message.schema.json` with strict `$ref` resolution.

## Cross-reference integrity (M-14 anchor sweep)

`python3 scripts/check_links.py` → `ALL LINKS OK`

```
spec refs: explicit=500 bare=811 external=19; artifact refs: 391; dangling=0
```

Every `ARSIA-X §N.N` and bare `§N.N` reference in spec/*.md resolves to an
existing heading (RFC-section citations excluded); explicit spec references in
schema and profile-catalog description strings are verified as well.

## RTM counts (header-driven parser — reproducible)

`python3 scripts/rtm_counts.py`

```
file                          rows  ragged  MUST  MUSTNOT  SHOULD   MAY  no-schema&no-vector
ARSIA-Actions.rtm.md           328       0   165       35      50    27                  121
ARSIA-Assets.rtm.md            262       0   114       13      32    24                   93
ARSIA-Core.rtm.md              392       0   189       32      62    32                  161
ARSIA-Identity.rtm.md          259       0   140       23      31    21                  104
ARSIA-Routing.rtm.md           262       0   127       38      33    24                  127
ARSIA-State.rtm.md             400       0   176       57      45    35                  146

TOTAL rows: 1903
TOTAL no-schema-and-no-vector: 752
Modal totals: {'MUST': 911, 'MUST_NOT': 198, 'SHOULD': 253, 'MAY': 163, 'RECOMMENDED': 82, 'REQUIRED': 188, 'SHOULD_NOT': 12, 'OPTIONAL': 89, 'NOT_RECOMMENDED': 7}
MUST + MUST_NOT total: 1109
```

Note: earlier Draft-02 figures (1994 rows / 1153 MUST+MUST_NOT) double-counted 91
duplicate Assets rows — a stale Draft-01 listing left in 8-column form. The
duplicates are removed (DR-P8) and `check_consistency.py` now fails on duplicate
RTM requirement IDs.

Note: the historical figure "638 MUSTs without vector" is NOT republished — it was
not reproducible (audit §8); the numbers above are computed from the current RTMs
by `scripts/rtm_counts.py`.

## Skip accounting

94 runtime-only vectors, individually classified in
`docs/draft-02-skip-classification.md`. No failure is hidden by a skip: the suite
reports 0 failures with every skip carrying a category, verification method, and
residual-risk note.

## Conformance criteria (Core §12.3)

Full conformance = 100% of the executable checks above + the documented
integration conformance tests (CORE-*/ACTIONS-*/IDENTITY-*/STATE-*/ROUTING-*/
ASSETS-*) executed against a deployment + documented verification procedures for
deployment/operational/legal requirement classes. The runner is fully in-repo; no
external unversioned package participates in the criteria (resolves audit M-18).
