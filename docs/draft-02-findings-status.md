<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Draft-02 Findings Status Matrix (Phase 0 baseline)

**Source audit:** `docs/auditoria-spec-draft-01.md` — SHA-256 `abc61eba97d59c1bb319fc637524171c8377d205170e92e55e711aa437252472`, committed at `e557f83`. The audit targeted `arsia-protocol-enterprise @ dacbc4a`; this matrix records reproduction against **this** repo (`draft-02` @ `9064744`). The independent-audit addendum file referenced by audit §8 is absent here; addendum findings (B-07/B-08, A-16..A-22, M-25..M-31) were reproduced from the §8 summary plus current spec text.

**Baseline verification results (2026-07-22):**
- `validate_vectors.py`: 613 vectors — 540 pass (415 message + 125 data), 73 skip, 0 fail. `--check-crypto`: **83/83 crypto-block vectors verified** (Ed25519 over RFC 8785 canonical form) → audit NOT-VERIFIED item 1 resolved. Note: ~220 vectors carry `security` objects; only 83 carry full `crypto` blocks.
- Schema meta-validation: **31/31** files valid against JSON Schema Draft 2020-12 → NOT-VERIFIED item 3 partially resolved (full content review below).
- RTM header-driven parser: **1994 data rows** (Core 392, State 400, Assets 353, Actions 328, Identity 259, Routing 262); **1153 MUST/MUST_NOT** — exactly reproduces the audit's addendum figure; 843 rows with neither schema nor vector. (Naive `grep '^|'` gives 2074 because it counts sub-table headers.) → NOT-VERIFIED item 7 resolved with reproducible numbers.
- Spec JSON examples: 66 fenced blocks, 61 parse; 5 are deliberate `...`-ellipsis fragments (Actions:337, 942, 1138; Identity:931; State:2900) — editorial annotation queued in Phase 3.
- `results/` is empty (`.gitkeep`) → NOT-VERIFIED items 8 and the FAQ-vs-results divergence are SUPERSEDED here; the `results/` conformance report will be regenerated in Phase 6.
- Skip classification (initial, from `test-vectors/README.md`, per-ID detail in Phase 6): Temporal/clock 36, Token/credential 10, X.509 7, Cross-field 6, Cross-object 5, Non-delegable capability 3, Forward-compat 3, Transport-specific 3 = 73.

**Status vocabulary:** CONFIRMED · PARTIAL · ALREADY-FIXED · SUPERSEDED · RECLASSIFY(sev) · NOT-REPRODUCED.

## Blockers

