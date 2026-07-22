# Auditoria do repositório da spec — ARSIA Protocol Draft-01

**Data:** 2026-07-22
**Escopo:** todo o repositório `arsialabs/arsia-protocol` (spec/, schemas/, profiles/, test-vectors/, docs/rtm/, documentos auxiliares). Somente leitura; SDKs e demos fora do escopo.
**Método:** leitura integral dos seis documentos da spec, dos 31 arquivos de schema, do catálogo de perfis e das RTMs; verificação mecânica de 339 referências cruzadas entre documentos e ~709 referências internas; verificação caractere a caractere de exemplos contra os patterns declarados; cruzamento de enums, defaults e error codes entre prosa, schemas e catálogo.
**Convenção de âncora:** `Doc §seção (Lnnn)` = arquivo em `spec/`, seção e linha. Schemas citados por arquivo + linha.

---

## 1. Sumário executivo

| Severidade | Quantidade |
|---|---|
| BLOQUEANTE | 11 |
| ALTO | 23 |
| MÉDIO | 50 |
| BAIXO | 12 |
| **Total** | **96** |

Verificações que passaram limpas: as 339 referências cruzadas `ARSIA-X §N.N` entre documentos apontam todas para seções existentes; os 7 nomes de perfis batem entre Core §4.3.6.1, State §6 e o catálogo JSON; a errata do payload.type (Core §4.4.1) está corretamente propagada para `arsia-common.schema.json`; todos os exemplos de agent-id e payload.type do Core passam nos patterns; as 3 assinaturas de exemplo do Apêndice A têm exatamente 86 caracteres.

**Os 5 achados mais importantes:**

1. **[X-01]** O piso de retenção MiFID II é **1825 dias** em Assets/Identity/Actions e **1827 dias** em Core/State/Routing/schemas/catálogo — uma implementação que passa no teste ASSETS-07 é rejeitada pela Rule 4 do Core.
2. **[RTG-01]** Na rota com broker, o token que o broker apresenta ao destinatário teria de ter `sub` = agente remetente original — impossível sob o modelo client-credentials do Core §6.2; o roteamento com broker (obrigatório quando há `data_residency`) é inimplementável como especificado.
3. **[STA-01]** Retenção abaixo do piso do perfil: State §8.3 Rule 2 manda **clampar** (`max()`), o teste STATE-13 manda **rejeitar** com `invalid_request` — duas implementações conformantes fazem coisas opostas.
4. **[CORE-02]** Não existe em nenhum documento o mecanismo de resolução agent-id → host/endpoint (discovery, JWKS, inbox); toda a cadeia de verificação depende de um mapeamento que a spec nunca define.
5. **[X-02]** Perfil de compliance com `human_oversight: required_before_execution` obriga o receptor a responder `pending_approval` (Core §4.3.6.5), mas Actions §3.7 proíbe (`MUST NOT`) enviar `pending_approval` para ação com descriptor `human_oversight_required: false` — sem regra de precedência.

---

## 2. Tabela de achados

