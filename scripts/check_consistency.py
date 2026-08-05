# SPDX-License-Identifier: BUSL-1.1
# Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda)
"""Draft-02 consistency checks.

Runs the repository-level invariants that individual vector validation cannot
see: schema meta-validation, strict $ref resolution, profiles-catalog validity,
constant anti-regression (B-03/M-02/M-31), and cross-artifact spot checks.
Exit code 0 = all green.
"""
import glob
import json
import re
import sys

FAIL = []


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + (f"  {detail}" if detail and not cond else ""))
    if not cond:
        FAIL.append(name)


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

    # RTM requirement IDs must be unique (a duplicated stale listing once inflated counts)
    from collections import Counter

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
        "DSA-VLOP": "P731D",
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
