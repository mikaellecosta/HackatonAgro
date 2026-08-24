# Tereza Gastronomia — backend Django

Backend do sistema de gestão para o **Grupo Tereza Gastronomia**:
matriz + filiais, com controle de cardápio, fornecedores, vendas,
solicitação de insumos e relatórios de consumo/faturamento.

> Veja o desafio original em [`desafio-tereza-overview.md`](./desafio-tereza-overview.md)
> e a cobertura das user stories em [`MAPEAMENTO.md`](./MAPEAMENTO.md).

---

## Stack

- **Python 3.12** + **Django 6.0**
- **SQLite** (dev) — trocar p/ Postgres em prod
- **django-unfold** para o admin
- **Pillow** para upload de fotos de perfil
- **requests** como cliente HTTP da Evolution API
- **Evolution API** (Docker, embarcada em `evolution-api/`) para
  integração WhatsApp via Baileys

ORM puro pra agregações; sem DRF neste momento (views são CBVs
server-side). A integração WhatsApp é opcional — Django sobe e
funciona normalmente sem ela.

---

## Setup local

```bash
# 1. Clonar e entrar no projeto
git clone <repo>
cd DevathonProject

# 2. Criar virtualenv
python3.12 -m venv venv
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Rodar migrations (já cria os grupos Matriz / Gerente de Filial)
python manage.py migrate

# 5. Popular dados de demo (cria filiais, fornecedores, insumos, pratos, usuários)
python manage.py seed_demo

# 6. Subir o servidor
python manage.py runserver
```

Acesse:
- App: <http://127.0.0.1:8000/>
- Admin: <http://127.0.0.1:8000/admin/>

### Usuários criados pelo `seed_demo`

| Usuário | Senha | Papel | Filial |
|---|---|---|---|
| `admin` | `admin123` | superuser (Matriz) | — |
| `gerente_sp` | `tereza123` | Gerente de Filial | Tereza Pinheiros |
| `gerente_rj` | `tereza123` | Gerente de Filial | Tereza Copacabana |

---

## Comandos úteis

```bash
# Rodar testes
python manage.py test

# Criar nova migration
python manage.py makemigrations

# Console interativo
python manage.py shell

# Verificar problemas
python manage.py check

# Limpar e re-seed
python manage.py flush --no-input && python manage.py migrate && python manage.py seed_demo
```

---

## Fluxo de dados — partindo do banco vazio

Esta é a ordem natural de cadastros e operações para o sistema sair do
zero e começar a gerar valor (gráficos, sugestões, alertas). Cada passo
depende do anterior.

> Atalho: `python manage.py seed_demo` faz tudo isso de uma vez com
> dados de exemplo.

