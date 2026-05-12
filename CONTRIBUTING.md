<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Contributing to ARSIA Protocol

Thank you for considering a contribution to the ARSIA Protocol.

This repository contains the normative specification, documentation, machine-readable interoperability artifacts, test vectors, profiles, scripts, tooling, and CI workflows that support the ARSIA Protocol.

Contributions of every size are welcome, from typo fixes and clarification notes to new test vectors, schemas, profiles, validation improvements, and tooling updates.

This guide explains what you can contribute, how the review process works, and how to submit changes.

## 1. Licensing Overview

ARSIA Protocol uses different licenses for different types of materials.

### 1.1 Specification and Documentation

Human-readable specification and documentation materials are licensed under the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0).

This includes, unless otherwise stated:

- `spec/`
- `docs/`
- `README.md`
- `AUTHORS.md`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `VERSIONING.md`
- `CLA.md`
- other human-readable protocol documentation

See [`LICENSE-SPEC.md`](licenses/LICENSE-SPEC.md).

### 1.2 Technical Interoperability Artifacts

Machine-readable technical interoperability artifacts are licensed under the Apache License 2.0.

This includes, unless otherwise stated:

- `schemas/`
- `profiles/`
- `test-vectors/`
- example payloads
- validation fixtures
- conformance fixtures
- other machine-readable protocol artifacts

See [`LICENSE-ARTIFACTS.md`](licenses/LICENSE-ARTIFACTS.md).

### 1.3 Software Components

Software components are licensed under the Business Source License 1.1.

This includes, unless otherwise stated:

- SDKs
- reference implementations
- `scripts/`
- `tools/`
- `.github/`
- `.github/workflows/`
- `.github/workflows/validate-vectors.yml`
- CI/CD workflows
- automation code
- software source code
- executable components
- buildable components

Each covered version converts to Mozilla Public License Version 2.0 (MPL-2.0), without the Exhibit B "Incompatible With Secondary Licenses" notice, after the applicable Change Date.

See [`LICENSE-CODE.md`](licenses/LICENSE-CODE.md).

## 2. Contributor License Agreement

All contributions are accepted under the [ARSIA Protocol Individual Contributor License Agreement](CLA.md) (the "CLA").

The CLA grants Arsia Labs (Arsia Tecnologia Unipessoal Lda) and recipients of the Project copyright and patent licenses to Your Contributions.

**You retain ownership of Your Contributions.** The CLA is a license grant, not a copyright assignment.

The CLA also allows Arsia Labs to use, sublicense, commercially license, and relicense Contributions as part of the Project, including under the Project Licenses and commercial licensing terms.

You indicate acceptance of the CLA by adding a `Signed-off-by` line to every commit message.

The `git` command adds this automatically with the `-s` flag:

```bash
git commit -s -m "docs: clarify broker relay example"
```

The resulting trailer looks like:

```
Signed-off-by: Your Name <your.email@example.com>
```

Pull requests without a `Signed-off-by` trailer on every commit cannot be merged.

If you forgot to sign off earlier commits, you can fix them with:

```bash
git commit --amend -s
```

for the most recent commit, or:

```bash
git rebase --signoff main
```

for a range of commits.

The name and email in the `Signed-off-by` trailer must correspond to your real identity. Pseudonymous contributions cannot be accepted.

## 3. What You Can Contribute

The following kinds of contributions are welcome and usually do not require prior discussion:

- **Specification text corrections** — typos, grammar, broken cross-references, inconsistent terminology, or unclear language.
- **Editorial improvements** — clearer phrasing, better examples, improved diagrams, or improved section organization.
- **Schema improvements** — tightening constraints, adding missing description fields, fixing regex patterns, or aligning schemas with normative text.
- **Profile improvements** — clarifications or corrections to compliance profiles.
- **New test vectors** — additional valid or invalid vectors that exercise underrepresented protocol behavior.
- **New conformance fixtures** — additional machine-readable examples that help implementers validate compatibility.
- **Validation tooling improvements** — improvements to scripts and CI workflows that validate schemas, profiles, or test vectors.
- **Errata reports** — inconsistencies between specification text, schemas, profiles, and test vectors.

