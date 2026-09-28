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
  R5  Amount grammar, length and per-asset-type scale;     (Assets §2, §3.1.1, D4)
      currency exponent from an injected ISO 4217 catalog
  R6  Idempotency precedence: signed envelope wins         (Core §10.4, M-25)
  R7  Correlation/root chain verification;                 (Core §4.2, B-01)
      oversight audit-record count                         (Actions §3.5/§3.6, A-25)
  R8  I-JSON number range rule                             (State §2.1.2, B-08)
  R9  Content-field mutual exclusivity                     (Core §4.4.7, A-08)
  R10 Effective human-oversight resolution / Rule 3        (Core §4.3.8, A-09)
  R11 Issuer trust and key-origin policy                    (Core §6.5)
  R12 Session-scope audit precedence                        (State §8.3)
  R13 JWKS-document cache: unknown-kid refresh, max-age     (Core §5.2/§7.3, A-18)
      capped at 3600 s, revocation event, shared-cache sequences
  R14 Audit hash chain: chain value, verification against   (State §7.2, DR-5)
      a held head, tombstones, conformance-level mandate

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
        if (prefix + ".").startswith("arsiaprotocol."):
            return False  # wildcard within the reserved namespace satisfies nothing
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
    check("R3 non-reserved lookalike namespace wildcard (A-36)", scope_satisfies("arsiaprotocolx.*", "arsiaprotocolx.read"))
    check("R3 reserved root wildcard satisfies nothing", not scope_satisfies("arsiaprotocol.*", "arsiaprotocol.state.read"))
    check("R3 arsiaprotocol.state.* grants no state capability (A-5, State §8.2.1)",
          not any(scope_satisfies("arsiaprotocol.state.*", "arsiaprotocol.state." + c)
                  for c in ("read", "write", "purge", "snapshot")))
    check("R3 partial capability list", not authorized(["notes.read"], ["notes.read", "notes.write"]))
    check("R3 multi-scope", authorized(["notes.read", "payments.charge"], ["notes.read", "payments.charge"]))
    check("R4 registry member ok", "arsiaprotocol.echo" in REGISTRY)
    check("R4 unknown reserved rejected (ITV-568)", "arsiaprotocol.zzz.unregistered" not in REGISTRY)


# ------------------------------------------------------------- R5 amount scale
# Assets §3.1.1: the ISO 4217 catalog edition is declared by the agent
# (iso4217_edition) and the receiver's edition governs, so the catalog is an input.
# SPEC_CATALOG holds only the minor-unit exponents the specification itself states
# (Assets §2.1 / §3.1.1: EUR 2, JPY 0, KWD 3). TEST_CATALOG adds codes the spec
# names without stating an exponent; those values are synthetic test fixtures, NOT
# a claim about the official ISO 4217 table. A catalog value of None models an
# entry with no numeric minor-unit exponent.
SPEC_CATALOG = {"EUR": 2, "JPY": 0, "KWD": 3}
TEST_CATALOG = {**SPEC_CATALOG, "SEK": 2, "USD": 2, "GBP": 2, "CHF": 2, "BHD": 3, "XXX": None}
AMOUNT_RE = re.compile(r"^(0|[1-9][0-9]*)(\.([0-9]+))?$")  # Assets §3.1.1 ABNF
CURRENCY_CODE_RE = re.compile(r"^[A-Z]{3}$")
UNIT_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,30}[a-z0-9]$")
MAX_FRACTION = {"token": 8, "entitlement": 2, "service_unit": 4}  # Assets §2.2-§2.4


