import pytest
from pytest import raises
from ..utils import staticmethods

skip = pytest.mark.skip
xfail = pytest.mark.xfail

from markup.src.nodes import table

@staticmethods
class Test_table_node:
    @xfail(reason='Empty tables are not yet handled')
    def test_only_accepts_headers_data_arg():
        assert table.table_node('table', data=['headers=rows']) == '<table></table>'
        with raises(table.InvalidData):
            table.table_node('table', data=['foo'])

    def test_caption_can_be_added_before_table_body_with_double_slash():
        assert table.table_node('table', text=['foo', '//', 'bar']) == '<table><caption>foo</caption><tr><td>bar</td></tr></table>'

    def test_table_rows_separated_by_single_slash():
        assert table.table_node('table', text=['foo', '/', 'bar', '/', 'baz']) == '<table><tr><td>foo</td></tr><tr><td>bar</td></tr><tr><td>baz</td></tr></table>'

    def test_table_cells_separated_by_pipe():
        assert table.table_node('table', text=['foo', '|', 'bar', '|', 'baz']) == '<table><tr><td>foo</td><td>bar</td><td>baz</td></tr></table>'

    def test_rows_must_all_contain_the_same_number_of_cells():
        assert table.table_node('table', text=['foo', '|', 'bar', '/', 'baz', '|', 'bif']) == '<table><tr><td>foo</td><td>bar</td></tr><tr><td>baz</td><td>bif</td></tr></table>'
        with raises(table.MarkupError):
            table.table_node('table', text=['foo', '|', 'bar', '/', 'baz'])

    def test_leading_and_trailing_whitespace_trimmed():
        assert table.table_node('table', text=['  ', 'foo', '   ']) == '<table><tr><td>foo</td></tr></table>'

    def test_leading_and_trailing_whitespace_moved_outside_cells():
        assert table.table_node('table', text=['\n', 'foo', '\r']) == '<table><tr>\n<td>foo</td>\r</tr></table>'

    def test_first_row_is_heading_cells_if_rows_in_header_data_arg():
        assert table.table_node('table', data=['headers=rows'], text=['foo', '|', 'bar', '/', 'baz', '|', 'bif']) == '<table><tr><th>foo</th><th>bar</th></tr><tr><td>baz</td><td>bif</td></tr></table>'

    def test_first_column_is_heading_cells_if_cols_in_header_data_arg():
        assert table.table_node('table', data=['headers=cols'], text=['foo', '|', 'bar', '/', 'baz', '|', 'bif']) == '<table><tr><th>foo</th><td>bar</td></tr><tr><th>baz</th><td>bif</td></tr></table>'

    def test_first_row_and_column_are_heading_cells_if_rows_and_cols_in_header_data_arg():
        assert table.table_node('table', data=['headers=rows,cols'], text=['foo', '|', 'bar', '/', 'baz', '|', 'bif']) == '<table><tr><th>foo</th><th>bar</th></tr><tr><th>baz</th><td>bif</td></tr></table>'

    def test_left_angle_brackets_increase_colspan_of_cell_to_the_left():
        assert table.table_node('table', text=['foo', '|', '<', '|', '<']) == '<table><tr><td colspan=3>foo</td></tr></table>'

    def test_row_cannot_begin_with_left_angle_bracket():
        with raises(table.MarkupError):
            table.table_node('table', text=['<', '|', '<'])

    def test_carets_increase_rowspan_of_cell_above():
        assert table.table_node('table', text=['foo', '/', '^', '/', '^']) == '<table><tr><td rowspan=3>foo</td></tr></table>'

    def test_column_cannot_begin_with_caret():
        with raises(table.MarkupError):
            table.table_node('table', text=['^', '/', '^'])

    def test_carets_under_a_merged_cell_increase_rowspan_of_cell():
        assert table.table_node('table', text=['foo', '|', '<', '|', '<', '/', '^', '|', '^', '|', '^']) == '<table><tr><td rowspan=2 colspan=3>foo</td></tr></table>'

    def test_must_have_correct_number_of_carets_for_merged_cell():
        with raises(table.MarkupError):
            table.table_node('table', text=['foo', '|', '<', '|', '<', '/', '^', '|', '^', '|', 'bar'])

    def test_carets_must_be_aligned_with_start_of_merged_cell():
        with raises(table.MarkupError):
            table.table_node('table', text=['foo', '|', '<', '|', '<', '/', 'bar', '|', '^', '|', '^'])
