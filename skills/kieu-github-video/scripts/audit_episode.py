#!/usr/bin/env python3
"""Structure audit for a Kieu GitHub Radar episode.

Usage: audit_episode.py --episode <ep>/scripts/episode.py [--repos 3]
Checks (ONE repo per video): exactly one repo, the nine beats in order (intro, growth, why, problem, how, usage, value,
ideas, outro), a caveat in `value`, intro tiles, a growth scene with numbers, no 5+ digit numbers in narration,
default speed 1.0, unique scene ids. If the module defines EPISODES every episode is audited.

With --short the module's SHORTS (one-minute cuts) are audited instead: one repo, the seven short beats (intro, growth,
why, how, usage, value, outro), the same caveat/hook/number rules, the opening question answered in the outro, visuals
identical to the full episode's scenes (so a number cannot differ; skipped for Short-only episodes with no full cut), and an estimated
runtime of at most SHORT_MAX_SECONDS (module constant, default 60; the GR04-GR08 Shorts set 180).
With --short --lang en the English cut (SHORTS_EN) is audited the same way: texts differ, but mode, line count, every numeric field
(total, month, week, today, segs, avg, chart point values) must equal the full episode's, scenes need `data.lang == 'en'`, and the
narration must contain no Vietnamese letters.
"""
from __future__ import annotations
import argparse, importlib.util, os, re, sys
from pathlib import Path

BEATS = ['intro', 'growth', 'why', 'problem', 'how', 'usage', 'value', 'ideas', 'outro']
SHORT_BEATS = ['intro', 'growth', 'why', 'how', 'usage', 'value', 'outro']
WORDS_PER_SECOND, TAIL = 2.9, 0.4    # shorts, measured with VoiceStudio Narrator 03 at 1.0x (English product names are slow)


LIMITS = {'max': 60}   # Short length cap in seconds; an episode module may raise it with SHORT_MAX_SECONDS (GR04-GR08: 180)


def load(path: Path):  # returns {name: scenes}
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location('episode', path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    LIMITS['max'] = getattr(m, 'SHORT_MAX_SECONDS', 60)
    return getattr(m, 'EPISODES', {'episode': m.S}), (getattr(m, 'SHORTS_EN', None) if os.environ.get('KIEU_AUDIT_LANG') == 'en' else getattr(m, 'SHORTS', None))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--episode', required=True); ap.add_argument('--short', action='store_true'); ap.add_argument('--lang', default='vi', choices=['vi', 'en'])
    a = ap.parse_args(); os.environ['KIEU_AUDIT_LANG'] = a.lang; episodes, shorts = load(Path(a.episode).resolve()); errors = []
    if a.short:
        if not shorts:
            print('AUDIT FAIL: module defines no SHORTS'); return 1
        episodes = shorts
    for name, S in episodes.items():
        err = lambda m: errors.append(f'{name}: {m}')
        ids = [s.id for s in S]
        if len(ids) != len(set(ids)):
            err('duplicate scene ids')
        repos = {s.repo for s in S}
        if len(repos) != 1 or '' in repos:
            err(f'a video must introduce exactly ONE repo, found {sorted(repos)}')
        want = SHORT_BEATS if a.short else BEATS
        if [s.beat for s in S] != want:
            err(f'beats {[s.beat for s in S]} != {want}')
        if a.short:
            full_scenes = dict(load(Path(a.episode).resolve())[0]).get(name)   # Short-only episodes (SHORT_ONLY) have no full cut
            full = {x.beat: x for x in full_scenes} if full_scenes else {}
            for s in S:
                if not full:
                    continue
                f = full[s.beat]
                if a.lang == 'vi':
                    if (s.mode, s.lines, s.data) != (f.mode, f.lines, f.data):
                        err(f'{s.id}: visuals differ from the full episode scene {f.id}')
                    continue
                nums = lambda d: [d.get(k) for k in ('total', 'month', 'week', 'today', 'segs', 'avg')] + [[v for _, v in d.get('pts', [])]]
                if s.mode != f.mode or len(s.lines) != len(f.lines) or nums(s.data) != nums(f.data) or s.data.get('lang') != 'en':
                    err(f'{s.id}: English visuals must keep mode, line count and every number of {f.id} and set lang=en')
                if re.search(r'[ăâđêôơưàáạảãèéẹẻẽìíịỉĩòóọỏõùúụủũỳýỵỷỹ]', s.script, re.I):
                    err(f'{s.id}: Vietnamese letters in English narration')
            seconds = sum(len(s.script.split()) / (2.0 if a.lang == 'en' else WORDS_PER_SECOND) + TAIL for s in S)
            if seconds > LIMITS['max']:
                err(f'estimated runtime {seconds:.0f}s exceeds {LIMITS["max"]}s')
        value = next((s for s in S if s.beat == 'value'), None)
        if value is not None and not (value.data.get('caveat_from') is not None and len(value.lines) > value.data['caveat_from']):
            err('value scene has no caveat')
        intro = next((s for s in S if s.beat == 'intro'), None)
        if intro is not None and (len(intro.data.get('chips', [])) != 4 or not intro.data.get('q')):
            err('intro needs a hook question `q` and 4 info chips')
        growth = next((s for s in S if s.beat == 'growth'), None)
        if growth is not None and not {'total', 'month', 'pts'} <= set(growth.data):
            err('growth scene needs total, month and chart points')
        if intro is not None and not any(w in intro.script.lower() for w in ('hãy tưởng tượng', 'bạn đã bao giờ', 'sáng nay', '?')):
            err('intro narration should open with a story/question hook')
        if next((s for s in S if s.beat == 'outro'), None) is not None and '?' not in S[0].script:
            err('opening question missing: the outro must answer it')
        for s in S:
            if re.search(r'\d{5,}', s.script):
                err(f'{s.id}: spell long numbers as words for TTS')
            if not s.silent and not s.script:
                err(f'{s.id}: no narration')
    cfg = Path(a.episode).resolve().parent / 'config.py'
    if cfg.exists() and "os.environ.get('KIEU_VIDEO_SPEED', '1.0')" not in cfg.read_text():
        errors.append('config.py VIDEO_SPEED default is not 1.0')
    if errors:
        print('AUDIT FAIL'); [print(' -', e) for e in errors]; return 1
    print('AUDIT PASS' + (f' (short, {a.lang})' if a.short else '') + ': ' + ', '.join(f'{n}: {len(S)} scenes, 1 repo' for n, S in episodes.items()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