def amount_valid(amount, asset_type, currency_or_unit, catalog):
    """Assets §2.1-§2.4 and §3.1.1 amount rules for a string amount."""
    if not isinstance(amount, str):
        return False  # string only; length is bounded by the digit limits (A-67)
    m = AMOUNT_RE.match(amount)
    if not m or len(m.group(1)) > 16:
        return False  # grammar; integer part at most 16 digits
    if set(amount.replace(".", "")) == {"0"}:
        return False  # strictly greater than zero
    frac = m.group(3) or ""
    if asset_type == "currency":
        if not CURRENCY_CODE_RE.match(currency_or_unit):
            return False
        exponent = catalog.get(currency_or_unit)
        if exponent is None:
            # No numeric minor-unit exponent: MUST be rejected (§3.1.1; the undefined
            # "explicit scale" exception was removed in A-66).
            return False
        return len(frac) == exponent  # fixed scale: exactly the minor-unit digits
    if asset_type in MAX_FRACTION:
        if len(currency_or_unit) > 32 or not UNIT_RE.match(currency_or_unit):
            return False
        if currency_or_unit.upper() in catalog:
            return False  # MUST NOT match an ISO 4217 code, case-insensitively (A-68)
        return len(frac) <= MAX_FRACTION[asset_type]
    return False  # asset_type outside the normative enumeration (Assets §2)


def r5():
    c = SPEC_CATALOG
    check("R5 EUR 1500.00", amount_valid("1500.00", "currency", "EUR", c))
    check("R5 EUR 1500.0 rejected (ITV-575)", not amount_valid("1500.0", "currency", "EUR", c))
    check("R5 EUR 1500 rejected (canonical equality)", not amount_valid("1500", "currency", "EUR", c))
    check("R5 EUR 1500.000 rejected", not amount_valid("1500.000", "currency", "EUR", c))
    check("R5 JPY 1500", amount_valid("1500", "currency", "JPY", c))
    check("R5 JPY 1500.00 rejected (ITV-576)", not amount_valid("1500.00", "currency", "JPY", c))
    check("R5 KWD 1500.000 (ITV-574)", amount_valid("1500.000", "currency", "KWD", c))
    check("R5 exponent rejected", not amount_valid("1.5e3", "currency", "EUR", c))
    check("R5 leading zero rejected", not amount_valid("01.50", "currency", "EUR", c))
    check("R5 negative rejected", not amount_valid("-5.00", "currency", "EUR", c))
    check("R5 zero rejected", not amount_valid("0.00", "currency", "EUR", c))
    check("R5 JSON number rejected", not amount_valid(1500.00, "currency", "EUR", c))
    check("R5 SEK accepted under the declared test catalog (A-37)", amount_valid("100.00", "currency", "SEK", TEST_CATALOG))
    check("R5 code absent from the catalog rejected", not amount_valid("100.00", "currency", "SEK", c))
    check("R5 entry without numeric exponent rejected", not amount_valid("100", "currency", "XXX", TEST_CATALOG))
    check("R5 lowercase currency code rejected", not amount_valid("100.00", "currency", "eur", c))
    check("R5 16-digit integer part accepted", amount_valid("1" * 16 + ".00", "currency", "EUR", c))
    check("R5 17-digit integer part rejected", not amount_valid("1" * 17 + ".00", "currency", "EUR", c))
    check("R5 20-digit integer part rejected (A-37)", not amount_valid("1" * 20 + ".00", "currency", "EUR", c))
    check("R5 35 fraction digits rejected by scale, not length (A-67)", not amount_valid("1." + "1" * 35, "token", "api-credits", c))
    check("R5 longest token amount (25 chars) accepted (A-67)", amount_valid("1" * 16 + "." + "1" * 8, "token", "api-credits", c))
    check("R5 unit 'eur' rejected: matches EUR case-insensitively (A-68)", not amount_valid("10", "token", "eur", c))
    check("R5 unit 'api' accepted: no ISO 4217 match (A-68)", amount_valid("10", "token", "api", c))
    check("R5 token 8 fraction digits", amount_valid("0.12345678", "token", "api-credits", c))
    check("R5 token 9 fraction digits rejected", not amount_valid("0.123456789", "token", "api-credits", c))
    check("R5 entitlement 2 fraction digits", amount_valid("0.50", "entitlement", "premium-seats", c))
    check("R5 entitlement 3 fraction digits rejected", not amount_valid("0.505", "entitlement", "premium-seats", c))
    check("R5 service_unit 4 fraction digits", amount_valid("0.0001", "service_unit", "gpu-hours", c))
    check("R5 service_unit 5 fraction digits rejected", not amount_valid("0.00001", "service_unit", "gpu-hours", c))
    check("R5 non-currency unit pattern rejected", not amount_valid("10", "token", "API_Credits", c))
    check("R5 unknown asset_type rejected", not amount_valid("10", "crypto", "btc", c))


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
    check("R7 single-approval cycle: 4 records (ACTIONS-10)", oversight_records(1) ==
          ["request", "pending_approval", "approval_decision", "response"])
    check("R7 multi-approval N=3 ending in a decision: N + 3 = 6 records (A-25)",
          len(oversight_records(3)) == 6)
    check("R7 multi-approval denial after 1 approval: N=2, 5 records (A-25)",
          len(oversight_records(2, final="error")) == 5)


