<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
# ARSIA Protocol — Test Vectors

1019 test vectors (512 schema-valid, 280 expected-invalid, 208 runtime-only, 19 raw parse vectors — validator classification) for
validating ARSIA Protocol implementations. Vectors with a `crypto` block use real Ed25519,
ES256 (ECDSA P-256), and RS256 (RSASSA-PKCS1-v1_5) signatures, and declare the expected
verification outcome (`crypto.expect_signature`). Signatures outside a crypto block verify with the
catalog key of their `kid` unless the vector declares a signature negative (see
[Signatures outside a crypto block](#signatures-outside-a-crypto-block)).

## Files

| File | Description |
|------|-------------|
| [arsia-test-vectors.json](arsia-test-vectors.json) | 1019 test vectors. Header: `version` `2.0.0` (the Draft-02 corpus, for wire 2.0; the Draft-01 corpora were 1.0.x) and `generated`, the instant this revision was prepared |
| [keypairs.json](keypairs.json) | 54 test keypairs: 49 Ed25519, 2 ES256 (P-256), 3 RSA (NOT secrets — committed intentionally). 17 Draft-02 entries; 35 imported unchanged from the Draft-01.1 catalog (`origin/main 17dcf33`), only those a Draft-02 vector uses (34 in the port, one in the main reconciliation); 2 generated. The `provenance` member lists the three sets with their digests. `agent:acme.legacy-system#rsa1024` is an RSA key of 1024 bits, deliberately below the 2048-bit minimum of Core §5.1, for the key-size negative ITV-425 only. Derivations are stated in the file |

## Vector Formats

Each vector matches exactly one of four discriminated formats defined by the
meta-schema (`schemas/arsia-test-vectors.meta.json`); the meta-schema excludes the
fields of every other format, both ways:

| Format | Count | Description |
|--------|-------|-------------|
| `message-only` | 343 | Full message validated against `arsia-message.schema.json`. Uses `message` + `valid` fields. |
| `schema-ref` | 590 | Data payload validated against a named schema. Uses `schema_ref` + `data` + `expected` fields. |
| `hybrid` | 4 | Full message validated against a named schema. Uses `schema_ref` + `message` + `expected` fields. |
| `raw` | 19 | Exact received bytes, checked only by the Core §5.2 pipeline steps 2–4. Uses `raw_hex` + `expected_parse` fields. |

**Raw parse vectors (Core §5.2 steps 2–4).** `raw_hex` holds the exact received bytes
(lowercase hex, an even number of digits); `expected_parse` is `accept` or `reject`,
and a rejection carries `expected_error: "invalid_request"`. A consumer decodes the
bytes as UTF-8 (step 2: UTF-8 and JSON, `NaN`/`Infinity` rejected), checks I-JSON
(step 3: no surrogate outside a valid pair and no noncharacter, in any member name or
string, literal or escaped, at any depth — [RFC 7493] §2.1) and then duplicate member
names at any depth after escape processing (step 4, [RFC 7493] §2.3), in that order.
Accepting a raw vector establishes only well-formed I-JSON text: it is not a valid,
authenticated or authorized message, and the steps add no limit on JSON numbers (an
integer beyond a library's default digit limit is still a number, CTV-16). This
is a test-corpus format, not an ARSIA envelope. The descriptions write escapes as they
are in the bytes (`\ud83d` is the six ASCII characters of the escape); `raw_hex` is
authoritative. The repository tools also load every artifact through these steps
(`strict_load` in `scripts/validate_vectors.py`): a duplicate member name in the corpus
itself stops the tools.

## ID Prefixes

| Prefix | Category | Count |
|--------|----------|-------|
| `ITV-` | Cross-spec (identity, state, routing, assets, actions, core) | 740 |
| `INV-` | Invalid (all specs) | 245 |
| `CTV-` | Core (envelope, intents, compliance, raw parsing) | 16 |
| `STV-` | State (operations, audit records) | 7 |
| `ATV-` | Assets (receipts, reversals, escrow) | 6 |
| `ACTV-` | Actions (explainability, rollback) | 3 |
| `RTV-` | Routing (broker relay) | 2 |

Next available ID: **ITV-741** / **INV-246** / **CTV-17**

## Runtime-Only Vectors

All signed vectors use the **Draft-02 (wire 2.0) signing profile**: the signing input
is the RFC 8785 canonical form of the envelope with `security` present and only the
`security.sig` property removed (Core §5.1). After editing a signed valid vector,
re-sign it with `scripts/regen_v2.py --ids <ID,…>` (dry run unless `--apply`); verify
with `--check-crypto`.

**Presented tokens (Core §4.3.9).** A vector whose envelope carries `authorization` and
whose `test_metadata.input` has no `presented_token` binds the UTF-8 string
`synthetic-token:<ID>` (its own vector ID): `authorization.token_hash` is
`"sha-256:"` + the SHA-256 of those octets. Harness R21 checks every such binding; it
shows that the binding holds, not that the vector's message is accepted (the vector may
be invalid for another reason). `token_binding` and `attestation` scenarios state the
presented token explicitly.

208 vectors have `skip_schema: true` with a corresponding `skip_reason`.
These test runtime constraints (e.g. signature verification, temporal
checks) that cannot be validated by JSON Schema alone. A skip exempts only the
runtime expectation: every runtime-only vector is still validated structurally
against its schema. Each one is classified individually, with its category and the
coverage this repository actually executes for it, in
[docs/draft-02-skip-classification.md](../docs/draft-02-skip-classification.md).

### Version handling (Core §4.1.1)

`scripts/validate_vectors.py` validates a message under the procedure its own `v`
selects:

- `"2.0"` (or an absent or malformed `v`) — the exact published schema (rule 1);
- a newer 2.x minor — the major-2 compatibility schema: derived from the 2.0 schema,
  it accepts any 2.x `v` and unknown top-level and payload fields, keeps every known
  field, conditional and format, and keeps the content fields mutually exclusive
  (rules 2-3, §4.4.7);
- another major — rejected with `not_implemented` (rule 6).

### Scenarios executed by the harness

A runtime vector may state, in `test_metadata`, a `scenario` with its `input` and
hand-written `expect`; `scripts/runtime_harness.py` runs it and compares: `resolution`
and `router` (R10), `execution` (R15), `timing` (R16) and `state` (R17). A `timing`
scenario gives the recipient's clock (`input.recipient_time`); R16 computes the
clock-skew tolerance (the profile's `clock_skew_seconds`, else 300 s), the `ts` offset
and expiry, and reports temporal causes apart from compliance causes. A `state`
scenario gives an operation sequence on one key (`input.ops`, with an optional
`retention` on a SET and `override` on a PURGE); R17 (ITV-677..681) and R18
(ITV-683..687) run it on a reference store and check that the vector's data is what the
store produces. A `token_binding` scenario (R21) gives the presented token
(`input.presented_token`); an `attestation` scenario (R22) gives the received envelope,
the presented token, the broker entry, a simulated JWKS, the recipient's clock and the
attestations already seen (`input.envelope`, `presented_token`, `broker_entry`, `jwks`,
`now`, `seen`), and expects `accept` or `unauthorized` with the Routing §7.4.1 step. A
vector whose `data` is the delivered envelope (schema `arsia-message.schema.json`) states the
`ARSIA-Relay-Attestation` header as received in `input.attestation_header` (`null` = absent);
an attestation vector without it is delivered with the base64url (no padding) encoding of its
compact `data`. Such scenarios also expect `service_unavailable` at step 1 (header absent,
with its `details`) or `not_required` (no `data_residency`); a header negative names in
`input.permissive` the decoder that tolerates its single defect (R22 (f)). In
an `execution` scenario with approvals (R15), each approval step may override the
approver's signed access token (`issuer`, `scope`, `sub`, `aud`, `token_lifetime`,
`token_tamper`, `token_drop`) or the decision (`capabilities`, `approver_id`,
`correlation_id`, `root_request_id`, `tamper`, `alg`), pre-fill the executing agent's JWKS cache
(`input.jwks_cache`), remove a key before verification (`remove_keys`), verify later
than receipt (`verify_at`, also on a review decision event) or stay queued until the
deadline timer (`queued`); the
result lists the rejected decisions (`rejections`) and the verification evidence of the
records (`evidence`: `verified_kid`, `jwks_fetched_at`). A `revocation` scenario (R13)
gives the senders' published keys (`input.publishers`) and timed steps — `fetch`,
`remove`, `publish`, `receive`, `verify` (a kid), `verify_message` (the vector's own
signed message) and `event` (the vector's message as a key-revocation event, Identity
§2.5) — and expects each step's result, including `invalidated` for an event. Two
scenarios of R23 sit on schema-valid audit records: `assets_audit_chain` gives the
`compliance` object the record's `obligation_resolution` is resolved from and, on the
reversal record, the vectors of the original record and of the reversal receipt
(`input.original`, `input.receipt`); `ict_incident_record` gives the incident event the
record must mirror, as a vector ID (`input.event`) or as an explicit payload
(`input.event_payload`). A schema-valid vector may also carry a scenario.

### Signatures outside a crypto block

A signed object (a `message`, or the `data` of an `arsia-message` or
`arsia-relay-attestation` schema-ref) that carries `security.sig` but no `crypto` block
has a signature that verifies mathematically, under the Draft-02 profile, with the key
`keypairs.json` publishes for its `kid`. The exception is a vector that declares
`signature_expectation`:

```json
"signature_expectation": { "result": "invalid", "cause": "kid", "condition": "binding" }
```

It may appear only on a vector without `crypto` whose signed object carries
`security.sig` as a string; the meta-schema enforces both conditions. It does not change
`valid`, `expected` or `expected_error`. Every `security.sig` outside a crypto block, declared
or not, is canonical base64url without padding (the URL-safe alphabet only, no `=`, unused
trailing bits zero); the guard checks the encoding before any cause, so a declared negative
never carries an additional encoding defect. The causes are these, and `check_consistency.py`
demonstrates the declared one while every other condition holds:
- `kid`: `binding`, where the kid's agent differs from `from` (or, for an attestation, from
  `broker_id`) while the signature verifies; or `unresolved`, where no key is published;
- `alg`: `not-allowed`, outside the allowlist; or `incompatible` with the key;
- `key`: `size`, an available RSA key below 2048 bits, under which the signature verifies;
- `signature`: `length`, a validly encoded signature of the wrong decoded length; or
  `mismatch`, a well-formed signature that does not verify.

A missing key does not prove a weak one, and a malformed signature does not prove a
wrong binding. The declared negatives are INV-11 and ITV-445 (`kid`/`binding`), ITV-425
(`key`/`size`), ITV-426 (`signature`/`length`, 32 bytes) and ITV-550 (`alg`/`not-allowed`).
`scripts/regen_v2.py --catalog --ids …` re-signs vectors without a crypto block. It refuses
a vector that declares `signature_expectation` or that has no `security.sig`.

### Posture

A vector whose expected outcome rests on an option the protocol permits but does not
require — a MAY, or an optional configuration such as strict mode — declares the
option it assumes in `posture`: the specification, section, `basis` (`MAY` or
`configuration`), the verbatim `text` that grants the option, and what the
expectation `assumes`. The expectation holds for an implementation that takes that
option. An implementation that does not take it is not non-conformant for failing
the vector; a conformance runner should report such a vector as not applicable.

## Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Vector identifier (`^[A-Z]+-\d+$`) |
| `description` | string | yes | Human-readable description |
| `expected_error` | string \| null | yes | Expected error for invalid vectors, `null` for valid |
| `category` | string | no | Spec area: core, identity, actions, state, routing, assets |
| `valid` | boolean | format-dep | Whether the vector is valid (message-only format) |
| `expected` | string | format-dep | `"valid"` or `"invalid"` (schema-ref and hybrid formats) |
| `message` | object | format-dep | Full ARSIA message envelope (message-only, hybrid) |
| `data` | object | format-dep | Data payload (schema-ref) |
| `schema_ref` | string | format-dep | Schema file or JSON Pointer reference (schema-ref, hybrid) |
| `crypto` | object | no | Key material, canonical bytes and signature (Ed25519, ES256, or RS256), with `expect_signature`: `valid` (the signature MUST verify), `invalid` (it MUST fail — a signature negative) or `absent` (the message deliberately has no `security` object; only the canonical bytes are checked). Independent of `valid`/`expected`/`expected_error` |
| `req_ids` | array | no | Linked requirement IDs (`req:hex`) |
| `skip_schema` | boolean | no | If `true`, validate structure only; the runtime expectation is evaluated separately |
| `skip_reason` | string | dep | Required when `skip_schema` is `true` |
| `test_metadata` | object | no | Auxiliary context for runtime-only vectors (e.g., token scope, authorization context, reference requests, harness scenarios) |
| `posture` | object | no | Option the expectation assumes (see Posture) |
| `signature_expectation` | object | no | Declared signature negative of a vector without `crypto` (see Signatures outside a crypto block) |

## Validation

### Schema validation (all formats)

```bash
# TAP output (default)
python3 scripts/validate_vectors.py --format tap

# Summary table
python3 scripts/validate_vectors.py --format summary

# JUnit XML (for CI)
python3 scripts/validate_vectors.py --format junit

# Include meta-schema check
python3 scripts/validate_vectors.py --check-meta --format summary

# Filter by vector ID glob
python3 scripts/validate_vectors.py --filter 'ITV-*'

# Filter by schema name
python3 scripts/validate_vectors.py --schema arsia-state-operations

# Verify invalid vectors fail for the expected reason
python3 scripts/validate_vectors.py --check-errors --format summary
```

### Verify signatures (Python)

The Python snippets below run from the `test-vectors/` directory.

```python
import json, base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from cryptography.hazmat.primitives.serialization import load_der_public_key

data = json.load(open('arsia-test-vectors.json'))
for v in data['vectors']:
    c = v.get('crypto')
    if not c or c['expect_signature'] != 'valid':
        continue
    env = v['message'] if isinstance(v.get('message'), dict) else v['data']  # the signed object
    alg = env['security']['alg']
    pub = bytes.fromhex(c['public_key_hex'])
    sig = base64.urlsafe_b64decode(c['signature_base64url'] + '==')
    canonical = bytes.fromhex(c['canonical_bytes_hex'])
    if alg == 'EdDSA':
        Ed25519PublicKey.from_public_bytes(pub).verify(sig, canonical)
    elif alg == 'ES256':  # raw r||s -> DER
        der = encode_dss_signature(int.from_bytes(sig[:32], 'big'), int.from_bytes(sig[32:], 'big'))
        ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), pub).verify(der, canonical, ec.ECDSA(hashes.SHA256()))
    else:  # RS256, DER public key
        load_der_public_key(pub).verify(sig, canonical, padding.PKCS1v15(), hashes.SHA256())
    print(f'{v["id"]}: VALID')
```

### Verify canonical bytes (Python, requires `rfc8785`)

```python
import json, rfc8785

data = json.load(open('arsia-test-vectors.json'))
for v in data['vectors']:
    if 'crypto' not in v:
        continue
    env = v['message'] if isinstance(v.get('message'), dict) else v['data']  # the signed object
    msg = json.loads(json.dumps(env))
    msg.get('security', {}).pop('sig', None)  # Draft-02 profile: only security.sig is removed
    canonical = rfc8785.dumps(msg)
    expected = bytes.fromhex(v['crypto']['canonical_bytes_hex'])
    assert canonical == expected, f'{v["id"]}: MISMATCH'
    print(f'{v["id"]}: canonical OK')
```

## CI

Vector validation runs automatically via `.github/workflows/validate-vectors.yml`
on push and PR to `main`. The workflow validates all vectors against their schemas
(with meta-schema check), verifies error paths and signatures, runs the consistency
checks and the runtime harness, and uploads a JUnit XML report as a build artifact.

---

*ARSIA Protocol ([arsiaprotocol.org](https://arsiaprotocol.org)) | by [Arsia Labs](https://arsialabs.ai)*
