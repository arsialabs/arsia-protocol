<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Session Handover — 2026-08-05

**Tree state:** branch `draft-02`, **Draft-02 committed as `e299278`**
("feat!: release Draft-02 — wire version 2.0", 78 files, signed-off, no
co-author trailer per owner request). Working tree carries **7 uncommitted
paths**: this handover plus the post-commit hardening batch (item 7 below),
left uncommitted for owner review alongside the planned cosmetic pass.
**No tag yet** (only `draft-01` exists) and the branch has **not been pushed**
— both deferred by owner decision this session.

## What this session did, in order

1. **Canonical product documentation** generated at
   `docs/generated/arsia-protocol-overview.md` (Confluence-bound): what the
   repository is/does, architecture and validation-pipeline diagrams, eleven
   ASCII sequence diagrams (signing/verification, discovery, action invocation,
   oversight, broker relay, escrow, reversal, dual authorisation, onboarding,
   retention/audit, Art. 17 erasure), version determination, stage assessment
   (**Pre-launch**), and a discrepancy register. Owner decisions recorded there:
   document the working tree (not HEAD), diagram all eleven flows. The file is
   **generated — regenerate it rather than hand-editing** when the repo changes.
2. **`scripts/requirements.txt` fixed** — was missing `cryptography` and
   `rfc8785`, which would have failed the CI crypto step on a clean runner
   (`validate_vectors.py` hard-exits without `cryptography`; without `rfc8785`
   the canonicalizer silently degrades to a non-RFC-8785 fallback). Verified by
   installing the file into a clean venv and re-running `--check-crypto`
   (83/83).
3. **Five-item correction sweep** (owner-approved scope):
   - **Spec headers → Draft-02.** All six specs: `Version: 2.0`,
     `Draft-02 | July 2026`, canonical URLs `/draft-02`, References-section
     citations of companion specs, Core end-line — plus the fifteen
     "ARSIA Protocol v1.0" scope labels in body text updated to v2.0 so header
     and body stay coherent. Draft-01 **compatibility notes were left
     untouched** (signing-profile note, `retention_days` mapping, etc.).
   - **Published counts 1108 → 1109 MUST+MUST_NOT.** Root cause isolated before
     editing: the delta is exactly one row, `ROUTE-§2.2.2-12` (WebSocket
     heartbeat), harmonized SHOULD→MUST after the previous conformance snapshot.
     Corrected in CLAUDE.md, final-report (with explanatory note), decisions,
     closure-graph, release-checklist, session-handover-2026-07-29;
     `results/draft-02-conformance-report.md` regenerated against the current
     tree (also refreshed its stale meta-check and check_links blocks, date).
     NOT touched: `findings-status.md:43` (a `Core:1108-1111` line-number
     reference) and historical 1994/1153 figures.
   - **Identity §7.1.3 contradiction fixed.** The bullet claiming the
     `approval_decision` intent delivers the Phase 5 onboarding decision now
     matches §7.6 (intent `request`, payload `arsiaprotocol.onboarding/decision`,
     audit `event_type` `"approval_decision"`). The same stale wording in RTM row
     `IDENT-§7.6-01` was corrected. check_links arithmetic confirmed the edit
     (explicit 501→500, bare 809→811).
   - **Prose dependency lists** in CLAUDE.md and `scripts/README.md` now list
     all four packages (they omitted `referencing`); the README install line
     points at `requirements.txt` (single source, no future drift).
   - **Mechanical:** `runtime_harness.py` docstring now documents R1–R13; dead
     `--check` flag removed from `regen_v2.py` (unreferenced anywhere; default
     run is a documented dry run, `--apply` is the only write path);
     `rtm_counts.py` shebang moved to line 1 (+x set); stale "R1-R10" in
     release-checklist → R1-R13.
4. **Full battery re-run after every phase** — all green (see below). The
   generated overview was updated to match (resolved discrepancies moved to a
   dated "Corrections applied during extraction" section; three remain).
5. **Commit `e299278`** of all 78 paths, Conventional Commits with `!`
   (breaking), `Signed-off-by: Kirk Patrick`, no Claude co-author trailer.
6. **Enterprise repo comparison** (owner-requested): verified what
   `~/Projects/arsialabs/arsia-protocol-enterprise` differs from this repo,
   with focus on its implementation disclosures. Findings and recommendations
   in the dedicated section below.
