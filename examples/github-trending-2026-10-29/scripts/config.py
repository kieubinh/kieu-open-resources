"""Per-episode names and settings shared by the pipeline scripts.

For a new GitHub Radar episode edit the constants below, the Remotion composition id in
package.json / src/root.tsx, and nothing else in scripts/ hardcodes the episode.
"""
from __future__ import annotations
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EPISODE = os.environ.get('KIEU_EPISODE', 'gr01').lower()   # one repo per video: gr01 | gr02 | gr03
AUDIO_SLUG = 'github-radar-voicestudio'       # public/audio/<AUDIO_SLUG>/<scene id>.wav (scene ids are unique per repo)
FORMAT = os.environ.get('KIEU_FORMAT', 'full').lower()   # full | short (one-minute cut, scripts/shorts.py)
SHORT = FORMAT == 'short'
LANG = os.environ.get('KIEU_LANG', 'vi').lower()          # vi | en (English exists for the short cut only)
EN = LANG == 'en'
if EN and not SHORT:
    raise SystemExit('KIEU_LANG=en needs KIEU_FORMAT=short')
OUT_PREFIX = EPISODE.upper() + ('_SHORT' if SHORT else '') + ('_EN' if EN else '')   # output/<OUT_PREFIX>_*.srt|json|mp4
COMPOSITION = 'GitHubRadarShort' if SHORT else 'GitHubRadar'   # short = 1080x1920 (9:16) for YouTube Shorts
FACE_NAME = EPISODE + ('_short' if SHORT else '') + ('_en' if EN else '')            # public/lipsync/<FACE_NAME>.mp4
SNAPSHOT_DATE = '2026-10-29'

AUDIO_DIR = ROOT / 'public' / 'audio' / AUDIO_SLUG
RAW_DIR = AUDIO_DIR / 'raw'
AUDIO_URL = f'audio/{AUDIO_SLUG}'

# Narration speed: 1.0x (normal) unless the owner asks otherwise (2026-10-29). Override with KIEU_VIDEO_SPEED;
# a value other than 1.0 is applied exactly once with FFmpeg atempo after raw synthesis (pitch preserved).
# Voice: Narrator 03 (27ad8d83) must still be listed by VoiceStudio --voices; override via env.
DEFAULT_VOICE = '823d23e3' if EN else '27ad8d83'   # en: Kieu Studio English B (approved for new English videos); vi: Narrator 03
VIDEO_SPEED = float(os.environ.get('KIEU_VIDEO_SPEED', '1.0'))
RUNTIME_MIN_MAX_SECONDS = (30, 60) if SHORT else (2 * 60, 8 * 60)   # full: one repo at 1.0x is 3-5 min; short: at most one minute
TAIL_SECONDS = 0.4 if SHORT else 0.6

# Avatar (owner-approved defaults at 1920x1080): 220 px circle, 64 px margins, 4 px ring.
AVATAR_FILE = 'brand/kieu-avatar.png'        # relative to public/, produced by prepare_avatar.py

_CANDIDATES = {
    'REGULAR': ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/Library/Fonts/DejaVuSans.ttf',
                '~/Library/Fonts/DejaVuSans.ttf', '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
                'C:/Windows/Fonts/arial.ttf'],
    'BOLD': ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/Library/Fonts/DejaVuSans-Bold.ttf',
             '~/Library/Fonts/DejaVuSans-Bold.ttf', '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
             'C:/Windows/Fonts/arialbd.ttf'],
    'MONO': ['/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', '/Library/Fonts/DejaVuSansMono.ttf',
             '~/Library/Fonts/DejaVuSansMono.ttf', '/System/Library/Fonts/Menlo.ttc', 'C:/Windows/Fonts/consola.ttf'],
}


def find_font(kind: str) -> str:
    env = os.environ.get('KIEU_FONT_' + kind, '').strip()
    for raw in ([env] if env else _CANDIDATES[kind]):
        p = Path(raw).expanduser()
        if p.is_file():
            return str(p)
    raise RuntimeError(f'No {kind.lower()} font found. Install DejaVu Sans or set KIEU_FONT_{kind} to a TTF/TTC '
                       'that covers Vietnamese and math symbols.')
