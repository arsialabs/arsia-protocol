<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
# ARSIA Protocol — JSON Schemas

JSON Schema Draft 2020-12 validation schemas for all ARSIA Protocol data structures.

## Schemas (31)

| Schema | Spec | Validates |
|--------|------|-----------|
| [arsia-message.schema.json](arsia-message.schema.json) | Core §4 | Full message envelope |
| [arsia-compliance-field.schema.json](arsia-compliance-field.schema.json) | Core §4.3.6 | Compliance sub-fields |
| [arsia-common.schema.json](arsia-common.schema.json) | Core | Shared definitions for the protocol schema suite |
| [arsia-discovery-response.schema.json](arsia-discovery-response.schema.json) | Core §7.1 | Agent metadata from discovery endpoint |
| [arsia-capability-descriptor.schema.json](arsia-capability-descriptor.schema.json) | Core §7.2 | Single capability exposed by an agent |
| [arsia-jwt-claims.schema.json](arsia-jwt-claims.schema.json) | Core §6.1 | Access token JWT claims and OAuth 2.0 token response |
| [arsia-dpop-proof.schema.json](arsia-dpop-proof.schema.json) | Core §6.3 | DPoP proof JWT payload per RFC 9449 |
| [arsia-jwk-entry.schema.json](arsia-jwk-entry.schema.json) | Core §7.3 | JWK entry in an agent's JWKS |
| [arsia-websocket-frame.schema.json](arsia-websocket-frame.schema.json) | Core §8.2 | WebSocket control frames (auth, ping, pong) |
| [arsia-compliance-profiles.schema.json](arsia-compliance-profiles.schema.json) | Core | Compliance profiles registry structure |
| [arsia-identity-record.schema.json](arsia-identity-record.schema.json) | Identity §1.2 | Agent identity record |
| [arsia-capability-policy.schema.json](arsia-capability-policy.schema.json) | Identity §8.1 | Capability policy for onboarding |
| [arsia-onboarding-decision.schema.json](arsia-onboarding-decision.schema.json) | Identity §7.6 | Onboarding decision (approved/denied) payload |
| [arsia-action-descriptor.schema.json](arsia-action-descriptor.schema.json) | Actions §2.1 | Action registry entries |
| [arsia-explanation.schema.json](arsia-explanation.schema.json) | Actions §5.2 | Explainability object (EU AI Act Art. 13) |
| [arsia-action-discovery-response.schema.json](arsia-action-discovery-response.schema.json) | Actions §2.3 | Paginated response from action discovery endpoint |
| [arsia-asset-transfer-request.schema.json](arsia-asset-transfer-request.schema.json) | Assets §3.1.1 | Transfer request payload |
| [arsia-asset-transfer-receipt.schema.json](arsia-asset-transfer-receipt.schema.json) | Assets §3.2.1 | Transfer receipt payload |
| [arsia-asset-transfer-reversal.schema.json](arsia-asset-transfer-reversal.schema.json) | Assets §3.3.1 | Transfer reversal payload |
| [arsia-escrow-conditions.schema.json](arsia-escrow-conditions.schema.json) | Assets §4.1 | Escrow conditions |
| [arsia-dora-incident.schema.json](arsia-dora-incident.schema.json) | Assets §6.2.2 | DORA incident event payload |
| [arsia-mifid-audit-record.schema.json](arsia-mifid-audit-record.schema.json) | Assets §6.1 | MiFID II audit record for asset transfers |
| [arsia-state-entry.schema.json](arsia-state-entry.schema.json) | State §2.1 | State entry |
| [arsia-audit-record.schema.json](arsia-audit-record.schema.json) | State §7.1 | Audit trail record |
| [arsia-state-operations.schema.json](arsia-state-operations.schema.json) | State §3 | Payload args/result for all 8 state operations |
| [arsia-audit-query-response.schema.json](arsia-audit-query-response.schema.json) | State §7.4 | Paginated response from audit trail query endpoint |
| [arsia-broker-entry.schema.json](arsia-broker-entry.schema.json) | Routing §7.2 | Compliance broker entry |
| [arsia-broker-discovery-request.schema.json](arsia-broker-discovery-request.schema.json) | Routing §7.2 | Broker discovery query parameters |
| [arsia-breach-notification.schema.json](arsia-breach-notification.schema.json) | State §5.7 | GDPR breach notification payload (Art. 33/34) |
| [arsia-broker-relay-audit.schema.json](arsia-broker-relay-audit.schema.json) | Routing §7.4 | Broker relay audit record |
| [arsia-test-vectors.meta.json](arsia-test-vectors.meta.json) | Meta | Meta-schema validating the structure of arsia-test-vectors.json |

## Conventions

- `$schema`: `https://json-schema.org/draft/2020-12/schema`
- `$id`: `https://arsiaprotocol.org/schemas/{name}/v1.0.json`
- `additionalProperties: false` unless the spec explicitly allows extension
- Every property has a `description` referencing the spec section
- Conditional required fields use `if/then` inside `allOf`
- Agent ID, UUID, timestamp, and country code patterns are shared across all schemas

## Validation

```bash
# With jsonschema (Python)
pip install jsonschema
python -c "
import json, jsonschema
schema = json.load(open('arsia-message.schema.json'))
vector = json.load(open('../test-vectors/arsia-test-vectors.json'))['vectors'][0]
jsonschema.validate(vector['message'], schema)
print('Valid')
"
```

---

*ARSIA Protocol ([arsiaprotocol.org](https://arsiaprotocol.org)) | by [Arsia Labs](https://arsialabs.ai)*
