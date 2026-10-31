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
