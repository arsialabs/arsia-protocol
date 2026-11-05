# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

The normative specification repository for the ARSIA Protocol — EU regulatory compliance as a wire-level primitive for AI agents. It contains **only** the spec text, machine-readable artifacts, and validation tooling. SDKs, reference implementations, and demos live in separate repos (e.g. `arsialabs/arsia-protocol-sdk`).

Current release: **Draft-02** (all six specs), wire version `2.0`. The protocol has one version — do not defer fixes to hypothetical future versions; Draft-02 supersedes Draft-01 entirely (see docs/draft-02-migration-guide.md).

## Commands

```bash
pip install -r scripts/requirements.txt   # jsonschema, referencing, rfc8785, cryptography (Python >= 3.12)

# Validate all 893 test vectors against schemas. Target: 0 failures.
python3 scripts/validate_vectors.py

# Full verification battery — what CI runs (.github/workflows/validate-vectors.yml)
python3 scripts/validate_vectors.py --check-meta --format summary
python3 scripts/validate_vectors.py --check-errors --format summary
python3 scripts/validate_vectors.py --check-crypto --format summary
python3 scripts/check_consistency.py   # 129 repo invariants: schema meta/$id/$ref, prose↔schema enum parity, constant anti-regression, RTM drift linter
python3 scripts/runtime_harness.py     # R1-R22: deterministic spec algorithms (calendar arithmetic, floors, matching, precedence)
python3 scripts/extract_examples.py    # every ```json block in spec/ parses; envelope examples validate
python3 scripts/check_links.py         # every §N.N reference resolves (specs + schema descriptions)

# Run a subset
python3 scripts/validate_vectors.py --filter 'STV-*'          # by vector ID glob
python3 scripts/validate_vectors.py --schema arsia-message    # by schema name substring

# Reproducible RTM counts (2045 rows / 1241 MUST+MUST_NOT)
python3 scripts/rtm_counts.py

# Output formats: tap (default), summary, junit
```

New consistency guards go INSIDE `scripts/check_consistency.py` as additional `check(...)` calls — never as a new script. The RTM drift linter there carries a synthetic self-test that fails if the detector goes dead.

## Architecture — the consistency web

The repository is a set of artifacts that must stay mutually consistent. A normative change in one place almost always requires touching the others:

1. **`spec/`** — six normative documents in a "5+1" architecture: `ARSIA-Core.md` (envelope, EdDSA signing, discovery, authorization, transport) plus five primitives that spell ARSIA: **A**ctions, **R**outing, **S**tate, **I**dentity, **A**ssets. Specs cross-reference each other by `ARSIA-X §N.N` — renumbering a section breaks references in other documents.
2. **`schemas/`** — 34 JSON Schemas (Draft 2020-12), each mapped to a specific spec section (see `schemas/README.md` for the mapping). `arsia-common.schema.json` holds shared definitions; `arsia-test-vectors.meta.json` is the meta-schema for the vector file itself.
3. **`test-vectors/arsia-test-vectors.json`** — 893 vectors in three discriminated formats: `message-only` (`message` + `valid`), `schema-ref` (`schema_ref` + `data` + `expected`), and `hybrid` (`schema_ref` + `message` + `expected`). 195 vectors have `skip_schema: true` for runtime-only constraints, individually classified (with the coverage actually executed) in `docs/draft-02-skip-classification.md`; a skip vector is still validated structurally. Messages are validated under the Core §4.1.1 procedure their own `v` selects. Each `crypto` block declares `expect_signature` (`valid`/`invalid`/`absent`); a vector whose expectation rests on a MAY or an optional configuration declares its `posture`. Signed vectors use the Draft-02 signing profile (envelope minus only `security.sig`); re-sign an edited valid vector with `scripts/regen_v2.py --ids <ID,…>` (dry run unless `--apply`). `keypairs.json` holds the 17 test keypairs — committed intentionally, not secrets.
4. **`profiles/arsia-compliance-profiles.json`** — the 7 compliance profiles (GDPR, EU AI Act ×2, MiFID II, PAC, DSA, DORA), defined normatively in ARSIA-State §6 and referenced by Core §4.3.6. Profile names, retention floors, and oversight modes must match between prose, this catalog, and schemas.
5. **`docs/rtm/`** — six Requirements Traceability Matrices tracing every MUST/SHOULD/MAY to schema and test vector.

`docs/auditoria-spec-draft-01.md` is the Draft-01 audit whose findings Draft-02 resolved — resolution status in `docs/draft-02-final-report.md`, decisions in `docs/draft-02-decisions.md` (DR-P8/DR-P9 record the post-RC residual sweeps), and the item-by-item de facto verification with the relation graph in `docs/draft-02-closure-graph.md`. `docs/spec-audit-draft-01.md` is an earlier audit kept for reference. Consult these before "fixing" an inconsistency — it may already be resolved or deliberately scoped (e.g., runtime-delegated rules in `docs/draft-02-skip-classification.md`).

## Conventions

- **Test vector IDs**: `CTV-` Core, `ITV-` Identity/cross-spec, `RTV-` Routing, `ACTV-` Actions, `STV-` State, `ATV-` Assets, `INV-` invalid. `test-vectors/README.md` records the next available IDs — update it when adding vectors.
- **Crypto in vectors is real**: any valid vector with a `crypto` object must carry a verifiable signature over the RFC 8785 canonical form of the message with `security` present and only `security.sig` removed (the Draft-02 signing profile, Core §5.1). Placeholder signatures are never accepted; use `keypairs.json` and verify with `--check-crypto`.
- **RFC 2119 keywords** (MUST, SHOULD, MAY, …) appear in ALL CAPS only when normative.
- **Licensing is path-dependent** — put files in the right place and use the matching SPDX header:
  - `spec/`, `docs/`, root Markdown → CC-BY-SA-4.0 (`<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->`)
  - `schemas/`, `profiles/`, `test-vectors/` → Apache-2.0 (no headers inside JSON files)
  - `scripts/`, `.github/` → BUSL-1.1 (`# SPDX-License-Identifier: BUSL-1.1`)
  - All headers include the line `Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda)`.
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`, `ci:`, `refactor:`), subject under 72 chars. Commit only when explicitly asked; never push unless explicitly asked.
  - Every commit carries exactly this CLA trailer, as its last line: `Signed-off-by: Kirk Patrick <kirk@arsialabs.ai>`. Add it explicitly with `git commit --trailer "Signed-off-by: Kirk Patrick <kirk@arsialabs.ai>"`. Do not rely on `git commit -s`: it signs with the local git identity, which may differ.
  - No other trailers or attribution: no `Co-Authored-By`, no "Generated with", no tool attribution of any kind.
  - Verify before reporting: `git log -1 --format=%B | git interpret-trailers --parse` must print only the Signed-off-by line above.
- Normative changes (new fields, MUST/SHOULD changes, wire format, new profiles) require a GitHub Issue before a PR — see CONTRIBUTING.md §4.
