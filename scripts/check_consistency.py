# SPDX-License-Identifier: BUSL-1.1
# Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda)
"""Draft-02 consistency checks.

Runs the repository-level invariants that individual vector validation cannot
see: schema meta-validation, strict $ref resolution, profiles-catalog validity,
constant anti-regression (B-03/M-02/M-31), and cross-artifact spot checks.
Exit code 0 = all green.
"""
import base64
import glob
import json
import re
import sys

FAIL = []


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + (f"  {detail}" if detail and not cond else ""))
    if not cond:
        FAIL.append(name)


# Rows of the State §7.1 extension table that the schema deliberately does not
# enforce. Each needs a written reason; any other row must match the schema exactly.
AUDIT_EXTENSION_EXCEPTIONS = {
    "ict_incident": "extension promised by Assets §6.2 but no field is defined yet",
    "jwks_fetched_at": "runtime-conditional (signed messages only); tracked by A-58",
}

# State §7.1 base fields whose prose requiredness deliberately differs from the schema's
# top-level `required`. Each needs a written reason; any other divergence fails.
AUDIT_BASE_EXCEPTIONS = {}


def audit_extension_parity(state_text, audit_schema, tombstone_schema=None):
    """State §7.1 per-event-type extension table vs the audit-record schema (A-59).

    Returns a list of problems; empty means prose and schema agree.
    """
    problems = []
    header = "| Record type | REQUIRED extension fields |"
    if header not in state_text:
        return ["State §7.1 extension table not found (header marker missing)"]
    block = state_text[state_text.index(header):].split("\n\n", 1)[0].splitlines()[2:]
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in block if ln.startswith("|")]
    props = audit_schema.get("properties", {})
    enum_values = set()

    def collect_values(o):
        if isinstance(o, dict):
            if isinstance(o.get("enum"), list):
                enum_values.update(v for v in o["enum"] if isinstance(v, str))
            if isinstance(o.get("const"), str):
                enum_values.add(o["const"])
            for v in o.values():
                collect_values(v)
        elif isinstance(o, list):
            for v in o:
                collect_values(v)
    collect_values(audit_schema)

    def condition(entry):
        # single-field condition of an allOf/if entry -> (field, frozenset(values));
        # compound and nested conditions are matched against their own table rows below
        p = entry.get("if", {}).get("properties", {})
        if len(p) != 1 or any("properties" in v for v in p.values()):
            return None
        field, spec = next(iter(p.items()))
        vals = spec.get("enum", [spec["const"]] if "const" in spec else [])
        return field, frozenset(vals)

    single = {}
    multi = []
    for entry in audit_schema.get("allOf", []):
        c = condition(entry)
        then = entry.get("then", {})
        alts = {f for a in then.get("anyOf", []) for f in a.get("required", [])}
        if c is None:
            multi.append((entry.get("if", {}).get("properties", {}), set(then.get("required", []))))
        else:
            single[c] = (set(then.get("required", [])), alts)

    def spec_values(spec):
        return frozenset(spec.get("enum", [spec["const"]] if "const" in spec else []))

    def needs_row(cond_props):
        # DR-3/DR-4 conditions: covered records (intent) and nested resolution outcome
        return "intent" in cond_props or any("properties" in v for v in cond_props.values())

    matched_multi = set()
    exceptions_seen = set()
    covered = set()
    for cells in rows:
        if len(cells) < 3:
            problems.append(f"malformed row: {cells}")
            continue
        rtype, required_cell, optional_cell = cells[0], cells[1], cells[2]
        if "(exception)" in rtype:
            key = next((k for k in AUDIT_EXTENSION_EXCEPTIONS if k in rtype or k in required_cell), None)
            if key is None:
                problems.append(f"undeclared exception row: {rtype}")
            else:
                exceptions_seen.add(key)
            continue
        # parenthetical remarks state conditions (values, other objects), not fields
        required = set(re.findall(r"`([a-z_]+)`", re.sub(r"\([^)]*\)", "", required_cell)))
        optional = set(re.findall(r"`([a-z_]+)`", re.sub(r"\([^)]*\)", "", optional_cell)))
        for name in required | optional:
            if name not in props and name not in enum_values:
                problems.append(f"{rtype}: `{name}` is neither a schema property nor a schema value")
        rcond = re.sub(r"\([^)]*\)", "", rtype).strip()
        nested = re.match(r"`([a-z_]+)`\.`([a-z_]+)` = `([a-z_]+)`$", rcond)
        if " and " in rcond or nested:
            if nested:
                want = {nested.group(1): ("nested", nested.group(2), frozenset([nested.group(3)]))}
            else:
                want = {f: ("flat", None, frozenset(re.findall(r"`([a-z_]+)`", vals)))
                        for f, vals in re.findall(r"`([a-z_]+)` (?:=|∈) ((?:`[a-z_]+`(?:, )?)+)", rcond)}
            hit = None
            for i, (cond_props, req) in enumerate(multi):
                got = {}
                for f, spec in cond_props.items():
                    if "properties" in spec:
                        (sub, sspec), = spec["properties"].items()
                        got[f] = ("nested", sub, spec_values(sspec))
                    else:
                        got[f] = ("flat", None, spec_values(spec))
                if got == want:
                    hit = i
                    if req != required:
                        problems.append(f"{rtype}: table REQUIRED {sorted(required)} != schema {sorted(req)}")
            if hit is None:
                problems.append(f"{rtype}: no schema condition with exactly this compound/nested condition")
            else:
                matched_multi.add(hit)
            continue
        m = re.match(r"`([a-z_]+)` = (.+)$", rtype)
        if not m:
            if required:  # rows without a schema condition may only list optional fields
                problems.append(f"{rtype}: REQUIRED fields without a schema condition")
            continue
        field, vals = m.group(1), frozenset(re.findall(r"`([a-z_]+)`", m.group(2)))
        covered.add((field, vals))
        req_schema, alts = single.get((field, vals), (set(), set()))
        if req_schema != required:
            problems.append(f"{rtype}: table REQUIRED {sorted(required)} != schema {sorted(req_schema)}")
        if not alts <= optional:
            problems.append(f"{rtype}: schema alternatives {sorted(alts - optional)} not in table")
        if "exactly as applicable" in optional_cell:  # table alternatives must be schema anyOf
            tab_alts = set(re.findall(r"`([a-z_]+)`", re.sub(
                r"\([^)]*\)", "", optional_cell.split("exactly as applicable", 1)[1])))
            if tab_alts != alts:
                problems.append(f"{rtype}: table alternatives {sorted(tab_alts)} != schema anyOf {sorted(alts)}")
        for cond_props, req in multi:
            spec = cond_props.get(field, {})
            if spec.get("const") in vals and not req <= optional:
                problems.append(f"{rtype}: conditional {sorted(req - optional)} not in table")
    for key, (req, _alts) in single.items():
        if key not in covered and req:
            problems.append(f"schema condition {key[0]}={sorted(key[1])} has no table row")
    for i, (cond_props, req) in enumerate(multi):
        if needs_row(cond_props) and req and i not in matched_multi:
            problems.append(f"schema condition {sorted(cond_props)} has no table row")
    if exceptions_seen != set(AUDIT_EXTENSION_EXCEPTIONS):
        problems.append(f"exception rows {sorted(exceptions_seen)} != declared {sorted(AUDIT_EXTENSION_EXCEPTIONS)}")

    # base fields: §7.1 fields marked exactly "**REQUIRED.**" == schema top-level required
    start, end = "### 7.1 ArsiaAuditRecord Structure", "#### Per-event-type extension fields"
    if start not in state_text or end not in state_text:
        return problems + ["State §7.1 base-field section not found (heading marker missing)"]
    section = state_text[state_text.index(start):state_text.index(end)]
    parts = re.split(r"\n#### `([a-z_]+)`\n", section)
    prose_required = {name for name, body in zip(parts[1::2], parts[2::2])
                      if re.search(r"^- \*\*REQUIRED\.\*\*\s*$", body, re.M)}
    if not prose_required:
        problems.append("no REQUIRED base fields extracted from State §7.1 (marker moved?)")
    diverging = prose_required ^ set(audit_schema.get("required", []))
    if diverging != set(AUDIT_BASE_EXCEPTIONS):
        problems.append(f"base-field requiredness diverges on {sorted(diverging)}; "
                        f"declared exceptions {sorted(AUDIT_BASE_EXCEPTIONS)}")

    # reverse coverage (DR-5): every schema property is a §7.1 field entry or is named in
    # the extension table — an optional schema field cannot exist without prose
    full71 = state_text[state_text.index(start):state_text.index("### 7.2 ")]
    entries = set(re.findall(r"^#### `([a-z_]+)`", full71, re.M))
    table = full71[full71.index(header):].split("\n\n", 1)[0]
    named = set(re.findall(r"`([a-z_]+)`", table))
    undocumented = sorted(set(props) - entries - named)
    if undocumented:
        problems.append(f"schema properties without a §7.1 entry or table mention: {undocumented}")

    # chain fields (State §7.2): prose all-or-none group == schema dependentRequired
    group = {n for n, b in zip(parts[1::2], parts[2::2]) if "Present together with the other chain" in b}
    dep = audit_schema.get("dependentRequired", {})
    want = {f: sorted(group - {f}) for f in group}
    if not group:
        problems.append("no chain fields found in State §7.1 (marker moved?)")
    elif {k: sorted(v) for k, v in dep.items()} != want:
        problems.append(f"chain all-or-none: prose group {sorted(group)} != schema dependentRequired {dep}")

    # tombstone (State §7.2): schema field set == the prose list "containing exactly ..."
    if tombstone_schema is not None:
        m = re.search(r"containing exactly (.+?)\. A tombstone carries", state_text, re.S)
        listed = set(re.findall(r"`([a-z_]+)`", re.sub(r"\([^)]*\)", "", m.group(1)))) if m else set()
        if not listed:
            problems.append("State §7.2 tombstone field list not found (marker moved?)")
        elif listed != set(tombstone_schema.get("properties", {})) or listed != set(tombstone_schema.get("required", [])):
            problems.append(f"tombstone fields: prose {sorted(listed)} != schema {sorted(tombstone_schema.get('properties', {}))}")
    return problems


