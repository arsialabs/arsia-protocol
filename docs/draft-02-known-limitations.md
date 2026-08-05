<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# ARSIA Draft-02 — Known Limitations and Residual Risks

Honest, load-bearing statements of what Draft-02 does NOT guarantee. Each entry
names the normative anchor that states the limitation in place.

## Residency and relay

1. **Relay attestation is evidence, not proof.** The attestation demonstrates
   that an identified, registered broker asserts having received and forwarded
   exactly this envelope under a policy. It does not prove the physical location
   of every processing step (Routing §5.3, §7.4.1).
2. **Recipient in-zone processing is not wire-verifiable.** The obligation is
   normative (Routing §5.1 item 4) but enforced by deployment and evidenced
   operationally (zone-stored audit records, attestation chain, inspections) —
   an accepted residual (Core §13.1 adversary 11).
3. **Brokers observe traffic metadata.** No-read/no-log obligations bound
   content exposure, but the broker necessarily learns sender, recipient,
   timing, and size.

## Audit and tamper evidence

4. **Tamper evidence is bounded** (State §7.2): mid-chain modification/removal/
   reordering are detectable against an independently held chain head; owner-level
   full rewrite, tail truncation, write-time omission, and forks are NOT detected
   by append-only + local hash chain alone. External anchoring is permitted, not
   mandated.
5. **Counterparty owner backfill.** When a counterparty's IdentityRecord is
   unresolvable at processing time, `counterparty_owner_id` arrives by appended
   correction record — there is a window in which accountability is by agent-id
   only (State §7.1).
6. **`regulated_entity` is self-asserted** (Identity §1.2); counterparties
   requiring assurance must verify out-of-band.

## Trust bootstrap

7. **Issuer trust and agent resolution are provisioning problems.** Core §6.5/§6.6
   make them explicit, deterministic, and fail-closed, but the protocol cannot
   conjure the first trusted mapping: it must arrive out-of-band (configuration,
   onboarding, operator registry).
8. **Revocation has a propagation window** bounded by the 3600 s JWKS cache
   ceiling (Core §5.2/§7.3); signatures accepted inside the window are identified
   via the recorded JWKS fetch timestamp, not prevented.
9. **A compromised approver with a live token** can approve until revoked; the
   protocol bounds this with non-delegable capability, signing, chain
   verification, and audit — not prevention (Core §13.1 adversary 8).

## Validation-layer boundaries (deliberate, classified)

10. **Calendar retention floors, per-currency fixed scale, registry membership,
    and effective-oversight resolution are runtime rules**, not JSON Schema
    constraints. They are covered by reference logic (`scripts/runtime_harness.py`)
    and runtime vectors (94 classified skips), not by schema validation
    (`docs/draft-02-skip-classification.md`).
11. **Schemas validate exactly one minor version.** Forward compatibility with
    future 2.x minors is a runtime behaviour (Core §4.1.1), intentionally outside
    the published schema.
12. **ISO 4217 catalog editions are operational.** The receiver's declared
    edition governs; edition skew between parties is logged, not arbitrated
    (Assets §3.1.1).

## Legal qualifications

13. **No legal claims are made.** PSD2/SCA (Assets §5.2/§6.3), GDPR hash/erasure
    analysis (State §7.2), EU AI Act role allocation (Identity §4.4), and DORA
    incident classification (Assets §6.2.4) are stated as technical contributions
    subject to legal review; regulatory citations have not been verified against
    the legal texts by counsel.

## Deferred design questions

14. **Bitemporality (H4).** State remains single-axis (valid time). "What did the
    system believe at T1 about T0" requires reconstruction from the audit trail's
    `timestamp`/`processed_at` distinction and append-only version history —
    coarse, not a query primitive. Revisit if regulatory dispute practice demands
    it.
15. **No DNS-based agent resolution.** Deliberately registry-based in Draft-02; a
    DNS convention would be additive (Core §6.6).
16. **Extension-profile discovery is by advertisement only**
    (`compliance_profiles_supported`); there is no central registry or search.

## Testing boundaries

17. **Integration-class conformance tests** (two live implementations: WebSocket
    behaviour, broker end-to-end, key rotation, onboarding phases) are specified
    in the documents and required for conformance claims, but are not executable
    from this repository alone (`results/draft-02-conformance-report.md`).
18. **Broker no-read/no-log/no-store, encryption at rest, physical location,
    backup purge propagation** are deployment-inspection and operational-evidence
    requirements — release gates by procedure, never simulated by the suite.
