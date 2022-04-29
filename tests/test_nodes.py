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
        assert nodes.DescribeNode().make_content([]) == []

    def test_term_and_any_number_of_descriptions_separated_by_pipes():
        assert nodes.DescribeNode().make_content('foo'.split()) == ['<dt>foo</dt>']
        assert nodes.DescribeNode().make_content('foo | bar'.split()) == ['<dt>foo</dt>', '<dd>bar</dd>']
        assert nodes.DescribeNode().make_content('foo | bar | baz'.split()) == ['<dt>foo</dt>', '<dd>bar</dd>', '<dd>baz</dd>']

    def test_terms_separated_by_slashes():
        assert nodes.DescribeNode().make_content('foo / bar / baz'.split()) == ['<dt>foo</dt>', '<dt>bar</dt>', '<dt>baz</dt>']

        assert nodes.DescribeNode().make_content('foo | bar / baz | bif'.split()) == ['<dt>foo</dt>', '<dd>bar</dd>', '<dt>baz</dt>', '<dd>bif</dd>']

    def test_no_tags_added_if_empty_row():
        assert nodes.DescribeNode().make_content('foo / / bar'.split()) == ['<dt>foo</dt>', '<dt>bar</dt>']


@staticmethods
class Test_LinkNode:
    def test_url_is_put_in_href_attribute():
        assert nodes.LinkNode(data={'url': 'foo.bar'}).make_attributes() == {'id': '', 'class': [], 'target': None, 'href': 'foo.bar'}

    def test_if_blank_data_arg_is_True_is_put_in_target_attribute():
        assert nodes.LinkNode(data={'_blank': True, 'url': 'foo.bar'}).make_attributes() == {'id': '', 'class': [], 'target': '_blank', 'href': 'foo.bar'}

    def test_if_text_is_blank_content_is_list_containing_url():
        assert nodes.LinkNode(data={'url': 'foo.bar'}).make_content([]) == ['foo.bar']


@staticmethods
class Test_SectionNode:
    def test_level_must_be_digit_1_to_6():
        with raises(nodes.MarkupError):
            nodes.SectionNode(data={'level': 'foo'})

    def test_title_and_body_separated_by_slash():
        assert nodes.SectionNode(data={'level': '2'}).make_content(['Foo', '/', 'Bar']) == ['<h2>Foo</h2>', '', 'Bar']


@staticmethods
class Test_ListNode:
    def test_tag_is_ol_only_if_data_given():
        assert nodes.ListNode().tag == 'ul'
        assert nodes.ListNode(data={'start': '6', 'reversed': True}).tag == 'ol'

    def test_adds_no_list_items_if_empty_text():
        assert nodes.ListNode().make_content([]) == []

    def test_adds_one_list_item_if_no_isolated_slash_in_text():
        assert nodes.ListNode().make_content(['foo/bar']) == ['<li>foo/bar</li>']
        assert nodes.ListNode().make_content(['foo / bar']) == ['<li>foo / bar</li>']
        assert nodes.ListNode().make_content(['foo', '/', 'bar']) == ['<li>foo</li>', '<li>bar</li>']

    def test_slash_separates_list_items():
        assert nodes.ListNode().make_content(['foo', '/', 'bar', '/', 'baz', '/', 'bif']) == ['<li>foo</li>', '<li>bar</li>', '<li>baz</li>', '<li>bif</li>']
