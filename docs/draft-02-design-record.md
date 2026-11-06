<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Draft-02 Design Record

Owner decisions governing the Draft-02 (wire 2.0) remediation. Each record
states the findings it resolves, the decision, its design requirements, the
normative changes it implies, and its dependencies. Decisions were proposed
in the owner's own analysis, reviewed by the orchestrator, and approved by
the owner on 2026-09-26. Audit baseline: `51610ac` (rewritten from
`fb5a875`, identical tree).

Provenance legend: **P** proposal, **R** orchestrator review, **A** owner
approval.

---

## DR-0 — Cross-cutting requirements

Apply to every record below.

1. **One resolution component.** DR-1, DR-3 and DR-4 describe a single
   procedure — resolution of effective obligations from authenticated
   sources into per-axis requirements — seen from three angles. The
   specification MUST define it once (a dedicated Core section) and have
   Rule 3, profile application, gateway policy and Assets reference it.
   Defining it in more than one place recreates the defect class this
   remediation removes.
2. **Regulatory attribution.** Where a profile imposes a control (e.g.
   pre-execution approval), the prose attributes it as the profile's
   technical choice, never as a literal requirement of the regulation
   unless the official text says so. AI Act Art. 14 requires oversight
   measures proportionate to risk, autonomy and context; it does not
   mandate per-transaction pre-approval. (Tracked as A-69.)
3. **Vectors and MAY-level behaviour.** A conformance vector whose
   expected outcome rests on a MAY must declare the posture it assumes; the
   vector cycle defines how such vectors are expressed. (Origin: ITV-545.)
4. **The 32 runtime-only structural failures** are classified
   individually before any edit: defective data / outdated expectation /
   case requiring a distinct validation procedure (e.g. ITV-405 tests
   version compatibility and must not be forced through the strict 2.0
   schema).

**Addendum — 2026-11-01 (owner decisions for the vector cycle, VC).**
- **V1 — Signatures.** A runtime vector whose cause lies past signature verification
  carries a real signature, so that it reaches its intended cause: the 24 requests and
  responses among the 32 without one, and INV-25 once re-expressed, are signed with a
  `crypto` block, using six new deterministic keypairs. Every `crypto` block declares
  `expect_signature` (`valid`, `invalid`, `absent`), independent of `valid`,
  `expected` and `expected_error`; it replaces the A-34 proxy. `absent` marks a message
  deliberately without `security`, checked on canonical bytes only and never counted
  as signature verification.
- **V2 — Version handling.** The validator applies Core §4.1.1 by the message's own
  `v`: the exact schema for 2.0, the major-2 compatibility schema for a newer 2.x
  minor (unknown top-level and payload fields accepted, known fields kept, content
  fields still exclusive), rejection with `not_implemented` for another major. It is a
  validation procedure, not a skip bypass.
- **V3 — ITV-438.** It keeps `v: "2.0"` and becomes the explicit negative of rule 1
  (failing on `additionalProperties` at the root); ITV-406, at 2.1, carries the
  acceptance of a newer minor with unknown fields.
- **V4 — Linked fixtures.** The CTV-08..10 chain and the five ITV decision ↔ pending
  pairs are corrected, together with the incidental pending ↔ reference request
  relations; a guard checks every declared link, and a deliberate negative fails only
  its stated relation. This is fixture consistency, not the approval-chain coverage of
  A-57.
- **V5 — Timing.** Harness rule R16 runs the six timing vectors against a declared
  recipient clock, keeping temporal causes apart from compliance causes; ITV-546 passes
  on time and is rejected for `missing_legal_basis` and `insufficient_retention`.
- **DR-0.3 expression.** A vector whose expectation rests on a MAY or an optional
  configuration carries `posture` (`spec`, `section`, `basis`, verbatim `text`,
  `assumes`); the expectation holds for an implementation that takes the option.
- **Contract corrections at review.** Branch discrimination in the compatibility
  schema (the relaxed payload branches otherwise overlap on error payloads); the G3
  inventory completed before execution (INV-14, ITV-401, INV-17, ITV-478..481, the
  ITV-479 re-expression, explicit recipients); the policy-identity guard keyed by
  (gateway, `policy_version`) as Identity §8.1 states; ITV-547's `data_residency: null`
  omitted.

**Addendum — 2026-11-04 (owner decisions for the tools cycle, under DR-0).**
- **F1 — `gen_state_vec2.py` retired.** The one-shot generator of ITV-215..277 is
  removed with its scripts/README entry. It had been applied, refused the existing
  IDs, emitted Draft-01 wire, gave an outcome different from the declared expectation
  for 18 of its 63 vectors under the current schemas, and no longer reproduced the 19
  vectors whose `message`/`data` later cycles changed. A-40's dry-run criterion is
  preserved in the ledger and closed by this disposition: the generator was not
  ported and no dry run of it passed. The corpus is the maintained source of these
  vectors; the generator remains their historical origin. Historical documents are
  unchanged.
