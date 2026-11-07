<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->
# ARSIA-Routing — Requirements Traceability Matrix

| ID | § | Modal | Layer | Kind | Requirement | Schema | Vector | Evidence |
|----|---|-------|-------|------|-------------|--------|--------|----------|
| ROUTE-§1-01 | 1 | MUST | sdk | procedural | All implementations MUST follow the normative topology determination logic defined in the routing model | — | — | untested(no-reference-model) |
| ROUTE-§1.1-01 | 1.1 | MUST | sdk | behavioural_positive | Each agent MUST have exactly one inbox endpoint for receiving messages | arsia-discovery-response | — | schema-ref:arsia-discovery-response; untested(structural-only) |
| ROUTE-§1.1-02 | 1.1 | MUST | deployment | behavioural_positive | The inbox endpoint MUST be served over TLS | — | — | out-of-repo(transport) |
| ROUTE-§1.1-03 | 1.1 | MUST | deployment | behavioural_positive | The inbox endpoint MUST require a valid access token or DPoP-bound token on every request | — | — | out-of-repo(transport) |
| ROUTE-§1.1-04 | 1.1 | MUST_NOT | sdk | behavioural_negative | Implementations MUST NOT use federated routing in ARSIA Protocol v1.0 | — | ITV-489 | struct:ITV-489; untested(structural-only) |
| ROUTE-§1.1-05 | 1.1 | MUST | sdk | structural | The data_residency field MUST contain an ISO 3166-1 alpha-2 or recognised regional code identifying the processing zone | arsia-message, arsia-compliance-field | ITV-23 | schema-ref:arsia-message; schema-ref:arsia-compliance-field; struct:ITV-23 |
| ROUTE-§1.1-06 | 1.1 | MUST | sdk | behavioural_positive | Messages with a data_residency constraint MUST be routed through a Compliance Broker within the declared zone | arsia-message | RTV-01 | schema-ref:arsia-message; struct:RTV-01; crypto:RTV-01 |
| ROUTE-§1.1-07 | 1.1 | MUST_NOT | sdk | behavioural_negative | Messages MUST NOT be sent if no compliant broker is available for the required residency zone | arsia-message | — | schema-ref:arsia-message; untested(structural-only) |
| ROUTE-§1.1-08 | 1.1 | MUST_NOT | external | behavioural_negative | Compliance Brokers MUST NOT modify the message envelope contents | — | ITV-490 | struct:ITV-490; untested(structural-only) |
| ROUTE-§1.1-09 | 1.1 | MUST | external | behavioural_positive | The sender's digital signature MUST remain valid end-to-end through broker relay | arsia-message | ITV-490 | schema-ref:arsia-message; struct:ITV-490; untested(structural-only) |
| ROUTE-§1.1-10 | 1.1 | MUST_NOT | external | behavioural_negative | Compliance Brokers MUST NOT read or log message payload contents | — | — | out-of-repo(external-party) |
| ROUTE-§1.1-11 | 1.1 | MAY | external | informational | Brokers MAY record the payload_hash for audit purposes | arsia-audit-record | — | — |
| ROUTE-§1.2.1-01 | 1.2.1 | MUST | sdk_enabled | behavioural_positive | The access token aud claim MUST equal the recipient's agent-id | arsia-jwt-claims | — | schema-ref:arsia-jwt-claims; untested(structural-only) |
| ROUTE-§1.2.1-02 | 1.2.1 | MUST | sdk_enabled | behavioural_positive | The access token sub claim MUST equal the sender's agent-id | arsia-jwt-claims | — | schema-ref:arsia-jwt-claims; untested(structural-only) |
| ROUTE-§1.2.1-03 | 1.2.1 | MUST | sdk_enabled | behavioural_positive | The access token scope claim MUST include all capabilities listed in the message | arsia-jwt-claims | — | schema-ref:arsia-jwt-claims; untested(structural-only) |
| ROUTE-§1.2.1-04 | 1.2.1 | MUST | sdk | behavioural_positive | Direct routing MUST be sufficient for Core conformance level | — | — | untested(integration) |
| ROUTE-§1.2.2-01 | 1.2.2 | MUST | sdk | behavioural_positive | Sender MUST route data_residency messages through a broker within the declared zone | arsia-message | ITV-491 | schema-ref:arsia-message; struct:ITV-491; untested(structural-only) |
| ROUTE-§1.2.2-02 | 1.2.2 | MUST_NOT | sdk | behavioural_negative | Sender MUST NOT bypass brokered routing even when direct connectivity is available | — | ITV-491 | struct:ITV-491; untested(structural-only) |
| ROUTE-§1.2.2-03 | 1.2.2 | MAY | deployment | informational | The broker registry MAY be hosted by recipient, dedicated service, or sender's organisation | — | — | — |
| ROUTE-§1.2.2-04 | 1.2.2 | MUST | external | behavioural_positive | Selected broker MUST declare the arsiaprotocol.broker.relay capability | arsia-discovery-response | — | schema-ref:arsia-discovery-response; untested(structural-only) |
| ROUTE-§1.2.2-05 | 1.2.2 | MUST | external | behavioural_positive | Selected broker MUST have a jurisdiction satisfying the required residency zone | arsia-broker-entry | ITV-05 | schema-ref:arsia-broker-entry; struct:ITV-05; untested(structural-only) |
| ROUTE-§1.2.2-06 | 1.2.2 | MUST | sdk | behavioural_positive | The broker access token MUST include the arsiaprotocol.broker.relay capability | arsia-jwt-claims | — | schema-ref:arsia-jwt-claims; untested(structural-only) |
| ROUTE-§1.2.2-07 | 1.2.2 | MUST | external | behavioural_positive | Broker MUST reject messages with service_unavailable if its jurisdiction does not match the required zone | arsia-broker-entry, arsia-message | ITV-80 | schema-ref:arsia-broker-entry; schema-ref:arsia-message; struct:ITV-80; untested(structural-only) |
| ROUTE-§1.2.2-08 | 1.2.2 | MUST_NOT | external | behavioural_negative | Broker MUST NOT modify the message envelope during relay | — | ITV-492 | struct:ITV-492; untested(structural-only) |
| ROUTE-§1.2.2-09 | 1.2.2 | MUST_NOT | external | behavioural_negative | Broker MUST NOT log payload contents during relay | — | — | out-of-repo(external-party) |
| ROUTE-§1.2.2-10 | 1.2.2 | MUST_NOT | sdk | behavioural_negative | Sender MUST NOT send a message if no eligible broker exists for the required zone | arsia-message | — | schema-ref:arsia-message; untested(structural-only) |
| ROUTE-§1.2.2-11 | 1.2.2 | MUST | sdk | behavioural_positive | Sender MUST return a service_unavailable error when no eligible broker is available | arsia-message | — | schema-ref:arsia-message; untested(structural-only) |
| ROUTE-§1.2.2-12 | 1.2.2 | SHOULD | sdk | behavioural_positive | T_e2e SHOULD be sender-constrained with DPoP (RFC 9449) under the checks of Identity §3.3 (single-use jti, check 11 acceptance window, recipient nonce when required, §2.3.3) | — | — | — |
| ROUTE-§1.2.3-01 | 1.2.3 | MUST_NOT | sdk | behavioural_negative | Agents MUST NOT use federated routing in v1.0 | — | ITV-493 | struct:ITV-493; untested(structural-only) |
| ROUTE-§1.2.3-02 | 1.2.3 | MUST | sdk | procedural | Cross-organisation routing MUST use brokered routing with a shared broker | — | ITV-494 | struct:ITV-494; untested(structural-only) |
| ROUTE-§1.2.3-03 | 1.2.3 | MUST | operational_policy | procedural | Both organisations MUST agree on a single shared broker within any applicable residency zone | — | — | out-of-repo(operator) |
| ROUTE-§1.3-01 | 1.3 | MUST | sdk | procedural | Sending agents MUST implement the topology determination procedure or equivalent logic | — | — | untested(no-reference-model) |
| ROUTE-§1.3-02 | 1.3 | MUST | sdk | procedural | Topology determination MUST be evaluated for every outbound message | — | — | untested(no-reference-model) |
| ROUTE-§1.3-03 | 1.3 | MUST_NOT | sdk | behavioural_negative | Topology determination results MUST NOT be cached across messages | — | — | untested(no-reference-model) |
| ROUTE-§1.3-04 | 1.3 | MUST | sdk | behavioural_positive | Messages with data_residency MUST use brokered routing even if both agents share the same zone | — | ITV-495 | struct:ITV-495; untested(structural-only) |
| ROUTE-§1.4-01 | 1.4 | MUST | sdk | procedural | Sender MUST select one broker from available candidates when brokered routing is required | — | — | untested(no-reference-model) |
| ROUTE-§1.4-02 | 1.4 | SHOULD | sdk | procedural | Sender SHOULD evaluate broker selection criteria in priority order | — | — | — |
| ROUTE-§1.4-03 | 1.4 | SHOULD | sdk | behavioural_positive | The first distinguishing criterion SHOULD determine broker selection | — | — | — |
| ROUTE-§1.4-04 | 1.4 | SHOULD | sdk | behavioural_positive | Sender SHOULD prefer the broker with lowest measured or estimated latency | — | — | — |
| ROUTE-§1.4-05 | 1.4 | MAY | sdk | informational | Latency MAY be measured via health checks, geographic proximity, or active probes | — | — | — |
| ROUTE-§1.4-06 | 1.4 | SHOULD | sdk | behavioural_positive | Sender SHOULD prefer brokers reporting healthy status in broker discovery | arsia-broker-entry | ITV-05 | — |
| ROUTE-§1.4-07 | 1.4 | SHOULD | sdk | behavioural_positive | Brokers reporting degraded health SHOULD be deprioritised in selection | arsia-broker-entry | — | — |
| ROUTE-§1.4-08 | 1.4 | MUST | sdk | behavioural_positive | Brokers reporting unhealthy status MUST be excluded from selection | arsia-broker-entry | ITV-167 | schema-ref:arsia-broker-entry; struct:ITV-167; untested(structural-only) |
| ROUTE-§1.4-09 | 1.4 | SHOULD | sdk | behavioural_positive | Sender SHOULD prefer brokers with lowest current_load_pct when load data is available | arsia-broker-entry | — | — |
| ROUTE-§1.4-10 | 1.4 | MUST | sdk | behavioural_positive | Sender MUST select randomly among equal candidates using uniform distribution | — | — | untested(no-reference-model) |
| ROUTE-§1.4-11 | 1.4 | MAY | sdk | informational | Implementations MAY define custom broker selection strategies | — | — | — |
| ROUTE-§1.4-12 | 1.4 | MUST | sdk | behavioural_positive | Custom selection strategies MUST still enforce the data residency zone constraint | — | ITV-496 | struct:ITV-496; untested(structural-only) |
| ROUTE-§1.4-13 | 1.4 | MUST | sdk | behavioural_positive | Selected broker MUST reside within the required data residency zone | arsia-broker-entry | ITV-496 | schema-ref:arsia-broker-entry; struct:ITV-496; untested(structural-only) |
| ROUTE-§1.4-14 | 1.4 | RECOMMENDED | sdk | behavioural_positive | Broker selection criteria (latency, availability, load, random) are RECOMMENDED, not mandatory | — | — | — |
| ROUTE-§1.4-15 | 1.4 | NOT_RECOMMENDED | external | behavioural_positive | Strict adherence to broker selection criteria order is not mandatory | — | — | — |
| ROUTE-§1.4-16 | 1.4 | MAY | sdk | informational | Sender MAY use any selection strategy provided the broker satisfies the residency zone | — | — | — |
| ROUTE-§2-01 | 2 | REQUIRED | deployment | procedural | HTTP/2 transport binding is REQUIRED for all conformant implementations | — | — | out-of-repo(transport) |
| ROUTE-§2-02 | 2 | OPTIONAL | deployment | informational | WebSocket transport binding is OPTIONAL for conformant implementations | — | — | — |
| ROUTE-§2.1.1-01 | 2.1.1 | MUST | sdk | structural | Request body MUST be a valid ARSIA message envelope serialised as UTF-8 JSON | arsia-message | — | schema-ref:arsia-message |
| ROUTE-§2.1.2-01 | 2.1.2 | MUST | sdk | structural | HTTP 200 response body MUST be a valid ARSIA envelope with intent response, error, pending_approval, or approval_decision | arsia-message | — | schema-ref:arsia-message |
| ROUTE-§2.1.2-02 | 2.1.2 | MUST | sdk_enabled | behavioural_positive | Response envelope correlation_id MUST equal the request message id | arsia-message | — | schema-ref:arsia-message; untested(structural-only) |
| ROUTE-§2.1.2-03 | 2.1.2 | MAY | sdk | informational | HTTP 202 response MAY contain an ARSIA envelope with intent pending_approval or receipt | arsia-message | — | — |
| ROUTE-§2.1.2-04 | 2.1.2 | MUST | sdk | structural | Error response body MUST be a valid ARSIA error envelope | arsia-message | — | schema-ref:arsia-message |
| ROUTE-§2.1.3-01 | 2.1.3 | MUST | deployment | behavioural_positive | All ARSIA HTTP connections MUST use TLS for confidentiality and integrity | — | — | out-of-repo(transport) |
| ROUTE-§2.1.3-02 | 2.1.3 | REQUIRED | deployment | behavioural_positive | TLS 1.3 is REQUIRED for all conformant implementations | — | — | out-of-repo(transport) |
| ROUTE-§2.1.3-03 | 2.1.3 | MUST | deployment | procedural | All conformant implementations MUST support TLS 1.3 | — | — | out-of-repo(transport) |
| ROUTE-§2.1.3-04 | 2.1.3 | MAY | deployment | informational | TLS 1.2 MAY be accepted for legacy interoperability | — | — | — |
| ROUTE-§2.1.3-05 | 2.1.3 | MUST | deployment | interoperability | TLS 1.3 MUST be preferred in all TLS version negotiations | — | — | out-of-repo(transport) |
| ROUTE-§2.1.3-06 | 2.1.3 | MUST | deployment | interoperability | Receiver MUST log a compliance warning when a TLS 1.2 connection is used | — | — | out-of-repo(transport) |
| ROUTE-§2.1.3-07 | 2.1.3 | MUST | deployment | behavioural_positive | TLS 1.2 compliance warning MUST include sender agent-id, TLS version, and timestamp | — | — | out-of-repo(transport) |
| ROUTE-§2.1.3-08 | 2.1.3 | MUST_NOT | deployment | behavioural_negative | TLS versions prior to 1.2 (TLS 1.0, 1.1, SSL 3.0, SSL 2.0) MUST NOT be accepted | — | — | out-of-repo(transport) |
| ROUTE-§2.1.3-09 | 2.1.3 | MUST | deployment | interoperability | Connections using TLS versions below 1.2 MUST be refused | — | — | out-of-repo(transport) |
| ROUTE-§2.1.3-10 | 2.1.3 | MUST | deployment | behavioural_positive | Production deployments MUST use certificates from a publicly trusted CA | — | — | out-of-repo(infrastructure) |
| ROUTE-§2.1.3-11 | 2.1.3 | MAY | deployment | informational | Development environments MAY use self-signed certificates with explicit trust configured | — | — | — |
| ROUTE-§2.1.3-12 | 2.1.3 | MUST_NOT | deployment | behavioural_negative | Self-signed certificates MUST NOT be used in production deployments | — | — | out-of-repo(infrastructure) |
| ROUTE-§2.1.3-13 | 2.1.3 | MUST | deployment | behavioural_positive | Certificate validation MUST include hostname verification | — | — | out-of-repo(infrastructure) |
| ROUTE-§2.1.3-14 | 2.1.3 | MUST | deployment | behavioural_positive | Certificate SAN or CN MUST match the inbox URL hostname | — | — | out-of-repo(infrastructure) |
| ROUTE-§2.1.3-15 | 2.1.3 | RECOMMENDED | deployment | behavioural_positive | HSTS is RECOMMENDED for production deployments | — | — | — |
| ROUTE-§2.1.3-16 | 2.1.3 | SHOULD | deployment | behavioural_positive | HSTS header SHOULD use max-age=31536000 with includeSubDomains | — | — | — |
| ROUTE-§2.1.3-17 | 2.1.3 | MAY | deployment | informational | mTLS MAY be used for additional transport-level authentication between agents | — | — | — |
| ROUTE-§2.1.3-18 | 2.1.3 | MUST | sdk | behavioural_positive | Sender MUST sign the message envelope even when mTLS is used | arsia-message | — | schema-ref:arsia-message; untested(structural-only) |
| ROUTE-§2.1.3-19 | 2.1.3 | MUST | sdk | behavioural_positive | Receiver MUST verify the message signature even when mTLS is used | arsia-message | — | schema-ref:arsia-message; untested(structural-only) |
| ROUTE-§2.1.3-20 | 2.1.3 | MUST_NOT | deployment | behavioural_negative | Implementations MUST NOT accept plaintext HTTP connections for ARSIA endpoints | — | — | out-of-repo(transport) |
| ROUTE-§2.1.3-21 | 2.1.3 | MUST | deployment | behavioural_positive | Plaintext HTTP connection attempts MUST be refused | — | — | out-of-repo(transport) |
| ROUTE-§2.1.3-22 | 2.1.3 | SHOULD | deployment | procedural | Plaintext HTTP requests SHOULD receive HTTP 301 redirect to HTTPS equivalent | — | — | — |
| ROUTE-§2.1.3-23 | 2.1.3 | MAY | deployment | informational | Implementations MAY close plaintext HTTP connections without redirect | — | — | — |
| ROUTE-§2.1.4-01 | 2.1.4 | MUST_NOT | deployment | behavioural_negative | HTTP/2 server push MUST NOT be initiated for ARSIA endpoints | — | — | out-of-repo(transport) |
| ROUTE-§2.1.4-02 | 2.1.4 | MAY | deployment | informational | Sending agents MAY send multiple concurrent requests on a single HTTP/2 connection | — | — | — |
| ROUTE-§2.1.4-03 | 2.1.4 | SHOULD | deployment | procedural | Implementations SHOULD use stream multiplexing for rapid successive messages to same recipient | — | — | — |
| ROUTE-§2.1.4-04 | 2.1.4 | MUST | deployment | procedural | Implementations MUST respect HTTP/2 flow control windows per RFC 9113 §6.9 | — | — | out-of-repo(transport) |
| ROUTE-§2.1.4-05 | 2.1.4 | MUST_NOT | deployment | behavioural_negative | Implementations MUST NOT disable or bypass HTTP/2 flow control | — | — | out-of-repo(transport) |
| ROUTE-§2.1.4-06 | 2.1.4 | MUST | deployment | behavioural_positive | Sender MUST wait for WINDOW_UPDATE frame when flow control window is exhausted | — | — | out-of-repo(transport) |
| ROUTE-§2.1.4-07 | 2.1.4 | SHOULD | deployment | procedural | Implementations SHOULD reuse HTTP/2 connections for multiple deliveries to same recipient | — | — | — |
| ROUTE-§2.1.4-08 | 2.1.4 | RECOMMENDED | deployment | behavioural_positive | HTTP/2 connection pooling is RECOMMENDED | — | — | — |
| ROUTE-§2.1.4-09 | 2.1.4 | MUST | deployment | interoperability | Implementations MUST respect SETTINGS_MAX_CONCURRENT_STREAMS for concurrent stream limits | — | — | out-of-repo(transport) |
| ROUTE-§2.1.4-10 | 2.1.4 | MUST | deployment | procedural | Implementations MUST support HPACK header compression | — | — | out-of-repo(transport) |
| ROUTE-§2.1.4-11 | 2.1.4 | SHOULD | deployment | procedural | HPACK SHOULD compress repetitive ARSIA headers across requests on same connection | — | — | — |
| ROUTE-§2.2.1-01 | 2.2.1 | MUST | deployment | behavioural_positive | WebSocket connections MUST use the wss:// scheme (TLS-encrypted) | — | — | out-of-repo(transport) |
| ROUTE-§2.2.1-02 | 2.2.1 | MUST_NOT | deployment | behavioural_negative | Plaintext ws:// connections MUST NOT be used for ARSIA communication | — | — | out-of-repo(transport) |
| ROUTE-§2.2.1-03 | 2.2.1 | MUST | deployment | behavioural_positive | WebSocket upgrade handshake MUST declare the arsia-v1 sub-protocol | — | — | out-of-repo(transport) |
| ROUTE-§2.2.1-04 | 2.2.1 | MUST | deployment | behavioural_positive | Server MUST confirm arsia-v1 sub-protocol in the upgrade response | — | — | out-of-repo(transport) |
| ROUTE-§2.2.1-05 | 2.2.1 | MUST | deployment | procedural | Client MUST close connection if server omits arsia-v1 sub-protocol from upgrade response | — | — | out-of-repo(transport) |
| ROUTE-§2.2.2-01 | 2.2.2 | MUST_NOT | deployment | behavioural_negative | Client MUST NOT send ARSIA messages before WebSocket authentication completes | — | — | out-of-repo(transport) |
| ROUTE-§2.2.2-02 | 2.2.2 | MUST | deployment | behavioural_positive | Client MUST authenticate via JSON auth frame after WebSocket connection is established | arsia-websocket-frame | ITV-60 | schema-ref:arsia-websocket-frame; struct:ITV-60; untested(structural-only) |
| ROUTE-§2.2.2-03 | 2.2.2 | MAY | deployment | informational | WebSocket session ID MAY be used for correlation in audit logs and debugging | arsia-websocket-frame | ITV-141 | — |
| ROUTE-§2.2.2-04 | 2.2.2 | MUST | deployment | behavioural_positive | Server MUST close WebSocket with code 4001 within 5 seconds of sending auth_error | arsia-websocket-frame | — | schema-ref:arsia-websocket-frame; untested(structural-only) |
| ROUTE-§2.2.2-05 | 2.2.2 | MUST_NOT | deployment | behavioural_negative | Client MUST NOT send further frames after receiving auth_error | — | — | out-of-repo(transport) |
| ROUTE-§2.2.2-06 | 2.2.2 | MUST | deployment | behavioural_positive | Server MUST close connection with code 4001 if no auth frame arrives within 10 seconds | — | — | out-of-repo(transport) |
| ROUTE-§2.2.2-07 | 2.2.2 | MUST | deployment | behavioural_positive | Each WebSocket frame MUST contain a complete, valid ARSIA message envelope | arsia-message | — | schema-ref:arsia-message; untested(structural-only) |
| ROUTE-§2.2.2-08 | 2.2.2 | MUST_NOT | deployment | behavioural_negative | Message envelopes MUST NOT be fragmented across multiple WebSocket frames | — | — | out-of-repo(transport) |
| ROUTE-§2.2.2-09 | 2.2.2 | MUST_NOT | deployment | behavioural_negative | Agents MUST NOT send binary WebSocket frames in v1.0 | — | — | out-of-repo(transport) |
| ROUTE-§2.2.2-10 | 2.2.2 | SHOULD | deployment | behavioural_positive | Server SHOULD close connection with code 1003 upon receiving a binary frame | — | — | — |
| ROUTE-§2.2.2-11 | 2.2.2 | MUST | deployment | behavioural_positive | Server MUST close connection with code 4003 when a frame exceeds max_message_bytes | — | — | out-of-repo(transport) |
| ROUTE-§2.2.2-12 | 2.2.2 | MUST | deployment | behavioural_positive | Client MUST send a ping heartbeat frame every 30 seconds (aligned to Core §8.2 — the MUST governs) | arsia-websocket-frame | ITV-142 | schema-ref:arsia-websocket-frame; struct:ITV-142; untested(structural-only) |
| ROUTE-§2.2.2-13 | 2.2.2 | MUST | deployment | behavioural_positive | Server MUST respond with pong heartbeat within 5 seconds of receiving ping | arsia-websocket-frame | ITV-143 | schema-ref:arsia-websocket-frame; struct:ITV-143; untested(structural-only) |
| ROUTE-§2.2.2-14 | 2.2.2 | SHOULD | deployment | behavioural_positive | Client SHOULD treat connection as dead if no pong arrives within 10 seconds | — | — | — |
| ROUTE-§2.2.2-15 | 2.2.2 | MAY | deployment | informational | Server MAY send unsolicited ping heartbeat requests to connected clients | arsia-websocket-frame | — | — |
| ROUTE-§2.2.2-16 | 2.2.2 | MUST | deployment | behavioural_positive | Client MUST respond with pong frame within 5 seconds of receiving server ping | arsia-websocket-frame | — | schema-ref:arsia-websocket-frame; untested(structural-only) |
| ROUTE-§2.2.2-17 | 2.2.2 | SHOULD | deployment | behavioural_positive | Server SHOULD close connection with code 4002 if client fails to respond to ping | — | — | — |
| ROUTE-§2.2.2-18 | 2.2.2 | MAY | deployment | informational | Application-level and protocol-level heartbeat mechanisms MAY be used concurrently | — | — | — |
| ROUTE-§2.2.2-19 | 2.2.2 | SHOULD_NOT | deployment | behavioural_negative | Closing party SHOULD NOT send further messages after initiating WebSocket close | — | — | — |
| ROUTE-§2.2.2-20 | 2.2.2 | MUST | deployment | behavioural_positive | Receiving party MUST respond with a WebSocket close frame per RFC 6455 §5.5.1 | — | — | out-of-repo(transport) |
| ROUTE-§2.2.2-21 | 2.2.2 | MUST | deployment | procedural | Client MUST implement exponential backoff for WebSocket reconnection | — | — | out-of-repo(transport) |
| ROUTE-§2.2.2-22 | 2.2.2 | RECOMMENDED | deployment | procedural | Reconnection backoff RECOMMENDED: 1s base, 2x multiplier, 30s max, ±25% jitter | — | — | — |
| ROUTE-§2.2.2-23 | 2.2.2 | RECOMMENDED | deployment | procedural | Maximum reconnection attempts RECOMMENDED unlimited with exponential backoff | — | — | — |
| ROUTE-§2.2.2-24 | 2.2.2 | RECOMMENDED | deployment | behavioural_positive | Reconnection jitter is RECOMMENDED to prevent thundering herd on server recovery | — | — | — |
| ROUTE-§2.2.2-25 | 2.2.2 | MUST | deployment | behavioural_positive | Client MUST re-authenticate after WebSocket reconnection | — | — | out-of-repo(transport) |
| ROUTE-§2.2.2-26 | 2.2.2 | MUST_NOT | deployment | behavioural_negative | Server MUST NOT assume a reconnected client retains prior authentication state | — | — | out-of-repo(infrastructure) |
| ROUTE-§2.2.2-27 | 2.2.2 | MAY | deployment | informational | Server MAY close WebSocket connections idle for 60 seconds with no frame exchange | — | — | — |
| ROUTE-§2.2.2-28 | 2.2.2 | SHOULD | deployment | behavioural_positive | Server SHOULD use close code 4002 for idle timeout closures | — | — | — |
| ROUTE-§2.2.3-01 | 2.2.3 | MAY | deployment | informational | Implementations MAY use additional standard WebSocket close codes per RFC 6455 §7.4.1 | — | — | — |
| ROUTE-§2.3.1-01 | 2.3.1 | MUST | sdk | behavioural_positive | The envelope to field MUST contain the final recipient's agent-id, not the broker's | arsia-message | — | schema-ref:arsia-message; untested(structural-only) |
| ROUTE-§2.3.1-02 | 2.3.1 | MUST | sdk | behavioural_positive | Authorization header MUST contain a token for the broker's relay capability | arsia-jwt-claims | — | schema-ref:arsia-jwt-claims; untested(structural-only) |
| ROUTE-§2.3.2-01 | 2.3.2 | MUST_NOT | external | behavioural_negative | Broker MUST NOT re-send a forwarded DPoP proof, including on a transport retry | — | — | check:`R20 (j) 4 the old proof reached the recipient exactly once (never re-sent)`; out-of-repo(external-party) |
| ROUTE-§2.3.3-01 | 2.3.3 | MUST | external | behavioural_positive | Broker MUST forward the recipient's synchronous response to sender without alteration | — | ITV-81, ITV-497 | struct:ITV-81, ITV-497; untested(structural-only) |
| ROUTE-§2.3.3-02 | 2.3.3 | MUST_NOT | external | behavioural_negative | On a recipient DPoP nonce challenge the broker MUST NOT produce, modify or re-send a DPoP proof on the sender's behalf | — | — | check:`R20 (j) 2 the broker does not present the recipient's nonce as its own DPoP-Nonce`; check:`R20 (j) 4 the old proof reached the recipient exactly once (never re-sent)`; out-of-repo(external-party) |
| ROUTE-§2.3.3-03 | 2.3.3 | MUST | external | behavioural_positive | Broker MUST return a recipient DPoP nonce challenge to the sender as a service_unavailable relay error with reason recipient_dpop_nonce, dpop_nonce and dpop_nonce_htu | arsia-message | ITV-690, INV-108, INV-109, INV-110 | schema-ref:arsia-message; struct:ITV-690, INV-108, INV-109, INV-110; untested(structural-only) |
| ROUTE-§2.3.3-04 | 2.3.3 | MUST | external | behavioural_positive | Broker MUST copy the recipient's DPoP-Nonce value unmodified into dpop_nonce | arsia-message | ITV-690 | schema-ref:arsia-message; struct:ITV-690; untested(structural-only) |
| ROUTE-§2.3.3-05 | 2.3.3 | MUST_NOT | external | behavioural_negative | Broker MUST NOT present a recipient's nonce in its own DPoP-Nonce response header | — | — | check:`R20 (j) 2 the broker does not present the recipient's nonce as its own DPoP-Nonce`; out-of-repo(external-party) |
| ROUTE-§2.3.4-01 | 2.3.4 | MUST | external | behavioural_positive | Broker MUST forward the message to recipient within 10 seconds of receipt | arsia-audit-record | RTV-01 | schema-ref:arsia-audit-record; struct:RTV-01; crypto:RTV-01 |
| ROUTE-§2.3.4-02 | 2.3.4 | MUST | external | behavioural_positive | Broker MUST respect the message's expires_at field during relay | arsia-message | — | schema-ref:arsia-message; untested(structural-only) |
| ROUTE-§2.3.4-03 | 2.3.4 | MUST | external | behavioural_positive | Broker MUST abandon relay and return service_unavailable if expires_at minus 5 seconds is exceeded | arsia-message | — | schema-ref:arsia-message; untested(structural-only) |
| ROUTE-§3.1-01 | 3.1 | MAY | sdk_enabled | informational | Under at-most-once delivery, a dropped connection MAY result in ambiguous processing status | — | — | — |
| ROUTE-§3.2-01 | 3.2 | MUST | sdk_enabled | behavioural_positive | Receiver MUST deduplicate at-least-once messages using the idempotency key | arsia-message | — | schema-ref:arsia-message; untested(structural-only) |
| ROUTE-§3.2-02 | 3.2 | MUST | sdk_enabled | procedural | Sender MUST follow the retry-with-idempotency procedure for at-least-once delivery | arsia-message | — | schema-ref:arsia-message; untested(structural-only) |
| ROUTE-§3.2-03 | 3.2 | RECOMMENDED | sdk_enabled | behavioural_positive | Maximum retry count of 3 is RECOMMENDED for at-least-once delivery | — | — | — |
| ROUTE-§3.2-04 | 3.2 | MUST | sdk_enabled | behavioural_positive | Sender MUST abandon the request and report failure after 3 failed retries | — | — | untested(no-reference-model) |
| ROUTE-§3.2-05 | 3.2 | SHOULD | sdk_enabled | behavioural_positive | A 409 conflict with Retry-After for an in-progress idempotent request SHOULD be resent identically after the delay (ARSIA-Core.md §11.3) | — | — | — |
| ROUTE-§4.1.7-01 | 4.1.7 | MAY | sdk_enabled | behavioural_positive | Sender MAY retry DISPATCH_FAILED messages using exponential backoff | — | — | — |
| ROUTE-§4.1.7-02 | 4.1.7 | RECOMMENDED | sdk_enabled | behavioural_positive | DISPATCH_FAILED becomes terminal after maximum retries (3 RECOMMENDED) | — | — | — |
| ROUTE-§4.1.7-03 | 4.1.7 | MUST | sdk_enabled | behavioural_positive | Retried messages MUST preserve the original id and idempotency key for deduplication | arsia-message | — | schema-ref:arsia-message; untested(structural-only) |
| ROUTE-§4.1.8-01 | 4.1.8 | MUST_NOT | sdk_enabled | behavioural_negative | HTTP 400/401/403/404/409/413/501 errors are non-retryable; sender MUST NOT retry without modifying the request (409 with Retry-After for an in-progress idempotent request excepted, ARSIA-Core.md §11.3) | arsia-message | — | schema-ref:arsia-message; untested(structural-only) |
| ROUTE-§4.1.8-02 | 4.1.8 | SHOULD | sdk_enabled | behavioural_positive | A 409 conflict carrying Retry-After for an in-progress idempotent request SHOULD be retried unchanged after the delay | — | — | — |
| ROUTE-§4.1.9-01 | 4.1.9 | MUST_NOT | sdk | behavioural_negative | Expired messages (past expires_at) MUST NOT be processed | — | ITV-498 | struct:ITV-498; exec:R16:ITV-498 |
| ROUTE-§4.1.9-02 | 4.1.9 | MUST_NOT | sdk | behavioural_negative | EXPIRED is a terminal state; the message MUST NOT be processed or retried | — | ITV-499 | struct:ITV-499; untested(structural-only) |
| ROUTE-§4.1.9-03 | 4.1.9 | MUST | sdk | behavioural_positive | Messages expiring during DISPATCHED or BROKER_RELAYED state MUST transition to EXPIRED | arsia-message | — | schema-ref:arsia-message; untested(structural-only) |
| ROUTE-§4.1.9-04 | 4.1.9 | MUST | sdk | behavioural_positive | Recipient MUST reject expired messages with error code invalid_request | arsia-message | ITV-499 | schema-ref:arsia-message; struct:ITV-499; untested(structural-only) |
| ROUTE-§5.1-01 | 5.1 | MUST | deployment | behavioural_positive | compliance.data_residency field MUST declare the geographic zone for message processing as ISO 3166-1 alpha-2 or regional code | arsia-message, arsia-compliance-field | — | schema-ref:arsia-message; schema-ref:arsia-compliance-field; untested(structural-only) |
| ROUTE-§5.1-02 | 5.1 | OPTIONAL | sdk | structural | The compliance.data_residency field is OPTIONAL in the message envelope | arsia-message | — | — |
| ROUTE-§5.1-03 | 5.1 | REQUIRED | sdk | behavioural_positive | Brokered routing is REQUIRED when compliance.data_residency is present and non-empty | arsia-message | — | schema-ref:arsia-message; untested(structural-only) |
| ROUTE-§5.1-04 | 5.1 | MAY | sdk | informational | Implementations MAY define additional regional codes beyond the standard set | — | — | — |
| ROUTE-§5.1-05 | 5.1 | SHOULD | sdk | behavioural_positive | Custom regional codes SHOULD use uppercase alphabetic strings of 2–4 characters to avoid ISO 3166-1 conflicts | arsia-compliance-field | — | — |
| ROUTE-§5.1-06 | 5.1 | MUST | sdk | behavioural_positive | Messages with data_residency MUST be routed through a Compliance Broker within the declared zone | — | ITV-500 | struct:ITV-500; untested(structural-only) |
| ROUTE-§5.1-07 | 5.1 | MUST | deployment | behavioural_positive | Broker physical servers MUST reside within the declared data residency zone | arsia-broker-entry | — | schema-ref:arsia-broker-entry; untested(structural-only) |
| ROUTE-§5.1-08 | 5.1 | MUST | deployment | behavioural_positive | Audit logs for data-residency-constrained messages MUST be stored within the declared zone | arsia-audit-record | — | schema-ref:arsia-audit-record; untested(structural-only) |
| ROUTE-§5.1-09 | 5.1 | SHOULD | deployment | behavioural_positive | Recipient processing infrastructure SHOULD be located within the declared data residency zone | — | — | — |
| ROUTE-§5.2-01 | 5.2 | MUST | deployment | behavioural_positive | For EU data residency, all message processing MUST occur within servers physically located in an EU/EEA member state | — | — | out-of-repo(infrastructure) |
| ROUTE-§5.2-02 | 5.2 | MUST | deployment | behavioural_positive | EU-zone Compliance Broker MUST be physically located in an EU/EEA member state | arsia-broker-entry | ITV-501 | schema-ref:arsia-broker-entry; struct:ITV-501; untested(structural-only) |
| ROUTE-§5.2-03 | 5.2 | MUST | external | behavioural_positive | EU broker IdentityRecord.jurisdiction MUST be an ISO 3166-1 alpha-2 code of an EU/EEA member state | arsia-identity-record | — | schema-ref:arsia-identity-record; untested(structural-only) |
| ROUTE-§5.2-04 | 5.2 | MUST | deployment | behavioural_positive | EU-zone audit logs MUST be stored on servers physically located in an EU/EEA member state | arsia-audit-record | — | schema-ref:arsia-audit-record; untested(structural-only) |
| ROUTE-§5.2-05 | 5.2 | MUST | operational_policy | behavioural_positive | Non-EU senders MUST ensure an appropriate GDPR transfer mechanism for EU-originating response data containing personal data | — | — | out-of-repo(operator) |
| ROUTE-§5.2-06 | 5.2 | MUST | sdk | behavioural_positive | Implementations MUST maintain an up-to-date list of EU/EEA member states for zone matching; the published list is dated (revision) and identified by its SHA-256, and residency normalization expands "EU" to it | — | ITV-617 | struct:ITV-617; exec:R10:ITV-617 |
| ROUTE-§5.2-07 | 5.2 | SHOULD | sdk | behavioural_positive | EU/EEA membership changes SHOULD be reflected in implementations within 90 days of the effective date | — | — | — |
| ROUTE-§5.3-01 | 5.3 | MUST | sdk | behavioural_positive | For country-code zones, broker jurisdiction MUST exactly equal the required zone code | arsia-broker-entry | — | schema-ref:arsia-broker-entry; untested(structural-only) |
| ROUTE-§5.3-02 | 5.3 | MUST | sdk | behavioural_positive | For the EU regional zone, broker jurisdiction MUST be an ISO 3166-1 alpha-2 code of an EU/EEA member state | arsia-broker-entry | ITV-501 | schema-ref:arsia-broker-entry; struct:ITV-501; untested(structural-only) |
| ROUTE-§5.3-03 | 5.3 | MAY | sdk_enabled | informational | Sender MAY verify the broker TLS certificate C= attribute for geographic consistency | — | — | — |
| ROUTE-§5.3-04 | 5.3 | SHOULD | sdk_enabled | behavioural_positive | TLS certificate C= country attribute SHOULD be consistent with the broker declared jurisdiction | — | — | — |
| ROUTE-§5.3-05 | 5.3 | RECOMMENDED | operational_policy | procedural | Regulated deployments SHOULD use additional assurance mechanisms beyond protocol-level residency verification | — | — | — |
| ROUTE-§5.3-06 | 5.3 | SHOULD | operational_policy | procedural | Brokers SHOULD provide SOC 2 Type II reports covering their declared residency zone | — | — | — |
| ROUTE-§5.3-07 | 5.3 | SHOULD | operational_policy | procedural | Cloud-hosted brokers SHOULD reference provider region identifiers and published geographic data | — | — | — |
| ROUTE-§5.3-08 | 5.3 | SHOULD | operational_policy | procedural | Regulated-industry brokers SHOULD be registered with the relevant national supervisory authority | — | — | — |
| ROUTE-§6.1-01 | 6.1 | MUST | sdk_enabled | behavioural_positive | Agent MUST accept at least requests_per_minute requests per minute under normal conditions | arsia-discovery-response | — | schema-ref:arsia-discovery-response; untested(structural-only) |
| ROUTE-§6.1-02 | 6.1 | SHOULD | sdk_enabled | behavioural_positive | Agent SHOULD accept up to burst_size additional requests within a short window before enforcing rate limits | arsia-discovery-response | — | — |
| ROUTE-§6.2-01 | 6.2 | SHOULD | sdk_enabled | behavioural_positive | Agents SHOULD include X-RateLimit-Limit, X-RateLimit-Remaining, and X-RateLimit-Reset headers on every HTTP response | — | — | — |
| ROUTE-§6.2-02 | 6.2 | MUST | sdk_enabled | behavioural_positive | Rate-limited requests MUST receive HTTP 429 with a standard ARSIA error envelope using code rate_limited | arsia-message | — | schema-ref:arsia-message; untested(structural-only) |
| ROUTE-§6.2-03 | 6.2 | MUST | sdk_enabled | structural | HTTP 429 responses MUST include Retry-After header and an ARSIA error envelope with code rate_limited | arsia-message | — | schema-ref:arsia-message |
| ROUTE-§6.2-04 | 6.2 | REQUIRED | sdk_enabled | behavioural_positive | The Retry-After header is REQUIRED on all HTTP 429 responses, specifying seconds until retry is allowed | — | — | out-of-repo(transport) |
| ROUTE-§6.3-01 | 6.3 | MAY | sdk_enabled | informational | Higher-priority messages MAY be processed before lower-priority messages in the inbox queue | arsia-message | — | — |
| ROUTE-§6.3-02 | 6.3 | MUST_NOT | sdk | behavioural_negative | Message priority MUST NOT affect processing correctness; only scheduling order may differ | — | ITV-502, ITV-503 | struct:ITV-502, ITV-503; untested(structural-only) |
| ROUTE-§6.3-03 | 6.3 | MUST | sdk | behavioural_positive | A priority-0 message MUST produce the same result as an identical priority-10 message | — | ITV-502, ITV-503 | struct:ITV-502, ITV-503; untested(structural-only) |
| ROUTE-§6.3-04 | 6.3 | SHOULD | sdk_enabled | behavioural_positive | Implementations SHOULD honour priority to distinguish interactive (8–10) from batch (0–2) workloads | arsia-message | — | — |
| ROUTE-§6.3-05 | 6.3 | MUST_NOT | sdk | behavioural_negative | Implementations MUST NOT starve low-priority messages indefinitely | — | — | untested(no-reference-model) |
| ROUTE-§6.3-06 | 6.3 | MUST | sdk | behavioural_positive | All messages MUST eventually be processed or expired regardless of priority | — | — | untested(no-reference-model) |
| ROUTE-§6.3-07 | 6.3 | SHOULD | sdk_enabled | behavioural_positive | Implementations SHOULD implement priority aging for long-queued messages to prevent starvation | — | — | — |
| ROUTE-§6.3-08 | 6.3 | SHOULD | sdk_enabled | behavioural_positive | Long-queued messages SHOULD have their effective priority increased over time | — | — | — |
| ROUTE-§6.3-09 | 6.3 | SHOULD | sdk_enabled | behavioural_positive | When X-Request-Priority header and context.priority differ, the server SHOULD use the header value | — | — | — |
| ROUTE-§6.3-10 | 6.3 | MAY | sdk_enabled | informational | Server MAY log a discrepancy between X-Request-Priority header and context.priority field | — | — | — |
| ROUTE-§7.1-01 | 7.1 | MUST | external | behavioural_positive | Broker MUST declare arsiaprotocol.broker.relay in its capabilities_supported array | arsia-discovery-response | — | schema-ref:arsia-discovery-response; untested(structural-only) |
| ROUTE-§7.1-02 | 7.1 | MUST | external | behavioural_positive | Broker MUST publish its IdentityRecord at /.well-known/arsia/identity | arsia-identity-record | — | schema-ref:arsia-identity-record; untested(structural-only) |
| ROUTE-§7.1-03 | 7.1 | MUST | external | behavioural_positive | Broker IdentityRecord MUST be signed with the broker Ed25519 key | — | ITV-504 | struct:ITV-504; untested(structural-only) |
| ROUTE-§7.1-04 | 7.1 | MUST | external | behavioural_positive | Broker IdentityRecord.jurisdiction MUST accurately reflect the broker physical location | arsia-identity-record | — | schema-ref:arsia-identity-record; untested(structural-only) |
| ROUTE-§7.1-05 | 7.1 | MUST | external | behavioural_positive | Broker jurisdiction MUST be the ISO 3166-1 alpha-2 code of the country where physical servers are located | arsia-identity-record | — | schema-ref:arsia-identity-record; untested(structural-only) |
| ROUTE-§7.1-06 | 7.1 | MUST | external | behavioural_positive | Multi-country brokers MUST set jurisdiction to the country where primary message processing occurs | — | — | out-of-repo(external-party) |
| ROUTE-§7.1-07 | 7.1 | MUST | external | behavioural_positive | Broker MUST support HTTP/2 transport binding for receiving and forwarding messages | — | — | out-of-repo(transport) |
| ROUTE-§7.1-08 | 7.1 | SHOULD | external | behavioural_positive | Broker SHOULD support WebSocket binding for long-lived relay connections | — | — | — |
| ROUTE-§7.1-09 | 7.1 | OPTIONAL | external | informational | Broker WebSocket support is OPTIONAL | — | — | — |
| ROUTE-§7.1-10 | 7.1 | MUST | external | behavioural_positive | Broker MUST expose a standard discovery endpoint at /.well-known/arsia | arsia-discovery-response | — | schema-ref:arsia-discovery-response; untested(structural-only) |
| ROUTE-§7.1-11 | 7.1 | MUST | external | behavioural_positive | Broker discovery response MUST include arsiaprotocol.broker.relay in capabilities_supported | arsia-discovery-response | — | schema-ref:arsia-discovery-response; untested(structural-only) |
| ROUTE-§7.1-12 | 7.1 | MUST | external | behavioural_positive | Broker MUST expose public keys at /.well-known/arsia/jwks.json | — | — | out-of-repo(external-party) |
| ROUTE-§7.1-13 | 7.1 | MUST | external | behavioural_positive | Broker MUST generate and store audit records for every relayed message | arsia-audit-record | RTV-02, ITV-43 | schema-ref:arsia-audit-record; struct:RTV-02, ITV-43; crypto:RTV-02 |
| ROUTE-§7.2-01 | 7.2 | MAY | deployment | informational | Broker discovery endpoint MAY be hosted by the recipient, a registry service, or the sender configuration | — | — | — |
| ROUTE-§7.2-02 | 7.2 | SHOULD | sdk_enabled | behavioural_positive | Broker discovery response SHOULD include Cache-Control and ETag caching headers | — | — | — |
| ROUTE-§7.2-03 | 7.2 | SHOULD | deployment | behavioural_positive | Senders SHOULD cache broker discovery responses for the Cache-Control max-age duration | — | — | — |
| ROUTE-§7.2-04 | 7.2 | RECOMMENDED | sdk_enabled | behavioural_positive | Maximum broker discovery cache duration of 5 minutes is RECOMMENDED | — | — | — |
| ROUTE-§7.2-05 | 7.2 | SHOULD | deployment | behavioural_positive | Senders SHOULD use If-None-Match with ETag for conditional broker discovery requests | — | — | — |
| ROUTE-§7.2-06 | 7.2 | MUST | sdk_enabled | behavioural_positive | Empty broker list for a requested zone MUST be returned as empty JSON array with HTTP 200 | — | ITV-505 | struct:ITV-505; untested(structural-only) |
| ROUTE-§7.2-07 | 7.2 | REQUIRED | external | structural | BrokerEntry.agent_id (string) is REQUIRED — the broker agent identifier | arsia-broker-entry | ITV-05 | schema-ref:arsia-broker-entry; struct:ITV-05 |
| ROUTE-§7.2-08 | 7.2 | REQUIRED | external | structural | BrokerEntry.inbox (string) is REQUIRED — absolute URL of the broker inbox endpoint | arsia-broker-entry | ITV-05 | schema-ref:arsia-broker-entry; struct:ITV-05 |
| ROUTE-§7.2-09 | 7.2 | REQUIRED | external | structural | BrokerEntry.jurisdiction (string) is REQUIRED — ISO 3166-1 alpha-2 code of broker physical location | arsia-broker-entry | ITV-05 | schema-ref:arsia-broker-entry; struct:ITV-05 |
| ROUTE-§7.2-10 | 7.2 | REQUIRED | external | structural | BrokerEntry.residency_zones (array) is REQUIRED — zone codes the broker serves | arsia-broker-entry | ITV-05, ITV-06 | schema-ref:arsia-broker-entry; struct:ITV-05, ITV-06 |
| ROUTE-§7.2-11 | 7.2 | OPTIONAL | external | structural | BrokerEntry.capacity (object) is OPTIONAL — load-based broker selection data | arsia-broker-entry | ITV-05 | — |
| ROUTE-§7.2-12 | 7.2 | OPTIONAL | external | structural | BrokerEntry.capacity.requests_per_minute (integer) is OPTIONAL — maximum relay capacity per minute | arsia-broker-entry | ITV-05 | — |
| ROUTE-§7.2-13 | 7.2 | OPTIONAL | external | structural | BrokerEntry.capacity.current_load_pct (integer) is OPTIONAL — current load as percentage (0–100) | arsia-broker-entry | ITV-05 | — |
| ROUTE-§7.2-14 | 7.2 | REQUIRED | external | structural | BrokerEntry.health (string) is REQUIRED — one of "healthy", "degraded", or "unhealthy" | arsia-broker-entry | ITV-05, ITV-167 | schema-ref:arsia-broker-entry; struct:ITV-05, ITV-167 |
| ROUTE-§7.2-15 | 7.2 | REQUIRED | external | structural | BrokerEntry.last_health_check (string) is REQUIRED — RFC 3339 timestamp of most recent health check | arsia-broker-entry | ITV-05 | schema-ref:arsia-broker-entry; struct:ITV-05 |
| ROUTE-§7.2-16 | 7.2 | REQUIRED | external | structural | Broker discovery query parameter residency (string) is REQUIRED — the zone to filter by | arsia-broker-discovery-request | ITV-505, ITV-506 | schema-ref:arsia-broker-discovery-request; struct:ITV-505, ITV-506 |
| ROUTE-§7.3-01 | 7.3 | MUST | external | procedural | All Compliance Brokers MUST implement the normative relay rules | — | — | out-of-repo(external-party) |
| ROUTE-§7.3-02 | 7.3 | MUST | external | behavioural_positive | Broker MUST verify the sender message signature before forwarding | — | ITV-507 | struct:ITV-507; untested(structural-only) |
| ROUTE-§7.3-03 | 7.3 | MUST | external | behavioural_positive | Broker MUST reject messages with invalid signatures using error code unauthorized | arsia-message | ITV-507 | schema-ref:arsia-message; struct:ITV-507; untested(structural-only) |
| ROUTE-§7.3-04 | 7.3 | MUST_NOT | external | behavioural_negative | Broker MUST NOT forward a message with an invalid signature | — | ITV-508 | struct:ITV-508; untested(structural-only) |
| ROUTE-§7.3-05 | 7.3 | MUST | external | behavioural_positive | Broker MUST verify that its own jurisdiction matches the message data_residency zone | arsia-broker-entry | ITV-509 | schema-ref:arsia-broker-entry; struct:ITV-509; untested(structural-only) |
| ROUTE-§7.3-06 | 7.3 | MUST | external | behavioural_positive | For country-code zones, broker IdentityRecord.jurisdiction MUST exactly equal the required zone | arsia-identity-record | — | schema-ref:arsia-identity-record; untested(structural-only) |
| ROUTE-§7.3-07 | 7.3 | MUST | external | behavioural_positive | For EU zone, broker IdentityRecord.jurisdiction MUST be an ISO 3166-1 alpha-2 code of an EU/EEA member state | arsia-identity-record | — | schema-ref:arsia-identity-record; untested(structural-only) |
| ROUTE-§7.3-08 | 7.3 | MUST | external | behavioural_positive | Broker MUST reject messages with service_unavailable when its jurisdiction does not match the required zone | arsia-message | ITV-509 | schema-ref:arsia-message; struct:ITV-509; untested(structural-only) |
| ROUTE-§7.3-09 | 7.3 | MUST_NOT | external | behavioural_negative | Broker MUST NOT forward a message when its jurisdiction does not match the required residency zone | — | ITV-509 | struct:ITV-509; untested(structural-only) |
| ROUTE-§7.3-10 | 7.3 | MUST | external | structural | Zone mismatch error MUST include data_residency_violation, broker_jurisdiction, and required_zone in details | arsia-message | ITV-509 | schema-ref:arsia-message; struct:ITV-509 |
| ROUTE-§7.3-11 | 7.3 | MUST_NOT | external | behavioural_negative | Broker MUST NOT modify the message envelope in any way during relay | — | ITV-510 | struct:ITV-510; untested(structural-only) |
| ROUTE-§7.3-12 | 7.3 | MUST | external | behavioural_positive | Forwarded message MUST be byte-identical to the received message after RFC 8785 canonicalization | — | ITV-510, ITV-511 | struct:ITV-510, ITV-511; untested(structural-only) |
| ROUTE-§7.3-13 | 7.3 | MUST_NOT | external | behavioural_negative | Broker MUST NOT add, remove, or modify any envelope fields | — | ITV-512 | struct:ITV-512; untested(structural-only) |
| ROUTE-§7.3-14 | 7.3 | MUST_NOT | external | behavioural_negative | Broker MUST NOT re-sign the relayed message | — | ITV-513 | struct:ITV-513; untested(structural-only) |
| ROUTE-§7.3-15 | 7.3 | MUST_NOT | external | behavioural_negative | Broker MUST NOT modify the security object during relay | — | ITV-514 | struct:ITV-514; untested(structural-only) |
| ROUTE-§7.3-16 | 7.3 | MUST_NOT | external | behavioural_negative | Broker MUST NOT modify the payload during relay | — | ITV-515 | struct:ITV-515; untested(structural-only) |
| ROUTE-§7.3-17 | 7.3 | MUST | external | behavioural_positive | Sender original digital signature MUST remain valid and verifiable by the recipient after broker relay | arsia-message | ITV-513 | schema-ref:arsia-message; struct:ITV-513; untested(structural-only) |
| ROUTE-§7.3-18 | 7.3 | MUST_NOT | external | behavioural_negative | Broker MUST NOT read or log payload contents | — | — | out-of-repo(external-party) |
| ROUTE-§7.3-19 | 7.3 | MAY | external | informational | Broker MAY compute and log a SHA-256 payload hash for audit purposes | arsia-audit-record | — | — |
| ROUTE-§7.3-20 | 7.3 | MUST_NOT | external | behavioural_negative | Broker MUST NOT store, inspect, index, or transmit payload contents to any party other than the recipient | — | — | out-of-repo(external-party) |
| ROUTE-§7.3-21 | 7.3 | MUST | external | behavioural_positive | Broker MUST forward the message to the recipient inbox as specified in §1.2.2 step 7 (sender's T_e2e and relay attestation; no broker token of its own) | arsia-audit-record | RTV-01 | schema-ref:arsia-audit-record; struct:RTV-01; crypto:RTV-01 |
| ROUTE-§7.3-22 | 7.3 | MUST | external | behavioural_positive | Broker MUST return the recipient response to the sender unmodified | — | ITV-516 | struct:ITV-516; untested(structural-only) |
| ROUTE-§7.3-23 | 7.3 | MUST | external | behavioural_positive | Broker MUST append a broker_relay audit record for every message received for relay, whether or not forwarded: messages rejected before forwarding (Rules 1, 2, §1.2.2 step 6, Rule 9), failed or timed-out forwarding, and relays resulting in errors | arsia-audit-record | RTV-02, ITV-508, ITV-688, ITV-689 | schema-ref:arsia-audit-record; struct:RTV-02, ITV-508, ITV-688, ITV-689; crypto:RTV-02 |
| ROUTE-§7.3-24 | 7.3 | MUST | external | structural | Broker audit record MUST contain message_id, from_agent, to_agent, message_ts, broker_agent_id, residency_zone, received_at, forwarding_result and payload_hash, and attestation_id, forwarded_at and relay_latency_ms when forwarding was initiated | arsia-audit-record | RTV-02, ITV-43, ITV-688, INV-48 | schema-ref:arsia-audit-record; struct:RTV-02, ITV-43, ITV-688, INV-48; crypto:RTV-02 |
| ROUTE-§7.3-25 | 7.3 | MUST_NOT | external | behavioural_negative | Broker MUST NOT cache or store message envelopes beyond the audit record | — | — | out-of-repo(external-party) |
| ROUTE-§7.3-26 | 7.3 | MUST | external | behavioural_positive | Broker MUST discard the message envelope from memory and temporary storage after forwarding | — | — | out-of-repo(external-party) |
| ROUTE-§7.3-27 | 7.3 | MUST | external | behavioural_positive | Broker MUST respect the message expires_at field during relay | arsia-message | — | schema-ref:arsia-message; untested(structural-only) |
| ROUTE-§7.3-28 | 7.3 | MUST | external | behavioural_positive | Broker MUST return service_unavailable if forwarding would exceed expires_at minus 5 seconds | arsia-message | ITV-517 | schema-ref:arsia-message; struct:ITV-517; untested(structural-only) |
| ROUTE-§7.3-29 | 7.3 | MUST_NOT | external | behavioural_negative | Broker MUST NOT forward a message when the expiration safety margin would be exceeded | — | ITV-517 | struct:ITV-517; untested(structural-only) |
| ROUTE-§7.3-30 | 7.3 | MUST | external | behavioural_positive | Broker MUST record a Rule 9 expiration refusal with forwarding_result "timeout" and without the forwarding fields | arsia-audit-record | ITV-689 | schema-ref:arsia-audit-record; struct:ITV-689; untested(structural-only) |
| ROUTE-§7.4-01 | 7.4 | MUST | deployment | behavioural_positive | Broker relay audit records MUST be stored within the declared data residency zone | arsia-audit-record | RTV-02 | schema-ref:arsia-audit-record; struct:RTV-02; crypto:RTV-02 |
| ROUTE-§7.4-02 | 7.4 | MUST | deployment | behavioural_positive | Broker relay audit records MUST be stored in append-only manner | — | — | out-of-repo(infrastructure) |
| ROUTE-§7.4-03 | 7.4 | MUST_NOT | deployment | behavioural_negative | Broker audit records MUST NOT be modified or deleted until the applicable retention period expires | — | — | out-of-repo(infrastructure) |
| ROUTE-§7.4-04 | 7.4 | MUST | deployment | behavioural_positive | Broker audit records MUST survive broker restarts and infrastructure failures | — | — | out-of-repo(infrastructure) |
| ROUTE-§7.4-05 | 7.4 | MUST | deployment | behavioural_positive | Broker audit storage MUST use durable storage such as PostgreSQL or append-only replicated files | — | — | out-of-repo(infrastructure) |
| ROUTE-§7.4-06 | 7.4 | REQUIRED | external | structural | ArsiaAuditRecord event_type (string) is REQUIRED — fixed value "broker_relay" | arsia-audit-record | ITV-43 | schema-ref:arsia-audit-record; struct:ITV-43 |
| ROUTE-§7.4-07 | 7.4 | REQUIRED | external | structural | broker_relay record attestation_id (string) — UUID v4, unique per relay operation; present when forwarding was initiated, REQUIRED when forwarding_result is success | arsia-audit-record | ITV-43, ITV-688, INV-101, INV-103 | schema-ref:arsia-audit-record; struct:ITV-43, ITV-688, INV-101, INV-103 |
| ROUTE-§7.4-08 | 7.4 | REQUIRED | external | structural | ArsiaAuditRecord (event_type broker_relay).message_id (string) is REQUIRED — the id of the relayed message | arsia-audit-record | ITV-43 | schema-ref:arsia-audit-record; struct:ITV-43 |
| ROUTE-§7.4-09 | 7.4 | REQUIRED | external | structural | ArsiaAuditRecord (event_type broker_relay).from_agent (string) is REQUIRED — the from field of the relayed message | arsia-audit-record | ITV-43 | schema-ref:arsia-audit-record; struct:ITV-43 |
| ROUTE-§7.4-10 | 7.4 | REQUIRED | external | structural | ArsiaAuditRecord (event_type broker_relay).to_agent (string) is REQUIRED — the to field of the relayed message | arsia-audit-record | ITV-43 | schema-ref:arsia-audit-record; struct:ITV-43 |
| ROUTE-§7.4-11 | 7.4 | REQUIRED | external | structural | ArsiaAuditRecord (event_type broker_relay).broker_agent_id (string) is REQUIRED — the broker own agent-id | arsia-audit-record | ITV-43, INV-48 | schema-ref:arsia-audit-record; struct:ITV-43, INV-48 |
| ROUTE-§7.4-12 | 7.4 | REQUIRED | external | structural | ArsiaAuditRecord (event_type broker_relay).residency_zone (string) is REQUIRED — the zone this relay satisfies | arsia-audit-record | ITV-43 | schema-ref:arsia-audit-record; struct:ITV-43 |
| ROUTE-§7.4-13 | 7.4 | REQUIRED | external | structural | broker_relay record forwarded_at (string) — RFC 3339 timestamp with millisecond precision of the forwarding attempt; present when forwarding was initiated, REQUIRED when forwarding_result is success | arsia-audit-record | ITV-43, ITV-688, INV-101, INV-102 | schema-ref:arsia-audit-record; struct:ITV-43, ITV-688, INV-101, INV-102 |
| ROUTE-§7.4-14 | 7.4 | REQUIRED | external | structural | ArsiaAuditRecord (event_type broker_relay).payload_hash (string) is REQUIRED — SHA-256 hash of payload, hex-encoded | arsia-audit-record | ITV-43 | schema-ref:arsia-audit-record; struct:ITV-43 |
| ROUTE-§7.4-15 | 7.4 | REQUIRED | external | structural | ArsiaAuditRecord (event_type broker_relay).relay_latency_ms (integer) — forwarded_at − received_at in whole milliseconds; present when forwarding was initiated, REQUIRED when forwarding_result is success | arsia-audit-record | ITV-43, ITV-688, INV-101 | schema-ref:arsia-audit-record; struct:ITV-43, ITV-688, INV-101 |
| ROUTE-§7.4-16 | 7.4 | REQUIRED | external | structural | ArsiaAuditRecord (event_type broker_relay).forwarding_result (string) is REQUIRED — one of "success", "failure", "timeout" | arsia-audit-record | ITV-43, ITV-44, ITV-146, ITV-147 | schema-ref:arsia-audit-record; struct:ITV-43, ITV-44, ITV-146, ITV-147 |
| ROUTE-§7.4-17 | 7.4 | MUST | external | behavioural_positive | relay_latency_ms MUST be forwarded_at − received_at exactly, in whole non-negative milliseconds, measured to the initiation of forwarding | — | ITV-43, ITV-146, ITV-147, ITV-490, ITV-492, ITV-511, ITV-515, ITV-691 | struct:ITV-43, ITV-146, ITV-147, ITV-490, ITV-492, ITV-511, ITV-515, ITV-691; untested(structural-only) |
| ROUTE-§7.4-18 | 7.4 | MUST | external | structural | attestation_id, forwarded_at and relay_latency_ms MUST be present together when the broker initiated forwarding | arsia-audit-record | ITV-691, INV-102, INV-103 | schema-ref:arsia-audit-record; struct:ITV-691, INV-102, INV-103 |
| ROUTE-§7.4-19 | 7.4 | MUST | external | structural | attestation_id, forwarded_at and relay_latency_ms MUST be absent when the broker did not initiate forwarding | arsia-audit-record | ITV-508, ITV-688, ITV-689 | schema-ref:arsia-audit-record; struct:ITV-508, ITV-688, ITV-689 |
| ROUTE-§7.4-20 | 7.4 | MUST | external | behavioural_positive | forwarding_result MUST be success (ARSIA envelope or HTTP 202 relayed), timeout (Rule 9 refusal or §2.3.4 abandonment) or failure (every other case, before or after forwarding) | arsia-audit-record | ITV-43, ITV-146, ITV-147, ITV-508, ITV-688, ITV-689, ITV-691, INV-101 | schema-ref:arsia-audit-record; struct:ITV-43, ITV-146, ITV-147, ITV-508, ITV-688, ITV-689, ITV-691, INV-101; untested(structural-only) |
| ROUTE-§7.4-21 | 7.4 | MUST | sdk | behavioural_negative | Recipient MUST verify the relay attestation signature against the broker's JWKS; the kid must belong to broker_id | arsia-relay-attestation | ITV-569, INV-124, INV-125 | schema-ref:arsia-relay-attestation; struct:ITV-569, INV-124, INV-125; crypto:ITV-569, INV-124, INV-125; exec:R22:ITV-569, INV-124, INV-125 |
| ROUTE-§7.4-22 | 7.4 | MUST | sdk | behavioural_negative | Recipient MUST verify that the broker is an authorised Compliance Broker for the declared zone (jurisdiction satisfies the zone; declares arsiaprotocol.broker.relay) | arsia-relay-attestation | INV-121, INV-122 | schema-ref:arsia-relay-attestation; struct:INV-121, INV-122; crypto:INV-121, INV-122; exec:R22:INV-121, INV-122 |
| ROUTE-§7.4-23 | 7.4 | MUST | sdk | behavioural_negative | Recipient MUST verify envelope_hash against the received complete signed envelope and authorization_token_hash against the envelope's authorization.token_hash and the presented token | arsia-relay-attestation | ITV-569, INV-115, INV-116, INV-117 | schema-ref:arsia-relay-attestation; struct:ITV-569, INV-115, INV-116, INV-117; crypto:ITV-569, INV-115, INV-116, INV-117; exec:R22:ITV-569, INV-115, INV-116, INV-117 |
| ROUTE-§7.4-24 | 7.4 | MUST | sdk | behavioural_negative | Recipient MUST verify message_id, sender and recipient against the envelope and reject attestations outside [issued_at, valid_until] with the applicable clock skew | arsia-relay-attestation | INV-118, INV-119, INV-120 | schema-ref:arsia-relay-attestation; struct:INV-118, INV-119, INV-120; crypto:INV-118, INV-119, INV-120; exec:R22:INV-118, INV-119, INV-120 |
| ROUTE-§7.4-25 | 7.4 | MUST | sdk | behavioural_negative | Recipient MUST treat an attestation_id repeated for a different envelope_hash as invalid (a repetition with the same envelope_hash is not rejected by this rule) | arsia-relay-attestation | INV-123, ITV-693 | schema-ref:arsia-relay-attestation; struct:INV-123, ITV-693; crypto:INV-123, ITV-693; exec:R22:INV-123, ITV-693 |
| ROUTE-§7.4-26 | 7.4 | MUST | sdk | behavioural_negative | A failure in attestation verification steps 2-5 MUST be rejected with unauthorized | arsia-relay-attestation | INV-115, INV-116, INV-117, INV-118, INV-119, INV-120, INV-121, INV-122, INV-123, INV-124, INV-125, INV-172, INV-173, INV-174, INV-175, INV-176, INV-177 | schema-ref:arsia-relay-attestation; struct:INV-115, INV-116, INV-117, INV-118, INV-119, INV-120, INV-121, INV-122, INV-123, INV-124, INV-125, INV-172, INV-173, INV-174, INV-175, INV-176, INV-177; crypto:INV-115, INV-116, INV-117, INV-118, INV-119, INV-120, INV-121, INV-122, INV-123, INV-124, INV-125; exec:R22:INV-115, INV-116, INV-117, INV-118, INV-119, INV-120, INV-121, INV-122, INV-123, INV-124, INV-125, INV-172, INV-173, INV-174, INV-175, INV-176, INV-177 |
| ROUTE-§7.4-27 | 7.4 | MUST | sdk | behavioural_negative | When compliance.data_residency is set, a message arriving without the ARSIA-Relay-Attestation header MUST be rejected with service_unavailable and details data_residency_violation and required_zone (step 1); a present header, even with an empty value, is processed by steps 2-5 | — | ITV-570, ITV-712, INV-172 | struct:ITV-570, ITV-712, INV-172; exec:R22:ITV-570, ITV-712, INV-172 |
| ROUTE-§7.4-28 | 7.4 | MUST | sdk | behavioural_negative | The attestation header value MUST be non-empty base64url without padding (base64url alphabet, no '=', a length that decodes to whole octets); the decoded octets MUST pass ARSIA-Core.md §5.2 steps 2-4 and the object MUST validate against the attestation schema (step 2) | arsia-relay-attestation | ITV-711, INV-172, INV-173, INV-174, INV-175, INV-176, INV-177 | schema-ref:arsia-relay-attestation; struct:ITV-711, INV-172, INV-173, INV-174, INV-175, INV-176, INV-177; exec:R22:ITV-711, INV-172, INV-173, INV-174, INV-175, INV-176, INV-177 |
| ROUTE-§7.4-29 | 7.4 | MUST | sdk | behavioural_negative | A failure of the ARSIA-Core.md §5.2 steps 2-4 checks on the decoded attestation is a step 2 failure, rejected with unauthorized, not with invalid_request | — | INV-176 | struct:INV-176; exec:R22:INV-176 |
| ROUTE-§8-01 | 8 | MUST | external | procedural | Conformant implementations MUST pass all routing conformance tests at the applicable level | — | — | untested(integration) → docs/draft-02-conformance-tests.md |
| ROUTE-§8-02 | 8 | MUST | external | procedural | Expiration conformance tests MUST use an expires_at more than 300 seconds in the past to guarantee rejection | — | ITV-518 | struct:ITV-518; exec:R16:ITV-518 |
| ROUTE-§8-03 | 8 | MUST | external | procedural | Conformance test framework MUST synchronise clocks between agents for timing-sensitive tests | — | — | out-of-repo(transport) |

---

## Coverage Gaps

Generated: 2026-07-22 (Draft-02 regeneration — header-driven parser, reproducible via scripts/check_consistency.py companion tooling)

### Summary

| Metric | Count |
|--------|------:|
| Total requirements | 283 |
| Schema ≠ — | 119 |
| Vector ≠ — | 94 |
| Both ≠ — | 62 |
| Both = — (gaps) | 132 |

### Per-section breakdown

| § | Total | Schema ≠ — | Vector ≠ — | Both ≠ — | Both = — |
|---|-------|-----------|-----------|---------|---------|
| 1 | 51 | 21 | 17 | 9 | 22 |
| 2 | 86 | 22 | 8 | 7 | 63 |
| 3 | 6 | 2 | 0 | 0 | 4 |
| 4 | 9 | 4 | 3 | 1 | 3 |
| 5 | 24 | 11 | 4 | 2 | 11 |
| 6 | 16 | 6 | 2 | 0 | 8 |
| 7 | 88 | 53 | 59 | 43 | 19 |
| 8 | 3 | 0 | 1 | 0 | 2 |

## Draft-02 Delta (normative changes traced)

| Change | Anchor | Schema | Vectors |
|---|---|---|---|
| Dual authorization: broker.use (sender) vs broker.relay (broker); T_e2e forwarded verbatim | §1.2.2, §2.3.1-2.3.2 | — | ITV-571/572 |
| NEW relay attestation (relay evidence) + recipient obligations | §7.4.1 | arsia-relay-attestation | ITV-569/570, INV-31/32 |
| Recipient step 1 (header absent → service_unavailable) and step 2 header decoding (base64url without padding, Core §5.2 steps 2-4, schema; failures unauthorized) — coverage SC4 | §7.4.1 | arsia-relay-attestation | ITV-570, ITV-711, ITV-712, INV-172..177 |
| Broker audit = ArsiaAuditRecord event_type broker_relay (legacy record retired) | §7.4.2 | audit-record branch | 9 converted (ITV-43/44 …) |
| Token Exchange (RFC 8693) OPTIONAL profile | §2.3.2.1 | — | — |
| §5.1 item 4: recipient in-zone processing MUST + reject-when-unable | §5.1 | — | integration |
| residency codes: closed registry (ISO + EU); custom codes removed | §5.1 | arsia-common | — |
| lifecycle events = operational log (not canonical audit) | §4.1 | — | — |
| approval_decision never a sync inbox response | §2.1.2 | — | — |
| at-least-once = retries; idempotency = dedup | §1, §3 | — | — |
| DSA-VLOP storage floor P1096D | §7.4 | catalog | consistency check |
| broker_relay timing and outcome defined: relay_latency_ms = forwarded_at − received_at; forwarding fields present together only when forwarding was initiated; audit of messages not forwarded (Rule 7, Rule 9 MUST); recipient DPoP nonce challenge relayed to the sender; forwarded proof single-use (A-89, A-49) | §1.2.2, §2.3.2, §2.3.3, §7.3, §7.4.2 | audit-record, message | ITV-43, ITV-44, ITV-146, ITV-147, ITV-490, ITV-492, ITV-508, ITV-511, ITV-515, INV-48 migrated; ITV-688..691, INV-101..103, INV-108..110; harness R19, R20 |