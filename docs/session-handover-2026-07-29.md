<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Session Handover — 2026-07-29

**Tree state:** branch `draft-02`, **everything uncommitted** (deliberate — the
owner decides commit/tag strategy). Baseline commit `e557f83`. All repository
content is English; this handover summarizes the session that took Draft-02 from
"release candidate" to "evidence-verified, guard-hardened release candidate".

## What this session did, in order

1. **Owner-requested double check** of the Draft-02 remediation against the plan
   (`docs/draft-02-implementation-plan.md`). Accounting confirmed (69 findings, 3
   closed by status); four parallel verification passes over ~60 findings found
   ~12 material secondary-site residuals (fix landed at the primary site, the old
   rule survived elsewhere) and 1 unfixed defect (N-07).
2. **DR-P8 sweep** (`docs/draft-02-decisions.md`): all residuals fixed. Worst
   cases: Routing's transport table still granting the unsigned `Idempotency-Key`
   override (M-25, reclassified HIGH); SCA overclaim surviving in Assets §1.1.8/
   §6.3 (A-19); onboarding-decision vectors still on the abolished
   `approval_decision` intent (M-16 — schema+vectors migrated, ITV-03/04
   re-signed); Assets RTM double-counting 91 duplicate rows → published counts
   corrected to **1903 rows / 1109 MUST+MUST_NOT**; ITV-559 declared `P730D`
   under DSA-VLOP (floor `P731D`) → fixed.
3. **Item-by-item closure pass** over the entire source audit
   (`docs/auditoria-spec-draft-01.md`): every finding, hypothesis, §5.2 cluster,
   and §6 NOT-VERIFIED item verified de facto in the tree, with a relation graph
   and orphan sweep → **`docs/draft-02-closure-graph.md`** (4 further orphans
   found and fixed).
4. **DR-P9 — prose-consistency guards** in `scripts/check_consistency.py` (no new
   tool): prose-enum ↔ schema-enum parity (legal_basis, human_oversight,
   ai_system_classification, audit event_type, §11.2 error codes) + the
   **cross-document RTM drift linter** (near-identical requirements with
   diverging modal/values; self-tested against synthetic drift every run). Its
   first run found a real surviving contradiction — Core §8.2 heartbeat MUST vs
   Routing §2.2.2 SHOULD — fixed (the MUST governs).
5. **Surface-doc alignment**: README (badge, profile table now duration-typed
   incl. `P731D`, RTM row count), FAQ (Draft-02 signing profile answer, counts),
   getting-started (v2 signing wording, vector counts, SDK-version caveat),
   CHANGELOG count, test-vectors README format counts, CLAUDE.md (full CI
   battery, guard discipline, traceability pointers).
6. **Profile gap analysis** recorded in
   `docs/compliance-profile-gap-analysis.md` (informative; no decision).

## Verification state (all reproducible, all green at handover)

```
python3 scripts/validate_vectors.py --check-meta --check-errors --check-crypto
  → 649 vectors, 0 fail; crypto 83/83 (v2 signing profile)
python3 scripts/check_consistency.py  → ALL CHECKS PASSED (90 checks)
python3 scripts/runtime_harness.py    → R1–R13 ALL PASSED
python3 scripts/extract_examples.py   → 76 blocks = 71 full (9 envelope-validated) + 5 fragments
python3 scripts/check_links.py        → 1,326 § refs, 0 dangling
python3 scripts/rtm_counts.py         → 1903 rows / 1109 MUST+MUST_NOT (deduplicated)
```

CI (`.github/workflows/validate-vectors.yml`) runs all of the above; note it has
not yet executed on GitHub (work uncommitted) — watch the first push.

## Key documents (read before touching anything)

- `docs/draft-02-closure-graph.md` — item-by-item de facto closure + relation graph.
- `docs/draft-02-decisions.md` — DR-B*/DR-D* (wire decisions D1-D5), DR-P2..P7
  (phases), **DR-P8** (residual sweep), **DR-P9** (consistency guards).
- `docs/draft-02-final-report.md`, `docs/draft-02-findings-status.md` — resolution
  and reproduction records; `results/draft-02-conformance-report.md` — reproducible
  evidence; `docs/draft-02-release-checklist.md` — 26/26 criteria + owner actions.
- `docs/draft-02-skip-classification.md` — all 94 runtime-only vectors, individually.

## Conventions the next session must keep

- New consistency guards go **inside `scripts/check_consistency.py`** as
  `check(...)` calls — never a new script. Detectors carry self-tests.
- Signed vectors: Draft-02 profile = envelope with `security` present, **only
  `security.sig` removed**; re-sign via `scripts/regen_v2.py` (never by hand).
- Retention is typed ISO 8601 durations end-to-end; reject-below-floor, never
  clamp; no `_days` fields anywhere (CI-guarded, incl. descriptions/narrations).
- The onboarding decision is a `request` + `payload.args` (audit label
  `approval_decision` is intentional — Identity §7.6/§9.3 note).
- RTM edits: keep IDs unique (CI-guarded) and modal/anchor aligned with prose.
- Historical records (CHANGELOG Draft-01 entry, audit documents, vector
  migration notes) are immutable — resolution is recorded forward, never by
  rewriting history.

## Open items

**Owner (blocking release):** review/approve the Draft-02 diff; decide
commit/tag; legal review of qualified regulatory statements (A-19/A-21/M-30,
known-limitations §13); integration-class conformance tests against a reference
deployment before any public conformance claim. No push/licence/governance
change without explicit instruction.

**Cross-repo (next real work):** `arsialabs/arsia-protocol-sdk` and the demo
agents still implement wire 1.0 — migrate per
`docs/draft-02-migration-guide.md`. The getting-started guide already carries an
SDK-version caveat.

**Deliberate deferrals (documented, not pending):** LLM-based contradiction
review and spec-toolchain migration (DR-P9 limits); H4 bitemporality
(known-limitations #14); prose↔prose contradictions written once in two
genuinely different phrasings remain adversarial-review territory — the durable
answer is two independent implementations at interop (recommended v2.0-Final
exit criterion).