- **F2 — `regen_v2.py` a selective re-signer.** `--ids` is required (no automatic
  selection), the run is dry unless `--apply`, and an unknown or ineligible ID aborts
  it with nothing written. Only `crypto.expect_signature: "valid"` vectors are
  eligible; negatives and `absent` blocks are fixtures. Only the signature and its
  derived crypto fields change; alg/key compatibility and the key pair are checked
  before signing, and the produced signature is verified before writing. Unselected
  vectors and the file format are preserved. The one-shot Draft-02 migration
  (`migrate_message`, `stringify_amounts`, the special cases) is removed: run today it
  would have rewritten the negative INV-41, re-signed ES256 vectors and appended a
  final newline. ES256 signatures may still differ between explicit runs.
- **F3 — `envelope_hash` kept and documented.** Its docstring states its purpose
  (Routing §7.4.1), that no tool calls it, that on its own it does not verify an
  attestation, and that attestation coverage stays with A-56; it is not evidence for
  A-56.
- **F4 — Coverage `executed: --check-crypto`.** The skip-classification vocabulary
  gains this value for signature negatives (`expect_signature: "invalid"`) whose
  decisive expectation is the signature failure: INV-18, INV-19 and the A-33
  negatives INV-111 and INV-112. A `crypto` block alone does not mean a vector's
  runtime expectation is executed; the guard admits the value only for signature
  negatives. The A-33 negatives carry the wrong alg before the signed bytes are
  computed, agree on bytes and both signature copies, verify under the key's own
  algorithm, and are rejected for the alg/key incompatibility; a verifier that selects
  the algorithm from the key material accepts them.

**Addendum — 2026-11-05 (owner decisions for coverage SC1, under DR-0).**
- **Programme split.** The ten open coverage findings run in four sub-cycles, each
  with its own plan, review and commit: SC1 signatures and bindings (A-54, A-55,
  A-56); SC2 approval and revocation (A-57, A-58); SC3 parsing, examples and timing
  (A-61, A-63, A-62); SC4 traceability (A-53, A-64), last, consuming the evidence of
  the others. The historical counts in the descriptions of A-53 and A-64 are not the
  current inventory.