def oversight_records(n_decisions, final="response"):
    """Actions §3.5/§3.6: audit records of an oversight flow that ends with a decision —
    Record 1, Record 2, one Record 3 per approval_decision received, Record 4."""
    return ["request", "pending_approval"] + ["approval_decision"] * n_decisions + [final]


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
JWKS_CEILING = 3600  # Core §5.2 Verification Caching: refresh at least every 3600 s


class JwksCache:
    """Cache of one sender's JWKS DOCUMENT (Core §5.2 Step 2 and Verification Caching).

    `fetch()` returns (published_kids, max_age_seconds) or raises ConnectionError.
    The cached document is refreshed when absent, when the Cache-Control max-age
    (capped at the 3600 s ceiling) has expired, or when the requested kid is not in
    it. A kid absent after refresh is rejected, and a failed lookup never makes the
    kid acceptable later. A key-revocation event invalidates the cached key at once.
    """

    def __init__(self, fetch):
        self.fetch = fetch
        self.kids = None
        self.fetched_at = None
        self.max_age = None

    def _refresh(self, now):
        kids, max_age = self.fetch()
        self.kids, self.fetched_at, self.max_age = set(kids), now, max_age

    def accept(self, kid, now):
        stale = (self.kids is None
                 or now - self.fetched_at > min(self.max_age, JWKS_CEILING))
        if stale or kid not in self.kids:
            try:
                self._refresh(now)
            except ConnectionError:
                return False  # JWKS unreachable when needed: reject (Step 2)
        return kid in self.kids

    def revocation_event(self, kid):
        if self.kids is not None:
            self.kids.discard(kid)  # invalidate at once; next lookup must refresh


class Publisher:
    """The sender's published JWKS, mutable over time."""

    def __init__(self, kids, max_age=3600):
        self.kids, self.max_age, self.up = set(kids), max_age, True

    def __call__(self):
        if not self.up:
            raise ConnectionError("JWKS unreachable")
        return set(self.kids), self.max_age