## 4. What Requires Discussion First

Please open a GitHub Issue before submitting a pull request for:

- new protocol features;
- new fields in envelopes, messages, profiles, or compliance structures;
- changes to normative requirements using MUST, MUST NOT, SHOULD, SHOULD NOT, or MAY;
- changes to wire format or compatibility behavior;
- new primitives;
- new specification sections;
- new compliance profiles;
- changes to published conformance tests;
- large restructurings of `spec/`, `schemas/`, `profiles/`, or `test-vectors/`;
- changes to licensing files, CLA terms, patent language, or trademark language;
- changes that may affect backward compatibility.

Opening an issue first avoids wasted work and gives maintainers a chance to flag compatibility, governance, or licensing concerns early.

## 5. How to Contribute

1. **Fork** the repository at `https://github.com/arsialabs/arsia-protocol`.
2. **Create a branch** from `main`.
   Use a short, descriptive branch name, for example:
   - `fix-state-section-ref`
   - `add-stv-vector-purge`
   - `improve-vector-validation`
3. **Make your changes.**
   Keep each pull request focused on one logical unit of work.
4. **Check licensing scope.**
   Make sure your changes are in the correct path and use the correct license:
   - documentation/specification: `CC-BY-SA-4.0`
   - schemas/profiles/test vectors: `Apache-2.0`
   - scripts/tools/workflows/code: `BUSL-1.1`
