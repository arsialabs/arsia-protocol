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
  R10 Effective obligation resolution: fill, collect,      (Core §4.3.10, DR-3/DR-4)
      compose, evaluate, record; Rule 3; receiver and router
      simulations; authenticated context (Identity §7)
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


# ------------------------------------------- R10 effective obligation resolution
PROFILES = json.load(open("profiles/arsia-compliance-profiles.json"))["profiles"]
OBLIGATION_RULES = json.load(open("profiles/arsia-obligation-rules.json"))
AXES = ("oversight", "audit", "explainability", "retention", "residency")
SUBFIELD = {"oversight": "human_oversight", "audit": "audit_required", "explainability": "explainability_required",
            "retention": "retention", "residency": "data_residency"}
# Core §4.3.10.6: §4.3.8 rule order, generic diagnostic last
DIAGNOSTIC_ORDER = ["unknown_profile", "missing_legal_basis", "high_risk_missing_oversight", "insufficient_retention",
                    "classification_escalation", "sensitive_requires_art9_basis", "obligation_conflict"]
CLASS_ORDER = ["minimal-risk", "limited-risk", "high-risk", "unacceptable-risk"]
ART9_BASES = {"explicit_consent", "employment_social_security", "vital_interests_incapacity", "legitimate_activities",
              "manifestly_public", "legal_claims", "substantial_public_interest", "health_medicine", "public_health",
              "archiving_research"}
# Routing §5.2 member list, revision 2026-03
EU_REVISION = "2026-03"
EU_MEMBERS = sorted("AT BE BG CY CZ DE DK EE ES FI FR GR HR HU IE IS IT LI LT LU LV MT NL NO PL PT RO SE SI SK".split())
PLATFORM_DEFAULT_RETENTION = "P90D"  # State §7.3


def jcs_sha256(obj):
    import hashlib
    import rfc8785
    return hashlib.sha256(rfc8785.dumps(obj)).hexdigest()


def rule_source(rule):
    return {"class": "protocol-rule", "id": rule["id"], "sha256": jcs_sha256(rule)}


def floor_source(profile):
    return {"class": "profile-floor", "id": profile, "sha256": jcs_sha256(PROFILES[profile])}


def normalize_residency(code):
    """Core §4.3.10.5: a regional code expands to its member list; returns (codes, expanded)."""
    return (set(EU_MEMBERS), True) if code == "EU" else ({code}, False)


def conflict(diagnostic, axis, declared, required, sources, field=None):
    c = {"diagnostic": diagnostic, "axis": axis, "declared": declared, "required": required, "sources": sources}
    if field:
        c["field"] = field
    return c


