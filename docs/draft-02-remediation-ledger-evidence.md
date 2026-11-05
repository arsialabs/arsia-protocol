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

**Follow-up (normative modals, after `036f239`).** Two State §7.2 sentences that
stated no modal now carry MUST, each with an RTM row: STATE-§7.2-21 — the chain
fields MUST be present together or not at all (`arsia-audit-record`
`dependentRequired`; INV-51, ITV-95, ITV-592..594, ITV-596; harness R14 (f));
STATE-§7.2-22 — a tombstone MUST persist for as long as its chain exists
(`arsia-audit-chain-tombstone`; ITV-595; harness R14 (a), (c)). RTM 1922 / 1130 →
1924 / 1132; every other battery output unchanged.

## 14. DR-3/DR-4 closure evidence

Each closure criterion was checked against the evidence below, at the DR-3/DR-4 commit
(execution baseline `94b8fc9`). Contract: Core §4.3.10 (new), §4.3.6.9, §4.3.7,
§4.3.8 Rules 3, 4 and 7; State §6, §6.2, §7.1; Identity §1.2, §4.2, §7.1.2, §7.2
Step 7, CHECK-05, §7.6, §7.7; Routing §5.1, §5.2; `profiles/arsia-obligation-rules.json`;
design record DR-3/DR-4 addendum (D1-D10).

| Finding | Closure criterion (clause by clause) | Evidence | Met |
|---|---|---|---|
| F-1 | (1) aligned quotes Core Rule 3 / State §6.2 / Actions §3.7; (2) executed high-risk/not_required vector | (1) Core Rule 3 and State §6.2 aligned on the composed oversight set; Actions §3.7 unchanged (DR-1). (2) ITV-608 (explicit not_required, MIFID-II, high-risk) rejected with high_risk_missing_oversight; INV-07, ITV-579, ITV-603..605 (R10) | partial (IPC) |
| A-32 | Harness rule equal for None / GDPR-STANDARD; ITV-579 and CORE-COMPLIANCE-06 (c) aligned to prose | `resolve_obligations` fills the no-profile defaults; check_consistency "A-32 absent profile == explicit GDPR-STANDARD" over classification × oversight (semantic comparison; fill source and declared profile preserved); ITV-604/605 executed; CORE-COMPLIANCE-06 (c) and ITV-579 now describe the composed-set rejection | yes |
| A-23 | Per-axis composition quote; disposition for multi-regime agents | Identity §4.2: any profile may be declared, the high-risk requirement set applies whatever the profile (Core §4.3.10.3); ITV-610: high-risk agent declaring MIFID-II, forwarded by the router after resolution with the bound context; IDENTITY-06 rewritten | yes |
| A-81 | declared_retention requiredness equal in State §7.1 and schema; guard exception removed | schema `required` includes declared_retention; `AUDIT_BASE_EXCEPTIONS` empty and the A-59 guard passes; INV-53 rejected | yes |
| A-73 (remainder) | Remainder resolved in the DR-3/DR-4 cycle | Core §4.3.6.6, Identity §1.2, State §6.2 (Art. 12, Art. 26(6), "Applied when", Annex III) and the Actions risk-table notes no longer present technical controls as proof of compliance | yes |

**Migration without masking (owner condition).** Every pre-existing vector keeps its
exact error signature (path, validator, message) — compared before and after, 0
differences; INV-07, which encoded the replaced Identity §4.2 rule, was re-expressed to
fail for the new reason (high-risk restriction unmet) and re-signed. The 12 invalid
audit vectors that lacked declared_retention and the 8 invalid covered records keep
their original single cause. The failing set of `validate_vectors.py` is the same 32 IDs
with the same structural reasons (list diffed). Chains: the chained records were
updated first, then ITV-95 and ITV-592..596 recomputed, then ITV-597..599 re-derived
from their updated bases with the same tampering; ITV-602 adds a tampered resolution.
ITV-03 was re-signed with `scripts/regen_v2.py`; crypto 85/85.

**Guards (each mutation-tested, 19/19 detected).** In `check_consistency.py`: runtime
vectors' stated results == reference resolver; A-32 semantic equivalence; Core
§4.3.10.3 table == rules artifact (scope, trigger, requirements, exceptions); Core
§4.3.10.6 diagnostics == audit conflict enum, artifact diagnostics belong to their rule,
artifact-schema enum ⊆ table; Identity §7.6 example valid with a recomputable
`context_sha256`; retention fields == derivation from `obligation_resolution`; source
digests recompute; Routing §5.2 list == resolver and digest recomputes; A-59 guard
extended to compound and nested conditions; chain tamper map incl. ITV-602. Mutations:
altered vector expectation, resolver dropping the audit requirement, absent profile
treated as no compliance, artifact scope/restriction/exception changes, Core table row
removed, diagnostic attached to the wrong rule, example digest altered and member
removed, diverging retention_source, catalog changed under recorded digests, EU list
member removed and digest altered, schema covered condition removed, State nested row
removed, ITV-602 substitution. Skip classification: `docs/draft-02-skip-classification.md`
rows == `skip_schema` vectors and its stated total (mutations: row removed, total
altered).

**Acceptance.** Audited rejection: every record the receiver and router simulations
emit is validated as a whole against `arsia-audit-record.schema.json` (R10): the
compliance `error` record of a request declaring audit_required false, the record of
the full INV-07 envelope, the request and `compliance_warning` records of a Rule 7
override, and the records of every runtime vector. Router: the trace shows resolution
before forwarding and no forwarding for a missing, expired, foreign-agent or
foreign-admission context (ITV-610, ITV-613..616), nor for a binding whose context is
null or malformed (ITV-626, ITV-627: `unauthorized`, no resolution). CHECK-05 compares
the prepared context with the Phase 1 evidence — record_sha256, signature, JWK,
classification and the presence and value of the record's valid_until — so a context
edited and re-hashed fails and is not admitted (ITV-623..625). The independent
expectation of INV-07 found a resolver defect (the conflict reported the filled default
as `declared`), fixed before the commit.

**Owner review before commit (2026-10-31).** The review reproduced the battery and found
three harness paths below the approved acceptance criteria: CHECK-05 accepted a context
whose valid_until had been removed and re-hashed, and an incorrect record_sha256; the
router raised an exception, instead of answering `unauthorized`, for a null context in
an existing binding; the emitted rejection record lacked record_id, payload_type,
payload_hash, retained_until and operator_id, so it was not schema-valid although this
section stated otherwise. All three were corrected in the harness (no change to the
contract), reproduced by ITV-623..627 and the R10 schema validation, and
mutation-tested: 6 of 7 mutations detected; the seventh (CHECK-05 reading the
context's valid_until instead of the record's) is equivalent once their equality is
checked. The same pass found the 25 runtime vectors of this cycle missing from the skip
classification; they were classified and the guard above added. It also found three
Identity passages still echoing the replaced rules, corrected with owner-approved
wording: §1.1 (receivers resolve every request of a high-risk agent with the high-risk
requirement set, whatever the profile and also without `compliance`; the former
obligation on request and response metadata removed; RTM IDENT-§1.1-06 re-traced),
§7.1.2 item 2 (compliance trust includes validation of the gateway's authenticated
context, CHECK-05) and IDENTITY-14 (denial when the authenticated context does not match
Phase 1). ITV-623..625 exercise CHECK-05's detection of the mismatch and the absence of
admission; they do not build the complete onboarding decision with
`conformance_failed`, which remains the normative expectation of IDENTITY-14.

**Battery (before → after).** Vectors 679 → 717: 438 → 441 valid, 147 → 157 invalid,
94 → 119 runtime-only, the same 32 known structural failures; error paths 0 → 0
mismatches; crypto 85/85; check_consistency 98 → 110 checks, all pass (every earlier
check unchanged); harness 126 → 199 assertions, all pass (R10 rewritten); examples 76
blocks OK; links OK; RTM 1924 / 1132 → 1940 / 1147.

## 15. DR-1/DR-2 closure evidence

Each closure criterion was checked against the evidence below, at the DR-1/DR-2 commit
(execution baseline `2d40aba`). Contract: Core §4.2.1, §4.3.6.5, §4.3.10.2/.4/.5/.6/.7,
§4.4.7, §4.4.8 (new), §5.2, §6.1, §6.4, §8.3, CORE-COMPLIANCE-09; Actions §1.4, §2.1,
§2.3, §3.2–§3.7, §3.9 (new), §4.1, §4.3, ACTIONS-04/05 and ACTIONS-13..19; Identity
§7.3 CHECK-03, §7.4, §7.6, §7.7, §8.1, §9.1, IDENTITY-16/18/21/22; Assets §5.2,
ASSETS-06; State §6 (CAP, DSA, DORA), §7.1; design record DR-1/DR-2 addendum (E1–E4).

| Finding | Closure criterion (clause by clause) | Evidence | Met |
|---|---|---|---|
| F-1 | (1) aligned quotes Core Rule 3 / State §6.2 / Actions §3.7; (2) executed high-risk/not_required vector | (1) Actions §3.7 now follows the effective oversight set with executor-policy sources; the descriptor is no veto. (2) ITV-608 (DR-3/DR-4) and ITV-640: high-risk sender, MIFID-II default, descriptor `false` → `pending_approval` (R15) — the execution equivalence the DR-3/DR-4 cycle left open | yes |
| A-3 | Schema validation of compliance_warning/oversight_timeout records, or disposition | `oversight_timeout` removed everywhere (guard); its role is `review_overdue`, in the prose, the enum and the schema (ITV-633), with the escalation result in `review_escalation` (ITV-634/635); `compliance_warning` covers a failed escalation | yes |
| A-4 | Aligned quotes for one within_24h evidence event + defined post-execution mechanism; executed C-09 | Core §4.3.6.5, Actions §3.9, CORE-COMPLIANCE-09 and State §6 (DSA, DORA, CAP) define one review with `review_overdue`; `required_post_execution` takes its deadline from `post_execution_review_period` or is rejected (ITV-647/648). C-09 executed by R15 ("R15 C-09") and ITV-645..661 | yes |
| A-11 | Aligned denied/expired response form; ASSETS-06 executed | Assets §5.2 Step 5 answers the Actions §3.4 Path 2/3 errors, no receipt; ASSETS-06 item 9 aligned and executed (ITV-673, "R15 ASSETS-06"); denial ITV-672 | yes |
| A-12 | Aligned quote defining the trigger source relative to Actions §3.7 | Assets §5.2: the risk assessment is an executor-policy source (Core §4.3.10.2); Actions §3.7 no longer forbids it; ITV-643, ITV-400/401 resolutions record `risk-assessment:` | yes |
| A-13 | Aligned Identity §7.3/§7.7 vs Actions §3.7 quotes | Identity §7.4/§7.7/§9.1 carry the CapabilityPolicy requirement in `arsia_oversight` (Core §6.1), consumed by the executor (Core §6.4); router rejection and re-issuance rules; CHECK-03 probe token; ITV-642, ITV-668..671 | yes |
| A-78 | Schema closes the canonical pending_approval field set | `pending-approval-args` closed; Actions §3.2 states the closed set; INV-63; guard | yes |
| A-80 | Record count for a multi-approval flow ending by expiry specified; editor's note removed | Actions §3.6 step 5: N + 4; ITV-663 (5 records) executed by R15 | yes |

**Migration without masking (owner condition).** Every pre-existing vector keeps its
exact error signature (path, validator, message): 717 compared before and after, 0
differences. The failing set of `validate_vectors.py` is the same 32 IDs with the same
reasons (diffed), and ITV-479 stays a runtime-only vector, structure-validated and
outside that set. Inventory by structure: 18 `pending_approval` envelopes (12 valid, 6
invalid, ITV-479 runtime-only) and 10 `approval_decision` envelopes (7 valid, 3
invalid). Each carries `test_metadata.reference_request` (payload, compliance,
executor descriptor, claim or assessment) from which `request_payload_hash` and
`obligation_resolution` recompute (guard); decisions carry the hash of their pending.
Scenario sources follow the inventory, with one adjustment: ITV-338 and ITV-401 have
risk 9, and Actions §2.2 requires `human_oversight_required: true` at risk 9-10, so
their reference descriptors are `true` and their resolutions record the descriptor
source beside the message or assessment source. Onboarding decisions ITV-130, ITV-38,
INV-61, ITV-589 and ITV-03 gain `policy_sha256` from a reference CapabilityPolicy whose
§8.3 evaluation reproduces their lists (guard). Signed vectors re-signed with
`scripts/regen_v2.py`: CTV-02, CTV-08, CTV-09, CTV-10, INV-14, INV-17, ITV-03; crypto
89/89.

