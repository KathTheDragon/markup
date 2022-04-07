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
        merged_row = []
        for leading, cell, trailing in row:
            if cell == ['<']:
                if not merged_row or merged_row[-1]['data'] == ('', ['^'], ''):
                    raise MarkupError('Invalid cell merge')
                merged_row[-1]['cols'] += 1
            elif cell == ['^']:
                merged_row.append({'data': ('', ['^'], ''), 'rows': 1, 'cols': 1})
            elif cell == ['.']:
                if not merged_row or merged_row[-1]['data'] != ('', ['^'], ''):
                    raise MarkupError('Invalid cell merge')
                merged_row[-1]['cols'] += 1
            else:
                merged_row.append({'data': (leading, cell, trailing), 'rows': 1, 'cols': 1})

        col = 0
        for cell in merged_row:
            if cell['data'] == ('', ['^'], ''):
                if not merged:
                    raise MarkupError('Invalid cell merge')
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
                        if mcell['cols'] == cell['cols']:
                            mcell['rows'] += 1
                            cell['data'] = None
                            break
                        else:
                            raise MarkupError('Misaligned table cell')
            col += cell['cols']

        merged.append(merged_row)
    return merged
