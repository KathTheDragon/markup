import string
from typing import Optional
from . import nodes
from .html import indent

class ParseError(Exception):
    def __init__(self, message: str, remainder: str) -> str:
        self.message = message
        self.remainder = remainder
        super().__init__(message)


STRING_CHARS = string.ascii_letters + string.digits + '_-'

def error(msg: str) -> str:
    return f'<span class="error">&lt;{msg}&gt;</span>'


def is_valid_char(char: str, alphabet: str, exclude: str) -> bool:
    return (not alphabet or char in alphabet) and char not in exclude


def unescape(string: str) -> str:
    import re
    escapes = {
        'n': '\n',
    }
    return re.sub(r'\\(.)', lambda m: escapes.get(m[1], m[1]), string, flags=re.S)


class Markup:
    def __init__(self) -> None:
        self.nodes = nodes.make_nodes()

    @property
    def prefixes(self) -> string:
        return ''.join(self.nodes)

    def parse(self, string: str, *, depth: int=0, **kwargs) -> str:
        try:
            output, _ = self.parse_string(string, **kwargs)
            return unescape(indent(output, depth=depth))
        except ParseError as e:
            return error(e.message)

    def parse_string(self, value: str, *, alphabet: str='', exclude: str='', error_msg: str='', **kwargs) -> tuple[str, str]:
        out = ''
        while value and is_valid_char(value[0], alphabet, exclude):
            if value[0] == '\\':
                if len(value) <= 1:
                    raise ParseError('Incomplete escape sequence', value)
                else:
                    out += value[:2]
                    value = value[2:]
            elif value[0] in self.prefixes:
                node, value = self.parse_node(value, **kwargs)
                out += node
            else:
                out += value[0]
                value = value[1:]
        if out or not error_msg:
            return out, value
        else:
            raise ParseError(error_msg, value)

    def parse_node(self, value: str, **kwargs) -> tuple[str, str]:
        # $cmd#id.class.class[data]{text}
        prefix, value = value[0], value[1:]
        command, value = self.parse_string(value, alphabet=STRING_CHARS, error_msg='Invalid command name')

        node = self.nodes.get(prefix, {}).get(command)
        if node is None:
            return error(f'Invalid node: {prefix}{command}'), value

        if value and value[0] == '#':
            id, value = self.parse_string(value[1:], alphabet=STRING_CHARS, error_msg='Invalid id')
        else:
            id = ''

        classes = []
        while value and value[0] == '.':
            class_, value = self.parse_string(value[1:], alphabet=STRING_CHARS, error_msg='Invalid class')
            classes.append(class_)

        if value and value[0] == '[':
            raw_data, value = self.parse_list(value[1:], exclude=self.prefixes, end=']', error_msg='Incomplete data field')
            data, kwargs = node.parse_data(raw_data, **kwargs)
            value = value[1:]
        else:
            data = []

        if value and value[0] == '{':
            text, value = self.parse_list(value[1:], end='}', error_msg='Incomplete text field', **kwargs)
            value = value[1:]
        else:
            text = []

        try:
            return str(node(id, classes, data, text)), value
        except nodes.MarkupError as e:
            return error(e.message), value
        except Exception as e:
            return error(f'{type(e).__name__}: {e}'), value

    def parse_list(self, value: str, *, exclude: str='', end: str='', error_msg: str='', **kwargs) -> tuple[list[str], str]:
        parts = []
        while value and value[0] not in end:
            if value[0] in string.whitespace:
                _, value = self.parse_string(value, alphabet=string.whitespace)
                continue
            elif value[0] == '"':
                part, value = self.parse_string(value[1:], exclude=exclude + '"', **kwargs)
                if not value:
                    raise ParseError('Incomplete string', value)
                elif value[0] != '"':
                    raise ParseError('Invalid character', value)
                value = value[1:]
            else:
                part, value = self.parse_string(value, exclude=exclude + end + '"' + string.whitespace, error_msg='Invalid character', **kwargs)
            parts.append(part)
        if end and not value:
            raise ParseError(error_msg, value)
        return parts, value
