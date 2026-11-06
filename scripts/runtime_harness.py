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
  R7  Pending args/root match;                              (Core §4.2, B-01)
      oversight audit-record count                         (Actions §3.5/§3.6, A-25)
  R8  I-JSON number range rule                             (State §2.1.2, B-08)
  R9  Content-field mutual exclusivity                     (Core §4.4.7, A-08)
  R10 Effective obligation resolution: fill, collect,      (Core §4.3.10, DR-3/DR-4)
      compose, evaluate, record; Rule 3; receiver and router
      simulations; authenticated context (Identity §7)
  R11 Issuer trust and key-origin policy                    (Core §6.5)
  R12 Session-scope audit precedence                        (State §8.3)
  R13 JWKS-document cache: unknown-kid refresh, max-age     (Core §5.2/§7.3, A-18; Identity §2.5, A-58)
      capped at 3600 s, revocation event, shared-cache sequences;
      `revocation` vectors: signed key-revocation events
      authenticated before invalidation, queued messages
  R14 Audit hash chain: chain value, verification against   (State §7.2, DR-5)
      a held head, tombstones, conformance-level mandate
  R15 Executor oversight and post-execution review:        (Actions §3, Core §4.3.10, DR-1/DR-2)
      executor sources, approval binding, review deadlines,
      overdue and escalation, async terminal results, tokens;
      approval/review decision verification in order with   (Actions §3.4, §3.9.3; A-57)
      signed tokens and a JWKS cache, decision_rejected,
      verified_kid/jwks_fetched_at evidence                  (Core §5.2, State §7.1; A-58)
  R16 Message timing: clock-skew tolerance and expiry       (Core §4.1.3, §4.2.2, §8.3)
      against a declared recipient clock; MAY posture;
      temporal causes kept apart from compliance causes
  R17 State generations: (key, generation, version)       (State §2.1.14, §2.4, §3.1.2, §3.2.1,
      identity, recreation, preconditions, snapshot,        §3.2.2; A-79, A-94)
      PURGE repetition
  R18 Retention axis: PURGE within retention needs a        (State §3.2.2, §6.3, §8.4; A-7, A-70)
      recorded override, evaluated from stored state over
      every generation; own record retention untouched;
      P1827D against P5Y over a 400-year cycle
  R19 Broker relay record: forwarding fields together,   (Routing §7.3 Rule 7, §7.4.2; A-89)
      success carries them, latency = forwarded_at − received_at
  R20 DPoP proof verification: RFC 9449 §4.3 checks and   (Identity §3.3, Routing §2.3.3; A-49)
      the ARSIA profile, nonce challenge, single-use jti
      (atomic reference store), brokered nonce challenge
  R21 Token binding: SHA-256 of the presented token's     (Core §4.3.9; A-55)
      exact octets against authorization.token_hash
  R22 Relay attestation verification: signature, broker  (Routing §7.4.1; A-56)
      authorisation, envelope and token binding, identities,
      window (profile skew), replay

