<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Draft-02 Remediation Ledger — Closure Evidence

Part of the [Draft-02 remediation ledger](draft-02-remediation-ledger.md). This file
holds the per-cycle closure evidence from C3a onward (§10, §12, §13); the C2 and
C2.1 evidence is in the [regulatory file](draft-02-remediation-ledger-regulatory.md).
Section numbers are those of the main ledger, so existing references stay valid.

## 10. C3a closure evidence

Each closure criterion was checked against the evidence below, at the C3a commit.

| Finding | Closure criterion | Evidence | Met |
|---|---|---|---|
| A-1 | Schema validation passing records built literally from Actions §3.5 (1-4, expiry) | Actions §3.5 tables use the base-field names of State §7.1 and state that records carry the base fields. The schema adds `decision` and `outcome` (enumerations exactly as in the prose: Record 3 and the expiry record; Record 4), `root_request_id`, and `reason` as string or null. The conditionals require them for pending_approval, approval_decision and approval_expired. ITV-581..585 validate; INV-46 is rejected. | yes |
| A-2 | Schema validation of Rule 7, deployer_id, cancellation records; CHECK-04/STATE-15 names aligned | Routing Rule 7: `relay_id`→`attestation_id`, `zone`→`residency_zone` and `relayed_at`→`received_at`/`forwarded_at` are mapped under the §7.4.2 names. `broker_agent_id` is kept, because Core §9.2 item 4 requires "the broker's own agent identifier"; it is added to §7.4.2, the schema and the vectors (INV-48). The §7.4.2 example plus base fields validates. `deployer_id` is an optional extension (ITV-588). `cancellation_reason` replaces `actual_timeout` on cancellations (ITV-586; INV-47). CHECK-04 names both profile fields, and STATE-15 plus the §7.4 filter use `compliance_profile_resolved`. | yes |
| A-3 | Schema validation of compliance_warning/oversight_timeout records, or disposition placing them outside the canonical trail | `compliance_warning` is in the State §7.1 enum and the schema (ITV-587; M-06 parity check passes). `delivery_failed` is recorded as a routing-log disposition. `oversight_timeout` is suspended (DR-2). | partly → IPC |
| A-9 | Schema description consistent with keyword; validation of declared extension behaviour | The Core §4.3.6 note and the schema description state the registered-fields reading; additionalProperties:false is kept; INV-49 is rejected. | yes |
| A-10 | Assets §5.2 example validates as printed | The `summary` requirement and property are removed. The §5.2 Step 3 example, with its placeholders filled and wrapped in an envelope, validates. ITV-400 drops `summary`; ITV-401 tests the missing `context`. | yes |
| A-27 | Schema minItems aligned with prose (or relaxed prose); §7.8 scenario validated | Identity §7.6 now requires the three arrays present and `effective_capabilities` non-empty; either sub-list may be empty. The schema is unchanged, and ITV-589 (the §7.8 approval) validates. | yes |
| A-59 | Consistency rule asserting State §7.1 table ⇔ schema extensions | The State §7.1 table has one row per record type, each validated against its originating prose (Actions §3.5; State §3.1.2, §3.1.3, §3.2.2, §3.3.1, §3.3.2, §8.3; Assets §4.2.4, §4.3; Routing §7.4.2; Core §9.2; Identity §2.5, §4.4). The guard passes on the repaired state. It fails on the `a8e9930` State and schema (table not checkable), on the repaired table against the `a8e9930` schema (17 problems), and on each targeted mutation (schema drops `broker_agent_id`; table drops `decision`; undeclared exception; schema drops the escrow_returned alternatives). | yes |

## 12. C3b closure evidence

Checked at the C3b commit. RFC 8785 §3.2.3 was read at rfc-editor.org
(2026-09-28): "Property name strings to be sorted are formatted as arrays of UTF-16
code units", compared "as unsigned integers, independent of locale settings".

| Item | Evidence |
|---|---|
| F-3 / A-35 | Core §5.1 Step 3 rewritten; ITV-590 member names `message`, U+1F600, U+FF21 sort in that order (D83D < FF21); a consistency check verifies the signature over the RFC 8785 bytes and rejects it over code-point order |
| A-18 | Aligned: Core §4.1.3, §4.2.2, §6.3, §6.4, §8.3 bullets, §13.2.4; Identity §3.3 step 6; Actions §3.4 Step 2; Routing §1.2.1 step g, §4.1.9, §8 test action; State §3.2.1; dpop-proof `iat`. Token-lifetime 300 s literals are not skew checks |
| A-30 | Assets §3.2.3 receipt, Assets §6.3.2 token (with `jti`) and the Core §7.1 discovery example (A-19) validate against their schemas; the ASSETS-06 amount matches the amount pattern |
| A-74 / A-81 guard | Removing `partial_rollback` from the table, or the `declared_retention` exception, fails the A-59 guard; so does requiring `declared_retention` in the schema while the exception is kept |
| Vectors | 669 (ITV-590, ITV-591, INV-50 added; ITV-99 gains the rollback fields): 430 valid / 145 invalid / 637 pass / 32 runtime-only failures, unchanged; crypto 85/85; error paths 0 mismatches |
| Tooling | check_consistency 94 checks, all pass; harness all pass (new R3, R5, R7 cases); 76 example blocks OK; links OK |
| RTM | 1909 rows / 1117 MUST+MUST_NOT (+6 rows: ASSETS-§4.1-19/20, ROUTE-§3.2-05, ROUTE-§4.1.8-02, ACT-§4.2-12, IDENT-§3.1-08); 26 rows re-traced; coverage summaries recomputed |

