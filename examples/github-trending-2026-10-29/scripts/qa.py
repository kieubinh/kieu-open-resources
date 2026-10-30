#!/usr/bin/env python3
"""Machine-readable QA for the GitHub Radar episode. Anything not run is NOT RUN, never PASS."""
from __future__ import annotations
import json, subprocess, sys, wave
from pathlib import Path
from episode import S
from config import ROOT, AUDIO_DIR, VIDEO_SPEED, RUNTIME_MIN_MAX_SECONDS, find_font

results = {}


def check(name, ok, detail=''):
    results[name] = dict(status='PASS' if ok else 'FAIL', detail=detail)


def not_run(name, why):
    results[name] = dict(status='NOT RUN', detail=why)


# glyph coverage of every on-screen / narrated string for the fonts used
try:
    from fontTools.ttLib import TTFont
    for kind in ('REGULAR', 'BOLD', 'MONO'):
        font = TTFont(find_font(kind), fontNumber=0)
        cmap = font.getBestCmap()
        if kind == 'MONO':   # mono is used only for code lines and repo names; Vietnamese comments render in sans
            text = ''.join(c for s in S for c in s.data.get('cmds', []) if not c.startswith('#')) + ''.join(s.repo for s in S)
        else:
            text = ''.join(s.title + s.phase + ''.join(s.lines) + json.dumps(s.data, ensure_ascii=False) for s in S)
        missing = sorted({c for c in text if ord(c) > 32 and ord(c) not in cmap and c not in '{}[]":,\\'})
        check(f'glyphs_{kind.lower()}', not missing, 'missing: ' + ''.join(missing))
except Exception as e:  # noqa
    not_run('glyphs', f'fontTools/font lookup unavailable: {e}')

timeline = json.loads((ROOT / 'src/timeline.json').read_text())
seconds = sum(r['frames'] for r in timeline) / 30
lo, hi = RUNTIME_MIN_MAX_SECONDS
check('runtime_bounds', lo <= seconds <= hi, f'{seconds / 60:.2f} min')
check('speed_is_normal', VIDEO_SPEED == 1.0, f'VIDEO_SPEED={VIDEO_SPEED}')
check('avatar_image_present', (ROOT / 'public/brand/kieu-avatar.png').is_file())
check('lipsync_assets', (ROOT / 'public/brand/kieu-avatar-nomouth.png').is_file() and (ROOT / 'src/avatar.mouth.json').is_file(), 'mouthless face + mouth anchor')

voiced = [s for s in S if not s.silent]
have = [s for s in voiced if (AUDIO_DIR / (s.id + '.wav')).exists()]
if len(have) == len(voiced):
    bad = []
    for s in voiced:
        with wave.open(str(AUDIO_DIR / (s.id + '.wav')), 'rb') as w:
            if w.getnframes() / w.getframerate() < 0.5:
                bad.append(s.id)
    check('voicestudio_wavs', not bad, f'{len(have)}/{len(voiced)} WAVs' + (f'; short: {bad}' if bad else ''))
    check('timeline_uses_wavs', all(r['audio'] for r in timeline if not r['silent']))
else:
    not_run('voicestudio_wavs', f'{len(have)}/{len(voiced)} WAVs present')
rep = ROOT / 'output/envelope_report.json'
env_kind = json.loads(rep.read_text()).get('kind') if rep.exists() else None
if env_kind == 'measured':
    check('avatar_envelope_measured', True, 'RMS of the real narration WAVs')
    mj = json.loads((ROOT / 'src/mouth.json').read_text())
    closed = sum(1 for v in mj.values() for x in v['o'] if x == 0); total = sum(len(v['o']) for v in mj.values())
    check('lipsync_mouth_track', total == sum(r['frames'] for r in timeline) and 0.05 < closed / total < 0.6, f'{closed}/{total} closed frames; opening varies with the audio')
else:
    not_run('avatar_envelope_measured', f'envelope kind: {env_kind} (estimated until VoiceStudio WAVs exist)')
not_run('captions_audio_aligned', 'cues are estimated from text; align with forced alignment or human check before upload')
not_run('human_editorial_approval', 'requires the owner')
out = ROOT / 'output/QA_results.json'
out.write_text(json.dumps(results, indent=2, ensure_ascii=False))
bad = [k for k, v in results.items() if v['status'] == 'FAIL']
print(json.dumps({k: v['status'] for k, v in results.items()}, indent=1))
sys.exit(1 if bad else 0)
