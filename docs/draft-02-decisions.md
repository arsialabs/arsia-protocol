<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Draft-02 Decision Records

Companion to `docs/draft-02-implementation-plan.md` and `docs/draft-02-findings-status.md` (audit provenance: SHA-256 `abc61eba…2472`). One record per blocker and per material wire-format change; small non-controversial fixes are grouped. Owner-approved decisions D1–D5 (2026-07-22) are binding inputs; their verbatim qualifications are preserved in the implementation plan.

---

## DR-B03 — MiFID II retention constant: 1827 days

- **Finding:** B-03 (CONFIRMED). 1825 appeared in Assets (×6: §3.1.2, §3.2.2, §3.3.3 examples; §6.1.2 ×2; ASSETS-07), Actions (×2: §2.1 example, §7.2), Identity §9.3 (miscited State §6.3, which says 1827). Core, State, Routing, FAQ, both compliance schemas, the profiles catalog, the MiFID audit-record schema, the Assets RTM, and all vectors already said 1827.
- **Decision:** standardize **1827** everywhere, per the audit's registered direction and the FAQ rationale (worst-case 5-year span contains 2 leap years: 1827 days; docs/FAQ.md:83-85).
- **Alternatives:** 1825 (rejected — undercounts leap days; would require changing Core, State, Routing, schemas, catalog and every vector, and contradicts the documented leap-year doctrine also used for 1096/731).
- **Files changed:** `spec/ARSIA-Assets.md` (6 sites), `spec/ARSIA-Actions.md` (2), `spec/ARSIA-Identity.md` (1 — the State §6.3 citation is now accurate), `scripts/gen_state_vec2.py` (stale generator constant).
- **Impact:** interop — none negative (schemas/vectors already enforced 1827; prose now matches). Compatibility — Draft-01 implementations that accepted 1825-1826 per Assets prose were already rejected by the schemas and Core Rule 4; migration guide will note it.
- **Tests:** floor boundary vectors (1826 invalid / 1827 valid) are delivered with DR-D1, which owns the reject rule and converts the retention model to typed durations. Anti-regression: the Phase-6 consistency checker greps for `1825` outside historical audit documents and the FAQ rationale.
- **Residual risk:** none beyond D1 dependency.

---

## DR-B01 — Correlation semantics + mandatory `root_request_id`

- **Finding:** B-01 (CONFIRMED). Core §2.2 said "id of the original request message" for all four reply intents; Core §4.2.1 and Actions §3.3 said immediate-predecessor; Actions §3.4 Step 3 rejects decisions correlated per §2.2's reading.
- **Decision (owner-approved):** `correlation_id` = id of the **immediately preceding message** (immediate causal parent) — Core §2.2 aligned to §4.2.1/Actions §3.3. New envelope field **`root_request_id`** (Core §4.2.4): REQUIRED whenever `correlation_id` is required; MUST equal the initiating request's `id`; MUST be absent on the initiating request. Receivers verify chain consistency (reply's root == correlated message's root/id) and reject mismatches with `invalid_request`. `payload.args.original_request_id` (pending_approval) is KEPT for payload self-containment with a MUST-equal-envelope-root constraint (negative test: mismatch).
- **Chain reconstruction:** request → pending_approval (corr=request, root=request) → approval_decision (corr=pending, root=request) → response/error (corr=request, root=request). Unknown/duplicate/late correlation rules added to §4.2.1 (unknown: not processed as reply, log; approval_decision → `invalid_request`; response/error MAY discard. Duplicate/late: MUST NOT change recorded outcome).
- **Alternatives:** (a) correlation always = original request (rejected: loses hop causality; contradicts Actions §3.4 verification and M-16 flows); (b) correlation-to-previous only, no root (rejected by owner review: original requester cannot match the final response in ≥3-party flows); (c) generic typed relation mechanism now (deferred to H3 assessment; root+correlation is the minimal sufficient pair).
- **Files:** `spec/ARSIA-Core.md` (§2.2 both definitions, §4.2.1 rewrite, new §4.2.4 — appended, no renumbering), `spec/ARSIA-Actions.md` (§3.2 envelope table + `original_request_id` constraint, §3.3 table, §3.4 Step 3, error examples, audit Records 2-4 tables), `schemas/arsia-message.schema.json` (`root_request_id` property added; conditional `required` deferred to the v2 regeneration pass, tracked in Phase 1.12).
- **Impact:** interop — deterministic chain reconstruction without payload knowledge; enables audit query per interaction and A-11 second receipts. Security — root mismatch rejection closes approval-misdirection splices. Compatibility — breaking (new required field in v2); migration guide entry queued.
- **Tests (Phase 1.12 vectors):** positive full chain; negative: decision with wrong root; pending_approval with args/envelope root mismatch; reply without root (v2); root present on initiating request; duplicate decision; late decision.
- **Residual risk:** H3 re-assessment may still add typed relations for supersedes/reversal; root covers reply-chains only.

---

## DR-D1 — Retention: global reject, typed calendar durations end-to-end (B-02, A-15, M-31, A-05 structural core, N-02, N-01 adjacency)

- **Findings:** B-02 (clamp-MUST vs reject-MUST), A-15 (schema floors reject where prose clamps; EU-AI-ACT floors missing), M-31 ("at least six months" rendered as 180 days), A-05 core (audit records declared-only), N-02 (catalog schema-invalid), N-01 (query-response AuditRecord drift). All CONFIRMED in Phase 0.
- **Decision (owner-approved D1):**
  1. **Global reject, no silent clamp.** Core §4.3.8 Rule 4 generalized from MiFID-II to "Profile retention floor" for every profile with a `retention_minimum`. Explicit below-floor declaration → `invalid_request` with details `{insufficient_retention, profile, declared_retention, minimum_retention, retention_anchor, declared_retained_until, minimum_retained_until, resolution_source}`. Absent → profile minimum applies (never rejects). Clamp language deleted from Core §4.3.6.4/§4.3.7 and State §2.1.8/§4.1/§8.3 rule 2 (the `max()` formulas).
  2. **Typed durations end-to-end.** Envelope field `retention_days` (integer) → `retention` (ISO 8601 calendar-duration subset `^P(?=\d)(\d+Y)?(\d+M)?(\d+D)?$`); same for the StateEntry override (§2.1.8) and the ActionDescriptor override (Actions §2.1). Catalog: `defaults.retention_days` → `retention_minimum` durations + `retention_basis` (`regulatory|profile_floor|technical_default|conservative_policy`), `retention_reference`, `retention_interpretation`. EU-AI-ACT-HIGH-RISK = **"P6M"** (calendar months, resolving M-31); MIFID-II/DORA P1827D; PAC P1096D; DSA-VLOP P730D (M-02 pending); LIMITED P90D; GDPR null.
  3. **Single anchor + calendar arithmetic** (new Core §4.3.6.4.1): anchor = creation instant of the retention-bearing object (audit record `processed_at`; state entry `created_at`; never message `ts`); month/year addition clamps to end of target month; comparison via `retained_until` instants from the same anchor.
  4. **Audit record (A-05 core / State §7.1):** `compliance_profile` → `compliance_profile_declared` (string|null) + `compliance_profile_resolved`; new `declared_retention`, `effective_retention`, `retention_anchor`, `retention_source` (`per-message|profile-minimum|platform-default|none`); `retained_until` = anchor + effective (calendar). Profile-absent-but-compliance-present case now defined (declared=null, resolved=GDPR-STANDARD).
