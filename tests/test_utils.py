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

    def test_removes_leading_and_trailing_whitespace_from_sublists():
        strings = [' ', '1', ' ', '2', ' ', '3', ' ']
        assert utils.partition(strings, '2') == [['1'], ['3']]


@staticmethods
class Test_strip:
    def test_removes_leading_and_trailing_whitespace_from_list():
        strings = ['\r  ', 'a', 'b', 'c', '\n\r\t']
        assert utils.strip(strings) == ['a', 'b', 'c']
