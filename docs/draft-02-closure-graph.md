<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Draft-02 Closure Graph — Item-by-Item De Facto Verification of the Draft-01 Audit

**Date:** 2026-07-29 · **Source audit:** `docs/auditoria-spec-draft-01.md`
(SHA-256 `abc61eba97d59c1bb319fc637524171c8377d205170e92e55e711aa437252472`,
committed at `e557f83`) · **Tree:** branch `draft-02`, uncommitted Draft-02 state.

**Method.** Every item of the audit — the 69 consolidated findings (B-01..B-08,
A-01..A-22, M-01..M-31, X-01..X-08), the §4 hypothesis verdicts (H1–H4), the §5.2
untested-MUST clusters, the §6 NOT-VERIFIED items 1–8, and the §7/§8 revision and
addendum notes — was checked **against the current tree** (not against status
documents): the claimed fix was located at its anchor, and a targeted orphan sweep
searched the whole repository for surviving mentions of each superseded rule, name,
value, or claim. Four verification passes over ~60 findings preceded this closure
pass (evidence in `docs/draft-02-findings-status.md`, DR-* records in
`docs/draft-02-decisions.md`); the residuals they found were fixed in **DR-P8**;
this pass re-verified everything after DR-P8 and found and fixed 4 further orphans
(§ "Orphans found in this pass" below).

