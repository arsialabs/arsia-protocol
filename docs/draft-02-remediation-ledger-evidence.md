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

## 25. Coverage SC3 closure evidence

Execution baseline `0af14ea`. Owner decisions P1–P4 and the plan-review adjustments
R1–R4 are in the design record (DR-0 addendum, coverage SC3). Line references are to
the files after the cycle. No key material was printed. Mutations ran on a scratch
copy: `git archive 0af14ea` with the full candidate diff applied, the unmutated copy
first passing the whole battery, and the candidate restored between cases.

| Finding | Closure criterion (clause) | Evidence | Mutation → failing check | Met |
|---|---|---|---|---|
| A-61 | Executed duplicate-member and non-I-JSON vectors, strict parser | Core §5.2 steps 3–4 state their content and a new paragraph fixes `invalid_request` (P2); [RFC 7493] added to the normative references. `strict_json` (`validate_vectors.py` l.98) parses with `_Pairs` (l.43), a typed list that keeps every occurrence, then runs `_check_ijson` (l.61, step 3) and `_check_unique` (l.77, step 4) in that order, and only then builds the document; Python's integer digit limit is lifted for the parse (steps 2–4 add no numeric limit) and restored after it; `strict_load` (l.121) is used for every artifact in validate_vectors, check_consistency, runtime_harness, extract_examples and regen_v2. The `raw` format (meta-schema, exclusive both ways) runs 18 vectors in the validator. Guard `strict_parsing_problems` (`check_consistency.py` l.1224): a corpus with a duplicate stops validate_vectors.py at step 4 before any vector; `{"x":"\ud800","a":1,"a":2}` is rejected at step 3; every raw vector at its stated step; mixed-format and incomplete raw vectors fail the meta-schema; `{}`, `[]`, `[["a", 1]]` preserved; a 5000-digit integer kept as an integer, with the global limit unchanged afterwards; no `json.load` on files | (a)–(k), (n2), (n3), (n5), (t) | yes |
| A-62 | Harness rule + ITV-545/546/547 with profile tolerances; clean "90 s under 120 s" case | R16 (`timing` scenario) executes the six earlier vectors and the clean case: EU-AI-ACT-HIGH-RISK message with complete compliance (`legal_basis`, retention P6M at the floor), signed with the catalog key, `token_hash` per the `synthetic-token:<ID>` convention: ITV-709 (−90 s) and ITV-710 (+90 s) accepted with tolerance 120 (`profile:EU-AI-ACT-HIGH-RISK`), INV-171 (−150 s) rejected only for `ts_outside_tolerance` under the MAY posture of ITV-545, and accepted without it | (q) | yes |
| A-63 | Extraction rule validating every non-envelope normative example | `extract_examples.py` requires an annotation on every full block and validates it (`residual` l.133, `check_example` l.167, `scan` l.199), with formats asserted (`format_checker`) and `@…/*` selectors accepted only over a JSON array (`select` l.118): 82 blocks = 77 full (53 complete, 10 template, 12 partial, 2 no-schema) + 5 fragments; 75 validated against a schema (9 before). Template exemptions only at the declared placeholder pointer and for the keywords a placeholder prevents; partial only for the declared omitted member; oneOf/anyOf re-evaluated on all branches, two valid oneOf branches still failing; no heuristic decides an exemption. Format assertion required two more declared placeholders: Identity §3.3 DPoP claims `/htu`, Routing §2.3.3 relay error `/dpop_nonce_htu`. Self-test `example_annotation_problems` (`check_consistency.py` l.1160). Examples corrected: Actions §3.3 and Assets §5.2 approval_decision (null `reason`/`conditions` omitted), Assets §5.2 `pending_approval` (`obligation_resolution` placeholder written as a value). R15 checks every decision it builds against the message schema (`fixture_check`, `runtime_harness.py` l.1568), outside the normative order | (l)–(n), (n4), (o), (p), (p2), (r), (s) | yes |

**Raw vectors (19).** Bytes as written (escapes are the ASCII bytes of the escape; the
hex segment is the decisive part of `raw_hex`). Minimal envelopes
`{"v":"2.0","id":…,"intent":"request","payload":{"type":"com.acme.test/run","args":{…}}}`
unless stated.

| ID | Bytes | Expected |
|---|---|---|
| CTV-11 | the CTV-01 envelope in RFC 8785 form | accept |
| CTV-12 | value `"\ud83d\ude00"` (escaped valid pair), hex `225c75643833645c756465303022` | accept |
| CTV-13 | value U+1F600 literal, hex `22f09f988022` | accept |
| CTV-14 | names `"a"`, `"A"`, and `"a"` again in a nested object | accept |
| CTV-15 | `"count":1152921504606846976` (2^60) | accept |
| CTV-16 | `"count":` followed by 5000 digits `7` (5131 bytes), beyond the 4300-digit default of Python's integer conversion | accept |
| INV-158 | `"id"` twice at the top | reject, step 4 |
| INV-159 | `"intent"` and `"\u0069ntent"` (hex `5c7530303639`) | reject, step 4 |
| INV-160 | `"k"` twice in `payload.args` | reject, step 4 |
| INV-161 | byte `ff` in a string | reject, step 2 |
| INV-162 | overlong `c0 af` in a string | reject, step 2 |
| INV-163 | CESU surrogate `ed a0 80` in a string | reject, step 2 |
| INV-164 | `"\ud800"` alone in `payload.args.note` (nested), hex `5c7564383030` | reject, step 3 |
| INV-165 | `"\udc00"` alone as a top-level member name | reject, step 3 |
| INV-166 | value `"\uffff"`, hex `225c756666666622` | reject, step 3 |
| INV-167 | literal U+FDD0 (`ef b7 90`) | reject, step 3 |
| INV-168 | value `"\ud83f\udffe"` (U+1FFFE), hex `225c75643833665c756466666522` | reject, step 3 |
| INV-169 | `NaN` as a value | reject, step 2 |
| INV-170 | `Infinity` as a value | reject, step 2 |

**Example inventory (82 blocks, by file:line after the cycle).**

```
Actions:336    partial   arsia-message.schema.json
Actions:344    fragment
Actions:928    complete  arsia-action-descriptor.schema.json
Actions:1062   fragment
Actions:1164   partial   arsia-message.schema.json
Actions:1274   fragment
Actions:1415   template  arsia-message.schema.json#/$defs/approval-decision-result @/result
Actions:1596   partial   arsia-message.schema.json
Actions:1645   partial   arsia-message.schema.json
Actions:2024   template  arsia-message.schema.json#/$defs/review-pending-data @/data
Actions:2073   template  arsia-message.schema.json#/$defs/review-decision-data @/data
Actions:2467   partial   arsia-message.schema.json
Actions:2486   complete  arsia-message.schema.json#/$defs/long-running-status
Actions:2501   complete  arsia-message.schema.json#/$defs/long-running-status
Actions:2527   complete  arsia-message.schema.json#/$defs/long-running-status
Actions:2733   complete  arsia-explanation.schema.json
Assets:723     complete  arsia-message.schema.json
Assets:781     complete  arsia-message.schema.json
Assets:1000    complete  arsia-message.schema.json
Assets:1042    complete  arsia-message.schema.json
Assets:1162    partial   arsia-message.schema.json
Assets:1205    complete  arsia-message.schema.json
Assets:1354    complete  arsia-escrow-conditions.schema.json
Assets:1835    partial   arsia-message.schema.json
Assets:1869    partial   arsia-message.schema.json
Assets:2266    complete  arsia-message.schema.json
Assets:2375    complete  arsia-jwt-claims.schema.json
Assets:2556    complete  arsia-escrow-conditions.schema.json
Core:1352      no-schema an invalid_request details object required by Core §4.3.8 Rule 4; arsia-message.schema.json defines no $def for it
Core:2402      complete  arsia-message.schema.json#/$defs/error-details-forbidden
Core:2574      complete  arsia-discovery-response.schema.json
Core:2650      complete  arsia-capability-descriptor.schema.json @/*
Core:2759      complete  arsia-jwk-entry.schema.json @/keys/*
Core:2822      complete  arsia-message.schema.json#/$defs/error-details-not-implemented
Core:3005      complete  arsia-websocket-frame.schema.json
Core:3020      complete  arsia-websocket-frame.schema.json
Core:3030      complete  arsia-websocket-frame.schema.json
Core:3049      complete  arsia-websocket-frame.schema.json
Core:3058      complete  arsia-websocket-frame.schema.json
Core:3266      complete  arsia-broker-entry.schema.json @/*
Core:3289      complete  arsia-message.schema.json#/$defs/error-details-service-unavailable-residency
Core:3568      complete  arsia-message.schema.json#/$defs/error-details-forbidden
Core:3577      complete  arsia-message.schema.json#/$defs/error-details-not-implemented
Core:3587      partial   arsia-message.schema.json#/$defs/error-details-not-implemented
Core:3595      complete  arsia-message.schema.json#/$defs/error-details-rate-limited
Core:3606      complete  arsia-message.schema.json#/$defs/error-details-payload-too-large
Core:3616      complete  arsia-message.schema.json#/$defs/error-details-service-unavailable-residency
Core:4287      complete  arsia-message.schema.json
Core:4340      complete  arsia-message.schema.json
Core:4447      complete  arsia-message.schema.json
Identity:369   complete  arsia-jwk-entry.schema.json @/keys/*
Identity:425   complete  arsia-key-revocation.schema.json @/data
Identity:557   complete  arsia-dpop-proof.schema.json#/$defs/dpop-header
Identity:567   template  arsia-dpop-proof.schema.json
Identity:1131  fragment
Identity:1449  complete  arsia-onboarding-decision.schema.json#/$defs/conformance-check
Identity:1663  complete  arsia-onboarding-decision.schema.json
Identity:1865  complete  arsia-capability-policy.schema.json
Identity:1914  complete  arsia-capability-policy.schema.json
Routing:416    template  arsia-message.schema.json
Routing:855    complete  arsia-websocket-frame.schema.json
Routing:865    complete  arsia-websocket-frame.schema.json
Routing:882    template  arsia-websocket-frame.schema.json
Routing:897    complete  arsia-websocket-frame.schema.json
Routing:937    complete  arsia-websocket-frame.schema.json
Routing:946    complete  arsia-websocket-frame.schema.json
Routing:958    complete  arsia-websocket-frame.schema.json
Routing:1112   partial   arsia-message.schema.json
Routing:1141   template  arsia-message.schema.json
Routing:1181   template  arsia-message.schema.json#/$defs/error-details-relay-failed
Routing:1217   template  arsia-message.schema.json#/$defs/error-details-relay-failed
Routing:1830   partial   arsia-discovery-response.schema.json
Routing:2025   complete  arsia-broker-entry.schema.json @/*
Routing:2120   template  arsia-message.schema.json#/$defs/error-details-service-unavailable-residency
Routing:2310   partial   arsia-audit-record.schema.json
State:1999     complete  arsia-message.schema.json#/$defs/error-details-service-unavailable-residency
State:2126     no-schema an invalid_request details object required by State §5.2 (missing legal basis); arsia-message.schema.json defines no $def for it
State:3686     fragment
State:3792     complete  arsia-message.schema.json#/$defs/error-details-forbidden
State:3857     complete  arsia-message.schema.json#/$defs/error-details-conflict-version
State:3873     complete  arsia-message.schema.json#/$defs/error-details-conflict-absent
State:3889     complete  arsia-message.schema.json#/$defs/error-details-retention-override
```

The two `no-schema` blocks (Core §4.3.8 Rule 4 retention details; State §5.2 missing
legal basis details) are `invalid_request` details objects that
`arsia-message.schema.json` does not define; they are listed in the notes.

**Mutations.** 26/26 detected:

```
(a) object_pairs_hook builds dict again (last duplicate wins): DETECTED (validator INV-158..160; A-61 guard)
(b) duplicate names compared on the raw text, before escape processing: DETECTED (validator INV-159)
(c) Unicode scan only at the top level: DETECTED (validator INV-164, nested surrogate)
(d) UTF-8 decoded with errors='replace': DETECTED (validator INV-161..163)
(e) surrogates not checked: DETECTED (validator INV-164, INV-165)
(f) only BMP noncharacters: DETECTED (validator INV-168)
(g) only U+FFFE/U+FFFF (FDD0-FDEF missed): DETECTED (validator INV-167)
(h) parse_constant accepts NaN/Infinity: DETECTED (validator INV-169, INV-170)
(i) any escaped surrogate rejected in the raw text, valid pairs included: DETECTED (validator CTV-12; CTV-13, literal, still passes)
(j) the raw parser rejects everything: DETECTED (validator CTV-11..15)
(k) the vectors are loaded with json.load again: DETECTED (A-61 guard: corpus duplicate no longer stops the tool; json.load on a file)
(l) template exempts any error of the object: DETECTED (A-63 self-test: template error outside the pointer accepted)
(l2) combinator decided by best_match: DETECTED (A-63 self-test: the composite control, whose only branch error is the exempt placeholder, rejected)
(m) partial exempts any missing required member: DETECTED (A-63 self-test: nested required accepted)
(n) a full block without annotation is tolerated: DETECTED (A-63 self-test: unannotated block accepted)
(n2) duplicates checked before the I-JSON scan: DETECTED (A-61 guard, step order)
(n3) the existing meta-schema branches no longer exclude the raw fields: DETECTED (A-61 guard, mixed format)
(n4) a oneOf with an empty error context taken as passing: DETECTED (A-63 self-test, two valid branches)
(n5) an array of pairs taken for an object when the tree is built: DETECTED (A-61 guard, [["a", 1]])
(o) the Actions §3.3 example has "reason": null again: DETECTED (extractor)
(p) the harness emits null optional members again: DETECTED (R15 fixture check)
(p2) INV-134 back to capabilities []: DETECTED (R15 INV-134 fixture check)
(q) R16 uses the 300 s default for a profile that defines clock_skew_seconds: DETECTED (R16 INV-171)
(r) the array selector accepts an object or a string: DETECTED (A-63 self-test: {"keys": {}} and {"keys": ""} accepted)
(s) the extractor validates without a format checker: DETECTED (A-63 self-test: Core discovery example with inbox 'not a URI' accepted)
(t) the parser keeps Python's integer digit limit: DETECTED (validator CTV-16)
```

The first runs of (i) and (n5) were too coarse: the regex of (i) also matched the
corpus's own descriptions and stopped the tool before CTV-12 was reported, and the
first (n5) collapsed empty objects and broke every schema load. Both were narrowed to
the defect they name (an escape not preceded by a backslash; an array of pairs read as
an object) and are detected by the intended check. With the installed jsonschema,
best_match picks the shortest-path branch error (`/` is not an array), not `/x/id`: (l2)
is therefore caught by the composite control (a block whose only branch error is the
exempt placeholder is rejected), while the composite defect case stays rejected under
that mutant by chance. The self-test keeps both cases, so a best_match that picked
`/x/id` would be caught by the defect case.

**Existing vectors changed.** INV-134 only: `capabilities` `[]` → `["test.unit"]`
(the empty array failed the schema's `minItems`, so a conforming implementation would
have rejected it at pipeline step 11 with `invalid_request` before the authority check),
expectation `forbidden` kept, description updated. No other vector changed result.

**Published-count correction.** The format table of `test-vectors/README.md` was stale
at the baseline (323 message-only / 488 schema-ref stated; 341 / 548 in the corpus); it
now states the corpus counts.

**Owner review correction.** The owner's double check reproduced three verifier gaps
that the battery and the first 23 mutations did not cover: (1) `select` enumerated the
target of `@…/*` without checking its type, so `{"keys": {}}` or `{"keys": ""}` was
counted as complete while validating nothing; (2) the extractor's validator had no
format checker, so a discovery example with `"inbox": "not a URI"` passed; (3) the
parser inherited Python's 4300-digit integer conversion limit, rejecting a valid JSON
integer of 5000 digits at step 2, contrary to P2. Fixed respectively by requiring a JSON
array for `@…/*`, by asserting formats (with `/htu` and `/dpop_nonce_htu` declared as
the placeholders they are), and by lifting the digit limit for the parse only.
Regressions: self-test cases (object and string under `@/keys/*`, the discovery example
with a non-URI `inbox` next to its unmodified control, a 5000-digit integer with the
limit restored), raw vector CTV-16; mutations (r), (s), (t). No decision changed.
Format assertion needs the format checkers' own packages: without them `jsonschema` skips
`uri`, `date-time` and the other formats silently. `scripts/requirements.txt` therefore
declares `jsonschema[format-nongpl]>=4.18.0`, which is what CI installs. Checked in two
fresh virtual environments: with the declared requirements, the whole battery passes;
with plain `jsonschema`, `check_consistency.py` fails on the extractor self-test
(discovery example with a non-URI `inbox` accepted), so a missing format dependency is
reported, never passed over.

**Counts before → after.**
- Vectors 893 → 915 (validator 483 / 215 / 195 → 485 / 215 / 196, and 19 raw: 6 accepted,
  13 rejected); crypto-checked 154 → 157 (142 → 145 verified, 9 negatives, 3 canonical
  only); 0 failures in all four modes.
- Skip classification 195 → 196 rows (temporal 13 → 14; INV-171 `executed: R16`).
- Spec examples: 82 blocks = 77 full (53 complete, 10 template, 12 partial, 2
  no-schema) + 5 fragments; schema-validated 9 → 75.