| ID | Sev. | Doc/Seção | Descrição | Direção de correção |
|---|---|---|---|---|
| X-01 | BLOQ | Assets §6.1.2/§7; Identity §9.3; Actions §2.2 vs Core §4.3.8 R4 | Piso de retenção MiFID II é 1825 dias em três docs e 1827 em quatro docs + schemas + catálogo. | Unificar em 1827 (decisão deliberada já documentada em FAQ.md:83-85). |
| CORE-01 | BLOQ | Core §7.4 vs §4.1.1 | Algoritmo de negociação aceita `v` maior que `server_max` (condições não testam `v ≤ server_max`), contradizendo o MUST-reject de §4.1.1. | Acrescentar a condição `v ≤ server_max` (ou grace de minor version) ao passo 3 de §7.4. |
| X-02 | BLOQ | Core §4.3.6.5 vs Actions §3.7 | MUST responder pending_approval (perfil) vs MUST NOT enviar pending_approval (descriptor false), sem precedência. | Definir regra de precedência análoga à de explainability (Actions §5.1 item 2). |
| ACT-01 | BLOQ | Actions §4.1 | COMPLETED declarado "Terminal state. No further transitions" mas ROLLED_BACK exige transição a partir de COMPLETED (diagrama inclusive). | Reclassificar COMPLETED como semi-terminal ou modelar rollback como novo ciclo. |
| AST-01 | BLOQ | Assets §4.2.3 vs §4.2.1/§4.2.4 | Árbitro resolve disputa enviando release_trigger/escrow-cancel, mas as regras de validação mandam rejeitar `forbidden` qualquer remetente ≠ release_agent/from_agent; não há mecanismo de delegação. | Definir exceção explícita para o arbitration_agent nas validações de release e cancel. |
| STA-01 | BLOQ | State §8.3 R2 vs STATE-13 (e §2.1.8, §4.1.1) | Retenção abaixo do piso: Rule 2 manda computar `max()` (clamp silencioso); STATE-13 exige rejeição `invalid_request`/`insufficient_retention`. | Escolher um comportamento (Core §4.3.6.4 sugere clamp+warning) e alinhar teste, regra e Core Rule 4. |
| STA-02 | BLOQ | State §3.1.1 (L930) vs §10.2 (L3279-3281) | GET sem acesso: `forbidden` obrigatório em §3.1.1 (e STATE-07) vs "MUST return empty results (not errors)" em §10.2. | Definir a matriz acesso × resposta (capability ausente vs grant ausente) em um único lugar. |
| STA-03 | BLOQ | State §3.1.2 R1 (L982-983) vs §3.3 (L1486-1493) | SET rule 1 restringe escrita ao próprio namespace, tornando grants `read_write` (que contemplam SET de grantee) inutilizáveis. | Adicionar exceção de grant ativo à rule 1. |
| STA-04 | BLOQ | State §2.1.12 (L685-689) | "version MUST NOT be reset, even if deleted and recreated" seguido de "the new entry starts with version 1" no mesmo parágrafo. | Escolher uma semântica; se resetar, definir unicidade no armazém temporal por (key, geração, versão). |
| RTG-01 | BLOQ | Routing §2.3.2 (L985-990) vs Core §6.2 | Token do broker ao destinatário deve ter `sub` = remetente original e scope com as capabilities da mensagem — inviável sob client_credentials; sem mecanismo de delegação/token exchange. | Especificar delegação (ex.: token exchange RFC 8693 ou isenção documentada de sub==from no salto broker→destinatário). |
| SCH-01 | BLOQ | arsia-audit-query-response L348-364 vs arsia-audit-record L338-384 | Cópia embutida do AuditRecord divergiu: sem `sensitive` no enum de pii_classification, legal_basis só Art. 6, sem `pii_special_categories` — registro válido de PII sensível é irrepresentável na resposta do endpoint de auditoria (additionalProperties:false). | Substituir a cópia embutida por `$ref` ao schema canônico. |
| CORE-02 | ALTO | Core §5.2 P2, §9.1; Identity §1.1 (L148-152, 419) | Resolução agent-id → host (discovery/JWKS/inbox) nunca é definida; "same infrastructure that owns the acme domain" é o máximo dito. | Definir mecanismo de resolução (convenção DNS, registro, ou declarar explicitamente out-of-band). |
| CORE-03 | ALTO | Core §4.3.6.1, §4.3.8 R1 | "Strict mode" é invocado normativamente mas nunca definido: como se ativa, como se descobre, o que mais muda. | Definir strict mode (flag de discovery?) ou remover e ficar só com warning+default. |
| CORE-04 | ALTO | Core §4.3.6.4/§4.3.7 vs profiles/arsia-compliance-profiles.json | Prosa aplica piso pelo "profile's minimum", mas o catálogo só define `defaults` — nenhum campo `minimum` existe. | Adicionar campo de mínimo ao formato do catálogo ou declarar default==minimum normativamente. |
| CORE-05 | ALTO | Core §4.3.6.8 (L984-986 vs L1001-1025) | O "Enum:" declarado de legal_basis lista só os 6 valores Art. 6, mas a Rule 8 exige os 10 valores Art. 9(2) no mesmo campo (schema aceita 16). | Declarar o enum completo de 16 valores com a condição de uso. |
| CORE-06 | ALTO | Core §4.3.5 (nota), §5.2, §13 | Mensagens `error` e `event` não exigem assinatura; broker/intermediário pode injetar erros forjados; §13.2.6 assume assinaturas como mitigação. | Exigir assinatura de error em rotas com broker ou cobrir o vetor no threat model. |
| CORE-07 | ALTO | Core §9.2 item 5; Routing §7.2 (L1852-1871), §5.3 (L1596-1612) | Cadeia de confiança do broker: registry sem autenticação/assinatura, hospedado "por qualquer serviço", residência auto-declarada, e a auditoria de relay é auto-atestada pelo próprio broker. | Exigir verificação da IdentityRecord do broker antes do uso e assinar respostas do registry; cobrir spoofing de registry no §13. |
| SCH-02 | ALTO | arsia-message L468 vs Core §4.1.2 e arsia-common uuid-v4 | Pattern do `id` é lowercase-only; Core permite hex maiúsculo e `correlation_id` usa o $def mixed-case — mensagem conformante ao Core falha no schema. | Alinhar `id` ao $def `uuid-v4` (ou tornar lowercase obrigatório na prosa). |
| SCH-03 | ALTO | vários schemas + State §7.1 vs Assets §6.1.1 | Enums do mesmo conceito divergem: `human_oversight_status` = denied/expired (State L2739, audit-record) vs rejected/timeout (Assets L1830, mifid-audit-record); legal_basis Art. 6-only em compliance-profiles.schema L110-117. | Fonte única de enums (common schema) e $ref em todos os lugares. |
| X-03 | ALTO | State §7.1 (L2729-2778) | ArsiaAuditRecord mistura declarado e resolvido sem distinguir: `compliance_profile` e `data_residency` são o valor declarado no envelope, `retained_until` é o resolvido; residency herdada só de perfil não é registrada. | Decidir e declarar o quê o registro captura; idealmente registrar o contexto resolvido pós-§4.3.7 (ou ambos). |
| ACT-02 | ALTO | Actions §3.2 (L1224-1227) | Entrega do pending_approval ao aprovador é "implementation-defined" — o fluxo de oversight não é interoperável entre implementações. | Definir endpoint/registro de oversight ou padrão mínimo de entrega. |
| ACT-03 | ALTO | Actions §2.4 (L1015-1024) vs §2.1 (L657-661) | Major version "treated as a new action" com `action_id` inalterado viola a unicidade do `action_id` no registry; descriptor não tem campo de versão; discovery não filtra por versão. | Adicionar versão ao ActionDescriptor e à discovery, ou codificar major no action_id. |
| ACT-04 | ALTO | Actions §2.1 (L781-783) vs §3.5 (L1547) | Retenção default de 90 dias sem perfil vs piso de 180 dias para risk_level ≥ 7, sem enforcement nem erro — ação de risco 7 sem perfil fica com 90 < 180. | Vincular o piso de 180d ao risk_level normativamente (validação de registro ou de mensagem). |
| AST-02 | ALTO | Assets §3.3.2 (L1061-1072) | Janela de reversão é provider-defined, mas o **receptor** MUST rejeitar `conflict` com `window_days` — obrigação sem meio de conhecer a janela. | Publicar a janela (discovery/ActionDescriptor/recibo) ou mover a obrigação para quem a conhece. |
| AST-03 | ALTO | Assets §6.1 (L1799-1804) | Gatilhos do audit MiFID dependem de "EU-regulated entity" na IdentityRecord alheia e de classificação MiFID Annex I — receptor não tem campo de protocolo para nenhum dos dois. | Sinalizar a condição no envelope (perfil/flag) ou exigir fetch de IdentityRecord explicitamente no fluxo. |
| IDN-01 | ALTO | Identity §3.2 (L455) vs §9.1 (L1693-1695) | `aud` do token: passo 4 exige aud == message.to; onboarding manda aud = router ou wildcard — tokens de onboarding falham na verificação normativa. | Definir a exceção de audience para topologia com router/gateway. |
| IDN-02 | ALTO | Identity §4.2 (L539-541) vs §3.1 (L412-427) | MUST rejeitar toda mensagem de agente unacceptable-risk exige buscar a IdentityRecord de cada remetente, mas o procedimento de verificação nunca inclui esse fetch. | Integrar o fetch/cache de IdentityRecord ao procedimento ou rebaixar para SHOULD com trigger definido. |
| IDN-03 | ALTO | Identity §7.7 (L1477-1488) | Router deve enforçar `max_risk_level` contra o ActionDescriptor do agente interno (que não possui) e "sinalizar" oversight ao agente interno por mecanismo inexistente (e L1149 proíbe campos novos). | Definir como o router obtém descriptors e um campo/header padrão para o sinal de oversight. |
| IDN-04 | ALTO | Identity §6.4.3 (L873-878) vs Core §11.2; Identity L1149 | Quatro error codes novos snake_case (`certificate_*`) violam a convenção do Core (custom = reverse-domain) e a própria afirmação "does NOT define new error codes". | Registrá-los formalmente no Core §11.2 (com HTTP status) ou renomeá-los em reverse-domain. |
| RTG-02 | ALTO | Routing §5.1(4) (L1494-1498) vs §5.2(1) (L1507-1510); ausência de check no receptor | Enforcement de residência é só do lado honesto: nada obriga o receptor a rejeitar mensagem com `data_residency` chegada direta; processamento no receptor é MUST em §5.2 e SHOULD em §5.1. | Definir obrigação (ou não-obrigação explícita) do receptor e alinhar MUST/SHOULD. |
| RTG-03 | ALTO | Routing §7.3 R3 vs Core §10.4 | Broker preserva só o envelope; nada manda replicar os headers `Idempotency-Key` e `X-Request-Priority` no forward — chave de idempotência header-only some silenciosamente em rota com broker. | Regra explícita de propagação de headers pelo broker (ou proibir header-only com broker). |
| STA-05 | ALTO | State §8.3 R3 (L3030-3033) vs §7.1 | legal_basis "MUST be recorded in the audit event", mas ArsiaAuditRecord não tem campo para isso (o schema até tem; a prosa §7.1 não) e as tabelas de evento de §3 também não. | Adicionar o campo à definição prosa do §7.1 e às tabelas de evento. |
| STA-06 | ALTO | State §3 (tabelas L1021-1029 etc.) vs §7.1 (L2632-2795) | Dois formatos de registro de auditoria incompatíveis: eventos de state usam key/initiator_agent_id/purged_at etc., inexistentes no ArsiaAuditRecord ("All fields are REQUIRED", sem extensão) — o registro esperado por STATE-03 é irrepresentável em §7.1. | Definir extensão por event_type do ArsiaAuditRecord ou mapear os campos. |
| STA-11 | ALTO | State §10.4 (L3311-3313), exemplos L438/758 vs §7.2 | Chaves com PII (ex.: número de contribuinte `PT501234567` nos exemplos) entram em registros de auditoria imutáveis e não-purgáveis — conflito direto com a tese "audit records não contêm dados pessoais" (L2827-2838) e com o Art. 17. | Proibir PII em chaves (como em agent-ids) ou definir pseudonimização de key em audit records. |
| CORE-08 | MÉDIO | Core §3.2 (L513-518) | Texto do 3º exemplo diz org-segment "arsia", mas o identificador é `agent:arsialabs.demo.risk-assessor`. | Corrigir o texto. |
| CORE-09 | MÉDIO | Core §3.1 vs §3.3 R8 | ABNF permite hífen inicial/final em segmentos e `_` inicial no resource-segment; a regex e as rules proíbem. | Apertar a ABNF para casar com regex/rules. |
| CORE-10 | MÉDIO | Core §4.1.1 (L604-615) | Prosa proíbe zeros à esquerda na versão; pattern `^\d+\.\d+$` aceita `01.0`. | Pattern `^(0|[1-9]\d*)\.(0|[1-9]\d*)$` ou remover a restrição da prosa. |
| CORE-11 | MÉDIO | Core §4.3.6.1 vs §4.3.8 R1 | Unknown profile: "SHOULD trigger a compliance warning" vs "MUST log a compliance warning" para o mesmo caso não-strict. | Unificar a força normativa. |
| CORE-12 | MÉDIO | Core §11.1 (L2696-2698) vs §4.3.3 (L808-811) | Description de erro "MUST be written in English" vs locale "MAY use this field to select the language of error descriptions". | Escolher: inglês fixo + campo separado localizável, ou localização permitida. |
| CORE-13 | MÉDIO | Core §9.2 item 3 (L2449-2454) | "Byte-identical ... (after JSON canonicalization)" é auto-contraditório; interage mal com a preservação de campos desconhecidos (§7.4). | Definir: broker repassa os bytes recebidos, e a igualdade é verificada por assinatura. |
| CORE-14 | MÉDIO | Core §7.3 (L1941-1943) vs Identity §2.2 (L319); schema kid | Formato do kid: "{agent-id}#{keyN}" sequencial (Core) vs "short alphanumeric identifier" (Identity, ex. `#2026q1`); message schema não valida kid. | Uma gramática formal de key-index num só lugar (o jwk-entry schema já tem uma — promovê-la). |
| CORE-15 | MÉDIO | Core §4.3.6.9/§4.3.8 R6; Identity §4.2 (L537-541) | `unacceptable-risk` é valor válido e a Rule 6 permite mensagens nesse nível se o agente também o for; a proibição de deploy é NO-ERR do lado do deployer. | Definir semântica protocolar (ex.: mensagens unacceptable sempre rejeitadas). |
| CORE-16 | MÉDIO | Core §4.3.6.2, §4.3.8 R5; Routing §5.1 (L1475-1478) | Conjunto de identificadores supranacionais é aberto ("EU" é o único definido); Routing sugere códigos custom de 2-4 letras que colidem com o espaço ISO 3166-1. | Registrar a lista de códigos supranacionais válidos e reservar formato não-colidente para custom. |
| CORE-17 | MÉDIO | Core §8.3 vs §4.3.7 | `clock_skew_seconds` de perfil não pode exceder 300, mas a cadeia de precedência permite valor por-mensagem sem limite declarado. | Estender o teto de 300s explicitamente ao valor por-mensagem. |
| CORE-18 | MÉDIO | Core §4.3.6.7 vs catálogo (MIFID-II/DSA-VLOP) | `pii_involved` tem "Default: false" fixo na prosa, mas MIFID-II e DSA-VLOP definem default true — a prosa não diz "per profile" como nos outros campos. | Marcar o default como "per profile; false na ausência". |
| CORE-19 | MÉDIO | Core §4.4/§4.4.7 vs Actions §5.2 e message schema | `payload.explanation` existe no schema (additionalProperties:false) e em Actions, mas está fora da estrutura §4.4 e da tabela de exclusividade §4.4.7. | Adicionar explanation à definição do payload no Core. |
| ACT-05 | MÉDIO | Actions §3.6 (L1602-1605) vs §3.5/ACTIONS-10 | Fórmula multi-approval "3 + N + 1" dá um registro a mais que o fluxo real (N+3); "minimum of four" vs "Exactly 4". | Corrigir a aritmética e unificar minimum/exactly. |
| ACT-06 | MÉDIO | Actions §3.4 (L1334-1338) | Direção da tolerância de skew no deadline não definida, e a frase seguinte anula a tolerância no sentido permissivo. | Definir: deadline + skew ou deadline − skew. |
| ACT-07 | MÉDIO | Actions §3.2 (L1131, 1165-1166) vs Core §4.2.2 | `expires_at` do envelope sobrecarregado como approval_deadline (até 24h) — interação com a regra de rejeição de mensagem expirada não endereçada. | Separar deadline de aprovação da expiração de mensagem. |
| ACT-08 | MÉDIO | Actions §4.2 (L1827-1836) | Sufixo `/rollback` não é reservado (colisão possível) e o rollback é autorizado pelas `required_capabilities` originais — qualquer portador desfaz ação de terceiro; identidade do solicitante não é restringida. | Reservar o sufixo e restringir rollback ao emissor original (ou capability dedicada). |
| ACT-09 | MÉDIO | Actions §4.3 (L1904-1962) | Padrão assíncrono usa status_url/result_url fora do envelope, sem auth, sem auditoria, sem correlação definidas; `"accepted"` fora do enum de status. | Especificar auth e semântica de auditoria/correlação do canal de polling. |
| AST-04 | MÉDIO | Assets §3.2.1 (L798-821), §4.2 (L1265-1283, 1383) | `status` de recibo descrito como "terminal" com 2 valores não-terminais; escrow: "three terminal states" mas DISPUTED não é terminal e a transição CANCELLED (4ª) está fora do diagrama. | Corrigir taxonomia de estados e diagrama. |
| AST-05 | MÉDIO | Assets §3.2.1 (L827-829) vs §3.3.2 (L1105-1107) | payment_reference de recibo "MUST match byte-for-byte" o request vs recibo de reversão com referência nova "-REV-" — mesmo payload type, semânticas opostas. | Condicionar a regra de eco ao tipo de operação. |
| AST-06 | MÉDIO | Assets §3.1.1 (L648-656) | `idempotency_key` duplicado em payload.args e envelope, sem regra para divergência. | Declarar um dos dois autoritativo (como Core §10.4 faz com o header). |
| AST-07 | MÉDIO | Assets L803-805, 1308-1309, 1328-1330, 1368 vs L781 e §6.1.2 | Recibos subsequentes (pending→completed, release, timeout, dispute) sem id/correlation/intent definidos; "replacing the original" contradiz imutabilidade do audit. | Definir a série de recibos como eventos correlacionados, nunca substituição. |
| AST-08 | MÉDIO | Assets L959, 980, 1119, 2081 | Quatro UUIDs de exemplo com nibble de variante inválido (c/d/e/f) — exemplos normativos falham o pattern uuid-v4. | Regenerar os exemplos. |
| AST-09 | MÉDIO | Assets §3.2.1 (L901-905) vs §2.5 (L479-481) | `audit_id` REQUIRED em todo recibo, mas auditoria é SHOULD para não-currency — recibo de token referencia registro que pode não existir. | Tornar audit_id condicional ou a auditoria MUST para todos. |
| AST-10 | MÉDIO | Assets §3.1.1 (L526-538) | Limites de casas decimais impostos sobre JSON number (ex. `1500.00`), que não preserva casas após parse. | Usar string decimal ou minor units inteiros. |
| AST-11 | MÉDIO | Assets §4.2.3 (L1352-1366) | Dispute não exige capability e suspende timeout indefinidamente — qualquer parte congela fundos se o árbitro não agir; sem deadline de disputa. | Deadline de resolução + retorno automático. |
| AST-12 | MÉDIO | Assets §4.2.4 (L1411-1412), §3.2.1 | `cancellation_reason` deve ser auditado mas não existe na mensagem de cancel; campo `metadata` de recibo usado (L852, 1368) mas nunca definido em §3.2.1. | Adicionar os campos às definições de mensagem. |
| AST-13 | MÉDIO | Assets §4.2.2 (L1331-1332) vs §3.3.1 (L1015-1016) | Timeout de escrow dispara "AssetTransferReversal interno" sobre transferência não-completed, que a própria regra de reversão proíbe; bypass de capability explícito. | Modelar retorno de escrow como operação própria, não como reversal. |
| IDN-05 | MÉDIO | Identity L1096/1179 vs L1512 | Discovery citada como `/.well-known/arsia` e como `/.well-known/arsia/agent.json`, ambos atribuídos a Core §7.1. | Corrigir para o path do Core. |
| IDN-06 | MÉDIO | Identity §2.4 (L364-375) vs §2.5 (L392-393) | Rotação "MUST follow this procedure" (com overlap ≥24h) sem cláusula de exceção, mas revogação manda rotacionar sem overlap. | Adicionar exceção de comprometimento ao procedimento. |
| IDN-07 | MÉDIO | Identity §7.6 (L1433-1434) vs §8.3 (L1676-1678) | Arrays effective/freely_allowed/oversight_required "MUST be present and non-empty" proíbe aprovações legítimas com uma das listas vazia, que o algoritmo §8.3 permite. | Exigir non-empty só da união. |
| IDN-08 | MÉDIO | Identity §6.2-§6.4 (L711-724, 749-756, 834-844, 880-881) | Verificação de certificados incompleta: L2 sem revocation check; L3 concedido por QcStatements sem checar Trusted List; keyCertSign/BasicConstraints sem passo de verificação; `details.reason` só definido para certificate_invalid. | Completar o procedimento §6.4.1 e a tabela de reasons. |
| IDN-09 | MÉDIO | Identity §1.2 (L204-209) | Taxonomia de 4 níveis atribuída ao "Annex III" (que só define casos high-risk); ordenação do enum usada pela regra "MUST NEVER be higher" nunca é definida formalmente. | Citar a base correta (Art. 5/6/50 + Annex III) e declarar a ordem. |
| IDN-10 | MÉDIO | Identity §7.6 (L1388) e §7.2 vs §7.5 (L1350-1368) | correlation_id da decisão aponta para "initial onboarding request" que nenhuma fase define; "If any of Phases 1 through 4 fails" contradiz Phase 4 "not a pass/fail gate"; denial_reason `no_permitted_capabilities` fora da lista padrão. | Definir a mensagem de iniciação e sanear a lista de fases/reasons. |
| RTG-04 | MÉDIO | Routing §2.3.3 (L1021) vs §1.2.2 (L261-262) | `recipient_status_url` leva o remetente a fazer polling direto no destinatário em troca com residency — bypass do broker não endereçado. | Exigir status via broker quando residency ativa. |
| RTG-05 | MÉDIO | Routing §1.4 (L495-496, 504 vs 525-529) | Critérios de seleção de broker têm dois MUSTs ("unhealthy MUST be excluded", desempate aleatório MUST) e depois "criteria ... are RECOMMENDED, not REQUIRED". | Resolver a força normativa item a item. |
| RTG-06 | MÉDIO | Routing §7.3 R7 (L1957-1964) vs §7.4 (L1986-1998) | Lista de campos do audit de relay diverge da tabela (campo `zone` vs `residency_zone`; R7 omite audit_type/latency/forwarding_result); rejeições pré-forward não têm valor de `forwarding_result`. | Unificar as listas e adicionar valor "rejected". |
| RTG-07 | MÉDIO | Routing §4.1/§4.2 (L1313-1315, 1425-1430) | BROKER_RELAYED→DISPATCH_FAILED contradiz a definição de DISPATCH_FAILED; falta transição BROKER_RELAYED→DELIVERY_FAILED; máquina única mistura perspectivas de observadores distintos. | Separar máquinas por papel (sender/broker) ou corrigir transições. |
| RTG-08 | MÉDIO | Routing L1670/1691 vs L1710; §8 ROUTING-07 (L2118) vs §6.1 | Exemplo 429: epoch 2024 vs reset_at 2026 para o mesmo instante; ROUTING-07 espera "10 (or up to burst_size)" quando burst é definido como acima da taxa sustentada. | Corrigir exemplo e expectativa do teste. |
| RTG-09 | MÉDIO | Routing §2.1.3 (L646-649) | Log de warning TLS 1.2 "MUST include the sender's agent-id" — indisponível no momento do handshake TLS. | Amarrar o log ao processamento do envelope, não à negociação. |
| RTG-10 | MÉDIO | Routing §3.2 (L1160-1162) | "Maximum retries: 3 (RECOMMENDED). After 3 failed retries, the sender MUST abandon" — MUST condicionado a parâmetro RECOMMENDED. | Definir se 3 é teto normativo ou default. |
| STA-07 | MÉDIO | State §2.2 (L765-778) | Reserva cobre prefixo `arsiaprotocol.`, mas dois dos três padrões reservados listados usam `arsia.meta/` — fora da regra de rejeição. | Alinhar os padrões ao prefixo reservado. |
| STA-08 | MÉDIO | State §2.1.9 (L597-600), §4.2.1 (L1748-1750) | Residency herdada do envelope que "criou **ou modificou por último**" — update muda a obrigação de armazenamento sem regra de migração/conflito (contraste: scope é imutável com erro definido). | Tornar residency imutável ou definir a migração. |
| STA-09 | MÉDIO | State §2.1.2 (L466-470) | "1.0 MUST NOT be returned as 1 ... however MAY normalize numbers per standard JSON parsing rules" — o MAY permite o que o MUST NOT proíbe. | Escolher fidelidade (exigindo preservação textual) ou normalização. |
| STA-10 | MÉDIO | State §7.1 (L2733-2734), §6.1 (L2182-2184) | Sentinela `"none"` colide com nome de perfil possível; caso "compliance presente sem profile" (que resolve para GDPR-STANDARD) não tem representação definida no audit. | Registrar o perfil resolvido e reservar o nome "none". |
| STA-12 | MÉDIO | State §1.1 (L179-189) vs §6.1 (L2218-2222) e §8.3 R3 | Session entries "MUST NOT generate audit events" e são isentas de compliance, mas o override de audit p/ PII e a rejeição por legal_basis se aplicam a SETs de sessão com dados pessoais — sem resolução. | Definir precedência sessão × PII. |
| STA-13 | MÉDIO | State §2.1.8 (L580-582), §2.4 (L848-850) | Retenção ancorada só em created_at: versões escritas tardiamente ficam deletáveis antes de completar o período regulatório próprio. | Ancorar retenção por versão ou no updated_at da última versão. |
| STA-14 | MÉDIO | State §3.3.1 (L1416), §10 | GRANT exige apenas `arsiaprotocol.state.write` — qualquer token com escrita pode conceder leitura de todo o namespace a terceiros (exfiltração); §10 não discute. | Capability dedicada de grant ou cobertura no threat model. |
| STA-15 | MÉDIO | State §10.4 (L3296-3299), §5.6 | Texto normativo truncado: "All obligations of personal apply, plus:" solto e "(per §2.1.10)" apontando para seção que não define authenticated encryption. | Restaurar o texto completo (padrão de truncamento já visto na auditoria 1.4b). |
| GER-01 | MÉDIO | Core §4.4.1/Actions §1.1/message schema L903 | Três gramáticas "reverse-domain" distintas (payload.type 1+ segmento com `/`; capability 2+ segmentos sem hífen; error code custom lowercase com hífen) — fácil de confundir, sem tabela comparativa completa. | Nota comparativa única + racional de cada restrição. |
| SCH-04 | MÉDIO | schemas/ diversos | Coleção de inconsistências de schema: `$id` relativo só no common; refs absolutas só em state-operations; maxLength 128 de capability aplicado em 5 lugares e ausente em 4; `$defs` nunca usados (reversal-payment-reference); `hash` de snapshot sem formato sha256-hex; timestamp de broker-entry com gramática própria; `grant_id` uuid any-version; ActionDescriptor duplicado sem o guard de namespace. | Normalizar por $ref ao common schema e deduplicar cópias embutidas. |
| BXO-01 | BAIXO | vários | Referências cruzadas sem prefixo de documento (Assets L1861, Routing L2127/2134, Actions L998) e mis-citações (Identity: Core §9.2 rotulado "Brokered Routing" vs "data residency", State §7.1 vs §7.2, Core §8 vs §8.3); listas de referências omitem seções citadas no corpo (Actions §7.1; State §12 sem Routing/Assets). | Passada editorial de referências. |
| BXO-02 | BAIXO | Core B.3 (L3597-3598) vs catálogo | CAP/PAC descrito como "(planned)" no Core, mas PAC-AGRICULTURE está ativo no catálogo. | Atualizar o texto. |
| BXO-03 | BAIXO | profiles/README.md L15 | "current specification (Draft-02)" — todo o resto do repo é Draft-01. | Corrigir. |
| BXO-04 | BAIXO | Identity §12 (L1895) | Seção 12 (BYOA) vem depois de §11 References. | Reordenar. |
| BXO-05 | BAIXO | Assets L2659 | Texto corrompido: "2## 006/42/EC" numa citação de diretiva. | Corrigir. |
| BXO-06 | BAIXO | Identity §6.7.1 (L996) | Referência a `packages/sandbox/local-ca/` — caminho inexistente neste repositório. | Apontar para o repo correto ou remover. |
| BXO-07 | BAIXO | Core §12.3 (L2927); catálogo L3 | Referências externas: pacote npm `@arsia-protocol/conformance-test` e `$schema` apontando a URL remota em vez do arquivo local. | Registrar como dependências externas explícitas. |
| BXO-08 | BAIXO | Core B.3 | Tom promocional (€16 trillion, value proposition) em documento normativo. | Mover para material de posicionamento fora da spec. |
| BXO-09 | BAIXO | Actions §1.4 (L161-176 vs 213); §2.3 (L937) | Prosa chama o namespace reservado de "arsia" mas o prefixo é `arsiaprotocol.`; well-known usa `/arsia/`. | Uniformizar a nomenclatura. |
| BXO-10 | BAIXO | Identity §7.3 (L1272) | SHOULD dentro de teste pass/fail (CHECK-03) sem dizer se desvio reprova. | Converter em MUST ou marcar informativo. |
| BXO-11 | BAIXO | Assets (nenhuma ref a schemas); State L168-169/342-344 | Assets não referencia os 5 schemas arsia-asset-*/dora/mifid existentes no repo; proibições fraseadas com "No agent MAY ..." (uso incorreto de MAY do RFC 2119). | Referenciar schemas; reescrever com MUST NOT. |
| BXO-12 | BAIXO | test-vectors/README L73 vs meta-schema; RTM | README documenta campo `req_ids` que o meta-schema proíbe e nenhum vetor usa; 318/613 vetores sem `category`; RTMs com 49 linhas com colunas deslocadas e a RTM de Routing sem seção de gaps. | Sanear meta-schema/README e reprocessar RTMs. |