def resolve_obligations(intent, compliance, identity=None, anchor="2026-10-31T00:00:00.000Z", strict=False,
                        executor=(), sensitive_entry=False):
    """Core §4.3.10 reference: fill, collect, compose, evaluate, record.

    compliance is the envelope's `compliance` object, or None when the field is absent. identity is the
    authenticated IdentityRecord fact {agent_id, ai_system_classification, evidence} or None. executor
    holds executor-class requirements for resolver-contract tests only (not integrated, Core §4.3.10.2).
    Returns the State §7.1 `obligation_resolution` object."""
    conflicts = []
    # ---- fill: profile (Core §4.3.7)
    if compliance is None:
        declared_profile, applied = "none", "none"
    else:
        declared_profile = compliance.get("profile")
        applied = declared_profile if declared_profile in PROFILES else "GDPR-STANDARD"
        if declared_profile is not None and declared_profile not in PROFILES and strict:
            conflicts.append(conflict("unknown_profile", None, declared_profile, sorted(PROFILES), [], "profile"))
    defaults = PROFILES[applied]["defaults"] if applied != "none" else {}
    default_source = "profile-default" if declared_profile in PROFILES else "no-profile-default"

    def fill(axis):
        sub = SUBFIELD[axis]
        if compliance is not None and sub in compliance:
            return {"present": True, "value": compliance[sub]}, {"value": compliance[sub], "source": "message"}
        key = "retention_minimum" if axis == "retention" else sub
        if compliance is None or key not in defaults:
            return {"present": False}, None
        return {"present": False}, {"value": defaults[key], "source": default_source}

    def effective(sub):
        if compliance is None:
            return None
        return compliance[sub] if sub in compliance else defaults.get(sub)

    # ---- collect: identity facts (identity-record source)
    declared_class = compliance.get("ai_system_classification") if compliance else None
    id_class = identity["ai_system_classification"] if identity else None
    facts = []
    if identity:
        facts.append({"fact": "ai_system_classification", "value": id_class, "declared": declared_class,
                      "evidence": identity["evidence"]})
        if declared_class and CLASS_ORDER.index(declared_class) > CLASS_ORDER.index(id_class):
            conflicts.append(conflict("classification_escalation", None, declared_class, id_class, [],
                                      "ai_system_classification"))
    pii = effective("pii_involved") is True
    legal_basis = effective("legal_basis")
    if pii and not legal_basis:
        conflicts.append(conflict("missing_legal_basis", None, None, "legal_basis", [], "legal_basis"))
    if sensitive_entry and legal_basis not in ART9_BASES:
        conflicts.append(conflict("sensitive_requires_art9_basis", None, legal_basis, sorted(ART9_BASES), [],
                                  "legal_basis"))

    # ---- collect: obligation rules (protocol-rule and profile-floor sources)
    reqs = {a: [] for a in AXES}
    for rule in OBLIGATION_RULES["rules"]:
        intents = rule["scope"]["intents"]
        if intents != "all" and intent not in intents:
            continue
        trig, fact_index = rule["trigger"], None
        if "fact" in trig:
            if "identity-record" in trig["from"] and id_class == trig["equals"]:
                fact_index = 0
            elif not ("message-declaration" in trig["from"] and declared_class == trig["equals"]):
                continue
        elif "field" in trig:
            if (effective(trig["field"]) is True) != trig["equals"]:
                continue
        elif "profile_member" in trig:
            if not defaults.get(trig["profile_member"]):
                continue
        for rq in rule["requirements"]:
            item = {"kind": rq["kind"], "source": rule_source(rule), "fact": fact_index}
            if rq["kind"] == "restriction":
                item["excludes"] = rq["excludes"]
            elif rq["kind"] == "value":
                item["value"] = rq["value"]
            else:
                item["minimum"] = defaults["retention_minimum"]
                item["source"] = floor_source(applied)
            reqs[rq["axis"]].append((item, rq.get("diagnostic"),
                                     [e for e in rule["exceptions"] if e["axis"] == rq["axis"]]))
    for ex in executor:
        reqs[ex["axis"]].append(({k: v for k, v in ex.items() if k != "axis"}, None, []))

    axes = {}

    def axis_entry(declared, filled, requirements, result, conflict_item=None, override=False):
        if conflict_item:
            status, result = "conflict", None
        elif not declared["present"] and filled is None and not requirements:
            status, result = "no-value", None
        else:
            status = "resolved"
        return {"status": status, "declared": declared, "fill": filled,
                "requirements": [r[0] for r in requirements], "result": result, "override": override,
                "conflict": conflict_item}

    # ---- compose + evaluate: oversight (set; restrictions on the composed set)
    declared, filled = fill("oversight")
    rq = reqs["oversight"]
    mode = filled["value"] if filled else None
    modes = {mode} if mode and mode != "not_required" else set()
    modes |= {r["value"] for r, _, _ in rq if r["kind"] == "value"}
    demanding = [(r, d) for r, d, _ in rq if r["kind"] == "value" or "not_required" in r.get("excludes", [])]
    c = None
    if declared["present"] and mode == "not_required" and demanding:
        c = conflict(next((d for _, d in demanding if d), "obligation_conflict"), "oversight", "not_required",
                     "oversight other than not_required", [r["source"] for r, _ in demanding])
    else:
        for r, d, _ in rq:
            if r["kind"] == "restriction" and not (modes - set(r["excludes"])):
                c = conflict(d or "obligation_conflict", "oversight", declared.get("value"), {"excludes": r["excludes"]},
                             [r["source"]])
                break
    axes["oversight"] = axis_entry(declared, filled, rq, sorted(modes), c)

    # ---- audit and explainability (unambiguous true replaces a default; audit override per Rule 7)
    for axis in ("audit", "explainability"):
        declared, filled = fill(axis)
        rq = reqs[axis]
        value = filled["value"] if filled else None
        c, override = None, False
        if any(r["kind"] == "value" and r["value"] is True for r, _, _ in rq):
            if declared["present"] and value is False:
                if any(e["effect"] == "override" for _, _, exs in rq for e in exs):
                    value, override = True, True
                else:
                    c = conflict("obligation_conflict", axis, False, True, [r["source"] for r, _, _ in rq])
            else:
                value = True
        axes[axis] = axis_entry(declared, filled, rq, value, c, override)

    # ---- retention (floors on the same object, compared by retained_until from one anchor)
    declared, filled = fill("retention")
    rq = reqs["retention"]
    floors = [r for r, _, _ in rq if r["kind"] == "floor"]
    at = iso(anchor)

    def until(d):
        return add_duration(at, d).strftime("%Y-%m-%dT%H:%M:%S.") + f"{at.microsecond // 1000:03d}Z"

    c, result = None, None
    if declared["present"]:
        short = [r for r in floors if add_duration(at, declared["value"]) < add_duration(at, r["minimum"])]
        if short:
            c = conflict("insufficient_retention", "retention", declared["value"], short[0]["minimum"],
                         [r["source"] for r in short])
        else:
            result = declared["value"]
    elif floors:
        result = max(floors, key=lambda r: add_duration(at, r["minimum"]))["minimum"]
    else:
        filled = {"value": PLATFORM_DEFAULT_RETENTION, "source": "platform-default"}
        result = PLATFORM_DEFAULT_RETENTION
    axes["retention"] = axis_entry(declared, filled, rq, result and {
        "duration": result, "anchor": anchor, "retained_until": until(result)}, c)

    # ---- residency (normalized restrictions intersected; absent = no restriction)
    declared, filled = fill("residency")
    rq = reqs["residency"]
    restrictions, expanded = [], False
    if filled and filled["value"]:
        codes, exp = normalize_residency(filled["value"])
        restrictions.append(codes)
        expanded |= exp
    for r, _, _ in rq:
        if r["kind"] == "restriction" and "allowed" in r:
            restrictions.append(set(r["allowed"]))
    c, result = None, None
    if restrictions:
        allowed = set.intersection(*restrictions)
        if not allowed:
            c = conflict("obligation_conflict", "residency", declared.get("value"), "non-empty intersection",
                         [r["source"] for r, _, _ in rq])
        else:
            result = {"codes": sorted(allowed)}
            if expanded:
                result.update(revision=EU_REVISION, sha256=jcs_sha256(EU_MEMBERS))
    entry = axis_entry(declared, filled, rq, result, c)
    if not restrictions:
        entry.update(status="no-value", result=None)  # State §7.1: no effective restriction is no-value
    axes["residency"] = entry

    # ---- evaluate + record
    conflicts += [a["conflict"] for a in axes.values() if a["conflict"]]
    conflicts.sort(key=lambda c_: DIAGNOSTIC_ORDER.index(c_["diagnostic"]))
    res = {"outcome": "rejected" if conflicts else "accepted",
           "profile": {"declared": declared_profile if compliance is not None else "none", "applied": applied,
                       "source": None if applied == "none" else {"name": applied,
                                                                 "sha256": jcs_sha256(PROFILES[applied])}},
           "facts": facts, "axes": axes}
    if conflicts:
        res["conflicts"] = conflicts
    return res


