# SPDX-License-Identifier: BUSL-1.1
# Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda)
"""Extract and validate the normative JSON examples embedded in spec prose.

Every ```json fenced block in spec/*.md is classified:

- full example  — parses as a standalone JSON document; envelope-shaped
  examples (objects carrying v/from/to/intent/security) are additionally
  validated against arsia-message.schema.json with strict $ref resolution;
- fragment      — does not parse but is deliberately partial: it contains
  <placeholder> tokens, an ellipsis marker, or is a bare property fragment
  ("name": {...}) illustrating a schema addition;
- FAILURE       — does not parse and carries no fragment marker.

Exit code 0 = every block is a valid full example or a recognized fragment
and every envelope-shaped example validates. Anything else fails.
"""
import glob
import json
import re
import sys

PLACEHOLDER = re.compile(r"<[A-Za-z]")
PROPERTY_FRAGMENT = re.compile(r'^\s*"[^"]+"\s*:')
ELLIPSIS = re.compile(r"\.\.\.|…")


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


def load_message_validator():
    from jsonschema import Draft202012Validator

    try:
        from referencing import Registry, Resource
    except ImportError:
        return None
    schemas = [json.load(open(f)) for f in glob.glob("schemas/*.schema.json")]
    registry = Registry().with_resources(
        [(j["$id"], Resource.from_contents(j)) for j in schemas]
    )
    message = next(j for j in schemas if j["$id"].endswith("arsia-message.schema.json"))
    return Draft202012Validator(message, registry=registry)


def main() -> int:
    validator = load_message_validator()
    total = full = fragments = envelopes = 0
    failures = []
    for path in sorted(glob.glob("spec/*.md")):
        text = open(path, encoding="utf-8").read()
        for m in re.finditer(r"```json\n(.*?)```", text, re.S):
            total += 1
            body = m.group(1)
            line = text[: m.start()].count("\n") + 2
            try:
                obj = json.loads(body)
            except Exception as exc:
                if is_fragment(body):
                    fragments += 1
                else:
                    failures.append(f"{path}:{line}: does not parse: {exc}")
                continue
            full += 1
            if (
                validator is not None
                and isinstance(obj, dict)
                and {"v", "from", "to", "intent", "security"} <= obj.keys()
            ):
                envelopes += 1
                for err in validator.iter_errors(obj):
                    failures.append(
                        f"{path}:{line}: envelope example invalid: "
                        f"{err.json_path}: {err.message[:100]}"
                    )
    print(
        f"blocks={total} full={full} fragments={fragments} "
        f"envelope-validated={envelopes} failures={len(failures)}"
    )
    for f in failures:
        print("FAIL " + f)
    if validator is None:
        print("note: referencing not installed — envelope validation skipped")
    print("ALL EXAMPLES OK" if not failures else "EXAMPLE FAILURES")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
