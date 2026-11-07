<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 Arsia Labs (Arsia Tecnologia Unipessoal Lda) -->

# Auditoria do repositório da spec — ARSIA Protocol Draft-01/Draft-01.1

**Data:** 2026-07-22
**Escopo:** repositório `arsia-protocol-enterprise` @ `dacbc4a` — `spec/` (6 documentos), `schemas/` (27), `profiles/`, `docs/` (FAQ, RTMs), `results/`, `test-vectors/`, `scripts/`, CI. Somente leitura; nenhum arquivo modificado além deste relatório.
**Método:** leitura integral dos 6 documentos da spec, do catálogo de perfis e dos schemas centrais (message, common, compliance-field, audit-record, identity-record, discovery-response, jwt-claims, action-descriptor, explanation, jwk-entry, state-operations, websocket-frame); verificação cruzada de enums, gramáticas, defaults, exemplos e referências; leitura dirigida do material auxiliar. Achados sem âncora não entraram. O que não foi confirmável está em §6 (NÃO VERIFICADO).
**Insumo para:** decisão de Draft-02 (fora desta auditoria).
**Adendo oficial:** [auditoria-independente-spec-e-validacao-documentos-2026-07-22.md](auditoria-independente-spec-e-validacao-documentos-2026-07-22.md) — segunda auditoria independente que confirma os 53 achados deste baseline e acrescenta 16 achados materiais (ver §8).

---

## 1. Sumário executivo

**Contagem de achados:** 6 BLOQUEANTE · 15 ALTO · 24 MÉDIO · 8 BAIXO — 53 no total.

**Os 5 mais importantes (uma linha cada):**

1. **[B-05]** O roteamento via broker, como especificado, é inexecutável sob as próprias regras de token do Core: o destinatário é obrigado a rejeitar o relay (`sub` do token do broker ≠ `from` da mensagem, Core §6.4) e o sender precisaria de uma capability (`arsiaprotocol.broker.relay`) que Actions §1.4 proíbe conceder a não-brokers.
2. **[B-02]/[B-03]** O piso de retenção MiFID II tem dois comportamentos contraditórios (clampar+avisar em Core §4.3.6.4/§4.3.7 vs rejeitar em Core §4.3.8 Regra 4) e dois valores (1827 em Core/State/JSON/schemas vs 1825 em Assets/Actions/Identity) — os exemplos normativos do Assets (retention_days 1825 sob MIFID-II) são rejeitados por uma implementação conformante do Core.
3. **[B-04]** A lista fechada de capacidades reservadas (Actions §1.4) não contém `arsiaprotocol.echo`, `arsiaprotocol.health` nem `arsiaprotocol.onboarding.evaluate` — a Regra 5 de Actions §1.1 obriga rejeitá-las, invalidando os exemplos A.1/A.3 do Core, o fluxo de onboarding do Identity e o próprio teste de conformance do echo.
4. **[B-06]** O `pending_approval` tem dois formatos de payload mutuamente incompatíveis (`payload.args` em Actions §3.2/Core §4.4.7/schema vs `payload.result` em Assets §5.2/ASSETS-06) e o enum de decisão diverge (`approved|denied` vs `rejected`/`timeout`).
5. **[A-05]** O `ArsiaAuditRecord` grava o compliance **declarado** (`compliance.profile` da mensagem), não o **resolvido** pela cadeia de precedência do Core §4.3.7 — e o caso "compliance presente sem profile" nem sequer é definido — de modo que a trilha de auditoria não prova qual obrigação foi efetivamente aplicada.

**Vereditos das hipóteses:** H1 CONFIRMADA · H2 REFUTADA na forma forte, com gaps reais confirmados · H3 CONFIRMADA · H4 CONFIRMADA (detalhe em §4).

---

## 2. Tabela de achados

Severidades: **B** = BLOQUEANTE (contradição normativa ou erro que quebra implementação conformante) · **A** = ALTO (gap que força implementadores a inventar comportamento) · **M** = MÉDIO (inconsistência/ambiguidade real sem quebra) · **X** = BAIXO (editorial, clareza, oportunidade).

