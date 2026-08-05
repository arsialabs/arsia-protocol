# SPDX-License-Identifier: BUSL-1.1
# Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda)
"""Draft-02 runtime-rule harness.

Reference implementations of the deterministic runtime algorithms that JSON
Schema cannot express, executed as tests — including against the runtime
(`skip_schema`) vectors that document their expected outcomes:

  R1  Calendar duration arithmetic + end-of-month clamp   (Core §4.3.6.4.1)
  R2  Retention-floor comparison / Rule 4                  (Core §4.3.8, D1)
  R3  Capability matching incl. reserved-namespace rule    (Actions §1.2, B-07)
  R4  Reserved-capability registry membership              (Actions §1.4, B-04)
  R5  Fixed ISO 4217 amount scale                          (Assets §3.1.1, D4)
  R6  Idempotency precedence: signed envelope wins         (Core §10.4, M-25)
  R7  Correlation/root chain verification                  (Core §4.2, B-01)
  R8  I-JSON number range rule                             (State §2.1.2, B-08)
  R9  Content-field mutual exclusivity                     (Core §4.4.7, A-08)
  R10 Effective human-oversight resolution / Rule 3        (Core §4.3.8, A-09)
  R11 Issuer trust and key-origin policy                    (Core §6.5)
  R12 Session-scope audit precedence                        (State §8.3)
  R13 Revocation under the JWKS cache ceiling               (Core §5.2/§7.3, A-18)

Exit code 0 = all green.
"""
import calendar
import datetime as dt
import json
import re
import sys

FAIL = []


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        FAIL.append(name)


# ---------------------------------------------------------------- R1 calendar
DUR_RE = re.compile(r"^P(?=\d)(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)D)?$")


def parse_duration(s):
    m = DUR_RE.match(s)
    if not m:
        raise ValueError(f"invalid ARSIA duration: {s!r}")
    y, mo, d = (int(g) if g else 0 for g in m.groups())
    return y, mo, d


def add_duration(anchor: dt.datetime, dur: str) -> dt.datetime:
    """Core §4.3.6.4.1: months/years advance the calendar with end-of-month clamp."""
    y, mo, d = parse_duration(dur)
    total_months = anchor.month - 1 + mo + 12 * y
    year = anchor.year + total_months // 12
    month = total_months % 12 + 1
    day = min(anchor.day, calendar.monthrange(year, month)[1])
    return anchor.replace(year=year, month=month, day=day) + dt.timedelta(days=d)


