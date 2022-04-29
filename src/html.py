from typing import Optional, Union

Attribute = Union[str, bool, list[str], None]
Attributes = dict[str, Attribute]

VOID = {
    'area',
    'base',
    'br',
    'col',
    'hr',
    'img',
    'input',
    'link',
    'meta',
    'source',
    'track',
    'wbr',
}
INLINE = {
    'a',
    'br',
    'em',
    'span',
    'strong',
    'sub',
    'sup',
}
TEXTBLOCK = {
    'caption',
    'dd',
    'dt',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'li',
    'p',
    'td',
    'th',
}
BLOCK = {
    'blockquote',
    'div',
    'dl',
    'hr',
    'ol',
    'section',
    'table',
    'tr',
    'ul',
}

def html(tag: str, attributes: Attributes, content: list[str]) -> str:
    open = f'{tag} {format_attributes(attributes)}'.strip()
    close = tag

    if tag in VOID:  # Self-closing
        return f'<{open} />'
    elif tag in BLOCK:  # Indented contents
        body = '\n'.join(content)
        return f'<{open}>\n{indent(body, 1)}\n</{close}>'
    else:
        return f'<{open}>{" ".join(content)}</{close}>'


def format_attributes(attributes: Attributes) -> str:
    attrs = []
    for attribute, value in attributes.items():
        if value is True:
            attrs.append(attribute)
        elif not value:
            continue
        elif isinstance(value, str):
            attrs.append(f'{attribute}="{value}"')
        elif isinstance(value, list):
            attrs.append(f'{attribute}="{" ".join(list(filter(None, value)))}"')
    return ' '.join(attrs)


def indent(text: str, depth: int=0) -> str:
    import re
    return re.sub(r'^', '    '*depth, text, flags=re.M)
