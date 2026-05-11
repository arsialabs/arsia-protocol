#!/usr/bin/env python3
# SPDX-License-Identifier: BUSL-1.1
# Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda)
"""Generate ARSIA-State §3–§11 test vectors (Vec-2)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VECTORS_FILE = ROOT / "test-vectors" / "arsia-test-vectors.json"

OPS = "arsia-state-operations.schema.json"
ENTRY = "arsia-state-entry.schema.json"
AUDIT = "arsia-audit-record.schema.json"

def audit_record(event_type, from_a, to_a, payload_type, profile="GDPR-STANDARD", **extra):
    rec = {
        "record_id": extra.pop("record_id", "b0000001-0001-4001-a001-000000000001"),
        "message_id": extra.pop("message_id", "a0000001-0001-4001-8001-000000000001"),
        "event_type": event_type,
        "from_agent": from_a,
        "to_agent": to_a,
        "intent": extra.pop("intent", "request"),
        "payload_type": payload_type,
        "payload_hash": extra.pop("payload_hash", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        "compliance_profile": profile,
        "processed_at": extra.pop("processed_at", "2026-04-15T10:00:00.000Z"),
        "retained_until": extra.pop("retained_until", "2026-07-14T10:00:00.000Z"),
        "operator_id": extra.pop("operator_id", "VAT:PT501234567"),
    }
    rec.update(extra)
    return rec

def state_entry(key, value, owner, scope, pii="none", version=1, **extra):
    entry = {
        "key": key,
        "value": value,
        "owner_agent_id": owner,
        "scope": scope,
        "created_at": extra.pop("created_at", "2026-04-15T09:00:00.000Z"),
        "updated_at": extra.pop("updated_at", "2026-04-15T09:00:00.000Z"),
        "pii_classification": pii,
        "version": version,
    }
    entry.update(extra)
    return entry


vectors = [
    # ── §3.1.1 GET ──────────────────────────────────────────────────
    {
        "id": "ITV-215",
        "description": "State §3.1.1: Valid GET for session-scoped entry — runtime MUST verify the requesting agent is one of the two session participants before returning the entry. Per ARSIA-State.md §3.1.1.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/get",
            "args": {"key": "agent:acme.billing/session/risk-context"}
        },
        "expected_error": None, "req_ids": []
    },

    # ── §3.1.2 SET ──────────────────────────────────────────────────
    {
        "id": "ITV-216",
        "description": "State §3.1.2: INVALID — SET with scope 'global'. Agents MUST NOT create global-scoped entries through SET; attempting this MUST result in error code 'forbidden'. Per ARSIA-State.md §3.1.2.",
        "schema_ref": OPS, "expected": "invalid",
        "data": {
            "type": "arsiaprotocol.state/set",
            "args": {
                "key": "agent:acme.billing/global/exchange-rates",
                "value": {"EUR_USD": 1.08, "EUR_GBP": 0.86},
                "scope": "global",
                "pii_classification": "none"
            }
        },
        "expected_error": "forbidden", "req_ids": []
    },
    {
        "id": "ITV-217",
        "description": "State §3.1.2: Valid SET with pii_classification 'personal' and data_residency — runtime MUST verify compliance.legal_basis is present in the message envelope, rejecting with 'invalid_request' if missing. Per ARSIA-State.md §3.1.2 rule 3.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/set",
            "args": {
                "key": "agent:acme.billing/agent/personal/client-42",
                "value": {"name": "Maria Silva", "vat": "PT501234567"},
                "scope": "agent",
                "pii_classification": "personal",
                "data_residency": "EU",
                "retention_days": 90
            }
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-218",
        "description": "State §3.1.2: Valid SET structure — runtime MUST reject when serialized value exceeds 1,048,576 bytes with error code 'payload_too_large'. Size enforcement is programmatic, not schema-level. Per ARSIA-State.md §3.1.2 rule 6.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/set",
            "args": {
                "key": "agent:acme.billing/agent/large-dataset",
                "value": {"records": [{"id": i, "payload": "x" * 100} for i in range(50)]},
                "scope": "agent",
                "pii_classification": "none"
            }
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-219",
        "description": "State §3.1.2: INVALID — SET with scope 'shared' but key containing '/agent/' scope segment. The scope segment of the key MUST match the scope field in payload.args. Per ARSIA-State.md §3.1.2 rule 2.",
        "schema_ref": OPS, "expected": "invalid",
        "data": {
            "type": "arsiaprotocol.state/set",
            "args": {
                "key": "agent:acme.billing/agent/config",
                "value": {"setting": "value"},
                "scope": "shared",
                "pii_classification": "none"
            }
        },
        "expected_error": "invalid_request", "req_ids": []
    },
    {
        "id": "ITV-220",
        "description": "State §3.1.2: Valid state_set audit record — when audit_required is true, SET MUST generate an audit event of type 'state_set' with key, owner, actor, version, pii_classification, and timestamp. Per ARSIA-State.md §3.1.2.",
        "schema_ref": AUDIT, "expected": "valid",
        "data": audit_record(
            "state_set", "agent:acme.billing", "agent:acme.state-store",
            "arsiaprotocol.state/set",
            record_id="b0000001-0001-4001-a001-000000000220",
            message_id="a0000001-0001-4001-8001-000000000220",
            profile="EU-AI-ACT-HIGH-RISK",
            retained_until="2026-10-12T10:00:00.000Z",
        ),
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-221",
        "description": "State §3.1.2: Valid state_set audit record — the audit event MUST NOT include the entry value. The audit record stores payload_hash (SHA-256), not raw payload content. Per ARSIA-State.md §3.1.2.",
        "schema_ref": AUDIT, "expected": "valid",
        "data": audit_record(
            "state_set", "agent:acme.billing", "agent:acme.state-store",
            "arsiaprotocol.state/set",
            record_id="b0000001-0001-4001-a001-000000000221",
            message_id="a0000001-0001-4001-8001-000000000221",
            payload_hash="a948904f2f0f479b8f8564e9a07e39e2e2ac7a0b7c55a7c3e0b3a0b7c55a7c3e",
        ),
        "expected_error": None, "req_ids": []
    },

    # ── §3.1.3 DELETE ───────────────────────────────────────────────
    {
        "id": "ITV-222",
        "description": "State §3.1.3: Valid DELETE — after logical deletion, the entry MUST remain visible via SNAPSHOT within its retention period. DELETE does not accelerate physical removal. Per ARSIA-State.md §3.1.3.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/delete",
            "args": {"key": "agent:acme.billing/agent/retained-entry"}
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-223",
        "description": "State §3.1.3: Valid state_delete audit record — when audit_required is true, DELETE MUST generate an audit event of type 'state_delete'. Per ARSIA-State.md §3.1.3.",
        "schema_ref": AUDIT, "expected": "valid",
        "data": audit_record(
            "state_delete", "agent:acme.billing", "agent:acme.state-store",
            "arsiaprotocol.state/delete",
            record_id="b0000001-0001-4001-a001-000000000223",
            message_id="a0000001-0001-4001-8001-000000000223",
        ),
        "expected_error": None, "req_ids": []
    },

    # ── §3.1.4 QUERY ────────────────────────────────────────────────
    {
        "id": "ITV-224",
        "description": "State §3.1.4: Valid QUERY — runtime MUST NOT return entries that the requesting agent is not authorised to access, regardless of filter criteria. Per ARSIA-State.md §3.1.4.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/query",
            "args": {"scope": "agent", "key_prefix": "agent:acme.billing/agent/"}
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-225",
        "description": "State §3.1.4: Valid QUERY for another agent's entries without a grant — result MUST be empty (not an error). Per ARSIA-State.md §3.1.4.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/query",
            "args": {"owner_agent_id": "agent:other.agent", "scope": "agent"}
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-226",
        "description": "State §3.1.4: Valid QUERY with time-based filter — results MUST be ordered by created_at ascending (oldest first) for deterministic pagination. Per ARSIA-State.md §3.1.4.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/query",
            "args": {
                "scope": "agent",
                "owner_agent_id": "agent:acme.billing",
                "key_prefix": "agent:acme.billing/agent/",
                "created_after": "2026-01-01T00:00:00.000Z",
                "limit": 100
            }
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-227",
        "description": "State §3.1.4: Valid QUERY with limit 1500 — runtime MUST clamp to maximum 1000 entries per query, not reject the request. Per ARSIA-State.md §3.1.4.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/query",
            "args": {"scope": "agent", "limit": 1500}
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-228",
        "description": "State §3.1.4: Valid QUERY with limit 2000 — MUST succeed (clamped to 1000), not rejected. Requests with limit exceeding 1000 MUST be clamped. Per ARSIA-State.md §3.1.4.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/query",
            "args": {"scope": "agent", "limit": 2000, "offset": 0}
        },
        "expected_error": None, "req_ids": []
    },

    # ── §3.2.1 SNAPSHOT ─────────────────────────────────────────────
    {
        "id": "ITV-229",
        "description": "State §3.2.1: Valid SNAPSHOT with far-future as_of — runtime MUST reject when as_of is beyond clock skew tolerance (±300s) with error 'invalid_request'. Per ARSIA-State.md §3.2.1.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/snapshot",
            "args": {"as_of": "2099-12-31T23:59:59.000Z"}
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-230",
        "description": "State §3.2.1: Valid SNAPSHOT with future as_of and filter — runtime MUST return error code 'invalid_request' for future timestamps. Per ARSIA-State.md §3.2.1.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/snapshot",
            "args": {
                "as_of": "2099-01-01T00:00:00.000Z",
                "filter": {"scope": "agent", "owner_agent_id": "agent:acme.billing"}
            }
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-231",
        "description": "State §3.2.1: Valid SNAPSHOT with very old as_of — runtime MUST reject when as_of predates the oldest retained version with error 'invalid_request'. Per ARSIA-State.md §3.2.1.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/snapshot",
            "args": {"as_of": "2000-01-01T00:00:00.000Z"}
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-232",
        "description": "State §3.2.1: Valid SNAPSHOT with historical as_of predating available history — runtime MUST return error 'invalid_request' with details { snapshot_unavailable: true, oldest_available: ... }. Per ARSIA-State.md §3.2.1.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/snapshot",
            "args": {
                "as_of": "2020-06-15T12:00:00.000Z",
                "filter": {"scope": "agent"}
            }
        },
        "expected_error": None, "req_ids": []
    },

    # ── §3.2.2 PURGE ────────────────────────────────────────────────
    {
        "id": "ITV-233",
        "description": "State §3.2.2: Valid state_purge audit record — PURGE audit event MUST NOT contain the purged value. The audit record stores payload_hash, not raw content. Per ARSIA-State.md §3.2.2.",
        "schema_ref": AUDIT, "expected": "valid",
        "data": audit_record(
            "state_purge", "agent:acme.billing", "agent:acme.state-store",
            "arsiaprotocol.state/purge",
            record_id="b0000001-0001-4001-a001-000000000233",
            message_id="a0000001-0001-4001-8001-000000000233",
        ),
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-234",
        "description": "State §3.2.2: Valid PURGE operation — after PURGE, SNAPSHOT queries for the key at any time MUST return null for the entry value. Per ARSIA-State.md §3.2.2.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/purge",
            "args": {"key": "agent:acme.billing/agent/gdpr/user-12345"}
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-235",
        "description": "State §3.2.2: Valid PURGE operation — if the entry has active grants, those grants MUST be automatically revoked as part of PURGE. Per ARSIA-State.md §3.2.2 step 6.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/purge",
            "args": {"key": "agent:acme.billing/agent/shared-data-with-grants"}
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-236",
        "description": "State §3.2.2: Valid state_revoke audit record from PURGE — grant revocation audit events MUST be generated for each revoked grant during PURGE. Per ARSIA-State.md §3.2.2 step 6.",
        "schema_ref": AUDIT, "expected": "valid",
        "data": audit_record(
            "state_revoke", "agent:acme.billing", "agent:acme.state-store",
            "arsiaprotocol.state/purge",
            record_id="b0000001-0001-4001-a001-000000000236",
            message_id="a0000001-0001-4001-8001-000000000236",
        ),
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-237",
        "description": "State §3.2.2: Valid state_purge audit record — the audit event MUST NOT contain the purged value (erasure must not be defeated by the audit trail). Per ARSIA-State.md §3.2.2.",
        "schema_ref": AUDIT, "expected": "valid",
        "data": audit_record(
            "state_purge", "agent:acme.billing", "agent:acme.state-store",
            "arsiaprotocol.state/purge",
            record_id="b0000001-0001-4001-a001-000000000237",
            message_id="a0000001-0001-4001-8001-000000000237",
            payload_hash="c3ab8ff13720e8ad9047dd39466b3c8974e592c2fa383d4a3960714caef0c4f2",
        ),
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-238",
        "description": "State §3.2.2: Valid PURGE operation structure — runtime MUST deny PURGE to agents with only arsiaprotocol.state.* wildcard capability. arsiaprotocol.state.purge MUST be explicitly granted. Per ARSIA-State.md §3.2.2.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/purge",
            "args": {"key": "agent:acme.billing/agent/restricted-data"}
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-239",
        "description": "State §3.2.2: Valid PURGE operation — PURGE is idempotent. A second PURGE on the same key MUST return success and MUST NOT generate a second audit event. Per ARSIA-State.md §3.2.2.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/purge",
            "args": {"key": "agent:acme.billing/agent/already-purged-entry"}
        },
        "expected_error": None, "req_ids": []
    },

    # ── §3.3.1 GRANT ────────────────────────────────────────────────
    {
        "id": "ITV-240",
        "description": "State §3.3.1: INVALID — GRANT with key_pattern not starting with 'agent:' prefix. The key_pattern MUST start with the granting agent's agent-id prefix. Per ARSIA-State.md §3.3.1.",
        "schema_ref": OPS, "expected": "invalid",
        "data": {
            "type": "arsiaprotocol.state/grant",
            "args": {
                "key_pattern": "shared:admin/entries*",
                "grantee_agent_id": "agent:acme.risk-assessor",
                "access_level": "read"
            }
        },
        "expected_error": "forbidden", "req_ids": []
    },
    {
        "id": "ITV-241",
        "description": "State §3.3.1: Valid GRANT structure with another agent's prefix — runtime MUST reject GRANT requests where the key_pattern agent-id does not match the request's 'from' field. Per ARSIA-State.md §3.3.1.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/grant",
            "args": {
                "key_pattern": "agent:other.agent/agent/data*",
                "grantee_agent_id": "agent:acme.risk-assessor",
                "access_level": "read"
            }
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-242",
        "description": "State §3.3.1: Valid GRANT structure — runtime MUST reject when key_pattern prefix does not match the 'from' field of the request message. Per ARSIA-State.md §3.3.1.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/grant",
            "args": {
                "key_pattern": "agent:acme.billing/agent/risk-*",
                "grantee_agent_id": "agent:acme.compliance-checker",
                "access_level": "read_write",
                "valid_until": "2026-12-31T23:59:59.000Z"
            }
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-243",
        "description": "State §3.3.1: Valid GET for non-owned entry — runtime MUST verify an active grant exists before permitting access. If no matching grant is found, reject with 'forbidden'. Per ARSIA-State.md §3.3.1.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/get",
            "args": {"key": "agent:acme.billing/agent/shared-risk-data"}
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-244",
        "description": "State §3.3.1: Valid state_grant audit record — when audit_required is true, GRANT MUST generate an audit event of type 'state_grant'. Per ARSIA-State.md §3.3.1.",
        "schema_ref": AUDIT, "expected": "valid",
        "data": audit_record(
            "state_grant", "agent:acme.billing", "agent:acme.state-store",
            "arsiaprotocol.state/grant",
            record_id="b0000001-0001-4001-a001-000000000244",
            message_id="a0000001-0001-4001-8001-000000000244",
        ),
        "expected_error": None, "req_ids": []
    },

    # ── §3.3.2 REVOKE ───────────────────────────────────────────────
    {
        "id": "ITV-245",
        "description": "State §3.3.2: Valid REVOKE — after revocation, the grantee MUST be denied access on the next operation. Per ARSIA-State.md §3.3.2.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/revoke",
            "args": {"grant_id": "a0b1c2d3-e4f5-4a6b-8c7d-9e0f1a2b3c4d"}
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-246",
        "description": "State §3.3.2: Valid REVOKE — revocation of a non-existent or already-revoked grant MUST return success (idempotent) and MUST NOT generate a second revocation audit event. Per ARSIA-State.md §3.3.2.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/revoke",
            "args": {"grant_id": "f0e1d2c3-b4a5-4968-8776-554433221100"}
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-247",
        "description": "State §3.3.2: Valid REVOKE structure — runtime MUST verify the requesting agent is the original grantor. Non-grantor attempts MUST be rejected. Per ARSIA-State.md §3.3.2.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/revoke",
            "args": {"grant_id": "11223344-5566-4778-899a-bbccddeeff00"}
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-248",
        "description": "State §3.3.2: Valid REVOKE structure — runtime MUST reject when the 'from' field of the REVOKE request does not match the grantor of the specified grant, returning 'forbidden'. Per ARSIA-State.md §3.3.2.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/revoke",
            "args": {"grant_id": "aabbccdd-eeff-4001-8002-112233445566"}
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-249",
        "description": "State §3.3.2: Valid state_revoke audit record — when audit_required is true, REVOKE MUST generate an audit event of type 'state_revoke'. Per ARSIA-State.md §3.3.2.",
        "schema_ref": AUDIT, "expected": "valid",
        "data": audit_record(
            "state_revoke", "agent:acme.billing", "agent:acme.state-store",
            "arsiaprotocol.state/revoke",
            record_id="b0000001-0001-4001-a001-000000000249",
            message_id="a0000001-0001-4001-8001-000000000249",
        ),
        "expected_error": None, "req_ids": []
    },

    # ── §4.1.1 Retention Hierarchy ──────────────────────────────────
    {
        "id": "ITV-250",
        "description": "State §4.1.1: Valid state entry with retention_days — the entry MUST NOT be physically deleted before the regulatory minimum retention period expires. Per ARSIA-State.md §4.1.1.",
        "schema_ref": ENTRY, "expected": "valid",
        "data": state_entry(
            "agent:acme.billing/agent/mifid-record",
            {"transaction_id": "TXN-2026-001", "amount": 50000},
            "agent:acme.billing", "agent",
            pii="pseudonymised", version=1,
            retention_days=1825, data_residency="EU",
        ),
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-251",
        "description": "State §4.1.1: Valid SET with retention_days below profile minimum — runtime MUST enforce that entry-level retention MUST NOT reduce retention below the regulatory minimum. Per ARSIA-State.md §4.1.1.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/set",
            "args": {
                "key": "agent:acme.billing/agent/short-retention-attempt",
                "value": {"data": "test"},
                "scope": "agent",
                "pii_classification": "none",
                "retention_days": 30
            }
        },
        "expected_error": None, "req_ids": []
    },

    # ── §4.1.2 Default Retention per Profile ────────────────────────
    {
        "id": "ITV-252",
        "description": "State §4.1.2: Valid state entry under PAC-AGRICULTURE profile — entry data MUST NOT be physically removed before 365 days from creation. Per ARSIA-State.md §4.1.2.",
        "schema_ref": ENTRY, "expected": "valid",
        "data": state_entry(
            "agent:acme.agri-monitor/agent/subsidy-calc-2026",
            {"hectares": 150, "crop": "wheat", "subsidy_eur": 45000},
            "agent:acme.agri-monitor", "agent",
            retention_days=365,
        ),
        "expected_error": None, "req_ids": []
    },

    # ── §4.1.4 Retention and Logical Deletion ───────────────────────
    {
        "id": "ITV-253",
        "description": "State §4.1.4: Valid SNAPSHOT for logically deleted entry within retention — DELETE hides entry from GET/QUERY but SNAPSHOT MUST still return it during the retention period. Per ARSIA-State.md §4.1.4.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/snapshot",
            "args": {
                "as_of": "2026-04-15T10:00:00.000Z",
                "filter": {
                    "scope": "agent",
                    "owner_agent_id": "agent:acme.billing",
                    "key_prefix": "agent:acme.billing/agent/deleted-but-retained"
                }
            }
        },
        "expected_error": None, "req_ids": []
    },

    # ── §4.2.3 Residency Violation Handling ─────────────────────────
    {
        "id": "ITV-254",
        "description": "State §4.2.3: Valid SET with data_residency for unavailable zone — runtime MUST reject with 'invalid_request' and details { data_residency_violation: true, required_zone: ... }. Per ARSIA-State.md §4.2.3.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/set",
            "args": {
                "key": "agent:acme.billing/agent/eu-only-data",
                "value": {"sensitive": "data"},
                "scope": "agent",
                "pii_classification": "personal",
                "data_residency": "EU"
            }
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-255",
        "description": "State §4.2.3: Valid SET with unavailable data_residency zone — runtime MUST NOT silently store data in the wrong zone; a clear, deterministic failure is required. Per ARSIA-State.md §4.2.3.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/set",
            "args": {
                "key": "agent:acme.billing/agent/zone-restricted",
                "value": {"client_data": "confidential"},
                "scope": "agent",
                "pii_classification": "personal",
                "data_residency": "JP"
            }
        },
        "expected_error": None, "req_ids": []
    },

    # ── §4.3.2 Archival Guarantees ──────────────────────────────────
    {
        "id": "ITV-256",
        "description": "State §4.3.2: Valid SNAPSHOT covering archived entry's time range — archived entries MUST remain available via SNAPSHOT for 12 months after archival. Per ARSIA-State.md §4.3.2.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/snapshot",
            "args": {
                "as_of": "2026-01-15T12:00:00.000Z",
                "filter": {
                    "scope": "agent",
                    "owner_agent_id": "agent:acme.billing",
                    "key_prefix": "agent:acme.billing/agent/archived-"
                }
            }
        },
        "expected_error": None, "req_ids": []
    },

    # ── §5.2 Legal Basis (Art. 6) ───────────────────────────────────
    {
        "id": "ITV-257",
        "description": "State §5.2: Valid SET with pii_classification 'personal' — runtime MUST reject when compliance.legal_basis is missing from the message envelope, per GDPR Art. 6 requirement. Error: 'invalid_request' with { missing_legal_basis: true }. Per ARSIA-State.md §5.2.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/set",
            "args": {
                "key": "agent:acme.billing/agent/personal/customer-99",
                "value": {"email": "user@example.com", "name": "Ana Costa"},
                "scope": "agent",
                "pii_classification": "personal",
                "data_residency": "PT"
            }
        },
        "expected_error": None, "req_ids": []
    },

    # ── §5.4 Data Minimisation ──────────────────────────────────────
    {
        "id": "ITV-258",
        "description": "State §5.4: Valid SET structure — runtime SHOULD enforce configurable per-agent limits (max entries, max storage, max personal entries) and reject when exceeded. Per ARSIA-State.md §5.4.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/set",
            "args": {
                "key": "agent:acme.billing/agent/limit-test-entry",
                "value": {"counter": 10001},
                "scope": "agent",
                "pii_classification": "none"
            }
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-259",
        "description": "State §5.4: Valid GET for session-scoped entry — after session ends, session-scoped entries MUST expire and GET MUST return null. Per ARSIA-State.md §5.4.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/get",
            "args": {"key": "agent:acme.billing/session/expired-session-data"}
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-260",
        "description": "State §5.4: Valid session-scoped state entry without explicit expires_at — runtime MUST set effective expiry to match session duration. Per ARSIA-State.md §5.4.",
        "schema_ref": ENTRY, "expected": "valid",
        "data": state_entry(
            "agent:acme.billing/session/temp-context",
            {"session_data": "temporary"},
            "agent:acme.billing", "session",
        ),
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-261",
        "description": "State §5.4: Valid state entry without explicit retention_days or expires_at — runtime MUST apply default expiry per scope (session: session duration, agent: 90 days RECOMMENDED). Per ARSIA-State.md §5.4.",
        "schema_ref": ENTRY, "expected": "valid",
        "data": state_entry(
            "agent:acme.billing/agent/no-explicit-retention",
            {"config": "default-expiry"},
            "agent:acme.billing", "agent",
        ),
        "expected_error": None, "req_ids": []
    },

    # ── §6.4 PAC-AGRICULTURE ────────────────────────────────────────
    {
        "id": "ITV-262",
        "description": "State §6.4: Valid message with compliance_profile 'PAC-AGRICULTURE' — implementations MUST accept this profile name without error. Per ARSIA-State.md §6.4.",
        "category": "state",
        "valid": True,
        "message": {
            "v": "1.0",
            "id": "a0000001-0001-4001-8001-000000000262",
            "ts": "2026-04-15T10:00:00.000Z",
            "from": "agent:acme.agri-monitor",
            "to": "agent:acme.state-store",
            "intent": "request",
            "expires_at": "2026-04-15T10:00:30.000Z",
            "capabilities": ["arsiaprotocol.state.write"],
            "compliance": {
                "profile": "PAC-AGRICULTURE",
                "audit_required": True,
                "retention_days": 365,
                "data_residency": "EU"
            },
            "payload": {
                "type": "arsiaprotocol.state/set",
                "args": {
                    "key": "agent:acme.agri-monitor/agent/subsidy-calc-2026q2",
                    "value": {"hectares": 200, "crop": "maize", "subsidy_eur": 60000},
                    "scope": "agent",
                    "pii_classification": "none"
                }
            }
        },
        "expected_error": None, "req_ids": []
    },

    # ── §7.4 Audit Trail Query Endpoint ─────────────────────────────
    {
        "id": "ITV-263",
        "description": "State §7.4: Valid GET operation — requesting the audit endpoint without arsiaprotocol.audit.read capability MUST be denied. Per ARSIA-State.md §7.4.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/get",
            "args": {"key": "agent:acme.billing/agent/audit-access-test"}
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-264",
        "description": "State §7.4: Valid QUERY operation — audit trail recipient MUST check for arsiaprotocol.audit.read capability before returning audit records. Per ARSIA-State.md §7.4.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/query",
            "args": {"scope": "agent", "owner_agent_id": "agent:acme.billing"}
        },
        "expected_error": None, "req_ids": []
    },

    # ── §8.1 Payload Type Prefix ────────────────────────────────────
    {
        "id": "ITV-265",
        "description": "State §8.1: INVALID — custom operation with reserved 'arsiaprotocol.state/' prefix in state operations schema. Implementations MUST NOT define custom state operations under this prefix. Per ARSIA-State.md §8.1.",
        "schema_ref": OPS, "expected": "invalid",
        "data": {
            "type": "arsiaprotocol.state/custom-archive",
            "args": {"key": "agent:acme.billing/agent/archive-batch"}
        },
        "expected_error": "forbidden", "req_ids": []
    },
    {
        "id": "ITV-266",
        "description": "State §8.1: INVALID — message with custom operation using reserved 'arsiaprotocol.state/' prefix. The message schema enforces that arsiaprotocol.state/ types MUST be one of the 8 defined operations. Per ARSIA-State.md §8.1.",
        "category": "state",
        "valid": False,
        "message": {
            "v": "1.0",
            "id": "a0000001-0001-4001-8001-000000000266",
            "ts": "2026-04-15T10:00:00.000Z",
            "from": "agent:acme.state-extension",
            "to": "agent:acme.state-store",
            "intent": "request",
            "expires_at": "2026-04-15T10:00:30.000Z",
            "capabilities": ["arsiaprotocol.state.write"],
            "payload": {
                "type": "arsiaprotocol.state/custom-archive",
                "args": {"key": "agent:acme.state-extension/agent/archive-batch"}
            }
        },
        "expected_error": "forbidden", "req_ids": []
    },

    # ── §8.2.1 Capability Hierarchy ─────────────────────────────────
    {
        "id": "ITV-267",
        "description": "State §8.2.1: Valid PURGE operation structure — the arsiaprotocol.state.* wildcard MUST NOT grant arsiaprotocol.state.purge or arsiaprotocol.state.snapshot. These elevated capabilities MUST be explicitly granted. Per ARSIA-State.md §8.2.1.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/purge",
            "args": {"key": "agent:acme.billing/agent/wildcard-test"}
        },
        "expected_error": None, "req_ids": []
    },

    # ── §8.2.2 Capability Enforcement ───────────────────────────────
    {
        "id": "ITV-268",
        "description": "State §8.2.2: Valid SET operation — runtime MUST enforce capabilities per Core §6.4. If required capability is missing, reject with 'forbidden' and details showing required vs provided capabilities. Per ARSIA-State.md §8.2.2.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/set",
            "args": {
                "key": "agent:acme.billing/agent/capability-test",
                "value": {"test": True},
                "scope": "agent",
                "pii_classification": "none"
            }
        },
        "expected_error": None, "req_ids": []
    },

    # ── §8.3 Compliance Inheritance ─────────────────────────────────
    {
        "id": "ITV-269",
        "description": "State §8.3: Valid state_set audit record with compliance profile — when the envelope's compliance.audit_required is true, all state operations MUST generate audit events regardless of default audit configuration. Per ARSIA-State.md §8.3.",
        "schema_ref": AUDIT, "expected": "valid",
        "data": audit_record(
            "state_set", "agent:acme.billing", "agent:acme.state-store",
            "arsiaprotocol.state/set",
            record_id="b0000001-0001-4001-a001-000000000269",
            message_id="a0000001-0001-4001-8001-000000000269",
            profile="EU-AI-ACT-HIGH-RISK",
            retained_until="2026-10-12T10:00:00.000Z",
            human_oversight_status="not_required",
            data_residency="EU",
        ),
        "expected_error": None, "req_ids": []
    },

    # ── §9 State Conformance Tests ──────────────────────────────────
    {
        "id": "ITV-270",
        "description": "State §9: Valid state_purge audit record — conformance test STATE-03 verifies PURGE audit event does not contain the purged value. The audit record stores payload_hash only. Per ARSIA-State.md §9.",
        "schema_ref": AUDIT, "expected": "valid",
        "data": audit_record(
            "state_purge", "agent:acme.billing", "agent:acme.state-store",
            "arsiaprotocol.state/purge",
            record_id="b0000001-0001-4001-a001-000000000270",
            message_id="a0000001-0001-4001-8001-000000000270",
            payload_hash="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        ),
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-271",
        "description": "State §9: Valid state entry with retention_days — conformance test STATE-05 verifies entries are protected during their retention period and not physically removed before retention expires. Per ARSIA-State.md §9.",
        "schema_ref": ENTRY, "expected": "valid",
        "data": state_entry(
            "agent:acme.billing/agent/retention-protected",
            {"transaction": "TXN-2026-042", "status": "completed"},
            "agent:acme.billing", "agent",
            pii="pseudonymised", version=3,
            retention_days=180, data_residency="EU",
            updated_at="2026-04-15T14:30:00.000Z",
        ),
        "expected_error": None, "req_ids": []
    },

    # ── §10.1 Access Control ────────────────────────────────────────
    {
        "id": "ITV-272",
        "description": "State §10.1: Valid SET operation — runtime MUST reject state operations without a valid access token (authorization failure returns 'unauthorized'). Per ARSIA-State.md §10.1.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/set",
            "args": {
                "key": "agent:acme.billing/agent/auth-test",
                "value": {"test": "unauthorized-attempt"},
                "scope": "agent",
                "pii_classification": "none"
            }
        },
        "expected_error": None, "req_ids": []
    },

    # ── §10.2 Injection and Abuse ───────────────────────────────────
    {
        "id": "ITV-273",
        "description": "State §10.2: Valid QUERY — QUERY/GET for inaccessible entries MUST return empty results (not errors) to prevent enumeration attacks. Per ARSIA-State.md §10.2.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/query",
            "args": {
                "scope": "agent",
                "owner_agent_id": "agent:secret.agent",
                "key_prefix": "agent:secret.agent/agent/"
            }
        },
        "expected_error": None, "req_ids": []
    },

    # ── §10.3 Side-Channel Risks ────────────────────────────────────
    {
        "id": "ITV-274",
        "description": "State §10.3: Valid QUERY — result count MUST reflect only entries accessible to the requesting agent, not the total system count. Per ARSIA-State.md §10.3.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/query",
            "args": {"scope": "agent", "limit": 100, "offset": 0}
        },
        "expected_error": None, "req_ids": []
    },

    # ── §11.3 Performance Considerations ────────────────────────────
    {
        "id": "ITV-275",
        "description": "State §11.3: Valid SET operation — after SET, an immediate GET MUST return the updated value (cache must be invalidated). Per ARSIA-State.md §11.3.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/set",
            "args": {
                "key": "agent:acme.billing/agent/cache-test",
                "value": {"version": "updated", "ts": "2026-04-15T15:00:00.000Z"},
                "scope": "agent",
                "pii_classification": "none"
            }
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-276",
        "description": "State §11.3: Valid SET with expected_version for cache verification — after SET, GET MUST reflect the new version number, confirming cache invalidation. Per ARSIA-State.md §11.3.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/set",
            "args": {
                "key": "agent:acme.billing/agent/versioned-cache",
                "value": {"counter": 42},
                "scope": "agent",
                "pii_classification": "none",
                "expected_version": 5
            }
        },
        "expected_error": None, "req_ids": []
    },
    {
        "id": "ITV-277",
        "description": "State §11.3: Valid SET operation — batch operations MUST generate individual audit events for each affected entry; a single batch audit event is not sufficient for regulatory compliance. Per ARSIA-State.md §11.3.",
        "schema_ref": OPS, "expected": "valid",
        "data": {
            "type": "arsiaprotocol.state/set",
            "args": {
                "key": "agent:acme.billing/agent/batch-entry-1",
                "value": {"batch_id": "BATCH-2026-001", "seq": 1},
                "scope": "agent",
                "pii_classification": "none"
            }
        },
        "expected_error": None, "req_ids": []
    },
]

assert len(vectors) == 63, f"Expected 63 vectors, got {len(vectors)}"

with open(VECTORS_FILE) as f:
    data = json.load(f)

last_id = data["vectors"][-1]["id"]
print(f"Last existing vector: {last_id}")
print(f"Appending {len(vectors)} new vectors (ITV-215 through ITV-277)")

data["vectors"].extend(vectors)

with open(VECTORS_FILE, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"Total vectors in file: {len(data['vectors'])}")
print("Done.")
