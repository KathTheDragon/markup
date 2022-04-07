class MarkupError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class InvalidData(MarkupError):
    def __init__(self) -> None:
        super().__init__('Invalid data field')

    def __str__(self) -> str:
        return ''