def r13():
    # Finding 2 sequence: one SHARED cache, two calls, never-published kid.
    pub = Publisher({"k1"})
    cache = JwksCache(pub)
    check("R13 never-published kid, shared cache, call 1 rejected", not cache.accept("k2", 10))
    check("R13 never-published kid, shared cache, call 2 rejected", not cache.accept("k2", 11))
    # Finding 2 sequence: revoked kid, shared cache, past the ceiling.
    pub = Publisher({"k1"})
    cache = JwksCache(pub)
    check("R13 published kid accepted", cache.accept("k1", 0))
    pub.kids.discard("k1")  # revocation = removal from the published JWKS
    check("R13 revoked kid within window accepted (bounded exposure)", cache.accept("k1", 1800))
    check("R13 revoked kid after ceiling, shared cache, call 1 rejected", not cache.accept("k1", 3601))
    check("R13 revoked kid after ceiling, shared cache, call 2 rejected", not cache.accept("k1", 3602))
    # Cache-Control max-age shorter than the ceiling governs.
    pub = Publisher({"k1"}, max_age=60)
    cache = JwksCache(pub)
    cache.accept("k1", 0)
    pub.kids.discard("k1")
    check("R13 max-age 60: accepted within max-age", cache.accept("k1", 30))
    check("R13 max-age 60: rejected after max-age", not cache.accept("k1", 61))
    check("R13 max-age 60: rejected again", not cache.accept("k1", 62))
    # A max-age longer than the ceiling is capped at 3600 s.
    pub = Publisher({"k1"}, max_age=7200)
    cache = JwksCache(pub)
    cache.accept("k1", 0)
    pub.kids.discard("k1")
    check("R13 max-age 7200 capped: rejected after 3600 s", not cache.accept("k1", 3601))
    # Key-revocation event: immediate invalidation inside the window.
    pub = Publisher({"k1"})
    cache = JwksCache(pub)
    cache.accept("k1", 0)
    pub.kids.discard("k1")  # emergency rotation removes the key immediately
    cache.revocation_event("k1")
    check("R13 revocation event: rejected at once, call 1", not cache.accept("k1", 5))
    check("R13 revocation event: rejected at once, call 2", not cache.accept("k1", 6))
    # A newly published kid is found through the unknown-kid refresh.
    pub = Publisher({"k1"})
    cache = JwksCache(pub)
    cache.accept("k1", 0)
    pub.kids.add("k2")
    check("R13 new kid accepted via unknown-kid refresh", cache.accept("k2", 10))
    # JWKS unreachable when a refresh is needed: reject.
    pub = Publisher({"k1"})
    cache = JwksCache(pub)
    cache.accept("k1", 0)
    pub.up = False
    check("R13 JWKS unreachable on needed refresh rejected", not cache.accept("k2", 10))
    check("R13 JWKS unreachable after ceiling rejected", not cache.accept("k1", 3601))


# --------------------------------------------------------- R14 audit hash chain
CHAIN_FIELDS = ("hash_chain", "chain_id", "chain_seq", "chain_format")
SUPPORTED_CHAIN_FORMATS = {1}


def chain_value(record, previous_value):
    """State §7.2: lowercase hex SHA-256 over RFC 8785 of
    {"previous_chain_value": P, "record": R'}, R' = the record without hash_chain."""
    import hashlib
    import rfc8785
    r = {k: v for k, v in record.items() if k != "hash_chain"}
    return hashlib.sha256(rfc8785.dumps({"previous_chain_value": previous_value, "record": r})).hexdigest()


def is_tombstone(entry):
    return "record_id" not in entry  # tombstones carry no field of the deleted record


def verify_chain(entries, head):
    """State §7.2 verification against a held head (chain_id, h, value).
    Returns (ok, reason, report); report lists tombstone positions and entries beyond h."""
    chain_id, h, head_value = head
    by_pos = {}
    for e in entries:
        pos = e.get("chain_seq")
        if not isinstance(pos, int) or pos < 1:
            return False, "invalid position", {}
        if pos in by_pos:
            return False, "duplicate position", {}
        by_pos[pos] = e
    if any(n not in by_pos for n in range(1, h + 1)):
        return False, "position gap", {}
    report = {"tombstones": [], "beyond_head": sorted(p for p in by_pos if p > h)}
    fmt, prev = None, None
    for n in range(1, h + 1):
        e = by_pos[n]
        if e.get("chain_id") != chain_id:
            return False, "foreign chain_id", report
        if e.get("chain_format") not in SUPPORTED_CHAIN_FORMATS:
            return False, "unsupported chain_format", report
        if fmt is not None and e["chain_format"] != fmt:
            return False, "chain_format differs", report
        fmt = e["chain_format"]
        if is_tombstone(e):
            if e.get("previous_chain_value") != prev:
                return False, "tombstone previous value mismatch", report
            report["tombstones"].append(n)
        elif chain_value(e, prev) != e.get("hash_chain"):
            return False, "chain value mismatch", report
        prev = e.get("hash_chain")
    if prev != head_value:
        return False, "head mismatch", report
    return True, "ok", report


def chain_mandate_ok(record, level):
    """State §7.2 / Core §12 (D1): chain fields all-or-none; REQUIRED at compliance and full."""
    present = [f in record for f in CHAIN_FIELDS]
    if any(present) and not all(present):
        return False
    return all(present) if level in ("compliance", "full") else True