| ID | Status | Evidence (current tree) | Affected files | Dependencies | Decision |
|----|--------|------------------------|----------------|--------------|----------|
| B-01 | CONFIRMED | Core:436-437 ("id of the original request message") vs Core:713-714 & Actions:1245 ("NOT the original request's id"); rejection path Actions:1340-1344 | Core §2.2/§4.2.1, Actions §3.3/§3.4, both RTMs | — | D: correlation = previous message + mandatory `root_request_id` (approved) |
| B-02 | CONFIRMED | Core:929-931 clamp MUST vs Core:1117-1118 reject MUST (R4); State:568-571 `max()` clamp; STATE-13 (State:3202-3210) tests reject; zero Rule-4 vectors (`insufficient_retention` = 0 hits) | Core §4.3.6.4/§4.3.7/§4.3.8, State §8.3 + STATE-13, both compliance schemas, vectors, RTMs | A-15, M-18, M-31 | **D1 approved**: global reject, typed durations |
| B-03 | CONFIRMED | 1825 in Assets:705,935,1138,1843,1858,2480; Actions:825,2400; Identity:1730 (miscites State §6.3). 1827 everywhere else (Core, State, Routing, FAQ, schemas, profiles, vectors). Assets RTM:231 & mifid schema already say 1827 → RTM currently contradicts its own spec | Assets, Actions, Identity prose only | B-02 (consequence of floor) | Standardize 1827 (audit direction) |
| B-04 | CONFIRMED | Actions:215-217 closed list §1.4 (:358-604) omits `echo`/`health`/`onboarding.evaluate`; used at Core:3326, Core:3486, Identity:1105, plus Identity:1589-1599 policy examples | Actions §1.1/§1.4, Core §4.4.1/A.1/A.3, Identity §7/§8, RTMs, vectors | B-07, M-16 | Registry per plan (approved direction) |
| B-05 | CONFIRMED | Routing:308-309 & 977-978 (sender token needs `broker.relay`) vs Actions:389 (broker-only); Routing:321 (broker's own token) vs Core:1702 (`sub`==`from`) + Core:650-653 (reject `unauthorized`); no delegation mechanism | Routing §1.2.2/§2.3/§7.3, Core §6.2/§6.4/§4.1.4/§9.2, Actions §1.4, jwt-claims schema, RTMs, vectors | A-17, A-01, B-04 | **D2 approved**: dual authorization + attestation |
| B-06 | CONFIRMED | Assets:1711 `payload.result`, :1755 `decision:"rejected"`, :1830 enum `rejected/timeout`; ASSETS-06 (Assets:2440-2443) vs Actions:1140-1148 `payload.args`, Actions:1268-1269 `approved/denied`, State:2739 `approved/denied/expired`, message schema :335/:397-409. **Both conformance tests contradict each other** (Actions:2249 vs ASSETS-06) | Assets §5.2/§6.1.1/§7, mifid schema enum, vectors | M-07 | Actions/Core/schema side canonical (approved direction) |
| B-07 | CONFIRMED | Core:1710-1711 "exact string comparison (no wildcards, no hierarchical expansion)" in §6.4 step 5 (the authorization comparison itself) vs Actions:234-235 + ACTIONS-03 (Actions:2236-2239, `notes.*` satisfies `notes.read`). New informative note Core:1713-1717 acknowledges but does not resolve | Core §6.4, Actions §1.2 + ACTIONS-03, RTMs | B-04 (non-delegable list) | Single algorithm w/ wildcard expansion (approved direction) |
| B-08 | CONFIRMED | State:466-470 "MUST NOT be returned as `1` … MAY normalize" — contradiction in one sentence; JCS (State:3427 ref) serializes 1.0→1 | State §2.1.2, state-entry schema, audit payload_hash semantics | D4 | **D4 approved**: value semantics + decimal strings |

## High findings

| ID | Status | Evidence | Affected files | Dependencies | Decision |
|----|--------|----------|----------------|--------------|----------|
| A-01 | CONFIRMED | Core:1400-1401, Identity:419-420 ("on the sender's domain"), Identity:149-150; no resolution mechanism anywhere | Core §5.2/§9.1/§7.1, Identity §1.1/§3.1, Routing §1.2.1 | blocks B-05, A-17 | Yes — resolution mechanism (Phase 1 minimal slice) |
| A-02 | CONFIRMED | Identity:409-410 (every message MUST carry security) vs Core:867-872 (optional for event/error) | Identity §3.1, Core §4.3.5/§5.2, FAQ | — | Yes — per-intent signature matrix |
| A-03 | CONFIRMED | Core:1099-1100, :899 — strict mode never defined; no discovery flag | Core §4.3.6.1/§4.3.8/§7.1, discovery schema | M-18 | Yes — define flag or remove |
| A-04 | CONFIRMED | Identity:868-878 four snake_case codes; Core:2723-2741 registry+reverse-domain convention; message schema :895-898 legitimizes them | Identity §6.4.3, Core §11.2, message schema (2 enum copies) | M-14 item 1 | Yes — register w/ HTTP status |
| A-05 | CONFIRMED | State:2733-2734 declared-only + "none"; profile-absent case undefined; audit-record schema has no resolved fields (only `retained_until` :150) | State §7.1, audit-record + audit-query-response schemas, vectors | A-06, M-19; structural core lands with D1 | **Partially decided** (D1 core); remainder Phase 2 |
| A-06 | CONFIRMED | Identity:512-514 both-parties MUST vs audit-record schema `operator_id` only + `additionalProperties:false`; Identity:567 also mandates deployer_id | Identity §4.1/§4.4, State §7.1, audit-record schema | A-05, M-30 | Yes — extend record |
| A-07 | CONFIRMED | message schema :459 `additionalProperties:false` vs Core:613-616 ("MUST be handled gracefully… SHOULD be ignored"), Core:2077 (forwarding MUST preserve). Prose is SHOULD-ignore (softer than audit implied) but contradiction real | message + discovery schemas, Core §4.1.1/§9.2 | A-08, M-12; minimal slice in Phase 1 (pre-regeneration) | Yes — v2 version/schema strategy |
| A-08 | CONFIRMED | Core:1267-1269 (warn + process intent field) vs message schema :838-857 `not anyOf` | Core §4.4.7, message schema, vectors | A-07 | Yes — pick one side |
| A-09 | CONFIRMED | compliance-field :112-126 + message schema :1424-1448 require explicit `human_oversight` for high-risk vs Core:1108-1111 (profile default suffices) | both schemas, Core §4.3.8 R3, ITV-421 | M-18 | Yes — drop conditional required |
| A-10 | CONFIRMED | Assets:1835 `updated_at` in-place vs Assets:1854-1856 + State:2799 append-only immutable | Assets §6.1.1, mifid schema, ASSETS-07 | M-19 | Append correction record (audit direction) |
| A-11 | CONFIRMED | Assets:803-805, :1307-1308 — second receipt with no delivery/correlation mechanism; Core one-reply model | Assets §3.2.1/§4.2, Core §8.1, receipt schema, vectors | M-21, B-01 root id helps | Yes — delivery mechanism |
| A-12 | CONFIRMED | Assets:1799-1800 "EU-regulated entity (as declared in their IdentityRecord)" — no such field in Identity §1.2 or schema (11 properties checked) | Assets §6.1, Identity §1.2, identity-record + mifid schemas | M-17, A-05 | Yes — add field or reword |
| A-13 | CONFIRMED | State:178-179 (session MUST NOT audit) vs State:3035-3037 (audit_required=true → ALL operations MUST audit) | State §1.1/§1.5/§8.3 | — | Yes — precedence rule |
| A-14 | CONFIRMED | Core:2977-3004 six vectors only; Routing:1596 "trust-based"; §5.1 vs §5.2 modal clash (Routing:1494 SHOULD vs :1509-1510 MUST) | Core §13, Routing §5, Actions §1.4, State PURGE, Assets escrow | B-05 attestation helps | Yes — threat-model extension (D2 partially) |
| A-15 | CONFIRMED | compliance-field allOf[2..5] + message schema :737-812: floors (reject) for MIFID-II/PAC/DSA-VLOP/DORA; none for the two EU-AI-ACT profiles; prose clamps for non-MIFID | both schemas, Core §4.3.8, vectors | **D1 approved** | Resolved by D1 |
| A-16 | CONFIRMED | Core:1323-1327 removes whole `security`; §5.2 Step 5 selects algorithm from unsigned `security.alg` (Core:1416-1417); validator mirrors (validate_vectors.py:225, :244); all 83 crypto vectors canonicalize message-minus-security | Core §5.1/§5.2/§13.2, validator, all signed vectors + keypairs | M-25 family | **D3 approved**: sign all but `sig` |
| A-17 | CONFIRMED | Identity:450 "trusted Authorization Server" undefined; Core:1566-1568 self-published JWKS; §6.4 step 3 (Core:1697-1703) never validates `iss` though jwt-claims requires it | Core §6.1/§6.4, Identity §3.2/§9.1, jwt-claims schema | prerequisite for B-05, M-13 | Yes — trust anchor (Phase 1 minimal slice) |
| A-18 | CONFIRMED | Identity:396-398 refetch-on-failure never fires for compromised (verifying) key; Core:1995-1997 unenforceable at cached recipients; internal inconsistency: max-age=3600 (Core:1999) vs 24 h refresh (Core:1429-1433) | Identity §2.5/§3.1, Core §7.3/§5.2 | A-17 | Yes — revocation model |
| A-19 | CONFIRMED | Assets:1766-1767 & 2121-2122 "satisfies PSD2 … SCA at the protocol level"; knowledge-factor claim :2130-2133 | Assets §5.2/§6.3 | A-21 class | Requalify language (approved direction) |
| A-20 | CONFIRMED | Amounts = JSON numbers; request schema :208-379 multipleOf per asset_type; receipt constrains only via `currency_or_unit ^[A-Z]{3}$` (token/entitlement/service_unit receipts unconstrained); reversal & mifid amounts no multipleOf; fixed 2dp breaks BHD/JPY | 5 asset schemas, Assets §2/§3.1.1, vectors | **D4 approved**; N-03 | Resolved by D4 |
| A-21 | CONFIRMED | State:2827-2839 absolutism + self-contradicting hedge in same paragraph; Core:3124 "Agent identifiers contain no PII"; FAQ:157 already correctly hedged | State §7.2, Core §13.3 | A-22 | Conditional language (approved direction) |
| A-22 | CONFIRMED | State:2820-2824, :3389-3391 — detects mid-chain modify/remove vs later-head holder; not: owner recomputation (records unsigned), tail truncation, write-time omission; hash_chain optional | State §7.2/appendix, audit-record schema | A-21, A-14 | Scope the claim (approved direction) |

## Medium findings

| ID | Status | Evidence | Affected files | Dependencies | Decision |
|----|--------|----------|----------------|--------------|----------|
| M-01 | CONFIRMED | State §6.2 (:2233-2240) & §6.3 (:2303-2311) omit clock_skew; §6.7 cites the missing MIFID row; catalog has 120/60/60; Core §8.3 gives normative effect | State §6.2/§6.3 | — | No — add rows |
| M-02 | CONFIRMED | FAQ:85 "2-year uses 731" vs 730 in State:1690/2477/2850, catalog :134, schemas | FAQ or State+catalog+schemas+vectors | B-03 rationale, D1 durations | Yes — 731 vs fix FAQ |
| M-03 | CONFIRMED | Core:1941-1942 `{keyN}` vs Identity:319-321 general form vs jwk-entry :28 pattern | Core §7.3/§4.3.5, Identity §2.2, 2 schemas | — | No — adopt Identity form |
| M-04 | CONFIRMED | Identity:1181-1182 `capabilities` (real: `capabilities_supported`, Core:1770); Identity:1512 wrong path | Identity §7.2/§7.8 | — | No — editorial |
| M-05 | CONFIRMED | Routing:1962 `zone` vs :1995 `residency_zone`; Core:2457-2458 requires `ts` absent from §7.4/schema; two competing record forms | Routing §7.3/§7.4, Core §9.2, State §7.1, 2 schemas, RTM, ITV-43/44 | A-06, M-06, D2 attestation | Yes — unify (folds into D2) |
| M-06 | CONFIRMED | Six lifecycle names (Routing:1255-1357) absent from 17-value enum (State:2654-2657, schema :46-64); `broker_relay` IS present | Routing §4.1, State §7.1, audit-record schema | M-05 | Yes — canonical vs operational |
| M-07 | CONFIRMED | Assets:1265 vs :1389-1390 (DISPUTED non-terminal), :1383-1413 heading/result mismatch; §4.3 `audit_id`/`timestamp` vs schema `record_id`/`processed_at` | Assets §4.2/§4.3, audit-record escrow branches | A-10, M-19, B-06 | No — fix taxonomy |
| M-08 | CONFIRMED | State:386-387 table (owner-only) vs :220-223, :1402 (grantee access); shared-vs-agent+grant undefined | State §1.5/§1.2/§3.3 | — | Yes — keep or merge `shared` |
| M-09 | CONFIRMED | State:765-766 reserves `arsiaprotocol.` but examples :773-774 use `arsia.meta/` | State §2.2 | — | No — rename examples |
| M-10 | CONFIRMED | Routing:596-597 includes `approval_decision`; Core:2153-2154 does not | Routing §2.1.2, Core §8.1 | B-01 | Yes — align lists |
| M-11 | CONFIRMED | Core:905-906 open set; Routing:1475-1477 2-4 chars (2=ISO space; 3-4 fail `^[A-Z]{2}$` in common :35); broker-discovery `residency` free-form | Core §4.3.6.2, Routing §5.1, 4+ schemas | — | Yes — closed registry |
| M-12 | CONFIRMED | message schema :468 lowercase-only `id` vs Core:620-623 (SHOULD lowercase); common uuid-v4 accepts both; correlation_id refs common | message + common schemas, Core §4.1.2 | A-07 family | Yes — decide case |
| M-13 | CONFIRMED | Identity:1693-1695 wildcard audience undefined vs Core:1703 `aud`==`to`; jwt-claims pattern can't express it | Identity §9.1, Core §6.4, jwt-claims | A-17 | Yes — define or remove |
| M-14 | PARTIAL | 4 of 5 reproduced (Identity:870-871 "Core §8"; STATE-13 cites clamp-Rule-2 for a reject; compliance-field :6 "§1.2" imprecise; Actions:1547 unanchored 180d). State §11.5 "§2.1.3" NOT FOUND — §11 ends at 11.4 | per item | item 3→B-02; item 5→M-31 | No — editorial pass w/ link checker |
| M-15 | CONFIRMED | Core:1204-1205 "latest known to receiver"; descriptor schema has zero version fields; **aggravator**: Actions:1020-1021 requires advertising both versions as separate descriptor entries — unimplementable | Core §4.4.2, Actions §2.1/§2.4, 2 schemas | H2, A-07 slice | Yes — H2 fix set |
| M-16 | CONFIRMED | Identity:1385-1390 (onboarding reuses approval_decision, wrong capability + correlation) vs Actions:1294-1298, :1245 | Identity §7.6/§7.1.3, Actions §3.3, onboarding schema, vectors | B-04, B-01 | Yes — exempt or new payload |
| M-17 | CONFIRMED | Assets:901-908 `audit_id` REQUIRED universally; record only mandated for §6.1 conditions; :908 shows visible partial edit | Assets §3.2.1/§6.1, receipt schema | A-12 | Yes — conditional or universal |
| M-18 | CONFIRMED | Core §12.4 = 3 tests covering Rules 2+6 only (:2933-2958); Full conformance depends on external unversioned `@arsia-protocol/conformance-test` (:2927); Rule 4 zero vectors | Core §12.3/§12.4, vectors | B-02, A-03, A-09 | Yes — in-repo runner (plan Phase 6) |
| M-19 | CONFIRMED | State §7.1 prose = 16 base fields (:2637-2780); schema = 50 properties w/ per-event_type extensions documented only in schema | State §7.1, audit-record schema | A-05, A-06, M-05, M-07 → one rewrite | No — document in prose |
| M-20 | CONFIRMED | message schema :383-386 risk_level min 1 vs Actions:700-703 (0-10) | message schema, Actions | — | No — min 0 |
| M-21 | CONFIRMED | Core:2163-2164 (202+Location) vs Actions:1904-1915 (response+status_url); no selection rule | Core §8.1, Actions §4.3 | A-11 | Yes — unify or precedence |
| M-22 | PARTIAL | results/ half SUPERSEDED (dir empty); State:628-632 intra-item contradiction CONFIRMED ("MUST be set … not a hard rejection"); state-entry :96 delegates to runtime; **nbf sub-claim NOT-REPRODUCED** (jwt-claims `additionalProperties:true` since Draft-01, `git show fbb30e7`) | State §2.1.10 | B-02 family | Yes — MUST-reject or SHOULD-warn |
| M-23 | CONFIRMED | Core:1030 per-message `unacceptable-risk` vs Identity:539-540 (reject ALL from such agents) + Identity:206-208 | Core §4.3.6.9/§4.3.8 R6, Identity §4.2, 2 schemas | — | Yes — remove per-message value |
| M-24 | **ALREADY-FIXED** | Core:3609 now ends "licensed under CC BY-SA 4.0 — there are no licensing barriers to adoption"; zero "commercial licence" hits in spec/ or docs/ | — | — | No — owner decision no longer needed |
| M-25 | **RECLASSIFY(HIGH)** | Core:2650-2657 header "takes precedence… MUST use the header value" (unconditional); header unsigned; Core:3031-3034 advertises idempotency as anti-replay. Replay w/ fresh header defeats dedup for the `expires_at` window | Core §10.1-10.4/§13.2.2/§8.1/§8.2 | A-16 class | Envelope field prevails (approved direction) |
| M-26 | PARTIAL | Addendum text unavailable; located: Routing:138-139 "at-least-once (opt-in via idempotency)" vs Core:2583-2584 + Routing:1120-1122 (dedup ≠ delivery guarantee; guarantee comes from §11.3 retries) | Routing §1/§3, Core §10/§11.3 | M-25 | No — clarify terminology |
| M-27 | CONFIRMED (re-scoped) | Disclaimer exists (Assets:2069-2071); residual defect = name `dora_incident` + pre-classification trigger (Assets:1940-1941 "MUST generate a DORA incident event" on any provider timeout) | Assets §6.2.2-6.2.3, State §7.1 enum, 3 schemas, vectors :4269-4275 | rename touches enum+vectors | Yes — rename + trigger rewording |
| M-28 | CONFIRMED | `confidence` in Actions §5.2 (:2070, :2087); unverifiable MUST :2095-2096. Anchor = §5.2 (addendum's §5.3 wrong) | Actions §5.2, explanation schema | — | No |
| M-29 | CONFIRMED | Sandboxing = Actions §4.4 (:1964); ACTIONS-11 :2311. Anchor = §4.4 (addendum's §5.2 wrong) | Actions §4.4 | — | No |
| M-30 | CONFIRMED | Identity:174/193-195 owner "owns and operates" vs :555-566 split model (deployer operates; owner = AI-Act "provider"); :514-516 Art. 26(1) claim mismatched to owner_id | Identity §1.2/§4.1/§4.4, identity-record schema, State §7.1 `operator_id` | A-06 | Yes — role mapping fix |
| M-31 | CONFIRMED | Actions:1544-1547, State:1655-1656, :2275-2278, catalog :48 — "at least six months" rendered as 180 days; 6 calendar months ≤ 184 days | Actions §3.5, State §6.2, catalog, schemas, Core A.2, vectors | **folded into D1** (calendar durations) | Resolved by D1 |

## Low findings (individually tracked)

| ID | Status | Evidence | Decision |
|----|--------|----------|----------|
| X-01 | CONFIRMED | Core:513 example `arsialabs…` vs :516-517 prose "org-segment is 'arsia'" | Fix prose |
| X-02 | CONFIRMED | Core:605 pattern `^\d+\.\d+$` accepts leading zeros prose forbids (:610-611); same in message schema :463, :829 | Tighten pattern (both) |
| X-03 | CONFIRMED | Actions:161, :176 "reserved `arsia`" — real prefix `arsiaprotocol.` (:213) | Wording fix |
| X-04 | CONFIRMED | State:3296-3300 out-of-order paragraph; §2.1.10 never defines authenticated encryption | Rewrite paragraph |
| X-05 | CONFIRMED | State:1934-1935 "only … personal" contradicts :1900-1901, :1921-1923 (personal or sensitive) | Fix sentence |
| X-06 | CONFIRMED | Routing:1981-1982 "(to be defined in ARSIA-State.md §7)" — §7 exists | Delete stale phrase |
| X-07 | PARTIAL | Header divergence NOT reproduced (all six identical). Confirmed: Routing RTM lacks Coverage Gaps section; Core RTM phantom §16 row (:434), no §15 row, §4 count 131 vs actual 136, total 388 vs actual 392 | Regenerate RTM summaries |
| X-08 | CONFIRMED | Core:2696-2697 English-only error description vs :808-809 `context.locale` | Note interaction or SHOULD |

## New defects found in Phase 0 (not in the audit)

| ID | Sev | Evidence | Affected files | Resolution phase |
|----|-----|----------|----------------|------------------|
| N-01 | **BLOCKING** | `arsia-audit-query-response.schema.json` `$defs/AuditRecord` drifted from standalone: `pii_classification` missing `sensitive`; `legal_basis` missing 10 Art. 9(2) values; `pii_special_categories` absent + `additionalProperties:false` → conformant sensitive audit records can never be returned by a valid §7.4 query response | audit-query-response schema | Phase 1 (with D1 audit-record migration) or Phase 5; fix = `$ref` the standalone |
| N-02 | HIGH | `profiles/arsia-compliance-profiles.json` invalid against its own schema: top-level `$comment` (license-header commit 2692450) not whitelisted under `additionalProperties:false`; nothing in CI validates the catalog | catalog + profiles schema + CI | Phase 1 (D1 touches catalog) |
| N-03 | **BLOCKING** | `multipleOf` on binary floats rejects wire-valid amounts: `19.99`/`0.07` EUR fail with the repo's own `jsonschema`; token `1e-08` and service_unit `0.0001` same hazard; current vectors pass only by luck of representable values | asset request + receipt schemas | Resolved by D4 (decimal strings), Phase 1 |
| N-04 | MEDIUM | `arsia-action-discovery-response.schema.json` descriptor copy has a 4th allOf rule (reserved-capability cross-check) the standalone `arsia-action-descriptor.schema.json` lacks — same object validates standalone, fails embedded | 2 action schemas | Phase 5 (with B-04) |
| N-05 | MEDIUM | `arsia-common.schema.json` `$id` is relative (`"arsia-common.schema.json"`) while all others are absolute — strict RFC 3986 resolvers fail every cross-file `$ref` (reproduced with `referencing`); works only via the validator's filename fallback | common schema | Phase 5 |
| N-06 | MEDIUM | `legal_basis`: schemas enumerate 16 values (Art. 6(1)+9(2)) per Rule 8, but Core §4.3.6.8 field definition lists only the 6 Art. 6(1) values — implementer coding from §4.3.6.8 rejects required Art. 9(2) values | Core §4.3.6.8 | Phase 3 |
| N-07 | LOW | receipt `settled_at` description claims "REQUIRED when completed" vs prose SHOULD; schema itself correct | receipt schema | Phase 5 |
| N-08 | LOW | `arsia-state-entry.schema.json` allOf[4] dead rule (empty `then`) — leftover of runtime-delegated invariant | state-entry schema | Phase 5 |
| N-09 | LOW | `arsia-broker-entry.schema.json` `last_health_check` bespoke timestamp pattern (0-6 fractional digits) vs suite-wide `rfc3339-ms-utc` (exactly 3) | broker-entry schema | Phase 5 |
| N-10 | LOW | 3-decimal ISO 4217 currencies (BHD, KWD, JOD, OMR, TND, IQD, LYD) in enum but inexpressible under 2dp rule — prose-origin | Assets §2/§3.1.1 | Resolved by D4 |

## Cross-cutting notes

- **A-16 broader than recorded:** verification algorithm and key are selected from the *unsigned* `security.alg`/`kid` (Core:1416-1417; validator :244) — D3's alg/key-coherence MUSTs address this directly.
- **A-18 internal inconsistency:** JWKS cache bound stated as both 1 h (`max-age=3600`, Core:1999) and 24 h (Core:1429-1433) — resolve in Phase 2 with the revocation model.
- **M-15 aggravator:** version-coexistence rule (Actions:1020-1021) requires per-version descriptor entries the descriptor cannot express — H2 fix must add the field.
- **Dependency spine for Phase 1 order:** B-03 → B-01 → D1(B-02+A-15+M-31+A-05core, incl. N-01/N-02) → B-04 → B-07 → B-06 → A-17/A-01 minimal → B-05(D2, absorbs M-05 relay-audit unification) → B-08/D4(+A-20/N-03/N-10) → A-07 minimal → v2 signer → D3+D5 regeneration.
- **Tally:** 8/8 blockers CONFIRMED · 22/22 high CONFIRMED (A-15/A-16/A-20 resolved-by-decision) · mediums: 26 CONFIRMED, 3 PARTIAL (M-14, M-22, M-26), 1 ALREADY-FIXED (M-24), 1 RECLASSIFY→HIGH (M-25) · lows: 7 CONFIRMED, 1 PARTIAL (X-07) · 10 new defects (2 blocking, 1 high, 3 medium, 4 low).
