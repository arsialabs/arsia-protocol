<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
# ARSIA Protocol — Test Vectors

613 test vectors (514 valid, 99 invalid, 73 runtime-only skipped) for
validating ARSIA Protocol implementations. Vectors use real Ed25519,
ES256 (ECDSA P-256), and RS256 (RSASSA-PKCS1-v1_5) signatures — no
placeholders.

## Files

| File | Description |
|------|-------------|
| [arsia-test-vectors.json](arsia-test-vectors.json) | 613 test vectors |
| [keypairs.json](keypairs.json) | 9 test keypairs: 7 Ed25519, 1 ES256, 1 RS256 (NOT secrets — committed intentionally) |

## Vector Formats

Each vector matches one of three discriminated formats defined by the
meta-schema (`schemas/arsia-test-vectors.meta.json`):

| Format | Count | Description |
|--------|-------|-------------|
| `message-only` | 295 | Full message validated against `arsia-message.schema.json`. Uses `message` + `valid` fields. |
| `schema-ref` | 314 | Data payload validated against a named schema. Uses `schema_ref` + `data` + `expected` fields. |
| `hybrid` | 4 | Full message validated against a named schema. Uses `schema_ref` + `message` + `expected` fields. |

## ID Prefixes

| Prefix | Category | Count |
|--------|----------|-------|
| `ITV-` | Cross-spec (identity, state, routing, assets, actions, core) | 560 |
| `INV-` | Invalid (all specs) | 25 |
| `CTV-` | Core (envelope, intents, compliance) | 10 |
| `STV-` | State (operations, audit records) | 7 |
| `ATV-` | Assets (receipts, reversals, escrow) | 6 |
| `ACTV-` | Actions (explainability, rollback) | 3 |
| `RTV-` | Routing (broker relay) | 2 |

Next available ID: **ITV-561** / **INV-26**

## Runtime-Only Vectors

73 vectors have `skip_schema: true` with a corresponding `skip_reason`.
These test runtime constraints (e.g. signature verification, temporal
checks) that cannot be validated by JSON Schema alone.

| Category | Count |
|----------|-------|
| Temporal / clock | 36 |
| Token / credential context | 10 |
| X.509 certificate validation | 7 |
| Cross-field comparison | 6 |
| Cross-object / cross-message | 5 |
| Non-delegable capability matching | 3 |
| Forward-compatibility | 3 |
| Transport-specific | 3 |

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
| `crypto` | object | no | Key material and signature (Ed25519, ES256, or RS256) |
| `req_ids` | array | no | Linked requirement IDs (`req:hex`) |
| `skip_schema` | boolean | no | If `true`, skip schema validation |
| `skip_reason` | string | dep | Required when `skip_schema` is `true` |
| `test_metadata` | object | no | Auxiliary context for runtime-only vectors (e.g., token scope, authorization context) |

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
    if not v['valid'] or 'crypto' not in v:
        continue
    c = v['crypto']
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
    if not v['valid']:
        continue
    msg = dict(v['message'])
    msg.pop('security', None)
    canonical = rfc8785.dumps(msg)
    expected = bytes.fromhex(v['crypto']['canonical_bytes_hex'])
    assert canonical == expected, f'{v["id"]}: MISMATCH'
    print(f'{v["id"]}: canonical OK')
```

## CI

Vector validation runs automatically via `.github/workflows/validate-vectors.yml`
on push and PR to `main`. The workflow validates all vectors against their schemas
(with meta-schema check) and uploads a JUnit XML report as a build artifact.

---

*ARSIA Protocol ([arsiaprotocol.org](https://arsiaprotocol.org)) | by [Arsia Labs](https://arsialabs.ai)*