---

## 3. Achados por documento (detalhe dos BLOQUEANTE e ALTO)

### 3.1 ARSIA-Core.md

**CORE-01 (BLOQUEANTE) — Negociação de versão aceita major não suportado.**
§7.4 passo 3 (L2051-2057): sucesso sse `server_min ≤ v` E `min_v ≤ server_max` (com min_v ausente trivialmente satisfeito). Para um servidor 1.0–1.0 e mensagem `v: "2.0"` sem `min_v`, ambas as condições valem e a negociação "sucede" — mas §4.1.1 (L611-613) exige: "Implementations MUST reject messages whose major version exceeds the maximum major version they support". Dois implementadores lendo seções diferentes divergem em comportamento observável no fio.

**CORE-02 (ALTO) — Resolução de identidade para endpoint inexistente.**
§5.2 Step 2 (L1399-1405) manda resolver a chave "by fetching the sender's JWKS endpoint — identified by the agent identifier in the `from` field"; §9.1 (L2406-2408) manda resolver o inbox "from the discovery endpoint". Nenhum documento define como se vai de `agent:acme.billing` a um host. Identity chega a dizer "the JWKS endpoint hosted by the same infrastructure that owns the `acme` domain" (L148-152) — o org-segment não é um FQDN. Sem isso, discovery, verificação de assinatura e roteamento dependem de convenção não escrita.