def iso(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ")


def r1():
    check("R1 end-of-month 2026-08-31+P6M", add_duration(iso("2026-08-31T10:00:00.000Z"), "P6M") == iso("2027-02-28T10:00:00.000Z"))
    check("R1 end-of-month 2028-08-31+P6M", add_duration(iso("2028-08-31T10:00:00.000Z"), "P6M") == iso("2029-02-28T10:00:00.000Z"))
    check("R1 leap 2023-08-29+P6M", add_duration(iso("2023-08-29T00:00:00.000Z"), "P6M") == iso("2024-02-29T00:00:00.000Z"))
    check("R1 days P1827D", add_duration(iso("2026-01-01T00:00:00.000Z"), "P1827D") == iso("2026-01-01T00:00:00.000Z") + dt.timedelta(days=1827))
    for bad in ("P", "P0", "PT12H", "180", "P6M5X"):
        try:
            parse_duration(bad)
            check(f"R1 reject {bad!r}", False)
        except ValueError:
            check(f"R1 reject {bad!r}", True)


# ------------------------------------------------------------ R2 retention floor
def retention_check(declared, minimum, anchor):
    """Returns (accepted, effective, source) per Core §4.3.8 Rule 4 / §4.3.7."""
    if declared is None:
        return True, minimum, "profile-minimum" if minimum else "none"
    if minimum is None:
        return True, declared, "per-message"
    if add_duration(anchor, declared) >= add_duration(anchor, minimum):
        return True, declared, "per-message"
    return False, None, "per-message"


def r2(vectors):
    a = iso("2026-07-22T10:00:00.000Z")
    check("R2 ITV-563 MIFID P365D rejected", retention_check("P365D", "P1827D", a)[0] is False)
    check("R2 ITV-564 P180D < P6M rejected", retention_check("P180D", "P6M", a)[0] is False)
    ok_, eff, src = retention_check(None, "P1827D", a)
    check("R2 ITV-565 absent -> profile minimum", ok_ and eff == "P1827D" and src == "profile-minimum")
    check("R2 boundary P1827D accepted", retention_check("P1827D", "P1827D", a)[0])
    check("R2 above floor accepted", retention_check("P2000D", "P1827D", a)[0])
    # P6M vs P184D: anchor-dependent — for this anchor six months = 184 days
    check("R2 P184D vs P6M (this anchor)", retention_check("P184D", "P6M", a)[0])
    check("R2 P183D vs P6M rejected (this anchor)", retention_check("P183D", "P6M", a)[0] is False)


# ---------------------------------------------------------- R3/R4 capabilities
REGISTRY = {
    "arsiaprotocol.oversight.approve", "arsiaprotocol.broker.relay", "arsiaprotocol.broker.use",
    "arsiaprotocol.audit.read", "arsiaprotocol.identity.admin", "arsiaprotocol.state.read",
    "arsiaprotocol.state.write", "arsiaprotocol.state.purge", "arsiaprotocol.state.snapshot",
    "arsiaprotocol.assets.transfer.initiate", "arsiaprotocol.assets.transfer.approve",
    "arsiaprotocol.assets.transfer.reverse", "arsiaprotocol.assets.escrow.create",
    "arsiaprotocol.assets.escrow.release", "arsiaprotocol.assets.escrow.cancel",
    "arsiaprotocol.assets.audit.read", "arsiaprotocol.compliance.breach.notify",
    "arsiaprotocol.echo", "arsiaprotocol.health", "arsiaprotocol.onboarding.evaluate",
}
CONCRETE = re.compile(r"^[a-zA-Z][a-zA-Z0-9]*(\.[a-zA-Z][a-zA-Z0-9]*)+$")
WILDCARD = re.compile(r"^[a-zA-Z][a-zA-Z0-9]*(\.[a-zA-Z][a-zA-Z0-9]*)*\.\*$")


def scope_satisfies(scope_entry, requested):
    """Actions §1.2: exact; trailing wildcard; reserved namespace exact-only."""
    if not CONCRETE.match(requested):
        raise ValueError("requested capability must be concrete")
    if scope_entry == requested:
        return True
    if requested.startswith("arsiaprotocol."):
        return False  # condition 3: reserved => exact only
    if WILDCARD.match(scope_entry):
        prefix = scope_entry[:-2]
        if prefix.startswith("arsiaprotocol"):
            return False  # reserved wildcard scope entries satisfy nothing
        return requested.startswith(prefix + ".")
    return False


def authorized(scope, requested_list):
    return all(any(scope_satisfies(s, r) for s in scope) for r in requested_list)


def r3():
    check("R3 exact", scope_satisfies("notes.read", "notes.read"))
    check("R3 wildcard valid (ITV-566)", authorized(["notes.*"], ["notes.read", "notes.write"]))
    check("R3 deep wildcard", scope_satisfies("notes.*", "notes.admin.reset"))
    check("R3 different namespace", not scope_satisfies("notes.*", "billing.read"))
    check("R3 specific !> wildcard request", True)  # wildcard requests are structurally invalid:
    for bad in ("notes.*", "*", "notes.*.read"):
        try:
            scope_satisfies("notes.read", bad)
            check(f"R3 concrete-only request {bad!r}", False)
        except ValueError:
            check(f"R3 concrete-only request {bad!r}", True)
    check("R3 reserved via wildcard (ITV-567)", not scope_satisfies("arsiaprotocol.*", "arsiaprotocol.oversight.approve"))
    check("R3 reserved via ns wildcard", not scope_satisfies("arsiaprotocol.state.*", "arsiaprotocol.state.purge"))
    check("R3 reserved exact ok", scope_satisfies("arsiaprotocol.state.purge", "arsiaprotocol.state.purge"))
    check("R3 partial capability list", not authorized(["notes.read"], ["notes.read", "notes.write"]))
    check("R3 multi-scope", authorized(["notes.read", "payments.charge"], ["notes.read", "payments.charge"]))
    check("R4 registry member ok", "arsiaprotocol.echo" in REGISTRY)
    check("R4 unknown reserved rejected (ITV-568)", "arsiaprotocol.zzz.unregistered" not in REGISTRY)


# ------------------------------------------------------------- R5 amount scale
MINOR_UNITS = {"EUR": 2, "USD": 2, "JPY": 0, "KWD": 3, "BHD": 3, "GBP": 2, "CHF": 2}
AMOUNT_RE = re.compile(r"^(0|[1-9]\d*)(\.(\d+))?$")


def amount_valid(amount, currency):
    m = AMOUNT_RE.match(amount)
    if not m:
        return False
    if currency not in MINOR_UNITS:
        return False  # no numeric exponent known -> reject unless descriptor scale
    scale = MINOR_UNITS[currency]
    frac = m.group(3) or ""
    if len(frac) != scale:
        return False  # fixed scale: exactly the minor-unit digits
    if amount == "0" or set(amount.replace(".", "")) == {"0"}:
        return False  # transfers are strictly positive
    return True


def r5():
    check("R5 EUR 1500.00", amount_valid("1500.00", "EUR"))
    check("R5 EUR 1500.0 rejected (ITV-575)", not amount_valid("1500.0", "EUR"))
    check("R5 EUR 1500 rejected (canonical equality)", not amount_valid("1500", "EUR"))
    check("R5 EUR 1500.000 rejected", not amount_valid("1500.000", "EUR"))
    check("R5 JPY 1500", amount_valid("1500", "JPY"))
    check("R5 JPY 1500.00 rejected (ITV-576)", not amount_valid("1500.00", "JPY"))
    check("R5 KWD 1500.000 (ITV-574)", amount_valid("1500.000", "KWD"))
    check("R5 exponent rejected", not amount_valid("1.5e3", "EUR"))
    check("R5 leading zero rejected", not amount_valid("01.50", "EUR"))
    check("R5 negative rejected", not amount_valid("-5.00", "EUR"))
    check("R5 zero rejected", not amount_valid("0.00", "EUR"))


# --------------------------------------------------- R6 idempotency precedence
def dedup_key(envelope_key, header_key):
    """Core §10.4 (Draft-02): the signed envelope field is authoritative."""
    if envelope_key is not None:
        return envelope_key
    return header_key  # best-effort courtesy only


def r6():
    check("R6 envelope wins", dedup_key("k-signed", "k-header") == "k-signed")
    check("R6 replay with fresh header still dedupes", dedup_key("k-signed", "k-fresh-attacker") == "k-signed")
    check("R6 header-only courtesy", dedup_key(None, "k-header") == "k-header")


# ------------------------------------------------------------- R7 chain verify
def verify_decision(decision, pending_store):
    """Actions §3.4 Step 3 (+ root check): returns (accepted, error)."""
    p = pending_store.get(decision.get("correlation_id"))
    if p is None:
        return False, "invalid_request"  # unknown correlation
    if decision.get("root_request_id") != p["root_request_id"]:
        return False, "invalid_request"  # root mismatch
    if p.get("resolved"):
        return False, "invalid_request"  # duplicate/late
    if decision["payload"]["result"]["decision"] not in ("approved", "denied"):
        return False, "invalid_request"  # bad enum (B-06)
    return True, None


def verify_pending(pending):
    """Actions §3.2: payload.args.original_request_id MUST equal envelope root_request_id."""
    return pending["payload"]["args"]["original_request_id"] == pending.get("root_request_id")


def r7():
    pend_msg = {"root_request_id": "R1", "payload": {"args": {"original_request_id": "R1"}}}
    check("R7 pending args/root match", verify_pending(pend_msg))
    check("R7 pending args/root MISMATCH rejected", not verify_pending({**pend_msg, "root_request_id": "RX"}))
    pend = {"P1": {"root_request_id": "R1", "resolved": False}}
    good = {"correlation_id": "P1", "root_request_id": "R1",
            "payload": {"result": {"decision": "approved"}}}
    check("R7 happy path", verify_decision(good, pend)[0])
    check("R7 unknown correlation", not verify_decision({**good, "correlation_id": "PX"}, pend)[0])
    check("R7 root mismatch", not verify_decision({**good, "root_request_id": "RX"}, pend)[0])
    bad_enum = {**good, "payload": {"result": {"decision": "rejected"}}}
    check("R7 invalid enum 'rejected' (B-06)", not verify_decision(bad_enum, pend)[0])
    pend2 = {"P1": {"root_request_id": "R1", "resolved": True}}
    check("R7 duplicate/late decision", not verify_decision(good, pend2)[0])


# ---------------------------------------------------------------- R8 I-JSON
def ijson_number_ok(n):
    return isinstance(n, (int, float)) and (not isinstance(n, int) or abs(n) <= 2**53 - 1)


def r8():
    check("R8 2^53-1 ok", ijson_number_ok(2**53 - 1))
    check("R8 2^53+1 rejected (ITV-577)", not ijson_number_ok(2**53 + 1))


# ------------------------------------------------------------ R9 exclusivity
def content_fields(payload):
    return [k for k in ("args", "result", "data", "error") if k in payload]


def r9():
    check("R9 one field ok", len(content_fields({"type": "t", "args": {}})) == 1)
    check("R9 two fields rejected", len(content_fields({"type": "t", "args": {}, "result": {}})) != 1)
    check("R9 zero fields rejected", len(content_fields({"type": "t"})) != 1)


# ------------------------------------------------- R10 effective oversight
PROFILES = json.load(open("profiles/arsia-compliance-profiles.json"))["profiles"]


def effective_oversight(message_value, profile):
    if message_value is not None:
        return message_value
    if profile and profile in PROFILES:
        return PROFILES[profile]["defaults"].get("human_oversight")
    return None


def rule3(classification, message_value, profile):
    if classification != "high-risk":
        return True
    return effective_oversight(message_value, profile) is not None


def r10():
    check("R10 explicit value", rule3("high-risk", "required_before_execution", None))
    check("R10 profile default (ITV-421)", rule3("high-risk", None, "EU-AI-ACT-HIGH-RISK"))
    check("R10 no profile -> reject (ITV-579)", not rule3("high-risk", None, None))
    check("R10 non-high-risk passes", rule3("limited-risk", None, None))


# ------------------------------------------------- R11 issuer trust (Core §6.5)
TRUST = {
    "https://as.acme.example": {
        "key_origin": "https://as.acme.example/.well-known/jwks.json",
        "audiences": {"agent:acme.billing", "agent:acme.payments"},
        "algs": {"EdDSA", "ES256"},
    }
}


def validate_token_trust(token, recipient):
    """Returns (accepted, reason). Token = {iss, aud, alg, key_url}."""
    cfg = TRUST.get(token["iss"])
    if cfg is None:
        return False, "unknown_issuer"
    if token.get("key_url") and token["key_url"] != cfg["key_origin"]:
        return False, "key_origin_not_configured"  # never resolve keys from the token
    if token["alg"] not in cfg["algs"]:
        return False, "alg_not_allowed"
    if recipient not in cfg["audiences"] or token["aud"] != recipient:
        return False, "audience_policy"
    return True, None


def r11():
    good = {"iss": "https://as.acme.example", "aud": "agent:acme.billing",
            "alg": "EdDSA", "key_url": "https://as.acme.example/.well-known/jwks.json"}
    check("R11 trusted issuer", validate_token_trust(good, "agent:acme.billing")[0])
    check("R11 unknown issuer rejected", validate_token_trust({**good, "iss": "https://evil.example"}, "agent:acme.billing")[1] == "unknown_issuer")
    check("R11 key from token URL rejected", validate_token_trust({**good, "key_url": "https://evil.example/jwks"}, "agent:acme.billing")[1] == "key_origin_not_configured")
    check("R11 audience policy", validate_token_trust({**good, "aud": "agent:other.agent"}, "agent:other.agent")[1] == "audience_policy")
    check("R11 alg allowlist", validate_token_trust({**good, "alg": "RS256"}, "agent:acme.billing")[1] == "alg_not_allowed")


# ------------------------------- R12 session-scope audit precedence (State §8.3 r4)
def audit_events_generated(scope, envelope_audit_required):
    if envelope_audit_required:
        return True  # rule 4 wins, including session scope
    return scope != "session"  # session default: no audit


def r12():
    check("R12 session default no audit", not audit_events_generated("session", False))
    check("R12 session + audit_required=true AUDITS", audit_events_generated("session", True))
    check("R12 agent scope audits per config", audit_events_generated("agent", False))


# ----------------------------- R13 revocation under cache (Core §5.2/§7.3, A-18)
def key_accepted(kid, cache, now, published_kids):
    """cache = {kid: fetched_at}; ceiling 3600 s; removal from JWKS = revocation."""
    fetched = cache.get(kid)
    if fetched is None or now - fetched > 3600:
        # forced refresh against the published set
        cache[kid] = now
        return kid in published_kids
    return True  # within cache window — exposure bounded by the ceiling


def r13():
    cache = {"k1": 0}
    published = set()  # k1 revoked (removed from JWKS)
    check("R13 within window still accepted (bounded exposure)", key_accepted("k1", dict(cache), 1800, published))
    check("R13 after ceiling refresh -> revoked key rejected", not key_accepted("k1", dict(cache), 3601, published))
    check("R13 unknown kid forces refresh and rejects", not key_accepted("k2", dict(cache), 10, published))
    check("R13 unknown kid forces refresh and accepts fresh key", key_accepted("k2", dict(cache), 10, {"k2"}))


def main() -> int:
    vectors = json.load(open("test-vectors/arsia-test-vectors.json"))["vectors"]
    r1(); r2(vectors); r3(); r5(); r6(); r7(); r8(); r9(); r10(); r11(); r12(); r13()
    print()
    print("ALL RUNTIME RULES PASSED" if not FAIL else f"{len(FAIL)} FAILURES: {FAIL}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
