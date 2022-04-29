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
    params: Attributes = {}

    def __init__(self, id: str='', classes: list[str]=None, data: Attributes=None, text: list[str]=None) -> None:
        self.attributes = {'id': id, 'class': classes or []}
        self.data = self.make_data(self.default_data() | (data or {}))
        self.text = text or []

    def __str__(self) -> str:
        return html(self.tag, self.make_attributes(), self.make_content(self.text))

    @classmethod
    def default_data(cls) -> Attributes:
        return {param.removesuffix('=').removesuffix('?'): value for param, value in cls.params.items()}

    @classmethod
    def parse_data(cls, raw_data: list[str], **kwargs) -> tuple[Attributes, Attributes]:
        return parse_data(raw_data, cls.params), kwargs

    def make_data(self, data: Attributes) -> Attributes:
        return data

    def make_attributes(self) -> Attributes:
        return self.attributes

    def make_content(self, text: list[str]) -> list[str]:
        return text


def parse_data(data: list[str], params: Attributes) -> Attributes:
    positionals = {param: default for param, default in reversed(params.items()) if not param.endswith('?') and not param.endswith('=')}
    boolean = {param.removesuffix('?'): default for param, default in params.items() if param.endswith('?')}
    named = {param.removesuffix('='): default for param, default in params.items() if param.endswith('=')}
    data_dict = {}
    for arg in data:
        # Test for named argument
        if '=' in arg:
            name, value = arg.split('=', maxsplit=1)
            if name in named or '*' in named:
                named.pop(name, None)
                data_dict[name] = value
            else:
                raise InvalidData(f'unknown named argument {name!r}')
        # Test for boolean argument
        elif arg in boolean:
            boolean.pop(arg)
            data_dict[arg] = True
        # Must be positional
        elif positionals:
            name, _ = positionals.popitem()
            data_dict[name] = arg
        else:
            raise InvalidData(f'additional positional argument {arg!r}')
    named.pop('*', None)
    missing = []
    for name, default in (positionals | boolean | named).items():
        if default is None:
            missing.append(name)
        else:
            data_dict[name] = default
    if missing:
        raise InvalidData(f'missing required arguments {"".join(list(map(repr, missing)))}')
    return data_dict
