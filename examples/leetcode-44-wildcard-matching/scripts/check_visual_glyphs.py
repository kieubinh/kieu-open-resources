#!/usr/bin/env python3
"""Fail if any non-ASCII character that the Remotion visuals can draw has no glyph in the vendored fonts.

Complements skills/kieu-leetcode-video/scripts/check_glyphs.py (which only looks at episode.py): this also scans
every string literal / JSX text in src/**/*.tsx plus the subtitle and title text in scripts/episode.py.
Requires fontTools:  python3 -m venv /tmp/ep03venv && /tmp/ep03venv/bin/pip install fonttools
"""
import re
import sys
from pathlib import Path

try:
    from fontTools.ttLib import TTFont
except ImportError:  # pragma: no cover
    sys.exit("fontTools is required: pip install fonttools")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

FONTS = {"Noto Sans": ROOT / "public/fonts/NotoSans-Variable.ttf", "JetBrains Mono": ROOT / "public/fonts/JetBrainsMono-Variable.ttf"}
NON_ASCII = re.compile(r"[^\x00-\x7f]")


def corpus():
    text = []
    for f in sorted((ROOT / "src").rglob("*.tsx")):
        text.append(f.read_text(encoding="utf-8"))
    from episode import S
    for s in S:
        text += [s.title, s.phase, *s.lines, s.script]
    return "\n".join(text)


def main():
    chars = sorted({c for c in NON_ASCII.findall(corpus()) if not c.isspace()})
    noto, mono = (TTFont(FONTS[k]).getBestCmap() for k in ("Noto Sans", "JetBrains Mono"))
    not_noto = [c for c in chars if ord(c) not in noto]
    uncovered = [c for c in not_noto if ord(c) not in mono]
    fmt = lambda cs: " ".join(f"{c}(U+{ord(c):04X})" for c in cs)
    print(f"{len(chars)} distinct non-ASCII characters in visuals + narration text")
    print(f"INFO  drawn from the JetBrains Mono fallback (absent in Noto Sans): {fmt(not_noto) or 'none'}")
    if uncovered:
        print(f"FAIL  no glyph in the vendored font stack: {fmt(uncovered)}")
        return 1
    print("PASS  every character is covered by the vendored font stack (Noto Sans -> JetBrains Mono); no system-font fallback needed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
