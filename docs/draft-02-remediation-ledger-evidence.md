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