5. **Validate your changes locally.** See [Validation](#6-validation).
6. **Commit** using conventional commit messages and the `-s` sign-off flag.
7. **Open a pull request** against `main`.
   In the pull request description, include:
   - motivation for the change;
   - related issue, if any;
   - summary of changed files;
   - validation steps you ran;
   - any compatibility concerns.

## 6. Validation

Before opening a pull request, please run the relevant checks below. These are the same types of checks that reviewers and CI may run.

### 6.1 Test Vector Validation

Run the test vector validator:

```bash
python3 scripts/validate_vectors.py
```

Expected output: pass, skip, and fail counts with 0 failures.

This validates test vectors against the corresponding JSON Schemas.

### 6.2 JSON Parsing

Every file under the following directories must parse as JSON with no errors:

- `schemas/`
- `profiles/`
- `test-vectors/`

You can use tools such as `jq`, Python's `json` module, or your editor's JSON parser.

### 6.3 Signature Verification

For any valid vector you add or modify that includes a `crypto` object, recompute the RFC 8785 canonical form and verify the signature.

Example:

```python
import json
import base64
import rfc8785
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

vector = json.load(open("test-vectors/arsia-test-vectors.json"))["vectors"][0]

if "crypto" in vector:
    message = {k: v for k, v in vector["message"].items() if k != "security"}
    canonical = rfc8785.dumps(message)
    assert canonical.hex() == vector["crypto"]["canonical_bytes_hex"]

    pub = Ed25519PublicKey.from_public_bytes(
        bytes.fromhex(vector["crypto"]["public_key_hex"])
    )

    sig_b64 = vector["crypto"]["signature_base64url"]
    sig = base64.urlsafe_b64decode(sig_b64 + "=" * (-len(sig_b64) % 4))

    pub.verify(sig, canonical)
```

Placeholder signatures are never accepted. All valid vectors with a `crypto` object must have real keypairs and verifiable signatures.

### 6.4 Specification Cross-References

If you move sections, rename sections, renumber anything, or add references to other sections, check that every § reference still points to the correct place.

### 6.5 CI Workflow Validation

The repository includes CI workflow validation, including:

- `.github/workflows/validate-vectors.yml`

This workflow is a software component and is licensed under Business Source License 1.1.

Changes to this workflow should be reviewed carefully because they affect project validation and release confidence.

## 7. Specification Conventions

A few conventions are enforced across the repository:

- **RFC 2119 / BCP 14 keywords** appear in ALL CAPS only when used normatively:
  - `MUST`
  - `MUST NOT`
  - `SHOULD`
  - `SHOULD NOT`
  - `MAY`
  - `REQUIRED`
  - `RECOMMENDED`
  - `OPTIONAL`

- **Specification filenames** use the form:
  `ARSIA-{Primitive}.md`
  Example:
  - `ARSIA-Core.md`
  - `ARSIA-State.md`

- **Schema filenames** use the form:
  `arsia-{name}.schema.json`

- **Test vector IDs** use the following prefixes:
  - `CTV-` — Core
  - `ITV-` — Identity
  - `RTV-` — Routing
  - `ACTV-` — Actions
  - `STV-` — State
  - `ATV-` — Assets
  - `INV-` — Invalid vector, any spec

- **Commit messages** follow Conventional Commits:
  - `feat:`
  - `fix:`
  - `docs:`
  - `test:`
  - `chore:`
  - `ci:`
  - `refactor:`

  Keep the subject line under 72 characters.

## 8. SPDX Headers

Files should include SPDX headers where the file format permits comments.

For specification and documentation Markdown files:

```html
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
```

For code, scripts, tools, and workflow files where `#` comments are valid:

```python
# SPDX-License-Identifier: BUSL-1.1
# Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda)
```

For JavaScript or TypeScript files:

```javascript
// SPDX-License-Identifier: BUSL-1.1
// Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda)
```

For JSON files, do not add comments because JSON does not support comments. Licensing for JSON schemas, profiles, and test vectors is handled by `licenses/LICENSE-ARTIFACTS.md`, repository metadata, and any applicable REUSE/SPDX annotations.

## 9. Review Process

Every pull request is reviewed by a maintainer.

- Small editorial changes may be merged quickly.
- Changes touching normative text usually require more review.
- Specification changes require review of affected schemas, profiles, and test vectors.
- Changes to schemas or test vectors must remain consistent with the normative specification.
- Changes to scripts, tools, or CI workflows must preserve validation behavior.
- Sign-off is verified on every commit.
- Licensing-sensitive changes may require additional review by Arsia Labs.

Maintainers may request changes, suggest alternatives, split a pull request, or decline a contribution.

If a contribution is declined, maintainers will try to explain the reason so you can decide whether to rework and resubmit.

## 10. Security Issues

Please do not report security vulnerabilities through public GitHub issues,
pull requests, or discussions.

If you believe you have found a security vulnerability in ARSIA Protocol,
please report it privately by email:

security@arsialabs.ai

See [SECURITY.md](SECURITY.md) for details.

## 11. Code of Conduct

All contributors, maintainers, and participants in ARSIA Protocol community
spaces are expected to follow the [ARSIA Protocol Code of Conduct](CODE_OF_CONDUCT.md).

The Code of Conduct applies to issues, pull requests, discussions, reviews,
community channels, and public representation of the project.

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to:

conduct@arsialabs.ai

If that address is not available, reports may be sent through the contact
channels listed at:

https://arsialabs.ai

## 12. License

By contributing to ARSIA Protocol, you agree that your Contributions will be licensed under the applicable Project License depending on their nature and location:

- `CC-BY-SA-4.0` for human-readable specification and documentation materials;
- `Apache-2.0` for machine-readable technical interoperability artifacts;
- `BUSL-1.1` for software components, including scripts, tools, automation code, and CI/CD workflows.

Software components licensed under `BUSL-1.1` convert to `MPL-2.0`, without the Exhibit B "Incompatible With Secondary Licenses" notice, after the applicable Change Date.

All Contributions are subject to the [ARSIA Protocol Individual Contributor License Agreement](CLA.md).

---

_ARSIA Protocol ([arsiaprotocol.org](https://arsiaprotocol.org)) | by [Arsia Labs (Arsia Tecnologia Unipessoal Lda)](https://arsialabs.ai)_
