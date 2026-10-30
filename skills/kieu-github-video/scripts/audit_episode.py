#!/usr/bin/env python3
"""Structure audit for a Kieu GitHub Radar episode.

Usage: audit_episode.py --episode <ep>/scripts/episode.py [--repos 3]
Checks (ONE repo per video): exactly one repo, the nine beats in order (intro, growth, why, problem, how, usage, value,
ideas, outro), a caveat in `value`, intro tiles, a growth scene with numbers, no 5+ digit numbers in narration,
default speed 1.0, unique scene ids. If the module defines EPISODES every episode is audited.
"""
from __future__ import annotations
import argparse, importlib.util, re, sys
from pathlib import Path

BEATS = ['intro', 'growth', 'why', 'problem', 'how', 'usage', 'value', 'ideas', 'outro']


def load(path: Path):  # returns {name: scenes}
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location('episode', path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return getattr(m, 'EPISODES', {'episode': m.S})


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--episode', required=True)
    a = ap.parse_args(); episodes = load(Path(a.episode).resolve()); errors = []
    for name, S in episodes.items():
        err = lambda m: errors.append(f'{name}: {m}')
        ids = [s.id for s in S]
        if len(ids) != len(set(ids)):
            err('duplicate scene ids')
        repos = {s.repo for s in S}
        if len(repos) != 1 or '' in repos:
            err(f'a video must introduce exactly ONE repo, found {sorted(repos)}')
        if [s.beat for s in S] != BEATS:
            err(f'beats {[s.beat for s in S]} != {BEATS}')
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
    print('AUDIT PASS: ' + ', '.join(f'{n}: {len(S)} scenes, 1 repo' for n, S in episodes.items()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
