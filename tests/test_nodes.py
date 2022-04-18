import pytest
from pytest import raises
from .utils import staticmethods

skip = pytest.mark.skip
xfail = pytest.mark.xfail

from markup.src import nodes

@staticmethods
class Test_SimpleNode:
    pass


@staticmethods
class Test_DescribeNode:
    def test_empty_content_if_no_text_given():
        assert nodes.DescribeNode().make_content() == ['']
        assert nodes.DescribeNode(text=[]).make_content() == ['']

    def test_content_with_only_whitespace_if_only_whitespace_given_in_text():
        assert nodes.DescribeNode(text=['\n\n']).make_content() == ['\n\n']

    def test_term_and_any_number_of_descriptions_separated_by_pipes():
        assert nodes.DescribeNode(text='foo'.split()).make_content() == ['', '<dt>foo</dt>', '']
        assert nodes.DescribeNode(text='foo | bar'.split()).make_content() == ['', '<dt>foo</dt>', '', '', '<dd>bar</dd>', '']
        assert nodes.DescribeNode(text='foo | bar | baz'.split()).make_content() == ['', '<dt>foo</dt>', '', '', '<dd>bar</dd>', '', '', '<dd>baz</dd>', '']

    def test_terms_separated_by_slashes():
        assert nodes.DescribeNode(text='foo / bar / baz'.split()).make_content() == ['', '<dt>foo</dt>', '', '', '<dt>bar</dt>', '', '', '<dt>baz</dt>', '']

        assert nodes.DescribeNode(text='foo | bar / baz | bif'.split()).make_content() == ['', '<dt>foo</dt>', '', '', '<dd>bar</dd>', '', '', '<dt>baz</dt>', '', '', '<dd>bif</dd>', '']

    def test_no_tags_added_if_empty_row():
        assert nodes.DescribeNode(text='foo / / bar'.split()).make_content() == ['', '<dt>foo</dt>', '', '', '', '<dt>bar</dt>', '']


@staticmethods
class Test_LinkNode:
    def test_url_is_put_in_href_attribute():
        assert nodes.LinkNode(data=['foo.bar']).make_attributes() == {'id': None, 'class': [], 'target': None, 'href': 'foo.bar'}

    def test_if_blank_data_arg_is_given_is_put_in_target_attribute():
        assert nodes.LinkNode(data=['_blank', 'foo.bar']).make_attributes() == {'id': None, 'class': [], 'target': '_blank', 'href': 'foo.bar'}

    def test_if_text_is_none_content_is_list_containing_url():
        assert nodes.LinkNode(data=['foo.bar']).make_content() == ['foo.bar']


@staticmethods
class Test_SectionNode:
    def test_id_formed_from_title_if_not_given():
        assert nodes.SectionNode(data=['2', 'Foo']).make_attributes() == {'id': 'sect-foo', 'class': []}
        assert nodes.SectionNode(id='bar', data=['2', 'Foo']).make_attributes() == {'id': 'bar', 'class': []}

    def test_level_must_be_digit_1_to_6():
        with raises(nodes.MarkupError):
            nodes.SectionNode(data=['Foo', 'Bar'])

    def test_if_first_line_of_text_is_blank_indent_of_second_line_applied_to_heading():
        assert nodes.SectionNode(data=['2', 'Foo'], text=['\n   ', 'Bar']).make_content() == ['\n   <h2>Foo</h2>\n', '\n   ', 'Bar']


@staticmethods
class Test_ListNode:
    def test_tag_is_ol_only_if_data_given():
        assert nodes.ListNode().tag == 'ul'
        assert nodes.ListNode(data=['start=6', 'reversed']).tag == 'ol'
        assert nodes.ListNode(id='foo', classes=['bar']).tag == 'ul'

    def test_adds_no_list_items_if_empty_text():
        assert nodes.ListNode().make_content() == []

    def test_adds_one_list_item_if_no_isolated_slash_in_text():
        assert nodes.ListNode(text=['foo/bar']).make_content() == ['<li>foo/bar</li>']
        assert nodes.ListNode(text=['foo / bar']).make_content() == ['<li>foo / bar</li>']
        assert nodes.ListNode(text=['foo', '/', 'bar']).make_content() == ['<li>foo</li>', '<li>bar</li>']

    def test_slash_separates_list_items():
        assert nodes.ListNode(text=['foo', '/', 'bar', '/', 'baz', '/', 'bif']).make_content() == ['<li>foo</li>', '<li>bar</li>', '<li>baz</li>', '<li>bif</li>']

    def test_leading_and_trailing_whitespace_trimmed():
        assert nodes.ListNode(text=[' foo ', '/', ' ', 'bar', ' ']).make_content() == ['<li> foo </li>', '<li>bar</li>']

    def test_leading_and_trailing_whitespace_moved_outside_list_items():
        assert nodes.ListNode(text=['\nfoo\n', '/', '\n', 'bar', '\n']).make_content() == ['<li>\nfoo\n</li>', '\n', '<li>bar</li>', '\n']
