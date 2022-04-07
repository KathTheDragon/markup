from .handler import handler, _HandlerReturn
from .exceptions import MarkupError, InvalidData
from ..html import Attributes, html
from ..utils import partition, strip

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

    text = text or []
    rows = []

    if '//' in text:
        caption, text = partition(text, '//')
        rows.append(html('caption', {}, caption))

    table = [[strip(cell) for cell in partition(row, '|')] for row in partition(text, '/')]
    if len(set(map(len, table))) != 1:
        raise MarkupError('Table rows must be the same size')
    for mrow in _merge_table(table):
        row = []
        for mcell in mrow:
            if mcell['data'] is not None:
                tag = 'th' if (header_row and not rows or header_col and not row) else 'td'
                leading, cell, trailing = mcell['data']
                cell_attributes = {}
                if mcell['rows'] != 1:
                    cell_attributes['rowspan'] = str(mcell['rows'])
                if mcell['cols'] != 1:
                    cell_attributes['colspan'] = str(mcell['cols'])
                row.extend([leading, html(tag, cell_attributes, cell), trailing])
        if row:
            rows.append(html('tr', {}, row))
    return 'table', attributes, rows


def _merge_table(table: list[list[tuple[str, list[str], str]]]) -> list[list[dict]]:
    merged = []
    for row in table:
        merged = _merge_up(merged, _merge_row(row))
    return merged


def _merge_row(row: list[tuple[str, list[str], str]]) -> list[dict]:
    merged_row = []
    for cell in row:
        merged_row = _merge_left(merged_row, cell)
    return merged_row


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