```
                 ┌──────────────────────────────┐
                 │  PASSO 0 — BOOTSTRAP          │
                 │  python manage.py migrate     │
                 │  → cria as tabelas + grupos   │
                 │    "Matriz" e                 │
                 │    "Gerente de Filial"        │
                 └──────────────┬───────────────┘
                                │
                 ┌──────────────▼───────────────┐
                 │  PASSO 1 — SUPERUSER          │
                 │  createsuperuser              │
                 │  → primeiro acesso ao admin   │
                 └──────────────┬───────────────┘
                                │
                                ▼
   ╔══════════════ FEITO PELA MATRIZ (admin) ══════════════╗
   ║                                                       ║
   ║   PASSO 2 — Cadastrar Filiais                         ║
   ║     ✓ Marcar 1 como is_matriz=True                    ║
   ║     ✓ Demais ficam como filial comum                  ║
   ║                                                       ║
   ║   PASSO 3 — Cadastrar Gerentes                        ║
   ║     ✓ Criar User no /admin/core/user/add/             ║
   ║     ✓ Adicionar ao grupo "Gerente de Filial"          ║
   ║     ✓ Ir em Filiais e definir o User como `gerente`   ║
   ║       (User.filial é resolvido por essa FK reversa)   ║
   ║                                                       ║
   ║   PASSO 4 — Cadastrar Insumos                         ║
   ║     ✓ Nome, unidade de medida, estoque mínimo         ║
   ║     → estoque mínimo dispara alertas de ruptura       ║
   ║                                                       ║
   ║   PASSO 5 — Cadastrar Fornecedores                    ║
   ║     ✓ CNPJ, contatos, ramo, cidade/UF                 ║
   ║     ✓ Vincular insumos via ItemFornecedor             ║
   ║       (preço + prazo de entrega) — alimenta a         ║
   ║       sugestão automática de pedido                   ║
   ║                                                       ║
   ║   PASSO 6 — Cadastrar Pratos                          ║
   ║     ✓ Nome, preço de venda                            ║
   ║     ✓ Receita (ItemPrato): qual insumo e quanto       ║
   ║       cada prato consome — alimenta a auto-baixa      ║
   ║       de estoque na venda                             ║
   ║                                                       ║
   ╚═══════════════════════════════════════════════════════╝
                                │
                                ▼
   ╔════════════ FEITO PELO GERENTE DE FILIAL ═════════════╗
   ║                                                       ║
   ║   PASSO 7 — Receber/Criar Pedidos (entrada)           ║
   ║     ✓ Pedido com Fornecedor + lista de insumos        ║
   ║     ✓ Status: pendente → concluida                    ║
   ║     → SOMENTE pedidos CONCLUÍDOS sobem o estoque      ║
   ║                                                       ║
   ║   PASSO 8 — Registrar Vendas (saída)                  ║
   ║     ✓ Venda com pratos vendidos (ItemVenda)           ║
   ║     ✓ Status concluida                                ║
   ║     → o signal post_save calcula automaticamente os   ║
   ║       ItemMovimentacao a partir da receita: cada      ║
   ║       prato baixa os insumos do estoque               ║
   ║                                                       ║
   ║   PASSO 9 — Movimentações livres (opcional)           ║
   ║     ✓ Ajuste de inventário, desperdício, etc.         ║
   ║                                                       ║
   ╚═══════════════════════════════════════════════════════╝
                                │
                                ▼
   ╔══════════════ DAÍ EM DIANTE — CONSULTAS ══════════════╗
   ║                                                       ║
   ║   /relatorios/estoque/      saldo atual por insumo    ║
   ║   /relatorios/ruptura/      alerta de estoque baixo   ║
   ║   /relatorios/consumo/      top insumos consumidos    ║
   ║   /relatorios/faturamento/  comparativo entre filiais ║
   ║   /sugestao-pedido/         pedidos sugeridos com     ║
   ║                             fornecedor mais barato    ║
   ║                                                       ║
   ╚═══════════════════════════════════════════════════════╝
```

### Regras importantes que dependem do fluxo

| Regra | Implicação prática |
|---|---|
| **Só `status=concluida` mexe no estoque** | Pedidos pendentes não sobem; vendas pendentes não baixam. Use status pra rascunho. |
| **`tipo` é forçado pelo modelo** | `Pedido` sempre vira `entrada`; `Venda` sempre vira `saida`. Não tem como bagunçar. |
| **Insumos da Venda são automáticos** | Não precisa preencher manualmente — basta listar pratos vendidos; o signal recalcula. |
| **Sugestão usa só insumos com `ItemFornecedor`** | Se um insumo está em ruptura mas sem fornecedor, ele aparece em "sem fornecedor" — cadastre o vínculo antes. |
| **Gerente sem `Filial.gerente` vê 0 dados** | Lembre-se de definir o gerente na Filial após criar o usuário. |
| **`is_matriz=True` pode estar em só uma Filial** | O `clean()` da Filial bloqueia uma segunda matriz. |

---

## Integração WhatsApp (Evolution API)

Tereza atende gerentes e fornecedores diretamente pelo WhatsApp. Em
vez de o gerente abrir o admin pra solicitar reposição, ele manda
mensagem; o bot calcula a sugestão de ruptura, confirma com ele, cria
os Pedidos e dispara WhatsApp pros fornecedores. Quando o fornecedor
responde "sim/tenho", o Pedido vira **CONCLUIDA** automaticamente
(estoque sobe). Quando responde "não", vira **CANCELADA**.

A camada externa de WhatsApp roda na **Evolution API** (Node + Postgres
+ Redis em containers Docker), embarcada em `evolution-api/`. O Django
fala com ela por HTTP nos dois sentidos: chama `/message/sendText` pra
enviar, recebe `POST /webhooks/evolution/` quando algo chega.

### O que está no repo

