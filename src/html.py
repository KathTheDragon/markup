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

def html(tag: str, attributes: Attributes={}, content: list[str]=None) -> str:
    open = f'{tag} {format_attributes(attributes)}'.strip()
    close = tag

    if tag in VOID:  # Self-closing
        return f'<{open} />'
    else:
        return f'<{open}>{"".join(content)}</{close}>'


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
