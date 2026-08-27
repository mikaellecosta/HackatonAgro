"""
Popula o banco com dados de demonstração coerentes para a apresentação:

- 1 matriz e 2 filiais (Pinheiros/SP e Copacabana/RJ)
- superuser `admin` e gerentes de cada filial
- 4 fornecedores em diferentes ramos e estados
- 8 insumos com estoque mínimo
- 4 pratos com receita
- vínculos ItemFornecedor com preços
- vendas e pedidos concluídos para alimentar relatórios

Idempotente — pode rodar várias vezes; usa get_or_create na maior
parte e limpa apenas o que precisa ser regerado.
"""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.models import (
    Filial,
    Fornecedor,
    Insumo,
    ItemFornecedor,
    ItemMovimentacao,
    ItemPrato,
    ItemVenda,
    Pedido,
    Prato,
    User,
    Venda,
)
from core.models.GestaoFinanceira import (
    Estado,
    RamoAlimenticio,
    StatusMovimentacao,
    UnidadeMedida,
)
from core.permissions import GRUPO_GERENTE_FILIAL, GRUPO_MATRIZ


class Command(BaseCommand):
    help = 'Popula o banco com dados de demonstração do desafio Tereza.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Seeding Tereza Gastronomia...'))

        # --- Filiais ---
        matriz, _ = Filial.objects.update_or_create(
            nome='Tereza Matriz',
            defaults=dict(
                cnpj='11111111000111',
                email='matriz@tereza.com.br',
                telefone='11 3000-0000',
                cidade='São Paulo',
                estado=Estado.SP,
                endereco='Av. Paulista, 1000 - Bela Vista, 01310-100',
                is_matriz=True,
            ),
        )
        filial_sp, _ = Filial.objects.update_or_create(
            nome='Tereza Pinheiros',
            defaults=dict(
                cnpj='11111111000222',
                email='pinheiros@tereza.com.br',
                telefone='11 3030-3030',
                cidade='São Paulo',
                estado=Estado.SP,
                endereco='Rua dos Pinheiros, 500 - Pinheiros, 05422-000',
                is_matriz=False,
            ),
        )
        filial_rj, _ = Filial.objects.update_or_create(
            nome='Tereza Copacabana',
            defaults=dict(
                cnpj='11111111000333',
                email='copa@tereza.com.br',
                telefone='21 2222-2222',
                cidade='Rio de Janeiro',
                estado=Estado.RJ,
                endereco='Av. Atlântica, 2000 - Copacabana, 22021-001',
                is_matriz=False,
            ),
        )

        # --- Usuários ---
        grupo_matriz = Group.objects.get(name=GRUPO_MATRIZ)
        grupo_gerente = Group.objects.get(name=GRUPO_GERENTE_FILIAL)

        admin, criado = User.objects.get_or_create(
            username='admin',
            defaults=dict(
                email='admin@tereza.com.br',
                first_name='Tereza',
                last_name='Admin',
                is_staff=True,
                is_superuser=True,
            ),
        )
        if criado:
            admin.set_password('admin123')
            admin.save()
        admin.groups.add(grupo_matriz)

        gerente_sp, criado = User.objects.get_or_create(
            username='gerente_sp',
            defaults=dict(
                email='ana.sp@tereza.com.br',
                first_name='Ana',
                last_name='Souza',
                is_staff=True,
            ),
        )
        if criado:
            gerente_sp.set_password('tereza123')
            gerente_sp.save()
        gerente_sp.groups.add(grupo_gerente)
        if filial_sp.gerente_id != gerente_sp.pk:
            filial_sp.gerente = gerente_sp
            filial_sp.save()

        gerente_rj, criado = User.objects.get_or_create(
            username='gerente_rj',
            defaults=dict(
                email='bruno.rj@tereza.com.br',
                first_name='Bruno',
                last_name='Lima',
                is_staff=True,
            ),
        )
        if criado:
            gerente_rj.set_password('tereza123')
            gerente_rj.save()
        gerente_rj.groups.add(grupo_gerente)
        if filial_rj.gerente_id != gerente_rj.pk:
            filial_rj.gerente = gerente_rj
            filial_rj.save()

        # --- Insumos ---
        insumos_specs = [
            ('Tomate maduro',   UnidadeMedida.QUILOGRAMA, '8'),
            ('Queijo mussarela',UnidadeMedida.QUILOGRAMA, '5'),
            ('Massa de pizza',  UnidadeMedida.QUILOGRAMA, '4'),
            ('Manjericão fresco', UnidadeMedida.GRAMA, '300'),
            ('Azeite de oliva', UnidadeMedida.LITRO, '3'),
            ('Pão francês',     UnidadeMedida.UNIDADE, '50'),
            ('Café em grão',    UnidadeMedida.QUILOGRAMA, '2'),
            ('Leite integral',  UnidadeMedida.LITRO, '10'),
        ]
        insumos = {}
        for nome, unidade, minimo in insumos_specs:
            obj, _ = Insumo.objects.update_or_create(
                nome=nome,
                defaults=dict(
                    unidade_medida=unidade,
                    estoque_minimo=Decimal(minimo),
                ),
            )
            insumos[nome] = obj

        # --- Fornecedores ---
        fornecedores_specs = [
            dict(
                nome='Hortifruti Central SP',
                cnpj='22222222000111',
                ramo_alimenticio=RamoAlimenticio.HORTIFRUTI,
                representante='Carlos Mendes',
                email='vendas@hortisp.com.br',
                telefone='11 4040-4040',
                cidade='São Paulo', estado=Estado.SP,
                endereco='Rua das Frutas, 100',
            ),
            dict(
                nome='Laticínios Vale Verde',
                cnpj='33333333000111',
                ramo_alimenticio=RamoAlimenticio.LATICINIOS,
                representante='Helena Castro',
                email='comercial@valeverde.com.br',
                telefone='11 5050-5050',
                cidade='Campinas', estado=Estado.SP,
                endereco='Rod. das Vacas, km 12',
            ),
            dict(
                nome='Padaria Atlântica',
                cnpj='44444444000111',
                ramo_alimenticio=RamoAlimenticio.PADARIA,
                representante='João Almeida',
                email='joao@atlantica.com.br',
                telefone='21 6060-6060',
                cidade='Rio de Janeiro', estado=Estado.RJ,
                endereco='Av. Atlântica, 3000',
            ),
            dict(
                nome='Café & Cia',
                cnpj='55555555000111',
                ramo_alimenticio=RamoAlimenticio.MERCEARIA,
                representante='Luiza Pereira',
                email='luiza@cafeecia.com.br',
                telefone='31 7070-7070',
                cidade='Belo Horizonte', estado=Estado.MG,
                endereco='Av. dos Cafezais, 200',
            ),
        ]
        fornecedores = {}
        for spec in fornecedores_specs:
            obj, _ = Fornecedor.objects.update_or_create(
                cnpj=spec['cnpj'], defaults=spec,
            )
            fornecedores[spec['nome']] = obj

        # --- ItemFornecedor (preços) ---
        precos_specs = [
            # Hortifruti SP
            ('Hortifruti Central SP', 'Tomate maduro',   '6.50',  2),
            ('Hortifruti Central SP', 'Manjericão fresco', '0.05', 1),
            # Laticínios
            ('Laticínios Vale Verde', 'Queijo mussarela', '38.00', 3),
            ('Laticínios Vale Verde', 'Leite integral',   '4.20',  2),
            # Padaria RJ
            ('Padaria Atlântica',     'Pão francês',      '0.75',  1),
            ('Padaria Atlântica',     'Massa de pizza',   '12.00', 2),
            # Mercearia MG
            ('Café & Cia',            'Café em grão',     '52.00', 5),
            ('Café & Cia',            'Azeite de oliva',  '32.00', 3),
        ]
        for forn_nome, ins_nome, preco, prazo in precos_specs:
            ItemFornecedor.objects.update_or_create(
                fornecedor=fornecedores[forn_nome],
                insumo=insumos[ins_nome],
                defaults=dict(preco=Decimal(preco), prazo_entrega_dias=prazo),
            )

        # --- Pratos com receita ---
        pratos_specs = [
            ('Pizza Margherita', '49.90', [
                ('Tomate maduro', '0.20'),
                ('Queijo mussarela', '0.15'),
                ('Massa de pizza', '0.30'),
                ('Manjericão fresco', '5'),
                ('Azeite de oliva', '0.02'),
            ]),
            ('Pão na chapa com queijo', '12.50', [
                ('Pão francês', '1'),
                ('Queijo mussarela', '0.04'),
            ]),
            ('Café espresso', '8.00', [
                ('Café em grão', '0.012'),
            ]),
            ('Pingado', '7.00', [
                ('Café em grão', '0.008'),
                ('Leite integral', '0.10'),
            ]),
        ]
        pratos = {}
        for nome, preco, receita in pratos_specs:
            prato, _ = Prato.objects.update_or_create(
                nome=nome,
                defaults=dict(preco=Decimal(preco), ativo=True),
            )
            pratos[nome] = prato
            for ins_nome, qtd in receita:
                ItemPrato.objects.update_or_create(
                    prato=prato,
                    insumo=insumos[ins_nome],
                    defaults=dict(quantidade=Decimal(qtd)),
                )

        # --- Limpa operações antigas dessas filiais (idempotência) ---
        Pedido.objects.filter(filial__in=[filial_sp, filial_rj, matriz]).delete()
        Venda.objects.filter(filial__in=[filial_sp, filial_rj, matriz]).delete()

        # --- Pedidos concluídos (entrada de estoque) ---
        agora = timezone.now()
        for filial, gerente, qtds in [
            (filial_sp, gerente_sp, {
                'Tomate maduro': '20',
                'Queijo mussarela': '10',
                'Massa de pizza': '15',
                'Manjericão fresco': '500',
                'Azeite de oliva': '5',
            }),
            (filial_rj, gerente_rj, {
                'Pão francês': '200',
                'Queijo mussarela': '6',
                'Café em grão': '4',
                'Leite integral': '20',
            }),
        ]:
            # Cada pedido vai ao fornecedor mais barato do insumo
            por_forn = {}
            for nome, qtd in qtds.items():
                ins = insumos[nome]
                melhor = (
                    ItemFornecedor.objects.filter(insumo=ins)
                    .order_by('preco').first()
                )
                if melhor is None:
                    continue
                por_forn.setdefault(melhor.fornecedor, []).append((ins, Decimal(qtd)))
            for fornecedor, itens in por_forn.items():
                pedido = Pedido.objects.create(
                    filial=filial,
                    usuario=gerente,
                    fornecedor=fornecedor,
                    status=StatusMovimentacao.CONCLUIDA,
                    data=agora - timedelta(days=10),
                )
                ItemMovimentacao.objects.bulk_create([
                    ItemMovimentacao(movimentacao=pedido, insumo=ins, quantidade=qtd)
                    for ins, qtd in itens
                ])

        # --- Vendas concluídas (saída + signal recalcula insumos) ---
        for dia, filial, gerente, prato_qtds in [
            (1, filial_sp, gerente_sp, [('Pizza Margherita', 12)]),
            (2, filial_sp, gerente_sp, [('Pizza Margherita', 8), ('Pão na chapa com queijo', 5)]),
            (1, filial_rj, gerente_rj, [('Café espresso', 30), ('Pingado', 20)]),
            (3, filial_rj, gerente_rj, [('Pão na chapa com queijo', 10), ('Café espresso', 15)]),
        ]:
            preco_total = sum(
                pratos[nome].preco * qtd for nome, qtd in prato_qtds
            )
            venda = Venda.objects.create(
                filial=filial,
                usuario=gerente,
                preco=preco_total,
                status=StatusMovimentacao.CONCLUIDA,
                data=agora - timedelta(days=dia),
            )
            for nome, qtd in prato_qtds:
                ItemVenda.objects.create(
                    venda=venda, prato=pratos[nome], quantidade=qtd,
                )
            # signal post_save em ItemVenda já recalcula ItemMovimentacao

        self.stdout.write(self.style.SUCCESS(
            f'Pronto! {Filial.objects.count()} filiais, '
            f'{Fornecedor.objects.count()} fornecedores, '
            f'{Insumo.objects.count()} insumos, '
            f'{Prato.objects.count()} pratos, '
            f'{Pedido.objects.count()} pedidos, '
            f'{Venda.objects.count()} vendas.'
        ))
        self.stdout.write('')
        self.stdout.write('Usuários criados:')
        self.stdout.write('  admin / admin123 — superuser (Matriz)')
        self.stdout.write('  gerente_sp / tereza123 — Gerente Pinheiros')
        self.stdout.write('  gerente_rj / tereza123 — Gerente Copacabana')