| Caminho | Função |
|---|---|
| `whatsapp/services.py` | Cliente HTTP da Evolution: `enviar_texto`, `numero_existe`, `listar_chats`, `listar_mensagens`, `estado_conexao`, normalização E.164. |
| `whatsapp/views.py` | Endpoint `POST /webhooks/evolution/`. Valida `apikey`, ignora `fromMe`, repassa pro bot. |
| `whatsapp/urls.py` | Roteia `/webhooks/evolution/` (sem `app_name` — URL externa, ninguém faz `reverse()` dela). |
| `whatsapp/phones.py` | Match tolerante de telefone (chave canônica = últimos 8 dígitos). Resolve quem é o remetente. |
| `whatsapp/bot.py` | Máquina de estados stateless: identifica gerente/fornecedor, gera sugestão, cria Pedidos, dispara confirmações. |
| `core/services/pedidos.py::sugerir_pedido_da_cidade` | Variante de `sugerir_pedido` que filtra fornecedores pela cidade da filial e ranqueia por preço. Consumida pelo bot. |
| `evolution-api/` | Stack Docker da Evolution (API + Manager + Postgres + Redis) com customizações para o Devathon. |
| `setup/settings.py` | Variáveis `EVOLUTION_*` + `host.docker.internal` em `ALLOWED_HOSTS`. |

### Setup da Evolution

```bash
# 1. Subir a stack
cd evolution-api
cp .env.example .env
# edite .env: defina AUTHENTICATION_API_KEY e POSTGRES_PASSWORD
docker compose up -d

# 2. Conferir que subiu
curl -s http://127.0.0.1:8081/                 # API
# Manager (UI) em http://127.0.0.1:3001/
```

Portas usadas (escolhidas pra não colidir com outra stack que rode em
8080/3000): API em **8081**, Manager em **3001**, Postgres e Redis só
internos.

### Setup do Django pra falar com a Evolution

No `setup/settings.py` (já configurado, sobrescreva via env var em prod):

```python
EVOLUTION_BASE_URL      = 'http://127.0.0.1:8081'
EVOLUTION_API_KEY       = '<mesmo AUTHENTICATION_API_KEY do .env>'
EVOLUTION_INSTANCE      = 'Tereza IA'      # nome da instância do WhatsApp
EVOLUTION_WEBHOOK_TOKEN = ''               # opcional, ver abaixo
EVOLUTION_HTTP_TIMEOUT  = 15               # segundos
```

`ALLOWED_HOSTS` precisa de `host.docker.internal` — é por esse hostname
que o container chama o Django no host.

E **rode o `runserver` em `0.0.0.0`** (não 127.0.0.1, senão o container
não enxerga):

```bash
python manage.py runserver 0.0.0.0:8000
```

### Parear um número (QR code)

1. Abre o Manager em <http://127.0.0.1:3001>
2. Login com a `AUTHENTICATION_API_KEY` do `.env`
3. Cria a instância **Tereza IA** (ou usa a existente)
4. **Connect / QR code** → escaneia no celular em
   *WhatsApp → Aparelhos conectados → Conectar um aparelho*

Se já existia parelhamento e caiu, normalmente a instância vai pra
`connecting` com `disconnectionReasonCode: 401` ("Log out instance").
**Remova primeiro o aparelho no celular** e reescaneie — escanear sem
remover não resolve.

### Cadastrar o webhook na Evolution

A Evolution não chama o Django sozinha — você precisa registrar a URL.
Uma vez só (e refaz se mudar URL/eventos):

```bash
API=http://127.0.0.1:8081
KEY=<sua AUTHENTICATION_API_KEY>

curl -s -X POST "$API/webhook/set/Tereza%20IA" \
  -H "Content-Type: application/json" -H "apikey: $KEY" \
  -d "{
    \"webhook\": {
      \"enabled\": true,
      \"url\": \"http://host.docker.internal:8000/webhooks/evolution/\",
      \"headers\": { \"apikey\": \"$KEY\" },
      \"byEvents\": false,
      \"base64\": false,
      \"events\": [\"MESSAGES_UPSERT\",\"CONNECTION_UPDATE\",\"SEND_MESSAGE\"]
    }
  }"
```

> **Cuidado:** o campo `headers` é essencial. Sem ele a Evolution não
> manda nenhum cabeçalho de auth e o webhook do Django responde `403`
> em todas as chamadas. A `apikey` ali precisa bater com
> `EVOLUTION_API_KEY` do Django.

