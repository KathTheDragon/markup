def html(tag: str, attributes: dict[str, str | bool]={}, content: str | None=None) -> str:
    if attributes:
        open = f'{tag} {format_attributes(attributes)}'
    else:
        open = tag
    close = tag

    if content is None:  # Self-closing
        return f'<{open} />'
    else:
        return f'<{open}>{content}</{close}>'


def format_attributes(attributes: dict[str, str | bool]) -> str:
    attrs = []
    for attribute, value in attributes.items():
        if value is True:
            attrs.append(attribute)
        elif value:
            attrs.append(f'{attribute}="{value}"')
    return ' '.join(attrs)
