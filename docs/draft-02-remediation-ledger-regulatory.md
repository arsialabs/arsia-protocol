<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Draft-02 Remediation Ledger — Regulatory Register

Part of the [Draft-02 remediation ledger](draft-02-remediation-ledger.md). This file
holds the regulatory citation register (§5), the regulatory Open notes (§8) and the
C2 and C2.1 closure evidence (§9, §11). Section numbers are those of the main ledger,
so existing references stay valid. Counts are per register and never merged with
those of any other register.

## 5. Regulatory citation register

- **V items:** provisions, verdicts and sources come from the regulatory
  verification report (EUR-Lex PDFs, verified 2026-09-25 at `fb5a875`).
- **T items:** verified in the triage session against the official
  non-EUR-Lex texts named.
- **O items:** verified by the orchestrator on EUR-Lex web pages, not on files
  in the sources folder.
- **X items:** verified in the retention-axis cycle (2026-11-03) on the EUR-Lex
  consolidations in the sources folder (`consolidated/`).

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
| A-48 | T-2 | ETSI EN 319 412-5: "any QcStatements" wording | CORRECT (restrictive reading) | ETSI EN 319 412-5 (triage) | `official host (C2); out of scope of OD-4 pass` | CORRECT (C0); no remediation |
| A-49 | T-3 | RFC 9449 §4.3: Core receiver checks omit ath | DEFECT | RFC 9449 (triage) | `official host (C2); out of scope of OD-4 pass` | closed (C2) |
| A-49 | T-4 | RFC 9449 §4.3: Identity omits typ/alg checks | DEFECT | RFC 9449 (triage) | `official host (C2); out of scope of OD-4 pass` | closed (C2) |
| A-49 | T-5 | RFC 9449 §4.2: the schema forbids nonce | DEFECT | RFC 9449 (triage) | `official host (C2); out of scope of OD-4 pass` | closed (C2) |
| A-49 | T-6 | RFC 9449 §4.3: jti replay as a requirement | CORRECT (not required) | RFC 9449 (triage) | `official host (C2); out of scope of OD-4 pass` | CORRECT (C0); no remediation |
| A-50 | T-7 | W3C Trace Context: all-zero ids accepted | DEFECT | W3C Trace Context (triage) | `official host (C2); out of scope of OD-4 pass` | closed (C2) |
| A-51 | T-8 | BCP 14: MAY used as a prohibition | DEFECT | BCP 14 (triage) | `official host (C2); out of scope of OD-4 pass` | closed (C2) |
| A-52 | T-9 | EDPB Guidelines 05/2021 v2.0 dated Feb 2022; the correct date is 14 Feb 2023 | DEFECT | EDPB (triage) | `official host (C2); out of scope of OD-4 pass` | closed (C2) |
| A-49 | T-10 | RFC 9449 §4.3: Identity §3.3 omitted checks 1-3 (one well-formed DPoP header field; required claims), 7 (no private key in `jwk`) and 10 (nonce match); Core §6.3 omitted the `typ`/`alg` checks (C2 residual) | DEFECT | rfc-editor.org `rfc9449.txt` | `RFC 9449 (September 2023), read 2026-11-04` | closed (relay/DPoP cycle) |
| A-49 | T-11 | RFC 9449 §9, §8.2, §11.3: a resource server provides a nonce with HTTP 401, `WWW-Authenticate: DPoP error="use_dpop_nonce"` and `DPoP-Nonce`; a nonce is accepted only by the server that issued it; once a nonce has been provided, no proof without the nonce claim is accepted — basis of Identity §3.3 and Routing §2.3.3 | CORRECT | rfc-editor.org `rfc9449.txt` | `RFC 9449 (September 2023), read 2026-11-04` | closed (relay/DPoP cycle) |
| A-49 | T-12 | RFC 9449 §11.1, §7.3: `jti` tracking is optional ("may not always be feasible in practice") and a unique proof is recommended on retries; Identity §3.3 states single use as an ARSIA requirement, not as a requirement of the RFC | CORRECT | rfc-editor.org `rfc9449.txt` | `RFC 9449 (September 2023), read 2026-11-04` | closed (relay/DPoP cycle) |
| A-44 | O-1 | Del. Reg. (EU) 2017/565 labelled "RTS 22"; RTS 22 is 2017/590 | DEFECT | EUR-Lex web page (orchestrator) | `02017R0565-20220802; 32017R0590 original` | closed (C2); currency confirmed 2026-09-28 |
| A-70 | X-1 | MiFIR, Reg. (EU) No 600/2014, Art. 25(1): investment firms keep "for five years, the relevant data relating to all orders and all transactions in financial instruments"; basis of the MIFID-II floor for the records it covers | CORRECT | EUR-Lex `consolidated/02014R0600-20251123.pdf` | `02014R0600-20251123` | closed (retention-axis cycle) |
| A-90 | X-2 | MiFID II Art. 72 cited for retention precedence over erasure (State §7.1); Art. 72 is "Exercise of supervisory powers and powers to impose sanctions" | DEFECT | EUR-Lex `consolidated/02014L0065-20260606.pdf` | `02014L0065-20260606` | closed (retention-axis cycle) |
| A-70, A-44 | X-3 | Del. Reg. (EU) 2017/565 Art. 72 presented as implementing MiFID II Art. 16(7) and as a source of the five-year period; its heading is "Retention of records (Article 16(6) of Directive 2014/65/EU)" and it sets no period | DEFECT | EUR-Lex `consolidated/02017R0565-20220802.pdf` | `02017R0565-20220802` | closed (retention-axis cycle) |
| A-96 | X-4 | DORA, Reg. (EU) 2022/2554, Art. 6(5) described as a review "on the basis of lessons learnt" that five years of records cover; the article provides for review at least once a year (periodically for microenterprises), after major ICT-related incidents and after supervisory instructions or testing and audit conclusions, and for continuous improvement, and does not establish a retention period for the records covered by the profile | DEFECT | EUR-Lex `32022R2554.pdf` | `32022R2554 original (no consolidation retrievable); no amending act; corrigenda R(01)-R(09) not EN (EUR-Lex 2026-11-05)` | closed (DORA floor cycle) |
| A-96 | X-5 | Five years presented as aligned with "European financial sector retention floors (CRD IV, Solvency II, IORP II)"; the consolidations read do not support a common floor of that kind | DEFECT | EUR-Lex `consolidated/02013L0036-20260711.pdf`, `02013R0575-20260626.pdf`, `02009L0138-20250117.pdf`, `02016L2341-20250117.pdf` | `consolidations of 11.07.2026, 26.06.2026, 17.01.2025, 17.01.2025 (current on EUR-Lex 2026-11-05)` | closed (DORA floor cycle) |
| A-96 | X-6 | Delegated Regulation (EU) 2024/1774 Art. 12(2): log retention set considering purpose, business and information security objectives, the reason for recording and the ICT risk assessment; Art. 22(d) as corrected: incident evidence retained no longer than necessary, commensurate with criticality, in accordance with Art. 8(2) of Delegated Regulation (EU) 2024/1772 and applicable Union-law retention requirements — basis of the qualification in State §6.7 | CORRECT | EUR-Lex `32024R1774.pdf`, `corrigenda/32024R1774R(02)-EN.pdf` | `32024R1774 original; consolidation 02024R1774-20240625 v000.002 incorporates corrigendum R(02) of 15.05.2025 as C1 ("Article 15" replaced by "Article 8(2)" in Art. 22(d))` | closed (DORA floor cycle) |
| A-48 | O-2 | eIDAS 2.0 described as a "Proposal … anticipated"; it is Reg. (EU) 2024/1183, in force | DEFECT | EUR-Lex web page (orchestrator) | `32024R1183 original; manifest status "In force"` | closed (C2); currency confirmed 2026-09-28 |

