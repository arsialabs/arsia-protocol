#!/usr/bin/env python3
# SPDX-License-Identifier: BUSL-1.1
# Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda)
"""Validate ARSIA test vectors against their JSON Schemas."""

from __future__ import annotations

import argparse
import base64
import copy
import fnmatch
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = ROOT / "schemas"
VECTORS_FILE = ROOT / "test-vectors" / "arsia-test-vectors.json"
META_SCHEMA_FILE = ROOT / "schemas" / "arsia-test-vectors.meta.json"

_ERROR_CODE_RE = re.compile(r"^[a-z]+(_[a-z]+)*$")
_IDENT_RE = re.compile(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*")
_STOP_WORDS = frozenset({
    "a", "an", "and", "are", "at", "be", "both", "but", "by", "can", "do",
    "does", "for", "has", "have", "in", "is", "it", "its", "may", "must",
    "no", "not", "of", "on", "only", "or", "so", "than", "that", "the",
    "this", "to", "use", "using", "was", "when", "with",
})


def check_error_path(expected_error: str, errors: list) -> tuple[bool, str]:
    if _ERROR_CODE_RE.match(expected_error.lower()):
        return True, "error-code (skip)"

    clause = expected_error.split(" — ")[0] if " — " in expected_error else expected_error
    identifiers = _IDENT_RE.findall(clause.lower())
    keywords: set[str] = set()
    for ident in identifiers:
        keywords.add(ident)
        if "." in ident:
            keywords.update(ident.split("."))
    keywords -= _STOP_WORDS

    if not keywords:
        return True, "no keywords (skip)"

    search_parts: list[str] = []
    def _collect(err: object) -> None:
        search_parts.append(err.message.lower())
        search_parts.append(err.validator.lower())
        search_parts.extend(str(p).lower() for p in err.absolute_path)
        for ctx in err.context or []:
            _collect(ctx)
    for error in errors:
        _collect(error)
    combined = " ".join(search_parts)

    for kw in sorted(keywords):
        if kw in combined:
            return True, f"matched '{kw}'"

    path_words: set[str] = set()
    for error in errors:
        path_words.update(str(p).lower() for p in error.absolute_path if isinstance(p, str))
    for kw in sorted(keywords):
        if len(kw) >= 6:
            stem = kw[: len(kw) - 2]
            for pw in path_words:
                if stem in pw:
                    return True, f"matched '{kw}' ~ '{pw}'"

    return False, f"keywords not found: {', '.join(sorted(keywords))}"


def build_registry() -> Registry:
    schemas_by_name: dict[str, dict] = {}
    resources: list[tuple[str, Resource]] = []

    for schema_path in sorted(SCHEMAS_DIR.glob("*.json")):
        with open(schema_path) as f:
            schema = json.load(f)
        schemas_by_name[schema_path.name] = schema
        resource = Resource.from_contents(schema, default_specification=DRAFT202012)
        schema_id = schema.get("$id", "")
        if schema_id:
            resources.append((schema_id, resource))
        resources.append((schema_path.name, resource))

    def retrieve(uri: str) -> Resource:
        fname = uri.rsplit("/", 1)[-1]
        if fname in schemas_by_name:
            return Resource.from_contents(schemas_by_name[fname], default_specification=DRAFT202012)
        raise KeyError(uri)

    return Registry(retrieve=retrieve).with_resources(resources)


def resolve_schema(schema_ref: str, registry: Registry) -> dict:
    if "#" in schema_ref:
        file_part, pointer = schema_ref.split("#", 1)
    else:
        file_part, pointer = schema_ref, ""

    resolved = registry.resolver().lookup(file_part)
    schema = resolved.contents

    if pointer:
        for part in pointer.strip("/").split("/"):
            schema = schema[part]

    return schema


MESSAGE_SCHEMA = "arsia-message.schema.json"
_VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)$")  # Core §4.1.1 pattern


def version_procedure(message: object) -> str:
    """Core §4.1.1 version handling model, selected by the message's own `v`:
    "exact" — the published schema validates exactly the 2.0 minor (rule 1); also used
    when `v` is absent or malformed, so the exact schema reports the defect;
    "major-2-compat" — a newer 2.x minor: validate the known fields and accept unknown
    top-level and payload fields (rules 2-3);
    "version-rejected" — another major: rejected with not_implemented (rule 6)."""
    v = message.get("v") if isinstance(message, dict) else None
    m = _VERSION_RE.match(v) if isinstance(v, str) else None
    if m is None or v == "2.0":
        return "exact"
    return "major-2-compat" if m.group(1) == "2" else "version-rejected"


