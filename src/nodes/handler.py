from functools import wraps
from typing import Callable
from ..html import Attributes, html

_HandlerArgs = [str, Attributes, list[str], list[str] | None]
_HandlerReturn = tuple[str, Attributes, list[str] | None]
_Handler = Callable[_HandlerArgs, _HandlerReturn]
HandlerArgs = [str, str | None, list[str], list[str], list[str] | None]
Handler = Callable[HandlerArgs, str]

def handler(func: _Handler) -> Handler:
    @wraps(func)
    def wrapper(command: str, id: str | None=None, classes: list[str]=None, data: list[str]=None, text: list[str] | None=None) -> str:
        attributes = {
            'id': id,
            'class': classes or [],
        }
        return html(*func(command, attributes, data or [], text))

    return wrapper
