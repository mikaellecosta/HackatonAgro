"""
Match tolerante de telefones para identificar quem mandou a mensagem.

O JID que a Evolution entrega vem como `5588999377017@s.whatsapp.net`
(DDI 55 + DDD + número, com o '9' do celular brasileiro). Mas o
`User.telefone` e `Fornecedor.telefone` no banco vêm digitados à mão,
podendo estar:

    - com máscara: '(88) 99937-7017'
    - sem DDI: '88999377017'
    - sem o '9' extra de celular: '8899377017'
    - com DDI: '+5588999377017'

Em vez de exigir que tudo seja normalizado na entrada (o que obrigaria
mexer em forms e migrar dados existentes), comparamos por uma chave
canônica baseada nos últimos 8 dígitos — assinatura do número que
sobrevive a todas essas variações comuns. Limitação aceita: dois
telefones com os mesmos 8 dígitos finais colidem (improvável no escopo).
"""
from __future__ import annotations


def _digits(s: str | None) -> str:
    """Devolve só os dígitos da string (descarta máscara, espaços, '+')."""
    if not s:
        return ''
    return ''.join(c for c in s if c.isdigit())


def jid_to_digits(jid: str) -> str:
    """
    Extrai os dígitos do JID da Evolution.

        '5588999377017@s.whatsapp.net' -> '5588999377017'
        '5511...@g.us' (grupo)         -> '5511...'
    """
    if not jid:
        return ''
    return _digits(jid.split('@', 1)[0])


def is_group_jid(jid: str) -> bool:
    """JIDs de grupo terminam em @g.us — não tratamos grupos por enquanto."""
    return bool(jid) and jid.endswith('@g.us')


def phone_key(value: str | None) -> str | None:
    """
    Chave canônica de comparação: últimos 8 dígitos do número
    (DDD2 + final-8 já é suficiente assinatura na prática).

    Devolve None se o valor não tem dígitos suficientes para servir
    como identificador.
    """
    d = _digits(value)
    if len(d) < 8:
        return None
    return d[-8:]


def phones_match(stored: str | None, jid_or_phone: str | None) -> bool:
    """True se os dois telefones provavelmente são o mesmo número."""
    a = phone_key(stored)
    b = phone_key(jid_or_phone)
    return bool(a) and a == b


def find_user_by_jid(jid: str):
    """
    Acha o User cujo `telefone` bate com o JID. Retorna None se ninguém
    bate. Importação local pra evitar ciclo de import quando este módulo
    é carregado antes do app `core` estar pronto.
    """
    from core.models import User

    target = phone_key(jid_to_digits(jid))
    if not target:
        return None
    # Filtra no Python — a base de usuários é pequena e o telefone está
    # com máscara mista. Em escala, normalizar no save resolve.
    for user in User.objects.exclude(telefone='').exclude(telefone__isnull=True):
        if phone_key(user.telefone) == target:
            return user
    return None


def find_fornecedores_by_jid(jid: str):
    """
    Acha TODOS os Fornecedores cujo `telefone` bate com o JID.

    Retorna lista — vazia se ninguém bate, com mais de um item quando
    dois cadastros compartilham o mesmo número (sócios da mesma empresa,
    representante de duas marcas, dado mal preenchido). Quem chama
    decide a ambiguidade — tipicamente olhando qual fornecedor tem
    pedido pendente.
    """
    from core.models import Fornecedor

    target = phone_key(jid_to_digits(jid))
    if not target:
        return []
    encontrados = []
    for fornecedor in Fornecedor.objects.exclude(telefone='').exclude(telefone__isnull=True):
        if phone_key(fornecedor.telefone) == target:
            encontrados.append(fornecedor)
    return encontrados


def find_fornecedor_by_jid(jid: str):
    """Compat: devolve o primeiro match (use `find_fornecedores_by_jid`)."""
    encontrados = find_fornecedores_by_jid(jid)
    return encontrados[0] if encontrados else None
