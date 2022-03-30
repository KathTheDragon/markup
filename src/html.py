Attribute = str | bool | list[str] | None
Attributes = dict[str, Attribute]

def html(tag: str, attributes: Attributes={}, content: list[str] | None=None) -> str:
    if attributes:
        open = f'{tag} {format_attributes(attributes)}'
    else:
        open = tag
    close = tag

    if content is None:  # Self-closing
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
            attrs.append(f'{attribute}="{" ".join(value)}"')
    return ' '.join(attrs)
