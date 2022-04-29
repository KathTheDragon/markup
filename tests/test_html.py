import pytest
from pytest import raises
from .utils import staticmethods

skip = pytest.mark.skip
xfail = pytest.mark.xfail

from markup.src import html

@staticmethods
class Test_html:
    def test_formats_attributes_into_open_tag():
        assert html.html('hr', {'foo': 'bar'}, []) == '<hr foo="bar" />'
        assert html.html('div', {'foo': 'bar'}, []) == '<div foo="bar">\n    \n</div>'
        assert html.html('p', {'foo': 'bar'}, []) == '<p foo="bar"></p>'

    def test_self_closing_opening_tag_when_tag_is_void_tag():
        assert html.html('hr', {}, []) == '<hr />'
        assert html.html('hr', {}, ['foo', 'bar']) == '<hr />'

    def test_places_each_content_item_on_new_line_with_indent_if_tag_is_block_tag():
        assert html.html('div', {}, ['foo', 'bar']) == '<div>\n    foo\n    bar\n</div>'

    def test_joins_content_list_with_spaces_if_tag_is_not_void_or_block_tag():
        assert html.html('p', {}, ['foo', 'bar', 'and', 'baz']) == '<p>foo bar and baz</p>'


@staticmethods
class Test_format_attributes:
    def test_True_values_become_boolean_attributes():
        assert html.format_attributes({'foo': True}) == 'foo'

    def test_falsy_values_are_omitted():
        assert html.format_attributes({'foo': False, 'bar': None, 'baz': '', 'bif': []}) == ''

    def test_string_values_become_attribute_values():
        assert html.format_attributes({'foo': 'bar'}) == 'foo="bar"'

    def test_list_values_are_separated_by_a_space_in_attribute_value():
        assert html.format_attributes({'foo': ['bar', 'baz', 'bif']}) == 'foo="bar baz bif"'

    def test_attributes_are_separated_by_a_space():
        assert html.format_attributes({'foo': True, 'bar': 'baz', 'bif': True}) == 'foo bar="baz" bif'


@staticmethods
class Test_indent:
    def test_adds_four_times_depth_spaces_to_the_start_of_each_line():
        input = 'foo\nbar\nbaz'
        output = '        foo\n        bar\n        baz'
        assert html.indent(input, depth=2) == output
