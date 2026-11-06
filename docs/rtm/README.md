<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
# Requirements Traceability Matrix (RTM)

This directory contains per-spec RTM files that trace every normative requirement to its schema coverage and test vector coverage.

## Files

| File | Spec | Description |
|------|------|-------------|
| `ARSIA-Core.rtm.md` | Core | Foundation — envelope, signing, discovery, authorization, transport |
| `ARSIA-Actions.rtm.md` | Actions | Capabilities, human oversight, explainability |
| `ARSIA-Routing.rtm.md` | Routing | Message routing, broker topology, data residency |
| `ARSIA-State.rtm.md` | State | State lifecycle, GDPR, compliance profiles, audit trail |
| `ARSIA-Identity.rtm.md` | Identity | Agent identity, certificates, onboarding |
| `ARSIA-Assets.rtm.md` | Assets | Transactions, escrow, MiFID II / DORA / PSD2 |

## Format

Each RTM uses a 9-column table:

| Column | Description |
|--------|-------------|
| ID | Requirement identifier (e.g., `CORE-§4.1.3-01`) |
| § | Spec section reference |
| Modal | BCP 14 keyword (MUST, SHOULD, MAY, etc.) |
| Layer | Implementation layer (sdk, deployment, external, etc.) |
| Kind | Requirement type (structural, behavioural, procedural, etc.) |
| Requirement | Normative text |
| Schema | Schema referenced by the row, or `—` |
| Vector | Test vectors cited by the row (vector IDs only), or `—` |
| Evidence | For MUST, MUST_NOT and REQUIRED rows: the evidence or disposition (below); `—` for every other row |

## Evidence column

Every mandatory row (MUST, MUST_NOT, REQUIRED) states its evidence or disposition as tokens
separated by `; `. A row may carry several: a schema reference for its structure and an
executed check for a runtime condition, for example. `scripts/check_consistency.py` verifies
each token against the executions of the same run — a citation of something that did not run
and pass fails the check (coverage SC4, A-64).

| Token | Meaning | What the guard verifies |
|-------|---------|-------------------------|
| `schema-ref:<name>` | Documentary reference to `schemas/<name>.schema.json` | The file exists and the row's Schema column names it. It does **not** assert that the schema enforces the requirement |
| `struct:<IDs>` | Structural validation executed by `scripts/validate_vectors.py` | Each vector's observed result equals its expected one (a negative is rejected, through the expected error path) |
| `raw:<IDs>` | Core §5.2 steps 2-4 executed on raw vectors | Each raw vector is accepted or rejected as stated |
| `crypto:<IDs>` | Canonical bytes and signature checked by `--check-crypto` | Each result passed (a signature negative passes when its verification fails) |
| `exec:<Rn>:<IDs>` | Behavioural execution by harness rule Rn | A passing check of that rule declared each vector as consumed (`# executed <Rn> <IDs>` in the harness output); a vector ID in a check's name does not count |
| `check:`<name>`` | A passing check of the harness or of `check_consistency.py`, without a vector | A passing check with exactly that name; only a trailing parenthesised count (e.g. ` (3 chains, 7 entries)`) may be omitted |
| `out-of-repo(<code>)` | Disposition: the requirement binds a deployment, operator or third party | Code in `transport`, `infrastructure`, `operator`, `external-party`, `implementation-internal` |
| `untested(<code>)` | Disposition: nothing in this repository executes it | Code in `no-reference-model`, `integration`, `structural-only`; optionally `→ <document>` |

`untested` and `out-of-repo` are traceability states, not evidence of a passed test.
`untested(structural-only)` marks a behavioural row whose only evidence is structural.
Every vector a mandatory row cites appears in an execution token. The counts by modal and by
evidence kind are printed by `scripts/rtm_counts.py`.

**Limit.** Traceability is verified for every mandatory row; schema references are verified
mechanically, without a full semantic review of each schema's ability to enforce each
requirement. The column supports a traceability claim, not a claim of complete behavioural
coverage of the protocol.