# Tampered chain vectors (State §7.2): schema-valid on their own; each, substituted for its
# base vector, MUST fail chain verification with the stated reason. Carried here, outside
# the vector format, until the vector cycle adds an explicit field (see the A-34 proxy note).
CHAIN_TAMPERED = {
    "ITV-597": ("ITV-593", "chain value mismatch"),
    "ITV-602": ("ITV-594", "chain value mismatch"),
    "ITV-598": ("ITV-594", "foreign chain_id"),
    "ITV-599": ("ITV-595", "tombstone previous value mismatch"),
}


# ------------------------------------ DR-3/DR-4: effective obligation resolution (Core §4.3.10)
def resolution_vector_mismatches(vectors, rh):
    """Runtime vectors stating a scenario: their expected results equal the reference resolver's."""
    out = []
    for v in vectors:
        meta = v.get("test_metadata", {})
        if meta.get("scenario") in ("resolution", "router", "execution"):
            got = rh.execution_case(meta["input"]) if meta["scenario"] == "execution" else rh.scenario_result(meta)
            miss = rh.subset_match(meta["expect"], got)
            if miss:
                out.append(f"{v['id']}: {', '.join(miss)}")
    return out


def a32_equivalence(rh):
    """A-32: absent profile and explicit GDPR-STANDARD give the same verdict, diagnostics and effective
    values; provenance keeps the difference in fill source and declared profile."""
    out = []

    def sem(r):
        return (r["outcome"], [c["diagnostic"] for c in r.get("conflicts", [])],
                {k: (a["status"], a["result"]) for k, a in r["axes"].items()})

    for cls in (None, "limited-risk", "high-risk"):
        ident = cls and {"agent_id": "agent:acme.analyst", "ai_system_classification": cls, "evidence": rh.TEST_EVIDENCE}
        for mode in (None, "not_required", "required_before_execution", "required_within_24h", "required_post_execution"):
            extra = {} if mode is None else {"human_oversight": mode}
            a = rh.resolve_obligations("request", dict(extra), ident)
            b = rh.resolve_obligations("request", dict(extra, profile="GDPR-STANDARD"), ident)
            if sem(a) != sem(b):
                out.append(f"{cls}/{mode}: {sem(a)} != {sem(b)}")
            for k in a["axes"]:
                fa, fb = (a["axes"][k]["fill"] or {}).get("source"), (b["axes"][k]["fill"] or {}).get("source")
                if fa == "no-profile-default" and fb != "profile-default":
                    out.append(f"{cls}/{mode}/{k}: fill source not preserved ({fa} vs {fb})")
            if a["profile"]["declared"] is not None or b["profile"]["declared"] != "GDPR-STANDARD":
                out.append(f"{cls}/{mode}: declared profile not preserved")
    return out


