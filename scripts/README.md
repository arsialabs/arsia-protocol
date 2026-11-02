<!-- SPDX-License-Identifier: BUSL-1.1 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
# Scripts

Utility scripts for the ARSIA Protocol specification repository.

## Files

| Script | Purpose |
|--------|---------|
| `validate_vectors.py` | Schema validation runner — validates all test vectors against their corresponding JSON Schemas (`--check-meta`, `--check-errors`, `--check-crypto`) |
| `check_consistency.py` | Repository-level invariants: schema meta-validation, strict `$ref` resolution, profiles-catalog validity, constant anti-regression, cross-artifact parity |
| `runtime_harness.py` | Reference implementations + tests for the deterministic runtime algorithms JSON Schema cannot express |
| `extract_examples.py` | Extracts every ```json block from spec prose; full examples must parse, envelope-shaped ones must validate against the message schema |
| `check_links.py` | Cross-reference link checker (M-14): every `§N.N` reference in specs and artifact descriptions must resolve to an existing heading |
| `rtm_counts.py` | Header-driven RTM parser — reproducible row/modal counts for the six traceability matrices |
| `regen_v2.py` | v2 signer/generator — re-signs affected vectors under the Draft-02 signing profile and logs the affected set |
| `gen_state_vec2.py` | Generator for state operation test vectors (development utility) |

## Usage

### validate_vectors.py

Validates every test vector in `test-vectors/arsia-test-vectors.json` against the schemas in `schemas/`.

```bash
python3 scripts/validate_vectors.py
```

Expected output: pass/skip/fail counts, with 0 failures. The CI workflow (`.github/workflows/validate-vectors.yml`) runs this on every push.

- **Runtime-only vectors** (`skip_schema: true`): the skip exempts only the runtime
  expectation. Each such vector is still validated structurally against its schema
  and reported as failing when it is structurally invalid.
- **Version handling** (Core §4.1.1): a message is validated under the procedure its
  own `v` selects — the exact schema for `"2.0"` (or an absent or malformed `v`), the
  major-2 compatibility schema for a newer 2.x minor, and rejection with
  `not_implemented` for another major. The summary prints the count per procedure.
- **`--check-crypto`**: each `crypto` block declares `expect_signature`. `valid`
  signatures must verify, `invalid` ones (signature negatives) must fail, and
  `absent` marks a message deliberately without `security`, for which only the
  canonical bytes are checked. The output reports verified signatures, asserted
  negatives and canonical-only blocks separately.

### Dependencies

- Python ≥ 3.12
- `jsonschema` (for Draft 2020-12 validation)
- `referencing` (for schema `$ref` registry resolution)
- `rfc8785` (for JSON canonicalization)
- `cryptography` (for Ed25519/ES256/RS256 signature verification)

Install: `pip install -r scripts/requirements.txt`