**Totals (this register only, 43 rows).**
- Defects: 33 (19 V + 8 T + 2 O + 4 X).
- Correct: 10 (4 V + 4 T + 2 X).
- Unverified: 0.
- State: closed 27 (C2 corrections; currency confirmed 2026-09-28 for the V and O items); reopened 2 (V-5 → A-71; V-21, CORRECT at C0, → A-72); CORRECT with currency confirmed 3 (V-20, V-22, V-23); CORRECT (C0), no remediation 2 (T-2, T-6; out of scope of the OD-4 pass); closed 3 (X-1..X-3, retention-axis cycle); closed 3 (T-10..T-12, relay/DPoP cycle); closed 3 (X-4..X-6, DORA floor cycle).
- X items (retention-axis cycle, 3; DORA floor cycle, 3): closed 6; not part of the 2026-09-28 currency pass.
- T-10..T-12 (relay/DPoP cycle, 3): closed 3; verified on the RFC text, not part of the 2026-09-28 currency pass.
- Currency totals (26 items): CONFIRMADO 24 / REABERTO 2 / PENDENTE 0; A-70 apart: evidence complete, finding closed in the retention-axis cycle ([§19][ev19]).

## 8. Open notes (regulatory)

- **Regulatory count provenance:** the cumulative regulatory count relies on
  O-1/O-2, verified by the orchestrator on EUR-Lex web pages, not on files in
  the sources folder.
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
- **RFC 9449 §4.3 residual (C2 observation, tracked in A-49):** Identity
  §3.3 omitted checks 1-3 (single, well-formed DPoP header; required claims),
  7 (no private key in `jwk`) and 10 (nonce match); Core §6.3 omitted the
  `typ`/`alg` checks. Closed in the relay/DPoP cycle (T-10; [§20][ev20]).