- **Schema expressibility trade-off (recorded deliberately):** calendar-duration floor comparison (`P180D` vs `P6M`) is not expressible in JSON Schema; the Draft-01 numeric `if/then` floors are superseded. Schemas validate the duration **format**; the floor is a runtime rule of the same class as the `data_residency` cross-object invariant already delegated to runtime, covered by runtime vectors (ITV-563/564/565, `skip_schema` with reasons) and by the Phase-6 runtime harness. This qualifies plan principle "schemas must reject what prose rejects" for calendar constraints — classified, tested, not silent.
- **Transition mechanics (suite green at every step):** schemas currently accept both `retention` (new) and `retention_days` (legacy) — the legacy field, the numeric floor `if/then` blocks, and the audit-record `compliance_profile` are REMOVED at the Phase-1.12 regeneration when all vectors flip to the v2 wire; tracked in the 1.12 checklist. Catalog + profiles schema already fully converted (no vector dependency).
- **Also fixed here:** **N-02** — `$comment` whitelisted in `arsia-compliance-profiles.schema.json`; catalog now validates (0 errors; CI check queued for Phase 6). **N-01** — `arsia-audit-query-response.schema.json` `$defs/AuditRecord` replaced by `$ref` to the standalone record schema (drift eliminated). **M-01** — `clock_skew_seconds` rows added to State §6.2 (120) and §6.3 (60), matching the catalog; §6.7's cross-reference now resolves.
- **Alternatives rejected:** global clamp (unexpressible in schema, silent declared≠effective divergence, compounds A-05); lex-specialis MIFID-only reject (leaves A-15 asymmetry, hard-codes a per-profile flag); per-profile `floor_behavior` flag (doubles conformance matrix, no profile needs clamp); day-typed fields with conservative conversion (recreates the M-31 approximation, owner-rejected).
- **Files:** `spec/ARSIA-Core.md` (§4.3.6.4 + new §4.3.6.4.1, §4.3.7, §4.3.8 Rule 4, ToC, §13.3 mention, Appendix A.2 → `"P6M"`), `spec/ARSIA-State.md` (§1 scope texts, §2.1.8, §3.1 args table, §4.1 hierarchy + mini-tables, §6.1–6.7 tables + Art. 26(6)/16(7)/2116/DSA rationales, §7.1 six field definitions, §7.3, STATE-12/13, STATE-xx SNAPSHOT precondition), `spec/ARSIA-Actions.md` (§2.1 descriptor field + example, §3.5 Art. 26(6) text), `spec/ARSIA-Assets.md` (3 examples, §2/§6.1.2 mentions, ASSETS-07 step 3), `spec/ARSIA-Identity.md` (§9.3, IDENTITY-20 table), `docs/FAQ.md` (3 entries), `profiles/arsia-compliance-profiles.json` (full conversion, version 2.0.0), `schemas/arsia-compliance-profiles.schema.json`, `schemas/arsia-compliance-field.schema.json`, `schemas/arsia-message.schema.json` (inline copy), `schemas/arsia-audit-record.schema.json` (6 new fields), `schemas/arsia-audit-query-response.schema.json` ($ref), `test-vectors/arsia-test-vectors.json` (+7: ITV-561..565, INV-26/27), `test-vectors/README.md`.
- **Impact:** interop — rejection observable by sender; deterministic calendar rule ends implementation divergence on month arithmetic. Security/audit — declared vs resolved provable; no silent divergence. Compatibility — breaking (field rename + type change); migration `retention_days: N` → `retention: "PND"` documented in field prose and queued for the migration guide.
- **Tests:** ITV-561 (P1827D boundary pass), ITV-562 (P6M pass), INV-26 (bare "180" rejected), INV-27 (time component rejected), ITV-563 (below-floor MIFID reject, runtime), ITV-564 (P180D vs P6M calendar reject, runtime), ITV-565 (absent → profile minimum, runtime). Suite: 620 vectors, 0 fail, meta+error-paths clean.
- **Residual risks:** calendar floor not schema-enforced (mitigated by runtime harness, Phase 6); M-02 (730 vs 731) pending Phase 3 and may adjust DSA-VLOP to P731D; legacy dual-acceptance window until 1.12 (tracked).

---

## DR-B04 — Reserved-capability registry

- **Finding:** B-04 (CONFIRMED). Actions §1.1 Rule 5 rejects any `arsiaprotocol.*` capability outside the closed §1.4 list, yet Core normatively uses `arsiaprotocol.echo` (§2.2/§4.2.3 note/A.1, conformance) and `arsiaprotocol.health` (A.3), Identity §7.1.1 REQUIRES `arsiaprotocol.onboarding.evaluate`, and Identity §8 examples used `arsiaprotocol.code.review`/`code.refactor`/`test.unit`.
- **Decision:** Actions §1.4 becomes the **single normative registry** of the reserved namespace, with an explicit extension rule (registration only by spec revision; unknown reserved names always rejected, never treated as application-defined). Registered: `echo`, `health`, `onboarding.evaluate` (gateway-only), and `broker.use` (delegable "use a broker" — the D2 counterpart of broker-only `broker.relay`), each with constraints. Dev-tooling example capabilities are NOT system capabilities: Identity §8 examples, IDENTITY-16-18 tests, 16 vector occurrences and one schema description moved off the prefix (`code.review`, `code.refactor`, `test.unit`, `test.*`).
- **Alternatives:** runtime-extensible reserved registry (rejected: reserved namespace must be closed for security review; applications have the whole unreserved space); registering the dev-tooling examples (rejected: they are illustrative application capabilities, not protocol machinery).
- **Files:** `spec/ARSIA-Actions.md` (§1.4 intro + 4 new entries), `spec/ARSIA-Identity.md` (18 renames), `schemas/arsia-capability-policy.schema.json` (description), `test-vectors/arsia-test-vectors.json` (16 renames; no crypto-block vector affected — 83/83 crypto still pass).
- **Impact:** examples/conformance no longer self-invalidating; Rule 5 unchanged (still fail-closed). Compatibility: Draft-01 deployments using the previously unregistered names were already non-conformant per Rule 5. Tests: registry-membership negative vector added with the B-07 batch; suite 620/0.
- **Residual:** `broker.use` semantics complete with DR-D2 (Routing §2.3).

---

## DR-B07 — Single capability-matching algorithm; reserved namespace never wildcard-matched

- **Finding:** B-07 (CONFIRMED). Core §6.4 step 5 mandated "exact string comparison (no wildcards, no hierarchical expansion)" in the very token-scope-vs-capabilities comparison where Actions §1.2/ACTIONS-03 mandate wildcard expansion; the Draft-01 informative note acknowledged but did not resolve it.
- **Decision:** Actions §1.2 is the **single normative matching algorithm**; Core §6.4 step 5 now delegates to it explicitly (informative note removed). Algorithm: (1) exact match; (2) single-trailing-wildcard expansion (`P.*` satisfies any concrete capability with prefix `P.`); (3) **reserved-namespace exception hardened** — every `arsiaprotocol.` capability is non-delegable: only exact scope entries satisfy them, wildcard scope entries inside the reserved namespace MUST NOT be issued and satisfy nothing. This flips the Draft-01 example row `arsiaprotocol.*` → `broker.relay` from ACCEPTED to REJECTED — a deliberate hardening: each reserved capability confers a role (approver, broker, gateway, admin) that a wildcard grant would confer without AS evaluation, contradicting §1.4's own role constraints. Envelope `capabilities` remain concrete-only (Core §4.2.3; schema `capability-name` pattern already enforces).
- **Mission case coverage:** exact ✔ (ACTIONS-02/existing); valid wildcard ✔ ITV-566/ACTIONS-03; invalid wildcard forms ✔ INV-28 (envelope wildcard), INV-29 (bare `*`), INV-30 (mid-name); non-delegable/elevated via wildcard ✔ ITV-567; unknown reserved name ✔ ITV-568 (also closes the B-04 negative); multiple scopes/partial list ✔ §1.2 multi-capability + scope-composition rules (runtime harness cases queued Phase 6); different namespace ✔ existing `notes.*`→`billing.read` row.
- **Files:** `spec/ARSIA-Core.md` (§6.4 step 5), `spec/ARSIA-Actions.md` (§1.2 condition 3, example table, §1.4 Non-Delegable block), `test-vectors/` (+6: ITV-566..568, INV-28..30), README counts.
- **Impact:** interop — one algorithm, referenced from both documents; security — closes wildcard role-escalation; compatibility — tokens relying on `arsiaprotocol.*` scopes stop working (they violated §1.4 role constraints already); migration guide entry queued. Suite: 626 vectors, 0 fail.
- **Residual:** scope-composition edge cases (multiple wildcards, overlapping scopes) covered by runtime harness in Phase 6.