def major2_compat_schema(exact: dict) -> dict:
    """The 2.0 message schema relaxed only as Core §4.1.1 rule 3 allows: any 2.x `v`, unknown
    top-level fields and unknown fields on the two object payload branches. The exclusivity
    the exact schema derives from additionalProperties:false is restated as discrimination:
    the generic branch excludes `error`, the error branch excludes args/result/data (§4.4.7).
    Required fields, conditionals, formats and the closed `error` object are unchanged."""
    schema = copy.deepcopy(exact)
    schema["$id"] = exact["$id"].replace("arsia-message.schema.json", "arsia-message.major-2-compat.schema.json")
    schema["properties"]["v"] = {"type": "string", "pattern": "^2\\.(0|[1-9]\\d*)$"}
    schema["additionalProperties"] = True
    generic, error_branch = schema["properties"]["payload"]["oneOf"][:2]
    assert "error" in error_branch["required"] and "error" not in generic["properties"]
    generic["additionalProperties"] = True
    generic["not"]["anyOf"].append({"required": ["error"]})
    error_branch["additionalProperties"] = True
    error_branch["not"] = {"anyOf": [{"required": ["args"]}, {"required": ["result"]}, {"required": ["data"]}]}
    return schema


def message_errors(payload: object, schema: dict, registry: Registry) -> tuple[str, list]:
    """Validates a message under the procedure its `v` selects; returns (procedure, errors)."""
    procedure = version_procedure(payload)
    if procedure == "version-rejected":
        major = payload["v"].split(".")[0]
        err = ValidationError(f"major version {major} not supported (Core §4.1.1 rule 6): not_implemented",
                              validator="version", path=["v"])
        return procedure, [err]
    if procedure == "major-2-compat":
        schema = major2_compat_schema(schema)
    return procedure, list(Draft202012Validator(schema, registry=registry).iter_errors(payload))


def determine_expected(vector: dict) -> bool:
    if "valid" in vector and isinstance(vector["valid"], bool):
        return vector["valid"]
    if "expected" in vector:
        return vector["expected"] == "valid"
    raise ValueError(f"Cannot determine expected result for {vector.get('id')}")


def classify_vector(vector: dict) -> tuple[str, str, dict]:
    has_schema_ref = "schema_ref" in vector
    has_data = "data" in vector
    has_message = "message" in vector

    if has_schema_ref and has_data:
        return "schema-ref", vector["schema_ref"], vector["data"]
    if has_schema_ref and has_message:
        return "hybrid", vector["schema_ref"], vector["message"]
    if has_message and not has_schema_ref:
        return "message-only", "arsia-message.schema.json", vector["message"]

    raise ValueError(f"Unknown format for {vector.get('id')}: keys={list(vector.keys())}")


def check_meta_schema(data: dict) -> bool:
    with open(META_SCHEMA_FILE) as f:
        meta = json.load(f)
    validator = Draft202012Validator(meta)
    errors = list(validator.iter_errors(data))
    if errors:
        print("Meta-schema: FAIL", file=sys.stderr)
        for e in errors:
            path = " -> ".join(str(p) for p in e.absolute_path) if e.absolute_path else "(root)"
            print(f"  {path}: {e.message}", file=sys.stderr)
        return False
    print("Meta-schema: OK")
    return True


def _base64url_decode(s: str) -> bytes:
    s += "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s)


ALLOWED_ALGS = ("EdDSA", "ES256", "RS256")  # Core §5.1 Supported Algorithms


def _key_type(pub_bytes: bytes) -> str:
    """Key type of the vector's public key material (the only key information the
    vector format carries): raw 32-byte Ed25519, uncompressed P-256 point, or DER RSA."""
    if len(pub_bytes) == 32:
        return "Ed25519"
    if len(pub_bytes) == 65 and pub_bytes[0] == 0x04:
        return "P-256"
    from cryptography.hazmat.primitives.serialization import load_der_public_key
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
    if isinstance(load_der_public_key(pub_bytes), RSAPublicKey):
        return "RSA"
    raise ValueError("unrecognised public key material")


