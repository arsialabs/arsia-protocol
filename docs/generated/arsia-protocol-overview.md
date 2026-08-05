<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Arsia Protocol

| | |
|---|---|
| **Product** | Arsia Protocol (normative specification and conformance artifacts) |
| **Repository** | `arsialabs/arsia-protocol` |
| **Commit** | `e557f83` (branch `draft-02`; working tree carries 78 uncommitted paths, see Discrepancies) |
| **Extraction date** | 2026-08-05 |

Generated from repository state. Do not edit by hand; regenerate instead.

---

## What it is

The Arsia Protocol is a wire-level agent messaging specification in which European Union regulatory
obligations are carried as first-class envelope fields rather than as out-of-band metadata. This
repository holds the normative specification and the machine-readable artifacts that make conformance
testable: six specification documents, thirty JSON Schemas plus a vector meta-schema, a corpus of 649
test vectors with real cryptographic signatures, a catalog of seven compliance profiles, six
requirements traceability matrices, and eight Python tools that verify the whole set stays mutually
consistent. Its consumers are implementers building agents that must demonstrate compliance with the
General Data Protection Regulation, the EU AI Act, MiFID II, the Digital Services Act, DORA, and the
Common Agricultural Policy regime. The repository deliberately contains no runnable protocol
implementation: [CLAUDE.md:7](../../CLAUDE.md) records that software development kits, reference
implementations, and demonstrations live in separate repositories such as `arsialabs/arsia-protocol-sdk`,
and [docs/getting-started.md](../getting-started.md) is a tutorial written against that separate software
development kit. Those are external references made by this repository, not components of it.

---

## What it does

### Defines the protocol normatively

Six specification documents totalling 17,591 lines (`wc -l spec/*.md`) and 437 numbered sections
(`python3 scripts/check_links.py`) in a "5+1" arrangement: [ARSIA-Core.md](../../spec/ARSIA-Core.md)
carries the envelope, signing, discovery, authorization, transport, routing, idempotency, error handling
and conformance levels, and five primitives spelling ARSIA carry the rest.

| Document | Lines | Numbered sections | Scope |
|---|---|---|---|
| [ARSIA-Core.md](../../spec/ARSIA-Core.md) | 4,171 | 110 | Envelope, security, authorization, discovery, transport, brokers, errors |
| [ARSIA-State.md](../../spec/ARSIA-State.md) | 3,669 | 95 | State entries and operations, retention, GDPR obligations, compliance profiles, audit trail |
| [ARSIA-Assets.md](../../spec/ARSIA-Assets.md) | 2,816 | 80 | Asset transfers, escrow, financial capability model, DORA incident reporting |
| [ARSIA-Actions.md](../../spec/ARSIA-Actions.md) | 2,532 | 32 | Capability model, action registry, human oversight signaling, execution semantics, explainability |
| [ARSIA-Routing.md](../../spec/ARSIA-Routing.md) | 2,403 | 59 | Routing model, transport bindings, delivery guarantees, residency, rate limiting, brokers |
| [ARSIA-Identity.md](../../spec/ARSIA-Identity.md) | 2,000 | 61 | Agent identity, key management, certificate trust levels, external agent onboarding |

Normative language follows RFC 2119 keywords. The requirements traceability matrices in
[docs/rtm/](../rtm/) trace 1,903 requirement rows, of which 911 are MUST and 198 are MUST NOT
(`python3 scripts/rtm_counts.py`), to a schema and a test vector where one exists. 752 of those rows have
neither a schema nor a vector binding, which the matrices record explicitly rather than omit.

### Makes conformance machine-checkable

Thirty JSON Schemas (Draft 2020-12) in [schemas/](../../schemas/), plus
`arsia-test-vectors.meta.json` as the meta-schema for the corpus file itself. Every schema `$id` sits
under `https://arsiaprotocol.org/schemas/v2.0/`, and
[schemas/README.md](../../schemas/README.md) maps each schema to the specification section it validates.
`arsia-common.schema.json` holds the shared definitions.

The corpus in [test-vectors/arsia-test-vectors.json](../../test-vectors/arsia-test-vectors.json) holds
649 vectors in three discriminated formats, resolved by `classify_vector()` at
[validate_vectors.py:128-141](../../scripts/validate_vectors.py):

| Format | Shape | Count |
|---|---|---|
| `message-only` | `message` plus boolean `valid`; validated against `arsia-message.schema.json` | 295 |
| `schema-ref` | `schema_ref` plus `data` plus `expected` | 350 |
| `hybrid` | `schema_ref` plus `message` plus `expected` | 4 |

418 vectors are expected valid, 137 expected invalid, and 94 carry `skip_schema: true` because they
encode runtime constraints that JSON Schema cannot express. Each of those 94 is classified individually
in [docs/draft-02-skip-classification.md](../draft-02-skip-classification.md). Vector identifiers are
prefixed by origin: ITV 579, INV 42, CTV 10, STV 7, ATV 6, ACTV 3, RTV 2.

### Verifies real cryptography, not placeholders

83 vectors carry a `crypto` object with the private key, public key, canonical signing bytes, and the
base64url signature. Running `python3 scripts/validate_vectors.py --check-crypto` reports
`Crypto: 83 vectors checked, 83 passed, 0 failed`. The breakdown by algorithm is 76 EdDSA, 2 ES256,
2 RS256, and 3 vectors with no declared algorithm (negative cases). Verification runs through the
`cryptography` hazmat primitives at
[validate_vectors.py:163-188](../../scripts/validate_vectors.py), over the RFC 8785 canonical form of
the envelope with only `security.sig` removed. Three independent checks run per vector: the canonical
bytes are recomputed and compared, the signature is verified against the public key, and the `sig` value
in the envelope is compared to the one recorded in the `crypto` block. The nine keypairs in
[test-vectors/keypairs.json](../../test-vectors/keypairs.json) are committed intentionally as test
material.

### Carries seven compliance profiles as data

[profiles/arsia-compliance-profiles.json](../../profiles/arsia-compliance-profiles.json) (version
`2.0.0`) is the normative catalog, defined in prose at ARSIA-State §6 and referenced from Core §4.3.6.1.
Values below are read from the catalog file, not from prose.