---

## DR-B06 — Canonical `pending_approval`/`approval_decision` contract

- **Finding:** B-06 (CONFIRMED). Assets §5.2 used `payload.result` with its own fields (`reason`, `human_oversight_required`, `summary`, `approver`, `justification`) and enums `rejected`/`timeout`; Actions §3.2-3.3, Core §4.4.7, the message schema and State §7.1 use `payload.args` with 6 canonical fields and `approved|denied` / `denied|expired`. The contradiction was embedded in two normative conformance tests (Actions table vs ASSETS-06).
- **Decision:** the **Actions §3.2/§3.3 contract is canonical**; Assets defines no oversight shape of its own. Assets §5.2 Steps 3-5 rewritten onto `payload.args` (canonical 6 fields; transfer description goes in `context`) and the canonical decision result (`decision ∈ approved|denied`, `approver_id`, `reason`, `conditions`), with `root_request_id` in both envelopes (DR-B01) and explicit invalid-decision handling (bad enum/correlation/capabilities → `invalid_request`/`forbidden`, no execution). Assets §6.1.1 `human_oversight_status` → `not_required|pending|approved|denied|expired` (matches State §7.1). ASSETS-06 rewritten on the canonical shape + a new expired-path expectation (timeout → receipt `failed`, audit `expired`). `arsia-mifid-audit-record.schema.json` enum unified; vectors ITV-123/ITV-145 updated accordingly.
- **Alternatives:** keeping an Assets-specific richer shape (rejected — two shapes for one payload type is the interop bug itself; the canonical `context` field carries the summary).
- **Files:** `spec/ARSIA-Assets.md` (§5.2 Steps 3-5, §6.1.1 row, ASSETS-06), `schemas/arsia-mifid-audit-record.schema.json`, `test-vectors/` (ITV-123, ITV-145).
- **Impact:** approval flows now validate against one schema; audit events consistent across Actions/State/Assets. Compatibility: Draft-01 Assets-style approvals were already schema-invalid; migration note queued. Coverage: approval/denial paths in existing ACTIONS/oversight vectors; timeout path in ASSETS-06 expectation + Phase-6 runtime harness; invalid-decision negatives queued for 1.12 batch (approval enum invalid; mis-correlated decision — with root mismatch case from DR-B01). Suite: 626/0, crypto 83/83, error-paths 0.
- **Residual:** escrow audit field naming (`audit_id`/`timestamp`) is M-07, Phase 3; A-10 `updated_at` handled in Phase 2.

---

## DR-A17/A01-MIN — Issuer trust + agent resolution (foundation slice for B-05)

- **Findings:** A-17, A-01 (both CONFIRMED; §6.4 never validated `iss`; no agent-id→origin mechanism anywhere).
- **Decision (minimal slice):** new **Core §6.5 Authorization Server Trust** — explicit issuer trust configuration (issuer id, key origin — never from inside the token, audience policy, allowed algorithms); §6.4 step 3 now validates `iss` against it and scopes `aud` by issuer policy; unknown issuer / unreachable keys → fail closed `unauthorized`. New **Core §6.6 Agent Identifier Resolution** — registry-based mapping agent-id→origin with 5 normative minimums (authenticated out-of-band source; deterministic, no heuristic DNS guessing; discovery `agent_id` consistency check; unresolvable `from` → reject `unauthorized`; caching tied to §7.3 + onboarding revocation). Core §5.2 Step 2 and Identity §3.1 step 4 now reference §6.6. DNS convention deliberately deferred (additive future option).
- **Files:** `spec/ARSIA-Core.md` (new §6.5/§6.6, §6.4 step 3, §5.2 Step 2), `spec/ARSIA-Identity.md` (§3.1 step 4).
- **Impact:** closes the "self-published key proves nothing" hole and makes verification chains startable deterministically; prerequisite for DR-D2. Full A-17 (trust policy details)/A-18 (revocation under cache, incl. the 1h-vs-24h cache inconsistency) complete in Phase 2. Tests: runtime harness cases (unknown issuer; iss mismatch; key from token URL; unresolvable from) queued Phase 6.

---

## DR-D2 — Executable broker relay: dual authorization + bound relay attestation (B-05, absorbs M-05, partial A-14)

