<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
# ARSIA-State — Requirements Traceability Matrix

| ID | § | Modal | Layer | Kind | Requirement | Schema | Vector |
|----|---|-------|-------|------|-------------|--------|--------|
| STATE-§1-01 | 1 | MUST | sdk | structural | Every state entry (§2) MUST declare exactly one scope. | arsia-state-entry | ITV-21, ITV-22, ITV-179 |
| STATE-§1-02 | 1 | MUST_NOT | sdk | behavioural_negative | The scope is immutable after creation — an entry's scope MUST NOT be changed. | — | ITV-179 |
| STATE-§1-03 | 1 | MUST | sdk | procedural | To move data between scopes, the agent MUST create a new entry in the target scope and delete the original | — | — |
| STATE-§1.1-01 | 1.1 | MUST_NOT | sdk | behavioural_negative | The session timeout MUST NOT exceed 24 hours. | — | — |
| STATE-§1.1-02 | 1.1 | RECOMMENDED | sdk_enabled | behavioural_positive | A session timeout of 1 hour is RECOMMENDED. | — | — |
| STATE-§1.1-03 | 1.1 | MUST | sdk | behavioural_positive | When the session ends, all session-scoped entries for that correlation chain MUST be eligible for immediate removal | — | — |
| STATE-§1.1-04 | 1.1 | SHOULD | sdk_enabled | behavioural_positive | Implementations SHOULD remove session state entries promptly after session termination | — | — |
| STATE-§1.1-05 | 1.1 | MUST_NOT | sdk_enabled | behavioural_negative | Other agents, including compliance brokers, MUST NOT access session-scoped entries. | — | ITV-180 |
| STATE-§1.1-06 | 1.1 | MUST_NOT | deployment | behavioural_negative | Session state MUST NOT be persisted to durable storage under normal operating conditions | — | — |
| STATE-§1.1-07 | 1.1 | SHOULD | deployment | behavioural_positive | Session state SHOULD be held in volatile memory (RAM, in-process cache, or equivalent) | — | — |
| STATE-§1.1-08 | 1.1 | MUST | deployment | procedural | Implementations using durable storage for session state MUST delete those entries upon session termination | — | — |
| STATE-§1.1-09 | 1.1 | MUST_NOT | deployment | behavioural_negative | Session state in durable storage MUST NOT be included in backup or replication processes | — | — |
| STATE-§1.1-10 | 1.1 | MUST_NOT | sdk | behavioural_negative | Session state entries MUST NOT generate audit events. | — | ITV-181 |
| STATE-§1.1-11 | 1.1 | MUST | sdk | behavioural_positive | Session-scoped entries MUST declare pii_classification regardless of ephemeral nature | arsia-state-entry | — |
| STATE-§1.1-12 | 1.1 | SHOULD | sdk_enabled | behavioural_positive | Agents SHOULD process personal session state in-memory without materialising to persistent media | — | — |
| STATE-§1.1-13 | 1.1 | MUST | deployment | behavioural_positive | Session state with personal data MUST NOT be captured in logs, debug dumps, or crash reports | — | — |
| STATE-§1.2-01 | 1.2 | MUST | deployment | behavioural_positive | Agent-scoped state MUST survive agent restarts, infrastructure migrations, and routine maintenance | — | — |
| STATE-§1.2-02 | 1.2 | MUST_NOT | sdk_enabled | behavioural_negative | Agents other than the one whose agent_id matches owner_agent_id MUST NOT read or write agent-scoped entries unless an explicit grant has been issued | — | STV-02, ITV-182 |
| STATE-§1.2-03 | 1.2 | MAY | sdk_enabled | behavioural_positive | Grantee agents MAY access agent-scoped entries per the grant's access_level (read or read-write) | — | ITV-182 |
| STATE-§1.2-04 | 1.2 | MUST | deployment | behavioural_positive | Agent-scoped state MUST be persisted to durable storage | — | — |
| STATE-§1.2-05 | 1.2 | MUST_NOT | sdk | behavioural_negative | Agent-scoped entries MUST NOT be physically deleted before retention expires, except via PURGE with a recorded retention override (§3.2.2) | — | ITV-183 |
| STATE-§1.2-06 | 1.2 | MUST | sdk | procedural | SET and DELETE on agent-scoped entries MUST generate audit events when audit_required is true | — | ITV-184, ITV-185 |
| STATE-§1.2-07 | 1.2 | MUST | sdk | behavioural_positive | Audit events MUST include operation type, entry key, owner_agent_id, actor, timestamp, generation, and version | arsia-audit-record | ITV-184 |
| STATE-§1.2-08 | 1.2 | MUST_NOT | sdk | behavioural_negative | Audit events MUST NOT include the entry value unless value-level auditing is required | — | ITV-185 |
| STATE-§1.2-09 | 1.2 | MUST | deployment | behavioural_positive | Agent-scoped entry storage MUST physically reside within the declared data_residency zone | arsia-state-entry | — |
| STATE-§1.3-01 | 1.3 | MUST_NOT | sdk | behavioural_negative | Agents without a grant MUST NOT access shared-scoped entries, even by key guessing | — | ITV-186 |
| STATE-§1.3-02 | 1.3 | MUST | sdk | behavioural_positive | Implementations MUST enforce access control at the operation level, not merely at key discovery | — | ITV-186, ITV-187 |
| STATE-§1.3-03 | 1.3 | MUST | deployment | behavioural_positive | Shared-scoped state MUST be persisted to durable storage with agent-scoped durability guarantees | — | — |
| STATE-§1.3-04 | 1.3 | MUST | sdk | procedural | Grant creation, modification, and revocation MUST generate audit events when audit_required is true | — | ITV-188 |
| STATE-§1.3-05 | 1.3 | MUST | sdk | behavioural_positive | Grant audit events MUST include grant ID, key pattern, grantee, access level, grantor, and timestamp | arsia-audit-record | ITV-188 |
| STATE-§1.3-06 | 1.3 | MUST | operational_policy | behavioural_positive | Art. 30 records MUST list all grantee agents as recipients when shared entries contain PII | — | — |
| STATE-§1.4-01 | 1.4 | MUST_NOT | sdk | behavioural_negative | Agents MUST NOT create, modify, or delete global-scoped entries through ARSIA State operations | arsia-state-operations | ITV-190 |
| STATE-§1.4-02 | 1.4 | MAY | sdk_enabled | behavioural_positive | All agents in the deployment MAY read global-scoped entries | — | ITV-189 |
| STATE-§1.4-03 | 1.4 | MUST_NOT | sdk_enabled | behavioural_negative | Agents MUST NOT write to global-scoped entries through ARSIA State operations. | — | ITV-190 |
| STATE-§1.4-04 | 1.4 | MUST | external | behavioural_positive | Platform operator MUST ensure global state complies with retention and data residency requirements | — | — |
| STATE-§1.4-05 | 1.4 | SHOULD_NOT | sdk_enabled | behavioural_positive | Global state SHOULD NOT contain personal data | — | — |
| STATE-§1.4-06 | 1.4 | NOT_RECOMMENDED | external | behavioural_positive | Storing personal or pseudonymised data in global state is NOT RECOMMENDED; operator bears GDPR responsibility | — | — |
| STATE-§1.4-07 | 1.4 | MUST | sdk | behavioural_positive | Global entries with personal data MUST set pii_classification to "personal" or "pseudonymised" | arsia-state-entry | — |
| STATE-§2.1.1-01 | 2.1.1 | REQUIRED | sdk | structural | StateEntry.key field is REQUIRED | arsia-state-entry | — |
| STATE-§2.1.1-02 | 2.1.1 | MUST | sdk | behavioural_positive | SET MUST be rejected when the key's agent-id prefix does not match the request's from field | arsia-state-entry | ITV-195 |
| STATE-§2.1.1-03 | 2.1.1 | MUST | sdk | behavioural_positive | The scope segment of the key MUST match the entry's scope field | arsia-state-entry, arsia-state-operations | ITV-191 |
| STATE-§2.1.1-04 | 2.1.1 | MAY | sdk_enabled | behavioural_positive | The local key MAY contain additional forward slashes to create a hierarchical structure | — | — |
| STATE-§2.1.1-05 | 2.1.1 | SHOULD | sdk_enabled | behavioural_positive | Session-scoped entry keys SHOULD include the correlation_id for uniqueness across sessions | — | — |
| STATE-§2.1.1-06 | 2.1.1 | SHOULD | external | behavioural_positive | Global-scoped entry keys SHOULD use the platform operator's agent-id as prefix | — | — |
| STATE-§2.1.1-07 | 2.1.1 | MUST_NOT | sdk | structural | Key MUST NOT exceed 512 characters (maximum length). | arsia-state-entry | ITV-523, ITV-524 |
| STATE-§2.1.2-01 | 2.1.2 | REQUIRED | sdk | structural | StateEntry.value field is REQUIRED for SET operations | arsia-state-operations | STV-01 |
| STATE-§2.1.2-02 | 2.1.2 | MUST | sdk | behavioural_negative | Implementations MUST store and return values exactly as provided, preserving JSON type fidelity | — | ITV-192, ITV-193 |
| STATE-§2.1.2-03 | 2.1.2 | MUST_NOT | sdk | behavioural_negative | A stored number like 1.0 MUST NOT be returned as 1 if the original included the decimal point | — | ITV-192, ITV-193 |
| STATE-§2.1.2-04 | 2.1.2 | MAY | sdk | behavioural_negative | Implementations MAY normalise numbers per standard JSON parsing rules | — | — |
| STATE-§2.1.2-05 | 2.1.2 | MUST | sdk | behavioural_positive | SET MUST be rejected with payload_too_large when serialised value exceeds 1 MiB | — | ITV-194 |
| STATE-§2.1.2-06 | 2.1.2 | SHOULD | deployment | behavioural_positive | Values with pii_classification "personal" or "pseudonymised" SHOULD be encrypted at rest | — | — |
| STATE-§2.1.3-01 | 2.1.3 | REQUIRED | sdk | structural | StateEntry.owner_agent_id field is REQUIRED | arsia-state-entry | ITV-195 |
| STATE-§2.1.3-02 | 2.1.3 | MUST_NOT | sdk | behavioural_negative | owner_agent_id is set at creation and MUST NOT be changed by any operation including SET | — | ITV-195 |
| STATE-§2.1.4-01 | 2.1.4 | REQUIRED | sdk | structural | StateEntry.scope field is REQUIRED | arsia-state-entry | ITV-21, ITV-22 |
| STATE-§2.1.4-02 | 2.1.4 | MUST | sdk | behavioural_positive | The scope MUST match the scope segment of the entry's key (§2.1.1). | arsia-state-entry, arsia-state-operations | STV-01, ITV-196 |
| STATE-§2.1.4-03 | 2.1.4 | MUST_NOT | sdk | behavioural_negative | The scope is immutable after creation — it MUST NOT be changed by any operation. | — | ITV-196 |
| STATE-§2.1.5-01 | 2.1.5 | REQUIRED | sdk | structural | StateEntry.created_at field is REQUIRED (RFC 3339, millisecond precision, UTC) | arsia-state-entry | — |
| STATE-§2.1.6-01 | 2.1.6 | REQUIRED | sdk | structural | StateEntry.updated_at field is REQUIRED (RFC 3339, millisecond precision, UTC) | arsia-state-entry | — |
| STATE-§2.1.7-01 | 2.1.7 | OPTIONAL | sdk_enabled | behavioural_positive | StateEntry.expires_at field is OPTIONAL (RFC 3339 expiry timestamp) | arsia-state-entry | — |
| STATE-§2.1.7-02 | 2.1.7 | MAY | sdk_enabled | behavioural_positive | Expired entries MAY be garbage-collected after expires_at, subject to retention rules | — | — |
| STATE-§2.1.7-03 | 2.1.7 | MUST_NOT | sdk | behavioural_negative | Entries MUST NOT be removed until both expires_at has passed AND retention period has elapsed | — | ITV-197 |
| STATE-§2.1.7-04 | 2.1.7 | SHOULD | sdk_enabled | behavioural_positive | Session entries' expires_at SHOULD match the request's expires_at or session timeout (earlier wins) | — | ITV-198 |
| STATE-§2.1.7-05 | 2.1.7 | MUST_NOT | sdk | behavioural_negative | Expired entries MUST NOT be returned by GET or QUERY operations. | — | ITV-199 |
| STATE-§2.1.7-06 | 2.1.7 | MAY | sdk_enabled | behavioural_positive | SNAPSHOT MAY return expired entries if they existed at the requested time and retention has not elapsed | — | — |
| STATE-§2.1.8-01 | 2.1.8 | OPTIONAL | sdk_enabled | behavioural_positive | StateEntry.retention field is OPTIONAL (integer, minimum 1) | arsia-state-entry | ITV-138 |
| STATE-§2.1.8-02 | 2.1.8 | MUST_NOT | sdk | behavioural_negative | The effective retention MUST NOT be less than the compliance profile's minimum. | arsia-state-entry | INV-08 |
| STATE-§2.1.8-03 | 2.1.8 | MUST_NOT | sdk | behavioural_negative | Entry-level retention MUST NOT reduce retention below the compliance profile minimum | — | INV-08 |
| STATE-§2.1.8-04 | 2.1.8 | MUST_NOT | sdk | behavioural_negative | Entries within retention MUST NOT be physically deleted, except via PURGE with a recorded retention override (§3.2.2) | — | ITV-200 |
| STATE-§2.1.9-01 | 2.1.9 | OPTIONAL | sdk_enabled | behavioural_positive | StateEntry.data_residency field is OPTIONAL (ISO 3166-1 or supranational code) | arsia-state-entry | ITV-138 |
| STATE-§2.1.9-02 | 2.1.9 | MUST | deployment | behavioural_positive | data_residency declares the geographic zone where the entry MUST be stored | arsia-state-entry | — |
| STATE-§2.1.9-03 | 2.1.9 | MUST | deployment | behavioural_positive | Storage backend MUST physically reside within the declared data_residency zone | — | — |
| STATE-§2.1.10-01 | 2.1.10 | REQUIRED | sdk | structural | StateEntry.pii_classification field is REQUIRED (none, pseudonymised, personal, or sensitive) | arsia-state-entry | — |
| STATE-§2.1.10-02 | 2.1.10 | SHOULD | sdk_enabled | behavioural_positive | pii_classification "none" SHOULD be used for all non-personal data | — | — |
| STATE-§2.1.10-03 | 2.1.10 | MUST | sdk | behavioural_positive | Pseudonymised entries MUST still comply with data residency requirements and retention policies | — | — |
| STATE-§2.1.10-04 | 2.1.10 | SHOULD | deployment | behavioural_positive | Implementations SHOULD encrypt pseudonymised data at rest. | — | — |
| STATE-§2.1.10-05 | 2.1.10 | MUST | sdk | behavioural_positive | compliance.legal_basis MUST be set in the envelope creating or updating personal entries | arsia-compliance-field, arsia-message | ITV-201 |
| STATE-§2.1.10-06 | 2.1.10 | MUST | sdk | behavioural_positive | SET operations for "personal" entries without a legal basis MUST be rejected. | — | ITV-201 |
| STATE-§2.1.10-07 | 2.1.10 | MUST | sdk | behavioural_positive | Personal entries MUST have data_residency set (entry-level or inherited from compliance profile) | arsia-state-entry, arsia-state-operations | ITV-202 |
| STATE-§2.1.10-08 | 2.1.10 | SHOULD | sdk_enabled | behavioural_positive | Implementations SHOULD warn when personal data lacks an explicit data residency constraint | — | — |
| STATE-§2.1.10-09 | 2.1.10 | MUST | operational_policy | behavioural_positive | Personal entries MUST be included in GDPR Art. 30 records of processing activities | — | — |
| STATE-§2.1.10-10 | 2.1.10 | MUST | deployment | behavioural_positive | Implementations MUST encrypt personal data at rest (§10.4). | — | — |
| STATE-§2.1.10-11 | 2.1.10 | MUST | sdk | behavioural_positive | Changing pii_classification requires a new SET creating a new version with the updated value | — | ITV-203 |
| STATE-§2.1.10-12 | 2.1.10 | MUST | sdk | behavioural_negative | "sensitive" entries: legal_basis MUST be an Art. 9(2) ground (Core §4.3.8, Rule 8) | arsia-compliance-field | ITV-555, INV-20 |
| STATE-§2.1.10-13 | 2.1.10 | MUST | sdk | structural | "sensitive" entries: pii_special_categories MUST be present with at least one value | arsia-state-entry, arsia-state-operations | INV-21 |
| STATE-§2.1.10-14 | 2.1.10 | MUST | deployment | behavioural_positive | "sensitive" entries: implementations MUST encrypt data at rest | — | — |
| STATE-§2.1.10-15 | 2.1.10 | SHOULD | deployment | behavioural_positive | "sensitive" entries: implementations SHOULD restrict read access to authorized agents for the specific category | — | — |
| STATE-§2.1.11-01 | 2.1.11 | REQUIRED | sdk | structural | pii_special_categories is REQUIRED when pii_classification is "sensitive" | arsia-state-entry, arsia-state-operations | INV-21 |
| STATE-§2.1.11-02 | 2.1.11 | MUST_NOT | sdk | behavioural_negative | pii_special_categories MUST NOT be present when pii_classification is not "sensitive" | — | INV-22 |
| STATE-§2.1.11-03 | 2.1.11 | MUST | sdk | structural | pii_special_categories MUST contain at least one value from the GDPR Art. 9(1) enum | arsia-state-entry | — |
| STATE-§2.1.12-01 | 2.1.12 | MUST | sdk | behavioural_positive | SET with expected_version MUST verify current version matches before applying the update | arsia-state-operations | — |
| STATE-§2.1.12-02 | 2.1.12 | MUST | sdk | behavioural_positive | SET MUST fail with error code "conflict" when expected_version does not match current version | arsia-message | ITV-82 |
| STATE-§2.1.12-03 | 2.1.12 | MUST_NOT | sdk | behavioural_negative | Entry version number is monotonically increasing and MUST NOT be reset or decremented within an entry's lifetime | arsia-state-entry | — |
| STATE-§2.1.12-04 | 2.1.12 | MUST | sdk | behavioural_positive | Recreated entries are a new generation starting at version 1; prior version history retained for SNAPSHOT | — | ITV-204, ITV-681 |
| STATE-§2.1.13-01 | 2.1.13 | MAY | sdk_enabled | behavioural_positive | Logically deleted entries MAY appear in SNAPSHOT results for times when they were active | — | ITV-206 |
| STATE-§2.1.13-02 | 2.1.13 | MUST_NOT | sdk | behavioural_negative | The deleted flag MUST NOT be set directly by agents; only the implementation sets it on DELETE | arsia-state-entry | STV-03 |
| STATE-§2.1.13-03 | 2.1.13 | MAY | sdk_enabled | behavioural_positive | After the retention period expires, the implementation MAY physically remove the entry | — | — |
| STATE-§2.1.13-04 | 2.1.13 | OPTIONAL | sdk_enabled | behavioural_positive | StateEntry.deleted field is OPTIONAL in representations returned to agents | arsia-state-entry | ITV-138, ITV-205 |
| STATE-§2.1.13-05 | 2.1.13 | SHOULD | sdk_enabled | behavioural_positive | Implementations SHOULD omit the deleted field from GET and QUERY responses | — | ITV-205 |
| STATE-§2.1.13-06 | 2.1.13 | REQUIRED | sdk | behavioural_positive | The deleted field is REQUIRED in SNAPSHOT responses for entries deleted at the queried time | — | ITV-206 |
| STATE-§2.1.14-01 | 2.1.14 | REQUIRED | sdk | structural | StateEntry.generation is REQUIRED (integer ≥ 1, implementation-set) | arsia-state-entry | INV-81, INV-82 |
| STATE-§2.1.14-02 | 2.1.14 | MUST_NOT | sdk | behavioural_negative | While any information of the key is held, a generation number already assigned under the key MUST NOT be assigned to a new entry, also after a PURGE or a partial removal | — | ITV-680, ITV-681 |
| STATE-§2.1.14-03 | 2.1.14 | MUST | sdk | behavioural_positive | The implementation MUST keep the highest generation assigned under a key for as long as it holds any information of the key (evidence: R17 (h)) | — | ITV-680 |
| STATE-§2.2-01 | 2.2 | RECOMMENDED | sdk_enabled | behavioural_positive | Naming conventions for the local-key segment of state entry keys are RECOMMENDED | — | — |
| STATE-§2.2-02 | 2.2 | MAY | sdk_enabled | structural | Agents MAY use any key format conforming to the §2.1.1 pattern; naming conventions are non-normative | arsia-state-entry | — |
| STATE-§2.2-03 | 2.2 | RECOMMENDED | sdk_enabled | behavioural_positive | Lowercase-with-hyphens key naming (e.g., client-preferences) is RECOMMENDED | — | — |
| STATE-§2.2-04 | 2.2 | NOT_RECOMMENDED | sdk_enabled | behavioural_positive | camelCase and underscore key naming (e.g., clientPreferences, client_preferences) is NOT RECOMMENDED | — | — |
| STATE-§2.2-05 | 2.2 | RECOMMENDED | sdk_enabled | behavioural_positive | Descriptive, self-documenting key names (e.g., risk-assessment-2026Q1) are RECOMMENDED | — | — |
| STATE-§2.2-06 | 2.2 | NOT_RECOMMENDED | sdk_enabled | behavioural_positive | Abbreviated or opaque key names (e.g., ra1) are NOT RECOMMENDED | — | — |
| STATE-§2.2-07 | 2.2 | MUST_NOT | sdk | behavioural_negative | Agents MUST NOT create entries with local keys starting with the reserved arsiaprotocol. prefix | arsia-state-operations | ITV-207, ITV-208 |
| STATE-§2.2-08 | 2.2 | MUST | sdk | behavioural_positive | SET operations to keys with the arsiaprotocol. prefix MUST be rejected with "forbidden" | arsia-state-operations | ITV-207, ITV-208 |
| STATE-§2.3-01 | 2.3 | MUST | sdk | behavioural_positive | StateEntry.value MUST be a valid JSON value per RFC 8259 | — | ITV-209, ITV-210 |
| STATE-§2.3-02 | 2.3 | MUST | sdk | behavioural_positive | Binary data MUST be base64-encoded before storage. | — | — |
| STATE-§2.3-03 | 2.3 | MUST_NOT | sdk | behavioural_negative | Implementations MUST NOT accept non-JSON values. | — | ITV-210 |
| STATE-§2.3-04 | 2.3 | MUST_NOT | sdk | behavioural_negative | Serialised JSON value MUST NOT exceed 1,048,576 bytes (1 MiB) | — | ITV-211 |
| STATE-§2.3-05 | 2.3 | SHOULD | sdk_enabled | behavioural_positive | Data exceeding the size limit SHOULD use the reference pattern (store externally, keep reference) | — | — |
| STATE-§2.3-06 | 2.3 | MUST_NOT | sdk | behavioural_negative | Values MUST NOT contain executable code intended for evaluation by receiving agents | — | — |
| STATE-§2.3-07 | 2.3 | MUST | sdk | behavioural_positive | All string values within the JSON MUST be valid UTF-8 | — | ITV-212, ITV-213 |
| STATE-§2.3-08 | 2.3 | MUST | sdk | behavioural_positive | Implementations MUST reject values containing invalid UTF-8 sequences. | — | ITV-212, ITV-213 |
| STATE-§2.4-01 | 2.4 | OPTIONAL | sdk_enabled | behavioural_positive | Both expected_version and expected_generation are OPTIONAL; when neither is supplied, SET is unconditional | arsia-state-operations | ITV-112, ITV-676 |
| STATE-§2.4-02 | 2.4 | MUST | sdk | behavioural_positive | SNAPSHOT-supporting implementations MUST retain version history for the effective retention period | — | ITV-214 |
| STATE-§2.4-03 | 2.4 | MUST | sdk | behavioural_positive | Each version MUST be associated with generation, version number, value, updated_at timestamp, and actor agent | — | ITV-214, ITV-677 |
| STATE-§3.1.1-01 | 3.1.1 | MUST | sdk | behavioural_positive | GET payload.args.key MUST be the full namespaced key of the entry to retrieve | arsia-state-operations | STV-02, ITV-172, ITV-180 |
| STATE-§3.1.1-02 | 3.1.1 | MUST | sdk | behavioural_positive | GET requests MUST carry the arsiaprotocol.state.read capability in the access token | — | STV-02 |
| STATE-§3.1.1-03 | 3.1.1 | MUST | sdk | behavioural_positive | GET requests MUST come from the entry owner or an agent with a matching active grant | — | STV-02 |
| STATE-§3.1.1-04 | 3.1.1 | MUST | sdk | behavioural_positive | Session-scoped GET MUST come from one of the two agents in the session (from or to) | — | ITV-215 |
| STATE-§3.1.1-05 | 3.1.1 | MUST | sdk | behavioural_positive | Denied GET requests MUST return error code "forbidden" | arsia-message | — |
| STATE-§3.1.1-06 | 3.1.1 | MAY | sdk_enabled | behavioural_positive | Implementations MAY generate GET audit events if the profile requires read-level auditing | — | — |
| STATE-§3.1.2-01 | 3.1.2 | REQUIRED | sdk | structural | SET payload.args.key field is REQUIRED | arsia-state-operations | ITV-47 |
| STATE-§3.1.2-02 | 3.1.2 | REQUIRED | sdk | structural | SET payload.args.value field is REQUIRED | arsia-state-operations | ITV-47 |
| STATE-§3.1.2-03 | 3.1.2 | REQUIRED | sdk | structural | SET payload.args.scope field is REQUIRED | arsia-state-operations | ITV-47, ITV-48, ITV-110, ITV-111 |
| STATE-§3.1.2-04 | 3.1.2 | REQUIRED | sdk | structural | SET payload.args.pii_classification field is REQUIRED | arsia-state-operations | ITV-47, ITV-108, ITV-109 |
| STATE-§3.1.2-05 | 3.1.2 | OPTIONAL | sdk_enabled | behavioural_positive | SET payload.args.expires_at field is OPTIONAL | arsia-state-operations | ITV-112 |
| STATE-§3.1.2-06 | 3.1.2 | OPTIONAL | sdk_enabled | behavioural_positive | SET payload.args.retention field is OPTIONAL | arsia-state-operations | ITV-112 |
| STATE-§3.1.2-07 | 3.1.2 | OPTIONAL | sdk_enabled | behavioural_positive | SET payload.args.data_residency field is OPTIONAL | arsia-state-operations | ITV-112 |
| STATE-§3.1.2-08 | 3.1.2 | OPTIONAL | sdk_enabled | behavioural_positive | SET payload.args.expected_version field is OPTIONAL | arsia-state-operations | ITV-112 |
| STATE-§3.1.2-09 | 3.1.2 | MUST_NOT | sdk | behavioural_negative | SET scope MUST NOT be "global"; agents cannot create global-scoped entries via SET | arsia-state-operations | ITV-49, ITV-216 |
| STATE-§3.1.2-10 | 3.1.2 | MUST | sdk | behavioural_positive | SET with scope "global" MUST return error code "forbidden" | — | ITV-216 |
| STATE-§3.1.2-11 | 3.1.2 | MUST | sdk | behavioural_positive | The agent-id prefix of the key MUST match the from field of the request message. | — | STV-01 |
| STATE-§3.1.2-12 | 3.1.2 | MUST | sdk | behavioural_positive | The scope segment of the key MUST match the scope field in payload.args. | arsia-state-operations | STV-01, ITV-219 |
| STATE-§3.1.2-13 | 3.1.2 | MUST | sdk | behavioural_positive | SET for personal entries MUST include legal_basis in the compliance envelope | arsia-compliance-field | ITV-217 |
| STATE-§3.1.2-14 | 3.1.2 | MUST | sdk | behavioural_positive | SET without legal_basis for personal entries MUST be rejected with "invalid_request" | — | ITV-201 |
| STATE-§3.1.2-15 | 3.1.2 | MUST | sdk | behavioural_positive | SET MUST fail with "conflict" when a precondition mismatches the live entry, returning the current generation and version and the stated preconditions | arsia-message | ITV-678 |
| STATE-§3.1.2-16 | 3.1.2 | MUST | sdk | behavioural_positive | SET MUST be rejected with "invalid_request" when the declared data_residency zone is unavailable | arsia-message | — |
| STATE-§3.1.2-17 | 3.1.2 | MUST | sdk | behavioural_positive | SET MUST be rejected with "payload_too_large" when value exceeds 1,048,576 bytes | — | ITV-218 |
| STATE-§3.1.2-18 | 3.1.2 | MUST | sdk | behavioural_positive | SET MUST be rejected with "invalid_request" when scope mismatches an existing entry's scope | — | ITV-219 |
| STATE-§3.1.2-19 | 3.1.2 | MUST | sdk | procedural | SET MUST generate a "state_set" audit event when audit_required is true | arsia-audit-record | ITV-220, ITV-527 |
| STATE-§3.1.2-20 | 3.1.2 | MUST_NOT | sdk | behavioural_negative | SET audit events MUST NOT include the entry value unless value-level auditing is required | arsia-audit-record | ITV-221 |
| STATE-§3.1.2-21 | 3.1.2 | NOT_RECOMMENDED | sdk | behavioural_positive | Value-level auditing of personal or pseudonymised entries is NOT RECOMMENDED | — | — |
| STATE-§3.1.2-22 | 3.1.2 | OPTIONAL | sdk_enabled | behavioural_positive | SET payload.args.expected_generation field is OPTIONAL | arsia-state-operations | ITV-676, INV-83 |
| STATE-§3.1.2-23 | 3.1.2 | MUST | sdk | behavioural_positive | Preconditions are evaluated against the live entry in one atomic check; when both are set, both MUST hold | — | ITV-678 |
| STATE-§3.1.2-24 | 3.1.2 | MUST | sdk | behavioural_positive | A conditional SET on a key without a live entry MUST be rejected with conflict and entry_live false | arsia-message | ITV-679 |
| STATE-§3.1.2-25 | 3.1.2 | MUST_NOT | sdk | behavioural_negative | A conditional SET on a key without a live entry MUST NOT create an entry | — | ITV-679 |
| STATE-§3.1.2-26 | 3.1.2 | MUST_NOT | sdk | behavioural_negative | Absent-entry conflict details MUST NOT distinguish a deleted key from a key never written | — | ITV-679 |
| STATE-§3.1.3-01 | 3.1.3 | MUST | sdk | behavioural_positive | The requesting agent MUST be the owning agent of the entry. | — | STV-03, ITV-173 |
| STATE-§3.1.3-02 | 3.1.3 | MUST_NOT | sdk | behavioural_negative | Grantees with read_write access MUST NOT DELETE entries; DELETE is owner-only | — | STV-03 |
| STATE-§3.1.3-03 | 3.1.3 | MUST | sdk | behavioural_positive | DELETE by a non-owner MUST return error code "forbidden" | arsia-message | — |
| STATE-§3.1.3-04 | 3.1.3 | SHOULD | sdk_enabled | behavioural_positive | Implementations SHOULD distinguish logical deletion (hidden) from physical removal eligibility | — | ITV-222 |
| STATE-§3.1.3-05 | 3.1.3 | MUST_NOT | sdk | behavioural_negative | Logically deleted entry data MUST NOT be physically removed until retention expires | — | ITV-222 |
| STATE-§3.1.3-06 | 3.1.3 | MAY | sdk_enabled | behavioural_positive | Past-retention deleted entries MAY be physically removed immediately | — | — |
| STATE-§3.1.3-07 | 3.1.3 | MUST | sdk | procedural | DELETE MUST generate a "state_delete" audit event when audit_required is true | arsia-audit-record | ITV-97, ITV-223, ITV-528 |
| STATE-§3.1.4-01 | 3.1.4 | OPTIONAL | sdk_enabled | behavioural_positive | QUERY payload.args.scope filter is OPTIONAL | arsia-state-operations | ITV-50, ITV-116, ITV-117 |
| STATE-§3.1.4-02 | 3.1.4 | OPTIONAL | sdk_enabled | behavioural_positive | QUERY payload.args.owner_agent_id filter is OPTIONAL | arsia-state-operations | ITV-115 |
| STATE-§3.1.4-03 | 3.1.4 | OPTIONAL | sdk_enabled | behavioural_positive | QUERY payload.args.key_prefix filter is OPTIONAL | arsia-state-operations | ITV-115 |
| STATE-§3.1.4-04 | 3.1.4 | OPTIONAL | sdk_enabled | behavioural_positive | QUERY payload.args.pii_classification filter is OPTIONAL | arsia-state-operations | ITV-115 |
| STATE-§3.1.4-05 | 3.1.4 | OPTIONAL | sdk_enabled | behavioural_positive | QUERY payload.args.created_after filter is OPTIONAL | arsia-state-operations | ITV-115 |
| STATE-§3.1.4-06 | 3.1.4 | OPTIONAL | sdk_enabled | behavioural_positive | QUERY payload.args.created_before filter is OPTIONAL | arsia-state-operations | ITV-115 |
| STATE-§3.1.4-07 | 3.1.4 | OPTIONAL | sdk_enabled | behavioural_positive | QUERY payload.args.limit is OPTIONAL (default 100, maximum 1000) | arsia-state-operations | — |
| STATE-§3.1.4-08 | 3.1.4 | OPTIONAL | sdk_enabled | behavioural_positive | QUERY payload.args.offset is OPTIONAL (default 0) | arsia-state-operations | — |
| STATE-§3.1.4-09 | 3.1.4 | MUST_NOT | sdk | behavioural_negative | QUERY MUST NOT return entries the requesting agent is not authorised to access | — | ITV-224 |
| STATE-§3.1.4-10 | 3.1.4 | MUST | sdk | behavioural_positive | QUERY for another agent's entries without a grant MUST return empty results, not an error | — | ITV-225 |
| STATE-§3.1.4-11 | 3.1.4 | MUST | sdk | behavioural_positive | Results MUST be ordered by created_at in ascending order (oldest first). | — | ITV-226 |
| STATE-§3.1.4-12 | 3.1.4 | MAY | sdk_enabled | behavioural_positive | Implementations MAY support additional ordering options in future versions | — | — |
| STATE-§3.1.4-13 | 3.1.4 | SHOULD | sdk_enabled | behavioural_positive | Implementations SHOULD optimise QUERY for prefix-based key lookups | — | — |
| STATE-§3.1.4-14 | 3.1.4 | SHOULD | sdk_enabled | behavioural_positive | The key_prefix filter SHOULD be indexed as the most frequently used QUERY filter | — | — |
| STATE-§3.1.4-15 | 3.1.4 | MUST | sdk | behavioural_positive | Implementations MUST enforce the maximum limit of 1000 entries per query. | — | ITV-227 |
| STATE-§3.1.4-16 | 3.1.4 | MUST | sdk | behavioural_positive | Requests with limit exceeding 1000 MUST be clamped to 1000 — not rejected. | — | ITV-227, ITV-228 |
| STATE-§3.2.1-01 | 3.2.1 | REQUIRED | sdk | structural | SNAPSHOT payload.args.as_of field is REQUIRED (RFC 3339 timestamp) | arsia-state-operations | ITV-174 |
| STATE-§3.2.1-02 | 3.2.1 | OPTIONAL | sdk_enabled | behavioural_positive | SNAPSHOT payload.args.filter field is OPTIONAL (same filters as QUERY) | arsia-state-operations | — |
| STATE-§3.2.1-03 | 3.2.1 | MUST | sdk | behavioural_positive | SNAPSHOT MUST return entries as they existed at the as_of timestamp, including deleted entries | — | STV-05, ITV-286, ITV-287 |
| STATE-§3.2.1-04 | 3.2.1 | MUST | sdk | behavioural_positive | SNAPSHOT MUST be supported when any active compliance profile sets audit_required to true | — | STV-05 |
| STATE-§3.2.1-05 | 3.2.1 | MUST | deployment | behavioural_positive | Temporal storage MUST retain version history for each entry's effective retention period | — | — |
| STATE-§3.2.1-06 | 3.2.1 | MAY | sdk_enabled | behavioural_positive | After the retention period expires, historical versions MAY be purged from the temporal store | — | — |
| STATE-§3.2.1-07 | 3.2.1 | MUST | sdk | behavioural_positive | Non-SNAPSHOT implementations MUST return "not_implemented" with feature "temporal_storage" | arsia-message | — |
| STATE-§3.2.1-08 | 3.2.1 | MUST_NOT | sdk | behavioural_negative | SNAPSHOT as_of MUST NOT be in the future (beyond the Core §8.3 tolerance (±300 s default, or the profile's clock_skew_seconds)) | — | ITV-229, ITV-230 |
| STATE-§3.2.1-09 | 3.2.1 | MUST | sdk | behavioural_positive | Requests with a future as_of MUST be rejected with error code "invalid_request". | — | ITV-229, ITV-230 |
| STATE-§3.2.1-10 | 3.2.1 | MUST_NOT | sdk | behavioural_negative | SNAPSHOT as_of MUST NOT predate the oldest retained version in the temporal store | — | ITV-231, ITV-232 |
| STATE-§3.2.1-11 | 3.2.1 | MUST | sdk | behavioural_positive | SNAPSHOT MUST return "invalid_request" with snapshot_unavailable when as_of predates history | — | ITV-231, ITV-232 |
| STATE-§3.2.1-12 | 3.2.1 | MUST_NOT | sdk | behavioural_negative | arsiaprotocol.state.snapshot MUST NOT be included in wildcard capability grants | — | STV-05 |
| STATE-§3.2.1-13 | 3.2.1 | SHOULD | sdk_enabled | behavioural_positive | SNAPSHOT operations SHOULD generate audit events when audit_required is true. | — | — |
| STATE-§3.2.2-01 | 3.2.2 | MUST | sdk | procedural | PURGE MUST remove the entry value and its version history, revoke any active grants, and generate an audit record | arsia-state-operations | STV-04, ITV-175 |
| STATE-§3.2.2-02 | 3.2.2 | MUST_NOT | sdk | behavioural_negative | PURGE audit event MUST NOT contain the purged entry value | arsia-audit-record | ITV-233, ITV-237 |
| STATE-§3.2.2-03 | 3.2.2 | MUST | sdk | behavioural_positive | After PURGE, SNAPSHOT queries for the key MUST return null for the value at any time | — | ITV-234 |
| STATE-§3.2.2-04 | 3.2.2 | SHOULD | deployment | behavioural_positive | Replicas SHOULD complete the purge within 24 hours. | — | — |
| STATE-§3.2.2-05 | 3.2.2 | SHOULD | deployment | behavioural_positive | Full purge propagation, including backup media rotation, SHOULD complete within 30 days | — | — |
| STATE-§3.2.2-06 | 3.2.2 | MUST | sdk | behavioural_positive | Active grants on purged entries MUST be automatically revoked during the PURGE operation | — | ITV-235 |
| STATE-§3.2.2-07 | 3.2.2 | MUST | sdk | behavioural_positive | Grant revocation audit events MUST be generated for each revoked grant. | arsia-audit-record | ITV-236 |
| STATE-§3.2.2-08 | 3.2.2 | MUST | sdk | procedural | PURGE MUST always generate an audit event, regardless of audit_required setting | arsia-audit-record | STV-04, ITV-103, ITV-233, ITV-529, ITV-683, ITV-684, ITV-686, ITV-687 |
| STATE-§3.2.2-09 | 3.2.2 | OPTIONAL | sdk_enabled | behavioural_positive | PURGE audit event reason field is OPTIONAL (e.g., "gdpr_erasure", "data_subject_request") | arsia-audit-record | STV-04 |
| STATE-§3.2.2-10 | 3.2.2 | MUST_NOT | sdk | behavioural_negative | PURGE audit event MUST NOT contain the purged value (erasure would be defeated) | arsia-audit-record | ITV-237 |
| STATE-§3.2.2-11 | 3.2.2 | MUST_NOT | sdk | behavioural_negative | arsiaprotocol.state.purge MUST NOT be included in wildcard capability grants | — | ITV-238, ITV-285 |
| STATE-§3.2.2-12 | 3.2.2 | MUST | sdk | behavioural_positive | arsiaprotocol.state.purge MUST be explicitly granted in the access token scope | — | STV-04, ITV-238, ITV-284 |
| STATE-§3.2.2-13 | 3.2.2 | MUST | sdk | behavioural_positive | Repeated PURGE with no later write MUST return success with the original purged_at timestamp | arsia-state-operations | ITV-239, ITV-680 |
| STATE-§3.2.2-14 | 3.2.2 | MUST_NOT | sdk | behavioural_negative | A repeated PURGE with no later write MUST NOT generate a second audit event. | — | ITV-239, ITV-680 |
| STATE-§3.2.2-15 | 3.2.2 | MUST | sdk | behavioural_positive | A PURGE after a later write MUST execute the procedure and generate a new audit event | arsia-audit-record | ITV-680 |
| STATE-§3.2.2-16 | 3.2.2 | MUST | sdk | procedural | The implementation MUST determine from stored state the generations whose values PURGE removes and entry_retained_until (latest instant), with or without a live entry | — | ITV-683, ITV-686, ITV-687 |
| STATE-§3.2.2-17 | 3.2.2 | MUST_NOT | sdk | behavioural_negative | Within-retention status and retention instants MUST NOT be taken from the PURGE request | arsia-state-operations | INV-99 |
| STATE-§3.2.2-18 | 3.2.2 | MUST | sdk | behavioural_positive | A PURGE within retention MUST carry retention_override (reason, determination_ref) | arsia-state-operations | ITV-682, INV-95, INV-96 |
| STATE-§3.2.2-19 | 3.2.2 | MUST | sdk | behavioural_negative | Without retention_override, a PURGE within retention MUST be rejected with invalid_request and {within_retention, entry_retained_until}, removing nothing | arsia-message | ITV-685, INV-97, INV-98 |
| STATE-§3.2.2-20 | 3.2.2 | MUST | sdk | behavioural_positive | The state_purge audit event MUST record within_retention, entry_retained_until and, when carried, retention_override | arsia-audit-record | ITV-683, ITV-684, INV-92, INV-93, INV-94, INV-100 |
| STATE-§3.2.2-21 | 3.2.2 | MUST | operational_policy | behavioural_positive | The operator MUST keep the determination referenced by determination_ref retrievable while the state_purge record is retained | — | — |
| STATE-§3.3.1-01 | 3.3.1 | REQUIRED | sdk | structural | GRANT payload.args.key_pattern field is REQUIRED | arsia-state-operations | ITV-51 |
| STATE-§3.3.1-02 | 3.3.1 | REQUIRED | sdk | structural | GRANT payload.args.grantee_agent_id field is REQUIRED | arsia-state-operations | ITV-51 |
| STATE-§3.3.1-03 | 3.3.1 | REQUIRED | sdk | structural | GRANT payload.args.access_level field is REQUIRED ("read" or "read_write") | arsia-state-operations | ITV-51, ITV-52, ITV-113 |
| STATE-§3.3.1-04 | 3.3.1 | OPTIONAL | sdk_enabled | behavioural_positive | GRANT payload.args.valid_until field is OPTIONAL (RFC 3339 expiry or null) | arsia-state-operations | ITV-114 |
| STATE-§3.3.1-05 | 3.3.1 | MUST | sdk | behavioural_positive | The pattern MUST start with the granting agent's agent-id prefix. | — | ITV-240 |
| STATE-§3.3.1-06 | 3.3.1 | MUST_NOT | sdk | behavioural_negative | An agent MUST NOT grant access to keys it does not own. | — | ITV-240, ITV-241 |
| STATE-§3.3.1-07 | 3.3.1 | MUST | sdk | behavioural_positive | GRANT MUST be rejected when the key pattern prefix does not match the request's from field | — | ITV-241, ITV-242 |
| STATE-§3.3.1-08 | 3.3.1 | MUST | sdk | behavioural_positive | State operations on non-owned entries MUST verify an active, matching, unexpired grant exists | — | ITV-243 |
| STATE-§3.3.1-09 | 3.3.1 | MUST | sdk | procedural | GRANT MUST generate a "state_grant" audit event when audit_required is true | arsia-audit-record | ITV-98, ITV-244, ITV-530 |
| STATE-§3.3.2-01 | 3.3.2 | MUST | sdk | behavioural_positive | In-flight operations arriving after a REVOKE MUST be rejected | — | ITV-245 |
| STATE-§3.3.2-02 | 3.3.2 | MUST | sdk | behavioural_positive | REVOKE of a non-existent or already-revoked grant MUST return success (idempotent) | arsia-state-operations | ITV-106, ITV-246 |
| STATE-§3.3.2-03 | 3.3.2 | MUST_NOT | sdk | behavioural_negative | Repeated REVOKE on the same grant MUST NOT generate a second audit event | — | ITV-246 |
| STATE-§3.3.2-04 | 3.3.2 | MUST_NOT | sdk_enabled | behavioural_negative | An agent other than the grantor agent MUST NOT revoke a grant | — | ITV-247 |
| STATE-§3.3.2-05 | 3.3.2 | MUST | sdk | behavioural_positive | REVOKE request's from field MUST match the original grantor of the grant | — | ITV-247, ITV-248 |
| STATE-§3.3.2-06 | 3.3.2 | MUST | sdk | behavioural_positive | REVOKE by a non-grantor MUST return error code "forbidden" | arsia-message | ITV-248 |
| STATE-§3.3.2-07 | 3.3.2 | MUST | sdk | procedural | REVOKE MUST generate a "state_revoke" audit event when audit_required is true | arsia-audit-record | ITV-104, ITV-249, ITV-531 |
| STATE-§3.3.2-08 | 3.3.2 | REQUIRED | sdk | structural | REVOKE payload.args.grant_id field is REQUIRED | arsia-state-operations | ITV-107 |
| STATE-§4.1-01 | 4.1 | MUST | sdk | behavioural_positive | Retention policy governs how long state entries MUST be kept before physical removal | — | — |
| STATE-§4.1.1-01 | 4.1.1 | MUST_NOT | sdk | behavioural_negative | Entries MUST NOT be physically deleted before the profile retention minimum expires, except via PURGE with a recorded retention override (§3.2.2) | — | ITV-250 |
| STATE-§4.1.1-02 | 4.1.1 | MUST_NOT | sdk | behavioural_negative | Entry-level retention MUST NOT reduce retention below the profile retention minimum | — | ITV-251 |
| STATE-§4.1.2-01 | 4.1.2 | RECOMMENDED | sdk_enabled | behavioural_positive | GDPR-STANDARD profile RECOMMENDED default retention is 90 days when no expires_at is set | — | — |
| STATE-§4.1.2-02 | 4.1.2 | MUST_NOT | sdk | behavioural_negative | EU-AI-ACT-HIGH-RISK entries MUST NOT be physically removed before created_at + P6M (six calendar months) | arsia-compliance-field | — |
| STATE-§4.1.2-03 | 4.1.2 | MUST_NOT | sdk | behavioural_negative | MIFID-II entries MUST NOT be physically removed before 1827 days from creation (profile floor) | arsia-compliance-field | — |
| STATE-§4.1.2-04 | 4.1.2 | MUST_NOT | sdk | behavioural_negative | PAC-AGRICULTURE entries MUST NOT be physically removed before 1096 days (3 years) from creation | arsia-compliance-field | ITV-252 |
| STATE-§4.1.2-05 | 4.1.2 | MUST_NOT | sdk | behavioural_negative | DSA-VLOP entries MUST NOT be physically removed before created_at + P1096D | arsia-compliance-field | — |
| STATE-§4.1.2-06 | 4.1.2 | MUST_NOT | sdk | behavioural_negative | DORA entries MUST NOT be physically removed before 1827 days from creation (conservative policy floor) | arsia-compliance-field | — |
| STATE-§4.1.3-01 | 4.1.3 | MAY | sdk_enabled | behavioural_positive | Post-retention entries MAY be handled by archival (cold storage) or permanent deletion | — | — |
| STATE-§4.1.3-02 | 4.1.3 | MUST | deployment | behavioural_positive | Archived entries MUST remain SNAPSHOT-accessible for 12 months after archival | — | — |
| STATE-§4.1.3-03 | 4.1.3 | MAY | sdk_enabled | behavioural_positive | After the 12-month archival period, the entry MAY be permanently deleted. | — | — |
| STATE-§4.1.3-04 | 4.1.3 | MUST | operational_policy | behavioural_positive | Implementations MUST document their post-retention behaviour in operational documentation | — | — |
| STATE-§4.1.3-05 | 4.1.3 | SHOULD | sdk_enabled | behavioural_positive | Regulated deployments SHOULD prefer archival over immediate deletion for regulatory safety | — | — |
| STATE-§4.1.4-01 | 4.1.4 | MUST | sdk | behavioural_positive | Logically deleted entries MUST remain in the temporal store until retention expires | — | ITV-253 |
| STATE-§4.1.4-02 | 4.1.4 | MAY | sdk_enabled | behavioural_positive | After the retention period expires, the entry MAY be physically removed. | — | — |
| STATE-§4.2.1-01 | 4.2.1 | MUST | deployment | behavioural_positive | Entry storage backend MUST physically reside within the declared data residency zone | — | — |
| STATE-§4.2.1-02 | 4.2.1 | MUST_NOT | deployment | behavioural_negative | Cross-zone replication MUST NOT occur; all replicas MUST be within the declared residency zone | — | — |
| STATE-§4.2.1-03 | 4.2.1 | MUST | deployment | behavioural_positive | Data MUST be processed (read, transformed, aggregated) within the declared residency zone | — | — |
| STATE-§4.2.1-04 | 4.2.1 | MUST | deployment | behavioural_positive | Backup copies of the data MUST be stored within the declared zone. | — | — |
| STATE-§4.2.1-05 | 4.2.1 | MUST | deployment | behavioural_positive | Backup media leaving the residency zone MUST be encrypted | — | — |
| STATE-§4.2.1-06 | 4.2.1 | MUST | deployment | behavioural_positive | Encryption keys for offsite backup media MUST be managed within the residency zone | — | — |
| STATE-§4.2.2-01 | 4.2.2 | MUST | deployment | behavioural_positive | Implementations MUST provide a mechanism to verify data residency enforcement | — | — |
| STATE-§4.2.2-02 | 4.2.2 | RECOMMENDED | sdk_enabled | behavioural_positive | Self-declaration of storage regions in IdentityRecord is RECOMMENDED as minimum verification | — | — |
| STATE-§4.2.2-03 | 4.2.2 | RECOMMENDED | sdk_enabled | behavioural_positive | SOC 2 Type II attestation is RECOMMENDED for GDPR personal data or MiFID II financial data | — | — |
| STATE-§4.2.3-01 | 4.2.3 | MUST | sdk | behavioural_positive | SET MUST be rejected with "invalid_request" when the implementation lacks storage in the declared zone | — | ITV-254 |
| STATE-§4.2.3-02 | 4.2.3 | MUST_NOT | sdk | behavioural_negative | Implementations MUST NOT silently store data in the wrong zone. | — | ITV-255 |
| STATE-§4.3.1-01 | 4.3.1 | RECOMMENDED | sdk_enabled | behavioural_positive | The RECOMMENDED inactivity threshold is equal to the effective retention period. | — | — |
| STATE-§4.3.1-02 | 4.3.1 | MAY | sdk_enabled | behavioural_positive | Implementations MAY archive entries proactively based on storage capacity or cost constraints | — | — |
| STATE-§4.3.2-01 | 4.3.2 | MUST | deployment | behavioural_positive | Archived entries MUST remain SNAPSHOT-accessible for regulatory inspection for 12 months | — | ITV-256 |
| STATE-§4.3.2-02 | 4.3.2 | MUST | deployment | behavioural_positive | SNAPSHOT queries covering an archived entry's time range MUST return that entry | — | ITV-256 |
| STATE-§4.3.2-03 | 4.3.2 | MAY | sdk_enabled | behavioural_positive | Implementations MAY increase response latency for archived entries (cold storage) | — | — |
| STATE-§4.3.2-04 | 4.3.2 | SHOULD | sdk_enabled | behavioural_positive | Implementations SHOULD document expected latency for archived entry access | — | — |
| STATE-§4.3.2-05 | 4.3.2 | MAY | sdk_enabled | behavioural_positive | After the 12-month archival period, the entry MAY be permanently deleted. | — | — |
| STATE-§4.3.3-01 | 4.3.3 | MUST | deployment | behavioural_positive | The entry's value MUST be removed from both primary and archival storage. | — | — |
| STATE-§4.3.3-02 | 4.3.3 | MUST | deployment | behavioural_positive | The archival record (if any) MUST be purged along with the primary record. | — | — |
| STATE-§5.1-01 | 5.1 | MUST | operational_policy | behavioural_positive | The operator MUST maintain the Art. 30 register; ARSIA does not generate it automatically | — | — |
| STATE-§5.1-02 | 5.1 | SHOULD | sdk_enabled | behavioural_positive | Implementations SHOULD provide tooling (reports, exports, APIs) to facilitate Art. 30 compliance | — | — |
| STATE-§5.2-01 | 5.2 | MUST | sdk | behavioural_positive | compliance.legal_basis MUST be set to a GDPR Art. 6(1) value for SET operations on personal entries | arsia-compliance-field | — |
| STATE-§5.2-02 | 5.2 | MUST | sdk | behavioural_positive | SET for personal entries MUST be rejected when compliance.legal_basis is missing from the envelope | — | ITV-257 |
| STATE-§5.2-03 | 5.2 | MUST | sdk | behavioural_positive | The rejection error MUST use code "invalid_request" with details including missing_legal_basis | arsia-message | — |
| STATE-§5.2-04 | 5.2 | SHOULD | sdk_enabled | behavioural_positive | Pseudonymised entries SHOULD include a legal_basis but are not required to | — | — |
| STATE-§5.2-05 | 5.2 | MUST | operational_policy | behavioural_positive | When the legal basis changes, the operator MUST delete the entry or update it with a new SET carrying the new basis | — | — |
| STATE-§5.3.1-01 | 5.3.1 | MAY | operational_policy | behavioural_positive | Operators MAY decline an Art. 17 erasure request when an Art. 17(3) exception applies | — | — |
| STATE-§5.3.1-02 | 5.3.1 | MUST | operational_policy | behavioural_positive | Operators declining erasure MUST inform the data subject of the grounds for refusal | — | — |
| STATE-§5.3.1-03 | 5.3.1 | SHOULD | deployment | behavioural_positive | Purge propagation to backup media SHOULD complete within 30 days | — | — |
| STATE-§5.3.1-04 | 5.3.1 | RECOMMENDED | deployment | behavioural_positive | A 30-day purge propagation timeline to backup media is RECOMMENDED | — | — |
| STATE-§5.3.1-05 | 5.3.1 | MUST | operational_policy | behavioural_positive | Operators MUST document the expected backup propagation timeline and communicate it on request | — | — |
| STATE-§5.3.2-01 | 5.3.2 | MUST | operational_policy | behavioural_positive | The operator MUST make the legal determination when GDPR erasure conflicts with regulatory retention | — | — |
| STATE-§5.4-01 | 5.4 | SHOULD | sdk_enabled | behavioural_positive | Implementations SHOULD enforce configurable per-agent limits on entry count and storage size | — | ITV-258 |
| STATE-§5.4-02 | 5.4 | RECOMMENDED | operational_policy | behavioural_positive | RECOMMENDED per-agent limits: 10,000 entries, 100 MiB storage, 1,000 personal data entries | — | — |
| STATE-§5.4-03 | 5.4 | SHOULD | operational_policy | behavioural_positive | Per-agent storage limits SHOULD be configurable by the platform operator | — | — |
| STATE-§5.4-04 | 5.4 | SHOULD | operational_policy | behavioural_positive | Implementations SHOULD apply per-agent limits as safeguards against unbounded data accumulation | — | — |
| STATE-§5.4-05 | 5.4 | MUST | sdk | behavioural_positive | Session-scoped entries MUST expire when the session ends | — | ITV-259 |
| STATE-§5.4-06 | 5.4 | SHOULD | sdk_enabled | behavioural_positive | Implementations SHOULD apply a default expiry to entries without explicit expires_at or retention | — | ITV-261 |
| STATE-§5.4-07 | 5.4 | MUST | sdk | behavioural_positive | Session scope default expiry is the session duration (MUST) | — | ITV-260 |
| STATE-§5.4-08 | 5.4 | RECOMMENDED | operational_policy | behavioural_positive | Agent scope default expiry of 90 days is RECOMMENDED | — | ITV-261 |
| STATE-§5.4-09 | 5.4 | RECOMMENDED | operational_policy | behavioural_positive | Shared scope default expiry of 90 days is RECOMMENDED | — | — |
| STATE-§5.4-10 | 5.4 | MUST | sdk | behavioural_positive | Agents needing longer retention MUST explicitly set expires_at or retention | — | — |
| STATE-§5.4-11 | 5.4 | SHOULD | operational_policy | behavioural_positive | Implementations SHOULD issue warnings when an agent approaches its storage limits | — | — |
| STATE-§5.4-12 | 5.4 | SHOULD | operational_policy | behavioural_positive | Storage limit warnings SHOULD be issued at 80% of any configured limit | — | — |
| STATE-§5.5-01 | 5.5 | MAY | operational_policy | behavioural_positive | Operators MAY transform exported entries into other formats (CSV, XML, etc.) for portability requests | — | — |
| STATE-§5.6-01 | 5.6 | MUST | sdk | behavioural_negative | "sensitive" entries MUST declare an Art. 9(2) legal basis; Art. 6(1) grounds rejected (Core §4.3.8, Rule 8) | arsia-compliance-field | ITV-555, INV-20 |
| STATE-§5.6-02 | 5.6 | SHOULD | operational_policy | behavioural_positive | Art. 30 records SHOULD include pii_special_categories values in "categories of personal data" | — | — |
| STATE-§5.7-01 | 5.7 | MUST | sdk | behavioural_positive | Breach notification payload type is arsiaprotocol.compliance/breach-notification with intent "event" | arsia-breach-notification, arsia-message | ITV-556, ITV-557 |
| STATE-§5.7-02 | 5.7 | MUST | sdk | schema_positive | REQUIRED fields: notification_target, breach_id, nature_of_breach, awareness_timestamp, dpo_contact, likely_consequences, measures_taken (GDPR Art. 33(3)(a)-(d), Art. 34(2)) | arsia-breach-notification | ITV-556, ITV-557 |
| STATE-§5.7-03 | 5.7 | SHOULD | sdk_enabled | behavioural_positive | supervisory_authority notifications SHOULD include categories_of_data, categories_of_data_subjects, approximate_data_subject_count, approximate_record_count | arsia-breach-notification | ITV-556 |
| STATE-§5.7-04 | 5.7 | SHOULD | sdk_enabled | behavioural_positive | data_subject notifications SHOULD include remediation_advice | arsia-breach-notification | ITV-557 |
| STATE-§5.7-05 | 5.7 | MUST | sdk | behavioural_positive | breach_id enables correlation of multiple notifications about the same breach per Art. 33(4) | arsia-breach-notification | ITV-556, ITV-557 |
| STATE-§6.1-01 | 6.1 | RECOMMENDED | sdk_enabled | behavioural_positive | GDPR-STANDARD profile: retention of 90 days is RECOMMENDED as platform default | — | — |
| STATE-§6.1-02 | 6.1 | MUST | sdk | behavioural_positive | GDPR-STANDARD with pii_involved true: legal_basis MUST be set in the compliance envelope | arsia-compliance-field | — |
| STATE-§6.1-03 | 6.1 | SHOULD | operational_policy | behavioural_positive | Operators SHOULD maintain GDPR Art. 30 records for all interactions involving personal data | — | — |
| STATE-§6.1-04 | 6.1 | MUST | sdk | behavioural_positive | GDPR-STANDARD with pii_involved true: audit_required is always effectively true (Core §4.3.8, Rule 7) | arsia-compliance-field | ITV-553, ITV-554 |
| STATE-§6.2-01 | 6.2 | RECOMMENDED | sdk_enabled | behavioural_positive | EU-AI-ACT-HIGH-RISK: data_residency "EU" is RECOMMENDED for EU-based operators | — | — |
| STATE-§6.2-02 | 6.2 | MUST | sdk | behavioural_positive | EU-AI-ACT-HIGH-RISK: every response MUST include payload.explanation with reasoning, confidence, and inputs_used | arsia-compliance-field | — |
| STATE-§6.2-03 | 6.2 | MUST_NOT | sdk | behavioural_negative | EU-AI-ACT-HIGH-RISK: when the effective oversight set includes required_before_execution, the action MUST NOT execute until human approval via the pending_approval flow | arsia-compliance-field, arsia-message | ITV-421, ITV-609 |
| STATE-§6.2-05 | 6.2 | SHOULD | sdk_enabled | behavioural_positive | A receiving agent that receives EU-AI-ACT-HIGH-RISK from an agent not classified as high-risk SHOULD log a compliance warning | — | — |
| STATE-§6.3-01 | 6.3 | MUST | external | behavioural_positive | MIFID-II: major ICT-related incidents MUST be reported to competent authorities | — | — |
| STATE-§6.3-02 | 6.3 | MUST | sdk | procedural | MIFID-II: all AssetTransferRequest messages MUST generate MiFID II audit records | arsia-compliance-field | — |
| STATE-§6.3-03 | 6.3 | MUST | sdk | procedural | MIFID-II: asset transfer audit records MUST contain all fields per ARSIA-Assets §6.1.1 | arsia-compliance-field | — |
| STATE-§6.4-01 | 6.4 | MUST | sdk | behavioural_positive | PAC-AGRICULTURE profile name MUST be accepted without error (active profile) | arsia-compliance-profiles | ITV-262 |
| STATE-§6.4-02 | 6.4 | MUST | sdk | behavioural_negative | PAC-AGRICULTURE: retention MUST NOT be less than 1096 (3-year CAP minimum) | arsia-compliance-field | — |
| STATE-§6.5-01 | 6.5 | MUST | sdk | behavioural_positive | EU-AI-ACT-LIMITED-RISK profile name MUST be accepted without error (active profile) | arsia-compliance-profiles | ITV-558 |
| STATE-§6.5-02 | 6.5 | MUST | sdk | behavioural_positive | EU-AI-ACT-LIMITED-RISK: transparency obligations per Art. 50 MUST be enforced | arsia-compliance-profiles | — |
| STATE-§6.6-01 | 6.6 | MUST | sdk | behavioural_positive | DSA-VLOP profile name MUST be accepted without error (active profile) | arsia-compliance-profiles | ITV-559 |
| STATE-§6.6-02 | 6.6 | MUST | sdk | behavioural_negative | DSA-VLOP: retention MUST NOT be less than 730 (2-year DSA minimum) | arsia-compliance-field | — |
| STATE-§6.7-01 | 6.7 | MUST | sdk | behavioural_positive | DORA profile name MUST be accepted without error (active profile) | arsia-compliance-profiles | ITV-560 |
| STATE-§6.7-02 | 6.7 | MUST | sdk | behavioural_negative | DORA: retention MUST NOT be less than 1827 days (profile conservative policy, not a DORA period) | arsia-compliance-field | — |
| STATE-§7.1-01 | 7.1 | REQUIRED | sdk | structural | ArsiaAuditRecord fields are REQUIRED unless explicitly marked OPTIONAL | arsia-audit-record | — |
| STATE-§7.1-02 | 7.1 | OPTIONAL | sdk | structural | Some ArsiaAuditRecord fields are marked OPTIONAL per individual field definitions | arsia-audit-record | — |
| STATE-§7.1-03 | 7.1 | REQUIRED | sdk | structural | ArsiaAuditRecord.record_id field is REQUIRED (string, UUID v4) | arsia-audit-record | — |
| STATE-§7.1-04 | 7.1 | REQUIRED | sdk | structural | ArsiaAuditRecord.event_type field is REQUIRED (enum of 22 protocol event types) | arsia-audit-record | ITV-17, ITV-88, ITV-89, ITV-90, ITV-91, ITV-93, ITV-94, ITV-96, ITV-99, ITV-100, ITV-101, ITV-102, ITV-632, ITV-633, ITV-634, ITV-636 |
| STATE-§7.1-05 | 7.1 | REQUIRED | sdk | structural | ArsiaAuditRecord.from_agent field is REQUIRED (string, agent-id of sender) | arsia-audit-record | — |
| STATE-§7.1-06 | 7.1 | REQUIRED | sdk | structural | ArsiaAuditRecord.message_id field is REQUIRED (links audit record to originating message) | arsia-audit-record | — |
| STATE-§7.1-07 | 7.1 | OPTIONAL | sdk | structural | ArsiaAuditRecord.human_oversight_status field is OPTIONAL (enum: not_required, pending, approved, denied, expired) | arsia-audit-record | ITV-16, ITV-17, ITV-89, STV-07 |
| STATE-§7.1-08 | 7.1 | OPTIONAL | sdk | structural | ArsiaAuditRecord.approver_id field is OPTIONAL (agent-id of the oversight decision maker) | arsia-audit-record | ITV-16, ITV-89, STV-07 |
| STATE-§7.1-09 | 7.1 | REQUIRED | sdk | structural | ArsiaAuditRecord.processed_at field is REQUIRED (RFC 3339, millisecond precision, UTC) | arsia-audit-record | — |
| STATE-§7.1-10 | 7.1 | MUST | sdk | behavioural_positive | ArsiaAuditRecord.retained_until defines the date until which the record MUST be retained | arsia-audit-record | STV-06 |
| STATE-§7.1-11 | 7.1 | MAY | sdk_enabled | behavioural_positive | After retained_until, the audit record MAY be archived or deleted per archival rules | — | — |
| STATE-§7.1-12 | 7.1 | OPTIONAL | sdk | structural | ArsiaAuditRecord.data_residency field is OPTIONAL (geographic storage zone) | arsia-audit-record | — |
| STATE-§7.1-13 | 7.1 | MUST | sdk | behavioural_positive | Audit record data_residency MUST match the originating message's compliance.data_residency | arsia-audit-record | — |
| STATE-§7.1-14 | 7.1 | MUST | deployment | behavioural_positive | Audit records with data residency constraints MUST be stored within the declared zone | arsia-audit-record | STV-06 |
| STATE-§7.1-15 | 7.1 | REQUIRED | sdk | structural | ArsiaAuditRecord.to_agent field is REQUIRED (string, agent-id of recipient) | arsia-audit-record | — |
| STATE-§7.1-16 | 7.1 | REQUIRED | sdk | structural | ArsiaAuditRecord.intent field is REQUIRED (intent from the originating message) | arsia-audit-record | — |
| STATE-§7.1-17 | 7.1 | REQUIRED | sdk | structural | ArsiaAuditRecord.payload_type field is REQUIRED (payload.type from the originating message) | arsia-audit-record | — |
| STATE-§7.1-18 | 7.1 | REQUIRED | sdk | structural | ArsiaAuditRecord.payload_hash field is REQUIRED (SHA-256 of canonicalised payload) | arsia-audit-record | — |
| STATE-§7.1-19 | 7.1 | REQUIRED | sdk | structural | ArsiaAuditRecord.compliance_profile_declared (profile as declared, null, or "none") and compliance_profile_resolved (profile actually applied, or "none") fields are REQUIRED | arsia-audit-record | — |
| STATE-§7.1-20 | 7.1 | REQUIRED | sdk | structural | ArsiaAuditRecord.operator_id field is REQUIRED (owner_id from the agent's IdentityRecord) | arsia-audit-record | — |
| STATE-§7.1-21 | 7.1 | OPTIONAL | sdk | structural | ArsiaAuditRecord.plaintext_hash field is OPTIONAL; present only when the originating message has security.encrypted=true | arsia-audit-record | ITV-525, ITV-526 |
| STATE-§7.1-22 | 7.1 | REQUIRED | sdk | structural | ArsiaAuditRecord.declared_retention is REQUIRED (nullable; null when omitted, including a rejected declaration) (A-81) | arsia-audit-record | INV-53, ITV-622 |
| STATE-§7.1-23 | 7.1 | MUST_NOT | sdk | behavioural_positive | On a record carrying obligation_resolution, the retention fields MUST NOT diverge from those derived from its retention member (rejection records: evidence retained under the profile minimum) | arsia-audit-record | ITV-97, ITV-600, ITV-622 |
| STATE-§7.1-24 | 7.1 | REQUIRED | sdk | structural | obligation_resolution is REQUIRED on covered records (intent request; event_type request, state_set, state_delete, state_purge, state_grant, state_revoke, asset_transfer, rollback) and on compliance rejection records | arsia-audit-record | ITV-601, ITV-600, INV-54, INV-56 |
| STATE-§7.1-25 | 7.1 | MUST | sdk | structural | A record with rejection_cause compliance MUST have event_type error, a rejected obligation_resolution with non-empty conflicts, and correlation_id set to the rejected message's id | arsia-audit-record | ITV-600, INV-57, INV-58, INV-59, INV-60 |
| STATE-§7.1-26 | 7.1 | MUST | sdk | behavioural_negative | Every rejection produced by compliance validation MUST produce a rejection_cause compliance record, whatever audit_required the rejected message declares | arsia-audit-record | ITV-603, ITV-622, INV-62 |
| STATE-§7.1-27 | 7.1 | MUST | sdk | structural | review_pending, review_overdue, review_escalation and review_decision records MUST carry their extension fields (State §7.1 table) | arsia-audit-record | ITV-632, ITV-633, ITV-634, ITV-635, ITV-636, ITV-637, INV-72, INV-73, INV-74, INV-75 |
| STATE-§7.2-01 | 7.2 | MUST | deployment | behavioural_positive | Audit records MUST be append-only. | — | STV-07 |
| STATE-§7.2-02 | 7.2 | MUST_NOT | deployment | behavioural_negative | Once an ArsiaAuditRecord is written, it MUST NOT be modified. | — | — |
| STATE-§7.2-03 | 7.2 | MUST | sdk | procedural | New audit records MUST be created for status changes; existing records MUST NOT be updated | — | STV-07 |
| STATE-§7.2-04 | 7.2 | MUST_NOT | deployment | behavioural_negative | Audit records MUST NOT be deleted before retained_until | — | — |
| STATE-§7.2-05 | 7.2 | MUST_NOT | deployment | behavioural_negative | No mechanism (API, admin tool, or database operation) may delete audit records within retention | — | — |
| STATE-§7.2-06 | 7.2 | MUST | deployment | behavioural_positive | Implementations MUST use an append-only storage mechanism for audit records. | — | — |
| STATE-§7.2-07 | 7.2 | MUST | deployment | behavioural_positive | Audit store MUST enforce INSERT-only semantics with durable persistence; application roles MUST NOT UPDATE or DELETE audit records | — | — |
| STATE-§7.2-08 | 7.2 | MUST | sdk | behavioural_positive | At Compliance and Full conformance every audit record MUST carry hash_chain, chain_id, chain_seq and chain_format and MUST be chained as defined in §7.2 | arsia-audit-record | ITV-95, ITV-592, ITV-593, ITV-594, ITV-595, ITV-596; harness R14 (f) |
| STATE-§7.2-09 | 7.2 | RECOMMENDED | sdk_enabled | behavioural_positive | At Core conformance, chaining audit records is RECOMMENDED | arsia-audit-record | harness R14 (f) |
| STATE-§7.2-10 | 7.2 | MUST | sdk | procedural | Chain value MUST be the lowercase hex SHA-256 of RFC 8785({previous_chain_value, record}) where record is the complete record without hash_chain; no other member excluded | arsia-audit-record | ITV-95, ITV-592, ITV-593, ITV-594, ITV-595, ITV-596; check_consistency (DR-5 chained vectors); harness R14 (a), (b) |
| STATE-§7.2-11 | 7.2 | MUST | sdk | structural | The first entry of a chain has chain_seq 1 and is computed with previous_chain_value null (part of the chaining MUST) | arsia-audit-record, arsia-audit-chain-tombstone | ITV-95, ITV-592; harness R14 (a) |
| STATE-§7.2-12 | 7.2 | MUST | operational_policy | behavioural_positive | Operators MUST document in Art. 30 register if audit payload_hash could be linked to personal data | — | — |
| STATE-§7.2-13 | 7.2 | MAY | deployment | informational | An audit log MAY consist of several chains; each record belongs to exactly one chain, identified by chain_id | arsia-audit-record | — |
| STATE-§7.2-14 | 7.2 | MUST | operational_policy | procedural | The operator's audit policy MUST document the chains of the log | — | — |
| STATE-§7.2-15 | 7.2 | MUST | sdk | structural | Chain entries MUST be ordered by chain_seq alone, consecutive from 1, with no gaps or duplicates (part of the chaining MUST) | arsia-audit-record, arsia-audit-chain-tombstone | ITV-592, ITV-593, ITV-594, ITV-595, ITV-596; harness R14 (c), (d) |
| STATE-§7.2-16 | 7.2 | MUST | deployment | behavioural_positive | Permanent deletion under §7.3 MUST be performed only through an operator-controlled maintenance path separate from application roles | — | — |
| STATE-§7.2-17 | 7.2 | MUST | deployment | behavioural_positive | The maintenance path MUST write the tombstone for a deleted chained record: exactly chain_id, chain_seq, chain_format, hash_chain and previous_chain_value, no field of the deleted record | arsia-audit-chain-tombstone | ITV-595, INV-52; harness R14 (a) |
| STATE-§7.2-18 | 7.2 | MUST | sdk | behavioural_negative | A verifier holding an independent head MUST reject the chain on missing or duplicate positions, foreign chain_id or format, recomputed value mismatch, tombstone previous-value mismatch, or head mismatch | arsia-audit-record, arsia-audit-chain-tombstone | ITV-597, ITV-598, ITV-599; check_consistency (DR-5 tampered); harness R14 (b)-(h) |
| STATE-§7.2-19 | 7.2 | MUST_NOT | operational_policy | behavioural_negative | Implementations MUST NOT claim stronger tamper-evidence properties than those stated in §7.2 | — | — |
| STATE-§7.2-20 | 7.2 | MUST | operational_policy | procedural | When external anchoring is deployed, its scope and cadence MUST be documented in the operator's audit policy | — | — |
| STATE-§7.2-21 | 7.2 | MUST | sdk | structural | The four chain fields (hash_chain, chain_id, chain_seq, chain_format) MUST be present together or not at all | arsia-audit-record | INV-51, ITV-95, ITV-592, ITV-593, ITV-594, ITV-596; harness R14 (f) |
| STATE-§7.2-22 | 7.2 | MUST | deployment | behavioural_positive | A tombstone MUST persist for as long as its chain exists | arsia-audit-chain-tombstone | ITV-595; harness R14 (a), (c) |
| STATE-§7.3-01 | 7.3 | RECOMMENDED | sdk_enabled | behavioural_positive | Minimum audit record retention varies by profile (RECOMMENDED: 90 days for GDPR-STANDARD) | arsia-compliance-field | — |
| STATE-§7.3-02 | 7.3 | MAY | sdk_enabled | behavioural_positive | Audit records past retained_until MAY be moved to cold storage (archive) | — | — |
| STATE-§7.3-03 | 7.3 | MUST | deployment | behavioural_positive | Archived audit records MUST remain available for regulatory inspection for 12 months | — | — |
| STATE-§7.3-04 | 7.3 | MAY | sdk_enabled | behavioural_positive | Audit records MAY be permanently deleted after 12 months in archive | — | — |
| STATE-§7.3-05 | 7.3 | SHOULD | operational_policy | behavioural_positive | Deletion of archived audit records SHOULD be documented in the operator's data retention policy | — | — |
| STATE-§7.3-06 | 7.3 | MAY | operational_policy | behavioural_positive | Operators MAY extend audit retention beyond profile minimum via per-message or platform-wide policy | — | — |
| STATE-§7.3-07 | 7.3 | MUST | deployment | behavioural_positive | Permanent deletion of a chained record MUST leave a tombstone at its chain position, written by the §7.2 maintenance path | arsia-audit-chain-tombstone | ITV-595 |
| STATE-§7.4-01 | 7.4 | MUST | deployment | interoperability | Compliance-level implementations MUST serve audit trail at GET /.well-known/arsia/audit, incl. chain retrieval by chain_id (§7.2) | arsia-audit-query-response | ITV-55, ITV-56 |
| STATE-§7.4-02 | 7.4 | MUST | deployment | interoperability | Audit trail endpoint MUST require the arsiaprotocol.audit.read capability | — | ITV-263 |
| STATE-§7.4-03 | 7.4 | MUST | sdk | behavioural_positive | Audit trail recipients MUST verify the requester holds arsiaprotocol.audit.read | — | ITV-263, ITV-264 |
| STATE-§7.4-04 | 7.4 | SHOULD | sdk_enabled | behavioural_positive | Access tokens for arsiaprotocol.audit.read SHOULD have a short lifetime | — | — |
| STATE-§7.4-05 | 7.4 | RECOMMENDED | sdk_enabled | behavioural_positive | A maximum lifetime of 300 seconds for arsiaprotocol.audit.read tokens is RECOMMENDED | — | — |
| STATE-§7.4-06 | 7.4 | MAY | sdk_enabled | behavioural_positive | Implementations MAY enforce additional record-level access controls on audit queries | — | — |
| STATE-§8.1-01 | 8.1 | MUST_NOT | sdk | behavioural_negative | Custom state operations MUST NOT use the reserved arsiaprotocol.state/ payload type prefix | arsia-state-operations, arsia-message | ITV-265, ITV-266 |
| STATE-§8.1-02 | 8.1 | MUST | sdk | behavioural_positive | State extensions MUST use a non-reserved prefix (e.g., com.example.state/custom-operation) | arsia-state-operations, arsia-message | ITV-265, ITV-266 |
| STATE-§8.2.1-01 | 8.2.1 | MUST | sdk | behavioural_positive | arsiaprotocol.state.purge and .snapshot MUST be explicitly granted; wildcards do not include them (non-delegable per Actions §1.2 condition 3) | — | ITV-267, INV-23, INV-24 |
| STATE-§8.2.1-02 | 8.2.1 | MUST | external | behavioural_positive | Elevated capability restriction MUST be enforced by both Authorization Servers and state implementations | — | — |
| STATE-§8.2.2-01 | 8.2.2 | MUST | sdk | behavioural_positive | State implementations MUST enforce capabilities per ARSIA-Core.md §6.4. | — | ITV-268 |
| STATE-§8.3-01 | 8.3 | MUST | sdk | procedural | All state operations MUST generate audit events when the envelope's compliance.audit_required is true | — | ITV-269 |
| STATE-§8.3-02 | 8.3 | MUST | sdk | behavioural_positive | Entry MUST inherit data_residency from envelope when payload.args does not set it | — | ITV-536 |
| STATE-§8.3-03 | 8.3 | MUST | sdk | behavioural_positive | payload.args.data_residency MUST take precedence over compliance.data_residency | — | ITV-537 |
| STATE-§8.3-04 | 8.3 | MUST | sdk | behavioural_positive | Entry MUST inherit retention from envelope when payload.args does not set it | — | ITV-538 |
| STATE-§8.3-05 | 8.3 | MUST | sdk | behavioural_positive | payload.args.retention takes precedence over compliance.retention; the applying value is resolved against the profile retention_minimum, and an explicit value below it MUST be rejected (Core §4.3.8 Rule 4) | — | ITV-539 |
| STATE-§8.3-06 | 8.3 | MUST | sdk | behavioural_positive | legal_basis MUST be checked when pii_classification is 'personal' or 'sensitive' | — | ITV-540, ITV-555 |
| STATE-§8.3-07 | 8.3 | MUST_NOT | sdk | behavioural_negative | legal_basis MUST NOT be stored on the StateEntry itself | arsia-state-entry | — |
| STATE-§8.3-08 | 8.3 | MUST | sdk | behavioural_positive | legal_basis MUST be recorded in the audit event | arsia-audit-record | ITV-542 |
| STATE-§8.3-09 | 8.3 | MUST | sdk | behavioural_positive | Profile defaults MUST be applied for compliance fields not explicitly set | — | ITV-541 |
| STATE-§8.4-01 | 8.4 | MUST | sdk | behavioural_positive | Conflict errors on a live entry MUST include current_generation, current_version, the stated preconditions, updated_at and updated_by | arsia-message | ITV-82, ITV-87, ITV-151, INV-86, INV-89 |
| STATE-§8.4-02 | 8.4 | MUST | sdk | behavioural_positive | Absent-entry conflict details MUST consist of entry_live false and the stated preconditions | arsia-message | ITV-679, INV-87, INV-90, INV-91 |
| STATE-§8.4-03 | 8.4 | MUST_NOT | sdk | behavioural_negative | Absent-entry conflict details MUST NOT include current_generation, current_version, updated_at or updated_by | arsia-message | INV-87 |
| STATE-§8.4-04 | 8.4 | MUST | sdk | behavioural_positive | PURGE retention error details MUST consist of within_retention (true) and entry_retained_until | arsia-message | ITV-685, INV-97, INV-98 |
| STATE-§9-01 | 9 | MUST | sdk_enabled | behavioural_positive | Conformant implementations MUST pass all conformance tests at their applicable level | — | — |
| STATE-§9-02 | 9 | MUST_NOT | sdk | behavioural_negative | PURGE audit event MUST NOT include the purged entry value (STATE-03 test) | arsia-audit-record | ITV-270 |
| STATE-§9-03 | 9 | MUST_NOT | sdk | behavioural_negative | Implementation MUST NOT physically remove entries before the retention period elapses (STATE-05 test) | arsia-state-entry | ITV-271 |
| STATE-§10.1-01 | 10.1 | MUST | deployment | interoperability | State operation messages MUST be transmitted over TLS 1.3 or later | — | — |
| STATE-§10.1-02 | 10.1 | MUST | sdk | interoperability | State operation messages MUST be signed per ARSIA-Core §5.1 | arsia-message | — |
| STATE-§10.1-03 | 10.1 | MUST | sdk | interoperability | State operation messages MUST carry a valid access token with the required capabilities | arsia-message | ITV-272 |
| STATE-§10.1-04 | 10.1 | SHOULD | sdk_enabled | behavioural_positive | Agents SHOULD request only the capabilities they need (least privilege) | — | — |
| STATE-§10.1-05 | 10.1 | SHOULD | sdk_enabled | behavioural_positive | Read-only agents SHOULD request arsiaprotocol.state.read only (reserved-namespace wildcards satisfy nothing, ARSIA-Actions.md §1.2) | — | — |
| STATE-§10.1-06 | 10.1 | SHOULD_NOT | sdk_enabled | behavioural_positive | Agents that never purge SHOULD NOT be granted arsiaprotocol.state.purge | — | — |
| STATE-§10.2-01 | 10.2 | MUST | sdk | behavioural_positive | Implementations MUST validate keys against the §2.1.1 pattern before processing any operation | arsia-state-entry, arsia-state-operations | — |
| STATE-§10.2-02 | 10.2 | MUST_NOT | sdk | behavioural_negative | Implementations MUST NOT interpret or execute state value contents | — | — |
| STATE-§10.2-03 | 10.2 | MUST | sdk | behavioural_positive | State values MUST be treated as data, not as code or commands | — | — |
| STATE-§10.2-04 | 10.2 | MUST | sdk_enabled | behavioural_positive | Agents MUST validate and sanitise consumed state values before use in injection-prone contexts | — | — |
| STATE-§10.2-05 | 10.2 | SHOULD | sdk_enabled | behavioural_positive | Implementations SHOULD enforce rate limits on state operations per agent discovery metadata | — | — |
| STATE-§10.2-06 | 10.2 | SHOULD_NOT | sdk_enabled | behavioural_positive | Agents SHOULD NOT be able to discover the existence of entries they cannot access | — | — |
| STATE-§10.2-07 | 10.2 | MUST | sdk | behavioural_positive | QUERY and GET MUST return empty results (not errors) when agent lacks access, except missing capabilities | — | ITV-273 |
| STATE-§10.3-01 | 10.3 | SHOULD | sdk_enabled | behavioural_positive | Implementations SHOULD use constant-time key comparison when lookups may reveal other agents' entries | — | — |
| STATE-§10.3-02 | 10.3 | SHOULD_NOT | sdk_enabled | behavioural_positive | Agents SHOULD NOT be able to infer the storage usage of other agents | — | — |
| STATE-§10.3-03 | 10.3 | MUST | sdk | behavioural_positive | QUERY result counts MUST only reflect entries accessible to the requesting agent | — | ITV-274 |
| STATE-§10.4-00 | 10.4 | MUST | deployment | behavioural_positive | Implementations MUST encrypt values at rest when pii_classification is "sensitive"; all "personal" obligations apply plus authenticated encryption (per §2.1.10) | — | — |
| STATE-§10.4-01 | 10.4 | MUST | deployment | behavioural_positive | Implementations MUST encrypt values at rest when pii_classification is "personal" | — | — |
| STATE-§10.4-02 | 10.4 | SHOULD | sdk_enabled | behavioural_positive | Implementations SHOULD encrypt values at rest when pii_classification is "pseudonymised" | — | — |
| STATE-§10.4-03 | 10.4 | RECOMMENDED | deployment | behavioural_positive | Encryption at rest for pii_classification "none" is RECOMMENDED but not required | — | — |
| STATE-§10.4-04 | 10.4 | MUST | deployment | behavioural_positive | At-rest encryption keys MUST follow ARSIA-Identity §2.1 key management (no plaintext in production) | — | — |
| STATE-§10.4-05 | 10.4 | RECOMMENDED | deployment | behavioural_positive | HSM or cloud KMS for at-rest encryption key storage is RECOMMENDED | — | — |
| STATE-§10.4-06 | 10.4 | SHOULD | sdk_enabled | behavioural_positive | Implementations SHOULD encrypt the key field when it may contain PII-derived identifiers | — | — |
| STATE-§11.1-01 | 11.1 | MAY | sdk_enabled | behavioural_positive | Implementations MAY use multiple storage backends for different scopes (e.g., Redis + PostgreSQL) | — | — |
| STATE-§11.2-01 | 11.2 | RECOMMENDED | sdk_enabled | behavioural_positive | PostgreSQL temporal tables (SQL:2011) are the RECOMMENDED approach for temporal storage | — | — |
| STATE-§11.3-01 | 11.3 | MUST | sdk_enabled | behavioural_positive | The StateEntry key field MUST be indexed for efficient GET operations | — | — |
| STATE-§11.3-02 | 11.3 | MAY | sdk_enabled | behavioural_positive | Implementations MAY support cursor-based pagination as a non-standard QUERY extension | — | — |
| STATE-§11.3-03 | 11.3 | MAY | sdk_enabled | behavioural_positive | Implementations MAY cache frequently-read entries (especially global-scoped) in memory | — | — |
| STATE-§11.3-04 | 11.3 | MUST | sdk_enabled | behavioural_positive | Cache invalidation MUST respect version semantics | — | ITV-276 |
| STATE-§11.3-05 | 11.3 | MUST | sdk_enabled | behavioural_positive | Cached entries MUST be invalidated when a SET operation updates the entry | — | ITV-275 |
| STATE-§11.3-06 | 11.3 | RECOMMENDED | sdk_enabled | behavioural_positive | TTL-based cache with 60-second refresh for infrequently-changing global entries is RECOMMENDED | — | — |
| STATE-§11.3-07 | 11.3 | MAY | sdk_enabled | behavioural_positive | Batch state operations MAY be defined as extensions under a custom payload type prefix | — | — |
| STATE-§11.3-08 | 11.3 | MUST | sdk_enabled | procedural | Batch operations MUST generate individual audit events per affected entry (no aggregation) | — | ITV-277 |
| STATE-§11.4-01 | 11.4 | REQUIRED | sdk | behavioural_positive | The hash chain is REQUIRED at Compliance and Full conformance and RECOMMENDED at Core (restates §7.2) | arsia-audit-record | ITV-95, ITV-592, ITV-593, ITV-594, ITV-595, ITV-596; harness R14 (f) |

## Coverage Gaps

Generated: 2026-07-22 (Draft-02 regeneration — header-driven parser, reproducible via scripts/check_consistency.py companion tooling)

### Summary

| Metric | Count |
|--------|------:|
| Total requirements | 432 |
| Schema ≠ — | 172 |
| Vector ≠ — | 230 |
| Both ≠ — | 119 |
| Both = — (gaps) | 149 |

### Per-section breakdown

| § | Total | Schema ≠ — | Vector ≠ — | Both ≠ — | Both = — |
|---|-------|-----------|-----------|---------|---------|
| 1 | 38 | 7 | 17 | 4 | 18 |
| 2 | 83 | 32 | 48 | 22 | 25 |
| 3 | 106 | 53 | 87 | 46 | 12 |
| 4 | 36 | 5 | 8 | 1 | 24 |
| 5 | 33 | 8 | 12 | 6 | 19 |
| 6 | 19 | 14 | 6 | 6 | 5 |
| 7 | 62 | 39 | 27 | 23 | 19 |
| 8 | 18 | 8 | 16 | 7 | 1 |
| 9 | 3 | 2 | 2 | 2 | 1 |
| 10 | 23 | 3 | 3 | 1 | 18 |
| 11 | 11 | 1 | 4 | 1 | 7 |

## Draft-02 Delta (normative changes traced)

| Change | Anchor | Schema | Vectors |
|---|---|---|---|
| value semantics (I-JSON); lexical fidelity dropped; 2^53 rule | §2.1.2 | — | ITV-577/578; harness R8 |
| entry retention override = duration; reject below floor | §2.1.8 | state-entry (Phase-5 note) | STATE-12/13 |
| profile tables: retention_minimum durations + basis + clock_skew | §6.1-6.7 | catalog + profiles schema | consistency check |
| DSA-VLOP P1096D | §6.6 | catalog | consistency check |
| audit record: declared/resolved profile, retention fields, counterparty_owner_id | §7.1 | audit-record | 45 migrated |
| per-event-type extension fields documented in prose | §7.1 | audit-record | — |
| tamper-evidence scope statement (detected vs not) | §7.2 | — | — |
| GDPR language qualified | §7.2 | — | — |
| session-scope audit precedence (audit_required wins) | §1.1, §8.3 r4 | — | integration |
| shared vs agent+GRANT guidance; scope table fixed | §1.5 | — | — |
| reserved prefix examples arsiaprotocol.meta/ | §2.2 | — | — |
| §2.1.10 item 2: SHOULD-set + MUST-warn | §2.1.10 | state-entry | — |
| §10.4 rewritten; AEAD defined; legal_basis personal+sensitive | §10.4, §5.2 | — | — |
| entry generation; preconditions across recreation (expected_generation, entry_live); PURGE repetition by generation; conflict details aligned (A-79, A-94, A-95) | §2.1.14, §2.4, §3.1.2, §3.2.2, §8.4 | state-entry, state-operations, audit-record, message | ITV-676..681, INV-81..91; harness R17 |
| PURGE within retention needs a recorded retention_override, evaluated from stored state over every generation; state_purge records within_retention / entry_retained_until; erasure-vs-retention guidance no longer adjudicates; MIFID-II floor re-grounded as profile_floor (A-7, A-70, A-90, A-44) | §3.2.2, §4.1.1, §4.1.2, §5.3.2, §6.3, §7.1, §8.4 | common, state-operations, audit-record, message, catalog | ITV-682..687, INV-92..100; harness R18 |
