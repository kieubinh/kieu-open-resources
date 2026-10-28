"""Per-episode names and portable font lookup shared by the pipeline scripts.

For a new episode edit the three constants below (and the Remotion composition id
in package.json / src/root.tsx); nothing else in scripts/ hardcodes the episode.
"""
from __future__ import annotations
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIO_SLUG = 'leetcode-04-voicestudio'   # public/audio/<AUDIO_SLUG>/<scene id>.wav
OUT_PREFIX = 'EP04'                       # output/<OUT_PREFIX>_*.srt|png|mp4
REVIEW_MP4 = 'EP04_MEDIAN_VISUAL_REVIEW_ONLY.mp4'

AUDIO_DIR = ROOT / 'public' / 'audio' / AUDIO_SLUG
AUDIO_URL = f'audio/{AUDIO_SLUG}'          # path relative to Remotion public/

# Override with KIEU_FONT_REGULAR / KIEU_FONT_BOLD / KIEU_FONT_MONO (absolute paths).
_CANDIDATES = {
    'REGULAR': [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/dejavu/DejaVuSans.ttf',
        '/Library/Fonts/DejaVuSans.ttf',
        '~/Library/Fonts/DejaVuSans.ttf',
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
        'C:/Windows/Fonts/arial.ttf',
    ],
    'BOLD': [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf',
        '/Library/Fonts/DejaVuSans-Bold.ttf',
        '~/Library/Fonts/DejaVuSans-Bold.ttf',
        # macOS Arial Bold lacks U+2076/U+21D2; Arial Unicode covers them but has no bold weight.
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
        'C:/Windows/Fonts/arialbd.ttf',
    ],
    'MONO': [
        '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
        '/usr/share/fonts/dejavu/DejaVuSansMono.ttf',
        '/Library/Fonts/DejaVuSansMono.ttf',
        '~/Library/Fonts/DejaVuSansMono.ttf',
        '/System/Library/Fonts/Menlo.ttc',
        'C:/Windows/Fonts/consola.ttf',
    ],
}


def find_font(kind: str) -> str:
    """Return a font path for REGULAR/BOLD/MONO or raise with the remedy.

    Glyph coverage is NOT assumed: qa.py and check_glyphs.py must still pass on the
    font that is returned here.
    """
    env = os.environ.get('KIEU_FONT_' + kind, '').strip()
    paths = [env] if env else _CANDIDATES[kind]
    for raw in paths:
        p = Path(raw).expanduser()
        if p.is_file():
            return str(p)
    raise RuntimeError(f'No {kind.lower()} font found. Install DejaVu Sans or set KIEU_FONT_{kind} to a TTF/TTC that covers Vietnamese and math symbols.')