def obligation_rules_table_parity(core, rules):
    """Core §4.3.10.3 table states the artifact's values: scope, trigger, requirements, exceptions."""
    head = "| Entry `id` | Scope | Trigger | Requirements | Exceptions |"
    if head not in core:
        return ["Core §4.3.10.3 table not found (header marker missing)"]
    rows = {}
    for ln in core[core.index(head):].split("\n\n", 1)[0].splitlines()[2:]:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        m = re.match(r"`([a-z0-9-]+)`$", cells[0])
        if m and len(cells) == 5:
            rows[m.group(1)] = cells[1:]
    out = []
    ids = [r["id"] for r in rules["rules"]]
    if sorted(rows) != sorted(ids):
        out.append(f"table entries {sorted(rows)} != artifact {sorted(ids)}")
    for r in rules["rules"]:
        if r["id"] not in rows:
            continue
        scope, trig, reqs, exc = rows[r["id"]]
        intents = r["scope"]["intents"]
        want_scope = "all intents" if intents == "all" else ", ".join(f"`{i}`" for i in intents)
        if scope != want_scope:
            out.append(f"{r['id']} scope: table {scope!r} != artifact {want_scope!r}")
        t = r["trigger"]
        if "fact" in t:
            need = [f"`{t['fact']}`", f'`"{t["equals"]}"`']
            need += ["authenticated IdentityRecord"] if "identity-record" in t["from"] else []
            need += ["per-message declaration"] if "message-declaration" in t["from"] else []
        elif "field" in t:
            need = [f"`{t['field']}` is `{str(t['equals']).lower()}`"]
        else:
            need = [f"defines `{t['profile_member']}`"]
        out += [f"{r['id']} trigger: table lacks {n!r}" for n in need if n not in trig]
        want = []
        for q in r["requirements"]:
            if q["kind"] == "restriction":
                want.append(f"`{q['axis']}`: restriction, excludes " + ", ".join(f'`"{x}"`' for x in q["excludes"]))
            elif q["kind"] == "value":
                want.append(f"`{q['axis']}`: `{str(q['value']).lower()}`")
            else:
                want.append(f"`{q['axis']}`: floor equal to `retention_minimum`")
        got = [p.strip() for p in reqs.split(";")]
        if sorted(got) != sorted(want):
            out.append(f"{r['id']} requirements: table {got} != artifact {want}")
        want_exc = [f"`{e['axis']}`: explicit `false` is overridden (Rule 7)"
                    for e in r["exceptions"] if e["effect"] == "override"] or ["—"]
        if [p.strip() for p in exc.split(";")] != want_exc:
            out.append(f"{r['id']} exceptions: table {exc!r} != artifact {want_exc}")
    return out


def diagnostic_parity(core, audit_schema, rules, rules_schema):
    """Core §4.3.10.6: the diagnostic table equals the audit conflict enum; the artifact's diagnostics are
    in the table and belong to the rule they cite; the artifact-schema enum is a subset of the table."""
    head = "| Failure | `details` diagnostic |"
    if head not in core:
        return ["Core §4.3.10.6 table not found (header marker missing)"]
    table = {}
    for ln in core[core.index(head):].split("\n\n", 1)[0].splitlines()[2:]:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        m = re.match(r"`([a-z_0-9]+): true`", cells[1]) if len(cells) == 2 else None
        if m:
            table[m.group(1)] = set(re.findall(r"Rule (\d)", cells[0]))
    out = []
    enum = audit_schema["$defs"]["conflict"]["properties"]["diagnostic"]["enum"]
    if sorted(table) != sorted(enum):
        out.append(f"table diagnostics {sorted(table)} != audit conflict enum {sorted(enum)}")
    for r in rules["rules"]:
        cited = set(re.findall(r"Rule (\d)", r["reference"]))
        for q in r["requirements"]:
            d = q.get("diagnostic")
            if d and d not in table:
                out.append(f"{r['id']}: diagnostic {d} not in the Core table")
            elif d and not (table[d] & cited):
                out.append(f"{r['id']}: diagnostic {d} belongs to Rule {sorted(table[d])}, rule cites {sorted(cited)}")
    extra = set(rules_schema["$defs"]["diagnostic"]["enum"]) - set(table)
    if extra:
        out.append(f"rules-schema diagnostics not in the Core table: {sorted(extra)}")
    return out


def decision_example_problems(identity_text, onboarding_schema, registry, rh):
    """Identity §7.6 decision example validates against its schema; its context_sha256 recomputes."""
    from jsonschema import Draft202012Validator
    blocks = [b for b in re.findall(r"```json\n(.*?)\n```", identity_text, re.S)
              if '"arsiaprotocol.onboarding/decision"' in b and '"authenticated_context"' in b]
    if len(blocks) != 1:
        return [f"expected one Identity §7.6 decision example with authenticated_context, found {len(blocks)}"]
    ex = json.loads(blocks[0])
    out = [f"schema: {e.message[:90]}" for e in
           list(Draft202012Validator(onboarding_schema, registry=registry).iter_errors(ex))[:3]]
    ctx = ex["args"]["authenticated_context"]
    if rh.context_digest(ctx) != ctx.get("context_sha256"):
        out.append("context_sha256 does not recompute (Identity §7.2 Step 7 formula)")
    return out


def retention_derivation_problems(vectors, rh):
    """State §7.1: a record's retention fields equal those derived from its obligation_resolution."""
    out = []
    for v in vectors:
        if v.get("expected") != "valid":
            continue
        d = v.get("data", {})
        recs = [d] if v.get("schema_ref") == "arsia-audit-record.schema.json" else (
            d.get("records", []) if v.get("schema_ref") == "arsia-audit-query-response.schema.json" else [])
        for r in recs:
            if "obligation_resolution" in r:
                want = rh.legacy_retention(r["obligation_resolution"], r["processed_at"])
                got = {k: r.get(k) for k in want}
                if got != want:
                    out.append(f"{v['id']}: {got} != {want}")
    return out


def source_digest_problems(vectors, rules, catalog, rh):
    """Every recorded source digest recomputes from the artifact entry or the catalog entry it names."""
    rule_d = {r["id"]: rh.jcs_sha256(r) for r in rules["rules"]}
    prof_d = {n: rh.jcs_sha256(p) for n, p in catalog["profiles"].items()}
    out = []

    def walk(o, vid):
        if isinstance(o, dict):
            if o.get("class") == "protocol-rule" and rule_d.get(o.get("id")) != o.get("sha256"):
                out.append(f"{vid}: protocol-rule {o.get('id')} digest")
            if o.get("class") == "profile-floor" and prof_d.get(o.get("id")) != o.get("sha256"):
                out.append(f"{vid}: profile-floor {o.get('id')} digest")
            if set(o) == {"name", "sha256"} and o["name"] in prof_d and prof_d[o["name"]] != o["sha256"]:
                out.append(f"{vid}: profile {o['name']} digest")
            for x in o.values():
                walk(x, vid)
        elif isinstance(o, list):
            for x in o:
                walk(x, vid)
    for v in vectors:
        walk(v.get("data"), v["id"])
        walk(v.get("message"), v["id"])
    return out


