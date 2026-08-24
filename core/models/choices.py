from django.db import models


class UnidadeMedida(models.TextChoices):
    QUILOGRAMA = 'kg', 'Quilograma (kg)'
    GRAMA = 'g', 'Grama (g)'
    LITRO = 'l', 'Litro (L)'
    MILILITRO = 'ml', 'Mililitro (mL)'
    UNIDADE = 'un', 'Unidade (un)'
    CAIXA = 'cx', 'Caixa (cx)'
    PACOTE = 'pct', 'Pacote (pct)'
    DUZIA = 'dz', 'Dúzia (dz)'


class TipoMovimentacao(models.TextChoices):
    ENTRADA = 'entrada', 'Entrada'
    SAIDA = 'saida', 'Saída'
    DESPERDICIO = 'desperdicio', 'Desperdício'
    AJUSTE = 'ajuste', 'Ajuste'


class StatusMovimentacao(models.TextChoices):
    PENDENTE = 'pendente', 'Pendente'
    CONCLUIDA = 'concluida', 'Concluída'
    CANCELADA = 'cancelada', 'Cancelada'


class Estado(models.TextChoices):
    AC = 'AC', 'Acre'
    AL = 'AL', 'Alagoas'
    AP = 'AP', 'Amapá'
    AM = 'AM', 'Amazonas'
    BA = 'BA', 'Bahia'
    CE = 'CE', 'Ceará'
    DF = 'DF', 'Distrito Federal'
    ES = 'ES', 'Espírito Santo'
    GO = 'GO', 'Goiás'
    MA = 'MA', 'Maranhão'
    MT = 'MT', 'Mato Grosso'
    MS = 'MS', 'Mato Grosso do Sul'
    MG = 'MG', 'Minas Gerais'
    PA = 'PA', 'Pará'
    PB = 'PB', 'Paraíba'
    PR = 'PR', 'Paraná'
    PE = 'PE', 'Pernambuco'
    PI = 'PI', 'Piauí'
    RJ = 'RJ', 'Rio de Janeiro'
    RN = 'RN', 'Rio Grande do Norte'
    RS = 'RS', 'Rio Grande do Sul'
    RO = 'RO', 'Rondônia'
    RR = 'RR', 'Roraima'
    SC = 'SC', 'Santa Catarina'
    SP = 'SP', 'São Paulo'
    SE = 'SE', 'Sergipe'
    TO = 'TO', 'Tocantins'


class RamoAlimenticio(models.TextChoices):
    CARNES = 'carnes', 'Carnes e frios'
    HORTIFRUTI = 'hortifruti', 'Hortifruti'
    MERCEARIA = 'mercearia', 'Mercearia'
    LATICINIOS = 'laticinios', 'Laticínios'
    BEBIDAS = 'bebidas', 'Bebidas'
    BEBIDAS_ALCOOLICAS = 'bebidas_alcoolicas', 'Bebidas alcoólicas'
    PADARIA = 'padaria', 'Padaria e confeitaria'
    CONGELADOS = 'congelados', 'Congelados'
    DESCARTAVEIS = 'descartaveis', 'Descartáveis e embalagens'
    LIMPEZA = 'limpeza', 'Higiene e limpeza'
    OUTROS = 'outros', 'Outros'
