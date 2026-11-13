#!/usr/bin/env python3
"""Cut a 9:16 Short with burned captions out of an episode project. Run from the studio folder.

Usage: make_short.py SRC NAME START END   SRC is projects/<episode>, START and END are seconds on its voiceover.
Writes projects/NAME, replacing any project of that name. Sound effects are dropped; mix.py rebuilds the audio.
"""
import json, os, shutil, subprocess, sys
src, name, a, b = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
dst = f'projects/{name}'; shutil.rmtree(dst, ignore_errors=True); os.makedirs(dst + '/input'); os.makedirs(dst + '/timeline'); os.makedirs(dst + '/story')
shutil.copytree(src + '/scenes', dst + '/scenes')
cfg = json.load(open(src + '/config.json'))
W = json.load(open(src + '/timeline/words.json')); W = W.get('words', W) if isinstance(W, dict) else W
keep = [dict(w, start=round(w['start'] - a, 3), end=round(w['end'] - a, 3)) for w in W if a <= w['start'] < b]
json.dump({'words': keep}, open(dst + '/timeline/words.json', 'w'), ensure_ascii=False)
S = json.load(open(src + '/story/shots.json')); shots = []
dur = round(b - a + 1.2, 2)
for s in S['shots']:
    if s['end'] <= a + 0.01 or s['start'] >= b - 0.01: continue
    n = dict(s); n['start'] = round(max(0, s['start'] - a), 3); n['end'] = round(min(dur, s['end'] - a), 3)
    shots.append(n)
shots[-1]['end'] = dur
m = [dict(x, start=max(0, x['start'] - a), end=min(dur, x['end'] - a)) for x in S['music'] if x['end'] > a and x['start'] < b]
json.dump({'title': cfg['title'], 'duration': dur, 'shots': shots, 'music': m, 'sfx': []}, open(dst + '/story/shots.json', 'w'), ensure_ascii=False, indent=1)
subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-ss', str(a), '-t', str(dur), '-i', src + '/input/voiceover.wav', '-c', 'copy', dst + '/input/voiceover.wav'], check=True)
cfg.update(aspect='9:16', duration=dur, captions=True, bars='none', fadeIn=0.2, fadeOut=0.5, voiceover='input/voiceover.wav'); cfg.pop('script', None)
json.dump(cfg, open(dst + '/config.json', 'w'), ensure_ascii=False, indent=1)
print(name, len(shots), 'shots', dur, 's', len(keep), 'words')
