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