- **Art. 14 mentions reviewed under A-69 (C2):** the remaining mentions were
  reviewed and none attributes per-action pre-execution approval to Art. 14.
  - Actions l.392 (Art. 14(1), a human in the decision loop);
  - Actions l.1011-1017 (framed as "the protocol's strongest
    interpretation");
  - Core l.1292-1293 (Rule 3, DR-3 scope);
  - Identity l.1332 (CHECK-03, signalling per gateway policy);
  - State l.2552 (limited-risk contrast).
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
- **Actions risk-tier table notes (C2.1 observation):** the Risk 7–8 table still reads
  "Article 14 human oversight applies." and "Article 13 transparency is mandatory."
  (Actions l.990-991), in the present tense. These are not among the nine A-73
  sentences, so they were left for the DR-3/DR-4 framing question. C3b: added to the
  A-73 open remainder.

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
| A-70 (verification) | State l.2395-2400: the fabricated Art. 72 quotation replaced by what Art. 72 provides. The floor and its echoes are unchanged (A-70). | Searched (whitespace-insensitive, local PDFs): Del. Reg. (EU) 2017/565 Arts. 72-76 and Annexes I and IV; Dir. 2014/65/EU Art. 16(6)-(7). Art. 72 sets no period. The only five-year periods found are Art. 76(8) (a copy of recordings "available on request for a period of five years") and Art. 16(7) (communications records "kept for a period of five years"). Other acts (e.g. Reg. (EU) No 600/2014) were not consulted, since they are not among the supplied sources. | EUR-Lex `32017R0565.pdf`, `32014L0065.pdf` | closed (A-70, retention-axis cycle; MiFIR Art. 25(1) verified as X-1; [§19][ev19]) |

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

[ev19]: draft-02-remediation-ledger-evidence.md#19-retention-axis-cycle-closure-evidence
[ev20]: draft-02-remediation-ledger-evidence.md#20-relaydpop-cycle-closure-evidence
[ev22]: draft-02-remediation-ledger-evidence.md#22-dora-floor-cycle-closure-evidence
