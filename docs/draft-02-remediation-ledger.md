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
| C1 | Remediation tracking artefacts | `63a233b` | this commit | this commit |

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

Rows: 9 (6 DR, 3 OD).

## 4. Findings register

"Dependencies / remediation" reproduces the Appendix column verbatim.

| ID | Cl | Triage status | Disposition | Remediation | Closure criterion | Closure evidence obtained | Dependencies / remediation | Cycle/commit |
|---|---|---|---|---|---|---|---|---|
| F-1 | 1 | CONF | per DR-3, DR-1 | open | Aligned quotes (Core Rule 3, State §6.2, Actions §3.7) + executed high-risk/not_required vector | pending | DR-3, DR-1 | pending |
| F-2 | 2 | CONF | pending | IPC | Harness shared-cache two-call test, revoked kid, reject/reject | harness R13 (C0.5) | IPC, C0.5 | C0.5 / 260ac73 |
| F-3 | 3 | CONF | pending | open | Core §5.1 text citing UTF-16 code units + signed vector with non-BMP keys | pending | prose cycle; prerequisite of DR-5 | pending |
| A-1 | 1 | CONF | pending | open | Schema validation passing records built literally from Actions §3.5 (1-4, expiry) | pending | prerequisite of DR-5 | pending |
| A-2 | 1 | PART (State §7.4 l.3093 is a query parameter, not a record field) | pending | open | Schema validation of Rule 7, deployer_id, cancellation records; CHECK-04/STATE-15 names aligned | pending | prerequisite of DR-5 | pending |
| A-3 | 1 | PART (delivery_failed sub-claim interpretive) | pending | open | Schema validation of compliance_warning/oversight_timeout records, or disposition placing them outside the canonical trail | pending | — | pending |
| A-4 | 1 | PART (holds: post-execution window undefined) | per DR-2 | open | Aligned quotes for one within_24h evidence event + defined post-execution mechanism; executed C-09 | pending | DR-2 | pending |
| A-5 | 1 | CONF | pending | open | Aligned State §8.2.1 / Actions §1.2 quotes + executed reserved-wildcard vector | pending | — | pending |
| A-6 | 1 | INT (Core §6.4 names Actions §1.2 the single rule) | Core §6.4 names Actions §1.2 the single rule | open | Disposition + editorial alignment of Identity §3.2 step 6; ITV-566 executed | pending | — | pending |
| A-7 | 1 | CONF | pending | open | Aligned PURGE/retention quotes (Core §13.1 #9, State §3.2.2/§5.3.2) | pending | DR-4 axis rules | pending |
| A-8 | 1 | CONF | per DR-5 | open | New chain construction + claim quotes; executed tamper test on a non-hashed field | pending | DR-5; A-1, A-2, A-59, F-3 | pending |
| A-9 | 1 | PART (extras limited to registered fields) | pending | open | Schema description consistent with keyword; validation of declared extension behaviour | pending | — | pending |
| A-10 | 1 | CONF | pending | open | Assets §5.2 example validates as printed | pending | — | pending |
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
| A-27 | 1 | PART (§7.8 informative) | pending | open | Schema minItems aligned with prose (or relaxed prose); §7.8 scenario validated | pending | — | pending |
| A-28 | 1 | INT (State qualifies its own claim) | State qualifies its own claim | open | Disposition; State §6.3 opening sentence rewritten via V-14 | pending | regulatory cycle | pending |
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
| A-43 | 3 | CONF via V-1..V-5 | pending | open | Corrected AI Act citations matched to official text | pending | regulatory cycle | pending |
| A-44 | 3 | CONF via O-1, V-6..V-9 | pending | open | Corrected MiFID II / 2017/565 citations | pending | regulatory cycle | pending |
| A-45 | 3 | CONF via V-10, V-11 | pending | open | Corrected DORA citations (Art. 18(1); 2025/301 Art. 5(1)(a) incl. 24 h cap) | pending | regulatory cycle | pending |
| A-46 | 3 | CONF via V-12..V-14 | pending | open | Corrected PSD2 / RTS 2018/389 citations; State §6.3 SCA sentence | pending | regulatory cycle; A-28 | pending |
| A-47 | 3 | CONF via V-15..V-17 | pending | open | Corrected GDPR citations; Art. 9(1) enum; DPO contact required | pending | regulatory cycle | pending |
| A-48 | 3 | PART (T-1 defect; T-2 correct; V-18 defect; O-2 defect) | pending | open | Corrected eIDAS/ETSI citations | pending | regulatory cycle | pending |
| A-49 | 3 | PART (T-3..T-5 defects; T-6 jti correct) | pending | open | Receiver-check lists aligned with RFC 9449 §4.3; DPoP schema accepts nonce | pending | regulatory cycle | pending |
| A-50 | 3 | CONF (T-7) | pending | open | Schema rejects all-zero trace_id/span_id; executed vector | pending | — | pending |
| A-51 | 3 | CONF (T-8) | pending | open | BCP 14 keywords corrected in six sentences; RTM rows re-traced | pending | — | pending |
| A-52 | 3 | CONF via V-19 (defect), V-20..V-23 (correct), T-9 (EDPB date defect) | pending | open | Corrected CAP citation; EDPB date corrected | pending | regulatory cycle | pending |
| A-53 | 4 | CONF | pending | open | Executed runner for the 74 named tests, or per-test disposition | pending | coverage program | pending |
| A-54 | 4 | CONF | pending | open | INV-37/38/39 with crypto blocks executed and asserted to fail | pending | coverage program | pending |
| A-55 | 4 | CONF | pending | open | Executed (token, token_hash) match/mismatch vectors | pending | coverage program | pending |
| A-56 | 4 | CONF | pending | open | Executed attestation vectors with tampered variants | pending | coverage program | pending |
| A-57 | 4 | CONF | pending | open | Executed approval-chain vectors (capability, deadline, approver id, signature) | pending | coverage program; DR-1 | pending |
| A-58 | 4 | CONF | pending | open | Schema rule for jwks_fetched_at; executed revocation/cache vectors | pending | coverage program | pending |
| A-59 | 4 | CONF | pending | open | Consistency rule asserting State §7.1 table ⇔ schema extensions | pending | prerequisite of DR-5 | pending |
| A-60 | 4 | CONF | per DR-5 | open | Executed hash_chain vectors incl. tamper case | pending | DR-5 | pending |
| A-61 | 4 | CONF | pending | open | Executed duplicate-member and non-I-JSON vectors, strict parser | pending | coverage program | pending |
| A-62 | 4 | CONF | pending | open | Harness rule + ITV-545/546/547 executed with profile tolerances; clean "90 s under 120 s" case | pending | coverage program | pending |
| A-63 | 4 | PART (A-30 explanation corrected) | pending | open | Extraction rule validating every non-envelope normative example | pending | coverage program | pending |
| A-64 | 4 | CONF | pending | open | RTM statistics: each MUST row mapped to evidence or disposition | pending | coverage program | pending |
| A-65 | 4 | PART (7 unsupported, 4 overstated) | pending | open | Skip-classification entries matched one-to-one to harness cases | pending | vector cycle | pending |
| A-66 | 1 | CONF (from C0.5) | pending | open | Assets §3.1.1 explicit-scale exception defined or removed | pending | prose/schema cycle | pending (raised in C0.5) |
| A-67 | E | CONF (from C0.5) | pending | open | Assets §3.1.1 36-char limit made effective or removed | pending | prose cycle | pending (raised in C0.5) |
| A-68 | E | CONF (from C0.5) | pending | open | Assets §3.1.1 ISO-code match rule made effective or removed | pending | prose cycle | pending (raised in C0.5) |
| A-69 | 3 | new (DR-0.2) | per DR-0.2 | open | EU-AI-ACT-HIGH-RISK prose attributes pre-execution approval as profile choice; Art. 14 cited correctly | pending | regulatory cycle | pending |

**Counts (this register only, 72 rows).**
- By class: 1 = 33; 2 = 12; 3 = 12; 4 = 13; E = 2.
- By triage status: CONF 48; PART 17; INT 6; UNV 0; new 1.
- By remediation state: open 65; IPC 6; mixed (validator IPC, vectors open) 1; closed 0.
- By disposition: per DR 10; interpretive justification 6; pending 56.

## 5. Regulatory citation register

- **V items:** provisions, verdicts and sources come from the regulatory
  verification report (EUR-Lex PDFs, verified 2026-09-25 at `fb5a875`).
- **T items:** verified in the triage session against the official
  non-EUR-Lex texts named.
- **O items:** verified by the orchestrator on EUR-Lex web pages, not on files
  in the sources folder.

| Parent | Item | Act and provision | Verdict | Source used | State |
|---|---|---|---|---|---|
| A-43 | V-1 | AI Act, Reg. (EU) 2024/1689: Art. 52 cited for limited-risk transparency obligations; the text places them in Art. 50 | DEFECT | EUR-Lex `32024R1689.pdf` | open |
| A-43 | V-2 | AI Act: Art. 17(1)(d) cited for record-keeping; the text places it in Art. 17(1)(k) | DEFECT | EUR-Lex `32024R1689.pdf` | open |
| A-43 | V-3 | AI Act: the quotation attributed to Art. 17 occurs nowhere in the Regulation | DEFECT | EUR-Lex `32024R1689.pdf` | open |
| A-43 | V-4 | AI Act: logging attributed to Art. 17; the text places it in Arts. 12(1) and 19(1) | DEFECT | EUR-Lex `32024R1689.pdf` | open |
| A-43 | V-5 | AI Act: high-risk provisions "applicable from August 2025"; Art. 113 gives 2 Aug 2026, or 2 Aug 2027 for Art. 6(1) | DEFECT | EUR-Lex `32024R1689.pdf` | open |
| A-44 | V-6 | Del. Reg. (EU) 2017/565: Art. 76 described as cancellations/modifications; it is the call-recording article, and transactions are in Art. 75 | DEFECT | EUR-Lex `32017R0565.pdf` | open |
| A-44 | V-7 | Del. Reg. (EU) 2017/565: Art. 73 described as providing records to authorities; it covers firm/client rights and obligations records | DEFECT | EUR-Lex `32017R0565.pdf` | open |
| A-44 | V-8 | MiFID II, Dir. 2014/65/EU: Art. 16(5) cited for algorithmic-trading records; the text places them in Art. 17 | DEFECT | EUR-Lex `32014L0065.pdf` | open |
| A-44 | V-9 | MiFID II: Art. 16(6) cited as a 5-year retention requirement; the period is in Art. 16(7) | DEFECT | EUR-Lex `32014L0065.pdf` | open |
| A-45 | V-10 | DORA, Reg. (EU) 2022/2554: Art. 17(1) cited for the classification criteria; the text places them in Art. 18(1) | DEFECT | EUR-Lex `32022R2554.pdf` | open |
| A-45 | V-11 | DORA: Art. 19 cited for the 4-hour initial notification; the limit is in Del. Reg. (EU) 2025/301 Art. 5(1)(a), with a 24 h cap | DEFECT | EUR-Lex `32022R2554.pdf`, `32025R0301.pdf` | open |
| A-46 | V-12 | PSD2, Dir. (EU) 2015/2366: money-exchange registration attributed to PSD2 transposition; Art. 3(f) excludes it | DEFECT | EUR-Lex `32015L2366.pdf` | open |
| A-46 | V-13 | PSD2: Art. 98 cited for the TRA exemption; the text places it in RTS 2018/389 Art. 18 | DEFECT | EUR-Lex `32015L2366.pdf`, `32018R0389.pdf` | open |
| A-46 | V-14 | PSD2 Arts. 4(30) and 97: SCA stated to be "satisfied through the human oversight flow" | DEFECT | EUR-Lex `32015L2366.pdf` | open |
| A-47 | V-15 | GDPR, Reg. (EU) 2016/679: Art. 5(1)(e) labelled "data minimisation"; the text gives that label to Art. 5(1)(c) | DEFECT | EUR-Lex `32016R0679.pdf` | open |
| A-47 | V-16 | GDPR: special-category enum stated to be "drawn from Art. 9(1)" | DEFECT | EUR-Lex `32016R0679.pdf` | open |
| A-47 | V-17 | GDPR: DPO/contact point treated as optional against Arts. 33(3)(b) and 34(2) | DEFECT | EUR-Lex `32016R0679.pdf` | open |
| A-48 | V-18 | eIDAS, Reg. (EU) No 910/2014: Art. 28 cited for seal certificates; the text places them in Art. 38 | DEFECT | EUR-Lex `32014R0910.pdf` | open |
| A-52 | V-19 | CAP, Reg. (EU) 2021/2116: Art. 47 cited for paying-agency accreditation; the text places it in Arts. 8-9 | DEFECT | EUR-Lex `32021R2116.pdf` | open |
| A-52 | V-20 | Reg. (EU) 2021/2116 Art. 51, access to documents | CORRECT | EUR-Lex `32021R2116.pdf` | open |
| A-52 | V-21 | Reg. (EU) 2021/2116 Art. 54, annual performance clearance | CORRECT | EUR-Lex `32021R2116.pdf` | open |
| A-52 | V-22 | Reg. (EU) 2021/2116 Art. 59, protection of the Union's financial interests | CORRECT | EUR-Lex `32021R2116.pdf` | open |
| A-52 | V-23 | Impl. Reg. (EU) 2022/128 Art. 34, retention periods for supporting documents | CORRECT | EUR-Lex `32022R0128.pdf` | open |
| A-48 | T-1 | ETSI EN 319 412-5: QcCompliance described as the seal indicator; the seal type is QcType id-etsi-qct-eseal | DEFECT | ETSI EN 319 412-5 (triage) | open |
| A-48 | T-2 | ETSI EN 319 412-5: "any QcStatements" wording | CORRECT (restrictive reading) | ETSI EN 319 412-5 (triage) | open |
| A-49 | T-3 | RFC 9449 §4.3: Core receiver checks omit ath | DEFECT | RFC 9449 (triage) | open |
| A-49 | T-4 | RFC 9449 §4.3: Identity omits typ/alg checks | DEFECT | RFC 9449 (triage) | open |
| A-49 | T-5 | RFC 9449 §4.2: the schema forbids nonce | DEFECT | RFC 9449 (triage) | open |
| A-49 | T-6 | RFC 9449 §4.3: jti replay as a requirement | CORRECT (not required) | RFC 9449 (triage) | open |
| A-50 | T-7 | W3C Trace Context: all-zero ids accepted | DEFECT | W3C Trace Context (triage) | open |
| A-51 | T-8 | BCP 14: MAY used as a prohibition | DEFECT | BCP 14 (triage) | open |
| A-52 | T-9 | EDPB Guidelines 05/2021 v2.0 dated Feb 2022; the correct date is 14 Feb 2023 | DEFECT | EDPB (triage) | open |
| A-44 | O-1 | Del. Reg. (EU) 2017/565 labelled "RTS 22"; RTS 22 is 2017/590 | DEFECT | EUR-Lex web page (orchestrator) | open |
| A-48 | O-2 | eIDAS 2.0 described as a "Proposal … anticipated"; it is Reg. (EU) 2024/1183, in force | DEFECT | EUR-Lex web page (orchestrator) | open |

**Totals (this register only, 34 rows).**
- Defects: 28 (19 V + 7 T + 2 O).
- Correct: 6 (4 V + 2 T).
- Unverified: 0.
- State: open 34.

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
