import pytest
from pytest import raises
from ..utils import staticmethods

skip = pytest.mark.skip
xfail = pytest.mark.xfail

from markup.src import nodes

@staticmethods
class Test_handler:
    def test_puts_id_in_id_attribute():
        assert nodes._make_simple_node('hr')(id='foo') == '<hr id="foo" />'

    def test_puts_classes_in_class_attribute():
        assert nodes._make_simple_node('hr')(classes=['foo', 'bar']) == '<hr class="foo bar" />'