| ID | Sev | Documento/Seção | Descrição (1 frase) | Direção de correção (1 frase) |
|----|-----|-----------------|---------------------|-------------------------------|
| B-01 | B | Core §2.2 vs Core §4.2.1 / Actions §3.3 | Core §2.2 define `correlation_id` como "id da **request original**" para os 4 intents, mas Actions §3.3 exige que `approval_decision` correlacione o **pending_approval** ("NOT the original request's id"). | Alinhar a definição do §2.2 ao modelo "responde à mensagem imediatamente anterior" de §4.2.1/Actions §3.3. |
| B-02 | B | Core §4.3.6.4, §4.3.7 vs §4.3.8 Regra 4 | Para `retention_days` abaixo do piso, o Core manda simultaneamente clampar ao mínimo com warning (§4.3.6.4, §4.3.7) e rejeitar com `invalid_request` (§4.3.8 Regra 4, MIFID-II; STATE-13). | Escolher um único comportamento (por perfil ou global) e propagar a schemas e testes. |
| B-03 | B | Assets §6.1.2/§3.1.2/§3.2.2/§3.3.3, Actions §2.1/§7.2, Identity §9.3 vs Core §4.3.8 R4, State §6.3, profiles JSON, schemas | O piso MiFID é 1827 dias em Core/State/JSON/schemas e 1825 em Assets ("1825 days MINIMUM"), Actions (exemplo e refs) e Identity §9.3 (que cita State §6.3 com o valor errado); os exemplos do Assets com `retention_days: 1825` são inválidos sob a Regra 4 e sob o schema. | Padronizar 1827 (racional já documentado no FAQ) em todos os documentos e exemplos. |
| B-04 | B | Actions §1.1 R5/§1.4 vs Core §2.2/A.1/A.3, Identity §7.1.1/§8.1 | A Regra 5 manda rejeitar qualquer capability `arsiaprotocol.*` fora da lista fechada de §1.4, mas Core usa `arsiaprotocol.echo`/`arsiaprotocol.health` (exemplos e conformance) e Identity usa `arsiaprotocol.onboarding.evaluate`, `arsiaprotocol.code.review`, `arsiaprotocol.test.unit` etc. | Registrar as capacidades faltantes em §1.4 (ou criar um registro extensível de capacidades reservadas). |
| B-05 | B | Routing §1.2.2 (6b, 7b), §2.3.1-2.3.2 vs Core §6.4/§4.1.4, Actions §1.4 | O relay exige que o token do **sender** contenha `arsiaprotocol.broker.relay` (que Actions §1.4 proíbe conceder a não-brokers) e o broker apresenta ao destinatário um token próprio cujo `sub` não bate com o `from` da mensagem, que o Core §6.4 manda rejeitar com `unauthorized`. | Definir o modelo de autorização do relay (ex.: token do sender para o destinatário transportado com a mensagem, ou exceção explícita de binding para brokers) e separar "capability que o broker declara" de "escopo que o sender solicita". |
| B-06 | B | Assets §5.2/ASSETS-06 vs Actions §3.2-§3.3, Core §4.4.7, arsia-message.schema | `pending_approval` em Assets usa `payload.result` com campos próprios (`reason`, `human_oversight_required`, `summary`) enquanto Actions/Core/schema exigem `payload.args` com `action_id/original_request_id/approval_deadline/approver_capability/context/risk_level`; e o Assets usa `decision: "rejected"` e statuses `rejected/timeout` onde o enum normativo é `approved|denied` / `denied|expired`. | Reescrever os exemplos e o teste ASSETS-06 sobre o formato de Actions §3.2/§3.3 e unificar os enums. |
| A-01 | A | Core §5.2 p.2, §9.1; Identity §3.1 p.4 | Nenhum documento define como resolver um `agent-id` (ex.: `agent:acme.billing`) para o host onde vivem `/.well-known/arsia`, JWKS e inbox — "fetch the sender's JWKS endpoint" e "on the sender's domain" pressupõem um mapeamento que não existe. | Especificar o mecanismo de resolução (DNS, registro, configuração) ou declará-lo explicitamente out-of-band com requisitos mínimos. |
| A-02 | A | Identity §3.1 vs Core §4.3.5 (nota), §5.2, FAQ | Identity §3.1 diz "Every ARSIA message MUST carry a `security` object", contradizendo o Core (e o FAQ), que tornam a assinatura opcional para `event` e `error`. | Restringir o MUST de Identity §3.1 aos intents cobertos por Core §5.2. |
| A-03 | A | Core §4.3.6.1, §4.3.8 Regra 1 | O "strict mode" muda um SHOULD-warn para MUST-reject, mas nunca é definido: não há como ativá-lo, anunciá-lo no discovery ou prever o comportamento do peer. | Definir o modo estrito como flag de discovery/perfil ou removê-lo. |
| A-04 | A | Identity §6.4.3 vs Core §11.2 | Os códigos `certificate_invalid`, `certificate_expired`, `key_mismatch`, `certificate_revoked` não estão no registro fechado do Core §11.2 e violam a convenção do próprio Core (códigos custom em reverse-domain), embora o schema da mensagem os legitime. | Adicionar os códigos ao registro do Core §11.2 (com status HTTP) ou renomeá-los conforme a convenção. |
| A-05 | A | State §7.1 `compliance_profile` + audit-record schema vs Core §4.3.7 | O audit record grava o perfil **declarado** ("or 'none' if the message had no compliance field"), não o resolvido; o caso "compliance presente mas sem profile" (que resolve para GDPR-STANDARD) fica indefinido, e não há campos para os valores efetivos de `audit_required`/`human_oversight`/etc. | Definir campos para o compliance resolvido (e/ou declarado + efetivo) e cobrir o caso profile-ausente. |
| A-06 | A | Identity §4.1 vs State §7.1 + arsia-audit-record.schema (`additionalProperties: false`) | Identity exige que o `owner_id` de **ambas** as partes conste do audit record, mas o `ArsiaAuditRecord` só tem `operator_id` (o dono do log) e o schema proíbe campos adicionais — o MUST é inimplementável no formato canônico. | Adicionar campos de accountability da contraparte ao ArsiaAuditRecord ou rebaixar o requisito. |
| A-07 | A | arsia-message.schema (`additionalProperties: false`) vs Core §4.1.1, §7.4 | O Core exige aceitar/ignorar campos desconhecidos de minor versions futuras, mas o schema do envelope rejeita qualquer campo não listado, quebrando a compatibilidade progressiva prometida. | Permitir `additionalProperties` no envelope (ou documentar que o schema valida somente v1.0 estrita). |
| A-08 | A | arsia-message.schema (payload `not anyOf`) vs Core §4.4.7 | O Core §4.4.7 diz que múltiplos campos de conteúdo geram warning e "MUST process the field corresponding to the intent and MUST ignore the others", mas o schema torna `args`+`result` (etc.) estruturalmente inválidos. | Alinhar schema e prosa (validação soft ou proibição hard nos dois lados). |
| A-09 | A | arsia-compliance-field.schema / arsia-message.schema vs Core §4.3.8 Regra 3 | A Regra 3 exige `human_oversight` **efetivo** (per-message ou default de perfil), mas os schemas exigem o campo explícito na mensagem sempre que `ai_system_classification: "high-risk"`, rejeitando mensagens válidas cujo valor viria do perfil. | Remover o `required` condicional do schema ou documentar a divergência deliberada. |
| A-10 | A | Assets §6.1.1 (`updated_at`) vs Assets §6.1.2, State §7.2 | O registro de auditoria MiFID tem `updated_at` "updated when the receipt is received", mas a mesma seção (§6.1.2) e o State §7.2 exigem registros imutáveis append-only com correções por novo registro. | Substituir a atualização in-place por registro complementar vinculado (padrão já descrito em §6.1.2). |
| A-11 | A | Assets §3.2.1 (`pending`/`escrowed`), §4.2.1-§4.2.2 vs Core §4.1.6/§8.1 | Receipts subsequentes ("um `completed` SHOULD seguir o `pending`"; novo receipt na liberação do escrow) exigem uma segunda resposta ao mesmo request, mas o Core define um único response por correlation e nenhum mecanismo de entrega para o segundo receipt. | Definir o mecanismo (novo request/event do processor, status URL, ou webhook) e os campos de correlação. |
| A-12 | A | Assets §6.1 (condição 2) vs Identity §1.2 | O gatilho do audit MiFID depende de "from_agent ou to_agent é uma EU-regulated entity conforme declarado na IdentityRecord", mas a IdentityRecord não possui nenhum campo que declare status regulatório. | Adicionar o campo à IdentityRecord ou reformular a condição em termos de campos existentes (jurisdiction/profile). |
| A-13 | A | State §1.1 vs State §8.3 regra 4, §3.1.2 | Session scope diz "session state entries MUST NOT generate audit events", mas §8.3 manda que, com `compliance.audit_required: true`, **todas** as operações de state da mensagem gerem evento — um SET session-scoped sob perfil auditado cai nas duas regras. | Definir a precedência (ex.: exceção explícita de session scope em §8.3). |
| A-14 | A | Core §13 vs Core §9.2, Routing §5.3 | A residência de dados é imposta apenas pelo **sender** (nada no envelope atesta a passagem por broker; Routing §5.3 admite verificação "trust-based"), e o threat model do §13 não analisa o sender que ignora o broker, nem oversight/assets/state como superfícies (aprovador comprometido, escrow, PURGE indevido). | Estender o §13 aos mecanismos dos outros cinco documentos e considerar atestação de relay verificável pelo destinatário. |
| A-15 | A | compliance-field/message schemas vs Core §4.3.8 | Os schemas impõem mínimos de `retention_days` para PAC-AGRICULTURE (1096), DSA-VLOP (730) e DORA (1827), mas a prosa só define rejeição para MIFID-II (Regra 4) — para os demais perfis a prosa manda clampar (§4.3.6.4), tornando inválido no schema o que a prosa aceita. | Definir na prosa o comportamento por perfil e igualar os schemas. |
| M-01 | M | State §6.2/§6.3 vs profiles JSON, Core §8.3, State §6.7 | As tabelas de defaults de EU-AI-ACT-HIGH-RISK e MIFID-II omitem `clock_skew_seconds` (120/60) presente no JSON — e a nota do DORA (§6.7) afirma "matches the MIFID-II profile's clock_skew_seconds" que a tabela §6.3 não contém. | Incluir `clock_skew_seconds` nas tabelas de §6.2/§6.3. |
| M-02 | M | FAQ ("2-year uses 731") vs DSA-VLOP=730 (State §6.6, JSON, schemas) | A regra declarada de pior caso com anos bissextos daria 731 dias para 2 anos, mas o DSA-VLOP usa 730 em todos os artefatos. | Corrigir para 731 ou corrigir o racional do FAQ. |
| M-03 | M | Core §7.3 (`{keyN}`, exemplo `#enc1`) vs Identity §2.2 (`2026q1`), jwk-entry schema | O Core prescreve rótulo sequencial `{keyN}`, o Identity permite qualquer identificador alfanumérico curto e o schema aceita `[a-zA-Z0-9][a-zA-Z0-9_-]*` — três contratos diferentes para o `kid`. | Adotar a forma geral do Identity §2.2 no Core §7.3. |
| M-04 | M | Identity §7.2 Step 1, §7.8 vs Core §7.1 + discovery schema | O onboarding exige campo `capabilities` no discovery (o campo real é `capabilities_supported`) e o exemplo §7.8 usa `/.well-known/arsia/agent.json` (o endpoint normativo é `/.well-known/arsia`). | Corrigir nome de campo e caminho. |
| M-05 | M | Routing §7.3 R7 (`zone`) vs §7.4 (`residency_zone`); Core §9.2.4 (`ts`) vs §7.4; State §7.1 vs BrokerRelayAuditRecord | O audit de relay tem três contratos divergentes: nomes de campo diferentes no mesmo documento, o `ts` da mensagem exigido pelo Core e ausente do formato do Routing, e duas formas concorrentes (`event_type: broker_relay` no ArsiaAuditRecord vs `audit_type` num record separado sem `record_id`/`retained_until`/`operator_id`). | Unificar num único formato que estenda formalmente o ArsiaAuditRecord. |
| M-06 | M | Routing §4.1 (audit events) vs State §7.1 enum | Os eventos de lifecycle exigidos pelo Routing (`dispatch`, `dispatch_failed`, `delivery_failed`, `expired`, `request_received`, `response_sent`, `broker_relay` do sender) não existem no enum `event_type` do ArsiaAuditRecord/schema. | Adicionar os event types ou declarar que o log de lifecycle é operacional, fora do audit trail canônico. |
| M-07 | M | Assets §4.2 ("three possible terminal states"), §4.2.3, §4.2.4, §4.3 vs audit-record schema | DISPUTED é listado como terminal mas resolve para RELEASED/RETURNED, o heading "ESCROWED → CANCELLED" termina em RETURNED, e os campos de audit do escrow usam `audit_id`/`timestamp` onde o schema usa `record_id`/`processed_at`. | Corrigir a taxonomia de estados e alinhar os nomes de campos ao schema. |
| M-08 | M | State §1.5 (tabela) vs §1.2/§3.3, STATE-07 | A tabela de escopos diz que agent scope é legível apenas pelo dono, mas §1.2 e o GRANT (§3.3, STATE-07) permitem acesso de grantees a entradas agent-scoped — e a distinção funcional entre `shared` e `agent`+grant fica indefinida. | Corrigir a tabela e explicitar quando usar `shared` vs grant sobre `agent`. |
| M-09 | M | State §2.2 (Reserved Prefix) | A regra reserva o prefixo `arsiaprotocol.`, mas dois dos três exemplos de chaves reservadas usam `arsia.meta/…`, que a regra não cobre (um agente pode escrevê-las). | Migrar os exemplos para `arsiaprotocol.meta/…` ou reservar ambos os prefixos. |
| M-10 | M | Routing §2.1.2 vs Core §8.1 | O Routing permite `approval_decision` como corpo de resposta síncrona do inbox; o Core §8.1 restringe a resposta a `response`/`error`/`pending_approval`. | Alinhar as duas listas. |
| M-11 | M | Core §4.3.6.2, Routing §5.1 vs arsia-common (`^[A-Z]{2}$`) | O conjunto de identificadores supranacionais é aberto/ambíguo ("EU" é o único reconhecido; códigos regionais custom de "2-4 caracteres" colidem com ISO em 2 chars e são rejeitados pelo pattern de 2 letras dos schemas em 3-4 chars). | Definir um registro fechado de códigos regionais e um pattern coerente. |
| M-12 | M | arsia-message.schema (`id`) vs Core §4.1.2, arsia-common `uuid-v4` | O schema aceita apenas UUID minúsculo em `id`, mas o Core permite maiúsculas (SHOULD lowercase) e o `correlation_id` referencia o def que aceita ambos. | Igualar os patterns (e decidir se maiúsculas são válidas). |
| M-13 | M | Identity §9.1 vs Core §6.1/§6.4, jwt-claims schema | O onboarding permite `aud` como "wildcard audience", mas o Core exige `aud == to` e o schema restringe `aud` ao pattern de agent-id. | Especificar o formato e a validação do wildcard audience ou removê-lo. |
| M-14 | M | Identity §6.4.3 ("Core §8"), State §11.5 ("§2.1.3"), STATE-13 ("§8.3 Rule 2"), compliance-field schema ("Core §1.2"), Actions §3.5 ("180 days" sem âncora normativa própria) | Cinco referências cruzadas apontam para seções erradas ou inexistentes para o que afirmam. | Revisão sistemática de âncoras num passe editorial de Draft-02. |
| M-15 | M | Core §4.4.2, Actions §2.4 | `payload.version` ausente = "latest known to the receiving agent" (não determinístico entre peers) e não há descoberta de versões suportadas (o ActionDescriptor não expõe versão), deixando a negociação só reativa via `not_implemented`. | Adicionar versões suportadas ao ActionDescriptor/discovery e reconsiderar o default "latest". |
| M-16 | M | Identity §7.6 vs Actions §3.3 | A decisão de onboarding reutiliza o intent `approval_decision` com `capabilities: ["arsiaprotocol.onboarding.evaluate"]` e `correlation_id` = request inicial, violando os MUSTs de Actions §3.3 (`arsiaprotocol.oversight.approve` obrigatório; correlação ao `pending_approval`). | Isentar explicitamente o uso onboarding ou criar payload próprio sem colidir com o contrato de §3.3. |
| M-17 | M | Assets §3.2.1 (`audit_id` REQUIRED) vs §6.1 | `audit_id` é obrigatório em todo receipt, mas para transferências fora das condições do §6.1 (não-currency, sem perfil, sem audit_required) nenhuma regra exige gerar o registro que o `audit_id` referencia. | Tornar `audit_id` condicional ou exigir audit record para todo receipt. |
| M-18 | M | Core §12.4, §12.3 | Os 3 testes normativos do Core §12.4 cobrem só as Regras 2 e 6 das 8 regras de validação de compliance (Regras 1, 3, 7 e 8 têm apenas vetores `skip_schema`, sem teste de conformance em documento; a Regra 4 tem STATE-13 mas nenhum vetor) e a Full conformance depende de um runner externo (`@arsia-protocol/conformance-test`) fora do repo. | Completar os CORE-COMPLIANCE-* e versionar/referenciar o runner de forma verificável. |
| M-19 | M | State §7.1 vs arsia-audit-record.schema | Os campos de extensão por event_type (`key`, `version`, `sub_type`, `grant_id`, `approval_deadline`, etc.) são exigidos apenas pelo schema — a prosa de §7.1 não os lista como campos do ArsiaAuditRecord, então quem implementa pela prosa produz registros inválidos. | Documentar as extensões por event_type na prosa de §7.1. |
| M-20 | M | arsia-message.schema (`pending-approval-args.risk_level` min 1) vs Actions §2.1 (0-10) | Um action de `risk_level: 0` com `human_oversight_required: true` gera um `pending_approval` inválido no schema. | Alinhar o mínimo a 0. |
| M-21 | M | Actions §4.3 vs Core §8.1 | Há dois padrões assíncronos concorrentes (HTTP 202+Location no Core; response com `status_url` em Actions) sem regra de escolha ou equivalência. | Unificar ou definir quando usar cada um. |
| M-22 | M | results/audit-schemas-vectors.md vs test-vectors, arsia-state-entry.schema, State §2.1.10 | O relatório prévio em results/ está desatualizado em dois pontos: conta 559 vetores (o arquivo atual tem 613, com 73 `skip_schema`, como diz o FAQ) e reporta como aberto um MISMATCH de `data_residency` que o schema atual já resolveu (a invariante foi delegada ao runtime — descrição em `arsia-state-entry.schema.json`, sem `if/then` correspondente); permanece, porém, a autocontradição da prosa de State §2.1.10 item 2 ("`data_residency` MUST be set" vs "this is not a hard rejection"). | Regenerar o relatório de results/ e resolver a contradição interna de §2.1.10 (MUST vs SHOULD-warn). |
| M-23 | M | Core §4.3.6.9/§4.3.8 R6 vs Identity §4.2 | `unacceptable-risk` é aceito como valor per-message (e é o topo da hierarquia da Regra 6), mas Identity §4.2 manda rejeitar **todas** as mensagens de agentes com essa classificação — o valor per-message é logicamente inutilizável e mesmo assim válido nos schemas. | Proibir `unacceptable-risk` como valor per-message. |
| M-24 | M | Core Abstract/§1.1, Appendix B.3 | O documento se declara "open protocol" e "open-source compliance layer", mas o Appendix B.3 termina com "adoption requires a commercial licence or written permission from Arsia Labs" — posicionamentos incompatíveis no mesmo documento. | Harmonizar o statement de licenciamento com o posicionamento declarado. |
| X-01 | X | Core §3.2 | O exemplo `agent:arsialabs.demo.risk-assessor` é descrito na prosa como org-segment "arsia". | Corrigir a prosa para "arsialabs". |
| X-02 | X | Core §4.1.1 | O pattern `^\d+\.\d+$` aceita zeros à esquerda que a prosa proíbe ("no leading zeros"). | Apertar o pattern (`^(0|[1-9]\d*)\.(0|[1-9]\d*)$`). |
| X-03 | X | Actions §1.1 (exemplos), §1.4 | A prosa fala em "reserved `arsia` namespace/prefix" quando o prefixo reservado é `arsiaprotocol.`. | Uniformizar a redação. |
| X-04 | X | State §10.4 | O parágrafo de abertura está fora de ordem/duplicado (regra de "sensitive" citada antes de "personal", com referência a §2.1.10 para "authenticated encryption" que §2.1.10 não define). | Reescrever o parágrafo. |
| X-05 | X | State §5.2 | "The legal_basis requirement applies only to entries with pii_classification of 'personal'" contradiz o próprio §5.2 e §3.1.2 (que incluem `sensitive`). | Corrigir para "personal ou sensitive". |
| X-06 | X | Routing §7.4 | "extends the ArsiaAuditRecord base type (to be defined in ARSIA-State.md §7)" — a referência "a definir" está obsoleta (State §7 existe). | Atualizar a frase. |
| X-07 | X | docs/rtm/ | O RTM do Routing não tem a seção de sumário de cobertura que os outros cinco têm, e o RTM do Core tem uma linha para a seção "16", inexistente no Core. | Uniformizar o formato dos RTMs. |
| X-08 | X | Core §11.1 error `description` "MUST be written in English" vs `context.locale` | O envelope oferece locale para respostas humanas, mas descrições de erro são obrigatoriamente em inglês — tensão menor de design, sem regra de interação. | Notar a interação (ou relaxar para SHOULD). |

