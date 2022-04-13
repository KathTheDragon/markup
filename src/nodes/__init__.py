import re
from typing import Optional
from .base import Node, HTML
from .exceptions import MarkupError, InvalidData
from .table import TableNode
from ..html import Attributes, html
from ..utils import partition, strip


class DescribeNode(Node):
    @staticmethod
    def process(attributes: Attributes, data: list[str], text: Optional[list[str]]) -> HTML:
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


class LinkNode(Node):
    @staticmethod
    def process(attributes: Attributes, data: list[str], text: Optional[list[str]]) -> HTML:
        if len(data) == 2 and data[0] == '_blank':
            attributes['target'], attributes['href'] = data
        elif len(data) == 1:
            attributes['href'], = data
        else:
            raise InvalidData()
        if text is None:
            text = [url]

        return 'a', attributes, text


class SectionNode(Node):
    @staticmethod
    def process(attributes: Attributes, data: list[str], text: Optional[list[str]]) -> HTML:
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


class FootnoteNode(Node):
    @staticmethod
    def process(attributes: Attributes, data: list[str], text: Optional[list[str]]) -> HTML:
        if len(data) != 1:
            raise InvalidData()
        number, = data
        attributes['class'].append('footnote')
        prefix = html('sup', {}, [number])
        text = text or []
        text.insert(0, prefix)

        return 'p', attributes, text


class ListNode(Node):
    @staticmethod
    def process(attributes: Attributes, data: list[str], text: Optional[list[str]]) -> HTML:
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


SIMPLE_NODES = [
    'br', 'blockquote', 'div', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'hr', 'p', 'sup', 'sub', 'strong',
]
def _make_simple_node(node: str) -> Node:
    class SimpleNode(Node):
        @staticmethod
        def process(attributes: Attributes, data: list[str], text: Optional[list[str]]) -> HTML:
            if data:
                raise InvalidData()
            return node, attributes, text
    name = f'{node.capitalize()}Node'
    SimpleNode.__name__ = name
    SimpleNode.__qualname__ = name

    return SimpleNode

Nodes = dict[str, dict[str, Node]]
def make_nodes() -> Nodes:
    return {
        '$': {
            'describe': DescribeNode,
            'footnote': FootnoteNode,
            'link': LinkNode,
            'list': ListNode,
            'section': SectionNode,
            'table': TableNode,
        } | {
            node: _make_simple_node(node) for node in SIMPLE_NODES
        }
    }
