import pytest
from pytest import raises
from .utils import staticmethods

skip = pytest.mark.skip
xfail = pytest.mark.xfail

from markup.src import nodes

attrs = {'id': None, 'class': []}

@staticmethods
class Test_handler:
    def test_puts_id_in_id_attribute():
        assert nodes.simple_node('hr', id='foo') == '<hr id="foo" />'

    def test_puts_classes_in_class_attribute():
        assert nodes.simple_node('hr', classes=['foo', 'bar']) == '<hr class="foo bar" />'


@staticmethods
class Test_simple_node:
    def test_raises_InvalidData_if_given_data():
        with raises(nodes.InvalidData):
            nodes.simple_node('hr', data=['foo'])


@staticmethods
class Test_link_node:
    def test_raises_InvalidData_if_not_given_data():
        with raises(nodes.InvalidData):
            nodes.link_node('link')

    def test_raises_InvalidData_if_given_blank_but_not_url():
        with raises(nodes.InvalidData):
            nodes.link_node('link', data=['_blank'])

    def test_raises_InvalidData_if_given_additional_data_arguments():
        with raises(nodes.InvalidData):
            nodes.link_node('link', data=['_blank', 'foo.bar', 'baz'])

    def test_url_is_put_in_href_attribute():
        assert nodes.link_node('link', data=['foo.bar'], text=['foo']) == '<a href="foo.bar">foo</a>'

    def test_if_blank_data_arg_is_given_is_put_in_target_attribute():
        assert nodes.link_node('link', data=['_blank', 'foo.bar'], text=['foo']) == '<a target="_blank" href="foo.bar">foo</a>'

    def test_if_text_is_none_is_set_to_list_containing_url():
        assert nodes.link_node('link', data=['foo.bar']) == '<a href="foo.bar">foo.bar</a>'


@staticmethods
class Test_section_node:
    def test_raises_InvalidData_if_not_given_level_and_title_data_args():
        with raises(nodes.InvalidData):
            nodes.section_node('section')

        with raises(nodes.InvalidData):
            nodes.section_node('section', data=['2'])

    def test_raises_InvalidData_if_given_additional_data_args():
        with raises(nodes.InvalidData):
            nodes.section_node('section', data=['2', 'Foo', 'Bar'])

    def test_id_formed_from_title_if_not_given():
        assert nodes.section_node('section', data=['2', 'Foo']) == '<section id="sect-foo"><h2>Foo</h2></section>'
        assert nodes.section_node('section', id='bar', data=['2', 'Foo']) == '<section id="bar"><h2>Foo</h2></section>'

    def test_level_must_be_digit_1_to_6():
        with raises(nodes.MarkupError):
            nodes.section_node('section', data=['Foo', 'Bar'])

    def test_if_first_line_of_text_is_blank_indent_of_second_line_applied_to_heading():
        assert nodes.section_node('section', data=['2', 'Foo'], text=['\n   ', 'Bar']) == '<section id="sect-foo">\n   <h2>Foo</h2>\n\n   Bar</section>'


@staticmethods
class Test_footnote_node:
    def test_raises_InvalidData_if_not_given_number_data_arg():
        with raises(nodes.InvalidData):
            nodes.footnote_node('footnote')

    def test_raises_InvalidData_if_given_additional_data_args():
        with raises(nodes.InvalidData):
            nodes.footnote_node('footnote', data=['1', 'Foo'])

    def test_footnote_added_to_classes():
        assert nodes.footnote_node('footnote', classes=['foo'], data=['1']) == '<p class="foo footnote"><sup>1</sup></p>'

    def test_sup_tag_inserted_at_start_of_content():
        assert nodes.footnote_node('footnote', data=['1'], text=['Foo']) == '<p class="footnote"><sup>1</sup>Foo</p>'


@staticmethods
class Test_list_node:
    def test_start_data_arg_mapped_to_start_attribute():
        assert nodes.list_node('list', data=['start=3']) == '<ol start="3"></ol>'

    def test_reversed_data_arg_mapped_to_reversed_attribute():
        assert nodes.list_node('list', data=['reversed']) == '<ol reversed></ol>'

    def test_raises_InvalidData_if_any_other_data_arg_given():
        with raises(nodes.InvalidData):
            nodes.list_node('list', data=['foo'])

    def test_tag_is_ol_only_if_data_given():
        assert nodes.list_node('list') == '<ul></ul>'
        assert nodes.list_node('list', data=['start=6', 'reversed']) == '<ol start="6" reversed></ol>'
        assert nodes.list_node('list', id='foo', classes=['bar']) == '<ul id="foo" class="bar"></ul>'

    def test_adds_no_list_items_if_empty_text():
        assert nodes.list_node('list') == '<ul></ul>'

    def test_adds_one_list_item_if_no_isolated_slash_in_text():
        assert nodes.list_node('list', text=['foo/bar']) == '<ul><li>foo/bar</li></ul>'
        assert nodes.list_node('list', text=['foo / bar']) == '<ul><li>foo / bar</li></ul>'
        assert nodes.list_node('list', text=['foo', '/', 'bar']) == '<ul><li>foo</li><li>bar</li></ul>'

    def test_slash_separates_list_items():
        assert nodes.list_node('list', text=['foo', '/', 'bar', '/', 'baz', '/', 'bif']) == '<ul><li>foo</li><li>bar</li><li>baz</li><li>bif</li></ul>'

    def test_leading_and_trailing_whitespace_trimmed():
        assert nodes.list_node('list', text=[' foo ', '/', ' ', 'bar', ' ']) == '<ul><li> foo </li><li>bar</li></ul>'

    def test_leading_and_trailing_whitespace_moved_outside_list_items():
        assert nodes.list_node('list', text=['\nfoo\n', '/', '\n', 'bar', '\n']) == '<ul><li>\nfoo\n</li>\n<li>bar</li>\n</ul>'


