from functools import wraps
from typing import Callable, Optional
from ..html import Attributes, html

_HandlerArgs = [str, Attributes, list[str], Optional[list[str]]]
_HandlerReturn = tuple[str, Attributes, Optional[list[str]]]
_Handler = Callable[_HandlerArgs, _HandlerReturn]
HandlerArgs = [str, Optional[str], list[str], list[str], Optional[list[str]]]
Handler = Callable[HandlerArgs, str]

def handler(func: _Handler) -> Handler:
    @wraps(func)
    def wrapper(command: str, id: Optional[str]=None, classes: list[str]=None, data: list[str]=None, text: Optional[list[str]]=None) -> str:
        attributes = {
            'id': id,
            'class': classes or [],
        }
        return html(*func(command, attributes, data or [], text))

    return wrapper
