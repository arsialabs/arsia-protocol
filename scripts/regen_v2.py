# SPDX-License-Identifier: BUSL-1.1
# Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda)
"""Draft-02 v2 signer/generator and one-shot vector regeneration.

Implements the v2 signing profile (DR-D3): the signing input is the RFC 8785
canonical form of the envelope with `security` PRESENT and only the
`security.sig` property removed. Also performs the selective v2 wire migration
of the vector corpus (DR-D5): message-envelope vectors move to v="2.0",
root_request_id, duration retention, string amounts, and authorization binding;
schema-ref vectors are touched only when their target schema changed.

Usage:
  python3 scripts/regen_v2.py --check     # dry run, print affected-vector counts
  python3 scripts/regen_v2.py --apply     # rewrite test-vectors/arsia-test-vectors.json

The affected-vector set is always logged (IDs), per the no-silent-caps rule.
"""
import argparse
import copy
import hashlib
import json
import sys
import uuid

try:
    import rfc8785
except ImportError:  # pragma: no cover
    rfc8785 = None

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

VECTORS = "test-vectors/arsia-test-vectors.json"

REPLY_INTENTS = {"response", "error", "pending_approval", "approval_decision"}


def jcs(obj) -> bytes:
    if rfc8785 is None:
        return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return rfc8785.dumps(obj)


def signing_input_v2(message: dict) -> bytes:
    """v2 signing profile: security present, only `sig` removed (Core §5.1)."""
    m = copy.deepcopy(message)
    sec = m.get("security")
    if isinstance(sec, dict):
        sec.pop("sig", None)
    return jcs(m)


def envelope_hash(message: dict) -> str:
    """sha-256:<hex> over JCS of the COMPLETE signed envelope (Routing §7.4.1)."""
    return "sha-256:" + hashlib.sha256(jcs(message)).hexdigest()


def b64url(b: bytes) -> str:
    import base64

    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def det_uuid4(seed: str) -> str:
    """Deterministic v4-shaped UUID from a seed (for synthetic root ids)."""
    h = hashlib.sha256(seed.encode()).hexdigest()
    return f"{h[0:8]}-{h[8:12]}-4{h[13:16]}-a{h[17:20]}-{h[20:32]}"


def migrate_message(msg: dict, vid: str) -> bool:
    """In-place v2 migration of one message envelope. Returns True if changed."""
    changed = False
    if msg.get("v") == "1.0":
        msg["v"] = "2.0"
        changed = True
    # root_request_id (Core §4.2.4)
    if msg.get("intent") in REPLY_INTENTS and "root_request_id" not in msg:
        if msg.get("intent") == "approval_decision":
            msg["root_request_id"] = det_uuid4(vid + ":root")
        else:
            msg["root_request_id"] = msg.get("correlation_id", det_uuid4(vid + ":root"))
        changed = True
    # retention_days -> retention (Core §4.3.6.4)
    comp = msg.get("compliance")
    if isinstance(comp, dict) and "retention_days" in comp:
        rd = comp.pop("retention_days")
        if rd is not None:
            comp["retention"] = f"P{int(rd)}D"
        changed = True
    # authorization binding required when data_residency set (Core §4.3.9)
    if isinstance(comp, dict) and comp.get("data_residency") and "authorization" not in msg:
        token_seed = f"synthetic-token:{vid}"
        msg["authorization"] = {
            "token_hash": "sha-256:" + hashlib.sha256(token_seed.encode()).hexdigest(),
            "proof_type": "bearer",
        }
        changed = True
    # amounts (payload subtrees) — string form
    changed |= stringify_amounts(msg.get("payload"))
    return changed


def stringify_amounts(o, in_currency=False) -> bool:
    import re

    changed = False
    if isinstance(o, dict):
        cur = in_currency or (
            isinstance(o.get("currency_or_unit"), str)
            and re.fullmatch(r"[A-Z]{3}", o["currency_or_unit"]) is not None
        )
        for k, v in list(o.items()):
            if k in ("amount", "actual_amount", "reversal_amount") and isinstance(v, (int, float)) and not isinstance(v, bool):
                o[k] = f"{v:.2f}" if cur else (repr(float(v))[:-2] if repr(float(v)).endswith(".0") else repr(float(v)))
                changed = True
            else:
                changed |= stringify_amounts(v, cur)
    elif isinstance(o, list):
        for x in o:
            changed |= stringify_amounts(x, in_currency)
    return changed


