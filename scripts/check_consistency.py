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
import os
import re
import sys

sys.path.insert(0, "scripts")
from validate_vectors import strict_json, strict_load  # noqa: E402  (A-61: artifacts load strictly)

FAIL = []
PASSED = []  # names of the consistency checks passed so far (evidence `check:` tokens may cite them, SC4)


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + (f"  {detail}" if detail and not cond else ""))
    if not cond:
        FAIL.append(name)
    else:
        PASSED.append(name)


# Rows of the State §7.1 extension table that the schema deliberately does not
# enforce. Each needs a written reason; any other row must match the schema exactly.
AUDIT_EXTENSION_EXCEPTIONS = {
    "ict_incident": "extension promised by Assets §6.2 but no field is defined yet",
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
    present_rows = set()
    dep = audit_schema.get("dependentRequired", {})
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
        present = re.match(r"`([a-z_]+)` present$", rcond)
        if present:  # presence condition: the schema's dependentRequired for that field (A-58)
            name = present.group(1)
            present_rows.add(name)
            if name not in props:
                problems.append(f"{rtype}: `{name}` is not a schema property")
            if set(dep.get(name, [])) != required:
                problems.append(f"{rtype}: table REQUIRED {sorted(required)} != schema dependentRequired "
                                f"{sorted(dep.get(name, []))}")
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
    want = {f: sorted(group - {f}) for f in group}
    if not group:
        problems.append("no chain fields found in State §7.1 (marker moved?)")
    elif {k: sorted(v) for k, v in dep.items() if k in group} != want:
        problems.append(f"chain all-or-none: prose group {sorted(group)} != schema dependentRequired {dep}")
    # every other dependentRequired entry is stated by a "`x` present" row of the table (A-58)
    unstated = sorted(set(dep) - group - present_rows)
    if unstated:
        problems.append(f"schema dependentRequired {unstated} without a '`x` present' table row")

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
        if meta.get("scenario") in ("resolution", "router", "execution", "timing", "state"):
            if meta["scenario"] == "timing":
                got = rh.timing(v["message"], meta["input"]["recipient_time"], v.get("posture"))
            elif meta["scenario"] == "state":
                got = rh.state_case(meta["input"])
            else:
                got = rh.execution_case(meta["input"]) if meta["scenario"] == "execution" else \
                    rh.scenario_result(meta, v.get("message"))
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


# ------------------------------------------- VC: runtime vectors and coverage claims
def expect_signature_problems(vectors, selftest=True):
    """A-34: every crypto block declares its signature expectation; `absent` exactly when the message
    has no security object; the signature negatives are the declared ones, never inferred."""
    out, negatives = [], []
    for v in vectors:
        c = v.get("crypto")
        if not c:
            continue
        e = c.get("expect_signature")
        has_sec = isinstance(_envelope(v).get("security"), dict)
        if e not in ("valid", "invalid", "absent"):
            out.append(f"{v['id']}: expect_signature {e!r}")
        elif (e == "absent") == has_sec:
            out.append(f"{v['id']}: expect_signature {e!r} but security object {'present' if has_sec else 'absent'}")
        if e == "invalid":
            negatives.append(v["id"])
            # the negative asserted by --check-crypto is the signature the envelope carries
            if (_envelope(v).get("security") or {}).get("sig") != c.get("signature_base64url"):
                out.append(f"{v['id']}: security.sig differs from crypto.signature_base64url")
    if sorted(negatives) != sorted(SIGNATURE_NEGATIVES):
        out.append(f"signature negatives {sorted(negatives)} != {sorted(SIGNATURE_NEGATIVES)}")
    by_id = {v["id"]: v for v in vectors}
    for vid in ALG_MISMATCH_NEGATIVES:
        if vid in by_id:
            out += alg_mismatch_problems(by_id[vid])
        else:
            out.append(f"{vid}: missing")
    for vid, construction in TAMPER_NEGATIVES.items():
        if vid in by_id:
            out += tamper_negative_problems(by_id[vid], construction)
        else:
            out.append(f"{vid}: missing")
    out += kid_key_problems(vectors)
    if selftest:
        out += negative_copy_selftest(vectors)
    return out


def negative_copy_selftest(vectors):
    """A-54 self-test: --check-crypto binds a signature negative to the signature its envelope carries. INV-124
    with only one of its two signature copies replaced by another invalid 64-byte signature must fail, and the
    unaltered vector must pass (a negative path that skips the copy comparison goes dead)."""
    import base64, subprocess, tempfile
    base = next((v for v in vectors if v["id"] == "INV-124"), None)
    if base is None:
        return ["INV-124: missing (negative copy self-test)"]
    other = base64.urlsafe_b64encode(bytes(range(64))).rstrip(b"=").decode()

    def run(probe):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"vectors": [probe]}, f)
        r = subprocess.run([sys.executable, "scripts/validate_vectors.py", "--vectors", f.name, "--check-crypto",
                            "--format", "summary"], capture_output=True, text=True)
        os.unlink(f.name)
        return r.returncode, r.stdout + r.stderr

    out = []
    code, _ = run(json.loads(json.dumps(base)))
    if code != 0:
        out.append("INV-124 unaltered: --check-crypto fails (self-test control)")
    for where in ("crypto.signature_base64url", "security.sig"):
        probe = json.loads(json.dumps(base))
        if where == "security.sig":
            probe["data"]["security"]["sig"] = other
        else:
            probe["crypto"]["signature_base64url"] = other
        code, text = run(probe)
        if code == 0 or "sig field mismatch" not in text:
            out.append(f"INV-124 with only {where} replaced: --check-crypto does not report the copy mismatch")
        if where == "crypto.signature_base64url" and not [
                p for p in expect_signature_problems([probe], selftest=False) if "differs from" in p]:
            out.append("INV-124 with only crypto.signature_base64url replaced: the negatives guard does not report it")
    return out


SIGNATURE_NEGATIVES = ("INV-18", "INV-19", "INV-111", "INV-112", "INV-37", "INV-38", "INV-39", "INV-124", "INV-150")
ALG_MISMATCH_NEGATIVES = ("INV-111", "INV-112")  # A-33: discriminate a key-selected verifier
# A-54: how each Draft-02 malleability negative was built (the bytes the signature was really made over)
TAMPER_NEGATIVES = {"INV-37": "alg flipped EdDSA -> ES256 after signing",
                    "INV-38": "kid swapped #key1 -> #other-key after signing",
                    "INV-39": "Draft-01 signature (whole security removed)",
                    "INV-150": "key-revocation effective_at changed after signing (A-58)"}
INV150_SIGNED_EFFECTIVE_AT = "2026-03-24T13:55:00.000Z"  # the effective_at the #other-key signature covers


def _catalog_keys():
    kp = strict_load("test-vectors/keypairs.json")["keypairs"]
    return {e["kid"]: e for e in kp.values()}


def tamper_negative_problems(v, construction):
    """A-54 (K2): the negative fails for the stated tamper only. Its signature verifies over the bytes it was really
    made over, with the key really used; it does not verify over the Draft-02 signing input of the presented
    envelope; crypto.public_key_hex is the catalog key of the envelope's kid; both signature copies agree."""
    sys.path.insert(0, "scripts")
    import copy
    import rfc8785
    from regen_v2 import signing_input_v2
    import validate_vectors as vv
    out, env, c = [], vv.crypto_envelope(v), v["crypto"]
    keys = _catalog_keys()
    kid = env["security"]["kid"]
    sig = vv._base64url_decode(c["signature_base64url"])
    ok = lambda alg, pub, data: _verifies(vv, alg, pub, sig, data)
    if env["security"].get("sig") != c["signature_base64url"]:
        out.append(f"{v['id']}: security.sig != crypto.signature_base64url")
    if bytes.fromhex(c["canonical_bytes_hex"]) != signing_input_v2(env):
        out.append(f"{v['id']}: canonical bytes are not the Draft-02 signing input of the presented envelope")
    if kid not in keys or keys[kid]["public_key_hex"] != c["public_key_hex"]:
        out.append(f"{v['id']}: crypto.public_key_hex is not the catalog key of kid {kid}")
    signer = keys.get("agent:acme.echo-client#key1", {}).get("public_key_hex")
    pre = copy.deepcopy(env)
    if v["id"] == "INV-150":
        pre["payload"]["data"]["effective_at"] = INV150_SIGNED_EFFECTIVE_AT
        made, really = signing_input_v2(pre), bytes.fromhex(keys.get(kid, {}).get("public_key_hex", "00"))
    elif v["id"] == "INV-37":
        pre["security"]["alg"] = "EdDSA"
        made, really = signing_input_v2(pre), bytes.fromhex(signer)
    elif v["id"] == "INV-38":
        pre["security"]["kid"] = "agent:acme.echo-client#key1"
        made, really = signing_input_v2(pre), bytes.fromhex(signer)
        if ok("EdDSA", bytes.fromhex(c["public_key_hex"]), signing_input_v2(env)):
            out.append(f"{v['id']}: verifies with the swapped kid's key")
    else:
        made, really = rfc8785.dumps({k: x for k, x in env.items() if k != "security"}), bytes.fromhex(signer)
    if not ok("EdDSA", really, made):
        out.append(f"{v['id']}: signature does not verify over the pre-tamper bytes ({construction})")
    if ok("EdDSA", really, signing_input_v2(env)):
        out.append(f"{v['id']}: signature verifies over the presented envelope; nothing was tampered")
    return out


def _verifies(vv, alg, pub, sig, data):
    try:
        vv._verify_signature(alg, pub, sig, data)
        return True
    except Exception:
        return False


def kid_key_problems(vectors):
    """K2: a crypto block whose kid is published uses the catalog key for it; signature negatives and relay
    attestations name a published kid."""
    sys.path.insert(0, "scripts")
    import validate_vectors as vv
    keys, out = _catalog_keys(), []
    for v in vectors:
        c = v.get("crypto")
        env = vv.crypto_envelope(v) if c else None
        kid = ((env or {}).get("security") or {}).get("kid")
        if kid is None:
            continue
        if kid in keys and keys[kid]["public_key_hex"] != c["public_key_hex"]:
            out.append(f"{v['id']}: crypto.public_key_hex differs from the catalog key of {kid}")
        must = v["id"] in SIGNATURE_NEGATIVES or v.get("schema_ref") == "arsia-relay-attestation.schema.json"
        if must and kid not in keys:
            out.append(f"{v['id']}: kid {kid} is not published in keypairs.json")
    return out


def alg_mismatch_problems(v):
    """A-33: the alg is wrong before the signed bytes are computed, the bytes and both signature copies agree,
    the signature verifies under the key's own algorithm, and the declared alg is rejected for incompatibility."""
    sys.path.insert(0, "scripts")
    from regen_v2 import signing_input_v2
    import validate_vectors as vv
    out, m, c = [], v["message"], v["crypto"]
    declared = m["security"]["alg"]
    pub = bytes.fromhex(c["public_key_hex"])
    canon = bytes.fromhex(c["canonical_bytes_hex"])
    sig = vv._base64url_decode(c["signature_base64url"])
    if canon != signing_input_v2(m) or json.loads(canon)["security"]["alg"] != declared:
        out.append(f"{v['id']}: canonical bytes are not the signing input with the declared alg {declared}")
    if m["security"].get("sig") != c["signature_base64url"]:
        out.append(f"{v['id']}: security.sig != crypto.signature_base64url")
    own = {"Ed25519": "EdDSA", "P-256": "ES256", "RSA": "RS256"}[vv._key_type(pub)]
    if own == declared:
        out.append(f"{v['id']}: declared alg {declared} matches the key; nothing to discriminate")
    try:
        vv._verify_signature(own, pub, sig, canon)
    except Exception:
        out.append(f"{v['id']}: signature does not verify under the key's own algorithm {own}")
    try:
        vv._verify_signature(declared, pub, sig, canon)
        out.append(f"{v['id']}: declared alg {declared} verified")
    except ValueError as exc:
        if "incompatible with" not in str(exc):
            out.append(f"{v['id']}: rejected for another reason: {exc}")
    except Exception as exc:
        out.append(f"{v['id']}: rejected for another reason: {type(exc).__name__}")
    return out


def spec_section(text, section):
    """The body of § `section` (e.g. "§8.3"): from its heading to the next heading of the same or a higher level."""
    num = section.lstrip("§")
    m = re.search(rf"^(#+) {re.escape(num)} .*$", text, re.M)
    if not m:
        return None
    nxt = re.search(rf"^#{{1,{len(m.group(1))}}} ", text[m.end():], re.M)
    return text[m.end(): m.end() + nxt.start() if nxt else len(text)]


def posture_problems(vectors, rh):
    """DR-0.3: a posture quotes, verbatim, the option its section grants; a timing vector rejected for its ts
    outside the tolerance (a MAY, Core §8.3) declares that posture."""
    out = []
    norm = lambda s: re.sub(r"\s+", " ", s).strip()
    for v in vectors:
        pos = v.get("posture")
        if pos:
            body = spec_section(open(f"spec/{pos['spec']}", encoding="utf-8").read(), pos["section"])
            if body is None or norm(pos["text"]) not in norm(body):
                out.append(f"{v['id']}: posture text not in {pos['spec']} {pos['section']}")
            if pos["basis"] == "MAY" and "MAY" not in pos["text"]:
                out.append(f"{v['id']}: MAY posture text states no MAY")
        meta = v.get("test_metadata", {})
        if meta.get("scenario") == "timing" and "ts_outside_tolerance" in meta["expect"].get("causes", []) \
                and (pos or {}).get("section") != "§8.3":
            out.append(f"{v['id']}: rejected for its ts without the Core §8.3 posture")
    return out


LINK_EXCEPTIONS = {"INV-14": {"correlation_id"}, "ITV-479": {"correlation_id"}}  # the deliberate negative causes


def link_relation_failures(v, by_id):
    """The relations a pending_approval or approval_decision vector declares through its links (Actions §3.2,
    §3.3): with its reference request, and with the pending it answers. Returns the failing relation names."""
    m = _envelope(v)
    ref = v.get("test_metadata", {}).get("reference_request", {})
    fails = set()
    if m["intent"] == "approval_decision":
        result = (m.get("payload") or {}).get("result") or {}
        if result.get("approver_id") != m.get("from"):
            fails.add("approver_id")
        if "pending_vector" in ref:
            p = _envelope(by_id[ref["pending_vector"]])
            for name, got, want in (("to", m.get("to"), p.get("from")), ("correlation_id", m.get("correlation_id"), p.get("id")),
                                    ("root_request_id", m.get("root_request_id"), p.get("root_request_id")),
                                    ("request_payload_hash", result.get("request_payload_hash"),
                                     p["payload"]["args"].get("request_payload_hash"))):
                if got != want:
                    fails.add(name)
        return fails
    req = by_id[ref["vector"]]["message"] if "vector" in ref else ref
    args = (m.get("payload") or {}).get("args") or {}
    for name, got, want in (("to", m.get("to"), req.get("from")), ("from", m.get("from"), req.get("to")),
                            ("correlation_id", m.get("correlation_id"), req.get("id")),
                            ("root_request_id", m.get("root_request_id"), req.get("id")),
                            ("original_request_id", args.get("original_request_id"), req.get("id"))):
        if got != want:
            fails.add(name)
    return fails