**Migration exceptions (owner, 2026-10-31).** CTV-02 and ITV-338 declared `retention:
"P180D"` under EU-AI-ACT-HIGH-RISK, whose floor is P6M; the reference resolver,
anchored at each envelope's `ts`, rejects both (`insufficient_retention`) and accepts
P6M. Both now declare `"P6M"`: CTV-02 is re-signed (its payload, and therefore the
request hash and STV-06/07's references, are unchanged); ITV-338 carries a structural
test signature and no `crypto` block, so it is not re-signed. ACTV-01 has the same
defect and is left unchanged for the vector cycle (notes).

**Guards (each mutation-tested, 33/33 detected).** New in `check_consistency.py`:
migrated pending/decision vectors recompute from their reference request, and a valid
pending's reference request is accepted with prior approval; onboarding
`policy_sha256` and lists == reference policy; closed member lists (Actions §3.2 args,
§3.9.3 review payloads, Core §6.1 claim) == schemas; Core §4.3.10.2 executor source
ids == harness; replaced rules absent (`oversight_timeout`, router annotation,
descriptor veto, the old within-24h description); the vector-scenario check extended
to `execution`; A-59 covers the four review records. Mutations, in R15 and the guards
(`mutation_evidence`): descriptor veto, claim dropped on re-issue, `review_deadline`
from `expires_at`, overdue terminal, lateness from timer order, deadline equality on
time, overdue record waiting for delivery, record mutated after escalation,
escalation counted as review, unsigned error with resolution accepted, token failures
as `invalid_request`, default recorded as declared, acknowledgment opening a review,
deadline moved by retrieval, retrieved result accepted unsigned or rejected for age,
retry before `Retry-After`, hash binding removed, missing period accepted, CTV-02 back
to P180D, pending args reopened, review member added, claim member renamed, executor
prefix changed, `oversight_timeout` reintroduced, review conditional removed, reference
policy altered, retrieval binding without the `correlation_id` comparison, without the
`root_request_id` comparison and with the signature only, review notice and overdue
notice sent to the default destinations, configuration rejection not emitted.

**Acceptance.** Every message and record emitted by R15 validates against
`arsia-message.schema.json` and `arsia-audit-record.schema.json`, and no record is
modified after emission (snapshot comparison). The 35 runtime vectors ITV-640..674
state hand-written expectations, all met; they cover the four prior-approval sources,
the review deadlines (24 h across midnight, P1M end-of-month), the configuration
conflict with inherited and declared modes, lateness at and after the deadline before
any timer, escalation backoff, `Retry-After` and exhaustion, duplicate and rejected
decisions by error code, objection, approval binding, multi-approval expiry,
asynchronous success and failure retrieved three days later, token re-issuance, the
CHECK-03 probe token, the Assets denial and expiry, and configured destinations that
differ from the defaults (ITV-674). The composition of both
post-execution modes is unreachable with this cycle's sources (executor-policy sources
demand prior approval only) and is unit-checked in R15.

**Owner review before commit (2026-11-01).** The review found one functional defect and
two verification gaps in R15, below the approved criteria; the resolution itself was
not shown wrong. (1) A configuration rejection was computed and audited but no envelope
was emitted, so the message checks ran over an empty list: the executor now emits a
signed `error` carrying the details and `payload.obligation_resolution`, and ITV-647..649
require it (`rejection_message`, `message_intents`). (2) The review and overdue notices
used the default destinations instead of the validated configuration: the run keeps the
configuration the resolution validated, and ITV-674 uses destinations different from
the defaults. (3) The asynchronous binding check was protected only by the signature,
because the foreign copy was not re-signed: validly re-signed copies differing only in
`correlation_id` or only in `root_request_id` are now required to be rejected (ITV-665,
ITV-666). The six corresponding mutations are detected (33/33 in all).

**Battery (before → after).** Vectors 717 → 780: 441 → 453 valid, 157 → 173 invalid,
119 → 154 runtime-only, the same 32 known structural failures; error paths 0 → 0
mismatches; crypto 85 → 89, all pass; check_consistency 110 → 115 checks, all pass;
harness R1–R14 → R1–R15, 199 → 316 assertions, all pass; examples 78 blocks OK; links
OK; RTM 1940 / 1147 → 1970 / 1173.

## 16. VC closure evidence

Each closure criterion was checked against the evidence below, at the VC commit
(execution baseline `e5e06a5`). The cycle changes no normative text: only the vectors,
the vector meta-schema (`crypto.expect_signature`, `posture`), the tooling
(`validate_vectors.py`, `runtime_harness.py` R16, `check_consistency.py`) and the
documents that describe them. Design record: DR-0 addendum (V1–V5).

| Finding | Closure criterion (clause by clause) | Evidence | Met |
|---|---|---|---|
| A-18 | (1) profile-aware tolerance in each timestamp check; (2) ITV-545/546/547 executed | (1) C3b. (2) Harness R16 runs ITV-545 (MIFID-II, 60 s: ts 120 s off, rejected under the MAY posture), ITV-546 (EU-AI-ACT-HIGH-RISK, 120 s: 90 s off, on time) and ITV-547 (default 300 s: 120 s off, accepted) against the declared recipient clock; checks "R16 ITV-545/546/547 result matches its stated expectation" | yes |
| A-34 | INV-18/19 asserted negatives with checker assertion (caveat: proxy) | `--check-crypto` asserts INV-18/19 from `expect_signature: "invalid"`; the proxy (expected-invalid + `unauthorized`) is removed — ITV-409/410 are `unauthorized` negatives whose signatures verify; guard "crypto.expect_signature declared and coherent"; mutations "A-34 proxy reintroduced", "INV-15 absent → valid", "canonical-only counted as verified" detected | yes |
| A-39 | ITV-404/406/438/439 expectations aligned with Core §4.1.1 and executed | ITV-404 `v: "3.0"` → `not_implemented` (rule 6); ITV-406 `v: "2.1"` with `future_field` → valid (rule 3); ITV-438 `v: "2.0"` with `routing_hint` → invalid, single error `additionalProperties` at the root (rule 1); ITV-439 `v: "2.2"` → valid (rules 3-4). All four are ordinary vectors run by the validator's version procedure | yes |
| A-42 | (validator) skip vectors validated structurally; (vectors) skip vectors structurally valid; ITV-545/546 aligned | Validator: a skip exempts only the runtime expectation; self-test "validator self-test: a structurally invalid runtime-only vector fails (A-42)" and the mutation "skip bypass restored" detected. Vectors: all 148 runtime-only vectors structurally valid (validator: 148 pass, 0 fail); ITV-545 declares the Core §8.3 MAY posture; ITV-546 left the skip set (single schema cause, Rule 2) and R16 attributes its compliance causes | yes |
| A-65 | Skip-classification entries matched one-to-one to harness cases | `docs/draft-02-skip-classification.md`: one row per runtime vector (148), closed coverage vocabulary — `executed` 66 (R10 26, R15 35, R16 5), `equivalent` 11, `partial` 5, `none` 66; the 14 earlier "covered" claims re-checked (7 unsupported → `none`, INV-08/ITV-421/ITV-579/INV-23/INV-24 → `partial`, INV-25/ITV-417 → `equivalent`); guard "skip classification coverage column == harness evidence" (every `executed` row has a scenario its rule consumes, every quoted check passes in the harness, totals computed) | yes |
| A-62 | Harness rule + ITV-545/546/547 executed with profile tolerances; clean "90 s under 120 s" case | R16 executes the three with profile tolerances. Pending: the clean case of a valid message 90 s off under a 120 s profile tolerance (ITV-546 is 90 s off but rejected for compliance causes) | no — stays open |

**DR-0.4 classification of the 32** (D = defective data, E = outdated expectation,
P = distinct validation procedure). "Signed" = a real Ed25519 signature with a
`crypto` block expecting it to verify.

| ID | Class | Cause | Treatment | Final expectation |
|---|---|---|---|---|
| ITV-405 | P | v 2.1 checked against the exact 2.0 schema | major-2 compatibility procedure; left the skip set | valid |
| ITV-406 | E+P | v 1.1 (another major) expected valid | v 2.1, `future_field` kept; compatibility procedure; left the skip set | valid |
| ITV-409 | D | request without `security` | signed (acme.billing); `test_metadata.token.sub` | invalid `unauthorized` |
| ITV-410 | D | idem | signed; `test_metadata.token.aud` | invalid `unauthorized` |
| ITV-411 | D | idem | signed; R16 (expired; ts outside, no posture, no cause) | invalid `invalid_request` |
| ITV-412 | D | idem | signed; `test_metadata.token.scope` | invalid `forbidden` |
| ITV-413 | D+E | idem; "recipient up to v1.0" no longer exercised `min_v` | signed; `min_v` 2.1; recipient range 2.0–2.0 | invalid `not_implemented` |
| ITV-414, 418, 422, 424 | D | idem | signed (ITV-424 still does not materialize 1 MiB) | unchanged |
| ITV-416 | D | idem | signed; posture `configuration` (strict mode) | invalid `invalid_request` |
| ITV-438 | E | v 2.0 with an unknown field expected valid | explicit negative of rule 1; left the skip set | invalid |
| ITV-439 | E+P | v 1.2 expected valid | v 2.2; compatibility procedure; left the skip set | valid |
| ITV-477 | D | response without `security` | signed (acme.echo-client); `test_metadata.external_agent_id` | invalid `conformance_failed` |
| ITV-536..541 | D | request without `expires_at`/`capabilities`; placeholder signature | fields; signed (acme.data-agent); ITV-539 `skip_reason` without max() | valid |
| ITV-543, 544 | D | request without `expires_at`/`capabilities` | fields; `data` → `args`; re-signed | valid |
| ITV-545 | D | request without `expires_at`/`capabilities`/`security` | fields; `args`; signed; posture MAY; R16 | invalid `invalid_request` |
| ITV-546 | D+E | id not UUID v4; request fields; Rule 2 schema-expressible | id variant 8; fields; `args`; signed; left the skip set; R16 | invalid `invalid_request` |
| ITV-547 | D | id not UUID v4; request fields; `data_residency: null` | id variant 9; fields; `args`; null residency omitted; re-signed; R16 | valid |
| ITV-553, 554 | D | request without `capabilities`/`security` | `data.process`; signed (acme.data-processor) | valid |
| ITV-555, INV-20, INV-22 | D | request without `security` | signed (acme.health-processor) | unchanged |
| INV-25 | D | intent `inform` does not exist; `args` for a decision | conformant `approval_decision` with a reference request; signed (acme.oversight-panel) | invalid `forbidden` |

Outside the 32: ITV-404 (A-39, above); ITV-408 and ITV-440 gain the MAY posture and
run in R16; new INV-79 (2.1 without `from`), ITV-675 (2.1 error with unknown top-level
and payload fields) and INV-80 (2.1 payload with `result` and `error`) test the
compatibility procedure. Before any edit, the 218 positive message vectors valid at the
baseline all passed the compatibility schema with `v: "2.1"`; after the repairs, 230.

**Linked fixtures (V4).** CTV-08 goes from compliance-checker to risk-assessor (CTV-02's
recipient to its sender); CTV-09/10 from risk-assessor (the approver) to
compliance-checker, with `root_request_id` = CTV-02's id and `approver_id` =
`agent:arsialabs.demo.risk-assessor`; all three re-signed. ITV-309→293, 310→303,
312→304, 313→305 and 314→306: `to` and `root_request_id` of the pending (no
signature to renew; ITV-312 keeps its single cause). Incidental pending relations:
INV-14 root (re-signed), ITV-401 and INV-17 correlation and root (INV-17's canonical
bytes recomputed), ITV-478..481 `to` = `agent:corp.gateway` (the probe claim's
issuer), ITV-479 `correlation_id` re-expressed so that the negative it announces
exists. The 20 reference requests without a corpus request gain an explicit `to`.
The guard checks recipient, correlation, root, approver and hash on every declared
link; INV-14 and ITV-479 fail only their stated `correlation_id` relation.

**Local notes.** ACTV-01 retention P6M (re-signed); CTV-08 and ITV-86 conformant
`action_id` (resolutions recomputed; `ACTION_ID_EXEMPT` removed); ITV-99 and INV-50
payload type `com.example.notes/create/rollback`; ITV-130, ITV-38, INV-61 and INV-78
`arsialabs-2026-q2b` with `test_metadata.gateway`; ITV-589 gateway as noted.