---

## 3. Achados detalhados por documento

### 3.1 ARSIA-Core.md

**[B-01] Contradição na definição de `correlation_id`.** Core §2.2 (Definitions, "Correlation ID"): "When an agent sends a response, error, pending_approval, or approval_decision message, it MUST include a `correlation_id` field whose value equals the `id` field of the **original request message**". Core §4.2.1 diz "MUST equal the `id` field of the **original message to which this message is a reply**". Actions §3.3 (tabela de envelope) fixa: "`correlation_id` | The `id` of the `pending_approval` message (**NOT the original request's id**)". Um implementador que siga §2.2 produz `approval_decision` que o passo 3 de Actions §3.4 ("Verify the correlation chain") manda rejeitar com `invalid_request`. Quebra de interoperabilidade entre implementações conformantes de leituras diferentes.

**[B-02] Piso de retenção: clampar ou rejeitar?** Core §4.3.6.4: "If a per-message value is lower than the profile minimum, the receiving agent MUST use the profile minimum and SHOULD log a compliance warning." Core §4.3.7 repete ("the effective value MUST be the profile's minimum"). Core §4.3.8 Regra 4: para MIFID-II com efetivo < 1827, "the message MUST be rejected with error code `invalid_request`". STATE-13 (State §9) testa a rejeição. Ambos são MUSTs sobre o mesmo input; não há regra de precedência. Registre-se a leitura alternativa possível — Regra 4 como *lex specialis* de MIFID-II sobre a regra geral de clamp — mas ela não está escrita em lugar nenhum, e §4.3.6.4/§4.3.7 formulam o clamp sem exceção ("If a per-message value is lower than the profile minimum, the receiving agent MUST use the profile minimum"), o que mantém a contradição para o caso MIFID-II; um Draft-02 que pretenda a leitura *lex specialis* precisa apenas declará-la.

