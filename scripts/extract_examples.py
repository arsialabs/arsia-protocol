# SPDX-License-Identifier: BUSL-1.1
# Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda)
"""Extract and validate the normative JSON examples embedded in spec prose (A-63).

Every ```json fenced block in spec/*.md is parsed with the strict parser (Core §5.2 steps 2-4) and
classified:

- full example  — parses; it MUST carry, on the line immediately above the fence, an annotation
      <!-- example: <target>[ @<selector>][; template=<ptr>,...][; partial=<ptr>,...] -->
      or
      <!-- example: no-schema — <reason> -->
  <target> is a schema file, optionally with #/$defs/<name>; @<selector> picks the validated object
  (@/data) or every item of an array (@/keys/*). The example is validated against the target, with
  only these exemptions:
  * template=<ptr>: the value at <ptr> (relative to the validated object) is a placeholder string
    (<...> or {...}); errors whose instance is exactly <ptr> and whose keyword is pattern, format,
    minLength, maxLength, enum, const or type are exempt — nothing else;
  * partial=<ptr>: the member at <ptr> is deliberately omitted; only the `required` error for that
    member in that object is exempt, and the member must indeed be absent;
  * oneOf/anyOf are re-evaluated branch by branch on ALL their errors with the exemptions applied
    (anyOf: some branch clean; oneOf: exactly one branch clean); `not` is never exempt. No heuristic
    (such as jsonschema's best_match) decides an exemption; a failing combinator is reported with the
    residual errors of its branches.
  no-schema needs a reason and is counted apart, never as validated.
- fragment      — does not parse but is deliberately partial: it contains <placeholder> tokens, an
  ellipsis marker, or is a bare property fragment ("name": {...}). It may carry
  <!-- example: fragment -->, and no other annotation.
- FAILURE       — anything else: a block that does not parse and is no fragment (an annotation never
  makes malformed JSON valid), a full block without annotation, an orphan annotation, an unknown
  target, a template pointer that is no placeholder, a partial pointer that is present, or a residual
  validation error.

Exit code 0 = no failure.
"""
import glob
import json
import re
import sys

sys.path.insert(0, "scripts")
import validate_vectors as vv  # noqa: E402
from validate_vectors import JsonRejected, strict_json, strict_load  # noqa: E402  (A-61: artifacts load strictly)

PLACEHOLDER = re.compile(r"<[A-Za-z]")
PROPERTY_FRAGMENT = re.compile(r'^\s*"[^"]+"\s*:')
ELLIPSIS = re.compile(r"\.\.\.|…")
ANNOTATION = re.compile(r"^\s*<!-- example: (.*?) -->$")
PLACEHOLDER_VALUE = re.compile(r"<[^<>]+>|\{[^{}]+\}")
EXEMPT_KEYWORDS = {"pattern", "format", "minLength", "maxLength", "enum", "const", "type"}


def strip_strings(body: str) -> str:
    """Remove JSON string literals so markers inside real data don't count."""
    return re.sub(r'"(?:[^"\\]|\\.)*"', '""', body)


def is_fragment(body: str) -> bool:
    stripped = strip_strings(body)
    return bool(
        PLACEHOLDER.search(stripped)
        or ELLIPSIS.search(stripped)
        or PROPERTY_FRAGMENT.match(body)
    )


def load_registry():
    from referencing import Registry, Resource
    schemas = {f.split("/")[-1]: strict_load(f) for f in glob.glob("schemas/*.schema.json")}
    registry = vv.schema_registry(schemas.values())
    return schemas, registry


def validator_for(target, schemas, registry):
    from jsonschema import Draft202012Validator
    name, _, fragment = target.partition("#")
    if name not in schemas:
        raise ValueError(f"unknown schema {name}")
    if fragment:
        node = schemas[name]
        for part in fragment.lstrip("/").split("/"):
            if part not in node:
                raise ValueError(f"unknown target {target}")
            node = node[part]
    # formats (uri, uuid, ...) are asserted, not just annotated, with the library's checks; date-time is the
    # tools' own check (validate_vectors.rfc3339_date_time_valid), the same one the vectors are validated with
    return vv.arsia_validator({"$ref": schemas[name]["$id"] + (f"#{fragment}" if fragment else "")}, registry,
                              format_checker=vv.arsia_format_checker(Draft202012Validator.FORMAT_CHECKER))


def parse_annotation(text):
    """-> dict(kind, target, selector, template, partial, reason) or raises ValueError."""
    if text == "fragment":
        return {"kind": "fragment"}
    m = re.match(r"no-schema — (.+)$", text)
    if m:
        return {"kind": "no-schema", "reason": m.group(1)}
    parts = [p.strip() for p in text.split(";")]
    head = parts[0].split(" @")
    ann = {"kind": "schema", "target": head[0], "selector": head[1] if len(head) > 1 else None,
           "template": [], "partial": []}
    for p in parts[1:]:
        key, _, vals = p.partition("=")
        if key not in ("template", "partial") or not vals:
            raise ValueError(f"bad annotation clause {p!r}")
        ann[key] = [v.strip() for v in vals.split(",")]
    return ann


def pointer_get(obj, ptr):
    for part in ptr.lstrip("/").split("/") if ptr not in ("", "/") else []:
        if isinstance(obj, list):
            obj = obj[int(part)]
        elif isinstance(obj, dict) and part in obj:
            obj = obj[part]
        else:
            raise KeyError(ptr)
    return obj


def select(obj, selector):
    if not selector:
        return [("", obj)]
    if selector.endswith("/*"):
        items = pointer_get(obj, selector[:-2])
        if not isinstance(items, list):  # @…/* selects the items of a JSON array, nothing else
            raise ValueError(f"selector {selector}: {type(items).__name__} is not a JSON array")
        return [(f"{selector[:-2]}/{i}", x) for i, x in enumerate(items)]
    return [(selector, pointer_get(obj, selector))]