def legacy_retention(res, anchor):
    """State §7.1: retention fields derived from the resolution; a rejected declaration keeps the
    evidence under the profile minimum and is not applied. anchor is the record's processed_at."""
    ax = res["axes"]["retention"]
    declared = ax["declared"]["value"] if ax["declared"]["present"] else None
    if ax["status"] == "resolved":
        src = {"message": "per-message", "profile-default": "profile-minimum",
               "no-profile-default": "profile-minimum", "platform-default": "platform-default"}[
            ax["fill"]["source"] if not ax["declared"]["present"] else "message"]
        return {"declared_retention": declared, "effective_retention": ax["result"]["duration"],
                "retention_anchor": ax["result"]["anchor"], "retention_source": src}
    if ax["status"] == "conflict":
        minimum = PROFILES[res["profile"]["applied"]]["defaults"]["retention_minimum"]
        return {"declared_retention": declared, "effective_retention": minimum,
                "retention_anchor": anchor, "retention_source": "profile-minimum"}
    return {"declared_retention": declared, "effective_retention": None, "retention_source": "none"}


def error_details(c, res, anchor):
    """Core §4.3.10.6: wire code is always invalid_request; the diagnostic goes in details."""
    if c["diagnostic"] == "insufficient_retention":
        until = lambda d: stamp(add_duration(iso(anchor), d))
        return {"insufficient_retention": True, "profile": res["profile"]["applied"],
                "declared_retention": c["declared"], "minimum_retention": c["required"], "retention_anchor": anchor,
                "declared_retained_until": until(c["declared"]), "minimum_retained_until": until(c["required"]),
                "resolution_source": "per-message"}
    if c["diagnostic"] == "obligation_conflict":
        return {"obligation_conflict": True, "axis": c["axis"], "declared": c["declared"],
                "required": c["required"], "sources": c["sources"]}
    if c["diagnostic"] == "high_risk_missing_oversight":
        return {"high_risk_missing_oversight": True, "declared": c["declared"], "sources": c["sources"]}
    return {c["diagnostic"]: True}