**[B-04] Capacidades reservadas: a lista fechada rejeita o próprio protocolo.** Actions §1.1 Regra 5: "Implementations MUST reject capability requests that use the `arsiaprotocol.` prefix **unless** the capability is one of the reserved system capabilities defined in §1.4." A lista de §1.4: `oversight.approve`, `broker.relay`, `audit.read`, `identity.admin`, `state.read/write/purge/snapshot`, `assets.transfer.initiate/approve/reverse`, `assets.escrow.create/release/cancel`, `assets.audit.read`, `compliance.breach.notify`. Fora da lista, mas usados normativamente: `arsiaprotocol.echo` (Core §2.2, A.1, capability de conformance), `arsiaprotocol.health` (Core A.3), `arsiaprotocol.onboarding.evaluate` (Identity §7.1.1 — MUST do gateway), além dos exemplos de política `arsiaprotocol.code.review`/`arsiaprotocol.code.refactor`/`arsiaprotocol.test.unit` (Identity §8.1, IDENTITY-16-18).

**[A-01] Resolução agent-id → URL.** Core §5.2 passo 2 ("fetching the sender's JWKS endpoint — identified by the agent identifier in the `from` field"), Core §9.1 item 1 ("resolve the recipient's inbox URL from the discovery endpoint (§7.1)") e Identity §3.1 passo 4 ("on the sender's domain") assumem que se conhece o host a partir do agent-id. O formato `agent:acme.billing` não é um hostname e nenhuma seção define registro, convenção DNS ou configuração. Dois implementadores razoáveis divergem já no primeiro passo de qualquer verificação de assinatura.

**[A-03] "Strict mode" indefinido.** §4.3.6.1 e §4.3.8 Regra 1 dividem o comportamento entre "non-strict (default)" e "strict mode (implementation-configurable)". Não há como o sender saber em qual modo o receptor está (nenhum flag em §7.1), nem definição de escopo (por agente? por perfil? por mensagem?).

**[A-07]/[A-08]/[M-12]** Schema vs prosa do envelope: ver tabela — três casos onde `arsia-message.schema.json` é mais estrito do que a prosa normativa permite (campos desconhecidos, exclusividade de conteúdo, case do UUID). Nota: o pattern corrigido pela ERRATA-01 de `payload.type` **está** propagado a `arsia-common.schema.json` (`payload-type`) — verificado.

**[A-14] Threat model incompleto e enforcement declarativo de residency.** §13.1 cobre 6 vetores centrados em transporte/chaves/broker. Não são analisados: (i) sender que ignora o broker — o destinatário não tem como detectar (nenhuma atestação de relay no envelope; Routing §5.3 chama a verificação de "trust-based" mas o §13 não registra o residual); (ii) aprovador (`arsiaprotocol.oversight.approve`) comprometido — a capability mais sensível do protocolo (Actions §1.4) não aparece no threat model; (iii) abuso de PURGE (destruição irreversível autorizada por token); (iv) escrow (release_agent comprometido). A privacidade (§13.3) declara "agent identifiers contain no PII" com enforcement apenas declarativo (regra §3.3-3, sem verificação definida em onboarding ou discovery) — parcialmente mitigado pela nota de pseudonimização do `operator_id` em State §7.1.

**[M-24] "Open protocol" vs licença comercial.** Abstract: "ARSIA … is an open protocol"; Appendix B.3: "ARSIA provides a ready-made, **open-source** compliance layer" e, no mesmo parágrafo final, "adoption requires a commercial licence or written permission from Arsia Labs". Para uma spec dirigida a uma comunidade de standards (AAIF), a contradição é material.

Outros: [B-03] (exemplos 1825 — ver §3.3 Assets), [A-04] (códigos de certificado — ver §3.4 Identity), [A-05]/[A-06] (audit — ver §3.5 State), [M-11], [M-18], [X-01], [X-02], [X-08], e a nota informativa de §4.3.6 que referencia "(§1.2)" para perfis (âncora fraca, agregada em M-14).

### 3.2 ARSIA-Actions.md

**[B-06 - lado Actions]** §3.2 define o payload do `pending_approval` como `payload.args` com 6 campos obrigatórios; §3.3 define `payload.result` de `approval_decision` com `decision ∈ {approved, denied}`, `approver_id`, `reason`, `conditions`. O schema (`pending-approval-args`, `approval-decision-result`) segue Actions. O Assets contradiz ambos (ver §3.3).

