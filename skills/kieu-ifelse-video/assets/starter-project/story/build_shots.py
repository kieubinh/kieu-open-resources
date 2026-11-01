#!/usr/bin/env python3
"""Turn story/shotlist.py + timeline/words.json into story/shots.json (cut 0.12 s before each anchor's first word)."""
import importlib.util, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sl', ROOT / 'story/shotlist.py'); sl = importlib.util.module_from_spec(spec); spec.loader.exec_module(sl)
words = json.loads((ROOT / 'timeline/words.json').read_text()); words = words.get('words', words) if isinstance(words, dict) else words
norm = lambda s: re.sub(r'[^\wÀ-ỹ]', '', s.lower())
W = [norm(w['word']) for w in words]
def find(anchor, frm):
    q = [norm(x) for x in anchor.split()]
    for i in range(frm, len(W) - len(q) + 1):
        if W[i:i + len(q)] == q: return i
    # hyphens/punctuation in the script can merge tokens; try joined
    sys.exit(f'anchor not found: {anchor!r} after word {frm}')
cfg = json.loads((ROOT / 'config.json').read_text()); total = cfg['duration']
idx, pos = [], 0
for sid, a, o in sl.L:
    i = find(a, pos); idx.append(i); pos = i + 1
st = [max(0, words[i]['start'] - 0.12) if n else 0 for n, i in enumerate(idx)]
shots = []
for n, (sid, a, o) in enumerate(sl.L):
    e = st[n + 1] if n + 1 < len(st) else total
    i0, i1 = idx[n], (idx[n + 1] if n + 1 < len(idx) else len(words))
    sh = {'id': sid, 'start': round(st[n], 3), 'end': round(e, 3), 'line': ' '.join(w['word'] for w in words[i0:i1]), 'scene': sid}
    if o.get('bars'): sh['bars'] = o['bars']
    if o.get('in'): sh['in'] = {'type': o['in'], 'dur': 0.5 if o['in'] in ('dip', 'fade') else 0.3}
    if 'sfx' in o: sh['sfx'] = [{'at': a2, 'name': nm, 'gain': g} for a2, nm, g in o['sfx']]
    if 'amb' in o: sh['amb'] = {'name': o['amb'], 'gain': -28}
    if o.get('captions') is False: sh['captions'] = False
    shots.append(sh)
mpos = 0; ms = []
for a, mood, inten in sl.MUSIC:
    i = find(a, mpos); mpos = i + 1; ms.append([words[i]['start'], mood, inten])
music = [{'start': (0 if k == 0 else round(m[0], 2)), 'end': round(ms[k + 1][0], 2) if k + 1 < len(ms) else total, 'mood': m[1], 'intensity': m[2]} for k, m in enumerate(ms)]
(ROOT / 'story/shots.json').write_text(json.dumps({'title': cfg['title'], 'duration': total, 'shots': shots, 'music': music, 'sfx': []}, ensure_ascii=False, indent=1))
d = sorted(s['end'] - s['start'] for s in shots); print(len(shots), 'shots; median', round(d[len(d) // 2], 2), 'min', round(d[0], 2), 'max', round(d[-1], 2), [s['id'] for s in shots if s['end'] - s['start'] < 0.7])