### Pré-requisitos no banco pro bot funcionar

Pra um gerente conseguir interagir, é preciso ter cadastrado:

1. **User** com `telefone` (qualquer formato — `(88) 99937-7017`,
   `+55 88 9...`, etc — o bot normaliza por últimos 8 dígitos).
2. Esse User definido como **`Filial.gerente`** de alguma filial.
3. A **Filial com `cidade`** preenchida (caso contrário a sugestão
   cai no fallback "qualquer fornecedor").
4. Pelo menos um **Insumo** com `estoque_minimo > 0` que esteja em
   ruptura (sem entradas suficientes no estoque).
5. Um **Fornecedor** na **mesma cidade** da Filial, com `telefone`,
   ligado ao Insumo via **`ItemFornecedor`** (com preço).

Sem isso, quem manda mensagem cai em "remetente desconhecido"
(`User` sem telefone que bata) ou "nada a solicitar agora" (Insumos
sem ruptura ou sem fornecedor na cidade).

### Fluxo end-to-end

```
   ╔════════════════ GERENTE ═══════════════════╗
   ║                                            ║
   ║  1. Manda QUALQUER mensagem pra Tereza     ║
   ║       │                                    ║
   ║       ▼                                    ║
   ║  2. Bot identifica pelo telefone           ║
   ║     -> sugerir_pedido_da_cidade(filial)    ║
   ║     -> responde lista agrupada por         ║
   ║        fornecedor (filtro: mesma cidade,   ║
   ║        ranqueia por preço)                 ║
   ║       │                                    ║
   ║       ▼                                    ║
   ║  3. Gerente responde "confirmar" / "sim"   ║
   ║       │                                    ║
   ║       ▼                                    ║
   ║  4. Bot recalcula (idempotente) e cria     ║
   ║     1 Pedido PENDENTE por fornecedor       ║
   ║     escolhido. Dispara WhatsApp pra cada   ║
   ║     um. Manda resumo pro gerente.          ║
   ║                                            ║
   ╚════════════════════════════════════════════╝
                      │
                      ▼
   ╔══════════════ FORNECEDOR ══════════════════╗
   ║                                            ║
   ║  5. Recebe: "A Filial X precisa de:        ║
   ║     - 5 kg de tomate                       ║
   ║     - 3 kg de cebola                       ║
   ║     Pode atender? sim / não"               ║
   ║       │                                    ║
   ║       ├─ "sim" / "tenho" / "ok"            ║
   ║       │     -> Pedido vira CONCLUIDA       ║
   ║       │     -> estoque sobe                ║
   ║       │     -> gerente é avisado           ║
   ║       │                                    ║
   ║       └─ "não" / "cancela"                 ║
   ║             -> Pedido vira CANCELADA       ║
   ║             -> gerente é avisado           ║
   ║                                            ║
   ╚════════════════════════════════════════════╝
```

Resposta ambígua do fornecedor (algo como "talvez") **não muda
status** — bot pede esclarecimento. Mensagem vinda de telefone
desconhecido é silenciosamente ignorada (o bot não responde a
qualquer um que aparece).

### Identificação por telefone

| Onde está | Bot busca |
|---|---|
| `User.telefone` (qualquer formato) | `find_user_by_jid` — se bater, fluxo de gerente |
| `Fornecedor.telefone` | `find_fornecedor_by_jid` — se bater, fluxo de fornecedor |
| Nenhum | Ignora |

A chave de comparação são os **últimos 8 dígitos** do número (após
strip de tudo que não é dígito). Tolera máscara, com/sem DDI 55,
com/sem o '9' extra do celular brasileiro. Limitação aceita: dois
telefones com mesmos 8 dígitos finais colidem (improvável na prática).

### Trade-offs assumidos

