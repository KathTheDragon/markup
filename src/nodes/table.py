from functools import reduce
from .base import MarkupError, InvalidData, Node
from ..html import Attributes, html
from ..utils import partition

class TableNode(Node):
    tag = 'table'
    params = {'headers=': ''}

    def make_data(self, data: Attributes) -> Attributes:
        data['headers'] = list(filter(None, data['headers'].split(',')))
        if not (set(data['headers']) <= {'rows', 'cols'}):
            raise InvalidData('headers can only contain \'rows\' and \'cols\'')
        return data

    def make_content(self, text: list[str]) -> list[str]:
        rows = []

        if '//' in text:
            caption, text = partition(text, '//')
            rows.append(html('caption', {}, caption))

        table = [partition(row, '|') for row in partition(text, '/')]
        if len(set(map(len, table))) != 1:
            raise MarkupError('Table rows must be the same size')
        for num, row in enumerate(_merge_table(table)):
            rows.extend(_make_tr(row, headers=set(self.data['headers']), row_num=num))
        return rows


def _merge_table(table: list[list[list[str]]]) -> list[list[dict]]:
    return reduce(_merge_up, map(lambda row: reduce(_merge_left, row, []), table), [])


def _merge_left(row: list[dict], cell: list[str]) -> list[dict]:
    if cell == ['<']:
        if not row or row[-1]['data'] == ['^']:
            raise MarkupError('Invalid cell merge')
        row[-1]['cols'] += 1
    elif cell == ['.']:
        if not row or row[-1]['data'] != ['^']:
            raise MarkupError('Invalid cell merge')
        row[-1]['cols'] += 1
    else:
        row.append({'data': cell, 'rows': 1, 'cols': 1})

    return row


def _merge_up(table: list[list[dict]], row: list[dict]) -> list[list[dict]]:
    col = 0
    for cell in row:
        if cell['data'] == ['^']:
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
                if tcell['data'] != ['^']:
                    if tcell['cols'] == cell['cols']:
                        tcell['rows'] += 1
                        break
                    else:
                        raise MarkupError('Misaligned table cell')
        col += cell['cols']

    table.append(row)
    return table


def _make_tr(row: list[dict], *, headers: set[str], row_num: int) -> list[str]:
    cells = []
    for num, cell in enumerate(row):
        cells.extend(_make_td(cell, headers=headers, row_num=row_num, col_num=num))
    if cells:
        return [html('tr', {}, cells)]
    else:
        return []


def _make_td(cell: dict, *, headers: set[str], row_num: int, col_num: int) -> list[str]:
    if cell['data'] != ['^']:
        tag = 'th' if ('cols' in headers and not row_num or 'rows' in headers and not col_num) else 'td'
        attributes = {}
        if cell['rows'] != 1:
            attributes['rowspan'] = str(cell['rows'])
        if cell['cols'] != 1:
            attributes['colspan'] = str(cell['cols'])
        return [html(tag, attributes, cell['data'])]
    else:
        return []