Exit code 0 = all green.
"""
import calendar
import datetime as dt
import json
import re
import sys

sys.path.insert(0, "scripts")
from validate_vectors import strict_json, strict_load  # noqa: E402  (A-61: artifacts load strictly)

FAIL = []


def check(name, cond, detail="", executed=()):
    """`executed`: the IDs of the corpus vectors whose content this check consumed. A passing check prints
    them as `# executed <rule> <IDs>` — the record the RTM and conformance `exec:` tokens are verified
    against (coverage SC4): a vector ID in a check's name is not evidence that the vector was read."""
    print(("ok   " if cond else "FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        FAIL.append(name)
    elif executed:
        print(f"# executed {name.split()[0]} {' '.join(executed)}")


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
# The approval_decision verification of Actions §3.4 runs in R15 (Run.approval), on the execution vectors.
def verify_pending(pending):
    """Actions §3.2: payload.args.original_request_id MUST equal envelope root_request_id."""
    return pending["payload"]["args"]["original_request_id"] == pending.get("root_request_id")


def r7():
    pend_msg = {"root_request_id": "R1", "payload": {"args": {"original_request_id": "R1"}}}
    check("R7 pending args/root match", verify_pending(pend_msg))
    check("R7 pending args/root MISMATCH rejected", not verify_pending({**pend_msg, "root_request_id": "RX"}))
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
PROFILES = strict_load("profiles/arsia-compliance-profiles.json")["profiles"]
OBLIGATION_RULES = strict_load("profiles/arsia-obligation-rules.json")
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
                        executor=(), sensitive_entry=False, review_config=None):
    """Core §4.3.10 reference: fill, collect, compose, evaluate, record.

    compliance is the envelope's `compliance` object, or None when the field is absent. identity is the
    authenticated IdentityRecord fact {agent_id, ai_system_classification, evidence} or None. executor
    holds the executor-policy requirements collected by the executing agent (Core §4.3.10.2;
    executor_sources below). review_config, given only at the executing agent, is its post-execution
    review configuration (Actions §3.9.1). Returns the State §7.1 `obligation_resolution` object."""
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
    if c is None and review_config is not None:
        for m in ("required_within_24h", "required_post_execution"):
            if m not in modes:
                continue
            needed = ["review_endpoint", "escalation_destination"]
            if m == "required_post_execution":
                needed.append("post_execution_review_period")
            missing = next((e for e in needed if not review_config.get(e)), None)
            if missing:
                c = conflict("obligation_conflict", "oversight", declared.get("value"), {"mode": m, "missing": missing},
                             [r["source"] for r, _, _ in rq if r["kind"] == "value" and r["value"] == m])
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
        docs = [strict_load(f) for f in sorted(glob.glob("schemas/*.json"))]
        _REGISTRY.append(Registry().with_resources([(d["$id"], Resource.from_contents(d)) for d in docs if "$id" in d]))
    reg = _REGISTRY[0]
    sid = strict_load(f"schemas/{schema_file}")["$id"]
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
        check(f"R10 {v['id']} result matches its stated expectation", not miss, ", ".join(miss), executed=[v["id"]])
        errs = [e for r in got["emitted"] for e in schema_errors(r, "arsia-audit-record.schema.json")]
        emitted += len(got["emitted"])
        check(f"R10 {v['id']} every emitted record is schema-valid", not errs, "; ".join(errs[:3]))
    check("R10 runtime vectors emitted records to validate", emitted > 0, str(emitted))


# ------------------------------- R15 executor oversight and post-execution review (DR-1, DR-2)
# Actions §2.1, §3.2-§3.9, §4.1, §4.3; Core §4.3.10.2, §4.4.8, §6.1, §6.4, §8.3, §11.3;
# Identity §7.3, §7.7, §9.1; Assets §5.2.
AGENT_SEEDS = {"agent:acme.executor": 11, "agent:acme.analyst": 12, "agent:acme.oversight-dashboard": 13,
               "agent:acme.escalation": 14, "agent:corp.gateway": 15, "agent:acme.approver-two": 16}
EXECUTOR_ID = "agent:acme.executor"
REQUESTER_ID = "agent:acme.analyst"
REVIEWER_ID = "agent:acme.oversight-dashboard"
TRUSTED_ISSUERS = {"https://as.acme.example"}
FULL_REVIEW_CONFIG = {"review_endpoint": REVIEWER_ID, "escalation_destination": "agent:acme.escalation"}
EXECUTOR_SOURCE_PREFIXES = ("action-descriptor:", "capability-policy:", "risk-assessment:")  # Core §4.3.10.2
SERVER_BACKOFF = (1, 2, 4)  # Core §11.3 Server Errors, without jitter
MAX_RETRIES = 3
TRANSIENT = {"internal_error", "service_unavailable", "timeout", "transport_failure", "rate_limited"}
POST_MODES = ("required_within_24h", "required_post_execution")


def det_id(seed):
    return record_id_for(seed, "message")


def _key(agent):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    return Ed25519PrivateKey.from_private_bytes(bytes([AGENT_SEEDS[agent]]) * 32)


def sign(msg, agent, alg="EdDSA"):
    """Draft-02 signing profile (envelope minus security.sig), Core §5.1, with the agent's Ed25519 key; `alg`
    is the declared algorithm, inside the signed bytes (another value builds an alg/key mismatch)."""
    from regen_v2 import signing_input_v2, b64url
    msg["security"] = {"alg": alg, "kid": f"{agent}#key-1"}
    msg["security"]["sig"] = b64url(_key(agent).sign(signing_input_v2(msg)))
    return msg


def signature_ok(msg):
    import base64
    from regen_v2 import signing_input_v2
    sec = msg.get("security") or {}
    agent = sec.get("kid", "").split("#")[0]
    if agent not in AGENT_SEEDS or agent != msg.get("from") or "sig" not in sec:
        return False
    try:
        _key(agent).public_key().verify(base64.urlsafe_b64decode(sec["sig"] + "=" * (-len(sec["sig"]) % 4)),
                                        signing_input_v2(msg))
        return True
    except Exception:
        return False


# A-57/A-58: verification through the recipient's JWKS cache (Core §5.2) and authenticated access tokens
# (Core §6.4 steps 2-3, §6.5), shared by approval decisions (Actions §3.4) and review decisions (§3.9.3).
APPROVE = "arsiaprotocol.oversight.approve"
JWKS_DEFAULT_MAX_AGE = 3600
ISSUER_SEEDS = {"https://as.acme.example": 31, "https://evil.example": 32}


def _epoch(at):
    return iso(at).replace(tzinfo=dt.timezone.utc).timestamp()


def _at(seconds):
    return stamp(dt.datetime.fromtimestamp(seconds, dt.timezone.utc).replace(tzinfo=None))


class KeyDirectory:
    """The executing agent's view of its senders' JWKS (Core §5.2): one JwksCache per sender over the sender's
    published key (`<agent>#key-1`). `cached` pre-fills a sender's cache with an earlier fetch:
    {agent: {"fetched_at": t, "max_age": s}}."""

    def __init__(self, cached=None):
        self.publishers, self.caches = {}, {}
        for agent, c in (cached or {}).items():
            self.cache(agent, c.get("max_age", JWKS_DEFAULT_MAX_AGE))._refresh(_epoch(c["fetched_at"]))

    def cache(self, agent, max_age=JWKS_DEFAULT_MAX_AGE):
        if agent not in self.caches:
            self.publishers[agent] = Publisher({f"{agent}#key-1"}, max_age)
            self.caches[agent] = JwksCache(self.publishers[agent])
        return self.caches[agent]

    def remove(self, kid):
        agent = kid.split("#", 1)[0]
        self.cache(agent)
        self.publishers[agent].kids.discard(kid)


def verify_signed(msg, directory, now):
    """Core §5.2 at `now`, the instant of verification: the kid belongs to `from`, its key is resolved through the
    cache under the refresh rules of Verification Caching, and the signature verifies. Returns (ok, verified_kid,
    jwks_fetched_at): the instant of the fetch that supplied the key, also when it was served from the cache."""
    sec = msg.get("security") or {}
    kid = sec.get("kid", "")
    agent = kid.split("#", 1)[0]
    if agent != msg.get("from") or agent not in AGENT_SEEDS:
        return False, None, None
    cache = directory.cache(agent)
    if not cache.accept(kid, _epoch(now)):
        return False, None, None
    sys.path.insert(0, "scripts")
    import validate_vectors as vv
    from regen_v2 import signing_input_v2
    try:  # Core §5.2 Step 5: the declared alg must be allowlisted and coherent with the key, then verify
        vv._verify_signature(sec.get("alg"), _unb64u(_jwk(agent)["x"]), vv._base64url_decode(sec.get("sig", "")),
                             signing_input_v2(msg))
    except Exception:
        return False, None, None
    return True, kid, _at(cache.fetched_at)


def _issuer_key(issuer):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    return Ed25519PrivateKey.from_private_bytes(bytes([ISSUER_SEEDS.get(issuer, 33)]) * 32)


def issue_token(claims, signer=None):
    """A compact JWS access token (Core §6.1) signed with its issuer's key, or with `signer`'s to forge one."""
    h = _b64u(json.dumps({"typ": "at+jwt", "alg": "EdDSA"}).encode())
    p = _b64u(json.dumps(claims).encode())
    return f"{h}.{p}." + _b64u(_issuer_key(signer or claims["iss"]).sign(f"{h}.{p}".encode()))


def verify_token(token, message, now, skew):
    """Core §6.4 steps 2-3 and §6.5 at `now`: a trusted issuer, an algorithm allowed for it and coherent with its
    Ed25519 key, the signature under the issuer's CONFIGURED key (never one the token names), exp/iat within the
    clock skew, sub = from, aud = to within the issuer's audience policy. Returns the claims, or None."""
    try:
        h, p, s = token.split(".")
        header, claims = json.loads(_unb64u(h)), json.loads(_unb64u(p))
    except Exception:
        return None
    cfg = TRUST.get(claims.get("iss"))
    if cfg is None or header.get("alg") not in cfg["algs"] or header.get("alg") != "EdDSA":
        return None
    try:
        _issuer_key(claims["iss"]).public_key().verify(_unb64u(s), f"{h}.{p}".encode())
    except Exception:
        return None
    if schema_errors(claims, "arsia-jwt-claims.schema.json"):  # Core §6.1: every required claim, none defaulted
        return None
    t = _epoch(now)
    if not (claims["exp"] + skew > t and claims["iat"] - skew <= t):
        return None
    if claims.get("sub") != message.get("from") or claims.get("aud") != message.get("to") \
            or claims.get("aud") not in cfg["audiences"]:
        return None
    return claims


def verify_oversight_decision(decision, token, verified_at, directory, skew):
    """Actions §3.4 verification steps 1-3 (also §3.9.3 steps 1-3), at the verification instant: signature,
    token, then the reserved approve capability matched exactly in the token scope and present in
    `capabilities`. Returns (code or None, evidence); evidence carries verified_kid and jwks_fetched_at once
    the signature verified (State §7.1), and nothing otherwise."""
    ok, kid, fetched = verify_signed(decision, directory, verified_at)
    if not ok:
        return "unauthorized", {}
    evidence = {"verified_kid": kid, "jwks_fetched_at": fetched}
    claims = verify_token(token, decision, verified_at, skew)
    if claims is None:
        return "unauthorized", evidence
    if not authorized(claims.get("scope", "").split(), [APPROVE]) or APPROVE not in decision.get("capabilities", []):
        return "forbidden", evidence
    return None, evidence


def executor_sources(action_id, descriptor=None, claim=None, capabilities=(), assessment=None):
    """Core §4.3.10.2 executor-policy requirements: each demands required_before_execution or nothing."""
    def demand(sid, digest):
        return {"axis": "oversight", "kind": "value", "value": "required_before_execution",
                "source": {"class": "executor-policy", "id": sid, "sha256": digest}}
    out = []
    if descriptor and descriptor.get("human_oversight_required") is True:
        out.append(demand(f"action-descriptor:{action_id}", jcs_sha256(descriptor)))
    if claim:
        pol = claim["policy"]
        out += [demand(f"capability-policy:{pol['issuer']}/{pol['version']}", pol["sha256"])
                for cap in capabilities if cap in claim["capabilities"]]
    if assessment and assessment["assessed_risk_level"] >= assessment["threshold"]:
        out.append(demand(f"risk-assessment:{action_id}", jcs_sha256(assessment)))
    return out


def plus_seconds(at, s):
    return stamp(iso(at) + dt.timedelta(seconds=s))


def deliver_escalation(outcomes, start):
    """Actions §3.9.4: Core §11.3 applied to the overdue notice. Server-error backoff for transient
    failures; rate_limited waits Retry-After (or retry_after_seconds, or 60 s); at most 3 retries."""
    t, times = iso(start), []
    for attempt, out in enumerate(outcomes[:MAX_RETRIES + 1], 1):
        times.append(stamp(t))
        code = out if isinstance(out, str) else out["code"]
        if code == "accepted":
            return "delivered", attempt, times
        if code not in TRANSIENT or attempt == MAX_RETRIES + 1:
            return "failed", attempt, times
        if code == "rate_limited":
            delay = out.get("retry_after", out.get("retry_after_seconds", 60)) if isinstance(out, dict) else 60
        else:
            delay = SERVER_BACKOFF[attempt - 1]
        t += dt.timedelta(seconds=delay)
    return "failed", len(times), times


class Run:
    """One request at the executing agent: resolution, prior approval, execution, terminal result,
    post-execution review. Records are append-only; snapshots prove none is modified later."""

    def __init__(self, req, descriptor, at, claim=None, assessment=None, review_config=FULL_REVIEW_CONFIG,
                 identity=None, escalation=None, directory=None):
        self.req, self.descriptor, self.at = req, descriptor, at
        self.records, self._snapshots, self.messages = [], [], []
        self.directory = directory or KeyDirectory()
        self.skew = skew_tolerance(req)[0]
        self.queue, self.required, self.approvers = [], 1, set()
        ok, kid, fetched = verify_signed(req, self.directory, at)  # Core §5.2 on the received request
        self.req_evidence = {"verified_kid": kid, "jwks_fetched_at": fetched} if ok else {}
        self.escalation = escalation or {}
        self.pending = self.terminal = self.review = self.ack = None
        self.remediation = False
        cfg = None
        if review_config is not None:
            cfg = dict(review_config, post_execution_review_period=descriptor.get("post_execution_review_period"))
        self.review_config = cfg  # the configuration validated by the resolution is the one the review uses
        ex = executor_sources(descriptor["action_id"], descriptor, claim, req.get("capabilities", []), assessment)
        self.res = resolve_obligations("request", req.get("compliance"), identity, at, executor=ex, review_config=cfg)
        self.modes = self.res["axes"]["oversight"]["result"] or []
        if self.res["outcome"] == "rejected":
            self.path = "rejected"
            self.error = {"code": "invalid_request",
                          "details": error_details(self.res["conflicts"][0], self.res, at)}
            self.rejection = sign({"v": "2.0", "id": det_id(req["id"] + "/rejection"), "ts": at, "from": EXECUTOR_ID,
                                   "to": req["from"], "intent": "error", "correlation_id": req["id"],
                                   "root_request_id": req["id"],
                                   "payload": {"type": req["payload"]["type"],
                                               "error": dict(self.error, description="Compliance obligations not satisfiable"),
                                               "obligation_resolution": self.res}}, EXECUTOR_ID)
            self.messages.append(self.rejection)
            self.record(req, "error", at, rejection_cause="compliance", correlation_id=req["id"],
                        obligation_resolution=self.res, **self.req_evidence)
            return
        self.record(req, "request", at, obligation_resolution=self.res, **self.req_evidence)
        if "required_before_execution" in self.modes:
            self.path = "pending"
            self._send_pending()
        else:
            self.path = "executing"

    def record(self, message, event_type, at, **extra):
        rec = audit_record(message, self.res, at, RECEIVER_OPERATOR, event_type, **extra)
        self.records.append(rec)
        self._snapshots.append(json.dumps(rec, sort_keys=True))
        return rec

    def unmodified(self):
        return [json.dumps(r, sort_keys=True) for r in self.records] == self._snapshots

    def _send_pending(self):
        req, deadline = self.req, plus_seconds(self.at, 3600)
        msg = {"v": "2.0", "id": det_id(req["id"] + "/pending"), "ts": self.at, "from": EXECUTOR_ID,
               "to": req["from"], "intent": "pending_approval", "correlation_id": req["id"],
               "root_request_id": req["id"], "expires_at": deadline,
               "payload": {"type": "arsiaprotocol.oversight/pending",
                           "args": {"action_id": self.descriptor["action_id"], "original_request_id": req["id"],
                                    "approval_deadline": deadline,
                                    "approver_capability": "arsiaprotocol.oversight.approve",
                                    "context": f"Execute {self.descriptor['action_id']} for {req['from']}.",
                                    "risk_level": self.descriptor["risk_level"],
                                    "request_payload_hash": payload_hash(req)},
                           "obligation_resolution": self.res}}
        self.pending = sign(msg, EXECUTOR_ID)
        self.messages.append(self.pending)
        self.approvers, self.approved = set(), False
        self.record(self.pending, "pending_approval", self.at, correlation_id=req["id"],
                    root_request_id=req["id"], approval_deadline=deadline)

    def approval(self, decision, received_at, required=None, token=None, verified_at=None):
        """Receipt and verification of one approval_decision (Actions §3.4). Returns the rejection code or None."""
        self.receive_decision(decision, received_at, token)
        return self.process(verified_at or received_at, required)[-1]

    def receive_decision(self, decision, received_at, token):
        """Receipt only: the receipt instant is kept for the deadline check (Actions §3.4, step 5)."""
        self.queue.append((decision, received_at, token))

    def process(self, now, required=None):
        """Verifies the queued decisions in receipt order at `now`, the instant of verification."""
        if required is not None:
            self.required = required
        codes = []
        while self.queue:
            decision, received_at, token = self.queue.pop(0)
            codes.append(self._decide(decision, received_at, token, now))
        return codes

    def _decide(self, decision, received_at, token, now):
        """Actions §3.4 verification, in order: signature, token and authority at the verification instant `now`
        (steps 1-3), correlation and binding (step 4), deadline at the receipt instant and pending state
        (step 5). The first failing step gives the code; a rejected decision is logged, nothing else changes."""
        p = self.pending
        result = decision["payload"]["result"]
        code, evidence = verify_oversight_decision(decision, token, now, self.directory, self.skew)
        if code is None and (decision.get("correlation_id") != p["id"]
                             or decision.get("root_request_id") != p["root_request_id"]
                             or result.get("request_payload_hash") != p["payload"]["args"]["request_payload_hash"]
                             or result.get("approver_id") != decision.get("from")):
            code = "invalid_request"
        if code is None and (iso(received_at) >= iso(p["payload"]["args"]["approval_deadline"])
                             or self.path != "pending" or decision["from"] in self.approvers):
            code = "invalid_request"
        if code is not None:
            self.reject(decision, now, code, evidence)
            return code
        self.approvers.add(decision["from"])
        self.record(decision, "approval_decision", now, correlation_id=p["id"],
                    root_request_id=p["root_request_id"], decision=result["decision"],
                    approver_id=result["approver_id"], reason=result.get("reason"), **evidence)
        if result["decision"] == "denied":
            self._finish_error(now, "forbidden", "Action denied by human oversight",
                               {"oversight_decision": "denied", "approver_id": result["approver_id"],
                                "reason": result.get("reason")})
        elif len(self.approvers) >= self.required:
            self.path = "executing"
        return None

    def reject(self, decision, at, code, evidence):
        """A received decision rejected and not admitted (Actions §3.4, §3.9.3; State §7.1): the record keeps the
        correlation the decision carried, as received, and the verification evidence only if its signature
        verified."""
        self.record(decision, "decision_rejected", at, correlation_id=decision.get("correlation_id"),
                    root_request_id=decision.get("root_request_id"), rejection_code=code, **evidence)

    def expire(self, now):
        """Path 3: the decisions received before the deadline are verified first; the pending_approval is
        resolved as expired only if it is still pending. Returns the codes of the decisions processed."""
        codes = self.process(now)
        if self.path != "pending" or iso(now) < iso(self.pending["payload"]["args"]["approval_deadline"]):
            return codes  # resolved already, or the deadline is not reached: no expiry
        p = self.pending
        self.record(p, "approval_expired", now, correlation_id=p["id"], root_request_id=p["root_request_id"],
                    decision="expired", reason=None)
        self._finish_error(now, "forbidden", "Action approval deadline exceeded",
                           {"oversight_decision": "expired", "deadline": p["payload"]["args"]["approval_deadline"]})
        return codes

    def _finish_error(self, at, code, description, details):
        req = self.req
        err = {"v": "2.0", "id": det_id(req["id"] + "/oversight-error"), "ts": at, "from": EXECUTOR_ID,
               "to": req["from"], "intent": "error", "correlation_id": req["id"], "root_request_id": req["id"],
               "payload": {"type": req["payload"]["type"],
                           "error": {"code": code, "description": description, "details": details},
                           "obligation_resolution": self.res}}
        self.final_error = sign(err, EXECUTOR_ID)
        self.messages.append(self.final_error)
        self.path = "failed"
        self.record(self.final_error, "error", at, correlation_id=req["id"], root_request_id=req["id"],
                    outcome=details["oversight_decision"])

    def acknowledge(self):
        """Asynchronous acknowledgment (Actions §4.3 item 1): not a terminal result."""
        req = self.req
        self.ack = sign({"v": "2.0", "id": det_id(req["id"] + "/ack"), "ts": self.at, "from": EXECUTOR_ID,
                         "to": req["from"], "intent": "response", "correlation_id": req["id"],
                         "root_request_id": req["id"],
                         "payload": {"type": req["payload"]["type"],
                                     "result": {"status": "accepted",
                                                "status_url": "https://executor.example/status/1"}}},
                        EXECUTOR_ID)
        self.messages.append(self.ack)

    def execute(self, end_at, outcome="success", asynchronous=False):
        """Executes and materializes the terminal result at end_at (Actions §3.9.2, §4.3)."""
        assert self.path == "executing"
        req = self.req
        if asynchronous:
            self.acknowledge()
        payload = {"type": req["payload"]["type"]}
        if outcome == "success":
            payload["result"] = {"status": "done"}
        else:
            payload["error"] = {"code": "internal_error", "description": "Action execution failed"}
        payload["obligation_resolution"] = self.res
        msg = {"v": "2.0", "id": det_id(req["id"] + "/terminal"), "ts": end_at, "from": EXECUTOR_ID,
               "to": req["from"], "intent": "response" if outcome == "success" else "error",
               "correlation_id": req["id"], "root_request_id": req["id"], "payload": payload}
        self.terminal = sign(msg, EXECUTOR_ID)
        self.messages.append(self.terminal)
        self.path = "completed" if outcome == "success" else "failed"
        self.record(self.terminal, msg["intent"], end_at, correlation_id=req["id"], root_request_id=req["id"],
                    outcome="success" if outcome == "success" else "error")
        if any(m in self.modes for m in POST_MODES):
            self.review = Review(self)
        return self.terminal



def accept_retrieved(result, expected_root):
    """Actions §4.3 item 3: a persisted, authenticated terminal result. Signature and binding are
    verified; its ts is never compared with the current time (Core §8.3) and never renewed."""
    return signature_ok(result) and result["correlation_id"] == expected_root and \
        result["root_request_id"] == expected_root


class Review:
    """Actions §3.9: obligations, deadlines, notices, states; lateness from deadlines and receipt."""

    def __init__(self, run):
        self.run, t = run, run.terminal
        at, d = t["ts"], run.descriptor
        self.obligations = []
        for m in POST_MODES:
            if m not in run.modes:
                continue
            if m == "required_within_24h":
                dl, ps = stamp(iso(at) + dt.timedelta(hours=24)), None
            else:
                dl = stamp(add_duration(iso(at), d["post_execution_review_period"]))
                ps = {"class": "executor-policy", "id": f"action-descriptor:{d['action_id']}",
                      "sha256": jcs_sha256(d)}
            self.obligations.append({"mode": m, "deadline": dl, "period_source": ps})
        self.review_deadline = min(self.obligations, key=lambda o: iso(o["deadline"]))["deadline"]
        req = run.req
        self.notice = sign({"v": "2.0", "id": det_id(req["id"] + "/review"), "ts": at, "from": EXECUTOR_ID,
                            "to": run.review_config["review_endpoint"], "intent": "event",
                            "correlation_id": t["id"], "root_request_id": req["id"],
                            "payload": {"type": "arsiaprotocol.oversight/review-pending",
                                        "data": {"action_id": d["action_id"], "original_request_id": req["id"],
                                                 "execution_message_id": t["id"], "executed_at": at,
                                                 "outcome": "success" if t["intent"] == "response" else "error",
                                                 "result_hash": payload_hash(t),
                                                 "obligations": self.obligations,
                                                 "review_deadline": self.review_deadline,
                                                 "reviewer_capability": "arsiaprotocol.oversight.approve",
                                                 "context": f"{d['action_id']} executed; review its result.",
                                                 "risk_level": d["risk_level"]}}}, EXECUTOR_ID)
        run.messages.append(self.notice)
        run.record(self.notice, "review_pending", at, correlation_id=t["id"], root_request_id=req["id"],
                   execution_message_id=t["id"], result_hash=payload_hash(t), review_deadline=self.review_deadline)
        self.state, self.overdue_done, self.decision, self.escalations = "pending", set(), None, []

    def tick(self, now):
        if self.decision is not None:
            return
        for i, ob in enumerate(self.obligations):
            if i not in self.overdue_done and iso(now) >= iso(ob["deadline"]):
                self._overdue(i, ob, now)

    def _overdue(self, i, ob, now):
        run, req = self.run, self.run.req
        self.overdue_done.add(i)
        self.state = "overdue"
        note = sign({"v": "2.0", "id": det_id(f"{req['id']}/overdue/{ob['mode']}"), "ts": now, "from": EXECUTOR_ID,
                     "to": run.review_config["escalation_destination"], "intent": "event",
                     "correlation_id": self.notice["id"], "root_request_id": req["id"],
                     "payload": {"type": "arsiaprotocol.oversight/review-overdue",
                                 "data": {"action_id": run.descriptor["action_id"], "original_request_id": req["id"],
                                          "execution_message_id": run.terminal["id"], "mode": ob["mode"],
                                          "deadline": ob["deadline"]}}}, EXECUTOR_ID)
        run.messages.append(note)
        run.record(note, "review_overdue", now, correlation_id=self.notice["id"], root_request_id=req["id"],
                   review_mode=ob["mode"], review_deadline=ob["deadline"])
        result, attempts, times = deliver_escalation(run.escalation.get(ob["mode"], ["accepted"]), now)
        self.escalations.append({"mode": ob["mode"], "result": result, "attempts": attempts, "times": times})
        run.record(note, "review_escalation", times[-1], correlation_id=self.notice["id"], root_request_id=req["id"],
                   review_mode=ob["mode"], escalation_result=result, escalation_attempts=attempts)
        if result == "failed":
            run.record(note, "compliance_warning", times[-1])

    def receive(self, decision, received_at, token, verified_at=None):
        """Actions §3.9.3 verification order; a rejected decision is logged as decision_rejected (State §7.1).
        A decision received after a deadline is not rejected for that reason (§3.9.4). Returns (code, state)."""
        verified_at = verified_at or received_at
        code, evidence = verify_oversight_decision(decision, token, verified_at, self.run.directory, self.run.skew)
        data, nd = decision["payload"]["data"], self.notice["payload"]["data"]
        if code is None and (decision.get("correlation_id") != self.notice["id"] or
                             decision.get("root_request_id") != self.notice["root_request_id"] or
                             data["execution_message_id"] != nd["execution_message_id"] or
                             data["result_hash"] != nd["result_hash"] or data["reviewer_id"] != decision["from"]):
            code = "invalid_request"
        if code is None and self.decision is not None:
            code = "invalid_request"  # duplicate: recorded outcome unchanged (Core §4.2.1 rule 2)
        if code is not None:
            self.run.reject(decision, verified_at, code, evidence)
            return code, self.state
        self.tick(received_at)  # overdue facts first, whatever the timer did (Actions §3.9.4)
        late = any(iso(received_at) >= iso(ob["deadline"]) for ob in self.obligations)
        self.decision = decision
        self.state = "completed_late" if late else "completed"
        self.run.record(decision, "review_decision", verified_at, correlation_id=self.notice["id"],
                        root_request_id=self.notice["root_request_id"], review_outcome=data["decision"],
                        reviewer_id=data["reviewer_id"], late=late, reason=data["reason"], **evidence)
        if data["decision"] == "objected":
            self.run.remediation = True
        return None, self.state


def review_decision_msg(review, at, decision="confirmed", reviewer=REVIEWER_ID, result_hash=None,
                        capabilities=("arsiaprotocol.oversight.approve",), tamper=False):
    nd = review.notice["payload"]["data"]
    msg = {"v": "2.0", "id": det_id(f"{review.notice['id']}/decision/{at}/{reviewer}"), "ts": at, "from": reviewer,
           "to": EXECUTOR_ID, "intent": "event", "correlation_id": review.notice["id"],
           "root_request_id": review.notice["root_request_id"], "capabilities": list(capabilities),
           "payload": {"type": "arsiaprotocol.oversight/review-decision",
                       "data": {"decision": decision, "reviewer_id": reviewer,
                                "execution_message_id": nd["execution_message_id"],
                                "result_hash": result_hash or nd["result_hash"],
                                "reason": None if decision == "confirmed" else "Result outside policy"}}}
    sign(msg, reviewer)
    if tamper:
        msg["payload"]["data"]["reason"] = "altered after signing"
    return msg


def reviewer_token(at, iss="https://as.acme.example", scope=APPROVE, sub=REVIEWER_ID, aud=EXECUTOR_ID,
                   lifetime=600, tamper=False, drop=()):
    """A signed access token for an approver or reviewer, issued at `at`, with every claim Core §6.1 requires;
    `drop` omits claims before the issuer signs, `tamper` changes a claim after it signed (its signature no
    longer verifies)."""
    t = int(_epoch(at))
    claims = {"iss": iss, "sub": sub, "aud": aud, "iat": t, "exp": t + lifetime, "scope": scope,
              "jti": det_id(f"token/{iss}/{sub}/{aud}/{scope}/{at}")}
    token = issue_token({k: v for k, v in claims.items() if k not in drop})
    if tamper:
        h, p, s = token.split(".")
        claims = json.loads(_unb64u(p))
        claims["exp"] += 86400
        token = f"{h}.{_b64u(json.dumps(claims).encode())}.{s}"
    return token


def approval_decision_msg(run, at, decision="approved", approver=REVIEWER_ID, payload_hash_override=None,
                          capabilities=(APPROVE,), approver_id=None, correlation_id=None, root_request_id=None,
                          tamper=False, alg="EdDSA"):
    """An approval_decision signed by its approver (Actions §3.3); the overrides build the negatives of the
    §3.4 verification, and `tamper` changes the reason after signing (its signature no longer verifies)."""
    p = run.pending
    msg = {"v": "2.0", "id": det_id(f"{p['id']}/approval/{approver}/{at}"), "ts": at, "from": approver,
           "to": EXECUTOR_ID, "intent": "approval_decision", "correlation_id": correlation_id or p["id"],
           "root_request_id": root_request_id or p["root_request_id"], "capabilities": list(capabilities),
           "payload": {"type": "arsiaprotocol.oversight/decision",
                       "result": {"decision": decision, "approver_id": approver_id or approver,
                                  "request_payload_hash": payload_hash_override
                                  or p["payload"]["args"]["request_payload_hash"]}}}  # optional members omitted
    sign(msg, approver, alg)
    if tamper:
        msg["payload"]["result"]["reason"] = "altered after signing"
    return msg


def reissue_token(claim, scope):
    """Identity §9.1: a new token keeps requirement and policy for every remaining listed capability."""
    caps = [c for c in claim["capabilities"] if c in scope]
    return {"requirement": claim["requirement"], "capabilities": caps, "policy": dict(claim["policy"])} if caps else None


def router_oversight_ok(decision_oversight, decision_policy, scope, claim):
    """Identity §7.7: every bound oversight capability in scope must be listed with the decision's policy."""
    needed = [c for c in scope if c in decision_oversight]
    if not needed:
        return True
    return bool(claim) and claim["policy"] == decision_policy and all(c in claim["capabilities"] for c in needed)


def make_request(rid, payload, compliance=None, capabilities=("test.unit",), at="2026-10-31T10:00:00.000Z",
                 sender=REQUESTER_ID):
    req = {"v": "2.0", "id": rid, "ts": at, "from": sender, "to": EXECUTOR_ID, "intent": "request",
           "expires_at": plus_seconds(at, 30), "capabilities": list(capabilities), "payload": payload}
    if compliance is not None:
        req["compliance"] = compliance
    return sign(req, sender)


def make_descriptor(action_id, oversight=False, risk=5, period=None):
    d = {"action_id": action_id, "category": "system", "description": f"Test action {action_id}",
         "risk_level": risk, "reversible": False, "idempotent": False, "required_capabilities": ["test.unit"],
         "human_oversight_required": oversight, "audit_required": True, "explainability_required": False}
    if period:
        d["post_execution_review_period"] = period
    return d


TEST_CLAIM_POLICY = {"issuer": "agent:corp.gateway", "version": "finco-2026-q1",
                     "sha256": "6b8c702884af67342d1aff9949d3474599aa3f84aae9f92a6e3fa0a78f59c698"}


def fixture_check(out, decision):
    """Fixture quality (not the normative flow): a decision the scenario builds is schema-valid, so that the code
    its vector expects from Actions §3.4 / §3.9.3 is not pre-empted by the full schema validation of the Core
    §5.2 pipeline (step 11). The executing agent's verification order is unchanged."""
    out.setdefault("fixture_errors", []).extend(f"{decision['id']}: {e}"
                                                 for e in schema_errors(decision, "arsia-message.schema.json"))


def execution_case(inp):
    """Runs a runtime vector's `execution` scenario; returns the computed result object."""
    case = inp["case"]
    at = inp.get("at", "2026-10-31T10:00:00.000Z")
    rid = inp.get("request_id", "7a000000-0000-4000-8000-000000000001")
    payload = inp.get("payload", {"type": "com.acme.test/run", "args": {"suite": "unit"}})
    desc = make_descriptor(payload["type"], inp.get("descriptor_oversight", False), inp.get("risk_level", 5),
                           inp.get("review_period"))
    claim = None
    if inp.get("claim"):
        claim = {"requirement": "required_before_execution", "capabilities": inp["claim"], "policy": TEST_CLAIM_POLICY}
    assessment = None
    if "assessed_risk" in inp:
        assessment = {"action_id": payload["type"], "assessed_risk_level": inp["assessed_risk"], "threshold": 7}
    cfg = dict(FULL_REVIEW_CONFIG, **inp.get("review_config", {}))
    for k in inp.get("missing_config", []):
        cfg.pop(k)
    identity = None
    if inp.get("high_risk_sender"):
        identity = {"agent_id": REQUESTER_ID, "ai_system_classification": "high-risk",
                    "evidence": dict(TEST_EVIDENCE, agent_id=REQUESTER_ID)}
    sender = "agent:corp.gateway" if case == "check03" else REQUESTER_ID  # CHECK-03 probe: gateway -> agent
    req = make_request(rid, payload, inp.get("compliance"), inp.get("capabilities", ["test.unit"]), at, sender)
    if case == "router":
        token_scope = inp["scope"]
        ok = router_oversight_ok(inp["decision_oversight"], TEST_CLAIM_POLICY, token_scope, claim)
        internal = reissue_token(claim, inp["internal_scope"]) if ok and claim and "internal_scope" in inp else None
        return {"forwarded": ok, "error": None if ok else "unauthorized", "internal_claim": internal,
                "emitted": [], "messages": []}
    if case == "check03":
        trusted = inp["probe_issuer"] in TRUSTED_ISSUERS
        if not trusted:
            return {"check03": "fail", "details": "probe credential rejected", "error": "unauthorized",
                    "emitted": [], "messages": []}
    run = Run(req, desc, at, claim, assessment, cfg, identity, inp.get("escalation"),
              KeyDirectory(inp.get("jwks_cache")))
    out = {"path": run.path, "outcome": run.res["outcome"],
           "oversight": {"result": run.res["axes"]["oversight"]["result"],
                         "status": run.res["axes"]["oversight"]["status"],
                         "declared": run.res["axes"]["oversight"]["declared"],
                         "fill": run.res["axes"]["oversight"]["fill"],
                         "source_ids": sorted(r["source"]["id"] for r in run.res["axes"]["oversight"]["requirements"])}}
    if run.path == "rejected":
        out["error"] = run.error
        out["conflict"] = run.res["axes"]["oversight"]["conflict"]
        r = run.rejection
        out["rejection_message"] = {"intent": r["intent"], "to": r["to"], "correlation_id": r["correlation_id"],
                                    "error": {k: r["payload"]["error"][k] for k in ("code", "details")},
                                    "resolution_outcome": r["payload"]["obligation_resolution"]["outcome"],
                                    "signature_ok": signature_ok(r)}
    if case == "check03":
        out["check03"] = "pass" if run.path == "pending" else "fail"
    if run.pending:
        out["pending"] = {"request_payload_hash_ok": run.pending["payload"]["args"]["request_payload_hash"] ==
                          payload_hash(req)}
        if case in ("approval", "assets"):
            run.required = inp.get("required_approvals", 1)
            for step in inp.get("approvals", []):
                approver = step.get("approver", REVIEWER_ID)
                dec = approval_decision_msg(run, step["at"], step.get("decision", "approved"), approver,
                                            step.get("payload_hash"), step.get("capabilities", [APPROVE]),
                                            step.get("approver_id"), step.get("correlation_id"),
                                            step.get("root_request_id"), step.get("tamper", False),
                                            step.get("alg", "EdDSA"))
                fixture_check(out, dec)
                tok = reviewer_token(step["at"], step.get("issuer", "https://as.acme.example"),
                                     step.get("scope", APPROVE), step.get("sub", approver),
                                     step.get("aud", EXECUTOR_ID), step.get("token_lifetime", 600),
                                     step.get("token_tamper", False), step.get("token_drop", ()))
                for kid in step.get("remove_keys", []):  # the approver's key leaves the published JWKS
                    run.directory.remove(kid)
                if step.get("queued"):  # received now, verified later (at the next processing instant)
                    run.receive_decision(dec, step["at"], tok)
                    continue
                err = run.approval(dec, step["at"], None, tok, step.get("verify_at"))
                out.setdefault("approval_errors", []).append(err)
            if inp.get("expire_at"):  # the deadline timer: Path 3 only while still pending (Actions §3.4)
                out.setdefault("approval_errors", []).extend(run.expire(inp["expire_at"]))
            out["admitted"] = len(run.approvers)
    if run.path == "executing" and inp.get("ack_only"):
        run.acknowledge()
        out["review_opened"] = run.review is not None
    if run.path == "executing" and inp.get("end_at"):
        run.execute(inp["end_at"], inp.get("outcome", "success"), inp.get("asynchronous", False))
        out["path"] = run.path
        out["terminal_ts"] = run.terminal["ts"]
        out["terminal_has_resolution"] = "obligation_resolution" in run.terminal["payload"]
        if run.ack:
            out["ack_opens_review"] = False  # the review is built only from the terminal result
        if inp.get("retrieve_at"):
            out["retrieval_accepted"] = accept_retrieved(run.terminal, rid)
            tampered = json.loads(json.dumps(run.terminal))
            tampered["payload"].setdefault("result", {})["status"] = "tampered"
            foreign = json.loads(json.dumps(run.terminal))
            foreign["correlation_id"] = foreign["root_request_id"] = "7a000000-0000-4000-8000-0000000000ff"
            out["tampered_accepted"] = accept_retrieved(tampered, rid)
            out["foreign_accepted"] = accept_retrieved(foreign, rid)
            # validly re-signed copies differing in one binding member only: the signature cannot catch them
            for member in ("correlation_id", "root_request_id"):
                other = json.loads(json.dumps(run.terminal))
                other[member] = "7a000000-0000-4000-8000-0000000000fe"
                sign(other, EXECUTOR_ID)
                out[f"resigned_foreign_{member}_accepted"] = accept_retrieved(other, rid)
            out["terminal_ts_after_retrieval"] = run.terminal["ts"]
    if run.review:
        rv = run.review
        for ev in inp.get("events", []):
            if ev["kind"] == "tick":
                rv.tick(ev["at"])
            else:
                dec = review_decision_msg(rv, ev["at"], ev.get("decision", "confirmed"), ev.get("reviewer", REVIEWER_ID),
                                          ev.get("result_hash"), tuple(ev.get("capabilities",
                                                                              ["arsiaprotocol.oversight.approve"])),
                                          ev.get("tamper", False))
                fixture_check(out, dec)
                tok = reviewer_token(ev["at"], ev.get("issuer", "https://as.acme.example"),
                                     ev.get("scope", "arsiaprotocol.oversight.approve"), ev.get("reviewer", REVIEWER_ID))
                err, _ = rv.receive(dec, ev["at"], tok, ev.get("verify_at"))
                out.setdefault("decision_errors", []).append(err)
        out["review"] = {"state": rv.state, "review_deadline": rv.review_deadline,
                         "notice_to": rv.notice["to"],
                         "overdue_to": sorted({m["to"] for m in run.messages
                                               if m["payload"]["type"] == "arsiaprotocol.oversight/review-overdue"}),
                         "overdue_recorded_at": [r["processed_at"] for r in run.records
                                                 if r["event_type"] == "review_overdue"],
                         "obligations": [{"mode": o["mode"], "deadline": o["deadline"]} for o in rv.obligations],
                         "escalations": [{k: e[k] for k in ("mode", "result", "attempts", "times")}
                                         for e in rv.escalations]}
    out["path"] = run.path
    out["remediation"] = run.remediation
    out["event_types"] = [r["event_type"] for r in run.records]
    out["evidence"] = [{k: r.get(k) for k in ("event_type", "from_agent", "verified_kid", "jwks_fetched_at",
                                              "processed_at")}
                       for r in run.records if r["from_agent"] != EXECUTOR_ID]
    out["rejections"] = [{k: r.get(k) for k in ("rejection_code", "correlation_id", "root_request_id", "verified_kid")}
                         for r in run.records if r["event_type"] == "decision_rejected"]
    out["message_intents"] = [m["intent"] for m in run.messages]
    out["records_unmodified"] = run.unmodified()
    if case == "assets":
        out["receipt_issued"] = False
        out["final_error"] = run.final_error["payload"]["error"] if getattr(run, "final_error", None) else None
    elif getattr(run, "final_error", None):
        out["final_error"] = run.final_error["payload"]["error"]
    out["emitted"], out["messages"] = run.records, run.messages
    return out


def r15(vectors):
    # F-1 equivalence: a descriptor `false` is no veto (Actions §3.7); the MIFID-II default demands prior approval
    r = execution_case({"case": "source", "compliance": {"profile": "MIFID-II"}, "high_risk_sender": True})
    check("R15 F-1: high-risk + MIFID-II default, descriptor false -> pending_approval", r["path"] == "pending")
    r = execution_case({"case": "source", "compliance": {"profile": "GDPR-STANDARD"}, "end_at": "2026-10-31T10:00:05.000Z"})
    check("R15 no source demands prior approval -> executed, resolution in terminal result",
          r["path"] == "completed" and r["terminal_has_resolution"] and "pending_approval" not in r["event_types"])
    # A-4 / C-09: one within_24h evidence event, review_overdue, then a late decision
    r = execution_case({"case": "review", "compliance": {"profile": "DSA-VLOP", "legal_basis": "legal_obligation"},
                        "end_at": "2026-10-31T10:00:05.000Z",
                        "events": [{"kind": "tick", "at": "2026-11-01T10:00:05.000Z"},
                                   {"kind": "decision", "at": "2026-11-01T12:00:00.000Z"}]})
    check("R15 C-09: within_24h overdue -> review_overdue + review_escalation, late decision completed_late",
          r["review"]["state"] == "completed_late" and r["event_types"][-3:] ==
          ["review_overdue", "review_escalation", "review_decision"] and r["records_unmodified"])
    # A-80: multi-approval expiry N + 4
    r = execution_case({"case": "approval", "descriptor_oversight": True, "compliance": {"profile": "GDPR-STANDARD"},
                        "required_approvals": 2, "approvals": [{"at": "2026-10-31T10:10:00.000Z"}],
                        "expire_at": "2026-10-31T11:00:00.000Z"})
    check("R15 A-80: multi-approval expiry with N=1 -> 5 records", r["event_types"] ==
          ["request", "pending_approval", "approval_decision", "approval_expired", "error"])
    # ASSETS-06: expiry gives the Path 3 error, no receipt
    r = execution_case({"case": "assets", "payload": {"type": "arsiaprotocol.assets/transfer-request",
                                                       "args": {"amount": "50000.00"}},
                        "compliance": {"profile": "MIFID-II", "human_oversight": "required_within_24h"},
                        "assessed_risk": 9, "capabilities": ["arsiaprotocol.assets.transfer.initiate"],
                        "approvals": [], "expire_at": "2026-10-31T11:00:00.000Z", "case_kind": "expiry"})
    check("R15 ASSETS-06: risk assessment source; expiry -> forbidden/expired, no receipt",
          "risk-assessment:arsiaprotocol.assets/transfer-request" in r["oversight"]["source_ids"]
          and r["final_error"]["details"]["oversight_decision"] == "expired" and r["receipt_issued"] is False)
    # escalation timing (Core §11.3 applied): backoff and Retry-After
    res, n, times = deliver_escalation(["service_unavailable", "service_unavailable", "accepted"],
                                       "2026-11-01T10:00:00.000Z")
    check("R15 escalation backoff 1 s, 2 s", (res, n, times) == ("delivered", 3, ["2026-11-01T10:00:00.000Z",
          "2026-11-01T10:00:01.000Z", "2026-11-01T10:00:03.000Z"]))
    res, n, times = deliver_escalation([{"code": "rate_limited", "retry_after": 10}, "accepted"],
                                       "2026-11-01T10:00:00.000Z")
    check("R15 rate_limited waits Retry-After, not the backoff", times[1] == "2026-11-01T10:00:10.000Z")
    check("R15 escalation exhausted after 3 retries", deliver_escalation(["timeout"] * 9, "2026-11-01T10:00:00.000Z")[:2]
          == ("failed", 4))
    check("R15 executor source prefixes == Core §4.3.10.2", all(
        any(s["source"]["id"].startswith(p) for p in EXECUTOR_SOURCE_PREFIXES)
        for s in executor_sources("a.b/c", make_descriptor("a.b/c", True),
                                  {"requirement": "required_before_execution", "capabilities": ["test.unit"],
                                   "policy": TEST_CLAIM_POLICY}, ["test.unit"],
                                  {"action_id": "a.b/c", "assessed_risk_level": 8, "threshold": 7})))
    # both post-execution modes: unreachable with this cycle's sources (executor-policy demands prior approval
    # only), so the composition of Actions §3.9.2 is unit-checked with the modes injected
    run = Run(make_request("7a000000-0000-4000-8000-0000000000b2", {"type": "com.acme.test/run", "args": {}},
                           {"profile": "GDPR-STANDARD", "human_oversight": "required_within_24h"}),
              make_descriptor("com.acme.test/run", period="P2D"), "2026-10-31T10:00:00.000Z")
    run.modes = ["required_post_execution", "required_within_24h"]
    run.execute("2026-10-31T10:00:05.000Z")
    check("R15 both post modes: one obligation each, review_deadline = earliest (within 24 h)",
          [(o["mode"], o["deadline"]) for o in run.review.obligations] ==
          [("required_within_24h", "2026-11-01T10:00:05.000Z"), ("required_post_execution", "2026-11-02T10:00:05.000Z")]
          and run.review.review_deadline == "2026-11-01T10:00:05.000Z")
    run.review.tick("2026-11-02T10:00:05.000Z")
    check("R15 both post modes: each obligation becomes overdue at its own deadline",
          [r["review_mode"] for r in run.records if r["event_type"] == "review_overdue"] ==
          ["required_within_24h", "required_post_execution"])
    with_meta = [v for v in vectors if v.get("test_metadata", {}).get("scenario") == "execution"]
    for v in with_meta:
        got = execution_case(v["test_metadata"]["input"])
        miss = subset_match(v["test_metadata"]["expect"], got)
        check(f"R15 {v['id']} result matches its stated expectation", not miss, ", ".join(miss), executed=[v["id"]])
        errs = [e for r in got["emitted"] for e in schema_errors(r, "arsia-audit-record.schema.json")]
        errs += [e for m in got["messages"] for e in schema_errors(m, "arsia-message.schema.json")]
        check(f"R15 {v['id']} emitted messages and records are schema-valid", not errs, "; ".join(errs[:3]))
        check(f"R15 {v['id']} no record modified after emission", got.get("records_unmodified", True))
        check(f"R15 {v['id']} constructed decisions are schema-valid fixtures", not got.get("fixture_errors"),
              "; ".join(got.get("fixture_errors", [])[:2]))
        # A-58 (Core §5.2, State §7.1): the verification evidence is on the records of received messages whose
        # signature verified, with the sender's kid and a fetch not later than the processing; never on records
        # of messages the executor emitted
        recs = got["emitted"]
        bad = [r["event_type"] for r in recs if r["from_agent"] == EXECUTOR_ID
               and ("verified_kid" in r or "jwks_fetched_at" in r)]
        bad += [r["event_type"] for r in recs if r["from_agent"] != EXECUTOR_ID and r["event_type"] != "decision_rejected"
                and (r.get("verified_kid") != r["from_agent"] + "#key-1"
                     or iso(r["jwks_fetched_at"]) > iso(r["processed_at"]))]
        check(f"R15 {v['id']} verified_kid/jwks_fetched_at exactly on received, verified messages", not bad, str(bad))
        if "admitted" in got:  # A-57: a rejected decision is never a Record 3 (Actions §3.5, §3.6)
            check(f"R15 {v['id']} Record 3 count == decisions admitted",
                  got["event_types"].count("approval_decision") == got["admitted"])
    check("R15 execution vectors present", len(with_meta) > 0, str(len(with_meta)))


# ------------------------------------------------- R11 issuer trust (Core §6.5)
TRUST = {
    "https://as.acme.example": {
        "key_origin": "https://as.acme.example/.well-known/jwks.json",
        "audiences": {"agent:acme.billing", "agent:acme.payments", "agent:acme.executor"},
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
        self.keys = {}
        self.fetched_at = None
        self.max_age = None

    def _refresh(self, now):
        kids, max_age = self.fetch()
        self.keys = dict(kids) if isinstance(kids, dict) else {}  # kid -> public key hex, when published
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
            self.keys.pop(kid, None)


class Publisher:
    """The sender's published JWKS, mutable over time."""

    def __init__(self, kids, max_age=3600):
        self.kids = dict(kids) if isinstance(kids, dict) else set(kids)  # a dict maps kid -> public key hex
        self.max_age, self.up = max_age, True

    def __call__(self):
        if not self.up:
            raise ConnectionError("JWKS unreachable")
        return (dict(self.kids) if isinstance(self.kids, dict) else set(self.kids)), self.max_age


def verify_signed_jwks(msg, caches, now):
    """Core §5.2 with published key material: the kid belongs to `from`, it is resolved through that sender's
    cache at `now` (refresh rules), and the signature verifies under the cached key, Draft-02 signing input."""
    sys.path.insert(0, "scripts")
    import validate_vectors as vv
    from regen_v2 import signing_input_v2
    sec = msg.get("security") or {}
    kid = sec.get("kid", "")
    cache = caches.get(kid.split("#", 1)[0])
    if cache is None or kid.split("#", 1)[0] != msg.get("from") or not cache.accept(kid, now):
        return False, None, None
    try:
        vv._verify_signature(sec.get("alg"), bytes.fromhex(cache.keys[kid]), vv._base64url_decode(sec.get("sig", "")),
                             signing_input_v2(msg))
    except Exception:
        return False, None, None
    return True, kid, _at(cache.fetched_at)


def process_key_revocation(event, caches, now):
    """Identity §2.5: the event is acted on only once authenticated — payload.data valid against its schema
    (else invalid_request); revoked_kid belongs to `from` and differs from the signing key, and the signature
    verifies with a published key of `from` (else unauthorized). Only then is the named key invalidated, at
    once, whatever effective_at states. Cache updates caused by resolving the signing key are ordinary JWKS
    refreshes, not effects of the event. Returns {result, code, invalidated}."""
    payload = event.get("payload") or {}
    data = payload.get("data")
    if payload.get("type") != "arsiaprotocol.identity/key-revocation" or not isinstance(data, dict) \
            or schema_errors(data, "arsia-key-revocation.schema.json"):
        return {"result": "rejected", "code": "invalid_request", "invalidated": None}
    sender, signer, revoked = event.get("from"), (event.get("security") or {}).get("kid", ""), data["revoked_kid"]
    if signer == revoked or revoked.split("#", 1)[0] != sender:
        return {"result": "rejected", "code": "unauthorized", "invalidated": None}
    if not verify_signed_jwks(event, caches, now)[0]:
        return {"result": "rejected", "code": "unauthorized", "invalidated": None}
    caches[sender].revocation_event(revoked)
    return {"result": "accepted", "code": None, "invalidated": revoked}


def revocation_case(inp, message):
    """Runs a `revocation` scenario (Core §5.2 Verification Caching; Identity §2.5): the senders' published keys,
    one recipient cache per sender, steps in time order. `message` is the vector's own signed message (a
    key-revocation event, or a message signed by the key under revocation). Returns one result per step."""
    pubs = {a: Publisher(dict(c["keys"]), c.get("max_age", JWKS_CEILING)) for a, c in inp["publishers"].items()}
    caches = {a: JwksCache(p) for a, p in pubs.items()}
    out = []
    for st in inp["steps"]:
        now, op = _epoch(st["at"]), st["op"]
        agent = st.get("agent") or st.get("kid", "").split("#", 1)[0]
        if op == "fetch":
            caches[agent]._refresh(now)
            out.append({"op": op})
        elif op == "remove":
            pubs[agent].kids.pop(st["kid"])
            out.append({"op": op})
        elif op == "publish":
            pubs[agent].kids[st["kid"]] = st["public_key_hex"]
            out.append({"op": op})
        elif op == "receive":  # the message is received; it is verified at a later step
            out.append({"op": op})
        elif op == "verify":  # a later message signed with this kid
            ok = caches[agent].accept(st["kid"], now)
            out.append({"op": op, "kid": st["kid"], "accepted": ok,
                        "jwks_fetched_at": _at(caches[agent].fetched_at) if ok else None})
        elif op == "verify_message":
            ok, _kid, fetched = verify_signed_jwks(message, caches, now)
            out.append({"op": op, "accepted": ok, "jwks_fetched_at": fetched})
        elif op == "event":
            res = process_key_revocation(message, caches, now)
            out.append(dict(res, op=op, sender_jwks_fetched_at=_at(caches[message["from"]].fetched_at)
                            if caches.get(message["from"]) and caches[message["from"]].fetched_at is not None
                            else None))
        else:
            raise ValueError(f"unknown revocation step {op}")
    return out


def r13(vectors=()):
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
    # A-58: revocation vectors (scenario `revocation`), with real signed messages and published keys
    sc = [v for v in vectors if v.get("test_metadata", {}).get("scenario") == "revocation"]
    check("R13 revocation scenario vectors present (event accepted and rejected)",
          {s.get("result") for v in sc for s in v["test_metadata"]["expect"]["steps"] if s.get("op") == "event"}
          >= {"accepted", "rejected"}, str(len(sc)))
    for v in sc:
        got = revocation_case(v["test_metadata"]["input"], v["message"])
        miss = [f"step {i}{m}" for i, (e, g) in enumerate(zip(v["test_metadata"]["expect"]["steps"], got))
                for m in subset_match(e, g)]
        if len(got) != len(v["test_metadata"]["expect"]["steps"]):
            miss.append("step count")
        check(f"R13 {v['id']} steps match their stated expectation", not miss, ", ".join(miss), executed=[v["id"]])


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

    def expect_fail(name, entries, hd, reason, executed=()):
        ok, why, _ = verify_chain(entries, hd)
        check(name, ok is False and why == reason, f"got ({ok}, {why})", executed=executed)

    ok, why, rep_ = verify_chain(chain, head)
    check("R14 (a) valid chain of 4 records + 1 tombstone verifies (ITV-592..596)",
          ok and rep_["tombstones"] == [4] and rep_["beyond_head"] == [], f"{why} {rep_}", executed=seq_ids)
    one = dict(by_id["ITV-95"]["data"])
    check("R14 (a) single-entry chain ITV-95 verifies",
          verify_chain([one], (one["chain_id"], 1, one["hash_chain"]))[0], executed=["ITV-95"])
    tampered = sub(2, "ITV-597")
    expect_fail("R14 (b) approver_id changed (ITV-597) rejected: chain value mismatch", tampered, head,
                "chain value mismatch", executed=["ITV-597"] + seq_ids)
    old = lambda r: __import__("hashlib").sha256((r["record_id"] + r["payload_hash"]).encode()).hexdigest()
    check("R14 (b) pre-DR-5 construction blind to the same change (A-8 reproduction)",
          old(chain[1]) == old(tampered[1]) and chain[1]["approver_id"] != tampered[1]["approver_id"])
    expect_fail("R14 (c) mid-chain record removed rejected: position gap",
                [e for e in chain if e.get("chain_seq") != 3], head, "position gap")
    swapped = [dict(e) for e in chain]
    swapped[0]["chain_seq"], swapped[1]["chain_seq"] = 2, 1
    expect_fail("R14 (d) two records reordered rejected: chain value mismatch", swapped, head,
                "chain value mismatch")
    expect_fail("R14 (e) foreign chain_id (ITV-598) rejected", sub(3, "ITV-598"), head, "foreign chain_id",
                executed=["ITV-598"] + seq_ids)
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
                "tombstone previous value mismatch", executed=["ITV-599"] + seq_ids)
    expect_fail("R14 (h) head value mismatch rejected", chain, (head[0], 5, "0" * 64), "head mismatch")
    ok, why, rep_ = verify_chain(chain, (head[0], 3, chain[2]["hash_chain"]))
    check("R14 entries beyond the held head are reported, not rejected",
          ok and rep_["beyond_head"] == [4, 5], f"{why} {rep_}")
    fmt = [dict(e) for e in chain]
    fmt[0]["chain_format"] = 2
    expect_fail("R14 unsupported chain_format rejected", fmt, head, "unsupported chain_format")


# ------------------------------------------- R16 message timing (Core §4.1.3, §4.2.2, §8.3)
DEFAULT_SKEW = 300  # Core §8.3 default tolerance, seconds
TS_POSTURE = ("ARSIA-Core.md", "§8.3", "MAY")  # the option to reject a ts outside the tolerance


def skew_tolerance(message):
    """Core §8.3: the declared profile's clock_skew_seconds when it defines one, else 300 s."""
    name = (message.get("compliance") or {}).get("profile")
    skew = PROFILES.get(name, {}).get("defaults", {}).get("clock_skew_seconds") if name else None
    return (skew, f"profile:{name}") if skew is not None else (DEFAULT_SKEW, "default")


def timing(message, recipient_time, posture=None):
    """Temporal verdict at the recipient's clock, kept apart from the global one. `expired` (§4.2.2)
    is a MUST and always a cause; a ts outside the tolerance (§4.1.3) is a cause only for a recipient
    that takes the §8.3 MAY. Compliance diagnostics of the reference resolver join the global causes."""
    tol, source = skew_tolerance(message)
    now = iso(recipient_time)
    offset = (iso(message["ts"]) - now).total_seconds()
    expired = "expires_at" in message and now > iso(message["expires_at"]) + dt.timedelta(seconds=tol)
    within = abs(offset) <= tol
    takes_may = posture is not None and (posture["spec"], posture["section"], posture["basis"]) == TS_POSTURE
    causes = (["expired"] if expired else []) + (["ts_outside_tolerance"] if not within and takes_may else [])
    if isinstance(message.get("compliance"), dict):
        res = resolve_obligations(message["intent"], message["compliance"], None, message["ts"])
        causes += [c["diagnostic"] for c in res.get("conflicts", [])]
    return {"tolerance_seconds": tol, "tolerance_source": source, "ts_offset_seconds": int(offset),
            "ts_within_tolerance": within, "expired": expired,
            "outcome": "rejected" if causes else "accepted", "causes": causes}


def r16(vectors):
    timed = [v for v in vectors if v.get("test_metadata", {}).get("scenario") == "timing"]
    check("R16 timing vectors present (ITV-408/411/440/545/546/547; clean profile case ITV-709/710, INV-171, A-62; "
          "expiry ITV-498/518, Draft-01.1 port)",
          sorted(v["id"] for v in timed) == ["INV-171", "ITV-408", "ITV-411", "ITV-440", "ITV-498", "ITV-518", "ITV-545",
                                             "ITV-546", "ITV-547", "ITV-709", "ITV-710"])
    for v in timed:
        got = timing(v["message"], v["test_metadata"]["input"]["recipient_time"], v.get("posture"))
        miss = subset_match(v["test_metadata"]["expect"], got)
        check(f"R16 {v['id']} result matches its stated expectation", not miss, ", ".join(miss), executed=[v["id"]])
        rejected = got["outcome"] == "rejected"
        check(f"R16 {v['id']} outcome agrees with the vector's valid/expected_error",
              rejected is (v["valid"] is False) and (not rejected or v["expected_error"] == "invalid_request"))
        if v.get("posture"):
            alt = timing(v["message"], v["test_metadata"]["input"]["recipient_time"], None)
            check(f"R16 {v['id']} expectation rests on the MAY: accepted without the posture", alt["outcome"] == "accepted")
    v546 = next(v for v in timed if v["id"] == "ITV-546")
    got = timing(v546["message"], v546["test_metadata"]["input"]["recipient_time"], v546.get("posture"))
    check("R16 ITV-546 on time (90 s within 120 s): the clock is no cause of its rejection",
          got["ts_within_tolerance"] and "ts_outside_tolerance" not in got["causes"]
          and got["causes"] == ["missing_legal_basis", "insufficient_retention"])
    m = {"ts": "2026-05-01T11:58:00.000Z", "intent": "event", "compliance": {"profile": "MIFID-II"}}
    check("R16 profile tolerance is used, not the default (MIFID-II 60 s)", timing(m, "2026-05-01T12:00:00.000Z")["tolerance_seconds"] == 60)
    m = {"ts": "2026-05-01T12:00:00.000Z", "intent": "event", "expires_at": "2026-05-01T12:00:00.000Z"}
    check("R16 expiry honours the tolerance: 300 s after expires_at is not expired",
          not timing(m, "2026-05-01T12:05:00.000Z")["expired"] and timing(m, "2026-05-01T12:05:00.001Z")["expired"])


# ------------------------------------------- R17 state generations (State §2.1.14, §2.4, §3.1.2, §3.2)
class StateStore:
    """Reference store for one owner: generations, versions, preconditions, snapshot, PURGE repetition,
    retention override. Entries are kept per (key, generation); `held` is the information the
    implementation still holds; `retained_until` is created_at + the effective retention resolved at
    creation (None when no retention period applies)."""

    def __init__(self, owner="agent:acme.billing"):
        self.owner = owner
        self.gens = {}         # key -> {generation: {"versions": [...], "created_at", "deleted_at", "purged_at"}}
        self.top = {}          # key -> highest generation ever assigned (kept while anything of the key is held)
        self.records = []      # audit records (state fields only)
        self.idem = {}         # idempotency key -> stored response
        self.purges = {}       # key -> (purged_at, latest generation covered) of the last purge

    def live(self, key):
        g = self.top.get(key)
        e = self.gens.get(key, {}).get(g)
        if e is None or e["deleted_at"] or e["purged_at"]:
            return None
        return g, e

    def held(self, key):
        return bool(self.gens.get(key)) or key in self.purges or any(r["key"] == key for r in self.records)

    def entry(self, key, g, e, ver, deleted=None):
        out = {"key": key, "value": ver["value"], "owner_agent_id": self.owner, "scope": key.split("/")[1],
               "created_at": e["created_at"], "updated_at": ver["at"], "pii_classification": "none",
               "generation": g, "version": ver["version"]}
        if deleted is not None:
            out["deleted"] = deleted
        return out

    def set(self, key, value, at, actor=None, expected_version=None, expected_generation=None, retention=None):
        actor = actor or self.owner
        cur = self.live(key)
        stated = {k: v for k, v in (("expected_generation", expected_generation),
                                    ("expected_version", expected_version)) if v is not None}
        if stated:
            if cur is None:
                return {"error": "conflict", "details": dict({"entry_live": False}, **stated)}
            g, e = cur
            last = e["versions"][-1]
            if (expected_version is not None and expected_version != last["version"]) or \
               (expected_generation is not None and expected_generation != g):
                return {"error": "conflict", "details": dict({"current_generation": g, "current_version": last["version"],
                                                              "updated_at": last["at"], "updated_by": last["actor"]}, **stated)}
        if cur is None:
            g = (self.top.get(key, 0) if self.held(key) else 0) + 1
            self.top[key] = g
            e = {"versions": [], "created_at": at, "deleted_at": None, "purged_at": None,
                 "retained_until": stamp(add_duration(iso(at), retention)) if retention else None}
            self.gens.setdefault(key, {})[g] = e
        else:
            g, e = cur
        ver = {"version": len(e["versions"]) + 1, "value": value, "at": at, "actor": actor}
        e["versions"].append(ver)
        self.records.append({"event_type": "state_set", "key": key, "owner_agent_id": self.owner,
                             "actor_agent_id": actor, "generation": g, "version": ver["version"], "timestamp": at})
        return {"result": self.entry(key, g, e, ver)}

    def delete(self, key, at, actor=None):
        cur = self.live(key)
        if cur is None:
            return {"result": None}
        g, e = cur
        e["deleted_at"] = at
        self.records.append({"event_type": "state_delete", "key": key, "owner_agent_id": self.owner,
                             "actor_agent_id": actor or self.owner, "generation": g,
                             "version": e["versions"][-1]["version"], "timestamp": at})
        return {"result": {"deleted": True, "key": key}}

    def purge(self, key, at, idem, override=None):
        if idem in self.idem:                                   # retransmission (Core §10.3)
            return self.idem[idem]
        latest = self.top.get(key)
        last = self.purges.get(key)
        if last and last[1] == latest:                          # no SET created an entry since that purge
            out = {"result": {"purged": True, "key": key, "purged_at": last[0]}}
        else:
            # State §3.2.2: generations whose values this PURGE removes, from stored state, live or not
            affected = [e for e in self.gens.get(key, {}).values() if not e["purged_at"]]
            instants = [e["retained_until"] for e in affected if e["retained_until"]]
            until = max(instants) if instants else None
            within = until is not None and at < until
            if within and override is None:
                out = {"error": "invalid_request", "details": {"within_retention": True, "entry_retained_until": until}}
                self.idem[idem] = out
                return out
            for e in affected:
                e["purged_at"] = at
                for ver in e["versions"]:
                    ver["value"] = None
            self.purges[key] = (at, latest)
            rec = {"event_type": "state_purge", "key": key, "owner_agent_id": self.owner,
                   "initiator_agent_id": self.owner, "generation": latest, "purged_at": at,
                   "within_retention": within, "entry_retained_until": until}
            if override is not None:
                rec["retention_override"] = override
            self.records.append(rec)
            out = {"result": {"purged": True, "key": key, "purged_at": at}}
        self.idem[idem] = out
        return out

    def snapshot(self, as_of):
        out = []
        for key in sorted(self.gens):
            for g in sorted(self.gens[key]):
                e = self.gens[key][g]
                vs = [v for v in e["versions"] if v["at"] <= as_of]
                if not vs:
                    continue
                deleted = bool(e["deleted_at"] and e["deleted_at"] <= as_of)
                ent = self.entry(key, g, e, vs[-1], deleted)
                if deleted:
                    ent["updated_at"] = e["deleted_at"]
                out.append(ent)
        return out

    def remove_generation(self, key, g):
        self.gens[key].pop(g, None)
        self.records = [r for r in self.records if not (r["key"] == key and r["generation"] == g)]

    def remove_all(self, key):
        self.gens.pop(key, None)
        self.purges.pop(key, None)
        self.records = [r for r in self.records if r["key"] != key]

    def history(self, key):
        return [(key, g, v["version"]) for g in sorted(self.gens.get(key, {})) for v in self.gens[key][g]["versions"]]


def state_case(inp):
    """Runs a runtime vector's `state` scenario; returns the last operation's result and the audit records."""
    st = StateStore(inp.get("owner", "agent:acme.billing"))
    out = None
    for op in inp["ops"]:
        kind = op["op"]
        if kind == "set":
            out = st.set(inp["key"], op["value"], op["at"], op.get("actor"), op.get("expected_version"),
                         op.get("expected_generation"), op.get("retention"))
        elif kind == "delete":
            out = st.delete(inp["key"], op["at"])
        elif kind == "purge":
            out = st.purge(inp["key"], op["at"], op["idem"], op.get("override"))
        elif kind == "snapshot":
            out = {"result": st.snapshot(op["as_of"])}
    return {"last": out, "records": st.records, "history": [list(t) for t in st.history(inp["key"])]}


STATE_PROJECTION = {"state_set": ("key", "owner_agent_id", "actor_agent_id", "generation", "version", "timestamp"),
                    "state_purge": ("key", "owner_agent_id", "initiator_agent_id", "generation", "purged_at",
                                    "within_retention", "entry_retained_until", "retention_override")}
R17_STATE_IDS = ["ITV-677", "ITV-678", "ITV-679", "ITV-680", "ITV-681"]
R18_STATE_IDS = ["ITV-683", "ITV-684", "ITV-685", "ITV-686", "ITV-687"]


def state_vector_data_matches(v, got):
    """The vector's data is what the reference store produces for the stated operation sequence."""
    body = v.get("data") or v.get("message")
    if v.get("schema_ref") == "arsia-state-operations.schema.json":
        return body["result"]["entries"] == got["last"]["result"]
    if "payload" in body:
        return body["payload"]["error"]["code"] == got["last"]["error"] and \
            body["payload"]["error"]["details"] == got["last"]["details"]
    rec = got["records"][-1]
    fields = STATE_PROJECTION[body["event_type"]]
    return body["event_type"] == rec["event_type"] and all(body.get(f) == rec.get(f) for f in fields)


def r17(vectors):
    K = "agent:acme.billing/agent/profile"
    t = lambda h: f"2026-04-15T{h}:00:00.000Z"
    st = StateStore()
    st.set(K, "v1", t("09")); st.set(K, "v2", t("10")); st.delete(K, t("11"))
    rec = st.set(K, "w1", t("12"))["result"]
    check("R17 (a) recreation after DELETE: generation 2, version 1, own created_at",
          (rec["generation"], rec["version"], rec["created_at"]) == (2, 1, t("12")))
    check("R17 (a) recreation leaves the first generation's created_at unchanged (A-88)",
          st.gens[K][1]["created_at"] == t("09"))
    hist = st.history(K)
    check("R17 (b) (key, generation, version) unique while version numbers repeat across generations",
          len(set(hist)) == len(hist) == 3 and [v for _, _, v in hist].count(1) == 2)
    trip = [(r["key"], r["generation"], r["version"]) for r in st.records if r["event_type"] == "state_set"]
    check("R17 (b) state_set records: triples unique, (key, version) pairs repeat",
          len(set(trip)) == len(trip) and len({(k, v) for k, _, v in trip}) < len(trip))
    before = st.snapshot("2026-04-15T10:30:00.000Z")
    check("R17 (c) snapshot between update and DELETE returns generation 1 at version 2",
          [(e["generation"], e["version"], e["value"]) for e in before] == [(1, 2, "v2")])
    after = st.snapshot(t("13"))
    check("R17 (c) snapshot after recreation returns both generations, distinguished by generation",
          [(e["generation"], e["version"], e["deleted"]) for e in after] == [(1, 2, True), (2, 1, False)])

    # (d)-(g) preconditions across generations
    st = StateStore()
    st.set(K, "a", t("09")); st.delete(K, t("10")); st.set(K, "b", t("11"))
    aba = st.set(K, "stale", t("12"), expected_version=1, expected_generation=1)
    check("R17 (d) ABA: expected_generation + expected_version rejected with the live details",
          aba == {"error": "conflict", "details": {"current_generation": 2, "current_version": 1, "updated_at": t("11"),
                                                   "updated_by": st.owner, "expected_generation": 1, "expected_version": 1}})
    check("R17 (e) declared limit: expected_version alone does not detect the recreation",
          "result" in st.set(K, "stale", t("13"), expected_version=1))
    check("R17 (f) declared limit: expected_generation alone accepts an update within the generation",
          "result" in st.set(K, "c", t("14"), expected_generation=2))
    st.delete(K, t("15"))
    gone = st.set(K, "x", t("16"), expected_version=3)
    fresh = StateStore().set("agent:acme.billing/agent/never", "x", t("16"), expected_version=3)
    check("R17 (g) no live entry: conflict entry_live false, no current_* member",
          gone == {"error": "conflict", "details": {"entry_live": False, "expected_version": 3}})
    check("R17 (g) deleted key and key never written give identical details", gone == fresh)
    check("R17 (g) the rejected conditional SET creates no entry", st.live(K) is None and st.top[K] == 2)

    # (h) numbering
    st = StateStore()
    st.set(K, "a", t("09")); st.purge(K, t("10"), "p1")
    check("R17 (h) numbering continues after PURGE", st.set(K, "b", t("11"))["result"]["generation"] == 2)
    st = StateStore()
    for i, h in enumerate(("09", "10", "11")):
        st.set(K, i, t(h)); st.delete(K, t(h).replace(":00:00", ":30:00"))
    st.remove_generation(K, 3); st.remove_generation(K, 1)
    check("R17 (h) partial removal (g3 removed, g2 held): next generation is 4, the sequence does not rewind",
          st.set(K, "d", t("12"))["result"]["generation"] == 4)
    st = StateStore()
    st.set(K, "a", t("09")); st.delete(K, t("10"))
    st.records = []  # audit trail removed; the logically deleted entry is still stored
    check("R17 (h) a logically deleted entry still stored keeps the sequence",
          st.set(K, "b", t("11"))["result"]["generation"] == 2)
    st.remove_all(K)
    check("R17 (h) declared limit: after every information of the key is removed the sequence restarts at 1",
          st.set(K, "c", t("12"))["result"]["generation"] == 1)

    # (i) PURGE repetition
    st = StateStore()
    st.set(K, "a", t("09"))
    p1 = st.purge(K, t("10"), "k1")
    check("R17 (i) retransmission with the same idempotency key: stored response, no new record",
          st.purge(K, "2026-04-15T10:05:00.000Z", "k1") == p1 and len([r for r in st.records if r["event_type"] == "state_purge"]) == 1)
    again = st.purge(K, t("11"), "k2")
    check("R17 (i) repeated PURGE without a later write: same purged_at, no new record",
          again["result"]["purged_at"] == t("10") and len([r for r in st.records if r["event_type"] == "state_purge"]) == 1)
    st.set(K, "b", t("12"))
    p3 = st.purge(K, t("13"), "k3")
    purges = [r for r in st.records if r["event_type"] == "state_purge"]
    check("R17 (i) PURGE after a later write: new purge, new record carrying generation 2",
          p3["result"]["purged_at"] == t("13") and len(purges) == 2 and purges[-1]["generation"] == 2)

    # (j) scenario vectors
    sv = [v for v in vectors if v.get("test_metadata", {}).get("scenario") == "state" and v["id"] in R17_STATE_IDS]
    check("R17 state vectors present (ITV-677..681)", sorted(v["id"] for v in sv) == R17_STATE_IDS)
    for v in sv:
        got = state_case(v["test_metadata"]["input"])
        miss = subset_match(v["test_metadata"]["expect"], got)
        check(f"R17 {v['id']} result matches its stated expectation", not miss, ", ".join(miss), executed=[v["id"]])
        check(f"R17 {v['id']} data is what the reference store produces", state_vector_data_matches(v, got))


def full_purge_record(rec, message, at, pii_classification, operator_id=RECEIVER_OPERATOR):
    """State §7.1 record for a store `state_purge` entry, completed with the purged entry's
    classification and the PURGE message's resolution. Its retention fields come from that
    resolution (§7.3), never from the removed values or the retention override."""
    res = resolve_obligations(message["intent"], message.get("compliance"), anchor=at)
    return audit_record(message, res, at, operator_id, "state_purge", obligation_resolution=res,
                        pii_classification=pii_classification,
                        **{k: v for k, v in rec.items() if k != "event_type"})


def r18(vectors):
    # (a) P1827D against P5Y from the same anchor over a 400-year Gregorian cycle (State §6.3)
    base, dist = dt.datetime(2000, 1, 1), {}
    for i in range(146097):
        a = base + dt.timedelta(days=i)
        d = (add_duration(a, "P1827D") - add_duration(a, "P5Y")).days
        dist[d] = dist.get(d, 0) + 1
    check("R18 (a) P1827D never shorter than P5Y; exceeds it by 0/1/2 days for 34,310/108,499/3,288 anchors",
          dist == {0: 34310, 1: 108499, 2: 3288}, str(dist))
    a = iso("2097-03-01T00:00:00.000Z")
    check("R18 (a) 2097-03-01: P5Y -> 2102-03-01, P1827D -> 2102-03-03 (2100 is not a leap year)",
          (add_duration(a, "P5Y"), add_duration(a, "P1827D"))
          == (iso("2102-03-01T00:00:00.000Z"), iso("2102-03-03T00:00:00.000Z")))

    K = "agent:acme.billing/agent/record"
    OVR = {"reason": "gdpr_art17_erasure", "determination_ref": "DPO-2026-0042"}
    T0, T1 = "2026-01-15T09:00:00.000Z", "2026-02-14T09:00:00.000Z"  # T1 = T0 + 30 days
    until = stamp(add_duration(iso(T0), "P1827D"))
    purges = lambda st: [r for r in st.records if r["event_type"] == "state_purge"]

    # (b)-(c) live entry within retention
    st = StateStore()
    st.set(K, "v", T0, retention="P1827D")
    check("R18 (b) within retention without override: invalid_request with the details of State §8.4",
          st.purge(K, T1, "k1") == {"error": "invalid_request",
                                     "details": {"within_retention": True, "entry_retained_until": until}})
    check("R18 (b) the rejected PURGE removes nothing and records nothing",
          st.gens[K][1]["versions"][0]["value"] == "v" and not st.gens[K][1]["purged_at"] and not purges(st))
    out = st.purge(K, T1, "k2", OVR)
    rec = purges(st)[-1] if purges(st) else {}
    check("R18 (c) with retention_override: purged; the record carries within_retention, entry_retained_until, override",
          "result" in out and st.gens[K][1]["versions"][0]["value"] is None
          and (rec.get("within_retention"), rec.get("entry_retained_until"), rec.get("retention_override")) == (True, until, OVR))

    # (d) no live entry
    st = StateStore()
    st.set(K, "v", T0, retention="P1827D"); st.delete(K, "2026-01-20T09:00:00.000Z")
    check("R18 (d) no live entry: a deleted generation within retention still requires the override",
          st.purge(K, T1, "k1").get("error") == "invalid_request" and "result" in st.purge(K, T1, "k2", OVR))

    # (e) the latest instant over every affected generation
    st = StateStore()
    st.set(K, "old", "2020-01-10T09:00:00.000Z", retention="P10Y"); st.delete(K, "2020-02-10T09:00:00.000Z")
    st.set(K, "new", "2020-03-10T09:00:00.000Z", retention="P6M")
    check("R18 (e) entry_retained_until is the latest instant (g1 deleted P10Y, g2 live P6M expired)",
          st.purge(K, T1, "k1") == {"error": "invalid_request", "details": {
              "within_retention": True, "entry_retained_until": "2030-01-10T09:00:00.000Z"}})

    # (f) beyond retention; (g) no retention period
    st = StateStore()
    st.set(K, "v", "2020-01-10T09:00:00.000Z", retention="P6M"); st.purge(K, T1, "k1")
    rec = purges(st)[-1] if purges(st) else {}
    check("R18 (f) values beyond retention: no override needed, within_retention false, instant in the past",
          (rec.get("within_retention"), rec.get("entry_retained_until")) == (False, "2020-07-10T09:00:00.000Z")
          and "retention_override" not in rec)
    st = StateStore()
    st.set(K, "v", T0); st.purge(K, T1, "k1")
    rec = purges(st)[-1] if purges(st) else {}
    check("R18 (g) no retention period: entry_retained_until null, within_retention false",
          (rec.get("within_retention"), rec.get("entry_retained_until")) == (False, None) and "entry_retained_until" in rec)

    # (h) a physically removed generation holds no value
    st = StateStore()
    st.set(K, "old", T0, retention="P10Y"); st.delete(K, "2026-01-20T09:00:00.000Z")
    st.set(K, "new", "2026-01-25T09:00:00.000Z"); st.remove_generation(K, 1)
    out = st.purge(K, T1, "k1")
    rec = purges(st)[-1] if purges(st) else {}
    check("R18 (h) a physically removed generation does not enter the evaluation",
          "result" in out and (rec.get("within_retention"), rec.get("entry_retained_until")) == (False, None))

    # (i) the record's own retention (State §7.3), against an independent expectation
    def own(created, retention, override):
        s = StateStore()
        s.set(K, "v", created, retention=retention)
        args = dict({"key": K}, **({"retention_override": override} if override else {}))
        msg = {"v": "2.0", "id": "b0000018-0001-4001-8001-0000000000" + ("01" if override else "00"),
               "ts": T1, "from": s.owner, "to": "agent:arsialabs.demo.state-store", "intent": "request",
               "capabilities": ["arsiaprotocol.state.purge"], "compliance": {"profile": "MIFID-II"},
               "payload": {"type": "arsiaprotocol.state/purge", "args": args}}
        s.purge(K, T1, "k1", override)
        pii = s.entry(K, 1, s.gens[K][1], s.gens[K][1]["versions"][-1])["pii_classification"]
        full = full_purge_record(purges(s)[-1], msg, T1, pii)
        return schema_errors(full, "arsia-audit-record.schema.json"), \
            {f: full.get(f) for f in ("effective_retention", "retention_anchor", "retained_until")}
    want = {"effective_retention": "P1827D", "retention_anchor": T1,
            "retained_until": stamp(iso(T1) + dt.timedelta(days=1827))}
    for name, created, override in (("expired values, no override", "2020-01-10T09:00:00.000Z", None),
                                    ("expired values, override", "2020-01-10T09:00:00.000Z", OVR),
                                    ("values within retention, override", T0, OVR)):
        errs, got = own(created, "P1827D", override)
        check(f"R18 (i) completed state_purge record validates against arsia-audit-record ({name})",
              not errs, "; ".join(errs[:3]))
        check(f"R18 (i) state_purge record retention from its own anchor, unaffected by the override ({name})",
              got == want, str(got))

    # (j) A-79 idempotency is unchanged
    st = StateStore()
    st.set(K, "v", T0, retention="P1827D")
    rejected = st.purge(K, T1, "k1")
    check("R18 (j) retransmission returns the stored response, including a rejection; nothing removed",
          st.purge(K, T1, "k1", OVR) == rejected and not purges(st))
    first = st.purge(K, T1, "k2", OVR)
    again = st.purge(K, "2026-02-15T09:00:00.000Z", "k3")
    check("R18 (j) repeated PURGE without a later write: same purged_at, no record, no new evaluation",
          again == first and len(purges(st)) == 1)
    st.set(K, "w", "2026-02-16T09:00:00.000Z")
    later = st.purge(K, "2026-02-17T09:00:00.000Z", "k4")
    check("R18 (j) PURGE after a later write is evaluated on the set it would remove (erased values excluded)",
          "result" in later and len(purges(st)) == 2 and purges(st)[-1]["within_retention"] is False)

    # (k) scenario vectors
    sv = [v for v in vectors if v.get("test_metadata", {}).get("scenario") == "state"]
    check("R18 state vectors present (ITV-683..687)",
          sorted(v["id"] for v in sv if v["id"] in R18_STATE_IDS) == R18_STATE_IDS)
    check("R18 every state-scenario vector belongs to R17 or R18",
          sorted(v["id"] for v in sv) == sorted(R17_STATE_IDS + R18_STATE_IDS), str(sorted(v["id"] for v in sv)))
    for v in sv:
        if v["id"] not in R18_STATE_IDS:
            continue
        got = state_case(v["test_metadata"]["input"])
        miss = subset_match(v["test_metadata"]["expect"], got)
        check(f"R18 {v['id']} result matches its stated expectation", not miss, ", ".join(miss), executed=[v["id"]])
        check(f"R18 {v['id']} data is what the reference store produces", state_vector_data_matches(v, got))


# ---------------------------------------------------------------- R19 broker relay record
RELAY_FORWARD_FIELDS = ("attestation_id", "forwarded_at", "relay_latency_ms")


def relay_record_problems(rec):
    """Routing §7.4.2 runtime rules of a broker_relay record, as (kind, text) pairs.

    structure: the forwarding fields are present together, and a success record carries them;
    timing: relay_latency_ms is forwarded_at − received_at exactly, in whole milliseconds, non-negative."""
    present = [f for f in RELAY_FORWARD_FIELDS if f in rec]
    problems = []
    if present and len(present) != len(RELAY_FORWARD_FIELDS):
        problems.append(("structure", f"forwarding fields partially present: {present}"))
    if rec.get("forwarding_result") == "success" and not present:
        problems.append(("structure", "success without the forwarding fields"))
    if "forwarded_at" in rec and "relay_latency_ms" in rec:
        delta = iso(rec["forwarded_at"]) - iso(rec["received_at"])
        ms = delta.days * 86_400_000 + delta.seconds * 1000 + delta.microseconds // 1000
        if ms < 0:
            problems.append(("timing", f"forwarded_at precedes received_at by {-ms} ms"))
        if rec["relay_latency_ms"] != ms:
            problems.append(("timing", f"relay_latency_ms {rec['relay_latency_ms']} != forwarded_at − received_at = {ms}"))
    return problems


def relay_record(message_id, received_at, result, forwarded_ms=None, attestation_id=None, seed="relay"):
    """A complete broker_relay ArsiaAuditRecord (State §7.1, Routing §7.4.2) under the platform default (P90D)."""
    rec = {"record_id": record_id_for(seed, "record"), "message_id": message_id, "event_type": "broker_relay",
           "from_agent": DPOP_SENDER, "to_agent": DPOP_RECIPIENT, "intent": "request",
           "payload_type": "com.acme.notes/list", "payload_hash": "c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4"}
    end = received_at + dt.timedelta(milliseconds=(forwarded_ms or 0) + 20)
    rec.update(processed_at=stamp(end), retained_until=stamp(add_duration(end, "P90D")),
               operator_id="urn:lei:5493001KJTIIGC8Y1R12", compliance_profile_declared=None,
               compliance_profile_resolved="none", retention_source="platform-default", declared_retention=None,
               broker_agent_id=DPOP_BROKER, message_ts=stamp(received_at - dt.timedelta(milliseconds=450)),
               residency_zone="EU", received_at=stamp(received_at), forwarding_result=result)
    if forwarded_ms is not None:
        rec.update(attestation_id=attestation_id, forwarded_at=stamp(received_at + dt.timedelta(milliseconds=forwarded_ms)),
                   relay_latency_ms=forwarded_ms)
    return rec


def r19(vectors):
    recs = [v for v in vectors if isinstance(v.get("data"), dict) and v["data"].get("event_type") == "broker_relay"]
    valid = [v for v in recs if v.get("expected") == "valid"]
    invalid = [v for v in recs if v.get("expected") == "invalid"]
    check("R19 broker_relay vectors present (valid and invalid)", len(valid) >= 10 and len(invalid) >= 5,
          f"{len(valid)} valid, {len(invalid)} invalid")
    # (a) every valid record satisfies Routing §7.4.2
    bad = {v["id"]: relay_record_problems(v["data"]) for v in valid if relay_record_problems(v["data"])}
    check("R19 (a) every valid broker_relay record: forwarding fields together, latency = forwarded_at − received_at",
          not bad, str(bad))
    # (b) an invalid record carries no timing defect: its only cause is the declared one
    bad = {v["id"]: p for v in invalid for p in [[t for k, t in relay_record_problems(v["data"]) if k == "timing"]] if p}
    check("R19 (b) no invalid broker_relay vector carries a timing defect besides its declared cause", not bad, str(bad))
    # (c) the Routing §7.4.2 example
    text = open("spec/ARSIA-Routing.md", encoding="utf-8").read()
    block = text.split("**Example audit record (extension fields shown):**", 1)[1].split("```json", 1)[1].split("```", 1)[0]
    example = json.loads(block)
    check("R19 (c) the Routing §7.4.2 example satisfies the derivation",
          example["relay_latency_ms"] == 47 and not relay_record_problems(example), str(relay_record_problems(example)))
    # (d) synthetic negatives
    t0 = dt.datetime(2026, 11, 4, 10, 0, 0, 100000)
    ok = relay_record("d0b00700-ffff-4a3d-8e4f-567890abcdef", t0, "success", 38, "d0b00700-aaaa-4a3d-8e4f-567890abcdef")
    off = dict(ok, relay_latency_ms=39)
    early = dict(ok, forwarded_at=stamp(t0 - dt.timedelta(milliseconds=5)), relay_latency_ms=-5)
    bare = {k: x for k, x in ok.items() if k not in RELAY_FORWARD_FIELDS}
    partial = {k: x for k, x in ok.items() if k not in ("attestation_id", "relay_latency_ms")}
    partial["forwarding_result"] = "failure"
    rejected = dict(bare, forwarding_result="failure")
    kinds = lambda r: {k for k, _ in relay_record_problems(r)}
    check("R19 (d) latency one millisecond off is detected", kinds(off) == {"timing"})
    check("R19 (d) forwarded_at before received_at is detected", "timing" in kinds(early))
    check("R19 (d) success without the forwarding fields is detected", kinds(dict(bare, forwarding_result="success")) == {"structure"})
    check("R19 (d) partial forwarding fields are detected", kinds(partial) == {"structure"})
    check("R19 (d) a record of a message not forwarded (failure, no forwarding fields) has no defect", not kinds(rejected))
    # (e) the schema agrees with the structural rules
    cases = {"complete": ok, "not forwarded": rejected, "success without fields": dict(bare, forwarding_result="success"),
             "partial": partial, "attestation only": dict(rejected, attestation_id="d0b00700-aaaa-4a3d-8e4f-567890abcdef")}
    disagree = [n for n, r in cases.items()
                if bool(schema_errors(r, "arsia-audit-record.schema.json")) != ("structure" in kinds(r))]
    check("R19 (e) arsia-audit-record accepts exactly the structurally sound records", not disagree, str(disagree))


# ---------------------------------------------------------------- R20 DPoP proof verification
DPOP_SENDER = "agent:acme.dpop-sender"
DPOP_INTRUDER = "agent:acme.dpop-intruder"
DPOP_RECIPIENT = "agent:acme.dpop-recipient"
DPOP_BROKER = "agent:arsialabs.broker.eu-west"
DPOP_INBOX = "https://agent.acme-recipient.example/v1/arsia/inbox"
DPOP_OTHER_INBOX = "https://agent.acme-recipient.example/v1/arsia/stream-inbox"
DPOP_SKEW = 300  # Core §8.3 default
DPOP_TOKEN = "eyJhbGciOiJFZERTQSJ9.dpop-bound-token.sig"  # an opaque presented token; its cnf.jkt is in bindings
AGENT_SEEDS.update({DPOP_SENDER: 17, DPOP_INTRUDER: 18})
NONCE_CHALLENGE = 'DPoP error="use_dpop_nonce"'


def _b64u(b):
    import base64
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _unb64u(s):
    import base64
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _jwk(agent):
    from cryptography.hazmat.primitives import serialization
    raw = _key(agent).public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return {"kty": "OKP", "crv": "Ed25519", "x": _b64u(raw)}


def jkt(jwk):
    """RFC 7638 JWK SHA-256 Thumbprint of an OKP key: required members crv, kty, x in lexicographic order."""
    import hashlib
    return _b64u(hashlib.sha256(json.dumps({k: jwk[k] for k in ("crv", "kty", "x")},
                                           separators=(",", ":")).encode()).digest())


def token_hash(token):
    import hashlib
    return _b64u(hashlib.sha256(token.encode()).digest())


def dpop_jti(n):
    return f"d0b0{n:04x}-0000-4000-8000-{n:012x}"


def make_proof(agent, htu, iat, jti, token, nonce=None, **over):
    """A DPoP proof JWT (Identity §3.3) signed with agent's key; over replaces header/payload members or the signer."""
    header = {"typ": "dpop+jwt", "alg": "EdDSA", "jwk": _jwk(agent)}
    payload = {"jti": jti, "htm": "POST", "htu": htu, "iat": iat, "ath": token_hash(token)}
    if nonce is not None:
        payload["nonce"] = nonce
    header.update(over.get("header", {}))
    payload.update(over.get("payload", {}))
    for c in over.get("drop", ()):
        payload.pop(c)
    signing_input = _b64u(json.dumps(header).encode()) + "." + _b64u(json.dumps(payload).encode())
    return signing_input + "." + _b64u(_key(over.get("signer", agent)).sign(signing_input.encode()))


def effective_uri(uri):
    """Identity §3.3 check 9: the URI without query and fragment, scheme and host lower-cased, default port dropped."""
    from urllib.parse import urlsplit, urlunsplit
    p = urlsplit(uri)
    host = (p.hostname or "").lower()
    if p.port and not (p.scheme.lower() == "https" and p.port == 443):
        host += f":{p.port}"
    return urlunsplit((p.scheme.lower(), host, p.path or "/", "", ""))


class JtiStore:
    """Reference single-use store (Identity §3.3): one atomic claim per (target URI, jti), held until iat + S."""

    def __init__(self):
        import threading
        self._seen, self._lock = {}, threading.Lock()

    def _get(self, key):
        return self._seen.get(key)

    def _put(self, key, until):
        self._seen[key] = until

    def claim(self, key, until, now):
        with self._lock:
            held = self._get(key)
            if held is not None and held >= now:
                return False
            self._put(key, until)
            return True

    def accepted(self, key, now):
        """Whether the jti is already recorded; records nothing (the nonce challenge must not consume it)."""
        with self._lock:
            until = self._get(key)
            return until is not None and until >= now


class NoncePolicy:
    """A receiving agent that requires a nonce (Identity §3.3, RFC 9449 §9): nonces it provided, per DPoP key."""

    def __init__(self):
        self.provided, self.n = {}, 0

    def issue(self, key_thumbprint):
        self.n += 1
        value = f"n-{self.n:04d}.{key_thumbprint[:8]}"
        self.provided.setdefault(key_thumbprint, set()).add(value)
        return value

    def accepts(self, key_thumbprint, nonce):
        return nonce in self.provided.get(key_thumbprint, set())


def dpop_verify(req, now, store, bindings, nonce_policy=None, skew=DPOP_SKEW):
    """Identity §3.3 verification of the DPoP proof of req at the receiving agent's clock now (epoch seconds).

    req = {"method", "url", "headers": [(name, value), ...]}; bindings maps an access token to its cnf.jkt.
    Returns the transport response: {"status", "headers", "code", "check"}."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    def fail(n):
        return {"status": 401, "headers": {}, "code": "unauthorized", "check": n}

    dpop = [v for k, v in req["headers"] if k.lower() == "dpop"]
    auth = [v for k, v in req["headers"] if k.lower() == "authorization"]
    if len(dpop) != 1:                                                           # check 1
        return fail(1)
    try:                                                                         # check 2
        h64, p64, s64 = dpop[0].split(".")
        header, payload = json.loads(_unb64u(h64)), json.loads(_unb64u(p64))
        assert isinstance(header, dict) and isinstance(payload, dict)
    except Exception:
        return fail(2)
    if any(c not in payload for c in ("jti", "htm", "htu", "iat", "ath")):      # check 3 (nonce: below)
        return fail(3)
    number = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool) and abs(x) < 2 ** 53
    if not all(isinstance(payload[c], str) for c in ("jti", "htm", "htu", "ath")) or not number(payload["iat"]):
        return fail(3)                                                           # claims of the wrong type
    if header.get("typ") != "dpop+jwt":                                          # check 4
        return fail(4)
    jwk = header.get("jwk")
    if (header.get("alg") != "EdDSA" or not isinstance(jwk, dict) or jwk.get("kty") != "OKP"
            or jwk.get("crv") != "Ed25519" or not isinstance(jwk.get("x"), str)):  # check 5
        return fail(5)
    try:                                                                         # check 6
        Ed25519PublicKey.from_public_bytes(_unb64u(jwk["x"])).verify(_unb64u(s64), f"{h64}.{p64}".encode())
    except Exception:
        return fail(6)
    if any(m in jwk for m in ("d", "p", "q", "dp", "dq", "qi", "k")):           # check 7
        return fail(7)
    if payload["htm"] != req["method"] or req["method"] != "POST":              # check 8
        return fail(8)
    try:                                                                         # check 9
        if effective_uri(payload["htu"]) != effective_uri(req["url"]):
            return fail(9)
    except ValueError:
        return fail(9)
    if abs(now - payload["iat"]) > skew:                                         # check 11
        return fail(11)
    token = auth[0].split(" ", 1)[1] if auth and auth[0].startswith("DPoP ") else None
    if token is None or payload["ath"] != token_hash(token) or bindings.get(token) != jkt(jwk):  # check 12
        return fail(12)
    key = (effective_uri(req["url"]), payload["jti"])                           # check 13: single use
    if nonce_policy is not None:                                                 # checks 3 and 10: nonce
        thumb = jkt(jwk)
        nonce = payload.get("nonce")
        if not (isinstance(nonce, str) and nonce_policy.accepts(thumb, nonce)):
            if store.accepted(key, now):                                         # not a nonce-only failure
                return fail(13)
            return {"status": 401, "code": None, "check": 10,
                    "headers": {"WWW-Authenticate": NONCE_CHALLENGE, "DPoP-Nonce": nonce_policy.issue(thumb)}}
    if not store.claim(key, payload["iat"] + skew, now):
        return fail(13)
    return {"status": 200, "headers": {}, "code": None, "check": None}


def dpop_request(proof, token=None, url=DPOP_INBOX, extra=()):
    token = token or DPOP_TOKEN
    return {"method": "POST", "url": url,
            "headers": [("Authorization", f"DPoP {token}"), ("DPoP", proof), *extra]}


class DpopRecipient:
    """A receiving agent behind a simulated transport; it records every proof that reaches it."""

    def __init__(self, bindings, nonce_policy=None):
        self.store, self.bindings, self.nonce_policy, self.seen = JtiStore(), bindings, nonce_policy, []

    def handle(self, req, now):
        self.seen.append([v for k, v in req["headers"] if k.lower() == "dpop"])
        return dpop_verify(req, now, self.store, self.bindings, self.nonce_policy)


AUTH_TOKEN = r"[!#$%&'*+.^_`|~0-9A-Za-z-]+"
AUTH_PARAM = re.compile(rf'({AUTH_TOKEN})[ \t]*=[ \t]*("(?:[^"\\]|\\.)*"|{AUTH_TOKEN})')
AUTH_TOKEN68 = re.compile(r"[A-Za-z0-9._~+/-]+=*")
AUTH_SCHEME = re.compile(AUTH_TOKEN)
NQCHAR_NONCE = re.compile(r"^[\x21\x23-\x5B\x5D-\x7E]+$")


def auth_challenges(value):
    """RFC 9110 §11.3, §11.6.1 WWW-Authenticate = #challenge, challenge = auth-scheme [ 1*SP ( token68 /
    #auth-param ) ]: [(scheme, {param: value}, token68 or None)], or None when the value does not parse.

    A challenge may carry no parameters, a token68 or auth-params, and several challenges share the field;
    after a comma, an element that is not an auth-param starts the next challenge."""
    n = len(value)

    def ows(p):
        while p < n and value[p] in " \t":
            p += 1
        return p

    def element(p):
        """Start of the next non-empty list element (empty elements and OWS skipped)."""
        p = ows(p)
        while p < n and value[p] == ",":
            p = ows(p + 1)
        return p

    out, pos = [], element(0)
    while pos < n:
        m = AUTH_SCHEME.match(value, pos)
        if not m:
            return None
        challenge = (m.group(0), {}, None)
        out.append(challenge)
        pos = m.end()
        if ows(pos) == n or value[ows(pos)] == ",":                              # no parameters
            pos = element(pos)
            continue
        if value[pos] != " ":                                                    # 1*SP before the parameters
            return None
        pos = ows(pos)
        p = AUTH_PARAM.match(value, pos)
        if not p:                                                                # token68
            t = AUTH_TOKEN68.match(value, pos)
            if not t or not (ows(t.end()) == n or value[ows(t.end())] == ","):
                return None
            out[-1] = (challenge[0], {}, t.group(0))
            pos = element(t.end())
            continue
        while p:                                                                 # #auth-param
            v = p.group(2)
            challenge[1][p.group(1).lower()] = re.sub(r"\\(.)", r"\1", v[1:-1]) if v.startswith('"') else v
            after = ows(p.end())
            if after < n and value[after] != ",":
                return None
            pos = element(after)
            p = AUTH_PARAM.match(value, pos) if pos < n else None
    return out


def recipient_nonce(resp):
    """The nonce of a complete DPoP nonce challenge (Identity §3.3, RFC 9449 §9), else None: HTTP 401, a DPoP
    challenge with error="use_dpop_nonce" (other parameters allowed), and a well-formed DPoP-Nonce header."""
    headers = {k.lower(): v for k, v in resp.get("headers", {}).items()}
    challenges = auth_challenges(headers.get("www-authenticate", "")) or []
    if resp.get("status") != 401 or not any(s.lower() == "dpop" and p.get("error") == "use_dpop_nonce"
                                            for s, p, _ in challenges):
        return None
    nonce = headers.get("dpop-nonce")
    return nonce if isinstance(nonce, str) and NQCHAR_NONCE.match(nonce) else None


class DpopBroker:
    """Routing §2.3.2/§2.3.3: forwards the sender's proof once and returns a recipient nonce challenge to the sender."""

    def __init__(self, transport):
        self.transport, self.records, self.n = transport, [], 0

    def relay(self, envelope, token, proof, now):
        self.n += 1
        received = dt.datetime(2026, 11, 4, 10, 0, 0) + dt.timedelta(seconds=now - DPOP_T0)
        attestation = f"d0b0{self.n:04x}-aaaa-4a3d-8e4f-567890abcdef"
        resp = self.transport(dpop_request(proof, token), now)
        if resp["status"] == 200:
            self.records.append(relay_record(envelope["id"], received, "success", 30, attestation, f"relay-{self.n}"))
            return {"headers": {}, "message": {"intent": "response", "correlation_id": envelope["id"]}}
        self.records.append(relay_record(envelope["id"], received, "failure", 30, attestation, f"relay-{self.n}"))
        details = {"relay_failed": True, "relay_id": attestation}
        nonce = recipient_nonce(resp)
        if nonce is not None:
            details.update(reason="recipient_dpop_nonce", dpop_nonce=nonce, dpop_nonce_htu=DPOP_INBOX)
        else:
            details["original_error"] = {"code": resp["code"] or "unauthorized", "description": "Recipient rejected the request."}
        message = {"v": "2.0", "id": record_id_for(f"relay-error-{self.n}", "message"),
                   "ts": stamp(received + dt.timedelta(milliseconds=60)), "from": DPOP_BROKER, "to": envelope["from"],
                   "intent": "error", "correlation_id": envelope["id"], "root_request_id": envelope["id"],
                   "payload": {"type": "arsiaprotocol.broker/relay-error",
                               "error": {"code": "service_unavailable",
                                         "description": "Failed to relay message to recipient.", "details": details}}}
        return {"headers": {}, "message": message}


DPOP_T0 = 1793786400  # 2026-11-04T10:00:00Z


def r20(vectors):
    import threading
    t0, S = DPOP_T0, DPOP_SKEW
    token = DPOP_TOKEN
    other_token = "eyJhbGciOiJFZERTQSJ9.another-token.sig"
    bindings = {token: jkt(_jwk(DPOP_SENDER)), other_token: jkt(_jwk(DPOP_SENDER))}
    seq = iter(range(1, 10_000))
    fresh = lambda **kw: make_proof(DPOP_SENDER, kw.pop("htu", DPOP_INBOX), kw.pop("iat", t0), dpop_jti(next(seq)),
                                    kw.pop("token", token), kw.pop("nonce", None), **kw)
    run = lambda req, now=t0, store=None, policy=None: dpop_verify(req, now, store or JtiStore(), bindings, policy)
    plain = lambda r: r["status"] == 401 and r["code"] == "unauthorized" and not r["headers"]

    # (a) a valid proof is accepted
    check("R20 (a) a valid DPoP proof is accepted", run(dpop_request(fresh()))["status"] == 200)

    # (b) one mutation per check not concerning the nonce: rejected by that check, generic unauthorized
    d_jwk = dict(_jwk(DPOP_SENDER), d=_b64u(bytes(32)))
    cases = {
        1: dpop_request(fresh(), token, extra=[("DPoP", fresh())]),
        2: dpop_request(fresh().rsplit(".", 1)[0], token),
        3: dpop_request(fresh(drop=("jti",))),
        4: dpop_request(fresh(header={"typ": "JWT"})),
        5: dpop_request(fresh(header={"alg": "ES256"})),
        6: dpop_request(fresh(signer=DPOP_INTRUDER)),
        7: dpop_request(fresh(header={"jwk": d_jwk})),
        8: dpop_request(fresh(payload={"htm": "GET"})),
        9: dpop_request(fresh(htu=DPOP_OTHER_INBOX)),
        11: dpop_request(fresh(iat=t0 - S - 1)),
        12: dpop_request(fresh(token=other_token)),
    }
    for n, req in cases.items():
        r = run(req)
        check(f"R20 (b) check {n} failure is rejected by check {n} with a generic unauthorized", plain(r) and r["check"] == n,
              f"got status {r['status']} check {r['check']}")
    r = run(dpop_request(fresh(header={"jwk": _jwk(DPOP_INTRUDER)}, signer=DPOP_INTRUDER)))
    check("R20 (b) check 12: a proof key other than the token's cnf.jkt is rejected", plain(r) and r["check"] == 12)
    st = JtiStore()
    p = fresh()
    run(dpop_request(p), store=st)
    r = run(dpop_request(p), store=st)
    check("R20 (b) check 13: a replayed jti is rejected with a generic unauthorized", plain(r) and r["check"] == 13)
    malformed = {"jwk null": (5, dict(header={"jwk": None})), "iat a string": (3, dict(payload={"iat": str(t0)})),
                 "htu null": (3, dict(payload={"htu": None})), "jti a list": (3, dict(payload={"jti": []})),
                 "htu with an invalid port": (9, dict(payload={"htu": "https://agent.acme-recipient.example:x/v1/arsia/inbox"}))}
    for name, (n, over) in malformed.items():
        try:
            r = run(dpop_request(fresh(**over)))
            got = f"status {r['status']} check {r['check']}"
            ok = plain(r) and r["check"] == n
        except Exception as e:
            got, ok = f"exception {type(e).__name__}", False
        check(f"R20 (b) malformed proof ({name}, validly signed) is rejected by check {n}, without an exception", ok, got)
    check("R20 (b) zero DPoP header fields fail check 1",
          plain(run({"method": "POST", "url": DPOP_INBOX, "headers": [("Authorization", f"DPoP {token}")]})))

    # (c) htu compared without query and fragment
    check("R20 (c) a request URI with query and fragment matches htu",
          run(dpop_request(fresh(), url=DPOP_INBOX + "?trace=1#frag"))["status"] == 200)

    # (d) single use per target URI; query or fragment variants share the scope
    st = JtiStore()
    p = fresh()
    first = run(dpop_request(p), store=st)
    again = run(dpop_request(p), store=st)
    variant = run(dpop_request(p, url=DPOP_INBOX + "?x=1#y"), store=st)
    jti = json.loads(_unb64u(p.split(".")[1]))["jti"]
    elsewhere = run(dpop_request(make_proof(DPOP_SENDER, DPOP_OTHER_INBOX, t0, jti, token), url=DPOP_OTHER_INBOX), store=st)
    check("R20 (d) the same jti is rejected again for the same target URI", first["status"] == 200 and again["check"] == 13)
    check("R20 (d) a query or fragment variant does not open a new scope for the same jti", variant["check"] == 13,
          f"status {variant['status']}")
    check("R20 (d) the same jti is accepted for another target URI", elsewhere["status"] == 200)

    # (e) retention until iat + S, not a fixed period from the first receipt
    st = JtiStore()
    p = fresh(iat=t0 + S)
    ahead = run(dpop_request(p), now=t0, store=st)
    late = run(dpop_request(p), now=t0 + S + 1, store=st)
    check("R20 (e) a proof with iat = t0 + S, first received at t0, is still rejected as a replay at t0 + S + 1",
          ahead["status"] == 200 and late["check"] == 13, f"replay at t0+S+1: {late}")

    # (f) after iat + S the proof fails check 11, whatever the store holds
    check("R20 (f) after iat + S the proof fails the acceptance window (check 11)",
          run(dpop_request(p), now=t0 + 2 * S + 1, store=st)["check"] == 11)

    # (g) a receiving agent that requires a nonce
    def challenge(r):
        return (r["status"] == 401 and r["headers"].get("WWW-Authenticate") == NONCE_CHALLENGE
                and bool(r["headers"].get("DPoP-Nonce")) and r["code"] is None)
    pol, st = NoncePolicy(), JtiStore()
    r1 = run(dpop_request(fresh()), store=st, policy=pol)
    check("R20 (g) 1 the first request without a nonce is answered with the nonce challenge (401, both headers)",
          challenge(r1), str(r1))
    r2 = run(dpop_request(fresh()), store=st, policy=pol)
    check("R20 (g) 2 a proof without nonce after one was provided gets the challenge, not a generic unauthorized",
          challenge(r2), str(r2))
    r3 = run(dpop_request(fresh(nonce="not-a-nonce-it-issued")), store=st, policy=pol)
    check("R20 (g) 3 a nonce the agent does not accept gets the challenge", challenge(r3), str(r3))
    nonce = r1["headers"].get("DPoP-Nonce")
    r4 = run(dpop_request(fresh(nonce=nonce)), store=st, policy=pol)
    r5 = run(dpop_request(fresh(nonce=nonce)), store=st, policy=pol)
    check("R20 (g) 4 the provided nonce is accepted; reused with a new jti it is accepted again",
          r4["status"] == 200 and r5["status"] == 200)
    r6 = run(dpop_request(fresh(nonce=nonce, token=other_token), token), store=st, policy=pol)
    check("R20 (g) 5 a correct nonce with another failure (ath) gets a generic unauthorized, no challenge",
          plain(r6) and r6["check"] == 12, str(r6))

    pol, st = NoncePolicy(), JtiStore()
    nonce = run(dpop_request(fresh()), store=st, policy=pol)["headers"].get("DPoP-Nonce")
    jti = dpop_jti(next(seq))
    once = lambda n: dpop_request(make_proof(DPOP_SENDER, DPOP_INBOX, t0, jti, token, n))
    r7 = run(once(nonce), store=st, policy=pol)
    r8 = run(once(nonce), store=st, policy=pol)
    r9 = run(once("not-a-nonce-it-issued"), store=st, policy=pol)
    check("R20 (g) 6 a jti already accepted, with an unaccepted nonce, is rejected by check 13, not challenged",
          r7["status"] == 200 and r8["check"] == 13 and plain(r9) and r9["check"] == 13, str(r9))
    jti2 = dpop_jti(next(seq))
    r10 = run(dpop_request(make_proof(DPOP_SENDER, DPOP_INBOX, t0, jti2, token, "stale")), store=st, policy=pol)
    r11 = run(dpop_request(make_proof(DPOP_SENDER, DPOP_INBOX, t0, jti2, token, r10["headers"].get("DPoP-Nonce"))),
              store=st, policy=pol)
    check("R20 (g) 7 a new jti with an unaccepted nonce is challenged, and the challenge does not consume the jti",
          challenge(r10) and r11["status"] == 200, f"{r10['status']}/{r11['status']}")
    r12 = run(dpop_request(fresh(nonce=7)), store=st, policy=pol)
    check("R20 (g) 8 a nonce claim of the wrong type is an unaccepted nonce: challenged, no exception", challenge(r12))

    # (h) retransmission: a new proof is accepted, the same proof is not
    st = JtiStore()
    p = fresh()
    run(dpop_request(p), store=st)
    check("R20 (h) a retransmission with a new proof is accepted; the re-sent proof is rejected",
          run(dpop_request(fresh()), store=st)["status"] == 200 and run(dpop_request(p), store=st)["check"] == 13)

    # (i) generated proofs conform to arsia-dpop-proof
    p = fresh(nonce="eyJ7S_zG.eyJH0-Z.HX4w-7v")
    h64, p64, _ = p.split(".")
    errs = (schema_errors(json.loads(_unb64u(h64)), "arsia-dpop-proof.schema.json", "dpop-header")
            + schema_errors(json.loads(_unb64u(p64)), "arsia-dpop-proof.schema.json"))
    check("R20 (i) the generated header and payload validate against arsia-dpop-proof", not errs, "; ".join(errs[:2]))

    # (j) brokered delivery: recipient challenge -> sender -> new proof -> delivery
    recipient = DpopRecipient(bindings, NoncePolicy())
    broker = DpopBroker(recipient.handle)
    envelope = {"id": "d0b00720-ffff-4a3d-8e4f-567890abcdef", "from": DPOP_SENDER}
    old = fresh()
    out1 = broker.relay(envelope, token, old, t0)
    det = out1["message"]["payload"]["error"]["details"] if out1["message"].get("intent") == "error" else {}
    issued = sorted(recipient.nonce_policy.provided.get(bindings[token], set()))
    check("R20 (j) 1 the broker returns the challenge: reason recipient_dpop_nonce, the recipient's nonce, its inbox URL",
          det.get("reason") == "recipient_dpop_nonce" and [det.get("dpop_nonce")] == issued
          and det.get("dpop_nonce_htu") == DPOP_INBOX, str(det))
    errs = schema_errors(out1["message"], "arsia-message.schema.json")
    check("R20 (j) 1 the relay error validates against arsia-message", not errs, "; ".join(errs[:2]))
    check("R20 (j) 2 the broker does not present the recipient's nonce as its own DPoP-Nonce",
          det.get("dpop_nonce") not in out1["headers"].values())
    rec1 = broker.records[-1]
    check("R20 (j) 3 the attempt is recorded as failure with the forwarding fields",
          rec1["forwarding_result"] == "failure" and all(f in rec1 for f in RELAY_FORWARD_FIELDS)
          and not relay_record_problems(rec1) and not schema_errors(rec1, "arsia-audit-record.schema.json"),
          str(schema_errors(rec1, "arsia-audit-record.schema.json")[:2]))
    out2 = broker.relay(envelope, token, fresh(nonce=det.get("dpop_nonce")), t0 + 1)
    rec2 = broker.records[-1]
    old_seen = sum(old in proofs for proofs in recipient.seen)
    check("R20 (j) 4 the old proof reached the recipient exactly once (never re-sent)", old_seen == 1, f"{old_seen} times")
    check("R20 (j) 5 the retry with a new proof and the nonce is delivered and recorded as success",
          out2["message"].get("intent") == "response" and rec2["forwarding_result"] == "success"
          and rec2["message_id"] == rec1["message_id"] and rec2["attestation_id"] != rec1["attestation_id"]
          and not relay_record_problems(rec2) and not schema_errors(rec2, "arsia-audit-record.schema.json"))

    variants = {
        "error_description parameter (RFC 9449 Figure 24)":
            ({"WWW-Authenticate": 'DPoP error="use_dpop_nonce", error_description="Resource server requires nonce in DPoP proof"',
              "DPoP-Nonce": "eyJ7S_zG.eyJH0-Z.HX4w-7v"}, "eyJ7S_zG.eyJH0-Z.HX4w-7v"),
        "another challenge first, lower-case header names":
            ({"www-authenticate": 'Bearer realm="acme", DPoP algs="EdDSA", error="use_dpop_nonce"', "dpop-nonce": "n-1"}, "n-1"),
        "after a challenge without parameters":
            ({"WWW-Authenticate": 'Negotiate, DPoP error="use_dpop_nonce"', "DPoP-Nonce": "n-1"}, "n-1"),
        "after a token68 challenge":
            ({"WWW-Authenticate": 'Negotiate YWJjZA==, DPoP error="use_dpop_nonce"', "DPoP-Nonce": "n-1"}, "n-1"),
        "challenge without DPoP-Nonce": ({"WWW-Authenticate": NONCE_CHALLENGE}, None),
        "another DPoP error with a nonce": ({"WWW-Authenticate": 'DPoP error="invalid_dpop_proof"', "DPoP-Nonce": "n-2"}, None),
        "unparseable WWW-Authenticate": ({"WWW-Authenticate": "== DPoP", "DPoP-Nonce": "n-3"}, None),
    }
    for name, (headers, expect) in variants.items():
        canned = lambda req, now, h=headers: {"status": 401, "headers": h, "code": None, "check": 10}
        try:
            out = DpopBroker(canned).relay(envelope, token, fresh(), t0 + 2)
            det = out["message"]["payload"]["error"]["details"]
            ok = (det.get("dpop_nonce") == expect and (det.get("reason") == "recipient_dpop_nonce") == (expect is not None)
                  and det.get("dpop_nonce_htu") == (DPOP_INBOX if expect else None)
                  and not schema_errors(out["message"], "arsia-message.schema.json"))
            got = str({k: det.get(k) for k in ("reason", "dpop_nonce", "dpop_nonce_htu")})
        except Exception as e:
            ok, got = False, f"exception {type(e).__name__}"
        check(f"R20 (j) 6 broker, {name}: " + ("the challenge is preserved" if expect else "a generic relay error, no exception"),
              ok, got)

    # (k) atomic claim on the shared reference store: two concurrent proofs, one acceptance
    class Interleaving(JtiStore):
        """Pauses after each lookup so that a non-atomic claim interleaves lookup A, lookup B, record A, record B."""

        def __init__(self):
            super().__init__()
            self.gate = threading.Barrier(2, timeout=0.5)

        def _get(self, key):
            held = super()._get(key)
            try:
                self.gate.wait()
            except threading.BrokenBarrierError:
                pass
            return held

    st, p, results = Interleaving(), fresh(), []
    threads = [threading.Thread(target=lambda: results.append(run(dpop_request(p), store=st)["status"]))
               for _ in range(2)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    check("R20 (k) two concurrent requests with the same jti and URI: exactly one is accepted",
          sorted(results) == [200, 401], str(results))


# ---------------------------------------------------------------- R21 token binding
def token_binding(envelope, presented_token):
    """Core §4.3.9: SHA-256 over the exact octets of the presented access token against
    authorization.token_hash. Checks the binding only — not the token's validity, authorization or DPoP."""
    import hashlib
    auth = envelope.get("authorization")
    if not auth:
        return "accept"
    digest = "sha-256:" + hashlib.sha256(presented_token.encode("utf-8")).hexdigest()
    return "accept" if digest == auth.get("token_hash") else "unauthorized"


def r21(vectors):
    envelope = lambda v: v.get("message") if isinstance(v.get("message"), dict) else v.get("data")
    # (a) every corpus vector with authorization and no explicit token: the synthetic-token convention binds
    bound = [v for v in vectors if isinstance(envelope(v), dict) and "authorization" in envelope(v)
             and "presented_token" not in v.get("test_metadata", {}).get("input", {})]
    bad = [v["id"] for v in bound if token_binding(envelope(v), f"synthetic-token:{v['id']}") != "accept"]
    check("R21 (a) every authorization binding of the corpus matches its synthetic-token:<ID> (binding only)",
          len(bound) >= 40 and not bad, f"{len(bound)} bound, mismatches {bad[:4]}", executed=[v["id"] for v in bound])
    # (b) token_binding scenarios reproduce their declared result
    sc = [v for v in vectors if v.get("test_metadata", {}).get("scenario") == "token_binding"]
    check("R21 token_binding scenario vectors present (accept and unauthorized)",
          {v["test_metadata"]["expect"]["result"] for v in sc} == {"accept", "unauthorized"}, str(len(sc)))
    for v in sc:
        got = token_binding(envelope(v), v["test_metadata"]["input"]["presented_token"])
        check(f"R21 (b) {v['id']} binding result is {v['test_metadata']['expect']['result']}",
              got == v["test_metadata"]["expect"]["result"], got, executed=[v["id"]])
    # (c) synthetic: exact octets
    token = "eyJhbGciOiJFZERTQSJ9.MixedCase-Token.Sig"
    env = {"authorization": {"token_hash": "sha-256:" + __import__("hashlib").sha256(token.encode()).hexdigest(),
                             "proof_type": "bearer"}}
    check("R21 (c) a correct token containing upper-case letters is accepted", token_binding(env, token) == "accept")
    check("R21 (c) the same token with a trailing space is rejected", token_binding(env, token + " ") == "unauthorized")
    check("R21 (c) the same token with its case changed is rejected", token_binding(env, token.lower()) == "unauthorized")
    check("R21 (c) another encoding of the token's characters is rejected",
          token_binding(env, token.replace("-", "‐")) == "unauthorized")
    check("R21 (c) an envelope without authorization requires no binding", token_binding({}, "anything") == "accept")


# ---------------------------------------------------------------- R22 relay attestation
def verify_attestation(att, envelope, presented_token, broker_entry, jwks, now, seen):
    """Routing §7.4.1 recipient verification, steps 2-5 and the replay rule. Returns (result, step).

    The clock skew is the envelope profile's (Core §8.3, skew_tolerance); a repeated attestation_id is
    rejected only for a different envelope_hash."""
    import hashlib
    sys.path.insert(0, "scripts")
    import validate_vectors as vv
    from regen_v2 import envelope_hash, signing_input_v2
    fail = lambda step: ("unauthorized", step)
    # step 2: the key belongs to the broker and is published; the signature verifies (envelope signing profile)
    sec = att.get("security") or {}
    kid = sec.get("kid", "")
    published = {k["kid"]: k["public_key_hex"] for k in jwks}
    if kid.split("#", 1)[0] != att.get("broker_id") or kid not in published:
        return fail(2)
    try:
        vv._verify_signature(sec.get("alg"), bytes.fromhex(published[kid]), vv._base64url_decode(sec.get("sig", "")),
                             signing_input_v2(att))
    except Exception:
        return fail(2)
    # step 3: an authorised Compliance Broker for the declared zone
    zone = (envelope.get("compliance") or {}).get("data_residency")
    if "arsiaprotocol.broker.relay" not in broker_entry.get("capabilities", []) or broker_entry.get("agent_id") != att["broker_id"]:
        return fail(3)
    if broker_entry.get("jurisdiction") not in normalize_residency(zone)[0]:
        return fail(3)
    # step 4: bound to the complete signed envelope and to the token
    token_digest = "sha-256:" + hashlib.sha256(presented_token.encode("utf-8")).hexdigest()
    if att.get("envelope_hash") != envelope_hash(envelope):
        return fail(4)
    if not (att.get("authorization_token_hash") == (envelope.get("authorization") or {}).get("token_hash") == token_digest):
        return fail(4)
    # step 5: identities, acceptance window, replay
    if (att.get("message_id"), att.get("sender"), att.get("recipient")) != (envelope["id"], envelope["from"], envelope["to"]):
        return fail(5)
    skew = dt.timedelta(seconds=skew_tolerance(envelope)[0])
    if not iso(att["issued_at"]) - skew <= iso(now) <= iso(att["valid_until"]) + skew:
        return fail(5)
    if any(s["attestation_id"] == att["attestation_id"] and s["envelope_hash"] != att["envelope_hash"] for s in seen):
        return fail(5)
    return ("accept", None)


ATTESTATION_HEADER_ALPHABET = re.compile(r"^[A-Za-z0-9_-]+$")


def decode_attestation_header(value):
    """Routing §7.4.1 step 2, decoding: base64url without padding, then Core §5.2 steps 2-4 on the
    decoded octets, then the attestation schema. Returns (attestation, None) or (None, reason); never
    raises. A failure here is a step 2 failure (unauthorized), never invalid_request."""
    import base64
    import validate_vectors as vv
    if not isinstance(value, str) or value == "":
        return None, "empty header value"
    if not ATTESTATION_HEADER_ALPHABET.match(value):
        return None, "character outside the base64url alphabet (padding included)"
    if len(value) % 4 == 1:
        return None, "length does not decode to whole octets"
    try:
        raw = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except Exception as exc:  # noqa: BLE001 - any decoding failure is a controlled rejection
        return None, f"base64url: {exc}"
    # Untrusted input: any failure while parsing or validating it is a controlled step 2 rejection, never an
    # exception — including what the parse accepts but later processing cannot handle (a JSON integer beyond
    # Python's digit limit reaching an error message, nesting deeper than the recursion limit).
    try:
        att = vv.strict_json(raw)
    except vv.JsonRejected as exc:
        return None, f"Core §5.2 {exc}"
    except (ValueError, RecursionError, MemoryError) as exc:
        return None, f"decoded content not processable: {type(exc).__name__}"
    try:
        if schema_errors(att, "arsia-relay-attestation.schema.json"):
            return None, "attestation schema"
    except (ValueError, RecursionError, MemoryError) as exc:
        return None, f"attestation schema not evaluable: {type(exc).__name__}"
    return att, None


def receive_attestation(header, envelope, presented_token, broker_entry, jwks, now, seen):
    """Routing §7.4.1 recipient verification with the header as received (None = header absent).
    Returns (result, step) or, for step 1, (result, 1, details)."""
    zone = (envelope.get("compliance") or {}).get("data_residency")
    if zone is None:
        return ("not_required", None)
    if header is None:
        return ("service_unavailable", 1, {"data_residency_violation": True, "required_zone": zone})
    att, _reason = decode_attestation_header(header)
    if att is None:
        return ("unauthorized", 2)
    return verify_attestation(att, envelope, presented_token, broker_entry, jwks, now, seen)


def b64url_nopad(raw):
    import base64
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def derived_header(att):
    """The header of an attestation vector that states none: base64url without padding of the compact
    JSON serialization of its data."""
    return b64url_nopad(json.dumps(att, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))


def permissive_decode(header, kind):
    """R22 (f) controls: a decoder that tolerates exactly one defect. The attestation it returns must be
    accepted, which shows that defect is the only cause of the rejection."""
    import base64
    import validate_vectors as vv
    if kind == "strip-padding":
        return vv.strict_json(base64.urlsafe_b64decode(header.rstrip("=") + "=" * (-len(header.rstrip("=")) % 4)))
    if kind == "standard-alphabet":
        return vv.strict_json(base64.b64decode(header + "=" * (-len(header) % 4)))
    if kind == "drop-last":
        h = header[:-1]
        return vv.strict_json(base64.urlsafe_b64decode(h + "=" * (-len(h) % 4)))
    if kind == "last-wins":
        return json.loads(base64.urlsafe_b64decode(header + "=" * (-len(header) % 4)))
    if kind == "no-schema":
        return vv.strict_json(base64.urlsafe_b64decode(header + "=" * (-len(header) % 4)))
    raise ValueError(kind)


def r22(vectors):
    sys.path.insert(0, "scripts")
    import validate_vectors as vv
    from regen_v2 import signing_input_v2
    sc = [v for v in vectors if v.get("test_metadata", {}).get("scenario") == "attestation"]
    check("R22 attestation scenario vectors present (accept, unauthorized, service_unavailable, not_required)",
          {v["test_metadata"]["expect"]["result"] for v in sc}
          == {"accept", "unauthorized", "service_unavailable", "not_required"}, str(len(sc)))
    ATT = "arsia-relay-attestation.schema.json"
    KEYS = ("presented_token", "broker_entry", "jwks", "now", "seen")

    def delivered(v):
        """(header, envelope) as the recipient receives them: an attestation vector carries the attestation
        in data and the envelope in its input; an envelope vector carries the envelope in data and the
        header (null = absent) in its input."""
        inp = v["test_metadata"]["input"]
        if v["schema_ref"] == ATT:
            return inp.get("attestation_header", derived_header(v["data"])), inp["envelope"]
        return inp["attestation_header"], v["data"]

    def run(v, **over):
        inp = v["test_metadata"]["input"]
        header, envelope = delivered(v)
        if "att" in over:
            header = derived_header(over["att"])
        return receive_attestation(over.get("header", header), envelope, **{k: over.get(k, inp[k]) for k in KEYS})

    for v in sc:
        exp = v["test_metadata"]["expect"]
        got = run(v)
        want = (exp["result"], exp.get("step")) + ((exp["details"],) if "details" in exp else ())
        check(f"R22 (a) {v['id']} is {exp['result']}" + (f" at step {exp['step']}" if exp.get("step") else ""),
              got == want, str(got), executed=[v["id"]])
    # (b) negatives of binding, window, authorisation and replay keep a valid signature: their cause is the intended one
    for v in sc:
        exp = v["test_metadata"]["expect"]
        if exp["result"] == "unauthorized" and exp.get("step") in (3, 4, 5) and v["schema_ref"] == ATT:
            a, keys = v["data"], {k["kid"]: k["public_key_hex"] for k in v["test_metadata"]["input"]["jwks"]}
            try:
                vv._verify_signature(a["security"]["alg"], bytes.fromhex(keys[a["security"]["kid"]]),
                                     vv._base64url_decode(a["security"]["sig"]), signing_input_v2(a))
                ok = True
            except Exception:
                ok = False
            check(f"R22 (b) {v['id']} keeps a valid attestation signature", ok)
    good = next((v for v in sc if v["id"] == "ITV-569"), None)
    check("R22 the accepted reference attestation (ITV-569) is present", good is not None)
    if good is None:
        return
    # (c) the signature is verified inside R22: one byte of the signature changed, everything else correct
    a = json.loads(json.dumps(good["data"]))
    s = a["security"]["sig"]
    a["security"]["sig"] = ("B" if s[0] != "B" else "C") + s[1:]
    check("R22 (c) an attestation whose signature does not verify is rejected at step 2, all else correct",
          run(good, att=a) == ("unauthorized", 2))
    # (d) envelope_hash covers the complete signed envelope: computed without sig it does not match
    import hashlib
    import rfc8785
    env = good["test_metadata"]["input"]["envelope"]
    without_sig = json.loads(json.dumps(env)); without_sig["security"].pop("sig")
    check("R22 (d) envelope_hash is over the complete signed envelope (security.sig included), not the signing input",
          good["data"]["envelope_hash"] != "sha-256:" + hashlib.sha256(rfc8785.dumps(without_sig)).hexdigest()
          and run(good) == ("accept", None))
    # (e) an attestation vector that states no header is delivered with the derived header, and that header
    # decodes to exactly its data
    for v in sc:
        if v["schema_ref"] == ATT and "attestation_header" not in v["test_metadata"]["input"]:
            att, why = decode_attestation_header(derived_header(v["data"]))
            check(f"R22 (e) {v['id']} derived header decodes to exactly its attestation", att == v["data"], str(why))
    # (f) each header negative has exactly one defect: a decoder tolerating only that defect recovers an
    # attestation that is accepted
    by_id = {v["id"]: v for v in sc}
    for v in sc:
        kind = v["test_metadata"]["input"].get("permissive")
        if not kind:
            continue
        header, envelope = delivered(v)
        inp = v["test_metadata"]["input"]
        try:
            att = permissive_decode(header, kind)
            got = verify_attestation(att, envelope, **{k: inp[k] for k in KEYS})
        except Exception as exc:  # noqa: BLE001
            got = ("exception", str(exc)[:80])
        check(f"R22 (f) {v['id']} has a single defect: the {kind} decoder recovers an accepted attestation",
              got == ("accept", None), str(got))
    # (g) the decoder itself, on pairs that decode to structurally valid attestations
    pairs = []
    if {"INV-174", "INV-173", "INV-175", "ITV-711"} <= set(by_id):
        h174, h173 = delivered(by_id["INV-174"])[0], delivered(by_id["INV-173"])[0]
        import base64
        pairs = [("standard alphabet", h174, b64url_nopad(base64.b64decode(h174 + "=" * (-len(h174) % 4)))),
                 ("padding", h173, h173.rstrip("=")),
                 ("impossible length", delivered(by_id["INV-175"])[0], delivered(by_id["ITV-711"])[0])]
    check("R22 (g) decoder control pairs present (INV-173, INV-174, INV-175, ITV-711)", len(pairs) == 3)
    for name, bad, good_h in pairs:
        try:
            rb, rg = decode_attestation_header(bad), decode_attestation_header(good_h)
            ok = rb[0] is None and rg[0] is not None
        except Exception as exc:  # noqa: BLE001
            ok, rb = False, (None, f"exception {exc}")
        check(f"R22 (g) decoder: {name} rejected without exception, its corrected form accepted", ok, str(rb[1]))
    # (h) decoded content that the parse accepts or the interpreter cannot process: a controlled step 2 rejection
    good_v = next((v for v in sc if v["id"] == "ITV-711"), None)
    if good_v is not None:
        inp, env = good_v["test_metadata"]["input"], good_v["data"]
        hostile = {"a 5000-digit integer member": b'{"v":' + b"9" * 5000 + b"}",
                   "nesting 100000 levels deep": b"[" * 100000 + b"]" * 100000}
        for name, raw in hostile.items():
            try:
                got = receive_attestation(b64url_nopad(raw), env, **{k: inp[k] for k in KEYS})
            except Exception as exc:  # noqa: BLE001
                got = ("exception", type(exc).__name__)
            check(f"R22 (h) header with {name}: unauthorized at step 2, no exception", got == ("unauthorized", 2), str(got))


def main() -> int:
    vectors = strict_load("test-vectors/arsia-test-vectors.json")["vectors"]
    r1(); r2(vectors); r3(); r5(); r6(); r7(); r8(); r9(); r10(vectors); r11(); r12(); r13(vectors); r14(vectors)
    r15(vectors)
    r16(vectors); r17(vectors); r18(vectors); r19(vectors); r20(vectors); r21(vectors); r22(vectors)
    print()
    print("ALL RUNTIME RULES PASSED" if not FAIL else f"{len(FAIL)} FAILURES: {FAIL}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