| Profile | Retention minimum | Basis | Human oversight | Audit | Explainability | Residency | Clock skew (s) |
|---|---|---|---|---|---|---|---|
| `GDPR-STANDARD` | none | `technical_default` | `not_required` | false | false | none | default |
| `EU-AI-ACT-LIMITED-RISK` | `P90D` | `conservative_policy` | `not_required` | true | true | none | default |
| `EU-AI-ACT-HIGH-RISK` | `P6M` | `regulatory` | `required_before_execution` | true | true | none | 120 |
| `MIFID-II` | `P1827D` | `regulatory` | `required_before_execution` | true | true | `EU` | 60 |
| `PAC-AGRICULTURE` | `P1096D` | `regulatory` | `required_post_execution` | true | true | `EU` | default |
| `DSA-VLOP` | `P731D` | `profile_floor` | `required_within_24h` | true | true | none | default |
| `DORA` | `P1827D` | `profile_floor` | `required_within_24h` | true | false | `EU` | 60 |

Profile resolution is a precedence chain (Core §4.3.7): a per-message value wins over a profile default,
which wins over the `GDPR-STANDARD` defaults, and a message with no `compliance` field carries no
obligation at all. Eight validation rules (Core §4.3.8, lines 1242 to 1342) then apply, covering profile
name validity, PII requiring a legal basis, high-risk requiring oversight, the profile retention floor,
residency forcing brokered routing, the prohibition on classification escalation, PII requiring an audit
trail, and sensitive data requiring an Article 9(2) legal basis.

### Classifies DORA ICT incidents

ARSIA-Assets §6.2 defines which transfer failures become reportable ICT incidents under DORA: the
infrastructure causes (`provider_unavailable`, `network_failure`, `database_failure`, `broker_failure`,
`tls_failure`, `unknown`) raise a candidate event, while business-logic failures (insufficient funds,
invalid account, compliance rejection, limit exceeded, duplicate, validation failure, authorization
failure) do not. This is a classification rule applied by one party rather than an exchange between
parties, so it appears here rather than among the sequence diagrams below.

### Enforces its own internal consistency

Eight Python tools in [scripts/](../../scripts/) (2,689 lines). Six are read-only verifiers; two are
generators. Observed output from running each verifier at extraction time:

| Tool | Lines | What it proves | Observed result |
|---|---|---|---|
| `validate_vectors.py` | 530 | Every vector validates against its schema, error paths match, signatures verify | `TOTAL 418 valid / 137 invalid / 649 pass / 0 fail`; `Error-path mismatches: 0`; `Crypto: 83/83 passed` |
| `check_consistency.py` | 342 | 90 repository invariants: schema meta-validity, `$id` scheme, strict `$ref` resolution, profile catalog validity, constant anti-regression, prose to schema enum parity, requirements matrix drift | `ALL CHECKS PASSED` (90 checks) |
| `runtime_harness.py` | 366 | R1 to R13, the deterministic algorithms JSON Schema cannot express | `ALL RUNTIME RULES PASSED` (73 assertions) |
| `extract_examples.py` | 100 | Every fenced JSON block in the specifications parses; envelope-shaped ones validate | `blocks=76 full=71 fragments=5 envelope-validated=9 failures=0` |
| `check_links.py` | 122 | Every section cross-reference resolves, in specifications and in schema descriptions | `explicit=501 bare=809 external=19; artifact refs: 391; dangling=0` |
| `rtm_counts.py` | 54 | Reproducible requirement counts from the traceability matrices | `TOTAL rows: 1903`; `MUST + MUST_NOT total: 1109` |

The two generators are `regen_v2.py` (234 lines, re-signs the corpus under the Draft-02 signing profile)
and `gen_state_vec2.py` (941 lines, generates 63 ARSIA-State vectors). Neither runs in continuous
integration.

The runtime rules verified by `runtime_harness.py`:

| Rule | Subject |
|---|---|
| R1 | Calendar duration arithmetic with end-of-month clamping |
| R2 | Retention floor comparison against the profile minimum |
| R3 | Capability matching, including the reserved-namespace rule |
| R4 | Reserved capability registry membership |
| R5 | Fixed ISO 4217 amount scale per currency |
| R6 | Idempotency precedence between signed envelope and header |
| R7 | Correlation and root chain verification |
| R8 | I-JSON number range limits |
| R9 | Content field mutual exclusivity |
| R10 | Effective human oversight resolution |
| R11 | Authorization server issuer trust |
| R12 | Session-scope audit precedence |
| R13 | Key revocation under cache ceiling |

---

## Architecture

This repository is a specification plus its verification tooling. It has no runtime: it listens on no
port, opens no network connection, and stores nothing. Its only input and output boundary is the local
filesystem, read by the Python tools and written only by the two generators. The HTTP endpoints named
throughout this document (`/.well-known/arsia`, `/v1/arsia/inbox`, and the rest) are obligations the
specification places on implementers; they are not surfaces this repository exposes.

### Top-level structure

| Path | Contents | License |
|---|---|---|
| [spec/](../../spec/) | Six normative specification documents | CC-BY-SA-4.0 |
| [schemas/](../../schemas/) | 30 JSON Schemas, 1 vector meta-schema, README mapping table | Apache-2.0 |
| [test-vectors/](../../test-vectors/) | 649-vector corpus, 9 test keypairs, README | Apache-2.0 |
| [profiles/](../../profiles/) | The seven-profile compliance catalog | Apache-2.0 |
| [docs/rtm/](../rtm/) | Six requirements traceability matrices | CC-BY-SA-4.0 |
| [docs/](../) | Frequently asked questions, getting started, audit and Draft-02 process records | CC-BY-SA-4.0 |
| [scripts/](../../scripts/) | Eight Python tools and `requirements.txt` | BUSL-1.1 |
| [.github/workflows/](../../.github/workflows/) | One continuous integration workflow | BUSL-1.1 |
| [licenses/](../../licenses/) | The three license texts and a licensing FAQ | Mixed |
| [results/](../../results/) | Committed conformance report output | CC-BY-SA-4.0 |

