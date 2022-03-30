import re
from typing import Callable
from .exceptions import MarkupError
from .html import html
from .utils import partition, strip

def link_node(command: str, id: str | None, classes: list[str], data: list[str], text: list[str] | None) -> tuple[str, dict[str, str | bool], str | None, list[str], list[str]]:
    attributes = {}
    if data[0] == '_blank':
        attributes['target'] = data.pop(0)
    url, = data
    attributes['href'], = url
    if text is None:
        text = [url]

    return 'a', attributes, id, classes, text


def section_node(command: str, id: str | None, classes: list[str], data: list[str], text: list[str] | None) -> tuple[str, dict[str, str | bool], str | None, list[str], list[str]]:
    level, title = data

    if id is None:
        id = f'sect-{title.lower().replace(" ", "-")}'

    if level not in ('1', '2', '3', '4', '5', '6'):
        raise MarkupError('Invalid level')
    heading = html(f'h{level}', {}, title)
    if text[0].startswith('\n'):
        indent = re.match(r'\n( *)', text[0]).group(1)
        text.insert(0, f'\n{indent}{heading}\n')
    else:
        text.insert(0, heading)

    return 'section', {}, id, classes, text


def footnote_node(command: str, id: str | None, classes: list[str], data: list[str], text: list[str] | None) -> tuple[str, dict[str, str | bool], str | None, list[str], list[str]]:
    number, = data
    classes.append('footnote')
    prefix = html('sup', {}, number)
    text.insert(0, prefix)

    return 'p', {}, id, classes, text


def list_node(command: str, id: str | None, classes: list[str], data: list[str], text: list[str] | None) -> tuple[str, dict[str, str | bool], str | None, list[str], list[str]]:
    attributes = {}
    for attr in data:
        if attr.startswith('start='):
            attributes['start'] = attr.removeprefix('start=')
        elif attr == 'reversed':
            attributes['reversed'] = True
        else:
            raise MarkupError('Invalid tag data')

    if attributes:
        tag = 'ol'
    else:
        tag = 'ul'

    parts = partition(text, '/')
    text = []
    for part in parts:
        leading, part, trailing = strip(part)
        if leading:
            text.append(leading)
        text.append(html('li', {}, ''.join(part)))
        if trailing:
            text.append(trailing)

    return tag, attributes, id, classes, text


def table_node(command: str, id: str | None, classes: list[str], data: list[str], text: list[str] | None) -> tuple[str, dict[str, str | bool], str | None, list[str], list[str]]:
    header_row = header_col = False
    for attr in data:
        if attr.startswith('headers='):
            headers = attr.removeprefix('headers=').split(',')
            header_row = 'rows' in headers
            header_col = 'cols' in headers

    parts = partition(text, '//')
    if len(parts) == 1:
        caption, text = None, parts[0]
    else:
        caption, text = parts

    table = [[strip(cell) for cell in partition(row, '|')] for row in partition(text, '/')]
    if len(set(map(len, table))) != 1:
        raise MarkupError('Table rows must be the same size')
    merged = []
    for row in table:
        col = 0
        merged_row = []
        for leading, cell, trailing in row:
            if cell == '<':
                if not merged_row:
                    raise MarkupError('Invalid cell merge')
                merged_row[-1]['cols'] += 1
            elif cell == '^':
                if merged_row[-1]['data'] == ('', '^', ''):
                    merged_row[-1]['cols'] += 1
                else:
                    if merged_row:
                        col += merged_row[-1]['cols']
                    merged_row.append({'data': ('', '^', ''), 'rows': 1, 'cols': 1})
                for mrow in reversed(merged):
                    mcol = 0
                    for mcell in mrow:
                        if mcol == col:
                            break
                        elif mcol > col:
                            raise MarkupError('Misaligned table cell')
                        else:
                            mcol += mcell['cols']
                    if mcell['data'] is not None:
                        if mcell['cols'] == merged_row[-1]['cols']:
                            mcell['rows'] += 1
                            merged_row[-1]['data'] = None
                            break
                        else:
                            raise MarkupError('Misaligned table cell')
            else:
                if merged_row:
                    col += merged_row[-1]['cols']
                merged_row.append({'data': (leading, cell, trailing), 'rows': 1, 'cols': 1})
        if any(cell['data'] == ('', '^', '') for cell in merged_row):
            raise MarkupError('Invalid cell merge')
        merged.append(merged_row)
    rows = []
    if caption is not None:
        rows.append(html('caption', {}, ''.join(caption)))
    for mrow in merged:
        row = []
        for mcell in mrow:
            if mcell['data'] is not None:
                tag = 'th' if (header_row and not rows or header_col and not row) else 'td'
                leading, cell, trailing = mcell['data']
                attributes = {}
                if mcell['rows'] != 1:
                    attributes['rowspan'] = mcell['rows']
                if mcell['cols'] != 1:
                    attributes['colspan'] = mcell['cols']
                row.extend([leading, html(tag, attributes, ''.join(cell)), trailing])
        if row:
            rows.append(html('tr', {}, ''.join(row)))
    return 'table', {}, id, classes, rows


SIMPLE_TAGS = [
    'br', 'dl', 'dt', 'dd', 'div', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p', 'blockquote', 'sup', 'sub', 'strong',
]
HANDLERS = {
    'link': link_node,
    'section': section_node,
    'footnote': footnote_node,
    'list': list_node,
    'table': table_node,
}
HandlerType = Callable[[str, str | None, list[str], list[str], list[str] | None], tuple[str, dict[str, str | bool], str | None, list[str], list[str]]]

def get_handler(command: str) -> HandlerType:
    if command in HANDLERS:
        return HANDLERS[command]
    elif command in SIMPLE_TAGS:
        return lambda command, id, classes, data, text: (command, {}, id, classes, text)
    else:
        raise MarkupError('Invalid command')


def process(command: str, id: str | None, classes: list[str], data: list[str], text: list[str] | None) -> str:
    tag, attributes, id, classes, text = get_handler(command)(command, id, classes, data, text)

    if id is not None:
        attributes['id'] = id
    if classes:
        attributes['class'] = ' '.join(classes)

    return html(tag, attributes, ''.join(text) if text is not None else None)