| Decisão | Por quê |
|---|---|
| **Sem state machine persistido** | Cada mensagem é interpretada idempotentemente do zero. Reenviar "oi" 3x não cria pedido 3x — recalcula e re-apresenta. |
| **Sem persistir mensagens no Django** | O histórico vive no Postgres da Evolution. Quando precisar consultar, `whatsapp.services.listar_chats/listar_mensagens` chamam `/chat/findChats` da Evolution. |
| **CONCLUIDA na confirmação do fornecedor** | Estoque sobe quando o fornecedor diz "tenho", **antes** da mercadoria chegar fisicamente. Trade simples por menos campos/migrations — relatório de ruptura pode ficar otimista até o recebimento físico. |
| **1 Pedido por fornecedor (mais barato)** | Sem fan-out paralelo nem concorrência entre fornecedores. Quem confirma, leva. |
| **Match de telefone por 8 dígitos finais** | Robusto contra variações de formato sem precisar normalizar a base existente. Custo: colisão teórica entre números diferentes mas mesmos 8 finais. |
| **Mensagens vindas de grupos (`@g.us`)** | Ignoradas. |

### Customizações na pasta `evolution-api/`

A `evolution-api/` é a Evolution oficial (`evoapicloud/evolution-api`)
embarcada no monorepo. As customizações que fizemos:

- **`docker-compose.yaml`** — containers prefixados `devathon_*`,
  porta API em **8081**, Manager em **3001** (8080/3000 ocupadas por
  outra stack local). Healthchecks com `start_period` mais alto.
  `extra_hosts: host.docker.internal:host-gateway` no serviço `api`
  pro container alcançar o Django.
- **`Docker/manager/nginx.conf`** — override do nginx do Manager (a
  versão da imagem upstream tem `gzip_proxied` inválido que bota o
  container em loop de restart).
- **`.gitignore`** — reforçado pra `*.backup` além do que o upstream
  já cobre (`.env`, `node_modules`, `dist`, `prisma/migrations/*`).

O `.env` da Evolution **não** está versionado (tem segredos:
`AUTHENTICATION_API_KEY`, `POSTGRES_PASSWORD`). Use o `.env.example`
como template.

Pra atualizar a Evolution upstream:

```bash
cd evolution-api
# baixa só o que mudou no docker-compose oficial pra você comparar:
git diff <(curl -s https://raw.githubusercontent.com/evolution-foundation/evolution-api/main/docker-compose.yaml) docker-compose.yaml
# ou faz clone limpo num /tmp e usa diff/patch manualmente
```

A imagem (`evoapicloud/evolution-api:latest`) é puxada do Docker Hub
pelo compose, então a maior parte dos updates de funcionalidade vem
sozinha sem precisar rebaixar source.

### Troubleshooting

| Sintoma | Causa provável | Como resolver |
|---|---|---|
| `connectionState: connecting` + `disconnectionReasonCode: 401` | Sessão WhatsApp deslogada (manualmente no celular ou expirada) | Remova o aparelho no celular, reescaneie QR no Manager |
| Webhook responde **403** "webhook nao autorizado" | Evolution não está mandando o header `apikey` | Re-registra com `headers: {apikey: ...}` (ver "Cadastrar o webhook") |
| Logs da Evolution: `ECONNREFUSED 172.17.0.1:8000` | Django escutando só em 127.0.0.1 | `runserver 0.0.0.0:8000` |
| Manager (3001) não abre | nginx em loop por `gzip_proxied` | Confere se o volume `Docker/manager/nginx.conf` está mapeado no compose |
| Bot não responde a uma mensagem real | Telefone do remetente não bate com nenhum `User.telefone` ou `Fornecedor.telefone` | Confere cadastro; o log do Django mostra `Mensagem de remetente desconhecido` |
| `core` reclama que `requests` falta | Dependência nova | `pip install -r requirements.txt` |
| `host.docker.internal` não resolve dentro do container | Falta `extra_hosts` no compose | Já está no `evolution-api/docker-compose.yaml`; se editou, restaura |
| Sequência de erros `Tentativa N/10 falhou` no log da Evolution | Webhook chegando mas Django não responde 2xx | Verifica se Django tá no ar e a URL bate exatamente com o que está em `/webhook/find` |

### Endpoints úteis pra debug

