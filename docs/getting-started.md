<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Getting Started with the ARSIA Protocol

This guide takes you from zero to a validated, signed ARSIA message in under 15 minutes. You will generate a keypair, create a message envelope, sign and verify it, apply a compliance profile, and validate the result against the protocol's JSON Schemas. Every step uses the Python SDK with references to the normative spec sections.

**Prerequisites:** Python 3.12+, pip.

---

## 1. Install the SDK

```bash
pip install arsia-protocol
```

Verify the installation:

```python
import arsia_protocol
print(arsia_protocol.__version__)
```

---

## 2. Create, Sign, and Verify a Message

The core ARSIA flow is: build an envelope, sign it with Ed25519, and verify the signature. This is what every ARSIA agent does on every message.

```python
from arsia_protocol import (
    create_request, generate_ed25519_keypair, sign_message,
    verify_message, validate_envelope,
)
import json

# Generate an Ed25519 keypair (Core §5.1).
private_key, public_key = generate_ed25519_keypair()
kid = "agent:acme.bot#key-1"

# Build a request envelope (Core §4).
envelope = create_request(
    from_agent="agent:acme.bot",
    to_agent="agent:partner.svc",
    payload_type="com.arsiaprotocol.echo",
    capabilities=["com.arsiaprotocol.echo"],
    args={"message": "Hello from ARSIA"},
)

# Sign the envelope (Core §5.1).
# The SDK canonicalizes the envelope with JCS (RFC 8785), signs the
# canonical bytes with Ed25519, and sets the security field.
signed = sign_message(envelope, private_key, kid)

# Verify the signature (Core §5.2).
assert verify_message(signed, public_key) is True

# Validate envelope structure and cross-field semantics.
errors = validate_envelope(signed)
assert errors == []

print(json.dumps(signed, indent=2))
```

The output is a complete ARSIA message envelope with `v`, `id`, `ts`, `from`, `to`, `intent`, `payload`, `expires_at`, `capabilities`, and `security` fields. The `security.sig` field contains the base64url-encoded Ed25519 signature over the canonicalized envelope.

**What just happened:**

| Step | SDK function | Spec reference |
|------|-------------|----------------|
| Generate keypair | `generate_ed25519_keypair()` | Core §5.1, Identity §2.1 |
| Build envelope | `create_request()` | Core §4 |
| Sign | `sign_message()` | Core §5.1 |
| Verify signature | `verify_message()` | Core §5.2 |
| Validate structure | `validate_envelope()` | Core §4.3 |

---

## 3. Apply a Compliance Profile

ARSIA defines 7 compliance profiles that map EU regulations to protocol fields (State §6). When you set a profile, `apply_profile()` fills in the regulatory defaults — retention period, oversight mode, audit requirements.

```python
from arsia_protocol import create_request, apply_profile, validate_compliance

# Build a request under the EU AI Act high-risk profile.
envelope = create_request(
    from_agent="agent:acme.hr-screener",
    to_agent="agent:acme.compliance-checker",
    payload_type="com.arsiaprotocol.screen",
    capabilities=["com.arsiaprotocol.screen"],
    args={"candidate_id": "C-1234"},
    compliance={
        "profile": "EU-AI-ACT-HIGH-RISK",
        "pii_involved": True,
        "legal_basis": "contract",
        "data_residency": "EU",
    },
)

# Apply profile defaults (retention_days, human_oversight, etc.).
envelope = apply_profile(envelope)

# The compliance field now has all regulatory defaults filled in:
#   retention_days: 180
#   human_oversight: "required_before_execution"
#   audit_required: true
#   explainability_required: true

# Validate compliance rules (Core §4.3.8).
errors = validate_compliance(envelope)
assert errors == []
```

**What happens when a required field is missing?** ARSIA rejects messages that declare `pii_involved: true` without a `legal_basis` — this enforces GDPR Art. 6 at the protocol level (Core §4.3.8, Rule 2):