def link_relation_problems(vectors):
    """V4: every declared pending/decision link holds; a deliberate negative fails exactly its stated relation."""
    by_id = {v["id"]: v for v in vectors}
    out = []
    for v in vectors:
        m = _envelope(v)
        if not isinstance(m, dict) or m.get("intent") not in ("pending_approval", "approval_decision") or "event_type" in m:
            continue
        if m["intent"] == "pending_approval" and "reference_request" not in v.get("test_metadata", {}):
            out.append(f"{v['id']}: pending without reference_request")
            continue
        fails = link_relation_failures(v, by_id)
        want = LINK_EXCEPTIONS.get(v["id"], set())
        if fails != want:
            out.append(f"{v['id']}: failing relations {sorted(fails)} != expected {sorted(want)}")
    return out


def valid_vector_resolution_problems(vectors, rh):
    """A valid (non-runtime) message vector carrying compliance is accepted by the reference resolver."""
    out = []
    for v in vectors:
        m = v.get("message")
        if v.get("skip_schema") or v.get("valid") is not True or not isinstance(m, dict) \
                or not isinstance(m.get("compliance"), dict):
            continue
        r = rh.resolve_obligations(m.get("intent"), m["compliance"], None, m["ts"])
        if r["outcome"] != "accepted":
            out.append(f"{v['id']}: {[c['diagnostic'] for c in r.get('conflicts', [])]}")
    return out


def policy_identity_problems(vectors):
    """Identity §8.1: one gateway never applies two policies under one policy_version — (gateway, version) maps to a
    single digest across onboarding decisions and arsia_oversight claims. Distinct gateways may share a version."""
    seen, out = {}, []

    def claims(o):
        if isinstance(o, dict):
            pol = o.get("policy")
            if isinstance(pol, dict) and set(pol) == {"issuer", "version", "sha256"}:
                yield pol
            for x in o.values():
                yield from claims(x)
        elif isinstance(o, list):
            for x in o:
                yield from claims(x)

    for v in vectors:
        for pol in claims(v):
            seen.setdefault((pol["issuer"], pol["version"]), set()).add(pol["sha256"])
        m = v.get("message") if isinstance(v.get("message"), dict) else None
        payload = (m or {}).get("payload") if m else v.get("data")
        args = payload.get("args") if isinstance(payload, dict) else None
        if not isinstance(args, dict) or not args.get("policy_sha256") or "policy_version" not in args:
            continue
        gateway = m["from"] if m else v.get("test_metadata", {}).get("gateway")
        if not gateway:
            out.append(f"{v['id']}: policy digest with no determinable gateway")
            continue
        seen.setdefault((gateway, args["policy_version"]), set()).add(args["policy_sha256"])
    out += [f"{k}: {len(d)} digests" for k, d in seen.items() if len(d) > 1]
    return out


COVERAGE_RULE = {"resolution": "R10", "router": "R10", "execution": "R15", "timing": "R16",
                 "token_binding": "R21", "attestation": "R22", "revocation": "R13"}


def coverage_claim_problems(skip_doc, vectors, passing=None):
    """A-65: the coverage column states only what the repository executes. `executed: Rn` needs a scenario
    that Rn consumes (or a lookup of the vector by ID in the harness); `equivalent`/`partial` quote a check
    the harness runs and passes under that rule; category totals are computed; the introduction's
    "0 failures" holds against the validator."""
    import subprocess
    sys.path.insert(0, "scripts")
    import validate_vectors as vv
    from jsonschema import Draft202012Validator
    harness = open("scripts/runtime_harness.py", encoding="utf-8").read()
    if passing is None:
        run = subprocess.run([sys.executable, "scripts/runtime_harness.py"], capture_output=True, text=True).stdout
        passing = {line[5:].split("  [")[0] for line in run.splitlines() if line.startswith("ok   ")}
    by_id = {v["id"]: v for v in vectors}
    out, cats = [], {}
    for line in skip_doc.splitlines():
        m = re.match(r"^\| ([A-Z]+-\d+) \| (.*) \|$", line)
        if not m:
            continue
        vid, cols = m.group(1), [c.strip() for c in m.group(2).split(" | ")]
        if len(cols) != 6 or vid not in by_id:
            out.append(f"{vid}: malformed row or unknown vector")
            continue
        cats[cols[2]] = cats.get(cols[2], 0) + 1
        cov = cols[5]
        if cov == "executed: --check-crypto":
            # a signature negative: its decisive expectation is the signature failure, nothing else
            if (by_id[vid].get("crypto") or {}).get("expect_signature") != "invalid":
                out.append(f"{vid}: 'executed: --check-crypto' without crypto.expect_signature 'invalid'")
        elif cov.startswith("executed: "):
            rule = cov[len("executed: "):]
            sc = by_id[vid].get("test_metadata", {}).get("scenario")
            if COVERAGE_RULE.get(sc) != rule and f'v["id"] == "{vid}"' not in harness:
                out.append(f"{vid}: '{cov}' but no scenario consumed by {rule}")
        elif cov.startswith(("equivalent: ", "partial: ")):
            q = re.match(r"^(?:equivalent|partial): (R\d+) \"([^\"]+)\"", cov)
            if not q or not q.group(2).startswith(q.group(1) + " ") or q.group(2) not in passing:
                out.append(f"{vid}: '{cov[:60]}' quotes no passing check of that rule")
            if cov.startswith("partial: ") and " — " not in cov:
                out.append(f"{vid}: partial without what is not exercised")
        elif not cov.startswith("none — "):
            out.append(f"{vid}: coverage outside the vocabulary: {cov[:40]}")
    stated = re.search(r"\*\*Category totals:\*\* (.*?) — total", skip_doc)
    computed = ", ".join(f"{k}: {cats[k]}" for k in sorted(cats))
    if not stated or stated.group(1) != computed:
        out.append(f"category totals stated != computed ({computed})")
    if "0 failures" in skip_doc:
        reg = vv.build_registry()
        for v in vectors:
            if v.get("skip_schema"):
                fmt, ref, payload = vv.classify_vector(v)
                schema = vv.resolve_schema(ref, reg)
                errs = vv.message_errors(payload, schema, reg)[1] if ref == vv.MESSAGE_SCHEMA else \
                    list(Draft202012Validator(schema, registry=reg).iter_errors(payload))
                if errs:
                    out.append(f"'0 failures' stated but {v['id']} is structurally invalid")
    return out


def retention_parity_problems(state_text, catalog):
    """A-96: every profile's State §6.x defaults table states the catalog's retention_minimum (the literal,
    `null` for none) and retention_basis (the first quoted value of the row)."""
    profiles = catalog["profiles"]
    entries = profiles.items() if isinstance(profiles, dict) else [(p["name"], p) for p in profiles]
    sections = {}
    for m in re.finditer(r"^### (6\.\d+) ([A-Z0-9-]+)[^\n]*\n(.*?)(?=^### |\Z)", state_text, re.M | re.S):
        sections[m.group(2)] = m.group(3)
    out = []
    for name, entry in entries:
        body, d = sections.get(name), entry["defaults"]
        if body is None:
            out.append(f"{name}: no State §6 section")
            continue
        mm = re.search(r"^\| `retention_minimum`\s*\| `(null|\"[^\"]*\")`", body, re.M)
        mb = re.search(r"^\| `retention_basis`\s*\| `\"([a-z_]+)\"`", body, re.M)
        if not mm:
            out.append(f"{name}: State §6 table has no retention_minimum row")
        else:
            prose = None if mm.group(1) == "null" else mm.group(1).strip('"')
            if prose != d.get("retention_minimum"):
                out.append(f"{name}: retention_minimum prose {prose!r} != catalog {d.get('retention_minimum')!r}")
        if not mb:
            out.append(f"{name}: State §6 table has no retention_basis row")
        elif mb.group(1) != d.get("retention_basis"):
            out.append(f"{name}: retention_basis prose {mb.group(1)!r} != catalog {d.get('retention_basis')!r}")
    return out