def stamp(at):
    return at.strftime("%Y-%m-%dT%H:%M:%S.") + f"{at.microsecond // 1000:03d}Z"


def payload_hash(message):
    """State §7.1 / Core §5.3.1: SHA-256 of the RFC 8785 payload, or of the JWE string when encrypted."""
    import hashlib
    if message.get("security", {}).get("encrypted"):
        return hashlib.sha256(message["payload"].encode("utf-8")).hexdigest()
    return jcs_sha256(message["payload"])


def record_id_for(message_id, event_type):
    """Deterministic UUID v4 for a simulated record (reproducible runs)."""
    import hashlib
    h = hashlib.sha256(f"{message_id}/{event_type}".encode()).hexdigest()
    return f"{h[:8]}-{h[8:12]}-4{h[13:16]}-{'89ab'[int(h[16], 16) % 4]}{h[17:20]}-{h[20:32]}"


def audit_record(message, res, anchor, operator_id, event_type, **extra):
    """A complete State §7.1 record: identity of the message, payload digest, operator and the
    retention fields derived from the resolution, retained_until = retention_anchor + effective."""
    retention = legacy_retention(res, anchor)
    if retention["effective_retention"] is None:
        raise ValueError("retention axis without value: retained_until undefined")
    payload_type = (message["payload"]["type"] if isinstance(message["payload"], dict)
                    else message["payload_type"])
    return dict({"record_id": record_id_for(message["id"], event_type), "message_id": message["id"],
                 "event_type": event_type, "from_agent": message["from"], "to_agent": message["to"],
                 "intent": message["intent"], "payload_type": payload_type, "payload_hash": payload_hash(message),
                 "processed_at": anchor, "operator_id": operator_id,
                 "compliance_profile_declared": res["profile"]["declared"],
                 "compliance_profile_resolved": res["profile"]["applied"]},
                **extra, **retention,
                retained_until=stamp(add_duration(iso(retention["retention_anchor"]), retention["effective_retention"])))


RECEIVER_OPERATOR = "urn:lei:529900HNOAA1KXQJUQ27"


def receive(message, identity=None, anchor="2026-10-31T00:00:00.000Z", strict=False, executor=(),
            event_type="request", operator_id=RECEIVER_OPERATOR):
    """Receiver simulation: resolve, then emit the audit records State §7.1 requires.
    A compliance rejection always emits its error record, whatever audit_required declares."""
    res = resolve_obligations(message["intent"], message.get("compliance"), identity, anchor, strict, executor)
    if res["outcome"] == "rejected":
        rec = audit_record(message, res, anchor, operator_id, "error", rejection_cause="compliance",
                           correlation_id=message["id"], obligation_resolution=res)
        return {"accepted": False,
                "error": {"code": "invalid_request", "details": error_details(res["conflicts"][0], res, anchor)},
                "records": [rec]}
    records = []
    if res["axes"]["audit"]["result"] is True:
        records.append(audit_record(message, res, anchor, operator_id, event_type, obligation_resolution=res))
        if res["axes"]["audit"]["override"]:
            records.append(audit_record(message, res, anchor, operator_id, "compliance_warning"))
    return {"accepted": True, "error": None, "records": records}


_REGISTRY = []


def schema_errors(instance, schema_file, defs=None):
    """Messages of the errors of instance against schemas/<schema_file> (or its $defs/<defs>)."""
    import glob
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
    if not _REGISTRY:
        docs = [json.load(open(f)) for f in sorted(glob.glob("schemas/*.json"))]
        _REGISTRY.append(Registry().with_resources([(d["$id"], Resource.from_contents(d)) for d in docs if "$id" in d]))
    reg = _REGISTRY[0]
    sid = json.load(open(f"schemas/{schema_file}"))["$id"]
    schema = {"$ref": f"{sid}#/$defs/{defs}"} if defs else {"$ref": sid}
    return [e.message for e in Draft202012Validator(schema, registry=reg).iter_errors(instance)]


# Identity §7.2 Step 7 / §7.6 / §7.7: authenticated context, binding and router
def context_well_formed(ctx):
    return isinstance(ctx, dict) and not schema_errors(ctx, "arsia-onboarding-decision.schema.json",
                                                       "authenticated-context")


def context_digest(ctx):
    return jcs_sha256({k: v for k, v in ctx.items() if k != "context_sha256"})


def prepare_context(context_id, record, signed_body, signature_b64, jwk, verified_at):
    import hashlib
    ctx = {"context_id": context_id, "agent_id": record["agent_id"],
           "ai_system_classification": record["ai_system_classification"],
           "evidence": {"signed_body_sha256": hashlib.sha256(signed_body).hexdigest(), "signature": signature_b64,
                        "jwk": jwk, "verified_at": verified_at, "record_sha256": jcs_sha256(record)}}
    if record.get("valid_until"):
        ctx["valid_until"] = record["valid_until"]
    ctx["context_sha256"] = context_digest(ctx)
    return ctx


