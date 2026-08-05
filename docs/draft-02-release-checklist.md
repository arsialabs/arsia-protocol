<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Draft-02 Release Checklist

Acceptance criteria from the remediation plan (26 items), with status and the
verifying artifact. Re-verify by running the six commands in
`results/draft-02-conformance-report.md`.

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | B-01..B-08 resolved | ✅ | DR-B01/B03/B04/B06/B07, DR-D1/D2/D3-D5/D4 in docs/draft-02-decisions.md |
| 2 | No known reproducible blocker | ✅ | Phase-7 adversarial review: 17 findings (3 blocking) ALL FIXED (DR-P7) |
| 3 | A-01..A-22 resolved or formally accepted | ✅ | DR-A17/A01-MIN, DR-P2; residuals in known-limitations |
| 4 | M-25 severity reassessed | ✅ | RECLASSIFY→HIGH, fixed (Core §10.4) |
| 5 | M-27 fixed per its nuance | ✅ | `ict_incident` rename + candidate trigger |
| 6 | 8 low findings individually tracked | ✅ | findings-status matrix, X-01..X-08 rows |
| 7 | Six documents aligned | ✅ | check_consistency.py; adversarial pass |
| 8 | Schemas and prose agree | ✅ | 649 vectors 0 fail; deliberate runtime delegations classified |
| 9 | Normative examples valid | ✅ | scripts/extract_examples.py (71 full parse, 9 envelope-validated, 5 fragments, 0 failures; in CI) |
| 10 | Profiles and tables agree | ✅ | check_consistency.py retention/clock-skew parity |
| 11 | Registries and enums consistent | ✅ | capability-registry parity check; oversight enums unified |
| 12 | All executable tests pass | ✅ | 649/0; crypto 83/83; harness R1-R13; consistency |
| 13 | No failure hidden by a skip | ✅ | skip-classification doc, 94/94 accounted |
| 14 | Skips classified and justified | ✅ | docs/draft-02-skip-classification.md |
| 15 | Critical security/interop reqs have +/− tests | ✅ | per-DR test lists; harness R1-R13 |
| 16 | MUST/MUST_NOT traced | ✅ | RTMs + Draft-02 delta sections; rtm_counts.py (1109 MUST/MUST_NOT, deduplicated — DR-P8) |
| 17 | Non-automatable reqs have verification method | ✅ | skip doc + Core §12.3 gates (inspection/evidence classes) |
| 18 | RTM counts reproducible | ✅ | scripts/rtm_counts.py (1903 rows, deduplicated — DR-P8) + duplicate-ID guard in check_consistency.py |
| 19 | Conformance runner verifiable | ✅ | in-repo runner (M-18 closed) |
| 20 | results/ updated | ✅ | results/draft-02-conformance-report.md |
| 21 | Cross-references valid | ✅ | scripts/check_links.py (1,297 spec + 389 artifact refs, 0 dangling; in CI) + adversarial pass |
| 22 | Threat model covers six documents | ✅ | Core §13.1 adversaries 1-12 |
| 23 | Audit/residency limitations honest | ✅ | known-limitations §1-6 |
| 24 | Unverified legal claims qualified | ✅ | A-19/A-21/M-30 language; limitations §13 |
| 25 | Changelog + migration guide | ✅ | CHANGELOG.md; docs/draft-02-migration-guide.md |
| 26 | Residual risks recorded | ✅ | known-limitations; per-DR residual sections |

## Pre-release actions (owner)

- [ ] Review and approve the Draft-02 diff (`git diff 9064744..HEAD` after commit).
- [ ] Decide commit/tag strategy (work is intentionally uncommitted pending your instruction).
- [ ] Legal review of the qualified regulatory statements (limitations §13).
- [ ] Execute the integration-class conformance tests against a reference deployment before any public conformance claim.
- [ ] No push/publication/licence/governance change is part of this checklist (explicitly out of scope per the mission).