Licensing is path-dependent and enforced by convention rather than by tooling: specification and
documentation paths carry CC-BY-SA-4.0, machine-readable artifacts carry Apache-2.0, and code carries
BUSL-1.1.

### Artifact consistency web

Every edge below is a constraint that some tool enforces. A normative change at one node almost always
requires a change at the others.

```
                        +---------------------------+
                        |          spec/            |
                        |  6 normative documents    |
                        |  437 numbered sections    |
                        +-------------+-------------+
                              |       |       |
      check_links.py          |       |       |          extract_examples.py
      (cross-refs resolve)    |       |       |          (fenced JSON parses,
                              |       |       |           envelopes validate)
              +---------------+       |       +---------------+
              |                       |                       |
              v                       v                       v
     +-----------------+    +------------------+    +------------------+
     |    schemas/     |    |    profiles/     |    |    docs/rtm/     |
     |  30 schemas +   |    |   7 compliance   |    |  6 matrices,     |
     |  1 meta-schema  |    |    profiles      |    |  1903 rows       |
     +--------+--------+    +---------+--------+    +---------+--------+
              |                       |                       |
              |    check_consistency.py enforces all three:   |
              |    meta-validity, $id scheme, strict $ref,    |
              |    catalog validity, prose/schema enum        |
              |    parity, constant anti-regression,          |
              |    cross-document requirement drift           |
              |                       |                       |
              +-----------+-----------+-----------------------+
                          |
                          v
              +-------------------------+
              |     test-vectors/       |
              |  649 vectors, 83 with   |<----- keypairs.json (9 keypairs)
              |  real signatures        |
              +-----------+-------------+
                          |
                          |  validate_vectors.py (schema, error path, crypto)
                          |  runtime_harness.py  (R1-R13 over skip_schema vectors)
                          v
                    pass / fail
```

### Validation pipeline

The single workflow [.github/workflows/validate-vectors.yml](../../.github/workflows/validate-vectors.yml)
runs one job, `validate-vectors`, on push and pull request to `main`.

```
   push / pull_request to main
              |
              v
   +----------------------+
   |  actions/checkout@v4 |
   +----------+-----------+
              |
              v
   +--------------------------+
   | actions/setup-python@v5  |
   |     Python 3.12          |
   +----------+---------------+
              |
              v
   +----------------------------------+
   | pip install -r                   |     declares: jsonschema, referencing,
   |   scripts/requirements.txt       |     rfc8785, cryptography
   +----------+-----------------------+
              |
              v
   +-------------------------------------------------+
   |  1. validate_vectors.py --check-meta             |--> corpus + meta-schema
   |  2. validate_vectors.py --check-errors           |--> corpus + expected_error
   |  3. validate_vectors.py --check-crypto           |--> corpus + keypairs
   |  4. check_consistency.py                         |--> schemas, profiles, rtm
   |  5. runtime_harness.py                           |--> skip_schema vectors
   |  6. extract_examples.py                          |--> spec/*.md JSON blocks
   |  7. check_links.py                               |--> spec + schema refs
   +----------+--------------------------------------+
              |
              v
   +-------------------------------------+
   | validate_vectors.py --format junit  |  (if: always())
   |        > vector-results.xml         |
   +----------+--------------------------+
              |
              v
   +-------------------------------------+
   | actions/upload-artifact@v4          |  (if: always())
   |   name: vector-validation-results   |
   +-------------------------------------+
```

Steps 1, 2, 3 and the JUnit step each re-validate the full corpus, so a run performs four complete
passes.

### Dependencies

Runtime dependencies: none, because there is no runtime. Tooling dependencies, by observation of the
import statements rather than the declaration file:

| Package | Used by | Declared in `requirements.txt` |
|---|---|---|
| `jsonschema` | `validate_vectors.py`, `check_consistency.py` | Yes |
| `referencing` | `validate_vectors.py` registry construction | Yes |
| `cryptography` | `validate_vectors.py --check-crypto`, `regen_v2.py` | Yes |
| `rfc8785` | canonicalization in `validate_vectors.py`, `regen_v2.py` | Yes |

There is no package manifest of any kind in the repository: no `package.json`, `pyproject.toml`,
`setup.py`, `go.mod`, `Cargo.toml`, or `Makefile`. There is no linter, formatter, or type-checker
configuration, and no installed git hooks.

### Configuration surface

Only `validate_vectors.py` takes arguments:

| Flag | Effect |
|---|---|
| `--format {tap,summary,junit}` | Output format, default `tap` |
| `--filter GLOB` | Select vectors by identifier glob |
| `--schema SUBSTR` | Select vectors by schema name substring |
| `--vectors PATH` | Override the corpus path |
| `--check-meta` | Validate the corpus against its meta-schema first |
| `--check-errors` | Confirm invalid vectors fail for the declared reason |
| `--check-crypto` | Verify canonical bytes, signatures, and `sig` field consistency |

`check_consistency.py`, `runtime_harness.py`, `extract_examples.py`, `check_links.py` and
`rtm_counts.py` take no arguments. `regen_v2.py` accepts `--apply` to write the re-signed corpus back to
disk; without it the run is a dry run. `gen_state_vec2.py` accepts nothing and executes at import time.

---

## Sequence diagrams

For a specification repository, a flow counts as implemented when it is normatively specified with a
section reference **and** covered by at least one schema, test vector, or runtime harness rule. All
eleven flows below meet that test; the coverage is named with each diagram. DORA incident classification
is described under What it does rather than diagrammed, because it is a single-party classification rule
rather than a multi-party exchange.

### 1. Message signing and verification

The foundational flow, entered at the signing procedure in ARSIA-Core §5.1 and the verification pipeline
in §5.2. Covered by `arsia-message.schema.json`, the 83 crypto vectors, and runtime rule R9.