**Signatures.** 25 vectors gain a real signature and a `crypto` block; re-signed:
CTV-08/09/10, ACTV-01, ITV-543/544/547, INV-14; INV-17's canonical bytes recomputed.
Six keypairs added (13 Ed25519, 1 ES256, 1 RS256): private key = SHA-256 of
"arsia-test-vectors keypair " followed by the agent-id. The 89 existing blocks gained
`expect_signature` with outcomes identical to the C0.5 checker (84 verified, 2
negatives, 3 canonical-only). Crypto after: 114 checked, 109 verified, 2 negatives,
3 canonical-only, 0 failures.

**Error signatures.** Compared vector by vector (path, validator, message) under the
exact schema: only the 29 repaired runtime-only vectors (the 32 less ITV-405/406/438/
439, plus ITV-404) change, and the three new vectors are added; every other vector
keeps its signature. Under the procedure the validator applies, ITV-404 fails only
on `v` (`not_implemented`), ITV-438 only on the root `additionalProperties`, INV-79
only on `from`, INV-80 only on `payload.oneOf`.

**Guards (each mutation-tested, 33/33 detected).** New in `check_consistency.py`:
`expect_signature` coherence; posture text verbatim in its section, and every
MAY-based ts rejection carrying the posture; linked relations with per-relation
negative exceptions; valid message vectors accepted by the reference resolver;
(gateway, `policy_version`) → one digest; coverage claims; validator self-test; the
scenario check extended to `timing`. Mutations: the A-34 proxy, `absent` → `valid`,
canonical-only counted as verified; the schema root relaxed; the procedure always
exact; another major accepted; compatibility dropping `required`, without branch
discrimination, without the error-branch exclusion; a skip vector made invalid; the
skip bypass restored; INV-14 root, ITV-401 correlation, INV-17 root, ITV-478
recipient, ITV-479 correlation, CTV-08 direction, CTV-09 root, CTV-10 approver,
ITV-309 recipient reverted; another relation of a negative broken; CTV-08's old
`action_id`; ACTV-01 back to P180D; a decision without gateway; two digests under one
(gateway, version); R16 tolerance always 300, posture ignored, ts never a cause, the
clock counted for ITV-546; ITV-545's posture removed; a coverage row quoting a missing
check, `executed` without a scenario; MAY → MUST in Core §8.3.

**Battery (before → after).** Vectors 780 → 783: 453 → 457 valid, 173 → 178 invalid,
154 → 148 runtime-only; structural failures 32 → 0; error paths 0 → 0 mismatches;
crypto 89 → 114, all pass; check_consistency 115 → 122 checks, all pass; harness
R1–R15 → R1–R16, 316 → 335 assertions, all pass; examples 78 blocks OK; links OK;
RTM 1970 / 1173 unchanged (CORE-§7.4-02/-04 re-traced to ITV-406, STATE-§8.3-05
re-worded to State §8.3 rule 2).

## 17. LM3 closure evidence

Execution baseline `bbb8ef3`. The cycle changes no normative text and no tooling: only
the ledger, its notes and this evidence. Mutations ran in a temporary
`git archive bbb8ef3` extract with the working directory set to it; the repository was
not touched. Unmutated baseline: `ALL RUNTIME RULES PASSED`.

| Finding | Closure criterion (clause by clause) | Evidence (checks in `scripts/runtime_harness.py`, added in C0.5 `260ac73`) | Mutation reintroducing the defect → required failing checks | Met |
|---|---|---|---|---|
| F-2 | (1) shared-cache two-call test; (2) revoked kid; (3) reject/reject | `JwksCache.accept` (l.1657); "R13 revoked kid after ceiling, shared cache, call 1 rejected" / "call 2 rejected" (l.1696-1697); "R13 never-published kid, shared cache, call 1/2 rejected" (l.1688-1689) | `accept` records the looked-up kid even when absent → "R13 never-published kid, shared cache, call 2 rejected" and "R13 revoked kid after ceiling, shared cache, call 2 rejected" FAIL | yes |
| A-36 | harness case `arsiaprotocolx.*` → True | `scope_satisfies` tests `(prefix + ".").startswith("arsiaprotocol.")` (l.142); "R3 non-reserved lookalike namespace wildcard (A-36)" (l.167) | trailing dot dropped (`prefix.startswith("arsiaprotocol")`) → that check FAILs | yes |
| A-37 | (1) SEK; (2) length/digit limits; (3) non-currency scales | `amount_valid` with an injected catalog (l.194); (1) "R5 SEK accepted under the declared test catalog (A-37)" (l.236); (2) "R5 16-digit integer part accepted", "R5 17-digit integer part rejected", "R5 20-digit integer part rejected (A-37)" (l.240-242); (3) token 8/9, entitlement 2/3, service_unit 4/5 fraction digits (l.247-252) | (a) the fixed C0.5 seven-currency table instead of the catalog → SEK check FAILs; (b) integer-part limit 16 → 99 → 17- and 20-digit checks FAIL; (c) scale check replaced by `True` → token 9, entitlement 3 and service_unit 5 checks FAIL | yes |
| A-38 | (1) max-age below the ceiling; (2) revocation-event invalidation | `JwksCache` caches the JWKS document, not a kid (l.1637); (1) "R13 max-age 60: accepted within / rejected after max-age / rejected again" (l.1703-1705), "R13 max-age 7200 capped: rejected after 3600 s" (l.1711); (2) "R13 revocation event: rejected at once, call 1/2" (l.1718-1719) | (a) `min(max_age, ceiling)` → ceiling → "R13 max-age 60: rejected after max-age" FAILs; (b) `revocation_event` emptied → "R13 revocation event: rejected at once, call 1" FAILs | yes |

Mutations: 7/7 detected. F-2 and A-38 already cited "harness R13 (C0.5)"; what was
pending for all four was the formal closure verification, not the evidence. A-33 stays
IPC (repo alg/key-mismatch vector pending).

**A-57 reproduction (reference harness).** A pending run built with the harness's own
`make_request`, `make_descriptor` and `Run` (the ITV-662 setup: descriptor oversight,
GDPR-STANDARD) receives one approval decision from `approval_decision_msg`, modified:

| Decision | `signature_ok` | `Run.approval()` | Run path |
|---|---|---|---|
| (a) `reason` changed after signing | False | no error | `pending` → `executing` |
| (b) `capabilities: []`, re-signed | True | no error | `pending` → `executing` |
| (c) `result.approver_id` ≠ `from`, re-signed | True | no error | `pending` → `executing` |

The gap is recorded under A-57 in the notes; A-57 stays open.

**Inventories at `bbb8ef3`** (scripted; recorded as observations, not findings or
closures):
- Signatures outside crypto-block verification: 187 = schema 160 (120 valid / 40
  invalid) + runtime-only 27 (9 / 18) = 55 fail with the identified key + 126 kid
  outside the catalog + 5 other alg + 1 verifies (INV-39), resolving the full kid under
  the Draft-02 profile. The most common placeholder value (base64url of
  "test-signature-for-schema-vali…") occurs in 98 of them; the runtime-only ones among
  those are exactly INV-23, INV-24, ITV-566, ITV-567, ITV-568.
- INV-39 verifies under the Draft-02 profile and fails under the Draft-01 profile;
  INV-38's kid is not in `keypairs.json`.
- Named conformance tests (level 3-5 headings naming `<PREFIX>-NN`, optionally after
  "Test", for the six spec prefixes): 74 at `fb5a875`, 83 at
  `bbb8ef3` (Actions 12 → 19, Identity 20 → 22; Core 9, State 15, Assets 8, Routing 10
  unchanged); onboarding checks CHECK-01..05 counted separately.
- Runtime `expected_error` outside the Core §11.2 enum (14 codes, `certificate_invalid`
  among them): 10 free-text values and 4 occurrences of two values
  (`identity_verification_failed`, `conformance_failed`).

**A-88 triage (owner decision 2026-11-02).** Source text of the decision:

> State §2.1.5 define `created_at` como imutável após a criação. State §2.1.12 e
> §3.1.2 qualificam a recriação após DELETE como criação de uma nova entrada, que
> recebe um novo `created_at`. Essas disposições são compatíveis quando a imutabilidade
> se aplica à vida de cada entrada. A-88 é tratado como questão interpretativa
> associada à representação das gerações em A-79, sem contradição normativa
> demonstrada.