- RTM 2045 / 1241 → 2049 / 1245 (CORE-§5.2-17..20; CORE-§8.3-09 and CORE-§4.1.3-03 gain
  the A-62 vectors); Core coverage summary recomputed; Draft-02 Delta row added.
- Consistency checks 129 → 131; harness R1-R22, 676 → 746 assertions.
- Findings register 99 rows: open 5 → 2, closed 94 → 97; disposition per DR or cycle
  addendum 34 → 37, recorded 16, pending 49 → 46. Coverage register 24 rows: open 6 →
  2, closed 18 → 22.

## 26. Coverage SC4 closure evidence

Execution baseline `94f96b6`. Owner decisions (A-53, A-64, Routing §7.4.1, base64url,
corpus header) and the plan-review adjustments R1–R5 are in the design record (DR-0
addendum, coverage SC4). Line references are to the files after the cycle. No key
material was printed. Mutations ran on a scratch copy: `git archive 94f96b6` with the full
candidate diff and the new file applied (tree identical to the working tree), the
unmutated copy first passing the whole battery, and the candidate restored between cases.

| Finding | Closure criterion (clause) | Evidence | Mutation → failing check | Met |
|---|---|---|---|---|
| A-53 | Executed runner for the named tests, or per-test disposition | `docs/draft-02-conformance-tests.md`: 89 tests (the 74 of the description is historical), each with the exercised preconditions, action and expected results, the executed evidence and the part not executed with its reason — integral 6, partial 43, equivalent 1, external 11, absent 28; CHECK-01..05 apart with their links. Guard `conformance_problems` (`check_consistency.py` l.1483) with self-test l.1535: the IDs equal the spec test headings, the class is in the closed vocabulary, every token resolves to an execution that passed in the same run (harness run once, l.1317; validator results), partial names its gap, equivalent its equivalence, external/absent claim no execution, the summary equals the rows. Assets §7: the runner executes only the parts identified as executed; "MUST pass all eight tests" unchanged | (i) a check that never ran → guard; (j) a test missing → guard; (j2) summary ≠ rows → guard | yes |
| A-64 | RTM statistics: each MUST row mapped to evidence or disposition | Column `Evidence` in the six RTMs (`docs/rtm/README.md`); 1445 MUST, MUST_NOT and REQUIRED rows carry tokens, every other row `—`. Validator results per vector (`vector_results` l.505, `crypto_results` l.380 of `validate_vectors.py`; "approved" = observed equal to expected, a negative's rejection included). Guard `rtm_evidence_problems` l.1425 (tokens `token_problems` l.1381) with self-test l.1456; header-driven parser `rtm_requirement_rows` l.1338 (every requirement line read, stated totals equal); drift linter reads every row (l.1974). Declared limit in the ledger and the RTM README | (k) Evidence emptied → guard; (l) `exec:R22:ITV-570` without the run → guard; (l2) a negative's crypto result inverted → guard; (m) 8-column regex restored → linter-rows check; (n) schema-ref outside the Schema column → guard; (p) `untested()` → guard; (q) `DR-5` in the Vector column → guard | yes |
| (coverage) ITV-570, Routing §7.4.1 step 1 | Step 1 executed (left from coverage SC1) | `receive_attestation` (`runtime_harness.py` l.3337): no `data_residency` → `not_required`; header absent → `service_unavailable`, step 1, residency details; otherwise `decode_attestation_header` (l.3312: non-empty, base64url alphabet, no `=`, length ≢ 1 mod 4, strict parse, attestation schema; every failure `unauthorized` at step 2, no exception) then `verify_attestation`. R22 (a) on ITV-570, ITV-711, ITV-712, INV-172..177; (e) derived headers of the earlier attestation vectors decode to exactly their data; (f) each header negative has a single defect (l.3362); (g) decoder pairs | (a) absent → unauthorized; (b) empty → absent; (c) padding stripped; (d) standard alphabet translated; (e) length ≡ 1 truncated; (f) duplicate last-wins; (g) no schema; (h) required without residency — each detected by R22 (a), and (c)–(e) also by R22 (g) | yes |

**Header vectors (data = the delivered envelope, the ITV-569 message unless stated).**

| ID | Header | Expected | Single-defect control (R22 (f)) |
|---|---|---|---|
| ITV-570 | absent (`null`) | `service_unavailable`, step 1, `{data_residency_violation: true, required_zone: "EU"}` | — |
| ITV-711 | base64url (no padding) of the compact attestation JSON S, 1144 characters (≡ 0 mod 4) | `accept` | — |
| ITV-712 | absent; envelope without `data_residency`, re-signed by its sender | `not_required` | — |
| INV-172 | `""` | `unauthorized`, step 2 | — |
| INV-173 | S followed by one space, base64url with its `==` padding (1148 characters) | `unauthorized`, step 2 | padding removed → accepted |
| INV-174 | the attestation with `policy_ref` `fixture->>>???`, re-signed by the broker (its base64url has `-` and `_`), encoded in the standard alphabet without padding (1120 characters) | `unauthorized`, step 2 | standard-alphabet decoding → accepted |
| INV-175 | the ITV-711 header plus `A` (1145 characters, ≡ 1 mod 4) | `unauthorized`, step 2 | last character dropped → accepted |
| INV-176 | S with `attestation_id` repeated with the same value (1219 characters) | `unauthorized`, step 2 (not `invalid_request`) | last occurrence wins → accepted |
| INV-177 | the attestation with an extra member `note`, re-signed by the broker over the object presented (1159 characters) | `unauthorized`, step 2 (schema) | without the schema check → accepted |

**Named tests: final classification.** Integral (6): ACTIONS-16, 17, 19; STATE-17, 18;
ROUTING-12 — each expected element of the test is compared by the cited execution. Equivalent (1): IDENTITY-23 — the three expected results are exercised by
separate R20 sequences rather than one exchange. Every other test is partial, external or
absent, with the part not executed named. Against the plan's provisional table: ACTIONS-05,
06, ASSETS-06, IDENTITY-03, 04 and ROUTING-11 are partial (an expected element is not
compared); ACTIONS-08, 09, CORE-COMPLIANCE-02, 05, STATE-01, 02, 06, 09, 11, 14, ASSETS-02,
07, 08, IDENTITY-05, 13 and 15 are absent (only structural, or no scenario).

**Owner review correction.** The owner's double check found the first version overstated
its evidence in three ways. (1) The guard accepted `exec:Rn:ID` whenever the ID appeared in
the name of a passing check; R2 tests fixed values and only names ITV-563..565, so
`exec:R2:ITV-563` passed with an empty corpus. A passing harness check now declares the
vectors it consumed (`check(..., executed=[…])`, printed `# executed <rule> <IDs>`; declared
by R10, R13, R14, R15, R16, R17, R18, R21 and R22 where they read a vector's content), and
`exec:` is verified against that record only; R2 and R3 evidence is cited as `check:`. The
`check:` abbreviation, which accepted any unique prefix (`R6 envelope`), is limited to
omitting a trailing parenthesised count; the STATE-§7.2-18 citation was completed. Both cases
are in the self-tests. (2) Twelve `integral` classifications claimed more than the cited
execution compares: CORE-COMPLIANCE-04 and STATE-13 (the R2 comparison, not the
`invalid_request` and its details), STATE-08 (a different snapshot instant, `updated_at` not
compared), IDENTITY-21 (the internal token's issuer, audience and signature not emitted) and
IDENTITY-22 (the `denied`/`conformance_failed` decision not exercised), found by the owner;
and, on re-reading every integral row against its vectors' expectations, ACTIONS-07 (the
error description), ACTIONS-13 (`policy.sha256`), ACTIONS-14 (`late: false`, the response's
resolution), ACTIONS-15 (the record's `late: true`), CORE-COMPLIANCE-09 (the identification
of the terminal result) and STATE-16 (the second snapshot's value). They are partial, with
the gap named; IDENTITY-23 is equivalent; ASSETS-03 no longer says the reference logic
returns a stored response (R6 selects the key only). (3) The header adapter caught only
`JsonRejected`: a 5000-digit integer reached a schema error message and raised `ValueError`,
deep nesting raised `RecursionError`. Both are now step 2 rejections without exception, with
R22 (h) regressions. The first report also stated 20 mutations for 19 labels; the campaign
below states each label. A second owner check reproduced two more overstatements, now
partial: ACTIONS-18 (ITV-663 compares the Path 3 error's code and `oversight_decision`
only; an altered description passed R15) and IDENTITY-18 (ITV-642 compares the source in
the scenario's internal resolution, not in the emitted `pending_approval`'s
`payload.obligation_resolution`; an altered source in the message passed R15). ACTIONS-13,
on the same fixture, states the same distinction.

**RTM Evidence.** Mandatory rows 1445: 338 with a behavioural execution (exec, check,
crypto or raw), 452 with structural execution only, 311 with a schema reference only (with
or without a disposition), 344 with a disposition only. Disposition tokens: `untested` 619
(structural-only 498, no-reference-model 96, integration 25), `out-of-repo` 244
(infrastructure 114, transport 56, operator 36, external-party 35,
implementation-internal 3). Review: the 140 sdk / sdk_enabled rows without evidence (141
before CORE-§4.3.6.4-03 was retired) were read one by one: 28 received `check:` or `exec:`
tokens where a passing check demonstrates the row or part of it (with a coded `untested`
for the rest of the row where the demonstration is partial), the others a coded `untested`
or `out-of-repo`; the 238 deployment, operational_policy and external rows
without evidence received `out-of-repo` with the code of their subject (transport by the
row's subject, otherwise by layer), and six of them also a demonstrating check (R20 (j),
R20 (k), R22 (d), the Identity §8.1 policy check); the 121 rows whose vectors run in a rule
received `exec:` after checking that the rule's domain is the row's; the 54 runtime-only
citations keep `struct` and `untested(structural-only)` unless a rule executes the vector;
no signature was added. Vector column normalised in 13 cells (CORE-§4.3.9-01,
IDENT-§7.3-19, STATE-§7.2-08, -10, -11, -15, -17, -18, -21, -22, STATE-§11.4-01; the
non-mandatory CORE-§12.1-02 and STATE-§7.2-09 moved to the section "References outside the
Vector column" of their RTM). Obsolete rows: retired CORE-§4.3.7-02, -03, CORE-§4.4.7-02,
-03, -04, IDENT-§2.5-04, -05, CORE-§4.3.6.4-03, -04; rewritten CORE-§4.4.7-01 (MUST: exactly
one content field), IDENT-§3.1-03 (MAY, the Core §5.2 bounds), CORE-§10.4-01 (the signed
envelope key is authoritative); added CORE-§4.3.7-04 (MUST NOT silently raise),
CORE-§4.4.7-05 (more than one content field, or none, rejected), ROUTE-§7.4-27..29
(§7.4.1 steps 1–2). CORE-§4.3.6.4-03, -04 and CORE-§10.4-01 were found during the review
and treated under the owner's bounded authorisation.

**Corpus header.** `version` `1.0.0` → `2.0.0`; `generated` `2026-04-10T00:00:00.000Z` →
`2026-11-05T23:27:56.000Z`, fixed when the revision was prepared and not recomputed by
any tool; `$schema` unchanged; `regen_v2.py` serialises the whole document and refuses
files it would not reproduce, so it keeps the header. Guard `corpus_header_problems`
l.1563; mutation (o) back to 1.0.1 → detected.

**Mutations.** 23 of 23 detected, each by the check its row names: (a)–(h) by R22 (a)
(and (c)–(e) also by R22 (g)); (i), (j), (j2) by the conformance guard; (k), (l), (l2), (n),
(p), (q) by the RTM Evidence guard; (m) by the drift-linter row count; (o) by the corpus header
guard; (r) the adapter catching only `JsonRejected` → R22 (h) both cases; (s) `exec:` accepted
from a check name → both guard self-tests; (t) any unique prefix accepted → the RTM guard
self-test; (u) R22 (a) no longer declaring the vectors it consumed → the RTM Evidence and
conformance guards.

**Counts before → after.**
- Vectors 915 → 923 (validator 485 / 215 / 196 → 487 / 215 / 202, raw 19); formats
  schema-ref 548 → 556; existing vectors changed: ITV-570 (rebuilt) and the corpus header
  only; crypto 157 (145 verified, 9 negatives, 3 canonical only), unchanged.
- Skip classification 196 → 202 rows (transport 5 → 11; ITV-570 none → `executed: R22`).
- RTM 2049 / 1245 → 2045 / 1247 MUST + MUST_NOT; 1445 MUST, MUST_NOT or REQUIRED, each with
  Evidence; coverage summaries recomputed; Routing Delta row added.
- Consistency checks 131 → 138; harness R1-R22, 746 → 779 assertions.
- Named tests classified 0 → 89.
- Findings register 99 rows: open 2 → 0, closed 97 → 99; disposition per DR or cycle
  addendum 37 → 39, recorded 16, pending 46 → 44. Coverage register 24 rows: open 2 → 0,
  closed 22 → 24.

## 27. Draft-01.1 port closure evidence

Execution baseline `acef2e4`. Owner decisions are in the design record (DR-0 addendum,
Draft-01.1 port). No key value was printed at any step; keys are named by kid only.
Mutations ran on a scratch copy: `git archive acef2e4` with the full candidate diff and
the untracked files applied (tree identical to the working tree), the unmutated copy first
passing the whole battery, and the candidate restored between cases.

| Finding | Closure criterion (clause) | Evidence | Mutation → failing check | Met |
|---|---|---|---|---|
| A-97 | Every signature outside a crypto block verifies with its kid's catalog key, or the vector declares and demonstrates its signature cause | **Inventory method:** every vector without `crypto` whose signed object (`message`, or the `data` of an arsia-message / arsia-relay-attestation schema-ref) carries `security.sig`; the key comes from the Draft-02 catalog, else the Draft-01.1 one; verification is mathematical under the Draft-02 profile.<br>**Groups:** P (positive expectation) 124; N (negative, other cause) 50; S (cause mentions signature, kid, alg or key) 8. INV-01, ITV-427 and INV-32 moved from S to N, so 177 were re-signed by `regen_v2.py --catalog` (`catalog_eligibility` l.147, `catalog_resign` l.165); only `security.sig` changed. Declared negatives: INV-11 and ITV-445 (`kid`/`binding`, mathematically valid with their kid's key), ITV-425 (`key`/`size`, signed with the published RSA-1024 key), ITV-426 (`signature`/`length`, 32 bytes), ITV-550 (`alg`/`not-allowed`).<br>**Guard:** `signature_problems` (`check_consistency.py` l.1699) first requires `security.sig` to be canonical base64url without padding (`strict_b64url` l.1636: URL-safe alphabet only, no `=`, no length ≡ 1 mod 4, unused bits zero). The validator's decoder skips characters outside the alphabet, so it is not used here. Self-tests: l.1755 (each other failure, encoding defects included, is rejected) and l.1825 (meta-schema). The meta-schema admits `signature_expectation` only without `crypto` and on a `message`, or on `data` of arsia-message / arsia-relay-attestation, whose `security.sig` is a string. | (a) a P vector back to its old signature; (b) INV-11 also corrupted; (c) ITV-425 re-keyed with RSA-2048 (also caught by the catalog guard); (d) ITV-426 with 64 bytes; (e) the field on a crypto vector; (l) any failure accepted as the declared cause → self-test; (m), (m2), (m3) `!!!!` appended to the signature of INV-11, ITV-445, ITV-426; (n) the lenient decoder restored in the guard → self-test; (o) the meta-schema condition reduced to the `crypto` exclusion → self-test; (o2) CTV-11 (raw) and (o3) ITV-358 (no `security.sig`) carrying the field → `--check-meta` (exit 1) and guard | yes |
| A-98 | Each point defect corrected with its intended expectation, and a regression guard | ITV-498: `ts` 09:55, `expires_at` 10:00, recipient 10:10. ITV-518: `ts` 10:05, `expires_at` 10:10, recipient 10:30. Both are `timing` scenarios rejected by R16 for `expired` only. ITV-550: `id` `…-4c9d-8e1f-…`. ITV-402: `capabilities` added, still no `security`. CTV-03: AssetTransferRequest args, re-signed through its crypto block. INV-21: schema-ref `arsia-state-operations.schema.json#/$defs/set-args` failing only on `pii_special_categories`, with `resolve_schema` (`validate_vectors.py` l.204) keeping the document as the resolution context; the results of the 923 vectors are identical before and after that change. ITV-449: skip reason. Guard `port_fixture_problems` l.1891: `expires_at` after `ts`; positive transfer-request args; ITV-426 a canonical encoding of exactly 32 bytes; `SINGLE_CAUSE` l.1882: INV-21 (`required` `pii_special_categories`), ITV-402 (`required` `security`) and ITV-550 (`enum` at `security/alg`) each fail with exactly that one error, validator, path and message. The general `--check-errors` comparator matches a keyword and accepts a second defect next to it | (h) ITV-498 back to `expires_at` < `ts`; (i) CTV-03 old args; (j) INV-21 message-only → guard; (j2) subschema extraction → `PointerToNowhere`, validator and consistency exit 1; (p) ITV-402 without `capabilities` again; (q) ITV-550 with its old id again → guard | yes |
| A-99 | Every kid that a signature outside a crypto block uses, and the kid of each of the 23 crypto blocks the port covered, is published; no existing entry overwritten | `keypairs.json` 17 → 53. 34 entries imported unchanged from `origin/main` 17dcf33 (32 Ed25519, 1 P-256, 1 RSA); 2 generated: `agent:contoso.crm#key1`, Ed25519 derived from the kid, and `agent:acme.legacy-system#rsa1024`, below the minimum and declared. The 5 conflicting kids (`agent:acme.data-agent#key1`, `agent:acme.data-processor#key1`, `agent:acme.health-processor#key1`, `agent:acme.oversight-panel#key1`, `agent:arsialabs.aiact.hr-screener#key1`) keep their Draft-02 key; their 8 failing vectors (ITV-309, 310, 313, 314, 512, 533, ITV-532, INV-66) were re-signed with it. `provenance` records the sets and digests. Guard `catalog_problems` l.1858. The 23 crypto blocks with a formerly unpublished kid are unchanged.<br>**INV-04, by disposition.** After the port it is the only vector whose signing kid is not in the catalog. Its crypto block keeps the malformed kid `echo-client#key1`, without the `agent:` prefix, matching the malformed `from` that is its structural defect (Core §3.3). The block carries its own key, which equals the catalog key of `agent:acme.echo-client#key1`, and `--check-crypto` verifies it. Publishing a key under a malformed identifier, or changing the vector, would serve only a wider wording of the criterion, so the vector is unchanged | (f) a conflicting kid overwritten; (g) an imported entry altered → digest | yes |

**Dependency search.** Before writing, every occurrence of each target's old signature and
old `envelope_hash` was located by vector and JSON path: 10,963 occurrences. 10,956 are the
target's placeholder repeated as another fixture's own `security.sig` (class 1, for
example ITV-12, ITV-13 and ITV-14). The other 7 match a `crypto.signature_base64url` of
another vector: the old signatures of INV-40 (= CTV-01, INV-37, INV-38), INV-68 and INV-69
(= ITV-629), INV-70 and INV-71 (= ITV-628). Those negatives were derived from the valid
vectors by copying the envelope with one structural change. They kept the original
signature, so it did not verify, and their stated causes (`root_request_id`,
`capabilities`, `correlation_id`, an extra member, a wrong intent) are structural. The
originals keep their own signature over their own envelope. Nothing has to stay coherent
and no crypto block changed, so the 7 are class 1 as well. No `envelope_hash` occurrence was
found. No global replacement was made.

**Re-signer contract.** `resigner_contract_problems` gains five cases for `--catalog`:
- (k) a crypto vector, (l) a declared negative (INV-11), (m) a vector without
  `security.sig` (ITV-358) and (n) a kid outside the catalog are each refused, with
  nothing written;
- (o) an edited envelope changes only its signature, which verifies with the catalog key.

**Inventory after the port.** 186 vectors changed: the 177 re-signed, the three signed
declared negatives (INV-11, ITV-445, ITV-425) and the point fixes. Fields other than
`security.sig` changed only in CTV-03, INV-11, INV-21, ITV-402, ITV-425, ITV-426, ITV-445,
ITV-449, ITV-498, ITV-518 and ITV-550. 186 undeclared signatures verify. The five declared
negatives fail for their cause. The only crypto block that changed is CTV-03's. The
validator's `--check-crypto` still checks 157 blocks.

**Mutations.** 23 of 23 detected: (a)–(j), (j2), (k), (k2), (l), (m), (m2), (m3), (n), (o),
(o2), (o3), (p) and (q), each by the check its table row names; (k) and (k2) are caught by
the re-signer contract guard. The 23 coverage SC4 mutations still all detect on the same
candidate. The unmutated copy passed first, and the tree was identical after each run.

**Owner double check.** The first review of the port found three gaps in the checks and
one closure statement that was too broad:
- the guard decoded with the lenient decoder, so INV-11, ITV-445 and ITV-426 with `!!!!`
  appended to the signature passed. The strict encoding check above now runs first;
- the meta-schema did not express the presence condition, so CTV-11 (raw) and ITV-358
  (no `security.sig`) with the field were accepted. The condition is now complete;
- removing `capabilities` from ITV-402 again, or restoring ITV-550's old id, passed the
  validator, `--check-errors` and the fixture guard. Both are now single-cause checks;
- A-99's criterion said every signing kid is published, while INV-04 keeps an unpublished
  malformed kid. The criterion is delimited, and INV-04's disposition is recorded.

No vector or key changed as a result of the review.

**Counts before → after.**
- Vectors 923 (485 / 215 / 204 runtime / 19 raw; ITV-498 and ITV-518 became runtime);
  formats message-only 344 → 343, schema-ref 556 → 557 (INV-21).
- Skip classification 202 → 204 rows (temporal 14 → 16, `executed: R16`); ITV-449's reason
  corrected.
- Keypairs 17 → 53. Consistency checks 138 → 142. Harness R1-R22, 779 → 783 assertions (R16
  executes ITV-498 and ITV-518).
- RTM: ROUTE-§4.1.9-01 and ROUTE-§8-02 gain `exec:R16`.
- Findings register 99 → 102 rows (A-97, A-98, A-99 registered and closed); open 0.
  Coverage register 24 → 25 rows, all closed.

## 28. Main reconciliation inventory

`git merge --no-commit --no-ff origin/main` on `de9db8d` (the port), committed after the
owner's review as `54c2726` (parents `de9db8d` and `17dcf33`). `origin/main` is
17dcf33, the PR #1 merge of `bbbd8df` onto the common base 2692450 (Draft-01): 18
commits, 21 files. Classes:
- **port**: equivalent by the port, `de9db8d`;
- **cycle**: equivalent by an earlier Draft-02 cycle, with the resolution cited;
- **merged**: incorporated in this merge;
- **n/a**: not applicable to Draft-02, with the reason;
- **repaired**: not resolved in Draft-02 before the merge; repaired here by owner decision
  (A-100, reconciliation addendum).

Corpus inventory method: each main commit's corpus diff, vector by vector and path by
path, set against the vector at `de9db8d`. The check covers format, expectation, crypto
block, the A-97 guard, validator and `--check-crypto` results, and the schema errors of
negatives. The cited cycle is the Draft-02 commit that last changed the vector before
the port (first-parent history).

**Corpus and keypairs**

| Main commit | Vectors | Class | Draft-02 resolution |
|---|---|---|---|
| 8d2e727 sign all valid vectors | ITV-12, 14, 15, 63, 64, 66, 73–86, 278, 282, 284, 285, 289–291, 293, 294, 300–311, 313–323, 325, 326, 328–330, 332–336, 338–341, 364–378, 380, 383–389, 393, 396, 399, 400, 403, 444, 478, 491, 494, 495, 497, 498, 500, 502–504, 510, 512–514, 516, 518, 533–535, 548, 549, 558–560 (119) | port | re-signed with catalog keys (A-97 group P). The 16 vectors whose `kid` main renamed keep their Draft-02 kid, which the port publishes (A-99) |
| 8d2e727, fe7763b (schema-valid requests) | ITV-536–541, 543, 544, 547, 553–555 | cycle | `bbb8ef3` (vector cycle): crypto blocks with real signatures (`--check-crypto` verified); schema-valid, with no message errors |
| 8d2e727, 119b914, 59c70ac keypairs | 57 main entries | port / repaired / n/a | 34 imported unchanged (A-99); `agent:acme.state-extension#key1` imported unchanged here for ITV-266 (A-100); 9 already in Draft-02 with the same key; 5 conflicting kids keep the Draft-02 key (port addendum); 8 used by no Draft-02 vector: `agent:acme.{compliance-checker,escrow-holder,escrow-service,identity-admin,notes,risk-engine,state-store,transfer-service}#key1` |
| 119b914 sign invalid vectors | INV-23, 24, ITV-13, 24–27, 68, 69, 87, 324, 327, 361, 382, 390–392, 398, 401, 427–429, 431–437, 446, 479–481, 526, 532 (35) | port | re-signed (A-97 group N); ITV-401's `correlation_id` came earlier in C3a (`aa5547d`) |
| 119b914 | INV-25 (`intent`) | cycle | `bbb8ef3`: `intent` `approval_decision`, crypto block verified |
| 9c1316a | ITV-498, ITV-518, CTV-03 | port | A-98 |
| 59c70ac second defects | ITV-402, ITV-550; ITV-449 (skip reason) | port | A-98, with single-cause checks |
| 59c70ac missing `security` | INV-20, INV-22, ITV-409–414, 416, 418, 422, 424, 477 | cycle | `bbb8ef3`: `security` with a verified crypto block |
| 59c70ac missing `security` | ITV-201, ITV-266, ITV-423 | repaired | `security` added as main has it (`alg`, `kid`), signed by `regen_v2.py --catalog` under the Draft-02 profile. Each now fails only for its rule: ITV-201 `legal_basis` (two schema rules), ITV-266 `enum` at `payload/type`, ITV-423 `oneOf` at `payload` |
| 59c70ac removal | ITV-482 | repaired | main removed it over the Draft-01 conflict between two `capabilities` values. Draft-02 has no such conflict (onboarding decisions no longer reuse `approval_decision`) and keeps the vector. It gains `capabilities: ["arsiaprotocol.onboarding.evaluate"]` (the Identity §7.6 table); its missing `security` stays the only error |
| 59c70ac removal | ITV-545 | n/a | Draft-02 keeps it with `posture` (MAY, Core §8.3; vector cycle) |
| 59c70ac | ITV-546 | cycle | `260ac73`, `bbb8ef3`: rebuilt as a Core §4.3.8 Rule 2/4 negative whose `ts` is within the tolerance |
| 59c70ac | ITV-448, ITV-450 (`expected` → invalid) | n/a | Draft-02 convention for runtime-only schema-ref vectors: `expected` is the structural result and the runtime outcome is `expected_error` (as INV-115..120 and INV-129..132) |
| 2b51be1 | INV-21 | port | resolved differently: a schema-ref against `set-args` with its cause executed, instead of a signed runtime-only vector |
| d769c1b | corpus `version` 1.0.1 | n/a | corpus `2.0.0` (SC4) |

**Specifications, RTMs and documentation**

| Main change | Class | Resolution |
|---|---|---|
| Version labels Draft-01.1 in the six specs (09ecf10) | n/a | Draft-02 labels |
| Core TOC link to §10.4 (09ecf10) | merged | `#104-header-vs-envelope-precedence-http-transport` |
| Core §4.4.1 errata note: label, "earlier pattern", example locations Actions §2.1 / §4.2 | merged | the Draft-02 locations are the same; the closing sentence becomes "did not change the wire protocol version, then `1.0`" (Draft-02 is wire 2.0) |
| RTM coverage-gap tables recomputed (7dec87d) | cycle | regenerated in `4686d4a`; recomputed in this merge from the requirement rows, all six RTMs match (summary and per-section) |
| RTM row count 1,903 (227c56e, 67246cc) | cycle | 2,045 (`rtm_counts.py`); `SECURITY.md` still said 2,086, corrected here |
| Assets gap list gains ASSETS-§4.2.3-03/04 | cycle | both are rows of the Draft-02 table (`untested(no-reference-model)`); the separate list was removed in `4686d4a` |
| CORE-§8.3-09 without ITV-545; IDENT-§7.6-03 without ITV-482 | n/a | Draft-02 keeps both vectors |
| Test-vector counts in README, SECURITY, getting-started, FAQ, test-vector README | cycle / merged | Draft-02 counts (923; 485 / 215 / 204 / 19); `SECURITY.md` counts updated here |
| Keypair count 57 | n/a | 54 (Draft-02 catalog: the 53 entries at the end of the port, plus the key imported here for ITV-266) |
| README oversight and data-residency links | merged | Actions §3 and Routing §5 anchors, verified against the Draft-02 headings |
| `SECURITY.md` "six dimensions", RTM and test-vector links | merged | six bullets counted; links resolve from the root |
| getting-started security-model link, cookbook 22 recipes | merged | `../SECURITY.md`; 22 recipes in the SDK cookbook on its `main` (`01d2f31`) |
| getting-started validation statement ("runtime-only skipped") | n/a | Draft-02 validates runtime-only vectors structurally (A-42) |
| getting-started signature claim limited to signed cases | merged | adapted: signatures verify unless the vector declares a signature negative |
| Test-vector README signature statement | merged | adapted to Draft-02: signatures outside a crypto block verify with the catalog key unless declared |
| Test-vector README skip-category table | n/a | per-vector classification in `docs/draft-02-skip-classification.md` |
| Test-vector README snippets (three algorithms; run from `test-vectors/`) | merged | adapted to `expect_signature` and to crypto blocks in `data`. The Draft-02 snippets read `message` only and failed on the 16 such blocks. Executed: 145 signatures verified, 157 canonical forms equal |
| VERSIONING errata paragraph | merged | artefact corrections and the retrocompatibility scope added; Draft-01.1 recorded as the last erratum, superseded by Draft-02 |
| VERSIONING `version` field "(profiles, test vectors)" | merged | no schema carries a top-level `version`; the profile catalog and the corpus do |
| profiles README "Draft-01.1" (merged silently) | n/a | Draft-02 label restored |
| README badge Draft-01.1 | n/a | Draft-02 |
| CHANGELOG | merged | the Draft-01.1 entry kept as history, below `## [Draft-02] — Unreleased`; Draft-01 entry corrections (oversight attribution, counts) kept; the Draft-02 entry's figures updated and the reconciliation noted |

**Repairs (A-100).** `merge_fix.py` (scratch) imports the key and edits the four vectors;
`regen_v2.py --catalog --ids ITV-201,ITV-423,ITV-266` signs them (only `security.sig`
written). The catalog's `provenance.imported` lists 35 kids with a new digest. Guards: the
`SINGLE_CAUSE` table gains the four vectors (exact error lists; ITV-266 and ITV-423 by
validator and path, since their messages repeat the instance or the whole enum), and
`port_fixture_problems` requires ITV-482's capability to be the §7.6 value.

**ITV-423 isolation.** Comparing ITV-423's `oneOf` error and its path does not show that the
coexistence of `args` and `result` is the only cause: without `payload.type` the same outer
error appears. The comparison is kept, and `single_cause_problems` adds `EXCLUSIVE_PAIR`:
- the fixture carries both `payload.args` and `payload.result`;
- in-memory copies without `args` alone and without `result` alone each validate
  structurally. The corpus is not changed, and signatures are not checked on these copies.

The regression `single_cause_selftest` builds a copy without `payload.type`, with `args`
and `result` kept, re-signed with the catalog key of `agent:acme.billing#key1`. That copy
verifies with the A-97 guard. The strengthened check rejects it, because its `args`-only
and `result`-only copies keep the `oneOf` error at `payload`. The original passes. The
message schema and the general `--check-errors` comparator are unchanged.

Mutations, 10 of 10 detected:
- (a)–(c) ITV-201, ITV-423 and ITV-266 without `security` again → fixture guard;
- (d) ITV-482 without `capabilities` again → fixture guard;
- (e) the imported key removed and (f) altered → catalog guard and A-97 guard (ITV-266);
- (g) ITV-201 with main's Draft-01 signature → A-97 guard;
- (h) ITV-482 with another capability → fixture guard;
- (i) the isolation removed (accepted again on the `oneOf` error and path alone) →
  regression: "not detected: ITV-423 without payload.type";
- (j) the corpus ITV-423 without `payload.type`, re-signed so it verifies → fixture guard.
  On its first run (j) exposed that the regression raised `KeyError` when the corpus
  vector lacked `payload.type`; the regression now reports that case instead of raising.

The port's 23 mutations and the coverage SC4 23 still detect on the same candidate.

**Conflicts.** 18 files conflicted; `SECURITY.md` and `profiles/README.md` merged without a
marker and were reviewed hunk by hunk. Corpus, keypairs, the six specs and the five RTMs
were resolved to the Draft-02 side, plus the two Core corrections above. Every other file
was resolved hunk by hunk as listed.

**Parent comparison.**
- Against `de9db8d`, besides the ledger, evidence, notes and CLAUDE.md:
  - documentation and Core: CHANGELOG, README, SECURITY, VERSIONING, getting-started,
    Core, test-vector README;
  - the four repaired vectors, one added keypair (with its description and provenance),
    and `check_consistency.py` (the guards above).

  Schemas, the other scripts, RTMs and profiles are byte-identical.
- Against `origin/main`: of the lines main added outside the JSON files, those absent
  from the result are only Draft-01.1 labels and counts, the Draft-01 skip table, the
  RTM figures and rows above, and snippet lines replaced by their adapted form.

  | File | Main-added lines | Present | Absent |
  |---|---|---|---|
  | CHANGELOG.md | 80 | 80 | 0 |
  | README.md | 7 | 1 | 6 |
  | SECURITY.md | 3 | 1 | 2 |
  | VERSIONING.md | 2 | 1 | 1 |
  | FAQ.md | 1 | 0 | 1 |
  | getting-started.md | 5 | 2 | 3 |
  | RTMs | 39 | 3 | 36 |
  | profiles/README.md | 1 | 0 | 1 |
  | specs | 39 | 7 | 32 |
  | test-vectors/README.md | 35 | 14 | 21 |

**Battery on the merge state** (system Python and clean venv):
- validator 4 modes: TOTAL 491 / 228 / 923, 0 failures; crypto 157 checked, 145
  verified, 9 negatives, 3 canonical only;
- consistency 142, harness 783, examples and links OK;
- RTM 2045 / 1247 / 1445; `git diff --check` clean.

## 29. Cycle F closure evidence

Baseline `ddd1737`. The post-merge triage classified the ledger notes against `54c2726`:
- **R:** resolved, recorded in `ddd1737`;
- **F:** repository defects, fixed here;
- **U and C:** normative gaps and coverage limits, kept for the Issue and the normative
  cycles, never closed early;
- **I:** informational.

The owner's addendum during execution extended F6 to six vectors and F7 to every
platform-default record, after a stop: the guards, applied to the whole corpus, found
more cases than the inventory listed.

| Finding | Correction | Guard (`check_consistency.py`) | Mutation → failing check |
|---|---|---|---|
| A-101 | `profiles/README.md` Retention column from `defaults.retention_minimum` | `repository_text_problems` via `retention_cell_problem`. A non-null floor needs the backticked equal duration; a null floor needs the explicit "None (no floor …)" text. The first version took a failed extraction as a match, so `P365D` in the GDPR-STANDARD row passed (owner review); the self-test `retention_cell_selftest` now rejects it | (b) EU-AI-ACT-HIGH-RISK back to 180 days; (b2) GDPR-STANDARD row `P365D`; (b3) the extraction-as-match comparison restored → self-test |
| A-102 | Actions `#14-reserved-system-capabilities-normative-registry`; Routing `#74-relay-attestation-and-broker-audit-record`, with the link text. The second anchor was found by the guard's sweep before any write | `repository_text_problems` (every internal anchor of the six specs) | (c), (c2) |
| A-103 | `[RFC 8785] §3.1` in State l.496 and Assets l.552 | `repository_text_problems` | (d) |
| A-104 | `ROUTE-§1.2.2-12` (SHOULD, Evidence "—", the rule for non-mandatory rows); Routing summary 282 → 283, §1 50 → 51 | Existing totals check | (i) row removed → "Total requirements stated 283, table has 282". Limit: removing the row and the stated totals together is not detected; no linter reads SHOULD sentences without rows |
| A-105 | `expected_error` on ITV-417, ITV-579, ITV-563, ITV-577, INV-08 (`invalid_request`) and ITV-571 (`unauthorized`); `expected`, `valid`, `skip_schema` and the tested objects unchanged. ITV-577 tests the State §2.1.2 numeric restriction, not a parser-wide rejection of large numbers | `runtime_expectation_problems`: 13 vectors in scope; the "with error code '…'" wording of INV-18/19 is read correctly | (e) ITV-417, (e2) INV-08; (e3) the regex reads "error" as the code → INV-18/19 flagged |
| A-106 | 16 `broker_relay` records: `effective_retention` `P90D` and `retention_anchor` = `processed_at` added, `retained_until` = anchor + P90D (10 dates corrected). 20 GDPR-STANDARD records: `retained_until` = anchor + P90D, now equal to their own `obligation_resolution` retention result. 10 review records (ITV-632..637, INV-72..75): `retention_anchor` = `processed_at`, per Core §4.3.6.4.1, State §7.1 and Actions §3.9.5; their execution instants, review deadlines and `processed_at` are unchanged | `platform_default_retention_problems`: the three fields together, over 62 records | (f) ITV-146, (f2) ITV-688, (f3) ITV-97, (f4) ITV-632 |
| A-107 | ITV-713, 714 (`supervisory_authority`, without and with the SHOULD fields), ITV-715, 716 (`data_subject`, without and with `remediation_advice`); INV-178..206, single-cause negatives: 7 required, enum, UUID, timestamp, each string's minLength and maxLength, array and item types, integer type and minimum, additionalProperties. STATE-§5.7-02 Vector and Evidence now cite them; the envelope does not validate the payload (removing `nature_of_breach` from ITV-556 leaves it valid) | `breach_notification_problems`: both targets covered; each negative's `<field>: <keyword> — State §5.7` is its only error; STATE-§5.7-02 `struct:` is exactly the 33 vectors | (g) a second defect in INV-178, (g2) no `data_subject` positive, (g3) Evidence back to ITV-556/557 |

**Other changes.**
- **F1:** SPDX/Copyright header added to `docs/auditoria-spec-draft-01.md`,
  `docs/spec-audit-draft-01.md` and CLAUDE.md; LICENSE.md is exempt as the licensing
  notice itself. Mutation (a).
- **F8:** migration guide §9–§13, covering:
  - generations and retention-protected PURGE;
  - broker relay audit and DPoP;
  - approval decisions and key revocation (SC2);
  - parsing and the attestation header (SC3, SC4);
  - the corpus and keys.

  §6 now notes that a recipient acts on a revocation event only after authenticating it.
  Owner review: the verification evidence applies only to compliance-relevant messages
  whose signatures were successfully verified (Core §5.2); the RSA-1024 key yields a
  mathematically valid signature rejected for key size (ITV-425 `key`/`size`).
  "What did NOT change" no longer says PURGE is unchanged. The DR-1..DR-5 changes are
  not yet described (note).

**Not changed (observed).**
- 18 `profile-minimum` records whose `retained_until` diverges from their own
  `obligation_resolution` result (note).
- U items 1–6 and C items 7–12 of the triage, kept for the Issue and their cycles.
- The 11 and 12 limits are recorded in the notes.

**Mutations.** 18 of 18 detected: (a), (b), (b2), (b3), (c), (c2), (d), (e), (e2), (e3), (f),
(f2), (f3), (f4), (g), (g2), (g3), (i). The unmutated copy passed the whole battery first, and the
candidate was restored between cases.

**Counts before → after.**
- **Vectors:** 923 → 956 (489 schema-valid / 244 expected-invalid / 204 runtime-only /
  19 raw); formats schema-ref 557 → 590; prefixes ITV 712 → 716, INV 177 → 206; next IDs
  ITV-717, INV-207. 52 existing vectors changed (6 F6, 46 F7), only in the fields named.
- **RTM:** 2045 → 2046 rows (SHOULD 248 → 249; MUST+MUST_NOT 1247 and the mandatory
  1445 unchanged).
- **Checks:** consistency 142 → 146.
- **Findings register:** 103 → 110 rows, all closed.
- **Coverage register:** 25 → 26 rows, all closed.

## 30. Maintenance cycle closure evidence

Baseline `97b421a`. The cycle F observation listed 18 `profile-minimum` records whose
`retained_until` diverged from their own `obligation_resolution`. The inventory of every
audit record of the corpus (an object with `retention_source` and `processed_at`, at any
depth) found two more groups, and the owner extended the scope to all three (maintenance
addendum). These are fixture corrections against the current contract (State §7.1,
§7.3; Core §4.3.6.4.1, §4.3.10.5), not a normative change.

| Finding | Correction | Guard (`check_consistency.py`) | Mutation → failing check |
|---|---|---|---|
| A-118 (A, 18) | ITV-16, ITV-88..92, ITV-95, ITV-96, ITV-99, ITV-220, ITV-269, ITV-525, ITV-586, ITV-588, ITV-681, INV-47, INV-50, INV-84: `retained_until` set to the resolution's `result.retained_until` (MIFID-II `P1827D` from 2026-04-27T14:00 is 2031-04-28T14:00, not 2033; EU-AI-ACT-HIGH-RISK `P6M`) | `audit_retention_problems` | (a) ITV-16 back to 2026-10-24 |
| A-118 (B, 20) | ITV-17, ITV-93, ITV-94, ITV-100, ITV-101, ITV-102, ITV-105, ITV-337, ITV-582..585, ITV-587, INV-46, INV-141..144, ITV-697, ITV-698: `effective_retention` (the catalog floor) and `retention_anchor` = `processed_at` added, `retained_until` = anchor + floor. ITV-17, ITV-100 and ITV-101 are GDPR-STANDARD, which has no floor: `retention_source` `platform-default`, `P90D` (Core §4.3.10.5); ITV-17's `retained_until` was already anchor + `P90D` and is kept | `audit_retention_problems` | (b) ITV-93 without `effective_retention`; (d) ITV-17 back to `profile-minimum`; (e) ITV-588 anchored before `processed_at` |
| A-118 (C, 1) | ITV-55 `/data/records/0` (audit query response, `platform-default`): `retained_until` 2033-04-10 → 2026-07-09, its resolution's result | `audit_retention_problems` (nested records) | (c) ITV-55 back to 2033 |
| A-118 (chain) | ITV-95 (`chain_seq` 1): `hash_chain` recomputed with `runtime_harness.chain_value(record, None)` in consequence of the retention correction. The old value was not invalid in itself: it authenticated the record with the wrong date. No other vector references its value or `chain_id` | DR-5 chain check; harness R14 (a) | (f) the old chain value → "DR-5 chained vectors recompute and verify" and R14 (a) |
| A-119 | `platform_default_retention_problems` (cycle F) replaced by `audit_retention_problems` with `audit_retention_selftest`. The check name carries the counts "(112 records, 19 controls)"; the RTM `check:` token of STATE-§7.1-23 cites it without the counts | Self-test controls (19) | (g)–(j), (m)–(p) below → self-test; (j2) → control count; (k), (l), (l2) → corpus |

**Guard rules.**
- With a resolution, `declared_retention` is the axis declaration (`null` when omitted, a
  conflict included).
- A resolved axis must match (`effective_retention`, `retention_anchor`, `retained_until`)
  = the result; the result itself is (`processed_at`, anchor + duration); and
  `retention_source` follows the fill source. The guard compares with the composed
  result, never with the catalog.
- A conflict keeps the evidence under the profile's `retention_minimum`, with
  `profile-minimum` as source.
- Without a resolution: `profile-minimum` is the catalog floor (a profile without floor is
  reported), `platform-default` is `P90D`, and `per-message` is the declared value.
  Audit records in this corpus have an applicable retention period under State §7.3 (the
  profile's minimum, or the `P90D` Default when no profile is active or the profile has
  no floor). The guard rejects `retention_source: "none"` without a resolution and does
  not allow that label to bypass resolution consistency or retention arithmetic. A
  resolved retention axis requires a result containing `duration`, `anchor` and
  `retained_until`.
- Whenever `effective_retention` is present: anchor = `processed_at`, and `retained_until` =
  anchor + effective (calendar arithmetic). The label never switches this off.
- Each problem names the fields its rule depends on. A vector whose `expected_error` names
  a retention field exactly is an intentional negative of that field: only the rules that
  depend on it are left to its expectation, and every other rule still applies to the
  record. INV-53 (`declared_retention` required) is therefore checked on its other fields.
  INV-94 and INV-100 name `entry_retained_until` and are checked in full.
- Each failing self-test control names the problem its rule must report, so another rule
  reporting the same record cannot mask it.
- Applied to the baseline corpus, the guard flags exactly the 39 vectors; after the
  corrections it passes on 112 records. The existing `retention_derivation_problems`
  (DR-3/DR-4) stays; it compares neither `retained_until` nor invalid vectors, which is
  why the 18 passed it.

**Fixture checks.** Only the 39 vectors changed. Schema errors are equal before and after
in validator, path and sub-errors; INV-47's message text includes the instance, and its
two `anyOf` sub-errors are unchanged. No description cites a date, and none of the
records is signed.

**Migration guide.** §14 (DR-1/DR-2: oversight authority, executor provenance,
post-execution review), §15 (DR-3/DR-4: the resolution procedure, composition, high-risk
requests, provenance, rejections, onboarding context) and §16 (DR-5: chain construction,
conformance, queries, tombstones, CHECK-04, declared limits). "What did NOT change" is
now §17 and states that the intent enum is unchanged (review uses `event`). §3 adds the
no-declaration, no-floor default and the derived retention fields. Each statement was
checked against the cited section:
- Actions §3.7, §3.9.1–§3.9.4;
- Core §4.3.8 Rule 3, §4.3.10.2–§4.3.10.6, §4.4.8, §6.1;
- Identity §7.2 Step 7, §7.4, §8, CHECK-04;
- Assets §5.2 Step 5;
- State §7.1, §7.2, §7.3, §7.4.

Two sentences of the first draft were corrected during the cycle, for precision against the text:
- an objection never changes the execution's terminal state (Actions §3.9.4);
- rule entries and profile floors are identified by digest, identity facts by agent-id and
  evidence (Core §4.3.10.2).

**Mutations.** 21 of 21 detected: (a), (b), (c), (d), (e), (f), and the guard mutations:
- (g) reading only the root record (positive nested control);
- (h) ignoring a divergence from the resolution (an internally consistent control);
- (i) comparing `profile-minimum` with the catalog despite a resolution (composed floor
  `P10Y` against the catalog `P6M`);
- (i2) no `declared_retention` check (the `"P1D"` control);
- (i3) conflict source not checked;
- (i4) end-date rule removed;
- (j) anchor rule removed with the self-test active;
- (j2) self-test call removed, detected outside the self-test because the check name
  shows "0 controls" instead of 19;
- (k) INV-53 with `retained_until` 2033-04-27T14:00, its missing `declared_retention` kept
  (the owner's reproduction; the schema errors are unchanged);
- (l) ITV-17 relabelled `"none"` with `retained_until` 2033-04-27T14:00 (the owner's
  reproduction), and (l2) relabelled `"none"` with its correct date;
- (m) an intentional negative skipping the whole record again;
- (n) the field exemption removed;
- (o) the State §7.3 rule for `"none"` removed;
- (p) the arithmetic switched off by the label again.

Two weaknesses were found and fixed in the self-test while building the campaign:
- the divergence control was also caught by the arithmetic rule;
- the nested control passed for the wrong reason ("no audit record") when the guard read
  only the root.

The owner's double check (2026-11-08) found two gaps in the guard and one imprecision in
the guide, all fixed in this cycle without touching the 39 fixtures:
- the INV-53 exemption skipped the whole record, so a tampered `retained_until` passed;
  the exemption is now limited to the rules on the named field (controls 18 and 19);
- `retention_source: "none"` switched off the anchor and end-date checks, so ITV-17
  relabelled `"none"` with a 2033 date passed both this guard and
  `retention_derivation_problems`; `"none"` is now checked against State §7.3, and the
  arithmetic depends on the presence of `effective_retention` (controls 16 and 17);
- guide §16 stated the chain limits without their conditions; it now keeps those of
  State §7.2: tail truncation goes undetected when the verifier holds no later head, and
  a withheld chain can be noticed against the operator's documented chains or an
  independently held head.

**Counts.** Vectors 956 (39 changed); RTM 2046 rows, one Evidence token added; checks 146
(one replaced); findings register 120 → 122 rows (open 10, closed 112).

## 31. State cycle closure evidence

Baseline `ddf2578`. Normative cycle for the three State items of Issue #2 (B1, B2, B3),
decided by the owner on 2026-11-17 and planned with two owner reviews (State cycle
addendum). A fourth finding, A-120, was registered in the review of the plan.

| Finding | Contract | Vectors | Executed by | Mutation → failing check |
|---|---|---|---|---|
| A-108 | State §8.3 rule 1 (selection, validation), §2.1.9, §3.1.2 rule 5, §4.2.1, §8.4; Core §4.3.10.5, §4.3.10.6 | ITV-536 (inherits `DE`), ITV-537 (`EU`/`FR`), ITV-717 (`FR`/`FR`), ITV-718 (MIFID-II default `EU`, `FR`), INV-207 (`DE`/`FR`), INV-208 (`FR`/`EU`), INV-209 (MIFID-II default `EU`, `US`) | R10, on each vector's own message (`input.from_message`) | (s1)–(s7) below |
| A-109 | State §3.2.1 (result table, "Snapshot hash"); Actions §1.4; `arsia-state-operations.schema.json` `snapshot-result.hash` pattern | ITV-174, ITV-286, ITV-677, INV-88 (recomputed), INV-210 (new) | R17 (k); guard `snapshot_hash_problems` | (s8)–(s13), (s23), (s27), (s28) |
| A-110 | State §2.1.8 ("Fixed per generation"), §3.1.2 rule 7, §8.3 rule 2, §3.2.2 step 1, §4.1.1, §8.4; `arsia-message.schema.json` `$defs/error-details-retention-fixed` | ITV-719 (accepted, `P12M` over `P1Y`), ITV-720, ITV-721, ITV-722 (`retention_fixed`), ITV-723 (PURGE after a late update) | R18 (l) and the scenario vectors | (s14)–(s22b) |
| A-120 | ITV-536..539 as conformant SET requests | ITV-536, ITV-537, ITV-538, ITV-539 (`scope: "agent"`, key segment `agent`, re-signed) | guard `set_fixture_problems` | (s25), (s26) |

**A-108, residency.**
- The rule separates selection from validation. A zone present in `payload.args` is the
  entry's own zone; without it a SET does not change an entry's own zone, and an entry
  that has none inherits the message's filled value, a profile default included.
- Validation applies to a zone present in `payload.args`: normalized to country codes, it
  is a subset of the restriction composed for the message. `FR` under `EU` and `FR` under
  `FR` are accepted; `FR` under `DE` and `EU` under `FR` are rejected with
  `invalid_request` and `obligation_conflict` on the `residency` axis.
- The comparison uses the composed restriction: INV-209 declares no
  `compliance.data_residency`, the MIFID-II default fills `EU`, and `US` is rejected.
- Conflict item: `axis` `residency`, `declared` the args zone, `required` the composed
  restriction (`codes`, with `revision` and `sha256` after a regional expansion),
  `sources` the requirement sources. The rejection record (`rejection_cause:
  "compliance"`) validates against `arsia-audit-record.schema.json`.
- Session entries (State §1.1) are outside the rule: the zone in args is not validated
  against the message and nothing is inherited (two R10 controls).
- What the cycle closes is the explicit zone in args against the composed restriction. No
  specific check of a stored zone against a later message without args is defined; the
  text says so and keeps the existing restrictions of the message and of the entry in
  force (notes, "Stored zone against a later message").
- The `resolution` scenario built a fixed payload, so a change to a vector's envelope did
  not change the executed case. With `input.from_message` the harness runs the vector's
  own `compliance` and `payload`.

**A-109, SNAPSHOT hash.**
- `hash` = `"sha-256:"` + lowercase hex SHA-256 over the RFC 8785 form of
  `{as_of, entries}` as carried, in the order carried. `hash` and `timestamp` are not
  hashed. No order is defined for `entries`.
- The four earlier fixtures used the prefix `sha256:`; ITV-174 and ITV-286 carried the
  digest of the empty string. All four now carry the construction. INV-88 keeps its
  defect (an entry without `generation`) and its schema error, with a correct hash.
- INV-210 is the single declared exception of the guard: the legacy prefix, a digest that
  still matches its content, and exactly one schema error, `pattern` at `result/hash`.
  Negatives are not exempted as a block.
- R17 (k): the three positive vectors verify; a changed value, the same entries in
  another order and another `as_of` change the hash; a later `timestamp` does not.

**A-110, retention per generation.**
- The effective retention is resolved when the generation is created, also when it comes
  from a profile floor, and is preserved. An update is validated in full: Rule 4 first (a
  compliance rejection), then the value that applies (`payload.args.retention`, else the
  envelope's `compliance.retention`) and the floors of the request, compared by the
  instant they produce from `created_at`.
- An incompatible update is rejected before any write with `invalid_request` and the
  details `retention_fixed`, `entry_retained_until` (or `null`) and
  `required_retained_until`. `retention_fixed` is a State validation, like
  `scope_mismatch`; it is not a diagnostic of Core §4.3.10.6.
- The schema applies `error-details-retention-fixed` through its own conditional (code
  `invalid_request`, discriminator `retention_fixed`); the `within_retention` conditional
  is unchanged.
- The reference store receives the inputs of the message (`retention`, `compliance`,
  `scope`) and resolves them: args or envelope, floor from the profile catalog. R18 (l)
  controls: `P12M` over `P1Y` accepted; another value in args rejected; args omitted with
  an incompatible envelope value rejected, with a compatible one accepted; creation under
  a floor preserves the floor, a later update under the same profile is accepted and
  under a higher floor rejected; a value below the floor is Rule 4, not
  `retention_fixed`; an entry with no retention period accepts neither a value nor a
  floor; every rejection leaves value, version, preserved retention and records
  unchanged; the response validates against the `$def` and in the error envelope;
  recreation takes its own period; session entries carry no retention and are not
  rejected.
- Declared cost: an update does not restart the period (ITV-723: created 2025-04-20 with
  `P1Y`, updated 2026-04-19, PURGE on 2026-04-27 is beyond retention).

**A-120, SET fixtures.** ITV-536..539 lacked `scope` and used the key segment `user`. They
fail `set-args` at the baseline and validate after the repair. The guard also covers the
five new residency vectors. No other fixture was swept.

**Guards (`check_consistency.py`, 146 → 149).**
- `snapshot_hash_problems` with `snapshot_hash_selftest`: "(5 results, 13 controls)". The
  hash is matched in full, so nothing may follow the digest.
- `set_fixture_problems`: args against `set-args`, key scope segment, agent prefix.
- `state_cycle_echo_problems`: the replaced sentences are absent from `spec/`, and State
  §2.1.8, §2.1.9, §3.1.2, §3.2.1, §3.2.2, §4.2.1, §8.3, §8.4, Core §4.3.10.5, §4.3.10.6
  and Actions §1.4 state the rules.

**Mutations.** 39 of 39 detected.
- A-108: (s1) ITV-537 back to `DE`/`FR`; (s2) pure intersection, a wider zone accepted;
  (s3) the literal field only; (s4) inheritance without the profile default; (s5) an
  update without args replacing the stored zone; (s6) the rule applied to session; (s6b)
  session inheriting; (s7) the scenario back to a fixed payload.
- A-109: (s8) legacy prefix in ITV-286; (s9), (s9b) `timestamp` hashed; (s10) order
  ignored; (s11) no digest check on negatives; (s11b) legacy prefix accepted in any
  negative; (s11c) the declared negative not required to fail only the pattern; (s12)
  self-test call removed, seen in the control count; (s13) INV-88 with a wrong hash; (s27)
  ITV-677 reordered; (s28) INV-210 with a wrong digest; (s23) the pattern removed.
- A-110: (s14) retention ignored on update; (s15) string comparison; (s16) floor ignored;
  (s17) envelope value ignored; (s18) a rejected update writing a version; (s19) an update
  restarting the period; (s20) `retention_fixed` where Rule 4 applies; (s21) the rules
  applied to session; (s22) the `$def` not applied; (s22b) creation under a floor
  preserving nothing.
- Owner double check: (s29) the envelope's declared retention escaping Rule 4 when
  `payload.args` is present; (s29b) a session SET escaping the floor of its own message;
  (s30) the guard accepting a line break after the digest; (s31) the schema accepting it.
- Echoes and fixtures: (s24) the old precedence sentence; (s24b) the old PURGE wording;
  (s24c) the session exception removed; (s25) ITV-538 without `scope`; (s26) ITV-539 with
  the key outside its scope.

Two weaknesses were found and fixed while building the campaign:
- (s11b) was not detected: no control declared a legacy prefix in a negative with another
  expectation. Control added (10 → 11).
- (s14) made the harness stop with an exception after its first two failures, so the
  vector checks did not run. The R18 controls no longer index a missing `details`.

The owner's double check (2026-11-17) reproduced two defects, fixed in this cycle:
- A-110: the reference store checked Rule 4 only on the value selected for the entry, so
  an update (or a creation) with a compatible `payload.args.retention` and an envelope
  `compliance.retention` below the floor was accepted and written, while the resolver
  rejects that `compliance`. The envelope's declared retention is now checked before any
  write, whatever value is selected and for every scope; args `P1Y` with an envelope
  `P2Y`, both above the floor, stays accepted and preserves `P1Y` (four R18 (l) controls).
- A-109: the schema pattern and the guard's `match` accepted a line break after the
  digest, also in INV-210's declared exception. The schema gains `maxLength: 72` and the
  guard matches the hash in full, the legacy prefix included (two controls, 11 → 13; one
  R17 (k) check). The schema states only the maximum: the pattern already excludes any
  shorter value, and a minimum would give INV-210 (71 characters) a second error.

**Regression.** The scripts of the earlier campaigns were lost with the session's scratch
directory. They were rebuilt from the session record, by replaying only the operations
that wrote each script, and their mutation counts match the documented ones. All ran on
the corrected candidate and detected every mutation: maintenance 21, cycle F 18, main
reconciliation 10, port 23, coverage SC4 23.

**Counts.** Vectors 956 → 967 (11 new, 8 changed); runtime-only 204 → 209; crypto blocks
157 → 165 (153 signatures verified, 9 negatives, 3 canonical only); consistency checks
146 → 149; harness checks 783 → 854; RTM 2046 → 2055 rows (MUST + MUST_NOT 1247 → 1256;
with REQUIRED 1445 → 1454); findings register 122 → 123 rows (open 10 → 7, closed 116). The
maintenance-cycle retention guard now reads 113 audit records (ITV-723 added), with its 19
controls.

## 32. Routing cycle closure evidence

Baseline `d41783c`. Normative cycle for the two Routing items of Issue #2 (B4, C1),
decided by the owner on 2026-11-17 (Routing cycle addendum). The owner's review of the
implementation required, before the commit, the single-cause and order controls of
R22 (i) and the wording of the two short A-117 texts recorded below; they are part of
this cycle.

| Finding | Contract | Vectors | Executed by | Mutation → failing check |
|---|---|---|---|---|
| A-111 | Routing §7.4.1 (table row, "Zone.", step 3), §1.2.2 step 7, §5.3; `arsia-relay-attestation.schema.json` `residency_zone` description | ITV-569 (`EU`/`EU`, control), ITV-724 (`PT`/`PT`, accepted), INV-211 (`EU`/`PT`), INV-212 (`PT`/`EU`) | R22 (a), (b), (i) | (r1)–(r9), (r18)–(r20) below; text (r10), (r11), (r14), (r15), (r17) |
| A-117 | Routing §2.3.3 ("Relay identifier"), §7.4.1 (replay handling), §7.4.2; `arsia-message.schema.json` `error-details-relay-failed.relay_id` description | none | guard `routing_cycle_echo_problems` | (r12), (r13), (r16), (r21), (r22) |

**A-111, attestation zone.**
- Before the cycle, R22 verified the broker's authorisation for the zone of the message
  and never read the attestation's `residency_zone`: a message that declares `EU` with a
  correctly signed attestation for `PT` was accepted (reproduced by the owner on ITV-569).
- The broker sets `residency_zone` to the value of the message's
  `compliance.data_residency`, unchanged. In step 3 the recipient requires the two to be
  equal as strings, then verifies the broker's jurisdiction and capability for that zone.
  A failure is `unauthorized`, under the existing rule for steps 2-5.
- No normalization, regional expansion or containment applies, in either direction:
  INV-211 (message `EU`, attestation `PT`) and INV-212 (message `PT`, attestation `EU`)
  are rejected at step 3.
- Single cause in both negatives: the attestation signature verifies (R22 (b)) and the
  broker's jurisdiction `PT` satisfies both zones. The permanent control is R22 (i)
  "has a single defect": each negative with only `residency_zone` corrected to the
  message's zone, re-signed, is accepted in full, so every binding of steps 4 and 5
  holds in the fixture. A second defect that the zone mismatch would hide (a wrong
  `authorization_token_hash`, another `message_id`) fails that control ((r19), (r20)).
- Order: the zone is verified in step 3, before the bindings of step 4. R22 (i) runs
  each negative with a wrong `envelope_hash` as well, re-signed: the result is
  `unauthorized` at step 3. The same wrong `envelope_hash` with the zone corrected is
  `unauthorized` at step 4, which shows that the added defect is a step 4 defect and
  that the signature passes step 2. A comparison moved after the bindings, still
  reporting step 3, fails the first of the two ((r18)).
- The synthetic variants are re-signed with a key of the harness, published under the
  attestation's kid in the JWKS given to the recipient; they add no vector to the
  corpus and use no catalog private key.
- ITV-724 shows the comparison uses the message's own value and not a fixed `EU`; with
  a broker in `IE` it is rejected at step 3, so equal zones do not replace the
  jurisdiction check.
- ITV-724 and INV-212 carry an envelope that declares `PT`: the envelope of CTV-02 with
  its own `id` and idempotency key, signed with the catalog key of its kid. The three
  attestations are signed with the catalog key `agent:arsialabs.broker.eu-west#2026q1`.
- The rule uses the literal `compliance.data_residency`, the field the procedure of
  §7.4.1 already uses; the cycle adds no resolution of defaults and no regional
  composition.

**A-117, identifiers.**
- `relay_id` identifies the relay operation in the receipts and errors the broker sends
  to the sender, also when the message is not forwarded (a Rule 9 error, ITV-517, has a
  `relay_id` and no attestation exists). `attestation_id` identifies the attestation
  issued when forwarding is initiated.
- The two have independent semantics: no equality, inequality or mapping is required,
  and a consumer MUST NOT assume equality. The two short texts (§7.4.1 replay handling,
  the `relay_id` schema description) say that the values "are not required to be equal
  or different"; the earlier wordings "is not the `relay_id`" and "distinct from
  attestation_id", which read as required inequality, are rejected by the guard
  ((r21), (r22)). The correlation of the attestation with the
  `broker_relay` record by the same `attestation_id` is unchanged.
- No vector and no harness code changed for this item. The reference harness reuses one value for both
  in its DPoP flow, which the rule permits. The RTM row of the MUST NOT
  (ROUTE-§2.3.3-06) is recorded as `out-of-repo(external-party)`: a consumer's
  assumption is not observable in the repository.

**Mutations (candidate copy identical to the final diff; 22 of 22 detected).**
- (r1) zone comparison removed → `R22 (a) INV-211`, `R22 (a) INV-212` (accepted).
- (r2) containment, attestation zone inside the message zone → `R22 (a) INV-211`.
- (r3) containment reversed → `R22 (a) INV-212`.
- (r4) attestation zone compared with the broker's jurisdiction → both negatives.
- (r5) comparison made in step 5, reporting step 5 → both negatives report step 5. This
  mutation changes the reported number as well; the order alone is (r18).
- (r6) jurisdiction check removed → `R22 (a) INV-121`, `R22 (i) equal zones do not
  replace the jurisdiction check`.
- (r7) INV-211 with zone `EU`, re-signed → `R22 (a) INV-211`, `R22 (i) zone vectors
  present`.
- (r8) INV-211 with a broker in `IE` → `R22 (i) INV-211: the broker's jurisdiction
  satisfies both zones`.
- (r9) ITV-724 with zone `EU`, re-signed → `R22 (a) ITV-724`, `R22 (i) zone vectors
  present`.
- (r10)–(r17) text and schema descriptions reverted (step 3, "Zone.", the MUST NOT, the
  "Relay identifier" paragraph, the table row, the two schema descriptions, the echoes
  of §1.2.2 and §5.3) → `Routing cycle anti-regression`.
- (r18) order only: the comparison moved after the bindings of step 4, still returning
  step 3 → `R22 (i) INV-211 with a wrong envelope_hash too`, `R22 (i) INV-212 with a
  wrong envelope_hash too` (step 4 reported). `R22 (a)` does not detect this mutation.
- (r19) INV-211 with a wrong `authorization_token_hash`, re-signed → `R22 (i) INV-211
  has a single defect`.
- (r20) INV-212 with another `message_id`, re-signed → `R22 (i) INV-212 has a single
  defect`.
- (r21) §7.4.1 replay handling back to "is not the `relay_id`" → `Routing cycle
  anti-regression`.
- (r22) `relay_id` description back to "distinct from attestation_id" → `Routing cycle
  anti-regression`.

**Regression.** The campaigns of the earlier cycles ran on the same candidate and
detected every mutation: State 39, maintenance 21, cycle F 18, main reconciliation 10,
port 23, coverage SC4 23.

**Counts.** Vectors 967 → 970 (3 new, none changed); runtime-only 209 → 211; crypto
blocks 165 → 168 (156 signatures verified, 9 negatives, 3 canonical only); consistency
checks 149 → 150; harness checks 854 → 873; RTM 2055 → 2057 rows (MUST + MUST_NOT
1256 → 1258; with REQUIRED 1454 → 1456); findings register 123 rows (open 7 → 5, closed
118).

## 33. Assets/audit cycle closure evidence

Baseline `97bf253`. Normative cycle for the two Assets/audit items of Issue #2 (B5, B6)
and post-merge triage item 14, decided by the owner on 2026-11-18 (Assets/audit cycle
addendum). The owner's two reviews of the plan added, before implementation: the
explicit reversal exception in Assets §3.2.1; the A-59 adjustment that lets the generic
`asset_transfer` row and the compound reversal row coexist, with a positive self-test
case; the permanent negative controls of R23 and the explicit source of ITV-727; a
coherent chronology for the reversal chain; and a MUST in Assets §6.2.3 for the RTM to
trace. All are part of this cycle. The owner's review of the implementation added the
record-type checks of R23 and their controls (below).

| Finding | Contract | Vectors | Executed by | Mutation → failing check |
|---|---|---|---|---|
| A-113 | Assets §3.3.2, §3.2.1, §5.1.3; State §7.1 (compound row, paragraph after the table, `payload_type`); `arsia-audit-record.schema.json` compound conditional and the `payment_reference` and `original_audit_id` descriptions | ITV-725 (reversal), ITV-728 (error record of a reversal), INV-214, INV-215; chain ITV-96 → ITV-725 → ITV-377 | validator; R23 (a), (c), (d); A-59 and its self-test | (a2)–(a4), (a8)–(a10), (a12), (a13), (a15), (a17), (a18), (a25), (a27), (a28), (a30); text (a19)–(a21) |
| A-121 | State §7.1 (`event_type` = `asset_transfer` row and paragraph); Assets §3.2.1; schema conditional | ITV-96 (changed), INV-213 | validator; A-59 | (a1) |
| A-112 | Assets §6.2.3 (MUST), §6.2.2 (`resolved_at` string or null); State §7.1 (row, paragraph, exception sentence removed); seven schema properties as `$ref` to the incident payload; `ict_incident` conditional; A-59 exception removed | ITV-102 (changed), ITV-726, ITV-727, INV-216..225 | validator; R23 (b), (d); cycle check | (a5)–(a7), (a11), (a14), (a16), (a26), (a29); text (a22)–(a24) |
| A-122 | registered, not corrected | — | — | — |

**A-113 and A-121, asset_transfer and reversal records.**
- Every `asset_transfer` record carries `payment_reference`, the reference of the
  transfer it belongs to: a plain transfer's own, the escrow transfer's, and on a
  reversal record the original transfer's. A query by it can return several records of
  one chain; the receipt's `audit_id` identifies a single record.
- A reversal record is identified by the compound condition `event_type`
  `asset_transfer` and `payload_type` `arsiaprotocol.assets/transfer-reversal`; it also
  carries `original_audit_id`, the `record_id` of the original record, which the
  original receipt's `audit_id` references. `sub_type` stays reserved to escrow. The
  reversal receipt keeps its new reference, which differs from the `payment_reference`
  of the record its `audit_id` references; Assets §3.2.1 states that exception
  explicitly so that its generic sentence does not read as the receipt's reference.
- The condition is compound in both directions: a record reduced to `event_type` would
  impose `original_audit_id` on plain and escrow records (ITV-96 and ITV-88 fail, (a2)),
  and one reduced to `payload_type` would impose the references on the error record of
  a reversal request (ITV-728 fails, (a25)).
- A-59 guard: condition values are read whole (`` `[^`]+` ``), so the payload type with
  `.`, `/` and `-` is no longer reduced to `event_type`; the generic row accepts a
  compound condition's fields already REQUIRED on it (`required | optional`), which
  the owner had reproduced as the interaction that would otherwise fail; a condition on
  `payload_type` needs a table row of its own. The self-test runs on the real table and
  schema, where both rows coexist without a problem, and requires four defects to be
  reported: the compound row reduced to the generic event, the schema condition without
  its `payload_type` predicate, the payload type truncated in the table, and the compound
  condition without a row.
- Chain ITV-96 → ITV-725 → ITV-377 (R23 (a)): the original is an `asset_transfer`
  record and the reversal an `asset_transfer` record of a transfer-reversal; the
  reversal's `payment_reference` is the
  original's, its `original_audit_id` the original's `record_id`; the receipt's
  `audit_id` is the reversal's `record_id`, its `payment_reference` (`…-REV-1`) differs,
  and its `correlation_id` is the reversal's `message_id`; original `processed_at` <
  reversal `processed_at` ≤ receipt `ts`. ITV-377 is unchanged; ITV-96 moves to
  2026-04-14T14:00:00.000Z and ITV-725 is processed at the receipt's `settled_at`,
  2026-04-15T11:12:30.456Z; `retained_until` is computed by the harness calendar
  (2031-04-15T14:00:00.000Z and 2031-04-16T11:12:30.456Z). The scenario verifies the
  audit links and their chronology, not the reversal window, which depends on the
  original receipt's `settled_at`.
- R23 (c): the `obligation_resolution` and retention fields of ITV-96 and ITV-725 are
  those `resolve_obligations` yields from their source `compliance` at their
  `processed_at`. ITV-96's source is the minimal `{"profile": "MIFID-II"}`, which
  reproduces its resolution in full; it is the fixture's source, not the recovery of a
  historical message. ITV-725's source is the compliance object of the Assets §3.3.3
  example (`MIFID-II`, `audit_required: true`, `retention: "P1827D"`), whose `id` is
  ITV-377's `correlation_id`: `declared_retention` `P1827D`, `retention_source`
  `per-message`.
- ITV-96 also moves to `payload_type` `arsiaprotocol.assets/transfer-request` and
  `to_agent` `agent:acme.transfer-processor`, the log of the reversal.

**A-112, ict_incident records.**
- The record carries `incident_type`, `affected_service`, `started_at`,
  `estimated_impact`, `severity` and `original_payment_reference` (REQUIRED) and
  `resolved_at` (OPTIONAL: absent, `null` or a timestamp). The seven audit-record
  properties are `$ref`s to the fields of `arsia-dora-incident.schema.json`, so types,
  enums, formats and limits are the payload's by construction; the cycle check requires
  each `$ref` and the equality of the two `required` sets.
- Assets §6.2.3 states the obligation as a MUST: the record carries the fields of the
  event's `payload.data` with the same values, and `resolved_at` exactly when the event
  has it. State §7.1 describes the record without a keyword of its own. Assets §6.2.2
  types `resolved_at` as string or null, as the schema and the §6.2.5 example allowed.
- R23 (b) requires `event_type` `ict_incident` and compares each record with an
  independent source, never rebuilt from the record: ITV-102 with ITV-139 (timestamp), ITV-726 with ITV-41 (`null`), ITV-727 with
  an explicit copy of ITV-41's payload without `resolved_at`, held in its
  `test_metadata`. `resolved_at` is compared by presence and by value, and `payload_hash`
  is the SHA-256 of the source's RFC 8785 payload.
- ITV-102 moves from `arsiaprotocol.assets/dora-incident`, which no specification
  defines, to `arsiaprotocol.ict/incident`, with ITV-139's fields and payload hash.

**R23 record types.** The schema accepts an incident record or a plain transfer record
whose `event_type` is changed to `error`: no rule forbids incident or transfer fields on
other record types, and the cycle does not add one. The owner reproduced that R23 then
still passed, because it did not check the type of the incident record or of the
original record. R23 now requires `event_type` `ict_incident` on each incident record
and `asset_transfer` on the original record of the chain; the reversal's type was
already checked.

**R23 negative controls (permanent, synthetic, no new IDs).** Each must be reported:
each of the original record, the reversal record and an incident record with only its
`event_type` changed to `error` (a diagnostic on `event_type`); a record with `resolved_at: null` against an event without the member; a record without
the member against an event with `null`; a reversal whose `original_audit_id` is another
record's (ITV-102's); a reversal processed before the original; and, with the source
intact, a record whose `severity` is another allowed value and whose `payload_hash` is
recomputed for the payload that record implies. The first two detect a comparison by
value only (`.get()` equates absent/absent and `null`/`null`); the last one discriminates
the source: a comparison with the independent source rejects it, and one that rebuilds
the source from the record accepts it.

**A-122 (registered, open).** Seven escrow records (ITV-88..92, ITV-586, INV-47) and
the `request` record ITV-95 carry `payload_type` `arsiaprotocol.assets/transfer`, which
no specification defines. None changes result under this cycle's rules. Correcting the
escrow fixtures needs a decision on the message that originates each transition (a
timeout return has none); ITV-95's `hash_chain` covers the value. It goes to the
schema-alignment cycle.

**Mutations (candidate copy identical to the final tree; 30 of 30 detected).**
- (a1) the `asset_transfer` rule removed → INV-213, A-59.
- (a2) the reversal rule reduced to `event_type` → ITV-96 (and the escrow records), A-59.
- (a25) the reversal rule reduced to `payload_type` → ITV-728, A-59.
- (a3) the rule's payload type truncated → INV-214, A-59.
- (a4) the reversal rule without `original_audit_id` → INV-214, A-59.
- (a5) the `ict_incident` rule without `severity` → INV-220, A-59.
- (a6) `severity` replaced by `{"type": "string"}` → INV-222, the cycle check (mirror).
- (a7) the `ict_incident` exception reintroduced → A-59.
- (a8) the generic-row check back to `req <= optional` → A-59 and its self-test (real case).
- (a9) the parser back to `[a-z_]+` → A-59 and its self-test.
- (a10) no row required for a `payload_type` condition → self-test (d).
- (a11) R23 `resolved_at` by value only → both presence controls.
- (a12) R23 without the `original_audit_id` comparison → the other-record control.
- (a13) R23 without the chronology check → the order control.
- (a14) R23 rebuilding the incident source from the record → the independent-source
  control.
- (a15) ITV-725 with another record's `original_audit_id` → R23 (a).
- (a16) ITV-726 with a `severity` different from its event → R23 (b) ITV-726.
- (a17) ITV-96 back to 2026-04-27 → R23 (a) (chronology), R23 (c) ITV-96.
- (a18) ITV-725 with ITV-96's retention result → R23 (c) ITV-725.
- (a19)–(a24) Assets §3.2.1, §3.3.2, §5.1.3, §6.2.2 and §6.2.3 texts and the State §7.1
  exception sentence reverted → the cycle check.
- (a26) R23 without the `ict_incident` type check → the incident-type control.
- (a27) R23 without the original record's type check → the original-type control.
- (a28) R23 without the reversal record's type check → the reversal-type control.
- (a29) ITV-726 with `event_type` `error`, accepted by the schema → R23 (b) ITV-726.
- (a30) ITV-96 with `event_type` `error`, accepted by the schema → R23 (a).

**Regression.** The campaigns of the earlier cycles ran on the same candidate and
detected every mutation: Routing 22, State 39, maintenance 21, cycle F 18, main
reconciliation 10, port 23, coverage SC4 23. The maintenance campaign checks that the
retention guard prints its record and control counts; its expected text was "113
records, 19 controls" and is now "130 records, 19 controls", because this cycle adds 17
audit records. The 19 controls are unchanged.

**Counts.** Vectors 970 → 987 (17 new: ITV-725..728, INV-213..225; 2 changed: ITV-96,
ITV-102); runtime-only 211 (unchanged); crypto blocks 168 (unchanged); consistency checks
150 → 152; harness checks 873 → 888 (R23 new); RTM 2057 → 2062 rows (MUST + MUST_NOT
1258 → 1260; with REQUIRED 1456 → 1461); findings register 125 rows (open 5 → 4, closed
121).

## 34. Schema-alignment cycle closure evidence

Baseline `bdcca34`. Schema-alignment cycle for the four class-4 findings reserved to it
(A-114, A-115, A-116, A-122), decided by the owner on 2026-11-19 (schema-alignment cycle
addendum), with five findings registered on the way (A-123..A-127). The owner's reviews
of the plan added, before implementation: ITV-92's `payload_type` change with its single
cause; the exclusive recognition of each `escrow_returned` modality; the link exception
bound to its declared cause, with a second-defect control; the single-cause control,
which `--check-errors` does not provide; the wording of State §5.2 and §8.4; the
distinction between `schema-ref:` and `struct:` evidence; and the exact evidence of
CORE-§4.3.8-18. The owner's double check of the implementation added: the timeout
chronology of ITV-90, INV-243 and INV-245; the link guard over nested escrow records and
over releases whose creation record is not in the corpus; and the explicit MUSTs of State
§7.4. All are part of this cycle.

| Finding | Contract | Vectors | Executed by | Mutation → failing check |
|---|---|---|---|---|
| A-114 | Core §4.3.8 Rule 2 (optional `pii_classification`) and Rule 4 (example validated), §4.3.10.6 (MUST of exact members); State §5.2 (no `message`, MUST on `pii_classification`); seven closed `error-details-<diagnostic>` `$def`s with presence dispatch | ITV-729..735, INV-226..232, INV-234 | validator; R10 (12 emitted details); R24; cycle check | (s1a)–(s1c), (s2), (s3), (s5)–(s7), (s29), (s31), (s32) |
| A-123 | Core §11.1; State §8.4; `localized_description` in the ten closed `$def`s | ITV-736..738, INV-233 | validator; R24 (a) | (s4), (s30), (s35) |
| A-115 | State §7.4 (MUSTs); query-response conditional | ITV-739, ITV-740, INV-235, INV-236 | validator; cycle check | (s8), (s9), (s34), (s44) |
| A-116 | message-schema conditionals (Rule 8, `pii-special-categories`); `set-args` and state-entry exclusion; `art9-legal-basis` | INV-20, INV-22, ITV-555 (no longer `skip_schema`), INV-237, INV-238 | validator; Art. 9(2) parity | (s10)–(s12) |
| A-122 | Assets §4.3 (MUST), §4.3.1–§4.3.4 tables; State §7.1 paragraph; schema constants | ITV-88..92, ITV-95, ITV-586, INV-47 (changed); INV-241..245 | validator; link guard; single-cause control; R14 | (s14)–(s20), (s26), (s28), (s33), (s36), (s39)–(s43) |
| A-124 | Assets §4.3.3 (MUST of exactly one); State §7.1 "never both"; `oneOf`; A-59 exclusive alternatives | INV-245 | validator; A-59 and self-test (e) | (s13), (s18), (s38) |
| A-125 | escrow references; link guard (i) | ITV-89, ITV-90, ITV-91, ITV-586, INV-47 | link guard and self-test | (s21), (s23)–(s25), (s27) |
| A-126 | Assets §4.3, §4.3.1; State §7.1; `payer_agent`, `payee_agent` | ITV-88, ITV-92, INV-239, INV-240 | validator; A-59 | (s22), (s37) |
| A-127 | registered, not corrected | — | — | — |

**A-114 and A-123, details contracts.**
- The seven diagnostics of Core §4.3.10.6 have closed `$def`s carrying exactly their
  rule's members: the indicator `const: true`; `declared` and `sources` for
  `high_risk_missing_oversight`; `axis`, `declared`, `required` and `sources` for
  `obligation_conflict`; the eight members of Rule 4 for `insufficient_retention`; and,
  for `missing_legal_basis`, an OPTIONAL `pii_classification` (`personal` |
  `sensitive`). Each accepts `localized_description` (string).
- The error envelope applies each `$def` when `code` is `invalid_request` and the
  diagnostic member is present, whatever its value; the `$def` then requires it `true`,
  so a `false` value does not escape (R24 (b), all seven). Other `invalid_request`
  details are not captured (R24 (b) control).
- R10 validates every details object the resolver emits for a corpus vector (INV-07,
  ITV-603, ITV-604, ITV-605, ITV-607, ITV-608, ITV-618, ITV-622, INV-62, INV-207,
  INV-208, INV-209: four diagnostics) against its `$def` and in an envelope, and requires
  the variant with the indicator `false` to be rejected by the same function, so a
  stubbed validation is reported. R24 (c) adds the State SET path's Rule 4 details and
  the resolver's output for `unknown_profile`, `classification_escalation` and
  `sensitive_requires_art9_basis`; for the last one the flag `sensitive_entry` is passed
  to the resolver directly.
- A-123: `error-details-conflict-absent`, `-retention-override` and `-retention-fixed`
  were closed without `localized_description`, which Core §11.1 allows in any error. The
  ten closed `$def`s now accept it; R24 (a) checks each with the member as a string
  (accepted), with a non-string value and with an unknown member (both rejected), alone
  and in its envelope. Permitting the member does not validate that the request carried
  `context.locale`, which belongs to the request.
- The Rule 4 and State §5.2 examples are annotated with their `$def`s; no example of
  `spec/` is `no-schema` any more.
- Not executed (declared): the receiver's emission of `sensitive_requires_art9_basis`
  for a SET (`receive(INV-20)` accepts it, the path does not set `sensitive_entry`), and
  the State §5.2 correspondence of `pii_classification` with the entry (the harness State
  path does not emit `missing_legal_basis`). CORE-§4.3.8-18 and STATE-§5.2-06 record them
  as `untested(no-reference-model)`; CORE-§4.3.8-18's `struct:INV-20` proves the
  structural rejection of the combination, R24 the diagnostic's contract.

**A-115, query responses.** A response that contains a tombstone requires `chain_id` and
`chain_seq` on every entry and an integer `next_cursor`, so a record cursor with a
tombstone is rejected (INV-235) and so is a tombstone beside an unchained record
(INV-236). A chained record in an ordinary query stays valid (ITV-740). The limit is
recorded: the response does not carry the query, so a tombstone returned to a query
without `chain_id`, even in a structurally coherent response, and entries of another
chain are a runtime obligation of the serving implementation (State §7.4).

**A-116, SET conditionals.** The message schema applies, on `arsiaprotocol.state/set`,
the Art. 9(2) subset to a declared `legal_basis` of a `sensitive` entry (absence stays
with Rule 2 and State §5.2) and `pii-special-categories` to `payload.args`; `set-args`
and the state entry exclude `pii_special_categories` when the classification is not
`sensitive`. INV-20, INV-22 and ITV-555 are validated structurally without changing their
bytes or signatures; no other vector changes result. `art9-legal-basis` equals the Core
§4.3.6.8 prose and the harness set (parity check).

**A-122, A-124, A-125, A-126, escrow records.**
- Each escrow record documents the message of its transition: creation and timeout
  `arsiaprotocol.assets/transfer-request`, release the `release_trigger`, dispute
  `arsiaprotocol.assets/escrow-dispute`, cancellation `arsiaprotocol.assets/escrow-cancel`.
  The schema fixes the constant types; within `escrow_returned`, the timeout
  (`actual_timeout` without `cancellation_reason`) and the cancellation
  (`cancellation_reason` without `actual_timeout`) are recognised exclusively, and the
  `oneOf` handles "neither" and "both": INV-47 and INV-245 fail only the `oneOf`.
- A timeout record documents the request that created the escrow: ITV-90 carries
  ITV-88's `message_id`, `from_agent`, `to_agent`, `intent`, `payload_type` and
  `payload_hash`, with its own `record_id`. ITV-586 (cancellation) gets its own
  `message_id`. ITV-89 uses `com.example.delivery/confirmed` (the Assets §4.1 example)
  as `release_trigger` and `payload_type`. ITV-95 moves to `transfer-request` and its
  `hash_chain` is recomputed (R14).
- `from_agent`/`to_agent` of the creation record are the envelope agents; `payer_agent`
  and `payee_agent` (REQUIRED) are the request's `payload.args.from_agent`/`to_agent`;
  ITV-88 has participants different from its envelope agents.
- The link guard reads every escrow record (`sub_type` `escrow_*`) at any depth of a
  vector's `data` or `message`, negatives included: the audit-record vectors, the
  `records` of a query response, a record carried in a message. On every record: a
  release's `payload_type` equal to its `release_trigger` (ii), which proves the
  coherence of the record's fields, not the link to an external message; a timeout
  record (`actual_timeout` without `cancellation_reason`) processed at or after its
  `actual_timeout` (iv). When `original_audit_id` resolves by `record_id` to an
  `escrow_created` record of the corpus: same `payment_reference` (i); a timeout's six
  base fields equal to the creation record's (iii). An `original_audit_id` outside the
  corpus is not a problem; only (i) and (iii) depend on it. INV-243, whose declared cause
  is its `payload_type`, is excepted from that one comparison of its own record only; the
  exception requires an invalid vector whose `expected_error` names the field. The
  self-test passes a sound set that includes a release with an unresolved
  `original_audit_id` and a query response carrying a release and a timeout record, and
  reports each divergence in a direct and in a nested record, a release with an
  unresolved `original_audit_id` whose `payload_type` is not its `release_trigger`, a
  timeout processed before it occurred, a second defect (`message_id`) on the excepted
  record, and malformed exceptions.
- ITV-90, INV-243 and INV-245 are processed at their `actual_timeout`
  (2026-05-27T14:00:01.000Z), with `retention_anchor`, `retained_until` (P1827D,
  2031-05-28T14:00:01.000Z) and the resolution's `anchor` and `retained_until` derived
  from it; their schema errors are unchanged.
- The single-cause control requires the exact errors of ITV-92 (`release_agent`), INV-47
  (one `oneOf` whose context is the two presence errors, none on `payload_type`) and the
  seven escrow negatives.

**A-127 (registered, open).** 79 vectors carry 38 undefined `arsiaprotocol.*` payload
types; the inventory by ID, with the three intentional negatives, is in the notes (§8).
No guard and no correction in this cycle.

**Mutations (candidate copy identical to the final tree; 46 of 46 detected).**
- (s1a)–(s1c) the dispatch of `unknown_profile`, `insufficient_retention` and
  `obligation_conflict` removed → R24 (b), the cycle check.
- (s2) `missing_legal_basis` `const: true` replaced by `type: boolean` → INV-227, R24 (b).
- (s3) the `missing_legal_basis` `$def` reopened → INV-234, R24 (a).
- (s4) `localized_description` removed from `error-details-retention-fixed` → ITV-738, R24 (a).
- (s5) `minimum_retained_until` out of the Rule 4 `required` → R24 (b).
- (s6) R10's details validation stubbed → R10 (the indicator-false variant is no longer rejected).
- (s7) dispatch by value (`const: true` in the condition) instead of presence → R24 (b).
- (s8) the tombstone condition removed → INV-235, INV-236; (s9) its `next_cursor`
  restriction removed → INV-235.
- (s10) the `else` of `pii-special-categories` removed → INV-22, INV-237; (s11) the Rule 8
  conditional removed → INV-20; (s12) `art9-legal-basis` without one ground → parity.
- (s13) `oneOf` back to `anyOf` → INV-245 (valid under `anyOf`), A-59.
- (s14)–(s17) the creation, dispute, timeout and cancellation constants removed, one at a
  time → INV-241, INV-242, INV-243, INV-244.
- (s18) the cancellation modality without its `not` → the single-cause control (INV-245
  gains a `payload_type` error); (s19) without its discriminator → the single-cause
  control (INV-47 gains one, which `--check-errors` accepts).
- (s20) ITV-92 without its `payload_type` change → the single-cause control.
- (s21) the link exception widened to the whole record → the link self-test (second defect).
- (s22) `payer_agent` out of the `escrow_created` `required` → INV-239, A-59.
- (s23)–(s25) the link guard without its `payment_reference`, `release_trigger` or
  timeout base-field comparison → the link self-test.
- (s26) ITV-90 with its old `message_id` and (s27) ITV-89 with `PAY-2026-04-0089` → the
  link guard; (s28) ITV-95 with its old `hash_chain` → R14.
- (s29)–(s38) Core §4.3.10.6, §11.1 and Rule 2; State §5.2, §7.1, §7.4 and §8.4;
  Assets §4.3, §4.3.1 and §4.3.3 texts reverted → the cycle check.
- (s39) the link guard reading only the vector's own record, not nested ones → the link
  self-test (nested cases).
- (s40) the release comparison made conditional on the creation record → the link
  self-test (unresolved release).
- (s41) the timeout chronology comparison removed → the link self-test (iv).
- (s42) ITV-90 back to `processed_at`, `retention_anchor` and `retained_until` (and the
  resolution) of the creation instant → the link guard (iv); (s43) the same on INV-243 →
  the link guard (iv).
- (s44) State §7.4 back to the declarative wording (no MUST) → the cycle check.

**Regression.** The campaigns of the earlier cycles ran on the same candidate and
detected every mutation: Assets 30, Routing 22, State 39, maintenance 21, cycle F 18,
main reconciliation 10, port 23, coverage SC4 23. The maintenance campaign checks that the
retention guard prints its record and control counts; its expected text was "130
records, 19 controls" and is now "147 records, 19 controls": this cycle adds 17 audit
records (INV-239..245 and the 10 records nested in ITV-739, ITV-740, INV-235 and
INV-236). The 19 controls are unchanged.

**Counts.** Vectors 987 → 1019 (32 new: ITV-729..740, INV-226..245; 8 changed: ITV-88,
ITV-89, ITV-90, ITV-91, ITV-92, ITV-95, ITV-586, INV-47); runtime-only 211 → 208 (INV-20,
INV-22, ITV-555); crypto blocks 168 (unchanged); consistency checks 152 → 157; harness
checks 888 → 956 (R24 new); RTM 2062 → 2069 rows (MUST + MUST_NOT 1260 → 1265; with
REQUIRED 1461 → 1466); findings register 125 → 130 rows (open 4 → 1, closed 121 → 129).

## 35. Corpus hygiene cycle closure evidence

Baseline `1b2b202`. Corpus hygiene cycle for A-127, the last open finding of the
register, decided by the owner on 2026-11-19 and 2026-11-20 (corpus hygiene cycle
addendum), with four findings registered on the way (A-128..A-131). The owner's reviews
of the plan added, before implementation: the `timestamp` of the expiry record in the
norm, the schema, State §7.1, the fixtures and the harness emission; declared expiry
pairs that a changed `correlation_id` cannot escape; the corrected count of changed
vectors (82, ITV-94 and ITV-584 among them); and the `check:` token for the synthetic
R15 check. All are part of this cycle.

| Finding | Text | Vectors | Execution | Mutations |
|---|---|---|---|---|
| A-127 | — (corpus only) | 82 changed (by-ID table in the notes, §8); ITV-265, ITV-266, ITV-480 declared | hygiene guard and self-test; validator; `--check-crypto` | (h1)–(h8), (h20) |
| A-128 | Actions §3.5 paragraph; State §7.1 row; schema conditional | ITV-93, ITV-94, ITV-584; INV-246..248 | validator; single-cause control; expiry guard and self-test; R15 | (h9)–(h19), (h21), (h23)–(h25) |
| A-129 | — (registered) | — | example-only class of the hygiene guard | (h3) |
| A-130, A-131 | — (registered) | — | — | — |

**A-127, payload types.**
- Inventory: 85 vectors and 44 types once `action_id` (a `payload.type`, Actions §2.1)
  and `details.unsupported_type` are read in `message`, `data` and `test_metadata`,
  nested included; the registration (79, 38) missed ITV-53, ITV-54, ITV-155, ITV-168,
  ITV-169 and ITV-288.
- A defined type only where the semantics, the content, the intent and the conditions
  of the type match (ITV-93, ITV-105, ITV-288, ITV-289); otherwise a non-reserved type
  keeping the area and action. Error responses carry the original request's type: the
  original's where the scenario identifies it (ITV-289, ITV-290), otherwise a fixture
  choice, recorded per vector in the notes. No payload is remodelled; descriptions that
  presented a protocol message change (RTV-01, ATV-06, ITV-288, ITV-94, ITV-584).
- The schema error trees of the 85 vectors (validator, path, schema path, message with
  types normalised, nested contexts) are identical before and after the substitutions.
- Signatures: 21 crypto blocks re-signed with `regen_v2.py --ids` and 13 envelopes
  outside crypto blocks with `--catalog` (ITV-24..27, ITV-289..291, ITV-307, ITV-526,
  ITV-548, ITV-549, INV-43, INV-44; the plan named 5, the corpus has 13); INV-19 rebuilt
  as at baseline, ITV-552's envelope with the first signature byte inverted.
- `payload_type_hygiene_problems` reads every `arsiaprotocol.*` value of the keys
  `type`, `payload_type`, `release_trigger`, `action_id` and `unsupported_type` at any
  depth of `message`, `data` and `test_metadata`. A value is accepted when the registry
  of defined types lists it and its cited section names it (25 types, each checked with
  `spec_section`), when it is one of the two exact example-only names (A-129), or when
  it is a declared intentional negative at its own path, the vector invalid and its
  `expected_error` naming the cause. It is a corpus-hygiene rule, not a normative
  reservation of the namespace. The self-test reports a third undefined type in
  `message`, in nested records and in `test_metadata`, an inexact example-only name, an
  exception at another path, for a valid vector or not naming its cause, and a registry
  entry whose section lacks the type.

**A-128, the expiry record.**
- Actions §3.5: the `approval_expired` record documents the `pending_approval` whose
  deadline was reached (`message_id`, `timestamp`, `from_agent`, `to_agent`, `intent`,
  `payload_type`, `payload_hash` MUST be those of that message; `correlation_id` MUST be
  its `id`; `processed_at` MUST NOT be earlier than the `approval_deadline`). State
  §7.1 lists `timestamp` among the REQUIRED fields of the record; the schema requires it
  and fixes `intent` `pending_approval` and `payload_type`
  `arsiaprotocol.oversight/pending`.
- ITV-93 gains `timestamp` (a fixture choice, the pending's `ts`); ITV-94 documents
  ITV-93's pending, processed at its deadline (15:00, retention re-derived); ITV-584
  documents ITV-582's. INV-246 (`payload_type` of the request), INV-247 (`intent`
  `error`) and INV-248 (no `timestamp`) fail for their cause only.
- `Run.expire` emits `timestamp` = the pending's `ts`; R15 checks that the emitted
  record carries the pending's identity, a field absent on both sides never counting as
  equal.
- `approval_expiry_link_problems` compares each expiry record with its pending, every
  documented field present on both sides and equal. The declared pairs (ITV-94 → ITV-93;
  ITV-584, INV-246, INV-247, INV-248 → ITV-582) fix the pending whatever the
  `correlation_id` says, and require the `correlation_id` to be its `message_id`. Each
  declared expiry fixture is checked directly to carry an `approval_expired` record in
  `data`, before the walker selects records by `event_type`: otherwise a fixture whose
  `event_type` changed would leave the comparison silently while the other records keep
  the dead-guard control satisfied (owner review). The three negatives are excepted from
  their own field only. The self-test reports each divergence, `timestamp` absent on both
  sides, an early expiry, a nested record, a declared expiry fixture with another
  `event_type` or without `data`, a declared pair with only its `correlation_id` changed,
  a second defect on the excepted record and malformed exceptions.

**A-129, A-130, A-131 (registered, open).** Inventories in the register (§4) and the
notes (§8). No correction in this cycle.

**Mutations (candidate copy identical to the final tree; 25 of 25 detected).**
- (h1) the registry without `oversight/pending` and (h2) `arsiaprotocol.error` citing
  Core §11.2 → the hygiene guard.
- (h3) the example-only class accepting a prefix, (h4) the guard without
  `test_metadata`, (h5) without nested lists, (h6) the intentional exception not bound to
  its path → the hygiene self-test.
- (h7) ITV-24 back to `arsiaprotocol.core/ping` and (h8) ITV-307 with the old
  `action_id` only in `test_metadata` → the hygiene guard.
- (h9) the `payload_type` constant and (h10) the `intent` constant removed → INV-246,
  INV-247, the cycle check; (h11) `timestamp` out of the `required` → INV-248, A-59.
- (h12) the expiry guard without `message_id`, (h13) accepting `timestamp` absent on
  both sides, (h14) without the chronology, (h15) with the exception widened, (h16)
  without the declared pairs → the expiry self-test.
- (h17) ITV-94 with only its `correlation_id` changed and (h19) ITV-94 back to 14:00 →
  the expiry guard.
- (h18) `Run.expire` without `timestamp` → R15.
- (h20) INV-19 with the valid signature → `--check-crypto`.
- (h21) the Actions §3.5 paragraph reverted and (h22) RTV-01's description back → the
  cycle check.
- (h23) the expiry guard without the direct check of a declared fixture's `event_type` →
  the expiry self-test; (h24) ITV-94 and (h25) ITV-584 with `event_type` `error` → the
  expiry guard.

**Regression.** The campaigns of the earlier cycles ran on the same candidate and
detected every mutation. The maintenance campaign's expected count text was "147
records, 19 controls" and is now "150 records, 19 controls": the cycle adds the 3
audit records INV-246..248. The 19 controls are unchanged. The schema-alignment
campaign's mutation (s39), which removes the nested walk of the escrow link guard, located
its loop by text that the expiry guard's walker now repeats; it is redirected to the escrow
walker by the line that precedes the loop, which only that walker has.

**Counts.** Vectors 1019 → 1022 (3 new: INV-246..248; 82 changed); runtime-only 208
(unchanged); crypto blocks 168 (unchanged); consistency checks 157 → 163; harness checks
956 → 957; RTM 2069 → 2072 rows (MUST + MUST_NOT 1265 → 1267; with REQUIRED 1466 →
1469); findings register 130 → 134 rows (open 1 → 3, closed 129 → 131).

## 36. Security contracts cycle closure evidence

Baseline of the exploration `55ba397`; effective parent `fdbcc71` (the registration of the
audit findings). First of three cycles for A-132..A-143, decided by the owner on 2026-11-20
and planned with four owner reviews (security contracts cycle addendum). No key material was
printed.

| Finding | Contract | Vectors | Executed by | Mutation → failing check |
|---|---|---|---|---|
| A-132 | Core §2.2, §4.3.2, §10.2, §10.3, §10.4, §13.2.2 | ITV-741 | R25 (reference store); cycle check | (s1)–(s18), (s45), (s46), (s55)–(s60), (s62), (s63) |
| A-133 | Identity §3.3, §7.7, §9.2; Core §6.3 | — (synthetic requests) | R20 (k) `token_presentation`; cycle check | (s19)–(s24) |
| A-136 | Core §5.3; `arsia-message.schema.json` error conditional; `keypairs.json` `encryption_keypairs` | ITV-742; INV-249, INV-250, INV-251, INV-252, INV-253, INV-254; controls ITV-155, ITV-741 | validator; R26; matrix guard; encryption key guard and self-test; single-cause control | (s25)–(s39), (s50)–(s54) |
| A-139 | Core §5.3.1; audit-record schema description | — | cycle check and self-test | (s40)–(s42) |
| A-135 | SECURITY.md | — | cycle check and self-test | (s43), (s44), (s61) |
| SPDX scope (declared deviation) | `repository_text_problems` | — | scope self-test | (s47)–(s49) |

**A-132.** The association is kept at least until the latest of `idempotency.expires_at`,
the end of the message's acceptance window and the determined outcome of the operation. R25
runs a reference store in the §10.3 order on ITV-741 (acceptable for 30 s, idempotency
instant at 1 s): a repetition at second 2 returns the stored response; the exact instant
`expires_at` + tolerance is still deduplicated and one millisecond later the envelope is
rejected as expired; a profile tolerance moves the instant; a message without `expires_at`
is kept until the server's `ts` limit, or without a finite instant when it sets none. A
message arriving between the lookup and the write of another cannot obtain the reservation
(a deterministic control) and of 32 concurrent messages one executes. A reservation without
a stored response answers `conflict`; an undetermined one is never released; an expired
envelope gets `invalid_request` and releases nothing; an error after an effect is stored; a
confirmed effect without a response stays reserved after the window; a read's success stays
stored; the safe release needs every condition, and an error code alone is not one; discard
is possible only after the window with the response stored; the header-only key is used only
by choice.

For an encrypted payload the received envelope holds a JWE string and gives no `payload.type`.
Core §10.2 item 1 counts the §5.3 decryption procedure among the verifications that precede
the reservation and takes the scope's type from the decrypted payload; Core §5.3 step 3 points
back to it. The sentence defines a term of the existing reservation requirement and adds no
RTM row; CORE-§10.2-02 carries it and its evidence. R26 runs the two procedures together on
synthetic encrypted requests built from INV-251's envelope (plaintext type corrected, an
idempotency key added, signed again): the first delivery reserves the key under the decrypted
type and a repetition in progress gets `conflict`; the repetition and another JWE of the same
plaintext reach the same association and get the stored response; the same key under another
decrypted type is another scope; a message rejected at the signature, at the decryption or at
the decrypted view reserves nothing, on an empty store and beside an existing association; the
store refuses to scope an encrypted envelope without the decrypted type.

The release condition is worded as Core §10.2 item 2 states it — the server has established
that no effect occurred, with the other three conditions — in the migration guide, the
changelog and CORE-§10.2-08, which read as permitting a release on an unknown outcome;
SECURITY.md names the safe release as the exception to its retention promise. The cycle check
holds the four texts.

**A-133.** `token_presentation` precedes `dpop_verify`: an unknown token and a malformed
`cnf` are `unauthorized` under either scheme; a bound token under `Bearer` or without a
`DPoP` header is `unauthorized`; a token without `cnf.jkt` under `DPoP` is `unauthorized`; a
bound token with a proof goes to the proof verification; an authenticated token without `cnf`
under `Bearer` takes the bearer path. The step receives authenticated token facts as trusted
context and verifies the presentation scheme only. The cycle check accepts the SHOULD of
adopting DPoP and reports a SHOULD on verifying a proof.

**A-136.** The error conditional is `intent` `error` and the message not encrypted; the
matrix guard runs `encrypted` absent, `false` and `true` against an object and a string
payload, and a request to show that the rule is of errors only. R26 runs the decryption
procedure in order — signature over the received envelope, protected header against
`security.enc_alg` and `enc_method`, authenticated decryption, strict parsing, the decrypted
view against the message schema, `payload_hash` over the JWE string:
- ITV-742 is accepted and decrypts to its declared plaintext;
- INV-249 (ciphertext altered) and INV-253 (header mismatch) are `unauthorized` at step 2,
  INV-250 (no `error`), INV-251 (undefined State type) and INV-254 (duplicate member name)
  `invalid_request` at step 3, each with a signature that verifies and a single cause;
- with only INV-251's plaintext type corrected and the JWE and signature rebuilt, the request
  is accepted;
- an invalid outer signature stops at step 1 and the decryption is not attempted;
- with only the JWE tag altered and the envelope signed again, decryption fails authentication;
- the JWE format is read strictly (RFC 7516 §5.2): five segments, each base64url without
  padding, foreign characters or an unused bit set, and the JWE Encrypted Key segment empty as
  written, not as decoded. Nine variants of ITV-742's JWE, each signed again, are
  `unauthorized` at step 2 for the format — among them a second segment that a lenient decoder
  reads as empty, a line break inside the ciphertext and a tag with an unused bit set, which
  decodes to the same octets;
- a protected header with a `crit` parameter is `unauthorized` at step 2 (the reference
  understands no extension, RFC 7516 §4.1.13); the same JWE without it is accepted.

The decoder reproduces the shared secret of RFC 8037 Appendix A.6 and the derived key of
RFC 7518 Appendix C with the appendix's own parameters (A128GCM, 128 bits, apu and apv); the
fixtures use A256GCM, 256 bits and no apu or apv — two cases of one function. An independent
JOSE implementation decrypts the corpus JWEs (notes, §8). The X25519 key is published in
`encryption_keypairs`, declared by `use`, `kty` and `crv`; the 54 signature entries, their
digests and every signature path are unchanged, and `_key_type` classifies signature material
only.

**A-139, A-135.** Core §5.3.1 no longer relies on signed audit records nor presents matching
hashes as proof of transmission or receipt. SECURITY.md sentences changed, each with its
source: signing input (Core §5.1); twelve adversaries, with 2.7–2.12 added (Core §13.1 items
7–12); idempotency retention (Core §10.2); proof required by the token's binding (Identity
§3.3; Core §6.3); residency without proof of physical location (Routing §5; Core §13.1 items
7 and 11); the chain required at Compliance and Full and what it does not detect, and audit
hashes not exempt by themselves (Core §12; State §7.2); messages signed, records chained
(Actions §3.5; State §7.2); Level 2 with the audit chain and Level 3 with the in-repository
tooling (Core §12.2, §12.3); RTM row count; `compliance.retention` and storage limitation
(Core §13.3).

**Declared deviations.** INV-251 is an encrypted request with an undefined State type instead
of an encrypted `pending_approval`, which the oversight guards would have required to carry a
reference request; those guards are unchanged and the hygiene guard declares the plaintext at
`test_metadata/plaintext/type` for that vector only. The SPDX guard checks tracked files and
new files that are not ignored, and every file when there is no Git metadata; two local
ignored planning documents had turned it red. Core §10.3's retained items on the HTTP status
and the stored envelope are sub-items of case 3.

**Mutations (candidate copy identical to the final tree; 63 of 63 detected).** A
mutation counts only when the expected check fails; a traceback is an error, not a detection.
- (s1)–(s5) the retention reduced to `idempotency.expires_at`, without the tolerance, with
  the exact instant excluded (rejection and discard), and `ts` + tolerance in place of no
  limit → R25.
- (s6)–(s18) reservation not atomic; in-progress duplicate executed; undetermined
  reservation released; re-execution, early release and discard by deadline with the effect
  confirmed and no response; an error after an effect not stored; release on an error code;
  a read's success released; an expired envelope answered from the store; a rejected message
  releasing; a failed verification reserving; the header-only key mandatory → R25.
- (s19)–(s22) a bound token under Bearer, an unbound one under DPoP, an unknown token and a
  malformed `cnf` accepted → R20; (s23), (s24) Identity §7.7 back to a SHOULD on verifying and
  the binding rule removed → the cycle check.
- (s25)–(s27) the error conditional reverted, without `intent`, and removed → ITV-742,
  INV-252, the cycle check and the matrix guard.
- (s28)–(s36) the view keeping `encrypted` true or not validated; plaintext parsed loosely;
  header not compared; tag not verified; both error codes exchanged; signature not verified
  first; Concat KDF with another AlgorithmID → R26.
- (s37), (s38) the X25519 key among the signature keys and recognised by length → the catalog
  guards; (s39) INV-251's declaration removed → the hygiene guard.
- (s40)–(s46) Core §5.3.1, the schema description, SECURITY.md, Core §10.4 and §10.3 back →
  the cycle check.
- (s47)–(s49) the SPDX scope checking ignored files, only tracked files, or nothing without
  Git metadata → its self-test.
- (s50)–(s54) JWE segments decoded leniently; an unused bit accepted; the JWE Encrypted Key
  segment checked after a lenient decoding, or not checked; `crit` ignored → R26.
- (s55)–(s58) the scope of an encrypted message a constant or the JWE string; the key reserved
  before the decryption procedure ends; the store scoping an encrypted envelope without the
  decrypted type → R26.
- (s59)–(s63) the migration guide and CORE-§10.2-08 back to the ambiguous release condition;
  SECURITY.md without the safe release; Core §10.2 and §5.3 without the scope of an encrypted
  message → the cycle check.

**Regression.** The temporary directory holding the campaign scripts was lost during the
cycle. The ten earlier campaigns were rebuilt from the session record by replaying, in order,
the operations that created and changed each script, in a durable directory outside the
repository; every mutation identifier of every rebuilt script is cited in its evidence
section (§26–§35), by itself or within a cited range. All ten ran on the same candidate with
a clean base and every mutation detected. One mutation was redirected: (p) of the coverage
campaign (§26), an `untested` disposition without a code, pointed at CORE-§2.2-09, which this
cycle gave R25 evidence; it now points at CORE-§4.3.2-03, with the same mutation and the same
failing check. The maintenance campaign's count text is unchanged
at "150 records, 19 controls": the cycle adds no audit record.

**Counts.** Vectors 1022 → 1030 (ITV-741, ITV-742, INV-249..254: 514 schema-valid, 284
expected-invalid, 213 runtime-only, 19 raw); crypto blocks 168 → 170 (158 signatures
verified, 9 negatives, 3 absent); five more signatures outside crypto blocks (INV-249,
INV-250, INV-251, INV-253, INV-254); signature keypairs 54 (unchanged), encryption keypairs
0 → 1; consistency checks 163 → 169; harness checks 957 → 1015; RTM 2072 → 2083 rows
(MUST + MUST_NOT 1267 → 1278; with REQUIRED 1469 → 1480); findings register 146 rows (open
15 → 10, closed 131 → 136).

## 37. Validation and parsing cycle closure evidence

Effective parent `bbba0b1`. Second of three cycles for A-132..A-143; decisions of the owner
on 2026-11-25, in the planning questions and three plan reviews (validation and parsing cycle
addendum). No key material was printed.

| Finding | Contract | Vectors | Executed by | Mutation → failing check |
|---|---|---|---|---|
| A-134, patterns | Core §2.3; every schema and prose pattern; `arsia_validator`; whole-value grammars of the tools | INV-255, INV-256, INV-257, INV-258 | validator; R27; cycle check; reference-path guard and self-test; single-cause guard | (v1)–(v9), (v40), (v48), (v51), (v52) |
| A-134, timestamps | Core §4.1.3; `arsia-common.schema.json` `rfc3339-ms-utc` | ITV-743; INV-259..INV-265 | validator; R27; cycle check; single-cause guard | (v10)–(v21), (v41), (v42), (v49) |
| A-134, scope | Core §6.1, §6.4 step 4; `oauth-scope` and the three contracts of `arsia-jwt-claims.schema.json` | ITV-744; INV-266..INV-273 | validator; R27; cycle check | (v22)–(v26), (v45)–(v47), (v53) |
| A-137 | Core §5.2 step 2; `strict_json`; the receiving entries | CTV-17, CTV-18, CTV-19, CTV-20 | validator (raw); R28; cycle check | (v27)–(v39), (v43), (v44), (v50) |

**Patterns.** Core §2.3 declares the ECMA-262 dialect; `\d` became `[0-9]` in the 13 distinct
schema patterns that used it (34 uses), in the two of the vector meta-schema and in the
specification patterns of Core, State, Actions and Assets. The tools match `pattern` through a
translation of that dialect (`$` the end of the value, `.` without the ECMA line terminators),
used as a search, and refuse the constructs whose meaning differs between dialects. The escapes
the translation accepts are a closed list — a backslash before an ECMA-262 syntax character or
`/`, before `-` inside a class, and the two-digit hexadecimal escape; an escape only Python
reads (`\A`, `\Z`), an empty class (`[]`, `[^]`), a possessive quantifier and a pattern Python
cannot compile are refused as unsupported, and a schema carrying one rejects the value with a
controlled diagnostic instead of an error of the regular expression library. Every
validator of the scripts is built by `arsia_validator`, and every registry holds copies of the
schemas without `$schema`: the same message is rejected by the same field and validator on the
schema itself, through a `$ref` to its root and from another document — an `id` with a final
line break (pattern), a `ts` on a day that does not exist (format), an undefined State type
(the prefix search of the State conditional) — while the unchanged messages stay valid. The
guard's self-test shows that a registry keeping `$schema` loses the two indirect paths. A
malformed version (`"2.0\n"`, `"2.1"` followed by U+0661, a leading space, leading zeros) stays
in the exact procedure and is rejected with an unknown member; `"2.7"` still selects the
compatibility procedure. Whole-value grammars of the tools use a full match with ASCII digits:
`_VERSION_RE`, `_ERROR_CODE_RE`, the compatibility pattern, `DUR_RE`, `CONCRETE`, `WILDCARD`,
`AMOUNT_RE`, `CURRENCY_CODE_RE`, `UNIT_RE`, `NQCHAR_NONCE`, `ATTESTATION_HEADER_ALPHABET`,
`VECTOR_ID`, `B64URL_NOPAD`, `RESERVED_PAYLOAD_TYPE`; position parsers and readers of repository
text are unchanged.

**Timestamps.** The `$def` pattern limits the month, day, hour, minute and second and excludes
the year 0000; `format: date-time` states the calendar rule and the tools assert it with the
general RFC 3339 meaning (any fraction, an offset, a day that exists; the second 60 only at a
leap second the IERS announced, after the offset is applied). The copy of the pattern on
`retention_anchor` became a `$ref`. Controls with stated expectations:

| Value | General format | ARSIA `$def` |
|---|---|---|
| `2000-02-29T00:00:00.000Z` | valid | valid |
| `2026-02-30T00:00:00.000Z`, `2100-02-29T00:00:00.000Z` | invalid | invalid (format only) |
| month 13, hour 24 | invalid | invalid (pattern and format) |
| `0000-01-01T00:00:00.000Z` | valid | invalid |
| an offset, a fraction of four digits | valid | invalid |
| `1990-12-31T23:59:60Z`, `1990-12-31T15:59:60-08:00` | valid | invalid |
| `1990-12-31T12:00:60Z`, `1991-12-31T23:59:60Z` | invalid | invalid |

Every value the `$def` accepts is read by the harness time arithmetic (years 0001 and 9999
included).

**Scope.** One `$def` carries the grammar for the claims, the token request and the token
response. `granted_scope` validates the whole value and only then splits at single spaces. At
the receiver, an `approval_decision` built for a pending approval and schema-valid is delivered
with a token valid in every other respect, each case on a pending flow of its own: with a
single space the decision is admitted, recorded as `approval_decision`, and the flow leaves the
pending state; with a tab it is `unauthorized` before the comparison of capabilities (the
comparison is not called), recorded as `decision_rejected`, and the flow stays pending; a
well-formed scope without the capability reaches the comparison, is `forbidden`, and the flow
stays pending.

**Nesting and the parser.** `strict_json` counts the depth iteratively before parsing — each
open object or array one level, the root container level 1, nothing inside a string — and
rejects the excess at step 2. With the limit at 32 a mixed document of depth 32 passes, the same
document one level deeper is rejected, and it passes under a limit of 64; 100000 nested arrays
are rejected by the depth check with no interpreter exception; a limit below 32 is refused as a
configuration. Integers of any length are converted in chunks no longer than the lowest digit
limit the interpreter can be configured with (`sys.int_info.str_digits_check_threshold`, 640)
and the interpreter-wide digit limit is never touched (a spy records no call). CTV-16 runs in
a process of its own with that limit set to 640: the document is accepted, the 5000-digit
member is the integer its digits denote, and the limit is the same before and after. The excess at each receiving entry:

| Entry | Depth 33 | Depth 32 |
|---|---|---|
| Envelope (raw vectors) | rejected at step 2 (`invalid_request`) | accepted |
| Relay attestation header (R22) | step 2 of the header decoding (`unauthorized`) | parsed, fails at the attestation schema |
| JWE protected header | `unauthorized`, step 2, cause format | accepted |
| JWE plaintext, authenticated | `invalid_request`, step 3, cause parse | accepted |
| Access token | rejected before its claims are validated | accepted |
| DPoP proof | check 2 (`unauthorized`) | passes check 2 |

**Single cause.** Each negative of the cycle fails in one field with exactly its declared set of
(validator, instance path); month 13 and hour 24 fail the pattern and the format of that field,
the two calendar-only values fail the format alone. For the 1030 earlier vectors, the procedure
and the validator, instance path and sub-errors of every error are the same before and after the
cycle (the message text is not compared: it changes where `\d` became `[0-9]`).

**Mutations (candidate copy identical to the final tree; 53 of 53 detected).** A
mutation counts only when the expected check fails; a traceback is an error, not a detection.
- (v1)–(v9) the registry keeping `$schema`; the matcher back to Python's search; `$` not
  translated; every pattern a full match; `\d` back in a schema; the version selected by a
  prefix match; the compatibility pattern with `\d`; a duration grammar matched by prefix; a
  validator built outside the factory → the reference-path guard, the validator, R27, the cycle
  check.
- (v10)–(v21) the timestamp pattern without ranges, with the year 0000, with the second 60; the
  format removed; the calendar accepting 30 February, 2100 as a leap year, 2000 as a common year;
  the general format refusing an offset, taking the second 60 in any minute or at any end of
  month (the 1991 control), or ignoring the offset; INV-262 with a second defect → the validator,
  R27, the cycle check, the single-cause guard.
- (v22)–(v26) the scope grammar loosened; a contract with its own pattern; the split before the
  validation; a malformed scope reaching the comparison; a well-formed scope without the
  capability answered `unauthorized` → the validator, the cycle check, R27.
- (v27)–(v39) the depth check removed; the root not counted; brackets of strings counted; an
  escaped quote ending the string; the limit at 33; the interpreter's error escaping; the digit
  limit changed; the excess at step 3; the token, the proof and the JWE header parsed without
  the limit; a deep plaintext reported as a defect of the view, or as `unauthorized` → the raw
  vectors, R28, the cycle check.
- (v40)–(v49) each new normative sentence weakened; a prose pattern back to `\d`; a prose
  timestamp pattern differing from the `$def` → the cycle check.
- (v50)–(v53), owner review of 2026-11-25: integer chunks above the lowest configurable digit
  limit; the escapes back to an exclusion list; a compilation error of the library escaping
  the translation; a decision rejected for its token still taking the flow out of the pending
  state → R28, R27.

**Regression.** The eleven earlier campaigns ran on the same candidate, each with a clean base
and every mutation detected. Three of their mutations aimed at text or behaviour this cycle
changed and were redirected: security (s44) now restores the previous row count from the
current one; state (s31) removes the end anchor together with `maxLength`, since `maxLength`
alone no longer decides a final line break under the declared dialect (the keyword stays in
the schema, by decision of the owner); coverage (r) expects the 5000-digit integer check only,
since a document 100000 levels deep is now rejected by the depth check before any exception.

**Counts.** Vectors 1030 → 1055 (ITV-743, ITV-744, INV-255..273, CTV-17..20: 516 schema-valid,
303 expected-invalid, 213 runtime-only, 23 raw); crypto blocks 170 (unchanged); one more
signature outside a crypto block (INV-265); keypairs unchanged; consistency checks 169 → 174;
harness checks 1015 → 1046; RTM 2083 → 2090 rows (MUST + MUST_NOT 1278 → 1284; with REQUIRED
1480 → 1486); findings register 146 rows (open 10 → 8, closed 136 → 138).
