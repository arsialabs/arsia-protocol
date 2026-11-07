<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Draft-02 Remediation Ledger — Open Notes

Part of the [Draft-02 remediation ledger](draft-02-remediation-ledger.md). This file
holds the Open notes register (§8); its section number is that of the main ledger.
Notes are observations, not a register with counts.

## 8. Open notes

The regulatory Open notes (C2, C2.1) are in the [regulatory file][reg8].

- **Vectors vs MAY behaviour:** ITV-545 is expected-invalid on a MAY (Core
  §4.1.3). The posture is to be defined in the vector cycle (DR-0.3).
  Resolved in VC: such vectors declare `posture` (verbatim granting text, guarded);
  ITV-408, ITV-440 and ITV-545 (Core §8.3 MAY) and ITV-416 (strict mode).
- **A-34 proxy:** exact for the current corpus (INV-18, INV-19). An explicit
  crypto field is the definitive fix (vector/meta-schema cycle). DR-5: the chain
  negativity of ITV-597..599 is likewise carried outside the vector format (the
  tampered-chain map in `check_consistency.py`) until that explicit field exists.
  Resolved in VC for signatures: `crypto.expect_signature` (valid/invalid/absent)
  replaces the proxy; the chain negativity of ITV-597..599 stays in the tampered-chain
  map.
- **ITV-546:** its coverage gap is mapped to A-62.
- **A-35:** resolved in C3b — the checker and the generator refuse to run without
  rfc8785.
- **CI:** `validate-vectors` has been red by design since C0.5, and stays red
  until the vector cycle. Since LM2, CLAUDE.md states this next to the validation
  command (32 runtime-only vectors fail by design).
  Resolved in VC: the 32 are repaired, `validate_vectors.py` reports 0 failures, and the
  CLAUDE.md caveat is removed.
- **Out-of-date docs:** `docs/draft-02-skip-classification.md` and
  `scripts/README.md` are out of date on the ITV-545/546 reasons, skip
  semantics and crypto output (follow-up under A-65).
  Resolved in VC: both documents rewritten (coverage vocabulary; skip, version and
  crypto behaviour).
- **Missing SPDX headers:** `docs/auditoria-spec-draft-01.md` and
  `docs/spec-audit-draft-01.md` lack the CC-BY-SA-4.0 header (follow-up; not
  fixed in C1).
  Resolved in cycle F: both files, and CLAUDE.md, carry the CC-BY-SA-4.0 header; LICENSE.md is
  exempt as the licensing notice itself; guard `repository_text_problems`.
- **Stale published counts (C2):** the root `README.md`, `CLAUDE.md` and files
  in `docs/` still state 649 vectors and 1109 MUST+MUST_NOT. After C2 the
  figures are 653 vectors and 1903 RTM rows / 1114 MUST+MUST_NOT. Only
  `test-vectors/README.md` was updated in C2, where the `ITV-` prefix count
  had been 578 against an actual 579 before C2. After C3a the figures are 666
  vectors and 1903 / 1114 (unchanged); `test-vectors/README.md` was updated again.
  Ledger maintenance (LM): the current-state documents (`README.md`, `CLAUDE.md`,
  `docs/FAQ.md`, `docs/getting-started.md`) now carry the tool-computed figures; dated
  records keep the figures they measured.
- **Breach-notification schema coverage (C2 observation):** no schema-ref
  vector exercises `arsia-breach-notification.schema.json`. ITV-556/557 are
  message-only, and the envelope schema does not validate the payload against
  it. C2 validated both payloads against the breach schema by hand.
  Resolved in cycle F (A-107): ITV-713..716 and INV-178..206 execute the payload schema;
  STATE-§5.7-02 cites them. Delivery and correlation of notifications stay untested.
- **`oversight_timeout` suspended (C3a, A-3):** Core §4.3.6.5 requires logging
  it, but it is one of the three `required_within_24h` definitions that DR-2
  replaces with one mechanism. It is added (or dropped) in the DR-2 cycle.
- **`ict_incident` audit extension undefined (C3a observation):** State §7.1 and
  Assets §6.2.3 promise incident classification fields in the `ict_incident`
  record, but no field is defined in prose or schema. It is an explicit exception
  of the A-59 guard.
- **`jwks_fetched_at` (C3a observation):** State §7.1 makes it REQUIRED for any
  signed compliance-relevant message; the schema cannot express that condition
  and leaves it optional. It is an explicit exception of the A-59 guard and is
  tracked by A-58.
  Limit recorded in cycle F: the condition is defined (State §7.1); the schema cannot express
  it; harness R15 executes the `verified_kid` / `jwks_fetched_at` evidence on its records.
- **Rollback audit fields undefined in schema (C3a observation):** Actions §4.2
  ("Rollback Audit") requires the original action's `message_id` and
  `action_id`, the rollback request's `message_id`, a timestamp and full/partial
  status. Neither the schema nor the State §7.1 table defines these fields
  (candidate finding).
  Resolved in C3b (`59addd5`): Actions §4.2 maps each item to a field
  (`original_message_id`, `action_id`, the base `message_id` and `processed_at`,
  `partial_rollback`). `arsia-audit-record` defines the three extension fields and
  requires them when `event_type` is `rollback`.
- **Plain `asset_transfer` records (C3a observation):** the former §7.1 table
  claimed `payment_reference`, `amount` and `original_audit_id` for
  non-escrow transfers and reversals. No originating prose or schema rule
  supports that, so the claim was removed from the table. The audit content of
  plain `asset_transfer` records is undefined (candidate finding).
- **`pii_special_categories` in `state_set` records (C3a observation):** it is
  required by the schema and the §7.1 table, but the originating operation
  prose (State §3.1.2 table, §8.3 rule 3) does not list it; §2.1.11 concerns
  Art. 30 records.
- **`relay_id` naming (C3a observation):** relay receipt and error payloads
  (Routing §2.3) carry `relay_id`, while the attestation and the audit record
  use `attestation_id` for the same per-relay UUID.
- **ITV-94 correlation semantics (C3a observation):** Actions §3.5 Record 3 sets
  `correlation_id` to the pending_approval id; ITV-94 uses the original request
  id. The schema cannot check this.
- **CHECK-04 field list (C3a observation):** Identity CHECK-04 presents its list
  as "the fields defined in ArsiaAuditRecord", but it omits the schema-required
  `retention_source`.
  Resolved in C3b (`59addd5`): the CHECK-04 list includes `retention_source`.
