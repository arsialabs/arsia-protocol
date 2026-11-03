<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
# ARSIA Protocol — Test Vectors

815 test vectors (469 schema-valid, 198 expected-invalid, 148 runtime-only — validator classification) for
validating ARSIA Protocol implementations. Vectors with a `crypto` block use real Ed25519,
ES256 (ECDSA P-256), and RS256 (RSASSA-PKCS1-v1_5) signatures, and declare the expected
verification outcome (`crypto.expect_signature`).

## Files

| File | Description |
|------|-------------|
| [arsia-test-vectors.json](arsia-test-vectors.json) | 815 test vectors |
| [keypairs.json](keypairs.json) | 15 test keypairs: 13 Ed25519, 1 ES256, 1 RS256 (NOT secrets — committed intentionally; the derivation of the six added in the vector cycle is stated in the file) |

## Vector Formats

Each vector matches one of three discriminated formats defined by the
meta-schema (`schemas/arsia-test-vectors.meta.json`):

| Format | Count | Description |
|--------|-------|-------------|
| `message-only` | 323 | Full message validated against `arsia-message.schema.json`. Uses `message` + `valid` fields. |
| `schema-ref` | 488 | Data payload validated against a named schema. Uses `schema_ref` + `data` + `expected` fields. |
| `hybrid` | 4 | Full message validated against a named schema. Uses `schema_ref` + `message` + `expected` fields. |

## ID Prefixes

| Prefix | Category | Count |
|--------|----------|-------|
| `ITV-` | Cross-spec (identity, state, routing, assets, actions, core) | 687 |
| `INV-` | Invalid (all specs) | 100 |
| `CTV-` | Core (envelope, intents, compliance) | 10 |
| `STV-` | State (operations, audit records) | 7 |
| `ATV-` | Assets (receipts, reversals, escrow) | 6 |
| `ACTV-` | Actions (explainability, rollback) | 3 |
| `RTV-` | Routing (broker relay) | 2 |

Next available ID: **ITV-688** / **INV-101**

## Runtime-Only Vectors

All signed vectors use the **Draft-02 (wire 2.0) signing profile**: the signing input
is the RFC 8785 canonical form of the envelope with `security` present and only the
`security.sig` property removed (Core §5.1). Vectors are regenerated with
`scripts/regen_v2.py`; verify with `--check-crypto`.

148 vectors have `skip_schema: true` with a corresponding `skip_reason`.
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
store produces. A
schema-valid vector may also carry a scenario.

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

```python
import json, base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

data = json.load(open('arsia-test-vectors.json'))
for v in data['vectors']:
    c = v.get('crypto')
    if not c or c['expect_signature'] != 'valid' or v['message']['security']['alg'] != 'EdDSA':
        continue
    pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(c['public_key_hex']))
    sig = base64.urlsafe_b64decode(c['signature_base64url'] + '==')
    canonical = bytes.fromhex(c['canonical_bytes_hex'])
    pub.verify(sig, canonical)
    print(f'{v["id"]}: VALID')
```

### Verify canonical bytes (Python, requires `rfc8785`)

```python
import json, rfc8785

data = json.load(open('arsia-test-vectors.json'))
for v in data['vectors']:
    if 'crypto' not in v:
        continue
    msg = json.loads(json.dumps(v['message']))
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
