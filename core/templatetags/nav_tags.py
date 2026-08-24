"""Template tags utilitárias da navegação (sidebar / topbar).

Use `{% active_link 'pedido_' 'sugestao_' %}` para marcar um link como ativo
quando o `url_name` da view atual começar com qualquer um dos prefixos dados.
"""

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def active_link(context, *prefixes, css_class='ts-side-link-active'):
    """Retorna `css_class` se o url_name atual bater com algum prefixo, senão "".

    Por que prefixos? As URLs CRUD do projeto seguem o padrão
    `<modelo>_list`, `<modelo>_create`, `<modelo>_detail`, etc. Passando
    `'pedido_'` casamos toda a família sem casar com `sugestao_pedido`.
    """
    request = context.get('request')
    if not request or not getattr(request, 'resolver_match', None):
        return ''
    url_name = request.resolver_match.url_name or ''
    return css_class if any(url_name.startswith(p) for p in prefixes) else ''