def check05(ctx, phase1, now):
    """CHECK-05: the prepared context matches the Phase 1 evidence; no token, no decision.
    phase1 holds what Phase 1 authenticated: record, signed_body, signature and jwk (Step 4).
    The context's members are compared with that evidence, never trusted on their own: a
    context re-hashed after an edit still fails here."""
    import base64
    import hashlib
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    record, body = phase1["record"], phase1["signed_body"]
    if not context_well_formed(ctx):
        return False, "context missing or malformed"
    if context_digest(ctx) != ctx["context_sha256"]:
        return False, "context_sha256 mismatch"
    ev = ctx["evidence"]
    if ctx["agent_id"] != record["agent_id"]:
        return False, "agent_id does not match the record"
    if (ev["signed_body_sha256"] != hashlib.sha256(body).hexdigest() or ev["signature"] != phase1["signature"]
            or ev["jwk"] != phase1["jwk"] or ev["record_sha256"] != jcs_sha256(record)):
        return False, "evidence does not match Phase 1"
    pad = lambda s: s + "=" * (-len(s) % 4)
    try:
        Ed25519PublicKey.from_public_bytes(base64.urlsafe_b64decode(pad(ev["jwk"]["x"]))).verify(
            base64.urlsafe_b64decode(pad(ev["signature"])), hashlib.sha256(body).digest())
    except Exception:
        return False, "signature does not verify"
    if ctx["ai_system_classification"] != record["ai_system_classification"]:
        return False, "classification mismatch"
    if ("valid_until" in ctx) != ("valid_until" in record) or ctx.get("valid_until") != record.get("valid_until"):
        return False, "valid_until does not match the record"
    if record.get("valid_until") and iso(record["valid_until"]) <= iso(now):
        return False, "record expired"
    return True, "ok"


def bind(store, jti, decision_id, ctx, subject, token_exp):
    """§7.6: the gateway records token jti ↔ decision id ↔ context."""
    store[jti] = {"decision_id": decision_id, "context": ctx, "context_sha256": ctx["context_sha256"],
                  "subject": subject, "token_exp": token_exp}


def router_forward(message, jti, store, now, revoked=frozenset()):
    """§7.7: verify the bound context, resolve before forwarding; trace records the order."""
    trace = ["verify-token"]
    b = store.get(jti)
    if b is None or jti in revoked or iso(b["token_exp"]) <= iso(now):
        return {"forwarded": False, "error": "unauthorized", "trace": trace + ["no usable binding"]}
    ctx = b["context"]
    if not context_well_formed(ctx):
        return {"forwarded": False, "error": "unauthorized", "trace": trace + ["context missing or malformed"]}
    if context_digest(ctx) != b["context_sha256"] or ctx["agent_id"] != b["subject"] or ctx["agent_id"] != message["from"]:
        return {"forwarded": False, "error": "unauthorized", "trace": trace + ["context mismatch"]}
    if ctx.get("valid_until") and iso(ctx["valid_until"]) <= iso(now):
        return {"forwarded": False, "error": "unauthorized", "trace": trace + ["context expired"]}
    trace.append("resolve")
    identity = {"agent_id": ctx["agent_id"], "ai_system_classification": ctx["ai_system_classification"],
                "evidence": dict(ctx["evidence"], agent_id=ctx["agent_id"])}
    out = receive(message, identity, now)
    if not out["accepted"]:
        return {"forwarded": False, "error": "invalid_request", "details": out["error"]["details"],
                "records": out["records"], "trace": trace + ["reject"]}
    return {"forwarded": True, "error": None, "records": out["records"], "trace": trace + ["forward"]}


def subset_match(expected, actual, path=""):
    """Every member stated in the expectation equals the computed one; returns mismatching paths."""
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return [path or "/"]
        return [m for k, v in expected.items() for m in subset_match(v, actual.get(k, "<absent>"), f"{path}/{k}")]
    return [] if expected == actual else [path or "/"]


TEST_PAYLOAD = {"type": "com.acme.ledger/post", "args": {"amount": "100.00"}}
TEST_EVIDENCE = {"agent_id": "agent:acme.analyst", "signed_body_sha256": "1" * 64, "signature": "c2ln",
                 "jwk": {"kty": "OKP", "crv": "Ed25519", "x": "eA"}, "verified_at": "2026-10-30T09:00:00.000Z",
                 "record_sha256": "2" * 64}