7. **Post-commit hardening batch** (owner-approved, uncommitted):
   - `gen_state_vec2.py` guard — `main()` + `--apply` (dry run by default) +
     idempotency refusal when ITV-215…277 already present; import now
     side-effect free (verified: refusal exit 1, corpus hash unchanged).
   - New consistency check `no duplicate test-vector IDs` in
     `check_consistency.py` (**91 checks now**, was 90) — closes the silent
     duplication the meta-schema does not catch; verified against a synthetic
     duplicate, corpus restored.
   - Workflow hardening: `permissions: contents: read`, `concurrency` group
     with cancel-in-progress, actions SHA-pinned to same-major latest
     (checkout v4.4.0 `11d5960a…`, setup-python v5.6.0 `a26af69b…`,
     upload-artifact v4.6.2 `ea165f8d…`), plus `.github/dependabot.yml`
     (monthly, github-actions ecosystem) to keep pins current. Signed
     `draft-02` tag + branch/tag protection remain owner actions at tag time.

## Verification state (all reproducible, all green at handover)

```
python3 scripts/validate_vectors.py --check-meta --check-errors --check-crypto
  → 649 vectors, 0 fail; error paths 0 mismatches; crypto 83/83 (v2 profile)
python3 scripts/check_consistency.py  → ALL CHECKS PASSED (91 checks)
python3 scripts/runtime_harness.py    → R1–R13 ALL PASSED (73 assertions)
python3 scripts/extract_examples.py   → blocks=76 full=71 fragments=5 envelope-validated=9 failures=0
python3 scripts/check_links.py        → explicit=500 bare=811 external=19; artifact refs 391; dangling=0
python3 scripts/rtm_counts.py         → 1903 rows / 1109 MUST+MUST_NOT (deduplicated)
```

CI (`.github/workflows/validate-vectors.yml`) has still **never executed on
GitHub** (triggers on push/PR to `main`; nothing pushed). With requirements.txt
fixed it should pass — watch the first push.

## Key documents

- `docs/generated/arsia-protocol-overview.md` — the canonical product overview
  (regenerate, don't hand-edit). Its Discrepancies section lists the three
  remaining known issues.
- `docs/session-handover-2026-07-29.md` — the closure-session handover;
  conventions listed there still apply (guards inside `check_consistency.py`,
  re-sign only via `regen_v2.py`, typed retention, RTM ID uniqueness,
  historical records immutable — the global 1108→1109 correction followed the
  DR-P8 precedent of correcting published counts, with the note in
  final-report).
- `docs/draft-02-decisions.md`, `docs/draft-02-closure-graph.md`,
  `results/draft-02-conformance-report.md` (regenerated 2026-08-05).

## Open items

**Owner (explicitly deferred this session):** create the `draft-02` tag and
push/merge to `main` — "depois tratamos disso". Suggested when ready:
`git tag -a draft-02 -m "ARSIA Protocol Draft-02 — wire version 2.0" e299278`.
Then: legal review of qualified regulatory statements and integration-class
conformance tests (carried over from 2026-07-29).

**Known, documented, not yet fixed** (tracked in the overview's Discrepancies
and Development-stage gaps): README/CLAUDE.md "31 JSON Schemas" phrasing (30
schemas + 1 vector meta-schema); no linter/formatter config. (The
`gen_state_vec2.py` guard and the workflow hardening were fixed in item 7.)

**Cross-repo (next real work):** `arsialabs/arsia-protocol-sdk` and the demo
agents still implement wire 1.0 — migrate per
`docs/draft-02-migration-guide.md`.

## Enterprise repo comparison (`arsia-protocol-enterprise`)

**Lineage.** The enterprise repo is a fork of the public Draft-01, frozen at
wire 1.0: public tagged `draft-01` 2026-05-11 (`fbb30e7`); enterprise root is
2026-05-20 (`220550f "ARSIA Protocol Enterprise"`), 4 commits total, checked
out on branch `audit` at `701eb6a` (2026-07-22), clean tree, no tags. It was
the **audit target** (`docs/auditoria-spec-draft-01.md` cites
`enterprise @ dacbc4a`) and matches the Draft-02 plan's reproduced baseline
exactly (613 vectors / 73 skips; 31 schemas incl. the abolished
`arsia-broker-relay-audit`; `v` validated by pattern, not `const`).

**What enterprise has that public does not — the implementation disclosures.**
"Implementation Notes — ARSIA Server Reference Implementation" sections added
to the specs, describing the reference server:

- Core Appendix C — five-guard fixed pipeline
  (identity→compliance→actions→assets→state) with ordering rationale; C.2
  `public_reason` vs internal `reason` error split.
- Identity §12.1–12.9 — **JWT signed with the server's own Ed25519 key (no
  dedicated OAuth AS)**; agent key cache (rotation → 401 until re-onboard);
  **in-memory revocation set (not persisted without PostgreSQL)**; Phase 0
  invite validation; approval-required mode; CHECK-03 skip precondition;
  three-way capability intersection (invite ceiling); re-authentication;
  crash recovery.
