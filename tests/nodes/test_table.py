import pytest
from pytest import raises
from ..utils import staticmethods

skip = pytest.mark.skip
xfail = pytest.mark.xfail

from markup.src.nodes import table

@staticmethods
class Test_TableNode:
    def test_headers_data_arg_can_only_have_rows_and_cols():
        with raises(table.InvalidData):
            table.TableNode(data=['headers=foo'])

    def test_caption_can_be_added_before_table_body_with_double_slash():
        assert table.TableNode(text=['foo', '//', 'bar']).make_content() == ['', '<caption>foo</caption>', '', '<tr><td>bar</td></tr>']

    def test_leading_and_trailing_whitespace_around_caption_placed_outside_tag():
        assert table.TableNode(text=['  \n  ', 'foo', '\t\r\t', '//', 'bar']).make_content() == ['\n  ', '<caption>foo</caption>', '\r\t', '<tr><td>bar</td></tr>']

    def test_table_rows_separated_by_single_slash():
        assert table.TableNode(text=['foo', '/', 'bar', '/', 'baz']).make_content() == ['<tr><td>foo</td></tr>', '<tr><td>bar</td></tr>', '<tr><td>baz</td></tr>']

    def test_table_cells_separated_by_pipe():
        assert table.TableNode(text=['foo', '|', 'bar', '|', 'baz']).make_content() == ['<tr><td>foo</td><td>bar</td><td>baz</td></tr>']

    def test_rows_must_all_contain_the_same_number_of_cells():
        assert table.TableNode(text=['foo', '|', 'bar', '/', 'baz', '|', 'bif']).make_content() == ['<tr><td>foo</td><td>bar</td></tr>', '<tr><td>baz</td><td>bif</td></tr>']
        with raises(table.MarkupError):
            table.TableNode(text=['foo', '|', 'bar', '/', 'baz']).make_content()

    def test_leading_and_trailing_whitespace_trimmed():
        assert table.TableNode(text=['  ', 'foo', '   ']).make_content() == ['<tr><td>foo</td></tr>']

    def test_leading_and_trailing_whitespace_moved_outside_cells():
        assert table.TableNode(text=['\n', 'foo', '\r']).make_content() == ['<tr>\n<td>foo</td>\r</tr>']

    def test_first_row_is_heading_cells_if_cols_in_header_data_arg():
        assert table.TableNode(data=['headers=cols'], text=['foo', '|', 'bar', '/', 'baz', '|', 'bif']).make_content() == ['<tr><th>foo</th><th>bar</th></tr>', '<tr><td>baz</td><td>bif</td></tr>']

    def test_first_column_is_heading_cells_if_rows_in_header_data_arg():
        assert table.TableNode(data=['headers=rows'], text=['foo', '|', 'bar', '/', 'baz', '|', 'bif']).make_content() == ['<tr><th>foo</th><td>bar</td></tr>', '<tr><th>baz</th><td>bif</td></tr>']

    def test_first_row_and_column_are_heading_cells_if_rows_and_cols_in_header_data_arg():
        assert table.TableNode(data=['headers=rows,cols'], text=['foo', '|', 'bar', '/', 'baz', '|', 'bif']).make_content() == ['<tr><th>foo</th><th>bar</th></tr>', '<tr><th>baz</th><td>bif</td></tr>']


@staticmethods
class Test_merge_left:
    def test_left_arrow_cannot_be_merged_into_empty_row():
        with raises(table.MarkupError):
            table._merge_left([], ('', ['<'], ''))

    def test_left_arrow_cannot_be_merged_after_up_arrow():
        row = table._merge_left([], ('', ['^'], ''))
        with raises(table.MarkupError):
            table._merge_left(row, ('', ['<'], ''))

    def test_left_arrow_increments_colspan_of_last_merged_cell():
        row = [
            {'data': ('', ['foo'], ''), 'cols': 1, 'rows': 1},
            {'data': ('', ['bar'], ''), 'cols': 3, 'rows': 1},
        ]
        assert table._merge_left(row, ('', ['<'], '')) == [
            {'data': ('', ['foo'], ''), 'cols': 1, 'rows': 1},
            {'data': ('', ['bar'], ''), 'cols': 4, 'rows': 1},
        ]

    def test_dot_cannot_be_merged_into_empty_row():
        with raises(table.MarkupError):
            table._merge_left([], ('', ['.'], ''))

    def test_dot_cannot_be_merged_after_text():
        row = table._merge_left([], ('', ['foo'], ''))
        with raises(table.MarkupError):
            table._merge_left(row, ('', ['.'], ''))

        row = table._merge_left(row, ('', ['<'], ''))
        with raises(table.MarkupError):
            table._merge_left(row, ('', ['.'], ''))

    def test_dot_increments_colspan_of_last_merged_caret():
        row = [
            {'data': ('', ['^'], ''), 'cols': 1, 'rows': 1},
            {'data': ('', ['^'], ''), 'cols': 3, 'rows': 1},
        ]
        assert table._merge_left(row, ('', ['.'], '')) == [
            {'data': ('', ['^'], ''), 'cols': 1, 'rows': 1},
            {'data': ('', ['^'], ''), 'cols': 4, 'rows': 1},
        ]

    def test_text_always_merged():
        assert table._merge_left([], ('', ['foo'], '')) == [
            {'data': ('', ['foo'], ''), 'cols': 1, 'rows': 1},
        ]
        row = [
            {'data': ('', ['foo'], ''), 'cols': 1, 'rows': 1},
            {'data': ('', ['bar'], ''), 'cols': 3, 'rows': 1},
        ]
        assert table._merge_left(row, ('', ['baz'], '')) == [
            {'data': ('', ['foo'], ''), 'cols': 1, 'rows': 1},
            {'data': ('', ['bar'], ''), 'cols': 3, 'rows': 1},
            {'data': ('', ['baz'], ''), 'cols': 1, 'rows': 1},
        ]


