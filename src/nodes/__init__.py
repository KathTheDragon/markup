import re
from .base import MarkupError, InvalidData, Node
from .table import TableNode
from ..html import Attributes, html
from ..utils import partition, strip


class DescribeNode(Node):
    tag = 'dl'

    def make_content(self) -> list[str]:
        content = []
        for row in partition(self.text, '/'):
            cells = [strip(cell) for cell in partition(row, '|')]
            leading, term, trailing = cells.pop(0)
            if term:
                content.extend([leading, html('dt', {}, term), trailing])
            else:
                content.append(leading)
            for leading, desc, trailing in cells:
                content.extend([leading, html('dd', {}, desc), trailing])
        return content


class LinkNode(Node):
    tag = 'a'
    params = {'_blank?': False, 'url': None}

    def make_attributes(self) -> Attributes:
        return self.attributes | {
            'target': '_blank' if self.data['_blank'] else None,
            'href': self.data['url']
        }

    def make_content(self) -> list[str]:
        return self.text or [self.data['url']]


class SectionNode(Node):
    tag = 'section'
    params = {'level': None, 'title': None}

    def make_data(self, data: Attributes) -> Attributes:
        if data['level'] not in ('1', '2', '3', '4', '5', '6'):
            raise InvalidData('level must be a digit 1-6')
        return data

    def make_attributes(self) -> Attributes:
        id = self.attributes['id'] or f'sect-{self.data["title"].lower().replace(" ", "-")}'
        return self.attributes | {'id': id}

    def make_content(self) -> list[str]:
        level, title = self.data['level'], self.data['title']
        heading = html(f'h{level}', {}, [title])
        if self.text and self.text[0].startswith('\n'):
            indent = re.match(r'\n( *)', self.text[0]).group(1)
            heading = f'\n{indent}{heading}\n'
        return [heading, *self.text]


class ListNode(Node):
    @property
    def tag(self) -> str:
        return 'ol' if any(self.data.values()) else 'ul'

    params = {'start=': '', 'reversed?': False}

    def make_attributes(self) -> Attributes:
        return self.attributes | self.data

    def make_content(self) -> list[str]:
        # Don't make list items if text is empty
        text = self.text
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
        return text


SIMPLE_NODES = [
    'br', 'blockquote', 'div', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'hr', 'p', 'sup', 'sub', 'strong',
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
