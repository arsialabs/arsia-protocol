<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
# ARSIA-Actions — Requirements Traceability Matrix

| ID | § | Modal | Layer | Kind | Requirement | Schema | Vector |
|----|---|-------|-------|------|-------------|--------|--------|
| ACT-§1.1-01 | 1.1 | MUST | sdk | structural | Concrete capability string MUST contain at least two dot-separated segments; wildcard capability string MUST contain at least one segment before .* | arsia-action-descriptor, arsia-message, arsia-capability-descriptor, arsia-onboarding-decision, arsia-discovery-response | INV-10, ITV-68 |
| ACT-§1.1-02 | 1.1 | MUST | sdk | behavioural_positive | Implementations MUST reject single-segment capability strings that lack a wildcard suffix | arsia-action-descriptor, arsia-message, arsia-capability-descriptor, arsia-onboarding-decision, arsia-discovery-response | ITV-68 |
| ACT-§1.1-03 | 1.1 | MUST_NOT | sdk | structural | Capability string MUST NOT exceed 128 characters including dots and wildcard suffix | arsia-action-descriptor, arsia-message | ITV-69 |
| ACT-§1.1-04 | 1.1 | MUST | sdk | behavioural_positive | Implementations MUST reject capability strings exceeding 128 characters | arsia-action-descriptor, arsia-message | ITV-69 |
| ACT-§1.1-05 | 1.1 | SHOULD | sdk_enabled | behavioural_positive | Implementations SHOULD use lowercase for capability strings by convention | — | ITV-278 |
| ACT-§1.1-06 | 1.1 | MUST_NOT | sdk_enabled | behavioural_negative | Implementations MUST NOT perform case-insensitive capability matching | — | ITV-278 |
| ACT-§1.1-07 | 1.1 | MUST_NOT | sdk | structural | Wildcard .* suffix MUST NOT appear in the middle of a capability string | arsia-action-descriptor, arsia-message | — |
| ACT-§1.1-08 | 1.1 | MUST_NOT | sdk | structural | Capability string MUST NOT consist solely of the wildcard .* | arsia-action-descriptor, arsia-message | — |
| ACT-§1.1-09 | 1.1 | MUST | sdk | behavioural_positive | Wildcard .* MUST be preceded by at least one domain-part segment | arsia-action-descriptor, arsia-message | — |
| ACT-§1.1-10 | 1.1 | MUST_NOT | sdk | structural | Application-defined capabilities MUST NOT use the arsiaprotocol. prefix | arsia-action-descriptor, arsia-action-discovery-response | ITV-279, ITV-280, ITV-281 |
| ACT-§1.1-11 | 1.1 | MUST | sdk | behavioural_positive | Implementations MUST reject arsiaprotocol. prefix unless it is a reserved system capability | arsia-action-descriptor, arsia-action-discovery-response | ITV-279, ITV-281 |
| ACT-§1.1-12 | 1.1 | MUST | sdk | structural | Capability segments MUST contain only ASCII letters (A-Z, a-z) and digits (0-9) | arsia-action-descriptor, arsia-message, arsia-capability-descriptor, arsia-onboarding-decision, arsia-discovery-response | — |
| ACT-§1.2-01 | 1.2 | MUST | sdk | behavioural_positive | Receiving agent MUST verify every requested capability is satisfied by the token scope | arsia-message | — |
| ACT-§1.2-02 | 1.2 | MUST_NOT | sdk | behavioural_negative | Wildcard matching MUST NOT satisfy a non-delegable capability — exact match required (condition 3) | — | INV-23, INV-24, INV-25 |
| ACT-§1.4-45 | 1.4 | MUST | sdk | behavioural_positive | Non-delegable capabilities MUST be explicitly listed as exact strings in the token scope claim | — | INV-23, INV-24, INV-25 |
| ACT-§1.4-46 | 1.4 | MUST_NOT | external | behavioural_negative | Authorization Servers MUST NOT issue tokens relying on wildcard expansion for non-delegable capabilities | — | — |
| ACT-§1.3-01 | 1.3 | MAY | sdk_enabled | informational | Receiving agent MAY grant fewer capabilities than requested (capability downgrading) | — | — |
| ACT-§1.3-02 | 1.3 | MAY | sdk | informational | Receiving agent MAY downgrade capabilities for policy, trust, or operational reasons | — | — |
| ACT-§1.3-03 | 1.3 | MUST | sdk | structural | Downgraded response MUST include effective_capabilities array in payload.result | — | ACTV-02 |
| ACT-§1.3-04 | 1.3 | MUST | sdk | behavioural_positive | effective_capabilities MUST be a subset of the original requested capabilities | — | ACTV-02 |
| ACT-§1.3-05 | 1.3 | MUST_NOT | sdk | behavioural_negative | effective_capabilities MUST NOT contain capabilities absent from the original request | — | ACTV-02 |
| ACT-§1.3-06 | 1.3 | MUST | sdk | structural | effective_capabilities array MUST contain at least one capability | — | ACTV-02 |
| ACT-§1.3-07 | 1.3 | MUST | sdk | behavioural_positive | Receiving agent MUST reject with error forbidden if no requested capability can be granted | — | ITV-282 |
| ACT-§1.3-08 | 1.3 | MUST | external | procedural | Sender MUST honour downgraded capabilities and not assume broader access | — | ACTV-02 |
| ACT-§1.3-09 | 1.3 | MUST_NOT | external | behavioural_negative | Sender MUST NOT assume broader access than declared in effective_capabilities | — | — |
| ACT-§1.3-10 | 1.3 | MUST | external | behavioural_positive | Sender MUST issue a new request to re-request a capability removed by downgrading | — | — |
| ACT-§1.3-11 | 1.3 | MUST_NOT | external | behavioural_negative | Agent MUST NOT invoke operations for capabilities not granted in effective_capabilities | — | — |
| ACT-§1.3-12 | 1.3 | MUST | sdk_enabled | procedural | Audit record MUST include both original and effective capabilities when downgrading occurs | arsia-audit-record | — |
| ACT-§1.4-01 | 1.4 | MUST_NOT | sdk | structural | Application-defined capabilities MUST NOT use the arsiaprotocol. reserved prefix | arsia-action-descriptor, arsia-action-discovery-response | ITV-283 |
| ACT-§1.4-02 | 1.4 | MUST | sdk | behavioural_positive | Implementations MUST recognise reserved system capabilities and enforce their semantics | — | — |
| ACT-§1.4-03 | 1.4 | MUST | external | behavioural_positive | arsiaprotocol.oversight.approve MUST only be granted to human oversight role agents | — | — |
| ACT-§1.4-04 | 1.4 | MUST_NOT | operational_policy | behavioural_negative | arsiaprotocol.oversight.approve MUST NOT be granted to fully autonomous agents | — | — |
| ACT-§1.4-05 | 1.4 | MUST | external | procedural | Authorization Server MUST verify additionally before issuing oversight.approve tokens | — | — |
| ACT-§1.4-06 | 1.4 | MUST | operational_policy | behavioural_positive | arsiaprotocol.broker.relay MUST only be granted to Compliance Broker agents in a declared zone | — | — |
| ACT-§1.4-07 | 1.4 | MUST_NOT | external | behavioural_negative | Agents with broker.relay MUST NOT modify contents of relayed message envelopes | — | — |
| ACT-§1.4-08 | 1.4 | MUST | external | behavioural_positive | Agents with broker.relay MUST append an audit record for every relayed message | arsia-audit-record | — |
| ACT-§1.4-09 | 1.4 | SHOULD | deployment | behavioural_positive | Access tokens with audit.read scope SHOULD have a short lifetime (max 300s recommended) | — | — |
| ACT-§1.4-10 | 1.4 | RECOMMENDED | sdk_enabled | informational | Recommended maximum lifetime for audit.read tokens is 300 seconds | — | — |
| ACT-§1.4-11 | 1.4 | MUST | deployment | behavioural_positive | Receiving agent MUST enforce record-level access controls for audit.read requests | arsia-audit-record | — |
| ACT-§1.4-12 | 1.4 | MAY | external | informational | audit.read access MAY be restricted to a specific time range or compliance profile | — | — |
| ACT-§1.4-13 | 1.4 | MUST | operational_policy | behavioural_positive | arsiaprotocol.identity.admin MUST be tightly controlled to prevent identity takeover | — | — |
| ACT-§1.4-14 | 1.4 | SHOULD | deployment | behavioural_positive | identity.admin SHOULD be restricted to infrastructure agents or human admin tools | — | — |
| ACT-§1.4-15 | 1.4 | MUST | external | behavioural_positive | Tokens with identity.admin scope MUST have the shortest practical lifetime | — | — |
| ACT-§1.4-16 | 1.4 | RECOMMENDED | external | informational | Recommended maximum lifetime for identity.admin tokens is 60 seconds | — | — |
| ACT-§1.4-17 | 1.4 | SHOULD | deployment | procedural | Authorization Server SHOULD require additional auth factors for identity.admin tokens | — | — |
| ACT-§1.4-18 | 1.4 | MUST | deployment | behavioural_positive | PII in state entries MUST be filtered or masked unless agent has GDPR authorization | — | — |
| ACT-§1.4-19 | 1.4 | SHOULD | operational_policy | behavioural_positive | state.write capability SHOULD be granted sparingly to agents with legitimate need | — | — |
| ACT-§1.4-20 | 1.4 | MUST | external | behavioural_positive | State writes MUST be logged when audit_required is true for the interaction | arsia-audit-record | — |
| ACT-§1.4-21 | 1.4 | MUST | sdk | behavioural_positive | state.purge MUST require explicit grant, not implied by state.write or wildcards | — | ITV-284 |
| ACT-§1.4-22 | 1.4 | MUST_NOT | sdk | behavioural_negative | state.purge MUST NOT be implied by arsiaprotocol.state.write or any wildcard scope (non-delegable, §1.2 condition 3) | — | ITV-284, ITV-285, INV-23 |
| ACT-§1.4-23 | 1.4 | MUST | external | procedural | Receiving agent MUST log purge request and deleted entry IDs before executing deletion | arsia-audit-record | — |
| ACT-§1.4-24 | 1.4 | MUST | sdk_enabled | behavioural_positive | state.snapshot responses MUST include timestamp and cryptographic hash for integrity | arsia-state-operations | ITV-286, ITV-287 |
| ACT-§1.4-25 | 1.4 | MAY | sdk_enabled | procedural | assets.transfer.initiate MAY require separate approval depending on amount and risk | — | — |
| ACT-§1.4-26 | 1.4 | MUST | external | behavioural_positive | Agents with transfer.initiate MUST declare supported asset types in their action registry | — | ITV-288 |
| ACT-§1.4-27 | 1.4 | MUST_NOT | external | behavioural_negative | Transfer initiator MUST NOT be the same agent that approves the transfer | — | ITV-289 |
| ACT-§1.4-28 | 1.4 | MUST | external | behavioural_positive | Authorization Server MUST enforce two-party separation for asset transfer approval | — | ITV-289 |
| ACT-§1.4-29 | 1.4 | MAY | sdk | informational | Agent MAY hold both transfer.approve and oversight.approve as a general oversight agent | — | — |
| ACT-§1.4-30 | 1.4 | MAY | sdk | informational | Asset transfer reversals are best-effort and MAY be rejected after reversal window | — | — |
| ACT-§1.4-31 | 1.4 | MUST | external | behavioural_positive | Reversal requests MUST be logged in audit trail with original transfer identifier | arsia-audit-record | — |
| ACT-§1.4-32 | 1.4 | MAY | sdk_enabled | informational | Human oversight MAY be required for escrow creation | — | — |
| ACT-§1.4-33 | 1.4 | MUST | sdk_enabled | behavioural_positive | Escrow creator MUST specify valid release_agent and timeout_at in EscrowConditions | arsia-escrow-conditions | — |
| ACT-§1.4-34 | 1.4 | SHOULD | sdk | behavioural_positive | Human oversight SHOULD be required for currency escrow releases | — | — |
| ACT-§1.4-35 | 1.4 | RECOMMENDED | operational_policy | informational | Human oversight RECOMMENDED for non-currency escrow releases above a defined threshold | — | — |
| ACT-§1.4-36 | 1.4 | MUST | external | behavioural_positive | Escrow releaser identity MUST match the release_agent field in EscrowConditions (or the arbitration_agent while DISPUTED, ARSIA-Assets.md §4.1) | — | ITV-290, ITV-591 |
| ACT-§1.4-37 | 1.4 | MUST | external | behavioural_positive | Escrow release message MUST be signed by the releasing agent's Ed25519 key | — | ITV-291, ITV-292 |
| ACT-§1.4-38 | 1.4 | MAY | sdk_enabled | informational | Human oversight MAY be required for escrow cancellation | — | — |
| ACT-§1.4-39 | 1.4 | SHOULD | deployment | behavioural_positive | Access tokens with assets.audit.read scope SHOULD have a short lifetime (max 300s) | — | — |
| ACT-§1.4-40 | 1.4 | RECOMMENDED | sdk_enabled | informational | Recommended maximum lifetime for assets.audit.read tokens is 300 seconds | — | — |
| ACT-§1.4-41 | 1.4 | MUST | deployment | behavioural_positive | Receiving agent MUST enforce record-level access controls for assets.audit.read | arsia-audit-record | — |
| ACT-§1.4-42 | 1.4 | MAY | sdk_enabled | informational | assets.audit.read MAY be restricted to specific date range, payment reference, or profile | — | — |
| ACT-§1.4-43 | 1.4 | SHOULD | sdk_enabled | behavioural_positive | arsiaprotocol.compliance.breach.notify SHOULD only be granted to controller-role agents | — | ITV-556, ITV-557 |
| ACT-§1.4-44 | 1.4 | MUST | sdk | behavioural_positive | Agents with breach.notify MUST ensure breach details are transmitted only to authorised recipients | — | — |
| ACT-§2.1-01 | 2.1 | REQUIRED | sdk | behavioural_positive | action_id field is REQUIRED in ActionDescriptor | arsia-action-descriptor | — |
| ACT-§2.1-02 | 2.1 | MUST | sdk | behavioural_positive | action_id MUST correspond to a payload.type value the agent accepts | arsia-action-descriptor | — |
| ACT-§2.1-03 | 2.1 | REQUIRED | sdk | behavioural_positive | category field is REQUIRED in ActionDescriptor | arsia-action-descriptor | ITV-168, ITV-169, ITV-170 |
| ACT-§2.1-04 | 2.1 | REQUIRED | sdk | behavioural_positive | description field is REQUIRED in ActionDescriptor | arsia-action-descriptor | — |
| ACT-§2.1-05 | 2.1 | MUST | operational_policy | behavioural_positive | ActionDescriptor description MUST be written in English | — | — |
| ACT-§2.1-06 | 2.1 | SHOULD | sdk_enabled | behavioural_positive | ActionDescriptor description SHOULD be detailed enough for human reviewer comprehension | arsia-action-descriptor | — |
| ACT-§2.1-07 | 2.1 | REQUIRED | sdk | behavioural_positive | risk_level field is REQUIRED in ActionDescriptor | arsia-action-descriptor | — |
| ACT-§2.1-08 | 2.1 | MUST | operational_policy | behavioural_positive | risk_level MUST be assigned by agent operator based on a risk assessment | — | — |
| ACT-§2.1-09 | 2.1 | MUST | sdk_enabled | behavioural_positive | risk_level MUST be consistent with agent's ai_system_classification in IdentityRecord | arsia-action-descriptor | — |
| ACT-§2.1-10 | 2.1 | SHOULD_NOT | sdk_enabled | behavioural_negative | Minimal-risk agents SHOULD NOT register actions with risk_level 7 or above | arsia-action-descriptor | — |
| ACT-§2.1-11 | 2.1 | REQUIRED | sdk | behavioural_positive | reversible field is REQUIRED in ActionDescriptor | arsia-action-descriptor | — |
| ACT-§2.1-12 | 2.1 | MUST | operational_policy | behavioural_positive | reversible field MUST accurately reflect whether the action supports rollback | — | — |
| ACT-§2.1-13 | 2.1 | REQUIRED | sdk | behavioural_positive | idempotent field is REQUIRED in ActionDescriptor | arsia-action-descriptor | — |
| ACT-§2.1-14 | 2.1 | REQUIRED | sdk | behavioural_positive | required_capabilities field is REQUIRED in ActionDescriptor | arsia-action-descriptor | — |
| ACT-§2.1-15 | 2.1 | MUST | sdk | structural | Each required_capabilities element MUST be a valid capability string per §1.1 grammar | arsia-action-descriptor | ITV-09 |
| ACT-§2.1-16 | 2.1 | MUST | sdk | behavioural_positive | Requesting agent MUST have all required_capabilities in its access token to invoke action | arsia-action-descriptor | — |
| ACT-§2.1-17 | 2.1 | MUST | sdk | structural | required_capabilities array MUST contain at least one element | arsia-action-descriptor | — |
| ACT-§2.1-18 | 2.1 | MUST | sdk | structural | Each optional_capabilities element MUST be a valid capability string per §1.1 grammar | arsia-action-descriptor | — |
| ACT-§2.1-19 | 2.1 | REQUIRED | sdk | behavioural_positive | human_oversight_required field is REQUIRED in ActionDescriptor | arsia-action-descriptor | — |
| ACT-§2.1-20 | 2.1 | MUST | sdk | procedural | When human_oversight_required is true, the descriptor demands required_before_execution (executor-policy source, Core §4.3.10.2) and the action MUST go through the pending_approval flow before execution | arsia-action-descriptor | ITV-293, ITV-641 |
| ACT-§2.1-21 | 2.1 | MUST_NOT | sdk | behavioural_negative | Agent MUST NOT execute action until approval_decision with decision approved is received | — | ITV-293 |
| ACT-§2.1-23 | 2.1 | REQUIRED | sdk | behavioural_positive | audit_required field is REQUIRED in ActionDescriptor | arsia-action-descriptor | — |
| ACT-§2.1-24 | 2.1 | MUST | sdk | procedural | When audit_required is true, every execution MUST generate an audit record | arsia-action-descriptor | — |
| ACT-§2.1-25 | 2.1 | MUST | sdk | behavioural_positive | Audit record MUST include action_id, requester identity, timestamp, params, and result | arsia-audit-record | — |
| ACT-§2.1-26 | 2.1 | OPTIONAL | sdk | informational | When audit_required is false, audit logging is OPTIONAL but compliance profile MAY require it | — | — |
| ACT-§2.1-27 | 2.1 | MAY | sdk | informational | Compliance profile MAY still require audit logging even when audit_required is false | — | — |
| ACT-§2.1-28 | 2.1 | OPTIONAL | sdk | informational | retention field is OPTIONAL in ActionDescriptor | arsia-action-descriptor | — |
| ACT-§2.1-29 | 2.1 | REQUIRED | sdk | behavioural_positive | explainability_required field is REQUIRED in ActionDescriptor | arsia-action-descriptor | — |
| ACT-§2.1-30 | 2.1 | MUST | sdk | behavioural_positive | When explainability_required is true, response MUST include payload.explanation object | arsia-action-descriptor | — |
| ACT-§2.1-31 | 2.1 | SHOULD | sdk_enabled | behavioural_positive | pending_approval message SHOULD include preliminary explanation for human oversight | arsia-explanation | — |
| ACT-§2.1-32 | 2.1 | OPTIONAL | sdk | informational | max_execution_ms field is OPTIONAL in ActionDescriptor (default 30000ms) | arsia-action-descriptor | — |
| ACT-§2.1-33 | 2.1 | MUST | sdk | procedural | Agent MUST respond with service_unavailable error if execution exceeds max_execution_ms | arsia-action-descriptor | ITV-294 |
| ACT-§2.1-34 | 2.1 | SHOULD | sdk | behavioural_positive | Actions expected to exceed max_execution_ms SHOULD use async execution pattern (§4.3) | — | — |
| ACT-§2.1-35 | 2.1 | MUST | deployment | procedural | Receiving agent MUST honour the max_execution_ms timeout | — | — |
| ACT-§2.1-36 | 2.1 | MUST_NOT | deployment | behavioural_negative | Receiving agent MUST NOT continue execution after max_execution_ms without client awareness | — | — |
| ACT-§2.1-37 | 2.1 | OPTIONAL | sdk | structural | post_execution_review_period (ISO 8601 calendar duration) is OPTIONAL; it is the executing agent's announced review period for required_post_execution | arsia-action-descriptor | ITV-638, INV-77 |
| ACT-§2.2-01 | 2.2 | MUST | operational_policy | behavioural_positive | Agent operators MUST assign risk levels consistent with the EU AI Act mapping | — | — |
| ACT-§2.2-02 | 2.2 | MUST | sdk | behavioural_positive | Implementations MUST enforce MUST-level risk-mapping requirements; violation is non-conformance | arsia-action-descriptor | — |
| ACT-§2.2-03 | 2.2 | MUST | sdk | behavioural_positive | Violation of MUST-level risk-mapping requirements constitutes a conformance failure | arsia-action-descriptor | — |
| ACT-§2.2-04 | 2.2 | MAY | sdk_enabled | informational | Risk 0-2 (minimal): audit_required MAY be false — no protocol audit obligation | — | — |
| ACT-§2.2-05 | 2.2 | SHOULD | sdk | behavioural_positive | Risk 0-2 (minimal): human_oversight_required SHOULD be false | — | ITV-295 |
| ACT-§2.2-06 | 2.2 | MAY | sdk_enabled | informational | Risk 0-2 (minimal): explainability_required MAY be false — no transparency obligation | — | — |
| ACT-§2.2-07 | 2.2 | SHOULD | sdk | behavioural_positive | Risk 3-4 (limited): audit_required SHOULD be true for traceability | — | ITV-296 |
| ACT-§2.2-08 | 2.2 | MAY | sdk_enabled | informational | Risk 3-4 (limited): human_oversight_required MAY be false | — | — |
| ACT-§2.2-09 | 2.2 | MAY | sdk_enabled | informational | Risk 3-4 (limited): explainability_required MAY be true for trust | — | — |
| ACT-§2.2-10 | 2.2 | SHOULD | sdk_enabled | behavioural_positive | Risk 3-4 agents SHOULD inform counterparties they are interacting with an AI system | — | — |
| ACT-§2.2-11 | 2.2 | MUST | sdk | behavioural_positive | Risk 5-6 (elevated): audit_required MUST be true — full audit trail mandatory | arsia-action-descriptor | ITV-08, ITV-297 |
| ACT-§2.2-12 | 2.2 | MAY | sdk_enabled | informational | Risk 5-6 (elevated): human_oversight_required MAY be true — recommended but optional | — | — |
| ACT-§2.2-13 | 2.2 | SHOULD | sdk | behavioural_positive | Risk 5-6 (elevated): explainability_required SHOULD be true | — | ITV-297 |
| ACT-§2.2-14 | 2.2 | SHOULD | operational_policy | behavioural_positive | Risk 5-6 actions SHOULD be reviewed for potential reclassification as high-risk | — | — |
| ACT-§2.2-15 | 2.2 | MUST | sdk | behavioural_positive | Risk 7-8 (high): audit_required MUST be true — full audit trail mandatory | arsia-action-descriptor | ITV-07, ITV-298 |
| ACT-§2.2-16 | 2.2 | SHOULD | sdk | behavioural_positive | Risk 7-8 (high): human_oversight_required SHOULD be true per EU AI Act Art. 14 | — | ITV-298 |
| ACT-§2.2-17 | 2.2 | MUST | sdk | behavioural_positive | Risk 7-8 (high): explainability_required MUST be true per EU AI Act Art. 13 | arsia-action-descriptor | ITV-07, ITV-298 |
| ACT-§2.2-18 | 2.2 | MUST | sdk | behavioural_positive | Risk 9-10 (critical): audit_required MUST be true — full audit trail mandatory | arsia-action-descriptor | ITV-519 |
| ACT-§2.2-19 | 2.2 | MUST | sdk | behavioural_positive | Risk 9-10 (critical): human_oversight_required MUST be true — autonomous execution prohibited | arsia-action-descriptor | ITV-133, ITV-519, ITV-520 |
| ACT-§2.2-20 | 2.2 | MUST | sdk | behavioural_positive | Risk 9-10 (critical): explainability_required MUST be true — full transparency mandatory | arsia-action-descriptor | ITV-519 |
| ACT-§2.2-21 | 2.2 | MUST_NOT | sdk | behavioural_negative | Risk 9-10 actions MUST NOT be executed without prior human approval | arsia-action-descriptor | ITV-133, ITV-520 |
| ACT-§2.2-22 | 2.2 | MAY | sdk_enabled | informational | Implementations MAY require multiple approvals for risk level 10 actions | arsia-action-descriptor | — |
| ACT-§2.3-01 | 2.3 | MUST | deployment | interoperability | Agents exposing actions MUST serve action registry at /.well-known/arsia/actions | arsia-action-discovery-response | — |
| ACT-§2.3-02 | 2.3 | MUST | deployment | structural | Action discovery response MUST be a JSON object with actions, total, limit, offset fields | arsia-action-discovery-response | ITV-53 |
| ACT-§2.3-03 | 2.3 | REQUIRED | deployment | structural | actions array of ActionDescriptor objects is REQUIRED in discovery response | arsia-action-discovery-response | ITV-53 |
| ACT-§2.3-04 | 2.3 | REQUIRED | deployment | procedural | total count of matching actions (before pagination) is REQUIRED in discovery response | arsia-action-discovery-response | ITV-53, ITV-54 |
| ACT-§2.3-05 | 2.3 | REQUIRED | deployment | structural | limit (max actions per response) is REQUIRED in discovery response | arsia-action-discovery-response | ITV-53 |
| ACT-§2.3-06 | 2.3 | REQUIRED | deployment | structural | offset (actions skipped for pagination) is REQUIRED in discovery response | arsia-action-discovery-response | ITV-53 |
| ACT-§2.3-07 | 2.3 | MUST | deployment | interoperability | Action discovery endpoint MUST support filtering and pagination query parameters | arsia-action-discovery-response | — |
| ACT-§2.3-08 | 2.3 | MUST | sdk | behavioural_positive | Discovery category filter value MUST be one of the allowed ActionDescriptor categories | arsia-action-descriptor, arsia-action-discovery-response | ITV-53 |
| ACT-§2.3-09 | 2.3 | MUST | deployment | interoperability | Multiple discovery query parameters MUST be combined with logical AND | arsia-action-discovery-response | — |
| ACT-§2.3-10 | 2.3 | SHOULD | deployment | behavioural_positive | Action discovery response SHOULD include Cache-Control and ETag caching headers | — | — |
| ACT-§2.3-11 | 2.3 | SHOULD | deployment | interoperability | Clients SHOULD respect action discovery caching headers | — | — |
| ACT-§2.3-12 | 2.3 | SHOULD | deployment | interoperability | Clients SHOULD refetch action registry on not_implemented error for a known action | — | — |
| ACT-§2.3-13 | 2.3 | SHOULD | deployment | interoperability | Action discovery endpoint SHOULD be publicly accessible without authentication | — | — |
| ACT-§2.3-14 | 2.3 | MAY | deployment | interoperability | Action discovery endpoint MAY require authentication if operator restricts visibility | — | — |
| ACT-§2.3-15 | 2.3 | MUST | deployment | interoperability | Authenticated discovery endpoint MUST return 401 Unauthorized for unauthenticated requests | — | ITV-299 |
| ACT-§2.4-01 | 2.4 | MUST | sdk | structural | Action version strings MUST follow MAJOR.MINOR format with non-negative integers | arsia-message | — |
| ACT-§2.4-02 | 2.4 | MUST | sdk | behavioural_positive | Implementations MUST process minor-version-bumped messages by ignoring unknown fields | — | ITV-300 |
| ACT-§2.4-03 | 2.4 | MUST | sdk | interoperability | Major version bump MUST be treated as a new action for capability enforcement and discovery | — | ITV-301 |
| ACT-§2.4-04 | 2.4 | MAY | deployment | interoperability | Old and new major versions MAY coexist in the action registry during migration | — | — |
| ACT-§2.4-05 | 2.4 | SHOULD | sdk_enabled | behavioural_positive | Agents SHOULD support the latest action version | — | — |
| ACT-§2.4-06 | 2.4 | MAY | sdk_enabled | informational | Agents MAY support older action versions concurrently | — | — |
| ACT-§2.4-07 | 2.4 | SHOULD | operational_policy | interoperability | Version migration period SHOULD be documented in the action's description field | — | — |
| ACT-§2.4-08 | 2.4 | MUST | sdk | interoperability | Receiving agent MUST use latest version when request omits payload.version | — | ITV-302 |
| ACT-§2.4-09 | 2.4 | MUST | sdk | procedural | Agent MUST respond with not_implemented error for unsupported payload.version values | arsia-message | ITV-301 |
| ACT-§3.2-01 | 3.2 | MUST | sdk | procedural | Agent receiving a request whose effective oversight set (with executor-policy sources) includes required_before_execution MUST follow the pending_approval procedure | arsia-message | ITV-303, ITV-640, ITV-641, ITV-642, ITV-643 |
| ACT-§3.2-02 | 3.2 | MUST_NOT | sdk | behavioural_negative | Receiving agent MUST NOT execute the action while it is held for prior approval | — | ITV-640 |
| ACT-§3.2-03 | 3.2 | MUST | sdk | procedural | Receiving agent MUST construct and send a pending_approval message with prescribed envelope fields | arsia-message | ITV-303 |
| ACT-§3.2-04 | 3.2 | MUST | sdk | structural | pending_approval payload MUST contain type, args (action_id, original_request_id, approval_deadline, approver_capability, context, risk_level), and explanation | arsia-message | ITV-86, ITV-303 |
| ACT-§3.2-05 | 3.2 | REQUIRED | sdk | structural | pending_approval args MUST include action_id from the ActionDescriptor of the held action | arsia-message | — |
| ACT-§3.2-06 | 3.2 | REQUIRED | sdk | procedural | pending_approval args MUST include original_request_id matching the original request message id | arsia-message | — |
| ACT-§3.2-07 | 3.2 | REQUIRED | sdk | structural | pending_approval args MUST include approval_deadline as an RFC 3339 timestamp with millisecond precision | arsia-message | — |
| ACT-§3.2-08 | 3.2 | MUST | sdk | behavioural_positive | approval_deadline in pending_approval args MUST equal the expires_at envelope field | — | ITV-304 |
| ACT-§3.2-09 | 3.2 | REQUIRED | sdk | structural | pending_approval args MUST include approver_capability identifying the required approval capability | arsia-message | — |
| ACT-§3.2-10 | 3.2 | MUST | sdk | behavioural_positive | approver_capability MUST be "arsiaprotocol.oversight.approve" in protocol v1.0 | arsia-message | — |
| ACT-§3.2-11 | 3.2 | REQUIRED | sdk | structural | pending_approval args MUST include context describing what will happen if the action is approved | arsia-message | — |
| ACT-§3.2-12 | 3.2 | MUST | sdk | behavioural_positive | context field MUST be written in plain language understandable by the approving natural person | arsia-message | — |
| ACT-§3.2-13 | 3.2 | MUST_NOT | sdk | structural | context field MUST NOT exceed 1024 characters | arsia-message | — |
| ACT-§3.2-14 | 3.2 | SHOULD | sdk | behavioural_positive | context field SHOULD include action nature, key parameters, and potential consequences | — | — |
| ACT-§3.2-15 | 3.2 | REQUIRED | sdk | structural | pending_approval args MUST include risk_level copied from the ActionDescriptor | arsia-message | — |
| ACT-§3.2-16 | 3.2 | OPTIONAL | sdk | structural | pending_approval payload MAY include explanation object for actions with explainability_required | arsia-message, arsia-explanation | — |
| ACT-§3.2-17 | 3.2 | RECOMMENDED | sdk | structural | Preliminary explanation is RECOMMENDED in pending_approval when explainability_required is true | arsia-message, arsia-explanation | — |
| ACT-§3.2-18 | 3.2 | SHOULD | sdk | structural | pending_approval explanation SHOULD conform to the explanation object format defined in §5.2 | arsia-message, arsia-explanation | — |
| ACT-§3.2-19 | 3.2 | MAY | sdk | structural | explanation field MAY be null or omitted when explainability_required is false | — | — |
| ACT-§3.2-20 | 3.2 | MUST | sdk | behavioural_positive | Agent MUST set approval_deadline and expires_at per the normative deadline rules | — | ITV-305 |
| ACT-§3.2-21 | 3.2 | MUST | sdk | behavioural_positive | approval_deadline MUST be in the future relative to the pending_approval message timestamp | — | ITV-305, ITV-306 |
| ACT-§3.2-22 | 3.2 | MUST_NOT | sdk | behavioural_negative | approval_deadline MUST NOT exceed 24 hours from the pending_approval message timestamp | — | ITV-307 |
| ACT-§3.2-23 | 3.2 | RECOMMENDED | sdk | informational | Approval deadlines of 60 min (risk 7-8) and 15 min (risk 9-10) are RECOMMENDED | — | — |
| ACT-§3.2-24 | 3.2 | MAY | operational_policy | informational | Agent operators MAY configure shorter or longer approval deadlines within the 24-hour upper bound | — | — |
| ACT-§3.2-25 | 3.2 | MUST | deployment | behavioural_positive | pending_approval message MUST be delivered to the original sender via ARSIA message delivery | — | — |
| ACT-§3.2-26 | 3.2 | SHOULD | deployment | interoperability | Agent SHOULD also deliver pending_approval to any registered oversight endpoints | — | — |
| ACT-§3.2-27 | 3.2 | REQUIRED | sdk | structural | pending_approval args MUST include request_payload_hash, the SHA-256 of the original request's payload | arsia-message | INV-64, ITV-640 |
| ACT-§3.2-28 | 3.2 | MUST | sdk | behavioural_negative | Receiver MUST reject a pending_approval whose payload.args has a member outside the closed field set with invalid_request | arsia-message | INV-63 |
| ACT-§3.2-29 | 3.2 | REQUIRED | sdk | structural | pending_approval MUST carry payload.obligation_resolution recording the prior-approval requirement and its sources | arsia-message | INV-65, ITV-640 |
| ACT-§3.3-01 | 3.3 | MUST | sdk | structural | approval_decision payload MUST contain type and result object with decision, approver_id, reason, and conditions | arsia-message | — |
| ACT-§3.3-02 | 3.3 | REQUIRED | sdk | structural | approval_decision result MUST include decision field as the oversight decision | arsia-message | — |
| ACT-§3.3-03 | 3.3 | MUST | sdk | behavioural_positive | decision field MUST be one of "approved" or "denied" | arsia-message | — |
| ACT-§3.3-04 | 3.3 | MUST_NOT | sdk | behavioural_negative | Action MUST NOT be executed when approval_decision carries decision "denied" | — | ITV-308 |
| ACT-§3.3-05 | 3.3 | REQUIRED | sdk | structural | approval_decision result MUST include approver_id matching the approving agent's agent-id | arsia-message | ITV-309 |
| ACT-§3.3-06 | 3.3 | MUST | sdk | behavioural_positive | approver_id MUST match the from field of the approval_decision envelope; a mismatch is rejected with invalid_request (§3.4 verification step 4) | — | ITV-309, INV-135 |
| ACT-§3.3-07 | 3.3 | OPTIONAL | sdk | informational | approval_decision result MAY include reason as human-readable text (max 512 characters) | arsia-message | — |
| ACT-§3.3-08 | 3.3 | RECOMMENDED | sdk | informational | Providing a reason is RECOMMENDED when the oversight decision is "denied" | — | — |
| ACT-§3.3-09 | 3.3 | RECOMMENDED | sdk | informational | Denial reason is strongly RECOMMENDED to help the requesting agent understand why action was blocked | — | — |
| ACT-§3.3-10 | 3.3 | OPTIONAL | sdk | structural | approval_decision result MAY include conditions array of strings attached to the approval | arsia-message | — |
| ACT-§3.3-11 | 3.3 | MUST | sdk | procedural | Executing agent MUST honour all conditions attached to the approval_decision | — | — |
| ACT-§3.3-12 | 3.3 | SHOULD | operational_policy | behavioural_positive | Implementations SHOULD document their supported approval condition formats | — | — |
| ACT-§3.3-13 | 3.3 | MUST | sdk | structural | approval_decision MUST include "arsiaprotocol.oversight.approve" in its capabilities array | arsia-message | ITV-310, ITV-532, ITV-533 |
| ACT-§3.3-14 | 3.3 | MUST | external | behavioural_positive | Receiving agent MUST verify the approver's token includes arsiaprotocol.oversight.approve scope | — | INV-133 |
| ACT-§3.3-15 | 3.3 | MUST | sdk | behavioural_positive | approval_decision from an agent without oversight.approve capability MUST be rejected as forbidden | arsia-message | ITV-311, ITV-532, ITV-533, INV-133, INV-134 |
| ACT-§3.3-16 | 3.3 | MUST | sdk | behavioural_positive | approval_decision MUST be signed by the approver's Ed25519 key, not the executing or requesting agent's key | arsia-message | ITV-312, ITV-313 |
| ACT-§3.3-17 | 3.3 | MUST | sdk | behavioural_positive | Receiving agent MUST verify the approval_decision signature per ARSIA-Identity.md §3.1 | — | INV-127, INV-128, INV-139, INV-155 |
| ACT-§3.3-18 | 3.3 | REQUIRED | sdk | structural | approval_decision result MUST include the request_payload_hash of the pending_approval decided | arsia-message | INV-66 |
| ACT-§3.4-01 | 3.4 | MUST | sdk | behavioural_negative | Executing agent MUST verify every approval_decision, approved or denied, in order — signature, token, authority, correlation and binding, deadline and pending state — before it takes effect; the first failing step gives the code | — | ITV-694, INV-127, INV-128, INV-139, INV-140, INV-152 |
| ACT-§3.4-02 | 3.4 | MUST | external | behavioural_positive | Executing agent MUST verify the approver's token includes arsiaprotocol.oversight.approve capability | — | ITV-314, INV-133 |
| ACT-§3.4-03 | 3.4 | MUST | sdk | behavioural_positive | Executing agent MUST reject the approval_decision with forbidden when arsiaprotocol.oversight.approve is missing from the token scope (exact match) or from capabilities | — | ITV-315, INV-133, INV-134 |
| ACT-§3.4-04 | 3.4 | MUST_NOT | sdk | behavioural_negative | Executing agent MUST NOT execute the action if approver lacks the required capability | — | ITV-316, INV-134 |
| ACT-§3.4-05 | 3.4 | MUST | sdk | procedural | Executing agent MUST verify the decision was received strictly before the approval_deadline, on its own clock, without clock-skew tolerance | — | ITV-317, ITV-695, INV-126 |
| ACT-§3.4-06 | 3.4 | MUST | sdk | procedural | Executing agent MUST resolve a still-pending flow as expired (Path 3) once the deadline is reached and the decisions received before it are verified | — | ITV-318, INV-126, ITV-705, ITV-707 |
| ACT-§3.4-07 | 3.4 | MUST_NOT | sdk | behavioural_negative | Executing agent MUST NOT execute an action whose approval_deadline has passed, even if approval was sent in time | — | ITV-319, INV-126 |
| ACT-§3.4-08 | 3.4 | MUST | sdk | behavioural_positive | Executing agent MUST verify approval_decision correlation_id matches a previously sent pending_approval id | arsia-message | ITV-320 |
| ACT-§3.4-09 | 3.4 | MUST | sdk | behavioural_positive | Executing agent MUST reject approval_decision with error invalid_request if no matching pending_approval exists | — | ITV-320, INV-136 |
| ACT-§3.4-10 | 3.4 | MUST_NOT | sdk_enabled | behavioural_negative | Executing agent MUST NOT execute the action if no matching pending_approval is found | — | ITV-321, INV-136 |
| ACT-§3.4-11 | 3.4 | MUST | sdk | procedural | Executing agent MUST execute the action after all verification steps pass | — | — |
| ACT-§3.4-12 | 3.4 | MUST | sdk | procedural | Executing agent MUST apply all conditions from the approval_decision to the action execution | — | — |
| ACT-§3.4-13 | 3.4 | MUST | sdk | procedural | Executing agent MUST send response to the original requester after execution completes | — | — |
| ACT-§3.4-14 | 3.4 | MUST | sdk | procedural | Executing agent MUST log request, pending_approval, approval_decision, and response in the audit trail | arsia-audit-record | ITV-694 |
| ACT-§3.4-15 | 3.4 | MUST_NOT | sdk | behavioural_negative | Executing agent MUST NOT execute the action when approval_decision decision is "denied" | — | ITV-322 |
| ACT-§3.4-16 | 3.4 | MUST | sdk | procedural | Executing agent MUST send a forbidden error to the original requester when action is denied | arsia-message | ITV-323 |
| ACT-§3.4-17 | 3.4 | MUST | sdk | behavioural_positive | Denied-action error code MUST be "forbidden" per ARSIA-Core.md §11.2 | arsia-message | ITV-323 |
| ACT-§3.4-18 | 3.4 | MUST | sdk | structural | Denied-action error details MUST include oversight_decision: "denied" to distinguish from standard auth failure | arsia-message | ITV-323, ITV-324 |
| ACT-§3.4-19 | 3.4 | MUST | sdk | procedural | Executing agent MUST log the oversight denial in the audit trail | arsia-audit-record | — |
| ACT-§3.4-20 | 3.4 | MUST_NOT | sdk | behavioural_negative | Executing agent MUST NOT execute the action when approval_deadline expires without a valid decision | — | ITV-325 |
| ACT-§3.4-21 | 3.4 | MUST | sdk | procedural | Executing agent MUST send a forbidden error to the original requester when approval deadline expires | arsia-message | ITV-325, ITV-326 |
| ACT-§3.4-22 | 3.4 | MUST | sdk | behavioural_positive | Expired-action error code MUST be "forbidden" | arsia-message | ITV-326 |
| ACT-§3.4-23 | 3.4 | MUST | sdk | structural | Expired-action error details MUST include oversight_decision: "expired" and the exceeded deadline | arsia-message | ITV-326, ITV-327 |
| ACT-§3.4-24 | 3.4 | MUST | sdk | procedural | Executing agent MUST log the approval expiry in the audit trail | arsia-audit-record | ITV-94 |
| ACT-§3.4-25 | 3.4 | MUST_NOT | sdk | behavioural_negative | Executing agent MUST NOT execute an action if approval_decision arrives after the approval_deadline | — | ITV-328, INV-126 |
| ACT-§3.4-26 | 3.4 | SHOULD | sdk | behavioural_positive | Executing agent SHOULD respond to a late approver with the code the verification determines: invalid_request with deadline_exceeded: true when no earlier step failed | arsia-message | ITV-328 |
| ACT-§3.4-27 | 3.4 | MUST | sdk | procedural | A late approval_decision MUST be logged as a rejected decision (decision_rejected) | arsia-audit-record | INV-126, INV-152 |
| ACT-§3.4-28 | 3.4 | MUST | sdk | behavioural_negative | Executing agent MUST reject an approval_decision whose request_payload_hash differs from the pending_approval's with invalid_request and MUST NOT execute the action | — | ITV-662 |
| ACT-§3.4-29 | 3.4 | MUST_NOT | sdk | behavioural_negative | Executing agent MUST NOT execute a materially changed action under an approval; a new pending_approval is required | — | — |
| ACT-§3.4-30 | 3.4 | MUST_NOT | sdk | behavioural_negative | A rejected approval_decision MUST NOT approve or deny: it is not admitted, does not count toward the required approvals, does not consume its approver, does not resolve the pending_approval and does not change a recorded outcome | — | INV-128, INV-138, ITV-696 |
| ACT-§3.4-31 | 3.4 | MUST | sdk | procedural | Executing agent MUST log every rejected approval_decision as decision_rejected, with the code of the first failing step, whether or not it replies | arsia-audit-record | INV-127, INV-136, ITV-698, INV-143 |
| ACT-§3.4-32 | 3.4 | SHOULD | sdk | behavioural_positive | Executing agent SHOULD reply to the sender of a rejected decision with an error carrying that code | — | — |
| ACT-§3.4-33 | 3.4 | MUST | sdk | behavioural_negative | Executing agent MUST verify the approver's access token — signature under the trusted issuer's configured key, exp/iat with the clock skew, sub = from, aud = to — and reject with unauthorized | — | INV-129, INV-130, INV-131, INV-132, INV-153, INV-156, INV-157 |
| ACT-§3.4-34 | 3.4 | MUST | sdk | behavioural_negative | Signature, key resolution and token are evaluated at the verification instant, not the receipt instant: deadline eligibility does not exempt authentication or a revocation applying when the decision is verified | — | INV-154 |
| ACT-§3.4-35 | 3.4 | MUST | sdk | behavioural_negative | Path 3 applies only while the pending_approval is still pending, after the decisions received before the deadline are verified; a resolved flow is never resolved again by expiry | — | ITV-705, ITV-706, ITV-707 |
| ACT-§3.4-36 | 3.4 | MUST | sdk | behavioural_negative | A duplicate or late decision is rejected with invalid_request only when no earlier verification step failed | — | INV-152 |
| ACT-§3.5-01 | 3.5 | MUST | sdk | procedural | Every oversight cycle MUST generate at least four audit records: request, pending_approval, decision, and response | arsia-audit-record | ITV-93, ITV-105, ITV-581, ITV-582, ITV-583, ITV-584, ITV-585 |
| ACT-§3.6-01 | 3.6 | MAY | sdk_enabled | procedural | Implementations MAY require multiple independent approvals for actions with risk_level 10 | — | — |
| ACT-§3.6-02 | 3.6 | OPTIONAL | sdk | informational | Multiple approval level support is OPTIONAL in ARSIA Protocol v1.0 | — | — |
| ACT-§3.6-03 | 3.6 | SHOULD | sdk | behavioural_positive | Implementations SHOULD support single-approval for all risk levels at minimum | — | — |
| ACT-§3.6-04 | 3.6 | MAY | sdk | informational | ActionDescriptor MAY include required_approvals field to support multi-approval workflows | arsia-action-descriptor | ITV-132 |
| ACT-§3.6-05 | 3.6 | OPTIONAL | sdk | procedural | required_approvals (integer, default 1) specifies the number of distinct approvals needed before execution | arsia-action-descriptor | ITV-132 |
| ACT-§3.6-06 | 3.6 | MUST | sdk | behavioural_positive | Each approval MUST come from a distinct approver with a different agent-id | — | ITV-329 |
| ACT-§3.6-07 | 3.6 | MUST | sdk | behavioural_positive | Each approval_decision verified and admitted to the flow MUST be logged as a separate audit record (Record 3); rejected decisions (decision_rejected) are not counted | arsia-audit-record | ITV-696, INV-138 |
| ACT-§3.6-08 | 3.6 | MUST | sdk_enabled | procedural | Executing agent MUST track which approvers have approved in a multi-approval flow | — | — |
| ACT-§3.6-09 | 3.6 | MUST_NOT | sdk_enabled | behavioural_negative | Executing agent MUST NOT accept duplicate approvals from the same approver | — | ITV-329, ITV-330 |
| ACT-§3.6-10 | 3.6 | SHOULD | operational_policy | behavioural_positive | Implementations SHOULD default to required_approvals: 1 and escalate only when warranted | — | — |
| ACT-§3.7-01 | 3.7 | MUST | sdk | procedural | Agent MUST proceed to execution without pending_approval when the effective oversight set does not include required_before_execution | — | ITV-331, ITV-332, ITV-644 |
| ACT-§3.7-02 | 3.7 | MUST | sdk | behavioural_positive | When the effective audit obligation is true, execution without prior approval MUST generate at least two audit records (request and terminal response or error) | arsia-audit-record | ITV-644 |
| ACT-§3.7-03 | 3.7 | MUST_NOT | sdk | behavioural_negative | Agent MUST NOT send pending_approval for a request whose effective oversight set does not include required_before_execution | — | ITV-332, ITV-644 |
| ACT-§3.7-05 | 3.7 | MUST | sdk | procedural | Receiving agent MUST resolve the effective obligations, including executor-policy sources, before any effect of the action | — | ITV-640, ITV-641, ITV-642, ITV-643 |
| ACT-§3.9-01 | 3.9.1 | MUST | sdk | procedural | With a post-execution mode in the effective set, the executing agent MUST establish its review configuration (review endpoint, escalation destination, review period for required_post_execution) before any effect | — | ITV-645, ITV-646 |
| ACT-§3.9-02 | 3.9.1 | MUST | sdk | behavioural_negative | A missing review-configuration element MUST cause rejection with invalid_request / obligation_conflict; the action is not executed | — | ITV-647, ITV-648, ITV-649 |
| ACT-§3.9-03 | 3.9.3 | MUST | sdk | behavioural_positive | Review notices, review decisions and overdue notices MUST be signed by their sender, and their receivers MUST verify the signature | arsia-message | ITV-628, ITV-629, ITV-630, ITV-657 |
| ACT-§3.9-04 | 3.9.3 | MUST | sdk | procedural | When a review is opened, the executing agent MUST send a review-pending event to its review endpoint | arsia-message | ITV-628, ITV-645, ITV-674 |
| ACT-§3.9-05 | 3.9.3 | MUST | sdk | behavioural_negative | Before recording a review decision the executing agent MUST verify signature (unauthorized), token (unauthorized), authority (forbidden) and correlation and binding (invalid_request), in that order | arsia-message | ITV-657, ITV-658, ITV-659, ITV-660, INV-68, INV-69, ITV-708 |
| ACT-§3.9-06 | 3.9.3 | MUST | sdk | behavioural_negative | A review decision that fails verification is not recorded as a decision and MUST be logged as decision_rejected | arsia-audit-record | ITV-657, ITV-658, ITV-659, ITV-660 |
| ACT-§3.9-07 | 3.9.3 | MUST_NOT | sdk | behavioural_negative | A later decision for the same review MUST NOT change the recorded outcome; it is logged as decision_rejected | — | ITV-656 |
| ACT-§3.9-08 | 3.9.3 | MUST | sdk | procedural | For each overdue obligation the executing agent MUST send a review-overdue event to its escalation destination | arsia-message | ITV-630, ITV-653, ITV-674 |
| ACT-§3.9-09 | 3.9.4 | MUST | sdk | behavioural_positive | Lateness depends only on the deadline (inclusive) and the receipt instant; the agent MUST record pending overdue facts and send their notices before recording a late decision | arsia-audit-record | ITV-651, ITV-652 |
| ACT-§3.9-10 | 3.9.4 | MUST | sdk | behavioural_positive | At an obligation deadline without a verified decision the executing agent MUST append a review_overdue record, independent of the escalation | arsia-audit-record | ITV-633, ITV-653 |
| ACT-§3.9-11 | 3.9.4 | MUST | sdk | procedural | Escalation delivery follows Core §11.3 (server-error backoff, Retry-After for rate_limited, at most 3 retries); its result is appended as review_escalation, and a failure also produces a compliance_warning | arsia-audit-record | ITV-634, ITV-635, ITV-653, ITV-654, ITV-655 |
| ACT-§3.9-12 | 3.9.4 | MUST | sdk | procedural | On an objected review decision the executing agent MUST start the operator's remediation procedure; the execution's terminal state and records never change | — | ITV-661 |
| ACT-§3.9-13 | 3.9.4 | MAY | sdk_enabled | informational | Remediation of a reversible action MAY use rollback (§4.2) under its own authorization | — | — |
| ACT-§4.1-01 | 4.1 | MUST | sdk | behavioural_positive | COMPLETED state MUST generate an audit record when ActionDescriptor has audit_required: true | arsia-audit-record | — |
| ACT-§4.1-02 | 4.1 | MUST | sdk | behavioural_positive | COMPLETED response MUST include payload.explanation when explainability_required is true | arsia-explanation | ACTV-01 |
| ACT-§4.1-03 | 4.1 | MUST | sdk | behavioural_positive | FAILED state MUST generate an audit record when ActionDescriptor has audit_required: true | arsia-audit-record | — |
| ACT-§4.1-04 | 4.1 | MUST | sdk | behavioural_positive | FAILED state error message MUST include an appropriate error code and failure description | arsia-message | — |
| ACT-§4.1-05 | 4.1 | MUST | sdk | behavioural_positive | ROLLED_BACK state MUST generate a rollback audit record | arsia-audit-record | — |
| ACT-§4.2-01 | 4.2 | SHOULD | sdk_enabled | behavioural_positive | Executing agent SHOULD support rollback for actions with reversible: true in the ActionDescriptor | arsia-action-descriptor | ACTV-03 |
| ACT-§4.2-02 | 4.2 | MUST | operational_policy | procedural | Agents MUST document which actions support rollback and under what conditions | — | ACTV-03 |
| ACT-§4.2-03 | 4.2 | MUST | sdk | behavioural_positive | Rollback request payload.args MUST include original_message_id of the completed action response | — | ACTV-03 |
| ACT-§4.2-04 | 4.2 | MUST | sdk | behavioural_negative | Agent MUST respond with error not_implemented when rollback is requested for a non-reversible action | — | ITV-333 |
| ACT-§4.2-05 | 4.2 | MAY | sdk_enabled | behavioural_positive | Implementations MAY define a rollback window limiting the time after execution during which rollback is possible | — | — |
| ACT-§4.2-06 | 4.2 | MUST | sdk | behavioural_negative | Agent MUST respond with error conflict when rollback is requested after the rollback window has elapsed | — | ITV-334 |
| ACT-§4.2-07 | 4.2 | MAY | sdk_enabled | behavioural_positive | Executing agent MAY perform partial rollback when full reversal is not possible | arsia-message | — |
| ACT-§4.2-08 | 4.2 | MUST | sdk | behavioural_positive | Partial rollback response MUST include details with partial_rollback, rolled_back, and not_rolled_back lists | arsia-message | ITV-85 |
| ACT-§4.2-09 | 4.2 | MUST | sdk | behavioural_negative | Rollback of an already ROLLED_BACK action MUST produce error conflict with already_rolled_back: true | arsia-message | ITV-335 |
| ACT-§4.2-10 | 4.2 | SHOULD | sdk_enabled | behavioural_positive | Rollback of actions that required human oversight SHOULD also require oversight unless explicitly bypassed | — | — |
| ACT-§4.2-11 | 4.2 | MUST | sdk | behavioural_positive | Successful rollback MUST generate an audit record with event_type: "rollback" carrying original_message_id, action_id and partial_rollback | arsia-audit-record | ITV-99, INV-50 |
| ACT-§4.2-12 | 4.2 | REQUIRED | sdk | structural | original_message_id, action_id and partial_rollback extension fields are REQUIRED on every rollback audit record | arsia-audit-record | ITV-99, INV-50 |
| ACT-§4.3-01 | 4.3 | MUST | sdk | behavioural_positive | Executing agent MUST cease execution and release all resources when the timeout is exceeded | — | — |
| ACT-§4.3-02 | 4.3 | MUST | sdk | behavioural_positive | Executing agent MUST respond with error code service_unavailable on action timeout | arsia-message | ITV-336 |
| ACT-§4.3-03 | 4.3 | SHOULD | sdk | behavioural_positive | Timeout error response SHOULD include timeout_ms and elapsed_ms in the details object | — | ITV-336 |
| ACT-§4.3-04 | 4.3 | SHOULD | sdk_enabled | behavioural_positive | Agent SHOULD attempt rollback of partial side effects on timeout for reversible actions | — | — |
| ACT-§4.3-05 | 4.3 | MUST | sdk | behavioural_positive | Agent MUST document partial execution in the audit record when rollback of timed-out side effects is not possible | arsia-audit-record | ITV-337 |
| ACT-§4.3-06 | 4.3 | SHOULD | sdk_enabled | procedural | Long-running actions exceeding max_execution_ms SHOULD use the asynchronous execution pattern | arsia-message | — |
| ACT-§4.3-07 | 4.3 | MUST | sdk | structural | Asynchronous status polling status field MUST be one of "running", "completed", or "failed" | arsia-message | — |
| ACT-§4.3-08 | 4.3 | MUST | sdk | behavioural_positive | The retriever of a terminal result MUST verify its signature and its binding to the execution | — | ITV-665, ITV-666 |
| ACT-§4.3-09 | 4.3 | MUST_NOT | sdk | behavioural_negative | The retriever MUST NOT reject a retrieved terminal result only because its ts lies outside the clock-skew tolerance | — | ITV-665, ITV-666 |
| ACT-§4.4-01 | 4.4 | MUST | deployment | behavioural_positive | Actions MUST be executed with isolation guarantees commensurate with their risk level | — | — |
| ACT-§4.4-02 | 4.4 | SHOULD | deployment | behavioural_positive | Risk 0-4 actions SHOULD use an isolated execution context (separate process or container) | — | — |
| ACT-§4.4-03 | 4.4 | SHOULD | deployment | behavioural_positive | Risk 0-4 actions SHOULD have filesystem access limited to the designated working directory | — | — |
| ACT-§4.4-04 | 4.4 | NOT_RECOMMENDED | deployment | behavioural_negative | Risk 0-4 host filesystem access outside the agent's data directory is NOT RECOMMENDED | — | — |
| ACT-§4.4-05 | 4.4 | MUST | deployment | behavioural_positive | Risk 5-7 actions MUST use an isolated execution context (separate process or container required) | — | — |
| ACT-§4.4-06 | 4.4 | MUST | deployment | behavioural_positive | Risk 5-7 execution process or container MUST have a unique identity for audit trail purposes | — | — |
| ACT-§4.4-07 | 4.4 | SHOULD | deployment | behavioural_positive | Risk 5-7 network egress SHOULD be restricted to endpoints declared in the action's configuration | — | — |
| ACT-§4.4-08 | 4.4 | SHOULD | operational_policy | procedural | Permitted egress endpoints for risk 5-7 SHOULD be documented in the ActionDescriptor or supplementary docs | — | — |
| ACT-§4.4-09 | 4.4 | SHOULD | deployment | behavioural_positive | Risk 5-7 execution memory limit SHOULD be set | — | — |
| ACT-§4.4-10 | 4.4 | MUST | deployment | behavioural_positive | Risk 5-7 memory limit MUST be sufficient for normal operation of the action | — | — |
| ACT-§4.4-11 | 4.4 | MUST | deployment | behavioural_negative | Risk 5-7 memory limit MUST prevent unbounded memory consumption | — | — |
| ACT-§4.4-12 | 4.4 | MUST | deployment | behavioural_positive | Risk 8-10 actions MUST use an isolated execution context with explicit, documented resource limits | — | — |
| ACT-§4.4-13 | 4.4 | REQUIRED | deployment | behavioural_positive | Risk 8-10 actions REQUIRE container-level isolation (Docker or OCI-compliant runtime) | — | — |
| ACT-§4.4-14 | 4.4 | MUST | deployment | behavioural_positive | Risk 8-10 container MUST have a unique identity for audit trail purposes | — | — |
| ACT-§4.4-15 | 4.4 | MUST | deployment | behavioural_positive | Risk 8-10 CPU limit MUST be set to prevent the action from monopolizing host CPU | — | — |
| ACT-§4.4-16 | 4.4 | SHOULD | operational_policy | procedural | Risk 8-10 CPU limit SHOULD be documented in supplementary documentation | — | — |
| ACT-§4.4-17 | 4.4 | MUST | deployment | behavioural_negative | Risk 8-10 CPU limit MUST prevent the action from monopolizing host CPU resources | — | — |
| ACT-§4.4-18 | 4.4 | MUST | deployment | behavioural_positive | Risk 8-10 memory limit MUST be set | — | — |
| ACT-§4.4-19 | 4.4 | SHOULD | operational_policy | procedural | Risk 8-10 memory limit SHOULD be documented in supplementary documentation | — | — |
| ACT-§4.4-20 | 4.4 | MUST | deployment | behavioural_negative | Risk 8-10 memory limit MUST prevent the action from exhausting host memory | — | — |
| ACT-§4.4-21 | 4.4 | MUST | deployment | behavioural_positive | Risk 8-10 out-of-memory conditions MUST be caught and reported as execution failures, not host crashes | — | — |
| ACT-§4.4-22 | 4.4 | MUST | deployment | behavioural_negative | Risk 8-10 network egress MUST be restricted to declared endpoints only | — | — |
| ACT-§4.4-23 | 4.4 | MUST_NOT | deployment | behavioural_negative | Risk 8-10 actions MUST NOT make outbound calls to endpoints not in the action's configuration | — | — |
| ACT-§4.4-24 | 4.4 | SHOULD | deployment | procedural | Risk 8-10 implementations SHOULD use network policy enforcement (e.g., Kubernetes NetworkPolicy) | — | — |
| ACT-§4.4-25 | 4.4 | MUST_NOT | deployment | behavioural_negative | Risk 8-10 actions MUST NOT have write access to host filesystem, agent config, or other actions' data | — | — |
| ACT-§4.4-26 | 4.4 | MUST | deployment | behavioural_positive | Risk 8-10 temporary storage MUST be bounded and cleaned up after execution | — | — |
| ACT-§4.4-27 | 4.4 | MUST | deployment | behavioural_positive | Risk 8-10 execution duration MUST be bounded by max_execution_ms from the ActionDescriptor | arsia-action-descriptor | — |
| ACT-§4.4-28 | 4.4 | MUST | deployment | behavioural_positive | Risk 8-10 container runtime MUST enforce the max_execution_ms timeout limit | arsia-action-descriptor | — |
| ACT-§4.4-29 | 4.4 | MUST | deployment | behavioural_positive | Risk 8-10 container MUST be terminated if the action exceeds the timeout | — | — |
| ACT-§5.1-01 | 5.1 | MUST | sdk | behavioural_positive | Explanation object MUST be provided when explainability_required is true at action or compliance level | arsia-explanation | — |
| ACT-§5.1-02 | 5.1 | MUST | sdk | behavioural_positive | Every response MUST include payload.explanation when ActionDescriptor has explainability_required: true | arsia-action-descriptor, arsia-explanation | — |
| ACT-§5.1-03 | 5.1 | MUST | sdk | behavioural_positive | Compliance-level explainability_required: true MUST override ActionDescriptor and require payload.explanation | arsia-compliance-field, arsia-explanation | ACTV-01 |
| ACT-§5.1-04 | 5.1 | SHOULD | sdk_enabled | behavioural_positive | pending_approval message SHOULD include preliminary explanation in payload.explanation for oversight actions | — | ITV-338 |
| ACT-§5.1-05 | 5.1 | MAY | sdk_enabled | behavioural_positive | Agents MAY voluntarily include an explanation in any response even when not required | — | — |
| ACT-§5.2-01 | 5.2 | REQUIRED | sdk | structural | reasoning field (string, max 4096 chars) is REQUIRED in the explanation object | arsia-explanation | — |
| ACT-§5.2-02 | 5.2 | MUST | operational_policy | behavioural_positive | reasoning MUST be written in plain language understandable by a non-technical person | arsia-explanation | ACTV-01 |
| ACT-§5.2-03 | 5.2 | SHOULD | sdk_enabled | behavioural_positive | reasoning SHOULD describe inputs considered, logic applied, and conclusion reached | — | — |
| ACT-§5.2-04 | 5.2 | MUST_NOT | operational_policy | behavioural_negative | reasoning MUST NOT contain raw model outputs, token probabilities, or non-human-readable data | — | — |
| ACT-§5.2-05 | 5.2 | REQUIRED | sdk | structural | confidence field (number, 0.0–1.0) is REQUIRED in the explanation object | arsia-explanation | — |
| ACT-§5.2-06 | 5.2 | MUST | operational_policy | behavioural_positive | confidence MUST reflect the agent's actual assessment of decision certainty | arsia-explanation | ACTV-01 |
| ACT-§5.2-07 | 5.2 | MUST_NOT | operational_policy | behavioural_negative | confidence MUST NOT be hardcoded to a fixed value | — | — |
| ACT-§5.2-08 | 5.2 | SHOULD | sdk_enabled | behavioural_positive | Agent SHOULD use a calibrated estimate for confidence when internal model produces no score | — | — |
| ACT-§5.2-09 | 5.2 | REQUIRED | sdk | structural | inputs_used field (array of strings) is REQUIRED in the explanation object | arsia-explanation | ACTV-01 |
| ACT-§5.2-10 | 5.2 | SHOULD | sdk_enabled | behavioural_positive | Each inputs_used entry SHOULD be traceable to a specific data source, state entry, or external input | — | — |
| ACT-§5.2-11 | 5.2 | SHOULD | sdk_enabled | procedural | Implementations SHOULD use a consistent naming convention for input identifiers to aid auditing | — | — |
| ACT-§5.2-12 | 5.2 | OPTIONAL | sdk | structural | alternatives_considered field (array of objects) is OPTIONAL in the explanation object | arsia-explanation | — |
| ACT-§5.2-13 | 5.2 | RECOMMENDED | sdk_enabled | structural | alternatives_considered is RECOMMENDED for actions with risk_level 7 or above | arsia-explanation | — |
| ACT-§5.2-14 | 5.2 | MUST | sdk | structural | Each alternatives_considered element MUST contain option, reason_rejected, and confidence fields | arsia-explanation | — |
| ACT-§5.2-15 | 5.2 | REQUIRED | sdk | structural | option field (string) is REQUIRED in each alternatives_considered element | arsia-explanation | — |
| ACT-§5.2-16 | 5.2 | REQUIRED | sdk | structural | reason_rejected field (string) is REQUIRED in each alternatives_considered element | arsia-explanation | — |
| ACT-§5.2-17 | 5.2 | REQUIRED | sdk | structural | confidence field (number, 0.0–1.0) is REQUIRED in each alternatives_considered element | arsia-explanation | — |
| ACT-§5.2-18 | 5.2 | OPTIONAL | sdk | structural | model_version field (string) is OPTIONAL in the explanation object | arsia-explanation | — |
| ACT-§5.2-19 | 5.2 | SHOULD | sdk_enabled | behavioural_positive | model_version SHOULD include a model name and a version or commit hash | — | — |
| ACT-§5.2-20 | 5.2 | OPTIONAL | sdk | structural | decision_timestamp field (RFC 3339, millisecond precision, UTC) is OPTIONAL in the explanation object | arsia-explanation | — |
| ACT-§5.2-21 | 5.2 | MUST | sdk | behavioural_positive | decision_timestamp MUST be earlier than or equal to the message's ts value | arsia-explanation | — |
| ACT-§5.3-01 | 5.3 | MUST | sdk | behavioural_positive | Explanation object MUST be included in the audit record as part of the payload | arsia-audit-record | ITV-338 |
| ACT-§5.3-02 | 5.3 | MUST | sdk | behavioural_positive | Both preliminary and final explanations MUST be preserved in the audit trail for oversight actions | — | ITV-338 |
| ACT-§6-01 | 6 | MUST | sdk | interoperability | Conformant implementations MUST pass all conformance tests at the applicable level | arsia-message | — |
| ACT-§6-02 | 6 | MUST | sdk | structural | Capability rejection error details MUST include required_capabilities and provided_capabilities arrays | arsia-message | — |
| ACT-§6-03 | 6 | MUST_NOT | sdk | behavioural_negative | pending_approval response MUST NOT contain the action result | arsia-message | — |
| ACT-§6-04 | 6 | MUST | sdk | structural | pending_approval payload.type MUST be "arsiaprotocol.oversight/pending" | arsia-message | — |
| ACT-§6-05 | 6 | MUST | sdk | behavioural_positive | pending_approval args MUST include action_id, original_request_id, approval_deadline, approver_capability, context, and risk_level | arsia-message | — |
| ACT-§6-06 | 6 | MUST | sdk | behavioural_positive | pending_approval correlation_id MUST equal the original request message id | arsia-message | — |
| ACT-§6-07 | 6 | MUST | sdk | behavioural_positive | pending_approval expires_at envelope field MUST equal the approval_deadline value | — | ITV-339 |
| ACT-§6-08 | 6 | MUST | sdk | behavioural_positive | Denied-action error details MUST include oversight_decision, approver_id, and denial reason | arsia-message | ITV-323, ITV-324, ITV-340 |
| ACT-§6-09 | 6 | MUST | sdk | behavioural_positive | Expired-action error details MUST include oversight_decision: "expired" and the exceeded deadline | arsia-message | ITV-326, ITV-327, ITV-341 |

