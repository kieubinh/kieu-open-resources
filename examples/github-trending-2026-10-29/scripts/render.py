#!/usr/bin/env python3
"""Render one episode (KIEU_EPISODE) with Remotion.

  render.py --review   silent estimated timing, drawn mouth            -> output/<ep>_REMOTION_REVIEW.mp4
  render.py --release  real VoiceStudio WAV timeline + measured tracks  -> output/<ep>_VOICESTUDIO_CANDIDATE.mp4

If public/lipsync/<ep>.mp4 exists (make_lipsync.py, photoreal SadTalker face) the avatar plays it instead of the drawn
mouth; set KIEU_LIPSYNC=drawn to force the drawn mouth.
"""
import argparse, json, os, subprocess, sys
from config import ROOT, EPISODE

ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
g.add_argument('--review', action='store_true'); g.add_argument('--release', action='store_true')
a = ap.parse_args()
py = sys.executable
steps = [[py, 'scripts/build_timeline.py'] + (['--preview'] if a.review else []), [py, 'scripts/make_envelope.py'] + (['--preview'] if a.review else [])]
for s in steps:
    subprocess.run(s, cwd=ROOT, check=True)
face = ROOT / 'public' / 'lipsync' / f'{EPISODE}.mp4'
use_face = a.release and face.is_file() and os.environ.get('KIEU_LIPSYNC', '') != 'drawn'
props = {'faceVideo': f'lipsync/{EPISODE}.mp4' if use_face else None}
name = f'{EPISODE.upper()}_' + ('REMOTION_REVIEW' if a.review else 'VOICESTUDIO_CANDIDATE') + ('_SADTALKER' if use_face else '') + '.mp4'
print(f'render {name} (avatar: {"SadTalker video" if use_face else "drawn mouth"})', flush=True)
subprocess.run(['npx', 'remotion', 'render', 'src/index.ts', 'GitHubRadar', f'output/{name}', '--codec=h264', '--props=' + json.dumps(props)], cwd=ROOT, check=True)