- Actions §8 — policy×token nine-combination table (most restrictive wins);
  HTTP 202 for oversight hold.
- State §11.4 — **hash chain RECOMMENDED but not implemented** (immutability
  via PostgreSQL triggers only); §11.5 — in-memory audit fallback (records
  lost on restart; dev-only).

Also enterprise-only: 4 Portuguese audit/strategy docs
(auditoria-independente…, pesquisa-panorama-2026,
propostas-draft-02-classe-mundial, relatorio-consolidado-decisoes-verificadas),
2 `results/` reports (audit-schemas-vectors 2026-04-30; spec-sender-verification
— the "sender = `from`, never the gateway" verification).

**Licensing divergence.** Enterprise strips all SPDX/CC BY-SA headers and
governance files (no LICENSE/CLA/CONTRIBUTING/SECURITY/README); its Core states
adoption "requires a commercial licence or written permission from Arsia Labs"
where the public repo states CC BY-SA / no licensing barriers.

**Crypto facts.** `keypairs.json` identical in both (modulo the licence
comment); 83 crypto vectors in both, but enterprise signatures use the Draft-01
profile (whole `security` removed) — none verify under Draft-02, by design.
The reference server documented by the notes therefore implements wire 1.0 and
is in the same migration queue as the SDK; Identity §12.1's simplified token
model additionally predates the Draft-02 issuer-trust hardening (Core §6.5,
harness R11).

**Leak check (clean).** Grep of the public repo (spec/, docs/, schemas/,
including the generated overview) for "ARSIA Server", "Five-Guard", "Agent Key
Cache", guard-pipeline terms: zero hits. The public Identity's out-of-order
§12 (BYOA after References) is explained by this lineage — it was enterprise
§12.10; only BYOA was absorbed.

**Recommendation (assistant's assessment, owner to decide)** — split the
disclosures in three classes rather than one policy:

1. **Keep out of the public repo** (current state, correct): the operational
   security details — key cache staleness, revocation persistence, in-memory
   audit, hash-chain absence, guard-ordering rationale. Scope argument beats
   the secrecy argument: CLAUDE.md defines this repo as spec + artifacts +
   validation tooling only; server implementation notes don't belong here
   regardless. Also consistent with the open-spec / commercial-implementation
   licensing model.
2. **Generalize and publish** the 2–3 items every independent implementer will
   hit, as informative guidance (natural home: State §11 "Implementation
   Guidance (Informative)" / Actions): the CHECK-03 skip-when-no-oversight
   precondition (the missing second example next to CHECK-05); the
   "most-restrictive-wins" policy×token intersection principle (without the
   server's table); a sentence confirming that *additional tightening*
   restrictions (three-way intersection / invite ceiling) are conformant under
   Identity §7.1.3. Informative additions need no Issue per CONTRIBUTING §4,
   but an Issue would document the decision.
3. **Customer-facing security disclosure** for the compliance-relevant
   limitations: in-memory audit fallback and hash-chain absence directly
   affect a customer's own DORA/MiFID II obligations — "not in the public
   repo" must not become "not disclosed to customers". Same honesty line
   Draft-02 already took with `known-limitations`.

**Rot risk:** the enterprise Implementation Notes cite Draft-01 sections and
describe a wire-1.0 server — already stale. When the server migrates to 2.0,
decide their long-term home (likely the server's own repo, next to the code
they document).

**This handover file is uncommitted by design** — owner decides whether/when it
enters history.
