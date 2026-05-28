_MAP = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
    "ж": "j", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "x", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch",
    "ъ": "ʼ", "ы": "i", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    "ў": "o‘", "қ": "q", "ғ": "g‘", "ҳ": "h",
}

_CAP = {
    "А": "A", "Б": "B", "В": "V", "Г": "G", "Д": "D", "Е": "E", "Ё": "Yo",
    "Ж": "J", "З": "Z", "И": "I", "Й": "Y", "К": "K", "Л": "L", "М": "M",
    "Н": "N", "О": "O", "П": "P", "Р": "R", "С": "S", "Т": "T", "У": "U",
    "Ф": "F", "Х": "X", "Ц": "Ts", "Ч": "Ch", "Ш": "Sh", "Щ": "Shch",
    "Ъ": "ʼ", "Ы": "I", "Ь": "", "Э": "E", "Ю": "Yu", "Я": "Ya",
    "Ў": "O‘", "Қ": "Q", "Ғ": "G‘", "Ҳ": "H",
}


def to_latin(text: str) -> str:
    if not text:
        return text
    out = []
    for ch in text:
        if ch in _MAP:
            out.append(_MAP[ch])
        elif ch in _CAP:
            out.append(_CAP[ch])
        else:
            out.append(ch)
    return "".join(out)


def is_cyrillic(text: str) -> bool:
    if not text:
        return False
    cyr = sum(1 for c in text if "Ѐ" <= c <= "ӿ")
    return cyr > len(text) * 0.2
