# SPDX-License-Identifier: BUSL-1.1
# Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda)
"""Draft-02 signing helpers and selective re-signer of valid signed vectors.

Implements the v2 signing profile (Core §5.1): the signing input is the RFC 8785
canonical form of the envelope with `security` PRESENT and only the `security.sig`
property removed.

The re-signer updates the signature of vectors named explicitly, typically after an
edit to a signed envelope. It never migrates or edits an envelope: only
`security.sig`, `crypto.canonical_bytes_hex` and `crypto.signature_base64url` change.

Usage:
  python3 scripts/regen_v2.py --ids ITV-03,CTV-02             # dry run: what would change, per ID
  python3 scripts/regen_v2.py --ids ITV-03 --apply            # write
  python3 scripts/regen_v2.py --ids ... --vectors PATH        # another corpus file

Rules: every ID is checked before anything is written, and one unknown or ineligible
ID aborts the run with nothing written. Only vectors whose `crypto.expect_signature`
is "valid" are eligible (signature negatives and "absent" blocks are fixtures, never
re-signed). Before signing, the declared alg must be allowlisted and compatible with
the public key, and the private key must derive exactly `public_key_hex`; the
produced signature is verified with the validator's own verifier before writing.
Unselected vectors and the file format (including the presence or absence of a final
newline) are preserved byte for byte: a file the tool's serializer would not reproduce
exactly (other escapes, CRLF line endings, other spacing) is refused with nothing
written. ES256 signatures differ from run to run.
"""
import argparse
import copy
import hashlib
import json
import sys

try:
    import rfc8785
except ImportError:  # pragma: no cover
    # No fallback: code-point key order (json.dumps sort_keys) is not RFC 8785 (Core §5.1).
    sys.exit("ERROR: rfc8785 library required (scripts/requirements.txt)")

VECTORS = "test-vectors/arsia-test-vectors.json"


def jcs(obj) -> bytes:
    return rfc8785.dumps(obj)


def signing_input_v2(message: dict) -> bytes:
    """v2 signing profile: security present, only `sig` removed (Core §5.1)."""
    m = copy.deepcopy(message)
    sec = m.get("security")
    if isinstance(sec, dict):
        sec.pop("sig", None)
    return jcs(m)


def envelope_hash(message: dict) -> str:
    """sha-256:<hex> over the RFC 8785 form of the COMPLETE signed envelope, `security.sig`
    included — the `envelope_hash` of a relay attestation (Routing §7.4.1).

    Reference helper: no tool calls it yet. On its own it does not verify an attestation
    (signature, `envelope_hash` and `token_hash` checks); that coverage is tracked as A-56."""
    return "sha-256:" + hashlib.sha256(jcs(message)).hexdigest()


def b64url(b: bytes) -> str:
    import base64

    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


class Refused(Exception):
    """A vector the re-signer will not write; the message states the reason."""


def _public_bytes(alg: str, private_key_hex: str) -> bytes:
    """The public key derived from the private key, in the encoding of `crypto.public_key_hex`."""
    from cryptography.hazmat.primitives import serialization

    if alg == "EdDSA":
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        key = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(private_key_hex))
        return key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    if alg == "ES256":
        from cryptography.hazmat.primitives.asymmetric import ec
        key = ec.derive_private_key(int(private_key_hex, 16), ec.SECP256R1())
        return key.public_key().public_bytes(serialization.Encoding.X962,
                                             serialization.PublicFormat.UncompressedPoint)
    key = serialization.load_der_private_key(bytes.fromhex(private_key_hex), password=None)
    return key.public_key().public_bytes(serialization.Encoding.DER,
                                         serialization.PublicFormat.SubjectPublicKeyInfo)


def _sign(alg: str, private_key_hex: str, data: bytes) -> bytes:
    """The one function that produces a signature (JWS encodings: Ed25519 raw, ES256 r||s, RS256 PKCS#1 v1.5)."""
    if alg == "EdDSA":
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        return Ed25519PrivateKey.from_private_bytes(bytes.fromhex(private_key_hex)).sign(data)
    if alg == "ES256":
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
        key = ec.derive_private_key(int(private_key_hex, 16), ec.SECP256R1())
        r, s = decode_dss_signature(key.sign(data, ec.ECDSA(hashes.SHA256())))
        return r.to_bytes(32, "big") + s.to_bytes(32, "big")
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    key = serialization.load_der_private_key(bytes.fromhex(private_key_hex), password=None)
    return key.sign(data, padding.PKCS1v15(), hashes.SHA256())


def eligibility(vec: dict | None, vid: str) -> None:
    """Raises Refused unless the vector is a valid signed vector the re-signer may update."""
    if vec is None:
        raise Refused(f"{vid}: no such vector")
    crypto = vec.get("crypto")
    if not isinstance(crypto, dict):
        raise Refused(f"{vid}: no crypto block")
    if crypto.get("expect_signature") != "valid":
        raise Refused(f"{vid}: crypto.expect_signature is {crypto.get('expect_signature')!r}, "
                      "only 'valid' vectors are re-signed (negatives and 'absent' blocks are fixtures)")
    env = vec.get("message") if isinstance(vec.get("message"), dict) else vec.get("data")
    if not isinstance(env, dict) or not isinstance(env.get("security"), dict) or not env["security"].get("alg"):
        raise Refused(f"{vid}: no security object with alg")