def eu_list_problems(routing, rh):
    """Routing §5.2: the dated EU member list is sorted, equals the resolver's, and its digest recomputes."""
    m = re.search(r"\*\*Member list, revision `(\d{4}-\d{2})`\.\*\*(.*?)\n\n", routing, re.S)
    if not m:
        return ["Routing §5.2 member list not found (marker missing)"]
    codes = re.findall(r"`([A-Z]{2})`", m.group(2))
    digest = re.search(r"`sha256:([0-9a-f]{64})`", m.group(2))
    out = []
    if codes != sorted(set(codes)):
        out.append("member list not sorted or not unique")
    if codes != rh.EU_MEMBERS or m.group(1) != rh.EU_REVISION:
        out.append("member list or revision differs from the reference resolver")
    if not digest or digest.group(1) != rh.jcs_sha256(codes):
        out.append("declared digest does not recompute")
    return out


# ------------------------------- DR-1/DR-2: executor oversight sources and post-execution review
def _envelope(v):
    return v.get("message") or v.get("data")


ACTION_ID_EXEMPT = {"CTV-08", "ITV-86"}  # pre-existing non-conformant action_id; vector cycle (ledger notes)


def migrated_oversight_problems(vectors, schemas, reg, rh):
    """Migrated pending_approval / approval_decision vectors recompute from test_metadata.reference_request;
    a valid pending's reference request is accepted with prior approval in its effective set."""
    from jsonschema import Draft202012Validator
    by_id = {v["id"]: v for v in vectors}
    desc_v = Draft202012Validator(schemas["arsia-action-descriptor.schema.json"], registry=reg)
    out = []
    for v in vectors:
        m = _envelope(v)
        if not isinstance(m, dict) or m.get("intent") not in ("pending_approval", "approval_decision") \
                or "event_type" in m:
            continue
        ref = v.get("test_metadata", {}).get("reference_request")
        if ref is None:
            out.append(f"{v['id']}: no reference_request")
            continue
        if m["intent"] == "approval_decision":
            if "pending_vector" in ref:
                want = _envelope(by_id[ref["pending_vector"]])["payload"]["args"]["request_payload_hash"]
            else:
                want = rh.payload_hash({"payload": ref["payload"]})
            got = m["payload"]["result"].get("request_payload_hash")
            if got != want and not (got is None and v.get("valid") is False):
                out.append(f"{v['id']}: request_payload_hash != reference")
            continue
        if "vector" in ref:
            req = by_id[ref["vector"]]["message"]
            if (req["id"], req["payload"], req.get("compliance")) != (ref["id"], ref["payload"], ref.get("compliance")):
                out.append(f"{v['id']}: reference_request differs from {ref['vector']}")
        ex = ref["executor"]
        errs = [e.message for e in desc_v.iter_errors(ex["descriptor"])]
        if v["id"] in ACTION_ID_EXEMPT:  # the pending's own action_id is not a valid action_id (notes)
            errs = [e for e in errs if ex["descriptor"]["action_id"] not in e]
        if errs:
            out.append(f"{v['id']}: reference descriptor schema-invalid: {errs[0][:60]}")
        srcs = rh.executor_sources(ex["descriptor"]["action_id"], ex["descriptor"], ex.get("claim"),
                                   ref["capabilities"], ex.get("assessment"))
        res = rh.resolve_obligations("request", ref.get("compliance"), None, ref["ts"], executor=srcs,
                                     review_config=dict(rh.FULL_REVIEW_CONFIG, post_execution_review_period=None))
        args = m["payload"]["args"]
        valid = v.get("valid", v.get("expected") == "valid")
        absent_ok = lambda x: x is None and valid is False  # the deliberate cause of a negative vector
        if args.get("request_payload_hash") != rh.payload_hash({"payload": ref["payload"]}) and \
                not absent_ok(args.get("request_payload_hash")):
            out.append(f"{v['id']}: request_payload_hash != SHA-256 of the reference payload")
        if m["payload"].get("obligation_resolution") != res and not absent_ok(m["payload"].get("obligation_resolution")):
            out.append(f"{v['id']}: obligation_resolution != reference resolver")
        if valid is True and (res["outcome"] != "accepted"
                              or "required_before_execution" not in (res["axes"]["oversight"]["result"] or [])):
            out.append(f"{v['id']}: valid pending whose reference request is not accepted with prior approval")
    return out


def onboarding_policy_problems(vectors, schemas, reg, rh):
    """Identity §7.6/§8.1/§8.3: policy_sha256 recomputes from the reference policy, whose evaluation
    over the effective capabilities reproduces freely_allowed and oversight_required."""
    from jsonschema import Draft202012Validator
    pol_v = Draft202012Validator(schemas["arsia-capability-policy.schema.json"], registry=reg)
    out = []
    for v in vectors:
        d = v.get("data") if v.get("schema_ref") == "arsia-onboarding-decision.schema.json" else None
        payload = v["message"].get("payload") if isinstance(v.get("message"), dict) else None
        if d is None and isinstance(payload, dict) and payload.get("type") == "arsiaprotocol.onboarding/decision":
            d = payload
        if not d or d.get("args", {}).get("decision") != "approved":
            continue
        args, pol = d["args"], v.get("test_metadata", {}).get("reference_policy")
        if pol is None:
            out.append(f"{v['id']}: no reference_policy")
            continue
        if list(pol_v.iter_errors(pol)):
            out.append(f"{v['id']}: reference policy schema-invalid")
        if pol["policy_version"] != args.get("policy_version"):
            out.append(f"{v['id']}: policy_version differs from the reference policy")
        if "policy_sha256" in args and args["policy_sha256"] != rh.jcs_sha256(pol):
            out.append(f"{v['id']}: policy_sha256 does not recompute")
        status = {r["capability"]: r["status"] for r in pol["capabilities"]}
        caps = args["effective_capabilities"]
        if [c for c in caps if status.get(c) == "allowed"] != args["freely_allowed"] or \
                [c for c in caps if status.get(c) == "oversight_required"] != args["oversight_required"]:
            out.append(f"{v['id']}: lists differ from the §8.3 evaluation of the reference policy")
    return out