**[M-15/H2]** §2.4 define bump rules e `not_implemented` com `supported_versions` para versões de action não suportadas — mas o ActionDescriptor (§2.1) não tem campo de versão, então não há descoberta proativa; e a regra vale para actions, não para payload types genéricos (eventos, receipts).

**[M-18 - cobertura]** §3.5 afirma "The minimum retention period for high-risk actions (risk_level ≥ 7) is 180 days" — o valor coincide com o default do perfil EU-AI-ACT-HIGH-RISK (State §6.2), mas como requisito por **risk_level** não existe em lugar nenhum (um action risk 8 sob GDPR-STANDARD não tem piso de 180 dias por nenhuma regra); afirmação sem âncora normativa (agregado em M-14).

**[M-20]** `pending-approval-args.risk_level` com mínimo 1 no schema vs 0-10 na prosa.

Outros: [B-01] (correlation), [B-04] (lista §1.4), [X-03]. A tabela de deadlines recomendados (§3.2 passo 3) cobre apenas risk 7-10 — actions de risco menor com `human_oversight_required: true` ficam sem recomendação (registrado como parte de M-14/editorial).

### 3.3 ARSIA-Assets.md

**[B-03] 1825 vs 1827.** §6.1.2: "**Retention period:** 1825 days (5 years) MINIMUM." Exemplos §3.1.2, §3.2.2 e §3.3.3 usam `compliance: { "profile": "MIFID-II", "retention_days": 1825 }` — sob Core §4.3.8 Regra 4 e sob o `if/then` do schema (`minimum: 1827`), essas mensagens são **inválidas**. ASSETS-07 exige "`retention_days` is ≥ 1825". Actions §2.1 (exemplo, 1825) e §7.2 ("minimum 5 years / 1825 days"), e Identity §9.3 ("this is 1825 days (5 years) per ARSIA-State.md §6.3" — citação incorreta: State §6.3 diz 1827) espalham o valor errado. O FAQ documenta exatamente por que 1827 é o correto.

**[B-06 - lado Assets]** §5.2 passo 3: `pending_approval` com `payload.result` e campos `action_id/risk_level/reason/human_oversight_required/summary`; passo 4: `approval_decision` com `approver`/`justification` (campos inexistentes em §3.3 de Actions); passo 5: "If the `approval_decision` has `decision: "rejected"`" (enum é `approved|denied`). §6.1.1: `human_oversight_status ∈ {…, "rejected", "timeout"}` vs `{…, "denied", "expired"}` em State §7.1/schema. ASSETS-06 fixa as expectativas no formato errado (`payload.result.*`).

**[A-10]** §6.1.1 `updated_at`: "Updated when the receipt is received" — no mesmo §6.1.2: "retained audit records are immutable — once written, they MUST NOT be modified… Corrections MUST be implemented by appending a new audit record".

**[A-11]** §3.2.1 status `pending`: "A subsequent AssetTransferReceipt with status `completed` or `failed` SHOULD follow" — sem definir como este segundo receipt é entregue/correlacionado (o Core prevê 1 response por request; um response não solicitado não tem gatilho; um `event` mudaria o shape). O mesmo vale para o novo receipt do escrow em §4.2.1-§4.2.2/§4.2.4.

**[A-12]** §6.1 condição 2 depende de "EU-regulated entity (as declared in their IdentityRecord)" — campo inexistente na IdentityRecord (§1.2 de Identity e schema). O custo da decisão recai sobre o receptor, que não tem a informação.

**[M-07]** §4.2: "exactly one initial state and three possible terminal states" com diagrama RELEASED/RETURNED/DISPUTED — mas §4.2.3 suspende o timeout e resolve DISPUTED para RELEASED/RETURNED (não-terminal), e §4.2.4 adiciona a transição de cancelamento (heading "ESCROWED → CANCELLED", resultado RETURNED). Os audit records de escrow (§4.3.1-§4.3.4) usam `audit_id` e `timestamp` onde o ArsiaAuditRecord/schema usam `record_id` e `processed_at`; `from_agent`/`to_agent` são payer/payee no escrow e sender/recipient no record base — semânticas colidem quando o processador é um terceiro.

**[M-17]** `audit_id` REQUIRED em todo receipt sem obrigação universal de gerar o registro correspondente.

Nota positiva: a fronteira de escopo (§1) e a separação infra/negócio do DORA (§6.2.1) são precisas e verificáveis; o schema do transfer-request implementa as precisões decimais por asset_type via `multipleOf` (confirmado no relatório prévio de schemas).

### 3.4 ARSIA-Identity.md

**[A-02]** §3.1: "Every ARSIA message MUST carry a `security` object with `alg`, `kid`, and `sig`" — contradiz Core §4.3.5 (nota: opcional para `event`/`error`), Core §5.2 (verificação RECOMMENDED para event/error) e o FAQ ("two of the six intent types — event and error — do not require signatures"). Um receptor implementando Identity rejeita eventos legítimos de um sender implementando Core.

**[A-04]** §6.4.3 define 4 códigos de erro novos em snake_case. Core §11.2: "Implementations MAY define additional application-specific error codes **using the reverse domain notation** … custom codes … **cannot collide with future standard code additions**". Os códigos de certificado violam a convenção e não constam do registro; o schema da mensagem os incluiu no enum "padrão", consagrando a divergência. A âncora "§6.4.3 … defined in ARSIA-Core.md §8" aponta para Transport Bindings (correto seria §11).

**[A-06]** §4.1: para mensagens com `audit_required: true`, "The `owner_id` of both parties MUST be included in the corresponding audit record (ARSIA-State.md §7)". O ArsiaAuditRecord (§7.1/schema) tem apenas `operator_id` ("the agent that owns this audit log") e o schema fecha `additionalProperties`.

**[M-16]** §7.6 reutiliza o intent `approval_decision` para a decisão de onboarding com `capabilities: ["arsiaprotocol.onboarding.evaluate"]` e `correlation_id` = mensagem inicial de onboarding. Actions §3.3: "The `approval_decision` message MUST include `arsiaprotocol.oversight.approve` in its `capabilities` array" e o receptor "MUST verify" isso; §7.1.3 do Identity afirma que o onboarding "does NOT define new message types" — mas o uso viola o contrato existente do intent.

**[M-04]** §7.2 Step 1: o discovery "MUST include `agent_id`, `protocol_version`, and `capabilities` fields" — o campo normativo (Core §7.1, schema) é `capabilities_supported`; §7.4 idem ("capabilities array from ARSIA-Core.md §7.2", que é outro endpoint). §7.8 usa `/.well-known/arsia/agent.json`.

**[M-13]** §9.1: `aud` "SHOULD be set to the infrastructure router's agent-id **or a wildcard audience**" — sem formato definido, contra Core §6.4 (aud MUST == to) e o pattern agent-id do jwt-claims schema.

Outros: [B-04] (`onboarding.evaluate` fora de §1.4), [B-03] (1825 em §9.3), [M-03] (kid), CHECK-04 cita "RECOMMENDED but not REQUIRED at Core Conformance level (Core §12.1)" — §12.1 não menciona o endpoint de audit (agregado em M-14). O uso de `nbf` em §3.2 é validado na prosa mas rejeitado pelo jwt-claims schema (`additionalProperties: false`) — já apontado pelo relatório prévio de schemas e não corrigido (agregado em M-22).

### 3.5 ARSIA-State.md

**[A-05]** §7.1 `compliance_profile`: "The compliance profile name from the message's `compliance.profile` field, or 'none' if the message had no `compliance` field". (i) O caso "campo `compliance` presente sem `profile`" — que pela precedência do Core §4.3.7 resolve para GDPR-STANDARD — não tem valor definido. (ii) O registro é a **declaração** do sender, não o resolvido: nenhum campo captura os valores efetivos pós-cadeia de precedência (o único efetivo é `retained_until`). A spec não distingue declarado de resolvido → o gap do escopo da auditoria está **confirmado**. O memo `results/spec-sender-verification.md` chega à mesma leitura por outro caminho e documenta uma implementação real desviando exatamente aqui.