**Graph legend.** Each entry lists its edges:
`⇐` resolved-by (a decision or another finding's fix resolves this one) ·
`⇒` prerequisite-of · `∪` absorbed/unified-with · `†` closed-by-status (no edit) ·
`↻` hardened in DR-P8 (secondary-site residual fixed after the first resolution).

**Verification state at time of writing** (all reproducible):
`validate_vectors.py --check-meta --check-errors --check-crypto` → 649 vectors,
0 fail, crypto 83/83 · `check_consistency.py` ALL PASSED (incl. guards added in
DR-P8/closure: schema-description + vector-description `retention_days`, duplicate
RTM IDs) · `runtime_harness.py` R1–R13 ALL PASSED · `extract_examples.py` 76 blocks
= 71 full (9 envelope-validated) + 5 fragments, 0 failures · `check_links.py`
1,326 § references, 0 dangling · `rtm_counts.py` 1903 rows / 1109 MUST+MUST_NOT
(deduplicated).

---

## 1. Blockers (8/8 resolved de facto, no orphans)

| ID | De facto state (evidence) | Graph edges | Orphans |
|----|---------------------------|-------------|---------|
| B-01 | `correlation_id` = immediate causal parent (Core §2.2:435, §4.2.1:758); `root_request_id` normative (Core §4.2.4, 13 refs; schema requires it on all reply intents and prohibits it on `request`, message schema allOf) | ⇒ H3 (made a new relation mechanism unnecessary) · ⇒ M-16, A-11 (their follow-up-request pattern uses `args.original_request_id` because root is schema-prohibited on `request`) | none: "id of the original request message" definition gone from §2.2 |
| B-02 | Global reject, no clamp: Core §4.3.8 Rule 4; State §2.1.8 item 3 "MUST NOT silently raise (\"clamp\")"; STATE-13 expects reject with full details (State:3398) | ⇐ D1 (with A-15, M-31, A-05 core) · ⇒ M-22 (same family) | every `clamp` mention in spec/ is a negation, the calendar end-of-month rule, or the unrelated query-limit clamp (State:1230) |
| B-03 | 1827 everywhere; CI guard `no 1825 outside compat notes` | ⇒ first Phase-1 step of the dependency spine | zero `1825` outside Draft-01 compat notes (CI-enforced) |
| B-04 | Actions §1.4 closed registry now defines `arsiaprotocol.echo` (:643), `health` (:657), `onboarding.evaluate` (:670), `broker.use` (:683); registry↔descriptor-enum parity CI-checked | ⇒ B-07 (non-delegable list), M-16, D2 (`broker.use`) | zero `arsiaprotocol.code.review`/`test.unit` (policy examples moved off the reserved prefix) |
| B-05 | Dual authorization implemented: sender uses `broker.use`; broker declares `broker.relay` (Routing:284); byte-identical forwarding; `authorization.token_hash` binding in message schema; signed relay attestation (`arsia-relay-attestation.schema.json`, headers `ARSIA-Relay-Attestation`/`-Authorization` in Routing §2/§7.4); recipient checks incl. hash match; runtime vectors ITV-570/571/572 | ⇐ D2 · ⇐ prerequisites A-17-min + A-01-min · ∪ M-05 (relay-audit unification) · partial A-14 (attestation = detectability) | no rule requiring `broker.relay` from the *sender* survives |
| B-06 | Canonical contract only: `payload.args` for pending_approval; enums `approved\|denied` / `denied\|expired` (Assets §6.1.1:1948 aligns to Actions §3.3/State §7.1); ASSETS-06 rewritten | ⇒ M-07 (escrow records aligned in same family) | zero `"rejected"`/`"timeout"` oversight enum values in spec/ |
| B-07 | One algorithm in Actions §1.2, referenced by Core §6.4 step 5 (Core:2033); wildcard = final-segment only; reserved namespace never wildcard-matched (Core:2036-2038); ACTIONS-03 cases as vectors | ⇐ B-04 | Core §6.4 no longer contains a competing "exact match, no wildcards" rule for the same comparison |
| B-08 | State §2.1.2 rewritten to JSON **value** semantics (`1.0` ≡ `1`, JCS-normalization MAY; State:483-487) | ⇐ D4 (with A-20, N-03, N-10) | no "MUST NOT be returned as `1`" lexical-fidelity rule survives |

## 2. High findings (22/22 resolved de facto; 5 hardened in DR-P8)

| ID | De facto state (evidence) | Graph edges | Orphans |
|----|---------------------------|-------------|---------|
| A-01 | Core §6.6 (:2093) registry-based agent-id→origin resolution: authenticated out-of-band mapping, deterministic, no heuristic derivation, fail-closed `unauthorized`, caching tied to §7.3; wired from Core §5.2/§6.4, Identity §3.1, Routing §1.2/§7 | ⇒ B-05, A-17 | "on the sender's domain" gone from Identity |
| A-02 | Per-intent signature matrix: Identity §3.1 restricted to the four signed intents + compliance-event carve-out; Core §5.2 mirrors and (↻ DR-P8) now cross-references the carve-out; schema conditionally requires `security` for exactly those intents | — | "Every ARSIA message MUST carry" gone |
| A-03 | Strict mode normatively defined (Core §4.3.8:1266-1274): per-agent, discovery-declared `strict_compliance` (Core §7.1 table :2170 + discovery schema :135), test case both paths | ⇒ M-18 (CORE-COMPLIANCE-05) | none |
| A-04 | 4 certificate codes registered in Core §11.2 (:3167-3170, HTTP 401, non-retryable); Identity §6.4.3 cross-references the registry | ∪ M-14 item 1 (the "Core §8" anchor) | none |
| A-05 | Audit record carries declared **and** resolved: `compliance_profile_declared`/`_resolved` (State §7.1:2783/2792), `declared_retention`/`effective_retention`/`retention_anchor`/`retained_until`/`retention_source` (schema :466-495); profile-absent case defined | ⇐ D1 (structural core) + DR-P2 (remainder) · ⇒ A-06, M-19 | none |
| A-06 | `counterparty_owner_id` in schema (:497) + State §7.1 runtime-required rule + append-record backfill; Identity §4.1 names both fields | ⇒ M-30 (role model) · ⇐ A-05 family | none |
| A-07 | Version-handling model (Core §4.1.1:629-633): schemas validate exactly one minor; minimal parser accepts any `2.x`; unknown fields preserved in signing input; envelope schema deliberately strict per-minor (documented, no longer a contradiction) | ⇒ D5, M-12, M-15/H2 | none |
| A-08 | Hard mutual exclusivity, prose = schema (Core §4.4.7:1482-1503, intent→field table, reject `invalid_request`) | ⇒ M-16 (forced the onboarding `args` migration) | none |
| A-09 | Schema conditional removed (compliance-field allOf keeps only pii→legal_basis); Rule 3 checks **effective** oversight; ITV-421 (profile default) + ITV-579 (reject) + harness R10 | — | none |
| A-10 | `updated_at` removed from MiFID prose, schema, and all 6 vectors; append-only corrections via `original_audit_id` | ⇒ M-19 | zero `updated_at` in mifid schema/Assets §6.1 |
| A-11 | Subsequent-receipt delivery normative (Assets §3.2.1:848-874): new `request` from processor, `args.original_request_id`, idempotency key scheme, ack + `delivery_failed` fallback, escrow covered | ⇐ B-01 (root/`original_request_id` pattern) · ⇒ M-21 (status-URL fallback) | none |
| A-12 | `regulated_entity` object in IdentityRecord (Identity §1.2:210, schema :99-118) + deterministic trigger fallback in Assets §6.1 (absent on both ⇒ only via resolved MIFID-II profile) | ⇒ M-17 | none |
| A-13 | Precedence stated on both sides (State §1.1:178-182 and §8.3 rule 4 :3214-3223, scope table row); both paths in harness R12, negative path ITV-181 | — | none |
| A-14 | Threat model = 12 adversaries with explicit `Mitigations:`/`Residual:` (Core §13.1:3471-3544: broker bypass, compromised approver, wrongful PURGE, escrow abuse, residency evasion, splicing); Routing §5.1/§5.2 modal clash resolved ("the MUST governs", Routing:1603) | ⇐ D2 partially (attestation = broker-bypass detectability) · ⇒ A-22 | none (leftover absolutist phrases fixed in DR-P8/closure) |
| A-15 | Schemas format-only for retention; floors are runtime calendar comparison, uniform for all profiles | ⇐ **D1** (resolved-by-decision) | none |
| A-16 | Signing input = envelope minus only `security.sig` (Core §5.1:939, §5.2 staged pipeline with alg/key-coherence steps); validator + 83 crypto vectors under the v2 profile | ⇐ **D3** + D5 regeneration · ⇐ M-25 family | DR-P7 #3 swept the survivors (Routing step 3, CHECK-02) |
| A-17 | Core §6.5 (:2063) issuer trust configuration (issuer id, key origin — never from the token, audience policy, alg allowlist, fail-closed); `iss` exact-match in §6.4 step 3; harness R11 | ⇐ prerequisite-of B-05 · ⇒ A-18, M-13 | no undefined "trusted Authorization Server" left |
| A-18 | 3600 s single cache ceiling; JWKS-removal = authoritative revocation; `arsiaprotocol.identity/key-revocation` event; fetch-timestamp audit MUST (Core §5.2:1716-1748); harness R13. ↻ DR-P8: `jwks_fetched_at` schema field added; Identity §2.5/§3.1 aligned (refetch-on-failure demoted to the benign rotation-lag case) | ⇐ A-17 | none; the defective refetch-on-failure model no longer stated anywhere as the revocation mechanism |
| A-19 | SCA claims qualified at **all** sites: §5.1.2 (primary) and ↻ DR-P8 §1.1.8, §6.3 intro, §6.3.1 Limitations — "controls that can serve as SCA elements; whether a deployment satisfies SCA is the PSP's legal determination (subject to legal review)" | class-sibling of A-21 | remaining "satisfies SCA" strings are all inside the qualified/negated sentences |
| A-20 | Decimal-string amounts, fixed ISO 4217 scale, JPY/EUR/KWD vectors | ⇐ **D4** · ⇒ N-03, N-10 | ↻ closure: last `multipleOf` narration in ITV-118 description fixed |
| A-21 | GDPR claims conditional: State §7.2 hash/linkability passage (:2998-3016), Core §13.3 item 1 design-rule-not-guarantee; ↻ DR-P8 trailing absolutist sentence requalified | ⇒ A-22 | none |
| A-22 | Tamper-evidence scope statement (State §7.2:2975: detected vs NOT detected — full rewrite, tail truncation, write-time omission, fork; "MUST NOT claim stronger"); §11.4 bounded claim | ⇐ A-21/A-14 family | ↻ DR-P8 Actions "Regulatory satisfaction" + State §11.2 phrases; ↻ closure: escrow "complete, immutable history" (Assets:1504) re-scoped |

## 3. Medium findings (31/31 closed; 1 by status; 7 hardened after first resolution)

| ID | De facto state (evidence) | Graph edges | Orphans |
|----|---------------------------|-------------|---------|
| M-01 | `clock_skew_seconds` rows present in State §6.2/§6.3 tables (4 mentions); catalog parity CI-checked (3 profiles) | ⇐ D1 catalog pass | none |
| M-02 | DSA-VLOP = `P731D` in catalog + State + schemas; FAQ rationale consistent | ⇐ D1 durations · ↻ closure: ITV-559 still declared `P730D` under DSA-VLOP → fixed to P731D | none |
| M-03 | One kid contract: Core §7.3 `{key-index}` = Identity §2.2 general form (Core:2329-2332); jwk-entry `kid-format` matches | ↻ DR-P8: relay-attestation kid pattern aligned to the common form | no `{keyN}` sequential-label rule left |
| M-04 | `capabilities_supported` + `/.well-known/arsia` corrected in Identity §7.2/§7.4/§7.8 | — | zero `agent.json` in normative artifacts |
| M-05 | Unified: `arsia-broker-relay-audit.schema.json` **deleted**; relay audit = `ArsiaAuditRecord` `event_type: broker_relay` with required extensions incl. `message_ts`, `residency_zone` (audit-record schema :855-877); wire evidence = relay attestation | ∪ **D2** · ⇐ A-06/M-06 family | "BrokerRelayAuditRecord" survives only in negations and vector migration notes |
| M-06 | Routing lifecycle events declared **operational log**, normatively excluded from the canonical enum (Routing §4.1:1294-1305); prose enum = schema enum (17 values); ↻ DR-P8 reciprocal cross-reference added in State §7.1 | ⇐ M-05 | none |
| M-07 | Taxonomy fixed (DISPUTED intermediate; cancellation → RETURNED; Assets §4.2:1341-47, §4.2.4 heading); ↻ DR-P8: §4.3.2/3/4 `audit_id` → `record_id` (§4.3.1 had been fixed alone, creating a self-contradiction) | ⇐ B-06/A-10/M-19 family | none |
| M-08 | Scope table row corrected (grantees via GRANT); shared-vs-grant normative guidance; ↻ DR-P8: guidance blockquote had been inserted mid-table breaking the markdown → moved below the table | — | none |
| M-09 | Examples use `arsiaprotocol.meta/…` (State §2.2:810); vector updated | — | zero `arsia.meta` |
| M-10 | Lists aligned to Core §8.1; Routing §2.1.2 (:655) explicitly states `approval_decision` is never a synchronous inbox response | ⇐ B-01 | none |
| M-11 | Closed normative registry (Routing §5.1:1573-1581, exactly `EU`; custom codes removed; Core §4.3.6.2 references it); schema pattern coherent (`^[A-Z]{2}$`); registry membership is a documented runtime rule | ↻ DR-P8: "pending Phase 3" stale marker replaced with the registry citation | none |
| M-12 | Uniform: both cases valid, SHOULD produce lowercase (Core §4.1.2:668; message schema = common `uuid-v4` pattern) | ⇐ A-07 family | none |
| M-13 | Wildcard audiences removed: Identity §9.1 (:1762) states they are NOT defined; `aud` = single agent-id (jwt-claims `$ref`); Core §6.4 `aud`==`to` | ⇐ A-17 | ↻ closure: IDENT-§9.1-07 RTM row still stated the old SHOULD → fixed |
| M-14 | 4/5 anchors fixed (Identity §6.4.3→§11.2; STATE-13→Rule 4; compliance-field `$comment`; Actions §3.5 →`P6M` with explicit no-risk-level-floor statement). Item 2 (State §11.5 "§2.1.3") **† NOT-REPRODUCED** — State §11 ends at §11.4, zero "§2.1.3" citations | ⇒ `scripts/check_links.py` (M-14's systematic sweep is now CI: 1,326 refs, 0 dangling) | none |
| M-15 | `supported_versions` on the descriptor (schema :117-129, single-entry migration, Actions §2.1/§2.4); deterministic absent-version default `"1.0"` (Core §4.4.2:1424); ↻ DR-P8: Actions §2.4 "latest supported version" negotiation paragraph — the original defect — replaced | ⇐ H2 fix set · ⇐ A-07 slice | "latest version known" survives only inside the Draft-01 parenthetical |
| M-16 | Dedicated payload `arsiaprotocol.onboarding/decision` on a **new `request`** (Identity §7.6:1413-21); ↻ DR-P8 full sweep: schema `required: [type, args]` + `args.original_request_id`; §7.6 example moved to `args`; §9.3 audit-label-vs-wire-intent note; vectors ITV-03/04/482 migrated off the abolished intent (+`expires_at`, onboarding capability) and **re-signed**; ITV-38/130/131/474 data renamed | ⇐ B-04, B-01, A-08 | none |
| M-17 | Universal-record route: every receipt MUST have its audit record regardless of profile (Assets §3.2.1:975-980); `audit_id` stays REQUIRED, coherently; ↻ DR-P8 stale schema description aligned | ⇐ A-12 | none |
| M-18 | In-repo runner is the normative criterion (Core §12.3 table :3364 — versioned scripts, "no external, unversioned package"); CORE-COMPLIANCE-04..09 close the Rules 1/3/4/5/7/8 gap; Rule 4 now has vectors (`insufficient_retention` INV set) | ⇒ Phase-6 conformance chain | ↻ closure: Assets §7 (:2356) still cited `@arsia-protocol/conformance-test` → fixed |
| M-19 | Per-event-type extensions documented in prose (State §7.1:2919 normative subsection + table); ↻ DR-P8: table's nonexistent enum names fixed (`state_revoke`, `asset_transfer`+`sub_type`; `state_snapshot` removed) and `jwks_fetched_at` row added | ⇐ A-05/A-06/M-05/M-07 (one rewrite) | none |
| M-20 | `risk_level` minimum 0 in message schema (:178) | — | none |
| M-21 | One async pattern, two surfaces (Core §8.1:2564 — 202+Location MUST over HTTP, URLs identical when both present); ↻ DR-P8 back-reference added at the Actions §4.3 `status_url` site | ⇐ A-11 | none |
| M-22 | results/ half **† SUPERSEDED** (dir was empty; report regenerated from scratch in `results/draft-02-conformance-report.md`); State §2.1.10 contradiction fixed (SHOULD + warning, "deliberately not a hard rejection", :668); nbf sub-claim was NOT-REPRODUCED | ⇐ B-02 family | none |
| M-23 | `unacceptable-risk` removed from the per-message enum (compliance-field :79-83; Core §4.3.6.9:1169 explicit reject rule); agent-level value retained; negative vector | — | Rule 6 ordering correctly still lists it (agent-level comparison) |
| M-24 | **† ALREADY-FIXED** upstream: Core ends "licensed under CC BY-SA 4.0 — no licensing barriers"; zero commercial-licence language in this snapshot | owner decision no longer needed | none |
| M-25 | RECLASSIFIED HIGH and fixed: signed envelope authoritative (Core §10.4:3072); ↻ DR-P8: Routing header-table row — which still granted the header override *citing §10.4* — rewritten; the §13.2.2 anti-replay note now actually exists | ⇐ A-16 class · ⇒ M-26 | none |
| M-26 | Delivery terminology decoupled from dedup (Routing §1.1:138-140, §3.1/§3.2:1206-1213: retries deliver, idempotency deduplicates) | ⇐ M-25 | none |
| M-27 | Renamed `ict_incident` / `arsiaprotocol.ict/incident` everywhere (spec, State enum, audit-record + dora-incident schemas, 8 vector occurrences); candidate-trigger rewording (Assets §6.2.2: persists-after-retries / multi-operation / operator policy; transient timeout is NOT an incident); ↻ DR-P8 stale Assets RTM row fixed | — | `dora_incident` only in CHANGELOG/history; schema filename retains `dora` (contents correct — deliberate) |
| M-28 | `confidence` anchor confirmed §5.2 (addendum's §5.3 was wrong) | anchor-correction only | none |
| M-29 | Sandboxing anchor confirmed §4.4 (addendum's §5.2 was wrong) | anchor-correction only | none |
| M-30 | Role model: Identity §4.4 many-to-many mapping, "records accountability identities, does not adjudicate regulatory roles"; ↻ DR-P8: §4.1 Art. 26(1) "satisfies" claim requalified; "owns and operates" removed from §1.1 Layer 3, `owner_id`, and the identity-record schema | ⇐ A-06 | none |
| M-31 | "6 months" = `P6M` calendar duration (catalog :68, Actions §3.5, State §6.2) | ⇐ **D1** (folded) | none |

## 4. Low findings (8/8 closed)

| ID | De facto state | Edges | Orphans |
|----|----------------|-------|---------|
| X-01 | Core §3.2 prose says "arsialabs" (:527) | — | none |
| X-02 | Envelope `v` = `const "2.0"` (strictest); prose pattern `^(0\|[1-9]\d*)\.(0\|[1-9]\d*)$`; ↻ DR-P8: the 6 remaining loose version patterns (message details/payload.version, discovery protocol_version/server_min/max) tightened | ⇐ D5 | none |
| X-03 | Uniform "reserved `arsiaprotocol.`" wording in Actions | — | none |
| X-04 | State §10.4 rewritten; AEAD defined in place, §2.1.10 mis-reference corrected; ↻ DR-P8 duplicated sentence removed | — | none |
| X-05 | "personal or sensitive" for legal_basis (State §5.2:1943 + Art. 9(2) list) | ⇐ N-06 family | none |
| X-06 | "(to be defined …)" phrase gone; Routing §7.4 fully specified | ⇐ M-05/D2 | none |
| X-07 | RTM summaries regenerated; Routing gained Coverage section; Core phantom §16 row gone; Draft-02 delta tables in all six; ↻ DR-P8: duplicate Coverage sections removed from 4 RTMs and the Assets double-count (91 stale 8-column duplicate rows) eliminated — published totals corrected to 1903/1109; duplicate-ID CI guard added | ⇒ corrected `rtm_counts` figures everywhere | none |
| X-08 | English `description` + optional `details.localized_description` interaction defined (Core §11.1:3125) | — | none |

## 5. Hypotheses (H1–H4)

| H | Verdict → Draft-02 outcome |
|---|----------------------------|
| H1 (no profile extension mechanism) | CONFIRMED → **defined**: extension profiles in reverse-domain notation (Core §4.3.6.1:1245), collision rule, discovery via `compliance_profiles_supported`, unknown-profile behaviour incl. strict mode (A-03) — DR-H |
| H2 (no payload-type versioning) | REFUTED-strong / gaps CONFIRMED → gaps fixed: `supported_versions` (M-15), deterministic default (M-15), uniform rule for non-action payload types (DR-H) |
| H3 (no typed causal reference) | CONFIRMED → assessed after B-01: `root_request_id` + `correlation_id` + typed fields suffice; no new mechanism added (deliberate, DR-H) |
| H4 (single-axis temporality) | CONFIRMED → **deliberately deferred**; recorded as known limitation #14 with mitigations (audit-record `timestamp` vs `processed_at`; append-only version history) |

## 6. Audit §5.2 — untested-MUST clusters

Each §5.2 row now maps to an executable check, a classified skip, or a documented
verification procedure (no silent gaps; classes per `docs/draft-02-skip-classification.md`
and the Core §12.3 gates):

| §5.2 cluster | Now |
|--------------|-----|
| Idempotency retention/duplicate/409 | harness (idempotency precedence) + M-25 rules; integration-class procedure documented |
| Post-`expires_at` processing | temporal skip class + runtime rule |
| Receiver-side broker/residency enforcement | D2: recipient MUST require attestation (Routing §5.2); vectors ITV-570/571/572; adversary #7/#11 residuals recorded |
| Compliance Rules 1,3,4,5,7,8 | CORE-COMPLIANCE-04..09; Rule 4 vectors added (`insufficient_retention`); R10 harness |
| `oversight_timeout` (`required_within_24h`) | enum exercised in vectors (ITV-18 family, ITV-93→approval_expired record); deadline expiry itself = temporal skip class |
| Media type `v` param / 415 | D5 propagation + `no v=1 media type left` CI check; transport-class procedure |
| WebSocket auth/close/heartbeat | transport-specific skip class + documented procedure |
| Key rotation/revocation/JWKS cache | A-18: harness R13 (ceiling refresh, stale key, unknown kid) |
| Physical retention / archival | deployment-inspection class (gates) |
| PURGE propagation/grants/idempotency | operational-evidence class + adversary #9 |
| At-rest encryption (personal/sensitive) | X-04 AEAD rule; deployment-inspection class |
| Sandboxing per risk tier | deployment-inspection class (M-29 anchor §4.4) |
| Two-party AS token separation | harness R11 audience/issuer cases + operational-evidence class |
| DORA infra-vs-business classification | M-27 candidate model; integration-class (recorded as documented non-tested, DR-P7 #16) |
| Certificates chain/SAN/revocation L3 | X.509 skip class + A-04 error codes |
| Onboarding order/deny-by-default/exact scope | M-16 contract + onboarding schema; integration-class procedure |

## 7. Audit §6 — NOT VERIFIED items 1–8

| # | Item | Closed by |
|---|------|-----------|
| 1 | Vector crypto not recomputed | `--check-crypto` 83/83 under the v2 profile (CI) |
| 2 | Vector file not reviewed vector-by-vector | meta-schema check + error-path verification + selective regeneration with logged affected set; closure pass fixed the last narration orphans (ITV-539, ITV-118, ITV-559 value) |
| 3 | Schemas only spot-read | 31/31 meta-validated + full Phase-5 pass + strict `$ref` resolution CI check |
| 4 | External references not followed | M-18: external runner reference replaced (Core §12.3, Assets §7); remaining URLs are informative |
| 5 | Legal-citation accuracy | out of scope, unchanged: qualified language everywhere (A-19/A-21/M-30) + known-limitations §13 + owner legal-review checklist item |
| 6 | Scripts not audited line-by-line | validator hardened + 5 new verification scripts, all CI-run and reproducible |
| 7 | RTM counts accepted as declared | header-driven `rtm_counts.py`; closure pass found and removed the Assets double-count → deduplicated 1903/1109 + duplicate-ID guard |
| 8 | FAQ 613 vs results 559 divergence | superseded: results/ was empty at baseline; report regenerated (649 vectors) |

## 8. Audit §7/§8 notes (revision + addendum)

- §7 corrections (compliance-field duplication risk, M-22 restatement, M-18 rule
  coverage): all absorbed — duplication resolved via `$ref` single source (N-01/N-04
  same class), M-22/M-18 closed above. The *lex specialis* note on B-02 became moot
  (single global rule).
- §8 addendum bookkeeping: the "638 MUSTs without vector" figure was never
  republished (non-reproducible); reproducible counts stand at 1903/1109. M-28/M-29
  anchor errata recorded. The 8 lows were tracked individually (never compressed).
  The addendum file itself is absent from this repo — reproduction was done from §8
  plus current text, recorded in the findings-status matrix.

## 9. Orphans found in this closure pass (all fixed)

1. Assets §4.3.1 (:1504): "complete, immutable history" of escrow → re-scoped to
   append-only + §7.2 bounded tamper evidence (A-22 class).
2. Assets §7 (:2356): external `@arsia-protocol/conformance-test` still cited as the
   test executor → in-repo runner per Core §12.3 (M-18 class).
3. `docs/rtm/ARSIA-Identity.rtm.md` IDENT-§9.1-07: still stated the wildcard-audience
   SHOULD that M-13 removed → aligned.
4. ITV-118 description: narrated the removed `multipleOf` mechanism → rewritten to
   the decimal-string scale rule (N-03/A-20 class).

## 10. Accepted residuals (deliberate, documented — not open items)

- Residency registry membership, retention floors, and cross-field rules are
  **runtime rules** by design (schemas format-only) — classified in the skip doc.
- `arsia-dora-incident.schema.json` keeps its filename (contents use `ict_incident`);
  renaming the file would churn `$id`s for a cosmetic gain.
- Audit `event_type: "approval_decision"` remains the audit label for onboarding
  decisions (queryability); the wire intent is `request` — the distinction is stated
  normatively in Identity §7.6/§9.3.
- Integration/deployment/operational/legal requirement classes are verified by
  documented procedures, not suite tests (Core §12.3 gates) — the mission's explicit
  boundary.
- Prose↔prose contradiction is now partially machine-guarded (DR-P9): prose-enum ↔
  schema-enum parity and the cross-document RTM drift linter (modal/value drift on
  near-identical requirements, self-tested). Contradictions written once in two
  genuinely different phrasings remain a matter for adversarial review and interop.

## Conclusion

Every item of `docs/auditoria-spec-draft-01.md` — 69 findings, 4 hypotheses, the
§5.2 clusters, the §6 NOT-VERIFIED list, and the §7/§8 notes — is accounted for
with a de facto verified terminal state: 65 findings resolved by edits in this tree
(several hardened twice: first resolution, then DR-P8 secondary-site sweep, then
this closure pass), 3 closed by status with evidence (M-24 already-fixed; M-14 item
2 not-reproduced; M-22 results-half superseded), 1 reclassified and fixed (M-25 →
HIGH). The dependency spine held (B-03 → B-01 → D1 → B-04 → B-07 → B-06 →
A-17/A-01 → D2 → D4 → A-07 → D3/D5 regeneration), and the graph shows no dangling
edge: no finding's fix reintroduced another's defect, and the orphan sweep over the
whole repository returns only negations, migration notes, and historical records.
