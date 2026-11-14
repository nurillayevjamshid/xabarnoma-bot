_MAP = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
    "ж": "j", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "x", "ц": "ts", "ч": "ç", "ш": "ş", "щ": "şç",
    "ъ": "ʼ", "ы": "i", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    "ў": "ō", "қ": "q", "ғ": "ğ", "ҳ": "h",
}

_CAP = {
    "А": "A", "Б": "B", "В": "V", "Г": "G", "Д": "D", "Е": "E", "Ё": "Yo",
    "Ж": "J", "З": "Z", "И": "I", "Й": "Y", "К": "K", "Л": "L", "М": "M",
    "Н": "N", "О": "O", "П": "P", "Р": "R", "С": "S", "Т": "T", "У": "U",
    "Ф": "F", "Х": "X", "Ц": "Ts", "Ч": "Ç", "Ш": "Ş", "Щ": "Şç",
    "Ъ": "ʼ", "Ы": "I", "Ь": "", "Э": "E", "Ю": "Yu", "Я": "Ya",
    "Ў": "Ō", "Қ": "Q", "Ғ": "Ğ", "Ҳ": "H",
}

_OLD_LATIN_MAP = [
    # CH
    ("CH", "Ç"),
    ("Ch", "Ç"),
    ("ch", "ç"),
    # SH
    ("SH", "Ş"),
    ("Sh", "Ş"),
    ("sh", "ş"),
    # O' variants (o‘, o', o`, oʻ, o’)
    ("O‘", "Ō"),
    ("O'", "Ō"),
    ("O`", "Ō"),
    ("Oʻ", "Ō"),
    ("O’", "Ō"),
    ("o‘", "ō"),
    ("o'", "ō"),
    ("o`", "ō"),
    ("oʻ", "ō"),
    ("o’", "ō"),
    # G' variants (g‘, g', g`, gʻ, g’)
    ("G‘", "Ğ"),
    ("G'", "Ğ"),
    ("G`", "Ğ"),
    ("Gʻ", "Ğ"),
    ("G’", "Ğ"),
    ("g‘", "ğ"),
    ("g'", "ğ"),
    ("g`", "ğ"),
    ("gʻ", "ğ"),
    ("g’", "ğ"),
]


def replace_old_latin(text: str) -> str:
    """Eski o'zbek lotin alifbosidagi harflarni yangi alifboga almashtiradi."""
    if not text:
        return text
    for old, new in _OLD_LATIN_MAP:
        text = text.replace(old, new)
    return text


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
    return replace_old_latin("".join(out))


def is_cyrillic(text: str) -> bool:
    if not text:
        return False
    cyr = sum(1 for c in text if "Ѐ" <= c <= "ӿ")
    return cyr > len(text) * 0.2
