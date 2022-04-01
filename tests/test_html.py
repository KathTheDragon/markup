import pytest
from pytest import raises
from .utils import staticmethods

skip = pytest.mark.skip
xfail = pytest.mark.xfail

from markup.src import html

@staticmethods
class Test_html:
    def test_self_closing_opening_tag_when_content_is_None():
        assert html.html('hr', {}, None) == '<hr />'
        assert html.html('hr', {'class': ['divider']}, None) == '<hr class="divider" />'

    def test_joins_content_list_when_not_None():
        assert html.html('p', {}, ['foo', 'bar', ' ', 'and', ' ', 'baz']) == '<p>foobar and baz</p>'


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
