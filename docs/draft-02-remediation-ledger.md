<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Draft-02 Remediation Ledger

## 1. Purpose and baselines

This ledger tracks the remediation of the Draft-02 (wire 2.0) audit findings:
the owner decisions that govern it, the regulatory citation verdicts, the
runtime-only vectors, and the declared guarantees still lacking evidence.

- **Audit baseline:** `51610ac`, permanent. It was rewritten from `fb5a875` with
  an identical tree (`9d86a7e`), verified by an empty
  `git diff fb5a875 51610ac --stat`. All audit line references resolve against
  this tree.
- **Execution baseline:** recorded per cycle in the cycle register (§2).
- **Update rule:** the ledger is updated in the same commit as the fixes it
  tracks.
- **Cycle identifiers:** rows cite cycle identifiers (`C0`, `C0.5`, `C1`, …)
  instead of self-referencing SHAs. A cycle's commit SHA is recorded in the
  cycle register by the next cycle.
- **Sources:** the owner's remediation brief for `C1`,
  `docs/draft-02-design-record.md`, and the regulatory verification report
  `draft-02-regulatory-verification-fb5a875.md` (held outside this repository
  with the EUR-Lex source texts). A field with no value in those sources reads
  "pending".
- **Counts:** reported per register. Registers are never summed together.

**Legend.**
- **Triage status:** CONF = confirmed; PART = partially confirmed; INT =
  interpretive conflict; UNV = unverified; new = raised after triage.
- **Class:** 1 = cross-spec conflict; 2 = reference algorithm vs prose; 3 = prose
  vs external standard; 4 = declared guarantee without coverage; E = editorial.
- **Remediation state:** open | implemented-pending-closure (IPC) | closed.

## 2. Cycle register

| Cycle | Scope | Execution baseline at start | Commit(s) | Status |
|---|---|---|---|---|
| C0 | Audit + triage + regulatory verification | `51610ac` (audit baseline) | none (read-only) | closed |
| C0.5 | Decision-independent verifier repair | `51610ac` (audit baseline; executed on the pre-rewrite `fb5a875`, identical tree) | `260ac73` ("fix: repair decision-independent reference verifiers (step 0.5)") | implemented, closure verification pending |
| C1 | Remediation tracking artefacts | `63a233b` | `e77c0ca` ("docs: add Draft-02 remediation ledger and design record") | closed |
| C2 | Regulatory and standards citation alignment (28 citation defects + A-69) | `e77c0ca` | `a8e9930` ("fix: align regulatory and standards citations with official texts") | implemented; per-item closure in §4, §5 and §9 |
| C3a | Prose ↔ schema parity (A-1, A-2, A-3, A-9, A-10, A-27, A-59) | `a8e9930` | `aa5547d` ("fix: align audit, compliance and onboarding schemas with prose (C3a)") | implemented; per-item closure in §4 and §10 |
| C2.1 | Regulatory currency results applied (OD-4; A-71, A-72, A-73) | `aa5547d` | this commit | implemented; per-item state in §4, §5 and §11 |

## 3. Decision register

| ID | Subject | Proposal | Orchestrator review | Owner approval | Design record |
|---|---|---|---|---|---|
| DR-0 | Cross-cutting requirements | Four requirements apply to every decision. 0.1: one resolution component, defined once in a dedicated Core section. 0.2: a profile-imposed control is attributed to the profile, not the regulation (A-69). 0.3: a vector resting on a MAY declares its posture. 0.4: the 32 runtime-only structural failures are classified individually before any edit. | concurred (record preamble) | 2026-09-26 | §DR-0 |
| DR-1 | Authority to require oversight (Q1) | Option b: layered authority with one resolution procedure. Effective obligations are computed from authenticated, authorized sources, and the descriptor is no longer a veto over oversight. Rejected: c. | concurred (P/R/A) | 2026-09-26 | §DR-1 |
| DR-2 | Post-execution review modes (Q2) | Option a: a complete minimal post-execution review mechanism (reviewer, deadline, signed decision, pending/completed/overdue). Rejected: b, c. | concurred (P/R/A) | 2026-09-26 | §DR-2 |
| DR-3 | High-risk oversight enforcement (Q3) | Option c: both layers rest on the same semantics. For high risk, `not_required` never satisfies oversight, even when it comes from a profile default. | concurred (P/R/A) | 2026-09-26 | §DR-3 |
| DR-4 | Profile composition for multi-regime agents (Q4) | Option a: compare obligations per axis, not profile names. One declared profile plus per-axis requirements of traceable origin. Rejected: b, c. | concurred (P/R/A) | 2026-09-26 | §DR-4 |
| DR-5 | Audit hash chain (A-8) | Option a: the chain commits to the full previous record, the previous hash and the chain context (RFC 8785). Corrections are new records. | concurred (P/R/A) | 2026-09-26 | §DR-5 |
| OD-1 | Remediation ledger | The ledger lives in the repository as Markdown, is updated with the fixes, and is kept in publication. | concurred (orchestrator) | 2026-09-26 | — (operational; not in design record) |
| OD-2 | Commit policy | Commits go on the work branch only, never on main, and are never pushed. Signed-off-by is mandatory, no tool trailers are allowed, and subjects follow Conventional Commits. | — (owner instruction) | 2026-09-26 | — (operational; not in design record) |
| OD-3 | EU-law verification source | EUR-Lex is the only source for EU-law verification. | — (owner instruction) | 2026-09-26 | — (operational; not in design record) |
| OD-4 | Currency of the legal source | Verify the wording applicable on the reference date, using the pertinent EUR-Lex consolidation and checking for later amendments and corrigenda not yet incorporated. Record the date of consultation, the version consulted and the relevant dates of application. In the absence of a consolidation, reconstruct the applicable wording from the original act and the pertinent amending acts and corrigenda. Distinguish entry into force from application, including transitional provisions. The original text suffices when it is confirmed that the relevant provision remains applicable without amendments or corrigenda affecting the conclusion; an act amended in another matter does not by itself invalidate the evidence for the provision at issue. | concurred (orchestrator) | 2026-09-28 | — (operational; not in design record) |

Rows: 10 (6 DR, 4 OD).

## 4. Findings register

"Dependencies / remediation" reproduces the Appendix column verbatim.