def _verify_signature(alg: str | None, pub_bytes: bytes, sig_bytes: bytes, data_bytes: bytes) -> None:
    """Verify per Core §5.2 Step 5: the declared alg must be allowlisted and compatible
    with the key type; the declared alg (never the key material) selects the verifier.
    Raises on any failure."""
    if alg not in ALLOWED_ALGS:
        raise ValueError(f"alg not in allowlist: {alg!r}")
    key_type = _key_type(pub_bytes)
    required = {"EdDSA": "Ed25519", "ES256": "P-256", "RS256": "RSA"}[alg]
    if key_type != required:
        raise ValueError(f"alg {alg} incompatible with {key_type} key")
    if alg == "EdDSA":
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        Ed25519PublicKey.from_public_bytes(pub_bytes).verify(sig_bytes, data_bytes)
    elif alg == "ES256":
        from cryptography.hazmat.primitives.asymmetric.ec import (
            EllipticCurvePublicKey, ECDSA, SECP256R1,
        )
        from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
        from cryptography.hazmat.primitives.hashes import SHA256
        key = EllipticCurvePublicKey.from_encoded_point(SECP256R1(), pub_bytes)
        # JWS encodes ES256 as raw r||s (32+32 bytes); cryptography expects DER
        r = int.from_bytes(sig_bytes[:32], "big")
        s = int.from_bytes(sig_bytes[32:], "big")
        der_sig = encode_dss_signature(r, s)
        key.verify(der_sig, data_bytes, ECDSA(SHA256()))
    else:  # RS256
        from cryptography.hazmat.primitives.serialization import load_der_public_key
        from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
        from cryptography.hazmat.primitives.hashes import SHA256
        key = load_der_public_key(pub_bytes)
        if key.key_size < 2048:  # Core §5.1: RSA key MUST be at least 2048 bits
            raise ValueError(f"RSA key {key.key_size} bits < 2048")
        key.verify(sig_bytes, data_bytes, PKCS1v15(), SHA256())


CRYPTO_DATA_SCHEMAS = ("arsia-message.schema.json", "arsia-relay-attestation.schema.json")


def crypto_envelope(vector: dict) -> dict | None:
    """The signed object a crypto block refers to: the message, or the data of a schema-ref vector whose
    schema is a signed object (an envelope or a relay attestation, Routing §7.4.1). Any other data is not
    an envelope."""
    if isinstance(vector.get("message"), dict):
        return vector["message"]
    if vector.get("schema_ref") in CRYPTO_DATA_SCHEMAS and isinstance(vector.get("data"), dict):
        return vector["data"]
    return None


