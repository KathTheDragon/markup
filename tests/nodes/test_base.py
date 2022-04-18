import pytest
from pytest import raises
from ..utils import staticmethods

skip = pytest.mark.skip
xfail = pytest.mark.xfail

from markup.src.nodes import base

class FooNode(base.Node):
    tag = 'foo'


@staticmethods
class Test_Node:
    def test_puts_id_in_id_attribute():
        assert FooNode(id='foo').attributes == {'id': 'foo', 'class': []}

    def test_puts_classes_in_class_attribute():
        assert FooNode(classes=['foo', 'bar']).attributes == {'id': None, 'class': ['foo', 'bar']}


@staticmethods
class Test_parse_data:
    # Named arguments
    def test_params_ending_with_equals_match_named_arguments():
        data = ['foo=bar', 'baz=bif']
        params = {'foo=': None, 'baz=': None}
        assert base.parse_data(data, params) == {'foo': 'bar', 'baz': 'bif'}

    def test_named_arguments_can_appear_out_of_order():
        data = ['baz=bif', 'foo=bar']
        params = {'foo=': None, 'baz=': None}
        assert base.parse_data(data, params) == {'foo': 'bar', 'baz': 'bif'}

    def test_unused_named_parameters_with_default_values_are_given_default_value():
        data = ['foo=bar']
        params = {'foo=': None, 'baz=': 'bif'}
        assert base.parse_data(data, params) == {'foo': 'bar', 'baz': 'bif'}

    def test_unused_named_parameters_without_default_values_are_an_error():
        data = ['foo=bar']
        params = {'foo=': None, 'baz=': None}
        with raises(base.InvalidData):
            base.parse_data(data, params)

    def test_unknown_named_parameters_are_an_error():
        data = ['bar=foo']
        params = {'foo=': None, 'baz=': None}
        with raises(base.InvalidData):
            base.parse_data(data, params)

    # Boolean arguments
    def test_params_ending_with_question_mark_match_parameter_name():
        data = ['foo', 'bar']
        params = {'foo?': None, 'bar?': None}
        assert base.parse_data(data, params) == {'foo': True, 'bar': True}

    def test_boolean_arguments_can_appear_out_of_order():
        data = ['bar', 'foo']
        params = {'foo?': None, 'bar?': None}
        assert base.parse_data(data, params) == {'foo': True, 'bar': True}

    def test_unused_boolean_parameters_with_default_values_are_given_default_value():
        data = ['foo']
        params = {'foo?': None, 'bar?': False}
        assert base.parse_data(data, params) == {'foo': True, 'bar': False}

    def test_unused_boolean_parameters_without_default_values_are_an_error():
        data = ['foo']
        params = {'foo?': None, 'bar?': None}
        with raises(base.InvalidData):
            base.parse_data(data, params)

    # Positional arguments
    def test_all_other_params_match_next_unmatched_argument():
        params = {'foo': None, 'bar?': None, 'baz=': None, 'bif': None}
        data = ['baz=oof', 'bar', 'rab', 'zab']
        assert base.parse_data(data, params) == {'foo': 'rab', 'bar': True, 'baz': 'oof', 'bif': 'zab'}

    def test_arguments_that_cannot_be_matched_are_an_error():
        params = {'foo': None, 'bar': None}
        data = ['baz', 'bif', 'oof']
        with raises(base.InvalidData):
            base.parse_data(data, params)

    def test_unmatched_positional_parameters_with_default_values_are_given_default_value():
        params = {'foo': None, 'bar': 'bif'}
        data = ['baz']
        assert base.parse_data(data, params) == {'foo': 'baz', 'bar': 'bif'}

    def test_unmatched_positional_parameters_without_default_values_are_an_error():
        params = {'foo': None, 'bar': None}
        data = ['baz']
        with raises(base.InvalidData):
            base.parse_data(data, params)