Anchors at `bbb8ef3`: State l.545-546 (§2.1.5, "first created … immutable
thereafter"); l.739-745 (§2.1.12, "the recreated entry is a new entry and starts with
version `1`"); l.1058-1061 (§3.1.2, "SET creates a new entry with `version: 1`,
`created_at` set to the current time"). Precedent: A-24's disposition. Triage changes
from `new (DR-5)` to `INT`; remediation state (open), closure criterion, dependency
(A-79 cycle) and evidence are unchanged.

**Counts before → after** (findings register, 95 rows): remediation IPC 7 → 3, closed
71 → 75, open 17 unchanged; triage INT 6 → 7, new 24 → 23; class and disposition
counts unchanged (A-88 was already among the 18 recorded dispositions). Coverage
register unchanged (open 14, closed 4; "Revocation under cache ceiling" stays open
through A-58). Tool counts unchanged: vectors 783, consistency checks 122, harness
R1-R16, RTM 1970 / 1173.

## 18. A-79 cycle closure evidence

Execution baseline `df6219c`. Owner decisions G1–G5 are in the design record (DR-5
addendum, A-79 cycle). Line references are to the files after the cycle. Mutations ran
on a scratch copy: `git archive df6219c` with the full candidate diff applied, the
unmutated copy first passing the whole battery, and the candidate restored between
cases; the repository was not touched and no early commit was made.

| Finding | Closure criterion (clause) | Evidence | Mutation → failing check | Met |
|---|---|---|---|---|
| A-79 | (key, version) history unambiguous across generations after reset | State §2.1.14 (l.773) `generation`, the highest assigned kept while any information of the key is held; §2.1.12 the triple (key, generation, version); §2.4 lifecycle items 1–5 and history keyed by (generation, version); §3.1.2 rule 4 (l.1108) preconditions on the live entry; §3.2.1 one entry per generation; §7.1 `generation` REQUIRED in state_set, state_delete, state_purge. Harness R17 (a)–(h) (`runtime_harness.py` l.1914 `StateStore`, l.2064 `r17`); ITV-677, ITV-678, ITV-679, ITV-681 executed by R17; INV-81, INV-82, INV-84 | (a) generation restarts at 1 → R17 (a), (b); (b) `expected_generation` ignored → R17 (d); (d) absent details carry `current_version` → R17 (g); (e) numbering restarts after PURGE → R17 (h); (f) next = highest retained + 1 → R17 (h) partial removal; (h) `generation` out of the state_set conditional → A-59 guard and INV-84 | yes |
| A-88 | `created_at` rule consistent with recreation (State §2) | §2.1.5 (l.538): creation time of this entry (generation), immutable for its lifetime, a recreation has its own `created_at`, retention of earlier generations neither changed nor renewed; disposition (LM3) unchanged; R17 (a) "recreation leaves the first generation's created_at unchanged (A-88)" | (a) → R17 (a) | yes (by clarification and disposition) |
| A-93 | Every `$ref` of every schema resolves by `$id` | 4 `$ref`s → `arsia-state-entry.schema.json`; `schemas/README.md` convention; `check_consistency.py` l.771 `unresolved_refs` (registry by `$id` only, nested `$id` bases, fragments, relative refs) with planted-reference self-test; INV-88 and ITV-677 validate entries through the resolved reference | (g) a `$ref` back to `…/state-entry/v1.0.json` → "every $ref in every schema resolves by $id" | yes |
| A-94 | PURGE repetition distinguishes retransmission, repetition without a later write and PURGE after a later write | §3.2.2 Idempotency (l.1531) rules 1–3, step 4 "of every generation", `state_purge.generation` (latest covered) REQUIRED; R17 (i) three cases; ITV-680 | (c) idempotency per key again → R17 (i) PURGE after a later write | yes |
| A-95 | Conflict-details schema equal to State §8.4 | §8.4 (l.3684) live and absent details; `arsia-message.schema.json` `error-details-conflict-version` (current_generation, current_version, updated_at, updated_by required; one stated precondition) and `error-details-conflict-absent` (`entry_live: false`, closed to the stated preconditions), selected by any concurrency member and by `entry_live`; ITV-82, ITV-151 valid; ITV-87, INV-86, INV-87, INV-89, INV-90, INV-91 invalid for their single stated cause; other `conflict` vectors (ITV-334, ITV-335, ITV-374 and those without details) keep their results | (i) live branch selected by `current_version` only → INV-89 accepted; (j) absent branch open → INV-91 accepted | yes |

**Mutations.** 10/10 detected:

```
(a) recreation restarts generation at 1: DETECTED
(b) expected_generation ignored: DETECTED
(c) PURGE idempotency per key again: DETECTED
(d) absent-entry details carry current_version: DETECTED
(e) numbering restarts after PURGE: DETECTED
(f) next generation = highest retained + 1: DETECTED
(g) a $ref back to state-entry/v1.0.json: DETECTED
(h) generation out of the state_set conditional: DETECTED
(i) live branch selected by current_version only: DETECTED
(j) absent branch without additionalProperties false: DETECTED
```

**Vector migration (structural, by ID).**
- StateEntry `generation` (24 objects in 23 vectors): STV-02, STV-05 (2), ITV-21, 22,
  138, 183, 191, 192, 193, 195, 197, 199, 200, 203, 204 (generation 2), 205, 206, 250,
  252, 260, 261, 271, INV-42.
- `state_set` records: ITV-16, 220, 221, 269, 527, 542, 594, 598, 602, INV-54.
  `state_delete`: ITV-97, 223, 528. `state_purge`: ITV-103, 233, 237, 270, 529.
- Conflict details: ITV-82, ITV-151 (`current_generation`); ITV-87 restated (no
  precondition as single cause).
- Re-signed with real signatures: STV-02, STV-05, ITV-151.
- Chain: ITV-594 recomputed; tombstone ITV-595 (`previous_chain_value` and its own
  value) and ITV-596 recomputed; ITV-598, ITV-599, ITV-602 rederived; R14 passes with
  the stated reasons. The record that ITV-595 replaces is synthetic; its chain value is
  `chain_value(record, ITV-594.hash_chain)` for:
  `{"record_id": "d5c00595-0001-4001-8001-000000000595", "message_id": "d5c00595-0002-4001-8001-000000000595", "event_type": "response", "from_agent": "agent:arsialabs.demo.compliance-checker", "to_agent": "agent:arsialabs.demo.risk-assessor", "intent": "response", "payload_type": "com.example.notes/delete", "payload_hash": "5555555555555555555555555555555555555555555555555555555555555555", "processed_at": "2026-09-28T10:20:00.000Z", "operator_id": "urn:lei:529900HNOAA1KXQJUQ27", "chain_id": "d5c00592-0000-4000-8000-000000000592", "chain_seq": 4, "chain_format": 1}`.
- New: ITV-676..681, INV-81..91 (17). Message vectors (7) signed for real:
  INV-86, INV-87, INV-89, INV-90, INV-91, ITV-678, ITV-679.

**Counts before → after.**
- Vectors 783 → 800 (validator 457 / 178 / 148 → 463 / 189 / 148; formats message-only
  313 → 320, schema-ref 466 → 476, hybrid 4); crypto-checked 114 → 121; 0 failures in
  all four modes.
- RTM 1970 / 1173 → 1981 / 1182 (11 rows added, 8 rewritten); State coverage summary
  recomputed (427 rows).
- Consistency checks 122 → 124; harness R1-R16 → R1-R17; example blocks 78 → 79.
- Findings register 95 → 98 rows: open 17 → 15, IPC 3, closed 75 → 80 (5 → 6 by
  disposition); class 1 48 → 51; triage CONF 48, PART 17, INT 7, new 23 → 26 (A-79
  keeps `new (C3b)`); disposition per DR or cycle addendum 16 → 20, recorded 18,
  pending 61 → 60.
- Coverage register 18 → 20 rows: open 14, closed 4 → 6.
- Named conformance tests 83 → 85 (STATE-16, STATE-17).

## 19. Retention-axis cycle closure evidence

Execution baseline `d5246ff`. Owner decisions R1–R4 are in the design record (DR-4
addendum, retention-axis cycle). Line references are to the files after the cycle.
Official texts are the EUR-Lex consolidations in the sources folder (`consolidated/`),
consulted 2026-11-03. Mutations ran on a scratch copy: `git archive d5246ff` with the
full candidate diff applied, the unmutated copy first passing the whole battery, and the
candidate restored between cases; the repository was not touched and no early commit
was made.

| Finding | Closure criterion (clause) | Evidence | Mutation → failing check | Met |
|---|---|---|---|---|
| A-7 | Aligned PURGE/retention quotes (Core §13.1 #9, State §3.2.2/§5.3.2) | Core §13.1 #9 (l.3872): a PURGE within retention is rejected without a `retention_override`; mitigation and its limit (attributable, not lawful). State §3.2.2 (l.1520) "Retention override" items 1–7: evaluation from stored state over every generation whose values are removed, live entry or not; `entry_retained_until` the latest instant; rejection with the §8.4 details (l.3813); record fields; determination retrievable; override not verified; record retention untouched; idempotency unchanged. Args table (l.1446). §1.2, §2.1.8, §4.1.1 (l.1793), §4.1.2 exception rows (l.1854–1899), §5.3.1 Step 4 (l.2187), §5.3.2 (l.2199), §8.2.1 and Actions §1.4 (l.489) aligned; docs/FAQ.md non-delegable and elevated-capability answers aligned (no "bypassing retention safeguards", no universal MiFID II five-year requirement). Schemas: common `retention-override`; `purge-args`; audit-record `within_retention`, `entry_retained_until`, `retention_override` (REQUIRED, and `entry_retained_until` non-null, when `within_retention` is true); message `error-details-retention-override`. R18 (b)–(j), where (i) validates the completed `state_purge` records (with `pii_classification` and `obligation_resolution`) against arsia-audit-record before comparing their retention fields; ITV-682..687, INV-92..100 | (a)–(e), (g)–(i), (k), (l), (n) | yes |
| A-70 | MIFID-II floor re-grounded with scope, anchor and day-count justified, or the floor and its attributions corrected; all echoes aligned | Catalog: `retention_basis` `"profile_floor"`, `retention_reference` `"MIFIR:25(1); MIFID-II:16(7)"`, references gain MiFIR Art. 25(1) and MiFID II Art. 16(6), Art. 72 relabelled (medium and form). State §6.3 (l.2567): MiFIR Art. 25(1), MiFID II Art. 16(7) and the ARSIA extension and anchor stated apart; value P1827D a profile policy, 0–2 days above P5Y; 2017/565 Art. 72 not a source of the period. Echoes: Core §1.1 (l.187), §4.3.8 Rule 4 (l.1362), [MiFIR] reference (l.4221); Actions references (l.3007); Assets §1.1.6 (l.189), §6.1.2 (l.2009), §6.1.4 (l.2057), ASSETS-07 (l.2681), §8.2 (l.2800); Identity §9.3 (l.1962); Routing §7.4.2 (l.2232); State §4.1.1, §4.1.2, §5.3.2, §7.3 (l.3560), §12.2 (l.4251); `arsia-mifid-audit-record.schema.json` description; README, profiles/README, FAQ. R18 (a) | (f), (j) | yes |
| A-90 | Retention-precedence citation verified against the official text | MiFID II Art. 72 heading "Exercise of supervisory powers and powers to impose sanctions" (X-2). State §7.1 `operator_id` note (l.3283): MiFIR Art. 25(1) as the example, erasure assessed under Art. 17(3)(b) per §5.3.2, the protocol does not determine that retention prevails | — (prose) | yes |
| A-44 | Corrected MiFID II / 2017/565 citations (remaining gap: retention attributions, tracked as A-70) | The five-year attributions name MiFIR Art. 25(1) and MiFID II Art. 16(7) for the records they cover; general record-keeping is Art. 16(6); 2017/565 Art. 72 is medium and form with no period (X-3); same echo list as A-70 | — (prose) | yes |

**Official excerpts (verbatim; `…` marks an omission).**
- MiFIR (Reg. (EU) No 600/2014, consolidation 2025-11-23) Art. 25(1): "Investment firms
  shall keep at the disposal of the competent authority, for five years, the relevant
  data relating to all orders and all transactions in financial instruments which they
  have carried out, whether on own account or on behalf of a client. In the case of
  transactions carried out on behalf of clients, the records shall contain all the
  information and details of the identity of the client …"
- MiFID II (Dir. 2014/65/EU, consolidation 2026-06-06) Art. 16(6): "An investment firm
  shall arrange for records to be kept of all services, activities and transactions
  undertaken by it …". Art. 16(7): "The records kept in accordance with this paragraph
  shall be provided to the client involved upon request and shall be kept for a period
  of five years and, where requested by the competent authority, for a period of up to
  seven years." Art. 72 heading: "Exercise of supervisory powers and powers to impose
  sanctions".
- Del. Reg. (EU) 2017/565 (consolidation 2022-08-02) Art. 72 heading: "Retention of
  records (Article 16(6) of Directive 2014/65/EU)"; Art. 76(11): "The period of time for
  the retention of a record shall begin on the date when the record is created."
- GDPR (Reg. (EU) 2016/679) recital 26: "Personal data which have undergone
  pseudonymisation, which could be attributed to a natural person by the use of
  additional information should be considered to be information on an identifiable
  natural person." Art. 17(3)(b): "for compliance with a legal obligation which requires
  processing by Union or Member State law to which the controller is subject …"

**P1827D against P5Y (R18 (a)).** Over the 146,097 anchors 2000-01-01..2399-12-31,
`add_duration(a, "P1827D") − add_duration(a, "P5Y")` is 0 days for 34,310 anchors,
1 day for 108,499 and 2 days for 3,288; never negative. Example: 2097-03-01 + P5Y =
2102-03-01, + P1827D = 2102-03-03 (2100 is not a leap year). The owner's independent run
gave the same distribution.

**Mutations.** 14/14 detected:

```
(a) evaluation considers only the live generation: DETECTED (R18 (d), (e))
(b) entry_retained_until is the minimum: DETECTED (R18 (e))
(c) PURGE within retention proceeds without override: DETECTED (R18 (b))
(d) evaluation counts generations already erased: DETECTED (R18 (j))
(e) remove_generation leaves the generation's values: DETECTED (R18 (h))
(f) P1827D becomes P1826D in the margin check: DETECTED (R18 (a))
(g) within_retention -> retention_override conditional removed: DETECTED (INV-92)
(h) purge-args without additionalProperties: DETECTED (INV-99)
(i) retention details without additionalProperties: DETECTED (INV-98)
(j) old MIFID-II digest back in one vector (ITV-96): DETECTED (digest guard)
(k) within_retention true accepts entry_retained_until null: DETECTED (INV-100)
(l) override alters the record's retention: DETECTED (R18 (i))
(n) completed state_purge record without obligation_resolution: DETECTED (R18 (i) schema validation)
(m) R17 selects every state vector again: DETECTED (R17 presence)
```

**Vector migration (structural, by ID).**
- `state_purge` records gain `within_retention: false` and `entry_retained_until: null`:
  ITV-103, 233, 237, 270, 680 (R17 scenario, from the reference store), ITV-529 and
  INV-85 (each still invalid by its own single cause).
- MIFID-II `profile-floor` digest (two occurrences each, no `crypto` block): ITV-88, 89,
  90, 91, 92, 95, 96, 525, 586, INV-47. ITV-95 `hash_chain` recomputed with
  `chain_value` (position 1); no vector chains from it. ITV-92 and INV-47 keep their
  single cause.
- New: ITV-682..687, INV-92..100 (15). Scenario vectors ITV-683..687 run in R18;
  ITV-685, INV-97 and INV-98 are signed for real. Each new or migrated schema negative
  has exactly one schema error; INV-97 and INV-98 have one leaf error under
  `payload.error.details`.
- The only `state_purge` records without the two fields are INV-93 and INV-94.

**Sweeps.** No occurrence of "16(7)" attributes a general period, and no occurrence of
"Art. 72" presents a source of a period (spec, profiles, schemas, README, FAQ, RTMs). No
"regulatory minimum" or "required by the applicable regulation" describes a profile
floor. No vector carries the old MIFID-II digest. The remaining "(5 years)" label is
DORA's (A-96).

**Counts before → after.**
- Vectors 800 → 815 (validator 463 / 189 / 148 → 469 / 198 / 148; formats message-only
  320 → 323, schema-ref 476 → 488, hybrid 4); crypto-checked 121 → 124; 0 failures in
  all four modes.
- RTM 1981 / 1182 → 1986 / 1189 (7 rows added, 2 retired, 9 rewritten: 8 State, 1 Core); State
  coverage summary recomputed (432 rows).
- Consistency checks 124 → 124; harness R1-R17 → R1-R18; example blocks 79 → 80.
- Findings register 98 → 99 rows: open 15 → 13, IPC 3 → 2, closed 80 → 84 (6 by
  disposition); class 3 17 → 18; triage new 26 → 27; disposition per DR or cycle
  addendum 20 → 24, recorded 18, pending 60 → 57.
- Regulatory register 34 → 37 rows (X-1..X-3).
- Coverage register 20 → 22 rows: open 14, closed 6 → 8.
- Named conformance tests 85 → 86 (STATE-18).

## 20. Relay/DPoP cycle closure evidence

Execution baseline `24b32ed`. Owner decisions P1–P3 are in the design record (DR-5
addendum, relay/DPoP cycle). Line references are to the files after the cycle. RFC 9449
was read on rfc-editor.org (`rfc9449.txt`) on 2026-11-04; the points relied on are
summarised below by section, not quoted. Mutations ran on a scratch copy: `git archive
24b32ed` with the full candidate diff applied, the unmutated copy first passing the whole
battery, and the candidate restored between cases; the repository was not touched and
no early commit was made.

| Finding | Closure criterion (clause) | Evidence | Mutation → failing check | Met |
|---|---|---|---|---|
| A-89 | `relay_latency_ms` derivation stated in Routing §7.4.2 | Routing §7.4.2 "Relay timing and outcome" (l.2262): `forwarded_at` the start of the forwarding attempt; `relay_latency_ms` = `forwarded_at` − `received_at`, exact whole non-negative milliseconds, to the initiation of forwarding; `attestation_id`, `forwarded_at` and `relay_latency_ms` present together when forwarding was initiated, absent otherwise; `forwarding_result` defined (`success` = delivery, `timeout`, `failure`). §7.3 Rule 7 (l.2144): a record for every message received for relay, including messages rejected before forwarding (a normative decision of the cycle); Rule 9 (l.2178) MUST record the timeout without forwarding fields. Echoes: §1.2.2 step 9 (l.395), §2.3.3 "Relay error" (l.1125), Core §9.2 item 4 (l.3214), State §7.1 extension row (l.3370). Schema: `broker_relay` conditional with the five unconditional fields and `dependentRequired` over the three forwarding fields; `success` requires them. ROUTING-11 (l.2450). R19 (a)–(e); 10 vectors migrated, ITV-688, ITV-689, ITV-691, INV-101..103 | (a)–(d), (l) | yes |
| A-49 | Receiver-check lists aligned with RFC 9449 §4.3; DPoP schema accepts nonce (remaining gap: Identity §3.3 checks 1-3, 7 and 10; Core §6.3 `typ`/`alg`) | Identity §3.3 (l.534): one normative list, checks 1–12 of RFC 9449 §4.3 with the ARSIA profile marked apart (EdDSA/Ed25519, `POST`, the Core §8.3 window) and check 13 (single-use `jti`, an ARSIA requirement); nonce precedence (a request lacking an acceptable nonce, the first included, gets the challenge whichever check detects it); "Single-use `jti`" (l.583: per target URI without query and fragment, atomic and shared across instances, held until `iat` + S); "Server-provided nonce" (l.603: RFC 9449 §9 challenge, §8.2, §11.3); "Retransmission" (l.614). Core §6.3 item 4 (l.2322) a normative reference; Core §13.2.2 (l.3945). Routing §2.3.3 "Recipient DPoP nonce challenge" (l.1158), §2.3.2 item 4 (l.1071), §1.2.2 (l.307, l.334, l.405); Identity §9.2 (l.2011); Assets (l.2359). Schemas: message `error-details-relay-failed` gains `dpop_nonce` and `dpop_nonce_htu` with both conditionals; dpop-proof descriptions point to Identity §3.3. IDENTITY-23 (l.805), ROUTING-12 (l.2461). R20 (a)–(k); INV-104..107, ITV-690, INV-108..110 | (e)–(k), (m)–(z) | yes |

**RFC 9449 points relied on (summary, by section).**
- §4.3: the twelve checks of a DPoP proof (one header field; a single well-formed JWT;
  the §4.2 claims; `typ`; an asymmetric registered `alg`; the signature under `jwk`; no
  private key in `jwk`; `htm`; `htu` ignoring query and fragment; the nonce when one was
  provided; the creation-time window; `ath` and the key binding of the token), in any
  order, with normalisation of `htu` recommended.
- §7.3: a unique proof is recommended even when retrying.
- §8.2 and §9: a resource server provides a nonce with HTTP 401, `WWW-Authenticate: DPoP
  error="use_dpop_nonce"` and `DPoP-Nonce`, and may provide a new one later; a nonce is
  accepted only by its issuer.
- §11.1: `jti` tracking per target URI is described as strong but optional; nonces may be
  reused while `jti` values are not.
- §11.3: once a nonce has been provided, proofs without the nonce claim are not accepted.

**R19 and R20 cases.**
- R19: (a) every valid `broker_relay` record of the corpus; (b) no invalid one carries a
  timing defect besides its declared cause; (c) the Routing §7.4.2 example (47 ms);
  (d) latency off by one, forwarding before receipt, `success` without the fields,
  partial fields detected, a record of a message not forwarded clean; (e) the schema
  accepts exactly the structurally sound records.
- R20 (real Ed25519 proofs, `ath`, RFC 7638 `jkt`): (a) valid proof accepted; (b) checks
  1–9, 11, 12 (both halves) and 13 each rejected by that check with a generic
  `unauthorized` and no challenge headers, zero header fields included; validly signed
  proofs with malformed members (`jwk` null, `iat` a string, `htu` null, `jti` a list,
  `htu` with an invalid port) rejected by checks 5, 3, 3, 3 and 9 with a controlled
  response, never an exception; (c) query and
  fragment ignored; (d) replay rejected for the same target URI, also through a query or
  fragment variant, and accepted for another URI; (e) a proof with `iat` = t0 + S still
  rejected as a replay at t0 + S + 1; (f) after `iat` + S check 11 fails; (g) a receiver
  requiring a nonce answers the first request, a missing nonce and an unaccepted nonce
  with the 401 challenge (both headers), accepts the provided nonce (and its reuse with a
  new `jti`), and answers a correct nonce with another failure with a generic
  `unauthorized`; a `jti` already accepted with an unaccepted nonce is rejected by check 13,
  not challenged; a challenge to a new `jti` records nothing, so the retry with the
  nonce and that `jti` is accepted; a nonce claim of the wrong type is challenged;
  (h) a retransmission with a new proof accepted, the re-sent proof
  rejected; (i) generated header and payload valid against arsia-dpop-proof; (j) the
  brokered flow — challenge returned to the sender with the recipient's nonce and inbox
  URL (valid against arsia-message), not in the broker's own `DPoP-Nonce`, attempt
  recorded as `failure` with the forwarding fields, the old proof delivered once, the
  retry with a new proof delivered and recorded as `success` with a new
  `attestation_id`; the broker parses `WWW-Authenticate` (RFC 9110 §11.3, §11.6.1)
  instead of matching one string: a DPoP challenge with `error_description` (RFC 9449
  Figure 24), or after another challenge — with auth-params, with no parameters, or with
  a token68 — with lower-case header names, keeps reason, nonce and URI in the relay
  error, and a challenge without a
  `DPoP-Nonce`, another DPoP error or an unparseable header gives the generic relay
  error without an exception; (k) two concurrent verifications of one proof on the shared reference
  store, interleaved after the lookup: exactly one accepted.
- Limit: R20 demonstrates the atomic claim of the reference store and the key and
  retention contract; it does not demonstrate the distributed infrastructure of a
  deployment, which remains a runtime obligation.

**Owner review findings (2026-11-04), fixed before commit.** The first candidate's
harness (a) recognised a recipient challenge only as the literal string
`DPoP error="use_dpop_nonce"`, so a valid challenge with `error_description` fell to
the generic relay error and lost the nonce, and the minimal challenge without
`DPoP-Nonce` raised `KeyError`; (b) used `jwk`, `iat`, `htu` and `jti` before checking
their type, so validly signed proofs with those members malformed raised exceptions
(the schemas already rejected the four inputs; the verifier did not apply equivalent
checks); (c) returned the nonce challenge before check 13, so a `jti` already accepted
with an unaccepted nonce was challenged instead of rejected (no replay was accepted).
The battery did not cover these cases. Fixes: a `WWW-Authenticate` parser and the
complete-challenge condition (`recipient_nonce`); type checks before use (checks 3 and 5;
an invalid `htu` port fails check 9); a non-recording `accepted` lookup before the
challenge, the atomic `claim` unchanged. Regressions: R20 (b) malformed proofs, R20 (g)
6–8, R20 (j) 6; mutations (t)–(x) restore each pre-fix behaviour. Core §6.3 item 4
(l.2322) now states the nonce-challenge exception, and CORE-§6.3-03 follows it.

**Second owner review (2026-11-04), fixed before commit.** The parser required a space or
the end of the field after a scheme and had no token68 alternative, so
`Negotiate, DPoP error="use_dpop_nonce"` and `Negotiate YWJjZA==, DPoP
error="use_dpop_nonce"` (both valid under RFC 9110 §11.3 and §11.6.1) did not parse and
the broker returned the generic relay error, losing the DPoP challenge. The parser now
follows `challenge = auth-scheme [ 1*SP ( token68 / #auth-param ) ]` in a `#challenge`
list (empty elements skipped; after a comma, an element that is not an auth-param starts
the next challenge). Regressions: the two forms in R20 (j) 6, which now also requires
`dpop_nonce_htu`; mutations (y) and (z).

**Mutations.** 26/26 detected:

```
(a) a valid vector's latency +1: DETECTED (R19 (a))
(b) relay_record_problems ignores partial presence: DETECTED (R19 (d))
(c) dependentRequired removed: DETECTED (INV-102)
(d) success conditional removed: DETECTED (INV-101)
(e) JtiStore with a fixed TTL from first receipt: DETECTED (R20 (e))
(f) jti scope without the target URI: DETECTED (R20 (d), another URI)
(g) proof without nonce accepted after one was provided: DETECTED (R20 (g) 2)
(h) htu compared with query and fragment: DETECTED (R20 (c))
(i) ath check skipped: DETECTED (R20 (b) check 12)
(j) jwk additionalProperties removed: DETECTED (INV-104)
(k) recipient_dpop_nonce conditional removed: DETECTED (INV-108)
(l) State broker_relay row back to the old REQUIRED list: DETECTED (A-59 guard)
(m) broker turns the challenge into the generic relay error: DETECTED (R20 (j) 1)
(n) broker re-sends the old proof: DETECTED (R20 (j) 4)
(o) broker presents the recipient nonce as its own DPoP-Nonce: DETECTED (R20 (j) 2)
(p) JtiStore splits lookup and recording: DETECTED (R20 (k))
(q) store key uses the raw request URI: DETECTED (R20 (d), query variant)
(r) first request without nonce gets a generic unauthorized: DETECTED (R20 (g) 1)
(s) missing nonce detected by check 3 gets a generic unauthorized: DETECTED (R20 (g) 2)
(t) broker matches the challenge as one literal string (pre-fix): DETECTED (R20 (j) 6)
(u) claim types not checked before use (pre-fix): DETECTED (R20 (b) malformed)
(v) jwk shape not checked before use (pre-fix): DETECTED (R20 (b) malformed)
(w) nonce challenge before the jti check (pre-fix): DETECTED (R20 (g) 6)
(x) the challenge consumes the jti: DETECTED (R20 (g) 7)
(y) parser rejects a challenge without parameters before a comma (pre-fix): DETECTED (R20 (j) 6)
(z) parser does not accept token68 (pre-fix): DETECTED (R20 (j) 6)
```

R20 (k) passed in five consecutive runs of the harness.

**Vector migration (by ID).**
- `relay_latency_ms` 12 → 50 (timestamps kept): ITV-43, ITV-44 (still invalid only by
  `forwarding_result: "dropped"`), INV-48 (still invalid only by the missing
  `broker_agent_id`).
- `forwarded_at` = `received_at` + `relay_latency_ms` (it had been set to
  `processed_at`, days later): ITV-146 (245 ms), ITV-147 (5000 ms), ITV-490 (35),
  ITV-492 (47), ITV-511 (23), ITV-515 (15).
- ITV-508 (Rule 1, not forwarded): `attestation_id`, `forwarded_at` and
  `relay_latency_ms` removed; still valid.
- Descriptions: ITV-43, ITV-146, ITV-147, ITV-508; ITV-451 ("§3.3 steps 1-6" →
  "checks 1-13").
- New: ITV-688..691, INV-101..110 (14); no `crypto` block (the relay errors follow
  ITV-517, unsigned). Each new schema negative has exactly one cause (INV-101: the three
  forwarding fields required; INV-102/103: `dependentRequired`); INV-108..110 have one
  leaf error under `payload.error.details`.

**Sweeps.** The two "as defined in §7.4.2" references of Rule 7 resolve to the new
definition. No DPoP verification list remains outside Identity §3.3 (Core §6.3 refers to
it). No "§3.3 step" reference remains. RFC section citations in the new text use the
`[RFC NNNN] §N` form on one line, so that `check_links.py` treats them as external
instead of resolving them, by coincidence, to sections of the citing document.

**Counts before → after.**
- Vectors 815 → 829 (validator 469 / 198 / 148 → 473 / 208 / 148; formats message-only
  323 → 327, schema-ref 488 → 498, hybrid 4); crypto-checked 124 → 124; 0 failures in
  all four modes.
- RTM 1986 / 1189 → 2020 / 1217 (34 rows added: Routing 9, Identity 23, Core 2; 9
  rewritten: Routing 6, Identity 2, Core 1; ROUTE-§7.3-30 SHOULD → MUST). Coverage summaries of the Routing, Identity
  and Core RTMs recomputed from their tables (273 / 297 / 404 rows).
- Consistency checks 124 → 124; harness R1-R18 → R1-R20; example blocks 80 → 81.
- Findings register 99 rows: open 13 → 12, IPC 2 → 1, closed 84 → 86 (6 by
  disposition); disposition per DR or cycle addendum 24 → 26, recorded 18 → 17, pending
  57 → 56.
- Regulatory register 37 → 40 rows (T-10..T-12).
- Coverage register 22 → 24 rows: open 14, closed 8 → 10.
- Named conformance tests 86 → 89 (ROUTING-11, ROUTING-12, IDENTITY-23).

## 21. Tools cycle closure evidence

Execution baseline `f618891`. Owner decisions F1–F4 are in the design record (DR-0
addendum, tools cycle). Line references are to the files after the cycle. Mutations
ran on a scratch copy: `git archive f618891` with the full candidate diff applied, the
unmutated copy first passing the whole battery, and the candidate restored between
cases; the repository was not touched and no early commit was made. No key material
was printed.

| Finding | Closure criterion (clause) | Evidence | Mutation → failing check | Met |
|---|---|---|---|---|
| A-33 | Executed alg/key-mismatch vector asserted to fail | INV-111 (Ed25519 key, `alg: "ES256"`) and INV-112 (P-256 key, `alg: "RS256"`), message-only, `skip_schema`, `expect_signature: "invalid"`. The wrong alg is in the envelope before the signing input is computed; each signature is valid for the key's own algorithm (Ed25519, ES256) over those bytes. `validate_vectors.py --check-crypto` asserts both negatives (126 checked: 119 verified, 4 negatives, 3 canonical only); `_verify_signature` (l.230) rejects them with "incompatible with". Guard `alg_mismatch_problems` (`check_consistency.py` l.596): bytes == signing input with the declared alg, `security.sig` == `crypto.signature_base64url`, verification under the key's algorithm, rejection for incompatibility. Coverage `executed: --check-crypto` for INV-18, INV-19, INV-111, INV-112, admitted by the A-65 guard only for signature negatives (l.785), with a synthetic negative control (l.1435). RTM CORE-§5.2-13 (new), CORE-§5.2-07, IDENT-§3.1-08 | (a)–(d) | yes |
| A-40 | Generator dry-run validated against v2 schemas; envelope_hash used or documented | Disposition: `scripts/gen_state_vec2.py` retired (removed with its scripts/README entry). It was not ported and no dry run of it passed; the criterion's dry run no longer applies because the generator no longer exists and the corpus is the maintained source of ITV-215..277. Before removal: 63 vectors; 18 gave an outcome different from their declared expectation under the current schemas; 19 differed from the corpus in `message`/`data` (all 63 differ as whole objects, by `req_ids`). `stringify_amounts` (two decimals for every currency) removed with the one-shot migration of `scripts/regen_v2.py`, now a selective re-signer (`eligibility` l.110, `resign` l.125, `main` l.171; `_sign` l.92 the only signing function). `envelope_hash` (l.55) documented: purpose (Routing §7.4.1), no consumer, does not verify an attestation on its own, coverage with A-56 — not A-56 evidence. Contract guard `resigner_contract_problems` (l.819) | (e)–(n) | yes |

**The removed `--apply` migration, simulated in memory at `f618891`.** It would have
changed three vectors and the file format: INV-41 (adding `root_request_id`, the very
field whose absence makes it a negative), ITV-551 and INV-18 (re-signed in ES256, a
different signature each run), and a final newline the corpus does not have. Its dry
run reported "migrated envelopes: 1" (INV-41) and "re-signed: 124".

**Re-signer contract (guard cases).** Run on temporary copies; "nothing written" is
observed by `st_mtime_ns` and hash, so an identical rewrite also counts.
- (a) dry run on CTV-02: exit 0, nothing written.
- (b) `--apply` on CTV-02 (EdDSA, deterministic): file identical byte for byte (format
  and the absent final newline kept).
- (c) `--apply` on ITV-551 (ES256): only its three signature fields change, the new
  signature verifies, the other vectors are identical.
- (d) unknown ID and (e) INV-18 (`invalid`), INV-15 (`absent`) with `--apply`: refused,
  nothing written.
- (f) mixed batch `CTV-02,INV-18` on a copy where CTV-02 was edited (so re-signing it
  would change the file): refused, nothing written.
- (g) a `public_key_hex` the private key does not derive: refused with "refused before
  signing", nothing written.
- (h) edited CTV-02 (`payload.args` changed, old crypto fields kept): the dry run writes
  nothing; `--apply` keeps the edit, recomputes the canonical bytes from the edited
  envelope, produces a verifying signature, changes only the three signature fields,
  and leaves every other vector identical.
- (i) in process, `_sign` replaced by a version that flips one byte, correct key pair:
  refused with "signature does not verify", nothing written.
- (j) a file the serializer would normalise — the `id` of the unselected CTV-01 written
  as `"\u0043TV-01"` (semantically identical), or CRLF line endings: `--apply --ids
  CTV-02` is refused ("byte for byte"), nothing written.

In (c) and (h) the other vectors are compared as objects and both files must be in the
one byte format the serializer reproduces; together, the other vectors are equal byte
for byte.

**Owner review (2026-11-05), fixed before commit.** The first candidate read the corpus
as text and re-serialised the whole document, so a semantically identical input in
another format (an escaped `id` of an unselected vector, CRLF) was rewritten: CTV-01's
representation changed while CTV-02 was reported "unchanged", and CRLF became LF. The
guard compared the other vectors only as objects. Fix: `main` reads bytes and refuses,
before any write, a file whose serialisation does not reproduce its bytes; it writes
bytes (`serialize`). Regressions: contract case (j) and the byte-format condition in
(c) and (h); mutation (n). Four published counts left behind are corrected: README.md
"815 test vectors" (now 831) and "1,986 rows" (twice), docs/getting-started.md "1,986
rows" (now 2,021).

The prior check (key pair and compatibility) and the final verification have distinct
purposes and are tested separately: (g) and mutation (i) for the first, (i) and
mutation (m) for the second. For a mismatched key pair the final verification is
redundant, which does not make it dispensable.

All 119 valid signed vectors re-sign under the new tool (dry run on a copy): 118
unchanged, ITV-551 re-signed (ES256). The real dry run `regen_v2.py --ids CTV-02` left
the corpus bytes, `git status --porcelain` and `git diff` as they were.

**Mutations.** 14/14 detected:

```
(a) the verifier selects the algorithm from the key type again: DETECTED (--check-crypto: INV-111, INV-112 verified)
(b) INV-111 signed before the alg was set to ES256: DETECTED (alg_mismatch_problems: no verification under the key's algorithm)
(c) INV-112 security.sig differs from crypto.signature_base64url: DETECTED (alg_mismatch_problems)
(d) coverage guard accepts executed: --check-crypto for any vector: DETECTED (coverage guard self-test)
(e) re-signer writes (identical content) despite an unknown ID: DETECTED (contract (d), mtime)
(f) re-signer accepts expect_signature 'invalid': DETECTED (contract (e))
(g) re-signer appends a final newline: DETECTED (contract (b))
(h) re-signer writes the valid IDs of a mixed batch before refusing the invalid one: DETECTED (contract (f))
(i) re-signer without the prior key-pair check: DETECTED (contract (g): reason becomes the final verification)
(j) re-signer also changes another envelope field (ts): DETECTED (contract (b), (c), (h))
(k) re-signer reuses the stored canonical bytes: DETECTED (contract (h))
(l) re-signer keeps the old security.sig in the envelope: DETECTED (contract (c), (h))
(m) re-signer without the final verification of the produced signature: DETECTED (contract (i))
(n) re-signer without the byte-format pre-check: DETECTED (contract (j): escaped id of CTV-01 rewritten)
```

**Sweeps.** No reference to `gen_state_vec2.py` remains in `scripts/`, `.github/`,
CLAUDE.md, README.md, CONTRIBUTING.md or `test-vectors/` (historical documents and
`docs/generated/` unchanged). `regen_v2.py` has no `migrate_message` or
`stringify_amounts`. The only signature negatives are INV-18, INV-19, INV-111 and
INV-112. CLAUDE.md now states the Draft-02 signing profile (only `security.sig`
removed) where it said "minus its `security` field".

**Counts before → after.**
- Vectors 829 → 831 (validator 473 / 208 / 148 → 473 / 208 / 150; message-only 327 →
  329); crypto-checked 124 → 126 (119 verified, 2 → 4 negatives, 3 canonical only); 0
  failures in all four modes.
- Skip classification 148 → 150 rows (crypto-behaviour 7 → 9); INV-18 and INV-19
  coverage `none — conformance test` → `executed: --check-crypto`, automation candidate
  `yes` → `—`.
- RTM 2020 / 1217 → 2021 / 1218 (CORE-§5.2-13 added; CORE-§5.2-07, IDENT-§3.1-08 gain
  INV-111/112); Core coverage summary recomputed (405 rows).
- Consistency checks 124 → 126 (re-signer contract; coverage guard self-test); harness
  R1-R20 unchanged.
- Findings register 99 rows: open 12 → 11, IPC 1 → 0, closed 86 → 88 (6 by
  disposition); disposition per DR or cycle addendum 26 → 28, recorded 17, pending
  56 → 54.
- Coverage register 24 rows: open 14 → 13, closed 10 → 11.

## 22. DORA floor cycle closure evidence

Execution baseline `edf92c3`. Owner decisions D1–D2 are in the design record (DR-4
addendum, DORA floor cycle). Line references are to the files after the cycle.
Official texts are EUR-Lex files in the sources folder (`manifest.md`, batches of
2026-11-05); currency was read on each act's EUR-Lex page on 2026-11-05. Mutations ran
on a scratch copy: `git archive edf92c3` with the full candidate diff applied, the
unmutated copy first passing the whole battery, and the candidate restored between
cases.

| Finding | Closure criterion (clause) | Evidence | Mutation → failing check | Met |
|---|---|---|---|---|
| A-96 | DORA floor rationale verified against the official texts, or the floor and its attributions corrected; all echoes aligned | **Verified:** DORA Art. 6(5) provides for the ICT risk management framework to be documented and reviewed at least once a year (periodically for microenterprises), after major ICT-related incidents and after supervisory instructions or testing and audit conclusions, and for continuous improvement; it does not establish a retention period for the records covered by the profile. The CRD IV, CRR, Solvency II and IORP II consolidations read do not support a common financial-sector floor of five years (X-5). Delegated Regulation (EU) 2024/1774 Art. 12(2) and Art. 22(d), the latter as corrected by 32024R1774R(02), tie log and incident-evidence retention to purpose, criticality and risk assessment (X-6). **Corrected:** catalog DORA `retention_basis` `profile_floor` → `conservative_policy` (`retention_reference` "DORA:6(5)" kept as context); State §6.7 defaults row (l.2850), Art. 6 paragraph (l.2864), retention block (l.2899: Art. 6(5) sets no retention period for the records covered, `P1827D` a technical ARSIA policy, motivation, arithmetic margin and the 2024/1774 qualification apart); §4.1.2 DORA rows (l.1896); §7.2 (l.3567, the generic DORA mention withdrawn); §7.3 (l.3588); Core §4.3.8 Rule 4 (l.1364); Routing §7.4.2 (l.2321); README, profiles/README; RTM STATE-§4.1.2-06, STATE-§6.7-02. `P1827D` unchanged (D2). Guard `retention_parity_problems` (`check_consistency.py` l.819) | (a)–(d) | yes |

**Correction to the A-96 description.** The description registered in the
retention-axis cycle says the sources were not in the local folder. That was wrong for
DORA: `32022R2554.pdf` has been in the folder since 2026-09-25 (manifest row 4). CRD IV,
CRR, Solvency II, IORP II and Delegated Regulation 2024/1774 were downloaded on
2026-11-05. The description is kept as registered.

**Sources and currency.**
- DORA 2022/2554: original OJ text (L 333, 27.12.2022); EUR-Lex lists a consolidation
  that cannot be retrieved. On 2026-11-05: in force, no amending act, corrigenda
  R(01)–R(09) each listed for languages other than English, so the English text of
  Art. 6(5) is the OJ text; completed by delegated acts including 2024/1772 and
  2024/1774 (OD-4).
- CRD IV 2013/36 (consolidation 11.07.2026), CRR 575/2013 (26.06.2026), Solvency II
  2009/138 (17.01.2025; a consolidation dated 30.01.2027 is also listed) and IORP II
  2016/2341 (17.01.2025): the current consolidations on 2026-11-05.
- Delegated Regulation 2024/1774: original and consolidation 02024R1774-20240625,
  version 000.002, which incorporates corrigendum 32024R1774R(02) (OJ L 2025/90420,
  15.5.2025) as C1 (page 1 lists it; on page 23 Art. 22(d), marked ▼C1, already refers
  to Art. 8(2) of Delegated Regulation 2024/1772). The corrigendum replaces, in
  Art. 22(d), "in accordance with Article 15 of Commission Delegated Regulation (EU)
  2024/1772" by "in accordance with Article 8(2) of …"; Delegated Regulation 2024/1772
  has 13 articles, and its Art. 8(2) concerns recurring incidents considered together as
  one major incident.

**Excerpts relied on (2024/1774, short).** Art. 12(2)(a): "the identification of the
events to be logged, the retention period of the logs, and the measures to secure and
handle the log data, considering the purpose for which the logs are created". Checked
in the downloaded PDF together with the final subparagraph of Art. 12(2) and Art. 22(d)
(corrected text).

**Reading method.** The acts were read by text extraction from the PDFs, searching for
retention, record-keeping and period wording with a spacing-robust search; every
passage relied on was checked in context. In CRD IV the "five years" mentions concern
how long published sanctions stay on the authority's website and a retention period of
remuneration instruments; in CRR, the 10-year time window of the operational-risk loss
data set (Arts. 317–318); in Solvency II, Art. 162 requires a branch to keep its
records, with no period; in IORP II, the depositary keeps records of assets, with no
period.

**Mutations.** 4/4 detected:

```
(a) catalog DORA back to profile_floor: DETECTED (parity guard)
(b) State §6.7 retention_basis row back to the old text: DETECTED (parity guard)
(c) a profile's retention_minimum changed only in the catalog (DSA-VLOP P1096D -> P1095D): DETECTED (parity guard)
(d) a §6.x table loses its retention_basis row (DSA-VLOP): DETECTED (parity guard: no retention_basis row)
```

**Sweeps.** No remaining "CRD IV", "Solvency II" or "IORP II" as a retention ground,
"(5 years)" next to DORA, or "5-year DORA minimum" in spec/, profiles/, README, FAQ,
schemas and RTMs. The current DORA catalog digest appears in no vector.

**Counts before → after.**
- Vectors 831 → 831 (0 failures in all four modes); RTM 2021 / 1218 unchanged (2 rows
  rewritten); consistency checks 126 → 127; harness R1-R20 unchanged.
- Findings register 99 rows: open 11 → 10, closed 88 → 89 (6 by disposition);
  disposition per DR or cycle addendum 28 → 29, recorded 17 → 16, pending 54.
- Regulatory register 40 → 43 rows (X-4, X-5 defects; X-6 correct).

## 23. Coverage SC1 closure evidence

Execution baseline `ad871ac`. Owner decisions (programme split, K1–K4) are in the
design record (DR-0 addendum, coverage SC1). Line references are to the files after
the cycle. No key material was printed. Mutations ran on a scratch copy: `git archive
ad871ac` with the full candidate diff applied, the unmutated copy first passing the
whole battery, and the candidate restored between cases.

| Finding | Closure criterion (clause) | Evidence | Mutation → failing check | Met |
|---|---|---|---|---|
| A-54 | INV-37/38/39 with crypto blocks executed and asserted to fail | `--check-crypto` reads the `data` of the message and relay-attestation schemas (`crypto_envelope`, `validate_vectors.py` l.268) and fails a crypto block whose envelope it cannot locate. INV-37 (alg flipped EdDSA → ES256 after signing), INV-38 (kid swapped `#key1` → `#other-key` after signing; `#other-key` now published) and INV-39 (rebuilt: Ed25519 signature over the Draft-01 input, the envelope without its whole `security`) carry `expect_signature: "invalid"` and are asserted. Guard `tamper_negative_problems` (`check_consistency.py` l.653): each signature verifies over the pre-tamper bytes with the key really used and not over the presented envelope; `crypto.public_key_hex` is the catalog key of the envelope's kid; both signature copies agree. `kid_key_problems` (l.700): every crypto block with a published kid uses the catalog key; signature negatives and attestations name a published kid. Every signature negative carries the asserted signature: `--check-crypto` compares `security.sig` with `crypto.signature_base64url` before verifying, on the negative path too (`validate_vectors.py` l.363), and the guard compares them for every negative; self-test `negative_copy_selftest` (l.603) replaces only one copy of INV-124 and requires the mismatch to be reported | (a)–(d), (p), (q) | yes |
| A-55 | Executed (token, token_hash) match/mismatch vectors | Harness R21 (`token_binding` l.2923, `r21` l.2934): SHA-256 of the presented token's exact UTF-8 octets against `authorization.token_hash` — binding only, not token validity, authorization or DPoP. (a) the 40 corpus vectors with `authorization` bind their documented `synthetic-token:<ID>` (the binding holds; their messages may be invalid for another reason); (b) ITV-692 accept, INV-113 (another token) and INV-114 (trailing space) unauthorized, the token stated in `test_metadata.input.presented_token`; (c) exact octets: upper-case token accepted, trailing space, case change and another encoding rejected, no `authorization` → no binding. RTM CORE-§4.3.9-01 | (e1), (e2), (f) | yes |
| A-56 | Executed attestation vectors with tampered variants | Harness R22 (`verify_attestation` l.2963, `r22` l.3007): Routing §7.4.1 steps 2-5 and the replay rule; the attestation signature is verified inside the acceptance path with the validator's verifier; the clock skew is the envelope profile's (`skew_tolerance`; CTV-02 → EU-AI-ACT-HIGH-RISK, 120 s). ITV-569 rebuilt as a real attestation of CTV-02 (envelope_hash over the complete signed envelope, authorization_token_hash = the envelope's token_hash = hash of the presented token), signed with the published broker key `#2026q1`. ITV-693 redelivery (same attestation_id, same envelope_hash) accepted; INV-115 altered envelope, INV-116 attestation token hash, INV-117 presented token, INV-118 message_id, INV-119 valid_until + 180 s, INV-120 now = issued_at − 180 s, i.e. issued_at 180 s ahead of the recipient's clock (both outside with 120 s, inside with 300 s), INV-121 jurisdiction US, INV-122 no relay capability, INV-123 attestation_id reused for another envelope_hash, INV-124 policy_ref altered after signing (signature negative), INV-125 a foreign agent's key published in an adversarial JWKS of that vector only. R22 (b): binding, window, authorisation and replay negatives keep a valid signature; (c) a corrupted signature is rejected at step 2 with all else correct; (d) envelope_hash differs from a hash of the signing input. RTM ROUTE-§7.4-21..26 | (g)–(o) | yes |

**Keys.** `test-vectors/keypairs.json` 15 → 17: `agent:arsialabs.broker.eu-west`
(kid `#2026q1`, the kid the six broker fixtures ITV-569, INV-31, INV-32, ITV-570,
ITV-571, ITV-572 already used) and `agent:acme.echo-client#other-key` (the kid of
INV-38), both Ed25519, private key = SHA-256 of `"arsia-test-vectors keypair " + kid`.
An additional key of an agent is indexed by its kid; the 15 existing entries are
unchanged. At the baseline `ad871ac` no script in this repository read the file; from this
cycle `check_consistency.py` reads it (`_catalog_keys`, for the kid → catalog key guard).

**Mutations.** 19/19 detected:

```
(a) --check-crypto reads only message: DETECTED (FAIL crypto block without an envelope)
(b) INV-39 back to a Draft-02 signature: DETECTED (tamper guard: no verification over the Draft-01 input)
(c) INV-38 crypto.public_key_hex is the #key1 key: DETECTED (kid -> catalog key)
(d) INV-37 signed after the alg flip: DETECTED (tamper guard: no verification over the pre-tamper bytes)
(e1) R21 strips the presented token: DETECTED (R21 (b) INV-114; R21 (c) trailing space)
(e2) R21 lower-cases the presented token: DETECTED (R21 (c) upper-case token accepted)
(f) R21 always accepts: DETECTED (R21 (b) INV-113)
(g) R22 skips envelope_hash: DETECTED (R22 (a) INV-115)
(h) R22 checks the token hash against the envelope only: DETECTED (R22 (a) INV-117)
(i) R22 replay rejects any repetition: DETECTED (R22 (a) ITV-693)
(j) R22 replay ignores repetitions: DETECTED (R22 (a) INV-123)
(k1) R22 does not check the relay capability: DETECTED (R22 (a) INV-122)
(k2) R22 does not check the jurisdiction: DETECTED (R22 (a) INV-121)
(l) R22 does not verify the signature: DETECTED (R22 (a) INV-124; R22 (c))
(m) R22 no longer checks that the kid belongs to broker_id: DETECTED (R22 (a) INV-125)
(o) R22 uses the 300 s default skew: DETECTED (R22 (a) INV-119, INV-120)
(p) --check-crypto compares the signature copies only on the valid path: DETECTED (negative copy self-test)
(q) the negatives guard no longer compares the signature copies: DETECTED (negative copy self-test)
(n) envelope_hash computed without sig: DETECTED (R22 (a) ITV-569; R22 (d))
```

**Owner review correction.** The first implementation compared the two signature copies only
after a signature had verified, so a negative whose `crypto.signature_base64url` differed
from `security.sig` still passed `--check-crypto` (owner reproduction on INV-124: only the
crypto copy replaced by another invalid 64-byte signature; 145/145, guard silent, R22
passing). The comparison now runs before verification for every vector with an envelope
signature, an expected signature without an embedded one fails, and the negatives guard
repeats the comparison; mutations (p) and (q) reopen each side. The corpus already had
equal copies, so no vector changed.

**Inventory.** ITV-569 carries no placeholder signature or hash. The 40 bindings match.
The six `#2026q1` fixtures resolve to the published key. The signature negatives are
exactly INV-18, INV-19, INV-37, INV-38, INV-39, INV-111, INV-112 and INV-124. 24 crypto
blocks name a kid outside the catalog (pre-existing, e.g. INV-04 with a malformed kid,
ITV-134..137 for agents without a published key); among the blocks whose kid is
published, none differs from the catalog key.

**Counts before → after.**
- Vectors 831 → 846 (validator 473 / 208 / 150 → 475 / 208 / 163); crypto-checked 126 →
  145 (119 → 134 verified, 4 → 8 negatives, 3 canonical only); 0 failures in all four
  modes.
- Skip classification 150 → 163 rows (cross-object 5 → 12, crypto-behaviour 9 → 11,
  temporal 11 → 13, token 15 → 17); INV-37/38/39 coverage `none` → `executed:
  --check-crypto`; INV-113/114 `executed: R21`; INV-115..125 `executed: R22`.
- RTM 2021 / 1218 → 2028 / 1225 (CORE-§4.3.9-01; ROUTE-§7.4-21..26; CORE-§5.2-07 and
  IDENT-§3.1-08 gain INV-37/38/39); Core and Routing coverage summaries recomputed.
- Consistency checks 127 → 127 (the guards extend existing checks); harness R1-R20 →
  R1-R22; keypairs 15 → 17.
- Findings register 99 rows: open 10 → 7, closed 89 → 92; disposition per DR or cycle
  addendum 29 → 32, recorded 16, pending 54 → 51. Coverage register 24 rows: open 13 →
  10, closed 11 → 14.

## 24. Coverage SC2 closure evidence

Execution baseline `002ed1c`. Owner decisions L1–L5 and the plan-review adjustments
R1–R7 are in the design record (DR-0 addendum, coverage SC2). Line references are to
the files after the cycle. No key material was printed. Mutations ran on a scratch
copy: `git archive 002ed1c` with the full candidate diff applied and the new schema
copied, the unmutated copy first passing the whole battery, and the candidate restored
between cases.

| Finding | Closure criterion (clause) | Evidence | Mutation → failing check | Met |
|---|---|---|---|---|
| A-57 | Executed approval-chain vectors: capability, deadline, approver id, signature | Actions §3.4 states one verification order for approved and denied decisions (Verification of an `approval_decision`, l.1483). Harness R15 runs every approval decision through `Run._decide` (`runtime_harness.py` l.1275) and every review decision through `Review.receive` (l.1448), both on `verify_oversight_decision` (l.1127): signature through the executing agent's JWKS cache (`KeyDirectory` l.1043, `verify_signed` l.1065, with the alg/key coherence of Core §5.2 Step 5 through the validator's `_verify_signature`); a JWS access token signed under the trusted issuer's configured key (`issue_token` l.1093, `verify_token` l.1100, every Core §6.1 claim required through `arsia-jwt-claims.schema.json`); `arsiaprotocol.oversight.approve` matched exactly (`scope_satisfies`) and present in `capabilities`; binding incl. `approver_id` = `from`; deadline on the receipt instant, no skew; pending state. Signature, key and token are evaluated at the verification instant. Rejections are logged as `decision_rejected` (`Run.reject` l.1305) and never admitted; `Run.expire` (l.1312) verifies queued decisions first and applies Path 3 only while pending and once the deadline is reached; an accepted review decision is recorded at its processing instant. Capability: INV-133, INV-134, INV-140; deadline: ITV-695, INV-126, INV-152, ITV-705..707; approver identity: INV-135; signature: INV-127, INV-128, INV-139, INV-155 (alg/key mismatch); token: INV-129..132, INV-153, INV-154, INV-156, INV-157 (missing iat, jti); correlation: INV-136..138; multi-approval: ITV-696; review record instant: ITV-708; accepted reference: ITV-694. The synthetic `verify_decision` of R7 is removed. | (a)–(l), (n), (v)–(z), (ab)–(af) | yes |
| A-58 | Schema rule for `jwks_fetched_at`; executed revocation/cache vectors | Schema: `verified_kid` ↔ `jwks_fetched_at` `dependentRequired`, the State §7.1 exception row replaced by two "present" rows (the runtime obligation stays in Core §5.2), parity guard extended to presence rows (`check_consistency.py` l.95, l.144, l.214). R15 checks the evidence on every record of every execution vector: the sender's kid and a fetch not later than the processing on records of received, verified messages; none on records of messages the executor emitted; the fetch instant from the cache (ITV-694: 09:30, not the 10:10 verification). Key-revocation payload schema (`arsia-key-revocation.schema.json`): ITV-699, INV-145..147. R13 `revocation` scenarios (`revocation_case` l.1938, `process_key_revocation` l.1918, `verify_signed_jwks` l.1899) with real signed messages: authenticated invalidation (ITV-700..702), unauthenticated events cause no invalidation (INV-148..151), cache ceiling and queued messages (ITV-703, ITV-704). | (m), (o)–(u), (aa) | yes |

**Vectors (47).**
- Execution (R15; base request at 10:00, deadline 11:00:00.000, GDPR-STANDARD skew
  300 s): ITV-694 (approver's JWKS cached at 09:30), ITV-695 (received at
  10:59:59.999), ITV-696 (required 2; X rejected for the token audience, then X and Y
  admitted), ITV-705 (received 10:59:59, queued; the timer at 11:00 verifies it first),
  ITV-706 (denial, then the deadline: no expiry); INV-126 (received exactly at
  11:00:00.000), INV-127/128 (approved/denied, reason changed after signing), INV-129
  (token `aud`), INV-130 (`sub`), INV-131 (untrusted issuer), INV-132 (token expired
  900 s before), INV-133 (scope `arsiaprotocol.*` only), INV-134 (`capabilities` empty,
  re-signed), INV-135 (`approver_id` of another agent, re-signed), INV-136 (unknown
  `correlation_id`, kept as received), INV-137 (`root_request_id`), INV-138 (approval
  after an admitted denial), INV-139 (invalid signature and wrong correlation →
  `unauthorized`), INV-140 (scope without approve and `approver_id` mismatch →
  `forbidden`), INV-152 (late and invalid signature → `unauthorized`), INV-153 (token
  claim changed after signing), INV-154 (received 10:09:59, key removed, verified
  10:10:01 past the 60 s max-age of the 10:09 fetch), INV-155 (alg ES256 declared over
  a valid Ed25519 signature), INV-156 and INV-157 (token validly signed without `iat`,
  without `jti`), ITV-707 (timer at 10:00:01, before the deadline: the queued decision
  is processed, no expiry), ITV-708 (review decision received 10:00:02, verified and
  recorded 10:01:02).
- Schema-ref: ITV-697, INV-141, INV-142 (`verified_kid` / `jwks_fetched_at`); ITV-698,
  INV-143, INV-144 (`decision_rejected`, `rejection_code`); ITV-699, INV-145..147
  (key-revocation payload).
- Revocation (R13; `agent:acme.echo-client`, revoked `#key1`, successor `#other-key`,
  both already in the catalog; 14:00 fetch, 14:05 removal, 14:10 event, 14:20 lookup):
  ITV-700 (successor already cached: no refresh at the event; the next `#key1` lookup
  refreshes and `#other-key` is then served from the 14:20 fetch), ITV-701 (successor
  published at the rotation: refresh at the event), ITV-702 (`effective_at` one day
  ahead: invalidation at once), INV-148 (signed by `#key1` itself), INV-149
  (`revoked_kid` of `agent:acme.billing`), INV-150 (`effective_at` changed after
  signing; signature negative, construction guarded), INV-151 (signing key never
  published: the refresh it causes is an ordinary JWKS update), ITV-703 (accepted at
  14:30 with `jwks_fetched_at` 14:00, rejected past the ceiling), ITV-704 (queued
  message verified after the 60 s max-age).

**Existing vectors changed.** ITV-694 (an SC2 vector) states `processed_at` in its
evidence after the review below. Expectations: ITV-656 and ITV-662 (`event_types` gain
`decision_rejected`); ITV-657..660 (`event_types` added; "not recorded" → "not
recorded as a decision; logged as decision_rejected"). Descriptions only, no result
change: ITV-314..316, ITV-319..321 and ITV-664 (stale "§3.4 Step N" references after
the renumbering), ITV-317 (the withdrawn "±300s clock skew tolerance" on the
deadline). Spec echo also aligned: the Assets §5.2 `pending_approval` example
("latest time approval will be accepted").

**Mutations.** 33/33 detected:

```
(a) approval verification skips the signature step: DETECTED (R15 INV-127, INV-128)
(b) a rejected denial ends the pending flow: DETECTED (R15 INV-128)
(c1) token aud not checked: DETECTED (R15 INV-129)
(c2) token sub not checked: DETECTED (R15 INV-130)
(d) approve capability satisfied by a wildcard: DETECTED (R15 INV-133)
(e) capability checked in the token only, not in capabilities: DETECTED (R15 INV-134)
(f) approver_id = from not checked: DETECTED (R15 INV-135)
(g) deadline with > instead of >=: DETECTED (R15 INV-126)
(h) deadline extended by 300 s of skew: DETECTED (R15 INV-126)
(i) a rejected attempt consumes its approver: DETECTED (R15 ITV-696)
(j) binding (step 4) checked before signature, token and authority: DETECTED (R15 INV-139, INV-140)
(k) decision_rejected not emitted: DETECTED (R15 ITV-662, INV-127)
(l) verified_kid recorded although the signature failed: DETECTED (R15 INV-127)
(m) jwks_fetched_at = the verification instant: DETECTED (R15 ITV-694; R13 ITV-703)
(n) a valid late review decision rejected: DETECTED (R15 C-09)
(o) authenticated revocation event not acted on: DETECTED (R13 ITV-700)
(p) event signed by the revoked key accepted: DETECTED (R13 INV-148)
(q) revoked_kid of another agent accepted: DETECTED (R13 INV-149)
(r) invalidation before authentication: DETECTED (R13 INV-148, INV-149, INV-150)
(s) a future effective_at delays the invalidation: DETECTED (R13 ITV-702)
(t) schema: verified_kid no longer requires jwks_fetched_at: DETECTED (validator INV-141)
(u) schema: decision_rejected without required rejection_code: DETECTED (validator INV-143)
(v) deadline checked before steps 1-4: DETECTED (R15 INV-152)
(w) Path 3 applied to a resolved flow: DETECTED (R15 ITV-706)
(x) the deadline timer expires without verifying queued decisions: DETECTED (R15 ITV-705)
(y) token signature not verified (claims only): DETECTED (R15 INV-153)
(z) steps 1-3 evaluated at the receipt instant: DETECTED (R15 INV-154)
(aa) State §7.1 loses the `verified_kid` present row: DETECTED (A-59 parity guard)
(ab) approval signature verified without alg/key coherence: DETECTED (R15 INV-155)
(ac) token claims not checked against Core §6.1; a missing iat defaulted: DETECTED (R15 INV-156, INV-157)
(ad) the token generator omits jti: DETECTED (R15 ITV-694)
(ae) Path 3 before the deadline is reached: DETECTED (R15 ITV-707)
(af) the accepted review decision recorded at its receipt instant: DETECTED (R15 ITV-708)
```

**Owner review correction.** The owner's double check reproduced four harness defects
that the battery and the first 28 mutations did not cover: (1) `verify_signed` delegated
to `signature_ok`, which verifies Ed25519 without checking `security.alg`, so an
approval declaring ES256 with a valid Ed25519 signature was admitted; (2)
`verify_token` defaulted a missing `iat`, did not require `jti`, and `reviewer_token`
issued no `jti`; (3) `Run.expire` resolved a pending flow by Path 3 before the deadline;
(4) `Review.receive` authenticated at the verification instant but recorded the
accepted decision at the receipt instant, so `processed_at` could precede
`jwks_fetched_at`. Fixed respectively by verifying through the validator's
`_verify_signature` (Core §5.2 Step 5), by checking the claims against
`arsia-jwt-claims.schema.json` with no defaults and issuing complete tokens, by a
deadline guard in `Run.expire` that still processes the queue, and by recording at the
verification instant. Regressions INV-155..157, ITV-707, ITV-708; mutations (ab)–(af);
(w) and (x) retargeted to the guarded `expire`. No decision changed.

Mutation (r) invalidates the named key before any check. It is detected where the event
would otherwise leave the cache untouched (INV-148..150); in INV-151 the refresh caused
by the unknown signing key removes `#key1` legitimately, so that vector does not
discriminate (r), as the plan review anticipated.

**Inventory.** The existing vectors changed are exactly those listed above; no other
vector changed result. The signature negatives are INV-18, INV-19, INV-37, INV-38,
INV-39, INV-111, INV-112, INV-124 and INV-150; the INV-150 construction guard proves the
signature verifies over the pre-tamper bytes (`effective_at` 13:55) with `#other-key`
and not over the presented event. No key was added to the catalog.

**Counts before → after.**
- Vectors 846 → 893 (validator 475 / 208 / 163 → 483 / 215 / 195); crypto-checked 145 →
  154 (134 → 142 verified, 8 → 9 negatives, 3 canonical only); 0 failures in all four
  modes.
- Skip classification 163 → 195 rows (crypto-behaviour 11 → 15, executor-oversight
  35 → 63), all new rows `executed: R15` or `executed: R13`.
- Schemas 33 → 34 (`arsia-key-revocation.schema.json`); consistency checks 127 → 129
  (its meta-schema and `$id` checks).
- RTM 2028 / 1225 → 2045 / 1241: ACT-§3.4-30..36, CORE-§4.2.1-05, CORE-§5.2-14..16,
  IDENT-§2.5-06..09, STATE-§7.1-28..29; ACT-§3.4-27 SHOULD → MUST; rows aligned to the
  new text; stale rows corrected where A-58 traces through them (CORE-§5.2-11 "every
  24 hours" → 3600 s, IDENT-§2.5-03 refetch-on-failure → the revocation event,
  STATE-§7.1-04 22 → 23 event types); Draft-02 Delta rows added; coverage summaries of
  the four touched RTMs recomputed from their tables (the Actions summary was stale at
  the baseline: 329 stated, 350 rows).
- Harness R1-R22, 492 → 676 assertions.
- Findings register 99 rows: open 7 → 5, closed 92 → 94; disposition per DR or cycle
  addendum 32 → 34, recorded 16, pending 51 → 49. Coverage register 24 rows: open 10 →
  6, closed 14 → 18.
