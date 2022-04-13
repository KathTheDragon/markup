import pytest
from pytest import raises
from .utils import staticmethods

skip = pytest.mark.skip
xfail = pytest.mark.xfail

from markup.src import html, nodes, parse

class TestNode(nodes.Node):
    @staticmethod
    def process(attributes: html.Attributes, data: list[str], text: list[str] | None) -> nodes.HTML:
        attributes['data'] = data
        return 'test', attributes, text


class ErrorNode(nodes.Node):
    @staticmethod
    def process(attributes: html.Attributes, data: list[str], text: list[str] | None) -> nodes.HTML:
        raise nodes.MarkupError('This always errors')


markup = parse.Markup()
markup.nodes['$']['test'] = TestNode
markup.nodes['$']['error'] = ErrorNode

error_msg = '<span class="error">&lt;{}&gt;</span>'


@staticmethods
class Test_Markup_parse:
    pass


@staticmethods
class Test_Markup_parse_string:
    def test_accepts_any_character_without_alphabet_or_exclude():
        assert markup.parse_string('abc') == ('abc', '')

    def test_only_accepts_characters_in_alphabet_if_given():
        assert markup.parse_string('abc', alphabet='ab') == ('ab', 'c')

    def test_does_not_accept_characters_in_exclude():
        assert markup.parse_string('abc', exclude='c') == ('ab', 'c')
        assert markup.parse_string('abc', alphabet='abc', exclude='c') == ('ab', 'c')

    def test_allows_escaped_characters_if_backslash_accepted():
        assert markup.parse_string('a\\nb') == ('a\\nb', '')
        assert markup.parse_string('a\\nb', exclude='\\') == ('a', '\\nb')

    def test_raises_ParseError_if_string_ends_after_backslash():
        with raises(parse.ParseError):
            markup.parse_string('\\')

    def test_allows_embedded_nodes_if_node_prefix_accepted():
        assert markup.parse_string('a $test b') == ('a <test /> b', '')
        assert markup.parse_string('a $test b', exclude='$') == ('a ', '$test b')

    def test_raises_ParseError_if_nothing_parsed_and_error_message_given():
        with raises(parse.ParseError, match='^Foo$'):
            markup.parse_string('abc', exclude='a', error_msg='Foo')

        markup.parse_string('abc', exclude='a') == ('', 'abc')


@staticmethods
class Test_Markup_parse_node:
    def test_raises_ParseError_if_prefix_is_not_followed_by_valid_character():
        with raises(parse.ParseError):
            markup.parse_node('$ ')

    def test_raises_ParseError_if_hash_is_not_followed_by_valid_character():
        with raises(parse.ParseError):
            markup.parse_node('$test# ')

    def test_raises_ParseError_if_dot_is_not_followed_by_valid_character():
        with raises(parse.ParseError):
            markup.parse_node('$test. ')

    def test_multiple_ids_are_not_accepted():
        assert markup.parse_node('$test#foo#bar') == ('<test id="foo" />', '#bar')

    def test_multiple_classes_are_accepted():
        assert markup.parse_node('$test.foo.bar') == ('<test class="foo bar" />', '')

    def test_data_ignores_whitespace():
        assert markup.parse_node('$test[foo\n\n\nbar]') == ('<test data="foo bar" />', '')

    def test_data_doesnt_allow_embedded_nodes():
        with raises(parse.ParseError):
            markup.parse_node('$test[foo $test bar]')

    def test_text_preserves_whitespace():
        assert markup.parse_node('$test{foo\n\n\nbar}') == ('<test>foo\n\n\nbar</test>', '')

    def test_text_allows_embedded_nodes():
        assert markup.parse_node('$test{foo $test bar}') == ('<test>foo <test /> bar</test>', '')

    def test_returns_error_span_if_unknown_node():
        assert markup.parse_node('$foo') == (error_msg.format('Invalid node: $foo'), '')

    def test_returns_error_span_if_handler_errors():
        assert markup.parse_node('$error') == (error_msg.format('This always errors'), '')


@staticmethods
class Test_Markup_parse_list:
    def test_accepts_characters_until_end_character():
        assert markup.parse_list('abc]def', end=']') == (['abc'], ']def')

    def test_groups_continguous_whitespace():
        assert markup.parse_list(' \r\n\t\v') == ([' \r\n\t\v'], '')

    def test_groups_quoted_characters():
        assert markup.parse_list('"a b\nc"') == (['a b\nc'], '')

    def test_doesnt_stop_at_end_character_inside_quotes():
        assert markup.parse_list('"a]b"', end=']') == (['a]b'], '')

    def test_groups_contiguous_non_whitespace():
        assert markup.parse_list('abc') == (['abc'], '')

    def test_separates_whitespace_from_non_whitespace():
        assert markup.parse_list('a b c') == (['a', ' ', 'b', ' ', 'c'], '')

    def test_skips_whitespace_with_skip_whitespace_True():
        assert markup.parse_list('a b c', skip_whitespace=True) == (['a', 'b', 'c'], '')

    def test_disallows_escaping_if_backslash_excluded():
        assert markup.parse_list('a\\nb') == (['a\\nb'], '')
        with raises(parse.ParseError):
            markup.parse_list('a\\nb', exclude='\\')

    def test_disallows_embedding_if_prefix_characters_excluded():
        assert markup.parse_list('$test') == (['<test />'], '')

        with raises(parse.ParseError):
            markup.parse_list('$test', exclude='$')
