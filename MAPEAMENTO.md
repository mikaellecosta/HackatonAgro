# Mapeamento de cobertura — User stories × código

Cada história do desafio Tereza Gastronomia mapeada para a feature, view,
service ou model que a cobre. Atualizar esta tabela quando algo mudar.

> Status: **11 de 11 histórias cobertas pelo backend.** O front consome
> as views Django (CBVs) listadas — templates pendentes em
> `frontend/templates/`.

---

## Matriz de cobertura

| # | História | Cobertura | URL | View | Service / Model |
|---|---|---|---|---|---|
| 1 | Visualizar vendas de cada filial em tempo real | ✅ | `/venda/` + `/relatorios/faturamento/` | `VendaListView`, `FaturamentoView` | `services.faturamento_por_filial`, `Venda` |
| 2 | Acessar lista de fornecedores | ✅ | `/fornecedor/` | `FornecedorListView` | `Fornecedor` |
| 3 | Cadastrar fornecedor (email, telefone, CNPJ, representante, localização, ramo) | ✅ | `/fornecedor/novo/` | `FornecedorCreateView` | `Fornecedor`, `RamoAlimenticio`, `Estado` |
| 4 | Registrar e acompanhar vendas da sede | ✅ | `/venda/`, `/venda/novo/` | `VendaListView`, `VendaCreateView` | `Venda`, `ItemVenda`, signal de recálculo |
| 5 | Fornecedores que atendem cada região | ✅ | `/fornecedor/?regiao=cidade\|estado` | `FornecedorListView` | filtro por `cidade`/`estado` em `Fornecedor` |
| 6 | Solicitar insumos pelo sistema (matriz) | ✅ | `/sugestao-pedido/` (GET) + `/sugestao-pedido/criar/` (POST) | `SugestaoPedidoView`, `CriarPedidoFromSugestaoView` | `services.sugerir_pedido`, `criar_pedido_da_sugestao` |
| 7 | Registrar filial (email, telefone, CNPJ, gestor, localização) | ✅ | `/filial/novo/` | `FilialCreateView` | `Filial`, `Estado` |
| 8 | Identificar padrões de consumo (matriz) | ✅ | `/relatorios/consumo/` | `ConsumoView` | `services.consumo_no_periodo`, `top_insumos_consumidos` |
| 9 | Vendas diárias da filial (gerente) | ✅ | `/venda/` (filial-scoped) | `VendaListView` + `FilialScopedQuerysetMixin` | `Venda` |
| 10 | Padrões de consumo (gerente) | ✅ | `/relatorios/consumo/` (filial-scoped) | `ConsumoView` | idem #8, com escopo automático na filial do gerente |
| 11 | Fornecedores da região + solicitar insumos (gerente) | ✅ | `/fornecedor/?regiao=...` + `/sugestao-pedido/` | idem #5 + #6 | idem |

---

## Permissionamento

Implementado **via Django Groups** (sem campo `papel` em User):

| Grupo | Permissões | Escopo |
|---|---|---|
| `Matriz` | 52 perms (CRUD em todo `core` + `auth.Group`) | global — vê todas as filiais |
| `Gerente de Filial` | 21 perms (view/add/change em movimentações; view em catálogo) | filial-scoped via `FilialScopedQuerysetMixin` |

**`User.filial`** é uma `@property` que retorna `self.filiais_gerenciadas.first()`
— sem FK duplicada; gerente é definido em `Filial.gerente`.

Helpers em `core/permissions.py`:
- `is_matriz(user)` — superuser **ou** grupo `Matriz`
- `is_gerente_filial(user)` — grupo `Gerente de Filial`

---

## Estrutura do código