- **Canonical pending_approval field set not enforced (C3a observation):** Assets
  §5.2 requires "exactly the canonical field set" of Actions §3.2, but the
  `pending-approval-args` schema does not close its properties.
  Resolved in DR-1/DR-2 (`e5e06a5`): `$defs/pending-approval-args` has
  `additionalProperties: false`, unchanged since.
- **Extension fields without RTM rows (C3a observation):** the per-event-type
  extension table has no dedicated RTM rows (A-64 domain).
- **ITV-401 pre-existing defect (C3a):** the vector also lacked `correlation_id`,
  so it was invalid for two causes. It was corrected when the vector was
  repurposed under Rule 4.

- **Findings register has no description column (C2.1):** defect descriptions live in
  the C0 audit report. For A-70 to A-73 the currency-pass text is placed under
  "Closure evidence obtained", as agreed with the owner. Adding a description column,
  and possibly moving the regulatory register to its own file, is a separate
  ledger-maintenance step.
  Resolved in LM: Description column added; the regulatory and vector registers
  moved to their own files.
- **ITV-99 `payload_type` (C3b):** `arsiaprotocol.actions/rollback` does not follow
  the Actions §4.2 `{action_id}/rollback` form (vector cycle).
  Resolved in VC: ITV-99 and INV-50 use `com.example.notes/create/rollback`.
- **Reversal records (C3b, A-75):** Assets §3.3.2 requires the reversal record to
  reference the original `audit_id` and `payment_reference`, but no schema
  discriminator identifies reversal records; adding one is a design choice.
- **Routing §2.3.3 (C3b, A-16):** "recipient error" among the cannot-forward causes
  is read as a failure to obtain a recipient envelope, per the A-16 disposition.
- **Stale counts outside scope (C3b):** CLAUDE.md still cites 1903 / 1109 RTM rows;
  the repository now has 1909 / 1117 (documentation outside C3b scope). Resolved in LM.
- **A-59 guard (C3b):** the guard now also compares State §7.1 base-field
  requiredness with the schema; `AUDIT_BASE_EXCEPTIONS` holds A-81.
- **Link coverage (LM):** `check_links.py` checks § references in `spec/` and the
  schema/profile JSON only; it does not read `docs/` or relative Markdown links. The
  ledger files were checked by a one-off script (tooling program).
- **Other stale CLAUDE.md figures (LM):** "91 repo invariants" and "R1-R13" are out
  of date; they are not vector or RTM totals, so LM left them. Resolved in LM2:
  CLAUDE.md states 98 repo invariants and R1-R14.
- **Propagation impact (DR-5):** implementations must emit the chain fields at
  Compliance and Full, serve chain queries in State §7.4 (`chain_id`,
  `after_chain_seq`, `next_cursor` as record_id or chain_seq), verify chains in
  CHECK-04, and pick up the new tombstone schema in the re-sync.
- **Query-response schema (DR-5):** it admits tombstones in any response; State §7.4
  allows them only in `chain_id` queries (schema more permissive than prose).
- **Published counts after DR-5:** 32 schemas (incl. meta), 679 vectors
  (438/147/94), RTM 1922 / 1130. README.md, CLAUDE.md (also "R1-R13", no R14) and
  docs are left for the maintenance step. Resolved in LM2: `README.md`, `CLAUDE.md`,
  `docs/FAQ.md` and `docs/getting-started.md` carry 32 schemas, 679 vectors
  (438/147/94) and RTM 1924 / 1132 (after the DR-5 follow-up).
- **Generated overview (LM2):** `docs/generated/arsia-protocol-overview.md` is a
  dated snapshot (commit `c4bc506`, extraction 2026-08-06) that still states 649
  vectors and RTM 1903 / 1109; it says to regenerate rather than hand-edit, so LM2
  left it (regeneration is a separate step).
- **Unchained audit-record vectors (DR-5):** older audit-record vectors carry no
  chain fields; the level mandate is enforced by harness R14 (f) and CHECK-04.
- **ITV-18/19 and post-execution review (DR-3/DR-4):** they stay structurally valid;
  accepting `required_within_24h` or `required_post_execution` in a resolution is not
  evidence that post-execution review works — that mechanism is DR-2.
- **Resolved is not fulfilled (DR-3/DR-4):** `obligation_resolution` records which
  obligations applied; fulfilment evidence comes from the flows that carry them out.
- **Resolver-contract tests (DR-3/DR-4):** ITV-609, ITV-617 and ITV-618 compose
  executor-class requirements to test the resolver's contract; they do not claim the
  executor integration, which is DR-1.
- **Removed RTM rows (DR-3/DR-4):** IDENT-§4.2-02 and -03 (warning and
  `classification_mismatch` rejection) and STATE-§6.2-04 (profile applicable only to
  high-risk agents) traced requirements that the cycle removed.
- **CHECK-05 (DR-3/DR-4):** the new check states no RFC 2119 keyword; it is traced
  through IDENT-§7.3-17 (all checks pass) and IDENT-§7.6-11, and exercised by the
  vectors carrying the authenticated context.