def scenario_result(meta):
    """Runs a runtime vector's test_metadata scenario and returns the computed result object."""
    inp = meta["input"]
    if meta["scenario"] == "resolution":
        identity = None
        if inp.get("identity"):
            identity = dict(inp["identity"], evidence=dict(TEST_EVIDENCE, agent_id=inp["identity"]["agent_id"]))
        msg = {"id": inp.get("id", "00000000-0000-4000-8000-000000000000"), "from": inp.get("from", "agent:acme.analyst"),
               "to": "agent:acme.executor", "intent": inp["intent"], "payload": TEST_PAYLOAD}
        if inp.get("compliance") is not None:
            msg["compliance"] = inp["compliance"]
        out = receive(msg, identity, inp.get("anchor", "2026-10-31T00:00:00.000Z"), inp.get("strict", False),
                      inp.get("executor", ()))
        res = out["records"][0]["obligation_resolution"] if out["records"] else resolve_obligations(
            msg["intent"], msg.get("compliance"), identity, executor=inp.get("executor", ()))
        return {"outcome": res["outcome"], "error": out["error"], "profile": res["profile"], "axes": res["axes"],
                "facts": [{"value": f["value"], "declared": f["declared"]} for f in res["facts"]],
                "conflicts": res.get("conflicts", []),
                "records": [{k: r[k] for k in ("event_type", "rejection_cause", "correlation_id", "declared_retention",
                                               "effective_retention", "retention_source") if k in r}
                            for r in out["records"]],
                "emitted": out["records"]}
    if meta["scenario"] == "router":
        return router_case(inp)
    raise ValueError(meta["scenario"])


ROUTER_KEY_SEED = bytes(range(32))


def router_case(inp):
    """Builds a signed IdentityRecord, prepares/checks/binds a context, then routes a request."""
    import base64
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    import hashlib
    key = Ed25519PrivateKey.from_private_bytes(ROUTER_KEY_SEED)
    x = base64.urlsafe_b64encode(key.public_key().public_bytes(serialization.Encoding.Raw,
                                                               serialization.PublicFormat.Raw)).decode().rstrip("=")
    record = dict(inp["record"])
    body = json.dumps(record, sort_keys=True).encode()
    sig = base64.urlsafe_b64encode(key.sign(hashlib.sha256(body).digest())).decode().rstrip("=")
    jwk = {"kty": "OKP", "crv": "Ed25519", "x": x}
    ctx = prepare_context("3f2b8c1d-4e5f-4a6b-9c7d-8e9f0a1b2c3d", record, body, sig, jwk, "2026-10-30T09:00:00.000Z")
    edit = inp.get("context_edit")
    if edit:  # an edited context, re-hashed so that only the comparison with Phase 1 can catch it
        for k in edit.get("drop", []):
            ctx.pop(k)
        for k, v in edit.get("set", {}).items():
            (ctx["evidence"] if k in ctx["evidence"] else ctx)[k] = v
        ctx["context_sha256"] = context_digest(ctx)
    ok05, why05 = check05(ctx, {"record": record, "signed_body": body, "signature": sig, "jwk": jwk},
                          inp.get("check_at", "2026-10-30T09:00:00.000Z"))
    store = {}
    if inp.get("bind", True) and ok05:  # Phase 5 admits only after Phase 2 passed
        bind(store, "jti-1", "9f1d2c3b-4a5e-4f60-8b7c-1d2e3f405060", ctx, record["agent_id"],
             inp.get("token_exp", "2026-11-30T00:00:00.000Z"))
    if inp.get("tamper") == "foreign-context":
        other = dict(record, agent_id="agent:other.agent")
        store["jti-1"]["context"] = prepare_context("4a3b2c1d-5e6f-4a7b-8c9d-0e1f2a3b4c5d", other, body, sig,
                                                    ctx["evidence"]["jwk"], "2026-10-30T09:00:00.000Z")
    if inp.get("tamper") == "foreign-admission":
        store["jti-1"]["context"] = dict(ctx, context_id="4a3b2c1d-5e6f-4a7b-8c9d-0e1f2a3b4c5d")
    if inp.get("tamper") == "context-null":
        store["jti-1"]["context"] = None
    if inp.get("tamper") == "context-malformed":
        store["jti-1"]["context"] = {k: v for k, v in ctx.items() if k != "evidence"}
    msg = {"id": "00000000-0000-4000-8000-000000000001", "from": inp["message"].get("from", record["agent_id"]),
           "to": "agent:corp.internal", "intent": "request", "payload": TEST_PAYLOAD}
    if inp["message"].get("compliance") is not None:
        msg["compliance"] = inp["message"]["compliance"]
    out = router_forward(msg, "jti-1", store, inp.get("now", "2026-10-31T00:00:00.000Z"))
    return {"check05": ok05, "check05_reason": why05, "forwarded": out["forwarded"], "error": out["error"],
            "trace": out["trace"], "details": out.get("details"), "emitted": out.get("records", [])}


