<!-- SPDX-License-Identifier: BUSL-1.1 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
# Scripts

Utility scripts for the ARSIA Protocol specification repository.

## Files

| Script | Purpose |
|--------|---------|
| `validate_vectors.py` | Schema validation runner — validates all test vectors against their corresponding JSON Schemas |
| `gen_state_vec2.py` | Generator for state operation test vectors (development utility) |

## Usage

### validate_vectors.py

Validates every test vector in `test-vectors/arsia-test-vectors.json` against the schemas in `schemas/`.

```bash
python3 scripts/validate_vectors.py
```

Expected output: pass/skip/fail counts. The CI workflow (`.github/workflows/validate-vectors.yml`) runs this on every push.

### Dependencies

- Python ≥ 3.12
- `jsonschema` (for Draft 2020-12 validation)
- `rfc8785` (for JSON canonicalization)
- `cryptography` (for Ed25519/ES256/RS256 signature verification)

Install: `pip install jsonschema rfc8785 cryptography`