```
Sender                        Sender JWKS                    Receiver
  |                                |                             |
  |  deep-clone envelope           |                             |
  |  set security.alg, security.kid|                             |
  |  delete ONLY security.sig      |                             |
  |  canonicalize (RFC 8785)       |                             |
  |  sign canonical bytes (Ed25519)|                             |
  |  base64url, no padding         |                             |
  |  write security.sig            |                             |
  |                                |                             |
  |------------- POST /v1/arsia/inbox (signed envelope) -------->|
  |                                |                             |
  |                                |            1. size limit    |
  |                                |            2. parse JSON    |
  |                                |            3. I-JSON check  |
  |                                |            4. reject dup    |
  |                                |               member names  |
  |                                |            5. minimal shape |
  |                                |            6. select v      |
  |                                |               signing profile
  |                                |            7. rebuild input |
  |                                |                             |
  |                                |<--- 8. GET jwks.json -------|
  |                                |---- JWK Set --------------->|
  |                                |                             |
  |                                |            9. alg coherence |
  |                                |           10. verify sig    |
  |                                |           11. full schema   |
  |                                |           12. token,        |
  |                                |               capability,   |
  |                                |               compliance    |
  |                                |           13. payload       |
  |                                |                             |
  |<------------ 200 response envelope, or error ----------------|
```

A Draft-01 signature never verifies under this procedure, and Core §5.1 forbids falling back to the
Draft-01 signing input on failure.

### 2. Agent discovery and first contact

How a sender reaches an agent it has not contacted before, entered at agent identifier resolution in
ARSIA-Core §6.6 and continued through §7.1 to §7.4. Covered by `arsia-discovery-response.schema.json` and
`arsia-jwk-entry.schema.json`.

```
Sender          Agent Directory      Recipient well-known      Recipient inbox
  |                    |                      |                       |
  |-- resolve agent-id>|                      |                       |
  |<-- https origin ---|                      |                       |
  |                    |                      |                       |
  |------ GET /.well-known/arsia ------------>|                       |
  |<----- AgentMetadata ----------------------|                       |
  |                    |                      |                       |
  |  verify returned agent_id equals          |                       |
  |  the resolved entry, else reject          |                       |
  |  with unauthorized                        |                       |
  |                    |                      |                       |
  |------ GET /.well-known/arsia/capabilities>|   (optional)          |
  |<----- capability descriptors -------------|                       |
  |                    |                      |                       |
  |------ GET /.well-known/arsia/jwks.json -->|                       |
  |<----- JWK Set (cache, max 3600 s) --------|                       |
  |                    |                      |                       |
  |  negotiate version: server_min <= v       |                       |
  |  and min_v <= server_max, else            |                       |
  |  not_implemented + supported_versions     |                       |
  |                    |                      |                       |
  |------------- POST signed request ------------------------------>  |
  |<------------ 200 response, or 202 + Location + Retry-After -----  |
```

Agent identifier resolution is explicit and provisioned out of band. The specification does not permit
deriving a host from an agent identifier heuristically, and an unreachable or inconsistent resolution
entry fails closed.

### 3. Capability discovery and action invocation

The primary operational path for an action that needs no human oversight, entered at the action
discovery endpoint in ARSIA-Actions §2.3 and the lifecycle in §4.1. Covered by
`arsia-action-descriptor.schema.json`, `arsia-action-discovery-response.schema.json`, and runtime rules
R3 and R4.

```
Requester      Actions endpoint   Authorization Server    Executor
   |                  |                     |                 |
   |-- GET /.well-known/arsia/actions ----->|                 |
   |   (filters: category, risk_level_min,  |                 |
   |    human_oversight_required, limit)    |                 |
   |<- {actions[], total, limit, offset} ---|                 |
   |                  |                     |                 |
   |------ POST token request (client_credentials) ---------->|
   |<----- access token, scope covers capabilities -----------|
   |                  |                     |                 |
   |--------- signed request, payload.type = action --------->|
   |                  |                     |                 |
   |                  |                     |     REQUESTED   |
   |                  |                     |  validate envelope
   |                  |                     |  verify authorization
   |                  |                     |  read descriptor
   |                  |                     |                 |
   |                  |                     |  human_oversight_required
   |                  |                     |    false -> EXECUTING
   |                  |                     |    true  -> see flow 4
   |                  |                     |                 |
   |                  |                     |     EXECUTING   |
   |                  |                     |  (timeout at    |
   |                  |                     |   max_execution_ms,
   |                  |                     |   default 30000)|
   |                  |                     |                 |
   |<-------- response, payload.result, correlation_id -------|
   |          plus payload.explanation when required          |
```

Terminal states are COMPLETED, FAILED, and ROLLED_BACK. Capability matching uses the single normative
algorithm in ARSIA-Actions §1.2: exact match or one trailing `prefix.*` wildcard, and a wildcard never
satisfies a capability in the reserved `arsiaprotocol.` namespace.

### 4. Human oversight escalation

The EU AI Act Article 14 path, entered when the descriptor sets `human_oversight_required: true`, at
ARSIA-Actions §3.2. Covered by `arsia-message.schema.json` intent enumeration, the oversight vectors, and
runtime rules R7 and R10.

```
Requester            Executor              Approver           Audit trail
   |                     |                     |                   |
   |--- request -------->|                     |                   |
   |                     |                     |                   |
   |                     |  MUST NOT execute.  |                   |
   |                     |  No side effects.   |                   |
   |                     |------ record 1: request ---------------->|
   |                     |                     |                   |
   |<-- pending_approval-|                     |                   |
   |    intent=pending_approval                |                   |
   |    correlation_id = request.id            |                   |
   |    root_request_id = request.id           |                   |
   |    expires_at = approval_deadline         |                   |
   |    payload.type =                         |                   |
   |      arsiaprotocol.oversight/pending      |                   |
   |                     |                     |                   |
   |                     |--- pending_approval to oversight ------>|
   |                     |    endpoints (SHOULD)                   |
   |                     |------ record 2: pending_approval ------>|
   |                     |                     |                   |
   |                     |<-- approval_decision|                   |
   |                     |    decision = approved | denied         |
   |                     |    correlation_id = pending_approval.id |
   |                     |    root_request_id = request.id         |
   |                     |------ record 3: approval_decision ----->|
   |                     |                     |                   |
   |                     |  1. approver token carries              |
   |                     |     arsiaprotocol.oversight.approve,    |
   |                     |     else forbidden                      |
   |                     |  2. now < approval_deadline (+/- 300 s),|
   |                     |     else treat as expired               |
   |                     |  3. correlation and root chain match a  |
   |                     |     pending_approval this agent sent,   |
   |                     |     else invalid_request. A duplicate   |
   |                     |     or late decision does not change    |
   |                     |     the recorded outcome                |
   |                     |  4. execute with the ORIGINAL request   |
   |                     |     parameters plus any conditions      |
   |                     |                     |                   |
   |<-- response --------|                     |                   |
   |    sent to the ORIGINAL requester,        |                   |
   |    not to the approver                    |                   |
   |                     |------ record 4: execution outcome ----->|
```