@staticmethods
class Test_table_node:
    @xfail(reason='Empty tables are not yet handled')
    def test_only_accepts_headers_data_arg():
        assert nodes.table_node('table', data=['headers=rows']) == '<table></table>'
        with raises(nodes.InvalidData):
            nodes.table_node('table', data=['foo'])

    def test_caption_can_be_added_before_table_body_with_double_slash():
        assert nodes.table_node('table', text=['foo', '//', 'bar']) == '<table><caption>foo</caption><tr><td>bar</td></tr></table>'

    def test_table_rows_separated_by_single_slash():
        assert nodes.table_node('table', text=['foo', '/', 'bar', '/', 'baz']) == '<table><tr><td>foo</td></tr><tr><td>bar</td></tr><tr><td>baz</td></tr></table>'

    def test_table_cells_separated_by_pipe():
        assert nodes.table_node('table', text=['foo', '|', 'bar', '|', 'baz']) == '<table><tr><td>foo</td><td>bar</td><td>baz</td></tr></table>'

    def test_rows_must_all_contain_the_same_number_of_cells():
        assert nodes.table_node('table', text=['foo', '|', 'bar', '/', 'baz', '|', 'bif']) == '<table><tr><td>foo</td><td>bar</td></tr><tr><td>baz</td><td>bif</td></tr></table>'
        with raises(nodes.MarkupError):
            nodes.table_node('table', text=['foo', '|', 'bar', '/', 'baz'])

    def test_leading_and_trailing_whitespace_trimmed():
        assert nodes.table_node('table', text=['  ', 'foo', '   ']) == '<table><tr><td>foo</td></tr></table>'

    def test_leading_and_trailing_whitespace_moved_outside_cells():
        assert nodes.table_node('table', text=['\n', 'foo', '\r']) == '<table><tr>\n<td>foo</td>\r</tr></table>'

    def test_first_row_is_heading_cells_if_rows_in_header_data_arg():
        assert nodes.table_node('table', data=['headers=rows'], text=['foo', '|', 'bar', '/', 'baz', '|', 'bif']) == '<table><tr><th>foo</th><th>bar</th></tr><tr><td>baz</td><td>bif</td></tr></table>'

    def test_first_column_is_heading_cells_if_cols_in_header_data_arg():
        assert nodes.table_node('table', data=['headers=cols'], text=['foo', '|', 'bar', '/', 'baz', '|', 'bif']) == '<table><tr><th>foo</th><td>bar</td></tr><tr><th>baz</th><td>bif</td></tr></table>'

    def test_first_row_and_column_are_heading_cells_if_rows_and_cols_in_header_data_arg():
        assert nodes.table_node('table', data=['headers=rows,cols'], text=['foo', '|', 'bar', '/', 'baz', '|', 'bif']) == '<table><tr><th>foo</th><th>bar</th></tr><tr><th>baz</th><td>bif</td></tr></table>'

    def test_left_angle_brackets_increase_colspan_of_cell_to_the_left():
        assert nodes.table_node('table', text=['foo', '|', '<', '|', '<']) == '<table><tr><td colspan=3>foo</td></tr></table>'

    def test_row_cannot_begin_with_left_angle_bracket():
        with raises(nodes.MarkupError):
            nodes.table_node('table', text=['<', '|', '<'])

    def test_carets_increase_rowspan_of_cell_above():
        assert nodes.table_node('table', text=['foo', '/', '^', '/', '^']) == '<table><tr><td rowspan=3>foo</td></tr></table>'

    def test_column_cannot_begin_with_caret():
        with raises(nodes.MarkupError):
            nodes.table_node('table', text=['^', '/', '^'])

    def test_carets_under_a_merged_cell_increase_rowspan_of_cell():
        assert nodes.table_node('table', text=['foo', '|', '<', '|', '<', '/', '^', '|', '^', '|', '^']) == '<table><tr><td rowspan=2 colspan=3>foo</td></tr></table>'

    def test_must_have_correct_number_of_carets_for_merged_cell():
        with raises(nodes.MarkupError):
            nodes.table_node('table', text=['foo', '|', '<', '|', '<', '/', '^', '|', '^', '|', 'bar'])

    def test_carets_must_be_aligned_with_start_of_merged_cell():
        with raises(nodes.MarkupError):
            nodes.table_node('table', text=['foo', '|', '<', '|', '<', '/', 'bar', '|', '^', '|', '^'])