def _make_row(row: str) -> list[dict]:
    from functools import reduce
    from markup.src.utils import partition, strip

    return reduce(table._merge_left, [strip([cell]) for cell in row.split()], [])


@staticmethods
class Test_merge_up:
    def test_row_with_carets_cannot_be_merged_into_empty_table():
        row = _make_row('foo < ^ . . bar')
        with raises(table.MarkupError):
            table._merge_up([], row)

    def test_caret_must_be_aligned_with_some_cell_in_last_row_of_table():
        table_ = [
            _make_row('foo < bar < < baz'),
        ]

        row = _make_row('foo ^ bar < < <')
        with raises(table.MarkupError):
            table._merge_up(table_, row)

        row = _make_row('foo < ^ bar < <')
        with raises(table.MarkupError):
            table._merge_up(table_, row)

        row = _make_row('foo < ^ . . bar')
        _row_1 = _make_row('foo < bar < < baz')
        _row_1[1]['rows'] = 2
        assert table._merge_up(table_, row) == [
            _row_1,
            _make_row('foo < ^ . . bar'),
        ]

    def test_caret_increases_rowspan_of_lowest_aligned_non_caret_cell():
        table_ = [
            _make_row('foo < bar < < baz'),
            _make_row('foo < bar < < baz'),
            _make_row('foo < bar < < baz'),
        ]
        row = _make_row('foo < ^ . . bar')
        _row_3 = _make_row('foo < bar < < baz')
        _row_3[1]['rows'] = 2
        assert table._merge_up(table_, row) == [
            _make_row('foo < bar < < baz'),
            _make_row('foo < bar < < baz'),
            _row_3,
            _make_row('foo < ^ . . bar'),
        ]


@staticmethods
class Test_make_tr:
    def test_returns_empty_string_if_row_contains_no_content_cells():
        row = _make_row('^ . . ^ . ^ ^ ^ .')
        assert table._make_tr(row, headers=set(), row_num=1) == ''

    def test_returns_tr_tag_otherwise():
        row = _make_row('foo bar baz')
        assert table._make_tr(row, headers=set(), row_num=0) == '<tr><td>foo</td><td>bar</td><td>baz</td></tr>'


@staticmethods
class Test_make_td:
    def test_returns_empty_list_if_cell_is_caret():
        cell = {'data': ('', ['^'], ''), 'rows': 1, 'cols': 1}
        assert table._make_td(cell, headers=set(), row_num=1, col_num=1) == []

    def test_tag_is_th_if_row_0_and_cols_in_headers():
        cell = {'data': ('', ['foo'], ''), 'rows': 1, 'cols': 1}
        assert table._make_td(cell, headers={'cols'}, row_num=0, col_num=1) == ['', '<th>foo</th>', '']

    def test_tag_is_th_if_col_0_and_rows_in_headers():
        cell = {'data': ('', ['foo'], ''), 'rows': 1, 'cols': 1}
        assert table._make_td(cell, headers={'rows'}, row_num=1, col_num=0) == ['', '<th>foo</th>', '']

    def test_tag_has_rowspan_attribute_if_cell_spans_more_than_1_row():
        cell = {'data': ('', ['foo'], ''), 'rows': 3, 'cols': 1}
        assert table._make_td(cell, headers=set(), row_num=1, col_num=1) == ['', '<td rowspan="3">foo</td>', '']

    def test_tag_has_colspan_attribute_if_cell_spans_more_than_1_row():
        cell = {'data': ('', ['foo'], ''), 'rows': 1, 'cols': 2}
        assert table._make_td(cell, headers=set(), row_num=1, col_num=1) == ['', '<td colspan="2">foo</td>', '']

    def test_leading_and_trailing_whitespace_placed_outside_tag():
        cell = {'data': ('\n  ', ['foo'], '\r\t'), 'rows': 1, 'cols': 1}
        assert table._make_td(cell, headers=set(), row_num=1, col_num=1) == ['\n  ', '<td>foo</td>', '\r\t']