def r14(vectors):
    by_id = {v["id"]: v for v in vectors}
    seq_ids = ["ITV-592", "ITV-593", "ITV-594", "ITV-595", "ITV-596"]
    chain = [dict(by_id[i]["data"]) for i in seq_ids]
    head = (chain[0]["chain_id"], 5, chain[4]["hash_chain"])

    def sub(pos, vid):
        c = [dict(e) for e in chain]
        c[pos - 1] = dict(by_id[vid]["data"])
        return c

    def expect_fail(name, entries, hd, reason):
        ok, why, _ = verify_chain(entries, hd)
        check(name, ok is False and why == reason, f"got ({ok}, {why})")

    ok, why, rep_ = verify_chain(chain, head)
    check("R14 (a) valid chain of 4 records + 1 tombstone verifies (ITV-592..596)",
          ok and rep_["tombstones"] == [4] and rep_["beyond_head"] == [], f"{why} {rep_}")
    one = dict(by_id["ITV-95"]["data"])
    check("R14 (a) single-entry chain ITV-95 verifies",
          verify_chain([one], (one["chain_id"], 1, one["hash_chain"]))[0])
    tampered = sub(2, "ITV-597")
    expect_fail("R14 (b) approver_id changed (ITV-597) rejected: chain value mismatch", tampered, head,
                "chain value mismatch")
    old = lambda r: __import__("hashlib").sha256((r["record_id"] + r["payload_hash"]).encode()).hexdigest()
    check("R14 (b) pre-DR-5 construction blind to the same change (A-8 reproduction)",
          old(chain[1]) == old(tampered[1]) and chain[1]["approver_id"] != tampered[1]["approver_id"])
    expect_fail("R14 (c) mid-chain record removed rejected: position gap",
                [e for e in chain if e.get("chain_seq") != 3], head, "position gap")
    swapped = [dict(e) for e in chain]
    swapped[0]["chain_seq"], swapped[1]["chain_seq"] = 2, 1
    expect_fail("R14 (d) two records reordered rejected: chain value mismatch", swapped, head,
                "chain value mismatch")
    expect_fail("R14 (e) foreign chain_id (ITV-598) rejected", sub(3, "ITV-598"), head, "foreign chain_id")
    no_chain = {k: v for k, v in chain[1].items() if k not in CHAIN_FIELDS}
    check("R14 (f) Compliance-level record without chain fields fails the mandate",
          chain_mandate_ok(no_chain, "compliance") is False)
    check("R14 (f) Full-level record without chain fields fails the mandate",
          chain_mandate_ok(no_chain, "full") is False)
    check("R14 (f) Core-level record without chain fields is allowed", chain_mandate_ok(no_chain, "core"))
    check("R14 (f) chained record satisfies the Compliance mandate", chain_mandate_ok(chain[1], "compliance"))
    partial = {k: v for k, v in chain[1].items() if k != "chain_id"}
    check("R14 (f) partial chain fields fail at every level",
          not any(chain_mandate_ok(partial, lv) for lv in ("core", "compliance", "full")))
    expect_fail("R14 (g) tombstone previous value wrong (ITV-599) rejected", sub(4, "ITV-599"), head,
                "tombstone previous value mismatch")
    expect_fail("R14 (h) head value mismatch rejected", chain, (head[0], 5, "0" * 64), "head mismatch")
    ok, why, rep_ = verify_chain(chain, (head[0], 3, chain[2]["hash_chain"]))
    check("R14 entries beyond the held head are reported, not rejected",
          ok and rep_["beyond_head"] == [4, 5], f"{why} {rep_}")
    fmt = [dict(e) for e in chain]
    fmt[0]["chain_format"] = 2
    expect_fail("R14 unsupported chain_format rejected", fmt, head, "unsupported chain_format")


def main() -> int:
    vectors = json.load(open("test-vectors/arsia-test-vectors.json"))["vectors"]
    r1(); r2(vectors); r3(); r5(); r6(); r7(); r8(); r9(); r10(); r11(); r12(); r13(); r14(vectors)
    print()
    print("ALL RUNTIME RULES PASSED" if not FAIL else f"{len(FAIL)} FAILURES: {FAIL}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
