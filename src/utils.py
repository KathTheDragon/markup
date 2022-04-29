def partition(strings: list[str], separator: str) -> list[list[str]]:
    parts = []
    i = 0
    while i < len(strings):
        if strings[i] == separator:
            parts.append(strip(strings[:i]))
            strings = strings[i+1:]
            i = 0
        else:
            i += 1
    parts.append(strip(strings))
    return parts


def strip(strings: list[str]) -> list[str]:
    if strings and strings[0].isspace():
        strings = strings[1:]
    if strings and strings[-1].isspace():
        strings = strings[:-1]
    return strings
