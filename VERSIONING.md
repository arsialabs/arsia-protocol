<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
# Versioning

The ARSIA Protocol uses three versioning layers.

**Document drafts** (`Draft-01`, `Draft-02`, …) are revisions of the specification text. Drafts may contain breaking changes. The current release is **Draft-01.1** of all six specs. Implementors should expect changes between drafts.

**Errata** (`Draft-01.1`, `Draft-01.2`, …) are corrections to a published draft that do not constitute a new draft. Errata fix bugs where the specification text contradicts its own normative examples or other sections. Errata are retrocompatible — they never reject inputs that the original draft accepted. The current release is **Draft-01.1** (errata: payload.type regex corrected to match normative examples).

**Wire version** (`v` field in the message envelope) identifies the protocol version on the wire. The current wire version is **`1.0`**. A minor bump (`1.0` → `1.1`) adds new optional fields — existing implementations continue to work by ignoring unknown fields. A major bump (`1.0` → `2.0`) indicates incompatible changes and is expected to be rare.

**Extensions** add capabilities without changing the wire version. New compliance profiles, new transport bindings, and new payload types are extensions. They are published as separate documents and do not modify the core specs. JSON artefact files (profiles, schemas) carry a top-level `version` field following [Semantic Versioning](https://semver.org/).

When Draft-01 stabilises after community feedback and interoperability testing, it will be published as **v1.0 Final**. Until then, the specs carry `Status: Draft` in their headers.

---

_ARSIA Protocol ([arsiaprotocol.org](https://arsiaprotocol.org)) | by [Arsia Labs (Arsia Tecnologia Unipessoal Lda)](https://arsialabs.ai)_