def resigner_contract_problems():
    """A-40: scripts/regen_v2.py re-signs only the named valid vectors, writes nothing on any refusal (observed
    by mtime and hash, so an identical rewrite also counts), changes only the signature fields, preserves the
    file format, refuses before signing on a key mismatch, and refuses to write a signature that does not verify."""
    import contextlib
    import hashlib
    import io
    import subprocess
    import tempfile
    sys.path.insert(0, "scripts")
    import regen_v2
    import validate_vectors as vv
    src = "test-vectors/arsia-test-vectors.json"
    original = open(src, encoding="utf-8").read()
    out = []
    tmp = tempfile.mkdtemp(prefix="regen-contract-")

    def copy_with(edit=None, name="c.json"):
        path = os.path.join(tmp, name)
        doc = json.loads(original)
        if edit:
            edit({v["id"]: v for v in doc["vectors"]})
        text = json.dumps(doc, indent=2, ensure_ascii=False) + ("\n" if original.endswith("\n") else "")
        open(path, "w", encoding="utf-8").write(text)
        os.utime(path, ns=(1_000_000_000, 1_000_000_000))  # a known mtime, so any write is visible
        return path

    def state(path):
        return os.stat(path).st_mtime_ns, hashlib.sha256(open(path, "rb").read()).hexdigest()

    def run(path, ids, apply=True):
        cmd = [sys.executable, "scripts/regen_v2.py", "--ids", ids, "--vectors", path] + (["--apply"] if apply else [])
        p = subprocess.run(cmd, capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def vec(path, vid):
        return next(v for v in strict_load(path)["vectors"] if v["id"] == vid)

    def run_cat(path, ids):
        cmd = [sys.executable, "scripts/regen_v2.py", "--catalog", "--ids", ids, "--vectors", path, "--apply"]
        p = subprocess.run(cmd, capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def edit_ctv02(by):
        by["CTV-02"]["message"]["payload"]["args"] = {"edited": "re-sign me"}

    def others_equal(a, b, vid):
        """Other vectors equal as objects, and both files in the one byte format the serializer reproduces:
        together, the other vectors are equal byte for byte."""
        ta, tb = open(a, "rb").read(), open(b, "rb").read()
        for t in (ta, tb):
            if regen_v2.serialize(json.loads(t), t.decode("utf-8")) != t:
                return False
        da, db = json.loads(ta)["vectors"], json.loads(tb)["vectors"]
        return [x for x in da if x["id"] != vid] == [x for x in db if x["id"] != vid]

    def signature_fields_only(before, after):
        strip = lambda v: regen_v2._without_signature(v)
        return strip(before) == strip(after)

    # (a) dry run writes nothing
    p = copy_with(); s = state(p); rc, _ = run(p, "CTV-02", apply=False)
    if rc != 0 or state(p) != s:
        out.append("(a) dry run wrote or failed")
    # (b) EdDSA apply on a correctly signed vector: identical bytes, format and final newline kept
    p = copy_with(); rc, msg = run(p, "CTV-02")
    if rc != 0 or open(p, encoding="utf-8").read() != original:
        out.append(f"(b) CTV-02 apply changed the file: {msg[-80:]}")
    # (c) ES256: only ITV-551's signature fields change, and the new signature verifies
    p = copy_with(); before = vec(p, "ITV-551"); rc, msg = run(p, "ITV-551"); after = vec(p, "ITV-551")
    ok = rc == 0 and signature_fields_only(before, after) and others_equal(p, src, "ITV-551")
    try:
        c = after["crypto"]
        vv._verify_signature("ES256", bytes.fromhex(c["public_key_hex"]), vv._base64url_decode(c["signature_base64url"]),
                             regen_v2.signing_input_v2(after["message"]))
    except Exception:
        ok = False
    if not ok or after["message"]["security"]["sig"] != after["crypto"]["signature_base64url"]:
        out.append(f"(c) ITV-551 re-signing changed more than its signature or does not verify: {msg[-80:]}")
    # (d) unknown ID, (e) a signature negative and an 'absent' block: refused, nothing written
    for case, ids in (("(d)", "NOPE-1"), ("(e)", "INV-18"), ("(e)", "INV-15")):
        p = copy_with(); s = state(p); rc, _ = run(p, ids)
        if rc == 0 or state(p) != s:
            out.append(f"{case} {ids}: not refused, or the file was written")
    # (f) mixed batch on an edited copy: re-signing CTV-02 would change the file, yet nothing is written
    p = copy_with(edit_ctv02, "f.json"); s = state(p); rc, _ = run(p, "CTV-02,INV-18")
    if rc == 0 or state(p) != s:
        out.append("(f) mixed batch: CTV-02 written before INV-18 was refused (partial apply)")
    # (g) a public key that the private key does not derive: refused before signing
    def wrong_key(by):
        by["CTV-02"]["crypto"]["public_key_hex"] = by["ITV-01"]["crypto"]["public_key_hex"]
    p = copy_with(wrong_key, "g.json"); s = state(p); rc, msg = run(p, "CTV-02")
    if rc == 0 or state(p) != s or "refused before signing" not in msg:
        out.append(f"(g) key mismatch not refused before signing: {msg[-90:]}")
    # (h) an edited envelope: the edit stays, the bytes are recomputed, the signature verifies, nothing else changes
    p = copy_with(edit_ctv02, "h.json"); s = state(p); before = vec(p, "CTV-02")
    rc1, _ = run(p, "CTV-02", apply=False)
    dry_ok = rc1 == 0 and state(p) == s
    rc, msg = run(p, "CTV-02"); after = vec(p, "CTV-02")
    ok = dry_ok and rc == 0 and after["message"]["payload"]["args"] == {"edited": "re-sign me"}
    ok = ok and after["crypto"]["canonical_bytes_hex"] == regen_v2.signing_input_v2(after["message"]).hex()
    ok = ok and after["message"]["security"]["sig"] == after["crypto"]["signature_base64url"]
    ok = ok and after["crypto"]["signature_base64url"] != before["crypto"]["signature_base64url"]
    try:
        c = after["crypto"]
        vv._verify_signature("EdDSA", bytes.fromhex(c["public_key_hex"]), vv._base64url_decode(c["signature_base64url"]),
                             bytes.fromhex(c["canonical_bytes_hex"]))
    except Exception:
        ok = False
    ok = ok and signature_fields_only(before, after) and others_equal(p, copy_with(edit_ctv02, "h0.json"), "CTV-02")
    if not ok:
        out.append(f"(h) edited CTV-02 not re-signed correctly: {msg[-80:]}")
    # (j) a file the serializer would normalise (an escaped id of an unselected vector; CRLF): refused, bytes kept
    for case, transform in (("escaped id of CTV-01", lambda s: s.replace('"id": "CTV-01"', '"id": "\\u0043TV-01"', 1)),
                            ("CRLF line endings", lambda s: s.replace("\n", "\r\n"))):
        p = os.path.join(tmp, "j.json")
        text = transform(original)
        assert text != original
        with open(p, "wb") as f:
            f.write(text.encode("utf-8"))
        os.utime(p, ns=(1_000_000_000, 1_000_000_000))
        s = state(p); rc, msg = run(p, "CTV-02")
        if rc == 0 or state(p) != s or "byte for byte" not in msg:
            out.append(f"(j) {case}: not refused, or the file was rewritten: {msg[-80:]}")
    # (i) a produced signature that does not verify (correct key pair): refused, nothing written
    p = copy_with(edit_ctv02, "i.json"); s = state(p)
    real_sign = regen_v2._sign
    regen_v2._sign = lambda alg, k, data: (lambda b: bytes([b[0] ^ 0xFF]) + b[1:])(real_sign(alg, k, data))
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = regen_v2.main(["--ids", "CTV-02", "--apply", "--vectors", p])
    finally:
        regen_v2._sign = real_sign
    if rc == 0 or state(p) != s or "signature does not verify" not in err.getvalue():
        out.append(f"(i) a non-verifying signature was not refused: {err.getvalue()[-90:]}")
    # --catalog (Draft-01.1 port): (k) a crypto vector, (l) a declared signature negative, (m) a vector without
    # security.sig, (n) a kid outside the catalog — each refused with nothing written
    def unknown_kid(by):
        by["ITV-278"]["message"]["security"]["kid"] = "agent:nobody.none#k"
    for case, ids, edit in (("(k)", "CTV-02", None), ("(l)", "INV-11", None), ("(m)", "ITV-358", None),
                            ("(n)", "ITV-278", unknown_kid)):
        p = copy_with(edit, f"cat{case[1]}.json"); s = state(p)
        rc, msg = run_cat(p, ids)
        if rc == 0 or state(p) != s:
            out.append(f"{case} --catalog {ids}: not refused, or the file was written: {msg[-80:]}")
    # (o) an edited envelope re-signed by --catalog: only security.sig changes, and it verifies with the catalog key
    def edit_278(by):
        by["ITV-278"]["message"].setdefault("context", {})["locale"] = "en-GB"
    p = copy_with(edit_278, "cato.json"); before = vec(p, "ITV-278"); rc, msg = run_cat(p, "ITV-278"); after = vec(p, "ITV-278")
    strip = lambda v: (lambda c: (c["message"]["security"].pop("sig"), c)[1])(json.loads(json.dumps(v)))
    cat = {e["kid"]: e for e in strict_load("test-vectors/keypairs.json")["keypairs"].values()}
    sec = after["message"]["security"]
    try:
        vv._verify_signature(sec["alg"], bytes.fromhex(cat[sec["kid"]]["public_key_hex"]), vv._base64url_decode(sec["sig"]),
                             regen_v2.signing_input_v2(after["message"]))
        verifies = True
    except Exception:  # noqa: BLE001
        verifies = False
    if rc != 0 or strip(before) != strip(after) or sec["sig"] == before["message"]["security"]["sig"] or not verifies \
            or not others_equal(p, copy_with(edit_278, "cato0.json"), "ITV-278"):
        out.append(f"(o) --catalog did not re-sign ITV-278 by its signature alone: {msg[-80:]}")
    return out


def unresolved_refs(schemas):
    """A-93: every $ref in every schema resolves in a registry built from the schemas' $id only (no
    file-name fallback) — fragments, relative references and nested $id bases included."""
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012
    from urllib.parse import urljoin
    reg = Registry().with_resources(
        [(j["$id"], Resource.from_contents(j, default_specification=DRAFT202012)) for j in schemas.values()])
    out = []

    def walk(node, base, name):
        if isinstance(node, dict):
            if isinstance(node.get("$id"), str):
                base = urljoin(base, node["$id"])
            ref = node.get("$ref")
            if isinstance(ref, str):
                try:
                    reg.resolver(base_uri=base).lookup(ref)
                except Exception:
                    out.append(f"{name}: {ref}")
            for v in node.values():
                walk(v, base, name)
        elif isinstance(node, list):
            for v in node:
                walk(v, base, name)

    for name, j in sorted(schemas.items()):
        walk(j, j["$id"], name)
    return out


def example_annotation_problems():
    """A-63: the example extractor applies only the declared exemptions. Synthetic spec blocks that MUST fail:
    a template error outside the declared pointer; the composite case (a oneOf with a placeholder at /x/id AND
    a real defect at /count); a partial that would hide an undeclared nested required member; a full block
    without annotation; a template pointer whose value is no placeholder. A control block MUST pass."""
    import tempfile
    sys.path.insert(0, "scripts")
    import extract_examples as ee
    from referencing import Resource
    schemas, registry = ee.load_registry()
    syn = {"$schema": "https://json-schema.org/draft/2020-12/schema",
           "$id": "https://arsiaprotocol.org/schemas/v2.0/syn-composite.schema.json",
           "oneOf": [{"type": "object", "required": ["x", "count"],
                      "properties": {"x": {"type": "object", "properties": {"id": {"type": "string", "pattern": "^[0-9]+$"}}},
                                     "count": {"type": "integer"}}},
                     {"type": "array"}]}
    amb = {"$schema": "https://json-schema.org/draft/2020-12/schema",
           "$id": "https://arsiaprotocol.org/schemas/v2.0/syn-ambiguous.schema.json",
           "oneOf": [{"type": "object"}, {"required": ["a"]}]}  # {"a": 1} is valid under BOTH branches
    schemas = dict(schemas, **{"syn-composite.schema.json": syn, "syn-ambiguous.schema.json": amb})
    registry = registry.with_resources([(syn["$id"], Resource.from_contents(syn)),
                                        (amb["$id"], Resource.from_contents(amb))])
    D = "arsia-message.schema.json#/$defs/error-details-forbidden"
    err = '{"intent": "error", "correlation_id": "7a000000-0000-4000-8000-000000000001", "root_request_id": "7a000000-0000-4000-8000-000000000001", "payload": {"type": "com.acme.test/run", "error": {"description": "d"}}}'
    cases = {  # name -> (annotation line or None, body, must_fail)
        "template error outside the pointer": (f"<!-- example: {D}; template=/required_capabilities -->",
                                               '{"required_capabilities": "<caps>", "provided_capabilities": 5}', True),
        "composite /x/id placeholder + /count defect": ("<!-- example: syn-composite.schema.json; template=/x/id -->",
                                                        '{"x": {"id": "<id>"}, "count": "three"}', True),
        "composite control (placeholder only)": ("<!-- example: syn-composite.schema.json; template=/x/id -->",
                                                 '{"x": {"id": "<id>"}, "count": 3}', False),
        "oneOf valid under two branches (empty error context)": ("<!-- example: syn-ambiguous.schema.json -->",
                                                                 '{"a": 1}', True),
        "partial hiding a nested required member": ("<!-- example: arsia-message.schema.json; partial=/v,/id,/ts,/from,/to,/security -->",
                                                    err, True),
        "full block without annotation": (None, '{"required_capabilities": ["a.b"], "provided_capabilities": []}', True),
        "template pointer that is no placeholder": (f"<!-- example: {D}; template=/required_capabilities -->",
                                                    '{"required_capabilities": ["a.b"], "provided_capabilities": []}', True),
        "control (complete)": (f"<!-- example: {D} -->", '{"required_capabilities": ["a.b"], "provided_capabilities": []}', False),
        "array selector over an object": ("<!-- example: arsia-jwk-entry.schema.json @/keys/* -->", '{"keys": {}}', True),
        "array selector over a string": ("<!-- example: arsia-jwk-entry.schema.json @/keys/* -->", '{"keys": ""}', True),
    }
    # formats are asserted: the Core discovery example, with only `inbox` changed to a non-URI, fails
    core = open("spec/ARSIA-Core.md", encoding="utf-8").read()
    m = re.search(r"<!-- example: arsia-discovery-response\.schema\.json -->\n```json\n(.*?)```", core, re.S)
    if m is None:
        out_pre = ["Core discovery example not found for the format control"]
    else:
        out_pre = []
        disc = json.loads(m.group(1))
        cases["discovery example (control)"] = ("<!-- example: arsia-discovery-response.schema.json -->", json.dumps(disc), False)
        cases["discovery example with inbox 'not a URI'"] = ("<!-- example: arsia-discovery-response.schema.json -->",
                                                             json.dumps(dict(disc, inbox="not a URI")), True)
    out = list(out_pre)
    for name, (ann, body, must_fail) in cases.items():
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write("# synthetic\n\n" + (ann + "\n" if ann else "") + "```json\n" + body + "\n```\n")
        _counts, failures, _inv = ee.scan([f.name], schemas, registry)
        os.unlink(f.name)
        if bool(failures) != must_fail:
            out.append(f"{name}: {'accepted' if must_fail else 'rejected: ' + '; '.join(failures)[:120]}")
    return out


def strict_parsing_problems(vectors):
    """A-61: the Core §5.2 steps 2-4 as the repository executes them.
    (1) a corpus with a duplicate member name stops validate_vectors.py (exit != 0, step 4) before any vector
    is reported; (2) the steps run in order: a document with both an unpaired surrogate and a duplicate is
    rejected at step 3; (3) every raw vector is accepted, or rejected at the step its description states;
    (4) the meta-schema keeps the raw format exclusive both ways; (5) the scripts load artifacts only through
    strict_load (no json.load on a file)."""
    import subprocess, tempfile
    from jsonschema import Draft202012Validator
    from validate_vectors import JsonRejected
    out = []
    with tempfile.NamedTemporaryFile("wb", suffix=".json", delete=False) as f:
        f.write(b'{"vectors": [], "vectors": []}')
    r = subprocess.run([sys.executable, "scripts/validate_vectors.py", "--vectors", f.name, "--format", "summary"],
                       capture_output=True, text=True)
    os.unlink(f.name)
    if r.returncode == 0 or "step 4" not in r.stderr or "TOTAL" in r.stdout:
        out.append("a corpus with a duplicate member name does not stop validate_vectors.py at step 4")
    try:
        strict_json(b'{"x":"\\ud800","a":1,"a":2}')
        out.append("unpaired surrogate + duplicate accepted")
    except JsonRejected as exc:
        if exc.step != 3:
            out.append(f"unpaired surrogate + duplicate rejected at step {exc.step}, not 3 (order 2 -> 3 -> 4)")
    for doc in (b'{}', b'[]', b'[["a", 1]]', b'{"a": []}', b'[{}]'):  # objects and arrays stay distinct
        if strict_json(doc) != json.loads(doc):
            out.append(f"{doc.decode()} not preserved: {strict_json(doc)!r}")
    limit = sys.get_int_max_str_digits()
    try:  # steps 2-4 add no limit on numbers: an integer beyond Python's default digit limit stays an integer
        big = strict_json(b'{"n":' + b"7" * 5000 + b"}")["n"]
        if not isinstance(big, int):
            out.append("a 5000-digit integer is not kept as an integer")
    except JsonRejected as exc:
        out.append(f"a 5000-digit integer rejected ({exc})")
    if sys.get_int_max_str_digits() != limit:
        out.append("strict_json leaves Python's int digit limit changed")
    try:
        strict_json(b'{"a":1,"a":2}')
        out.append("duplicate-only document accepted")
    except JsonRejected as exc:
        if exc.step != 4:
            out.append(f"duplicate-only document rejected at step {exc.step}, not 4")
    raw = [v for v in vectors if "raw_hex" in v]
    if {v["expected_parse"] for v in raw} != {"accept", "reject"}:
        out.append("raw vectors lack accepted controls or rejections")
    for v in raw:
        stated = re.search(r"\(step (\d)", v["description"])
        try:
            strict_json(bytes.fromhex(v["raw_hex"]))
            got = ("accept", None)
        except JsonRejected as exc:
            got = ("reject", exc.step)
        want = (v["expected_parse"], int(stated.group(1)) if stated and v["expected_parse"] == "reject" else None)
        if got != want:
            out.append(f"{v['id']}: {got} != stated {want}")
    meta = strict_load("schemas/arsia-test-vectors.meta.json")
    mv = Draft202012Validator(meta["$defs"]["test-vector"])
    base = {"id": "SYN-1", "description": "synthetic", "expected_error": None}
    if mv.is_valid(dict(base, message={}, valid=True, raw_hex="7b7d", expected_parse="accept")):
        out.append("meta-schema accepts a vector mixing message-only and raw")
    if mv.is_valid(dict(base, raw_hex="7b7d")):
        out.append("meta-schema accepts raw_hex without expected_parse")
    if not mv.is_valid(dict(base, raw_hex="7b7d", expected_parse="accept")):
        out.append("meta-schema rejects a well-formed raw vector")
    for script in ("validate_vectors.py", "check_consistency.py", "runtime_harness.py", "extract_examples.py", "regen_v2.py"):
        text = open(f"scripts/{script}", encoding="utf-8").read()
        if re.search(r"json\.load\(", text):
            out.append(f"scripts/{script} loads a file with json.load, not strict_load")
    return out


def skip_structure_selftest(vectors):
    """A-42 self-test: the validator still validates runtime-only vectors structurally. A synthetic skip vector
    missing a required envelope field must make validate_vectors.py fail (a restored skip bypass goes dead)."""
    import subprocess, tempfile
    probe = json.loads(json.dumps(next(v for v in vectors if v["id"] == "ITV-536")))
    probe["id"] = "ITV-0"
    del probe["message"]["expires_at"]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"vectors": [probe]}, f)
    r = subprocess.run([sys.executable, "scripts/validate_vectors.py", "--vectors", f.name, "--format", "summary"],
                       capture_output=True, text=True)
    os.unlink(f.name)
    return r.returncode != 0 and re.search(r"runtime-only: structure-validated\)\s+0\s+1$", r.stdout, re.M) is not None


# ---------------------------------------------------------------- SC4: executed evidence (A-53, A-64)
_HARNESS_RUN = None


def harness_run():
    """One run of scripts/runtime_harness.py (cached): (names of the passing checks, the set of (rule, vector ID)
    pairs that passing checks declared as consumed — the `# executed <rule> <IDs>` lines)."""
    global _HARNESS_RUN
    if _HARNESS_RUN is None:
        import subprocess
        run = subprocess.run([sys.executable, "scripts/runtime_harness.py"], capture_output=True, text=True).stdout
        names = [line[5:].split("  [")[0] for line in run.splitlines() if line.startswith("ok   ")]
        executed = {(parts[2], vid) for line in run.splitlines() if line.startswith("# executed ")
                    for parts in [line.split()] for vid in parts[3:]}
        _HARNESS_RUN = (names, executed)
    return _HARNESS_RUN


def harness_passing():
    """Names of the harness checks that PASS in one run of scripts/runtime_harness.py."""
    return harness_run()[0]


COUNT_SUFFIX = re.compile(r"^ \(\d+ [a-z]+(?:, \d+ [a-z]+)*\)$")


def check_name_matches(name, passed):
    """A `check:` token names a passing check exactly; the only abbreviation allowed drops a trailing
    parenthesised count suffix such as ' (3 chains, 7 entries)', which varies with the corpus."""
    return name in passed or len([n for n in passed if n.startswith(name) and COUNT_SUFFIX.match(n[len(name):])]) == 1


RTM_HEADER = ["ID", "§", "Modal", "Layer", "Kind", "Requirement", "Schema", "Vector", "Evidence"]
RTM_ROW_LINE = re.compile(r"^\| [A-Z]+-§")
VECTOR_ID = re.compile(r"^(?:ITV|INV|CTV|STV|ATV|ACTV|RTV)-\d+$")
MANDATORY_MODALS = {"MUST", "MUST_NOT", "REQUIRED"}
EVIDENCE_CODES = {
    "out-of-repo": {"transport", "infrastructure", "operator", "external-party", "implementation-internal"},
    "untested": {"no-reference-model", "integration", "structural-only"},
}
EXECUTION_KINDS = ("struct", "raw", "crypto", "exec", "check")


