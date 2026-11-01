"""Vietnamese number reading for narration (digits are never sent to the TTS engine)."""

DIGITS = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
GROUPS = ["", "nghìn", "triệu", "tỷ"]


def _two(n):
    """Read 0 <= n <= 99 (n >= 1)."""
    if n < 10:
        return DIGITS[n]
    tens, unit = divmod(n, 10)
    head = "mười" if tens == 1 else DIGITS[tens] + " mươi"
    if unit == 0:
        return head
    if unit == 1 and tens > 1:
        return head + " mốt"
    if unit == 5:
        return head + " lăm"
    return head + " " + DIGITS[unit]


def _three(n, leading):
    """Read one 3-digit group; ``leading`` means it is the most significant group."""
    hundreds, rest = divmod(n, 100)
    if hundreds == 0:
        if leading:
            return _two(rest)
        return "không trăm " + (("lẻ " + DIGITS[rest]) if 0 < rest < 10 else _two(rest))
    head = DIGITS[hundreds] + " trăm"
    if rest == 0:
        return head
    if rest < 10:
        return head + " lẻ " + DIGITS[rest]
    return head + " " + _two(rest)


def vi_int(n):
    if n < 0:
        return "âm " + vi_int(-n)
    if n == 0:
        return "không"
    groups = []
    while n:
        n, g = divmod(n, 1000)
        groups.append(g)
    parts = []
    for index in range(len(groups) - 1, -1, -1):
        g = groups[index]
        if g == 0:
            continue
        parts.append(_three(g, leading=(index == len(groups) - 1)) + (" " + GROUPS[index] if GROUPS[index] else ""))
    return " ".join(parts)


def vi_decimal(text):
    """'33,1' -> 'ba mươi ba phẩy một'; digits after the comma are read one by one."""
    whole, _, frac = text.partition(",")
    spoken = vi_int(int(whole))
    if frac:
        spoken += " phẩy " + " ".join(DIGITS[int(c)] for c in frac)
    return spoken


def vn_group(n):
    """Display an integer with Vietnamese thousands separators: 967654 -> '967.654'."""
    return f"{n:,}".replace(",", ".")