```
core/
├── admin/             ModelAdmins (Unfold) com FilialScopedAdminMixin
│   ├── filial.py
│   ├── filters.py     MinhaRegiaoFilter
│   ├── fornecedor.py
│   ├── insumo.py
│   ├── mixins.py      FilialScopedAdminMixin
│   ├── movimentacao.py
│   ├── prato.py
│   └── user.py
├── forms/             ModelForms agrupados por modelo
│   ├── fornecedor.py
│   ├── filial.py
│   ├── insumo.py
│   ├── movimentacao.py    + ItemMovimentacaoFormSet, ItemVendaFormSet
│   └── prato.py            + ItemPratoFormSet
├── migrations/
├── models/            Pacotes de models, choices reutilizáveis
│   ├── choices.py     UnidadeMedida, TipoMovimentacao, StatusMovimentacao,
│   │                  Estado, RamoAlimenticio
│   ├── filial.py      Filial (com is_matriz, gerente FK, clean())
│   ├── fornecedor.py  Fornecedor + ItemFornecedor (M2M)
│   ├── insumo.py
│   ├── movimentacao.py Movimentacao + ItemMovimentacao + Pedido + Venda + ItemVenda
│   ├── prato.py       Prato + ItemPrato (receita)
│   └── user.py        User custom (cpf, telefone, foto_perfil) + property filial
├── permissions.py     Helpers is_matriz, is_gerente_filial
├── services/          Regras de domínio reutilizáveis (relatórios)
│   ├── consumo.py
│   ├── estoque.py     estoque_atual, insumos_em_ruptura
│   ├── faturamento.py
│   └── pedidos.py     sugerir_pedido, criar_pedido_da_sugestao
├── signals/           Recalcula ItemMovimentacao da Venda
│   └── venda.py
├── urls.py            Helper _crud() gera 5 paths × N modelos
└── views/             CBVs
    ├── base.py        MatrizRequiredMixin, GerenteFilialRequiredMixin,
    │                  FilialScopedQuerysetMixin, FilialScopedFormMixin
    ├── fornecedor.py
    ├── filial.py
    ├── insumo.py
    ├── prato.py
    ├── movimentacao.py
    ├── pedidos_sugestao.py
    ├── relatorios.py  EstoqueView, RupturaView, ConsumoView, FaturamentoView
    └── home.py
```

---

## URLs públicas

```
/                                Home (cards de KPI por papel)
/login/, /logout/                Auth (django.contrib.auth)
/admin/                          Admin do Django (Unfold)

# CRUD do catálogo (matriz cria/edita; gerente só lê)
/fornecedor/{,novo,<pk>,/<pk>/editar,/<pk>/excluir}/
/filial/{,novo,<pk>,/<pk>/editar,/<pk>/excluir}/    # filial-scoped p/ gerente
/insumo/{...}
/prato/{...}                       # com receita inline (ItemPratoFormSet)

# CRUD das operações (filial-scoped pra gerente)
/movimentacao/{...}
/pedido/{...}
/venda/{...}                       # com ItemVendaFormSet; insumos auto via signal

# Relatórios
/relatorios/estoque/             ?filial=<id>
/relatorios/ruptura/             ?filial=<id>
/relatorios/consumo/             ?filial=<id>&dias=<n>
/relatorios/faturamento/         ?filial=<id>&dias=<n>

# Solicitação guiada
/sugestao-pedido/                GET — mostra pedidos sugeridos
/sugestao-pedido/criar/          POST fornecedor=<id>
```

Total: **41 URLs** namespacedas como `core:*`.

---

## Templates pendentes (frontend/templates/)

```
registration/login.html

core/home.html

core/fornecedor/{list,detail,form,confirm_delete}.html
core/filial/{list,detail,form,confirm_delete}.html
core/insumo/{list,detail,form,confirm_delete}.html
core/prato/{list,detail,form,confirm_delete}.html
core/movimentacao/{list,detail,form,confirm_delete}.html
core/pedido/{list,detail,form,confirm_delete}.html
core/venda/{list,detail,form,confirm_delete}.html

core/relatorios/{estoque,ruptura,consumo,faturamento}.html

core/pedidos/sugestao.html
```

Cada view tem o **contrato do contexto documentado no docstring** — o front
sabe quais variáveis e tipos esperar sem precisar abrir o código Python.
