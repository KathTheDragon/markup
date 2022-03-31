import pytest
from pytest import raises
from .utils import staticmethods

skip = pytest.mark.skip
xfail = pytest.mark.xfail

from markup.src import utils

@staticmethods
class Test_partition:
    def test_splits_a_list_into_sublists_by_a_certain_element():
        strings = ['1', '2', '3', '2', '4', '5', '2', '6']
        assert utils.partition(strings, '2') == [
            ['1'], ['3'], ['4', '5'], ['6']
        ]

    def test_returns_the_original_list_in_the_outer_list_if_separator_does_not_occur():
        strings = ['1', '2', '3', '2', '4', '5', '2', '6']
        assert utils.partition(strings, 'a') == [strings]

        assert utils.partition([], 'a') == [[]]


@staticmethods
class Test_strip:
    def test_separates_leading_and_trailing_whitespace_from_list():
        strings = ['  ', 'a', 'b', 'c', '\n\r\t']
        assert utils.strip(strings) == ('  ', ['a', 'b', 'c'], '\n\r\t')

    def test_returns_empty_strings_if_no_leading_or_trailing_whitespace():
        strings = ['a', 'b', 'c', ' ']
        assert utils.strip(strings) == ('', ['a', 'b', 'c'], ' ')

        strings = [' ', 'a', 'b', 'c']
        assert utils.strip(strings) == (' ', ['a', 'b', 'c'], '')

        strings = ['a', 'b', 'c']
        assert utils.strip(strings) == ('', ['a', 'b', 'c'], '')

    def test_assumes_leading_whitespace():
        strings = [' ']
        assert utils.strip(strings) == (' ', [], '')