- **K1 — Mechanism.** `--check-crypto` also reads `data` of the two signed-object
  schemas (message, relay attestation) and of no other; harness R21 (`token_binding`)
  compares the hash of the presented token's exact octets with
  `authorization.token_hash` — it does not test the token's validity, authorization or
  DPoP; harness R22 (`attestation`) verifies the broker's authorisation for the zone,
  the binding to the complete signed envelope and to the token, the identities, the
  window and the replay rule of Routing §7.4.1, with the attestation signature inside
  its acceptance path (reusing the validator's verifier). Binding and replay negatives
  keep a valid signature. The replay rule rejects only an `attestation_id` reused for
  a different `envelope_hash`.
- **K2 — A-54.** Discriminating guards prove how each negative was built, including the
  correspondence between the kid and the key actually used; INV-39 is rebuilt as a
  Draft-01 signature presented to a Draft-02 verifier.
- **K3 — Keys.** Two test keys in `keypairs.json` (15 → 17), with the identifiers the
  fixtures already use (`agent:arsialabs.broker.eu-west#2026q1`,
  `agent:acme.echo-client#other-key`); an additional key of an agent is indexed by its
  kid, so the existing entries and their consumers are unchanged.
- **K4 — A-55.** The `synthetic-token:<ID>` convention of the 40 existing bindings is
  documented and executed; they show that the binding holds, not that the message is
  accepted. New scenarios state the presented token explicitly, including the mismatch
  that must yield `unauthorized`.
- **Review adjustments.** R22's clock skew is the envelope profile's (Core §8.3; 120 s
  for CTV-02), with window negatives that separate 120 s from 300 s; INV-125's
  adversarial JWKS publishes the foreign key so that only the kid's membership rejects
  it.

**Addendum — 2026-11-05 (owner decisions for coverage SC2, under DR-0).** Normative
alignments, listed for the GitHub Issue (CONTRIBUTING §4).
- **L1 — Approval verification order.** One order for every `approval_decision`,
  approved or denied: signature → `unauthorized`; access token (Core §6.4 steps 2–3,
  §6.5, including `sub`/`aud`) → `unauthorized`; `arsiaprotocol.oversight.approve`
  matched exactly in the token scope and present in `capabilities` → `forbidden`;
  correlation, root, `request_payload_hash` and `approver_id` = `from` →
  `invalid_request`; then deadline and pending state; then the decision applies. An
  invalid decision neither approves nor denies. The error to the original requester on
  expiry and the handling of a late decision toward the approver stay distinct; the
  SHOULD replies stay SHOULD.
- **L2 — Deadline.** No clock skew: in time when received strictly before the
  `approval_deadline`, on the executing agent's clock, independent of the decision's
  `ts` and of the timer (precedent: Actions §3.9.4). The skew still applies to external
  timestamps and to the token. The equality with `pending_approval.expires_at` stays and
  grants no extension.
- **L3 — `verified_kid`.** New audit field, present together with `jwks_fetched_at`.
  The schema states the joint presence; the obligation to carry both on the record of a
  verified compliance-relevant message is Core §5.2's, at runtime; the harness proves
  the emission, the key and the fetch instant actually used, also from the cache.
  `verified_kid` means a successful verification; `jwks_fetched_at` is the fetch
  instant.
- **L4 — Key-revocation event.** `payload.data` = {`revoked_kid`, `effective_at`},
  closed schema; `revoked_kid` and the signing key belong to `from`; the signing key is
  published and differs from `revoked_kid`; invalidation only after authentication;
  removal from the JWKS stays the authoritative signal; `effective_at` never delays the
  immediate invalidation.
- **L5 — `decision_rejected`.** New event type, common to approval and review
  decisions, recording the received message (its correlation as received) with
  `rejection_code`: verification failures, duplicates, late arrivals that prevent
  admission. A valid late review decision stays `review_decision` with `late: true`.
  Not a Record 3, not an approval, does not consume the approver, changes no outcome;
  logged whether or not an `error` is sent; `verified_kid` only if the signature
  verified. §3.5 and §3.6 count "decisions verified and admitted to the flow".
- **Plan-review adjustments.** R1 duplicate and deadline give `invalid_request` only
  when no earlier step failed (late + invalid signature → `unauthorized`); R2 Path 3
  only for a still-pending flow, after the decisions received before the deadline are
  verified, §3.6 rule 3 qualified; R3 an unauthenticated event causes no invalidation,
  ordinary JWKS refreshes from resolving its key are unaffected; R4 the token signature
  is executed (JWS under the trusted issuer's configured key); R6 the deadline echoes
  (§3.2, §3.6 rule 4, state machine) refer to the Path 3 conditions; R7 the receipt
  instant decides only the deadline, signature, key resolution and token are evaluated
  at the verification instant.

**Addendum — 2026-11-05 (owner decisions for coverage SC3, under DR-0).**
- **P1 — Raw vectors.** Parsing vectors carry the exact received bytes (`raw_hex`) in a
  fourth test-corpus format, exclusive of the other three both ways; they exercise only
  the Core §5.2 pipeline steps 2–4, with accepted controls as well as rejections. The
  tools load every artifact through the same strict parser; a duplicate in the corpus
  stops them. The new contract is documented for consumers; changing the SDK
  repositories is outside the cycle.
- **P2 — Scope and code (normative).** Rejected with `invalid_request`: invalid UTF-8,
  an unpaired surrogate, a noncharacter (member names and strings, literal or escaped,
  any depth), a duplicate member name after escape processing; a valid surrogate pair
  stays accepted ([RFC 7493] §§2.1–2.3). No general ban on integers beyond ±(2^53−1);
  RFC 8785 canonicalization and ARSIA-State §2.1.2 still apply; `NaN`/`Infinity` are
  not JSON.
- **P3 — Example annotations.** Every full example in `spec/` carries an annotation:
  complete validation, `template` (only the declared placeholder values and the
  constraints they prevent), `partial` (only the declared omissions; shown members,
  nested `required` included, still constrained) or `no-schema` with a reason;
  annotations never make malformed JSON valid.
- **P4 — null optionals.** The approval_decision examples omit `reason`/`conditions`
  without a value; the harness stops emitting `null`; R15 validates the decisions it
  builds as fixture quality, outside the normative order; the schema is unchanged.
- **Plan-review adjustments.** R1 no heuristic (best_match) decides an exemption;
  combinators are re-evaluated on all branches, two valid oneOf branches remain a
  failure; R2 the raw format is exclusive both ways; R3 escaped bytes are explicit, the
  detectors of the parser mutations are fixed; R4 duplicates are preserved through the
  parse and the checks run 2 → 3 → 4; objects and arrays stay distinct in the
  intermediate tree.

**Addendum — 2026-11-05 (owner decisions for coverage SC4, under DR-0).**
- **A-53 — Named tests.** Each of the 89 named tests is classified by what the
  repository executes: `integral`, `partial` (the part not executed stated),
  `equivalent` (the equivalence stated), `external` (requires execution against an
  implementation; the class does not state that it took place) or `absent` (no reference
  model; the reason stated). A rule cited, or a test ID in a check name, is not by itself
  evidence of integral execution. CHECK-01..05 are listed apart with their links, without
  duplicated execution. No new harness model is built. Assets §7 keeps "MUST pass all
  eight tests" and says the runner executes only the parts identified as executed.
- **A-64 — Evidence column.** Every MUST, MUST_NOT and REQUIRED row carries an
  `Evidence` cell with a closed vocabulary that separates documentary reference
  (`schema-ref`, which asserts no enforcement), structural execution and behavioural
  execution; a row may carry several tokens; `untested` and `out-of-repo` carry a coded
  reason and are never evidence of a passed test. The guard checks each token against
  the executions of the same run. Every row is checked mechanically; the gaps, the
  runtime-only citations and the obsolete rows are reviewed by hand. The closure is one
  of traceability: schema references are verified mechanically, without a full semantic
  review of each schema's ability to enforce each requirement.
- **Routing §7.4.1 (normative clarification).** When the attestation is required, a
  missing header gives `service_unavailable` with the residency details; a present header
  — including an empty one — that fails decoding, JSON, structure or verification gives
  `unauthorized`. Decoding, the Core §5.2 steps 2–4 checks and the schema precede the
  signature, in step 2; the envelope's own parsing errors are unchanged.
- **base64url.** The header is base64url without padding, as an explicit ARSIA rule
  (RFC 4648 §3.2 otherwise requires padding).
- **Corpus header.** `version` 2.0.0 for the Draft-02 corpus (incompatible with the
  1.0.x corpora); `generated` is fixed when the revision is prepared and kept; `$schema`
  is unchanged; the guard checks this configuration without coupling the corpus and wire
  majors.
- **Plan-review adjustments.** R1 the validator returns its observed result per vector
  for the structural, raw and crypto modes, and every token is checked against it (a
  negative passes when its rejection is observed); R2 the Evidence obligations apply to
  mandatory rows, and the 13 Vector cells that held other references are normalised, the
  two non-mandatory ones to a documentary section; R3/R4 every header negative has a
  single defect, shown by a decoder that tolerates only that defect, and INV-177 is
  signed coherently so that only the schema rejects it; R5 the runner sentence and the
  definition of `external` say what is executed and what requires an implementation.
  Obsolete RTM rows found during the review are retired or rewritten when the current
  text demonstrates the obsolescence and no new protocol rule is chosen (owner's bounded
  authorisation).

---

## DR-1 — Authority to require oversight (Q1 → option b)

**Findings:** F-1 (partly), A-11, A-12, A-13; touches A-14, A-57.

**Problem.** Three sources claim authority to trigger `pending_approval`
— the ActionDescriptor, the gateway's CapabilityPolicy, and the Assets
dynamic risk assessment — and Actions §3.7 forbids two of them. The
external agent cannot know the gateway's policy.

**Decision (P/R/A).** Layered authority with one defined resolution
procedure. Multiple legitimate sources; the executor computes effective
obligations from authenticated and authorized sources. A mandatory
requirement from one source cannot be cancelled by a `false` in another:
the descriptor ceases to be a veto over oversight.

**Design requirements.**
- Static policies are announced with identification and version; dynamic
  requirements are communicated before any effect of the action.
- The executor's signed response records the effective requirement and
  its origin, preserving the original envelope.
- Approval is bound to the action, parameters and conditions actually
  presented to the human; material changes require a new approval.
- No simple ordering among the four oversight modes: pre-execution
  approval and post-execution review can be cumulative. "Most restrictive
  wins" is insufficient when obligations differ in kind.

**Rejected.** Option c (envelope effective value as sole runtime
authority): the sender does not necessarily know the local policy or the
executor-computed risk. An envelope effective value may be a verifiable
declaration; it is not the only authority.

**Normative changes implied.** Actions §3.7 rescoped (descriptor `false`
alone does not require approval; it no longer prohibits other authorized
sources); Identity §7.3/§7.4/§7.7 and Assets §5.2 reference the resolution
component; an announcement mechanism for gateway policies (discovery
surface); Assets §5.2 denied/expired response form aligned with Actions
§3.4 (A-11).

**Dependencies.** DR-0.1; DR-2 for post-execution modes.

---

## DR-2 — Post-execution review modes (Q2 → option a)

**Findings:** A-4; C-09 test; State §7.1 `approval_expired` semantics.

**Problem.** `required_within_24h` has three incompatible definitions and
`required_post_execution` has no protocol mechanism.

**Decision (P/R/A).** A complete minimal post-execution review mechanism:
identification of the execution and of the reviewed result, an entitled
reviewer, a deadline, a signed decision, pending / completed / overdue
states, and a defined consequence of overdue.

**Design requirements.**
- `pending_approval` keeps meaning "execution is blocked". Post-execution
  review has distinct semantics: a later negative decision does not make
  an executed action "not executed"; it may start remediation or reversal
  where possible.
- `required_within_24h`: deadline derived from a normatively defined
  execution instant.
- `required_post_execution`: mandatory review with an explicit deadline set
  by the applicable policy; no obligation may remain pending indefinitely.
- These deadlines are ARSIA controls. Regulatory notification clocks (e.g.
  DORA major-incident reporting under Delegated Regulation (EU) 2025/301
  Art. 5) run independently and never wait for this review.

**Rejected.** Option b (audit-only) would withdraw the protocol's promise
of human review; option c (remove the modes) loses expressiveness the
profiles rely on.

**Normative changes implied.** New message/state surface in Actions;
audit record types and transitions in State §7; C-09 rewritten; A-4's
three definitions replaced by one.

**Dependencies.** DR-0.1; audit-record extension model (A-1/A-2/A-59) for
the new record types.

**Addendum — 2026-10-31 (owner decisions for the DR-1/DR-2 cycle).**
- **E1 — Review messages.** The post-execution review uses `event` messages with
  payload types `arsiaprotocol.oversight/review-pending`,
  `arsiaprotocol.oversight/review-decision` and `arsiaprotocol.oversight/review-overdue`;
  the intent enum is unchanged and `pending_approval` keeps meaning that execution is
  blocked. The contract requires signature, reviewer authority, correlation,
  identification of the execution and of the reviewed result, and duplicate and late
  handling. Being events exempts them from the high-risk set only. The review's state
  is separate from the execution's: a later decision updates the review, never the
  execution.
- **E2 — Deadlines.** `required_post_execution` has no protocol default: the executor
  resolves an explicit deadline from its announced `post_execution_review_period`
  before any effect, or rejects with `obligation_conflict`. `required_within_24h` keeps
  a fixed 24 h deadline that no source lengthens; when both modes apply both
  obligations are kept. `review_deadline` is distinct from `expires_at`.
- **E3 — Overdue.** Record plus escalation, no universal blocking: the overdue fact is
  recorded at the deadline independently of the escalation, whose result is appended
  separately; a late authorized decision is accepted with lateness preserved; an
  objection starts remediation. Escalation has a configured destination and the
  retry policy of Core §11.3; an attempt never counts as a review.
- **E4 — Gateway policy.** The CapabilityPolicy's oversight requirement travels in the
  token claim `arsia_oversight`, mandatory when it applies, with the policy's
  identification; re-issuance preserves requirement and origin for every remaining
  capability. The claim does not replace the announcement of static policies.
- **Executor choices accepted at review.** Reuse of `arsiaprotocol.oversight.approve`;
  `post_execution_review_period` in the ActionDescriptor; approval bound by
  `request_payload_hash`; executor provenance in `payload.obligation_resolution`
  (Core §4.4.8); A-78 and A-80 in scope.
- **Contract corrections at review (rev. 2).** Execution instant from the terminal
  result, including asynchronous success and failure, retrieved results not rejected
  for the age of their `ts`; overdue fact separate from the escalation result;
  CHECK-03 probe token with its own direction, audience and trust; signature required
  on executor errors carrying the resolution; authentication error codes kept for
  review decisions; declared versus default preserved in the configuration conflict;
  by-ID migration inventory with reproducible references; the CTV-02 and ITV-338
  retention exception.

---

## DR-3 — High-risk oversight enforcement (Q3 → option c)

**Findings:** F-1, A-32, A-23 (via DR-4); A-13 (via DR-1).

**Problem.** Envelope Rule 3 accepts `not_required` for high-risk; State
§6.2 requires pre-execution approval; the harness, ITV-579 and C-06(c)
diverge from Core's own precedence prose.

**Decision (P/R/A).** Both layers, backed by the same semantics: profile
resolution determines requirements; Rule 3 verifies that the resolved
result satisfies the applicable minimum; execution enforces it. For a
high-risk operation, `not_required` does not satisfy the oversight
requirement — including when it came from a profile default (the A-32
GDPR-STANDARD case).

**Design requirements.**
- Omitting `compliance`, choosing another profile, or declaring a lower
  classification cannot dispense an obligation established by trusted
  context. The framing distinguishes the system, the operation and the
  applicable obligations; the sender's own classification is not trusted
  alone.
- A consistency guard verifies equivalence among resolution, validation
  and execution, including A-32: absence of profile and explicit
  GDPR-STANDARD MUST produce the same result when semantically equivalent.
- Per DR-0.2, the EU-AI-ACT-HIGH-RISK profile's pre-execution approval is
  stated as the profile's technical choice.

**Normative changes implied.** Core §4.3.8 Rule 3 rewritten against the
resolution component; Core §4.3.7 precedence aligned; State §6.2 references
the component; harness rule and ITV-579/C-06(c) aligned; guard rule added to
the consistency checker.

**Dependencies.** DR-0.1; DR-4 (otherwise A-23 becomes mass rejection).

---

## DR-4 — Profile composition for multi-regime agents (Q4 → option a)

**Findings:** A-23; interacts with A-7 (PURGE vs retention), Rule 4 floors,
residency rules.

**Problem.** "At least EU-AI-ACT-HIGH-RISK" has no ordering to rest on;
one profile per message makes a high-risk MiFID II agent impossible.

**Decision (P/R/A).** Compare obligations, not profile names. One declared
profile plus additional applicable requirements per axis, each with
traceable origin. An operation can declare MIFID-II and also satisfy the
pertinent high-risk controls without asserting that any profile is "above"
another.

**Design requirements.** Composition is deterministic and published:
- retention floors compared against their correct anchors;
- residency restrictions satisfied simultaneously;
- oversight obligations accumulated when distinct;
- incompatibilities rejected explicitly.
"Greatest value wins" is not a general rule: retention has limits and
purposes, residency intersections can be empty, oversight may require
different steps.

**Rejected.** Option b (multiple profiles on the wire) would still need
this composition; option c (composite catalog profiles) multiplies
combinations.

**Normative changes implied.** Identity §4.2 and CHECK-05 rewritten; the
resolution component gains the per-axis composition rules; State §6 profile
definitions expose their axes.

**Dependencies.** DR-0.1.

**Addendum — 2026-10-31 (owner decisions for the DR-3/DR-4 cycle).**
- **D1 — Scope.** DR-3 and DR-4 form a bounded stage of the single resolution
  component (DR-0.1, Core §4.3.10). The component's contract is complete — sources,
  per-axis requirements, provenance, accumulation, conflicts — and integrates the
  message-side sources (declared values, profile, authenticated IdentityRecord,
  carried through onboarding to the router). DR-1 integrates the executor sources
  into the same component. The cycle demonstrates resolution and validation, not
  equivalence with execution: Actions §3.7 is unchanged, so F-1 stays partial.
- **D2 — High-risk oversight minimum.** `not_required`, absent and null never
  satisfy it; sufficiency is evaluated on the composed oversight set, where a valid
  mode filled from a default counts. A post-execution mode suffices only when no
  applicable source requires prior approval; distinct requirements accumulate. It is
  a protocol rule, not a reading of Article 14. Accepting a post-execution mode is
  not evidence that post-execution review works (DR-2).
- **D3 — Downgrade.** A lower classification declared by the sender does not, by
  itself, reduce obligations established by trusted context. A reduction needs an
  authenticated, authorized source with scope and provenance; none is defined, so a
  declared downgrade dispenses nothing and is recorded separately.
- **D4 — Axes.** Oversight, audit, explainability, retention and residency, without
  resolving A-70 (grounding of the MIFID-II floor) or A-7 (PURGE × retention).
  Retention requirements on the same object are compared by `retained_until` from
  that object's anchor; residency restrictions are normalized to member sets before
  intersecting (absent ≠ empty); oversight is a set.
- **D5 — Profile oversight is a substitutable default.** Fill (message, profile
  default, no-profile default), then apply requirement sources. Defaults never
  accumulate as obligations; `retention_minimum` is the only profile requirement.
- **D6 — High-risk requirement set.** Oversight ≠ `not_required`,
  `audit_required: true`, `explainability_required: true`, for `request` messages
  only; it imports neither P6M nor prior approval. A protocol technical rule, not a
  compliance claim.
- **D7 — Provenance.** Inline in the audit record (State §7.1
  `obligation_resolution`) and in rejection details; in the signed executor response
  with DR-1. Rebuildable per axis; normative presence; chained content; one
  resolution feeds the retention fields; "resolved" ≠ "fulfilled".
- **D8 — Authenticated context.** Prepared in Phase 1 (Identity §7.2 Step 7),
  verified by CHECK-05, bound at Phase 5 to the decision and token, verified by the
  router, which resolves before forwarding. Usable until the first of token expiry,
  IdentityRecord `valid_until`, or authenticated invalidation; renewal re-binds a
  valid context. The binding is not evidence of the agent's future conduct.
- **D9 — Source identification.** A declarative rules artifact
  (`profiles/arsia-obligation-rules.json`) interpreted only by Core §4.3.10; sources
  identified by content digests (RFC 8785); identity evidence keeps the signed
  bytes' hash, signature and JWK, and the bytes are retained.
- **D10 — Rejections.** Every compliance rejection, for any intent, produces an
  `error` audit record with `rejection_cause: "compliance"`, whatever
  `audit_required` declares. The wire error code stays `invalid_request`; the
  specific diagnostics of Core §4.3.8 take precedence over the generic
  `obligation_conflict`.

**Addendum — 2026-11-03 (owner decisions for the retention-axis cycle, under D4).**
- **R1 — A-7: recorded override.** Not adjudicating the legal question does not, by
  itself, permit any PURGE. A PURGE that removes values still within retention is
  executed under the existing authorization together with an explicit determination of
  the operator, recorded and bound to the request (`retention_override`: `reason`,
  `determination_ref`); without it, it is rejected. The executor determines
  `within_retention` and the retention instants from stored state, never from the
  request, over every generation whose values the PURGE removes, with or without a live
  entry; `entry_retained_until` is the latest instant. The override does not shorten
  the retention of the `state_purge` record, and the A-79 idempotency rules stand. Its
  presence is not evidence that the determination is legally correct. State §5.3.2 no
  longer promises that pseudonymisation satisfies both duties (GDPR recital 26) or that
  the PURGE record satisfies the obligation to preserve the erased records.
- **R2 — A-70: `profile_floor`.** MiFIR Art. 25(1) (orders and transactions, five
  years), MiFID II Art. 16(7) (the communications it covers, five years, up to seven on
  request) and the ARSIA choice (the floor extended to every record of the profile,
  anchored by the protocol) are stated separately; `retention_reference` is
  `"MIFIR:25(1); MIFID-II:16(7)"`; Delegated Regulation (EU) 2017/565 Art. 72 is not a
  source of the period. The Art. 17(3)(b) argument resting on those provisions is
  limited to the records they cover, without denying that other records may be subject
  to another legal retention obligation.
- **R3 — Value.** `P1827D` is kept as a profile policy: under the Core calendar
  arithmetic it is never shorter than `P5Y` from the same anchor and exceeds it by zero
  to two days (34,310 / 108,499 / 3,288 of the 146,097 anchors of a 400-year cycle). It
  is neither an exact conversion of "five years" nor a statement of legal sufficiency.
  The catalog change alters the `profile-floor` digest; the vectors carrying it are
  migrated.
- **R4 — Adjacent.** Core §2's "all communications … algorithmic communications"
  sentence is corrected as an A-70 echo. The DORA rationale is registered (A-96)
  without changing the floor; the absence of its sources from the local folder neither
  confirms nor refutes it.

**Addendum — 2026-11-05 (owner decisions for the DORA floor cycle, under D4).**
- **D1 — `conservative_policy`.** The DORA floor is classified like
  EU-AI-ACT-LIMITED-RISK: the period is an ARSIA choice, not the transcription of a
  legal period. `retention_reference: "DORA:6(5)"` stays as a contextual reference to
  the review of the ICT risk management framework, stating that the article does not
  set the period: it provides for a review at least once a year, periodically for
  microenterprises, and after incidents and other events, and it does not require
  keeping five cycles. Wording: "Art. 6(5) does not establish a retention period for the
  records covered by the profile. P1827D is a technical policy defined by ARSIA" — not
  "DORA prescribes no retention period", which is broader than shown. The claim of a
  common financial-sector floor (CRD IV, Solvency II, IORP II) is withdrawn without
  replacing it by another general negative about those acts.
- **D2 — `P1827D` kept.** The comparison with `P5Y` (R18 (a)) supports the zero-to-two
  day arithmetic margin, not that five years are necessary or appropriate. "Five annual
  cycles" may appear as an ARSIA motivation, neither as an obligation nor as a
  guarantee of review coverage. Commission Delegated Regulation (EU) 2024/1774
  Arts. 12(2) and 22(d) accompany the rationale: a longer retention is not by itself
  more appropriate in law.

---

## DR-5 — Audit hash chain (A-8 → option a)

**Findings:** A-8, A-60; interacts with A-1, A-2, A-59.

**Problem.** The chain covers only the previous `record_id` and
`payload_hash`; approver identity, oversight status and retention fields
can be altered without changing it, while the prose claims detection of
any modification.

**Decision (P/R/A).** The chain commits to the full previous record, the
previous hash and the chain context, using the canonicalization already
adopted (RFC 8785). Exclude only the record's own computed hash and any
derived field whose exclusion is explicitly specified; include accepted
extensions. Chain identifier, sequence and format version are protected.
Corrections are always new records, never rewrites.

**Design requirements.**
- The previous hash participates in the computation (transitive chain);
  hashing records in isolation is not a chain.
- Mandatory at the conformance level that promises audit integrity.
- Declared limits: the chain does not prove truthfulness, completeness or
  absence of forks; independent anchoring remains necessary against
  rewrite by the owner.

**Normative changes implied.** State §7.2 construction and claim
rewritten; audit-record schema field descriptions; a chain
computation/verification check in the tooling, including a tamper case.

**Dependencies.** A-1, A-2 and the A-59 guard (extension model settled
before "accepted extensions" can be included); F-3 (Core §5.1
canonicalization text corrected) in the same or an earlier cycle.

**Addendum — 2026-09-28 (owner decisions for the DR-5 cycle).**
- **D1 — Conformance mandate.** The chain is REQUIRED at the Compliance and Full
  conformance levels and RECOMMENDED at Core. Core §12, State §7 and Identity
  CHECK-04 state the same.
- **D2 — A-79 detached.** The `(key, version)` collision across generations is
  resolved in its own cycle (State §2 semantics, explicit generation counter). This
  cycle does not touch State §2.
- **D3 — Registration.** Chain-related observations of the DR-5 investigation are
  fixed and registered as findings closed in the cycle. The `relay_latency_ms`
  formula and the "MiFID II Art. 72" citation are register-only.
- **D4 — Construction (deviation from the letter of the decision above).** Each
  chain value commits to its own complete record (RFC 8785; only its own chain value
  is excluded), to the previous chain value and to the chain context. The full
  previous record is committed transitively, through the previous chain value that
  commits to it. Justification: under the literal form (the value of record n
  commits to record n−1 in full), a tombstone carrying no content cannot let a
  verifier recompute the successor's value after a permanent deletion. The
  self-inclusive form keeps the transitive commitment and also covers the newest
  record.
- **D5 — Tombstones.** Permanent deletion (State §7.3) leaves a tombstone carrying
  only chain context, position, the deleted record's chain value and the previous
  value it held. Only an operator-controlled maintenance path, separate from
  application roles, writes it. It persists for as long as its chain exists, and it
  attests that a deletion occurred, not that it was legitimate.
- **D6 — Tombstone schema.** A separate schema file.
- **D7 — Wording.** Tombstone wording is technical ("carries no field of the deleted
  record"). The State §7.2 GDPR paragraph is unchanged.
- **D8 — Chains per log.** A log MAY hold several chains. State §7.4 retrieves a
  chain by its identifier, and omission of a whole chain is a declared limit.
- **D9 — Onboarding.** Identity CHECK-04 requires the chain fields and verifies each
  returned chain.
- **Verification scope (owner condition).** Positions 1 to h of the held head must
  be present exactly and consecutively. Later entries are reported, not rejected.

**Addendum — 2026-11-03 (owner decisions for the A-79 cycle, under D2).**
- **G1 — Generation numbering.** A new entry takes the generation after the highest
  ever assigned under its key. The implementation keeps that highest number while it
  holds any information of the key — the live entry, a logically deleted entry still
  stored, temporal versions, archive, PURGE metadata, audit records — so neither a
  PURGE nor a partial removal rewinds the sequence. Restart at 1 is possible only after
  every such information is removed; the uniqueness of (key, generation, version) is
  bounded by that, as a declared limit (State §2.1.14).
- **G2 — Preconditions.** `expected_generation` joins `expected_version`; both are
  checked against the live entry in one atomic check. Version alone does not detect a
  recreation; generation alone does not detect updates within a generation. A
  conditional SET on a key without a live entry gets `conflict` with
  `entry_live: false`, no `current_*` member, no entry created, and nothing that
  distinguishes a deleted key from a key never written. The ABA protection holds
  within G1.
- **G3 — A-88.** `created_at` is the creation time of the entry (generation) and is
  immutable for its lifetime; a recreation has its own. Retention anchor and
  calculation unchanged; recreation renews nothing of earlier generations. Triage
  stays INT; closed by the §2.1.5 clarification and the disposition.
- **G4 — Adjacent findings closed in the cycle.** A-93: the four dead StateEntry
  `$ref`s of the state-operations schema, the README `$id` convention, and a guard over
  every `$ref` (fragments and relative bases included). A-94: PURGE repetition —
  retransmission per Core §10.3, repeated PURGE without a later write idempotent, PURGE
  after a later write a new purge; `state_purge.generation` is the latest generation
  covered. A-7 (PURGE versus retention) is not touched.
- **G5 — A-95 (plan proposal, accepted at review).** The conflict-details schema
  follows the existing State §8.4 MUST (current and updated members required); the
  live and absent branches are selected by any concurrency member and by
  `entry_live`, and the absent branch admits only `entry_live` and the stated
  preconditions.

**Addendum — 2026-11-04 (owner decisions for the relay/DPoP cycle, under D3).**
- **P1 — A-89: conditional forwarding fields.** `forwarded_at` is the instant the
  broker initiated the forwarding attempt; `relay_latency_ms` is `forwarded_at` −
  `received_at`, exactly, in whole non-negative milliseconds, measured to the
  initiation of forwarding, not to the recipient's response. `attestation_id`,
  `forwarded_at` and `relay_latency_ms` are present together when forwarding was
  initiated and absent when the message was stopped before it: a `forwarded_at` that
  records a decision not to forward, or an `attestation_id` with no attestation, would
  be misleading evidence. `success` records delivery under the Routing criterion (an
  ARSIA envelope or HTTP 202 relayed), not the outcome of the operation; `failure` is
  any failure that is not a timeout, and `timeout` a deadline that prevented or ended
  the relay — both before or after forwarding was initiated. The schema checks the
  structure; the timestamps and their correspondence to what occurred are a runtime
  obligation. Auditing messages rejected before forwarding (Rules 1, 2 and 9) is a
  normative decision of this cycle: the previous Rule 7 covered relayed messages
  without unambiguously requiring a record of every rejection, and Rule 9 used SHOULD.
  The migration keeps the declared cause of every negative vector.
- **P2 — A-49: one normative list in Identity §3.3.** Core §6.3 item 4 becomes a
  normative reference. The list keeps the conditions of RFC 9449 §4.3 — the nonce
  check is conditional, check 12 holds both `ath` and the key binding of the token,
  `htu` is compared without query and fragment — and marks apart the restrictions of
  the ARSIA profile (EdDSA/Ed25519, `POST` inbox delivery, the Core §8.3 window,
  single-use `jti`), so that protocol choices are not presented as requirements of
  the RFC. No duplicate list and no guard for one.
- **P3 — Nonce per RFC 9449 §9; single-use `jti` as an ARSIA requirement.** A
  receiving agent MAY require a nonce and provides it with the HTTP 401
  `use_dpop_nonce` challenge; a nonce is valid only at its issuer, and a request
  lacking an acceptable nonce — the first one included, whichever check detects it —
  is answered with the challenge rather than a generic `unauthorized`. The `jti` is
  accepted once per target URI (query and fragment excluded), by one atomic operation
  shared across the instances of the endpoint, and kept for as long as the proof could
  still be accepted (`iat` + S, not a fixed period from first receipt). A
  retransmission presents a new proof and may keep the envelope and its idempotency
  key; a nonce does not replace the `jti` check. In brokered delivery the broker
  returns the recipient's challenge to the sender in a relay error that preserves the
  nonce and identifies its issuer (`dpop_nonce`, `dpop_nonce_htu`), never as a generic
  error, and never re-sends or produces a proof.