The approval deadline must be in the future and must not exceed 24 hours. With `required_approvals` set
to N (ARSIA-Actions §3.6), one `pending_approval` goes to N distinct approvers, any single denial
terminates the flow immediately, and the audit trail holds `3 + N + 1` records.

### 5. Broker-mediated routing under data residency

Mandatory whenever `compliance.data_residency` is set, entered at ARSIA-Routing §1.2.2 and ARSIA-Core
§9.2. Covered by `arsia-broker-entry.schema.json`, `arsia-broker-discovery-request.schema.json`, and
`arsia-relay-attestation.schema.json`.

```
Sender      Broker Registry   Authorization Server    Broker      Recipient
  |               |                    |                 |             |
  | read compliance.data_residency     |                 |             |
  |               |                    |                 |             |
  |-- GET /.well-known/arsia/brokers?residency=EU ------>|             |
  |<- [BrokerEntry] ------------------------------------ |             |
  |               |                    |                 |             |
  | select broker declaring            |                 |             |
  | arsiaprotocol.broker.relay with a  |                 |             |
  | jurisdiction satisfying the zone   |                 |             |
  |               |                    |                 |             |
  |------ request T_use (aud = broker) --------->|       |             |
  |<----- T_use --------------------------------|       |             |
  |------ request T_e2e (aud = recipient) ------>|       |             |
  |<----- T_e2e (<= 300 s, SHOULD be DPoP-bound)|       |             |
  |               |                    |                 |             |
  | set authorization.token_hash =     |                 |             |
  |   sha-256 over T_e2e octets        |                 |             |
  | sign envelope end to end           |                 |             |
  |               |                    |                 |             |
  |--------- POST /v1/arsia/inbox ------------------->|                |
  |          Authorization: Bearer T_use             |                |
  |          ARSIA-Recipient-Token: T_e2e            |                |
  |                                                   |                |
  |                                     a. verify sender signature    |
  |                                     b. verify T_use               |
  |                                     c. sha-256(T_e2e) equals      |
  |                                        authorization.token_hash   |
  |                                     d. broker jurisdiction        |
  |                                        matches declared zone      |
  |                                                   |                |
  |                                     sign relay attestation over   |
  |                                     the exact envelope            |
  |                                                   |                |
  |                                                   |-- POST ------->|
  |                                                   |  Authorization:|
  |                                                   |    Bearer T_e2e|
  |                                                   |  ARSIA-Relay-  |
  |                                                   |    Attestation |
  |                                                   |  envelope is   |
  |                                                   |  byte-identical|
  |                                                   |                |
  |                                                   |<-- 200 --------|
  |<-------- response forwarded unmodified -----------|                |
```

The broker never signs the envelope, never modifies it, and never redeems `T_e2e` for any purpose other
than forwarding. Recipient token validation is identical to direct routing, so the two are
indistinguishable at the token layer. The broker logs a `broker_relay` audit record and must not log
payload contents. If no eligible broker exists for the zone, the sender must not send at all and returns
`service_unavailable` with `data_residency_violation: true` and an empty `available_zones`.

### 6. Asset transfer with escrow lifecycle

Entered at the transfer request in ARSIA-Assets §3.1, with the escrow state machine in §4.2. Covered by
`arsia-asset-transfer-request.schema.json`, `arsia-asset-transfer-receipt.schema.json`,
`arsia-escrow-conditions.schema.json`, and runtime rule R5.

```
from_agent      Escrow holder      Payment provider   release_agent    to_agent
    |                 |                    |                |             |
    |-- AssetTransferRequest ------------->|                |             |
    |   capability: assets.transfer.initiate                |             |
    |   expires_at and idempotency REQUIRED                 |             |
    |   escrow_conditions present          |                |             |
    |                 |                    |                |             |
    |                 |-- debit hold ----->|                |             |
    |                 |                    |                |             |
    |<- receipt, status = escrowed --------|                |             |
    |                 |                    |                |             |
    |                 |  state = ESCROWED  |                |             |
    |                 |--- audit: escrow created ---------->|             |
    |                 |                    |                |             |
    |                 |<---- release_trigger message -------|             |
    |                 |      signed by release_agent        |             |
    |                 |                    |                |             |
    |                 |  validate: from matches release_agent,            |
    |                 |  payload.type matches release_trigger,            |
    |                 |  signature valid, not already terminal,           |
    |                 |  now < timeout_at                   |             |
    |                 |                    |                |             |
    |                 |-- credit --------->|                |             |
    |                 |                    |------------------ funds ---->|
    |                 |                    |                |             |
    |<- NEW receipt, status = completed, settled_at set ----|             |
    |                 |  state = RELEASED  |                |             |
    |                 |--- audit: escrow released --------->|             |
```

The alternative transitions from ESCROWED, all deterministic given the conditions and the message
sequence:

```
                        +-----------+
                        |  ESCROWED |
                        +-----+-----+
                              |
        +---------------------+---------------------+
        |                     |                     |
  release_agent          timeout_at            either party
  sends trigger          reached               invokes arbitration
        |                     |                     |
        v                     v                     v
  +----------+          +----------+          +----------+
  | RELEASED |          | RETURNED |          | DISPUTED |
  +----------+          +----------+          +-----+----+
                        receipt status              |
                        = failed, plus        timeout clock
                        automatic internal    suspended; resolves
                        reversal              to RELEASED or RETURNED
```