def resign(vec: dict) -> bool:
    """Re-sign a vector carrying a crypto block under the v2 profile.

    Handles EdDSA (raw 32-byte keys), ES256 (raw scalar / uncompressed point),
    RS256 (DER), and security-less negatives (canonical == whole message)."""
    crypto = vec.get("crypto")
    msg = vec.get("message") or vec.get("data")
    if not crypto or not isinstance(msg, dict):
        return False
    alg = (msg.get("security") or {}).get("alg", "EdDSA")
    canon = signing_input_v2(msg)
    priv_hex = crypto["private_key_hex"]
    if alg == "EdDSA":
        priv = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(priv_hex))
        sig = priv.sign(canon)
        pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(crypto["public_key_hex"]))
        pub.verify(sig, canon)
    elif alg == "ES256":
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

        key = ec.derive_private_key(int(priv_hex, 16), ec.SECP256R1())
        der = key.sign(canon, ec.ECDSA(hashes.SHA256()))
        r, s_ = decode_dss_signature(der)
        sig = r.to_bytes(32, "big") + s_.to_bytes(32, "big")
    elif alg == "RS256":
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding

        key = serialization.load_der_private_key(bytes.fromhex(priv_hex), password=None)
        sig = key.sign(canon, padding.PKCS1v15(), hashes.SHA256())
    else:
        return False
    if isinstance(msg.get("security"), dict):
        msg["security"]["sig"] = b64url(sig)
    crypto["canonical_bytes_hex"] = canon.hex()
    crypto["signature_base64url"] = b64url(sig)
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="write the migrated corpus back to disk (default: dry run)")
    args = ap.parse_args()

    doc = json.load(open(VECTORS))
    migrated, resigned, skipped_es256 = [], [], []
    for vec in doc["vectors"]:
        msg = vec.get("message")
        changed = False
        if isinstance(msg, dict) and "v" in msg:
            changed = migrate_message(msg, vec["id"])
        data = vec.get("data")
        if (
            isinstance(data, dict)
            and vec.get("schema_ref") == "arsia-message.schema.json"
            and "v" in data
        ):
            changed = migrate_message(data, vec["id"]) or changed
        if changed:
            migrated.append(vec["id"])
        # purpose-preserving special cases (before signing)
        if vec["id"] == "INV-09" and isinstance(vec.get("message"), dict):
            # currency precision negative: keep it a grammar/scale violation as a string
            vec["message"]["payload"]["args"]["amount"] = "10.5055"
        if vec["id"] == "INV-08":
            # retention floor is a runtime rule in Draft-02 (DR-D1): schema-valid, runtime-reject
            vec["skip_schema"] = True
            vec["skip_reason"] = ("Runtime constraint — calendar retention-floor comparison "
                                  "(Core §4.3.8 Rule 4); Draft-02 moved floors from schema to runtime")
        if vec.get("crypto"):
            if resign(vec):
                if vec["id"] in ("INV-18", "INV-19"):
                    # deliberately corrupt the first signature byte to preserve the negative
                    import base64 as _b64
                    raw = _b64.urlsafe_b64decode(vec["crypto"]["signature_base64url"] + "==")
                    bad = bytes([raw[0] ^ 0xFF]) + raw[1:]
                    b = b64url(bad)
                    vec["crypto"]["signature_base64url"] = b
                    m2 = vec.get("message") or vec.get("data")
                    if isinstance(m2.get("security"), dict):
                        m2["security"]["sig"] = b
                resigned.append(vec["id"])
            else:
                skipped_es256.append(vec["id"])
        # INV-36 activation
        if vec["id"] == "INV-36" and args.apply:
            vec.pop("skip_schema", None)
            vec.pop("skip_reason", None)
            vec["expected"] = "invalid"
            vec["expected_error"] = "amount must be a canonical decimal string, not a JSON number — Assets §3.1.1"

    print(f"migrated envelopes: {len(migrated)}")
    print(f"re-signed: {len(resigned)}  {resigned}")
    if skipped_es256:
        print(f"SKIPPED (no key material): {skipped_es256}")
    print("migrated ids:", ",".join(migrated))

    if args.apply:
        json.dump(doc, open(VECTORS, "w"), ensure_ascii=False, indent=2)
        open(VECTORS, "a").write("\n")
        print("written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
