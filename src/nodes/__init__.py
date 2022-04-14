import re
from typing import Optional
from .base import Node
from .exceptions import MarkupError, InvalidData
from .table import TableNode
from ..html import Attributes, html
from ..utils import partition, strip


class DescribeNode(Node):
    tag = 'dl'

    def make_content(self) -> Optional[list[str]]:
        content = []
        for row in partition(self.text or [], '/'):
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

    def parse_data(self, data: list[str]) -> Attributes:
        data_dict = {}
        if len(data) == 2 and data[0] == '_blank':
            data_dict['target'], data_dict['href'] = data
        elif len(data) == 1:
            data_dict['href'], = data
        else:
            raise InvalidData()
        return data_dict

    def make_content(self) -> Optional[list[str]]:
        return self.text or [self.data['href']]


class SectionNode(Node):
    tag = 'section'

    def parse_data(self, data: list[str]) -> Attributes:
        if len(data) != 2 or data[0] not in ('1', '2', '3', '4', '5', '6'):
            raise InvalidData()
        return {'level': data[0], 'title': data[1]}

    def make_attributes(self) -> Attributes:
        id = self.attributes['id'] or f'sect-{self.data["title"].lower().replace(" ", "-")}'
        return self.attributes | {'id': id}

    def make_content(self) -> Optional[list[str]]:
        level, title = self.data['level'], self.data['title']
        heading = html(f'h{level}', {}, [title])
        if self.text and self.text[0].startswith('\n'):
            indent = re.match(r'\n( *)', self.text[0]).group(1)
            heading = f'\n{indent}{heading}\n'
        return [heading, *(self.text or [])]


class FootnoteNode(Node):
    tag = 'p'

    def parse_data(self, data: list[str]) -> Attributes:
        if len(data) != 1:
            raise InvalidData()
        return {'number': data[0]}

    def make_attributes(self) -> Attributes:
        return self.attributes | {'class': [*self.attributes['class'], 'footnote']}

    def make_content(self) -> Optional[list[str]]:
        prefix = html('sup', {}, [self.data['number']])
        return [prefix, *(self.text or [])]


class ListNode(Node):
    @property
    def tag(self) -> str:
        return 'ol' if self.data else 'ul'

    def parse_data(self, data: list[str]) -> Attributes:
        data_dict = {}
        for attr in data:
            if attr.startswith('start='):
                data_dict['start'] = attr.removeprefix('start=')
            elif attr == 'reversed':
                data_dict['reversed'] = True
            else:
                raise InvalidData()
        return data_dict

    def make_content(self) -> Optional[list[str]]:
        # Don't make list items if text is empty
        text = self.text or []
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
            'footnote': FootnoteNode,
            'link': LinkNode,
            'list': ListNode,
            'section': SectionNode,
            'table': TableNode,
        } | {
            node: _make_simple_node(node) for node in SIMPLE_NODES
        }
    }