def rtm_requirement_rows(paths=None):
    """Header-driven RTM parser (SC4): the requirement table is the one whose header is RTM_HEADER; every
    requirement line of a file must belong to it. Returns (rows, problems); rows are dicts keyed by the
    lower-cased header, plus 'file'."""
    rows, probs = [], []
    for f in paths or sorted(glob.glob("docs/rtm/ARSIA-*.rtm.md")):
        lines = open(f, encoding="utf-8").read().split("\n")
        header, in_table, n_lines = None, False, 0
        for line in lines:
            if RTM_ROW_LINE.match(line):
                n_lines += 1
            cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("|") else None
            if cells == RTM_HEADER:
                header, in_table = [c.lower() for c in cells], True
                continue
            if in_table and cells is not None:
                if set("".join(cells)) <= set("-: "):
                    continue
                if not RTM_ROW_LINE.match(line):
                    probs.append(f"{f}: non-requirement line inside the requirement table")
                    continue
                if len(cells) != len(header):
                    probs.append(f"{f}: {cells[0]} has {len(cells)} cells, not {len(header)}")
                    continue
                rows.append({**dict(zip(header, cells)), "file": f})
            elif in_table:
                in_table = False
        got = sum(1 for r in rows if r["file"] == f)
        if header is None:
            probs.append(f"{f}: no requirement table with header {' | '.join(RTM_HEADER)}")
        if got != n_lines:
            probs.append(f"{f}: {n_lines} requirement lines, {got} parsed in the table")
        stated = re.search(r"\| Total requirements \| (\d+) \|", "\n".join(lines))
        if not stated or int(stated.group(1)) != got:
            probs.append(f"{f}: Total requirements stated {stated.group(1) if stated else None}, table has {got}")
    return rows, probs


def evidence_tokens(cell):
    """Split an Evidence cell on '; ' outside backquoted check names."""
    return [t.strip() for t in re.findall(r"(?:`[^`]*`|[^;`])+", cell) if t.strip()]


def token_problems(tok, results, crypto, harness, consistency, schema_cell=None, executed=frozenset()):
    """Problems of one evidence token against what was executed. results/crypto: per-vector records of
    validate_vectors (vector_results/crypto_results), keyed by ID; harness/consistency: passing check names;
    executed: (rule, vector ID) pairs that passing harness checks declared as consumed."""
    m = re.match(r"^(schema-ref|struct|raw|crypto):(.+)$", tok)
    if m:
        kind, arg = m.groups()
        if kind == "schema-ref":
            if not os.path.exists(f"schemas/{arg}.schema.json"):
                return [f"{tok}: no schema file"]
            if schema_cell is not None and arg not in [s.strip() for s in schema_cell.split(",")]:
                return [f"{tok}: not in the Schema column"]
            return []
        out = []
        for vid in [x.strip() for x in arg.split(",")]:
            if kind == "crypto":
                if not (crypto.get(vid) or {}).get("passed"):
                    out.append(f"{tok}: {vid} has no passed crypto result")
            else:
                r = results.get(vid)
                if not r or not r.get("approved") or (r.get("format") == "raw") != (kind == "raw"):
                    out.append(f"{tok}: {vid} has no approved {kind} result")
        return out
    m = re.match(r"^exec:(R\d+):(.+)$", tok)
    if m:
        rule, ids = m.group(1), [x.strip() for x in m.group(2).split(",")]
        return [f"{tok}: {vid} not consumed by a passing {rule} check" for vid in ids if (rule, vid) not in executed]
    m = re.match(r"^check:`([^`]+)`$", tok)
    if m:
        if check_name_matches(m.group(1), list(harness) + list(consistency)):
            return []
        return [f"{tok}: no single passing check of that name"]
    m = re.match(r"^(out-of-repo|untested)\(([a-z-]+)\)(?: → (\S+))?$", tok)
    if m:
        kind, code, ref = m.groups()
        if code not in EVIDENCE_CODES[kind]:
            return [f"{tok}: unknown {kind} code"]
        if ref and not os.path.exists(ref):
            return [f"{tok}: reference {ref} does not exist"]
        return []
    return [f"{tok}: unknown evidence token"]


def rtm_evidence_problems(rows, results, crypto, harness, consistency, executed=frozenset()):
    """A-64: Evidence of every mandatory row is present and backed by an execution that PASSED; other rows
    carry '—'; the Vector column holds only vector IDs; every vector a mandatory row cites is represented in an
    execution token."""
    out = []
    for r in rows:
        rid, vec, ev = r["id"], r["vector"], r["evidence"]
        cited = [x.strip() for x in vec.split(",")] if vec != "—" else []
        bad = [x for x in cited if not VECTOR_ID.match(x)]
        if bad:
            out.append(f"{rid}: Vector column holds {bad}")
        if r["modal"] not in MANDATORY_MODALS:
            if ev != "—":
                out.append(f"{rid}: {r['modal']} row with Evidence {ev[:40]!r}")
            continue
        toks = evidence_tokens(ev) if ev not in ("", "—") else []
        if not toks:
            out.append(f"{rid}: mandatory row without Evidence")
            continue
        represented = set()
        for t in toks:
            out += [f"{rid}: {p}" for p in token_problems(t, results, crypto, harness, consistency, r["schema"], executed)]
            m = re.match(r"^(struct|raw|crypto|exec:R\d+):(.+)$", t)
            if m:
                represented |= {x.strip() for x in m.group(2).split(",")}
        missing = [x for x in cited if VECTOR_ID.match(x) and x not in represented]
        if missing:
            out.append(f"{rid}: cited vectors without an execution token: {missing}")
    return out


def rtm_evidence_selftest():
    """The A-64 guard rejects each defect shape and accepts a sound row."""
    results = {"ITV-90001": {"approved": True, "format": "schema-ref"}, "ITV-90002": {"approved": False, "format": "schema-ref"}}
    crypto = {"ITV-90001": {"passed": True}, "ITV-90003": {"passed": False}}
    harness = ["R22 (a) ITV-90001 is accept", "R2 ITV-90002 MIFID P365D rejected", "R6 envelope wins",
               "DR-5 chained vectors recompute and verify (3 chains, 7 entries)"]
    executed = {("R22", "ITV-90001")}
    def row(rid, ev, vec="—", schema="—", modal="MUST"):
        return {"id": rid, "modal": modal, "vector": vec, "schema": schema, "evidence": ev}
    rows = [row("A", "—"),                                            # mandatory without evidence
            row("B", "exec:R22:ITV-90002", "ITV-90002"),                      # vector not executed by the rule
            row("C", "struct:ITV-90002", "ITV-90002"),                        # structural result not approved
            row("D", "crypto:ITV-90003"),                                 # crypto result not passed
            row("E", "foo:bar"),                                      # unknown token
            row("F", "schema-ref:arsia-message"),                     # schema not in the Schema column
            row("G", "untested(something)"),                          # untested without a legend code
            row("H", "struct:ITV-90001", "ITV-90001, DR-5"),                  # non-vector item in the Vector column
            row("I", "schema-ref:arsia-message; struct:ITV-90001; exec:R22:ITV-90001; crypto:ITV-90001; "
                     "check:`R22 (a) ITV-90001 is accept`", "ITV-90001", "arsia-message"),   # sound
            row("J", "struct:ITV-90001", modal="SHOULD"),                 # non-mandatory row with Evidence
            row("K", "exec:R2:ITV-90002"),                               # ID only in a check name, never consumed
            row("L", "check:`R6 envelope`"),                             # truncated check name
            row("M", "check:`DR-5 chained vectors recompute and verify`")]  # count suffix dropped: allowed
    flagged = {p.split(":")[0] for p in rtm_evidence_problems(rows, results, crypto, harness, [], executed)}
    return flagged == {"A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L"}, sorted(flagged)


CONFORMANCE_DOC = "docs/draft-02-conformance-tests.md"
CONFORMANCE_CLASSES = {"integral", "partial", "equivalent", "external", "absent"}
NAMED_TEST = re.compile(r"^#{3,4} (?:Test )?((?:ACTIONS|IDENTITY|ROUTING|STATE|ASSETS|CORE-COMPLIANCE)-\d+)", re.M)


def conformance_problems(doc, spec_ids, results, crypto, harness, consistency, executed=frozenset()):
    """A-53: one row per named test of the specs, a class from the closed vocabulary, every evidence token
    backed by a passing execution; partial names its gap, equivalent its equivalence, external/absent claim
    no execution and give the reason; CHECK-01..05 listed apart with valid evidence."""
    out, seen, checks = [], [], []
    for line in doc.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("| ") else []
        if cells and re.match(r"^(?:ACTIONS|IDENTITY|ROUTING|STATE|ASSETS|CORE-COMPLIANCE)-\d+$", cells[0]):
            if len(cells) != 6:
                out.append(f"{cells[0]}: {len(cells)} cells, not 6")
                continue
            tid, _sec, cls, exercised, ev, gap = cells
            seen.append(tid)
            if cls not in CONFORMANCE_CLASSES:
                out.append(f"{tid}: class {cls!r}")
                continue
            toks = evidence_tokens(ev) if ev != "—" else []
            for t in toks:
                out += [f"{tid}: {p}" for p in token_problems(t, results, crypto, harness, consistency, None, executed)]
            executes = [t for t in toks if t.split(":")[0] in EXECUTION_KINDS]
            if cls in ("integral", "partial", "equivalent") and not executes:
                out.append(f"{tid}: {cls} without an execution token")
            if cls == "partial" and gap in ("", "—"):
                out.append(f"{tid}: partial without the part not executed")
            if cls == "equivalent" and "Equivalence:" not in exercised:
                out.append(f"{tid}: equivalent without the equivalence stated")
            if cls in ("external", "absent") and (toks or gap in ("", "—")):
                out.append(f"{tid}: {cls} must claim no execution and give the reason")
        elif cells and re.match(r"^CHECK-0[1-5]$", cells[0]):
            checks.append(cells[0])
            for t in (evidence_tokens(cells[-2]) if len(cells) >= 2 and cells[-2] != "—" else []):
                out += [f"{cells[0]}: {p}" for p in token_problems(t, results, crypto, harness, consistency, None,
                                                                 executed)]
    dupes = sorted({t for t in seen if seen.count(t) > 1})
    if dupes:
        out.append(f"duplicate rows {dupes}")
    if sorted(set(seen)) != sorted(spec_ids):
        out.append(f"tests missing {sorted(set(spec_ids) - set(seen))[:5]} extra {sorted(set(seen) - set(spec_ids))[:5]}")
    if sorted(checks) != [f"CHECK-0{i}" for i in range(1, 6)]:
        out.append(f"CHECK rows {checks}")
    if "## Summary" in doc:
        counts = {c: 0 for c in CONFORMANCE_CLASSES}
        for line in doc.splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("| ") else []
            if len(cells) == 6 and re.match(r"^(?:ACTIONS|IDENTITY|ROUTING|STATE|ASSETS|CORE-COMPLIANCE)-\d+$", cells[0]) \
                    and cells[2] in counts:
                counts[cells[2]] += 1
        stated = dict(re.findall(r"^\| (\w+) \| (\d+) \|$", doc.split("## Summary", 1)[1], re.M))
        if any(int(stated.get(c, -1)) != n for c, n in counts.items()):
            out.append(f"summary {stated} != computed {counts}")
    return out


def conformance_selftest():
    """The A-53 guard rejects each defect shape."""
    results = {"SYN-1": {"approved": True, "format": "schema-ref"}, "SYN-2": {"approved": False, "format": "schema-ref"}}
    harness = ["R15 SYN-1 result matches its stated expectation", "R2 SYN-3 MIFID P365D rejected"]
    executed = {("R15", "SYN-1")}
    checks = "".join(f"| CHECK-0{i} | — | — | — | — |\n" for i in range(1, 6))
    def doc(*rows):
        return "".join(f"| {' | '.join(r)} |\n" for r in rows) + checks
    good = ("ACTIONS-01", "§", "integral", "all", "exec:R15:SYN-1", "—")
    cases = {
        "integral with a check never run": doc(("ACTIONS-01", "§", "integral", "all", "check:`R99 not run`", "—")),
        "integral with a check only in the source": doc(("ACTIONS-01", "§", "integral", "all", "exec:R15:SYN-2", "—")),
        "vector cited without approved result": doc(("ACTIONS-01", "§", "partial", "x", "struct:SYN-2", "y")),
        "partial without its gap": doc(("ACTIONS-01", "§", "partial", "x", "exec:R15:SYN-1", "—")),
        "spec test missing": doc(good),
        "exec of a vector only named by a check": doc(("ACTIONS-01", "§", "partial", "x", "exec:R2:SYN-3", "y")),
    }
    out = []
    for name, d in cases.items():
        ids = ["ACTIONS-01"] if name != "spec test missing" else ["ACTIONS-01", "ACTIONS-02"]
        if not conformance_problems(d, ids, results, {}, harness, [], executed):
            out.append(f"self-test case not detected: {name}")
    if conformance_problems(doc(good), ["ACTIONS-01"], results, {}, harness, [], executed):
        out.append("self-test control rejected")
    return out


CORPUS_VERSION = "2.0.0"   # the Draft-02 corpus, for wire 2.0 (SC4); inherited 1.0.0 / 1.0.1 do not satisfy it


def corpus_header_problems(doc):
    out = []
    if doc.get("version") != CORPUS_VERSION:
        out.append(f"corpus version {doc.get('version')!r}, the Draft-02 corpus is {CORPUS_VERSION}")
    if doc.get("generated") in (None, "2026-04-10T00:00:00.000Z"):
        out.append(f"generated {doc.get('generated')!r} describes the Draft-01 corpus")
    if doc.get("$schema") != "https://arsiaprotocol.org/schemas/test-vectors/v1.0.json":
        out.append("$schema changed")
    return out


# ---------------------------------------------------------------- Draft-01.1 port (A-97, A-98, A-99)
SIGNED_DATA_SCHEMAS = ("arsia-message.schema.json", "arsia-relay-attestation.schema.json")
SIG_LENGTH = {"EdDSA": 64, "ES256": 64}
B64URL_NOPAD = re.compile(r"^[A-Za-z0-9_-]*$")


def strict_b64url(s):
    """The octets of s if s is base64url without padding in its canonical form (RFC 4648 §5, unpadded as
    Core §5.1 encodes security.sig): only the URL-safe alphabet, no '=', no length ≡ 1 (mod 4), unused trailing
    bits zero. None otherwise; never raises. The validator's lenient decoder skips characters outside the
    alphabet, so a guard that promises "no other defect" decodes with this one."""
    import base64
    if not isinstance(s, str) or not B64URL_NOPAD.match(s) or len(s) % 4 == 1:
        return None
    try:
        raw = base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
    except Exception:  # noqa: BLE001 - not decodable is reported as None
        return None
    return raw if base64.urlsafe_b64encode(raw).decode().rstrip("=") == s else None


def signed_object(v):
    if isinstance(v.get("message"), dict):
        return v["message"]
    if v.get("schema_ref") in SIGNED_DATA_SCHEMAS and isinstance(v.get("data"), dict):
        return v["data"]
    return None


def _key_facts(pub_hex):
    """(key type, RSA bits or None) of a catalog public key; never raises."""
    import validate_vectors as vv
    try:
        kt = vv._key_type(bytes.fromhex(pub_hex))
    except Exception:  # noqa: BLE001 - an unrecognised key is reported as such
        return None, None
    if kt != "RSA":
        return kt, None
    from cryptography.hazmat.primitives.serialization import load_der_public_key
    return kt, load_der_public_key(bytes.fromhex(pub_hex)).key_size


def _math_verifies(alg, pub_hex, sig_bytes, data):
    """Mathematical verification only (no allowlist, no RSA size floor): does sig verify under this key?"""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec, padding
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
    from cryptography.hazmat.primitives.serialization import load_der_public_key
    from cryptography.exceptions import InvalidSignature
    pub = bytes.fromhex(pub_hex)
    try:
        if alg == "EdDSA":
            Ed25519PublicKey.from_public_bytes(pub).verify(sig_bytes, data)
        elif alg == "ES256":
            if len(sig_bytes) != 64:
                return False
            ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), pub).verify(
                encode_dss_signature(int.from_bytes(sig_bytes[:32], "big"), int.from_bytes(sig_bytes[32:], "big")),
                data, ec.ECDSA(hashes.SHA256()))
        elif alg == "RS256":
            load_der_public_key(pub).verify(sig_bytes, data, padding.PKCS1v15(), hashes.SHA256())
        else:
            return False
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False


