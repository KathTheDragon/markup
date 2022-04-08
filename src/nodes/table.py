from functools import reduce
from .handler import handler, _HandlerReturn
from .exceptions import MarkupError, InvalidData
from ..html import Attributes, html
from ..utils import partition, strip

@handler
def table_node(command: str, attributes: Attributes, data: list[str], text: list[str] | None) -> _HandlerReturn:
    headers = []
    for attr in data:
        if attr.startswith('headers='):
            headers = set(attr.removeprefix('headers=').split(','))
            if not (headers <= {'rows', 'cols'}):
                raise InvalidData()
        else:
            raise InvalidData()

    text = text or []
    rows = []

    if '//' in text:
        caption, text = partition(text, '//')
        rows.append(html('caption', {}, caption))

    table = [[strip(cell) for cell in partition(row, '|')] for row in partition(text, '/')]
    if len(set(map(len, table))) != 1:
        raise MarkupError('Table rows must be the same size')
    for num, row in enumerate(_merge_table(table)):
        rows.append(_make_tr(row, headers=headers, row_num=num))
    return 'table', attributes, rows


def _merge_table(table: list[list[tuple[str, list[str], str]]]) -> list[list[dict]]:
    return reduce(_merge_up, map(lambda row: reduce(_merge_left, row, []), table), [])


def _merge_left(row: list[dict], cell: tuple[str, list[str], str]) -> list[dict]:
    if cell[1] == ['<']:
        if not row or row[-1]['data'] is None:
            raise MarkupError('Invalid cell merge')
        row[-1]['cols'] += 1
    elif cell[1] == ['^']:
        row.append({'data': None, 'rows': 1, 'cols': 1})
    elif cell[1] == ['.']:
        if not row or row[-1]['data'] is not None:
            raise MarkupError('Invalid cell merge')
        row[-1]['cols'] += 1
    else:
        row.append({'data': cell, 'rows': 1, 'cols': 1})

    return row


def _merge_up(table: list[list[dict]], row: list[dict]) -> list[list[dict]]:
    col = 0
    for cell in row:
        if cell['data'] is None:
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
                if tcell['data'] is not None:
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
    if cell['data'] is not None:
        tag = 'th' if ('rows' in headers and not row_num or 'cols' in headers and not col_num) else 'td'
        attributes = {}
        if cell['rows'] != 1:
            attributes['rowspan'] = str(cell['rows'])
        if cell['cols'] != 1:
            attributes['colspan'] = str(cell['cols'])
        leading, content, trailing = cell['data']
        return [leading, html(tag, attributes, content), trailing]
    else:
        return []