def ptr_of(error):
    return "/" + "/".join(str(p) for p in error.absolute_path) if error.absolute_path else "/"


def residual(errors, template, partial):
    """The errors that remain after the declared exemptions, combinators re-evaluated on all branches."""
    out = []
    for e in errors:
        if e.validator in ("oneOf", "anyOf"):
            branches = {}
            for c in e.context or []:
                branches.setdefault(c.relative_schema_path[0], []).append(c)
            clean = [i for i in range(len(e.validator_value)) if not residual(branches.get(i, []), template, partial)]
            if (len(clean) == 1) if e.validator == "oneOf" else bool(clean):
                continue
            out.append(e)
            continue
        if e.validator in EXEMPT_KEYWORDS and ptr_of(e) in template:
            continue
        if e.validator == "required":
            m = re.match(r"'(.+)' is a required property$", e.message)
            base = ptr_of(e)
            if m and (base.rstrip("/") + "/" + m.group(1)) in partial:
                continue
        out.append(e)
    return out


def residual_leaves(error, template, partial):
    """Diagnostic: the non-exempt leaf errors under a failing combinator (all branches)."""
    if error.validator not in ("oneOf", "anyOf") or not error.context:
        return []
    out = []
    for c in residual(list(error.context), template, partial):
        out += residual_leaves(c, template, partial) or [c]
    return out


def check_example(obj, ann, schemas, registry):
    """-> list of failure strings for one annotated full example."""
    fails = []
    try:
        v = validator_for(ann["target"], schemas, registry)
        targets = select(obj, ann["selector"])
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        return [f"annotation: {exc}"]
    for where, inst in targets:
        for p in ann["template"]:
            try:
                val = pointer_get(inst, p)
            except (KeyError, IndexError, ValueError):
                fails.append(f"template {p}: absent")
                continue
            if not (isinstance(val, str) and PLACEHOLDER_VALUE.search(val)):
                fails.append(f"template {p}: {val!r} is not a placeholder")
        for p in ann["partial"]:
            try:
                pointer_get(inst, p)
                fails.append(f"partial {p}: present in the example")
            except (KeyError, IndexError, ValueError):
                pass
        errors = list(v.iter_errors(inst))
        res = residual(errors, set(ann["template"]), set(ann["partial"]))
        for e in res:
            leaves = residual_leaves(e, set(ann["template"]), set(ann["partial"]))
            for leaf in leaves or [e]:
                fails.append(f"{where}{ptr_of(leaf)}: {leaf.message[:110]}")
    return fails


def scan(paths, schemas, registry):
    counts = {"blocks": 0, "full": 0, "fragments": 0, "complete": 0, "template": 0, "partial": 0, "no-schema": 0,
              "messages": 0}
    failures, inventory = [], []
    for path in paths:
        text = open(path, encoding="utf-8").read()
        lines = text.split("\n")
        fences = {}
        for m in re.finditer(r"```json\n(.*?)```", text, re.S):
            fences[text[: m.start()].count("\n")] = m.group(1)
        for i, ln in enumerate(lines):  # orphan annotations
            if ANNOTATION.match(ln) and (i + 1) not in fences:
                failures.append(f"{path}:{i + 1}: annotation not immediately above a ```json block")
        for idx, body in fences.items():
            counts["blocks"] += 1
            line = idx + 2
            am = ANNOTATION.match(lines[idx - 1]) if idx else None
            try:
                ann = parse_annotation(am.group(1)) if am else None
            except ValueError as exc:
                failures.append(f"{path}:{line}: {exc}")
                continue
            try:
                obj = strict_json(body.encode("utf-8"))
            except JsonRejected as exc:
                if is_fragment(body) and (ann is None or ann["kind"] == "fragment"):
                    counts["fragments"] += 1
                    inventory.append((path, line, "fragment", ""))
                else:
                    failures.append(f"{path}:{line}: does not parse ({exc})")
                continue
            counts["full"] += 1
            if ann is None or ann["kind"] == "fragment":
                failures.append(f"{path}:{line}: full example without an example annotation")
                continue
            if ann["kind"] == "no-schema":
                counts["no-schema"] += 1
                inventory.append((path, line, "no-schema", ann["reason"]))
                continue
            kind = "partial" if ann["partial"] else ("template" if ann["template"] else "complete")
            counts[kind] += 1
            if ann["target"] == "arsia-message.schema.json" and not ann["partial"]:
                counts["messages"] += 1  # complete messages validated against the envelope schema
            inventory.append((path, line, kind, ann["target"] + (f" @{ann['selector']}" if ann["selector"] else "")))
            for f in check_example(obj, ann, schemas, registry):
                failures.append(f"{path}:{line}: {f}")
    return counts, failures, inventory


def main() -> int:
    schemas, registry = load_registry()
    counts, failures, inventory = scan(sorted(glob.glob("spec/*.md")), schemas, registry)
    if "--inventory" in sys.argv:
        for path, line, kind, what in inventory:
            print(f"{path}:{line}\t{kind}\t{what}")
    print(f"blocks={counts['blocks']} full={counts['full']} (complete={counts['complete']} "
          f"template={counts['template']} partial={counts['partial']} no-schema={counts['no-schema']}; "
          f"messages={counts['messages']}) fragments={counts['fragments']} failures={len(failures)}")
    for f in failures:
        print("FAIL " + f)
    print("ALL EXAMPLES OK" if not failures else "EXAMPLE FAILURES")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
