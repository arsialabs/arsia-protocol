<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Session Handover — 2026-08-06

**Tree state:** branch `draft-02`, HEAD `c4bc506` (post-release hardening).
Working tree carries the uncommitted legal-triage batch described below (15
paths). **No tag, no push** — unchanged owner decisions. Previous handovers:
`session-handover-2026-08-05.md` (release commit + hardening),
`session-handover-2026-07-29.md` (closure).

## What this session did

1. **Received the legal review** of the qualified regulatory statements
   (A-19/A-21/M-30 + known-limitations item 13) and saved it verbatim as
   `docs/draft-02-legal-review-triage.md`. **Internal reference only**: the
   specifications cite the underlying legal sources directly and never cite the
   review (owner instruction).
2. **Applied the corrections the review classifies as required before counsel
   handoff**, per owner approval:
   - **Actions §3.5 + §6 note 3 downgraded** — "satisfy" → "provide technical
     records that support the operator's compliance", with the standard
     "statement subject to legal review" marker and explicit reference to the
     State §7.2 tamper-evidence scope. Also covered the third §3.5 claim the
     review did not number (Art. 14(4)(d): "prove" → "demonstrate"). Section
     heading renamed "Regulatory satisfaction" → "Regulatory support".
   - **State §7.2 pseudonymisation reference** — draft EDPB guidance replaced by
     CJEU EDPS v SRB, C-413/23 P (judgment of 4 September 2025), contextual
     approach.
   - **PAC citation corrected** — Reg. 2021/2116 Art. 60 (contains no retention
     rule) → Art. 51 + Implementing Reg. (EU) 2022/128 Art. 34, in State §4
     table, State §6.4 regulatory mapping, and the catalog
     (`retention_reference`, `regulatory_references`). `P1096D` kept, documented
     as a conservative approximation of the event-anchored statutory clocks
     (clearance / final payment / recovery), marked subject to legal review.
   - **DSA-VLOP floor corrected — wire-behavior change, done pre-tag** —
     `P731D` citing Art. 37 (no retention rule; no basis located for 2 years)
     → `P1096D` derived from DSA Art. 34(3) (risk-assessment supporting
     documents, ≥3 years). Owner qualifier applied: the interpretive mapping
     (profile floor ← Art. 34(3) document retention) carries the
     "statement subject to legal review" marker so counsel keeps the
     checkpoint without blocking the correction. Declared retentions in
     [`P731D`, `P1095D`] under DSA-VLOP are now rejected by Rule 4.
3. **Full surface updated together** (consistency web): State §4/§6.6, Routing
   §7.4 floor list, profile catalog v2.0.0, `arsia-compliance-field` schema
   example, `check_consistency.py` expected value, vector ITV-559 (unsigned —
   value + description), RTM rows (State §6.6, Routing §7.4 — all six RTMs
   swept), README profile table, CHANGELOG Draft-02 entry, FAQ leap-day
   rationale (731 removed), migration guide floor list, generated overview.
4. **Deliberately NOT changed:** `docs/draft-02-closure-graph.md:83` (historical
   record — P731D was the verified value at closure time; history is never
   rewritten) and the Portuguese audit documents. D.3 of the review
   (AI Act applicability dates) has no repo impact — no applicability dates are
   stated anywhere in specs or profiles (verified by grep).

## Verification state (all green after the batch)

```
validate_vectors --check-meta/--check-errors/--check-crypto
  → 649 vectors, 0 fail; error paths 0 mismatches; crypto 83/83
check_consistency.py  → ALL CHECKS PASSED (91 checks, incl. new DSA-VLOP P1096D parity)
runtime_harness.py    → R1–R13 ALL PASSED
extract_examples.py   → ALL EXAMPLES OK
check_links.py        → ALL LINKS OK, 0 dangling
rtm_counts.py         → 1903 rows / 1109 MUST+MUST_NOT
```

## Open items for counsel (from the review; no repo action taken)

1. Endorse or reject the **Art. 34(3) → DSA-VLOP floor mapping** (marked in
   State §6.6); if rejected, a second value change would be needed.
2. Decide the **PAC anchoring model**: keep P1096D as conservative
   approximation (current text) or reformulate event-conditional.
3. **MiFID erasure guidance** (State §5.3.2): endorse the firmer Art. 17(3)(b)
   formulation or remove; assess the pseudonymisation alternative.
4. **Linkability-analysis framing** (State §7.2): Art. 30 register vs
   accountability artifact (Art. 5(2)/24) or DPIA.
5. **Art. 25 gap** (Identity §4.4): whether a reference to provider-switching
   circumstances is needed.
6. **DORA RTS citation** (Assets §6.2.4): whether Delegated Reg. (EU) 2024/1772
   should be cited alongside Art. 18/19.
7. Confirm no Assets passage implies the protocol *contributes* an SCA element
   (review Part A.1 counsel task).
8. Re-check Digital Omnibus adoption status for AI Act applicability dates at
   review time (review D.3).

## Owner items (unchanged)

Tag `draft-02` (signed: `git tag -s draft-02 -m "..." <commit>`) + branch/tag
protection; push/merge to `main` (first CI run); cosmetic pass before push;
cross-repo migration (SDK, demos, enterprise reference server) per the
migration guide.
