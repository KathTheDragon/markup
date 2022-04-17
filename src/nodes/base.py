from typing import Optional
from ..html import Attributes, html

class MarkupError(Exception):
    prefix = ''

    def __init__(self, message: str) -> None:
        self.message = message
        if self.prefix:
            super().__init__(f'{self.prefix}: {message}')
        else:
            super().__init__(message)


class InvalidData(MarkupError):
    prefix = 'Invalid data'


class Node:
    tag: str
    params: tuple[str, ...] = ()

    def __init__(self, id: Optional[str]=None, classes: list[str]=None, data: list[str]=None, text: Optional[list[str]]=None) -> None:
        self.attributes = {'id': id, 'class': classes or []}
        self.data = self.parse_data(data or [])
        self.text = text

    def __str__(self) -> str:
        return html(self.tag, self.make_attributes(), self.make_content())

    def parse_data(self, data: list[str]) -> Attributes:
        return parse_data(data, self.params)

    def make_attributes(self) -> Attributes:
        return self.attributes

    def make_content(self) -> Optional[list[str]]:
        return self.text


def parse_data(data: list[str], params: tuple[str, ...]) -> Attributes:
    positionals = [param for param in reversed(params) if not param.endswith('?') and not param.endswith('=')]
    boolean = {param.removesuffix('?') for param in params if param.endswith('?')}
    named = {param.removesuffix('=') for param in params if param.endswith('=')}
    data_dict = {}
    for arg in data:
        # Test for named argument
        if '=' in arg:
            name, value = arg.split('=', maxsplit=1)
            if name in named:
                named.remove(name)
                data_dict[name] = value
            else:
                raise InvalidData(f'unknown named argument {name!r}')
        # Test for boolean argument
        elif arg in boolean:
            boolean.remove(arg)
            data_dict[arg] = True
        # Must be positional
        elif positionals:
            name = positionals.pop()
            data_dict[name] = arg
        else:
            raise InvalidData(f'additional positional argument {arg!r}')
    if positionals:
        raise InvalidData(f'missing required arguments {"".join(list(map(repr, positionals)))}')
    return data_dict
