import string
from .exceptions import MarkupError
from .html import html
from .nodes import process

class ParseError(Exception):
    def __init__(self, message: str, remainder: str) -> str:
        self.message = message
        self.remainder = remainder
        super().__init__(message)


def parse(value: str, *, skip_whitespace: bool=False, exclude: str='', end: str='', embed: bool=True, error_msg: str='') -> tuple[list[str], str]:
    parts = []
    quoted_exclude = exclude + '"'
    unquoted_exclude = exclude + end + '"' + string.whitespace
    while value and value[0] not in exclude + end:
        if value[0] in string.whitespace:
            part, value = parse_string(value, alphabet=string.whitespace, exclude=exclude, error_msg='Invalid whitespace')
            if skip_whitespace:
                continue
        elif value[0] == '"':
            part, value = parse_string(value[1:], alphabet='', exclude=quoted_exclude, escape=True, no_escape=exclude, embed=embed, error_msg='Empty or incomplete string')
            if value[0] != '"':
                raise ParseError('Incomplete string', value)
            value = value[1:]
        else:
            part, value = parse_string(value, alphabet='', exclude=unquoted_exclude, escape=True, no_escape=exclude, embed=embed)
        parts.append(part)
    return parts, value


STRING_CHARS = string.ascii_letters + string.digits + '_-'
NODE_TYPES = {
    '$': process,
}

def parse_string(value: str, *, alphabet: str=STRING_CHARS, exclude: str='', escape: bool=False, no_escape: str='', embed: bool=False, error_msg: str='') -> tuple[str, str]:
    out = ''
    while value:
        if escape and value[0] == '\\':
            if len(value) <= 1:
                raise ParseError('Incomplete escape sequence', value)
            elif value[1] in no_escape:
                raise ParseError('Invalid escape sequence', value)
            else:
                out += value[:2]
                value = value[2:]
        elif embed and value[0] in NODE_TYPES:
            tag, value = parse_tag(value)
            out += tag
        elif (not alphabet or value[0] in alphabet) and value[0] not in exclude:
            out += value[0]
            value = value[1:]
        else:
            break
    if out:
        return out, value
    else:
        raise ParseError(error_msg, value)


def parse_tag(value: str) -> str:
    # $cmd#id.class.class[data]{text}
    func = NODE_TYPES[value[0]]
    value = value[1:]
    command, value = parse_string(value, error_msg='Invalid command name')
    id, value = parse_id(value)
    classes, value = parse_classes(value)
    data, value = parse_data(value)
    text, value = parse_text(value)

    try:
        return html(*func(command, id, classes, data, text)), value
    except MarkupError as e:
        raise ParseError(e.message, value)
    except Exception:
        raise ParseError('An unknown error occurred', value)


def parse_id(value: str) -> tuple[str | None, str]:
    if value and value[0] == '#':
        return parse_string(value[1:], error_msg='Invalid id')
    else:
        return None, value


def parse_classes(value: str) -> tuple[list[str], str]:
    classes = []
    while value and value[0] == '.':
        class_, value = parse_string(value[1:], error_msg='Invalid class')
        classes.append(class_)
    return classes, value


def parse_data(value: str) -> tuple[list[str], str]:
    if value and value[0] == '[':
        data, value = parse(value[1:], skip_whitespace=True, exclude='\r\n', end=']', embed=False)
        return data, value[1:]
    else:
        return [], value


def parse_text(value: str) -> tuple[list[str] | None, str]:
    if value and value[0] == '{':
        text, value = parse(value[1:], end='}')
        return text, value[1:]
    else:
        return None, value


def error(msg: str) -> str:
    return f'<span class="error">&lt;{msg}&gt;</span>'
