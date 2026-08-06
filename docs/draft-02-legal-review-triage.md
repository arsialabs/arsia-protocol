<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
<!-- Internal reference document. Not cited by the specifications; spec corrections
     cite the underlying legal sources directly. -->

# Legal Review: Qualified Regulatory Statements

**Scope:** Findings A-19, A-21, M-30 and known-limitations item 13, inherited from 2026-07-29.
**Status:** Preliminary technical-legal triage. Prepared to support formal review by counsel. This document is not legal advice.
**Date:** 2026-08-06
**Sources:** Official texts read on EUR-Lex (Regulation (EU) 2024/1689, Regulation (EU) 2021/2116, Implementing Regulation (EU) 2022/128, Regulation (EU) 2022/2065) and primary case-law coverage of CJEU C-413/23 P.

---

## Part A. Qualified statements (marker "statement subject to legal review")

### 1. PSD2/SCA (ARSIA-Assets, sections 5.2 and 6.3, finding A-19)

**Assessment: correct, low risk.**

The negative claim ("the protocol does NOT, by itself, satisfy SCA") is safe. SCA under PSD2 Art. 97 and RTS (EU) 2018/389 requires payer authentication elements (knowledge, possession, inherence), independence of elements (RTS Art. 9) and dynamic linking for remote payments (RTS Art. 5). All of these sit on the PSP/operator side. A protocol-level dual-authorization flow cannot constitute an SCA element.

**Counsel task:** confirm that no passage implies the protocol *contributes* an SCA element. The delimitation itself is correctly drawn.

### 2. GDPR hash, pseudonymisation, erasure (ARSIA-State, section 7.2, finding A-21)

**Assessment: correct, and reinforced by new case law. Reference update required.**

The spec position (a hash is not automatically anonymous; a linkability analysis is mandatory) matches the contextual, risk-based approach adopted by the CJEU in **EDPS v SRB, C-413/23 P, judgment of 4 September 2025**: pseudonymised data is not automatically personal data for every party; classification depends on whether the recipient can reasonably re-identify individuals, considering technical, organisational and legal factors.

**Correction required:** the spec currently references "EDPB guidance". EDPB Guidelines 01/2025 on pseudonymisation were a consultation draft, are partially contradicted by the judgment, and are under revision by the EDPB. The spec should cite the C-413/23 P judgment, not the draft guidelines.

**Minor precision point:** the obligation to record the linkability analysis is currently framed as an Art. 30 register entry. The Art. 30 record has exhaustive mandatory content; the linkability analysis fits more naturally as an accountability artifact (Art. 5(2)/Art. 24) or DPIA documentation. Counsel to decide the framing.

Art. 17(3)(b) treated as case-by-case ("not a blanket immunity"): correct as written.

### 3. EU AI Act role allocation (ARSIA-Identity, section 4.4, finding M-30)

**Assessment: defensible. One gap to flag.**

"Hosting infrastructure does not by itself constitute use under one's own authority" aligns with the deployer definition in Art. 3(4) of Regulation (EU) 2024/1689. The informative, per-deployment framing of the owner/deployer_id mapping to provider/deployer roles is correct.

**Gap for counsel:** Art. 25 (circumstances under which a third party *becomes* a provider, e.g. substantial modification or rebranding) is not addressed. The Art. 16 vs Art. 26 boundary is not static; counsel should confirm whether a reference to Art. 25 is needed.

### 4. Operator GDPR programmes (ARSIA-State, section 7.3)

**Assessment: no additional issue.** Same marker, closes the audit section. Covered by the analysis of item 2.

---

## Part B. Surviving positive claims (verb "satisfy"): priority for downgrade

### 5. ARSIA-Actions, section 3.5, "Regulatory satisfaction"

**Assessment: partial overreach. Verb downgrade recommended before counsel review.**

- **Art. 17 (quality management system):** overreach. The QMS is an organisational system of the provider (policies, procedures, resources). Audit records can *evidence* parts of it; they cannot "satisfy" it.
- **Art. 26(6) (deployer log retention):** closer, but "satisfy" still overstates. The article requires deployers to keep automatically generated logs, to the extent under their control, for a period appropriate to the intended purpose and at least six months, unless Union or national law provides otherwise. The records operationalize this obligation; "satisfy" ignores the scope qualifier ("under their control"), the appropriateness of the period, and sector-law extensions. Note also that financial-institution deployers keep these logs under Union financial services law documentation rules.

**Recommended wording:** "provide technical records that support the operator's compliance with [articles]", plus the standard "statement subject to legal review" marker.

**Dependency:** these claims rest on the tamper-evidence scope of State section 7.2 (see item 10). The records are tamper-evident against third parties, not against the operator itself. Any satisfaction language must be read against that scope; this is an independent reason for the downgrade.

### 6. ARSIA-Actions, section 6, note 3 (Art. 13(1))

**Assessment: strongest overreach in the text. Downgrade before counsel review.**

Art. 13(1) requires the high-risk AI system to be *designed and developed* in such a way that its operation is sufficiently transparent for deployers to interpret the output and use it appropriately. It is a design obligation on the provider of the high-risk system. A protocol explanation object plus audit trail is at most a contributing technical capability (compare Art. 13(3)(b)(iv) and (vii), which list output-explanation capabilities and output-interpretation information as instruction-for-use content). "The combination of the explanation object and the audit trail satisfies EU AI Act Article 13(1)" is not defensible as written.

**Recommended treatment:** same downgrade pattern as item 5.

---

## Part C. Responsibility delimitations (verify boundary placement)