**CORE-03 (ALTO) — Strict mode indefinido.** §4.3.6.1 (L897-900) e §4.3.8 Rule 1 (L1097-1100) definem comportamento distinto em "strict mode (implementation-configurable)", sem definição de ativação, anúncio ou descoberta. O remetente não tem como prever se um perfil desconhecido causa warning ou rejeição.

**CORE-04 (ALTO) — "Profile minimum" sem existência no catálogo.** §4.3.6.4 (L925-931): "Per-message values ... MUST NOT be less than the profile's minimum"; §4.3.7 (L1082-1084) idem. O catálogo (`profiles/arsia-compliance-profiles.json`) só define `defaults.retention_days`; nenhum `minimum` existe em nenhum perfil. Só o MIFID-II tem piso explícito (hardcoded na Rule 4). Para EU-AI-ACT-HIGH-RISK (default 180), não é decidível se retention_days=30 é válido, clampado ou rejeitado.

**CORE-05 (ALTO) — Enum declarado de legal_basis não contém os valores exigidos pela Rule 8.** §4.3.6.8 declara "Enum:" com 6 valores Art. 6(1) (L984-986); a prosa seguinte (L1001-1025) e a Rule 8 (L1145-1155) exigem 10 valores Art. 9(2) no mesmo campo. O schema (`arsia-compliance-field.schema.json` L62-79) aceita os 16 — a prosa é auto-inconsistente.