```python
bad_envelope = create_request(
    from_agent="agent:acme.hr-screener",
    to_agent="agent:acme.compliance-checker",
    payload_type="com.arsiaprotocol.screen",
    capabilities=["com.arsiaprotocol.screen"],
    args={"candidate_id": "C-1234"},
    compliance={
        "profile": "EU-AI-ACT-HIGH-RISK",
        "pii_involved": True,
        # no legal_basis — this will fail validation
    },
)

errors = validate_compliance(bad_envelope)
print(errors[0].message)
# → "R2: compliance.legal_basis is required when
#    compliance.pii_involved is true (Core §4.3.8 Rule 2)"
```

---

## 4. Validate Against JSON Schemas

The protocol ships 31 JSON Schemas (Draft 2020-12) in [`schemas/`](../schemas/) that validate every structure in the spec.

**Option A — SDK convenience function:**

```python
from arsia_protocol import validate_schema

errors = validate_schema(signed)
assert errors == []
```

**Option B — Direct schema validation** (useful for non-Python implementations):

```bash
pip install jsonschema
```

```python
import json
from pathlib import Path
from jsonschema import validate, Draft202012Validator
from referencing import Registry, Resource

schemas_dir = Path("schemas")

# Build a registry so $ref resolution works across schema files.
registry = Registry()
for schema_file in schemas_dir.glob("*.schema.json"):
    schema = json.loads(schema_file.read_text())
    resource = Resource.from_contents(schema)
    registry = registry.with_resource(schema["$id"], resource)

# Validate an envelope against the message schema.
message_schema = json.loads(
    (schemas_dir / "arsia-message.schema.json").read_text()
)
validator = Draft202012Validator(message_schema, registry=registry)
validator.validate(signed)  # raises on error
```

---

## 5. Run the Validation Script

The spec repo includes a validation script that checks all 613 test vectors against the JSON Schemas, with optional cryptographic signature verification:

```bash
cd scripts/
pip install -r requirements.txt
python validate_vectors.py               # schema validation only
python validate_vectors.py --check-crypto # + signature verification
```

The test vectors in [`test-vectors/`](../test-vectors/) include 514 valid and 99 invalid cases with real Ed25519, ES256, and RS256 signatures. Use them to verify your own implementation produces and accepts correct envelopes.

---

## 6. Conformance Levels

ARSIA defines three conformance levels so you can adopt progressively (Core §12):

| Level | Name | What it requires |
|-------|------|-----------------|
| 1 | **Core** | Envelope validation, Ed25519 signing/verification, OAuth 2.0 authorization, discovery, HTTP/2 transport, idempotency |
| 2 | **Compliance** | Core + compliance profiles, audit trail, human oversight signaling, brokered routing for data residency |
| 3 | **Full** | Compliance + all 5 domain primitives, all profiles, WebSocket, payload encryption, ES256 |

**Core** is the minimum viable implementation — secure agent communication without regulatory features. **Compliance** is the minimum for EU-regulated environments. **Full** is the complete protocol, suitable for reference implementations.

---

## 7. What's Next

**Go deeper with the specs:**

- [Core](../spec/ARSIA-Core.md) — message envelope, security, authorization, transport
- [Actions](../spec/ARSIA-Actions.md) — capabilities, human oversight (EU AI Act Art. 14)
- [State](../spec/ARSIA-State.md) — audit trail, GDPR obligations, compliance profiles

**Build with the SDK:**

- [Learning Path](https://github.com/arsialabs/arsia-protocol-sdk/blob/main/python/docs/learning-path.md) — step-by-step from install to production
- [Cookbook](https://github.com/arsialabs/arsia-protocol-sdk/blob/main/python/docs/cookbook.md) — 19 copy-pasteable recipes

**Evaluate for compliance:**

- [Compliance profiles](../profiles/) — 7 profiles mapping EU regulation to protocol fields
- [Security model](security.md) — threat model, cryptographic foundation, data protection
- [RTMs](rtm/) — 6 Requirements Traceability Matrices (2,086 rows)

---

ARSIA Protocol ([arsiaprotocol.org](https://arsiaprotocol.org)) | by [Arsia Labs](https://arsialabs.ai)
