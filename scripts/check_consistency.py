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
AUDIT_BASE_EXCEPTIONS = {
    "declared_retention": "prose REQUIRED (nullable), schema does not require it — "
                          "retention axis, DR-4 (A-81)",
}


def audit_extension_parity(state_text, audit_schema):
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
        # single-field condition of an allOf/if entry -> (field, frozenset(values))
        p = entry.get("if", {}).get("properties", {})
        if len(p) != 1:
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
    return problems


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
    probs = audit_extension_parity(state, schemas["arsia-audit-record.schema.json"])
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

    print()
    print(f"{'ALL CHECKS PASSED' if not FAIL else f'{len(FAIL)} FAILURES: ' + ', '.join(FAIL)}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