**[A-13]** §1.1: "Session state entries MUST NOT generate audit events" vs §8.3 regra 4: "If the envelope's `compliance.audit_required` is `true`, all state operations in that message MUST generate audit events, regardless of the implementation's default audit configuration".

**[M-19]** A prosa de §7.1 define 15 campos do ArsiaAuditRecord; as operações (§3.1.2, §3.3, §3.2.2) e o Assets/Actions exigem eventos com campos (`key`, `version`, `actor_agent_id`, `grant_id`, `sub_type`, `approval_deadline`, …) que só o schema documenta como parte do record.

**[M-01]** §6.2/§6.3 omitem `clock_skew_seconds` (120 e 60 no JSON); §6.7 afirma que o valor do DORA "matches the MIFID-II profile's" — que a tabela de §6.3 não tem. Como o Core §8.3 dá efeito normativo ao campo (substitui o default de ±300s), a omissão muda o comportamento de quem implementa pela prosa.

**[M-08]/[M-09]/[X-04]/[X-05]** — ver tabela. Oportunidade correlata: a sobreposição funcional entre escopo `shared` e `agent`+GRANT (nenhuma operação exige `shared`; §3.3 opera sobre chaves `agent`) é candidata a simplificação no Draft-02.

### 3.6 ARSIA-Routing.md

**[B-05]** Dois defeitos compostos no fluxo brokered (§1.2.2):
1. Passo 6b: "Verify the sender's access token. The token MUST include the `arsiaprotocol.broker.relay` capability" (idem §2.3.1: "token that authorises the sender to use the broker's … capability"). Actions §1.4 sobre `broker.relay`: "MUST only be granted to agents that operate as Compliance Brokers". Um Authorization Server conformante de Actions não pode emitir o token que o Routing exige do sender.
2. Passo 7b/§2.3.2: o broker "obtains an access token for the recipient" e faz o POST. No destinatário, Core §6.4 passo 3 exige `sub == message.from` e Core §4.1.4 manda rejeitar com `unauthorized` quando não bate. O token do broker tem `sub` = broker; o `from` da mensagem é o sender original (imutável por §9.2.3). O relay conformante é, portanto, rejeitado por um destinatário conformante. Nenhum documento define exceção de binding, encaminhamento do token original do sender (cujo `aud` seria o destinatário — mas aí o broker não teria como obtê-lo) ou emissão delegada.

**[M-05]/[M-06]** — contratos divergentes do audit de relay e event types de lifecycle ausentes do enum canônico (ver tabela).

**[M-10]** §2.1.2 admite `approval_decision` como resposta síncrona do inbox; Core §8.1 não.

**[M-11]** §5.1 permite códigos regionais custom "2-4 characters … to avoid conflict with ISO 3166-1 country codes" — logicamente invertido para 2 chars (é exatamente o espaço ISO) e estruturalmente inválido para 3-4 chars sob o pattern `^[A-Z]{2}$` usado por `compliance.data_residency` nos schemas.

Nota: a exigência de avaliar o algoritmo de topologia **por mensagem** (§1.3, invariants) combinada com broker discovery + verificação de IdentityRecord do broker implica custo de latência não discutido — o caching de §7.2 (5 min) mitiga; registrado como observação, não achado.

### 3.7 Schemas e catálogo de perfis

Além dos itens já listados ([A-07], [A-08], [A-09], [A-15], [M-12], [M-20], [M-22]):

- **Catálogo (`profiles/arsia-compliance-profiles.json`)**: consistente com State §6 em todos os defaults **exceto** os `clock_skew_seconds` extra (M-01). MIFID-II com `retention_days: 1827` confirma B-03.
- **`arsia-compliance-field.schema.json`** é duplicado dentro de `arsia-message.schema.json` (propriedades inline + regras repetidas no `allOf` do envelope) em vez de referenciado por `$ref`. Verificação em segunda passada: as duas cópias são hoje substantivamente equivalentes — inclusive a regra high-risk→human_oversight existe em ambas (no message schema, no `allOf` de nível de envelope) — de modo que o problema é o risco de deriva de manutenção, não uma divergência atual.
- **`arsia-audit-record.schema.json`**: bem construído por event_type, mas sem os campos exigidos por Identity §4.1 (A-06), sem os event types de Routing §4.1 (M-06) e com o BrokerRelayAuditRecord fora (M-05).
- **`arsia-discovery-response.schema.json`**: fiel ao Core §7.1; `additionalProperties: false` impede extensões de discovery (mesma tensão de A-07, menor).
- **`arsia-jwk-entry.schema.json`**: pattern do `kid` segue Identity §2.2 (forma geral), divergindo do `{keyN}` do Core §7.3 (M-03).
- **Errata ERRATA-01**: propagada corretamente a `arsia-common.schema.json#payload-type` e `arsia-action-descriptor.schema.json` — verificado, sem achado.
- **Exemplos dos apêndices do Core**: assinaturas ilustrativas têm 86 caracteres (comprimento correto para Ed25519 base64url sem padding) — verificado por script; A.2 usa `retention_days: 180` = piso do perfil (válido).

### 3.8 Material auxiliar (FAQ, RTMs, results, vetores, CI)

- **FAQ**: em geral fiel à spec; dois problemas: o racional de anos bissextos implica 731 dias para 2 anos enquanto DSA-VLOP usa 730 em todos os artefatos (M-02); e "613 test vectors / 70+ skip_schema" diverge do relatório `results/audit-schemas-vectors.md` (509 pass / 50 skip = 559) — o arquivo atual tem de fato 613/73, ou seja, o relatório em results/ está desatualizado (M-22).
- **RTMs**: formato sólido (ID, §, modal, layer, kind, schema, vector), mas o RTM do Routing não tem o sumário de gaps dos demais e o do Core lista uma seção "16" inexistente (X-07). Os números de cobertura foram usados na matriz do §5.
- **CI** (`validate-vectors.yml`): valida meta-schema, vetores e error-paths — cobre schemas/vetores, não a consistência prosa↔prosa (todo o conjunto B/A acima passa despercebido pela CI atual).
- **`results/spec-sender-verification.md`**: análise consistente com esta auditoria (sender=`from`; audit espelha o envelope); a "nuance 2" do memo já sugere a direção que o A-05 formaliza (campo separado para perfil imposto por política).

---

## 4. Veredito das hipóteses H1-H4

**H1 — Não existe mecanismo de extensão de perfis de compliance: CONFIRMADA.**
Evidência: Core §4.3.6.1 enumera os 7 nomes conhecidos; Core §4.3.8 Regra 1 só admite "a known profile name as defined in ARSIA-State.md §6 **or in a future extension of this specification**" — ou seja, extensão apenas por revisão da própria spec; nomes desconhecidos → warning/reject. State §6 define os 7 perfis sem regra de nomeação para terceiros. VERSIONING.md declara "New compliance profiles … are extensions … published as separate documents", mas não existe namespacing (nada análogo ao reverse-domain de `payload.type`, Core §4.4.1), registro, nem semântica de descoberta além da lista plana `compliance_profiles_supported` (Core §7.1). O FAQ ("Why don't compliance profiles have per-profile versioning?") confirma o modelo "novo perfil = novo nome" sem resolver colisão de nomes entre organizações. Contraste direto com a extensibilidade de payload types.

**H2 — Não existe semântica de versionamento para payload types que evoluíram: REFUTADA na forma forte; gaps parciais CONFIRMADOS.**
Existe mecanismo: Core §4.4.2 define `payload.version` (formato, default) e Actions §2.4 define bump rules MAJOR/MINOR, coexistência na migração e o erro `not_implemented` + `supported_versions` para versão não suportada. Gaps confirmados: (i) sem descoberta — o ActionDescriptor (Actions §2.1/schema) não expõe versões suportadas, então a negociação é apenas reativa por erro; (ii) o default "assumed to be the **latest version known to the receiving agent**" (Core §4.4.2) é não-determinístico entre peers e pode executar semântica diferente da pretendida pelo sender; (iii) a semântica de §2.4 cobre actions — payload types que não são actions (receipts, eventos, breach-notification) não têm regra de evolução.