## 13. DR-5 closure evidence

Each closure criterion was checked against the evidence below, at the DR-5 commit
(execution baseline `eaeb308`). Construction and claim: State §7.2 "Hash chain" and
"Tamper-evidence scope" as rewritten; mandate: Core §12.1, §12.2, State §7.2, §7.4,
§11.4, Identity CHECK-04; design record DR-5 addendum (D1-D9).

| Finding | Closure criterion (clause by clause) | Evidence | Met |
|---|---|---|---|
| A-8 | (1) new chain construction quoted; (2) claim quoted; (3) executed tamper test on a field the old construction did not cover | (1) §7.2 "Chain value": SHA-256 over RFC 8785 of `{"previous_chain_value": P, "record": R'}`, R' = the complete record without `hash_chain`; (2) §7.2 detected / not-detected lists, "MUST NOT claim stronger properties" kept; (3) ITV-597 (`approver_id` changed) rejected — harness R14 (b) "chain value mismatch" and the check_consistency tampered-vector check; R14 also shows the pre-DR-5 construction blind to the same change | yes |
| A-60 | Executed hash_chain vectors including a tamper case | check_consistency "DR-5 chained vectors recompute and verify (2 chains, 6 entries)": ITV-95, ITV-592..596; "DR-5 tampered chain vectors fail verification with the stated reason": ITV-597..599; harness R14 (a)-(h) | yes |
| A-82 | Byte-exact construction, ordering, first-record rule and verification defined | §7.2 "Position", "Chain value" steps 1-5, first entry `null`, "Verification" rejection list 1-5 and verified-prefix rule | yes |
| A-83 | A conformance level states the chain mandate | Core §12.2 table row "Audit hash chain"; Core §12.1 SHOULD; State §7.2, §7.4, §11.4; Identity §7.3 (D1) | yes |
| A-84 | ITV-95 value reproducible under a stated rule | ITV-95 is the first entry of its own chain (`chain_seq` 1, previous `null`); recomputed by check_consistency and R14 (a) | yes |
| A-85 | No "v1.0"/"future REQUIRED" wording where the chain is described | schema `hash_chain` description rewritten; STATE-§7.2-10/-11 rewritten to the construction and first-record MUSTs | yes |
| A-86 | The two untraced MUSTs have RTM rows | STATE-§7.2-19 (MUST NOT claim stronger properties), STATE-§7.2-20 (anchoring scope and cadence) | yes |
| A-87 | `hash_chain` and `sub_type` have §7.1 entries | §7.1 entries for `hash_chain`, `chain_id`, `chain_seq`, `chain_format`, `sub_type`; A-59 guard extended with reverse coverage (every schema property has a §7.1 entry or table mention) | yes |
| A-91 | Permanent deletion no longer breaks verification | §7.2 "Tombstones" + §7.3 sentence; ITV-595 bridges position 4; R14 (a) accepts, R14 (g) and ITV-599 reject a wrong previous value | yes |
| A-92 | A defined actor and path for permanent deletion | §7.2 "Permanent deletion path" MUST sentence; §7.3 refers to it; RTM STATE-§7.2-16/-17, STATE-§7.3-07 | yes |

**Guard extension (A-59, D6, owner condition C3).** `audit_extension_parity` now also
checks reverse field coverage, the chain fields' all-or-none rule (prose ⇔ schema
`dependentRequired`) and the tombstone field list (prose ⇔ tombstone schema). Each
fails on a targeted mutation (removed `hash_chain` entry, dropped
`dependentRequired`, extra tombstone field). INV-51 fails only on
`dependentRequired` (three errors, one per missing chain field, no other cause);
INV-52 only on `additionalProperties`.

**Cross-references re-checked, unchanged and still accurate:** Actions §3.5
"Regulatory support" (tamper-evidence scope of State §7.2); Actions §5 audit
inclusion (explanation integrity within that scope); Assets §4.3; Core §13.1 #9
(purge plus audit-store control defeats local tamper evidence); Identity §9.3.

**Independence.** Each edited item depends only on the chain behaviour: the
construction, verification and tombstone rules use no retention period, profile or
regulatory conclusion; the §7.3 sentence and the maintenance path govern how a
deletion is written, not when it may occur (retention axis unchanged); the
conformance mandate (D1) and CHECK-04 read the chain fields, not any profile.

**Battery (before → after).** Vectors 669 → 679: 430 → 438 valid, 145 → 147 invalid,
637 → 647 pass, 32 → 32 runtime-only structural failures; crypto 85/85 → 85/85;
error paths 0 → 0 mismatches; check_consistency 94 → 98 checks, all pass (every
earlier check unchanged); harness 110 → 126 assertions, all pass (R14); examples 76
blocks OK; links OK; RTM 1909 / 1117 → 1922 / 1130.