## Coverage Gaps

Generated: 2026-07-22 (Draft-02 regeneration — header-driven parser, reproducible via scripts/check_consistency.py companion tooling)

### Summary

| Metric | Count |
|--------|------:|
| Total requirements | 357 |
| Schema ≠ — | 166 |
| Vector ≠ — | 151 |
| Both ≠ — | 78 |
| Both = — (gaps) | 118 |

### Per-section breakdown

| § | Total | Schema ≠ — | Vector ≠ — | Both ≠ — | Both = — |
|---|-------|-----------|-----------|---------|---------|
| 1 | 72 | 21 | 26 | 8 | 33 |
| 2 | 82 | 48 | 28 | 19 | 25 |
| 3 | 111 | 54 | 72 | 36 | 21 |
| 4 | 55 | 17 | 15 | 8 | 31 |
| 5 | 28 | 18 | 7 | 5 | 8 |
| 6 | 9 | 8 | 3 | 2 | 0 |

## Draft-02 Delta (normative changes traced)

| Change | Anchor | Schema | Vectors |
|---|---|---|---|
| §1.4 = closed normative registry; +echo/health/onboarding.evaluate/broker.use | §1.4 | descriptor registry rule | ITV-568, ITV-281 |
| Reserved namespace non-delegable (wildcard never matches) | §1.2 c3, §1.4 | — | ITV-567; harness R3 |
| Example capabilities de-reserved (code.review etc.) | §1.1 exs | capability-policy desc | 16 vector renames |
| pending_approval/approval_decision: root_request_id rows; §3.4 root check; duplicate/late rules | §3.2-§3.4 | arsia-message | regenerated corpus |
| descriptor `retention` duration override (upward only) | §2.1 | action-descriptor | — |
| NEW `supported_versions` on ActionDescriptor; single-entry migration | §2.1, §2.4 | descriptor + discovery | — |
| risk_level minimum 0 in pending-approval args | §2.1/§3.2 | arsia-message | — |
| async: one mechanism, two surfaces (202+Location ≡ status_url) | §4.3 | — | — |
| risk-level retention-floor claim removed | §3.5 | — | — |
| approval_decision verification in one order for approved and denied (signature, token, authority, binding incl. approver_id, deadline); deadline on the receipt instant without skew; rejected decisions logged as decision_rejected and never admitted; Path 3 only while pending (A-57) | §3.2-§3.6, §3.9.3, state machine | audit-record | ITV-694..696, ITV-705..708, INV-126..140, INV-152..157; harness R15 |