- **Finding:** B-05 (CONFIRMED, both defects: sender required to hold broker-only `broker.relay`; broker's own token `sub`≠`from` force-rejected by Core §6.4). M-05 (three divergent relay-audit contracts). A-14 (broker bypass undetectable).
- **Decision (owner-approved D2 — "end-to-end sender authorization + independently authenticated relay"):**
  1. **Two authorities:** `T_use` (sub=sender, aud=broker, scope ⊇ `arsiaprotocol.broker.use` — new delegable capability, DR-B04) authorises using the broker; the broker's role remains `broker.relay` (broker-only, non-delegable per DR-B07). `T_e2e` (sub=from, aud=to, scope = envelope capabilities, TTL ≤300 s recommended, DPoP-preferred) travels with the message and is forwarded verbatim — **Core §6.4 unchanged**; direct and brokered delivery indistinguishable at the token layer. The broker obtains no token for the recipient and MUST NOT redeem/exchange `T_e2e`.
  2. **Cryptographic binding (no mix-and-match):** new envelope field `authorization {token_hash: "sha-256:<hex>", proof_type: bearer|dpop}` (Core §4.3.9), REQUIRED when `data_residency` is set, covered by the end-to-end signature; attestation carries both `envelope_hash` and `authorization_token_hash`. Hash definitions unambiguous: `envelope_hash = SHA-256(JCS(complete signed envelope incl. security.sig))` ≠ signing input (JCS minus `sig`).
  3. **Relay attestation** ("relay evidence", not physical-residency proof): versioned signed object `{v, attestation_id, broker_id, message_id, sender, recipient, envelope_hash, authorization_token_hash, residency_zone, received_at, forwarded_at, policy_ref, issued_at, valid_until, security}` — Routing §7.4.1; signed like an envelope (JCS minus `security.sig` — consistent with D3); `valid_until` bounds relay acceptance only, evidentiary verifiability governed by retention + broker key history (ties to A-18); replay rules via `attestation_id` + window.
  4. **Normative transport mapping:** sender→broker `Authorization: Bearer|DPoP {T_use}` + `ARSIA-Recipient-Token: {T_e2e}` + conditional `ARSIA-Recipient-DPoP` (precomputed against recipient `htu`; fits the 10 s forwarding budget); broker→recipient `Authorization: {T_e2e verbatim}` + conditional `DPoP` + `ARSIA-Relay-Attestation` (Routing §2.3.1/2.3.2 header tables). The attestation JWS is the broker's authentication on the relay leg — no second broker token round-trip inside the 10 s budget; broker authorization is established by the recipient checking broker registry/IdentityRecord + `broker.relay` declaration + zone.
  5. **Recipient obligations** (Routing §7.4.1): residency-constrained message without valid attestation → `service_unavailable {data_residency_violation}` — **broker bypass now detectable** (A-14 partial); attestation signature/broker authorization/hash-match/window failures → `unauthorized`.
  6. **M-05 unified:** `BrokerRelayAuditRecord`/`audit_type`/`zone` contracts replaced by ArsiaAuditRecord `event_type: "broker_relay"` with named extension fields incl. `message_ts` (Core §9.2's required `ts`) — Routing §7.4.2; Core §9.2 items 2/4 rewritten; §7.4 retention list converted to durations (D1). Legacy `arsia-broker-relay-audit.schema.json` marked superseded; removal at 1.12.
  7. **RFC 8693** = OPTIONAL token-exchange profile (Routing §2.3.2.1), additive only, requires §6.5 issuer trust + PoP + audience policy; never replaces the base flow.
- **Alternatives rejected:** RFC 8693 as base (rewrites §6.4 at every recipient, extra round-trip in the 10 s budget, depends on A-17-complete infrastructure); token-binding exception for trusted brokers (breaks the sub==from invariant, confused-deputy surface).
- **Files:** `spec/ARSIA-Routing.md` (§1.2.2 steps 5-9, §2.3.1/2.3.2 + §2.3.2.1, §5.3, §7.4 rewritten), `spec/ARSIA-Core.md` (new §4.3.9, §9.2 items 2/4), `spec/ARSIA-Actions.md` (§1.4 `broker.use`, via DR-B04), `schemas/arsia-message.schema.json` (`authorization`), new `schemas/arsia-relay-attestation.schema.json`, `schemas/README.md`, vectors ITV-569..572 + INV-31/32.
- **Impact:** brokered routing becomes executable under the protocol's own rules for the first time. Security: bearer exposure of `T_e2e` to the broker bounded by TTL + DPoP + hash binding + idempotency (worst case: broker re-delivers the same signed message — deduplicated); mix-and-match splicing closed by the three-way hash binding. Compatibility: Draft-01 brokered routing was unexecutable, so no conformant deployment breaks; wire additions are two headers + one envelope field + one attestation object. Migration guide + Core §13.2 threat-model entry queued (A-14, Phase 2).
- **Tests:** ITV-569 (attestation valid), INV-31 (missing token binding), INV-32 (hash format), ITV-570 (bypass detection), ITV-571 (broker token substitution rejected), ITV-572 (missing broker.use / wrong aud). Happy-path end-to-end + envelope-modification cases → runtime harness (Phase 6) + ROUTING-01..04 updates (Phase 6 RTM pass). Suite: 632 vectors, 0 fail.
- **Residual risks:** attestation is evidence, not physical proof (stated normatively); broker can still observe traffic metadata (threat model, Phase 2); DPoP nonce management deployment-specific.

---

## DR-D4 — Value semantics + decimal-string amounts (B-08, A-20, N-03, N-10)

- **Findings:** B-08 (State §2.1.2 MUST-NOT + MAY self-contradiction on lexical fidelity, JCS-incompatible), A-20 (2dp universal rule vs ISO 4217 minor units; receipt precision keyed on wrong discriminator), N-03 (float `multipleOf` rejects wire-valid `19.99` EUR), N-10 (3-decimal currencies inexpressible).
- **Decision (owner-approved D4):**
  1. **State §2.1.2 rewritten:** JSON **value and type** semantics per I-JSON preserved; lexical form explicitly NOT preserved (`1.0` ≡ `1`; returned values MAY use JCS canonical serialization — the signing layer makes lexical round-tripping impossible by construction). Integers beyond ±2^53−1 as JSON numbers → `invalid_request`; precision-significant values MUST be strings. Version history/SNAPSHOT compare by value.
  2. **Assets amounts = canonical decimal strings** (request/receipt/reversal amounts, MiFID record `amount`/`actual_amount`, generic audit-record `amount` extension): corrected ABNF `amount = integer [fraction]; integer = "0" / non-zero-digit *DIGIT; fraction = "." 1*DIGIT` (accepts `"0.01"`); no exponent/`+`/sign/whitespace/thousands separators/decimal comma/leading zeros/NaN/Infinity; limits ≤36 chars, ≤16 integer digits; strictly positive — **no negative amounts anywhere; reversal is the operation type with positive `reversal_amount`**; per-operation zero rule (transfers reject 0).
  3. **Currency = fixed ISO 4217 scale** (one canonical representation per value): EUR `"1500.00"`, JPY `"1500"`, KWD `"1500.000"`; canonical-equality explicit — for EUR, `"1500"`, `"1500.0"`, `"1500.000"` are invalid. Entries without a numeric minor-unit exponent → reject unless profile/descriptor defines a scale. Catalog edition declared via new discovery field `iso4217_edition` (Core §7.1 + discovery schema); receiver's edition governs; mismatch logged. Token ≤8 / entitlement ≤2 / service_unit ≤4 fraction digits.
  4. **Schema layer:** `multipleOf` float checks REMOVED (N-03); per-asset_type string patterns bound scale (currency ≤3 dp structurally; exact per-currency scale is a runtime rule against the catalog — same delegation class as D1's calendar floors, covered by runtime vectors + Phase-6 harness). Zero excluded via `not: ^0(\.0+)?$`.
  5. **Transition:** amount fields dual-accept (string | legacy number without multipleOf) until the 1.12 regeneration; 68 non-crypto vectors already converted to strings; the 9 crypto vectors convert when re-signed; INV-36 pre-registered to flip legacy-number to schema-invalid at 1.12.
- **Alternatives rejected:** lexical preservation on the wire (mathematically incompatible with RFC 8785 signing); keeping numeric amounts (float multipleOf unreliability, `1500.00`→`1500` inside signed MiFID audit evidence, no path to 0/3-minor-unit currencies); dual number+string representation (two sources of truth).
- **Files:** `spec/ARSIA-State.md` (§2.1.2), `spec/ARSIA-Assets.md` (§2 per-type precision, §3.1.1 amount, §3.2.1 receipt amount, §3.3.1 reversal_amount, §6.1.1 table types, examples), `spec/ARSIA-Core.md` (§7.1 `iso4217_edition`), 5 schemas (transfer-request/receipt/reversal, mifid-audit-record, audit-record) + discovery schema + message-schema embedded examples, vectors (68 converted + ITV-573..578, INV-33..36 + 4 precision negatives re-based ITV-70/71/119/347), `test-vectors/README.md`.
- **Impact:** deterministic, validator-independent amount validation; audit evidence preserves scale inside signatures; JPY/KWD expressible. Breaking for Assets payloads (loud schema type failure post-1.12); State clients must stop asserting lexical round-trips. Migration table (`1500.00` → `"1500.00"`) queued for the migration guide.
- **Tests:** ITV-573 (JPY), ITV-574 (KWD), INV-33 (exponent), INV-34 (leading zero), INV-35 (negative), INV-36 (legacy number, activates at 1.12), ITV-575/576 (fixed-scale runtime EUR/JPY), ITV-577 (2^53+1), ITV-578 (1.0≡1), re-based ITV-70/71/119/347. Suite: 642 vectors, 0 fail, crypto 83/83, error-paths 0.
- **Residual risks:** exact per-currency scale not schema-enforced (runtime harness Phase 6); ISO 4217 edition governance is operational (declared, logged); legacy dual-acceptance window until 1.12 (tracked).

---

## DR-A07-MIN/D5 — v2 version/schema strategy (A-07 minimal slice + D5 v1 policy + X-02)

- **Decision (Core §4.1.1 rewritten):** wire version becomes **`"2.0"`**. Explicit division of labour: (1) JSON Schemas validate **exactly one minor version** (`additionalProperties:false` intentional — the schema is not the forward-compat mechanism); (2) minimal parsing accepts any `2.x` and selects the matching minor schema; (3) unknown newer minor → major-2 compatibility rules (validate known fields, accept unknown top-level/payload fields); (4) unknown fields are **preserved in the signing input and on forwarding**, ignored semantically after verification; (5) minor versions never change security-relevant field semantics; (6) unsupported major → `not_implemented` + `supported_versions`, and **v2 verification failure is never retried under v1 rules** — v1 support only as an explicitly configured compatibility profile with isolated verifier and separate conformance claims. X-02 fixed in the same edit (pattern `^(0|[1-9]\d*)\.(0|[1-9]\d*)$`).
- **Sequenced before regeneration** (owner-mandated) so vectors are generated once. Propagation of `"2.0"` to schemas/media type/examples/vectors happens in the 1.12 pass. A-07 remainder (discovery-schema extensibility, future-minor vector) in Phase 2.
- **Files:** `spec/ARSIA-Core.md` §4.1.1. Suite unaffected (prose ahead of artifacts during the construction window; reconciled at 1.12).

---

## DR-D3/D5-REGEN — v2 signing profile + wire 2.0 regeneration (A-16 executed, D5 propagated)

- **Decision executed (owner-approved D3+D5):**
  1. **Signing profile v2 (Core §5.1 Steps 2/6 rewritten):** signing input = JCS(envelope with `security` present, only the `sig` **property** removed — not null/"", not a rebuilt object); `alg`, `kid`, encryption metadata, and the D2 `authorization` binding are integrity-protected. Draft-01 compatibility note embedded; downgrade prohibited.
  2. **Staged processing pipeline (new Core §5.2 "Message Processing Pipeline"):** 13 normative steps — size limits → JSON parse → I-JSON → duplicate-key rejection → minimal security-shape check → version/profile selection → signing-input reconstruction → key resolution → **algorithm coherence** (allowlist ∩ declared alg ∩ resolved key type; `kid` must belong to `from`; never algorithm-from-untrusted-input alone) → verify → only then full schema/semantic validation → token/capabilities/compliance → processing. §5.2 Steps 3/5 rewritten accordingly; Identity §3.1 step 7 aligned; §13.2.3 rationale updated.
  3. **Wire 2.0 propagated selectively (D5):** tooling `scripts/regen_v2.py` (v2 signer/generator: EdDSA raw keys, ES256 scalar, RS256 DER; deterministic canonical bytes; verification round-trip; logs the affected set). Migration: **332 envelope vectors** → `v: "2.0"`, `root_request_id` (deterministic synthetic roots for isolated approval_decision fixtures), `retention_days`→`retention` durations, string amounts, `authorization` binding on residency vectors; **83 crypto vectors re-signed** under the v2 profile; schema-ref vectors untouched unless their schema changed. Purpose-preserving special cases: INV-08 → runtime floor skip; INV-09 → string-scale negative; INV-18/19 corrupted-signature negatives re-corrupted post-resign; ITV-405 → v2.1 forward-compat runtime vector; INV-36 activated (numeric amount now schema-invalid).
  4. **Schema flips to v2-only:** message schema `v: const "2.0"`; `root_request_id` added to all four conditional-required sets; `data_residency → require authorization`; `retention_days` + numeric floor blocks removed (message inline copy + compliance-field); amount fields string-only (5 schemas); audit-record `compliance_profile` → `compliance_profile_declared`/`compliance_profile_resolved` + `retention_source` required (45 embedded records migrated; MiFID record keeps its own field set — its declared/resolved alignment tracked in Phase 2 A-05 remainder). `validate_vectors.py` crypto check moved to the v2 profile.
  5. **Spec examples swept:** `"v": "1.0"`→`"2.0"`, media type `arsia+json; v=1`→`v=2`, `protocol_version`/version-negotiation `max` → `"2.0"` (payload-type versions deliberately untouched — payload versioning is independent of wire version, H2).
- **Evidence:** suite 645 vectors — 0 fail; `--check-crypto` 83/83 under the v2 profile; `--check-meta`/`--check-errors` clean. Affected-vector IDs logged by the regen tool (no silent caps).
- **New D3 vectors:** INV-37 (alg flip post-signing), INV-38 (kid swap), INV-39 (Draft-01-style signature rejected, no downgrade) — runtime class.
- **Deferred (tracked):** `arsia-broker-relay-audit.schema.json` retirement + re-expression of its 9 vectors as ArsiaAuditRecord `broker_relay` records → Phase 5 (prose already makes ArsiaAuditRecord normative; DR-D2); VERSIONING/CHANGELOG → Phase 8; MiFID-record declared/resolved fields → Phase 2.

---

## DR-P2 — Phase 2: remaining high findings (grouped record)

All A-findings now resolved or formally closed. Non-controversial fixes grouped per the mission's allowance; each traced below.

- **A-02:** Identity §3.1 aligned to Core §5.2 (request/response/pending/approval MUST-sign; event/error RECOMMENDED) with a new MUST-sign carve-out for compliance-relevant events (`breach-notification`, `dora/incident`, `identity/key-revocation`, on-wire audit events) — evidentiary value requires authenticated origin.
- **A-03:** strict mode normatively defined (Core §4.3.8 Rule 1): per-agent receiving-side configuration, announced as `strict_compliance: true` in discovery (declaration informative; receiver config governs), affects only the rules that reference it, agent-wide scope. Discovery-schema field lands in Phase 5.
- **A-04:** the four certificate codes registered as standard codes in Core §11.2 (HTTP 401, non-retryable) with a registry note; message-schema enum already carried them.
- **A-06:** new `counterparty_owner_id` audit-record field (State §7.1 + schema): both parties' owners now recordable; unresolvable counterparty → agent-id recorded + correction-record backfill (append-only preserved). Identity §4.1 MUST is now implementable and references the concrete fields.
- **A-07 (full):** the §4.1.1 version-handling model (DR-A07-MIN) is the complete resolution: schemas are exact-per-minor by design; wire tolerance is a runtime behaviour; forward-compat vector ITV-405 (v2.1) reclassified runtime.
- **A-08:** hard mutual exclusivity chosen (Core §4.4.7 rewritten): exactly one content field, extra or missing → `invalid_request` — aligning prose to the schema's existing `not/anyOf` and eliminating receiver divergence over which content is processed. Deliberate hardening vs Draft-01's warn-and-pick.
- **A-09:** schema-level `high-risk → required human_oversight` clauses removed from both schema copies; Rule 3 checks the EFFECTIVE mode (per-message or profile default). ITV-421 reclassified runtime (profile-default path); new ITV-579 (no profile → reject) covers the negative; explicit-value and conflict cases live in existing Rule-6 vectors + Phase-6 harness.
- **A-10:** MiFID audit record `updated_at` (in-place mutation) removed from §6.1.1 — lifecycle progress recorded by appended correction/completion records via `original_audit_id`, per §6.1.2/State §7.2. Schema `updated_at` removal in Phase 5 sweep.
- **A-11:** subsequent-receipt delivery defined (Assets §3.2.1): each later receipt is a new `request` (`arsiaprotocol.assets/transfer-receipt`) from processor to requester carrying `original_request_id`, idempotency key `receipt:{payment_reference}:{status}`, mandatory ack, retry per §11.3, `delivery_failed` audit + status-URL fallback, terminal-status rules incl. escrow. Draft-01's undeliverable "second response" eliminated.
- **A-12:** new self-asserted `regulated_entity {regulated, regimes[]}` IdentityRecord field (Identity §1.2 + schema); Assets §6.1 trigger reformulated onto it with a deterministic fallback (absent on both parties → condition met only under resolved MIFID-II profile). Self-assertion limits stated.
- **A-13:** precedence defined: explicit `compliance.audit_required: true` overrides the session-scope no-audit default (compliance-first); both paths stated in §1.1, §1.5 table, §8.3 rule 4. Both-path runtime tests queued in the Phase-6 harness.
- **A-14:** Core §13.1 extended with six adversaries (broker bypass — mitigated by mandatory attestation; compromised approver; wrongful PURGE; escrow abuse; recipient residency evasion — declared residual; envelope/token/attestation splicing — closed by hash binding), each with mitigations AND explicit residuals; Routing §5.1 item 4 SHOULD→MUST resolved (recipient in-zone processing MUST, verified operationally, reject when unable).
- **A-17/A-18 (full):** §6.5 completes the trust anchor; §5.2 Verification Caching rewritten: single 3600 s cache ceiling (resolving the internal 1 h/24 h clash), JWKS-removal as authoritative revocation signal, `arsiaprotocol.identity/key-revocation` emergency event, JWKS-fetch-timestamp recording in audit records for compromise-window accounting.
- **A-19:** PSD2/SCA claims requalified (Assets §5.2/§6.3): protocol provides technical controls (signed, capability-gated, chain-bound approval) an operator MAY use in an SCA design; payer authentication, element independence, dynamic-linking presentation, and exemption conditions are operator-side; "subject to legal review" stated. No protocol-level SCA satisfaction claim remains.
- **A-21:** GDPR absolutisms replaced by qualified, conditional language (State §7.2): hashing = pseudonymisation where linkable; agent identifiers may relate to persons; Art. 17(3)(b) assessed case-by-case; Art. 30 documentation; "not legal advice" stated. Core §13.3's "no PII" claim aligned in Phase 3 sweep.
- **A-22:** normative tamper-evidence scope statement (State §7.2): detected (mid-chain modification/removal/reordering vs an independently held head) vs NOT detected (owner rewrite, tail truncation, write-time omission, fork); overclaiming prohibited; external anchoring permitted and documented when used; the "REQUIRED in a future version" deferral removed.
- **Suite:** 646 vectors, 0 fail; crypto 83/83; error-paths 0. Files: Core, Identity, State, Assets, Routing + audit-record/identity-record/compliance-field/message schemas + vectors/README.

---

## DR-P3 — Phase 3: medium and low findings (grouped record)

All mediums resolved except deliberate deferrals (M-15 → H2/Phase 4; M-18 runner → Phase 6; X-07 RTM regeneration → Phase 6). Individually:

- **M-02:** 731 chosen (worst-case leap-day doctrine, consistent with 1827/1096): DSA-VLOP `retention_minimum` → `"P731D"` in State §6.6 tables + rationale; catalog updated in the same pass (Phase 5 verifies).
- **M-03:** `kid` unified on Identity §2.2's general form (`[a-zA-Z0-9][a-zA-Z0-9_-]*`); Core §4.3.5/§7.3 `{keyN}` sequential-only contract removed.
- **M-04:** Identity onboarding/audit texts corrected to `capabilities_supported` and `/.well-known/arsia`.
- **M-06:** Routing §4.1 lifecycle events classified as the **operational routing log** — normatively excluded from the canonical `ArsiaAuditRecord` enum; only `broker_relay` crosses into the canonical trail.
- **M-07:** escrow taxonomy corrected (one initial, one intermediate DISPUTED, two terminal RELEASED/RETURNED; cancellation is a path to RETURNED); §4.3 audit tables renamed to base fields (`record_id`, `processed_at`).
- **M-08:** scope table row fixed (agent readable by owner + grantees); normative guidance added for `shared` vs `agent`+GRANT (symmetric co-ownership vs revocable audited delegation; prefer grants when in doubt).
- **M-09:** reserved-key examples migrated to `arsiaprotocol.meta/…`.
- **M-10:** Routing §2.1.2 aligned to Core §8.1 — `approval_decision` never a synchronous inbox response.
- **M-11:** residency codes closed: ISO 3166-1 alpha-2 ∪ registry (`"EU"`); custom codes prohibited; Draft-01's self-contradictory 2-4-char rule removed; Core §4.3.6.2 aligned.
- **M-12:** envelope `id` accepts both hex cases (matching prose + `correlation_id`); ITV-407 flipped to valid.
- **M-13:** wildcard audience removed; router-as-recipient pattern documented instead.
- **M-14:** item 1 (Identity §6.4.3 → Core §11), item 3 (STATE-13 → Core §4.3.8 Rule 4, via DR-D1), item 4 (compliance-field `$comment` → §4.1.1 version model), item 5 (risk-level 180-day claim replaced by "floors come only from profiles"); item 2 (State §11.5) NOT-REPRODUCED in this tree.
- **M-16:** onboarding decision moved off the `approval_decision` intent → dedicated payload `arsiaprotocol.onboarding/decision` over a `request` with `original_request_id` + idempotency; oversight contract of Actions §3.3 no longer violated.
- **M-17:** universal rule chosen — every receipt has an audit record (`audit_id` REQUIRED ⇒ record exists), platform-default retention outside profiles.
- **M-20:** `pending-approval-args.risk_level` minimum → 0.
- **M-21:** one async mechanism, two surfaces (HTTP 202+Location ≡ envelope `status_url`; identical URLs when both; envelope surface only on WebSocket).
- **M-22:** State §2.1.10 item 2 → SHOULD-set + MUST-warn (no hard rejection), matching the schema's runtime delegation; `results/` half superseded (dir empty).
- **M-23:** `unacceptable-risk` removed from the per-message enum (prose + both schema copies); ITV-137 flipped to invalid.
- **M-25 (HIGH):** signed envelope `idempotency.key` is authoritative; mismatched header ignored (or strict-rejected) but never used for dedup; header-only requests get best-effort courtesy dedup with no replay-defence claims.
- **M-26:** at-least-once = retries (§11.3); idempotency = dedup, not a delivery guarantee.
- **M-27:** `dora_incident` → **`ict_incident`**, payload `arsiaprotocol.ict/incident`; trigger reworded to incident-candidate criteria (persistent/multi-operation/policy-directed — a single retried timeout is not a candidate); classification remains the operator's DORA function (§6.2.4). One crypto vector re-signed via `regen_v2.py`.
- **M-28/M-29:** anchors verified in-tree (confidence = Actions §5.2; sandboxing = Actions §4.4); the addendum's wrong anchors noted in the findings matrix (addendum file not in repo).
- **M-30:** role model fixed: ARSIA `owner`/`deployer_id` are accountability/infrastructure roles; EU AI Act provider/deployer mapping is many-to-many and per-deployment (owner is typically the AI Act deployer; the vendor-provider may be absent from the record); Art. 26(1) claim corrected; subject-to-legal-review stated.
- **M-24** already fixed upstream; **M-01/M-05/M-31** resolved in Phase 1 (D1/D2).
- **Lows:** X-01 (org-segment prose), X-02 (pattern, via DR-A07-MIN), X-03 (`arsiaprotocol.` wording), X-04 (§10.4 rewritten; authenticated encryption defined in place), X-05 (personal or sensitive), X-06 (stale phrase gone with §7.4 rewrite), X-08 (English SHOULD + `details.localized_description`); X-07 → Phase 6.
- **N-06:** Core §4.3.6.8 now lists all 16 legal bases (6×Art. 6(1) + 10×Art. 9(2)) with the sensitive-data rule.
- **Also:** Core §13.3 "identifiers contain no PII" qualified (A-21 alignment).
- **Suite:** 646 vectors, 0 fail; crypto 83/83; error-paths 0.

---

## DR-H — Hypotheses H1–H4

- **H1 (CONFIRMED → mechanism defined).** Extension profiles use **reverse-domain namespacing** (`com.example.healthcare-profile`), mirroring payload-type extensibility: org-controlled namespaces eliminate cross-org collision without a central registry. Standard profiles remain bare uppercase names extended only by spec revision. Publication = a catalog document conforming to `arsia-compliance-profiles.schema.json` at a stable HTTPS URL; discovery/recognition = `compliance_profiles_supported`; unknown names follow Rule 1 (warn+GDPR-STANDARD default / strict reject); versioning = renaming (existing doctrine). *Alternative considered:* a central IANA-style registry — rejected for Draft-02 (governance overhead, single point of coordination; the namespace approach is additive and a registry can be layered later without breaking names). Core §4.3.8 Rule 1 rewritten.
- **H2 (gaps fixed, mechanism preserved).** (i) Deterministic default: absent `payload.version` = exactly `"1.0"` — Draft-01's "latest known to the receiver" removed as non-deterministic. (ii) Proactive discovery: new `supported_versions` array on the ActionDescriptor (prose + descriptor schema + discovery-response copy); migration coexistence now advertised in ONE descriptor entry (fixing the M-15 aggravator — Draft-01 required separate entries the descriptor could not express). (iii) §2.4 evolution semantics (bump rules, `not_implemented` + `supported_versions`) declared uniform for ALL payload types. Payload-version pattern tightened (X-02 family).
- **H3 (CONFIRMED → no new mechanism).** After DR-B01, causal reconstruction uses exactly two generic fields (`correlation_id` = immediate parent, `root_request_id` = interaction root) plus a small closed set of typed refs for non-reply relations (`original_request_id` — payload self-containment, MUST equal root; `original_audit_id` — audit corrections/reversals/escrow chains; `payment_reference` — asset lifecycle; `breach_id` — notification updates). Assessment: every relation in the six documents is now reachable via root+correlation walk or one documented typed ref; a generic supersedes/derived-from mechanism would duplicate these without new expressive power. Decision: **no additional mechanism in Draft-02**; revisit only if a new primitive introduces a relation the current set cannot express.
*(DR-P5 below; H4 continues)*

## DR-P5 — Phase 5: full schema/profiles pass (grouped record)

- **N-04:** discovery-response's extra descriptor rule reconciled — the blanket "no reserved capabilities in application actions" rule was WRONG on both sides: replaced by **registry enforcement** (reserved-prefix capabilities in `required`/`optional_capabilities` must be members of the Actions §1.4 registry; registered ones like `audit.read` are legitimate). Embedded descriptor copy replaced by `$ref` to the standalone schema (drift class eliminated). ITV-281 flipped invalid (unregistered reserved name); ITV-53 sample updated to registered names.
- **Dedup:** message schema's inline compliance object replaced by `$ref arsia-compliance-field.schema.json` (single source; envelope-level cross-field rules remain in the message schema's `allOf`).
- **N-05:** all 31 `$id`s unified to `https://arsiaprotocol.org/schemas/v2.0/<filename>` so relative `$ref`s resolve identically under filename-based and strict RFC 3986 resolvers — verified by validating CTV-01 through the `referencing` library with `$id`-only registration.
- **Broker-relay-audit retirement (DR-D2 deferral closed):** `arsia-broker-relay-audit.schema.json` deleted; audit-record schema gains the `broker_relay` extension branch (7 required fields per Routing §7.4.2); the 9 legacy vectors converted to full `ArsiaAuditRecord` form (ITV-44 kept as the enum negative).
- **M-02 propagation:** catalog DSA-VLOP → `"P731D"`; Routing §7.4 list aligned.
- **N-07** (settled_at description → SHOULD), **N-08** (dead allOf removed), **N-09** (broker-entry timestamp → suite-wide `rfc3339-ms-utc`), **A-10 schema side** (`updated_at` removed from mifid schema + 6 vectors).
- **Vector-format hygiene:** ITV-137 normalized to hybrid form; ITV-407 stray key removed (meta-schema now clean).
- **Verification:** 646 vectors — 0 fail; meta 0; error-paths 0; crypto 83/83; 31/31 schemas meta-valid; catalog validates (0 errors).

---

*(DR-P7 below; H4 continues)*

## DR-P7 — Adversarial review: 17 verified findings, all fixed

An independent adversarial agent reviewed the full Draft-02 delta against the mission checklist. It confirmed the automated suites green and the major mechanisms consistent, and found 17 real defects (3 blocking, 3 high, 6 medium, 4 low, 1 nit) — all fixed in the same phase:

1. **(blocking)** `retention_days` survived in state-entry/state-operations/action-descriptor schemas (with clamp-doctrine descriptions) — renamed to `retention` durations with reject doctrine; 18 vectors converted; INV-42 legacy negative added.
2. **(blocking)** Day-integer retention statements in State (§ tables, §7.3 summary, a conformance expectation) contradicted `P6M`/`P731D` — all converted; day-integer anti-regression added to `check_consistency.py`.
3. **(blocking)** Draft-01 signing profile survived in Core §4.3.5 `sig` definition, Routing §1.2.2 step 3, Identity CHECK-02 and an Identity informative note — all rewritten to "only `security.sig` removed".
4. **(high)** Assets §2.1 still imposed the universal 2-dp rule with provider rounding — replaced by the fixed-ISO-4217-scale rule (no rounding, ever).
5. **(high)** Spec example envelopes missing `root_request_id`/`authorization` — programmatic sweep fixed all (verified zero remaining).
6. **(high)** `strict_compliance` missing from discovery schema + §7.1 table — added.
7. **(medium)** Schema didn't prohibit `root_request_id` on `intent: request`; two promised negatives missing — schema clause + INV-40/41 added; harness R7 extended with the pending args/root mismatch case.
8. **(medium)** compliance-field still `additionalProperties: true` with stale description and `retention_days` examples — closed (`false`), `clock_skew_seconds` explicitly registered (per-message echo, profile governs), examples regenerated; Core §975 note aligned.
9. **(medium)** Message-schema `examples` were v1.0 with `retention_days` — regenerated from v2 vectors.
10. **(medium)** FAQ still described `arsiaprotocol.*` scopes as functional — rewritten to condition 3.
11. **(medium)** VERSIONING.md still declared Draft-01.1/wire 1.0 — updated coherently with the CHANGELOG.
12. **(medium)** Promised harness cases absent — R11 (issuer trust: unknown issuer, key-from-token-URL, audience policy, alg allowlist), R12 (session+audit_required precedence, both paths), R13 (revocation under cache: ceiling refresh, stale key, unknown kid) added.
13. **(low)** Identity "v1.0" algorithm line fixed. 14. **(low)** INV-08 description rewritten to duration terms. 15. **(low)** Core §8.1 reply construction now names `root_request_id`. 16. **(low)** Three integration-class untested behaviours (subsequent receipt, tamper detection, DORA discrimination) recorded as documented non-tested in the skip classification. 17. **(nit)** ASSETS-01 amounts quoted as strings.

**Post-fix verification:** 649 vectors — 0 fail; meta + error-paths clean; crypto 83/83; `check_consistency.py` ALL PASSED (now incl. day-integer guard); `runtime_harness.py` R1–R13 ALL PASSED. The reviewer's "verified clean" list (correlation model, B-06 enums, capability matching, amounts, ict_incident, version sweep, D2 artifacts, token adversarial cases, Phase-5 promises) stands.

---

- **H4 (CONFIRMED → deliberately deferred).** Single-axis temporality stands. Use cases for transaction time (bitemporality) are real but narrow: regulatory disputes reconstructing "what did the system believe at T1 about T0". Costs: a second axis on every entry + SNAPSHOT (`as_of` × `known_at`), wire and storage growth, migration of version history — disproportionate for Draft-02. Partial mitigations already present: the audit record's `timestamp` (event) vs `processed_at` (ingestion) distinction, and append-only version history ordered by `updated_at`, allow coarse reconstruction of knowledge states. Decision: NOT implemented; recorded as a known limitation (Phase 8) with the mitigation guidance; SNAPSHOT semantics documented as valid-time only.

## DR-P8 — Evidence-level double check: secondary-site residuals (2026-07-29)

**Trigger:** an owner-requested double check verified every claimed resolution against
the tree (4 independent verification passes over ~60 findings). Pattern found: fixes
had landed at the primary site while secondary sites restating the old rule survived.
All residuals below are now fixed; each was a localized edit, no new wire decision.

**Material fixes:**
1. **M-25** — Routing §2.1.1 optional-header table still said the unsigned
   `Idempotency-Key` header "overrides" the envelope field (citing §10.4 for the rule
   §10.4 forbids) → rewritten: envelope authoritative, mismatching header ignored or
   rejected. The anti-replay note claimed for Core §13.2.2 did not exist → added.
2. **A-19** — "satisfies PSD2 SCA at the protocol level" survived in Assets §1.1.8 and
   §6.3 (incl. "satisfy the legal requirement" in §6.3.1) → requalified consistently
   with §5.1.2 (controls that can serve as SCA elements; legal determination is the
   PSP's; subject to legal review).
3. **M-15** — Actions §2.4 "Version negotiation" still mandated "latest supported
   version" for absent `payload.version` → deterministic `"1.0"` per Core §4.4.2.
4. **A-18** — the Core §5.2 MUST to record the JWKS fetch timestamp had no schema
   field → `jwks_fetched_at` added to arsia-audit-record (runtime-required,
   schema-optional) + State §7.1 row; Identity §2.5/§3.1 still carried the
   refetch-on-failure-only revocation model → aligned to the Core model (removal =
   authoritative signal, 3600 s ceiling, key-revocation event referenced).
5. **M-30** — Identity §4.1 "This satisfies EU AI Act Art. 26(1)" and the
   "owns and operates" wording in §1.1 Layer 3 / `owner_id` / identity-record schema →
   requalified per the §4.4 role model.
6. **N-06** — 4 of 16 `legal_basis` values in Core §4.3.6.8's Art. 9(2) enum summary
   did not match the schemas → corrected to the canonical values.
7. **N-07** — receipt `settled_at` had three contradictory rules (schema description
   REQUIRED vs prose SHOULD vs §6.1.1 OPTIONAL) → schema description aligned to the
   prose SHOULD, cross-field rule marked runtime.
8. **N-10/D4** — Assets §2.5 registry table still said "Max Decimals: 2" for currency
   (breaks KWD/BHD, misstates JPY); request-schema description still cited
   `multipleOf`/≤2dp → both aligned to the fixed ISO 4217 scale rule.
9. **M-07** — escrow §4.3.2/3/4 still used `audit_id` (self-contradictory after
   §4.3.1's rename) → `record_id`, with `original_audit_id` descriptions corrected.
10. **M-16** — the onboarding decision remained `intent: approval_decision` in the
    schema description, Identity §9.3, the §7.6 example (`payload.result` on a
    request), and vectors ITV-03/04/482 (plus schema-ref ITV-38/130/131/474) →
    migrated to the §7.6 contract: `request` + `payload.args` (with
    `original_request_id`), `arsiaprotocol.onboarding.evaluate`, `expires_at`;
    onboarding-decision schema now requires `args`; ITV-03/04 re-signed; audit
    `event_type: approval_decision` kept as the audit label with an explicit note.
11. **X-07** — four RTMs carried two contradictory Coverage Gaps sections → stale ones
    removed. In Assets the stale Draft-01 "no enforcement" listing had been left in
    8-column form and was double-counted by the parser: **91 duplicate rows removed;
    published totals were inflated — true counts are 1903 rows / 1109 MUST+MUST_NOT
    (was 1994/1153), Assets 262 (was 353)**; Assets coverage summary regenerated.
12. **Vectors** — ITV-539's description asserted the abolished clamp doctrine
    (`max()`) as a MUST → rewritten to the §8.3 Rule 2 precedence+reject model; 15
    descriptions narrating `retention_days` rewritten; **ITV-559 declared
    `retention: "P730D"` under DSA-VLOP (floor P731D — a "valid" vector a conformant
    runtime rejects)** → P731D.

**Minor fixes:** X-02 (6 remaining loose version patterns tightened in message +
discovery schemas), X-04 (duplicated sentence removed), M-08 (guidance blockquote had
been inserted mid-table, breaking the §1.5 markdown → moved below), M-21 (Actions
§4.3 back-reference to the Core §8.1 single-async rule), M-11 ("pending Phase 3"
marker → closed-registry citation), M-19 (extension table used enum names that do not
exist: `state_grant_revoked`→`state_revoke`, `state_snapshot` removed,
`asset_transfer_*`/`escrow_*`→`asset_transfer`+`sub_type`; operational-log
cross-reference added), M-03 (relay-attestation `kid` pattern aligned to the common
kid-format), A-21/A-22 (leftover absolutist phrases qualified in Core §13.3, the Actions
"Regulatory satisfaction" note, State §11.2), M-27 (stale Assets RTM row), A-02 (Core §5.2 now cross-references
the Identity §3.1 compliance-event MUST-sign carve-out), M-17/N-03 (stale schema
descriptions), message-schema description "v1.0" → "wire version 2.0".

**New CI guards:** `check_consistency.py` now also fails on (a) `retention_days` in
vector descriptions, (b) duplicate RTM requirement IDs — the two classes that let
residuals 11-12 survive. Prose↔prose contradiction sweeps remain manual (the original
CI limitation the Draft-01 audit noted; partially compensated by `check_links.py` and
`extract_examples.py`).

**Post-fix verification:** 649 vectors — 0 fail; meta + error-paths clean; crypto
83/83; `check_consistency.py` ALL PASSED (incl. the two new guards);
`runtime_harness.py` R1–R13 ALL PASSED; `extract_examples.py` 71 full + 5 fragments,
0 failures; `check_links.py` 1,326 refs, 0 dangling; `rtm_counts.py` 1903 rows / 1109
MUST+MUST_NOT (deduplicated).

## DR-P9 — Prose-consistency guards: RTM drift linter + enum parity (2026-07-29)

**Motivation.** The remaining CI blind spot was prose↔prose contradiction (the class
behind B-02, B-03, M-25, the Routing §5.1/§5.2 clash). Root cause is restatement
drift, which is mechanically detectable in two forms without semantic analysis.

**Added to `check_consistency.py` (no new tool; same file, same CI step):**
1. **Prose-enum ↔ schema-enum parity** — the prose enum listings for `legal_basis`,
   `human_oversight`, `ai_system_classification` (per-message), audit `event_type`,
   and the §11.2 error-code registry table are extracted and must be set-equal to
   the corresponding schema enums (largest enum = authority; conditional sub-enums
   must be subsets). Re-guards the N-06 / B-06 / M-23 / M-06 / A-04 classes.
2. **Cross-document RTM drift linter** — requirement pairs across the six RTMs with
   near-identical normalized text (token-Jaccard ≥ 0.8) but diverging modal
   strength/polarity or diverging embedded values (numbers, durations, quoted
   enums) fail the build. A synthetic self-test (one value-drift pair, one
   modal-drift pair) must be flagged on every run — a dead detector fails loudly.

**First run found a real contradiction** (survived the audit, Draft-02, DR-P7,
DR-P8, and the closure pass): Core §8.2 "client **MUST** send a heartbeat frame
every 30 seconds" vs Routing §2.2.2 Phase 4 "client **SHOULD** send…". Resolution:
the MUST governs (Core owns the WebSocket binding; the server idle-timeout depends
on the heartbeat) — Routing §2.2.2 and ROUTE-§2.2.2-12 aligned, with the Draft-01
note convention used for the §5.1/§5.2 clash.

**Limits (recorded honestly).** The linter sees drift between *restatements*; a
contradiction written once in two genuinely different phrasings (like B-05's
inconsistent authorization model) remains a matter for adversarial review and,
ultimately, independent-implementation interop. Deliberately NOT added: LLM-based
contradiction jobs (CI cost/flakiness) and a spec-toolchain migration — revisit
when a second independent implementation or PR volume justifies them.

**Verification:** full battery green — 649 vectors / 0 fail, crypto 83/83,
`check_consistency.py` ALL PASSED (49 checks incl. the self-test), harness R1–R13,
examples 71+5/0, links 0 dangling.
