"""
Popula o banco com dados de demonstração agrícolas para a apresentação:

- 1 matriz e 2 unidades produtivas no Ceará
- superuser `admin` e gerentes de cada filial
- 4 fornecedores de insumos agrícolas
- 8 insumos com estoque mínimo
- 4 produtos agrícolas com composição
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
from core.models.choices import (
    Estado,
    RamoAlimenticio,
    StatusMovimentacao,
    UnidadeMedida,
)
from core.permissions import GRUPO_GERENTE_FILIAL, GRUPO_MATRIZ


class Command(BaseCommand):
    help = 'Popula o banco com dados de demonstração da operação agrícola.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Seeding Colheita de Dados...'))

        # Remove os registros do cenário antigo antes de recriar o demo agrícola.
        legacy_filiais = Filial.objects.filter(nome__in=[
            'Tereza Matriz', 'Tereza Pinheiros', 'Tereza Copacabana',
        ])
        Pedido.objects.filter(filial__in=legacy_filiais).delete()
        Venda.objects.filter(filial__in=legacy_filiais).delete()
        legacy_filiais.delete()

        Prato.objects.filter(nome__in=[
            'Pizza Margherita', 'Pão na chapa com queijo', 'Café espresso',
            'Pingado', 'Lote de milho para plantio',
            'Mudas de tomate selecionadas', 'Aplicação de bioinsumo',
        ]).delete()
        Insumo.objects.filter(nome__in=[
            'Tomate maduro', 'Queijo mussarela', 'Massa de pizza',
            'Manjericão fresco', 'Azeite de oliva', 'Pão francês',
            'Café em grão', 'Leite integral',
        ]).delete()
        Fornecedor.objects.filter(nome__in=[
            'Hortifruti Central SP', 'Laticínios Vale Verde',
            'Padaria Atlântica', 'Café & Cia', 'Cooperativa Sertão Verde',
            'AgroCampo Insumos Rurais',
        ]).delete()
        User.objects.filter(username__in=['gerente_sp', 'gerente_rj']).delete()

        # --- Filiais ---
        matriz, _ = Filial.objects.update_or_create(
            nome='Colheita de Dados - Matriz',
            defaults=dict(
                cnpj='11111111000111',
                email='matriz@colheitadedados.com.br',
                telefone='88 3000-0000',
                cidade='Iguatu',
                estado=Estado.CE,
                endereco='Rod. CE-060, km 12 - Zona Rural',
                is_matriz=True,
            ),
        )
        filial_sp, _ = Filial.objects.update_or_create(
            nome='Unidade Milho Sertão',
            defaults=dict(
                cnpj='11111111000222',
                email='milho@colheitadedados.com.br',
                telefone='88 3030-3030',
                cidade='Quixelô',
                estado=Estado.CE,
                endereco='Sítio Boa Esperança, Zona Rural',
                is_matriz=False,
            ),
        )
        filial_rj, _ = Filial.objects.update_or_create(
            nome='Unidade Horticultura Verde',
            defaults=dict(
                cnpj='11111111000333',
                email='horticultura@colheitadedados.com.br',
                telefone='88 2222-2222',
                cidade='Jucás',
                estado=Estado.CE,
                endereco='Fazenda Lagoa Seca, Zona Rural',
                is_matriz=False,
            ),
        )

        # --- Usuários ---
        grupo_matriz = Group.objects.get(name=GRUPO_MATRIZ)
        grupo_gerente = Group.objects.get(name=GRUPO_GERENTE_FILIAL)

        admin, criado = User.objects.get_or_create(
            username='admin',
            defaults=dict(
                email='admin@colheitadedados.com.br',
                first_name='Colheita',
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
            username='gerente_milho',
            defaults=dict(
                email='gerente.milho@colheitadedados.com.br',
                first_name='Ana',
                last_name='Sertão',
                is_staff=True,
            ),
        )
        if criado:
            gerente_sp.set_password('agro123')
            gerente_sp.save()
        gerente_sp.groups.add(grupo_gerente)
        if filial_sp.gerente_id != gerente_sp.pk:
            filial_sp.gerente = gerente_sp
            filial_sp.save()

        gerente_rj, criado = User.objects.get_or_create(
            username='gerente_horta',
            defaults=dict(
                email='gerente.horta@colheitadedados.com.br',
                first_name='Bruno',
                last_name='Verde',
                is_staff=True,
            ),
        )
        if criado:
            gerente_rj.set_password('agro123')
            gerente_rj.save()
        gerente_rj.groups.add(grupo_gerente)
        if filial_rj.gerente_id != gerente_rj.pk:
            filial_rj.gerente = gerente_rj
            filial_rj.save()

        # --- Insumos ---
        insumos_specs = [
            ('Sementes de milho híbrido', UnidadeMedida.QUILOGRAMA, '25'),
            ('Fertilizante NPK 04-14-08', UnidadeMedida.QUILOGRAMA, '100'),
            ('Mudas de tomate', UnidadeMedida.UNIDADE, '500'),
            ('Bioinsumo para controle biológico', UnidadeMedida.LITRO, '20'),
            ('Calcário agrícola', UnidadeMedida.QUILOGRAMA, '250'),
            ('Sementes de feijão', UnidadeMedida.QUILOGRAMA, '30'),
            ('Herbicida seletivo', UnidadeMedida.LITRO, '15'),
            ('Ração para gado', UnidadeMedida.QUILOGRAMA, '300'),
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
                nome='AgroCampo Insumos Rurais',
                cnpj='22222222000111',
                ramo_alimenticio=RamoAlimenticio.HORTIFRUTI,
                representante='Carlos Mendes',
                email='vendas@agrocampo.com.br',
                telefone='85 4040-4040',
                cidade='Fortaleza', estado=Estado.CE,
                endereco='Av. das Sementes, 450 - Messejana',
            ),
            dict(
                nome='Cooperativa Sertão Verde',
                cnpj='33333333000111',
                ramo_alimenticio=RamoAlimenticio.HORTIFRUTI,
                representante='Helena Castro',
                email='comercial@sertaoverde.coop.br',
                telefone='88 5050-5050',
                cidade='Iguatu', estado=Estado.CE,
                endereco='Rod. CE-060, km 12 - Zona Rural',
            ),
            dict(
                nome='Nutrivale Fertilizantes',
                cnpj='44444444000111',
                ramo_alimenticio=RamoAlimenticio.OUTROS,
                representante='João Almeida',
                email='joao@nutrivale.com.br',
                telefone='85 6060-6060',
                cidade='Sobral', estado=Estado.CE,
                endereco='Rod. BR-222, km 18 - Distrito Industrial',
            ),
            dict(
                nome='Sertão Sementes',
                cnpj='55555555000111',
                ramo_alimenticio=RamoAlimenticio.MERCEARIA,
                representante='Luiza Pereira',
                email='luiza@sertaosementes.com.br',
                telefone='88 7070-7070',
                cidade='Crato', estado=Estado.CE,
                endereco='Av. do Agricultor, 200 - Centro',
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
            ('AgroCampo Insumos Rurais', 'Herbicida seletivo', '48.00', 5),
            ('AgroCampo Insumos Rurais', 'Ração para gado', '2.90', 3),
            ('Cooperativa Sertão Verde', 'Mudas de tomate', '1.80', 7),
            ('Cooperativa Sertão Verde', 'Bioinsumo para controle biológico', '28.00', 5),
            ('Nutrivale Fertilizantes', 'Fertilizante NPK 04-14-08', '3.20', 12),
            ('Nutrivale Fertilizantes', 'Calcário agrícola', '0.65', 10),
            ('Sertão Sementes', 'Sementes de milho híbrido', '14.50', 10),
            ('Sertão Sementes', 'Sementes de feijão', '11.80', 8),
        ]
        for forn_nome, ins_nome, preco, prazo in precos_specs:
            ItemFornecedor.objects.update_or_create(
                fornecedor=fornecedores[forn_nome],
                insumo=insumos[ins_nome],
                defaults=dict(preco=Decimal(preco), prazo_entrega_dias=prazo),
            )

        # --- Produtos agrícolas com composição ---
        pratos_specs = [
            ('Saca de milho beneficiado', '145.00', [
                ('Sementes de milho híbrido', '1'),
            ]),
            ('Lote de mudas de tomate', '90.00', [
                ('Mudas de tomate', '10'),
            ]),
            ('Aplicação de bioinsumo', '320.00', [
                ('Bioinsumo para controle biológico', '5'),
            ]),
            ('Análise de solo e recomendação', '180.00', [
                ('Calcário agrícola', '20'),
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
                'Sementes de milho híbrido': '120',
                'Fertilizante NPK 04-14-08': '500',
                'Calcário agrícola': '800',
            }),
            (filial_rj, gerente_rj, {
                'Mudas de tomate': '1500',
                'Bioinsumo para controle biológico': '60',
                'Herbicida seletivo': '40',
            }),
            (matriz, admin, {
                'Sementes de feijão': '100',
                'Ração para gado': '1000',
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
            (1, filial_sp, gerente_sp, [('Saca de milho beneficiado', 12)]),
            (2, filial_sp, gerente_sp, [('Aplicação de bioinsumo', 3)]),
            (1, filial_rj, gerente_rj, [('Lote de mudas de tomate', 20)]),
            (3, filial_rj, gerente_rj, [('Análise de solo e recomendação', 8)]),
            (4, matriz, admin, [('Saca de milho beneficiado', 25)]),
            (5, matriz, admin, [('Lote de mudas de tomate', 30)]),
            (6, matriz, admin, [('Aplicação de bioinsumo', 5)]),
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
        self.stdout.write('  gerente_milho / agro123 — Unidade Milho Sertão')
        self.stdout.write('  gerente_horta / agro123 — Unidade Horticultura Verde')