```bash
API=http://127.0.0.1:8081
KEY=<sua AUTHENTICATION_API_KEY>

# Estado da instância (open / connecting / close)
curl -s "$API/instance/connectionState/Tereza%20IA" -H "apikey: $KEY"

# Lista todas as instâncias com contadores (Chat/Message/Contact)
curl -s "$API/instance/fetchInstances" -H "apikey: $KEY"

# Webhook configurado
curl -s "$API/webhook/find/Tereza%20IA" -H "apikey: $KEY"

# Forçar restart da conexão (sem desparear)
curl -s -X PUT "$API/instance/restart/Tereza%20IA" -H "apikey: $KEY"

# Ver chats salvos (Postgres da Evolution)
curl -s -X POST "$API/chat/findChats/Tereza%20IA" -H "apikey: $KEY" \
     -H "Content-Type: application/json" -d '{}'

# Mandar texto (do shell — útil pra testar saída isolada do bot)
curl -s -X POST "$API/message/sendText/Tereza%20IA" -H "apikey: $KEY" \
     -H "Content-Type: application/json" \
     -d '{"number":"55DDD9XXXXXXXX","text":"teste"}'
```

---

## Arquitetura

Resumo (a fundo em [`MAPEAMENTO.md`](./MAPEAMENTO.md)):

- **`core/models/`** — domínio: `User`, `Filial`, `Fornecedor`,
  `Insumo`, `Prato`, `Movimentacao` (com `Pedido` e `Venda` por
  multi-table inheritance), e through models (`ItemFornecedor`,
  `ItemPrato`, `ItemMovimentacao`, `ItemVenda`).
- **`core/services/`** — regras de domínio reutilizáveis: estoque,
  consumo, faturamento, sugestão de pedidos. Não dependem de admin
  nem de view. Inclui `sugerir_pedido_da_cidade` (variante com filtro
  geográfico, consumida pelo bot WhatsApp).
- **`core/admin/`** — admin Unfold com `FilialScopedAdminMixin`.
- **`core/views/`** — CBVs públicas com `MatrizRequiredMixin`,
  `GerenteFilialRequiredMixin`, `FilialScopedQuerysetMixin` e
  `FilialScopedFormMixin`.
- **`core/forms/`** — `ModelForm` por modelo + formsets inline.
- **`core/signals/`** — recalcula `ItemMovimentacao` da `Venda`
  automaticamente quando `ItemVenda` muda.
- **`core/permissions.py`** — `is_matriz()`, `is_gerente_filial()`
  (papel via Django Groups, sem campo `papel` em User).
- **`whatsapp/`** — app de integração com a Evolution API. Cliente
  HTTP (`services.py`), webhook de entrada (`views.py`), bot
  conversacional stateless (`bot.py`) e helpers de match de telefone
  (`phones.py`). Detalhes na seção
  [Integração WhatsApp](#integração-whatsapp-evolution-api).
- **`evolution-api/`** — stack Docker da Evolution (Node + Postgres +
  Redis) embarcada e customizada para o projeto. Roda separada do
  Django.

### Permissionamento

- **Grupos do Django** (criados por data migration `0013`):
  - `Matriz` — controle global; superusers entram aqui automaticamente
  - `Gerente de Filial` — vê e opera apenas a própria filial
- **`User.filial`** é uma `@property` que delega para `Filial.gerente`
  — sem FK duplicada.
- **Mixins** (`FilialScopedQuerysetMixin`, `FilialScopedAdminMixin`)
  filtram queryset; `FilialScopedFormMixin` esconde `filial`/`usuario`
  do form e auto-preenche no save.

---

## Para o front

Cada view CBV documenta no docstring:
- `template_name` esperado
- contrato do contexto (chaves e tipos)

Lista completa de templates pendentes em
[`MAPEAMENTO.md`](./MAPEAMENTO.md#templates-pendentes-frontendtemplates).

Templates ficam em **`frontend/templates/`** (já configurado no
`TEMPLATES['DIRS']` do `settings.py`).

---

## Roadmap

- [x] Modelagem do MVP (Fases 1–4)
- [x] Views públicas e CRUDs (Fases 5A–5C)
- [x] Relatórios (Fase 5D)
- [x] Solicitação guiada de insumos (Fase 7)
- [x] Documentação (Fase 9 — você está aqui)
- [x] Integração WhatsApp via Evolution API (bot stateless de
      solicitação/confirmação de pedidos — gerente e fornecedor
      conversam pelo mesmo canal)
- [ ] Validações duras: CNPJ, CPF + clean adicionais (Fase 8)
- [ ] Testes unitários
- [ ] Templates do front
- [ ] Migração para Postgres em produção
- [ ] Migrar instância da Evolution pra `WHATSAPP-BUSINESS` (Cloud API
      oficial) se o uso escalar — Baileys é mais frágil contra ban