def closed_member_problems(actions, core, schemas):
    """Prose member lists == closed schema definitions (A-78; Actions §3.9.3; Core §6.1)."""
    msg, out = schemas["arsia-message.schema.json"], []
    s32 = actions[actions.index("#### Step 2: Construct the `pending_approval` message."):]
    block = s32.split("```json")[1].split("```")[0]
    args = re.findall(r'^\s+"([a-z_]+)":', block[block.index('"args"'):block.index("\n  }")], re.M)
    pa = msg["$defs"]["pending-approval-args"]
    if set(args) != set(pa["properties"]) or pa.get("additionalProperties") is not False:
        out.append(f"Actions §3.2 args {sorted(args)} != schema {sorted(pa['properties'])} (closed: "
                   f"{pa.get('additionalProperties') is False})")
    s393 = actions[actions.index("#### 3.9.3 Messages"):actions.index("#### 3.9.4")]
    blocks = [json.loads(re.sub(r"\"<[^\"]*>\"", "\"x\"", b.split("```")[0])) for b in s393.split("```json")[1:]]
    for b, name in zip(blocks, ("review-pending-data", "review-decision-data")):
        d = msg["$defs"][name]
        if set(b["data"]) != set(d["properties"]) or set(d["required"]) != set(d["properties"]) or \
                d.get("additionalProperties") is not False:
            out.append(f"Actions §3.9.3 {name} members != closed schema")
    m = re.search(r"\*\*Overdue notice\.\*\*.*?contains\s+exactly (.*?) of the overdue", s393, re.S)
    od = msg["$defs"]["review-overdue-data"]
    if not m or set(re.findall(r"`([a-z_]+)`", m.group(1))) != set(od["properties"]) or \
            od.get("additionalProperties") is not False:
        out.append("Actions §3.9.3 overdue notice members != closed schema")
    para = core[core.index("**`arsia_oversight`.**"):].split("\n\n")[0]
    jwt = schemas["arsia-jwt-claims.schema.json"]["properties"]["arsia_oversight"]
    if set(re.findall(r"`([a-z_]+)` —", para)) != set(jwt["properties"]) or \
            set(re.findall(r"`([a-z0-9_]+)` \(", para)) != set(jwt["properties"]["policy"]["properties"]):
        out.append("Core §6.1 arsia_oversight members != JWT schema")
    return out


def executor_prefix_problems(core, rh):
    row = next(l for l in core.splitlines() if l.startswith("| `executor-policy` |"))
    prefixes = tuple(sorted(set(re.findall(r"`([a-z-]+:)<", row))))
    return [] if prefixes == tuple(sorted(rh.EXECUTOR_SOURCE_PREFIXES)) else \
        [f"Core §4.3.10.2 {prefixes} != harness {rh.EXECUTOR_SOURCE_PREFIXES}"]


def replaced_rule_echoes():
    """A-3/A-4 and DR-1 anti-regression: wording of the replaced rules is gone."""
    out = []
    for f in sorted(glob.glob("spec/*.md") + glob.glob("schemas/*.json")):
        text = open(f, encoding="utf-8").read()
        for needle in ("oversight_timeout", "SHOULD annotate the message", "Transfer\ndenied by human oversight",
                       "Prohibition on unnecessary oversight", "human MUST review within 24 hours"):
            if needle in text:
                out.append(f"{f}: {needle!r}")
    return out