**CORE-06 (ALTO) — Mensagens error/event sem assinatura obrigatória.** §5.2 (L1383-1388) só exige verificação para request/response/pending_approval/approval_decision; a nota de §4.3.5 (L867-873) confirma. Em rota com broker, um broker comprometido pode injetar mensagens `error` forjadas não-assinadas; §13.2.6 (L3095-3114) mitiga "inject forged messages" via assinaturas — que aqui não são exigidas.

**CORE-07 (ALTO) — Cadeia de confiança do broker é declarativa de ponta a ponta.** O registry de brokers "MAY be hosted by any ARSIA infrastructure service" (L2461-2470) sem definição de como o remetente o encontra nem autenticação da resposta; `residency_zones`/`jurisdiction` são auto-declarados (Routing L1596-1599 admite: "The sender trusts the broker's IdentityRecord declaration"); o registro de auditoria do relay é produzido pelo próprio broker (Routing L1275-1276). A garantia central do protocolo (residência verificável) repousa em três elos não verificáveis. O threat model §13.1(6) cobre broker comprometido, mas não registry spoofing nem falsa declaração de residência.

Demais achados do Core: ver tabela (CORE-08 … CORE-19).

### 3.2 ARSIA-Actions.md

**ACT-01 (BLOQUEANTE) — Máquina de estados contraditória.** §4.1: "COMPLETED ... Terminal state. No further transitions." (L1754-1755) vs ROLLED_BACK: "A previously COMPLETED action has been successfully reversed" (L1770-1772) e o diagrama (L1797-1802) desenha COMPLETED → ROLLED_BACK.