| ID | Cl | Triage status | Disposition | Remediation | Closure criterion | Closure evidence obtained | Dependencies / remediation | Cycle/commit |
|---|---|---|---|---|---|---|---|---|
| F-1 | 1 | CONF | per DR-3, DR-1 | open | Aligned quotes (Core Rule 3, State §6.2, Actions §3.7) + executed high-risk/not_required vector | pending | DR-3, DR-1 | pending |
| F-2 | 2 | CONF | pending | IPC | Harness shared-cache two-call test, revoked kid, reject/reject | harness R13 (C0.5) | IPC, C0.5 | C0.5 / 260ac73 |
| F-3 | 3 | CONF | pending | open | Core §5.1 text citing UTF-16 code units + signed vector with non-BMP keys | pending | prose cycle; prerequisite of DR-5 | pending |
| A-1 | 1 | CONF | pending | closed | Schema validation passing records built literally from Actions §3.5 (1-4, expiry) | Actions §3.5 Records 1-4 and the expiry record, built literally from the prose tables, validate (ITV-581..585); INV-46 (decision missing) rejected (§10) | prerequisite of DR-5 | C3a |
| A-2 | 1 | PART (State §7.4 l.3093 is a query parameter, not a record field) | State §7.4 `compliance_profile` is a query-parameter name, not a record field: name unchanged; the filter is defined as matching `compliance_profile_resolved` (owner decision 2026-09-28) | closed | Schema validation of Rule 7, deployer_id, cancellation records; CHECK-04/STATE-15 names aligned | Routing §7.4.2 record incl. broker_agent_id (§7.4.2 example + base fields; INV-48), deployer_id (ITV-588) and cancellation (ITV-586; INV-47) records validate; CHECK-04/STATE-15 aligned (§10) | prerequisite of DR-5 | C3a |
| A-3 | 1 | PART (delivery_failed sub-claim interpretive) | `delivery_failed` is an operational routing-log event (Routing §4.1 audit classification note), not a canonical `ArsiaAuditRecord` event_type; not added to the enum | IPC | Schema validation of compliance_warning/oversight_timeout records, or disposition placing them outside the canonical trail | `compliance_warning` added to prose and schema enum and validated (ITV-587). Gap: `oversight_timeout` suspended — it is one of the three `required_within_24h` definitions that DR-2 replaces (§10) | — | C3a (partial) |
| A-4 | 1 | PART (holds: post-execution window undefined) | per DR-2 | open | Aligned quotes for one within_24h evidence event + defined post-execution mechanism; executed C-09 | pending | DR-2 | pending |
| A-5 | 1 | CONF | pending | open | Aligned State §8.2.1 / Actions §1.2 quotes + executed reserved-wildcard vector | pending | — | pending |
| A-6 | 1 | INT (Core §6.4 names Actions §1.2 the single rule) | Core §6.4 names Actions §1.2 the single rule | open | Disposition + editorial alignment of Identity §3.2 step 6; ITV-566 executed | pending | — | pending |
| A-7 | 1 | CONF | pending | open | Aligned PURGE/retention quotes (Core §13.1 #9, State §3.2.2/§5.3.2) | pending | DR-4 axis rules | pending |
| A-8 | 1 | CONF | per DR-5 | open | New chain construction + claim quotes; executed tamper test on a non-hashed field | pending | DR-5; A-1, A-2, A-59, F-3 | pending |
| A-9 | 1 | PART (extras limited to registered fields) | pending | closed | Schema description consistent with keyword; validation of declared extension behaviour | Core §4.3.6 note and schema description now state the registered-fields reading; additionalProperties:false kept; INV-49 (unregistered member) rejected (§10) | — | C3a |
| A-10 | 1 | CONF | pending | closed | Assets §5.2 example validates as printed | Assets-only summary requirement removed from the message schema; the Assets §5.2 example, wrapped in an envelope, validates; ITV-400/401 aligned (§10) | — | C3a |
| A-11 | 1 | CONF | per DR-1 | open | Aligned denied/expired response form; ASSETS-06 executed | pending | DR-1 | pending |
| A-12 | 1 | PART (risk_level sub-claim fails) | per DR-1 | open | Aligned quote defining trigger source relative to Actions §3.7 | pending | DR-1 | pending |
| A-13 | 1 | CONF | per DR-1 | open | Aligned Identity §7.3/§7.7 vs Actions §3.7 quotes | pending | DR-1 | pending |
| A-14 | 1 | INT (Assets l.1855-1858 checks token capabilities) | Assets l.1855-1858 checks token capabilities | open | Disposition + executed vector with token lacking transfer.approve | pending | DR-1 (touches, per design record) | pending |
| A-15 | 1 | PART (rules scoped to ESCROWED) | pending | open | Explicit arbitration exception in Assets §4.1 + dispute vector | pending | — | pending |
| A-16 | 1 | PART (Rule 6 vs §2.3.3 interpretive) | pending | open | Aligned Rule 5/step 7 quotes; disposition on Rule 6 scope | pending | — | pending |
| A-17 | 1 | CONF | pending | open | Aligned 409/Retry-After quotes (Routing §3.2/§4.1.8, Core §11.3) | pending | — | pending |
| A-18 | 1 | PART (literal only at Identity l.526, Core l.2002) | pending | open | Profile-aware tolerance in each timestamp check; ITV-545/546/547 executed | pending | — | pending |
| A-19 | 1 | PART (step 2 does check the range) | pending | open | Aligned step 3 quotes; discovery example validated with consistent versions | pending | — | pending |
| A-20 | 1 | CONF | pending | open | Appendix A.1 note aligned with §5.1 Step 2 | pending | F-3 | pending |
| A-21 | 1 | CONF | pending | open | Identity §1.1 references Core §6.6 resolution | pending | — | pending |
| A-22 | 1 | PART (step 9 Ed25519-only holds) | pending | open | Identity §3.1 step 9 aligned; ES256 vector executed | pending | — | pending |
| A-23 | 1 | CONF | per DR-4 | open | Per-axis composition quote; disposition for multi-regime agents | pending | DR-4 | pending |
| A-24 | 1 | CONF | pending | open | Aligned version-reset quotes (State §2.1.12/§2.4) | pending | — | pending |
| A-25 | 1 | CONF | pending | open | Aligned arithmetic; ACTIONS-10-style count assertion for N>1 | pending | — | pending |
| A-26 | 1 | CONF | pending | open | Aligned CHECK-04 / State §7.4 response shape | pending | — | pending |
| A-27 | 1 | PART (§7.8 informative) | pending | closed | Schema minItems aligned with prose (or relaxed prose); §7.8 scenario validated | Identity §7.6 relaxed to the intended behaviour (effective_capabilities non-empty; sub-lists may be empty); §7.8 scenario validates (ITV-589); schema unchanged (§10) | — | C3a |
| A-28 | 1 | INT (State qualifies its own claim) | State qualifies its own claim | closed (C2); currency confirmed 2026-09-28 (via V-14) | Disposition; State §6.3 opening sentence rewritten via V-14 | V-14 rewrite of the State §6.3 PSD2 paragraph (§9, row V-14); disposition as recorded | regulatory cycle | C2 |
| A-29 | 1 | INT | Core's SHOULD reconnect and Routing's MUST back off when reconnecting can both hold; the idle-close MAY does not negate Core's SHOULD. | open | Disposition on modal strength; drift-linter rule | pending | — | pending |
| A-30 | 1 | PART (all sub-claims hold; "normative" overstated) | pending | open | Per-example schema validation; error-code count aligned | pending | — | pending |
| A-31 | 1 | INT | Core step 6 selects the signing profile while Routing step (e) is §7.4 negotiation — different operations; Core's pipeline does not order expiry or idempotency; the missing compliance step is an omission, not a contradiction. | open | Disposition marking Routing §1.2.1 step 6 non-normative, or aligned order | pending | — | pending |
| A-32 | 2 | CONF | per DR-3 | open | Harness rule equal for None / GDPR-STANDARD; ITV-579 and C-06(c) aligned to prose | pending | DR-3 | pending |
| A-33 | 2 | CONF | pending | IPC | Executed alg/key-mismatch vector asserted to fail | negative control run; repo vector pending | IPC, C0.5 (negative control run; repo vector pending) | C0.5 / 260ac73 |
| A-34 | 2 | CONF | pending | IPC | INV-18/19 asserted negatives with checker assertion | INV-18/19 asserted (C0.5); caveat: unauthorized proxy exact for current corpus only | IPC, C0.5; caveat: unauthorized proxy exact for current corpus only | C0.5 / 260ac73 |
| A-35 | 2 | CONF | pending | open | Checker/generator refuse without RFC 8785, or fallback validated against RFC 8785 data | pending | open | pending |
| A-36 | 2 | CONF | pending | IPC | Harness case arsiaprotocolx.* → True | pending | IPC, C0.5 | C0.5 / 260ac73 |
| A-37 | 2 | CONF | pending | IPC | Harness cases for SEK, length/digit limits, non-currency scales | pending | IPC, C0.5; spawned A-66 | C0.5 / 260ac73 |
| A-38 | 2 | CONF | pending | IPC | Harness cases for max-age below ceiling and revocation-event invalidation | harness R13 (C0.5) | IPC, C0.5 | C0.5 / 260ac73 |
| A-39 | 2 | CONF | pending | open | ITV-404/406/438/439 expectations aligned with Core §4.1.1 and executed | pending | vector cycle, DR-0.4 | pending |
| A-40 | 2 | CONF | pending | open | Generator dry-run validated against v2 schemas; envelope_hash used or documented | pending | — | pending |
| A-41 | 2 | INT (Core §11.2 defines the mandatory set) | Core §11.2 defines the mandatory set | open | Disposition or aligned pseudocode quote | pending | — | pending |
| A-42 | 2 | PART (16, not 17, expected-valid) | pending | validator IPC (C0.5); vectors open | 94 skip vectors structurally valid; ITV-545/546 aligned | pending | validator IPC C0.5; vectors open | C0.5 / 260ac73 (validator) |
| A-43 | 3 | CONF via V-1..V-5 | pending | closed (C2); currency re-verified 2026-09-28 — V-1..V-4 confirmed; V-5 reopened as A-71 | Corrected AI Act citations matched to official text | V-1..V-5 corrected and matched to Reg. (EU) 2024/1689 (§9) | regulatory cycle | C2 |
| A-44 | 3 | CONF via O-1, V-6..V-9 | pending | IPC; currency confirmed 2026-09-28 (O-1, V-6..V-9); gap remains A-70 | Corrected MiFID II / 2017/565 citations | O-1 and V-6..V-9 corrected (§9). Gap: the MiFID II / 2017/565 retention attributions (five-year basis, Art. 16(7) used for general record-keeping) remain uncorrected and are tracked as A-70 | regulatory cycle | C2 |
| A-45 | 3 | CONF via V-10, V-11 | pending | closed (C2); currency confirmed 2026-09-28 | Corrected DORA citations (Art. 18(1); 2025/301 Art. 5(1)(a) incl. 24 h cap) | V-10, V-11 corrected incl. Del. Reg. (EU) 2025/301 Art. 5(1)(a) 24 h cap (§9) | regulatory cycle | C2 |
| A-46 | 3 | CONF via V-12..V-14 | pending | closed (C2); currency confirmed 2026-09-28 | Corrected PSD2 / RTS 2018/389 citations; State §6.3 SCA sentence | V-12..V-14 corrected; State §6.3 SCA paragraph rewritten (§9) | regulatory cycle; A-28 | C2 |
| A-47 | 3 | CONF via V-15..V-17 | pending | closed (C2); currency confirmed 2026-09-28 | Corrected GDPR citations; Art. 9(1) enum; DPO contact required | V-15..V-17 corrected; Art. 9(1) enum complete with mapping; contact point REQUIRED (§9) | regulatory cycle | C2 |
| A-48 | 3 | PART (T-1 defect; T-2 correct; V-18 defect; O-2 defect) | pending | closed (C2); currency confirmed 2026-09-28 | Corrected eIDAS/ETSI citations | T-1, V-18, O-2 corrected (§9); T-2 verified correct, unchanged | regulatory cycle | C2 |
| A-49 | 3 | PART (T-3..T-5 defects; T-6 jti correct) | pending | IPC | Receiver-check lists aligned with RFC 9449 §4.3; DPoP schema accepts nonce | T-3, T-4, T-5 corrected; nonce accepted by schema, ITV-580 / INV-45 executed (§9). Gap: Identity §3.3 still omits RFC 9449 §4.3 checks 1-3, 7 and 10; Core §6.3 omits the typ/alg checks | regulatory cycle | C2 |
| A-50 | 3 | CONF (T-7) | pending | closed | Schema rejects all-zero trace_id/span_id; executed vector | T-7: schema rejects all-zero ids without lookaround; INV-43 / INV-44 executed (§9) | — | C2 |
| A-51 | 3 | CONF (T-8) | pending | closed | BCP 14 keywords corrected in six sentences; RTM rows re-traced | T-8: six sentences corrected; five RTM rows re-traced MAY → MUST_NOT (§9) | — | C2 |
| A-52 | 3 | CONF via V-19 (defect), V-20..V-23 (correct), T-9 (EDPB date defect) | pending | closed (C2); currency confirmed 2026-09-28 (V-19, T-9); V-21 (CORRECT at C0) reopened as A-72 | Corrected CAP citation; EDPB date corrected | V-19, T-9 corrected (§9); V-20..V-23 verified correct, unchanged | regulatory cycle | C2 |
| A-53 | 4 | CONF | pending | open | Executed runner for the 74 named tests, or per-test disposition | pending | coverage program | pending |
| A-54 | 4 | CONF | pending | open | INV-37/38/39 with crypto blocks executed and asserted to fail | pending | coverage program | pending |
| A-55 | 4 | CONF | pending | open | Executed (token, token_hash) match/mismatch vectors | pending | coverage program | pending |
| A-56 | 4 | CONF | pending | open | Executed attestation vectors with tampered variants | pending | coverage program | pending |
| A-57 | 4 | CONF | pending | open | Executed approval-chain vectors (capability, deadline, approver id, signature) | pending | coverage program; DR-1 | pending |
| A-58 | 4 | CONF | pending | open | Schema rule for jwks_fetched_at; executed revocation/cache vectors | pending | coverage program | pending |
| A-59 | 4 | CONF | pending | closed | Consistency rule asserting State §7.1 table ⇔ schema extensions | check_consistency guard "audit extension table == schema conditionals (A-59)" passes on the repaired state and fails on the a8e9930 baseline and on targeted mutations; exceptions ict_incident and jwks_fetched_at declared with reasons (§10) | prerequisite of DR-5 | C3a |
| A-60 | 4 | CONF | per DR-5 | open | Executed hash_chain vectors incl. tamper case | pending | DR-5 | pending |
| A-61 | 4 | CONF | pending | open | Executed duplicate-member and non-I-JSON vectors, strict parser | pending | coverage program | pending |
| A-62 | 4 | CONF | pending | open | Harness rule + ITV-545/546/547 executed with profile tolerances; clean "90 s under 120 s" case | pending | coverage program | pending |
| A-63 | 4 | PART (A-30 explanation corrected) | pending | open | Extraction rule validating every non-envelope normative example | pending | coverage program | pending |
| A-64 | 4 | CONF | pending | open | RTM statistics: each MUST row mapped to evidence or disposition | pending | coverage program | pending |
| A-65 | 4 | PART (7 unsupported, 4 overstated) | pending | open | Skip-classification entries matched one-to-one to harness cases | pending | vector cycle | pending |
| A-66 | 1 | CONF (from C0.5) | pending | open | Assets §3.1.1 explicit-scale exception defined or removed | pending | prose/schema cycle | pending (raised in C0.5) |
| A-67 | E | CONF (from C0.5) | pending | open | Assets §3.1.1 36-char limit made effective or removed | pending | prose cycle | pending (raised in C0.5) |
| A-68 | E | CONF (from C0.5) | pending | open | Assets §3.1.1 ISO-code match rule made effective or removed | pending | prose cycle | pending (raised in C0.5) |
| A-69 | 3 | new (DR-0.2) | per DR-0.2 | closed; currency confirmed 2026-09-28; applicability tracked in A-73 | EU-AI-ACT-HIGH-RISK prose attributes pre-execution approval as profile choice; Art. 14 cited correctly | State §6.2 and the Assets §6.3.1 echo rewritten; every other Art. 14 mention reviewed (§9, row A-69) | regulatory cycle | C2 |
| A-70 | 3 | new (C2); evidence updated by currency re-verification 2026-09-28 | pending | open | MIFID-II floor re-grounded (e.g. MiFIR Art. 25(1) for order and transaction data) with scope, anchor and day-count justified, or the floor and its attributions corrected; all echoes aligned | The MIFID-II profile's retention floor (P1827D) and its attributions (MiFID II Art. 16(7); Del. Reg. (EU) 2017/565 Art. 72) are not supported as written. In the sources consulted, five-year periods appear only in: (i) MiFIR (Reg. (EU) No 600/2014) Art. 25(1), unchanged in the consolidated version of 23.11.2025 — investment firms keep at the disposal of the competent authority, "for five years", the relevant data relating to all orders and all transactions in financial instruments carried out on own account or on behalf of a client; (ii) MiFIR Art. 25(2), as replaced by Art. 3 of Reg. (EU) 2024/2809 with effect from 4 December 2024 (entry into force on the twentieth day after publication in OJ L of 14.11.2024; Art. 3 is not among the provisions deferred by Art. 4(2)-(4)) — operators of trading venues keep order data "for at least five years", in a machine-readable format and using a common template; (iii) MiFID II Art. 16(7) — records of telephone conversations and electronic communications, five years (up to seven on request); (iv) 2017/565 Art. 76(8) — copy of recordings available on request for five years. None sets a period for "all services, activities and transactions"; 2017/565 Art. 72 sets none. MiFIR Art. 25 states no anchor for the count (2017/565 Art. 76(11) anchors at record creation, within Art. 76 only). The conversion of "five years" to P1827D and the extension of the floor to every record under the profile (state entries, audit records, asset-transfer records not concerning financial instruments) are ARSIA technical decisions requiring their own justification; A-70 remains open as to that correspondence. Corrigenda 32014L0065R(19) and 32017R0565R(07)-R(09) have no English edition (manifest) and do not alter the English wording relied on. Echoes: Core §4.3.8 Rule 4; Assets §1.1.6, §6.1.2, §6.1.4, §8.2; State §4.1.2, §5.3.2, §6.3, §12.2; profiles catalog MIFID-II retention_reference and regulatory references | retention-axis cycle (DR-4) | pending (raised in C2; updated in currency passes) |
| A-71 | 3 | new (currency) | per this cycle | closed | Core passages aligned with Art. 113 as amended; official text cited | Core (at a8e9930, l.250-253) stated that Article 6(1) with its corresponding obligations applies from 2 August 2027. Reg. (EU) 2026/1744, Art. 1(40)(b), replaced Art. 113, third paragraph, point (c): Chapter III, Sections 1, 2 and 3 (except Art. 6(5)) apply from 2 December 2027 for systems classified under Art. 6(2) and Annex III, and from 2 August 2028 under Art. 6(1) and Annex I; Art. 1(40)(a) and (c) also set 2 December 2026 for Art. 5(1)(ba)/(bb) and 5(1a)/(1b), and 27 July 2026 for Arts. 102-110. Reg. (EU) 2026/1744 entered into force on the third day after publication in OJ L of 24.7.2026 (27 July 2026; Art. 4), matching the consolidated version of 27.07.2026. Core "through 2027" was also outdated. C2.1: Core l.164-167 and l.252-258 aligned with Art. 113 as amended; [EU-AI-Act-2026/1744] reference added; dates verified against 32026R1744 Art. 1(40), Art. 4 and the consolidated Art. 113 (§11) | A-73 | C2.1 |
| A-72 | 3 | new (currency) | DR-0.2 (profile choice) | closed | State §6.4 and the catalog no longer rely on Art. 54; the default stated as a profile choice | State §6.4 and the PAC-AGRICULTURE catalog entry cited Reg. (EU) 2021/2116 Art. 54 ("Annual performance clearance") as the basis for the profile's explainability_required default. Art. 54 was deleted by Reg. (EU) 2025/2649, Art. 2, point (10); that regulation entered into force on the day after publication in OJ L of 31.12.2025, and under its Art. 4 the deletion applies in respect of agricultural financial year 2025 and all subsequent agricultural financial years. No transitional rule preserves the annual performance clearance: Art. 3(3)-(4) only empower the Commission to amend Delegated Regulation (EU) 2022/127 and Implementing Regulation (EU) 2022/128 to reflect the deletion; recital 61 states the output-matching requirement of Art. 37(1)(b)(i) is covered by the conformity procedure of Art. 55. C2.1: State §6.4 paragraph restated as a profile choice citing the deletion (Art. 2(10), Art. 4 verified in 32025R2649); the MUST kept without the suppressed-process clause; catalog reference to Art. 54 removed; 2025/2649 added to State references (§11) | — | C2.1 |
| A-73 | 3 | new (currency) | sentences aligned (this cycle); framing question referred to DR-3/DR-4 | IPC | remainder resolved in the DR-3/DR-4 cycle | Sentences asserting current applicability of AI Act Chapter III obligations aligned with Art. 113(c) as amended (seven replacements above). Open remainder: the sentences claiming the profile satisfies/implements Arts. 12, 13, 26(6) and the Annex III classification statements (locations listed in the C2.1 report) — what the EU-AI-ACT-HIGH-RISK profile claims to implement before 2 December 2027 is referred to the owner. C2.1: the nine sentences applied (Actions l.392-393, l.981-985, l.993-1000, l.1165-1167; Core l.1297-1299; State l.1716, §6.2). Open remainder: State l.2348-2349 (Art. 12 "satisfied"), State l.2358 ("This satisfies Article 26(6)"), Core l.1110 ("implements EU AI Act Article 13"), Identity l.206, State l.2293-2294 and l.2363-2364 (Annex III classification) (§11) | DR-3, DR-4; V-4; A-69 | C2.1 (partial) |

**Counts (this register only, 76 rows).**
- By class: 1 = 33; 2 = 12; 3 = 16; 4 = 13; E = 2.
- By triage status: CONF 48; PART 17; INT 6; UNV 0; new 5.
- By remediation state: open 47; IPC 10; mixed (validator IPC, vectors open) 1; closed 18.
- By disposition: per DR 10; interpretive justification or recorded disposition 11; pending 55.

## 5. Regulatory citation register

- **V items:** provisions, verdicts and sources come from the regulatory
  verification report (EUR-Lex PDFs, verified 2026-09-25 at `fb5a875`).
- **T items:** verified in the triage session against the official
  non-EUR-Lex texts named.
- **O items:** verified by the orchestrator on EUR-Lex web pages, not on files
  in the sources folder.

| Parent | Item | Act and provision | Verdict | Source used | Source version (consulted 2026-09-28) | State |
|---|---|---|---|---|---|---|
| A-43 | V-1 | AI Act, Reg. (EU) 2024/1689: Art. 52 cited for limited-risk transparency obligations; the text places them in Art. 50 | DEFECT | EUR-Lex `32024R1689.pdf` | `02024R1689-20260727 v001.001; 32026R1744` | closed (C2); currency confirmed 2026-09-28 |
| A-43 | V-2 | AI Act: Art. 17(1)(d) cited for record-keeping; the text places it in Art. 17(1)(k) | DEFECT | EUR-Lex `32024R1689.pdf` | `02024R1689-20260727 v001.001; 32026R1744` | closed (C2); currency confirmed 2026-09-28 |
| A-43 | V-3 | AI Act: the quotation attributed to Art. 17 occurs nowhere in the Regulation | DEFECT | EUR-Lex `32024R1689.pdf` | `02024R1689-20260727 v001.001; 32026R1744` | closed (C2); currency confirmed 2026-09-28 |
| A-43 | V-4 | AI Act: logging attributed to Art. 17; the text places it in Arts. 12(1) and 19(1) | DEFECT | EUR-Lex `32024R1689.pdf` | `02024R1689-20260727 v001.001; 32026R1744` | closed (C2); currency confirmed 2026-09-28 |
| A-43 | V-5 | AI Act: high-risk provisions "applicable from August 2025"; Art. 113 gives 2 Aug 2026, or 2 Aug 2027 for Art. 6(1) | DEFECT | EUR-Lex `32024R1689.pdf` | `02024R1689-20260727 v001.001; 32026R1744` | reopened (currency 2026-09-28) → A-71 |
| A-44 | V-6 | Del. Reg. (EU) 2017/565: Art. 76 described as cancellations/modifications; it is the call-recording article, and transactions are in Art. 75 | DEFECT | EUR-Lex `32017R0565.pdf` | `02017R0565-20220802 v005.001; corrigenda R(07)-R(09) not EN (manifest)` | closed (C2); currency confirmed 2026-09-28 |
| A-44 | V-7 | Del. Reg. (EU) 2017/565: Art. 73 described as providing records to authorities; it covers firm/client rights and obligations records | DEFECT | EUR-Lex `32017R0565.pdf` | `02017R0565-20220802 v005.001; corrigenda R(07)-R(09) not EN (manifest)` | closed (C2); currency confirmed 2026-09-28 |
| A-44 | V-8 | MiFID II, Dir. 2014/65/EU: Art. 16(5) cited for algorithmic-trading records; the text places them in Art. 17 | DEFECT | EUR-Lex `32014L0065.pdf` | `02014L0065-20260606 v014.001; corrigendum R(19) not EN (manifest)` | closed (C2); currency confirmed 2026-09-28 |
| A-44 | V-9 | MiFID II: Art. 16(6) cited as a 5-year retention requirement; the period is in Art. 16(7) | DEFECT | EUR-Lex `32014L0065.pdf` | `02014L0065-20260606 v014.001; corrigendum R(19) not EN (manifest)` | closed (C2); currency confirmed 2026-09-28 |
| A-45 | V-10 | DORA, Reg. (EU) 2022/2554: Art. 17(1) cited for the classification criteria; the text places them in Art. 18(1) | DEFECT | EUR-Lex `32022R2554.pdf` | `32022R2554 original; corrigenda R(01)-R(09) not EN (manifest)` | closed (C2); currency confirmed 2026-09-28 |
| A-45 | V-11 | DORA: Art. 19 cited for the 4-hour initial notification; the limit is in Del. Reg. (EU) 2025/301 Art. 5(1)(a), with a 24 h cap | DEFECT | EUR-Lex `32022R2554.pdf`, `32025R0301.pdf` | `32022R2554 original; corrigenda R(01)-R(09) not EN (manifest); 32025R0301 original; corrigendum R(01) not EN (manifest)` | closed (C2); currency confirmed 2026-09-28 |
| A-46 | V-12 | PSD2, Dir. (EU) 2015/2366: money-exchange registration attributed to PSD2 transposition; Art. 3(f) excludes it | DEFECT | EUR-Lex `32015L2366.pdf` | `02015L2366-20250117 v002.001; corrigendum R(08) not EN (manifest); 32023L2673 (no effect on cited articles)` | closed (C2); currency confirmed 2026-09-28 |
| A-46 | V-13 | PSD2: Art. 98 cited for the TRA exemption; the text places it in RTS 2018/389 Art. 18 | DEFECT | EUR-Lex `32015L2366.pdf`, `32018R0389.pdf` | `02015L2366-20250117 v002.001; corrigendum R(08) not EN (manifest); 32023L2673 (no effect on cited articles); 02018R0389-20230912 v002.001` | closed (C2); currency confirmed 2026-09-28 |
| A-46 | V-14 | PSD2 Arts. 4(30) and 97: SCA stated to be "satisfied through the human oversight flow" | DEFECT | EUR-Lex `32015L2366.pdf` | `02015L2366-20250117 v002.001; corrigendum R(08) not EN (manifest); 32023L2673 (no effect on cited articles)` | closed (C2); currency confirmed 2026-09-28 |
| A-47 | V-15 | GDPR, Reg. (EU) 2016/679: Art. 5(1)(e) labelled "data minimisation"; the text gives that label to Art. 5(1)(c) | DEFECT | EUR-Lex `32016R0679.pdf` | `02016R0679-20160504 v000.002 (C1 2018); corrigenda R(01), R(03) not EN (manifest; R(03) read in PT/IT/DE)` | closed (C2); currency confirmed 2026-09-28 |
| A-47 | V-16 | GDPR: special-category enum stated to be "drawn from Art. 9(1)" | DEFECT | EUR-Lex `32016R0679.pdf` | `02016R0679-20160504 v000.002 (C1 2018); corrigenda R(01), R(03) not EN (manifest; R(03) read in PT/IT/DE)` | closed (C2); currency confirmed 2026-09-28 |
| A-47 | V-17 | GDPR: DPO/contact point treated as optional against Arts. 33(3)(b) and 34(2) | DEFECT | EUR-Lex `32016R0679.pdf` | `02016R0679-20160504 v000.002 (C1 2018); corrigenda R(01), R(03) not EN (manifest; R(03) read in PT/IT/DE)` | closed (C2); currency confirmed 2026-09-28 |
| A-48 | V-18 | eIDAS, Reg. (EU) No 910/2014: Art. 28 cited for seal certificates; the text places them in Art. 38 | DEFECT | EUR-Lex `32014R0910.pdf` | `02014R0910-20241018 v002.003; corrigenda 32014R0910R(11)-R(12), 32024R1183R(01), R(03)-R(06) not EN (manifest)` | closed (C2); currency confirmed 2026-09-28 |
| A-52 | V-19 | CAP, Reg. (EU) 2021/2116: Art. 47 cited for paying-agency accreditation; the text places it in Arts. 8-9 | DEFECT | EUR-Lex `32021R2116.pdf` | `02021R2116-20260818 v004.001; derogating acts 32022R1172, 32023R1508, 32024R2434, 32025R1796 (no effect on cited articles)` | closed (C2); currency confirmed 2026-09-28 |
| A-52 | V-20 | Reg. (EU) 2021/2116 Art. 51, access to documents | CORRECT | EUR-Lex `32021R2116.pdf` | `02021R2116-20260818 v004.001; derogating acts 32022R1172, 32023R1508, 32024R2434, 32025R1796 (no effect on cited articles)` | CORRECT (C0); currency confirmed 2026-09-28 |
| A-52 | V-21 | Reg. (EU) 2021/2116 Art. 54, annual performance clearance | CORRECT | EUR-Lex `32021R2116.pdf` | `02021R2116-20260818; 32025R2649` | CORRECT at C0; reopened (currency 2026-09-28) → A-72 |
| A-52 | V-22 | Reg. (EU) 2021/2116 Art. 59, protection of the Union's financial interests | CORRECT | EUR-Lex `32021R2116.pdf` | `02021R2116-20260818 v004.001; derogating acts 32022R1172, 32023R1508, 32024R2434, 32025R1796 (no effect on cited articles)` | CORRECT (C0); currency confirmed 2026-09-28 |
| A-52 | V-23 | Impl. Reg. (EU) 2022/128 Art. 34, retention periods for supporting documents | CORRECT | EUR-Lex `32022R0128.pdf` | `02022R0128-20260722 (HTML) v004.001` | CORRECT (C0); currency confirmed 2026-09-28 |
| A-48 | T-1 | ETSI EN 319 412-5: QcCompliance described as the seal indicator; the seal type is QcType id-etsi-qct-eseal | DEFECT | ETSI EN 319 412-5 (triage) | `official host (C2); out of scope of OD-4 pass` | closed (C2) |
| A-48 | T-2 | ETSI EN 319 412-5: "any QcStatements" wording | CORRECT (restrictive reading) | ETSI EN 319 412-5 (triage) | `official host (C2); out of scope of OD-4 pass` | open |
| A-49 | T-3 | RFC 9449 §4.3: Core receiver checks omit ath | DEFECT | RFC 9449 (triage) | `official host (C2); out of scope of OD-4 pass` | closed (C2) |
| A-49 | T-4 | RFC 9449 §4.3: Identity omits typ/alg checks | DEFECT | RFC 9449 (triage) | `official host (C2); out of scope of OD-4 pass` | closed (C2) |
| A-49 | T-5 | RFC 9449 §4.2: the schema forbids nonce | DEFECT | RFC 9449 (triage) | `official host (C2); out of scope of OD-4 pass` | closed (C2) |
| A-49 | T-6 | RFC 9449 §4.3: jti replay as a requirement | CORRECT (not required) | RFC 9449 (triage) | `official host (C2); out of scope of OD-4 pass` | open |
| A-50 | T-7 | W3C Trace Context: all-zero ids accepted | DEFECT | W3C Trace Context (triage) | `official host (C2); out of scope of OD-4 pass` | closed (C2) |
| A-51 | T-8 | BCP 14: MAY used as a prohibition | DEFECT | BCP 14 (triage) | `official host (C2); out of scope of OD-4 pass` | closed (C2) |
| A-52 | T-9 | EDPB Guidelines 05/2021 v2.0 dated Feb 2022; the correct date is 14 Feb 2023 | DEFECT | EDPB (triage) | `official host (C2); out of scope of OD-4 pass` | closed (C2) |
| A-44 | O-1 | Del. Reg. (EU) 2017/565 labelled "RTS 22"; RTS 22 is 2017/590 | DEFECT | EUR-Lex web page (orchestrator) | `02017R0565-20220802; 32017R0590 original` | closed (C2); currency confirmed 2026-09-28 |
| A-48 | O-2 | eIDAS 2.0 described as a "Proposal … anticipated"; it is Reg. (EU) 2024/1183, in force | DEFECT | EUR-Lex web page (orchestrator) | `32024R1183 original; manifest status "In force"` | closed (C2); currency confirmed 2026-09-28 |

**Totals (this register only, 34 rows).**
- Defects: 28 (19 V + 7 T + 2 O).
- Correct: 6 (4 V + 2 T).
- Unverified: 0.
- State: closed 27 (C2 corrections; currency confirmed 2026-09-28 for the V and O items); reopened 2 (V-5 → A-71; V-21, CORRECT at C0, → A-72); CORRECT with currency confirmed 3 (V-20, V-22, V-23); open 2 (T-2, T-6: verified correct, out of scope of the OD-4 pass).
- Currency totals (26 items): CONFIRMADO 24 / REABERTO 2 / PENDENTE 0; A-70 apart: evidence complete, finding open.

## 6. Runtime-vector register

Structural results come from `scripts/validate_vectors.py` at execution
baseline `63a233b`, which validates runtime-only (`skip_schema`) vectors
structurally since C0.5. "First failure reason" is the first reported schema
error, truncated.

**Columns.**
- **Classification:** for structural failures, pending the individual
  classification required by DR-0.4.
- **Coverage:** recorded at audit baseline `51610ac`. PC = crypto-checked; PH =
  hand-coded harness mirror; N = not exercised. No vector was fully covered.

**Annotations.**
- **X (A-39):** expectation contradicted by Draft-02.
- **X — corrected in C0.5:** that contradiction was fixed in C0.5.
- **MAY posture (DR-0.3):** expected-invalid on a MAY.
- **A-65:** the skip-classification document claims harness coverage that
  does not exist.

| ID | Structure | First failure reason | Classification | Coverage | Annotations |
|---|---|---|---|---|---|
| INV-07 | pass | — | — | PC | A-65: documented harness coverage does not exist |
| INV-08 | pass | — | — | PC | — |
| INV-09 | pass | — | — | PC | — |
| INV-11 | pass | — | — | N | — |
| INV-12 | pass | — | — | PC | — |
| ITV-404 | pass | — | — | N | X (A-39) |
| ITV-405 | fail | `'2.0' was expected` | pending (DR-0.4) | N | — |
| ITV-406 | fail | `Additional properties are not allowed ('future_field' was unexpected)` | pending (DR-0.4) | N | X (A-39) |
| ITV-408 | pass | — | — | N | — |
| ITV-409 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| ITV-410 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| ITV-411 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| ITV-412 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| ITV-413 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| ITV-414 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| ITV-416 | fail | `'security' is a required property` | pending (DR-0.4) | N | A-65: documented harness coverage does not exist |
| ITV-417 | pass | — | — | PH | — |
| ITV-418 | fail | `'security' is a required property` | pending (DR-0.4) | N | A-65: documented harness coverage does not exist |
| ITV-421 | pass | — | — | PH | — |
| ITV-422 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| ITV-424 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| ITV-425 | pass | — | — | N | — |
| ITV-426 | pass | — | — | N | — |
| ITV-427 | pass | — | — | N | — |
| ITV-429 | pass | — | — | N | — |
| ITV-431 | pass | — | — | N | — |
| ITV-432 | pass | — | — | N | — |
| ITV-433 | pass | — | — | N | — |
| ITV-434 | pass | — | — | N | — |
| ITV-435 | pass | — | — | N | — |
| ITV-436 | pass | — | — | N | — |
| ITV-437 | pass | — | — | N | — |
| ITV-438 | fail | `Additional properties are not allowed ('routing_hint' was unexpected)` | pending (DR-0.4) | N | X (A-39) |
| ITV-439 | fail | `Additional properties are not allowed ('extended_context', 'telemetry_flags' were unexp…` | pending (DR-0.4) | N | X (A-39) |
| ITV-440 | pass | — | — | N | — |
| ITV-442 | pass | — | — | N | — |
| ITV-445 | pass | — | — | N | — |
| ITV-446 | pass | — | — | N | — |
| ITV-448 | pass | — | — | N | — |
| ITV-449 | pass | — | — | N | — |
| ITV-450 | pass | — | — | N | — |
| ITV-457 | pass | — | — | N | — |
| ITV-458 | pass | — | — | N | — |
| ITV-459 | pass | — | — | N | — |
| ITV-460 | pass | — | — | N | — |
| ITV-461 | pass | — | — | N | — |
| ITV-462 | pass | — | — | N | — |
| ITV-463 | pass | — | — | N | — |
| ITV-466 | pass | — | — | N | — |
| ITV-467 | pass | — | — | N | — |
| ITV-475 | pass | — | — | N | — |
| ITV-476 | pass | — | — | N | — |
| ITV-477 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| ITV-479 | pass | — | — | N | A-65: documented harness coverage does not exist |
| ITV-487 | pass | — | — | N | — |
| ITV-526 | pass | — | — | N | — |
| ITV-536 | fail | `'expires_at' is a required property` | pending (DR-0.4) | N | A-65: documented harness coverage does not exist |
| ITV-537 | fail | `'expires_at' is a required property` | pending (DR-0.4) | N | — |
| ITV-538 | fail | `'expires_at' is a required property` | pending (DR-0.4) | N | A-65: documented harness coverage does not exist |
| ITV-539 | fail | `'expires_at' is a required property` | pending (DR-0.4) | N | — |
| ITV-540 | fail | `'expires_at' is a required property` | pending (DR-0.4) | N | — |
| ITV-541 | fail | `'expires_at' is a required property` | pending (DR-0.4) | N | — |
| ITV-543 | fail | `'expires_at' is a required property` | pending (DR-0.4) | PC | — |
| ITV-544 | fail | `'expires_at' is a required property` | pending (DR-0.4) | PC | — |
| ITV-545 | fail | `'expires_at' is a required property` | pending (DR-0.4) | N | MAY posture (DR-0.3) |
| ITV-546 | fail | `'b0546001-d4e5-4f60-c123-445566778899' does not match '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4…` | pending (DR-0.4) | N | X — corrected in C0.5 |
| ITV-547 | fail | `'c0547001-e5f6-4071-d234-556677889900' does not match '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4…` | pending (DR-0.4) | PC | — |
| INV-18 | pass | — | — | PC | — |
| INV-19 | pass | — | — | PC | — |
| ITV-553 | fail | `'capabilities' is a required property` | pending (DR-0.4) | N | — |
| ITV-554 | fail | `'capabilities' is a required property` | pending (DR-0.4) | N | — |
| ITV-555 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| INV-20 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| INV-22 | fail | `'security' is a required property` | pending (DR-0.4) | N | — |
| INV-23 | pass | — | — | N | — |
| INV-24 | pass | — | — | N | — |
| INV-25 | fail | `'inform' is not one of ['request', 'response', 'event', 'error', 'pending_approval', 'a…` | pending (DR-0.4) | PH | — |
| ITV-563 | pass | — | — | PH | — |
| ITV-564 | pass | — | — | PH | — |
| ITV-565 | pass | — | — | PH | — |
| ITV-566 | pass | — | — | PH | — |
| ITV-567 | pass | — | — | PH | — |
| ITV-568 | pass | — | — | PH | — |
| ITV-570 | pass | — | — | N | — |
| ITV-571 | pass | — | — | N | — |
| ITV-572 | pass | — | — | N | — |
| ITV-575 | pass | — | — | PH | — |
| ITV-576 | pass | — | — | PH | — |
| ITV-577 | pass | — | — | PH | — |
| ITV-578 | pass | — | — | N | A-65: documented harness coverage does not exist |
| INV-37 | pass | — | — | N | — |
| INV-38 | pass | — | — | N | — |
| INV-39 | pass | — | — | N | — |
| ITV-579 | pass | — | — | PH | — |

**Counts (this register only, 94 rows).**
- Structure: pass 62; fail 32.
- Classification: pending (DR-0.4) 32.
- Coverage at `51610ac`: PC 9; PH 13; N 72; fully covered 0.
- Annotations: X (A-39) 4; X — corrected in C0.5 1; MAY posture 1; A-65 7.

## 7. Coverage register

| Guarantee | Current evidence at baseline | Required evidence type | Findings | State |
|---|---|---|---|---|
| 74 named normative tests | none executed | executed cases or per-test disposition | A-53 | open |
| alg/kid malleability closure | INV-37/38/39 not executed | negative crypto vectors executed and asserted to fail | A-54 | open |
| Algorithm coherence in verifier | repaired in C0.5 (negative control only) | repo mismatch vector asserted rejected | A-33 | open |
| Negative crypto rejection | INV-18/19 asserted (C0.5) | keep assertion; explicit crypto field later | A-34 | open |
| Token binding (token_hash) | schema presence/pattern only | (token, hash) match/mismatch vectors | A-55 | open |
| Relay attestation verification | schema only | signed attestation vectors with tampered variants | A-56 | open |
| Approval chain verification | harness R7 subset | vectors for capability, deadline, approver identity, signature | A-57 | open |
| Revocation under cache ceiling | harness R13 (C0.5) | keep; add vector sequence | A-58, F-2 | open |
| jwks_fetched_at recording | none | schema rule + audit-record vectors | A-58 | open |
| Key-revocation event invalidation | harness R13 (C0.5) | keep; add vector | A-58 | open |
| Audit prose↔schema parity | event-type enum only | consistency rule over extension table | A-59 | open |
| Hash-chain tamper evidence | ITV-95 schema only | chain vectors incl. tamper case | A-60, A-8 | open |
| I-JSON conformance | none | strict-parser vectors | A-61 | open |
| Duplicate-member rejection | none | raw-text vectors with duplicate detection | A-61 | open |
| Profile clock-skew override | 3 skipped vectors; ITV-546 reclassified | harness rule + executed ITV-545/546/547 + clean 90 s/120 s case | A-62 | open |
| Non-envelope normative examples | 9 envelope examples validated | per-example validation for every non-envelope example | A-63 | open |
| RTM MUST rows | 1,297 rows: 369 no evidence, 61 skipped-only | each row mapped to evidence or disposition | A-64 | open |
| Runtime-vector coverage claims | skip-classification doc (7 unsupported, 4 overstated) | one-to-one vector→harness map | A-65 | open |

**Counts (this register only, 18 rows):** open 18; closed 0.

## 8. Open notes

- **Vectors vs MAY behaviour:** ITV-545 is expected-invalid on a MAY (Core
  §4.1.3). The posture is to be defined in the vector cycle (DR-0.3).
- **A-34 proxy:** exact for the current corpus (INV-18, INV-19). An explicit
  crypto field is the definitive fix (vector/meta-schema cycle).
- **ITV-546:** its coverage gap is mapped to A-62.
- **A-35:** the canonicalization fallback stays latent while rfc8785 is
  installed.
- **CI:** `validate-vectors` has been red by design since C0.5, and stays red
  until the vector cycle.
- **Out-of-date docs:** `docs/draft-02-skip-classification.md` and
  `scripts/README.md` are out of date on the ITV-545/546 reasons, skip
  semantics and crypto output (follow-up under A-65).
- **Regulatory count provenance:** the cumulative regulatory count relies on
  O-1/O-2, verified by the orchestrator on EUR-Lex web pages, not on files in
  the sources folder.
- **Missing SPDX headers:** `docs/auditoria-spec-draft-01.md` and
  `docs/spec-audit-draft-01.md` lack the CC-BY-SA-4.0 header (follow-up; not
  fixed in C1).
- **Stale published counts (C2):** the root `README.md`, `CLAUDE.md` and files
  in `docs/` still state 649 vectors and 1109 MUST+MUST_NOT. After C2 the
  figures are 653 vectors and 1903 RTM rows / 1114 MUST+MUST_NOT. Only
  `test-vectors/README.md` was updated in C2, where the `ITV-` prefix count
  had been 578 against an actual 579 before C2. After C3a the figures are 666
  vectors and 1903 / 1114 (unchanged); `test-vectors/README.md` was updated again.
- **AI Act Art. 13 quotation (C2 observation):** State §6.2 (l.2319-2321) quotes
  Art. 13(1) inside quotation marks, but not verbatim ("the system's output" against the
  official "a system's output").
- **W3C Trace Context reference (C2 observation):** Core's
  `[W3C-TraceContext]` entry cites the February 2020 Recommendation. The
  current published version is the Recommendation of 23 November 2021.
- **Identity §6.4.1 step (g) (C2 observation):** it assigns trust level 3 on
  any QcStatements indicating a qualified certificate and does not check
  QcType `id-etsi-qct-eseal`, which §6.3 now names (T-2 was verified correct
  under the restrictive reading).
- **Breach-notification schema coverage (C2 observation):** no schema-ref
  vector exercises `arsia-breach-notification.schema.json`. ITV-556/557 are
  message-only, and the envelope schema does not validate the payload against
  it. C2 validated both payloads against the breach schema by hand.
- **RFC 9449 §4.3 residual (C2 observation, tracked in A-49):** Identity
  §3.3 omits checks 1-3 (single, well-formed DPoP header; required claims),
  7 (no private key in `jwk`) and 10 (nonce match). Core §6.3 omits the
  `typ`/`alg` checks.
- **Art. 14 mentions reviewed under A-69 (C2):** the remaining mentions were
  reviewed and none attributes per-action pre-execution approval to Art. 14.
  - Actions l.392 (Art. 14(1), a human in the decision loop);
  - Actions l.1011-1017 (framed as "the protocol's strongest
    interpretation");
  - Core l.1292-1293 (Rule 3, DR-3 scope);
  - Identity l.1332 (CHECK-03, signalling per gateway policy);
  - State l.2552 (limited-risk contrast).

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
- **Rollback audit fields undefined in schema (C3a observation):** Actions §4.2
  ("Rollback Audit") requires the original action's `message_id` and
  `action_id`, the rollback request's `message_id`, a timestamp and full/partial
  status. Neither the schema nor the State §7.1 table defines these fields
  (candidate finding).
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
- **Canonical pending_approval field set not enforced (C3a observation):** Assets
  §5.2 requires "exactly the canonical field set" of Actions §3.2, but the
  `pending-approval-args` schema does not close its properties.
- **Extension fields without RTM rows (C3a observation):** the per-event-type
  extension table has no dedicated RTM rows (A-64 domain).
- **ITV-401 pre-existing defect (C3a):** the vector also lacked `correlation_id`,
  so it was invalid for two causes. It was corrected when the vector was
  repurposed under Rule 4.

- **Corrigenda and language editions (C2.1):** an OJ corrigendum corrects only the
  language edition(s) in which it is published; one with no English edition does not
  alter the English wording the spec cites. The 24 corrigenda of the 2026-09-28
  currency check have no English edition (manifest).
- **GDPR R(03) (C2.1):** it exists in 15 languages, none of them EN, and corrects
  different passages per language (PT Arts. 4(11), 61(4)(b); IT recital 158,
  Art. 56(1); DE Arts. 30(2), 33(5), 34(3)). Corrections are language-specific.
- **PSD2 and 2023/2673 (C2.1):** Dir. 2023/2673 repeals Dir. 2002/65/EC from 19 June
  2026 (Art. 3) and does not mention 2015/2366. The EUR-Lex "implicitly repealed"
  marker can only concern the PSD2 provisions tied to 2002/65/EC (Arts. 39, 110), not
  Arts. 3(f), 4(30), 97 or 98.
- **CAP derogations (C2.1):** the four "Derogated in" acts derogate from Arts. 44(2)
  and 104(1)(a)(iv) of 2021/2116; none touches Arts. 8, 9, 51 or 59.
- **Manifest discrepancies resolved (C2.1):** 2016/97 is ▼M2 in MiFID II and does not
  touch Arts. 16-17; 2025/1156 is ▼M10 in MiFIR and does not touch Art. 25.
- **Non-retrievable consolidations (C2.1):** for 02022R2554, 02025R0301 and
  02017R0590, the original plus the manifest amendment lists were used (OD-4
  fallback). The 2022/128 consolidation exists only in HTML.
- **Consolidation date is not the incorporation cut-off (C2.1):** eIDAS 18.10.2024
  carries a 9.4.2025 corrigendum as C1.
- **Closure history preserved (C2.1):** no C2 closure was deleted; affected rows carry
  the currency annotation.
- **Findings register has no description column (C2.1):** defect descriptions live in
  the C0 audit report. For A-70 to A-73 the currency-pass text is placed under
  "Closure evidence obtained", as agreed with the owner. Adding a description column,
  and possibly moving the regulatory register to its own file, is a separate
  ledger-maintenance step.
- **Actions risk-tier table notes (C2.1 observation):** the Risk 7–8 table still reads
  "Article 14 human oversight applies." and "Article 13 transparency is mandatory."
  (Actions l.990-991), in the present tense. These are not among the nine A-73
  sentences, so they were left for the DR-3/DR-4 framing question.

## 9. C2 closure evidence

Spec locations are line numbers in the C2 commit. Official excerpts are
verbatim from the source named; `…` marks an omission.

| Item | Corrected text (location) | Official provision and excerpt | Source | State |
|---|---|---|---|---|
| V-1 | Actions l.957, l.2521: Art. 50 | Reg. (EU) 2024/1689 Art. 50 heading: "Transparency obligations for providers and deployers of certain AI systems" | EUR-Lex `32024R1689.pdf` | closed |
| V-2 | Actions l.1651-1653, l.2517: Art. 17(1)(k) | Art. 17(1)(k): "systems and procedures for record-keeping of all relevant documentation and information" | EUR-Lex `32024R1689.pdf` | closed |
| V-3 | State l.2339-2341: verbatim Art. 17(1)(k) quotation | Art. 17(1)(k), as above | EUR-Lex `32024R1689.pdf` | closed |
| V-4 | Core l.172-175; Actions l.994-997; State l.2345-2349: logging moved to Arts. 12(1) and 19(1) | Art. 12(1): "High-risk AI systems shall technically allow for the automatic recording of events (logs) over the lifetime of the system." Art. 19(1): "Providers of high-risk AI systems shall keep the logs referred to in Article 12(1)" | EUR-Lex `32024R1689.pdf` | closed |
| V-5 | Core l.250-253: application dates | Art. 113: "It shall apply from 2 August 2026." (b) "Chapter III Section 4 … shall apply from 2 August 2025"; (c) "Article 6(1) and the corresponding obligations in this Regulation shall apply from 2 August 2027." | EUR-Lex `32024R1689.pdf` | closed |
| A-69 | State l.2327-2335 (§6.2); Assets l.2276-2282 (§6.3.1): pre-execution / per-operation approval stated as the profile's technical choice | Art. 14(3): "commensurate with the risks, level of autonomy and context of use of the high-risk AI system"; Art. 14(4)(d): "to decide, in any particular situation, not to use the high-risk AI system or to otherwise disregard, override or reverse the output of the high-risk AI system" | EUR-Lex `32024R1689.pdf` | closed |
| V-6 | Assets l.153-156 (Art. 75 + Annex IV §2 pt 37); l.2755 (Art. 76 heading) | Annex IV, Section 2, point 37: "Each placed order's sequences in order to reflect the chronology of every event affecting it, including but not limited to modifications, cancellations and execution"; Art. 76 heading: "Recording of telephone conversations or electronic communications" | EUR-Lex `32017R0565.pdf` | closed |
| V-7 | Assets l.2008-2011 (Art. 72(1)(a)); l.2751 (Art. 73 heading) | Art. 72(1)(a): "the competent authority is able to access them readily and to reconstitute each key stage of the processing of each transaction"; Art. 73 heading: "Record keeping of rights and obligations of the investment firm and the client" | EUR-Lex `32017R0565.pdf` | closed |
| V-8 | Identity l.1973-1974: Art. 17(2) | Dir. 2014/65/EU Art. 17(2): "The investment firm shall arrange for records to be kept in relation to the matters referred to in this paragraph" | EUR-Lex `32014L0065.pdf` | closed |
| V-9 | Routing l.2396-2398: Art. 16(6) and Art. 16(7) described separately | Art. 16(6): "records to be kept of all services, activities and transactions undertaken by it"; Art. 16(7): "shall be kept for a period of five years and, where requested by the competent authority, for a period of up to seven years" | EUR-Lex `32014L0065.pdf` | closed |
| O-1 | Assets l.190, l.194, l.2745; State l.3711: "RTS 22" label removed from 2017/565 | RTS 22 is Del. Reg. (EU) 2017/590 (ledger O-1) | EUR-Lex web page (orchestrator); no local file | closed |
| V-10 | Assets l.2090-2095; `arsia-dora-incident.schema.json` description: Art. 18(1) | Reg. (EU) 2022/2554 Art. 18(1): "Financial entities shall classify ICT-related incidents and shall determine their impact based on the following criteria" | EUR-Lex `32022R2554.pdf` | closed |
| V-11 | State l.2683-2689, l.2703-2706, l.2718-2719; reference entry l.3718 | Art. 19(4): "within the time limits to be laid down in accordance with Article 20"; Del. Reg. (EU) 2025/301 Art. 5(1)(a): "within four hours from the classification of the ICT-related incident as a major ICT-related incident and no later than 24 hours from the moment the financial entity has become aware of the ICT-related incident" | EUR-Lex `32022R2554.pdf`, `32025R0301.pdf` | closed |
| V-12 | Assets l.299-300: PSD2 licence attribution removed; no substitute claim | Dir. (EU) 2015/2366 Art. 3(f): "cash-to-cash currency exchange operations where the funds are not held on a payment account" | EUR-Lex `32015L2366.pdf` | closed |
| V-13 | Assets l.2333-2336, l.2352, l.2780; RTM ASSETS-§6.3.2-02 | Del. Reg. (EU) 2018/389 Art. 18(1): "Payment service providers shall be allowed not to apply strong customer authentication where the payer initiates a remote electronic payment transaction identified … as posing a low level of risk"; PSD2 Art. 98(1)(b): "the exemptions from the application of Article 97(1), (2) and (3)" | EUR-Lex `32018R0389.pdf`, `32015L2366.pdf` | closed |
| V-14 | State l.2415-2423 (§6.3): SCA applied by the PSP to the payer; the oversight flow is not SCA (also closes A-28) | PSD2 Art. 97(1): "a payment service provider applies strong customer authentication where the payer"; Art. 4(30): "two or more elements categorised as knowledge … possession … and inherence" | EUR-Lex `32015L2366.pdf` | closed |
| V-15 | Core l.3706-3707: storage-limitation principle | Reg. (EU) 2016/679 Art. 5(1)(e): "kept in a form which permits identification of data subjects for no longer than is necessary" | EUR-Lex `32016R0679.pdf` | closed |
| V-16 | State l.700-718 (§2.1.11 values and mapping table); enums in `arsia-state-entry`, `arsia-state-operations` and `arsia-audit-record` gain `philosophical` and `sex_life` | Art. 9(1): "religious or philosophical beliefs … data concerning a natural person's sex life or sexual orientation" | EUR-Lex `32016R0679.pdf` | closed |
| V-17 | State l.2207-2220 (§5.7); `arsia-breach-notification.schema.json` (contact point REQUIRED; points (b)/(c)/(d) corrected); RTM STATE-§5.7-02/-03; ITV-557 | Art. 33(3)(b): "communicate the name and contact details of the data protection officer or other contact point where more information can be obtained"; Art. 34(2): "at least the information and measures referred to in points (b), (c) and (d) of Article 33(3)" | EUR-Lex `32016R0679.pdf` | closed |
| V-18 | Identity l.1963: Art. 38 | Reg. (EU) No 910/2014 Art. 38 heading: "Qualified certificates for electronic seals" | EUR-Lex `32014R0910.pdf` | closed |
| O-2 | Identity l.839-840, l.1965-1966: Reg. (EU) 2024/1183, adopted and in force; "anticipated 2026-2027" removed | Reg. (EU) 2024/1183 in force (ledger O-2) | EUR-Lex web page (orchestrator); no local file | closed |
| T-1 | Identity l.806-812 (§6.3); RTM IDENT-§6.3-01; ITV-02 description | ETSI EN 319 412-5 V2.6.1, clause 4.2.3: "id-etsi-qct-eseal … -- Certificate for electronic seals as defined in Regulation (EU) No 910/2014"; clause 4.2.1 Table 1, QcType "Absent": "The certificate is issued for electronic signatures" | etsi.org, EN 319 412-5 V2.6.1 (2026-05) | closed |
| T-3 | Core l.2009-2010 (§6.3): `ath` receiver check | RFC 9449 §4.3, check 12: "ensure that the value of the ath claim equals the hash of that access token" | rfc-editor.org RFC 9449 | closed |
| T-4 | Identity l.523-526 (§3.3, steps 1-2) | RFC 9449 §4.3, checks 4-5: "The typ JOSE Header Parameter has the value dpop+jwt."; "The alg JOSE Header Parameter indicates a registered asymmetric digital signature algorithm" | rfc-editor.org RFC 9449 | closed |
| T-5 | `arsia-dpop-proof.schema.json`: optional `nonce` (1*NQCHAR); ITV-580 valid, INV-45 invalid, both executed | RFC 9449 §4.2: "the DPoP proof MUST also contain the following claim: nonce"; §8.1: "nonce = 1*NQCHAR"; RFC 6749 App. A: "NQCHAR = %x21 / %x23-5B / %x5D-7E" | rfc-editor.org RFC 9449, RFC 6749 | closed |
| T-7 | `arsia-message.schema.json` trace_id/span_id: `not`/`const` all-zero, no lookaround; Core l.887-898; RTM CORE-§4.3.3-02/03; INV-43/44 executed. The patterns compile in Go `regexp` (RE2) and ripgrep (Rust `regex`), and a lookaround control is rejected by both. | W3C Trace Context §3.2.2.3: "All bytes as zero (00000000000000000000000000000000) is considered an invalid value."; §3.2.2.4: "All bytes as zero (0000000000000000) is considered an invalid value." | w3.org, Trace Context REC 23 Nov 2021 | closed |
| T-8 | Core l.585-586; State l.168-169, l.221-224, l.345-346, l.1608-1609; Assets l.1497-1498; RTM CORE-§3.3-08, STATE-§1.1-05, STATE-§1.2-02, STATE-§1.4-03, STATE-§3.3.2-04 moved MAY → MUST_NOT | RFC 2119 §2: MUST NOT "mean that the definition is an absolute prohibition of the specification"; §5: MAY "mean that an item is truly optional" | rfc-editor.org RFC 2119, RFC 8174 | closed |
| T-9 | Routing l.2389: "Version 2.0, adopted 14 February 2023" | EDPB Guidelines 05/2021 v2 PDF: "Version 2.0 14 02 2023 Adoption of the Guidelines after public consultation" | edpb.europa.eu (PDF) | closed |
| V-19 | State l.2469-2475 (§6.4); profiles catalog PAC-AGRICULTURE references: Arts. 8 and 9 | Reg. (EU) 2021/2116 Art. 8(1)(a): "the issuing, reviewing and withdrawing of accreditation of paying agencies"; Art. 9(2): "sufficient guarantees that payments are legal, regular and properly accounted for" | EUR-Lex `32021R2116.pdf` | closed |
| A-70 (verification) | State l.2395-2400: the fabricated Art. 72 quotation replaced by what Art. 72 provides. The floor and its echoes are unchanged (A-70). | Searched (whitespace-insensitive, local PDFs): Del. Reg. (EU) 2017/565 Arts. 72-76 and Annexes I and IV; Dir. 2014/65/EU Art. 16(6)-(7). Art. 72 sets no period. The only five-year periods found are Art. 76(8) (a copy of recordings "available on request for a period of five years") and Art. 16(7) (communications records "kept for a period of five years"). Other acts (e.g. Reg. (EU) No 600/2014) were not consulted, since they are not among the supplied sources. | EUR-Lex `32017R0565.pdf`, `32014L0065.pdf` | open (A-70) |

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

## 11. C2.1 closure evidence

Official texts: `32026R1744.pdf` Art. 1(40)(a)-(c) and Art. 4; the consolidated AI Act
`02024R1689-20260727`, Art. 113; and `32025R2649.pdf` Art. 2(10), Art. 3(3)-(4) and
Art. 4. All were verified before writing. Line numbers are at the C2.1 commit.

| Item | Before | After (location) |
|---|---|---|
| A-71 | Core: "phased compliance deadlines extending through 2027"; "Article 6(1) with its corresponding obligations from 2 August 2027" | Core l.164-167 and l.252-258 give the Art. 113 dates as amended (2 Dec 2027 Annex III; 2 Aug 2028 Annex I; Chapter III Section 4 from 2 Aug 2025). A `[EU-AI-Act-2026/1744]` reference is added. |
| A-73.1 | Actions: "are classified as high-risk and are subject to the full set of EU AI Act obligations…" | Actions l.981-985. The whole sentence is replaced so that "are classified as high-risk" is not duplicated. |
| A-73.2 | Actions: three occurrences of "…obligations apply" | Actions l.993-1000, each "…apply from 2 December 2027 for Annex III systems (Article 113(c))" |
| A-73.3 | Actions: "This is not a suggestion — … phased through 2027." | Actions l.1165-1167 |
| A-73.4 | Actions: "as required by EU AI Act Article 14(1)" | Actions l.392-393 |
| A-73.5 | Core Rule 3: "This enforces EU AI Act Article 14." | Core l.1297-1299 (rule semantics untouched) |
| A-73.6 | State EU-AI-ACT-HIGH-RISK retention Rationale | State l.1716, with the applicability clause appended |
| A-73.7 | State §6.2 (no applicability statement) | State §6.2, inserted before "Regulatory mapping" |
| A-72 | State §6.4 "EU 2021/2116 Art. 54 — Annual performance clearance…"; catalog "EU Regulation 2021/2116 Art. 54" | State §6.4 "Explainability — profile choice" cites the deletion (Art. 2(10); Art. 4). The MUST is kept without the suppressed-process clause. The catalog entry is removed, and a 2025/2649 reference is added. |
| Open remainder (A-73) | State l.2348-2349 and l.2358; Core l.1110; Identity l.206; State l.2293-2294 and l.2363-2364 | Unchanged; referred to DR-3/DR-4 |

References: the Actions and State EU AI Act entries gain Art. 113, and both gain a
Regulation (EU) 2026/1744 entry; State also gains a Regulation (EU) 2025/2649 entry.
RTM: no row references the edited sentences, so no rows were re-traced and the counts
stay at 1903 / 1114.
