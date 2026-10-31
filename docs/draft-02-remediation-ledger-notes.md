<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Draft-02 Remediation Ledger — Open Notes

Part of the [Draft-02 remediation ledger](draft-02-remediation-ledger.md). This file
holds the Open notes register (§8); its section number is that of the main ledger.
Notes are observations, not a register with counts.

## 8. Open notes

The regulatory Open notes (C2, C2.1) are in the [regulatory file][reg8].

- **Vectors vs MAY behaviour:** ITV-545 is expected-invalid on a MAY (Core
  §4.1.3). The posture is to be defined in the vector cycle (DR-0.3).
- **A-34 proxy:** exact for the current corpus (INV-18, INV-19). An explicit
  crypto field is the definitive fix (vector/meta-schema cycle). DR-5: the chain
  negativity of ITV-597..599 is likewise carried outside the vector format (the
  tampered-chain map in `check_consistency.py`) until that explicit field exists.
- **ITV-546:** its coverage gap is mapped to A-62.
- **A-35:** resolved in C3b — the checker and the generator refuse to run without
  rfc8785.
- **CI:** `validate-vectors` has been red by design since C0.5, and stays red
  until the vector cycle. Since LM2, CLAUDE.md states this next to the validation
  command (32 runtime-only vectors fail by design).
- **Out-of-date docs:** `docs/draft-02-skip-classification.md` and
  `scripts/README.md` are out of date on the ITV-545/546 reasons, skip
  semantics and crypto output (follow-up under A-65).
- **Missing SPDX headers:** `docs/auditoria-spec-draft-01.md` and
  `docs/spec-audit-draft-01.md` lack the CC-BY-SA-4.0 header (follow-up; not
  fixed in C1).
- **Stale published counts (C2):** the root `README.md`, `CLAUDE.md` and files
  in `docs/` still state 649 vectors and 1109 MUST+MUST_NOT. After C2 the
  figures are 653 vectors and 1903 RTM rows / 1114 MUST+MUST_NOT. Only
  `test-vectors/README.md` was updated in C2, where the `ITV-` prefix count
  had been 578 against an actual 579 before C2. After C3a the figures are 666
  vectors and 1903 / 1114 (unchanged); `test-vectors/README.md` was updated again.
  Ledger maintenance (LM): the current-state documents (`README.md`, `CLAUDE.md`,
  `docs/FAQ.md`, `docs/getting-started.md`) now carry the tool-computed figures; dated
  records keep the figures they measured.
- **Breach-notification schema coverage (C2 observation):** no schema-ref
  vector exercises `arsia-breach-notification.schema.json`. ITV-556/557 are
  message-only, and the envelope schema does not validate the payload against
  it. C2 validated both payloads against the breach schema by hand.
- **`oversight_timeout` suspended (C3a, A-3):** Core §4.3.6.5 requires logging
  it, but it is one of the three `required_within_24h` definitions that DR-2
  replaces with one mechanism. It is added (or dropped) in the DR-2 cycle.
- **`ict_incident` audit extension undefined (C3a observation):** State §7.1 and
  Assets §6.2.3 promise incident classification fields in the `ict_incident`
  record, but no field is defined in prose or schema. It is an explicit exception
  of the A-59 guard.
- **`jwks_fetched_at` (C3a observation):** State §7.1 makes it REQUIRED for any
  signed compliance-relevant message; the schema cannot express that condition
  and leaves it optional. It is an explicit exception of the A-59 guard and is
  tracked by A-58.
- **Rollback audit fields undefined in schema (C3a observation):** Actions §4.2
  ("Rollback Audit") requires the original action's `message_id` and
  `action_id`, the rollback request's `message_id`, a timestamp and full/partial
  status. Neither the schema nor the State §7.1 table defines these fields
  (candidate finding).
- **Plain `asset_transfer` records (C3a observation):** the former §7.1 table
  claimed `payment_reference`, `amount` and `original_audit_id` for
  non-escrow transfers and reversals. No originating prose or schema rule
  supports that, so the claim was removed from the table. The audit content of
  plain `asset_transfer` records is undefined (candidate finding).
- **`pii_special_categories` in `state_set` records (C3a observation):** it is
  required by the schema and the §7.1 table, but the originating operation
  prose (State §3.1.2 table, §8.3 rule 3) does not list it; §2.1.11 concerns
  Art. 30 records.
- **`relay_id` naming (C3a observation):** relay receipt and error payloads
  (Routing §2.3) carry `relay_id`, while the attestation and the audit record
  use `attestation_id` for the same per-relay UUID.
- **ITV-94 correlation semantics (C3a observation):** Actions §3.5 Record 3 sets
  `correlation_id` to the pending_approval id; ITV-94 uses the original request
  id. The schema cannot check this.
- **CHECK-04 field list (C3a observation):** Identity CHECK-04 presents its list
  as "the fields defined in ArsiaAuditRecord", but it omits the schema-required
  `retention_source`.
- **Canonical pending_approval field set not enforced (C3a observation):** Assets
  §5.2 requires "exactly the canonical field set" of Actions §3.2, but the
  `pending-approval-args` schema does not close its properties.
- **Extension fields without RTM rows (C3a observation):** the per-event-type
  extension table has no dedicated RTM rows (A-64 domain).
- **ITV-401 pre-existing defect (C3a):** the vector also lacked `correlation_id`,
  so it was invalid for two causes. It was corrected when the vector was
  repurposed under Rule 4.