def run_crypto_checks(args: argparse.Namespace) -> int:
    try:
        import rfc8785
    except ImportError:
        # No fallback: a code-point-ordered serialization (json.dumps sort_keys) is
        # not RFC 8785 and would silently diverge on non-BMP member names (Core §5.1).
        print("ERROR: rfc8785 library required for --check-crypto", file=sys.stderr)
        sys.exit(1)
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey  # noqa: F401
    except ImportError:
        print("ERROR: cryptography library required for --check-crypto", file=sys.stderr)
        sys.exit(1)

    vectors_file = Path(args.vectors) if args.vectors else VECTORS_FILE
    with open(vectors_file) as f:
        data = json.load(f)

    vectors = data["vectors"]
    checked = 0
    failed = 0
    verified_count = 0
    negatives_asserted = 0
    absent_count = 0
    failures: list[str] = []

    for vector in vectors:
        crypto = vector.get("crypto")
        if not crypto:
            continue

        vid = vector["id"]
        if args.filter and not fnmatch.fnmatch(vid, args.filter):
            continue

        checked += 1
        msg = crypto_envelope(vector)
        if msg is None:
            failed += 1
            failures.append(f"  FAIL {vid}: crypto block without an envelope (message, or data of "
                            f"{', '.join(CRYPTO_DATA_SCHEMAS)})")
            continue
        # The expected signature outcome is declared, never inferred from valid/expected or
        # expected_error: a vector rejected for authorization or compliance still carries a
        # signature that MUST verify (A-34).
        expectation = crypto.get("expect_signature")
        if expectation not in ("valid", "invalid", "absent"):
            failed += 1
            failures.append(f"  FAIL {vid}: crypto.expect_signature missing or unknown: {expectation!r}")
            continue
        signature_negative = expectation == "invalid"

        # CHECK 1 — canonical bytes (Draft-02 signing profile, Core §5.1:
        # security PRESENT, only the sig property removed)
        msg_copy = copy.deepcopy(msg)
        if isinstance(msg_copy.get("security"), dict):
            msg_copy["security"].pop("sig", None)
        canonical = rfc8785.dumps(msg_copy)
        expected_hex = crypto["canonical_bytes_hex"]
        actual_hex = canonical.hex()
        if actual_hex != expected_hex:
            failed += 1
            failures.append(
                f"  FAIL {vid}: canonical bytes mismatch\n"
                f"    expected: {expected_hex[:80]}...\n"
                f"    actual:   {actual_hex[:80]}..."
            )
            continue

        # CHECK 2 — signature verification (Core §5.2). "absent" declares a message with no
        # security object: there is no envelope signature to verify (Step 1 needs
        # security.sig), only the canonical bytes above, and it is not counted as verified.
        has_security = isinstance(msg.get("security"), dict)
        if expectation == "absent":
            if has_security:
                failed += 1
                failures.append(f"  FAIL {vid}: expect_signature 'absent' but the message has a security object")
            else:
                absent_count += 1
            continue
        if not has_security:
            failed += 1
            failures.append(f"  FAIL {vid}: expect_signature {expectation!r} without a security object")
            continue
        # CHECK 3 — sig field consistency, before verification so that it binds the signature
        # negatives too: the signature asserted here is the one the envelope carries.
        security = msg["security"]
        embedded_sig = None
        if "sig" in security:
            embedded_sig = security["sig"]
        elif "signatures" in security:
            sigs = security["signatures"]
            if sigs and isinstance(sigs, list):
                embedded_sig = sigs[0].get("signature")
        if embedded_sig is None:
            failed += 1
            failures.append(f"  FAIL {vid}: expect_signature {expectation!r} without an embedded signature")
            continue
        if embedded_sig != crypto["signature_base64url"]:
            failed += 1
            failures.append(
                f"  FAIL {vid}: sig field mismatch\n"
                f"    message.security.sig: {embedded_sig[:40]}...\n"
                f"    crypto.signature:     {crypto['signature_base64url'][:40]}..."
            )
            continue
        alg = msg["security"].get("alg")
        pub_bytes = bytes.fromhex(crypto["public_key_hex"])
        sig_bytes = _base64url_decode(crypto["signature_base64url"])
        data_bytes = bytes.fromhex(crypto["canonical_bytes_hex"])
        try:
            _verify_signature(alg, pub_bytes, sig_bytes, data_bytes)
            verified, reason = True, None
        except Exception as exc:
            verified, reason = False, exc
        if signature_negative:
            if verified:
                failed += 1
                failures.append(f"  FAIL {vid}: expected signature failure, but it verified")
            else:
                negatives_asserted += 1
            continue
        if not verified:
            failed += 1
            failures.append(f"  FAIL {vid}: signature verification failed — {reason}")
            continue
        verified_count += 1

    passed = checked - failed
    if failures:
        for f_msg in failures:
            print(f_msg, file=sys.stderr)
    print(f"Crypto: {checked} vectors checked, {passed} passed, {failed} failed "
          f"({verified_count} signatures verified, {negatives_asserted} signature negatives asserted, "
          f"{absent_count} without signature: canonical bytes only)")
    return 1 if failed else 0


