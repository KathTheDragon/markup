import string
from . import nodes
from .exceptions import MarkupError
from .html import html

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


class Markup:
    def __init__(self) -> None:
        self.node_handlers = nodes.make_node_handlers()
        self.simple_nodes = nodes.make_simple_nodes()
        self.prefixes = ''.join(set(self.simple_nodes) | set(self.node_handlers))

    def parse(self, string: str) -> str:
        output, remainder = self.parse_string(string, alphabet='', embed=True)
        if remainder:
            ...
        return output

    def parse_string(self, value: str, *, alphabet: str=STRING_CHARS, exclude: str='', error_msg: str='') -> tuple[str, str]:
        escape = is_valid_char('\\', alphabet, exclude)
        embed = any(is_valid_char(char, alphabet, exclude) for char in self.prefixes)
        out = ''
        while value:
            if escape and value[0] == '\\':
                if len(value) <= 1:
                    raise ParseError('Incomplete escape sequence', value)
                else:
                    out += value[:2]
                    value = value[2:]
            elif embed and value[0] in self.prefixes:
                tag, value = self.parse_node(value)
                out += tag
            elif is_valid_char(value[0], alphabet, exclude):
                out += value[0]
                value = value[1:]
            else:
                break
        if out:
            return out, value
        else:
            raise ParseError(error_msg, value)

    def parse_node(value: str) -> str:
        # $cmd#id.class.class[data]{text}
        prefix, value = value[0], value[1:]
        command, value = self.parse_string(value, error_msg='Invalid command name')

        if value and value[0] == '#':
            id, value = self.parse_string(value[1:], error_msg='Invalid id')
        else:
            id = None

        classes = []
        while value and value[0] == '.':
            class_, value = self.parse_string(value[1:], error_msg='Invalid class')
            classes.append(class_)

        if value and value[0] == '[':
            data, value = self.parse_list(value[1:], skip_whitespace=True, exclude=self.prefixes, end=']')
            value = value[1:]
        else:
            data = []

        if value and value[0] == '{':
            text, value = self.parse_list(value[1:], end='}')
            value = value[1:]
        else:
            text = None

        try:
            handler = self.node_handlers.get(prefix, {}).get(command)
            if handler is None:
                if command in self.simple_nodes.get(prefix, []):
                    handler = nodes.simple_node
                else:
                    raise MarkupError(f'Invalid node: {prefix}{command}')

            return handler(command, id, classes, data, text), value
        except MarkupError as e:
            return error(e.message), value
        except Exception:
            return error(f'{type(e).__name__}: {e}'), value

    def parse_list(self, value: str, *, skip_whitespace: bool=False, exclude: str='', end: str='', error_msg: str='') -> tuple[list[str], str]:
        parts = []
        while value and value[0] not in end:
            if value[0] in string.whitespace:
                part, value = self.parse_string(value, alphabet=string.whitespace, error_msg='Invalid whitespace')
                if skip_whitespace:
                    continue
            elif value[0] == '"':
                part, value = self.parse_string(value[1:], alphabet='', exclude=exclude + '"', error_msg='Empty or incomplete string')
                if value[0] != '"':
                    raise ParseError('Incomplete string', value)
                value = value[1:]
            else:
                part, value = self.parse_string(value, alphabet='', exclude=exclude + end + '"' + string.whitespace)
            parts.append(part)
        return parts, value
