def truncate(s: str, length: int = 70, kill_words: bool = True, end: str = "...") -> str:
    if len(s) <= length:
        return s

    if kill_words:
        return s[: length - len(end)] + end

    result = s[: length - len(end)].rsplit(maxsplit=1)[0]
    return result + end
