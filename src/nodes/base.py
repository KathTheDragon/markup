from typing import Optional
from ..html import Attributes, html

class Node:
    def __init__(self, id: Optional[str]=None, classes: list[str]=None, data: list[str]=None, text: Optional[list[str]]=None) -> None:
        self.attributes = {'id': id, 'class': classes or []}
        self.data = self.parse_data(data or [])
        self.text = text

    def __str__(self) -> str:
        return html(self.tag, self.make_attributes(), self.make_content())

    def parse_data(self, data: list[str]) -> Attributes:
        if data:
            raise InvalidData()
        return {}

    def make_attributes(self) -> Attributes:
        return self.attributes | self.data

    def make_content(self) -> Optional[list[str]]:
        return self.text
