from typing import Optional
from ..html import Attributes, html

HTML = tuple[str, Attributes, Optional[list[str]]]

class Node:
    @classmethod
    def make(cls, id: Optional[str]=None, classes: list[str]=None, data: list[str]=None, text: Optional[list[str]]=None) -> str:
        attributes = {
            'id': id,
            'class': classes or [],
        }
        return html(*cls.process(attributes, data or [], text))
