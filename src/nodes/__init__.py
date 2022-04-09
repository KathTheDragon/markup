import re
from typing import Optional
from .handler import handler, Handler, _HandlerReturn
from .exceptions import MarkupError, InvalidData
from .table import table_node
from ..html import Attributes, html
from ..utils import partition, strip

@handler
def simple_node(command: str, attributes: Attributes, data: list[str], text: Optional[list[str]]) -> _HandlerReturn:
    if data:
        raise InvalidData()
    return command, attributes, text


@handler
def describe_node(command: str, attributes: Attributes, data: list[str], text: Optional[list[str]]) -> _HandlerReturn:
    if data:
        raise InvalidData()

    content = []
    for row in partition(text or [], '/'):
        cells = [strip(cell) for cell in partition(row, '|')]
        leading, term, trailing = cells.pop(0)
        if term:
            content.extend([leading, html('dt', {}, term), trailing])
        else:
            content.append(leading)
        for leading, desc, trailing in cells:
            content.extend([leading, html('dd', {}, desc), trailing])

    return 'dl', attributes, content


@handler
def link_node(command: str, attributes: Attributes, data: list[str], text: Optional[list[str]]) -> _HandlerReturn:
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
def section_node(command: str, attributes: Attributes, data: list[str], text: Optional[list[str]]) -> _HandlerReturn:
    if len(data) != 2:
        raise InvalidData()
    level, title = data

    if attributes['id'] is None:
        attributes['id'] = f'sect-{title.lower().replace(" ", "-")}'

    if level not in ('1', '2', '3', '4', '5', '6'):
        raise MarkupError('Invalid level')
    heading = html(f'h{level}', {}, [title])
    text = text or []
    if text and text[0].startswith('\n'):
        indent = re.match(r'\n( *)', text[0]).group(1)
        text.insert(0, f'\n{indent}{heading}\n')
    else:
        text.insert(0, heading)

    return 'section', attributes, text


@handler
def footnote_node(command: str, attributes: Attributes, data: list[str], text: Optional[list[str]]) -> _HandlerReturn:
    if len(data) != 1:
        raise InvalidData()
    number, = data
    attributes['class'].append('footnote')
    prefix = html('sup', {}, [number])
    text = text or []
    text.insert(0, prefix)

    return 'p', attributes, text


@handler
def list_node(command: str, attributes: Attributes, data: list[str], text: Optional[list[str]]) -> _HandlerReturn:
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
            text.append(html('li', {}, part))
            if trailing:
                text.append(trailing)

    return tag, attributes, text or []


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
            'describe': describe_node,
            'footnote': footnote_node,
            'link': link_node,
            'list': list_node,
            'section': section_node,
            'table': table_node,
        }
    }