**X-02 (BLOQUEANTE) — Conflito de oversight entre Core e Actions.** Core §4.3.6.5 (L946-949): com `required_before_execution` efetivo, "The receiving agent MUST respond with a pending_approval message". Actions §3.7 (L1641-1646): "An agent MUST NOT send a pending_approval message for an action whose ActionDescriptor has human_oversight_required: false". Uma mensagem MIFID-II (default do perfil: required_before_execution) para uma ação com descriptor false ativa as duas obrigações. Actions §5.1 item 2 (L2056-2059) define o override do perfil **só** para explainability — a ausência do análogo para oversight torna o conflito irresoluto.

**ACT-02 (ALTO)** — Entrega ao aprovador "implementation-defined" (L1224-1227): o envelope do pending_approval tem `to` = solicitante original (L1128); como o detentor de `arsiaprotocol.oversight.approve` fica sabendo é extra-protocolo — o fluxo central de compliance (EU AI Act Art. 14) não é interoperável.

**ACT-03 (ALTO)** — §2.4: major bump "MUST be treated as a new action" com "action_id also remains unchanged" (L1015-1024), mas §2.1 define action_id como único no registry (L657-661); o descriptor não tem campo de versão e a discovery (§2.3) não filtra por versão — coexistência de versões é irrepresentável.

**ACT-04 (ALTO)** — Retenção default 90 dias sem perfil (L781-783) vs piso de 180 dias para risk ≥ 7 (L1547), sem regra de enforcement nem erro; o piso só aparece na discussão de satisfação regulatória (Art. 26(6)).

Também relevantes: contagem multi-approval off-by-one (ACT-05), sobrecarga de expires_at (ACT-07), rollback autorizado pelas capabilities originais (ACT-08), canal assíncrono fora do envelope sem auth/audit (ACT-09). Dos ~126 MUSTs do documento, ~100 não têm comportamento de erro definido (sem error code para a violação); os definidos concentram-se em forbidden/not_implemented/conflict/service_unavailable.

### 3.3 ARSIA-Assets.md

**X-01 (BLOQUEANTE) — 1825 vs 1827 dias.** Assets §6.1.2: "Retention period: 1825 days (5 years) MINIMUM" (L1843), "beyond 1825 days" (L1858), teste ASSETS-07: "retention_days is ≥ 1825" (L2480), exemplos com 1825 (L705, 935, 1138). Contra: Core §4.3.8 Rule 4 "MUST be at least 1827" (L1115-1121), State §6.3 (L2305-2319, com justificativa de anos bissextos), Routing (L2026), catálogo (L91) e `arsia-compliance-field.schema.json` (L142, 199) — todos 1827. Identity L1730 ("1825 days ... per ARSIA-State.md §6.3") e Actions L825/L2400 também dizem 1825, citando o State que diz 1827. FAQ.md:83-85 documenta 1827 como decisão deliberada. Uma implementação que aceita retention_days 1825-1826 passa em ASSETS-07 e viola a Rule 4.

**AST-01 (BLOQUEANTE) — Arbitragem inoperante.** §4.2.3 (L1373-1377): o árbitro resolve enviando release_trigger "acting as a delegate of the release_agent" ou escrow-cancel; mas §4.2.1 (L1295, L1218-1219) exige `from` == release_agent (senão `forbidden`) e §4.2.4 (L1415-1418) restringe cancel ao from_agent. Nenhum mecanismo de delegação existe — toda resolução arbitral é rejeitada pelas próprias regras de validação.

**AST-02 (ALTO)** — Janela de reversão é do provedor (T+1/T+30 RECOMMENDED, L1061-1068), mas o **receptor** deve rejeitar `conflict` incluindo `window_days` (L1070-1090) — obrigação sobre quem não tem a informação.

**AST-03 (ALTO)** — Gatilhos do registro MiFID (L1799-1804) dependem de status regulatório do contraparte (na IdentityRecord alheia) e de classificação jurídica (MiFID II Annex I) — nada disso trafega no protocolo.

Também relevantes: estados "terminais" que não são (AST-04), semântica dupla de payment_reference (AST-05), reversal interna de escrow que viola a própria precondição de reversal (AST-13), 4 UUIDs de exemplo inválidos (AST-08). O documento não referencia nenhum dos 5 schemas JSON de Assets existentes no repo (BXO-11).

### 3.4 ARSIA-Identity.md

**IDN-01 (ALTO)** — §3.2 passo 4 (L455): `aud` MUST == message.to; §9.1 (L1693-1695): aud dos tokens de onboarding "SHOULD be set to the infrastructure router's agent-id or a wildcard audience". Agente interno que aplica §3.2 rejeita todo tráfego onboarded.

**IDN-02 (ALTO)** — §4.2 (L539-541): rejeitar TODAS as mensagens de agente unacceptable-risk pressupõe fetch da IdentityRecord do remetente, ausente do procedimento normativo de verificação (§3.1, L412-427).

**IDN-03 (ALTO)** — §7.7: o router deve comparar `max_risk_level` com o `risk_level` do ActionDescriptor do agente interno (L1477-1482) — que ele não hospeda — e "sinalizar" oversight ao agente interno (L1485-1488) por mecanismo indefinido, enquanto L1149 afirma que o onboarding não define campos novos.

**IDN-04 (ALTO)** — §6.4.3 (L873-878) cria 4 error codes snake_case (`certificate_invalid`, `certificate_expired`, `key_mismatch`, `certificate_revoked`). Core §11.2 (L2718-2727) reserva snake_case para o registro padrão e exige reverse-domain para códigos adicionais; L1149 do próprio Identity afirma "does NOT define ... new error codes". O message schema já os incorporou ao enum (L884-899), consolidando a violação.

Também relevantes: paths de discovery contraditórios (IDN-05), rotação vs revogação sem cláusula de exceção (IDN-06), lacunas na verificação de certificados (IDN-08), provenance check quebrado por refresh de IdentityRecord (F27 do extrator — o `created_at` renovado torna `earliest_audit_record < identity_created_at` e reprova agentes legítimos; L1361-1364 vs L225). Privacidade: a IdentityRecord pública expõe `owner_name`/`contact_email` — para operador sole-proprietor (Unipessoal) o nome legal É um dado pessoal; nenhum tratamento é dado. A regra "contact_email MUST be role-based" (L228-231) não tem enforcement.

### 3.5 ARSIA-Routing.md

**RTG-01 (BLOQUEANTE) — Autenticação do salto broker→destinatário inimplementável.** §2.3.2 (L985-990): o token que acompanha o forward deve ter `aud` = destinatário, "`sub` claim MUST equal the **sender's** agent-id" e scope cobrindo as capabilities da mensagem; mas quem obtém o token é o broker (L986-987 "Obtains an access token for the recipient from an authorization server"). Sob Core §6.2 (client_credentials, client_id = o próprio agente), um AS não emite token com `sub` de terceiro para o broker — não há token exchange/delegação definidos. Ou o broker impersona o remetente no AS (não especificado e indesejável), ou o destinatário viola a checagem sub==from do Core §6.4. Como o roteamento com broker é obrigatório sempre que `data_residency` está presente (Rule 5), o caminho de compliance central não fecha.

**RTG-02 (ALTO)** — Enforcement de residência é inteiramente sender/broker-side; nenhuma regra manda o receptor rejeitar mensagem com `data_residency` recebida diretamente. Processamento do receptor em zona: MUST em §5.2(1) (L1507-1510), SHOULD em §5.1(4) (L1494-1498) — mesma obrigação, forças diferentes. Adicional: "audit logs at the sender ... MUST be stored within the declared zone" (L1491-1493) é impossível para remetente extra-EU, cenário que o próprio doc contempla (L1527-1533).

**RTG-03 (ALTO)** — Rule 3 preserva só o envelope; `Idempotency-Key` (que tem precedência sobre o campo do envelope, Core §10.4) e `X-Request-Priority` não têm regra de propagação no forward (§2.3.2 silencioso) — dedup e prioridade mudam de comportamento conforme a rota.

