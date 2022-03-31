def partition(strings: list[str], separator: str) -> list[list[str]]:
    parts = []
    i = 0
    while i < len(strings):
        if strings[i] == separator:
            parts.append(strings[:i])
            strings = strings[i+1:]
            i = 0
        else:
            i += 1
    parts.append(strings)
    return parts


def strip(strings: list[str]) -> tuple[str, list[str], str]:
    leading = trailing = ''
    if strings and strings[0].isspace():
        leading = strings.pop(0)
    if strings and strings[-1].isspace():
        trailing = strings.pop()
    return leading, strings, trailing