def signature_problems(vectors, catalog):
    """A-97: outside crypto blocks, a present security.sig verifies with the catalog key of its kid (the
    Draft-02 profile, Core §5.1/§5.2 Step 5 rules), unless the vector declares signature_expectation; a
    declared negative fails exactly for its cause and condition while every other condition holds. Envelopes:
    kid binding to `from` is not part of the default rule (INV-01 has no from); attestations: the signer is the
    broker (kid of broker_id, Routing §7.4.1 step 2). catalog: kid -> entry."""
    import validate_vectors as vv
    from regen_v2 import signing_input_v2
    out = []
    for v in vectors:
        exp = v.get("signature_expectation")
        obj = signed_object(v)
        sec = (obj or {}).get("security") if obj else None
        has_sig = isinstance(sec, dict) and isinstance(sec.get("sig"), str)
        if exp is not None and ("crypto" in v or not has_sig):
            out.append(f"{v['id']}: signature_expectation without a signed object carrying security.sig, or with crypto")
            continue
        if "crypto" in v or not has_sig:
            continue
        alg, kid, sig = sec.get("alg"), sec.get("kid"), sec["sig"]
        sig_bytes = strict_b64url(sig)
        if sig_bytes is None:  # checked before every predicate: an encoding defect is never an extra, silent one
            out.append(f"{v['id']}: security.sig is not canonical base64url without padding")
            continue
        entry = catalog.get(kid)
        kt, bits = _key_facts(entry["public_key_hex"]) if entry else (None, None)
        allowed = alg in vv.ALLOWED_ALGS
        compatible = allowed and kt == {"EdDSA": "Ed25519", "ES256": "P-256", "RS256": "RSA"}[alg]
        data = signing_input_v2(obj)
        math_ok = bool(entry and compatible and _math_verifies(alg, entry["public_key_hex"], sig_bytes, data))
        size_ok = kt != "RSA" or (bits or 0) >= 2048
        owner = obj.get("broker_id") if v.get("schema_ref") == "arsia-relay-attestation.schema.json" else obj.get("from")
        if exp is None:
            if not (entry and compatible and size_ok and math_ok):
                out.append(f"{v['id']}: security.sig does not verify with the catalog key of {kid}")
            continue
        cause, cond = exp.get("cause"), exp.get("condition")
        expected_len = SIG_LENGTH.get(alg) or ((bits or 0) // 8 if kt == "RSA" else None)
        ok = {
            ("kid", "binding"): bool(entry) and compatible and size_ok and math_ok
                                and isinstance(owner, str) and kid.split("#", 1)[0] != owner,
            ("kid", "unresolved"): entry is None and allowed,
            ("alg", "not-allowed"): not allowed,
            ("alg", "incompatible"): allowed and entry is not None and not compatible,
            ("key", "size"): bool(entry) and compatible and kt == "RSA" and (bits or 0) < 2048 and math_ok,
            ("signature", "length"): bool(entry) and compatible and size_ok and len(sig_bytes) != expected_len,
            ("signature", "mismatch"): bool(entry) and compatible and size_ok and len(sig_bytes) == expected_len
                                       and not math_ok,
        }.get((cause, cond))
        if exp.get("result") != "invalid" or ok is None:
            out.append(f"{v['id']}: signature_expectation {exp} outside the contract")
        elif not ok:
            out.append(f"{v['id']}: declared {cause}/{cond} not demonstrated (another condition fails or the declared one does not)")
    return out


def signature_selftest(catalog):
    """Each failure other than the declared one is rejected; one sound case per cause is accepted."""
    import copy as _copy
    import base64 as _b64
    from regen_v2 import signing_input_v2, _sign
    by_kid = catalog
    ed = "agent:acme.echo-client#key1"
    rsa_small = "agent:acme.legacy-system#rsa1024"
    rsa_ok = next(k for k, e in by_kid.items() if _key_facts(e["public_key_hex"]) == ("RSA", 2048) or
                  (_key_facts(e["public_key_hex"])[0] == "RSA" and (_key_facts(e["public_key_hex"])[1] or 0) >= 2048))
    b64 = lambda b: _b64.urlsafe_b64encode(b).decode().rstrip("=")

    def vec(vid, frm, kid, alg, exp=None, sig_kid=None, sig=None):
        m = {"v": "2.0", "id": "00000000-0000-4000-8000-000000000000", "ts": "2026-01-01T00:00:00.000Z",
             "from": frm, "to": "agent:acme.echo-server", "intent": "event",
             "payload": {"type": "com.acme.test/event", "data": {}}, "security": {"alg": alg, "kid": kid, "sig": ""}}
        if sig is None:
            k = sig_kid or kid
            m["security"]["sig"] = b64(_sign(alg if alg in ("EdDSA", "RS256", "ES256") else "EdDSA",
                                             by_kid[k]["private_key_hex"], signing_input_v2(m)))
        else:
            m["security"]["sig"] = sig
        v = {"id": vid, "message": m}
        if exp:
            v["signature_expectation"] = {"result": "invalid", "cause": exp[0], "condition": exp[1]}
        return v

    def with_sig(v, f):
        v = _copy.deepcopy(v); v["message"]["security"]["sig"] = f(v["message"]["security"]["sig"])
        return v

    def corrupt(v):
        v = _copy.deepcopy(v); s_ = v["message"]["security"]["sig"]
        v["message"]["security"]["sig"] = ("B" if s_[0] != "B" else "C") + s_[1:]
        return v
    good = {
        "default": vec("G0", "agent:acme.echo-client", ed, "EdDSA"),
        "kid/binding": vec("G1", "agent:acme.billing", ed, "EdDSA", ("kid", "binding")),
        "kid/unresolved": vec("G2", "agent:acme.echo-client", "agent:nobody.none#k", "EdDSA", ("kid", "unresolved"), sig="A" * 86),
        "alg/not-allowed": vec("G3", "agent:acme.echo-client", ed, "DSA", ("alg", "not-allowed"), sig="A" * 86),
        "alg/incompatible": vec("G4", "agent:acme.echo-client", ed, "ES256", ("alg", "incompatible"), sig="A" * 86),
        "key/size": vec("G5", "agent:acme.legacy-system", rsa_small, "RS256", ("key", "size")),
        "signature/length": vec("G6", "agent:acme.echo-client", ed, "EdDSA", ("signature", "length"), sig="A" * 43),
        "signature/mismatch": corrupt(vec("G7", "agent:acme.echo-client", ed, "EdDSA", ("signature", "mismatch"))),
    }
    out = [f"control {k} rejected: {p}" for k, v in good.items() for p in signature_problems([v], by_kid)]
    bad = {
        "kid/binding with a corrupted signature": corrupt(good["kid/binding"]),
        "kid/binding with an unresolved kid": vec("B2", "agent:acme.billing", "agent:nobody.none#k", "EdDSA", ("kid", "binding"), sig="A" * 86),
        "key/size with a 2048-bit key": vec("B3", rsa_ok.split("#")[0], rsa_ok, "RS256", ("key", "size")),
        "key/size with a kid without key": vec("B4", "agent:nobody.none", "agent:nobody.none#k", "RS256", ("key", "size"), sig="A" * 171),
        "signature/length with 64 bytes": vec("B5", "agent:acme.echo-client", ed, "EdDSA", ("signature", "length"), sig="A" * 86),
        "alg/not-allowed with an allowed alg": vec("B6", "agent:acme.echo-client", ed, "EdDSA", ("alg", "not-allowed")),
        "an undeclared vector with an altered signature": corrupt(good["default"]),
        "result other than invalid": dict(good["kid/binding"], signature_expectation={"result": "valid", "cause": "kid", "condition": "binding"}),
        "a field without security.sig": {"id": "B9", "message": {k: x for k, x in good["default"]["message"].items() if k != "security"},
                                         "signature_expectation": {"result": "invalid", "cause": "signature", "condition": "mismatch"}},
        "a field on a vector with crypto": dict(good["kid/binding"], crypto={"expect_signature": "valid"}),
        "kid/binding with characters outside the alphabet appended": with_sig(good["kid/binding"], lambda x: x + "!!!!"),
        "kid/binding with '=' padding": with_sig(good["kid/binding"], lambda x: x + "=="),
        "signature/length with characters outside the alphabet appended": with_sig(good["signature/length"], lambda x: x + "!!!!"),
        "signature/length with non-zero unused bits": with_sig(good["signature/length"], lambda x: x[:-1] + "B"),
        "an undeclared vector with characters outside the alphabet appended": with_sig(good["default"], lambda x: x + "!!!!"),
    }
    for name, v in bad.items():
        if not signature_problems([v], by_kid):
            out.append(f"not detected: {name}")
    return out


def signature_format_selftest(vectors):
    """The meta-schema admits signature_expectation only where the guard does: no crypto block, and a signed
    object (message, or data of a signed-object schema) whose security.sig is a string. The declared corpus
    negatives are the controls; each case below must be rejected by the meta-schema alone."""
    import copy as _copy
    from jsonschema import Draft202012Validator
    meta = strict_load("schemas/arsia-test-vectors.meta.json")
    mv = Draft202012Validator(meta["$defs"]["test-vector"])
    by_id = {v["id"]: v for v in vectors}
    out = []
    declared = [v for v in vectors if "signature_expectation" in v]
    if not declared:
        out.append("no declared signature negative to serve as control")
    out += [f"meta-schema rejects the declared negative {v['id']}" for v in declared if not mv.is_valid(v)]
    field = {"result": "invalid", "cause": "signature", "condition": "mismatch"}
    bad = {}
    for vid, why in (("CTV-11", "a raw vector"), ("ITV-358", "a message without security.sig"), ("CTV-01", "a vector with crypto")):
        if vid not in by_id:
            out.append(f"self-test fixture {vid} missing")
            continue
        bad[f"{why} ({vid})"] = dict(_copy.deepcopy(by_id[vid]), signature_expectation=field)
    data_case = next(v for v in declared if v.get("schema_ref"))  # ITV-550: data of arsia-message
    bad["data of a schema that is not a signed object"] = dict(_copy.deepcopy(data_case), schema_ref="arsia-common.schema.json")
    nosig = _copy.deepcopy(data_case); nosig["data"]["security"]["sig"] = 0
    bad["security.sig not a string"] = nosig
    bad["a cause outside the vocabulary"] = dict(_copy.deepcopy(declared[0]),
                                                 signature_expectation=dict(field, cause="hash"))
    for name, v in bad.items():
        if mv.is_valid(v):
            out.append(f"meta-schema accepts signature_expectation on {name}")
    return out


def catalog_problems(doc):
    """A-99: the keypair catalog keeps its Draft-02 entries, holds the imported entries exactly, and marks the one
    key deliberately below the RSA minimum."""
    import hashlib
    import rfc8785
    out = []
    prov = doc.get("provenance") or {}
    entries = {e["kid"]: e for e in doc["keypairs"].values()}
    dig = lambda kids: "sha-256:" + hashlib.sha256(rfc8785.dumps({k: entries[k] for k in sorted(kids)})).hexdigest()
    for part in ("draft-02", "imported"):
        kids = (prov.get(part) or {}).get("kids") or []
        if not kids or any(k not in entries for k in kids) or dig(kids) != prov[part].get("sha256"):
            out.append(f"{part} entries differ from their recorded digest")
    gen = (prov.get("generated") or {}).get("kids") or []
    listed = set((prov.get("draft-02") or {}).get("kids", [])) | set((prov.get("imported") or {}).get("kids", [])) | set(gen)
    if listed != set(entries) or len(entries) != len(doc["keypairs"]):
        out.append(f"catalog kids {len(entries)} != provenance sets {len(listed)}")
    small = sorted(k for k, e in entries.items() if _key_facts(e["public_key_hex"])[0] == "RSA"
                   and (_key_facts(e["public_key_hex"])[1] or 0) < 2048)
    if small != sorted((prov.get("generated") or {}).get("below_minimum", [])):
        out.append(f"keys below the RSA minimum {small} != declared")
    return out


LEGAL_BASIS = ("required", ("compliance",), "'legal_basis' is a required property")
SINGLE_CAUSE = (  # (vector, format, schema, its errors exactly: validator, instance path, message)
    ("INV-21", "data", "arsia-state-operations.schema.json#/$defs/set-args",
     [("required", (), "'pii_special_categories' is a required property")]),
    ("ITV-402", "message", "arsia-message.schema.json", [("required", (), "'security' is a required property")]),
    ("ITV-550", "data", "arsia-message.schema.json",
     [("enum", ("security", "alg"), "'DSA' is not one of ['EdDSA', 'ES256', 'RS256']")]),
    # main reconciliation (Draft-01.1 59c70ac): signed, so the announced rule is the only failure
    ("ITV-201", "message", "arsia-message.schema.json", [LEGAL_BASIS, LEGAL_BASIS]),  # the compliance and the
    # envelope conditional both require legal_basis when pii_involved is true: one cause, two schema rules
    ("ITV-266", "message", "arsia-message.schema.json", "enum payload/type"),  # the reserved state type
    ("ITV-423", "message", "arsia-message.schema.json", "oneOf payload"),  # args and result together
    ("ITV-482", "message", "arsia-message.schema.json", [("required", (), "'security' is a required property")]),
)


def port_fixture_problems(vectors, registry):
    """A-98: expires_at > ts in every signed envelope carrying both; positive transfer-request args conform to
    AssetTransferRequest; ITV-426 encodes exactly 32 bytes; INV-21 (set-args, pii_special_categories), ITV-402
    (missing security), ITV-550 (security.alg enum) and, from the main reconciliation (A-100), ITV-201 (legal_basis),
    ITV-266 (reserved state type), ITV-423 (args with result) and ITV-482 (missing security) each fail with exactly
    their announced error."""
    import validate_vectors as vv
    from jsonschema import Draft202012Validator
    out = []
    ts_schema = vv.resolve_schema("arsia-asset-transfer-request.schema.json", registry)
    for v in vectors:
        m = signed_object(v)
        if not isinstance(m, dict):
            continue
        if isinstance(m.get("ts"), str) and isinstance(m.get("expires_at"), str) and not m["expires_at"] > m["ts"]:
            out.append(f"{v['id']}: expires_at not after ts (Core §4.2.2)")
        p = m.get("payload") if isinstance(m.get("payload"), dict) else {}
        positive = (v.get("valid") is True or v.get("expected") == "valid") and not v.get("expected_error")
        if p.get("type") == "arsiaprotocol.assets/transfer-request" and m.get("intent") == "request" and positive:
            errs = list(Draft202012Validator(ts_schema, registry=registry).iter_errors(p.get("args", {})))
            if errs:
                out.append(f"{v['id']}: transfer-request args do not conform ({errs[0].message[:60]})")
    v426 = next((v for v in vectors if v["id"] == "ITV-426"), None)
    raw426 = strict_b64url(v426["message"]["security"]["sig"]) if v426 else None
    n426 = None if raw426 is None else len(raw426)
    if n426 != 32:  # a valid encoding of the length its description announces (Core §5.2 Step 1), not merely "not 64"
        out.append(f"ITV-426 signature is not a canonical base64url encoding of the announced 32 bytes ({n426})")
    v482 = next((v for v in vectors if v["id"] == "ITV-482"), None)
    if not v482 or (v482.get("message") or {}).get("capabilities") != ["arsiaprotocol.onboarding.evaluate"]:
        out.append("ITV-482 capabilities are not the Identity §7.6 decision value [arsiaprotocol.onboarding.evaluate]")
    out += single_cause_problems(vectors, registry)
    return out


# A cause that is the coexistence of two members: comparing the oneOf error and its path cannot tell it from another
# payload defect (without payload.type the same error appears), so both members must be present and removing either
# one alone must leave a structurally valid envelope (copies in memory; signatures are not checked there).
EXCLUSIVE_PAIR = {"ITV-423": ("payload", "args", "result")}


def single_cause_problems(vectors, registry, only=None):
    """Single-cause negatives: the general --check-errors comparator matches a keyword ("required", "enum") and
    would accept a second defect next to the announced one, so each fails with exactly its errors."""
    import copy as _copy
    import validate_vectors as vv
    from jsonschema import Draft202012Validator
    out = []
    by_id = {v["id"]: v for v in vectors}
    for vid, fmt, ref, want in SINGLE_CAUSE:
        if only is not None and vid not in only:
            continue
        v = by_id.get(vid)
        if not v or (fmt == "message" and not isinstance(v.get("message"), dict)) or \
                (fmt == "data" and (v.get("schema_ref") != ref or not isinstance(v.get("data"), dict))):
            out.append(f"{vid} is not a {fmt} vector of {ref}")
            continue
        schema = vv.resolve_schema(ref, registry)
        if fmt == "message":
            errs = vv.message_errors(v["message"], schema, registry)[1]
        elif ref.startswith("arsia-message.schema.json"):
            errs = vv.message_errors(v["data"], schema, registry)[1]
        else:
            errs = list(Draft202012Validator(schema, registry=registry).iter_errors(v["data"]))
        got = [(e.validator, tuple(e.absolute_path), e.message) for e in errs]
        shown = [(g[0], "/".join(map(str, g[1])), g[2][:50]) for g in got]
        if isinstance(want, str):  # one error, compared by validator and path (its message repeats the instance
            # or the whole enum)
            got = [f"{g[0]} {'/'.join(map(str, g[1]))}" for g in got]
            want = [want]
        if got != want:
            out.append(f"{vid} does not fail for its announced cause only: {shown}")
        if vid in EXCLUSIVE_PAIR:
            obj = v["message"] if fmt == "message" else v["data"]
            parent, a, b = EXCLUSIVE_PAIR[vid]
            node = obj.get(parent) if isinstance(obj.get(parent), dict) else {}
            if a not in node or b not in node:
                out.append(f"{vid}: {parent} does not carry both {a} and {b}")
                continue
            for drop in (a, b):
                c = _copy.deepcopy(obj)
                del c[parent][drop]
                rest = vv.message_errors(c, schema, registry)[1]
                if rest:
                    out.append(f"{vid} without {parent}.{drop} is not structurally valid (another defect): "
                               f"{[(e.validator, '/'.join(map(str, e.absolute_path))) for e in rest]}")
    return out


def single_cause_selftest(vectors, catalog, registry):
    """Regression for the ITV-423 isolation: a copy without payload.type (args and result kept), re-signed with the
    catalog key of its kid, verifies, yet must be rejected for that additional defect; the original passes."""
    import base64 as _b64
    import copy as _copy
    from regen_v2 import signing_input_v2, _sign
    out = []
    orig = next((v for v in vectors if v["id"] == "ITV-423"), None)
    if orig is None:
        return ["ITV-423 missing"]
    if single_cause_problems([orig], registry, only={"ITV-423"}):
        out.append("the original ITV-423 is rejected")
    probe = _copy.deepcopy(orig)
    m = probe.get("message")
    if not (isinstance(m, dict) and isinstance(m.get("payload"), dict) and "type" in m["payload"]
            and isinstance(m.get("security"), dict) and m["security"].get("kid") in catalog):
        return out + ["ITV-423 has no signed payload.type to remove for the probe"]
    del m["payload"]["type"]
    sec = m["security"]
    sec["sig"] = _b64.urlsafe_b64encode(_sign(sec["alg"], catalog[sec["kid"]]["private_key_hex"],
                                              signing_input_v2(m))).decode().rstrip("=")
    if signature_problems([probe], catalog):
        out.append("the probe without payload.type does not verify with its catalog key")
    if not single_cause_problems([probe], registry, only={"ITV-423"}):
        out.append("not detected: ITV-423 without payload.type (same oneOf error at payload)")
    return out


# ---------------------------------------------------------------- cycle F (pre-release repository defects)
SPDX_EXEMPT = {"LICENSE.md"}  # the licensing notice itself: it states several licences by path and its copyright line
SPDX_LINES = ("<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->",
              "<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->")


NO_FLOOR_CELL = re.compile(r"^None \(no floor\b[^`]*\)$")  # the explicit "no floor" text, with no duration in it
DURATION_CELL = re.compile(r"^`(P[0-9YMD]+)`(?: \([^`]*\))?$")  # a backticked duration, optionally qualified


def retention_cell_problem(name, floor, cell):
    """One profiles README Retention cell against the catalog floor: a non-null floor needs the backticked equal
    duration; a null floor needs the explicit "None (no floor ...)" text. A failed extraction never counts as a
    match, so a bare or wrong duration in a no-floor row is a mismatch."""
    cell = cell.strip()
    if floor is None:
        return None if NO_FLOOR_CELL.match(cell) and not re.search(r"P\d", cell) else \
            f"profiles/README.md {name}: retention '{cell}' is not the explicit no-floor text (catalog null)"
    m = DURATION_CELL.match(cell)
    return None if m and m.group(1) == floor else f"profiles/README.md {name}: retention '{cell}' != catalog {floor}"


def retention_cell_selftest():
    """Regression: the no-floor row with a duration (bare or backticked) is rejected; the sound cells pass."""
    cases = [("GDPR-STANDARD", None, "P365D", False), ("GDPR-STANDARD", None, "`P365D`", False),
             ("GDPR-STANDARD", None, "", False), ("GDPR-STANDARD", None, "None (no floor; per operator)", True),
             ("EU-AI-ACT-HIGH-RISK", "P6M", "180 days", False), ("EU-AI-ACT-HIGH-RISK", "P6M", "`P90D`", False),
             ("EU-AI-ACT-HIGH-RISK", "P6M", "`P6M` (six calendar months)", True)]
    return [f"retention cell self-test: {n} {c!r} {'rejected' if ok else 'accepted'}" for n, f, c, ok in cases
            if (retention_cell_problem(n, f, c) is None) != ok]


def github_slug(heading):
    """GitHub's heading anchor: lower case, punctuation other than '-' and '_' dropped, spaces to '-'."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def repository_text_problems():
    """Cycle F (F1-F4): every Markdown file at the root, in spec/ and in docs/ opens with the SPDX/Copyright pair
    (LICENSE.md excepted); the profiles README retention column equals each profile's retention_minimum; every
    internal anchor of the six specs resolves to a heading; an RFC section is cited with the bracketed RFC."""
    out = []
    md = sorted(set(glob.glob("*.md") + glob.glob("spec/*.md") + glob.glob("docs/**/*.md", recursive=True)))
    for f in md:
        if os.path.basename(f) in SPDX_EXEMPT and os.path.dirname(f) == "":
            continue
        lines = open(f, encoding="utf-8").read().splitlines()
        if tuple(lines[:2]) != SPDX_LINES:
            out.append(f"{f}: no SPDX/Copyright header")
    cat = strict_load("profiles/arsia-compliance-profiles.json")["profiles"]
    rows = {m.group(1): m.group(2) for m in re.finditer(r"^\| `([A-Z0-9-]+)` \|[^|]*\| ([^|]+) \|", open("profiles/README.md", encoding="utf-8").read(), re.M)}
    if set(rows) != set(cat):
        out.append(f"profiles/README.md lists {sorted(rows)}, the catalog {sorted(cat)}")
    for name, p in cat.items():
        prob = retention_cell_problem(name, p["defaults"].get("retention_minimum"), rows.get(name, ""))
        if prob:
            out.append(prob)
    out += retention_cell_selftest()
    for f in sorted(glob.glob("spec/*.md")):
        text = open(f, encoding="utf-8").read()
        heads, seen = set(), {}
        for h in re.findall(r"^#{1,6} (.+)$", text, re.M):
            slug = github_slug(h)
            heads.add(slug if slug not in seen else f"{slug}-{seen[slug]}")
            seen[slug] = seen.get(slug, 0) + 1
        out += [f"{f}: anchor #{a} resolves to no heading" for a in re.findall(r"\]\(#([^)]+)\)", text) if a not in heads]
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(r"(?<!\[)RFC ?\d{3,5} §", line):
                out.append(f"{f}:{i}: RFC section cited without the bracketed RFC")
    return out


ANNOUNCED_CODE = re.compile(r"MUST be rejected (?:at runtime )?with (?:error code )?[`'\"]?([a-z_]+)")


def runtime_expectation_problems(vectors):
    """Cycle F (F6): a runtime-only vector whose description announces "MUST be rejected with <code>" (or "with
    error code '<code>'") carries an expected_error that starts with that code; `expected`/`valid` stay structural."""
    out = []
    for v in vectors:
        m = ANNOUNCED_CODE.search(v.get("description", ""))
        if v.get("skip_schema") and m and not str(v.get("expected_error") or "").startswith(m.group(1)):
            out.append(f"{v['id']}: description announces {m.group(1)}, expected_error is {v.get('expected_error')!r}")
    return out


RETENTION_FIELDS = ("declared_retention", "effective_retention", "retention_anchor", "retention_source",
                    "retained_until")


def retention_floors():
    """Each catalog profile's retention_minimum (null when the profile has no floor)."""
    profiles = strict_load("profiles/arsia-compliance-profiles.json")["profiles"]
    pairs = profiles.items() if isinstance(profiles, dict) else ((p["name"], p) for p in profiles)
    return {name: (p.get("defaults") or {}).get("retention_minimum") for name, p in pairs}


def audit_records(node, path):
    """Every audit record (an object with retention_source and processed_at) at any depth, with its path."""
    if isinstance(node, dict):
        if "retention_source" in node and "processed_at" in node:
            yield path, node
        for k, x in node.items():
            yield from audit_records(x, f"{path}/{k}")
    elif isinstance(node, list):
        for i, x in enumerate(node):
            yield from audit_records(x, f"{path}/{i}")


def plus_duration(anchor, duration):
    """anchor + duration with the Core §4.3.6.4.1 calendar arithmetic; None when either is unusable."""
    import datetime as _dt
    import runtime_harness as rh
    try:
        u = rh.add_duration(_dt.datetime.strptime(anchor, "%Y-%m-%dT%H:%M:%S.%fZ"), duration)
    except (TypeError, ValueError):
        return None
    return u.strftime("%Y-%m-%dT%H:%M:%S.") + f"{u.microsecond // 1000:03d}Z"


def retention_record_problems(r, floors):
    """State §7.1 retention fields of one audit record, as (fields the rule depends on, problem) pairs. With
    obligation_resolution they are derived from its retention member and MUST NOT diverge: declared_retention is the
    declared value (null when omitted, also in a conflict); a resolved axis gives effective_retention,
    retention_anchor and retained_until (its result requires all three), and the fill source gives retention_source;
    a conflict keeps the evidence under the profile's retention_minimum. Without a resolution a retention
    always applies to an audit record (State §7.3: the profile's minimum, or the P90D Default when no profile is
    active or the profile has no floor), so profile-minimum is the catalog floor, platform-default is P90D,
    per-message is the declared value and "none" is never coherent. The label never switches the arithmetic off:
    whenever effective_retention is present, anchor = processed_at (Core §4.3.6.4.1) and retained_until =
    anchor + effective."""
    out = []
    eff, anchor, until, src = (r.get(f) for f in ("effective_retention", "retention_anchor", "retained_until",
                                                  "retention_source"))
    profile = r.get("compliance_profile_resolved")
    floor = floors.get(profile)
    res_obj = r.get("obligation_resolution")
    ax = ((res_obj.get("axes") or {}).get("retention")) if isinstance(res_obj, dict) else None
    if isinstance(ax, dict):
        declared = ax.get("declared") or {}
        want_decl = declared.get("value") if declared.get("present") else None
        if r.get("declared_retention") != want_decl:
            out.append(({"declared_retention"},
                        f"declared_retention {r.get('declared_retention')!r} is not the axis declaration {want_decl!r}"))
        if ax.get("status") == "resolved":
            res = ax.get("result") or {}
            for f, have, key in (("effective_retention", eff, "duration"), ("retention_anchor", anchor, "anchor"),
                                 ("retained_until", until, "retained_until")):
                if have != res.get(key):
                    out.append(({f}, f"{f} {have} diverges from the resolution result {res.get(key)}"))
            if res.get("anchor") != r.get("processed_at") or \
                    res.get("retained_until") != plus_duration(res.get("anchor"), res.get("duration")):
                out.append((set(), "the resolution result is not (processed_at, anchor + duration)"))
            fill = (ax.get("fill") or {}).get("source")
            want_src = ("per-message" if fill == "message" else "platform-default" if fill == "platform-default"
                        else "none" if not ax.get("result") else "profile-minimum")
            if src != want_src:
                out.append(({"retention_source"},
                            f"retention_source {src} does not follow the fill source {fill} ({want_src})"))
        elif ax.get("status") == "conflict":
            if floor is None:
                out.append((set(), "conflict record without a profile retention_minimum for its evidence"))
            else:
                if eff != floor:
                    out.append(({"effective_retention"},
                                f"conflict evidence effective_retention {eff} is not the floor {floor}"))
                if src != "profile-minimum":
                    out.append(({"retention_source"}, f"conflict evidence retention_source {src} is not "
                                                      "profile-minimum"))
        else:
            out.append((set(), f"retention axis status {ax.get('status')!r}"))
    else:
        applicable = (floor, "profile-minimum") if floor is not None else ("P90D", "platform-default")
        if src == "profile-minimum":
            if floor is None:
                out.append(({"retention_source"}, f"profile-minimum under {profile}, which has no floor"))
            elif eff != floor:
                out.append(({"retention_source", "effective_retention"},
                            f"profile-minimum effective_retention {eff} is not the catalog floor {floor}"))
        elif src == "platform-default":
            if eff != "P90D":
                out.append(({"retention_source", "effective_retention"},
                            f"platform-default effective_retention {eff} is not P90D"))
        elif src == "per-message":
            if eff is None or eff != r.get("declared_retention"):
                out.append(({"retention_source", "effective_retention", "declared_retention"},
                            f"per-message effective_retention {eff} is not the declared "
                            f"{r.get('declared_retention')}"))
        elif src == "none":
            out.append(({"retention_source"}, f"retention_source none, but State §7.3 applies {applicable[0]} "
                                              f"({applicable[1]}) under {profile}"))
        else:
            out.append(({"retention_source"}, f"retention_source {src!r}"))
    if eff is not None:
        if anchor != r.get("processed_at"):
            out.append(({"retention_anchor"}, f"retention_anchor {anchor} is not processed_at {r.get('processed_at')}"))
        if until != plus_duration(anchor, eff):
            out.append(({"retained_until", "retention_anchor", "effective_retention"},
                        f"retained_until {until} is not anchor + {eff}"))
    elif src != "none":
        out.append(({"effective_retention"}, f"effective_retention missing under retention_source {src}"))
    return out


def audit_retention_problems(vectors, floors):
    """Maintenance cycle (A-118, A-119): the retention fields of every audit record of the corpus, nested ones
    included. A vector whose expected_error names a retention field is an intentional negative of that field: the
    rules that depend on that field are left to its own expectation, and every other rule still applies to the
    record. Returns (problems, records checked)."""
    out, n = [], 0
    for v in vectors:
        exempt = {f for f in RETENTION_FIELDS
                  if re.search(rf"(?<!\w){f}(?!\w)", str(v.get("expected_error") or ""))}
        for root in ("data", "message"):
            for path, r in audit_records(v.get(root), root):
                n += 1
                out += [f"{v['id']} {path}: {p}" for deps, p in retention_record_problems(r, floors)
                        if not deps & exempt]
    if n == 0:
        out.append("no audit record in the corpus")
    return out, n


def audit_retention_selftest(floors):
    """Synthetic controls, one per rule; returns (problems, controls executed). A failing control names the problem
    its rule must report, so that another rule reporting the same record does not mask it. The count is printed in
    the check name so that a run in which the self-test did not execute is visible from outside."""
    import copy

    def resolved(duration, anchor, fill, declared=None, floor_minimum=None):
        req = [{"kind": "floor", "minimum": floor_minimum}] if floor_minimum else []
        return {"axes": {"retention": {
            "status": "resolved",
            "declared": {"present": True, "value": declared} if declared else {"present": False},
            "fill": {"value": duration, "source": fill}, "requirements": req,
            "result": {"duration": duration, "anchor": anchor,
                       "retained_until": plus_duration(anchor, duration)}}}}

    T = "2026-04-27T14:00:00.000Z"
    TAMPERED = "2033-04-27T14:00:00.000Z"
    base = {"record_id": "r", "processed_at": T, "compliance_profile_resolved": "EU-AI-ACT-HIGH-RISK",
            "declared_retention": None, "effective_retention": "P6M", "retention_anchor": T,
            "retention_source": "profile-minimum", "retained_until": plus_duration(T, "P6M")}

    def rec(**kw):
        r = copy.deepcopy(base)
        r.update(kw)
        return r

    def without(r, field):
        r = copy.deepcopy(r)
        del r[field]
        return r

    gdpr = rec(compliance_profile_resolved="GDPR-STANDARD", effective_retention="P90D",
               retention_source="platform-default", retained_until=plus_duration(T, "P90D"))
    conflict = {"axes": {"retention": {"status": "conflict", "declared": {"present": True, "value": "P1M"},
                                       "fill": {"value": "P1M", "source": "message"}, "result": None}}}
    ok_conflict = rec(declared_retention="P1M", obligation_resolution=conflict)
    missing_decl = "declared_retention is required — State §7.1"
    cases = [
        # (name, vector, None when the control passes, else a fragment of the problem its rule must report)
        ("no-resolution profile-minimum", {"data": rec()}, None),
        ("resolved, internally consistent but diverging from the resolution",
         {"data": rec(obligation_resolution=resolved("P6M", T, "profile-default", floor_minimum="P6M"),
                      effective_retention="P1Y", retained_until=plus_duration(T, "P1Y"))},
         "effective_retention P1Y diverges from the resolution"),
        ("resolved valid declaration above the floor",
         {"data": rec(declared_retention="P2Y", effective_retention="P2Y", retention_source="per-message",
                      retained_until=plus_duration(T, "P2Y"),
                      obligation_resolution=resolved("P2Y", T, "message", declared="P2Y", floor_minimum="P6M"))},
         None),
        ("resolved composed floor differing from the catalog floor, no declaration",
         {"data": rec(effective_retention="P10Y", retained_until=plus_duration(T, "P10Y"),
                      obligation_resolution=resolved("P10Y", T, "profile-default", floor_minimum="P10Y"))}, None),
        ("resolved declared_retention diverging from the axis declaration",
         {"data": rec(declared_retention="P1D",
                      obligation_resolution=resolved("P6M", T, "profile-default", floor_minimum="P6M"))},
         "is not the axis declaration"),
        ("conflict evidence retention with the rejected declaration recorded", {"data": ok_conflict}, None),
        ("conflict with the rejected value applied",
         {"data": dict(ok_conflict, effective_retention="P1M", retained_until=plus_duration(T, "P1M"))},
         "conflict evidence effective_retention P1M"),
        ("conflict with declared_retention null", {"data": dict(ok_conflict, declared_retention=None)},
         "is not the axis declaration"),
        ("conflict with a wrong retention_source", {"data": dict(ok_conflict, retention_source="per-message")},
         "conflict evidence retention_source"),
        ("conflict with a wrong retained_until",
         {"data": dict(ok_conflict, retained_until=plus_duration(T, "P1Y"))}, "is not anchor + P6M"),
        ("nested record diverging", {"data": {"records": [rec(retained_until=plus_duration(T, "P7Y"))]}},
         "is not anchor + P6M"),
        ("nested record consistent", {"data": {"records": [rec()]}}, None),
        ("profile-minimum under a profile without floor",
         {"data": rec(compliance_profile_resolved="GDPR-STANDARD")}, "which has no floor"),
        ("per-message diverging from the declaration",
         {"data": rec(retention_source="per-message", declared_retention="P2Y")}, "per-message effective_retention"),
        ("anchor other than processed_at",
         {"data": rec(retention_anchor="2026-04-27T13:00:00.000Z",
                      retained_until=plus_duration("2026-04-27T13:00:00.000Z", "P6M"))}, "is not processed_at"),
        ("none without a resolution, no retention fields", {"data": dict(
            gdpr, retention_source="none", effective_retention=None)}, "retention_source none, but State §7.3"),
        ("none relabelling an applicable platform retention with a wrong retained_until",
         {"data": dict(gdpr, retention_source="none", retained_until=TAMPERED)}, f"retained_until {TAMPERED}"),
        ("intentional negative of declared_retention, other rules still apply",
         {"expected_error": missing_decl, "data": without(rec(retained_until=TAMPERED), "declared_retention")},
         f"retained_until {TAMPERED}"),
        ("intentional negative of declared_retention, rules on that field left to its expectation",
         {"expected_error": missing_decl, "data": without(rec(
             retention_source="per-message", effective_retention="P2Y",
             retained_until=plus_duration(T, "P2Y")), "declared_retention")}, None),
    ]
    out = []
    for name, vec, expect in cases:
        probs, _ = audit_retention_problems([dict(vec, id="SELFTEST")], floors)
        if expect is None and probs:
            out.append(f"self-test '{name}': expected pass, got {probs[:1]}")
        elif expect is not None and not any(expect in p for p in probs):
            out.append(f"self-test '{name}': expected a problem with {expect!r}, got {probs[:2]}")
    return out, len(cases)


SNAPSHOT_HASH = re.compile(r"(sha-256:|sha256:)([0-9a-f]{64})")
SNAPSHOT_LEGACY_PREFIX = "result/hash: pattern — State §3.2.1"


def snapshot_results(vectors):
    """(vector, result) for every SNAPSHOT result of the corpus that carries a hash."""
    for v in vectors:
        body = v.get("data") if isinstance(v.get("data"), dict) else None
        if body is None and isinstance(v.get("message"), dict) and isinstance(v["message"].get("payload"), dict):
            body = v["message"]["payload"]
        res = body.get("result") if body and body.get("type") == "arsiaprotocol.state/snapshot" else None
        if isinstance(res, dict) and "hash" in res:
            yield v, res


def snapshot_hash_problems(vectors, registry):
    """State cycle (A-109): every SNAPSHOT result with a hash carries the digest of State §3.2.1 — SHA-256 over
    the RFC 8785 form of {as_of, entries} as carried, in the order carried — whatever else the vector tests (a
    structural negative keeps a correct hash). The prefix is "sha-256:"; the single declared exception is a vector
    whose expected_error is the legacy-prefix expectation: its digest still matches its content, and it fails
    only the pattern of result/hash. Returns (problems, results checked)."""
    import runtime_harness as rh
    import validate_vectors as vv
    from jsonschema import Draft202012Validator
    out, n = [], 0
    for v, res in snapshot_results(vectors):
        n += 1
        m = SNAPSHOT_HASH.fullmatch(res["hash"]) if isinstance(res["hash"], str) else None   # no trailing newline
        want = rh.snapshot_hash(res.get("as_of"), res.get("entries"))
        if not m:
            out.append(f"{v['id']}: hash {res['hash']!r} is not a prefixed lowercase SHA-256")
            continue
        if "sha-256:" + m.group(2) != want:
            out.append(f"{v['id']}: hash digest is not that of {{as_of, entries}} as carried")
        legacy = v.get("expected_error") == SNAPSHOT_LEGACY_PREFIX
        if (m.group(1) == "sha256:") != legacy:
            out.append(f"{v['id']}: prefix {m.group(1)} with expected_error {v.get('expected_error')!r}")
        elif legacy:
            schema = vv.resolve_schema(v.get("schema_ref", ""), registry)
            errs = [(e.validator, "/".join(map(str, e.absolute_path))) for e in
                    Draft202012Validator(schema, registry=registry).iter_errors(v.get("data"))]
            if v.get("expected") != "invalid" or errs != [("pattern", "result/hash")]:
                out.append(f"{v['id']}: legacy-prefix negative fails with {errs}, not only pattern at result/hash")
    if n == 0:
        out.append("no SNAPSHOT result with a hash in the corpus")
    return out, n


def snapshot_hash_selftest(vectors, registry):
    """Synthetic controls of the SNAPSHOT hash guard; returns (problems, controls executed)."""
    import copy
    import runtime_harness as rh
    base = next((v for v, res in snapshot_results(vectors) if len(res.get("entries") or []) >= 2
                 and v.get("expected") == "valid"), None)
    if base is None:
        return ["self-test: no valid SNAPSHOT result with two entries to derive controls from"], 0

    def variant(**kw):
        v = copy.deepcopy(base)
        v["id"] = "SELFTEST"
        r = v["data"]["result"]
        for k, x in kw.items():
            if k == "expected_error":
                v["expected_error"], v["expected"] = x, "invalid"
            else:
                r[k] = x(r) if callable(x) else x
        return v

    legacy = lambda r: r["hash"].replace("sha-256:", "sha256:")
    cases = [
        ("unchanged result", variant(), None),
        ("entry value changed after hashing", variant(entries=lambda r: [dict(r["entries"][0], value="x")] + r["entries"][1:]),
         "hash digest is not that"),
        ("entries reordered after hashing", variant(entries=lambda r: r["entries"][::-1]), "hash digest is not that"),
        ("as_of changed after hashing", variant(as_of="2020-01-01T00:00:00.000Z"), "hash digest is not that"),
        ("timestamp changed: not hashed", variant(timestamp="2030-01-01T00:00:00.000Z"), None),
        ("legacy prefix without the declared expectation", variant(hash=legacy), "prefix sha256:"),
        ("legacy prefix in a negative that declares another expectation",
         variant(hash=legacy, expected_error="generation is required"), "prefix sha256:"),
        ("a line break after a correct hash", variant(hash=lambda r: r["hash"] + "\n"), "is not a prefixed lowercase SHA-256"),
        ("declared legacy-prefix negative with a line break after the digest",
         variant(hash=lambda r: legacy(r) + "\n", expected_error=SNAPSHOT_LEGACY_PREFIX), "is not a prefixed lowercase SHA-256"),
        ("declared legacy-prefix negative with a correct digest", variant(hash=legacy, expected_error=SNAPSHOT_LEGACY_PREFIX), None),
        ("declared legacy-prefix negative with a wrong digest",
         variant(hash="sha256:" + "0" * 64, expected_error=SNAPSHOT_LEGACY_PREFIX), "hash digest is not that"),
        ("declared legacy-prefix negative with a second schema defect",
         variant(hash=legacy, expected_error=SNAPSHOT_LEGACY_PREFIX,
                 entries=lambda r: [{k: x for k, x in r["entries"][0].items() if k != "generation"}] + r["entries"][1:]),
         "not only pattern at result/hash"),
        ("structural negative with a wrong hash (no block exemption of negatives)",
         variant(hash="sha-256:" + "0" * 64, expected_error="generation is required"), "hash digest is not that"),
    ]
    # the legacy-prefix controls with changed entries carry the digest of their own content
    for name, v, _ in cases:
        r = v["data"]["result"]
        if "second schema defect" in name:
            r["hash"] = rh.snapshot_hash(r["as_of"], r["entries"]).replace("sha-256:", "sha256:")
    out = []
    for name, v, expect in cases:
        probs, _ = snapshot_hash_problems([v], registry)
        if expect is None and probs:
            out.append(f"self-test '{name}': expected pass, got {probs[:1]}")
        elif expect is not None and not any(expect in p_ for p_ in probs):
            out.append(f"self-test '{name}': expected a problem with {expect!r}, got {probs[:2]}")
    return out, len(cases)


STATE_CYCLE_SET_FIXTURES = ("ITV-536", "ITV-537", "ITV-538", "ITV-539", "ITV-717", "ITV-718",
                            "INV-207", "INV-208", "INV-209")


def set_fixture_problems(vectors, registry):
    """State cycle (A-120): the SET fixtures of State §8.3 rules 1 and 2 are conformant SET requests — their
    payload.args validate against set-args, the key's scope segment is the declared scope (§3.1.2 rule 2) and the
    key's agent prefix is the sender (rule 1) — so that each one tests only the rule it states."""
    import validate_vectors as vv
    from jsonschema import Draft202012Validator
    schema = vv.resolve_schema("arsia-state-operations.schema.json#/$defs/set-args", registry)
    by_id = {v["id"]: v for v in vectors}
    out = []
    for vid in STATE_CYCLE_SET_FIXTURES:
        v = by_id.get(vid)
        if v is None:
            out.append(f"{vid}: missing")
            continue
        m = v.get("message") or {}
        payload = m.get("payload") or {}
        args = payload.get("args") or {}
        if payload.get("type") != "arsiaprotocol.state/set":
            out.append(f"{vid}: not a SET request")
            continue
        errs = [e.message for e in Draft202012Validator(schema, registry=registry).iter_errors(args)]
        if errs:
            out.append(f"{vid}: args fail set-args: {errs[0]}")
        parts = str(args.get("key", "")).split("/")
        if len(parts) < 3 or parts[1] != args.get("scope"):
            out.append(f"{vid}: key scope segment {parts[1:2]} is not the declared scope {args.get('scope')!r}")
        if parts[0] != m.get("from"):
            out.append(f"{vid}: key agent prefix {parts[0]!r} is not the sender {m.get('from')!r}")
    return out


def state_cycle_echo_problems():
    """State cycle (A-108, A-110) anti-regression: the replaced rules do not come back, and each echo cites the
    rule that now governs it."""
    import glob
    out = []
    texts = {f: open(f, encoding="utf-8").read() for f in sorted(glob.glob("spec/*.md"))}
    flat = {f: re.sub(r"\s+", " ", t) for f, t in texts.items()}
    for f, t in flat.items():
        for old in ("`payload.args` value MUST take precedence", "inherit the envelope's data residency value",
                    "instant `created_at + effective retention` of that entry",
                    "inherited from the `compliance.data_residency` field of the message envelope"):
            if old in t:
                out.append(f"{f}: the replaced text {old!r} is back")
    state = flat.get("spec/ARSIA-State.md", "")
    core = flat.get("spec/ARSIA-Core.md", "")
    actions = flat.get("spec/ARSIA-Actions.md", "")
    for where, text_, needles in (
            ("State §8.3 rule 1", state, ("it MUST be a subset of the composed restriction",
                                          "This rule applies to entries of every scope except session (§1.1). *Selection.*",
                                          "an entry that already has one keeps it",
                                          "This rule defines no additional check of an entry's stored zone")),
            ("State §2.1.9", state, ("lies within the residency restriction composed for the message that set it (§8.3 rule 1)",)),
            ("State §4.2.1", state, ("within the composed restriction of the message that set it (§8.3 rule 1)",)),
            ("State §3.1.2", state, ("the diagnostic `obligation_conflict` (§8.3 rule 1)",
                                     "the preserved retention of its generation (§2.1.8) is not recalculated",
                                     "MUST NOT extend, shorten or re-anchor the preserved retention")),
            ("State §2.1.8", state, ("**Fixed per generation.**", "does not restart the period")),
            ("State §8.3 rule 2", state, ("checked for compatibility with the preserved retention (§3.1.2 rule 7); they never replace it",)),
            ("State §3.2.2", state, ("the instant `created_at +` the retention preserved for that generation (§2.1.8, §4.1.1)",)),
            ("State §3.2.1", state, ('`hash` is the string `"sha-256:"` followed by the SHA-256 digest',
                                     "`hash` and `timestamp` are not part of the hashed object",
                                     "this specification defines no order for `entries`")),
            ("State §8.4", state, ("**Fixed retention details:**",)),
            ("Core §4.3.10.5", core, ("MUST be a subset of the composed result, and a zone that is not is a conflict on this axis",)),
            ("Core §4.3.10.6", core, ("an entry zone outside the composed residency restriction (ARSIA-State.md §8.3)",)),
            ("Actions §1.4", actions, ("integrity verification (construction: ARSIA-State.md §3.2.1)",))):
        for needle in needles:
            if needle not in text_:
                out.append(f"{where}: missing {needle[:60]!r}")
    return out


BREACH_REF = "arsia-breach-notification.schema.json"
BREACH_CAUSE = re.compile(r"^([\w/]+): (\w+) — State §5\.7$")


def breach_notification_problems(vectors, registry):
    """Cycle F (F9): schema-ref vectors of arsia-breach-notification: valid ones cover both notification_target
    values with no error; each invalid one declares '<field>: <keyword> — State §5.7' and fails with exactly that
    one error (validator, and the field's path, or the root for required/additionalProperties)."""
    import validate_vectors as vv
    from jsonschema import Draft202012Validator
    out = []
    schema = vv.resolve_schema(BREACH_REF, registry)
    targets = set()
    vs = [v for v in vectors if v.get("schema_ref") == BREACH_REF]
    for v in vs:
        errs = [(e.validator, "/".join(map(str, e.absolute_path)), e.message) for e in
                Draft202012Validator(schema, registry=registry).iter_errors(v.get("data"))]
        if v.get("expected") == "valid":
            targets.add((v.get("data") or {}).get("notification_target"))
            if errs:
                out.append(f"{v['id']}: positive with errors {errs[:2]}")
            continue
        m = BREACH_CAUSE.match(str(v.get("expected_error") or ""))
        if not m:
            out.append(f"{v['id']}: expected_error does not declare '<field>: <keyword> — State §5.7'")
            continue
        field, kw = m.groups()
        path = "" if kw in ("required", "additionalProperties") else field
        root_field = field.split("/")[0]
        if len(errs) != 1 or errs[0][:2] != (kw, path) or (not path and f"'{root_field}'" not in errs[0][2]):
            out.append(f"{v['id']}: fails with {[(e[0], e[1]) for e in errs]}, not exactly {kw} at {field}")
    if targets != {"supervisory_authority", "data_subject"}:
        out.append(f"positives cover notification_target {sorted(t for t in targets if t)}, not both values")
    # STATE-§5.7-02 (REQUIRED fields) cites the vectors that execute the payload schema, not envelope-only ones
    row = next((l for l in open("docs/rtm/ARSIA-State.rtm.md", encoding="utf-8").read().splitlines()
                if l.startswith("| STATE-§5.7-02 |")), "")
    cited = set()
    for tok in evidence_tokens(row.rstrip(" |").rsplit("|", 1)[-1]) if row else []:
        if tok.startswith("struct:"):
            cited |= {x.strip() for x in tok[len("struct:"):].split(",")}
    missing = sorted({v["id"] for v in vs} - cited)
    if not row or missing or cited - {v["id"] for v in vs}:
        out.append(f"STATE-§5.7-02 Evidence struct: is not exactly the breach-notification vectors (missing {missing[:3]}, "
                   f"others {sorted(cited - {v['id'] for v in vs})[:3]})")
    return out


def main() -> int:
    from jsonschema import Draft202012Validator

    schema_files = sorted(glob.glob("schemas/*.schema.json")) + [
        "schemas/arsia-test-vectors.meta.json"
    ]
    schemas = {}
    for f in schema_files:
        j = strict_load(f)
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
        doc = strict_load("test-vectors/arsia-test-vectors.json")
        sample = next(x for x in doc["vectors"] if x["id"] == "CTV-01")["message"]
        check("strict $ref resolution (CTV-01)", not list(v.iter_errors(sample)))
        dead = unresolved_refs(schemas)
        check("every $ref in every schema resolves by $id (fragments, relative bases; A-93)", not dead,
              ", ".join(dead[:5]))
        planted = json.loads(json.dumps(schemas))
        planted["arsia-state-operations.schema.json"]["$defs"]["set-result"]["$ref"] = \
            "https://arsiaprotocol.org/schemas/state-entry/v1.0.json"
        check("$ref resolution self-test (a planted dead reference is detected)",
              unresolved_refs(planted) == ["arsia-state-operations.schema.json: "
                                           "https://arsiaprotocol.org/schemas/state-entry/v1.0.json"])
    except ImportError:
        print("skip strict-resolution check (referencing not installed)")

    # profiles catalog validates against its own schema (N-02)
    catalog = strict_load("profiles/arsia-compliance-profiles.json")
    errs = list(
        Draft202012Validator(schemas["arsia-compliance-profiles.schema.json"]).iter_errors(catalog)
    )
    check("profiles catalog valid", not errs, "; ".join(e.message[:60] for e in errs[:3]))
    probs = retention_parity_problems(open("spec/ARSIA-State.md", encoding="utf-8").read(), catalog)
    check("State §6 retention_minimum and retention_basis == catalog for every profile (A-96)", not probs,
          "; ".join(probs[:4]))

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
    vec_doc = strict_load("test-vectors/arsia-test-vectors.json")
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

    parsed_rows, parse_probs = rtm_requirement_rows()
    check("RTM requirement tables parsed by header: every requirement line read, totals stated (SC4)",
          not parse_probs and len(parsed_rows) > 0, "; ".join(parse_probs[:4]))
    rtm_rows = [(r["id"], r["modal"], r["requirement"]) for r in parsed_rows]

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

    n_lines = sum(1 for f in sorted(glob.glob("docs/rtm/ARSIA-*.rtm.md"))
                  for line in open(f, encoding="utf-8") if RTM_ROW_LINE.match(line))
    check("RTM drift linter reads every requirement row (a table-format change cannot silence it)",
          len(rtm_rows) == n_lines and n_lines > 0, f"linter rows {len(rtm_rows)}, requirement lines {n_lines}")
    flagged = drift_pairs(rtm_rows)
    check("RTM cross-document drift (near-identical requirements, diverging modal/values)",
          not flagged,
          "; ".join(f"{a}~{b} [{r}]" for a, b, r in flagged[:5]))

    # DR-3/DR-4: effective obligation resolution (Core §4.3.10)
    sys.path.insert(0, "scripts")
    import runtime_harness as rh
    from referencing import Registry, Resource
    reg = Registry().with_resources([(j["$id"], Resource.from_contents(j)) for j in schemas.values()])
    rules = strict_load("profiles/arsia-obligation-rules.json")
    vectors = strict_load("test-vectors/arsia-test-vectors.json")["vectors"]
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

    check("validator self-test: a structurally invalid runtime-only vector fails (A-42)", skip_structure_selftest(vectors))
    probs = example_annotation_problems()
    check("example extractor self-test: only declared template/partial exemptions, combinators on all branches, "
          "annotation required (A-63)", not probs, "; ".join(probs[:4]))
    probs = strict_parsing_problems(vectors)
    check("strict JSON (Core §5.2 steps 2-4): corpus duplicate stops the tools, step order, raw vectors at their "
          "stated step, raw format exclusive, artifacts loaded strictly (A-61)", not probs, "; ".join(probs[:4]))
    probs = coverage_claim_problems(skip_doc, vectors)
    check("skip classification coverage column == harness evidence; totals computed (A-65)", not probs,
          "; ".join(probs[:4]))
    synth_doc = ("| SYN-1 | — | synthetic | crypto-behaviour | behavioural-runtime | — | executed: --check-crypto |\n"
                 "| SYN-2 | — | synthetic | crypto-behaviour | behavioural-runtime | — | executed: --check-crypto |\n"
                 "**Category totals:** crypto-behaviour: 2 — total 2.\n")
    synth = [{"id": "SYN-1", "skip_schema": True},
             {"id": "SYN-2", "skip_schema": True, "crypto": {"expect_signature": "valid"}}]
    st = coverage_claim_problems(synth_doc, synth, passing=set())
    check("skip coverage guard self-test: 'executed: --check-crypto' on an ineligible vector is reported (A-65, A-33)",
          sorted(p.split(":")[0] for p in st) == ["SYN-1", "SYN-2"], "; ".join(st))
    probs = resigner_contract_problems()
    check("regen_v2 re-signer contract: selection, eligibility, no partial write, signature fields only (A-40)",
          not probs, "; ".join(probs[:4]))

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

    # VC: runtime vectors and coverage claims
    probs = expect_signature_problems(vectors)
    check("crypto.expect_signature declared and coherent; signature negatives carry the asserted signature and discriminate their construction (self-test); kid -> catalog key (A-34, A-33, A-54)", not probs,
          "; ".join(probs[:4]))
    probs = posture_problems(vectors, rh)
    check("vector postures quote their section verbatim; MAY-based ts rejections declare it (DR-0.3)", not probs,
          "; ".join(probs[:4]))
    probs = link_relation_problems(vectors)
    check("pending/decision links: recipient, correlation, root, approver, hash; negatives fail only their cause",
          not probs, "; ".join(probs[:4]))
    probs = valid_vector_resolution_problems(vectors, rh)
    check("valid message vectors with compliance are accepted by the reference resolver", not probs,
          "; ".join(probs[:4]))
    probs = policy_identity_problems(vectors)
    check("(gateway, policy_version) -> one policy digest (Identity §8.1)", not probs, "; ".join(probs[:4]))

    # Draft-01.1 port (A-97, A-98, A-99)
    import validate_vectors as vv
    kp_doc = strict_load("test-vectors/keypairs.json")
    catalog = {e["kid"]: e for e in kp_doc["keypairs"].values()}
    corpus_vectors = strict_load("test-vectors/arsia-test-vectors.json")["vectors"]
    probs = signature_problems(corpus_vectors, catalog)
    check("signatures outside crypto blocks verify with the catalog key, or fail exactly for their declared cause (A-97)",
          not probs, "; ".join(probs[:4]))
    probs = signature_selftest(catalog) + signature_format_selftest(corpus_vectors)
    check("signature-expectation guard self-test: every other failure rejected (encoding first), one sound case per "
          "cause accepted; the meta-schema admits the field only on a signed object with security.sig (A-97)",
          not probs, "; ".join(probs[:4]))
    probs = catalog_problems(kp_doc)
    check("keypair catalog: Draft-02 and imported entries equal their recorded digests; the below-minimum key declared (A-99)",
          not probs, "; ".join(probs[:4]))
    registry = vv.build_registry()
    probs = port_fixture_problems(corpus_vectors, registry) + single_cause_selftest(corpus_vectors, catalog, registry)
    check("fixtures: expires_at after ts; positive transfer-request args conform; ITV-426 encodes 32 bytes; INV-21, "
          "ITV-402, ITV-550, ITV-201, ITV-266, ITV-423 and ITV-482 fail with exactly their announced error; ITV-423 "
          "isolated by its args/result controls and a re-signed probe without payload.type (A-98, A-100)",
          not probs, "; ".join(probs[:4]))

    # Cycle F (A-101..): pre-release repository defects
    probs = repository_text_problems()
    check("repository text: SPDX headers, profiles README retention column, spec anchors, bracketed RFC citations (cycle F)",
          not probs, "; ".join(probs[:4]))
    probs = runtime_expectation_problems(corpus_vectors)
    check("runtime-only vectors carry the error code their description announces (cycle F)", not probs, "; ".join(probs[:4]))
    floors = retention_floors()
    probs, n_records = audit_retention_problems(corpus_vectors, floors)
    self_probs, n_controls = audit_retention_selftest(floors)
    probs += self_probs
    check("audit-record retention fields: anchor processed_at, retained_until anchor + effective, source and "
          "declaration consistent with obligation_resolution, nested records included (maintenance cycle) "
          f"({n_records} records, {n_controls} controls)", not probs, "; ".join(probs[:4]))
    probs = breach_notification_problems(corpus_vectors, registry)
    check("breach-notification vectors: positives for both targets, each negative fails exactly its declared constraint (cycle F)",
          not probs, "; ".join(probs[:4]))
    probs, n_results = snapshot_hash_problems(corpus_vectors, registry)
    self_probs, n_controls = snapshot_hash_selftest(corpus_vectors, registry)
    probs += self_probs
    check("SNAPSHOT results: hash is the State §3.2.1 digest of as_of and entries as carried; the legacy prefix only "
          f"in its declared negative, which fails only the pattern (State cycle) ({n_results} results, {n_controls} controls)",
          not probs, "; ".join(probs[:4]))
    probs = set_fixture_problems(corpus_vectors, registry)
    check("State §8.3 SET fixtures are conformant SET requests: args valid against set-args, key scope segment and "
          "agent prefix (State cycle, A-120)", not probs, "; ".join(probs[:4]))
    probs = state_cycle_echo_problems()
    check("State cycle anti-regression: entry residency within the composed restriction, retention fixed per "
          "generation and the SNAPSHOT hash construction are stated, and the replaced rules are absent",
          not probs, "; ".join(probs[:4]))

    # SC4 (A-53, A-64): evidence is checked against what was executed and passed
    import validate_vectors as vv
    corpus = strict_load("test-vectors/arsia-test-vectors.json")
    probs = corpus_header_problems(corpus)
    check("test-vector corpus header: Draft-02 corpus 2.0.0 (wire 2.0), generated set, $schema kept (SC4)",
          not probs, "; ".join(probs))
    results = {r["id"]: r for r in vv.vector_results(corpus, True)}
    crypto = {r["id"]: r for r in vv.crypto_results(corpus)}
    harness, executed = harness_run()
    ok, flagged = rtm_evidence_selftest()
    check("RTM evidence guard self-test: each defect shape reported, sound row accepted (A-64)", ok, str(flagged))
    probs = rtm_evidence_problems(parsed_rows, results, crypto, harness, list(PASSED), executed)
    check("RTM Evidence: every mandatory row mapped to passed executions or a coded disposition (A-64)",
          not probs, "; ".join(probs[:4]))
    probs = conformance_selftest()
    check("conformance classification guard self-test (A-53)", not probs, "; ".join(probs))
    spec_ids = [m for f in sorted(glob.glob("spec/*.md")) for m in NAMED_TEST.findall(open(f, encoding="utf-8").read())]
    probs = conformance_problems(open(CONFORMANCE_DOC, encoding="utf-8").read() if os.path.exists(CONFORMANCE_DOC)
                                 else "", spec_ids, results, crypto, harness, list(PASSED), executed)
    check(f"named conformance tests ({len(spec_ids)}) classified with executed evidence; CHECK-01..05 apart (A-53)",
          not probs, "; ".join(probs[:4]))

    print()
    print(f"{'ALL CHECKS PASSED' if not FAIL else f'{len(FAIL)} FAILURES: ' + ', '.join(FAIL)}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
