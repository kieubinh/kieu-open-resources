#!/bin/zsh
# Rebuild an episode from checked takes: join, align, shots, render, mix, metadata, review MP4.
# Usage: build_episode.sh STUDIO_DIR projects/NAME EPISODE_DIR   Run in the background; the render takes about 40 minutes for a 7-minute episode.
set -e
ST=$1; P=$2; EP=$3; SK=${0:A:h}
cd $ST; PY=.venv/bin/python
$PY $SK/patch_kit.py --studio $ST --check
$PY $SK/join_voice.py --episode $EP --out $ST/$P/input/voiceover.wav
$PY tools/transcribe.py --project $P --script $P/input/script.txt --lang vi --model small 2>&1 | tail -3
P=$P $PY - <<'X'
import json, os, subprocess
P = os.environ['P']; p = P + '/config.json'; c = json.load(open(p))
d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', P + '/input/voiceover.wav']))
c['duration'] = round(d + 3.5, 2); json.dump(c, open(p, 'w'), ensure_ascii=False, indent=1); print('duration', c['duration'])
X
$PY $P/story/build_shots.py
node render.mjs --project $P --sheet --scale 0.4 2>&1 | tail -1
node render.mjs --project $P 2>&1 | tail -2
$PY audio/mix.py --project $P 2>&1 | tail -3
$PY $SK/make_meta.py --episode $EP --project $ST/$P
cp $P/out/*.mp4 $EP/review.mp4
echo FINISHED