- **Findings register has no description column (C2.1):** defect descriptions live in
  the C0 audit report. For A-70 to A-73 the currency-pass text is placed under
  "Closure evidence obtained", as agreed with the owner. Adding a description column,
  and possibly moving the regulatory register to its own file, is a separate
  ledger-maintenance step.
  Resolved in LM: Description column added; the regulatory and vector registers
  moved to their own files.
- **ITV-99 `payload_type` (C3b):** `arsiaprotocol.actions/rollback` does not follow
  the Actions §4.2 `{action_id}/rollback` form (vector cycle).
- **Reversal records (C3b, A-75):** Assets §3.3.2 requires the reversal record to
  reference the original `audit_id` and `payment_reference`, but no schema
  discriminator identifies reversal records; adding one is a design choice.
- **Routing §2.3.3 (C3b, A-16):** "recipient error" among the cannot-forward causes
  is read as a failure to obtain a recipient envelope, per the A-16 disposition.
- **Stale counts outside scope (C3b):** CLAUDE.md still cites 1903 / 1109 RTM rows;
  the repository now has 1909 / 1117 (documentation outside C3b scope). Resolved in LM.
- **A-59 guard (C3b):** the guard now also compares State §7.1 base-field
  requiredness with the schema; `AUDIT_BASE_EXCEPTIONS` holds A-81.
- **Link coverage (LM):** `check_links.py` checks § references in `spec/` and the
  schema/profile JSON only; it does not read `docs/` or relative Markdown links. The
  ledger files were checked by a one-off script (tooling program).
- **Other stale CLAUDE.md figures (LM):** "91 repo invariants" and "R1-R13" are out
  of date; they are not vector or RTM totals, so LM left them. Resolved in LM2:
  CLAUDE.md states 98 repo invariants and R1-R14.
- **Propagation impact (DR-5):** implementations must emit the chain fields at
  Compliance and Full, serve chain queries in State §7.4 (`chain_id`,
  `after_chain_seq`, `next_cursor` as record_id or chain_seq), verify chains in
  CHECK-04, and pick up the new tombstone schema in the re-sync.
- **Query-response schema (DR-5):** it admits tombstones in any response; State §7.4
  allows them only in `chain_id` queries (schema more permissive than prose).
- **Published counts after DR-5:** 32 schemas (incl. meta), 679 vectors
  (438/147/94), RTM 1922 / 1130. README.md, CLAUDE.md (also "R1-R13", no R14) and
  docs are left for the maintenance step. Resolved in LM2: `README.md`, `CLAUDE.md`,
  `docs/FAQ.md` and `docs/getting-started.md` carry 32 schemas, 679 vectors
  (438/147/94) and RTM 1924 / 1132 (after the DR-5 follow-up).
- **Generated overview (LM2):** `docs/generated/arsia-protocol-overview.md` is a
  dated snapshot (commit `c4bc506`, extraction 2026-08-06) that still states 649
  vectors and RTM 1903 / 1109; it says to regenerate rather than hand-edit, so LM2
  left it (regeneration is a separate step).
- **Unchained audit-record vectors (DR-5):** older audit-record vectors carry no
  chain fields; the level mandate is enforced by harness R14 (f) and CHECK-04.
- **ITV-18/19 and post-execution review (DR-3/DR-4):** they stay structurally valid;
  accepting `required_within_24h` or `required_post_execution` in a resolution is not
  evidence that post-execution review works — that mechanism is DR-2.
- **Resolved is not fulfilled (DR-3/DR-4):** `obligation_resolution` records which
  obligations applied; fulfilment evidence comes from the flows that carry them out.
- **Resolver-contract tests (DR-3/DR-4):** ITV-609, ITV-617 and ITV-618 compose
  executor-class requirements to test the resolver's contract; they do not claim the
  executor integration, which is DR-1.
- **Removed RTM rows (DR-3/DR-4):** IDENT-§4.2-02 and -03 (warning and
  `classification_mismatch` rejection) and STATE-§6.2-04 (profile applicable only to
  high-risk agents) traced requirements that the cycle removed.
- **CHECK-05 (DR-3/DR-4):** the new check states no RFC 2119 keyword; it is traced
  through IDENT-§7.3-17 (all checks pass) and IDENT-§7.6-11, and exercised by the
  vectors carrying the authenticated context.
- **Stale CORE-§4.3.7-02/-03 (observed in DR-3/DR-4, not fixed):** the rows describe a
  retention clamp and an override warning that Core §4.3.7 forbids ("MUST NOT silently
  raise"); they predate the cycle and are left for the RTM pass (A-64 domain).
- **Stale profiles/README.md retention column (observed in DR-3/DR-4, not fixed):** it
  states day counts (e.g. 180 days for EU-AI-ACT-HIGH-RISK, 730 for DSA-VLOP) that differ
  from the catalog (P6M, P1096D); out of the cycle's scope.
- **getting-started breakdown (DR-3/DR-4):** the vector breakdown "430 / 145 / 94" missed
  by LM2 now carries the tool-computed figures.
- **Published counts after DR-3/DR-4:** 33 schemas (incl. meta), 717 vectors
  (441/157/119), RTM 1940 / 1147, 110 consistency checks; README.md, CLAUDE.md,
  docs/FAQ.md, docs/getting-started.md and test-vectors/README.md updated. The generated
  overview stays a dated snapshot.

[reg8]: draft-02-remediation-ledger-regulatory.md#8-open-notes-regulatory
