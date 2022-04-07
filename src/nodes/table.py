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

    parts = partition(text or [], '//')
    if len(parts) == 1:
        caption, text = None, parts[0]
    else:
        caption, text = parts

    table = [[strip(cell) for cell in partition(row, '|')] for row in partition(text, '/')]
    if len(set(map(len, table))) != 1:
        raise MarkupError('Table rows must be the same size')
    merged = _merge_table(table)
    rows = []
    if caption is not None:
        rows.append(html('caption', {}, caption))
    for mrow in merged:
        row = []
        for mcell in mrow:
            if mcell['data'] is not None:
                tag = 'th' if (header_row and not rows or header_col and not row) else 'td'
                leading, cell, trailing = mcell['data']
                attributes = {}
                if mcell['rows'] != 1:
                    attributes['rowspan'] = str(mcell['rows'])
                if mcell['cols'] != 1:
                    attributes['colspan'] = str(mcell['cols'])
                row.extend([leading, html(tag, attributes, cell), trailing])
        if row:
            rows.append(html('tr', {}, row))
    return 'table', attributes, rows


def _merge_table(table: list[list[tuple[str, list[str], str]]]) -> list[list[dict]]:
    merged = []
    for row in table:
        col = 0
        merged_row = []
        for leading, cell, trailing in row:
            if cell == ['<']:
                if not merged_row:
                    raise MarkupError('Invalid cell merge')
                merged_row[-1]['cols'] += 1
            elif cell == ['^']:
                if merged_row and merged_row[-1]['data'] == ('', ['^'], ''):
                    merged_row[-1]['cols'] += 1
                else:
                    if merged_row:
                        col += merged_row[-1]['cols']
                    merged_row.append({'data': ('', ['^'], ''), 'rows': 1, 'cols': 1})
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
                        if mcell['cols'] == merged_row[-1]['cols']:
                            mcell['rows'] += 1
                            merged_row[-1]['data'] = None
                            break
                        else:
                            raise MarkupError('Misaligned table cell')
            else:
                if merged_row:
                    col += merged_row[-1]['cols']
                merged_row.append({'data': (leading, cell, trailing), 'rows': 1, 'cols': 1})
        if any(cell['data'] == ('', ['^'], '') for cell in merged_row):
            raise MarkupError('Invalid cell merge')
        merged.append(merged_row)
    return merged