Também relevantes: cláusula OR morta em §1.2.1 (L246-254 vs L466-469), polling de status que fura o broker (RTG-04), duas listas divergentes de campos do audit de relay (RTG-06), máquina de estados com transições impossíveis (RTG-07). Core §13 nunca é citado pelo Routing; broker como acumulador de tokens, spoofing de registry e DoS em brokers ficam fora de qualquer threat model.

### 3.6 ARSIA-State.md

**STA-01 (BLOQUEANTE)** — §8.3 Rule 2 (L3024-3028): retenção efetiva = `max(payload.args.retention_days, compliance.retention_days)` — clamp silencioso, coerente com §2.1.8 (L574-576) e Core §4.3.6.4. STATE-13 (L3202-3210), citando a mesma Rule 2, exige rejeição com `invalid_request` + `insufficient_retention`. O discriminador `insufficient_retention` nem aparece na lista de details de §8.4 (L3050).

**STA-02 (BLOQUEANTE)** — §3.1.1 (L930): acesso negado em GET → "MUST return an error with code forbidden" (STATE-07 espera isso); §10.2 (L3279-3281): "QUERY and GET operations MUST return empty results (not errors) when the agent lacks access ... unless the access failure is due to a missing capability". Para o caso "capability presente, sem grant", as duas regras exigem respostas diferentes.

**STA-03 (BLOQUEANTE)** — SET rule 1 (L982-983): "An agent can only write to its own namespace"; §3.3 (L1486-1493) define enforcement de grant para "GET, SET, QUERY" de grantee com `access_level: "read_write"`. Sob a rule 1, todo SET de grantee é rejeitado — o nível read_write não tem uso possível.

**STA-04 (BLOQUEANTE)** — §2.1.12 (L685-689): versão "MUST NOT be reset, even if the entry is deleted and recreated" e, na frase seguinte, "the new entry starts with version 1" (§2.4 L824-826 repete o reset).

**STA-05/STA-06 (ALTO)** — §8.3 Rule 3 exige legal_basis registrado "in the audit event", mas a definição prosa do ArsiaAuditRecord (§7.1, "All fields are REQUIRED unless marked OPTIONAL") não tem esse campo (o schema JSON tem — schema e prosa divergem); e as tabelas de evento de §3 (key, initiator_agent_id, purged_at, grant_id...) descrevem registros irrepresentáveis no §7.1 — o próprio STATE-03 espera campos que o formato canônico não possui.

**STA-11 (ALTO)** — Os exemplos normativos embutem número de contribuinte na key (`client-profile/PT501234567`, L438/758); keys entram em audit records imutáveis e não-purgáveis; §10.4 (L3311-3313) admite "keys that include client tax numbers". Isso contradiz a tese de §7.3 (L2827-2838) de que registros de auditoria não contêm dados pessoais e deixa o conflito Art. 17 sem saída definida.

**X-03 (ALTO) — Pergunta da auditoria: o ArsiaAuditRecord captura o compliance resolvido ou o declarado?** A spec não distingue, e o resultado é misto: `compliance_profile` = valor declarado no envelope ("from the message's compliance.profile field", L2729-2734), `data_residency` = declarado ("MUST match the originating message's ... value", L2772-2778), `retained_until` = **resolvido** ("processed_at + effective retention_days", L2764-2770). Consequências não endereçadas: mensagem com compliance sem `profile` (que resolve para GDPR-STANDARD) não tem representação definida; residency vinda só de default de perfil (ex. MIFID-II → "EU") não fica registrada; `audit_required`/`explainability_required`/`pii_involved` efetivos não são persistidos. Um auditor não consegue reconstruir o contexto efetivo a partir do registro. **Gap confirmado.**

Também relevantes: prefixo reservado vs `arsia.meta/` (STA-07), re-herança de residency em update (STA-08), retenção ancorada em created_at (STA-13), GRANT como vetor de exfiltração com capability ordinária (STA-14), truncamento em §10.4 (STA-15, padrão da auditoria 1.4b).

### 3.7 Schemas, catálogo e artefatos

**SCH-01 (BLOQUEANTE)** — `arsia-audit-query-response.schema.json` embute uma cópia do AuditRecord que divergiu do canônico: enum de `pii_classification` sem `sensitive` (L348-352 vs canônico L338-344), `legal_basis` só com 6 valores Art. 6 (L357-364 vs 16), sem `pii_special_categories`, condicional de legal_basis só para `personal`. Com `additionalProperties: false`, um registro de state_set sensível válido pelo `arsia-audit-record.schema.json` **não pode ser servido** pelo endpoint de query — exatamente os registros de maior valor regulatório.

**SCH-02 (ALTO)** — `arsia-message.schema.json` L468: `id` com pattern lowercase-only, contra Core §4.1.2 (maiúsculo permitido, lowercase apenas SHOULD) e contra `correlation_id`, que usa o $def mixed-case do common schema. O mesmo UUID em caixa alta é aceito como correlation_id e rejeitado como id.

**SCH-03 (ALTO)** — Enums duplicados divergentes: `human_oversight_status` denied/expired (State L2739, arsia-audit-record L117-123) vs rejected/timeout (Assets L1830, arsia-mifid-audit-record L171-177); `defaults.legal_basis` do compliance-profiles.schema restrito a Art. 6 (L110-117) — um perfil não pode declarar default Art. 9; requiredness de approver_id presente no audit-record e ausente no mifid-audit-record.

**SCH-04 (MÉDIO)** — ver tabela. Adicional digno de nota: os schemas não impõem os pisos de retenção dos perfis EU-AI-ACT-* (só MIFID-II/PAC/DSA/DORA têm condicionais), e `payload.version` existe no schema sem descrição, default ou uso em condicional algum.

**Catálogo/perfis** — consistente com Core §4.3.6.1 e State §6 nos 7 nomes e defaults verificados (inclusive clock_skew_seconds 120/60/60). Gaps: sem campo `minimum` (CORE-04); `retention_days: null` do GDPR-STANDARD sem semântica formal no schema (a FAQ explica; a spec não); DORA cita clock_skew "matches the MIFID-II profile's value" enquanto a tabela MIFID-II do State §6.3 não lista o campo (State L2549 vs L2301-2310).

**Test vectors** — 613 vetores (514 válidos/99 inválidos), assinaturas reais; 73 vetores runtime-only fora de validação de schema (temporais, token, X.509, cross-message). Nunca referenciados via schema_ref: `arsia-breach-notification`, `arsia-compliance-profiles`, `arsia-explanation`. 318/613 sem campo `category`. README documenta campo `req_ids` que o meta-schema proíbe (additionalProperties:false) e nenhum vetor contém — o link RTM→vetor é unidirecional.

---

## 4. Veredito das hipóteses

**H1 — Não existe mecanismo de extensão de perfis de compliance: CONFIRMADA (com uma nuance).**
Core §4.3.8 Rule 1 (L1093-1095): perfil deve ser "known profile name as defined in ARSIA-State.md §6 **or in a future extension of this specification**" — extensão só por revisão da spec. Nome desconhecido → warning + GDPR-STANDARD, ou rejeição em strict mode (§4.3.6.1). VERSIONING.md confirma: novos perfis são "extensions ... published as separate documents"; FAQ:89: mudanças breaking = "create a new profile with a distinct name". Não há namespace reverse-domain, prefixo de vendor ou registro de terceiros — contraste direto com payload types (Core §4.4.1) e até com error codes custom (Core §11.2). Nuance: o **formato** do catálogo é aberto (`additionalProperties` no compliance-profiles.schema L26-31 aceita qualquer chave de perfil, e o campo compliance aceita propriedades extras por design), ou seja, a extensibilidade existe no artefato mas não no protocolo: um perfil privado de deployment é, para qualquer contraparte, um unknown profile.