### 7. DORA (ARSIA-Assets, section 6.2.4)

**Assessment: correct.** Incident classification as major or minor is the financial entity's function under DORA Art. 18, with classification criteria in Delegated Regulation (EU) 2024/1772 (RTS on classification of ICT-related incidents). Boundary well drawn. Counsel to confirm whether the RTS should be cited alongside Art. 18/19.

### 8. Erasure vs MiFID II retention (ARSIA-State, section 5.3.2)

**Assessment: guidance is weaker than the law supports.**

MiFID II Art. 16(7) requires records of telephone conversations and electronic communications to be kept for five years and, where requested by the competent authority, for up to seven years. This is consistent with the P1827D floor. A five-year statutory retention duty is a legal obligation, which falls squarely within GDPR Art. 17(3)(b). The current wording ("the operator MAY argue that MiFID II retention takes precedence") understates the standard framing.

**Counsel decision:** either endorse a firmer formulation ("the retention obligation under Art. 16(7) constitutes a legal obligation within the meaning of Art. 17(3)(b)") or remove the guidance.

**Caution on the pseudonymisation alternative:** a pseudonymised record may not fulfil the evidential purpose of Art. 16(7). Counsel should assess before endorsing that suggestion.

### 9. Identifiers without PII (ARSIA-Core, section 13.3, item 1)

**Assessment: correct.** "A design rule, not a guarantee" aligns with A-21 and with the contextual approach of C-413/23 P (a sole proprietor's org segment may relate to a natural person; linkability governs).

### 10. Tamper-evidence scope (ARSIA-State, section 7.2, finding A-22)

**Assessment: correct and load-bearing.** The explicit non-detection list (owner rewrite, tail truncation, write omission, fork) means the audit trail is tamper-evident against third-party modification only, not against operator fraud. This scope conditions every logging-related satisfaction claim (items 5 and 6). Keep the list; it is what makes the downgraded wording defensible.

---

## Part D. Umbrella: known-limitations item 13 (article-by-article verification)

### D.1 Verified correct

| Citation | Verification result |
|---|---|
| EU AI Act Arts. 13, 14, 17, 26, 50 | Article numbering matches the final text of Regulation (EU) 2024/1689. Art. 50 covers limited-risk transparency obligations, matching EU-AI-ACT-LIMITED-RISK. |
| P6M floor | Supported by Art. 19 (provider log retention, at least six months) and Art. 26(6) (deployer log retention, at least six months), both extensible by sector law. Suggest adding Art. 19 to the cited list; it is the provider-side counterpart and is currently absent. |
| MiFID II Art. 16(7) → P1827D | Five years, up to seven on competent-authority request. 5 x 365 + 2 leap days = 1827. Consistent. |
| PSD2 Art. 97 | Correct article for SCA. |
| GDPR Arts. 6, 9, 17, 30 | Correct subjects (lawful basis, special categories, erasure, records of processing). |
| DORA Arts. 17, 18, 19 | Correct subjects (incident management process, classification, reporting). |
| DSA Art. 37 as an audit obligation | Correct subject (annual independent audits of VLOPs/VLOSEs). Incorrect as a retention basis; see D.2. |

### D.2 Errors found (correction required)

**PAC: "Regulation 2021/2116 Art. 60" as basis for P1096D. Wrong article.**

Art. 60 of Regulation (EU) 2021/2116 is titled "Rules regarding checks to be carried out" and governs Member State management and control systems: systematic risk-targeted checks and sampling. It contains no retention period.

The correct basis for the three-year floor:

- **Regulation (EU) 2021/2116, Art. 51** (Access to documents): paying agencies keep supporting documents relating to payments and checks at the Commission's disposal; the storage period is delegated to Commission implementing acts under Art. 51(3).
- **Implementing Regulation (EU) 2022/128, Art. 34** (Conservation of accounting information): EAGF documents kept for 3 years following the year in which the Commission clears the accounts; EAFRD documents at least 3 years following the year of final payment by the paying agency; in cases of irregularity, at least 3 years following the year of full recovery; conformity-procedure documents at least 1 year after conclusion of the procedure.

**Additional nuance for counsel:** the three-year clocks are event-anchored (clearance, final payment, recovery), not anchored to record creation. A fixed P1096D counted from record creation can undershoot the legal obligation. Counsel to decide whether the profile floor should be reformulated as event-conditional or documented as a conservative approximation requiring extension when the anchoring events occur later.

**DSA: "Art. 37" as basis for P731D. Wrong article and unsupported duration.**

Art. 37 of Regulation (EU) 2022/2065 establishes annual independent audits; it contains no retention period. No basis for a two-year (P731D) retention floor was located anywhere in the DSA.

The DSA's documentation-retention rule is **Art. 34(3)**: providers of VLOPs and VLOSEs shall preserve the supporting documents of risk assessments for at least three years after the performance of the risk assessments, and communicate them on request to the Commission and the Digital Services Coordinator of establishment.

If the DSA-VLOP profile intends a documentation floor, the correct citation is Art. 34(3) with a three-year duration (approximately P1096D), not Art. 37 with P731D. Two corrections: the cited article and, most likely, the duration value.

### D.3 Timing fact relevant to counsel

The EU AI Act high-risk obligations, previously applicable from 2 August 2026, were deferred by the Digital Omnibus: 2 December 2027 for stand-alone Annex III high-risk systems and 2 August 2028 for high-risk systems embedded in regulated products under Annex I. Any applicability dates stated in profiles or spec prose must reflect this. Formal adoption status should be re-checked at review time.