def main() -> int:
    from jsonschema import Draft202012Validator

    schema_files = sorted(glob.glob("schemas/*.schema.json")) + [
        "schemas/arsia-test-vectors.meta.json"
    ]
    schemas = {}
    for f in schema_files:
        j = json.load(open(f))
        schemas[f.split("/")[-1]] = j
        try:
            Draft202012Validator.check_schema(j)
            ok = True
        except Exception:
            ok = False
        check(f"meta-valid {f}", ok)

    # $id scheme uniform (N-05)
    for name, j in schemas.items():
        check(
            f"$id scheme {name}",
            j.get("$id") == f"https://arsiaprotocol.org/schemas/v2.0/{name}",
            j.get("$id", "MISSING"),
        )

    # strict resolution of the message schema (N-05)
    try:
        from referencing import Registry, Resource

        reg = Registry().with_resources(
            [(j["$id"], Resource.from_contents(j)) for j in schemas.values()]
        )
        v = Draft202012Validator(schemas["arsia-message.schema.json"], registry=reg)
        doc = json.load(open("test-vectors/arsia-test-vectors.json"))
        sample = next(x for x in doc["vectors"] if x["id"] == "CTV-01")["message"]
        check("strict $ref resolution (CTV-01)", not list(v.iter_errors(sample)))
    except ImportError:
        print("skip strict-resolution check (referencing not installed)")

    # profiles catalog validates against its own schema (N-02)
    catalog = json.load(open("profiles/arsia-compliance-profiles.json"))
    errs = list(
        Draft202012Validator(schemas["arsia-compliance-profiles.schema.json"]).iter_errors(catalog)
    )
    check("profiles catalog valid", not errs, "; ".join(e.message[:60] for e in errs[:3]))

    # constant anti-regression: no 1825 in normative artifacts (B-03)
    hits = []
    for f in glob.glob("spec/*.md") + glob.glob("schemas/*.json") + [
        "profiles/arsia-compliance-profiles.json"
    ]:
        for i, line in enumerate(open(f, encoding="utf-8"), 1):
            if "1825" in line and "Draft-01" not in line and "compatibility" not in line:
                hits.append(f"{f}:{i}")
    check("no 1825 outside compat notes (B-03)", not hits, ",".join(hits[:5]))

    # duration anti-regression: no day-integer retention statements in State/Assets (F2)
    hits2 = []
    for f in ("spec/ARSIA-State.md", "spec/ARSIA-Assets.md"):
        for i, line in enumerate(open(f, encoding="utf-8"), 1):
            if re.search(r"before 180 days|180-day minimum|before 730 days|\| 180 days|\| 730 days", line):
                hits2.append(f"{f}:{i}")
    check("no day-integer retention statements (D1)", not hits2, ",".join(hits2[:5]))

    # schema descriptions must not describe v2 behavior via removed *_days fields (D1)
    def desc_hits(obj, path, out):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if (
                    k == "description"
                    and isinstance(v, str)
                    and "retention_days" in v
                    and "Draft-01" not in v
                ):
                    out.append(path)
                else:
                    desc_hits(v, f"{path}/{k}", out)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                desc_hits(v, f"{path}/{i}", out)

    hits3 = []
    for name, j in schemas.items():
        desc_hits(j, name, hits3)
    check("no retention_days in schema descriptions (D1)", not hits3, ",".join(hits3[:5]))

    # vector descriptions must not narrate removed Draft-01 retention_days semantics (D1)
    vec_doc = json.load(open("test-vectors/arsia-test-vectors.json"))
    hits4 = []
    for v in vec_doc["vectors"]:
        desc = v.get("description", "")
        if "retention_days" in desc and "Draft-01" not in desc and "not a valid property" not in desc:
            hits4.append(v["id"])
    check("no retention_days in vector descriptions (D1)", not hits4, ",".join(hits4[:5]))

    # vector IDs must be unique (a re-run generator once risked silent duplication)
    from collections import Counter

    vec_ids = [v["id"] for v in vec_doc["vectors"]]
    vec_dupes = sorted(k for k, n in Counter(vec_ids).items() if n > 1)
    check("no duplicate test-vector IDs", not vec_dupes, ",".join(vec_dupes[:5]))

    # RTM requirement IDs must be unique (a duplicated stale listing once inflated counts)

    rtm_id = re.compile(r"^\|\s*([A-Z]+-§[^|]+?)\s*\|", re.M)
    hits5 = []
    for f in sorted(glob.glob("docs/rtm/*.rtm.md")):
        ids = rtm_id.findall(open(f, encoding="utf-8").read())
        dupes = [k for k, n in Counter(ids).items() if n > 1]
        hits5 += [f"{f}:{d}" for d in dupes]
    check("no duplicate RTM requirement IDs", not hits5, ",".join(hits5[:5]))

    # retention minimums in catalog match the normative values (D1/M-02)
    expected = {
        "GDPR-STANDARD": None,
        "EU-AI-ACT-HIGH-RISK": "P6M",
        "EU-AI-ACT-LIMITED-RISK": "P90D",
        "MIFID-II": "P1827D",
        "PAC-AGRICULTURE": "P1096D",
        "DSA-VLOP": "P1096D",
        "DORA": "P1827D",
    }
    for prof, want in expected.items():
        got = catalog["profiles"][prof]["defaults"].get("retention_minimum")
        check(f"retention_minimum {prof}", got == want, f"got {got!r}, want {want!r}")

    # clock_skew_seconds parity: catalog vs State §6 tables (M-01)
    state = open("spec/ARSIA-State.md", encoding="utf-8").read()
    for prof, skew in [("EU-AI-ACT-HIGH-RISK", 120), ("MIFID-II", 60), ("DORA", 60)]:
        cat_v = catalog["profiles"][prof]["defaults"].get("clock_skew_seconds")
        check(f"clock_skew catalog {prof}", cat_v == skew, str(cat_v))
    check("clock_skew in State tables", state.count("`clock_skew_seconds`") >= 3)

    # wire version coherence (D5)
    msg = schemas["arsia-message.schema.json"]
    check("message schema v const 2.0", msg["properties"]["v"].get("const") == "2.0")
    core = open("spec/ARSIA-Core.md", encoding="utf-8").read()
    check("no v=1 media type left", "arsia+json; v=1" not in core)

    # reserved-capability registry parity: Actions §1.4 vs descriptor-schema enum (B-04)
    actions = open("spec/ARSIA-Actions.md", encoding="utf-8").read()
    prose_caps = set(re.findall(r"^#### `(arsiaprotocol\.[a-z0-9.]+)`", actions, re.M))
    desc = schemas["arsia-action-descriptor.schema.json"]
    enum_caps = set()
    def collect(o):
        if isinstance(o, dict):
            e = o.get("enum")
            if isinstance(e, list) and any(str(x).startswith("arsiaprotocol.") for x in e):
                enum_caps.update(e)
            for v_ in o.values():
                collect(v_)
        elif isinstance(o, list):
            for v_ in o:
                collect(v_)
    collect(desc)
    check(
        "capability registry parity (§1.4 == descriptor enum)",
        prose_caps == enum_caps,
        f"prose-only={sorted(prose_caps-enum_caps)} enum-only={sorted(enum_caps-prose_caps)}",
    )

    # ---- prose-enum <-> schema-enum parity (generalized table extraction) ----
    # Each entry: (label, prose extractor, schema enum set). A prose enum listing
    # and its schema enum MUST be set-equal — guards the N-06/M-06/A-04/B-06 class.

    def prose_values(text, start_marker, stop_prefix="- **"):
        """Backticked \"value\" tokens from start_marker's line through following
        continuation lines, stopping at the next bullet attribute or at the first
        em-dash explanation (which may mention non-member values)."""
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if start_marker in line:
                block = [line.split(" — ")[0]]
                if " — " not in line:
                    for nxt in lines[i + 1:]:
                        if nxt.lstrip().startswith(stop_prefix):
                            break
                        if " — " in nxt:
                            block.append(nxt.split(" — ")[0])
                            break
                        block.append(nxt)
                return set(re.findall(r'`"([a-z0-9_.-]+)"`', "\n".join(block)))
        return set()

    def schema_enum(schema, prop_name):
        out = []
        def walk(o):
            if isinstance(o, dict):
                p = o.get("properties")
                if isinstance(p, dict) and prop_name in p:
                    def grab(node):
                        if isinstance(node, dict):
                            if isinstance(node.get("enum"), list):
                                out.append(set(node["enum"]))
                            for v_ in node.values():
                                grab(v_)
                        elif isinstance(node, list):
                            for v_ in node:
                                grab(v_)
                    grab(p[prop_name])
                for v_ in o.values():
                    walk(v_)
            elif isinstance(o, list):
                for v_ in o:
                    walk(v_)
        walk(schema)
        return out

    state = open("spec/ARSIA-State.md", encoding="utf-8").read()
    cf = schemas["arsia-compliance-field.schema.json"]

    parities = [
        ("legal_basis prose == schema (N-06)",
         prose_values(core, "- **Enum (Art. 6(1) bases):**")
         | prose_values(core, "- **Enum (Art. 9(2) conditions"),
         schema_enum(cf, "legal_basis")),
        ("human_oversight prose == schema (B-06 class)",
         prose_values(core, '- **Enum:** `"not_required"`'),
         schema_enum(cf, "human_oversight")),
        ("ai_system_classification prose == schema (M-23)",
         prose_values(core, '- **Enum:** `"minimal-risk"`'),
         schema_enum(cf, "ai_system_classification")),
        ("audit event_type prose == schema (M-06)",
         prose_values(state, '- **Enum:** `"request"`'),
         schema_enum(schemas["arsia-audit-record.schema.json"], "event_type")),
    ]
    for label, prose_set, enum_sets in parities:
        # full enum (largest) must equal prose; conditional sub-enums must be subsets
        full = max(enum_sets, key=len) if enum_sets else set()
        ok = (bool(prose_set) and bool(enum_sets) and prose_set == full
              and all(s <= full for s in enum_sets))
        detail = "" if ok else (
            f"prose={sorted(prose_set)[:6]} schema={sorted(full)[:6]}"
            if prose_set and enum_sets else "extraction returned empty — marker moved?"
        )
        check(label, ok, detail)

    # audit-record extension fields: State §7.1 table == schema conditionals (A-59)
    probs = audit_extension_parity(state, schemas["arsia-audit-record.schema.json"],
                                   schemas["arsia-audit-chain-tombstone.schema.json"])
    check("audit extension table == schema conditionals (A-59)", not probs, "; ".join(probs[:4]))

    # A-29 disposition: Core's SHOULD reconnect and Routing's MUST back off both hold; if
    # either modal changes, the disposition must be re-examined.
    routing = open("spec/ARSIA-Routing.md", encoding="utf-8").read()
    flat = lambda s: re.sub(r"\s+", " ", s)
    check("A-29 reconnection modals (Core SHOULD reconnect; Routing MUST back off)",
          "the client SHOULD attempt to reconnect using exponential backoff" in flat(core)
          and "the client MUST implement exponential backoff for reconnection" in flat(routing))

    # F-3: the non-BMP signed vector discriminates RFC 8785 (UTF-16 code unit) key order
    # from code-point order — RFC 8785 bytes verify, code-point bytes do not (Core §5.1)
    import copy
    import rfc8785
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    vec = next((v for v in vec_doc["vectors"] if v["id"] == "ITV-590"), None)
    ok, detail = False, "ITV-590 missing"
    if vec:
        m = copy.deepcopy(vec["message"])
        sig = m["security"].pop("sig")
        jcs_bytes = rfc8785.dumps(m)
        cp_bytes = json.dumps(m, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(vec["crypto"]["public_key_hex"]))
        raw = base64.urlsafe_b64decode(sig + "=" * (-len(sig) % 4))

        def verifies(data):
            try:
                key.verify(raw, data)
                return True
            except InvalidSignature:
                return False
        ok = (jcs_bytes.hex() == vec["crypto"]["canonical_bytes_hex"] and cp_bytes != jcs_bytes
              and verifies(jcs_bytes) and not verifies(cp_bytes))
        detail = f"jcs==hex {jcs_bytes.hex() == vec['crypto']['canonical_bytes_hex']}, differs {cp_bytes != jcs_bytes}"
    check("F-3 non-BMP vector: RFC 8785 order verifies, code-point order does not (ITV-590)", ok, detail)

    # DR-5: recompute the chain of every chained vector (State §7.2) so vectors cannot drift
    sys.path.insert(0, "scripts")
    from runtime_harness import verify_chain
    chain_refs = ("arsia-audit-record.schema.json", "arsia-audit-chain-tombstone.schema.json")
    chained = [v for v in vec_doc["vectors"] if v.get("schema_ref") in chain_refs
               and v.get("expected") == "valid" and "chain_id" in v.get("data", {})]
    by_id = {v["id"]: v for v in chained}
    chains = {}
    for v in chained:
        if v["id"] not in CHAIN_TAMPERED:
            chains.setdefault(v["data"]["chain_id"], []).append(v)
    bad_chains = []
    for cid, vs in chains.items():
        vs.sort(key=lambda v: v["data"]["chain_seq"])
        last = vs[-1]["data"]
        ok_, why, _ = verify_chain([v["data"] for v in vs], (cid, last["chain_seq"], last["hash_chain"]))
        if not ok_:
            bad_chains.append(f"{cid}: {why} ({', '.join(v['id'] for v in vs)})")
    check(f"DR-5 chained vectors recompute and verify ({len(chains)} chains, {len(chained) - len(CHAIN_TAMPERED)} entries)",
          len(chains) >= 2 and not bad_chains, "; ".join(bad_chains) or f"only {len(chains)} chains")
    bad_t = []
    for tid, (base_id, reason) in CHAIN_TAMPERED.items():
        if tid not in by_id or base_id not in by_id:
            bad_t.append(f"{tid}/{base_id} missing")
            continue
        base = by_id[base_id]["data"]
        vs = [by_id[tid]["data"] if v["id"] == base_id else v["data"]
              for v in chains.get(base["chain_id"], [])]
        last = chains[base["chain_id"]][-1]["data"]
        ok_, why, _ = verify_chain(vs, (base["chain_id"], last["chain_seq"], last["hash_chain"]))
        if ok_ or why != reason:
            bad_t.append(f"{tid}: expected '{reason}', got ({ok_}, {why})")
    check("DR-5 tampered chain vectors fail verification with the stated reason (ITV-597..599, ITV-602)",
          not bad_t, "; ".join(bad_t))

    # error-code registry: Core §11.2 table == every standard-code enum copy (A-04)
    prose_codes = set(re.findall(r"^\| `([a-z_]+)`\s*\|\s*\d{3}\s*\|", core, re.M))
    code_enums = [s for s in schema_enum(schemas["arsia-message.schema.json"], "code")
                  if "invalid_request" in s]
    ok = bool(prose_codes) and bool(code_enums) and all(prose_codes == s for s in code_enums)
    check("error-code registry §11.2 == schema enum copies (A-04)", ok,
          "" if ok else f"prose-only={sorted(prose_codes - (code_enums[0] if code_enums else set()))} "
                        f"schema-only={sorted((code_enums[0] if code_enums else set()) - prose_codes)}")

    # ---- RTM drift linter: near-duplicate requirements with diverging modal/values ----
    # Contradictions are born as restatements that drift (1825-vs-1827, clamp-vs-reject,
    # SHOULD-vs-MUST). Flags cross-document requirement pairs whose normalized text is
    # near-identical but whose modal strength/polarity or embedded values differ.

    STOP = {"the", "a", "an", "of", "to", "in", "for", "is", "are", "be", "and", "or",
            "with", "by", "on", "at", "its", "this", "that", "must", "should", "may",
            "not", "shall", "required", "recommended", "optional", "agent", "message"}
    VALUE = re.compile(r"P\d+[DMY]|P\d+[DMY]?\d*[DMY]|\b\d+\b|\"[a-z0-9_-]+\"")
    STRENGTH = {"MUST": 2, "MUST_NOT": 2, "REQUIRED": 2, "SHALL": 2,
                "SHOULD": 1, "SHOULD_NOT": 1, "RECOMMENDED": 1, "NOT_RECOMMENDED": 1,
                "MAY": 0, "OPTIONAL": 0}
    NEGATIVE = {"MUST_NOT", "SHOULD_NOT", "NOT_RECOMMENDED"}

    def drift_pairs(rows, jaccard_threshold=0.8):
        """rows: (id, modal, requirement). Returns flagged (id_a, id_b, reason)."""
        toks = []
        for rid, modal, req in rows:
            words = frozenset(w for w in re.findall(r"[a-z0-9_.]+", req.lower())
                              if len(w) > 2 and w not in STOP)
            vals = frozenset(VALUE.findall(req))
            toks.append((rid, modal, words, vals))
        index = {}
        for i, (_, _, words, _) in enumerate(toks):
            for w in words:
                index.setdefault(w, []).append(i)
        flagged, seen = [], set()
        for i, (rid, modal, words, vals) in enumerate(toks):
            if len(words) < 5:
                continue
            cand = {j for w in words for j in index[w] if j > i}
            for j in cand:
                rjd, mj, wj, vj = toks[j]
                if rid.split("-§")[0] == rjd.split("-§")[0]:
                    continue  # cross-document only
                if len(wj) < 5 or (i, j) in seen:
                    continue
                seen.add((i, j))
                inter = len(words & wj)
                if inter / len(words | wj) < jaccard_threshold:
                    continue
                sa, sb = STRENGTH.get(modal, 1), STRENGTH.get(mj, 1)
                na, nb = modal in NEGATIVE, mj in NEGATIVE
                if sa != sb or na != nb:
                    flagged.append((rid, rjd, f"modal {modal} vs {mj}"))
                elif vals != vj:
                    flagged.append((rid, rjd, f"values {sorted(vals ^ vj)[:4]}"))
        return flagged

    rtm_row = re.compile(
        r"^\|\s*([A-Z]+-§[^|]+?)\s*\|\s*[^|]*\|\s*([A-Z_]+)\s*\|[^|]*\|[^|]*\|\s*([^|]+?)\s*\|[^|]*\|[^|]*\|\s*$",
        re.M)
    rtm_rows = []
    for f in sorted(glob.glob("docs/rtm/*.rtm.md")):
        rtm_rows += rtm_row.findall(open(f, encoding="utf-8").read())

    # self-test: the detector MUST flag known drift shapes (guards against dead check)
    synth = [
        ("AAA-§1-01", "MUST", "MiFID II audit records retained for 1827 days minimum per profile floor"),
        ("BBB-§1-01", "MUST", "MiFID II audit records retained for 1825 days minimum per profile floor"),
        ("AAA-§2-01", "MUST", "broker forward the byte-identical envelope to the recipient inbox unchanged"),
        ("BBB-§2-01", "SHOULD", "broker forward the byte-identical envelope to the recipient inbox unchanged"),
    ]
    st = drift_pairs(synth)
    check("RTM drift linter self-test (detects value + modal drift)", len(st) == 2,
          f"expected 2 synthetic flags, got {len(st)}: {st}")

    flagged = drift_pairs(rtm_rows)
    check("RTM cross-document drift (near-identical requirements, diverging modal/values)",
          not flagged,
          "; ".join(f"{a}~{b} [{r}]" for a, b, r in flagged[:5]))

    # DR-3/DR-4: effective obligation resolution (Core §4.3.10)
    sys.path.insert(0, "scripts")
    import runtime_harness as rh
    from referencing import Registry, Resource
    reg = Registry().with_resources([(j["$id"], Resource.from_contents(j)) for j in schemas.values()])
    rules = json.load(open("profiles/arsia-obligation-rules.json"))
    vectors = json.load(open("test-vectors/arsia-test-vectors.json"))["vectors"]
    identity_text = open("spec/ARSIA-Identity.md", encoding="utf-8").read()
    routing_text = open("spec/ARSIA-Routing.md", encoding="utf-8").read()
    errs = list(Draft202012Validator(schemas["arsia-obligation-rules.schema.json"]).iter_errors(rules))
    check("obligation rules artifact valid against its schema", not errs, "; ".join(e.message[:60] for e in errs[:3]))
    probs = resolution_vector_mismatches(vectors, rh)
    check("runtime resolution vectors: expected results == reference resolver (Core §4.3.10)", not probs,
          "; ".join(probs[:4]))
    probs = a32_equivalence(rh)
    check("A-32 absent profile == explicit GDPR-STANDARD (semantic; provenance keeps the difference)", not probs,
          "; ".join(probs[:4]))
    probs = obligation_rules_table_parity(core, rules)
    check("Core §4.3.10.3 table == obligation rules artifact (scope, trigger, requirements, exceptions)",
          not probs, "; ".join(probs[:4]))
    probs = diagnostic_parity(core, schemas["arsia-audit-record.schema.json"], rules,
                              schemas["arsia-obligation-rules.schema.json"])
    check("Core §4.3.10.6 diagnostics == audit conflict enum; artifact diagnostics belong to their rule",
          not probs, "; ".join(probs[:4]))
    probs = decision_example_problems(identity_text, schemas["arsia-onboarding-decision.schema.json"], reg, rh)
    check("Identity §7.6 decision example valid; context_sha256 recomputes", not probs, "; ".join(probs[:4]))
    probs = retention_derivation_problems(vectors, rh)
    check("retention fields == those derived from obligation_resolution (State §7.1)", not probs,
          "; ".join(probs[:4]))
    probs = source_digest_problems(vectors, rules, catalog, rh)
    check("recorded source digests recompute (Core §4.3.10.2)", not probs, "; ".join(probs[:4]))
    probs = eu_list_problems(routing_text, rh)
    check("Routing §5.2 EU member list sorted, == resolver, digest recomputes", not probs, "; ".join(probs[:4]))
    skip_doc = open("docs/draft-02-skip-classification.md", encoding="utf-8").read()
    classified = re.findall(r"^\| ([A-Z]+-\d+) \|", skip_doc, re.M)
    skipped = [v["id"] for v in vectors if v.get("skip_schema")]
    total = re.search(r"— total (\d+)\.", skip_doc)
    check("skip classification rows == skip_schema vectors, total stated",
          sorted(classified) == sorted(skipped) and total and int(total.group(1)) == len(skipped),
          f"missing {sorted(set(skipped) - set(classified))[:4]} extra {sorted(set(classified) - set(skipped))[:4]}"
          f" total {total.group(1) if total else None} vs {len(skipped)}")

    # DR-1/DR-2: executor oversight sources and post-execution review
    probs = migrated_oversight_problems(vectors, schemas, reg, rh)
    check("pending/decision vectors recompute from their reference request (DR-1)", not probs, "; ".join(probs[:4]))
    probs = onboarding_policy_problems(vectors, schemas, reg, rh)
    check("onboarding policy_sha256 and lists == reference policy (Identity §8.1, §8.3)", not probs,
          "; ".join(probs[:4]))
    probs = closed_member_problems(actions, core, schemas)
    check("closed member lists: Actions §3.2 args, §3.9.3 review payloads, Core §6.1 claim == schemas", not probs,
          "; ".join(probs[:4]))
    probs = executor_prefix_problems(core, rh)
    check("Core §4.3.10.2 executor-policy source ids == harness", not probs, "; ".join(probs))
    probs = replaced_rule_echoes()
    check("replaced oversight rules absent (oversight_timeout, router annotation, descriptor veto)", not probs,
          "; ".join(probs[:4]))

    print()
    print(f"{'ALL CHECKS PASSED' if not FAIL else f'{len(FAIL)} FAILURES: ' + ', '.join(FAIL)}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
