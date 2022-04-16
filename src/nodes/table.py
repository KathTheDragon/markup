from functools import reduce
from typing import Optional
from .base import Node
from .exceptions import MarkupError, InvalidData
from ..html import Attributes, html
from ..utils import partition, strip

class TableNode(Node):
    tag = 'table'
    params = ('headers=',)

    def parse_data(self, data: list[str]) -> Attributes:
        data_dict = super().parse_data(data)
        data_dict['headers'] = list(filter(None, data_dict.get('headers', '').split(',')))
        if not (set(data_dict['headers']) <= {'rows', 'cols'}):
            raise InvalidData()
        return data_dict

    def make_content(self) -> Optional[list[str]]:
        text = self.text or []
        rows = []

        if '//' in text:
            caption, text = partition(text, '//')
            leading, caption, trailing = strip(caption)
            rows.extend([leading, html('caption', {}, caption), trailing])

        table = [[strip(cell) for cell in partition(row, '|')] for row in partition(text, '/')]
        if len(set(map(len, table))) != 1:
            raise MarkupError('Table rows must be the same size')
        for num, row in enumerate(_merge_table(table)):
            rows.append(_make_tr(row, headers=set(self.data['headers']), row_num=num))
        return rows


def _merge_table(table: list[list[tuple[str, list[str], str]]]) -> list[list[dict]]:
    return reduce(_merge_up, map(lambda row: reduce(_merge_left, row, []), table), [])


def _merge_left(row: list[dict], cell: tuple[str, list[str], str]) -> list[dict]:
    if cell[1] == ['<']:
        if not row or row[-1]['data'][1] == ['^']:
            raise MarkupError('Invalid cell merge')
        row[-1]['cols'] += 1
    elif cell[1] == ['.']:
        if not row or row[-1]['data'][1] != ['^']:
            raise MarkupError('Invalid cell merge')
        row[-1]['cols'] += 1
    else:
        row.append({'data': cell, 'rows': 1, 'cols': 1})

    return row


def _merge_up(table: list[list[dict]], row: list[dict]) -> list[list[dict]]:
    col = 0
    for cell in row:
        if cell['data'][1] == ['^']:
            if not table:
                raise MarkupError('Invalid cell merge')
            for trow in reversed(table):
                tcol = 0
                for tcell in trow:
                    if tcol == col:
                        break
                    elif tcol > col:
                        raise MarkupError('Misaligned table cell')
                    else:
                        tcol += tcell['cols']
                if tcell['data'][1] != ['^']:
                    if tcell['cols'] == cell['cols']:
                        tcell['rows'] += 1
                        break
                    else:
                        raise MarkupError('Misaligned table cell')
        col += cell['cols']

    table.append(row)
    return table


def _make_tr(row: list[dict], *, headers: set[str], row_num: int) -> str:
    cells = []
    for num, cell in enumerate(row):
        cells.extend(_make_td(cell, headers=headers, row_num=row_num, col_num=num))
    if cells:
        return html('tr', {}, cells)
    else:
        return ''


def _make_td(cell: dict, *, headers: set[str], row_num: int, col_num: int) -> list[str]:
    if cell['data'][1] != ['^']:
        tag = 'th' if ('cols' in headers and not row_num or 'rows' in headers and not col_num) else 'td'
        attributes = {}
        if cell['rows'] != 1:
            attributes['rowspan'] = str(cell['rows'])
        if cell['cols'] != 1:
            attributes['colspan'] = str(cell['cols'])
        leading, content, trailing = cell['data']
        return [leading, html(tag, attributes, content), trailing]
    else:
        return []