The timeout check must execute within 60 seconds of `timeout_at`. A dispute requires an
`arbitration_agent` in the escrow conditions, and that agent must verify the disputing party is actually
a party to the escrow, rejecting others with `forbidden`. Arbitration itself is out of scope for the
protocol.

### 7. Explicit transfer reversal

Entered at ARSIA-Assets §3.3, distinct from the automatic internal reversal that follows an escrow
timeout. Covered by `arsia-asset-transfer-reversal.schema.json`.

```
Requester                Processor              Payment provider
    |                        |                          |
    |-- AssetTransferReversal>|                         |
    |   capability:           |                         |
    |     assets.transfer.reverse                       |
    |   args.original_payment_reference                 |
    |   args.reversal_reason                            |
    |   args.requested_by                               |
    |   args.reversal_amount                            |
    |   idempotency REQUIRED  |                         |
    |                        |                          |
    |                        | original transfer exists?|
    |                        | status = completed?      |
    |                        | inside reversal window?  |
    |                        |   any failure -> not_found
    |                        |                          |
    |                        |-- reverse debit -------->|
    |                        |<- provider confirmation -|
    |                        |                          |
    |<- receipt for the reversal                        |
    |                        |-- audit record --------->|
```

### 8. Two-party authorisation for high-risk financial operations

Entered at ARSIA-Assets §5.2. It composes the oversight flow of diagram 4 with the transfer flow of
diagram 6. Covered by `arsia-asset-transfer-request.schema.json` and the oversight vectors.

```
Initiator              Processor                    Approver
    |                      |                            |
    |-- AssetTransferRequest>|                          |
    |   assets.transfer.initiate                        |
    |                      |                            |
    |                      | Step 2: risk assessment    |
    |                      |  amount and asset type,    |
    |                      |  compliance profile,       |
    |                      |  descriptor risk_level,    |
    |                      |  operator policy           |
    |                      |  risk >= 7 -> oversight    |
    |                      |                            |
    |<- pending_approval --|                            |
    |   payload.type = arsiaprotocol.oversight/pending  |
    |   approver_capability =                           |
    |     arsiaprotocol.oversight.approve               |
    |   risk_level carried                              |
    |                      |                            |
    |                      |--- pending_approval ------>|
    |                      |                            |
    |                      |<-- approval_decision ------|
    |                      |    signed by a DISTINCT    |
    |                      |    approver                |
    |                      |                            |
    |                      | execute the transfer       |
    |                      |                            |
    |<- receipt to the ORIGINAL requester -             |
```

ARSIA-Assets §6.3 maps this onto PSD2 strong customer authentication in two options: the approver
identity authenticated by the authorization server combined with the Ed25519 signature, or a
hardware-bound token carrying a `cnf` claim combined with DPoP. The specification explicitly states that
the protocol alone does not satisfy strong customer authentication.

### 9. External agent onboarding, six phases

The admission protocol for an untrusted external agent, entered at ARSIA-Identity §7.2. Phases must not
be reordered or skipped, and a failure in Phases 1 through 4 jumps directly to a Phase 5 denial. Covered
by `arsia-identity-record.schema.json`, `arsia-onboarding-decision.schema.json`, and
`arsia-capability-policy.schema.json`.

```
External Agent                 Onboarding Gateway         Infrastructure Router
      |                               |                            |
      |   PHASE 1: Discovery and Identity Verification             |
      |<-- GET /.well-known/arsia ----|                            |
      |--- AgentMetadata ------------>|  fail -> discovery_failed  |
      |<-- GET /.well-known/arsia/identity                         |
      |--- IdentityRecord + X-ARSIA-Sig header ------------------->|
      |<-- GET /.well-known/arsia/jwks.json                        |
      |--- JWK Set, >= 1 Ed25519 key >|                            |
      |                               | verify X-ARSIA-Sig over    |
      |                               | SHA-256 of the raw body    |
      |                               | check kid prefix matches   |
      |                               |   agent_id                 |
      |                               | classification is NOT      |
      |                               |   unacceptable-risk        |
      |                               |                            |
      |   PHASE 2: Compliance Conformance Test (5 checks)          |
      |<-- CHECK-01 envelope validity |                            |
      |<-- CHECK-02 signature verification (v2 profile)            |
      |<-- CHECK-03 oversight: agent MUST answer with              |
      |             pending_approval, not a direct response        |
      |<-- CHECK-04 audit trail format, skip on HTTP 404           |
      |<-- CHECK-05 classification consistency, skip if not        |
      |             high-risk                                      |
      |--- results: pass | fail | skip >                           |
      |                               | any fail ->                |
      |                               |   conformance_failed       |
      |                               |                            |
      |   PHASE 3: Capability Scoping |                            |
      |                               | effective =                |
      |                               |  (declared AND allowed)    |
      |                               |  OR (declared AND          |
      |                               |      oversight_required)   |
      |                               | deny by default            |
      |                               | partition into             |
      |                               |  freely_allowed and        |
      |                               |  oversight_required        |
      |                               |                            |
      |   PHASE 4: Provenance Verification                         |
      |<-- GET /.well-known/arsia/audit                            |
      |--- earliest audit record ---->| informational only;        |
      |                               | MUST NOT auto-deny         |
      |                               |                            |
      |   PHASE 5: Onboarding Decision|                            |
      |<-- request, payload.type =    |                            |
      |    arsiaprotocol.onboarding/decision                       |
      |    carrying token and effective_capabilities               |
      |--- response (acknowledgement) >                            |
      |                               | audit record with          |
      |                               | event_type =               |
      |                               |   approval_decision        |
      |                               |                            |
      |   PHASE 6: Operational Phase  |                            |
      |------------- request with Bearer token ------------------->|
      |                               |<- POST /v1/arsia/verify-token
      |                               |-- valid | invalid --------->|
      |                               |                            |
      |                               |  capability subset check,  |
      |                               |  else forbidden            |
      |                               |  risk_level vs             |
      |                               |  policy max_risk_level,    |
      |                               |  else forbidden with       |
      |                               |  risk_level_exceeded       |
      |<------------ response, or forbidden ---------------------- |
```