**H2 — Não existe semântica de versionamento para payload types que evoluíram: CONFIRMADA NA SUBSTÂNCIA (letra parcialmente refutada).**
Existe um campo: Core §4.4.2 define `payload.version` com semântica mínima ("When absent, the version is assumed to be the latest version known to the **receiving** agent" — o que já é perigoso: mensagem antiga sem versão é reinterpretada sob schema novo). Actions §2.4 define minor/major para ações, mas com as contradições de ACT-03, e Assets fixa tudo em "1.0" sem regra alguma de negociação (H2 do extrator de Assets). Não há descoberta de versões suportadas por payload type (a discovery expõe versão de protocolo, não de payloads), não há regra de coexistência implementável, e o schema trata `payload.version` como string sem uso. Falta o mecanismo; sobra o campo.

**H3 — Não existe referência causal tipada além do correlation_id 1:1: CONFIRMADA.**
O envelope só tem `correlation_id` (1:1 com o id da mensagem original, Core §4.2.1). Todas as demais relações causais existem, mas ad-hoc dentro de payloads, cada uma com convenção própria: `original_request_id` (Actions L1143), `original_message_id` de rollback — que aponta para o id da **resposta** (Actions L1835-1837), `original_payment_reference` e `original_audit_id` (Assets L1009-1013, L1111-1112, reversal/escrow), sufixo derivacional `-REV-` (Assets L1105-1107), `payment_reference` como chave de ciclo de vida (Assets L605-607), `grant_id` (State), `breach_id` (State §5.7), `hash_chain` (State §7.1 — predecessor linear, não causal). Nenhum campo derived-from/supersedes/in-reply-to tipado existe em schema algum (verificado na suíte inteira). O fan-in do multi-approval (N decisões → 1 pending_approval, Actions L1591-1593) e os recibos múltiplos de Assets (AST-07) já quebram o pressuposto 1:1 hoje.

**H4 — A temporalidade do State é eixo único: CONFIRMADA.**
SNAPSHOT recebe um único parâmetro temporal `as_of` (State L1216) e retorna "entries as they existed at as_of" (L1219-1226); o histórico de versões guarda um timestamp por versão (`updated_at`, L848-859) — tempo de transação/sistema apenas. Os backends sugeridos (§11.2: SQL:2011 system-versioned, event sourcing) são todos single-axis. Não existe valid time, effective time nem consulta "o que sabíamos em T1 sobre T2"; correções são indistinguíveis de updates comuns. Nenhuma menção a bitemporalidade em documento algum.

---

## 5. Matriz MUST × conformance

### 5.1 Testes in-spec vs regras do Core

O Core §12.4 define **3** testes (CORE-COMPLIANCE-01/02/03) para **8** regras de validação (§4.3.8) e nenhum para o restante do documento:

| Regra/cluster normativo do Core | Teste in-spec | Observação |
|---|---|---|
| §4.3.8 R1 (unknown profile) | — | strict mode indefinido agrava (CORE-03) |
| §4.3.8 R2 (PII → legal_basis) | CORE-COMPLIANCE-01 | coberto |
| §4.3.8 R3 (high-risk → oversight) | — | |
| §4.3.8 R4 (piso MiFID 1827) | — (STATE-13 cobre) | STATE-13 contradiz a Rule 2 do State (STA-01) |
| §4.3.8 R5 (residency → broker) | — (ROUTING-02/03 cobrem parcial) | sem teste do lado receptor (RTG-02) |
| §4.3.8 R6 (escalação de classificação) | CORE-COMPLIANCE-02 | coberto |
| §4.3.8 R7 (PII → audit override) | — | |
| §4.3.8 R8 (sensitive → Art. 9) | — (STATE-11/12 cobrem no State) | |
| §3 agent-id (validação/case) | — | |
| §4.1/§4.2 campos obrigatórios/condicionais | — (vetores INV-* cobrem parcial) | |
| §5.1/§5.2 assinatura e verificação | — (IDENTITY-02/03; vetores) | sem teste no Core |
| §4.2.2 expiração | — (ROUTING-08) | |
| §6.4 capability enforcement | — (ACTIONS-02) | |
| §7.4 negociação de versão | — | **nenhum teste em doc algum**; e o algoritmo é contraditório (CORE-01) |
| §10 idempotência | — (ROUTING-06; ASSETS-02) | precedência header vs envelope (§10.4) sem teste |
| §11.3 retry policy | — | |
| §14.1 media type v-param | — | |

Wrapping MCP/A2A (Apêndice B) tem 1 teste (CORE-COMPLIANCE-03) e nenhum vetor.

### 5.2 Cobertura agregada (fonte: docs/rtm/, verificada por contagem independente)

| Documento | Requisitos na RTM | Sem schema E sem vetor | MUST-level sem vetor |
|---|---|---|---|
| Core | 388 | 162 | 163 |
| Actions | 323 | 119 | 126 |
| Assets | (sem tabela-resumo na RTM) | 185 | 109 |
| Identity | 257 | 104 | 117 |
| Routing | 263 (sem seção de gaps na RTM) | 127 | 115 |
| State | 382 | 147 | 104 |
| **Total** | **~1.976** | **~844** | **~734** |

≈37% dos requisitos MUST/MUST NOT/REQUIRED da suíte não têm vetor de teste; os piores clusters auto-reportados: Actions §1 (capabilities, 32/70 sem cobertura), Identity §6 (certificados, 27/51), State §4 (retenção, 24/34), State §5 (direitos GDPR, 20/28). Nota metodológica: as RTMs têm defeitos próprios (49 linhas com colunas deslocadas; RTM de Routing sem seção "Coverage Gaps") — os números acima são contagens mecânicas sobre os arquivos como estão.

---

## 6. NÃO VERIFICADO

1. **Conteúdo integral de `test-vectors/arsia-test-vectors.json`** (807 KB): verificados estrutura, contagens, distribuição de ids/categorias e ausência de `req_ids` via jq; os 613 vetores não foram validados individualmente contra schemas nem as assinaturas recomputadas. Motivo: volume; a execução dos scripts de validação violaria a regra de somente-leitura apenas se gerasse artefatos — ainda assim optou-se por não executar código.
2. **Referências externas não seguidas** (por regra de execução): `https://arsiaprotocol.org/schemas/...` ($id/$schema), pacote npm `@arsia-protocol/conformance-test`, repo `arsialabs/arsia-protocol-sdk`, URLs de RFCs/regulamentos. A afirmação do README de que `pip install arsia-protocol` corresponde ao SDK não foi verificada.
3. **Exatidão jurídica das citações regulatórias** (artigos do EU AI Act, GDPR, MiFID II, DORA, DSA, CAP): a auditoria verificou consistência **interna** das citações; a conformidade material com os textos legais está fora do escopo. Exceção pontual: a atribuição da taxonomia de 4 níveis ao "Annex III" (IDN-09) foi apontada por ser inconsistência textual identificável.
4. **RTMs linha a linha**: os totais de §5.2 são contagens mecânicas; as 49 linhas com colunas deslocadas não foram corrigidas/reinterpretadas individualmente.
5. **Comportamento do CI** (`.github/workflows/validate-vectors.yml`): existência confirmada; execução não verificada.
6. **`arsia-websocket-frame.schema.json` vs Routing §2.2.2** no detalhe de `session_id` (opcional no schema; requiredness na prosa não determinada com certeza) — registrado sem veredito.

---

*Relatório gerado por auditoria automatizada somente-leitura em 2026-07-22. Nenhum arquivo da spec foi modificado; nenhum commit foi feito. A decisão sobre o que entra no Draft-02 é do dono do protocolo.*
