import re
from typing import Union
from .base import MarkupError, InvalidData, Node
from .table import TableNode
from ..html import Attributes, html
from ..utils import partition


class DescribeNode(Node):
    tag = 'dl'

    def make_content(self, text: list[str]) -> list[str]:
        content = []
        for row in partition(text, '/'):
            cells = partition(row, '|')
            term = cells.pop(0)
            if term:
                content.append(html('dt', {}, term))
            for desc in cells:
                content.append(html('dd', {}, desc))
        return content


class LinkNode(Node):
    tag = 'a'
    params = {'_blank?': False, 'url': None}

    def make_attributes(self) -> Attributes:
        return self.attributes | {
            'target': '_blank' if self.data['_blank'] else None,
            'href': self.data['url']
        }

    def make_content(self, text: list[str]) -> list[str]:
        return text or [self.data['url']]


class SectionNode(Node):
    tag = 'section'
    params = {'level': None}

    def make_data(self, data: Attributes) -> Attributes:
        if data['level'] not in ('1', '2', '3', '4', '5', '6'):
            raise InvalidData('level must be a digit 1-6')
        return data

    def make_content(self, text: list[str]) -> list[str]:
        title, body = partition(text, '/')
        return [html(f'h{self.data["level"]}', {}, title), ''] + body


class ListNode(Node):
    @property
    def tag(self) -> str:
        return 'ol' if any(self.data.values()) else 'ul'

    params = {'start=': '', 'reversed?': False}

    def make_attributes(self) -> Attributes:
        return self.attributes | self.data

    def make_content(self, text: list[str]) -> list[str]:
        # Don't make list items if text is empty
        if text:
            text = [html('li', {}, part) for part in partition(text, '/')]
        return text


SIMPLE_NODES = [
    'br', 'blockquote', 'div', 'em', 'hr', 'p', 'sup', 'sub', 'strong',
]
def _make_simple_node(node: str) -> Node:
    return type(f'{node.capitalize()}Node', (Node,), {'tag': node})

Nodes = dict[str, dict[str, Node]]
def make_nodes() -> Nodes:
    return {
        '$': {
            'describe': DescribeNode,
            'link': LinkNode,
            'list': ListNode,
            'section': SectionNode,
            'table': TableNode,
        } | {
            node: _make_simple_node(node) for node in SIMPLE_NODES
        }
    }