External agents are untrusted by default. The gateway must not grant trust from out-of-band information
such as email confirmations or manual configuration, and every trust decision must be traceable in the
audit trail.

### 10. Retention, audit trail and compliance profile enforcement

The compliance evaluation every receiving agent performs, entered at the precedence chain in ARSIA-Core
§4.3.7 and the eight validation rules in §4.3.8. Covered by `arsia-compliance-field.schema.json`,
`arsia-compliance-profiles.schema.json`, `arsia-audit-record.schema.json`, and runtime rules R1, R2, R10
and R12.

```
Sender               Receiver              Profile catalog        Audit trail
  |                     |                        |                     |
  |-- signed message -->|                        |                     |
  |   compliance.profile|                        |                     |
  |   compliance.retention                       |                     |
  |   compliance.pii_involved                    |                     |
  |                     |                        |                     |
  |                     |-- resolve profile ---->|                     |
  |                     |<- defaults ------------|                     |
  |                     |                        |                     |
  |                     | precedence:            |                     |
  |                     |   per-message value    |                     |
  |                     |   > profile default    |                     |
  |                     |   > GDPR-STANDARD      |                     |
  |                     |   > no obligation      |                     |
  |                     |                        |                     |
  |                     | Rule 1 profile name valid                    |
  |                     | Rule 2 PII needs legal_basis                 |
  |                     | Rule 3 high-risk needs oversight             |
  |                     | Rule 4 retention >= profile floor,           |
  |                     |        resolved on a real anchor date;       |
  |                     |        below the floor is REJECTED,          |
  |                     |        never clamped                         |
  |                     | Rule 5 residency forces brokered routing     |
  |                     | Rule 6 classification MUST NOT escalate      |
  |                     | Rule 7 PII requires an audit trail           |
  |                     | Rule 8 sensitive data needs Art. 9(2) basis  |
  |                     |                        |                     |
  |<- invalid_request --|  on any rule failure   |                     |
  |                     |                        |                     |
  |                     | on success: operate on state                 |
  |                     |   GET, SET, DELETE, QUERY, SNAPSHOT,         |
  |                     |   PURGE, GRANT, REVOKE                       |
  |                     |                        |                     |
  |                     |----- ArsiaAuditRecord ------------------->   |
  |                     |      immutable, retained per the floor       |
  |                     |                        |                     |
  |                  queryable: GET /.well-known/arsia/audit           |
  |                  capability arsiaprotocol.audit.read               |
  |                  filters: from_agent, to_agent, after, before,     |
  |                  event_type, compliance_profile,                   |
  |                  human_oversight_status, payment_reference         |
```

Rule 4 rejects rather than clamps, because clamping would let the declared obligation and the applied
obligation diverge. Retention durations are ISO 8601 calendar expressions evaluated with end-of-month
clamping, which is what runtime rule R1 verifies.

### 11. GDPR Article 17 right to erasure

Entered at ARSIA-State §5.3, built on the PURGE operation of §3.2.2. Covered by
`arsia-state-operations.schema.json` and the PURGE vectors.

```
Data subject           Operator              State store         Audit trail
     |                     |                      |                   |
     |-- erasure request ->|                      |                   |
     |   (channel out of scope)                   |                   |
     |                     |                      |                   |
     |                     |-- QUERY by ---------->|                  |
     |                     |   pii_classification  |                  |
     |                     |   = personal          |                  |
     |                     |<- matching entries ---|                  |
     |                     |                      |                   |
     |                     | consult Art. 30 register                 |
     |                     |                      |                   |
     |                     | Art. 17(3) exception check:              |
     |                     |  (a) freedom of expression               |
     |                     |  (b) legal obligation                    |
     |                     |  (c) public health                       |
     |                     |  (d) archiving and research              |
     |                     |  (e) legal claims                        |
     |                     |                      |                   |
     |<- refusal with grounds (if an exception applies)               |
     |                     |                      |                   |
     |                     |-- PURGE per entry -->|                   |
     |                     |   physical deletion from ALL storage,    |
     |                     |   including the temporal store           |
     |                     |                      |-- purge event --->|
     |                     |                      |                   |
     |                     | backup propagation SHOULD complete       |
     |                     | within 30 days; timeline documented      |
     |                     |                      |                   |
     |<- confirmation, referencing PURGE audit events                 |
```

Where erasure conflicts with a regulatory retention floor such as the MiFID II five-year requirement,
the specification provides the mechanism but explicitly does not adjudicate the legal conflict; that
determination is the operator's.

---

## Current version

The repository carries several independent version identifiers. They are reported here with their
sources and are not reconciled, because two of them disagree.

| Layer | Value | Source |
|---|---|---|
| Latest git tag | `draft-01` | `git tag -l`, at commit `fbb30e7`, dated 2026-05-11 |
| Document draft | `Draft-02`, dated 2026-07-22 | [CHANGELOG.md:13](../../CHANGELOG.md), "Draft-02 supersedes Draft-01. Breaking release: wire version 2.0." |
| Wire version | `2.0` | `"const": "2.0"` at [schemas/arsia-message.schema.json:462](../../schemas/arsia-message.schema.json) |
| Schema namespace | `v2.0` | All 31 schema `$id` values under `https://arsiaprotocol.org/schemas/v2.0/` |
| Profile catalog | `2.0.0` | `version` in [profiles/arsia-compliance-profiles.json](../../profiles/arsia-compliance-profiles.json) |
| Test vector corpus | `1.0.0` | `version` in [test-vectors/arsia-test-vectors.json](../../test-vectors/arsia-test-vectors.json) |
| Specification headers | `Version: 2.0`, `Status: Draft`, `Draft-02 \| July 2026` | Lines 6, 7 and 12 of all six files in [spec/](../../spec/) |

[VERSIONING.md](../../VERSIONING.md) defines three deliberately independent layers: the document draft,
errata releases, and the wire version carried in the envelope `v` field. It states that Draft-02 will
publish as v2.0 Final after community feedback, and that the specifications keep `Status: Draft` until
then.