- **Stale CORE-§4.3.7-02/-03 (observed in DR-3/DR-4, not fixed):** the rows describe a
  retention clamp and an override warning that Core §4.3.7 forbids ("MUST NOT silently
  raise"); they predate the cycle and are left for the RTM pass (A-64 domain).
  Resolved in coverage SC4: both retired; successor CORE-§4.3.7-04 (MUST NOT silently
  raise) and the Rule 4 rows; the warning obligation no longer exists.
- **Stale profiles/README.md retention column (observed in DR-3/DR-4, not fixed):** it
  states day counts (e.g. 180 days for EU-AI-ACT-HIGH-RISK, 730 for DSA-VLOP) that differ
  from the catalog (P6M, P1096D); out of the cycle's scope.
  Resolved in cycle F (A-101): the column is the catalog's `retention_minimum`; guarded.
- **getting-started breakdown (DR-3/DR-4):** the vector breakdown "430 / 145 / 94" missed
  by LM2 now carries the tool-computed figures.
- **Published counts after DR-3/DR-4:** 33 schemas (incl. meta), 717 vectors
  (441/157/119), RTM 1940 / 1147, 110 consistency checks; README.md, CLAUDE.md,
  docs/FAQ.md, docs/getting-started.md and test-vectors/README.md updated. The generated
  overview stays a dated snapshot.
- **ITV-18/19 after DR-1/DR-2:** their descriptions now state the post-execution review
  the modes open (Actions §3.9); the mechanism is exercised by ITV-645..661.
- **ACTV-01 retention (observed in DR-1/DR-2, not fixed):** the response declares
  `retention: "P180D"` under EU-AI-ACT-HIGH-RISK (floor P6M) and would be rejected by
  the resolver; CTV-02 and ITV-338, which had the same defect and belong to the DR-1/DR-2
  migration, were corrected by owner exception. Left for the vector cycle.
  Resolved in VC: ACTV-01 declares P6M and is re-signed; a guard requires every valid
  message vector with compliance to be accepted by the reference resolver.
- **Non-conformant action_id in CTV-08 and ITV-86 (observed in DR-1/DR-2, not fixed):**
  their `pending_approval` args carry `ACT-2026-03-24-001` and `ACT-2026-04-27-001`,
  which are not valid `action_id` values; the migration guard exempts only that pattern
  error for their reference descriptors (`ACTION_ID_EXEMPT`). Left for the vector cycle.
  Resolved in VC: CTV-08 uses `arsiaprotocol.compliance/check` (CTV-02's payload type)
  and ITV-86 `com.acme.payments/transfer`; `ACTION_ID_EXEMPT` is removed.
- **Shared policy_version with incompatible lists (observed in DR-1/DR-2, not fixed):**
  ITV-03 (gateway `agent:arsialabs.demo.compliance-checker`) and the payload-only
  decisions ITV-130, ITV-38 and INV-61 all name `arsialabs-2026-q2`, but
  `arsiaprotocol.state.write` is oversight-required in ITV-03 and freely allowed in
  ITV-130. Each carries its own reference policy, which reproduces its lists; Identity
  §8.1 forbids one gateway applying two policies under one version, and the
  payload-only decisions name no gateway. The vector cycle should give them distinct
  versions.
  Resolved in VC: the trio and INV-78 use `arsialabs-2026-q2b` with
  `test_metadata.gateway` `agent:arsialabs.demo.gateway` (the `iss` of their tokens); the
  guard is keyed by (gateway, `policy_version`), as Identity §8.1 states.
- **Stale CORE-§4.4.7-01..04 (observed in DR-1/DR-2, not fixed):** the rows still trace
  the Draft-01 "warn and process" rule that Core §4.4.7 replaced with a hard rejection;
  they predate the cycle (A-64 domain).
  Resolved in coverage SC4: CORE-§4.4.7-01 rewritten (MUST, exactly one content field);
  -02, -03, -04 retired; CORE-§4.4.7-05 added (more than one content field, or none,
  rejected with `invalid_request`).
- **Removed RTM rows (DR-1/DR-2):** CORE-§4.3.6.5-01, -03, -04, -05 and -06 (autonomous
  execution, the 24 h review MUST and `oversight_timeout`), ACT-§2.1-22 and ACT-§3.7-04
  (descriptor as dispensation; re-registration as the only way to add oversight),
  IDENT-§7.4-03 and IDENT-§7.7-07/-08 (pending_approval triggered by the policy status
  and router annotation) and ASSETS-§5.2-01 (the Assets-only oversight MUST) traced
  requirements that the cycle replaced; their successors are new rows of Core §4.3.10,
  §4.4.8, §6.1, Actions §3.2, §3.7, §3.9, Identity §7.7, §9.1 and Assets §5.2.
- **Both post-execution modes (DR-1/DR-2):** Actions §3.9.2 defines the review when
  `required_within_24h` and `required_post_execution` both apply, but no source of this
  cycle can produce that set (executor-policy sources demand prior approval only); R15
  unit-checks the composition with the modes injected.
  Limit recorded in cycle F: the composition is defined and exercised by two R15 checks that
  inject both modes (deadlines composed, each obligation expiring on its own). That the current
  sources produce the combination is not demonstrated; the composition rule is kept.
- **Compliance-field description (DR-1/DR-2):** the `human_oversight` description in
  `arsia-compliance-field.schema.json` still stated the replaced within-24h rule; the
  echo sweep found it and it now follows Core §4.3.6.5 (guarded).
- **Actions TOC anchor (observed in DR-1/DR-2, not fixed):** the table of contents links
  `#14-reserved-system-capabilities`, but the heading is "1.4 Reserved System
  Capabilities (Normative Registry)"; the dead anchor predates the cycle. The §3.7 and
  §3.9 entries added or renamed by the cycle resolve.
  Resolved in cycle F (A-102), together with the Routing §7.4 anchor of the same kind; every
  internal anchor of the six specs is guarded.
- **test-vectors/README format table (DR-1/DR-2):** the format counts (297/378/4) were
  stale since before DR-3/DR-4; they now carry the tool-computed figures.
- **Published counts after DR-1/DR-2:** 33 schemas (incl. meta), 780 vectors
  (453/173/154), RTM 1970 / 1173, 115 consistency checks, harness R1-R15; README.md,
  CLAUDE.md, docs/FAQ.md, docs/getting-started.md and test-vectors/README.md updated.

- **Published counts after VC:** 33 schemas (incl. meta), 783 vectors (457/178/148),
  15 keypairs, RTM 1970 / 1173 (unchanged), 122 consistency checks, harness R1-R16;
  README.md, CLAUDE.md, docs/FAQ.md, docs/getting-started.md, test-vectors/README.md
  and scripts/README.md updated.
- **ITV-589 gateway (VC):** the Identity §7.8 example names no gateway agent-id and
  the vector's token carries no `iss`; `test_metadata.gateway` records
  `agent:regulated-entity.gateway` as a fixture choice so the policy-identity guard
  can key it.
- **ITV-537 residency precedence (observed in VC, not fixed):** the vector follows
  State §8.3 rule 1 (`payload.args.data_residency` takes precedence over the
  envelope's), which may be in tension with the residency intersection of Core
  §4.3.10.5 when the args value lies outside the envelope restriction (candidate
  finding).
- **Schema-expressible runtime rules (observed in VC, not fixed):** INV-20 (Rule 8
  Art. 9(2) basis for sensitive entries) and INV-22 (State §2.1.11 exclusion) test
  cross-field rules JSON Schema could express; they stay runtime-only.
- **Expectation vs description (observed in VC, not fixed):** ITV-417 and ITV-579 carry
  `expected: valid` while their descriptions state a runtime rejection.
  Resolved in cycle F (A-105): `expected_error: "invalid_request"` on both, with ITV-563,
  ITV-571, ITV-577 and INV-08; `expected` stays structural.
- **Placeholder signatures outside the 32 (observed in VC, not fixed):** INV-23,
  INV-24, ITV-566, ITV-567 and ITV-568 are runtime vectors with the literal
  placeholder signature; a runtime runner would stop at signature verification.
  Qualified in LM3: the five carry the most common placeholder value (base64url of
  "test-signature-for-schema-vali…", 98 vectors in all, only these five runtime-only).
  The inventory of signatures outside crypto-block verification (below) is a different
  survey; it does not replace this count.
  Resolved in the Draft-01.1 port (`de9db8d`): INV-23, INV-24, ITV-566, ITV-567 and
  ITV-568 are re-signed and verify with the catalog key of their kid (A-97 guard). The
  placeholder value remains only in ITV-550, a declared signature negative
  (`alg`/`not-allowed`).
- **Free-text expected_error (observed in VC, not fixed):** 16 runtime vectors state
  free text or codes outside Core §11.2 (e.g. `certificate_invalid`,
  `identity_verification_failed`) in `expected_error`.
  Corrected in LM3: 14, not 16 — 10 free-text values and 4 occurrences of two values
  outside the Core §11.2 enum; `certificate_invalid` is a Core §11.2 code (seven runtime
  vectors use it) and was wrongly cited as an example. Classification: expectation
  description only — INV-07, INV-09, INV-11, INV-12, ITV-526, INV-20, INV-22; a §11.2
  code followed by a description — INV-23, INV-24, INV-25 (`forbidden — …`); onboarding
  denial reasons (Identity §7.6 `denial_reason`), valid in their context — ITV-475,
  ITV-476 (`identity_verification_failed`), ITV-477, ITV-479 (`conformance_failed`). Not
  registered as normative defects.
- **R10 scenario candidates (coverage program):** ITV-416, ITV-418, ITV-536, ITV-538,
  ITV-541, ITV-553 and ITV-554 could become R10 scenarios; the resolver already
  implements strict mode and `classification_escalation`.
- **Actions §3.3 example (observed in VC, not fixed):** the decision example shows
  `"reason": null` and `"conditions": null`, while the field definitions and
  `approval-decision-result` type them as string and array; INV-25 omits
  `conditions`.
  Resolved in coverage SC3 (`94f96b6`): that commit removed both null members from the
  §3.3 example, which carries neither now.

- **Signatures outside crypto-block verification (LM3):** 187 vectors carry
  `security.sig` without a `crypto` block, so they are not included in the
  cryptographic verification of `validate_vectors.py --check-crypto`. That alone does
  not show the absence of all validation or of equivalent coverage, and they are not
  "187 invalid signatures". By group: schema 160 (120 expected valid, 40 invalid);
  runtime-only 27 (9 valid, 18 invalid). By cause, resolving the full kid against
  `keypairs.json` under the Draft-02 profile: 55 EdDSA signatures fail with the
  identified key; 126 carry a kid outside the catalog; 5 declare another alg
  (ITV-548, ITV-549, ITV-550; runtime ITV-425, INV-37); 1 verifies (INV-39). Runtime
  IDs: failing — INV-11, ITV-426, ITV-427, ITV-429, ITV-432..437, ITV-446, ITV-479,
  ITV-526, ITV-566, ITV-567, ITV-568; kid outside the catalog — ITV-431, ITV-445,
  INV-23, INV-24, ITV-570, ITV-571, ITV-572, INV-38. The coverage program separates
  purely structural fixtures from runtime scenarios in which a non-verifying signature
  would stop processing before the intended cause.
- **Named conformance tests (LM3, A-53):** by the method that gave 74 at `fb5a875`,
  `bbb8ef3` defines 83 (Actions 19, Core 9, State 15, Assets 8, Identity 22, Routing
  10); the 5 onboarding checks CHECK-01..05 are counted separately. "Executed by no
  script" understates what exists: harness checks name ACTIONS-10 (R7), ASSETS-06 and
  C-09 (R15), and R15 executes the scenario vectors ITV-653/654, ITV-647/648, ITV-662
  and ITV-663, which cite ACTIONS-15, -16, -17 and -18. Per-test classification
  (integral, partial, equivalent, absent) belongs to the coverage program; a literal
  reference to a test name does not count as coverage.
  After the A-79 cycle: 85 (State 17, adding STATE-16 and STATE-17); their scenarios
  are executed by harness R17.
- **INV-39 and INV-38 fixtures (LM3, A-54):** INV-39 verifies under the Draft-02
  profile (only `security.sig` removed) and fails under the Draft-01 profile (the whole
  `security` removed), which is the scenario its description announces; the negative
  needs correcting as well as executing. A-54's criterion (crypto block executed and
  asserted to fail) already forces that correction, so the criterion is unchanged.
  INV-38's kid `#other-key` is not in the catalog; representing its announced scenario
  needs its own key and context.
- **Reference harness approval path (LM3, A-57):** `Run.approval()`
  (`runtime_harness.py`, Actions §3.4) checks correlation, root,
  `request_payload_hash`, the deadline and a duplicate approver. It accepts a decision
  with an invalid signature, one without the `arsiaprotocol.oversight.approve`
  capability, and one whose `result.approver_id` differs from `from`: in each case it
  returns no error and the run moves from `pending` to `executing` (reproduced in LM3,
  [§17][ev17]). The gap is in the reference harness; the fixture relation guards (G3)
  do not replace validation of a received decision, and the result is not extended to
  other repositories.
- **A-88 scope (LM3):** triaged INT by owner decision (2026-11-02) and kept open. Its
  closure is reconsidered in the review of the A-79 cycle, checking that the
  generation model keeps an update of the same entry distinct from the creation of a
  new entry after DELETE. A reasoned disposition can meet the closure criterion; a text
  change is needed only if that review finds remaining ambiguity. A-88 does not
  authorize changing the retention calculation or its anchor, altering schemas or
  adding fields.
  Resolved in the A-79 cycle: the generation model (State §2.1.14) keeps an update of
  the same entry apart from a new entry after DELETE; §2.1.5 now states that
  `created_at` is the creation time of the entry (generation) and is immutable for its
  lifetime. Retention calculation and anchor are unchanged; the `generation` field
  comes from A-79 (DR-5/D2), not from A-88. Closed by clarification and disposition
  ([§18][ev18]).
- **Published counts after the A-79 cycle:** 33 schemas (incl. meta), 800 vectors
  (463/189/148), 15 keypairs, RTM 1981 / 1182, 124 consistency checks, harness
  R1-R17; README.md, CLAUDE.md, docs/FAQ.md, docs/getting-started.md and
  test-vectors/README.md updated. docs/FAQ.md still said 154 skip_schema vectors (stale
  since VC); it now says 148. README.md (two places) and docs/getting-started.md still
  said 1,940 RTM rows (the DR-3/DR-4 total, stale since DR-1/DR-2 raised it to 1,970); they now say 1,981.
- **State RTM coverage summary (A-79 cycle):** the "Coverage Gaps" summary of
  docs/rtm/ARSIA-State.rtm.md stated 411 requirements while the table held 416 rows at
  `df6219c` (§6 and §7 stale since earlier cycles); it is recomputed from the table
  (427 rows after the cycle).
- **STATE-01 (A-79 cycle):** its expected StateEntry now lists `generation` = `1`, a
  consequence of the REQUIRED field (not listed in the cycle plan's text).
- **SNAPSHOT `hash` construction (observed in the A-79 cycle, not fixed):** Actions
  §1.4 requires a "cryptographic hash of the state data" in snapshot responses and the
  schema requires `hash`, but no construction is defined. ITV-677 carries an
  illustrative value (SHA-256 of the RFC 8785 form of its entries) that no rule
  checks.
- **Propagation impact (A-79 cycle):** implementations emit `generation` in every
  StateEntry and in state_set, state_delete and state_purge records, accept
  `expected_generation`, return the State §8.4 details (including `entry_live: false`)
  and keep the highest generation per key while any information of it is held. The SDK
  migration track carries this.
- **Chain fixtures regenerated (A-79 cycle):** ITV-594 gained `generation`, so its
  chain value and those of positions 4 and 5 changed. The record that tombstone
  ITV-595 replaces is synthetic; its content is recorded in [§18][ev18] so the
  tombstone value is reproducible. ITV-598, ITV-599 and ITV-602 were rederived from the
  new ITV-594 and ITV-595 and fail with their stated reasons.
- **Published counts after the retention-axis cycle:** 33 schemas (incl. meta), 815
  vectors (469/198/148), 15 keypairs, RTM 1986 / 1189, 124 consistency checks, harness
  R1-R18; README.md, CLAUDE.md, docs/FAQ.md, docs/getting-started.md and
  test-vectors/README.md updated. README.md still said 783 test vectors in its "New
  here?" paragraph (stale since the A-79 cycle); it now says 815.
- **Named conformance tests (retention-axis cycle):** 86 (State 18, adding STATE-18);
  its scenario is executed by harness R18. STATE-17 now states that its entry has no
  retention period, so its PURGEs need no override.
- **Echoes outside the plan inventory (retention-axis cycle):** the sweeps found two
  A-70 echoes the plan did not list: the MIFID-II row of profiles/README.md ("MiFID II
  Art. 16(7)") and the description of `arsia-mifid-audit-record.schema.json` ("Article
  16(7) record-keeping", "1827 days (5 years)"). Both were aligned with the State §6.3
  grounding.
- **Stale RTM retention rows (retention-axis cycle):** STATE-§4.1.2-02 ("180 days") and
  STATE-§4.1.2-05 ("730 days (2 years)") had drifted from the spec (P6M, P1096D); they
  were corrected with the §4.1.2 rows of the cycle. The day counts of the profiles/README.md
  retention column (180 for EU-AI-ACT-HIGH-RISK, 730 for DSA-VLOP; observed in
  DR-3/DR-4) remain stale and out of the cycle's scope.
- **Retired RTM rows (retention-axis cycle):** STATE-§5.3.2-02 (MAY argue MiFID II
  Art. 16(7) precedence) and STATE-§5.3.2-03 (SHOULD consider pseudonymisation as
  satisfying both duties): the informative guidance of §5.3.2 no longer uses RFC 2119
  keywords and no longer makes either claim.
- **Extension-field descriptions (retention-axis cycle):** `within_retention`,
  `entry_retained_until` and `retention_override` are described by the State §3.2.2
  purge audit table and the §7.1 extension table, like `generation` in the A-79 cycle;
  §7.1 has no per-field heading for extension fields.
- **Retention changes on update (observed in the retention-axis cycle, not fixed):**
  the spec does not say whether a SET that updates an entry may change its `retention`,
  nor, if it may, which retention governs the values written before the change. State
  §3.2.2 uses "the effective retention of that entry" (§2.1.8, §4.1.1); harness R18 uses
  the retention resolved when the generation was created.
- **Propagation impact (retention-axis cycle):** implementations evaluate PURGE against
  stored retention over every generation, accept `retention_override`, reject with the
  State §8.4 retention details, and emit `within_retention`, `entry_retained_until` and
  `retention_override` in `state_purge` records. The SDK migration track carries this.
- **Published counts after the relay/DPoP cycle:** 33 schemas (incl. meta), 829
  vectors (473/208/148), 15 keypairs, RTM 2020 / 1217, 124 consistency checks, harness
  R1-R20; README.md, CLAUDE.md, docs/FAQ.md, docs/getting-started.md and
  test-vectors/README.md (including the per-prefix counts ITV 691, INV 110) updated.
  schemas/README.md maps arsia-dpop-proof to Identity §3.3 and Core §6.3.
- **Named conformance tests (relay/DPoP cycle):** 89 (Identity 23, Routing 12; adding
  IDENTITY-23, ROUTING-11, ROUTING-12). IDENTITY-23 and ROUTING-12 correspond to R20
  (g), (h) and (j) on the reference model; the record shape of ROUTING-11 is ITV-688.
  No test is run against an implementation.
- **RTM coverage summaries (relay/DPoP cycle):** the "Coverage Gaps" summaries of the
  Identity, Routing and Core RTMs were stale since the Draft-02 regeneration (at
  `24b32ed` they stated 263 / 264 / 393 requirements while the tables held 274 / 264 /
  402 rows; Routing's total matched but its vector counts did not). They are recomputed
  from the tables (297 / 273 / 404 rows after the cycle). The "Generated: 2026-07-22"
  lines are kept, as in the State RTM.
- **Broker relay retention fields (observed in the relay/DPoP cycle, not fixed):** the
  ten pre-existing `broker_relay` vectors state `retention_source: "platform-default"`
  and `compliance_profile_resolved: "none"` with `retained_until` 2031-04-11 (five
  years), while the platform default is P90D (State §7.3); in ITV-146, 147, 490, 492,
  508, 511 and 515 the `retained_until` anchor also precedes `processed_at` by days. No
  rule checks these fields for broker records. The new records (ITV-688, 689, 691,
  INV-101..103) use `processed_at` + P90D.
  Resolved in cycle F (A-106): the 16 platform-default `broker_relay` records carry
  `effective_retention` P90D, `retention_anchor` = `processed_at` and `retained_until` =
  anchor + P90D, as do 30 GDPR-STANDARD platform-default records (20 end dates, 10 review
  anchors); guarded over all 62 platform-default records.
- **RFC section citations (observed in the relay/DPoP cycle, not fixed):** State and
  Assets each cite "RFC 8785 §3.1" without brackets; `check_links.py` resolves the §3.1
  to a section of the citing document by coincidence. The new text of the cycle uses the
  bracketed form, which the checker treats as external.
  Resolved in cycle F (A-103): `[RFC 8785] §3.1` in both; guarded.
- **Routing §1.2.2 step 5 (observed in the relay/DPoP cycle, not fixed):** the SHOULD
  that `T_e2e` be sender-constrained with DPoP has no RTM row; the cycle rewrote the
  sentence without adding one.
  Resolved in cycle F (A-104): `ROUTE-§1.2.2-12`.
- **Migration guide (observed in the relay/DPoP cycle, not fixed):**
  docs/draft-02-migration-guide.md does not describe the changes of the A-79,
  retention-axis and relay/DPoP cycles (generations, `retention_override`, conditional
  forwarding fields, the DPoP checks).
  Partly resolved in cycle F: §9–§13 cover the A-79, retention-axis, relay/DPoP and SC2–SC4
  changes and the corpus, and §6 and "What did NOT change" are corrected. The DR-1..DR-5
  changes (post-execution review, obligation resolution, hash chain) are still not described
  (see below).
- **Propagation impact (relay/DPoP cycle):** brokers emit a `broker_relay` record for
  every message received for relay, with the forwarding fields only when forwarding
  was initiated and `relay_latency_ms` computed from the two instants; return a
  recipient nonce challenge as a `recipient_dpop_nonce` relay error and never re-send
  or produce a proof. Receiving agents implement the Identity §3.3 list, the nonce
  challenge and an atomic, shared single-use `jti` store held until `iat` + S. Senders
  retry with a new proof. The SDK migration track carries this.
- **Published counts after the tools cycle:** 33 schemas (incl. meta), 831 vectors
  (473/208/150), 15 keypairs, RTM 2021 / 1218, 126 consistency checks, harness R1-R20;
  README.md, CLAUDE.md, docs/FAQ.md, docs/getting-started.md and test-vectors/README.md
  (INV 112, next INV-113) updated. docs/getting-started.md still said 463 / 189 / 148
  (stale since the A-79 cycle); it now says 473 / 208 / 150. README.md ("815 test
  vectors" in its "New here?" paragraph; "1,986 rows" twice) and docs/getting-started.md
  ("1,986 rows") had been missed by earlier count sweeps, which searched the number
  without its thousands separator; they now say 831 and 2,021.
- **Coverage of the signature negatives (tools cycle):** INV-18 and INV-19 were
  classified `none — conformance test against an implementation` since VC, although
  `validate_vectors.py --check-crypto` asserts their failure; they are now
  `executed: --check-crypto`, like INV-111 and INV-112.
- **Retired tools in historical documents (tools cycle, not changed):** the Draft-01
  audit, the session handovers, docs/draft-02-decisions.md and
  docs/generated/arsia-protocol-overview.md still describe `gen_state_vec2.py` and the
  `--apply` migration of `regen_v2.py`; they record the state at their date.
- **Propagation impact (tools cycle):** none on the wire. Implementations can use
  INV-111 and INV-112 to check that their verifier selects the algorithm from the
  declared `alg` and the key type together (Core §5.2 Step 5).
- **Published counts after the DORA floor cycle:** unchanged (831 vectors, RTM 2021 /
  1218) except 127 consistency checks (CLAUDE.md).
- **Delegated Regulation 2024/1774 Art. 22(d) cross-reference (DORA floor cycle):** the
  original refers to "Article 15" of Delegated Regulation 2024/1772, which has 13
  articles; corrigendum 32024R1774R(02) (OJ L 2025/90420, 15.5.2025) officially
  replaces it by "Article 8(2)". The consolidation 02024R1774-20240625, version
  000.002, incorporates that corrigendum as C1: its Art. 22(d) already refers to
  Art. 8(2) of Delegated Regulation 2024/1772.
- **CRR loss data window (DORA floor cycle, out of scope):** CRR Arts. 317–318 use a
  10-year time window for the operational-risk loss data set; it is a different purpose
  and period and does not ground the DORA floor.
- **Reading method (DORA floor cycle):** the acts were read by PDF text extraction;
  every passage relied on was checked in context.
- **Impact (DORA floor cycle):** no change to the wire structure, the floor value or the
  retention rules. The DORA classification and the DORA catalog digest change; no need
  to migrate existing vectors was identified (the current DORA digest appears in no
  vector).
- **Published counts after coverage SC1:** 846 vectors (475/208/163), 17 keypairs, RTM
  2028 / 1225, 127 consistency checks, harness R1-R22; README.md, CLAUDE.md,
  docs/FAQ.md, docs/getting-started.md and test-vectors/README.md (ITV 693, INV 125,
  next ITV-694 / INV-126) updated.
- **Keypair catalog (coverage SC1, for the SDKs):** two entries added, derived from the
  kid; an additional key of an agent is indexed by its kid
  (`agent:acme.echo-client#other-key`), so consumers that look up an agent's first key
  by agent-id are unaffected.
- **Presented-token convention (coverage SC1):** the 40 vectors with `authorization` and
  no explicit token bind `synthetic-token:<ID>`; the convention, introduced by the
  Draft-02 migration, is now stated in test-vectors/README.md and executed by R21.
- **Routing §7.4.1 step 1 (coverage SC1, not covered):** a residency-constrained message
  arriving without an attestation → `service_unavailable` (ITV-570) is not executed; it
  belongs to SC4. Resolved in coverage SC4: ITV-570 rebuilt as an executed R22 scenario
  (header absent), with ITV-711, ITV-712 and INV-172..177.
- **Crypto blocks with an unpublished kid (observed in coverage SC1, not fixed):** 24
  pre-existing blocks name a kid absent from keypairs.json (e.g. INV-04, ITV-134..137);
  their signatures verify against the key in the block. Draft-01.1 port: the kids of 23 of
  those blocks are now published (A-99); INV-04's malformed kid stays unpublished by
  disposition. The kid ↔ catalog guard applies to published kids and requires one for
  signature negatives and attestations.
- **Attestation zone (observed in coverage SC1, not fixed):** Routing §7.4.1 checks the
  broker's jurisdiction against the message's declared zone; it states no check that the
  attestation's own `residency_zone` equals that zone. R22 follows the text.
- **Published counts after coverage SC2:** 34 schemas (incl. meta), 893 vectors
  (483/215/195), 17 keypairs, RTM 2045 / 1241, 129 consistency checks, harness R1-R22;
  README.md, CLAUDE.md, docs/FAQ.md, docs/getting-started.md, schemas/README.md and
  test-vectors/README.md (ITV 708, INV 157, next ITV-709 / INV-158) updated.
- **Normative changes for the Issue (coverage SC2, CONTRIBUTING §4):** Actions §3.4
  verification order for approved and denied decisions, receipt-instant deadline
  without skew, rejected decisions and Path 3 only while pending (with the §3.2, §3.3,
  §3.5, §3.6, state-machine and §3.9.3 echoes, Assets §5.2); Core §4.2.1 (the log is
  `decision_rejected`) and §5.2 (`verified_kid`, authenticated revocation event);
  Identity §2.5 key-revocation payload and authentication; State §7.1
  `decision_rejected`, `rejection_code`, `verified_kid`; new schema
  `arsia-key-revocation.schema.json`. The late-decision log moved from SHOULD to MUST
  (ACT-§3.4-27); the replies stay SHOULD.
- **Event before removal (coverage SC2, out of scope):** an authenticated
  key-revocation event that arrives while the sender still publishes the key: the
  invalidated cache entry is restored by the next refresh. The vectors follow the
  contract (removal at once, Identity §2.5 item 2); whether an authenticated event
  should outlast a refresh is not stated.
- **R7 reduced (coverage SC2):** the synthetic `verify_decision` was removed; the
  approval-decision verification is executed by R15 on the vectors. R7 keeps the
  pending args/root match and the oversight record counts.
- **Review decisions logged (coverage SC2):** `Review.receive` now records the rejected
  review decisions (verification failures and duplicates) as `decision_rejected`, as
  Actions §3.9.3 required; a valid late review decision is still `review_decision` with
  `late: true`.
- **Receiver simulation without signatures (coverage SC2, not changed):** `receive()`
  of R10 (compliance resolution) does not verify signatures, so its records carry no
  `verified_kid`; the evidence obligation is executed in R15, which verifies.
- **Token claims in the harness (coverage SC2):** the access token is a compact JWS with
  every claim Core §6.1 requires (`iss`, `sub`, `aud`, numeric `iat`/`exp`, `jti`,
  `scope`; checked against `arsia-jwt-claims.schema.json`, none defaulted), signed with an Ed25519 key derived in the harness for the
  trusted issuer and verified under that configured key; R11's issuer audience policy
  now lists `agent:acme.executor`.
- **Stale RTM rows outside the cycle (observed in coverage SC2, not fixed):**
  IDENT-§2.5-04 and IDENT-§3.1-03 (a RECOMMENDED or SHOULD 1-hour cache TTL; the rule is
  the Core §5.2 3600 s MUST ceiling) and IDENT-§2.5-05 (a MAY about future revocation
  mechanisms that §2.5 no longer states) belong to SC4. Resolved in coverage SC4:
  IDENT-§2.5-04 retired (successor CORE-§5.2-11), IDENT-§2.5-05 retired (successors
  IDENT-§2.5-06..09), IDENT-§3.1-03 rewritten as the MAY of Identity §3.1.
- **Published counts after coverage SC3:** 34 schemas (incl. meta), 915 vectors
  (485 schema-valid / 215 expected-invalid / 196 runtime-only / 19 raw), 17 keypairs,
  RTM 2049 / 1245, 131 consistency checks, harness R1-R22; spec examples 82 blocks (77
  full: 75 schema-validated, 2 no-schema; 5 fragments); README.md, CLAUDE.md,
  docs/FAQ.md, docs/getting-started.md and test-vectors/README.md (ITV 710, INV 171, CTV
  16; next ITV-711 / INV-172 / CTV-17) updated.
- **Raw vector format for consumers (coverage SC3):** a fourth test-corpus format
  (`raw_hex` + `expected_parse`, documented in test-vectors/README.md) exercises only the
  Core §5.2 pipeline steps 2–4; a consumer that iterates the corpus expecting
  `message`/`data` must recognize it. Updating the SDK repositories is outside the cycle.
- **Normative change for the Issue (coverage SC3, CONTRIBUTING §4):** Core §5.2 steps 3–4
  state their content (UTF-8, surrogates and noncharacters literal or escaped at any
  depth, duplicates after escape processing) and a document failing steps 2–4 is
  rejected with `invalid_request`; steps 2–4 add no limit on JSON numbers. [RFC 7493] is
  added to the Core normative references.
- **Details objects without schema (coverage SC3, not changed):** the `invalid_request`
  details of Core §4.3.8 Rule 4 (insufficient retention) and of State §5.2 (missing
  legal basis) are required by the text but `arsia-message.schema.json` defines no
  `$def` for them; their examples are annotated `no-schema`. A candidate for a schema
  addition, which would be normative.
- **Example annotations (coverage SC3):** every full ```json block in `spec/` carries
  `<!-- example: … -->` on the line above (vocabulary in `scripts/extract_examples.py`);
  a new example without one fails the extractor.
- **Fixture quality (coverage SC3):** R15 validates against the message schema every
  approval and review decision it builds; this exposed INV-134 (`capabilities: []`
  fails `minItems`, so pipeline step 11 would have pre-empted its `forbidden`), now
  `["test.unit"]`.

- **Published counts after coverage SC4:** 34 schemas (incl. meta), 923 vectors
  (487 schema-valid / 215 expected-invalid / 202 runtime-only / 19 raw), 17 keypairs,
  RTM 2045 rows / 1247 MUST + MUST_NOT / 1445 MUST, MUST_NOT or REQUIRED, 138 consistency
  checks, harness R1-R22; README.md, CLAUDE.md, docs/FAQ.md, docs/getting-started.md and
  test-vectors/README.md (ITV 712, INV 177, CTV 16; next ITV-713 / INV-178 / CTV-17)
  updated. SECURITY.md still carries Draft-01 counts; it changed only on main and is
  reconciled with the merge.
- **Normative changes for the Issue (coverage SC4, CONTRIBUTING §4):** Routing §7.4.1 —
  step 1 rejects a residency-constrained message without the `ARSIA-Relay-Attestation`
  header (`service_unavailable`), and a present header, even empty, is processed by steps
  2–5; step 2 requires non-empty base64url without padding (an explicit ARSIA rule against
  RFC 4648 §3.2's default), the Core §5.2 steps 2–4 checks on the decoded octets and the
  attestation schema before the signature; their failures are `unauthorized`, not
  `invalid_request`. The header descriptions (§1.2.2 step 7, §7.3) say "without padding";
  [RFC 4648] added to the Routing normative references.
- **Assets §7 runner sentence (coverage SC4):** the runner "executes only the test parts
  identified as executed in `docs/draft-02-conformance-tests.md`"; "MUST pass all eight
  tests" unchanged. Not a change of conformance requirements.
- **RTM format for consumers (coverage SC4):** the RTMs have a ninth column, `Evidence`
  (vocabulary in docs/rtm/README.md); a consumer that parses them by position must read
  the header. The Vector column now holds only vector IDs.
- **Validator results for consumers (coverage SC4):** `vector_results` and `crypto_results`
  in `scripts/validate_vectors.py` return the observed result per vector; the CLI output
  is unchanged except `# crypto: ok …` comment lines in TAP mode.
- **Corpus header (coverage SC4):** `version` 2.0.0 (the Draft-02 corpus; Draft-01 corpora
  were 1.0.x) and `generated` 2026-11-05T23:27:56.000Z; consumers that pin the corpus by
  version must expect the new major.
- **Removed RTM rows (coverage SC4):** CORE-§4.3.7-02, -03, CORE-§4.3.6.4-03, -04 (clamp to
  the floor and its warning; successor CORE-§4.3.7-04 and the Rule 4 rows),
  CORE-§4.4.7-02, -03, -04 (warn and process; successor CORE-§4.4.7-05), IDENT-§2.5-04,
  -05 (successors CORE-§5.2-11, IDENT-§2.5-06..09). Rewritten: CORE-§4.4.7-01,
  IDENT-§3.1-03, CORE-§10.4-01 (the signed envelope key is authoritative). CORE-§4.3.6.4-03,
  -04 and CORE-§10.4-01 were found in the review and treated under the owner's bounded
  authorisation.
- **Named tests not executed here (coverage SC4):** the absent and external classes of
  `docs/draft-02-conformance-tests.md` (39 tests) and the unexecuted parts of the 43
  partial ones and of the equivalent one remain conformance requirements for
  implementations; models for QUERY, GRANT, escrow, X.509, onboarding phases and transport
  were outside the cycle.

- **Draft-01.1 port (for consumers):**
  - `test-vectors/keypairs.json` has 53 entries and a `provenance` member. The 34 imported
    entries are byte-identical to the Draft-01.1 catalog.
    `agent:acme.legacy-system#rsa1024` is below the RSA minimum by design and must never
    verify.
    Correction (cycle F): "must never verify" was imprecise when written. ITV-425 carries
    a mathematically valid signature with this key, which a conformant verifier rejects
    for insufficient key size; the key and the vector are unchanged.
  - A vector without a crypto block may carry `signature_expectation`, only when its
    signed object (`message`, or `data` of an arsia-message / arsia-relay-attestation
    schema-ref) carries `security.sig` as a string; the meta-schema enforces it. Without
    the field, a present signature verifies with the catalog key of its kid. Every such
    signature is canonical base64url without padding.
  - The catalog publishes every kid a signature outside a crypto block uses and the kids
    of the 23 crypto blocks the port covered. INV-04 is the one exception, by
    disposition: its crypto block keeps the malformed kid `echo-client#key1` that its
    structural defect requires, carries its own key (the catalog key of
    `agent:acme.echo-client#key1`) and verifies.
  - `regen_v2.py --catalog` re-signs such vectors.
  - INV-21 changed format from message-only to schema-ref, against `#/$defs/set-args`.
  - `resolve_schema` now returns a reference into the document for fragment schema refs.
- **Published counts after the Draft-01.1 port:** 923 vectors (485 schema-valid / 215
  expected-invalid / 204 runtime-only / 19 raw), 53 keypairs, 142 consistency checks,
  updated in README.md, CLAUDE.md, docs/getting-started.md and test-vectors/README.md.
- **Main reconciliation (for consumers):**
  - ITV-201, ITV-423 and ITV-266 now carry a signed `security` block, and ITV-482
    carries `capabilities: ["arsiaprotocol.onboarding.evaluate"]` (Identity §7.6). Each
    now fails only for the rule it tests (A-100).
  - `keypairs.json` imports `agent:acme.state-extension#key1` unchanged from the
    Draft-01.1 catalog: 54 entries, 35 of them imported.
  - CHANGELOG: `## [Draft-02] — Unreleased` above the historical Draft-01.1 entry.
- **Published counts after the main reconciliation:** 923 vectors (unchanged), 54
  keypairs, 142 consistency checks, updated in README.md, CLAUDE.md, CHANGELOG.md and
  test-vectors/README.md.
- **Retention end dates outside cycle F (observed in cycle F, not fixed):** 18 records with
  `retention_source: profile-minimum` carry a `retained_until` that differs from their own
  `obligation_resolution` retention result (State §7.1: the fields MUST NOT diverge): ITV-16,
  ITV-88..92, ITV-95, ITV-96, ITV-99, ITV-220, ITV-269, ITV-525, ITV-586, ITV-588, ITV-681,
  INV-47, INV-50, INV-84 (MIFID-II 10, EU-AI-ACT-HIGH-RISK 8; e.g. ITV-16 2026-10-24 against
  `P6M` from 2026-04-27, i.e. 2026-10-27). Outside the authorised cycle F groups.
- **Migration guide, DR-1..DR-5 (observed in cycle F, not fixed):** the guide predates
  `e5e06a5`; it does not describe executor oversight and post-execution review (DR-1/DR-2),
  the obligation resolution (DR-3/DR-4) or the audit hash chain and tombstones (DR-5).
- **Cycle F (for consumers):** 33 new breach-notification vectors; 6 runtime-only vectors gain
  `expected_error`; 46 audit-record fixtures change retention fields only;
  `ROUTE-§1.2.2-12`; profiles README retention column from the catalog.
- **Published counts after cycle F:** 956 vectors, 54 keypairs, 146 consistency checks, RTM 2046
  rows, updated in README.md, CLAUDE.md, docs/getting-started.md, docs/FAQ.md, SECURITY.md,
  CHANGELOG.md and test-vectors/README.md.

[ev17]: draft-02-remediation-ledger-evidence.md#17-lm3-closure-evidence
[ev18]: draft-02-remediation-ledger-evidence.md#18-a-79-cycle-closure-evidence
[reg8]: draft-02-remediation-ledger-regulatory.md#8-open-notes-regulatory
