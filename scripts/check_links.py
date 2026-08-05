# SPDX-License-Identifier: BUSL-1.1
# Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda)
"""Cross-reference link checker for the spec suite (M-14 anchor sweep).

Verifies that every `§N.N` section reference in spec/*.md resolves to an
existing heading:

- explicit references (`ARSIA-Core.md §6.4`, `Core §6.4`) must exist in the
  named document;
- bare references (`§6.4`) must exist in the current document, or — to allow
  reference-list continuations like "ARSIA-Core.md §4, §10, §11" — in the
  most recently named ARSIA document;
- references to external standards (`[RFC 8785] §3.2.2`) are skipped when the
  RFC citation appears on the same line.

Also verifies explicit `ARSIA-X(.md) §N.N` references found in schema and
profile-catalog description strings. Exit code 0 = no dangling reference.
"""
import glob
import json
import re
import sys

NAMES = "Core|Actions|Routing|State|Identity|Assets"
HEADING = re.compile(r"^#{2,6}\s+(\d+(?:\.\d+)*)[.\s]")
TOKEN = re.compile(
    rf"\[RFC\s*\d+\]"
    rf"|(?:ARSIA-)?({NAMES})(?:\.md)?(?=\s+§)"
    rf"|ARSIA-({NAMES})(?:\.md)?"
    rf"|§(\d+(?:\.\d+)*)"
)
EXPLICIT = re.compile(rf"ARSIA-({NAMES})(?:\.md)?\s+§(\d+(?:\.\d+)*)")


def load_sections():
    docs = {}
    for path in sorted(glob.glob("spec/*.md")):
        name = path.split("/")[-1]
        sections = set()
        for line in open(path, encoding="utf-8"):
            m = HEADING.match(line)
            if m:
                sections.add(m.group(1).rstrip("."))
        docs[name] = sections
    return docs


def check_specs(docs):
    bad = []
    n_explicit = n_bare = n_external = 0
    for path in sorted(glob.glob("spec/*.md")):
        me = path.split("/")[-1]
        text = open(path, encoding="utf-8").read()
        ctx = None       # most recently named ARSIA document
        pending = None   # document named immediately before an upcoming §
        rfc_line = -1
        for m in TOKEN.finditer(text):
            line = text[: m.start()].count("\n") + 1
            if m.group(0).startswith("[RFC"):
                rfc_line = line
                pending = None
                continue
            if m.group(1) or m.group(2):
                ctx = f"ARSIA-{m.group(1) or m.group(2)}.md"
                pending = ctx if m.group(1) else None
                continue
            sec = m.group(3).rstrip(".")
            if pending:
                n_explicit += 1
                if sec not in docs[pending]:
                    bad.append(f"{path}:{line}: {pending} §{sec} (explicit)")
                pending = None
                continue
            if line == rfc_line:
                n_external += 1
                continue
            n_bare += 1
            if sec in docs[me] or (ctx and sec in docs[ctx]):
                continue
            target = f"{me}" + (f" nor {ctx}" if ctx else "")
            bad.append(f"{path}:{line}: §{sec} not in {target}")
    return n_explicit, n_bare, n_external, bad


def check_artifacts(docs):
    """Explicit ARSIA-X §N.N references inside JSON artifact text."""
    bad = []
    n = 0
    files = sorted(glob.glob("schemas/*.json")) + [
        "profiles/arsia-compliance-profiles.json"
    ]
    for path in files:
        text = open(path, encoding="utf-8").read()
        for m in EXPLICIT.finditer(text):
            n += 1
            target = f"ARSIA-{m.group(1)}.md"
            sec = m.group(2).rstrip(".")
            if sec not in docs[target]:
                line = text[: m.start()].count("\n") + 1
                bad.append(f"{path}:{line}: {target} §{sec}")
    return n, bad


def main() -> int:
    docs = load_sections()
    for name, sections in sorted(docs.items()):
        print(f"{name}: {len(sections)} numbered sections")
    n_explicit, n_bare, n_external, bad = check_specs(docs)
    n_artifacts, bad_artifacts = check_artifacts(docs)
    bad += bad_artifacts
    print(
        f"spec refs: explicit={n_explicit} bare={n_bare} external={n_external}; "
        f"artifact refs: {n_artifacts}; dangling={len(bad)}"
    )
    for b in bad:
        print("FAIL " + b)
    print("ALL LINKS OK" if not bad else "DANGLING REFERENCES")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