**Determination:** the current version is **Draft-02, wire version 2.0**. The changelog entry, the
schema constant, and the specification document headers agree. It is untagged: the only tag in the
repository is `draft-01`. The specification headers keep `Status: Draft`, which matches
[VERSIONING.md](../../VERSIONING.md): the status stays Draft until Draft-02 publishes as v2.0 Final.

---

## Development stage

**Pre-launch.**

Functional criteria are met, verified by running the tools at extraction time rather than by citing the
project's own reports:

- 649 of 649 test vectors pass, 0 fail, across 418 expected-valid and 137 expected-invalid cases.
- 0 error-path mismatches: every expected-invalid vector fails for the reason it declares.
- 83 of 83 cryptographic signatures verify, across EdDSA, ES256 and RS256.
- 90 repository consistency invariants pass.
- 73 runtime-rule assertions pass across R1 to R13.
- 76 fenced JSON blocks in the specifications parse; 9 envelope-shaped examples validate; 0 failures.
- 1,311 section cross-references and 391 artifact references resolve; 0 dangling.

Operational readiness is partially met. One continuous integration workflow exists with twelve steps and
uploads a JUnit artifact. Contributor, security, licensing, versioning, code of conduct and contributor
license agreement documents are all present at the repository root. A conformance report is committed at
[results/draft-02-conformance-report.md](../../results/draft-02-conformance-report.md).

It is not Released. The Draft-02 work is entirely uncommitted, the only tag is `draft-01`, and no
published artifact is traceable from this repository.

### Gaps to the next stage

1. **Draft-02 is uncommitted and untagged.** 78 paths are modified or untracked, including all six
   specifications, five of the eight scripts, and every Draft-02 process document.
2. **No code quality tooling.** No linter, formatter, or type checker is configured anywhere, and no git
   hooks are installed.
3. **Workflow hardening.** The workflow declares no `permissions:` block and no `concurrency:` group, and
   pins actions to floating major tags rather than commit SHAs.
4. **A non-idempotent generator with no guard.** `gen_state_vec2.py` executes at module scope with no
   `if __name__ == "__main__"` guard, no arguments, and no dry-run mode; lines 925 to 941 unconditionally
   read, extend by 63 vectors, and rewrite the corpus. Running it twice duplicates vectors ITV-215 through
   ITV-277.

---

## Discrepancies

Cases where documentation, CLAUDE.md, or process files disagree with the artifacts.

1. **Schema count is stated imprecisely.** [README.md:48](../../README.md) and line 110, and
   [CLAUDE.md:45](../../CLAUDE.md), say 31 JSON Schemas. There are 30 `*.schema.json` files plus
   `arsia-test-vectors.meta.json`, which is the meta-schema for the vector corpus rather than a protocol
   schema. Counting the meta-schema is defensible, but the phrasing conflates the two.

2. **The working tree diverges from HEAD.** Commit `e557f83` contains none of the Draft-02 work. The 78
   uncommitted paths include every specification, the profiles catalog, the vector corpus, five scripts
   (`check_consistency.py`, `check_links.py`, `extract_examples.py`, `regen_v2.py`, `rtm_counts.py`,
   `runtime_harness.py`), one schema (`arsia-relay-attestation.schema.json`), and CLAUDE.md itself. This
   document describes the working tree, per the extraction decision recorded in the header.

3. **Superseded figures that survive in process documents.** These are historical records rather than
   current claims, but they read as current out of context and should not be quoted:
   [docs/draft-02-findings-status.md:11](../draft-02-findings-status.md) states 1994 rows and 1153
   MUST/MUST NOT, corrected later to 1903; and
   [docs/draft-02-implementation-plan.md:19](../draft-02-implementation-plan.md) states a 613-vector
   baseline, since grown to 649.

### Corrections applied during extraction (2026-08-05)

The first extraction (2026-07-30) recorded eight further discrepancies. They were fixed in the working
tree on 2026-08-05 and verified by re-running the full battery (all checks pass):

- `scripts/requirements.txt` was missing `cryptography` and `rfc8785`; both added and verified by
  installing the file into a clean virtual environment and re-running `--check-crypto` (83 of 83 pass).
- The prose dependency lists in [CLAUDE.md:14](../../CLAUDE.md) and
  [scripts/README.md](../../scripts/README.md) omitted `referencing`; both now list all four packages and
  the README install line points at `requirements.txt`.
- All six specification headers declared `Version: 1.0` and `Draft-01 | March 2026` with canonical URLs
  under `/draft-01`; updated to `Version: 2.0`, `Draft-02 | July 2026`, `/draft-02`, together with the
  companion-specification citations in each References section and the fifteen "ARSIA Protocol v1.0"
  scope labels in body text. Compatibility notes that genuinely describe Draft-01 behaviour were left
  unchanged.
- Five documents stated 1108 MUST plus MUST NOT; the reproducible count is 1109 (`MUST: 911`,
  `MUST_NOT: 198`). The one-row delta is `ROUTE-§2.2.2-12` (WebSocket heartbeat), harmonized from SHOULD
  to MUST after the earlier snapshot; all count statements now read 1109, and
  [results/draft-02-conformance-report.md](../../results/draft-02-conformance-report.md) was regenerated
  against the current tree.
- ARSIA-Identity §7.1.3 said the `approval_decision` intent is used for the Phase 5 onboarding decision,
  contradicting §7.6; the bullet now matches §7.6 (intent `request`, payload type
  `arsiaprotocol.onboarding/decision`, audit `event_type` `"approval_decision"`). The matching stale
  wording in RTM row `IDENT-§7.6-01` was corrected as well.
- The `runtime_harness.py` docstring documented only R1 through R10; R11, R12 and R13 added.
- The parsed-but-unread `--check` flag was removed from `regen_v2.py`; the default run is a dry run and
  `--apply` remains the only write path.
- The `rtm_counts.py` shebang sat on line 3; moved to line 1.

No discrepancy was found between the schemas, the vector corpus, the profile catalog, and the
traceability matrices. Every automated consistency check in the repository passes.