def run_validation(args: argparse.Namespace) -> int:
    vectors_file = Path(args.vectors) if args.vectors else VECTORS_FILE
    with open(vectors_file) as f:
        data = json.load(f)

    if args.check_meta:
        if not check_meta_schema(data):
            return 1

    vectors = data["vectors"]

    registry = build_registry()
    results: list[dict] = []

    for vector in vectors:
        vid = vector["id"]

        if args.filter and not fnmatch.fnmatch(vid, args.filter):
            continue

        fmt, schema_ref, payload = classify_vector(vector)

        if vector.get("skip_schema"):
            # A skip exempts only the runtime expectation the schema cannot express.
            # Everything else is still validated: the vector must be structurally valid
            # against its schema, whatever its runtime outcome (valid/expected) is.
            if args.schema and args.schema not in schema_ref:
                continue
            schema = resolve_schema(schema_ref, registry)
            if schema_ref == MESSAGE_SCHEMA:
                procedure, errors = message_errors(payload, schema, registry)
            else:
                procedure, errors = "exact", list(Draft202012Validator(schema, registry=registry).iter_errors(payload))
            results.append({
                "id": vid,
                "schema": schema_ref.split("#")[0],
                "format": fmt,
                "expected_valid": True,
                "actual_valid": not errors,
                "passed": not errors,
                "error": "; ".join(e.message for e in errors[:3]) if errors else None,
                "description": vector.get("description", ""),
                "skipped": True,
                "skip_reason": vector.get("skip_reason", "skip_schema flag set"),
                "procedure": procedure,
            })
            continue

        if args.schema and args.schema not in schema_ref:
            continue

        expected_valid = determine_expected(vector)
        schema = resolve_schema(schema_ref, registry)
        if schema_ref == MESSAGE_SCHEMA:
            procedure, errors = message_errors(payload, schema, registry)
        else:
            procedure, errors = "exact", list(Draft202012Validator(schema, registry=registry).iter_errors(payload))
        actual_valid = len(errors) == 0

        base_ref = schema_ref.split("#")[0] if "#" in schema_ref else schema_ref
        passed = actual_valid == expected_valid
        error_msg = "; ".join(e.message for e in errors[:3]) if errors else None

        error_path = None
        if args.check_errors and not expected_valid and errors:
            expected_error = vector.get("expected_error", "")
            if expected_error:
                error_path = check_error_path(expected_error, errors)

        results.append({
            "id": vid,
            "schema": base_ref,
            "format": fmt,
            "expected_valid": expected_valid,
            "actual_valid": actual_valid,
            "passed": passed,
            "error": error_msg,
            "description": vector.get("description", ""),
            "skipped": False,
            "error_path": error_path,
            "procedure": procedure,
        })

    check = args.check_errors
    if args.format == "summary":
        return print_summary(results, check)
    if args.format == "junit":
        return print_junit(results, check)
    return print_tap(results, check)


def print_tap(results: list[dict], check_errors: bool = False) -> int:
    print("TAP version 14")
    print(f"1..{len(results)}")

    failed = 0
    skipped = 0
    skip_failed = 0
    mismatches = 0
    for i, r in enumerate(results, 1):
        if r.get("skipped"):
            skipped += 1
            reason = r.get("skip_reason", "runtime constraint")
            if r["passed"]:
                print(f"ok {i} - {r['id']} (runtime-only: structure valid; skipped: {reason})")
            else:
                skip_failed += 1
                print(f"not ok {i} - {r['id']} {r['schema']} (runtime-only) — "
                      f"skip vector fails structural validation: {r['error']}")
            continue

        label = "valid" if r["expected_valid"] else "invalid"
        if r.get("procedure", "exact") != "exact":
            label += f", {r['procedure']}"
        desc = f"{r['id']} {r['schema']} ({label}"
        if not r["expected_valid"] and r["description"]:
            desc += f": {r['description']}"
        desc += ")"

        if r["passed"]:
            print(f"ok {i} - {desc}")
        else:
            failed += 1
            if r["expected_valid"]:
                print(f"not ok {i} - {desc} — unexpected error: {r['error']}")
            else:
                print(f"not ok {i} - {desc} — should have failed but passed")

        ep = r.get("error_path")
        if ep:
            matched, detail = ep
            if matched:
                print(f"# error-path: MATCH ({detail})")
            else:
                mismatches += 1
                print(f"# error-path: MISMATCH — {detail}")

    total = len(results)
    passed = total - failed - skipped
    print("# ---")
    print(f"# Passed: {passed}/{total}")
    print(f"# Skipped (runtime-only, structure-validated): {skipped}/{total} "
          f"({skip_failed} structurally invalid)")
    print(f"# Failed: {failed}/{total}")
    if check_errors:
        print(f"# Error-path mismatches: {mismatches}")
    print(f"# Version procedure (Core §4.1.1): {procedure_counts(results)}")

    return 1 if failed or skip_failed or (check_errors and mismatches) else 0


def procedure_counts(results: list[dict]) -> str:
    counts: dict[str, int] = {}
    for r in results:
        if r["schema"] == MESSAGE_SCHEMA:
            counts[r.get("procedure", "exact")] = counts.get(r.get("procedure", "exact"), 0) + 1
    return ", ".join(f"{k} {counts[k]}" for k in sorted(counts))


