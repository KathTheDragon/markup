from functools import wraps
from typing import Callable, Optional
from ..html import Attributes, html

_HandlerArgs = [Attributes, list[str], Optional[list[str]]]
_HandlerReturn = tuple[str, Attributes, Optional[list[str]]]
_Handler = Callable[_HandlerArgs, _HandlerReturn]
HandlerArgs = [Optional[str], list[str], list[str], Optional[list[str]]]
Handler = Callable[HandlerArgs, str]

def handler(func: _Handler) -> Handler:
    @wraps(func)
    def wrapper(id: Optional[str]=None, classes: list[str]=None, data: list[str]=None, text: Optional[list[str]]=None) -> str:
        attributes = {
            'id': id,
            'class': classes or [],
        }
        return html(*func(attributes, data or [], text))

    return wrapper