**H3 — Não existe referência causal tipada além do `correlation_id` 1:1: CONFIRMADA.**
O único mecanismo genérico é `correlation_id` = id da mensagem imediatamente anterior (Core §4.2.1). Cadeias mais longas existem, mas cada primitiva inventa seu próprio campo ad hoc: `original_request_id` (Actions §3.2), `original_message_id` (rollback, Actions §4.2), `original_payment_reference` (Assets §3.3.1), `original_audit_id` (Assets §4.3.2-§4.3.4), `breach_id` para atualizações de notificação (State §5.7), `payment_reference` como elo de ciclo de vida (Assets §3.1.1). Não há nada tipado para derived-from, supersedes ou in-reply-to multi-hop — a reconstrução de cadeias em auditoria depende de conhecimento por-payload-type.

**H4 — A temporalidade do State é de eixo único: CONFIRMADA.**
SNAPSHOT (State §3.2.1) aceita um único `as_of`; o histórico de versões (§2.4) indexa por `updated_at`. Não há segundo eixo (transaction time) — não é possível perguntar "o que o sistema **acreditava** em T1 sobre o estado em T0". O ArsiaAuditRecord distingue `timestamp` (evento) de `processed_at` (ingestão) — schema, descrições — mas isso não se estende ao state store nem ao SNAPSHOT. Para disputas regulatórias ("o agente decidiu com base em que versão do dado?"), o eixo único obriga soluções fora do protocolo.

---

## 5. Matriz MUST × conformance

Duas camadas de verificação existem no repo: os testes de conformance dos próprios documentos (CORE-COMPLIANCE-01..03, ACTIONS-01..12, IDENTITY-01..20, STATE-01..15, ROUTING-01..10, ASSETS-01..08 = 68 testes) e a malha schema+vetores rastreada pelos RTMs.

### 5.1 Cobertura agregada (fonte: docs/rtm/*.rtm.md; Routing recontado por script)

| Documento | Requisitos rastreados | Sem schema **e** sem vetor |
|---|---:|---:|
| Core | 388 | 162 (42%) |
| Actions | 323 | 119 (37%) |
| Assets | 256 | 88 (34%) |
| Identity | 257 | 104 (40%) |
| Routing | 262 | 127 (48%) |
| State | 382 | 147 (38%) |
| **Total** | **1868** | **747 (40%)** |

Os RTMs não separam modal nos sumários (os gaps incluem MAY/SHOULD); a lista abaixo isola MUSTs estruturais/comportamentais sem teste correspondente (nem §12/testes de documento, nem schema, nem vetor), com o ID do RTM quando existente.

### 5.2 MUSTs normativos sem teste de conformance correspondente (seleção dos estruturais)

| Requisito (MUST) | Âncora | RTM | Observação |
|---|---|---|---|
| Armazenar chave de idempotência pela duração de `idempotency.expires_at` e devolver a resposta original em duplicata | Core §10.2-10.3 | CORE-§2.2-09/10 (— / —) | ROUTING-06 cobre o caso feliz; retenção/expiração/409 in-progress sem teste |
| Rejeitar processamento após `expires_at` (MUST NOT process) | Core §4.2.2 | CORE-§4.2.2-02 (— / —) | ROUTING-08 cobre a rejeição na entrega; não o processamento tardio pós-aceite |
| Roteamento por broker quando `data_residency` setado — enforcement no lado receptor | Core §9.2 / Routing §1.2.2 | CORE-§2.2-12 (— / —) | ROUTING-02/03 testam o sender; nada verifica que o receptor detecte violação (cf. A-14) |
| Regras de validação de compliance 1, 3, 4, 5, 7 e 8 | Core §4.3.8 | — | §12.4 só testa Regras 2 e 6; nos documentos, Regra 4 tem STATE-13 (contraditório com §4.3.6.4, cf. B-02) e Regra 5 tem ROUTING-02/03 (lado sender apenas); Regras 1, 3, 7 e 8 têm somente vetores `skip_schema` (ITV-416, ITV-421, ITV-553/554, ITV-555/INV-20) sem teste de conformance em documento; Regra 4 sem vetor; o `oversight_timeout` de §4.3.6.5 (`required_within_24h`) não tem teste nem vetor |
| Media type `v` deve igualar o major do envelope; 415 para Content-Type não suportado | Core §8.1/§14.1 | Core §14: 2 reqs vector-only parciais | Sem teste de conformance dos documentos |
| WebSocket: auth handshake, close codes 4001/4002/4003, heartbeat | Core §8.2 | Core §8: 30/41 sem cobertura | ROUTING-09/10 cobrem só auth ok/fail |
| Rotação de chaves: overlap ≥ 24h, remoção imediata em comprometimento, cache JWKS ≤ 24h | Core §7.3 / Identity §2.4-2.5 | Identity §2: 20/27 sem cobertura | IDENTITY-07/08 cobrem overlap; revogação e caching sem teste |
| Broker: MUST NOT ler/logar payload, MUST NOT armazenar envelope, forward ≤ 10s | Routing §7.3 R4/R8, §2.3.4 | ROUTE-§7.3-25/26 (— / —) | Não-observáveis por vetor; exigiriam teste comportamental |
| Retenção física: não deletar antes do período; pós-retenção com arquivamento 12 meses | State §4.1/§4.3, §7.3 | State §4: 24/34 sem cobertura | STATE-05 cobre 1 caso; arquivamento sem teste |
| PURGE: propagação a réplicas/backup (24h/30d), revogação automática de grants, idempotência | State §3.2.2 | State §3 parcial | STATE-03 cobre o caso base; propagação/idempotência sem teste |
| Encriptação at rest para `personal`/`sensitive` | State §10.4 | State §10: 17/22 sem cobertura | Sem teste (comportamental) |
| Sandboxing por risk tier (processo/container, egress restrito) | Actions §4.4 | Actions §4: 31/52 sem cobertura | ACTIONS-11 declara verificação "implementation-specific" |
| Two-party: AS MUST NOT emitir token com initiate+approve juntos | Assets §5.1.2 | — | Sem teste; exigiria vetor de política do AS |
| DORA: classificação infra vs negócio e geração do evento | Assets §6.2 | Assets: 88/256 sem cobertura | ASSETS-08 cobre 1 caminho (provider timeout) |
| Certificados: cadeia, SAN, key-mismatch, revogação L3 (OCSP/CRL) | Identity §6.4 | Identity §6: 27/51 sem cobertura | IDENTITY-10-12 cobrem L2 básico; L3/revogação sem teste |
| Onboarding: fases em ordem, deny-by-default, token exato ao effective_capabilities | Identity §7/§9.1 | Identity §7: 19/75 sem cobertura | IDENTITY-13-20 cobrem os principais caminhos; ordem das fases e escopo exato sem teste |

### 5.3 Observações estruturais

- O Core §12.4 é a única ponte normativa entre "regras de compliance" e "testes" e cobre 2 das 8 regras; a Full conformance (§12.3) delega "pass the conformance test suite at 100%" a um pacote externo (`@arsia-protocol/conformance-test`) que não está no repositório nem é versionado por hash — o critério de Full conformance não é verificável a partir do repo (M-18).
- Compliance conformance (§12.2) exige "at least one compliance profile" e "audit trail" sem apontar quais testes provam cada linha da tabela; um mapeamento linha→teste (como os RTMs já fazem para schema/vetor) fecharia o ciclo.

---

## 6. NÃO VERIFICADO

Itens fora do que pôde ser confirmado por leitura, com o motivo:

1. **Criptografia dos vetores CTV** (chaves, bytes canônicos, assinaturas em `test-vectors/`): não recomputada nesta auditoria (execução de código de validação estava fora do escopo de leitura; a CI do repo executa `validate_vectors.py`, mas seu resultado não foi reproduzido aqui).
2. **`arsia-test-vectors.json` vetor a vetor** (16.820 linhas): verificado por contagens (613 vetores, 73 `skip_schema`, categorias) e pela amostragem do relatório prévio em `results/`; não houve revisão integral de cada vetor contra a seção citada.
3. **Schemas lidos apenas pontualmente**: `asset-transfer-receipt/reversal`, `audit-query-response`, `broker-entry/relay-audit/discovery-request`, `capability-descriptor/policy`, `dora-incident`, `breach-notification`, `dpop-proof`, `onboarding-decision`, `mifid-audit-record`, `state-entry` (via relatório prévio), `action-discovery-response`, `escrow-conditions` — checados por grep dirigido e pelo `results/audit-schemas-vectors.md`, não integralmente; achados neles podem estar subnotificados.
4. **Referências externas registradas e não seguidas** (conforme regra do escopo): `packages/sandbox/local-ca/` (Identity §6.7), `@arsia-protocol/conformance-test` (Core §12.3), URLs `arsiaprotocol.org/spec/*`, `github.com/arsialabs/arsia-protocol/issues`, e o repositório `arsia-gateway` citado em `results/spec-sender-verification.md`.
5. **Exatidão jurídica das citações regulatórias** (números de artigos do EU AI Act, GDPR, MiFID II/2017-565, DORA, DSA, PSD2, EU 2021/2116, eIDAS): não conferida contra os textos legais — fora do escopo desta auditoria técnica. A alegação do Assets §6.3 de que oversight humano "satisfaz SCA no nível de protocolo" é uma interpretação legal, não verificável aqui.
6. **`scripts/validate_vectors.py` e `scripts/gen_state_vec2.py`**: não auditados linha a linha (apenas o papel na CI foi constatado).
7. **Números de cobertura dos RTMs**: aceitos como declarados nos sumários (exceto Routing, recontado por script: 262 requisitos, 127 sem schema e sem vetor); não recontados linha a linha para os demais documentos.
8. **Divergência FAQ (613/70+) vs results (559)**: constatada; a causa (relatório gerado sobre versão anterior dos vetores) é inferência plausível, não confirmada por histórico git (o repo tem apenas 2 commits).

---

## 7. Registro de revisão (segunda passada)

Todos os achados BLOQUEANTE e ALTO foram reconferidos contra o texto-fonte por busca literal das citações (âncoras B-01…B-06 e A-01…A-15 confirmadas caractere a caractere). Três erros da primeira versão deste relatório foram encontrados e corrigidos nesta revisão:

1. **§3.7 (compliance-field vs message schema):** a primeira versão afirmava que a cópia inline do compliance no message schema não continha a regra high-risk→human_oversight; a regra existe no `allOf` de nível de envelope (`arsia-message.schema.json`). Corrigido para registrar apenas a duplicação sem `$ref` (risco de deriva), sem divergência substantiva atual.
2. **M-22:** a primeira versão afirmava que o MISMATCH de `data_residency` do state-entry schema (reportado em `results/audit-schemas-vectors.md`) "continuava presente"; o schema atual já delega a invariante ao runtime. Corrigido: o que permanece é a autocontradição da prosa de State §2.1.10 e a desatualização do relatório em results/.
3. **M-18 / §5.2 (cobertura das Regras do §4.3.8):** a primeira versão afirmava que as Regras 1 e 7 não tinham teste "em documento algum" sem registrar os vetores; verificação nos 613 vetores mostrou cobertura por vetores `skip_schema` para as Regras 1 (ITV-416), 3 (ITV-421), 7 (ITV-553/554) e 8 (ITV-555/INV-20). Corrigido: o gap real é a ausência de testes de conformance **nos documentos** para essas regras, a ausência de **vetor** para a Regra 4 e a ausência total de cobertura para o `oversight_timeout` de §4.3.6.5.

Duas nuances de imparcialidade foram adicionadas na mesma passada: a leitura *lex specialis* possível (mas não escrita) em B-02, e a remoção de State §6.1 da lista M-14 (a âncora "§8.3, Rule 3" é parcialmente defensável — a Regra 3 de §8.3 trata de fato de legal_basis, ainda que o anchor preciso para `pii_involved` de envelope seja Core §4.3.8 Regra 2).

## 8. Adendo — auditoria independente de 2026-07-22

O documento [auditoria-independente-spec-e-validacao-documentos-2026-07-22.md](auditoria-independente-spec-e-validacao-documentos-2026-07-22.md) foi adotado como **adendo oficial** deste baseline após avaliação técnica. Registro da avaliação:

**O que o adendo acrescenta.** 16 achados materiais novos — B-07 (wildcard: Core §6.4 exige exact match na mesma comparação em que Actions §1.2/ACTIONS-03 exigem expansão), B-08 (State §2.1.2: MUST NOT e MAY contraditórios na mesma frase sobre fidelidade lexical de números, incompatível com JCS), A-16 a A-22 (objeto `security` fora da assinatura; trust anchor do Authorization Server indefinido; revogação de chave ineficaz sob cache — o refetch dispara por falha e a chave comprometida verifica; overreach nos claims PSD2/SCA; precisão monetária incompatível com ISO 4217 minor units; absolutismos GDPR sobre hashes; tamper evidence além do que o append-only entrega), M-25 a M-31 (destaque: `Idempotency-Key` não assinado prevalecendo sobre campo assinado do envelope) e a expansão do A-14 (choque SHOULD/MUST entre Routing §5.1 e §5.2). Total consolidado: **~69 achados**.

**Resultado da avaliação do adendo (verificação executada em 2026-07-22):** 14 achados novos confirmados como procedentes e 2 procedentes com nuance (A-16: exploitabilidade imediata estreita, mas contradição real com a promessa do Core §13.2.3; M-27: o Assets §6.2.4 já disclaima a classificação DORA — o defeito remanescente é nome e gatilho do evento). M-25 é candidato a reclassificação para ALTO (bypass de deduplicação por replay com header novo dentro da janela de `expires_at`, sendo a idempotência listada como defesa anti-replay no Core §13.2.2). B-08 e a caracterização do AP2 v0.2 foram confirmados contra fonte primária; a suíte local foi executada (540 pass / 73 skip / 0 fail em 613 vetores), confirmando os números do adendo.

**Correções que o adendo produz sobre os documentos companheiros deste baseline:** a referência ao "MCP 2026-07-28" em [pesquisa-panorama-2026.md](pesquisa-panorama-2026.md) passa a NOT VERIFIED (data futura em relação à auditoria); o racional do D2 em [relatorio-consolidado-decisoes-verificadas.md](relatorio-consolidado-decisoes-verificadas.md) fica corrigido — AP2 v0.2 tem Human Present/Not Present, mandates assinados pelo usuário, PoP, selective disclosure e signed receipts; o diferencial ARSIA é compliance resolution/audit/residency e asset types não-commerce, não ausência de autorização humana no AP2 (a conclusão "manter + bindings" permanece); no D3, "mais rico" não implica "superior" em propriedades de prova; no D1, RFC 8693 é peça necessária mas não suficiente para o B-05 (exige também issuer trust/A-17, PoP e audience policy).

**Ressalvas registradas sobre o próprio adendo** (a serem corrigidas nele): (i) o total "638 MUSTs sem vetor" não é reproduzível pelo comando awk publicado no §6.3 do adendo — a execução produz 593, e o breakdown por camada do §6.1 soma 622; causa provável: o RTM do Assets usa formato de colunas reduzido que quebra a extração uniforme; os totais 2.002 linhas e 1.153 MUST/MUST_NOT foram reproduzidos com exatidão; (ii) âncoras trocadas em M-28 ("Actions §5.3" → confidence está em §5.2) e M-29 ("Actions §5.2" → sandboxing está em §4.4); (iii) os 8 achados BAIXOS deste baseline foram comprimidos em "L-01–L-08" sem listagem individual.

**Precedência de leitura:** este baseline + o adendo formam o conjunto de referência da auditoria Draft-01. Em caso de divergência de contagem, valem os números reproduzíveis registrados nesta seção. A ordem lógica de correção do §9 do adendo (trust model antes de features; resolver os 8 bloqueantes incluindo B-07/B-08) substitui, como sequenciamento inicial, a ordenação implícita das ondas do documento de propostas.

---

*Relatório gerado por auditoria somente leitura; nenhum arquivo da spec, schema, perfil ou vetor foi modificado.*