def print_summary(results: list[dict], check_errors: bool = False) -> int:
    by_schema: dict[str, dict] = {}
    total_skipped = 0
    skip_failed = 0
    mismatches = 0
    for r in results:
        if r.get("skipped"):
            total_skipped += 1
            if not r["passed"]:
                skip_failed += 1
            continue
        s = by_schema.setdefault(r["schema"], {"valid": 0, "invalid": 0, "pass": 0, "fail": 0})
        if r["expected_valid"]:
            s["valid"] += 1
        else:
            s["invalid"] += 1
        if r["passed"]:
            s["pass"] += 1
        else:
            s["fail"] += 1
        ep = r.get("error_path")
        if ep and not ep[0]:
            mismatches += 1

    hdr = f"{'Schema':<45} {'Valid':>5} {'Invalid':>7} {'Pass':>5} {'Fail':>5}"
    print(hdr)
    totals = {"valid": 0, "invalid": 0, "pass": 0, "fail": 0}
    for schema in sorted(by_schema):
        s = by_schema[schema]
        print(f"{schema:<45} {s['valid']:>5} {s['invalid']:>7} {s['pass']:>5} {s['fail']:>5}")
        for k in totals:
            totals[k] += s[k]

    skip_passed = total_skipped - skip_failed
    print(f"{'(runtime-only: structure-validated)':<45} {'':>5} {'':>7} {skip_passed:>5} {skip_failed:>5}")
    print(f"{'TOTAL':<45} {totals['valid']:>5} {totals['invalid']:>7} {totals['pass'] + skip_passed:>5} {totals['fail'] + skip_failed:>5}")
    if check_errors:
        print(f"Error-path mismatches: {mismatches}")
    print(f"Version procedure (Core §4.1.1): {procedure_counts(results)}")

    return 1 if totals["fail"] or skip_failed or (check_errors and mismatches) else 0


def print_junit(results: list[dict], check_errors: bool = False) -> int:
    testsuites = ET.Element("testsuites")
    testsuite = ET.SubElement(testsuites, "testsuite", name="arsia-test-vectors")

    failures = 0
    skipped = 0
    for r in results:
        tc = ET.SubElement(testsuite, "testcase", name=r["id"], classname=r["format"])
        if r.get("procedure", "exact") != "exact":
            ET.SubElement(ET.SubElement(tc, "properties"), "property", name="procedure", value=r["procedure"])
        tc_failed = False
        if r.get("skipped"):
            if r["passed"]:
                skipped += 1
                skip_el = ET.SubElement(tc, "skipped")
                skip_el.set("message", r.get("skip_reason", "skip_schema flag set"))
            else:
                tc_failed = True
                msg = f"skip vector fails structural validation: {r['error']}"
                fail_el = ET.SubElement(tc, "failure", message=msg[:200])
                fail_el.text = msg
        else:
            if not r["passed"]:
                tc_failed = True
                if r["expected_valid"]:
                    msg = f"expected valid but got error: {r['error']}"
                else:
                    msg = "expected invalid but validation passed"
                fail_el = ET.SubElement(tc, "failure", message=msg[:200])
                fail_el.text = msg

            ep = r.get("error_path")
            if ep:
                matched, detail = ep
                props = ET.SubElement(tc, "properties")
                ET.SubElement(props, "property", name="error-path", value="MATCH" if matched else "MISMATCH")
                ET.SubElement(props, "property", name="error-path-detail", value=detail)
                if not matched and check_errors:
                    tc_failed = True
                    fail_el = ET.SubElement(tc, "failure", message=f"error-path mismatch: {detail}"[:200])
                    fail_el.text = f"error-path mismatch: {detail}"

        if tc_failed:
            failures += 1

    testsuite.set("tests", str(len(results)))
    testsuite.set("failures", str(failures))
    testsuite.set("skipped", str(skipped))

    tree = ET.ElementTree(testsuites)
    ET.indent(tree, space="  ")
    tree.write(sys.stdout, encoding="unicode", xml_declaration=True)
    print()
    return 1 if failures else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ARSIA test vectors against JSON Schemas")
    parser.add_argument("--format", choices=["tap", "summary", "junit"], default="tap")
    parser.add_argument("--filter", help="Glob pattern for vector IDs (e.g. 'ITV-*')")
    parser.add_argument("--schema", help="Filter by schema name substring (e.g. 'arsia-message')")
    parser.add_argument("--vectors", help="Path to test vectors JSON (default: test-vectors/arsia-test-vectors.json)")
    parser.add_argument("--check-meta", action="store_true",
                        help="Validate test-vectors file against meta-schema before running")
    parser.add_argument("--check-errors", action="store_true",
                        help="Verify invalid vectors fail for the expected reason")
    parser.add_argument("--check-crypto", action="store_true",
                        help="Verify cryptographic signatures on vectors with crypto blocks")
    args = parser.parse_args()

    exit_code = 0
    if args.check_crypto:
        exit_code |= run_crypto_checks(args)
    exit_code |= run_validation(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