def resign(vec: dict) -> tuple[bytes, bytes]:
    """(signature, canonical bytes) for the vector's current envelope; writes nothing.

    Refused before signing when the declared alg is not allowlisted, does not match the
    public key, or the private key does not derive `public_key_hex`; refused after signing
    when the produced signature does not verify (Core §5.2 Step 5, the validator's verifier)."""
    from validate_vectors import ALLOWED_ALGS, _key_type, _verify_signature

    vid, crypto = vec["id"], vec["crypto"]
    env = vec.get("message") if isinstance(vec.get("message"), dict) else vec.get("data")
    alg = env["security"]["alg"]
    pub = bytes.fromhex(crypto["public_key_hex"])
    required = {"EdDSA": "Ed25519", "ES256": "P-256", "RS256": "RSA"}.get(alg)
    if alg not in ALLOWED_ALGS or required is None:
        raise Refused(f"refused before signing: {vid}: alg {alg!r} not in the allowlist")
    try:
        key_type = _key_type(pub)
    except Exception as exc:
        raise Refused(f"refused before signing: {vid}: public key not recognised ({exc})")
    if key_type != required:
        raise Refused(f"refused before signing: {vid}: alg {alg} incompatible with {key_type} key")
    try:
        derived = _public_bytes(alg, crypto["private_key_hex"])
    except Exception as exc:
        raise Refused(f"refused before signing: {vid}: private key unusable for {alg} ({type(exc).__name__})")
    if derived != pub:
        raise Refused(f"refused before signing: {vid}: private key does not derive public_key_hex")
    canon = signing_input_v2(env)
    sig = _sign(alg, crypto["private_key_hex"], canon)
    try:
        _verify_signature(alg, pub, sig, canon)
    except Exception as exc:
        raise Refused(f"signature does not verify: {vid}: {type(exc).__name__} {exc}".rstrip())
    return sig, canon


def _without_signature(vec: dict) -> dict:
    """The vector minus the three fields re-signing may change."""
    v = copy.deepcopy(vec)
    env = v.get("message") if isinstance(v.get("message"), dict) else v.get("data")
    env["security"].pop("sig", None)
    v["crypto"].pop("canonical_bytes_hex", None)
    v["crypto"].pop("signature_base64url", None)
    return v


def serialize(doc: dict, original: str) -> bytes:
    """The corpus format: indent 2, unescaped UTF-8, LF, final newline only if the original had one."""
    return (json.dumps(doc, indent=2, ensure_ascii=False) + ("\n" if original.endswith("\n") else "")).encode("utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Re-sign the named valid signed vectors (Core §5.1 profile).")
    ap.add_argument("--ids", required=True, help="comma-separated vector IDs to re-sign")
    ap.add_argument("--apply", action="store_true", help="write the corpus (default: dry run)")
    ap.add_argument("--vectors", default=VECTORS, help=f"corpus file (default: {VECTORS})")
    args = ap.parse_args(argv)

    ids = [i.strip() for i in args.ids.split(",") if i.strip()]
    if not ids:
        print("ERROR: --ids names no vector", file=sys.stderr)
        return 2
    raw_bytes = open(args.vectors, "rb").read()
    raw = raw_bytes.decode("utf-8")
    doc = json.loads(raw)
    if serialize(doc, raw) != raw_bytes:
        # rewriting would change bytes of vectors nobody selected (escapes, line endings, spacing)
        print(f"ERROR: {args.vectors} is not in the format this tool reproduces byte for byte "
              "(indent 2, unescaped UTF-8, LF line endings); nothing written", file=sys.stderr)
        return 1
    by_id = {v["id"]: v for v in doc["vectors"]}

    results = []
    try:
        for vid in ids:
            eligibility(by_id.get(vid), vid)
        for vid in ids:
            vec = by_id[vid]
            sig, canon = resign(vec)
            env = vec.get("message") if isinstance(vec.get("message"), dict) else vec.get("data")
            before = copy.deepcopy(vec)
            env["security"]["sig"] = b64url(sig)
            vec["crypto"]["canonical_bytes_hex"] = canon.hex()
            vec["crypto"]["signature_base64url"] = b64url(sig)
            if _without_signature(vec) != _without_signature(before):
                raise Refused(f"{vid}: re-signing would change more than the signature fields")
            results.append((vid, "unchanged" if vec == before else "re-signed"))
    except Refused as exc:
        print(f"ERROR: {exc}; nothing written", file=sys.stderr)
        return 1

    for vid, state in results:
        print(f"{vid}: {state}")
    if not args.apply:
        print("dry run: corpus not written (use --apply)")
        return 0
    with open(args.vectors, "wb") as f:
        f.write(serialize(doc, raw))
    print(f"written: {args.vectors}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
