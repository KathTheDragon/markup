import re
from functools import wraps
from typing import Callable
from .html import Attributes, html
from .utils import partition, strip

_HandlerArgs = [str, Attributes, list[str], list[str] | None]
_HandlerReturn = tuple[str, Attributes, list[str] | None]
_Handler = Callable[_HandlerArgs, _HandlerReturn]
HandlerArgs = [str, str | None, list[str], list[str], list[str] | None]
Handler = Callable[HandlerArgs, str]

class MarkupError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class InvalidData(MarkupError):
    def __init__(self) -> None:
        super().__init__('Invalid data field')

    def __str__(self) -> str:
        return ''


def handler(func: _Handler) -> Handler:
    @wraps(func)
    def wrapper(command: str, id: str | None, classes: list[str], data: list[str], text: list[str] | None) -> str:
        attributes = {
            'id': id,
            'class': classes,
        }
        return html(*func(command, attributes, data, text))

    return wrapper


@handler
def simple_node(command: str, attributes: Attributes, data: list[str], text: list[str] | None) -> _HandlerReturn:
    if data:
        raise InvalidData()
    return command, attributes, text


@handler
def link_node(command: str, attributes: Attributes, data: list[str], text: list[str] | None) -> _HandlerReturn:
    if not data:
        raise InvalidData()
    if data[0] == '_blank':
        attributes['target'] = data.pop(0)
    if len(data) != 1:
        raise InvalidData()
    url, = data
    attributes['href'] = url
    if text is None:
        text = [url]

    return 'a', attributes, text


@handler
def section_node(command: str, attributes: Attributes, data: list[str], text: list[str] | None) -> _HandlerReturn:
    if len(data) != 2:
        raise InvalidData()
    level, title = data

    if attributes['id'] is None:
        attributes['id'] = f'sect-{title.lower().replace(" ", "-")}'

    if level not in ('1', '2', '3', '4', '5', '6'):
        raise MarkupError('Invalid level')
    heading = html(f'h{level}', {}, title)
    if text and text[0].startswith('\n'):
        indent = re.match(r'\n( *)', text[0]).group(1)
        text.insert(0, f'\n{indent}{heading}\n')
    else:
        text.insert(0, heading)

    return 'section', attributes, text


@handler
def footnote_node(command: str, attributes: Attributes, data: list[str], text: list[str] | None) -> _HandlerReturn:
    if len(data) != 1:
        raise InvalidData()
    number, = data
    attributes['class'].append('footnote')
    prefix = html('sup', {}, number)
    text.insert(0, prefix)

    return 'p', attributes, text


@handler
def list_node(command: str, attributes: Attributes, data: list[str], text: list[str] | None) -> _HandlerReturn:
    for attr in data:
        if attr.startswith('start='):
            attributes['start'] = attr.removeprefix('start=')
        elif attr == 'reversed':
            attributes['reversed'] = True
        else:
            raise InvalidData()

    if data:
        tag = 'ol'
    else:
        tag = 'ul'

    # Don't make list items if text is empty
    if text:
        parts = partition(text, '/')
        text = []
        for part in parts:
            leading, part, trailing = strip(part)
            if leading:
                text.append(leading)
            text.append(html('li', {}, ''.join(part)))
            if trailing:
                text.append(trailing)

    return tag, attributes, text


@handler
def table_node(command: str, attributes: Attributes, data: list[str], text: list[str] | None) -> _HandlerReturn:
    header_row = header_col = False
    for attr in data:
        if attr.startswith('headers='):
            headers = attr.removeprefix('headers=').split(',')
            header_row = 'rows' in headers
            header_col = 'cols' in headers
        else:
            raise InvalidData()

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
    return 'table', attributes, rows


SimpleNodes = dict[str, list[str]]
def make_simple_nodes() -> SimpleNodes:
    return {
        '$': [
            'br', 'blockquote', 'dl', 'dt', 'dd', 'div', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'hr', 'p', 'sup', 'sub', 'strong',
        ],
    }

NodeHandlers = dict[str, dict[str, Handler]]
def make_node_handlers() -> NodeHandlers:
    return {
        '$': {
            'footnote': footnote_node,
            'link': link_node,
            'list': list_node,
            'section': section_node,
            'table': table_node,
        }
    }