def r10(vectors):
    hr = {"agent_id": "agent:acme.analyst", "ai_system_classification": "high-risk", "evidence": TEST_EVIDENCE}
    req = lambda comp: resolve_obligations("request", comp, hr)
    check("R10 high-risk + MIFID-II, no mode declared: default counts (A-23)",
          req({"profile": "MIFID-II"})["outcome"] == "accepted"
          and req({"profile": "MIFID-II"})["axes"]["oversight"]["result"] == ["required_before_execution"])
    for label, comp in (("absent compliance", None), ("absent profile", {}), ("explicit GDPR-STANDARD", {"profile": "GDPR-STANDARD"})):
        r = req(comp)
        check(f"R10 A-32 {label}: rejected high_risk_missing_oversight",
              r["outcome"] == "rejected" and r["conflicts"][0]["diagnostic"] == "high_risk_missing_oversight")
    check("R10 A-32 provenance keeps the fill difference (no-profile-default vs profile-default)",
          req({})["axes"]["audit"]["fill"]["source"] == "no-profile-default"
          and req({"profile": "GDPR-STANDARD"})["axes"]["audit"]["fill"]["source"] == "profile-default"
          and req(None)["axes"]["audit"]["fill"] is None)
    r = req({"profile": "MIFID-II", "human_oversight": "not_required"})
    check("R10 explicit not_required + high risk -> high_risk_missing_oversight",
          r["conflicts"][0]["diagnostic"] == "high_risk_missing_oversight")
    r = resolve_obligations("request", {"profile": "MIFID-II", "human_oversight": "required_post_execution"}, hr,
                            executor=[{"axis": "oversight", "kind": "value", "value": "required_before_execution",
                                       "source": {"class": "executor-policy", "id": "descriptor", "sha256": "3" * 64}}])
    check("R10 resolver contract: declared post + demanded prior -> {prior, post}",
          r["outcome"] == "accepted" and r["axes"]["oversight"]["result"] == ["required_before_execution", "required_post_execution"])
    r = req({"profile": "MIFID-II", "human_oversight": "required_within_24h"})
    check("R10 MIFID-II default replaced by required_within_24h (no prior-approval requirement)",
          r["outcome"] == "accepted" and r["axes"]["oversight"]["result"] == ["required_within_24h"])
    r = req({"profile": "GDPR-STANDARD", "human_oversight": "required_within_24h", "ai_system_classification": "minimal-risk"})
    check("R10 declared downgrade does not dispense (set still applies)",
          r["axes"]["explainability"]["result"] is True and r["axes"]["explainability"]["requirements"])
    r = req({"profile": "GDPR-STANDARD", "human_oversight": "required_within_24h", "audit_required": False})
    check("R10 explicit audit_required false -> Rule 7 override, accepted",
          r["outcome"] == "accepted" and r["axes"]["audit"]["override"] is True)
    r = req({"profile": "GDPR-STANDARD", "human_oversight": "required_within_24h", "explainability_required": False})
    check("R10 explicit explainability_required false -> obligation_conflict",
          r["conflicts"][0]["diagnostic"] == "obligation_conflict" and r["conflicts"][0]["axis"] == "explainability")
    r = resolve_obligations("response", None, hr)
    check("R10 high-risk set does not apply to a response", r["outcome"] == "accepted"
          and r["axes"]["oversight"]["status"] == "no-value")
    r = resolve_obligations("event", {"pii_involved": True}, None)
    check("R10 Rule 2 rejects an event (any intent), axis null + field",
          r["conflicts"][0]["diagnostic"] == "missing_legal_basis" and r["conflicts"][0]["axis"] is None
          and r["conflicts"][0]["field"] == "legal_basis")
    r = resolve_obligations("request", {"profile": "MIFID-II", "human_oversight": "required_within_24h", "retention": "P1D"}, hr)
    lr = legacy_retention(r, "2026-10-31T00:00:00.000Z")
    check("R10 rejected P1D: conflict, evidence kept under the floor, declaration preserved",
          r["conflicts"][0]["diagnostic"] == "insufficient_retention" and lr["declared_retention"] == "P1D"
          and lr["effective_retention"] == "P1827D" and lr["retention_anchor"] == "2026-10-31T00:00:00.000Z"
          and r["axes"]["retention"]["result"] is None)
    r = resolve_obligations("event", None, None)
    check("R10 no compliance, no floor -> platform default P90D",
          r["axes"]["retention"]["result"]["duration"] == "P90D" and r["axes"]["retention"]["fill"]["source"] == "platform-default")
    r = resolve_obligations("event", {"profile": "GDPR-STANDARD"}, None)
    check("R10 residency null default -> no-value, fill preserved",
          r["axes"]["residency"]["status"] == "no-value" and r["axes"]["residency"]["fill"] == {"value": None, "source": "profile-default"})
    de = [{"axis": "residency", "kind": "restriction", "allowed": ["DE"],
           "source": {"class": "executor-policy", "id": "policy", "sha256": "4" * 64}}]
    r = resolve_obligations("event", {"profile": "MIFID-II"}, None, executor=de)
    check("R10 residency EU ∩ DE -> DE with member-list revision",
          r["axes"]["residency"]["result"] == {"codes": ["DE"], "revision": EU_REVISION, "sha256": jcs_sha256(EU_MEMBERS)})
    ch = [{"axis": "residency", "kind": "restriction", "allowed": ["CH"],
           "source": {"class": "executor-policy", "id": "policy", "sha256": "4" * 64}}]
    r = resolve_obligations("event", {"profile": "MIFID-II"}, None, executor=ch)
    check("R10 residency empty intersection -> obligation_conflict",
          r["conflicts"][0]["diagnostic"] == "obligation_conflict" and r["axes"]["residency"]["status"] == "conflict")
    out = receive({"id": "00000000-0000-4000-8000-0000000000aa", "from": "agent:acme.analyst", "to": "agent:x.y",
                   "intent": "request", "compliance": {"audit_required": False}, "payload": TEST_PAYLOAD}, hr)
    rec = out["records"][0] if out["records"] else {}
    check("R10 receiver emits the compliance error record with audit_required false",
          not out["accepted"] and rec.get("event_type") == "error" and rec.get("rejection_cause") == "compliance"
          and rec.get("correlation_id") == "00000000-0000-4000-8000-0000000000aa"
          and rec["obligation_resolution"]["outcome"] == "rejected" and out["error"]["code"] == "invalid_request")
    errs = schema_errors(rec, "arsia-audit-record.schema.json")
    check("R10 that emitted error record is valid against arsia-audit-record.schema.json", not errs, "; ".join(errs[:3]))
    inv07 = next(v for v in vectors if v["id"] == "INV-07")["message"]
    out = receive(inv07, dict(hr, agent_id=inv07["from"], evidence=dict(TEST_EVIDENCE, agent_id=inv07["from"])),
                  "2026-03-24T12:00:01.000Z")
    errs = [e for r in out["records"] for e in schema_errors(r, "arsia-audit-record.schema.json")]
    check("R10 INV-07 envelope: rejected, its emitted error record is schema-valid",
          not out["accepted"] and [r["event_type"] for r in out["records"]] == ["error"] and not errs,
          "; ".join(errs[:3]))
    out = receive({"id": "00000000-0000-4000-8000-0000000000ab", "from": "agent:acme.analyst", "to": "agent:x.y",
                   "intent": "request", "payload": TEST_PAYLOAD,
                   "compliance": {"profile": "GDPR-STANDARD", "human_oversight": "required_within_24h",
                                  "audit_required": False}}, hr)
    errs = [e for r in out["records"] for e in schema_errors(r, "arsia-audit-record.schema.json")]
    check("R10 override: request and compliance_warning records emitted, both schema-valid",
          out["accepted"] and [r["event_type"] for r in out["records"]] == ["request", "compliance_warning"]
          and not errs, "; ".join(errs[:3]))
    with_meta = [v for v in vectors if v.get("test_metadata", {}).get("scenario") in ("resolution", "router")]
    emitted = 0
    for v in with_meta:
        got = scenario_result(v["test_metadata"])
        miss = subset_match(v["test_metadata"]["expect"], got)
        check(f"R10 {v['id']} result matches its stated expectation", not miss, ", ".join(miss))
        errs = [e for r in got["emitted"] for e in schema_errors(r, "arsia-audit-record.schema.json")]
        emitted += len(got["emitted"])
        check(f"R10 {v['id']} every emitted record is schema-valid", not errs, "; ".join(errs[:3]))
    check("R10 runtime vectors emitted records to validate", emitted > 0, str(emitted))


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
    r1(); r2(vectors); r3(); r5(); r6(); r7(); r8(); r9(); r10(vectors); r11(); r12(); r13(); r14(vectors)
    print()
    print("ALL RUNTIME RULES PASSED" if not FAIL else f"{len(FAIL)} FAILURES: {FAIL}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
